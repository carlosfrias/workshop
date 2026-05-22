# PATTERNS — Communication Patterns

**Section ID:** PATTERNS
**Size:** ~1.8KB
**LOD Level:** Medium (load when implementing cross-node communication)
**Purpose:** Concrete code patterns for fire-and-forget, ask-and-wait, and polling, plus the cross-machine message flow diagram.

---

## Fire-and-Forget (status update)

Send a one-way update. No reply expected.

```typescript
coms_net_send({
  target: "orchestrator",
  prompt: "Phase 1 complete: all SSHFS mounts verified. Moving to health checks."
})
```

Use when: reporting progress, logging events, sending heartbeats.

## Ask-and-Wait (decision needed)

Send a question and block until the reply arrives.

```typescript
const result = coms_net_send({
  target: "orchestrator",
  prompt: "Worker swap is at 85%. Should I restart or continue monitoring?"
})
// Returns: { msg_id: "01JQK..." }

const reply = coms_net_await({ msg_id: result.msg_id })
// Returns: "Continue monitoring — restart only if swap exceeds 90% for >5min."
```

Use when: you need a decision or data from another node before proceeding.

## Polling (periodic check)

Discover which peers are online and their current status.

```typescript
const peers = coms_net_list()
// Returns list with context usage %, model, status per peer
```

Use when: choosing a target, checking fleet health, or before delegating work.

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

**Key points:**
- Hub is the central Bun server — all messages route through it
- Registration is automatic on startup
- SSE events propagate between nodes in real time
- Replies route back through the hub automatically