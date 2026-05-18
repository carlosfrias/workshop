# PLAN: Keyword Disambiguation Process

**Created:** 2026-05-03  
**Priority:** 🔴 High  
**Estimated Effort:** 8-12 hours  
**Domain:** prompt-routing / natural-language-processing  

---

## Objective

Build a keyword disambiguation process to prevent prompts from triggering multiple processes simultaneously, resolving ambiguity through context analysis, user confirmation, and learning from past decisions.

---

## Phase 1: Keyword Taxonomy & Classification (2-3 hours)

### Tasks
1. **Audit existing keywords and triggers**
   - List all current trigger keywords
   - Map keywords to processes/actions
   - Identify overlaps and conflicts
   - Document false positive rates

2. **Create keyword taxonomy**
   ```
   Level 1: Domain (infrastructure, research, trading, bookkeeping)
   Level 2: Action Type (analyze, deploy, monitor, document)
   Level 3: Specific Target (fnet7, grants, positions, ledger)
   Level 4: Modifiers (urgent, recursive, verbose, dry-run)
   ```

3. **Classify ambiguity types**
   - **Homonyms:** Same word, different meanings ("deploy" → infrastructure vs. theory)
   - **Polysemy:** Related meanings, different contexts ("monitor" → verb vs. noun)
   - **Overlapping Triggers:** Multiple processes claim same keyword
   - **User Confusion:** User uses wrong term for intended action

4. **Build keyword registry**
   ```json
   {
     "keyword": "deploy",
     "processes": [
       {"name": "deploy-infrastructure", "confidence": 0.8, "context": "infrastructure"},
       {"name": "deploy-theory", "confidence": 0.3, "context": "research"}
     ],
     "disambiguation_required": true
   }
   ```

### Deliverables
- [ ] Keyword audit report
- [ ] Keyword taxonomy document
- [ ] Ambiguity type classification
- [ ] Keyword registry (JSON)

### Success Criteria
- All trigger keywords catalogued
- Overlaps clearly identified
- Ambiguity types understood

---

## Phase 2: Context Analysis for Intent Detection (2-3 hours)

### Tasks
1. **Define context signals**
   - **Lexical:** Surrounding words in prompt
   - **Domain:** Which domain file was loaded
   - **Recent:** Previous turns in conversation
   - **User:** User's typical patterns
   - **Temporal:** Time of day, urgency markers

2. **Implement context scoring**
   ```python
   def detect_intent(keyword, context):
       scores = {}
       for process in keyword_registry[keyword]['processes']:
           score = 0
           score += lexical_match(context.words, process.keywords) * 0.3
           score += domain_match(context.domain, process.domain) * 0.3
           score += recent_match(context.history, process.patterns) * 0.2
           score += user_match(context.user_id, process.user_history) * 0.2
           scores[process.name] = score
       return scores
   ```

3. **Create confidence thresholds**
   - **High Confidence (>0.8):** Auto-route, no confirmation needed
   - **Medium Confidence (0.5-0.8):** Suggest with confirmation
   - **Low Confidence (<0.5):** Require explicit disambiguation

4. **Build context window**
   - Track last N turns of conversation
   - Extract domain-relevant terms
   - Maintain user preference profile
   - Update in real-time

### Deliverables
- [ ] Context signal definitions
- [ ] Intent detection algorithm
- [ ] Confidence threshold framework
- [ ] Context window implementation

### Success Criteria
- Intent detection accuracy >85% on test set
- False positive rate <5%

---

## Phase 3: Conflict Resolution Rules (2-3 hours)

### Tasks
1. **Define resolution hierarchy**
   ```
   Priority 1: Explicit user specification ("deploy infrastructure" vs "deploy theory")
   Priority 2: Domain context (if in infrastructure domain, prefer infra processes)
   Priority 3: Recent conversation history (what was just discussed)
   Priority 4: User's historical patterns (what they usually mean)
   Priority 5: Default/fallback (most common usage)
   ```

2. **Implement resolution engine**
   ```python
   def resolve_conflict(keyword, candidates, context):
       # Priority 1: Explicit specification
       if context.explicit_target:
           return filter_by_target(candidates, context.explicit_target)
       
       # Priority 2: Domain context
       if context.domain:
           domain_matches = filter_by_domain(candidates, context.domain)
           if len(domain_matches) == 1:
               return domain_matches
       
       # Priority 3: Recent history
       if context.history:
           history_matches = filter_by_history(candidates, context.history)
           if len(history_matches) == 1:
               return history_matches
       
       # Priority 4: User patterns
       # Priority 5: Default
       return select_most_common(candidates)
   ```

