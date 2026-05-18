# PROMPT: Event-Driven TI-010 Protocol

**Prompt ID:** PROMPT-TI010-EVENT-DRIVEN  
**Created:** 2026-05-04  
**Domain:** technical-infrastructure (Off-Premises Orchestration)  
**Purpose:** Implement and operate the event-driven Gist Message Protocol (TI-010)  

---

## Context

You are implementing or operating the **event-driven Gist Message Protocol** (TI-010), which provides an async message bus over GitHub Gist for off-premises communication with lab nodes.

**Why Event-Driven?**
- Old polling: Workers waste CPU/API calls every 30s scanning all comments
- New event-driven: Workers pull only when events exist, subscribe to specific types
- Impact: 90% reduction in API usage, near-instant delivery, ordered delivery

---

## Event Types

| Event Type | Description | Producer | Consumer |
|------------|-------------|----------|----------|
| `task.created` | New task available | Orchestrator | Any node |
| `task.assigned` | Task claimed by node | Orchestrator | Specific node |
| `task.completed` | Task finished | Node | Orchestrator |
| `task.failed` | Task errored | Node | Orchestrator |
| `node.online` | Node connected | Node | Orchestrator |
| `node.offline` | Node disconnected | Node | Orchestrator |
| `node.health` | Health check request | Orchestrator | Specific node |
| `model.request` | Model inference request | Orchestrator | Any node |
| `model.response` | Inference result | Node | Orchestrator |
| `agent.heartbeat` | Agent alive signal | Agent | Orchestrator |

---

## Event Schema

```json
{
  "id": "evt_YYYY-MM-DD-HH-MM-SS-abcdef",
  "type": "task.created",
  "source": "orchestrator",
  "target": "fnet3",
  "timestamp": "2026-05-04T14:30:00Z",
  "correlation_id": "corr_YYY-MM-DD-HH-MM-SS",
  "payload": {
    // Event-specific data
  },
  "metadata": {
    "version": "1.0",
    "ttl_seconds": 86400,
    "delivery_attempt": 1,
    "max_attempts": 3
  }
}
```

---

## Publishing Events (Orchestrator)

### Basic Publish
```python
from gist_event_bus import EventBus

bus = EventBus(gist_id="0c517214489cb78c0484ca661f3d8463")

bus.publish(
    type="task.created",
    target="fnet3",  # Optional: if omitted, broadcast to all
    payload={
        "task_id": "task_001",
        "command": "ollama run qwen3.5:4b 'hello'",
        "timeout_seconds": 60
    },
    priority="normal"  # normal, high, critical
)
```

### Priority Events
```python
# High-priority event (skip queue, immediate delivery)
bus.publish(
    type="node.health",
    target="fnet3",
    payload={"urgent": True},
    priority="high"
)
```

### Broadcast Events
```python
# No target = broadcast to all subscribed consumers
bus.publish(
    type="agent.heartbeat",
    payload={"timestamp": "2026-05-04T14:30:00Z"}
)
```

---

## Subscribing to Events (Node)

### Basic Consumer
```python
from gist_event_bus import EventConsumer

consumer = EventConsumer(
    node_id="fnet3",
    gist_id="0c517214489cb78c0484ca661f3d8463",
    subscriptions=["task.*"]  # Wildcard: all task events
)

@consumer.on("task.created")
def handle_new_task(event):
    task = event.payload
    print(f"Received task {task['task_id']}")
    # Execute task...
    
    # ACK on success (removes from queue)
    consumer.ack(event.id)
    
    # Or NACK on failure (triggers retry)
    # consumer.nack(event.id, requeue=True)
```

### Multiple Subscriptions
```python
consumer = EventConsumer(
    node_id="fnet3",
    gist_id="...",
    subscriptions=[
        "task.created",     # New tasks
        "task.cancelled",   # Cancelled tasks
        "node.health",      # Health checks
    ]
)
```

### Polling Interval
```python
# Default: 5s for event-driven (faster response)
consumer.run(poll_interval=5)

# For low-priority consumers: 30s (saves API calls)
consumer.run(poll_interval=30)
```

---

## Error Recovery

### Retry Behavior
| Attempt | Delay | Action |
|---------|-------|--------|
| 1 | 0s | Immediate |
| 2 | 30s | First retry |
| 3 | 60s | Second retry |
| 3+ | Dead Letter Queue | Manual review |

### Dead Letter Queue (DLQ)
```python
# Failed events land in DLQ after 3 retries
# Review with:
python3 gist_event_bus.py --dlq

# Reprocess manually:
python3 gist_event_bus.py --requeue dlq_event_id

# Or delete:
python3 gist_event_bus.py --delete-dlq dlq_event_id
```

---

## Observability

