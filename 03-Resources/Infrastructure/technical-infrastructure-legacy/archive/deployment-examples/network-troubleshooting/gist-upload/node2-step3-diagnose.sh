#!/bin/bash
# Node 2 Setup - Step 3: Run Diagnostics (WITH TETHER CONNECTED)
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step3-diagnose.sh -o ./node2-step3-diagnose.sh && bash ./node2-step3-diagnose.sh

set -e

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
TETHER_CONNECTION="netplan-enp7s0"
TARGET_IP="192.168.0.254"
GATEWAY="192.168.0.1"
ETHERNET_IFACE="enp7s0"

echo "========================================"
echo "NODE 2 SETUP: STEP 3 - DIAGNOSTICS"
echo "========================================"
echo ""
echo "This script will:"
echo "  1. Check current connectivity (tether stays connected)"
echo "  2. Configure ethernet (enp7s0) WITHOUT disconnecting tether"
echo "  3. Test enp7s0 specifically (interface-bound tests)"
echo "  4. Run diagnostics"
echo "  5. Post to Gist"
echo "  6. Wait for fix commands"
echo ""
echo "✓ Tether remains connected for internet access"
echo "✓ All tests use explicit interface binding"
echo ""
read -p "Press ENTER to start..."

# ================================================================================
# STEP 1: Check current connectivity
# ================================================================================
echo "========================================"
echo "STEP 1: CHECKING CURRENT CONNECTIVITY"
echo "========================================"
echo ""

echo "Current network interfaces:"
ip -br addr show | grep -v "lo"
echo ""

# Check tether status
if ip -br addr show | grep -q "enx"; then
    TETHER_IFACE=$(ip -br addr show | grep "enx" | awk '{print $1}')
    TETHER_IP=$(ip -br addr show | grep "enx" | awk '{print $3}')
    echo "✓ Tether detected:"
    echo "  Interface: $TETHER_IFACE"
    echo "  IP: $TETHER_IP"
    echo ""
    TETHER_CONNECTED=true
else
    echo "⚠ No tether interface detected"
    echo "  You may lose internet access during this script"
    echo ""
    TETHER_CONNECTED=false
fi

# Test internet connectivity (via whatever route is active)
echo "Testing internet connectivity..."
if ping -c 2 -W 2 8.8.8.8 &>/dev/null; then
    echo "✓ Internet reachable (via active route)"
    INTERNET_OK=true
else
    echo "✗ Internet NOT reachable"
    INTERNET_OK=false
fi
echo ""

# ================================================================================
# STEP 2: Configure ethernet (enp7s0) - TETHER STAYS CONNECTED
# ================================================================================
echo "========================================"
echo "STEP 2: CONFIGURING ETHERNET (enp7s0)"
echo "========================================"
echo ""
echo "✓ Tether remains connected during this step"
echo ""

echo "Cleaning enp7s0 interface..."
sudo ip addr flush dev $ETHERNET_IFACE 2>/dev/null || true

echo "Assigning IP: $TARGET_IP/24 to $ETHERNET_IFACE"
sudo ip addr add $TARGET_IP/24 dev $ETHERNET_IFACE

echo "Bringing interface up..."
sudo ip link set $ETHERNET_IFACE up

echo "Adding gateway route via $ETHERNET_IFACE (metric 100)..."
sudo ip route add default via $GATEWAY dev $ETHERNET_IFACE metric 100 2>/dev/null || true

echo ""
echo "Interface status:"
ip -br addr show | grep $ETHERNET_IFACE
echo ""

echo "Current routing table:"
ip route show
echo ""

# ================================================================================
# STEP 3: Test enp7s0 specifically (INTERFACE-BOUND TESTS)
# ================================================================================
echo "========================================"
echo "STEP 3: TESTING enp7s0 SPECIFICALLY"
echo "========================================"
echo ""
echo "✓ All tests bound to enp7s0 interface (not tether)"
echo ""

GATEWAY_OK=false
INTERNET_VIA_ENP7S0=false

