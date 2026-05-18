#!/bin/bash
# install-ollama.sh - Install Ollama on Ubuntu/Debian systems
# Compatible with Ubuntu 20.04, 22.04, 24.04, 26.04

set -e

echo "=== Ollama Installation Script ==="
echo "Detected OS: $(lsb_release -ds 2>/dev/null || cat /etc/*release 2>/dev/null | head -1)"
echo ""

# Check if already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
    ollama --version
    echo ""
    echo "To update Ollama, run: ollama serve & && curl -fsSL https://ollama.com/install.sh | sh"
    exit 0
fi

# Install curl if not present
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    apt-get update
    apt-get install -y curl
fi

# Download and run Ollama installer
echo "Downloading Ollama installer..."
curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh

echo "Running Ollama installer..."
chmod +x /tmp/ollama-install.sh
sh /tmp/ollama-install.sh

# Verify installation
echo ""
echo "=== Installation Complete ==="
if command -v ollama &> /dev/null; then
    echo "✓ Ollama installed successfully"
    ollama --version
    echo ""
    echo "To start Ollama service:"
    echo "  ollama serve &"
    echo ""
    echo "Or as a systemd service (if available):"
    echo "  sudo systemctl start ollama"
else
    echo "✗ Installation may have failed. Please check for errors above."
    exit 1
fi
