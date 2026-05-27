#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# standup-hub.sh — Stand up the coms-net hub for local development
# ═══════════════════════════════════════════════════════════════════════════════
# Usage: ./standup-hub.sh [--port PORT] [--project PROJECT] [--token TOKEN]
#
# Steps:
#   1. Kill old hub process (if any)
#   2. Clean stale state files
#   3. Start hub with fixed port
#   4. Wait for server.json
#   5. Read auth token
#   6. Verify health endpoint
#   7. Print connection info for pi sessions
#
# Design decisions:
#   - Fixed port (6420 default) to avoid ephemeral port confusion
#   - Binds 0.0.0.0 (all interfaces) by default; use --host 127.0.0.1 for loopback-only
#   - Auto-generates token on all-interfaces or loopback; required for other custom hosts
#   - Prints env vars to export for pi sessions
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVER_TS="$PROJECT_DIR/server/coms-net-server.ts"

# Defaults
PORT="${PI_COMS_NET_PORT:-6420}"
HOST="${PI_COMS_NET_HOST:-0.0.0.0}"
PROJECT="${PI_COMS_NET_PROJECT:-default}"
TOKEN="${PI_COMS_NET_AUTH_TOKEN:-}"
COMS_DIR="$HOME/.pi/coms-net/projects/$PROJECT"

# ── Parse flags ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --port)   PORT="$2"; shift 2 ;;
        --host)   HOST="$2"; shift 2 ;;
        --project) PROJECT="$2"; shift 2 ;;
        --token)  TOKEN="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [--port PORT] [--host HOST] [--project PROJECT] [--token TOKEN]"
            echo ""
            echo "Defaults: port=6420, host=0.0.0.0, project=default"
            echo "Token: auto-generated on all-interfaces/loopback; required for custom host"
            exit 0 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

COMS_DIR="$HOME/.pi/coms-net/projects/$PROJECT"

# ── Step 1: Kill old hub ──
echo "── Step 1: Kill old hub ──"
if [ -f "$COMS_DIR/server.json" ]; then
    OLD_PID=$(python3 -c "import json; print(json.load(open('$COMS_DIR/server.json')).get('pid',''))" 2>/dev/null || true)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Killing old hub (PID $OLD_PID)"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 1
    fi
fi
# Fallback: kill by process name
pkill -f "coms-net-server.ts" 2>/dev/null || true
sleep 1

# ── Step 2: Clean stale state files ──
echo "── Step 2: Clean stale state files ──"
rm -f "$COMS_DIR/server.json" "$COMS_DIR/server.secret.json" 2>/dev/null || true
mkdir -p "$COMS_DIR"

# ── Step 3: Start hub ──
echo "── Step 3: Start hub on $HOST:$PORT (project=$PROJECT) ──"
if ! command -v bun &>/dev/null; then
    echo "FAIL: bun not found. Install: curl -fsSL https://bun.sh/install | bash" >&2
    exit 1
fi

export PI_COMS_NET_HOST="$HOST"
export PI_COMS_NET_PORT="$PORT"
export PI_COMS_NET_PROJECT="$PROJECT"
if [ -n "$TOKEN" ]; then
    export PI_COMS_NET_AUTH_TOKEN="$TOKEN"
fi

nohup bun "$SERVER_TS" > /tmp/coms-net-hub.log 2>&1 &
HUB_PID=$!

# ── Step 4: Wait for server.json ──
echo "── Step 4: Wait for server.json ──"
for i in $(seq 1 20); do
    if [ -f "$COMS_DIR/server.json" ]; then break; fi
    sleep 0.5
done

if [ ! -f "$COMS_DIR/server.json" ]; then
    echo "FAIL: server.json not created after 10s" >&2
    echo "Check log: cat /tmp/coms-net-hub.log" >&2
    kill "$HUB_PID" 2>/dev/null || true
    exit 1
fi

# ── Step 5: Read URL and token ──
echo "── Step 5: Read connection info ──"
URL=$(python3 -c "import json; print(json.load(open('$COMS_DIR/server.json')).get('local_url',''))" 2>/dev/null)
RESOLVED_TOKEN=""
if [ -z "$TOKEN" ] && [ -f "$COMS_DIR/server.secret.json" ]; then
    # Auto-generated token (all-interfaces or loopback mode)
    RESOLVED_TOKEN=$(python3 -c "import json; print(json.load(open('$COMS_DIR/server.secret.json')).get('token',''))" 2>/dev/null)
else
    RESOLVED_TOKEN="$TOKEN"
fi

if [ -z "$URL" ]; then
    echo "FAIL: could not read local_url from server.json" >&2
    kill "$HUB_PID" 2>/dev/null || true
    exit 1
fi

# ── Step 6: Verify health ──
echo "── Step 6: Verify health endpoint ──"
AUTH_HEADER=""
if [ -n "$RESOLVED_TOKEN" ]; then
    AUTH_HEADER="-H \"Authorization: Bearer $RESOLVED_TOKEN\""
fi

for i in $(seq 1 10); do
    HEALTH=$(curl -sf $AUTH_HEADER "$URL/health" 2>/dev/null) && break
    sleep 0.5
done

if [ -z "${HEALTH:-}" ]; then
    echo "FAIL: hub not healthy at $URL" >&2
    echo "Check log: cat /tmp/coms-net-hub.log" >&2
    kill "$HUB_PID" 2>/dev/null || true
    exit 1
fi

# ── Step 7: Print connection info ──
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ coms-net hub online"
echo "═══════════════════════════════════════════════════"
echo "  URL:     $URL"
echo "  PID:     $HUB_PID"
echo "  Project: $PROJECT"
echo "  Token:   ${RESOLVED_TOKEN:0:8}…"
echo ""
echo "  To connect new pi sessions (auto-discovers server.json):"
echo "    pi"
echo ""
echo "  To connect existing pi sessions, export env vars:"
echo "    export PI_COMS_NET_SERVER_URL=\"$URL\""
echo "    export PI_COMS_NET_AUTH_TOKEN=\"$RESOLVED_TOKEN\""
echo "    export PI_COMS_NET_PROJECT=\"$PROJECT\""
echo ""
echo "  Or restart pi to discover the hub (server.json is read at session start)."
echo ""
echo "  To shut down: scripts/shutdown-hub.sh --project $PROJECT"
echo "═══════════════════════════════════════════════════"
echo ""

# Export for downstream consumers
export PI_COMS_NET_SERVER_URL="$URL"
export PI_COMS_NET_AUTH_TOKEN="$RESOLVED_TOKEN"
export PI_COMS_NET_PROJECT="$PROJECT"
export COMS_NET_HUB_PID="$HUB_PID"
