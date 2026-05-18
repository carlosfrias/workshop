# Quality Checklist

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/quality-checklist.md`

Before considering **any** technical-infrastructure task complete, verify:

## Session Documentation

- [ ] **Document session activity:** capture what changed, write `wiki/operational/status/STATUS-{YYYY-MM-DD-HHMM}.md`, link it in `WIKI.md` Operational Snapshots, update header (`Last Updated` / `Status`), commit and push
- [ ] **Before deleting ephemeral files, audit for scripts to promote:** scan `/tmp/`, home directory, and workspace root for any `.sh`, `.py`, `.service`, `.conf`, `.yml` files created during the session. Relocate anything that should be permanent to `technical-infrastructure/scripts/`, `ansible/roles/`, or the appropriate directory.
- [ ] **Update backlog:** capture incomplete items, deferred work, and next steps with `{YYYY-MM-DD-HHMM}` timestamps in [`wiki/operational/BACKLOG.md`](wiki/operational/BACKLOG.md). Reference new items from the status doc and WIKI.md Backlog section.
- [ ] **Capture session narrative:** when agents produce rich operational output (diagnostic steps, failures, pivots), extract key findings into `wiki/operational/sessions/SESSION-NOTES-{YYYY-MM-DD-HHMM}.md`. Use the [`SESSION-NOTES template`](wiki/templates/SESSION-NOTES-template.md) which includes model performance tracking tables.

## Technical Validation

- [ ] **Document technical work comprehensively** so that it can be done fully without assistance. For scripts: include usage, expected inputs, environment variables. For playbooks: document variables, inventory requirements, expected outcomes.
- [ ] **Test before declaring complete:** validate scripts (bash -n, shellcheck), run `ansible-playbook --syntax-check`, test on a subset of nodes before full deployment, verify output. Testing is co-equal with fixing — not an afterthought. Capture test results in the status doc.
- [ ] **Verify domain activation keywords cover actual vocabulary:** after writing a PLAN or planning work, scan the document for domain-specific terms that are NOT in the Domain Agent File Routing table. If terms are missing, add them before execution begins.
- [ ] **Performance logging is required, not optional:** any framework, script, or system that routes work must log every decision: timestamp, prompt type, model used, latency, cost, quality. Without logs, impact is unmeasurable and improvement is impossible.

## Planning Quality Gates

- [ ] **When creating PLAN documents, specify latency budget per component:** every proposed model call, API request, or script execution must have an estimated latency. If actual latency exceeds 2× the budget during execution, the approach is wrong — pivot immediately.
- [ ] **Budget 20-30% contingency for architectural pivots:** if the first approach fails (model too slow, API incompatible, script doesn't work), budget time to try alternative B. Do not assume the first approach will succeed.
- [ ] **Documentation updates are part of the plan, not afterthoughts:** every session that introduces new terminology, conventions, or workflows must update AGENTS.md, WIKI.md, or the appropriate domain file. Budget 10-15 minutes per session for this.

## Infrastructure Requirements

- [ ] API connectivity confirmed for all affected endpoints
- [ ] Secrets are stored in environment variables or secrets manager, not in code
- [ ] Configuration changes are logged with timestamp
- [ ] Rollback plan documented for any deployment
- [ ] Latency and uptime metrics are within acceptable thresholds
- [ ] **For publishing tasks:** README updated, package.json versioned, local test passed

---

**Related:** [Planning Gates](planning-gates.md) | [Rules](rules.md)
