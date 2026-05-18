# Node Connection Guide

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/node-connection-guide.md`

**Purpose:** Connect cloud agent to worker nodes for management and troubleshooting  
**Version:** 1.0  
**Last Updated:** 2026-04-26

---

## 🎯 Connection Options

### Option 1: GitHub Gist (Recommended for Offline/Async)

**Best For:**
- ✅ Nodes with intermittent connectivity
- ✅ Asynchronous communication
- ✅ Persistent audit trail
- ✅ No API keys required
- ✅ Works behind firewalls

**Setup:**
```bash
# On each node (fnet2, fnet6, fnet7)
cd ~/network-troubleshooting-bundle

# Download gist-message-queue skill
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md

# Authenticate GitHub CLI
gh auth login

# Test Gist communication
gh gist list
```

**Communication Pattern:**
```bash
# Worker posts status
echo "DIAGNOSTIC_READY" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# Cloud agent monitors
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-STATUS.md"

# Cloud agent responds
# Posts fix commands to Gist
# Worker polls and executes
```

**Pros:**
- No API keys needed
- Persistent audit trail
- Works offline (once authenticated)
- Firewall-friendly (HTTPS only)
- Free, no cost

**Cons:**
- Polling-based (10-60 second latency)
- Requires GitHub authentication
- Rate limits (60 requests/hour unauthenticated, 5000/hour authenticated)

**Gist URL:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

### Option 2: SSH Direct Connection (Recommended for Real-Time)

**Best For:**
- ✅ Real-time interaction
- ✅ Full shell access
- ✅ Complex troubleshooting
- ✅ File transfers
- ✅ Interactive sessions

**Setup:**
```bash
# Generate SSH key on orchestrator (Mac)
ssh-keygen -t ed25519 -f ~/.ssh/trading-lab -C "trading-lab-orchestrator"

# Copy key to each node
ssh-copy-id -i ~/.ssh/trading-lab friasc@fnet2.local
ssh-copy-id -i ~/.ssh/trading-lab friasc@fnet6.local
ssh-copy-id -i ~/.ssh/trading-lab friasc@fnet7.local

# Test connection
ssh -i ~/.ssh/trading-lab friasc@fnet2.local "hostname"
```

**SSH Config (Mac Orchestrator):**
```bash
# ~/.ssh/config
Host fnet2
    HostName fnet2.local
    User friasc
    IdentityFile ~/.ssh/trading-lab
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host fnet6
    HostName fnet6.local
    User friasc
    IdentityFile ~/.ssh/trading-lab
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host fnet7
    HostName fnet7.local
    User friasc
    IdentityFile ~/.ssh/trading-lab
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

**Usage:**
```bash
# Connect to node
ssh fnet2 "cd ~/network-troubleshooting-bundle && bash ./step2-diagnostics.sh"

# Copy files to node
scp ~/scripts/fix.sh fnet2:~/network-troubleshooting-bundle/

# Port forward (if needed)
ssh -L 8080:localhost:80 fnet2
```

**Pros:**
- Real-time interaction
- Full shell access
- Secure (encrypted)
- Standard tooling
- No polling latency

**Cons:**
- Requires network connectivity
- SSH key management
- May need firewall configuration
- No persistent audit trail (unless logged)

---

### Option 3: pi-intercom (Local Network)

**Best For:**
- ✅ Same local network
- ✅ Session-to-session coordination
- ✅ Real-time agent communication
- ✅ Cross-session context sharing

**Setup:**
```bash
# Install pi-intercom on all nodes
pi install pi-intercom

# Start intercom on each node
pi-intercom start --name fnet2
pi-intercom start --name fnet6
pi-intercom start --name fnet7

# List active sessions
pi-intercom list
```

**Usage:**
```bash
# Send message to node
pi-intercom send --to fnet2 --message "Run diagnostics"

# Ask and wait for reply
pi-intercom ask --to fnet2 --message "What is your status?"

# Reply from node
pi-intercom reply --message "Status: COMPLETE"
```

**Pros:**
- Real-time communication
- Built for agent coordination
- No external dependencies
- Context sharing possible

**Cons:**
- Requires local network connectivity
- All nodes must run pi with intercom
- Less mature than SSH/Gist
- No persistent audit trail

---

### Option 4: Hybrid Approach (Recommended for Production)

**Best For:**
- ✅ Production environments
- ✅ Maximum flexibility
- ✅ Redundancy
- ✅ Different scenarios

**Configuration:**
```bash
# Primary: SSH for real-time when online
# Secondary: Gist for async when offline
# Tertiary: pi-intercom for local coordination
```

**Decision Tree:**
```
Node reachable via SSH?
    ├─ YES → Use SSH (real-time)
    └─ NO → Node offline?
        ├─ YES → Use Gist (async, polling)
        └─ NO → Use pi-intercom (local)
```

**Implementation:**
```bash
#!/bin/bash
# connect-node.sh - Smart connection script

NODE=$1
COMMAND=$2

# Try SSH first
if ssh -o ConnectTimeout=5 $NODE "echo OK" 2>/dev/null; then
    echo "SSH available - using real-time"
    ssh $NODE "$COMMAND"
    
# Fall back to Gist
elif curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/${NODE}-STATUS.md" 2>/dev/null | grep -q "."; then
    echo "SSH unavailable - using Gist (async)"
    # Post command to Gist
    echo "$COMMAND" > /tmp/${NODE}-command.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/${NODE}-command.txt
    echo "Command posted - waiting for execution"
    
else
    echo "ERROR: Node unreachable via SSH and Gist"
    exit 1
fi
```

---

## 📊 Connection Comparison

