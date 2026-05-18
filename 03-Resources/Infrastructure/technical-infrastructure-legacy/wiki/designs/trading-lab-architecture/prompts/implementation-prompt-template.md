# Trading Lab Implementation Prompt Template

Use this prompt to begin implementation once prerequisite questions are answered and Phase 0 (network remediation) is complete.

---

## Prompt for Implementation Agent

```markdown
You are implementing a distributed multi-agent architecture for a 7-node trading lab cluster.

## Context

Read these documents first:
1. `/Users/friasc/Dropbox/agent-workspace/trading-lab-architecture/DESIGN.md` — Full architecture design
2. `/Users/friasc/Dropbox/agent-workspace/trading-lab-architecture/README.md` — Quick start guide

## Current State

**Network Status**:
- Online nodes: [FILL IN: e.g., 01, 02, 04, 05]
- Offline nodes: [FILL IN: e.g., 03, 06, 07 — reason if known]
- All nodes reachable via SSH: [YES/NO]

**Hardware Summary**:
[FILL IN table or summary of RAM/CPU/GPU per node]

**Answers to Prerequisite Questions**:
- Q1 (why offline): [ANSWER]
- Q2 (topology): [ANSWER]
- Q3 (reachability): [ANSWER]
- Q4 (hardware): [ANSWER]
- Q5 (Ollama capable): [ANSWER]
- Q6 (symmetric vs hierarchical): [ANSWER]
- Q7 (workload type): [ANSWER]
- Q8 (SSH auth): [ANSWER]
- Q9 (internet access): [ANSWER]
- Q10 (uptime requirements): [ANSWER]
- Q11 (failure handling): [ANSWER]
- Q12 (dashboard needed): [ANSWER]

## Your Task

Implement Phase [FILL IN: 1-6] of the trading-lab architecture as described in DESIGN.md.

### Phase [X] Deliverables

[FILL IN specific deliverables from the phase you're implementing]

Example for Phase 1:
- Create `scripts/trading-lab-node-setup.sh` — Automated setup script for all nodes
- Create `configs/node-settings.template.json` — Configuration template
- Test connectivity to all online nodes
- Document installation process

### Constraints

- All 7 nodes must have unique session names (node-01 through node-07)
- Use SSH key-based authentication
- Support both online and offline node scenarios
- Follow patterns from decomposition-skill and local-model-pilot
- Log all actions to bookkeeping system

### Success Criteria

[FILL IN success criteria for the phase you're implementing]

Example for Phase 1:
- [ ] Setup script runs successfully on all online nodes
- [ ] pi installed with intercom and model-router extensions
- [ ] Each node has unique session name configured
- [ ] Orchestrator can list all connected nodes via `intercom list`
- [ ] Configuration documented in `trading-lab-architecture/IMPLEMENTATION.md`

### Available Tools

- `bash` — Execute commands on local machine and remote nodes via SSH
- `read`/`write`/`edit` — Create and modify configuration files
- `subagent` — Delegate to specialized agents (decomposer, verifier, etc.)
- `intercom` — Coordinate with other pi sessions (once set up)

### Output Format

Produce:
1. Implementation report with what was done
2. Scripts and configuration files created
3. Test results (connectivity, basic task dispatch)
4. Issues encountered and how resolved
5. Next steps for subsequent phase

---

## Instructions

1. Read DESIGN.md completely before starting
2. Confirm you understand the architecture and phase goals
3. Ask clarifying questions if any answers to Q1-Q12 are unclear
4. Execute the implementation systematically
5. Document everything in `trading-lab-architecture/IMPLEMENTATION.md`
6. Test thoroughly before marking phase complete

Begin by reading the design documents and confirming your understanding.
```

---

## How to Use This Template

1. **Copy this file** to a new prompt file (e.g., `implement-phase-1.prompt.md`)
2. **Fill in the bracketed sections** with current state and answers
3. **Specify which phase** you want to implement
4. **Run with pi** using the `/run` command or paste into a new session

### Example Usage

```bash
# Create a filled-in prompt
cp trading-lab-architecture/prompts/implementation-prompt.md \
   trading-lab-architecture/prompts/implement-phase-1.md

# Edit with your answers (use your editor)
nano trading-lab-architecture/prompts/implement-phase-1.md

# Run with pi
pi run trading-lab-architecture/prompts/implement-phase-1.md
```

---

## Prompt Variants

### For Phase 0 (Network Remediation)

```markdown
You are diagnosing network connectivity issues on 3 offline trading-lab nodes.

## Task

Diagnose why nodes 03, 06, 07 are unreachable from the orchestrator.

## Available Information

- Orchestrator IP: [FILL IN]
- Expected node IPs: [FILL IN]
- Network topology: [FILL IN]
- Physical access: [YES/NO — who can access?]

## Steps

1. Document current network configuration from orchestrator
2. If physical access available:
   - Check cable connections
   - Verify NIC status: `ip link`, `ethtool`
   - Check IP configuration: `ip addr`, `ip route`
   - Test local connectivity: `ping gateway`, `ping orchestrator`
3. If remote access via alternative path:
   - SSH via management network
   - Check firewall rules: `iptables -L`, `ufw status`
   - Verify SSH service: `systemctl status sshd`
4. Document findings and recommended fixes

## Output

- Root cause analysis for each offline node
- Remediation steps (with commands)
- Prevention recommendations
```

### For Phase 3 (Agent Definitions)

```markdown
You are creating agent definitions for the trading-lab architecture.

## Task

Create the following agent definition files:
1. `agents/trading-lab-worker.md` — Worker agent for each node
2. `agents/trading-lab-orchestrator.md` — Orchestrator agent
3. `chains/trading-lab-task-dispatch.chain.md` — Task dispatch workflow

## Requirements

- Worker agents must:
  - Listen for intercom messages from orchestrator
  - Execute tasks using local model-router
  - Reply with structured results
  - Handle errors gracefully

- Orchestrator agent must:
  - Dispatch tasks to specific nodes or broadcast
  - Track task status in bookkeeping ledger
  - Handle offline node scenarios
  - Aggregate results from multiple nodes

## Reference

See DESIGN.md Appendix B for configuration templates.

## Output

- Three agent/chain definition files
- Usage examples
- Test plan for validating agents work correctly
```

---

**Version**: 1.0  
**Date**: 2026-04-24
