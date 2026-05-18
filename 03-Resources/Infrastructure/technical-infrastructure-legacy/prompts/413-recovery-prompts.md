# Prompt Templates: Autonomous 413 Recovery

## Prompt 1: Decompose Oversized Task
**Use when:** A task exceeds context limits and needs to be split into smaller sub-tasks.
**File:** `technical-infrastructure/prompts/413-decompose-oversized.md`

```markdown
# Decompose Oversized Task

You are an expert task decomposition engine. A task has exceeded the context window 
of available models and must be split into smaller, independently executable chunks.

## Original Task
{task_description}

## Constraints
- Each sub-task must fit within {max_tokens} tokens (input + output)
- Sub-tasks must be independently executable (can run in parallel)
- Each sub-task must produce a result that can be synthesized
- Preserve all requirements from the original task
- Do not lose information during splitting

## Output Format
Return a JSON array of sub-tasks:
```json
[
  {
    "id": "chunk-1",
    "description": "Clear description of this sub-task",
    "type": "partial",
    "estimated_tokens_in": 500,
    "estimated_tokens_out": 1500,
    "input_data": "What data this chunk receives",
    "output_data": "What this chunk produces",
    "required_capabilities": ["reasoning", "coding"],
    "priority": 1
  }
]
```

## Rules
1. Each chunk must be < {max_tokens} tokens total
2. Chunks should have logical boundaries (don't split mid-sentence or mid-function)
3. If the task is sequential, number chunks and specify dependencies
4. If the task is parallel, specify that chunks are independent
5. Include a final "synthesis" chunk that combines all outputs
```

---

## Prompt 2: Recovery Decision Analysis
**Use when:** The system needs to decide which recovery strategy to apply.
**File:** `technical-infrastructure/prompts/413-recovery-decision.md`

```markdown
# Recovery Decision Analysis

You are an infrastructure orchestration advisor. A task has failed with a 413 
"Request Entity Too Large" error. Analyze the situation and recommend the best recovery.

## Error Details
- Failed node: {node}
- Failed model: {model}
- Estimated tokens: {tokens}
- Model context limit: {context_limit}
- Required capabilities: {capabilities}
- Attempt number: {attempt}

## Available Recovery Options

### Option 1: Same-Node Upgrade
- Upgrade to larger model on same node
- Available: {same_node_options}
- Cost: Local only
- Latency: ~3-6s

### Option 2: Cross-Node Same Model
- Same model on different node
- Available nodes: {cross_node_options}
- Cost: Local only
- Latency: +network transfer

### Option 3: Cross-Node Upgrade
- Larger model on different node
- Available: {cross_node_upgrade_options}
- Cost: Local only
- Latency: ~3-6s

### Option 4: Cloud Escalation
- Cloud model with larger context
- Available: {cloud_options}
- Cost: ~${cost} per call
- Latency: ~5-15s

### Option 5: Chunking
- Split task into smaller pieces
- Estimated chunks: {num_chunks}
- Cost: Local × chunks
- Latency: ~{chunk_latency}s per chunk

### Option 6: Truncation
- Hard truncate to fit context
- Warning: May lose information
- Cost: Local only
- Latency: ~3s

## Analysis Request
1. Evaluate each option against the constraints
2. Consider cost, latency, and information preservation
3. Recommend the SINGLE best option
4. Explain why other options are inferior

## Output Format
```json
{
  "recommended_strategy": "CROSS_NODE_UPGRADE",
  "recommended_model": "qwen3.5:4b",
  "recommended_node": "fnet4",
  "confidence": 0.92,
  "reasoning": "qwen3.5:4b has 131K context which fits the 75K payload, and fnet4 has 27GB RAM. Same-node upgrade to gemma4:e4b would also work but qwen3.5:4b is faster and sufficient.",
  "rejected_options": [
    {"strategy": "CLOUD", "reason": "Unnecessary cost when local option exists"},
    {"strategy": "CHUNK", "reason": "Single model can handle full payload"}
  ],
  "risk_assessment": "Low risk — local model with sufficient context"
}
```
```

---

## Prompt 3: Post-Recovery Validation
**Use when:** A recovery task has completed and needs validation.
**File:** `technical-infrastructure/prompts/413-post-recovery-validation.md`

