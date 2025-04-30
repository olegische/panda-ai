# OpenAI Assistant MCP Tools Documentation

This document provides detailed documentation for all tools available in the OpenAI Assistant MCP server.

## Tool Categories

- [Assistant Tools](#assistant-tools) - Create and manage assistants
- [Thread Tools](#thread-tools) - Manage conversation threads
- [Message Tools](#message-tools) - Handle messages within threads
- [Run Tools](#run-tools) - Execute and manage assistant runs
- [Run Step Tools](#run-step-tools) - Track individual steps within runs

## Assistant Tools

### create_assistant

Creates a new assistant with specified configuration.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "model": {
      "type": "string",
      "description": "ID of the model to use (e.g., gpt-4-turbo-preview)"
    },
    "name": {
      "type": "string",
      "description": "Name of the assistant (max 256 chars)"
    },
    "description": {
      "type": "string",
      "description": "Description of the assistant (max 512 chars)"
    },
    "instructions": {
      "type": "string",
      "description": "System instructions (max 256k chars)"
    },
    "tools": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["code_interpreter", "file_search", "function"]
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs (max 16 pairs)"
    }
  },
  "required": ["model"]
}
```

**Example:**
```python
assistant = use_mcp_tool("create_assistant", {
    "model": "gpt-4-turbo-preview",
    "name": "Python Tutor",
    "description": "Expert Python programming tutor",
    "instructions": "You are a Python programming tutor...",
    "tools": [
        {"type": "code_interpreter"}
    ]
})
```

### list_assistants

Lists available assistants.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "integer",
      "description": "Number of assistants to return (1-100)",
      "default": 20
    },
    "order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    },
    "after": {
      "type": "string",
      "description": "Pagination cursor for next page"
    },
    "before": {
      "type": "string",
      "description": "Pagination cursor for previous page"
    }
  }
}
```

**Example:**
```python
assistants = use_mcp_tool("list_assistants", {
    "limit": 10,
    "order": "desc"
})
```

### get_assistant

Retrieves a specific assistant by ID.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "assistant_id": {
      "type": "string",
      "description": "The ID of the assistant to retrieve"
    }
  },
  "required": ["assistant_id"]
}
```

**Example:**
```python
assistant = use_mcp_tool("get_assistant", {
    "assistant_id": "asst_abc123"
})
```

### modify_assistant

Modifies an existing assistant.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "assistant_id": {
      "type": "string",
      "description": "The ID of the assistant to modify"
    },
    "model": {
      "type": "string",
      "description": "ID of the model to use"
    },
    "name": {
      "type": "string",
      "description": "Name of the assistant"
    },
    "description": {
      "type": "string",
      "description": "Description of the assistant"
    },
    "instructions": {
      "type": "string",
      "description": "System instructions"
    },
    "tools": {
      "type": "array",
      "description": "List of tools"
    }
  },
  "required": ["assistant_id"]
}
```

**Example:**
```python
updated = use_mcp_tool("modify_assistant", {
    "assistant_id": "asst_abc123",
    "name": "Advanced Python Tutor",
    "instructions": "Updated instructions..."
})
```

### delete_assistant

Deletes an assistant.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "assistant_id": {
      "type": "string",
      "description": "The ID of the assistant to delete"
    }
  },
  "required": ["assistant_id"]
}
```

**Example:**
```python
result = use_mcp_tool("delete_assistant", {
    "assistant_id": "asst_abc123"
})
```

## Thread Tools

### create_thread

Creates a new thread for conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "messages": {
      "type": "array",
      "description": "Initial messages for the thread",
      "items": {
        "type": "object",
        "properties": {
          "role": {
            "type": "string",
            "enum": ["user", "assistant"]
          },
          "content": {
            "type": "string"
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  }
}
```

**Example:**
```python
thread = use_mcp_tool("create_thread", {
    "messages": [{
        "role": "user",
        "content": "Hello! Can you help me with Python?"
    }]
})
```

### get_thread

Retrieves a specific thread.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread to retrieve"
    }
  },
  "required": ["thread_id"]
}
```

**Example:**
```python
thread = use_mcp_tool("get_thread", {
    "thread_id": "thread_abc123"
})
```

### modify_thread

Modifies a thread's metadata.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread to modify"
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  },
  "required": ["thread_id"]
}
```

**Example:**
```python
updated = use_mcp_tool("modify_thread", {
    "thread_id": "thread_abc123",
    "metadata": {"topic": "python_basics"}
})
```

### delete_thread

Deletes a thread.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread to delete"
    }
  },
  "required": ["thread_id"]
}
```

**Example:**
```python
result = use_mcp_tool("delete_thread", {
    "thread_id": "thread_abc123"
})
```

## Message Tools

### create_message

Creates a new message in a thread.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "role": {
      "type": "string",
      "enum": ["user", "assistant"],
      "description": "Role of the message sender"
    },
    "content": {
      "type": "string",
      "description": "The message content"
    },
    "file_ids": {
      "type": "array",
      "description": "Array of file IDs to attach"
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  },
  "required": ["thread_id", "role", "content"]
}
```

**Example:**
```python
message = use_mcp_tool("create_message", {
    "thread_id": "thread_abc123",
    "role": "user",
    "content": "How do I use list comprehensions?"
})
```

### list_messages

Lists messages in a thread.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "limit": {
      "type": "integer",
      "description": "Number of messages (1-100)",
      "default": 20
    },
    "order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    },
    "after": {
      "type": "string",
      "description": "Pagination cursor"
    },
    "before": {
      "type": "string",
      "description": "Pagination cursor"
    }
  },
  "required": ["thread_id"]
}
```

**Example:**
```python
messages = use_mcp_tool("list_messages", {
    "thread_id": "thread_abc123",
    "limit": 10,
    "order": "asc"
})
```

### get_message

Retrieves a specific message.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "message_id": {
      "type": "string",
      "description": "The ID of the message"
    }
  },
  "required": ["thread_id", "message_id"]
}
```

**Example:**
```python
message = use_mcp_tool("get_message", {
    "thread_id": "thread_abc123",
    "message_id": "msg_abc123"
})
```

### modify_message

Modifies a message's metadata.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "message_id": {
      "type": "string",
      "description": "The ID of the message"
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  },
  "required": ["thread_id", "message_id"]
}
```

**Example:**
```python
updated = use_mcp_tool("modify_message", {
    "thread_id": "thread_abc123",
    "message_id": "msg_abc123",
    "metadata": {"type": "question"}
})
```

## Run Tools

### create_run

Creates a new run for processing messages.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "assistant_id": {
      "type": "string",
      "description": "The ID of the assistant"
    },
    "model": {
      "type": "string",
      "description": "Optional model override"
    },
    "instructions": {
      "type": "string",
      "description": "Optional instructions override"
    },
    "tools": {
      "type": "array",
      "description": "Optional tools override"
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  },
  "required": ["thread_id", "assistant_id"]
}
```

**Example:**
```python
run = use_mcp_tool("create_run", {
    "thread_id": "thread_abc123",
    "assistant_id": "asst_abc123",
    "instructions": "Focus on beginner-friendly explanations"
})
```

### list_runs

Lists runs in a thread.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "limit": {
      "type": "integer",
      "description": "Number of runs (1-100)",
      "default": 20
    },
    "order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    }
  },
  "required": ["thread_id"]
}
```

**Example:**
```python
runs = use_mcp_tool("list_runs", {
    "thread_id": "thread_abc123",
    "limit": 10
})
```

### get_run

Retrieves a specific run.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    }
  },
  "required": ["thread_id", "run_id"]
}
```

**Example:**
```python
run = use_mcp_tool("get_run", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123"
})
```

### modify_run

Modifies a run's metadata.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    },
    "metadata": {
      "type": "object",
      "description": "Key-value pairs"
    }
  },
  "required": ["thread_id", "run_id"]
}
```

**Example:**
```python
updated = use_mcp_tool("modify_run", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123",
    "metadata": {"priority": "high"}
})
```

### submit_tool_outputs

Submits outputs for tool calls.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    },
    "tool_outputs": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "tool_call_id": {
            "type": "string",
            "description": "The ID of the tool call"
          },
          "output": {
            "type": "string",
            "description": "The output of the tool call"
          }
        },
        "required": ["tool_call_id", "output"]
      }
    }
  },
  "required": ["thread_id", "run_id", "tool_outputs"]
}
```

**Example:**
```python
result = use_mcp_tool("submit_tool_outputs", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123",
    "tool_outputs": [{
        "tool_call_id": "call_abc123",
        "output": json.dumps({"result": "success"})
    }]
})
```

### cancel_run

Cancels a run.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    }
  },
  "required": ["thread_id", "run_id"]
}
```

**Example:**
```python
result = use_mcp_tool("cancel_run", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123"
})
```

## Run Step Tools

### list_run_steps

Lists steps in a run.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    },
    "limit": {
      "type": "integer",
      "description": "Number of steps (1-100)",
      "default": 20
    },
    "order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    }
  },
  "required": ["thread_id", "run_id"]
}
```

**Example:**
```python
steps = use_mcp_tool("list_run_steps", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123",
    "limit": 10
})
```

### get_run_step

Retrieves a specific run step.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "thread_id": {
      "type": "string",
      "description": "The ID of the thread"
    },
    "run_id": {
      "type": "string",
      "description": "The ID of the run"
    },
    "step_id": {
      "type": "string",
      "description": "The ID of the step"
    }
  },
  "required": ["thread_id", "run_id", "step_id"]
}
```

**Example:**
```python
step = use_mcp_tool("get_run_step", {
    "thread_id": "thread_abc123",
    "run_id": "run_abc123",
    "step_id": "step_abc123"
})
```

## Common Patterns

### 1. Creating and Running an Assistant

```python
# Create assistant
assistant = use_mcp_tool("create_assistant", {
    "model": "gpt-4-turbo-preview",
    "name": "Math Tutor",
    "instructions": "You are a helpful math tutor..."
})

# Create thread with initial message
thread = use_mcp_tool("create_thread", {
    "messages": [{
        "role": "user",
        "content": "Can you help me with algebra?"
    }]
})

# Create run
run = use_mcp_tool("create_run", {
    "thread_id": thread["id"],
    "assistant_id": assistant["id"]
})

# Wait for completion
while True:
    run_status = use_mcp_tool("get_run", {
        "thread_id": thread["id"],
        "run_id": run["id"]
    })
    if run_status["status"] == "completed":
        break
    time.sleep(1)

# Get response
messages = use_mcp_tool("list_messages", {
    "thread_id": thread["id"],
    "order": "desc",
    "limit": 1
})
```

### 2. Function Calling with Tools

```python
# Create assistant with function
assistant = use_mcp_tool("create_assistant", {
    "model": "gpt-4-turbo-preview",
    "tools": [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }]
})

# Create and run thread
thread = use_mcp_tool("create_thread")
run = use_mcp_tool("create_run", {
    "thread_id": thread["id"],
    "assistant_id": assistant["id"]
})

# Handle tool calls
while True:
    run_status = use_mcp_tool("get_run", {
        "thread_id": thread["id"],
        "run_id": run["id"]
    })

    if run_status["status"] == "requires_action":
        tool_outputs = []
        for call in run_status["required_action"]["submit_tool_outputs"]["tool_calls"]:
            if call["function"]["name"] == "get_weather":
                # Call weather API
                weather_data = {"temp": 20, "condition": "sunny"}
                tool_outputs.append({
                    "tool_call_id": call["id"],
                    "output": json.dumps(weather_data)
                })

        use_mcp_tool("submit_tool_outputs", {
            "thread_id": thread["id"],
            "run_id": run["id"],
            "tool_outputs": tool_outputs
        })
    elif run_status["status"] == "completed":
        break

    time.sleep(1)
```

### 3. Managing Multiple Conversations

```python
# Create assistant
assistant = use_mcp_tool("create_assistant", {...})

# Create threads for different users
thread1 = use_mcp_tool("create_thread", {
    "metadata": {"user_id": "user1"}
})
thread2 = use_mcp_tool("create_thread", {
    "metadata": {"user_id": "user2"}
})

# Add messages to each thread
use_mcp_tool("create_message", {
    "thread_id": thread1["id"],
    "role": "user",
    "content": "Question from user 1"
})

use_mcp_tool("create_message", {
    "thread_id": thread2["id"],
    "role": "user",
    "content": "Question from user 2"
})

# Run assistant on both threads
run1 = use_mcp_tool("create_run", {
    "thread_id": thread1["id"],
    "assistant_id": assistant["id"]
})

run2 = use_mcp_tool("create_run", {
    "thread_id": thread2["id"],
    "assistant_id": assistant["id"]
})
