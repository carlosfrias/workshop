#!/bin/bash
# STEP 3: POLL & EXECUTE (<10 minutes)
# Run: bash ./step3-poll.sh

set -e

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

echo "=== STEP 3: POLL & EXECUTE (<10 min) ==="
echo ""

# Set working directory
cd ~/network-troubleshooting-bundle || { echo "ERROR: Directory not found"; exit 1; }
echo "Working in: $(pwd)"
echo ""

echo "Polling for fix commands..."
echo "Interval: 10 seconds"
echo "Timeout: 10 minutes (60 attempts)"
echo ""

START_TIME=$(date +%s)

for i in {1..60}; do
    # Check elapsed time
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    ELAPSED_MIN=$((ELAPSED / 60))
    
    # Report if taking too long
    if [ $ELAPSED_MIN -gt 5 ]; then
        echo "ESCALATED: Polling >5 min (${ELAPSED}s)" > ./node2-STATUS.md
        gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md 2>/dev/null || true
    fi
    
    # Check for fix commands
    FIX_FILE=$(curl -sL "$GIST_URL/node2-fix-commands.sh" 2>/dev/null)
    
    if echo "$FIX_FILE" | grep -q "^#"; then
        echo ""
        echo "✅ FIX COMMANDS RECEIVED!"
        echo ""
        
        # Save fix commands
        echo "$FIX_FILE" > ./fixes.sh
        chmod +x ./fixes.sh
        
        # Check script size
        LINES=$(wc -l < ./fixes.sh)
        if [ $LINES -gt 50 ]; then
            echo "⚠️ Script too long ($LINES lines)"
            echo "ESCALATED: Fix script too long ($LINES lines)" > ./node2-STATUS.md
            gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
            exit 1
        fi
        
        # Execute fixes
        echo "Executing fixes..."
        bash ./fixes.sh
        EXIT_CODE=$?
        
        echo ""
        echo "Posting results..."
        echo "Fix executed at $(date)" > /tmp/node2-results.txt
        echo "Exit code: $EXIT_CODE" >> /tmp/node2-results.txt
        
        if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
            gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-results.txt
            echo "RESULTS_READY" > ./node2-STATUS.md
            gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
            echo "  ✓ Results posted"
        fi
        
        # Run verification
        echo ""
        echo "Running verification..."
        if [ -f ./verify.sh ]; then
            bash ./verify.sh
            cat /tmp/node-ready.txt > /tmp/node2-verification.txt 2>/dev/null || true
            gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-verification.txt 2>/dev/null || true
        fi
        
        # Mark complete
        echo "COMPLETE" > ./node2-STATUS.md
        gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md 2>/dev/null || true
        
        echo ""
        echo "=== STEP 3 COMPLETE ==="
        echo "Status: COMPLETE"
        exit 0
    fi
    
    # Show progress
    echo -ne "  Polling... $i/60 (${ELAPSED_MIN} min elapsed)\r"
    sleep 10
done

# Timeout
echo ""
echo ""
echo "⚠️ TIMEOUT: No fix commands after 10 minutes"
echo ""
echo "ESCALATED: Timeout waiting for fixes" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md 2>/dev/null || true

echo ""
echo "=== STEP 3 COMPLETE (ESCALATED) ==="
exit 1
