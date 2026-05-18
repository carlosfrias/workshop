# Real-Time Control Patterns

Sub-agents exist on a spectrum from fully autonomous to fully supervised. This document covers the control patterns available and when to use each.

---

## The Control Spectrum

```
Autonomous ◄─────────────────────────────────────► Supervised

  fire-and-     intercom        caller_ping     direct pane    main session
  forget        ask/send        (exit+resume)   interaction    steering

  No mid-run    Sub-agent can   Sub-agent       Human types    User types
  control       message the     exits and       directly in    in main
                orchestrator     waits for       sub-agent      pi window
                                response        pane
```

---

## 1. Fire-and-Forget (No Control)

The default. Sub-agent runs to completion. You get a result or an error.

```typescript
// pi-subagents
{ agent: "scout", task: "Find all auth code" }

// No way to steer mid-run. Cancel with Ctrl+C (kills subprocess).
```

**Use when:**
- Task is well-defined and unlikely to need clarification
- You trust the agent to handle edge cases independently
- Speed is more important than oversight

---

## 2. Intercom `ask` and `send` (With pi-intercom)

Sub-agents can message the orchestrator in real-time. This requires `pi-intercom` installed and the intercom bridge enabled in `pi-subagents` config.

### `ask` — Blocks Until Response

The sub-agent sends a question and **waits** for the orchestrator to respond. The orchestrator's next turn is triggered by the incoming intercom message, so it can provide an answer.

```
Sub-agent:  intercom({ action: "ask", to: "planner", message: "Which approach?" })
            (blocks, waiting for response)
Orchestrator receives: 📨 From worker — "Which approach?"
Orchestrator responds:  intercom({ action: "send", to: "worker-session-id", message: "Use v2" })
Sub-agent unblocks with the answer and continues.
```

### `send` — Fire-and-Forget Update

The sub-agent sends a status update without waiting.

```
Sub-agent:  intercom({ action: "send", to: "planner", message: "Phase 1 done, starting phase 2" })
            (returns immediately, sub-agent continues working)
```

### How the Bridge Works

When `pi-subagents` spawns a sub-agent with the intercom bridge enabled, it:

1. Resolves the orchestrator's session name (or falls back to `subagent-chat-<id>`)
2. Injects bridge instructions into the sub-agent's system prompt, including the orchestrator target
3. Adds `intercom` to the sub-agent's tool allowlist

The injected instructions tell the sub-agent:
- **When to ask** (blocked, need decision)
- **When to send** (status update, no decision needed)
- **How to format the calls** (with `{orchestratorTarget}` resolved to the session name)

Custom bridge instructions can be provided in `~/.pi/agent/extensions/subagent/intercom-bridge-custom.md`.

### Trading Workflow Example

```yaml
# In trade-executor agent definition:
---
name: trade-executor
description: Plans trade execution and validates parameters with the orchestrator before proceeding
tools: read, write, bash, intercom
---

# Agent prompt:
**Intercom triggers:** Asks on ANY trade that exceeds risk limits or position size guidelines,
confirmation of unusual execution parameters (GTC vs day, limit price, stop level), market conditions
that conflict with the trade thesis. Sends on completed trade plans and validation results.
```

```typescript
// Inside trade-executor:
if (positionSize > riskThreshold) {
  const response = await intercom({
    action: "ask",
    to: orchestratorTarget,
    message: `Position size ${positionSize}% exceeds ${riskThreshold}% limit. Proceed anyway? Recommended: No.`
  });
  // response contains orchestrator's decision
}
```

---

## 3. `caller_ping` (pi-interactive-subagents Only)

The sub-agent **exits its session** and sends a ping. The parent receives a notification and can resume the session with a response.

```typescript
// Inside worker sub-agent:
caller_ping({ message: "Should I use v1 or v2 of the migration?" })
// → Session exits, parent gets notification

// Parent decides:
subagent_resume({ sessionPath: "/path/to/session.jsonl", message: "Use v2" })
// → Session resumes with the parent's answer
```

**Difference from intercom:** The sub-agent session **stops** until the parent resumes it. With intercom, the sub-agent blocks but stays alive, and the response arrives within the same turn.

**Use when:**
- You want explicit pause points in complex workflows
- The sub-agent should not proceed without explicit approval
- You prefer a clean handoff rather than blocking

---

## 4. Direct Pane Interaction (pi-interactive-subagents Only)

