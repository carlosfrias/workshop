#!/bin/bash
# apply-fix.sh - Apply network fixes based on cloud agent diagnosis
# This script is a template - the cloud agent will specify which sections to run

set -e

LOG_FILE="/tmp/network-fix-$(date +%Y%m%d-%H%M%S).log"

echo "=== NETWORK FIX APPLICATION ===" | tee $LOG_FILE
echo "Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Function to log steps
log_step() {
    echo "[$(date +%H:%M:%S)] $1" | tee -a $LOG_FILE
}

log_step "Script started. Waiting for cloud agent instructions..."
echo "" | tee -a $LOG_FILE
echo "AVAILABLE FIXES:" | tee -a $LOG_FILE
echo "  1. Install Realtek r8168 driver" | tee -a $LOG_FILE
echo "  2. Install Intel microcode/firmware" | tee -a $LOG_FILE
echo "  3. Restart NetworkManager" | tee -a $LOG_FILE
echo "  4. Renew DHCP lease" | tee -a $LOG_FILE
echo "  5. Clear firewall rules" | tee -a $LOG_FILE
echo "  6. Set static IP" | tee -a $LOG_FILE
echo "  7. Configure DNS" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "INSTRUCTIONS: The cloud agent will specify which fix(es) to apply." | tee -a $LOG_FILE
echo "Run this script with the fix number(s) as arguments, or follow cloud agent prompts." | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE

# Fix 1: Install Realtek r8168 driver
fix_r8168() {
    log_step "Installing Realtek r8168 driver..."
    
    # Check if already installed
    if lsmod | grep -q r8168; then
        log_step "r8168 driver already loaded"
        return 0
    fi
    
    # Install from apt (requires internet)
    apt-get update
    apt-get install -y r8168-dkms
    
    # Switch drivers
    modprobe -r r8169 2>/dev/null || true
    modprobe r8168
    
    # Blacklist r8169 to prevent fallback
    echo "blacklist r8169" > /etc/modprobe.d/blacklist-r8169.conf
    update-initramfs -u
    
    log_step "r8168 driver installed and activated"
}

# Fix 2: Install Intel firmware
fix_intel_firmware() {
    log_step "Installing Intel firmware..."
    
    apt-get update
    apt-get install -y firmware-intel intel-microcode
    
    log_step "Intel firmware installed"
}

# Fix 3: Restart NetworkManager
fix_restart_network() {
    log_step "Restarting NetworkManager..."
    systemctl restart NetworkManager
    sleep 3
    log_step "NetworkManager restarted"
}

# Fix 4: Renew DHCP lease
fix_dhcp_renew() {
    log_step "Renewing DHCP lease..."
    primary_iface=$(ip route | grep default | awk '{print $5}' | head -1)
    if [ -n "$primary_iface" ]; then
        dhclient -r $primary_iface 2>/dev/null || true
        dhclient -v $primary_iface
        log_step "DHCP lease renewed on $primary_iface"
    else
        log_step "No primary interface found for DHCP renewal"
    fi
}

# Fix 5: Clear firewall rules
fix_clear_firewall() {
    log_step "Clearing firewall rules..."
    
    # Clear iptables
    iptables -F 2>/dev/null || true
    iptables -X 2>/dev/null || true
    
    # Stop ufw if running
    ufw disable 2>/dev/null || true
    
    log_step "Firewall rules cleared"
}

# Fix 6: Set static IP
fix_static_ip() {
    local ip=$1
    local gateway=$2
    local dns=$3
    
    log_step "Setting static IP: $ip (gateway: $gateway, DNS: $dns)"
    
    primary_iface=$(ip route | grep default | awk '{print $5}' | head -1)
    if [ -z "$primary_iface" ]; then
        primary_iface="eth0"
        log_step "Using default interface: $primary_iface"
    fi
    
    # Create Netplan config (Ubuntu 18.04+)
    cat > /etc/netplan/01-static-ip.yaml <<EOF
network:
  version: 2
  ethernets:
    $primary_iface:
      addresses: [$ip/24]
      routes:
        - to: default
          via: $gateway
      nameservers:
        addresses: [$dns]
EOF
    
    netplan apply
    log_step "Static IP configured via Netplan"
}

# Fix 7: Configure DNS
fix_dns() {
    local dns=$1
    
    log_step "Configuring DNS: $dns"
    
    # Backup existing resolv.conf
    cp /etc/resolv.conf /etc/resolv.conf.backup
    
    # Write new DNS config
    cat > /etc/resolv.conf <<EOF
nameserver $dns
nameserver 8.8.8.8
EOF
    
    log_step "DNS configured"
}

# Main execution - parse arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <fix_number> [fix_number...] [options]" | tee -a $LOG_FILE
    echo "" | tee -a $LOG_FILE
    echo "Examples:" | tee -a $LOG_FILE
    echo "  $0 1        # Install r8168 driver" | tee -a $LOG_FILE
    echo "  $0 3 4      # Restart NetworkManager, then renew DHCP" | tee -a $LOG_FILE
    echo "  $0 6 192.168.0.254 192.168.0.1 8.8.8.8  # Set static IP" | tee -a $LOG_FILE
    exit 1
fi

# Process fixes
for arg in "$@"; do
    case $arg in
        1)
            fix_r8168
            ;;
        2)
            fix_intel_firmware
            ;;
        3)
            fix_restart_network
            ;;
        4)
            fix_dhcp_renew
            ;;
        5)
            fix_clear_firewall
            ;;
        6)
            # Requires additional arguments: IP, gateway, DNS
            shift
            fix_static_ip "$1" "$2" "$3"
            shift 2
            ;;
        7)
            # Requires DNS argument
            shift
            fix_dns "$1"
            shift
            ;;
        *)
            log_step "Unknown fix number: $arg"
            ;;
    esac
done

echo "" | tee -a $LOG_FILE
log_step "Fix application completed"
echo "Log saved to: $LOG_FILE" | tee -a $LOG_FILE
echo "" | tee -a $LOG_FILE
echo "NEXT STEP: Run verify.sh to confirm the fix worked" | tee -a $LOG_FILE
