#!/usr/bin/env bash
# Task Worker for Lab Nodes (v2)
# Receives tasks, executes via Ollama, logs performance, verifies results

TASK_DIR="/srv/lab-worker"
PENDING_DIR="$TASK_DIR/pending"
RUNNING_DIR="$TASK_DIR/running"
RESULT_DIR="$TASK_DIR/results"
LOG_SCRIPT="/usr/local/bin/log-performance.py"
VERIFY_SCRIPT="/usr/local/bin/verify-result.py"

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_msg "Task worker starting (PID: $$)"

while true; do
    found_task=false
    for task_file in "$PENDING_DIR"/*.json; do
        [ -e "$task_file" ] || continue
        found_task=true
        id=$(basename "$task_file" .json)
        log_msg "Processing task: $id"
        
        mv "$task_file" "$RUNNING_DIR/$id.json"
        
        # Read task
        task=$(cat "$RUNNING_DIR/$id.json")
        prompt=$(echo "$task" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt',''))")
        model=$(echo "$task" | python3 -c "import sys,json; print(json.load(sys.stdin).get('model','qwen3.5:4b'))")
        
        log_msg "Running inference: model=$model"
        start_time=$(date +%s.%N)
        
        # Run inference
        response=$(curl -s -X POST http://localhost:11434/api/generate \
            -H "Content-Type: application/json" \
            -d "{\"model\":\"$model\",\"prompt\":\"$prompt\",\"stream\":false}" \
            2>&1)
        
        # Also save raw JSON result
        echo "$response" > "$RESULT_DIR/$id.json"
        
        end_time=$(date +%s.%N)
        latency=$(python3 -c "print(f'{$end_time - $start_time:.3f}')")
        
        # Extract token counts from Ollama response
        prompt_eval=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt_eval_count',0))")
        eval_count=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('eval_count',0))")
        
        log_msg "Inference complete: ${latency}s, prompt_tokens=${prompt_eval}, response_tokens=${eval_count}"
        
        # Log performance
        if [ -x "$LOG_SCRIPT" ]; then
            $LOG_SCRIPT "$(hostname)" "$model" "$id" "$latency" "$prompt_eval" "$eval_count" "true" > /dev/null 2>&1 || true
        fi
        
        # Verify result
        if [ -x "$VERIFY_SCRIPT" ]; then
            verify_out=$($VERIFY_SCRIPT "$RESULT_DIR/$id.json" 2>&1)
            verify_status=$(echo "$verify_out" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','UNKNOWN'))")
            log_msg "Verification: $verify_status"
        fi
        
        rm "$RUNNING_DIR/$id.json"
    done
    
    if [ "$found_task" = false ]; then
        sleep 2
    fi
done
