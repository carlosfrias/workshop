#!/usr/bin/env bash
# dispatch-wiki-links.sh - Submit TI-WIKI-LINKS tasks to lab nodes
# Usage: ./scripts/dispatch-wiki-links.sh
# Protocol: TI-031 (Lab Node Offload - Orchestrator CRITICAL)

set -e

WORKSPACE="/Users/friasc/Dropbox/workshop"
LOG_DIR="$WORKSPACE/logs/wiki-links"
SCRIPTS_DIR="$WORKSPACE/technical-infrastructure/scripts"

echo "=== TI-WIKI-LINKS Dispatch ==="
echo "Protocol: TI-031 (Orchestrator CRITICAL - Lab Node Offload)"
echo "Timestamp: $(date -Iseconds)"
echo ""

# Create log directories
mkdir -p "$LOG_DIR"/{fnet3,fnet4,fnet5,fnet6,orchestrator}

echo "Submitting 5 parallel tasks to lab nodes..."
echo ""

# Step 001 → fnet3
echo "[Step 001] Submitting to fnet3..."
ssh fnet3 "cd $WORKSPACE && python3 $SCRIPTS_DIR/fix-wiki-home-links.py" > "$LOG_DIR/fnet3/step-001.log" 2>&1 &
PID_001=$!
echo "  → PID: $PID_001, Log: $LOG_DIR/fnet3/step-001.log"

# Step 002 → fnet4
echo "[Step 002] Submitting to fnet4..."
ssh fnet4 "cd $WORKSPACE && python3 $SCRIPTS_DIR/fix-wiki-readme-links.py" > "$LOG_DIR/fnet4/step-002.log" 2>&1 &
PID_002=$!
echo "  → PID: $PID_002, Log: $LOG_DIR/fnet4/step-002.log"

# Step 003 → fnet5
echo "[Step 003] Submitting to fnet5..."
ssh fnet5 "cd $WORKSPACE && python3 $SCRIPTS_DIR/fix-wiki-model-assignment-links.py" > "$LOG_DIR/fnet5/step-003.log" 2>&1 &
PID_003=$!
echo "  → PID: $PID_003, Log: $LOG_DIR/fnet5/step-003.log"

# Step 004 → fnet3 (parallel with 001)
echo "[Step 004] Submitting to fnet3..."
ssh fnet3 "cd $WORKSPACE && python3 $SCRIPTS_DIR/fix-wiki-anchor-links.py" > "$LOG_DIR/fnet3/step-004.log" 2>&1 &
PID_004=$!
echo "  → PID: $PID_004, Log: $LOG_DIR/fnet3/step-004.log"

# Step 005 → fnet6
echo "[Step 005] Submitting to fnet6..."
ssh fnet3 "cd $WORKSPACE && python3 $SCRIPTS_DIR/create-wiki-directory-indexes.py" > "$LOG_DIR/fnet6/step-005.log" 2>&1 &
PID_005=$!
echo "  → PID: $PID_005, Log: $LOG_DIR/fnet6/step-005.log"

echo ""
echo "Waiting for parallel tasks to complete..."
wait $PID_001 $PID_002 $PID_003 $PID_004 $PID_005
PARALLEL_STATUS=$?

echo ""
if [ $PARALLEL_STATUS -eq 0 ]; then
    echo "✅ All parallel tasks completed successfully."
    echo ""
    echo "Running Step 006 (verification) on orchestrator..."
    echo ""
    
    # Step 006 → orchestrator
    cd "$WORKSPACE"
    npm run build > "$LOG_DIR/orchestrator/build.log" 2>&1
    BUILD_STATUS=$?
    
    if [ $BUILD_STATUS -eq 0 ]; then
        python3 "$SCRIPTS_DIR/test-wiki-links.py" --verbose > "$LOG_DIR/orchestrator/verification.log" 2>&1
        VERIFY_STATUS=$?
        
        if [ $VERIFY_STATUS -eq 0 ]; then
            echo "✅ TI-WIKI-LINKS COMPLETE: All links valid!"
            echo ""
            echo "Summary:"
            tail -5 "$LOG_DIR/orchestrator/verification.log"
            exit 0
        else
            echo "❌ TI-WIKI-LINKS FAILED: Verification errors"
            echo ""
            echo "Check: $LOG_DIR/orchestrator/verification.log"
            tail -20 "$LOG_DIR/orchestrator/verification.log"
            exit 1
        fi
    else
        echo "❌ TI-WIKI-LINKS FAILED: Build errors"
        echo ""
        echo "Check: $LOG_DIR/orchestrator/build.log"
        tail -20 "$LOG_DIR/orchestrator/build.log"
        exit 1
    fi
else
    echo "❌ One or more parallel tasks failed. Check individual logs:"
    echo "  - $LOG_DIR/fnet3/step-001.log"
    echo "  - $LOG_DIR/fnet4/step-002.log"
    echo "  - $LOG_DIR/fnet5/step-003.log"
    echo "  - $LOG_DIR/fnet3/step-004.log"
    echo "  - $LOG_DIR/fnet6/step-005.log"
    exit 1
fi
