#!/bin/bash
#
# wiki-auto-commit.sh
# Stages and commits any new wiki/lab-specs artifacts collected from nodes.
# Run after task-collect-artifacts.sh.
#
# Usage: ./wiki-auto-commit.sh [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
DRY_RUN=false

if [ "${1:-}" == "--dry-run" ]; then
    DRY_RUN=true
fi

cd "$REPO_DIR"

# Find new or modified files in wiki/ and lab-specs/
new_files=$(git status --short | awk '
    $1 ~ /^\?\?$/ && $2 ~ /technical-infrastructure\/(wiki|lab-specs)\// { print $2 }
    $1 ~ /^ M$/ && $2 ~ /technical-infrastructure\/(wiki|lab-specs)\// { print $2 }
')

if [ -z "$new_files" ]; then
    echo "No new or modified wiki artifacts to commit."
    exit 0
fi

echo "=== Files to commit ==="
echo "$new_files"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "(dry-run: not committing)"
    exit 0
fi

# Stage files
echo "$new_files" | while IFS= read -r f; do
    git add "$f"
done

# Generate commit message
cat > "/tmp/wiki-commit-msg.txt" <<<EOF
Auto-collect artifacts from lab nodes
EOF

# Add file list
(echo ""; echo "Files:"; echo "$new_files") >> "/tmp/wiki-commit-msg.txt"

echo "=== Committing ==="
git commit -F "/tmp/wiki-commit-msg.txt" && git push origin main

echo ""
echo "=== Done ==="
git log -1 --oneline
