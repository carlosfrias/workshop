---
refined: "2026-05-22"
version: v1
source_sessions:
  - journal/2026-05-22-1959.md (workshop root)
  - 01-Projects/decompose-execute-verify/journal/2026-05-22-1959.md
  - 01-Projects/health-monitor/journal/2026-05-22-1959.md
  - 01-Projects/local-model-pilot/journal/2026-05-22-1959.md
  - 01-Projects/node-router/journal/2026-05-22-1959.md
  - 01-Projects/pi-intercom/journal/2026-05-22-1959.md
  - 01-Projects/sshfs-accessible/journal/2026-05-22-1959.md
assessment: WARRANTED — 6 skills decomposed with consistent golden path
---

# Refined AGENTS — Skill Decomposition Golden Path v1

**Refined:** 2026-05-22 — [[refined-agents/AGENTS-REFINED-v1.md|v1]]

## [S-TIGHT]

Skill decomposition from monolith to manifest pattern follows a consistent 7-step golden path: (1) Write SKILL.md as manifest with LOD table, (2) Extract sections into individual .md files, (3) Write MANIFEST.json for machine readability, (4) Create linear/ scripts for low-capacity models, (5) Remove embedded content from SKILL.md, (6) Verify LOD links work, (7) Git commit with descriptive message.

## Conventions (Verified)

| Convention | Evidence | Source |
|-----------|----------|--------|
| SKILL.md must be a manifest, not monolith | 6 skills successfully refactored | All decomposition sessions |
| MANIFEST.json mirrors SKILL.md sections | Machine consumers need structured metadata | pi skill loader requirements |
| LOD levels: Low (<4K), Medium (~8K), High (~32K), Cloud (>32K) | Validated across qwen3:8b, qwen3.5:9b-mlx, sonnet | local-model-pilot tier detection |
| Linear scripts required for <32K context | 4B model with linear script outperforms 8B with decomposed | doc-standards validation results |

## Rules (Battle-Tested)

| Rule | Failure Mode Prevented | Evidence |
|------|----------------------|----------|
| Never load >2 sections for low-capacity models | Context overflow, hallucinations | Validation results in doc-standards |
| MANIFEST.json must list all sections with LOD tags | Skill consumers can't auto-discover | pi extension system |
| SKILL.md summary must be ≤3 sentences | Exceeds token budget for routing | 6-skill decomposition sprint |
| Each section file must be self-contained | Cross-reference navigation exhausts low-capacity context | doc-standards validation |
| Git submodules may need `git pull --rebase` before push | Fast-forward rejection on shared repos | decompose-execute-verify push failure |

## Golden Path (Direct Execution)

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Write SKILL.md as manifest with LOD routing table | LOD table lists all sections with sizes, load conditions |
| 2 | Extract each major section into its own .md file | Each file has Summary header and LOD tag |
| 3 | Write MANIFEST.json with section metadata | Validates against JSON schema |
| 4 | Create linear/ scripts for <32K models | Each script is self-contained, no cross-refs |
| 5 | Remove embedded content from SKILL.md, keep manifest only | SKILL.md is <3KB with only routing |
| 6 | Verify all LOD links resolve correctly | Each link targets a real file with correct heading |
| 7 | Git commit with "Skill decomposition: {skill-name}" | Clean diff shows additions only |

## Quality Checklist (Verified)

- [ ] SKILL.md is ≤3KB with manifest + routing only
- [ ] Every section has `## Summary` header
- [ ] Every section has LOD loading directive
- [ ] MANIFEST.json lists all sections with correct file paths
- [ ] Linear scripts exist for tasks commonly done by low-capacity models
- [ ] No cross-references within linear scripts
- [ ] Git commit message references the skill name
- [ ] FOCUS.md updated with decomposition status

## Common Mistakes (Discovered)

| Mistake | Root Cause | Correct Approach |
|---------|-----------|-----------------|
| Leaving section content in SKILL.md | Fear of losing content during refactor | Move don't copy; SKILL.md only has routing |
| Omitting MANIFEST.json | Not needed for human readers | Required for pi skill auto-discovery |
| Writing linear scripts with cross-refs | Assuming linear models can navigate files | Each script must be fully self-contained |
| Forgetting LOD tags on section files | Assuming consumers know the tier | Every file must declare its LOD level |

## Resolved Ambiguities

| Ambiguity | Resolution | Source |
|-----------|-----------|--------|
| Manifest vs monolith pattern? | Manifest pattern wins — proven across 6 skills | All 6 decomposition sessions |
| Should SKILL.md embed any content? | No — SKILL.md is routing only | Token budget validation |
| Linear scripts or decomposed for low-capacity? | Linear scripts — validated 4B > 8B decomposed | doc-standards results |
| MANIFEST.json necessary? | Yes — machine consumers need it | pi skill system requirement |

## Delta Report

| Aspect | Before (Monolith) | After (Manifest) | Efficiency |
|--------|-------------------|-------------------|------------|
| SKILL.md size | 15-25KB | 2-3KB | ~85% reduction |
| Load time | Full skill always | On-demand sections | ~75% token savings |
| Low-capacity support | Poor (context overflow) | Excellent (linear scripts) | New capability |
| Discovery | Manual reading | MANIFEST.json auto | Machine-readable |

## Decision Rationale

The manifest + decomposed section pattern was chosen over monolith because:
1. Token budgets require progressive disclosure
2. Low-capacity models (4B) need self-contained scripts
3. Machine consumers (pi, agents) need structured metadata
4. Maintenance is easier when sections are independent files
5. 6-skill validation proves the pattern is generalizable
