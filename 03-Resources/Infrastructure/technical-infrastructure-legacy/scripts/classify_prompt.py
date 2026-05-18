#!/usr/bin/env python3
"""
classify_prompt.py — Hybrid Heuristic Prompt Complexity Classifier
Phase 1: Meta-Orchestration Framework

Design: Fast heuristic classification (<50ms) with LLM fallback for uncertain cases.
Heuristic rules are updated weekly by offline LLM analysis of logged prompts.

Usage:
    python3 classify_prompt.py "Check if fnet2 is online"
    python3 classify_prompt.py --json "Design a framework..."
    python3 classify_prompt.py --file prompts.txt --profile
    python3 classify_prompt.py --llm "Uncertain prompt..."  # Force LLM fallback
"""
import json, sys, re, time, os, argparse
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path

# Add TI-011 node registry import path
TI011_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if TI011_SCRIPT_DIR not in sys.path:
    sys.path.insert(0, TI011_SCRIPT_DIR)
try:
    from ti011_node_registry import NodeRegistry
except ImportError:
    NodeRegistry = None

try:
    from performance_logger import log_routing_decision
except ImportError:
    log_routing_decision = None

# ── CONFIGURATION ──────────────────────────────────────────────────
TRIVIAL_KEYWORDS = [
    r"\b(check|ping|test|verify|is|are|list|show|display|echo|print|get|find)\b.*\b(online|up|down|status|version|size|count|files?|dir)\b",
    r"\b(format|indent|prettify|sort|clean|convert)\b.*\b(json|yaml|csv|text|markdown)\b",
    r"\b(copy|scp|rsync|move|delete|remove|chmod|chown)\b.*\b(file|dir|path)\b",
    r"\b(rm|cp|mv|ls|cat|grep|head|tail|wc)\b\s+\S+",
    r"^\s*(what|when|where|who|how many)\s+(is|are|was|were|does|did)\b",
]

SIMPLE_KEYWORDS = [
    r"\b(write|create|generate|build)\b.*\b(script|function|class|module|file)\b",
    r"\b(validate|lint|check)\b.*\b(syntax|schema|types|config)\b",
    r"\b(summarize|extract|parse)\b.*\b(from|out of|data|text|document)\b",
    r"\b(install|setup|configure)\b.*\b(one|single|a|basic|simple)\b",
    r"\b(create|add|set up)\b.*\b(cron job|service|timer|user|group)\b",
    r"\b(update|modify|change|edit)\b.*\b(config|setting|variable|parameter)\b",
]

MEDIUM_KEYWORDS = [
    r"\b(create|write|build|design)\b.*\b(playbook|role|collection|workflow|pipeline)\b",
    r"\b(build|develop|implement)\b.*\b(system|service|component|module|queue|worker|orchestrat)\b",
    r"\b(analyze|compare|evaluate|assess)\b.*\b(across|between|among|multiple|several)\b",
    r"\b(troubleshoot|debug|fix|resolve|diagnose)\b.*\b(issue|problem|error|failure|bug)\b",
    r"\b(sync|replicate|mirror|distribute|deploy)\b.*\b(across|to all|multiple|nodes?|servers?)\b",
    r"\b(migrate|upgrade|refactor|restructure)\b.*\b(from|to|into)\b",
    r"\b(automate|orchestrate|schedule|manage)\b.*\b(process|task|job|workflow)\b",
    r"\b(integrate|connect|link|bridge)\b.*\b(with|to|and)\b.*\b(system|service|api|tool)\b",
]

HARD_KEYWORDS = [
    r"\b(design|architect|engineer|invent|create)\b.*\b(framework|system|architecture|platform|infrastructure)\b",
    r"\b(propose|justify|develop)\b.*\b(model|strategy|approach|methodology|framework|tiered|cost|pricing)\b",
    r"\b(novel|new|innovative|creative|unique|unprecedented)\b.*\b(approach|solution|method|pattern|strategy)\b",
    r"\b(meta-|self-|auto-|adaptive|dynamic|intelligent)\b.*\b(orchestrat|organiz|rout|manag|optimiz)\b",
    r"\b(cross-domain|multi-domain|interdisciplinary|holistic|systemic)\b",
    r"\b(why does|explain why|fundamental|deep|root cause)\b.*\b(happen|occur|work|behave|interact)\b",
    r"\b(strategic|long-term|vision|roadmap|future|evolution)\b",
]

# Domain multipliers — certain domains increase complexity
domain_complexity = {
    "trading": 0.5,      # Trading analysis tends to be medium/hard
    "finance": 0.5,
    "market": 0.5,
    "architecture": 1.0, # Architecture design is hard
    "framework": 1.0,
    "meta": 1.0,
    "systemd": 0.3,      # Systemd tasks are medium
    "lvm": 0.3,
    "ansible": 0.2,      # Ansible is usually medium
    "ollama": 0.1,
    "script": -0.5,      # Scripts are usually simple
    "format": -1.0,
    "syntax": -0.5,
}

# ── CORE FUNCTIONS ─────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars/token)."""
    return len(text) // 4

def heuristic_classify(prompt: str) -> Dict:
    """Fast heuristic classification. Returns dict with complexity, confidence, reasoning."""
    start = time.time()
    prompt_lower = prompt.lower()
    tokens = estimate_tokens(prompt)
    
    # Base scores
    scores = {"TRIVIAL": 0.0, "SIMPLE": 0.0, "MEDIUM": 0.0, "HARD": 0.0}
    
    # Keyword matching
    for pattern in TRIVIAL_KEYWORDS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            scores["TRIVIAL"] += 1.0
    for pattern in SIMPLE_KEYWORDS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            scores["SIMPLE"] += 1.0
    for pattern in MEDIUM_KEYWORDS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            scores["MEDIUM"] += 1.0
    for pattern in HARD_KEYWORDS:
        if re.search(pattern, prompt_lower, re.IGNORECASE):
            scores["HARD"] += 1.0
    
    # Length factor
    if tokens < 50:
        scores["TRIVIAL"] += 0.3
    elif tokens < 200:
        scores["SIMPLE"] += 0.2
    elif tokens < 500:
        scores["MEDIUM"] += 0.2
    else:
        scores["HARD"] += 0.3
    
    # Domain adjustments
    for domain, adjustment in domain_complexity.items():
        if domain in prompt_lower:
            if adjustment > 0:
                scores["HARD"] += adjustment
                scores["MEDIUM"] += adjustment * 0.5
            else:
                scores["TRIVIAL"] += abs(adjustment) * 0.3
                scores["SIMPLE"] += abs(adjustment) * 0.2
    
    # Question type
    if re.search(r"^(what|when|where|who|how many|is|are|does|did)\s", prompt_lower):
        scores["TRIVIAL"] += 0.2
    if re.search(r"\b(why|explain|describe|elaborate)\b", prompt_lower):
        scores["MEDIUM"] += 0.2
    
    # Multi-step indicators
    step_words = len(re.findall(r"\b(then|next|after|finally|step|stage|phase)\b", prompt_lower))
    scores["MEDIUM"] += step_words * 0.15
    scores["HARD"] += step_words * 0.1
    
    # Determine winner
    complexity = max(scores, key=scores.get)
    max_score = scores[complexity]
    total_score = sum(scores.values())
    
    # Confidence: how dominant is the winner?
    if total_score == 0:
        confidence = 0.0
        complexity = "MEDIUM"  # Safe default
    else:
        confidence = max_score / total_score
    
    # Build reasoning
    reasons = []
    if tokens < 50:
        reasons.append("very short prompt")
    elif tokens > 1000:
        reasons.append("very long prompt")
    
    matched_keywords = [k for k, v in scores.items() if v > 0 and k == complexity]
    if matched_keywords:
        reasons.append(f"keyword patterns matched")
    
    latency_ms = int((time.time() - start) * 1000)
    
    tier_map = {"TRIVIAL": "low", "SIMPLE": "low", "MEDIUM": "medium", "HARD": "high"}
    
    return {
        "complexity": complexity,
        "confidence": round(confidence, 2),
        "suggested_tier": tier_map[complexity],
        "reasoning": f"Heuristic: {complexity}. {'; '.join(reasons)}." if reasons else f"Heuristic: {complexity}",
        "latency_ms": latency_ms,
        "estimated_tokens_in": tokens,
        "estimated_tokens_out": 0,
        "fallback": False,
        "heuristic": True,
        "scores": scores,
    }

