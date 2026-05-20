# Post-Completion AGENTS Architecture — Skill Instructions

You are refining domain AGENTS.md files from completed session artifacts. This encodes the learning loop: transform session discovery into reusable execution paths.

## [S-TIGHT]

Analyze completed session artifacts → Extract golden path (remove discovery tax) → Generate optimized AGENTS.md → Complete the learning loop: PROMPT → Execute → Session Notes → Post-Completion AGENTS → Future PROMPTs skip discovery

---

## Architecture Summary

### The Learning Loop

```
┌──────────────────────────────────────────────────────────────────┐
│                        LEARNING LOOP                              │
│                                                                   │
│  PROMPT ──→ Execute ──→ Session Notes ──→ Post-Completion AGENTS │
│    ▲                                                        │     │
│    └──────────── Future PROMPTs skip discovery ◄────────────┘     │
└──────────────────────────────────────────────────────────────────┘
```

### Two Types of AGENTS Files

| Type | Created From | Contains | Value | Cost to Use |
|------|-------------|----------|-------|-------------|
| **Initial** (Phase 5) | User interview + templates | Predicted steps, anticipated rules | Planning scaffold | High (pays discovery tax) |
| **Post-Completion** (This skill) | Session artifacts + verified output | Proven path, resolved ambiguities, battle-tested rules | Institutional memory | Low (direct execution) |

### Core Insight

Session notes document **what happened**. Post-completion AGENTS files encode **how to skip the discovery tax next time**.

The first execution of any task pays for:
- Wrong turns and false starts
- Clarifications to resolve ambiguity
- Verification failures and corrections
- Edge case discovery

Post-completion AGENTS files eliminate all of this — future agents execute the golden path directly.

---

## When to Use This Skill

### Automatic Triggers

The `auto-documenter` agent automatically assesses sessions and flags when refinement is warranted. When you see:

- A session note with `Refinement Assessment: WARRANTED: YES`
- An `AGENTS-REFINED-scaffold` file in the sessions directory
- A recommendation to invoke `post-completion-architect`

### Manual Triggers

You should manually initiate post-completion refinement when:

