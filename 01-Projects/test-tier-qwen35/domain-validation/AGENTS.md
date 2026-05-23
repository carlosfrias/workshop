# domain-validation — Evidence Threshold Validation

## Purpose

This domain handles automated evidence validation at threshold levels. Each claim, evidence, or finding must meet minimum requirements to be considered valid at the project level.

**Primary Use Cases:**
- Evidence threshold validation
- Source verification and cross-checking
- Quality assessment
- Threshold level classification

## Conventions

- **Evidence Sources:** Minimum 3 independent sources required for Level 1 evidence
- **Threshold Levels:**
  - Level 0: Single source, uncorroborated
  - Level 1: 3+ independent sources (recommended)
  - Level 2: 5+ independent sources
  - Level 3: 10+ independent sources (gold standard)
- **Validation Format:** Use `validate()` function with explicit source counts
- **Terminology:** "Evidence", "source", "threshold", "corroborated", "valid"

## Rules

### Mandatory Rules

1. **Source Count Requirement** — No evidence can be marked valid below Level 1 without explicit justification
2. **Independent Sources** — Count only truly independent sources (different authors, different publications, not derivative)
3. **Explicit Threshold** — Every validation must explicitly state the threshold being applied

### Prohibited Actions

1. **No implicit validity** — Never mark evidence as valid without explicit threshold check
2. **No partial counts** — Do not accept partial source counts; full audit required
3. **No hedging** — Never use "probably", "likely", or "possibly" in validation output

## Quality Checklist

**Good validation looks like:**
- Clear source count (exact number)
- Explicit threshold level
- Source independence verification
- Timestamp of last validation
- Cross-reference to source files

**Bad validation looks like:**
- "Looks good" without evidence count
- Vague threshold references
- Unverified source counts
- No source file references

## Documentation Protocol

When validating evidence that meets threshold requirements:
1. Create an entry in the domain's wiki page
2. Update the Activity Log.md with timestamp and validation details
3. Tag with `#threshold-validated` and the appropriate level
4. Include cross-references to all sources

Example entry in Activity Log.md:
```markdown
### 2026-05-22T14:30:00Z — Threshold Validation Complete
**Item:** Qwen3.5 threshold validation
**Sources:** 5 independent sources identified and verified
**Level:** Level 2 (5+ sources required)
**Status:** PASSED ✓
**Cross-references:** [sources/1.md](srcs/1.md), [sources/2.md](srcs/2.md), [sources/3.md](srcs/3.md)...

Related to: [validation/Activity Log.md](srcs/src-2025-01-15.md)
```

## Routing References

Related to domain: **results** — Results domain handles the actual output generation. After validation passes, results should be routed there.

After validation is complete, document the result and route to the results domain for further processing. Consult the results domain AGENTS.md for the full output protocol.

---

*Last updated: 2026-05-22*
