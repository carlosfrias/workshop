#!/bin/bash
#
# model-depot-sync.sh
# Syncs Ollama model blobs and manifests from a depot node to a target node.
# Avoids repeated WAN downloads by using LAN rsync.
#
# Usage: ./model-depot-sync.sh <depot_ip> <target_ip> [model1,model2,...]
#
# Examples:
#   ./model-depot-sync.sh 192.168.0.143 192.168.0.144 gemma4:e4b
#   ./model-depot-sync.sh 192.168.0.143 192.168.0.144

set -eo pipefail

DEPOT_IP="$1"
TARGET_IP="$2"
MODEL_FILTER="$3"
SSH_USER="friasc"
DEPOT_DIR="/usr/share/ollama/.ollama/models"
TARGET_DIR="/usr/share/ollama/.ollama/models"

if [ -z "$DEPOT_IP" ] || [ -z "$TARGET_IP" ]; then
    echo "Usage: $0 <depot_ip> <target_ip> [model1,model2,...]"
    echo "  Example: $0 192.168.0.143 192.168.0.144 gemma4:e4b,qwen3:8b"
    exit 1
fi

echo "=== Model Depot Sync ==="
echo "Depot:  ${DEPOT_IP}"
echo "Target: ${TARGET_IP}"
echo "Filter: ${MODEL_FILTER:-(all models)}"
echo ""

# Ensure target directory structure exists
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${TARGET_IP}" \
    "mkdir -p ${TARGET_DIR}/blobs ${TARGET_DIR}/manifests/registry.ollama.ai/library" 2>/dev/null || true

# If a filter is provided, sync only specific manifests and their blobs.
if [ -n "$MODEL_FILTER" ]; then
    IFS=',' read -ra MODELS <<< "$MODEL_FILTER"
    for model in "${MODELS[@]}"; do
        echo "--- Syncing model: ${model} ---"
        model_name=$(echo "$model" | cut -d':' -f1)
        model_tag=$(echo "$model" | cut -d':' -f2)
        manifest_path="manifests/registry.ollama.ai/library/${model_name}/${model_tag}"

        # Fetch manifest from depot via scp
        if ! scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
            "${SSH_USER}@${DEPOT_IP}:${DEPOT_DIR}/${manifest_path}" \
            "/tmp/${model_name}-${model_tag}-manifest" >/dev/null 2>&1; then
            echo "Warning: failed to fetch manifest for ${model}"
            continue
        fi

        # Push manifest to target
        if ! scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
            "/tmp/${model_name}-${model_tag}-manifest" \
            "${SSH_USER}@${TARGET_IP}:${TARGET_DIR}/${manifest_path}" >/dev/null 2>&1; then
            echo "Warning: failed to push manifest for ${model}"
            continue
        fi

        # Extract blob digests from the local copy of manifest
        blob_list=$(grep -oE 'sha256-[a-f0-9]+' "/tmp/${model_name}-${model_tag}-manifest" | sort -u || true)
        rm -f "/tmp/${model_name}-${model_tag}-manifest"

        if [ -z "$blob_list" ]; then
            echo "Warning: no blobs found in manifest for ${model}"
            continue
        fi

        # Build a list file for rsync --files-from
        LIST_FILE=$(mktemp)
        for blob in $blob_list; do
            echo "blobs/${blob}" >> "$LIST_FILE"
        done

        # Copy list file to target
        if ! scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$LIST_FILE" \
            "${SSH_USER}@${TARGET_IP}:/tmp/depot-sync-list.txt" >/dev/null 2>&1; then
            echo "Warning: failed to push blob list"
            rm -f "$LIST_FILE"
            continue
        fi
        rm -f "$LIST_FILE"

        # Run rsync on target pulling from depot using the list file
        if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${TARGET_IP}" \
            "cd ${TARGET_DIR} && rsync -avz --files-from=/tmp/depot-sync-list.txt -e 'ssh -o StrictHostKeyChecking=no' ${SSH_USER}@${DEPOT_IP}:${DEPOT_DIR}/ ." >/dev/null 2>&1; then
            echo "Warning: blob rsync failed for ${model}"
        fi
        echo ""
    done
else
    echo "Syncing entire model directory..."
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${TARGET_IP}" \
        "rsync -avz -e 'ssh -o StrictHostKeyChecking=no' ${SSH_USER}@${DEPOT_IP}:${DEPOT_DIR}/ ${TARGET_DIR}/" >/dev/null 2>&1 || {
        echo "Warning: full sync failed"
    }
fi

echo ""
echo "=== Sync complete. Verifying on target... ==="
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${TARGET_IP}" "sudo ollama list" 2>/dev/null || echo "Warning: ollama list failed on target"
