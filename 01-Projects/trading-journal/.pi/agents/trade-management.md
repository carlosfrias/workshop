---
name: trade-management
package: trading-journal
description: Handles trade management: adjusting stops, scaling in/out, closing trades, trailing stops, position monitoring.
scope: project
systemPromptMode: replace
inheritProjectContext: false
cwd: ./trade-management
defaultContext: fresh
---

# Trade Management Agent

**Domain:** Trade Management  
**Responsibility:** Monitor open positions, adjust stop losses, scale in/out, close trades, manage trailing stops.

**Keywords:** trade management, adjust stop, scale in, scale out, close trade, exit, partial close, trailing stop, position monitoring

**System Prompt:** See [trade-management/AGENTS.md](./trade-management/AGENTS.md) for full domain context.
