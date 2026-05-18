# Network Troubleshooting Prompt

**Purpose:** Systematic network troubleshooting for offline nodes  
**Domain:** Technical Infrastructure  
**Use When:** Node is offline, unreachable, or has network connectivity issues

---

## 🎯 Initial Assessment

```
You are a technical infrastructure specialist troubleshooting network connectivity on a remote node.

CONTEXT:
- Node: [NODE_NAME, e.g., fnet2, fnet6, fnet7]
- User: [USER_NAME, e.g., friasc]
- Home Directory: /home/[USER]/
- Working Directory: /home/[USER]/network-troubleshooting-bundle/

INITIAL QUESTIONS:
1. What is the node hostname?
2. What network interfaces are available? (enp7s0, eth0, etc.)
3. Is there a phone tether or alternative connectivity available?
4. What is the expected IP configuration?
   - IP Address: [e.g., 192.168.0.254]
   - Subnet: [e.g., /24]
   - Gateway: [e.g., 192.168.0.1]
   - DNS: [e.g., 8.8.8.8]

FIRST STEPS:
1. Establish communication channel (GitHub Gist, SSH, etc.)
2. Download troubleshooting scripts from Gist
3. Run hardware detection
4. Test interface-specific connectivity
5. Report findings to cloud agent
```

---

## 🔧 Step-by-Step Workflow

### Step 1: Establish Communication

```bash
# Set working directory
cd /home/[USER]/network-troubleshooting-bundle
pwd
# Verify: /home/[USER]/network-troubleshooting-bundle

# Download troubleshooting scripts from Gist
GIST_URL="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"

curl -sL "$GIST_URL/step1-setup.sh" -o ./step1-setup.sh && chmod +x ./step1-setup.sh
curl -sL "$GIST_URL/step2-diagnostics.sh" -o ./step2-diagnostics.sh && chmod +x ./step2-diagnostics.sh
curl -sL "$GIST_URL/step3-poll.sh" -o ./step3-poll.sh && chmod +x ./step3-poll.sh
curl -sL "$GIST_URL/NODE2-AGENTS.md" -o ./NODE2-AGENTS.md

# Initialize status
echo "INITIALIZING" > ./node2-STATUS.md
```

---

### Step 2: Hardware Detection

```bash
# Run hardware detection script
./detect-hardware.sh > /tmp/hardware-report.txt

# Review output
cat /tmp/hardware-report.txt

# Key information to extract:
# - NIC model (Realtek, Intel, etc.)
# - Driver in use (r8168, r8169, e1000e, etc.)
# - MAC address
# - Interface name (enp7s0, eth0, etc.)
```

**Expected Output:**
```
Interface: enp7s0
  MAC: 0c:9d:92:cc:55:4c
  Driver: r8168
  State: UP/DOWN
  IP: [assigned IP or none]
```

---

### Step 3: Interface Configuration

```bash
# Configure interface (tether stays connected for internet access)
ETHERNET_IFACE="enp7s0"  # Change based on hardware detection
TARGET_IP="192.168.0.254"  # Change based on network
GATEWAY="192.168.0.1"

# Clean interface
sudo ip addr flush dev $ETHERNET_IFACE

# Assign IP
sudo ip addr add $TARGET_IP/24 dev $ETHERNET_IFACE

# Bring up
sudo ip link set $ETHERNET_IFACE up

# Add gateway route (higher metric so tether is fallback)
sudo ip route add default via $GATEWAY dev $ETHERNET_IFACE metric 100

# Verify
ip -br addr show $ETHERNET_IFACE
```

---

### Step 4: Interface-Bound Testing

```bash
# Test gateway through specific interface (tether stays connected)
ping -c 3 -W 2 -I $ETHERNET_IFACE $GATEWAY

# Test internet through specific interface
ping -c 3 -W 2 -I $ETHERNET_IFACE 8.8.8.8

# Test DNS through specific interface
ping -c 3 -W 2 -I $ETHERNET_IFACE google.com

# Record results
GATEWAY_OK=$([ $? -eq 0 ] && echo "PASS" || echo "FAIL")
INTERNET_OK=$([ $? -eq 0 ] && echo "PASS" || echo "FAIL")
```

**Interpretation:**
| Gateway | Internet | Diagnosis |
|---------|----------|-----------|
| PASS | PASS | ✅ Interface working |
| PASS | FAIL | ⚠️ Router blocking (MAC filter, firewall) |
| FAIL | FAIL | ✗ Physical/link issue (cable, port, NIC) |
| FAIL | PASS | 🚨 Impossible - check test |

---

### Step 5: Post Diagnostics

```bash
# Combine diagnostics
cat /tmp/hardware-report.txt > /tmp/node2-diagnostic.txt
echo "" >> /tmp/node2-diagnostic.txt
echo "=== INTERFACE TESTS ===" >> /tmp/node2-diagnostic.txt
echo "Time: $(date)" >> /tmp/node2-diagnostic.txt
echo "Interface: $ETHERNET_IFACE" >> /tmp/node2-diagnostic.txt
echo "Gateway Test: $GATEWAY_OK" >> /tmp/node2-diagnostic.txt
echo "Internet Test: $INTERNET_OK" >> /tmp/node2-diagnostic.txt

# Post to Gist
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-diagnostic.txt

# Update status
echo "DIAGNOSTIC_READY" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# Report to cloud agent
echo "Diagnostics posted - awaiting analysis" > ./node2-progress.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-progress.txt
```

---

### Step 6: Cloud Agent Analysis

