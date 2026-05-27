# {domain_name} — Refined (Post-Completion)

> **Generated:** YYYY-MM-DD from session {session_id}
> **Version:** v{N} — [versioned record](./refined-agents/AGENTS-REFINED-v{N}.md) | [latest](./refined-agents/AGENTS-REFINED.md)
> **Original AGENTS.md:** {path_to_original}
> **Efficiency gain:** {estimated % reduction in tokens/steps for repeat execution}
> **Status:** AWAITING REVIEW — sits alongside {original_agents_path}, not yet merged

{domain_description}

## [S-TIGHT]

{2-3 sentence golden-path summary: what this domain does, the proven execution sequence, and key conventions that eliminate ambiguity}

---

## Conventions (Verified)

Conventions that emerged from actual execution — all proven necessary:

- {convention_1} — *Learned from: {what went wrong before this convention existed}*
- {convention_2} — *Learned from: {discovery context}*

## Rules (Battle-Tested)

### Must Always (proven by verification failures)
- {rule_always_1} — *Failure mode prevented: {what verification caught}*
- {rule_always_2} — *Failure mode prevented: {what verification caught}*

### Must Never (proven by discovery tax)
- {rule_never_1} — *Cost of violation: {what happened when we did this}*
- {rule_never_2} — *Cost of violation: {what happened when we did this}*

## Golden Path (Direct Execution)

The proven, minimal sequence to complete this domain's primary task:

### Prerequisites
- [ ] {prerequisite_1}
- [ ] {prerequisite_2}

### Execution Sequence

| Step | Action | File/Tool | Expected Output | Verification |
|------|--------|-----------|-----------------|--------------|
| 1 | {action} | {target} | {expected} | {how to verify} |
| 2 | {action} | {target} | {expected} | {how to verify} |
| 3 | {action} | {target} | {expected} | {how to verify} |

### Post-Execution
- [ ] Write to Activity Log at `{wiki_path}`
- [ ] Run quality checklist below
- [ ] If deviations from golden path occur, flag for AGENTS.md update

## Quality Checklist (Verified)

Before considering any task complete, verify:

- [ ] {quality_check_1} — *Caught by verification: {specific example}*
- [ ] {quality_check_2} — *Caught by verification: {specific example}*
- [ ] {quality_check_3} — *Caught by verification: {specific example}*

## Common Mistakes (Discovered)

These were encountered and resolved during actual execution:

| Mistake | Symptom | Root Cause | Correct Approach |
|---------|---------|------------|-----------------|
| {mistake_1} | {what we saw} | {why it happened} | {what works} |
| {mistake_2} | {what we saw} | {why it happened} | {what works} |

## Resolved Ambiguities

Clarifications obtained during execution that prevent future confusion:

| Ambiguity | Resolution | Source |
|-----------|-----------|--------|
| {ambiguous_question} | {definitive answer} | {user clarification / session discovery} |

## Decision Rationale

Key architectural decisions made during execution — why this path, not alternatives:

| Decision | Alternatives Considered | Why This Choice |
|----------|------------------------|-----------------|
| {decision_1} | {alt_1}, {alt_2} | {rationale} |

## Delta Report

### What Changed from Original AGENTS.md

| Section | Change | Rationale |
|---------|--------|-----------|
| {section} | {added/modified/removed} | {why} |

### Efficiency Analysis

| Metric | Original AGENTS | Refined AGENTS | Improvement |
|--------|----------------|----------------|-------------|
| Steps to completion | {N} | {M} | {N-M} fewer steps |
| Ambiguity points | {N} | 0 | All resolved |
| Known failure modes | {N} | {M} | {M-N} additional covered |
| Token budget (est.) | {N}KB | {M}KB | {delta} |

## Documentation Protocol

After completing any task:
1. Write to wiki activity log at `{wiki_path}/{project_name}/{domain_name}/Activity Log.md`:

```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Golden Path Step**: {Which step(s) from above were executed}
**Deviations**: {Any departure from golden path — flag for review}
**Lessons**: {New learnings that may update this AGENTS.md}
```

2. If new mistakes or optimizations are discovered, flag for AGENTS.md update
3. If path changes significantly, request re-architecture via post-completion-architect

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).
