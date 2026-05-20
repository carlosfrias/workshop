# Agent Definitions

## study

| Field | Value |
|-------|-------|
| Name | `study` |
| Description | Bible passage analysis, exegesis, word studies, and commentary research |
| Model | `ollama/qwen3.5:397b` |
| Tools | read, write, edit, bash, intercom |
| CWD | `./study` |
| Inherit Project Context | false |
| System Prompt Mode | replace |

**Usage:** Analyzing passages, word studies, cross-referencing, original language research, commentary analysis.

---

## devotional

| Field | Value |
|-------|-------|
| Name | `devotional` |
| Description | Devotional content, meditation guides, prayer frameworks, and spiritual formation |
| Model | `ollama/qwen3.5:397b` |
| Tools | read, write, edit, bash, intercom |
| CWD | `./devotional` |
| Inherit Project Context | false |
| System Prompt Mode | replace |

**Usage:** Creating devotionals, prayer guides, meditation content, spiritual formation resources.

---

## data

| Field | Value |
|-------|-------|
| Name | `data` |
| Description | Bible data fetching, API clients, scrapers, and data pipelines |
| Model | `ollama/deepseek-v4-pro` |
| Tools | read, write, edit, bash, intercom |
| CWD | `./data` |
| Inherit Project Context | false |
| System Prompt Mode | replace |

**Usage:** Building scrapers, API clients, data pipelines, caching systems for Bible text.

---

## site

| Field | Value |
|-------|-------|
| Name | `site` |
| Description | MkDocs site build, deployment, and configuration for His Desk |
| Model | `ollama/deepseek-v4-pro` |
| Tools | read, write, edit, bash, intercom |
| CWD | `./site` |
| Inherit Project Context | false |
| System Prompt Mode | replace |

**Usage:** Building and deploying the His Desk site, configuring navigation, testing builds.