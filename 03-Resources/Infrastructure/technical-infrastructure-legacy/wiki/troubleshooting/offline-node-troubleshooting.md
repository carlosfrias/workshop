# Offline Node Troubleshooting with Cloud-Assisted Diagnosis

**Created:** 2026-04-25  
**Pattern:** Decompose → Execute → Verify  
**Use Case:** Time-limited tether connections for offline node repair

---

## Overview

When troubleshooting offline nodes with expensive/time-limited internet connections (e.g., phone tethering), minimize cloud connection time by:

1. **Cloud phase (tether connected):** Hardware diagnosis, model selection, decomposition planning
2. **Local phase (tether disconnected):** Autonomous diagnostics, fix application, verification
3. **Cloud phase (brief reconnection):** Verification and approval

This pattern reduces tether time from **hours** to **~15 minutes per node**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TETHER SESSION 1 (Setup)                     │
│                    Duration: 10-15 minutes                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Install pi + Ollama                                         │
│  2. Run detect-hardware.sh → Cloud diagnosis                    │
│  3. Run benchmark-model.sh → Cloud model selection              │
│  4. Download recommended model                                  │
│  5. Deploy troubleshooting agents                               │
│  6. DISCONNECT TETHER                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OFFLINE WORK (Autonomous)                    │
│                    Duration: 30-45 minutes                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Run diagnose.sh (local agent)                               │
│  2. Apply fixes per decomposition plan                          │
│  3. Run verify.sh                                               │
│  4. Write status to /tmp/node-ready.txt                         │
│  5. Signal: "COMPLETE" or "FAILED: <reason>"                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 TETHER SESSION 2 (Verification)                 │
│                    Duration: 1-2 minutes                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Reconnect tether                                            │
│  2. Upload verification log to cloud agent                      │
│  3. Cloud agent confirms: COMPLETE or iterate                   │
│  4. DISCONNECT TETHER                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Bundle

### Contents

```
network-troubleshooting-bundle.tar.gz
├── README.md                     # Quick-start instructions
├── SESSION-RECREATION.md         # Prompt for recreating this session
├── .pi/
│   ├── agents/
│   │   ├── technical-infrastructure.md   # Local execution agent
│   │   └── verifier.md                   # Cloud verification agent
│   └── model-router.json                 # Automatic model routing
└── scripts/
    ├── install-ollama.sh         # Ollama installer
    ├── detect-hardware.sh        # Hardware detection
    ├── benchmark-model.sh        # Model capacity test
    ├── diagnose.sh               # Network diagnostics
    ├── apply-fix.sh              # Fix application
    └── verify.sh                 # Post-fix verification
```

### Download Location

**Gist:** `[PENDING - Upload to Gist after review]`

**Alternative:** Copy bundle from orchestrator via USB drive:
```bash
# On orchestrator (Mac):
tar -czvf /tmp/nt-bundle.tar.gz -C ~/Dropbox/workshop/technical-infrastructure/archive/deployment-examples/network-troubleshooting .

# Copy to USB drive, then to target node
```

---

## Quick Start (On Target Node)

### Step 1: Download Bundle

```bash
# From Gist (replace <GIST_ID>)
curl -L https://gist.github.com/<GIST_ID>/raw/network-troubleshooting-bundle.tar.gz -o /tmp/nt-bundle.tar.gz
cd ~ && tar -xzf /tmp/nt-bundle.tar.gz
cd ~/network-troubleshooting-bundle
```

### Step 2: Install pi

```bash
sudo npm install -g @mariozechner/pi-coding-agent
pi --version
```

### Step 3: Install Ollama

```bash
chmod +x ~/network-troubleshooting-bundle/scripts/install-ollama.sh
sudo ~/network-troubleshooting-bundle/scripts/install-ollama.sh
ollama serve &
```

### Step 4: Connect Tether

```bash
# Connect phone via USB, enable tethering
ping -c 3 8.8.8.8  # Verify connectivity
```

### Step 5: Hardware Detection

```bash
chmod +x ~/network-troubleshooting-bundle/scripts/detect-hardware.sh
~/network-troubleshooting-bundle/scripts/detect-hardware.sh > /tmp/hardware-report.txt
cat /tmp/hardware-report.txt
# → PASTE ENTIRE OUTPUT TO CLOUD AGENT
```

### Step 6: Model Benchmark

```bash
chmod +x ~/network-troubleshooting-bundle/scripts/benchmark-model.sh
~/network-troubleshooting-bundle/scripts/benchmark-model.sh > /tmp/benchmark-report.txt
cat /tmp/benchmark-report.txt
# → PASTE ENTIRE OUTPUT TO CLOUD AGENT
```

### Step 7: Follow Cloud Agent Instructions

Cloud agent will provide:
1. Recommended Ollama model
2. Required driver packages
3. Decomposition plan

### Step 8: Deploy Agents

```bash
cp -r ~/network-troubleshooting-bundle/.pi ~/.pi
pi agents list
```

### Step 9: Disconnect Tether

```bash
# Disable tether on phone
# Node will work offline from here
```

### Step 10: Run Diagnostics

