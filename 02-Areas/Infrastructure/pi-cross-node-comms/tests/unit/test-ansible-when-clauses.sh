#!/usr/bin/env bash
# test-ansible-when-clauses.sh — Validate when-clause parenthesis balance in all playbooks
#
# Bug: standup-fleet.yml and phase2-pi-availability.yml had unbalanced
# parentheses in `when:` conditions using Jinja2 filters. The expression
# `(pi_current.stdout | regex_replace('^v', '')) is version(pi_version_target, '<'))`
# was missing an opening `(` — the outer `pi_current.stdout is defined and (...)`
# was not properly closed.
#
# TDD: Written BEFORE fixes. Tests started RED (unbalanced parens detected)
# and went GREEN after fixes were applied.
#
# Run: bash tests/unit/test-ansible-when-clauses.sh

set -euo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/../../ansible" && pwd)"

PASS=0
FAIL=0
TOTAL=0

# Extract when: blocks from YAML using awk and check parenthesis balance
# This catches the specific bug: missing closing ) in Jinja2 when conditions
assert_when_parens_balanced() {
  local playbook="$1"
  local label="${2:-$1}"
  TOTAL=$((TOTAL + 1))

  local errors=""

  # Extract when: blocks and check paren balance
  # Strategy: find lines starting with "when:" and collect their value(s),
  # then count ( and ) in the Jinja2 expression
  local in_when=false
  local when_text=""
  local line_num=0
  local when_start=0

  while IFS= read -r line; do
    line_num=$((line_num + 1))

    # Detect start of when: block
    if [[ "$line" =~ ^[[:space:]]*when:[[:space:]]*(.*) ]]; then
      in_when=true
      when_start=$line_num
      when_text="${BASH_REMATCH[1]}"
      # Handle single-line when
      if [[ -n "$when_text" ]]; then
        # Check paren balance
        opens=$(echo "$when_text" | tr -cd '(' | wc -c | tr -d ' ')
        closes=$(echo "$when_text" | tr -cd ')' | wc -c | tr -d ' ')
        if [[ "$opens" != "$closes" ]]; then
          errors="${errors}Line $when_start: unbalanced parens (opens=$opens, closes=$closes): ${when_text:0:80}...\n"
        fi
        in_when=false
        when_text=""
      fi
      continue
    fi

    # Collect continuation lines (indented more than when: itself)
    if $in_when; then
      # Continuation lines are more indented than the when: line
      # A blank line or a line at the same/lower indentation ends the block
      if [[ "$line" =~ ^[[:space:]]*$ ]]; then
        # Blank line — end of when block
        opens=$(echo "$when_text" | tr -cd '(' | wc -c | tr -d ' ')
        closes=$(echo "$when_text" | tr -cd ')' | wc -c | tr -d ' ')
        if [[ "$opens" != "$closes" ]]; then
          errors="${errors}Line $when_start: unbalanced parens (opens=$opens, closes=$closes): ${when_text:0:120}...\n"
        fi
        in_when=false
        when_text=""
        continue
      fi

      # Check if this is still a continuation (more indented)
      if [[ "$line" =~ ^[[:space:]]+[^[:space:]] ]]; then
        # Add this line to the when text
        when_text="$when_text ${line##*([[:space:]])}"
      else
        # Not indented — end of when block
        opens=$(echo "$when_text" | tr -cd '(' | wc -c | tr -d ' ')
        closes=$(echo "$when_text" | tr -cd ')' | wc -c | tr -d ' ')
        if [[ "$opens" != "$closes" ]]; then
          errors="${errors}Line $when_start: unbalanced parens (opens=$opens, closes=$closes): ${when_text:0:120}...\n"
        fi
        in_when=false
        when_text=""
      fi
    fi
  done < "$playbook"

  # Flush any remaining when block
  if $in_when && [[ -n "$when_text" ]]; then
    opens=$(echo "$when_text" | tr -cd '(' | wc -c | tr -d ' ')
    closes=$(echo "$when_text" | tr -cd ')' | wc -c | tr -d ' ')
    if [[ "$opens" != "$closes" ]]; then
      errors="${errors}Line $when_start: unbalanced parens (opens=$opens, closes=$closes): ${when_text:0:120}...\n"
    fi
  fi

  if [[ -z "$errors" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $label — when-clause parens balanced"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $label — unbalanced when-clause parentheses"
    echo -e "$errors"
  fi
}

echo "=== Ansible When-Clause Parenthesis Balance Tests ==="
echo ""

for f in "$ANSIBLE_DIR"/*.yml; do
  [[ "$(basename "$f")" == "inventory.yml" ]] && continue
  assert_when_parens_balanced "$f" "$(basename "$f")"
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $TOTAL total ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi