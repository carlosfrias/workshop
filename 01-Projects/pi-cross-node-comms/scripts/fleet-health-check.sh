#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# fleet-health-check.sh — Validate health across all fleet nodes
# ═══════════════════════════════════════════════════════════════════════════════
# Usage: ./fleet-health-check.sh [--nodes NODE1,NODE2,...] [--verbose]
#
# Checks:
#   1. Disk usage (per node)
#   2. LVM utilization (detect 100G vs full disk)
#   3. tmux socket persistence ($HOME/.tmux)
#   4. Hub connectivity (SSE connection status)
#   5. Partial ollama blobs (interrupted model pulls)
#   6. Ollama load status (models loaded vs available)
#
# Output: Pass/fail per node with one-liner fix suggestions
# ═══════════════════════════════════════════════════════════════════════════════
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Configuration ──
HUB_HOST="${PI_COMS_NET_HUB_HOST:-192.168.0.142}"
HUB_PORT="${PI_COMS_NET_HUB_PORT:-8080}"
HUB_URL="http://${HUB_HOST}:${HUB_PORT}"

# Lab nodes from Ansible inventory
declare -A NODES=(
    ["fnet1"]="192.168.0.141"
    ["fnet2"]="192.168.0.142"  # Hub host
    ["fnet3"]="192.168.0.143"
    ["fnet4"]="192.168.0.144"
    ["fnet5"]="192.168.0.145"
    ["fnet6"]="192.168.0.146"
    ["fnet7"]="192.168.0.147"
)

# Thresholds
DISK_WARN=80
DISK_CRIT=90
LVM_EXPECTED_PERCENT=95  # Should be using ~95-100% of VG after expansion

# ── Parse flags ──
VERBOSE=false
NODE_FILTER=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --nodes) NODE_FILTER="$2"; shift 2 ;;
        --verbose|-v) VERBOSE=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--nodes NODE1,NODE2,...] [--verbose]"
            echo ""
            echo "Checks all fleet nodes for:"
            echo "  - Disk usage (warn: ${DISK_WARN}%, crit: ${DISK_CRIT}%)"
            echo "  - LVM utilization (expected: ${LVM_EXPECTED_PERCENT}%+)"
            echo "  - tmux socket persistence (\$HOME/.tmux)"
            echo "  - Hub connectivity (SSE connection)"
            echo "  - Partial ollama blobs (interrupted pulls)"
            echo "  - Ollama load status"
            echo ""
            echo "Examples:"
            echo "  $0                     # Check all nodes"
            echo "  $0 --nodes fnet1,fnet3 # Check specific nodes"
            echo "  $0 -v                  # Verbose output"
            exit 0 ;;
        *) echo "Unknown flag: $1" >&2; exit 1 ;;
    esac
done

# ── Helper Functions ──

log() {
    if [[ "$VERBOSE" == true ]]; then
        echo "  [DEBUG] $*" >&2
    fi
}

# SSH command wrapper
ssh_cmd() {
    local node="$1"
    local host="$2"
    local cmd="$3"
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "friasc@${host}" "$cmd" 2>/dev/null
}

# Check disk usage
check_disk() {
    local node="$1"
    local host="$2"
    
    local result
    result=$(ssh_cmd "$node" "$host" "df -h / | awk 'NR==2 {gsub(/%/,\"\"); print \$5}'")
    
    if [[ -z "$result" ]]; then
        echo "FAIL"
        return 1
    fi
    
    local usage="${result%.*}"  # Remove decimal
    if [[ "$usage" -ge "$DISK_CRIT" ]]; then
        echo "CRIT:${usage}"
    elif [[ "$usage" -ge "$DISK_WARN" ]]; then
        echo "WARN:${usage}"
    else
        echo "OK:${usage}"
    fi
}

# Check LVM utilization
check_lvm() {
    local node="$1"
    local host="$2"
    
    # Get LV size and VG size
    local lv_info
    lv_info=$(ssh_cmd "$node" "$host" "sudo lvs ubuntu-vg/ubuntu-lv --noheadings --units g -o lv_size 2>/dev/null | tr -d ' g'")
    local vg_info
    vg_info=$(ssh_cmd "$node" "$host" "sudo vgs ubuntu-vg --noheadings --units g -o vg_size 2>/dev/null | tr -d ' g'")
    
    if [[ -z "$lv_info" || -z "$vg_info" ]]; then
        echo "FAIL"
        return 1
    fi
    
    # Calculate percentage
    local percent
    percent=$(awk "BEGIN {printf \"%.0f\", ($lv_info / $vg_info) * 100}")
    
    if [[ "$percent" -lt 50 ]]; then
        echo "WARN:${percent}%"
    else
        echo "OK:${percent}%"
    fi
}

