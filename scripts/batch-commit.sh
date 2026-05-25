#!/bin/bash
# Batch Commit Script for Nested Git Repos
# Generated: 2026-05-22 08:12
# Usage: ./batch-commit.sh [--dry-run]

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo "=== DRY RUN MODE ==="
fi

WORKSHOP_ROOT="/Users/friasc/Cloud/carlos-desktop/workshop"
cd "$WORKSHOP_ROOT" || exit 1

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

commit_count=0
skip_count=0

# Function to commit a repo
commit_repo() {
    local repo_path="$1"
    local commit_msg="$2"
    
    cd "$WORKSHOP_ROOT/$repo_path" || return 1
    
    # Check if there are staged changes
    if git diff --cached --quiet && git diff --quiet; then
        echo -e "${YELLOW}SKIP${NC}: $repo_path (no changes)"
        ((skip_count++))
        return 0
    fi
    
    if [ "$DRY_RUN" == true ]; then
        echo -e "${YELLOW}WOULD COMMIT${NC}: $repo_path"
        echo "  Message: $commit_msg"
        git status --short
        ((commit_count++))
        return 0
    fi
    
    # Commit
    git commit -m "$commit_msg"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}COMMITTED${NC}: $repo_path"
        ((commit_count++))
    else
        echo -e "${RED}FAILED${NC}: $repo_path"
        return 1
    fi
}

echo "=================================="
echo "Batch Commit - Workshop Repos"
echo "=================================="
echo ""

# Project repos with untracked files
commit_repo "01-Projects/clief" \
    "feat: Initialize CLIEF project structure

- Add AGENTS.md domain routing
- Add FOCUS.md current state tracking
- Add harness/README.md core architecture docs"

commit_repo "01-Projects/doc-standards-enablement" \
    "feat: Add mkdocs export pipeline and validation scripts

- Add export/ mkdocs documentation site (6 guides)
- Add scripts/linter-rules.md for frontmatter validation
- Add scripts/validate-frontmatter.sh automated checker
- Update scaffold-project.sh with latest templates"

commit_repo "01-Projects/his-desk" \
    "feat: Add routing domain structure

- Add routing/ directory with domain routing tables
- Add conventions.md, domains.md, workspace.md
- Update AGENTS.md with routing section references"

commit_repo "01-Projects/nextcloud" \
    "feat: Add routing domain structure

- Add routing/ directory with domain routing tables
- Add domain-routing.md, lab-inventory.md, overview.md
- Update AGENTS.md with routing section references"

commit_repo "01-Projects/pi-cross-node-comms" \
    "feat: Add Docker deployment, systemd services, and test suite

- Add Dockerfile, docker-compose.yml, .dockerignore
- Add ansible/systemd/ agent service templates
- Add server/__tests__/ integration and unit tests
- Add src/skills/pi-cross-node-comms/ decomposed sections
- Add .pi/skills/lab-fleet-deployment/ complete skill docs
- Add bun.lock dependency lockfile
- Update package.json, ansible configs, inventory"

commit_repo "02-Areas/project-blueprint" \
    "feat: Add linear scripts and WORKBENCH template

- Add skills/project-blueprint/linear/ (5 task scripts)
- Add prompts/ linear prompt templates (4 files)
- Add templates/WORKBENCH.md reference implementation
- Update SKILL.md, setup.md, package.json"

commit_repo "02-Areas/Trading/bookkeeping" \
    "feat: Add cost-model, import pipeline, and ledger subdomains

- Add cost-model/AGENTS.md cost tracking domain
- Add import/AGENTS.md + routing/ pipeline docs (5 files)
- Add ledger/AGENTS.md double-entry domain
- Update parent AGENTS.md with subdomain routing"

commit_repo "03-Resources/Infrastructure/technical-infrastructure-legacy" \
    "feat: Add routing domain structure

- Add routing/ directory with 4 routing tables
- Add conventions-and-rules.md, documentation-loading.md
- Add quality-and-readiness.md, routing-tables.md
- Update AGENTS.md with routing references"

# Infrastructure resources (multiple small repos)
echo ""
echo "--- Infrastructure Resources ---"

for repo in "doc-standardizer" "gist-message-protocol" "gist-message-queue" "playbook-executor"; do
    commit_repo "03-Resources/Infrastructure/$repo" \
        "feat: Add decomposed skill sections and playbooks

- $repo: Add MANIFEST.json, sections/, playbooks/"
done

echo ""
echo "=================================="
echo "Summary:"
echo -e "  ${GREEN}Committed${NC}: $commit_count repos"
echo -e "  ${YELLOW}Skipped${NC}: $skip_count repos"
echo "=================================="
