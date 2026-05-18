#!/bin/bash
# Node 2 Complete Setup - Single Command
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/setup-node2.sh | bash
#
# This script:
#   1. Installs GitHub CLI (gh)
#   2. Authenticates with GitHub
#   3. Downloads communication script
#   4. Runs ethernet fix
#   5. Sends diagnostics to cloud agent automatically

set -e

echo "========================================"
echo "NODE 2 COMPLETE SETUP"
echo "========================================"
echo ""
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

# Step 1: Install GitHub CLI
echo "## Step 1: Installing GitHub CLI..."
if command -v gh &> /dev/null; then
    echo "  ✓ gh already installed"
else
    echo "  Installing gh..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
    echo "  ✓ gh installed"
fi
echo ""

# Step 2: Authenticate
echo "## Step 2: Authenticating with GitHub..."
if gh auth status &> /dev/null 2>&1; then
    echo "  ✓ Already authenticated"
else
    echo ""
    echo "  Opening browser for authentication..."
    echo "  Follow the prompts to complete login"
    echo ""
    gh auth login --web
    echo ""
    if gh auth status &> /dev/null 2>&1; then
        echo "  ✓ Authentication successful"
    else
        echo "  ✗ Authentication failed"
        echo "  Please run: gh auth login"
        exit 1
    fi
fi
echo ""

# Step 3: Download communication script
echo "## Step 3: Setting up Gist communication..."
GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
curl -sL "$GIST_URL/gist-comm.sh" -o ~/gist-comm.sh
chmod +x ~/gist-comm.sh
echo "  ✓ gist-comm.sh downloaded"
echo ""

# Step 4: Download and run ethernet fix
echo "## Step 4: Running ethernet fix..."
curl -sL "$GIST_URL/fix-node2.sh" -o ~/fix-node2.sh
chmod +x ~/fix-node2.sh
echo "  ✓ fix-node2.sh downloaded"
echo ""
echo "  Executing fix..."
echo ""
~/fix-node2.sh
echo ""

# Step 5: Send diagnostics to cloud
echo "## Step 5: Sending diagnostics to cloud agent..."
echo ""

# Collect diagnostic files
DIAG_FILES=""
if [ -f /tmp/hardware-report.txt ]; then
    DIAG_FILES="$DIAG_FILES /tmp/hardware-report.txt"
fi
if [ -f /tmp/network-diagnosis-*.log ]; then
    DIAG_FILES="$DIAG_FILES /tmp/network-diagnosis-"*.log
fi

if [ -n "$DIAG_FILES" ]; then
    # Concatenate all diagnostics into one file
    cat $DIAG_FILES > /tmp/node2-diagnostic.txt
    
    # Post to Gist
    if gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-diagnostic.txt 2>/dev/null; then
        echo "  ✓ Diagnostics posted to Gist"
        echo ""
        echo "  Cloud agent can now review at:"
        echo "  https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463"
    else
        echo "  ⚠ Failed to post to Gist"
        echo "  Showing output for manual copy:"
        echo ""
        cat /tmp/node2-diagnostic.txt
    fi
else
    echo "  ⚠ No diagnostic files found"
    echo "  Run: ~/fix-node2.sh first"
fi
echo ""

# Step 6: Check for fix commands from cloud
echo "## Step 6: Checking for fix commands from cloud..."
echo ""
echo "  Waiting for cloud agent to review diagnostics..."
echo "  This may take a few moments..."
echo ""

# Poll for fix commands (max 5 minutes)
for i in {1..30}; do
    if curl -sL "$GIST_URL/node2-fix-commands.sh" 2>/dev/null | grep -q "^#"; then
        echo "  ✓ Fix commands received from cloud!"
        echo ""
        echo "  Downloading and executing..."
        curl -sL "$GIST_URL/node2-fix-commands.sh" -o /tmp/node2-fix-commands.sh
        chmod +x /tmp/node2-fix-commands.sh
        bash /tmp/node2-fix-commands.sh
        
        # Send results back
        echo ""
        echo "  Sending results to cloud..."
        echo "Fix executed at $(date)" > /tmp/node2-results.txt
        echo "Exit code: $?" >> /tmp/node2-results.txt
        gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-results.txt 2>/dev/null && echo "  ✓ Results posted"
        break
    else
        echo -ne "  Waiting... $i/30\r"
        sleep 10
    fi
done
echo ""

# Summary
echo "========================================"
echo "SETUP COMPLETE"
echo "========================================"
echo ""
echo "Gist communication:"
echo "  https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463"
echo ""
echo "Commands:"
echo "  ~/gist-comm.sh send diagnostic <file>  - Send to cloud"
echo "  ~/gist-comm.sh recv fix-commands       - Get commands from cloud"
echo "  ~/gist-comm.sh status                  - Check status"
echo ""
echo "Next:"
echo "  1. Cloud agent will review diagnostics"
echo "  2. Fix commands will auto-execute if posted"
echo "  3. Or run: ~/gist-comm.sh recv fix-commands"
echo ""
