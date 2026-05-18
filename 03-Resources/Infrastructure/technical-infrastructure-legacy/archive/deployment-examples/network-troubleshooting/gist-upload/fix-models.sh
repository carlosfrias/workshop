#!/bin/bash
# Fix models.json configuration
# REPLICATES EXACT SCHEMA FROM WORKING MAC CONFIGURATION
# NO providers.json - all config in models.json
# CRITICAL: Run this on the TARGET NODE (fnet2, fnet6, or fnet7)

set -e

HOSTNAME=$(hostname)

echo "========================================"
echo "PI MODEL CONFIGURATION SETUP"
echo "========================================"
echo ""
echo "Current hostname: $HOSTNAME"
echo ""

# Verify OLLAMA_CLOUD_API_KEY is set
if [ -z "$OLLAMA_CLOUD_API_KEY" ]; then
    echo "✗ ERROR: OLLAMA_CLOUD_API_KEY environment variable is not set"
    echo ""
    echo "Set it first:"
    echo "  export OLLAMA_CLOUD_API_KEY=your_actual_key"
    echo ""
    exit 1
fi

echo "✓ OLLAMA_CLOUD_API_KEY is set"
echo ""

# Verify this is NOT the Mac orchestrator
if [[ "$HOSTNAME" == *"Frias"* ]] || [[ "$HOSTNAME" == *"frias"* ]]; then
    echo "⚠ WARNING: This appears to be your Mac orchestrator!"
    echo ""
    read -p "Continue anyway? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "Config location: ~/.pi/agent/"
echo ""

# Ensure directory exists
mkdir -p ~/.pi/agent/agents

# Step 1: Clean up old files (including providers.json which doesn't exist on Mac)
echo "## Step 1: Cleaning up..."
rm -f ~/.pi/models.json ~/.pi/providers.json ~/.pi/model-router.json 2>/dev/null || true
echo "  ✓ Removed any files in wrong location"
echo ""

# Step 2: Backup existing configs
echo "## Step 2: Backing up existing configs..."
if [ -f ~/.pi/agent/models.json ]; then
    cp ~/.pi/agent/models.json ~/.pi/agent/models.json.backup.$(date +%Y%m%d%H%M)
    echo "  ✓ Backed up models.json"
fi
if [ -f ~/.pi/agent/providers.json ]; then
    rm -f ~/.pi/agent/providers.json
    echo "  ✓ Removed providers.json (not used - config is in models.json)"
fi
echo ""

# Step 3: Create models.json with EXACT Mac schema
echo "## Step 3: Creating models.json..."
cat > ~/.pi/agent/models.json << MODELS
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "$OLLAMA_CLOUD_API_KEY",
      "models": [
        {
          "id": "qwen3.5:4b",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 262144,
          "maxTokens": 16000,
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          }
        },
        {
          "id": "qwen3:8b",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 40960,
          "maxTokens": 16000,
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          }
        },
        {
          "id": "qwen3.5:cloud",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 256000,
          "maxTokens": 32000,
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          }
        }
      ]
    }
  }
}
MODELS
echo "  ✓ models.json created"
echo ""
echo "  NOTE: No providers.json - all config in models.json (like your Mac)"
echo ""

# Step 4: Verify
echo "========================================"
echo "CONFIGURATION COMPLETE"
echo "========================================"
echo ""
ls -la ~/.pi/agent/models.json
echo ""

# Step 5: Test
echo "========================================"
echo "TESTING PI"
echo "========================================"
echo ""
pi models list 2>&1 | head -20
echo ""
pi "Hello" --model qwen3.5:4b 2>&1 | head -5 || echo "⚠ Local model test failed"
echo ""
pi "Hello" --model qwen3.5:cloud 2>&1 | head -5 || echo "⚠ Cloud model test failed"
echo ""
echo "========================================"
echo "SUCCESS"
echo "========================================"
