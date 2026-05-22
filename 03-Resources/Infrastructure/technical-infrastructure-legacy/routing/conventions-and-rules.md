# Conventions and Rules

**Section ID:** conventions-and-rules  
**Size:** ~2KB  
**LOD:** Low  
**Purpose:** Behavioral conventions, mandatory rules, and prohibited actions for technical infrastructure work.

---

## [S-TIGHT]

Technical infrastructure follows strict conventions (lowercase hostnames, ms latency, percentage uptime, env vars for secrets) and two rule sets: Must Always (verify connectivity, log changes, test before deploy, semantic versioning) and Must Never (no hardcoding secrets, no untested prod deploys, no changes without rollback plans). Low-capacity models: load this section for any infrastructure task.

---

## Conventions

- All hostnames and endpoints documented in lowercase
- All latency measurements in milliseconds (ms)
- All uptime as percentage
- Configuration changes must be tracked with timestamp and author
- Use environment variables for secrets — never hardcode credentials
- All outputs should be structured and machine-parseable where possible
- Seek the `.venv` in the project root folder and if found, then activate it
- Python 3.14.4 is the target version for `.venv`

## Must Always

[LOD: Low] — These are hard constraints, not suggestions.

- **Verify TI-011 orchestration framework is operational before any multi-node or infrastructure work** (see [Framework Readiness Check](./framework-readiness.md))
- **Include orchestrator node (Mac) in infrastructure fixes** — when fixing model configs, caches, or extensions on lab nodes, apply the same fix to the orchestrator. See `AGENTS-full.md` Orchestrator Node Conventions.
- Verify API connectivity before executing any dependent operation
- Log all configuration changes with before/after state
- Test scripts and playbooks immediately after creating or fixing them
- Test in a staging environment before production deployment
- Monitor latency thresholds and alert on breaches
- Document every integration endpoint and authentication method
- Publish with semantic versioning (major.minor.patch)
- Test locally before publishing
- Follow the [Quality Checklist](./quality-and-readiness.md) before completing any task

## Must Never

[LOD: Low] — These are hard prohibitions.

- **Execute multi-node infrastructure work without routing through TI-011** (classify → decompose → submit → collect). Direct SSH to nodes from the orchestrator is only for framework bootstrap or single-node emergencies.
- Store API keys or secrets in plain text or code
- Deploy untested changes to production infrastructure
- Ignore connectivity alerts or latency degradation
- Run infrastructure changes without a rollback plan
- Assume a service is healthy without verifying
- Publish without updating README.md
- Break backward compatibility without a major version bump

---

*Load [quality-and-readiness.md](./quality-and-readiness.md) for the quality checklist and TI-011 framework readiness check.*