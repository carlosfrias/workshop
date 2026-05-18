# Publishing Workflow

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/publishing-workflow.md`

This workspace is the **factory** for extensions, skills, and agents that other workspaces consume via `pi install`.

## What Lives Here

| Directory | Contents | Published As |
|-----------|----------|--------------|
| `extensions/` | pi extensions (e.g., `pi-keyword-router`) | `pi install github:carlosfrias/pi-keyword-router` |
| `skills/` | Agent skills (e.g., `project-blueprint`) | `pi install github:carlosfrias/project-blueprint` |
| `agents/` | Reusable agent definitions (e.g., `decomposer`, `verifier`) | `pi install github:carlosfrias/trading-agents` |
| `wiki/` | Documentation for consumers | GitHub wiki, npm README |

## Publishing Stages

1. **Development** → Work in `technical-infrastructure/packages`
2. **Local Test** → `pi install ../technical-infrastructure/extensions/<name>`
3. **GitHub** → Push to `carlosfrias/<repo>`, users install via `pi install github:carlosfrias/<repo>`
4. **npm (Mature)** → `npm publish`, users install via `pi install <package-name>`

## Quality Gates Before Publishing

- [ ] Extension/skill works in isolation (no workspace-specific dependencies)
- [ ] README.md includes installation instructions for all three stages
- [ ] package.json has correct name, version, repository, and license
- [ ] Config files use namespaced paths (e.g., `.pi/keyword-router.json` not `.pi/model-router.json`)
- [ ] Keybinding namespaces are unique (e.g., `keywordRouter.*` not `modelRouter.*`)
- [ ] Event names are namespaced (e.g., `keyword-router:ready` not `model-router:ready`)

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Hardcoding API keys in scripts | Use environment variables or a secrets manager |
| Deploying without testing staging | Always validate in staging before production |
| Ignoring latency spikes | Investigate immediately — latency degrades fill quality |
| Assuming a broker API is always up | Health-check before any order submission |
| Changing config without logging | Always log before/after state with timestamp |
| **Publishing without local test** | Install locally first, verify in real session |
| **Using generic keybinding namespaces** | Use unique namespace (e.g., `keywordRouter.*`) |

---

**Related:** [Published Packages](published-packages.md)
