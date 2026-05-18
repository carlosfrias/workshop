---
title: "Intercom Coordination Workflows — Patterns"
issue_id: INTERCOM-001
type: patterns
last_updated: 2026-05-14
---

# Intercom Coordination Workflows — Patterns

---

## Overview

This document details the coordination patterns enabled by intercom-coord-workflows. Each pattern includes:
- **Purpose:** When to use this pattern
- **Flow:** Visual representation of message flow
- **Implementation:** Code examples
- **Best Practices:** Tips for effective use
- **Anti-patterns:** What to avoid

---

## Pattern 1: Orchestrator-Worker Delegation

### Purpose

Standard task delegation from orchestrator to worker with autonomous execution and result reporting.

### When to Use

- ✅ Single worker task assignment
- ✅ Monitoring and reporting
- ✅ Data collection
- ✅ Analysis tasks
- ✅ SSHFS operations

### Flow

```
Orchestrator                    Worker
     │                             │
     │─── intercom.send ──────────►│
     │    "Task: {description}"    │
     │    "Deadline: {time}"       │
     │                             │
     │                             │── Execute task
     │                             │
     │                             │── (Optional: Progress updates)
     │                             │
     │◄── intercom.send ───────────│
     │    "Task complete.          │
     │     Results: {summary}"     │
     │                             │
```

### Implementation

```typescript
// Orchestrator: Assign task
await intercom({
  action: "send",
  to: "worker-1",
  message: `
    Task: Health check fnet1, fnet2
    Checks: CPU, RAM, SSHFS mount status
    Deadline: 5 minutes
    Report: intercom.send when complete
    Escalate: intercom.ask if any check fails
    Progress: Update every 2 minutes if task exceeds 5 minutes
  `
});

// Worker: Acknowledge
await intercom({
  action: "send",
  to: "orchestrator",
  message: "Task received. Starting health check on fnet1, fnet2. ETA: 5 minutes."
});

// Worker: Execute
const results = await executeHealthCheck(["fnet1", "fnet2"]);

// Worker: Report
await intercom({
  action: "send",
  to: "orchestrator",
  message: `
    Task Complete: Health Check
    
    Results:
    - fnet1: CPU 12%, RAM 50%, SSHFS ✅
    - fnet2: CPU 8%, RAM 38%, SSHFS ✅
    
    Status: All nodes healthy
  `
});
```

### Best Practices

1. **Set clear expectations** — Specify deadline, reporting method, escalation path
2. **Acknowledge receipt** — Worker confirms task received immediately
3. **Provide progress updates** — For tasks > 2 minutes, send checkpoints
4. **Report in standard format** — Use consistent structure for easy parsing

### Anti-Patterns

❌ **Vague instructions:**
```typescript
intercom.send("worker", "Check the nodes");
```

✅ **Clear instructions:**
```typescript
intercom.send("worker", `
  Health check: fnet1, fnet2
  Checks: CPU, RAM, SSHFS
  Deadline: 5 minutes
  Report: intercom.send
  Escalate: intercom.ask on failure
`);
```

❌ **Silent execution:**
```typescript
// Worker starts without acknowledgment
```

✅ **Immediate acknowledgment:**
```typescript
intercom.send("orchestrator", "Task received. Starting now. ETA: 5 minutes.");
```

---

## Pattern 2: Blocking Clarification (Ask/Reply)

### Purpose

Worker requests decision from orchestrator when encountering ambiguity or exceptions.

### When to Use

- ✅ Exception handling
- ✅ Ambiguity resolution
- ✅ Strategic decisions
- ✅ Recovery action selection
- ✅ Escalation

### Flow

```
Worker                        Orchestrator
   │                               │
   │─── intercom.ask ─────────────►│
   │    "ESCALATION: {issue}"      │
   │    "Options: A, B, C"         │
   │    "Recommendation: {X}"      │
   │                               │
   │                               │── Evaluate
   │                               │── Decide
   │                               │
   │◄── intercom.reply ────────────│
   │    "Proceed with Option B"    │
   │                               │
   │── Implement decision ─────────│
```

### Implementation

