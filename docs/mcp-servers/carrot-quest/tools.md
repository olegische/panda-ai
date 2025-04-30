# Carrot Quest MCP Tools Documentation

This document provides detailed documentation for all tools available in the Carrot Quest MCP server.

## Tool Categories

- [Apps Tools](#apps-tools) - Manage app-level operations
- [Conversations Tools](#conversations-tools) - Handle customer conversations
- [Users Tools](#users-tools) - Manage user data and interactions

## Apps Tools

### get_active_users

Get online users on the site.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "app_id": {
      "type": "string",
      "description": "The ID of the app to get users for"
    },
    "paginate_position": {
      "type": "string",
      "description": "Optional pagination parameter for v2 pagination. Only 'before' direction is supported"
    }
  },
  "required": ["app_id"]
}
```

**Example:**
```python
active_users = use_mcp_tool("get_active_users", {
    "app_id": "123",
    "paginate_position": "before_cursor"
})
```

### get_app_users

Get users (leads) from the app.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "app_id": {
      "type": "string",
      "description": "The ID of the app to get users for"
    },
    "filters": {
      "type": "object",
      "description": "Optional filters object for user filtering"
    },
    "sort_prop": {
      "type": "string",
      "description": "Property to sort by",
      "default": "$last_seen"
    },
    "sort_order": {
      "type": "string",
      "enum": ["asc", "desc"],
      "default": "desc"
    },
    "offset": {
      "type": "integer",
      "description": "Pagination offset",
      "default": 0
    },
    "limit": {
      "type": "integer",
      "description": "Max number of users to return (1-50)",
      "default": 20
    }
  },
  "required": ["app_id"]
}
```

**Example:**
```python
users = use_mcp_tool("get_app_users", {
    "app_id": "123",
    "filters": {"has_email": true},
    "sort_prop": "$last_seen",
    "limit": 10
})
```

### get_app_conversations

Get conversations for the app.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "app_id": {
      "type": "string",
      "description": "The ID of the app to get conversations for"
    },
    "closed": {
      "type": "boolean",
      "description": "Filter by closed status"
    },
    "answered": {
      "type": "boolean",
      "description": "Filter by answered status (last message from admin/user)"
    },
    "delayed": {
      "type": "boolean",
      "description": "Filter by delayed status"
    },
    "assigned": {
      "type": "integer",
      "description": "Filter by assigned admin ID (0 for unassigned)"
    },
    "tags": {
      "type": "array",
      "description": "Filter by conversation tags"
    },
    "channel": {
      "type": "integer",
      "description": "Filter by channel ID (0 for no channel)"
    },
    "assistant_type": {
      "type": "string",
      "description": "Filter by assistant type (dialogflow, yandex_ai, etc)"
    },
    "include_no_tags": {
      "type": "boolean",
      "description": "Include conversations with no tags",
      "default": false
    },
    "include_not_assigned": {
      "type": "boolean",
      "description": "Include unassigned conversations",
      "default": false
    },
    "paginate_position": {
      "type": "string",
      "description": "Pagination parameter"
    }
  },
  "required": ["app_id"]
}
```

**Example:**
```python
conversations = use_mcp_tool("get_app_conversations", {
    "app_id": "123",
    "closed": false,
    "assigned": 456,
    "tags": ["support", "urgent"]
})
```

### get_app_channels

Get list of channels for the app.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "app_id": {
      "type": "string",
      "description": "The ID of the app to get channels for"
    }
  },
  "required": ["app_id"]
}
```

**Example:**
```python
channels = use_mcp_tool("get_app_channels", {
    "app_id": "123"
})
```

## Conversations Tools

### get_conversation

Get conversation by ID.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to get"
    }
  },
  "required": ["conversation_id"]
}
```

**Example:**
```python
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})
```

### get_conversation_parts

Get conversation parts (messages).

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to get parts for"
    },
    "paginate_position": {
      "type": "array",
      "items": {
        "type": "integer"
      },
      "description": "Optional pagination parameter (list of part IDs)"
    }
  },
  "required": ["conversation_id"]
}
```

