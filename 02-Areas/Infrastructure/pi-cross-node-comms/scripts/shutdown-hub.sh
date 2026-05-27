#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# shutdown-hub.sh — Shut down the local coms-net hub and clean state files
# ═══════════════════════════════════════════════════════════════════════════════
# Usage: ./shutdown-hub.sh [--project PROJECT]
#
# Steps:
#   1. Read PID from server.json → kill process
#   2. Fallback: kill by process name
#   3. Clean server.json + server.secret.json
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

PROJECT="${PI_COMS_NET_PROJECT:-default}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project) PROJECT="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--project PROJECT]"
            exit 0 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

COMS_DIR="$HOME/.pi/coms-net/projects/$PROJECT"
KILLED=false

# ── Step 1: Kill by PID from server.json ──
if [ -f "$COMS_DIR/server.json" ]; then
    PID=$(python3 -c "import json; print(json.load(open('$COMS_DIR/server.json')).get('pid',''))" 2>/dev/null || true)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "Killing hub (PID $PID)"
        kill "$PID" 2>/dev/null || true
        KILLED=true
        # Wait for process to exit
        for i in $(seq 1 10); do
            kill -0 "$PID" 2>/dev/null || break
            sleep 0.5
        done
    fi
fi

# ── Step 2: Fallback — kill by process name ──
if pkill -f "coms-net-server.ts" 2>/dev/null; then
    echo "Killed by process name match"
    KILLED=true
fi

# ── Step 3: Clean state files ──
rm -f "$COMS_DIR/server.json" "$COMS_DIR/server.secret.json" 2>/dev/null || true

if [ "$KILLED" = true ]; then
    echo "✅ coms-net hub shut down, state files cleaned"
else
    echo "ℹ️  No running hub found"
fi