3. **Create override mechanisms**
   - User can explicitly specify: "deploy [infrastructure]"
   - User can override: "not X, I meant Y"
   - System can ask: "Did you mean X or Y?"
   - System can learn: "User typically means X in this context"

4. **Handle edge cases**
   - No matches found → suggest alternatives
   - All matches equally likely → ask user
   - User overrides repeatedly → update user profile
   - New keyword with no history → conservative routing

### Deliverables
- [ ] Resolution hierarchy document
- [ ] Resolution engine implementation
- [ ] Override mechanism design
- [ ] Edge case handling playbook

### Success Criteria
- Conflicts resolved correctly 90%+ of time
- User overrides handled gracefully
- Edge cases documented and handled

---

## Phase 4: User Confirmation Workflows (2-3 hours)

### Tasks
1. **Design confirmation UI patterns**

| Confidence Level | UI Pattern | Example |
|------------------|------------|---------|
| **High (>0.8)** | Silent routing | No confirmation, just execute |
| **Medium (0.5-0.8)** | Inline suggestion | "Did you mean: Deploy Infrastructure?" |
| **Low (<0.5)** | Explicit choice | "Ambiguous: Deploy Infrastructure or Deploy Theory?" |

2. **Implement confirmation prompts**
   ```markdown
   ⚠️ **Ambiguous Keyword Detected**
   
   The keyword "**{keyword}**" could mean:
   
   1. **{Option A}** — {description}
      Example: "{example_A}"
   
   2. **{Option B}** — {description}
      Example: "{example_B}"
   
   **Please clarify:**
   - Reply "1" or "2" to select
   - Or rephrase your request more specifically
   - Or say "always use option 1 for this keyword"
   ```

3. **Create learning from confirmations**
   - Record user's choice
   - Update user preference profile
   - Adjust confidence scores for future
   - Optionally update global keyword registry

4. **Handle confirmation timeouts**
   - If no response after N minutes → escalate
   - Escalation: ask again with more context
   - Final fallback: use most common interpretation with disclaimer

### Deliverables
- [ ] Confirmation UI patterns
- [ ] Confirmation prompt templates
- [ ] Learning mechanism from confirmations
- [ ] Timeout handling protocol

### Success Criteria
- Users find confirmations helpful, not annoying
- Confirmation rate decreases over time (system learns)
- User satisfaction >4/5 with disambiguation process

---

## Phase 5: Learning from Past Ambiguities (2-3 hours)

### Tasks
1. **Design ambiguity log**
   ```json
   {
     "timestamp": "2026-05-03T14:30:00Z",
     "keyword": "deploy",
     "context": {"domain": "infrastructure", "user": "friasc"},
     "candidates": ["deploy-infrastructure", "deploy-theory"],
     "selected": "deploy-infrastructure",
     "confidence_before": 0.6,
     "confidence_after": 0.8,
     "user_feedback": "correct"
   }
   ```

2. **Implement learning algorithm**
   ```python
   def update_from_ambiguity(log_entry):
       # Update user profile
       user_profiles[log_entry.user].add_preference(
           log_entry.keyword, 
           log_entry.selected
       )
       
       # Update keyword registry
       keyword_registry[log_entry.keyword].update_confidence(
           log_entry.selected,
           log_entry.confidence_after
       )
       
       # Update domain mappings
       if log_entry.context.domain:
           domain_keyword_map[log_entry.context.domain][log_entry.keyword] = log_entry.selected
   ```

3. **Create periodic review process**
   - Weekly: Review ambiguity logs
   - Identify patterns (same keyword, same confusion)
   - Update keyword registry proactively
   - Retrain intent detection model if needed

4. **Build feedback loop**
   - User can rate routing accuracy
   - System can ask "Was this routing correct?"
   - Negative feedback triggers immediate review
   - Positive feedback reinforces current approach

### Deliverables
- [ ] Ambiguity log schema
- [ ] Learning algorithm implementation
- [ ] Periodic review process
- [ ] Feedback loop mechanism

### Success Criteria
- Ambiguity rate decreases 50%+ over 30 days
- System learns from each ambiguity event
- User feedback incorporated within 24 hours

---

## Success Metrics

- [ ] Keyword ambiguity rate <5% after 30 days
- [ ] Intent detection accuracy >90%
- [ ] User confirmation rate <20% (system learns)
- [ ] User satisfaction >4/5 with disambiguation
- [ ] Zero instances of wrong process triggered without recovery

---

## Notes

- Disambiguation is ongoing — new keywords and conflicts will emerge
- User experience is critical — confirmations should feel helpful, not obstructive
- Learning should be transparent — users can see and correct their profile
- Consider multi-language support if workspace expands

---

**END OF PLAN**
