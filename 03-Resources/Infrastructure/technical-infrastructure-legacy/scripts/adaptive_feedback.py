#!/usr/bin/env python3
"""
adaptive_feedback.py — Adaptive Feedback Loop for TI-011 Meta-Orchestration
Reads performance logs, identifies patterns, suggests routing updates.

Usage:
    python3 adaptive_feedback.py --days 7 --dry-run
    python3 adaptive_feedback.py --days 7 --apply
    python3 adaptive_feedback.py --report
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Resolve paths: this script is in technical-infrastructure/scripts/
REPO_ROOT = Path(__file__).resolve().parents[2]
SESSIONS_DIR = REPO_ROOT / "technical-infrastructure" / "wiki" / "operational" / "sessions"
JSONL_FILE = SESSIONS_DIR / "model-routing-decisions.jsonl"


def load_logs(days: int = 7) -> List[Dict]:
    if not JSONL_FILE.exists():
        print(f"No log file found at {JSONL_FILE}")
        return []
    
    cutoff = datetime.now() - timedelta(days=days)
    logs = []
    with open(JSONL_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("timestamp", "1970-01-01T00:00:00"))
                if ts >= cutoff:
                    logs.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue
    return logs


def analyze_patterns(logs: List[Dict]) -> Dict:
    patterns = {"local_success": {}, "cloud_needed": {}, "by_complexity": {}}
    stop_words = {"the","and","for","are","but","not","you","all","can","had","her","was","one","our","out","day","get","has","him","his","how","its","may","new","now","old","see","two","way","who","boy","did","she","use","than","them","well","were"}
    
    for entry in logs:
        prompt = entry.get("prompt_preview", "").lower()
        complexity = entry.get("complexity", "UNKNOWN")
        provider = entry.get("provider", "unknown")
        
        words = [w for w in re.findall(r'\b[a-z]{3,}\b', prompt) if w not in stop_words]
        prompt_key = " ".join(words[:3]) if words else "unknown"
        
        if complexity not in patterns["by_complexity"]:
            patterns["by_complexity"][complexity] = []
        patterns["by_complexity"][complexity].append(entry)
        
        if provider == "ollama":
            if prompt_key not in patterns["local_success"]:
                patterns["local_success"][prompt_key] = []
            patterns["local_success"][prompt_key].append(entry)
        else:
            if prompt_key not in patterns["cloud_needed"]:
                patterns["cloud_needed"][prompt_key] = []
            patterns["cloud_needed"][prompt_key].append(entry)
    
    return patterns


def suggest_updates(patterns: Dict) -> List[Dict]:
    suggestions = []
    
    for keyword, entries in patterns["local_success"].items():
        complexities = set(e.get("complexity", "") for e in entries)
        if complexities == {"MEDIUM"} or complexities == {"HARD"}:
            avg_latency = sum(e.get("latency_ms", 0) for e in entries) / len(entries)
            if avg_latency < 3000:
                suggestions.append({
                    "type": "downgrade",
                    "keyword": keyword,
                    "from_tier": list(complexities)[0],
                    "to_tier": "SIMPLE",
                    "rationale": f"{len(entries)} runs, avg {avg_latency:.0f}ms on local.",
                    "confidence": min(len(entries) / 5, 1.0),
                })
    
    for keyword, entries in patterns["cloud_needed"].items():
        complexities = set(e.get("complexity", "") for e in entries)
        if complexities == {"SIMPLE"} or complexities == {"TRIVIAL"}:
            avg_latency = sum(e.get("latency_ms", 0) for e in entries) / len(entries)
            suggestions.append({
                "type": "upgrade",
                "keyword": keyword,
                "from_tier": list(complexities)[0],
                "to_tier": "MEDIUM",
                "rationale": f"{len(entries)} runs needed cloud, avg {avg_latency:.0f}ms.",
                "confidence": min(len(entries) / 5, 1.0),
            })
    
    suggestions.sort(key=lambda x: -x["confidence"])
    return suggestions


def apply_updates(suggestions: List[Dict], dry_run: bool = True) -> str:
    if not suggestions:
        return "No updates suggested."
    
    report_lines = ["# Adaptive Feedback Report", f"Generated: {datetime.now().isoformat()}", ""]
    
    for s in suggestions:
        if s["confidence"] < 0.5:
            continue
        report_lines.append(f"## {s['type'].upper()}: {s['keyword']}")
        if 'from_tier' in s:
            report_lines.append(f"- **From:** {s['from_tier']}")
        if 'to_tier' in s:
            report_lines.append(f"- **To:** {s['to_tier']}")
        report_lines.append(f"- **Rationale:** {s['rationale']}")
        report_lines.append(f"- **Confidence:** {s['confidence']:.0%}")
        report_lines.append("")
    
    report = "\n".join(report_lines)
    
    if dry_run:
        return report + "\n\n---\nDRY RUN: No changes applied."
    
    rec_dir = REPO_ROOT / "technical-infrastructure" / "wiki" / "operational" / "recommendations"
    rec_dir.mkdir(parents=True, exist_ok=True)
    rec_file = rec_dir / f"RECOMMENDATION-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md"
    with open(rec_file, 'w') as f:
        f.write(report)
    
    return report + f"\n\n---\nWritten to: {rec_file}"


def main():
    parser = argparse.ArgumentParser(description="Adaptive feedback loop for TI-011")
    parser.add_argument("--days", type=int, default=7, help="Days of logs to analyze")
    parser.add_argument("--dry-run", action="store_true", help="Print without applying")
    parser.add_argument("--apply", action="store_true", help="Apply updates")
    parser.add_argument("--report", action="store_true", help="Show patterns only")
    args = parser.parse_args()
    
    logs = load_logs(args.days)
    if not logs:
        print("No logs found.")
        sys.exit(1)
    
    print(f"Loaded {len(logs)} log entries from last {args.days} days")
    
    patterns = analyze_patterns(logs)
    
    if args.report:
        print(f"\n=== Pattern Summary ===")
        print(f"Local successes: {len(patterns['local_success'])} unique prompt patterns")
        print(f"Cloud escalations: {len(patterns['cloud_needed'])} unique prompt patterns")
        for c, entries in sorted(patterns['by_complexity'].items()):
            print(f"  {c}: {len(entries)} prompts")
        sys.exit(0)
    
    suggestions = suggest_updates(patterns)
    result = apply_updates(suggestions, dry_run=not args.apply)
    print(result)


if __name__ == "__main__":
    main()
