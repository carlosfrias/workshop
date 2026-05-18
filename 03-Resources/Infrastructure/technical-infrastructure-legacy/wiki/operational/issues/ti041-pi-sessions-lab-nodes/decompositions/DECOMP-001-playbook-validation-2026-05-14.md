# DECOMP-001: Validate TI-041 Playbooks Before Execution

**Date:** 2026-05-14  
**Decomposed by:** Plan Owner (kimi-k2.6)  
**Trigger:** Orchestrator selected Option A — validate before execute  
**Framework:** TI-039 Decompose-Execute-Verify

---

## Why This Decomposition Exists

**Technical debt discovered:** Playbooks were authored by Plan Owner (this session) rather than by lab node models. They have not been validated on the actual target hosts.

**Goal:** Before executing any production playbook, run a validation sub-task on a representative lab node. The node-side model reviews playbook syntax and identifies host-specific issues.

---

## Sub-Task Definition

### Sub-Task: `playbook-validate-check`

**Complexity:** Low (syntax check + static analysis)  
**Assignee:** Medium-Local Model (`gemma4:e4b`) on preferred node (fnet3 — highest RAM, most stable)  
**Duration:** ~15 minutes  
**Expected output:** JSON report per playbook

---

## Task JSON

```json
{
  "task_id": "ti041-decomp-001-playbook-validate",
  "framework": "TI-039",
  "phase": "pre-flight validation",
  "dispatcher": "orchestrator",
  "target": "fnet3",
  "model": "ollama/gemma4:e4b",
  "rationale": "fnet3 has 31GB RAM, stable pi 0.74.0, Node.js v20. Representative for most playbooks.",
  "steps": [
    {
      "step_id": "1",
      "description": "Checkout workspace files via SSHFS mount",
      "command": "ls /mnt/orchestrator/technical-infrastructure/ansible/playbooks/",
      "evidence": "directory listing"
    },
    {
      "step_id": "2",
      "description": "Ansible syntax check all TI-041 playbooks",
      "command": "ansible-playbook --syntax-check -i /mnt/orchestrator/technical-infrastructure/ansible/inventory.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/deploy-pi.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/verify-pi.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/check-node-version.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/verify-intercom.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/configure-pi-service.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/restart-pi-service.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/test-auto-restart.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/test-full-chain.yml",
      "evidence": "stdout showing PASS or FAIL per playbook"
    },
    {
      "step_id": "3",
      "description": "Identify node-specific risks",
      "analysis": [
        "Check `hosts: lab_nodes` vs inventory group",
        "Check `become: yes` and sudo availability",
        "Check template file paths exist on target",
        "Check Node.js version detection works on Ubuntu 24.04",
        "Check `pi --version` path consistency"
      ],
      "evidence": "written report markdown"
    },
    {
      "step_id": "4",
      "description": "Run `ansible-playbook --check` on deploy-pi playbook",
      "command": "ansible-playbook --check -i /mnt/orchestrator/technical-infrastructure/ansible/inventory.yml /mnt/orchestrator/technical-infrastructure/ansible/playbooks/deploy-pi.yml",
      "evidence": "JSON stdout with predicted changes"
    }
  ],
  "expected_output_format": "json",
  "required_fields": [
    "node_id",
    "syntax_check_status",
    "playbooks_checked",
    "playbooks_passed",
    "playbooks_failed",
    "risk_level",
    "recommendations"
  ]
}
```

---

## Dispatch Instructions for Orchestrator

1. **Invoke decomposer** with the task JSON above
2. **Node Registry** routes to fnet3 (highest capacity, stable)
3. **Verfier** checks JSON has all required fields
4. **Report back to Plan Owner** with:
   - Which playbooks passed syntax-check
   - Which playbooks need fixes
   - Risk level (LOW / MEDIUM / HIGH)
   - Recommendations before production execution

---

## After Validation — Decision Matrix

| Validator Result | Plan Owner Action |
|-----------------|-------------------|
| All playbooks PASS, risk LOW | Approve Phase 1 execution as-is |
| 1–2 playbooks FAILED, risk MEDIUM | Decompose fix task (DECOMP-002) |
| >2 playbooks FAILED or risk HIGH | Halt Phase 1, decomp full rewrite |

---

## Evidence Standard

Every claim ("playbook works") must be backed by:
- `ansible-playbook --syntax-check` output showing `syntax: ok`
- `--check` mode output showing predictable changes
- Node-specific analysis written by the lab node model

No human-interpreted stdout. Only structured JSON evidence.

---

*Decomposed by Plan Owner. Awaiting orchestrator dispatch via TI-039 framework.*