```typescript
// Worker: Detect issue
try {
  await mountNode("fnet3");
} catch (error) {
  // Escalate with options
  const decision = await intercom({
    action: "ask",
    to: "orchestrator",
    message: `
      ESCALATION: fnet3 mount failed
      Error: ${error.message}
      Cause: SSH key not in authorized_keys
      Impact: Blocks fnet3 operations
      Options:
        (A) Skip fnet3, continue with other nodes
        (B) Wait for manual key addition, then retry
        (C) Add key now via SSH command
      Recommendation: Option C — I can add key via SSH
    `
  });
  
  // Implement decision
  await handleDecision(decision);
}

// Orchestrator: Respond
await intercom({
  action: "reply",
  message: "Option C. Add key now. Command: ssh fnet3 'cat ~/.ssh/id_rsa.pub' >> ~/.ssh/authorized_keys"
});
```

### Best Practices

1. **Structure escalations** — Include error, cause, impact, options, recommendation
2. **Provide options** — Give orchestrator clear choices (A, B, C)
3. **Make recommendation** — Suggest best option based on context
4. **Respond promptly** — Orchestrator must reply within 10-minute timeout

### Anti-Patterns

❌ **Vague escalation:**
```typescript
intercom.ask("orchestrator", "fnet3 failed. What do I do?");
```

✅ **Structured escalation:**
```typescript
intercom.ask("orchestrator", `
  ESCALATION: fnet3 mount failed
  Error: Permission denied
  Cause: SSH key missing
  Options: (A) Skip, (B) Wait, (C) Add key
  Recommendation: Option C
`);
```

❌ **Late escalation:**
```typescript
// Worker tries to recover for 8 minutes, then escalates with 2 minutes left
```

✅ **Early escalation:**
```typescript
// Worker escalates immediately on detecting issue
```

---

## Pattern 3: Multi-Worker Broadcast

### Purpose

Parallel task execution across multiple workers with synchronized deadlines and centralized aggregation.

### When to Use

- ✅ Fleet-wide health checks
- ✅ Parallel monitoring
- ✅ Distributed data collection
- ✅ Load-balanced operations
- ✅ Time-sensitive tasks

### Flow

```
                    Orchestrator
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   ┌─────────┐    ┌─────────┐    ┌─────────┐
   │ Worker 1│    │ Worker 2│    │ Worker 3│
   │         │    │         │    │         │
   │ Execute │    │ Execute │    │ Execute │
   │         │    │         │    │         │
   └─────────┘    └─────────┘    └─────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
                        ▼
                  Aggregation
```

### Implementation

```typescript
// Orchestrator: Define assignments
const assignments = {
  "worker-1": ["fnet1", "fnet2"],
  "worker-2": ["fnet3", "fnet4"],
  "lab-worker": ["fnet5", "fnet6", "fnet7"]
};

// Orchestrator: Broadcast tasks
Object.entries(assignments).forEach(([worker, nodes]) => {
  intercom({
    action: "send",
    to: worker,
    message: `
      Health check: ${nodes.join(", ")}
      Checks: CPU, RAM, SSHFS
      Deadline: 5 minutes
      Report: intercom.send when complete
    `
  });
});

// Workers: Execute in parallel (each worker runs independently)
// Worker 1
const results1 = await executeHealthCheck(["fnet1", "fnet2"]);
intercom.send("orchestrator", `fnet1-2: ${summarize(results1)}`);

// Worker 2
const results2 = await executeHealthCheck(["fnet3", "fnet4"]);
intercom.send("orchestrator", `fnet3-4: ${summarize(results2)}`);

// Worker 3
const results3 = await executeHealthCheck(["fnet5", "fnet6", "fnet7"]);
intercom.send("orchestrator", `fnet5-7: ${summarize(results3)}`);

// Orchestrator: Aggregate
const allResults = await collectResults(["worker-1", "worker-2", "lab-worker"]);
const summary = aggregateResults(allResults);
console.log("Fleet Summary:", summary);
```

### Best Practices

1. **Balance workload** — Assign nodes based on worker capacity
2. **Synchronize deadlines** — All workers report around same time
3. **Track progress centrally** — Monitor all workers simultaneously
4. **Handle stragglers** — Send reminders if workers exceed deadline

### Anti-Patterns

❌ **Unbalanced assignments:**
```typescript
// worker-1: 1 node, worker-2: 6 nodes
```

✅ **Balanced assignments:**
```typescript
// worker-1: 2 nodes, worker-2: 2 nodes, worker-3: 3 nodes
```

❌ **No deadline:**
```typescript
intercom.send("worker", "Check nodes");
```

