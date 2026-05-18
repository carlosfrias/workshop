# Trading Desk Workspace Setup

**Purpose:** Clean, reusable workspace demonstrating predictable tool integration  
**Version:** 1.0.0  
**Created:** 2026-05-06

---

## Overview

This workspace integrates all built tools into a cohesive, production-ready environment for AI-orchestrated trading operations.

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Gist Message Queue** | `packages/gist-message-queue/` | Async agent communication |
| **Master Prompt System** | `packages/master-prompt-system/` | Health-aware orchestration |
| **PI Keyword Router** | `packages/pi-keyword-router/` | Model routing |
| **Local Model Pilot** | `packages/local-model-pilot/` | Local node management |
| **Decomposition Skill** | `packages/decomposition-skill/` | Task decomposition |
| **Trading Agents** | `packages/trading-agents/` | Domain-specific agents |

---

## Quick Start

### 1. Install Packages

```bash
cd technical-infrastructure/packages

# Install all packages
for pkg in */; do
    echo "Installing $pkg..."
    cd "$pkg" && pip install -e . --break-system-packages && cd ..
done
```

### 2. Verify Installation

```bash
# Check all CLI tools
gist-mq --version
# Output: gist-mq 1.0.0

# Check imports
python3 -c "from gistmq import GistMessageQueue; print('OK')"
# Output: OK

# Run tests
cd packages/gist-message-queue && python3 -m pytest tests/ -v
```

### 3. Initialize Workspace

```bash
# Create workspace config
mkdir -p ~/.trading-desk
cat > ~/.trading-desk/config.json << 'EOF'
{
  "workspace": "workshop",
  "gist_id": "YOUR_GIST_ID",
  "agent_name": "orchestrator",
  "nodes": ["fnet1", "fnet2", "fnet3", "fnet4", "fnet5", "fnet6", "fnet7"]
}
EOF
```

---

## Workspace Structure

```
workshop/
├── technical-infrastructure/
│   ├── packages/              # Reusable packages
│   │   ├── gist-message-queue/
│   │   ├── master-prompt-system/
│   │   ├── pi-keyword-router/
│   │   └── ...
│   ├── scripts/               # Operational scripts
│   ├── playbooks/             # Ansible playbooks
│   └── wiki/                  # Documentation
├── wiki/                      # Knowledge base
│   ├── operational/           # Operating procedures
│   ├── trading-desk/          # Trading domain
│   └── index.md               # Master index
├── bookkeeping/               # Trade logging
├── market-research/           # Analysis & signals
├── position-management/       # Position tracking
└── AGENTS.md                  # Root router
```

---

## Standard Operating Procedures

### SOP-001: Start New Session

```bash
# 1. Check system health
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# 2. Review backlog
cat technical-infrastructure/wiki/operational/BACKLOG.md | head -50

# 3. Load phase files (automatic via AGENTS.md)
# Phase 1: Domain activation
# Phase 2: Planning
# Phase 3: Execution
# Phase 4: Quality check
# Phase 5: Documentation
```

### SOP-002: Deploy Task to Nodes

```bash
# Using Gist Message Queue
gist-mq init $GIST_ID --agent-name orchestrator

# Send task
cat > /tmp/task.json << 'EOF'
{"task": "benchmark", "model": "qwen3.5:4b"}
EOF
gist-mq send task.created /tmp/task.json --target fnet3

# Monitor
gist-mq status --verbose
```

### SOP-003: Run Acceptance Tests

```bash
# Test Gist MQ
cd packages/gist-message-queue
python3 -m pytest tests/ -v

# Test orchestration
cd ../../scripts
python3 acceptance-test-suite.py

# Test wiki links
python3 test-wiki-links.py
```

### SOP-004: Document Work

```bash
# Create session notes
mkdir -p technical-infrastructure/operational/sessions
cat > technical-infrastructure/operational/sessions/SESSION-$(date +%Y-%m-%d).md << 'EOF'
# Session Notes - DATE

## Objectives
- [ ] 

## Work Completed
- [ ] 

## Issues/Blockers
- [ ] 

## Next Steps
- [ ] 
EOF
```

---

## Tool Integration Patterns

### Pattern 1: Health-Aware Decomposition

```python
from gistmq import MessageProducer
from technical-infrastructure.scripts import orchestrator_health

# Check health first
health = orchestrator_health.check()
if health['status'] == 'stressed':
    # Route to cloud
    producer.send('task.escalated', health, target='cloud')
else:
    # Decompose locally
    producer.send('task.decompose', health, target='fnet3')
```

### Pattern 2: Multi-Node Coordination

```bash
# Coordinator sends to all nodes
for node in fnet{1..7}; do
    gist-mq send task.created /tmp/task.json --target $node
done

# Each node processes independently
# Results collected via Gist
```

### Pattern 3: Wiki Documentation Flow

```bash
# 1. Create document
vim wiki/trading-desk/my-strategy.md

# 2. Add to index
python3 scripts/generate-wiki-index.py

# 3. Verify links
python3 scripts/test-wiki-links.py

# 4. Commit
git add . && git commit -m "docs: Add trading strategy"
```

---

## Demonstration Workflows

### Demo 1: End-to-End Task Distribution

```bash
#!/bin/bash
# demo-001-task-distribution.sh

set -e
echo "=== Demo 1: Task Distribution ==="

# 1. Initialize
gist-mq init ABC123 --agent-name demo-orchestrator

# 2. Create task
cat > /tmp/demo-task.json << 'EOF'
{
  "task_id": "demo-001",
  "description": "Benchmark qwen3.5:4b",
  "priority": "high"
}
EOF

# 3. Send to node
gist-mq send task.created /tmp/demo-task.json --target fnet3

# 4. Monitor status
gist-mq status --verbose

# 5. Collect result
gist-mq recv task.completed --timeout 300

echo "✅ Demo complete"
```

### Demo 2: Health-Aware Routing

```bash
#!/bin/bash
# demo-002-health-routing.sh

set -e
echo "=== Demo 2: Health-Aware Routing ==="

# 1. Check health
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# 2. Route based on health
# (See health_aware_executor.py for logic)

# 3. Execute
python3 technical-infrastructure/scripts/health_aware_executor.py \
  --prompt "Analyze market data" \
  --test

echo "✅ Demo complete"
```

### Demo 3: Wiki Link Integrity

```bash
#!/bin/bash
# demo-003-wiki-integrity.sh

set -e
echo "=== Demo 3: Wiki Link Integrity ==="

# 1. Build wiki
npm run build

# 2. Test links
python3 scripts/test-wiki-links.py

# 3. Report
cat technical-infrastructure/operational/testing/link-test-report.json

echo "✅ Demo complete"
```

---

## Configuration Reference

### Environment Variables

```bash
# Gist MQ
export GIST_MQ_GIST_ID="ABC123"
export GIST_MQ_AGENT_NAME="orchestrator"
export GITHUB_TOKEN="ghp_..."

# Orchestration
export ORCHESTRATOR_HEALTH_CHECK="true"
export DECOMPOSITION_ENABLED="true"
export CLOUD_ESCALATION_TIERS="3"
```

### Config Files

| File | Purpose | Location |
|------|---------|----------|
| `config.json` | Workspace config | `~/.trading-desk/` |
| `config.json` | Gist MQ config | `~/.gist-mq/` |
| `model-router.json` | Model routing | `technical-infrastructure/` |
| `phase-index.json` | Phase loading | `.pi/agents/phases/` |

---

## Quality Assurance

### Pre-Commit Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Links valid (`test-wiki-links.py`)
- [ ] Health check passes (`orchestrator_health.py`)
- [ ] Documentation updated
- [ ] Backlog updated

### Post-Session Checklist

- [ ] Session notes created
- [ ] Completed items archived
- [ ] Backlog sorted by priority
- [ ] Master index updated
- [ ] Git committed

---

## Troubleshooting

### Common Issues

**Issue:** `gist-mq` command not found  
**Solution:** `pip install -e packages/gist-message-queue`

**Issue:** Tests fail with import errors  
**Solution:** `pip install -e . --break-system-packages`

**Issue:** Wiki links broken  
**Solution:** `python3 scripts/test-wiki-links.py --fix`

**Issue:** Health check fails  
**Solution:** Check RAM/CPU usage, close unnecessary processes

---

## Support

- **Documentation:** `wiki/` directory
- **Examples:** `packages/*/examples/`
- **Tests:** `packages/*/tests/`
- **Issues:** Backlog in `technical-infrastructure/wiki/operational/BACKLOG.md`

---

**Version:** 1.0.0  
**Created:** 2026-05-06  
**Maintained By:** Trading Desk Agents
