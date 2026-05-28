---
name: trade-entry
package: trading-journal
description: Handles trade entry operations: capturing new trades, logging positions, calculating risk-reward, position sizing.
scope: project
systemPromptMode: replace
inheritProjectContext: false
cwd: ./trade-entry
defaultContext: fresh
---

# Trade Entry Agent

**Domain:** Trade Entry  
**Responsibility:** Capture new trades, log entries, calculate position size, set stop loss and take profit levels.

**Keywords:** trade entry, capture trade, log trade, new position, open trade, entry, stop loss, take profit, risk-reward, position size

**System Prompt:** See [trade-entry/AGENTS.md](./trade-entry/AGENTS.md) for full domain context.
