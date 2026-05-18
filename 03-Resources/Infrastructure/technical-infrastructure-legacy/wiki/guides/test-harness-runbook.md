# TI-011 Orchestration Framework Testing Harness — Runbook

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/test-harness-runbook.md`

**File:** `technical-infrastructure/scripts/test_orchestration_harness.py`  
**Created:** 2026-05-03  
**Purpose:** Comprehensive end-to-end testing of the TI-011 meta-orchestration framework with 49 tests, dry-run by default, live mode available.

---

## Quick Start

```bash
cd ~/Dropbox/workshop

# Run everything in safe dry-run mode (~10 seconds)
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all

# Run everything with verbose output
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --verbose

# Generate a markdown report
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --report --output wiki/operational/sessions/test-report-$(date +%Y%m%d-%H%M).md
```

---

## Test Suites

| Flag | Tests | What It Tests |
|------|-------|--------------|
| `--classify` | 6 | `classify_prompt.py` — heuristic/LLM classification, routing attachment, `inject_complexity_tag()` |
| `--registry` | 5 | `ti011_node_registry.py` — node loading, `best_model_for()`, `match_subtask_to_local()`, scoring |
| `--health` | 3 | `orchestrator_health.py` — JSON output, importability, integration into classifier |
| `--submit` | 2 | `submit_task.py` — task JSON creation, dry-run vs live submission |
| `--decompose` | 5 | `decompose_llm.py` + watcher — dry-run, validation, trigger directories, list-pending |
| `--collect` | 3 | `task-collect-results.py` — subprocess execution, report JSON validity |
| `--synthesize` | 2 | `synthesize_results.py` — result combination, PLAN update |
| `--extension` | 5 | Extension config — `keyword-router.json`, `package.json`, `complexity-router.json`, `index.ts` |
| `--node-health` | 14 | SSH reachability + Ollama response for all 7 fnet nodes |
| `--report` | N/A | Writes a markdown report after all tests complete |

---

## Test Combinations

```bash
# Specific suites
python3 technical-infrastructure/scripts/test_orchestration_harness.py --classify --registry --health

# Everything
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all

# Everything with report
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --report --output report.md

# Just extension config and node health
python3 technical-infrastructure/scripts/test_orchestration_harness.py --extension --node-health
```

---

## Live Mode (Actually Submits to Nodes)

**Warning:** `--live` causes real SSH/SCP to lab nodes and writes real task files. Only use when the framework is known to be healthy.

```bash
# Live full suite
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all --live --verbose

# Live submit only
python3 technical-infrastructure/scripts/test_orchestration_harness.py --submit --live

# Live node health (same as dry-run — just SSH pings)
python3 technical-infrastructure/scripts/test_orchestration_harness.py --node-health --live
```

---

## What Happens in Live Mode

- **submit suite**: Creates a real task JSON and SCPs it to the node's `/srv/tasks/pending/`. Cleaned up after.
- **node-health suite**: Runs `ssh fnet{i} hostname` and `ssh fnet{i} ollama list`. These are read-only.
- **All other suites**: Unchanged (they exercise local Python logic only).

---

## Interpreting Results

### Pass
```
[PASS] PASS: health: fnet3 SSH reachable — hostname=fnet3, latency=405ms
```

### Fail
```
[FAIL] FAIL: health: fnet3 SSH reachable — expected reachable, got Connection refused
```

### Report Output
When `--report` is used, the harness writes a markdown file with:
- Timestamp and test mode (dry-run vs live)
- A summary table: Total, Passed, Failed, Latency
- A detailed table of every test result

---

## When to Run

| Scenario | Command |
|----------|---------|
| After any change to `classify_prompt.py` | `--classify` |
| After any change to `ti011_node_registry.py` | `--registry` |
| After any change to `pi-keyword-router` extension | `--extension` |
| Before a multi-node deployment | `--all` |
| Weekly health check | `--all` |
| Debug a single failing node | `--node-health --verbose` |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'ti011_node_registry'`
The harness sets `sys.path` to include the scripts directory. If running from outside the repo, use the full path or symlink. Working example:
```bash
cd ~/Dropbox/workshop
python3 technical-infrastructure/scripts/test_orchestration_harness.py --all
```

### SSH timeouts in live mode
Check that your SSH key auth to `friasc@fnet{i}` is working:
```bash
ssh -o ConnectTimeout=3 friasc@fnet3 hostname
```

### No logs for report
The `--report` flag works regardless of test results but the report table looks better with `--verbose`.

---

## Coverage

Last updated: 2026-05-03  
- 49 tests | 100% pass rate in dry-run  
- 7/7 nodes reachable via SSH  
- 7/7 nodes Ollama responding

---
*This runbook is part of the TI-011 meta-orchestration framework documentation.*
