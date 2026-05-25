# Test Plan: Autonomous 413 Recovery System (TI-011)
**Date:** 2026-05-02  
**Status:** Ready for execution  
**Scope:** End-to-end validation of 413 detection, recovery, and prevention

---

## Test Categories

### Category 1: Pre-flight Checks (`handle_413.py --preflight`)

#### Test 1.1: Normal Prompt (Within Limits)
- **Input:** `python3 handle_413.py --preflight --prompt "Write hello world" --model qwen3:8b`
- **Expected:** `status: "ok"`, `tokens: ~4`, `exit_code: 0`
- **Pass Criteria:** Status is "ok", utilization < 60%

#### Test 1.2: Warning Zone (60-85% of Context)
- **Input:** Prompt with ~22,000 tokens (67% of qwen3:8b 32K context)
- **Expected:** `status: "warning"`, suggests splitting
- **Pass Criteria:** Status is "warning", exit code 1

#### Test 1.3: Hard Limit Exceeded (>85%)
- **Input:** Prompt with ~30,000 tokens on qwen3:8b
- **Expected:** `status: "oversized"`, action recommended
- **Pass Criteria:** Status is "oversized", exit code 2, action is not None

#### Test 1.4: Vision Requirement Check
- **Input:** `--preflight --prompt "Analyze image" --model qwen3:8b --requires-vision`
- **Expected:** Status reflects vision capability mismatch
- **Pass Criteria:** Action accounts for vision requirement

#### Test 1.5: JSON Output Format
- **Input:** All above tests with `--json` flag
- **Expected:** Valid JSON with all required fields
- **Pass Criteria:** JSON parses, contains: status, tokens, context, action, action_details

---

### Category 2: Recovery Decision Logic (`handle_413.py` internal)

#### Test 2.1: Same-Node Upgrade
- **Scenario:** qwen3:8b on fnet3 with 35K tokens
- **Expected:** Strategy = SAME_NODE_UPGRADE, model = gemma4:e4b
- **Pass Criteria:** fnet3 can run gemma4:e4b (18.9GB < 27GB) and 35K < 111K context

#### Test 2.2: Cross-Node Same Model
- **Scenario:** qwen3:8b on fnet3, but fnet3 is at capacity
- **Expected:** Strategy = CROSS_NODE_SAME, node = fnet4/fnet5/fnet6
- **Pass Criteria:** Alternative 31GB node selected

#### Test 2.3: Cross-Node Upgrade
- **Scenario:** qwen3:8b on fnet1 (15GB node) with 40K tokens
- **Expected:** Strategy = CROSS_NODE_UPGRADE, model = qwen3.5:4b, node = fnet1
- **Pass Criteria:** qwen3.5:4b has 131K context, fits on fnet1 (5.7GB < 12.5GB)

#### Test 2.4: Cloud Escalation
- **Scenario:** 150K tokens, exceeds all local models
- **Expected:** Strategy = CLOUD, model = qwen3.5:397b-cloud
- **Pass Criteria:** Cloud model has 262K context, cost ~$0.011

#### Test 2.5: Chunking
- **Scenario:** 250K tokens, exceeds even cloud model (262K × 0.85 = 222K)
- **Expected:** Strategy = CHUNK, num_chunks >= 2
- **Pass Criteria:** Each chunk < 157K tokens (85% of 131K gemma4:e4b or 222K cloud)

#### Test 2.6: Vision-Aware Recovery
- **Scenario:** Vision task on qwen3:8b (no vision)
- **Expected:** Strategy upgrades to vision-capable model (qwen3.5:4b or gemma4:e4b)
- **Pass Criteria:** Selected model has has_vision = True

#### Test 2.7: Tools-Aware Recovery
- **Scenario:** Tools-required task, check that tools capability is preserved
- **Expected:** All recovery options maintain tools=True
- **Pass Criteria:** No model without tools is selected

---

### Category 3: Chunking (`handle_413.py --chunk`)

#### Test 3.1: No Chunking Needed
- **Input:** Text with 1000 tokens, max_chunk=8000
- **Expected:** Single chunk, type="full"
- **Pass Criteria:** len(chunks) == 1, chunk[0].type == "full"

#### Test 3.2: Two Chunks
- **Input:** Text with 15,000 tokens, max_chunk=8000
- **Expected:** 2 chunks with overlap
- **Pass Criteria:** len(chunks) == 2, each chunk.tokens < 8000, overlap present

