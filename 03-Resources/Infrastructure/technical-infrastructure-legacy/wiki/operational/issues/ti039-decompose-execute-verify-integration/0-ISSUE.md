# TI-039: Decompose-Execute-Verify v2.1 — Intercom, SSHFS, and Doc-Standards Core Prompt Integration

**Issue ID:** ti039-decompose-execute-verify-integration
**Status:** ✅ COMPLETE
**Priority:** 🔴 HIGH
**Created:** 2026-05-14
**Owner:** Technical Infrastructure

---

## [S-TIGHT]
Integrate intercom-coord-workflow, sshfs-integration, and doc-standards as core behavioral prompts into decompose-execute-verify so realtime cross-session/cross-node communication, automatic parallel filesystem orchestration, and LOD documentation standards become automatic behaviors.

---

## Objective
Integrate the specified core behaviors (Intercom, SSHFS, Doc-Standards) into the `decompose-execute-verify` framework to enable seamless orchestration across local lab nodes and professional documentation standards.

---

## Acceptance Criteria
- [x] `agents/decomposer.md` updated with intercom, SSHFS, and doc-standards core prompts
- [x] `agents/verifier.md` updated with intercom reporting, SSHFS evidence collection, and doc-standards verification
- [x] New chain: `decomposed-intercom-dispatch.chain.md`
- [x] `SKILL.md` updated with integrated patterns per doc-standards LOD
- [x] `ARCHITECTURE.md` updated with cross-node execution flow diagrams
- [x] Full 15-component plan assembled per `master-assembly-guide.md`
- [x] Running questions list maintained in `QUESTIONS.md` — all 8 answered
- [x] Complete end-to-end workflow validated (decomposer + verifier functional, chain discoverable via TUI `/chain`) — smoke test passed 2026-05-14
- [x] Auto-documentation agent integrated — `agents/auto-documenter.md` writes LOD-compliant session notes on every chain invocation — completed 2026-05-14
- [x] Programmatic chain invocation — `scripts/run-decomposed-intercom-dispatch.sh` enables non-interactive bash/cron execution — completed 2026-05-14
- [x] Orchestrator health gate — `health-monitor` step prevents cloud decomposer when stressed — completed 2026-05-14
- [x] Cost persistence — `scripts/cost-logger.py` tracks per-run model costs in JSONL — completed 2026-05-14
- [x] Decision log auto-population — `scripts/decision-logger.py` captures routing choices — completed 2026-05-14

---

## References
1. `~/.pi/agent/git/github.com/carlosfrias/decompose-execute-verify/skills/decompose-execute-verify/SKILL.md`
2. `/Users/friasc/Dropbox/workshop/technical-infrastructure/packages/sshfs-accessible/skills/sshfs-accessible/SKILL.md`
3. `/usr/local/lib/node_modules/pi-intercom/skills/pi-intercom/SKILL.md`
4. `/Users/friasc/.pi/agent/git/github.com/carlosfrias/doc-standards/skills/doc-standards/SKILL.md`
5. `/Users/friasc/Dropbox/workshop/technical-infrastructure/wiki/templates/master-assembly-guide.md`

---

## Related Issues
- None.

---

*This issue follows the issue-centric documentation standard. All work for this issue lives in this folder.*
