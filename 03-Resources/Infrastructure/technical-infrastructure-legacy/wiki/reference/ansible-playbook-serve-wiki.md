# Ansible Playbook: `serve-wiki.yml`

**Purpose:** Controls the local VitePress dev server for the Trading Desk Wiki. Can start, stop, restart, or toggle the server. Automatically opens the default browser on macOS when the server starts.

---

## Quick Start

```bash
cd technical-infrastructure/ansible

# Toggle (default): start if stopped, stop if running
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml

# Force start (opens browser on macOS)
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml -e "wiki_state=start"

# Start without opening browser
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml -e "wiki_state=start open_browser=false"

# Force stop
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml -e "wiki_state=stop"

# Check status
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml -e "wiki_state=status"

# Restart (stop + start)
ansible-playbook -i localhost, -c local playbooks/serve-wiki.yml -e "wiki_state=restart"
```

---

## Architecture

The wiki is served by VitePress from the **project root**, not a subdirectory:

```
Project Root (/Users/friasc/Cloud/workshop/)
├── .vitepress/config.js          # VitePress configuration
├── wiki/                         # Content directory
│   ├── index.md                  # Home page
│   ├── operations/
│   ├── technical-infrastructure/
│   └── trading-desk/
├── node_modules/                 # Symlinked from wiki-build/
└── technical-infrastructure/
    └── ansible/
        └── playbooks/
            └── serve-wiki.yml    # This playbook
```

- **Server:** VitePress dev server
- **URL:** `http://localhost:5173/`
- **Log:** `/tmp/vitepress-wiki.log`
- **Content hot-reload:** Yes — edit any `.md` file and refresh

---

## Browser Auto-Open

### macOS

When `open_browser` is `true` (default) and the server starts, the playbook runs:

```bash
open http://localhost:5173/
```

This opens the URL in your **default browser** (Safari, Chrome, Firefox, etc.).

### Linux / Other

Browser auto-open is currently **macOS only** (`ansible_os_family == 'Darwin'`). For Linux, add a similar task with `xdg-open` or `google-chrome`.

### Disabling Auto-Open

**One-time:**
```bash
ansible-playbook ... -e "open_browser=false"
```

**Permanent:** Edit `vars/main.yml`:
```yaml
open_browser: false
```

---

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `wiki_state` | `toggle` | `start`, `stop`, `restart`, `status`, or `toggle` |
| `open_browser` | `true` | Whether to open the default browser (macOS only) |
| `vitepress_port` | `5173` | Port VitePress listens on |
| `wiki_log_file` | `/tmp/vitepress-wiki.log` | Server output log |
| `wiki_root` | Project root | Directory containing `.vitepress/config.js` |
| `wiki_content_dir` | `{{ wiki_root }}/wiki` | Content source directory |

---

## State Machine

```
wiki_state=toggle
    ├── Server running? ──yes──→ Stop it
    └── Server stopped? ─yes──→ Start it

wiki_state=start
    ├── Server running? ──yes──→ Already running (skip)
    └── Server stopped? ─yes──→ Start it + open browser

wiki_state=stop
    └── Stop unconditionally

wiki_state=restart
    ├── Stop unconditionally
    └── Start + open browser

wiki_state=status
    └── Report current state only
```

---

## Tasks Breakdown

### Pre-Start
1. Verify Node.js is installed
2. Verify npm is installed
3. Ensure `wiki/index.md` exists
4. Create symlink `index.md` → `README.md` in subdirectories
5. Clear stale VitePress cache

### Start
6. Start VitePress dev server in background (`nohup`)
7. Poll `http://localhost:5173/` until it returns 200
8. **Open default browser** (macOS, conditional)

### Stop
1. Send SIGTERM to the Node.js process
2. Wait up to 5 seconds for graceful shutdown
3. Fallback to SIGKILL if still alive
4. Confirm port 5173 is free

---

## Troubleshooting

### Server won't start

```bash
# Check the log
cat /tmp/vitepress-wiki.log

# Verify port not in use
lsof -i :5173

# Manual start for debugging
cd /Users/friasc/Cloud/workshop
npx vitepress dev --port 5173
```

### Browser doesn't open

- Only works on macOS (`Darwin`). Check `ansible_os_family`.
- Verify `open_browser` is not set to `false`.
- Check browser console for errors.

### Stale cache issues

The playbook automatically clears `.vitepress/cache/` before starting. If you see old content:

```bash
ansible-playbook ... -e "wiki_state=restart"
```

### Permission denied on symlinks

The playbook creates symlinks for subdirectories. If this fails:

```bash
ls -la wiki/operations/index.md
# Should point to: wiki/operations/README.md
```

---

## Files

| File | Purpose |
|------|---------|
| `playbooks/serve-wiki.yml` | Main playbook |
| `roles/wiki-local/tasks/main.yml` | State machine logic |
| `roles/wiki-local/tasks/start.yml` | Start server + open browser |
| `roles/wiki-local/tasks/stop.yml` | Stop server |
| `roles/wiki-local/tasks/check.yml` | Detect running server |
| `roles/wiki-local/vars/main.yml` | Configuration variables |

---

## Related

- [VitePress Documentation](https://vitepress.dev/)
- [Wiki Home](/) — Locally served at `http://localhost:5173/`
- [Ansible Playbook Index](ansible-playbook-index.md) — All available playbooks
