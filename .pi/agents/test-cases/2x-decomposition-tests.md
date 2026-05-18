# 2x Decomposition Test Cases

This document contains test scenarios to validate the 2x decomposition workflow. Each test includes:
- Input task
- Expected decomposer output
- Simulated executor output (with failures)
- Expected verifier report
- Expected intercom exchange

---

## Test Case 1: Valid 2x Decomposition Request

### Scenario: Complex Trade Analysis

**Input Task:**
```
Analyze the following trading signals and execute position sizing:
1. Read the current portfolio state from ./position-management/portfolio.json
2. Read the new signal from ./market-research/signals/2026-04-25-ES.json
3. Calculate optimal position size based on 2% risk rule and current exposure
4. Check if the trade violates any risk limits (sector concentration, notional limits)
5. Output a structured order recommendation with entry, stop, target, and size
```

---

### Expected Decomposer Output

```markdown
## Decomposition Plan

### Overview
Analyze trading signal, calculate position size with risk checks, and produce order recommendation.

### Sub-Tasks

| # | Task | Target Agent | Complexity | Rationale | Expected Output |
|---|------|--------------|------------|-----------|-----------------|
| 1 | Read portfolio.json and extract current positions, total equity, and sector exposure percentages | position-monitor | low | Simple data extraction | JSON with positions, equity, sector breakdown |
| 2 | Read 2026-04-25-ES.json signal file and extract signal direction, entry price, stop price, target price | position-monitor | low | Simple data extraction | JSON with signal fields |
| 3 | Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure | position-management | **high** | Multi-step calculation with conditional logic | JSON with calculated size, risk amount, sector exposure |
| 4 | Check risk limits: sector concentration < 30%, total notional < $500k, position size ≥ minimum order size | position-management | medium | Multiple comparisons, simple boolean logic | JSON with pass/fail for each limit |
| 5 | Combine calculations and risk checks into final order recommendation with all required fields | position-management | **high** | Synthesis of multiple inputs, formatting | Structured order object with entry, stop, target, size, risk_limits_passed |

### Dependencies
- Task 3 depends on Task 1 and Task 2 (needs portfolio + signal data)
- Task 4 depends on Task 3 (needs calculated size)
- Task 5 depends on Task 3 and Task 4 (needs all inputs)

### Verification Criteria

**Task 1:**
- [ ] All positions from portfolio.json are listed
- [ ] Total equity matches sum of positions
- [ ] Sector percentages sum to 100% (or account for cash)

**Task 2:**
- [ ] All signal fields extracted exactly (no modification)
- [ ] Direction is one of: long, short
- [ ] Prices are positive numbers

**Task 3:**
- [ ] Position size formula is correct: (equity × 0.02) / (entry - stop)
- [ ] Risk amount equals position size × (entry - stop)
- [ ] Sector exposure calculation includes new position

**Task 4:**
- [ ] Each risk limit is compared correctly
- [ ] Boolean results are accurate (true = pass, false = violate)

**Task 5:**
- [ ] All required fields present (entry, stop, target, size, risk_limits_passed)
- [ ] Values match outputs from Task 3 and Task 4
- [ ] JSON is valid and parseable

### Complexity Notes

**Task 3 (high):** Combines data extraction from two sources, multi-step calculation, and exposure projection. Watch for:
- Arithmetic errors in position size formula
- Missing sector exposure projection
- Confusion between risk amount and position size

**Task 5 (high):** Synthesizes multiple inputs into structured output. Watch for:
- Field mismatches with previous task outputs
- Missing required fields
- Format drift (wrong JSON structure)
```

---

### Simulated Executor Output (Task 3 - Over-Complex)

