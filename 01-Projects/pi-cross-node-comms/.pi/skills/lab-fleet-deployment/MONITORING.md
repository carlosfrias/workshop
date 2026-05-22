---
section_id: monitoring
size_estimate: ~2.8KB
lod_level: Medium
purpose: Fleet status checks, SSH per-node checks, and key file locations.
---

# Monitoring

[S-TIGHT] Check hub health via curl, agent list via API, node reachability via SSH. Key logs in `/tmp/pi-agent-*.log` and `/tmp/coms-net-hub.log`.

[LOD: Medium] *Load when checking fleet health or debugging connectivity.*

## Fleet Status (one-liner)

```bash
export TOKEN="7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0"

echo "=== HUB ==="
curl -sf http://192.168.0.142:8080/health | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'Server: {d[\"server_id\"][:12]}...  Up since: {d[\"started_at\"][:19]}')"

echo "=== AGENTS ==="
curl -sf -H "Authorization: Bearer $TOKEN" "http://192.168.0.142:8080/v1/agents?project=lab" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for a in d['agents']:
    print(f'  {a[\"name\"]:8} {a[\"status\"]:8} ctx:{a[\"context_used_pct\"]}% queue:{a[\"queue_depth\"]} model:{a[\"model\"]}')
print(f'  Total: {len(d[\"agents\"])} online')
"
```

### What It Shows

- **Hub health:** server ID, uptime
- **Agent list:** name, status, context %, queue depth, model for each agent
- **Count:** total agents online

## Per-Node SSH Check

```bash
for node in fnet1 fnet2 fnet3 fnet4 fnet5 fnet6 fnet7; do
  echo -n "  $node: "
  ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no "$node" "echo OK" 2>/dev/null || echo "DOWN"
done
```

### What It Shows

- `OK` — node reachable, SSH working
- `DOWN` — node unreachable (network / power issue)

## Key Files on Nodes

| File | Path | Purpose |
|------|------|---------|
| Agent log | `/tmp/pi-agent-{hostname}.log` | Agent output and errors |
| Agent PID | `/tmp/pi-agent-{hostname}.pid` | Process ID |
| Hub log | `/tmp/coms-net-hub.log` | Hub server output |
| Hub PID | `/tmp/coms-net-hub.pid` | Hub process ID |
| Extension code | `~/pi-cross-node-comms/` | Extension files |

### Quick Log Commands

```bash
# Agent log on a specific node
ssh fnet3 "tail -50 /tmp/pi-agent-fnet3.log"

# Hub log (always on fnet2)
ssh fnet2 "tail -50 /tmp/coms-net-hub.log"
```

---

*See also: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for symptom-based diagnostics, [INVENTORY.md](INVENTORY.md) for node IPs.*