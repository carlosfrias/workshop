# PLAN: Prompt Structure for Context Retention with Breadcrumbs

**Created:** 2026-05-03  
**Priority:** 🔴 High  
**Estimated Effort:** 8-12 hours  
**Domain:** prompt-engineering / context-management  

---

## Objective

Design prompt structures that maintain critical information in context while providing breadcrumbs to lost information, enabling efficient use of limited context windows.

---

## Phase 1: Context Retention Research (2-3 hours)

### Tasks
1. **Study prompt engineering patterns**
   - Research "system prompt" best practices
   - Analyze "few-shot learning" effectiveness
   - Review "chain-of-thought" prompting
   - Document "recursive summarization" techniques

2. **Understand attention mechanisms**
   - How do LLMs prioritize context? (recency bias)
   - What influences token retention? (position, repetition, importance markers)
   - Can we "pin" critical tokens? (system prompts, repeated mentions)

3. **Identify information categories**
   - **Critical:** Must always be in context (goals, constraints, key decisions)
   - **Important:** Should be in context if possible (recent discussion, active tasks)
   - **Reference:** Can be retrieved if needed (background, history, details)
   - **Ephemeral:** Can be discarded (greetings, false starts, tangents)

4. **Review existing solutions**
   - LangChain memory modules
   - AutoGen conversation patterns
   - Custom implementations in open-source projects

### Deliverables
- [ ] Prompt engineering patterns document
- [ ] Information categorization framework
- [ ] Competitive analysis of existing solutions

### Success Criteria
- Clear taxonomy of prompt techniques for context retention
- Understanding of what can/cannot be influenced

---

## Phase 2: Breadcrumb Strategy Design (2-3 hours)

### Tasks
1. **Define breadcrumb types**

| Type | Format | Use Case |
|------|--------|----------|
| **Reference Link** | "See Section 3.2 for architecture details" | Point to specific lost content |
| **Summary Pointer** | "As summarized earlier: [brief summary]" | Condensed version of lost info |
| **Checksum** | "Decision hash: abc123" | Verify consistency with earlier decisions |
| **Topic Tag** | "[Topic: Database Design]" | Enable search/retrieval |
| **Timestamp** | "[2026-05-03 14:30]" | Temporal reference |

2. **Design breadcrumb syntax**
   ```markdown
   [BC-REF:chunk_005] Architecture decision: microservices
   [BC-SUM:topic_auth] Auth system: OAuth2 + JWT tokens
   [BC-DEC:dec_012] PostgreSQL selected for primary DB
   [BC-TAG:security] Related to security considerations
   ```

3. **Implement breadcrumb injection**
   - Automatic: System adds breadcrumbs to each response
   - Manual: User can request breadcrumb for specific topic
   - Triggered: Breadcrumb added when topic is referenced

4. **Create breadcrumb index**
   - Map breadcrumbs to chunk IDs
   - Enable lookup: breadcrumb → full content
   - Track breadcrumb usage (which are referenced most)

### Deliverables
- [ ] Breadcrumb type definitions
- [ ] Syntax specification
- [ ] Injection mechanism
- [ ] Breadcrumb index system

### Success Criteria
- Breadcrumbs are concise (<50 tokens each)
- Can navigate from breadcrumb to full content
- Breadcrumb overhead is <5% of total tokens

---

## Phase 3: Importance Ranking Methods (2-3 hours)

### Tasks
1. **Define importance criteria**

| Criterion | Weight | Detection Method |
|-----------|--------|------------------|
| **Recency** | 20% | Timestamp analysis |
| **Frequency** | 15% | Token repetition count |
| **User Emphasis** | 25% | Explicit markers ("IMPORTANT:", "Remember:") |
| **Decision Status** | 25% | Decision keywords ("decided", "concluded") |
| **Action Required** | 15% | Action verbs ("must", "should", "will") |

2. **Implement importance scoring**
   ```python
   def calculate_importance(message, conversation_history):
       score = 0
       score += recency_score(message) * 0.20
       score += frequency_score(message, conversation_history) * 0.15
       score += emphasis_score(message) * 0.25
       score += decision_score(message) * 0.25
       score += action_score(message) * 0.15
       return score  # 0.0 to 1.0
   ```

3. **Create importance markers**
   - User can explicitly mark: `[IMPORTANT]`, `[DECISION]`, `[ACTION]`
   - System can auto-detect: "We decided to...", "Key requirement..."
   - Visual indicators in UI: ⚠️, ✅, 📌

