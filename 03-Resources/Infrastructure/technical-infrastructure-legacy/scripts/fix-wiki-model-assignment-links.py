#!/usr/bin/env python3
"""
Step 003: Fix model-assignment-strategy.html Links
Fixes broken decompose-execute-verify-pattern link.
"""

WORKSPACE = "/Users/friasc/Dropbox/ai-trading-workspace"
FILE_PATH = f"{WORKSPACE}/wiki/model-assignment-strategy.md"
LOG_PREFIX = "Step 003"

def main():
    print(f"{LOG_PREFIX}: Starting...")
    
    with open(FILE_PATH, 'r') as f:
        content = f.read()
    
    # Fix decompose-execute-verify-pattern link
    old = 'decompose-execute-verify-pattern'
    new = '/technical-infrastructure/reference/decompose-execute-verify-pattern'
    
    if old in content:
        content = content.replace(old, new)
        print(f"  Fixed: {old} → {new}")
        count = 1
    else:
        print(f"  Not found: {old}")
        count = 0
    
    with open(FILE_PATH, 'w') as f:
        f.write(content)
    
    print(f"{LOG_PREFIX}: Complete - {count} links fixed in wiki/model-assignment-strategy.md")

if __name__ == "__main__":
    main()
