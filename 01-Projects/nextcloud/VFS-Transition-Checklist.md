# VFS Transition Checklist — Execute After rsync Completes

**Prerequisites:** rsync of 239GB to fnet1 complete, ownership fixed, NC External Storage configured

---

## Pre-Flight Checks

- [ ] rsync complete: `ps aux | grep rsync` — should show NO rsync process
- [ ] fnet1 data size matches: `ssh friasc@192.168.0.141 "du -sh /srv/archive/dropbox/"` ≈ 239GB
- [ ] Ownership correct: `ssh friasc@192.168.0.141 "ls -la /srv/archive/dropbox/"` — shows uid 33

## Step 1: Fix Ownership + Add Bind Mount

```bash
# Fix ownership for NextCloud (www-data = uid 33)
ssh friasc@192.168.0.141 "sudo chown -R 33:33 /srv/archive/dropbox"

# Add bind mount to docker-compose on fnet1
ssh friasc@192.168.0.141 "sed -i 's|/srv/nextcloud/data:/srv/nextcloud/data|/srv/nextcloud/data:/srv/nextcloud/data\n      - /srv/archive/dropbox:/srv/archive/dropbox:shared|' /srv/nextcloud/docker-compose.yml"

# Redeploy NextCloud
ssh friasc@192.168.0.141 "cd /srv/nextcloud && docker compose up -d"

# Verify bind mount
ssh friasc@192.168.0.141 "docker exec nextcloud-app ls /srv/archive/dropbox/ | head -5"
```

- [ ] Ownership fixed
- [ ] Bind mount in docker-compose
- [ ] NextCloud redeployed
- [ ] Files visible inside container

## Step 2: Configure NC External Storage

1. Open https://nextcloud.home → Settings → Administration → External Storage
2. Click "Add storage" → Type: **Local**
3. Folder name: `Dropbox-Archive`
4. Location: `/srv/archive/dropbox`
5. Available for: Carlos
6. Click ✓ to save
7. Verify: **Green dot** next to the storage entry

```bash
# Scan files after configuration
ssh friasc@192.168.0.141 "docker exec -u www-data nextcloud-app php occ files:scan --all"
```

- [ ] External Storage configured in admin UI
- [ ] Green dot visible
- [ ] Files scanned

## Step 3: Quit Dropbox

1. Menu bar → click Dropbox icon → gear → **Quit Dropbox**
2. System Settings → General → Login Items → **disable Dropbox**
3. Verify: `ps aux | grep -i dropbox | grep -v grep` — empty

- [ ] Dropbox client quit
- [ ] Dropbox auto-start disabled

## Step 4: Launch NextCloud Client + VFS

1. Open `/Applications/Nextcloud.app`
2. Add Account → Server: `https://nextcloud.home`
3. Login with Carlos credentials
4. **Choose local folder: `/Users/friasc/Cloud/`**
5. **Choose: "Keep existing data"** ← IMPORTANT
6. Settings → Enable **Virtual Files** for this account

- [ ] NC client launched
- [ ] Account connected
- [ ] Sync folder = ~/Cloud/ with "Keep existing data"
- [ ] VFS enabled

## Step 5: Pin carlos-desktop/ Local

1. In Finder: navigate to `~/Cloud/carlos-desktop/`
2. Right-click `carlos-desktop` folder → **"Keep locally" / "Make available offline"**
3. Wait for green checkmarks to appear

- [ ] carlos-desktop/ has green checkmarks (pinned local, 22GB)

## Step 6: Verify VFS State

1. In Finder, check other folders:
   - `Equity&Law/` → cloud icons ☁️ (virtual, 0 bytes)
   - `tmp/` → cloud icons ☁️ (virtual, 0 bytes)
   - Other folders → cloud icons ☁️ (virtual)
2. Check disk: `df -h /` → should show ~304GB free (was 87GB)
3. Test: double-click a virtual file → downloads and opens

- [ ] Non-carlos-desktop folders show cloud icons
- [ ] Mac free space ≈ 304GB
- [ ] Virtual file download works

## Step 7: Test Collabora Editing

1. Open https://nextcloud.home in browser
2. Navigate to any .docx file in Dropbox-Archive
3. Click to open → should open in Collabora editor
4. Make a small edit → verify it saves

- [ ] .docx opens in Collabora in browser
- [ ] Edit and save works

## Step 8: Verify NC ↔ Mac Sync

1. Create a test file in `~/Cloud/carlos-desktop/` on Mac
2. Wait 30 seconds
3. Check NextCloud web UI → file appears
4. Upload a file via NextCloud web UI (to NC native storage)
5. Wait 30 seconds
6. Check Mac → file appears in Finder

- [ ] Mac → NC sync works
- [ ] NC → Mac sync works

## rclone Token (Do When Convenient)

After the above is verified stable:

```bash
# In a separate Mac terminal:
rclone authorize "dropbox"
# Opens browser → login → token appears in terminal
# Save token for Phase 2D (rclone backup cron)
```

- [ ] rclone Dropbox token generated

---

*Created: 2026-05-23*