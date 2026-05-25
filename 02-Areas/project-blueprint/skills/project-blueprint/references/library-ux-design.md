# Library UX Design — TUI Overlay for Completed Threads

**Decision:** TUI overlay with hide/show toggle
**Date:** 2026-05-25
**Phase:** 5.3

## Overview

The Library surfaces completed session threads proactively through a TUI overlay in pi. When a session is documented by the auto-documenter, it registers in the Library. On next pi session start (or on command), the overlay shows recently completed threads that may be relevant to the current task.

## UX Flow

```
Session completes → auto-documenter runs → writes library.jsonl entry
                                                    ↓
Next pi session starts → TUI overlay checks library → shows recent threads
                                                    ↓
User can: /library hide (dismiss) | /library show (re-display) | click to load thread
```

## Data Store

**`threads/project-blueprint/library.jsonl`** — append-only JSON lines:

```jsonl
{"id":"session-2026-05-25-1300","date":"2026-05-25","title":"Distribution Discipline","warranted":true,"domain":"project-blueprint","summary":"All 10 pi packages git-distributed; workflow encoded"}
```

## TUI Overlay

### Display
- Appears at session start (after "pi ready" message)
- Shows last 5 threads (or fewer if less exist)
- Format: compact, one line per thread with date + title + domain
- Threads flagged `warranted: true` get a ⚡ marker

### Controls
| Command | Action |
|---------|--------|
| `/library` | Show overlay (manually) |
| `/library hide` | Dismiss overlay for this session |
| `/library show` | Re-display if hidden |
| `/library list` | List all threads (paginated) |
| `/library load {id}` | Load thread context into current session |

### Auto-hide
- Overlay auto-hides after 30 seconds if not interacted with
- Overlay does NOT appear if library.jsonl has no entries since last session

## Implementation

The TUI overlay is implemented in the `pi-intercom` extension as a UI component. The auto-documenter writes the library.jsonl. The post-completion-architect may append additional entries for refined AGENTS files.

### Components
1. **auto-documenter** — writes library.jsonl entry per session
2. **pi-intercom TUI** — reads library.jsonl on startup, renders overlay
3. **Library commands** — `/library` slash commands for control

## States

| State | Overlay visible? | How to show |
|-------|-----------------|-------------|
| Normal | Yes (on startup) | Automatic |
| Hidden | No | `/library show` |
| Dismissed | No (this session) | `/library show` (re-displays) |
| Empty library | No | `/library list` (shows "no threads") |
