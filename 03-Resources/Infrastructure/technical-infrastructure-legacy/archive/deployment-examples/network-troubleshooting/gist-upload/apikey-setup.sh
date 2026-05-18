#!/bin/bash
# API Key Setup for Ollama Cloud
# Run this script to configure pi for cloud model access

set -e

echo "========================================"
echo "OLLAMA CLOUD API KEY SETUP"
echo "========================================"
echo ""

# Create providers.json
echo "Creating providers.json for Ollama Cloud..."
mkdir -p ~/.pi

cat > ~/.pi/providers.json << 'PROVIDERS'
{
  "ollama-cloud": {
    "apiKey": "YOUR_OLLAMA_CLOUD_API_KEY",
    "baseUrl": "https://api.ollama.cloud"
  },
  "ollama": {
    "baseUrl": "http://localhost:11434"
  }
}
PROVIDERS

# Update models.json to match existing format but with ollama-cloud
echo "Creating models.json..."
cat > ~/.pi/models.json << 'MODELS'
{
  "providers": {
    "cloud": "ollama-cloud",
    "local": "ollama"
  },
  "models": {
    "cloud": {
      "provider": "ollama-cloud",
      "model": "qwen3.5:cloud"
    },
    "local": {
      "provider": "ollama",
      "model": "qwen3.5:4b"
    }
  },
  "default": "local"
}
MODELS

echo ""
echo "✓ Configuration files created:"
echo "  - ~/.pi/providers.json"
echo "  - ~/.pi/models.json"
echo ""
echo "========================================"
echo "NEXT STEP: Add Your Ollama Cloud API Key"
echo "========================================"
echo ""
echo "1. Get your Ollama Cloud API key:"
echo "   https://ollama.com/settings/keys"
echo ""
echo "2. Edit providers.json:"
echo "   nano ~/.pi/providers.json"
echo ""
echo "3. Replace YOUR_OLLAMA_CLOUD_API_KEY"
echo "   with your actual API key"
echo ""
echo "4. Test configuration:"
echo "   pi models list"
echo "   pi \"Hello test\" --model qwen3.5:cloud"
echo ""
echo "========================================"
