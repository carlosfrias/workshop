#!/usr/bin/env python3
"""
handle_413.py — Autonomous 413 "Request Entity Too Large" recovery

Detects, diagnoses, and recovers from 413 errors at both routing time and
execution time. Strategies (in order):

  1. PREVENTION: Pre-flight token check before routing
  2. SAME-NODE ESCALATION: Try next-larger model on same node
  3. CROSS-NODE ESCALATION: Try node with more RAM for same model
  4. CLOUD ESCALATION: Route to cloud model with larger context
  5. CHUNKING: Split oversized task via LLM decomposition
  6. TRUNCATION: Hard truncate with warning (last resort)

Usage:
    # Pre-flight check (prevention)
    python3 handle_413.py --preflight --prompt "..." --model qwen3:8b

    # Recovery after 413 error
    python3 handle_413.py --recover --task /tmp/tasks/failed/xxx.json

    # Chunk a large prompt
    python3 handle_413.py --chunk --prompt "..." --max-chunk-tokens 8000

    # Test as library
    from handle_413 import recover_from_413, preflight_check
    result = recover_from_413(task_dict, error="413 from ollama on fnet3/qwen3:8b")
"""
import json, sys, os, subprocess, re
from pathlib import Path
from typing import Optional, List, Dict

# Add scripts dir to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from ti011_node_registry import NodeRegistry
except ImportError:
    NodeRegistry = None

# Known model context limits and sizes (fallback when registry unavailable)
MODEL_PROFILES = {
    "qwen3.5:4b": {"context": 131072, "size_gb": 5.7, "tier": "low", "has_tools": True, "has_vision": True},
    "qwen3:8b": {"context": 32768, "size_gb": 10.8, "tier": "medium", "has_tools": True, "has_vision": False},
    "gemma4:e4b": {"context": 131072, "size_gb": 18.9, "tier": "high", "has_tools": True, "has_vision": True},
    "qwen3.5:397b-cloud": {"context": 262144, "size_gb": 0, "tier": "cloud_low", "has_tools": True, "has_vision": True},
    "gemma4:31b-cloud": {"context": 256000, "size_gb": 0, "tier": "cloud_medium", "has_tools": True, "has_vision": True},
    "kimi-k2.6:cloud": {"context": 262144, "size_gb": 0, "tier": "cloud_high", "has_tools": True, "has_vision": True},
    "deepseek-v3.1:671b-cloud": {"context": 163840, "size_gb": 0, "tier": "cloud_high", "has_tools": True, "has_vision": False},
}

# Node RAM capacities (safe capacity after OS overhead)
NODE_CAPACITIES = {
    "fnet1": 12.5, "fnet2": 12.5, "fnet3": 27.0, "fnet4": 27.0,
    "fnet5": 27.0, "fnet6": 27.0, "fnet7": 12.5,
}

# Model upgrade chain per node (same-node escalation)
# Ordered from smallest to largest context
NODE_MODEL_CHAINS = {
    # 15GB nodes: qwen3.5:4b only (no upgrade path on-node)
    "fnet1": ["qwen3.5:4b"],
    "fnet2": ["qwen3.5:4b"],
    "fnet7": ["qwen3.5:4b"],
    # 31GB nodes: qwen3:8b -> gemma4:e4b
    "fnet3": ["qwen3.8b", "gemma4:e4b"],
    "fnet4": ["qwen3:8b", "gemma4:e4b"],
    "fnet5": ["qwen3:8b", "gemma4:e4b"],
    "fnet6": ["qwen3:8b", "gemma4:e4b"],
}

HARD_LIMIT_FRACTION = 0.85
SOFT_LIMIT_FRACTION = 0.60


