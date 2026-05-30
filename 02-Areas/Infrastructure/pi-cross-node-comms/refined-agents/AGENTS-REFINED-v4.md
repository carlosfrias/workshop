---
version: 4
date: 2026-05-29
session: 2026-05-29-fleet-model-loading-root-cause
status: active
trigger: Fleet nodes loading models at idle despite --model, defaultModel, and initial prompt all removed
supersedes: AGENTS-REFINED-v3.md (RULE 6 revised, RULES 12-14 added)
---

# AGENTS-REFINED-v4 — pi-cross-node-comms

## New Rules (This Session)

### RULE 12: pi-model-router Extension Required on Fleet Nodes

**Trigger:** Deploying or configuring pi on any fleet node.

**Rule:** The `npm:@yeliu84/pi-model-router` extension MUST be installed on every fleet node. Without it, pi's native fallback chain auto-selects and loads a model at startup:

1. `buildSessionOptions` — selects `enabledModels[0]` from settings.json
2. `findInitialModel` — selects `modelRegistry.getAvailable()[0]` from models.json

Both fallbacks result in a local Ollama model being loaded into GPU immediately at startup, causing idle CPU burn. The model-router extension manages model selection at the turn level (not session level), so models only load when a task actually requires inference.

**Required in Ansible:** Phase 2.5 (`phase2.5-model-router.yml`) installs the extension and sets defaultModel. This runs in Chain 2 after Pi install (Phase 2) and before agent startup (Phase 5).

**Substance:** Sessions 2026-05-29 and 2026-05-30 — the prior fix (removing --model, defaultModel, initial prompt) was incomplete. After a full reboot, models loaded again because pi's native fallback selected `enabledModels[0]` (qwen3.5:4b). Installing the model-router + setting defaultModel to medium tier model eliminated all auto-loading.

### RULE 13: defaultModel Required in Fleet Settings

**Trigger:** Configuring `settings.json` on any fleet node.

**Rule:** Fleet nodes MUST have `defaultModel` set in settings.json. Without it, `findInitialModel` in sdk.js falls through to `modelRegistry.getAvailable()[0]`, which selects the first local Ollama model and loads it into GPU.

Set `defaultModel` to the medium-tier model from the model-router profile (currently `openbmb/minicpm-o2.6:8b` for all tiers). This satisfies pi's startup model selection without triggering GPU loading, because the model-router intercepts at the turn level for actual inference.

**Revision of RULE 6 (v3):** RULE 6 previously said "Remove defaultModel from Fleet Settings." This was WRONG. Removing defaultModel removes the guardrail and exposes pi's fallback to `getAvailable()[0]`. The correct rule is: SET defaultModel to prevent fallback auto-selection. The original issue (RULE 6 was created because defaultModel was set to `qwen3:8b` causing CPU burn) was not about having defaultModel — it was about which model it pointed to. With the model-router managing turn-level selection, defaultModel acts as a session startup guardrail, not a permanent model assignment.

**Substance:** This session traced pi's source code (main.js → sdk.js → model-resolver.js) to identify all model auto-selection code paths. The two-layer fallback was designed for interactive pi sessions where cloud models don't trigger local GPU loading. On fleet nodes with only local models, both fallbacks trigger immediate model loading.

### RULE 14: Fan/Governor Persistence via Systemd Oneshot

**Trigger:** Fleet node setup or validation.

**Rule:** Fan cooling devices and CPU governor are sysfs runtime settings that reset on every reboot. Use a systemd oneshot service (`fleet-cooling.service`) to re-apply them on boot. This service must be:
- Type: oneshot, RemainAfterExit: yes
- After: multi-user.target
- WantedBy: multi-user.target
- ExecStart: a script that sets all Fan cooling devices to max_state and CPU governor to powersave

**Deployed via Ansible Phase 5** (`phase5-agent-services.yml`) alongside other systemd units.

**Substance:** fnet7's governor resets to "performance" on reboot; all nodes' fans reset to cur_state=0. Without this service, every reboot requires manual intervention to prevent thermal issues.

