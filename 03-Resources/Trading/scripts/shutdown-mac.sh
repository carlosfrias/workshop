#!/bin/bash
# shutdown-mac.sh — Shutdown the orchestrator Mac before sleep
# Usage: ./shutdown-mac.sh

echo "Shutting down orchestrator Mac in 60 seconds..."
echo "Press Ctrl+C to cancel"
sleep 60
sudo shutdown -h now
