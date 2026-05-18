#!/usr/bin/env bash
# bring-up-wiki.sh
# One-command wrapper to start, stop, or toggle the Trading Desk Wiki.
#
# The VitePress site now lives at the project root:
#   - Config: .vitepress/config.js
#   - Content: wiki/ (unified: trading desk + operations + technical infrastructure)
#
# Usage:
#   ./bring-up-wiki.sh          Toggle (stop if running, start if stopped)
#   ./bring-up-wiki.sh start    Force start (only if stopped)
#   ./bring-up-wiki.sh stop     Force stop
#   ./bring-up-wiki.sh restart  Stop then start (always restarts)
#   ./bring-up-wiki.sh status   Show server status

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse argument
ACTION="${1:-toggle}"

case "$ACTION" in
  start|stop|restart|status|toggle)
    ;;
  *)
    echo "Usage: $0 [start|stop|restart|status|toggle]"
    exit 1
    ;;
esac

# Navigate to project root (two levels up from scripts/)
cd "${SCRIPT_DIR}/../.."

PROJECT_ROOT="$(pwd)"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Trading Desk Wiki  —  $ACTION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Ensure vitepress is available
if ! command -v npx >/dev/null 2>&1; then
    echo "❌ npx is not installed. Install Node.js first."
    exit 1
fi

# Check if node_modules exists or is a symlink
if [[ ! -e "node_modules" ]]; then
    echo "⚠️  node_modules not found. Running from technical-infrastructure/wiki-build/..."
    # Fall back to using the node_modules from wiki-build via the symlink
    if [[ ! -e "node_modules" ]]; then
        echo "❌ No node_modules available. Run: cd technical-infrastructure/wiki-build && npm install"
        exit 1
    fi
fi

VITEPRESS_LOG="/tmp/vitepress-wiki.log"

detect_server() {
    local pid
    pid=$(lsof -i :5173 2>/dev/null | grep LISTEN | awk '{print $2}' | head -1) || true
    if [[ -n "$pid" ]]; then
        # Verify it's a node process
        if ps -p "$pid" -o comm= 2>/dev/null | grep -q node; then
            echo "$pid"
            return 0
        fi
    fi
    echo ""
    return 1
}

stop_server() {
    local pid
    pid=$(detect_server) || true
    if [[ -z "$pid" ]]; then
        echo "ℹ️  Wiki server is already stopped"
        return 0
    fi

    echo "Stopping wiki server (PID $pid)..."
    kill "$pid" 2>/dev/null || true

    # Wait up to 5s for graceful exit
    for i in 1 2 3 4 5; do
        sleep 1
        if ! ps -p "$pid" >/dev/null 2>&1; then
            echo "🛑 Wiki stopped. Port 5173 is free."
            return 0
        fi
    done

    # Force kill
    kill -9 "$pid" 2>/dev/null || true
    sleep 1
    echo "🛑 Wiki stopped (SIGKILL). Port 5173 is free."
}

start_server() {
    local pid
    pid=$(detect_server) || true
    if [[ -n "$pid" ]]; then
        echo "⚠️  Wiki is already running (PID $pid). Use 'restart' to force a restart."
        echo "   → http://localhost:5173/"
        return 0
    fi

    # Clear stale cache
    if [[ -d ".vitepress/cache" ]]; then
        rm -rf .vitepress/cache
    fi

    echo "Starting VitePress from project root..."
    nohup node node_modules/vitepress/bin/vitepress.js dev --host --port 5173 > "$VITEPRESS_LOG" 2>&1 &

    # Wait for server
    echo -n "Waiting for server"
    for i in $(seq 1 30); do
        sleep 1
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
            echo ""
            echo ""
            echo "═══════════════════════════════════════════════════════════════"
            echo ""
            echo "  ✅ Wiki is running at:"
            echo ""
            echo "        http://localhost:5173/"
            echo ""
            echo "     Log: $VITEPRESS_LOG"
            echo "     Root: $PROJECT_ROOT"
            echo ""
            echo "═══════════════════════════════════════════════════════════════"
            return 0
        fi
        echo -n "."
    done
    echo ""
    echo "❌ Server did not start within 30 seconds. Check log: $VITEPRESS_LOG"
    return 1
}

case "$ACTION" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 1
        start_server
        ;;
    status)
        pid=$(detect_server) || true
        if [[ -n "$pid" ]]; then
            echo ""
            echo "  ✅ Wiki is RUNNING (PID $pid)"
            echo "  → http://localhost:5173/"
            echo "  → Log: $VITEPRESS_LOG"
        else
            echo ""
            echo "  🛑 Wiki is STOPPED"
            echo "  → Nothing on port 5173"
        fi
        ;;
    toggle)
        pid=$(detect_server) || true
        if [[ -n "$pid" ]]; then
            stop_server
        else
            start_server
        fi
        ;;
esac

echo ""
