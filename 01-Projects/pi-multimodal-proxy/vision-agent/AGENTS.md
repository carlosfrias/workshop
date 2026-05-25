# Vision Agent Domain

Vision and image processing operations: OCR, visual analysis, diagram interpretation, screenshot analysis, chart/graph reading, and multimodal reasoning.

## Conventions

- Image inputs: Describe what you see, don't transcribe verbatim unless explicitly requested
- OCR output: Structured format (JSON, table, or bullet list) — never raw text dumps
- Confidence levels: Always flag low-confidence regions (e.g., "blurry text at coordinates X,Y")
- Coordinate system: Use (x, y) from top-left when referencing image regions
- Timestamps: US Eastern (America/New_York), format YYYY-MM-DD HH:MM

## Rules

### Must Do
- Analyze the full image before answering — scan all regions
- Quote token budget usage at end of response (e.g., "Tokens: ~1.8KB input, ~3.2KB output")
- Flag ambiguities: "Cannot determine if this is X or Y due to occlusion"
- Use structured output for data extraction (tables, JSON, lists)
- Check back via intercom if image quality prevents reliable analysis

### Must Not Do
- Never transcribe entire images verbatim (summarize key content)
- Never guess at unclear text — mark as "[illegible]" instead
- Never exceed token budget (see root AGENTS.md)
- Never skip wiki documentation for non-trivial tasks

## Quality Checklist

Before delivering results:

- [ ] Full image scanned (not just focal region)
- [ ] Token budget respected (<2KB input + <4KB output for single image)
- [ ] Output structured (not verbose prose)
- [ ] Low-confidence regions flagged
- [ ] All user questions answered explicitly
- [ ] Wiki Activity Log updated
- [ ] Intercom check-back sent if decisions needed

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Verbatim transcription of entire screenshot | Summarize key elements, quote only critical text |
| Missing text in corners or margins | Systematic scan: top-left → bottom-right grid |
| Overconfident claims on blurry regions | Add confidence qualifier: "appears to be", "likely" |
| Forgetting token count | Always append token usage to response |

## Documentation Protocol

After completing any non-trivial task, document in wiki:

**Where:** `../../wiki/pi-multimodal-proxy/vision-agent/Activity Log.md`

**Format:**
```markdown
### YYYY-MM-DD — {Task Title}

**Task**: {What was requested}
**Input**: {Image type, size, complexity}
**Outcome**: {What was extracted/analyzed}
**Tokens**: {Input KB / Output KB}
**Lessons**: {Edge cases, quality issues, tips}
```

## Routing Reference

For routing table and token budget conventions, see `../AGENTS.md`.

---

*Last updated: 2026-05-24*
