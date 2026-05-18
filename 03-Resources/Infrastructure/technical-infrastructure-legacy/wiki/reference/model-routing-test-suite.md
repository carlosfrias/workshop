# Model Routing Verification Suite

This suite is designed to verify that the `pi-model-router` is correctly dispatching prompts to the appropriate model tiers based on keywords and domains.

## Verification Protocol
For each test case below:
1. Enter the **Probe Prompt** into the pi session.
2. Immediately run the command `/model-route`.
3. Verify that the **Expected Route** and **Expected Model** match the actual decision shown in the routing status output.

---

## Test Cases

### 1. Ultra-Reasoning Tier (High Capacity)
*Goal: Trigger the 1T+ parameter model for mission-critical logic.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "I need a **comprehensive** and **thorough** architectural **deep dive** into the trading desk's failover logic." | `ultra-reasoning` | `kimi-k2.6:cloud` | `comprehensive`, `deep dive` |
| "This is a **mission-critical** update; **think deeply** about the potential for race conditions." | `ultra-reasoning` | `kimi-k2.6:cloud` | `mission-critical`, `think deeply` |

### 2. Reasoning Tier (Mid-High Capacity)
*Goal: Trigger the 600B+ parameter model for strategic analysis.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "**Analyze** the correlation between the current signal and the 200-day moving average." | `reasoning` | `deepseek-v3.1:671b-cloud` | `analyze` |
| "**Evaluate** the risk of the current portfolio allocation and **recommend** a hedge." | `reasoning` | `deepseek-v3.1:671b-cloud` | `evaluate`, `recommend` |
| "**Decompose** the task of implementing a new broker API integration into sub-tasks." | `reasoning` | `deepseek-v3.1:671b-cloud` | `decompose` |

### 3. Cloud-Standard Tier (High Capacity)
*Goal: Trigger the 300B+ parameter model for general high-quality drafting.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "Please **summarize** the key findings of the latest market research report." | `cloud-standard` | `qwen3.5:397b-cloud` | `summarize` |
| "Provide a general **overview** of how the order execution pipeline works." | `cloud-standard` | `qwen3.5:397b-cloud` | `overview` |

### 4. Structured Tier (Local Flagship)
*Goal: Trigger the local model for data-heavy, non-reasoning tasks.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "**Log** the following trade: AAPL, 100 shares, Buy, $220.50." | `structured` | `gemma4:e4b` | `log` |
| "**Reconcile** the balance between the broker statement and the internal ledger." | `structured` | `gemma4:e4b` | `reconcile` |

### 5. Monitoring Tier (Local Utility)
*Goal: Trigger the fast, lightweight model for health checks.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "**Check** the **status** of the lab nodes and **report** any offline servers." | `monitoring` | `qwen3.5:4b` | `status`, `check` |
| "What is the current **health** and **latency** of the API connection?" | `monitoring` | `qwen3.5:4b` | `health`, `latency` |

### 6. Infrastructure Tier (Local Utility)
*Goal: Trigger the model suited for server operations.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "**Troubleshoot** the SSH connectivity issue on fnet2." | `infrastructure` | `qwen3:8b` | `troubleshoot` |
| "**Deploy** the new version of the model router to all lab nodes." | `infrastructure` | `qwen3:8b` | `deploy` |

### 7. Default Route (Fallback)
*Goal: Verify the fallback when no keywords match.*

| Probe Prompt | Expected Route | Expected Model | Trigger Keyword |
| :--- | :--- | :--- | :--- |
| "Hello, how are you doing today?" | `(default)` | `gemma4:e4b` | N/A |

---

## Troubleshooting Routing Failures

If a prompt routes to the wrong model:
1. **Keyword Overlap:** Check if a higher-priority route (higher `priority` value in `model-router.json`) contains a keyword that also appears in the prompt.
2. **Domain Conflict:** Check if the current session is in a domain folder (e.g., `/bookkeeping`) which might be forcing a specific route regardless of keywords.
3. **Manual Override:** Verify that no `<!-- model-route: ... -->` tags are present in the prompt.
