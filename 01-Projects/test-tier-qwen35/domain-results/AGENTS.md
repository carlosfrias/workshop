# domain-results — Results Compilation & Analysis

## Purpose

This domain handles automated result compilation, analysis, and synthesis. All evidence that passes validation is processed here to produce final outcomes, summaries, and findings.

**Primary Use Cases:**
- Result compilation and aggregation
- Outcome analysis and interpretation
- Finding synthesis
- Summary generation

## Conventions

- **Results Format:** Structured JSON output with metadata
- **Evidence Tags:** Each result item must reference validated threshold evidence
- **Timestamps:** `YYYY-MM-DD[TechTime]` for all result metadata
- **Output Structure:** `results/{date}/{id}.json` for all findings

## Rules

### Mandatory Rules

1. **Evidence Reference** — Every result must reference its validating threshold evidence
2. **JSON Structure** — Results must follow the schema: `{ id, level, sources[], timestamp, validationRef }`
3. **Progressive Analysis** — Results build cumulatively; never delete prior validated results
4. **Synthesis First** — Multiple related results must be aggregated into a single synthesis before final delivery

### Prohibited Actions

1. **No standalone results** — Results without threshold validation are invalid
2. **No duplicate processing** — Do not re-process already compiled results
3. **No partial outputs** — Complete syntheses only; never deliver incomplete analysis

## Quality Checklist

**Good results look like:**
- Complete JSON structure with all required fields
- Proper evidence cross-references
- Accurate timestamp and metadata
- Synthesis from all related validated items

**Bad results look like:**
- Missing source references
- Incomplete JSON schema
- No timestamp or metadata
- Fragmented analysis

## Documentation Protocol

When compiling results:
1. Create entries in the domain's wiki page
2. Update Activity Log.md with timestamp, result summary, and JSON link
3. Use tags `#result-compiled` and `#analysis-complete`
4. Include cross-references to validation domain for traceability

Example entry in Activity Log.md:
```markdown
### 2026-05-22T15:00:00Z — Results Compilation Complete
**Item:** Qwen3.5 threshold analysis results
**JSON Output:** [results/2026-05-22/analysis-001.json](results/2026-05-22/analysis-001.json)
**Validation Ref:** [validation/Activity Log.md](validation/Activity Log.md) #threshold-validated level-2
**Summary:** 4 threshold-valid items synthesized into unified analysis
**Status:** READY FOR DELIVERY ✓

Related to: [results/Activity Log.md](srcs/src-2025-01-15.md)
```

## Routing References

Related to domain: **validation** — Results domain depends on validation. Before processing, consult validation domain to confirm threshold compliance.

Related to domain: **wiki/test-tier-qwen35/** — All results should be documented in the wiki. Route results documentation to `./wiki/test-tier-qwen35/domain-results/`

After results are compiled and validated, route documentation to the wiki domain for broader visibility. Consult the wiki domain AGENTS.md for full documentation protocol.

---

*Last updated: 2026-05-22*
