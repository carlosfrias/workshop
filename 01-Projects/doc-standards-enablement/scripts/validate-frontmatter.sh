#!/usr/bin/env bash
# validate-frontmatter.sh — Validate FOCUS.md and PLAN.md frontmatter fields
#
# Usage:
#   ./validate-frontmatter.sh                     # Validate all FOCUS.md and PLAN.md files
#   ./validate-frontmatter.sh --fix                # Auto-fix what can be fixed (add defaults)
#   ./validate-frontmatter.sh --path ./01-Projects # Validate only under this path
#   ./validate-frontmatter.sh --help               # This message
#
# Validates:
#   FOCUS.md: name, summary, status, phase, progress, tracked
#   PLAN.md:  name, phase, progress
#
# Complies with doc-standards v2.4

set -euo pipefail

# ── Help ──────────────────────────────────────────────────────────────────

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  sed -n '2,13p' "$0"
  exit 0
fi

# ── Args ──────────────────────────────────────────────────────────────────

FIX=false
SEARCH_ROOT="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fix)   FIX=true; shift ;;
    --path)  SEARCH_ROOT="$2"; shift 2 ;;
    *)       echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ── Schema ────────────────────────────────────────────────────────────────

# FOCUS.md required fields and valid values
FOCUS_REQUIRED=("name" "summary" "status" "phase" "progress")
FOCUS_OPTIONAL=("tracked")
FOCUS_STATUS_VALUES=("active" "blocked" "ready" "complete" "paused" "abandoned")
FOCUS_TRACKED_VALUES=("true" "false")

# PLAN.md required fields
PLAN_REQUIRED=("name" "phase" "progress")

# ── Counters ──────────────────────────────────────────────────────────────

ERRORS=0
WARNINGS=0
FIXED=0
TOTAL=0

# ── Functions ─────────────────────────────────────────────────────────────

extract_frontmatter_field() {
  local file="$1" field="$2"
  # Extract value from YAML frontmatter (handles quoted and unquoted values)
  sed -n "/^---$/,/^---$/p" "$file" | grep "^${field}:" | head -1 | sed "s/^${field}: *//" | sed 's/^"//;s/"$//' | sed "s/^'//;s/'$//"
}

validate_focus() {
  local file="$1"
  local dir="$(dirname "$file")"
  local project="$(basename "$dir")"
  local has_errors=0

  TOTAL=$((TOTAL + 1))

  # Check required fields
  for field in "${FOCUS_REQUIRED[@]}"; do
    value=$(extract_frontmatter_field "$file" "$field")
    if [[ -z "$value" ]]; then
      echo "  ❌ MISSING: $field (in $file)"
      ERRORS=$((ERRORS + 1))
      has_errors=1

      # Auto-fix with defaults
      if [[ "$FIX" == true ]]; then
        case "$field" in
          name)      default="$project" ;;
          summary)   default="Project setup required" ;;
          status)    default="active" ;;
          phase)     default='"Phase 1: Setup"' ;;
          progress)  default="10" ;;
        esac
        # Insert field after --- line
        sed -i '' "/^---$/a\\
${field}: ${default}" "$file"
        echo "  🔧 FIXED: Added ${field}: ${default}"
        FIXED=$((FIXED + 1))
      fi
    fi
  done

  # Validate status values
  status=$(extract_frontmatter_field "$file" "status")
  if [[ -n "$status" ]] && ! echo "${FOCUS_STATUS_VALUES[@]}" | grep -qw "$status"; then
    echo "  ⚠️  INVALID status: '$status' (valid: ${FOCUS_STATUS_VALUES[*]}) — in $file"
    WARNINGS=$((WARNINGS + 1))
  fi

  # Validate progress is numeric 0-100
  progress=$(extract_frontmatter_field "$file" "progress")
  if [[ -n "$progress" ]]; then
    if ! [[ "$progress" =~ ^[0-9]+$ ]] || [[ "$progress" -lt 0 ]] || [[ "$progress" -gt 100 ]]; then
      echo "  ⚠️  INVALID progress: '$progress' (must be 0-100) — in $file"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi

  # Validate tracked if present
  tracked=$(extract_frontmatter_field "$file" "tracked")
  if [[ -n "$tracked" ]] && ! echo "${FOCUS_TRACKED_VALUES[@]}" | grep -qw "$tracked"; then
    echo "  ⚠️  INVALID tracked: '$tracked' (valid: true, false) — in $file"
    WARNINGS=$((WARNINGS + 1))
  fi

  if [[ $has_errors -eq 0 ]]; then
    echo "  ✅ $file"
  fi
}

validate_plan() {
  local file="$1"
  local has_errors=0

  TOTAL=$((TOTAL + 1))

  for field in "${PLAN_REQUIRED[@]}"; do
    value=$(extract_frontmatter_field "$file" "$field")
    if [[ -z "$value" ]]; then
      echo "  ❌ MISSING: $field (in $file)"
      ERRORS=$((ERRORS + 1))
      has_errors=1

      if [[ "$FIX" == true ]]; then
        dir="$(dirname "$file")"
        project="$(basename "$dir")"
        case "$field" in
          name)      default="$project" ;;
          phase)     default='"Phase 1: Setup"' ;;
          progress)  default="10" ;;
        esac
        sed -i '' "/^---$/a\\
${field}: ${default}" "$file"
        echo "  🔧 FIXED: Added ${field}: ${default}"
        FIXED=$((FIXED + 1))
      fi
    fi
  done

  # Validate progress is numeric 0-100
  progress=$(extract_frontmatter_field "$file" "progress")
  if [[ -n "$progress" ]]; then
    if ! [[ "$progress" =~ ^[0-9]+$ ]] || [[ "$progress" -lt 0 ]] || [[ "$progress" -gt 100 ]]; then
      echo "  ⚠️  INVALID progress: '$progress' (must be 0-100) — in $file"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi

  if [[ $has_errors -eq 0 ]]; then
    echo "  ✅ $file"
  fi
}

# ── Main ──────────────────────────────────────────────────────────────────

echo "════════════════════════════════════════════════"
echo "  doc-standards frontmatter validator v2.4"
echo "════════════════════════════════════════════════"
echo ""

echo "── Validating FOCUS.md files ──"
while IFS= read -r -d '' file; do
  validate_focus "$file"
done < <(find "$SEARCH_ROOT" -name "FOCUS.md" -not -path "*/.obsidian/*" -not -path "*/.trash/*" -print0 2>/dev/null)

echo ""
echo "── Validating PLAN.md files ──"
while IFS= read -r -d '' file; do
  validate_plan "$file"
done < <(find "$SEARCH_ROOT" -name "PLAN.md" -not -path "*/.obsidian/*" -not -path "*/.trash/*" -print0 2>/dev/null)

echo ""
echo "════════════════════════════════════════════════"
echo "  Results: $TOTAL files checked"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
if [[ "$FIX" == true ]]; then
  echo "  Fixed:    $FIXED"
fi
echo "════════════════════════════════════════════════"

if [[ $ERRORS -gt 0 ]]; then
  exit 1
fi
exit 0