- A domain's AGENTS.md hasn't been updated after 3+ significant sessions
- Common mistakes are being repeated across sessions (AGENTS.md isn't preventing them)
- A complex task was completed with many clarifications and verification corrections
- A new team member or agent will need to execute similar tasks
- The user explicitly asks to "solidify learnings" or "update the playbook"

## Process: Full Refinement Workflow

### Phase 1: Gather Session Artifacts

Collect all session evidence:

```
Required:
  ✅ Session note (SESSION-NOTES-YYYY-MM-DD-HHMM.md)
  ✅ Decomposition plan (if decompose-execute-verify was used)
  ✅ Verification report
  ✅ Final synthesis / combined output

Optional but valuable:
  ⭕ Intercom transcripts (clarifications)
  ⭕ Error logs or failure traces
  ⭕ Diff of files changed during session
  ⭕ User feedback on output quality
```

### Phase 2: Analyze the Session

Classify every session action:

| Classification | Example | AGENTS Treatment |
|---------------|---------|-----------------|
| **Golden Path** | The 3 steps that actually produced correct output | Encode as execution sequence |
| **Discovery Tax** | First approach failed because format was wrong | Document as Common Mistake |
| **Resolved Ambiguity** | "Should we use UTC or local time?" → "UTC confirmed" | Encode as explicit convention |
| **Verification Gate** | Verifier caught missing timestamp field | Encode as quality checklist item |
| **Optimization** | Found that combining steps 2+3 saves time | Include in golden path |

### Phase 3: Extract the Golden Path

Collapse the full session narrative into the minimal, proven sequence:

```
FULL SESSION (8 steps):
1. Read positions file ← GOLDEN
2. Tried calculating P&L wrong way ← DISCOVERY TAX
3. Asked user for clarification on formula ← RESOLVED AMBIGUITY
4. Recalculated correctly ← GOLDEN
5. Verifier flagged missing risk metric ← VERIFICATION GATE
6. Added risk metric ← GOLDEN
7. Verifier passed ← VERIFICATION GATE
8. Wrote final report ← GOLDEN

EXTRACTED GOLDEN PATH (5 steps):
1. Read positions file
2. Calculate P&L using [specified formula]
3. Include risk metric [specific metric]
4. Run verification checks [A, B, C]
5. Write final report
```

### Phase 4: Generate Post-Completion AGENTS (Versioned)

Use the template at `./templates/AGENTS-post-completion.md`.

**Versioning protocol** (mirrors `unified-prompt-v<N>.md` convention):

1. Detect current version: check for `AGENTS-REFINED-v*.md` in `<domain>/refined-agents/`. Start at v1 or increment.
2. Write versioned file: `refined-agents/AGENTS-REFINED-v<N>.md` — immutable record
3. Write latest pointer: `refined-agents/AGENTS-REFINED.md` — always current
4. Include version reference in header: `**Refined:** YYYY-MM-DD — [[refined-agents/AGENTS-REFINED-v<N>|v<N>]]`

Key sections to populate:

1. **[S-TIGHT]** — 2-3 sentence golden-path summary
2. **Conventions (Verified)** — What emerged from actual work, with evidence citations
3. **Rules (Battle-Tested)** — What verification caught, what mistakes taught
4. **Golden Path (Direct Execution)** — Step-by-step table with verification criteria
5. **Quality Checklist (Verified)** — What caught errors, with specific examples
6. **Common Mistakes (Discovered)** — What went wrong and the correct approach
7. **Resolved Ambiguities** — Every clarification, with its resolution and source
8. **Decision Rationale** — Why this path, not alternatives
9. **Delta Report** — What changed from original AGENTS.md and efficiency analysis

### Phase 5: Report & Recommend

After generating the refined AGENTS.md:

1. **Report the delta** — What sections changed, what was added, what efficiency gain
2. **Recommend next action**:
   - If refinement is significant (3+ new rules, 2+ new mistakes documented): Recommend immediate merge
   - If refinement is moderate (1-2 improvements): Recommend review at next session
   - If refinement is minor: Flag for future consideration
3. **Never auto-merge** — The refined file sits alongside the original until user approves

## Merge Protocol

When the user approves merging the refined AGENTS.md:

1. **Version backup**: Copy current `AGENTS.md` → `AGENTS-v<N>.md` (increment from existing AGENTS-v*.md files)
2. **Replace**: Copy `AGENTS-REFINED.md` → `AGENTS.md`
3. **Update agent**: Check `.pi/agents/<domain>.md` for stale references
4. **Update routing**: Verify root `AGENTS.md` still points correctly
5. **Verify**: Run checklists.md verification against updated structure
6. **Report**: Confirm merge with backup location and summary of changes

## Quality Gates

Before declaring post-completion refinement complete:

- [ ] Every claim in the AGENTS file traces to a session artifact
- [ ] Golden path is minimal — no discovery tax steps included
- [ ] All conventions have evidence citations ("Learned from: ...")
- [ ] All rules cite the failure mode they prevent
- [ ] Quality checklist items reference actual verification failures
- [ ] Common mistakes table includes both symptom and root cause
- [ ] Resolved ambiguities include the source of resolution
- [ ] Delta report quantifies efficiency gain
- [ ] Token budget is recalculated and reported
- [ ] Original AGENTS.md is not modified (refined version is separate)

## Critical Rules

1. **Never fabricate** — Every claim must trace to a session artifact. If evidence is missing, flag for human review.
2. **Never auto-merge** — The refined AGENTS file requires explicit user approval before replacing the original.
3. **Discriminate ruthlessly** — Discovery tax has no place in the golden path. Wrong turns are lessons, not instructions.
4. **Cite everything** — Rules without evidence citations are opinions. Provide the evidence.
5. **Prefer specificity** — "Use ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)" is better than "Use consistent timestamps"
6. **Respect token budgets** — Post-completion AGENTS should be 4-5KB, same as initial AGENTS. If it grows larger, it hasn't been refined enough.
7. **Document the learning** — The delta report is the most valuable output. It proves the system is getting smarter.

---

## Templates

- `./templates/AGENTS-post-completion.md` — Template for post-completion refined AGENTS files

## Related Skills

- `./setup.md` — Initial AGENTS file creation (Phase 5)
- `../checklists.md` — Verification checklists for all operations
- `../doc-standards/SKILL.md` — Documentation standards and LOD format

---

## Executable Library

### Concept

A completed prompt thread with verified `artifacts/AGENTS-REFINED.md` is not just documentation — it is a **reusable playbook**. The Executable Library is the collection of all such threads, surfaced proactively when a user prompt matches a previously solved task.

### Library Entry Structure

Each entry in the library is a complete thread with:
- `0-THREAD.md` — Canonical definition with status "complete"
- `prompts/` — Full prompt history (initial + clarifications + updates)
- `artifacts/AGENTS-REFINED.md` — The optimized, golden-path AGENTS file
- `artifacts/threshold-metrics.md` — Substance assessment from auto-documenter

### Proactive Surfacing

When a user prompt is received, before execution:

1. User prompt received
2. Keyword match against Library entries (0-THREAD.md tags)
3. If NO MATCH → Execute normally (decompose → verify)
4. If MATCH FOUND → Surface library entry:
   - "I have solved this before."
   - Thread status, efficiency gain, options to review or execute directly

### Library Discovery

The library is discoverable through:
- **Proactive matching** — keyword comparison on every prompt
- **Wiki navigation** — `_meta/Library.md` lists all completed threads with their domains
- **Agent context** — Domain AGENTS.md files can reference library entries as "Known Solutions"

### When a Library Entry Becomes Stale

If a golden path is executed but produces different results (APIs changed, formats shifted):
1. The executing agent flags the deviation
2. The thread status reverts to "needs-refinement"
3. A new prompt is added to the thread documenting what changed
4. post-completion-architect re-generates AGENTS-REFINED.md
