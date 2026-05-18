#!/bin/bash
# Download and extract network troubleshooting decomposition prompts
# Run this on fnet2 to get the prompt files

set -e

echo "=== Network Troubleshooting Decomposition - Download Script ==="
echo ""

# Define the Gist URL (29-task fine-grained decomposition for qwen3:4b)
GIST_URL="https://gist.githubusercontent.com/carlosfrias/81a73c4d4b42cae8fadc46d36a73f75f/raw/network-troubleshooting-decomposition.tar.gz.b64"

# Define target directory (relative to home)
TARGET_DIR="$HOME/technical-infrastructure/wiki/decomposition-examples/network-troubleshooting"

echo "Step 1: Downloading base64-encoded archive..."
curl -L "$GIST_URL" -o /tmp/decomposition.b64

echo "Step 2: Decoding and extracting to $HOME/..."
base64 -d /tmp/decomposition.b64 | tar -xzf - -C "$HOME"

echo "Step 3: Verifying extraction..."
if [ -d "$TARGET_DIR" ]; then
    echo ""
    echo "✓ Success! Files extracted to:"
    echo "  $TARGET_DIR"
    echo ""
    echo "Files:"
    ls -1 "$TARGET_DIR"
    echo ""
    echo "Total files: $(ls -1 "$TARGET_DIR" | wc -l)"
else
    echo "✗ Error: Directory not found at $TARGET_DIR"
    exit 1
fi

# Cleanup
rm -f /tmp/decomposition.b64

echo ""
echo "=== Done! ==="
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. Start with: cat 00-decomposition-plan.md"
echo "  3. Examine individual prompts: cat 02-prompt-ping-gateway.md"
echo ""