**Example:**
```python
messages = use_mcp_tool("get_conversation_parts", {
    "conversation_id": "123",
    "paginate_position": [456, 789]
})
```

### reply_to_conversation

Reply to a conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to reply to"
    },
    "body": {
      "type": "string",
      "description": "Text message content"
    },
    "body_json": {
      "type": "object",
      "description": "Additional message content in JSON format"
    },
    "attachment": {
      "type": "string",
      "format": "binary",
      "description": "File attachment content (max 10MB)"
    },
    "attachment_file_name": {
      "type": "string",
      "description": "Attachment filename (required if attachment provided)"
    },
    "from_user": {
      "type": ["string", "integer"],
      "description": "User ID or 'default_user' to send as user"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' to send as admin"
    },
    "type_": {
      "type": "string",
      "enum": ["reply_admin", "note", "article"],
      "description": "Reply type"
    },
    "external_id": {
      "type": "string",
      "description": "External message ID"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    },
    "auto_assign": {
      "type": "integer",
      "description": "Admin ID to assign conversation to"
    },
    "auto_assign_random_id": {
      "type": "integer",
      "description": "Random ID for assign part"
    },
    "referrer": {
      "type": "string",
      "description": "Referrer URL"
    }
  },
  "required": ["conversation_id"]
}
```

**Example:**
```python
reply = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Thank you for your message!",
    "from_admin": "default_admin",
    "type_": "reply_admin"
})
```

### set_typing

Set typing status in conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation"
    },
    "body": {
      "type": "string",
      "description": "The message being typed"
    },
    "from_user": {
      "type": "string",
      "description": "User ID to set typing for"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' to set typing for"
    }
  },
  "required": ["conversation_id", "body"]
}
```

**Example:**
```python
result = use_mcp_tool("set_typing", {
    "conversation_id": "123",
    "body": "Hello...",
    "from_admin": "default_admin"
})
```

### assign_conversation

Assign conversation to an admin.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to assign"
    },
    "admin": {
      "type": "integer",
      "description": "Admin ID to assign to (null to unassign)"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' performing assignment"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    }
  },
  "required": ["conversation_id"]
}
```

**Example:**
```python
result = use_mcp_tool("assign_conversation", {
    "conversation_id": "123",
    "admin": 456,
    "from_admin": "default_admin"
})
```

### add_conversation_tag

Add a tag to a conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to tag"
    },
    "tag": {
      "type": "string",
      "description": "The tag to add (1-255 characters)"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' adding the tag"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    }
  },
  "required": ["conversation_id", "tag"]
}
```

**Example:**
```python
result = use_mcp_tool("add_conversation_tag", {
    "conversation_id": "123",
    "tag": "urgent",
    "from_admin": "default_admin"
})
```

### delete_conversation_tag

Delete a tag from a conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to remove tag from"
    },
    "tag": {
      "type": "string",
      "description": "The tag to remove (1-255 characters)"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' removing the tag"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    }
  },
  "required": ["conversation_id", "tag"]
}
```

**Example:**
```python
result = use_mcp_tool("delete_conversation_tag", {
    "conversation_id": "123",
    "tag": "urgent",
    "from_admin": "default_admin"
})
```

### close_conversation

Close a conversation.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "conversation_id": {
      "type": "string",
      "description": "The ID of the conversation to close"
    },
    "from_admin": {
      "type": ["string", "integer"],
      "description": "Admin ID or 'default_admin' closing conversation"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    }
  },
  "required": ["conversation_id"]
}
```

**Example:**
```python
result = use_mcp_tool("close_conversation", {
    "conversation_id": "123",
    "from_admin": "default_admin"
})
```

## Users Tools

### get_user

Get user data by ID.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "props": {
      "type": "boolean",
      "description": "Show system properties",
      "default": true
    },
    "props_events": {
      "type": "boolean",
      "description": "Show event-related properties",
      "default": false
    },
    "props_custom": {
      "type": "boolean",
      "description": "Show custom properties",
      "default": false
    },
    "presence_details": {
      "type": "boolean",
      "description": "Show presence details",
      "default": false
    },
    "events": {
      "type": "boolean",
      "description": "Show events in convenient format",
      "default": false
    },
    "segments": {
      "type": "boolean",
      "description": "Show user segments",
      "default": false
    },
    "notes": {
      "type": "boolean",
      "description": "Show user notes",
      "default": false
    },
    "tags": {
      "type": "boolean",
      "description": "Show user tags",
      "default": false
    },
    "email_status": {
      "type": "boolean",
      "description": "Show email subscription status",
      "default": false
    },
    "convert_props_types": {
      "type": "boolean",
      "description": "Convert property values to appropriate types",
      "default": true
    },
    "timezone_offset": {
      "type": "boolean",
      "description": "Show timezone offset",
      "default": false
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id"]
}
```

**Example:**
```python
user = use_mcp_tool("get_user", {
    "user_id": "123",
    "by_user_id": true,
    "props": true,
    "props_custom": true
})
```

### set_user_props

Set user properties.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "operations": {
      "type": "array",
      "description": "List of property operations to perform",
      "items": {
        "type": "object",
        "properties": {
          "op": {
            "type": "string",
            "enum": ["update_or_create", "add", "delete"]
          },
          "key": {
            "type": "string"
          },
          "value": {
            "type": ["string", "number", "boolean", "null"]
          }
        }
      }
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "double_subscribe": {
      "type": "boolean",
      "description": "Allow resubscribing unsubscribed users",
      "default": false
    },
    "parse_custom_props_type": {
      "type": "boolean",
      "description": "Auto-detect custom property types",
      "default": true
    },
    "source": {
      "type": "object",
      "description": "Source info for contact collection"
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id", "operations"]
}
```

**Example:**
```python
result = use_mcp_tool("set_user_props", {
    "user_id": "123",
    "operations": [
        {
            "op": "update_or_create",
            "key": "$name",
            "value": "John Doe"
        }
    ],
    "by_user_id": true
})
```

### get_user_events

Get user events.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "filter_name": {
      "type": "string",
      "description": "Event name filter"
    },
    "props_as_string": {
      "type": "boolean",
      "description": "Return property values as strings",
      "default": false
    },
    "paginate_position": {
      "type": "array",
      "items": {
        "type": "integer"
      },
      "description": "Optional pagination parameter (list of event IDs)"
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id"]
}
```

**Example:**
```python
events = use_mcp_tool("get_user_events", {
    "user_id": "123",
    "by_user_id": true,
    "filter_name": "purchase"
})
```

### record_user_event

Record user event.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "event": {
      "type": "string",
      "description": "Event name (max 255 characters)"
    },
    "params": {
      "type": "object",
      "description": "Event parameters"
    },
    "created": {
      "type": "integer",
      "description": "Event timestamp (UTC)"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id", "event"]
}
```

**Example:**
```python
result = use_mcp_tool("record_user_event", {
    "user_id": "123",
    "event": "purchase",
    "params": {
        "product": "Premium Plan",
        "amount": 99.99
    },
    "by_user_id": true
})
```

### get_user_conversations

Get user conversations.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "with_user_replies_only": {
      "type": "boolean",
      "description": "Only return conversations with user replies",
      "default": false
    },
    "recipient_type": {
      "type": "string",
      "enum": ["web", "sdk"],
      "description": "Message recipient type",
      "default": "web"
    },
    "paginate_after": {
      "type": "number",
      "description": "Optional pagination timestamp"
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id"]
}
```

**Example:**
```python
conversations = use_mcp_tool("get_user_conversations", {
    "user_id": "123",
    "by_user_id": true,
    "with_user_replies_only": true
})
```

### send_message

Send message to user.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "body": {
      "type": "string",
      "description": "Message text to send"
    },
    "type_": {
      "type": "string",
      "enum": ["popup_chat", "popup_small", "popup_big"],
      "description": "Message display type",
      "default": "popup_chat"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id", "body"]
}
```

