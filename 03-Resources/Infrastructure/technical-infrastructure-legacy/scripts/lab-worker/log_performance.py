#!/usr/bin/env python3
"""Performance Logger
Logs task execution metrics: model, latency, tokens, cost, timestamps.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Log locally on the lab node or orchestrator
import os
if os.path.exists("/srv/lab-worker"):
    LOG_FILE = Path("/srv/lab-worker/performance-log.jsonl")
else:
    # Orchestrator fallback
    LOG_FILE = Path("/Users/friasc/Dropbox/ai-trading-workspace/technical-infrastructure/wiki/operational/sessions/model-performance-log.jsonl")

def log_entry(node, model, task_id, latency_s, prompt_tokens, response_tokens, success=True):
    """Append a performance log entry."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Cost model: local models ~$0 (electricity only), cloud models have actual cost
    is_cloud = ":cloud" in model or "cloud" in model
    cost_per_1k = 0.0 if not is_cloud else 0.015  # placeholder cloud rate
    
    total_tokens = (prompt_tokens or 0) + (response_tokens or 0)
    cost = (total_tokens / 1000) * cost_per_1k
    
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "node": node,
        "model": model,
        "task_id": task_id,
        "latency_sec": round(latency_s, 3),
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "total_tokens": total_tokens,
        "cost_usd": round(cost, 6),
        "cloud_escalated": is_cloud,
        "success": success,
        "provider": "ollama-cloud" if is_cloud else "ollama",
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry

def main():
    if len(sys.argv) < 7:
        print(f"Usage: {sys.argv[0]} <node> <model> <task_id> <latency_s> <prompt_tokens> <response_tokens> [success]")
        sys.exit(1)
    
    entry = log_entry(
        sys.argv[1], sys.argv[2], sys.argv[3],
        float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]),
        sys.argv[7].lower() == "true" if len(sys.argv) > 7 else True
    )
    print(json.dumps(entry, indent=2))

if __name__ == "__main__":
    main()
