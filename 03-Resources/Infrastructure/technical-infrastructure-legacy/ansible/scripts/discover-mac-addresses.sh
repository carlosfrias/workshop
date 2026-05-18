#!/bin/bash
# Discover MAC addresses for all lab nodes
# Use this to configure DHCP reservations on the router

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     LAB NODES MAC ADDRESS DISCOVERY                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Define expected inventory (from ansible/inventory.yml)
NODES="fnet1:192.168.0.141 fnet2:192.168.0.142 fnet3:192.168.0.143 fnet4:192.168.0.144 fnet5:192.168.0.145 fnet6:192.168.0.146 fnet7:192.168.0.147"

echo "| Hostname | IP Address     | MAC Address       | Status     |"
echo "|----------|----------------|-------------------|------------|"

for entry in $NODES; do
  name=$(echo $entry | cut -d: -f1)
  ip=$(echo $entry | cut -d: -f2)
  
  mac=$(ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no friasc@$ip "ip link show | grep ether | awk '{print \$2}'" 2>/dev/null | head -1)
  
  if [ -n "$mac" ]; then
    status="✅ ONLINE"
  else
    mac="N/A"
    status="❌ OFFLINE"
  fi
  
  printf "| %-8s | %-14s | %-17s | %-10s |\n" "$name" "$ip" "$mac" "$status"
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "1. Power on all offline nodes"
echo "2. Re-run this script to get all MAC addresses"
echo "3. Configure DHCP reservations on TP-Link AX6000 router"
echo "   Admin Panel: http://192.168.0.1 or http://tplinkwifi.net"
echo "   Path: Advanced → Network → DHCP Server → Address Reservation"
echo "═══════════════════════════════════════════════════════════"
