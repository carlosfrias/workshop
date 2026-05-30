---
status: testing
version: 0.3.1
last_updated: 2026-05-30
phase: Full power-down/restart fleet validation test
---

# FOCUS — pi-cross-node-comms

## Current Focus

**Full fleet power-down and restart validation test.** All fixes from sessions 2026-05-29 and 2026-05-30 need end-to-end verification after a cold reboot. This tests that NFS mounts, Ollama config, systemd units, and fan/governor settings all survive a reboot.

### Session 2026-05-30 — Fleet Validation Power-Down/Restart Test

**Objective:** Verify that all fleet config changes persist across a full power cycle by shutting down all 7 fleet nodes, restarting them, and validating:

1. **NFS mount** — `/mnt/carlos-desktop` auto-mounts from fstab and is read/write
2. **Ollama idle** — No Ollama runner loaded at idle, `OLLAMA_KEEP_ALIVE=0` in effect
3. **Pi agents** — systemd services start, no `--model` flag, agents connect to hub
4. **Fan cooling** — Fan devices at `cur_state=max_state` (not 0)
5. **CPU governor** — Set to `powersave` (not `performance`)
6. **Temperatures** — All nodes under 55°C at idle within 5 minutes of boot

**Prerequisites completed:**
- [x] Fleet idle CPU burn fix (removed `--model`, `defaultModel`, initial prompt)
- [x] `OLLAMA_KEEP_ALIVE=0` set in systemd and ollama override
- [x] NFS mounts configured on all 7 nodes with persistent fstab entries
- [x] Fan cooling devices set to max on fnet3–fnet7
- [x] CPU governor set to powersave on fnet7
- [x] All changes committed and tagged v0.3.0 in both repos

**Test plan:**
1. SSH into all 7 nodes and run `sudo shutdown -h now` (or `sudo poweroff`)
2. Wait 30 seconds after all nodes are down
3. Wake/power on all nodes (may require physical button press or WOL)
4. Wait 2-3 minutes for boot
5. SSH into each node and validate all 6 checks above
6. Run `ansible-playbook -i inventory.yml phase0-nfs-mount.yml` to verify idempotent NFS setup
7. Run `ansible-playbook -i inventory.yml phase6-fleet-validation.yml` for full validation

## Active Work

- [ ] Full power-down of all 7 fleet nodes
- [ ] Restart and validate NFS mounts persist
- [ ] Validate Ollama idle (no runner loaded)
- [ ] Validate pi-agent services start without `--model`
- [ ] Validate fan cooling devices active
- [ ] Validate CPU governor is powersave
- [ ] Validate temperatures under 55°C at idle

## Next Steps

1. Power down all fleet nodes: `for n in fnet{1..7}; do ssh $n sudo poweroff; done`
2. Wait, then power on (physical or WOL)
3. Run validation playbook against all nodes
4. If any config doesn't persist, add to Ansible playbooks for persistence

## Blockers

- Some nodes may not support Wake-on-LAN — may need physical power button press
- fnet3–fnet7 fan/governor settings are runtime-only and may not survive reboot unless added to systemd or sysfs rules

## Quality Checks

- [x] All ansible playbooks pass `--syntax-check`
- [x] pi_version_target matches latest npm release (0.77.0)
- [x] No unbalanced parentheses in when-clauses
- [x] systemctl status reports use `'active'` not `'running'`
- [x] deploy-fleet.yml has valid YAML structure
- [x] All 7 fleet nodes confirmed IDLE with no Ollama runners
- [x] NFS mounts verified read+write on all 7 nodes
- [ ] NFS mounts persist across reboot (PENDING TEST)
- [ ] Fan/governor settings persist across reboot (PENDING TEST)
- [ ] Pi agents start without model loading (PENDING TEST)

## Key Files

| File | Purpose | Must Be In Sync With |
|------|---------|----------------------|
| `ansible/phase0-nfs-mount.yml` | NFS mount for orchestrator workspace | Workshop + upstream |
| `ansible/systemd/pi-cross-node-agent@.service.template` | Agent systemd unit (**no --model**) | Workshop + upstream |
| `ansible/systemd/pi-agent-standalone.sh` | Agent wrapper (**no initial prompt**) | Workshop + upstream |
| `ansible/systemd/ollama-idle-unload.sh` | Watchdog (safety net, disabled by default) | Workshop + upstream |
| `ansible/phase3-ollama-models.yml` | Ollama + models + `OLLAMA_KEEP_ALIVE=0` override | Workshop + upstream |
| `ansible/standup-fleet.yml` | Full fleet standup (7 phases, incl. NFS) | Workshop + upstream |
| `FOCUS.md` | Current focus & status | Workshop only |

---

*Last updated: 2026-05-30*