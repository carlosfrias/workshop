# Published Packages

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/published-packages.md`

| Package | Repository | Install Command | Status | Notes |
|---------|------------|-----------------|--------|-------|
| `pi-keyword-router` | `carlosfrias/pi-keyword-router` | `pi install github:carlosfrias/pi-keyword-router` | ✅ Published | Extension — developed here |
| `project-blueprint` | `carlosfrias/project-blueprint` | `pi install github:carlosfrias/project-blueprint` | ✅ Published | Skill — separate repo (general-purpose) |
| `trading-agents` | `carlosfrias/trading-agents` | `pi install github:carlosfrias/trading-agents` | 📋 Planned | Agent package — decomposer, verifier |

## Publishing Workflow

See [publishing-workflow.md](publishing-workflow.md) for the complete publishing process including:

- Development stages (local → GitHub → npm)
- Quality gates before publishing
- Common mistakes to avoid

## Package Structure

Each published package must include:

```
package-name/
├── README.md          # Installation + usage instructions
├── package.json       # Name, version, repository, license
├── src/               # Source code
├── config/            # Configuration files (namespaced)
└── tests/             # Test suite (optional but recommended)
```

## Version Naming

Follow semantic versioning (major.minor.patch):

- **Major** (1.0.0 → 2.0.0): Breaking changes
- **Minor** (1.1.0 → 1.2.0): New features, backward compatible
- **Patch** (1.1.1 → 1.1.2): Bug fixes only

---

**Related:** [Publishing Workflow](publishing-workflow.md)
