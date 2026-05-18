# Node 2 Reference Guide (Complete Documentation)

**Version:** 4.1 | **Companion to:** NODE2-AGENTS.md  
**Purpose:** Detailed reference - download when needed  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

## 📖 HOW TO USE THIS REFERENCE

**Main File:** `NODE2-AGENTS.md` (~100 lines) - Keep loaded always  
**Reference File:** `NODE2-REFERENCE.md` (this file) - Download when needed

**Download on demand:**
```bash
curl -sL "$GIST_URL/NODE2-REFERENCE.md" -o ./NODE2-REFERENCE.md
```

**Load specific sections:**
```bash
# Load troubleshooting section
grep -A 50 "TROUBLESHOOTING DECISION TREE" ./NODE2-REFERENCE.md

# Load emergency procedures
grep -A 30 "EMERGENCY PROCEDURES" ./NODE2-REFERENCE.md
```

---

## 🌳 TROUBLESHOOTING DECISION TREE

```
Problem detected
    │
    ├─→ Can't find files?
    │   ├─→ Check directory: pwd
    │   ├─→ If wrong: cd ~/network-troubleshooting-bundle
    │   └─→ Download: curl -sL $GIST_URL/file -o ./file
    │
    ├─→ Script taking >2 min?
    │   ├─→ Report: echo "ESCALATED: >2 min" > ./node2-STATUS.md
    │   ├─→ Post to Gist
    │   └─→ Request decomposition
    │
    ├─→ Wrong directory?
    │   ├─→ Stop current operation
    │   ├─→ cd ~/network-troubleshooting-bundle
    │   └─→ Verify: pwd = /home/friasc/network-troubleshooting-bundle
    │
    ├─→ Can't post to Gist?
    │   ├─→ Check auth: gh auth status
    │   ├─→ Re-auth: gh auth login
    │   └─→ Report: Post error to node2-help.txt
    │
    ├─→ Tests failing?
    │   ├─→ Document: Save test output
    │   ├─→ Report: Post to Gist with details
    │   └─→ Wait: Cloud agent will analyze
    │
    └─→ Completely stuck?
        ├─→ Stop all activity
        ├─→ Document: What step, what error, what tried
        ├─→ Report: node2-help.txt with full details
        └─→ Wait: Cloud agent will respond
```

---

## 📥 COMPLETE FILE REFERENCE

### Scripts to Download (All from Gist)

| File | Purpose | Size | Download Command |
|------|---------|------|------------------|
| `NODE2-AGENTS.md` | Main context | ~100 lines | `curl -sL $GIST_URL/NODE2-AGENTS.md -o ./NODE2-AGENTS.md` |
| `NODE2-REFERENCE.md` | This reference | ~400 lines | `curl -sL $GIST_URL/NODE2-REFERENCE.md -o ./NODE2-REFERENCE.md` |
| `step1-setup.sh` | Setup (<1 min) | ~40 lines | `curl -sL $GIST_URL/step1-setup.sh -o ./step1-setup.sh` |
| `step2-diagnostics.sh` | Diagnostics (<2 min) | ~60 lines | `curl -sL $GIST_URL/step2-diagnostics.sh -o ./step2-diagnostics.sh` |
| `step3-poll.sh` | Poll & execute (<10 min) | ~80 lines | `curl -sL $GIST_URL/step3-poll.sh -o ./step3-poll.sh` |
| `context-health-check.sh` | Health monitoring | ~80 lines | `curl -sL $GIST_URL/context-health-check.sh -o ./context-health-check.sh` |
| `detect-hardware.sh` | Hardware detection | ~100 lines | `curl -sL $GIST_URL/detect-hardware.sh -o ./detect-hardware.sh` |
| `diagnose.sh` | Network diagnostics | ~120 lines | `curl -sL $GIST_URL/diagnose.sh -o ./diagnose.sh` |
| `verify.sh` | Verification | ~100 lines | `curl -sL $GIST_URL/verify.sh -o ./verify.sh` |

### Files to Create (Your Output)

