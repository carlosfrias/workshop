#!/bin/bash
# Node 2 Ethernet Fix - Single Command Execution with Tether Management
# Run: curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/fix-node2.sh | bash

set -e

TETHER_CONNECTION="netplan-enp7s0"
GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
TARGET_IP="192.168.0.254"
ALT_IP="192.168.0.150"
GATEWAY="192.168.0.1"
MAC="0c:9d:92:cc:55:4c"

echo "========================================"
echo "NODE 2 ETHERNET FIX"
echo "========================================"
echo ""
echo "Target: Configure enp7s0 for internet access"
echo "Primary IP: $TARGET_IP/24"
echo "Alternative IP: $ALT_IP/24 (if conflict)"
echo "Gateway: $GATEWAY"
echo "MAC: $MAC"
echo ""

# Download tether management script
echo "## Step 0: Downloading tether management script..."
curl -sL "$GIST_URL/manage-tether.sh" -o ~/manage-tether.sh
chmod +x ~/manage-tether.sh
echo "  ✓ manage-tether.sh downloaded"
echo ""

# CRITICAL: Disconnect tether FIRST
echo "========================================"
echo "DISCONNECTING TETHER"
echo "========================================"
echo ""
echo "Tether must be disconnected to test ethernet."
echo ""
echo "Disconnecting: $TETHER_CONNECTION"
nmcli connection down "$TETHER_CONNECTION" 2>/dev/null || echo "  (Connection may already be down)"
echo ""
echo "Waiting 5 seconds for routes to clear..."
sleep 5
echo ""
echo "Verifying tether is disconnected..."
if ip -br addr show | grep -q "enx"; then
    echo "  ⚠ Tether interface still detected"
    echo "  Please disable USB tethering on your phone"
    read -p "Press ENTER after disabling tether..."
else
    echo "  ✓ Tether disconnected"
fi
echo ""

# Step 1: Clean interface
echo "## Step 1: Preparing interface..."
# Remove all IPs from enp7s0
sudo ip addr flush dev enp7s0 2>/dev/null || true
# Remove any existing routes via gateway
sudo ip route del default via $GATEWAY 2>/dev/null || true
echo "  ✓ Interface cleaned"
echo ""

# Step 2: Assign IP
echo "## Step 2: Assigning IP address..."
sudo ip addr add $TARGET_IP/24 dev enp7s0
echo "  ✓ IP assigned: $TARGET_IP/24"
echo ""

# Step 3: Ensure interface is up
echo "## Step 3: Ensuring interface is up..."
sudo ip link set enp7s0 up
echo "  ✓ Interface up"
echo ""

# Step 4: Add default gateway
echo "## Step 4: Adding default gateway..."
sudo ip route add default via $GATEWAY dev enp7s0
echo "  ✓ Gateway added: $GATEWAY"
echo ""

# Step 5: Test gateway
echo "## Step 5: Testing gateway..."
if ping -c 2 -W 2 $GATEWAY; then
    echo "  ✓ Gateway reachable"
else
    echo "  ✗ Gateway unreachable - check router"
    echo ""
    read -p "Press ENTER to continue..."
fi
echo ""

# Step 6: Test internet
echo "## Step 6: Testing internet..."
if ping -c 2 -W 2 8.8.8.8; then
    echo "  ✓ Internet reachable - FIX SUCCESSFUL!"
    INTERNET_OK=true
else
    echo "  ⚠ Internet unreachable - Router may be blocking this node"
    INTERNET_OK=false
    echo ""
    echo "  Possible causes:"
    echo "    1. MAC address filtering on router"
    echo "    2. Parental controls blocking this device"
    echo "    3. IP conflict (another device has $TARGET_IP)"
    echo "    4. Router firewall blocking this MAC"
    echo ""
    read -p "Press ENTER to continue troubleshooting..."
    echo ""
    echo "  Checking for IP conflict..."
    if arping -c 2 -I enp7s0 $TARGET_IP 2>&1 | grep -q "Unicast reply"; then
        echo "  ⚠ IP CONFLICT: Another device is using $TARGET_IP"
        echo "  Trying alternative IP: $ALT_IP"
        echo ""
        sudo ip addr flush dev enp7s0
        sudo ip addr add $ALT_IP/24 dev enp7s0
        sudo ip route replace default via $GATEWAY dev enp7s0
        if ping -c 2 -W 2 8.8.8.8; then
            echo "  ✓ Alternative IP works!"
            INTERNET_OK=true
            TARGET_IP=$ALT_IP
        else
            echo "  ⚠ Still blocked - router-side issue"
            echo ""
            read -p "Press ENTER to continue..."
        fi
    else
        echo "  ✓ No IP conflict detected"
        echo ""
        read -p "Press ENTER to continue..."
    fi
fi
echo ""

# Step 7: Test DNS
echo "## Step 7: Testing DNS..."
if ping -c 2 -W 2 google.com; then
    echo "  ✓ DNS resolution works"
else
    echo "  ⚠ DNS resolution failed - trying direct DNS..."
    echo ""
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
    if ping -c 2 -W 2 google.com; then
        echo "  ✓ DNS works with 8.8.8.8"
    else
        echo "  ⚠ DNS still failing"
        echo ""
        read -p "Press ENTER to continue..."
    fi
fi
echo ""

# Step 8: Make permanent (NetworkManager)
echo "## Step 8: Making configuration permanent..."
if command -v nmcli &> /dev/null; then
    # Check if connection exists
    if nmcli connection show "Wired" &> /dev/null; then
        nmcli connection modify "Wired" ipv4.addresses $TARGET_IP/24 ipv4.gateway $GATEWAY ipv4.dns "8.8.8.8" ipv4.method manual
        nmcli connection up "Wired"
        echo "  ✓ Existing connection updated"
    else
        nmcli connection add type ethernet ifname enp7s0 con-name "Wired" ipv4.addresses $TARGET_IP/24 ipv4.gateway $GATEWAY ipv4.dns "8.8.8.8" ipv4.method manual
        echo "  ✓ New connection created"
    fi
else
    echo "  ⚠ NetworkManager not available - configuration is temporary"
    echo ""
    read -p "Press ENTER to continue..."
fi
echo ""

# Summary
echo "========================================"
echo "STATUS"
echo "========================================"
echo ""
echo "Network configuration:"
echo "  IP:       $TARGET_IP/24"
echo "  Gateway:  $GATEWAY"
echo "  DNS:      8.8.8.8"
echo "  MAC:      $MAC"
echo ""

# Check final connectivity
echo "Final connectivity check:"
if ping -c 2 -W 2 8.8.8.8 2>/dev/null; then
    echo "  ✓ Internet: WORKING"
    echo ""
    echo "========================================"
    echo "FIX COMPLETE - NETWORK IS WORKING"
    echo "========================================"
else
    echo "  ✗ Internet: BLOCKED (router-side issue)"
    echo ""
    echo "========================================"
    echo "ROUTER CONFIGURATION REQUIRED"
    echo "========================================"
    echo ""
    echo "The router is blocking this node. To fix:"
    echo ""
    echo "1. Reconnect tether to access router admin:"
    echo "   ~/manage-tether.sh up"
    echo ""
    echo "2. From another device, go to: http://$GATEWAY"
    echo "3. Log into router admin"
    echo "4. Find and disable:"
    echo "   - MAC Address Filtering"
    echo "   - Access Control"
    echo "   - Parental Controls"
    echo "5. Or add this MAC to allowed list:"
    echo "   $MAC"
    echo ""
    echo "6. Save changes and reboot router"
    echo ""
    read -p "Press ENTER after you've checked the router settings..."
fi
echo ""

echo "========================================"
echo "TETHER MANAGEMENT COMMANDS"
echo "========================================"
echo ""
echo "Use these commands to manage tether:"
echo "  ~/manage-tether.sh down      - Disconnect tether (for diagnostics)"
echo "  ~/manage-tether.sh up        - Reconnect tether (for router admin)"
echo "  ~/manage-tether.sh restart   - Restart NetworkManager + reconnect"
echo "  ~/manage-tether.sh status    - Check tether status"
echo ""
read -p "Press ENTER to continue..."

echo ""
echo "NEXT STEP:"
echo "  1. Run: ~/network-troubleshooting-bundle/verify.sh"
echo "  2. Check: cat /tmp/node-ready.txt"
if [ "$INTERNET_OK" = false ]; then
    echo "  3. Reconnect tether: ~/manage-tether.sh up"
    echo "  4. Configure router (see above)"
    echo "  5. Disconnect tether: ~/manage-tether.sh down"
    echo "  6. Test again"
fi
echo "  7. Paste output to cloud agent"
echo ""
read -p "Press ENTER to exit..."
