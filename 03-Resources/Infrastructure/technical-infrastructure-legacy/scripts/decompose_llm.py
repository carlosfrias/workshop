#!/usr/bin/env python3
"""
decompose_llm.py — LLM-Driven Cloud Decomposer for TI-019
Tier 0: qwen3.5:397b-cloud (smart splitter)
Tier 1: kimi-k2.6-cloud (final decomposer)

Role: Decompose a complex prompt into weighted sub-tasks with
complexity assessment, token estimates, capability needs, and confidence.

Usage:
    python3 decompose_llm.py --prompt "Design a meta-orchestration framework..."
    python3 decompose_llm.py --prompt "..." --tier 0 --json
    python3 decompose_llm.py --prompt "..." --dry-run  # Show prompt, don't call API
    python3 decompose_llm.py --file prompt.txt --output decomposition.json

Environment:
    OLLAMA_API_KEY — read from ~/.ollama/ollama-api.key
    OLLAMA_CLOUD_URL — default https://api.ollama.cloud
"""
import json, sys, os, argparse, re, subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# ── CONFIGURATION ──────────────────────────────────────────────────

# Cloud model costs (USD per decomposition call ~2500 tokens)
TIER_COSTS = {
    0: 0.011,   # qwen3.5:397b-cloud — LOW (cheapest available)
    1: 0.017,   # gemma4:31b-cloud — MEDIUM (re-decomposition)
    2: 0.055,   # kimi-k2.6-cloud — HIGH (final escalation)
}

DEFAULT_CLOUD_URL = "https://api.ollama.cloud"
DEFAULT_TIER_0_MODEL = "qwen3.5:397b-cloud"   # LOW — cheapest, first attempt
DEFAULT_TIER_1_MODEL = "gemma4:31b-cloud"      # MEDIUM — re-decomposition
DEFAULT_TIER_2_MODEL = "kimi-k2.6-cloud"       # HIGH — final escalation only

# Read API key from file
API_KEY_PATH = Path.home() / ".ollama" / "ollama-api.key"

def get_api_key() -> Optional[str]:
    """Read API key from ~/.ollama/ollama-api.key, env var, or ~/.pi/agent/models.json."""
    # Priority 1: dedicated key file
    if API_KEY_PATH.exists():
        return API_KEY_PATH.read_text().strip()
    # Priority 2: environment variable
    env_key = os.environ.get("OLLAMA_API_KEY")
    if env_key:
        return env_key
    # Priority 3: models.json provider config (canonical source)
    try:
        models_path = Path.home() / ".pi" / "agent" / "models.json"
        if models_path.exists():
            models = json.loads(models_path.read_text())
            for prov in models.get("providers", {}).values():
                api_key = prov.get("apiKey")
                if api_key and api_key != "YOUR_API_KEY_HERE":
                    return api_key
    except Exception:
        pass
    return None

def get_cloud_url() -> str:
    return os.environ.get("OLLAMA_CLOUD_URL", DEFAULT_CLOUD_URL)

# ── DECOMPOSITION PROMPT ───────────────────────────────────────────

DECOMPOSITION_SYSTEM_PROMPT = """You are a task decomposition engine. Your job is to break complex tasks into smaller, independently executable sub-tasks.

RULES:
1. Each sub-task MUST be independently executable (can produce useful output without other sub-tasks)
2. Each sub-task MUST have a specific, actionable description
3. Complexity must be one of: trivial, simple, medium, hard
4. Token estimates should include both input (prompt) and output (response) tokens
5. Capabilities must be from: tools, reasoning, vision, coding, math, creative
6. Confidence must be 0.0-1.0 (your certainty that the decomposition is correct)
7. Weight must be 0.0-1.0 (relative importance to overall task, sum = 1.0)
8. Dependencies must reference other sub-task IDs (empty = no dependencies)

OUTPUT FORMAT: Return ONLY valid JSON matching this schema:
{
  "version": "1.0",
  "decomposer_model": "model-name",
  "sub_tasks": [
    {
      "id": "1",
      "description": "specific actionable sub-task description",
      "rationale": "why this sub-task is needed",
      "complexity": "medium",
      "estimated_tokens_in": 1200,
      "estimated_tokens_out": 800,
      "required_capabilities": ["tools", "reasoning"],
      "confidence": 0.92,
      "weight": 0.30,
      "dependencies": [],
      "can_parallelize": true
    }
  ],
  "global_constraints": {
    "max_total_tokens": 10000,
    "preferred_local": true,
    "max_cloud_escalation_depth": 2
  }
}

NO EXTRA TEXT. ONLY JSON."""

