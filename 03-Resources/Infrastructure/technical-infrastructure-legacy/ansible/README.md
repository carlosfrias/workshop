# Ansible Automation for Trading Lab

**Purpose:** Ansible playbooks for managing Trading Lab infrastructure  
**Version:** 1.0  
**Last Updated:** 2026-04-26

---

## 📋 Included Playbooks

| Playbook | Purpose | Command |
|----------|---------|---------|
| `capacity-report.yml` | Gather hardware/capacity specs from all nodes | `ansible-playbook -i inventory.ini capacity-report.yml -kK` |
| `deploy-pi.yml` | Install Node.js, pi, pi-intercom on all nodes | `ansible-playbook -i inventory.ini deploy-pi.yml -kK` |

---

## 🚀 Quick Start

### 1. Prerequisites (Orchestrator/Mac)

```bash
# Install Ansible
pip install ansible

# Verify
ansible --version

# Install sshpass (for password-based SSH)
brew install sshpass
```

---

### 2. Inventory Configuration

**File:** `inventory.ini`

**Nodes:**
| Host | IP | Tier | Notes |
|------|-----|------|-------|
| fnet1 | 192.168.0.131 | 2 | Renamed from fnode1 |
| fnet2 | 192.168.0.150 | 2 | Resolute Raccoon (Ubuntu 26.04 dev) |
| fnet3 | 192.168.0.179 | 1 | Focal (Ubuntu 20.04) |
| fnet4 | 192.168.0.109 | 1 | Focal (Ubuntu 20.04) |
| fnet5 | 192.168.0.119 | 1 | Focal (Ubuntu 20.04) |
| fnet6 | 192.168.0.103 | 1 | Hostname currently fnet7 → will be fixed |
| fnet7 | 192.168.0.172 | 2 | Jammy (Ubuntu 22.04) |

---

### 3. Run Capacity Report

```bash
cd technical-infrastructure/ansible

# Prompt for SSH password and sudo password
ansible-playbook -i inventory.ini capacity-report.yml --ask-pass --ask-become-pass

# Or using -kK shorthand
ansible-playbook -i inventory.ini capacity-report.yml -kK
```

**Output:** `../lab-specs/lab-capacity-report.json`

---

### 4. Deploy pi + pi-intercom

```bash
cd technical-infrastructure/ansible

# Deploy to all lab nodes
ansible-playbook -i inventory.ini deploy-pi.yml -kK

# Deploy to specific nodes
ansible-playbook -i inventory.ini deploy-pi.yml -kK --limit fnet1,fnet2,fnet3
```

**Actions performed on each node:**
1. Fix hostname (fnode1 → fnet1, fnet6 conflict resolved)
2. Update `/etc/hosts` with all node entries
3. Install Node.js v20
4. Install pi globally
5. Install pi-intercom skill
6. Download NODE2-AGENTS.md
7. Create systemd service for pi-intercom
8. Install GitHub CLI

---

### 5. Verify Deployment

```bash
# Check intercom status on each node
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
    echo "=== $node ==="
    ssh friasc@$node "pi-intercom status"
done

# From orchestrator
pi-intercom list
```

---

## 📊 Capacity Report Structure

**Output:** `technical-infrastructure/lab-specs/lab-capacity-report.json`

**Contains:**
- Per-node: hostname, CPU, RAM, disk, OS, Ollama models
- Summary: tiers, aggregate stats, OS standardization needs
- Recommendations: which nodes for which workloads

---

## 🔒 Security Notes

**Password Handling:**
- ⚠️ **NEVER commit passwords to git**
- Use `ansible-playbook --ask-pass` (prompt at runtime)
- Or use Ansible Vault for encrypted passwords
- Or configure SSH keys beforehand

**SSH Key Setup (Recommended):**
```bash
# Generate key
ssh-keygen -t ed25519 -f ~/.ssh/trading-lab -C "trading-lab"

# Copy to all nodes
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
    ssh-copy-id -i ~/.ssh/trading-lab friasc@$node
done

# Then run without password prompt
ansible-playbook -i inventory.ini deploy-pi.yml
```

---

## 📁 Files

```
technical-infrastructure/ansible/
├── inventory.ini              #Node definitions (7 lab + 1 orchestrator)
├── capacity-report.yml        #Playbook: generate capacity report
├── deploy-pi.yml             #Playbook: deploy pi + pi-intercom
├── pi-intercom.service.j2    #Systemd service template
└── README.md                  #This file
```

---

## 🚨 Troubleshooting

### SSH Connection Refused

```bash
# Check node is reachable
ping 192.168.0.131

# Verify SSH service
ssh -o ConnectTimeout=5 friasc@192.168.0.131 "hostname"
```

### Sudo Password Incorrect

```bash
# Verify password manually first
ssh friasc@192.168.0.131 "echo 'password' | sudo -S hostname"
```

### Node.js Install Fails

```bash
# Manual fallback for fnet2 (unknown release)
ssh friasc@192.168.0.150 "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs"
```

---

**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Wiki:** See `wiki/operations/` for operations documentation  
**Version:** 1.0  
**Last Updated:** 2026-04-26
