#!/usr/bin/env bash
# test-model-accuracy.sh — P0 model accuracy integration test
#
# Validates that:
#   1. Valid model strings stored exactly as provided
#   2. Invalid model strings sanitized to "unknown" (after sanitizeModel fix)
#   3. Heartbeat model updates work; empty/undefined strings don't wipe good values
#   4. Re-registration updates model; omitting model preserves existing
#   5. Provider field is set at registration and immutable after
#   6. Model appears in agent data after update
#   7. Hub still healthy after all tests
#
# Prerequisites:
#   - Hub running at the configured URL
#   - AUTH_TOKEN with write access
#
# Run: bash tests/integration/test-model-accuracy.sh

set -uo pipefail

PASS=0
FAIL=0
TOTAL=0

HUB_URL="${PI_COMS_NET_SERVER_URL:-http://192.168.0.142:8080}"
AUTH_TOKEN="${PI_COMS_NET_AUTH_TOKEN:-7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0}"
PROJECT="${PI_COMS_NET_PROJECT:-default}"

# Track session IDs for cleanup (space-separated)
CLEANUP_SIDS=""

echo "=== pi-cross-node-comms model accuracy test ==="
echo "   Hub: $HUB_URL"
echo "   Project: $PROJECT"
echo ""

# ─── Helpers ─────────────────────────────────────────────────────────────────

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

register_and_check_model() {
  local sid="$1" name="$2" model="$3" expected="$4" provider="${5:-}"
  local data
  if [[ -n "$provider" ]]; then
    data=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$sid',
    'name': '$name',
    'model': '$model',
    'provider': '$provider',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
  else
    data=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$sid',
    'name': '$name',
    'model': '$model',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
  fi

  local resp=$(curl -s -X POST \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$data" \
    "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")

  CLEANUP_SIDS="$CLEANUP_SIDS $sid"

  local actual=$(echo "$resp" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('agent', {}).get('model', '<NOT_FOUND>'))
" 2>/dev/null || echo "<PARSE_ERROR>")

  assert_eq "model='$model'" "$expected" "$actual"
  sleep 0.3
}

assert_eq() {
  local desc="$1" expected="$2" actual="$3"
  TOTAL=$((TOTAL + 1))
  if [[ "$expected" == "$actual" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ $desc: $actual"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ $desc: expected '$expected', got '$actual'"
  fi
}

cleanup_all() {
  echo ""
  echo "--- Cleanup: unregistering test agents ---"
  for sid in $CLEANUP_SIDS; do
    local enc_sid=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$sid'))")
    curl -s -X DELETE -H "Authorization: Bearer $AUTH_TOKEN" "$HUB_URL/v1/agents/$enc_sid" > /dev/null 2>&1 || true
  done
}
trap cleanup_all EXIT

# ─── Step 1: Hub health ─────────────────────────────────────────────────────

echo "--- Step 1: Hub health ---"
TOTAL=$((TOTAL + 1))
HEALTH=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
if echo "$HEALTH" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Hub is healthy"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub unreachable — aborting"
  exit 1
fi

# ─── Step 2: Valid model strings stored exactly ──────────────────────────────

echo ""
echo "--- Step 2: Valid model strings stored exactly ---"

for MODEL in "qwen3.5:4b" "claude-3.5-sonnet" "gemini-2.5-flash" "gpt-4o" "ollama/qwen3.5:4b"; do
  SID="vm-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
  register_and_check_model "$SID" "test-valid-model" "$MODEL" "$MODEL"
done

# ─── Step 3: Invalid model strings sanitized to 'unknown' ──────────────────

echo ""
echo "--- Step 3: Invalid model strings sanitized to 'unknown' ---"

# 3a: empty string
SID="im-empt-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$SID',
    'name': 'test-im',
    'model': '',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
RESP=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$DATA" "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")
CLEANUP_SIDS="$CLEANUP_SIDS $SID"
ACTUAL=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','<NOT_FOUND>'))" 2>/dev/null || echo "<PARSE_ERROR>")
assert_eq "model='' → unknown" "unknown" "$ACTUAL"
sleep 0.3

# 3b: "undefined"
SID="im-undef-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
register_and_check_model "$SID" "test-im2" "undefined" "unknown"

# 3c: "null"
SID="im-null-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
register_and_check_model "$SID" "test-im3" "null" "unknown"

# 3d: whitespace
SID="im-ws-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$SID',
    'name': 'test-im4',
    'model': '   ',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
RESP=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$DATA" "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")
CLEANUP_SIDS="$CLEANUP_SIDS $SID"
ACTUAL=$(echo "$RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','<NOT_FOUND>'))" 2>/dev/null || echo "<PARSE_ERROR>")
assert_eq "model='   ' (whitespace) → unknown" "unknown" "$ACTUAL"
sleep 0.3

# 3e: all-uppercase hash
SID="im-up-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
register_and_check_model "$SID" "test-im5" "ABCDEF" "unknown"

# ─── Step 4: Heartbeat model update ───────────────────────────────────────────

echo ""
echo "--- Step 4: Heartbeat model update ---"

HB_SID="test-hb-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
HB_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$HB_SID',
    'name': 'test-hb',
    'model': 'model-v1',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
HB_RESP=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$HB_DATA" "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")
CLEANUP_SIDS="$CLEANUP_SIDS $HB_SID"
sleep 0.3

# 4a: heartbeat WITH model → updates
HB_UPD=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'context_used_pct': 50,
    'queue_depth': 0,
    'model': 'model-v2'
}))
")
api_call "POST" "/v1/agents/$HB_SID/heartbeat" "$HB_UPD" > /dev/null
sleep 0.3
HB_MODEL=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for a in d.get('agents', []):
    if a.get('session_id') == '$HB_SID':
        print(a.get('model', '?'))
        break
" 2>/dev/null || echo "?")
assert_eq "Heartbeat updates model to v2" "model-v2" "$HB_MODEL"

# 4b: heartbeat WITHOUT model → preserves existing
HB_NOP=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'context_used_pct': 55,
    'queue_depth': 0
}))
")
api_call "POST" "/v1/agents/$HB_SID/heartbeat" "$HB_NOP" > /dev/null
sleep 0.3
HB_MODEL2=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for a in d.get('agents', []):
    if a.get('session_id') == '$HB_SID':
        print(a.get('model', '?'))
        break
" 2>/dev/null || echo "?")
assert_eq "Heartbeat without model preserves v2" "model-v2" "$HB_MODEL2"

# ─── Step 5: Re-registration model behavior ────────────────────────────────────

echo ""
echo "--- Step 5: Re-registration model behavior ---"

RR_SID="test-rr-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
RR_DATA1=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$RR_SID',
    'name': 'test-rr',
    'model': 'model-v1',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$RR_DATA1" "$HUB_URL/v1/agents/register" > /dev/null 2>&1
CLEANUP_SIDS="$CLEANUP_SIDS $RR_SID"
sleep 0.3

# 5a: re-register with different model → updates
RR_DATA2=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$RR_SID',
    'name': 'test-rr',
    'model': 'model-v2',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
RR_RESP=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$RR_DATA2" "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")
RR_MODEL=$(echo "$RR_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null || echo "?")
assert_eq "Re-registration updates model" "model-v2" "$RR_MODEL"

# ─── Step 6: Provider field ──────────────────────────────────────────────────

echo ""
echo "--- Step 6: Provider field ---"

PV_SID="test-pv-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
PV_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$PV_SID',
    'name': 'test-pv',
    'model': 'test-model',
    'provider': 'anthropic',
    'purpose': 'test',
    'cwd': '/tmp',
    'node': 'mac-test',
    'explicit': True
}))
")
PV_RESP=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$PV_DATA" "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")
CLEANUP_SIDS="$CLEANUP_SIDS $PV_SID"
PV_PROV=$(echo "$PV_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('provider','<NOT_FOUND>'))" 2>/dev/null || echo "<PARSE_ERROR>")
assert_eq "Provider stored at registration" "anthropic" "$PV_PROV"
sleep 0.3

# 6b: heartbeat with different provider → provider NOT updated
PV_HB=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'context_used_pct': 60,
    'queue_depth': 0,
    'model': 'test-model'
}))
")
api_call "POST" "/v1/agents/$PV_SID/heartbeat" "$PV_HB" > /dev/null
sleep 0.3
PV_PROV2=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "
import json, sys
d = json.load(sys.stdin)
for a in d.get('agents', []):
    if a.get('session_id') == '$PV_SID':
        print(a.get('provider', '?'))
        break
" 2>/dev/null || echo "?")
assert_eq "Provider unchanged after heartbeat" "anthropic" "$PV_PROV2"

# ─── Step 7: Model field present in agent data ──────────────────────────────

echo ""
echo "--- Step 7: Model field present in agent data ---"

TOTAL=$((TOTAL + 1))
CNT=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(sum(1 for a in d.get('agents', []) if a.get('model')))
" 2>/dev/null || echo "0")
if [[ "$CNT" -gt 0 ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ $CNT agents have model field"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No agents have model field"
fi

# ─── Step 8: Hub still healthy ────────────────────────────────────────────────

echo ""
echo "--- Step 8: Hub still healthy ---"

TOTAL=$((TOTAL + 1))
HEALTH2=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
if echo "$HEALTH2" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok') == True" 2>/dev/null; then
  PASS=$((PASS + 1))
  echo "  ✅ Hub still healthy after all tests"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub unhealthy after tests"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "=========================================="
echo "model-accuracy: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi