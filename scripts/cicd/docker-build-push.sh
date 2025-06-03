#!/bin/bash

read_first_line_of_file() {
  local file="$1"
  if [ -e "$file" ]; then
    read -r line < "$file"
    echo "$line"
  else
    echo "File $file does not exist."
    exit 1
  fi
}

# Load environment variables from .env file
set -a
source .env
set +a

# Read Docker credentials
docker_token=$(read_first_line_of_file "secrets/.docker-oauth-token")
docker_username=$(read_first_line_of_file "secrets/.docker-login-username")

echo "Building Docker image..."
docker compose -f docker-compose.build.yml build

if [ $? -eq 0 ]; then
    echo "Build successful. Stopping and restarting development containers..."
    docker compose -f docker-compose.dev.yml down
    docker compose -f docker-compose.dev.yml up -d

    echo "Logging in to Yandex Container Registry..."
    echo "$docker_token" | docker login --username "$docker_username" --password-stdin cr.yandex

    echo "Pushing Docker images to registry..."
    docker compose -f docker-compose.build.yml push

    echo "Logging out from registry..."
    docker logout cr.yandex

    echo "Build and push completed successfully!"
else
    echo "Build failed!"
    exit 1
fi
