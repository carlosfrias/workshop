#!/bin/bash
# Node 2 Setup - Step 1: Authentication
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step1-auth.sh | bash

echo "=== NODE 2 SETUP: STEP 1 ==="
echo "Installing GitHub CLI..."

if command -v gh &> /dev/null; then
    echo "✓ gh already installed"
else
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>&1
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update -qq
    sudo apt install gh -y -qq
    echo "✓ gh installed"
fi

echo ""
echo "Authenticating with GitHub..."
if gh auth status &> /dev/null 2>&1; then
    echo "✓ Already authenticated"
else
    gh auth login --web
fi

echo ""
echo "=== STEP 1 COMPLETE ==="
echo "Next: Run step 2 (download scripts)"
echo "  curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash"
