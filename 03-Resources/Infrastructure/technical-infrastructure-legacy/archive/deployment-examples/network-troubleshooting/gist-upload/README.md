# Network Troubleshooting Deployment Bundle

**Version:** 1.0  
**Created:** 2026-04-25  
**Purpose:** Deploy offline nodes with pi + Ollama + troubleshooting chain

---

## Quick Start (Copy-Paste Instructions)

### Option A: Automated Setup Script (Recommended)

**The Gist includes a ready-to-run setup script in the Gist comment.**

1. **Download the Gist comment** (copy-paste instructions):
   - Go to the Gist URL
   - Copy the entire "Setup Script (Copy-Paste)" section from the Gist comment
   - Paste into terminal on target node
   - Script runs all steps automatically

2. **Wait for script to complete** (~8-12 minutes)

3. **Copy reports to cloud agent**:
   - `/tmp/hardware-report.txt` → Paste to cloud agent
   - `/tmp/benchmark-report.txt` → Paste to cloud agent

4. **Follow cloud agent instructions** for model selection and decomposition plan

### Option B: Manual Step-by-Step

If you prefer manual execution, follow the steps below.

### Step 1: Download and Extract

```bash
# Download from Gist (replace <GIST_ID> with actual)
curl -L https://gist.github.com/<GIST_ID>/raw/network-troubleshooting-bundle.tar.gz -o /tmp/nt-bundle.tar.gz

# Extract to home directory
cd ~ && tar -xzf /tmp/nt-bundle.tar.gz

# Enter bundle directory
cd ~/network-troubleshooting-bundle
```

### Step 2: Install pi

```bash
# Install pi coding agent globally
sudo npm install -g @mariozechner/pi-coding-agent

# Verify installation
pi --version
```

### Step 3: Install Ollama

```bash
# Run Ollama installer
chmod +x ~/network-troubleshooting-bundle/scripts/install-ollama.sh
sudo ~/network-troubleshooting-bundle/scripts/install-ollama.sh

# Start Ollama service
ollama serve &

# Verify Ollama is running
ollama list
```

### Step 4: Connect to Internet (Phone Tether)

```bash
# Connect phone via USB and enable tethering
# Wait for network to connect, then verify:
ping -c 3 8.8.8.8
```

### Step 5: Run Hardware Detection

```bash
# Detect hardware (NIC, driver, system info)
chmod +x ~/network-troubleshooting-bundle/scripts/detect-hardware.sh
~/network-troubleshooting-bundle/scripts/detect-hardware.sh > /tmp/hardware-report.txt

# Review the report
cat /tmp/hardware-report.txt
```

**📋 Copy the entire output of `/tmp/hardware-report.txt` and paste it to the cloud agent for diagnosis.**

### Step 6: Run Model Benchmark

```bash
# Benchmark local model capacity
chmod +x ~/network-troubleshooting-bundle/scripts/benchmark-model.sh
~/network-troubleshooting-bundle/scripts/benchmark-model.sh > /tmp/benchmark-report.txt

# Review the report
cat /tmp/benchmark-report.txt
```

**📋 Copy the entire output of `/tmp/benchmark-report.txt` and paste it to the cloud agent for model selection.**

### Step 7: Wait for Cloud Agent Instructions

The cloud agent will provide:
1. **Recommended Ollama model** (based on benchmark)
2. **Required driver packages** (based on hardware detection)
3. **Decomposition plan** for network troubleshooting

Follow the cloud agent's instructions exactly.

### Step 8: Deploy Troubleshooting Chain

After cloud agent provides the plan:

```bash
# Copy .pi folder to home directory
cp -r ~/network-troubleshooting-bundle/.pi ~/.pi

# Verify agents are registered
pi agents list
```

### Step 9: Run Diagnostics (Offline)

Once the cloud agent confirms setup is complete, you can disconnect the tether:

```bash
# Run the diagnostic chain
pi "Run network diagnostics on this node and report findings"
```

### Step 10: Signal Completion

When the node completes its work:

```bash
# Check completion status
cat /tmp/node-ready.txt
```

**Expected output:** `COMPLETE` or `FAILED: <reason>`

---

## File Structure

```
network-troubleshooting-bundle/
├── README.md                     # This file
├── .pi/
│   ├── agents/
│   │   ├── technical-infrastructure.md   # Infrastructure agent
│   │   └── verifier.md                   # Verification agent
│   ├── model-router.json                 # Model routing config
│   └── agents.json                       # Agent registry
└── scripts/
    ├── install-ollama.sh         # Ollama installer
    ├── detect-hardware.sh        # Hardware detection
    ├── benchmark-model.sh        # Model capacity test
    ├── diagnose.sh               # Network diagnostics
    ├── apply-fix.sh              # Apply fixes
    └── verify.sh                 # Post-fix verification
```

---

## Troubleshooting

### pi Installation Fails

```bash
# Check npm is installed
npm --version

# If not, install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Retry pi installation
sudo npm install -g @mariozechner/pi-coding-agent
```

### Ollama Installation Fails

```bash
# Check if Ollama is already installed
which ollama

# If installed but not working, restart service
sudo systemctl restart ollama
ollama list
```

### Network Not Working After Tether

```bash
# Check interface status
ip addr show

# Check routing table
ip route show

# Try renewing DHCP lease
sudo dhclient -v

# Check DNS resolution
cat /etc/resolv.conf
ping -c 3 google.com
```

---

## Completion Signal

The node writes its status to `/tmp/node-ready.txt`:

| Content | Meaning |
|---------|---------|
| `COMPLETE` | All diagnostics and fixes applied successfully |
| `FAILED: <reason>` | Issue encountered, see reason |
| (file not present) | Work still in progress |

**When you see `COMPLETE`, reconnect the tether and notify the cloud agent for verification.**

---

## Support

If you encounter issues during deployment:
1. Keep the tether connected
2. Copy error messages
3. Paste to cloud agent for troubleshooting
