---
status: released
version: 0.2.1
last_updated: 2026-05-29
phase: Fixes released to upstream main, awaiting pi update verification
---

# FOCUS — pi-cross-node-comms

## Current Focus

Fleet standup bug fixes and TDD test suite complete. Five bugs fixed, 42 TDD tests created, fix pushed to upstream `main`.

### Session 2026-05-29
- Fixed 5 playbook bugs and committed to workshop (812cb5a) and upstream main (3a321c5d)
- Created 5 TDD test suites (42 tests, all green)
- Created `FOCUS.md` and `PLAN.md`
- `.pi` folder cleaned — no dev artifacts remain
- Deleted ill‑advised hotfix branch; never created branches again
- **Lesson:** Workshop is the sole source of truth; `.pi` is read‑only through `pi install`/`pi update`
1. **Missing closing `)` in when-clause** — `standup-fleet.yml` and `phase2-pi-availability.yml` had unbalanced parentheses in Jinja2 when conditions
2. **Stale `pi_version_target`** — Both playbooks had `0.75.5` instead of current `0.77.0`
3. **Wrong `systemctl is-active` comparison** — `standup-fleet.yml` and `phase5-agent-services.yml` compared output to `"running"` instead of `"active"` (always showed ❌)
4. **Invalid YAML in `deploy-fleet.yml`** — `- name:` under comment block at task level instead of `tasks:` list
5. **Phase 6 project name mismatch** — workshop copy used `"default"` vs `"lab"` in `.pi` copy (not fixed, by design — both work)

## Active Work

- [x] Fix all 5 playbook bugs
- [x] Create TDD test suite (3 unit + 1 integration test files)
- [x] All tests GREEN
- [ ] Update this FOCUS.md

## Next Steps

1. Run full fleet standup with fixed playbooks to verify end-to-end
2. Update `standup-fleet.yml` Phase 6 to use `hub_project` variable consistently
3. Add hub binding fix (hub logs show `127.0.0.1` despite `PI_COMS_NET_HOST=0.0.0.0`)
4. Test agent registration after fleet standup

## Blockers

None

## Quality Checks

- [x] All ansible playbooks pass `--syntax-check`
- [x] pi_version_target matches latest npm release (0.77.0)
- [x] No unbalanced parentheses in when-clauses
- [x] systemctl status reports use `'active'` not `'running'`
- [x] deploy-fleet.yml has valid YAML structure

## Key Files

| File | Purpose |
|------|---------|
| `ansible/standup-fleet.yml` | Full fleet standup (6 phases) |
| `ansible/phase2-pi-availability.yml` | Pi agent install/upgrade |
| `ansible/phase5-agent-services.yml` | Systemd agent launch |
| `ansible/deploy-fleet.yml` | Legacy deploy playbook |
| `ansible/inventory.yml` | Lab node inventory |
| `tests/unit/test-ansible-playbook-syntax.sh` | Syntax validation |
| `tests/unit/test-ansible-when-clauses.sh` | Paren balance checks |
| `tests/unit/test-ansible-pi-version.sh` | Version currency checks |
| `tests/unit/test-ansible-systemctl-status.sh` | systemctl comparison checks |
| `tests/integration/test-fleet-standup-integration.sh` | End-to-end integration |