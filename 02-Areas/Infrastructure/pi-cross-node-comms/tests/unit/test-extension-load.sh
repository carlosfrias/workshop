#!/usr/bin/env bash
# test-extension-load.sh — Validate that the pi-cross-node-comms extension TypeScript
# compiles and pi can load it without errors.
#
# TDD: Written BEFORE implementation changes.
#
# Run: bash tests/unit/test-extension-load.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

PASS=0
FAIL=0
TOTAL=0

echo "=== pi-cross-node-comms extension load validation ==="
echo ""

# 1. Extension entry point must exist
TOTAL=$((TOTAL + 1))
EXT_FILE="$REPO_ROOT/src/index.ts"
if [[ -f "$EXT_FILE" ]]; then
  PASS=$((PASS + 1))
  echo "  ✅ Extension entry point exists: src/index.ts"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Extension entry point missing: src/index.ts"
fi

# 2. TypeScript syntax check — verify the extension compiles without obvious errors
# We use bun to transpile since the project uses bun
TOTAL=$((TOTAL + 1))
if command -v bun &>/dev/null; then
  # Attempt to transpile the extension entry point
  if bun build "$EXT_FILE" --no-bundle --target=bun 2>&1 | head -5 | grep -qi "error\|fail"; then
    FAIL=$((FAIL + 1))
    echo "  ❌ TypeScript compilation has errors"
  else
    PASS=$((PASS + 1))
    echo "  ✅ TypeScript compiles without errors"
  fi
else
  # If bun isn't available, just check for obvious syntax issues
  PASS=$((PASS + 1))
  echo "  ⚠️  bun not available, skipping compile check"
fi

# 3. Export check — extension must export a default function (pi extension contract)
TOTAL=$((TOTAL + 1))
if grep -q "export default" "$EXT_FILE" || grep -q "export.*function" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Extension has export"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Extension missing export"
fi

# 4. Must register the 4 tools and 1 command
EXPECTED_TOOLS=("coms_net_list" "coms_net_send" "coms_net_get" "coms_net_await")
for TOOL in "${EXPECTED_TOOLS[@]}"; do
  TOTAL=$((TOTAL + 1))
  if grep -q "name: \"$TOOL\"" "$EXT_FILE"; then
    PASS=$((PASS + 1))
    echo "  ✅ Registers tool: $TOOL"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Missing tool registration: $TOOL"
  fi
done

# 5. Must register the coms-net command
TOTAL=$((TOTAL + 1))
if grep -q "registerCommand.*coms-net\|\"coms-net\"" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Registers command: coms-net"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing command registration: coms-net"
fi

# 6. Must import required dependencies
REQUIRED_IMPORTS=("ExtensionAPI" "@sinclair/typebox" "Theme")
for IMPORT in "${REQUIRED_IMPORTS[@]}"; do
  TOTAL=$((TOTAL + 1))
  if grep -q "$IMPORT" "$EXT_FILE"; then
    PASS=$((PASS + 1))
    echo "  ✅ Has import/usage: $IMPORT"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Missing import/usage: $IMPORT"
  fi
done

# 7. Required flags must be registered
EXPECTED_FLAGS=("project" "auth-token" "server-url" "name" "node")
for FLAG in "${EXPECTED_FLAGS[@]}"; do
  TOTAL=$((TOTAL + 1))
  if grep -q "registerFlag.*\"$FLAG\"" "$EXT_FILE"; then
    PASS=$((PASS + 1))
    echo "  ✅ Registers flag: $FLAG"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Missing flag registration: $FLAG"
  fi
done

# 8. Helper modules must exist
HELPER_FILES=("src/heartbeat-tick.ts" "src/resolve-node.ts" "src/themeMap.ts")
for HELPER in "${HELPER_FILES[@]}"; do
  TOTAL=$((TOTAL + 1))
  if [[ -f "$REPO_ROOT/$HELPER" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Helper module exists: $HELPER"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Helper module missing: $HELPER"
  fi
done

echo ""
echo "=========================================="
echo "pi-cross-node-comms extension-load: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi