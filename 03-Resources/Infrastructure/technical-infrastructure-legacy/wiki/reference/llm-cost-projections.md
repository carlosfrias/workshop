# LLM Cost Model & Financial Projections

This document outlines the synthetic cost framework used to quantify the operational expense of the AI-orchestrated Trading Desk. While the current infrastructure utilizes an Ollama subscription (effective cost = 0), we maintain a projected cost model to prepare for transitioning to consumption-based pricing.

## Cost Calculation Methodology

Costs are tracked per **1 Million (1M) Tokens**. 

The total cost of a request is calculated as:
$$\text{Total Cost} = (\text{Input Tokens} \times \text{Cost}_{\text{in}}) + (\text{Output Tokens} \times \text{Cost}_{\text{out}}) + (\text{Cache Read} \times \text{Cost}_{\text{cr}}) + (\text{Cache Write} \times \text{Cost}_{\text{cw}})$$

---

## Projected Pricing Tiers

We have categorized models into five cost tiers based on parameter count and cognitive effort. These values are synthetic proxies based on current market rates for frontier models (e.g., GPT-4o, Claude 3.5 Sonnet, DeepSeek V3).

| Tier | Example Model | Cost / 1M In | Cost / 1M Out | Note |
|------|---------------|----------------|-----------------|------|
| **Ultra** | `kimi-k2.6:cloud` | \$10.00 | \$30.00 | High-params, heavy thinking |
| **Reasoning** | `deepseek-v3.1:cloud` | \$5.00 | \$15.00 | Optimized frontier reasoning |
| **Standard Cloud** | `qwen3.5:397b-cloud` | \$2.00 | \$6.00 | General high-capacity |
| **Mid-Tier Cloud** | `gemma4:31b-cloud` | \$3.00 | \$9.00 | Balanced performance |
| **Local** | `gemma4:e4b` | \$0.00 | \$0.00 | Electricity cost baseline |

---

## Financial Projection Scenarios

To project future costs, we analyze the "average prompt profile" for different trading activities.

### Scenario 1: Moderate Research (Daily)
- **Activity:** 10 signal evaluations using `reasoning` tier.
- **Avg Profile:** 5k input tokens / 1k output tokens per request.
- **Daily Projection:** $10 \times (5,000 \times \$0.000005 + 1,000 \times \$0.000015) = \$0.04$ / day.

### Scenario 2: High-Intensity Architecture (Monthly)
- **Activity:** 5 deep-dive system designs using `ultra-reasoning` tier.
- **Avg Profile:** 50k input tokens / 10k output tokens per request.
- **Monthly Projection:** $5 \times (50,000 \times \$0.000010 + 10,000 \times \$0.000030) = \$4.00$ / month.

### Scenario 3: Systematic Bookkeeping (Daily)
- **Activity:** 100 trade logs using `local` tier.
- **Daily Projection:** \$0.00.

## Summary for Budgeting

| Component | Current Cost | Projected Consumption Cost | Risk Level |
|-----------|--------------|----------------------------|------------|
| Local Models | \$0 | \$0 | Low |
| Reasoning Cloud | \$0 | Low to Medium | Medium |
| Ultra Cloud | \$0 | Medium (due to high output tokens) | High |

**Strategic Recommendation:** To minimize future financial impact, maximize the use of `local` models for structured data and utilize `ultra-reasoning` only for mission-critical architectural changes.
