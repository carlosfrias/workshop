---
version: 3
date: 2026-05-30
session: 2026-05-30-fleet-idle-cpu-burn
status: active
trigger: All 7 fleet nodes running Ollama model at 580-600% CPU idle, causing thermal stress up to 99°C
supersedes: AGENTS-REFINED-v1.md
---

# AGENTS-REFINED-v2 — pi-cross-node-comms

## Battle-Tested Rules

### RULE 1: Workshop-First, Release-Through-Main

**Trigger:** Any code change to ansible playbooks, tests, scripts, or extension code.  
**Rule:** All code changes MUST originate in the workshop codebase (`workshop/02-Areas/Infrastructure/pi-cross-node-comms/`). The `.pi/agent/git/` clone is read-only — never edit files there directly. Changes reach `.pi` ONLY through `pi install`/`pi update` pulling from the GitHub `main` branch. No exceptions.

**The correct flow:**

```
workshop (develop) → git commit → git push origin main → pi update (consume)
```

**Never:**
- Edit files in `~/.pi/agent/git/` directly
- Create hotfix branches in `.pi`
- Copy workshop files to `.pi` as a shortcut

**Always:**
- Develop in workshop
- Commit to workshop repo
- Port functional changes to upstream repo via git push to `main`
- Verify `pi update` pulls the fix with no specifiers

### RULE 2: TDD for All Development

**Trigger:** Creating or modifying any code — Ansible playbooks, shell scripts, TypeScript, Python, config files, or any other executable or declarative artifact.  
**Rule:** Every change that affects behavior MUST have corresponding test coverage before or alongside the change. Tests live in the project's `tests/` directory.

### RULE 3: No Hardcoded Model in Fleet Agent Unit

**Trigger:** Modifying the pi-cross-node-agent systemd unit template or pi-agent-standalone.sh.  
**Rule:** The `--model` flag MUST NOT be hardcoded in the systemd unit. Pi must use the model-router for on-demand model selection. When `--model` is omitted, pi defers to the model-router's default profile, which loads models only when a task arrives and unloads them after inference (with `OLLAMA_KEEP_ALIVE=0`). Hardcoding `--model ollama/qwen3.5:4b` caused every fleet node to immediately load and hold a persistent streaming connection to Ollama, burning 580-600% CPU at idle (known Ollama bug: https://github.com/ollama/ollama/issues/7645).

**Substance:** Session 2026-05-30 found all 7 fleet nodes running at 580-600% CPU idle with temperatures reaching 99°C on fnet7. Root cause was `--model ollama/qwen3.5:4b` in the systemd unit + `defaultModel` in `.pi/agent/settings.json`. Removing both fixed the issue — models now load on-demand only.

**Correct:**
```ini
ExecStart=.../pi-agent-standalone.sh \
    --no-session \
    --extension .../src/index.ts \
    ...
```

**Wrong:**
```ini
ExecStart=.../pi-agent-standalone.sh \
    --model ollama/qwen3.5:4b \    # ❌ Forces immediate model load and persistent connection
    --no-session \
    --extension .../src/index.ts \
    ...
```

### RULE 4: OLLAMA_KEEP_ALIVE=0 on Fleet Nodes

**Trigger:** Deploying or configuring Ollama on any fleet node.  
**Rule:** Fleet nodes MUST set `OLLAMA_KEEP_ALIVE=0` in both the Ollama service override AND the pi-agent service environment. This ensures models unload immediately after inference. Without this, even brief pauses between requests keep models loaded.

**Required config on every fleet node:**
```ini
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_KEEP_ALIVE=0"
```

```ini
# In pi-cross-node-agent@.service template
Environment=OLLAMA_KEEP_ALIVE=0
```

**Substance:** Without `OLLAMA_KEEP_ALIVE=0`, models stay loaded for the default 5 minutes after each request. Combined with the persistent connection bug, they never unload.

### RULE 5: No Initial Prompt for Fleet Agents

**Trigger:** Modifying pi-agent-standalone.sh.  
**Rule:** The `INITIAL_PROMPT_ENABLED` flag MUST be `false` for fleet agents. Sending an initial prompt triggers pi to immediately load the model and establish a persistent Ollama connection, which prevents model unloading even with `OLLAMA_KEEP_ALIVE=0`.

**Substance:** The initial prompt "You are a coms-net fleet agent..." caused pi to immediately load the model on startup, defeating the purpose of on-demand model loading. The coms-net extension connects to the hub independently — no prompt is needed.

### RULE 6: Remove defaultModel from Fleet Settings

**Trigger:** Deploying pi to any fleet node.  
**Rule:** The `.pi/agent/settings.json` file on fleet nodes MUST NOT contain a `defaultModel` key. If pi finds `defaultModel`, it overrides the model-router and loads that model on startup. The model-router handles model selection; a hardcoded default re-introduces the idle CPU burn.

**Check on every deploy:**
```bash
# Remove defaultModel from settings.json
python3 -c "
import json
f = '/home/friasc/.pi/agent/settings.json'
with open(f) as fh: d = json.load(fh)
if 'defaultModel' in d: del d['defaultModel']; open(f,'w').write(json.dumps(d, indent=2))
"
```

**Substance:** Nodes fnet1 and fnet7 had `"defaultModel": "qwen3:8b"` in settings.json which overrode the model-router and caused immediate model loading even after removing `--model` from the systemd unit.

### RULE 7: Fan Cooling Devices Must Be Active on Intel NUCs

**Trigger:** Setting up or validating fleet nodes.  
**Rule:** All `Fan` cooling devices in `/sys/class/thermal/cooling_device*/` MUST be set to `cur_state=max_state`. Intel NUCs have a Linux ACPI bug where fan cooling devices default to state 0 (off) regardless of temperature. Without manual activation, fans never spin even at 90°C+.

**Required check in fleet validation:**
```bash
for cd in /sys/class/thermal/cooling_device*; do
  type=$(cat "$cd/type" 2>/dev/null)
  if [ "$type" = "Fan" ]; then
    max=$(cat "$cd/max_state 2>/dev/null")
    echo "$max" | sudo tee "$cd/cur_state" > /dev/null
  fi
done
```

**Substance:** All 7 fleet nodes had fans stuck at `cur_state=0` (off). fnet7 reached 99°C before this was discovered. This should be added to the fleet standup playbook (phase 6 validation).

### RULE 8: CPU Governor Must Be powersave on Fleet Nodes

**Trigger:** Fleet node setup or validation.  
**Rule:** All fleet nodes MUST have CPU governor set to `powersave`. The `performance` governor locks all cores at max frequency, dramatically increasing idle power consumption and heat. Found on fnet7 during this session.

**Required check:**
```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# Must output: powersave
# If not:
echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

### RULE 9: Fleet Node Health Check Items

**Trigger:** Diagnosing fleet node issues.  
**Rule:** When a fleet node is loud or hot, check these in order:
1. **Ollama runner process** — `pgrep -f "ollama runner"` — if present at idle, a model is loaded unnecessarily
2. **Pi→Ollama connections** — `ss -tnp | grep :11434 | grep pi` — persistent connections prevent model unloading
3. **Thermal zones** — `cat /sys/class/thermal/thermal_zone*/temp` — temperatures above 85°C are critical for NUCs
4. **Fan cooling devices** — `cat /sys/class/thermal/cooling_device*/cur_state` — must be at max_state, not 0
5. **CPU governor** — must be `powersave`, not `performance`
6. **OLLAMA_KEEP_ALIVE** — `cat /proc/$(pgrep -f 'ollama serve')/environ | tr '\0' '\n' | grep OLLAMA_KEEP_ALIVE` — must be 0
7. **defaultModel in settings.json** — must not exist

### Universal Rules (from root AGENTS.md)

These rules apply across ALL projects and were extracted from the 2026-05-29 session:

- **RULE 1:** Workshop-First, Release-Through-Main (same as this project's RULE 1)
- **RULE 2:** TDD for All Development (same as this project's RULE 2)
- **RULE 3:** Project-Level AGENTS.md Required
- **RULE 4:** Refined Agents Are Versioned and Mandatory

---

## Key Files

| File | Purpose | Must Be In Sync With |
|------|---------|----------------------|
| `ansible/systemd/pi-cross-node-agent@.service.template` | Agent systemd unit (**no --model**) | Workshop + upstream |
| `ansible/systemd/pi-agent-standalone.sh` | Agent wrapper (**no initial prompt**) | Workshop + upstream |
| `ansible/systemd/ollama-idle-unload.sh` | Watchdog (safety net, disabled by default) | Workshop + upstream |
| `ansible/phase3-ollama-models.yml` | Ollama + models + `OLLAMA_KEEP_ALIVE=0` override | Workshop + upstream |
| `ansible/standup-fleet.yml` | Full fleet standup (6 phases) | Workshop + upstream |
| `FOCUS.md` | Current focus & status | Workshop only |

## Discovery Path

```
1. carlos-desktop/AGENTS.md                           ← Root router
2. workshop/AGENTS.md                                 ← Workspace router
3. workshop/02-Areas/Infrastructure/AGENTS.md          ← Domain router
4. pi-cross-node-comms/AGENTS.md                      ← Project router
5. pi-cross-node-comms/FOCUS.md                       ← Current state
6. pi-cross-node-comms/refined-agents/AGENTS-REFINED-v3.md ← THIS FILE
```

---

*Created 2026-05-30 — refined from session 2026-05-30-fleet-idle-cpu-burn*
*Supersedes AGENTS-REFINED-v1.md (v1 rules still apply where not overridden)*