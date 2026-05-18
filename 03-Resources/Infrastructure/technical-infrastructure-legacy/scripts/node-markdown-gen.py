#!/usr/bin/env python3
"""
node-markdown-gen.py — Generate markdown content via local ollama on lab nodes

Deployed to all lab nodes (fnet1-fnet7) at /usr/local/bin/node-markdown-gen.py.
Used by auto-distribution pipeline to generate wiki pages, documentation,
and other text content in parallel across the lab.

Usage (on any node with ollama running):
    python3 node-markdown-gen.py --prompt "Write a guide on..." --model qwen3:8b --output /tmp/guide.md
    python3 node-markdown-gen.py --prompt-file prompt.txt --model gemma4:e4b --output result.md

Usage (from orchestrator, via submit_task.py):
    {"type": "shell", "command": "python3 /usr/local/bin/node-markdown-gen.py --prompt ..."}

Design:
- No timeout (ollama timeout handled at orchestrator level)
- num_predict=1000 keeps generation fast (<60s on qwen3:8b)
- keep_alive=10m prevents model unload between tasks
- Temperature 0.3 for consistent, factual output
"""
import requests, sys, argparse

def generate(prompt: str, model: str = "qwen3:8b") -> str:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.3, "num_predict": 1000}
    }
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        return f"ERROR: {e}"

def main():
    p = argparse.ArgumentParser(description="Generate markdown via local ollama")
    p.add_argument("--prompt", help="Prompt text")
    p.add_argument("--prompt-file", help="Read prompt from file")
    p.add_argument("--model", default="qwen3:8b", help="Ollama model (default: qwen3:8b)")
    p.add_argument("--output", required=True, help="Output markdown file")
    p.add_argument("--json", action="store_true", help="Wrap output in JSON with metadata")
    args = p.parse_args()

    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read()
    if not prompt:
        print("Error: --prompt or --prompt-file required", file=sys.stderr)
        sys.exit(1)

    result = generate(prompt, args.model)

    if args.json:
        import json
        out = {
            "model": args.model,
            "input_chars": len(prompt),
            "output_chars": len(result),
            "text": result,
        }
        with open(args.output, "w") as f:
            json.dump(out, f, indent=2)
    else:
        with open(args.output, "w") as f:
            f.write(result)

    print(f"Generated {len(result)} chars to {args.output}")

if __name__ == "__main__":
    main()
