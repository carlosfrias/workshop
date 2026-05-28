---
name: Infrastructure Area
summary: Workshop infrastructure projects: pi-cross-node-comms (fleet/communication), local-model-pilot, node-router, health-monitor, playbook-executor, cost-aware-routing, project-blueprint, doc-standards, decompose-execute-verify, librarian, sshfs-accessible. All projects tracked in personal-vault with workshop mirrors.
status: active
phase: "Cross-cutting: coms-net model accuracy + multimodal proxy TDD"
progress: 75
tracked: true
---

# Infrastructure Area Focus

**Last session:** 2026-05-28 — coms-net v0.2.0 released with `sanitizeModel()` + heartbeat guards. Fleet nodes fnet1–fnet7 visible in TUI footer. Multimodal proxy v1.3.0 released with 40 model-reporting tests. Cross-cutting TDD now active.

---

## Active Projects

### 1. pi-cross-node-comms — Fleet Communication Hub ✅→🟡

**Status:** v0.2.0 released, deployed on fnet2 Docker hub. 7/7 fleet nodes visible.

**Completed:**
- [x] `sanitizeModel()` server validation — rejects empty, undefined, null, whitespace, hash-like model strings
- [x] Heartbeat model preservation — empty/undefined body.model doesn't wipe good values
- [x] 9 integration tests for fleet hostnames
- [x] 18 integration tests for model accuracy
- [x] 32 TS unit tests + 11 todo documenting test harness gaps
- [x] `--` separator bug fixed in `pi-agent-standalone.sh`
- [x] Docker support in `setup-hub-on-fnet2.sh`
- [x] Project default changed from `lab` → `default`

**Remaining (coms-net side of cross-cutting):**
- [ ] Import `sanitizeModel()` into test harness `helpers.ts` so 11 `test.todo` flip to pass
- [ ] Document provider field immutability in API specs
- [ ] Cross-cutting integration tests with multimodal-proxy (see Phase 5.2 below)

### 2. pi-multimodal-proxy — Vision Proxy 🟢 (Phase 5)

**Status:** v1.3.0 released. 176 total tests. Gap audit complete. Phase 5 active.

**See:** [../../01-Projects/pi-multimodal-proxy/AGENTS.md](../../01-Projects/pi-multimodal-proxy/AGENTS.md)  
**Vault plan:** [../../../personal-vault/01-Projects/pi-multimodal-proxy/PLAN.md](../../../personal-vault/01-Projects/pi-multimodal-proxy/PLAN.md)

**Cross-cutting priorities:**
- [ ] 5.2.1 LLM model immutability under proxy activation
- [ ] 5.2.2 Vision model NOT in coms-net registration payload
- [ ] 5.2.3 Status line visibility separate from coms-net model field
- [ ] 5.2.4 SSE agent_updated preserves LLM model on proxy config change
- [ ] 5.2.5 Heartbeat model field stable under proxy vision load
- [ ] 5.3.1 Fleet node proxy active → `coms_net_list` accuracy E2E

### 3. Supporting Infrastructure (Stable)

| Project | Status | Last Action |
|---------|--------|-------------|
| local-model-pilot | ✅ Stable | Model tier routing active |
| node-router | ✅ Stable | Physical execution routing |
| health-monitor | ✅ Stable | Unified health monitoring |
| playbook-executor | ✅ Stable | Ansible playbooks for fleet |
| cost-aware-routing | ✅ Stable | Cost tracking |
| project-blueprint | ✅ Stable | Workspace scaffolding |
| doc-standards | ✅ Stable | Documentation conventions |
| decompose-execute-verify | ✅ Stable | 3-tier execution cascade |
| librarian | ✅ Stable | GitHub research scout |
| sshfs-accessible | ✅ Stable | Remote filesystem access |

---

## Cross-Cutting Concerns

### Model Accuracy Boundary

```
┌─────────────────────────────────────────────────────────────────┐
│  Fleet Node (e.g., fnet3)                                       │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  Pi Agent (LLM: qwen3.5:4b)                               │   │
│  │  ├── Registers with coms-net: model="qwen3.5:4b"        │   │
│  │  ├── Heartbeat: model preserved (sanitizeModel guard)    │   │
│  │  └── Extension: multimodal-proxy                         │   │
│  │       ├── Vision model: ollama/minicpm-o2.6              │   │
│  │       ├── Status line: "MiniCPM-o2.6 [ollama]"          │   │
│  │       └── NEVER touches coms-net model field            │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
│  coms_net_list → { node: "fnet3", model: "qwen3.5:4b" }          │
│  (NOT "ollama/minicpm-o2.6")                                     │
└─────────────────────────────────────────────────────────────────┘
```

**Invariant:** `coms-net.model === LLM_model` always. Vision model lives only in proxy config + status line.

**Test coverage needed:**
1. Unit: Proxy never calls any coms-net API (it can't — no API in ExtensionContext)
2. Integration: Simulate proxy config change → verify coms-net heartbeat unchanged
3. E2E: Live fleet node with proxy → verify `coms_net_list` shows LLM model

---

## Next Actions

1. **Write proxy unit tests** for `analyzeImages`, `analyzeVideo`, `ensureConsent`, `before_agent_start`, command handlers
2. **Write cross-cutting integration tests** using coms-net test harness + proxy mocks
3. **Run live fleet E2E** for model accuracy under proxy load
4. **Commit + release** when Phase 5 complete

---

*Last updated: 2026-05-28*