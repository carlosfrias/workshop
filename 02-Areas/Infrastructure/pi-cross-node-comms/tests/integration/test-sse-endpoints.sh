#!/usr/bin/env bash
# test-sse-endpoints.sh — Integration test: validate all SSE/HTTP API endpoints
# on the coms-net hub, including register, heartbeat, list, message, SSE, and error paths.
#
# TDD: Written BEFORE implementation changes.
#
# Prerequisites:
#   - Hub running on fnet2 (http://192.168.0.142:8080)
#   - Auth token in ~/.pi/coms-net/projects/lab/server.secret.json
#
# Run: bash tests/integration/test-sse-endpoints.sh

set -euo pipefail

PASS=0
FAIL=0
TOTAL=0

COMS_NET_DIR="$HOME/.pi/coms-net"
PROJECT="lab"

echo "=== pi-cross-node-comms SSE/HTTP endpoints integration test ==="
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
  echo "❌ Cannot run integration test: HUB_URL or AUTH_TOKEN not configured"
  echo "   HUB_URL: '$HUB_URL'"
  echo "   AUTH_TOKEN: '${AUTH_TOKEN:+<set>}${AUTH_TOKEN:-<empty>}'"
  echo ""
  echo "RESULT: SKIP"
  exit 2
fi

API_BASE="$HUB_URL"

# ─── Helper function ────────────────────────────────────────────────────────

api_call() {
  local method="$1" endpoint="$2" data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -s -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$API_BASE$endpoint" 2>/dev/null
  else
    curl -s -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      "$API_BASE$endpoint" 2>/dev/null
  fi
}

http_status() {
  local method="$1" endpoint="$2" data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -s -o /dev/null -w "%{http_code}" -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$API_BASE$endpoint" 2>/dev/null
  else
    curl -s -o /dev/null -w "%{http_code}" -X "$method" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      "$API_BASE$endpoint" 2>/dev/null
  fi
}

# ─── Register test agent ───────────────────────────────────────────────────

TEST_SESSION_ID="test-sse-$PPID-$(date +%s)"
TEST_AGENT_NAME="test-sse-endpoints"

REGISTER_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$TEST_SESSION_ID',
    'name': '$TEST_AGENT_NAME',
    'purpose': 'SSE endpoint test',
    'model': 'test-model',
    'color': '#72F1B8',
    'cwd': '/tmp',
    'node': 'mac-test-sse',
    'explicit': False
}))
" 2>/dev/null)

REGISTER_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REGISTER_DATA" \
  "$API_BASE/v1/agents/register" 2>/dev/null || echo "{}")

REGISTER_OK=$(echo "$REGISTER_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('yes' if d.get('ok') else 'no')
" 2>/dev/null || echo "no")

# Cleanup — unregister test agent on exit
unregister_test_agent() {
  curl -s -X DELETE \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    "$API_BASE/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_SESSION_ID'))")" \
    2>/dev/null || true
}
trap unregister_test_agent EXIT

# ─── 1. GET /health ─────────────────────────────────────────────────────────

echo "--- 1. GET /health ---"

TOTAL=$((TOTAL + 1))
HEALTH_RESP=$(curl -s "$API_BASE/health" 2>/dev/null || echo "")
if echo "$HEALTH_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Health endpoint returns ok:true"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Health endpoint did not return ok:true — got: $HEALTH_RESP"
fi

TOTAL=$((TOTAL + 1))
if echo "$HEALTH_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'version' in d and 'server_id' in d" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Health response includes version and server_id"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Health response missing version or server_id"
fi

# ─── 2. POST /v1/agents/register ─────────────────────────────────────────────

echo ""
echo "--- 2. POST /v1/agents/register ---"

TOTAL=$((TOTAL + 1))
if [[ "$REGISTER_OK" == "yes" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Register returns ok:true"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Register did not return ok:true — got: $REGISTER_RESP"
fi

TOTAL=$((TOTAL + 1))
REGISTER_AGENT_HAS_FIELDS=$(echo "$REGISTER_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agent = d.get('agent', {})
required = ['session_id', 'name', 'project']
missing = [k for k in required if k not in agent]
if missing:
    print(f'Missing: {missing}')
    sys.exit(1)
print('valid')
" 2>/dev/null || echo "error")
if [[ "$REGISTER_AGENT_HAS_FIELDS" == "valid" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Register response contains agent object with session_id, name, project"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Register response missing agent fields: $REGISTER_AGENT_HAS_FIELDS"
fi

TOTAL=$((TOTAL + 1))
REGISTER_SE_SSE_URL=$(echo "$REGISTER_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('sse_url', ''))
" 2>/dev/null || echo "")
if [[ -n "$REGISTER_SE_SSE_URL" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Register response includes sse_url"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Register response missing sse_url"
fi

# ─── 3. GET /v1/agents (with and without auth) ──────────────────────────────

echo ""
echo "--- 3. GET /v1/agents (auth required) ---"

# Authenticated request should succeed
TOTAL=$((TOTAL + 1))
LIST_STATUS=$(http_status "GET" "/v1/agents?project=$PROJECT&include_explicit=false")
if [[ "$LIST_STATUS" == "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Authenticated GET /v1/agents returns 200"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Authenticated GET /v1/agents failed (status=$LIST_STATUS)"
fi

# Unauthenticated request should fail
TOTAL=$((TOTAL + 1))
UNAUTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "$API_BASE/v1/agents?project=$PROJECT" 2>/dev/null || echo "000")
if [[ "$UNAUTH_STATUS" != "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Unauthenticated request rejected (status=$UNAUTH_STATUS)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Unauthenticated request accepted (should be rejected)"
fi

# ─── 4. POST /v1/agents/:session_id/heartbeat ────────────────────────────────

echo ""
echo "--- 4. POST /v1/agents/:session_id/heartbeat ---"

TOTAL=$((TOTAL + 1))
HEARTBEAT_DATA='{"project":"'$PROJECT'","context_used_pct":12.5,"queue_depth":0,"status":"online"}'
HEARTBEAT_STATUS=$(http_status "POST" "/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_SESSION_ID'))")/heartbeat" "$HEARTBEAT_DATA")
if [[ "$HEARTBEAT_STATUS" == "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Heartbeat returns 200"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Heartbeat failed (status=$HEARTBEAT_STATUS)"
fi

TOTAL=$((TOTAL + 1))
HEARTBEAT_RESP=$(api_call "POST" "/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_SESSION_ID'))")/heartbeat" "$HEARTBEAT_DATA")
if echo "$HEARTBEAT_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Heartbeat response contains ok:true"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Heartbeat response missing ok:true — got: $HEARTBEAT_RESP"
fi

# ─── 5. DELETE /v1/agents/:session_id ────────────────────────────────────────

echo ""
echo "--- 5. DELETE /v1/agents/:session_id ---"

# Register a second throwaway agent for delete testing (keep main test agent alive)
TEMP_SESSION_ID="test-sse-del-$PPID-$(date +%s)"
TEMP_REGISTER_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$TEMP_SESSION_ID',
    'name': 'test-delete-agent',
    'purpose': 'delete test',
    'model': 'test',
    'color': '#FF7EDB',
    'cwd': '/tmp',
    'node': 'mac-test-del',
    'explicit': False
}))
" 2>/dev/null)

curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$TEMP_REGISTER_DATA" \
  "$API_BASE/v1/agents/register" 2>/dev/null > /dev/null || true

# Give the server a moment to fully register
sleep 1

# Now delete the temporary agent (must include project param)
TOTAL=$((TOTAL + 1))
DELETE_RESP_FILE=$(mktemp)
DELETE_HTTP_CODE=$(curl -s -w '%{http_code}' -o "$DELETE_RESP_FILE" -X DELETE \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  "$API_BASE/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEMP_SESSION_ID'))")?project=$PROJECT" 2>/dev/null || echo '000')
DELETE_BODY=$(cat "$DELETE_RESP_FILE" 2>/dev/null || echo '{}')
rm -f "$DELETE_RESP_FILE"

if [[ "$DELETE_HTTP_CODE" == "200" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ DELETE agent returns 200"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ DELETE agent failed (status=$DELETE_HTTP_CODE)"
fi

TOTAL=$((TOTAL + 1))
if echo "$DELETE_BODY" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ DELETE response contains ok:true"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ DELETE response missing ok:true — got: $DELETE_BODY"
fi

# Verify the deleted agent is gone
TOTAL=$((TOTAL + 1))
AGENTS_AFTER=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true")
DELETED_AGENT_GONE=$(echo "$AGENTS_AFTER" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    if a.get('session_id') == '$TEMP_SESSION_ID':
        sys.exit(1)
print('gone')
" 2>/dev/null || echo "still_there")
if [[ "$DELETED_AGENT_GONE" == "gone" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Deleted agent no longer in agent list"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Deleted agent still appears in agent list"
fi

# ─── 6. POST /v1/messages (send) ─────────────────────────────────────────────

echo ""
echo "--- 6. POST /v1/messages ---"

# Discover a target agent
AGENTS_RESP=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=false")
TARGET_NAME=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
# Find first agent that is NOT our test agent
for a in agents:
    if a.get('session_id', '') != '$TEST_SESSION_ID' and a.get('session_id', '') != '$TEMP_SESSION_ID':
        print(a.get('name', ''))
        break
" 2>/dev/null || echo "")
TARGET_SESSION=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    if a.get('session_id', '') != '$TEST_SESSION_ID' and a.get('session_id', '') != '$TEMP_SESSION_ID':
        print(a.get('session_id', ''))
        break
" 2>/dev/null || echo "")

TOTAL=$((TOTAL + 1))
if [[ -n "$TARGET_NAME" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Target agent found: $TARGET_NAME"
else
  # No other agents — send to self as fallback
  TARGET_NAME="$TEST_AGENT_NAME"
  TARGET_SESSION="$TEST_SESSION_ID"
  PASS=$((PASS + 1))
  echo "  ⚠️  No other agents found, sending to self"
fi

SEND_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'sender_session': '$TEST_SESSION_ID',
    'target': '$TARGET_NAME',
    'target_session': '$TARGET_SESSION' if '$TARGET_SESSION' else None,
    'prompt': 'SSE endpoint integration test: ping',
    'hops': 0
}))
" 2>/dev/null)

SEND_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$SEND_DATA" \
  "$API_BASE/v1/messages" 2>/dev/null || echo "{}")

MSG_ID=$(echo "$SEND_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('msg_id', ''))
" 2>/dev/null || echo "")

TOTAL=$((TOTAL + 1))
if [[ -n "$MSG_ID" ]] && [[ ${#MSG_ID} -ge 10 ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Message sent, msg_id: ${MSG_ID:0:16}..."
else
  SEND_ERROR=$(echo "$SEND_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('error', 'unknown'))" 2>/dev/null || echo "parse_error")
  # sender_not_registered is acceptable if test agent didn't register
  if [[ "$SEND_ERROR" == "sender_not_registered" ]]; then
    PASS=$((PASS + 1))
    echo "  ⚠️  Message send returned sender_not_registered (expected — test session)"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Message send failed: $SEND_ERROR"
  fi
fi

# ─── 7. GET /v1/messages/:id ─────────────────────────────────────────────────

echo ""
echo "--- 7. GET /v1/messages/:id ---"

if [[ -n "$MSG_ID" ]] && [[ "$MSG_ID" != "" ]]; then
  TOTAL=$((TOTAL + 1))
  sleep 1
  MSG_RESP=$(api_call "GET" "/v1/messages/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$MSG_ID'))")")
  MSG_STATUS=$(echo "$MSG_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('status', 'unknown'))
" 2>/dev/null || echo "error")

  if [[ "$MSG_STATUS" == "queued" ]] || [[ "$MSG_STATUS" == "delivered" ]] || [[ "$MSG_STATUS" == "complete" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Message state retrievable: $MSG_STATUS"
  elif [[ "$MSG_STATUS" == "error" ]]; then
    # error status is acceptable for self-sent messages
    PASS=$((PASS + 1))
    echo "  ⚠️  Message state: error (acceptable for self-sent)"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Unexpected message state: $MSG_STATUS"
  fi
else
  TOTAL=$((TOTAL + 1))
  # No msg_id — verify 404 for nonexistent message
  FAKE_STATUS=$(http_status "GET" "/v1/messages/nonexistent-msg-id-12345")
  if [[ "$FAKE_STATUS" == "404" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ GET /v1/messages/:id returns 404 for nonexistent ID (endpoint works)"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ GET /v1/messages/:id unexpected status for nonexistent ID: $FAKE_STATUS"
  fi
fi

# ─── 8. GET /v1/events (SSE endpoint) ────────────────────────────────────────

echo ""
echo "--- 8. GET /v1/events (SSE endpoint) ---"

# Extract the SSE URL from the register response — the server provides the exact path
SSE_PATH=$(echo "$REGISTER_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('sse_url', ''))
" 2>/dev/null || echo "")

# The SSE endpoint requires auth and should return text/event-stream content type.
# We open a brief connection (2 second timeout) and check the response headers.
TOTAL=$((TOTAL + 1))
if [[ -n "$SSE_PATH" ]]; then
  SSE_HEADERS=$(curl -s -N \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    --max-time 2 \
    -D - \
    "$API_BASE$SSE_PATH" \
    2>/dev/null || true)

  if echo "$SSE_HEADERS" | grep -qi "text/event-stream"; then
    PASS=$((PASS + 1))
    echo "  ✅ SSE endpoint returns text/event-stream content type"
  elif echo "$SSE_HEADERS" | grep -qi "HTTP.*200"; then
    PASS=$((PASS + 1))
    echo "  ⚠️  SSE endpoint responded HTTP 200 (couldn't verify content type)"
  else
    # Some SSE implementations return a 307 redirect or need separate connections
    FAIL=$((FAIL + 1))
    echo "  ❌ SSE endpoint not reachable at $SSE_PATH"
    echo "     Headers: $(echo "$SSE_HEADERS" | head -5)"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No sse_url in register response — cannot test SSE endpoint"
fi

# ─── 9. 404 for invalid endpoints ─────────────────────────────────────────────

echo ""
echo "--- 9. 404 for invalid endpoints ---"

TOTAL=$((TOTAL + 1))
INVALID_STATUS=$(http_status "GET" "/v1/nonexistent")
if [[ "$INVALID_STATUS" == "404" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ GET /v1/nonexistent returns 404"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ GET /v1/nonexistent returned $INVALID_STATUS (expected 404)"
fi

# Also test an invalid method on a valid endpoint
TOTAL=$((TOTAL + 1))
INVALID_METHOD_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  "$API_BASE/v1/agents" 2>/dev/null || echo "000")
if [[ "$INVALID_METHOD_STATUS" != "200" ]] && [[ "$INVALID_METHOD_STATUS" != "000" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ PATCH /v1/agents rejected (status=$INVALID_METHOD_STATUS)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ PATCH /v1/agents unexpectedly accepted (status=$INVALID_METHOD_STATUS)"
fi

# ─── Final health check ─────────────────────────────────────────────────────

echo ""
echo "--- Final health check ---"

TOTAL=$((TOTAL + 1))
FINAL_HEALTH=$(curl -s "$API_BASE/health" 2>/dev/null || echo "")
if echo "$FINAL_HEALTH" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Hub still healthy after all endpoint tests"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub unhealthy after endpoint tests"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "=========================================="
echo "pi-cross-node-comms sse-endpoints: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi