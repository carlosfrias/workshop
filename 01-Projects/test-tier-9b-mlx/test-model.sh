#!/bin/bash
# test-model.sh — Run 3 concurrent subagent DE benchmark for a single model
# Usage: ./test-model.sh <model-id> <maxTokens> <thinking-level>
set -euo pipefail

MODEL_ID="${1:?Usage: test-model.sh <model-id> <maxTokens> <thinking-level>}"
MAX_TOKENS="${2:-4096}"
THINKING="${3:-medium}"
TIMEOUT=300
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="/Users/friasc/Cloud/carlos-desktop/workshop/01-Projects/test-tier-9b-mlx"
ARTIFACT_DIR="$LOG_DIR/artifacts"
HEALTH_LOG="$ARTIFACT_DIR/${MODEL_ID//:/_}-health.csv"
RESULT_FILE="$ARTIFACT_DIR/${MODEL_ID//:/_}-results.txt"

echo "=== TESTING: $MODEL_ID ==="
echo "   maxTokens: $MAX_TOKENS"
echo "   thinking: $THINKING"
echo "   timeout:  ${TIMEOUT}s"
echo "   time:     $(date)"
echo ""

# Baseline health snapshot
echo "timestamp,ram_pct,swap_mb,load" > "$HEALTH_LOG"
python3 -c "
import subprocess, time
r = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
total = int(r.stdout.strip())
# Quick RAM % from vm_stat
import os
result = os.popen('vm_stat').read()
lines = result.strip().split('\n')
pages = {}
for line in lines:
    if ':' in line:
        k, v = line.split(':')
        pages[k.strip()] = int(v.strip().rstrip('.'))
page_size = 16384
active = pages.get('Pages active', 0)
wired = pages.get('Pages wired down', 0)
used = (active + wired) * page_size
pct = (used / total) * 100
swap = os.popen('sysctl vm.swapusage').read().split()
swap_used = [s for i,s in enumerate(swap) if s == 'used' and i+1 < len(swap)]
swap_mb = float(swap_used[0+1]) if swap_used else 0
# Try to get a numeric; parse sysctl output directly
import re
m = re.search(r'used\\s*=\\s*([\\d.]+)M', os.popen('sysctl vm.swapusage').read())
swap_mb = float(m.group(1)) if m else 0
load = float(os.popen('sysctl -n vm.loadavg').read().split()[1])
print(f'{time.time():.0f},{pct:.1f},{swap_mb:.0f},{load:.2f}')
" >> "$HEALTH_LOG"

echo "Baseline health captured"
echo ""

# Run 3 concurrent agents using pi subagent
echo "Launching 3 concurrent subagents..."
START_TIME=$(date +%s)

# We'll use the Agent tool via a script that creates 3 parallel agents
# Each agent gets a specific claim to validate (same as previous tests)
CLAIM_1="Claim: Reducing maxTokens from 16000 to 4096 was the key fix that made qwen3.5:4b viable on 16GB hardware. Investigate and report whether this is accurate."
CLAIM_2="Claim: A model's context window size is the dominant factor in DE orchestration stability on constrained hardware, not model weight size. Investigate and report."
CLAIM_3="Claim: gemma4:e4b is the best local model choice for DE orchestrated workloads on M1 Pro 16GB. Investigate and report whether this still holds with new 9b and MLX variants."

echo "Agent 1: $CLAIM_1"
echo "Agent 2: $CLAIM_2"
echo "Agent 3: $CLAIM_3"

# Run agents sequentially for safety on 16GB (concurrent would compete for RAM)
# But we time them to see total wall time
echo ""
echo "--- Running Agent 1 ---"
AGEND1=$(date +%s)
timeout $TIMEOUT pi agent run --model "ollama/$MODEL_ID" --thinking "$THINKING" --max-turns 10 --prompt "$CLAIM_1" 2>&1 | tee "$ARTIFACT_DIR/${MODEL_ID//:/_}-agent1.md" || echo "Agent 1 timed out or errored"
AEND1=$(date +%s)
ADUR1=$((AEND1 - AGEND1))
echo "Agent 1 duration: ${ADUR1}s"

# Health snapshot
python3 -c "
import subprocess, time, re, os
r = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
total = int(r.stdout.strip())
result = os.popen('vm_stat').read()
lines = result.strip().split('\n')
pages = {}
for line in lines:
    if ':' in line:
        k, v = line.split(':')
        pages[k.strip()] = int(v.strip().rstrip('.'))
page_size = 16384
used = (pages.get('Pages active', 0) + pages.get('Pages wired down', 0)) * page_size
pct = (used / total) * 100
m = re.search(r'used\\s*=\\s*([\\d.]+)M', os.popen('sysctl vm.swapusage').read())
swap_mb = float(m.group(1)) if m else 0
load = float(os.popen('sysctl -n vm.loadavg').read().split()[1])
print(f'{time.time():.0f},{pct:.1f},{swap_mb:.0f},{load:.2f}')
" >> "$HEALTH_LOG"

echo "--- Running Agent 2 ---"
AGEND2=$(date +%s)
timeout $TIMEOUT pi agent run --model "ollama/$MODEL_ID" --thinking "$THINKING" --max-turns 10 --prompt "$CLAIM_2" 2>&1 | tee "$ARTIFACT_DIR/${MODEL_ID//:/_}-agent2.md" || echo "Agent 2 timed out or errored"
AEND2=$(date +%s)
ADUR2=$((AEND2 - AGEND2))
echo "Agent 2 duration: ${ADUR2}s"

# Health snapshot
python3 -c "
import subprocess, time, re, os
r = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
total = int(r.stdout.strip())
result = os.popen('vm_stat').read()
lines = result.strip().split('\n')
pages = {}
for line in lines:
    if ':' in line:
        k, v = line.split(':')
        pages[k.strip()] = int(v.strip().rstrip('.'))
page_size = 16384
used = (pages.get('Pages active', 0) + pages.get('Pages wired down', 0)) * page_size
pct = (used / total) * 100
m = re.search(r'used\\s*=\\s*([\\d.]+)M', os.popen('sysctl vm.swapusage').read())
swap_mb = float(m.group(1)) if m else 0
load = float(os.popen('sysctl -n vm.loadavg').read().split()[1])
print(f'{time.time():.0f},{pct:.1f},{swap_mb:.0f},{load:.2f}')
" >> "$HEALTH_LOG"

echo "--- Running Agent 3 ---"
AGEND3=$(date +%s)
timeout $TIMEOUT pi agent run --model "ollama/$MODEL_ID" --thinking "$THINKING" --max-turns 10 --prompt "$CLAIM_3" 2>&1 | tee "$ARTIFACT_DIR/${MODEL_ID//:/_}-agent3.md" || echo "Agent 3 timed out or errored"
AEND3=$(date +%s)
ADUR3=$((AEND3 - AGEND3))
echo "Agent 3 duration: ${ADUR3}s"

END_TIME=$(date +%s)
TOTAL=$((END_TIME - START_TIME))

echo ""
echo "=== RESULTS: $MODEL_ID ==="
echo "Agent 1: ${ADUR1}s"
echo "Agent 2: ${ADUR2}s"
echo "Agent 3: ${ADUR3}s"
echo "Total wall time: ${TOTAL}s"