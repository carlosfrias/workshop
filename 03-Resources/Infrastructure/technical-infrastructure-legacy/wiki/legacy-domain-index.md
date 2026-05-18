# Technical Infrastructure - Wiki Navigation Hub

**Last Updated:** 2026-05-04
**Status:** All 7 lab nodes **OFFLINE** after graceful shutdown, orchestrator RAM at 97%/critical, TI-030 decomposition planning in progress

This file is the top-level navigation hub for the Carlos' Desktop technical infrastructure domain. All documentation, prompts, playbooks, and scripts are discoverable from here.

---

## Quick Navigation

| I need to... | Go to |
|-------------|-------|
| Test the orchestration framework | [Testing Harness](wiki/testing-harness.md) |
| Understand the lab topology | [Lab Specs](#lab-specs) |
| Reimage a node with autoinstall | [Autoinstall Prompts](#autoinstall-prompts) |
| Set up Ollama on lab nodes | [Ollama Setup](wiki/guides/ollama-setup.md) |
| Configure WireGuard VPN | [WireGuard VPN](wiki/guides/wireguard-lab-vpn.md) |
| Run Ansible cleanup | [Cleanup Playbook](#ansible-playbooks) |
| Troubleshoot network issues | [Network Troubleshooting](#troubleshooting) |
| See recent operations | [Operational Snapshots](#operational-snapshots) |

---

## Lab Specs

### Hardware Inventory
| File | Description |
|------|-------------|
| [`operational/data/lab-specs/lab-capacity-report.json`](operational/data/lab-specs/lab-capacity-report.json) | Full hardware matrix: CPU, RAM, disk, BIOS, OS version per node |
| [`scripts/extract-hardware-specs.sh`](scripts/extract-hardware-specs.sh) | Script to extract and save hardware specs from all nodes |

### Node Assignments
| Node | IP | Tier | RAM | Role |
|------|-----|------|-----|------|
| fnet1 | 192.168.0.141 | Tier 2 | 15GB | Control plane (PXE, HTTP, WireGuard) |
| fnet2 | 192.168.0.142 | Tier 2 | 14GB | General purpose (reimaged) |
| fnet3 | 192.168.0.143 | Tier 1 | 31GB | Heavy inference / depot |
| fnet4 | 192.168.0.144 | Tier 1 | 31GB | Heavy inference |
| fnet5 | 192.168.0.145 | Tier 1 | 31GB | Heavy inference |
| fnet6 | 192.168.0.146 | Tier 1 | 31GB | Heavy inference |
| fnet7 | 192.168.0.147 | Tier 2 | 15GB | General purpose |

---

## Autoinstall Prompts

Prompts for creating and using Ubuntu 24.04 autoinstall USBs for zero-intervention node reimaging.

| Prompt | Description | Use Case |
|--------|-------------|----------|
| [`prompts/ubuntu-autoinstall-lab-nodes.md`](prompts/ubuntu-autoinstall-lab-nodes.md) | Full autoinstall workflow: ISO creation, grub.cfg with quoted `ds=`, user-data YAML, recovery mode reset | Standardize any lab node to 24.04 |
| [`prompts/create-ubuntu-autoinstall-usb.md`](prompts/create-ubuntu-autoinstall-usb.md) | Step-by-step USB creation: prerequisites, xorriso, dd, HTTP server | Build the autoinstall media |

**Key lessons baked into these prompts:**
- `ds=nocloud-net;s=...` must be **quoted** in grub (GRUB drops unquoted semicolons)
- Use `storage: {layout: {name: lvm, match: {size: largest, ssd: true}}}` (explicit paths crash Subiquity)
- Include `systemctl set-default multi-user.target` in late-commands (prevents gdm headless hang)
- Communicate plaintext password before creating user-data (never use unknown hashes)

---

## Ansible Playbooks

Located in `ansible/playbooks/`. Run with:
```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/<name>.yml
```

| Playbook | Description | Verified |
|----------|-------------|----------|
| [`cleanup-lab-nodes.yml`](ansible/playbooks/cleanup-lab-nodes.yml) | Remove desktop bloat, create swapfile, harden /tmp, configure logrotate | fnet6+fnet7 done |
| [`configure-nopasswd-sudo.yml`](ansible/playbooks/configure-nopasswd-sudo.yml) | Idempotent NOPASSWD sudo setup (prompts once, configures all) | fnet2-fnet5 verified |
| [`setup-ollama.yml`](ansible/playbooks/setup-ollama.yml) | Install Ollama service across lab nodes | All nodes |
| [`add-vpn-peer.yml`](ansible/playbooks/add-vpn-peer.yml) | Add WireGuard VPN peer | fnet1 gateway |
| [`setup-vpn-gateway.yml`](ansible/playbooks/setup-vpn-gateway.yml) | Deploy WireGuard server on fnet1 | Active since 2026-04-29 |
| [`gather-hardware-specs.yml`](ansible/playbooks/gather-hardware-specs.yml) | Collect hardware specs into JSON | Lab report generated |

### Ansible Roles
| Role | Location | Description |
|------|----------|-------------|
| `ollama-setup` | `ansible/roles/ollama-setup/` | 8-task decomposition: preflight, install, depot, models, validate, benchmark, cleanup |
| `wireguard-server` | `ansible/roles/wireguard-server/` | WireGuard gateway deployment |
| `wireguard-client` | `ansible/roles/wireguard-client/` | Client config generation |
| `duckdns-updater` | `ansible/roles/duckdns-updater/` | Dynamic DNS cron job |

---

## Prompt Templates

Reusable domain-specific prompts for `technical-infrastructure` tasks.

| Prompt | Description |
|--------|-------------|
| [`prompts/ubuntu-autoinstall-lab-nodes.md`](prompts/ubuntu-autoinstall-lab-nodes.md) | Autoinstall ISO creation and node reimaging |
| [`prompts/create-ubuntu-autoinstall-usb.md`](prompts/create-ubuntu-autoinstall-usb.md) | Step-by-step USB flashing guide |
| [`prompts/optimize-model-routing.md`](prompts/optimize-model-routing.md) | Model routing optimization on orchestrator |
| [`prompts/ollama-lab-setup.md`](prompts/ollama-lab-setup.md) | Ollama installation and model configuration across lab |
| [`prompts/hardware-spec-extraction.md`](prompts/hardware-spec-extraction.md) | Extract and save hardware specs from all nodes |
| [`prompts/network-router-upgrade.md`](prompts/network-router-upgrade.md) | Router firmware upgrade procedures |
| [`prompts/network-troubleshooting.md`](prompts/network-troubleshooting.md) | Diagnose and fix network issues across nodes |
| [`prompts/new-project-setup.md`](prompts/new-project-setup.md) | Scaffold a new project workspace |
| [`prompts/project-setup-template.md`](prompts/project-setup-template.md) | Project setup template reference |
| [`prompts/setup-wizard-template.md`](prompts/setup-wizard-template.md) | Setup wizard template with guided steps |

---

## Scripts

Utility scripts for infrastructure management.

| Script | Description |
|--------|-------------|
| [`scripts/extract-hardware-specs.sh`](scripts/extract-hardware-specs.sh) | Extract CPU, RAM, disk, OS from all nodes + generate JSON report |
| [`scripts/ollama-lab-setup.sh`](scripts/ollama-lab-setup.sh) | Install and configure Ollama tier-by-tier |
| [`scripts/ollama-benchmark.sh`](scripts/ollama-benchmark.sh) | Performance benchmark with tokens/second |
| [`scripts/ollama-cleanup.sh`](scripts/ollama-cleanup.sh) | Remove Ollama service and models from nodes |
| [`scripts/model-depot-sync.sh`](scripts/model-depot-sync.sh) | Sync models from depot to client nodes |
| [`scripts/duckdns-update.sh`](scripts/duckdns-update.sh) | Dynamic DNS IP update cron script |
| [`scripts/ollama-setup.sh`](scripts/ollama-setup.sh) | Legacy full Ollama setup (superseded by Ansible) |
| [`scripts/project-blueprint-setup.sh`](scripts/project-blueprint-setup.sh) | Project scaffolding with agents, wiki, etc. |

---

## Infrastructure Services

### PXE Server (fnet1)
- **Config:** `/etc/dnsmasq.d/pxe-lab.conf`
- **TFTP Root:** `/srv/tftp/`
- **HTTP Server:** `python3 -m http.server 8081` on `192.168.0.141`
- **Status:** Configured. DHCP proxy mode (doesn't conflict with TP-Link router)
- **Note:** Intel NICs PXE boot successfully; Realtek/consumer PXE ROMs time out

### WireGuard VPN
- **Server:** fnet1 (`wg0`, `10.200.200.1/24`)
- **DuckDNS:** `carlos-lab.duckdns.org`
- **Client Config:** `/usr/local/etc/wireguard/wg0.conf` (orchestrator)
- **Status:** Active. Off-premises access deferred (consumer router UDP issues)

### Ollama Model Depot
- **Depot Node:** fnet3
- **Models:** qwen3.5:4b, qwen3:8b, gemma4:e4b
- **Sync:** `scripts/model-depot-sync.sh`
- **Status:** Models need repull after standardization cleanup


---

## Wiki Domain Docs

Documentation for infrastructure consumers and developers.

| Doc | Description |
|-----|-------------|
| [wiki/guides/ollama-setup.md](wiki/guides/ollama-setup.md) | Ollama installation, model tiers, configuration |
| [wiki/guides/wireguard-lab-vpn.md](wiki/guides/wireguard-lab-vpn.md) | WireGuard VPN lab setup guide |
| [wiki/troubleshooting/network-troubleshooting-guide.md](wiki/troubleshooting/network-troubleshooting-guide.md) | Network diagnostic procedures |
| [wiki/guides/node-connection-guide.md](wiki/guides/node-connection-guide.md) | SSH key distribution, node access |
| [wiki/guides/static-ip-configuration.md](wiki/guides/static-ip-configuration.md) | DHCP reservation on TP-Link AX6000 |
| [wiki/guides/multi-node-setup-2026-04-26.md](wiki/guides/multi-node-setup-2026-04-26.md) | 7-node cluster deployment |
| [wiki/troubleshooting/node2-troubleshooting-session.md](wiki/troubleshooting/node2-troubleshooting-session.md) | Complete troubleshooting session log |

## Templates

Machine-readable templates for documentation that feeds the adaptive meta-orchestration system.

| Template | Purpose | Machine-Readable Tables |
|----------|---------|------------------------|
| [PLAN template](wiki/templates/PLAN-template.md) | Multi-step planning with decomposition tracking | Suggested/Actual model, node, latency, fallback |
| [SESSION-NOTES template](wiki/templates/SESSION-NOTES-template.md) | Session narrative with model performance tracking | Prompt type, model, cost, quality, adequacy |

These templates include structured tables that the meta-orchestration framework can parse to improve routing decisions, decomposition patterns, and cost optimization.

---

## Decomposition Examples

Step-by-step decomposition patterns for debugging and repair.

| Example | Steps | Description |
|---------|-------|-------------|
| [Network Troubleshooting](wiki/decomposition-examples/network-troubleshooting/00-decomposition-plan.md) | 29 | End-to-end network debugging: ping → DNS → firewall → driver fix |
| [Systemd Mount Lock](wiki/decomposition-examples/systemd-mount-lock/00-decomposition-plan.md) | 6 | Block device "busy" despite no visible processes: `lsof` → mountinfo → early-boot service |

---

## Operational Snapshots

Recent session artifacts. Not canonical documentation - reference for context.

| Date | File | Description |
|------|------|-------------|
| 2026-05-03 | [wiki/operational/status/STATUS-2026-05-03-0431.md](wiki/operational/status/STATUS-2026-05-03-0431.md) | Graceful shutdown playbook created, TI-030 decomposition planning started |
| 2026-05-03 | [operational/sessions/SESSION-NOTES-2026-05-03-0432.md](operational/sessions/SESSION-NOTES-2026-05-03-0432.md) | Session narrative: shutdown + AGENTS.md decomposition investigation |
| 2026-05-01 | [wiki/operational/status/STATUS-2026-05-01.md](wiki/operational/status/STATUS-2026-05-01.md) | Lab standardization complete, Ollama deployed, shutdown log |
| 2026-04-30 | [wiki/operational/status/STATUS-2026-04-30.md](wiki/operational/status/STATUS-2026-04-30.md) | Pre-standardization state (superseded) |

---

## Testing Harness

Run the TI-011 orchestration framework testing harness to validate all components end-to-end before deployments.

| Resource | Link |
|----------|------|
| **Full documentation** | [`wiki/testing-harness.md`](wiki/testing-harness.md) |
| **Run the harness** | [`wiki/guides/test-harness-runbook.md`](wiki/guides/test-harness-runbook.md) |
| **Latest test report** | [`operational/sessions/`](operational/sessions/) `TEST-REPORT-YYYY-MM-DD-*.md` |
| **Extension test coverage** | 54 tests across classifier, registry, health, submit, decompose, collect, synthesize, extension config, and node health |

**Quick start:**
```bash
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --verbose
```

---

## Backlog

Active and proposed work items for the technical-infrastructure domain. See [wiki/operational/BACKLOG.md](wiki/operational/BACKLOG.md) for full details with acceptance criteria.

| ID | Priority | Item | Status |
|----|----------|------|--------|
| TI-030 | 🔴 High | [Decompose AGENTS.md for local models](wiki/operational/BACKLOG.md#ti-030) | In Progress |
| TI-001 | 🔴 High | [Ansible Vault for sudo passwords](wiki/operational/BACKLOG.md#ti-001) | Proposed |
| TI-002 | 🟡 Medium | [fnet1 storage rebuild (LVM)](wiki/operational/BACKLOG.md#ti-002) | Deferred |
| TI-003 | 🟡 Medium | [Hardware spec JSON refresh](wiki/operational/BACKLOG.md#ti-003) | Deferred |
| TI-004 | 🟡 Medium | [Ollama benchmark fix](wiki/operational/BACKLOG.md#ti-004) | Deferred |
| TI-005 | 🟢 Low | [Model depot sync (fnet6 secondary)](wiki/operational/BACKLOG.md#ti-005) | Proposed |
| TI-006 | 🟢 Low | [NextCloud installation](wiki/operational/BACKLOG.md#ti-006) | Proposed |
| TI-007 | 🟢 Low | [File migration](wiki/operational/BACKLOG.md#ti-007) | Proposed |
| TI-008 | 🟢 Low | [Off-premises VPN (OPNsense)](wiki/operational/BACKLOG.md#ti-008) | Deferred |

---

## Recommendations

Actionable suggestions captured during sessions. One line each - expand when prioritized.

| Date | File | Topic |
|------|------|-------|
| 2026-05-01 | [RECOMMENDATION-2026-05-01-1055.md](recommendations/RECOMMENDATION-2026-05-01-1055.md) | Disable unattended-upgrade before early-boot reconfig |
| 2026-05-01 | [RECOMMENDATION-2026-05-01-0922.md](recommendations/RECOMMENDATION-2026-05-01-0922.md) | Different Ansible strategy for model pulls |
| 2026-05-01 | [RECOMMENDATION-2026-05-01-0915.md](recommendations/RECOMMENDATION-2026-05-01-0915.md) | Consider ZFS for fnet1 instead of LVM |

See [recommendations/](recommendations/) for all.

---

## Planning

Strategic ideas requiring dedicated design discussion. Captured during work so nothing is lost.

| Date | File | Topic |
|------|------|-------|
| 2026-05-01 | [PLAN-2026-05-01-0915.md](operational/planning/PLAN-2026-05-01-0915.md) | Depot redundancy model (fnet3 + fnet6) |
| 2026-05-01 | [PLAN-2026-05-01-1547.md](operational/planning/PLAN-2026-05-01-1547.md) | Task decomposition pipeline foundation |
| 2026-05-01 | [PLAN-2026-05-01-1605.md](operational/planning/PLAN-2026-05-01-1605.md) | Artifact sync and documentation loop |
| 2026-05-01 | [PLAN-2026-05-01-1645.md](operational/planning/PLAN-2026-05-01-1645.md) | Meta-orchestration framework full architecture |
| 2026-05-01 | [PLAN-2026-05-01-1730.md](operational/planning/PLAN-2026-05-01-1730.md) | Auto-complexity routing integration (remaining phases) |

See [operational/planning/](operational/planning/) for all.

---

## Cross-Domain References

| Domain | Wiki | Purpose |
|--------|------|---------|
| bookkeeping | `bookkeeping/wiki/` | Trade logging, reconciliation |
| market-research | `market-research/wiki/` | Signal generation, backtesting |
| position-management | `position-management/wiki/` | Order execution, risk |

---

## When You Need Help

| What happened | Where to look |
|---------------|---------------|
| New node needs OS install | [Autoinstall Prompts](#autoinstall-prompts) |
| Network unreachable | [`prompts/network-troubleshooting.md`](prompts/network-troubleshooting.md) |
| Ollama won't start | [`wiki/guides/ollama-setup.md`](wiki/guides/ollama-setup.md) |
| VPN connection failed | [`wiki/guides/wireguard-lab-vpn.md`](wiki/guides/wireguard-lab-vpn.md) |
| Model routing questions | [`pi-keyword-router/`](pi-keyword-router/) |

---

**For the full package documentation (extensions, skills, agents), see [`wiki/README.md`](wiki/README.md)**
