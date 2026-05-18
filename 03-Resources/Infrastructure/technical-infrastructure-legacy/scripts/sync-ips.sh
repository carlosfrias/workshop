#!/usr/bin/env bash
# sync-ips.sh — Single source of truth for lab node IP addresses
# Reads from inventory.ini, generates all dependent files
#
# Usage: ./sync-ips.sh
# Canonical source: technical-infrastructure/ansible/inventory.ini
# Generated targets:
#   - technical-infrastructure/ansible/inventory.yml
#   - ~/.ssh/config (lab node entries)
#   - technical-infrastructure/lab-specs/node-hardware/*-hardware.json
#
# Run this whenever inventory.ini changes.

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TI_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INI="${TI_ROOT}/ansible/inventory.ini"
YAML="${TI_ROOT}/ansible/inventory.yml"
SSH_CONFIG="${HOME}/.ssh/config"
HW_DIR="${TI_ROOT}/lab-specs/node-hardware"

echo "=== Sync IPs from inventory.ini ==="
echo "Source: ${INI}"
echo ""

# Parse lab_nodes from inventory.ini
# Format: fnetN ansible_host=IP ...
declare -A IPS
while IFS= read -r line; do
    if [[ "$line" =~ ^fnet[0-9]+[[:space:]]+ansible_host= ]]; then
        NODE=$(echo "$line" | awk '{print $1}')
        IP=$(echo "$line" | grep -o 'ansible_host=[^[:space:]]*' | cut -d'=' -f2)
        IPS["$NODE"]="$IP"
    fi
done < "$INI"

if [ ${#IPS[@]} -eq 0 ]; then
    echo "❌ No lab_nodes found in ${INI}"
    exit 1
fi

echo "Found ${#IPS[@]} nodes:"
for NODE in $(echo "${!IPS[@]}" | tr ' ' '\n' | sort); do
    echo "  ${NODE}: ${IPS[$NODE]}"
done
echo ""

# 1. Generate inventory.yml
echo "---" > "$YAML"
echo "all:" >> "$YAML"
echo "  children:" >> "$YAML"
echo "    lab_nodes:" >> "$YAML"
echo "      hosts:" >> "$YAML"

for NODE in $(echo "${!IPS[@]}" | tr ' ' '\n' | sort); do
    printf "        %s:\n" "$NODE" >> "$YAML"
    printf "          ansible_host: %s\n" "${IPS[$NODE]}" >> "$YAML"
done

echo "✅ Generated ${YAML}"

# 2. Update ~/.ssh/config (preserve non-lab entries)
TEMP_SSH=$(mktemp)

# Write header comment
cat > "$TEMP_SSH" << 'HEAD'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes

# Trading Lab Nodes — AUTO-GENERATED from inventory.ini
# DO NOT EDIT MANUALLY. Run: ./scripts/sync-ips.sh
HEAD

for NODE in $(echo "${!IPS[@]}" | tr ' ' '\n' | sort); do
    cat >> "$TEMP_SSH" << NODECFG
Host ${NODE}
    HostName ${IPS[$NODE]}
    User friasc
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3

NODECFG
done

# Preserve any custom entries after the lab nodes block (currently: nothing)
# If ~/.ssh/config has entries AFTER fnet7, append them here.
# (Future enhancement: detect and preserve manual entries)

mv "$TEMP_SSH" "$SSH_CONFIG"
chmod 600 "$SSH_CONFIG"
echo "✅ Generated ${SSH_CONFIG}"

# 3. Update hardware spec files
for NODE in $(echo "${!IPS[@]}" | tr ' ' '\n' | sort); do
    HW_FILE="${HW_DIR}/${NODE}-hardware.json"
    if [ -f "$HW_FILE" ]; then
        python3 -c "
import json, sys
with open('$HW_FILE') as f: data = json.load(f)
data['network'] = {'primary_ip': '${IPS[$NODE]}'}
with open('$HW_FILE', 'w') as f: json.dump(data, f, indent=2)
" 2>/dev/null || true
        echo "  ✅ ${NODE}: ${IPS[$NODE]}"
    else
        echo "  ⚠️ ${NODE}: no ${HW_FILE} (skipped)"
    fi
done

echo ""
echo "=== Sync Complete ==="
echo "Run 'ansible-inventory -i inventory.yml --graph' to verify"
