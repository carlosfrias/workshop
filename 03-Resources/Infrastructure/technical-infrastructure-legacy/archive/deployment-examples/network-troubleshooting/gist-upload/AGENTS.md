# Node 2 Agent - Autonomous Network Troubleshooting

**Role:** Local execution agent for network diagnostics and fix application  
**Orchestrator:** Cloud agent (Mac session)  
**Communication:** GitHub Gist (async, persistent)  
**Gist:** https://gist.github.com/carlosfrias/0c517214489cb78c0484ca661f3d8463

---

## Capabilities

### What Node 2 Agent Does Autonomously

| Task | Autonomous? | Notes |
|------|-------------|-------|
| Hardware detection | ✅ Yes | Run locally, post to Gist |
| Network diagnostics | ✅ Yes | Run locally, post to Gist |
| Apply fix commands | ✅ Yes | Execute from cloud agent |
| Verification tests | ✅ Yes | Run locally, post results |
| Tether management | ✅ Yes | Disconnect/reconnect as needed |
| Status updates | ✅ Yes | Update `node2-STATUS.md` |

### What Requires Cloud Agent

| Task | Cloud Agent Role |
|------|------------------|
| Root cause analysis | Analyze diagnostics, identify issue |
| Fix command generation | Create targeted fix commands |
| Complex decision making | Choose between alternative fixes |
| Final verification | Confirm node is ready |
| Escalation | Prompt human if automated fix fails |

### What Requires Human User

| Task | When to Prompt |
|------|----------------|
| Router configuration | If router-side blocking detected |
| Hardware replacement | If NIC failure detected |
| Authorization | If sudo password required (rare) |
| Confirmation | Before destructive operations |

---

## Communication Protocol

### Gist File Conventions

| File Pattern | Direction | Purpose |
|--------------|-----------|---------|
| `node2-diagnostic.txt` | Node 2 → Cloud | Diagnostic output |
| `node2-fix-commands.sh` | Cloud → Node 2 | Fix commands to execute |
| `node2-results.txt` | Node 2 → Cloud | Fix execution results |
| `node2-verification.txt` | Node 2 → Cloud | Verification output |
| `node2-STATUS.md` | Both | Current workflow state |
| `node2-COMPLETE.md` | Cloud → Node 2 | Final confirmation |

### Status States

| State | File Content | Who Sets | Next Action |
|-------|--------------|----------|-------------|
| `INITIALIZING` | Node 2 starting up | Node 2 | Begin diagnostics |
| `DIAGNOSTIC_READY` | Diagnostics posted | Node 2 | Cloud agent analyzes |
| `FIXES_PENDING` | Waiting for fixes | Node 2 | Poll for commands |
| `FIXES_READY` | Fix commands posted | Cloud | Node 2 executes |
| `RESULTS_READY` | Results posted | Node 2 | Cloud agent verifies |
| `VERIFICATION_PENDING` | Waiting for verification | Node 2 | Cloud agent reviews |
| `COMPLETE` | All done | Cloud | Workflow ends |
| `ESCALATED` | Human intervention needed | Either | User prompted |

---

## Workflow (Autonomous)

### Phase 1: Initialization
```bash
# Node 2 Agent runs:
~/node2-step1-auth.sh      # Authenticate GitHub CLI
~/node2-step2-download.sh   # Download scripts
```

**Status:** `INITIALIZING` → `READY`

---

### Phase 2: Diagnostics
```bash
# Node 2 Agent runs:
~/node2-step3-diagnose.sh   # Disconnect tether, test network

# Then posts to Gist:
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-diagnostic.txt
echo "DIAGNOSTIC_READY" > node2-STATUS.md
```

**Status:** `DIAGNOSTIC_READY`  
**Cloud Agent:** Analyzes diagnostics, creates fix commands

---

### Phase 3: Fix Execution
```bash
# Node 2 Agent polls for fix commands:
while ! curl -sL "$GIST_URL/node2-fix-commands.sh" | grep -q "^#"; do
    sleep 10
done

# Downloads and executes:
curl -sL "$GIST_URL/node2-fix-commands.sh" -o /tmp/fixes.sh
bash /tmp/fixes.sh

# Posts results:
echo "Fix executed at $(date)" > node2-results.txt
echo "Exit code: $?" >> node2-results.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-results.txt
echo "RESULTS_READY" > node2-STATUS.md
```

