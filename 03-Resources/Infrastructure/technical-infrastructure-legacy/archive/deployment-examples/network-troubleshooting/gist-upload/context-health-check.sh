#!/bin/bash
# context-health-check.sh - Node 2 Context Monitoring
# Run: bash ./context-health-check.sh
# Download: curl -sL GIST_URL/context-health-check.sh -o ./context-health-check.sh

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
SESSION_START_FILE="/tmp/node2-session-start.txt"

# Record session start if first run
if [ ! -f "$SESSION_START_FILE" ]; then
    date > "$SESSION_START_FILE"
fi

# Set working directory
cd ~/network-troubleshooting-bundle 2>/dev/null || cd ~

echo "========================================"
echo "CONTEXT HEALTH CHECK - Node 2"
echo "========================================"
echo ""

# 1. Directory Check
echo "1. WORKING DIRECTORY:"
echo "   Current: $(pwd)"
echo "   Expected: /home/friasc/network-troubleshooting-bundle"
if [ "$(pwd)" != "/home/friasc/network-troubleshooting-bundle" ]; then
    echo "   WARNING: Wrong directory! Run: cd ~/network-troubleshooting-bundle"
fi
echo ""

# 2. Identity Check
echo "2. IDENTITY:"
echo "   I am Node 2 (WORKER), user friasc"
echo "   NOT the orchestrator (Mac cloud agent)"
echo ""

# 3. Status Check
echo "3. STATUS:"
if [ -f ./node2-STATUS.md ]; then
    echo "   Current: $(cat ./node2-STATUS.md)"
else
    echo "   No status file found"
fi
echo ""

# 4. Time Check
echo "4. TIME:"
echo "   Current: $(date)"
if [ -f "$SESSION_START_FILE" ]; then
    echo "   Session start: $(cat $SESSION_START_FILE)"
    START_EPOCH=$(date -d "$(cat $SESSION_START_FILE)" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    ELAPSED=$((NOW_EPOCH - START_EPOCH))
    ELAPSED_MIN=$((ELAPSED / 60))
    echo "   Elapsed: ${ELAPSED_MIN} minutes"
    if [ $ELAPSED_MIN -gt 5 ]; then
        echo "   WARNING: Session >5 min - Reload AGENTS.md"
    fi
fi
echo ""

# 5. Script Check
echo "5. SCRIPTS:"
if [ -f ./fixes.sh ]; then
    LINES=$(wc -l < ./fixes.sh)
    echo "   fixes.sh: $LINES lines"
    if [ $LINES -gt 50 ]; then
        echo "   WARNING: Too large - Request decomposition"
    fi
else
    echo "   No pending scripts"
fi
echo ""

# 6. Gist Connectivity
echo "6. GIST CONNECTIVITY:"
if curl -sL "$GIST_URL/NODE2-AGENTS.md" 2>/dev/null | grep -q "Node 2"; then
    echo "   OK - Gist reachable"
else
    echo "   WARNING - Gist may be unreachable"
fi
echo ""

# 7. Local Files Check
echo "7. LOCAL FILES:"
for file in ~/.pi/agent/AGENTS.md ./context-health-check.sh ./detect-hardware.sh ./diagnose.sh ./verify.sh; do
    if [ -f "$file" ]; then
        echo "   OK - $file"
    else
        echo "   MISSING - $file"
        echo "            Download: curl -sL \$GIST_URL/$(basename $file) -o $file"
    fi
done
echo ""

# 8. Reload Recommendation
echo "8. RECOMMENDATIONS:"
if [ $ELAPSED_MIN -gt 5 ] 2>/dev/null; then
    echo "   - Session >5 min: Reload AGENTS.md"
    echo "     curl -sL \$GIST_URL/NODE2-AGENTS.md | grep -A 25 'IDENTITY'"
elif [ -f ./fixes.sh ] && [ $(wc -l < ./fixes.sh) -gt 50 ] 2>/dev/null; then
    echo "   - Large script: Request decomposition"
else
    echo "   - On track - continue workflow"
fi
echo "   - File missing? DOWNLOAD from Gist (don't create!)"
echo "   - Wrong directory? cd ~/network-troubleshooting-bundle"
echo ""

echo "========================================"
echo "HEALTH CHECK COMPLETE"
echo "========================================"
