# Node 2 ↔ Cloud Agent Communication Protocol

**Medium:** GitHub Gist  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

## Message Flow

```
Node 2                          Gist Files                        Cloud Agent (Mac)
  │                                  │                                  │
  ├── Step 1: Deploy ──────────────► │                                  │
  │                                  │                                  │
  ├── Step 2: Run diagnostics ─────► │ post-diagnostic-output.txt       │
  │                                  │ ◄──────── Read & Analyze ────────│
  │                                  │                                  │
  │                                  │ write-fix-commands.sh            │
  │ ◄──────── Read & Execute ────────│                                  │
  │                                  │                                  │
  ├── Step 3: Run fixes ───────────► │ post-fix-results.txt             │
  │                                  │ ◄──────── Read & Verify ────────│
  │                                  │                                  │
  │                                  │ write-verification-request.sh    │
  │ ◄──────── Read & Execute ────────│                                  │
  │                                  │                                  │
  ├── Step 4: Verification ────────► │ post-verification-output.txt     │
  │                                  │ ◄──────── Final Review ──────────│
  │                                  │                                  │
  │                                  │ COMPLETE.md                      │
  │ ◄──────── Done ──────────────────│                                  │
  │                                  │                                  │
```

---

## File Naming Convention

| File Pattern | Direction | Purpose |
|--------------|-----------|---------|
| `node2-diagnostic-*.txt` | Node 2 → Cloud | Diagnostic output |
| `node2-fix-commands.sh` | Cloud → Node 2 | Fix commands to execute |
| `node2-results-*.txt` | Node 2 → Cloud | Fix execution results |
| `node2-verification-*.txt` | Node 2 → Cloud | Verification output |
| `node2-COMPLETE.md` | Cloud → Node 2 | Final confirmation |
| `node2-STATUS.md` | Either | Current status |

---

## Message Status States

| State | File | Content |
|-------|------|---------|
| `WAITING_DIAGNOSTIC` | `node2-STATUS.md` | Cloud agent waiting for diagnostics |
| `DIAGNOSTIC_READY` | `node2-STATUS.md` | Diagnostics posted, cloud should review |
| `FIXES_READY` | `node2-STATUS.md` | Fix commands posted, node should execute |
| `RESULTS_READY` | `node2-STATUS.md` | Results posted, cloud should verify |
| `COMPLETE` | `node2-COMPLETE.md` | All done |

---

## Node 2 Commands

### Send Diagnostics to Cloud
```bash
# Post diagnostic output to Gist
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/post-to-gist.sh | bash -s -- diagnostic /tmp/hardware-report.txt /tmp/network-diagnosis-*.log
```

### Check for New Commands
```bash
# Check if cloud agent posted fix commands
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/check-gist.sh | bash -s -- fix-commands
```

### Execute Commands from Cloud
```bash
# Download and execute fix commands from Gist
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/execute-from-gist.sh | bash -s -- fix-commands
```

### Send Results to Cloud
```bash
# Post execution results to Gist
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/post-to-gist.sh | bash -s -- results /tmp/fix-results.txt
```

---

## Cloud Agent Commands (On Mac)

### Check for New Diagnostics
```bash
# Check if Node 2 posted diagnostics
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/check-gist.sh | bash -s -- diagnostic
```

### Post Fix Commands
```bash
# Upload fix commands for Node 2 to execute
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/post-to-gist.sh | bash -s -- fix-commands < fix-commands.sh
```

### Review Results
```bash
# Check fix results from Node 2
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/check-gist.sh | bash -s -- results
```

---

## Automation Script (Node 2)

```bash
#!/bin/bash
# Autonomous troubleshooting loop for Node 2

GIST_BASE="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

# Step 1: Run diagnostics
./diagnose.sh
curl -L "$GIST_BASE/post-to-gist.sh" | bash -s -- diagnostic /tmp/diagnostic-output.txt

# Step 2: Wait for fix commands (poll every 10 seconds)
while true; do
    if curl -sL "$GIST_BASE/node2-fix-commands.sh" | grep -q "^#"; then
        curl -L "$GIST_BASE/execute-from-gist.sh" | bash
        curl -L "$GIST_BASE/post-to-gist.sh" | bash -s -- results /tmp/fix-results.txt
        break
    fi
    sleep 10
done

# Step 3: Wait for verification
while true; do
    if curl -sL "$GIST_BASE/node2-COMPLETE.md" | grep -q "COMPLETE"; then
        echo "Troubleshooting complete!"
        break
    fi
    sleep 10
done
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **No manual copy/paste** | All communication via Gist |
| **Asynchronous** | Node 2 can work offline between messages |
| **Audit trail** | All messages preserved in Gist history |
| **Resume capability** | Can restart from any step if interrupted |
| **Scalable** | Same pattern works for Nodes 6, 7, etc. |

---

## Limitations

| Limitation | Mitigation |
|------------|------------|
| Gist API rate limits | Use raw URLs, cache locally |
| Polling delay (10-30s) | Acceptable for troubleshooting workflow |
| Manual gist updates (no API key) | Use curl with raw URLs |
| File size limits (10MB) | Not an issue for text diagnostics |

---

**Next:** Implement `post-to-gist.sh`, `check-gist.sh`, and `execute-from-gist.sh` scripts.
