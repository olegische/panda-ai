#!/bin/bash

# Default values
# Use API_HOST if set, otherwise default to localhost:8990
if [ -z "$API_HOST" ]; then
    # API_HOST="http://localhost:8990"
    API_HOST="https://rorotools.com"
fi
HOST="$API_HOST"

# Get current timestamp in ISO format
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Generate unique IDs for testing
MESSAGE_ID="test-msg-$(date +%s)"
THREAD_ID="test-thread-$(date +%s)"
USER_ID="test-user-123"

# Send a simple text message to the API
echo "Sending simple text message to $HOST/api/v1/message"
curl -X POST "${HOST}/api/v1/message" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "This is a simple test message",
    "message_id": "'"$MESSAGE_ID"'",
    "thread_id": "'"$THREAD_ID"'",
    "user_id": "'"$USER_ID"'",
    "source": "carrot_quest",
    "timestamp": "'"$TIMESTAMP"'"
  }' \
  -v