# Test gateway through enp7s0 specifically
echo "Testing gateway ($GATEWAY) via $ETHERNET_IFACE..."
if ping -c 3 -W 2 -I $ETHERNET_IFACE $GATEWAY 2>&1 | tee /tmp/gateway-test.log | grep -q "received"; then
    echo "  ✓ Gateway reachable via $ETHERNET_IFACE"
    GATEWAY_OK=true
else
    echo "  ✗ Gateway UNREACHABLE via $ETHERNET_IFACE"
    echo ""
    cat /tmp/gateway-test.log | tail -3
    echo ""
fi
echo ""

# Test internet through enp7s0 specifically
echo "Testing internet (8.8.8.8) via $ETHERNET_IFACE..."
if ping -c 3 -W 2 -I $ETHERNET_IFACE 8.8.8.8 2>&1 | tee /tmp/internet-test.log | grep -q "received"; then
    echo "  ✓ Internet reachable via $ETHERNET_IFACE"
    INTERNET_VIA_ENP7S0=true
else
    echo "  ✗ Internet UNREACHABLE via $ETHERNET_IFACE"
    echo ""
    cat /tmp/internet-test.log | tail -3
    echo ""
fi
echo ""

# Test DNS through enp7s0 specifically
echo "Testing DNS (google.com) via $ETHERNET_IFACE..."
if ping -c 3 -W 2 -I $ETHERNET_IFACE google.com &>/dev/null; then
    echo "  ✓ DNS resolution works via $ETHERNET_IFACE"
    DNS_OK=true
else
    echo "  ✗ DNS resolution FAILED via $ETHERNET_IFACE"
    DNS_OK=false
fi
echo ""

# Check routing
echo "Checking routing..."
echo "Routes via $ETHERNET_IFACE:"
ip route show | grep $ETHERNET_IFACE || echo "  (none found)"
echo ""

# ================================================================================
# STEP 4: Analyze and report
# ================================================================================
echo "========================================"
echo "CONNECTIVITY SUMMARY (enp7s0 specific)"
echo "========================================"
echo ""
echo "  Gateway via enp7s0:     $([ "$GATEWAY_OK" = true ] && echo '✓ WORKING' || echo '✗ FAILED')"
echo "  Internet via enp7s0:    $([ "$INTERNET_VIA_ENP7S0" = true ] && echo '✓ WORKING' || echo '✗ FAILED')"
echo "  DNS via enp7s0:         $([ "$DNS_OK" = true ] && echo '✓ WORKING' || echo '✗ FAILED')"
echo "  Tether connected:       $([ "$TETHER_CONNECTED" = true ] && echo '✓ YES' || echo '✗ NO')"
echo "  Internet (any route):   $([ "$INTERNET_OK" = true ] && echo '✓ WORKING' || echo '✗ FAILED')"
echo ""

if [ "$GATEWAY_OK" = true ] && [ "$INTERNET_VIA_ENP7S0" = true ]; then
    echo "✅ enp7s0 IS WORKING - All tests passed!"
    echo ""
    DIAGNOSIS="enp7s0_WORKING"
elif [ "$GATEWAY_OK" = true ] && [ "$INTERNET_VIA_ENP7S0" = false ]; then
    echo "⚠️ PARTIAL: Gateway works but internet blocked via enp7s0"
    echo "  → Likely router-side blocking (MAC filter, parental controls, firewall)"
    echo ""
    DIAGNOSIS="enp7s0_GATEWAY_OK_INTERNET_BLOCKED"
elif [ "$GATEWAY_OK" = false ]; then
    echo "✗ CRITICAL: Gateway unreachable via enp7s0"
    echo "  → Check cable, router port, NIC hardware, or driver"
    echo ""
    DIAGNOSIS="enp7s0_GATEWAY_UNREACHABLE"
else
    echo "⚠️ UNKNOWN STATE - Review test output above"
    DIAGNOSIS="enp7s0_UNKNOWN"
fi

read -p "Press ENTER to continue..."
echo ""

# ================================================================================
# STEP 5: Run full diagnostics
# ================================================================================
echo "========================================"
echo "STEP 5: RUNNING FULL DIAGNOSTICS"
echo "========================================"
echo ""

