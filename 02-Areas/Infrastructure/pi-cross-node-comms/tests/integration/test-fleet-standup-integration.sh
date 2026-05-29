#!/usr/bin/env bash
# test-fleet-standup-integration.sh — Integration test for fleet standup playbook
#
# Validates that the full standup-fleet.yml playbook can be parsed and has
# all required phases, tasks, and variable references intact.
#
# TDD: Written after bugs were found during fleet standup to prevent regressions.
#
# Run: bash tests/integration/test-fleet-standup-integration.sh

set -euo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/../../ansible" && pwd)"

PASS=0
FAIL=0
TOTAL=0

echo "=== Fleet Standup Integration Tests ==="
echo ""

# Test 1: standup-fleet.yml has all 6 phases
TOTAL=$((TOTAL + 1))
PLAYBOOK="$ANSIBLE_DIR/standup-fleet.yml"
PHASES=$(grep -c "^- name: PHASE" "$PLAYBOOK" 2>/dev/null || echo "0")
if [[ "$PHASES" -ge 6 ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: standup-fleet.yml has $PHASES phases (expected 6+)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: standup-fleet.yml has $PHASES phases (expected 6+)"
fi

# Test 2: pi_version_target is not stale (< 0.77.0)
TOTAL=$((TOTAL + 1))
DECLARED=$(grep -o 'pi_version_target: "[^"]*"' "$PLAYBOOK" | head -1 | sed 's/pi_version_target: "//;s/"$//')
MAJOR=$(echo "$DECLARED" | cut -d. -f1)
MINOR=$(echo "$DECLARED" | cut -d. -f2)
if [[ "$MAJOR" -ge 1 ]] || [[ "$MINOR" -ge 77 ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: pi_version_target=$DECLARED is current (>= 0.77.0)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: pi_version_target=$DECLARED appears stale (expected >= 0.77.0)"
fi

# Test 3: No 'running' string comparison in systemctl is-active checks across fleet playbooks
TOTAL=$((TOTAL + 1))
BAD_COUNT=0
for pf in "$ANSIBLE_DIR"/standup-fleet.yml "$ANSIBLE_DIR"/phase5-agent-services.yml "$ANSIBLE_DIR"/start-agents.yml; do
  [[ -f "$pf" ]] || continue
  C=$(grep -c 'echo "running"' "$pf" 2>/dev/null || true)
  BAD_COUNT=$((BAD_COUNT + C))
done
if [[ "$BAD_COUNT" -eq 0 ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: No 'running' string comparison bug in systemctl checks"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: Found $BAD_COUNT 'echo \"running\"' occurrences in systemctl checks"
fi

# Test 4: systemctl is-active uses 'active' comparison in fleet playbooks
TOTAL=$((TOTAL + 1))
GOOD_COUNT=0
for pf in "$ANSIBLE_DIR"/standup-fleet.yml "$ANSIBLE_DIR"/phase5-agent-services.yml; do
  [[ -f "$pf" ]] || continue
  C=$(grep -c "pi_running.stdout | trim == 'active'" "$pf" 2>/dev/null || true)
  GOOD_COUNT=$((GOOD_COUNT + C))
done
if [[ "$GOOD_COUNT" -ge 2 ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: systemctl is-active compares to 'active' ($GOOD_COUNT occurrences across playbooks)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: systemctl is-active should compare to 'active' (found $GOOD_COUNT occurrences, expected 2+)"
fi

# Test 5: All phase playbooks have consistent pi_version_target
TOTAL=$((TOTAL + 1))
CONSISTENT=true
for pf in "$ANSIBLE_DIR"/phase2-pi-availability.yml "$ANSIBLE_DIR"/standup-fleet.yml; do
  [[ -f "$pf" ]] || continue
  PV=$(grep -o 'pi_version_target: "[^"]*"' "$pf" | head -1 | sed 's/pi_version_target: "//;s/"$//')
  if [[ "$PV" != "$DECLARED" ]]; then
    CONSISTENT=false
    echo "  FAIL: $(basename "$pf") pi_version_target=$PV differs from standup-fleet.yml=$DECLARED"
  fi
done
if $CONSISTENT; then
  PASS=$((PASS + 1))
  echo "  PASS: All playbooks have consistent pi_version_target=$DECLARED"
else
  FAIL=$((FAIL + 1))
fi

# Test 6: phase2-pi-availability.yml when-clause parens balanced
TOTAL=$((TOTAL + 1))
PHASE2="$ANSIBLE_DIR/phase2-pi-availability.yml"
WHEN_LINE=$(grep -n "when: >" "$PHASE2" -A 3 2>/dev/null | grep "is version" || true)
OPEN=$(echo "$WHEN_LINE" | tr -cd '(' | wc -c | tr -d ' ')
CLOSE=$(echo "$WHEN_LINE" | tr -cd ')' | wc -c | tr -d ' ')
if [[ "$OPEN" == "$CLOSE" ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: phase2-pi-availability.yml when-clause parens balanced (opens=$OPEN, closes=$CLOSE)"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: phase2-pi-availability.yml when-clause parens unbalanced (opens=$OPEN, closes=$CLOSE)"
fi

# Test 7: phase5-agent-services.yml has correct systemctl comparison
TOTAL=$((TOTAL + 1))
PHASE5="$ANSIBLE_DIR/phase5-agent-services.yml"
BAD5=$(grep -c 'echo "running"' "$PHASE5" 2>/dev/null || true)
GOOD5=$(grep -c "pi_running.stdout | trim == 'active'" "$PHASE5" 2>/dev/null || true)
if [[ "$BAD5" -eq 0 && "$GOOD5" -ge 1 ]]; then
  PASS=$((PASS + 1))
  echo "  PASS: phase5-agent-services.yml systemctl comparison correct"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: phase5-agent-services.yml systemctl comparison incorrect (bad=$BAD5, good=$GOOD5)"
fi

# Test 8: deploy-fleet.yml has valid YAML syntax
TOTAL=$((TOTAL + 1))
INVENTORY="$ANSIBLE_DIR/inventory.yml"
if ansible-playbook --syntax-check -i "$INVENTORY" "$ANSIBLE_DIR/deploy-fleet.yml" 2>&1 | grep -q "^playbook:"; then
  PASS=$((PASS + 1))
  echo "  PASS: deploy-fleet.yml YAML syntax valid"
else
  FAIL=$((FAIL + 1))
  echo "  FAIL: deploy-fleet.yml YAML syntax invalid"
fi

# Test 9: All playbook files pass ansible syntax check
TOTAL=$((TOTAL + 1))
ALL_VALID=true
for pf in "$ANSIBLE_DIR"/*.yml; do
  [[ "$(basename "$pf")" == "inventory.yml" ]] && continue
  if ! ansible-playbook --syntax-check -i "$INVENTORY" "$pf" 2>&1 | grep -q "^playbook:"; then
    ALL_VALID=false
    echo "  FAIL: $(basename "$pf") syntax check failed"
  fi
done
if $ALL_VALID; then
  PASS=$((PASS + 1))
  echo "  PASS: All playbook files pass ansible syntax check"
else
  FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $TOTAL total ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi