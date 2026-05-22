---
name: pi-cross-node-comms
description: Cross-node coordination patterns for pi agents connected via a coms-net HTTP/SSE hub. Covers discovery, delegation, reply handling, and multi-machine workflows.
---

# pi-cross-node-comms — Skill Manifest

**Size:** ~5.5KB total (decomposed). **Low-capacity models:** Load only the sections listed for your task below.

## [S-TIGHT]

Cross-node pi communication via coms-net hub. 4 tools: list, send, get, await. Never use coms_net_send to reply to inbound messages — reply normally. Same-machine? Use pi-intercom instead.

---

## LOD Loading Directive

| Model Tier | Load Strategy |
|------------|---------------|
| **Low (<4K)** | CORE only (always) + CONFIG (if setting up) |
| **Medium (~8K)** | CORE + PATTERNS + CONFIG |
| **High / Cloud** | All sections |

---

## Available Sections

| Section | File | Size | LOD | What It Covers | Load When |
|---------|------|------|-----|----------------|-----------|
| CORE | [CORE.md](CORE.md) | ~1.5KB | Low | When to use, tool reference, reply rules | Always |
| PATTERNS | [PATTERNS.md](PATTERNS.md) | ~1.8KB | Medium | Fire-and-forget, ask-and-wait, polling, workflow diagram | Implementing cross-node calls |
| CONFIG | [CONFIG.md](CONFIG.md) | ~0.7KB | Low | AGENTS.md XML snippet for hub connection | Setting up a new agent |

---

## Quick Task Routing

| Need | Load |
|------|------|
| "How do I use cross-node comms?" | CORE.md |
| "Send a message to a remote node" | CORE.md → PATTERNS.md |
| "Wait for a reply from remote node" | CORE.md → PATTERNS.md |
| "Configure agent for cross-node hub" | CORE.md → CONFIG.md |
| "Understand message flow" | PATTERNS.md (workflow diagram) |

---

*This manifest is the only file loaded by default. All other sections are demand-loaded per the LOD directive above.*