# Set working directory
cd ~/network-troubleshooting-bundle

echo "Hardware detection..."
./detect-hardware.sh > /tmp/hardware-report.txt
echo "  ✓ Saved to /tmp/hardware-report.txt"

echo "Network diagnostics..."
./diagnose.sh > /tmp/network-diagnosis.log
echo "  ✓ Saved to /tmp/network-diagnosis.log"

# Add interface-specific test results
cat >> /tmp/network-diagnosis.log << DIAGNOSIS

=== INTERFACE-SPECIFIC TEST RESULTS ===
Test Time: $(date)
Interface: $ETHERNET_IFACE
Target IP: $TARGET_IP
Gateway: $GATEWAY
Tether Connected: $TETHER_CONNECTED

Gateway Test (via enp7s0): $([ "$GATEWAY_OK" = true ] && echo 'PASS' || echo 'FAIL')
Internet Test (via enp7s0): $([ "$INTERNET_VIA_ENP7S0" = true ] && echo 'PASS' || echo 'FAIL')
DNS Test (via enp7s0): $([ "$DNS_OK" = true ] && echo 'PASS' || echo 'FAIL')

Diagnosis: $DIAGNOSIS
DIAGNOSIS

# Combine into single diagnostic file
cat /tmp/hardware-report.txt /tmp/network-diagnosis.log > /tmp/node2-diagnostic.txt
echo ""

# ================================================================================
# STEP 6: Post to Gist
# ================================================================================
echo "========================================"
echo "STEP 6: POSTING TO GIST"
echo "========================================"
echo ""

if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
    echo "Posting diagnostics..."
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-diagnostic.txt
    echo "  ✓ Diagnostics posted"
    
    echo "Updating status..."
    echo "DIAGNOSTIC_READY" > ./node2-STATUS.md
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
    echo "  ✓ Status: DIAGNOSTIC_READY"
    echo ""
    echo "✅ Posted to Gist successfully"
    echo ""
else
    echo "⚠️ GitHub CLI not authenticated"
    echo ""
    echo "Manual copy required. Copy everything below:"
    echo "========================================"
    cat /tmp/node2-diagnostic.txt
    echo "========================================"
fi
echo ""

# ================================================================================
# STEP 7: Wait for fix commands (tether stays connected)
# ================================================================================
echo "========================================"
echo "STEP 7: WAITING FOR FIX COMMANDS"
echo "========================================"
echo ""
echo "Polling for fix commands from cloud agent..."
echo "Timeout: 10 minutes (600 seconds)"
echo "Polling interval: 10 seconds"
echo "✓ Tether remains connected for internet access"
echo ""

for i in {1..60}; do
    # Check for fix commands
    if curl -sL "$GIST_URL/node2-fix-commands.sh" 2>/dev/null | grep -q "^#"; then
        echo ""
        echo "✅ FIX COMMANDS RECEIVED!"
        echo ""
        
        echo "Downloading..."
        curl -sL "$GIST_URL/node2-fix-commands.sh" -o ./fixes.sh
        chmod +x ./fixes.sh
        
        echo "Executing..."
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
        break
    else
        echo -ne "  Polling... $i/60 (10s intervals)\r"
        sleep 10
    fi
done
echo ""

if [ $i -eq 60 ]; then
    echo ""
    echo "⚠️ TIMEOUT: No fix commands received after 10 minutes"
    echo ""
    echo "Possible causes:"
    echo "  1. Cloud agent hasn't seen diagnostics yet"
    echo "  2. Gist post failed"
    echo "  3. Network connectivity issue"
    echo ""
    echo "Next steps:"
    echo "  - Check Gist in browser: https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463"
    echo "  - Verify node2-diagnostic.txt was posted"
    echo "  - Contact cloud agent"
    echo ""
    echo "ESCALATED: Timeout waiting for fix commands" > ./node2-STATUS.md
fi

echo ""
echo "========================================"
echo "STEP 3 COMPLETE"
echo "========================================"
echo ""
echo "Next: Run verification"
echo "  ./verify.sh"
echo ""
echo "Or check status:"
echo "  cat ./node2-STATUS.md"
echo ""
