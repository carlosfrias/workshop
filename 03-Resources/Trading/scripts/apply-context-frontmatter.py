#!/usr/bin/env python3
"""
Apply context preservation frontmatter to existing wiki documents.

Usage:
    python scripts/apply-context-frontmatter.py --dry-run wiki/
    python scripts/apply-context-frontmatter.py --apply wiki/

This script:
1. Scans wiki directory for .md files
2. Checks if frontmatter exists
3. If missing, adds template frontmatter with placeholder values
4. If present, checks for required context fields
5. Reports files needing manual review
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime

FRONTMATTER_TEMPLATE = """---
title: "{title}"
document_id: "{doc_id}"
document_type: "{doc_type}"

context:
  created_by: "NEEDS_REVIEW"
  created_for: "NEEDS_REVIEW"
  decision_rationale: "NEEDS_REVIEW"
  alternatives_considered:
    - "NEEDS_REVIEW"
  related_documents: []
  knowledge_level: "detail"
  prerequisites: "NEEDS_REVIEW"

created_date: "{created_date}"
last_updated: "{last_updated}"
version: "1.0"
status: "active"
tags: []
---

"""

def extract_title(filepath):
    """Extract title from first H1 heading or filename."""
    with open(filepath, 'r') as f:
        content = f.read(2000)
    
    # Look for first H1
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Fallback to filename
    return Path(filepath).stem.replace('-', ' ').title()

def infer_document_type(filepath):
    """Infer document type from path or filename."""
    path_str = str(filepath).lower()
    name = Path(filepath).stem.lower()
    
    if 'plan' in path_str or 'plan' in name:
        return 'plan'
    elif 'session' in path_str or 'session' in name:
        return 'session'
    elif 'guide' in path_str or 'guide' in name:
        return 'guide'
    elif 'procedure' in path_str or 'runbook' in name:
        return 'procedure'
    elif 'backlog' in path_str or 'backlog' in name:
        return 'backlog'
    else:
        return 'reference'

def generate_doc_id(filepath, title):
    """Generate a document ID from path and title."""
    # Extract domain from path
    path_parts = str(filepath).split('/')
    domain = 'UNK'
    for part in path_parts:
        if part in ['technical-infrastructure', 'trading-desk', 'bookkeeping', 'operations']:
            domain = part.split('-')[0].upper()[:2]
            break
    
    # Short title
    short_title = ''.join(word[:3] for word in title.split()[:3]).upper()
    
    return f"{domain}-{short_title}"

def has_frontmatter(content):
    """Check if file already has YAML frontmatter."""
    return content.startswith('---')

def process_file(filepath, apply_changes=False):
    """Process a single markdown file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    result = {
        'path': str(filepath),
        'action': 'skip',
        'reason': ''
    }
    
    if has_frontmatter(content):
        # Check if it has context fields
        if 'context:' in content[:2000]:
            result['action'] = 'skip'
            result['reason'] = 'Already has context frontmatter'
        else:
            result['action'] = 'review'
            result['reason'] = 'Has frontmatter but missing context fields'
    else:
        # Generate frontmatter
        title = extract_title(filepath)
        doc_type = infer_document_type(filepath)
        doc_id = generate_doc_id(filepath, title)
        today = datetime.now().strftime('%Y-%m-%d')
        
        frontmatter = FRONTMATTER_TEMPLATE.format(
            title=title,
            doc_id=doc_id,
            doc_type=doc_type,
            created_date=today,
            last_updated=today
        )
        
        result['action'] = 'add'
        result['reason'] = 'Missing frontmatter'
        result['new_content'] = frontmatter + content
        
        if apply_changes:
            with open(filepath, 'w') as f:
                f.write(frontmatter + content)
            result['action'] = 'added'
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Apply context frontmatter to wiki documents')
    parser.add_argument('directory', help='Wiki directory to scan')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry-run)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
    args = parser.parse_args()
    
    wiki_dir = Path(args.directory)
    if not wiki_dir.exists():
        print(f"Error: Directory {wiki_dir} does not exist")
        return
    
    # Find all markdown files
    md_files = list(wiki_dir.rglob('*.md'))
    
    results = {'add': 0, 'review': 0, 'skip': 0, 'added': 0}
    files_to_review = []
    
    print(f"Scanning {len(md_files)} markdown files in {wiki_dir}...")
    print()
    
    for filepath in md_files:
        result = process_file(filepath, apply_changes=args.apply)
        results[result['action']] = results.get(result['action'], 0) + 1
        
        if result['action'] in ['add', 'added']:
            print(f"[{'APPLIED' if result['action'] == 'added' else 'WOULD ADD'}] {filepath}")
        elif result['action'] == 'review':
            files_to_review.append(filepath)
            print(f"[REVIEW NEEDED] {filepath} - {result['reason']}")
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Frontmatter added: {results.get('added', 0)}")
    print(f"  Would add (dry-run): {results.get('add', 0)}")
    print(f"  Need manual review: {results.get('review', 0)}")
    print(f"  Already complete: {results.get('skip', 0)}")
    
    if files_to_review:
        print()
        print("Files needing manual review (has frontmatter, missing context):")
        for f in files_to_review[:20]:  # Show first 20
            print(f"  - {f}")
        if len(files_to_review) > 20:
            print(f"  ... and {len(files_to_review) - 20} more")

if __name__ == '__main__':
    main()
