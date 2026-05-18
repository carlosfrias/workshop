# Phase 4: Quality Check

**Purpose:** Verify work against checklist before declaring task complete.
**When to load:** After work completes, before reporting success.
**Target model:** gemma4:e4b

---

### Quality Gates Before Publishing

- [ ] Extension/skill works in isolation (no workspace-specific dependencies)
- [ ] README.md includes installation instructions for all three stages
- [ ] package.json has correct name, version, repository, and license
- [ ] Config files use namespaced paths (e.g., `.pi/keyword-router.json` not `.pi/model-router.json`)
- [ ] Keybinding namespaces are unique (e.g., `keywordRouter.*` not `modelRouter.*`)
- [ ] Event names are namespaced (e.g., `keyword-router:ready` not `model-router:ready`)

### Testing After Every Change

**After modifying any script or playbook, the next action in the same session must be testing it.**

| What changed | Test to run |
|-------------|-------------|
| Bash script | `bash -n script.sh` (syntax), then execute |
| Python script | `python3 -m py_compile script.py`, then execute |
| Ansible playbook | `--syntax-check`, then `--check`, then live with `-vvv` if issues |
| SSH config | `ssh -v HOSTNAME "hostname"` |
| Inventory file | `ansible-inventory -i inventory.yml --graph` |

**Session integration**: Playbooks, scripts, and their tests are authored and validated in a single working session. Do not defer testing to a future session — context is lost and issues go undetected.

## Quality Checklist

Before considering **any** technical-infrastructure task complete, verify:

- [ ] **Document session activity:** capture what changed, write `wiki/operational/status/STATUS-{YYYY-MM-DD-HHMM}.md`, link it in `WIKI.md` Operational Snapshots, update header (`Last Updated` / `Status`), commit and push
- [ ] **Before deleting ephemeral files, audit for scripts to promote:** scan `/tmp/`, home directory, and workspace root for any `.sh`, `.py`, `.service`, `.conf`, `.yml` files created during the session. Relocate anything that should be permanent to `technical-infrastructure/scripts/`, `ansible/roles/`, or the appropriate directory. This is the most common cause of lost work.
- [ ] **Update backlog:** capture incomplete items, deferred work, and next steps with `{YYYY-MM-DD-HHMM}` timestamps in [`wiki/operational/BACKLOG.md`](wiki/operational/BACKLOG.md). Reference new items from the status doc and WIKI.md Backlog section.
- [ ] **Capture session narrative:** when agents produce rich operational output (diagnostic steps, failures, pivots), extract key findings into `wiki/operational/sessions/SESSION-NOTES-{YYYY-MM-DD-HHMM}.md`. Use the [`SESSION-NOTES template`](wiki/templates/SESSION-NOTES-template.md) which includes model performance tracking tables. Reference from the status doc's Session Narrative section with a one-paragraph summary and a link. One narrative per major task.
- [ ] **Document technical work comprehensively** so that it can be done fully without assistance. For scripts: include usage, expected inputs, environment variables. For playbooks: document variables, inventory requirements, expected outcomes.
- [ ] **Test before declaring complete:** validate scripts (bash -n, shellcheck), run `ansible-playbook --syntax-check`, test on a subset of nodes before full deployment, verify output. Testing is co-equal with fixing — not an afterthought. Capture test results in the status doc.
- [ ] **When creating PLAN documents, specify latency budget per component:** every proposed model call, API request, or script execution must have an estimated latency. If actual latency exceeds 2× the budget during execution, the approach is wrong — pivot immediately, do not power through.
- [ ] **Budget 20-30% contingency for architectural pivots:** if the first approach fails (model too slow, API incompatible, script doesn't work), budget time to try alternative B. Do not assume the first approach will succeed.
- [ ] **Verify domain activation keywords cover actual vocabulary:** after writing a PLAN or planning work, scan the document for domain-specific terms that are NOT in the Domain Agent File Routing table. If terms are missing, add them before execution begins. Silent domain failures cost more than explicit keyword gaps.
- [ ] **Performance logging is required, not optional:** any framework, script, or system that routes work must log every decision: timestamp, prompt type, model used, latency, cost, quality. Without logs, impact is unmeasurable and improvement is impossible.
- [ ] **Documentation updates are part of the plan, not afterthoughts:** every session that introduces new terminology, conventions, or workflows must update AGENTS.md, WIKI.md, or the appropriate domain file. Budget 10-15 minutes per session for this. Undocumented conventions are lost conventions.
- [ ] API connectivity confirmed for all affected endpoints
- [ ] Secrets are stored in environment variables or secrets manager, not in code
- [ ] Configuration changes are logged with timestamp
- [ ] Rollback plan documented for any deployment
- [ ] Latency and uptime metrics are within acceptable thresholds
- [ ] **For publishing tasks:** README updated, package.json versioned, local test passed


## Next Phase

After quality check passes, load **Phase 5: Documentation** (`phase-5-documentation.md`).
