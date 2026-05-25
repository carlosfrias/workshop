# Network Troubleshooting Deployment - Node Setup Script

**For:** Nodes 2, 6, 7 (Offline Ubuntu machines)  
**Created:** 2026-04-25  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Pattern:** Decompose → Execute → Verify (Cloud-Assisted)

---

## Quick Start (Recommended)

**One-line download and setup:**

```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/download.sh | bash
```

This will:
1. Download all scripts and documentation to `~/network-troubleshooting-bundle`
2. Make scripts executable
3. Set up `.pi` directory structure

Then follow the setup steps below.

---

## Full Setup Script (Copy-Paste)

```bash
#!/bin/bash
# Network Troubleshooting Node Setup
# Run this script on each offline node (2, 6, 7)

set -e

echo "========================================"
echo "NETWORK TROUBLESHOOTING NODE SETUP"
echo "========================================"
echo ""
echo "Node: $(hostname)"
echo "Date: $(date)"
echo "OS: $(lsb_release -ds 2>/dev/null || cat /etc/*release 2>/dev/null | head -1)"
echo ""

# Step 1: Download bundle
echo "## Step 1: Downloading deployment bundle..."
cd ~
mkdir -p network-troubleshooting-bundle
cd network-troubleshooting-bundle

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

curl -L "$GIST_URL/install-ollama.sh" -o install-ollama.sh
curl -L "$GIST_URL/detect-hardware.sh" -o detect-hardware.sh
curl -L "$GIST_URL/benchmark-model.sh" -o benchmark-model.sh
curl -L "$GIST_URL/diagnose.sh" -o diagnose.sh
curl -L "$GIST_URL/apply-fix.sh" -o apply-fix.sh
curl -L "$GIST_URL/verify.sh" -o verify.sh
curl -L "$GIST_URL/README.md" -o README.md
curl -L "$GIST_URL/technical-infrastructure.md" -o technical-infrastructure.md
curl -L "$GIST_URL/verifier.md" -o verifier.md
curl -L "$GIST_URL/model-router.json" -o model-router.json

chmod +x *.sh

mkdir -p .pi/agents
mv technical-infrastructure.md .pi/agents/
mv verifier.md .pi/agents/
mv model-router.json .pi/

echo "✓ Bundle downloaded to ~/network-troubleshooting-bundle"
echo ""

# Step 2: Install pi
echo "## Step 2: Installing pi coding agent..."
if ! command -v pi &> /dev/null; then
    sudo npm install -g @mariozechner/pi-coding-agent
    echo "✓ pi installed"
else
    echo "✓ pi already installed"
    pi --version
fi
echo ""

# Step 3: Install Ollama
echo "## Step 3: Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    sudo ./install-ollama.sh
    echo "✓ Ollama installed"
else
    echo "✓ Ollama already installed"
    ollama --version
fi
echo ""

# Step 4: Start Ollama
echo "## Step 4: Starting Ollama service..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    ollama serve &
    sleep 3
    echo "✓ Ollama service started"
else
    echo "✓ Ollama service already running"
fi
echo ""

# Step 5: Verify connectivity
echo "## Step 5: Verifying internet connectivity..."
if ping -c 2 -W 2 8.8.8.8 &> /dev/null; then
    echo "✓ Internet connectivity confirmed"
else
    echo "✗ WARNING: Cannot reach 8.8.8.8"
    echo "Check phone tether connection and try again"
    exit 1
fi
echo ""

# Step 6: Hardware detection
echo "## Step 6: Running hardware detection..."
./detect-hardware.sh > /tmp/hardware-report.txt
echo "✓ Hardware report saved to /tmp/hardware-report.txt"
echo ""
echo "========================================"
echo "HARDWARE REPORT (Preview)"
echo "========================================"
head -30 /tmp/hardware-report.txt
echo "..."
echo "(Full report: /tmp/hardware-report.txt)"
echo ""

# Step 7: Model benchmark
echo "## Step 7: Running model benchmark..."
./benchmark-model.sh > /tmp/benchmark-report.txt
echo "✓ Benchmark report saved to /tmp/benchmark-report.txt"
echo ""
echo "========================================"
echo "BENCHMARK REPORT (Preview)"
echo "========================================"
head -30 /tmp/benchmark-report.txt
echo "..."
echo "(Full report: /tmp/benchmark-report.txt)"
echo ""

# Final instructions
echo "========================================"
echo "SETUP COMPLETE - NEXT STEPS"
echo "========================================"
echo ""
echo "1. Copy the ENTIRE contents of /tmp/hardware-report.txt"
echo "   and paste it to the cloud agent for diagnosis."
echo ""
echo "2. Copy the ENTIRE contents of /tmp/benchmark-report.txt"
echo "   and paste it to the cloud agent for model selection."
echo ""
echo "3. Follow the cloud agent's instructions for:"
echo "   - Recommended Ollama model"
echo "   - Required driver packages"
echo "   - Decomposition plan"
echo ""
echo "4. After cloud agent confirms setup:"
echo "   cp -r ~/network-troubleshooting-bundle/.pi ~/.pi"
echo ""
echo "5. Disconnect tether and run offline diagnostics."
echo ""
echo "========================================"
```

---

## After Running Setup Script

### On Cloud Agent (This Session)

Paste the following to the cloud agent:

```
## Node Setup Complete

**Node:** [Node 2 / Node 6 / Node 7]

### Hardware Report
[Paste entire contents of /tmp/hardware-report.txt]

### Benchmark Report
[Paste entire contents of /tmp/benchmark-report.txt]

Please provide:
1. Recommended Ollama model for this node's capacity
2. Driver diagnosis and required packages
3. Decomposition plan for network troubleshooting
```

### On Target Node (After Cloud Agent Response)

```bash
# Deploy agents (as instructed by cloud agent)
cp -r ~/network-troubleshooting-bundle/.pi ~/.pi

# Download recommended model (as instructed by cloud agent)
ollama pull <recommended-model>

# Disconnect tether
# Disable phone tethering

# Run diagnostics (offline)
~/network-troubleshooting-bundle/scripts/diagnose.sh

# Apply fixes (as instructed by cloud agent)
~/network-troubleshooting-bundle/scripts/apply-fix.sh <fix-number> [options]

# Verify
~/network-troubleshooting-bundle/scripts/verify.sh

# Check status
cat /tmp/node-ready.txt

# Expected output: COMPLETE
```

### Final Verification (Reconnect Tether)

```bash
# Reconnect tether
# Paste verification log to cloud agent:
cat /tmp/network-verify-*.log

# Wait for cloud agent confirmation
# If COMPLETE, node is ready
# If not, follow cloud agent's iteration instructions
```

---

## Node-Specific Notes

### Node 2 (Ubuntu 26.04, Unknown NIC)
- Likely Realtek NIC (same OS as Node 1 which had r8169 issue)
- Watch for `r8169` driver in hardware report
- If confirmed, cloud agent will recommend `r8168-dkms` installation

### Node 6 (Intel NUC, 20.04/22.04)
- Likely Intel NIC (e1000e, igb, or igc driver)
- In-kernel drivers should work; issue is likely configuration
- Cloud agent will check NetworkManager config, DHCP, DNS

### Node 7 (Intel NUC, 20.04/22.04)
- Same as Node 6
- May have different Intel NIC variant

---

## Troubleshooting Setup Issues

### npm/pi Installation Fails
```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Retry pi installation
sudo npm install -g @mariozechner/pi-coding-agent
```

### Ollama Installation Fails
```bash
# Check if already installed
which ollama

# If installed but not working
sudo systemctl restart ollama
ollama list
```

### Bundle Download Fails
```bash
# Alternative: Copy from USB drive
# On orchestrator (Mac):
#   tar -czvf /tmp/nt-bundle.tar.gz -C ~/Cloud/workshop/technical-infrastructure/deployment-bundles/network-troubleshooting .
# Copy to USB, then to node:
#   tar -xzf /media/usb/nt-bundle.tar.gz -C ~
```

---

## Estimated Time Per Node

| Phase | Duration | Tether Required |
|-------|----------|-----------------|
| Setup script | 8-12 min | ✅ Yes |
| Cloud diagnosis | 2-3 min | ✅ Yes |
| Model download | 2-5 min | ✅ Yes |
| Offline work | 30-45 min | ❌ No |
| Verification | 1-2 min | ✅ Yes |
| **Total Tether Time** | **~15 min** | |

---

## Success Criteria

- [ ] Hardware report generated and reviewed by cloud agent
- [ ] Benchmark completed and model selected
- [ ] Agents deployed to `~/.pi`
- [ ] Diagnostics run successfully
- [ ] Fixes applied per cloud agent plan
- [ ] Verification passes all tests
- [ ] `/tmp/node-ready.txt` contains: `COMPLETE`

---

**Questions?** Keep tether connected and paste error messages to cloud agent.
