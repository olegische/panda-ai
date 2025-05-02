"""Meta-orchestrator for dynamically creating and managing AI assistants."""
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from openai.types.beta.threads.run import Run

from agent.types import ProcessingResult
from core.cache import RedisClient
from core.logger import LoggerService
from mcp_clients import CarrotQuestMCPClient, OpenAIMCPClient

from .instructions import get_orchestrator_instructions


class Orchestrator:
    """Orchestrates creation and management of AI assistants through LLM."""

    def __init__(
        self,
        logger: LoggerService,
        cache: RedisClient,
        carrot_quest: CarrotQuestMCPClient,
        openai: OpenAIMCPClient,
    ):
        """Initialize orchestrator.

        Args:
            logger: Logger service instance
            cache: Redis cache client
            carrot_quest: Carrot Quest MCP client
            openai: OpenAI MCP client
        """
        self.logger = logger.get_logger(__name__)
        self.cache = cache
        self.carrot_quest = carrot_quest
        self.openai = openai
        self.openai_client = AsyncOpenAI(
            api_key=openai.settings.OPENAI_API_KEY,
            organization=openai.settings.OPENAI_ORG_ID,
        )
        self._models_cache: Optional[List[Dict[str, Any]]] = None
        self._models_cache_time: Optional[float] = None

    async def _get_available_models(
        self, force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Get list of available models.

        Args:
            force_refresh: Force refresh cache

        Returns:
            List of available models
        """
        # Check cache
        now = time.time()
        if not force_refresh and self._models_cache and self._models_cache_time:
            if (
                now - self._models_cache_time
                < self.openai.settings.OPENAI_MODELS_CACHE_TTL
            ):
                return self._models_cache

        # Get models from API
        models = await self.openai_client.models.list()

        # Convert to list of dicts with relevant info
        model_list = [
            {
                "id": model.id,
                "created": model.created,
                "owned_by": model.owned_by,
                "context_window": getattr(model, "context_window", None),
            }
            for model in models.data
        ]

        # Update cache
        self._models_cache = model_list
        self._models_cache_time = now

        return model_list

    async def process_event(
        self, event_type: str, user_id: str, data: Dict[str, Any]
    ) -> ProcessingResult:
        """Process an incoming event through the meta-orchestrator.

        Args:
            event_type: Type of event to process
            user_id: User ID
            data: Event data

        Returns:
            Processing result
        """
        start_time = datetime.utcnow()

        try:
            # Format event data for the orchestrator
            event_context = {"event_type": event_type, "user_id": user_id, **data}

            # Get available models
            available_models = await self._get_available_models()

            # Get available tools from MCP clients
            carrot_tools = await self.carrot_quest.get_available_tools()
            openai_tools = await self.openai.get_available_tools()

            # Create chat completion with meta-orchestrator
            response = await self.openai_client.chat.completions.create(
                model=self.openai.settings.ORCHESTRATOR_MODEL,
                messages=[
                    {"role": "system", "content": get_orchestrator_instructions()},
                    {
                        "role": "user",
                        "content": f"Process this event:\n{json.dumps(event_context, indent=2)}\n\n"
                        f"Available models:\n{json.dumps(available_models, indent=2)}\n\n"
                        f"Available CarrotQuest tools:\n{json.dumps(carrot_tools, indent=2)}\n\n"
                        f"Available OpenAI Assistant tools:\n{json.dumps(openai_tools, indent=2)}",
                    },
                ],
                tools=[*carrot_tools, *openai_tools],
                tool_choice="auto",
            )

            # Process tool calls from the orchestrator
            run = None
            assistant_id = ""
            thread_id = ""
            pattern_hash = ""

            while True:
                if response.choices[0].message.tool_calls:
                    tool_outputs = []

                    for tool_call in response.choices[0].message.tool_calls:
                        try:
                            # Log tool usage
                            self.logger.info(
                                f"Orchestrator calling tool: {tool_call.function.name} "
                                f"with args: {tool_call.function.arguments}"
                            )

                            # Execute tool call
                            args = json.loads(tool_call.function.arguments)

                            if tool_call.function.name.startswith("carrot_quest."):
                                result = await self.carrot_quest.execute_tool(
                                    tool_call.function.name.split(".")[1], args
                                )
                            else:
                                result = await self.openai.execute_tool(
                                    tool_call.function.name.split(".")[1], args
                                )

                                # Track assistant and thread IDs for result
                                if tool_call.function.name == "openai.create_assistant":
                                    assistant_id = result["id"]
                                elif tool_call.function.name == "openai.create_thread":
                                    thread_id = result["id"]
                                elif tool_call.function.name == "openai.create_run":
                                    run = Run(**result)

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

                    # Get next action from orchestrator
                    response = await self.openai_client.chat.completions.create(
                        model=self.openai.settings.ORCHESTRATOR_MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": get_orchestrator_instructions(),
                            },
                            {
                                "role": "assistant",
                                "content": response.choices[0].message.content,
                                "tool_calls": response.choices[0].message.tool_calls,
                            },
                            {
                                "role": "tool",
                                "tool_call_id": tool_outputs[0]["tool_call_id"],
                                "content": json.dumps(tool_outputs),
                            },
                        ],
                        tools=[*carrot_tools, *openai_tools],
                        tool_choice="auto",
                    )
                else:
                    # Orchestrator is done
                    break

            # Calculate response time
            end_time = datetime.utcnow()
            response_time = (end_time - start_time).total_seconds()

            return ProcessingResult(
                success=True,
                response_time=response_time,
                assistant_id=assistant_id,
                thread_id=thread_id,
                pattern_hash=pattern_hash,
            )

        except Exception as e:
            self.logger.error(f"Error in meta-orchestrator: {str(e)}", exc_info=True)
            return ProcessingResult(
                success=False,
                response_time=0,
                assistant_id="",
                thread_id="",
                pattern_hash="",
                error=str(e),
            )