#### Test 3.3: Paragraph Boundary
- **Input:** Multiple paragraphs, total 20,000 tokens
- **Expected:** Chunks split at paragraph boundaries
- **Pass Criteria:** No chunk starts mid-paragraph (unless paragraph > max_chunk)

#### Test 3.4: Sentence Boundary Fallback
- **Input:** Single paragraph > max_chunk, total 15,000 tokens
- **Expected:** Chunks split at sentence boundaries (. ! ?)
- **Pass Criteria:** No chunk starts mid-sentence

#### Test 3.5: Word Boundary Fallback
- **Input:** Single sentence > max_chunk, total 15,000 tokens
- **Expected:** Chunks split at word boundaries
- **Pass Criteria:** No chunk starts mid-word

#### Test 3.6: JSON Output Validity
- **Input:** Any chunking test with --json
- **Expected:** Valid JSON array with chunk_id, tokens, text, type
- **Pass Criteria:** JSON parses, all fields present

---

### Category 4: Worker Detection (`task-worker.sh`)

#### Test 4.1: 413 in stderr
- **Setup:** Create task that produces "413 Request Entity Too Large" in stderr
- **Execution:** Run task-worker.sh
- **Expected:** Result file has status="failed_413", recovery_needed=True
- **Pass Criteria:** Status field is exactly "failed_413"

#### Test 4.2: 413 in stdout
- **Setup:** Create task that produces "context length exceeded" in stdout
- **Execution:** Run task-worker.sh
- **Expected:** Same as 4.1
- **Pass Criteria:** Detection works for both stdout and stderr

#### Test 4.3: Token Parsing
- **Setup:** Create task with error containing "45000 tokens exceeds limit of 32768"
- **Execution:** Run task-worker.sh
- **Expected:** detected_tokens=45000, detected_limit=32768
- **Pass Criteria:** Both values parsed correctly from error text

#### Test 4.4: Normal Failure (Not 413)
- **Setup:** Create task that exits with code 1 but no 413 indicators
- **Execution:** Run task-worker.sh
- **Expected:** status="failed" (not "failed_413")
- **Pass Criteria:** Does NOT misclassify non-413 errors

#### Test 4.5: Successful Task
- **Setup:** Create task that exits with code 0
- **Execution:** Run task-worker.sh
- **Expected:** status="completed"
- **Pass Criteria:** No false positives on successful tasks

---

### Category 5: Watcher Auto-Recovery (`decompose-watcher.py`)

#### Test 5.1: Detect and Recover Single 413
- **Setup:** Submit task to fnet3/qwen3:8b with 40K token payload
- **Execution:** Run watcher with --poll --execute
- **Expected:** 
  1. Task fails with status="failed_413"
  2. Watcher detects 413 during polling
  3. Recovery task submitted (e.g., to fnet4/qwen3.5:4b)
  4. Recovery task completes successfully
- **Pass Criteria:** Final report shows 1 successful recovery

#### Test 5.2: Multiple 413s in Batch
- **Setup:** Submit 3 tasks, 2 will trigger 413
- **Execution:** Run watcher
- **Expected:** Both 413s recovered independently
- **Pass Criteria:** 2 recovery tasks submitted, both complete

#### Test 5.3: Recovery Loop Prevention
- **Setup:** Submit task where recovery also triggers 413
- **Execution:** Run watcher
- **Expected:** 
  1. Original task fails 413
  2. Recovery task attempted
  3. Recovery also fails 413
  4. No further recovery attempted (_recovery_attempted flag set)
- **Pass Criteria:** Exactly 2 attempts, no infinite loop

#### Test 5.4: Timeout Handling
- **Setup:** Submit task, configure very short timeout
- **Execution:** Run watcher with --timeout 30
- **Expected:** Report shows timed_out=True
- **Pass Criteria:** Does not hang, returns within timeout

#### Test 5.5: Dry Run Mode
- **Setup:** Any 413 scenario
- **Execution:** Run watcher without --execute
- **Expected:** Reports recovery plan but does not submit
- **Pass Criteria:** No actual tasks submitted

---

### Category 6: Integration Tests (End-to-End)

#### Test 6.1: Full Pipeline — Normal Case
- **Setup:** Submit HARD prompt with < 25K tokens
- **Flow:** Trigger → Decompose → Match → Submit → Execute → Collect → Synthesize
- **Expected:** All local, no 413s, no cloud costs
- **Pass Criteria:** 100% local execution, total time < 60s

