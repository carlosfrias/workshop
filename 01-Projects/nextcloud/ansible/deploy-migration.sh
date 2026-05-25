#!/bin/bash
# =============================================================================
# NextCloud Migration + Collabora + VFS Deployment Script
# Target: fnet1 (192.168.0.141)
# Created: 2026-05-23
# Updated: 2026-05-23 (v2 — VFS architecture)
#
# Usage:
#   ./deploy-migration.sh [phase]
#   phase: all | 2a-data | 2b-collabora | 2c-server | 3-vfs | 4-rclone | 5-verify
#
# Phases:
#   2a-data      - Migrate Dropbox data to /srv/archive/dropbox
#   2b-collabora - Deploy Collabora CODE container + Nginx config
#   2c-server    - Configure NC External Storage + notify_push
#   3-vfs        - Mac client transition: Dropbox → NextCloud VFS
#   4-rclone     - Install rclone for backup + cleanup
#   5-verify     - Verify full stack
#   all          - Run phases 2a through 4 (5-verify separate)
# =============================================================================

set -euo pipefail

FNET1="friasc@192.168.0.141"
DROPBOX_SRC="/Users/friasc/Cloud/"
ARCHIVE_DST="/srv/archive/dropbox"
COMPOSE_DIR="/srv/nextcloud"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
step()  { echo -e "${BLUE}[STEP]${NC} $*"; }

check_ssh() {
    info "Checking SSH connectivity to fnet1..."
    ssh -o ConnectTimeout=5 "$FNET1" "echo 'SSH OK'" 2>/dev/null || error "Cannot SSH to $FNET1"
}

check_docker() {
    info "Checking Docker stack on fnet1..."
    ssh "$FNET1" "docker ps --format '{{.Names}}' | grep -q nextcloud-app" || error "NextCloud not running on fnet1"
    info "NextCloud stack is running."
}

# =============================================================================
# Phase 2A: Data Migration
# =============================================================================
phase_2a_data() {
    info "========================================="
    info "Phase 2A: Data Migration (Mac → fnet1)"
    info "  Source: $DROPBOX_SRC (239GB)"
    info "  Target: $FNET1:$ARCHIVE_DST"
    info "  Est. time: ~40 min at Gigabit LAN"
    info "========================================="

    # Step 1: Create target directory
    step "Creating target directory on fnet1..."
    ssh "$FNET1" "sudo mkdir -p $ARCHIVE_DST && sudo chown friasc:friasc $ARCHIVE_DST"
    info "Target directory ready: $ARCHIVE_DST"

    # Step 2: Dry run
    step "Running rsync dry run..."
    rsync -avzn --progress \
        --exclude='.dropbox' \
        --exclude='.dropbox.cache' \
        --exclude='.DS_Store' \
        "$DROPBOX_SRC" \
        "$FNET1:$ARCHIVE_DST/" || warn "Dry run had warnings (check output above)"

    echo ""
    warn "Review the dry run output above."
    read -p "Proceed with actual copy? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Aborting. Re-run with '2a-data' to continue."
        exit 0
    fi

    # Step 3: Actual copy
    step "Starting rsync (this will take ~40 minutes for 239GB over Gigabit LAN)..."
    info "  This is resumable — if interrupted, just re-run this phase."
    rsync -avz --progress \
        --exclude='.dropbox' \
        --exclude='.dropbox.cache' \
        --exclude='.DS_Store' \
        "$DROPBOX_SRC" \
        "$FNET1:$ARCHIVE_DST/"

    # Step 4: Fix ownership for NextCloud (www-data = uid 33)
    step "Fixing ownership for NextCloud (www-data = uid 33)..."
    ssh "$FNET1" "sudo chown -R 33:33 $ARCHIVE_DST"

    # Step 5: Verify sizes
    step "Verifying data transfer..."
    SRC_SIZE=$(du -sh "$DROPBOX_SRC" 2>/dev/null | cut -f1)
    DST_SIZE=$(ssh "$FNET1" "du -sh $ARCHIVE_DST" 2>/dev/null | cut -f1)
    info "Source: $SRC_SIZE | Destination: $DST_SIZE"

    info "Phase 2A complete. ✅ Data migrated to fnet1."
}