| File | Purpose | When | Command |
|------|---------|------|---------|
| `node2-STATUS.md` | Workflow status | After every step | `echo "STATUS" > ./node2-STATUS.md` |
| `node2-diagnostic.txt` | Diagnostic output | After step 2 | `cat /tmp/hardware-report.txt /tmp/network-diagnosis.log > /tmp/node2-diagnostic.txt` |
| `node2-results.txt` | Execution results | After step 3 | `echo "Fix executed at $(date)" > /tmp/node2-results.txt` |
| `node2-verification.txt` | Verification | After step 3 | `cat /tmp/node-ready.txt > /tmp/node2-verification.txt` |
| `node2-help.txt` | Help requests | When stuck | `echo "Need help: [details]" > ./node2-help.txt` |
| `node2-progress.txt` | Progress reports | Optional detailed | `echo "Progress: [details]" > ./node2-progress.txt` |

---

## 🚨 EMERGENCY PROCEDURES (Complete)

### Procedure 1: Lost/Confused

```bash
# 1. Stop all activity
echo "PAUSED: Need guidance" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# 2. Check and fix directory
cd ~/network-troubleshooting-bundle
pwd

# 3. Document current state
cat > ./node2-help.txt << HELP
LOST/CONFUSED
Time: $(date)
Current step: [What were you doing?]
Last successful: [What last worked?]
Error: [What went wrong?]
Tried: [What did you try?]
HELP
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt

# 4. Reload context
curl -sL "$GIST_URL/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md
cp ./NODE2-AGENTS.md ~/.pi/agent/AGENTS.md

# 5. Wait for cloud agent
```

---

### Procedure 2: Wrong Directory

```bash
# 1. Identify current directory
CURRENT=$(pwd)
echo "⚠️ Wrong directory: $CURRENT"

# 2. Fix immediately
cd ~/network-troubleshooting-bundle

# 3. Verify
NEW=$(pwd)
if [ "$NEW" = "/home/friasc/network-troubleshooting-bundle" ]; then
    echo "✓ Fixed: Now in $NEW"
else
    echo "✗ Still wrong: $NEW"
    echo "ESCALATED: Can't fix directory" > ./node2-help.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt
fi

# 4. Report
echo "DIRECTORY_FIXED" > ./node2-STATUS.md
echo "Was: $CURRENT" >> ./node2-STATUS.md
echo "Now: $NEW" >> ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

### Procedure 3: Script Too Large

```bash
# 1. Check script size
LINES=$(wc -l < ./script.sh)

# 2. If >50 lines, don't execute
if [ $LINES -gt 50 ]; then
    echo "⚠️ Script too large: $LINES lines"
    
    # 3. Request decomposition
    cat > ./node2-help.txt << HELP
EFFICIENCY ALERT
Script: [name]
Lines: $LINES
Threshold: 50
Request: Decompose into smaller steps
HELP
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt
    
    # 4. Update status
    echo "ESCALATED: Script $LINES lines - need decomposition" > ./node2-STATUS.md
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
    
    # 5. Wait for cloud agent
else
    # Safe to execute
    bash ./script.sh
fi
```

---

### Procedure 4: Gist Auth Failed

```bash
# 1. Check auth status
gh auth status

# 2. If not authenticated, re-auth
if ! gh auth status &>/dev/null; then
    echo "⚠️ Not authenticated"
    
    # Try to re-auth (may need user intervention)
    gh auth login -h github.com -p ssh
    
    # Verify
    if gh auth status &>/dev/null; then
        echo "✓ Re-authenticated"
    else
        echo "✗ Re-auth failed - need user help"
        echo "ESCALATED: GitHub auth failed" > ./node2-help.txt
        gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt
    fi
fi
```

---

### Procedure 5: Timeout Waiting for Fixes

```bash
# After 10 minutes of polling with no fix commands

# 1. Document timeout
cat > ./node2-help.txt << HELP
TIMEOUT
Step: step3-poll.sh
Duration: 10 minutes
Polling attempts: 60
Status: No fix commands received
Possible causes:
- Diagnostics not posted
- Cloud agent hasn't seen diagnostics
- Gist sync issue
HELP
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt

