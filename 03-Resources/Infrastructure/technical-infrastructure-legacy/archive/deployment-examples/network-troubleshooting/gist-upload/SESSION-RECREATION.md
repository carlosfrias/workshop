# Session Recreation Prompt

**Purpose:** Recreate this exact troubleshooting session for additional nodes or future incidents.

---

## Context to Provide Cloud Agent

```
I need to troubleshoot network connectivity on offline Ubuntu nodes using a time-limited phone tether connection.

## Environment
- Orchestrator: MacBook (this session)
- Target nodes: Offline Ubuntu machines (20.04/22.04/26.04)
- Connection: USB phone tether (time-limited, costly)
- Local AI: Ollama with local models (capacity varies by node)

## Goal
Minimize tether time by:
1. Using cloud agent during tether for: hardware diagnosis, model selection, decomposition planning
2. Running diagnostics and fixes offline with local agents
3. Reconnecting briefly for verification only

## Available Resources
- Deployment bundle: [GIST_URL_HERE]
- Scripts: detect-hardware.sh, benchmark-model.sh, diagnose.sh, apply-fix.sh, verify.sh
- Agents: technical-infrastructure (local), verifier (cloud)
- Pattern: Decompose → Execute → Verify

## Node Status
| Node | Hardware | OS | Status |
|------|----------|-----|--------|
| 2 | Unknown | 26.04 | ❌ Offline |
| 6 | Intel NUC | 20.04/22.04 | ❌ Offline |
| 7 | Intel NUC | 20.04/22.04 | ❌ Offline |

## Workflow

### Tether Session 1 (Setup) - 10-15 min
1. Install pi: `sudo npm install -g @mariozechner/pi-coding-agent`
2. Install Ollama: `./scripts/install-ollama.sh`
3. Start Ollama: `ollama serve &`
4. Run hardware detection: `./scripts/detect-hardware.sh > /tmp/hardware-report.txt`
5. **Paste hardware report to cloud agent**
6. Run benchmark: `./scripts/benchmark-model.sh > /tmp/benchmark-report.txt`
7. **Paste benchmark report to cloud agent**
8. Cloud agent provides: model recommendation, driver diagnosis, decomposition plan
9. Download recommended model: `ollama pull <model>`
10. Deploy agents: `cp -r ~/.pi ~/.pi`
11. Disconnect tether

### Offline Work - 30-45 min
1. Run diagnostics: `./scripts/diagnose.sh`
2. Cloud agent reviews logs (next tether session)
3. Apply fixes: `./scripts/apply-fix.sh <fix_number>`
4. Verify: `./scripts/verify.sh`
5. Check status: `cat /tmp/node-ready.txt`

### Tether Session 2 (Verification) - 2 min
1. Reconnect tether
2. **Paste verification log to cloud agent**
3. Cloud agent confirms: COMPLETE or provides next steps
4. If COMPLETE, node is ready. If not, repeat offline work.

## Hardware Notes
- Node 2: Unknown NIC (possibly Realtek, same OS as node 1 which had r8169 issue)
- Nodes 6-7: Intel NUCs (likely in-kernel Intel drivers: e1000e, igb, or igc)
- Intel NUCs rarely need external drivers; issues are usually configuration

## Expected Driver Scenarios
| Hardware | Likely Driver | Fix |
|----------|---------------|-----|
| Realtek RTL8168H | r8168 (external) | Install r8168-dkms |
| Realtek RTL8125 | r8125 (external) | Install r8125-dkms |
| Intel I219-V | e1000e (in-kernel) | Configuration fix |
| Intel I225-V | igc (in-kernel) | Configuration fix |
| Intel I350 | igb (in-kernel) | Configuration fix |

## Key Files
- Hardware report: `/tmp/hardware-report.txt`
- Benchmark report: `/tmp/benchmark-report.txt`
- Diagnostic log: `/tmp/network-diagnosis-*.log`
- Fix log: `/tmp/network-fix-*.log`
- Verification log: `/tmp/network-verify-*.log`
- Status file: `/tmp/node-ready.txt`

## Success Criteria
- All nodes can reach 8.8.8.8 and google.com
- Packet loss <50% to gateway
- Stable driver loaded (not buggy r8169 on Realtek)
- Status file shows: COMPLETE
```

---

## Cloud Agent Instructions

When the user pastes hardware/benchmark reports:

1. **Analyze hardware report** → Identify NIC chipset and current driver
2. **Analyze benchmark report** → Recommend optimal Ollama model for node capacity
3. **Provide decomposition plan** → Specific fixes needed for this node
4. **Wait for verification logs** → Confirm fix success or iterate

---

## Model Routing

| Task | Model | Reason |
|------|-------|--------|
| Hardware diagnosis | qwen3.5:cloud | Requires reasoning about driver compatibility |
| Model selection | qwen3.5:cloud | Requires judgment about capacity vs performance |
| Decomposition plan | qwen3.5:cloud | Complex multi-step planning |
| Verification | qwen3.5:cloud | Quality gate before node is marked complete |
| Local diagnostics | qwen3.5:4b or qwen3:8b | Routine monitoring task |
| Log parsing | gemma4:e4b | Structured data extraction |

---

## Estimated Time Budget

| Phase | Duration | Cloud Time |
|-------|----------|------------|
| Setup (per node) | 10-15 min | 3-5 min (diagnosis + planning) |
| Offline work | 30-45 min | 0 min |
| Verification (per node) | 2 min | 1-2 min (review + approval) |
| **Total per node** | **~45 min** | **~5-7 min** |

---

## Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| pi installation fails | Install Node.js first: `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash -` |
| Ollama won't start | Check port 11434: `sudo lsof -i :11434` |
| Model download too slow | Use smaller model: `llama3.2:3b` or `phi3:3.8b` |
| Hardware detection fails | Run individual commands: `lspci -nn`, `lsusb`, `ethtool -i eth0` |
| Verification fails | Review log, identify failed test, apply targeted fix |
