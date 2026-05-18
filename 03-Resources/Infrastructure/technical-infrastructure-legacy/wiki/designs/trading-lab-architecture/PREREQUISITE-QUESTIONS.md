# Trading Lab Prerequisite Questions — Answer Sheet

Use this document to capture answers to the prerequisite questions before implementation can begin.

**Instructions**: Fill in your answers below. Be as specific as possible — vague answers will cause delays during implementation.

---

## Network & Connectivity

### Q1: Why are nodes 03, 06, 07 offline?

**Diagnosis**: [FILL IN]

**Root cause** (check all that apply):
- [ ] Network misconfiguration (wrong IP, subnet, gateway)
- [ ] Physical connectivity (cable unplugged, switch port dead)
- [ ] OS/driver issues (network driver failed, interface down)
- [ ] Intentional air-gap for security
- [ ] Hardware failure (NIC dead, motherboard issue)
- [ ] Unknown — need to diagnose

**Details**:
```
[Describe what you know about each offline node]

Node 03: 
Node 06:
Node 07:
```

**Remediation plan**:
```
[What needs to be done to bring each node online]
```

---

### Q2: What is the network topology?

**Orchestrator machine**:
- IP address: _______________
- Subnet mask: _______________
- Gateway: _______________
- Hostname: _______________

**Trading lab nodes**:

| Node | IP Address | Subnet Mask | Gateway | Hostname | Notes |
|------|------------|-------------|---------|----------|-------|
| 01   |            |             |         |          |       |
| 02   |            |             |         |          |       |
| 03   |            |             |         |          | offline |
| 04   |            |             |         |          |       |
| 05   |            |             |         |          |       |
| 06   |            |             |         |          | offline |
| 07   |            |             |         |          | offline |

**Network layout** (check one):
- [ ] All nodes on same LAN subnet (single broadcast domain)
- [ ] Multiple subnets with router between them
- [ ] VLAN segmentation (describe: _______________)
- [ ] Some nodes behind NAT
- [ ] Other: _______________

**Network diagram** (if available, attach or describe):
```
[Describe or attach network diagram]
```

---

### Q3: Can offline nodes reach the orchestrator machine directly?

**Once network issues are fixed**:
- [ ] Yes, direct Layer 2/Layer 3 connectivity exists
- [ ] No, requires routing through intermediate network
- [ ] Unknown, need to test after remediation

**Current test results** (if any):
```
[Run ping/traceroute from orchestrator to offline node IPs if known]
```

---

## Hardware Specifications

### Q4: What are the hardware specs for each node?

**Run these commands on each node** (or collect from documentation):

```bash
# RAM
free -h

# CPU
lscpu | grep -E "Model name|CPU\(s\)"

# GPU (if NVIDIA)
nvidia-smi --query-gpu=name,memory.total --format=csv

# GPU (if AMD)
rocm-smi

# Storage
df -h /

# OS
lsb_release -a  # or cat /etc/os-release
```

**Results**:

| Node | RAM | CPU | GPU | GPU VRAM | Storage | OS |
|------|-----|-----|-----|----------|---------|-----|
| 01   |     |     |     |          |         |     |
| 02   |     |     |     |          |         |     |
| 03   |     |     |     |          |         |     |
| 04   |     |     |     |          |         |     |
| 05   |     |     |     |          |         |     |
| 06   |     |     |     |          |         |     |
| 07   |     |     |     |          |         |     |

**Notes**:
```
[Any special hardware considerations, e.g., "Node 03 has broken GPU", "Node 07 only has 4GB RAM"]
```

---

### Q5: Can each node run local Ollama models?

**Current Ollama installation status**:

| Node | Ollama Installed? | Version | Models Pulled | Can Run? |
|------|-------------------|---------|---------------|----------|
| 01   |                   |         |               |          |
| 02   |                   |         |               |          |
| 03   |                   |         |               |          |
| 04   |                   |         |               |          |
| 05   |                   |         |               |          |
| 06   |                   |         |               |          |
| 07   |                   |         |               |          |

**Command to check**:
```bash
ollama --version
ollama list
```

**If not installed**:
- [ ] I will install Ollama on all nodes before Phase 1
- [ ] I want the setup script to handle Ollama installation
- [ ] Some nodes cannot run Ollama (specify: _______________)

**Minimum RAM per node for local models**:
- [ ] All nodes have ≥8GB (can run qwen3.5:4b comfortably)
- [ ] Some nodes have <8GB (will need cloud escalation)
  - Which nodes: _______________

---

## Agent Configuration