def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars/token for English/ASCII)."""
    if not text:
        return 0
    return len(text) // 4


def parse_413_error(error_msg: str) -> Dict:
    """Parse a 413 error message to extract node, model, and token info."""
    result = {"node": None, "model": None, "tokens": None, "limit": None, "raw": error_msg}
    
    # Try to extract node/model from patterns like "fnet3/qwen3:8b" or "413 from ollama on fnet3"
    nm_match = re.search(r'(fnet\d+)/([\w\.:]+)', error_msg)
    if nm_match:
        result["node"] = nm_match.group(1)
        result["model"] = nm_match.group(2)
    
    # Try to extract token counts
    tok_match = re.search(r'(\d+)\s*tokens?\s*(?:needed|requested|input)', error_msg, re.I)
    if tok_match:
        result["tokens"] = int(tok_match.group(1))
    
    lim_match = re.search(r'limit\s*(?:of|is)?\s*(\d+)', error_msg, re.I)
    if lim_match:
        result["limit"] = int(lim_match.group(1))
    
    return result


def get_model_context(model: str) -> int:
    """Get context window for a model."""
    if model in MODEL_PROFILES:
        return MODEL_PROFILES[model]["context"]
    # Fallback: try registry
    if NodeRegistry:
        reg = NodeRegistry()
        for node_name, data in reg.nodes.items():
            for m in data.get("models", []):
                if m["id"] == model:
                    return m.get("capabilities", {}).get("contextSize", 32768)
    return 32768  # safe default


def get_model_size_gb(model: str) -> float:
    """Get model size in GB."""
    if model in MODEL_PROFILES:
        return MODEL_PROFILES[model]["size_gb"]
    return 15.0  # conservative default


def get_node_capacity(node: str) -> float:
    """Get safe capacity for a node."""
    if node in NODE_CAPACITIES:
        return NODE_CAPACITIES[node]
    if NodeRegistry:
        reg = NodeRegistry()
        data = reg.nodes.get(node, {})
        return reg._parse_capacity_gb(data) if hasattr(reg, '_parse_capacity_gb') else 12.5
    return 12.5


def can_fit_on_node(model: str, node: str) -> bool:
    """Check if model can fit on node's available RAM."""
    size = get_model_size_gb(model)
    cap = get_node_capacity(node)
    return size < cap


def find_larger_model(current_model: str, required_vision: bool = False, required_tools: bool = True) -> Optional[str]:
    """Find the next-larger model in the hierarchy."""
    profiles = MODEL_PROFILES
    if current_model not in profiles:
        return None
    
    current_tier = profiles[current_model]["tier"]
    current_context = profiles[current_model]["context"]
    
    # Tier ordering
    tier_order = ["low", "medium", "high", "cloud_low", "cloud_medium", "cloud_high"]
    current_idx = tier_order.index(current_tier) if current_tier in tier_order else -1
    
    candidates = []
    for model_id, prof in profiles.items():
        if model_id == current_model:
            continue
        # Must be larger context
        if prof["context"] <= current_context:
            continue
        # Must meet capability requirements
        if required_vision and not prof.get("has_vision", False):
            continue
        if required_tools and not prof.get("has_tools", False):
            continue
        # Prefer closer tiers
        tier_idx = tier_order.index(prof["tier"]) if prof["tier"] in tier_order else 99
        tier_distance = abs(tier_idx - current_idx)
        candidates.append((model_id, prof["context"], tier_distance))
    
    if not candidates:
        return None
    
    # Sort by: smallest tier distance, then largest context
    candidates.sort(key=lambda x: (x[2], -x[1]))
    return candidates[0][0]


def find_node_for_model(model: str, exclude: Optional[List[str]] = None) -> Optional[str]:
    """Find a node that can run the given model."""
    exclude = exclude or []
    size = get_model_size_gb(model)
    
    # Try nodes with most capacity first
    node_caps = [(n, NODE_CAPACITIES.get(n, 0)) for n in NODE_CAPACITIES if n not in exclude]
    node_caps.sort(key=lambda x: -x[1])
    
    for node, cap in node_caps:
        if size < cap:
            return node
    return None


def preflight_check(prompt: str, model: str, node: Optional[str] = None) -> Dict:
    """Pre-flight check to prevent 413 before routing.
    
    Returns dict with status and recommended action.
    """
    tokens = estimate_tokens(prompt)
    context = get_model_context(model)
    hard_limit = int(context * HARD_LIMIT_FRACTION)
    soft_limit = int(context * SOFT_LIMIT_FRACTION)
    
    result = {
        "status": "ok",
        "tokens": tokens,
        "context": context,
        "hard_limit": hard_limit,
        "soft_limit": soft_limit,
        "model": model,
        "node": node,
        "utilization_percent": round(100 * tokens / context, 1) if context > 0 else 0,
        "action": None,
        "action_details": {},
    }
    
    if tokens > hard_limit:
        result["status"] = "oversized"
        result["reason"] = f"{tokens} tokens > hard limit {hard_limit} ({HARD_LIMIT_FRACTION*100:.0f}% of {context})"
        
        # Determine best recovery strategy
        recovery = determine_recovery(model, tokens, required_vision=False, required_tools=True)
        result["action"] = recovery["strategy"]
        result["action_details"] = recovery
        
    elif tokens > soft_limit:
        result["status"] = "warning"
        result["reason"] = f"{tokens} tokens > soft limit {soft_limit} — consider splitting"
        
    else:
        result["reason"] = f"Within safe range ({tokens}/{hard_limit})"
    
    return result


