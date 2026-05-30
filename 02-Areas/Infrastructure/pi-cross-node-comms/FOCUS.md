---
status: active
version: 0.3.1
last_updated: 2026-05-29
phase: Monitoring + remaining persistence tasks
---

# FOCUS — pi-cross-node-comms

## Current Focus

**Fleet idle CPU burn is FIXED.** All 7 nodes verified at 0 models, 0 runners after full standup + reboot. Monitoring needed. Remaining tasks: fan/governor TDD tests, model-router integration verification with coms-net tasks.

### Session 2026-05-29 — Root Cause Fix for Model Auto-Loading

**Status: COMPLETE ✅**

**Root cause:** Fleet nodes missing `pi-model-router` extension and `defaultModel` setting. Pi's two-layer fallback (buildSessionOptions → findInitialModel → getAvailable()) auto-selected first local model on startup.

**Fix:**
- Installed `npm:@yeliu84/pi-model-router` on all 7 nodes
- Set `defaultModel: "openbmb/minicpm-o2.6:8b"` (medium tier)
- Added `fleet-cooling.service` systemd oneshot for fan/governor persistence
- Updated Ansible: phase2.5-model-router.yml in Chain 2, cooling in Phase 5

**Validated:** Full standup with reboot — all 7 nodes: 0 models, 0 runners, agents active, cooling on, governor powersave.

## Active Work

- [ ] Monitor fleet nodes for 24h — confirm idle CPU stays at 0%
- [ ] Verify model-router selects correct tier models when coms-net tasks arrive
- [ ] Write TDD tests for fan/governor persistence (fleet-cooling service)
- [ ] Update pi-cross-node-comms AGENTS.md to reference v4 refined agent

## Next Steps

1. Monitor fleet nodes via SSH — check models/runners/temps periodically
2. Run actual coms-net task to verify model-router selects correct tier
3. Write TDD tests for fleet-cooling service
4. Update project AGENTS.md to link AGENTS-REFINED-v4.md

## Quality Checks

- [x] All ansible playbooks pass `--syntax-check`
- [x] Full standup validated with reboot (all 7 nodes: 0 models, 0 runners)
- [x] Workshop + upstream repos committed and pushed
- [x] v0.3.1 tagged on upstream
- [ ] TDD tests for fleet-cooling service (PENDING)
- [ ] Coms-net task routing with model-router (PENDING)

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