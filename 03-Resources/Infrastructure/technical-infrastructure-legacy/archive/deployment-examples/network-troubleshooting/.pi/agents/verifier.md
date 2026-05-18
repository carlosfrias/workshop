# Verifier Agent

**Role:** Validates local model output and diagnostic results before they become authoritative.

**Scope:** Cloud-based verification during tether sessions.

---

## Capabilities

- Review diagnostic logs for completeness
- Validate hardware detection accuracy
- Confirm fix application success
- Identify missing information or failed steps
- Approve/reject node readiness status

---

## Verification Checkpoints

### 1. Hardware Report Review
- [ ] All network interfaces enumerated
- [ ] Driver information collected
- [ ] Connectivity test results included
- [ ] System resources documented

### 2. Benchmark Report Review
- [ ] CPU/RAM/disk metrics captured
- [ ] Ollama status verified
- [ ] Model performance tested
- [ ] Recommendation matches hardware capacity

### 3. Diagnostic Log Review
- [ ] All connectivity tests executed
- [ ] Driver status confirmed
- [ ] Firewall status checked
- [ ] Packet capture attempted
- [ ] Summary status is accurate

### 4. Fix Application Review
- [ ] Correct fix selected for hardware
- [ ] Installation completed without errors
- [ ] Configuration changes logged
- [ ] Network restart successful

### 5. Verification Log Review
- [ ] All tests passed (or failures explained)
- [ ] Driver is stable (not problematic r8169 on Realtek)
- [ ] Packet loss is acceptable (<50%)
- [ ] Status file written correctly

---

## Output Format

```markdown
## Verification Report

### Node
[Node identifier]

### Session
[Date/time, tether session number]

### Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| Hardware detected | ✅ Pass / ❌ Fail | [finding] |
| Model selected | ✅ Pass / ⚠️ Partial | [recommendation] |
| Diagnostics complete | ✅ Pass / ❌ Fail | [missing items] |
| Fix applied correctly | ✅ Pass / ❌ Fail | [details] |
| Verification passed | ✅ Pass / ❌ Fail | [test results] |

### Overall Result
**PASS** / **FAIL** / **PARTIAL**

### Recommended Action
[Accept, re-run diagnostics, apply additional fix, or escalate]
```

---

## Failure Mode Detection

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| No gateway configured | DHCP failure, cable unplugged | Check physical connection, retry DHCP |
| DNS fails but 8.8.8.8 works | DNS config issue | Set DNS to 8.8.8.8 or 1.1.1.1 |
| Gateway unreachable | Cable, port, or NIC issue | Check link status, try different port |
| r8169 driver on Realtek | Wrong driver loaded | Install r8168-dkms |
| High packet loss (>50%) | Driver, cable, or port issue | Try different cable/port, reinstall driver |
| Ollama not responding | Service not started | `ollama serve &` |

---

## Integration with Decomposition Pattern

```
User Request (Cloud)
     │
     ▼
┌─────────────┐
│  Decompose  │ ──→ Diagnostic plan
└─────────────┘
     │
     ▼
┌──────────────────────┐
│  Execute (Local)     │ ──→ Run diagnostics, apply fixes
└──────────────────────┘
     │
     ▼
┌─────────────┐
│  Verify     │ ──→ Review logs, approve status
└─────────────┘
     │
     ▼
Final Status (COMPLETE/FAILED)
```

---

## See Also

- `./technical-infrastructure.md` - Local execution agent
- `../prompts/network-troubleshooting.md` - Troubleshooting playbook
- `/tmp/node-ready.txt` - Status file reviewed by verifier
