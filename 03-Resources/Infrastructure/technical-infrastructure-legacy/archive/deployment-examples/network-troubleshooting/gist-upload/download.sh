#!/bin/bash
# Download and setup network troubleshooting bundle from Gist
# GIST: https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

set -e

echo "========================================"
echo "NETWORK TROUBLESHOOTING BUNDLE DOWNLOAD"
echo "========================================"
echo ""

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

# Create working directory
echo "Creating working directory..."
mkdir -p ~/network-troubleshooting-bundle
cd ~/network-troubleshooting-bundle

# Download scripts
echo "Downloading scripts..."
curl -sL "$GIST_URL/install-ollama.sh" -o install-ollama.sh && echo "  ✓ install-ollama.sh"
curl -sL "$GIST_URL/detect-hardware.sh" -o detect-hardware.sh && echo "  ✓ detect-hardware.sh"
curl -sL "$GIST_URL/benchmark-model.sh" -o benchmark-model.sh && echo "  ✓ benchmark-model.sh"
curl -sL "$GIST_URL/diagnose.sh" -o diagnose.sh && echo "  ✓ diagnose.sh"
curl -sL "$GIST_URL/apply-fix.sh" -o apply-fix.sh && echo "  ✓ apply-fix.sh"
curl -sL "$GIST_URL/verify.sh" -o verify.sh && echo "  ✓ verify.sh"

# Download documentation
echo "Downloading documentation..."
curl -sL "$GIST_URL/README.md" -o README.md && echo "  ✓ README.md"
curl -sL "$GIST_URL/SESSION-RECREATION.md" -o SESSION-RECREATION.md && echo "  ✓ SESSION-RECREATION.md"

# Download agent definitions
echo "Downloading agent definitions..."
curl -sL "$GIST_URL/technical-infrastructure.md" -o technical-infrastructure.md && echo "  ✓ technical-infrastructure.md"
curl -sL "$GIST_URL/verifier.md" -o verifier.md && echo "  ✓ verifier.md"
curl -sL "$GIST_URL/model-router.json" -o model-router.json && echo "  ✓ model-router.json"

# Make scripts executable
echo "Making scripts executable..."
chmod +x *.sh

# Create .pi directory structure
echo "Setting up .pi directory structure..."
mkdir -p .pi/agents
mv technical-infrastructure.md .pi/agents/
mv verifier.md .pi/agents/
mv model-router.json .pi/

echo ""
echo "========================================"
echo "✓ BUNDLE DOWNLOADED SUCCESSFULLY"
echo "========================================"
echo ""
echo "Location: ~/network-troubleshooting-bundle"
echo ""
echo "Contents:"
ls -la
echo ""
ls -la .pi/
echo ""
ls -la .pi/agents/
echo ""
echo "========================================"
echo "NEXT STEPS"
echo "========================================"
echo ""
echo "1. Connect phone tether and verify internet:"
echo "   ping -c 2 8.8.8.8"
echo ""
echo "2. Install pi coding agent:"
echo "   sudo npm install -g @mariozechner/pi-coding-agent"
echo ""
echo "3. Install Ollama:"
echo "   sudo ./install-ollama.sh"
echo ""
echo "4. Start Ollama service:"
echo "   ollama serve &"
echo ""
echo "5. Run hardware detection:"
echo "   ./detect-hardware.sh > /tmp/hardware-report.txt"
echo ""
echo "6. Run model benchmark:"
echo "   ./benchmark-model.sh > /tmp/benchmark-report.txt"
echo ""
echo "7. Paste BOTH reports to cloud agent for diagnosis"
echo ""
echo "========================================"