✅ **Clear deadline:**
```typescript
intercom.send("worker", "Check nodes. Deadline: 5 minutes.");
```

---

## Pattern 4: Planner-Executor Pipeline

### Purpose

Multi-phase operations with sequential dependencies, phase-by-phase reporting, and escalation support.

### When to Use

- ✅ SSHFS deployments
- ✅ Multi-step installations
- ✅ Coordinated rollouts
- ✅ Complex operations with dependencies
- ✅ Audit-required operations

### Flow

```
Planner                       Executor
   │                              │
   │── Plan (attachment) ────────►│
   │   Phases: 1,2,3,4,5          │
   │                              │
   │                              │── Phase 1
   │◄── Phase 1 complete ─────────│
   │                              │
   │                              │── Phase 2
   │◄── Phase 2 complete ─────────│
   │                              │
   │                              │── Phase 3 (ESCALATION)
   │◄── intercom.ask ─────────────│
   │   "Phase 3 failed. Retry?"   │
   │                              │
   │── Reply: "Retry once" ──────►│
   │                              │
   │                              │── Phase 3 retry
   │◄── Phase 3 complete ─────────│
   │                              │
   │                              │── Phases 4, 5
   │◄── Final report ─────────────│
```

### Implementation

```typescript
// Planner: Create detailed plan
const plan = {
  operation: "sshfs-mount-all",
  phases: [
    { id: 1, name: "verify-ssh", duration: "2 min" },
    { id: 2, name: "verify-prereqs", duration: "2 min" },
    { id: 3, name: "create-mount-points", duration: "3 min" },
    { id: 4, name: "mount-all", duration: "5 min" },
    { id: 5, name: "verify-mounts", duration: "3 min" }
  ],
  totalDuration: "15 min",
  riskLevel: "Medium"
};

// Planner: Send plan
await intercom({
  action: "send",
  to: "executor",
  message: "Execute SSHFS mount operation",
  attachments: [{
    type: "snippet",
    name: "mount-plan.json",
    content: JSON.stringify(plan, null, 2)
  }]
});

// Executor: Execute phases sequentially
for (const phase of plan.phases) {
  console.log(`Starting Phase ${phase.id}: ${phase.name}`);
  
  try {
    await executePhase(phase);
    
    // Report phase completion
    await intercom.send("planner", `
      Phase ${phase.id} complete: ${phase.name}
      Duration: ${actualDuration}
      Status: Success
    `);
    
  } catch (error) {
    // Escalate phase failure
    const decision = await intercom.ask("planner", `
      ESCALATION: Phase ${phase.id} failed
      Phase: ${phase.name}
      Error: ${error.message}
      Options: (A) Retry, (B) Skip, (C) Debug
      Recommendation: Option A
    `);
    
    await handlePhaseFailure(phase, decision);
  }
}

// Executor: Final report
await intercom.send("planner", `
  Operation Complete: ${plan.operation}
  Status: Success
  Duration: ${totalDuration}
  Phases: ${plan.phases.length}/${plan.phases.length}
  Issues: ${issues.length}
`);
```

### Best Practices

1. **Detailed phases** — Break into small, verifiable steps
2. **Clear success criteria** — Define what "done" looks like per phase
3. **Anticipate failures** — Document recovery actions
4. **Report after each phase** — Don't batch multiple phases

### Anti-Patterns

❌ **Large phases:**
```typescript
phases: ["Setup everything", "Run everything", "Verify everything"]
```

✅ **Small phases:**
```typescript
phases: [
  "verify-ssh",
  "verify-prereqs",
  "create-mount-points",
  "mount-all",
  "verify-mounts"
]
```

❌ **No escalation path:**
```typescript
// Executor tries to recover complex failures alone
```

✅ **Clear escalation:**
```typescript
// Executor escalates phase failures immediately
```

---

## Pattern 5: Exception Escalation

### Purpose

Structured exception handling with clear escalation paths, decision tracking, and recovery implementation.

### When to Use

- ✅ SSHFS mount failures
- ✅ SSH authentication errors
- ✅ Resource exhaustion
- ✅ Network timeouts
- ✅ Permission issues

### Flow