## Existing Rules (from v3 — still active)

### RULE 1: Workshop-First, Release-Through-GitHub-Upstream

**Trigger:** Any code change to ansible playbooks, tests, scripts, or extension code.

**Rule:** All code changes MUST originate in the workshop codebase. The `~/.pi/agent/git/` clones are read-only caches — they are NOT the upstream repository. The upstream is the project's GitHub repository (e.g., `carlosfrias/pi-cross-node-comms`). The `.pi` cache is updated ONLY through `pi install`/`pi update` pulling from GitHub `main`. No exceptions.

### RULE 2: TDD for All Development

**Trigger:** Creating or modifying any code.
**Rule:** Every change that affects behavior MUST have corresponding test coverage.

### RULE 3: No Hardcoded Model in Fleet Agent Unit

**Trigger:** Modifying the pi-cross-node-agent systemd unit template.
**Rule:** The `--model` flag MUST NOT be hardcoded in the systemd unit.

### RULE 4: OLLAMA_KEEP_ALIVE=0 on Fleet Nodes

**Trigger:** Deploying or configuring Ollama on any fleet node.
**Rule:** Fleet nodes MUST set `OLLAMA_KEEP_ALIVE=0` in both the Ollama service override AND the pi-agent service environment.

### RULE 5: No Initial Prompt for Fleet Agents

**Trigger:** Modifying pi-agent-standalone.sh.
**Rule:** The `INITIAL_PROMPT_ENABLED` flag MUST be `false` for fleet agents.

### RULE 7: Fan Cooling Devices Must Be Active on Intel NUCs

**Trigger:** Setting up or validating fleet nodes.
**Rule:** All `Fan` cooling devices in `/sys/class/thermal/cooling_device*/` MUST be set to `cur_state=max_state`. (See RULE 14 for persistence across reboots.)

### RULE 8: CPU Governor Must Be powersave on Fleet Nodes

**Trigger:** Fleet node setup or validation.
**Rule:** All fleet nodes MUST have CPU governor set to `powersave`. (See RULE 14 for persistence across reboots.)

### RULE 9: Fleet Node Health Check Items

**Trigger:** Diagnosing fleet node issues.
**Rule:** Check in order: 1) Ollama runner, 2) Pi→Ollama connections, 3) Thermal zones, 4) Fan cooling devices, 5) CPU governor, 6) OLLAMA_KEEP_ALIVE, 7) defaultModel in settings.json.

### RULE 10: NFS Mount for Orchestrator Workspace

**Trigger:** Fleet node setup or standup.
**Rule:** All fleet nodes MUST mount the macOS orchestrator's workspace directory via NFS.

### RULE 11: sudo Requires Terminal on macOS Orchestrator

**Trigger:** Any task that requires `sudo` on the macOS host.
**Rule:** Write a shell script to `/tmp/` and ask the user to run `sudo bash /tmp/script.sh` in their terminal.

## Revised Rules (from v3 — corrected this session)

### ~~RULE 6~~ → RULE 13 (REVISED): defaultModel Required, Not Removed

**Old rule:** "Remove defaultModel from Fleet Settings"
**New rule:** RULE 13 — Set defaultModel to prevent fallback auto-selection. Removing it exposes pi's fallback to `getAvailable()[0]`.

## Discovery Path

```
1. carlos-desktop/AGENTS.md                           ← Root router
2. workshop/AGENTS.md                                 ← Workspace router
3. workshop/02-Areas/Infrastructure/AGENTS.md          ← Domain router
4. pi-cross-node-comms/AGENTS.md                      ← Project router
5. pi-cross-node-comms/refined-agents/AGENTS-REFINED-v4.md ← THIS FILE
```

---

*Created 2026-05-29 — refined from session 2026-05-29-fleet-model-loading-root-cause*
*Supersedes AGENTS-REFINED-v3.md (RULE 6 revised, RULES 12-14 added)*