# Check tmux socket persistence
check_tmux() {
    local node="$1"
    local host="$2"
    
    local socket_exists
    socket_exists=$(ssh_cmd "$node" "$host" "test -d \$HOME/.tmux && echo 'ok' || echo 'missing'")
    
    if [[ "$socket_exists" == "ok" ]]; then
        # Check if pi-agent session exists
        local session_exists
        session_exists=$(ssh_cmd "$node" "$host" "tmux has-session -t pi-agent 2>/dev/null && echo 'ok' || echo 'missing'")
        
        if [[ "$session_exists" == "ok" ]]; then
            echo "OK"
        else
            echo "WARN:no-session"
        fi
    else
        echo "FAIL:no-socket"
    fi
}

# Check hub connectivity
check_hub() {
    local node="$1"
    local host="$2"
    
    # Check if this is the hub host
    if [[ "$host" == "$HUB_HOST" ]]; then
        # Check Docker container health
        local health
        health=$(ssh_cmd "$node" "$host" "docker inspect --format='{{.State.Health.Status}}' coms-net-hub 2>/dev/null || echo 'unknown'")
        
        if [[ "$health" == "healthy" ]]; then
            echo "OK(HUB)"
        elif [[ "$health" == "unknown" ]]; then
            echo "WARN:docker-not-running"
        else
            echo "FAIL:$health"
        fi
        return
    fi
    
    # For worker nodes, check if they can reach the hub
    local response
    response=$(ssh_cmd "$node" "$host" "curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 ${HUB_URL}/health 2>/dev/null || echo '000'")
    
    if [[ "$response" == "200" ]]; then
        echo "OK"
    elif [[ "$response" == "000" ]]; then
        echo "FAIL:unreachable"
    else
        echo "WARN:http-${response}"
    fi
}

# Check for partial ollama blobs
check_ollama_blobs() {
    local node="$1"
    local host="$2"
    
    # Look for partial downloads in ollama blob directory
    local partial_count
    partial_count=$(ssh_cmd "$node" "$host" "find /usr/share/ollama/.ollama/blobs -name 'partial-*' 2>/dev/null | wc -l | tr -d ' '")
    
    if [[ "$partial_count" -gt 0 ]]; then
        echo "WARN:${partial_count}-partial"
    else
        echo "OK"
    fi
}

# Check ollama load status
check_ollama_status() {
    local node="$1"
    local host="$2"
    
    # Check if ollama service is running
    local status
    status=$(ssh_cmd "$node" "$host" "systemctl is-active ollama 2>/dev/null || echo 'inactive'")
    
    if [[ "$status" == "active" ]]; then
        # Check if models are loaded
        local model_count
        model_count=$(ssh_cmd "$node" "$host" "ollama list 2>/dev/null | wc -l | tr -d ' '")
        
        if [[ "$model_count" -ge 3 ]]; then
            echo "OK:${model_count}-models"
        else
            echo "WARN:only-${model_count}-models"
        fi
    else
        echo "FAIL:$status"
    fi
}

# ── Main Execution ──

echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Fleet Health Check — $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Hub: ${HUB_URL}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Build node list
if [[ -n "$NODE_FILTER" ]]; then
    IFS=',' read -ra SELECTED_NODES <<< "$NODE_FILTER"
    declare -A FILTERED_NODES
    for node in "${SELECTED_NODES[@]}"; do
        if [[ -v NODES[$node] ]]; then
            FILTERED_NODES[$node]="${NODES[$node]}"
        else
            echo "⚠️  Unknown node: $node" >&2
        fi
    done
else
    declare -A FILTERED_NODES
    FILTERED_NODES=("${NODES[@]}")
fi

# Summary counters
PASS=0
WARN=0
FAIL=0

# Check each node
printf "%-8s %-6s %-8s %-10s %-15s %-12s %-12s %-20s\n" \
    "NODE" "STATUS" "DISK" "LVM" "TMUX" "HUB" "OLLAMA" "FIX"
printf "%-8s %-6s %-8s %-10s %-15s %-12s %-12s %-20s\n" \
    "----" "------" "----" "---" "----" "---" "------" "---"

