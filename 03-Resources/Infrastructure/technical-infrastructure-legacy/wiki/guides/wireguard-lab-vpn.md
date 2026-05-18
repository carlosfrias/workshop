# WireGuard VPN Lab Setup

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/wireguard-lab-vpn.md`

**Date**: 2026-04-29
**Server**: fnet1 (192.168.0.141)
**Server Interface**: enp8s0
**VPN Subnet**: 10.200.200.0/24
**Port**: 51820 UDP (server listens) / 51822 UDP (router external, if configured)
**DuckDNS**: carlos-lab.duckdns.org <-> 104.3.179.84
**Status**: ✅ Server operational | ⚠️ Off-premises access DEFERRED (see below)

---

## ⚠️  Off-Premises VPN Status: DEFERRED

**Decision**: Off-premises access is deferred until a dedicated gateway (Protectli Vault / OPNsense) replaces the TP-Link + AT&T consumer stack.

### Why Deferred

| Problem | Root Cause | Resolution Path |
|---------|-----------|-----------------|
| AT&T gateway + TP-Link double NAT creates port-forward failure | Consumer router firmware SPI firewall / UDP passthrough unreliable | Replace with Protectli Vault running OPNsense — single device, no double NAT, built-in WireGuard |
| 3+ hours of router debugging with zero external packets reaching server | AT&T gateway DMZ may not bypass all firewall layers | Hardware upgrade |

**Local LAN VPN is fully functional.** All lab nodes can reach fnet1 via the VPN subnet when on the same network.

### What Works Right Now (Local LAN)

| Capability | Status | Access |
|-----------|--------|--------|
| fnet1 WireGuard server | ✅ Active | LAN nodes can connect to 10.200.200.1 |
| DuckDNS updater | ✅ Active | Updates every 5 min to 104.3.179.84 |
| Depot sync between lab nodes | ✅ Working | `rsync` over 192.168.0.x LAN |
| SSH to any node | ✅ Working | 192.168.0.141-147 |
| Ollama API on any node | ✅ Working | localhost:11434 on each node |

### What Is Deferred (Off-Premises)

| Capability | Deferred Until | Reason |
|-----------|----------------|--------|
| MacBook → Lab via internet | Protectli gateway installation | Double NAT impossible to debug on consumer routers |
| Phone → Lab via internet | Same | Carrier DNS + double NAT + SPI firewall |
| General remote access | Same | Single-device VPN gateway required |

### Interim Workaround (If Needed Before Gateway)

If you must access the lab from outside before the Protectli arrives, use a **cloud relay** (temporary):
1. Spin up a $5/month DigitalOcean droplet or AWS Lightsail instance
2. Install WireGuard on the cloud VM (single public IP, no NAT)
3. Configure fnet1 as a WireGuard **client** of the cloud VM, with a persistent keepalive
4. Connect your MacBook to the same cloud VM
5. Both devices are on the same WireGuard subnet through the cloud relay

This costs ~$5/month and takes 15 minutes to set up. It bypasses your router entirely.

**Recommended**: Wait for the Protectli. The lab local infrastructure is fully operational.

---

## Original Deployment Docs (Preserved Below)

*The following sections document what was deployed. They remain valid for local LAN use and will be re-activated when the hardware gateway is installed.*

**When migrating to Protectli / OPNsense:**
1. Copy `/etc/wireguard/wg0.conf` from fnet1 to the new gateway
2. Update `Endpoint` in MacBook client config to new gateway's public IP or DuckDNS
3. Remove manual port-forward rules on TP-Link and AT&T gateway
4. Disable `wg-quick@wg0` on fnet1: `ssh friasc@fnet1 "sudo systemctl disable wg-quick@wg0"`
5. The client private key (`client-orchestrator.conf`) remains the same

---

## Server Configuration (Current)

| Component | Value |
|-----------|-------|
| Interface | wg0 |
| Server VPN IP | 10.200.200.1/24 |
| LAN IP | 192.168.0.141 |
| Listen Port | 51820 UDP |
| Server Public Key | `BSvCX5R6MBaOqgVBadSD+qkKkxflEktZt1CYaESihlg=` |
| **Rotated Client Public Key** | `08b9BCFTmP5nyrhflxA5t8qpsOaQrYMTDe87qu/t4jE=` |
| IP Forwarding | Enabled |
| NAT/Masquerade | Enabled on enp8s0 |
| Auto-start | `systemctl enable wg-quick@wg0` |
| Status | Active (UDP 51820 listening) |

### DuckDNS Dynamic DNS

| Component | Value |
|-----------|-------|
| Domain | carlos-lab.duckdns.org |
| Public IP | 104.3.179.84 |
| Update Frequency | Every 5 minutes (cron) |
| Script | `/usr/local/bin/duckdns-update.sh` |

### Orchestrator (MacBook) — Installed

| Component | Location |
|-----------|----------|
| WireGuard CLI | `/usr/local/bin/wg`, `/usr/local/bin/wireguard-go` |
| Config | `/usr/local/etc/wireguard/wg0.conf` |
| Up script | `/usr/local/bin/wg-up.sh` |
| Down script | `/usr/local/bin/wg-down.sh` |
| Split tunnel | `AllowedIPs = 192.168.0.0/24, 10.200.200.0/24` |

---

## Local LAN Client Config

For connecting from a lab node or MacBook **while on the same WiFi**:

```ini
[Interface]
Address = 10.200.200.2/32
PrivateKey = QDRp58BLRTKDyT/6ZSG2jRFEZhCgv1FxzrvZiw3tqlk=
DNS = 192.168.0.1
MTU = 1420

[Peer]
PublicKey = BSvCX5R6MBaOqgVBadSD+qkKkxflEktZt1CYaESihlg=
# For local LAN only, use the internal IP directly (no router needed):
# Endpoint = 192.168.0.141:51820
# For off-premises (deferred), use:
Endpoint = carlos-lab.duckdns.org:51820
AllowedIPs = 192.168.0.0/24, 10.200.200.0/24
PersistentKeepalive = 25
```

---

## Security Notes

- Client private key is `.gitignored` in `operational/operational/vpn/client-orchestrator.conf`
- Template `operational/operational/vpn/client-orchestrator.conf.template` is safe to commit
- Keys were rotated on 2026-04-29 after accidental exposure
- DuckDNS token is in the Ansible role, not in committed files

---

## Ansible Automation

For re-deploying the VPN after OS reimage or gateway migration:

```bash
cd technical-infrastructure/ansible
ansible-playbook -i inventory.yml playbooks/setup-vpn-gateway.yml \
  --extra-vars "duckdns_token=YOUR_TOKEN"
```

See `README-vpn.md` for full Ansible role documentation.
