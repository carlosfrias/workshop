# Trading Lab Multi-Agent Architecture

## Quick Start

This project defines a distributed agent architecture for a 7-node trading lab cluster using:
- **pi-intercom** — Session-to-session coordination
- **local-model-pilot** — Hardware-aware model routing per node
- **decomposition-skill** — Cost-optimized task breakdown (75-85% savings)
- **Bookkeeping** — Task ledger and audit trail

## Current Status

**⚠️ BLOCKED on Network Remediation**

- **Online nodes**: 4/7 (nodes 01, 02, 04, 05)
- **Offline nodes**: 3/7 (nodes 03, 06, 07) — need network repair
- **Next action**: Answer prerequisite questions, then fix offline nodes

## Documentation

- **[Full Design Document](DESIGN.md)** — Complete architecture, questions, implementation plan
- **`Setup Scripts`** — (To be created) Node installation scripts
- **`Agent Definitions`** — (To be created) Worker and orchestrator agents
- **`Chains`** — (To be created) Pre-built workflows

## Prerequisite Questions (Must Answer Before Implementation)

See [DESIGN.md](DESIGN.md) section **"Questions to Answer"** for the full list.

**Critical (Phase 0 - Blocking)**:
1. Why are nodes 03, 06, 07 offline?
2. What is the network topology?
3. Can offline nodes reach orchestrator once fixed?
4. Hardware specs for each node (RAM, CPU, GPU)?
5. Can nodes run local Ollama models?

**Design Decisions**:
6. Symmetric vs hierarchical agent setup?
7. Primary workload type?
8. SSH/authentication method?
9. Internet access on nodes for cloud escalation?
10. Uptime requirements?
11. Task failure handling strategy?
12. Monitoring dashboard needed?

## Implementation Phases

| Phase | Name | Status | Blocking |
|-------|------|--------|----------|
| 0 | Network Remediation | ⏳ Waiting | YES — Cannot proceed |
| 1 | Infrastructure Setup | ⏳ Pending | Phase 0 |
| 2 | Model Router Config | ⏳ Pending | Phase 0 |
| 3 | Agent Definitions | ⏳ Pending | Phase 0 |
| 4 | Decomposition Integration | ⏳ Pending | Phase 3 |
| 5 | Offline Handling | ⏳ Pending | Phase 3 |
| 6 | Monitoring Dashboard | ⏳ Pending | Optional |

## How to Use This Document

1. **Read [DESIGN.md](DESIGN.md)** — Understand the architecture
2. **Answer questions Q1-Q12** — Provide answers in DESIGN.md or as a separate document
3. **Complete Phase 0** — Fix offline nodes (physical access required)
4. **Review implementation plan** — Approve or modify phases 1-6
5. **Begin implementation** — Start with Phase 1 (infrastructure setup)

## Example Workflow

Once implemented:

```bash
# From orchestrator (your main session)
/chain decomposed-trading-monitor "Monitor all trading-lab nodes"

# Automatically:
# 1. Decomposes task into per-node checks
# 2. Dispatches via intercom to each node
# 3. Each node uses local model-router for optimal execution
# 4. Results aggregated, verified, and logged
# 5. Offline nodes queued for retry
# 6. Total cost: ~$0.05 vs ~$0.25 cloud-only
```

## Next Steps

**Immediate**:
1. Answer prerequisite questions (Q1-Q12 in DESIGN.md)
2. Physically access nodes 03, 06, 07 to diagnose network issues
3. Document network topology and hardware specs

**After Phase 0**:
4. Run setup scripts on all nodes
5. Configure intercom and model-router
6. Test basic task dispatch
7. Implement decomposition workflows

## Contact

For questions or to provide answers to prerequisite questions, reply to this document or update the DESIGN.md file directly.

---

**Version**: 1.0  
**Date**: 2026-04-24  
**Author**: Carlos Frias
