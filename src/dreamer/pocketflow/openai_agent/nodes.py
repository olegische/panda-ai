"""Agentic nodes for OpenAI MCP agent (PocketFlow, MCP-style, per pocketflow-mcp example)."""

from typing import Any, Dict

from pocketflow import Node

from src.dreamer.pocketflow.openai_agent.utils import call_llm


class GetToolsNode(Node):
    """Node to provide available OpenAI MCP tools (static, as in pocketflow-mcp example)."""

    def prep(self, shared: Dict[str, Any]) -> None:
        """No preparation needed.

        Args:
            shared: Shared state dictionary.

        Returns:
            None.
        """
        return None

    def exec(self, _: None) -> Any:
        """Return available tools (static list).

        Args:
            _: Not used.

        Returns:
            List of tool dicts.
        """
        tools = [
            {
                "name": "create_assistant",
                "description": "Create a new OpenAI assistant.",
                "inputSchema": {
                    "properties": {
                        "model": {"type": "string"},
                        "name": {"type": "string"},
                        "instructions": {"type": "string"},
                    },
                    "required": ["model"],
                },
            },
            {
                "name": "create_thread",
                "description": "Create a new conversation thread.",
                "inputSchema": {"properties": {}, "required": []},
            },
            {
                "name": "create_message",
                "description": "Add a message to a thread.",
                "inputSchema": {
                    "properties": {
                        "thread_id": {"type": "string"},
                        "role": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["thread_id", "role", "content"],
                },
            },
            {
                "name": "create_run",
                "description": "Run the assistant on a thread.",
                "inputSchema": {
                    "properties": {
                        "thread_id": {"type": "string"},
                        "assistant_id": {"type": "string"},
                    },
                    "required": ["thread_id", "assistant_id"],
                },
            },
        ]
        return tools

    def post(self, shared: Dict[str, Any], prep_res: None, exec_res: Any) -> str:
        """Store tools and format tool_info for LLM prompt.

        Args:
            shared: Shared state dictionary.
            prep_res: Not used.
            exec_res: List of tool dicts.

        Returns:
            Action string for next node.
        """
        shared["tools"] = exec_res
        tool_info = []
        for i, tool in enumerate(exec_res, 1):
            properties = tool["inputSchema"].get("properties", {})
            required = tool["inputSchema"].get("required", [])
            params = []
            for param_name, param_info in properties.items():
                param_type = param_info.get("type", "unknown")
                req_status = "(Required)" if param_name in required else "(Optional)"
                params.append(f"    - {param_name} ({param_type}): {req_status}")
            tool_info.append(
                f"[{i}] {tool['name']}\n  Description: {tool['description']}\n  Parameters:\n"
                + "\n".join(params)
            )
        shared["tool_info"] = "\n".join(tool_info)
        return "decide"


class DecideToolNode(Node):
    """Node for LLM reasoning: select tool and parameters (per pocketflow-mcp example)."""

    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare prompt for LLM.

        Args:
            shared: Shared state dictionary.

        Returns:
            Prompt string for LLM.
        """
        tool_info = shared["tool_info"]
        question = shared.get("question", "No question provided.")
        prompt = f"""
### CONTEXT
You are an assistant that can use tools via Model Context Protocol (MCP).

### ACTION SPACE
{tool_info}

### TASK
Answer this question: "{question}"

## NEXT ACTION
Analyze the question, extract any numbers or parameters, and decide which tool to use.
Return your response in this format:

```yaml
thinking: |
    <your step-by-step reasoning about what the question is asking and what numbers to extract>
tool: <name of the tool to use>
reason: <why you chose this tool>
parameters:
    <parameter_name>: <parameter_value>
    <parameter_name>: <parameter_value>
```
IMPORTANT:
1. Extract numbers from the question properly
2. Use proper indentation (4 spaces) for multi-line fields
3. Use the | character for multi-line text fields
"""
        return prompt

    def exec(self, prompt: str) -> str:
        """Call LLM to select tool and parameters.

        Args:
            prompt: Prompt string for LLM.

        Returns:
            LLM response as string.
        """
        return call_llm(prompt)

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Parse LLM response and store tool choice.

        Args:
            shared: Shared state dictionary.
            prep_res: Prompt string.
            exec_res: LLM response.

        Returns:
            Action string for next node.
        """
        import yaml

        try:
            yaml_str = exec_res.split("```yaml")[1].split("```")[0].strip()
            decision = yaml.safe_load(yaml_str)
            shared["tool_name"] = decision["tool"]
            shared["parameters"] = decision["parameters"]
            shared["thinking"] = decision.get("thinking", "")
            return "execute"
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print("Raw response:", exec_res)
            return "done"


class ExecuteToolNode(Node):
    """Node to execute the selected MCP tool (stub, as in pocketflow-mcp example)."""

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Prepare tool name and parameters.

        Args:
            shared: Shared state dictionary.

        Returns:
            Tuple of tool name and parameters.
        """
        return shared["tool_name"], shared["parameters"]

    def exec(self, inputs: Any) -> Any:
        """Call the selected MCP tool (stub).

        Args:
            inputs: Tuple of tool name and parameters.

        Returns:
            Tool result.
        """
        tool_name, parameters = inputs
        print(f"Calling MCP tool: {tool_name}({parameters})")
        # Здесь должен быть реальный вызов MCP tool через OpenAIMCPClient
        return {"result": f"stub_result_of_{tool_name}"}

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store result and finish flow.

        Args:
            shared: Shared state dictionary.
            prep_res: Tool call arguments.
            exec_res: Tool result.

        Returns:
            Action string for next node.
        """
        shared["tool_result"] = exec_res
        print(f"\n✅ Final Answer: {exec_res}")
        return "done"
