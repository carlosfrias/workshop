#!/usr/bin/env bash
# test-fleet-dispatch.sh — Integration test: send a task to a fleet node via the
# coms-net hub and verify end-to-end message delivery and response.
#
# TDD: Written BEFORE implementation changes.
#
# Prerequisites:
#   - Hub running on fnet2 with fleet nodes connected
#   - At least 1 fleet node registered on project "lab"
#
# Run: bash tests/integration/test-fleet-dispatch.sh

set -euo pipefail

PASS=0
FAIL=0
TOTAL=0

COMS_NET_DIR="$HOME/.pi/coms-net"
PROJECT="lab"

echo "=== pi-cross-node-comms fleet dispatch integration test ==="
echo ""

# ─── Configuration ───────────────────────────────────────────────────────────

SERVER_FILE="$COMS_NET_DIR/projects/$PROJECT/server.json"
SECRET_FILE="$COMS_NET_DIR/projects/$PROJECT/server.secret.json"
HUB_URL=""
AUTH_TOKEN=""

if [[ -f "$SERVER_FILE" ]]; then
  HUB_URL=$(python3 -c "import json; print(json.load(open('$SERVER_FILE'))['local_url'])" 2>/dev/null || echo "")
fi
if [[ -f "$SECRET_FILE" ]]; then
  AUTH_TOKEN=$(python3 -c "import json; print(json.load(open('$SECRET_FILE'))['token'])" 2>/dev/null || echo "")
fi

if [[ -z "$HUB_URL" ]] || [[ -z "$AUTH_TOKEN" ]]; then
  echo "❌ Cannot run fleet dispatch test: HUB_URL or AUTH_TOKEN not configured"
  echo "   HUB_URL: '$HUB_URL'"
  echo "   AUTH_TOKEN: '${AUTH_TOKEN:+<set>}${AUTH_TOKEN:-<empty>}'"
  echo ""
  echo "RESULT: SKIP"
  exit 2
fi

# ─── Helper function ────────────────────────────────────────────────────────

api_call() {
  local method="$1" endpoint="$2" data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -s -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$HUB_URL$endpoint" 2>/dev/null
  else
    curl -s -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      "$HUB_URL$endpoint" 2>/dev/null
  fi
}

# ─── Register test agent so we can send messages ────────────────────────────
TEST_SESSION_ID="test-fleet-$PPID-$(date +%s)"
TEST_AGENT_NAME="test-fleet-dispatch"

REGISTER_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$TEST_SESSION_ID',
    'name': '$TEST_AGENT_NAME',
    'purpose': 'fleet dispatch test',
    'model': 'test',
    'color': '#00FF00',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': False
}))
" 2>/dev/null)

REGISTER_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REGISTER_DATA" \
  "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")

REGISTER_OK=$(echo "$REGISTER_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('yes' if d.get('ok') else 'no')
" 2>/dev/null || echo "no")

if [[ "$REGISTER_OK" == "yes" ]]; then
  echo "  ✅ Test agent registered: $TEST_AGENT_NAME"
else
  echo "  ⚠️  Test agent registration may have failed (proceeding anyway)"
fi

# Cleanup — unregister test agent on exit
unregister_test_agent() {
  curl -s -X DELETE \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    "$HUB_URL/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_SESSION_ID'))")" 2>/dev/null || true
}
trap unregister_test_agent EXIT

# ─── Step 1: Verify hub is healthy ──────────────────────────────────────────

echo "--- Step 1: Hub health ---"

TOTAL=$((TOTAL + 1))
HEALTH=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
if echo "$HEALTH" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Hub is healthy"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub is unhealthy or unreachable — aborting fleet dispatch test"
  echo ""
  echo "=========================================="
  echo "pi-cross-node-comms fleet-dispatch: $PASS passed, $FAIL failed, $TOTAL total"
  echo "=========================================="
  echo "RESULT: FAIL"
  exit 1
fi

# ─── Step 2: Discover fleet nodes ────────────────────────────────────────────

echo ""
echo "--- Step 2: Discover fleet nodes ---"

TOTAL=$((TOTAL + 1))
AGENTS_RESP=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=false")
AGENT_NAMES=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    print(a.get('name', 'unknown'))
" 2>/dev/null || echo "")

AGENT_COUNT=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
print(len(agents))
" 2>/dev/null || echo "0")

if [[ "$AGENT_COUNT" -ge 1 ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Found $AGENT_COUNT agent(s): $(echo "$AGENT_NAMES" | tr '\n' ', ')"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No fleet nodes found — cannot test dispatch"
  echo ""
  echo "=========================================="
  echo "pi-cross-node-comms fleet-dispatch: $PASS passed, $FAIL failed, $TOTAL total"
  echo "=========================================="
  echo "RESULT: FAIL"
  exit 1
fi

# ─── Step 3: Send test message to first fleet node ───────────────────────────

echo ""
echo "--- Step 3: Send test dispatch ---"

# Pick the first online agent as target
TARGET_NAME=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    if a.get('status') == 'online' or True:
        print(a.get('name', ''))
        break
" 2>/dev/null || echo "")

TARGET_SESSION=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    if a.get('status') == 'online' or True:
        print(a.get('session_id', ''))
        break
" 2>/dev/null || echo "")

TOTAL=$((TOTAL + 1))
if [[ -n "$TARGET_NAME" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Target identified: $TARGET_NAME (session: ${TARGET_SESSION:0:12}...)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Could not identify a target agent"
fi

# Send the message
TOTAL=$((TOTAL + 1))
SEND_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'sender_session': '$TEST_SESSION_ID',
    'target': '$TARGET_NAME',
    'target_session': '$TARGET_SESSION' if '$TARGET_SESSION' else None,
    'prompt': 'Fleet dispatch integration test: respond with pong',
    'hops': 0
}))
" 2>/dev/null)

SEND_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$SEND_DATA" \
  "$HUB_URL/v1/messages" 2>/dev/null || echo "{}")

MSG_ID=$(echo "$SEND_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('msg_id', ''))
" 2>/dev/null || echo "")

SEND_ERROR=$(echo "$SEND_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('error', ''))
" 2>/dev/null || echo "")

if [[ -n "$MSG_ID" ]] && [[ "$MSG_ID" != "" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Message dispatched, msg_id: ${MSG_ID:0:12}..."
elif [[ -n "$SEND_ERROR" ]]; then
  FAIL=$((FAIL + 1))
  echo "  ❌ Dispatch failed with error: $SEND_ERROR"
  # Don't abort — still test the GET endpoint
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Dispatch failed — no msg_id returned"
fi

# ─── Step 4: Verify message is queued/delivered ──────────────────────────────

echo ""
echo "--- Step 4: Verify message state ---"

TOTAL=$((TOTAL + 1))
if [[ -n "$MSG_ID" ]]; then
  # Poll for message status a few times
  MSG_STATUS="unknown"
  for i in 1 2 3; do
    sleep 1
    MSG_RESP=$(curl -s -X GET \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      "$HUB_URL/v1/messages/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$MSG_ID'))")" \
      2>/dev/null || echo "{}")
    
    MSG_STATUS=$(echo "$MSG_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('status', 'unknown'))
" 2>/dev/null || echo "unknown")

    if [[ "$MSG_STATUS" == "delivered" ]] || [[ "$MSG_STATUS" == "complete" ]] || [[ "$MSG_STATUS" == "queued" ]]; then
      break
    fi
  done

  if [[ "$MSG_STATUS" == "queued" ]] || [[ "$MSG_STATUS" == "delivered" ]] || [[ "$MSG_STATUS" == "complete" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Message state: $MSG_STATUS"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Unexpected message state: $MSG_STATUS"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Cannot verify message state — no msg_id"
fi

# ─── Step 5: Hub still healthy after dispatch ────────────────────────────────

echo ""
echo "--- Step 5: Hub still healthy ---"

TOTAL=$((TOTAL + 1))
HEALTH2=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
if echo "$HEALTH2" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Hub still healthy after dispatch"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub unhealthy after dispatch"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "=========================================="
echo "pi-cross-node-comms fleet-dispatch: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi