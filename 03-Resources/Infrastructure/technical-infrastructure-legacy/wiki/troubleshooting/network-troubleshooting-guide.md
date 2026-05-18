# Network Troubleshooting Guide

**Domain:** Technical Infrastructure  
**Purpose:** Complete guide for troubleshooting network connectivity on offline nodes  
**Version:** 1.0  
**Last Updated:** 2026-04-26

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [2x Decomposed Workflow](#_2x-decomposed-workflow)
4. [Step-by-Step Instructions](#step-by-step-instructions)
5. [Common Issues](#common-issues)
6. [Worker Node Documentation](#worker-node-documentation)
7. [Autonomous Monitoring](#autonomous-monitoring)
8. [Case Studies](#case-studies)

---

## Overview

This guide provides a systematic approach to troubleshooting network connectivity on offline nodes (fnet2, fnet6, fnet7, etc.) using a 2x decomposed workflow with cloud agent support.

**Key Features:**
- ✅ 2x decomposed steps (<2 minutes each)
- ✅ Tether-aware testing (stays connected)
- ✅ Interface-bound diagnostics
- ✅ Cloud agent monitoring (<60 second response)
- ✅ Progress reporting enforced
- ✅ Subagent integration

---

## Prerequisites

### Required Tools

- GitHub CLI (`gh`) - authenticated
- Bash shell
- Basic network utilities (`ping`, `ip`, `ethtool`)
- Internet access (via tether or alternative)

### Gist Access

All scripts are available in this Gist:
**https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463**

### Worker Node Setup

```bash
# Create working directory
mkdir -p ~/network-troubleshooting-bundle
cd ~/network-troubleshooting-bundle

# Download main context
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md
```

---

## 2x Decomposed Workflow

### Workflow Overview

```
STEP 1: Setup (<1 min)
  ↓
  REPORT PROGRESS
  ↓
STEP 2: Diagnostics (<2 min)
  ↓
  REPORT + POST DIAGNOSTICS
  ↓
  CLOUD AGENT ANALYSIS (<60 sec)
  ↓
  [IF NEEDED] FIX COMMANDS POSTED
  ↓
STEP 3: Poll & Execute (<10 min)
  ↓
  REPORT + VERIFY
  ↓
COMPLETE
```

### Scripts

| Script | Purpose | Time | Size |
|--------|---------|------|------|
| `step1-setup.sh` | Download files, initialize | <1 min | ~40 lines |
| `step2-diagnostics.sh` | Configure interface, test | <2 min | ~60 lines |
| `step3-poll.sh` | Poll for fixes, execute | <10 min | ~80 lines |

---

## Step-by-Step Instructions

### Step 1: Setup (<1 min)

**Purpose:** Download all required scripts and initialize status.

```bash
cd ~/network-troubleshooting-bundle

# Download scripts
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/step1-setup.sh" -o ./step1-setup.sh
chmod +x ./step1-setup.sh

# Run setup
bash ./step1-setup.sh

# REPORT (REQUIRED!)
echo "STEP 1: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

**Expected Output:**
```
=== STEP 1: SETUP (<1 min) ===
Working in: /home/friasc/network-troubleshooting-bundle
Downloading scripts...
  ✓ Downloaded: step2-diagnostics.sh
  ✓ Downloaded: step3-poll.sh
  ✓ Downloaded: detect-hardware.sh
  ✓ Downloaded: diagnose.sh
  ✓ Downloaded: verify.sh
=== STEP 1 COMPLETE ===
Next: Run step2-diagnostics.sh
```

---

### Step 2: Diagnostics (<2 min)

**Purpose:** Configure network interface and run connectivity tests.

```bash
# Run diagnostics
bash ./step2-diagnostics.sh

# REPORT (REQUIRED!)
echo "STEP 2: COMPLETE - DIAGNOSTIC_READY - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

**What it does:**
1. Configures enp7s0 with static IP (tether stays connected)
2. Runs interface-bound tests:
   - `ping -I enp7s0 192.168.0.1` (gateway)
   - `ping -I enp7s0 8.8.8.8` (internet)
3. Runs hardware detection
4. Posts diagnostics to Gist
5. Sets status to `DIAGNOSTIC_READY`

**Expected Output:**
```
=== STEP 2: DIAGNOSTICS (<2 min) ===
Working in: /home/friasc/network-troubleshooting-bundle
Configuring enp7s0...
  IP: 192.168.0.254/24
  Gateway: 192.168.0.1
Testing enp7s0...
  ✓ Gateway reachable
  ✓ Internet reachable
Running hardware detection...
  ✓ Saved to /tmp/hardware-report.txt
Running network diagnostics...
  ✓ Saved to /tmp/network-diagnosis.log
Posting diagnostics to Gist...
  ✓ Posted to Gist
  ✓ Status: DIAGNOSTIC_READY
=== STEP 2 COMPLETE ===
Next: Run step3-poll.sh
```

---

### Step 3: Poll & Execute (<10 min)

**Purpose:** Wait for cloud agent to post fix commands (if needed), execute, and verify.

```bash
# Run poll script
bash ./step3-poll.sh

# REPORT (REQUIRED!)
echo "STEP 3: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

**What it does:**
1. Polls Gist every 10 seconds for `node2-fix-commands.sh`
2. When found, downloads and executes fix commands
3. Posts execution results
4. Runs verification
5. Sets status to `COMPLETE`

**Scenarios:**

**A. All Tests Passed (No Fixes Needed):**
```
=== STEP 3: POLL & EXECUTE (<10 min) ===
Polling for fix commands...
  ✓ No issues detected - proceeding to verification
Running verification...
  ✓ All tests PASSED
=== STEP 3 COMPLETE ===
Status: COMPLETE
```

**B. Issues Detected (Fix Commands Executed):**
```
=== STEP 3: POLL & EXECUTE (<10 min) ===
Polling for fix commands...
✅ FIX COMMANDS RECEIVED!
Executing fixes...
  ✓ Fix applied successfully
Posting results...
  ✓ Results posted
Running verification...
  ✓ Verification PASSED
=== STEP 3 COMPLETE ===
Status: COMPLETE
```

---

## Common Issues

### Issue 1: Wrong Driver (r8169 vs r8168)

**Node:** fnet2  
**Symptoms:** Intermittent connectivity, no link  
**Root Cause:** Wrong driver loaded (r8169 instead of r8168)

**Resolution:**
```bash
# Blacklist wrong driver
echo "blacklist r8169" | sudo tee /etc/modprobe.d/blacklist-r8169.conf

# Install correct driver
sudo apt update
sudo apt install r8168-dkms

# Reboot
sudo reboot
```

---

### Issue 2: No IP Assigned

**Node:** fnet2  
**Symptoms:** Interface exists but no IP  
**Root Cause:** Interface not configured

**Resolution:**
```bash
# Assign static IP
sudo ip addr add 192.168.0.254/24 dev enp7s0
sudo ip link set enp7s0 up
sudo ip route add default via 192.168.0.1 dev enp7s0 metric 100
```

---

### Issue 3: Router Blocking

**Node:** fnet2  
**Symptoms:** Gateway works, internet fails  
**Root Cause:** MAC address filter or parental controls

**Resolution:**
1. Check router admin interface
2. Add MAC address to allowed list
3. Disable parental controls for this device
4. Retry connectivity test

---

### Issue 4: Tether Masking Diagnostics

**Symptom:** Can't tell if ethernet is working because tether provides internet

**Resolution:**
```bash
# Keep tether connected for Gist communication
# But test ethernet specifically with -I flag

ping -I enp7s0 192.168.0.1  # Tests enp7s0 only
ping -I enp7s0 8.8.8.8      # Tests enp7s0 only
```

**DO NOT disconnect tether** - it's needed for communication with cloud agent.

---

## Worker Node Documentation

### NODE2-AGENTS.md

**Purpose:** Lightweight worker context (~100 lines)  
**Location:** `~/network-troubleshooting-bundle/NODE2-AGENTS.md`  
**Download:** Always loaded at session start

**Key Sections:**
- Identity (worker, not orchestrator)
- Progress reporting requirement
- 2-minute rule
- Download-before-create rule
- Working directory management

### NODE2-REFERENCE.md

**Purpose:** Complete reference guide (~400 lines)  
**Location:** Download on-demand  
**When to Use:** When stuck, need detailed procedures

**Download:**
```bash
curl -sL "https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/NODE2-REFERENCE.md" -o ./NODE2-REFERENCE.md
```

**Includes:**
- Troubleshooting decision tree
- Emergency procedures
- Hallucination prevention
- Status state definitions
- Subagent usage guide

---

## Autonomous Monitoring

### Overview

Cloud agent monitors worker node progress with:
- **Check Interval:** 60 seconds
- **Response Time:** <60 seconds
- **Triggers:** STATUS updates, diagnostic posts, help requests

### Monitoring Script

```bash
# Run autonomous monitoring (background)
nohup bash /tmp/monitor-node2.sh > /tmp/node2-monitor.out 2>&1 &
```

### Response Triggers

| Trigger | Response Time | Action |
|---------|---------------|--------|
| `DIAGNOSTIC_READY` | <60 sec | Review, create fixes if needed |
| `RESULTS_READY` | <60 sec | Verify completion |
| `ESCALATED` | <60 sec | Investigate, respond |
| `node2-help.txt` | <60 sec | Provide guidance |
| Timeout (>10 min) | Immediate | Check, assist |

---

## Case Studies

### Case Study 1: Node 2 (fnet2) - Realtek NIC

**Issue:** enp7s0 ethernet not working  
**NIC:** Realtek RTL8111/8168/8211  
**Driver Issue:** r8169 (wrong) vs r8168 (correct)

**Resolution Steps:**
1. Hardware detection identified Realtek NIC
2. Found r8169 driver loaded (wrong)
3. Blacklisted r8169, installed r8168-dkms
4. Rebooted, interface came up correctly
5. Configured static IP
6. Verified connectivity

**Time:** ~15 minutes total  
**Outcome:** ✅ SUCCESS - enp7s0 working

---

### Case Study 2: Node 6 - Intel NUC

**Issue:** Network connectivity  
**NIC:** Intel (in-kernel driver)  
**Resolution:** [To be documented]

**Time:** [TBD]  
**Outcome:** ✅ SUCCESS - Online

---

### Case Study 3: Node 7 - Intel NUC

**Issue:** Network connectivity  
**NIC:** Intel (in-kernel driver)  
**Resolution:** [To be documented]

**Time:** [TBD]  
**Outcome:** ✅ SUCCESS - Online

---

## Appendix A: Quick Reference

### Essential Commands

```bash
# Set directory
cd ~/network-troubleshooting-bundle

# Download script
curl -sL "$GIST_URL/script.sh" -o ./script.sh

# Check status
cat ./node2-STATUS.md

# Post to Gist
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./file

# Test interface
ping -c 3 -W 2 -I enp7s0 192.168.0.1
```

### Status States

| State | Meaning |
|-------|---------|
| `INITIALIZING` | Starting |
| `STEP1_COMPLETE` | Setup done |
| `DIAGNOSTIC_READY` | Diagnostics posted |
| `FIXES_PENDING` | Polling for fixes |
| `RESULTS_READY` | Execution done |
| `COMPLETE` | All done |
| `ESCALATED` | Need help |

---

**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Prompt:** `/Users/friasc/Dropbox/workshop/technical-infrastructure/prompts/network-troubleshooting.md`  
**Version:** 1.0  
**Last Updated:** 2026-04-26
