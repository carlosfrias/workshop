#!/usr/bin/env python3
"""
test-phase-loading.py — Verify phase-based AGENTS.md decomposition

Tests that each phase file:
1. Loads correctly as markdown
2. Is under the stated token budget
3. Contains the expected section headers
4. References the next phase correctly

Usage:
    python3 scripts/test-phase-loading.py
    python3 scripts/test-phase-loading.py --verbose
"""
import json
import sys
from pathlib import Path

PHASES_DIR = Path(".pi/agents/phases")
INDEX_FILE = PHASES_DIR / "phase-index.json"


def load_index() -> dict:
    with open(INDEX_FILE) as f:
        return json.load(f)


def check_phase(phase_name: str, phase_info: dict, verbose: bool = False) -> list:
    """Check a single phase file. Returns list of error strings."""
    errors = []
    file_path = PHASES_DIR / phase_info["file"]
    
    # 1. File exists
    if not file_path.exists():
        errors.append(f"{phase_name}: File missing: {file_path}")
        return errors
    
    # 2. Load content
    content = file_path.read_text()
    chars = len(content)
    tokens = chars // 4
    
    # 3. Check token budget
    stated_tokens = phase_info.get("tokens", "")
    if stated_tokens:
        # Extract number from "~800" or "~2,800"
        import re
        match = re.search(r"[\d,]+", stated_tokens)
        if match:
            stated = int(match.group().replace(",", ""))
            if tokens > stated * 1.2:  # Allow 20% variance
                errors.append(f"{phase_name}: Token overrun: {tokens} vs stated {stated}")
    
    # 4. Check expected headers
    expected_headers = {
        "domain-activation": ["Domain Activation Check", "Domain Agent File Routing"],
        "planning": ["Framework Readiness Check", "TI-011 Meta-Orchestration"],
        "execution": ["Must Always", "Must Never"],
        "quality-check": ["Quality Checklist"],
        "documentation": ["Session Documentation", "Backlog Updates"],
    }
    for header in expected_headers.get(phase_name, []):
        if header not in content:
            errors.append(f"{phase_name}: Missing expected section: '{header}'")
    
    # 5. Check next phase reference (except phase 5)
    if phase_name != "documentation":
        next_phrase = "Next Phase"
        if next_phrase not in content:
            errors.append(f"{phase_name}: Missing '{next_phrase}' section")
    
    if verbose:
        print(f"  {phase_name}: {chars} chars ≈ {tokens} tokens — {file_path.name}")
    
    return errors


def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print("═" * 60)
    print("  Phase-Based AGENTS.md Verification")
    print("═" * 60)
    print()
    
    # Load index
    try:
        index = load_index()
    except Exception as e:
        print(f"❌ Failed to load phase index: {e}")
        sys.exit(1)
    
    phases = index.get("phases", {})
    print(f"Phases found: {len(phases)}")
    print(f"Load order: {', '.join(index.get('load_order', []))}")
    print()
    
    # Check each phase
    all_errors = []
    for phase_name in index.get("load_order", []):
        phase_info = phases.get(phase_name, {})
        errors = check_phase(phase_name, phase_info, verbose)
        all_errors.extend(errors)
        
        if not errors:
            print(f"  ✅ {phase_name}: PASS")
    
    print()
    
    # Report results
    if all_errors:
        print("❌ Failures:")
        for err in all_errors:
            print(f"  - {err}")
        print(f"\nTotal: {len(all_errors)} errors")
        sys.exit(1)
    else:
        # Calculate reduction
        orig_agents_full = Path("technical-infrastructure/AGENTS-full.md")
        orig_size = orig_agents_full.stat().st_size if orig_agents_full.exists() else 25278
        max_phase = max(
            (PHASES_DIR / p["file"]).stat().st_size
            for p in phases.values()
        )
        reduction = (orig_size - max_phase) * 100 // orig_size
        
        print("🟢 All phases verified.")
        print(f"   Original AGENTS-full.md: {orig_size:,} bytes")
        print(f"   Heaviest single phase: {max_phase:,} bytes")
        print(f"   Per-inference reduction: {reduction}%")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
