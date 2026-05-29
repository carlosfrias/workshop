#!/usr/bin/env bash
# test-ansible-systemctl-status.sh — Validate systemctl status checks use correct output values
#
# Bug: `systemctl is-active <service>` outputs "active" on success, not "running".
# Two playbooks compared the output to "running" which would always fail,
# producing a ❌ emoji even when the service was healthy.
#
# Fixed by: removing the `&& echo "running"` post-processing and comparing
# the trimmed shell output directly to "active".
#
# TDD: Written BEFORE fixes. Tests started RED (wrong comparison values)
# and went GREEN after fixes were applied.
#
# Run: bash tests/unit/test-ansible-systemctl-status.sh

set -euo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/../../ansible" && pwd)"

PASS=0
FAIL=0
TOTAL=0

assert_no_running_comparison() {
  local playbook="$1"
  local label="${2:-$1}"
  TOTAL=$((TOTAL + 1))

  # Search for the specific bug pattern: comparing systemctl output to "running"
  # The bug was: `systemctl is-active ... && echo "running" || echo "not running"`
  # followed by `pi_running.stdout == 'running'`
  local bad_patterns
  bad_patterns=$(grep -n 'echo "running"' "$playbook" 2>/dev/null || true)

  # Also check for the Jinja2 comparison pattern
  local bad_jinja
  bad_jinja=$(grep -n "pi_running.stdout == 'running'" "$playbook" 2>/dev/null || true)

  if [[ -z "$bad_patterns" && -z "$bad_jinja" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $label — no 'running' comparison bug found"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $label — found systemctl 'running' comparison bug"
    [[ -n "$bad_patterns" ]] && echo "         Lines with echo:'$bad_patterns'"
    [[ -n "$bad_jinja" ]] && echo "         Lines with jinja2:'$bad_jinja'"
  fi
}

assert_active_comparison() {
  local playbook="$1"
  local label="${2:-$1}"
  TOTAL=$((TOTAL + 1))

  # The fix uses: pi_running.stdout | trim == 'active'
  local good_patterns
  good_patterns=$(grep -n "pi_running.stdout | trim == 'active'" "$playbook" 2>/dev/null || true)

  if [[ -n "$good_patterns" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $label — uses correct 'active' comparison for systemctl"
  else
    # Check if this playbook even has a systemctl is-active check
    local has_systemctl
    has_systemctl=$(grep -c "systemctl is-active" "$playbook" 2>/dev/null || true)

    if [[ "$has_systemctl" == "0" || -z "$has_systemctl" ]]; then
      PASS=$((PASS + 1))
      echo "  SKIP: $label — no systemctl is-active check (not applicable)"
    else
      FAIL=$((FAIL + 1))
      echo "  FAIL: $label — has systemctl is-active but doesn't compare to 'active'"
    fi
  fi
}

echo "=== Ansible systemctl Status Comparison Tests ==="
echo ""

for f in "$ANSIBLE_DIR"/standup-fleet.yml "$ANSIBLE_DIR"/phase5-agent-services.yml "$ANSIBLE_DIR"/start-agents.yml; do
  if [[ -f "$f" ]]; then
    assert_no_running_comparison "$f" "$(basename "$f") no-running-comparison"
    assert_active_comparison "$f" "$(basename "$f") uses-active-comparison"
  fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $TOTAL total ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi