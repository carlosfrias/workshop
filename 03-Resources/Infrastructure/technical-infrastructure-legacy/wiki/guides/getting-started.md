# Getting Started with technical-infrastructure

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/getting-started.md`

This workspace is the **factory** for extensions, skills, and agents used across trading workspaces.

## Published Packages

| Package | Repository | Install | Status |
|---------|------------|---------|--------|
| **pi-keyword-router** | [github:carlosfrias/pi-keyword-router](https://github.com/carlosfrias/pi-keyword-router) | `pi install github:carlosfrias/pi-keyword-router` | ✅ Published v1.0.0 |
| **project-blueprint** | [github:carlosfrias/project-blueprint](https://github.com/carlosfrias/project-blueprint) | `pi install github:carlosfrias/project-blueprint` | ✅ Published (separate repo) |
| **trading-agents** | [github:carlosfrias/trading-agents](https://github.com/carlosfrias/trading-agents) | `pi install github:carlosfrias/trading-agents` | 📋 Planned |

**Note**: `project-blueprint` is a general-purpose skill and lives as its own repository. A reference copy exists in `technical-infrastructure/skills/` for local development.

## Quick Start: Install pi-keyword-router

```bash
# In any workspace that needs keyword routing
pi install github:carlosfrias/pi-keyword-router
```

This installs the extension that automatically routes prompts to the right model:
- **Reasoning tasks** → `ollama/qwen3.5:cloud` (medium thinking)
- **Structured tasks** → `ollama/gemma4:e4b` (no thinking)
- **Monitoring** → `ollama/qwen3.5:4b` (fast, no thinking)
- **Infrastructure** → `ollama/qwen3:8b` (no thinking)

### Usage Examples

```
<!-- keyword-route: reasoning -->
Analyze this backtest result and recommend position size.

<!-- model: ollama/qwen3.5:cloud thinking: medium -->
Evaluate the risk and decide on entry criteria.

<!-- Just use reasoning keywords -->
Decompose this trading signal into executable steps.
```

### Commands

```
/keyword-route       # Show routing status and history
/keyword-route-off   # Disable automatic routing
/keyword-route-on    # Re-enable routing
```

### Configuration

Project config: `.pi/keyword-router.json`

```json
{
  "default": {
    "provider": "ollama",
    "model": "gemma4:e4b",
    "thinkingLevel": "off"
  },
  "routes": {
    "reasoning": {
      "name": "reasoning",
      "provider": "ollama",
      "model": "qwen3.5:cloud",
      "thinkingLevel": "medium",
      "keywords": ["analyze", "evaluate", "decide", "decompose", ...],
      "domains": ["market-research", "position-management", "decomposer", "verifier"]
    }
  }
}
```

## Development Workflow

### 1. Develop Locally

```bash
cd ~/Dropbox/workshop/technical-infrastructure

# Make changes to packages/pi-keyword-router/

# Test in trading-workspace
cd ../trading-workspace
pi install ../technical-infrastructure/packages/pi-keyword-router
```

### 2. Publish to GitHub

```bash
cd ~/Dropbox/workshop/technical-infrastructure/packages/pi-keyword-router

# Update version in package.json
# Commit changes
git add -A
git commit -m "feat: add new feature"
git tag v1.1.0
git push origin main --tags
```

### 3. Install from GitHub

```bash
# In consumer workspace
pi install github:carlosfrias/pi-keyword-router@v1.1.0
```

### 4. Publish to npm (When Mature)

```bash
cd ~/Dropbox/workshop/technical-infrastructure/packages/pi-keyword-router
npm version minor  # or patch, or major
npm publish
```

## Quality Gates

Before publishing:

- [ ] Works in isolation (no workspace-specific paths)
- [ ] README.md has installation instructions for all 3 stages
- [ ] package.json has correct name, version, repository, license
- [ ] Namespaced keybindings (e.g., `keywordRouter.*`)
- [ ] Namespaced events (e.g., `keyword-router:ready`)
- [ ] Namespaced config (e.g., `.pi/keyword-router.json`)
- [ ] Local test passed in consumer workspace

## Wiki Structure

This wiki contains:

- **[getting-started.md](getting-started.md)** — This page
- **[publishing-workflow.md](publishing-workflow.md)** — Three-stage publishing process
- **[wiki-separation-plan.md](../operational/planning/wiki-separation-plan.md)** — Migration to wiki-per-workspace
- **pi-keyword-router** — Extension documentation (stub)
- **project-blueprint** — Skill documentation (stub)
- **trading-agents** — Agent package documentation (stub)

## Next Steps

1. ✅ **pi-keyword-router** — Published to GitHub
2. ✅ **project-blueprint** — Already published (separate repo, general-purpose skill)
3. 📋 **trading-agents** — Create repo and publish decomposer/verifier agents
4. 📋 **Wiki Separation** — Execute wiki-separation-plan.md

## Support

- **Issues**: GitHub issues on respective repos
- **Discussions**: GitHub discussions on respective repos
- **Trading-workspace usage**: See `trading-workspace/wiki/` for trading-specific guides
