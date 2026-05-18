#!/bin/bash
# verify.sh - Post-fix verification script
# Tests network connectivity and reports results

set -e

LOG_FILE="/tmp/network-verify-$(date +%Y%m%d-%H%M%S).log"
STATUS_FILE="/tmp/node-ready.txt"

echo "=== NETWORK VERIFICATION ===" | tee $LOG_FILE
echo "Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Track pass/fail
PASS_COUNT=0
FAIL_COUNT=0

test_check() {
    local name=$1
    local result=$2
    
    if [ $result -eq 0 ]; then
        echo "✓ $name: PASS" | tee -a $LOG_FILE
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "✗ $name: FAIL" | tee -a $LOG_FILE
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "## CONNECTIVITY TESTS" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Test 1: Interface has IP
primary_iface=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -n "$primary_iface" ] && ip addr show $primary_iface | grep -q "inet "; then
    test_check "Interface ($primary_iface) has IP" 0
else
    test_check "Interface has IP" 1
fi

# Test 2: Gateway reachable
gateway=$(ip route | grep default | awk '{print $3}')
if [ -n "$gateway" ] && ping -c 2 -W 2 $gateway &> /dev/null; then
    test_check "Gateway ($gateway) reachable" 0
else
    test_check "Gateway reachable" 1
fi

# Test 3: Can reach 8.8.8.8
if ping -c 2 -W 2 8.8.8.8 &> /dev/null; then
    test_check "Internet (8.8.8.8) reachable" 0
else
    test_check "Internet (8.8.8.8) reachable" 1
fi

# Test 4: DNS resolution
if ping -c 2 -W 2 google.com &> /dev/null; then
    test_check "DNS resolution (google.com)" 0
else
    test_check "DNS resolution (google.com)" 1
fi

# Test 5: Driver loaded correctly
echo "" | tee -a $LOG_FILE
echo "## DRIVER STATUS" | tee -a $LOG_FILE
if [ -n "$primary_iface" ] && command -v ethtool &> /dev/null; then
    driver=$(ethtool -i $primary_iface 2>/dev/null | grep "driver:" | cut -d: -f2 | xargs)
    echo "Active driver: $driver" | tee -a $LOG_FILE
    
    # Check for problematic drivers
    if [ "$driver" = "r8169" ]; then
        echo "⚠ WARNING: r8169 driver detected (known issues with some Realtek chips)" | tee -a $LOG_FILE
        test_check "Driver is not r8169" 1
    elif [ "$driver" = "r8168" ] || [ "$driver" = "e1000e" ] || [ "$driver" = "igb" ] || [ "$driver" = "igc" ]; then
        test_check "Driver is stable ($driver)" 0
    else
        test_check "Driver status ($driver)" 0
    fi
else
    echo "Driver check skipped (ethtool not available or no interface)" | tee -a $LOG_FILE
fi

# Test 6: Packet loss check
echo "" | tee -a $LOG_FILE
echo "## PACKET LOSS TEST" | tee -a $LOG_FILE
if [ -n "$gateway" ]; then
    packet_loss=$(ping -c 10 -W 1 $gateway 2>&1 | tail -1 | grep -oE "[0-9]+% packet loss" | grep -oE "[0-9]+")
    if [ -n "$packet_loss" ] && [ "$packet_loss" -eq 0 ]; then
        test_check "Packet loss to gateway (0%)" 0
    elif [ -n "$packet_loss" ] && [ "$packet_loss" -lt 50 ]; then
        echo "⚠ WARNING: ${packet_loss}% packet loss detected" | tee -a $LOG_FILE
        test_check "Packet loss acceptable (<50%)" 1
    else
        echo "✗ HIGH packet loss: ${packet_loss:-unknown}%" | tee -a $LOG_FILE
        test_check "Packet loss acceptable" 1
    fi
fi

# Summary
echo "" | tee -a $LOG_FILE
echo "## VERIFICATION SUMMARY" | tee -a $LOG_FILE
echo "Passed: $PASS_COUNT" | tee -a $LOG_FILE
echo "Failed: $FAIL_COUNT" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Determine overall status
if [ $FAIL_COUNT -eq 0 ]; then
    echo "OVERALL STATUS: ✓ ALL TESTS PASSED" | tee -a $LOG_FILE
    echo "COMPLETE" > $STATUS_FILE
    echo "" | tee -a $LOG_FILE
    echo "Node is ready. Status written to: $STATUS_FILE" | tee -a $LOG_FILE
    echo "Content: $(cat $STATUS_FILE)" | tee -a $LOG_FILE
elif [ $FAIL_COUNT -le 2 ]; then
    echo "OVERALL STATUS: ⚠ PARTIAL (some tests failed)" | tee -a $LOG_FILE
    echo "PARTIAL: $FAIL_COUNT tests failed" > $STATUS_FILE
    echo "" | tee -a $LOG_FILE
    echo "Node has partial connectivity. Review log for details." | tee -a $LOG_FILE
else
    echo "OVERALL STATUS: ✗ VERIFICATION FAILED" | tee -a $LOG_FILE
    echo "FAILED: $FAIL_COUNT tests failed" > $STATUS_FILE
    echo "" | tee -a $LOG_FILE
    echo "Node verification failed. Review log and re-run fixes." | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "Verification completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a $LOG_FILE
echo "Log saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "INSTRUCTIONS: Show the contents of $STATUS_FILE to the cloud agent during verification." | tee -a $LOG_FILE
