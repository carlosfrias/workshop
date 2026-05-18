# Phase 2: Planning

**Purpose:** Framework readiness check, complexity assessment, decomposition decision.
**When to load:** After domain is activated, before execution begins.
**Target model:** qwen3:8b

---

## Publishing Workflow (if applicable)

This workspace is the **factory** for extensions, skills, and agents.

### Quality Gates Before Publishing

- [ ] Extension/skill works in isolation (no workspace-specific dependencies)
- [ ] README.md includes installation instructions
- [ ] package.json has correct name, version, repository, license
- [ ] Config files use namespaced paths
- [ ] Keybinding namespaces are unique
- [ ] Event names are namespaced

## Planning Quality Gates

Before starting multi-step work:

1. **Is the task simple (<3 steps, single domain)?** → Proceed directly to Phase 3 (Execution)
2. **Is the task complex (≥3 steps or multi-domain)?** →
   - Run `classify_prompt.py` to assess complexity
   - If MEDIUM/HARD with ≥2 domains → decomposition trigger written automatically
   - Wait for `decompose-watcher.py` to process (or run `--once`)
   - Review sub-tasks before dispatch
3. **Does the task touch ≥2 nodes?** → Verify TI-011 framework (see checks below)

## TI-011 Meta-Orchestration Conventions

### Architecture
```
Prompt → Classify → Decompose → Match → Submit → Execute → Collect → Synthesize
```

### Routing Rules
- Classify first (1ms heuristic, qwen3.5:4b)
- Decompose if MEDIUM/HARD (cloud, ~8s)
- Match sub-tasks to local models (qwen3.5:4b, qwen3:8b, gemma4:e4b)
- Submit to nodes via SSH/NFS queue
- Collect results, synthesize, verify with cloud if needed

### Data Sources
- `lab-specs/node-capacity-summary.json` — node × model matrix
- `lab-specs/node-hardware/` — per-node CPU/RAM/disk
- `lab-specs/node-benchmarks/` — tokens/sec per model per node
- `~/.pi/agent/models.json` — cloud model definitions

### When to Re-run Detection + Benchmarking
- After any node hardware change
- After Ollama version upgrade
- After model pull/remove
- Weekly (automated via cron)

### Performance Logging (Required)
Every routing decision MUST log:
- Prompt preview (first 50 chars)
- Complexity classification + confidence
- Model selected + node assigned
- Latency (ms) + cost ($)
- Success/failure + reason if failed

Log file: `wiki/operational/sessions/model-routing-decisions.jsonl`

## Framework Readiness Check (Mandatory Before Multi-Node Work)

Before any infrastructure task touching ≥2 nodes, verify TI-011:

| Check | Command | Expected Result |
|-------|---------|-----------------|
| **Orchestrator health** | `python3 scripts/orchestrator_health.py --json` | Status: healthy (RAM <80%, Swap =0) |
| Extension installed | `ls ~/.pi/agent/extensions/pi-keyword-router/index.ts` | File exists |
| Classifier functional | `python3 scripts/classify_prompt.py --help` | Returns usage |
| Node registry functional | `python3 scripts/ti011_node_registry.py --help` | Returns usage |
| Submitter functional | `python3 scripts/submit_task.py --help` | Returns usage |
| Lab nodes reachable | `ansible -i ansible/inventory.yml lab_nodes -m ping` | All green |

**Health Thresholds (Mac M4 Pro, 24GB RAM, 14 cores):**

| Metric | Healthy | Stressed | Critical | Action |
|--------|---------|----------|----------|--------|
| RAM % | <80% | 80-92% | >92% | Decompose + offload |
| CPU load | <4.0 | 4.0-6.0 | >6.0 | Decompose + offload |
| Swap used | 0 | 0 | >0 | **IMMEDIATE offload** |

**If health check returns "critical" or "stressed":**
- **Decomposition is automatic** — do not proceed with local execution
- **Route to cloud models** — use `ollama-cloud/qwen3.5:397b` or higher tier
- **Log the decision** — append to `wiki/operational/sessions/health-decisions.jsonl`

**If any other check fails:** Stop. Fix framework before proceeding.

**Single-node exceptions:** Direct SSH permitted for bootstrap, emergency repair, or post-work verification only.

## Next Phase

After planning is complete, load **Phase 3: Execution** (`phase-3-execution.md`).
