#!/bin/bash
# detect-hardware.sh - Collect hardware information for cloud diagnosis
# Focus: Network interfaces, drivers, system info

set -e

echo "=== HARDWARE DETECTION REPORT ==="
echo "Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

echo "## SYSTEM INFORMATION"
echo "Hostname: $(hostname)"
echo "OS: $(lsb_release -ds 2>/dev/null || cat /etc/*release 2>/dev/null | head -1)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "CPU: $(lscpu | grep "Model name" | cut -d: -f2 | xargs)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo ""

echo "## NETWORK INTERFACES"
echo ""

# List all network interfaces
echo "### Interface List"
ip -br addr show 2>/dev/null || ip addr show 2>/dev/null | grep -E "^[0-9]+:|inet "
echo ""

# Detailed info for each interface
echo "### Detailed Interface Information"
for iface in $(ip -o link show | awk -F': ' '{print $2}' | cut -d'@' -f1); do
    echo ""
    echo "Interface: $iface"
    echo "  MAC: $(ip link show $iface 2>/dev/null | grep link/ether | awk '{print $2}')"
    echo "  State: $(ip link show $iface 2>/dev/null | grep -oE "state [A-Z]+" | cut -d' ' -f2)"
    echo "  IP: $(ip -4 addr show $iface 2>/dev/null | grep inet | awk '{print $2}')"
done
echo ""

echo "## NETWORK INTERFACE CONTROLLERS (NIC)"
echo ""

# PCI devices - network controllers
echo "### PCI Network Controllers"
lspci -nn | grep -i "network\|ethernet" || echo "No PCI network controllers found"
echo ""

# USB network devices
echo "### USB Network Devices"
lsusb | grep -i "network\|ethernet\|Ralink\|Realtek\|Intel" || echo "No USB network devices found"
echo ""

echo "## DRIVER INFORMATION"
echo ""

# Kernel modules in use
echo "### Loaded Network Driver Modules"
lsmod | grep -E "r8169|r8168|e1000|e1000e|igb|igc|atlantic|bonding" || echo "No common network driver modules loaded"
echo ""

# Driver details for each interface
echo "### Driver Details per Interface"
for iface in $(ip -o link show | awk -F': ' '{print $2}' | cut -d'@' -f1 | grep -v lo); do
    echo ""
    echo "Interface: $iface"
    
    # Try ethtool for driver info
    if command -v ethtool &> /dev/null; then
        driver=$(ethtool -i $iface 2>/dev/null | grep "driver:" | cut -d: -f2 | xargs)
        version=$(ethtool -i $iface 2>/dev/null | grep "version:" | cut -d: -f2 | xargs)
        firmware=$(ethtool -i $iface 2>/dev/null | grep "firmware-version:" | cut -d: -f2 | xargs)
        echo "  Driver: ${driver:-unknown}"
        echo "  Driver Version: ${version:-unknown}"
        echo "  Firmware: ${firmware:-unknown}"
    else
        echo "  ethtool not installed"
    fi
    
    # Kernel module info
    module=$(readlink /sys/class/net/$iface/device/driver/module 2>/dev/null | xargs basename 2>/dev/null)
    echo "  Kernel Module: ${module:-unknown}"
done
echo ""

echo "## NETWORK CONNECTIVITY TEST"
echo ""

# Check default gateway
echo "### Default Gateway"
ip route | grep default || echo "No default gateway configured"
echo ""

# DNS configuration
echo "### DNS Configuration"
cat /etc/resolv.conf 2>/dev/null || echo "Cannot read /etc/resolv.conf"
echo ""

# Ping test (if connected)
echo "### Connectivity Test"
if ping -c 2 -W 2 8.8.8.8 &> /dev/null; then
    echo "✓ Can reach 8.8.8.8"
    ping -c 2 -W 2 8.8.8.8 | tail -2
else
    echo "✗ Cannot reach 8.8.8.8"
fi
echo ""

if ping -c 2 -W 2 google.com &> /dev/null; then
    echo "✓ DNS resolution works"
else
    echo "✗ DNS resolution failed"
fi
echo ""

echo "## INSTALLED PACKAGES"
echo ""

# Check for network-related packages
echo "### Network Driver Packages"
dpkg -l | grep -E "r8168|r8169|intel-microcode|firmware-realtek|firmware-intel" || echo "No specific network driver packages found"
echo ""

echo "### END OF HARDWARE REPORT ==="
echo ""
echo "INSTRUCTIONS: Copy this entire report and paste it to the cloud agent for diagnosis."
