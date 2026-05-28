#!/usr/bin/env bash
# test-package-json.sh — package.json pi.extensions and pi.skills validation for pi-cross-node-comms
# TDD: Written BEFORE any changes.
#
# Run: bash tests/unit/test-package-json.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

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

assert_json_array_includes() {
  local file="$1" path="$2" value="$3" label="${4:-$1}"
  TOTAL=$((TOTAL + 1))
  if python3 -c "
import json, sys
d = json.load(open('$file'))
parts = '$path'.split('.')
obj = d
for p in parts:
    obj = obj[p]
arr = obj if isinstance(obj, list) else [obj]
sys.exit(0 if '$value' in arr else 1)
" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — '$path' does not include '$value'"
  fi
}

assert_json_matches() {
  local file="$1" expr="$2" label="${3:-$1}"
  TOTAL=$((TOTAL + 1))
  if python3 -c "
import json, sys
d = json.load(open('$file'))
result = $expr
sys.exit(0 if result else 1)
" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — expression failed: $expr"
  fi
}

echo "=== pi-cross-node-comms package.json validation ==="
echo ""

PKG_JSON="$REPO_ROOT/package.json"

# package.json exists
assert_exists "$PKG_JSON" "package.json"

if [[ -f "$PKG_JSON" ]]; then
  # pi key must exist
  TOTAL=$((TOTAL + 1))
  if python3 -c "
import json
d = json.load(open('$PKG_JSON'))
assert 'pi' in d
" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: package.json missing top-level 'pi' key"
  fi

  # pi.extensions must be an array containing "./src/index.ts"
  assert_json_array_includes "$PKG_JSON" "pi.extensions" "./src/index.ts" "pi.extensions includes extension entry point"

  # pi.skills must be an array containing "./src/skills"
  assert_json_array_includes "$PKG_JSON" "pi.skills" "./src/skills" "pi.skills includes skills dir"

  # name must be pi-cross-node-comms
  assert_json_matches "$PKG_JSON" "d['name'] == 'pi-cross-node-comms'" "package name is pi-cross-node-comms"

  # type must be module (for ESM)
  assert_json_matches "$PKG_JSON" "d.get('type') == 'module'" "package type is module"

  # Vestigial pi.agents must NOT exist
  TOTAL=$((TOTAL + 1))
  if python3 -c "
import json
d = json.load(open('$PKG_JSON'))
assert 'agents' not in d.get('pi', {})
" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: Vestigial pi.agents key still in package.json"
  fi

  # pi.extensions must have exactly 1 entry (the main extension)
  TOTAL=$((TOTAL + 1))
  EXT_COUNT=$(python3 -c "
import json
d = json.load(open('$PKG_JSON'))
print(len(d.get('pi', {}).get('extensions', [])))
" 2>/dev/null || echo "0")
  if [ "$EXT_COUNT" -eq 1 ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: pi.extensions should have exactly 1 entry, found $EXT_COUNT"
  fi
fi

echo ""
echo "=========================================="
echo "pi-cross-node-comms package-json: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi