---
status: in-progress
version: 0.3.1
last_updated: 2026-05-30
---

# PLAN — pi-cross-node-comms v0.3.1

## Release: Fleet Validation Power-Down/Restart Test

### Objective

Verify that all fleet configuration changes from v0.2.0 (bug fixes) and v0.3.0 (idle CPU burn fix + NFS) persist across a full power cycle.

### Test Plan

| Step | Action | Validation |
|------|--------|------------|
| 1 | Power off all 7 fleet nodes | `ssh fnet{1..7} sudo poweroff` |
| 2 | Wait 30s for full shutdown | All nodes unreachable |
| 3 | Power on all 7 nodes | Physical button press or WOL |
| 4 | Wait 2-3 min for boot | All nodes respond to SSH |
| 5 | Validate NFS mount | `/mnt/carlos-desktop` mounted, read+write |
| 6 | Validate Ollama idle | No runner loaded, `KEEP_ALIVE=0` |
| 7 | Validate pi agents | systemd `active`, no `--model` flag |
| 8 | Validate fan cooling | `cur_state=max_state` for all Fan devices |
| 9 | Validate CPU governor | `powersave` on all nodes |
| 10 | Validate temperatures | Under 55°C at idle within 5 min |
| 11 | Run Ansible validation | `phase0-nfs-mount.yml` (idempotent) |
| 12 | Run Ansible validation | `phase6-fleet-validation.yml` |

### Persistence Concerns

| Config | Persist Method | Risk |
|--------|---------------|------|
| NFS fstab entry | `/etc/fstab` | ✅ Persists across reboot |
| Ollama override | `/etc/systemd/system/ollama.service.d/override.conf` | ✅ Persists |
| Pi agent unit (no --model) | `/etc/systemd/system/pi-cross-node-agent@*.service` | ✅ Persists |
| OLLAMA_KEEP_ALIVE in agent unit | systemd Environment directive | ✅ Persists |
| defaultModel removed from settings.json | File edit | ✅ Persists |
| Fan cooling `cur_state` | Runtime sysfs only | ❌ Resets to 0 on reboot |
| CPU governor `powersave` | Runtime sysfs only | ❌ May reset to `performance` |
| pi-agent-standalone.sh changes | File edit on each node | ✅ Persists |

### Items to Add to Ansible for Persistence

- [ ] Fan cooling activation task in fleet validation phase
- [ ] CPU governor check/set task in fleet validation phase
- [ ] Consider systemd udev rules or sysfs persistence for fan/governor

### Known Operational Notes

- Phase 6 "Wait for agents to register" may need extended timeout after cold boot
- fnet3–fnet7 have broken ACPI passive thermal trip points (-274°C) — cosmetic, not functional
- NFS `-mapall=501:20` on macOS is mutually exclusive with `-maproot`

### Previous Release (v0.3.0)

See [PLAN.md v0.2.0](./PLAN.md) for the bug fix release notes.