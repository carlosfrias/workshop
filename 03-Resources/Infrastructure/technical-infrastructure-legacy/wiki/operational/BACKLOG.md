# Technical Infrastructure Backlog

**Last Updated:** 2026-05-14
**Status:** 21 active items, 14 completed (archived)

---

## Navigation

**By Priority:**
- [🔴 High Priority](#🔴-high-priority)
- [🟡 Medium Priority](#🟡-medium-priority)
- [🟢 Low Priority](#🟢-low-priority)

**Archive:**
- [Completed Items](../../../wiki/operational/backlog-completed/technical-infrastructure-BACKLOG.md)

---

## 🔴 High Priority

### TI-038: SSHFS Integration Skill — Automatic Parallel Filesystem Orchestration
**Issue Home:** [TI-038](issues/sshfs-integration/0-ISSUE.md)
**Created:** 2026-05-14
**Status:** 📋 **PLANNED**
**Priority:** 🔴 **HIGH** — Makes SSHFS mounting automatic core framework capability; eliminates manual orchestration for parallel filesystem work
**Rationale:** The existing `sshfs-accessible` skill provides manual mount/unmount scripts. When a task requires filesystem work across lab nodes, the orchestrator must remember to mount, decompose, route, and collect manually. This breaks the automatic decomposition promise of the `decompose-execute-verify` framework. The `sshfs-integration` skill closes this gap by detecting when parallel filesystem execution would benefit a task, automatically ensuring mounts, decomposing into node-parallel sub-tasks, routing via file-based dispatch, and synthesizing results — all without user prompting.

**Gap Analysis:**
| Layer | Current State (sshfs-accessible) | Gap |
|-------|----------------------------------|-----|
| Mount trigger | Manual: user must run `mount-all.sh` | Should be automatic when task needs parallel execution |
| Task detection | None | No heuristic to decide if a task benefits from distributed filesystem work |
| Decomposition | None | No schema for splitting filesystem tasks across nodes |
| Routing | None | No mechanism to dispatch sub-tasks to mounted nodes |
| Collection | None | No aggregation of distributed results |
| Lifecycle | Manual unmount | No idle-timeout or health-aware remount policy |

**Deliverables:**
- [ ] **Phase 1:** TDD test plan + architecture document + detection heuristic + mount lifecycle policy
- [ ] **Phase 2:** `ensure-mounted.sh` + `route-tasks.sh` + `execute-on-node.sh` + `collect-results.sh`
- [ ] **Phase 3:** Python modules — `detect_parallel_need.py`, `decompose_task.py`, `synthesize_results.py`
- [ ] **Phase 4:** Framework integration — hook points in decompose-execute-verify pipeline, model router keywords
- [ ] **Phase 5:** Package assembly — `SKILL.md`, `README.md`, `package.json`, semantic versioning
- [ ] **Phase 6:** End-to-end acceptance test on live lab nodes (fnet1–fnet7)
- [ ] **Phase 7:** Wiki documentation + integration guide + backlog update

**Success Criteria:**
1. A prompt like "grep ERROR in /var/log across all nodes" automatically triggers SSHFS integration without explicit user request
2. Mount status is checked and missing mounts are created automatically within 5 seconds
3. Task is decomposed into sub-tasks with round-robin node assignment
4. Sub-tasks execute on lab nodes via mounted workspaces
5. Results are collected, failures flagged, and synthesized output returned
6. Idle mounts are unmounted after 300s of inactivity
7. All TDD tests pass (red → green → refactor cycle complete)

**Plan Document:** [`technical-infrastructure/wiki/operational/issues/sshfs-integration/1-PLAN.md`](issues/sshfs-integration/1-PLAN.md)

**Estimated Effort:** 20–29 hours (3 weeks)
**Target Completion:** 2026-06-04

---

### TI-041: Pi Sessions on Lab Nodes — Cross-Node Intercom Infrastructure
**Issue Home:** [TI-041](issues/ti041-pi-sessions-lab-nodes/0-ISSUE.md)
**Created:** 2026-05-14
**Status:** 📋 **PLANNED**
**Priority:** 🔴 **HIGH** — Blocks true cross-node intercom dispatch in TI-039; chain falls back to SSH
**Rationale:** The `decomposed-intercom-dispatch` chain (TI-039) includes `intercom({ action: "ask", to: "fnet3" })` steps that cannot execute because lab nodes have no pi sessions. Intercom is same-machine only. The chain falls back to SSH dispatch, breaking the "automatic real-time coordination" promise.

**Deliverables:**
- [ ] **Phase 1:** Install pi CLI on fnet1–fnet7 (Node.js/npm + `pi` binary)
- [ ] **Phase 2:** Persistent pi sessions (systemd service or tmux script)
- [ ] **Phase 3:** Intercom connectivity test (orchestrator → lab node message delivery)
- [ ] **Phase 4:** Chain update (replace SSH fallback with intercom dispatch)
- [ ] **Phase 5:** Health monitoring (detect crashed pi sessions, auto-restart)
- [ ] **Phase 6:** Documentation (setup guide, troubleshooting, rollback)

**Dependencies:** TI-033 (SSHFS mounts) ✅, TI-039 (decompose-execute-verify v2.1) ✅

**Plan Document:** [`technical-infrastructure/wiki/operational/issues/ti041-pi-sessions-lab-nodes/1-PLAN.md`](issues/ti041-pi-sessions-lab-nodes/1-PLAN.md)

**Estimated Effort:** 6–10 hours (2 phases)
**Target Completion:** 2026-05-28

---

### TI-036: Playbook-Executor Natural-Language Trigger Expansion
**Issue Home:** [TI-036](issues/ti036-playbook-nl-triggers/0-ISSUE.md)
**Created:** 2026-05-13
**Status:** 🔄 **IN PROGRESS**
**Priority:** 🔴 **HIGH** — Low-capacity models cannot execute playbooks from natural-language prompts; breaks the "exact-match" execution promise
**Rationale:** The playbook-executor package is designed for 2–8B parameter models with a strict "Never reason — Always trigger" policy. However, the trigger registry (`config/playbook-index.json`) and the AGENTS.md routing table only map snake_case composite keywords and narrow technical phrases. When a user types `"run the wiki"`, `"start the wiki server"`, or `"deploy pi to the lab"`, none of the pipeline layers match. The keyword router does not route to playbook-executor, AGENTS.md keywords do not match, and the playbook index triggers are too literal. This leaves low-capacity models unable to perform the single task they are optimized for.

**Gap Analysis:**
| Layer | Current State | Gap |
|-------|--------------|-----|
| `playbook-index.json` triggers | `serve_wiki`, `wiki_server`, `wiki_serve` | Missing `run the wiki`, `start the wiki`, `launch wiki` |
| `playbook-index.json` verbs | None | Missing verb+object expansion (`run`, `start`, `launch`, `fix`, `deploy`) |
| `AGENTS.md` keywords | `playbook-executor, run playbook, execute playbook, service recovery...` | Missing natural-language variants |
| Keyword router | `infrastructure` route with generic keywords | No playbook-executor-specific keywords |
| Low-capacity model | "Never reason" instruction | Cannot bridge semantic gap; returns **E002** |

**Deliverables:**
- [x] **Phase 1:** Expand `config/playbook-index.json` with ≥10 natural-language synonyms per playbook (verb + object + phrase triggers)
- [ ] **Phase 2:** Update `AGENTS.md` and `AGENTS-full.md` with broad natural-language keywords for playbook-executor (captured as standalone backlog item for future session)
- [ ] **Phase 3:** Create `scripts/intent-to-trigger.py` — deterministic bridge from natural language to exact trigger
- [ ] **Phase 4:** Update keyword-router config with playbook-executor route (or sub-keywords under infrastructure)
- [ ] **Phase 5:** Integration validation — 10 natural-language prompts must execute correct playbooks on `qwen3.5:4b`
- [ ] **Phase 6:** Documentation discoverability — linked from `wiki/index.md`, product catalog, prompt-references

**Success Criteria:**
1. `"run the wiki"` → executes `serve-wiki.yml` on `qwen3.5:4b` with zero reasoning
2. `"deploy pi to the lab"` → executes `deploy-pi.yml`
3. `"fix ollama api"` → executes `fix-ollama-network-bind.yml`
4. `"get capacity report"` → executes `capacity-report.yml`
5. All tests pass without invoking cloud models

**Plan Document:** [`technical-infrastructure/wiki/products/playbook-executor/index.md`](../../../wiki/products/playbook-executor/index.md)

**Estimated Effort:** 11–15 hours
**Target Completion:** 2026-05-20

---

### TI-036-P2: Playbook-Executor AGENTS.md Natural-Language Routing Update
**Issue Home:** [TI-036-Phase-2](issues/playbook-executor/0-ISSUE.md)
**Created:** 2026-05-14
**Status:** 📋 **BACKLOGGED** — Ready for future session
**Priority:** 🟡 **MEDIUM** — Depends on completed Phase 1
**Rationale:** Phase 1 expanded `config/playbook-index.json` with 865 natural-language triggers. However, the routing layer above it (`AGENTS.md` keyword table, keyword router config) does not yet include natural-language keywords. A prompt like "run the wiki" still fails at the router/AGENTS.md layer before reaching the expanded playbook-index. Phase 2 closes this gap.

**Dependencies:** Phase 1 trigger expansion (COMPLETE)

**Deliverables:**
- [ ] Update `AGENTS.md` keyword row with broad natural-language keywords (run the wiki, deploy pi, fix ollama, etc.)
- [ ] Add optional per-playbook keyword rows to AGENTS.md
- [ ] Update `AGENTS-full.md` with natural-language variants and README links
- [ ] Verify consistency between AGENTS.md and AGENTS-full.md

**Estimated Effort:** 1–1.5 hours
**Plan Document:** [`technical-infrastructure/wiki/operational/issues/playbook-executor/2-PLAN-phase2.md`](issues/playbook-executor/2-PLAN-phase2.md)

---

### TI-035: Fix Keyword-Router Keyword Collisions and Priority Inversions
**Issue Home:** [TI-035](issues/ti035-keyword-router-collisions/0-ISSUE.md)
**Created:** 2026-05-07
**Status:** 🔄 **OPEN** — Collision analysis completed, fixes pending
**Priority:** 🔴 **HIGH** — Causes incorrect model routing, wasted API cost, wrong model for task complexity
**Rationale:** Comprehensive analysis of pi-keyword-router trigger keywords revealed 9 critical keyword collisions across routes (same keyword in multiple routes) and 4 surprising priority inversions where simpler routes outrank complex ones. This causes expensive cloud models to be used for trivial tasks and cheap local models to be used for complex reasoning tasks.

**Critical Collisions Found:**
| Keyword | Routes Conflicted | Winner (Wrong?) |
|---------|------------------|-----------------|
| `verify` | reasoning, monitoring, trivial | reasoning — but monitoring/trivial should own simple verification |
| `validate` | reasoning, structured | reasoning — but structured should own data validation |
| `list` | structured, trivial | trivial — **correct for simple lists** |
| `format` | structured, trivial | trivial — **correct for simple formatting** |
| `synthesize` | reasoning, hard | hard — but reasoning should own signal synthesis |
| `decompose` | reasoning, infrastructure | reasoning — but infrastructure owns task decomposition |
| `ping` | monitoring, trivial | trivial — **correct** |

**Priority Inversions (Wrong Model Chosen):**
| Prompt | Expected Route | Actual Route | Why |
|--------|---------------|--------------|-----|
| "basic research on market trends" | reasoning (cloud) | **simple** (qwen3:8b) | "basic" priority 2 > "research" priority 1 |
| "straightforward analysis" | reasoning | **simple** | "straightforward" priority 2 > "analysis" priority 1 |
| "simple check of server status" | monitoring | **trivial** | "simple check" priority 2 > monitoring priority 0 |
| "design a simple script" | hard/reasoning | **hard** wins but simple keyword also matches | ambiguous |

**Root Causes:**
1. **Substring matching:** `promptLower.includes(kw)` treats "position" as matching "position-sizing" — any word containing "position" triggers reasoning
2. **Priority numbers inverted:** Complexity routes (trivial/simple/medium/hard) have priorities 2-3, semantic routes have 0-1. This was intentional (complexity routes win ties) but causes semantic misrouting
3. **Overloaded words:** "verify", "validate", "check", "list" are domain-general and appear in multiple routes
4. **Meta-words in infrastructure:** "classify", "complexity", "decompose" describe the router itself, not infrastructure tasks

**Deliverables:**
- [x] Remove `verify`/`validate` from reasoning (let monitoring/structured handle)
- [x] Remove `list`/`format` from structured (let trivial handle simple ops)
- [x] Fix "simple" keyword priority inversion (removed all keywords from complexity routes)
- [x] Remove "synthesize" from hard (let reasoning handle)
- [x] Split "decompose" by context: "decompose signal" → reasoning, "decompose task" → infrastructure
- [x] Remove meta-words from infrastructure ("classify", "complexity", "decomposition")
- [x] Switch keyword matcher from `includes()` to `\bkeyword\b` regex for word boundaries + multi-word phrase support
- [x] Add "system architecture", "deployment plan", "task decomposition" to infrastructure
- [x] Re-test all priority inversion scenarios after fixes — **27/27 acceptance tests pass**
- [x] Update `keyword-router.json` in Trading Desk workspace

**Verification:** [TI-035 Acceptance Test Suite](../../../wiki/operational/testing/ti035-acceptance-test.js) — 27 tests, 100% pass rate

**Resolution Plan:** [TI-035 Resolution Recommendations](../../../wiki/operational/analysis/TI-035-resolution-recommendations.md) — 6 prioritized fixes, ~1 hour implementation

**References:**
- [Collision Analysis Document](../../../wiki/operational/analysis/keyword-router-trigger-collision-analysis.md)
- [Resolution Recommendations](../../../wiki/operational/analysis/TI-035-resolution-recommendations.md)

---

### keyword-router-regression: Default Route Regression — All Prompts Routed to `qwen3.5:4b`
**Issue Home:** [keyword-router-regression/0-ISSUE.md](issues/keyword-router-regression/0-ISSUE.md)
**Created:** 2026-05-13
**Status:** ✅ **CORE FIXED** — Regression root cause resolved; 3 residual items tracked in issue home
**Priority:** 🔴 **HIGH** — Core fix complete; B-KR-004 (cloud escalation) remains 🔴 High
**Rationale:** Commit `93e1d39` changed the keyword-router default route from `ollama:gemma4:e4b` to `router:auto`. When `pi-model-router` is absent, this falls back to the lowest-capacity local model (`qwen3.5:4b`), making keyword routing unusable for anything beyond trivial tasks. Persistent kill-switch, bisection, and TDD test infrastructure also built.

**Deliverables:**
- [x] B-KR-001: Kill-switch for `extensions.pi-keyword-router.enabled`
- [x] B-KR-002: Bisected regression commit (`93e1d39`)
- [x] B-KR-003: One-line fix — restored `ollama:gemma4:e4b` default in `lib/config.ts`
- [ ] B-KR-004: Cloud escalation for deep research prompts — 🔴 High
- [ ] B-KR-005: Operational runbook — 🟡 Medium
- [ ] B-KR-006: CI regression test — 🟡 Medium

**Remaining Backlog:** [BACKLOG-keyword-router.md](issues/keyword-router-regression/BACKLOG-keyword-router.md)

---

### TI-031: Orchestrator Health Monitoring Protocol
**Created:** 2026-05-05
**Status:** ✅ **IMPLEMENTED** — Protocol active as of this session
**Priority:** 🔴 **CRITICAL** — Non-negotiable safety guardrail
**Rationale:** User instruction requires health monitoring on every prompt to prevent orchestrator saturation. This ensures decomposition is triggered before memory/CPU thresholds are breached.

**Protocol:**
- [x] Health check on every prompt (`orchestrator_health.py --json`)
- [x] Automatic decomposition if RAM >80%, CPU >4.0, or Swap >0
- [x] Cloud model routing when stressed/critical
- [x] Logging to `wiki/operational/sessions/health-decisions.jsonl`

**Reference:** [`wiki/operational/backlog-completed/TI-031-health-monitoring-protocol.md`](../../../wiki/operational/backlog-completed/TI-031-health-monitoring-protocol.md)

---

### TI-010: Event-Driven Gist Message Protocol (Backup Orchestration)
**Created:** 2026-05-01
**Status:** ✅ **COMPLETE** — Event bus operational, tested against live Gist
**Priority:** 🔴 High
**Rationale:** Gist protocol was created during bare-bones phone-tether connectivity. It works but has UX problems - workers don't self-poll, operators must constantly remind workers to check/update gist. **Redesigned as event-driven architecture** with pub/sub semantics over the existing Gist transport layer.

**Completed Deliverables:**
- [x] `gist_event_bus.py` — Core library (publish, consume, ack, nack, DLQ)
- [x] `EventConsumer` class — Decorator-based handlers, wildcard subscriptions (in `gist_event_bus.py`)
- [x] `gist_lag_monitor.py` — Observability (status, lag, metrics, trace)
- [x] Event schema with type, source, target, payload, metadata, TTL
- [x] Retry logic: 3 attempts, 30s/60s backoff → DLQ
- [x] Wildcard matching: `task.*` matches `task.created`, `task.failed`, etc.
- [x] Compaction: auto-cleanup of consumed events after 7 days
- [x] End-to-end verified: publish → consume → ack flow against live Gist
- [x] Architecture plan: `PLAN-TI010-EVENT-DRIVEN.md`
- [x] Master prompt: `PROMPT-TI010-EVENT-DRIVEN.md`
- [x] Test harness: `test_ti010.py` (comprehensive 21-test suite)
- [x] Acceptance tests: `acceptance-test-ti010.py` (28 tests, 100% pass rate)

**Architecture:**
- Producer (orchestrator) appends events to `events` file in Gist
- Consumer (lab node) polls Gist, matches subscriptions via fnmatch wildcards
- ACK marks event as consumed (immutable append-only history)
- NACK increments delivery attempt; after 3 → DLQ file
- Rate limiting: 1s between API calls (GitHub allows 5000/hr for auth users)

**Testing:**
- Comprehensive test harness: `scripts/test_ti010.py` (21 tests covering connectivity, pub/sub, ACK/NACK, DLQ, rate limiting, compaction)
- Acceptance test suite: `scripts/acceptance-test-ti010.py` (28 tests, 100% pass rate as of 2026-05-06)
- Test report: `operational/testing/ti010-acceptance-report.json`

**Acceptance Criteria Status:**
- ✅ Event bus library published to Gist
- ✅ Consumer lag monitor operational
- ✅ DLQ captures failed events
- ✅ Retry logic with 3 attempts
- ✅ Wildcard subscription matching
- ✅ Event compaction works
- ✅ Event schema correct
- ✅ Test harness exists
- ✅ Documentation complete
- ✅ Backlog status accurate

**Integration:**
```bash
# Publish event
python3 gist_event_bus.py --publish task.created --target fnet3 \
  --payload '{"task_id":"001","command":"benchmark"}'

# Consume events (on lab node)
python3 gist_event_bus.py --consume --node-id fnet3 --poll-interval 5

# Monitor
python3 gist_lag_monitor.py --status
python3 gist_lag_monitor.py --lag
```

---

### TI-011: Meta-Orchestration Framework (Local-First LLM Routing)
**Issue Home:** [TI-011](issues/ti011-meta-orchestration/0-ISSUE.md)
**Created:** 2026-05-01
**Status:** ▶️ **IN PROGRESS** - Phase 1 classifier complete
**Priority:** 🔴 High (reduces cloud costs by 75-90%)
**Rationale:** Cloud model usage dominates sessions despite 7 local nodes being available. Current routing is keyword-based, not complexity-based. Every "think deeply" triggers ultra-reasoning even for simple analysis. Building a meta-orchestration framework classifies prompts by complexity, decomposes multi-step tasks, routes to appropriate local models, and escalates only specific sub-tasks to cloud.

**Phase 1: Classification + Simple Routing ✅ COMPLETE**
- [x] Build hybrid heuristic classifier (classify_prompt.py) - 1ms latency, 100% heuristic
- [x] Add infrastructure keywords to model-router.json
- [x] Create complexity-router.json mapping complexity to models
- [x] Wire complexity layer into actual routing logic - NodeRegistry integration
- [x] Test with live prompts through full pipeline - `classify_prompt.py --route` working
- [ ] Start performance logging (needs session data)

**Phase 2: Decomposition Engine ✅ COMPLETE**
- [x] Build decompose_task.py (PLAN template → task JSON)
- [x] Integrate with submit_task.py for fan-out
- [x] Build synthesize_results.py for combining sub-outputs
- [x] Wire NodeRegistry into decompose_task.py for dynamic model/node assignment

**Phase 3: Performance Monitor ✅ COMPLETE**
- [x] Log every prompt: type, model, latency, tokens, cost, quality - `performance_logger.py` with JSONL output
- [x] Log every decomposition: trigger_id, sub_task_count, latency, model_used, success/failure
- [x] Log every dispatch: trigger_id, sub_task_id, node, model, latency, success/failure
- [x] Weekly report script: `scripts/generate-weekly-report.py` - markdown output with routing/decomposition/dispatch stats
- [x] Benchmark data collected and integrated into routing decisions

**Phase 4: Adaptive Feedback 🔄 PENDING (needs 2+ weeks of performance data)**
- [ ] Auto-update classifier few-shot examples from logs
- [ ] Auto-update PLAN templates from successful decompositions
- [ ] Auto-generate SESSION-NOTES summaries for knowledge base
- [ ] Tier adjustment engine (monthly analysis)

**Dependent On:** TI-009 (orchestration must be working - ✅ MVP complete), TI-016 (per-node profiles - ✅ complete)

**Estimated Effort:** 25-35 hours total (2-3 weeks)

---

### TI-018: Cost-Aware Routing + Billing Model
**Issue Home:** [TI-018](issues/ti018-cost-aware-routing/0-ISSUE.md)
**Created:** 2026-05-02
**Status:** 🔄 **IN PROGRESS** - Cost calculation implemented, billing tiers defined
**Priority:** 🔴 High (enables customer billing and infrastructure monetization)
**Rationale:** Local models currently treated as "free" ($0) but they consume real resources - electricity, hardware depreciation, facility space. A unified cost model (cost per 1K tokens) allows billing customers regardless of execution venue and reveals that local compute is 70-78% cheaper than cloud.

**Deliverables:**
- [x] `ti011_node_registry.py` - `_compute_node_hourly_cost()` + `_compute_cost_per_1k_tokens()`
- [x] Hardware cost defaults by RAM tier ($500 for 15GB, $800 for 31GB)
- [x] Power cost: 0.15 kWh × $0.12/kWh = $0.018/hour per node
- [x] Scoring updated: 30% speed + 45% fit + 25% cost
- [x] Billing tiers defined:
  - Local Basic (qwen3.5:4b): $0.005/1Ktk (40% margin)
  - Local Standard (qwen3:8b): $0.006/1Ktk (50% margin)
  - Local Premium (gemma4:e4b): $0.005/1Ktk (56% margin)
  - Cloud Standard: $0.015/1Ktk (33% margin)
  - Cloud Premium: $0.050/1Ktk (20% margin)
- [ ] Invoice generation script (future)
- [ ] Customer usage tracking (future)

**Dependent On:** TI-019 (LLM-driven decomposition) ✅ COMPLETE - generates weighted sub-tasks for accurate per-task billing

**Estimated Effort:** 3-4 hours (core done, billing infrastructure pending)

---

### TI-034: Project-Blueprint Consumer Acceptance Testing
**Issue Home:** [TI-034](issues/ti034-project-blueprint-testing/0-ISSUE.md)
**Created:** 2026-05-06
**Status:** ✅ **COMPLETE** — All 6 fixes implemented, 27/27 acceptance tests pass
**Priority:** 🔴 **HIGH** — Causes incorrect model routing, wasted API cost, wrong model for task complexity
**Rationale:** When consumers install project-blueprint via `pi install github:carlosfrias/project-blueprint`, the scaffolding wizard creates unexpected files in the workspace root (`technical-infrastructure/`, `templates/`, `Final Summary.md`, `model-routing-decisions.*`). These artifacts belong in the skill folder (`~/.pi/agent/skills/project-blueprint/`) or in `.pi/sessions/`, NOT in the consumer's workspace. This breaks the "clean root" contract and makes consumers lose trust in the tool.

**Discovered in:** `~/Dropbox/carlos-desktop` workspace (his-desk domain setup)

**Critical Bugs to Fix:**
- 🔴 **CRITICAL:** `technical-infrastructure/` created in workspace root (Trading Desk artifact leaked)
- 🔴 **CRITICAL:** `templates/` copied to workspace root (should stay in skill folder only)
- 🔴 **CRITICAL:** `Final Summary.md` dumped to root (should archive to `.pi/sessions/`)
- 🟡 **MEDIUM:** `model-routing-decisions.jsonl` stored in wrong directory (`technical-infrastructure/wiki/sessions/` instead of `.pi/sessions/`)
- 🟡 **MEDIUM:** No skill reference file in `.pi/agents/skills/project-blueprint.md`

**Deliverables:**
- [x] Consumer acceptance prompt: `technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`
- [x] Wiki page with embedded prompt: `wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`
- [ ] Fix scaffolding logic: remove `technical-infrastructure/` from root creation
- [ ] Fix scaffolding logic: keep `templates/` in skill folder only
- [ ] Fix scaffolding logic: redirect `Final Summary.md` to `.pi/sessions/`
- [ ] Fix scaffolding logic: store session artifacts in `.pi/sessions/`
- [ ] Add skill reference: `.pi/agents/skills/project-blueprint.md`
- [ ] Run acceptance test: execute prompt in fresh workspace
- [ ] Verify clean root: `ls -la` shows only AGENTS.md, .pi/, domain folders, wiki/ (if requested)
- [ ] Verify consumer access: confirm `~/.pi/agent/skills/project-blueprint/` is readable/modifiable
- [ ] Tag as production-ready when all AC-4 (clean root) criteria pass

**Acceptance Criteria (30+ checklist items):**
- **AC-1 (Installation):** Install succeeds, skill in `pi skill list`, no root files created during install
- **AC-2 (Skill Location):** Templates in `~/.pi/agent/skills/project-blueprint/templates/`, NOT root
- **AC-3 (Scaffolding Interview):** Interview starts, questions stored in `.pi/sessions/`, no root files during interview
- **AC-4 (Clean Root — CRITICAL):** Only `AGENTS.md`, `.pi/`, domain folders, `wiki/` (if requested) in root. ❌ No `technical-infrastructure/`, ❌ No `templates/`, ❌ No `Final Summary.md`, ❌ No `model-routing-decisions.*`
- **AC-5 (Wiki & VitePress):** `wiki/` has markdown only, `wiki-build/` is sibling to `wiki/`, NOT in root
- **AC-6 (Session Storage):** All artifacts in `.pi/sessions/`, none in root
- **AC-7 (Consumer Access):** Can locate and modify skill files at `~/.pi/agent/skills/project-blueprint/`
- **AC-8 (Domain Management):** `/add-domain`, `/rename-domain`, `/remove-domain` maintain clean root

**Prompts:**
- Standalone prompt: [`technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`](../../prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md)
- Wiki page: [`wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`](../../../wiki/operational/planning/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md)

**Known Issues:**
| Issue | Severity | Root Cause | Required Fix |
|-------|----------|-----------|--------------|
| `technical-infrastructure/` in root | 🔴 Critical | Scaffolding logic creates Trading Desk artifact | Remove hardcoded path |
| `templates/` in root | 🔴 Critical | Copy step misplaces templates | Templates stay in skill folder only |
| `Final Summary.md` in root | 🔴 Critical | Output file location hardcoded to root | Redirect to `.pi/sessions/` |
| `model-routing-decisions.jsonl` wrong location | 🟡 Medium | Session data stored in wrong directory | Move to `.pi/sessions/` |
| Missing skill reference in `.pi/agents/` | 🟡 Medium | No skill metadata file created | Add `skills/project-blueprint.md` |

**Test Environment:**
- Fresh workspace: `mkdir ~/pb-consumer-test`
- No git init, no existing files
- Run `pi install github:carlosfrias/project-blueprint`
- Run `pi skill project-blueprint`
- Verify with `ls -la`

**Estimated Effort:** 4-6 hours (prompt creation ✅ done, fixes 3-4h, testing 1-2h)

---

## 🟡 Medium Priority

### TI-002: fnet1 Storage Rebuild (LVM)
**Created:** 2026-05-01
**Status:** Deferred from standardization session
**Priority:** 🟡 Medium
**Details:** fnet1 has 3× 931GB spinning disks with a manual partition layout from an older install. The LVM rebuild attempt failed because `sfdisk` was missing. The 238GB swap partition (`/dev/sda1`) is deactivated but still present.

**Options:**
- **Option A:** Retry LVM with `fdisk` instead of `sfdisk`
- **Option B:** Manually wipe and create PV/VG/LV
- **Option C:** Rebuild from scratch during next maintenance window

**Acceptance Criteria:**
- [ ] Single VG `vg-lab` across sda+sdb+sdc
- [ ] LVs: var (50GB), srv (200GB), varlog (20GB), tmp (20GB), opt (20GB), usrlocal (20GB), archive (remaining)
- [ ] All data migrated safely
- [ ] `/etc/fstab` updated with UUIDs
- [ ] Reboot and verify all mounts

---

### TI-004: Ollama Benchmark Fix
**Created:** 2026-05-01
**Status:** Deferred - benchmarking failed on fnet2, fnet4, fnet5, fnet7
**Priority:** 🟡 Medium
**Details:** `ollama-benchmark.sh` exited with code 255. Likely missing `curl`, `jq`, or Python dependency. Not blocking - models load and run.

---

### TI-020: Decomposition Tier Escalation with Attempt Tracking
**Created:** 2026-05-02
**Status:** 📋 **BACKLOG** - Deferred
**Priority:** 🟡 Medium
**Rationale:** When local high model (gemma4:e4b) fails to decompose, escalate to cloud models. Track attempts per tier and escalate after 3 consecutive failures, wrapping from HIGH back to LOW.

**Rules:**
1. Local decomposition attempted first (gemma4:e4b)
2. On local failure → escalate to cloud LOW (qwen3.5:397b-cloud)
3. After 3 attempts at any tier → escalate to next higher cloud tier
4. After 3 attempts at HIGH → wrap back to LOW (cyclical, never gives up)
5. State tracked per task_id in DecomposerState object

**Estimated Effort:** 2-3 hours

---

### TI-022: Time-Based Cost Tracking for Decomposition
**Created:** 2026-05-02
**Status:** 📋 **BACKLOG**
**Priority:** 🟡 Medium
**Rationale:** Current cost model tracks token-based costs only. Decomposition is billed at flat rate ($0.011 per call) regardless of how long it takes. For fair billing and capacity planning, we need time-based metrics: tokens/sec, wall time, and cost per minute of compute.

**Estimated Effort:** 2-3 hours

---

### TI-024: Cloud Lab Nodes - Virtual Server Expansion
**Created:** 2026-05-02
**Status:** 📋 **BACKLOG**
**Priority:** 🟡 Medium
**Rationale:** The current lab is limited to 7 physical nodes. By adding virtual nodes in cloud services (AWS EC2, GCP Compute, Hetzner, etc.), we can dramatically increase available capacity for peak workloads and serve as a natural extension of the local lab.

**Estimated Effort:** 8-12 hours (research + provisioning + integration)

---

### TI-025: Local Sub-Agent Integration with TI-011 Orchestration
**Created:** 2026-05-02
**Status:** 📋 **BACKLOG**
**Priority:** 🟡 Medium
**Rationale:** pi has a powerful sub-agent system (decomposer, verifier, worker, scout, etc.) and custom agent definitions in `.pi/agents/`. Currently these run manually or semi-manually. They should flow naturally into the TI-011 meta-orchestration framework.

**Estimated Effort:** 5-7 hours

---





## 🟢 Low Priority

### TI-005: Model Depot Sync (fnet6 as Secondary Depot)
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Details:** fnet3 is the primary depot. fnet6 (also 31GB RAM, Intel i7) could serve as secondary depot for redundancy. Network saturation should be monitored.

---

### TI-006: NextCloud Installation
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Details:** Install NextCloud on appropriate node (fnet2 was designated). Prerequisites already in autoinstall packages.

---

### TI-007: File Migration (Orchestrator → Lab Storage)
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Details:** 900GB orchestrator storage needs migration to fnet1 `/srv/archive/` or fnet2 `/srv/`.

---

### TI-008: Off-Premises VPN (OPNsense/Protectli)
**Created:** 2026-05-01
**Status:** Deferred indefinitely
**Priority:** 🟢 Low
**Details:** Consumer router (TP-Link AX6000 + AT&T) blocks inbound UDP. WireGuard off-premises access requires OPNsense/Protectli replacement. This is a hardware purchase decision.

---

### TI-012: Auto-Apply Adaptive Feedback Suggestions
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Rationale:** adaptive_feedback.py currently suggests updates but requires manual review. After 2+ weeks of data, we can evaluate auto-apply with safety checks (e.g., only for high-confidence suggestions, rollback capability).

**Blocked By:** Needs 2+ weeks of performance data

**Estimated Effort:** 4-6 hours

---

### TI-013: Cross-Session Pattern Learning
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Rationale:** Parse SESSION-NOTES performance tables across sessions to identify persistent patterns (e.g., "markdown formatting always works on qwen3.5:4b"). This is broader than single-session log analysis.

**Blocked By:** Needs multiple SESSION-NOTES with performance tables

**Estimated Effort:** 3-4 hours

---

### TI-014: Model Performance Prediction
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Rationale:** Before executing a prompt, predict which model will succeed based on prompt features + historical data. This would eliminate trial-and-error for novel prompt types.

**Blocked By:** Needs extensive performance data (50+ prompts per model)

**Estimated Effort:** 6-8 hours

---

### TI-015: Dynamic Tier Adjustment
**Created:** 2026-05-01
**Status:** Proposed
**Priority:** 🟢 Low
**Rationale:** Monthly automated reclassification of prompt types into complexity tiers based on 30 days of performance data. E.g., if "Ansible playbook" prompts consistently succeed on qwen3:8b, reclassify from MEDIUM to SIMPLE.

**Blocked By:** Needs 1+ month of data

**Estimated Effort:** 4-6 hours

---

## 🔄 Trading Desk Orchestration Framework (TDOF)

**Formerly:** AgenticOS Implementation
**Progress:** ~40% → Target 80% for rebrand decision
**Rebrand Candidates:** Trading Desk Orchestration Framework, Carlos' Desktop
**Status:** 🔄 IN PROGRESS - Option 1 Trajectory (build capabilities, decide name at 80%)

### TDOF-001: Vector Memory with RAG Retrieval
**Issue Home:** [TDOF-001](issues/tdof-001-chromadb/0-ISSUE.md)
**Created:** 2026-05-04  
**Status:** ✅ **COMPLETE** — ChromaDB deployed, Ollama embeddings integrated, RAG retrieval functional  
**Priority:** 🔴 **CRITICAL** — Biggest gap between "stateless chatbot" and "agentic system"  
**Rationale:** AgenticOS design specifies vector-backed long-term storage with RAG retrieval. Currently Trading Desk has file-based memory (session notes, status docs) but no semantic search or retrieval augmentation.  

**Deliverables:**
- [x] ChromaDB deployed on fnet3 (31GB RAM, **v0.6.2**, port 8000) — *0.6.3 had async bug in collections endpoint*
- [x] Ollama `nomic-embed-text` on fnet3 for 768-dim embeddings
- [x] Embedding pipeline (`chromadb-embedding.py`) with Ollama integration, incremental updates
- [x] RAG retrieval API (`rag-retrieve.py`) with domain/date filtering — **VERIFIED WORKING**
- [x] Performance logger updated with `log_retrieval()`
- [x] Plan document created
- [x] Initial index run completed (609 chunks across 76 documents)
- [ ] Integration with decomposer tested

**Verification:**
```bash
# ChromaDB health
curl http://192.168.0.143:8000/api/v1/heartbeat  # → 200

# Index documents (generates embeddings via Ollama)
python3 technical-infrastructure/scripts/chromadb-embedding.py --index-all

# Test RAG retrieval
python3 technical-infrastructure/scripts/rag-retrieve.py "fnet7 performance" --top-k 5
```

**Estimated Effort:** 4-6 hours
**Blocked By:** None

### TDOF-002: MCP Tool Registry
**Issue Home:** [TDOF-002](issues/tdof-002-mcp-registry/0-ISSUE.md)
**Created:** 2026-05-04
**Status:** 📋 **BACKLOG**
**Priority:** 🔴 **HIGH** - Standardizes tool integration
**Rationale:** AgenticOS specifies MCP (Model Context Protocol) for tool abstraction. Currently tools are ad-hoc (scripts, SSH commands). MCP provides standard interface, retry logic, and observability.

**Deliverables:**
- [ ] MCP server skeleton (Python or TypeScript)
- [ ] Tool registry with 5+ tools (file ops, SSH, pi CLI, etc.)
- [ ] Retry logic with exponential backoff
- [ ] Cost/latency tracking per tool call

**Estimated Effort:** 6-8 hours
**Blocked By:** None

### TDOF-003: Autonomous Agent Loop
**Issue Home:** [TDOF-003](issues/tdof-003-autonomous-agent/0-ISSUE.md)
**Created:** 2026-05-04
**Status:** 📋 **BACKLOG**
**Priority:** 🟡 **MEDIUM** - Core agentic capability
**Rationale:** AgenticOS specifies continuous perception → reasoning → action loop. Currently Trading Desk is reactive (user prompts trigger actions). Autonomous loop enables proactive monitoring and task execution.

**Deliverables:**
- [ ] Agent loop implementation (Python async)
- [ ] Perception triggers (cron, file change, webhook)
- [ ] Reasoning engine (ReAct pattern)
- [ ] Action executor (MCP tool calls)
- [ ] Safety guardrails (financial limits, approval workflows)

**Estimated Effort:** 8-12 hours
**Blocked By:** TDOF-001 (vector memory), TDOF-002 (MCP registry)

### TDOF-004: Rebrand Decision (At 80% Completion)
**Issue Home:** [TDOF-004](issues/tdof-004-rebrand/0-ISSUE.md)
**Created:** 2026-05-04
**Status:** 📋 **FUTURE**
**Priority:** 🟢 **LOW** - Naming decision, not functional
**Rationale:** When TDOF reaches 80% completion, decide on branding:
- **Option A:** Trading Desk Orchestration Framework (technical, descriptive)
- **Option B:** Carlos' Desktop (personal brand, includes trading-desk domain)
- **Option C:** Keep unnamed (function over form)

**Decision Criteria:**
- User preference
- External vs. internal focus
- Marketing considerations

**Estimated Effort:** 30 minutes
**Blocked By:** Reaching 80% progress

---

### TI-032: Integrated Health-Aware Playbook Monitoring System (Master Prompt)
**Issue Home:** [TI-032](issues/ti032-master-prompt/0-ISSUE.md)
**Created:** 2026-05-05  
**Status:** 🔄 **IN PROGRESS** — Phase 0 Foundation started  
**Priority:** 🔴 **CRITICAL** — Non-negotiable safety guardrail  
**Rationale:** Merges TI-031 Health Monitoring, Master Prompt Monitoring, and ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md into single cohesive system. Prevents orchestrator saturation through unified health checks, automatic decomposition, node recovery timeouts, and tiered cloud escalation.

**Supersedes:**
- [TI-PLAYBOOK-MASTER](#ti-playbook-master-master-prompt-for-playbook-keyword-system-with-wiki-documentation) — Items integrated
- [PLAN-TI031-INTEGRATION-v1.0.md](../operational/planning/PLAN-TI031-INTEGRATION-v1.0.md) — Archived
- [ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md](../operational/planning/ASSESSMENT-TI031-MASTER-PROMPT-GAPS.md) — Archived

**Phase 0 Deliverables (IN PROGRESS):**
- [ ] `technical-infrastructure/prompts/core-prompt.md` — Always-loaded core instructions (150 tokens)
- [ ] `technical-infrastructure/prompts/module-{1-6}*.md` — On-demand module files (100-150 tokens each)
- [ ] `technical-infrastructure/ansible/playbooks/playbook-index.json` — Machine-readable playbook registry
- [ ] `technical-infrastructure/ansible/playbooks/template.yml` — Ansible playbook template
- [ ] `technical-infrastructure/scripts/unified_health_monitor.py` — Single health check entry point
- [ ] `technical-infrastructure/scripts/unified_decision_engine.py` — Single routing decision maker

**Phase 1 Deliverables (PENDING):**
- [ ] `technical-infrastructure/scripts/binary_decompose.py` — 2x binary decomposition logic
- [ ] `technical-infrastructure/scripts/node_recovery_watcher.py` — Recovery timeout mechanism
- [ ] `technical-infrastructure/scripts/cloud_escalation.py` — Tiered escalation manager
- [ ] `technical-infrastructure/scripts/lab_node_monitor.py` — SSH-based node monitoring

**Phase 2 Deliverables (PENDING):**
- [ ] `technical-infrastructure/scripts/memory_manager.py` — Health-aware memory allocation
- [ ] `technical-infrastructure/reference/model-routing-guide.md` — Updated with health states
- [ ] `.pi/agents/phases/phase-2-planning.md` — Health check requirement
- [ ] `.pi/agents/phases/phase-3-execution.md` — Health monitoring during execution

**Documentation Created:**
- ✅ [Master Playbook Prompt](../../wiki/technical-infrastructure/master-playbook-prompt) — Comprehensive prompt system
- ✅ [Unified Health Monitoring](../../wiki/technical-infrastructure/unified-health-monitoring) — Integrated master plan
- ✅ [Plan Location Guide](../../wiki/technical-infrastructure/PLAN-LOCATION-GUIDE) — Quick reference
- ✅ [Research Citations](../operational/planning/RESEARCH-CITATIONS-MASTER-PROMPT) — 2025-2026 research validation
- ✅ [Integration Summary](../operational/planning/TI031-TI032-INTEGRATION-MASTER-PROMPT) — Architecture details

**Wiki Location:** [Unified Health Monitoring](/technical-infrastructure/technical-infrastructure/unified-health-monitoring)

**Estimated Effort:** 16 hours (P0: 5h, P1: 7h, P2: 4h)
**Blocked By:** None
**Next Action:** Phase 0 implementation in progress

---

## 🆕 New Items

### TI-037: TI-011 + Master Integration & Routing Transparency Fix
**Issue Home:** [TI-037](issues/ti037-master-integration/0-ISSUE.md)
**Created:** 2026-05-12
**Status:** 🔄 **IN PROGRESS** — 3 parallel agents executing
**Priority:** 🔴 **HIGH** — Consolidates orchestration systems, fixes critical bugs
**Rationale:** TI-011 meta-orchestration framework is broken (missing node configs), Master Prompt System lacks complexity-based routing, and routing-transparency has data integrity bugs causing command crashes. Three work streams initiated to consolidate architecture and fix bugs.

**Work Delegated (Parallel):**
1. **Restore TI-011 Node Configs** — Agent `a0991c30-fdeb-4ea`
   - Create `lab-specs/node-configs/{fnet1-7}/` directory structure
   - Generate `models.json` and `model-router.json` for each node
   - Verify `ti011_node_registry.py --dump` works
2. **Update Master Core-Prompt with TI-011 Integration** — Agent `8b825382-260f-440`
   - Add complexity classification step before decomposition
   - Integrate `classify_prompt.py` as pre-processing
   - Document trigger keywords for lab routing
3. **Fix Routing-Transparency Logging** — Agent `6e952201-f1f9-4ba`
   - Fix `mapEventToRoutingDecision()` — ensure all fields have defaults
   - Add Master + TI-011 event listeners
   - Fix `/routing-log`, `/routing-bill`, `/routing-stats` crashes

**Deliverables:**
- [ ] All 7 node config directories with models.json and model-router.json
- [ ] Updated core-prompt.md with TI-011 integration
- [ ] Fixed routing-transparency with no command crashes
- [ ] Status report: `wiki/operational/status/STATUS-2026-05-12-1730.md` ✅ COMPLETE
- [ ] Session notes: `wiki/operational/sessions/SESSION-NOTES-2026-05-12-1730.md`

**Architecture Decision:** Master Prompt System v2.0 remains primary orchestrator; TI-011 becomes lab-specific extension for multi-node tasks.

**Estimated Effort:** 15-20 minutes (agent execution time)
**Blocked By:** None

---

### TI-036: End-to-End Acceptance Testing — Health-Aware Decomposition + Playbook Execution Flow
**Created:** 2026-05-10
**Status:** 📋 **BACKLOG**
**Priority:** 🔴 **HIGH** — Validates entire orchestration stack after package consolidation
**Rationale:** Recent architectural consolidation (merging playbook-trigger → playbook-executor, removing duplicate decomposer/verifier agents, establishing clean separation between master-prompt-system and decompose-execute-verify) requires comprehensive end-to-end validation. Individual package tests exist, but no test suite validates the complete flow: health check → decomposition → local execution → verification → playbook execution → logging. This is critical for production confidence.

**Test Scenarios (12 Total):**

#### Scenario 1: HEALTHY → Local Execution ✅
**Given:** Orchestrator RAM <80%, CPU <4.0, Swap = 0
**When:** User prompts "monitor my portfolio positions and log the status"
**Then:**
- [ ] Health check returns HEALTHY status
- [ ] master-prompt-system routes to decompose-execute-verify
- [ ] decomposer creates plan with 3 sub-tasks (read positions, calculate exposure, log status)
- [ ] Sub-tasks execute on local model (gemma4:e4b or qwen3.5:4b)
- [ ] verifier validates each sub-task output
- [ ] All outputs marked PASS → no cloud escalation
- [ ] Final result returned to user
- [ ] Session logged to `wiki/operational/sessions/`

#### Scenario 2: STRESSED → Cloud-Low Escalation ✅
**Given:** Orchestrator RAM 85%, CPU 4.5, Swap = 0
**When:** User prompts "decompose this signal research task"
**Then:**
- [ ] Health check returns STRESSED status
- [ ] master-prompt-system triggers 2× decomposition
- [ ] decomposer runs on cloud-low (qwen3.5:397b-cloud)
- [ ] Sub-tasks routed to cloud-low tier
- [ ] verifier validates outputs on cloud-low
- [ ] Final synthesis returned to user
- [ ] Health decision logged to `wiki/operational/sessions/health-decisions.jsonl`

#### Scenario 3: CRITICAL → Cloud-High Escalation ✅
**Given:** Orchestrator RAM 94%, CPU 6.5, Swap >0
**When:** User prompts "execute the deploy playbook"
**Then:**
- [ ] Health check returns CRITICAL status
- [ ] master-prompt-system blocks local execution
- [ ] Task routed to cloud-high (kimi-k2.6 or equivalent)
- [ ] playbook-executor invoked with health bypass flag
- [ ] Playbook executes on cloud node
- [ ] Result logged with CRITICAL health warning
- [ ] Alert sent via intercom to operator

#### Scenario 4: Keyword-Triggered Playbook Execution ✅
**Given:** HEALTHY orchestrator
**When:** User prompts "deploy the application" (keyword: `deploy`)
**Then:**
- [ ] playbook-executor matches keyword to `deploy_app.yml`
- [ ] Pre-flight health check passes
- [ ] Ansible playbook executes successfully
- [ ] Playbook output captured and returned
- [ ] Execution logged to `wiki/operational/sessions/playbook-executions.jsonl`

#### Scenario 5: Direct Playbook Execution ✅
**Given:** HEALTHY orchestrator
**When:** User runs `./scripts/run-playbook.sh backup_data_v1.0`
**Then:**
- [ ] playbook-executor loads playbook by filename
- [ ] No keyword lookup performed
- [ ] Ansible executes with provided vars
- [ ] Success/failure status returned

#### Scenario 6: Decomposition → Playbook Chain ✅
**Given:** HEALTHY orchestrator
**When:** User prompts "check health, then run the fix-broken-links playbook"
**Then:**
- [ ] master-prompt-system decomposes into 2 steps
- [ ] Step 1: health-monitor checks orchestrator health
- [ ] Step 2: playbook-executor runs fix-broken-links.yml
- [ ] Chain executes sequentially
- [ ] Both steps logged with timestamps

#### Scenario 7: Verifier 2× Decomposition Request ✅
**Given:** Local model fails sub-task with 2+ independent failures
**When:** Verifier detects format drift + logic error + missing fields
**Then:**
- [ ] Verifier sends intercom.ask to orchestrator
- [ ] Orchestrator reviews failure modes
- [ ] Option A: Orchestrator agrees → decomposer re-runs with split sub-tasks
- [ ] Option B: Orchestrator declines → cloud re-run recommended
- [ ] Decision logged with rationale

#### Scenario 8: Complexity Rating Accuracy ✅
**Given:** Mixed-complexity decomposition plan
**When:** Decomposer assigns low/medium/high ratings
**Then:**
- [ ] Low complexity: single operation, structured output (e.g., "extract commands from file")
- [ ] Medium complexity: 2-3 steps, simple logic (e.g., "compare values and flag violations")
- [ ] High complexity: multi-step reasoning (e.g., "diagnose root cause from symptoms")
- [ ] High-complexity sub-tasks flagged for cloud execution or 2× pre-split

#### Scenario 9: Intercom Protocol — Orchestrator ↔ Decomposer ✅
**Given:** Ambiguous task requiring clarification
**When:** Decomposer receives "fix the thing"
**Then:**
- [ ] Decomposer sends intercom.ask with recommended interpretations
- [ ] Orchestrator responds with clarification
- [ ] Decomposer produces refined plan
- [ ] Full conversation logged

#### Scenario 10: Intercom Protocol — Orchestrator ↔ Verifier ✅
**Given:** Verifier detects over-complex sub-task
**When:** 3+ independent failure modes detected
**Then:**
- [ ] Verifier sends intercom.ask with 2× decomposition request
- [ ] Request includes: failure modes, evidence, proposed split
- [ ] Orchestrator responds within 5 minutes
- [ ] Verifier updates report based on decision

#### Scenario 11: Package Installation Cleanliness ✅
**Given:** Fresh pi installation
**When:** User runs `pi install github:carlosfrias/health-monitor`, `pi install github:carlosfrias/decompose-execute-verify`, `pi install github:carlosfrias/playbook-executor`, `pi install github:carlosfrias/master-prompt-system`
**Then:**
- [ ] All packages install without errors
- [ ] No duplicate agent definitions (verify with `pi agent list`)
- [ ] health-monitor has no psutil dependency errors
- [ ] decompose-execute-verify agents appear in `pi agent list`
- [ ] playbook-executor playbooks accessible via `pi playbook list`
- [ ] master-prompt-system prompts load without conflicts

#### Scenario 12: DRY Violation Verification ✅
**Given:** Both packages installed
**When:** Inspect agent definitions
**Then:**
- [ ] decomposer.md exists ONLY in decompose-execute-verify/agents/
- [ ] verifier.md exists ONLY in decompose-execute-verify/agents/
- [ ] master-prompt-system has NO decomposer.md or verifier.md
- [ ] master-prompt-system README references decompose-execute-verify
- [ ] No functionality lost (all features present in canonical location)

**Acceptance Criteria:**
- [ ] **AC-1 (Test Suite Created):** 12 scenario tests implemented as executable scripts or documented manual tests
- [ ] **AC-2 (Test Environment):** Isolated test workspace created (`~/tdof-e2e-test/`) with clean pi installation
- [ ] **AC-3 (All Scenarios Pass):** 12/12 scenarios execute successfully with expected outcomes
- [ ] **AC-4 (Health Integration):** Health checks correctly route to local/cloud tiers based on RAM/CPU/Swap thresholds
- [ ] **AC-5 (Decomposition Quality):** Decomposer produces atomic sub-tasks with correct complexity ratings
- [ ] **AC-6 (Verification Accuracy):** Verifier catches local model failure modes (hallucinations, format drift, missing fields)
- [ ] **AC-7 (2× Decomposition):** Over-complex sub-tasks trigger re-decomposition protocol
- [ ] **AC-8 (Intercom Coordination):** All intercom asks/replies logged with timestamps
- [ ] **AC-9 (Playbook Execution):** Keyword-triggered and direct execution both work
- [ ] **AC-10 (Package Cleanliness):** No duplicate agents, no missing features, clean installs
- [ ] **AC-11 (Documentation Updated):** Test results published to `wiki/operational/testing/TI-036-e2e-test-report.md`
- [ ] **AC-12 (Session Logs):** All test runs logged to `wiki/operational/sessions/e2e-test-session-YYYY-MM-DD.jsonl`

**Test Harness Requirements:**
```bash
# Test runner script (to be created)
technical-infrastructure/scripts/run-e2e-tests.sh

# Usage:
./run-e2e-tests.sh --all              # Run all 12 scenarios
./run-e2e-tests.sh --scenario 1,2,3   # Run specific scenarios
./run-e2e-tests.sh --health healthy   # Test with HEALTHY orchestrator
./run-e2e-tests.sh --health stressed  # Test with STRESSED orchestrator
./run-e2e-tests.sh --health critical  # Test with CRITICAL orchestrator
```

**Test Data Requirements:**
- Mock health states (HEALTHY/STRESSED/CRITICAL) via environment variables or test fixtures
- Sample playbook files for execution tests
- Mock position data for portfolio monitoring tests
- Test trigger keywords for playbook-executor tests

**Dependencies:**
- TI-031 (Health Monitoring Protocol) ✅ COMPLETE
- TI-032 (Master Prompt System) ✅ COMPLETE
- TI-035 (Keyword Router Fixes) ✅ COMPLETE
- decompose-execute-verify v2.0.0 ✅ COMPLETE
- playbook-executor v2.0.0 ✅ COMPLETE

**Estimated Effort:** 8-12 hours
- Test harness creation: 3-4h
- Scenario implementation: 3-4h
- Manual testing + validation: 2-3h
- Documentation + reporting: 1-2h

**Blocked By:** None (all prerequisite packages complete)

**Success Metrics:**
- 100% pass rate on all 12 scenarios
- Zero DRY violations (verified via file inspection)
- Health-aware routing works correctly in all 3 health states
- No package installation conflicts
- All intercom protocols functional

**References:**
- [TI-035 Acceptance Test Suite](../../../wiki/operational/testing/ti035-acceptance-test.js)
- [TI-010 Acceptance Tests](../../../wiki/operational/testing/ti010-acceptance-report.json)
- [decompose-execute-verify SKILL.md](../../packages/decompose-execute-verify/skills/decompose-execute-verify/SKILL.md)
- [master-prompt-system README](../../packages/master-prompt-system/README.md)
- [playbook-executor README](../../packages/playbook-executor/README.md)
- [health-monitor SKILL.md](../../packages/health-monitor/skills/health-monitor/SKILL.md)

---### PB-001: Add /list-domain Command to project-blueprint Skill
**Issue Home:** [PB-001](issues/pb-001-list-domain/0-ISSUE.md)
**Created:** 2026-05-07
**Status:** ✅ **IMPLEMENTED** — All deliverables complete, ready for `pi update`
**Priority:** 🟡 **MEDIUM** — Improves usability, reduces manual file inspection
**Completed:** 2026-05-07
**Rationale:** The `project-blueprint` skill provides domain management commands (`/add-domain`, `/rename-domain`, `/remove-domain`) but lacks a `/list-domain` command to list existing domains. Users must manually inspect `AGENTS.md` routing table or list `.pi/agents/` directory to discover configured domains. A dedicated command would improve discoverability and reduce friction.

**Current Workaround:**
```bash
# Manual inspection required
cat AGENTS.md | grep -A50 "Routing Table"
ls .pi/agents/
```

**Desired Behavior:**
```bash
# List all configured domains with metadata
/list-domain

# Expected output:
Configured Domains (3):
  1. bookkeeping      — invoice, payment, reconciliation, P&L
  2. position-management — position, order, risk, allocation, sizing
  3. market-research  — research, analysis, signal, backtest, data

# Or with verbose flag:
/list-domain --verbose

# Expected output:
Configured Domains (3):

bookkeeping
  Keywords: invoice, payment, reconciliation, P&L, trade logging
  Agent: bookkeeping
  Directory: ./bookkeeping/
  Agent File: .pi/agents/bookkeeping.md
  Domain Context: ./bookkeeping/AGENTS.md

position-management
  Keywords: position, order, risk, allocation, sizing, exits
  Agent: position-management
  Directory: ./position-management/
  Agent File: .pi/agents/position-management.md
  Domain Context: ./position-management/AGENTS.md

market-research
  Keywords: research, analysis, signal, backtest, data, indicators
  Agent: market-research
  Directory: ./market-research/
  Agent File: .pi/agents/market-research.md
  Domain Context: ./market-research/AGENTS.md
```

**Implementation Plan:**

1. **Create prompt file:** `prompts/list-domain.md`
   - Description: "List all configured domains in this project with keywords and metadata"
   - Argument hint: `[--verbose]` (optional flag for detailed output)
   - Instructions: Parse root `AGENTS.md` routing table, extract domain names, keywords, and file paths

2. **Update SKILL.md:** Add "List Domains" section to domain management operations
   - Document the command syntax
   - Add verification checklist
   - Include output format examples

3. **Update README.md:** Add `/list-domain` to domain management examples
   - Quick Start section
   - Usage section
   - Domain Management subsection

4. **Update package.json:** No changes needed (prompt auto-registered)

**Deliverables:**
- [x] Create `technical-infrastructure/packages/project-blueprint/prompts/list-domain.md` ✅
- [x] Add "List Domains" section to `technical-infrastructure/packages/project-blueprint/skills/project-blueprint/SKILL.md` ✅
- [x] Update `technical-infrastructure/packages/project-blueprint/README.md` with `/list-domain` examples ✅
- [x] Update `technical-infrastructure/packages/project-blueprint/prompts/README.md` to list the new prompt ✅
- [x] Update package.json version (1.0.0 → 1.0.1) ✅
- [x] Update README.md changelog with v1.0.1 entry ✅
- [x] Create acceptance test suite: `technical-infrastructure/wiki/operational/testing/pb-001-list-domain-acceptance-test.md` ✅
- [x] Update wiki documentation: `technical-infrastructure/wiki/products/project-blueprint.md` ✅
- [x] Create implementation plan: `technical-infrastructure/wiki/operational/planning/PB-001-list-domain-implementation.md` ✅

**Acceptance Criteria:**
- [x] **AC-1 (Basic Listing):** `/list-domain` outputs domain names and keywords in readable format ✅
- [x] **AC-2 (Verbose Mode):** `/list-domain --verbose` outputs full metadata (directory, agent file, domain context file) ✅
- [x] **AC-3 (Empty Project):** Returns "No domains configured" message when routing table is empty ✅
- [x] **AC-4 (Parsing Accuracy):** Correctly parses routing table from root `AGENTS.md` (handles markdown table format) ✅
- [x] **AC-5 (Count Accuracy):** Domain count matches actual number of routing table entries (excluding wiki default) ✅
- [x] **AC-6 (Non-Destructive):** Command does not modify any files (read-only operation) ✅
- [x] **AC-7 (Documentation):** README.md and SKILL.md updated with usage examples ✅
- [x] **AC-8 (Wiki Updated):** Product wiki page lists the new command ✅

**Technical Notes:**
- Parsing logic: Extract rows from markdown table in root `AGENTS.md` under "Routing Table" or "Domain Routing" section
- Skip the default wiki domain entry (it's not a user-created domain)
- Sort domains alphabetically for consistent output
- Use color coding if terminal supports it (optional enhancement)

**Dependencies:** None (standalone feature addition)

**Estimated Effort:** 2-3 hours (implementation + testing + documentation)

**References:**
- Existing domain management prompts: `prompts/add-domain.md`, `prompts/remove-domain.md`, `prompts/rename-domain.md`
- Skill documentation: `skills/project-blueprint/SKILL.md` (Domain Management section)
- Architecture reference: `skills/project-blueprint/references/architecture.md`

---

### TI-PLAYBOOK-MASTER: Master Prompt for Playbook Keyword System with Wiki Documentation
**Created:** 2026-05-05
**Status:** 🔄 **SUPERSEDED** — Integrated into [TI-032](#ti-032-integrated-health-aware-playbook-monitoring-system)
**Priority:** 🟡 **MEDIUM**
**Integration:** TI-027 (Modular AGENTS.md) + TI-030 (Phase-based decomposition) patterns integrated

**Legacy Deliverables (Completed):**
- [x] Playbook template: `technical-infrastructure/ansible/playbooks/ansible-playbook-template.yml`
- [x] Playbook template docs: `technical-infrastructure/ansible/playbooks/playbook-template.md`
- [x] Wiki structure: `technical-infrastructure/wiki/technical-infrastructure/wiki-playbook-structure.md`
- [x] Low-capacity validation: `technical-infrastructure/wiki/technical-infrastructure/low-capacity-model-validation.md`
- [x] Status monitor: `technical-infrastructure/wiki/technical-infrastructure/orchestration-status-monitor.md`
- [x] Status monitor script: `technical-infrastructure/scripts/orchestrator-status.py`
- [x] Trigger keywords: `technical-infrastructure/ansible/group_vars/trigger_keywords.yml`
- [x] Schedule config: `technical-infrastructure/orchestration/schedules.yml`

**TI-027/TI-030 Integration:**
- [x] Modular loading pattern adopted from TI-027 (79% token reduction)
- [x] Phase-based architecture adopted from TI-030 (55% → 67% token reduction)
- [x] `technical-infrastructure/ansible/playbooks/playbook-index.json` created (mirrors phase-index.json)
- [x] `technical-infrastructure/scripts/test-playbook-loading.py` created (mirrors test-phase-loading.py)
- [x] 6 playbook modules defined with 150-token budgets each

**Note:** All monitoring components + TI-027/TI-030 patterns now integrated into unified system. See TI-032 for current plan. Integration assessment: `technical-infrastructure/operational/planning/INTEGRATION-TI027-TI030-PLAYBOOK-MASTER.md`

### TI-WIKI-LINKS: Wiki Link Integrity - Fix 185 Broken Internal Links
**Created:** 2026-05-04
**Status:** 🚧 **IN PROGRESS — Phase 1 Complete (508 → 193, -62%) | Phase 2 Awaiting Content Decisions**
**Priority:** 🟡 **MEDIUM** - User experience, every 404 erodes trust
**Rationale:** Post-restructure, 185 internal links are broken (177 page links + 8 anchor links). Home page quick-access tables, README cross-references, and backlog TOC anchors all lead to 404s. A reusable test harness exists at `scripts/test-wiki-links.py` and confirms every fix.

**Progress Log (2026-05-05):**
| Metric | Initial | After Merge | After Structural Fixes | After Scripts | Current |
|--------|---------|-------------|--------------------------|---------------|---------|
| Total broken | 508 | ~506 | 508 (unified) | 203 (fixed paths) | **193** |
| page-not-found | 467+ | 467+ | 469 | 174 | **167** |
| anchor-mismatch | ~40 | ~40 | 22 | 22 | **22** |
| directory-no-index | ~30 | ~30 | 17 | 7 | **4** |

**Phase 1 Fixes Applied (bash-only, zero model inference):**
- [x] Flattened `technical-infrastructure/wiki/technical-infrastructure/` → `technical-infrastructure/wiki/` (20 files moved)
- [x] Fixed `/technical-infrastructure/technical-infrastructure/` double-prefix paths (8→0)
- [x] Fixed moved-file relative links (`../operational/` → `./operational/`) (6 files)
- [x] Fixed `../../../prompts/` → `../prompts/` source-relative links
- [x] Fixed `wiki/pi-keyword-router/` → `pi-keyword-router/` relative links
- [x] Fixed `operational/backlog-completed/` relative path in backlog-management-prompt
- [x] Fixed master-playbook-prompt.md `/prompts/` absolute links → `../../../prompts/` relative
- [x] Created `wiki/recommendations/index.md`
- [x] Installed `sshfs` on all 7 lab nodes (TI-033 prerequisite)

**Phase 2 Pending (Requires Content Decisions):**
| Issue | Count | Root Cause | Decision Needed |
|-------|-------|-----------|----------------|
| Source-file refs in wiki/index.md | 167 | Links to `prompts/`, `operational/testing/`, `operational/status/` — outside VitePress tree | Convert to `<code>` blocks? Create wiki pages? Use external link syntax? |
| Anchor mismatches | 22 | Anchors pointing to source files outside wiki tree | Same as above |
| Directory listings (prompts, pi-keyword-router, recommendations) | 4 | `prompts/` dir not in wiki tree | Create symlink? Create wiki page? |

**Plan Decomposition:**
- Master Prompt: `wiki/operational/planning/prompts/PROMPT-TI-WIKI-LINKS.md`
- Step 001: Fix home page table links → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-001.md`
- Step 002: Fix README cross-references → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-002.md`
- Step 003: Fix model-assignment-strategy → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-003.md`
- Step 004: Fix all anchor links → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-004.md`
- Step 005: Add missing directory index.md → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-005.md`
- Step 006: Final verification + CI → `wiki/operational/planning/plan-steps/STEP-TI-WIKI-LINKS-006.md`

**Test Harness:** `scripts/test-wiki-links.py` - reusable Python, runs against `.vitepress/dist/`

**Verification Command:**
```bash
npm run build && python3 scripts/test-wiki-links.py
```

**Estimated Effort:** 2-3 hours (step-by-step, commit per category)
**Blocked By:** None
**Orchestration Note:** Can be delegated to lab nodes (fnet3-fnet6) for step execution. Orchestrator retains verification authority.

---
## 🚧 Project Plan: Gist Message System Refactoring (Protocol/Queue Split)

**Goal:** To decouple the message message **definition** (the contract) from the message **transportation logic** (the implementation). This ensures that the protocol can evolve independently of the queue code, maintaining architectural clarity and testability.

**Status:** 📝 Planning - Requires Review and Development

---

### 🎯 Architectural Vision

We are shifting from a monolithic message handling system to a two-package dependency structure:

1.  **`gist-message-protocol`:** The **Contract Layer**. This package will contain only message schema definitions (e.g., JSON/YAML schemas), type declarations, and example usage. It *cannot* contain executable logic. Its purpose is to define *what* a message looks like.
2.  **`gist-message-queue`:** The **Implementation Layer**. This package handles all runtime concerns: connecting to the message bus, serialization/deserialization, validation, and business logic involving messages. It explicitly depends on `gist-message-protocol`.

### ⚙️ Implementation Steps

**Step 1: Cleanse the Protocol Package (`gist-message-protocol`)**
*   **Action:** Delete all current executable source code from `src/` (e.g., removal of `messages.py` with logic).
*   **Replacement:** Introduce `schemas/` directory containing definitive, machine-readable message schemas for all message types (e.g., `v1.json`).
*   **Documentation:** Update `README.md` to explicitly state that this package is a definition layer and is not executable.
*   **Result:** A read-only definition repository.

**Step 2: Update the Queue Package (`gist-message-queue`)**
*   **Dependency Management:** Add `gist-message-protocol = "^1.0.0"` as a required dependency in the queue package's `pyproject.toml`.
*   **Code Migration:** Update all internal `import` statements: any message type reference must be migrated from local definitions to imports from `gist-message-protocol`.
*   **Robustness:** Implement proactive message validation logic within the queue package's sending/receiving pathways, using the schemas from the protocol package (e.g., using a validator library against the defined schema).
*   **Result:** The queue is now actively validated against a separate, defined contract.

**Step 3: Release & Documentation**
*   **Versioning:** Coordinate distinct version bumps for both packages upon release.
*   **Documentation:** Update the top-level library documentation to clearly present this modular architecture, explaining the roles of the Protocol and the Queue package.

### ⚠️ Risks and Mitigation

*   **Risk:** Breaking existing consumers who expected merged functionality.
    *   **Mitigation:** Treat the initial phase as a parallel development track; avoid deprecating the old structure until the new versions pass comprehensive integration testing.
*   **Risk:** Confusion around required files/existence.
    *   **Mitigation:** Use explicit instructions in the build/setup documentation pointing to the correct package to enforce the new separation.

---
### TI-023-STANDALONE — Package decompose-watcher as pi skill

| Field | Value |
|-------|-------|
| **ID** | TI-023-STANDALONE |
| **Priority** | Low |
| **Status** | Backlog |
| **Domain** | technical-infrastructure |
| **Description** | Convert `decompose-watcher.py` (527-line script) into a proper pi skill package at `technical-infrastructure/packages/decompose-watcher` that can be installed via `pi install`. |
| **Current State** | Loose script at `technical-infrastructure/scripts/decompose-watcher.py` (19,499 bytes). Manages `~/.pi/decomposition-triggers/` directory with pending/completed/failed/plans subdirs. Monitors for JSON trigger files and dispatches to lab nodes. |
| **Required** | - package.json with pi section<br>- SKILL.md with usage instructions<br>- Agent definition for decompose-watcher<br>- References docs explaining trigger system<br>- `~/.pi/decomposition-triggers/` is local data dir (not part of package)<br>- Clean any orphaned stress-test artifacts from `~/.pi/decomposition-triggers/` |
| **Blocked By** | — |
| **Depends On** | — |
| **Estimated Effort** | ~8 hours |
| **Notes** | This is separate from the `decompose-execute-verify` skill. That skill provides the decomposition pattern (agents + chains). This would be a standalone stress-test/dispatch tool that writes trigger files and watches for them. Consider whether it should be part of decompose-execute-verify instead of separate. |

### TI-032 — Fix health-monitor Python dependency for zero-config install

| Field | Value |
|-------|-----|
| **ID** | TI-032 |
| **Priority** | **HIGH** |
| **Status** | Backlog |
| **Domain** | technical-infrastructure |
| **Description** | Resolve the `psutil` Python dependency so the `health-monitor` skill is **fully functional immediately after `pi install`** without requiring manual `pip install psutil`. |
| **Current State** | Skill installs successfully via `pi install`, but core scripts (`orchestrator_health.py`, `health_aware_executor.py`) fail at runtime with `ModuleNotFoundError: psutil`. This breaks the primary use case (health checking) for users who don't have psutil pre-installed. |
| **Required** | Choose and implement ONE of:<br><br>**Option A — Vendor psutil:** Include a minimal vendorized copy of psutil's core functions (RAM/CPU/swap) directly in the package, eliminating the external dependency entirely.<br><br>**Option B — Shell fallback:** Modify `orchestrator_health.py` to auto-detect missing psutil and fall back to native shell commands (`vm_stat`, `sysctl`, `/proc/meminfo`, `/proc/loadavg`) with identical JSON output format.<br><br>**Option C — Post-install hook:** Add npm `postinstall` script that runs `pip install psutil` automatically after `pi install` completes. Must handle pip not found, permission errors, and virtual environments gracefully.<br><br>**Option D — Split package:** Separate the psutil-dependent scripts into an optional sub-package (`health-monitor-core`) while keeping the rest (orchestrator-status, gist_lag_monitor, playbooks) in the main package that works out-of-the-box. |
| **Blocked By** | — |
| **Depends On** | — |
| **Estimated Effort** | 2–4 hours |
| **Notes** | The SKILL.md documentation already includes comprehensive Python dependency explanations and 3 fallback options (shell commands, Ansible-only, orchestrator-status.py). However, **documentation is not a substitute for functionality** — users expect `pi install` + immediate use. The fix must make the default path work without manual steps. Preference is for Option B (shell fallback) as it has zero external dependencies and works on macOS/Linux immediately. |

### SVC-MIG-001 — Extract Playbook Logic to Standalone Microservice

| Field | Value |
|-------|--------|
| **ID** | SVC-MIG-001 |
| **Priority** | **HIGH** |
| **Status** | Backlog |
| **Domain** | technical-infrastructure |
| **Description** | Extract Playbook logic into a standalone microservice/package (`Playbook Core`) to reduce risk during migration. The new service must **not** require the old system; instead, use a Facade/Adapter pattern with a **Feature Flag** controlled by `USE_NEW_PLAYBOOK_CORE`. All Playbook callers must call the new service through `IPlaybookAdapter`, not directly. |
| **Current State** | Playbook logic is monolithic within the main application. Any change to the core playbook workflow requires a full redeployment with high risk. |
| **Migration Plan** | **Phase 1: Discovery & Blueprinting**<br>Map all callers and data contracts. Identify dependencies (`Validation`, `Notification`, `StateManagement`). Create architecture blueprint.<br><br>**Phase 2: Mock & Shadow**<br>Implement `PlaybookCore` with stub/mock implementations. Add `IPlaybookAdapter` layer that executes BOTH old and new logic simultaneously in shadow mode.<br><br>**Phase 3: Feature Flag**<br>Implement `USE_NEW_PLAYBOOK_CORE` flag. **Initial State = OFF** (all calls go through legacy). **Validation State = ON** for shadow comparison only.<br><br>**Phase 4: Cutover & Decommission**<br>Toggle flag ON. Run parallel validation for ~2 weeks. Remove old playbook code paths once validated. Retire legacy code. |
| **Test Artifacts** | 1. Feature Flag config (`USE_NEW_PLAYBOOK_CORE`)<br>2. `IPlaybookAdapter` implementation<br>3. `PlaybookCore` service stub (v1.0)<br>4. Shadow test logs (legacy vs new path) |
| **Success Criteria** | 1. Shadow test passes: legacy output == new output (100%)<br>2. New service deployed to staging<br>3. Feature flag ON for 2 weeks in staging<br>4. Production cutover successful |
| **Dependencies** | Cloud resource setup<br>Service Mesh/API Gateway<br>Monitoring & logging infrastructure |
| **Risk Mitigation** | • **Strangler Fig Pattern**: New service runs in parallel, doesn't replace old immediately<br>• **Feature Flag**: Immediate rollback path if discrepancy detected<br>• **Shadow Testing**: Both paths produce logs, allows validation before traffic shift<br>• **Stub Implementation**: New code can be tested without affecting production |
| **Estimated Effort** | **3–4 sprints** (Dependency Mapping & Development & Testing & Cutover) |
| **Notes** | • This is a **critical migration project** due to risk<br>• Must use **Dependency Injection** to abstract service consumption<br>• **No direct calls** to old logic allowed during validation phase<br>• Feature flag must be **toggled OFF** if any discrepancy occurs |

---

## Archive Reference

**Completed items:** 14 items archived to [`wiki/operational/backlog-completed/technical-infrastructure-BACKLOG.md`](../../../wiki/operational/backlog-completed/technical-infrastructure-BACKLOG.md)

**Archived Items Include:**
- TI-019: LLM-Driven Recursive Decomposition ✅
- TI-030: Decompose AGENTS.md for Local Low-Cloud Model Ingestion ✅
- TI-009: Local Network Orchestration (Task Distribution System) ✅
- TI-001: Ansible Vault for Secure Sudo Password Management ✅
- TI-016: Expand local-model-pilot for Lab Nodes ✅
- TI-023: Orchestrator Health Monitoring + Workload Redistribution ✅
- TI-021: Model Cache Cleanup (Ollama Pruning) ✅
- TI-003: Hardware Spec JSON Refresh ✅
- TI-026: Fix Keyword Router Extension Installation ✅
- TI-027: Modular AGENTS.md for Low Model Efficiency ✅
- TI-033: Lab Node SSHFS Mount Capability ✅
- SSHFS-ACCESSIBLE: Pi Skill Package ✅
- TI-028: Clean Up Deprecated model-router.json Files ✅

---

**Backlog Management:** See [`wiki/operational/backlog-management-prompt.md`](../../../wiki/operational/backlog-management-prompt.md) for maintenance procedures.
