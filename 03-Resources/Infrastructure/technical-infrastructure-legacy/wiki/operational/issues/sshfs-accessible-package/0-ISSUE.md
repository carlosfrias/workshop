# SSHFS Accessible — Pi Skill Package

**Issue Home:** [0-ISSUE.md](./0-ISSUE.md)
**Status:** ✅ **COMPLETE** — 2026-05-14
**Priority:** 🔴 **HIGH** — Blocks parallel lab node work
**Related:** [TI-033](ti033-lab-sshfs-mount/0-ISSUE.md) (prerequisite — SSHFS mount capability)

---

## Overview

Package the SSHFS workspace-mounting functionality as a standalone pi skill (`sshfs-accessible`), installable via `pi install git:github.com/carlosfrias/sshfs-accessible` and updatable via `pi update`.

The skill exposes node topology in a user-editable `config/nodes.json` file and provides scripts for mounting, unmounting, and verifying SSHFS mounts across the lab node fleet.

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| User-editable `nodes.json` | Topology changes (IPs, new nodes, mount paths) must not require code edits |
| Scripts colocated in package | No pollution outside `technical-infrastructure/packages/sshfs-accessible/` |
| Reverse SSHFS (lab→orch) | Lab nodes initiate mount back to orchestrator; orchestrator remains control point |
| `jq` for JSON parsing | Portable, zero-dependency JSON handling in bash |
| Portable bash | Avoid bash 4+ only features (`mapfile` → `while read` loop) |

## Deliverables

- [x] `package.json` with pi manifest (`pi.skills`)
- [x] `skills/sshfs-accessible/SKILL.md` — Agent Skills standard compliant
- [x] `config/nodes.json` — User-editable topology (orchestrator + 7 lab nodes)
- [x] `scripts/mount-all.sh` — Mount workspace on all/specific nodes
- [x] `scripts/unmount-all.sh` — Unmount workspace from nodes
- [x] `scripts/verify-mounts.sh` — Status check (human + JSON output)
- [x] `scripts/lib/mount-helpers.sh` — Shared library functions
- [x] `README.md` — Package overview
- [x] Full lifecycle test: unmount all → remount all → verify

## Acceptance Criteria

- [x] `pi install git:github.com/carlosfrias/sshfs-accessible` installs the skill
- [x] Skill auto-loads when user mentions SSHFS, mount, lab nodes
- [x] User can edit `config/nodes.json` to change topology
- [x] `mount-all.sh` mounts all configured nodes
- [x] `unmount-all.sh` unmounts all configured nodes
- [x] `verify-mounts.sh --json` returns machine-readable status
- [x] All scripts portable (no bash >=4 features)
- [x] Complete doc-standards documentation in this issue home

## Installation

```bash
# From anywhere in the workspace:
pi install git:github.com/carlosfrias/sshfs-accessible

# Or local path during development:
pi install ./technical-infrastructure/packages/sshfs-accessible
```

## Architecture

```
sshfs-accessible/
├── package.json                          # pi package manifest
├── README.md                             # Quick start
├── config/
│   └── nodes.json                        # ⬅ User-editable topology
├── skills/
│   └── sshfs-accessible/
│       └── SKILL.md                      # Agent skill instructions
└── scripts/
    ├── mount-all.sh                      # Mount orchestrator→lab nodes
    ├── unmount-all.sh                    # Unmount lab nodes
    ├── verify-mounts.sh                  # Health check (human/JSON)
    └── lib/
        └── mount-helpers.sh              # Shared functions
```

## Issue Lifecycle

| Doc | Purpose |
|-----|---------|
| [0-ISSUE.md](./0-ISSUE.md) | This file — canonical definition |
| [sessions/](sessions/) | Session notes |
| [status/](status/) | Point-in-time snapshots |
| [prompts/](prompts/) | User prompts that drove work |
| [tests/](tests/) | Test evidence |
| [artifacts/](artifacts/) | Supporting files |

---

## Navigation

- **Back to backlog:** [../../BACKLOG.md](../../BACKLOG.md)
- **Prerequisite issue:** [../ti033-lab-sshfs-mount/0-ISSUE.md](../ti033-lab-sshfs-mount/0-ISSUE.md)
- **Package:** [../../packages/sshfs-accessible/](../../packages/sshfs-accessible/)
