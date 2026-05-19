# High-Frequency Decomposition Detection

**Template ID:** COMP-004  
**Extracted from:** `1-PLAN.md` Section "High-Frequency Decomposition Detection"  
**Use in:** Any plan that decomposes work across model tiers and wants to detect excessive decomposition rates.

---

The **medium cloud model** (`{{MEDIUM_CLOUD_MODEL}}`) and the **low cloud model** (`{{LOW_CLOUD_MODEL}}`) collaborate to detect and respond to excessive decomposition rates. The medium cloud focuses on **analysis and recommendation**; the low cloud focuses on **action**.

## Roles

| Model | Role | Executes Code? |
|-------|------|---------------|
| **Medium Cloud** (`{{MEDIUM_CLOUD_MODEL}}`) | Analyzes decomposition trends, produces deeper decomposition plans, signals Low Cloud | **NO** |
| **Low Cloud** (`{{LOW_CLOUD_MODEL}}`) | Receives signal, engages deeper decomposition, logs metrics, reports to user | **YES** (action only) |

## Detection Protocol

1. **Low cloud collects metrics** — Every task assignment and decomposition event is timestamped in session notes.
2. **Medium cloud reads session notes** at {{CHECK_INTERVAL}}-minute intervals and calculates the ratio:
   ```
   {{RATIO_FORMULA}}
   ```
3. **Threshold table:**

| Ratio | Window | Action | Owner |
|-------|--------|--------|-------|
| > {{HIGH_THRESHOLD}} | Rolling {{WINDOW_MINUTES}} min | Medium Cloud signals Low Cloud → high-frequency mode | Medium Cloud |
| {{MONITOR_LOW}}–{{MONITOR_HIGH}} | Rolling {{WINDOW_MINUTES}} min | Monitor only, no action | Low Cloud |
| < {{EXIT_THRESHOLD}} | Two consecutive windows | Exit high-frequency mode, resume {{DECOMP_MULTIPLIER}}x | Low Cloud |

4. **Medium Cloud produces deeper decomposition** — When ratio > {{HIGH_THRESHOLD}}, the medium cloud re-examines pending and incoming steps from the High Cloud and produces **{{DEEP_DECOMP_FACTOR}} finer decomposition plans**. These plans are passed to the Low Cloud as replacement step definitions.
5. **Medium Cloud escalates to High Cloud** — If the ratio stays > {{HIGH_THRESHOLD}} for > {{ESCALATION_MINUTES}} consecutive minutes, the medium cloud reports to the High Cloud that the initial decomposition granularity may be systematically too coarse.

## High-Frequency Mode Behavior (Low Cloud)

When the Low Cloud receives a high-frequency signal from the Medium Cloud:

1. **Adopt deeper decomposition plans** from Medium Cloud ({{DEEP_DECOMP_FACTOR}} instead of {{DECOMP_MULTIPLIER}}x).
2. **Finer model matching** — assign simplest fragments to low local; reserve medium/high local for only the most complex pieces.
3. **Alert in next health report** — flag the condition and which step_ids triggered it.
4. **Log the signal** — record timestamp, ratio, and medium cloud recommendation in session notes.

For the full detection and reporting protocol, see [`{{AGENTS_MD_PATH}}`](./{{AGENTS_MD_PATH}}).

---

## Placeholder Reference

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{MEDIUM_CLOUD_MODEL}}` | Cloud model for analysis | `ollama/deepseek-v4-pro` |
| `{{LOW_CLOUD_MODEL}}` | Cloud model for orchestration | `ollama/qwen3.5:397b` |
| `{{CHECK_INTERVAL}}` | Minutes between ratio checks | `10` |
| `{{RATIO_FORMULA}}` | How to calculate decomposition ratio | `ratio = (tasks_decomposed in last 10 min) / (total_tasks_assigned in last 10 min)` |
| `{{HIGH_THRESHOLD}}` | Threshold for high-frequency mode | `60%` |
| `{{MONITOR_LOW}}` | Low end of monitor-only band | `40%` |
| `{{MONITOR_HIGH}}` | High end of monitor-only band | `60%` |
| `{{EXIT_THRESHOLD}}` | Threshold to exit high-frequency mode | `40%` |
| `{{WINDOW_MINUTES}}` | Rolling window for ratio calculation | `10` |
| `{{ESCALATION_MINUTES}}` | Minutes before escalating to High Cloud | `20` |
| `{{DECOMP_MULTIPLIER}}` | Standard decomposition multiplier | `2` |
| `{{DEEP_DECOMP_FACTOR}}` | Deeper decomposition factor | `3x–4x` |
| `{{AGENTS_MD_PATH}}` | Path to full protocol | `AGENTS.md` |
