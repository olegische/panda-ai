"""Dreamer agent implementation using OpenAI Responses API."""
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from api.models.message import Message
from core.logger import LoggerService
from core.settings import Settings
from dreamer.instructions import get_orchestrator_instructions
from mcp_clients.carrot_quest.client import CarrotQuestMCPClient
from mcp_clients.openai import OpenAIMCPClient


class DreamerAgent:
    """Meta-orchestrator agent using OpenAI Responses API."""

    def __init__(
        self,
        logger: LoggerService,
        settings: Settings,
    ):
        """Initialize the Dreamer agent.

        Args:
            logger: Logger service instance
            settings: Application settings
        """
        self.logger = logger.get_logger(__name__)
        self.settings = settings

        # Initialize OpenAI client for Responses API
        self.openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            organization=settings.OPENAI_ORG_ID,
        )

        # Initialize MCP clients
        self.carrot_quest_client = CarrotQuestMCPClient(
            logger=logger, settings=settings
        )
        self.openai_mcp_client = OpenAIMCPClient(logger=logger, settings=settings)

    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from MCP clients.

        Returns:
            List of tools in OpenAI Responses API format
        """
        tools = []

        try:
            # Get tools from Carrot Quest MCP
            cq_tools = await self.carrot_quest_client.list_tools()
            # Convert to OpenAI tools format
            for tool_name, tool_schema in cq_tools.items():
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": f"carrot_quest_{tool_name}",
                            "description": tool_schema.get("description", ""),
                            "parameters": tool_schema.get("inputSchema", {}),
                        },
                    }
                )

            # Get tools from OpenAI MCP
            openai_tools = await self.openai_mcp_client.list_tools()
            for tool_name, tool_schema in openai_tools.items():
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": f"openai_{tool_name}",
                            "description": tool_schema.get("description", ""),
                            "parameters": tool_schema.get("inputSchema", {}),
                        },
                    }
                )

        except Exception as e:
            self.logger.error(f"Error getting tools: {e}")

        return tools

    async def process_message(
        self,
        message: Message,
    ) -> Dict[str, Any]:
        """Process incoming message through Responses API.

        Args:
            message: Message model with chat message data

        Returns:
            Dictionary with processing results
        """
        # Get available tools
        available_tools = await self.get_available_tools()

        # Build context for orchestrator
        context = self._build_context(message)

        # Create request to Responses API
        response = await self.openai_client.responses.create(
            model=self.settings.ORCHESTRATOR_MODEL,
            input=[
                {"role": "system", "content": get_orchestrator_instructions()},
                {"role": "user", "content": context},
            ],
            tools=available_tools,
            tool_choice="auto",  # Let the model choose tools
        )

        # Process response
        result = await self._process_response(response)

        return result

    def _build_context(self, message: Message) -> str:
        """Build context for the orchestrator.

        Args:
            message: Message model with chat message data

        Returns:
            Formatted context string
        """
        # Extract message content
        content = ""
        if isinstance(message.input, str):
            content = message.input
        elif isinstance(message.input, list):
            # Process list of InputMessage objects
            for input_msg in message.input:
                if isinstance(input_msg.content, str):
                    content += input_msg.content + "\n"
                elif isinstance(input_msg.content, list):
                    # Process list of InputText/InputFile objects
                    for item in input_msg.content:
                        if hasattr(item, "text"):
                            content += item.text + "\n"

        context_parts = [
            f"Source: {message.source}",
            f"Thread ID: {message.thread_id}",
            f"Message ID: {message.message_id}",
            f"User ID: {message.user_id}",
            f"Content: {content}",
        ]

        if message.source_context:
            context_parts.append(f"Source Context: {message.source_context}")

        return "\n".join(context_parts)

    async def _process_response(
        self,
        response,
    ) -> Dict[str, Any]:
        """Process response from Responses API.

        Args:
            response: Response from OpenAI Responses API

        Returns:
            Dictionary with processed results
        """
        result = {"status": "success", "actions": [], "messages": []}

        # Extract text output
        if hasattr(response, "output_text"):
            result["messages"].append(
                {"role": "assistant", "content": response.output_text}
            )

        # Process tool calls
        for tool_call in response.tool_calls or []:
            tool_result = await self._execute_tool_call(tool_call)
            result["actions"].append(
                {
                    "tool": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                    "result": tool_result,
                }
            )

        return result

    async def _execute_tool_call(
        self,
        tool_call,
    ) -> Any:
        """Execute tool call through appropriate MCP client.

        Args:
            tool_call: Tool call from Responses API

        Returns:
            Result of tool execution
        """
        tool_name = tool_call.function.name
        arguments = tool_call.function.arguments

        try:
            if tool_name.startswith("carrot_quest_"):
                # Remove prefix
                actual_tool_name = tool_name.replace("carrot_quest_", "")

                # Use the instance's client
                return await self.carrot_quest_client.call_tool(
                    actual_tool_name, arguments
                )

            elif tool_name.startswith("openai_"):
                actual_tool_name = tool_name.replace("openai_", "")

                # Use the instance's client
                return await self.openai_mcp_client.call_tool(
                    actual_tool_name, arguments
                )

            else:
                self.logger.error(f"Unknown tool prefix: {tool_name}")
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}
