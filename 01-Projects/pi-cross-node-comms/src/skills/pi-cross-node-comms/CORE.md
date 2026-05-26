# CORE — When to Use + Quick Reference

**Section ID:** CORE
**Size:** ~1.5KB
**LOD Level:** Low (always load)
**Purpose:** Essential reference for cross-node coordination — when to use, tool reference, and reply rules.

---

## When to Use

- Multi-machine task distribution (research, execution, monitoring)
- Fleet coordination (orchestrator + lab workers)
- Remote agent delegation
- Cross-node health checks and status aggregation
- **Auto-dispatch:** Say "use fleet" to trigger full D-E-V cascade (see `use-fleet` agent)

**Not when:** Same-machine coordination — use pi-intercom instead.

## Quick Reference

| Action | Tool | Blocks? |
|--------|------|---------|
| See who's online | `coms_net_list()` | No |
| Send a message | `coms_net_send({ target, prompt })` | No (returns msg_id) |
| Check for reply | `coms_net_get({ msg_id })` | No |
| Wait for reply | `coms_net_await({ msg_id })` | Yes (up to 30min) |

## Replying to Inbound Messages

**Do NOT use `coms_net_send` to reply to an inbound message.** The extension automatically captures your turn output and submits it as a reply. If you receive:

```
[from worker @ /home/lab] Check node health...
```

Just write your answer normally as your assistant message. The extension handles delivery back to the sender.

Only use `coms_net_send` to **initiate new conversations**.