```bash
chmod +x ~/network-troubleshooting-bundle/scripts/diagnose.sh
~/network-troubleshooting-bundle/scripts/diagnose.sh
```

### Step 11: Apply Fixes

Follow cloud agent's decomposition plan:
```bash
chmod +x ~/network-troubleshooting-bundle/scripts/apply-fix.sh
~/network-troubleshooting-bundle/scripts/apply-fix.sh <fix_number> [options]
```

### Step 12: Verify

```bash
chmod +x ~/network-troubleshooting-bundle/scripts/verify.sh
~/network-troubleshooting-bundle/scripts/verify.sh
cat /tmp/node-ready.txt
```

**Expected output:** `COMPLETE`

### Step 13: Reconnect for Verification

```bash
# Reconnect tether
# Paste /tmp/network-verify-*.log to cloud agent
# Wait for confirmation
```

---

## Hardware Detection Guide

### Intel NUCs (Nodes 6, 7)

**Likely NICs:**
- Intel I219-V → `e1000e` driver (in-kernel)
- Intel I225-V → `igc` driver (in-kernel)
- Intel I350 → `igb` driver (in-kernel)

**Common Issues:**
- NetworkManager configuration
- Firmware/EEPROM corruption
- Cable/port problems
- Router-side access control

**Fixes:**
```bash
# Install Intel firmware
sudo apt-get install -y firmware-intel intel-microcode

# Restart NetworkManager
sudo systemctl restart NetworkManager

# Renew DHCP
sudo dhclient -v eth0
```

### Unknown Hardware (Node 2, Ubuntu 26.04)

**Possible NICs:**
- Realtek RTL8168H → `r8168` driver (external, known issue with `r8169`)
- Realtek RTL8125 → `r8125` driver (external)

**Symptoms of r8169 Issue:**
- Can ping gateway but not 8.8.8.8
- tcpdump shows packets leaving, no replies
- Router logs show no blocks

**Fix:**
```bash
sudo apt-get install -y r8168-dkms
sudo modprobe -r r8169
sudo modprobe r8168
sudo systemctl restart NetworkManager
```

---

## Model Selection Guide

| RAM | CPU Cores | Recommended Model | Size |
|-----|-----------|-------------------|------|
| ≥16 GB | ≥8 | `qwen3:8b` | ~2GB |
| 8-16 GB | ≥4 | `qwen3.5:4b` or `gemma4:e4b` | ~1GB |
| 4-8 GB | ≥4 | `llama3.2:3b` or `phi3:3.8b` | ~500MB |
| <4 GB | <4 | `qwen3.5:cloud` (cloud-only) | N/A |

**Note:** For troubleshooting tasks, local models handle diagnostics; cloud model handles diagnosis and verification.

---

## Output Files

| File | Purpose | When to Share |
|------|---------|---------------|
| `/tmp/hardware-report.txt` | Hardware detection | Tether Session 1 |
| `/tmp/benchmark-report.txt` | Model capacity test | Tether Session 1 |
| `/tmp/network-diagnosis-*.log` | Diagnostic session | After offline work |
| `/tmp/network-fix-*.log` | Fix application | After applying fixes |
| `/tmp/network-verify-*.log` | Verification results | Tether Session 2 |
| `/tmp/node-ready.txt` | Status signal | Check before reconnecting |

---

## Troubleshooting

### pi Installation Fails

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Retry pi installation
sudo npm install -g @mariozechner/pi-coding-agent
```

### Ollama Won't Start

```bash
# Check if port is in use
sudo lsof -i :11434

# Kill existing process
sudo kill $(sudo lsof -t -i :11434)

# Start fresh
ollama serve &
```

### Model Download Too Slow

```bash
# Use smaller model
ollama pull llama3.2:3b

# Or use cloud-only mode (requires tether)
```

### Verification Fails

1. Check `/tmp/network-verify-*.log` for failed tests
2. Identify root cause:
   - Gateway unreachable → Check cable, port, NIC
   - DNS fails → Set DNS to 8.8.8.8
   - High packet loss → Try different cable/port, reinstall driver
3. Apply targeted fix
4. Re-run verification

---

## Time Budget

| Phase | Per Node | Total (3 nodes) |
|-------|----------|-----------------|
| Tether Session 1 | 10-15 min | 30-45 min |
| Offline Work | 30-45 min | 90-135 min (parallel) |
| Tether Session 2 | 1-2 min | 3-6 min |
| **Total Tether Time** | **~15 min** | **~45 min** |
| **Total Elapsed** | **~60 min** | **~180 min** (sequential) |

**Note:** Offline work can be parallelized across nodes.

---

## Session Recreation

To recreate this exact session for additional nodes or future incidents, see:

**`SESSION-RECREATION.md`** in the deployment bundle.

Copy the "Context to Provide Cloud Agent" section and paste it to a new pi session.

---

## See Also

- [Decompose → Execute → Verify Pattern](/technical-infrastructure/reference/decompose-execute-verify-pattern)
- [Network Troubleshooting Guide](/technical-infrastructure/troubleshooting/network-troubleshooting-guide)
- [pi-keyword-router](/technical-infrastructure/products/pi-keyword-router)
