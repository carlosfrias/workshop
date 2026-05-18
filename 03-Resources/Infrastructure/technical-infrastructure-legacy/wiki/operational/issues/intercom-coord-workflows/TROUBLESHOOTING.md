---
title: "Intercom Coordination Workflows — Troubleshooting Guide"
issue_id: INTERCOM-001
type: troubleshooting
last_updated: 2026-05-14
---

# Intercom Coordination Workflows — Troubleshooting Guide

---

## Quick Reference

| Symptom | Likely Cause | First Action |
|---------|--------------|--------------|
| "Session not found" | Target session not running or not named | Check `intercom.list()` |
| "Already waiting for reply" | Multiple pending asks | Complete current ask first |
| Ask timeout (10 min) | Orchestrator unresponsive | Use `send` for updates |
| Message not delivered | Target session disconnected | Verify with `intercom.list()` |
| Worker silent | Worker stuck or crashed | Send `intercom.ask` to check status |
| Inconsistent results | Worker misconfiguration | Cross-check with direct queries |

---

## Session Issues

### Problem: Session Not Found

**Symptoms:**
```typescript
intercom.send("worker-1", "Task") 
// Returns: { delivered: false, reason: "Session not found" }
```

**Diagnosis:**
```bash
# Check if session exists
intercom({ action: "list" })

# Expected output:
# orchestrator - active
# worker-1 - active
# worker-2 - active

# If worker-1 missing:
# 1. Session not started
# 2. Session didn't run /name command
# 3. Session crashed or exited
```

**Solutions:**

1. **Verify session is running:**
   ```bash
   # Check process list
   ps aux | grep pi
   
   # Or check in terminal where session should be running
   ```

2. **Verify session is named:**
   ```bash
   # In worker session terminal, run:
   /name worker-1
   
   # Then verify from orchestrator:
   intercom({ action: "list" })
   ```

3. **Restart session if needed:**
   ```bash
   # In new terminal
   cd /Users/friasc/Dropbox/workshop
   pi
   /name worker-1
   /model ollama/qwen3.5:4b
   ```

**Prevention:**
- Always run `/name` immediately after starting pi session
- Use tmux or screen to keep sessions running
- Monitor session health periodically

---

### Problem: Already Waiting for Reply

**Symptoms:**
```typescript
intercom.ask("orchestrator", "Question 1")
// ... before receiving reply ...
intercom.ask("orchestrator", "Question 2")
// Returns: { error: "Already waiting for a reply from orchestrator" }
```

**Diagnosis:**
- Worker has pending ask that hasn't been answered
- Can't have multiple pending asks from same session

**Solutions:**

1. **Wait for current ask to be answered:**
   ```typescript
   // Just wait - orchestrator will reply
   const reply = await intercom.ask("orchestrator", "Question 1");
   // Now can ask another question
   ```

2. **Cancel current ask (if needed):**
   ```typescript
   // No direct cancel - must receive reply or timeout
   // Timeout occurs after 10 minutes
   ```

3. **Use send for non-blocking updates:**
   ```typescript
   // Instead of ask, use send for progress updates
   intercom.send("orchestrator", "Progress update: 50% complete");
   ```

**Prevention:**
- Use `ask` only for blocking decisions
- Use `send` for progress updates and notifications
- Track pending asks in worker state

---

### Problem: Ask Timeout

**Symptoms:**
```typescript
const decision = await intercom.ask("orchestrator", "Retry or skip?");
// ... 10 minutes pass with no reply ...
// Throws: { error: "Timeout: No reply received within 10 minutes" }
```

**Diagnosis:**
- Orchestrator didn't reply within 10-minute timeout
- Orchestrator may be:
  - Busy with other tasks
  - Unaware of ask (notification missed)
  - Crashed or exited

**Solutions:**

1. **Retry with send first:**
   ```typescript
   // Before asking, send warning
   intercom.send("orchestrator", 
     "Need decision in 2 minutes: Retry or skip fnet3?");
   
   // Then ask
   const decision = await intercom.ask("orchestrator", 
     "Retry or skip fnet3? Options: (A) Retry, (B) Skip");
   ```