**Example:**
```python
result = use_mcp_tool("send_message", {
    "user_id": "123",
    "body": "Welcome to our service!",
    "type_": "popup_chat",
    "by_user_id": true
})
```

### start_conversation

Start conversation as user.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "body": {
      "type": "string",
      "description": "Message text"
    },
    "attachment": {
      "type": "string",
      "format": "binary",
      "description": "File attachment content"
    },
    "attachment_file_name": {
      "type": "string",
      "description": "Attachment filename (required if attachment provided)"
    },
    "random_id": {
      "type": "integer",
      "description": "Random ID for RTS correlation"
    },
    "referrer": {
      "type": "string",
      "description": "Referrer URL"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id"]
}
```

**Example:**
```python
result = use_mcp_tool("start_conversation", {
    "user_id": "123",
    "body": "Hi, I need help with...",
    "by_user_id": true
})
```

### set_presence

Set user presence status.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID from Carrot quest"
    },
    "presence": {
      "type": "string",
      "enum": ["online", "idle"],
      "description": "Status"
    },
    "current_page": {
      "type": "string",
      "description": "Current page title"
    },
    "current_url": {
      "type": "string",
      "description": "Current page URL"
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id", "presence"]
}
```

**Example:**
```python
result = use_mcp_tool("set_presence", {
    "user_id": "123",
    "presence": "online",
    "current_page": "Homepage",
    "current_url": "https://example.com"
})
```

### unsubscribe_email

Unsubscribe user from email.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "description": "User ID (from Carrot quest or your system)"
    },
    "by_user_id": {
      "type": "boolean",
      "description": "Whether user_id is from your system",
      "default": false
    },
    "app": {
      "type": "integer",
      "description": "App ID override"
    }
  },
  "required": ["user_id"]
}
```

**Example:**
```python
result = use_mcp_tool("unsubscribe_email", {
    "user_id": "123",
    "by_user_id": true
})
```

## Common Patterns

### 1. Managing User Properties

```python
# Get user details
user = use_mcp_tool("get_user", {
    "user_id": "123",
    "by_user_id": true,
    "props": true,
    "props_custom": true
})

# Update user properties
result = use_mcp_tool("set_user_props", {
    "user_id": "123",
    "by_user_id": true,
    "operations": [
        {
            "op": "update_or_create",
            "key": "$name",
            "value": "John Doe"
        },
        {
            "op": "update_or_create",
            "key": "$email",
            "value": "john@example.com"
        }
    ]
})

# Track user event
event = use_mcp_tool("record_user_event", {
    "user_id": "123",
    "by_user_id": true,
    "event": "subscription_started",
    "params": {
        "plan": "premium",
        "price": 99.99
    }
})
```

### 2. Managing Conversations

```python
# Start a conversation
conversation = use_mcp_tool("start_conversation", {
    "user_id": "123",
    "by_user_id": true,
    "body": "Hi, I need help with integration"
})

# Get conversation history
messages = use_mcp_tool("get_conversation_parts", {
    "conversation_id": conversation["id"]
})

# Reply to conversation
reply = use_mcp_tool("reply_to_conversation", {
    "conversation_id": conversation["id"],
    "body": "I'll help you with the integration",
    "from_admin": "default_admin",
    "type_": "reply_admin"
})

# Assign conversation
assign = use_mcp_tool("assign_conversation", {
    "conversation_id": conversation["id"],
    "admin": 456,
    "from_admin": "default_admin"
})

# Add tags
tag = use_mcp_tool("add_conversation_tag", {
    "conversation_id": conversation["id"],
    "tag": "integration",
    "from_admin": "default_admin"
})
```

### 3. Monitoring Active Users

```python
# Get active users
active = use_mcp_tool("get_active_users", {
    "app_id": "123"
})

# Update user presence
for user in active["data"]:
    presence = use_mcp_tool("set_presence", {
        "user_id": user["id"],
        "presence": "online",
        "current_page": "Dashboard",
        "current_url": "https://example.com/dashboard"
    })
