# Project Setup — Complete Configuration Template

**Purpose:** Single-file prompt template for complete AI-orchestrated project setup. Fill in the placeholders and paste into pi. No interactive questions needed.

**Time:** 5 minutes to fill in + 10 minutes automated setup

---

## Copy This Template

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Project Name** | <PROJECT_NAME> |
| **Project Description** | <PROJECT_DESCRIPTION> |

Example:
| Field | Value |
|-------|-------|
| **Project Name** | Healthcare Analytics Lab |
| **Project Description** | Healthcare analytics platform for patient outcomes research, billing optimization, and regulatory compliance reporting |

---

## 2. Domain Configuration

Add one row per domain. Duplicate the row structure for each additional domain.

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | <DOMAIN_1_NAME> | <DOMAIN_1_DESCRIPTION> | <DOMAIN_1_KEYWORDS> | <DOMAIN_1_USERS> |
| **Domain 2** | <DOMAIN_2_NAME> | <DOMAIN_2_DESCRIPTION> | <DOMAIN_2_KEYWORDS> | <DOMAIN_2_USERS> |
| **Domain 3** | <DOMAIN_3_NAME> | <DOMAIN_3_DESCRIPTION> | <DOMAIN_3_KEYWORDS> | <DOMAIN_3_USERS> |
| **Domain 4** (optional) | <DOMAIN_4_NAME> | <DOMAIN_4_DESCRIPTION> | <DOMAIN_4_KEYWORDS> | <DOMAIN_4_USERS> |

### Example: Trading Project

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | bookkeeping | Trade logging, reconciliation, P&L calculation, and audit trails | trades, reconciliation, P&L, ledger, fills, executions | Trade analysts, accountants, auditors |
| **Domain 2** | position-management | Position sizing, order execution, risk controls, portfolio allocation | positions, orders, risk, sizing, allocation, stops | Traders, risk managers, portfolio managers |
| **Domain 3** | market-research | Signal generation, backtesting, market analysis, sentiment research | signals, backtesting, analysis, sentiment, research | Quant researchers, analysts, strategists |

### Example: Healthcare Project

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | patient-records | Managing patient data, HIPAA compliance, medical record integrity | patients, HIPAA, medical records, data privacy, compliance | Healthcare administrators, compliance officers, data analysts |
| **Domain 2** | billing | Insurance claims processing, invoicing, revenue cycle management | claims, invoices, insurance, revenue, payments | Billing specialists, insurance coordinators, finance team |
| **Domain 3** | compliance | Regulatory audit trails, reporting, policy enforcement | regulations, audit, reporting, policy, enforcement | Compliance officers, auditors, legal team |

### Example: Legal Project

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | case-management | Case tracking, client communications, court deadlines, matter management | cases, clients, deadlines, matters, litigation | Attorneys, paralegals, legal assistants |
| **Domain 2** | billing | Time tracking, client invoicing, trust accounting, payment processing | time, invoices, trust, payments, retainer | Billing specialists, accountants, managing partners |
| **Domain 3** | document-review | Document analysis, discovery, contract review, legal research | documents, discovery, contracts, research, review | Attorneys, paralegals, legal researchers |

### Example: E-commerce Project

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | inventory | Stock tracking, supplier management, reorder alerts, warehouse operations | inventory, stock, suppliers, warehouse, reorder | Inventory managers, warehouse staff, procurement |
| **Domain 2** | orders | Order processing, fulfillment, shipping, returns management | orders, fulfillment, shipping, returns, tracking | Order processors, fulfillment staff, customer service |
| **Domain 3** | customer-support | Customer inquiries, ticket management, returns, feedback analysis | customers, tickets, support, returns, feedback | Customer service reps, support managers |

---

## 3. Wiki Configuration

| Field | Value |
|-------|-------|
| **Wiki Location** | <WIKI_LOCATION> (default: ./wiki/) |
| **Build HTML Wiki** | <HTML_WIKI> (yes/no, default: yes) |

Example:
| Field | Value |
|-------|-------|
| **Wiki Location** | ./wiki/ |
| **Build HTML Wiki** | yes |

---

## 4. Model Configuration

| Field | Value |
|-------|-------|
| **Orchestrator Model** | <ORCHESTRATOR_MODEL> (default: current pi default) |
| **Sub-Agent Model (Reasoning)** | <SUB_AGENT_MODEL> (default: anthropic/claude-sonnet-4) |
| **Sub-Agent Model (Fast)** | <FAST_MODEL> (default: anthropic/claude-haiku-4-5) |
| **Sub-Agent Model (Local)** | <LOCAL_MODEL> (optional, e.g., ollama/gemma4:e4b) |

Example (Cloud):
| Field | Value |
|-------|-------|
| **Orchestrator Model** | ollama/glm-5.1:cloud |
| **Sub-Agent Model (Reasoning)** | anthropic/claude-sonnet-4 |
| **Sub-Agent Model (Fast)** | anthropic/claude-haiku-4-5 |

Example (Local):
| Field | Value |
|-------|-------|
| **Orchestrator Model** | ollama/gemma4:e4b |
| **Sub-Agent Model (Reasoning)** | ollama/qwen3:14b |
| **Sub-Agent Model (Fast)** | ollama/qwen3.5:4b |

---

## 5. Intercom Configuration

| Field | Value |
|-------|-------|
| **Sub-Agent Check-Back** | <CHECKBACK> (yes/no, default: yes) |
| **Check-Back Triggers** | <TRIGGERS> (decisions, blockers, risk breaches, etc.) |

Example:
| Field | Value |
|-------|-------|
| **Sub-Agent Check-Back** | yes |
| **Check-Back Triggers** | Decisions on ambiguous requirements, risk limit breaches, threshold violations, unexpected findings |

---

## 6. Chain Workflows

Specify any multi-step workflows between domains. Add one row per chain.

| Chain Name | Step 1 | Step 2 | Step 3 | Purpose |
|------------|--------|--------|--------|---------|
| <CHAIN_1_NAME> | <CHAIN_1_STEP1> | <CHAIN_1_STEP2> | <CHAIN_1_STEP3> | <CHAIN_1_PURPOSE> |
| <CHAIN_2_NAME> | <CHAIN_2_STEP1> | <CHAIN_2_STEP2> | (optional) | <CHAIN_2_PURPOSE> |

### Example: Trading Chains

| Chain Name | Step 1 | Step 2 | Step 3 | Purpose |
|------------|--------|--------|--------|---------|
| signal-to-trade | market-research | position-management | — | Research signal, then evaluate and size position |
| trade-to-log | position-management | bookkeeping | — | Execute trade, then log in ledger |
| full-trade-cycle | market-research | position-management | bookkeeping | End-to-end from signal to ledger entry |
| post-trade-audit | bookkeeping | risk-analyst | reviewer | Reconcile trades, analyze risk, review accuracy |

### Example: Healthcare Chains

| Chain Name | Step 1 | Step 2 | Step 3 | Purpose |
|------------|--------|--------|--------|---------|
| patient-to-billing | patient-records | billing | — | Process patient intake, generate billing records |
| compliance-audit | patient-records | compliance | — | Audit patient records for HIPAA compliance |
| claims-processing | billing | compliance | — | Process insurance claims with compliance check |

---

## 7. Additional Requirements

<List any specific requirements, constraints, or preferences>

Examples:
- "All agents should use the delegate pattern with intercom check-back"
- "Create chain files for common workflows between domain1 and domain2"
- "Include sample prompts in the wiki for non-technical users"
- "Optimize for local LLM execution where possible"
- "Add decompose-execute-verify pattern chains for cost optimization"

---

## 8. Instructions for the Agent

Please create the complete project structure including:

1. **Root AGENTS.md** — Identity + routing table with all domains from the table above
2. **.pi/APPEND_SYSTEM.md** — Project identity only
3. **Domain AGENTS.md files** — One per domain row with conventions, rules, QC checklists
4. **Agent definitions** — One per domain in .pi/agents/ with intercom configuration
5. **Chain files** — For each chain workflow specified in the table above
6. **Wiki structure** — Home page, architecture docs, domain sub-wikis with activity logs
7. **Sample prompts** — Ready-to-use prompts for each domain

Follow the project-blueprint skill instructions for the complete 10-phase setup process.

After creation, verify:
- ✅ Token budget: orchestrator < 2KB permanent, sub-agents < 6KB per invocation
- ✅ All routing table entries point to existing AGENTS.md files
- ✅ All agent definitions have `inheritProjectContext: false` and correct `cwd`
- ✅ Wiki navigation links all pages
- ✅ Chain files reference valid agents

```

---

## Placeholder Reference

| Placeholder | Format | Example |
|-------------|--------|---------|
| `<PROJECT_NAME>` | Title Case, no spaces | `Healthcare Analytics Lab` |
| `<PROJECT_DESCRIPTION>` | 1-2 sentences | `Healthcare analytics for patient outcomes and billing` |
| `<DOMAIN_NAME>` | lowercase, hyphenated | `patient-records`, `bookkeeping` |
| `<DOMAIN_DESCRIPTION>` | 1 sentence | `Managing patient data and HIPAA compliance` |
| `<DOMAIN_KEYWORDS>` | comma-separated | `patients, HIPAA, records, compliance` |
| `<DOMAIN_USERS>` | role descriptions | `Healthcare administrators, compliance officers` |
| `<WIKI_LOCATION>` | relative path | `./wiki/` |
| `<HTML_WIKI>` | yes/no | `yes` |
| `<ORCHESTRATOR_MODEL>` | model identifier | `ollama/gemma4:e4b` |
| `<SUB_AGENT_MODEL>` | model identifier | `anthropic/claude-sonnet-4` |
| `<FAST_MODEL>` | model identifier | `anthropic/claude-haiku-4-5` |
| `<CHECKBACK>` | yes/no | `yes` |
| `<CHAIN_NAME>` | lowercase, hyphenated | `signal-to-trade`, `patient-to-billing` |

---

## How to Use

### Option 1: Copy from File

```bash
# Open the template
cat technical-infrastructure/prompts/project-setup-template.md

# Copy the template section (between the markdown code blocks)
# Fill in your details
# Paste into pi
```

### Option 2: Copy from Wiki

Open in your browser and copy the template section.

### Option 3: Use with Setup Script

```bash
# Fill in the template, save as my-project-config.md
# Then run:
./project-blueprint-setup.sh --template my-project-config.md
```

---

## After Running This Prompt

The agent will create:

```
<project-root>/
├── AGENTS.md                          # ~1.2 KB (identity + routing table)
├── .pi/
│   ├── APPEND_SYSTEM.md               # ~200 B (identity)
│   └── agents/                        # Agent definitions + chains
│       ├── <domain1>.md
│       ├── <domain2>.md
│       ├── <domain3>.md
│       ├── <chain1>.chain.md
│       ├── <chain2>.chain.md
│       └── ...
├── <domain1>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
├── <domain2>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
├── <domain3>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
└── wiki/
    └── <project-name>/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        ├── <domain1>/
        │   └── Activity Log.md
        ├── <domain2>/
        │   └── Activity Log.md
        └── <domain3>/
            └── Activity Log.md
```

**Token Budget:**
- Orchestrator (permanent): ~1.2 KB
- Sub-agent (per invocation): ~4-5 KB
- No redundancy between orchestrator and sub-agents

---

## Troubleshooting

**Problem:** Agent asks follow-up questions

**Solution:** The template should have all required information. If the agent asks for clarification, provide the missing detail from the placeholder reference and it will continue.

**Problem:** Setup fails partway through

**Solution:** Run the prompt again. The agent will detect existing files and continue from where it left off.

**Problem:** Need to add a domain later

**Solution:** Use the domain management commands:
```
Add a <domain-name> domain for <description> with keywords: <keywords>
```

---

## See Also

- [Quick Start Guide](../wiki/quick-start.md) — Complete step-by-step instructions
- [Setup Script](../scripts/project-blueprint-setup.sh) — Automated setup automation
- [Ollama Setup](../wiki/ollama-setup.md) — Local LLM installation and configuration
- [Project Blueprint Skill](https://github.com/carlosfrias/project-blueprint) — The underlying skill
