#!/bin/bash
#
# deploy-task-workers.sh — Deploy task-worker.sh to lab nodes
# Handles both local (orchestrator) and remote (fnet2-fnet7) deployment.
# Skips unreachable nodes via SSH connectivity check.
#
# Usage:
#   bash scripts/deploy-task-workers.sh         # Deploy to all reachable nodes
#   bash scripts/deploy-task-workers.sh --local # Deploy locally only
#   bash scripts/deploy-task-workers.sh --dry-run # Print what would happen
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_WORKER_SRC="$SCRIPT_DIR/task-worker.sh"
NODES=(fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7)
DEPLOY_DRY_RUN=false
DEPLOY_LOCAL_ONLY=false

deploy_local() {
    echo "=== Deploy task-worker locally ==="
    local base="$HOME/srv/tasks"
    mkdir -p "$base"/{pending,running,completed}
    cp "$TASK_WORKER_SRC" "$HOME/bin/task-worker.sh" 2>/dev/null || cp "$TASK_WORKER_SRC" "$HOME/srv/tasks/"
    echo "  Worker copied to: $HOME/srv/tasks/task-worker.sh"
    echo "  Task base: $base"
    echo "  Run manually: bash $HOME/srv/tasks/task-worker.sh"
    echo "  Or add to crontab: * * * * * bash $HOME/srv/tasks/task-worker.sh"
}

deploy_remote() {
    local node="$1"
    echo "  Checking $node..."
    
    # SSH connectivity test (3s timeout)
    if ! ssh -o ConnectTimeout=3 -o BatchMode=yes "$node" "hostname" >/dev/null 2>&1; then
        echo "    ❌ $node unreachable — skipping"
        return 1
    fi
    
    echo "    ✅ $node online"
    
    if [ "$DEPLOY_DRY_RUN" = true ]; then
        echo "    Would deploy: task-worker.sh → $node:/srv/tasks/"
        echo "    Would install: systemd timer for task-worker"
        return 0
    fi
    
    # Ensure directories
    ssh "$node" 'sudo mkdir -p /srv/tasks/{pending,running,completed} 2>/dev/null || mkdir -p /srv/tasks/{pending,running,completed}'
    
    # Copy worker
    scp -o ConnectTimeout=5 "$TASK_WORKER_SRC" "friasc@$node:/srv/tasks/task-worker.sh"
    ssh "$node" 'chmod +x /srv/tasks/task-worker.sh'
    
    # Install systemd service (Linux)
    ssh "$node" 'cat > /tmp/task-worker.service <<EOF
[Unit]
Description=TI-011 Task Worker
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash /srv/tasks/task-worker.sh
User=friasc
StandardOutput=journal
StandardError=journal
EOF
sudo cp /tmp/task-worker.service /etc/systemd/system/task-worker.service
sudo systemctl daemon-reload'

    # Install timer (run every 15 seconds)
    ssh "$node" 'cat > /tmp/task-worker.timer <<EOF
[Unit]
Description=TI-011 Task Worker Timer

[Timer]
OnBootSec=30
OnUnitActiveSec=15s
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF
sudo cp /tmp/task-worker.timer /etc/systemd/system/task-worker.timer
sudo systemctl daemon-reload'
    
    # Enable and start
    ssh "$node" 'sudo systemctl enable task-worker.timer && sudo systemctl start task-worker.timer && systemctl is-active task-worker.timer'
    
    echo "    ✅ Deployed to $node"
}

main() {
    # Parse args
    for arg in "$@"; do
        case "$arg" in
            --dry-run) DEPLOY_DRY_RUN=true ;;
            --local) DEPLOY_LOCAL_ONLY=true ;;
        esac
    done
    
    echo "Task Worker Deployment"
    echo "  Dry run: $DEPLOY_DRY_RUN"
    echo "  Local only: $DEPLOY_LOCAL_ONLY"
    echo ""
    
    # Always deploy locally (orchestrator fallback)
    deploy_local
    
    # Deploy to remote nodes
    if [ "$DEPLOY_LOCAL_ONLY" = false ]; then
        echo ""
        echo "=== Deploying to remote nodes ==="
        for node in "${NODES[@]}"; do
            deploy_remote "$node" || true
        done
        echo ""
        echo "Done. Check systemd status on each node with:"
        echo "  ssh friasc@NODE \"systemctl status task-worker.timer\""
    fi
    
    echo ""
    echo "=== Deployment Complete ==="
}

main "$@"