4. **Test importance accuracy**
   - Manually label important content in test conversations
   - Compare with automated importance scores
   - Adjust weights based on accuracy

### Deliverables
- [ ] Importance scoring algorithm
- [ ] Marker syntax (user and system)
- [ ] Accuracy evaluation results

### Success Criteria
- 80%+ accuracy in identifying critical information
- Users can influence importance with markers
- False positive rate <10%

---

## Phase 4: Context Window Optimization (2-3 hours)

### Tasks
1. **Design context priority queue**
   ```
   [System Prompt] — Always present (pinned)
   [Critical Info] — High importance, always present
   [Recent Turns] — Last N turns (sliding window)
   [Important References] — Medium importance, space-permitting
   [Breadcrumbs] — Pointers to lost content (always present)
   [Ephemeral] — Lowest priority, dropped first
   ```

2. **Implement dynamic context management**
   - Monitor token count in real-time
   - Drop lowest-priority content when approaching limit
   - Inject breadcrumbs before dropping content
   - Compact similar content (merge redundant statements)

3. **Create context templates**
   ```markdown
   # System Context (Always Present)
   You are a helpful assistant for [PROJECT].
   Current goal: [GOAL]
   Constraints: [CONSTRAINTS]
   
   # Critical Information (Pinned)
   [CRITICAL_INFO_1]
   [CRITICAL_INFO_2]
   
   # Recent Discussion (Last 5 turns)
   [RECENT_TURNS]
   
   # Breadcrumbs (Pointers to Archived Content)
   [BC-REF:chunk_003] Database architecture details
   [BC-REF:chunk_007] Security requirements
   
   # Current Task
   [CURRENT_TASK]
   ```

4. **Optimize for different model sizes**
   - Small models (4-8B): Aggressive compaction, more breadcrumbs
   - Medium models (30-70B): Balanced approach
   - Large models (100B+): More context, less compaction

### Deliverables
- [ ] Context priority queue implementation
- [ ] Dynamic context management system
- [ ] Context templates for different scenarios
- [ ] Model-specific optimization profiles

### Success Criteria
- Critical information always in context
- Breadcrumbs provide navigation to lost content
- Context fits within model limits with 10% buffer

---

## Phase 5: Testing with Different Model Sizes (2-3 hours)

### Tasks
1. **Select test models**
   - Small: qwen3.5:4b (context: 131K, but slower)
   - Medium: qwen3:8b (context: 40K)
   - Large: gemma4:e4b (context: 32K, but faster per token)
   - Cloud: kimi-k2.6:cloud (context: 128K)

2. **Design test conversations**
   - Short (10 turns): Baseline behavior
   - Medium (50 turns): Some compaction needed
   - Long (200 turns): Heavy compaction required
   - Multi-topic (100 turns, 5 topics): Topic switching + compaction

3. **Measure effectiveness**
   - Information retention: % of critical info recalled
   - Breadcrumb utility: % of breadcrumbs actually used
   - User satisfaction: Does conversation feel continuous?
   - Token efficiency: Overhead vs. benefit ratio

4. **Iterate based on results**
   - Adjust importance weights per model
   - Refine breadcrumb density
   - Optimize context templates

### Deliverables
- [ ] Test conversation suite
- [ ] Performance metrics per model
- [ ] Optimization recommendations

### Success Criteria
- All models retain 80%+ critical information
- Breadcrumb usage >50% (breadcrumbs are useful)
- User satisfaction score >4/5

---

## Tools & Technologies

### Prompt Engineering
- Jinja2 for template rendering
- Custom Python classes for context management
- YAML/JSON for configuration

### Testing
- Automated conversation simulators
- Manual evaluation with rubric
- A/B testing frameworks

### Monitoring
- Token counting (tiktoken, custom counters)
- Context utilization dashboards
- Breadcrumb usage analytics

---

## Success Metrics

- [ ] 90%+ critical information retention across all model sizes
- [ ] Breadcrumb click-through rate >50%
- [ ] Context overhead <15% (breadcrumbs + metadata)
- [ ] User satisfaction >4/5 on conversation continuity
- [ ] Zero instances of critical info lost without breadcrumb

---

## Notes

- Breadcrumbs are a fallback — primary goal is keeping critical info in context
- Different users may prefer different breadcrumb densities
- Consider user control: allow manual pinning of important content
- Breadcrumbs should be actionable (can retrieve full content if needed)

---

**END OF PLAN**
