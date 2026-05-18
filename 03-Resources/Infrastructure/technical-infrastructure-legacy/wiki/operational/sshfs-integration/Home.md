# SSHFS Integration — Operational Home

## [S-TIGHT]

Operational hub for the `sshfs-integration` skill. Links to issue home, plan, package docs, and the 5-step parallel-task workflow.

---

## Status [LOD: Low]

| Item | Value |
|------|-------|
| **Current Phase** | Execution |
| **Last Update** | 2026-05-14 |
| **Next Milestone** | Verify package docs and TDD tests are populated |

---

## Quick Links [LOD: Low]

| Resource | Path | Type |
|----------|------|------|
| Issue Home | [`../issues/sshfs-integration/0-ISSUE.md`](../issues/sshfs-integration/0-ISSUE.md) | Operational |
| Plan | [`../issues/sshfs-integration/1-PLAN.md`](../issues/sshfs-integration/1-PLAN.md) | Operational |
| Architecture | [`../../../packages/sshfs-integration/docs/architecture.md`](../../../packages/sshfs-integration/docs/architecture.md) | Reference |
| TDD Tests | [`../../../packages/sshfs-integration/tests/test-plan.md`](../../../packages/sshfs-integration/tests/test-plan.md) | Reference |
| Integration Guide | [`../../../packages/sshfs-integration/docs/integration-guide.md`](../../../packages/sshfs-integration/docs/integration-guide.md) | Reference |
| Package README | [`../../../packages/sshfs-integration/README.md`](../../../packages/sshfs-integration/README.md) | Reference |

---

## Quick Start [LOD: Medium]

5-step process for running a parallel task:

1. **Ensure mounts**
   ```bash
   ./scripts/ensure-mounted.sh
   ```

2. **Create task descriptor**
   Write a JSON or natural-language descriptor that defines the task, inputs, expected outputs, and target nodes.

3. **Decompose**
   ```bash
   ./src/decompose_task.py --descriptor task.json --output decomposed/
   ```

4. **Route**
   ```bash
   ./scripts/route-tasks.sh --decomposed-dir decomposed/ --nodes lab1,lab2
   ```

5. **Collect**
   ```bash
   ./scripts/collect-results.sh --job-id $(cat decomposed/job-id.txt)
   ```

---

## Active Sessions [LOD: Low]

> **Placeholder.** No active session logs yet.

Capture session notes under [`../issues/sshfs-integration/sessions/`](../issues/sshfs-integration/sessions/).

---

## Test Status [LOD: Low]

> **Placeholder.** No test results recorded yet.

Results will be posted under:
- [`../issues/sshfs-integration/tests/`](../issues/sshfs-integration/tests/)
- [`../../../packages/sshfs-integration/tests/test-plan.md`](../../../packages/sshfs-integration/tests/test-plan.md)

---

## Known Issues [LOD: Low]

> **Placeholder.** No known issues recorded yet.

If issues surface, document them in [`../issues/sshfs-integration/troubleshooting/`](../issues/sshfs-integration/troubleshooting/) and link here.

---

## Related Issues [LOD: Low]

| Issue | Relationship |
|-------|-------------|
| **TI-038** | Dependency — tracks parallel-work orchestration enablement (see issue home when filed) |
| **TI-033** | Related — [`../issues/ti033-lab-sshfs-mount/`](../issues/ti033-lab-sshfs-mount/) lab SSHFS mount configuration |

---

*Navigation: [Operational Index](../index.md) · [Technical Infrastructure Index](../../../index.md)*
