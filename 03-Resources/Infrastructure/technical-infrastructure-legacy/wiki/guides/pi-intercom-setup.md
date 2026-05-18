# pi-intercom Setup Guide

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/pi-intercom-setup.md`

**Purpose:** Set up pi and pi-intercom on all trading lab nodes for agent coordination  
**Version:** 1.1  
**Last Updated:** 2026-04-26  
**Nodes:** fnet1, fnet2, fnet3, fnet4, fnet5, fnet6, fnet7

---

## 🎯 Overview

This guide walks through:
1. Installing pi on each node (fnet1 through fnet7)
2. Configuring pi-intercom for agent-to-agent communication
3. Assessing node capacity (CPU, RAM, storage, models)
4. Assigning workloads based on capacity

---

## 📋 Prerequisites

### Network Requirements

- All nodes on same local network (192.168.0.0/24)
- Nodes can reach each other via hostname (fnet1.local through fnet7.local)
- Port 8080 available for intercom (default)

### User Access

- SSH access to each node (user: friasc)
- Sudo privileges on each node
- GitHub CLI authenticated on each node

---

## 🚀 Phase 1: Install pi on Each Node

### All Nodes (fnet1 through fnet7)

```bash
# SSH to node (replace X with node number 1-7)
ssh friasc@fnetX.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js (if not installed)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify Node.js
node --version  # Should be v20.x
npm --version   # Should be 9.x or higher

# Install pi globally
sudo npm install -g @mariozechner/pi-coding-agent

# Verify pi installation
pi --version

# Create pi directory
mkdir -p ~/.pi/agent
cd ~/.pi/agent

# Download NODE2-AGENTS.md (will customize per node later)
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./AGENTS.md

# Test pi
pi "Hello, this is fnetX. Confirm you can read AGENTS.md"
```

---

### Quick Deploy Script (Run from Mac Orchestrator)

```bash
#!/bin/bash
# deploy-pi-all-nodes.sh
# Run from Mac orchestrator

NODES=("fnet1" "fnet2" "fnet3" "fnet4" "fnet5" "fnet6" "fnet7")

for node in "${NODES[@]}"; do
    echo "=== DEPLOYING TO $node ==="
    
    # SSH and install
    ssh friasc@$node.local << 'SSHSCRIPT'
        # Update
        sudo apt update && sudo apt upgrade -y
        
        # Install Node.js
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt install -y nodejs
        
        # Install pi
        sudo npm install -g @mariozechner/pi-coding-agent
        
        # Create directory
        mkdir -p ~/.pi/agent
        cd ~/.pi/agent
        
        # Download AGENTS.md
        curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./AGENTS.md
        
        # Test
        pi --version
SSHSCRIPT
    
    echo "✓ $node complete"
    echo ""
done

echo "=== ALL NODES DEPLOYED ==="
```

---

## 🚀 Phase 2: Install pi-intercom on Each Node

### On All Nodes (fnet1 through fnet7)

```bash
# Install pi-intercom skill
pi install pi-intercom

# Verify installation
pi-intercom --help

# Start intercom with node-specific name
# fnet1:
pi-intercom start --name fnet1

# fnet2:
pi-intercom start --name fnet2

# ... repeat for fnet3 through fnet7
```

### Run as Background Service (Optional)

```bash
# Create systemd service
sudo tee /etc/systemd/system/pi-intercom.service << 'SERVICE'
[Unit]
Description=pi-intercom for agent coordination
After=network.target

[Service]
Type=simple
User=friasc
WorkingDirectory=/home/friasc
ExecStart=/usr/bin/pi-intercom start --name %H
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable pi-intercom
sudo systemctl start pi-intercom

# Check status
sudo systemctl status pi-intercom
```

---

## 🚀 Phase 3: Test Intercom Connectivity

### From Orchestrator (Mac)

```bash
# Install pi-intercom on Mac too
pi install pi-intercom

# Start orchestrator intercom
pi-intercom start --name orchestrator

# List all active sessions
pi-intercom list

# Expected output:
# fnet1 - active
# fnet2 - active
# fnet3 - active
# fnet4 - active
# fnet5 - active
# fnet6 - active
# fnet7 - active
# orchestrator - active
```

### Test Communication

```bash
# Send message to fnet1
pi-intercom send --to fnet1 --message "Test message from orchestrator"

# Ask fnet1 and wait for reply
pi-intercom ask --to fnet1 --message "What is your hostname?"

# fnet1 should reply:
pi-intercom reply --message "Hostname: fnet1"

# Broadcast to all nodes
pi-intercom send --to all --message "System check - please confirm"
```

---

## 📊 Phase 4: Node Capacity Assessment

### Run on Each Node

```bash
#!/bin/bash
# capacity-assessment.sh
# Run on each node: fnet1 through fnet7

echo "=== NODE CAPACITY ASSESSMENT ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

# CPU
echo "=== CPU ==="
echo "Model: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2 | xargs)"
echo "Cores: $(nproc)"
echo "Threads: $(grep -c processor /proc/cpuinfo)"
lscpu | grep -E "CPU\(s\)|Thread|Core"
echo ""

# RAM
echo "=== MEMORY ==="
free -h
echo ""
echo "Total RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Available RAM: $(free -h | grep Mem | awk '{print $7}')"
echo ""

# Storage
echo "=== STORAGE ==="
df -h / /home 2>/dev/null
echo ""
echo "Available Storage: $(df -h / | tail -1 | awk '{print $4}')"
echo ""

# GPU (if any)
echo "=== GPU ==="
lspci | grep -i vga || echo "No dedicated GPU found"
echo ""

# Network
echo "=== NETWORK ==="
ip -br addr show | grep -v "lo"
echo ""

# Ollama Status
echo "=== OLLAMA ==="
if command -v ollama &> /dev/null; then
    echo "Ollama: Installed"
    ollama list 2>/dev/null || echo "No models pulled yet"
else
    echo "Ollama: Not installed"
fi
echo ""

# pi Version
echo "=== PI ==="
pi --version 2>/dev/null || echo "pi not found"
echo ""

# pi-intercom Status
echo "=== PI-INTERCOM ==="
if command -v pi-intercom &> /dev/null; then
    echo "pi-intercom: Installed"
    pi-intercom status 2>/dev/null || echo "Not running"
else
    echo "pi-intercom: Not installed"
fi
echo ""

# Load Average
echo "=== SYSTEM LOAD ==="
uptime
echo ""

# Assessment Summary
echo "=== CAPACITY SUMMARY ==="
CPU_CORES=$(nproc)
TOTAL_RAM=$(free -g | grep Mem | awk '{print $2}')
AVAILABLE_STORAGE=$(df -g / | tail -1 | awk '{print $4}')

echo "CPU Cores: $CPU_CORES"
echo "Total RAM: ${TOTAL_RAM}G"
echo "Available Storage: ${AVAILABLE_STORAGE}G"
echo ""

# Workload Recommendation
echo "=== WORKLOAD RECOMMENDATION ==="
if [ $CPU_CORES -ge 8 ] && [ $TOTAL_RAM -ge 32 ]; then
    echo "✅ HIGH CAPACITY - Can run large models (7B+), complex analysis"
elif [ $CPU_CORES -ge 4 ] && [ $TOTAL_RAM -ge 16 ]; then
    echo "✅ MEDIUM CAPACITY - Can run medium models (3B-7B), standard tasks"
else
    echo "⚠️  LOW CAPACITY - Run small models (1B-3B), simple tasks only"
fi
echo ""
```

---

### Run Assessment on All Nodes

```bash
# From Mac orchestrator
# Create assessment script
cat > /tmp/capacity-assessment.sh << 'SCRIPT'
# [Paste the script above]
SCRIPT
chmod +x /tmp/capacity-assessment.sh

# Run on each node via SSH
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
    echo "=== ASSESSING $node ==="
    ssh friasc@$node "bash -s" < /tmp/capacity-assessment.sh > /tmp/${node}-capacity.txt
    echo "Saved to /tmp/${node}-capacity.txt"
done

