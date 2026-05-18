#!/bin/bash
# ================================================================================
# NETWORK TROUBLESHOOTING - AUTOMATED DEPLOYMENT
# ================================================================================
# Single command deployment for offline node troubleshooting
# 
# Usage: curl -L <GIST_URL>/deploy.sh | bash -s -- --api-key YOUR_OLLAMA_CLOUD_API_KEY
#
# What this does:
#   1. Downloads diagnostic scripts
#   2. Configures pi with local + cloud models
#   3. Configures model router (cloud-first for troubleshooting)
#   4. Tests pi is working
#   5. Prompts you to disconnect tether (CRITICAL STEP)
#   6. Runs diagnostics WITHOUT tether
#   7. Displays output to paste to cloud agent
#
# Gist: https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463
# ================================================================================

set -e

# Parse arguments
API_KEY=""
for arg in "$@"; do
    case $arg in
        --api-key=*) API_KEY="${arg#*=}" ;;
        --api-key) API_KEY="$2"; shift ;;
        *) ;;
    esac
done

echo "========================================"
echo "NETWORK TROUBLESHOOTING DEPLOYMENT"
echo "========================================"
echo ""
echo "Node: $(hostname)"
echo "Date: $(date)"
echo ""

# Validate API key
if [ -z "$API_KEY" ]; then
    echo "✗ ERROR: API key is required"
    echo ""
    echo "Usage:"
    echo "  curl -L <GIST_URL>/deploy.sh | bash -s -- --api-key YOUR_KEY"
    echo ""
    echo "Get your key: https://ollama.com/settings/keys"
    exit 1
fi

echo "✓ API key provided"
echo ""

# Gist base URL
GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

# ================================================================================
# STEP 1: Setup directories
# ================================================================================
echo "## Step 1: Setting up directories..."
mkdir -p ~/.pi/agent/agents
echo "  ✓ Created ~/.pi/agent/agents"
echo ""

# ================================================================================
# STEP 2: Download diagnostic scripts
# ================================================================================
echo "## Step 2: Downloading diagnostic scripts..."
cd ~/network-troubleshooting-bundle 2>/dev/null || mkdir -p ~/network-troubleshooting-bundle && cd ~/network-troubleshooting-bundle

curl -sL "$GIST_URL/install-ollama.sh" -o install-ollama.sh && echo "  ✓ install-ollama.sh"
curl -sL "$GIST_URL/detect-hardware.sh" -o detect-hardware.sh && echo "  ✓ detect-hardware.sh"
curl -sL "$GIST_URL/benchmark-model.sh" -o benchmark-model.sh && echo "  ✓ benchmark-model.sh"
curl -sL "$GIST_URL/diagnose.sh" -o diagnose.sh && echo "  ✓ diagnose.sh"
curl -sL "$GIST_URL/apply-fix.sh" -o apply-fix.sh && echo "  ✓ apply-fix.sh"
curl -sL "$GIST_URL/verify.sh" -o verify.sh && echo "  ✓ verify.sh"
chmod +x *.sh
echo ""

# ================================================================================
# STEP 3: Download agent definitions
# ================================================================================
echo "## Step 3: Downloading agent definitions..."
curl -sL "$GIST_URL/technical-infrastructure.md" -o ~/.pi/agent/agents/technical-infrastructure.md && echo "  ✓ technical-infrastructure.md"
curl -sL "$GIST_URL/verifier.md" -o ~/.pi/agent/agents/verifier.md && echo "  ✓ verifier.md"
echo ""

# ================================================================================
# STEP 4: Create models.json (exact Mac schema)
# ================================================================================
echo "## Step 4: Creating models.json..."
cat > ~/.pi/agent/models.json << MODELS
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "$API_KEY",
      "models": [
        {
          "id": "qwen3.5:4b",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 262144,
          "maxTokens": 16000,
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
        },
        {
          "id": "qwen3:8b",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 40960,
          "maxTokens": 16000,
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
        },
        {
          "id": "qwen3.5:cloud",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 256000,
          "maxTokens": 32000,
          "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
        }
      ]
    }
  }
}
MODELS
echo "  ✓ models.json created"
echo ""
echo "  Models available:"
echo "    - qwen3.5:4b   (local, low capacity)"
echo "    - qwen3:8b     (local, medium capacity)"
echo "    - qwen3.5:cloud (cloud, no local resources)"
echo ""

