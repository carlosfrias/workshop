#!/usr/bin/env bash
# test-reply-guard.sh — Validate that the extension's critical safety guards
# exist in the source code. These guards prevent ping-pong loops and message
# misuse. If any are removed accidentally, these tests will catch it.
#
# Run: bash tests/unit/test-reply-guard.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXT_FILE="$REPO_ROOT/src/index.ts"

PASS=0
FAIL=0
TOTAL=0

assert_contains() {
  local file="$1" pattern="$2" label="${3:-}"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$file" ]]; then
    FAIL=$((FAIL + 1))
    echo "  ❌ $label — file missing: $file"
    return
  fi
  if grep -q "$pattern" "$file"; then
    PASS=$((PASS + 1))
    echo "  ✅ $label"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ $label — pattern not found: $pattern"
  fi
}

echo "=== pi-cross-node-comms reply guard validation ==="
echo ""

# ─── 1. coms_net_send description ─────────────────────────────────────────

echo "--- coms_net_send tool description ---"

assert_contains "$EXT_FILE" \
  "DO NOT call this tool to REPLY to an inbound message" \
  "coms_net_send warns against replying to inbound messages"

assert_contains "$EXT_FILE" \
  "ping-pong loop" \
  "coms_net_send mentions ping-pong loop"

# ─── 2. coms_net_get description ─────────────────────────────────────────

echo ""
echo "--- coms_net_get tool description ---"

assert_contains "$EXT_FILE" \
  "only use msg_ids you got back from coms_net_send" \
  "coms_net_get restricts msg_id ownership to outbound"

# ─── 3. coms_net_await description ────────────────────────────────────────

echo ""
echo "--- coms_net_await tool description ---"

assert_contains "$EXT_FILE" \
  "Do NOT call this with a msg_id that came in via an inbound" \
  "coms_net_await warns against using inbound msg_ids"

assert_contains "$EXT_FILE" \
  "auto-submit" \
  "coms_net_await mentions auto-submit behavior"

# ─── 4. Inbound relay warning ────────────────────────────────────────────

echo ""
echo "--- Inbound message relay ---"

assert_contains "$EXT_FILE" \
  "DO NOT call coms_net_send/coms_net_await/coms_net_get to reply" \
  "Inbound relay injects reply guard warning"

# ─── 5. Inbound context tracking ──────────────────────────────────────────

echo ""
echo "--- Inbound context tracking ---"

assert_contains "$EXT_FILE" \
  "currentInbound =" \
  "currentInbound is assigned when processing inbound messages"

# ─── 6. Pending replies map ──────────────────────────────────────────────

echo ""
echo "--- Outbound message tracking ---"

assert_contains "$EXT_FILE" \
  "pendingReplies" \
  "pendingReplies Map exists for tracking outbound responses"

# ─── Summary ──────────────────────────────────────────────────────────────

echo ""
echo "=========================================="
echo "pi-cross-node-comms reply-guard: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi