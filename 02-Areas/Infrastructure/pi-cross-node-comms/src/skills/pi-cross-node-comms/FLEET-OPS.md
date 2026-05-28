# FLEET-OPS — Fleet Deployment & Management

**Section ID:** FLEET-OPS
**Size:** ~1KB
**LOD Level:** Low (load when standing up or shutting down fleet)
**Purpose:** Dispatch table for fleet operations — which script, which host, which order.

---

## Fleet Architecture

The coms-net hub production deployment runs on **fnet2** (192.168.0.142), a dedicated Linux lab node. The local Mac orchestrator sessions connect TO fnet2.

```
┌──────────────┐         ┌──────────────┐
│  Mac (this)   │ ──SSE── │  fnet2        │
│  pi sessions  │ ◄──────► │  coms-net hub │
│  192.168.0.148│         │  192.168.0.142│
└──────────────┘         │  port 8080    │
                         └──────────────┘
```

## Dispatch Table

| Intent | Action | Where |
|--------|--------|-------|
| "Stand up the fleet" / "stand up fleet" / "start hub" | `ssh fnet2 "bash /tmp/setup-hub-on-fnet2.sh start"` | **fnet2** |
| "Shut down the fleet" / "shutdown hub" | `ssh fnet2 "bash /tmp/setup-hub-on-fnet2.sh stop"` | **fnet2** |
| "Restart the fleet" | `ssh fnet2 "bash /tmp/setup-hub-on-fnet2.sh restart"` | **fnet2** |
| "Fleet status" / "hub status" | `ssh fnet2 "bash /tmp/setup-hub-on-fnet2.sh status"` | **fnet2** |
| Local dev hub (testing only) | `scripts/standup-hub.sh` | local Mac |

## Stand Up Fleet — Full Steps

```bash
# 1. Copy setup script to fnet2 (first time or after changes)
scp scripts/setup-hub-on-fnet2.sh fnet2:/tmp/setup-hub-on-fnet2.sh

# 2. Run it on fnet2
ssh fnet2 "bash /tmp/setup-hub-on-fnet2.sh start"

# 3. Verify from Mac
curl -s http://192.168.0.142:8080/health
```

## Connect Mac pi Sessions

After the hub is up on fnet2, local pi sessions need these env vars:

```bash
export PI_COMS_NET_SERVER_URL="http://192.168.0.142:8080"
export PI_COMS_NET_AUTH_TOKEN="7e095b8e0b5d8bc44feea4da24e989fcf92b9341b5db8ed9604f05c412f386a0"
export PI_COMS_NET_PROJECT="lab"
```

Or restart pi — it auto-discovers from `server.json` on the hub host.

## ⚠️ Common Mistake

**Do NOT run `standup-hub.sh` locally when the user says "stand up the fleet".** That script starts a local dev hub on the Mac. The fleet hub belongs on fnet2.

---

*Back to [SKILL.md](SKILL.md)*