# ================================================================================
# STEP 5: Create model-router.json (cloud-first for troubleshooting)
# ================================================================================
echo "## Step 5: Creating model-router.json..."
cat > ~/.pi/agent/model-router.json << 'ROUTER'
{
  "enabled": true,
  "defaultProfile": "troubleshooting",
  "debug": false,
  "phaseBias": 0.5,
  "largeContextThreshold": 100000,
  "rules": [
    {
      "matches": ["diagnose", "troubleshoot", "analyze", "root cause", "why", "what"],
      "tier": "high",
      "reason": "Diagnostic analysis needs cloud model"
    },
    {
      "matches": ["fix", "apply", "configure", "install", "restart"],
      "tier": "medium",
      "reason": "Fix application needs reasoning"
    },
    {
      "matches": ["verify", "check", "status", "ping", "test"],
      "tier": "low",
      "reason": "Verification can use local model"
    },
    {
      "matches": ["log", "report", "summary"],
      "tier": "low",
      "reason": "Logging is simple structured task"
    }
  ],
  "profiles": {
    "troubleshooting": {
      "high": {
        "model": "qwen3.5:cloud",
        "thinking": "medium",
        "reason": "Cloud model for complex diagnosis (no local resources)"
      },
      "medium": {
        "model": "qwen3.5:cloud",
        "thinking": "low",
        "reason": "Cloud model for fix planning"
      },
      "low": {
        "model": "qwen3.5:4b",
        "thinking": "off",
        "reason": "Local model for simple verification (safe for low capacity)"
      }
    },
    "general": {
      "high": {
        "model": "qwen3.5:cloud",
        "thinking": "medium"
      },
      "medium": {
        "model": "qwen3:8b",
        "thinking": "low"
      },
      "low": {
        "model": "qwen3.5:4b",
        "thinking": "off"
      }
    }
  },
  "modelAliases": {
    "cloud": "qwen3.5:cloud",
    "local": "qwen3.5:4b",
    "medium": "qwen3:8b"
  }
}
ROUTER
echo "  ✓ model-router.json created"
echo ""
echo "  Routing strategy:"
echo "    - High tier (diagnosis):   qwen3.5:cloud (cloud)"
echo "    - Medium tier (planning):  qwen3.5:cloud (cloud)"
echo "    - Low tier (verification): qwen3.5:4b (local)"
echo ""
echo "  NOTE: Cloud-first for troubleshooting (no local resource usage)"
echo "  NOTE: After hardware assessment, router can be updated with optimal models"
echo ""

# ================================================================================
# STEP 6: Test pi
# ================================================================================
echo "## Step 6: Testing pi..."
echo ""
echo "  Testing local model (qwen3.5:4b)..."
if pi "Hello" --model qwen3.5:4b 2>&1 | head -3; then
    echo "  ✓ Local model working"
else
    echo "  ⚠ Local model test failed - Ollama may not be running"
    echo "  Start Ollama: ollama serve &"
fi
echo ""

echo "  Testing cloud model (qwen3.5:cloud)..."
if pi "Hello" --model qwen3.5:cloud 2>&1 | head -3; then
    echo "  ✓ Cloud model working"
else
    echo "  ⚠ Cloud model test failed - check API key"
fi
echo ""

# ================================================================================
# STEP 7: CRITICAL - Disconnect tether
# ================================================================================
echo "========================================"
echo "⚠ CRITICAL: DISCONNECT TETHER NOW"
echo "========================================"
echo ""
echo "pi is now configured and working."
echo ""
echo "The diagnostics MUST run WITHOUT tether to see the actual"
echo "ethernet problem. If tether is connected, diagnostics will"
echo "show the tether connection and mask the real issue."
echo ""
echo "ACTION REQUIRED:"
echo "  1. Disable USB tethering on your phone"
echo "  2. Unplug the USB cable"
echo "  3. Wait 5 seconds for routes to clear"
echo ""
read -p "Press ENTER after you've disconnected the tether..."
echo ""

