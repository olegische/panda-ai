"""Orchestrator for dynamically creating agents based on event context."""
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.message import Message
from openai.types.beta.threads.run import Run

from agent.types import AssistantMapping, ProcessingResult
from core.cache import RedisClient
from core.logger import LoggerService
from mcp_clients import CarrotQuestMCPClient, OpenAIMCPClient

from .instructions import (
    build_support_assistant_instructions,
    format_context_from_cases,
    get_analyzer_instructions,
)


class Orchestrator:
    """Orchestrates creation and management of AI assistants."""

    def __init__(
        self,
        logger: LoggerService,
        cache: RedisClient,
        carrot_quest: CarrotQuestMCPClient,
        openai: OpenAIMCPClient,
    ):
        """Initialize orchestrator.

        Args:
            logger: Logger service
            cache: Redis cache client
            carrot_quest: Carrot Quest MCP client
            openai: OpenAI MCP client
        """
        self.logger = logger.get_logger(__name__)
        self.cache = cache
        self.carrot_quest = carrot_quest
        self.openai = openai

    async def process_event(
        self, event_type: str, user_id: str, data: Dict[str, Any]
    ) -> ProcessingResult:
        """Process an incoming event.

        Args:
            event_type: Type of event to process
            user_id: User ID
            data: Event data

        Returns:
            Processing result
        """
        try:
            if event_type == "message":
                return await self._handle_message(user_id, data)
            elif event_type == "conversation_closed":
                await self._handle_conversation_closed(data["conversation_id"])
                return ProcessingResult(
                    success=True,
                    response_time=0,
                    assistant_id="",
                    thread_id="",
                    pattern_hash="",
                )
            else:
                self.logger.warning(f"Unhandled event type: {event_type}")
                return ProcessingResult(
                    success=False,
                    response_time=0,
                    assistant_id="",
                    thread_id="",
                    pattern_hash="",
                    error=f"Unhandled event type: {event_type}",
                )

        except Exception as e:
            self.logger.error(f"Error processing event: {str(e)}", exc_info=True)
            return ProcessingResult(
                success=False,
                response_time=0,
                assistant_id="",
                thread_id="",
                pattern_hash="",
                error=str(e),
            )

    async def _handle_message(
        self, user_id: str, data: Dict[str, Any]
    ) -> ProcessingResult:
        """Handle a new message event.

        Args:
            user_id: User ID
            data: Message data

        Returns:
            Processing result
        """
        start_time = datetime.utcnow()
        conversation_id = data["conversation_id"]
        message = data["message"]

        # Set typing indicator
        await self.carrot_quest.set_typing(
            conversation_id=conversation_id, body="Analyzing your message..."
        )

        # Analyze conversation context
        analysis = await self._analyze_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message=message,
            context=data.get("context", {}),
        )

        # Create or get thread
        thread = cast(Thread, await self.openai.create_thread())
        thread_id = thread.id

        # Format context from similar cases
        context_str = format_context_from_cases(
            analysis["context_data"]["similar_conversations"]
        )

        # Build assistant instructions
        instructions = build_support_assistant_instructions(
            user_props=analysis["context_data"]["user_properties"],
            similar_cases=analysis["context_data"]["similar_conversations"],
            message_type=analysis["context_data"]["pattern_content"]["message_type"],
        )

        # Create assistant with context
        assistant = cast(
            Assistant,
            await self.openai.create_assistant(
                model="gpt-4-turbo-preview",
                name=f"Support Assistant - {user_id}",
                instructions=instructions,
                tools=analysis["mcp_tools"],
                metadata={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "pattern_hash": analysis["pattern_hash"],
                    "created_at": datetime.utcnow().isoformat(),
                },
            ),
        )

        # Add context message
        await self.openai.create_message(
            thread_id=thread_id, role="system", content=context_str
        )

        # Add user message
        await self.openai.create_message(
            thread_id=thread_id, role="user", content=message
        )

        # Create and start run
        run = cast(
            Run,
            await self.openai.create_run(
                thread_id=thread_id, assistant_id=assistant.id
            ),
        )

        # Update typing message
        await self.carrot_quest.set_typing(
            conversation_id=conversation_id, body="Processing your request..."
        )

        # Wait for run completion and get response with timeout
        max_retries = 60  # 1 minute timeout
        retry_count = 0

        while retry_count < max_retries:
            run_status = cast(
                Run, await self.openai.get_run(thread_id=thread_id, run_id=run.id)
            )

            if run_status.status == "completed":
                # Get assistant's response
                messages = cast(
                    Dict[str, List[Message]],
                    await self.openai.list_messages(thread_id=thread_id, limit=1),
                )
                if messages["data"]:
                    message = messages["data"][0]
                    response = message.content[0].text.value
                    # Send response to Carrot Quest
                    await self.carrot_quest.reply_to_conversation(
                        conversation_id=conversation_id, body=response
                    )
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                error_msg = f"Run failed with status: {run_status.status}"
                if run_status.last_error:
                    error_msg += f" - {run_status.last_error}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            elif run_status.status == "requires_action":
                # Handle tool calls
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                if tool_calls:
                    tool_outputs = []
                    for tool_call in tool_calls:
                        try:
                            # Log tool usage
                            self.logger.info(
                                f"Processing tool call: {tool_call.function.name} "
                                f"with args: {tool_call.function.arguments}"
                            )

                            result = await self._execute_tool(
                                tool_call.function.name,
                                json.loads(tool_call.function.arguments),
                            )
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps(result),
                                }
                            )

                        except Exception as e:
                            error_msg = (
                                f"Error executing tool {tool_call.function.name}: "
                                f"{str(e)}"
                            )
                            self.logger.error(error_msg)
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps({"error": str(e)}),
                                }
                            )

                    await self.openai.submit_tool_outputs(
                        thread_id=thread_id, run_id=run.id, tool_outputs=tool_outputs
                    )

            retry_count += 1
            await asyncio.sleep(1)

        if retry_count >= max_retries:
            error_msg = "Assistant response timeout exceeded"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        # Store mapping
        mapping = AssistantMapping(
            assistant_id=assistant.id,
            thread_id=thread_id,
            pattern_hash=analysis["pattern_hash"],
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            total_messages=1,
        )
        await self._store_mapping(conversation_id, mapping)

        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds()

        return ProcessingResult(
            success=True,
            response_time=response_time,
            assistant_id=assistant["id"],
            thread_id=thread_id,
            pattern_hash=analysis["pattern_hash"],
        )

    async def _handle_conversation_closed(self, conversation_id: str) -> None:
        """Handle conversation closed event.

        Args:
            conversation_id: ID of closed conversation
        """
        mapping = await self._get_mapping(conversation_id)
        if mapping:
            # Clean up mapping
            await self._delete_mapping(conversation_id)

    async def _store_mapping(
        self, conversation_id: str, mapping: AssistantMapping
    ) -> None:
        """Store assistant mapping.

        Args:
            conversation_id: Conversation ID
            mapping: Assistant mapping to store
        """
        await self.cache.set(f"conversation:{conversation_id}:mapping", mapping.dict())

    async def _get_mapping(self, conversation_id: str) -> Optional[AssistantMapping]:
        """Get assistant mapping.

        Args:
            conversation_id: Conversation ID

        Returns:
            Assistant mapping if found
        """
        data = await self.cache.get(f"conversation:{conversation_id}:mapping")
        return AssistantMapping.parse_obj(data) if data else None

    async def _delete_mapping(self, conversation_id: str) -> None:
        """Delete assistant mapping.

        Args:
            conversation_id: Conversation ID
        """
        await self.cache.delete(f"conversation:{conversation_id}:mapping")

    async def _execute_tool(
        self, tool_name: str, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call from any assistant.

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments

        Returns:
            Tool execution result
        """
        tool_registry = {
            "get_user_info": self._tool_get_user_info,
            "get_conversation": self._tool_get_conversation,
            "get_similar_conversations": self._tool_get_similar_conversations,
            "update_user_properties": self._tool_update_user_properties,
            "add_conversation_tags": self._tool_add_conversation_tags,
        }

        if tool_name not in tool_registry:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return await tool_registry[tool_name](args)
        except Exception as e:
            self.logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}

    async def _tool_get_user_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get user information from Carrot Quest."""
        return await self.carrot_quest.get_user(args["user_id"])

    async def _tool_get_conversation(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get conversation details from Carrot Quest."""
        return await self.carrot_quest.get_conversation(args["conversation_id"])

    async def _tool_get_similar_conversations(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find similar conversations by tags."""
        conversations = await self.carrot_quest.get_app_conversations(
            tags=args["tags"], limit=args.get("limit", 5)
        )
        return {"conversations": conversations}

    async def _tool_update_user_properties(
        self, args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user properties in Carrot Quest."""
        await self.carrot_quest.set_user_props(
            user_id=args["user_id"], props=args["properties"]
        )
        return {"success": True}

    async def _tool_add_conversation_tags(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add tags to a conversation in Carrot Quest."""
        await self.carrot_quest.add_conversation_tags(
            conversation_id=args["conversation_id"], tags=args["tags"]
        )
        return {"success": True}

    async def _analyze_conversation(
        self, conversation_id: str, user_id: str, message: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze conversation using an OpenAI Assistant.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            message: Message content
            context: Additional context

        Returns:
            Analysis result containing pattern hash, tools, and context data
        """
        # Create thread for analysis
        thread = cast(Thread, await self.openai.create_thread())

        # Create analyzer assistant
        assistant = cast(
            Assistant,
            await self.openai.create_assistant(
                model="gpt-4-turbo-preview",
                name="Conversation Analyzer",
                instructions=get_analyzer_instructions(),
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_user_info",
                            "description": "Get user information from Carrot Quest",
                            "parameters": {
                                "type": "object",
                                "properties": {"user_id": {"type": "string"}},
                                "required": ["user_id"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_conversation",
                            "description": "Get conversation details from Carrot Quest",
                            "parameters": {
                                "type": "object",
                                "properties": {"conversation_id": {"type": "string"}},
                                "required": ["conversation_id"],
                            },
                        },
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_similar_conversations",
                            "description": "Find similar conversations by tags",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "tags": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "limit": {"type": "integer", "default": 5},
                                },
                                "required": ["tags"],
                            },
                        },
                    },
                ],
            ),
        )

        # Add context and message
        await self.openai.create_message(
            thread_id=thread.id,
            role="user",
            content=f"""Analyze this conversation:
User ID: {user_id}
Conversation ID: {conversation_id}
Message: {message}
Context: {json.dumps(context, indent=2)}
""",
        )

        # Run analysis
        run = cast(
            Run,
            await self.openai.create_run(
                thread_id=thread.id, assistant_id=assistant.id
            ),
        )

        # Wait for completion
        while True:
            run_status = cast(
                Run, await self.openai.get_run(thread_id=thread.id, run_id=run.id)
            )

            if run_status.status == "completed":
                messages = cast(
                    Dict[str, List[Message]],
                    await self.openai.list_messages(thread_id=thread.id, limit=1),
                )
                if messages["data"]:
                    # Parse analysis result
                    result = json.loads(messages["data"][0].content[0].text.value)
                    return result
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                raise Exception(
                    f"Analysis failed: {run_status.last_error or 'Unknown error'}"
                )
            elif run_status.status == "requires_action":
                # Handle tool calls
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                if tool_calls:
                    tool_outputs = []
                    for tool_call in tool_calls:
                        try:
                            result = await self._execute_tool(
                                tool_call.function.name,
                                json.loads(tool_call.function.arguments),
                            )
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps(result),
                                }
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error executing analyzer tool: {str(e)}"
                            )
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps({"error": str(e)}),
                                }
                            )

                    await self.openai.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

            await asyncio.sleep(1)