def build_decomposition_prompt(user_prompt: str, context: str = "") -> str:
    ctx = f"\nAdditional context: {context}" if context else ""
    return f"Decompose the following task into weighted sub-tasks.\n\nTASK: {user_prompt}{ctx}\n\nGenerate the JSON decomposition now."

# ── API CALL ───────────────────────────────────────────────────────

def call_cloud_model(prompt: str, model: str = DEFAULT_TIER_0_MODEL, timeout: int = 60) -> dict:
    """Call cloud model via Ollama API. Returns parsed response or error dict."""
    api_key = get_api_key()
    cloud_url = get_cloud_url()
    
    if not api_key:
        return {"error": "No API key found. Set OLLAMA_API_KEY or create ~/.ollama/ollama-api.key"}
    
    # Try Ollama HTTP API first
    import urllib.request
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DECOMPOSITION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2000},
    }
    
    req = urllib.request.Request(
        f"{cloud_url}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as e:
        return {"error": str(e), "fallback": True}


def call_local_fallback(prompt: str, model: str = "gemma4:e4b", timeout: int = 120) -> dict:
    """Fallback to local model via Ollama HTTP API."""
    full_prompt = f"{DECOMPOSITION_SYSTEM_PROMPT}\n\n{prompt}"
    
    import urllib.request
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2000},
    }
    
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


# ── JSON EXTRACTION ────────────────────────────────────────────────

def extract_json_from_response(response: dict) -> Optional[dict]:
    """Extract JSON from various response formats."""
    # Try OpenAI-style format
    if "choices" in response:
        content = response["choices"][0].get("message", {}).get("content", "")
    elif "message" in response:
        content = response["message"].get("content", "")
    elif "response" in response:
        content = response["response"]
    else:
        content = str(response)
    
    # Find JSON block
    # Try markdown code block first
    json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    
    # Try raw JSON object
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Try the whole content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    return None


def validate_decomposition(data: dict) -> tuple:
    """Validate decomposition JSON. Returns (is_valid, errors)."""
    errors = []
    
    if "sub_tasks" not in data or not isinstance(data["sub_tasks"], list):
        errors.append("Missing or invalid 'sub_tasks' array")
        return False, errors
    
    total_weight = 0.0
    for i, st in enumerate(data["sub_tasks"]):
        prefix = f"sub_task[{i}]"
        if "id" not in st:
            errors.append(f"{prefix}: missing 'id'")
        if "description" not in st:
            errors.append(f"{prefix}: missing 'description'")
        if "complexity" not in st or st["complexity"] not in ["trivial", "simple", "medium", "hard"]:
            errors.append(f"{prefix}: invalid 'complexity'")
        if "estimated_tokens_in" not in st or not isinstance(st["estimated_tokens_in"], int):
            errors.append(f"{prefix}: missing/invalid 'estimated_tokens_in'")
        if "estimated_tokens_out" not in st or not isinstance(st["estimated_tokens_out"], int):
            errors.append(f"{prefix}: missing/invalid 'estimated_tokens_out'")
        if "confidence" not in st or not (0.0 <= st["confidence"] <= 1.0):
            errors.append(f"{prefix}: invalid 'confidence' (must be 0.0-1.0)")
        if "weight" not in st or not (0.0 <= st["weight"] <= 1.0):
            errors.append(f"{prefix}: invalid 'weight' (must be 0.0-1.0)")
        total_weight += st.get("weight", 0)
    
    if not (0.99 <= total_weight <= 1.01):
        errors.append(f"Weights must sum to 1.0, got {total_weight:.2f}")
    
    return len(errors) == 0, errors


# ── MAIN ───────────────────────────────────────────────────────────

