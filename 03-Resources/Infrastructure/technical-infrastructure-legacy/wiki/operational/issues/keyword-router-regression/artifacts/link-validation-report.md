# Link Validation Report

**Directory scanned:** `technical-infrastructure/wiki/operational/issues/keyword-router-regression/`
**Date:** 2026-05-14
**Files scanned:** 15 markdown files
**Strategy:** Grep for `[text](path)` pattern, resolve relative path from each file's directory, test file/directory existence via shell.

---

## Summary

| Category | Count |
|----------|-------|
| Total links checked | ~55 |
| Valid links | ~45 |
| **Broken links** | **8** |
| In-page anchors (ignored) | 12 |

---

## Broken Links (8)

### 1. `../../reference/node-capacity-map.md` — Target path is wrong by one level

All three instances resolve `../../` to `operational/`, but `reference/` actually lives at `wiki/reference/` (three levels up from `keyword-router-regression/`).

| File | Line | Link text | Actual target exists? |
|------|------|-----------|----------------------|
| `AGENTS.md` | 103 | `node-capacity-map.md` | `../../../reference/node-capacity-map.md` exists |
| `1-PLAN.md` | 357 | `node-capacity-map.md` | same as above |
| `BACKLOG-keyword-router.md` | 116 | `node-capacity-map.md` | same as above |

**Suggested fix:** Change `../../../reference/` to `../../../../reference/` in all three files.

---

### 2. `./1-PLAN.md` — File does not exist

The actual plan file is named `1-PLAN.md`.

| File | Line | Link text |
|------|------|-----------|
| `AGENTS.md` | 442 | `1-PLAN.md` |
| `BACKLOG-keyword-router.md` | 49 | `1-PLAN.md` |
| `BACKLOG-keyword-router.md` | 113 | `1-PLAN.md` |

**Suggested fix:** Rename target or change links to `./1-PLAN.md`.

---

### 3. `../sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md` — File not in sibling `sessions/` dir

From `keyword-router-regression/`, `../sessions/` resolves to `issues/sessions/` which does **not** exist. The file lives in `operational/sessions/` (two levels up).

| File | Line | Link text | Correct relative path |
|------|------|-----------|---------------------|
| `BACKLOG-keyword-router.md` | 117 | `ROOT-CAUSE-B-KR-002-2026-05-14.md` | `../../sessions/ROOT-CAUSE-B-KR-002-2026-05-14.md` |

---

### 4. `../sessions/B-KR-003-COMPLETION-2026-05-14.md` — Same mis-directory issue

| File | Line | Link text | Correct relative path |
|------|------|-----------|---------------------|
| `BACKLOG-keyword-router.md` | 118 | `B-KR-003-COMPLETION-2026-05-14.md` | `../../sessions/B-KR-003-COMPLETION-2026-05-14.md` |

---

### 5. `../prompts/2026-05-13-1926-kickoff.md` — Prompts directory is empty

| File | Line | Link text | Reason |
|------|------|-----------|--------|
| `sessions/2026-05-13-1926.md` | 67 | `2026-05-13-1926-kickoff.md` | `prompts/` exists but contains 0 files |

---

### 6. `../prompts/2026-05-14-0800-bisection-refinement.md` — Prompts directory is empty

| File | Line | Link text | Reason |
|------|------|-----------|--------|
| `sessions/2026-05-13-1926.md` | 68 | `2026-05-14-0800-bisection-refinement.md` | `prompts/` exists but contains 0 files |

---

### 7. `./BACKLOG-MASTER.md` — File does not exist

No markdown links point to this file, but as requested it was checked. The actual backlog file is `BACKLOG-keyword-router.md`. If any external reference expects `BACKLOG-MASTER.md`, it should be renamed or a symlink created.

---

### 8. `../../wiki/` paths — None found

No `../../wiki/` relative links were discovered in the scanned files.

---

## Validated Link Samples (Passing)

- `./AGENTS.md` — exists in all referencing files' directories
- `./1-PLAN.md` — exists
- `./BACKLOG-keyword-router.md` — exists
- `./INVOCATION-GUIDE-2026-05-13.md` — exists
- `./DECOMP-B-KR-001-2026-05-13.md` — exists (decompositions/)
- `./B-KR-002-REFINED-DISPATCH-2026-05-13.md` — exists
- `./decompositions/` — directory exists
- `./troubleshooting/` — directory exists
- `./artifacts/` — directory exists
- `0-PLAN.md` / `1-analysis.md` / `2-resolution.md` — exist within `troubleshooting/`
- `../BACKLOG-keyword-router.md` — resolves correctly from `troubleshooting/`
- `../decompositions/DECOMP-B-KR-002-2026-05-13.md` — resolves correctly from `troubleshooting/`

---

## Empty Target Directories (Note — Not Broken, But Worth Highlighting)

| Directory | Status |
|-----------|--------|
| `prompts/` | Empty (0 files) |
| `tests/` | Empty (0 files) |

Links to these directories as folders (e.g., `./prompts/` in `0-ISSUE.md`) resolve successfully because the directory itself exists, but there is no content inside.

---

*End of report.*
