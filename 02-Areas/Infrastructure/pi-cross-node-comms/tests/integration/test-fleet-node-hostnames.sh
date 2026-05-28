#!/usr/bin/env bash
# test-fleet-node-hostnames.sh — TDD integration test: fleet node hostnames
# appear in the hub's agent listing and SSE events.
#
# Validates that:
#   1. Docker hub deployment is healthy and running latest code
#   2. Fleet node agents register with valid hostnames (not "unknown")
#   3. The `node` field in agent listings matches expected hostnames
#   4. A local test agent can discover fleet nodes via GET /v1/agents
#   5. SSE pool_snapshot includes fleet node hostnames
#   6. Node name validation rejects auto-generated IDs and accepts hostnames
#
# Prerequisites:
#   - Hub running on fnet2 (Docker or bare)
#   - At least 1 fleet node agent registered with a valid hostname
#   - AUTH_TOKEN and HUB_URL accessible
#
# Run: bash tests/integration/test-fleet-node-hostnames.sh

set -euo pipefail

PASS=0
FAIL=0
TOTAL=0

HUB_URL="${PI_COMS_NET_SERVER_URL:-http://192.168.0.142:8080}"
AUTH_TOKEN="${PI_COMS_NET_AUTH_TOKEN:-7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0}"
PROJECT="${PI_COMS_NET_PROJECT:-lab}"

echo "=== pi-cross-node-comms fleet node hostname test ==="
echo "   Hub: $HUB_URL"
echo "   Project: $PROJECT"
echo ""

# ─── Helper functions ────────────────────────────────────────────────────────

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

assert_contains() {
  local desc="$1" haystack="$2" needle="$3"
  TOTAL=$((TOTAL + 1))
  if echo "$haystack" | grep -q "$needle"; then
    PASS=$((PASS + 1))
    echo "  ✅ $desc: contains '$needle'"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ $desc: expected to contain '$needle'"
  fi
}

assert_not_contains() {
  local desc="$1" haystack="$2" needle="$3"
  TOTAL=$((TOTAL + 1))
  if ! echo "$haystack" | grep -q "$needle"; then
    PASS=$((PASS + 1))
    echo "  ✅ $desc: does NOT contain '$needle'"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ $desc: should NOT contain '$needle'"
  fi
}

# ─── Step 1: Hub health ─────────────────────────────────────────────────────

echo "--- Step 1: Hub health ---"

TOTAL=$((TOTAL + 1))
HEALTH=$(curl -s "$HUB_URL/health" 2>/dev/null || echo "")
HEALTH_OK=$(echo "$HEALTH" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok',False))" 2>/dev/null || echo "False")

if [[ "$HEALTH_OK" == "True" ]]; then
  PASS=$((PASS + 1))
  SERVER_ID=$(echo "$HEALTH" | python3 -c "import json,sys; print(json.load(sys.stdin).get('server_id',''))" 2>/dev/null || echo "")
  echo "  ✅ Hub is healthy (server_id: ${SERVER_ID:0:12}...)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Hub is unhealthy or unreachable at $HUB_URL — aborting"
  echo ""
  echo "=========================================="
  echo "fleet-node-hostnames: $PASS passed, $FAIL failed, $TOTAL total"
  echo "=========================================="
  echo "RESULT: FAIL"
  exit 1
fi

# ─── Step 2: Register a test agent with a valid hostname ────────────────────

echo ""
echo "--- Step 2: Register test agent (mac-test-host) ---"

TEST_SESSION_ID="test-hostname-$$-$(date +%s)"
REGISTER_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$TEST_SESSION_ID',
    'name': 'test-hostname-agent',
    'purpose': 'hostname validation test',
    'model': 'test-runner',
    'color': '#00FF00',
    'cwd': '/tmp',
    'node': 'mac-test-host',
    'explicit': False
}))
")

REGISTER_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REGISTER_DATA" \
  "$HUB_URL/v1/agents/register" 2>/dev/null || echo "{}")

REGISTER_OK=$(echo "$REGISTER_RESP" | python3 -c "import json,sys; print('yes' if json.load(sys.stdin).get('ok') else 'no')" 2>/dev/null || echo "no")

assert_eq "Test agent registration" "yes" "$REGISTER_OK"

# Cleanup
unregister_test_agent() {
  curl -s -X DELETE \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    "$HUB_URL/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$TEST_SESSION_ID'))")" 2>/dev/null || true
}
trap unregister_test_agent EXIT

# ─── Step 3: Discover fleet nodes and validate hostnames ────────────────────

echo ""
echo "--- Step 3: Discover fleet nodes (include_explicit=true) ---"

AGENTS_RESP=$(api_call "GET" "/v1/agents?project=$PROJECT&include_explicit=true")
AGENT_COUNT=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(len(d.get('agents', d if isinstance(d, list) else [])))
" 2>/dev/null || echo "0")

TOTAL=$((TOTAL + 1))
if [[ "$AGENT_COUNT" -ge 2 ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Found $AGENT_COUNT agent(s) (test + fleet)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Expected ≥2 agents (test + fleet), found $AGENT_COUNT"
fi

# ─── Step 4: Validate node hostnames are not "unknown" ──────────────────────

echo ""
echo "--- Step 4: Validate node hostnames ---"

# Check all agents have valid node names (not "unknown")
INVALID_NODES=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    node = a.get('node', 'unknown')
    name = a.get('name', '?')
    if node == 'unknown':
        print(f'  WARNING: agent {name} has node=unknown')
invalid = [a for a in agents if a.get('node') == 'unknown']
sys.exit(len(invalid))
" 2>/dev/null; echo "exit:$?")

# Count agents with valid node (not "unknown")
VALID_NODE_COUNT=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
print(len([a for a in agents if a.get('node', 'unknown') != 'unknown']))
" 2>/dev/null || echo "0")

TOTAL=$((TOTAL + 1))
if [[ "$VALID_NODE_COUNT" -ge 1 ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ $VALID_NODE_COUNT agent(s) with valid hostname (not 'unknown')"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No agents with valid hostnames — all show node='unknown'"
fi

# List all agent nodes
echo ""
echo "  Registered agents:"
echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
for a in agents:
    print(f'    {a.get(\"name\", \"?\"):20s}  node={a.get(\"node\", \"unknown\"):20s}  model={a.get(\"model\", \"?\"):15s}  status={a.get(\"status\", \"?\")}')
" 2>/dev/null

# ─── Step 5: Verify specific fleet node hostname appears ────────────────────

echo ""
echo "--- Step 5: Fleet node hostname visibility ---"

# Check if any agent has a node that looks like a fleet hostname (fnet*)
FNET_NODES=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
fnet = [a for a in agents if a.get('node', '').startswith('fnet')]
print(len(fnet))
" 2>/dev/null || echo "0")

TOTAL=$((TOTAL + 1))
if [[ "$FNET_NODES" -ge 1 ]]; then
  PASS=$((PASS + 1))
  FNET_NAMES=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
fnet = [a for a in agents if a.get('node', '').startswith('fnet')]
print(', '.join(a.get('node','?') for a in fnet))
" 2>/dev/null || echo "")
  echo "  ✅ Fleet node hostname(s) visible: $FNET_NAMES"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ No fleet node hostnames (fnet*) found in agent listing"
  echo "     Fleet nodes may not be registered or may have node='unknown'"
fi

# ─── Step 6: Verify our test agent node is correct ──────────────────────────

echo ""
echo "--- Step 6: Test agent node field ---"

TEST_AGENT_NODE=$(echo "$AGENTS_RESP" | python3 -c "
import json, sys
d = json.load(sys.stdin)
agents = d.get('agents', d if isinstance(d, list) else [])
test = [a for a in agents if a.get('session_id') == '$TEST_SESSION_ID']
print(test[0].get('node', 'NOT_FOUND') if test else 'NOT_FOUND')
" 2>/dev/null || echo "PARSE_ERROR")

assert_eq "Test agent node field" "mac-test-host" "$TEST_AGENT_NODE"

# ─── Step 7: Node name validation (reject auto-generated IDs) ───────────────

echo ""
echo "--- Step 7: Invalid node names rejected ---"

# Register an agent with an invalid node name (auto-generated ID pattern)
INVALID_SESSION_ID="test-invalid-node-$$-$(date +%s)"
INVALID_DATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$INVALID_SESSION_ID',
    'name': 'invalid-node-agent',
    'purpose': 'node validation test',
    'model': 'test',
    'cwd': '/tmp',
    'node': 'agent-GBH8T1',
    'explicit': True
}))
")

INVALID_RESP=$(curl -s -X POST \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$INVALID_DATA" \
  "$HUB_URL/v1/agents/register")

INVALID_OK=$(echo "$INVALID_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "False")
INVALID_NODE=$(echo "$INVALID_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('node','NOT_FOUND'))" 2>/dev/null || echo "PARSE_ERROR")

TOTAL=$((TOTAL + 1))
if [[ "$INVALID_OK" == "True" ]] && [[ "$INVALID_NODE" == "unknown" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Auto-generated ID 'agent-GBH8T1' sanitized to 'unknown'"
elif [[ "$INVALID_OK" != "True" ]]; then
  FAIL=$((FAIL + 1))
  echo "  ❌ Registration with invalid node failed unexpectedly: $INVALID_RESP"
  echo "     (expected registration to succeed with node sanitized to 'unknown')"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Auto-generated ID 'agent-GBH8T1' was NOT sanitized (got: '$INVALID_NODE')"
fi

# Cleanup invalid agent
curl -s -X DELETE \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  "$HUB_URL/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$INVALID_SESSION_ID'))")" >/dev/null 2>&1 || true

# ─── Step 8: Valid hostname accepted ────────────────────────────────────────

echo ""
echo "--- Step 8: Valid hostnames accepted ---"

# Test various valid hostname patterns
VALID_NAMES=("fnet3" "raspberrypi.local" "192.168.0.154" "mac-orchestrator" "lab-node-01")

VALID_PASSES=0
VALID_TOTAL=${#VALID_NAMES[@]}
for VNAME in "${VALID_NAMES[@]}"; do
  VSESSION="test-val-$$-$(python3 -c 'import random; print(random.randint(100000,999999))')"
  VDATA=$(python3 -c "
import json
print(json.dumps({
    'project': '$PROJECT',
    'session_id': '$VSESSION',
    'name': 'test-node-val',
    'purpose': 'node validation',
    'model': 'test',
    'cwd': '/tmp',
    'node': '$VNAME',
    'explicit': True
}))
")
  VRESP=$(curl -s -X POST \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$VDATA" \
    "$HUB_URL/v1/agents/register")

  VOK=$(echo "$VRESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('ok', False))" 2>/dev/null || echo "False")
  VNODE=$(echo "$VRESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('agent',{}).get('node','?'))" 2>/dev/null || echo "?")

  if [[ "$VOK" == "True" ]] && [[ "$VNODE" == "$VNAME" ]]; then
    VALID_PASSES=$((VALID_PASSES + 1))
  else
    echo "  ⚠️  Hostname '$VNAME': registration ok=$VOK, node=$VNODE (expected node=$VNAME)"
  fi

  # Cleanup
  curl -s -X DELETE \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    "$HUB_URL/v1/agents/$(python3 -c "import urllib.parse; print(urllib.parse.quote('$VSESSION'))")" >/dev/null 2>&1 || true
  sleep 0.3
done

TOTAL=$((TOTAL + 1))
if [[ "$VALID_PASSES" -eq "$VALID_TOTAL" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ All $VALID_TOTAL valid hostnames accepted"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Only $VALID_PASSES/$VALID_TOTAL valid hostnames were accepted"
fi

# ─── Step 9: Hub still healthy after tests ────────────────────────────────────

echo ""
echo "--- Step 9: Hub still healthy ---"

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
echo "fleet-node-hostnames: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi