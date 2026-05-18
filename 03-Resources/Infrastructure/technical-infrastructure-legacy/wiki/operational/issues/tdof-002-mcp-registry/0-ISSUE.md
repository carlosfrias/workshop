# TDOF-002: MCP Tool Registry

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** TBD
**Priority:** TBD

---

### TDOF-002: MCP Tool Registry
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

---

## Navigation

| Need | Location |
|------|----------|
| Back to backlog | [../BACKLOG.md](../BACKLOG.md) |
