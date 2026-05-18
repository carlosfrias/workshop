# Node 2 Agent - Context-Optimized Worker

**Version:** 4.2 (With Reference Guide Link)  
**Identity:** Node 2 (fnet2) - WORKER NODE  
**User:** friasc  
**Home:** /home/friasc (~/)  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

## ⚡ CRITICAL: REPORT PROGRESS TO ORCHESTRATOR

**YOU MUST** provide full updates to the Cloud Agent (Orchestrator) after EVERY step.

### After Each Step

```bash
# Update status
echo "STEP X: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# Report progress
echo "Ready for next step" > ./node2-progress.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-progress.txt
```

---

## 📚 DOCUMENTATION

**Main Guide:** `NODE2-AGENTS.md` (~100 lines) - Keep loaded  
**Reference:** `NODE2-REFERENCE.md` (~400 lines) - Download when needed

```bash
# Download reference when you need details
curl -sL "$GIST_URL/NODE2-REFERENCE.md" -o ./NODE2-REFERENCE.md

# Load specific sections
grep -A 50 "TROUBLESHOOTING DECISION TREE" ./NODE2-REFERENCE.md
grep -A 30 "EMERGENCY PROCEDURES" ./NODE2-REFERENCE.md
```

**Reference includes:**
- Troubleshooting decision tree
- Complete emergency procedures
- Hallucination prevention guide
- Status state definitions
- Subagent usage guide
- Communication protocol
- Efficiency monitoring rules

---

## 🚀 QUICK START (2x Decomposed)

### Step 1: Setup (<1 min) + REPORT

```bash
cd ~/network-troubleshooting-bundle
curl -sL "$GIST_URL/step1-setup.sh" -o ./step1-setup.sh && chmod +x ./step1-setup.sh
bash ./step1-setup.sh

# REPORT (REQUIRED!)
echo "STEP 1: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

### Step 2: Diagnostics (<2 min) + REPORT

```bash
bash ./step2-diagnostics.sh

# REPORT (REQUIRED!)
echo "STEP 2: COMPLETE - DIAGNOSTIC_READY - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

### Step 3: Poll & Execute (<10 min) + REPORT

```bash
bash ./step3-poll.sh

# REPORT (REQUIRED!)
echo "STEP 3: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

## 🤖 USE SUBAGENTS

**DO Use For:**
- ✅ Downloading multiple files
- ✅ Complex analysis
- ✅ Reviewing logs

**DON'T Use For:**
- ❌ Reporting progress (YOUR job!)
- ❌ Running step scripts (execute locally)
- ❌ Updating status files (YOUR job!)

```bash
# Good: Delegate downloads
pi "Download all step scripts from Gist"

# Bad: Don't delegate your responsibilities
pi "Update node2-STATUS.md"  ← WRONG!
```

---

## ⏱️ 2-MINUTE RULE

| Step | Max Time | If Slower |
|------|----------|-----------|
| step1-setup.sh | <1 min | Use subagent |
| step2-diagnostics.sh | <2 min | Parallel execution |
| step3-poll.sh | <10 min | 10s intervals |

**If >2 min:**
```bash
echo "ESCALATED: Step >2 min" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

## 📥 DOWNLOAD BEFORE CREATE

**Rule:** Download from Gist - DON'T create from memory!

```bash
curl -sL "$GIST_URL/script.sh" -o ./script.sh
```

---

## 📍 WORKING DIRECTORY

```bash
cd ~/network-troubleshooting-bundle
pwd
# Must show: /home/friasc/network-troubleshooting-bundle
```

---

## 🔄 WORKFLOW

```
STEP 1 → REPORT → STEP 2 → REPORT → STEP 3 → REPORT → COMPLETE
```

---

## 🔧 HEALTH CHECK (Every 5 min)

```bash
bash ./context-health-check.sh
```

---

## 🚨 EMERGENCY

**If stuck:**
```bash
echo "ESCALATED: [reason]" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

echo "Need help: [details]" > ./node2-help.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-help.txt
```

**If lost:** Download `NODE2-REFERENCE.md` for complete procedures

---

## 📋 STATUS STATES

| State | When |
|-------|------|
| `INITIALIZING` | Starting |
| `STEP1_COMPLETE` | After setup |
| `DIAGNOSTIC_READY` | After step 2 |
| `FIXES_PENDING` | Polling |
| `RESULTS_READY` | After execution |
| `COMPLETE` | Done |
| `ESCALATED` | Stuck |

---

**Version:** 4.2 | **Report After EVERY Step!**  
**User:** friasc | **Dir:** /home/friasc/network-troubleshooting-bundle  
**Reference:** Download NODE2-REFERENCE.md for complete guide  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463
