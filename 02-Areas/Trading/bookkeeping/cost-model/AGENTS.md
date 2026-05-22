# cost-model — AI Inference Cost Tracking

Track AI model usage costs in a separate Beancount ledger (`ai-cost-model.beancount`), distinct from the brokerage ledger. Covers cloud API spend, local model electricity+hardware amortization, quality-adjusted costs, and routing efficiency savings. Sub-domain of `../AGENTS.md` (Bookkeeping).

## [S-TIGHT]

Separate Beancount ledger `ledger/ai-cost-model.beancount` for AI inference costs. Cloud models tracked as actual API spend. Local models tracked as derived cost (electricity + hardware depreciation). Token tracking via `TOKENS` commodity.

## Account Structure

### Cloud API Spend (Actual)
- `Expenses:AI:Compute:Cloud:Anthropic` — Anthropic API costs
- `Expenses:AI:Compute:Cloud:OpenAI` — OpenAI API costs
- `Expenses:AI:Compute:Cloud:Ollama-Cloud` — Ollama cloud endpoints

### Local Model Derived Costs
- `Expenses:AI:Compute:Local:Electricity` — Electricity for GPU/CPU
- `Expenses:AI:Compute:Local:Hardware-Depreciation` — Hardware amortization

### Quality-Adjusted Costs
- `Expenses:AI:Quality-Adjusted:Code-Generation` — Cost/quality for code tasks
- `Expenses:AI:Quality-Adjusted:Analysis` — Cost/quality for analysis tasks
- `Expenses:AI:Quality-Adjusted:Monitoring` — Cost/quality for monitoring tasks

### Routing Efficiency
- `Income:AI:Routing-Savings` — Cost saved by routing to optimal tier

### Budget Tracking
- `Assets:AI:Budget` — Allocated budget
- `Liabilities:AI:Overage` — Budget overage tracking

## Token Pricing

| Model | Venue | Price per 1K tokens |
|-------|-------|---------------------|
| qwen3.5:4b | local | $0.005 |
| qwen3:8b | local | $0.006 |
| gemma4:e4b | local | $0.005 |
| gemma4:31b-cloud | cloud | $0.015 |
| kimi-k2.6:cloud | cloud | $0.050 |

## Rules

### Must Always
- Track ALL models — local at $0.00 cash cost still contribute derived costs
- Record per-session cost estimates in session journal
- Use `~` prefix for estimated token/cost figures
- Distinguish actual cloud spend from derived local costs

### Must Never
- Mix AI cost tracking with brokerage ledger — separate `.beancount` files
- Fabricate cost data — mark as "not tracked" if unsure
- Skip recording zero-cost sessions (local-only runs) — they matter for utilization

## Session Close Integration

When `close session` is invoked:
1. Estimate per-model token usage and cost
2. Write cost to session journal
3. Update `costs/AI-MODEL-COSTS.md` (vault side)

## Cost Thresholds

| Threshold | Action |
|-----------|--------|
| $0.00 (local only) | Note as zero-cost |
| < $0.05 | Routine |
| $0.05–$0.25 | Flag in session note |
| $0.25–$1.00 | Review routing |
| > $1.00 | Escalate — consider decomposition or local models |

## Key Files

| File | Purpose |
|------|---------|
| `ledger/ai-cost-model.beancount` | AI cost ledger (72 lines) |
| `ledger/combined.beancount` | Merges all ledgers for unified Fava view |
