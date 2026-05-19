# Orchestrator Node Conventions

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/orchestrator-conventions.md`

The orchestrator (Mac M4 Pro, 24GB RAM) is **part of the technical-infrastructure domain** and must be treated with the same rigor as lab nodes. Work done on lab nodes **must include the orchestrator** when the same issue applies.

## Model Configuration

The orchestrator's model configuration lives in `~/.pi/agent/models.json` and must be kept in sync with the lab node philosophy: **only configured models should be available**.

### Problem Pattern (TI-021)

The `pi-ollama` extension dynamically registers cloud models (without `:cloud` suffix) under the `ollama` provider. These models appear in Ctrl+P alongside the manually-configured models in `models.json` (with `:cloud` suffix under `ollama` provider), creating duplicates and confusion.

### Solution

1. Remove `pi-ollama` from `~/.pi/agent/settings.json` packages
2. Create `~/.pi/agent/keyword-router.json` using `ollama` provider and `:cloud`-suffixed models (matching `models.json`)
3. Restart pi

### Fix Script

`scripts/fix-orchestrator-ctrl-p.py`:
- Backs up `settings.json`
- Removes `pi-ollama` extension reference
- Creates `keyword-router.json` with correct provider/model mappings
- Prints verification of models in `models.json`

## Orchestrator Health Monitoring

Unlike lab nodes, the orchestrator previously had **no health monitoring** (TI-023). This caused decomposition tasks to run locally even when the Mac was under pressure.

### Health Check Script

```bash
python3 scripts/orchestrator_health.py        # human-readable
python3 scripts/orchestrator_health.py --json # JSON output
```

### Thresholds (Mac M4 Pro, 24GB RAM, 14 cores)

| Metric | Healthy | Stressed | Critical |
|--------|---------|----------|----------|
| RAM % | <80% | 80-92% | >92% |
| CPU load | <4.0 | 4.0-6.0 | >6.0 |
| Swap | 0 | 0 | >0 |

### Routing Impact

| Orchestrator Status | Decompose On | Synthesize On |
|---------------------|-------------|---------------|
| healthy | Mac qwen3.5:4b | Mac gemma4:e4b |
| stressed | fnet3 qwen3:8b | Mac gemma4:e4b |
| critical | Cloud LOW | Cloud LOW |

## Extension Management on Orchestrator

Extensions installed on the orchestrator affect all sessions. When fixing model-related issues:

1. Check `~/.pi/agent/settings.json` for packages that register models dynamically
2. Verify `~/.pi/agent/models.json` is the single source of truth for model availability
3. Remove or disable extensions that duplicate model registration
4. Update `keyword-router.json` to match `models.json` provider/model IDs

## Ansible Inclusion

When creating Ansible playbooks that fix model or configuration issues on lab nodes, **always check if the orchestrator needs the same fix**. The orchestrator is not in the `lab_nodes` inventory but should be documented in the playbook's `post_tasks` or a separate `orchestrator` play.

### Example Pattern

```yaml
- name: Fix Ctrl+P Model Cycling
  hosts: lab_nodes
  tasks:
    - name: Remove extra ollama models
      shell: ollama list | grep -v ... | xargs ollama rm

- name: Fix Ctrl+P on Orchestrator
  hosts: localhost
  connection: local
  tasks:
    - name: Run orchestrator fix script
      command: python3 scripts/fix-orchestrator-ctrl-p.py
```

---

**Related:** [TI-011 Orchestration](ti011-orchestration.md) | [Ansible Testing](ansible-testing.md)
