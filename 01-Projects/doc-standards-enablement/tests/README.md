# Inline Decomposition TDD Test Suite

**Project:** doc-standards-enablement
**Purpose:** Validate that AGENTS.md, SKILL.md, and their downstream path chain files follow the inline decomposition pattern proven superior for models up to 32B parameters.

## Background

Phase 6 lab validation (2026-05-21/22) proved that **linear scripts enable low-capacity models to follow instructions correctly**, while the decomposed skill approach causes ALL model tiers below ~32K context to improvise rather than follow templates. The root cause: **navigation overhead in decomposed files exhausts context windows regardless of available system memory.**

See: `personal-vault/01-Projects/doc-standards/wiki/doc-standards/reference/linear-scripts/validation-results.md`

## What This Suite Tests

| Test File | What It Verifies |
|-----------|-----------------|
| `test_lod_compliance.py` | LOD headers, tier-loading directives, section size budgets, path prefix rules |
| `test_inline_decomposition.py` | Cross-reference budgets per tier, self-containment, linear script presence |
| `test_agents_md.py` | S-TIGHT headers, routing tables, path resolution, size limits |
| `test_skill_md.py` | Manifest structure, MANIFEST.json validity, size estimate accuracy, linear scripts |
| `test_path_chain.py` | Chain depth, node LOD compliance, link resolution, chain node self-containment |

## Key Metrics

| Tier | Context | Cross-Ref Budget | Path Depth | Max Section |
|------|---------|-----------------|------------|-------------|
| Low | <4K | 3 (router: 6) | 2 hops | 2KB |
| Medium | ~8K | 6 (router: 12) | 3 hops | 4KB |
| High | ~32K | 12 (router: 24) | 4 hops | 10KB |

## Running

```bash
cd workshop/01-Projects/doc-standards-enablement

# Run all tests
python3 -m pytest tests/ -v

# Run specific module
python3 -m pytest tests/test_agents_md.py -v

# Run with verbose output showing file summaries
python3 -m pytest tests/ -v --tb=short
```

## What "Inline Decomposition" Means

A file is inline-decomposable when:
1. It has **[LOD: Low/Medium/High]** markers on section headers
2. It has a **tier-based loading directive** (model tier → what to load)
3. Its **cross-reference count** stays within budget for its target tier
4. It is **self-contained** — a model can understand the file without reading references
5. It enforces **`./` prefix on navigable links** for correct path resolution

A skill is inline-decomposable when it provides both:
- **Decomposed sections** for ≥32K models (LOD-tagged files)
- **Linear scripts** (`linear/` directory) for <32K models (flat, self-contained)
