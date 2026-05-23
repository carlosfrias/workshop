# Agent Definitions

## vault Agent

| Field | Value |
|-------|-------|
| Name | vault |
| Description | Study notes, curriculum tracking, and knowledge management |
| Model | ollama/qwen3.5:4b |
| Tools | read, write, edit, bash, intercom |
| CWD | ./vault |
| Context | inheritedProjectContext: false, systemPromptMode: replace |
| File | `.pi/agents/vault.md` |

**When to use:** Study notes, curriculum progress tracking, ICM concept research, schedule updates, reading comprehension.

---

## workshop Agent

| Field | Value |
|-------|-------|
| Name | workshop |
| Description | Code, ICM implementations, practice exercises, and workspace building |
| Model | ollama/deepseek-v4-pro:cloud |
| Tools | read, write, edit, bash, intercom |
| CWD | ./workshop |
| Context | inheritedProjectContext: false, systemPromptMode: replace |
| File | `.pi/agents/workshop.md` |

**When to use:** Building ICM workspaces, writing pipeline code, implementing exercises, creating practice projects.

---

## Intercom Pattern

Both agents use the `delegate` check-back pattern:
- Report results after completing tasks
- Ask for guidance on ambiguity or blockers
- Wait for orchestrator response before proceeding on uncertain points