```
Worker                        Orchestrator
   │                               │
   │─── Detect Issue ──────────────│
   │                               │
   │─── Attempt Local Recovery ────│
   │         (if simple)           │
   │                               │
   │   Still failing?              │
   │       │                       │
   │       ├─ No ── Continue       │
   │       │                       │
   │       ▼ Yes                   │
   │─── intercom.ask ─────────────►│
   │    "ESCALATION: {details}"    │
   │                               │
   │                               │── Evaluate
   │                               │── Consult logs
   │                               │── Make decision
   │                               │
   │◄── intercom.reply ────────────│
   │    "Decision: {action}"       │
   │                               │
   │─── Implement Decision ────────│
   │                               │
   │─── Report Outcome ────────────│
```

### Implementation

```typescript
// Worker: Detect and attempt recovery
async function executeWithEscalation(operation, context) {
  try {
    return await operation();
  } catch (error) {
    // Attempt simple recovery
    if (error.recoverable) {
      try {
        console.log("Attempting local recovery...");
        return await recoverAndRetry(error, operation);
      } catch (recoveryError) {
        // Recovery failed, escalate
        return await escalateAndHandle(error, context);
      }
    } else {
      // Not recoverable locally, escalate immediately
      return await escalateAndHandle(error, context);
    }
  }
}

async function escalateAndHandle(error, context) {
  // Escalate with full context
  const decision = await intercom({
    action: "ask",
    to: "orchestrator",
    message: `
      ESCALATION: ${context.operation} failed
      Node: ${context.node}
      Error: ${error.message}
      Stage: ${error.stage}
      Attempts: ${error.attempts}
      Impact: ${error.impact}
      Options:
        (A) ${error.options.retry}
        (B) ${error.options.skip}
        (C) ${error.options.debug}
      Recommendation: ${error.recommendation}
    `
  });
  
  // Implement decision
  return await implementDecision(decision, error, context);
}

// Orchestrator: Handle escalation
async function handleEscalation(ask) {
  const { message, from } = ask;
  
  // Parse escalation
  const escalation = parseEscalation(message);
  
  // Consult historical data
  const history = await getNodeHistory(escalation.node);
  
  // Make decision
  const decision = makeDecision(escalation, history);
  
  // Respond
  await intercom({
    action: "reply",
    to: from,
    message: formatDecision(decision)
  });
  
  // Log decision
  await logDecision(escalation, decision);
}
```

### Best Practices

1. **Attempt simple recovery first** — Don't escalate recoverable issues
2. **Provide full context** — Include node, stage, attempts, impact
3. **Offer clear options** — Give orchestrator actionable choices
4. **Make recommendation** — Suggest best option based on context
5. **Log decisions** — Track escalation history for future reference

### Anti-Patterns

❌ **Immediate escalation:**
```typescript
// Escalate without attempting recovery
```

✅ **Recovery first:**
```typescript
// Try simple recovery, escalate only if it fails
```

❌ **Incomplete context:**
```typescript
intercom.ask("orchestrator", "Mount failed");
```

✅ **Full context:**
```typescript
intercom.ask("orchestrator", `
  ESCALATION: Mount failed
  Node: fnet3
  Error: Permission denied
  Stage: SSH authentication
  Attempts: 1
  Impact: Blocks fnet3 operations
  Options: (A) Retry, (B) Skip, (C) Add key
  Recommendation: Option C
`);
```

---

## Pattern 6: Progress Checkpoints

### Purpose

Regular progress reporting for long-running tasks to maintain visibility and enable early intervention.

### When to Use

- ✅ Tasks > 5 minutes
- ✅ Multi-phase operations
- ✅ Fleet-wide operations
- ✅ High-risk operations
- ✅ Time-sensitive tasks

### Flow

```
Worker                        Orchestrator
   │                               │
   │─── Start Task ───────────────►│
   │    "ETA: 10 minutes"          │
   │                               │
   │── Execute Phase 1 ────────────│
   │                               │
   │─── Checkpoint 1 ─────────────►│
   │    "2 min: 20% complete"      │
   │                               │
   │── Execute Phase 2 ────────────│
   │                               │
   │─── Checkpoint 2 ─────────────►│
   │    "4 min: 40% complete"      │
   │                               │
   │── Execute Phase 3 ────────────│
   │                               │
   │─── Checkpoint 3 ─────────────►│
   │    "6 min: 60% complete"      │
   │                               │
   │── Execute Remaining ──────────│
   │                               │
   │─── Final Report ─────────────►│
   │    "Complete: 100%"           │
```