```json
{
  "task": "Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure",
  "output": {
    "position_size": 150,
    "risk_amount": 3000,
    "entry": 5200,
    "stop": 5180,
    "equity_used": 780000,
    "sector_exposure": {
      "equity": "28%",
      "new_position": "5%",
      "combined": "33%"
    },
    "notes": "Based on the portfolio equity of around $750k I think, the 2% risk would be about $15k but I'm adjusting for the sector limits. The position size of 150 contracts gives us good exposure. Current sector exposure looks like it's about 28% based on my reading of the portfolio, and adding this position would bring it to maybe 33% which might be over the limit but I'm not sure if the limit is 30% or 35%. Also the stop distance is 20 points so risk per contract is $1000, so 150 contracts is $150k notional which seems reasonable. Wait, let me recalculate: 150 × 20 × $50 = $150,000 risk, that's too high. Actually the equity is $780,000 so 2% is $15,600. So position size should be $15,600 / (20 × $50) = 15.6 contracts. But I said 150 earlier. Let me just use 15 contracts instead. The sector exposure for equity indices is currently around 25-30% and this would add maybe 3-5% more."
  },
  "metadata": {
    "agent": "position-management",
    "model": "ollama/qwen3.5:4b",
    "execution_time_ms": 8420,
    "tokens_used": 1250
  }
}
```

**Failure Analysis:**
- ❌ **Arithmetic errors**: Position size changed mid-output (150 → 15.6 → 15)
- ❌ **Inconsistent values**: equity_used ($780k) doesn't match stated equity (~$750k)
- ❌ **Format drift**: Sector exposure as strings ("28%") instead of numbers (0.28)
- ❌ **Task-switching**: Agent recalculating mid-output, showing uncertainty
- ❌ **Vague hand-waving**: "about 28%", "maybe 33%", "I think", "looks like"
- ❌ **Missing fields**: No clear risk_amount calculation, no definitive answer

---

### Expected Verifier Report (with 2x Decomposition Request)

```markdown
## Verification Report

### Task
Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure

### Agent
position-management (ollama/qwen3.5:4b)

### Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| Position size formula correct | ❌ Fail | Agent changed answer 3 times: 150 → 15.6 → 15 contracts. Final value unclear. |
| Risk amount calculation | ❌ Fail | Stated "$150,000 risk" then "$15,600 risk" — contradictory within same output |
| Sector exposure as numbers | ❌ Fail | Used strings ("28%") instead of decimals (0.28) as required by format |
| Sector exposure projection | ⚠️ Partial | Provided estimate but with uncertainty ("maybe 33%", "about 28%") |
| JSON validity | ✅ Pass | Structure is valid, but values are unreliable |
| Single definitive answer | ❌ Fail | Output shows mid-stream recalculation and uncertainty |

### Overall Result
**FAIL** — Output has multiple independent errors and shows evidence of task-overload

---

### Complexity Analysis

**Failure Mode Count:** 5 independent failures
1. Arithmetic inconsistency (position size changed 3x)
2. Contradictory risk amounts
3. Format drift (strings vs numbers)
4. Vague estimates instead of precise calculations
5. Task-switching mid-output (agent rethinking approach mid-turn)

**Evidence of Task-Switching:**
> "Wait, let me recalculate... Actually the equity is $780,000 so 2% is $15,600. So position size should be... But I said 150 earlier. Let me just use 15 contracts instead."

This shows the agent attempting extraction + calculation + validation all in one turn, then realizing errors and trying to correct mid-stream.

**Suggested Split:**
```
Original: "Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure"

Proposed Sub-Task 3a: "Extract equity amount and current sector exposure percentages from Task 1 output. Output as JSON with numeric values (not strings)."

Proposed Sub-Task 3b: "Calculate position size using formula: (equity × 0.02) / (entry - stop). Use exact values from Task 2 (entry, stop) and Task 3a (equity). Show calculation steps. Output: position_size, risk_amount, risk_per_contract."

Proposed Sub-Task 3c: "Calculate projected sector exposure: current_exposure + (position_notional / total_equity). Use outputs from 3a and 3b. Output: current_percent, new_position_percent, combined_percent as decimals."
```

**Rationale:** The original task combines data extraction, multi-step arithmetic, and projection logic. Splitting into 3 atomic steps ensures each calculation uses verified inputs and produces a single definitive answer.

---

### Recommended Action
⚠️ **Request 2x decomposition** — This sub-task appears too complex for single-turn execution. See complexity analysis above.

**Status:** PENDING — Awaiting orchestrator decision via intercom
```

---

### Expected Intercom Exchange

**Verifier → Orchestrator:**
```typescript
intercom({
  action: "ask",
  to: "orchestrator",
  message: `⚠️ Request 2x Decomposition

**Sub-Task:** "Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure"

**Verification Failures:**
- [Failure 1]: Arithmetic inconsistency — position size changed 3x (150 → 15.6 → 15)
- [Failure 2]: Contradictory risk amounts ($150k vs $15.6k)
- [Failure 3]: Format drift — used strings ("28%") instead of decimals (0.28)
- [Failure 4]: Vague estimates ("maybe 33%", "about 28%")
- [Failure 5]: Task-switching mid-output (agent recalculating mid-turn)

**Evidence of Over-Complexity:**
> "Wait, let me recalculate... Actually the equity is $780,000 so 2% is $15,600. So position size should be... But I said 150 earlier. Let me just use 15 contracts instead."

**Proposed Split:**
- Sub-Task 3a: Extract equity and sector exposure as numeric values
- Sub-Task 3b: Calculate position size with formula (equity × 0.02) / (entry - stop)
- Sub-Task 3c: Calculate projected sector exposure

**Question:** Should I proceed with "Re-run with cloud model" or will you re-decompose this sub-task?`
})
```

**Orchestrator → Verifier (Response):**
```typescript
intercom({
  action: "reply",
  replyTo: "msg_abc123",
  message: `✅ **Agree to 2x decomposition**

Your proposed split is appropriate. This is clearly a complexity issue, not a knowledge gap.

**Action:** I'm launching a refined decomposition with tasks 3a, 3b, 3c as you proposed.

**New Chain Run:** decomposed-trade-to-log (refined)
**Decomposition ID:** 2026-04-25-002-refined

Please mark your current report as PENDING and await the refined chain output.`
})
```

---

### Expected Final Verifier Report (After Re-decomposition)

```markdown
## Verification Report (Updated)

### Task
Calculate position size using 2% risk rule: (equity × 0.02) / (entry - stop). Also calculate current sector exposure + new position exposure

### Agent
position-management (ollama/qwen3.5:4b)

### Status
**PENDING → RESOLVED**

### Intercom Resolution
Orchestrator approved 2x decomposition on 2026-04-25 14:32:00 EST.

**New Sub-Tasks:**
- 3a: Extract equity and sector exposure (EXECUTING)
- 3b: Calculate position size (QUEUED)
- 3c: Calculate projected exposure (QUEUED)

### Recommended Action
Await refined chain completion. Original verification report voided.

---

**Note:** This sub-task will be re-verified after 3a/3b/3c complete. Expected improvement: 3 independent atomic calculations instead of 1 complex multi-step operation.
```

---

## Test Case 2: Invalid 2x Request (Should Decline)

### Scenario: Simple Format Error

**Input Task:**
```
Ping 8.8.8.8 and report success/failure as JSON with fields: success, latency_ms, raw_output
```

### Simulated Executor Output
```json
{
  "task": "Ping 8.8.8.8 and report success/failure",
  "output": {
    "success": "true",
    "latency": 15.2,
    "output": "PING 8.8.8.8... 3 packets transmitted, 3 received"
  }
}
```

### Expected Verifier Report
```markdown
## Verification Report

### Task
Ping 8.8.8.8 and report success/failure as JSON

### Agent
position-monitor (ollama/qwen3.5:4b)

### Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| success field is boolean | ❌ Fail | Used string "true" instead of boolean true |
| latency_ms field present | ❌ Fail | Used "latency" instead of "latency_ms" |
| raw_output field present | ❌ Fail | Used "output" instead of "raw_output" |
| Ping executed correctly | ✅ Pass | Command ran successfully |

### Overall Result
**FAIL** — Format drift on field names and types

---

### Complexity Analysis
**Failure Mode Count:** 3 failures, but ALL are format drift (same root cause)

**Evidence of Task-Switching:** None — task is atomic (single operation)

**Assessment:** This is a simple format compliance issue, not over-complexity. The agent executed the ping correctly but didn't follow the exact schema.

### Recommended Action
**Re-run with cloud model** — Do NOT request 2x decomposition. This sub-task is already atomic; the failure is instruction-following, not complexity.
```

