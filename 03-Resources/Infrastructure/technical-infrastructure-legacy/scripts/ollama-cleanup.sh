#!/bin/bash
#
# ollama-cleanup.sh
# Removes all Ollama models from target node(s) to prepare for clean re-deployment.
# Stops service, purges models, verifies empty state.
#
# Usage:
#   ./ollama-cleanup.sh <host/ip>
#   ./ollama-cleanup.sh all        # clean all lab nodes
#   ./ollama-cleanup.sh --local    # clean localhost (orchestrator)

set -eo pipefail

TARGET="$1"
SSH_USER="friasc"
LAB_NODES=(fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7)

cleanup_node() {
    local host="$1"
    echo "=== Cleaning Ollama on ${host} ==="
    
    if [ "$host" = "localhost" ] || [ "$host" = "127.0.0.1" ]; then
        host=""
    fi
    
    if [ -n "$host" ]; then
        ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${host}" \
            "sudo systemctl stop ollama 2>/dev/null || true
            ollama list 2>/dev/null | tail -n +2 | awk '{print \$1}' | xargs -r ollama rm 2>/dev/null || true
            sudo rm -rf /usr/share/ollama/.ollama/models/* 2>/dev/null || true
            sudo systemctl start ollama 2>/dev/null || true
            echo 'Done. Verifying:'
            ollama list 2>/dev/null || echo '(none)'
            echo 'Disk usage:'
            sudo du -sh /usr/share/ollama/.ollama/models/ 2>/dev/null || echo '0'"
    else
        # Local cleanup (orchestrator / macOS)
        ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' | xargs -r ollama rm 2>/dev/null || true
        rm -rf ~/.ollama/models/* 2>/dev/null || true
        echo "Done. Verifying:"
        ollama list 2>/dev/null || echo "(none)"
        echo "Disk usage:"
        du -sh ~/.ollama/models/ 2>/dev/null || echo "0"
    fi
    echo ""
}

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <host> | all | --local"
    echo "  Examples:"
    echo "    $0 fnet3          # clean single node"
    echo "    $0 all             # clean all lab nodes"
    echo "    $0 --local         # clean orchestrator (this machine)"
    exit 1
fi

if [ "$TARGET" = "all" ]; then
    echo "WARNING: This will remove ALL Ollama models from ALL lab nodes."
    echo "Nodes: ${LAB_NODES[*]}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    for node in "${LAB_NODES[@]}"; do
        cleanup_node "$node"
    done
elif [ "$TARGET" = "--local" ]; then
    echo "WARNING: This will remove ALL Ollama models from this machine (orchestrator)."
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted."
        exit 0
    fi
    cleanup_node ""
else
    cleanup_node "$TARGET"
fi

echo "Cleanup complete."