### Q6: Do you want symmetric or hierarchical agent setup?

**Definitions**:
- **Symmetric**: All nodes run identical agent configuration
- **Hierarchical**: Orchestrator has full capabilities, nodes are workers only
- **Hybrid**: Nodes have different roles based on hardware

**Your choice**: [FILL IN]

**Rationale**:
```
[Why did you choose this approach?]
```

---

### Q7: What is the primary workload for the trading lab?

**Check all that apply** (primary first):
- [ ] Portfolio monitoring and risk checks
- [ ] Backtesting strategies on historical data
- [ ] Live trading execution
- [ ] Market data processing and analysis
- [ ] Model training/fine-tuning
- [ ] Other: _______________

**Workload characteristics**:
- Typical task duration: [ ] < 1 min  [ ] 1-5 min  [ ] 5-30 min  [ ] > 30 min
- Tasks per day: [ ] < 10  [ ] 10-100  [ ] 100-1000  [ ] > 1000
- Parallelization: [ ] Highly parallelizable  [ ] Mostly sequential  [ ] Mixed

**Impact on design**:
```
[Any special requirements based on workload]
```

---

## Security & Access

### Q8: How will SSH/authentication be handled?

**Your choice**:
- [ ] SSH key-based authentication (recommended)
- [ ] Password authentication (not recommended)
- [ ] Certificate-based authentication
- [ ] Other: _______________

**If SSH keys**:
- Key type: [ ] ED25519 (recommended)  [ ] RSA 4096  [ ] Other
- Will you generate keys or use existing? _______________
- Do all nodes already have authorized_keys configured? [ ] YES  [ ] NO

**SSH connectivity test** (run from orchestrator):
```bash
for i in 01 02 04 05; do
    echo "Testing node-$i..."
    ssh node-$i "hostname"
done
```

**Results**:
```
[Paste output here]
```

---

### Q9: Do nodes have internet access for cloud model escalation?

**Your answer**:
- [ ] Yes, all nodes have direct internet access
- [ ] No, only orchestrator has internet (nodes need proxy)
- [ ] Restricted (firewall whitelist required)
- [ ] Unknown, need to test

**Test command** (run on a node):
```bash
curl -I https://ollama.com
```

**If no direct internet**:
- Proxy server available: [ ] YES  [ ] NO
- Proxy URL: _______________
- Can orchestrator act as proxy: [ ] YES  [ ] NO

---

## Operational Requirements

### Q10: What are the uptime/availability requirements?

**Your choice**:
- [ ] Best effort (nodes can go offline occasionally)
- [ ] High availability (99%+ uptime, ~7 hours/month downtime OK)
- [ ] Mission critical (99.9%+ uptime, ~43 minutes/month downtime OK)

**Monitoring expectations**:
- Alert on node offline > [FILL IN] minutes
- Check interval: every [FILL IN] minutes

---

### Q11: How should task failures be handled?

**Retry strategy**:
- Automatic retry: [ ] YES  [ ] NO
- Max retries: [FILL IN]
- Backoff strategy: [ ] Fixed delay  [ ] Exponential backoff
- Delay between retries: [FILL IN] seconds

**Escalation**:
- [ ] Retry on same node
- [ ] Retry on different node
- [ ] Escalate to cloud model after N failures
- [ ] Alert human immediately on failure

**Logging**:
- [ ] Log all failures to bookkeeping ledger
- [ ] Log only persistent failures (after all retries exhausted)
- [ ] Send failure notifications via [email/slack/other]: _______________

---

### Q12: Do you need a monitoring dashboard?

**Your choice**:
- [ ] Yes, real-time web dashboard showing:
  - Node status (online/offline)
  - Task queue depth
  - Model usage per node
  - Cost tracking
  - Historical uptime
  
- [ ] No, command-line tools are sufficient
  
- [ ] Later phase (start with CLI, add dashboard in Phase 6)

**If dashboard needed**:
- Preferred technology: [ ] Web (React/Vue)  [ ] TUI (terminal UI)  [ ] Grafana  [ ] Other
- Who will build it: [ ] Me  [ ] Agent  [ ] Outsource

---

## Additional Notes

[Any other requirements, constraints, or considerations not covered above]

```
[FILL IN]
```

---

## Sign-off

**Completed by**: _______________  
**Date**: _______________  
**Review date**: _______________ (review answers before Phase 1 kickoff)

---

**Next Steps After Completion**:
1. Review answers with implementation team
2. Confirm Phase 0 (network remediation) plan
3. Schedule Phase 1 kickoff
4. Assign responsibilities