# =============================================================================
# Phase 2B: Collabora CODE Deployment
# =============================================================================
phase_2b_collabora() {
    info "========================================="
    info "Phase 2B: Collabora CODE Deployment"
    info "========================================="

    # Step 1: Copy updated docker-compose.yml to fnet1
    step "Copying updated docker-compose.yml to fnet1..."
    scp "$SCRIPT_DIR/../infrastructure/docker/nextcloud-docker-compose.yml" \
        "$FNET1:$COMPOSE_DIR/docker-compose.yml"

    # Step 2: Copy Collabora Nginx config
    step "Copying Collabora Nginx config..."
    scp "$SCRIPT_DIR/../infrastructure/nginx/collabora.home.conf" \
        "$FNET1:/tmp/collabora.home.conf"
    ssh "$FNET1" "sudo cp /tmp/collabora.home.conf /etc/nginx/sites-available/collabora.home.conf && sudo ln -sf /etc/nginx/sites-available/collabora.home.conf /etc/nginx/sites-enabled/collabora.home.conf"

    # Step 3: Add DNS entry
    step "Adding DNS entry for collabora.home..."
    ssh "$FNET1" "grep -q 'collabora.home' /etc/hosts || echo '192.168.0.141  collabora.home' | sudo tee -a /etc/hosts"

    # Step 4: Test Nginx config
    step "Testing Nginx configuration..."
    ssh "$FNET1" "sudo nginx -t" || error "Nginx config test failed"

    # Step 5: Reload Nginx + start Collabora
    step "Reloading Nginx and starting Collabora container..."
    ssh "$FNET1" "sudo systemctl reload nginx && cd $COMPOSE_DIR && docker compose up -d collabora"

    # Step 6: Wait for Collabora to be healthy
    step "Waiting for Collabora to start (30s)..."
    sleep 30
    ssh "$FNET1" "docker ps --format '{{.Names}} {{.Status}}' | grep collabora" || warn "Collabora container may not be healthy yet"

    # Step 7: Verify Collabora WOPI discovery
    step "Verifying Collabora WOPI discovery..."
    ssh "$FNET1" "curl -sk https://collabora.home/hosting/discovery 2>/dev/null | head -5" || warn "WOPI discovery not reachable yet"

    # Step 8: Install and configure richdocuments app
    step "Installing richdocuments (Nextcloud Office) app..."
    ssh "$FNET1" "docker exec nextcloud-app php occ app:install richdocuments 2>/dev/null || echo 'Already installed'"
    ssh "$FNET1" "docker exec nextcloud-app php occ app:enable richdocuments"

    step "Configuring WOPI URL..."
    ssh "$FNET1" "docker exec nextcloud-app php occ config:app:set richdocuments wopi_url --value='https://collabora.home'"

    info "Phase 2B complete. ✅ Collabora CODE deployed."
}

# =============================================================================
# Phase 2C: Server Configuration (External Storage + notify_push)
# =============================================================================
phase_2c_server() {
    info "========================================="
    info "Phase 2C: Server Configuration"
    info "========================================="

    # Step 1: Ensure bind mount in docker-compose
    step "Verifying bind mount for /srv/archive/dropbox..."
    ssh "$FNET1" "docker inspect nextcloud-app --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'" | grep -q "archive" || {
        info "Restarting NextCloud stack to pick up new bind mount..."
        ssh "$FNET1" "cd $COMPOSE_DIR && docker compose up -d"
        sleep 15
    }

    # Step 2: Enable External Storage
    step "Enabling files_external app..."
    ssh "$FNET1" "docker exec nextcloud-app php occ app:enable files_external"

    # Step 3: Install notify_push for VFS instant change detection
    step "Installing notify_push (required for responsive VFS)..."
    ssh "$FNET1" "docker exec nextcloud-app php occ app:install notify_push 2>/dev/null || echo 'Already installed'"
    ssh "$FNET1" "docker exec nextcloud-app php occ app:enable notify_push"

    # Step 4: Scan files
    step "Scanning files for External Storage..."
    ssh "$FNET1" "docker exec -u www-data nextcloud-app php occ files:scan --all"

    info ""
    info "==============================================="
    info "MANUAL STEP REQUIRED:"
    info "1. Go to https://nextcloud.home"
    info "2. Settings → Administration → External Storage"
    info "3. Click 'Add storage' → Type: Local"
    info "4. Folder name: Dropbox-Archive"
    info "5. Location: /srv/archive/dropbox"
    info "6. Available for: Carlos"
    info "7. Click the checkmark to save"
    info "==============================================="
    info ""
    read -p "Done configuring External Storage in admin UI? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Phase 2C complete. ✅ Server configured."
    else
        warn "External Storage not configured yet. Complete the manual step and re-run verification."
    fi
}

