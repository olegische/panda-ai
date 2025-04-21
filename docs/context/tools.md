# Carrot Quest MCP Server Tools Documentation

This document provides a comprehensive overview of all available tools in the Carrot Quest MCP server.

## Table of Contents
- [Apps Tools](#apps-tools)
- [Conversations Tools](#conversations-tools)
- [Users Tools](#users-tools)

## Apps Tools

### get_active_users
Get online users on the site.

**Arguments:**
- `app_id` (required): The ID of the app to get users for
- `paginate_position` (optional): Pagination parameter

### get_app_users
Get users (leads) from the app.

**Arguments:**
- `app_id` (required): The ID of the app to get users for
- `filters` (optional): Filters object for user filtering
- `sort_prop` (optional): Property to sort by (default: $last_seen)
- `sort_order` (optional): Sort direction - 'asc' or 'desc' (default: desc)
- `offset` (optional): Pagination offset (default: 0)
- `limit` (optional): Max number of users to return (1-50, default: 20)

### get_app_conversations
Get conversations for the app.

**Arguments:**
- `app_id` (required): The ID of the app to get conversations for
- `closed` (optional): Filter by closed status
- `answered` (optional): Filter by answered status
- `delayed` (optional): Filter by delayed status
- `assigned` (optional): Filter by assigned admin ID (0 for unassigned)
- `tags` (optional): Filter by conversation tags
- `channel` (optional): Filter by channel ID (0 for no channel)
- `assistant_type` (optional): Filter by assistant type
- `include_no_tags` (optional): Include conversations with no tags
- `include_not_assigned` (optional): Include unassigned conversations
- `paginate_position` (optional): Pagination parameter

### get_app_channels
Get list of channels for the app.

**Arguments:**
- `app_id` (required): The ID of the app to get channels for

## Conversations Tools

### get_conversation
Get conversation by ID.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to get

### get_conversation_parts
Get conversation parts (messages).

**Arguments:**
- `conversation_id` (required): The ID of the conversation to get parts for
- `paginate_position` (optional): Optional pagination parameter (list of part IDs)

### reply_to_conversation
Reply to a conversation.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to reply to
- `body` (optional): Text message content
- `body_json` (optional): Additional message content in JSON format
- `attachment` (optional): File attachment content
- `attachment_file_name` (optional): Attachment filename
- `from_user` (optional): User ID or 'default_user' to send as user
- `from_admin` (optional): Admin ID or 'default_admin' to send as admin
- `type_` (optional): Reply type (reply_admin, note, article)
- `external_id` (optional): External message ID
- `random_id` (optional): Random ID for RTS correlation
- `auto_assign` (optional): Admin ID to assign conversation to
- `auto_assign_random_id` (optional): Random ID for assign part
- `referrer` (optional): Referrer URL

### set_typing
Set typing status in conversation.

**Arguments:**
- `conversation_id` (required): The ID of the conversation
- `body` (required): The message being typed
- `from_user` (optional): User ID to set typing for
- `from_admin` (optional): Admin ID or 'default_admin' to set typing for

### assign_conversation
Assign conversation to an admin.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to assign
- `admin` (optional): Admin ID to assign to (None to unassign)
- `from_admin` (optional): Admin ID or 'default_admin' performing assignment
- `random_id` (optional): Random ID for RTS correlation

### add_conversation_tag
Add a tag to a conversation.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to tag
- `tag` (required): The tag to add (1-255 characters)
- `from_admin` (optional): Admin ID or 'default_admin' adding the tag
- `random_id` (optional): Random ID for RTS correlation

### delete_conversation_tag
Delete a tag from a conversation.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to remove tag from
- `tag` (required): The tag to remove (1-255 characters)
- `from_admin` (optional): Admin ID or 'default_admin' removing the tag
- `random_id` (optional): Random ID for RTS correlation

### close_conversation
Close a conversation.

**Arguments:**
- `conversation_id` (required): The ID of the conversation to close
- `from_admin` (optional): Admin ID or 'default_admin' closing conversation
- `random_id` (optional): Random ID for RTS correlation

## Users Tools

### get_user
Get user data by ID.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `by_user_id` (optional): Whether user_id is from your system
- `props` (optional): Show system properties (default: true)
- `props_events` (optional): Show event-related properties
- `props_custom` (optional): Show custom properties
- `presence_details` (optional): Show presence details
- `events` (optional): Show events in convenient format
- `segments` (optional): Show user segments
- `notes` (optional): Show user notes
- `tags` (optional): Show user tags
- `email_status` (optional): Show email subscription status
- `convert_props_types` (optional): Convert property values to appropriate types (default: true)
- `timezone_offset` (optional): Show timezone offset
- `app` (optional): App ID override

### set_user_props
Set user properties.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `operations` (required): List of property operations
- `by_user_id` (optional): Whether user_id is from your system
- `double_subscribe` (optional): Allow resubscribing unsubscribed users
- `parse_custom_props_type` (optional): Auto-detect custom property types (default: true)
- `source` (optional): Source info for contact collection
- `app` (optional): App ID override

### get_user_events
Get user events.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `by_user_id` (optional): Whether user_id is from your system
- `filter_name` (optional): Event name filter
- `props_as_string` (optional): Return property values as strings
- `paginate_position` (optional): Pagination parameter
- `app` (optional): App ID override

### record_user_event
Record user event.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `event` (required): Event name
- `params` (optional): Event parameters
- `created` (optional): Event timestamp
- `by_user_id` (optional): Whether user_id is from your system
- `app` (optional): App ID override

### get_user_conversations
Get user conversations.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `by_user_id` (optional): Whether user_id is from your system
- `with_user_replies_only` (optional): Only return conversations with user replies
- `recipient_type` (optional): Message recipient type (web or sdk) (default: web)
- `paginate_after` (optional): Pagination timestamp
- `app` (optional): App ID override

### send_message
Send message to user.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `body` (required): Message text
- `type_` (optional): Message type (popup_chat, popup_small, popup_big) (default: popup_chat)
- `by_user_id` (optional): Whether user_id is from your system
- `app` (optional): App ID override

### start_conversation
Start conversation as user.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `body` (optional): Message text
- `attachment` (optional): File attachment content
- `attachment_file_name` (optional): Attachment filename
- `random_id` (optional): Random ID for RTS correlation
- `referrer` (optional): Referrer URL
- `by_user_id` (optional): Whether user_id is from your system
- `app` (optional): App ID override

### set_presence
Set user presence status.

**Arguments:**
- `user_id` (required): User ID from Carrot quest
- `presence` (required): Status (online or idle)
- `current_page` (optional): Current page title
- `current_url` (optional): Current page URL
- `app` (optional): App ID override

### unsubscribe_email
Unsubscribe user from email.

**Arguments:**
- `user_id` (required): User ID (from Carrot quest or your system)
- `by_user_id` (optional): Whether user_id is from your system
- `app` (optional): App ID override
