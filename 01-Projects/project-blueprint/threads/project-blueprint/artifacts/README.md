# artifacts/

Post-completion outputs generated from prompt threads. When a thread reaches "complete" status with verified golden-path artifacts, it becomes an executable library entry.

## What Lives Here

| File | Producer | Purpose |
|------|----------|---------|
| `AGENTS-REFINED-scaffold.md` | `auto-documenter` | Initial scaffold — substance indicators, new rules, mistakes, recommended next step |
| `AGENTS-REFINED.md` | `post-completion-architect` | Full optimized AGENTS file — golden path, battle-tested rules, resolved ambiguities, delta report |
| `threshold-metrics.md` | `auto-documenter` | Substance threshold assessment — which criteria were met, confidence scores |

## Artifact Lifecycle

```
Session Complete
     │
     ▼
auto-documenter writes session note
     │
     ├── Threshold NOT met → no artifacts, thread stays active
     │
     └── Threshold MET → writes AGENTS-REFINED-scaffold.md
              │
              ▼
         post-completion-architect generates AGENTS-REFINED.md
              │
              ▼
         Human reviews → approves merge → thread status = complete
              │
              ▼
         Thread becomes LIBRARY ENTRY (executable on repeat prompts)
```

## Navigation

These artifacts are navigable from the thread home:
```
0-THREAD.md → Artifacts section → links to individual files
```

And bidirectionally from each artifact:
```markdown
**Thread:** [0-THREAD.md](../0-THREAD.md)
```
