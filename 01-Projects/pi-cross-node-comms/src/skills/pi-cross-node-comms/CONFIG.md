# CONFIG — Agent Configuration

**Section ID:** CONFIG
**Size:** ~0.7KB
**LOD Level:** Low (load when setting up a new agent or AGENTS.md)
**Purpose:** AGENTS.md XML snippet for connecting a pi agent to a cross-node hub.

---

## AGENTS.md Configuration

Add this block to `AGENTS.md` for agents that should participate in cross-node communication:

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

**Fields to customize:**
- `Hub project` — the coms-net hub project name
- `My role` — this agent's role (orchestrator, worker, researcher, etc.)
- `Available peers` — known peer names on the hub