```markdown
# Post-Recovery Validation

A task that failed with 413 has been recovered using an alternative strategy.
Validate whether the recovery was successful and complete.

## Original Task
{original_task}

## Recovery Strategy Used
{recovery_strategy}

## Recovery Task Results
```
{recovery_results}
```

## Validation Criteria
1. **Completeness:** Did the recovery produce all expected outputs?
2. **Accuracy:** Is the output correct and consistent with the original task?
3. **Information preservation:** Was any information lost during recovery?
4. **Cost efficiency:** Was the chosen strategy cost-effective?

## Output Format
```json
{
  "validation_status": "PASS" | "PARTIAL" | "FAIL",
  "completeness_score": 0.95,
  "accuracy_score": 0.90,
  "information_preserved": true,
  "cost_efficiency": "good",
  "issues": [
    "Minor truncation in section 3, but core logic intact"
  ],
  "recommendation": "Accept results. Log recovery pattern for future routing optimization.",
  "feedback_for_router": {
    "original_model": "qwen3:8b",
    "should_have_routed_to": "qwen3.5:4b",
    "reason": "Token count was underestimated during initial routing"
  }
}
```
```

---

## Prompt 4: 413 Feedback Loop Analysis
**Use when:** Weekly/monthly review of 413 incidents to improve routing.
**File:** `technical-infrastructure/prompts/413-feedback-analysis.md`

```markdown
# 413 Incident Pattern Analysis

Analyze 413 incident logs to identify patterns and recommend routing improvements.

## Incident Data
```json
{incident_logs}
```

## Analysis Questions
1. Which models/nodes have the highest 413 rate?
2. What token ranges are most problematic?
3. Which recovery strategies are most successful?
4. Are there routing decisions that consistently lead to 413?
5. What capacity adjustments would prevent the most 413s?

## Output Format
```json
{
  "summary": {
    "total_incidents": 23,
    "successful_recoveries": 21,
    "failed_recoveries": 2,
    "avg_recovery_time_sec": 8.5
  },
  "top_patterns": [
    {
      "pattern": "Tasks with >30K tokens routed to qwen3:8b",
      "frequency": 15,
      "severity": "high",
      "recommendation": "Route >25K tokens directly to qwen3.5:4b or gemma4:e4b"
    }
  ],
  "routing_adjustments": [
    {
      "rule": "If estimated_tokens > 25000, skip qwen3:8b",
      "expected_reduction": "65%",
      "priority": 1
    }
  ],
  "capacity_recommendations": [
    "fnet3 shows highest 413 rate — consider reducing load or adding RAM"
  ],
  "cost_savings_potential": "$12.50/month"
}
```
```

---

## Prompt 5: Chunk Synthesis
**Use when:** Multiple chunks have completed and need to be combined.
**File:** `technical-infrastructure/prompts/413-chunk-synthesis.md`

```markdown
# Chunk Synthesis

Multiple chunks of a previously split task have completed. Synthesize them into a 
coherent final result.

## Original Task
{original_task}

## Completed Chunks
```
{chunk_results}
```

## Synthesis Instructions
1. Combine all chunk outputs into a single coherent result
2. Eliminate redundancy between overlapping sections
3. Ensure logical flow from chunk to chunk
4. Preserve all key information
5. Format consistently with original task requirements

## Output
Provide the complete synthesized result.
```

---

## Usage in Code

```python
# Load prompt template
from pathlib import Path

PROMPT_DIR = Path("technical-infrastructure/prompts")

def load_prompt(name: str, **kwargs) -> str:
    template = (PROMPT_DIR / f"413-{name}.md").read_text()
    return template.format(**kwargs)

# Example: Recovery decision
prompt = load_prompt(
    "recovery-decision",
    node="fnet3",
    model="qwen3:8b",
    tokens=35000,
    context_limit=32768,
    capabilities="[coding, reasoning]",
    attempt=1,
    same_node_options="gemma4:e4b (18.9GB)",
    cross_node_options="fnet4 (27GB)",
    cloud_options="qwen3.5:397b-cloud ($0.011)",
    num_chunks=2,
    chunk_latency=6,
)

# Send to LLM for decision
result = call_llm(prompt, model="qwen3:8b")
decision = json.loads(result)
```
