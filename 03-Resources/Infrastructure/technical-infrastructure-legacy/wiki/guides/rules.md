# Technical Infrastructure Rules

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/rules.md`

## Must Always

- Verify API connectivity before executing any dependent operation
- Log all configuration changes with before/after state
- **Test scripts and playbooks immediately after creating or fixing them** — run `bash -n`, `ansible-playbook --syntax-check`, or execute on one node before mass deployment. Testing is co-equal with authoring, not an afterthought.
- Test in a staging environment before production deployment
- Monitor latency thresholds and alert on breaches
- Document every integration endpoint and authentication method
- **Publish with semantic versioning** — major.minor.patch
- **Test locally before publishing** — install in trading-workspace first
- **Follow the Quality Checklist before completing any task**

## Must Never

- Store API keys or secrets in plain text or code
- Deploy untested changes to production infrastructure
- Ignore connectivity alerts or latency degradation
- Run infrastructure changes without a rollback plan
- Assume a service is healthy without verifying
- **Publish without updating README.md** — installation instructions must be current
- **Break backward compatibility without a major version bump**

---

**Related:** [Quality Checklist](quality-checklist.md) | [Conventions](conventions.md)
