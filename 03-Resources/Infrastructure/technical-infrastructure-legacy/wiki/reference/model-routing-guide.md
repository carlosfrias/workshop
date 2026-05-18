# Model Routing Guide

Comprehensive guide to the automated model routing system in the Trading Desk. This system uses a keyword-and-domain-driven approach to ensure the most efficient model is used for every task, balancing cost, latency, and cognitive capacity.

## Routing Architecture

The router operates by scanning the user's prompt and the current session context for specific **Keywords** and **Domains**. When a match is found, the router selects the associated model and thinking level.

### Model Tiers

| Tier | Model | Capability | Use Case |
|-------|-------|-----------|----------|
| **Ultra Reasoning** | `kimi-k2.6:cloud` | 1.04T Params, High Thinking | Mission-critical architecture, deep-dive research, complex system design. |
| **Reasoning** | `deepseek-v3.1:671b-cloud` | 671B Params, Med Thinking | Strategic analysis, signal evaluation, complex debugging, position sizing logic. |
| **Cloud Standard** | `qwen3.5:397b-cloud` | 397B Params, Low Thinking | Detailed summaries, standard explanations, high-quality drafting. |
| **Local Flagship** | `gemma4:e4b` | Local, No/Low Thinking | Structured data, general project management, bookkeeping. |
| **Local Utility** | `qwen3:8b` / `qwen3.5:4b` | Fast Local | Infrastructure checks, status monitoring, simple script execution. |

---

## Routing Scenarios & Invocation

### 1. Automated Invocation (Keyword Based)

The router automatically switches models when it detects specific triggers.

#### Scenario A: Complex Strategy Analysis
**Prompt:** *"Analyze the current volatility of the S&P 500 and evaluate the risk of my current long exposure."*
- **Detected Keywords:** `Analyze`, `evaluate`, `risk`.
- **Route:** `reasoning` $\rightarrow$ `deepseek-v3.1:671b-cloud` (Thinking: Medium).

#### Scenario B: System-Critical Architecture
**Prompt:** *"Perform a deep dive into the network latency between the lab nodes and the broker API; we need a comprehensive plan to reduce jitter."*
- **Detected Keywords:** `deep dive`, `comprehensive`, `plan`.
- **Route:** `ultra-reasoning` $\rightarrow$ `kimi-k2.6:cloud` (Thinking: High).

#### Scenario C: Data Entry / Bookkeeping
**Prompt:** *"Log the trade execution for AAPL at $220.50, 100 shares, filled at 10:01 AM."*
- **Detected Keywords:** `Log`, `trade execution`.
- **Route:** `structured` $\rightarrow$ `gemma4:e4b` (Thinking: Off).

#### Scenario D: Health Check
**Prompt:** *"Check the status of the lab nodes and report connectivity."*
- **Detected Keywords:** `status`, `check`, `report`.
- **Route:** `monitoring` $\rightarrow$ `qwen3.5:4b` (Thinking: Off).

---

## Manual Overrides

If the automated router selects a model that is too lightweight (or too heavy) for your specific need, you can use explicit routing tags.

### Explicit Model Selection
Use the `<!-- model: ... -->` tag to force a specific model.

```html
<!-- model: ollama/kimi-k2.6:cloud thinking: high -->
Refactor the core order execution logic to handle partial fills.
```

### Explicit Route Selection
Use the `<!-- model-route: ... -->` tag to use a predefined route.

```html
<!-- model-route: ultra-reasoning -->
Design the multi-region failover architecture for the trading desk.
```

---

## Domain Routing

Beyond keywords, the router uses **Domain Routing**. If a task is associated with a specific domain folder (e.g., `/bookkeeping`), the router automatically prioritizes models suited for that domain.

- **Market Research** $\rightarrow$ `reasoning`
- **Position Management** $\rightarrow$ `reasoning`
- **Bookkeeping** $\rightarrow$ `structured`
- **Technical Infrastructure** $\rightarrow$ `infrastructure`

## Maintenance & Optimization

To update the routing logic:
1. Edit `~/.pi/model-router.json` to add new keywords or change model assignments.
2. Synchronize the changes with `~/.pi/agent/models.json` to ensure the model IDs are registered.
3. Run `/model-route` in a session to verify the active configuration.
