# TI-035: Fix Keyword-Router Keyword Collisions and Priority Inversions

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TI-035: Fix Keyword-Router Keyword Collisions and Priority Inversions
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

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
