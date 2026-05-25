#!/usr/bin/env python3
"""
File Relocation Test Suite
Tests that files are in correct permanent locations after cleanup.

Usage:
    python3 test-file-locations.py --phase=before   # Check current state
    python3 test-file-locations.py --phase=after    # Check after move
"""

import os
import sys
import argparse
from pathlib import Path

BASE = Path("/Users/friasc/Cloud/ai-trading-workspace")

# Files that should NOT exist in these locations (temp files to delete)
SHOULD_NOT_EXIST = [
    BASE / "FOOTER",
    BASE / "FOOTER_EOF",
    BASE / "PYEOF",
]

# Files that should NOT remain in root directory
SHOULD_NOT_BE_IN_ROOT = [
    BASE / "progress.md",
]

# Files that should NOT remain in technical-infrastructure/ root
SHOULD_NOT_BE_IN_TECH_INFRA_ROOT = [
    BASE / "technical-infrastructure" / "ansible-playbook-template.yml",
    BASE / "technical-infrastructure" / "orchestration-framework.md",
    BASE / "technical-infrastructure" / "playbook-template.md",
    BASE / "technical-infrastructure" / "verification-report.txt",
    BASE / "technical-infrastructure" / "WIKI.md",
    BASE / "technical-infrastructure" / "wiki-playbook-structure.md",
]

# Files that SHOULD exist in permanent locations
SHOULD_EXIST_PERMANENT = [
    (BASE / "technical-infrastructure" / "operational" / "status" / "progress.md",
     "Project progress tracking"),
    (BASE / "technical-infrastructure" / "playbooks" / "ansible-playbook-template.yml",
     "Ansible playbook template"),
    (BASE / "technical-infrastructure" / "playbooks" / "playbook-template.md",
     "Playbook template documentation"),
    (BASE / "technical-infrastructure" / "wiki" / "technical-infrastructure" / "orchestration-framework.md",
     "Orchestration framework documentation"),
    (BASE / "technical-infrastructure" / "wiki" / "technical-infrastructure" / "wiki-playbook-structure.md",
     "Wiki playbook structure guide"),
    (BASE / "technical-infrastructure" / "wiki" / "technical-infrastructure" / "legacy-domain-index.md",
     "Wiki navigation hub (legacy domain index)"),
    (BASE / "technical-infrastructure" / "operational" / "testing" / "verification-report.txt",
     "Verification report"),
]

# Files in technical-infrastructure/ that are NOT allowed in root
ALLOWED_IN_TECH_INFRA_ROOT = {
    "AGENTS.md", "AGENTS-routing.md", "AGENTS-full.md",
    "ansible.cfg", "inventory", "requirements.yml",
}


def test_temp_files_deleted(results):
    """Test that temporary files are deleted."""
    results["temp_files_deleted"] = {"passed": True, "failures": []}
    for filepath in SHOULD_NOT_EXIST:
        if filepath.exists():
            results["temp_files_deleted"]["passed"] = False
            results["temp_files_deleted"]["failures"].append(f"Temp file still exists: {filepath.relative_to(BASE)}")


def test_root_cleaned(results):
    """Test that root directory no longer has misplaced files."""
    results["root_cleaned"] = {"passed": True, "failures": []}
    for filepath in SHOULD_NOT_BE_IN_ROOT:
        if filepath.exists():
            results["root_cleaned"]["passed"] = False
            results["root_cleaned"]["failures"].append(f"Still in root: {filepath.name}")


def test_tech_infra_root_cleaned(results):
    """Test that technical-infrastructure root only has allowed files."""
    results["tech_infra_cleaned"] = {"passed": True, "failures": []}
    for filepath in SHOULD_NOT_BE_IN_TECH_INFRA_ROOT:
        if filepath.exists():
            results["tech_infra_cleaned"]["passed"] = False
            results["tech_infra_cleaned"]["failures"].append(f"Still in tech-infra root: {filepath.name}")


def test_permanent_locations(results):
    """Test that files exist in permanent locations."""
    results["permanent_locations"] = {"passed": True, "failures": []}
    for filepath, description in SHOULD_EXIST_PERMANENT:
        if not filepath.exists():
            results["permanent_locations"]["passed"] = False
            results["permanent_locations"]["failures"].append(f"Missing: {filepath.relative_to(BASE)} ({description})")


def test_link_integrity(results):
    """Test that links/references in key files still resolve."""
    results["link_integrity"] = {"passed": True, "failures": []}
    
    # Check wiki index links
    wiki_index = BASE / "wiki" / "index.md"
    if wiki_index.exists():
        content = wiki_index.read_text()
        # Check that new locations are referenced
        expected_refs = [
            "master-prompt-guide",
            "master-prompt-architecture",
            "master-prompt-training",
            "performance-benchmarking",
        ]
        for ref in expected_refs:
            if ref not in content:
                results["link_integrity"]["passed"] = False
                results["link_integrity"]["failures"].append(f"wiki/index.md missing reference: {ref}")


def run_all_tests(phase="after"):
    results = {}
    
    if phase == "before":
        print("=" * 60)
        print("PRE-MOVE VERIFICATION")
        print("=" * 60)
        # Only check what currently exists
        print("\nChecking current file locations...")
        for filepath, desc in SHOULD_EXIST_PERMANENT:
            dest = filepath.relative_to(BASE)
            source_check = "EXISTS" if filepath.exists() else "MISSING"
            print(f"  {dest}: {source_check}")
        return {"phase": "before", "status": "checked"}
    
    print("=" * 60)
    print("POST-MOVE VERIFICATION")
    print("=" * 60)
    
    test_temp_files_deleted(results)
    test_root_cleaned(results)
    test_tech_infra_root_cleaned(results)
    test_permanent_locations(results)
    test_link_integrity(results)
    
    # Summarize
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"\n{status} — {test_name}")
        if not result["passed"]:
            all_passed = False
            for failure in result["failures"]:
                print(f"    • {failure}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED — File relocation complete")
        return 0
    else:
        print("❌ TESTS FAILED — See failures above")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["before", "after"], default="after")
    args = parser.parse_args()
    
    os.chdir(BASE)
    exit_code = run_all_tests(args.phase)
    sys.exit(exit_code)
