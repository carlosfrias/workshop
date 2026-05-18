#!/usr/bin/env python3
"""
Step 004: Fix Broken Anchor Links
Fixes broken anchor references across multiple files.
"""

import os

WORKSPACE = "/Users/friasc/Dropbox/ai-trading-workspace"
LOG_PREFIX = "Step 004"

FILES_TO_FIX = [
    ('wiki/index.md', [
        ('(#operational-sessions)', '(#operational-sessions)'),
    ]),
    ('wiki/trading-desk/backlog.md', [
        ('(#integration--chains)', '(#integration-chains)'),
        ('(#documentation--wiki)', '(#documentation-wiki)'),
    ]),
    ('technical-infrastructure/wiki/troubleshooting/node2-troubleshooting-session.md', [
        ('(#issues--resolutions)', '(#issues-resolutions)'),
    ]),
    ('technical-infrastructure/wiki/troubleshooting/network-troubleshooting-guide.md', [
        ('(#2x-decomposed-workflow)', '(#2x-decomposed-workflow)'),
    ]),
    ('technical-infrastructure/wiki/operational/BACKLOG.md', [
        ('(#-high-priority)', '(#🔴-high-priority)'),
        ('(#-medium-priority)', '(#🟡-medium-priority)'),
        ('(#-low-priority)', '(#🟢-low-priority)'),
    ]),
]

def main():
    print(f"{LOG_PREFIX}: Starting...")
    total_fixed = 0
    skipped = 0

    for filepath, replacements in FILES_TO_FIX:
        full_path = f"{WORKSPACE}/{filepath}"
        try:
            with open(full_path, 'r') as f:
                content = f.read()

            file_count = 0
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    file_count += 1
                    print(f"  Fixed in {filepath}: {old} → {new}")

            if file_count > 0:
                with open(full_path, 'w') as f:
                    f.write(content)
                total_fixed += file_count
        except FileNotFoundError:
            print(f"  SKIPPED (not found): {filepath}")
            skipped += 1

    print(f"{LOG_PREFIX}: Complete - {total_fixed} anchor links fixed, {skipped} files not found")

if __name__ == "__main__":
    main()
