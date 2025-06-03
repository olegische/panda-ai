"""ReasoningCache: High-level reasoning and progress tracking for Dreamer."""

from typing import Any, Dict, List, Optional

from src.core.cache import RedisClient


class ReasoningCache:
    """Stores and retrieves reasoning steps, decisions, and results for agents and subagents.

    Uses RedisClient for persistence.
    """

    def __init__(self, cache_client: RedisClient):
        """Initialize the ReasoningCache with a Redis cache client.

        Args:
            cache_client: Redis cache client for persistence
        """
        self.cache = cache_client
        self._prefix = "dreamer:reasoning:"

    def _get_log_key(self, agent_id: str) -> str:
        """Get the Redis key for an agent's reasoning log.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Redis key for the agent's reasoning log
        """
        return f"{self._prefix}log:{agent_id}"

    def _get_state_key(self, agent_id: str) -> str:
        """Get the Redis key for an agent's state.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Redis key for the agent's state
        """
        return f"{self._prefix}state:{agent_id}"

    def _get_done_key(self, agent_id: str) -> str:
        """Get the Redis key for an agent's completion status.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Redis key for the agent's completion status
        """
        return f"{self._prefix}done:{agent_id}"

    async def log_step(self, agent_id: str, entry: Dict[str, Any]) -> None:
        """Log a reasoning step or decision for an agent.

        Args:
            agent_id: Unique identifier for the agent
            entry: Dictionary containing reasoning step information
        """
        log_key = self._get_log_key(agent_id)
        state_key = self._get_state_key(agent_id)

        # Get existing log or initialize empty list
        existing_log = await self.cache.get(log_key) or []

        # Add timestamp to entry
        entry["timestamp"] = entry.get("timestamp") or int(__import__("time").time())

        # Append new entry to log
        existing_log.append(entry)

        # Update log in cache
        await self.cache.set(log_key, existing_log)

        # Update last state
        await self.cache.set(state_key, entry)

    async def get_log(self, agent_id: str) -> List[Dict[str, Any]]:
        """Retrieve the reasoning log for an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            List of reasoning step entries
        """
        log_key = self._get_log_key(agent_id)
        return await self.cache.get(log_key) or []

    async def mark_done(self, agent_id: str) -> None:
        """Mark an agent as completed.

        Args:
            agent_id: Unique identifier for the agent
        """
        done_key = self._get_done_key(agent_id)
        await self.cache.set(done_key, True)

    async def is_done(self, agent_id: str) -> bool:
        """Check if an agent has completed execution.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            True if the agent has completed execution, False otherwise
        """
        done_key = self._get_done_key(agent_id)
        return bool(await self.cache.get(done_key))

    async def get_last_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the last known state for an agent (for recovery).

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Dictionary with the agent's last known state or None if not found
        """
        state_key = self._get_state_key(agent_id)
        return await self.cache.get(state_key)

    async def reset_log(self, agent_id: str) -> None:
        """Clear the reasoning log for an agent.

        Args:
            agent_id: Unique identifier for the agent
        """
        log_key = self._get_log_key(agent_id)
        state_key = self._get_state_key(agent_id)
        done_key = self._get_done_key(agent_id)

        # Delete all keys for this agent
        await self.cache.delete(log_key)
        await self.cache.delete(state_key)
        await self.cache.delete(done_key)
