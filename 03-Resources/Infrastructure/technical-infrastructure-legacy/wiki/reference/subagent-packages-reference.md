# Sub-Agent Packages Reference

Two packages provide sub-agent orchestration for pi. They can coexist and are used for different workflows.

---

## `pi-subagents` (v0.17.0) — nicobailon

**Execution model:** Sub-agents run as subprocesses (`pi --mode json`). The orchestrator waits for the result (foreground) or gets it later (background).

### Strengths

| Feature | Detail |
|---------|--------|
| **Chains** | Sequential pipelines: scout → planner → worker, with `{previous}` placeholder |
| **Parallel** | Up to 8 tasks concurrently, 4 simultaneous |
| **Parallel-in-chain** | `{ parallel: [...] }` fan-out/fan-in within chains |
| **Worktree isolation** | `worktree: true` gives each parallel agent its own git worktree |
| **Chain files** | Reusable `.chain.md` pipeline definitions |
| **Async/background** | `--bg` flag or `async: true`, status via `/subagents-status` |
| **Forked context** | `context: "fork"` starts from parent's session branch |
| **Model fallback** | `fallbackModels` tries backup models on quota errors |
| **Thinking levels** | Per-agent `thinking: high` in frontmatter |
| **Skill injection** | Per-agent `skill:` in frontmatter + runtime overrides |
| **Intercom bridge** | Injects `intercom` tool + bridge instructions into sub-agents |
| **Agents Manager TUI** | `Ctrl+Shift+A` — browse, edit, create, launch agents |
| **MCP tool support** | `tools: mcp:server:name` (with pi-mcp-adapter) |
| **Nested depth guard** | `PI_SUBAGENT_MAX_DEPTH` (default: 2 levels) |
| **Agent overrides** | Override builtin fields in settings.json without copying files |

### Slash Commands

| Command | Description |
|---------|-------------|
| `/run <agent> <task>` | Single agent |
| `/chain agent1 "task1" -> agent2 "task2"` | Sequential pipeline |
| `/parallel agent1 "task1" -> agent2 "task2"` | Concurrent |
| `/agents` or `Ctrl+Shift+A` | Agents Manager overlay |
| `/subagents-status` | Background run status overlay |

### Tool Call Modes

| Mode | Parameters | Description |
|------|-----------|-------------|
| **Single** | `{ agent: "name", task: "..." }` | One agent, one task |
| **Parallel** | `{ tasks: [{agent, task}, ...], concurrency? }` | Multiple agents concurrently |
| **Chain** | `{ chain: [{agent, task?}, ...], clarify? }` | Sequential with `{previous}` placeholder |

### Built-in Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| `scout` | Haiku | read, grep, find, ls, bash, write | Fast recon → context.md |
| `planner` | Opus (high thinking) | read, grep, find, ls, write | Implementation plans → plan.md |
| `worker` | Sonnet | (all defaults) | General implementation |
| `reviewer` | Codex (high thinking) | read, grep, find, ls, bash, edit, write | Code review |
| `context-builder` | Sonnet | read, grep, find, ls, bash, write, web_search | Requirements → context.md + meta-prompt.md |
| `researcher` | Sonnet | read, write, web_search, fetch_content, get_search_content | Web research → research.md |
| `delegate` | (inherits parent model) | (inherits) | Lightweight append-mode delegate |

---

## `pi-interactive-subagents` — HazAT

**Execution model:** Sub-agents run in visible multiplexer panes (cmux/tmux/zellij/wezterm). The orchestrator is non-blocking — it gets results via steer messages.

### Strengths

| Feature | Detail |
|---------|--------|
| **Interactive panes** | Sub-agents visible in terminal mux, you can type to them directly |
| **Async by default** | `subagent()` returns immediately, results steer back later |
| **caller_ping** | Sub-agent escalates questions to parent, parent resumes with answer |
| **subagent_resume** | Resume a previous sub-agent session |
| **session-mode** | `standalone`, `lineage-only`, or `fork` (inherits conversation) |
| **auto-exit** | Autonomous agents shut down automatically on completion |
| **spawning control** | `spawning: false` blocks nested sub-agent calls per agent |
| **Role folders** | Agent-specific `cwd` with its own `.pi/` and `CLAUDE.md` |
| **/iterate** | Fork current session into sub-agent for quick fixes |
| **/plan** | Start a planning workflow |

### Key Difference: `caller_ping`

This is the signature feature. A sub-agent that's stuck or needs a decision:

```typescript
// Inside a worker sub-agent:
caller_ping({ message: "Found two conflicting migration files — which should I use?" })
// → Sub-agent session exits
// → Parent receives steer notification: "Sub-agent Worker needs help: ..."
// → Parent resumes: subagent_resume({ sessionPath: "...", message: "Use v2" })
// → Child picks up where it left off with the parent's answer
```

### Requires a Multiplexer

You must run pi inside cmux, tmux, zellij, or WezTerm:

```bash
cmux pi                    # recommended
tmux new -A -s pi 'pi'     # alternative
zellij --session pi        # alternative
# WezTerm works natively
```

---

## Comparison

| Aspect | `pi-subagents` | `pi-interactive-subagents` |
|--------|---------------|---------------------------|
| Simple delegation | ✅ | ✅ |
| Chain/parallel pipelines | ✅ Mature | ❌ Single agent only |
| Worktree isolation | ✅ | ❌ |
| Background execution | ✅ `async: true` | ✅ In mux panes |
| Interactive steering | ❌ Sub-agent runs autonomously | ✅ Type to sub-agent in its pane |
| Child→Parent escalation | ✅ via intercom (needs pi-intercom) | ✅ via `caller_ping` |
| Parent→Child response | ✅ intercom `ask`/`send` | ✅ `subagent_resume` |
| Forked context | ✅ `context: "fork"` | ✅ `fork: true` or `session-mode: fork` |
| Agent management UI | ✅ `Ctrl+Shift+A` | ❌ (listed via `subagents_list`) |
| Chain files | ✅ `.chain.md` | ❌ |
| Nested depth guard | ✅ `PI_SUBAGENT_MAX_DEPTH` | ✅ `spawning: false` per agent |
| Model fallback | ✅ `fallbackModels` | ❌ |
| Requires mux | No | Yes |

### When to Use Which

| Need | Use |
|------|-----|
| Batch chains (scout→planner→worker) | `pi-subagents` |
| Parallel scouts | `pi-subagents` |
| Git worktree isolation for concurrent edits | `pi-subagents` |
| Interactive mid-run steering by a human | `pi-interactive-subagents` |
| Child asks parent for decisions | Either (intercom or caller_ping) |
| Quick iteration (/iterate) | `pi-interactive-subagents` |

Both packages can be installed simultaneously and used for different workflows.

---

## See Also

- [Real-Time Control Patterns](real-time-control-patterns.md) — Control spectrum from autonomous to supervised
- [pi-intercom Setup](../guides/pi-intercom-setup.md) — Intercom configuration for child→parent escalation
- [pi-subagents Configuration](pi-subagents-config-reference.md) — Config file reference and agent overrides
