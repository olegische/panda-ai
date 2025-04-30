"""Assistant orchestrator for managing conversations and assistants."""
import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional

from agent.types import AssistantMapping, ProcessingResult
from core.cache import RedisClient
from core.logger import LoggerService
from mcp_clients.carrot_quest import CarrotQuestMCPClient
from mcp_clients.openai import OpenAIMCPClient
from neural_network.analyzer import ConversationAnalyzer


class AssistantOrchestrator:
    """Orchestrates interactions between components."""

    def __init__(
        self,
        cache: RedisClient,
        carrot_quest: CarrotQuestMCPClient,
        openai: OpenAIMCPClient,
        analyzer: ConversationAnalyzer,
        logger: LoggerService,
    ):
        """Initialize orchestrator.

        Args:
            cache: Redis cache client
            carrot_quest: Carrot Quest MCP client
            openai: OpenAI MCP client
            analyzer: Conversation analyzer
            logger: Logger service
        """
        self.cache = cache
        self.carrot_quest = carrot_quest
        self.openai = openai
        self.analyzer = analyzer
        self.logger = logger.get_logger(__name__)

    async def process_message(
        self, conversation_id: str, user_id: str, message: str, context: Dict[str, Any]
    ) -> ProcessingResult:
        """Process incoming message.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            message: Message content
            context: Additional context

        Returns:
            Processing result
        """
        start_time = time.time()
        self.logger.debug(f"Processing message for conversation {conversation_id}")

        try:
            # Set typing indicator
            await self.carrot_quest.set_typing(
                conversation_id=conversation_id, body="Analyzing your message..."
            )

            # Get or create assistant mapping
            mapping = await self._get_assistant_mapping(conversation_id)

            if mapping:
                # Use existing assistant
                self.logger.debug(f"Using existing assistant {mapping.assistant_id}")
                result = await self._process_with_existing_assistant(
                    mapping=mapping, message=message, conversation_id=conversation_id
                )
            else:
                # Create new assistant
                self.logger.debug("Creating new assistant")
                result = await self._process_with_new_assistant(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message=message,
                    context=context,
                )

            # Update processing time
            response_time = time.time() - start_time

            # Update assistant stats
            await self._update_assistant_stats(
                assistant_id=result.assistant_id,
                success=result.success,
                response_time=response_time,
            )

            return result

        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return ProcessingResult(
                success=False,
                response_time=time.time() - start_time,
                assistant_id="",
                thread_id="",
                pattern_hash="",
                error=str(e),
            )

    async def handle_conversation_closed(self, conversation_id: str) -> None:
        """Handle conversation closed event.

        Args:
            conversation_id: Conversation ID
        """
        self.logger.debug(f"Handling closed conversation {conversation_id}")

        # Get mapping
        mapping = await self._get_assistant_mapping(conversation_id)
        if not mapping:
            return

        # Update assistant metadata
        metadata = await self.cache.get_assistant_metadata(mapping.assistant_id)
        if metadata:
            metadata.last_used = datetime.utcnow()
            await self.cache.set_assistant_metadata(
                assistant_id=mapping.assistant_id, metadata=metadata.dict()
            )

        # Clean up mapping
        await self.cache.delete(f"conversation:{conversation_id}:mapping")

    async def _get_assistant_mapping(
        self, conversation_id: str
    ) -> Optional[AssistantMapping]:
        """Get assistant mapping for conversation.

        Args:
            conversation_id: Conversation ID

        Returns:
            Assistant mapping if exists
        """
        mapping_data = await self.cache.get(f"conversation:{conversation_id}:mapping")
        return AssistantMapping.parse_obj(mapping_data) if mapping_data else None

    async def _store_assistant_mapping(
        self, conversation_id: str, mapping: AssistantMapping
    ) -> None:
        """Store assistant mapping.

        Args:
            conversation_id: Conversation ID
            mapping: Assistant mapping
        """
        await self.cache.set(f"conversation:{conversation_id}:mapping", mapping.dict())

    async def _process_with_existing_assistant(
        self, mapping: AssistantMapping, message: str, conversation_id: str
    ) -> ProcessingResult:
        """Process message with existing assistant.

        Args:
            mapping: Assistant mapping
            message: Message content
            conversation_id: Conversation ID

        Returns:
            Processing result
        """
        # Create message in thread
        await self.openai.create_message(
            thread_id=mapping.thread_id, role="user", content=message
        )

        # Create and monitor run
        run = await self.openai.create_run(
            thread_id=mapping.thread_id, assistant_id=mapping.assistant_id
        )

        # Wait for completion
        while True:
            run_status = await self.openai.get_run(
                thread_id=mapping.thread_id, run_id=run["id"]
            )

            if run_status["status"] == "completed":
                # Get assistant's response
                messages = await self.openai.list_messages(
                    thread_id=mapping.thread_id, limit=1
                )
                if messages["data"]:
                    response = messages["data"][0]["content"][0]["text"]["value"]
                    # Send response
                    await self.carrot_quest.reply_to_conversation(
                        conversation_id=conversation_id, body=response
                    )
                break

            elif run_status["status"] in ["failed", "cancelled"]:
                raise Exception(
                    f"Run failed: {run_status.get('last_error', 'Unknown error')}"
                )

            await asyncio.sleep(1)

        # Update mapping
        mapping.last_used = datetime.utcnow()
        mapping.total_messages += 1
        await self._store_assistant_mapping(conversation_id, mapping)

        return ProcessingResult(
            success=True,
            response_time=0,  # Will be updated by caller
            assistant_id=mapping.assistant_id,
            thread_id=mapping.thread_id,
            pattern_hash=mapping.pattern_hash,
        )

    async def _process_with_new_assistant(
        self, conversation_id: str, user_id: str, message: str, context: Dict[str, Any]
    ) -> ProcessingResult:
        """Process message with new assistant.

        Args:
            conversation_id: Conversation ID
            user_id: User ID
            message: Message content
            context: Additional context

        Returns:
            Processing result
        """
        # Analyze conversation
        analysis = await self.analyzer.analyze_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            message=message,
            context=context,
        )

        # Create assistant
        assistant = await self.openai.create_assistant(
            model=analysis["assistant_config"]["model"],
            name=analysis["assistant_config"]["name"],
            description=analysis["assistant_config"]["description"],
            instructions=analysis["assistant_config"]["instructions"],
            tools=analysis["assistant_config"]["tools"],
            metadata=analysis["assistant_config"]["metadata"],
        )

        # Create thread
        thread = await self.openai.create_thread(
            messages=[{"role": "user", "content": message}]
        )

        # Create run
        run = await self.openai.create_run(
            thread_id=thread["id"], assistant_id=assistant["id"]
        )

        # Wait for completion
        while True:
            run_status = await self.openai.get_run(
                thread_id=thread["id"], run_id=run["id"]
            )

            if run_status["status"] == "completed":
                # Get assistant's response
                messages = await self.openai.list_messages(
                    thread_id=thread["id"], limit=1
                )
                if messages["data"]:
                    response = messages["data"][0]["content"][0]["text"]["value"]
                    # Send response
                    await self.carrot_quest.reply_to_conversation(
                        conversation_id=conversation_id, body=response
                    )
                break

            elif run_status["status"] in ["failed", "cancelled"]:
                raise Exception(
                    f"Run failed: {run_status.get('last_error', 'Unknown error')}"
                )

            await asyncio.sleep(1)

        # Store mapping
        mapping = AssistantMapping(
            assistant_id=assistant["id"],
            thread_id=thread["id"],
            pattern_hash=analysis["pattern_hash"],
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow(),
            total_messages=1,
        )
        await self._store_assistant_mapping(conversation_id, mapping)

        return ProcessingResult(
            success=True,
            response_time=0,  # Will be updated by caller
            assistant_id=assistant["id"],
            thread_id=thread["id"],
            pattern_hash=analysis["pattern_hash"],
        )

    async def _update_assistant_stats(
        self, assistant_id: str, success: bool, response_time: float
    ) -> None:
        """Update assistant statistics.

        Args:
            assistant_id: Assistant ID
            success: Whether processing was successful
            response_time: Processing time in seconds
        """
        metadata = await self.cache.get_assistant_metadata(assistant_id)
        if metadata:
            metadata.last_used = datetime.utcnow()
            metadata.total_interactions += 1
            if success:
                # Update success rate
                metadata.success_rate = (
                    metadata.success_rate * (metadata.total_interactions - 1) + 1
                ) / metadata.total_interactions
            # Update average response time
            metadata.avg_response_time = (
                metadata.avg_response_time * (metadata.total_interactions - 1)
                + response_time
            ) / metadata.total_interactions
            await self.cache.set_assistant_metadata(
                assistant_id=assistant_id, metadata=metadata.dict()
            )
