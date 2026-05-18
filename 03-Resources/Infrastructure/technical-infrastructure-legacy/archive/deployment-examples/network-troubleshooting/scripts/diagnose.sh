#!/bin/bash
# diagnose.sh - Network diagnostic script for offline execution
# Runs comprehensive network tests and logs results

set -e

LOG_FILE="/tmp/network-diagnosis-$(date +%Y%m%d-%H%M%S).log"

echo "=== NETWORK DIAGNOSIS ===" | tee $LOG_FILE
echo "Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a $LOG_FILE
echo "Log file: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Function to log section headers
log_section() {
    echo "" | tee -a $LOG_FILE
    echo "## $1" | tee -a $LOG_FILE
    echo "----------------------------------------" | tee -a $LOG_FILE
}

log_section "INTERFACE STATUS"
ip -br addr show 2>/dev/null || ip addr show 2>/dev/null | grep -E "^[0-9]+:|inet "
echo "" | tee -a $LOG_FILE

log_section "DEFAULT GATEWAY"
ip route | grep default || echo "No default gateway configured"
echo "" | tee -a $LOG_FILE

log_section "DNS CONFIGURATION"
cat /etc/resolv.conf 2>/dev/null || echo "Cannot read /etc/resolv.conf"
echo "" | tee -a $LOG_FILE

log_section "PING TESTS"

echo "Testing gateway..."
gateway=$(ip route | grep default | awk '{print $3}')
if [ -n "$gateway" ]; then
    if ping -c 3 -W 2 $gateway &> /dev/null; then
        echo "✓ Gateway ($gateway): Reachable" | tee -a $LOG_FILE
        ping -c 3 -W 2 $gateway | tail -2 | tee -a $LOG_FILE
    else
        echo "✗ Gateway ($gateway): Unreachable" | tee -a $LOG_FILE
    fi
else
    echo "⚠ No gateway configured" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

echo "Testing 8.8.8.8 (Google DNS)..."
if ping -c 3 -W 2 8.8.8.8 &> /dev/null; then
    echo "✓ 8.8.8.8: Reachable" | tee -a $LOG_FILE
    ping -c 3 -W 2 8.8.8.8 | tail -2 | tee -a $LOG_FILE
else
    echo "✗ 8.8.8.8: Unreachable" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

echo "Testing google.com (DNS resolution)..."
if ping -c 3 -W 2 google.com &> /dev/null; then
    echo "✓ google.com: Reachable (DNS works)" | tee -a $LOG_FILE
    ping -c 3 -W 2 google.com | tail -2 | tee -a $LOG_FILE
else
    echo "✗ google.com: Unreachable (DNS or routing issue)" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

log_section "DRIVER STATUS"
for iface in $(ip -o link show | awk -F': ' '{print $2}' | cut -d'@' -f1 | grep -v lo); do
    echo "Interface: $iface" | tee -a $LOG_FILE
    if command -v ethtool &> /dev/null; then
        ethtool -i $iface 2>/dev/null | tee -a $LOG_FILE || echo "  ethtool failed" | tee -a $LOG_FILE
    else
        echo "  ethtool not installed" | tee -a $LOG_FILE
    fi
    echo "" | tee -a $LOG_FILE
done

log_section "FIREWALL STATUS"
echo "iptables rules:" | tee -a $LOG_FILE
sudo iptables -L -n 2>/dev/null | head -20 | tee -a $LOG_FILE || echo "  Cannot read iptables" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

echo "ufw status:" | tee -a $LOG_FILE
sudo ufw status 2>/dev/null | tee -a $LOG_FILE || echo "  ufw not available" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

log_section "PACKET CAPTURE (10 packets)"
primary_iface=$(ip route | grep default | awk '{print $5}' | head -1)
if [ -n "$primary_iface" ]; then
    echo "Capturing on $primary_iface..." | tee -a $LOG_FILE
    sudo timeout 5 tcpdump -i $primary_iface -c 10 2>&1 | tee -a $LOG_FILE || echo "  tcpdump failed or no packets" | tee -a $LOG_FILE
else
    echo "No primary interface found" | tee -a $LOG_FILE
fi
echo "" | tee -a $LOG_FILE

log_section "DIAGNOSIS SUMMARY"

# Determine status
if ping -c 1 -W 2 google.com &> /dev/null; then
    echo "STATUS: ONLINE" | tee -a $LOG_FILE
    echo "Network is fully functional" | tee -a $LOG_FILE
elif ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
    echo "STATUS: PARTIAL (DNS issue)" | tee -a $LOG_FILE
    echo "Can reach IP addresses but DNS resolution failed" | tee -a $LOG_FILE
elif [ -n "$gateway" ] && ping -c 1 -W 2 $gateway &> /dev/null; then
    echo "STATUS: PARTIAL (Gateway only)" | tee -a $LOG_FILE
    echo "Can reach gateway but not internet" | tee -a $LOG_FILE
else
    echo "STATUS: OFFLINE" | tee -a $LOG_FILE
    echo "Cannot reach gateway or internet" | tee -a $LOG_FILE
fi

echo "" | tee -a $LOG_FILE
echo "Diagnosis completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "Log saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "INSTRUCTIONS: This log will be reviewed by the cloud agent during verification." | tee -a $LOG_FILE
