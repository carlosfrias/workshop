# Agents

Agent definitions are the **guided experience layer** of Project Blueprint. They describe a specialist AI agent that can be dispatched to set up a project in its own isolated context window.

## Why a Custom Agent?

The skill and prompt templates work within the current session — the orchestrator reads the skill and follows the steps using its own context. A custom agent is different: it runs in a **separate process** with its own context window, model, and tool set.

This matters when you want:

- **Isolation** — the setup process doesn't consume the orchestrator's context window
- **Different model** — the builder can use a more capable model for the interview and scaffolding
- **Interactive interview** — the agent asks questions and waits for answers, without cluttering the main conversation
- **Clean handoff** — the agent creates everything, reports a summary, and exits

### How it differs from the skill and prompts

| Layer | Context | Best For |
|-------|---------|----------|
| **Skill** | Loads into your current session | Quick setup, no process overhead |
| **Prompt template** | Expands a command in your editor | Fast invocation with parameters |
| **Custom agent** | Separate context window | Guided, interactive setup when you want isolation |

All three read the same `SKILL.md`. The agent is just another way to invoke it.

### Why not always use the agent?

An agent spawns a new `pi` process, which adds startup time. For a quick `add-domain` operation, loading the skill directly in the current session is faster. The agent is best when you want a full guided setup experience — asking questions, getting recommendations, and reviewing the plan before anything is created.

## What's Included

| Agent | File | What It Does |
|-------|------|-------------|
| `project-blueprint.project-builder` | `project-blueprint-project-builder.md` | Interviews you, reads the skill, creates the full project structure |
| `project-blueprint.auto-documenter` | `project-blueprint-auto-documenter.md` | Generates session notes + assesses sessions for AGENTS.md refinement potential |
| `project-blueprint.post-completion-architect` | `project-blueprint-post-completion-architect.md` | Analyzes completed sessions, extracts golden path, generates optimized AGENTS.md files |

## Usage

### From any pi session

```typescript
{ agent: "project-builder", task: "Set up a project for my healthcare analytics work" }
```

### From a prompt template

```
/new-project healthcare analytics with billing and compliance
```

The prompt template loads the skill in the current session, which is equivalent but without spawning a separate process.

### What the project-builder does

1. **Reads the skill** at `../skills/project-blueprint/SKILL.md`
2. **Interviews you** about your project (name, domains, models, wiki location, check-back)
3. **Reads the templates** and customizes them for your project
4. **Creates everything** following the skill's 10-phase process
5. **Verifies** the token budget and file structure
6. **Reports** a summary of what was created

### Configuration

The agent definition's frontmatter controls its behavior:

| Setting | Value | Why |
|---------|-------|-----|
| `model` | `anthropic/claude-sonnet-4-6` | Capable model for the interview and scaffolding |
| `thinking` | `high` | Thoughtful analysis of domain structure and routing |
| `systemPromptMode` | `replace` | Clean system prompt focused on project setup |
| `inheritProjectContext` | `true` | Sees the current project context for awareness |
| `inheritSkills` | `true` | Can load the project-blueprint skill |
| `tools` | `read, write, edit, bash, intercom` | File operations + orchestrator communication |

## Creating Your Own Agent Definitions

If you want a specialized variant of the project-builder (e.g., one that only adds domains, or one that uses a local model), create a new `.md` file in your agents directory:

```markdown
---
name: my-agent
description: What this agent does
tools: read, write, bash
model: ollama/qwen3:8b
systemPromptMode: replace
inheritProjectContext: false
cwd: ./my-domain
---
Your system prompt goes here.
```

Save it as `~/.pi/agent/agents/my-agent.md` (user-level) or `.pi/agents/my-agent.md` (project-level) and invoke it with `{ agent: "my-agent", task: "..." }`.