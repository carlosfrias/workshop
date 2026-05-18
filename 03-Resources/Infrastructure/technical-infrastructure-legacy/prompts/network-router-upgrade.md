# Network Router Upgrade for AI-Friendly Trading Lab

**Created:** 2026-04-24  
**Status:** Pending Hardware Purchase  
**Domain:** Technical Infrastructure  
**Priority:** Medium (planning phase)

---

## Overview

Upgrade the trading lab network infrastructure to support AI-friendly management via natural language prompts, with hardware optimized for HFT (High-Frequency Trading) workloads.

---

## Requirements

### Functional Requirements
- [ ] **HFT-capable wired network** for trading execution systems (ultra-low latency)
- [ ] **WiFi 7** for laptops and non-trading devices (Roku, monitoring)
- [ ] **AI prompt-based management** via pi agent integration
- [ ] **Traffic optimization** for trading VLAN prioritization
- [ ] **Network analytics** and latency monitoring
- [ ] **Configuration maintenance** as trading lab needs evolve
- [ ] **~20-30 devices** typical load
- [ ] **Fiber internet** connection (SFP+ WAN)

### Constraints
- [ ] **Budget:** ~$800 (flexible if justified)
- [ ] **No Docker** — all software must run as native binaries or Python packages
- [ ] **Fresh deployment** — no existing UniFi infrastructure
- [ ] **Data privacy:** All management data stays local (no cloud dependencies)

---

## Hardware Recommendation

### Proposed Bill of Materials

| Component | Model | Price (USD) | Purpose |
|-----------|-------|-------------|---------|
| **Router/Gateway** | Ubiquiti UniFi Cloud Gateway Fiber | $279 | Routing, firewall, UniFi Controller |
| **Switch** | Ubiquiti UniFi Switch Pro 24 PoE | $299 | Low-latency wired connections, PoE for AP |
| **WiFi Access Point** | Ubiquiti U7 Pro (WiFi 7) | $179 | Wireless for laptops/Roku |
| **Total** | | **$757** | |

### Why This Hardware?

**Cloud Gateway Fiber:**
- 5 Gbps IDS/IPS throughput
- 3x 10G ports (SFP+), 4x 2.5G LAN ports
- Built-in UniFi Controller (no separate software needed)
- Optimized for fiber internet (SFP+ WAN port)
- Proven low-latency performance in reviews

**Switch Pro 24 PoE:**
- Hardware-accelerated switching (sub-microsecond latency)
- 24 ports with PoE (powers the AP)
- VLAN support for traffic segmentation
- Layer 3 routing capabilities

**U7 Pro (WiFi 7):**
- Wi-Fi 7 (802.11be) with 6GHz band
- AI-driven Radio Resource Management (RRM)
- 10G uplink port
- Optimized for dense device environments

### Network Architecture

```
                    Fiber Internet
                          │
                          ▼
            ┌─────────────────────────┐
            │ Cloud Gateway Fiber     │
            │ (Router + Controller)   │
            └───────────┬─────────────┘
                        │
                        ▼
            ┌─────────────────────────┐
            │ Switch Pro 24 PoE       │
            ├─────────┬───────────────┤
            │         │               │
            ▼         ▼               ▼
    Trading PCs   U7 Pro AP      Other Wired
    (VLAN 10)     (WiFi 7)       Devices
    Wired Only    VLAN 20/30
```

### VLAN Plan

| VLAN ID | Name | Purpose | Priority |
|---------|------|---------|----------|
| 10 | Trading | Execution systems (wired only) | Highest |
| 20 | Research | Laptops, monitoring | High |
| 30 | General | Roku, IoT, guests | Normal |

---

## Software Architecture

### MCP Server Integration

**Selected:** `enuno/unifi-mcp-server` (Python package)

**Why this over alternatives:**
- ✅ No Docker required
- ✅ No compilation (Go not needed)
- ✅ Simple `pip install`
- ✅ 50+ tools covers all common management tasks
- ✅ Published on PyPI (well-maintained)
- ✅ Supports 3 API modes for flexibility

**Alternatives considered:**
- `oliverames/ames-unifi-mcp` — 310 tools but requires Go compilation
- `h-cli` — Rejected (requires Docker)

### Integration Flow

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Pi Agent     │───▶│ unifi-mcp-server │───▶│ UniFi Controller│
│ (trading     │    │ (Python process) │    │ (Cloud Gateway) │
│  workspace)  │    │                  │    │                 │
└──────────────┘    └──────────────────┘    └─────────────────┘
```

### Example Prompts (Post-Installation)

```
"List all devices on VLAN 10 (Trading)"
"Show network latency for the last hour"
"Prioritize traffic from MAC address XX:XX:XX during market hours"
"Block Roku access 9:30-16:00 ET on trading days"
"Generate a network health report"
"What's the throughput on port 3?"
"Create a new VLAN for research laptops"
```

---

## Installation Steps (To Execute After Hardware Arrives)

### Step 1: Install MCP Server

```bash
# Activate trading workspace venv
cd /Users/friasc/Dropbox/workshop
source .venv/bin/activate

# Install MCP server
pip install unifi-mcp-server
```

### Step 2: Configure Pi Agent

Create/edit `~/.pi/agent/mcp.json`:

```json
{
  "mcpServers": {
    "unifi": {
      "command": "unifi-mcp-server",
      "args": [
        "--host", "https://192.168.1.1:8443",
        "--username", "admin",
        "--password", "<YOUR_PASSWORD>"
      ]
    }
  }
}
```

**Note:** Replace `192.168.1.1` with actual Cloud Gateway IP after setup.

### Step 3: Restart Pi

```bash
# Restart pi to load MCP configuration
# (Method depends on how pi is running)
```

### Step 4: Verify Integration

```
# In pi agent, test with:
"Show me all connected devices"
"List UniFi MCP tools available"
```

### Step 5: Configure Network

Via pi prompts:
```
"Create VLAN 10 named 'Trading' with highest priority"
"Create VLAN 20 named 'Research'"
"Create VLAN 30 named 'General'"
"Assign port 1-8 to VLAN 10"
"Configure WiFi SSID 'Trading-Lab' with VLAN 20"
"Configure WiFi SSID 'Trading-Guest' with VLAN 30"
```

---

## HFT Latency Considerations

### Critical Notes

⚠️ **HFT execution systems MUST be wired** — WiFi introduces unacceptable jitter:
- WiFi latency: 2-10ms with high variance
- Wired latency: <0.1ms with minimal variance
- A 1ms delay can cost millions in HFT strategies

### Unknown: Actual Latency Requirements

**To Determine:**
- What is the strategy's maximum acceptable latency?
- Is this true HFT (microseconds) or low-latency trading (milliseconds)?
- Do we need FPGA-accelerated NICs?
- Is co-location required for the strategy?

**Recommended Action:**
Before purchasing hardware, consult with the trading strategy developer to confirm:
1. Target latency (microseconds vs milliseconds)
2. Maximum acceptable jitter
3. Whether this setup is for research/backtesting or live execution
4. If live execution, what's the broker/data center location?

**If true HFT (microsecond latency required):**
- This Ubiquiti setup may not be sufficient
- Consider Arista 7130 Series or similar FPGA-accelerated switches
- May need dark fiber or microwave links to exchange
- Budget increases significantly ($10k+)

---

## Open Questions

- [ ] **What is the actual HFT latency requirement?** (microseconds vs milliseconds)
- [ ] **Is this for live execution or research/backtesting?**
- [ ] **Where will the MCP server run?** (Same machine as pi, or separate?)
- [ ] **Do we need to create a setup script** for automated installation?
- [ ] **Should we draft custom pi agent prompts** for common network management workflows?
- [ ] **What are the trading day hours** for automated QoS rules? (Assume 9:30-16:00 ET?)
- [ ] **Are there compliance requirements** for network logging/audit trails?

---

## Next Actions

1. [ ] **Confirm HFT latency requirements** with trading team
2. [ ] **Order hardware** (Cloud Gateway Fiber + Switch Pro 24 + U7 Pro)
3. [ ] **Schedule installation** once hardware arrives
4. [ ] **Create installation script** (optional, for repeatability)
5. [ ] **Document network configuration** in wiki after setup
6. [ ] **Set up monitoring alerts** for latency thresholds

---

## References

### MCP Server Options

| Project | Language | Tools | Install | Notes |
|---------|----------|-------|---------|-------|
| `enuno/unifi-mcp-server` | Python | 50+ | `pip install` | ✅ Selected |
| `oliverames/ames-unifi-mcp` | Go | 310 | `go build` | More tools, requires Go |
| `claytono/go-unifi-mcp` | Go | ~100 | `go build` | IPv6 + firewall v1/v2 |
| `h-cli` | Python | Custom | Docker | ❌ Rejected (Docker) |

### Hardware Links

- [Ubiquiti Cloud Gateway Fiber](https://ui.com/unifi/cloud-gateway-fiber)
- [Ubiquiti Switch Pro 24 PoE](https://ui.com/unifi/switch-pro-24-poe)
- [Ubiquiti U7 Pro](https://ui.com/unifi/u7-pro)

### Documentation

- [UniFi MCP Server (enuno)](https://github.com/enuno/unifi-mcp-server)
- [UniFi API Documentation](https://developer.ui.com/)
- [ames-unifi-mcp (alternative)](https://github.com/oliverames/ames-unifi-mcp)

---

## Session Notes

**Session Date:** 2026-04-24  
**Agent:** Pi coding agent with web_search capability  
**Key Decisions:**
- Selected Ubiquiti UniFi ecosystem for AI-friendly management
- Chose `enuno/unifi-mcp-server` (Python) over Go alternatives to avoid compilation
- Rejected h-cli due to Docker requirement
- Budget: $757 for hardware (under $800 target)
- HFT latency requirements still unknown — needs clarification before purchase

**Follow-up Required:**
- Confirm HFT latency specs with trading team
- Order hardware
- Execute installation steps above
