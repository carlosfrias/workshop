---
name: pi-cross-node-comms
description: Cross-node coordination patterns for pi agents connected via a coms-net HTTP/SSE hub. Covers discovery, delegation, reply handling, and multi-machine workflows.
---

# pi-cross-node-comms

Coordinate with pi sessions running on **different machines** via a shared coms-net hub.

## [S-TIGHT]

Cross-node pi communication via coms-net hub. 4 tools: list, send, get, await. Never use coms_net_send to reply to inbound messages — reply normally.

## LOD Loading Directive

| Model Tier | Load |
|------------|------|
| **Low (<4K)** | CORE + Quick Reference + Configuration |
| **Medium+** | Full file (~2KB) |

---

## CORE — When to Use + Quick Reference (LOD: Low)

- Multi-machine task distribution (research, execution, monitoring)
- Fleet coordination (orchestrator + lab workers)
- Remote agent delegation
- Cross-node health checks and status aggregation

**Not when:** Same-machine coordination — use pi-intercom instead.

## Quick Reference

| Action | Tool | Blocks? |
|--------|------|---------|
| See who's online | `coms_net_list()` | No |
| Send a message | `coms_net_send({ target, prompt })` | No (returns msg_id) |
| Check for reply | `coms_net_get({ msg_id })` | No |
| Wait for reply | `coms_net_await({ msg_id })` | Yes (up to 30min) |

## PATTERNS — Communication Patterns (LOD: Medium)

### Fire-and-Forget (status update)

```typescript
coms_net_send({
  target: "orchestrator",
  prompt: "Phase 1 complete: all SSHFS mounts verified. Moving to health checks."
})
```

### Ask-and-Wait (decision needed)

```typescript
const result = coms_net_send({
  target: "orchestrator",
  prompt: "Worker swap is at 85%. Should I restart or continue monitoring?"
})
// Returns: { msg_id: "01JQK..." }

const reply = coms_net_await({ msg_id: result.msg_id })
// Returns: "Continue monitoring — restart only if swap exceeds 90% for >5min."
```

### Polling (periodic check)

```typescript
const peers = coms_net_list()
// Returns list with context usage %, model, status per peer
```

## Replying to Inbound Messages

**Do NOT use `coms_net_send` to reply to an inbound message.** The extension automatically captures your turn output and submits it as a reply. If you receive:

```
[from worker @ /home/lab] Check node health...
```

Just write your answer normally as your assistant message. The extension handles delivery back to the sender.

Only use `coms_net_send` to **initiate new conversations**.

## Cross-Machine Workflow

```
Orchestrator (macOS)          Hub (Bun server)          Worker (Ubuntu lab)
      │                            │                          │
      │── register ──────────────►│                          │
      │                            │◄───── register ──────────│
      │                            │── agent_joined (SSE) ──►│
      │◄── agent_joined (SSE) ────│                          │
      │                            │                          │
      │── coms_net_send ─────────►│── prompt (SSE) ─────────►│
      │                            │                          │
      │                            │◄── response ─────────────│
      │◄── response (SSE) ────────│                          │
```

## CONFIG — Configuration (LOD: Low)

Add to `AGENTS.md` for agents:

```xml
<coms-net>
Connected to a cross-node hub. Peers are on remote machines. Use coms_net_list to
discover available agents. Prefer coms_net_send for fire-and-forget, coms_net_await
only when blocked. NEVER use coms_net_send to reply to an inbound message — just
answer normally.

Hub project: demo
My role: worker
Available peers: orchestrator, researcher
</coms-net>
```
