#!/bin/bash

# Function to undeploy the stack
cleanup() {
  echo "Undeploying the stack..."
  source ./stop-docker-stack.sh
  exit 0
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Deploy the stack
echo "Deploying the stack..."
docker-compose down --remove-orphans
docker-compose up -d --remove-orphans

echo "Launching the proxy..."
docker stack deploy --with-registry-auth --compose-file ./docker-stack.yaml zane
source ./attach-proxy-networks.sh

echo "Scaling up all zane-ops services..."
services=$(docker service ls --filter label=zane-managed=true --format "{{.Name}}")
for service in $services; do
  if [ "$service"  != "zane_zane-proxy" ]; then
    docker service scale --detach $service=1
  fi
done

# Wait until Ctrl+C is pressed
echo "Server launched at http://app.zaneops.local"
echo "Press Ctrl+C to stop everything..."
while true; do
  sleep 1
done
