# VPN Ansible Automation

Ansible playbooks and roles for deploying a self-hosted WireGuard VPN gateway with DuckDNS dynamic DNS on the lab infrastructure.

---

## Roles

| Role | Purpose | Target |
|------|---------|--------|
| `wireguard-server` | Installs WireGuard server, generates keys, enables NAT | `vpn_gateway` (fnet1) |
| `wireguard-client` | Configures a node as WireGuard client/peer | `vpn_peers` |
| `duckdns-updater` | Keeps dynamic public IP synced with DuckDNS hostname | `vpn_gateway` |

---

## Playbooks

### `setup-vpn-gateway.yml`

Deploys the complete VPN gateway on fnet1 (WireGuard server + DuckDNS).

**Usage:**

```bash
cd technical-infrastructure/ansible

# First run: generates keys and deploys
ansible-playbook -i inventory.yml playbooks/setup-vpn-gateway.yml \
  --extra-vars "duckdns_token=381f40da-62d2-4e79-98af-07c6288a2984"
```

**What it does:**
1. Generates server keypair (stored in `vpn-keys/`)
2. Generates orchestrator client keypair (stored in `vpn-keys/`)
3. Deploys WireGuard server on fnet1
4. Configures IP forwarding and NAT masquerade
5. Installs DuckDNS updater with 5-minute cron
6. Outputs the orchestrator public key for client config

**Idempotent:**
- Re-running the playbook preserves existing keys (uses `creates:`)
- Only updates `/etc/wireguard/wg0.conf` if template content changes

---

### `add-vpn-peer.yml`

Adds a new device (peer) to an existing gateway.

**Usage:**

```bash
ansible-playbook -i inventory.yml playbooks/add-vpn-peer.yml
```

**Prompts for:**
- Peer name (e.g., `laptop2`, `phone`)
- Peer public key (run `wg genkey | tee priv.key | wg pubkey > pub.key` on the device)
- Peer allowed IPs (default: `10.200.200.3/32`)

**After running:**
- Playbook appends the new `[Peer]` block to server's wg0.conf
- Displays a client config template to copy to the new device
- Restarts `wg-quick@wg0` service

---

## Directory Layout

```
ansible/
├── ansible.cfg              # Roles path, SSH options
├── inventory.yml            # With vpn_gateway and vpn_peers groups
├── vpn-keys/                # Generated keys (do NOT commit)
│   ├── server.private.key
│   ├── server.public.key
│   ├── orchestrator.private.key
│   └── orchestrator.public.key
├── playbooks/
│   ├── setup-vpn-gateway.yml
│   └── add-vpn-peer.yml
└── roles/
    ├── wireguard-server/
    │   ├── defaults/main.yml
│   ├── tasks/main.yml
│   ├── templates/wg0.conf.j2
│   └── handlers/main.yml
    ├── wireguard-client/
│   ├── defaults/main.yml
│   ├── tasks/main.yml
│   ├── templates/client.conf.j2
│   └── handlers/main.yml
    └── duckdns-updater/
       ├── defaults/main.yml
        ├── tasks/main.yml
        └── templates/duckdns-update.sh.j2
```

---

## Key Generation Workflow

### Generate New Peer Keys (on any machine with `wg` installed)

```bash
# 1. Generate keypair
wg genkey | tee peer.private.key | wg pubkey > peer.public.key

# 2. Copy public key for Ansible
 cat peer.public.key
# Output: <64-character base64>

# 3. Run add-vpn-peer playbook, paste the public key when prompted
ansible-playbook -i inventory.yml playbooks/add-vpn-peer.yml
```

### Configure the Peer Device

**macOS:** Use the WireGuard app, import a config file:

```ini
[Interface]
Address = 10.200.200.3/32
PrivateKey = <contents of peer.private.key>
DNS = 192.168.0.1

[Peer]
PublicKey = <server public key from vpn-keys/server.public.key>
Endpoint = carlos-lab.duckdns.org:51820
AllowedIPs = 192.168.0.0/24, 10.200.200.0/24
PersistentKeepalive = 25
```

**Linux:**

```bash
sudo cp peer.conf /etc/wireguard/wg0.conf
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

---

## Security Notes

- **Never commit `vpn-keys/*.key` files to git.** The `.gitignore` excludes `vpn-keys/` but verify with `git status`.
- **Server private key** stays only on the gateway (fnet1) and in the local `vpn-keys/` directory.
- **Client private keys** stay only on their respective devices.
- **Rotate keys** if compromise suspected: delete the `[Peer]` block from server's wg0.conf and re-run key generation.

---

## Verifying the Tunnel

On the orchestrator (after connecting):

```bash
# Ping the VPN gateway
ping 10.200.200.1

# SSH to any lab node through the tunnel
ssh friasc@192.168.0.143

# View active WireGuard interfaces
sudo wg show
```

On the gateway (fnet1):

```bash
# Show active peers and latest handshake
sudo wg show wg0

# Check DuckDNS last update
sudo tail /var/log/duckdns-update.log
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "duckdns_token not provided" | Add `--extra-vars "duckdns_token=xxx"` to playbook |
| "Peer key already exists" | Each peer needs a unique IP in AllowedIPs |
| "wg-quick restart failed" | Check `sudo systemctl status wg-quick@wg0` and `sudo wg show` |
| DuckDNS not updating | Run `/usr/local/bin/duckdns-update.sh` manually on fnet1 for error output |
| Port 51820 not reachable | Verify router port-forward: UDP 51820 → 192.168.0.141 |