#### Test 6.2: Full Pipeline — 413 Recovery
- **Setup:** Submit HARD prompt that decomposes into sub-task > 27K tokens
- **Flow:** Trigger → Decompose → Match → Submit → 413 Detected → Recover → Re-submit → Complete
- **Expected:** Original fails 413, recovery succeeds, final result valid
- **Pass Criteria:** Final status "completed", recovery path documented

#### Test 6.3: Full Pipeline — Chunking
- **Setup:** Submit prompt requiring 250K+ token processing
- **Flow:** Trigger → Decompose → Match → 413 → Chunk → Match Chunks → Parallel Submit → Synthesize
- **Expected:** Multiple chunks execute in parallel, final synthesis combines results
- **Pass Criteria:** All chunks complete, synthesis produces coherent result

#### Test 6.4: Full Pipeline — Vision + 413
- **Setup:** Submit vision task with large image analysis
- **Flow:** Trigger → Decompose → Match → 413 (vision model too small) → Upgrade to vision model
- **Expected:** Recovery routes to vision-capable model (qwen3.5:4b or gemma4:e4b)
- **Pass Criteria:** Vision capability preserved through recovery

---

### Category 7: Load and Stress Tests

#### Test 7.1: Concurrent 413s
- **Setup:** Submit 10 tasks simultaneously, all oversized
- **Execution:** Run watcher
- **Expected:** All 10 recovered independently, no race conditions
- **Pass Criteria:** 10/10 recovered, no duplicate recovery tasks

#### Test 7.2: Rapid Succession
- **Setup:** Submit 5 tasks in rapid succession (< 1s apart)
- **Execution:** Run watcher
- **Expected:** Each handled independently
- **Pass Criteria:** All processed, no dropped tasks

#### Test 7.3: Maximum Chunk Count
- **Setup:** Submit 1MB text (250K tokens)
- **Execution:** Chunk and execute
- **Expected:** Reasonable number of chunks (< 50), all complete
- **Pass Criteria:** < 50 chunks, total time < 300s

---

### Category 8: Regression Tests

#### Test 8.1: Non-413 Errors Unchanged
- **Setup:** Task that fails with network error, permission error, etc.
- **Execution:** Run worker + watcher
- **Expected:** status="failed" (not "failed_413"), no recovery attempted
- **Pass Criteria:** Original behavior preserved

#### Test 8.2: Small Payloads Unchanged
- **Setup:** Task with < 1000 tokens
- **Execution:** Run full pipeline
- **Expected:** No pre-flight rejections, no unnecessary checks
- **Pass Criteria:** No performance regression

#### Test 8.3: Existing Task Format Compatibility
- **Setup:** Task JSON without "requires_vision" or "requires_tools" fields
- **Execution:** Run recovery
- **Expected:** Defaults applied (vision=False, tools=True)
- **Pass Criteria:** No KeyError exceptions

---

## Test Execution Schedule

| Phase | Tests | Environment | Estimated Time | Owner |
|-------|-------|-------------|----------------|-------|
| Phase 1 | 1.1–1.5, 2.1–2.7 | Local (Mac orchestrator) | 30 min | Auto |
| Phase 2 | 3.1–3.6 | Local | 20 min | Auto |
| Phase 3 | 4.1–4.5 | fnet3 (single node) | 15 min | Deployed worker |
| Phase 4 | 5.1–5.5 | fnet3 + orchestrator | 30 min | Watcher |
| Phase 5 | 6.1–6.4 | Full lab (all nodes) | 45 min | End-to-end |
| Phase 6 | 7.1–7.3 | Full lab | 30 min | Stress test |
| Phase 7 | 8.1–8.3 | Full lab | 15 min | Regression |

**Total Estimated Time:** ~3 hours  
**Automation:** All tests can be scripted. Phase 1-2 run locally. Phase 3-7 require lab.

---

## Test Scripts

### Quick Validation Script
```bash
#!/bin/bash
# Run all pre-flight tests locally

cd /Users/friasc/Cloud/workshop/technical-infrastructure/scripts

echo "=== Test 1.1: Normal prompt ==="
python3 handle_413.py --preflight --prompt "Hello world" --model qwen3:8b --json

echo "=== Test 1.3: Oversized ==="
python3 -c "print('A ' * 30000)" > /tmp/big-prompt.txt
python3 handle_413.py --preflight --file /tmp/big-prompt.txt --model qwen3:8b --json

echo "=== Test 2.1: Same-node upgrade ==="
python3 -c "
import sys; sys.path.insert(0, '.')
from handle_413 import determine_recovery
r = determine_recovery('qwen3:8b', 35000, failed_node='fnet3')
print(r)
"

echo "=== Test 2.4: Cloud escalation ==="
python3 -c "
import sys; sys.path.insert(0, '.')
from handle_413 import determine_recovery
r = determine_recovery('qwen3:8b', 150000, failed_node='fnet3')
print(r)
"

echo "=== Test 2.5: Chunking ==="
python3 -c "
import sys; sys.path.insert(0, '.')
from handle_413 import determine_recovery
r = determine_recovery('qwen3:8b', 250000, failed_node='fnet3')
print(r)
"
```

