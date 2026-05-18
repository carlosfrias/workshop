# TI-011 Orchestration Framework Testing Harness

**File:** `technical-infrastructure/scripts/test_orchestration_harness.py`  
**Lines:** 818  
**Tests:** 54  
**Last Run:** 2026-05-03 — 54/54 passing  
**Status:** Ready for manual and CI/CD execution  

---

## Why This Exists

The TI-011 meta-orchestration framework has 11+ Python scripts, a TypeScript extension, 7 lab nodes, and multiple interdependent components. Before this harness, **zero automated tests** existed. A single edit to `classify_prompt.py` could silently break downstream `submit_task.py` — no one would know until the user typed a prompt.

This harness validates **every** component end-to-end without requiring user interaction.

---

## Test Architecture

```
test_orchestration_harness.py
    ├── test_classifier_suite (6 tests)
    │   ├── heuristic_classify for TRIVIAL, SIMPLE, MEDIUM, HARD
    │   ├── routing info attachment from NodeRegistry
    │   └── inject_complexity_tag() output validation
    ├── test_registry_suite (5 tests)
    │   ├── Load all 7 nodes from lab-specs
    │   ├── best_model_for(trivial/simple/medium/hard)
    │   ├── match_subtask_to_local()
    │   └── dump() without errors
    ├── test_health_suite (3 tests)
    │   ├── orchestrator_health.py JSON output
    │   ├── check_health() importable from Python
    │   └── Integration into classify_prompt
    ├── test_submit_suite (2 tests)
    │   ├── Task JSON generation
    │   └── Dry-run vs live mode gate
    ├── test_decompose_suite (5 tests)
    │   ├── decompose_llm.py dry-run
    │   ├── validate_decomposition()
    │   ├── Trigger directory tree
    │   ├── Manual trigger write
    │   └── watcher --list-pending
    ├── test_collect_suite (3 tests)
    │   ├── task-collect-results.py subprocess
    │   ├── Report JSON validity
    │   └── Execution verification
    ├── test_synthesize_suite (2 tests)
    │   ├── Result combination
    │   └── PLAN update
    ├── test_extension_suite (10 tests)
    │   ├── keyword-router.json validation
    │   ├── package.json validation
    │   ├── index.ts source files
    │   ├── complexity-router.json validation
    │   ├── P0 dispatch bridge (dispatchToLab)
    │   ├── P0 health cache (getOrchestratorHealth)
    │   ├── P1 commands (5 commands registered)
    │   ├── P0 skipPythonClassifier flag
    │   └── P0 router skip method
    └── test_node_health_suite (14 tests)
        ├── SSH reachability for fnet1-fnet7
        └── Ollama response for fnet1-fnet7
```

---

## Coverage Matrix

| Component | File | Tests | Validated |
|-----------|------|-------|-----------|
| Classifier | `classify_prompt.py` | 6 | ✅ |
| Node Registry | `ti011_node_registry.py` | 5 | ✅ |
| Health Check | `orchestrator_health.py` | 3 | ✅ |
| Task Submit | `submit_task.py` | 2 | ✅ |
| Decomposer | `decompose_llm.py`, `decompose-watcher.py` | 5 | ✅ |
| Result Collector | `task-collect-results.py` | 3 | ✅ |
| Synthesizer | `synthesize_results.py` | 2 | ✅ |
| Extension | `pi-keyword-router/*.ts` | 10 | ✅ |
| Node Health | SSH + Ollama | 14 | ✅ |
| **Total** | | **54** | **54/54** |

---

## Prerequisites

- Python 3.14.4 (workspace `.venv` activated)
- SSH key auth to `friasc@fnet1` through `friasc@fnet7`
- `ansible/inventory.yml` present (for node health tests)
- For `--live` mode: all 7 nodes must be reachable

---

## Quick Start

### 1. Safe Dry-Run (No Network)

```bash
cd ~/Dropbox/workshop
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all
```

**Output:** 54/54 passed in ~10 seconds. No SSH, no SCP, no remote access.

### 2. Verbose Output

```bash
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --verbose
```

Shows every test with latency and detail fields.

### 3. Generate Report

