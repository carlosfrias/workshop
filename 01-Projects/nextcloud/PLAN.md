# NextCloud — Project Plan

**Last Updated:** 2026-05-24 (nvm migration + fleet update complete)

---

## Active Tasks

| # | Task | Priority | Status | Notes |
|---|------|----------|--------|-------|
| 1 | Monitor NC sync completion on fnet1 | High | ⏳ In Progress | Ongoing monitoring of `/srv/archive/nextcloud-data/data/Carlos/` |
| 2 | Monitor rclone backup cron (5x daily) | High | ⏳ In Progress | Ongoing verification of daily runs |
| 3 | Migrate fnet2, fnet5, fnet6: NodeSource → nvm | High | ✅ Complete | nvm v0.40.x + Node v24.15.0, NodeSource removed, .bashrc clean on all 3 |
| 4 | Update `pi-agent-standalone.sh` & `standup-fleet.yml` | Medium | ✅ Complete | nvm sourcing already in both scripts; no changes needed |
| 5 | Fleet-wide `pi update` | Low | ✅ Complete | All 3 nodes on pi v0.75.5 via nvm, ansible fleet-pi-update.yml verified |

---

## Completed

| # | Task | Completed | Notes |
|---|------|-----------|-------|
| 1 | Audit fleet nodes for `.npmrc` and nvm config | 2026-05-24 | ID'd latent issues on fnet2/6; confirmed NodeSource on fnet2/5/6 |
| 8 | Install pi on fnet6 (was missing) | 2026-05-24 | npm install -g @earendil-works/pi-coding-agent → v0.75.5 |
| 9 | Run fleet-pi-update.yml on fnet2/5/6 | 2026-05-24 | All 3 nodes: pi v0.75.5, already current |
| 2 | Deploy Collabora CODE container | 2026-05-23 | WOPI + richdocuments working |
| 3 | Configure Nginx reverse proxy for collabora.home | 2026-05-23 | SSL cert with SAN |
| 4 | Move NC data to /srv/archive/nextcloud-data | 2026-05-23 | 2.1TB free, bind mount |
| 5 | Configure External Storage (Dropbox-Archive) | 2025-05-23 | Local, 203GB browse-only |
| 6 | Set up rclone backup to Dropbox cloud | 2026-05-23 | 5x daily cron on fnet1 |
| 7 | Clean up orphaned files_external_dropbox | 2026-05-23 | Removed from disk + DB |

---

## Backlog

*No items currently in backlog*

---

## Notes

- All documentation lives in vault: `../../personal-vault/01-Projects/nextcloud/`
- This project contains code and agent configs only
- Target node: **fnet1** (`192.168.0.141`, 3TB primary depot)
