# AGENTS-REFINED: NextCloud Migration v2

**Created:** 2026-05-23
**Session:** 2026-05-23-migration-execution-full
**Unified Prompt:** N/A (battle-tested rules from execution)

## Battle-Tested Rules

### 1. rclone OAuth tokens can't be shared cross-machine
**Context:** Generating `rclone authorize dropbox` on Mac and copying the token JSON to fnet1 failed — rclone stripped the refresh_token.
**Rule:** Run `rclone authorize` on the machine that will USE the token. For headless servers, use `rclone authorize` on a machine with a browser, then write the config via Python (not heredoc/SSH which truncates long tokens). Base64 encoding the entire config and piping through `base64 -d` on the remote is reliable.

### 2. NC33 files_external app:remove fails for disabled apps
**Context:** `files_external_dropbox` was disabled but listed in `occ app:list`. `occ app:remove` said "not enabled". Manual DB cleanup was required.
**Rule:** For orphaned NC apps that can't be removed via `occ app:remove`, delete from `/var/www/html/custom_apps/` on disk, then clean up `oc_appconfig` table via MySQL. The `oc_apps` table doesn't exist in NC33 — app registry is in `oc_appconfig` only.

### 3. NC33 External Storage admin URL has an 's'
**Context:** The correct URL is `/settings/admin/externalstorages` (plural), NOT `/settings/admin/externalstorage`.
**Rule:** When configuring NC External Storage via URL, use `https://nextcloud.home/settings/admin/externalstorages` with the trailing 's'.

### 4. Self-signed SSL certs need SAN regeneration for new subdomains
**Context:** Adding `collabora.home` to the Nginx config broke HTTPS because the existing cert only covered `nextcloud.home`.
**Rule:** When adding a new subdomain to an Nginx reverse proxy, regenerate the self-signed cert with ALL SANs: `sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout key.crt -out cert.crt -subj '/CN=nextcloud.home' -addext 'subjectAltName=DNS:nextcloud.home,DNS:collabora.home,DNS:nextcloud,IP:192.168.0.141'`. Then update the macOS System Keychain: `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cert.crt`.

### 5. NC Docker volumes must be migrated to bind mounts for large data
**Context:** Docker named volume `nextcloud_data` was only on /srv (164GB free). Moving to `/srv/archive` (2.1TB free) required converting to a bind mount in docker-compose.yml.
**Rule:** For NC deployments with >100GB data, always use bind mounts (`/srv/archive/nextcloud-data:/var/www/html`) instead of named volumes. Named volumes couple data to Docker's internal storage on the root partition. Bind mounts let you use any partition.

### 6. The NC client External Storage shows red with "not synced" — by design
**Context:** External Storage mounts (like Dropbox-Archive) show as red/not synced in the NC desktop client. This is expected — desktop clients don't sync external storage.
**Rule:** External Storage is browse-only in the desktop client. It's accessible via the NC web UI for searching and downloading individual files. If users need desktop sync of specific archived files, they should download via web UI or use the NC web UI directly.

### 7. Chown on rsync'd data must include chmod for directories
**Context:** `chown -R 33:33` made files owned by www-data but some directories had 700 permissions from the source, causing rsync pass 2 to fail with "Permission denied".
**Rule:** After rsync to NC storage, run both: `chown -R 33:33` AND `find -type d -exec chmod 755` + `find -type f -exec chmod 644`. This ensures the data is readable by the NC container for both access and future rsync delta checks.

### 8. NC maintenance:mode must be disabled before redeploying containers
**Context:** Enabling `maintenance:mode --on` before a container restart works, but you must also disable it in `config.php` directly if the containers were recreated, since `occ` may not be available during the window.
**Rule:** After container recreation, verify maintenance mode is off: `grep maintenance config/config.php` and set to `false` if needed. Or use `docker exec nextcloud-app php occ maintenance:mode --off` after containers are up.

---

*These rules were extracted from the 2026-05-23 migration execution session. Each was discovered through live debugging on production infrastructure.*