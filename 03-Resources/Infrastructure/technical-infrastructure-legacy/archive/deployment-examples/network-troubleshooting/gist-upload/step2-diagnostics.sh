#!/bin/bash
# STEP 2: DIAGNOSTICS (<2 minutes)
# Run: bash ./step2-diagnostics.sh

set -e

GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
ETHERNET_IFACE="enp7s0"
TARGET_IP="192.168.0.254"
GATEWAY="192.168.0.1"

echo "=== STEP 2: DIAGNOSTICS (<2 min) ==="
echo ""

# Set working directory
cd ~/network-troubleshooting-bundle || { echo "ERROR: Directory not found"; exit 1; }
echo "Working in: $(pwd)"
echo ""

# Configure enp7s0 (tether stays connected)
echo "Configuring $ETHERNET_IFACE..."
sudo ip addr flush dev $ETHERNET_IFACE 2>/dev/null || true
sudo ip addr add $TARGET_IP/24 dev $ETHERNET_IFACE
sudo ip link set $ETHERNET_IFACE up
sudo ip route add default via $GATEWAY dev $ETHERNET_IFACE metric 100 2>/dev/null || true
echo "  IP: $TARGET_IP/24"
echo "  Gateway: $GATEWAY"
echo ""

# Test enp7s0 specifically (interface-bound)
echo "Testing $ETHERNET_IFACE..."

GATEWAY_OK=false
INTERNET_OK=false

if ping -c 2 -W 2 -I $ETHERNET_IFACE $GATEWAY 2>&1 | grep -q "received"; then
    echo "  ✓ Gateway reachable"
    GATEWAY_OK=true
else
    echo "  ✗ Gateway unreachable"
fi

if ping -c 2 -W 2 -I $ETHERNET_IFACE 8.8.8.8 2>&1 | grep -q "received"; then
    echo "  ✓ Internet reachable"
    INTERNET_OK=true
else
    echo "  ✗ Internet unreachable"
fi

echo ""

# Run hardware detection
echo "Running hardware detection..."
./detect-hardware.sh > /tmp/hardware-report.txt
echo "  ✓ Saved to /tmp/hardware-report.txt"

# Run network diagnostics
echo "Running network diagnostics..."
./diagnose.sh > /tmp/network-diagnosis.log
echo "  ✓ Saved to /tmp/network-diagnosis.log"

# Combine diagnostics
cat /tmp/hardware-report.txt /tmp/network-diagnosis.log > /tmp/node2-diagnostic.txt

# Add test results
cat >> /tmp/node2-diagnostic.txt << TESTRESULTS

=== INTERFACE TESTS ===
Time: $(date)
Interface: $ETHERNET_IFACE
Gateway Test: $([ "$GATEWAY_OK" = true ] && echo 'PASS' || echo 'FAIL')
Internet Test: $([ "$INTERNET_OK" = true ] && echo 'PASS' || echo 'FAIL')
TESTRESULTS

echo ""

# Post to Gist
echo "Posting diagnostics to Gist..."
if command -v gh &> /dev/null && gh auth status &> /dev/null 2>&1; then
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-diagnostic.txt
    echo "DIAGNOSTIC_READY" > ./node2-STATUS.md
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
    echo "  ✓ Posted to Gist"
    echo "  ✓ Status: DIAGNOSTIC_READY"
else
    echo "  ⚠ GitHub CLI not authenticated"
    echo "  Manual post required"
fi

echo ""
echo "=== STEP 2 COMPLETE ==="
echo "Next: Run step3-poll.sh"
echo ""
