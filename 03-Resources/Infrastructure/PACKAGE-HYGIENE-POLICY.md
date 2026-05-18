# Package Hygiene Policy

**Status:** Active
**Last Updated:** 2026-05-12
**Applies To:** All `technical-infrastructure` packages and dependencies

## Rule: All Packages Belong in `technical-infrastructure/packages/`

Any distributable package, extension, skill, or agent module that is developed as part of the Trading Desk Orchestration Framework **must** reside in:

```
technical-infrastructure/packages/<package-name>/
```

### Prohibited Locations

Do **not** place packages in these locations:

- `technical-infrastructure/agents/` — Use `packages/<pkg>/agents/`
- `technical-infrastructure/extensions/` — Use `packages/<pkg>/`
- `technical-infrastructure/scripts/` — Use `packages/<pkg>/scripts/`
- Root workspace directories (`./scripts`, `./demos`, etc.)

### Exception: General Infrastructure Scripts

Scripts that are part of the core TI-011 orchestration framework (e.g., `classify_prompt.py`, `decompose_task.py`, `orchestrator_health.py`) may remain in `technical-infrastructure/scripts/` as they are not distributable packages.

## DRY Enforcement

1. **No duplicate agent definitions** — `decomposer.md` and `verifier.md` exist only in `packages/decompose-execute-verify/agents/`
2. **No cross-package contamination** — Each package owns its own `agents/`, `scripts/`, and `prompts/`
3. **Canonical source of truth** — The `packages/` directory is the single source of truth for all distributable artifacts

## Verification

Run the hygiene test suite to verify compliance:

```bash
cd technical-infrastructure/packages/e2e-test-suite
./scripts/run-e2e-tests.sh --scenario 11,12
```

## New Package Onboarding Checklist

When creating a new package:

- [ ] Directory created at `technical-infrastructure/packages/<package-name>/`
- [ ] `package.json` present with correct metadata
- [ ] `README.md` describes purpose and install command
- [ ] No duplicate files exist in other package directories
- [ ] All internal references use `packages/<package-name>/` path
- [ ] Added to `e2e-test-suite` Scenario 11 coverage (if applicable)
