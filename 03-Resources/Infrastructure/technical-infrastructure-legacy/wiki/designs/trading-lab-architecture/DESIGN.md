# Trading Lab Multi-Agent Architecture

## Overview

Design and implement a distributed agent architecture for a 7-node trading lab cluster, combining:
- **pi-intercom** for session-to-session coordination
- **local-model-pilot** for hardware-aware model routing on each node
- **decomposition-skill** for cost-optimized task breakdown
- **Bookkeeping** for task ledger and audit trail

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Trading Lab Network                         │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Orchestrator (Main Session)                     │   │
│  │  - pi + intercom bridge                                      │   │
│  │  - decomposition skill                                       │   │
│  │  - bookkeeping (task ledger)                                 │   │
│  │  - model-router (for local tasks)                            │   │
│  └────────────────────┬─────────────────────────────────────────┘   │
│                       │ intercom                                    │
│         ┌─────────────┼─────────────┬─────────────┐                 │
│         ▼             ▼             ▼             ▼                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │
│  │  Node-01   │ │  Node-02   │ │  Node-03   │ │  Node-04   │        │
│  │  (online)  │ │  (online)  │ │  (offline) │ │  (online)  │        │
│  │            │ │            │ │  (needs    │ │            │        │
│  │ ┌────────┐ │ │ ┌────────┐ │ │   repair)  │ │ ┌────────┐ │        │
│  │ │intercom│ │ │ │intercom│ │ │            │ │ │intercom│ │        │
│  │ │ bridge │ │ │ │ bridge │ │ │            │ │ │ bridge │ │        │
│  │ └───┬────┘ │ │ └───┬────┘ │ │            │ │ └───┬────┘ │        │
│  │     │      │ │     │      │ │            │ │     │      │        │
│  │ ┌───▼──────┴─┴─┬───▼──────┴─┴────────────┴─┴─────▼────┐ │        │
│  │ │  local-model-pilot + model-router                   │ │        │
│  │ │  (Hardware-aware routing per node)                  │ │        │
│  │ └───┬──────────┬───────────┬───────────┬──────────────┘ │        │
│  │     │          │           │           │                │         │
│  │ ┌───▼──┐  ┌────▼───┐  ┌────▼───┐ ┌─────▼──┐             │         │
│  │ │qwen  │  │gemma   │  │qwen    │ │ cloud  │             │         │
│  │ │3.5:4b│  │4:e4b   │  │3:8b    │ │ esc    │             │         │
│  │ └──────┘  └────────┘  └────────┘ └────────┘             │         │
│  │            (Models per node's hardware)                │         │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘         │
│                                                                       │
│  Nodes 05, 06, 07: Similar setup (06, 07 offline)                    │
└───────────────────────────────────────────────────────────────────────┘
```

## Current State

- **Total nodes**: 7
- **Online (wired)**: 4 nodes (01, 02, 04, 05)
- **Offline**: 3 nodes (03, 06, 07) — need network remediation
- **Architecture**: Not yet implemented
- **Priority**: Connect offline nodes before deploying agents

## Target Capabilities

### 1. Distributed Task Execution
- Orchestrator dispatches tasks to specific nodes or broadcasts to all
- Each node executes with locally-optimal model (via model-router)
- Results returned via intercom

### 2. Hardware-Aware Routing
- Each node configures `local-model-pilot` based on its own RAM/GPU
- High-RAM nodes: Run larger models locally
- Low-RAM nodes: Use cloud escalation automatically
- Orchestrator doesn't track per-node model availability

### 3. Cost-Optimized Workflows
- Use `decomposition-skill` for complex multi-step tasks
- Break into sub-tasks → execute on local nodes → verify → log
- 75-85% cost reduction vs cloud-only execution

### 4. Task Ledger & Audit Trail
- All tasks logged via bookkeeping agent
- Track: task ID, target node, status, timestamps, results
- Enables retry logic for offline nodes

### 5. Offline Node Handling
- Tasks to offline nodes queue in ledger
- Periodic retry with exponential backoff
- Alert if node offline > threshold (e.g., 1 hour)

---

## Questions to Answer (Prerequisites)

Before implementation, the following must be determined:

### Network & Connectivity

**Q1: Why are nodes 03, 06, 07 offline?**
- [ ] Network misconfiguration (wrong IP, subnet, gateway)?
- [ ] Physical connectivity (cable unplugged, switch port dead)?
- [ ] OS/driver issues (network driver failed, interface down)?
- [ ] Intentional air-gap for security?
- [ ] Hardware failure (NIC dead, motherboard issue)?

**Action needed**: Run network diagnostics on offline nodes (physical access required)

**Q2: What is the network topology?**
- [ ] All nodes on same LAN subnet (e.g., 192.168.1.x)?
- [ ] Multiple subnets with routing between them?
- [ ] Some nodes behind NAT?
- [ ] VLAN segmentation?

**Action needed**: Document IP addresses, subnet masks, gateway for all 7 nodes

**Q3: Can offline nodes reach the orchestrator machine directly?**
- [ ] Yes, once network issue is fixed
- [ ] No, they're on isolated network segment
- [ ] Unknown, need to test

**Action needed**: Once online, test: `ping orchestrator` from each node

### Hardware Specifications

**Q4: What are the hardware specs for each node?**

| Node | RAM | CPU | GPU | Storage | OS |
|------|-----|-----|-----|---------|-----|
| 01   | ?   | ?   | ?   | ?       | ?   |
| 02   | ?   | ?   | ?   | ?       | ?   |
| 03   | ?   | ?   | ?   | ?       | ?   |
| 04   | ?   | ?   | ?   | ?       | ?   |
| 05   | ?   | ?   | ?   | ?       | ?   |
| 06   | ?   | ?   | ?   | ?       | ?   |
| 07   | ?   | ?   | ?   | ?       | ?   |

**Action needed**: Run `free -h`, `lscpu`, `nvidia-smi` (if NVIDIA), `lsb_release -a` on each node

**Q5: Can each node run local Ollama models?**
- [ ] Yes, all nodes have sufficient RAM (≥8GB recommended)
- [ ] Some nodes need cloud-only configuration
- [ ] Need to install Ollama on all nodes

**Action needed**: Verify Ollama installation: `ollama --version` on each node

### Agent Configuration

**Q6: Do you want symmetric or hierarchical agent setup?**
- **Symmetric**: All nodes run identical agent configuration
- **Hierarchical**: Orchestrator has full capabilities, nodes are workers only
- **Hybrid**: Nodes have different roles based on hardware

**Recommendation**: Hierarchical (simpler management, clearer responsibilities)

**Q7: What is the primary workload for the trading lab?**
- [ ] Portfolio monitoring and risk checks
- [ ] Backtesting strategies on historical data
- [ ] Live trading execution
- [ ] Market data processing and analysis
- [ ] Mixed workload (specify: ________)

**Impact**: Determines model selection, task decomposition patterns, priority

### Security & Access

**Q8: How will SSH/authentication be handled?**
- [ ] SSH key-based auth (recommended)
- [ ] Password auth (not recommended for automation)
- [ ] Certificate-based auth
- [ ] Other: ________

**Action needed**: Generate SSH keys if not already done

**Q9: Do nodes have internet access for cloud model escalation?**
- [ ] Yes, all nodes can reach Ollama Cloud
- [ ] No, only orchestrator has internet (nodes use orchestrator as proxy)
- [ ] Restricted (whitelist required)

**Impact**: Determines cloud escalation architecture

### Operational Requirements

**Q10: What are the uptime/availability requirements?**
- [ ] Best effort (nodes can go offline occasionally)
- [ ] High availability (99%+ uptime required)
- [ ] Mission critical (99.9%+, immediate alerting on failures)

**Impact**: Determines retry logic, monitoring, alerting complexity

**Q11: How should task failures be handled?**
- [ ] Retry automatically (how many times? ___)
- [ ] Alert human immediately
- [ ] Log and continue with other tasks
- [ ] Escalate to cloud model

**Q12: Do you need a monitoring dashboard?**
- [ ] Yes, real-time view of node status, task queue, model usage
- [ ] No, command-line tools are sufficient
- [ ] Later phase (start with CLI, add dashboard later)

---

## Implementation Phases

### Phase 0: Network Remediation (BLOCKING)
**Priority**: CRITICAL — Cannot proceed until complete

**Tasks**:
1. Physically access nodes 03, 06, 07
2. Diagnose network connectivity issue
3. Fix network configuration or hardware
4. Verify all 7 nodes can ping orchestrator
5. Document network topology

**Exit criteria**: All 7 nodes reachable via SSH from orchestrator

**Estimated effort**: 2-4 hours (depends on root cause)

---

### Phase 1: Infrastructure Setup
**Priority**: HIGH

**Tasks**:
1. Install Ollama on all 7 nodes
2. Install pi on all 7 nodes
3. Configure unique session names (node-01 through node-07)
4. Set up SSH key-based authentication
5. Test basic connectivity: `intercom list` from orchestrator

**Deliverables**:
- Setup script: `trading-lab-node-setup.sh`
- Configuration template: `node-settings.json.template`
- Connectivity test report

**Estimated effort**: 4-6 hours

---

### Phase 2: Model Router Configuration
**Priority**: HIGH

**Tasks**:
1. Run `local-model-pilot` on each node
2. Generate hardware-specific `models.json` and `model-router.json`
3. Test model routing on each node
4. Document per-node model availability

**Deliverables**:
- Per-node model configurations
- Model capability matrix (which models on which nodes)
- Cloud escalation configuration

**Estimated effort**: 3-4 hours

---

### Phase 3: Agent Definitions
**Priority**: MEDIUM

**Tasks**:
1. Create `trading-lab-worker` agent definition
2. Create `trading-lab-orchestrator` agent definition
3. Define intercom protocols (message formats, response patterns)
4. Create task ledger schema for bookkeeping

**Deliverables**:
- `agents/trading-lab-worker.md`
- `agents/trading-lab-orchestrator.md`
- `chains/trading-lab-task-dispatch.chain.md`
- Bookkeeping schema for task ledger

**Estimated effort**: 4-5 hours

---

### Phase 4: Decomposition Integration
**Priority**: MEDIUM

**Tasks**:
1. Create trading-lab-specific decomposition chains
2. Define verification criteria for common tasks
3. Test decompose → execute → verify workflow across nodes
4. Measure cost savings vs cloud-only execution

**Deliverables**:
- `chains/decomposed-trading-monitor.chain.md`
- `chains/decomposed-backtest.chain.md`
- Cost analysis report

**Estimated effort**: 5-6 hours

---

### Phase 5: Offline Handling & Retry Logic
**Priority**: MEDIUM

**Tasks**:
1. Implement task queue for offline nodes
2. Add exponential backoff retry logic
3. Create alerting for persistent offline nodes
4. Test failover scenarios

**Deliverables**:
- Retry logic in orchestrator agent
- Alerting configuration
- Failure scenario test report

**Estimated effort**: 4-5 hours

---

### Phase 6: Monitoring & Dashboard (Optional)
**Priority**: LOW

**Tasks**:
1. Design monitoring dashboard (if requested)
2. Implement real-time node status display
3. Add task queue visualization
4. Create usage analytics (model usage, cost tracking)

**Deliverables**:
- Monitoring dashboard (web-based or TUI)
- Usage analytics reports

**Estimated effort**: 8-12 hours

---

## Work Backlog

### Blocked (Waiting on Answers)
- [ ] **BLOCKED**: Network remediation for nodes 03, 06, 07 (waiting on Q1-Q3 answers)
- [ ] **BLOCKED**: Hardware assessment (waiting on Q4-Q5 answers)
- [ ] **BLOCKED**: Agent configuration design (waiting on Q6-Q7 answers)

### Ready to Start (No Dependencies)
- [ ] Create setup script template
- [ ] Draft agent definitions (can be refined later)
- [ ] Create bookkeeping schema for task ledger
- [ ] Document intercom protocol patterns

### Future Enhancements
- [ ] Monitoring dashboard
- [ ] Automated model synchronization across nodes
- [ ] Dynamic load balancing based on node capacity
- [ ] Integration with trading desk bookkeeping system

---

## Success Criteria

### Phase 0-3 (MVP)
- [ ] All 7 nodes online and reachable
- [ ] pi + intercom running on all nodes
- [ ] Orchestrator can dispatch tasks to any node
- [ ] Each node routes to appropriate local model
- [ ] Task results returned to orchestrator

### Phase 4-5 (Production Ready)
- [ ] Decomposition workflows operational
- [ ] Offline node handling with retry logic
- [ ] Task ledger with full audit trail
- [ ] Cost savings ≥75% vs cloud-only execution

### Phase 6+ (Enhanced)
- [ ] Monitoring dashboard operational
- [ ] Automated alerting on node failures
- [ ] Usage analytics and cost tracking

---

## Next Steps

1. **Answer prerequisite questions** (Q1-Q12 above)
2. **Complete Phase 0** (network remediation) — BLOCKING
3. **Review and approve implementation plan**
4. **Begin Phase 1** (infrastructure setup)

---

## Document History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2026-04-24 | 1.0 | Carlos Frias | Initial architecture design |

---

## Appendix A: Example Workflows

### Workflow 1: Portfolio Monitoring

```bash
# From orchestrator
/chain decomposed-trading-monitor "Monitor all trading-lab nodes"

# Decomposition Plan:
| # | Task | Target | Model (per-node routing) |
|---|------|--------|--------------------------|
| 1 | Check node-01 status | intercom → node-01 | node-01 router: monitoring profile → qwen3.5:4b |
| 2 | Check node-02 status | intercom → node-02 | node-02 router: monitoring profile → qwen3.5:4b |
| 3 | Check node-03 status | intercom → node-03 | OFFLINE → queue for retry |
| ... | ... | ... | ... |
| 8 | Aggregate results | orchestrator | orchestrator router: reasoning profile → gemma4:e4b |
| 9 | Verify aggregation | verifier | cloud: qwen3.5:cloud |
| 10 | Log to bookkeeping | bookkeeping | local: gemma4:e4b |
```

### Workflow 2: Distributed Backtesting

```bash
# From orchestrator
"Run backtest on Q1-Q4 data across available nodes"

# Decomposition:
| Task | Node | Model | Duration |
|------|------|-------|----------|
| Backtest Q1 data | node-01 | gemma4:e4b (local) | ~5 min |
| Backtest Q2 data | node-02 | gemma4:e4b (local) | ~5 min |
| Backtest Q3 data | node-04 | gemma4:e4b (local) | ~5 min |
| Backtest Q4 data | node-05 | gemma4:e4b (local) | ~5 min |
| Aggregate results | orchestrator | gemma4:e4b | ~1 min |
| Verify results | verifier | qwen3.5:cloud | ~30 sec |

# Total cost: ~$0.05 (decomposition + verification)
# vs ~$0.30 for cloud-only execution
```

---

## Appendix B: Configuration Templates

### Node Settings Template

```json
{
  "intercom": {
    "enabled": true,
    "bridgeTarget": "orchestrator",
    "sessionName": "node-XX"
  },
  "defaultProvider": "router",
  "defaultModel": "auto",
  "packages": [
    "pi-intercom",
    "@yeliu84/pi-model-router"
  ]
}
```

### Agent Definition Template

```markdown
---
name: trading-lab-worker
description: Worker agent for trading-lab node operations
tools: read, write, bash, intercom
model: ollama/qwen3.5:4b
thinking: minimal
systemPromptMode: replace
inheritProjectContext: false
inheritSkills: true
---

You are a worker agent on a trading-lab node.

## Responsibilities
1. Execute tasks received via intercom from orchestrator
2. Use local model-router for optimal model selection
3. Report results back via intercom
4. Handle offline scenarios gracefully

## Intercom Protocol
- Listen for tasks from "orchestrator"
- Execute locally using bash tools
- Reply with structured results
- If task fails, report error with details
```

---

**END OF DOCUMENT**