Sub-agents run in visible terminal panes. You can switch to a pane and type directly.

```
tmux session:
┌─────────────────┬──────────────────┐
│  π (orchestrator) │  π/worker (sub)  │
│                  │                  │
│  Main session    │  Working on task │
│                  │                  │
│  [switch with    │  [type here to   │
│   Ctrl+B arrows] │   give guidance] │
└─────────────────┴──────────────────┘
```

This is the most direct form of real-time control. The sub-agent's context receives your input immediately.

**Use when:**
- You want to co-pilot the sub-agent in real-time
- The task requires human judgment at multiple points
- You're debugging or exploring unfamiliar code

---

## 5. Main Session Steering (Not Sub-Agents)

Within the main pi session, you have two steering mechanisms:

| Mechanism | Key | Behavior |
|-----------|-----|----------|
| **Steering message** | Enter (while agent is working) | Delivered after current assistant turn finishes its tool calls |
| **Follow-up message** | Alt+Enter (while agent is working) | Delivered only after agent stops all work |

These do not apply to sub-agents — they control the main session's agent loop.

---

## Sub-Agent Calling Sub-Agent (Nesting)

### pi-subagents

Controlled by `PI_SUBAGENT_MAX_DEPTH` (default: 2, meaning orchestrator → sub-agent → sub-sub-agent). Set in environment or in config:

```json
// ~/.pi/agent/extensions/subagent/config.json
{
  "subagents": {
    "maxSubagentDepth": 1
  }
}
```

Per-agent `maxSubagentDepth` in frontmatter can tighten (but not relax) the inherited limit.

### pi-interactive-subagents

Controlled per-agent with `spawning: false` (blocks all sub-agent tools) or `deny-tools` (blocks specific tools).

```yaml
---
name: worker          # Can still use subagent tool
spawning: true        # (default — allowed)
---

---
name: scout           # Blocked from spawning
spawning: false
---
```

---

## Choosing the Right Control Pattern

| Situation | Pattern |
|-----------|---------|
| Fire-and-forget research task | Default (no intercom, no ping) |
| Task might need clarification | Intercom `ask` in agent prompt |
| Long task with progress updates | Intercom `send` at milestones |
| Human wants to co-pilot the sub-agent | Interactive panes (pi-interactive-subagents) |
| Sub-agent might hit blockers rarely | Intercom `ask` or `caller_ping` |
| Strict hierarchy: planner→worker→scout | Nested spawning with depth limits |
| Trading: need approval before placing orders | Intercom `ask` for trade confirmation |
| Code review: escalate critical findings | Intercom `ask` with recommended action |
| Monitoring: report status periodically | Intercom `send` at checkpoints |

---

## Intercom Check-Back Protocol (All Agents)

Every custom agent with intercom follows this protocol:

### When to Ask (blocks until response)

Use `intercom({ action: "ask", to: "<orchestratorTarget>", message: "..." })` when:
- You need a decision to proceed
- You found something unexpected that changes scope
- You are blocked on something outside your control
- There is an ambiguity with multiple valid interpretations

**Always include your recommended answer** so the orchestrator can just confirm.

### When to Send (fire-and-forget)

Use `intercom({ action: "send", to: "<orchestratorTarget>", message: "..." })` when:
- Completed a milestone or the task
- Found something time-sensitive to report
- Status update that doesn't need a decision

### Fallback

If no target is provided or intercom is unavailable, continue using best judgment and note assumptions in your output.

### Orchestrator Response Flow

```
┌──────────────┐    ask(message)    ┌──────────────────┐
│  Sub-agent   │ ──────────────────► │   Orchestrator   │
│              │                    │                  │
│              │ ◄──────────────── │  responds with   │
│              │   reply arrives    │  guidance        │
│              │   as tool result   │                  │
│  (continues  │                    │                  │
│   working)   │    send(update)   │                  │
│              │ ──────────────────►│  (no response    │
│              │                    │   needed)        │
└──────────────┘                    └──────────────────┘
```

---

## See Also

- [Sub-Agent Packages Reference](subagent-packages-reference.md) — Feature comparison of pi-subagents and pi-interactive-subagents
- [pi-intercom Setup](../guides/pi-intercom-setup.md) — Installation and configuration
- [pi-subagents Configuration](pi-subagents-config-reference.md) — Intercom bridge config and agent overrides
