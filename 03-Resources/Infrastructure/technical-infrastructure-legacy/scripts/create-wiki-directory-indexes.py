#!/usr/bin/env python3
"""
Step 005: Add Missing index.md for Directory Listings
Creates index.md files for directories that need them for VitePress navigation.
"""

import os

WORKSPACE = "/Users/friasc/Cloud/ai-trading-workspace"
LOG_PREFIX = "Step 005"

DIRECTORIES = [
    ('operational/backlog-completed', 'Backlog (Completed)', 'Archived completed backlog items.'),
    ('technical-infrastructure/operational/status', 'Operational Status', 'Node and system status reports.'),
    ('technical-infrastructure/operational/sessions', 'Operational Sessions', 'Session logs and transcripts.'),
    ('technical-infrastructure/operational/planning', 'Planning', 'Planning documents and decomposition plans.'),
]

def main():
    print(f"{LOG_PREFIX}: Starting...")
    
    created = 0
    for dir_path, title, description in DIRECTORIES:
        index_path = f"{WORKSPACE}/wiki/{dir_path}/index.md"
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Create index.md content
        content = f"""# {title}

{description}

## Contents

<!-- AUTO-GENERATED: List files in this directory -->

"""
        
        # Check if file already exists
        if os.path.exists(index_path):
            print(f"  EXISTS: {index_path}")
        else:
            with open(index_path, 'w') as f:
                f.write(content)
            print(f"  CREATED: {index_path}")
            created += 1
    
    print(f"{LOG_PREFIX}: Complete - {created} index.md files created")

if __name__ == "__main__":
    main()
