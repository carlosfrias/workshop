# Module 1: Purpose & Scope

**Version:** 1.0  
**Tokens:** ~120  
**Load Trigger:** User asks "what", "why", "purpose", "does"  
**Unload:** After response sent

---

## Purpose

**{PLAYBOOK_NAME}** accomplishes:

{2-3 sentence summary of what this playbook does}

**Example:**
> `deploy_app_v1.0.yml` deploys application containers to specified environments with automated health checks and rollback capability on failure.

---

## Scope

### In Scope ✅

- {Task 1 this playbook handles}
- {Task 2 this playbook handles}
- {Task 3 this playbook handles}

**Example:**
- Container deployment to target nodes
- Health check verification
- Automatic rollback on failure

### Out of Scope ❌

- {Task this playbook does NOT handle}
- {Task this playbook does NOT handle}

**Example:**
- Database migrations
- SSL certificate management
- DNS updates

---

## Use Cases

1. **Primary:** {Most common use case}
   - Example: Deploy new application version to production

2. **Secondary:** {Less common but supported}
   - Example: Rollback to previous version on failure

3. **Edge Case:** {Rare but handled}
   - Example: Scale application to additional nodes

---

## Expected Outcome

After **successful** execution:

- ✅ {Outcome 1}
- ✅ {Outcome 2}
- ✅ {Outcome 3}

**Example:**
- ✅ Application running on target nodes
- ✅ Health checks passing (all endpoints responding)
- ✅ Previous version archived for rollback

---

## Related Playbooks

| Playbook | Relationship |
|----------|--------------|
| `{playbook_name}` | {How related} |
| `{playbook_name}` | {How related} |

**Example:**

| Playbook | Relationship |
|----------|--------------|
| `check_health_v1.0.yml` | Run after deployment |
| `rollback_app_v1.0.yml` | Use on deployment failure |

---

## Questions This Module Answers

- ✅ "What does {playbook} do?"
- ✅ "Why would I use {playbook}?"
- ✅ "What is the purpose of {playbook}?"
- ✅ "Does {playbook} handle {task}?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} depend on?" → Load Module 2
- ❌ "What data does {playbook} use?" → Load Module 3
- ❌ "When should {playbook} run?" → Load Module 4
- ❌ "How long does {playbook} take?" → Load Module 5
- ❌ "What hardware is needed?" → Load Module 6

---

**Module End**

*Return to core prompt after use*
