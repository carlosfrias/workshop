## Prompt Capture — TI-038 Initiation

**Timestamp:** 2026-05-14 15:15:00 US Eastern
**Issue:** TI-038
**Session:** Initial planning and backlog creation

---

### Original Prompt (Verbatim)

> I want to integrate the sshfs-accessible skill into the orchestration framework so that a model that is required to do file system work can mount a file system across the lab nodes and decompose the work so it can be done in parallel. I want this to be carried out as a part of core functionality that does not need to be prompted but that if the context, need or logic determines that it would best serve a task to use the sshfs that it would simply be used. Create a backlog issue that contains a plan to create this integration skill. Follow doc-standards and routing to lab all work. Use sshfs if needed so you perform no work on this node except for what absolutely necessary. You can now mount a folder from this node with sshfs and have a lab node work on this node. Prepare the documents with diagrams and comprehensive explanations the describe the architecture, approach and implementation following TDD to ensure that low local lab nodes don't hallucinate. Code workspace is technical-infrastructure/packages/sshfs-integration/. Document workspace: technical-infrastructure/wiki/operational/sshfs-integration.

---

### Key Requirements Extracted

1. **Automatic integration** — No manual prompting; framework detects when SSHFS parallelization benefits a task
2. **Core functionality** — Not an optional add-on; part of the orchestration framework
3. **Detection heuristic** — Context/need/logic determines when to use SSHFS
4. **Decomposition** — Split filesystem work across lab nodes automatically
5. **Parallel execution** — Route sub-tasks to mounted nodes
6. **TDD-first** — Tests written before code to prevent low-capacity model hallucinations
7. **Comprehensive documentation** — Architecture diagrams, approach docs, implementation plan
8. **Lab-node delegation** — Use sshfs-mounted workspace to distribute work to lab nodes
9. **Doc-standards compliance** — All markdown files follow S-TIGHT, LOD, and structural rules
10. **Code workspace:** `technical-infrastructure/packages/sshfs-integration/`
11. **Document workspace:** `technical-infrastructure/wiki/operational/sshfs-integration/`

---

### Lessons

- **Decomposition is critical for TDD:** When low-capacity models write code, giving them a test plan first (red phase) prevents hallucination. The test-plan.md was written before any code scripts.
- **SSHFS mount verification before delegation:** Some lab nodes were unmounted at session start. Always run `ensure-mounted.sh` before dispatching work that depends on mounted paths.
- **Path precision matters:** Early agents wrote files to a relative `mnt/trading-desk/` directory instead of the actual workspace. Explicit absolute paths in prompts prevent this.
- **Parallel agent execution saves time:** Running 3–4 documentation agents simultaneously reduced wall-clock time by ~60% versus sequential execution.
- **Bash syntax checks are fast wins:** All 4 scripts passed `bash -n` immediately. Enforcing this on every script before declaring done catches structural errors.
- **Doc-standards S-TIGHT headers enable low-model consumption:** Every document begins with a 1-sentence summary, allowing qwen3.5:4b to stop there unless deeper context is needed.

---

### Related Files

- Issue Home: `../0-ISSUE.md`
- Plan: `../1-PLAN.md`
- Code Package: `../../../../packages/sshfs-integration/`