2. **Handle timeout gracefully:**
   ```typescript
   try {
     const decision = await intercom.ask("orchestrator", "Retry or skip?");
     await implementDecision(decision);
   } catch (error) {
     if (error.message.includes("timeout")) {
       // Use default action
       console.log("Timeout - using default: skip");
       await skipNode("fnet3");
     }
   }
   ```

3. **Escalate to human:**
   ```typescript
   if (timeout) {
     await escalateToHuman("orchestrator-unresponsive");
   }
   ```

**Prevention:**
- Set expectations upfront: "Need reply in 5 minutes"
- Send reminder before timeout: "2 minutes until timeout"
- Use `send` for non-critical questions
- Implement default actions for timeouts

---

## Message Delivery Issues

### Problem: Message Not Delivered

**Symptoms:**
```typescript
const result = intercom.send("worker-1", "Task");
// Returns: { delivered: false, reason: "..." }
```

**Diagnosis:**
```bash
# Check target session status
intercom({ action: "list" })

# If worker-1 not listed:
# - Session not running
# - Session not named correctly
# - Intercom not enabled

# If worker-1 listed but still fails:
# - Network issue (unlikely, same machine)
# - Intercom service issue
```

**Solutions:**

1. **Verify target session:**
   ```bash
   intercom({ action: "list" })
   # Should show: worker-1 - active
   ```

2. **Check for self-targeting:**
   ```typescript
   // Can't send to own session
   // If running as worker-1, can't send to worker-1
   
   // Check current session name
   intercom({ action: "status" })
   ```

3. **Restart intercom if needed:**
   ```bash
   # In affected session
   # Exit and restart pi
   exit
   pi
   /name worker-1
   ```

**Prevention:**
- Always verify target exists before sending
- Don't target own session
- Monitor session health

---

### Problem: Message Delivered But No Response

**Symptoms:**
```typescript
intercom.send("worker-1", "Task");
// Returns: { delivered: true }
// ... but worker-1 never responds ...
```

**Diagnosis:**
- Worker received message but:
  - Stuck executing task
  - Crashed during execution
  - Ignored message (bug)
  - Waiting for something

**Solutions:**

1. **Check worker status:**
   ```typescript
   const status = await intercom.ask("worker-1", "Status?");
   ```

2. **Send reminder:**
   ```typescript
   intercom.send("worker-1", 
     "Reminder: Task was assigned 5 minutes ago. Status?");
   ```

3. **Mark worker offline and reassign:**
   ```typescript
   if (noResponseAfter(10 * 60 * 1000)) { // 10 minutes
     console.log("worker-1 unresponsive. Reassigning tasks...");
     await reassignTasks("worker-1", "worker-2");
   }
   ```

**Prevention:**
- Set clear deadlines in task assignments
- Request progress updates every 2 minutes
- Monitor worker responsiveness
- Implement heartbeat mechanism

---

## Worker Issues

### Problem: Worker Silent (No Progress Updates)

**Symptoms:**
- Worker acknowledged task
- No progress updates received
- Deadline approaching or exceeded

**Diagnosis:**
```typescript
// Check if worker is responsive
const status = await intercom.ask("worker-1", "Status?");

// Possible outcomes:
// 1. Worker responds: "Almost done, 1 minute"
// 2. Worker responds: "Stuck on fnet3, retrying"
// 3. No response: Worker may have crashed
```

**Solutions:**

1. **Request status:**
   ```typescript
   const status = await intercom.ask("worker-1", 
     "Task was due 2 minutes ago. Status? ETA?");
   ```

2. **Offer help:**
   ```typescript
   intercom.send("worker-1", 
     "Seeing delay. Any issues I can help with?");
   ```

3. **Request partial results:**
   ```typescript
   intercom.send("worker-1", 
     "Send partial results for completed work. " +
     "Will reassign remaining.");
   ```

**Prevention:**
- Require progress updates every 2 minutes
- Set intermediate checkpoints
- Monitor worker activity
- Alert on silence > 3 minutes

---

### Problem: Worker Keeps Failing Same Task

**Symptoms:**
- Worker assigned task
- Task fails
- Retry fails
- Multiple escalations for same issue

**Diagnosis:**
```typescript
// Check failure pattern
const history = await getWorkerHistory("worker-1");
// Shows: fnet3 mount failed 5 times

// Root cause may be:
// - Environmental issue (SSH key, network, permissions)
// - Worker bug
// - Incorrect task parameters
```

**Solutions:**

1. **Investigate root cause:**
   ```bash
   # SSH to affected node directly
   ssh fnet3 "mount | grep sshfs"
   ssh fnet3 "cat /var/log/syslog | grep sshfs"
   ```

2. **Fix environmental issue:**
   ```bash
   # Add SSH key
   ssh fnet3 "cat ~/.ssh/id_rsa.pub" >> ~/.ssh/authorized_keys
   
   # Create mount point
   ssh fnet3 "sudo mkdir -p /mnt/trading-desk"
   
   # Install missing package
   ssh fnet3 "sudo apt install sshfs"
   ```

3. **Reassign to different worker:**
   ```typescript
   // worker-1 keeps failing, try worker-2
   await reassignTask("worker-1", "worker-2", task);
   ```

**Prevention:**
- Verify prerequisites before task assignment
- Check worker logs for patterns
- Implement circuit breaker (stop after 3 failures)
- Use different workers for retries

---

## Orchestrator Issues

### Problem: Orchestrator Overwhelmed (Multiple Pending Asks)

**Symptoms:**
- Multiple workers sending asks simultaneously
- Orchestrator can't respond to all quickly
- Some asks timing out

**Diagnosis:**
```typescript
// Check pending asks
const pending = await intercom({ action: "pending" });
// Returns: [
//   { from: "worker-1", message: "ESCALATION: fnet3 failed" },
//   { from: "worker-2", message: "ESCALATION: fnet5 failed" },
//   { from: "lab-worker", message: "Clarification needed" }
// ]
```

**Solutions:**

1. **Prioritize critical escalations:**
   ```typescript
   const critical = pending.filter(a => 
     a.message.includes("ESCALATION") || 
     a.message.includes("CRITICAL")
   );
   
   for (const ask of critical) {
     const decision = await makeDecision(ask);
     await intercom.reply(ask.from, decision);
   }
   ```

2. **Acknowledge non-critical asks:**
   ```typescript
   // For non-critical asks, acknowledge and defer
   intercom.reply("worker-2", 
     "Received. Will respond in 2 minutes after handling critical issues.");
   ```

3. **Request batching:**
   ```typescript
   // Instruct workers to batch non-urgent questions
   intercom.send("all-workers", 
     "Batch non-urgent questions. Send every 5 minutes instead of immediately.");
   ```

**Prevention:**
- Stagger task deadlines to avoid simultaneous escalations
- Train workers to distinguish urgent vs. non-urgent
- Implement ask prioritization
- Use send for non-blocking updates

---

### Problem: Orchestrator Making Poor Decisions

**Symptoms:**
- Workers escalating same issue repeatedly
- Decisions leading to more failures
- Pattern of bad outcomes

**Diagnosis:**
```typescript
// Review decision history
const decisions = await getDecisionHistory();
// Shows: "Retry" decided 5 times, all failed

// Root cause may be:
// - Missing context in escalation
// - Orchestrator not consulting logs/history
// - Systemic issue requiring different approach
```

**Solutions:**

1. **Improve escalation format:**
   ```typescript
   // Worker: Include full context
   intercom.ask("orchestrator", `
     ESCALATION: fnet3 mount failed
     Error: ${error.message}
     Attempts: 3
     History: Failed 5 times in past 24h
     Pattern: Always fails at 2pm (network congestion?)
     Options: (A) Retry, (B) Skip, (C) Schedule for off-peak
     Recommendation: Option C - schedule for 3am
   `);
   ```

2. **Consult historical data:**
   ```typescript
   // Orchestrator: Check history before deciding
   const history = await getNodeHistory("fnet3");
   if (history.failures > 3) {
     // Don't retry, try different approach
     return "Skip fnet3. Pattern of failures suggests systemic issue.";
   }
   ```

3. **Escalate to human:**
   ```typescript
   if (patternOfBadDecisions) {
     await escalateToHuman("orchestrator-decision-quality");
   }
   ```

**Prevention:**
- Require full context in escalations
- Implement decision logging
- Review decision quality periodically
- Train orchestrator on common patterns

