#!/usr/bin/env python3
"""
validate-router-config.py — Validate pi-keyword-router configuration consistency

Checks for:
1. Multiple config files that could collide (project-level, global, stale model-router.json)
2. Default thinking level mismatch (should be "off", not "medium")
3. Stop-words in reasoning route keywords ("what", "when", "which", "why", "where")
4. Missing infrastructure keywords (orchestration, decomposition, framework, etc.)
5. Route priority consistency (reasoning should be 1, infrastructure 0)

Usage:
    python3 scripts/validate-router-config.py
    python3 scripts/validate-router-config.py --fix

Exit codes:
    0 — Config is clean
    1 — Warnings found
    2 — Errors found (collision or critical misconfiguration)
"""
import json
import sys
import argparse
from pathlib import Path

HOME = Path.home()
PROJECT_ROOT = Path("/Users/friasc/Dropbox/ai-trading-workspace")

CONFIG_PATHS = {
    "project": PROJECT_ROOT / ".pi" / "keyword-router.json",
    "global": HOME / ".pi" / "agent" / "keyword-router.json",
    "stale_model_router": HOME / ".pi" / "model-router.json",
    "stale_global_model": HOME / ".pi" / "agent" / "model-router.json",
}

STOP_WORDS = {"what", "when", "which", "why", "where"}
INFRASTRUCTURE_KEYWORDS = {
    "orchestration", "orchestrate", "framework", "pipeline", "wiring",
    "decomposition", "decompose", "distribute", "distribution", "fan out",
    "route", "routing", "classify", "complexity", "queue", "worker",
    "node", "cluster", "performance", "latency", "ansible", "playbook",
}


def load_config(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ {path}: Invalid JSON — {e}")
        return None


def check_stale_files() -> list:
    """Check for stale config files that could cause confusion."""
    issues = []
    for name, path in CONFIG_PATHS.items():
        if "stale" in name and path.exists():
            issues.append(f"⚠️  Stale file exists: {path} (not read by router, may confuse operators)")
        elif name == "global" and path.exists():
            issues.append(f"⚠️  Global fallback exists: {path} (project-level overrides it, but divergence possible)")
    return issues


def check_default_thinking(cfg: dict, label: str) -> list:
    """Check that default thinking level is 'off', not 'medium'."""
    issues = []
    default = cfg.get("default", {})
    tl = default.get("thinkingLevel", "NOT SET")
    if tl != "off":
        issues.append(f"❌ {label}: default.thinkingLevel = '{tl}' (should be 'off')")
    return issues


def check_reasoning_keywords(cfg: dict, label: str) -> list:
    """Check reasoning route for stop-words that match every question."""
    issues = []
    routes = cfg.get("routes", {})
    reasoning = routes.get("reasoning", {})
    keywords = set(reasoning.get("keywords", []))
    found_stop = keywords & STOP_WORDS
    if found_stop:
        issues.append(f"❌ {label}: reasoning route has stop-words {sorted(found_stop)} — matches every question")
    return issues


def check_infrastructure_keywords(cfg: dict, label: str) -> list:
    """Check infrastructure route has orchestration/decomposition keywords."""
    issues = []
    routes = cfg.get("routes", {})
    infra = routes.get("infrastructure", {})
    keywords = set(infra.get("keywords", []))
    missing = INFRASTRUCTURE_KEYWORDS - keywords
    if missing:
        issues.append(f"⚠️  {label}: infrastructure route missing keywords {sorted(missing)}")
    return issues


def check_reasoning_priority(cfg: dict, label: str) -> list:
    """Check reasoning route priority is 1 (not 0)."""
    issues = []
    routes = cfg.get("routes", {})
    reasoning = routes.get("reasoning", {})
    priority = reasoning.get("priority")
    if priority != 1:
        issues.append(f"⚠️  {label}: reasoning priority = {priority} (should be 1 to override domain routes)")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Validate pi-keyword-router config")
    parser.add_argument("--fix", action="store_true", help="Apply fixes where possible")
    args = parser.parse_args()

    print("═" * 60)
    print("  pi-keyword-router Config Validator")
    print("═" * 60)
    print()

    all_issues = []
    critical = 0

    # ── Check for stale/collision files ──
    stale_issues = check_stale_files()
    all_issues.extend(stale_issues)
    for issue in stale_issues:
        if "❌" in issue:
            critical += 1

    # ── Load project-level config (authoritative) ──
    project_cfg = load_config(CONFIG_PATHS["project"])
    if project_cfg is None:
        print(f"❌ Project config not found: {CONFIG_PATHS['project']}")
        critical += 1
        print()
        print(f"Result: {critical} critical, {len(all_issues)} total issues")
        sys.exit(2)

    print(f"✅ Authoritative config: {CONFIG_PATHS['project']}")
    print()

    # ── Validate project-level config ──
    checks = [
        ("default thinking", check_default_thinking),
        ("reasoning stop-words", check_reasoning_keywords),
        ("infrastructure keywords", check_infrastructure_keywords),
        ("reasoning priority", check_reasoning_priority),
    ]

    for check_name, check_fn in checks:
        issues = check_fn(project_cfg, "project")
        all_issues.extend(issues)
        for issue in issues:
            print(f"  {issue}")
        if issues:
            print()

    # ── Count issues ──
    for issue in all_issues:
        if "❌" in issue:
            critical += 1

    print("─" * 60)
    print(f"Result: {critical} critical, {len(all_issues)} total issues")
    print()

    if critical > 0:
        print("🔴 Config has critical errors. Fix before proceeding.")
        sys.exit(2)
    elif all_issues:
        print("🟡 Config has warnings. Review recommended.")
        sys.exit(1)
    else:
        print("🟢 Config is clean.")
        sys.exit(0)


if __name__ == "__main__":
    main()
