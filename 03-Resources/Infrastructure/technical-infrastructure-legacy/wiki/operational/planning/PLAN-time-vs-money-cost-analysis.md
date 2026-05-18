# PLAN: Time Cost vs. Monetary Cost Analysis

**Created:** 2026-05-03  
**Priority:** 🟡 Medium  
**Estimated Effort:** 6-10 hours  
**Domain:** llm-economics / decision-frameworks  

---

## Objective

Analyze when time cost becomes greater than monetary cost for LLM usage, creating a decision framework for model selection based on urgency, quality, and budget constraints.

---

## Phase 1: Define Time Cost Metrics (2-3 hours)

### Tasks
1. **Identify time cost components**

| Component | Description | Measurement |
|-----------|-------------|-------------|
| **Wait Time** | Time from prompt to response | Seconds/minutes |
| **Iteration Cycles** | Number of retries needed | Count per task |
| **Productivity Impact** | User time lost waiting | Minutes × hourly rate |
| **Opportunity Cost** | Value of delayed decisions | $ per hour of delay |
| **Context Switching** | Mental overhead from delays | Subjective rating 1-5 |

2. **Create time cost formula**
   ```
   Time Cost = (Wait Time + Iterations × Retry Time) × User Hourly Rate
              + Opportunity Cost + Context Switching Penalty
   ```

3. **Define user hourly rates**
   - Developer: $75-150/hour
   - Analyst: $50-100/hour
   - Executive: $200-500/hour
   - Hobbyist: $0-25/hour (opportunity cost only)

4. **Measure baseline latencies**
   - Small local models: 3-6 tokens/sec
   - Large local models: 2-4 tokens/sec
   - Cloud models: 50-100 tokens/sec
   - Include network latency for cloud

### Deliverables
- [ ] Time cost component definitions
- [ ] Time cost calculation formula
- [ ] User rate card
- [ ] Latency benchmark data

### Success Criteria
- Time cost can be calculated for any task
- Formula accounts for all major factors

---

## Phase 2: Define Monetary Cost Metrics (1-2 hours)

### Tasks
1. **Catalog monetary costs**

| Cost Type | Small Local | Large Local | Cloud Standard | Cloud Premium |
|-----------|-------------|-------------|----------------|---------------|
| **Per 1K Tokens** | $0.003 | $0.004 | $0.010 | $0.050 |
| **Per Task (avg)** | $0.015 | $0.020 | $0.050 | $0.250 |
| **Monthly Fixed** | $50 (electricity) | $50 | $0 | $0 |
| **Infrastructure** | $500-800/node | $500-800/node | $0 | $0 |

2. **Create monetary cost formula**
   ```
   Monetary Cost = (Input Tokens × Input Rate) + (Output Tokens × Output Rate)
                   + Fixed Costs (amortized) + Infrastructure (amortized)
   ```

3. **Build cost calculator**
   ```python
   def calculate_monetary_cost(model_id, input_tokens, output_tokens):
       rates = {
           'qwen3.5:4b': {'input': 0.003, 'output': 0.003},
           'qwen3:8b': {'input': 0.004, 'output': 0.004},
           'kimi-k2.6:cloud': {'input': 0.010, 'output': 0.030},
           # ... etc
       }
       rate = rates[model_id]
       return (input_tokens * rate['input'] + output_tokens * rate['output']) / 1000
   ```

4. **Validate with real usage data**
   - Pull actual token counts from performance logs
   - Compare calculated vs. actual costs
   - Adjust rates if needed

### Deliverables
- [ ] Monetary cost catalog
- [ ] Cost calculation formula
- [ ] Cost calculator tool
- [ ] Validation results

### Success Criteria
- Monetary cost can be calculated for any task
- Calculated costs match actual costs within 10%

---

## Phase 3: Break-Even Analysis Model (2-3 hours)

### Tasks
1. **Define break-even scenarios**

| Scenario | Time Sensitivity | Quality Requirement | Budget Constraint |
|----------|-----------------|---------------------|-------------------|
| **Urgent + Critical** | Minutes matter | Must be correct | Secondary |
| **Urgent + Routine** | Minutes matter | Good enough | Secondary |
| **Non-Urgent + Critical** | Hours/days OK | Must be correct | Secondary |
| **Non-Urgent + Routine** | Hours/days OK | Good enough | Primary |

2. **Create break-even calculator**
   ```python
   def break_even_analysis(task_urgency, quality_requirement, budget):
       # Calculate total cost for each model option
       options = []
       for model in available_models:
           time_cost = calculate_time_cost(model, task_urgency)
           monetary_cost = calculate_monetary_cost(model)
           total_cost = time_cost + monetary_cost
           quality_score = get_quality_score(model, quality_requirement)
           
           if quality_score >= quality_requirement:
               options.append({
                   'model': model,
                   'total_cost': total_cost,
                   'time_cost': time_cost,
                   'monetary_cost': monetary_cost
               })
       
       return min(options, key=lambda x: x['total_cost'])
   ```

