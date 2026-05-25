---
title: "Intercom Coordination Workflows — Quick Start"
issue_id: INTERCOM-001
type: quickstart
last_updated: 2026-05-14
---

# Intercom Coordination Workflows — Quick Start

---

## 5-Minute Quick Start

### Step 1: Install Package

```bash
cd /Users/friasc/Cloud/workshop/technical-infrastructure/packages/intercom-coord-workflows
pi install .
```

Or from GitHub (when published):
```bash
pi install github:carlosfrias/intercom-coord-workflows
```

### Step 2: Start Named Sessions

Open **4 separate terminals**:

```bash
# Terminal 1: Orchestrator (High Cloud)
cd /Users/friasc/Cloud/workshop
pi
/name orchestrator
/model ollama/qwen3.5:397b

# Terminal 2: Worker 1 (Medium Cloud)
cd /Users/friasc/Cloud/workshop
pi
/name worker-1
/model ollama/qwen3.5:4b

# Terminal 3: Worker 2 (Low Cloud)
cd /Users/friasc/Cloud/workshop
pi
/name worker-2
/model ollama/qwen3:8b

# Terminal 4: Lab Worker (Local)
cd /Users/friasc/Cloud/workshop
pi
/name lab-worker
/model ollama/gemma4:e4b
```

### Step 3: Verify Connectivity

From **orchestrator terminal**:
```bash
intercom({ action: "list" })

# Expected output:
# orchestrator - active
# worker-1 - active
# worker-2 - active
# lab-worker - active
```

### Step 4: Run First Workflow

From **orchestrator terminal**:
```bash
/chain orchestrator-worker "Test health check on all workers"
```

Or test broadcast:
```bash
/chain multi-worker-broadcast "Send test message to all workers"
```

---

## Sample Workflows

### Workflow 1: Fleet Health Check

**Orchestrator:**
```bash
/chain multi-worker-broadcast "Health check all lab nodes: CPU, RAM, SSHFS status"
```

**Expected Flow:**
1. Orchestrator assigns nodes to workers
2. Workers check assigned nodes in parallel
3. Workers report results
4. Orchestrator aggregates and summarizes

**Duration:** ~5 minutes  
**Cost:** ~$0.12 (vs. $1.25 for all-high-cloud)

---

### Workflow 2: SSHFS Deployment

**Orchestrator:**
```bash
/chain planner-executor "Deploy SSHFS mounts on all lab nodes"
```

**Expected Flow:**
1. Planner creates 5-phase plan
2. Executor runs phases sequentially
3. Reports after each phase
4. Escalates failures for decisions
5. Final verification

**Duration:** ~15-20 minutes  
**Cost:** ~$0.30 (vs. $2.50 for all-high-cloud)

---

### Workflow 3: Portfolio Monitoring

**Orchestrator:**
```bash
/chain orchestrator-worker "Monitor portfolio positions on all lab nodes"
```

**Expected Flow:**
1. Orchestrator assigns nodes to workers
2. Workers read positions, calculate exposure
3. Workers check risk limits
4. Orchestrator aggregates results

**Duration:** ~5-7 minutes  
**Cost:** ~$0.10 (vs. $0.75 for all-high-cloud)

---

## Model Tier Guide

### When to Use Each Tier

| Tier | Model | Cost | Use For |
|------|-------|------|---------|
| **High Cloud** | `qwen3.5:397b-cloud` | ~$0.10-0.30/turn | Orchestrator, complex decisions, exceptions |
| **Medium Cloud** | `qwen3.5:4b` | ~$0.00-0.02/turn | Analysis, monitoring, data prep |
| **Low Cloud** | `qwen3:8b` | ~$0.00/turn | Simple checks, status reports |
| **Local** | `gemma4:e4b` | ~$0.00/turn | SSHFS ops, health checks, direct access |

### Cost Optimization Tips

1. **Use local workers** for simple tasks (90%+ savings)
2. **Reserve high cloud** for orchestrator only
3. **Broadcast tasks** to parallelize work
4. **Empower workers** to handle common issues without escalation

---

## Common Commands

### Session Management

```bash
# List all sessions
intercom({ action: "list" })

# Check status
intercom({ action: "status" })

# View pending asks
intercom({ action: "pending" })
```

### Message Types

```bash
# Send (fire-and-forget)
intercom.send("worker-1", "Task assigned")

# Ask (blocking, 10-min timeout)
const decision = intercom.ask("orchestrator", "Retry or skip?")

# Reply (response to ask)
intercom.reply("worker-1", "Retry once")
```

### Chain Execution

```bash
# Standard delegation
/chain orchestrator-worker "Task description"

# Broadcast to multiple workers
/chain multi-worker-broadcast "Task description"

# Multi-phase operation
/chain planner-executor "Task description"
```

---

## Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| "Session not found" | Run `/name` in target session, then `intercom.list()` |
| Ask timeout | Use `send` for non-blocking updates |
| Worker silent | Send `intercom.ask("worker", "Status?")` |
| Message not delivered | Check `intercom.list()` shows target |
| Multiple pending asks | Prioritize critical, acknowledge others |

For detailed troubleshooting: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

## Next Steps

### Learn More

1. **[Architecture](./ARCHITECTURE.md)** — System design and model tiers
2. **[Patterns](./PATTERNS.md)** — Coordination patterns and examples
3. **[Skill Docs](../../packages/intercom-coord-workflows/skills/intercom-coord-workflows/SKILL.md)** — Complete usage guide
4. **[Agents](../../packages/intercom-coord-workflows/agents/)** — Orchestrator and worker definitions

### Advanced Usage

1. **Custom chains** — Create domain-specific workflows
2. **Exception handling** — Implement robust escalation paths
3. **Cost tracking** — Monitor and optimize model costs
4. **Performance tuning** — Balance workload across workers

### Integration

1. **SSHFS Accessible** — Mount orchestrator workspace on lab nodes
2. **Health Monitor** — Integrate with infrastructure monitoring
3. **Decompose-Execute-Verify** — Use for complex task breakdown

---

## Support

- **Documentation:** See wiki/operational/issues/intercom-coord-workflows/
- **Issues:** Open GitHub issue
- **Examples:** See README.md for detailed examples

---

**Quick Start Version:** 1.0.0  
**Last Updated:** 2026-05-14  
**Maintained By:** Trading Desk Team
