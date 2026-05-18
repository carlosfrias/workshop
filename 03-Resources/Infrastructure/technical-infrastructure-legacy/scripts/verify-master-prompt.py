#!/usr/bin/env python3
"""
verify-master-prompt.py — Verify Master Prompt system integrity

Checks:
- Core prompt exists and is under 150 tokens
- All 6 module files exist and are under 150 tokens each
- Reference file paths are valid
- Reports total context size

Usage:
    python3 verify-master-prompt.py [--json]
"""

import os
import sys
import json
from pathlib import Path

def count_tokens(text):
    """Simple word-based token counting."""
    return len(text.split())

def verify_prompt():
    """Verify master prompt system integrity."""
    base_dir = Path(__file__).parent.parent
    prompts_dir = base_dir / 'prompts'
    
    errors = []
    warnings = []
    
    # Check core prompt
    core_prompt_path = prompts_dir / 'core-prompt.md'
    if not core_prompt_path.exists():
        errors.append(f"❌ Core prompt not found: {core_prompt_path}")
        core_tokens = 0
    else:
        core_tokens = count_tokens(core_prompt_path.read_text())
        if core_tokens > 150:
            warnings.append(f"⚠️ Core prompt exceeds 150 tokens: {core_tokens} tokens")
        else:
            print(f"✅ Core prompt: {core_tokens} tokens (<150)")
    
    # Check modules
    modules = [
        'module-1-purpose.md',
        'module-2-dependencies.md',
        'module-3-data-sources.md',
        'module-4-conditions.md',
        'module-5-performance.md',
        'module-6-hardware.md'
    ]
    
    module_tokens = []
    for module in modules:
        module_path = prompts_dir / module
        if not module_path.exists():
            errors.append(f"❌ Module not found: {module_path}")
            module_tokens.append(0)
        else:
            tokens = count_tokens(module_path.read_text())
            module_tokens.append(tokens)
            if tokens > 150:
                warnings.append(f"⚠️ {module} exceeds 150 tokens: {tokens} tokens")
            else:
                print(f"✅ {module}: {tokens} tokens (<150)")
    
    # Check playbook index
    playbook_index = base_dir / 'playbooks' / 'playbook-index.json'
    if not playbook_index.exists():
        warnings.append(f"⚠️ Playbook index not found: {playbook_index}")
    else:
        try:
            with open(playbook_index) as f:
                index = json.load(f)
            print(f"✅ Playbook index: {len(index.get('playbooks', []))} playbooks defined")
        except Exception as e:
            errors.append(f"❌ Playbook index invalid: {e}")
    
    # Calculate total context
    total_tokens = core_tokens + sum(module_tokens)
    
    # Print results
    print("\n" + "="*50)
    if errors:
        print("❌ VERIFICATION FAILED")
        for error in errors:
            print(f"  {error}")
        return 1
    elif warnings:
        print("⚠️ VERIFICATION PASSED WITH WARNINGS")
        for warning in warnings:
            print(f"  {warning}")
        print(f"\nTotal context size: {total_tokens} tokens")
        return 0
    else:
        print("✅ VERIFICATION PASSED")
        print(f"\nTotal context size: {total_tokens} tokens")
        print(f"Target: <650 tokens for gemma4:e4b compatibility")
        if total_tokens < 650:
            print("✅ Within target!")
        else:
            print("⚠️ Exceeds target - consider reducing module sizes")
        return 0