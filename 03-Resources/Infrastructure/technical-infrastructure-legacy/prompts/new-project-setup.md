# New Project Setup — Complete Configuration

**Purpose:** Single-prompt template to set up a complete AI-orchestrated project without interactive questions. Fill in the placeholders and paste into pi.

**Time to complete:** 5 minutes (fill in template) + 10 minutes (automated setup)

---

## Template (Copy and Fill In)

```markdown
Set up a new AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** <PROJECT_NAME>
**Project Description:** <PROJECT_DESCRIPTION>

Example:
- Project Name: Healthcare Analytics Lab
- Project Description: Healthcare analytics platform for patient outcomes research, billing optimization, and regulatory compliance reporting.

## Domains

Configure the following domains (add as many as needed):

### Domain 1
- **Name:** <DOMAIN_1_NAME>
- **Description:** <DOMAIN_1_DESCRIPTION>
- **Keywords (for routing):** <DOMAIN_1_KEYWORDS>
- **Primary Users:** <DOMAIN_1_USERS>

Example:
- Name: patient-records
- Description: Managing patient data, HIPAA compliance, and medical record integrity
- Keywords: patients, HIPAA, medical records, data privacy, compliance
- Primary Users: Healthcare administrators, compliance officers, data analysts

### Domain 2
- **Name:** <DOMAIN_2_NAME>
- **Description:** <DOMAIN_2_DESCRIPTION>
- **Keywords (for routing):** <DOMAIN_2_KEYWORDS>
- **Primary Users:** <DOMAIN_2_USERS>

Example:
- Name: billing
- Description: Insurance claims processing, invoicing, and revenue cycle management
- Keywords: claims, invoices, insurance, revenue, payments
- Primary Users: Billing specialists, insurance coordinators, finance team

### Domain 3 (Optional)
- **Name:** <DOMAIN_3_NAME>
- **Description:** <DOMAIN_3_DESCRIPTION>
- **Keywords (for routing):** <DOMAIN_3_KEYWORDS>
- **Primary Users:** <DOMAIN_3_USERS>

Example:
- Name: compliance
- Description: Regulatory audit trails, reporting, and policy enforcement
- Keywords: regulations, audit, reporting, policy, enforcement
- Primary Users: Compliance officers, auditors, legal team

## Wiki Configuration

**Wiki Location:** <WIKI_LOCATION> (default: ./wiki/)
**Build HTML Wiki:** <HTML_WIKI> (yes/no, default: yes)

Example:
- Wiki Location: ./wiki/
- Build HTML Wiki: yes

## Model Configuration

**Orchestrator Model:** <ORCHESTRATOR_MODEL> (default: current pi default)
**Sub-Agent Model (Reasoning):** <SUB_AGENT_MODEL> (default: anthropic/claude-sonnet-4)
**Sub-Agent Model (Fast):** <FAST_MODEL> (default: anthropic/claude-haiku-4-5)

Example:
- Orchestrator Model: ollama/gemma4:e4b
- Sub-Agent Model (Reasoning): anthropic/claude-sonnet-4
- Sub-Agent Model (Fast): anthropic/claude-haiku-4-5

## Intercom Configuration

**Sub-Agent Check-Back:** <CHECKBACK> (yes/no, default: yes)

Example:
- Sub-Agent Check-Back: yes

## Additional Requirements

<List any specific requirements, constraints, or preferences>

Examples:
- "All agents should use the delegate pattern with intercom check-back"
- "Create chain files for common workflows between domain1 and domain2"
- "Include sample prompts in the wiki for non-technical users"
- "Optimize for local LLM execution where possible"

---

## Instructions for the Agent

Please create the complete project structure including:

1. **Root AGENTS.md** — Identity + routing table with all domains
2. **.pi/APPEND_SYSTEM.md** — Project identity only
3. **Domain AGENTS.md files** — One per domain with conventions, rules, QC
4. **Agent definitions** — One per domain in .pi/agents/ with intercom
5. **Chain files** — For multi-step workflows between domains
6. **Wiki structure** — Home page, architecture docs, domain sub-wikis
7. **Sample prompts** — Ready-to-use prompts for each domain

Follow the project-blueprint skill instructions for the complete 10-phase setup process.

After creation, verify:
- Token budget: orchestrator < 2KB permanent, sub-agents < 6KB per invocation
- All routing table entries point to existing AGENTS.md files
- All agent definitions have inheritProjectContext: false and correct cwd
- Wiki navigation links all pages
```

---

## Quick Fill-In Guide

### For Trading Projects

```
Project Name: Trading Laboratory
Project Description: Systematic trading workspace for stocks, options, and futures with automated bookkeeping and risk management

Domain 1:
- Name: bookkeeping
- Description: Trade logging, reconciliation, P&L calculation, and audit trails
- Keywords: trades, reconciliation, P&L, ledger, fills, executions
- Users: Trade analysts, accountants, auditors

Domain 2:
- Name: position-management
- Description: Position sizing, order execution, risk controls, portfolio allocation
- Keywords: positions, orders, risk, sizing, allocation, stops
- Users: Traders, risk managers, portfolio managers

Domain 3:
- Name: market-research
- Description: Signal generation, backtesting, market analysis, sentiment research
- Keywords: signals, backtesting, analysis, sentiment, research
- Users: Quant researchers, analysts, strategists

Wiki: ./wiki/
HTML Wiki: yes
Models: ollama/gemma4:e4b (orchestrator), anthropic/claude-sonnet-4 (sub-agents)
Check-Back: yes
```

