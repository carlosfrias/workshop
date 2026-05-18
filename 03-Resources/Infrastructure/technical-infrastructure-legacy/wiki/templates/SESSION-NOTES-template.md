# SESSION-NOTES Template with Model Performance Tracking
**Use this template when creating new SESSION-NOTES documents.**

The model performance tracking table allows the meta-orchestration system to learn which models handle which prompt types effectively.

---

## Standard Header

```markdown
# Session Notes — YYYY-MM-DD

**Session:** {Morning | Afternoon | Evening} — brief description
**Focus:** {What was the main goal}
**Status:** {In progress | Complete | Interrupted}
```

---

## Model Performance Tracking Table

For each significant prompt or task during the session, record what model handled it and how it performed:

```markdown
## Model Performance Log

| # | Time | Prompt Type | Model | Node | Tokens In | Tokens Out | Latency | Quality | Cost | Adequate? |
|---|------|-------------|-------|------|-----------|------------|---------|---------|------|-----------|
| 1 | 09:15 | Hardware spec extraction | gemma4:e4b | orchestrator | 1500 | 800 | 4.2s | High | $0 | Yes |
| 2 | 09:22 | Status doc generation | qwen3.5:4b | orchestrator | 200 | 1200 | 1.8s | Medium | $0 | Yes |
| 3 | 09:45 | LVM diagnosis reasoning | kimi-k2.6 | cloud | 3000 | 2500 | 12s | Very High | $0.05 | Yes |
| 4 | 10:10 | Playbook syntax fix | qwen3:8b | fnet3 | 800 | 300 | 2.1s | High | $0 | Yes |
| 5 | 10:15 | Decomposition planning | qwen3.5:397b | cloud | 2500 | 1800 | 8s | High | $0.03 | Yes |
| 6 | 10:30 | Wiki markdown formatting | qwen3.5:4b | orchestrator | 400 | 600 | 0.9s | High | $0 | Yes |
| 7 | 11:00 | Troubleshooting analysis | kimi-k2.6 | cloud | 5000 | 4000 | 15s | Very High | $0.08 | Yes |
```

**Fields:**
- **#:** Sequential number for reference
- **Time:** When the prompt was sent
- **Prompt Type:** Category (extraction, generation, reasoning, debugging, planning, formatting, etc.)
- **Model:** Which model handled it
- **Node:** Where it ran (orchestrator, fnet3, cloud, etc.)
- **Tokens In/Out:** Approximate token counts (from model response metadata if available)
- **Latency:** Wall-clock time from prompt to response
- **Quality:** Subjective rating (Very High, High, Medium, Low)
- **Cost:** Estimated cost ($0 for local, estimated for cloud)
- **Adequate?:** Could a cheaper model have handled this? Yes/No/Maybe

**"Adequate?" is the critical field.** It captures whether we over-spent on model capacity:
- **Yes** — the model used was appropriate for the task
- **No** — a cheaper/faster model could have handled this (e.g., used kimi-k2.6 for a simple formatting task)
- **Maybe** — uncertain, needs further testing with cheaper model

---

## Pattern Analysis (Fill at Session End)

After the session, analyze patterns:

```markdown
## Pattern Analysis

### Prompt Types That Stayed Local (✅ Correct Routing)
| Prompt Type | Model Used | Why It Worked |
|-------------|-----------|---------------|
| Hardware spec extraction | gemma4:e4b | Structured JSON output, deterministic |
| Status doc generation | qwen3.5:4b | Template-based, low complexity |
| Playbook syntax fix | qwen3:8b | Code generation with context |
| Wiki formatting | qwen3.5:4b | Markdown is well-represented in training |

### Prompt Types That Required Cloud (⚠️ Necessary Escalation)
| Prompt Type | Cloud Model | Why Local Failed |
|-------------|-------------|-----------------|
| LVM diagnosis reasoning | kimi-k2.6 | Required understanding systemd mount namespaces + LVM + early-boot services simultaneously |
| Troubleshooting analysis | kimi-k2.6 | Multi-domain reasoning (network + storage + systemd) with no clear answer |
| Decomposition planning | qwen3.5:397b | Needed to design architecture across multiple systems |

### Potential Mis-Routings (❌ Could Have Been Local)
| Prompt Type | Model Used | Should Have Used | Evidence |
|-------------|-----------|-----------------|----------|
| Status doc generation | qwen3.5:4b | qwen3.5:4b | ✅ Actually correct |
| Playbook review | qwen3.5:397b | qwen3:8b | Cloud used but output was simple validation |
```

