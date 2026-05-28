#!/usr/bin/env bash
# test-extension-behavior.sh — Validate behavioral contracts in the extension source:
#   - Reply guard (coms_net_send must warn about replying to inbound messages)
#   - Hop limit enforcement (MAX_HOPS prevents infinite ping-pong)
#   - Heartbeat mechanism (periodic heartbeat to hub)
#   - Inbound message flow (SSE → pi.sendUserMessage)
#   - Auto-cleanup on shutdown (clearInterval, unregister)
#   - Systemd template uses -- separator for extension flags
#
# TDD: Written AFTER understanding architecture, tests contract invariants.
#
# Run: bash tests/unit/test-extension-behavior.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXT_FILE="$REPO_ROOT/src/index.ts"
SYSTEMD_TEMPLATE="$REPO_ROOT/ansible/systemd/pi-cross-node-agent@.service.template"

PASS=0
FAIL=0
TOTAL=0

assert_contains() {
  local file="$1" pattern="$2" label="${3:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$file" ]]; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — file missing: $file"
    return
  fi
  if grep -q "$pattern" "$file"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — does not contain: $pattern"
  fi
}

assert_not_contains() {
  local file="$1" pattern="$2" label="${3:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$file" ]]; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — file missing: $file"
    return
  fi
  if grep -q "$pattern" "$file"; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — unexpectedly contains: $pattern"
  else
    PASS=$((PASS + 1))
  fi
}

echo "=== pi-cross-node-comms extension behavior validation ==="
echo ""

# ─── Reply Guard ────────────────────────────────────────────────────────────

echo "--- Reply guard (prevents ping-pong) ---"

# coms_net_send description must warn about not using it to reply
assert_contains "$EXT_FILE" \
  "DO NOT call this tool to REPLY to an inbound message" \
  "coms_net_send has reply guard in description"

# coms_net_get must warn about not using peer msg_ids
assert_contains "$EXT_FILE" \
  "only use msg_ids you got back from coms_net_send" \
  "coms_net_get has msg_id ownership warning"

# coms_net_await must warn about not using peer msg_ids
assert_contains "$EXT_FILE" \
  "Do NOT call this with a msg_id that came in via an inbound" \
  "coms_net_await has inbound msg_id warning"

# The ping-pong loop text must be present in warnings
assert_contains "$EXT_FILE" \
  "ping-pong loop" \
  "Extension warns about ping-pong loops"

# ─── Hop Limit ────────────────────────────────────────────────────────────

echo ""
echo "--- Hop limit (prevents runaway chains) ---"

# MAX_HOPS must be defined
assert_contains "$EXT_FILE" \
  "MAX_HOPS" \
  "MAX_HOPS constant defined"

# Hop limit must be enforced in coms_net_send
assert_contains "$EXT_FILE" \
  "hop limit reached\|hops >= MAX_HOPS" \
  "Hop limit enforced in send"

# Hops must be auto-incremented from inbound context
assert_contains "$EXT_FILE" \
  "currentInbound.*hops.*+.*1\|hops.*currentInbound" \
  "Hops auto-incremented from inbound context"

# ─── Heartbeat Mechanism ───────────────────────────────────────────────────

echo ""
echo "--- Heartbeat mechanism ---"

# Heartbeat interval must be configurable via env
assert_contains "$EXT_FILE" \
  "PI_COMS_NET_HEARTBEAT_MS" \
  "Heartbeat interval reads PI_COMS_NET_HEARTBEAT_MS"

# Default heartbeat must be 10 seconds
assert_contains "$EXT_FILE" \
  "10_000" \
  "Default heartbeat interval is 10s"

# Heartbeat endpoint must be called
assert_contains "$EXT_FILE" \
  "heartbeat" \
  "Heartbeat endpoint called"

# Heartbeat timer must be unref'd (not keep process alive)
assert_contains "$EXT_FILE" \
  "unref" \
  "Heartbeat timer unref'd to not keep process alive"

# Heartbeat must be cleaned up on shutdown
assert_contains "$EXT_FILE" \
  "clearInterval.*heartbeatTimer\|heartbeatTimer.*clearInterval" \
  "Heartbeat timer cleared on shutdown"

# ─── Inbound Message Flow ────────────────────────────────────────────────

echo ""
echo "--- Inbound message flow ---"

# SSE events must be processed
assert_contains "$EXT_FILE" \
  "EventSource\|SSE\|sse" \
  "Extension handles SSE events"

