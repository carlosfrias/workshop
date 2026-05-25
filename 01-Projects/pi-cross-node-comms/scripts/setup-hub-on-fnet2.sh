#!/usr/bin/env bash
#
# setup-hub-on-fnet2.sh
#
# Installs Bun, copies coms-net hub server code from macOS, and starts
# the hub on fnet2 (192.168.0.142) bound to 0.0.0.0:8080.
#
# Run this script ON fnet2. It assumes SSH access to the macOS machine
# (192.168.0.148) to pull the server code.
#
# Usage: ./setup-hub-on-fnet2.sh [start|stop|restart|status|install]
#
# Default action: full setup + start

set -euo pipefail

# ─── Config ────────────────────────────────────────────────────────────────
MACOS_IP="192.168.0.148"
MACOS_USER="friasc"
MACOS_SERVER_SRC="/Users/friasc/Cloud/carlos-desktop/workshop/01-Projects/pi-cross-node-comms/server/coms-net-server.ts"
LOCAL_SERVER_DIR="$HOME/.pi/coms-net/server"
LOCAL_SERVER_FILE="$LOCAL_SERVER_DIR/coms-net-server.ts"
HUB_HOST="0.0.0.0"
HUB_PORT="8080"
HUB_PROJECT="${PI_COMS_NET_PROJECT:-lab}"
PID_FILE="/tmp/coms-net-hub.pid"
LOG_FILE="/tmp/coms-net-hub.log"
# Auth token — same as macOS hub
AUTH_TOKEN="7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0"

# ─── Colors ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${GREEN}[setup-hub]${NC} $*"; }
warn() { echo -e "${YELLOW}[setup-hub]${NC} $*"; }
err()  { echo -e "${RED}[setup-hub]${NC} $*"; }

# ─── Helpers ───────────────────────────────────────────────────────────────

install_bun() {
    if command -v bun &>/dev/null; then
        log "Bun already installed: $(bun --version)"
        return 0
    fi
    log "Installing Bun..."
    curl -fsSL https://bun.sh/install | bash
    export BUN_INSTALL="$HOME/.bun"
    export PATH="$BUN_INSTALL/bin:$PATH"
    if command -v bun &>/dev/null; then
        log "Bun installed: $(bun --version)"
    else
        err "Bun installation failed."
        exit 1
    fi
}

copy_server_code() {
    mkdir -p "$LOCAL_SERVER_DIR"
    log "Copying coms-net-server.ts from macOS ($MACOS_IP)..."
    scp "${MACOS_USER}@${MACOS_IP}:${MACOS_SERVER_SRC}" "$LOCAL_SERVER_FILE"
    if [ -f "$LOCAL_SERVER_FILE" ]; then
        log "Server code copied ($(wc -l < "$LOCAL_SERVER_FILE") lines)"
    else
        err "Failed to copy server code."
        exit 1
    fi
}

server_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    if ss -tlnp 2>/dev/null | grep -q ":$HUB_PORT "; then
        return 0
    fi
    return 1
}

start_hub() {
    if server_running; then
        warn "Hub already running on port $HUB_PORT."
        curl -s "http://localhost:$HUB_PORT/health" | python3 -m json.tool 2>/dev/null || true
        return 0
    fi

    export PI_COMS_NET_AUTH_TOKEN="$AUTH_TOKEN"
    export PI_COMS_NET_HOST="$HUB_HOST"
    export PI_COMS_NET_PORT="$HUB_PORT"
    export PI_COMS_NET_PROJECT="$HUB_PROJECT"
    export PI_COMS_NET_LOG_QUIET=0
    export PI_COMS_NET_LOG_HEARTBEAT=0

    log "Starting coms-net hub on $HUB_HOST:$HUB_PORT (project=$HUB_PROJECT)..."
    nohup bun run "$LOCAL_SERVER_FILE" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    sleep 2

    if kill -0 "$pid" 2>/dev/null; then
        log "Hub started! PID=$pid"
        sleep 1
        if curl -s "http://localhost:$HUB_PORT/health" >/dev/null 2>&1; then
            log "Health check passed:"
            curl -s "http://localhost:$HUB_PORT/health" | python3 -m json.tool 2>/dev/null || true
        else
            warn "Health check failed. Check: tail -f $LOG_FILE"
        fi
    else
        err "Hub failed to start. Check: cat $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_hub() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            log "Stopping hub (PID=$pid)..."
            kill "$pid"
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            log "Hub stopped."
        fi
        rm -f "$PID_FILE"
    else
        local pid
        pid=$(ss -tlnp 2>/dev/null | grep ":$HUB_PORT " | sed -n 's/.*pid=\([0-9]*\).*/\1/p')
        if [ -n "$pid" ]; then
            log "Stopping hub on port $HUB_PORT (PID=$pid)..."
            kill "$pid"
            log "Hub stopped."
        else
            log "No hub running."
        fi
    fi
}

show_status() {
    echo ""
    echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  coms-net Hub — fnet2 (192.168.0.142)${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}── System Resources ──${NC}"
    echo "  CPU:     $(nproc) cores ($(lscpu 2>/dev/null | grep 'Model name' | sed 's/.*: *//'))"
    echo "  RAM:     $(free -h | awk '/Mem:/{print $2 " total, " $7 " available"}')"
    echo "  Disk:    $(df -h / | awk 'NR==2{print $4 " free / " $2 " total (" $5 " used)"}')"
    echo "  OS:      $(uname -sr)"
    echo ""
    echo -e "${GREEN}── Bun ──${NC}"
    if command -v bun &>/dev/null; then
        echo "  Bun:     $(bun --version) ($(which bun))"
    else
        echo "  Bun:     NOT INSTALLED"
    fi
    echo ""
    echo -e "${GREEN}── Hub Status ──${NC}"
    if server_running; then
        echo "  Hub:     RUNNING on 0.0.0.0:$HUB_PORT"
        if curl -s "http://localhost:$HUB_PORT/health" >/dev/null 2>&1; then
            local health server_id started
            health=$(curl -s "http://localhost:$HUB_PORT/health")
            server_id=$(echo "$health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('server_id','?'))" 2>/dev/null)
            started=$(echo "$health" | python3 -c "import json,sys; print(json.load(sys.stdin).get('started_at','?'))" 2>/dev/null)
            echo "  Server:  $server_id"
            echo "  Started: $started"
            echo "  Project: $HUB_PROJECT"
        else
            echo "  Health:  NOT RESPONDING"
        fi
    else
        echo "  Hub:     NOT RUNNING"
    fi
    echo ""
    echo -e "${GREEN}── LAN Latency (avg from fnet2) ──${NC}"
    for target in fnet1 fnet5 192.168.0.148; do
        local avg
        avg=$(ping -c 3 -q "$target" 2>/dev/null | awk -F/ '/rtt/{print $5}')
        if [ -n "$avg" ]; then
            printf "  %-18s %s ms\n" "$target:" "$avg"
        else
            printf "  %-18s unreachable\n" "$target:"
        fi
    done
    echo ""
}

# ─── Main ───────────────────────────────────────────────────────────────────

ACTION="${1:-start}"

case "$ACTION" in
    start)
        install_bun
        if [ ! -f "$LOCAL_SERVER_FILE" ]; then
            copy_server_code
        else
            log "Server code already present."
        fi
        start_hub
        ;;
    stop)   stop_hub ;;
    restart) stop_hub; sleep 1; start_hub ;;
    status) show_status ;;
    install) install_bun; copy_server_code ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|install}"
        exit 1
        ;;
esac
