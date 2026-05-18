#!/bin/bash
# =============================================================================
# unmount-lab-node.sh — Unmount orchestrator workspace from a lab node
# =============================================================================
# Usage: ./unmount-lab-node.sh [LAB_HOST]
#   LAB_HOST  defaults to fnet1
# =============================================================================

set -euo pipefail

LAB_HOST="${1:-fnet1}"
MOUNT_POINT="/mnt/trading-desk"

echo "========================================"
echo "TI-032 Lab Node Unmount"
echo "========================================"
echo "Lab node:     $LAB_HOST"
echo "Mount point:  $MOUNT_POINT"
echo ""

# --- Test SSH ---
echo "[1/3] Testing SSH connectivity..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$LAB_HOST" "echo ok" >/dev/null 2>&1; then
    echo "ERROR: Cannot SSH to $LAB_HOST" >&2
    exit 1
fi
echo "      SSH OK"

# --- Check if mounted ---
echo "[2/3] Checking mount state..."
if ! ssh "$LAB_HOST" "mount | grep -q '$MOUNT_POINT'" 2>/dev/null; then
    echo "INFO: $MOUNT_POINT is not currently mounted on $LAB_HOST"
    exit 0
fi
echo "      Mount detected — proceeding with unmount"

# --- Unmount ---
echo "[3/3] Unmounting $MOUNT_POINT..."
ssh "$LAB_HOST" "fusermount -u $MOUNT_POINT 2>/dev/null || umount -f $MOUNT_POINT 2>/dev/null || sudo umount -f $MOUNT_POINT 2>/dev/null || true" >/dev/null 2>&1
sleep 1

# --- Verify ---
if ssh "$LAB_HOST" "mount | grep -q '$MOUNT_POINT'" 2>/dev/null; then
    echo "WARNING: Lazy unmount in progress. Checking lsof..."
    ssh "$LAB_HOST" "lsof $MOUNT_POINT 2>/dev/null || echo 'No open handles'" >/dev/null 2>&1 || true
    # Try force unmount again
    ssh "$LAB_HOST" "sudo umount -fl $MOUNT_POINT 2>/dev/null || true" >/dev/null 2>&1
fi

if ! ssh "$LAB_HOST" "mount | grep -q '$MOUNT_POINT'" 2>/dev/null; then
    echo ""
    echo "========================================"
    echo "SUCCESS: Unmounted from $LAB_HOST"
    echo "========================================"
    exit 0
else
    echo ""
    echo "ERROR: Unmount failed on $LAB_HOST" >&2
    ssh "$LAB_HOST" "mount | grep '$MOUNT_POINT'" 2>/dev/null || true
    exit 1
fi
