#!/usr/bin/env bash
#
# setup-gist-orchestrator.sh — Orchestrator-side Gist Message Protocol setup
#
# PURPOSE:
#   Prepares the Mac orchestrator to dispatch tasks to and collect results from
#   lab nodes via GitHub Gist. Run this once on the orchestrator (your Mac).
#
# WHAT IT DOES:
#   1. Verifies or creates the shared Gist for the message queue
#   2. Prompts for / verifies the GitHub Personal Access Token
#   3. Installs gist-orchestrator.py to a local bin directory
#   4. Adds environment variables to shell profile
#   5. Verifies connectivity to GitHub Gist API
#
# USAGE:
#   bash scripts/setup-gist-orchestrator.sh
#   bash scripts/setup-gist-orchestrator.sh --gist-id 0c517214489cb78c0484ca661f3d8463
#
# ENVIRONMENT (set by this script):
#   GIST_ORCHESTRATOR_GIST_ID — The shared Gist ID used as the message queue
#   GITHUB_TOKEN              — Personal access token with 'gist' scope
#
# FOR THIRD PARTIES:
#   If you are setting up a new cluster, create a new Gist and share the ID
#   with the orchestrator owner. Do not reuse an existing Gist ID.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="${REPO_ROOT}/scripts/gist-orchestrator.py"
GIST_ID="${GIST_ORCHESTRATOR_GIST_ID:-0c517214489cb78c0484ca661f3d8463}"
LOCAL_BIN="${HOME}/.local/bin"

echo "========================================"
echo "Gist Message Protocol — Orchestrator Setup"
echo "========================================"
echo ""

# ── Parse arguments ─────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --gist-id)
            GIST_ID="$2"; shift 2 ;;
        --token)
            GITHUB_TOKEN="$2"; shift 2 ;;
        *)
            echo "Usage: $0 [--gist-id ID] [--token TOKEN]"; exit 1 ;;
    esac
done

# ── Check prerequisites ─────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "✗ python3 required"; exit 1
fi
if ! python3 -c "import urllib.request, json" 2>/dev/null; then
    echo "✗ Python urllib.request / json modules required"; exit 1
fi
if ! command -v gh &> /dev/null; then
    echo "⚠ GitHub CLI (gh) not installed — strongly recommended for Gist management"
    echo "  Install: brew install gh"
fi

# ── GitHub Token prompt ─────────────────────────────────────────────
if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    if gh auth status &>/dev/null; then
        echo "✓ GitHub CLI authenticated — using gh token"
        GITHUB_TOKEN=$(gh auth token)
    else
        echo "GitHub Personal Access Token required."
        echo "  Create one at: https://github.com/settings/tokens/new"
        echo "  Required scope: ✓ gist"
        echo ""
        echo -n "Enter token (or press Enter to skip): "
        read -r GITHUB_TOKEN
    fi
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
    echo "⚠ No token provided — operations requiring Gist writes will fail"
    echo "  You can set GITHUB_TOKEN later in your shell profile"
    GITHUB_TOKEN=""
fi

# ── Verify or create Gist ──────────────────────────────────────────
echo ""
echo "Verifying Gist: ${GIST_ID}..."

gist_check=$(python3 -c "
import urllib.request, json, sys
try:
    req = urllib.request.Request(
        'https://api.github.com/gists/${GIST_ID}',
        headers={'Accept': 'application/vnd.github+json', 'Authorization': 'Bearer ${GITHUB_TOKEN}'}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        print(data.get('html_url', 'unknown'))
except Exception as e:
    print(f'ERROR: {e}', file=sys.stderr)
    sys.exit(1)
" 2>&1)

if [[ $? -eq 0 ]]; then
    echo "✓ Gist accessible: ${gist_check}"
else
    echo "✗ Gist not accessible: ${gist_check}"
    echo ""
    echo -n "Create a new Gist? (y/n): "
    read -r create_gist
    if [[ "$create_gist" == "y" ]]; then
        if command -v gh &> /dev/null; then
            new_gist=$(gh gist create --public --filename "README.md" "Gist Message Queue — ${USER} @ $(date)")
            GIST_ID=$(echo "$new_gist" | sed 's|.*/||')
            echo "✓ Created Gist: ${new_gist}"
            echo "  ID: ${GIST_ID}"
        else
            echo "✗ Cannot create Gist without gh CLI. Install with: brew install gh"
            exit 1
        fi
    else
        echo "Please create a Gist manually and provide its ID: https://gist.github.com"
        exit 1
    fi
fi

# ── Install orchestrator script ──────────────────────────────────────
echo ""
echo "Installing gist-orchestrator.py..."
mkdir -p "${LOCAL_BIN}"

cat > "${LOCAL_BIN}/gist-orchestrator" << 'PYEOF'
#!/usr/bin/env python3
# Wrapper: passes through environment and changes to repo root
import os, sys, subprocess
repo = os.path.expanduser("~/Cloud/workshop")
script = os.path.join(repo, "technical-infrastructure", "scripts", "gist-orchestrator.py")
if not os.path.exists(script):
    print("✗ gist-orchestrator.py not found at", script)
    sys.exit(1)
subprocess.run([sys.executable, script] + sys.argv[1:], cwd=repo)
PYEOF

chmod +x "${LOCAL_BIN}/gist-orchestrator"
echo "✓ Installed to ${LOCAL_BIN}/gist-orchestrator"

# ── Shell profile update ────────────────────────────────────────────
echo ""
echo "Adding environment variables to shell profile..."

SHELL_PROFILE=""
if [[ "$SHELL" == */zsh ]]; then
    SHELL_PROFILE="${HOME}/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    SHELL_PROFILE="${HOME}/.bash_profile"
    [[ ! -f "$SHELL_PROFILE" ]] && SHELL_PROFILE="${HOME}/.bashrc"
fi

if [[ -n "$SHELL_PROFILE" ]]; then
    # Remove old entries
    sed -i.bak '/# Gist Message Protocol/d' "$SHELL_PROFILE"
    sed -i.bak '/export GIST_ORCHESTRATOR_GIST_ID/d' "$SHELL_PROFILE"
    sed -i.bak '/export GITHUB_TOKEN/d' "$SHELL_PROFILE"
    # Add new entries
    cat >> "$SHELL_PROFILE" << EOF

# Gist Message Protocol (added $(date +%Y-%m-%d))
export GIST_ORCHESTRATOR_GIST_ID="${GIST_ID}"
export GITHUB_TOKEN="${GITHUB_TOKEN}"
EOF
    echo "✓ Updated ${SHELL_PROFILE}"
else
    echo "⚠ Could not detect shell profile — add manually:"
    echo "  export GIST_ORCHESTRATOR_GIST_ID=\"${GIST_ID}\""
    echo "  export GITHUB_TOKEN=\"${GITHUB_TOKEN}\""
fi

# ── PATH check ──────────────────────────────────────────────────────
if [[ ":$PATH:" != *":${LOCAL_BIN}:"* ]]; then
    echo ""
    echo "⚠ ${LOCAL_BIN} not in PATH"
    echo "  Add to shell profile: export PATH=\"\${HOME}/.local/bin:\$PATH\""
fi

# ── Quick test ──────────────────────────────────────────────────────
echo ""
echo "Running connectivity test..."
export GIST_ORCHESTRATOR_GIST_ID="${GIST_ID}"
export GITHUB_TOKEN="${GITHUB_TOKEN}"

gist-orchestrator --status 2>/dev/null || python3 "$SCRIPT" --gist-id "$GIST_ID" --token "$GITHUB_TOKEN" --status

# ── Summary ────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Setup Complete"
echo "========================================"
echo ""
echo "Gist ID:        ${GIST_ID}"
echo "Orchestrator:   ${LOCAL_BIN}/gist-orchestrator"
echo "Script:         ${SCRIPT}"
echo ""
echo "Quick commands:"
echo "  gist-orchestrator --status                 # Show queue status"
echo "  gist-orchestrator --submit --node fnet3 --command 'hostname'"
echo "  gist-orchestrator --submit-all --command 'ollama list'"
echo "  gist-orchestrator --collect --since 300"
echo "  gist-orchestrator --watch"
echo ""
echo "To activate environment in a new shell:"
echo "  source ~/.bashrc  # or ~/.zshrc"
echo ""
echo "To deploy workers to lab nodes (when on-premise):"
echo "  cd technical-infrastructure/ansible"
echo "  ansible-playbook -i inventory.yml playbooks/deploy-gist-worker.yml"
echo ""
echo "To deploy the full protocol (orchestrator + workers):"
echo "  ansible-playbook -i inventory.yml playbooks/deploy-gist-message-protocol.yml"
echo ""
