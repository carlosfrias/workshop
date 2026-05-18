#!/usr/bin/env bash
# benchmark-lab.sh — Benchmark candidate models on all lab nodes
# Part of TI-016: local-model-pilot lab expansion
#
# Usage: ./benchmark-lab.sh [OPTIONS] [node_list]
# Options:
#   --output-dir DIR    Write benchmark JSON to DIR (default: auto-detect)
#   --num-tokens N    Tokens per benchmark (default: 128)
# Arguments:
#   node_list         comma-separated (default: fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7)
#
# Ansible usage:
#   ansible-playbook -i inventory.yml playbooks/run-pilot-benchmark.yml

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TI_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Parse CLI args
OUTPUT_DIR=""
NUM_TOKENS=128
NODES=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --num-tokens)
            NUM_TOKENS="$2"
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
OUTPUT_DIR="${OUTPUT_DIR:-${DEFAULT_TI_ROOT}/lab-specs/node-benchmarks}"
NODES="${NODES:-fnet1,fnet2,fnet3,fnet4,fnet5,fnet6,fnet7}"
SSH_USER="friasc"
SSH_OPTS="-o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no"

# Candidate models to benchmark per node
CANDIDATE_MODELS=("qwen3.5:4b" "qwen3:8b" "gemma4:e4b")

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "=== Lab Model Benchmark ==="
echo "Output dir: ${OUTPUT_DIR}"
echo "Nodes: ${NODES}"
echo "Models: ${CANDIDATE_MODELS[@]}"
echo "Tokens per benchmark: ${NUM_TOKENS}"
echo ""

mkdir -p "${OUTPUT_DIR}"

IFS=',' read -ra NODE_ARRAY <<< "$NODES"

for NODE in "${NODE_ARRAY[@]}"; do
    NODE=$(echo "$NODE" | xargs)
    echo "--- ${NODE} ---"

    # Test connectivity
    if ! ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "echo PONG" >/dev/null 2>&1; then
        echo "  ⚠️  UNREACHABLE (skipped all models)"
        continue
    fi

    # Get installed models
    INSTALLED=$(ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "ollama list 2>/dev/null | tail -n +2 | awk '{print \$1}'" 2>/dev/null || echo "")

    for MODEL in "${CANDIDATE_MODELS[@]}"; do
        MODEL_SAFE="${MODEL//:/_}"
        OUTFILE="${OUTPUT_DIR}/${NODE}-${MODEL_SAFE}.json"

        # Check if model is installed
        if ! echo "$INSTALLED" | grep -q "^${MODEL}$"; then
            echo "  ⚠️  ${MODEL}: not installed (skipped)"
            cat > "$OUTFILE" << NOMODEL
{
  "node": "${NODE}",
  "model": "${MODEL}",
  "timestamp": "${TIMESTAMP}",
  "status": "not_installed"
}
NOMODEL
            continue
        fi

        echo "  ▶️  ${MODEL}: benchmarking..."

        # Run benchmark inline via SSH
        RESULT=$(ssh ${SSH_OPTS} "${SSH_USER}@${NODE}" "python3 -c '
import json, time, urllib.request, sys
model = \"${MODEL}\"
payload = json.dumps({
    \"model\": model,
    \"prompt\": \"Explain quantum computing briefly.\",
    \"stream\": False,
    \"options\": {\"num_predict\": ${NUM_TOKENS}}
}).encode(\"utf-8\")
req = urllib.request.Request(
    \"http://localhost:11434/api/generate\",
    data=payload, headers={\"Content-Type\": \"application/json\"},
    method=\"POST\"
)
try:
    start = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode(\"utf-8\"))
    end = time.time()
    duration = end - start
    tokens = data.get(\"eval_count\", 0)
    tps = round(tokens / duration, 2) if duration > 0 else 0
    result = {
        \"node\": \"${NODE}\",
        \"model\": model,
        \"timestamp\": \"${TIMESTAMP}\",
        \"status\": \"success\",
        \"tokens_per_sec\": tps,
        \"total_time_s\": round(duration, 2),
        \"tokens_generated\": tokens,
        \"prompt_eval_count\": data.get(\"prompt_eval_count\", 0)
    }
except Exception as e:
    result = {
        \"node\": \"${NODE}\",
        \"model\": model,
        \"timestamp\": \"${TIMESTAMP}\",
        \"status\": \"error\",
        \"error\": str(e)
    }
print(json.dumps(result))
'" 2>/dev/null)

        echo "$RESULT" > "$OUTFILE"
        TPS=$(echo "$RESULT" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tokens_per_sec','N/A'))")
        echo "     ✅ ${MODEL}: ${TPS} t/s"
    done
    echo ""
done

echo "=== Benchmark Complete ==="
echo "Results in: ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"