### Implementation

```typescript
// Worker: Execute with checkpoints
async function executeWithCheckpoints(task, totalWork) {
  const startTime = Date.now();
  const expectedDuration = 10 * 60 * 1000; // 10 minutes
  const checkpointInterval = 2 * 60 * 1000; // 2 minutes
  
  let completed = 0;
  let lastCheckpoint = startTime;
  
  while (completed < totalWork) {
    // Do work
    await completeOneUnit();
    completed++;
    
    const now = Date.now();
    const elapsed = now - lastCheckpoint;
    
    // Send checkpoint every 2 minutes
    if (elapsed >= checkpointInterval) {
      const percent = Math.round((completed / totalWork) * 100);
      const eta = Math.round((expectedDuration - (now - startTime)) / 60000);
      
      await intercom.send("orchestrator", `
        Checkpoint:
        - Progress: ${completed}/${totalWork} (${percent}%)
        - Elapsed: ${Math.round((now - startTime) / 60000)} minutes
        - ETA: ${eta} minutes
        - Status: ${getStatus()}
      `);
      
      lastCheckpoint = now;
    }
    
    // Warn if approaching deadline
    if (now - startTime > expectedDuration - 60000) {
      await intercom.send("orchestrator", `
        ⚠️ WARNING: Approaching deadline
        - Progress: ${completed}/${totalWork}
        - Time Remaining: 1 minute
        - Action: Will request extension or deliver partial
      `);
    }
  }
  
  // Final report
  const duration = Math.round((Date.now() - startTime) / 60000);
  await intercom.send("orchestrator", `
    Task Complete:
    - Total Work: ${totalWork}
    - Completed: ${completed}
    - Duration: ${duration} minutes
    - Checkpoints Sent: ${Math.floor(duration / 2)}
  `);
}
```

### Best Practices

1. **Set interval appropriately** — Every 2 minutes for long tasks
2. **Include key metrics** — Progress, elapsed time, ETA, status
3. **Warn before deadline** — Alert orchestrator 1 minute before timeout
4. **Be consistent** — Use same format for all checkpoints

### Anti-Patterns

❌ **No checkpoints:**
```typescript
// Silent execution for 10 minutes
```

✅ **Regular checkpoints:**
```typescript
// Report every 2 minutes
```

❌ **Inconsistent format:**
```typescript
"20% done"
"Progress: 2/10"
"Still working..."
```

✅ **Consistent format:**
```typescript
`Checkpoint:
- Progress: 2/10 (20%)
- Elapsed: 2 minutes
- ETA: 8 minutes
- Status: On track`
```

---

## Pattern Selection Guide

| Pattern | Use When | Complexity | Cost Impact |
|---------|----------|------------|-------------|
| Orchestrator-Worker | Simple delegation | Low | Minimal |
| Blocking Clarification | Decisions needed | Medium | Low (orchestrator time) |
| Multi-Worker Broadcast | Parallel execution | Medium | Medium (multiple workers) |
| Planner-Executor | Multi-phase ops | High | Medium-High |
| Exception Escalation | Error handling | Medium | Low (prevents waste) |
| Progress Checkpoints | Long tasks | Low | Low (extra messages) |

---

## Combining Patterns

### Example: SSHFS Deployment (Multiple Patterns)

```typescript
// Pattern 4: Planner-Executor (overall structure)
const plan = createMountPlan();
await sendPlanToExecutor(plan);

// Pattern 6: Progress Checkpoints (within each phase)
for (const phase of plan.phases) {
  await executePhaseWithCheckpoints(phase);
}

// Pattern 5: Exception Escalation (on failures)
try {
  await mountNode("fnet3");
} catch (error) {
  await escalateAndHandle(error); // Pattern 5
}

// Pattern 3: Multi-Worker Broadcast (parallel node mounting)
await broadcastToWorkers({
  "worker-1": ["fnet1", "fnet2"],
  "worker-2": ["fnet3", "fnet4"],
  "lab-worker": ["fnet5", "fnet6", "fnet7"]
});
```

---

## References

- [Architecture Docs](./ARCHITECTURE.md)
- [Skill Documentation](../../packages/intercom-coord-workflows/skills/intercom-coord-workflows/SKILL.md)
- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [Issue Home](./0-ISSUE.md)

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-05-14  
**Maintained By:** Trading Desk Team