3. **Generate break-even curves**
   - X-axis: Time sensitivity (minutes to hours)
   - Y-axis: Total cost (time + monetary)
   - Lines for each model option
   - Identify crossover points

4. **Validate with historical data**
   - Pull past tasks from logs
   - Calculate what optimal choice would have been
   - Compare with actual choice made
   - Measure cost of suboptimal decisions

### Deliverables
- [ ] Break-even scenarios
- [ ] Break-even calculator
- [ ] Break-even curve visualizations
- [ ] Historical validation results

### Success Criteria
- Break-even point clearly identified for each scenario
- Calculator recommends optimal model 80%+ of time

---

## Phase 4: Scenario Testing (2-3 hours)

### Tasks
1. **Design test scenarios**

| Scenario | Description | Expected Optimal Choice |
|----------|-------------|------------------------|
| **Emergency Debug** | Production down, need answer NOW | Cloud premium (fastest) |
| **Code Review** | Review PR, 30 min deadline | Cloud standard (fast + accurate) |
| **Research Task** | Explore topic, no deadline | Small local (cheap) |
| **Draft Writing** | First draft of document | Small local with CoT |
| **Data Analysis** | Complex analysis, 2 hr deadline | Large local or cloud standard |

2. **Run scenario tests**
   - Execute each scenario with different models
   - Measure time cost, monetary cost, quality
   - Calculate total cost for each option
   - Verify optimal choice matches prediction

3. **Sensitivity analysis**
   - What if user hourly rate doubles?
   - What if cloud prices drop 50%?
   - What if task requires 10 iterations?
   - What if deadline moves up by 1 hour?

4. **Document edge cases**
   - When does cheapest become most expensive?
   - When does fastest become slowest (due to iterations)?
   - What scenarios have no clear optimal choice?

### Deliverables
- [ ] Test scenario suite
- [ ] Scenario test results
- [ ] Sensitivity analysis
- [ ] Edge case documentation

### Success Criteria
- All scenarios tested with multiple models
- Optimal choice validated empirically
- Sensitivity analysis reveals key decision factors

---

## Phase 5: Decision Framework (1-2 hours)

### Tasks
1. **Create decision tree**
   ```
   Start
   │
   ├─ Is deadline < 5 minutes?
   │  ├─ Yes → Cloud Premium (kimi-k2.6:cloud)
   │  └─ No → Continue
   │
   ├─ Is accuracy critical (cost of error > $1000)?
   │  ├─ Yes → Cloud Standard + Verification
   │  └─ No → Continue
   │
   ├─ Is task simple (classification, extraction)?
   │  ├─ Yes → Small Local (qwen3.5:4b)
   │  └─ No → Continue
   │
   ├─ Is budget constrained (< $1/day)?
   │  ├─ Yes → Small Local with CoT
   │  └─ No → Large Local or Cloud Standard
   ```

2. **Build interactive decision tool**
   ```python
   def recommend_model(task_description, deadline_minutes, accuracy_critical, budget_per_day):
       # Ask clarifying questions
       # Calculate scores for each model
       # Return recommendation with rationale
       pass
   ```

3. **Create quick reference card**
   ```
   Quick Decision Guide:
   
   🚨 URGENT (< 5 min) → Cloud Premium
   ⚠️  IMPORTANT (< 1 hr) → Cloud Standard
   📊 ANALYTICAL (complex) → Large Local or Cloud Standard
   💰 BUDGET (< $1/day) → Small Local
   🔒 PRIVATE (sensitive data) → Local Only
   ```

4. **Integrate with keyword router**
   - Add decision logic to routing system
   - Auto-select model based on task characteristics
   - Allow user override with feedback loop

### Deliverables
- [ ] Decision tree diagram
- [ ] Interactive decision tool
- [ ] Quick reference card
- [ ] Router integration plan

### Success Criteria
- Decision framework is easy to use
- Recommendations match break-even analysis
- Router integration reduces manual decisions by 80%+

---

## Success Metrics

- [ ] Time cost formula validated with real usage data
- [ ] Break-even analysis accurate within 10%
- [ ] Decision framework recommends optimal model 80%+ of time
- [ ] Interactive tool completes recommendation in <30 seconds
- [ ] Quick reference card fits on single page

---

## Notes

- Time cost is highly individual — customize user hourly rate
- Urgency often overrides cost considerations
- Quality requirements may eliminate cheaper options
- Revisit analysis quarterly as models and prices change

---

**END OF PLAN**
