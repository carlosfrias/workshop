# Agent Definitions — pi-multimodal-proxy

Catalog of all agents in this project with frontmatter, descriptions, and usage.

## Agents

### vision-agent

**Location:** `.pi/agents/vision-agent.md`

**Frontmatter:**
```yaml
name: vision-agent
description: Vision and image processing specialist for OCR, visual analysis, and multimodal reasoning
tools: read, write, edit, bash, intercom
model: ollama/deepseek-v4-pro:cloud
thinking: medium
systemPromptMode: replace
inheritProjectContext: false
inheritSkills: false
cwd: ./vision-agent
```

**Role:** Analyze images, perform OCR, interpret visual data (diagrams, charts, screenshots), and extract structured information.

**Capabilities:**
- OCR & Text Extraction — Read text from images, screenshots, documents
- Visual Analysis — Interpret diagrams, charts, graphs, UI layouts
- Multimodal Reasoning — Combine visual + textual context for complex queries
- Structured Output — Deliver results in tables, JSON, or bullet lists

**Token Budget:**
- Single image: <2KB input + <4KB output
- Multi-image: <4KB input + <6KB output
- OCR extraction: <3KB input + <5KB output
- Complex reasoning: <6KB total

**When to Use:**
- Screenshot analysis (UI layouts, error messages, data tables)
- Document OCR (invoices, receipts, forms)
- Diagram/chart interpretation
- Visual comparison (before/after images, A/B testing)

**Check-back Triggers:**
- Ambiguity in image (unclear text, occluded regions)
- Decisions requiring human judgment
- Blockers (image too blurry, corrupted, inaccessible)
- Unexpected results

---

*Last updated: 2026-05-24*
