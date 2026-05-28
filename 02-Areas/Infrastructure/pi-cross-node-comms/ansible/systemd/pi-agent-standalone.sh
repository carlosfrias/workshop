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

# ── Load nvm so systemd uses the managed Node.js version ──
# Save positional params before sourcing nvm (nvm processes $@)
_saved_args=("$@")
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
set -- "${_saved_args[@]}"
unset _saved_args

SESSION_NAME="pi-agent"
TMUX_TMPDIR="$HOME/.tmux"
mkdir -p "$TMUX_TMPDIR"
export TMUX_TMPDIR
INITIAL_PROMPT="You are a coms-net fleet agent. Your extension is already loaded. Report your hostname, then wait for tasks via the coms-net tools."

# Kill any existing tmux session with this name
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# Find absolute path to pi
PI_BIN=$(which pi)
if [ -z "$PI_BIN" ]; then
    echo "Error: pi binary not found" >&2
    exit 1
fi

# Build the pi command from all flags.
#
# Pi v0.76+ supports extension CLI flags (like --name, --project,
# --server-url, --auth-token, --purpose, --node) directly on the
# command line — no -- separator needed. The systemd unit template
# historically used a -- separator between native and extension flags.
# We now flatten all flags into a single command line, which works
# correctly regardless of whether -- is present.
#
# Split at -- is kept for backward compat with older systemd units,
# but the resulting PI_CMD omits the -- separator entirely.

ALL_ARGS=()
SEEN_DASH_DASH=false
for arg in "$@"; do
    if [[ "$arg" == "--" ]]; then
        SEEN_DASH_DASH=true
        continue
    fi
    ALL_ARGS+=("$arg")
done

# Build the pi command — all flags flat (no -- separator)
PI_CMD="$PI_BIN"
for arg in "${ALL_ARGS[@]}"; do
    PI_CMD="$PI_CMD $arg"
done

# Create a new tmux session running pi
# -d = detached (no terminal attached)
# The pi process inherits a proper PTY from tmux.
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50 \
    $PI_CMD

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
