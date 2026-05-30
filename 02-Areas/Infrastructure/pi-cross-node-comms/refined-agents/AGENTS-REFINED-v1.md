---
version: 1
date: 2026-05-29
session: 2026-05-29-fleet-standup-bugfix
status: active
trigger: Fleet standup playbook failures + .pi contamination incident
---

# AGENTS-REFINED-v1 — pi-cross-node-comms

## Battle-Tested Rules

### RULE 1: Workshop-First, Release-Through-Main

**Trigger:** Any code change to ansible playbooks, tests, scripts, or extension code.  
**Rule:** All code changes MUST originate in the workshop codebase (`workshop/02-Areas/Infrastructure/pi-cross-node-comms/`). The `.pi/agent/git/` clone is read-only — never edit files there directly. Changes reach `.pi` ONLY through `pi install`/`pi update` pulling from the GitHub `main` branch. No exceptions.

**Substance:** This session contaminated the `.pi` folder with direct edits, then created an unnecessary hotfix branch, then had to clean both. The correct flow is:

```
workshop (develop) → git commit → git push origin main → pi update (consume)
```

**Never:**
- Edit files in `~/.pi/agent/git/` directly
- Create hotfix branches in `.pi`
- Copy workshop files to `.pi` as a shortcut

**Always:**
- Develop in workshop
- Commit to workshop repo
- Port functional changes to upstream repo `carlosfrias/pi-cross-node-comms` via git push to `main`
- Verify `pi update` pulls the fix with no specifiers

### RULE 2: TDD for Ansible Playbooks

**Trigger:** Creating or modifying any `.yml` playbook under `ansible/`.  
**Rule:** Every playbook change MUST have corresponding test coverage in `tests/unit/` or `tests/integration/`. Test files follow the naming convention `test-ansible-{category}.sh`.

**Minimum test coverage:**
- `test-ansible-playbook-syntax.sh` — `ansible-playbook --syntax-check` for all playbooks
- Any `when:` clause with `is version()` or nested parentheses → paren balance test
- Any `systemctl is-active` comparison → correct output value test
- Any version pin (e.g., `pi_version_target`) → currency test against npm registry

### RULE 3: Ansible When-Clause Paren Balance

**Trigger:** Writing `when:` conditions with Jinja2 filters, especially `is version()`, `regex_replace()`, or nested boolean groups.  
**Rule:** Every `when:` condition with nested parentheses MUST have balanced open/close parens. Test with `test-ansible-when-clauses.sh`. The specific pattern that bit us:

```yaml
# WRONG — missing closing paren for outer group
when: >
  pi_current.failed or
  (pi_current.stdout is defined and
   pi_current.stdout | length > 0 and
   (pi_current.stdout | regex_replace('^v', '')) is version(pi_version_target, '<'))

# CORRECT — outer group closed
when: >
  pi_current.failed or
  (pi_current.stdout is defined and
   (pi_current.stdout | length > 0 and
   (pi_current.stdout | regex_replace('^v', '')) is version(pi_version_target, '<')))
```

### RULE 4: systemctl Output Values

**Trigger:** Any task that checks systemd service status.  
**Rule:** `systemctl is-active <service>` returns `"active"` on success, NOT `"running"`. Never compare its output to `"running"`. Use `stdout | trim == 'active'` or check `service_status.status.ActiveState == 'active'`.

### RULE 5: Release Pipeline for pi-cross-node-comms

**Trigger:** Making changes to pi-cross-node-comms that need to reach fleet nodes.  
**Rule:** The release pipeline is:

1. **Develop** in `workshop/02-Areas/Infrastructure/pi-cross-node-comms/`
2. **Commit** to workshop monorepo (`carlosfrias/workshop`)
3. **Port** functional changes to upstream repo (`carlosfrias/pi-cross-node-comms`) by copying changed files (paths differ between monorepo and flat repo)
4. **Push** to upstream `main` branch
5. **Consume** via `pi install`/`pi update` in any pi session

The workshop monorepo path is `workshop/02-Areas/Infrastructure/pi-cross-node-comms/ansible/*`. The upstream flat repo path is `ansible/*`. Directory structure differs — always map paths when porting.

### RULE 6: Project-Level AGENTS.md Required

**Trigger:** Creating or significantly modifying a project under `02-Areas/Infrastructure/`.  
**Rule:** Every project MUST have an `AGENTS.md` at its root with: project purpose, status, key files, routing rules, and discovery path. The domain AGENTS.md (`02-Areas/Infrastructure/AGENTS.md`) links to project-level AGENTS.md files.

---

## Key Files

| File | Purpose | Must Be In Sync With |
|------|---------|----------------------|
| `ansible/standup-fleet.yml` | Full fleet standup (6 phases) | Workshop + upstream |
| `ansible/phase2-pi-availability.yml` | Pi agent install/upgrade | Workshop + upstream |
| `ansible/phase5-agent-services.yml` | Systemd agent launch | Workshop + upstream |
| `ansible/deploy-fleet.yml` | Legacy deploy playbook | Workshop + upstream |
| `tests/unit/test-ansible-*.sh` | TDD test suites | Workshop only |
| `tests/integration/test-fleet-standup-integration.sh` | Integration test | Workshop only |
| `FOCUS.md` | Current focus & status | Workshop only |
| `PLAN.md` | Release plan | Workshop only |

## Discovery Path

```
1. workshop/AGENTS.md                              ← Root router
2. workshop/02-Areas/Infrastructure/AGENTS.md       ← Domain router
3. pi-cross-node-comms/AGENTS.md                   ← THIS FILE (project router)
4. pi-cross-node-comms/FOCUS.md                    ← Current state
5. pi-cross-node-comms/PLAN.md                    ← Release plan
```

---

*Created 2026-05-29 — refined from session 2026-05-29-fleet-standup-bugfix*