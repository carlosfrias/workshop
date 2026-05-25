#!/bin/bash
# NextCloud Backup Script
# Runs on fnet1, rsyncs NextCloud data to fnet6:/srv/archive/nextcloud/
#
# Usage: backup-nextcloud.sh [--dry-run]
#   --dry-run   Show what would be transferred without making changes
#
# Managed by Ansible playbook: backup-nextcloud.yml
# Called via: ./scripts/run-playbook.sh "backup nextcloud"

set -euo pipefail

REMOTE_HOST="friasc@192.168.0.146"
REMOTE_BASE="/srv/archive/nextcloud"
LOCAL_DATA="/srv/archive/nextcloud-data/config"
LOCAL_DB="/srv/nextcloud/db"
LOCAL_CONFIG="/srv/nextcloud/config"

# Optional: full user data backup (uncomment if fnet6 has space)
# LOCAL_USER_DATA="/srv/archive/nextcloud-data/data"
LOG_FILE="/srv/nextcloud/backup.log"

RSYNC_OPTS="-az --delete --compress-level=6 --human-readable --itemize-changes"

if [[ "${1:-}" == "--dry-run" ]]; then
    RSYNC_OPTS="$RSYNC_OPTS --dry-run"
    echo "=== DRY RUN ==="
fi

# Create remote directory
ssh "$REMOTE_HOST" "sudo mkdir -p $REMOTE_BASE/{data,db,config} && sudo chown friasc:friasc $REMOTE_BASE $REMOTE_BASE/{data,db,config}" 2>/dev/null || true

# Enable NextCloud maintenance mode
docker exec nextcloud-app php occ maintenance:mode --on 2>/dev/null || true

# Record start time
START_TIME=$(date +%s)
echo "$(date '+%Y-%m-%d %H:%M:%S') — Backup started" | tee -a "$LOG_FILE"

# Rsync NextCloud config (app config, not user data)
echo ">>> Syncing config directory..."
rsync $RSYNC_OPTS "$LOCAL_CONFIG/" "$REMOTE_HOST:$REMOTE_BASE/config/" 2>&1 | tee -a "$LOG_FILE"

# Rsync database
echo ">>> Syncing database directory..."
rsync $RSYNC_OPTS "$LOCAL_DB/" "$REMOTE_HOST:$REMOTE_BASE/db/" 2>&1 | tee -a "$LOG_FILE"

# Rsync NextCloud config from data directory
echo ">>> Syncing NC app data config..."
rsync $RSYNC_OPTS "$LOCAL_DATA/" "$REMOTE_HOST:$REMOTE_BASE/app-config/" 2>&1 | tee -a "$LOG_FILE"

# Disable maintenance mode
docker exec nextcloud-app php occ maintenance:mode --off 2>/dev/null || true

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "$(date '+%Y-%m-%d %H:%M:%S') — Backup completed in ${ELAPSED}s" | tee -a "$LOG_FILE"