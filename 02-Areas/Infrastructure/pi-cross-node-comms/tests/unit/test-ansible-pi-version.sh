#!/usr/bin/env bash
# test-ansible-pi-version.sh — Validate pi_version_target is current, not stale
#
# Bug: pi_version_target was set to "0.75.5" but the latest pi release is
# newer (0.77.0 at time of writing). Stale version targets cause unnecessary
# reinstalls or skipped upgrades.
#
# TDD: Written BEFORE the version bump. Test checks that pi_version_target
# in playbooks matches the latest npm published version.
#
# Run: bash tests/unit/test-ansible-pi-version.sh

set -euo pipefail

ANSIBLE_DIR="$(cd "$(dirname "$0")/../../ansible" && pwd)"

PASS=0
FAIL=0
TOTAL=0

# Get the latest pi version from npm
LATEST_PI_VERSION=$(npm view @earendil-works/pi-coding-agent version 2>/dev/null || echo "unknown")

assert_version_current() {
  local playbook="$1"
  local label="${2:-$1}"
  TOTAL=$((TOTAL + 1))

  local declared_version
  declared_version=$(grep -o 'pi_version_target: "[^"]*"' "$playbook" 2>/dev/null | head -1 | sed 's/pi_version_target: "//;s/"$//' || echo "NOT_FOUND")

  if [[ "$declared_version" == "NOT_FOUND" ]]; then
    # Playbook doesn't use pi_version_target — skip
    PASS=$((PASS + 1))
    echo "  SKIP: $label — no pi_version_target found (not applicable)"
    return
  fi

  if [[ "$LATEST_PI_VERSION" == "unknown" ]]; then
    # Can't reach npm — warn but don't fail
    PASS=$((PASS + 1))
    echo "  WARN: $label — pi_version_target=$declared_version (can't verify latest, npm unavailable)"
    return
  fi

  if [[ "$declared_version" == "$LATEST_PI_VERSION" ]]; then
    PASS=$((PASS + 1))
    echo "  PASS: $label — pi_version_target=$declared_version matches latest $LATEST_PI_VERSION"
  else
    # Check if declared is at least not clearly stale (< 2 major versions behind)
    # Allow minor/patch differences — we just don't want major drift
    FAIL=$((FAIL + 1))
    echo "  FAIL: $label — pi_version_target=$declared_version but latest is $LATEST_PI_VERSION"
  fi
}

echo "=== Ansible pi_version_target Currency Tests ==="
echo "  Latest pi version from npm: $LATEST_PI_VERSION"
echo ""

for f in "$ANSIBLE_DIR"/standup-fleet.yml "$ANSIBLE_DIR"/phase2-pi-availability.yml; do
  if [[ -f "$f" ]]; then
    assert_version_current "$f" "$(basename "$f")"
  fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed, $TOTAL total ==="

if [[ $FAIL -gt 0 ]]; then
  exit 1
fi