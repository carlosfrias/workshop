#!/bin/bash
# ollama-idle-unload.sh — Watchdog that kills stuck Ollama model runners
#
# Problem: Pi agents maintain persistent streaming connections to Ollama,
# preventing the model from unloading even with OLLAMA_KEEP_ALIVE=0.
# This causes the runner to sit at 100% CPU indefinitely.
# Known Ollama bug: https://github.com/ollama/ollama/issues/7645
#
# Solution: This watchdog monitors the ollama runner process. After
# IDLE_THRESHOLD seconds, it forcefully kills the runner. Ollama
# recreates the runner on the next inference request. Pi reconnects
# automatically when a coms-net task arrives.
#
# Run via systemd timer (ollama-idle-unload.timer) every 15 seconds.
#
# Usage:   ./ollama-idle-unload.sh [--dry-run]

set -euo pipefail

IDLE_THRESHOLD=60  # Seconds before killing a stuck runner (gives pi time to register)
DRY_RUN=false

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    shift
fi

runner_pid=$(pgrep -f "ollama runner" 2>/dev/null | head -1 || true)

if [ -z "$runner_pid" ]; then
    exit 0
fi

runner_secs=$(ps -p "$runner_pid" -o etimes --no-headers 2>/dev/null | awk '{print int($1)}' || echo "0")

if [ "$runner_secs" -lt "$IDLE_THRESHOLD" ]; then
    exit 0
fi

# Runner has been alive too long — kill it regardless of state.
# Ollama will recreate it on next request. Pi reconnects automatically.
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN: Would kill ollama runner PID $runner_pid (alive ${runner_secs}s)"
else
    kill "$runner_pid" 2>/dev/null || true
    echo "$(date -Iseconds): Killed ollama runner PID $runner_pid (alive ${runner_secs}s)" >> /tmp/ollama-idle-unload.log
fi