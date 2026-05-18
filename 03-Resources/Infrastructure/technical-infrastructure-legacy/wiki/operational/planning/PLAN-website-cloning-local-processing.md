# PLAN: Website Cloning for Local Processing

**Created:** 2026-05-03  
**Priority:** 🟡 Medium  
**Estimated Effort:** 6-10 hours  
**Domain:** web-scraping / data-processing  

---

## Objective

Create a systematic approach to clone websites for local processing, ensuring legal compliance, technical completeness, and efficient storage organization.

---

## Phase 1: Legal & Ethical Framework (2-3 hours)

### Tasks
1. **Review terms of service**
   - Create checklist for ToS compliance per site
   - Identify explicit prohibitions on scraping/mirroring
   - Document acceptable use policies
   - Note rate limiting requirements

2. **Understand legal boundaries**
   - Research CFAA (Computer Fraud and Abuse Act) implications
   - Review hiQ Labs v. LinkedIn precedent (public data scraping)
   - Understand copyright limitations (factual data vs. creative content)
   - Document fair use considerations for research/personal use

3. **Establish ethical guidelines**
   - Robots.txt compliance (respect Disallow rules)
   - Rate limiting (1 request per 2-5 seconds minimum)
   - User-Agent identification (transparent bot identification)
   - No circumvention of authentication/paywalls
   - No commercial redistribution without permission

4. **Create permission request template**
   - Email template for requesting explicit permission
   - Documentation of granted permissions
   - Alternative: Use official APIs when available

### Deliverables
- [ ] Legal compliance checklist
- [ ] Ethical scraping guidelines document
- [ ] Permission request email template
- [ ] Risk assessment matrix (low/medium/high per site)

### Success Criteria
- Clear go/no-go decision for each target site
- No legal exposure from cloning activities
- Documented due diligence for each site

---

## Phase 2: Tool Selection & Setup (2-3 hours)

### Tasks
1. **Evaluate static site mirroring tools**

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **wget** | Simple static sites | Built-in, recursive, fast | No JS rendering |
| **HTTrack** | Complete mirrors | GUI, resumption, filters | Windows-focused, dated |
| **SiteSucker** | macOS users | Easy, handles CSS/JS | Paid, no JS rendering |
| **Cyotek WebCopy** | Windows | Good UI, customizable | Windows only |
| **BrowseX** | Advanced users | Python-based, extensible | Requires coding |

2. **Evaluate dynamic content tools**
   - **Playwright** — Full browser automation, handles JS
   - **Puppeteer** — Chrome-based, good for React/Vue sites
   - **Selenium** — Mature, multi-browser support
   - **SingleFile** (browser extension) — Manual single-page capture

3. **Select hybrid approach**
   - wget/HTTrack for static assets
   - Playwright for JavaScript-rendered content
   - Manual capture for critical pages

4. **Install and configure tools**
   ```bash
   # macOS
   brew install wget
   brew install --cask httrack
   npm install -g playwright
   playwright install
   ```

### Deliverables
- [ ] Tool comparison matrix
- [ ] Installed and tested toolkit
- [ ] Configuration profiles for different site types

### Success Criteria
- All tools installed and functional
- Test clone completed successfully on sample site

---

## Phase 3: Cloning Methodology (3-4 hours)

### Tasks
1. **Static site cloning (wget)**
   ```bash
   wget --mirror \
        --convert-links \
        --adjust-extension \
        --page-requisites \
        --no-parent \
        --wait=2 \
        --random-wait \
        --user-agent="Mozilla/5.0 (compatible; ResearchBot/1.0)" \
        https://example.com
   ```

2. **Dynamic site cloning (Playwright)**
   ```python
   # Clone dynamic site with Playwright
   from playwright.sync_api import sync_playwright
   
   def clone_site(start_url, output_dir):
       with sync_playwright() as p:
           browser = p.chromium.launch()
           page = browser.new_page()
           # Crawl and save pages
           # Handle JavaScript rendering
           browser.close()
   ```

3. **Handle common challenges**
   - **Pagination:** Detect and follow "next" links
   - **Infinite scroll:** Use Playwright to scroll and capture
   - **Login walls:** Skip (ethical boundary)
   - **CDN resources:** Download from original CDN or mirror locally
   - **Forms:** Document but don't submit

4. **Incremental updates**
   - Track last clone timestamp
   - Use `--if-modified-since` with wget
   - Compare sitemaps for changes
   - Version control cloned content (git LFS for large files)

### Deliverables
- [ ] Cloning scripts for static and dynamic sites
- [ ] Challenge resolution playbook
- [ ] Incremental update workflow

### Success Criteria
- Complete clone of test site (100+ pages)
- All links functional in local copy
- JavaScript-rendered content captured

---

## Phase 4: Storage Organization (2-3 hours)

### Tasks
1. **Design directory structure**
   ```
   cloned-sites/
   ├── example-com/
   │   ├── metadata.json          # Clone timestamp, URL, tool used
   │   ├── sitemap.xml            # Original sitemap if available
   │   ├── pages/                 # HTML files
   │   ├── assets/                # CSS, JS, images
   │   │   ├── css/
   │   │   ├── js/
   │   │   └── images/
   │   └── logs/                  # Clone logs, errors
   ├── another-site-com/
   └── INDEX.md                   # Master index of all cloned sites
   ```

2. **Create metadata schema**
   ```json
   {
     "url": "https://example.com",
     "cloneDate": "2026-05-03T14:30:00Z",
     "tool": "wget",
     "toolVersion": "1.21.4",
     "totalPages": 147,
     "totalSize": "23.4MB",
     "dynamicContent": false,
     "robotsCompliant": true,
     "permissionGranted": false,
     "notes": "Static site, fully cloned"
   }
   ```

3. **Implement versioning**
   - Git repository for text content
   - Git LFS for binary assets
   - Tagged releases per clone date
   - Diff tracking between versions

4. **Search index creation**
   - Elasticsearch or Meilisearch for full-text search
   - Index HTML content, metadata, URLs
   - Enable cross-site search

### Deliverables
- [ ] Standardized directory structure
- [ ] Metadata JSON schema
- [ ] Version control setup
- [ ] Search index implementation

### Success Criteria
- Easy to locate specific cloned site
- Metadata complete for audit purposes
- Search functional across all cloned content

---

## Phase 5: Local Processing Pipeline (3-4 hours)

### Tasks
1. **Design processing workflow**
   ```
   Cloned Site → Text Extraction → Cleaning → Chunking → Embedding → Vector DB → Query
   ```

2. **Text extraction tools**
   - **BeautifulSoup** — HTML parsing, text extraction
   - **Readability** (Mozilla) — Extract main content, remove boilerplate
   - **trafilatura** — High-quality text extraction
   - **html2text** — Convert HTML to Markdown

3. **Content cleaning**
   - Remove navigation, ads, footers
   - Normalize whitespace
   - Fix encoding issues
   - Remove script/style tags
   - Deduplicate content

4. **Chunking strategies**
   - By semantic sections (headings)
   - By token count (512, 1024, 2048 tokens)
   - Overlapping chunks for context continuity
   - Hierarchical chunking (page → section → paragraph)

5. **Embedding and indexing**
   - Choose embedding model (local: nomic-embed-text, cloud: text-embedding-3-large)
   - Vector database (Chroma, Qdrant, Pinecone)
   - Metadata enrichment (URL, title, date, site)

6. **Query interface**
   - Natural language search
   - Filter by site, date, content type
   - Citation back to original URL
   - Export results (JSON, Markdown, PDF)

### Deliverables
- [ ] Text extraction pipeline
- [ ] Chunking configuration
- [ ] Vector database with embeddings
- [ ] Query interface (CLI or web UI)

### Success Criteria
- Can query cloned content and get relevant results
- Citations link back to original source
- Processing pipeline handles 1000+ pages efficiently

---

## Tools & Technologies

### Cloning
- wget, HTTrack, SiteSucker
- Playwright, Puppeteer, Selenium
- SingleFile (browser extension)

### Processing
- Python: BeautifulSoup, trafilatura, readability-lxml
- Node.js: jsdom, cheerio
- Embedding: sentence-transformers, OpenAI embeddings
- Vector DB: Chroma, Qdrant, Weaviate

### Storage
- Git + Git LFS
- Directory structure with metadata
- Elasticsearch/Meilisearch for search

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Legal action from site owner | Low | High | Strict ToS compliance, permission requests |
| Incomplete clone (missing JS) | Medium | Medium | Use Playwright for dynamic sites |
| Storage space exhaustion | Medium | Low | Monitor disk usage, compress old clones |
| Broken links in local copy | High | Low | Accept as limitation, document known issues |
| Rate limiting / IP ban | Medium | Medium | Respect rate limits, use delays, rotate IPs if needed |

---

## Success Metrics

- [ ] 10+ websites successfully cloned with full content
- [ ] 100% legal compliance (no ToS violations)
- [ ] Search query returns relevant results in <2 seconds
- [ ] Processing pipeline handles 100 pages/minute
- [ ] Storage efficient: <10MB per 100 pages average

---

## Notes

- Always prioritize official APIs over scraping when available
- Consider Internet Archive (archive.org) as alternative source
- Document all cloning activities for accountability
- Regularly review and delete outdated clones
- Consider ethical implications of data usage

---

**END OF PLAN**
