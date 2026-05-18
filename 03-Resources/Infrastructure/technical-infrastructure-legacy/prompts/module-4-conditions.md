# Module 4: Execution Conditions

**Version:** 1.0  
**Tokens:** ~140  
**Load Trigger:** User asks "when", "condition", "trigger", "should I run"  
**Unload:** After response sent

---

## Trigger Conditions

**Execute when ANY of these are true:**

- [ ] {Condition 1}
- [ ] {Condition 2}
- [ ] {Condition 3}

**Example:**

- [ ] New application version available
- [ ] Scheduled deployment window (2:00-5:00 AM)
- [ ] Manual deployment request received

---

## Pre-Flight Checks

**All must pass before execution:**

- [ ] {Check 1}
- [ ] {Check 2}
- [ ] {Check 3}

**Example:**

- [ ] Target nodes reachable (SSH test)
- [ ] Sufficient disk space (>10GB available)
- [ ] No other deployments in progress
- [ ] Health check passed (TI-031: status = healthy)

---

## Contraindications

**Do NOT execute if:**

- ❌ {Contraindication 1}
- ❌ {Contraindication 2}
- ❌ {Contraindication 3}

**Example:**

- ❌ Production freeze active (check with release manager)
- ❌ Critical bug known in this version (see JIRA-1234)
- ❌ Backup incomplete or failed
- ❌ TI-031 health status = stressed or critical

---

## Optimal Timing

| Time Window | Suitability | Reason |
|-------------|-------------|--------|
| **Best** | {Time range} | {Why optimal} |
| **Acceptable** | {Time range} | {Why acceptable} |
| **Avoid** | {Time range} | {Why avoid} |

**Example:**

| Time Window | Suitability | Reason |
|-------------|-------------|--------|
| **Best** | 2:00-5:00 AM | Low traffic, minimal user impact |
| **Acceptable** | 10:00-11:00, 14:00-15:00 | Moderate traffic, team available |
| **Avoid** | 9:00-10:00, 17:00-18:00 | Peak traffic, shift change |

---

## Health Check Requirements (TI-031)

**Mandatory before execution:**

```bash
python3 technical-infrastructure/scripts/orchestrator_health.py --json
```

**Required status:**

| Health Status | RAM | CPU | Swap | Can Execute? |
|---------------|-----|-----|------|--------------|
| **HEALTHY** | <80% | <4.0 | 0 | ✅ Yes (local) |
| **STRESSED** | 80-92% | 4.0-6.0 | 0 | ⚠️ Decompose + cloud low |
| **CRITICAL** | >92% | >6.0 | >0 | ❌ Decompose + cloud high |

---

## Environmental Conditions

| Condition | Required Value | Check Command |
|-----------|----------------|---------------|
| Network | All nodes reachable | `ping fnet{1-7}` |
| Storage | >10GB free | `df -h /srv` |
| Memory | >4GB available | `free -g` |
| TI-031 Status | healthy | `orchestrator_health.py` |

---

## Scheduling

**For scheduled execution:**

```yaml
# Add to orchestration/schedules.yml
- name: "{playbook_name} scheduled run"
  schedule: "0 3 * * *"  # Daily at 3:00 AM
  script: "scripts/{playbook_name}_scheduler.sh"
  priority: low
  background: true
```

---

## Questions This Module Answers

- ✅ "When should {playbook} run?"
- ✅ "What conditions trigger {playbook}?"
- ✅ "Can I run {playbook} now?"
- ✅ "Should I run {playbook} during {time}?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} do?" → Load Module 1
- ❌ "What does {playbook} depend on?" → Load Module 2
- ❌ "What data does {playbook} use?" → Load Module 3
- ❌ "How long does {playbook} take?" → Load Module 5
- ❌ "What hardware is needed?" → Load Module 6

---

**Module End**

*Return to core prompt after use*
