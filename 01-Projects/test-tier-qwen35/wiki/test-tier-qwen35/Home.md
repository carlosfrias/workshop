# test-tier-qwen35 Wiki

Welcome to the test-tier-qwen35 documentation wiki. This project validates and curates evidence at threshold levels using Qwen3.5 models.

## Domain Navigation

The wiki is organized by domain — domains are front and center. Each domain owns its section and is responsible for maintaining it.

### [Domain: Validation](../domain-validation/Activity Log.md)
Evidence threshold validation. Source count requirements, level classifications, and quality checks.

### [Domain: Results](../domain-results/Activity Log.md)
Results compilation and analysis. JSON output, finding synthesis, and outcome aggregation.

## Reference Pages

Project-level reference documentation is organized in `_meta/`. These pages are important but are *about* the system — they don't represent active working domains:

### [Architecture](../_meta/Architecture.md)
Why structural routing, self-contained domains, inheritProjectContext:false

### [Documentation Standard](../_meta/Documentation Standard.md)
Conventions, formatting, Activity Log format, quality checklist

### [Agent Definitions](../_meta/Agent Definitions.md)
All agents with frontmatter, descriptions, and usage

### [Sample Prompts](../_meta/Sample Prompts.md)
Ready-to-use prompts for each domain

## Workspace Map

```
test-tier-qwen35/
├── domain-validation/      # Validation domain (sources checked)
├── domain-results/         # Results domain (analysis done)
├── wiki/test-tier-qwen35/ (this wiki)
└── personal-vault/         # Human workspace
```

## Token Budget

**Session Load:** ~4KB average per task  
**Total Project Budget:** ~100K tokens (estimated)

*For efficiency, all domains use qwen3.5:4b model.*

---

*Last updated: 2026-05-22*
