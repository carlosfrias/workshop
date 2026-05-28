#!/usr/bin/env bash
set -uo pipefail

PASS=0
FAIL=0
TOTAL=0

HUB_URL="${PI_COMS_NET_SERVER_URL:-http://192.168.0.142:8080}"
AUTH_TOKEN="${PI_COMS_NET_AUTH_TOKEN:-7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0}"
PROJECT="${PI_COMS_NET_PROJECT:-default}"
CLEANUP_SIDS=""
ADD_SID() { CLEANUP_SIDS="$CLEANUP_SIDS $1"; }

echo "=== pi-cross-node-comms model accuracy test ==="
echo "   Hub: $HUB_URL   Project: $PROJECT"
echo ""

api_call() {
  local method="$1" endpoint="$2" data="${3:-}"
  if [[ -n "$data" ]]; then
    curl -s -X "$method" -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" -d "$data" "$HUB_URL$endpoint" 2>/dev/null
  else
    curl -s -X "$method" -H "Authorization: Bearer $AUTH_TOKEN" "$HUB_URL$endpoint" 2>/dev/null
  fi
}

unregister() { curl -s -X DELETE -H "Authorization: Bearer $AUTH_TOKEN" "$HUB_URL/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$1'))")" > /dev/null 2>&1 || true; }
cleanup_all() { for sid in $CLEANUP_SIDS; do unregister "$sid"; done; echo "Cleaned up."; }
trap cleanup_all EXIT

assert_eq() { local desc="$1" expected="$2" actual="$3"; TOTAL=$((TOTAL+1)); if [[ "$expected" == "$actual" ]]; then PASS=$((PASS+1)); echo "  ✅ $desc: $actual"; else FAIL=$((FAIL+1)); echo "  ❌ $desc: expected '$expected', got '$actual'"; fi; }

# Step 1: Health
echo "--- Step 1: Hub health ---"
TOTAL=$((TOTAL+1)); H=$(curl -s "$HUB_URL/health" 2>/dev/null||"")
if echo "$H" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok')" 2>/dev/null; then PASS=$((PASS+1)); echo "  ✅ Hub healthy"; else FAIL=$((FAIL+1)); echo "  ❌ Hub unreachable"; exit 1; fi

# Step 2: Valid models
echo ""; echo "--- Step 2: Valid model strings stored exactly ---"
for M in "qwen3.5:4b" "claude-3.5-sonnet" "gemini-2.5-flash" "gpt-4o" "ollama/qwen3.5:4b"; do
  SID="vm-$$-$(python3 -c 'import random,uuid; print(uuid.uuid4().hex[:12])')"
  R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
    -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-vm','model':'$M','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
    "$HUB_URL/v1/agents/register")
  RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
  assert_eq "model='$M'" "$M" "$RM"
  ADD_SID "$SID"; sleep 0.2
done

# Step 3: Invalid models → "unknown"
echo ""; echo "--- Step 3: Invalid model strings sanitized to 'unknown' ---"

# 3a: empty string
SID="im-empt-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-im','model':'','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "model='' → unknown" "unknown" "$RM"
ADD_SID "$SID"; sleep 0.2

# 3b: "undefined"
SID="im-undef-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-im2','model':'undefined','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "model='undefined' → unknown" "unknown" "$RM"
ADD_SID "$SID"; sleep 0.2

# 3c: "null"
SID="im-null-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-im3','model':'null','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "model='null' → unknown" "unknown" "$RM"
ADD_SID "$SID"; sleep 0.2

# 3d: whitespace
SID="im-ws-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-im4','model':'   ','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "model='   ' (whitespace) → unknown" "unknown" "$RM"
ADD_SID "$SID"; sleep 0.2

# 3e: all-uppercase hash
SID="im-up-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-im5','model':'ABCDEF','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "model='ABCDEF' → unknown" "unknown" "$RM"
ADD_SID "$SID"; sleep 0.2

# Step 4: Heartbeat model update
echo ""; echo "--- Step 4: Heartbeat model update ---"
SID="hb-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-hb','model':'model-v1','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
ADD_SID "$SID"; sleep 0.2

# 4a: heartbeat WITH model
api_call "POST" "/v1/agents/$SID/heartbeat" "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','context_used_pct':50,'queue_depth':0,'model':'model-v2'}))")" > /dev/null
sleep 0.3
M=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "import json,sys; [print(a.get('model','?')) for a in json.load(sys.stdin).get('agents',[]) if a.get('session_id')=='$SID']" 2>/dev/null||echo "?")
assert_eq "Heartbeat updates model to v2" "model-v2" "$M"

# 4b: heartbeat WITHOUT model → preserves
api_call "POST" "/v1/agents/$SID/heartbeat" "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','context_used_pct':55,'queue_depth':0}))")" > /dev/null
sleep 0.3
M2=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "import json,sys; [print(a.get('model','?')) for a in json.load(sys.stdin).get('agents',[]) if a.get('session_id')=='$SID']" 2>/dev/null||echo "?")
assert_eq "Heartbeat without model preserves v2" "model-v2" "$M2"

# Step 5: Re-registration
echo ""; echo "--- Step 5: Re-registration model behavior ---"
SID="rr-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-rr','model':'model-v1','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
ADD_SID "$SID"; sleep 0.2

# 5a: re-register with different model
R2=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-rr','model':'model-v2','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
RM=$(echo "$R2" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('model','?'))" 2>/dev/null||echo "?")
assert_eq "Re-registration updates model" "model-v2" "$RM"

# Step 6: Provider field
echo ""; echo "--- Step 6: Provider field ---"
SID="pv-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
R=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" -H "Content-Type: application/json" \
  -d "$(python3 -c "import json; print(json.dumps({'project':'$PROJECT','session_id':'$SID','name':'t-pv','model':'test-model','provider':'anthropic','purpose':'test','cwd':'/tmp','node':'mac-test','explicit':True}))")" \
  "$HUB_URL/v1/agents/register")
PV=$(echo "$R" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('provider','<NOT_FOUND>'))" 2>/dev/null||echo "?")
assert_eq "Provider stored at registration" "anthropic" "$PV"
ADD_SID "$SID"; sleep 0.2

# Step 7: Model in agent data
echo ""; echo "--- Step 7: Model field present in agent data ---"
TOTAL=$((TOTAL+1))
CNT=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(1 for a in d.get('agents',[]) if a.get('model')))" 2>/dev/null||echo "0")
if [[ "$CNT" -gt 0 ]]; then PASS=$((PASS+1)); echo "  ✅ $CNT agents have model field"; else FAIL=$((FAIL+1)); echo "  ❌ No agents have model field"; fi

# Step 8: Health
echo ""; echo "--- Step 8: Hub still healthy ---"
TOTAL=$((TOTAL+1)); H2=$(curl -s "$HUB_URL/health" 2>/dev/null||"")
if echo "$H2" | python3 -c "import json,sys; assert json.load(sys.stdin).get('ok')" 2>/dev/null; then PASS=$((PASS+1)); echo "  ✅ Hub still healthy"; else FAIL=$((FAIL+1)); echo "  ❌ Hub unhealthy"; fi

echo ""; echo "=========================================="
echo "model-accuracy: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
[[ "$FAIL" -gt 0 ]] && echo "RESULT: FAIL" && exit 1 || echo "RESULT: PASS" && exit 0