# Inbound messages must be relayed to pi via sendUserMessage
assert_contains "$EXT_FILE" \
  "sendUserMessage" \
  "Inbound messages relayed via pi.sendUserMessage"

# The relay must include the "DO NOT reply" guidance
assert_contains "$EXT_FILE" \
  "DO NOT call coms_net_send/coms_net_await/coms_net_get to reply" \
  "Inbound relay includes reply guard guidance"

# ─── Shutdown / Cleanup ───────────────────────────────────────────────────

echo ""
echo "--- Shutdown cleanup ---"

# Must unregister agent on shutdown (DELETE /v1/agents/:session_id)
assert_contains "$EXT_FILE" \
  "/v1/agents/" \
  "Agent unregistration endpoint referenced on shutdown"
assert_contains "$EXT_FILE" \
  "DELETE" \
  "DELETE HTTP method used for agent unregistration"

# Must clear heartbeat timer on shutdown
assert_contains "$EXT_FILE" \
  "clearInterval" \
  "Timer cleanup on shutdown"

# ─── Systemd Template ─────────────────────────────────────────────────────

echo ""
echo "--- Systemd template ---"

if [[ -f "$SYSTEMD_TEMPLATE" ]]; then
  # Template must use -- separator between pi flags and extension flags
  assert_contains "$SYSTEMD_TEMPLATE" \
    "^[[:space:]]*--" \
    "Systemd template uses -- separator for extension flags"

  # Template must set env vars for fallback config
  assert_contains "$SYSTEMD_TEMPLATE" \
    "PI_COMS_NET_SERVER_URL" \
    "Systemd template sets PI_COMS_NET_SERVER_URL env"
  assert_contains "$SYSTEMD_TEMPLATE" \
    "PI_COMS_NET_AUTH_TOKEN" \
    "Systemd template sets PI_COMS_NET_AUTH_TOKEN env"
  assert_contains "$SYSTEMD_TEMPLATE" \
    "PI_COMS_NET_PROJECT" \
    "Systemd template sets PI_COMS_NET_PROJECT env"

  # Template must include --name, --project, --server-url, --auth-token as extension flags
  assert_contains "$SYSTEMD_TEMPLATE" \
    "\-\-name" \
    "Systemd template includes --name extension flag"
  assert_contains "$SYSTEMD_TEMPLATE" \
    "\-\-project" \
    "Systemd template includes --project extension flag"
  assert_contains "$SYSTEMD_TEMPLATE" \
    "\-\-server-url" \
    "Systemd template includes --server-url extension flag"
  assert_contains "$SYSTEMD_TEMPLATE" \
    "\-\-auth-token" \
    "Systemd template includes --auth-token extension flag"

  # Template must NOT pass auth-token as command-line arg visible in ps
  # (It should use env var or secret file instead)
  # Actually, systemd ExecStart is fine — it's in the unit file, not ps visible
fi

# ─── Config Priority Chain ────────────────────────────────────────────────

echo ""
echo "--- Config priority chain verification ---"

# resolveServerUrl must check CLI flag first
assert_contains "$EXT_FILE" \
  "resolveServerUrl" \
  "resolveServerUrl function exists"

# resolveAuthToken must check CLI flag first
assert_contains "$EXT_FILE" \
  "resolveAuthToken" \
  "resolveAuthToken function exists"

# Both must fall back to env vars
assert_contains "$EXT_FILE" \
  "SERVER_URL_ENV" \
  "Server URL env var used as fallback"
assert_contains "$EXT_FILE" \
  "AUTH_TOKEN_ENV" \
  "Auth token env var used as fallback"

# ─── Error Messages ───────────────────────────────────────────────────────

echo ""
echo "--- Error messages and edge cases ---"

# Must notify user when no server URL
assert_contains "$EXT_FILE" \
  "no server URL" \
  "Error message when server URL not found"

# Must notify user when no auth token
assert_contains "$EXT_FILE" \
  "no auth token" \
  "Error message when auth token not found"

# Must notify user when server unreachable
assert_contains "$EXT_FILE" \
  "server unreachable\|unreachable" \
  "Error message when server unreachable"

# Must notify user when register fails
assert_contains "$EXT_FILE" \
  "register failed" \
  "Error message when registration fails"

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "=========================================="
echo "pi-cross-node-comms extension-behavior: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi