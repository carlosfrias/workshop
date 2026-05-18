# Module 2: Dependencies

**Version:** 1.0  
**Tokens:** ~130  
**Load Trigger:** User asks "depend", "require", "prerequisite", "need"  
**Unload:** After response sent

---

## Required Services

| Service | Version | Purpose | Fallback |
|---------|---------|---------|----------|
| {Service} | {Version} | {Why needed} | {Alternative} |

**Example:**

| Service | Version | Purpose | Fallback |
|---------|---------|---------|----------|
| Docker | 24.0+ | Container runtime | Podman 4.0+ |
| Ollama | 0.1.20+ | Model serving | None (required) |
| Ansible | 2.15+ | Playbook execution | None (required) |

---

## Required Roles

- `{role_name}` — {Purpose}
- `{role_name}` — {Purpose}

**Example:**

- `docker_admin` — Docker daemon access
- `ansible_runner` — Playbook execution

---

## Required Variables

```yaml
{variable_name}: {description}
{variable_name}: {description}
```

**Example:**

```yaml
target_environment: dev|staging|production
app_version: Semantic version (e.g., 1.2.3)
health_check_timeout: Seconds (default: 30)
```

---

## External Dependencies

### Network

- {Required connectivity}

**Example:**
- Internet access for container image pull
- Access to container registry (registry.example.com:5000)

### Storage

- {Required disk space}

**Example:**
- 10GB available for container images
- 5GB for application data

### Permissions

- {Required sudo/API access}

**Example:**
- Sudo access for Docker commands
- Read access to container registry

---

## Dependency Check Command

```bash
{command to verify all dependencies}
```

**Example:**

```bash
ansible-playbook playbooks/check_dependencies.yml \
  --extra-vars "playbook=deploy_app"
```

---

## Missing Dependency Handling

**If dependency missing:**

1. ❌ Do NOT execute playbook
2. ℹ️ Return missing dependency list
3. 💡 Suggest installation commands
4. 📝 Log to `wiki/operational/sessions/dependency-failures.jsonl`

**Example Response:**

```markdown
**Status:** ❌ DEPENDENCY MISSING

**Missing:**
- Docker 24.0+ (found: 20.10)

**Install:**
```bash
sudo apt-get install docker-ce=24.0*
```

**Retry:** After installation, run playbook again.
```

---

## Questions This Module Answers

- ✅ "What does {playbook} depend on?"
- ✅ "What is required for {playbook}?"
- ✅ "Can I run {playbook} without {dependency}?"
- ✅ "What version of {service} is needed?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} do?" → Load Module 1
- ❌ "What data does {playbook} use?" → Load Module 3
- ❌ "When should {playbook} run?" → Load Module 4
- ❌ "How long does {playbook} take?" → Load Module 5
- ❌ "What hardware is needed?" → Load Module 6

---

**Module End**

*Return to core prompt after use*
