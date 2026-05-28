#!/usr/bin/env bash
# test-skill-format.sh — SKILL.md format validation for pi-cross-node-comms skill
# Tests that the skill follows the agentskills.io spec with proper frontmatter,
# decomposed sections with MANIFEST.json, and LOD loading directives.
#
# TDD: Written BEFORE implementation changes.
#
# Run: bash tests/unit/test-skill-format.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/src/skills"

# --- Assert helpers ---
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

assert_file_contains() {
  local file="$1" pattern="$2" label="${3:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$file" ]]; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — file missing, cannot check for: $pattern"
    return
  fi
  if grep -q "$pattern" "$file"; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — does not contain: $pattern"
  fi
}

assert_file_not_contains() {
  local file="$1" pattern="$2" label="${3:-$1}"
  TOTAL=$((TOTAL + 1))
  if [[ ! -f "$file" ]]; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — file missing"
    return
  fi
  if grep -q "$pattern" "$file"; then
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — unexpectedly contains: $pattern"
  else
    PASS=$((PASS + 1))
  fi
}

validate_name() {
  local name="$1" label="$2"
  TOTAL=$((TOTAL + 1))
  if [[ "$name" =~ ^[a-z0-9] ]] && \
     [[ "$name" =~ [a-z0-9]$ ]] && \
     [[ ! "$name" =~ -- ]] && \
     [[ "$name" =~ ^[a-z0-9-]+$ ]] && \
     [[ ${#name} -le 64 ]] && \
     [[ ${#name} -ge 1 ]]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $label — invalid name '$name' (must be lowercase, hyphens, 1-64 chars, no leading/trailing/consecutive hyphens)"
  fi
}

echo "=== pi-cross-node-comms SKILL.md format validation ==="
echo ""

SKILL_NAME="pi-cross-node-comms"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"
SKILL_FILE="$SKILL_DIR/SKILL.md"
MANIFEST_FILE="$SKILL_DIR/MANIFEST.json"

echo "--- Testing: $SKILL_NAME ---"

# SKILL.md must exist
assert_exists "$SKILL_FILE" "$SKILL_NAME SKILL.md"

if [[ -f "$SKILL_FILE" ]]; then
  # YAML frontmatter opening
  assert_file_contains "$SKILL_FILE" "^---" "$SKILL_NAME has frontmatter delimiter"

  # name field in frontmatter — must match parent directory
  assert_file_contains "$SKILL_FILE" "^name:" "$SKILL_NAME has name frontmatter"
  assert_file_contains "$SKILL_FILE" "^name: $SKILL_NAME" "$SKILL_NAME name matches parent dir"
  validate_name "$SKILL_NAME" "$SKILL_NAME name format"

  # description field in frontmatter
  assert_file_contains "$SKILL_FILE" "^description:" "$SKILL_NAME has description frontmatter"

  # Decomposed skill: must reference MANIFEST.json and sections
  assert_file_contains "$SKILL_FILE" "MANIFEST" "$SKILL_NAME references MANIFEST.json"
  assert_file_contains "$SKILL_FILE" "LOD" "$SKILL_NAME has LOD loading directive"
fi

# MANIFEST.json must exist and be valid JSON
assert_exists "$MANIFEST_FILE" "$SKILL_NAME MANIFEST.json"
if [[ -f "$MANIFEST_FILE" ]]; then
  TOTAL=$((TOTAL + 1))
  if python3 -c "import json; json.load(open('$MANIFEST_FILE'))" 2>/dev/null; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $SKILL_NAME MANIFEST.json is invalid JSON"
  fi

  # MANIFEST must list sections
  TOTAL=$((TOTAL + 1))
  SECTION_COUNT=$(python3 -c "
import json
d = json.load(open('$MANIFEST_FILE'))
print(len(d.get('sections', [])))
" 2>/dev/null || echo "0")
  if [ "$SECTION_COUNT" -ge 1 ]; then
    PASS=$((PASS + 1))
  else
    FAIL=$((FAIL + 1))
    echo "FAIL: $SKILL_NAME MANIFEST.json has no sections"
  fi
fi

# Check decomposed section files exist
SECTION_FILES=(
  "CORE.md"
  "PATTERNS.md"
  "CONFIG.md"
)

for SECTION_FILE in "${SECTION_FILES[@]}"; do
  assert_exists "$SKILL_DIR/$SECTION_FILE" "$SKILL_NAME section $SECTION_FILE"
done

# CORE.md must contain tool reference table
if [[ -f "$SKILL_DIR/CORE.md" ]]; then
  assert_file_contains "$SKILL_DIR/CORE.md" "coms_net_list" "CORE.md references coms_net_list"
  assert_file_contains "$SKILL_DIR/CORE.md" "coms_net_send" "CORE.md references coms_net_send"
  assert_file_contains "$SKILL_DIR/CORE.md" "coms_net_await" "CORE.md references coms_net_await"
  assert_file_contains "$SKILL_DIR/CORE.md" "coms_net_get" "CORE.md references coms_net_get"
fi

# PATTERNS.md must contain workflow patterns
if [[ -f "$SKILL_DIR/PATTERNS.md" ]]; then
  assert_file_contains "$SKILL_DIR/PATTERNS.md" "Fire-and-Forget\|fire-and-forget\|Fire and Forget" "PATTERNS.md has fire-and-forget pattern"
fi

# CONFIG.md must contain agent configuration
if [[ -f "$SKILL_DIR/CONFIG.md" ]]; then
  assert_file_contains "$SKILL_DIR/CONFIG.md" "coms-net\|hub\|project" "CONFIG.md references configuration"
fi

echo ""
echo "=========================================="
echo "pi-cross-node-comms skill-format: $PASS passed, $FAIL failed, $TOTAL total"
echo "=========================================="
if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi