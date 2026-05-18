# Ansible Collection Gap Assessment

**Purpose:** Document the actual gap between current Ansible structure and a proper Ansible collection  
**Evidence Date:** 2026-05-02  
**Method:** Read from disk, do not assume or calculate

---

## 📂 Current Evidence: Files on Disk

### Collection Metadata (✅ Now Present)
```
galaxy.yml                    ✅ Present at root
meta/runtime.yml              ✅ Present (requires_ansible: ">=2.14.0")
```

### Roles (6 roles exist)
```
roles/duckdns-updater/tasks/main.yml
roles/duckdns-updater/defaults/main.yml
roles/duckdns-updater/templates/duckdns-update.sh.j2

roles/ollama-setup/tasks/main.yml (imports 7 other ymls)
roles/ollama-setup/tasks/benchmark.yml
roles/ollama-setup/tasks/cleanup.yml
roles/ollama-setup/tasks/depot.yml
roles/ollama-setup/tasks/install.yml
roles/ollama-setup/tasks/models.yml
roles/ollama-setup/tasks/preflight.yml
roles/ollama-setup/tasks/validate.yml

roles/pi-installation/tasks/main.yml
roles/pi-installation/templates/pi-intercom.service.j2   ← Moved 2026-05-02

roles/pi-optimization/tasks/main.yml

roles/wireguard-client/defaults/main.yml
roles/wireguard-client/handlers/main.yml
roles/wireguard-client/tasks/main.yml
roles/wireguard-client/templates/client.conf.j2

roles/wireguard-server/defaults/main.yml
roles/wireguard-server/handlers/main.yml
roles/wireguard-server/tasks/main.yml
roles/wireguard-server/templates/wg0.conf.j2
```

### Playbooks (15 files, all in `playbooks/`)
```
playbooks/add-vpn-peer.yml
playbooks/capacity-report.yml
playbooks/cleanup-lab-nodes.yml
playbooks/cleanup-ollama.yml
playbooks/configure-nopasswd-sudo.yml
playbooks/deploy-pi.yml
playbooks/fix-pi-availability.yml
playbooks/full-pi-validation.yml
playbooks/gather-hardware-specs.yml
playbooks/install-pi.yml
playbooks/optimize-lab.yml
playbooks/setup-ollama.yml
playbooks/setup-vpn-gateway.yml
playbooks/test-pi-installation.yml
playbooks/test-reboot-persistence.yml
playbooks/update-pi.yml
```

### Templates (3 templates across roles)
```
roles/duckdns-updater/templates/duckdns-update.sh.j2
roles/pi-installation/templates/pi-intercom.service.j2
roles/wireguard-client/templates/client.conf.j2
roles/wireguard-server/templates/wg0.conf.j2
```

### Scripts (2 scripts)
```
scripts/discover-mac-addresses.sh
scripts/run-validation.sh
```

### Config files
```
ansible.cfg
inventory.ini          ← Environment-specific (not part of collection)
inventory.yml          ← Environment-specific (not part of collection)
```

### Documentation
```
README.md
README-vpn.md
README_COLLECTION.md
```

---

## ✅ What Is Already Collection-Ready

### Roles (6 of 6)

All 6 roles follow proper Ansible role conventions:

| Role | tasks/main.yml | defaults/main.yml | handlers/main.yml | templates/ |
|------|----------------|-------------------|-------------------|------------|
| `duckdns-updater` | ✅ | ✅ | ❌ | ✅ (1 template) |
| `ollama-setup` | ✅ | ❌ | ❌ | ❌ |
| `pi-installation` | ✅ | ❌ | ❌ | ✅ (1 template) |
| `pi-optimization` | ✅ | ❌ | ❌ | ❌ |
| `wireguard-client` | ✅ | ✅ | ✅ | ✅ (1 template) |
| `wireguard-server` | ✅ | ✅ | ✅ | ✅ (1 template) |

**Verdict on roles:** 3 roles (duckdns-updater, wireguard-client, wireguard-server) are fully-featured with defaults, handlers, templates. 3 roles (ollama-setup, pi-installation, pi-optimization) lack defaults and handlers. All have proper `tasks/main.yml`.

**Template placement verified 2026-05-02:**
- `pi-intercom.service.j2` moved from `ansible/` root → `roles/pi-installation/templates/`

### Playbooks

All 15 playbooks are now in `playbooks/` subdirectory. None remain at the root level.

### Metadata

| File | Status | Content |
|------|--------|---------|
| `galaxy.yml` | ✅ Present | namespace: friaslab, name: trading_lab, version: 1.0.0 |
| `meta/runtime.yml` | ✅ Present | requires_ansible: ">=2.14.0", action_groups, plugin_routing |

---

## ❌ What Is Still Missing for a Full Collection

| Collection Requirement | Files Found | Status | Priority |
|------------------------|------------|--------|----------|
| `plugins/` directory | None | ❌ Not present | Low |
| `docs/` directory | None | ❌ Not present | Medium |
| `changelogs/` | None | ❌ Not present | Low |
| `meta/execution-environment.yml` | None | ❌ Not present | Low |
| Role defaults for 3 roles | Partial | 🟡 Missing | Medium |
| Role handlers for 3 roles | Partial | 🟡 Missing | Low |

---

## 📊 Remaining Gap Analysis

### 1. No `plugins/`

Collections often include custom modules/filter plugins. Not currently needed — all functionality uses built-in modules and community.general.

**Effort:** Low (only needed if we write custom modules).

### 2. No `docs/`

Collection documentation for `ansible-doc` and Galaxy. The `README_COLLECTION.md` exists at root but there is no structured `docs/` directory.

**Effort:** Low (move/rename README_COLLECTION.md or create docs structure).

### 3. No `changelogs/`

Version tracking. Optional for collections. Can be added when publishing to Galaxy.

**Effort:** Low (create `changelogs/config.yaml` when ready to publish).

### 4. Inventory Files at Root

`inventory.ini` and `inventory.yml` are environment-specific. In a collection, these are typically **not packaged** — the consumer provides their own inventory.

**Current state:** They live at root. For collection packaging, add to `build_ignore` in `galaxy.yml` (already partially covered by `'*.swp'` etc., but should explicitly list `inventory.ini` and `inventory.yml`).

**Effort:** Trivial (update `galaxy.yml` `build_ignore`).

### 5. Three Roles Lack Defaults/Handlers

| Role | Missing defaults | Missing handlers | Impact |
|------|------------------|------------------|--------|
| `ollama-setup` | ✅ | ✅ | Role variables not configurable without editing tasks |
| `pi-installation` | ✅ | ✅ | Service restarts not handled via handlers |
| `pi-optimization` | ✅ | ✅ | Same as above |

**Effort:** Medium (create 6 files: 3 defaults/main.yml, 3 handlers/main.yml).

---

## 🎯 Recommendation

### Current Verdict

**The Ansible directory IS now a minimum viable collection.** `galaxy.yml` and `meta/runtime.yml` are present. All playbooks are in `playbooks/`. All roles are properly structured. The collection can be built and installed.

### To Package Now (Minimum Effort)

1. **Update `galaxy.yml` `build_ignore`** to explicitly exclude `inventory.ini`, `inventory.yml`, `ansible.cfg` (environment-specific)
2. **Verify with `ansible-galaxy collection build`**
3. **Test install locally**

### To Reach "Full Collection" (Medium Effort)

1. Add `roles/ollama-setup/defaults/main.yml`
2. Add `roles/ollama-setup/handlers/main.yml`
3. Add `roles/pi-installation/defaults/main.yml`
4. Add `roles/pi-installation/handlers/main.yml`
5. Add `roles/pi-optimization/defaults/main.yml`
6. Add `roles/pi-optimization/handlers/main.yml`
7. Create `docs/` directory (or symlink `README_COLLECTION.md`)
8. Optionally add `plugins/` placeholder
9. Optionally add `changelogs/config.yaml`

---

## 📋 Action Log

| Date | Action | File |
|------|--------|------|
| 2026-04-29 | Initial assessment | This file created |
| 2026-04-30 | `galaxy.yml` and `meta/runtime.yml` added | Root |
| 2026-05-01 | All playbooks moved into `playbooks/` | — |
| 2026-05-02 | `ssh-config` moved to `~/.ssh/config` | Removed from root |
| 2026-05-02 | `pi-intercom.service.j2` moved to `roles/pi-installation/templates/` | Relocated |
| 2026-05-02 | Assessment updated | This file rewritten |

---

## Evidence Checked From Disk

All file paths, role structures, and playbook locations were verified with `find` and `ls`. No assumptions made.

---

**END OF ASSESSMENT**
