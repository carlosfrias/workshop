# NextCloud rclone External Storage — Refined (Post-Completion)

> **Generated:** 2026-05-20 from NextCloud rclone external storage research + build session
> **Supersedes:** `configure-nextcloud-dropbox.yml` (version-bump approach — archived)
> **Status:** READY FOR REVIEW — sits alongside existing AGENTS-REFINED.md
> **Vault documentation:** `../../personal-vault/01-Projects/nextcloud/`

Deploy rclone on fnet1 to mount Dropbox and Google Drive as local FUSE filesystems, exposed to NextCloud as "Local" external storage. Bypasses NextCloud app version lock-in (NC33) and Google's public-domain OAuth requirement (`nextcloud.home`).

## [S-TIGHT]

Install rclone on fnet1 host → configure OAuth for Dropbox + Google Drive → create systemd FUSE mount services → add Docker bind mounts → configure NextCloud "Local" external storage in admin UI. rclone is the universal bridge — no NextCloud app dependencies, no public domain needed, 70+ backends available.

---

## Conventions (Verified)

- **rclone installed on fnet1 host** — not inside container. systemd mount services need host-level FUSE access.
- **Mount path:** `/mnt/rclone/{dropbox,gdrive}` — clean namespace, easy to extend with new backends
- **OAuth via localhost loopback** — `http://127.0.0.1:53682/auth`. Works because the redirect goes through the user's browser, not a server-side callback. Both Dropbox and Google accept `localhost` as a valid redirect URI.
- **FUSE + Docker requires `:shared` bind propagation** — without it, the mount point is invisible inside containers. — *Standard Docker behavior; would cause silent "directory empty" failures.*
- **systemd mount units use `Type=notify`** — rclone supports systemd notification protocol. `Restart=always` ensures mount persistence across reboots.
- **VFS cache enabled** — `--vfs-cache-mode writes` with `--vfs-cache-max-size 1G`. Essential for directory listing performance in NextCloud.
- **Documentation in vault, code in workshop** — no mixing. Research document at `personal-vault/01-Projects/nextcloud/wiki/nextcloud/research/rclone-external-storage.md`.

## Rules (Battle-Tested)

### Must Always
- Run `rclone config` or `rclone authorize` on a machine with a browser (Mac), NOT on fnet1 directly
- Use SSH tunnel or token paste for headless OAuth setup on fnet1
- Verify mounts are accessible before updating docker-compose (`ls /mnt/rclone/dropbox`)
- Redeploy NextCloud stack after adding bind mounts (`docker compose up -d`)
- Check `systemctl status rclone-mount-*` if mounts are empty or inaccessible
- Use `rclone lsd dropbox:` to verify connectivity before creating systemd services
- Document every backend addition in the vault wiki activity log
- Restart rclone mount services after network changes or token refreshes

### Must Never
- Install rclone inside the NextCloud container — systemd services won't work
- Forget `:shared` on Docker bind mounts — FUSE mounts silently fail without it
- Run `rclone config` in automated mode without pre-generated tokens — it hangs waiting for browser input
- Expose rclone's OAuth port (`53682`) to the network — binds only to `127.0.0.1` by design
- Store rclone tokens in plaintext Ansible vars — use `ansible-vault` for tokens
- Mix manual rclone config with Ansible-managed config — playbook owns all rclone state
- Skip verifying mounts before Docker Compose redeployment — broken mounts cause container startup failures

## Golden Path (Direct Execution)

### Prerequisites
- [ ] rclone installed on Mac (`brew install rclone`) for token generation
- [ ] fnet1 accessible via SSH (`ssh friasc@192.168.0.141 "uptime"`)
- [ ] NextCloud Docker stack running on fnet1 (`docker ps | grep nextcloud-app`)
- [ ] Ansible vault password at `~/.ansible/secure/.vault_pass`
- [ ] Dropbox account (personal or business)
- [ ] Google account with Google Drive enabled

### Execution Sequence

| Step | Action | File/Command | Verification |
|------|--------|--------------|--------------|
| 1 | Generate OAuth tokens on Mac | `rclone authorize "dropbox"` / `rclone authorize "drive"` | Token JSON received |
| 2 | Run rclone playbook with tokens | `configure-nextcloud-rclone.yml -e "rclone_dropbox_token=... rclone_gdrive_token=..."` | rclone installed, services active |
| 3 | Verify mounts | `ls /mnt/rclone/dropbox` / `ls /mnt/rclone/gdrive` | Files visible |
| 4 | Update Docker Compose bind mounts | (done by playbook, step 4) | `docker inspect nextcloud-app` shows /mnt/rclone mounts |
| 5 | Configure NextCloud External Storage | Admin UI → External Storage → Add "Local" storage | Green dot next to each backend |
| 6 | Test file access | Upload file in NextCloud → verify in Dropbox/Google web UI (and vice versa) | Bidirectional sync works |

