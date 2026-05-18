# TI-039 Open Questions

## Q1: Workspace vs. SSHFS Path Canonicality
**ANSWER (2026-05-14):** `/mnt/trading-desk/` (SSHFS-mounted workspace) is canonical for all file operations during task execution. Lab nodes read/write through the mounted workspace. If a package needs editing (e.g., `decompose-execute-verify`), edits are made on the orchestrator's workspace copy and propagated via SSHFS. Lab nodes do NOT SSH back to edit `~/.pi/agent/git/`.

## Q2: Version Strategy
**ANSWER (2026-05-14):** v2.1 — backward-compatible additions. Existing agents (`decomposer`, `verifier`) were extended with new sections (SSHFS, LOD, Intercom) without modifying their core interface or breaking existing chains. No wrapper agents were created.

## Q3: "Core Prompt" Definition
**ANSWER (2026-05-14):** Core prompt means modifying the existing `systemPrompt` block. We appended sections to `agents/decomposer.md` (SSHFS Integration Protocol, Doc-Standards LOD Enforcement, Intercom Coordination Protocol) and `agents/verifier.md` (SSHFS Evidence Collection, Doc-Standards LOD Verification, Intercom Coordination) without creating wrapper agents.

## Q4: SSHFS Auto-Verification Policy
**ANSWER (2026-05-14):** Auto-verify before every dispatch. The `SSHFS Integration Protocol` in `agents/decomposer.md` mandates that any plan dispatching to lab nodes includes mount verification as the first sub-task. The 1s latency is acceptable given the reliability gain. The new chain `decomposed-intercom-dispatch` explicitly includes `sshfs-accessible` verification as Step 1.

## Q5: Intercom Auto-Dispatch vs. Status-Only
**ANSWER (2026-05-14):** Auto-dispatch. The new chain `decomposed-intercom-dispatch` includes explicit `orchestrator` steps for dispatching sub-tasks to named lab node sessions via `intercom({ action: "ask", ... })`. The orchestrator handles both dispatch and status collection.

## Q6: ti011_node_registry.py Integration
**ANSWER (2026-05-14):** Static node map for now. The lab node dispatch rules use `nodes.json` from `sshfs-accessible` package. Dynamic `ti011_node_registry.py` integration is a Phase 2 enhancement tracked as open backlog item.

## Q7: Doc-Standards Scope
**ANSWER (2026-05-14):** BOTH. LOD enforcement applies to decomposition plans (via `agents/decomposer.md`'s `Output Verification Checklist`) AND skill documentation (via new subsections in SKILL.md and ARCHITECTURE.md). The decomposer now requires [S-TIGHT] summaries and LOD markers on all sub-tasks.

## Q8: Lab Node Session Pre-Provisioning
**ANSWER (2026-05-14):** No existing pi sessions on lab nodes. Intercom is same-machine only. For true cross-node coordination, the framework must either (a) spawn pi sessions via SSH on demand, or (b) use the SSHFS-mounted workspace for file-based coordination with scripted dispatch. The current implementation uses (b) for this session; (a) is a future infrastructure requirement.
