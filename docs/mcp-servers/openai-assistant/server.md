# OpenAI Assistant MCP Server

This document describes the OpenAI Assistant MCP server that provides tools for interacting with the OpenAI Assistant API.

## Overview

The OpenAI Assistant MCP server provides a set of tools for creating and managing AI assistants through OpenAI's Assistant API. It acts as a thin wrapper around the official OpenAI API, providing direct access to assistant management, thread operations, messaging, and run execution capabilities.

## Agent Development Guide

### Basic Workflow

The typical workflow for developing an agent with the OpenAI Assistant API involves:

1. Creating an assistant with specific instructions and capabilities
2. Managing conversation threads for different user interactions
3. Handling messages and runs to process user inputs
4. Using tools to extend the assistant's capabilities

### Example Patterns

#### 1. Single-Turn Interaction

For simple question-answering scenarios:

```python
# Create a one-off thread and run
response = use_mcp_tool("create_thread_and_run", {
    "assistant_id": "asst_123",
    "thread": {
        "messages": [{
            "role": "user",
            "content": "What is the capital of France?"
        }]
    }
})

# Wait for completion and get response
messages = use_mcp_tool("list_messages", {
    "thread_id": response["thread_id"],
    "order": "desc",
    "limit": 1
})
```

#### 2. Multi-Turn Conversation

For maintaining context across multiple interactions:

```python
# Create a persistent thread
thread = use_mcp_tool("create_thread")

# First interaction
message1 = use_mcp_tool("create_message", {
    "thread_id": thread["id"],
    "role": "user",
    "content": "I need help with Python programming."
})

run1 = use_mcp_tool("create_run", {
    "thread_id": thread["id"],
    "assistant_id": "asst_123"
})

# Second interaction (maintains context)
message2 = use_mcp_tool("create_message", {
    "thread_id": thread["id"],
    "role": "user",
    "content": "How do I use list comprehensions?"
})

run2 = use_mcp_tool("create_run", {
    "thread_id": thread["id"],
    "assistant_id": "asst_123"
})
```

#### 3. Function Calling

For assistants that need to call external functions:

```python
# Create an assistant with function calling
assistant = use_mcp_tool("create_assistant", {
    "model": "gpt-4-turbo-preview",
    "tools": [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }]
})

# Handle function calls
run = use_mcp_tool("create_run", {
    "thread_id": thread_id,
    "assistant_id": assistant["id"]
})

# Check if the run requires action
if run["status"] == "requires_action":
    tool_outputs = []
    for call in run["required_action"]["submit_tool_outputs"]["tool_calls"]:
        if call["function"]["name"] == "get_weather":
            # Call your actual weather API here
            weather_data = {"temperature": 20, "condition": "sunny"}
            tool_outputs.append({
                "tool_call_id": call["id"],
                "output": json.dumps(weather_data)
            })

    # Submit the outputs
    use_mcp_tool("submit_tool_outputs", {
        "thread_id": thread_id,
        "run_id": run["id"],
        "tool_outputs": tool_outputs
    })
```

## API Reference

### Assistant Management

[Rest of the API documentation remains unchanged...]
