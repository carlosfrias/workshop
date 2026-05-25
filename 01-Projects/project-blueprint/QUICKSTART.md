# Project Blueprint — Quick Start

Get from zero to a working AI-orchestrated project in 5 minutes.

## 1. Install

```bash
pi install git:git@github.com:carlosfrias/project-blueprint.git
```

Verify it's installed:
```bash
pi list | grep project-blueprint
```

## 2. Create Your First Project

```bash
cd ~/my-new-project
pi skill project-blueprint
```

The agent interviews you about:
- Project name and description
- Domains (workflows/areas of responsibility)
- Wiki preferences
- Model choices

It then generates the full project structure — routing, agents, domains, and wiki.

## 3. Manage Domains

```bash
# See what domains exist
/list-domain

# Add a new domain
/add-domain billing "invoice, payment, subscription"

# Rename a domain
/rename-domain auth authentication

# Remove a domain
/remove-domain legacy-module
```

## 4. Distribution Cycle

After making changes to your project:

```bash
git add -A
git commit -m "Describe your changes"
git push origin main
pi update --extensions
```

> ⚠️ **Never leave a session with uncommitted changes.** Workshop edits that aren't committed and pushed are invisible to pi.

## 5. Verify Distribution

Before closing a session, run the Distribution Gate checklist:

- [ ] All changes committed and pushed
- [ ] `pi update --extensions` completed
- [ ] No local paths in `~/.pi/agent/settings.json`
- [ ] No stale symlinks in `~/.pi/agent/extensions/`

## Next Steps

- Read the full [README.md](README.md) for architecture, templates, and troubleshooting
- Read [BUILD.md](BUILD.md) for complete build instructions
- See [checklists.md](skills/project-blueprint/checklists.md) for verification gates
