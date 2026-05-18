#!/bin/bash
#
# task-worker.sh — Lab Node Task Worker (MVP)
# Installed on fnet1-fnet7. Runs via cron or systemd timer.
# Polls /srv/tasks/pending for new task JSON, executes, writes result.
#
TASK_BASE="/srv/tasks"
PENDING="$TASK_BASE/pending"
RUNNING="$TASK_BASE/running"
COMPLETED="$TASK_BASE/completed"
LOG="$TASK_BASE/worker.log"

# Ensure directories exist
for dir in "$PENDING" "$RUNNING" "$COMPLETED"; do
    sudo mkdir -p "$dir" 2>/dev/null || mkdir -p "$dir"
done

# Process all pending tasks
shopt -s nullglob
for task_file in "$PENDING"/*.json; do
    [ -f "$task_file" ] || continue

    task_id=$(basename "$task_file" .json)
    #echo "$(date -Iseconds) [$task_id] Claiming task" >> "$LOG"

    # Move to running (atomic rename — claim)
    # If another worker claimed it, skip
    if ! mv "$task_file" "$RUNNING/$task_id.json" 2>/dev/null; then
        continue
    fi

    # Parse command
    cmd=$(python3 -c "import json,sys; d=json.load(open('$RUNNING/$task_id.json')); print(d.get('command',''))")
    task_type=$(python3 -c "import json,sys; d=json.load(open('$RUNNING/$task_id.json')); print(d.get('type','shell'))")

    # Execute
    stdout=$(mktemp)
    stderr=$(mktemp)
    start_time=$(date +%s)

    if [ "$task_type" = "ansible" ]; then
        # Special handling for ansible playbooks
        timeout=$((3600))  # 1 hour
        eval "$cmd" >"$stdout" 2>"$stderr"; rc=$?
    else
        # Standard shell execution with timeout
        timeout=$((3600))
        eval "$cmd" >"$stdout" 2>"$stderr"; rc=$?
    fi

    elapsed=$(( $(date +%s) - start_time ))
    out=$(cat "$stdout" 2>/dev/null | head -c 50000 | sed 's/"/\\"/g' | tr '\n' ' ')
    err=$(cat "$stderr" 2>/dev/null | head -c 10000 | sed 's/"/\\"/g' | tr '\n' ' ')
    rm -f "$stdout" "$stderr"

    # ── Autonomous 413 Detection ─────────────────────────────────────────
    # Check if stderr/stdout contains 413 error indicators
    is_413=0
    if echo "$err" | grep -qi "413\|entity too large\|context length\|token limit\|max tokens"; then
        is_413=1
    elif echo "$out" | grep -qi "413\|entity too large\|context length\|token limit\|max tokens"; then
        is_413=1
    fi

    # Build result JSON
    python3 - "$RUNNING/$task_id.json" "$rc" "$elapsed" "$out" "$err" "$is_413" <<PYEOF
import json, sys, re

with open(sys.argv[1], 'r') as f:
    task = json.load(f)

rc = int(sys.argv[2])
is_413 = int(sys.argv[6])

# Detect 413 from error text even if rc is not obviously 413
err_text = sys.argv[5]
out_text = sys.argv[4]
combined = (err_text + " " + out_text).lower()
413_indicators = [
    "413", "request entity too large", "payload too large",
    "context length exceeded", "token limit exceeded", "max tokens exceeded",
    "input length exceeded", "sequence length", "too many tokens"
]
detected_413 = is_413 or any(ind in combined for ind in 413_indicators)

# Parse node/model from task if present
node = task.get('node', '?')
model = task.get('model', task.get('ollama_model', '?'))

if rc == 0:
    task['status'] = 'completed'
elif detected_413:
    task['status'] = 'failed_413'
    task['failure_category'] = 'payload_too_large'
    # Parse token info if available
    tok_match = re.search(r'(\d+)\s*tokens?', err_text + out_text)
    if tok_match:
        task['detected_tokens'] = int(tok_match.group(1))
    lim_match = re.search(r'limit\s*(?:of|is)?\s*(\d+)', err_text + out_text, re.I)
    if lim_match:
        task['detected_limit'] = int(lim_match.group(1))
    # Recovery hint for orchestrator
    task['recovery_needed'] = True
    task['recovery_strategy_hint'] = 'auto_413_recovery'
else:
    task['status'] = 'failed'

task['rc'] = rc
task['elapsed_seconds'] = int(sys.argv[3])
task['stdout'] = sys.argv[4]
task['stderr'] = sys.argv[5]
task['completed'] = __import__('datetime').datetime.now().isoformat()

with open('$COMPLETED/$task_id.json', 'w') as f:
    json.dump(task, f, indent=2)
PYEOF

    # Remove running
    rm -f "$RUNNING/$task_id.json"
    #echo "$(date -Iseconds) [$task_id] Completed (rc=$rc, elapsed=${elapsed}s)" >> "$LOG"

done
shopt -u nullglob
