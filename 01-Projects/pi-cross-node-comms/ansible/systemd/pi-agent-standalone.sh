#!/bin/bash
# pi-agent-standalone.sh — Persistent coms-net fleet agent via tmux
#
# Pi needs a TTY to stay in interactive mode with extensions active.
# This script runs pi inside a tmux session, which provides a pseudo-terminal.
# The coms-net extension maintains its SSE connection to the hub as long as
# pi's REPL is alive. systemd manages the tmux session lifecycle.
#
# After pi starts, we send an initial prompt via tmux send-keys to kick
# pi into its agent loop (extension loading, hub connection).

set -euo pipefail

SESSION_NAME="pi-agent"
INITIAL_PROMPT="You are a coms-net fleet agent. Your extension is already loaded. Report your hostname, then wait for tasks via the coms-net tools."

# Kill any existing tmux session with this name
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Create a new tmux session running pi with all arguments
# -d = detached (no terminal attached)
# The pi process inherits a proper PTY from tmux
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50 \
    pi "$@"

# Wait for pi to initialize and be ready for input
sleep 5

# Send the initial prompt to kick pi into its agent loop
# This triggers extension loading and coms-net hub connection
tmux send-keys -t "$SESSION_NAME" "$INITIAL_PROMPT" Enter

# Wait for the tmux session to exit (which happens if pi crashes)
# tmux wait-session blocks until the session is destroyed
while tmux has-session -t "$SESSION_NAME" 2>/dev/null; do
    sleep 5
done