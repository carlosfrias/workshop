# Linear Script: refine-agents (Post-Completion)

**Target Tier:** <8K (Low Capacity)
**Token Budget:** ~1.5KB
**Objective:** Refine a domain AGENTS.md from completed session artifacts, extracting the golden path.

## Context
The Learning Loop: PROMPT → Execute → Session Notes → Post-Completion AGENTS → Future PROMPTs skip discovery.

Two types of AGENTS files:
- **Initial**: From user interview. Predicted steps. High discovery tax.
- **Post-Completion**: From session artifacts. Proven path. Low cost.

Your job: turn "what happened" (session notes) into "how to skip discovery next time" (refined AGENTS).

## Steps

### Phase 1: Gather Artifacts
Read these files:
1. Session note (what was done)
2. Decomposition plan (what was planned)
3. Verification report (what was checked)
4. Current domain AGENTS.md (what exists now)

### Phase 2: Classify Every Action
For each action in the session, classify as:
- **Golden Path**: Necessary step that produced the correct output
- **Discovery Tax**: Wrong turn, false start, or clarification that should be skipped
- **Resolved Ambiguity**: A question that was answered — encode the answer as a rule
- **Verification Gate**: A check that caught an error — encode as a quality check

### Phase 3: Extract Golden Path
Build the minimal proven sequence:
1. Remove all Discovery Tax actions
2. Inline all Resolved Ambiguities as rules
3. Preserve Verification Gates as quality checks
4. Keep Golden Path steps in their executing order

### Phase 4: Generate AGENTS-REFINED.md
Write the refined file with:
- Same structure as the original AGENTS.md
- Golden Path steps replacing speculative steps
- New rules from Resolved Ambiguities
- New quality checks from Verification Gates
- Section: "## Battle-Tested Rules" for rules derived from experience

### Phase 5: Report Delta
Show what changed:
- Steps removed (discovery tax)
- Rules added (resolved ambiguities)
- Quality checks added (verification gates)
- Estimated efficiency gain (% of original steps that were discovery tax)

## Critical Rules
- Never auto-merge — refined file sits alongside original until human approves
- Never remove rules from original AGENTS — only ADD proven rules
- The delta report is how the human decides to merge — make it clear
- If Substance Threshold not met (minimal discovery tax), report "NOT WARRANTED"