# =============================================================================
# Phase 3: Mac VFS Client Transition
# =============================================================================
phase_3_vfs() {
    info "========================================="
    info "Phase 3: Mac Client Transition (Dropbox → NextCloud VFS)"
    info "========================================="
    info ""
    warn "⚠️  IMPORTANT: This phase requires manual interaction on your Mac."
    warn "⚠️  The script will guide you through each step."
    info ""

    # Step 1: Quit Dropbox
    step "STEP 1: Quit Dropbox client"
    echo "  Open menu bar → click Dropbox icon → gear → Quit Dropbox"
    echo "  Also: System Settings → General → Login Items → disable Dropbox"
    read -p "Dropbox client is quit and disabled from auto-starting? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "Cannot proceed while Dropbox is running (both clients can't sync the same folder)."
        exit 0
    fi

    # Step 2: Launch NextCloud client
    step "STEP 2: Launch NextCloud client"
    echo "  Open /Applications/Nextcloud.app"
    read -p "NextCloud client launched? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "NextCloud client must be running."
    fi

    # Step 3: Add account
    step "STEP 3: Add NextCloud account"
    echo "  Server URL: https://nextcloud.home"
    echo "  Login with Carlos credentials"
    read -p "Account added? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Account setup is required."
    fi

    # Step 4: Choose sync folder
    step "STEP 4: Choose local sync folder"
    echo ""
    warn "⭐ CRITICAL: When prompted for local folder, choose:"
    echo "  /Users/friasc/Cloud/"
    echo ""
    echo "  When asked about existing data, choose:"
    echo "  ✅ 'Keep existing data' (NOT 'Start clean sync')"
    echo ""
    read -p "Sync folder set to ~/Cloud/ with 'Keep existing data'? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Must point at ~/Cloud/ with Keep existing data."
    fi

    # Step 5: Enable VFS
    step "STEP 5: Enable Virtual Files"
    echo "  In NextCloud client → Settings for this account"
    echo "  Enable 'Virtual Files' mode"
    read -p "VFS enabled? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "VFS not enabled. Disk space won't be freed. You can enable it later in client settings."
    fi

    # Step 6: Pin carlos-desktop
    step "STEP 6: Pin carlos-desktop/ as 'Always keep locally'"
    echo "  In Finder: navigate to ~/Cloud/carlos-desktop/"
    echo "  Right-click the folder → 'Keep locally' / 'Make available offline'"
    echo "  This ensures your pi CWD, Obsidian vault, and git repos stay on disk."
    read -p "carlos-desktop/ pinned local? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "carlos-desktop/ not pinned. Pi sessions may be slow for virtual file access."
    fi

    # Step 7: Verify
    step "STEP 7: Verify VFS state"
    echo "  In Finder, you should see:"
    echo "    carlos-desktop/ → ✅ green checkmarks (local)"
    echo "    Equity&Law/     → ☁️ cloud icons (virtual)"
    echo "    tmp/            → ☁️ cloud icons (virtual)"
    echo "    Other folders   → ☁️ cloud icons (virtual)"
    echo ""
    DF_FREE=$(df -h / | tail -1 | awk '{print $4}')
    info "Current free space: $DF_FREE"
    info "  Before migration: 87GB free"
    info "  After VFS:         ~304GB free (217GB freed)"

    read -p "VFS icons visible and disk space improved? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "Phase 3 complete. ✅ VFS activated on Mac."
        info "  carlos-desktop/ = 22GB (pinned local)"
        info "  Everything else  = virtual (cloud, on-demand)"
    else
        warn "VFS may not be configured correctly. Check NC client settings."
    fi
}

# =============================================================================
# Phase 4: rclone Setup (Backup Only)
# =============================================================================
phase_4_rclone() {
    info "========================================="
    info "Phase 4: rclone Setup (Backup Only)"
    info "========================================="

    # Step 1: Generate token
    step "Generate Dropbox OAuth token on Mac..."
    echo "  Run: rclone authorize \"dropbox\""
    echo "  This opens a browser for Dropbox login."
    echo "  Paste the resulting token JSON below."
    read -p "Have you generated the token? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "Token not generated. rclone won't be configured. You can do this later."
        info "Phase 4 deferred."
        return
    fi

    # Step 2: Run playbook (user must provide token)
    step "Run rclone playbook with token..."
    echo "  ansible-playbook -i inventory.ini configure-nextcloud-rclone.yml \\"
    echo "    -e 'rclone_dropbox_token=<YOUR_TOKEN>'"
    read -p "Playbook executed? [y/N] " -n 1 -r
    echo

    # Step 3: Uninstall files_external_dropbox
    step "Uninstalling obsolete files_external_dropbox app..."
    ssh "$FNET1" "docker exec nextcloud-app php occ app:remove files_external_dropbox" 2>/dev/null || warn "App already removed or not found"

    info "Phase 4 complete. ✅ rclone configured for backup."
    info "  Note: Create weekly backup cron after testing."
}

# =============================================================================
# Phase 5: Full Stack Verification
# =============================================================================
phase_5_verify() {
    info "========================================="
    info "Phase 5: Full Stack Verification"
    info "========================================="

    info "Checking all Docker containers..."
    ssh "$FNET1" "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

    info ""
    info "Checking disk usage on fnet1..."
    ssh "$FNET1" "df -h /srv /srv/archive"

    info ""
    info "Checking Collabora health..."
    ssh "$FNET1" "curl -sk https://collabora.home/hosting/discovery 2>/dev/null | grep -c 'wopi' && echo 'Collabora WOPI discovery: OK' || echo 'Collabora WOPI discovery: NOT YET'"

    info ""
    info "Checking NextCloud External Storage..."
    ssh "$FNET1" "docker exec nextcloud-app php occ files_external:list 2>/dev/null || echo 'No external storage configured yet'"

    info ""
    info "Checking notify_push..."
    ssh "$FNET1" "docker exec nextcloud-app php occ app:list 2>/dev/null | grep notify_push || echo 'notify_push not installed'"

    info ""
    info "Checking Mac disk space..."
    DF_FREE=$(df -h / | tail -1 | awk '{print $4}')
    info "Mac free space: $DF_FREE"
    info "  Target: ~304GB free (was 87GB before migration)"

    info ""
    info "Checking rclone..."
    ssh "$FNET1" "which rclone 2>/dev/null && rclone version || echo 'rclone not yet installed'"

    info ""
    info "========================================="
    info "Verification Summary"
    info ""
    info "Manual checks remaining:"
    info "1. Finder: carlos-desktop/ has green checkmarks (pinned local)"
    info "2. Finder: Equity&Law/ has cloud icons (virtual)"
    info "3. Spotlight: search for a known virtual file"
    info "4. VFS: double-click a virtual file → downloads and opens"
    info "5. NC web UI: open a .docx → opens in Collabora"
    info "6. NC web UI: browse Dropbox-Archive folder"
    info "7. Create a file in carlos-desktop/ → appears in NC web UI"
    info ""
    info "After 2 weeks of stable operation:"
    info "  - Pause Dropbox client (keep installed as fallback)"
    info "  - (Optional) Downgrade Dropbox subscription"
    info "========================================="
}

# =============================================================================
# Main
# =============================================================================
PHASE="${1:-all}"

info "NextCloud Migration + Collabora + VFS Deployment"
info "Target: $FNET1"
info "Phase: $PHASE"
info ""

check_ssh
check_docker

case "$PHASE" in
    2a-data)
        phase_2a_data
        ;;
    2b-collabora)
        phase_2b_collabora
        ;;
    2c-server)
        phase_2c_server
        ;;
    3-vfs)
        phase_3_vfs
        ;;
    4-rclone)
        phase_4_rclone
        ;;
    5-verify)
        phase_5_verify
        ;;
    all)
        phase_2a_data
        phase_2b_collabora
        phase_2c_server
        phase_3_vfs
        phase_4_rclone
        phase_5_verify
        ;;
    *)
        echo "Usage: $0 {all|2a-data|2b-collabora|2c-server|3-vfs|4-rclone|5-verify}"
        exit 1
        ;;
esac

info "Done!"