def llm_classify(prompt: str, model: str = "qwen3.5:4b") -> Dict:
    """LLM-based classification (slow, accurate). Used for fallback or offline analysis."""
    import subprocess
    
    start = time.time()
    
    # Minimal prompt for speed
    classify_prompt = f"""Classify: TRIVIAL, SIMPLE, MEDIUM, or HARD.
Task: {prompt[:500]}
Answer with ONLY the word:"""
    
    proc = subprocess.run(
        ["ollama", "run", model, classify_prompt],
        capture_output=True, text=True, timeout=30
    )
    latency_ms = int((time.time() - start) * 1000)
    
    if proc.returncode != 0:
        return {
            "complexity": "MEDIUM",
            "confidence": 0.0,
            "suggested_tier": "medium",
            "reasoning": f"LLM classifier failed: {proc.stderr[:100]}",
            "latency_ms": latency_ms,
            "fallback": True,
        }
    
    raw = proc.stdout.strip().upper()
    # Extract complexity from raw output
    for level in ["TRIVIAL", "SIMPLE", "MEDIUM", "HARD"]:
        if level in raw:
            complexity = level
            break
    else:
        complexity = "MEDIUM"
    
    tier_map = {"TRIVIAL": "low", "SIMPLE": "low", "MEDIUM": "medium", "HARD": "high"}
    
    return {
        "complexity": complexity,
        "confidence": 0.85,  # LLM is generally confident
        "suggested_tier": tier_map[complexity],
        "reasoning": f"LLM classification: {complexity}",
        "latency_ms": latency_ms,
        "estimated_tokens_in": estimate_tokens(prompt),
        "fallback": False,
        "heuristic": False,
    }

try:
    from orchestrator_health import check_health
except ImportError:
    check_health = None

def classify(prompt: str, llm_fallback_threshold: float = 0.60, force_llm: bool = False, with_routing: bool = True, skip_health_check: bool = False) -> Dict:
    """Main entry point: hybrid classification with optional node-model routing."""
    
    # Check orchestrator health before routing
    health_status = "unknown"
    if not skip_health_check and check_health:
        try:
            health = check_health()
            health_status = health.get("status", "unknown")
        except Exception:
            health_status = "unknown"
    
    if force_llm:
        try:
            result = llm_classify(prompt)
        except Exception as e:
            result = {
                "complexity": "MEDIUM",
                "confidence": 0.0,
                "suggested_tier": "medium",
                "reasoning": f"LLM fallback failed: {str(e)[:80]}",
                "latency_ms": 0,
                "fallback": True,
            }
        if with_routing and NodeRegistry:
            _attach_routing(result, prompt, health_status)
        return result
    
    # Try heuristic first
    result = heuristic_classify(prompt)
    
    # Payload guard: skip LLM fallback for oversized prompts to avoid 413 errors
    prompt_tokens = estimate_tokens(prompt)
    LLM_FALLBACK_TOKEN_CAP = 10000  # Never send >10K tokens to LLM classifier
    
    if result["confidence"] < llm_fallback_threshold:
        if prompt_tokens > LLM_FALLBACK_TOKEN_CAP:
            result["fallback_reason"] = (
                f"Heuristic confidence {result['confidence']} < {llm_fallback_threshold}, "
                f"but prompt too large ({prompt_tokens} tokens > {LLM_FALLBACK_TOKEN_CAP} cap); "
                f"skipping LLM fallback to prevent 413 Payload Too Large"
            )
            result["confidence"] = max(result["confidence"], 0.5)
            # Still attach routing info so we don't lose model assignment
            if with_routing and NodeRegistry:
                _attach_routing(result, prompt)
            return result
        
        try:
            llm_result = llm_classify(prompt)
            llm_result["heuristic"] = result  # Attach heuristic for comparison
            llm_result["fallback_reason"] = f"Heuristic confidence {result['confidence']} < {llm_fallback_threshold}"
            result = llm_result
        except Exception as e:
            # LLM failed, use heuristic anyway with warning
            result["fallback_reason"] = f"LLM fallback failed ({str(e)[:60]}), using heuristic despite low confidence"
            result["confidence"] = max(result["confidence"], 0.5)  # Boost to usable
    
    if with_routing and NodeRegistry:
        _attach_routing(result, prompt, health_status)
    
    # ── Auto-decomposition trigger (P2) ──
    # Write trigger when complexity is medium/hard and prompt touches multiple domains/files
    _write_decomposition_trigger(result, prompt)
    
    return result