---

## SSHFS-Specific Issues

### Problem: SSHFS Mount Fails with "Permission Denied"

**Symptoms:**
```bash
# Worker reports:
"ESCALATION: fnet3 mount failed
Error: Permission denied (publickey)"
```

**Diagnosis:**
```bash
# Check SSH key on node
ssh fnet3 "cat ~/.ssh/authorized_keys | grep -c 'ssh-rsa'"
# If 0: Key not present

# Check known_hosts
ssh fnet3 "cat ~/.ssh/known_hosts | grep -c 'mac-orchestrator'"
# If 0: Host key not trusted
```

**Solutions:**

1. **Add worker's public key to orchestrator:**
   ```bash
   # From orchestrator
   ssh fnet3 "cat ~/.ssh/id_rsa.pub" >> ~/.ssh/authorized_keys
   ```

2. **Add orchestrator's host key to worker:**
   ```bash
   # From worker node
   ssh-keyscan -H mac-orchestrator >> ~/.ssh/known_hosts
   ```

3. **Verify SSH connectivity:**
   ```bash
   # Test SSH from worker to orchestrator
   ssh fnet3 "ssh friasc@mac-orchestrator 'hostname'"
   # Should return: mac-orchestrator
   ```

**Prevention:**
- Verify SSH keys during setup
- Include SSH check in Phase 1 of deployments
- Monitor key expiration
- Automate key distribution

---

### Problem: SSHFS Mount Fails with "Bad Mount Point"

**Symptoms:**
```bash
# Worker reports:
"ESCALATION: fnet3 mount failed
Error: bad mount point: /mnt/trading-desk"
```

**Diagnosis:**
```bash
# Check if mount point exists
ssh fnet3 "ls -la /mnt/trading-desk"
# If "No such file or directory": Mount point doesn't exist

# Check permissions
ssh fnet3 "stat /mnt/trading-desk"
# If wrong owner: Permission issue
```

**Solutions:**

1. **Create mount point:**
   ```bash
   ssh fnet3 "sudo mkdir -p /mnt/trading-desk"
   ssh fnet3 "sudo chown friasc:friasc /mnt/trading-desk"
   ```

2. **Verify mount point:**
   ```bash
   ssh fnet3 "ls -la /mnt/ | grep trading-desk"
   # Should show: drwxr-xr-x friasc friasc trading-desk
   ```

**Prevention:**
- Include mount point creation in Phase 3 of deployments
- Verify mount points in pre-flight checks
- Use idempotent scripts (create if not exists)

---

### Problem: SSHFS Mount Fails with "Connection Reset"

**Symptoms:**
```bash
# Worker reports:
"ESCALATION: fnet3 mount failed
Error: Connection reset by peer"
```

**Diagnosis:**
```bash
# Check network connectivity
ssh fnet3 "ping -c 3 mac-orchestrator"
# If fails: Network issue

# Check SSH service on orchestrator
ssh fnet3 "ssh friasc@mac-orchestrator 'systemctl status ssh'"
# If fails: SSH service issue
```

**Solutions:**

1. **Verify network connectivity:**
   ```bash
   ssh fnet3 "ping -c 3 192.168.0.184"
   # Should succeed
   ```

2. **Check SSH service:**
   ```bash
   # On orchestrator (macOS)
   # System Preferences → Sharing → Remote Login (should be checked)
   ```

3. **Retry mount:**
   ```bash
   # Wait for network to stabilize, then retry
   ssh fnet3 "sshfs friasc@mac-orchestrator:/path /mnt/trading-desk"
   ```

**Prevention:**
- Verify network stability before deployments
- Use SSHFS reconnect option: `-o reconnect`
- Monitor network health
- Implement retry logic with backoff

---

## Performance Issues

### Problem: Slow Task Execution

**Symptoms:**
- Tasks taking longer than expected
- Deadlines consistently exceeded
- Workers reporting delays

**Diagnosis:**
```typescript
// Analyze task duration history
const durations = await getTaskDurations();
// Shows: Average 8 minutes, expected 5 minutes

// Check for:
// - Network latency
// - Node overload
// - Inefficient queries
// - Resource contention
```

**Solutions:**

