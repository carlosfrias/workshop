---
type: workbench
updated: 2026-05-30
---

# WORKBENCH — pi-cross-node-comms

## 🔨 Current Work

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | **Full fleet power-down/restart validation test** | 🟡 READY | All fixes from v0.3.0 need end-to-end verification after cold reboot |
| 2 | Add fan/governor persistence tasks to Ansible playbooks | ⏳ AFTER TEST | Fan `cur_state` and CPU governor are runtime-only, won't survive reboot |
| 3 | Run pi-multimodal-proxy test suite on fleet nodes via NFS | ⏳ AFTER TEST | Code now accessible via NFS mount at `/mnt/carlos-desktop` |

## ✅ Recently Done

| # | Task | Date | Result |
|---|------|------|--------|
| 1 | Fix fleet idle CPU burn (580-600% → 0%) | 2026-05-30 | ✅ All 7 nodes idle, temps dropped 18-47°C |
| 2 | Configure NFS workspace sharing | 2026-05-30 | ✅ All 7 nodes mounted read+write, fstab persistent |
| 3 | Release v0.3.0 | 2026-05-30 | ✅ Tagged and pushed to GitHub upstream |
| 4 | Update universal RULE 1 in root AGENTS.md | 2026-05-30 | ✅ .pi/agent/git is read-only cache, not upstream |
| 5 | Update refined-agents v3 | 2026-05-30 | ✅ RULE 10 (NFS), RULE 11 (sudo), RULE 1 fix |

## 📋 Next Agent Handoff

**Copy-paste this prompt to continue the fleet validation test:**

```
Resume the pi-cross-node-comms fleet validation test. All 7 fleet nodes (fnet1-fnet7) need a full power-down and restart to verify that NFS mounts, Ollama config, systemd units, fan cooling, and CPU governor settings persist across a reboot.

IMPORTANT CONTEXT — read these files first:
- /Users/friasc/Cloud/carlos-desktop/workshop/02-Areas/Infrastructure/pi-cross-node-comms/FOCUS.md
- /Users/friasc/Cloud/carlos-desktop/workshop/02-Areas/Infrastructure/pi-cross-node-comms/PLAN.md
- /Users/friasc/Cloud/carlos-desktop/workshop/02-Areas/Infrastructure/pi-cross-node-comms/refined-agents/AGENTS-REFINED-v3.md

TEST STEPS:
1. Power off all 7 nodes: for n in fnet{1..7}; do ssh -o ConnectTimeout=5 $n sudo poweroff; done
2. Wait 30s, then verify all nodes are down (SSH unreachable)
3. Power on — check if Wake-on-LAN works: for n in fnet{1..7}; do wakeonlan $(ssh $n cat /etc/hostname 2>/dev/null)-mac 2>/dev/null; done. If WOL fails, ask Carlos to physically press the power button on each node.
4. Wait 2-3 min for boot, then SSH into each node and validate:
   a. NFS mount: mountpoint -q /mnt/carlos-desktop && touch /mnt/carlos-desktop/workshop/.test
   b. Ollama idle: pgrep -f "ollama runner" should return nothing
   c. Pi agent active: systemctl is-active pi-cross-node-agent@$(hostname)
   d. Fan cooling: for cd in /sys/class/thermal/cooling_device*; do [ "$(cat $cd/type)" = "Fan" ] && echo "$cd: $(cat $cd/cur_state)/$(cat $cd/max_state)"; done
   e. CPU governor: cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor should be "powersave"
   f. Temperature: paste /sys/class/thermal/thermal_zone*/temp (divide by 1000)
5. Run: cd workshop/02-Areas/Infrastructure/pi-cross-node-comms/ansible && ansible-playbook -i inventory.yml phase0-nfs-mount.yml (verify idempotent)
6. For any settings that DON'T persist (fan/governor), add systemd or udev rules to the Ansible playbooks.

KEY GOTCHAS (from AGENTS-REFINED-v3.md RULES 3-11):
- RULE 3: No hardcoded --model in systemd unit
- RULE 5: INITIAL_PROMPT_ENABLED must be false
- RULE 7: Fan cooling devices reset to cur_state=0 on reboot (NEEDS ANSIBLE TASK)
- RULE 8: CPU governor resets to "performance" on some nodes (NEEDS ANSIBLE TASK)
- RULE 10: NFS mount must use vers=3 (no v4), no "intr" option, mapall=501:20 on macOS
- RULE 11: Cannot use sudo on macOS orchestrator from pi agent — write script to /tmp/ and ask user to run it

FLEET INVENTORY: fnet1 (15Gi, 4-core), fnet2 (15Gi, 12-core, hub server), fnet3-fnet6 (31Gi, 12-core), fnet7 (15Gi, 12-core)
NFS: 192.168.0.154:/Users/friasc/Cloud/carlos-desktop → /mnt/carlos-desktop
HUB: fnet2:8080
```

## 📎 References

- [FOCUS.md](./02-Areas/Infrastructure/pi-cross-node-comms/FOCUS.md) — Current status
- [PLAN.md](./02-Areas/Infrastructure/pi-cross-node-comms/PLAN.md) — Test plan
- [AGENTS-REFINED-v3.md](./02-Areas/Infrastructure/pi-cross-node-comms/refined-agents/AGENTS-REFINED-v3.md) — Battle-tested rules
- [Root AGENTS.md](../../AGENTS.md) — Universal rules (RULE 1 updated: .pi is NOT upstream)