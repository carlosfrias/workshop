# Session: Fleet Maintenance & Cross-Node Fix
**Date:** 2026-05-24
**Workspace:** workshop/01-Projects/pi-cross-node-comms
**Models Used:** kimi-k2.6:cloud (primary), interacted with glm-5.1:cloud / gemma4:31b-cloud sessions
**Est. Cost:** ~$2-3 (fleet ops spanned multiple tool calls + SSH coordination)

## Summary
Fixed recurring cross-node comms binding issue + performed full fleet maintenance. Coordinated with parallel pi session to avoid interference with active 35b model deployment.

## Changes Made

### Code Changes (Persistent — Self-Healing)
| File | Change |
|------|--------|
| `server/coms-net-server.ts` | Default HOST `127.0.0.1` → `0.0.0.0`; added `isSafeToAutoToken()` for auto-token on LAN binds; added `detectLanIP()` for `public_url` |
| `scripts/standup-hub.sh` | Default HOST → `0.0.0.0`; updated docs |
| `ansible/systemd/pi-agent-standalone.sh` | Added `TMUX_TMPDIR="$HOME/.tmux"` to survive systemd-tmpfiles cleanup |

### Fleet Operations (One-Time)
- **LVM expanded:** fnet2 (156G→226G), fnet3 (20G→143G), fnet4 (21G→144G), fnet5 (21G→144G) — total +520GB
- **Partial blobs cleaned:** fnet3 (-20GB), fnet4 (-3GB)
- **Broken services removed:** `pi-agent.service` purged from fnet1, fnet3-7 (203/EXEC failures, /usr/local/bin/pi missing)
- **All agents restarted:** systemd `pi-cross-node-agent@*` services → connected to fnet2 hub

## Root Cause Analysis
1. **Hub localhost binding** → coms-net defaults were loopback-only
2. **Tmux socket loss** → `/tmp/tmux-*` cleaned by systemd-tmpfiles; now persistent in `$HOME/.tmux`
3. **LVM under-provisioning** → Ubuntu installer defaults to 100G LVs on 233G disks
4. **Orphaned service units** → old `pi-agent.service` remained alongside playbook's `pi-cross-node-agent@`

## Remaining Gaps
- **LVM expansion** not in Ansible playbook — new nodes still get 100G LVs (needs `lvextend` in standup-fleet.yml)
- **Partial blob cleanup** not automated — only surfaces during interrupted model pulls

## Coordination Notes
- Checked with `subagent-chat-019e59cc` (glm-5.1) via pi-intercom before any fleet work
- Other session was deploying qwen3.5:35b-a3b across fnet3-6 — held off during maintenance
- 35b pulls resumed autonomously after all-clear (fnet3 at 64%, others 2-15%)

## Next Steps
- Add `lvextend -l +100%FREE` + `resize2fs` to `standup-fleet.yml` to eliminate LVM gap
- **Build fleet health check script** — runs diagnostics in sequence and surfaces actionable items only. Checks: disk usage, LVM utilization, tmux socket persistence, hub connectivity, partial blob presence, ollama load status. Output: pass/fail per node with one-liner fix suggestions. Put in `scripts/fleet-health-check.sh` or as Ansible ad-hoc task.
