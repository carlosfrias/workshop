#!/bin/bash
# Node 2 Setup - Step 2: Download Scripts
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash

echo "=== NODE 2 SETUP: STEP 2 ==="
echo "Downloading scripts..."

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

# Download core scripts
for script in gist-comm.sh manage-tether.sh; do
    echo -n "  Downloading $script... "
    curl -sL "$GIST_URL/$script" -o ~/$script
    chmod +x ~/$script
    echo "✓"
done

# Download diagnostic scripts
mkdir -p ~/network-troubleshooting-bundle
cd ~/network-troubleshooting-bundle

for script in detect-hardware.sh diagnose.sh verify.sh; do
    echo -n "  Downloading $script... "
    curl -sL "$GIST_URL/$script" -o $script
    chmod +x $script
    echo "✓"
done

echo ""
echo "=== STEP 2 COMPLETE ==="
echo ""
echo "Scripts downloaded:"
ls -1 ~/gist-comm.sh ~/manage-tether.sh ~/network-troubleshooting-bundle/*.sh 2>/dev/null
echo ""
echo "Next: Run Step 3 (diagnostics)"
echo "  curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step3-diagnose.sh | bash"
