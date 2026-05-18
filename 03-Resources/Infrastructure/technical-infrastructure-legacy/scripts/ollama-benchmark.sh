#!/bin/bash
#
# ollama-benchmark.sh
# Measures tokens/sec via the Ollama HTTP API (localhost:11434).
#
# Usage: ./ollama-benchmark.sh <host/ip> <model> [num_tokens]

set -eo pipefail

HOST="$1"
MODEL="$2"
NUM_TOKENS="${3:-128}"
SSH_USER="friasc"
REPORT_DIR="./lab-specs/benchmarks"

if [ -z "$HOST" ] || [ -z "$MODEL" ]; then
    echo "Usage: $0 <host> <model> [num_tokens]"
    echo "  Example: $0 fnet3 qwen3.5:4b 128"
    exit 1
fi

mkdir -p "$REPORT_DIR"

echo "=== Benchmarking ${MODEL} on ${HOST} ==="
echo "Target tokens: ${NUM_TOKENS}"
echo ""

# Write a remote benchmark script to a temp file
cat > /tmp/ollama-bench-remote.py << 'SCRIPT_EOF'
#!/usr/bin/env python3
import json, time, urllib.request, sys, os

MODEL = sys.argv[1]
NUM_TOKENS = int(sys.argv[2])
NODE = os.uname().nodename

payload = json.dumps({
    'model': MODEL,
    'prompt': 'Explain quantum computing briefly.',
    'stream': False,
    'options': {'num_predict': NUM_TOKENS}
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:11434/api/generate',
    data=payload,
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    start = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    end = time.time()

    duration = end - start
    tokens = data.get('eval_count', 0)
    tps = round(tokens / duration, 2) if duration > 0 else 0

    result = {
        'model': MODEL,
        'node': NODE,
        'tokens_per_sec': tps,
        'total_time_s': round(duration, 2),
        'tokens_generated': tokens,
        'prompt_eval_count': data.get('prompt_eval_count', 0),
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e), 'model': MODEL, 'node': NODE}))
    sys.exit(1)
SCRIPT_EOF

# Copy script to target
scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no /tmp/ollama-bench-remote.py "${SSH_USER}@${HOST}:/tmp/ollama-bench.py" >/dev/null 2>&1

# Pre-load the model to avoid cold-start penalty
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    "curl -fsSL -o /dev/null -d '{\"model\":\"${MODEL}\",\"keep_alive\":\"30m\"}' http://localhost:11434/api/generate" >/dev/null 2>&1 || true

# Run benchmark
RESULT=$(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    "python3 /tmp/ollama-bench.py '${MODEL}' ${NUM_TOKENS}")

echo "$RESULT"
OUTFILE="${REPORT_DIR}/${HOST}-${MODEL//:/_}.json"
echo "$RESULT" > "$OUTFILE"
echo "Saved to $OUTFILE"

# Cleanup
ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "${SSH_USER}@${HOST}" \
    "rm -f /tmp/ollama-bench.py" >/dev/null 2>&1 || true
