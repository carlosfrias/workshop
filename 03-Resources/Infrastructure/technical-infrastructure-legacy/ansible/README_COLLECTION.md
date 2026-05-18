# friaslab.trading_lab — Ansible Collection for Trading Infrastructure

**Namespace:** `friaslab`  
**Collection:** `trading_lab`  
**Version:** `1.0.0`  
**License:** MIT

---

## 📋 Collection Contents

### Playbooks (15)

| Playbook | Purpose | Target |
|----------|---------|--------|
| `capacity-report.yml` | Gather hardware/capacity specs from all nodes | All nodes |
| `deploy-pi.yml` | Install Node.js, pi, pi-intercom on lab nodes | Lab nodes |
| `add-vpn-peer.yml` | Add a new peer to WireGuard VPN | VPN gateway |
| `cleanup-lab-nodes.yml` | Clean up temporary files and unused models | Lab nodes |
| `cleanup-ollama.yml` | Remove unused Ollama models | Lab nodes |
| `fix-pi-availability.yml` | Restart pi and intercom services | Lab nodes |
| `full-pi-validation.yml` | Validate pi install across all nodes | All nodes |
| `gather-hardware-specs.yml` | Hardware spec inventory | All nodes |
| `install-pi.yml` | Install pi on a node | Lab nodes |
| `optimize-lab.yml` | Optimize lab configuration | Lab nodes |
| `setup-ollama.yml` | Configure Ollama on nodes | Lab nodes |
| `setup-vpn-gateway.yml` | Set up WireGuard VPN gateway | VPN gateway |
| `test-pi-installation.yml` | Test pi installation | Lab nodes |
| `test-reboot-persistence.yml` | Test service persistence after reboot | Lab nodes |
| `update-pi.yml` | Update pi to latest version | Lab nodes |

### Roles (6)

| Role | Purpose |
|------|---------|
| `ollama-setup` | Install, configure, benchmark Ollama models |
| `pi-installation` | Install Node.js and pi globally |
| `pi-optimization` | Optimize pi configuration for lab |
| `duckdns-updater` | Dynamic DNS update for off-premises access |
| `wireguard-server` | WireGuard VPN server |
| `wireguard-client` | WireGuard VPN client |

### Scripts (2)

| Script | Purpose |
|--------|---------|
| `scripts/discover-mac-addresses.sh` | Discover node MAC addresses |
| `scripts/run-validation.sh` | Run validation suite |

---

## 🚀 Install the Collection

The collection lives inside this repository at `technical-infrastructure/ansible/`.

### From Git Repository

```bash
# Install from embedded subdirectory
ansible-galaxy collection install git+https://github.com/carlosfrias/trading-workspace.git,main#technical-infrastructure/ansible

# Development: force reinstall to pull latest changes
ansible-galaxy collection install git+https://github.com/carlosfrias/trading-workspace.git,main#technical-infrastructure/ansible --force
```

### Build and Install Local Tarball

```bash
cd technical-infrastructure/ansible
ansible-galaxy collection build
ansible-galaxy collection install friaslab-trading_lab-1.0.0.tar.gz --force
```

---

## 📊 Run Playbooks

### Using Collection Syntax

```bash
# Capacity report
ansible-playbook friaslab.trading_lab.capacity-report -i inventory.yml -kK

# Deploy pi to all lab nodes
ansible-playbook friaslab.trading_lab.deploy-pi -i inventory.yml -kK

# Setup Ollama on selected nodes
ansible-playbook friaslab.trading_lab.setup-ollama -i inventory.yml -kK --limit fnet3,fnet4
```

### Using Local Collection

```bash
cd technical-infrastructure/ansible

# Direct play
ansible-playbook -i inventory.yml playbooks/capacity-report.yml -kK
ansible-playbook -i inventory.yml playbooks/deploy-pi.yml -kK
```

---

## 📁 Inventory

### Nodes

| Node | IP | Tier | OS | Role |
|------|-----|------|-----|------|
| fnet1 | 192.168.0.141 | 2 | Ubuntu 24.04 | Lab node |
| fnet2 | 192.168.0.142 | 2 | Ubuntu 26.04 | Lab node |
| fnet3 | 192.168.0.143 | 1 | Ubuntu 20.04 | Lab node |
| fnet4 | 192.168.0.144 | 1 | Ubuntu 20.04 | Lab node |
| fnet5 | 192.168.0.145 | 1 | Ubuntu 20.04 | Lab node |
| fnet6 | 192.168.0.146 | 1 | Ubuntu 22.04 | Lab node |
| fnet7 | 192.168.0.147 | 2 | Ubuntu 22.04 | Lab node |

---

## 🔒 Security

Passwords are never stored in collection files.

**At runtime:**
```bash
ansible-playbook -i inventory.yml playbooks/deploy-pi.yml --ask-pass --ask-become-pass
```

**Or via Ansible Vault:**
```bash
ansible-vault create group_vars/all/secrets.yml
```

---

## 📖 Documentation

- [Collection Wiki](../../wiki/operations/ansible-collection.md)
- [Lab Specs](../../wiki/operations/lab-specs.md)
- [Node Connection Guide](../../wiki/operations/node-connection-guide.md)
- [Network Troubleshooting](../../wiki/operations/network-troubleshooting-guide.md)

---

**Repository:** https://github.com/carlosfrias/trading-workspace  
**Version:** 1.0.0  
**Updated:** 2026-04-29