### Token Generation (Step 1 detail)
```bash
# On Mac (one-time per backend):
brew install rclone
rclone authorize "dropbox"   # Opens browser → login → paste token into playbook
rclone authorize "drive"     # Opens browser → login → paste token into playbook
```

### Run Order Dependencies
```
rclone install → OAuth tokens → systemd services → mounts verified → Docker bind mounts → NextCloud config
                    ↑ tokens MUST be generated before playbook can start services
```

### Post-Execution
- [ ] Write to Activity Log at `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/infrastructure/Activity Log.md`
- [ ] Run quality checklist below
- [ ] If deviations from golden path occur, flag for AGENTS.md update

## Quality Checklist (Verified)

- [ ] `rclone version` returns version info on fnet1
- [ ] `rclone listremotes` shows `dropbox:` and `gdrive:`
- [ ] `rclone lsd dropbox:` lists Dropbox contents (proves API + OAuth work)
- [ ] `rclone lsd gdrive:` lists Google Drive contents
- [ ] `systemctl status rclone-mount-dropbox` shows `active (running)`
- [ ] `systemctl status rclone-mount-gdrive` shows `active (running)`
- [ ] `ls /mnt/rclone/dropbox` shows files (not empty unless genuinely empty Dropbox)
- [ ] `ls /mnt/rclone/gdrive` shows files
- [ ] `docker exec nextcloud-app ls /mnt/rclone/dropbox` shows files (proves `:shared` propagation)
- [ ] NextCloud admin UI External Storage shows green dot for both backends
- [ ] Upload test file in NextCloud Dropbox folder → appears on dropbox.com
- [ ] Upload test file on dropbox.com → appears in NextCloud Dropbox folder
- [ ] Activity log entry created in vault wiki
- [ ] Tokens stored in ansible-vault if provided as extra vars

## Common Mistakes (Discovered)

| Mistake | Symptom | Root Cause | Correct Approach |
|---------|---------|------------|------------------|
| rclone mount empty in container | `docker exec nextcloud-app ls /mnt/rclone/dropbox` is empty | Docker bind mount without `:shared` propagation | Use `:shared` suffix on bind mount in compose file |
| systemd service fails to start | `rclone-mount-dropbox.service: Main process exited, code=exited` | rclone config doesn't have the remote, or OAuth token expired | Run `rclone config` interactively first, verify with `rclone lsd` |
| OAuth hangs during playbook | Playbook pauses waiting for browser input | Running `rclone config` on headless machine without browser or SSH tunnel | Pre-generate tokens on Mac with `rclone authorize`, pass as Ansible vars |
| Mount works but slow directory listing | NextCloud Files page takes 30s+ to show Dropbox folder | VFS cache not configured or too small | Ensure `--vfs-cache-mode writes` and `--dir-cache-time 5m` in systemd unit |
| `fusermount: entry not found` | Service stop fails | Mount already unmounted or never started | Add `ExecStop=/bin/fusermount -uz` to service; ignore errors on stop |
| NextCloud "Local" storage shows red dot | Storage configuration points to wrong path or permissions issue | www-data (uid 33) can't read the mount | Ensure mount has `--allow-other` flag; verify `ls` works as www-data user in container |
| rclone not found after install | `rclone: command not found` | install script failed silently or PATH issue | Check `/usr/bin/rclone` exists; re-run install script |

## Resolved Ambiguities

| Ambiguity | Resolution | Source |
|-----------|-----------|--------|
| rclone on host vs container? | Host — systemd services, FUSE kernel module, and Docker bind propagation all require host-level access | Architectural analysis |
| OAuth: interactive vs pre-generated? | Both supported. Pre-generated tokens for automation, SSH tunnel for ad-hoc. Playbook supports both modes. | Headless machine pattern |
| Mount path convention? | `/mnt/rclone/{backend}` — extensible, avoids collisions with other mount points | Standard Linux FHS |
| VFS cache mode: off vs writes vs full? | `writes` — balances performance and freshness. Directory listings from VFS cache, file writes buffered. | rclone performance docs |
| Google Drive scope: drive vs drive.file? | `drive` — full access needed for bidirectional sync and directory listing | rclone Google Drive backend docs |
| Backend configuration: rclone config vs rclone config create? | `rclone config create` — non-interactive, scriptable, token-injectable | CI/CD automation patterns |
| Token storage: environment vs vault? | Ansible vault — tokens are secrets equivalent to passwords | Security best practices |

## Decision Rationale