# ================================================================================
# STEP 8: Verify tether is disconnected
# ================================================================================
echo "## Verifying tether is disconnected..."
echo ""

# Check for USB ethernet interfaces (common tether pattern)
if ip -br addr show | grep -q "enx"; then
    echo "  ⚠ WARNING: USB ethernet interface detected"
    echo ""
    echo "  Tether may still be active. Please ensure:"
    echo "    - USB tethering is disabled on phone"
    echo "    - USB cable is unplugged"
    echo ""
    read -p "Press ENTER to continue anyway, or Ctrl+C to abort and disconnect..."
else
    echo "  ✓ No USB ethernet interfaces detected"
fi

# Show current interfaces
echo ""
echo "  Current network interfaces:"
ip -br addr show | grep -v "lo" || echo "    (none)"
echo ""

# ================================================================================
# STEP 9: Run diagnostics
# ================================================================================
echo "========================================"
echo "RUNNING DIAGNOSTICS (No Tether)"
echo "========================================"
echo ""

cd ~/network-troubleshooting-bundle

echo "Hardware detection..."
./detect-hardware.sh > /tmp/hardware-report.txt
echo "  ✓ Saved to /tmp/hardware-report.txt"
echo ""

echo "Running deep network diagnostics..."
echo ""
echo "========================================"
echo "DIAGNOSTIC OUTPUT (Copy everything below)"
echo "========================================"
echo ""

echo "=== GATEWAY PING ==="
ping -c 3 192.168.0.1 2>&1 || echo "  Gateway unreachable"
echo ""

echo "=== ARP TABLE ==="
arp -n | grep 192.168.0.1 2>/dev/null || echo "  No ARP entry for gateway"
ip neigh show 2>/dev/null || echo "  ip neigh failed"
echo ""

echo "=== LINK STATUS ==="
sudo ethtool enp7s0 2>/dev/null | grep -E "Link detected|Speed|Duplex" || echo "  ethtool failed"
echo ""

echo "=== INTERFACE STATE ==="
ip link show enp7s0 2>/dev/null || echo "  ip link failed"
echo ""

echo "=== IP CONFLICT CHECK ==="
arping -c 3 -I enp7s0 192.168.0.254 2>/dev/null || echo "  arping failed"
echo ""

echo "=== ROUTING TABLE ==="
ip route show 2>/dev/null || echo "  ip route failed"
echo ""

echo "=== DNS CONFIGURATION ==="
cat /etc/resolv.conf 2>/dev/null || echo "  Cannot read resolv.conf"
echo ""

echo "=== CONNECTIVITY TEST ==="
if ping -c 2 -W 2 8.8.8.8 2>/dev/null; then
    echo "✓ Can reach 8.8.8.8"
else
    echo "✗ Cannot reach 8.8.8.8"
fi
echo ""

if ping -c 2 -W 2 google.com 2>/dev/null; then
    echo "✓ DNS resolution works"
else
    echo "✗ DNS resolution failed"
fi
echo ""

# ================================================================================
# STEP 10: Next steps
# ================================================================================
echo "========================================"
echo "DIAGNOSTICS COMPLETE"
echo "========================================"
echo ""
echo "NEXT STEP:"
echo ""
echo "1. Copy ALL output above (from === GATEWAY PING === onwards)"
echo ""
echo "2. Paste it to the cloud agent session on your Mac"
echo ""
echo "3. The cloud agent will analyze and provide specific fix commands"
echo ""
echo "4. Run the fix commands on this node"
echo ""
echo "5. Run verification: ~/network-troubleshooting-bundle/verify.sh"
echo ""
echo "6. Reconnect tether briefly for final verification"
echo ""
echo "========================================"
echo "MODEL ROUTING INFO"
echo "========================================"
echo ""
echo "Model router is configured for cloud-first troubleshooting:"
echo ""
echo "  Task Type          | Model          | Tier"
echo "  -------------------|----------------|-------"
echo "  Diagnosis/Analysis | qwen3.5:cloud  | High"
echo "  Fix Planning       | qwen3.5:cloud  | Medium"
echo "  Verification       | qwen3.5:4b     | Low"
echo ""
echo "This minimizes local resource usage during troubleshooting."
echo "After hardware assessment, the router can be optimized."
echo ""
