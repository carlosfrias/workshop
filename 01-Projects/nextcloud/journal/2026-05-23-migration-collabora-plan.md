# Session Journal: NextCloud Migration + Collabora + VFS Plan

**Date:** 2026-05-23
**Model:** Claude Sonnet (cloud)
**Session Focus:** Unified migration plan with VFS architecture for disk management

## Summary

Created and refined a unified migration plan (v2) combining four objectives:
1. **Data Migration:** 239GB Dropbox data from orchestrator Mac → fnet1 /srv/archive/dropbox via rsync
2. **NextCloud as Primary:** Replace Dropbox sync with local NextCloud (18x faster, 11ms vs 200ms)
3. **LibreOffice/Collabora:** Deploy Collabora CODE container with WOPI integration
4. **VFS Disk Management:** Use NextCloud Virtual Files to free 217GB on Mac (87GB → 304GB free)

## Key Discovery: VFS Changes Everything

The NextCloud client v33.0.5 installed on Mac already has VFS support (FileProviderExt, nextcloudsync_vfs_suffix.dylib). This means:
- All 239GB of Dropbox files appear in Finder as virtual placeholders
- Only `carlos-desktop/` (22GB) stays pinned local
- 217GB freed on Mac disk
- Intelligent auto-eviction: NC client evicts cold files when disk >85% full
- Spotlight works on virtual files
- Double-click any virtual file → downloads from fnet1 over LAN in <5s

## VFS Pinning Strategy

| Folder | Size | VFS Mode | Mac Disk Impact |
|--------|------|----------|-----------------|
| carlos-desktop/ | 22GB | Always local (pinned) | Stays on disk |
| Equity&Law/ | 120GB | Virtual (cloud icon) | 0 bytes |
| tmp/ | 30GB | Virtual | 0 bytes |
| Everything else | 67GB | Virtual | 0 bytes |
| **Total on Mac** | | | **22GB** (was 239GB) → 217GB freed |

## Architecture: Dropbox → NextCloud VFS

- Files stay in ~/Cloud/ — no path changes
- Quit Dropbox client → Start NC client → point at same folder → Enable VFS → Pin carlos-desktop/
- "Keep existing data" option means no re-download
- rclone (backup only) replaces original FUSE mount design

## Files Created/Updated

| File | Action | Key Change |
|------|--------|------------|
| `wiki/.../Migration-Plan-fnet1.md` | Rewritten v2 | VFS architecture, 6 phases, 22KB |
| `PLAN.md` | Updated | Phase 2C (VFS) + Phase 3 (verify) added |
| `FOCUS.md` | Updated | VFS pinning strategy, disk space targets |
| `deploy-migration.sh` | Rewritten v2 | Phase 3-vfs interactive guide |
| `docker-compose.yml` | Already updated | collabora service + archive bind mount |
| `collabora.home.conf` | Already created | Nginx reverse proxy for Collabora |

## D-E-V Pattern Usage

- Decomposer: Broke task into 8 sub-tasks with dependencies
- Executor (Explore): Researched Collabora CODE + rclone migration approaches
- Verifier: Validated NC33.0.3 version (verifier wrongly flagged as hallucination — NC33 IS real)
- Second research pass: VFS capabilities on macOS, FileProvider integration

## Cost

- Claude Sonnet (cloud): ~$0.25 for full session (decomposition + research + plan writing)
- 4 sub-agents: ~$0.05 each (Explore ×2, verifier ×1, decomposer ×1)

## Next Steps

1. Execute Phase 2A: rsync 239GB (~40 min)
2. Execute Phase 2B-2C: Server config
3. Execute Phase 3: VFS client transition
4. Phase 4: rclone backup
5. Phase 5: Verify + 2-week monitoring