def _attach_routing(result: Dict, prompt: str = "", health_status: str = "healthy"):
    """Attach node-model routing info to classification result via NodeRegistry."""
    import json
    start = time.time()
    try:
        reg = NodeRegistry()
        
        # Health-aware routing
        if health_status == "stressed":
            # Dynamic: find best node with qwen3:8b (or next best medium model)
            all_routes = []
            for node_name in ["fnet4", "fnet3", "fnet5", "fnet6"]:
                node_data = reg.nodes.get(node_name, {})
                for m in node_data.get("models", []):
                    if m["id"] in ["qwen3:8b", "qwen3.5:4b"]:
                        tps = m.get("tokens_per_sec", 0)
                        all_routes.append({
                            "node": node_name,
                            "model": m["id"],
                            "provider": "ollama",
                            "tokens_per_sec": tps,
                        })
            if all_routes:
                # Sort by tokens/sec descending
                all_routes.sort(key=lambda x: -x["tokens_per_sec"])
                route = all_routes[0]
            else:
                # Fallback: query NodeRegistry for medium complexity
                route = reg.best_model_for("medium")
            result["route"] = route
            result["health_override"] = True
            result["route_note"] = f"Orchestrator {health_status} -- routed to {route['node']}/{route['model']}"
        elif health_status == "critical":
            # Dynamic: find cheapest available cloud model from models.json
            try:
                models_path = Path.home() / ".pi" / "agent" / "models.json"
                with open(models_path) as f:
                    models_data = json.load(f)
                
                cloud_models = []
                for prov in models_data.get("providers", {}).values():
                    for m in prov.get("models", []):
                        mid = m.get("id", "")
                        if "cloud" in mid:
                            cost = m.get("cost", {})
                            # Compute cost per 1K tokens (in + out)
                            cost_per_1k = (1000 * cost.get("input", 0) / 1_000_000) + (1500 * cost.get("output", 0) / 1_000_000)
                            cloud_models.append({
                                "model": mid,
                                "cost_per_1k": round(cost_per_1k, 4),
                            })
                
                if cloud_models:
                    cloud_models.sort(key=lambda x: x["cost_per_1k"])
                    cheapest = cloud_models[0]
                    route = {
                        "node": "cloud",
                        "model": cheapest["model"],
                        "provider": "ollama-cloud",
                        "tokens_per_sec": 0,
                    }
                else:
                    route = {"node": "cloud", "model": "qwen3.5:397b-cloud", "provider": "ollama-cloud", "tokens_per_sec": 0}
            except Exception:
                route = {"node": "cloud", "model": "qwen3.5:397b-cloud", "provider": "ollama-cloud", "tokens_per_sec": 0}
            
            result["route"] = route
            result["health_override"] = True
            result["route_note"] = f"Orchestrator {health_status} -- routed to cloud {route['model']} (${cheapest.get('cost_per_1k',0):.4f}/1Ktk)"
        else:
            # Normal routing
            route = reg.best_model_for(result["complexity"].lower())
            if route:
                result["route"] = {
                    "node": route["node"],
                    "model": route["model"],
                    "provider": route["provider"],
                    "tokens_per_sec": route["tokens_per_sec"],
                }
            else:
                result["route"] = None
                result["route_note"] = "No local model matches -- cloud fallback needed"
        
        # Log the routing decision
        if log_routing_decision and result.get("route"):
            elapsed = int((time.time() - start) * 1000) + result.get("latency_ms", 0)
            cost = 0 if result["route"]["provider"] == "ollama" else 0.011
            log_routing_decision(
                prompt=prompt,
                complexity=result["complexity"],
                model=result["route"]["model"],
                latency_ms=elapsed,
                cost=cost,
                node=result["route"]["node"],
                provider=result["route"]["provider"]
            )
        else:
            result["route"] = None
            result["route_note"] = "No local model matches -- cloud fallback needed"
    except Exception as e:
        result["route"] = None
        result["route_note"] = f"Registry lookup failed: {str(e)[:60]}"