**Status:** `RESULTS_READY`  
**Cloud Agent:** Reviews results, posts verification request or COMPLETE

---

### Phase 4: Verification
```bash
# Node 2 Agent runs:
~/network-troubleshooting-bundle/verify.sh

# Posts verification:
cat /tmp/node-ready.txt > node2-verification.txt
gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-verification.txt
echo "VERIFICATION_PENDING" > node2-STATUS.md
```

**Status:** `VERIFICATION_PENDING`  
**Cloud Agent:** Confirms COMPLETE or requests additional fixes

---

## Decision Matrix

### Network Issue Classification

| Symptom | Node 2 Action | Cloud Agent Action |
|---------|---------------|-------------------|
| No IP assigned | Assign static IP | Confirm configuration |
| Gateway unreachable | Check ARP, cable | Analyze router config |
| Internet blocked | Check IP conflict | Create router fix commands |
| DNS fails | Set explicit DNS | Verify resolution |
| Driver issue | Reinstall driver | Confirm driver version |
| Hardware failure | Report error | Escalate to human |

### When to Escalate to Human

```bash
# Node 2 Agent checks:
if [ "$INTERNET_OK" = false ] && [ "$GATEWAY_OK" = true ]; then
    # Router is blocking - may need human intervention
    echo "ESCALATED: Router configuration required" > node2-STATUS.md
    echo "" >> node2-escalation.txt
    echo "Issue: Router blocking this node" >> node2-escalation.txt
    echo "MAC: $(cat /sys/class/net/enp7s0/address)" >> node2-escalation.txt
    echo "Required: Router admin access" >> node2-escalation.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-escalation.txt
fi
```

---

## Agent-to-Agent Communication

### Node 2 → Cloud Agent

```bash
# Function to send message
send_to_cloud() {
    local type="$1"
    local file="$2"
    
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add "$file"
    echo "$type:$(date -Iseconds)" >> node2-message-log.txt
    gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-message-log.txt
}

# Usage:
send_to_cloud "diagnostic" "node2-diagnostic.txt"
send_to_cloud "results" "node2-results.txt"
send_to_cloud "escalation" "node2-escalation.txt"
```

### Cloud Agent → Node 2

```bash
# Function to check for messages
check_from_cloud() {
    local type="$1"
    local url="https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw"
    
    case "$type" in
        fix-commands)
            curl -sL "$url/node2-fix-commands.sh" | grep -q "^#"
            return $?
            ;;
        complete)
            curl -sL "$url/node2-COMPLETE.md" | grep -q "COMPLETE"
            return $?
            ;;
        status)
            curl -sL "$url/node2-STATUS.md"
            return $?
            ;;
    esac
}

# Usage:
if check_from_cloud "fix-commands"; then
    echo "Fix commands received from cloud agent"
fi
```

---

## Autonomous Operation Rules

### Rule 1: Always Update Status
After every major action, update `node2-STATUS.md`

### Rule 2: Log Everything
All actions logged to `node2-message-log.txt`

### Rule 3: Poll Respectfully
Poll Gist every 10 seconds (not faster) for fix commands

### Rule 4: Fail Gracefully
If fix fails, report results and wait for new commands

### Rule 5: Escalate Early
If stuck for >5 minutes, escalate to cloud agent

---

## Quick Reference

### Start Autonomous Workflow
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step1-auth.sh | bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step2-download.sh | bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-step3-diagnose.sh | bash
# Then autonomous until COMPLETE
```

### Check Status
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-STATUS.md
```

### View Message Log
```bash
curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-message-log.txt
```

---

## Cloud Agent Instructions

When Node 2 posts `DIAGNOSTIC_READY`:

1. Fetch diagnostics: `curl -L https://gist.githubusercontent.com/carlosfrias/0c517214489cb78c0484ca661f3d8463/raw/node2-diagnostic.txt`
2. Analyze root cause
3. Create fix commands in `node2-fix-commands.sh`
4. Post to Gist: `gh gist edit 0c517214489cb78c0484ca661f3d8463 --add node2-fix-commands.sh`
5. Node 2 will auto-execute within 10 seconds

When Node 2 posts `RESULTS_READY`:

1. Fetch results: `curl -L .../node2-results.txt`
2. Verify fix worked
3. If success: Post `node2-COMPLETE.md`
4. If failed: Post new `node2-fix-commands.sh` with alternative fix

---

**Node 2 Agent operates autonomously. Human user only prompted for router config or hardware issues.**