# Combine results
cat /tmp/fnet*-capacity.txt > /tmp/all-nodes-capacity.txt
```

---

## 📊 Phase 5: Workload Assignment

### Node Capacity Template

| Node | CPU | RAM | Storage | GPU | Ollama | Capacity | Recommended Workload |
|------|-----|-----|---------|-----|--------|----------|---------------------|
| **fnet1** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet2** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet3** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet4** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet5** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet6** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |
| **fnet7** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [Based on assessment] |

---

### Workload Categories

#### High Capacity (8+ cores, 32G+ RAM)
**Suitable Nodes:** [TBD after assessment]

**Can Run:**
- ✅ 7B+ parameter models (qwen2.5:7b, llama3.1:8b, mistral:7b)
- ✅ Complex data analysis
- ✅ Multi-step reasoning
- ✅ Backtesting workflows
- ✅ Real-time signal processing
- ✅ Market research analysis
- ✅ Position management

**Recommended Roles:**
- Primary analysis node
- Model inference server
- Backtesting engine

---

#### Medium Capacity (4-7 cores, 16-31G RAM)
**Suitable Nodes:** [TBD after assessment]

**Can Run:**
- ✅ 3B-7B parameter models (qwen2.5:3b, gemma2:9b, phi3:medium)
- ✅ Standard analysis tasks
- ✅ Data preprocessing
- ✅ Monitoring and alerting
- ✅ Bookkeeping tasks
- ✅ Position monitoring

**Recommended Roles:**
- Secondary analysis node
- Monitoring and alerting
- Bookkeeping and reconciliation
- Position monitoring

---

#### Low Capacity (<4 cores, <16G RAM)
**Suitable Nodes:** [TBD after assessment]

**Can Run:**
- ✅ 1B-3B parameter models (qwen2.5:1.5b, gemma2:2b, phi3:mini)
- ✅ Simple monitoring
- ✅ Data collection
- ✅ Status reporting
- ✅ Lightweight tasks
- ✅ Health checks

**Recommended Roles:**
- Data collection
- Status reporting
- Health monitoring
- Simple logging tasks

---

## 🔧 Troubleshooting

### pi-intercom Not Starting

```bash
# Check if port is available
netstat -tlnp | grep 8080

# Kill any process using port 8080
sudo lsof -ti:8080 | xargs kill -9

# Restart intercom
pi-intercom start --name <node-name>
```

### Nodes Can't See Each Other

```bash
# Check network connectivity
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
    ping -c 1 $node.local
done

# Check /etc/hosts entries
cat /etc/hosts | grep fnet

# Add if missing
sudo tee -a /etc/hosts << 'HOSTS'
192.168.0.1 fnet1.local fnet1
192.168.0.2 fnet2.local fnet2
192.168.0.3 fnet3.local fnet3
192.168.0.4 fnet4.local fnet4
192.168.0.5 fnet5.local fnet5
192.168.0.6 fnet6.local fnet6
192.168.0.7 fnet7.local fnet7
HOSTS
```

### pi Not Found After Install

```bash
# Check npm global bin
npm config get prefix

# Add to PATH if needed
echo 'export PATH=$(npm config get prefix)/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
pi --version
```

---

## ✅ Setup Checklist

### Orchestrator (Mac)

- [ ] pi installed
- [ ] pi-intercom installed
- [ ] SSH keys distributed to all nodes (fnet1-fnet7)
- [ ] Can SSH to all nodes
- [ ] Intercom started: `pi-intercom start --name orchestrator`

### Node 1 (fnet1)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet1`
- [ ] Capacity assessment run

### Node 2 (fnet2)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet2`
- [ ] Capacity assessment run

### Node 3 (fnet3)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet3`
- [ ] Capacity assessment run

### Node 4 (fnet4)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet4`
- [ ] Capacity assessment run

### Node 5 (fnet5)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet5`
- [ ] Capacity assessment run

### Node 6 (fnet6)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet6`
- [ ] Capacity assessment run

### Node 7 (fnet7)

- [ ] Node.js installed (v20.x)
- [ ] pi installed
- [ ] pi-intercom installed
- [ ] AGENTS.md downloaded
- [ ] Intercom started: `pi-intercom start --name fnet7`
- [ ] Capacity assessment run

---

## 📊 Test Communication

```bash
# From orchestrator
# List all sessions
pi-intercom list

# Expected:
# fnet1 - active
# fnet2 - active
# fnet3 - active
# fnet4 - active
# fnet5 - active
# fnet6 - active
# fnet7 - active
# orchestrator - active

# Send test message to each
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
    pi-intercom send --to $node --message "Capacity assessment request"
done

# Wait for responses
# Each node should run capacity assessment and reply
```

---

## 📋 Next Steps After Setup

1. **Run capacity assessment on all 7 nodes**
2. **Document results in capacity table**
3. **Assign workloads based on capacity**
4. **Create node-specific AGENTS.md files**
5. **Test intercom communication**
6. **Deploy initial tasks**

---

**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Version:** 1.1  
**Last Updated:** 2026-04-26  
**Nodes:** fnet1, fnet2, fnet3, fnet4, fnet5, fnet6, fnet7
