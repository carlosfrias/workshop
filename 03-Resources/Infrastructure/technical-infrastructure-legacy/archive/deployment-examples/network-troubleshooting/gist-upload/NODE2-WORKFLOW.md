# Node 2 Troubleshooting Workflow

**Lightweight, step-by-step execution for better performance**

---

## Quick Start (All Steps)

```bash
# Step 1: Authenticate
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step1-auth.sh | bash

# Step 2: Download scripts
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash

# Step 3: Run diagnostics
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step3-diagnose.sh | bash

# Step 4: Post to cloud (automatic)
# Step 5: Wait for fix commands (automatic)
# Step 6: Execute fixes (automatic)
# Step 7: Verify (automatic)
```

---

## Step-by-Step Details

### Step 1: Authentication (~2 min)
**Purpose:** Enable Gist communication  
**Script:** `node2-step1-auth.sh`  
**What it does:**
- Installs GitHub CLI (`gh`)
- Authenticates with GitHub
- Verifies access

**Run:**
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step1-auth.sh | bash
```

---

### Step 2: Download Scripts (~30 sec)
**Purpose:** Get all troubleshooting scripts  
**Script:** `node2-step2-download.sh`  
**What it does:**
- Downloads communication script (`gist-comm.sh`)
- Downloads diagnostic scripts
- Downloads fix scripts
- Makes all executable

**Run:**
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash
```

---

### Step 3: Run Diagnostics (~2 min)
**Purpose:** Test network without tether  
**Script:** `node2-step3-diagnose.sh`  
**What it does:**
- Disconnects tether automatically
- Waits for routes to clear
- Assigns static IP to ethernet
- Tests gateway and internet
- Generates diagnostic report

**Run:**
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step3-diagnose.sh | bash
```

---

### Step 4: Post to Cloud (Automatic)
**Purpose:** Send diagnostics to cloud agent  
**Script:** Called by Step 3  
**What it does:**
- Posts `node2-diagnostic.txt` to Gist
- Updates `node2-STATUS.md` to `DIAGNOSTIC_READY`
- Notifies cloud agent

**Automatic** - no action needed

---

### Step 5: Wait for Fix Commands (Automatic, ~1-5 min)
**Purpose:** Receive fix commands from cloud  
**Script:** Polling loop in Step 3  
**What it does:**
- Polls Gist every 10 seconds
- Checks for `node2-fix-commands.sh`
- Downloads when available

**Automatic** - no action needed

---

### Step 6: Execute Fixes (Automatic, ~1 min)
**Purpose:** Apply cloud agent's fix commands  
**Script:** Auto-executed when received  
**What it does:**
- Runs fix commands from cloud
- Captures output
- Posts results to Gist

**Automatic** - no action needed

---

### Step 7: Verify (Automatic, ~1 min)
**Purpose:** Confirm fix worked  
**Script:** Auto-executed after fixes  
**What it does:**
- Runs verification tests
- Posts results to cloud
- Marks `COMPLETE` if successful

**Automatic** - no action needed

---

## Manual Commands (If Needed)

### Check Status
```bash
~/gist-comm.sh status
```

### Send Message to Cloud
```bash
~/gist-comm.sh send diagnostic /tmp/hardware-report.txt
```

### Receive Commands from Cloud
```bash
~/gist-comm.sh recv fix-commands
```

### Check Gist Files
```bash
curl -s https://api.github.com/gists/0c517214489cb78c0484ca661f3d8463 | python3 -c "import sys,json; [print(k) for k in json.load(sys.stdin).get('files',{}).keys()]"
```

---

## Workflow State Machine

```
START
  │
  ▼
┌─────────────────┐
│ Step 1: Auth    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 2: Download│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 3: Diagnose│───────┐
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ Step 4: Post    │       │
└────────┬────────┘       │
         │                │
         ▼                │
┌─────────────────┐       │
│ Step 5: Wait    │◄──────┘ (polling)
└────────┬────────┘
         │ (fixes received)
         ▼
┌─────────────────┐
│ Step 6: Execute │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Step 7: Verify  │
└────────┬────────┘
         │
         ▼
       COMPLETE
```

---

## Troubleshooting

### Step Fails
```bash
# Re-run just that step
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash
```

### Script Too Slow
Each step is <50 lines and runs in <2 minutes. If still slow, run commands manually:

```bash
# Manual auth
gh auth login

# Manual download
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/gist-comm.sh -o ~/gist-comm.sh && chmod +x ~/gist-comm.sh

# Manual diagnose
~/manage-tether.sh down && sudo ip addr add 192.168.0.254/24 dev enp7s0 && ping -c 2 192.168.0.1
```

### Gist Not Updating
```bash
# Check auth
gh auth status

# Try manual post
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/hardware-report.txt
```

---

**Start with Step 1 and proceed sequentially.** Each step completes in under 2 minutes.
