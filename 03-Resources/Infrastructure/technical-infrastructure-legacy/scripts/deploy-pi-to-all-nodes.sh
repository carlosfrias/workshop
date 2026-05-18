#!/bin/bash
# deploy-pi-to-all-nodes.sh
# SSH key-based deployment - macOS compatible

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     PI + INTERCOM DEPLOYMENT - ALL NODES (fnet1-fnet7)    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Find SSH key
SSH_KEY="$HOME/.ssh/id_ed25519"
if [ ! -f "$SSH_KEY" ]; then
    SSH_KEY="$HOME/.ssh/id_rsa"
fi

echo "Using SSH key: $SSH_KEY"
echo ""

# Node list (IP:hostname)
NODES="192.168.0.131:fnet1 192.168.0.150:fnet2 192.168.0.179:fnet3 192.168.0.109:fnet4 192.168.0.119:fnet5 192.168.0.103:fnet6 192.168.0.172:fnet7"

echo "Nodes to deploy:"
for node in $NODES; do
    ip=$(echo $node | cut -d: -f1)
    hostname=$(echo $node | cut -d: -f2)
    echo "  $ip → $hostname"
done
echo ""

# Test SSH connectivity
echo "=== TESTING SSH CONNECTIVITY ==="
for node in $NODES; do
    ip=$(echo $node | cut -d: -f1)
    hostname=$(echo $node | cut -d: -f2)
    if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o BatchMode=yes friasc@$ip "echo OK" &>/dev/null; then
        echo "  ✓ $hostname ($ip) - reachable"
    else
        echo "  ✗ $hostname ($ip) - UNREACHABLE"
    fi
done
echo ""

# Fix hostnames
echo "=== FIXING HOSTNAME CONFLICTS ==="
echo "→ Changing fnode1 to fnet1 (192.168.0.131)..."
ssh -i "$SSH_KEY" friasc@192.168.0.131 "sudo hostnamectl set-hostname fnet1 && sudo sed -i 's/fnode1/fnet1/g' /etc/hosts" && echo "  ✓ fnet1 set" || echo "  ⚠️ fnet1 failed"

echo "→ Changing fnet6 hostname (192.168.0.103) from fnet7 to fnet6..."
ssh -i "$SSH_KEY" friasc@192.168.0.103 "sudo hostnamectl set-hostname fnet6 && sudo sed -i 's/fnet7/fnet6/g' /etc/hosts" && echo "  ✓ fnet6 set" || echo "  ⚠️ fnet6 failed"
echo ""

# Install pi on all nodes
echo "=== INSTALLING PI ON ALL NODES ==="
for node in $NODES; do
    ip=$(echo $node | cut -d: -f1)
    hostname=$(echo $node | cut -d: -f2)
    echo "→ $hostname ($ip)..."
    
    ssh -i "$SSH_KEY" friasc@$ip << 'SSH'
        sudo apt update -qq 2>/dev/null || true
        if ! command -v node &> /dev/null; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt install -y -qq nodejs
        fi
        sudo npm install -g -q @mariozechner/pi-coding-agent 2>/dev/null || sudo npm install -g @mariozechner/pi-coding-agent
        mkdir -p ~/.pi/agent
        cd ~/.pi/agent
        curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./AGENTS.md
        echo "pi: $(pi --version 2>&1 | head -1)"
SSH
    
    echo "  ✓ $hostname"
done
echo ""

# Install pi-intercom
echo "=== INSTALLING PI-INTERCOM ==="
for node in $NODES; do
    ip=$(echo $node | cut -d: -f1)
    hostname=$(echo $node | cut -d: -f2)
    echo "→ $hostname ($ip)..."
    
    ssh -i "$SSH_KEY" friasc@$ip << 'SSH'
        pi install pi-intercom 2>&1 | tail -1
        echo "pi-intercom: $(command -v pi-intercom &>/dev/null && echo 'installed' || echo 'failed')"
SSH
    
    echo "  ✓ $hostname"
done
echo ""

# Start intercom on nodes
echo "=== STARTING INTERCOM ON NODES ==="
for node in $NODES; do
    ip=$(echo $node | cut -d: -f1)
    hostname=$(echo $node | cut -d: -f2)
    echo "→ $hostname..."
    
    ssh -i "$SSH_KEY" friasc@$ip "pkill -f pi-intercom 2>/dev/null; sleep 1; nohup pi-intercom start --name $hostname > /tmp/pi-intercom.log 2>&1 &"
    echo "  ✓ $hostname started"
done
echo ""

# Start orchestrator intercom
echo "=== STARTING ORCHESTRATOR INTERCOM ==="
pkill -f "pi-intercom.*orchestrator" 2>/dev/null || true
sleep 1
nohup pi-intercom start --name orchestrator > /tmp/orchestrator-intercom.log 2>&1 &
sleep 3
echo "✓ Orchestrator intercom started"
echo ""

# Test connectivity
echo "=== TESTING INTERCOM CONNECTIVITY ==="
sleep 2
pi-intercom list 2>/dev/null || echo "pi-intercom not found on Mac - installing..."
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    DEPLOYMENT COMPLETE                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "All nodes: fnet1, fnet2, fnet3, fnet4, fnet5, fnet6, fnet7"
echo ""
echo "Next: Run capacity assessment"
echo "  bash /Users/friasc/Dropbox/workshop/technical-infrastructure/scripts/capacity-assessment-all-nodes.sh"
