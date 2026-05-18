# PLAN: Conversation Chunking for Compaction Survival

**Created:** 2026-05-03  
**Priority:** 🔴 High  
**Estimated Effort:** 10-15 hours  
**Domain:** llm-architecture / context-management  

---

## Objective

Discover and implement conversation chunking strategies that preserve context through LLM compaction, enabling long-running conversations without critical information loss.

---

## Phase 1: Context Window Research (2-3 hours)

### Tasks
1. **Understand compaction mechanisms**
   - Research how different LLMs handle context limits
   - Document compaction strategies:
     - Sliding window (drop oldest tokens)
     - Summarization (compress old context)
     - Hierarchical attention (prioritize recent)
     - External memory (RAG-style retrieval)

2. **Map model context limits**
   | Model | Context Window | Compaction Behavior |
   |-------|---------------|---------------------|
   | qwen3.5:4b | 131K tokens | Sliding window + summarization |
   | qwen3:8b | 40K tokens | Sliding window |
   | gemma4:e4b | 32K tokens | Sliding window |
   | kimi-k2.6:cloud | 128K tokens | Proprietary |

3. **Identify information loss patterns**
   - What gets dropped first? (oldest tokens)
   - What gets preserved? (recent context, system prompts)
   - Can compaction be influenced? (prompt engineering)

4. **Review academic literature**
   - Search for "conversation summarization" papers
   - Research "long-context LLM" techniques
   - Study "memory augmentation" approaches

### Deliverables
- [ ] Context management research document
- [ ] Model comparison matrix
- [ ] Information loss pattern analysis

### Success Criteria
- Clear understanding of how/when compaction occurs
- Identified leverage points for influencing compaction

---

## Phase 2: Chunking Algorithm Design (3-4 hours)

### Tasks
1. **Define chunking strategies**

| Strategy | Description | Pros | Cons |
|----------|-------------|------|------|
| **Token-based** | Fixed token counts (512, 1024, 2048) | Simple, predictable | May split semantic units |
| **Semantic** | Chunk by topic/theme changes | Preserves meaning | Requires topic detection |
| **Hierarchical** | Multi-level (conversation → topic → turn) | Flexible, scalable | Complex implementation |
| **Importance-weighted** | Rank by importance, keep high | Preserves critical info | Requires importance scoring |
| **Temporal** | Time-based windows (last N minutes/hours) | Natural for chats | Ignores content density |

2. **Implement chunking prototype**
   ```python
   def chunk_conversation(messages, strategy='semantic', max_tokens=2048):
       if strategy == 'token-based':
           return chunk_by_tokens(messages, max_tokens)
       elif strategy == 'semantic':
           return chunk_by_topics(messages)
       elif strategy == 'hierarchical':
           return chunk_hierarchical(messages)
       # ... etc
   ```

3. **Add metadata to chunks**
   - Timestamp
   - Topic/theme tags
   - Importance score (1-10)
   - Cross-references to related chunks
   - Summary of chunk content

4. **Implement chunk linking**
   - Forward references: "See chunk #5 for details"
   - Backward references: "As mentioned in chunk #2"
   - Thematic links: "Related to: authentication, security"

### Deliverables
- [ ] Chunking algorithm implementations
- [ ] Metadata schema for chunks
- [ ] Chunk linking mechanism

### Success Criteria
- Multiple chunking strategies implemented
- Chunks can be reconstructed into coherent narrative

---

## Phase 3: Checkpoint/Save-Point System (2-3 hours)

### Tasks
1. **Design checkpoint format**
   ```json
   {
     "checkpoint_id": "chk_001",
     "timestamp": "2026-05-03T14:30:00Z",
     "conversation_summary": "Discussed project architecture...",
     "key_decisions": [
       "Use microservices architecture",
       "Deploy to AWS",
       "PostgreSQL for primary DB"
     ],
     "open_questions": [
       "Which authentication provider?",
       "Redis or Memcached for caching?"
     ],
     "chunk_references": ["chk_000", "chk_001"],
     "context_snapshot": "..."
   }
   ```

2. **Implement checkpoint creation**
   - Manual checkpoints (user-triggered)
   - Automatic checkpoints (every N turns, or on topic change)
   - Event-triggered checkpoints (after major decisions)

3. **Build checkpoint retrieval**
   - Load checkpoint into context
   - Merge with current conversation
   - Resolve references to earlier chunks

