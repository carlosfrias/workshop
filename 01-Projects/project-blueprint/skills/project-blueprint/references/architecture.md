# Structural Routing Architecture Reference

This is the stable reference for the architectural decisions encoded in the `project-blueprint` skill. It documents why each decision was made so that future setups don't need to re-derive them.

## 1. Why Structural Routing (Not Feature-Based Routing)

**Decision:** The routing table lives in `AGENTS.md`, not in harness-specific files like `.pi/APPEND_SYSTEM.md`.

**Rationale:**
- `AGENTS.md` is discovered by any harness that walks directories (pi, Cursor, Claude Code, etc.)
- `.pi/APPEND_SYSTEM.md` is only read by pi
- A routing table in `.pi/APPEND_SYSTEM.md` only works in pi; in `AGENTS.md` it works everywhere
- The routing table is structural (part of the project's organization), not operational (part of the harness configuration)

**Trade-off:** pi-specific features like `cwd` and `inheritProjectContext` provide stronger guarantees, but they're pi-only. The routing table provides weaker guarantees (the LLM might not follow it) but works everywhere.

**Resolution:** Use both. Structural routing in `AGENTS.md` for universality. `cwd` and `inheritProjectContext: false` for pi-specific optimization.

## 2. Why Self-Contained Domains (No Supplementary Files)

**Decision:** Each domain folder has exactly one `AGENTS.md` with everything. No `CONTEXT.md`, `REFERENCES.md`, or `QualityControl.md`.

**Rationale:**
- Pi auto-discovers `AGENTS.md` and `CLAUDE.md` via directory walk. It does NOT auto-discover custom file names.
- Multiple files per domain created confusion about which file had the right version of a rule.
- Supplementary files required explicit `reads:` directives in agent definitions, adding configuration burden.
- One file per domain is simpler to maintain, simpler to check, and simpler for new contributors to understand.

**Trade-off:** A single large `AGENTS.md` is less modular than multiple focused files. But modularity is lost anyway if the harness only auto-loads one of them.

**Resolution:** One `AGENTS.md` per domain. If a domain grows too large, split it into sub-domains with their own folders and `AGENTS.md` files, and add routing table entries.

## 3. Why `inheritProjectContext: false`

**Decision:** All domain agents set `inheritProjectContext: false`.

**Rationale:**
- With `inheritProjectContext: true` (default), the orchestrator's entire project context is injected into the sub-agent. This means the sub-agent gets a redundant copy of root `AGENTS.md` plus any other auto-discovered files.
- With `false`, the sub-agent discovers context independently via its own `cwd` walk. It still loads root `AGENTS.md` (because the walk goes up to root), but it gets the current version, not a stale copy.
- The key benefit: if `root/AGENTS.md` changes between the orchestrator's turn and the sub-agent's invocation, the sub-agent gets the latest version.
- Token savings: no redundant injection of orchestrator context.

**Trade-off:** The sub-agent doesn't see the orchestrator's conversation history. This is acceptable because:
- Sub-agents are task-focused, not conversation-aware
- If conversation history is needed, use `context: "fork"` or pass relevant context in the task description
- Intercom provides a channel for the sub-agent to ask questions if needed

## 4. Why `cwd` on Domain Agents

**Decision:** Each domain agent has `cwd: ./<domain>` in frontmatter.

**Rationale:**
- Without `cwd`, the sub-agent starts in the project root and walks up, discovering only root `AGENTS.md`. It would not auto-discover the domain's `AGENTS.md`.
- With `cwd: ./<domain>`, pi walks up from the domain directory and discovers:
  1. `./<domain>/AGENTS.md` (domain context, closest to cwd)
  2. `./AGENTS.md` (root context, walked up)
- This is a pi-specific optimization. The structural routing table in root `AGENTS.md` provides a fallback for non-pi harnesses.

**Trade-off:** `cwd` is a pi-specific setting. In other harnesses, the user or agent must follow the routing table manually.

**Resolution:** Use `cwd` for pi optimization, but always include the routing table in root `AGENTS.md` so the fallback works.

## 5. Why Minimal Orchestrator Context

**Decision:** The orchestrator carries only identity + routing table (~1.2KB).

**Rationale:**
- The orchestrator's context is permanent — loaded every turn, never released.
- Domain context (4-5KB per domain) is only needed when a task is routed to that domain.
- If domain context lives permanently in the orchestrator's context, every model call pays for it, even when the task has nothing to do with that domain.
- With multiple domains, the permanent load grows linearly. Three domains = 12-15KB permanently loaded.
- With structural routing, the orchestrator loads 1.2KB permanently. Domain context is loaded by sub-agents only when needed.

**Trade-off:** The orchestrator can't answer domain questions from memory. It must either:
- Read the domain `AGENTS.md` explicitly (adds to that turn's context)
- Delegate to a sub-agent (separate context, released after completion)

**Resolution:** For quick answers, the orchestrator can read the domain file. For substantial work, delegate to a sub-agent. The routing table tells the orchestrator where to look.

## 6. Why Default Wiki Name is `wiki`

**Decision:** The wiki directory defaults to `wiki/`, not `research/`.

**Rationale:**
- `wiki` is a universally understood term for documentation
- `research` implies a specific domain (academic/scientific research) that may not apply to all projects
- A non-technical user understands "wiki" immediately
- The wiki itself is a domain with its own `AGENTS.md` that gets a routing table entry

**Resolution:** Default to `wiki/`, allow user override via the interview phase.

## 7. Why Intercom Check-Back

**Decision:** Sub-agents are configured to check back with the orchestrator via intercom on decisions and blockers.

**Rationale:**
- Fully autonomous sub-agents can go down wrong paths without the orchestrator knowing
- Intercom provides a lightweight channel for sub-agents to ask "should I proceed with X?"
- The `delegate` agent pattern (check back on decisions and blockers) balances autonomy with oversight
- More autonomous patterns are available (e.g., `worker` which only checks back on blockers)

**Trade-off:** Check-back adds latency (waiting for orchestrator response). But it prevents costly mistakes.

**Resolution:** Default to `delegate` pattern. Allow user to choose stricter (more check-back) or looser (less) patterns per agent.

---

## 8. Why Domains Are Central in the Wiki

**Decision:** Domain wiki directories live at the root of the wiki. Project-level reference documentation lives in `_meta/`.

**Rationale:**
- Domains are the active, living content of the project — they are the reason the wiki exists
- Project-level reference pages (architecture, agent definitions, sample prompts) are "about" the system, not the work itself
- When each domain contained its own wiki (inside the domain folder), documentation and knowledge sharing became fragmented — you had to check multiple locations to understand cross-domain concerns
- By placing domains at the wiki root with a shared `_meta/` for reference, domains maintain their own space while sharing a common navigation layer
- The `_meta/` prefix signals "internal/reference" — grouped together, non-competing with domain directories

**Trade-off:** Reference pages are one extra click away (inside `_meta/` instead of wiki root). But this is the correct trade-off: domains are what users and agents interact with daily; reference pages are consulted occasionally.

**Resolution:** Domains at wiki root, reference docs in `_meta/`. The home page provides a domain index at the top and a reference navigation section below it.

---

## 9. Why Integrate Wiki and Extract Domain Operations

**Decision:** The skill provides `integrate-wiki` and `extract-domain` as first-class domain management operations alongside add, rename, and remove.

**Rationale:**
- Projects evolve. A workspace created with an older project-blueprint may have wiki content in legacy layouts (numbered pages at root, wikis inside domain folders). `integrate-wiki` restructures existing content into the domain-centric layout without losing anything.
- Domains mature and may outgrow their current project. `extract-domain` packages a domain (folder, agent, wiki, chains) as a self-contained unit that can seed a new workspace. This is the inverse of `add-domain`.
- Without `extract-domain`, the only way to share a domain between projects is manual copy — error-prone and likely to miss touchpoints (agent definitions, wiki content, chain references).
- Without `integrate-wiki`, migrating from old wiki layouts requires manual file-by-file reorganization — tedious and mistake-prone.

**Trade-off:** These operations add complexity to the skill. But they address real migration and reuse needs that arise in any project that grows over time.

**Resolution:** Both operations follow the same interview-then-execute pattern as add/rename/remove. `integrate-wiki` is non-destructive (copies, confirms before moves). `extract-domain` is read-only on the source project (never modifies the original).