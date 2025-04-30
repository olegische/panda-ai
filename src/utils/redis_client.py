"""Redis client for managing assistant mappings and patterns."""
from typing import Optional, Dict, Any, List
import json
import aioredis
from datetime import datetime, timedelta


class RedisClient:
    """Redis client for managing assistant mappings and patterns."""

    def __init__(self, redis_url: str, default_ttl: int = 3600):
        """Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL for keys in seconds (default: 1 hour)
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url)

    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    @property
    def redis(self) -> aioredis.Redis:
        """Get Redis connection."""
        if self._redis is None:
            raise RuntimeError("Redis client is not connected")
        return self._redis

    # Assistant Mappings
    async def get_assistant_id(self, user_id: str) -> Optional[str]:
        """Get assistant ID for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Assistant ID if exists, None otherwise
        """
        key = f"user:{user_id}:assistant"
        return await self.redis.get(key)

    async def set_assistant_id(self, user_id: str, assistant_id: str, ttl: Optional[int] = None):
        """Set assistant ID for user.
        
        Args:
            user_id: User ID
            assistant_id: Assistant ID
            ttl: Optional TTL override
        """
        key = f"user:{user_id}:assistant"
        await self.redis.set(key, assistant_id, ex=ttl or self.default_ttl)

    async def get_thread_id(self, conversation_id: str) -> Optional[str]:
        """Get thread ID for conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Thread ID if exists, None otherwise
        """
        key = f"conversation:{conversation_id}:thread"
        return await self.redis.get(key)

    async def set_thread_id(self, conversation_id: str, thread_id: str, ttl: Optional[int] = None):
        """Set thread ID for conversation.
        
        Args:
            conversation_id: Conversation ID
            thread_id: Thread ID
            ttl: Optional TTL override
        """
        key = f"conversation:{conversation_id}:thread"
        await self.redis.set(key, thread_id, ex=ttl or self.default_ttl)

    # Assistant Metadata
    async def get_assistant_metadata(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """Get assistant metadata.
        
        Args:
            assistant_id: Assistant ID
            
        Returns:
            Metadata dict if exists, None otherwise
        """
        key = f"assistant:{assistant_id}:metadata"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_assistant_metadata(
        self,
        assistant_id: str,
        metadata: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Set assistant metadata.
        
        Args:
            assistant_id: Assistant ID
            metadata: Metadata dict
            ttl: Optional TTL override
        """
        key = f"assistant:{assistant_id}:metadata"
        await self.redis.set(key, json.dumps(metadata), ex=ttl or self.default_ttl)

    async def update_assistant_stats(
        self,
        assistant_id: str,
        success: bool,
        response_time: float
    ):
        """Update assistant success rate and response time stats.
        
        Args:
            assistant_id: Assistant ID
            success: Whether interaction was successful
            response_time: Response time in seconds
        """
        key = f"assistant:{assistant_id}:metadata"
        metadata = await self.get_assistant_metadata(assistant_id) or {
            "stats": {
                "total_interactions": 0,
                "successful_interactions": 0,
                "total_response_time": 0
            }
        }
        
        stats = metadata["stats"]
        stats["total_interactions"] += 1
        if success:
            stats["successful_interactions"] += 1
        stats["total_response_time"] += response_time
        
        await self.set_assistant_metadata(assistant_id, metadata)

    # Pattern Storage
    async def store_pattern(
        self,
        pattern_hash: str,
        pattern_data: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Store conversation pattern.
        
        Args:
            pattern_hash: Hash of pattern content
            pattern_data: Pattern data including context and success metrics
            ttl: Optional TTL override
        """
        key = f"pattern:{pattern_hash}"
        await self.redis.set(key, json.dumps(pattern_data), ex=ttl or self.default_ttl)

    async def get_pattern(self, pattern_hash: str) -> Optional[Dict[str, Any]]:
        """Get conversation pattern.
        
        Args:
            pattern_hash: Hash of pattern content
            
        Returns:
            Pattern data if exists, None otherwise
        """
        key = f"pattern:{pattern_hash}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def get_similar_patterns(
        self,
        pattern_hashes: List[str]
    ) -> List[Dict[str, Any]]:
        """Get multiple conversation patterns.
        
        Args:
            pattern_hashes: List of pattern hashes
            
        Returns:
            List of pattern data
        """
        keys = [f"pattern:{h}" for h in pattern_hashes]
        data = await self.redis.mget(keys)
        return [json.loads(d) for d in data if d]

    async def update_pattern_success_rate(
        self,
        pattern_hash: str,
        success: bool
    ):
        """Update pattern success rate.
        
        Args:
            pattern_hash: Hash of pattern content
            success: Whether pattern application was successful
        """
        pattern = await self.get_pattern(pattern_hash)
        if pattern:
            stats = pattern.get("stats", {
                "total_uses": 0,
                "successful_uses": 0
            })
            stats["total_uses"] += 1
            if success:
                stats["successful_uses"] += 1
            pattern["stats"] = stats
            await self.store_pattern(pattern_hash, pattern)

    # Cleanup
    async def cleanup_expired_mappings(self):
        """Remove expired mappings to free up memory.
        
        This is typically called periodically by a background task.
        """
        # Redis automatically removes expired keys, but we might want to
        # implement additional cleanup logic here in the future
        pass