def decompose(prompt: str, tier: int = 0, context: str = "", dry_run: bool = False) -> dict:
    """Main decomposition entry point."""
    
    model_map = {
        0: DEFAULT_TIER_0_MODEL,   # LOW
        1: DEFAULT_TIER_1_MODEL,   # MEDIUM
        2: DEFAULT_TIER_2_MODEL,   # HIGH
    }
    model = model_map.get(tier, DEFAULT_TIER_0_MODEL)
    cost = TIER_COSTS.get(tier, 0.011)
    
    decomposition_prompt = build_decomposition_prompt(prompt, context)
    
    if dry_run:
        return {
            "status": "dry-run",
            "tier": tier,
            "model": model,
            "cost": cost,
            "prompt_preview": prompt[:80],
            "full_prompt": decomposition_prompt,
        }
    
    # Call cloud model
    response = call_cloud_model(decomposition_prompt, model)
    
    # Fallback to local if cloud fails
    if "error" in response:
        response = call_local_fallback(decomposition_prompt)
        cost = 0.0  # Local is free
    
    # Extract JSON
    data = extract_json_from_response(response)
    if data is None:
        return {
            "status": "error",
            "tier": tier,
            "model": model,
            "cost": cost,
            "error": "Could not extract valid JSON from model response",
            "raw_response": str(response)[:500],
        }
    
    # Validate
    is_valid, errors = validate_decomposition(data)
    
    # Enrich with metadata
    data["_meta"] = {
        "timestamp": datetime.now().isoformat(),
        "tier": tier,
        "model": model,
        "cost": cost,
        "status": "valid" if is_valid else "invalid",
        "validation_errors": errors,
        "prompt_preview": prompt[:100],
    }
    
    return data


def main():
    parser = argparse.ArgumentParser(description="LLM-driven task decomposition")
    parser.add_argument("--prompt", help="Task to decompose")
    parser.add_argument("--file", help="Read prompt from file")
    parser.add_argument("--context", default="", help="Additional context")
    parser.add_argument("--tier", type=int, default=0, choices=[0, 1, 2], help="Decomposer tier (0=LOW/qwen3.5, 1=MEDIUM/gemma4, 2=HIGH/kimi)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Show prompt without calling API")
    parser.add_argument("--output", help="Write result to file")
    parser.add_argument("--validate-only", help="Validate existing decomposition JSON file")
    args = parser.parse_args()
    
    if args.validate_only:
        with open(args.validate_only) as f:
            data = json.load(f)
        is_valid, errors = validate_decomposition(data)
        print(f"Valid: {is_valid}")
        if errors:
            for e in errors:
                print(f"  ❌ {e}")
        sys.exit(0 if is_valid else 1)
    
    prompt = ""
    if args.prompt:
        prompt = args.prompt
    elif args.file:
        with open(args.file) as f:
            prompt = f.read().strip()
    else:
        # Demo
        prompt = "Design a meta-orchestration framework with complexity classification and adaptive feedback for a 7-node lab"
    
    result = decompose(prompt, tier=args.tier, context=args.context, dry_run=args.dry_run)
    
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        lines = [f"Decomposition Result (Tier {result.get('_meta', {}).get('tier', '?')})"]
        meta = result.get("_meta", {})
        lines.append(f"Model: {meta.get('model', '?')} | Cost: ${meta.get('cost', 0):.3f}")
        lines.append(f"Status: {meta.get('status', '?')}")
        if meta.get("validation_errors"):
            lines.append("Validation Errors:")
            for e in meta["validation_errors"]:
                lines.append(f"  ❌ {e}")
        lines.append("")
        lines.append("Sub-tasks:")
        for st in result.get("sub_tasks", []):
            lines.append(f"  [{st.get('id', '?')}] {st.get('complexity', '?').upper()} (conf: {st.get('confidence', 0):.2f}, weight: {st.get('weight', 0):.2f})")
            lines.append(f"      {st.get('description', '?')[:60]}...")
            lines.append(f"      Tokens: {st.get('estimated_tokens_in', 0)} in / {st.get('estimated_tokens_out', 0)} out")
            lines.append(f"      Caps: {', '.join(st.get('required_capabilities', []))}")
            lines.append("")
        output = "\n".join(lines)
    
    print(output)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(json.dumps(result, indent=2))
        print(f"\nWrote to: {args.output}")


if __name__ == "__main__":
    main()
