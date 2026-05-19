# Wiki — Workshop Pointer

**Documentation lives in the vault.** This directory contains only the wiki AGENTS.md router and the VitePress build configuration.

All wiki content (Home, research briefs, evaluation pages, _meta/ reference) lives at:
```
personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research/
```

## Workshop Wiki Contents

| File | Purpose |
|------|---------|
| `AGENTS.md` | Wiki domain router (this file) |
| `workflow-orchestration-research/wiki-build/` | VitePress HTML build config (reads vault markdown) |

## Vault Wiki Contents

| File | Purpose |
|------|---------|
| `wiki/AGENTS.md` | Wiki domain conventions and rules |
| `wiki/workflow-orchestration-research/Home.md` | Domain index + project structure |
| `wiki/workflow-orchestration-research/research/` | Research briefs and activity log |
| `wiki/workflow-orchestration-research/evaluation/` | Evaluation matrices and activity log |
| `wiki/workflow-orchestration-research/_meta/` | Reference docs (Architecture, Agent Definitions, etc.) |

## How It Works

1. **Agents write documentation** → writes to vault wiki paths
2. **VitePress builds HTML** → reads vault markdown (config points `srcDir` to vault)
3. **Workshop keeps only execution infrastructure** → agents, chains, build config