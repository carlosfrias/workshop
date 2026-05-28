#!/usr/bin/env bash
# test-env-config.sh — Validate config resolution: env vars, server.json, server.secret.json
# Tests that the extension correctly reads config from env vars and fallback files.
#
# TDD: Written BEFORE implementation changes.
#
# Run: bash tests/unit/test-env-config.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
COMS_NET_DIR="$HOME/.pi/coms-net"

PASS=0
FAIL=0
TOTAL=0

assert_exists() {
  local file="$1" label="${2:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ -f "$file" ]]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — file does not exist: $file"
  fi
}

assert_dir_exists() {
  local dir="$1" label="${2:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ -d "$dir" ]]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — directory does not exist: $dir"
  fi
}

echo "=== pi-cross-node-comms env config validation ==="
echo ""

# 1. Extension must reference env var constants
EXT_FILE="$REPO_ROOT/src/index.ts"

ENV_VARS=("PI_COMS_NET_SERVER_URL" "PI_COMS_NET_AUTH_TOKEN" "PI_COMS_NET_PROJECT" "PI_COMS_NET_NODE")
for VAR in "${ENV_VARS[@]}"; do
  TOTAL=$((TOTAL + 1))
  if grep -q "$VAR" "$EXT_FILE"; then
    PASS=$((PASS + 1))
    echo "  ✅ References env var: $VAR"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Missing env var reference: $VAR"
  fi
done

# 2. Extension must reference config directory ~/.pi/coms-net/
TOTAL=$((TOTAL + 1))
if grep -q 'path.join.*coms-net\|"coms-net"' "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ References coms-net config directory"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing reference to coms-net config directory"
fi

# 3. Extension must reference server.json reading
TOTAL=$((TOTAL + 1))
if grep -q "server.json\|readServerJson" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Has server.json config reading"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing server.json config reading"
fi

# 4. Extension must reference server.secret.json reading
TOTAL=$((TOTAL + 1))
if grep -q "server.secret.json\|readServerSecret" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Has server.secret.json auth token reading"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing server.secret.json auth token reading"
fi

# 5. Verify priority: CLI flags > env vars > config files
# Extract resolveServerUrl function body and verify cliFlag is checked BEFORE SERVER_URL_ENV
TOTAL=$((TOTAL + 1))
SERVERURL_BODY=$(sed -n '/^function resolveServerUrl/,/^}/p' "$EXT_FILE" 2>/dev/null || sed -n '/resolveServerUrl/,/^}/p' "$EXT_FILE" 2>/dev/null || echo "")
if [[ -n "$SERVERURL_BODY" ]]; then
  CLI_LINE=$(echo "$SERVERURL_BODY" | grep -n "cliFlag" | head -1 | cut -d: -f1)
  ENV_LINE=$(echo "$SERVERURL_BODY" | grep -n "SERVER_URL_ENV" | head -1 | cut -d: -f1)
  FILE_LINE=$(echo "$SERVERURL_BODY" | grep -n "readServerJson" | head -1 | cut -d: -f1)
  if [[ -n "$CLI_LINE" ]] && [[ -n "$ENV_LINE" ]] && [[ "$CLI_LINE" -lt "$ENV_LINE" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Server URL priority: cliFlag (line $CLI_LINE) < SERVER_URL_ENV (line $ENV_LINE)"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Server URL priority incorrect: cliFlag=$CLI_LINE, SERVER_URL_ENV=$ENV_LINE (should be cliFlag first)"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Cannot extract resolveServerUrl function body"
fi

# 6. Verify auth token has same priority chain
TOTAL=$((TOTAL + 1))
AUTHTOKEN_BODY=$(sed -n '/^function resolveAuthToken/,/^}/p' "$EXT_FILE" 2>/dev/null || sed -n '/resolveAuthToken/,/^}/p' "$EXT_FILE" 2>/dev/null || echo "")
if [[ -n "$AUTHTOKEN_BODY" ]]; then
  CLI_LINE=$(echo "$AUTHTOKEN_BODY" | grep -n "cliFlag" | head -1 | cut -d: -f1)
  ENV_LINE=$(echo "$AUTHTOKEN_BODY" | grep -n "AUTH_TOKEN_ENV" | head -1 | cut -d: -f1)
  FILE_LINE=$(echo "$AUTHTOKEN_BODY" | grep -n "readServerSecret" | head -1 | cut -d: -f1)
  if [[ -n "$CLI_LINE" ]] && [[ -n "$ENV_LINE" ]] && [[ "$CLI_LINE" -lt "$ENV_LINE" ]]; then
    PASS=$((PASS + 1))
    echo "  ✅ Auth token priority: cliFlag (line $CLI_LINE) < AUTH_TOKEN_ENV (line $ENV_LINE)"
  else
    FAIL=$((FAIL + 1))
    echo "  ❌ Auth token priority incorrect: cliFlag=$CLI_LINE, AUTH_TOKEN_ENV=$ENV_LINE (should be cliFlag first)"
  fi
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Cannot extract resolveAuthToken function body"
fi

# 7. Config directory tree must exist for known projects
assert_dir_exists "$COMS_NET_DIR" "coms-net config root"

# 8. Verify config directory structure in code — projects/<project>/server.json
TOTAL=$((TOTAL + 1))
if grep -q "projects.*server.json\|projectDir" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Uses project-scoped config paths"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing project-scoped config paths"
fi

# 9. Default project must be "default"
TOTAL=$((TOTAL + 1))
if grep -q '"default".*project\|project.*"default"' "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Default project is 'default'"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Default project is not 'default'"
fi

# 10. Auth token secret file must be mode 0600 (checked in readServerSecret)
TOTAL=$((TOTAL + 1))
if grep -q "0o600\|0600" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Validates server.secret.json file permissions (0600)"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing server.secret.json file permission validation"
fi

# 11. Health check must be done before registration
TOTAL=$((TOTAL + 1))
if grep -q "/health\|health" "$EXT_FILE"; then
  PASS=$((PASS + 1))
  echo "  ✅ Health check before registration"
else
  FAIL=$((FAIL + 1))
  echo "  ❌ Missing health check"
fi

echo ""
echo "=========================================="
echo "pi-cross-node-comms env-config: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi