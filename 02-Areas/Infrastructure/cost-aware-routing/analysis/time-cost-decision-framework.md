
# Time-Cost Decision Framework

**Assumptions:**
- Your hourly rate: $100/hr
- Cloud Premium (kimi-k2.6): $0.05/1K tokens
- Local Standard (qwen3:8b): $0.006/1K tokens
- Premium difference: $0.044000000000000004/1K tokens

---

## Quick Decision Card

| Scenario | Time Pressure | Recommended Model | Rationale |
|----------|--------------|-------------------|-----------|
| **URGENT** | < 5 min deadline | Cloud Premium | Time cost >> monetary savings |
| **IMPORTANT** | < 1 hr deadline | Cloud Standard | Balance of speed and cost |
| **ANALYTICAL** | Complex reasoning | Large Local or Cloud Std | Quality over speed |
| **BUDGET** | <$1/day limit | Small Local | Monetary cost priority |
| **PRIVATE** | Sensitive data | Local Only | Privacy over all else |

---

## Break-Even Analysis

When does waiting for local cost more than cloud premium?

| Tokens | Cloud Premium Cost | Break-Even Wait Time |
|--------|-------------------|---------------------|
| 1,000 | $0.0440 | 1.6 sec (0.03 min) |
| 5,000 | $0.2200 | 7.9 sec (0.13 min) |
| 10,000 | $0.4400 | 15.8 sec (0.26 min) |
| 50,000 | $2.2000 | 79.2 sec (1.32 min) |
| 100,000 | $4.4000 | 158.4 sec (2.64 min) |

---

## Rules of Thumb

1. **If response > 16 sec** (for 10K tokens)
   → Cloud is cheaper when counting your time

2. **If iteration count > 2**
   → Cloud pays off (fewer retries needed)

3. **If deadline < 5 minutes**
   → Always use cloud

4. **If data is sensitive**
   → Always use local (compliance > cost)

---

*Generated: 2026-05-26 11:14*
