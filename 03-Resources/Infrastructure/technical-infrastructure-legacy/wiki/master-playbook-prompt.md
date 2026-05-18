# Master Playbook Management Prompt

> **📍 Navigation**  
> **Parent:** [Technical Infrastructure Wiki](../../WIKI.md) | [Technical Infrastructure Docs](./)  
> **Related:** [Unified Health Monitoring](./unified-health-monitoring.md) | [Plan Location Guide](./PLAN-LOCATION-GUIDE.md) | [Low-Capacity Validation](./low-capacity-model-validation.md)  
> **Quick Links:** [Core Prompt](../../../prompts/core-prompt.md) | [Module Files](../../../prompts/) | [Playbook Index](../../../playbooks/playbook-index.json)  
> **Backlog:** [TI-032](/operational/BACKLOG.md#ti-032)

---

**Purpose:** Comprehensive prompt system for creating, updating, and managing Ansible playbooks with keyword-based triggers, optimized for low-capacity models (<2B parameters).

**Version:** 1.0  
**Created:** 2026-05-05  
**Model Target:** 2B+ parameters (qwen3.5:4b, gemma4:e4b, phi3:mini)

---

## Architecture Overview

This master prompt uses **modular architecture** with dynamic loading to minimize context usage:

```
┌─────────────────────────────────────────────────────┐
│              CORE PROMPT (Always Loaded)            │
│  - Trigger keyword recognition                      │
│  - Playbook selection logic                         │
│  - Execution state management                       │
│  - Error handling framework                         │
└─────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Module 1 │    │ Module 2 │    │ Module 3 │
  │ Purpose  │    │ Dependen │    │ Data     │
  │ \& Scope │    │ cies     │    │ Sources  │
  └──────────┘    └──────────┘    └──────────┘
        ↓                 ↓                 ↓
  ┌──────────┐    ┌──────────┐    ┌──────────┐
  │ Module 4 │    │ Module 5 │    │ Module 6 │
  │ Condit-  │    │ Perform- │    │ Hardware │
  │ ions     │    │ ance     │    │ Specs    │
  └──────────┘    └──────────┘    └──────────┘
```

**Context Management:**
- Core prompt: ~150 tokens (always in memory)
- Each module: ~100-150 tokens (loaded on demand)
- Maximum context: 500-650 tokens (fits gemma4:e4b 8K limit)

---

## Module 1: Playbook Purpose \& Scope

**Load Trigger:** User asks "what does this playbook do?" or selects a playbook

```markdown
## Playbook: {PLAYBOOK_NAME}

### Purpose
{2-3 sentence summary of what this playbook accomplishes}

### Scope
- **In Scope:** {List of tasks this playbook handles}
- **Out of Scope:** {List of related tasks this playbook does NOT handle}

### Use Cases
1. {Primary use case}
2. {Secondary use case}
3. {Edge case if applicable}

### Expected Outcome
After successful execution:
- {Outcome 1}
- {Outcome 2}
- {Outcome 3}
```

**Example:**
```markdown
## Playbook: deploy_app

### Purpose
Deploys application containers to specified environment with health checks and rollback capability.

### Scope
- **In Scope:** Container deployment, health verification, rollback on failure
- **Out of Scope:** Database migrations, SSL certificate management, DNS updates

### Use Cases
1. Deploy new application version to production
2. Rollback to previous version on failure
3. Scale application to additional nodes

### Expected Outcome
- Application running on target nodes
- Health checks passing
- Previous version archived for rollback
```

---

## Module 2: Dependencies

**Load Trigger:** User asks "what does this depend on?" or pre-flight check requested

```markdown
## Dependencies: {PLAYBOOK_NAME}

### Required Services
| Service | Version | Purpose | Fallback |
|---------|---------|---------|----------|
| {Service} | {Version} | {Why needed} | {Alternative} |

### Required Roles
- `{role_name}` - {Purpose}
- `{role_name}` - {Purpose}

### Required Variables
```yaml
{variable_name}: {description}
{variable_name}: {description}
```

### External Dependencies
- **Network:** {Required connectivity}
- **Storage:** {Required disk space}
- **Permissions:** {Required sudo/API access}

### Dependency Check Command
```bash
{command to verify all dependencies}
```
```

---

## Module 3: Data Sources

**Load Trigger:** User asks "what data does this use?" or data validation requested

```markdown
## Data Sources: {PLAYBOOK_NAME}

### Input Data
| Source | Format | Location | Update Frequency |
|--------|--------|----------|------------------|
| {Source} | {JSON/YAML/CSV} | {Path/URL} | {Real-time/Daily/Manual} |

### Data Validation
```python
# Validation rules
{validation_logic}
```

### Data Storage
- **Primary:** {Location of primary data store}
- **Backup:** {Location of backup data}
- **Cache:** {Location of cached data, if any}

### Data Flow Diagram
```
{Source} → {Validation} → {Transformation} → {Destination}
```

### Data Retention
- **Active Data:** {Retention period}
- **Archived Data:** {Retention period}
- **Logs:** {Retention period}
```

---

## Module 4: Execution Conditions

**Load Trigger:** User asks "when should this run?" or condition check requested

```markdown
## Execution Conditions: {PLAYBOOK_NAME}

### Trigger Conditions
Execute when **ANY** of these are true:
- [ ] {Condition 1: e.g., "CPU > 80% for 5 minutes"}
- [ ] {Condition 2: e.g., "New deployment request received"}
- [ ] {Condition 3: e.g., "Scheduled maintenance window"}

### Pre-Flight Checks
All must pass before execution:
- [ ] {Check 1: e.g., "Target nodes reachable"}
- [ ] {Check 2: e.g., "Sufficient disk space (>10GB)"}
- [ ] {Check 3: e.g., "No other deployments in progress"}

### Contraindications
Do **NOT** execute if:
- ❌ {Contraindication 1: e.g., "Production freeze active"}
- ❌ {Contraindication 2: e.g., "Critical bug known in version"}
- ❌ {Contraindication 3: e.g., "Backup incomplete"}

### Optimal Timing
- **Best:** {Time window: e.g., "2:00-5:00 AM local time"}
- **Acceptable:** {Time window: e.g., "10:00-11:00, 14:00-15:00"}
- **Avoid:** {Time window: e.g., "9:00-10:00, 17:00-18:00"}
```

---

## Module 5: Performance Metrics

**Load Trigger:** User asks "how long does this take?" or performance optimization requested

```markdown
## Performance Metrics: {PLAYBOOK_NAME}

### Expected Execution Times
| Environment | Avg Time | P95 Time | P99 Time | Target |
|-------------|----------|----------|----------|--------|
| Development | {time} | {time} | {time} | <{target} |
| Staging | {time} | {time} | {time} | <{target} |
| Production | {time} | {time} | {time} | <{target} |

### Resource Usage
| Metric | Avg | Peak | Limit |
|--------|-----|------|-------|
| CPU | {percentage} | {percentage} | {percentage} |
| Memory | {GB} | {GB} | {GB} |
| Network | {Mbps} | {Mbps} | {Mbps} |
| Disk I/O | {MB/s} | {MB/s} | {MB/s} |

### Performance History
| Date | Execution Time | Notes |
|------|----------------|-------|
| {date} | {time} | {success/failure/notes} |
| {date} | {time} | {success/failure/notes} |

### Optimization Tips
1. {Tip 1: e.g., "Run during low-traffic hours"}
2. {Tip 2: e.g., "Clear cache before execution"}
3. {Tip 3: e.g., "Use parallel execution for large deployments"}
```

---

## Module 6: Hardware Specifications

**Load Trigger:** User asks "what hardware is needed?" or capacity planning requested

```markdown
## Hardware Specifications: {PLAYBOOK_NAME}

### Minimum Requirements
| Component | Specification | Purpose |
|-----------|---------------|---------|
| CPU | {cores} @ {speed} | {Workload type} |
| RAM | {GB} | {Memory-intensive operations} |
| Storage | {GB} {type} | {Storage type: SSD/HDD} |
| Network | {speed} | {Network-intensive operations} |

### Recommended Specifications
| Component | Specification | Purpose |
|-----------|---------------|---------|
| CPU | {cores} @ {speed} | {Optimal performance} |
| RAM | {GB} | {Headroom for spikes} |
| Storage | {GB} {type} | {Faster I/O} |
| Network | {speed} | {Redundancy} |

### Load Characteristics
- **CPU Load:** {Low/Medium/High} - {Description of CPU-intensive tasks}
- **Memory Load:** {Low/Medium/High} - {Description of memory usage patterns}
- **I/O Load:** {Low/Medium/High} - {Description of disk/network I/O}

### Scaling Recommendations
- **Vertical Scaling:** {When to add more resources to existing node}
- **Horizontal Scaling:** {When to add more nodes}
- **Threshold:** {Specific metrics that trigger scaling}

### Compatible Nodes
| Node | Specs | Performance | Recommendation |
|------|-------|-------------|----------------|
| {node} | {specs} | {rating} | {Recommended/Not Recommended} |
```

---

## Execution Framework

### Step 1: Keyword Recognition (Core - Always Loaded)
```python
def recognize_trigger(user_prompt):
    """
    Match user prompt to registered trigger keywords.
    Returns: (playbook_name, confidence_score)
    """
    triggers = load_trigger_keywords()  # From ansible/group_vars/trigger_keywords.yml
    
    for keyword, playbook in triggers.items():
        if keyword in user_prompt.lower():
            return playbook, 0.9
        # Fuzzy matching for partial matches
        if any(word in user_prompt.lower() for word in keyword.split('_')):
            return playbook, 0.7
    
    return None, 0.0
```

### Step 2: Playbook Selection (Core - Always Loaded)
```python
def select_playbook(trigger, context):
    """
    Select appropriate playbook based on trigger and context.
    Uses progressive loading: core → metadata → full playbook
    """
    # Load only metadata first (~50 tokens)
    metadata = load_playbook_metadata(trigger)
    
    # Check conditions
    if not check_conditions(metadata['conditions']):
        return suggest_alternative(metadata)
    
    # Load full playbook only if conditions met
    playbook = load_full_playbook(trigger)
    return playbook
```

### Step 3: Module Loading (On-Demand)
```python
def load_module(playbook_name, module_type, user_query):
    """
    Load specific module based on user query type.
    Only loads what's needed, keeping context minimal.
    """
    module_map = {
        'what': 'purpose',
        'why': 'purpose',
        'depend': 'dependencies',
        'require': 'dependencies',
        'data': 'data_sources',
        'when': 'conditions',
        'how long': 'performance',
        'fast': 'performance',
        'hardware': 'hardware_specs',
        'specs': 'hardware_specs',
    }
    
    for query_pattern, module in module_map.items():
        if query_pattern in user_query.lower():
            return load_module_file(playbook_name, module)
    
    # Default: load purpose module
    return load_module_file(playbook_name, 'purpose')
```

### Step 4: Execution with Memory Reuse (Core - Always Loaded)
```python
def execute_with_memory_reuse(playbook, user_context):
    """
    Execute playbook while maintaining critical state in memory.
    Reloads non-critical components as needed.
    """
    # Persistent state (kept in memory)
    persistent_state = {
        'trigger_keyword': playbook['trigger'],
        'execution_id': generate_id(),
        'start_time': datetime.now(),
    }
    
    # Load task components sequentially (not all at once)
    for task in playbook['tasks']:
        # Load task definition
        task_def = load_task(task['name'])
        
        # Execute task
        result = execute_task(task_def, persistent_state)
        
        # Update state
        persistent_state[f'task_{task["name"]}_result'] = result
        
        # Clear task from memory (except results)
        clear_task_from_memory(task['name'])
    
    return persistent_state
```

### Step 5: Error Handling (Core - Always Loaded)
```python
def handle_error(error, playbook_context):
    """
    Handle errors with minimal context reload.
    Only loads error-specific recovery information.
    """
    error_type = classify_error(error)
    
    # Load only recovery steps for this error type
    recovery = load_recovery_steps(error_type)
    
    # Attempt recovery
    if recovery['auto_retry']:
        return retry_with_adjustments(playbook_context, recovery['adjustments'])
    else:
        return request_user_intervention(error, recovery)
```

---

## Wiki Documentation Template

Every playbook **MUST** have a corresponding wiki page at:
`wiki/technical-infrastructure/ansible/playbooks/{PLAYBOOK_NAME}.md`

```markdown
# Playbook: {PLAYBOOK_NAME}

**Trigger Keywords:** `{keyword1}`, `{keyword2}`, `{keyword3}`  
**Version:** {version}  
**Last Updated:** {date}  
**Status:** {Active/Deprecated/Experimental}

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Purpose** | {1-sentence summary} |
| **Execution Time** | {avg time} |
| **Hardware** | {minimum specs} |
| **Dependencies** | {count} services, {count} roles |

---

## Full Documentation

{Include all 6 modules here for complete reference}

---

## Execution History

| Date | Trigger | Result | Duration | Notes |
|------|---------|--------|----------|-------|
| {date} | {keyword} | ✅/❌ | {time} | {notes} |

---

## Related Playbooks

- [{playbook_name}]({link}) - {relationship}
- [{playbook_name}]({link}) - {relationship}

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {date} | {author} | Initial version |
```

---

## Update Workflow

### When Creating a New Playbook

1. **Generate playbook YAML** using `ansible-playbook-template.yml`
2. **Register trigger keywords** in `ansible/group_vars/trigger_keywords.yml`
3. **Create wiki page** using documentation template above
4. **Add to schedule** if recurring execution needed
5. **Test with low-capacity model** (gemma4:e4b or qwen3.5:4b)
6. **Validate** using `orchestrator-status.py --health`

### When Updating an Existing Playbook

1. **Check current version** in wiki
2. **Update YAML** with changes
3. **Update wiki documentation** (all 6 modules if affected)
4. **Increment version** in wiki page header
5. **Add change log entry**
6. **Re-test** with low-capacity model
7. **Schedule background update** if non-urgent

### Background Update Scheduling

For non-urgent updates, use background scheduling:

```bash
# Schedule wiki update for next low-usage window
python3 scripts/schedule-wiki-update.py \
  --playbook {playbook_name} \
  --priority low \
  --window "2:00-5:00"
```

---

## Model Optimization Guidelines

### For gemma4:e4b (8K context, ~4B params)
- **Always use chunking** - Split prompts into 150-token segments
- **Load 1-2 modules max** at a time
- **Keep persistent state under 100 tokens**
- **Use progressive loading** for all multi-step tasks

### For qwen3.5:4b (32K context, ~4B params)
- **Optional chunking** - Only for prompts >500 tokens
- **Can load 2-3 modules** together
- **Keep persistent state under 200 tokens**
- **Batch related tasks** when possible

### For qwen3:8b (32K context, ~8B params)
- **Minimal chunking needed** - Full prompts usually fit
- **Can load all modules** if needed
- **Keep persistent state under 300 tokens**
- **Flexible loading strategy**

---

## Quality Checklist

Before marking a playbook as **COMPLETE**:

- [ ] Trigger keywords registered in `ansible/group_vars/trigger_keywords.yml`
- [ ] Playbook YAML follows `ansible-playbook-template.yml` structure
- [ ] Wiki page created with all 6 modules
- [ ] Performance benchmarks documented
- [ ] Hardware specifications documented
- [ ] Execution conditions clearly defined
- [ ] Dependencies listed and validated
- [ ] Data sources documented with locations
- [ ] Tested with at least one low-capacity model
- [ ] Background schedule configured (if applicable)
- [ ] Orchestrator health check passes

---

## Related Documents

- [Playbook Template](../ansible-playbook-template.yml)
- [Wiki Structure](./wiki-playbook-structure.md)
- [Low-Capacity Validation](./technical-infrastructure/low-capacity-model-validation.md)
- [Orchestration Status](./technical-infrastructure/orchestration-status-monitor.md)
- [Trigger Keywords](../ansible/group_vars/trigger_keywords.yml)
- [Schedule Config](../orchestration/schedules.yml)
- [Backlog Item](/operational/BACKLOG.md#ti-playbook-master)

---

**Maintenance:** This master prompt should be reviewed and updated monthly or when new optimization techniques are discovered.

**Owner:** Technical Infrastructure Team  
**Review Cycle:** Monthly  
**Next Review:** 2026-06-05
