# TI-031/TI-032 Master Prompt System — Quick Start Guide

**Version:** 1.0  
**Last Updated:** 2026-05-05  
**Time to Complete:** 5 minutes  
**Prerequisites:** Ansible 2.15+, Python 3.10+, Ollama installed

---

## Table of Contents

1. [5-Minute Setup](#5-minute-setup)
2. [First Playbook Execution](#first-playbook-execution)
3. [Common Commands](#common-commands)
4. [Troubleshooting Quick Reference](#troubleshooting-quick-reference)
5. [Next Steps](#next-steps)

---

## 5-Minute Setup

### Step 1: Verify Prerequisites (1 minute)

```bash
# Check Ansible version (required: 2.15+)
ansible --version

# Check Python version (required: 3.10+)
python3 --version

# Check Ollama is running
ollama list
```

**Expected Output:**
```
ansible [core 2.15.0 or newer]
Python 3.10.0 or newer
NAME              ID              SIZE      MODIFIED
gemma4:e4b        xxxxxxx         4.2 GB    2 days ago
qwen3.5:4b        xxxxxxx         4.1 GB    2 days ago
```

**If missing:**
```bash
# Install Ansible
pip install ansible

# Install/upgrade Ollama
brew install ollama  # macOS
# or
curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull required models
ollama pull gemma4:e4b
ollama pull qwen3.5:4b
```

---

### Step 2: Verify File Structure (1 minute)

```bash
# Navigate to workspace
cd /Users/friasc/Dropbox/workshop

# Check prompt files exist
ls -la technical-infrastructure/prompts/

# Check health script exists and is executable
ls -la technical-infrastructure/scripts/orchestrator_health.py
```

**Expected Output:**
```
core-prompt.md
module-1-purpose.md
module-2-dependencies.md
module-3-data-sources.md
module-4-conditions.md
module-5-performance.md
module-6-hardware.md

-rwxr-xr-x  1 user  staff  2048 May  5 10:00 orchestrator_health.py
```

**If files missing:**
```bash
# Restore from git
git checkout technical-infrastructure/prompts/
git checkout technical-infrastructure/scripts/
```

---

### Step 3: Test Health Check (1 minute)

```bash
# Run health check
python3 technical-infrastructure/scripts/orchestrator_health.py --json
```

**Expected Output:**
```json
{
  "status": "HEALTHY",
  "ram_percent": 65.2,
  "cpu_load": 1.8,
  "swap_used": 0,
  "timestamp": "2026-05-05T14:30:00Z"
}
```

**Status Interpretation:**
| Status | Action |
|--------|--------|
| `HEALTHY` | ✅ Ready for local execution |
| `STRESSED` | ⚠️ Will decompose to cloud low |
| `CRITICAL` | ❌ Will decompose to cloud high |

**If health check fails:**
```bash
# Run with verbose output
python3 technical-infrastructure/scripts/orchestrator_health.py --verbose

# Check script permissions
chmod +x technical-infrastructure/scripts/orchestrator_health.py
```

---

### Step 4: Verify Playbook Index (1 minute)

```bash
# Check playbook index exists
cat playbooks/playbook-index.json | python3 -m json.tool

# Verify JSON is valid
python3 -m json.tool playbooks/playbook-index.json > /dev/null && echo "Valid JSON"
```

**Expected Output:**
```json
{
  "playbooks": [
    {
      "name": "deploy_app_v1.0.yml",
      "triggers": ["deploy", "deploy_app"],
      "purpose": "Deploy application containers"
    }
  ]
}
Valid JSON
```

**If index missing:**
```bash
# Create minimal index
cat > playbooks/playbook-index.json << 'EOF'
{
  "playbooks": [
    {
      "name": "check_health_v1.0.yml",
      "triggers": ["health", "check_health"],
      "purpose": "System health check"
    }
  ]
}
EOF
```

---

### Step 5: Test Model Response (1 minute)

```bash
# Test with simple query
ollama run gemma4:e4b "What is 2+2?"
```

**Expected Output:**
```
4
```

**If model fails:**
```bash
# Pull model again
ollama pull gemma4:e4b

# Check Ollama service
ollama serve &
```

---

## First Playbook Execution

### Scenario: Health Check Execution

**Command:**
```bash
# Using the orchestrator (recommended)
python3 technical-infrastructure/scripts/run-playbook.py --trigger health

# Or direct Ansible execution
ansible-playbook playbooks/check_health_v1.0.yml
```

**Expected Output:**
```markdown
**Health Status:** healthy (RAM: 65%, CPU: 1.8, Swap: 0)

**Matched Playbook:** check_health_v1.0.yml

**Execution:**
$ ansible-playbook playbooks/check_health_v1.0.yml
PLAY [Health Check] *******************
TASK [Check system status] ************
ok: [localhost]
PLAY RECAP ****************************
localhost: ok=3 changed=0 unreachable=0 failed=0

**Result:** ✅ SUCCESS (3 seconds)
```

### Scenario: Information Query

**User Query:** "What does deploy_app do?"

**Expected Response:**
```markdown
**Module Loaded:** Purpose & Scope

**Playbook:** deploy_app_v1.0.yml

**Purpose:**
Deploys application containers to specified environments with automated health checks and rollback capability on failure.

**Scope:**
- ✅ Container deployment to target nodes
- ✅ Health check verification
- ✅ Automatic rollback on failure

**Expected Outcome:**
- ✅ Application running on target nodes
- ✅ Health checks passing
- ✅ Previous version archived
```

### Scenario: Execution with Health Check

**User Query:** "Deploy the app"

**System Flow:**
```
1. Match keyword "deploy" → deploy_app_v1.0.yml
2. Run TI-031 health check
3. Status: HEALTHY → Execute locally
4. Run playbook
5. Return result
```

**Expected Output:**
```markdown
**Health Status:** healthy (RAM: 68%, CPU: 2.1, Swap: 0)

**Matched Playbook:** deploy_app_v1.0.yml

**Execution:**
$ ansible-playbook playbooks/deploy_app_v1.0.yml
PLAY [Deploy Application] *************
TASK [Deploy containers] **************
changed: [localhost]
PLAY RECAP ****************************
localhost: ok=5 changed=3 unreachable=0 failed=0

**Result:** ✅ SUCCESS (12 seconds)
```

---

## Common Commands

### Health & Status

```bash
# Check system health
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# Check health with verbose output
python3 technical-infrastructure/scripts/orchestrator_health.py --verbose

# Continuous health monitoring
watch -n 5 python3 technical-infrastructure/scripts/orchestrator_health.py --json
```

### Playbook Execution

```bash
# Execute by trigger keyword
python3 technical-infrastructure/scripts/run-playbook.py --trigger deploy

# Execute specific playbook
ansible-playbook playbooks/deploy_app_v1.0.yml

# Execute with extra variables
ansible-playbook playbooks/deploy_app_v1.0.yml \
  --extra-vars "target_environment=production"

# Dry run (no changes)
ansible-playbook playbooks/deploy_app_v1.0.yml --check

# Verbose execution
ansible-playbook playbooks/deploy_app_v1.0.yml -vvv
```

### Module Queries

```bash
# Query purpose module
python3 technical-infrastructure/scripts/query-module.py \
  --playbook deploy_app \
  --module purpose

# Query dependencies
python3 technical-infrastructure/scripts/query-module.py \
  --playbook deploy_app \
  --module dependencies

# Query hardware specs
python3 technical-infrastructure/scripts/query-module.py \
  --playbook deploy_app \
  --module hardware
```

### Model Testing

```bash
# Test with gemma4:e4b
ollama run gemma4:e4b "What is the purpose of deploy_app?"

# Test with qwen3.5:4b
ollama run qwen3.5:4b "What does deploy_app depend on?"

# Test with context
ollama run gemma4:e4b \
  --system "You are a playbook trigger system" \
  "Deploy the app"
```

### Log Inspection

```bash
# View recent executions
tail -50 wiki/operational/sessions/playbook-executions.jsonl | jq .

# View errors only
grep '"status":"error"' wiki/operational/sessions/playbook-executions.jsonl | jq .

# View by playbook
grep 'deploy_app' wiki/operational/sessions/playbook-executions.jsonl | jq .

# Count executions
wc -l wiki/operational/sessions/playbook-executions.jsonl
```

### Maintenance

```bash
# Clear playbook cache
rm -rf /tmp/playbook-cache/*

# Reset orchestrator state
python3 technical-infrastructure/scripts/reset-orchestrator.py

# Validate all prompt files
python3 technical-infrastructure/scripts/validate-prompts.py

# Check model availability
ollama list | grep -E "gemma4|qwen3"
```

---

## Troubleshooting Quick Reference

### Quick Diagnostic Commands

```bash
# Full system diagnostic
python3 technical-infrastructure/scripts/diagnose.py

# Check only health
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# Check only playbooks
python3 technical-infrastructure/scripts/validate-playbooks.py

# Check only models
ollama list
```

### Common Issues & Fixes

| Issue | Symptom | Quick Fix |
|-------|---------|-----------|
| **Health check fails** | All executions go to cloud | `chmod +x technical-infrastructure/scripts/orchestrator_health.py` |
| **Module not loading** | Generic responses | `ls technical-infrastructure/prompts/module-*.md` |
| **Playbook not found** | "No match" error | `cat playbooks/playbook-index.json \| jq .` |
| **Model unavailable** | Ollama connection error | `ollama pull gemma4:e4b` |
| **Execution timeout** | Playbook hangs | `ping <target-node>` |
| **Memory exhausted** | Truncated responses | Clear cache: `rm -rf /tmp/playbook-cache/*` |

### Error Code Quick Reference

| Code | Meaning | One-Line Fix |
|------|---------|--------------|
| E001 | Health check failed | Run health script manually |
| E002 | No playbook matched | Check trigger keywords |
| E003 | Module load failed | Verify file exists |
| E004 | Execution timeout | Check node connectivity |
| E005 | Memory exceeded | Clear cache, restart |
| E006 | Dependency missing | Install required service |
| E007 | Invalid YAML | Validate playbook syntax |

### Emergency Recovery

```bash
# 1. Stop all running playbooks
pkill -f "ansible-playbook"

# 2. Clear all caches
rm -rf /tmp/playbook-cache/*
rm -rf /tmp/ollama-cache/*

# 3. Reset orchestrator
python3 technical-infrastructure/scripts/reset-orchestrator.py

# 4. Verify health
python3 technical-infrastructure/scripts/orchestrator_health.py --json

# 5. Test basic execution
ansible-playbook playbooks/check_health_v1.0.yml
```

### Getting Help

```bash
# View full documentation
cat technical-infrastructure/wiki/technical-infrastructure/master-prompt-guide.md

# View architecture docs
cat technical-infrastructure/wiki/technical-infrastructure/master-prompt-architecture.md

# View research validation
cat technical-infrastructure/wiki/technical-infrastructure/master-prompt-research.md

# Check backlog for known issues
cat technical-infrastructure/wiki/operational/BACKLOG.md
```

---

## Next Steps

### After Quick Start

1. **Read Full Guide** → `master-prompt-guide.md` (comprehensive user documentation)
2. **Review Architecture** → `master-prompt-architecture.md` (technical deep-dive)
3. **Explore Research** → `master-prompt-research.md` (validation summary)
4. **Create First Playbook** → Use `ansible-playbook-template.yml`
5. **Register Triggers** → Add to `playbooks/playbook-index.json`
6. **Test End-to-End** → Execute with health check validation

### Learning Path

| Day | Topic | Resource |
|-----|-------|----------|
| 1 | Quick start | This document |
| 2 | Core concepts | `master-prompt-guide.md` |
| 3 | Architecture | `master-prompt-architecture.md` |
| 4 | Module creation | Module templates in `prompts/` |
| 5 | Playbook development | `ansible-playbook-template.yml` |
| 6 | Health monitoring | `unified-health-monitoring.md` |
| 7 | Production deployment | `operational/production-checklist.md` |

### Recommended Practice Exercises

1. **Exercise 1:** Execute health check 5 times, observe consistency
2. **Exercise 2:** Query all 6 modules for same playbook
3. **Exercise 3:** Create simple playbook with 2 tasks
4. **Exercise 4:** Register new trigger keyword
5. **Exercise 5:** Simulate stressed system (manually set threshold)
6. **Exercise 6:** Review execution logs for patterns
7. **Exercise 7:** Implement custom module for new playbook

---

## Quick Reference Card

### Core Commands

```
Health Check    : python3 scripts/orchestrator_health.py --json
Run Playbook    : python3 scripts/run-playbook.py --trigger <keyword>
Query Module    : python3 scripts/query-module.py --module <name>
Clear Cache     : rm -rf /tmp/playbook-cache/*
View Logs       : tail -50 wiki/operational/sessions/*.jsonl | jq .
```

### Status Codes

```
✅ HEALTHY   : RAM <80%, CPU <4.0, Swap = 0
⚠️ STRESSED  : RAM 80-92%, CPU 4.0-6.0, Swap = 0
❌ CRITICAL  : RAM >92%, CPU >6.0, Swap >0
```

### Module Triggers

```
Purpose      : "what", "why", "purpose", "does"
Dependencies : "depend", "require", "prerequisite"
Data Sources : "data", "input", "source", "file"
Conditions   : "when", "condition", "trigger"
Performance  : "how long", "performance", "time"
Hardware     : "hardware", "specs", "requirements"
```

### File Locations

```
Core Prompt       : prompts/core-prompt.md
Modules           : prompts/module-*.md
Playbook Index    : playbooks/playbook-index.json
Health Script     : scripts/orchestrator_health.py
Execution Logs    : wiki/operational/sessions/playbook-executions.jsonl
Documentation     : wiki/technical-infrastructure/master-prompt-*.md
```

---

**Document Owner:** Technical Infrastructure Team  
**Support:** Check backlog or run diagnostic script  
**Last Updated:** 2026-05-05
