# pi-subagents Configuration Reference

Complete configuration reference for the pi-subagents extension.

---

## Config File Location

`~/.pi/agent/extensions/subagent/config.json`

---

## Current Configuration (Trading Workspace)

```json
{
  "subagents": {
    "intercomBridge": {
      "mode": "always",
      "instructionFile": "./intercom-bridge-custom.md"
    },
    "agentOverrides": {}
  }
}
```

---

## All Config Options

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| **intercomBridge** | `mode` | `"always"` | When to inject bridge: `"always"`, `"fork-only"`, `"off"` |
| | `instructionFile` | (built-in default) | Path to custom bridge instructions (relative to config dir) |
| **parallel** | `maxTasks` | `8` | Maximum parallel tasks |
| | `concurrency` | `4` | Maximum concurrent tasks |
| **maxSubagentDepth** | — | `2` | Maximum nesting depth (env `PI_SUBAGENT_MAX_DEPTH`) |
| **defaultSessionDir** | — | (derived from parent session) | Override session log directory |
| **agentOverrides** | — | `{}` | Override builtin agent fields without copying files |
| **worktreeSetupHook** | — | (none) | Script to run per worktree during parallel `worktree: true` |
| **worktreeSetupHookTimeoutMs** | — | `30000` | Timeout for worktree setup hook |

---

## Agent Overrides

Override builtin agent fields in settings without modifying the original files. Project scope (`.pi/settings.json`) overrides user scope (`~/.pi/agent/settings.json`).

### Example Configuration

```json
{
  "subagents": {
    "agentOverrides": {
      "reviewer": {
        "model": "anthropic/claude-opus-4",
        "inheritProjectContext": false
      },
      "scout": {
        "disabled": true
      },
      "worker": {
        "thinking": "high",
        "fallbackModels": ["openai/gpt-5-mini", "anthropic/claude-sonnet-4"]
      }
    }
  }
}
```

### Disable a Builtin Agent

Set `disabled: true` to hide a builtin from discovery (it still appears in `/agents` so you can re-enable it):

```json
{
  "subagents": {
    "agentOverrides": {
      "scout": {
        "disabled": true
      }
    }
  }
}
```

### Disable All Builtins

```json
{
  "subagents": {
    "disableBuiltins": true
  }
}
```

Then selectively re-enable with `"disabled": false` in individual overrides.

### Overrideable Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Model to use |
| `fallbackModels` | string or string[] | Ordered backup models |
| `thinking` | string | Thinking level (off, minimal, low, medium, high, xhigh) |
| `systemPromptMode` | string | `replace` or `append` |
| `inheritProjectContext` | boolean | Include AGENTS.md/CLAUDE.md |
| `inheritSkills` | boolean | Include discovered skills |
| `disabled` | boolean | Hide from discovery |
| `skills` | string | Comma-separated skill names |
| `tools` | string | Comma-separated builtin tool names |
| `systemPrompt` | string | Override the agent's markdown body |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PI_SUBAGENT_MAX_DEPTH` | `2` | Maximum nesting depth (orchestrator → sub-agent → sub-sub-agent) |
| `PI_SUBAGENT_DEPTH` | (internal) | Current depth (set automatically, don't set manually) |

---

## Global Settings Integration

The `settings.json` at `~/.pi/agent/settings.json` also manages packages:

```json
{
  "lastChangelogVersion": "0.67.68",
  "defaultProvider": "ollama",
  "defaultModel": "glm-5.1:cloud",
  "packages": [
    "npm:@tintinweb/pi-subagents",
    "npm:pi-web-access",
    "npm:pi-subagents",
    "npm:@aliou/pi-guardrails",
    "npm:pi-coding-agent",
    "npm:@yeliu84/pi-model-router",
    "npm:pi-intercom"
  ],
  "skills": [
    "~/.pi/agent/skills/pi-skills/README.md"
  ],
  "defaultThinkingLevel": "medium"
}
```

**Important:** The subagent config at `extensions/subagent/config.json` is separate from `settings.json` — the subagent extension reads its own config file.

---

## Intercom Bridge Configuration

For detailed intercom bridge setup, see [pi-intercom-setup.md](../guides/pi-intercom-setup.md).

### Quick Reference

```json
{
  "subagents": {
    "intercomBridge": {
      "mode": "always",
      "instructionFile": "./intercom-bridge-custom.md"
    }
  }
}
```

| Mode | When Bridge Is Active |
|------|----------------------|
| `"always"` | All sub-agents (fresh + forked contexts) |
| `"fork-only"` | Only forked contexts (`context: "fork"`) |
| `"off"` | Never (no bridge instructions injected) |

---

## Worktree Setup Hook

For parallel execution with git worktree isolation, you can run a setup script per worktree:

```json
{
  "subagents": {
    "worktreeSetupHook": "./scripts/setup-worktree.sh",
    "worktreeSetupHookTimeoutMs": 30000
  }
}
```

The script runs in each worktree before the agent starts. Use it to:
- Install dependencies
- Set environment variables
- Initialize local state

---

## Model Fallback Configuration

Configure fallback models for quota errors or rate limits:

```json
{
  "subagents": {
    "agentOverrides": {
      "worker": {
        "model": "anthropic/claude-sonnet-4",
        "fallbackModels": [
          "openai/gpt-5-mini",
          "anthropic/claude-sonnet-4"
        ]
      }
    }
  }
}
```

Fallback models are tried in order when the primary model fails.

---

## Parallel Execution Configuration

Control concurrent task execution:

```json
{
  "subagents": {
    "parallel": {
      "maxTasks": 8,
      "concurrency": 4
    }
  }
}
```

| Setting | Description |
|---------|-------------|
| `maxTasks` | Maximum total parallel tasks in a single `/parallel` call |
| `concurrency` | Maximum tasks running simultaneously (default: 4) |

---

## Session Directory Configuration

Override where session logs are stored:

```json
{
  "subagents": {
    "defaultSessionDir": "/path/to/sessions"
  }
}
```

By default, sessions are stored in a temp directory derived from the parent session.

---

## Verification

After modifying config, restart pi or run:

```
/reload
```

This reloads extensions, skills, prompts, and context files without restarting pi.

Verify the config is loaded:

```typescript
subagent({ action: "list" })
```

Check that agent overrides are applied and the intercom bridge is active.

---

## See Also

- [pi-intercom Setup](../guides/pi-intercom-setup.md) — Intercom broker and bridge configuration
- [Real-Time Control Patterns](real-time-control-patterns.md) — Intercom ask/send patterns
- [Sub-Agent Packages Reference](subagent-packages-reference.md) — Feature overview and comparison
