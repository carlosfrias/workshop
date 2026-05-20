# Data Domain

Bible data fetching, API clients, scrapers, and data pipelines. This domain covers all data acquisition — downloading Bible texts, interfacing with Bible APIs (e.g., ESV API, Bible gateway), parsing original language resources, and managing scripture databases.

## [S-TIGHT]

Self-contained domain context for data tasks. Read this file, follow its rules, then execute.

---

## Conventions

- All scripts in `./data/scripts/`
- All raw data in `./data/raw/`
- All processed data in `./data/processed/`
- API keys stored in `.env` (never committed)
- Scripture references as filenames: `john-3.md`, `genesis-1.json`
- JSON for structured data, Markdown for readable output
- Rate-limit API calls (default: 1 req/sec for free tiers)
- All dates in YYYY-MM-DD format

## Rules

### Must Always
- Store API keys in `.env` files, never in source code
- Rate-limit all API calls to respect service limits
- Cache API responses locally to minimize redundant calls
- Version all processed data with timestamps
- Log all scraper runs with start time, records fetched, and errors
- Validate downloaded data before processing

### Must Never
- Commit API keys or credentials to git
- Make unauthenticated requests to paid APIs
- Ignore rate limits or terms of service
- Store large raw datasets in git (use `.gitignore` and document data sources)
- Skip error handling on network requests

## Quality Checklist

Before considering any data task complete, verify:

- [ ] API keys are in `.env`, not in source code
- [ ] `.env` is in `.gitignore`
- [ ] Rate limiting is implemented
- [ ] Responses are cached locally
- [ ] Data validation passes (schema, completeness)
- [ ] Scripts have clear usage documentation (README or docstrings)
- [ ] Error handling covers network failures and malformed responses

## Common Mistakes

| Mistake | Correct Approach |
|---------|-----------------|
| Hardcoding API keys | Use `.env` files with a template `.env.example` |
| Hitting rate limits | Implement rate limiting and exponential backoff |
| Re-fetching the same data | Cache responses with timestamps |
| No error handling on API calls | Wrap in try/catch, log errors, retry on transient failures |
| Storing binary/large data in git | Use `.gitignore` and document data sources in README |

## Documentation Protocol

After completing any task, document what you did in the project wiki.

### When to Document
- After creating or modifying a scraper or API client
- After discovering API limitations or rate limit behavior
- After processing a new dataset or fixing data quality issues
- After resolving edge cases in scripture data

### What to Document
- **What was done** — Brief summary of the data task and results
- **Why** — Rationale for approach, API choice, or data format
- **What changed** — Scripts created/modified, data files generated
- **Lessons learned** — API quirks, rate limits, gotchas

### Where to Document
- Write to the data activity log: `../../wiki/his-desk/data/Activity Log.md`
- Create dedicated pages for API documentation or data schemas
- Project-level reference pages live in `../../wiki/his-desk/_meta/`

### Format
```markdown
### YYYY-MM-DD — {Title}

**Task**: {What was requested}
**Outcome**: {What was done and result}
**Rationale**: {Why this approach was chosen}
**Files changed**: {List of files created/modified}
**Lessons**: {What to remember for next time}
```

## Cross-Domain References

For tasks that span domains, consult the routing table in `./AGENTS.md` (project root).

- Study tools consuming data → `../study/AGENTS.md`
- Devotional content generation → `../devotional/AGENTS.md`
- Publishing data to site → `../site/AGENTS.md`
- Vault-side notes → `../../../../personal-vault/01-Projects/his-desk/`

---

*Last updated: 2026-05-19*