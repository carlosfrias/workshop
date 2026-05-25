#!/usr/bin/env python3
"""
Step 002: Fix index.html / README.html Broken Links
Fixes broken paths in wiki/README.md root files.
"""

WORKSPACE = "/Users/friasc/Cloud/ai-trading-workspace"
FILE_PATH = f"{WORKSPACE}/wiki/README.md"
LOG_PREFIX = "Step 002"

def main():
    print(f"{LOG_PREFIX}: Starting...")
    
    with open(FILE_PATH, 'r') as f:
        content = f.read()
    
    # Fix technical-infrastructure paths
    replacements = [
        ('technical-infrastructure/multi-node-setup-2026-04-26', '/technical-infrastructure/guides/multi-node-setup-2026-04-26'),
        ('technical-infrastructure/designs/trading-lab-architecture/WORK-BACKLOG', '/technical-infrastructure/designs/trading-lab-architecture/work-backlog'),
    ]
    
    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
            print(f"  Fixed: {old} → {new}")
    
    with open(FILE_PATH, 'w') as f:
        f.write(content)
    
    print(f"{LOG_PREFIX}: Complete - {count} links fixed in wiki/README.md")

if __name__ == "__main__":
    main()