### Worker Detection Test
```bash
#!/bin/bash
# Test 413 detection on a node

NODE="fnet3"
ssh $NODE "mkdir -p /srv/tasks/pending /srv/tasks/completed"

# Create a fake 413 task
cat <>'EOF' | ssh $NODE "cat > /srv/tasks/pending/test-413.json"
{"id":"test-413","command":"echo '413 Request Entity Too Large: token limit exceeded' >&2; exit 1","type":"shell"}
EOF

# Run worker
ssh $NODE "sudo /usr/local/bin/task-worker.sh"

# Check result
ssh $NODE "cat /srv/tasks/completed/test-413.json | python3 -m json.tool"
```

### End-to-End Test
```bash
#!/bin/bash
# Full pipeline test with 413 recovery

cd /Users/friasc/Cloud/workshop

# Create trigger
cat > .pi/decompose-triggers/pending/test-e2e-413.json <<'EOF'
{"id":"test-e2e-413","prompt":"Process 40000 words of market data analysis","confidence":0.9,"timestamp":"2026-05-02T22:00:00","node_pool":["fnet3"],"max_steps":3}
EOF

# Run watcher
python3 technical-infrastructure/scripts/decompose-watcher.py --poll --execute

# Check results
ls -la .pi/decompose-triggers/completed/test-e2e-413*
cat .pi/decompose-triggers/results/test-e2e-413.json 2>/dev/null || echo "No results yet"
```

---

## Pass/Fail Criteria

| Metric | Pass Threshold | Fail Threshold |
|--------|---------------|----------------|
| Pre-flight accuracy | 100% correct classification | Any misclassification |
| Recovery strategy selection | Correct strategy for 100% of scenarios | > 0% wrong strategy |
| Chunking correctness | All chunks < limit, logical boundaries | Any chunk > limit or mid-word |
| Worker detection | 100% of 413s detected | Any missed 413 |
| Worker false positives | 0% non-413s misclassified | Any misclassification |
| Watcher auto-recovery | ≥ 90% of 413s recovered | < 90% recovery rate |
| Recovery loop prevention | 0 infinite loops | Any loop > 3 attempts |
| End-to-end success | ≥ 80% of 413 scenarios succeed | < 80% success |
| Total execution time | < 300s for 413 recovery | > 300s |
| Cloud cost per 413 | ≤ $0.011 (LOW tier) | > $0.011 |

---

## Test Data

### Token Counts by Scenario

| Scenario | Characters | Estimated Tokens | Context | % of Context |
|----------|-----------|----------------|---------|-------------|
| Normal | 50 | 13 | 32,768 | 0.04% |
| Warning | 90,000 | 22,500 | 32,768 | 69% |
| Oversized (qwen3:8b) | 120,000 | 30,000 | 32,768 | 92% |
| Same-node upgrade | 140,000 | 35,000 | 32,768 | 107% |
| Cloud needed | 600,000 | 150,000 | 32,768 | 458% |
| Chunking | 1,000,000 | 250,000 | 32,768 | 763% |

### Test Payload Generator
```python
def generate_payload(tokens: int) -> str:
    """Generate test payload of approximately N tokens."""
    chars_needed = tokens * 4
    return "WORD " * (chars_needed // 5)
```

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Test Engineer | Auto | 2026-05-02 | ✅ Phase 1-2 complete |
| System Engineer | Auto | 2026-05-02 | ✅ Phase 3 complete |
| Integration Lead | Auto | 2026-05-02 | ⏳ Phase 4-7 pending |
| QA Lead | Auto | 2026-05-02 | ⏳ Pending |

---

## Related Documents

- [SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md](../sessions/SESSION-NOTES-2026-05-02-2200-AUTONOMOUS-413-RECOVERY.md)
- [PLAN-2026-05-02-1930-LLM-DRIVEN-DECOMPOSITION.md](PLAN-2026-05-02-1930-LLM-DRIVEN-DECOMPOSITION.md)
- `handle_413.py`
- `scripts/task-worker.sh`
