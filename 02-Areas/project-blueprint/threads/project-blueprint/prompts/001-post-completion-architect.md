# 001: Post-Completion AGENTS Architecture — Kickoff

**Thread:** [0-THREAD.md](../0-THREAD.md)
**Date:** 2026-05-18 07:30
**Type:** initial
**Status after this prompt:** Feature designed and implemented — agents created, thread structure extended, Library concept defined

---

## User Prompt (verbatim)

In the same way as we raised the profile of a PROMPT, I think we need to also create support for AGENTS file creation. The AGENTS file that would be created from a PROMPT would be quite different from the AGENTS file that would be created from the context of a PROMPT, PROMPT clarifications and the session output and thinking that was required to arrive at task completion. An AGENTS file created after the work I expect would yield a direct path to task completion without the overhead required to arrive at task completion the first time the task was completed.

[User confirmed assessment, then requested implementation of:]
1. Create a post-completion-architect agent that analyzes completed sessions and generates optimized AGENTS files
2. Extend the auto-documenter to produce both session notes AND a refined AGENTS file
3. Add a new skill to the project-blueprint package for post-completion AGENTS file generation

[User then requested self-contained portability, library visibility, and domain routing clarity]

## Context

The project-blueprint system has two types of AGENTS files:
- **Initial** — Created during project setup from user interview + templates. Speculative.
- **Post-Completion** — Created after task execution from verified session artifacts. Empirical.

The learning loop was incomplete: sessions documented what happened but didn't encode how to skip discovery next time.

## Outcome

### Files Created
| File | Location | Purpose |
|------|----------|---------|
| `post-completion-architect.md` | `packages/project-blueprint/agents/` | Agent: analyzes sessions, extracts golden path, generates optimized AGENTS.md |
| `auto-documenter.md` (extended) | `packages/project-blueprint/agents/` | Agent: now produces session notes + refinement assessment with substance threshold |
| `post-completion.md` | `packages/project-blueprint/skills/project-blueprint/` | Skill: full refinement workflow, merge protocol, quality gates |
| `AGENTS-post-completion.md` | `packages/project-blueprint/skills/project-blueprint/templates/` | Template for refined AGENTS files |
| `SKILL.md` (updated) | `packages/project-blueprint/skills/project-blueprint/` | Manifest updated with post-completion routing |
| `agents/README.md` (updated) | `packages/project-blueprint/agents/` | Agent directory updated with two new agents |
| `artifacts/README.md` | `packages/project-blueprint/threads/project-blueprint/artifacts/` | Artifacts folder pattern documentation |
| `0-THREAD.md` (extended) | `packages/project-blueprint/threads/project-blueprint/` | Thread format extended with Artifacts section |

### Agents README (updated) | `packages/project-blueprint/agents/` | Agent directory updated with two new agents |

### Architecture Decisions

1. **Code lives in workshop** — All agents, skills, and templates versioned in `packages/project-blueprint/`, not in global `~/.pi/agent/`
2. **Post-completion artifacts are thread entries** — `artifacts/` subfolder in each thread holds AGENTS-REFINED.md, scaffold, and metrics
3. **Executable Library pattern** — Completed threads with verified golden paths become proactively surfaced library entries
4. **Ownership split** — project-blueprint owns implementation and threads; doc-standards-enablement documents usage
5. **Substance Threshold** — auto-documenter assesses sessions: WARRANTED (generate scaffold), FLAGGED (recommend), or NOT warranted

### Key Features

| Feature | Agent | Trigger |
|---------|-------|---------|
| Session notes | `auto-documenter` | Every decompose-execute-verify completion |
| Refinement assessment | `auto-documenter` | Substance threshold met |
| Golden path extraction | `post-completion-architect` | Scaffold exists + user invokes |
| Library surfacing | Orchestrator | Keyword match on prompt receipt |

### Learning Loop (Now Complete)

```
PROMPT → Execute → Session Notes → Post-Completion AGENTS → Future PROMPTs skip discovery
```

## Decisions Made

1. **Dual-output auto-documenter** — Preserves existing session note behavior while adding refinement assessment. Backward compatible.
2. **Scaffold-before-refine pattern** — auto-documenter provides lightweight assessment; post-completion-architect does heavy analysis. Separates concerns.
3. **Never auto-merge** — AGENTS-REFINED.md sits alongside original until human approves. Safety-first.
4. **Evidence-citation requirement** — Every rule in a refined AGENTS file must trace to a session artifact. Prevents fabrication.
5. **Conservative threshold** — When in doubt, FLAG rather than generate. Prevents noisy refinements.

## Thread Impact

This prompt establishes the foundation. Subsequent prompts will:
- Exercise the full pipeline (real session → scaffold → refine → library entry)
- Add library discovery to wiki navigation
- Document the feature in doc-standards-enablement

## Lessons

- The distinction between speculative AGENTS files and empirical ones is architecturally significant — it's the difference between a workspace that documents work and one that compounds learning
- The thread system is the natural home for post-completion artifacts — they're part of the same narrative arc
- Self-containment requires moving all artifacts into the versioned package, not relying on global agent directories
