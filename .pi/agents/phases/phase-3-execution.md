# Phase 3: Execution (Core Index)

**Purpose:** Must Always / Must Never rules, core working standards, and safety.
**When to load:** During active work — file edits, commands, deployments.
**Target model:** qwen3:8b

---

## Core Working Standards

- **Chunked Execution:** Work in small, testable blocks with tight supervision. Create one script, validate syntax, report before proceeding. Provide concise status updates after each chunk.
- **Parallelization:** Minimize user decisions. Parallelize independent tasks concurrently and report results together.
- **Quick Capture:** Store emergent ideas without interrupting flow:
  - **Recommendations** (`wiki/recommendations/RECOMMENDATION-{YYYY-MM-DD-HHMM}.md`)
  - **Planning** (`wiki/operational/planning/PLAN-{YYYY-MM-DD-HHMM}.md`)
- **Permanent File Placement:** Create scripts in their permanent location immediately. Never leave operational scripts in `/tmp/` before cleanup.
- **Automation Preference:** Technical work must be automated in re-usable scripts, with a preference for Ansible integrated into the project collection.

## General Conventions

- All hostnames and endpoints documented in lowercase.
- Latency in milliseconds (ms), uptime as percentage.
- Configuration changes must be tracked with timestamp and author.
- Use environment variables for secrets — **never hardcode credentials**.
- Structured, machine-parseable outputs are preferred.
- **Python environment:** Always check the project root for `.venv`; activate it and ensure Python 3.14.4 is used.

## Rules

### Must Always
- Verify API connectivity before executing any dependent operation.
- Log all configuration changes with before/after state.
- **Test scripts and playbooks immediately after creating/fixing** (syntax checks $\rightarrow$ dry-run $\rightarrow$ execute).
- Test in a staging environment before production deployment.
- Monitor latency thresholds and alert on breaches.
- Document every integration endpoint and authentication method.
- **Publish with semantic versioning** (major.minor.patch) and test locally first.
- **Follow the Quality Checklist** as the authoritative completion criteria.
- **Load the `doc-standards` skill AND the vault-native taxonomy mapping** before creating, editing, or reviewing ANY `.md` file. (`/Users/friasc/.pi/agent/git/github.com/carlosfrias/doc-standards/skills/doc-standards/SKILL.md` + `/Users/friasc/Cloud/carlos-desktop/personal-vault/01-Projects/Carlos-Trading-Desk/archive/Doc-Standards Vault Taxonomy.md`) If the task involves documentation, the skill overrides general conventions.

### Must Never
- Store API keys or secrets in plain text.
- Deploy untested changes to production infrastructure.
- Ignore connectivity alerts or latency degradation.
- Run infrastructure changes without a rollback plan.
- Assume a service is healthy without verifying.
- **Publish without updating README.md**.
- **Break backward compatibility without a major version bump**.
- **Write, edit, or review any `.md` file without first loading the `doc-standards` skill.**

---

## Specialized Modules

Depending on the task, load the following specialized modules for detailed tooling and hardware rules:

| Module | File | Keywords |
|---------|------|----------|
| **Ansible/Vault** | `phase-3-ansible.md` | ansible, vault, playbook, encrypt, sudo |
| **Orchestrator/Mac** | `phase-3-orchestrator.md` | orchestrator, mac, m4, models.json, health-check |

---

## Next Phase

After work is complete, load **Phase 4: Quality Check** (`phase-4-quality-check.md`).
