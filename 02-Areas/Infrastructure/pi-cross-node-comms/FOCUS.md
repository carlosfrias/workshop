---
status: released
version: 0.3.0
last_updated: 2026-05-30
phase: Fleet idle CPU burn fix released to upstream main
---

# FOCUS — pi-cross-node-comms

## Current Focus

Fleet idle CPU burn fix. All 7 nodes were running qwen3.5:4b at 580-600% CPU even with no tasks, causing thermal stress (up to 99°C on fnet7). Root cause identified and fixed.

### Session 2026-05-30 — Fleet Idle CPU Burn Fix

**Root Cause:** The systemd unit template hardcoded `--model ollama/qwen3.5:4b`, which caused pi to immediately load and hold a persistent streaming connection to Ollama. The Ollama runner burned 100% CPU per core indefinitely because Ollama cannot unload the model while a client holds an open HTTP connection — even with `OLLAMA_KEEP_ALIVE=0` (known bug [ollama#7645](https://github.com/ollama/ollama/issues/7645)). Additionally, `.pi/agent/settings.json` on some nodes had `defaultModel` set, overriding the model-router.

**Additional finding:** fnet7 had its CPU governor set to `performance` instead of `powersave`, and all fan cooling devices were stuck at state 0 (off) on fnet3–fnet7 despite temperatures reaching 84–99°C.

**Fixes applied:**
1. Removed `--model ollama/qwen3.5:4b` from systemd unit template — pi now uses model-router for on-demand model selection
2. Removed `defaultModel` from `.pi/agent/settings.json` on all fleet nodes
3. Set `INITIAL_PROMPT_ENABLED=false` in pi-agent-standalone.sh — prevents model load on startup
4. Added `OLLAMA_KEEP_ALIVE=0` to systemd unit template and ollama service override
5. Set fan cooling devices to max on fnet3–fnet7
6. Fixed fnet7 CPU governor from `performance` to `powersave`
7. Added ollama-idle-unload watchdog script (safety net, currently disabled)
8. Added Ollama keep-alive override to phase3-ollama-models.yml Ansible playbook

**Results:** All 7 nodes went from 580-600% CPU idle burn to 0% (no Ollama runner loaded). Temperatures dropped dramatically:

| Node | Before | After | Δ |
|------|--------|-------|---|
| fnet1 | 49.5°C | 49.5°C | — |
| fnet2 | 56.0°C | 37.0°C | -19°C |
| fnet3 | 86.0°C | 41.0°C | -45°C |
| fnet4 | 91.0°C | 44.0°C | -47°C |
| fnet5 | 90.0°C | 47.0°C | -43°C |
| fnet6 | 93.0°C | 63.0°C | -30°C |
| fnet7 | 99.0°C | 60.0°C | -39°C |

## Active Work

- [x] Remove --model flag from systemd unit template
- [x] Remove defaultModel from settings.json on all nodes
- [x] Set OLLAMA_KEEP_ALIVE=0 in systemd unit and ollama override
- [x] Set INITIAL_PROMPT_ENABLED=false in pi-agent-standalone.sh
- [x] Fix fnet7 CPU governor to powersave
- [x] Force fan cooling devices on fnet3–fnet7
- [x] Add ollama-idle-unload.sh watchdog (safety net)
- [x] Add Ollama keep-alive override to phase3 playbook
- [x] Commit and push all changes to upstream main

## Next Steps

1. Run full fleet standup with updated playbooks to verify end-to-end
2. Verify model-router correctly selects models when coms-net tasks arrive
3. Remove `defaultModel` from Ansible-deployed settings template (if one exists)
4. Add fan cooling device configuration to fleet standup playbooks
5. Add CPU governor check (ensure `powersave`) to fleet validation phase

## Blockers

None

## Quality Checks

- [x] All ansible playbooks pass `--syntax-check`
- [x] pi_version_target matches latest npm release (0.77.0)
- [x] No unbalanced parentheses in when-clauses
- [x] systemctl status reports use `'active'` not `'running'`
- [x] deploy-fleet.yml has valid YAML structure
- [x] All 7 fleet nodes confirmed IDLE with no Ollama runners

## Key Files

| File | Purpose |
|------|---------|
| `ansible/standup-fleet.yml` | Full fleet standup (6 phases) |
| `ansible/phase3-ollama-models.yml` | Ollama + models + keep-alive override |
| `ansible/phase5-agent-services.yml` | Systemd agent launch |
| `ansible/systemd/pi-cross-node-agent@.service.template` | Agent unit (no --model) |
| `ansible/systemd/pi-agent-standalone.sh` | Agent wrapper (no initial prompt) |
| `ansible/systemd/ollama-idle-unload.sh` | Watchdog safety net |
| `ansible/systemd/pi-cross-node-agent.conf` | Per-node env file |

---

*Last updated: 2026-05-30*