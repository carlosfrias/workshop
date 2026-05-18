#!/bin/bash
#
# ollama-lab-setup.sh
# Master manual setup script for the Ollama Lab.
# Hardware-aware, tiered, depot-based deployment.
#
# Usage:
#   ./ollama-lab-setup.sh <host> <tier> [depot_ip]
#   ./ollama-lab-setup.sh fnet3 tier1
#   ./ollama-lab-setup.sh fnet4 tier2 192.168.0.143

set -eo pipefail

HOST="$1"
TIER="$2"
DEPOT_IP="${3:-192.168.0.143}"
SSH_USER="friasc"

if [ -z "$HOST" ] || [ -z "$TIER" ]; then
    echo "Usage: $0 <host> <tier1|tier2|orchestrator> [depot_ip]"
    echo ""
    echo "Tiers:"
    echo "  tier1         - Heavy inference (gemma4:e4b, qwen3:8b, qwen3.5:4b)"
    echo "  tier2         - General purpose (qwen3:8b, qwen3.5:4b)"
    echo "  orchestrator  - Local orchestrator (ask user before large models)"
    exit 1
fi

echo "=========================================="
echo "Ollama Lab Setup — Manual Baseline"
echo "=========================================="
echo ""

# Step 1: Hardware validation
echo "[1/6] Extracting hardware specs..."
SPECS=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    'bash -s' < ./technical-infrastructure/scripts/extract-hardware-specs.sh 2>/dev/null)
echo "$SPECS" | head -20
echo ""

# Step 2: Determine models from tier
if [ "$TIER" = "tier1" ]; then
    MODELS=("gemma4:e4b" "qwen3:8b" "qwen3.5:4b")
elif [ "$TIER" = "tier2" ]; then
    MODELS=("qwen3:8b" "qwen3.5:4b")
    # Conditional: try gemma4:e4b if RAM >= 16
    RAM_GB=$(echo "$SPECS" | grep '"total_gb"' | head -1 | grep -o '[0-9]*')
    if [ "${RAM_GB:-0}" -ge 16 ]; then
        MODELS+=("gemma4:e4b")
        echo "Note: Including gemma4:e4b due to sufficient RAM (${RAM_GB}GB)"
    fi
elif [ "$TIER" = "orchestrator" ]; then
    echo "⚠️  ORCHESTRATOR NODE — prompting user before model changes"
    MODELS=("qwen3.5:4b" "gemma4:e4b")
    echo "Suggested models: ${MODELS[*]}"
    read -p "Proceed with these models? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted by user."
        exit 0
    fi
else
    echo "Unknown tier: $TIER"
    exit 1
fi

echo "Target models: ${MODELS[*]}"
echo ""

# Step 3: Install Ollama (if missing)
echo "[2/6] Verifying Ollama installation..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    'command -v ollama >/dev/null || (command -v curl >/dev/null && curl -fsSL https://ollama.com/install.sh | sh)' 2>/dev/null || {
    echo "Warning: Ollama not installed and auto-install failed"
}
echo ""

# Step 4: Ensure service is running
echo "[3/6] Ensuring Ollama service is active..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    'command -v systemctl >/dev/null && sudo systemctl is-active ollama >/dev/null || sudo systemctl start ollama' 2>/dev/null || true
echo ""

# Step 5: Deploy models (from depot if available, else direct pull)
echo "[4/6] Deploying models..."
if [ "$TIER" = "orchestrator" ]; then
    # Orchestrator pulls directly
    for model in "${MODELS[@]}"; do
        echo "Pulling $model (direct)..."
        ollama pull "$model" || echo "Warning: failed to pull $model"
    done
else
    # Lab nodes sync from depot
    for model in "${MODELS[@]}"; do
        echo "Syncing $model from depot ($DEPOT_IP)..."
        ./technical-infrastructure/scripts/model-depot-sync.sh "$DEPOT_IP" "$HOST" "$model" || {
            echo "Depot sync failed for $model, falling back to direct pull..."
            ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
                "OLLAMA_NUM_PARALLEL=1 ollama pull $model" || echo "Warning: direct pull also failed"
        }
    done
fi
echo ""

# Step 6: Validation
echo "[5/6] Validating deployed models..."
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    "ollama list" 2>/dev/null || echo "Warning: ollama list failed"
echo ""

# Step 7: Benchmark (Tier 1 and representative Tier 2)
echo "[6/6] Benchmarking..."
if [ "$TIER" = "tier1" ] || { [ "$TIER" = "tier2" ] && [ "$HOST" = "fnet2" ]; }; then
    for model in "${MODELS[@]}"; do
        echo "Benchmarking $model..."
        ./technical-infrastructure/scripts/ollama-benchmark.sh "$HOST" "$model" 128 || echo "Benchmark failed"
    done
else
    echo "Skipping benchmark for this tier/host"
fi
echo ""

echo "=========================================="
echo "Setup complete for $HOST ($TIER)"
echo "=========================================="