4. **Checkpoint versioning**
   - Branch checkpoints for alternative paths
   - Merge checkpoints (combine decision trees)
   - Rollback to earlier checkpoint

### Deliverables
- [ ] Checkpoint data format
- [ ] Checkpoint creation/retrieval system
- [ ] Version control for checkpoints

### Success Criteria
- Can save conversation state and resume later
- Checkpoints survive context window overflow

---

## Phase 4: Summarization Techniques (3-4 hours)

### Tasks
1. **Evaluate summarization approaches**

| Approach | Method | Quality | Speed |
|----------|--------|---------|-------|
| **Extractive** | Select key sentences | Good | Fast |
| **Abstractive** | Rewrite in condensed form | Better | Slower |
| **Structured** | Bullet points, decision logs | Excellent for reference | Fast |
| **LLM-generated** | Ask LLM to summarize | Best | Slow, costly |

2. **Implement summarization pipeline**
   ```python
   def summarize_chunk(chunk, style='structured'):
       if style == 'extractive':
           return extract_key_sentences(chunk)
       elif style == 'structured':
           return create_decision_log(chunk)
       elif style == 'llm':
           return llm_summarize(chunk)
   ```

3. **Create summary templates**
   ```markdown
   ## Conversation Summary [Chunk #5]
   **Time:** 2026-05-03 14:30-15:00
   **Topic:** Database Architecture
   
   ### Key Decisions
   - [x] PostgreSQL as primary database
   - [x] Redis for session caching
   
   ### Open Questions
   - [ ] Replica configuration
   - [ ] Backup strategy
   
   ### Action Items
   - [ ] Research PostgreSQL extensions
   - [ ] Estimate storage requirements
   
   ### References
   - See Chunk #3 for initial requirements
   - See Chunk #7 for performance benchmarks
   ```

4. **Test summary quality**
   - Can original context be reconstructed from summary?
   - Are decisions and rationale preserved?
   - Is summary searchable and indexable?

### Deliverables
- [ ] Summarization implementations
- [ ] Summary templates
- [ ] Quality evaluation framework

### Success Criteria
- Summaries preserve critical information
- Can resume conversation from summary alone

---

## Phase 5: Testing & Validation (2-3 hours)

### Tasks
1. **Design test scenarios**
   - Long conversation (100+ turns)
   - Multiple topic shifts
   - Critical information early in conversation
   - Decisions made mid-conversation
   - References to earlier context

2. **Define success metrics**
   - Information retention rate (% of critical info preserved)
   - Reconstruction accuracy (can original be recovered?)
   - Query accuracy (can questions be answered from chunks?)
   - User satisfaction (does it feel continuous?)

3. **Run comparative tests**
   - Test each chunking strategy
   - Compare with/without checkpoints
   - Measure information loss over time
   - Benchmark performance (latency, token usage)

4. **Iterate and refine**
   - Adjust chunk sizes based on results
   - Improve summarization templates
   - Optimize checkpoint frequency
   - Fine-tune importance scoring

### Deliverables
- [ ] Test scenario suite
- [ ] Performance benchmarks
- [ ] Optimization recommendations

### Success Criteria
- 90%+ critical information retained after 100 turns
- Conversation feels continuous to user
- Chunking overhead <10% of total tokens

---

## Tools & Technologies

### Chunking
- Python: nltk, spaCy (for semantic analysis)
- Transformers: BERT for topic modeling
- Custom algorithms for token-based chunking

### Summarization
- LLM-based: Use local models (qwen3.5:4b)
- Extractive: textrank, sumy
- Structured: Custom templates

### Storage
- JSON/JSONL for chunk storage
- SQLite for metadata indexing
- Vector DB for semantic search across chunks

---

## Success Metrics

- [ ] 90%+ information retention after 100 conversation turns
- [ ] Checkpoints load in <2 seconds
- [ ] Chunking overhead <10% of total tokens
- [ ] User can resume conversation after 24+ hours with full context
- [ ] Search across chunks returns relevant results in <1 second

---

## Notes

- Compaction is inevitable — goal is graceful degradation, not prevention
- Different use cases may need different chunking strategies
- User control is important: allow manual checkpoints and chunk editing
- Consider hybrid approach: automatic chunking + user-curated highlights

---

**END OF PLAN**