**Cloud Agent will:**
1. Review diagnostics within 60 seconds
2. Identify root cause (driver, IP, gateway, router blocking, hardware)
3. Create fix commands if needed
4. Post `node2-fix-commands.sh` to Gist

**Wait for fix commands:**
```bash
# Poll for fix commands (10-second intervals, 10-minute timeout)
for i in {1..60}; do
    if curl -sL "$GIST_URL/node2-fix-commands.sh" | grep -q "^#"; then
        curl -sL "$GIST_URL/node2-fix-commands.sh" -o ./fixes.sh
        chmod +x ./fixes.sh
        bash ./fixes.sh
        break
    fi
    sleep 10
done
```

---

### Step 7: Execute Fixes

```bash
# Fix commands are posted by cloud agent
# Execute and report results

bash ./fixes.sh
EXIT_CODE=$?

# Post results
echo "Fix executed at $(date)" > /tmp/node2-results.txt
echo "Exit code: $EXIT_CODE" >> /tmp/node2-results.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-results.txt

# Update status
echo "RESULTS_READY" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

### Step 8: Verification

```bash
# Run verification script
./verify.sh

# Check node-ready status
cat /tmp/node-ready.txt

# Post verification
cat /tmp/node-ready.txt > /tmp/node2-verification.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add /tmp/node2-verification.txt

# Mark complete
echo "COMPLETE" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

## 🚨 Common Issues & Fixes

### Issue 1: Wrong Driver (r8169 vs r8168)

**Symptoms:**
- Interface shows `r8169` driver but hardware needs `r8168`
- Intermittent connectivity or no link

**Fix:**
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

**Symptoms:**
- Interface exists but no IP address
- `ip addr show` shows interface without inet address

**Fix:**
```bash
# Assign static IP
sudo ip addr add 192.168.0.254/24 dev enp7s0
sudo ip link set enp7s0 up
sudo ip route add default via 192.168.0.1 dev enp7s0 metric 100

# Or use DHCP
sudo dhclient enp7s0
```

---

### Issue 3: Gateway Unreachable

**Symptoms:**
- `ping -I enp7s0 192.168.0.1` fails
- Link is up but no response from gateway

**Possible Causes:**
- Bad ethernet cable
- Wrong router port
- Router port disabled
- NIC hardware failure

**Troubleshooting:**
```bash
# Check link status
ethtool enp7s0 | grep "Link detected"

# Try different cable
# Try different router port
# Check router admin interface for port status
```

---

### Issue 4: Router Blocking

**Symptoms:**
- Gateway ping works
- Internet ping fails
- DNS fails

**Possible Causes:**
- MAC address filter
- Parental controls
- Firewall rules
- Device not authorized

**Fix:**
```bash
# Check router admin interface
# Add MAC address to allowed list
# Disable parental controls for this device
# Check firewall rules

# MAC address from hardware report:
cat /tmp/hardware-report.txt | grep -A 5 "Interface: enp7s0"
```

---

### Issue 5: Tether Masking Diagnostics

**Symptoms:**
- Tether is connected and provides internet
- Can't tell if ethernet is working
- Tests use tether route instead of ethernet

**Fix:**
```bash
# Keep tether connected for internet access
# But test ethernet specifically with -I flag

ping -I enp7s0 192.168.0.1  # Tests enp7s0 specifically
ping -I enp7s0 8.8.8.8      # Tests enp7s0 specifically

# DO NOT disconnect tether - needed for Gist communication
```

---

## 📋 Progress Reporting

**After EVERY step, report to cloud agent:**

```bash
# After Step 1
echo "STEP 1: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# After Step 2
echo "STEP 2: COMPLETE - DIAGNOSTIC_READY - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md

# After Step 3
echo "STEP 3: COMPLETE - $(date)" > ./node2-STATUS.md
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add ./node2-STATUS.md
```

---

## 🤖 Subagent Usage

**Use subagent for:**
- Downloading multiple files
- Complex log analysis
- Cross-referencing documentation

**Don't use subagent for:**
- Reporting progress (worker responsibility)
- Running step scripts (execute locally)
- Updating status files (worker responsibility)

**Example:**
```bash
# Good: Delegate downloads
pi "Download all troubleshooting scripts from Gist to ~/network-troubleshooting-bundle"

# Good: Delegate analysis
pi "Analyze this hardware report and identify the NIC driver issue: [paste report]"

# Bad: Don't delegate responsibilities
pi "Update node2-STATUS.md"  ← WRONG!
```

---

## 📊 Efficiency Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| Script size | >50 lines | Request decomposition |
| Step time | >2 minutes | Report, request help |
| Polling time | >10 minutes | Escalate |
| Health check | Every 5 minutes | Run automatically |

---

## 📁 Files Reference

**Download from Gist:**
- `NODE2-AGENTS.md` - Worker context (~100 lines)
- `NODE2-REFERENCE.md` - Complete reference (~400 lines)
- `step1-setup.sh` - Setup script
- `step2-diagnostics.sh` - Diagnostics script
- `step3-poll.sh` - Poll & execute script
- `context-health-check.sh` - Health monitoring
- `detect-hardware.sh` - Hardware detection
- `diagnose.sh` - Network diagnostics
- `verify.sh` - Verification

**Create locally:**
- `node2-STATUS.md` - Workflow status
- `node2-diagnostic.txt` - Diagnostic output
- `node2-results.txt` - Execution results
- `node2-help.txt` - Help requests
- `node2-progress.txt` - Progress reports

---

**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463  
**Version:** 1.0  
**Last Updated:** 2026-04-26
