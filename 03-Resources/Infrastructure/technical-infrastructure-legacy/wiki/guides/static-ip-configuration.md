# Static IP Configuration

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/static-ip-configuration.md` for Lab Nodes

**Problem:** TP-Link AX6000 router changes IP addresses on DHCP lease renewal, breaking Ansible inventory and SSH configurations.

**Solution:** Configure DHCP reservations (static DHCP leases) on the router.

---

## Why DHCP Reservation (Not Static IP on Nodes)?

| Approach | Pros | Cons |
|----------|------|------|
| **DHCP Reservation** | ✅ Centralized management<br>✅ No node config changes<br>✅ Survives OS reinstall<br>✅ Router manages conflicts | ⚠️ Requires router access |
| **Static IP on Node** | ✅ Works without router access | ❌ Each node needs config<br>❌ Can cause IP conflicts<br>❌ Must update on network changes |

**Recommendation:** Use DHCP reservation on the router.

---

## Step 1: Discover MAC Addresses

Run the discovery script:

```bash
cd /Users/friasc/Cloud/workshop/technical-infrastructure/ansible
./scripts/discover-mac-addresses.sh
```

Or manually:

```bash
ssh friasc@192.168.0.XXX "ip link show | grep ether | awk '{print $2}'"
```

---

## Step 2: Configure TP-Link AX6000 DHCP Reservation

### Access Router Admin Panel

1. Open browser: **http://192.168.0.1** or **http://tplinkwifi.net**
2. Login with admin credentials

### Navigate to Address Reservation

**Path:** `Advanced` → `Network` → `DHCP Server` → `Address Reservation`

(Alternative path on some firmware: `Advanced` → `LAN` → `DHCP Server` → `Reserve`)

### Add Reservations

Click **Add** and enter for each node:

| Hostname | MAC Address | Reserved IP | Status |
|----------|-------------|-------------|--------|
| fnet1 | _(run discovery)_ | 192.168.0.131 | ⚠️ Needs MAC |
| fnet2 | 0c:9d:92:cc:55:4c | 192.168.0.150 | ✅ Ready |
| fnet3 | 1c:69:7a:6c:da:4c | 192.168.0.179 | ✅ Ready |
| fnet4 | 1c:69:7a:6c:dc:fa | 192.168.0.109 | ✅ Ready |
| fnet5 | _(run discovery)_ | 192.168.0.119 | ⚠️ Needs MAC |
| fnet6 | _(run discovery)_ | 192.168.0.103 | ⚠️ Needs MAC |
| fnet7 | _(run discovery)_ | 192.168.0.172 | ⚠️ Needs MAC |

### Save and Apply

1. Click **Save** after each entry
2. Reboot router if prompted
3. Reboot all lab nodes to acquire new reserved IPs

---

## Step 3: Verify Configuration

After router reboot and node reboot:

```bash
# Ping all nodes to verify IPs are stable
for i in 131 150 179 109 119 103 172; do
  ping -c 1 192.168.0.$i && echo "✅ 192.168.0.$i reachable" || echo "❌ 192.168.0.$i unreachable"
done
```

---

## Alternative: Static IP on Each Node (If Router Access Unavailable)

If you cannot access the router admin panel, configure static IPs on each node:

### Ubuntu 20.04+ (Netplan)

```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  eth0:
    dhcp4: no
    addresses: [192.168.0.131/24]
    gateway4: 192.168.0.1
    nameservers:
      addresses: [8.8.8.8, 8.8.4.4]
```

Apply: `sudo netplan apply`

### Ansible Automation

An Ansible playbook can configure this automatically. Request creation if needed.

---

## Update Ansible Inventory

After IPs are stabilized, update the inventory:

```yaml
# technical-infrastructure/ansible/inventory.yml
lab_nodes:
  hosts:
    fnet1:
      ansible_host: 192.168.0.131
    # ... etc
```

---

## Troubleshooting

### Node has wrong IP after reservation
- Reboot the node: `sudo reboot`
- Or renew DHCP: `sudo dhclient -r && sudo dhclient`

### Router admin panel inaccessible
- Try: http://192.168.1.1 (some TP-Link models)
- Check router label for default gateway
- Reset router if credentials unknown

### IP conflicts after reservation
- Clear DHCP leases on router
- Reboot all nodes simultaneously

---

## References

- [TP-Link AX6000 Manual](https://www.tp-link.com/us/support/archer-ax6000/)
- [Ansible Collection](/technical-infrastructure/products/project-blueprint)
- [Multi-Node Setup](multi-node-setup-2026-04-26.md)
