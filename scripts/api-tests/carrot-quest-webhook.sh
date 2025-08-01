#!/bin/bash

# Default values
# Use WEBHOOK_HOST if set, otherwise default to localhost:8220
if [ -z "$WEBHOOK_HOST" ]; then
    WEBHOOK_HOST="http://localhost:8220"
    # WEBHOOK_HOST="https://rorotools.com"
fi
HOST="$WEBHOOK_HOST"

# Get token from .env if not provided
if [ -z "$WEBHOOK_TOKEN" ]; then
    # Try to extract from .env file
    WEBHOOK_TOKEN=$(grep CARROT_QUEST_WEBHOOK_TOKEN .env | cut -d '"' -f 2)
    if [ -z "$WEBHOOK_TOKEN" ]; then
        WEBHOOK_TOKEN="service-token"  # Default from .env
    fi
fi

# Send the webhook request with real data format
echo "Sending webhook to $HOST/webhook/carrot-quest/conversations"
curl -X POST "${HOST}/webhook/carrot-quest/conversations" \
  -H "User-Agent: Carrotquest Webhook 1.0" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "conversation={
\"id\": \"1983951193033934722\",
\"created\": 1748613412,
\"conversation\": \"1976383525275829882\",
\"body\": \"\\u043e\\u0439 \\u0432\\u0435\\u0439. \\u043a\\u043e\\u0433\\u0434\\u0430 \\u0436\\u0435 \\u0432\\u0441\\u0435 \\u0440\\u0435\\u0448\\u0438\\u0442\\u0441\\u044f?\",
\"body_json\": {},
\"direction\": \"u2a\",
\"type\": \"reply_user\",
\"sent_via\": \"web_user\",
\"meta_data\": {},
\"reply_type\": \"no\",
\"actions\": null,
\"edited\": null,
\"removed\": null,
\"external_id\": null,
\"part_group\": \"1983940664684971054\",
\"conversation_delayed_until\": null,
\"conversation_last_update\": 1748613412,
\"conversation_closed\": false,
\"conversation_replied\": true,
\"conversation_tags\": [\"clarify-intent\", \"order-change\", \"delivery-israel\"],
\"conversation_admin_unread_count\": 3,
\"conversation_last_user_reply_time\": 1748613412,
\"conversation_type\": \"popup_chat\",
\"conversation_not_answered_admin_replies\": 0,
\"channel\": null,
\"assignee\": {
  \"id\": \"139584\",
  \"name\": \"Oleg\",
  \"avatar\": \"https://files.carrotquest.app/avatars/default-v4.png\",
  \"type\": \"admin\",
  \"name_internal\": \"dimatroso@gmail.com\"
},
\"conversation_assistant_type\": null,
\"user\": \"1976380630065219468\",
\"from\": \"1976380630065219468\",
\"random_id\": 1053297924
}" \
  -d "type=conversation" \
  -d "token=$WEBHOOK_TOKEN" \
  -v
