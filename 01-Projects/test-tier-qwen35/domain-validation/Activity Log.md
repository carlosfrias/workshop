# domain-validation — Activity Log

## [S-TIGHT]
Evidence threshold validation activity log. All validation events recorded chronologically.

---

### 2026-05-22T09:28:00-04:00 — Threshold Validation: qwen3.5:4b Local Model Viability

**Item:** qwen3.5:4b on Apple M1 Pro / 16 GB for decompose-execute-verify orchestrated workloads

**Finding:** Model is **not viable** for orchestrated local execution on this hardware.

**Evidence:**
- Model: qwen3.5:4b (3.4 GB weight, 262,144 token context window)
- Hardware: Apple M1 Pro, 16 GB unified memory
- Test: decompose-execute-verify pipeline with subagent orchestration (decomposer → fleet-dispatcher → verifier)
- Result: Machine became completely unresponsive for 1,200+ seconds (20+ minutes)
- Root cause: Combined memory pressure from model weights (3.4 GB) + 262K context window + subagent spawning exceeded available RAM, triggering aggressive macOS swapping

**Sources:** 1 (single test session)
**Level:** Level 0 — single source, uncorroborated. Requires 2+ additional independent tests/sources to reach Level 1.

**Status:** EVIDENCE RECORDED — NEEDS CORROBORATION ⚠

**Cross-references:**
- [journal/2026-05-22-0928.md](../journal/2026-05-22-0928.md)
- [FOCUS.md](../FOCUS.md)

#threshold-validated #level-0