```bash
python3 technical-infrastructure/scripts/test_orchestration_harness.py \
    --all --report \
    --output wiki/operational/sessions/test-report-$(date +%Y%m%d-%H%M).md
```

Produces a machine-readable markdown report with summary table and per-test details.

### 4. Live Mode (Real SSH/SCP)

⚠️ Only run when nodes are on-premise and known healthy.

```bash
python3 technical-infrastructure/scripts/test_orchestration_harness.py \
    --all --live --verbose
```

---

## CLI Reference

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--all` | `false` | Run all test suites |
| `--classify` | `false` | Test `classify_prompt.py` |
| `--registry` | `false` | Test `ti011_node_registry.py` |
| `--health` | `false` | Test `orchestrator_health.py` |
| `--submit` | `false` | Test `submit_task.py` |
| `--decompose` | `false` | Test decomposition pipeline |
| `--collect` | `false` | Test `task-collect-results.py` |
| `--synthesize` | `false` | Test `synthesize_results.py` |
| `--extension` | `false` | Test extension config |
| `--node-health` | `false` | SSH + Ollama health on all nodes |
| `--report` | `false` | Generate markdown report |
| `--output PATH` | `wiki/report.md` | Report file path |
| `--verbose` | `false` | Show test details |
| `--live` | `false` | Run with actual SSH/SCP |

### Common Combinations

| Goal | Command |
|------|---------|
| Validate a `classify_prompt.py` change | `--classify` |
| Validate extension changes | `--extension` |
| Pre-deployment health check | `--node-health --verbose` |
| CI/CD gate (minimal) | `--all --report --output ci-report.md` |
| Full validation | `--all --live --verbose` |

---

## Interpretation Guide

### When a Test Fails

| Test | Likely Cause | Fix |
|------|------------|-----|
| `extension: repo config valid` | `keyword-router.json` malformed | Check JSON syntax |
| `extension: P0 dispatch bridge` | Install path mismatch | Re-run `pi install` or symlink |
| `health: fnet3 SSH reachable` | Node offline or SSH key missing | Check VPN, `ssh friasc@fnet3 hostname` |
| `health: fnet3 Ollama responding` | Ollama service down | `ssh friasc@fnet3 "sudo systemctl status ollama"` |
| `classify: routing info` | `classify_prompt.py --route` broke | Check NodeRegistry imports |
| `registry: load all nodes` | Lab spec JSONs missing | Re-run hardware detection |
| `collect: subprocess` | `task-collect-results.py` syntax error | `python3 -m py_compile` |

---

## When to Run

| Trigger | Mode | Rationale |
|---------|------|-----------|
| Edit `classify_prompt.py` | `--classify --registry` | Routing logic change |
| Edit `ti011_node_registry.py` | `--registry` | Node/model mapping change |
| Edit extension TypeScript | `--extension` | Extension logic change |
| Before deployments | `--all` | Full gate |
| Weekly scheduled | `--all --report` | Proactive monitoring |
| After node changes | `--node-health` | Topology validation |

---

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Test TI-011 Framework
  run: |
    python3 technical-infrastructure/scripts/test_orchestration_harness.py \
      --all --report --output test-report.md
    if ! grep -q "PASS: Results: 54/54 passed" test-report.md; then
      echo "Test failures detected"
      exit 1
    fi
```

---

## Related Resources

| Resource | Link |
|----------|------|
| Harness source | `scripts/test_orchestration_harness.py` |
| Quick runbook | [`wiki/guides/test-harness-runbook.md`](guides/test-harness-runbook) |
| PLAN | [PLAN-2026-05-03-0800-ORCHESTRATION-FRAMEWORK-FIX](operational/planning/PLAN-2026-05-03-0800-ORCHESTRATION-FRAMEWORK-FIX) |
| Session notes | [SESSION-NOTES-2026-05-03-0845](operational/sessions/SESSION-NOTES-2026-05-03-0845) |
| Latest report | [TEST-REPORT-2026-05-03-0900](/operational/sessions/TEST-REPORT-2026-05-03-0900) |

---

*Last updated: 2026-05-03 10:00 ET*