| Feature | Gist | SSH | pi-intercom | Hybrid |
|---------|------|-----|-------------|--------|
| **Real-time** | ❌ (10-60s latency) | ✅ | ✅ | ✅ (when online) |
| **Offline capable** | ✅ | ❌ | ❌ | ✅ (fallback) |
| **Audit trail** | ✅ (persistent) | ⚠️ (must log) | ❌ | ✅ |
| **Firewall friendly** | ✅ (HTTPS) | ⚠️ (port 22) | ⚠️ (local) | ✅ |
| **Setup complexity** | Low | Medium | Low | Medium |
| **API keys** | ❌ None | ❌ None | ❌ None | ❌ None |
| **Best for** | Async, offline | Real-time | Local coordination | Production |

---

## 🎯 Recommended Configuration

### For Each Node

#### Node 2 (fnet2) - Realtek NIC
```bash
# Primary: SSH
ssh -i ~/.ssh/trading-lab friasc@fnet2.local

# Secondary: Gist (when offline)
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-STATUS.md"

# Working directory
cd ~/network-troubleshooting-bundle
```

#### Node 6 (fnet6) - Intel NUC
```bash
# Primary: SSH
ssh -i ~/.ssh/trading-lab friasc@fnet6.local

# Secondary: Gist (when offline)
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node6-STATUS.md"

# Working directory
cd ~/network-troubleshooting-bundle
```

#### Node 7 (fnet7) - Intel NUC
```bash
# Primary: SSH
ssh -i ~/.ssh/trading-lab friasc@fnet7.local

# Secondary: Gist (when offline)
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node7-STATUS.md"

# Working directory
cd ~/network-troubleshooting-bundle
```

---

## 🔧 Setup Checklist

### Orchestrator (Mac)

```bash
# 1. Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/trading-lab -C "trading-lab-orchestrator"

# 2. Add to SSH config
cat >> ~/.ssh/config << 'SSHCONFIG'
Host fnet2
    HostName fnet2.local
    User friasc
    IdentityFile ~/.ssh/trading-lab

Host fnet6
    HostName fnet6.local
    User friasc
    IdentityFile ~/.ssh/trading-lab

Host fnet7
    HostName fnet7.local
    User friasc
    IdentityFile ~/.ssh/trading-lab
SSHCONFIG

# 3. Test GitHub CLI auth
gh auth status

# 4. Install pi-intercom (optional)
pi install pi-intercom
```

### Each Worker Node (fnet2, fnet6, fnet7)

```bash
# 1. Add orchestrator SSH key
# (Copy public key from Mac to ~/.ssh/authorized_keys)

# 2. Install GitHub CLI (if not installed)
sudo apt update && sudo apt install gh

# 3. Authenticate GitHub CLI
gh auth login

# 4. Create working directory
mkdir -p ~/network-troubleshooting-bundle
cd ~/network-troubleshooting-bundle

# 5. Download NODE2-AGENTS.md
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md

# 6. Test Gist access
gh gist list

# 7. Install pi-intercom (optional)
pi install pi-intercom
```

---

## 📋 Usage Examples

### Check Node Status

```bash
# Via SSH (real-time)
ssh fnet2 "cat ~/network-troubleshooting-bundle/node2-STATUS.md"

# Via Gist (async)
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-STATUS.md"
```

### Run Diagnostics

```bash
# Via SSH (real-time)
ssh fnet2 "cd ~/network-troubleshooting-bundle && bash ./step2-diagnostics.sh"

# Via Gist (async)
# Post command to Gist
echo "bash ./step2-diagnostics.sh" > /tmp/fnet2-command.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/fnet2-command.txt
# Node polls and executes
```

### Monitor All Nodes

```bash
# Create monitoring script
cat > ~/monitor-all-nodes.sh << 'MONITOR'
#!/bin/bash
echo "=== NODE STATUS MONITOR ==="
for node in fnet2 fnet6 fnet7; do
    echo ""
    echo "=== $node ==="
    # Try SSH first
    if ssh -o ConnectTimeout=3 $node "cat ~/network-troubleshooting-bundle/node2-STATUS.md" 2>/dev/null; then
        :
    else
        # Fall back to Gist
        curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/${node}-STATUS.md" 2>/dev/null || echo "No status"
    fi
done
MONITOR

chmod +x ~/monitor-all-nodes.sh
bash ~/monitor-all-nodes.sh
```

---

## 🚨 Troubleshooting Connections

### SSH Connection Fails

```bash
# Check node is reachable
ping fnet2.local

# Check SSH service
ssh -v fnet2.local "hostname"

# Check key permissions
chmod 600 ~/.ssh/trading-lab

# Check SSH config
ssh -F ~/.ssh/config fnet2.local "hostname"
```

### Gist Connection Fails

```bash
# Check GitHub CLI auth
gh auth status

# Re-authenticate if needed
gh auth login

# Test Gist access
gh gist list

# Check network connectivity
curl -sL https://gist.github.com
```

### pi-intercom Connection Fails

```bash
# Check intercom is running
pi-intercom status

# List active sessions
pi-intercom list

# Restart intercom
pi-intercom stop
pi-intercom start --name <node-name>
```

---

## 📊 Recommended Setup

**For Production:**

| Node | Primary | Secondary | Tertiary |
|------|---------|-----------|----------|
| fnet2 | SSH | Gist | - |
| fnet6 | SSH | Gist | - |
| fnet7 | SSH | Gist | - |

**Rationale:**
- SSH for real-time when nodes are online
- Gist for async when nodes are offline
- No need for pi-intercom unless local coordination needed
- Redundancy ensures management capability

---

**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Version:** 1.0  
**Last Updated:** 2026-04-26
