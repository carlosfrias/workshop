#!/usr/bin/env python3
"""
Step 001: Fix WIKI.html Home Page Table Links
Fixes broken flat-path links in wiki/index.md technical infrastructure tables.
Updated for flat directory structure (post-merge).
"""

import os

WORKSPACE = "/Users/friasc/Dropbox/ai-trading-workspace"
FILE_PATH = f"{WORKSPACE}/wiki/index.md"
LOG_PREFIX = "Step 001"

def main():
    print(f"{LOG_PREFIX}: Starting...")
    
    if not os.path.isfile(FILE_PATH):
        print(f"  ERROR: {FILE_PATH} not found")
        return 1
    
    with open(FILE_PATH, 'r') as f:
        content = f.read()
    
    # Fix: remove double-nested /technical-infrastructure/technical-infrastructure/
    # This was a pre-existing bug from the nested directory days
    count = 0
    if '/technical-infrastructure/technical-infrastructure/' in content:
        content = content.replace('/technical-infrastructure/technical-infrastructure/', '/technical-infrastructure/')
        count += content.count('/technical-infrastructure/technical-infrastructure/')
        print(f"  Fixed: {count} double-nested paths")
    
    # Fix remaining flat-path links → nested paths (for files that DO exist in wiki tree)
    replacements = [
        ('/technical-infrastructure/model-routing-guide', '/technical-infrastructure/reference/model-routing-guide'),
        ('/technical-infrastructure/node-capacity-map', '/technical-infrastructure/reference/node-capacity-map'),
        ('/technical-infrastructure/ansible-playbook-index', '/technical-infrastructure/reference/ansible-playbook-index'),
        ('/technical-infrastructure/multi-node-setup-2026-04-26', '/technical-infrastructure/guides/multi-node-setup-2026-04-26'),
        ('/technical-infrastructure/network-troubleshooting-guide', '/technical-infrastructure/troubleshooting/network-troubleshooting-guide'),
        ('/technical-infrastructure/ollama-setup', '/technical-infrastructure/guides/ollama-setup'),
        ('/technical-infrastructure/wireguard-lab-vpn', '/technical-infrastructure/guides/wireguard-lab-vpn'),
        ('/technical-infrastructure/pi-intercom-setup', '/technical-infrastructure/guides/pi-intercom-setup'),
        ('/technical-infrastructure/decomposition-examples/systemd-mount-lock', '/technical-infrastructure/decomposition-examples/systemd-mount-lock/00-decomposition-plan'),
    ]
    
    fixed = 0
    for old, new in replacements:
        if old in content and old + '/' not in content.replace(new, ''):  # avoid double-fixing
            # Only replace exact match, not if already correctly pathed
            content = content.replace(old, new)
            fixed += 1
            print(f"  Fixed: {old} → {new}")
    
    with open(FILE_PATH, 'w') as f:
        f.write(content)
    
    print(f"{LOG_PREFIX}: Complete - {count} double-nested + {fixed} flat links fixed in wiki/index.md")
    return 0

if __name__ == "__main__":
    exit(main())
