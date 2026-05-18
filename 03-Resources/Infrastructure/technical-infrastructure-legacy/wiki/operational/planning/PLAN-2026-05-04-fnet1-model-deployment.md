# FNET1 Model Deployment — Decomposition Plan
**Created:** 2026-05-04  
**Orchestrator:** Carlos' Desktop (Mac M4 Pro)  
**Target:** fnet1 (192.168.0.141)  
**Rationale:** fnet1 has Ollama 0.20.2 installed, 0 models, 15GB RAM. Configs already exist for qwen3.5:4b + qwen3:8b. Need upgrade + model pull + verification.

---

## Hardware Constraints

| Metric | Value |
|--------|-------|
| CPU | Intel i5-6400 @ 2.70GHz, 4 cores |
| RAM | 15GB |
| Safe model size | 9GB |
| Storage | 227G usable (170G free), NVMe boot + 3×931G spinning LVM |
| OS | Ubuntu 24.04.4 LTS |
| Ollama | 0.20.2 (needs → 0.22.1) |
| Installed models | 0 |

**Model capacity analysis:**
- qwen3.5:4b: 3.4GB → Fits (3.4 < 9) ✅
- qwen3:8b: 5.2GB → Fits (5.2 < 9) ✅
- Combined: 3.4 + 5.2 = 8.6GB → Fits (8.6 < 9) ✅
- gemma4:e4b: 9.6GB → Does NOT fit (9.6 > 9) ❌

**Reference data (fnet7, same 15GB tier):**
- Runs qwen3.5:4b + qwen3:8b successfully
- Model-router profile: auto (high=qwen3.5:4b, medium/low=qwen3:8b)
- Benchmark: qwen3.5:4b @ 3.99 t/s [source: STATUS-2026-05-03-fnet7-benchmark]

**Conclusion:** Pull qwen3.5:4b + qwen3:8b. Exclude gemma4:e4b.

---

## Decomposed Sub-Tasks

### Phase 1: Validate Model Selection (Parallel)

| ID | Task | Agent | Complexity |
|----|------|-------|------------|
| P1-A | Validate fnet1 model capacity math (3.4+5.2=8.6 < 9) and confirm no conflicts with existing configs | verifier | Simple |
| P1-B | Cross-check fnet7 as reference node (same 15GB tier) — confirm model set works, gather expected performance baseline | technical-infrastructure | Simple |

### Phase 2: Execute Deployment (Sequential)

| ID | Task | Executor | Estimated Time |
|----|------|----------|----------------|
| S1 | Upgrade Ollama 0.20.2 → 0.22.1 on fnet1 via SSH | Orchestrator (bash) | 2-3 min |
| S2 | Pull qwen3.5:4b on fnet1 (3.4GB download) | Orchestrator (bash) | 3-5 min |
| S3 | Pull qwen3:8b on fnet1 (5.2GB download) | Orchestrator (bash) | 5-8 min |

### Phase 3: Verify + Update (Parallel)

| ID | Task | Agent | Complexity |
|----|------|-------|------------|
| P3-A | SSH to fnet1, verify models installed, run basic inference test, confirm Ollama service status | technical-infrastructure | Medium |
| P3-B | Update fnet1 models.json with tokens_per_sec estimate (fnet7 baseline), update node capacity summary to show fnet1 as fully operational | verifier | Simple |

---

## Acceptance Criteria

- [ ] fnet1 Ollama version = 0.22.1
- [ ] fnet1 has qwen3.5:4b installed (confirmed via `ollama list`)
- [ ] fnet1 has qwen3:8b installed (confirmed via `ollama list`)
- [ ] Basic inference test passes (prompt "Hello" returns non-empty response)
- [ ] node-capacity-summary.json updated to show fnet1 available_models = ["qwen3.5:4b", "qwen3:8b"]
- [ ] models.json tokens_per_sec populated (from fnet7 benchmark or new measurement)
