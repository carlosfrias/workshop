# Phase 1: Domain Activation

**Purpose:** Scan user prompt for domain keywords and route to the correct domain AGENTS.md.
**When to load:** At the start of EVERY prompt — before any work begins.
**Target model:** qwen3.5:4b (fast, lightweight classification)

---

## Domain Activation Check — MANDATORY

Before any work: scan user prompt for keywords matching the **Domain Routing Table** below. State detected keywords and activated domain.

- **One domain matches** → Read that domain's AGENTS.md, then proceed.
- **No match** → Present potential keywords, ask user to choose domain.
- **Multiple match** → Present ambiguity, ask user to choose. Do not guess.

**Hard Rule:** No file reads, code changes, or script execution until domain is activated and its AGENTS.md is read.

## Model Routing (Quick Reference)

| Route | Model | Triggers |
|-------|-------|----------|
| ultra-reasoning | ollama/kimi-k2.6 | think deeply, comprehensive, thorough |
| reasoning | ollama/qwen3.5:397b | analyze, evaluate, decide, research, plan |
| coding | ollama/deepseek-v4-pro | code, implement, develop, debug |
| vision | ollama/qwen3-vl:235b | image, screenshot, chart, visual |
| structured | ollama/gemma4:e4b | log, reconcile, parse, format, ledger |
| monitoring | ollama/qwen3.5:4b | status, check, ping, health, monitor |
| infrastructure | ollama/qwen3:8b | server, deploy, network, ansible, node, orchestration |
| (default) | ollama/gemma4:e4b | — |

## Domain Agent File Routing

| Task keywords | Read this file |
|----------|---------------|
| servers, APIs, infrastructure, deployment, monitoring, orchestration, routing, classify, complexity, decompose, queue, worker, task, node, cluster, performance, ansible, script, bash, playbook | `./technical-infrastructure/AGENTS.md` |
| trade logging, reconciliation, P&L, accounting, balances, fees | `./bookkeeping/AGENTS.md` |
| research, analysis, signals, backtesting, data, indicators | `./market-research/AGENTS.md` |
| positions, orders, risk, allocation, sizing, exits, portfolio | `./position-management/AGENTS.md` |
| position status, monitoring, risk limits | `./position-management/AGENTS.md` |
| wiki, documentation, planning | `./wiki/AGENTS.md` |
| network troubleshooting, node offline, driver issue | `./technical-infrastructure/prompts/network-troubleshooting.md` |

After reading the domain file, follow its instructions.

## Explicit Domain Switches — Personal Vault Projects

When the user says "Switch to {ProjectName}", "activate {ProjectName}" domain, or similar explicit domain switch phrasing:

1. Scan `../personal-vault/01-Projects/` for a directory matching `{ProjectName}` (case-insensitive, partial match accepted)
2. If found, read that project's `AGENTS.md` and activate it as the current domain
3. If not found, search `../personal-vault/02-Areas/` and `../personal-vault/03-Resources/` for matching directory
4. If still not found, report back and ask user to clarify

This catch-all ensures all vault projects are reachable without adding individual entries to the routing table.

## Prompt Capture — Automatic on Domain Activation

After activating any domain (whether from the routing table or explicit switch):

1. Check the project root for `README.md` or `FOCUS.md` with `prompt_thread: active` in frontmatter
2. If `prompt_thread: active` is present:
   - Confirm a `threads/<project>/prompts/` directory exists (create if missing)
   - Capture the user's prompt verbatim in a new numbered markdown file (e.g., `001-brief-slug.md`)
   - Update `threads/<project>/0-THREAD.md` prompt sequence table
   - Update the thread's "Evolution" section with a summary of this prompt's intent
3. If `prompt_thread` is absent or set to `complete`/`abandoned`, skip capture

This makes prompt capture pipeline-automatic — no agent memory or per-domain AGENTS.md rule required.

## Next Phase

Once domain is activated, load **Phase 2: Planning** (`phase-2-planning.md`).