---

## Test Case 3: Boundary Case (Medium Complexity)

### Scenario: Calculation with Single Failure Mode

**Input Task:**
```
Calculate total P&L for all open positions: sum(position_size × unrealized_pnl_per_contract) for each position
```

### Simulated Executor Output
```json
{
  "task": "Calculate total P&L",
  "output": {
    "positions": [
      {"symbol": "ES", "size": 5, "pnl_per_contract": 250.50},
      {"symbol": "NQ", "size": 3, "pnl_per_contract": 412.75},
      {"symbol": "CL", "size": 10, "pnl_per_contract": -125.00}
    ],
    "total_pnl": 3751.25,
    "calculation": "5×250.50 + 3×412.75 + 10×(-125.00) = 1252.50 + 1238.25 - 1250.00 = 1240.75"
  }
}
```

### Expected Verifier Report
```markdown
## Verification Report

### Task
Calculate total P&L for all open positions

### Agent
position-monitor (ollama/qwen3.5:4b)

### Checks

| Criterion | Status | Notes |
|-----------|--------|-------|
| All positions included | ✅ Pass | 3 positions match portfolio |
| Multiplication correct per position | ✅ Pass | ES: 1252.50 ✓, NQ: 1238.25 ✓, CL: -1250.00 ✓ |
| Summation correct | ❌ Fail | Shows 1240.75 in calculation but 3751.25 in total_pnl field |
| JSON validity | ✅ Pass | Structure is valid |

### Overall Result
**FAIL** — Arithmetic error in final summation

---

### Complexity Analysis
**Failure Mode Count:** 1 failure (arithmetic error in final step)

**Evidence of Task-Switching:** None — agent followed correct steps, made single calculation error

**Assessment:** This is a simple arithmetic mistake, not over-complexity. The agent correctly structured the calculation but botched the final addition.

### Recommended Action
**Re-run with cloud model** — Do NOT request 2x decomposition. Task is atomic; failure is computational accuracy, not complexity.
```

---

## Running the Tests

### Test Execution Plan

1. **Test Case 1 (Valid 2x Request)**
   - Command: Run decomposed-trade-to-log.chain with the complex trade analysis task
   - Expected: Verifier requests 2x decomposition, orchestrator agrees, chain re-runs with refined plan
   - Success Criteria: Refined sub-tasks (3a, 3b, 3c) all pass verification

2. **Test Case 2 (Invalid 2x Request)**
   - Command: Run monitor-to-log.chain with simple ping task, manually inject format errors
   - Expected: Verifier recommends "cloud re-run" without intercom request
   - Success Criteria: No 2x decomposition requested

3. **Test Case 3 (Boundary Case)**
   - Command: Run position-monitor with P&L calculation, manually inject arithmetic error
   - Expected: Verifier recommends "cloud re-run" without intercom request
   - Success Criteria: Single failure mode correctly identified as non-complexity issue

### Metrics to Collect

| Metric | Target | Measurement |
|--------|--------|-------------|
| 2x request accuracy | >80% | % of 2x requests that orchestrator approves |
| Post-split success rate | >90% | % of split sub-tasks passing verification |
| False positive rate | <10% | % of 2x requests that should have been simple re-runs |
| Time overhead | <5 min | Avg time for intercom + re-decomposition loop |

---

## Test Commands

```bash
# Test Case 1: Complex trade analysis (expect 2x decomposition)
/chain decomposed-trade-to-log "Analyze the following trading signals and execute position sizing: [full task from Test Case 1]"

# Test Case 2: Simple ping (expect no 2x request)
# Note: This requires manually injecting format errors in executor output for testing

# Test Case 3: P&L calculation (expect no 2x request)
# Note: This requires manually injecting arithmetic error for testing
```

### Manual Testing Notes

For Test Cases 2 and 3, you'll need to either:
1. **Mock the executor output** — Temporarily modify the chain to use hardcoded failing output
2. **Natural failure** — Run the chain and hope the local model makes the expected errors (unreliable)
3. **Adversarial testing** — Manually edit the executor's output file before verifier runs

Recommended approach: Create test fixtures with known outputs and run verifier directly against them.
