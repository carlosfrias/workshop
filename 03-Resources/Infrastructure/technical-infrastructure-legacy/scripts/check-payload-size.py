#!/usr/bin/env python3
"""
check-payload-size.py — Pre-flight payload guard for TI-011 orchestration
Prevents 413 Payload Too Large errors by estimating tokens and enforcing model caps.

Usage:
    python3 scripts/check-payload-size.py --prompt "Very long prompt..." --model qwen3:8b
    python3 scripts/check-payload-size.py --file large-prompt.txt --model gemma4:e4b
    python3 scripts/check-payload-size.py --task /path/to/task.json

Returns exit code 0 if OK, 1 if would exceed threshold, 2 if way over limit.
"""
import json, sys, argparse, os

# Known model context limits (defaults when not in node configs)
MODEL_CONTEXT_LIMITS = {
    "qwen3.5:4b": 131072,
    "qwen3:8b": 32768,
    "gemma4:e4b": 131072,
    "qwen3.5:397b-cloud": 32768,
    "kimi-k2.6": 131072,
}

# Safety thresholds: refuse if input exceeds this fraction of context
HARD_LIMIT_FRACTION = 0.85   # 85% of context window = hard rejection
SOFT_LIMIT_FRACTION = 0.60   # 60% of context window = warning, suggest truncation


def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars/token for English/ASCII)."""
    return len(text) // 4


def check_payload(text: str, model: str = "qwen3:8b") -> dict:
    """Check if payload size is within safe limits for model."""
    tokens = estimate_tokens(text)
    limit = MODEL_CONTEXT_LIMITS.get(model, 32768)
    hard_limit = int(limit * HARD_LIMIT_FRACTION)
    soft_limit = int(limit * SOFT_LIMIT_FRACTION)

    status = "ok"
    reason = f"Estimated {tokens} tokens vs {limit} limit ({100*tokens/limit:.0f}%)"
    exit_code = 0

    if tokens > hard_limit:
        status = "rejected"
        reason += f" — exceeds hard limit of {hard_limit} tokens"
        exit_code = 2
    elif tokens > soft_limit:
        status = "warning"
        reason += f" — exceeds soft limit of {soft_limit} tokens, consider truncation or splitting"
        exit_code = 1
    else:
        reason += " — within safe range"

    return {
        "status": status,
        "tokens": tokens,
        "limit": limit,
        "hard_limit": hard_limit,
        "soft_limit": soft_limit,
        "utilization_percent": round(100 * tokens / limit, 1),
        "reason": reason,
        "exit_code": exit_code,
    }


def main():
    parser = argparse.ArgumentParser(description="Payload size guard")
    parser.add_argument("--prompt", help="Prompt text to check")
    parser.add_argument("--file", help="File containing prompt/task")
    parser.add_argument("--task", help="Task JSON file to check (uses task.command)")
    parser.add_argument("--model", default="qwen3:8b", help="Target model (default: qwen3:8b)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    text = ""
    if args.prompt:
        text = args.prompt
    elif args.file:
        with open(args.file) as f:
            text = f.read()
    elif args.task:
        with open(args.task) as f:
            task = json.load(f)
        text = task.get("command", "") + "\n" + json.dumps(task)
    else:
        parser.print_help()
        sys.exit(2)

    result = check_payload(text, args.model)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Status: {result['status']}")
        print(f"Tokens: {result['tokens']} / {result['limit']} ({result['utilization_percent']}%)")
        print(f"Reason: {result['reason']}")

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
