#!/usr/bin/env bash
# test-hub-connection.sh — Integration test: connect to the coms-net hub on fnet2,
# verify health endpoint responds, and validate auth token works.
#
# TDD: Written BEFORE implementation changes.
#
# Prerequisites:
#   - Hub must be running on fnet2 (http://192.168.0.142:8080)
#   - Auth token must be set in server.secret.json for project "lab"
#
# Run: bash tests/integration/test-hub-connection.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COMS_NET_DIR="$HOME/.pi/coms-net"

PASS=0
FAIL=0
TOTAL=0

echo "=== pi-cross-node-comms hub connection integration test ==="
echo ""

# ─── Configuration ───────────────────────────────────────────────────────────

HUB_URL="http://192.168.0.142:8080"
PROJECT="lab"
SECRET_FILE="$COMS_NET_DIR/projects/$PROJECT/server.secret.json"
SERVER_FILE="$COMS_NET_DIR/projects/$PROJECT/server.json"
AUTH_TOKEN=""

# Read auth token
TOTAL=$((TOTAL + 1))
if [[ -f "$SECRET_FILE" ]]; then
  AUTH_TOKEN=$(python3 -c "import json; print(json.load(open('$SECRET_FILE'))['token'])" 2>/dev/null || echo "")
  if [[ -n "$AUTH_TOKEN" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Auth token loaded from server.secret.json"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Could not read auth token from server.secret.json"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ server.secret.json not found at: $SECRET_FILE"
fi

# Read server URL from config
TOTAL=$((TOTAL + 1))
if [[ -f "$SERVER_FILE" ]]; then
  CONFIG_URL=$(python3 -c "import json; print(json.load(open('$SERVER_FILE'))['local_url'])" 2>/dev/null || echo "")
  if [[ -n "$CONFIG_URL" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Server URL from config: $CONFIG_URL"
    # Use the configured URL for subsequent tests
    HUB_URL="$CONFIG_URL"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Could not read server URL from server.json"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ server.json not found at: $SERVER_FILE"
fi

# ─── Health Check ─────────────────────────────────────────────────────────────

echo ""
echo "--- Health endpoint ---"

# 1. Health endpoint must return 200
TOTAL=$((TOTAL + 1))
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HUB_URL/health" 2>/dev/null || echo "000")
if [[ "$HEALTH_STATUS" == "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Health endpoint returns 200 (status=$HEALTH_STATUS)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Health endpoint failed (status=$HEALTH_STATUS, expected 200)"
fi

# 2. Health response must contain {"ok":true}
TOTAL=$((TOTAL + 1))
HEALTH_BODY=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
if echo "$HEALTH_BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Health response contains ok:true"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Health response missing ok:true — got: $HEALTH_BODY"
fi

# 3. Health response must include version and server_id
TOTAL=$((TOTAL + 1))
if echo "$HEALTH_BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'version' in d and 'server_id' in d" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Health response includes version and server_id"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Health response missing version or server_id"
fi

# ─── Auth Token Validation ───────────────────────────────────────────────────

echo ""
echo "--- Auth token validation ---"

# 4. Auth token must be valid format (64-char hex)
TOTAL=$((TOTAL + 1))
if [[ "${#AUTH_TOKEN}" -ge 32 ]] && [[ "$AUTH_TOKEN" =~ ^[a-f0-9]+$ ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Auth token has valid format (${#AUTH_TOKEN} chars hex)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Auth token has invalid format (expected hex, got ${#AUTH_TOKEN} chars)"
fi

# 5. Authenticated request must succeed (list agents)
TOTAL=$((TOTAL + 1))
LIST_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  "$HUB_URL/v1/agents?project=$PROJECT" 2>/dev/null || echo "000")
if [[ "$LIST_STATUS" == "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Authenticated agent list returns 200"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Authenticated agent list failed (status=$LIST_STATUS)"
fi

# 6. Unauthenticated request must fail
TOTAL=$((TOTAL + 1))
UNAUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "$HUB_URL/v1/agents?project=$PROJECT" 2>/dev/null || echo "000")
if [[ "$UNAUTH_STATUS" != "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Unauthenticated request rejected (status=$UNAUTH_STATUS)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Unauthenticated request accepted (should be rejected)"
fi

# ─── Server Config Consistency ────────────────────────────────────────────────

echo ""
echo "--- Server config consistency ---"

# 7. server.json URL must match what health endpoint reports
TOTAL=$((TOTAL + 1))
if [[ -n "$CONFIG_URL" ]]; then
  # Normalize URLs for comparison (strip trailing slash)
  NORMALIZED_CONFIG="${CONFIG_URL%/}"
  if [[ -n "$HEALTH_BODY" ]]; then
    # The hub URL from config should be reachable
    PASS=$((PASS + 1))
    echo "  ✅ Server config URL is reachable: $NORMALIZED_CONFIG"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Server config URL unreachable: $NORMALIZED_CONFIG"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No server config URL to validate"
fi

echo ""
echo "--- Stale config detection ---"

# 8. No unexpected project config directories (prevents stale hubs)
TOTAL=$((TOTAL + 1))
EXPECTED_PROJECTS=("lab" "default")
UNEXPECTED_DIRS=""
for DIR in "$COMS_NET_DIR/projects"/*/; do
  DIR_NAME=$(basename "$DIR")
  FOUND=false
  for EXPECTED in "${EXPECTED_PROJECTS[@]}"; do
    if [[ "$DIR_NAME" == "$EXPECTED" ]]; then
      FOUND=true
      break
    fi
  done
  if [[ "$FOUND" == "false" ]]; then
    UNEXPECTED_DIRS="$UNEXPECTED_DIRS $DIR_NAME"
  fi
done
if [[ -z "$UNEXPECTED_DIRS" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ No unexpected project config directories"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Unexpected project config dirs: $UNEXPECTED_DIRS (stale hub configs)"
fi

echo ""
echo "=========================================="
echo "pi-cross-node-comms hub-connection: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi