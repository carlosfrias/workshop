# Phase 3: Orchestrator (Mac) Module

**Purpose:** Hardware-specific constraints and configuration for the Orchestrator Node.
**When to load:** When performing work that affects the Orchestrator (Mac M4 Pro) or updating model configurations.

---

## Hardware Specifications
- **Device:** Mac M4 Pro, 24GB RAM, 14 cores
- **Role:** Technical Infrastructure domain member. Treat with the same rigor as lab nodes.

## Model Configuration (TI-021)
The orchestrator's model configuration lives in `~/.pi/agent/models.json`. Keep in sync with the lab node philosophy: **only configured models should be available**.

**Fix Pattern for Ctrl+P Duplicates:**
1. Remove `pi-ollama-cloud` from `~/.pi/agent/settings.json` packages.
2. Create `~/.pi/agent/keyword-router.json` using `ollama` provider and `:cloud`-suffixed models.
3. Restart pi.
**Fix Script:** `scripts/fix-orchestrator-ctrl-p.py`

## Orchestrator Health Monitoring (TI-023)
Use `scripts/orchestrator_health.py` to prevent saturating the Mac during decomposition.

### Health Thresholds
| Metric | Healthy | Stressed | Critical |
| :--- | :--- | :--- | :--- |
| **RAM %** | <80% | 80-92% | >92% |
| **CPU load** | <4.0 | 4.0-6.0 | >6.0 |
| **Swap** | 0 | 0 | >0 |

### Routing Decisions (Automatic Offload)
| Status | Decompose On | Synthesize On |
| :--- | :--- | :--- |
| **Healthy** | Mac qwen3.5:4b | Mac gemma4:e4b |
| **Stressed** | fnet3 qwen3:8b | Mac gemma4:e4b |
| **Critical** | Cloud LOW | Cloud LOW |

**Critical Rule (TI-031):** If **Swap > 0**, execute **IMMEDIATE** cloud offload. Do not attempt local execution. Log decisions to `wiki/operational/sessions/health-decisions.jsonl`.

## Extension Management
1. Check `~/.pi/agent/settings.json` for packages that register models dynamically.
2. `~/.pi/agent/models.json` is the single source of truth.
3. Disable extensions that duplicate model registration.
4. Update `keyword-router.json` to match `models.json` provider/model IDs.

## Ansible Integration
When fixing lab nodes, always verify if the orchestrator needs the same fix. Include a `localhost` connection play or `post_tasks` to apply fixes to the orchestrator via `scripts/fix-orchestrator-ctrl-p.py` or similar.