for node in "${!FILTERED_NODES[@]}"; do
    host="${FILTERED_NODES[$node]}"
    
    log "Checking $node ($host)..."
    
    # Run all checks
    disk_result=$(check_disk "$node" "$host")
    lvm_result=$(check_lvm "$node" "$host")
    tmux_result=$(check_tmux "$node" "$host")
    hub_result=$(check_hub "$node" "$host")
    ollama_blobs=$(check_ollama_blobs "$node" "$host")
    ollama_status=$(check_ollama_status "$node" "$host")
    
    # Determine overall status
    overall="PASS"
    fix_suggestions=()
    
    # Process disk result
    if [[ "$disk_result" == "FAIL" ]]; then
        overall="FAIL"
        fix_suggestions+=("check-ssh")
    elif [[ "$disk_result" == CRIT:* ]]; then
        overall="FAIL"
        fix_suggestions+=("free-disk-space")
    elif [[ "$disk_result" == WARN:* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("monitor-disk")
    fi
    
    # Process LVM result
    if [[ "$lvm_result" == "FAIL" ]]; then
        overall="FAIL"
        fix_suggestions+=("check-lvm")
    elif [[ "$lvm_result" == WARN:* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("lvextend")
    fi
    
    # Process tmux result
    if [[ "$tmux_result" == "FAIL"* ]]; then
        overall="FAIL"
        fix_suggestions+=("fix-tmux-socket")
    elif [[ "$tmux_result" == "WARN"* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("restart-agent")
    fi
    
    # Process hub result
    if [[ "$hub_result" == "FAIL"* ]]; then
        overall="FAIL"
        fix_suggestions+=("check-hub-connectivity")
    elif [[ "$hub_result" == "WARN"* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("verify-hub")
    fi
    
    # Process ollama blobs
    if [[ "$ollama_blobs" == WARN:* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("clean-partial-blobs")
    fi
    
    # Process ollama status
    if [[ "$ollama_status" == "FAIL"* ]]; then
        overall="FAIL"
        fix_suggestions+=("start-ollama")
    elif [[ "$ollama_status" == WARN:* ]]; then
        [[ "$overall" == "PASS" ]] && overall="WARN"
        fix_suggestions+=("pull-models")
    fi
    
    # Build fix suggestion string
    local fix_str="—"
    if [[ ${#fix_suggestions[@]} -gt 0 ]]; then
        fix_str="${fix_suggestions[0]}"
        if [[ ${#fix_suggestions[@]} -gt 1 ]]; then
            fix_str+=" (+$(( ${#fix_suggestions[@]} - 1 )) more)"
        fi
    fi
    
    # Print status line
    local status_icon
    case "$overall" in
        PASS) status_icon="✅"; ((PASS++)) ;;
        WARN) status_icon="⚠️ "; ((WARN++)) ;;
        FAIL) status_icon="❌"; ((FAIL++)) ;;
    esac
    
    # Extract values for display
    local disk_display="${disk_result#*:}"
    [[ "$disk_result" == "FAIL" ]] && disk_display="FAIL"
    
    local lvm_display="${lvm_result#*:}"
    [[ "$lvm_result" == "FAIL" ]] && lvm_display="FAIL"
    
    printf "%-8s %-6s %-8s %-10s %-15s %-12s %-12s %-20s\n" \
        "$node" "$status_icon $overall" "$disk_display" "$lvm_display" "$tmux_result" "$hub_result" "$ollama_status" "$fix_str"
    
    log "  Disk: $disk_result"
    log "  LVM: $lvm_result"
    log "  Tmux: $tmux_result"
    log "  Hub: $hub_result"
    log "  Blobs: $ollama_blobs"
    log "  Ollama: $ollama_status"
done

# Print summary
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  Summary: ${PASS} PASS  |  ${WARN} WARN  |  ${FAIL} FAIL"
echo "═══════════════════════════════════════════════════════════════════════════"

# Exit with error if any failures
if [[ "$FAIL" -gt 0 ]]; then
    echo ""
    echo "❌ ${FAIL} node(s) require immediate attention"
    exit 1
elif [[ "$WARN" -gt 0 ]]; then
    echo ""
    echo "⚠️  ${WARN} node(s) have warnings (review recommended)"
    exit 0
else
    echo ""
    echo "✅ All nodes healthy"
    exit 0
fi
