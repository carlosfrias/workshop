#!/bin/bash
# STEP 1: SETUP (<1 minute)
# Run: bash ./step1-setup.sh

set -e

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

echo "=== STEP 1: SETUP (<1 min) ==="
echo ""

# Set working directory
echo "Setting working directory..."
cd ~/network-troubleshooting-bundle || { echo "ERROR: Directory not found"; exit 1; }
echo "Working in: $(pwd)"
echo ""

# Download scripts (parallel would be faster, but keeping simple)
echo "Downloading scripts..."

for script in step2-diagnostics.sh step3-poll.sh detect-hardware.sh diagnose.sh verify.sh context-health-check.sh; do
    if [ ! -f ./$script ]; then
        echo "  Downloading: $script"
        curl -sL "$GIST_URL/$script" -o ./$script
        chmod +x ./$script 2>/dev/null || true
    else
        echo "  ✓ Already exists: $script"
    fi
done

echo ""

# Download AGENTS.md
if [ ! -f ~/.pi/agent/AGENTS.md ]; then
    echo "Downloading AGENTS.md..."
    curl -sL "$GIST_URL/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md
    cp ./NODE2-AGENTS.md ~/.pi/agent/AGENTS.md
fi

# Initialize status
echo "INITIALIZING" > ./node2-STATUS.md

echo ""
echo "=== STEP 1 COMPLETE ==="
echo "Next: Run step2-diagnostics.sh"
echo ""
