# TDOF-003: Autonomous Agent Loop

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TDOF-003: Autonomous Agent Loop
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

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
