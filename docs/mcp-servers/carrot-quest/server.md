# Carrot Quest MCP Server

This document describes the Carrot Quest MCP server that provides tools for interacting with the Carrot Quest API.

## Overview

The Carrot Quest MCP server provides a set of tools for managing customer communication and data through Carrot Quest's API. It acts as a wrapper around the official Carrot Quest API, providing direct access to:

- User management and tracking
- Conversation handling
- App-level operations
- Channel management

## Integration Guide

### Basic Workflow

The typical workflow for integrating with Carrot Quest involves:

1. Managing users and their properties
2. Tracking user events and presence
3. Handling customer conversations
4. Managing app-level features

### Example Patterns

#### 1. Responding to User Messages

When a user sends a message, here's the complete flow:

```python
# 1. Get conversation details
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})

# 2. Get conversation history
messages = use_mcp_tool("get_conversation_parts", {
    "conversation_id": "123"
})

# 3. Show typing indicator
typing = use_mcp_tool("set_typing", {
    "conversation_id": "123",
    "body": "I'm typing a response...",
    "from_admin": "default_admin"
})

# 4. Reply with text
reply = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Thank you for your message! I'll help you with that.",
    "from_admin": "default_admin",
    "type_": "reply_admin"
})

# 5. Optionally assign to specific admin
assign = use_mcp_tool("assign_conversation", {
    "conversation_id": "123",
    "admin": 456,  # Admin ID
    "from_admin": "default_admin"
})
```

#### 2. Internal Notes and Knowledge Base

For internal communication and documentation:

```python
# First get conversation details
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})

# Add internal note
note = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Customer needs premium features - follow up next week",
    "from_admin": "default_admin",
    "type_": "note"  # Internal note, not visible to customer
})

# Share knowledge base article
article = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Here's our guide on premium features",
    "from_admin": "default_admin",
    "type_": "article"  # Knowledge base article
})
```

#### 3. File Attachments

When handling file attachments:

```python
# First get conversation details
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})

# Reply with file attachment
reply = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Here's the requested document",
    "from_admin": "default_admin",
    "attachment": file_content,  # Binary file content
    "attachment_file_name": "guide.pdf"  # Must be 1-255 chars
})
```

#### 4. Conversation Organization

For managing conversation workflow:

```python
# First get conversation details
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})

# Add tags for categorization
tag = use_mcp_tool("add_conversation_tag", {
    "conversation_id": "123",
    "tag": "billing-issue",
    "from_admin": "default_admin"
})

# Remove resolved tag
untag = use_mcp_tool("delete_conversation_tag", {
    "conversation_id": "123",
    "tag": "pending",
    "from_admin": "default_admin"
})

# Close resolved conversation
close = use_mcp_tool("close_conversation", {
    "conversation_id": "123",
    "from_admin": "default_admin"
})
```

#### 5. Team Collaboration

For team-based support:

```python
# First get conversation details
conversation = use_mcp_tool("get_conversation", {
    "conversation_id": "123"
})

# Get conversation history
messages = use_mcp_tool("get_conversation_parts", {
    "conversation_id": "123"
})

# Assign to specific admin with message
reply = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "I'll transfer you to our billing specialist",
    "from_admin": "default_admin",
    "auto_assign": 789,  # Billing specialist's ID
    "auto_assign_random_id": 12345  # For tracking assignment
})

# Add internal note about transfer
note = use_mcp_tool("reply_to_conversation", {
    "conversation_id": "123",
    "body": "Transferred to billing team - needs invoice adjustment",
    "from_admin": "default_admin",
    "type_": "note"
})
```

#### 6. App Management

For managing app-level features:

```python
# Get active users
active = use_mcp_tool("get_active_users", {
    "app_id": "123"
})

# Get app channels
channels = use_mcp_tool("get_app_channels", {
    "app_id": "123"
})

# Get filtered conversations
conversations = use_mcp_tool("get_app_conversations", {
    "app_id": "123",
    "closed": False,
    "assigned": 456,
    "tags": ["urgent"],
    "include_not_assigned": True
})

# For each conversation, get details and history
for conv in conversations["data"]:
    details = use_mcp_tool("get_conversation", {
        "conversation_id": conv["id"]
    })
    messages = use_mcp_tool("get_conversation_parts", {
        "conversation_id": conv["id"]
    })
```

## API Reference

### Apps Tools

The server provides tools for managing app-level operations:

- `get_active_users` - Get online users on the site
- `get_app_users` - Get users (leads) from the app
- `get_app_conversations` - Get conversations for the app
- `get_app_channels` - Get list of channels for the app

### Conversations Tools

Tools for handling customer conversations:

- `get_conversation` - Get conversation by ID
- `get_conversation_parts` - Get conversation messages
- `reply_to_conversation` - Reply to a conversation
- `set_typing` - Set typing status
- `assign_conversation` - Assign conversation to admin
- `add_conversation_tag` - Add conversation tag
- `delete_conversation_tag` - Remove conversation tag
- `close_conversation` - Close a conversation

### Users Tools

Tools for managing user data and interactions:

- `get_user` - Get user data by ID
- `set_user_props` - Set user properties
- `get_user_events` - Get user events
- `record_user_event` - Record user event
- `get_user_conversations` - Get user conversations
- `send_message` - Send message to user
- `start_conversation` - Start conversation as user
- `set_presence` - Set user presence status
- `unsubscribe_email` - Unsubscribe from email

## Best Practices

1. **User Management**
   - Use `by_user_id=True` when working with your system's user IDs
   - Handle system properties (starting with $) appropriately
   - Consider auto-detection of property types

2. **Conversation Handling**
   - Use appropriate message types (reply_admin, note, article)
   - Handle attachments properly (max 10MB)
   - Manage conversation assignments effectively

3. **Event Tracking**
   - Use system events (starting with $) when appropriate
   - Include relevant parameters with events
   - Consider timestamp handling for historical events

4. **Error Handling**
   - Handle API errors appropriately
   - Validate inputs before making API calls
   - Consider rate limiting and pagination

5. **Performance**
   - Use pagination for large data sets
   - Cache frequently accessed data
   - Monitor API usage and limits
