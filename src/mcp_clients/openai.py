"""OpenAI MCP client implementation."""
from typing import Optional, Dict, Any, List
from mcp import ClientSession, types
from mcp.client.sse import sse_client


class OpenAIMCPClient:
    """Client for OpenAI MCP server."""

    def __init__(self, server_url: str):
        """Initialize client.
        
        Args:
            server_url: URL of the OpenAI MCP server
        """
        self.server_url = server_url
        self._session: Optional[ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    async def connect(self):
        """Connect to MCP server using SSE."""
        if self._session is None:
            async with sse_client(self.server_url) as (read, write):
                self._session = ClientSession(read, write)
                await self._session.initialize()

    async def disconnect(self):
        """Disconnect from MCP server."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    @property
    def session(self) -> ClientSession:
        """Get current session."""
        if self._session is None:
            raise RuntimeError("Client is not connected. Use 'async with' or call connect()")
        return self._session

    # Assistant Tools
    async def create_assistant(
        self,
        model: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new assistant."""
        return await self.session.call_tool(
            "create_assistant",
            arguments={
                "model": model,
                "name": name,
                "description": description,
                "instructions": instructions,
                "tools": tools,
                "metadata": metadata
            }
        )

    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """Get assistant by ID."""
        return await self.session.call_tool(
            "get_assistant",
            arguments={"assistant_id": assistant_id}
        )

    async def modify_assistant(
        self,
        assistant_id: str,
        model: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Modify an existing assistant."""
        return await self.session.call_tool(
            "modify_assistant",
            arguments={
                "assistant_id": assistant_id,
                "model": model,
                "name": name,
                "description": description,
                "instructions": instructions,
                "tools": tools
            }
        )

    # Thread Tools
    async def create_thread(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new thread."""
        return await self.session.call_tool(
            "create_thread",
            arguments={
                "messages": messages,
                "metadata": metadata
            }
        )

    async def get_thread(self, thread_id: str) -> Dict[str, Any]:
        """Get thread by ID."""
        return await self.session.call_tool(
            "get_thread",
            arguments={"thread_id": thread_id}
        )

    # Message Tools
    async def create_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        file_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new message in a thread."""
        return await self.session.call_tool(
            "create_message",
            arguments={
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "file_ids": file_ids,
                "metadata": metadata
            }
        )

    async def list_messages(
        self,
        thread_id: str,
        limit: int = 20,
        order: str = "desc",
        after: Optional[str] = None,
        before: Optional[str] = None
    ) -> Dict[str, Any]:
        """List messages in a thread."""
        return await self.session.call_tool(
            "list_messages",
            arguments={
                "thread_id": thread_id,
                "limit": limit,
                "order": order,
                "after": after,
                "before": before
            }
        )

    # Run Tools
    async def create_run(
        self,
        thread_id: str,
        assistant_id: str,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new run for processing messages."""
        return await self.session.call_tool(
            "create_run",
            arguments={
                "thread_id": thread_id,
                "assistant_id": assistant_id,
                "model": model,
                "instructions": instructions,
                "tools": tools,
                "metadata": metadata
            }
        )

    async def get_run(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        """Get run by ID."""
        return await self.session.call_tool(
            "get_run",
            arguments={
                "thread_id": thread_id,
                "run_id": run_id
            }
        )

    async def submit_tool_outputs(
        self,
        thread_id: str,
        run_id: str,
        tool_outputs: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Submit outputs for tool calls."""
        return await self.session.call_tool(
            "submit_tool_outputs",
            arguments={
                "thread_id": thread_id,
                "run_id": run_id,
                "tool_outputs": tool_outputs
            }
        )

    async def cancel_run(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        """Cancel a run."""
        return await self.session.call_tool(
            "cancel_run",
            arguments={
                "thread_id": thread_id,
                "run_id": run_id
            }
        )

    # Run Step Tools
    async def list_run_steps(
        self,
        thread_id: str,
        run_id: str,
        limit: int = 20,
        order: str = "desc"
    ) -> Dict[str, Any]:
        """List steps in a run."""
        return await self.session.call_tool(
            "list_run_steps",
            arguments={
                "thread_id": thread_id,
                "run_id": run_id,
                "limit": limit,
                "order": order
            }
        )

    async def get_run_step(
        self,
        thread_id: str,
        run_id: str,
        step_id: str
    ) -> Dict[str, Any]:
        """Get run step by ID."""
        return await self.session.call_tool(
            "get_run_step",
            arguments={
                "thread_id": thread_id,
                "run_id": run_id,
                "step_id": step_id
            }
        )