---

## Cost Summary

```markdown
## Cost Summary

| Category | Count | Est. Cost | Notes |
|----------|-------|-----------|-------|
| Local prompts | 15 | $0 | All tiers (4b, 8b, gemma4) |
| Cloud prompts | 5 | $0.16 | kimi-k2.6 × 3, qwen3.5:397b × 2 |
| **Total** | **20** | **$0.16** | **80% local, 20% cloud** |

**Target for next session:** Reduce cloud to <10% by pre-decomposing hard prompts.
```

---

## Cost Justification and Tiered Model

The performance log enables a data-driven cost model where cloud usage is justified by evidence, not default behavior:

### Tiered Cost Model

| Tier | Model | Cost/Prompt | Justification Trigger | Evidence Required |
|------|-------|-------------|----------------------|-----------------|
| Local Fast | qwen3.5:4b | $0 | Trivial tasks (<500 tokens, single domain) | Consistent success log |
| Local Standard | qwen3:8b / gemma4:e4b | $0 | Standard tasks (1-2 domains, <2000 tokens) | Consistent success log |
| Cloud Standard | qwen3.5:397b | ~$0.005 | Complex tasks (3+ domains, reasoning, planning) | Local model failure log + cloud success |
| Cloud Premium | kimi-k2.6 | ~$0.01-0.05 | Novel cross-domain integration, creative synthesis | Specific justification per prompt |

**Key Principle:** Cloud Premium is not the default for "hard" — it's reserved for prompts where the performance log shows local models *consistently fail* or where the output quality gap between Cloud Standard and Cloud Premium is *material*.

### Justification Tracking

Add this analysis after each session with cloud usage:

```markdown
## Cloud Cost Justification

| Prompt | Cloud Model | Cost | Justification | Would Local Have Succeeded? |
|--------|-------------|------|---------------|----------------------------|
| LVM + systemd mount namespace diagnosis | kimi-k2.6 | $0.05 | 3-domain integration (storage + systemd + boot sequencing), no local model has sufficient context | No — tested qwen3:8b, failed to identify private mount mechanism |
| Ansible vault playbook design | qwen3.5:397b | $0.03 | Multi-step reasoning with security constraints | Maybe — qwen3:8b could handle with decomposition |
| Market regime shift analysis | kimi-k2.6 | $0.08 | Novel pattern recognition across 5 timeframes with backtesting | Unknown — need to test qwen3.5:397b on same prompt |

**Unjustified Cloud Usage This Session:**
| Prompt | Should Have Used | Lost Savings |
|--------|-----------------|--------------|
| Markdown table formatting | qwen3.5:4b | $0.03 |
| JSON structure validation | qwen3.5:4b | $0.02 |

**Total Session Cost:** $0.16
**Justified Cost:** $0.13 (81%)
**Avoidable Cost:** $0.03 (19%)
**Target for Next Session:** <10% avoidable
```

### Adaptive Tier Adjustment

Over time, the evidence base enables dynamic tier changes:

| Month | Finding | Action |
|-------|---------|--------|
| Month 1 | qwen3.5:397b succeeds on 90% of "planning" prompts | Route all planning to Cloud Standard instead of Cloud Premium |
| Month 2 | qwen3.8b handles "Ansible syntax validation" reliably | Downgrade from Cloud Standard to Local Standard |
| Month 3 | kimi-k2.6 still needed for cross-domain integration | Keep Cloud Premium tier, but now with data-backed justification |
| Month 4 | gemma4:e4b matches qwen3.5:397b on "extraction" tasks | Downgrade extraction from Cloud Standard to Local Standard |

This turns the cost model from "expensive default" to "tiered with evidence."

---

## Complete Example

See [SESSION-NOTES-2026-05-01-0915.md](/technical-infrastructure/operational/sessions/SESSION-NOTES-2026-05-01-0915) for a real example without tracking (pre-convention).

The next SESSION-NOTES document should use this template.
