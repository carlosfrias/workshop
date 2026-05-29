#!/usr/bin/env bash
# test-ansible-playbook-syntax.sh — Validate all Ansible playbooks have valid YAML/Jinja2 syntax
#
# TDD: Written BEFORE the fixes were applied. These tests started RED
# (syntax errors in deploy-fleet.yml, standup-fleet.yml, phase2, phase5)
# and went GREEN after the fixes.
#
# Run: bash tests/unit/test-ansible-playbook-syntax.sh

set -euo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/../../ansible" && pwd)"
INVENTORY="$ANSIBLE_DIR/inventory.yml"

PASS=0
FAIL=0
TOTAL=0

assert_syntax_valid() {
  local playbook="$1"
  local label="${2:-$1}"
  TOTAL=$((TOTAL + 1))
  if ansible-playbook --syntax-check -i "$INVENTORY" "$playbook" 2>&1 | grep -q "^playbook:"; then
    PASS=$((PASS + 1))
    echo "  PASS: $label"
  else
    FAIL=$((FAIL + 1))
    echo "  FAIL: $label — syntax check failed"
    ansible-playbook --syntax-check -i "$INVENTORY" "$playbook" 2>&1 | tail -5
  fi
}

echo "=== Ansible Playbook Syntax Tests ==="
echo ""

assert_syntax_valid "$ANSIBLE_DIR/standup-fleet.yml" "standup-fleet.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase2-pi-availability.yml" "phase2-pi-availability.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase5-agent-services.yml" "phase5-agent-services.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/deploy-fleet.yml" "deploy-fleet.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/deploy-hub-to-fnet2.yml" "deploy-hub-to-fnet2.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase1-hub-server.yml" "phase1-hub-server.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase3-ollama-models.yml" "phase3-ollama-models.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase4-extension-deploy.yml" "phase4-extension-deploy.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/phase6-fleet-validation.yml" "phase6-fleet-validation.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/shutdown-fleet.yml" "shutdown-fleet.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/start-agents.yml" "start-agents.yml syntax valid"
assert_syntax_valid "$ANSIBLE_DIR/standup-fleet-chains.yml" "standup-fleet-chains.yml syntax valid"

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $TOTAL total ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi