# Architecture — test-tier-qwen35

Self-contained structural routing with minimal dependencies.

## High-Level Design

1. **Two-Tier Routing** — Domain AGENTS.md → domain wiki (no third tier)
2. **Minimal Context** — `inheritProjectContext: false`
3. **No Third-Tier Docs** — No `Context.md`, `QualityControl.md`, or similar
4. **Self-Contained** — Each domain owns its context, output, and rules

## Domain Structure

### Domain Validation
*Purpose:* Source count + independence audit → threshold level assignment
*Routing:* Validation domain `AGENTS.md` → Validation wiki (Activity Log.md)

### Domain Results
*Purpose:* JSON output, evidence cross-reference, synthesis compilation
*Routing:* Results domain `AGENTS.md` → Results wiki (Activity Log.md)

## Structural Principles

1. **No Duplication** — Domain AGENTS.md and wiki pages are complementary; no redundancy
2. **One-File Context** — Each domain uses one file (`AGENTS.md`) for full context
3. **Activity Log Format** — Wiki pages use a standardized Activity Log format
4. **Domain Independence** — Domains route independently; no shared files

## Output Format

All outputs are self-contained with embedded cross-references. Each domain:

1. Produces output (JSON for results, validation entry for validation)
2. Logs to Activity Log.md
3. Tags entry with relevant tags (#domain #status)

## Example Outputs

### Validation Domain
**Output Format:**
```json
{
  "id": "validation-001",
  "level": "level-1",
  "sources": 5,
  "validated": true,
  "crossReferences": ["sources/1.md", "sources/2.md", "sources/3.md", "sources/4.md", "sources/5.md"]
}
```

### Results Domain
**Output Format:**
```json
{
  "id": "analysis-001",
  "validationRef": "validation-001",
  "sources": ["sources/1.md", "sources/2.md"],
  "analysis": "Synthesized findings",
  "timestamp": "2026-05-22T14:00:00Z"
}
```

## Quality Checklist

Good outputs have all required fields, proper cross-references, and Activity Log entries.  
Bad outputs leave fields missing, lack context, or duplicate content unnecessarily.

---

*Last updated: 2026-05-22*
