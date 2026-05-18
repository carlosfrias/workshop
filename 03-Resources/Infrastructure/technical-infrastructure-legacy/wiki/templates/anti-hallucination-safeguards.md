# Anti-Hallucination Safeguards

**Template ID:** COMP-002  
**Extracted from:** `1-PLAN.md` Section "Anti-Hallucination Safeguards"  
**Use in:** Any plan where local models execute code and report completion.

---

Local models are prone to hallucinating success. The following safeguards apply to all execution:

1. **{{EVIDENCE_TYPE_1}}.** A local model must not report a step as complete without providing:
   - Test command output showing pass/fail counts.
   - File diff (`git diff --stat`) of changed files.
   - Lab Node verification for integration/acceptance layers.
2. **{{VERIFIER_ROLE}}.** The low cloud model re-runs tests independently to confirm pass counts before accepting any completion claim.
3. **{{NO_SUCCESS_WITHOUT_GREEN}}.** A completion claim is **invalid** unless all new tests were initially failing (RED confirmed) and now pass (GREEN confirmed), and the verifier confirms the pass.
4. **{{REJECT_MISSING_EVIDENCE}}.** If a local model claims success without test evidence, the low cloud model must reject the claim, re-run tests, and either return for correction or escalate.

For full safeguard procedures, see [`{{AGENTS_MD_PATH}}`](./{{AGENTS_MD_PATH}}).

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{EVIDENCE_TYPE_1}}` | Name of primary evidence requirement | `Test Evidence Required` |
| `{{VERIFIER_ROLE}}` | Who verifies test claims | `Verifier Pattern` |
| `{{NO_SUCCESS_WITHOUT_GREEN}}` | Rule about green tests | `No Success Without Green Tests` |
| `{{REJECT_MISSING_EVIDENCE}}` | Action when evidence is missing | `Reject Missing Evidence` |
| `{{AGENTS_MD_PATH}}` | Path to AGENTS.md for full protocol | `AGENTS.md` |
