#!/usr/bin/env bash
# Task Worker for Orchestrator (fnet0)
# Processes tasks from ~/.pi/lab-worker/pending/ queue
# Runs as background process or systemd service (Linux) / launchd (macOS)

QUEUE_DIR="$HOME/.pi/lab-worker"
PENDING_DIR="$QUEUE_DIR/pending"
RUNNING_DIR="$QUEUE_DIR/running"
RESULT_DIR="$QUEUE_DIR/results"
LOG_DIR="$QUEUE_DIR/logs"

# Ensure directories exist
mkdir -p "$PENDING_DIR" "$RUNNING_DIR" "$RESULT_DIR" "$LOG_DIR"

log_msg() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/worker.log"
}

log_msg "Task worker for fnet0 starting (PID: $$)"

while true; do
    found_task=false
    
    for task_file in "$PENDING_DIR"/*.json; do
        [ -e "$task_file" ] || continue
        
        found_task=true
        id=$(basename "$task_file" .json)
        log_msg "Processing task: $id"
        
        # Move to running
        mv "$task_file" "$RUNNING_DIR/$id.json"
        
        # Read task
        task=$(cat "$RUNNING_DIR/$id.json")
        prompt=$(echo "$task" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt',''))")
        model=$(echo "$task" | python3 -c "import sys,json; print(json.load(sys.stdin).get('model','qwen3.5:4b'))")
        
        log_msg "Running inference: model=$model"
        start_time=$(date +%s.%N)
        
        # Run inference via Ollama (local on Mac)
        response=$(curl -s -X POST http://localhost:11434/api/generate \
            -H "Content-Type: application/json" \
            -d "{\"model\":\"$model\",\"prompt\":\"$prompt\",\"stream\":false}" \
            2>&1)
        
        # Save result
        echo "$response" > "$RESULT_DIR/$id.json"
        
        end_time=$(date +%s.%N)
        latency=$(python3 -c "print(f'{$end_time - $start_time:.3f}')")
        
        # Extract token counts
        prompt_eval=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('prompt_eval_count',0))" 2>/dev/null || echo "0")
        eval_count=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('eval_count',0))" 2>/dev/null || echo "0")
        
        log_msg "Inference complete: ${latency}s, prompt_tokens=${prompt_eval}, response_tokens=${eval_count}"
        
        # Cleanup running file
        rm "$RUNNING_DIR/$id.json"
    done
    
    if [ "$found_task" = false ]; then
        sleep 2
    fi
done
