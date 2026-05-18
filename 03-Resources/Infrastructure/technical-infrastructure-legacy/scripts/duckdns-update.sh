#!/bin/bash
#
# duckdns-update.sh
# Updates DuckDNS with current public IP.
# Run via cron every 5 minutes.
#
# Usage: Set DUCKDNS_DOMAIN and DUCKDNS_TOKEN below, then:
#   ./duckdns-update.sh

set -e

DUCKDNS_DOMAIN="${DUCKDNS_DOMAIN:-YOUR-SUBDOMAIN}"
DUCKDNS_TOKEN="${DUCKDNS_TOKEN:-YOUR-TOKEN}"

if [ "$DUCKDNS_DOMAIN" = "YOUR-SUBDOMAIN" ] || [ "$DUCKDNS_TOKEN" = "YOUR-TOKEN" ]; then
    echo "ERROR: Set DUCKDNS_DOMAIN and DUCKDNS_TOKEN in this script first."
    exit 1
fi

RESULT=$(curl -fsSL "https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" 2>/dev/null)

if [ "$RESULT" = "OK" ]; then
    echo "[$(date)] DuckDNS update successful: ${DUCKDNS_DOMAIN}.duckdns.org"
else
    echo "[$(date)] DuckDNS update failed: ${RESULT}"
    exit 1
fi