def determine_recovery(current_model: str, tokens_needed: int, 
                        required_vision: bool = False, required_tools: bool = True,
                        failed_node: Optional[str] = None) -> Dict:
    """Determine the best recovery strategy for an oversized payload.
    
    Strategies (in preference order):
    1. SAME_NODE_UPGRADE: Larger model on same node
    2. CROSS_NODE_SAME: Same model on larger node
    3. CROSS_NODE_UPGRADE: Larger model on larger node
    4. CLOUD: Cloud model with huge context
    5. CHUNK: Split into smaller tasks
    6. TRUNCATE: Hard truncate (last resort)
    """
    
    # Strategy 1: Same-node upgrade
    if failed_node:
        chain = NODE_MODEL_CHAINS.get(failed_node, [])
        try:
            idx = chain.index(current_model)
            if idx + 1 < len(chain):
                larger = chain[idx + 1]
                prof = MODEL_PROFILES.get(larger, {})
                if required_vision and not prof.get("has_vision", False):
                    pass  # Skip, try next strategy
                elif required_tools and not prof.get("has_tools", False):
                    pass
                else:
                    larger_context = get_model_context(larger)
                    if tokens_needed < int(larger_context * HARD_LIMIT_FRACTION):
                        return {
                            "strategy": "SAME_NODE_UPGRADE",
                            "model": larger,
                            "node": failed_node,
                            "reason": f"Upgrade {current_model} -> {larger} on {failed_node} (context: {larger_context})",
                            "cost_delta": "local only",
                        }
        except ValueError:
            pass
    
    # Strategy 2: Cross-node, same model
    if failed_node:
        for node in NODE_CAPACITIES:
            if node == failed_node:
                continue
            if can_fit_on_node(current_model, node):
                # Verify capabilities on this model
                prof = MODEL_PROFILES.get(current_model, {})
                if required_vision and not prof.get("has_vision", False):
                    continue
                if required_tools and not prof.get("has_tools", False):
                    continue
                ctx = get_model_context(current_model)
                if tokens_needed < int(ctx * HARD_LIMIT_FRACTION):
                    return {
                        "strategy": "CROSS_NODE_SAME",
                        "model": current_model,
                        "node": node,
                        "reason": f"Same model {current_model} on {node} (capacity: {NODE_CAPACITIES[node]}GB)",
                        "cost_delta": "local only",
                    }
    
    # Strategy 3: Cross-node upgrade
    larger_model = find_larger_model(current_model, required_vision, required_tools)
    if larger_model:
        larger_size = get_model_size_gb(larger_model)
        for node in sorted(NODE_CAPACITIES, key=lambda n: -NODE_CAPACITIES[n]):
            if node == failed_node:
                continue
            if NODE_CAPACITIES[node] > larger_size:
                ctx = get_model_context(larger_model)
                if tokens_needed < int(ctx * HARD_LIMIT_FRACTION):
                    return {
                        "strategy": "CROSS_NODE_UPGRADE",
                        "model": larger_model,
                        "node": node,
                        "reason": f"Upgrade to {larger_model} on {node} (context: {ctx})",
                        "cost_delta": "local only" if not larger_model.endswith("-cloud") else "cloud",
                    }
    
    # Strategy 4: Cloud escalation
    cloud_models = ["qwen3.5:397b-cloud", "gemma4:31b-cloud", "kimi-k2.6:cloud"]
    for cm in cloud_models:
        prof = MODEL_PROFILES.get(cm, {})
        if required_vision and not prof.get("has_vision", False):
            continue
        if required_tools and not prof.get("has_tools", False):
            continue
        ctx = prof.get("context", 0)
        if tokens_needed < int(ctx * HARD_LIMIT_FRACTION):
            return {
                "strategy": "CLOUD",
                "model": cm,
                "node": "cloud",
                "reason": f"Cloud model {cm} with {ctx} context",
                "cost_delta": "cloud",
                "estimated_cost": round(0.011 if "qwen3.5" in cm else 0.017 if "gemma4" in cm else 0.055, 3),
            }
    
    # Strategy 5: Chunking
    # Find the best available context window
    best_local_ctx = 0
    for node in NODE_CAPACITIES:
        for model in NODE_MODEL_CHAINS.get(node, []):
            ctx = get_model_context(model)
            if ctx > best_local_ctx:
                best_local_ctx = ctx
    
    # Also consider cloud
    for cm in cloud_models:
        ctx = MODEL_PROFILES.get(cm, {}).get("context", 0)
        if ctx > best_local_ctx:
            best_local_ctx = ctx
    
    chunk_size = int(best_local_ctx * SOFT_LIMIT_FRACTION)
    num_chunks = (tokens_needed // chunk_size) + 1
    
    return {
        "strategy": "CHUNK",
        "reason": f"Payload too large for any single model. Split into {num_chunks} chunks of ~{chunk_size} tokens",
        "chunk_size": chunk_size,
        "num_chunks": num_chunks,
        "cost_delta": "local" if best_local_ctx <= 32768 else "mixed",
    }


def chunk_prompt(prompt: str, max_chunk_tokens: int = 8000, overlap_tokens: int = 500) -> List[Dict]:
    """Split a large prompt into chunks with overlap for context preservation.
    
    Uses paragraph-based splitting first, then falls back to sentence/word
    boundaries if paragraphs are too large.
    """
    total_tokens = estimate_tokens(prompt)
    
    if total_tokens <= max_chunk_tokens:
        return [{"chunk_id": 0, "tokens": total_tokens, "text": prompt, "type": "full"}]
    
    max_chars = max_chunk_tokens * 4  # ~4 chars/token
    overlap_chars = overlap_tokens * 4
    
    chunks = []
    chunk_id = 0
    start = 0
    
    while start < len(prompt):
        # Find a good break point
        end = start + max_chars
        if end >= len(prompt):
            end = len(prompt)
        else:
            # Try to break at paragraph
            para_break = prompt.rfind("\n\n", start, end)
            if para_break > start + max_chars // 2:
                end = para_break
            else:
                # Try sentence boundary
                sent_break = max(
                    prompt.rfind(". ", start, end),
                    prompt.rfind("! ", start, end),
                    prompt.rfind("? ", start, end),
                )
                if sent_break > start + max_chars // 2:
                    end = sent_break + 1
                else:
                    # Try word boundary
                    word_break = prompt.rfind(" ", start, end)
                    if word_break > start + max_chars // 2:
                        end = word_break
        
        chunk_text = prompt[start:end]
        # Add overlap context from previous chunk for continuity
        if start > 0 and overlap_chars > 0:
            overlap_start = max(0, start - overlap_chars)
            overlap_text = prompt[overlap_start:start]
            chunk_text = overlap_text + "\n\n[...continuing...]\n\n" + chunk_text
        
        chunks.append({
            "chunk_id": chunk_id,
            "tokens": estimate_tokens(chunk_text),
            "text": chunk_text,
            "type": "partial",
        })
        
        chunk_id += 1
        start = end
    
    return chunks


def recover_from_413(task: Dict, error_msg: str, attempt: int = 1) -> Dict:
    """Autonomous recovery from a 413 error.
    
    Args:
        task: The task dict that failed
        error_msg: The error message (may contain node/model info)
        attempt: Recovery attempt number (1-based)
    
    Returns:
        Dict with recovery action and new task(s) to submit.
        If recovery impossible, returns {"strategy": "FAILED", ...}
    """
    parsed = parse_413_error(error_msg)
    node = parsed.get("node") or task.get("node")
    model = parsed.get("model") or task.get("model")
    
    # Estimate tokens from task
    prompt = task.get("command", "") + "\n" + task.get("prompt", "")
    tokens = parsed.get("tokens") or estimate_tokens(prompt)
    
    # Check if this is a real 413 or something else
    if not node and not model:
        return {
            "strategy": "FAILED",
            "reason": "Cannot parse node/model from error. Manual intervention needed.",
            "error": error_msg,
            "suggested_action": "Check node logs and retry with explicit routing",
        }
    
    # Get required capabilities from task
    required_vision = task.get("requires_vision", False)
    required_tools = task.get("requires_tools", True)
    
    # Determine recovery strategy
    recovery = determine_recovery(
        model, tokens, 
        required_vision=required_vision, 
        required_tools=required_tools,
        failed_node=node,
    )
    
    result = {
        "original_task_id": task.get("id"),
        "original_node": node,
        "original_model": model,
        "tokens": tokens,
        "attempt": attempt,
        **recovery,
    }
    
    # Generate replacement task(s)
    if recovery["strategy"] in ["SAME_NODE_UPGRADE", "CROSS_NODE_SAME", "CROSS_NODE_UPGRADE"]:
        new_task = dict(task)
        new_task["id"] = f"{task['id']}-r{attempt}"
        new_task["node"] = recovery["node"]
        new_task["model"] = recovery["model"]
        new_task["_recovery_from"] = task["id"]
        new_task["_recovery_reason"] = recovery["reason"]
        result["tasks"] = [new_task]
        
    elif recovery["strategy"] == "CLOUD":
        new_task = dict(task)
        new_task["id"] = f"{task['id']}-c{attempt}"
        new_task["node"] = "cloud"
        new_task["model"] = recovery["model"]
        new_task["_recovery_from"] = task["id"]
        new_task["_recovery_reason"] = recovery["reason"]
        new_task["_estimated_cloud_cost"] = recovery.get("estimated_cost", 0)
        result["tasks"] = [new_task]
        
    elif recovery["strategy"] == "CHUNK":
        chunks = chunk_prompt(prompt, max_chunk_tokens=recovery["chunk_size"])
        chunk_tasks = []
        for chunk in chunks:
            ct = dict(task)
            ct["id"] = f"{task['id']}-c{chunk['chunk_id']}"
            ct["command"] = chunk["text"]
            ct["_chunk_id"] = chunk["chunk_id"]
            ct["_total_chunks"] = len(chunks)
            ct["_recovery_from"] = task["id"]
            ct["_recovery_reason"] = f"Chunk {chunk['chunk_id']+1}/{len(chunks)}: {chunk['tokens']} tokens"
            ct["_chunking_strategy"] = "paragraph_split"
            chunk_tasks.append(ct)
        result["tasks"] = chunk_tasks
        result["num_chunks"] = len(chunk_tasks)
        
    elif recovery["strategy"] == "TRUNCATE":
        # Hard truncate — last resort
        max_chars = int(get_model_context(model) * HARD_LIMIT_FRACTION * 4)
        truncated = prompt[:max_chars]
        new_task = dict(task)
        new_task["id"] = f"{task['id']}-t{attempt}"
        new_task["command"] = truncated
        new_task["_truncated"] = True
        new_task["_original_length"] = len(prompt)
        new_task["_recovery_reason"] = "Hard truncated to fit context window"
        result["tasks"] = [new_task]
        result["warning"] = "Task was truncated. Results may be incomplete."
    
    else:
        result["strategy"] = "FAILED"
        result["reason"] = f"Unknown recovery strategy: {recovery.get('strategy')}"
        result["tasks"] = []
    
    return result


def log_413_incident(result: Dict, log_dir: str = "/tmp/tasks/413-log"):
    """Log a 413 incident for feedback loop analysis."""
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d-%H%M%S")
    task_id = result.get("original_task_id", "unknown")
    log_file = Path(log_dir) / f"{task_id}-{timestamp}.json"
    with open(log_file, "w") as f:
        json.dump(result, f, indent=2)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous 413 recovery")
    parser.add_argument("--preflight", action="store_true", help="Pre-flight check")
    parser.add_argument("--prompt", help="Prompt text to check")
    parser.add_argument("--model", default="qwen3:8b", help="Target model")
    parser.add_argument("--node", help="Target node")
    parser.add_argument("--recover", action="store_true", help="Recover from failed task")
    parser.add_argument("--task", help="Path to failed task JSON")
    parser.add_argument("--error", help="Error message from failed execution")
    parser.add_argument("--chunk", action="store_true", help="Chunk a large prompt")
    parser.add_argument("--max-chunk-tokens", type=int, default=8000, help="Max tokens per chunk")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    if args.preflight:
        if not args.prompt:
            print("Error: --preflight requires --prompt", file=sys.stderr)
            sys.exit(1)
        result = preflight_check(args.prompt, args.model, args.node)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Status: {result['status']}")
            print(f"Tokens: {result['tokens']} / {result['context']} ({result['utilization_percent']}%)")
            if result['action']:
                print(f"Action: {result['action']}")
                print(f"Details: {result['action_details'].get('reason', '')}")
        sys.exit(0 if result['status'] == 'ok' else 1)
    
    elif args.recover:
        if not args.task:
            print("Error: --recover requires --task", file=sys.stderr)
            sys.exit(1)
        with open(args.task) as f:
            task = json.load(f)
        error = args.error or "413 Request Entity Too Large"
        result = recover_from_413(task, error)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Recovery: {result['strategy']}")
            print(f"Reason: {result.get('reason', '')}")
            if result.get('tasks'):
                print(f"Generated {len(result['tasks'])} replacement task(s)")
                for t in result['tasks']:
                    print(f"  -> {t['id']} on {t.get('node', '?')}/{t.get('model', '?')}")
        log_413_incident(result)
        sys.exit(0)
    
    elif args.chunk:
        if not args.prompt:
            print("Error: --chunk requires --prompt", file=sys.stderr)
            sys.exit(1)
        chunks = chunk_prompt(args.prompt, args.max_chunk_tokens)
        if args.json:
            print(json.dumps({"chunks": chunks}, indent=2))
        else:
            print(f"Split into {len(chunks)} chunk(s):")
            for c in chunks:
                print(f"  Chunk {c['chunk_id']}: {c['tokens']} tokens ({c['type']})")
        sys.exit(0)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
