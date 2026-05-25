#!/bin/bash
# =============================================================================
# mount-lab-node.sh — Mount orchestrator workspace on a lab node via SSHFS
# =============================================================================
# Usage: ./mount-lab-node.sh [LAB_HOST]
#   LAB_HOST  defaults to fnet1
# =============================================================================

set -euo pipefail

LAB_HOST="${1:-fnet1}"
MOUNT_POINT="/mnt/trading-desk"
LOCAL_PATH="/Users/friasc/Cloud/workshop"
ORCH_HOST="mac-orchestrator"

echo "========================================"
echo "TI-032 Lab Node SSHFS Mount"
echo "========================================"
echo "Lab node:     $LAB_HOST"
echo "Mount point:  $MOUNT_POINT"
echo "Source:       $LOCAL_PATH (via $ORCH_HOST)"
echo ""

# --- Test SSH ---
echo "[1/4] Testing SSH connectivity to $LAB_HOST..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$LAB_HOST" "echo ok" >/dev/null 2>&1; then
    echo "ERROR: Cannot SSH to $LAB_HOST. Ensure passwordless SSH is configured." >&2
    exit 1
fi
echo "      SSH OK"

# --- Create remote mount point ---
echo "[2/4] Creating mount point on $LAB_HOST..."
ssh "$LAB_HOST" "test -d $MOUNT_POINT || sudo mkdir -p $MOUNT_POINT && sudo chown \$(whoami) $MOUNT_POINT" >/dev/null 2>&1 || {
    echo "ERROR: Cannot create $MOUNT_POINT on $LAB_HOST" >&2
    exit 1
}
echo "      Mount point ready"

# --- Check for existing mount ---
echo "[3/4] Checking for existing mount..."
if ssh "$LAB_HOST" "mount | grep -q '$MOUNT_POINT'" 2>/dev/null; then
    echo "INFO: Already mounted. Skipping."
    ssh "$LAB_HOST" "mount | grep '$MOUNT_POINT'"
    exit 0
fi
echo "      No existing mount"

# --- Mount via SSHFS (from lab node back to orchestrator) ---
echo "[4/4] Mounting $ORCH_HOST:$LOCAL_PATH → $LAB_HOST:$MOUNT_POINT..."
ssh "$LAB_HOST" "sshfs -o reconnect,follow_symlinks ${ORCH_HOST}:${LOCAL_PATH} ${MOUNT_POINT} >/dev/null 2>&1" || {
    echo "ERROR: SSHFS mount failed on $LAB_HOST" >&2
    exit 1
}

# --- Verify ---
sleep 1
if ssh "$LAB_HOST" "mount | grep -q '$MOUNT_POINT'" 2>/dev/null; then
    echo ""
    echo "========================================"
    echo "SUCCESS: Mounted on $LAB_HOST"
    echo "========================================"
    echo "Test remote ls:"
    ssh "$LAB_HOST" "ls -la $MOUNT_POINT/package.json" 2>/dev/null || echo "      (package.json not found — verify source path)"
    exit 0
else
    echo ""
    echo "ERROR: Mount verification failed on $LAB_HOST" >&2
    exit 1
fi
