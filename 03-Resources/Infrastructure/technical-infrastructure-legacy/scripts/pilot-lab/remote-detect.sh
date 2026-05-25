#!/usr/bin/env bash
# remote-detect.sh — Run hardware detection and model scan on all lab nodes
# Part of TI-016: local-model-pilot lab expansion
#
# Usage: ./remote-detect.sh [OPTIONS] [node_list]
# Options:
#   --output-dir DIR    Write hardware JSON to DIR (default: auto-detect)
#   --lmp-dir DIR       Path to local-model-pilot scripts (default: ~/Cloud/agent-workspace/local-model-pilot)
# Arguments:
#   node_list           comma-separated (default: fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7)
#
# Ansible usage:
#   ansible-playbook -i inventory.yml playbooks/run-pilot-detection.yml

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TI_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DEFAULT_LMP_DIR="${HOME}/Dropbox/agent-workspace/local-model-pilot"

# Parse CLI args
OUTPUT_DIR=""
LMP_DIR=""
NODES=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --lmp-dir)
            LMP_DIR="$2"
            shift 2
            ;;
        --*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            if [ -z "$NODES" ]; then
                NODES="$1"
            fi
            shift
            ;;
    esac
done

# Apply defaults
OUTPUT_DIR="${OUTPUT_DIR:-${DEFAULT_TI_ROOT}/lab-specs/node-hardware}"
LMP_DIR="${LMP_DIR:-${DEFAULT_LMP_DIR}}"
NODES="${NODES:-fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7}"
SSH_USER="friasc"
SSH_OPTS="-o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no"

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "=== Remote Detection for local-model-pilot ==="
echo "Output dir: ${OUTPUT_DIR}"
echo "LMP dir: ${LMP_DIR}"
echo "Nodes: ${NODES}"
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Validate dependencies
if [ ! -f "${LMP_DIR}/scripts/detect-hardware.sh" ]; then
    echo "❌ detect-hardware.sh not found at: ${LMP_DIR}/scripts/detect-hardware.sh" >&2
    echo "   Use --lmp-dir to specify the local-model-pilot directory." >&2
    exit 1
fi

if [ ! -f "${LMP_DIR}/scripts/scan-ollama-models.sh" ]; then
    echo "❌ scan-ollama-models.sh not found at: ${LMP_DIR}/scripts/scan-ollama-models.sh" >&2
    exit 1
fi

mkdir -p "${OUTPUT_DIR}"

IFS=',' read -ra NODE_ARRAY <<< "$NODES"

for NODE in "${NODE_ARRAY[@]}"; do
    NODE=$(echo "$NODE" | xargs)
    echo "--- ${NODE}: Probing ---"

    # Test connectivity
    if ! ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "echo PONG" >/dev/null 2>&1; then
        echo "  ⚠️  ${NODE}: UNREACHABLE (skipped)"
        cat > "${OUTPUT_DIR}/${NODE}-hardware.json" << UNREACH
{
  "node": "${NODE}",
  "timestamp": "${TIMESTAMP}",
  "status": "unreachable",
  "error": "SSH connection failed"
}
UNREACH
        continue
    fi

    echo "  ✅ ${NODE}: Reachable, running detection..."

    # Collect IP address from the remote node
    NODE_IP=$(ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "hostname -I | awk '{print \$1}'" 2>/dev/null | xargs || echo "unknown")

    # Run detect-hardware.sh remotely and capture output
    HW=$(ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "bash -s" 2>/dev/null <"${LMP_DIR}/scripts/detect-hardware.sh")

    RAM_GB=$(echo "$HW" | grep "^Total_RAM_GB:" | awk '{print $2}' || echo "unknown")
    CPU_MODEL=$(echo "$HW" | grep "^CPU:" | cut -d':' -f2- | xargs || echo "unknown")
    CPU_CORES=$(echo "$HW" | grep "^CPU_Cores:" | awk '{print $2}' || echo "unknown")
    SAFE_MODEL_GB=$(echo "$HW" | grep "^Safe_Model_Size_GB:" | awk '{print $2}' || echo "unknown")
    GPU_INFO=$(echo "$HW" | grep "^GPU:" | cut -d':' -f2- | xargs || echo "none")
    OLLAMA_VERSION=$(echo "$HW" | grep "^Ollama_Version:" | cut -d':' -f2- | xargs || echo "not installed")
    OLLAMA_RUNNING=$(echo "$HW" | grep "^Ollama_Running:" | awk '{print $2}' || echo "false")
    INSTALLED_MODELS=$(echo "$HW" | grep "^Installed_Models:" | awk '{print $2}' || echo "0")
    ARCH=$(echo "$HW" | grep "^Architecture:" | awk '{print $2}' || echo "unknown")
    OS=$(echo "$HW" | grep "^OS:" | cut -d':' -f2- | xargs || echo "unknown")
    DISTRO=$(echo "$HW" | grep "^Distribution:" | cut -d':' -f2- | xargs || echo "unknown")

    # Run model scan remotely
    MODELS_RAW=$(ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "bash -s" 2>/dev/null <"${LMP_DIR}/scripts/scan-ollama-models.sh" || echo "[]")

    # Validate MODELS_RAW is valid JSON
    if ! echo "$MODELS_RAW" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
        echo "  ⚠️  ${NODE}: Model scan produced invalid JSON, using empty array"
        MODELS_RAW='[]'
    fi

    cat > "${OUTPUT_DIR}/${NODE}-hardware.json" << RESULT
{
  "node": "${NODE}",
  "timestamp": "${TIMESTAMP}",
  "status": "success",
  "system": {
    "os": "${OS}",
    "distro": "${DISTRO}",
    "arch": "${ARCH}"
  },
  "cpu": {
    "model": "${CPU_MODEL}",
    "cores": "${CPU_CORES}"
  },
  "memory": {
    "total_gb": "${RAM_GB}",
    "safe_model_size_gb": "${SAFE_MODEL_GB}"
  },
  "gpu": {
    "info": "${GPU_INFO}"
  },
  "network": {
    "primary_ip": "${NODE_IP}"
  },
  "ollama": {
    "version": "${OLLAMA_VERSION}",
    "running": "${OLLAMA_RUNNING}",
    "installed_models": ${INSTALLED_MODELS}
  },
  "models": ${MODELS_RAW}
}
RESULT

    echo "  ✅ ${NODE}: Saved ${NODE}-hardware.json"
    echo "     RAM=${RAM_GB}GB, SafeModel=${SAFE_MODEL_GB}GB, Ollama=${OLLAMA_RUNNING}, Models=${INSTALLED_MODELS}"
    echo ""
done

echo "=== Remote Detection Complete ==="
echo "Results in: ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"
