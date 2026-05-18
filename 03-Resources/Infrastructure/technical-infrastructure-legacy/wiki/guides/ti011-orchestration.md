# TI-011 Meta-Orchestration

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/ti011-orchestration.md`

The meta-orchestration framework routes prompts to the optimal (node, model) pair based on real-world benchmark data. This is the primary mechanism for reducing cloud costs while maintaining quality.

## Architecture

```
User Prompt
    │
    ▼
classify_prompt.py ──→ complexity (TRIVIAL / SIMPLE / MEDIUM / HARD)
    │                    + confidence + reasoning
    │
    ▼
ti011_node_registry.py ──→ best (node, model) for complexity + capability
    │                         Reads: lab-specs/node-configs/*/models.json
    │                         Reads: lab-specs/node-configs/*/model-router.json
    │
    ▼
Route to node via SSH / task-worker.sh
    │
    ▼
Collect result ──→ log: prompt_type, model, node, latency, tokens, cost
    │
    ▼
Adaptive feedback loop ──→ update classifier examples, PLAN templates, routing rules
```

## Key Components

| Script | Role | Output |
|--------|------|--------|
| `scripts/classify_prompt.py` | Hybrid heuristic + LLM classification | `{"complexity": "MEDIUM", "confidence": 0.85, "route": {"node": "fnet6", "model": "gemma4:e4b"}}` |
| `scripts/decompose_task.py` | PLAN → sub-task JSONs with model assignments | Task queue entries with `suggested_model` + `suggested_node` |
| `scripts/ti011_node_registry.py` | Runtime (node × model) availability + performance map | `best_model_for(complexity, vision=True)` → optimal pair |
| `scripts/submit_task.py` | Dispatch sub-tasks to node queues | SCP to `/srv/lab-worker/pending/` |
| `scripts/synthesize_results.py` | Combine sub-outputs into coherent response | Final answer to user |

## Routing Rules

1. **Heuristic classification first** — `< 50ms`, keyword-based. If confidence ≥ 0.75, use heuristic result.
2. **LLM fallback** — If heuristic confidence < 0.75, run `qwen3.5:4b` locally for classification (≤ 0.5s).
3. **Node-model lookup** — Query `NodeRegistry` for the fastest node running the appropriate model for the complexity tier.
4. **Capability filtering** — If prompt requires vision, filter to vision-capable models. If tools required, filter to tools-capable models.
5. **Cloud escalation** — Only when no local node has a matching model, or when local execution fails/times out.
6. **Escalation is per sub-task** — If a HARD prompt decomposes into 5 sub-tasks and 4 succeed locally but 1 fails, only that 1 sub-task goes to cloud.

## Data Sources

| File | Purpose | How Updated |
|------|---------|-------------|
| `lab-specs/node-configs/{node}/models.json` | Per-node model definitions with `tokens_per_sec` | `generate-node-profiles.py` after benchmarking |
| `lab-specs/node-configs/{node}/model-router.json` | Routing profiles per node (auto/local/cloud/fast) | `generate-node-profiles.py` after benchmarking |
| `lab-specs/node-capacity-summary.json` | Machine-readable node index | `generate-node-profiles.py` |
| `lab-specs/node-hardware/*.json` | Hardware + installed model inventory | `remote-detect.sh` |
| `lab-specs/node-benchmarks/*.json` | Benchmark results (tokens/sec) | `benchmark-lab.sh` |

## When to Re-run Detection + Benchmarking

- After pulling new models on any node
- After hardware changes (RAM, CPU, GPU)
- After node additions or removals
- Weekly, as a scheduled health check
- When benchmark data is > 30 days old

Use the integrated playbook:
```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/run-pilot-lab.yml --vault-password-file ~/.ansible/secure/.vault_pass
```

## Performance Logging (Required)

Every routed prompt **must** log:
```json
{
  "timestamp": "2026-05-02T15:00:00Z",
  "prompt_type": "ansible_playbook_generation",
  "complexity": "MEDIUM",
  "node": "fnet6",
  "model": "gemma4:e4b",
  "latency_ms": 2847,
  "tokens_in": 450,
  "tokens_out": 128,
  "cost": 0,
  "adequate": true,
  "cloud_escalated": false
}
```

Without these logs, the adaptive feedback loop cannot function.

---

**Related:** [Orchestrator Conventions](orchestrator-conventions.md) | [Planning Gates](planning-gates.md)
