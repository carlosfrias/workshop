# Module 3: Data Sources

**Version:** 1.0  
**Tokens:** ~130  
**Load Trigger:** User asks "data", "input", "source", "file", "config"  
**Unload:** After response sent

---

## Input Data

| Source | Format | Location | Update Frequency |
|--------|--------|----------|------------------|
| {Source} | {JSON/YAML/CSV} | {Path/URL} | {Real-time/Daily/Manual} |

**Example:**

| Source | Format | Location | Update Frequency |
|--------|--------|----------|------------------|
| Application Config | YAML | `config/app.yml` | Manual (per deploy) |
| Environment Vars | ENV | `.env` file | Manual (per deploy) |
| Container Image | Docker | Registry URL | Per version release |

---

## Data Validation

```python
# Validation rules
{validation_logic}
```

**Example:**

```python
# Validate config
assert 'app_name' in config
assert 'version' in config
assert semver.valid(config['version'])

# Validate environment
assert os.getenv('DATABASE_URL') is not None
assert os.getenv('API_KEY') is not None
```

---

## Data Storage

| Type | Location | Purpose |
|------|----------|---------|
| **Primary** | {Path/URL} | Main data store |
| **Backup** | {Path/URL} | Backup copy |
| **Cache** | {Path/URL} | Cached data (if any) |

**Example:**

| Type | Location | Purpose |
|------|----------|---------|
| **Primary** | `config/app.yml` | Application configuration |
| **Backup** | `config/backup/app.yml.bak` | Previous version |
| **Cache** | `/tmp/app_config.cache` | Cached for quick access |

---

## Data Flow Diagram

```
{Source} → {Validation} → {Transformation} → {Destination}
```

**Example:**

```
config/app.yml → YAML parse → Merge with ENV → Container deploy
```

---

## Data Retention

| Data Type | Retention Period | Archive Location |
|-----------|------------------|------------------|
| Active Data | {Period} | {Path} |
| Archived Data | {Period} | {Path} |
| Logs | {Period} | {Path} |

**Example:**

| Data Type | Retention Period | Archive Location |
|-----------|------------------|------------------|
| Active Config | Current version | `config/app.yml` |
| Archived Config | 90 days | `archive/config/` |
| Deployment Logs | 30 days | `logs/deployments/` |

---

## Data Sensitivity

| Data | Sensitivity | Encryption |
|------|-------------|------------|
| {Data item} | {Public/Internal/Secret} | {Yes/No} |

**Example:**

| Data | Sensitivity | Encryption |
|------|-------------|------------|
| App name | Public | No |
| API keys | Secret | Yes (Ansible Vault) |
| Database URL | Internal | Yes (Ansible Vault) |

---

## Questions This Module Answers

- ✅ "What data does {playbook} use?"
- ✅ "Where does {playbook} get its input?"
- ✅ "What files does {playbook} read?"
- ✅ "Is {data} encrypted?"

---

## Questions This Module Does NOT Answer

- ❌ "What does {playbook} do?" → Load Module 1
- ❌ "What does {playbook} depend on?" → Load Module 2
- ❌ "When should {playbook} run?" → Load Module 4
- ❌ "How long does {playbook} take?" → Load Module 5
- ❌ "What hardware is needed?" → Load Module 6

---

**Module End**

*Return to core prompt after use*
