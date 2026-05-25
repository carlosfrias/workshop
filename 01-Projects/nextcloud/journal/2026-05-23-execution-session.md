# Session Journal: NextCloud Migration Execution

**Date:** 2026-05-23
**Model:** Claude Sonnet (cloud)
**Session Focus:** Executing migration Phases 2A–2B + 2C (server side) in parallel

## What Was Done This Session

### Phase 2A: Data Migration — IN PROGRESS
- `rsync -avz` launched at ~9:41 AM ET, transferring 239GB from Mac to fnet1:/srv/archive/dropbox/
- Running via `nohup` — survives session disconnect
- Log: `/tmp/nextcloud-migration-rsync.log`
- Status marker: `cat /tmp/nextcloud-rsync-status.txt` (empty = still running, "COMPLETE" = done)
- ~16GB of 239GB transferred when user stepped away (~1.5 hours remaining at 29MB/s)

### Phase 2B: Collabora CODE Deployment — ✅ COMPLETE
- Collabora container running (127.0.0.1:9980)
- Nginx config `collabora.home.conf` deployed + symlinked
- DNS: `collabora.home` → 192.168.0.141 (hosts + dnsmasq)
- SSL cert regenerated with `collabora.home` in SANs
- richdocuments v10.1.3 installed + enabled
- WOPI URL configured: `https://collabora.home`
- WOPI discovery returns valid XML ✅
- notify_push v1.3.3 installed + enabled

### Phase 2C: Server Configuration — PARTIAL
- files_external app enabled ✅
- files_external_dropbox (orphaned) removed ✅
- External Storage (Local) NOT yet configured — needs rsync to finish first
- Bind mount for /srv/archive/dropbox NOT yet in docker-compose — waiting for rsync
- notify_push installed ✅

### VFS Transition Checklist — WRITTEN (not yet executed)
- File: `workshop/01-Projects/nextcloud/VFS-Transition-Checklist.md`
- Covers: ownership fix, bind mount, NC External Storage config, Dropbox quit, NC client VFS setup, pin carlos-desktop/, verification

### Path Rename Plan — WRITTEN (future, after VFS stable)
- File: `personal-vault/.../wiki/nextcloud/infrastructure/Path-Rename-Plan.md`
- Includes IntelliJ global configs (6 files in ~/Library/Application Support/JetBrains/)
- Includes fleet node server-side rename (optional)

## Files Created/Modified This Session
| File | Action |
|------|--------|
| `workshop/.../docker/nextcloud-docker-compose.yml` | Added collabora service (bind mount NOT added yet) |
| `workshop/.../nginx/collabora.home.conf` | Created |
| `workshop/.../ansible/deploy-migration.sh` | Created (v2 with VFS) |
| `workshop/.../VFS-Transition-Checklist.md` | Created |
| `personal-vault/.../Migration-Plan-fnet1.md` | Rewritten v2 (VFS architecture) |
| `personal-vault/.../Path-Rename-Plan.md` | Created (~/Cloud → ~/Cloud) |
| `personal-vault/.../PLAN.md` | Updated (Phase 2C, Phase 4) |
| `personal-vault/.../FOCUS.md` | Updated (VFS architecture, pinning strategy) |

## Current fnet1 State
- All 5 NC containers + Collabora running and healthy
- SSL cert covers: nextcloud.home, collabora.home, nextcloud, 192.168.0.141
- /srv/archive/dropbox/ has ~16GB (rsync still writing, target ~239GB)
- /srv/archive has 2.3TB free (plenty of room)

## Next Session Handoff
1. Check rsync status: `cat /tmp/nextcloud-rsync-status.txt`
2. If COMPLETE: follow `VFS-Transition-Checklist.md`
3. If still running: wait (check `du -sh /srv/archive/dropbox/` on fnet1)
4. After VFS: optionally generate rclone token (`rclone authorize "dropbox"`)
5. After 1+ week stable: follow `Path-Rename-Plan.md` for ~/Cloud → ~/Cloud

## Cost
- Claude Sonnet: ~$0.35 (main session, decomposition, planning, execution)
- 1 background agent (Collabora deploy): ~$0.10
- 1 decomposer agent: ~$0.02
- 4 failed delegate agents ($0 — no API key for haiku)
- Total: ~$0.47