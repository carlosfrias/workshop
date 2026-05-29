---
status: released
version: 0.2.0
release_date: 2026-05-29
tests: 42/42 pass
---

# PLAN — pi-cross-node-comms v0.2.0

## Release: Fleet Standup Bug Fix

### Bugs Fixed

| # | Description | Files Changed |
|---|-------------|---------------|
| 1 | Missing closing paren in when-clause `is version()` | `standup-fleet.yml`, `phase2-pi-availability.yml` |
| 2 | Stale `pi_version_target` (0.75.5 → 0.77.0) | `standup-fleet.yml`, `phase2-pi-availability.yml` |
| 3 | systemctl is-active returns "active" not "running" | `standup-fleet.yml`, `phase5-agent-services.yml` |
| 4 | Invalid YAML structure in deploy-fleet.yml | `deploy-fleet.yml` |
| 5 | Inconsistent `hub_project` (default vs lab) | `standup-fleet.yml`, `phase5-agent-services.yml`, `deploy-fleet.yml`, `phase6-fleet-validation.yml` |

### TDD Test Suite

| Suite | Tests | Status |
|-------|-------|--------|
| `test-ansible-playbook-syntax.sh` | 12 | 🟢 PASS |
| `test-ansible-when-clauses.sh` | 13 | 🟢 PASS |
| `test-ansible-pi-version.sh` | 2 | 🟢 PASS |
| `test-ansible-systemctl-status.sh` | 6 | 🟢 PASS |
| `test-fleet-standup-integration.sh` | 9 | 🟢 PASS |
| **Total** | **42** | **🟢 ALL GREEN** |

### Release Checklist

- [x] Fix parenthesis imbalance in `when:` conditions
- [x] Update `pi_version_target` to match npm latest (0.77.0)
- [x] Fix systemctl status comparison to use "active"
- [x] Fix deploy-fleet.yml YAML structure
- [x] Standardize `hub_project` to "lab"
- [x] Create unit tests for each bug category
- [x] Create integration test for fleet standup
- [x] All tests run green
- [x] No development in `.pi` folders
- [x] FOCUS.md created

### Known Operational Issue

Phase 6 validation "Wait for agents to register" may fail if agents cannot reach the hub. The hub starts successfully (health check passes) but agents may need additional time or network troubleshooting to register. **This is an operational concern, not a playbook bug.**
