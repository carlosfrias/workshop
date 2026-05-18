# PLAN: Prompt Structure for Website Information Extraction

**Created:** 2026-05-03  
**Priority:** 🟡 Medium  
**Estimated Effort:** 6-10 hours  
**Domain:** web-scraping / prompt-engineering  

---

## Objective

Design prompt structures that reliably extract specific information from websites, handling various site structures and content types while maintaining ethical and legal compliance.

---

## Phase 1: Ethics & Legality Review (1-2 hours)

### Tasks
1. **Review legal boundaries**
   - Terms of Service compliance
   - Copyright considerations (factual data vs. creative content)
   - CFAA implications (unauthorized access)
   - GDPR/privacy regulations for personal data

2. **Establish ethical guidelines**
   - Robots.txt compliance
   - Rate limiting (1 request per 2-5 seconds)
   - No authentication bypass
   - No paywall circumvention
   - Respect data ownership

3. **Identify acceptable use cases**
   - ✅ Personal research and analysis
   - ✅ Public data aggregation
   - ✅ Price comparison (public prices)
   - ❌ Commercial redistribution without permission
   - ❌ Personal data harvesting
   - ❌ Competitive intelligence on private data

4. **Create permission checklist**
   - [ ] Site ToS allows scraping
   - [ ] Data is publicly accessible
   - [ ] No authentication required
   - [ ] Rate limiting respected
   - [ ] Use case is ethical

### Deliverables
- [ ] Legal compliance checklist
- [ ] Ethical guidelines document
- [ ] Acceptable use case list
- [ ] Permission checklist

### Success Criteria
- Clear go/no-go decision for each extraction task
- No legal exposure from extraction activities

---

## Phase 2: Prompt Pattern Design (2-3 hours)

### Tasks
1. **Define extraction patterns**

| Pattern | Use Case | Example |
|---------|----------|---------|
| **Structured Table** | Extract tabular data | "Extract all rows from the pricing table" |
| **Key-Value Pairs** | Extract specifications | "Extract: model, price, availability" |
| **List Extraction** | Extract itemized lists | "Extract all product names and prices" |
| **Narrative Summary** | Extract from prose | "Summarize the main features described" |
| **Comparative** | Compare across pages | "Compare prices across these 3 products" |

2. **Create prompt templates**
   ```markdown
   # Structured Extraction Template
   
   You are a precise data extraction assistant.
   
   **Source:** {URL}
   **Content:** {PAGE_CONTENT}
   
   **Extraction Task:** {TASK_DESCRIPTION}
   
   **Required Fields:**
   - {FIELD_1}
   - {FIELD_2}
   - {FIELD_3}
   
   **Output Format:** JSON
   ```

3. **Add context priming**
   ```markdown
   **Context:** This is a product page from an e-commerce site.
   **Your Role:** Extract product information accurately.
   **Constraints:** 
   - Only extract information explicitly stated on the page
   - Do not infer or assume values
   - Mark missing fields as null
   ```

4. **Handle ambiguity**
   ```markdown
   **If information is unclear:**
   - State what is ambiguous
   - Provide best interpretation with confidence score
   - Suggest where to find clarification
   ```

### Deliverables
- [ ] Extraction pattern catalog
- [ ] Prompt template library
- [ ] Context priming guidelines
- [ ] Ambiguity handling protocol

### Success Criteria
- Templates work across different site types
- Extraction accuracy >90% on test set

---

## Phase 3: Site Structure Handling (2-3 hours)

### Tasks
1. **Categorize site structures**

| Structure Type | Characteristics | Extraction Approach |
|----------------|-----------------|---------------------|
| **Static HTML** | Simple, server-rendered | Direct parsing |
| **SPA (React/Vue)** | Client-side rendering | Need Playwright/Selenium |
| **Paginated** | Content split across pages | Follow pagination |
| **Infinite Scroll** | Dynamic loading | Scroll + capture |
| **Mixed Content** | Text + images + tables | Multi-modal extraction |

2. **Pre-process content for LLM**
   - Strip boilerplate (nav, footer, ads)
   - Preserve semantic structure (headings, tables, lists)
   - Convert to Markdown for clarity
   - Truncate to fit context window

3. **Handle multi-page extraction**
   ```python
   def extract_across_pages(urls, extraction_prompt):
       all_results = []
       for url in urls:
           content = fetch_and_clean(url)
           result = query_llm(extraction_prompt.format(content=content))
           all_results.append(result)
       return consolidate_results(all_results)
   ```

4. **Handle dynamic content**
   - Use Playwright to render JavaScript
   - Capture page state after interactions
   - Extract from rendered HTML
   - Note any content that requires user action

### Deliverables
- [ ] Site structure categorization
- [ ] Content preprocessing pipeline
- [ ] Multi-page extraction workflow
- [ ] Dynamic content handling guide

### Success Criteria
- Can extract from all major site types
- Preprocessing reduces token count by 50%+ without losing info

---

## Phase 4: Validation & Verification (2-3 hours)

### Tasks
1. **Design validation checks**
   - Schema validation (required fields present)
   - Type checking (numbers are numeric, dates are valid)
   - Range checking (prices are reasonable, dates are in range)
   - Cross-field consistency (sale price < original price)

2. **Implement verification workflow**
   ```python
   def verify_extraction(extracted_data, source_content):
       checks = [
           check_required_fields(extracted_data),
           check_data_types(extracted_data),
           check_reasonable_ranges(extracted_data),
           check_cross_field_consistency(extracted_data),
           spot_check_vs_source(extracted_data, source_content)
       ]
       return all(checks), generate_validation_report(checks)
   ```

3. **Create confidence scoring**
   ```
   Confidence Score = (Fields Extracted / Fields Requested) 
                      × Format Accuracy 
                      × Validation Pass Rate
   ```

4. **Handle low-confidence extractions**
   - Flag for human review
   - Request clarification from user
   - Try alternative extraction approach
   - Note specific uncertainty

### Deliverables
- [ ] Validation check suite
- [ ] Verification workflow
- [ ] Confidence scoring system
- [ ] Low-confidence handling protocol

### Success Criteria
- Validation catches 95%+ of extraction errors
- Confidence score correlates with actual accuracy

---

## Phase 5: Automation Pipeline (1-2 hours)

### Tasks
1. **Design end-to-end pipeline**
   ```
   URL → Fetch → Clean → Chunk (if needed) → Extract → Validate → Output
   ```

2. **Build pipeline orchestration**
   ```python
   def extract_pipeline(url, extraction_template, output_format='json'):
       # Fetch
       content = fetch_url(url)
       
       # Clean
       cleaned = clean_content(content)
       
       # Extract
       result = query_llm(extraction_template.format(content=cleaned))
       
       # Validate
       is_valid, report = verify_extraction(result, cleaned)
       
       if not is_valid:
           handle_validation_failure(report)
       
       # Output
       return format_output(result, output_format)
   ```

3. **Add error handling**
   - Network failures (retry with backoff)
   - LLM failures (fallback to simpler model)
   - Validation failures (flag for review)
   - Rate limiting (pause and resume)

4. **Create output formats**
   - JSON (structured data)
   - CSV (tabular data)
   - Markdown (reports)
   - Database insert (direct to DB)

### Deliverables
- [ ] Pipeline architecture diagram
- [ ] Pipeline implementation
- [ ] Error handling playbook
- [ ] Output format templates

### Success Criteria
- Pipeline processes 100 URLs without manual intervention
- Error rate <5%
- Output ready for downstream use

---

## Success Metrics

- [ ] Extraction accuracy >90% on test set
- [ ] Validation catches 95%+ of errors
- [ ] Pipeline processes 100 URLs/hour
- [ ] Confidence score correlates with actual accuracy (r > 0.8)
- [ ] Zero legal/ethical violations

---

## Notes

- Always start with manual extraction to validate approach
- Consider official APIs before scraping
- Document all extraction activities for accountability
- Regularly review and update templates as sites change

---

**END OF PLAN**