# ── CLI ──────────────────────────────────────────────────────────────

def _write_decomposition_trigger(result: Dict, prompt: str):
    """Write a decomposition trigger when complexity warrants fan-out.
    
    Triggers when:
    - complexity is MEDIUM or HARD
    - prompt mentions multiple domains (≥2 distinct domain keywords)
    - prompt implies multi-file work (≥3 files or 'all nodes')
    """
    complexity = result.get("complexity", "MEDIUM")
    if complexity not in ("MEDIUM", "HARD"):
        return  # Simple tasks don't need decomposition
    
    # Count domain keywords in prompt
    prompt_lower = prompt.lower()
    domains_found = set()
    for domain in domain_complexity.keys():
        if domain in prompt_lower:
            domains_found.add(domain)
    
    # Multi-file indicators
    file_indicators = [
        r"\b(all|every|each)\b.*\b(node|file|script|config|playbook|role|template|domain|agent|task|chain)\b",
        r"\b(multiple|several|many|various)\b.*\b(file|script|node|config|playbook|task|step)\b",
        r"\b(3|4|5|6|7)\b.*\b(file|script|node|config|playbook|task|step|node)\b",
        r"\b(update|fix|sync|deploy|distribute)\b.*\b(all|every|each|multiple|all 7)\b",
    ]
    multi_file = any(re.search(p, prompt_lower) for p in file_indicators)
    
    # Decision
    should_decompose = len(domains_found) >= 2 or multi_file
    
    if should_decompose:
        trigger_dir = Path.home() / ".pi" / "decomposition-triggers"
        trigger_dir.mkdir(parents=True, exist_ok=True)
        
        import hashlib
        trigger_id = hashlib.md5(f"{prompt}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        trigger_file = trigger_dir / f"pending" / f"{trigger_id}.json"
        trigger_file.parent.mkdir(exist_ok=True)
        
        trigger = {
            "id": trigger_id,
            "prompt": prompt,
            "complexity": complexity,
            "confidence": result.get("confidence", 0),
            "domains": sorted(domains_found),
            "multi_file": multi_file,
            "created_at": datetime.now().isoformat(),
            "route": result.get("route"),
            "status": "pending",
        }
        trigger_file.write_text(json.dumps(trigger, indent=2))
        result["decomposition_trigger"] = {
            "id": trigger_id,
            "path": str(trigger_file),
            "reason": f"{len(domains_found)} domains + multi_file={multi_file}",
        }

# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Hybrid prompt complexity classifier")
    parser.add_argument("prompt", nargs="?", help="Single prompt to classify")
    parser.add_argument("--file", help="File with one prompt per line")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--llm", action="store_true", help="Force LLM classification")
    parser.add_argument("--threshold", type=float, default=0.75, help="Heuristic confidence threshold")
    parser.add_argument("--profile", action="store_true", help="Show latency profile")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--route", action="store_true", help="Show node-model routing (requires TI-016 profiles)")
    args = parser.parse_args()
    
    prompts = []
    if args.prompt:
        prompts.append(args.prompt)
    elif args.file:
        with open(args.file) as f:
            prompts = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    else:
        # Demo prompts
        prompts = [
            "Check if fnet2 is online",
            "Write a Python script that submits tasks to remote nodes",
            "Create an Ansible playbook that sets up Ollama on 7 nodes",
            "Design a meta-orchestration framework with complexity classification",
            "Format this JSON with proper indentation",
        ]
    
    results = []
    for p in prompts:
        results.append(classify(p, args.threshold, args.llm, with_routing=args.route))
    
    if args.json:
        print(json.dumps(results[0] if len(results) == 1 else results, indent=2))
        return
    
    # Table output
    if args.route:
        print(f"{'#':<3} {'Complexity':<10} {'Conf':<6} {'Latency':<10} {'Tier':<8} {'Method':<12} {'Node/Model':<20} {'Prompt'}")
        print("-" * 140)
    else:
        print(f"{'#':<3} {'Complexity':<10} {'Conf':<6} {'Latency':<10} {'Tier':<8} {'Method':<12} {'Prompt'}")
        print("-" * 120)
    for i, r in enumerate(results):
        method = "LLM" if not r.get("heuristic") else f"heur ({r['latency_ms']}ms)"
        marker = "🤖" if not r.get("heuristic") else "⚡"
        if args.route:
            route_str = f"{r['route']['node']}/{r['route']['model']}" if r.get('route') else "(cloud)"
            print(f"{i+1:<3} {r['complexity']:<10} {r['confidence']:.2f}   {r['latency_ms']}ms      {r['suggested_tier']:<8} {method:<12} {route_str:<20} {prompts[i][:40]}")
        else:
            print(f"{i+1:<3} {r['complexity']:<10} {r['confidence']:.2f}   {r['latency_ms']}ms      {r['suggested_tier']:<8} {method:<12} {prompts[i][:50]}")
    
    print()
    heuristic_count = sum(1 for r in results if r.get("heuristic"))
    llm_count = len(results) - heuristic_count
    print(f"Results: {len(results)} prompts | {heuristic_count} heuristic ({heuristic_count/len(results)*100:.0f}%) | {llm_count} LLM fallback ({llm_count/len(results)*100:.0f}%)")
    
    if args.profile:
        h_latencies = [r["latency_ms"] for r in results if r.get("heuristic")]
        if h_latencies:
            print(f"Heuristic latency: min={min(h_latencies)}ms max={max(h_latencies)}ms avg={sum(h_latencies)//len(h_latencies)}ms")
        l_latencies = [r["latency_ms"] for r in results if not r.get("heuristic")]
        if l_latencies:
            print(f"LLM latency: min={min(l_latencies)}ms max={max(l_latencies)}ms avg={sum(l_latencies)//len(l_latencies)}ms")
    
    if args.verbose:
        print("\n--- Reasoning ---")
        for i, r in enumerate(results):
            print(f"\n[{i+1}] {prompts[i]}")
            print(f"    Complexity: {r['complexity']} (confidence: {r['confidence']:.2f})")
            print(f"    Reasoning: {r['reasoning']}")
            if r.get("fallback_reason"):
                print(f"    Fallback: {r['fallback_reason']}")
            if isinstance(r.get("heuristic"), dict):
                print(f"    Heuristic would have guessed: {r['heuristic']['complexity']} (conf: {r['heuristic']['confidence']:.2f})")

if __name__ == "__main__":
    main()

# ── ROUTER INTEGRATION ──────────────────────────────────────────────

def inject_complexity_tag(prompt: str, llm_fallback_threshold: float = 0.60) -> str:
    """Classify prompt and return it with injected complexity + routing tag for keyword-router.
    
    Usage:
        tagged = inject_complexity_tag("Check if fnet2 is online")
        # Returns: "Check if fnet2 is online\n\n<!-- complexity: trivial -->\n<!-- route: fnet6/qwen3.5:4b -->"
    """
    result = classify(prompt, llm_fallback_threshold, with_routing=True)
    complexity = result["complexity"].lower()
    route_part = ""
    if result.get("route"):
        r = result["route"]
        route_part = f"\n<!-- route: {r['node']}/{r['model']} -->"
    return f"{prompt}\n\n<!-- complexity: {complexity} -->{route_part}"
