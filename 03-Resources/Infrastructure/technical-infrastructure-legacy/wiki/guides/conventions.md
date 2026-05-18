# Technical Infrastructure Conventions

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/conventions.md`

## Standard Conventions

- All hostnames and endpoints documented in lowercase (e.g., `api.broker.example.com`)
- All latency measurements in milliseconds (ms)
- All uptime as percentage (e.g., 99.95%)
- Configuration changes must be tracked with timestamp and author
- Use environment variables for secrets — never hardcode credentials
- All outputs should be structured and machine-parseable where possible
- Seek the `.venv` in the project root folder and if found, then activate the `.venv`
- Python 3.14.4 is the target version for `.venv`

## Execution Conventions

- **Work in chunked blocks with tight supervision and frequent feedback.** When executing complex or multi-step tasks, break work into small, testable chunks. After each chunk, provide a concise status update: what changed, what was verified, and what's next.
- **When given multiple tasks, parallelize if they're independent.** Minimize user decisions by examining whether tasks have actual dependencies or can run concurrently.
- **Capture emergent ideas without interrupting flow** — follow the guidelines defined in the `project-documentation-standards` skill for creating Recommendations and Planning files.
- **Script Location**: Scripts must be created in their permanent location immediately. Follow the standards in the `project-documentation-standards` skill regarding ephemeral storage.
- Technical work is automated and stored in re-usable scripts with a preference toward Ansible when appropriate.

---

**Related:** [Quality Checklist](quality-checklist.md) | [Rules](rules.md)
