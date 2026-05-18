# Routing Transparency Extension

**TUI footer enhancement with routing visibility, cost tracking, and billing reports.**

---

## Overview

The Routing Transparency extension provides complete visibility into how prompts are routed through the Trading Desk AI workspace, with full audit trails and customer billing capabilities.

**GitHub:** [`carlosfrias/pi-routing-transparency`](https://github.com/carlosfrias/pi-routing-transparency) (Private)

---

## Problem Solved

**Before:**
- TUI footer showed confusing status: `"trivial → ollama/qwen3.5:4b @ fnet6 router:off (auto) -> ollama/qwen3.5:4b"`
- No visibility into which keywords matched which route
- No visibility into why a model was selected
- Ctrl+P model cycling didn't update status messages
- **Impossible to bill customers** without routing/cost trails
- Accidental cloud model overuse ($$$)

**After:**
- Clear 3-row footer showing route, keywords, domain, timing, cost
- Full JSONL audit trail of every routing decision
- Billing reports in Markdown, CSV, and Quicken QIF (Gnucash)
- Domain-to-customer mapping for consolidated billing
- Performance analytics with P95/P99 latencies

---

## Features

### 1. Enhanced TUI Footer (3 Rows)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ ~/Dropbox/workshop (main)                                           │
│ ↑1.8M ↓33k R1.2s W0.8s $6.052  5.1%/262k  qwen3.5:4b • thinking off            │
│ ROUTE: monitoring ← [status,check] | domain: position-monitor | TIME: 2.0s | EST│
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Row 1:** Path + git branch (preserved from current TUI)

**Row 2:**
| Field | Meaning |
|-------|---------|
| `↑1.8M` | Input tokens (1.8 million) |
| `↓33k` | Output tokens (33 thousand) |
| `R1.2s` | **Routing time** — time to classify prompt (1.2 seconds) |
| `W0.8s` | **Waiting time** — time waiting for model response (0.8 seconds) |
| `$6.052` | Cumulative session cost |
| `5.1%/262k` | Context window usage |
| `qwen3.5:4b • thinking off` | Current model + thinking level |

**Row 3:**
| Field | Meaning |
|-------|---------|
| `ROUTE: monitoring` | Matched route name |
| `← [status,check]` | Keywords that triggered the route |
| `domain: position-monitor` | Customer domain |
| `TIME: 2.0s` | Total execution time |
| `EST: $0.00` | Estimated cost for this prompt |

---

### 2. JSONL Audit Trail

**Location:** `~/.pi/logs/routing-decisions.jsonl`

**Format:**
```json
{
  "timestamp": "2026-05-11T08:23:45.123Z",
  "prompt": "check position status for AAPL",
  "route": "monitoring",
  "model": "qwen3.5:4b",
  "provider": "ollama",
  "thinkingLevel": "off",
  "source": "keyword",
  "domain": "position-monitor",
  "matchedKeywords": ["status", "check"],
  "complexityPrediction": { "level": "trivial", "confidence": 0.82 },
  "timing": {
    "routingDecisionMs": 2.3,
    "modelLatencyMs": 1234.5,
    "totalExecutionMs": 1289.7
  },
  "cost": {
    "estimated": 0.00,
    "actual": 0.00,
    "currency": "USD"
  },
  "tokens": {
    "input": 234,
    "output": 567,
    "cacheRead": 0,
    "cacheWrite": 0
  },
  "session": {
    "id": "sess_abc123",
    "startTime": "2026-05-11T08:00:00.000Z",
    "cumulativeCost": 0.003
  }
}
```

**Log Management:**
- Auto-rotation after 30 days
- Optional compression after 7 days
- Configurable field inclusion (prompt, keywords, cost, timing)

---

### 3. Billing Reports

**Commands:**

```bash
# Markdown report (human-readable)
/routing-bill --domain market-research --period 7d

# CSV export (spreadsheet)
/routing-bill --domain market-research --format csv --output report.csv

# Quicken QIF (Gnucash import)
/routing-bill --domain market-research --format quicken --output report.qif

# Custom date range
/routing-bill --domain market-research \
  --from 2026-05-01T09:00 \
  --to 2026-05-11T17:30
```

**Markdown Output Example:**
```markdown
## Billing Report

**Domain (Customer):** Acme Trading  
**Period:** 2026-05-01 09:00 to 2026-05-11 17:30 (10 days, 8 hours)

| Date/Time | Route | Model | Prompts | Input | Output | Time | Cost |
|-----------|-------|-------|---------|-------|--------|------|------|
| 2026-05-11 08:00-09:00 | monitoring | qwen3.5:4b | 45 | 12.4k | 23.7k | 0.8s avg | $0.00 |
| 2026-05-11 09:00-10:00 | reasoning | gemma4:e4b | 12 | 8.2k | 15.6k | 6.1s avg | $0.00 |
| 2026-05-10 14:00-15:00 | reasoning | kimi-k2.6:cloud | 3 | 2.3k | 4.5k | 14.8s avg | $0.18 |

**Totals:**
- **Prompts:** 60
- **Input Tokens:** 23.0k
- **Output Tokens:** 44.0k
- **Total Time:** 8m 23s (avg: 8.4s/prompt)
- **Total Cost:** $0.18
```

**Quicken QIF Format (for Gnucash):**
```qif
!Type:Cash
^Acme Trading - market-research

D2026/05/11
T-0.50
Pkimi-k2.6:cloud
M3 prompts via kimi-k2.6:cloud (reasoning)
^

D2026/05/11
T0.00
Pqwen3.5:4b
M45 prompts via qwen3.5:4b (monitoring)
^
```

---

### 4. Performance Analytics

```bash
# Show stats for last 7 days
/routing-stats --domain market-research --period 7d

# Show stats for last 30 days with trends
/routing-stats --period 30d --trend
```

**Output:**
```markdown
## Performance Analytics — market-research
**Period:** Last 7 days
**Total Prompts:** 323

### By Route

| Route | Prompts | Avg Time | P95 | P99 | Total Cost |
|-------|---------|----------|-----|-----|------------|
| monitoring | 234 | 0.80s | 1.20s | 2.10s | $0.00 |
| reasoning | 89 | 6.20s | 8.90s | 12.30s | $0.00 |

### By Model

| Model | Prompts | Avg Time | P95 | P99 | Total Cost |
|-------|---------|----------|-----|-----|------------|
| qwen3.5:4b | 312 | 0.80s | 1.20s | 2.10s | $0.00 |
| gemma4:e4b | 145 | 6.20s | 8.90s | 12.30s | $0.00 |
| kimi-k2.6:cloud | 23 | 14.50s | 22.10s | 31.20s | $1.38 |

**Recommendations:**
- ⚠️ `reasoning` route using cloud models 26% of the time — consider local fallback
- ✅ `monitoring` route 100% local — optimal cost efficiency
- 📈 Prompt volume up 12% vs. last week, cost down 5% (good optimization)
```

---

### 5. CLI Commands

| Command | Description |
|---------|-------------|
| `/routing-status` | Current routing state + historical averages |
| `/routing-log [--limit N] [--route NAME] [--domain NAME]` | View recent decisions |
| `/routing-bill --domain NAME [--format markdown\|csv\|quicken]` | Billing report |
| `/routing-stats [--domain NAME] [--period 7d\|30d]` | Performance analytics |
| `/routing-test "your prompt"` | Test routing without executing |

---

## Installation

### From GitHub (Private Repo)

```bash
pi install git:git@github.com:carlosfrias/pi-routing-transparency
```

### From Local Path (Development)

```bash
cd /Users/friasc/Dropbox/workshop
pi install ./technical-infrastructure/packages/routing-transparency
```

### Build from Source

```bash
cd technical-infrastructure/packages/routing-transparency
npm install
npm run build
npm test
```

---

## Configuration

### keyword-router.json

Configure in `~/.pi/agent/keyword-router.json` or `<project>/.pi/keyword-router.json`:

```json
{
  "logging": {
    "enabled": true,
    "path": "~/.pi/logs/routing-decisions.jsonl",
    "maxAgeDays": 30,
    "compressAfterDays": 7,
    "includePrompt": true,
    "includeKeywords": true,
    "includeCost": true,
    "includeTiming": true
  },
  "billing": {
    "enabled": true,
    "domainMapping": {
      "market-research": {
        "customer": "Acme Trading",
        "contact": "trading@acme.com",
        "rateCard": "standard"
      },
      "position-monitor": {
        "customer": "Acme Trading",
        "contact": "trading@acme.com"
      },
      "position-management": {
        "customer": "Acme Trading",
        "contact": "trading@acme.com"
      },
      "bookkeeping": {
        "customer": "Internal Ops",
        "contact": "ops@internal.com",
        "rateCard": "internal"
      },
      "technical-infrastructure": {
        "customer": "Internal Ops",
        "contact": "ops@internal.com"
      }
    },
    "defaultDomain": "internal",
    "costPerRoute": {
      "monitoring": 0.00,
      "structured": 0.00,
      "reasoning": 0.00,
      "infrastructure": 0.00,
      "trivial": 0.00,
      "simple": 0.00,
      "medium": 0.00,
      "hard": 0.05
    },
    "costPerModel": {
      "qwen3.5:4b": { "input": 0, "output": 0 },
      "gemma4:e4b": { "input": 0, "output": 0 },
      "kimi-k2.6:cloud": { "input": 10.0, "output": 30.0 },
      "qwen3.5:397b-cloud": { "input": 2.0, "output": 6.0 }
    }
  },
  "analytics": {
    "enabled": true,
    "computePercentiles": true,
    "trendAnalysis": true,
    "recommendationsEnabled": true
  },
  "respectManualSelection": true,
  "notifyOnSwitch": true,
  "maxHistorySize": 1000
}
```

### Configuration Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `logging.enabled` | boolean | `true` | Enable JSONL logging |
| `logging.path` | string | `~/.pi/logs/routing-decisions.jsonl` | Log file path |
| `logging.maxAgeDays` | number | `30` | Delete logs older than N days |
| `logging.compressAfterDays` | number | `7` | Compress logs after N days |
| `logging.includePrompt` | boolean | `true` | Include prompt text in logs |
| `logging.includeKeywords` | boolean | `true` | Include matched keywords |
| `logging.includeCost` | boolean | `true` | Include cost data |
| `logging.includeTiming` | boolean | `true` | Include timing data |
| `billing.domainMapping` | object | `{}` | Domain → customer mapping |
| `billing.defaultDomain` | string | `"internal"` | Default domain for unmapped routes |
| `billing.costPerRoute` | object | `{}` | Fixed cost per route (optional) |
| `billing.costPerModel` | object | `{}` | Cost per million tokens by model |
| `analytics.enabled` | boolean | `true` | Enable performance analytics |
| `analytics.computePercentiles` | boolean | `true` | Calculate P95/P99 latencies |
| `analytics.trendAnalysis` | boolean | `true` | Compare periods (week-over-week) |
| `analytics.recommendationsEnabled` | boolean | `true` | Generate optimization recommendations |

---

## Usage Examples

### Check Current Routing State

```bash
/routing-status
```

**Output:**
```
## Current Routing State

**Active Route:** monitoring
**Model:** qwen3.5:4b (ollama)
**Thinking Level:** off
**Source:** keyword
**Domain:** position-monitor (Customer: Acme Trading)
**Matched Keywords:** [status, check]
**Complexity:** trivial (confidence: 82%)

**Timing:**
- This prompt: 1.2s
- Historical avg: 0.8s (last 100 prompts)
- P95: 1.5s, P99: 2.3s

**Cost:**
- This prompt: $0.00
- Session total: $0.003
- Domain total (today): $0.12
```

### View Routing Log

```bash
# Last 10 decisions
/routing-log

# Last 50 decisions
/routing-log --limit 50

# Filter by route
/routing-log --route monitoring

# Filter by domain/customer
/routing-log --domain market-research

# Filter by time range
/routing-log --from 2026-05-11T08:00 --to 2026-05-11T09:00

# Filter by minimum execution time
/routing-log --min-time 5s

# Filter by minimum cost
/routing-log --min-cost 0.01
```

### Generate Billing Report

```bash
# Last 7 days, markdown format
/routing-bill --domain market-research --period 7d

# Specific date range, CSV format
/routing-bill --domain market-research \
  --from 2026-05-01T00:00 \
  --to 2026-05-11T23:59 \
  --format csv \
  --output billing.csv

# Quicken QIF for Gnucash import
/routing-bill --domain market-research \
  --format quicken \
  --output billing.qif

# Include historical comparison
/routing-bill --domain market-research --period 7d --compare
```

### Performance Analytics

```bash
# Last 7 days
/routing-stats --domain market-research --period 7d

# Last 30 days with trends
/routing-stats --domain market-research --period 30d --trend

# All domains consolidated
/routing-stats --all-domains
```

### Test Routing

```bash
# Test how a prompt would be routed
/routing-test "check position status for AAPL"

# Test with domain override
/routing-test "deploy playbook to fnet2" --domain technical-infrastructure

# Show alternative routes considered
/routing-test "analyze trading signals" --show-alternatives
```

---

## Period Range Formats

All commands support flexible period ranges:

| Format | Example | Description |
|--------|---------|-------------|
| `--period 7d` | Last 7 days | Shorthand for days |
| `--period 2h` | Last 2 hours | Shorthand for hours |
| `--period 30m` | Last 30 minutes | Shorthand for minutes |
| `--from YYYY-MM-DD` | `2026-05-01` | Start date |
| `--from YYYY-MM-DDTHH:MM` | `2026-05-11T08:00` | Start datetime |
| `--to YYYY-MM-DDTHH:MM:SS` | `2026-05-11T17:30:00` | End datetime |

---

## Domain-to-Customer Mapping

Each domain maps to a customer for billing. Multiple domains can map to the same customer for consolidated billing.

**Example Configuration:**
```json
"billing": {
  "domainMapping": {
    "market-research": {
      "customer": "Acme Trading",
      "contact": "trading@acme.com"
    },
    "position-monitor": {
      "customer": "Acme Trading"
    },
    "position-management": {
      "customer": "Acme Trading"
    },
    "bookkeeping": {
      "customer": "Internal Ops"
    },
    "technical-infrastructure": {
      "customer": "Internal Ops"
    }
  }
}
```

**Billing Report Consolidation:**
When you run `/routing-bill --domain market-research`, it includes all prompts routed to the `market-research` domain. To get a consolidated report for Acme Trading across all their domains:

```bash
# Create a custom script or run multiple times
/routing-bill --domain market-research --format csv --output acme-market.csv
/routing-bill --domain position-monitor --format csv --output acme-monitor.csv
/routing-bill --domain position-management --format csv --output acme-positions.csv

# Then merge CSVs in spreadsheet
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User Prompt                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    pi-keyword-router                                     │
│  - Classifies prompt by keywords                                        │
│  - Selects route (monitoring, reasoning, etc.)                          │
│  - Selects model (qwen3.5:4b, gemma4:e4b, etc.)                         │
│  - Emits keyword-router:routed event                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 routing-transparency Extension                           │
│  - Listens to keyword-router:routed event                               │
│  - Updates TUI footer with routing info                                 │
│  - Logs decision to JSONL file                                          │
│  - Tracks cost and timing                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
          ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
          │ TUI Footer  │ │ JSONL Log   │ │ Commands    │
          │ Component   │ │ Writer      │ │ Handler     │
          │             │ │             │ │             │
          │ - 3 rows    │ │ - Audit     │ │ - status    │
          │ - R/W time  │ │ - Filtering │ │ - log       │
          │ - Route     │ │ - Rotation  │ │ - bill      │
          │ - Cost      │ │             │ │ - stats     │
          └─────────────┘ └─────────────┘ └─────────────┘
```

---

## Events

Dependent extensions can listen to these events on `pi.events`:

| Event | Payload | When |
|-------|---------|------|
| `routing-transparency:ready` | `{ config }` | Extension initialized |
| `routing-transparency:routed` | `{ decision, timestamp }` | Every routing decision |
| `routing-transparency:billing-export` | `{ report, format }` | Billing report generated |

**Example Listener:**
```typescript
pi.events.on('routing-transparency:routed', (data) => {
  console.log(`Routed to ${data.decision.route} on ${data.decision.model}`);
});
```

---

## Test Suite

```bash
cd technical-infrastructure/packages/routing-transparency
npm test
```

**Coverage:**
- ✅ 92 tests passing
- ✅ TUI footer rendering (33 tests)
- ✅ JSONL logging (16 tests)
- ✅ Billing report generation (13 tests)
- ✅ Command handlers (12 tests)
- ✅ Extension lifecycle (9 tests)
- ✅ Type safety (10 tests)

**Test Files:**
- `test/routing-footer.test.ts` — TUI footer component
- `test/logger.test.ts` — JSONL log writer
- `test/billing.test.ts` — Billing report generator
- `test/commands.test.ts` — CLI commands
- `test/extension.test.ts` — Extension lifecycle
- `test/types.test.ts` — TypeScript types

---

## Files

```
routing-transparency/
├── package.json                 # Extension metadata
├── tsconfig.json                # TypeScript config
├── README.md                    # User documentation
├── ROUTING-TRANSPARENCY-FIX.md  # Design document
├── src/
│   ├── index.ts                 # Extension entry point
│   ├── types.ts                 # TypeScript types
│   ├── routing-footer.ts        # TUI footer component
│   ├── logger.ts                # JSONL log writer
│   ├── billing.ts               # Billing report generator
│   └── commands.ts              # CLI commands
└── test/
    ├── README.md                # Test documentation
    ├── routing-footer.test.ts
    ├── logger.test.ts
    ├── billing.test.ts
    ├── commands.test.ts
    ├── extension.test.ts
    └── types.test.ts
```

---

## Troubleshooting

### Footer Not Showing

**Symptom:** TUI footer shows only 2 rows instead of 3.

**Solution:**
1. Check extension is installed: `pi extensions list`
2. Check for errors: `~/.pi/logs/pi.log`
3. Restart pi session

### Logs Not Being Written

**Symptom:** `~/.pi/logs/routing-decisions.jsonl` doesn't exist or is empty.

**Solution:**
1. Check `logging.enabled` is `true` in config
2. Check log directory exists: `mkdir -p ~/.pi/logs`
3. Check file permissions

### Billing Report Shows $0.00

**Symptom:** All costs show as $0.00 even for cloud models.

**Solution:**
1. Check `billing.costPerModel` is configured correctly
2. Verify model names match exactly (e.g., `kimi-k2.6:cloud` not `kimi-k2.6`)
3. Check `logging.includeCost` is `true`

### Domain Not Mapped to Customer

**Symptom:** Billing report shows domain name instead of customer name.

**Solution:**
1. Add domain to `billing.domainMapping` in config
2. Check domain name matches exactly (case-sensitive)
3. Restart pi session after config change

---

## Performance Impact

**Overhead:** <5ms per prompt

| Component | Avg Time | P95 | P99 |
|-----------|----------|-----|-----|
| Footer render | 0.5ms | 1.2ms | 2.1ms |
| JSONL log write | 1.8ms | 3.2ms | 5.1ms |
| Total overhead | 2.3ms | 4.4ms | 7.2ms |

**Memory:** ~5MB additional

---

## Security Considerations

### Log Privacy

**Current:** Logs are plaintext JSONL files in `~/.pi/logs/`.

**Recommendations:**
- Restrict file permissions: `chmod 600 ~/.pi/logs/routing-decisions.jsonl`
- Consider encryption for production use (future feature)
- Regular log rotation prevents excessive disk usage

### Customer Data

**Prompt Text:** If `logging.includePrompt` is `true`, full prompt text is logged.

**Recommendations:**
- Disable for sensitive prompts: `logging.includePrompt: false`
- Use domain mapping to segregate customer data
- Implement log access controls

---

## Future Enhancements

### Phase 6 (Planned)
- [ ] Real-time cost alerts (notify when daily budget exceeded)
- [ ] Multi-currency support
- [ ] Integration with accounting systems (QuickBooks, Xero)
- [ ] Encrypted log storage
- [ ] Web dashboard for billing analytics

### Backlog
- [ ] Customer portal for self-service billing
- [ ] Automated invoice generation
- [ ] Budget tracking per domain/customer
- [ ] Anomaly detection (unusual cost spikes)

---

## Related Documentation

- [pi-keyword-router](./pi-keyword-router.md) — Keyword-based model routing
- [local-model-pilot](./local-model-pilot.md) — Local LLM model routing
- [decomposition-skill](./decomposition-skill.md) — Task decomposition
- [Trading Desk Backlog](../../wiki/trading-desk/backlog.md) — Active backlog items

---

## Changelog

### v1.0.0 (2026-05-11)
- Initial release
- 3-row TUI footer
- JSONL audit trail
- Billing reports (Markdown/CSV/Quicken)
- 5 CLI commands
- 92 passing tests

---

## License

MIT

## Author

Carlos Frias — Trading Desk AI Workspace
