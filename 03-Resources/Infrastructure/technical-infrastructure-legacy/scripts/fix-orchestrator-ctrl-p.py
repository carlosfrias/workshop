#!/usr/bin/env python3
"""
fix-orchestrator-ctrl-p.py — Fix Ctrl+P model cycling on Mac orchestrator

Problem: pi-ollama-cloud extension registers models without :cloud suffix,
creating duplicates not in models.json. This script:
1. Backs up current config
2. Removes pi-ollama-cloud from packages (prevents duplicate model registration)
3. Creates keyword-router.json using models.json format (:cloud suffix, ollama provider)
4. Verifies only models.json models remain available
"""
import json, shutil, sys
from pathlib import Path

SETTINGS_FILE = Path.home() / ".pi/agent/settings.json"
BACKUP_DIR = Path.home() / ".pi/agent/backups"
KEYWORD_ROUTER_FILE = Path.home() / ".pi/agent/keyword-router.json"

def backup_file(path: Path):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"{path.name}.{Path(__file__).stem}.bak"
    shutil.copy2(path, backup_path)
    print(f"✓ Backed up {path} → {backup_path}")

def remove_ollama_cloud_extension():
    """Remove pi-ollama-cloud from settings.json packages."""
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)

    original_count = len(settings.get("packages", []))
    settings["packages"] = [
        pkg for pkg in settings.get("packages", [])
        if "pi-ollama-cloud" not in pkg
    ]
    new_count = len(settings["packages"])

    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

    removed = original_count - new_count
    if removed > 0:
        print(f"✓ Removed pi-ollama-cloud extension from settings.json")
    else:
        print(f"ℹ pi-ollama-cloud extension not found in settings.json")
    return removed > 0

def create_keyword_router_config():
    """Create keyword-router.json using models.json conventions."""
    config = {
        "default": {
            "provider": "ollama",
            "model": "gemma4:e4b",
            "thinkingLevel": "off"
        },
        "routes": {
            "reasoning": {
                "name": "reasoning",
                "provider": "ollama",
                "model": "qwen3.5:397b-cloud",
                "thinkingLevel": "medium",
                "keywords": ["analyze", "evaluate", "decide", "synthesize"],
                "domains": ["market-research", "position-management"],
                "description": "Complex reasoning and decision-making",
                "priority": 1
            },
            "structured": {
                "name": "structured",
                "provider": "ollama",
                "model": "gemma4:e4b",
                "thinkingLevel": "off",
                "keywords": ["log", "record", "reconcile", "parse", "format"],
                "domains": ["bookkeeping"],
                "description": "Structured data operations"
            },
            "monitoring": {
                "name": "monitoring",
                "provider": "ollama",
                "model": "qwen3.5:4b",
                "thinkingLevel": "off",
                "keywords": ["status", "check", "ping", "monitor"],
                "description": "Status checks and lightweight reporting"
            },
            "infrastructure": {
                "name": "infrastructure",
                "provider": "ollama",
                "model": "qwen3:8b",
                "thinkingLevel": "off",
                "keywords": ["server", "deploy", "network", "ssh"],
                "description": "Infrastructure operations"
            },
            "trivial": {
                "name": "trivial",
                "provider": "ollama",
                "model": "qwen3.5:4b",
                "thinkingLevel": "off",
                "description": "Single-step deterministic tasks under 500 tokens"
            },
            "simple": {
                "name": "simple",
                "provider": "ollama",
                "model": "qwen3:8b",
                "thinkingLevel": "low",
                "description": "Bounded tasks with known output, 1-2 steps"
            },
            "medium": {
                "name": "medium",
                "provider": "ollama",
                "model": "gemma4:e4b",
                "thinkingLevel": "medium",
                "description": "Multi-step tasks requiring coordination, 3-5 steps"
            },
            "hard": {
                "name": "hard",
                "provider": "ollama",
                "model": "kimi-k2.6:cloud",
                "thinkingLevel": "high",
                "description": "Open-ended, novel, or cross-domain integration tasks"
            }
        },
        "enableComplexityRouting": True,
        "complexityConfidenceThreshold": 0.55,
        "respectManualSelection": True,
        "notifyOnSwitch": True,
        "maxHistorySize": 50
    }

    with open(KEYWORD_ROUTER_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Created {KEYWORD_ROUTER_FILE}")

def verify_available_models():
    """Verify only models.json models are available."""
    models_json = Path.home() / ".pi/agent/models.json"
    with open(models_json) as f:
        cfg = json.load(f)

    configured = set()
    for provider, pcfg in cfg.get("providers", {}).items():
        for m in pcfg.get("models", []):
            configured.add(f"{provider}/{m.get('id')}")

    print(f"\nModels in models.json: {len(configured)}")
    for mid in sorted(configured):
        print(f"  ✓ {mid}")

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("1. Restart pi completely (quit and reopen)")
    print("2. Press Ctrl+P — only the above models should appear")
    print("3. If old models still appear, run: pi uninstall github:fgrehm/pi-ollama-cloud")
    print("="*60)

def main():
    print("Fixing Ctrl+P on orchestrator (Mac)...")
    print("="*60)

    # Backup
    if SETTINGS_FILE.exists():
        backup_file(SETTINGS_FILE)

    # Remove extension
    changed = remove_ollama_cloud_extension()

    # Create keyword router config
    create_keyword_router_config()

    # Verify
    verify_available_models()

    if changed:
        print("\n⚠ IMPORTANT: Restart pi for changes to take effect")

if __name__ == "__main__":
    main()
