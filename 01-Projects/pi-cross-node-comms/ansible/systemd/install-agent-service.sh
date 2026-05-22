#!/usr/bin/env bash
#
# install-agent-service.sh — Install and enable the pi-cross-node-agent systemd service
#
# Usage:   ./install-agent-service.sh [--hostname HOSTNAME] [--env-file PATH]
# Example: ./install-agent-service.sh --hostname fnet3
#
# This script is designed to be called by Ansible in standup-fleet.yml Phase 5,
# but can also be run manually on individual nodes.
#
# It:
#   1. Templates the systemd unit with actual values from the env file
#   2. Installs the unit to /etc/systemd/system/
#   3. Copies the env file with secure permissions (0600, root:root)
#   4. Enables and starts the service
#   5. Verifies the service is running

set -euo pipefail

# ─── Defaults ──────────────────────────────────────────────────────────────

HOSTNAME="${HOSTNAME:-$(hostname -s)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/pi-cross-node-agent.conf"
UNIT_TEMPLATE="${SCRIPT_DIR}/pi-cross-node-agent@.service.template"
SERVICE_NAME="pi-cross-node-agent@${HOSTNAME}"
DRY_RUN=false

# ─── Parse Args ────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --hostname)       HOSTNAME="$2"; shift 2 ;;
        --env-file)       ENV_FILE="$2"; shift 2 ;;
        --dry-run)        DRY_RUN=true; shift ;;
        -h|--help)
            echo "Usage: $0 [--hostname HOSTNAME] [--env-file PATH] [--dry-run]"
            exit 0 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

SERVICE_NAME="pi-cross-node-agent@${HOSTNAME}"

echo "═══════════════════════════════════════════════════"
echo "  pi-cross-node-agent service installer"
echo "  Hostname:   ${HOSTNAME}"
echo "  Service:    ${SERVICE_NAME}"
echo "  Env file:   ${ENV_FILE}"
echo "═══════════════════════════════════════════════════"

if [[ "$DRY_RUN" == "true" ]]; then
    echo "(dry run — no changes will be made)"
fi

# ─── Load env file ────────────────────────────────────────────────────────

if [[ ! -f "$ENV_FILE" ]]; then
    echo "❌ Env file not found: ${ENV_FILE}"
    exit 1
fi

# Shellcheck: env file may contain spaces in values, use proper quoting
declare -A ENV_VARS
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue
    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)
    ENV_VARS["$key"]="$value"
done < "$ENV_FILE"

HUB_URL="${ENV_VARS[HUB_URL]:-http://192.168.0.142:8080}"
COMS_TOKEN="${ENV_VARS[COMS_TOKEN]:-}"
HUB_PROJECT="${ENV_VARS[HUB_PROJECT]:-lab}"
EXTENSION_PATH="${ENV_VARS[EXTENSION_PATH]:-/home/${HOSTNAME}/pi-cross-node-comms}"

if [[ -z "$COMS_TOKEN" ]]; then
    echo "❌ COMS_TOKEN is required in env file"
    exit 1
fi

echo "  Hub URL:        ${HUB_URL}"
echo "  Project:        ${HUB_PROJECT}"
echo "  Extension path: ${EXTENSION_PATH}"
echo "  Token:          ${COMS_TOKEN:0:8}..."

# ─── Template the systemd unit ─────────────────────────────────────────────

if [[ ! -f "$UNIT_TEMPLATE" ]]; then
    echo "❌ Unit template not found: ${UNIT_TEMPLATE}"
    exit 1
fi

UNIT_CONTENT=$(sed \
    -e "s|{{ HUB_URL }}|${HUB_URL}|g" \
    -e "s|{{ COMS_TOKEN }}|${COMS_TOKEN}|g" \
    -e "s|{{ HUB_PROJECT }}|${HUB_PROJECT}|g" \
    -e "s|{{ EXTENSION_PATH }}|${EXTENSION_PATH}|g" \
    "$UNIT_TEMPLATE"
)

# ─── Install ───────────────────────────────────────────────────────────────

install_unit() {
    local unit_name="${SERVICE_NAME}.service"
    local target="/etc/systemd/system/${unit_name}"
    local tmp_target="/tmp/${unit_name}"

    echo ""
    echo "Installing systemd unit: ${unit_name}"

    # Write to temp first
    echo "$UNIT_CONTENT" > "$tmp_target"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "(dry run) Would install unit to ${target}:"
        echo "---"
        cat "$tmp_target"
        echo "---"
        rm -f "$tmp_target"
        return
    fi

    # Install unit
    sudo cp "$tmp_target" "$target"
    rm -f "$tmp_target"
    sudo chmod 644 "$target"

    echo "✅ Unit installed: ${target}"
}

install_env() {
    local target="/etc/pi-cross-node-agent.conf"
    local target_per_instance="/etc/pi-cross-node-agent@${HOSTNAME}.conf"

    echo ""
    echo "Installing env file: ${target_per_instance}"

    if [[ "$DRY_RUN" == "true" ]]; then
        echo "(dry run) Would install env to ${target_per_instance}"
        return
    fi

    # Install per-instance env file with secure permissions
    sudo cp "$ENV_FILE" "$target_per_instance"
    sudo chmod 600 "$target_per_instance"
    sudo chown root:root "$target_per_instance"

    # Also install the shared default
    sudo cp "$ENV_FILE" "$target"
    sudo chmod 600 "$target"
    sudo chown root:root "$target"

    echo "✅ Env installed: ${target_per_instance} (0600, root:root)"
}

enable_and_start() {
    if [[ "$DRY_RUN" == "true" ]]; then
        echo ""
        echo "(dry run) Would run:"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable ${SERVICE_NAME}"
        echo "  sudo systemctl start ${SERVICE_NAME}"
        echo "  sudo systemctl status ${SERVICE_NAME}"
        return
    fi

    echo ""
    echo "Enabling and starting ${SERVICE_NAME}..."

    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}"
    sudo systemctl start "${SERVICE_NAME}"

    # Wait for service to settle
    sleep 3

    # Verify
    if sudo systemctl is-active --quiet "${SERVICE_NAME}"; then
        echo "✅ ${SERVICE_NAME} is running"
    else
        echo "⚠️  ${SERVICE_NAME} may have failed to start. Checking journal..."
        sudo journalctl -u "${SERVICE_NAME}" --no-pager -n 20
        exit 1
    fi
}

# ─── Execute ───────────────────────────────────────────────────────────────

install_unit
install_env
enable_and_start

echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ pi-cross-node-agent@${HOSTNAME} installed and running"
echo ""
echo "  Manage with:"
echo "    systemctl status ${SERVICE_NAME}"
echo "    journalctl -u ${SERVICE_NAME} -f"
echo "    systemctl restart ${SERVICE_NAME}"
echo "    systemctl stop ${SERVICE_NAME}"
echo "═══════════════════════════════════════════════════"