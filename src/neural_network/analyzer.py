"""Neural network analyzer for conversation analysis and pattern recognition."""
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json
from datetime import datetime

from src.core.cache import RedisClient
from src.core.logger import LoggerService
from src.mcp_clients.carrot_quest import CarrotQuestMCPClient


class ConversationAnalyzer:
    """Analyzes conversations and determines optimal processing strategy."""

    def __init__(
        self,
        cache: RedisClient,
        carrot_quest: CarrotQuestMCPClient,
        logger: LoggerService
    ):
        """Initialize analyzer.
        
        Args:
            cache: Redis cache client
            carrot_quest: Carrot Quest MCP client
            logger: Logger service instance
        """
        self.cache = cache
        self.carrot_quest = carrot_quest
        self.logger = logger.get_logger(__name__)

    def _generate_pattern_hash(self, content: Dict[str, Any]) -> str:
        """Generate hash for pattern content.
        
        Args:
            content: Pattern content
            
        Returns:
            Pattern hash
        """
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    async def _get_similar_conversations(
        self,
        app_id: str,
        tags: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get similar conversations based on tags.
        
        Args:
            app_id: Carrot Quest app ID
            tags: List of conversation tags
            limit: Maximum number of conversations to return
            
        Returns:
            List of similar conversations
        """
        # Try to get from cache first
        cache_key = f"similar_conversations:{app_id}:{','.join(sorted(tags))}"
        cached = await self.cache.cache_get(cache_key)
        if cached:
            self.logger.debug(f"Found similar conversations in cache for tags: {tags}")
            return cached

        # Get from Carrot Quest
        conversations = await self.carrot_quest.get_app_conversations(
            app_id=app_id,
            tags=tags,
            limit=limit
        )

        # Cache the result
        await self.cache.cache_set(cache_key, conversations)
        return conversations

    async def analyze_conversation(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze conversation and determine optimal processing strategy.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            message: Current message
            context: Additional context
            
        Returns:
            Analysis result containing:
            - pattern_hash: Hash of identified pattern
            - assistant_config: Suggested assistant configuration
            - mcp_tools: List of suggested MCP tools
            - context_data: Additional context for processing
        """
        self.logger.debug(f"Analyzing conversation {conversation_id}")

        # Get conversation details
        conversation = await self.carrot_quest.get_conversation(conversation_id)
        app_id = conversation.get("app_id")
        tags = conversation.get("tags", [])

        # Get user details
        user = await self.carrot_quest.get_user(user_id)
        user_props = user.get("props", {})

        # Get similar conversations
        similar = await self._get_similar_conversations(app_id, tags)

        # Analyze patterns
        pattern_content = {
            "message_type": self._classify_message(message),
            "user_properties": user_props,
            "conversation_tags": tags,
            "similar_patterns": [
                self._extract_pattern(conv) for conv in similar
            ]
        }

        pattern_hash = self._generate_pattern_hash(pattern_content)

        # Generate assistant configuration
        assistant_config = self._generate_assistant_config(
            pattern_content,
            similar
        )

        # Determine optimal MCP tools
        mcp_tools = self._select_mcp_tools(
            pattern_content,
            assistant_config
        )

        return {
            "pattern_hash": pattern_hash,
            "assistant_config": assistant_config,
            "mcp_tools": mcp_tools,
            "context_data": {
                "user_properties": user_props,
                "conversation_tags": tags,
                "similar_conversations": similar,
                "pattern_content": pattern_content
            }
        }

    def _classify_message(self, message: str) -> str:
        """Classify message type.
        
        Args:
            message: Message content
            
        Returns:
            Message classification
        """
        # TODO: Implement actual message classification
        # For now, return a basic classification
        if "?" in message:
            return "question"
        if any(word in message.lower() for word in ["help", "support", "issue"]):
            return "support_request"
        return "general"

    def _extract_pattern(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Extract pattern from conversation.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Extracted pattern
        """
        return {
            "tags": conversation.get("tags", []),
            "message_count": len(conversation.get("messages", [])),
            "resolution_time": self._calculate_resolution_time(conversation),
            "successful": conversation.get("resolved", False)
        }

    def _calculate_resolution_time(self, conversation: Dict[str, Any]) -> Optional[float]:
        """Calculate conversation resolution time in minutes.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Resolution time in minutes or None if not resolved
        """
        created_at = conversation.get("created_at")
        resolved_at = conversation.get("resolved_at")
        
        if not (created_at and resolved_at):
            return None
            
        try:
            start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
            return (end - start).total_seconds() / 60
        except (ValueError, TypeError):
            return None

    def _generate_assistant_config(
        self,
        pattern: Dict[str, Any],
        similar: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate assistant configuration based on pattern.
        
        Args:
            pattern: Identified pattern
            similar: Similar conversations
            
        Returns:
            Assistant configuration
        """
        message_type = pattern["message_type"]
        
        # Base configuration
        config = {
            "model": "gpt-4-turbo-preview",
            "name": f"Support Assistant - {message_type.title()}",
            "description": "AI support assistant for customer inquiries",
            "tools": [{"type": "code_interpreter"}],  # Default tools
            "metadata": {
                "pattern_type": message_type,
                "created_at": datetime.utcnow().isoformat()
            }
        }

        # Customize based on message type
        if message_type == "question":
            config["instructions"] = (
                "You are a helpful support assistant focused on answering customer "
                "questions clearly and concisely. Use examples when helpful."
            )
        elif message_type == "support_request":
            config["instructions"] = (
                "You are a support assistant focused on resolving customer issues. "
                "Gather relevant information and provide step-by-step solutions."
            )
            config["tools"].append({"type": "file_search"})  # Add file search capability
        else:
            config["instructions"] = (
                "You are a friendly and professional support assistant. "
                "Help customers with their inquiries while maintaining a positive tone."
            )

        # Add context from similar conversations
        if similar:
            successful_patterns = [
                conv for conv in similar 
                if conv.get("resolved", False)
            ]
            if successful_patterns:
                config["metadata"]["similar_patterns_count"] = len(successful_patterns)
                avg_resolution_time = sum(
                    conv.get("resolution_time", 0) 
                    for conv in successful_patterns
                ) / len(successful_patterns)
                config["metadata"]["avg_resolution_time"] = avg_resolution_time

        return config

    def _select_mcp_tools(
        self,
        pattern: Dict[str, Any],
        assistant_config: Dict[str, Any]
    ) -> List[str]:
        """Select optimal MCP tools based on pattern.
        
        Args:
            pattern: Identified pattern
            assistant_config: Generated assistant configuration
            
        Returns:
            List of selected MCP tool names
        """
        # Base tools that are always needed
        tools = [
            "get_conversation",
            "reply_to_conversation",
            "set_typing"
        ]

        message_type = pattern["message_type"]
        user_props = pattern.get("user_properties", {})

        # Add tools based on message type
        if message_type == "support_request":
            tools.extend([
                "get_user",
                "set_user_props",
                "record_user_event"
            ])

        # Add tools based on user properties
        if user_props.get("is_premium"):
            tools.append("get_user_events")

        # Add tools based on conversation tags
        tags = pattern.get("conversation_tags", [])
        if "technical" in tags:
            tools.extend([
                "get_app_users",
                "get_active_users"
            ])

        return list(set(tools))  # Remove duplicates