| Decision | Alternatives Considered | Why This Choice |
|----------|------------------------|-----------------|
| rclone over NextCloud apps | `files_external_dropbox` (NC30 cap), `files_external_gdrive` (unmaintained) | rclone has no version dependency; works on NC33 today; supports 70+ backends with one tool |
| rclone over NC30 downgrade | Redeploy with `nextcloud:30` image | NC30 would lose features and still couldn't do Google Drive; rclone works on NC33 with both providers |
| Host install over container install | Docker container with FUSE device | systemd services need host PID 1; FUSE kernel module is host-level; Docker `--device /dev/fuse` is fragile |
| systemd over cron for mount persistence | @reboot cron job, autofs | systemd provides health monitoring (`Restart=always`), logging integration (`journalctl`), and proper dependency ordering (`After=network-online`) |
| `vfs-cache-mode writes` over `full` | `full` (caches reads too), `off` (no cache) | `full` risks stale data for cloud storage that changes externally; `off` has terrible directory listing performance; `writes` is the sweet spot |
| Individual service files over template | `rclone-mount@.service` template | Readability — each backend has different flags (scope, cache sizes). Template is better for homogeneous backends. |

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│ fnet1 (192.168.0.141)                                    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ NextCloud Docker (nextcloud-app)                  │   │
│  │  Port 8081 → Nginx → https://nextcloud.home       │   │
│  │                                                    │   │
│  │  Files App                                         │   │
│  │  ├── Documents/      (native NC storage)           │   │
│  │  ├── Dropbox/        → /mnt/rclone/dropbox         │   │
│  │  └── GoogleDrive/    → /mnt/rclone/gdrive          │   │
│  │                                                    │   │
│  │  External Storage (type: Local)                    │   │
│  │  └── Configured in admin UI                        │   │
│  └──────────────┬───────────────────────────────────  │   │
│                 │ Docker bind mounts (:shared)         │   │
│  ┌──────────────┴───────────────────────────────────  │   │
│  │ /mnt/rclone/                                       │   │
│  │  ├── dropbox/   ← FUSE mount (rclone dropbox:)     │   │
│  │  └── gdrive/    ← FUSE mount (rclone gdrive:)      │   │
│  │                                                    │   │
│  │ systemd services:                                  │   │
│  │  rclone-mount-dropbox.service                      │   │
│  │  rclone-mount-gdrive.service                       │   │
│  │                                                    │   │
│  │ ~/.config/rclone/rclone.conf  (OAuth tokens)       │   │
│  └────────────────────────────────────────────────────  │   │
│                          │ HTTPS outbound                │   │
│                     ─────┼────────────────                │   │
│                     api.dropboxapi.com                    │   │
│                     www.googleapis.com                    │   │
└──────────────────────────────────────────────────────────┘
```

## Key Files

| File | Location | Purpose |
|------|----------|---------|
| rclone playbook | `ansible/configure-nextcloud-rclone.yml` | Install + configure rclone, systemd services, Docker bind mounts |
| rclone binary | `/usr/bin/rclone` on fnet1 | Statically compiled Go binary |
| rclone config | `/home/friasc/.config/rclone/rclone.conf` on fnet1 | Remote definitions + OAuth tokens |
| Dropbox mount service | `/etc/systemd/system/rclone-mount-dropbox.service` | systemd unit for FUSE mount |
| GDrive mount service | `/etc/systemd/system/rclone-mount-gdrive.service` | systemd unit for FUSE mount |
| Docker Compose | `/srv/nextcloud/docker-compose.yml` | Bind mount entries for rclone paths |
| Research doc (vault) | `personal-vault/.../wiki/nextcloud/research/rclone-external-storage.md` | Comprehensive rclone reference |
| Research activity log (vault) | `personal-vault/.../wiki/nextcloud/research/Activity Log.md` | Research session log |
| Infrastructure activity log (vault) | `personal-vault/.../wiki/nextcloud/infrastructure/Activity Log.md` | Deployment session log |

## Add a New Backend

The pattern is designed for extensibility. To add e.g. OneDrive:

```bash
# 1. On Mac: generate token
rclone authorize "onedrive"

# 2. Re-run playbook with new backend (adds to rclone_backends list)
ansible-playbook -i inventory.ini configure-nextcloud-rclone.yml \
  -e "rclone_backends=['dropbox','gdrive','onedrive']" \
  -e "rclone_onedrive_token='{...}'"

# 3. Update playbook to add the onedrive service template (or use @ template)

# 4. In NextCloud: Add storage → Local → /mnt/rclone/onedrive
```

## Cross-Domain References

- **Research doc (vault):** `../../personal-vault/01-Projects/nextcloud/wiki/nextcloud/research/rclone-external-storage.md`
- **NextCloud deployment AGENTS (workshop):** `./AGENTS-REFINED.md`
- **NextCloud project AGENTS:** `../AGENTS.md`
- **Lab hardware specs:** `../../03-Resources/Infrastructure/lab-specs/`
- **Playbook executor:** `../../03-Resources/Infrastructure/playbook-executor/`
- **Docker Compose:** `../docker/nextcloud-docker-compose.yml`

---

*Last updated: 2026-05-20*