# 2. Verify diagnostics were posted
if curl -sL "$GIST_URL/node2-diagnostic.txt" | grep -q "HARDWARE"; then
    echo "✓ Diagnostics in Gist"
else
    echo "✗ Diagnostics NOT in Gist - re-post"
    # Re-post diagnostics
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-diagnostic.txt
fi

# 3. Update status
echo "ESCALATED: Timeout - no fix commands after 10 min" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# 4. Wait for cloud agent
```

---

## 🎯 HALLUCINATION PREVENTION (Complete Guide)

### Common Triggers and Mitigations

| Trigger | Symptom | Prevention | Recovery |
|---------|---------|------------|----------|
| Long session (>5 min) | Forgets identity | Reload AGENTS.md every 5 min | Run health check |
| Complex script | Tries to analyze | Remember: Execute only | Reload EFFICIENCY section |
| Multiple files | Loses track | One file at a time | List files: ls -la |
| Timeout/wait | Makes up responses | Wait for actual data | Check Gist directly |
| Error state | Hallucinates fixes | Escalate, don't improvise | Post error, wait |
| Forgot tools | Tries invalid commands | Reload TOOLS section | Check available commands |
| File not found | Tries to create from memory | DOWNLOAD from Gist | Use curl, don't cat> |
| Wrong directory | Can't find files | cd ~/network-troubleshooting-bundle first | pwd, then cd |
| Root directory (/) | CRITICAL | Never go to / | Immediately cd ~ |

### Pre-Action Checklist (Complete)

Before ANY action, verify:

```
□ Identity: "I am Node 2 (WORKER), user friasc"
□ Directory: pwd = /home/friasc/network-troubleshooting-bundle
□ Files needed: Download from Gist (don't create!)
□ Script size: <50 lines (if not, escalate)
□ Status file: Updated before posting
□ Time check: Step taking <2 min?
```

---

## 📊 STATUS STATE DEFINITIONS (Complete)

| State | When to Set | Required Details | Example |
|-------|-------------|------------------|---------|
| `INITIALIZING` | Starting step 1 | Time, directory, files to download | `INITIALIZING\nTime: 2026-04-26 18:00\nDir: /home/friasc/network-troubleshooting-bundle` |
| `STEP1_COMPLETE` | After setup | Files downloaded, next step | `STEP1_COMPLETE\nDownloaded: step2, step3, detect, diagnose, verify\nNext: step2-diagnostics.sh` |
| `DIAGNOSTIC_READY` | After step 2 | Test results, diagnostic posted | `DIAGNOSTIC_READY\nGateway: PASS\nInternet: FAIL\nDiagnostic: Posted` |
| `FIXES_PENDING` | Starting step 3 | Polling started, interval | `FIXES_PENDING\nPolling: Every 10s\nTimeout: 10 min` |
| `RESULTS_READY` | After execution | Exit code, errors, timestamp | `RESULTS_READY\nExecuted: 2026-04-26 18:10\nExit: 0\nErrors: None` |
| `COMPLETE` | All done | Verification results | `COMPLETE\nVerified: PASS\nAll tests: PASSED` |
| `ESCALATED` | Stuck/error | Full details, what tried | `ESCALATED\nIssue: Script timeout\nStep: step3\nTried: Increased timeout\nNeed: Decomposition` |

---

## 🤖 SUBAGENT USAGE (Complete Guide)

### When to Use Subagents

**DO Use Subagent For:**
- ✅ Downloading multiple files in parallel
- ✅ Complex analysis of diagnostic output
- ✅ Reviewing large log files
- ✅ Generating detailed reports
- ✅ Cross-referencing documentation

**DON'T Use Subagent For:**
- ❌ Simple file downloads (curl is fine)
- ❌ Running step scripts (execute locally)
- ❌ Reporting progress (your responsibility!)
- ❌ Updating status files (your responsibility!)
- ❌ Health checks (run locally)

### Subagent Command Examples

```bash
# Good: Delegate bulk download
pi "Download all troubleshooting scripts from Gist to ~/network-troubleshooting-bundle:
     step1-setup.sh, step2-diagnostics.sh, step3-poll.sh,
     detect-hardware.sh, diagnose.sh, verify.sh,
     context-health-check.sh"

# Good: Delegate analysis
pi "Analyze this network diagnostic output and identify the root cause:
     [paste diagnostic output]"

# Bad: Don't delegate your responsibilities
pi "Update node2-STATUS.md"  ← WRONG! You do this!

pi "Run step2-diagnostics.sh"  ← WRONG! You execute this!
```

---

## 🔧 HEALTH CHECK (Complete Script Reference)

**What it checks:**
1. Working directory (must be ~/network-troubleshooting-bundle)
2. Identity (Node 2, worker, friasc)
3. Status file (current workflow state)
4. Session time (alert if >5 min without reload)
5. Script sizes (alert if >50 lines)
6. Gist connectivity (can reach Gist?)
7. Local files (are required scripts present?)

**When to run:**
- Every 5 minutes during active workflow
- Before starting any new step
- After any error or unexpected state
- When feeling "lost" or uncertain

**How to run:**
```bash
bash ./context-health-check.sh

# Or delegate to subagent for interpretation
pi "Run context-health-check.sh and summarize any issues"
```

---

## 📋 COMMUNICATION PROTOCOL (Complete)

### Posting to Gist

```bash
# Basic post
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./filename

# Post with description
gh gist edit 0c517214489cb78c0484ca661f3d8463 -d "Node 2 status update" --add ./node2-STATUS.md

# Post multiple files (separate commands)
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./file1.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./file2.txt
```

### Checking Gist

```bash
# List all files
curl -s https://api.github.com/gists/0c517214489cb78c0484ca661f3d8463 | \
  python3 -c "import sys,json; [print(k) for k in json.load(sys.stdin).get('files',{}).keys()]"

# Download specific file
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/filename"

# Check for new files (from cloud agent)
curl -sL "$GIST_URL/node2-fix-commands.sh" | head -1
# If starts with "#", fix commands are ready
```

### Progress Report Template

```bash
# After each step, use this template:
cat > ./node2-progress.txt << PROGRESS
=== PROGRESS REPORT ===
Time: $(date)
Step: [step1/step2/step3]
Status: [COMPLETE/IN_PROGRESS/FAILED]
Directory: $(pwd)
Files: [list relevant files]
Tests: [results if applicable]
Next: [next action]
Issues: [any problems]
=== END REPORT ===
PROGRESS

gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-progress.txt
```

---

## ⚡ EFFICIENCY MONITORING (Complete Rules)

### Script Size Limits

| Script Type | Max Lines | If Exceeded |
|-------------|-----------|-------------|
| Setup scripts | 50 | Request decomposition |
| Diagnostic scripts | 80 | Acceptable (run anyway) |
| Poll scripts | 100 | Acceptable (background) |
| Fix commands (from cloud) | 50 | Request decomposition |

### Time Limits

| Step | Max Time | Action if Exceeded |
|------|----------|-------------------|
| step1-setup.sh | 1 min | Use subagent for downloads |
| step2-diagnostics.sh | 2 min | Run tests in parallel |
| step3-poll.sh | 10 min total | 10s intervals, background |
| Health check | 30 sec | Simple script only |
| Any single command | 30 sec | Background or decompose |

### Memory/CPU Monitoring

```bash
# Check memory usage
free -h

# If swap >50%, report
if [ $(free | awk '/Swap/ {print $3}') -gt 0 ]; then
    echo "⚠️ Swap in use - memory constrained" > ./node2-efficiency.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-efficiency.txt
fi

# Check CPU load
load=$(uptime | awk -F'load average:' '{print $2}' | cut -d',' -f1)
if (( $(echo "$load > 2.0" | bc -l) )); then
    echo "⚠️ High CPU load: $load" > ./node2-efficiency.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-efficiency.txt
fi
```

---

**End of Reference Guide**

For quick start, see: `NODE2-AGENTS.md`  
Gist: https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463