### For Healthcare Projects

```
Project Name: Healthcare Analytics Lab
Project Description: Healthcare analytics platform for patient outcomes research, billing optimization, and regulatory compliance

Domain 1:
- Name: patient-records
- Description: Managing patient data, HIPAA compliance, medical record integrity
- Keywords: patients, HIPAA, medical records, data privacy, compliance
- Users: Healthcare administrators, compliance officers, data analysts

Domain 2:
- Name: billing
- Description: Insurance claims processing, invoicing, revenue cycle management
- Keywords: claims, invoices, insurance, revenue, payments
- Users: Billing specialists, insurance coordinators, finance team

Domain 3:
- Name: compliance
- Description: Regulatory audit trails, reporting, policy enforcement
- Keywords: regulations, audit, reporting, policy, enforcement
- Users: Compliance officers, auditors, legal team

Wiki: ./wiki/
HTML Wiki: yes
Models: ollama/gemma4:e4b (orchestrator), anthropic/claude-sonnet-4 (sub-agents)
Check-Back: yes
```

### For Legal Projects

```
Project Name: Legal Practice Management
Project Description: Law firm practice management with case tracking, client billing, and document review automation

Domain 1:
- Name: case-management
- Description: Case tracking, client communications, court deadlines, matter management
- Keywords: cases, clients, deadlines, matters, litigation
- Users: Attorneys, paralegals, legal assistants

Domain 2:
- Name: billing
- Description: Time tracking, client invoicing, trust accounting, payment processing
- Keywords: time, invoices, trust, payments, retainer
- Users: Billing specialists, accountants, managing partners

Domain 3:
- Name: document-review
- Description: Document analysis, discovery, contract review, legal research
- Keywords: documents, discovery, contracts, research, review
- Users: Attorneys, paralegals, legal researchers

Wiki: ./wiki/
HTML Wiki: yes
Models: ollama/gemma4:e4b (orchestrator), anthropic/claude-sonnet-4 (sub-agents)
Check-Back: yes
```

### For E-commerce Projects

```
Project Name: E-commerce Operations
Project Description: Online store operations with inventory management, order processing, and customer support automation

Domain 1:
- Name: inventory
- Description: Stock tracking, supplier management, reorder alerts, warehouse operations
- Keywords: inventory, stock, suppliers, warehouse, reorder
- Users: Inventory managers, warehouse staff, procurement

Domain 2:
- Name: orders
- Description: Order processing, fulfillment, shipping, returns management
- Keywords: orders, fulfillment, shipping, returns, tracking
- Users: Order processors, fulfillment staff, customer service

Domain 3:
- Name: customer-support
- Description: Customer inquiries, ticket management, returns, feedback analysis
- Keywords: customers, tickets, support, returns, feedback
- Users: Customer service reps, support managers

Wiki: ./wiki/
HTML Wiki: yes
Models: ollama/gemma4:e4b (orchestrator), anthropic/claude-sonnet-4 (sub-agents)
Check-Back: yes
```

---

## How to Use

### Option 1: Copy from Wiki

1. Open this file in your browser or editor
2. Copy the template section (between the markdown code blocks)
3. Fill in the placeholders
4. Paste into pi

### Option 2: Use the Script

```bash
# The setup script can read from this template
./project-blueprint-setup.sh --template new-project-setup.md
```

### Option 3: Interactive + Template Hybrid

1. Run the interactive setup script: `./project-blueprint-setup.sh --interactive`
2. Use the template to prepare your answers in advance
3. Copy-paste from template during interactive session

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

---

## After Running This Prompt

The agent will create:

```
<project-root>/
├── AGENTS.md                          # ~1.2 KB (identity + routing)
├── .pi/
│   ├── APPEND_SYSTEM.md               # ~200 B (identity)
│   └── agents/                        # Agent definitions + chains
│       ├── <domain1>.md
│       ├── <domain2>.md
│       ├── <domain1>-to-<domain2>.chain.md
│       └── ...
├── <domain1>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
├── <domain2>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
└── wiki/
    └── <project-name>/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        ├── <domain1>/
        │   └── Activity Log.md
        └── <domain2>/
            └── Activity Log.md
```

**Token Budget:**
- Orchestrator (permanent): ~1.2 KB
- Sub-agent (per invocation): ~4-5 KB
- No redundancy between orchestrator and sub-agents

---

## Troubleshooting

**Problem:** Agent asks follow-up questions

**Solution:** The template should have all required information. If the agent asks for clarification, provide the missing detail and it will continue.

**Problem:** Setup fails partway through

**Solution:** Run the prompt again. The agent will detect existing files and continue from where it left off.

**Problem:** Wrong model names

**Solution:** Check available models with `pi list models` and update the template.

---

## See Also

- [Quick Start Guide](../wiki/quick-start.md) — Complete step-by-step setup instructions
- [Setup Script](../scripts/project-blueprint-setup.sh) — Automated setup automation
- [Project Blueprint Skill](https://github.com/carlosfrias/project-blueprint) — The underlying skill