### Consumer Lag
```bash
# Check how far behind consumers are
python3 gist_event_bus.py --lag

# Output:
# Node    Lag (events)  Last Seen    Status
# fnet3   2             10s ago      OK
# fnet4   0             5s ago       OK
# fnet5   15            3min ago     WARNING
```

### Metrics
```bash
# Show event bus metrics
python3 gist_event_bus.py --metrics

# Output:
# Messages published: 152
# Messages consumed: 147
# Messages lost: 2
# Messages in DLQ: 3
# Avg delivery latency: 4.2s
# Max delivery latency: 12.1s
```

### Event Tracing
```bash
# Trace a specific event through the system
python3 gist_event_bus.py --trace evt_2026-05-04-14-30-00-abc123

# Output:
# 14:30:00 — Published by orchestrator
# 14:30:02 — Claimed by fnet3
# 14:30:15 — Completed (ACK received)
```

---

## Rules

### Must Always
- **ACK on success** — Always acknowledge events after successful processing
- **NACK on failure** — Always nack on failure (not same as error) to trigger retry
- **Log all events** — Every publish/consume logged to `model-dispatch-events.jsonl`
- **Handle duplicates** — Consumers must be idempotent (at-least-once delivery)
- **Respect priority** — Process critical events before normal events

### Must Never
- **Never silently drop events** — Always ACK or NACK
- **Never modify events** — Event history is immutable (append-only)
- **Never exceed rate limits** — Max 100 requests/min to GitHub API
- **Never expose Gist ID** — Gist ID is not a secret but don't publicize it

---

## Common Patterns

### Pattern 1: Task Fan-Out
```python
# Orchestrator publishes task
for node in ["fnet3", "fnet4", "fnet5"]:
    bus.publish("task.created", target=node, payload={...})

# All nodes pick up tasks in parallel
```

### Pattern 2: Result Collection
```python
# Nodes publish results
consumer.on("task.completed", handle_result)

# Orchestrator collects results
results = bus.collect(timeout=300)
```

### Pattern 3: Health Check Ping
```python
# Orchestrator sends health check
bus.publish("node.health", target="fnet3")

# Node responds
consumer.on("node.health", lambda e: {"status": "ok"})
```

### Pattern 4: Broadcast Shutdown
```python
# Emergency shutdown
bus.publish("node.offline", broadcast=True, priority="critical")
```

---

## Debugging

### Check Event Bus Status
```bash
python3 gist_event_bus.py --status
```

### List Pending Events
```bash
python3 gist_event_bus.py --pending
```

### View Event Details
```bash
python3 gist_event_bus.py --show evt_YYY-MM-DD-HH-MM-SS-abcdef
```

### Simulate Consumer
```bash
# Dry-run: show what a consumer would receive
python3 gist_event_bus.py --consume --dry-run --subscriptions "task.*"
```

---

## Integration Points

| System | Integration | Event Type |
|--------|-------------|------------|
| **TI-009** (Task Distribution) | Event-driven task queue | `task.created`, `task.completed` |
| **TI-011** (Meta-Orchestration) | Trigger decomposition on events | `decomposition.trigger` |
| **TI-019** (LLM Decomposition) | Publish decomposed sub-tasks | `task.created` |
| **TI-023** (Health Monitoring) | Health checks via events | `node.health` |
| **TDOF-001** (Vector Memory) | Query results as events | `model.request`, `model.response` |
| **TDOF-003** (Agent Loop) | Agent heartbeat + task events | `agent.heartbeat`, `task.*` |

---

## Migration from Old TI-010

```bash
# 1. Stop old polling workers
ansible -i ansible/inventory.yml lab_nodes -a "systemctl stop gist-worker@*.timer"

# 2. Start new event-driven workers
ansible -i ansible/inventory.yml lab_nodes -a "systemctl start gist-event-consumer@*.timer"

# 3. Verify health
python3 gist_event_bus.py --status
python3 gist_event_bus.py --lag

# 4. Rollback if needed
ansible -i ansible/inventory.yml lab_nodes -a "systemctl stop gist-event-consumer@*.timer systemctl start gist-worker@*.timer"
```

---

## Files

| File | Purpose |
|------|---------|
| `scripts/gist_event_bus.py` | Core event bus library |
| `scripts/gist_consumer.py` | Consumer base class |
| `scripts/gist_producer.py` | Producer API |
| `scripts/gist_lag_monitor.py` | Observability CLI |
| `prompts/PROMPT-TI010-EVENT-DRIVEN.md` | This file |
| `wiki/operational/planning/PLAN-TI010-EVENT-DRIVEN.md` | Architecture plan |

---

**Version:** 1.0  
**Last Updated:** 2026-05-04  
**Prompt Owner:** technical-infrastructure agent