1. **Optimize queries:**
   ```bash
   # Instead of: top -bn1 (slow)
   # Use: cat /proc/stat (fast)
   
   # Instead of: df -h (slow)
   # Use: cat /proc/mounts (fast)
   ```

2. **Reduce workload per worker:**
   ```typescript
   // Before: worker-1 checks 4 nodes
   // After: worker-1 checks 2 nodes
   const assignments = {
     "worker-1": ["fnet1", "fnet2"],  // Was 4 nodes
     "worker-2": ["fnet3", "fnet4"],  // New worker
   };
   ```

3. **Adjust deadlines:**
   ```typescript
   // Set realistic deadlines based on historical data
   const avgDuration = getHistoricalAverage(taskType);
   const deadline = avgDuration * 1.5; // 50% buffer
   ```

**Prevention:**
- Benchmark task durations
- Set realistic deadlines with buffer
- Monitor execution times
- Optimize frequently-run queries

---

### Problem: High Orchestrator Cost

**Symptoms:**
- Cloud model costs higher than expected
- Orchestrator running many turns
- Many escalations to orchestrator

**Diagnosis:**
```typescript
// Analyze cost breakdown
const costs = await getCostBreakdown();
// Shows: Orchestrator: $0.80, Workers: $0.20
// Expected: Orchestrator: $0.10, Workers: $0.04

// Check for:
// - Too many escalations
// - Complex decision-making
// - Orchestrator doing worker tasks
```

**Solutions:**

1. **Reduce escalations:**
   ```typescript
   // Train workers to handle more cases locally
   if (error.recoverable && error.attempts < 3) {
     await retryLocally();  // Don't escalate
   }
   ```

2. **Simplify decisions:**
   ```typescript
   // Provide clear recommendations
   intercom.ask("orchestrator", `
     ESCALATION: Mount failed
     Recommendation: Skip (failed 5 times already)
     Justification: Pattern suggests systemic issue
   `);
   ```

3. **Use lower-tier models for orchestrator:**
   ```bash
   # For simple coordination, use medium cloud
   /model ollama/qwen3.5:4b  # Instead of qwen3.5:397b-cloud
   ```

**Prevention:**
- Empower workers to handle common issues
- Provide clear recommendations in escalations
- Use appropriate model tier for task complexity
- Monitor cost per task type

---

## Debugging Tools

### Command: Check Session Status

```bash
# From any session
intercom({ action: "list" })
intercom({ action: "status" })
intercom({ action: "pending" })
```

### Command: Test Message Delivery

```typescript
// Test send
const result = intercom.send("worker-1", "Test message");
console.log("Send result:", result);

// Test ask
const response = intercom.ask("worker-1", "Test question");
console.log("Ask response:", response);
```

### Command: View Message History

```typescript
// Get recent messages (if logging enabled)
const history = await getMessageHistory("worker-1", { limit: 10 });
console.log("Recent messages:", history);
```

### Command: Analyze Performance

```typescript
// Get task duration metrics
const metrics = await getPerformanceMetrics({
  worker: "worker-1",
  taskType: "health-check",
  period: "24h"
});
console.log("Performance metrics:", metrics);
```

---

## Getting Help

### Internal Resources

- [Architecture Docs](./ARCHITECTURE.md) — System design and patterns
- [Skill Documentation](../../packages/intercom-coord-workflows/skills/intercom-coord-workflows/SKILL.md) — Usage guide
- [Patterns Guide](./PATTERNS.md) — Coordination patterns
- [Issue Home](./0-ISSUE.md) — Full lifecycle documentation

### External Resources

- [pi-intercom Skill](/usr/local/lib/node_modules/pi-intercom/skills/pi-intercom/SKILL.md) — Core intercom API
- [SSHFS Accessible](../../packages/sshfs-accessible/skills/sshfs-accessible/SKILL.md) — SSHFS integration
- [doc-standards](../../packages/doc-standards/skills/doc-standards/SKILL.md) — Documentation standards

### Support Channels

1. **Check documentation** — Most issues documented above
2. **Review logs** — Check message history and decision logs
3. **Escalate to human** — For unresolved issues
4. **Open GitHub issue** — For bugs or feature requests

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-05-14  
**Maintained By:** Trading Desk Team
