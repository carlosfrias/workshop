# Setup Wizard Template — Complete Project Configuration

**Purpose:** Single-file prompt that answers all setup wizard questions. Fill in the placeholders and paste into pi. No interactive back-and-forth needed.

**Time:** 5 minutes to fill in + 10 minutes automated setup

---

## Template (Copy and Fill In)

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** <PROJECT_NAME>

**Project Description:** <PROJECT_DESCRIPTION>

---

## Domain Configuration

Add one row per domain. Duplicate the row structure for each additional domain.

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| <DOMAIN_1_NAME> | <DOMAIN_1_DESCRIPTION> | <DOMAIN_1_KEYWORDS> | <DOMAIN_1_USERS> |
| <DOMAIN_2_NAME> | <DOMAIN_2_DESCRIPTION> | <DOMAIN_2_KEYWORDS> | <DOMAIN_2_USERS> |
| <DOMAIN_3_NAME> | <DOMAIN_3_DESCRIPTION> | <DOMAIN_3_KEYWORDS> | <DOMAIN_3_USERS> |

---

## Wiki Configuration

**Wiki Location:** <WIKI_LOCATION> (default: ./wiki/)

**Build HTML Wiki:** <HTML_WIKI> (yes or no, default: yes)

---

## Model Configuration

**Orchestrator Model:** <ORCHESTRATOR_MODEL> (default: current pi default)

**Sub-Agent Model for Reasoning:** <SUB_AGENT_MODEL> (default: anthropic/claude-sonnet-4)

**Sub-Agent Model for Fast Tasks:** <FAST_MODEL> (default: anthropic/claude-haiku-4-5)

---

## Intercom Configuration

**Sub-Agent Check-Back:** <CHECKBACK> (yes or no, default: yes)

**Check-Back Triggers:** <TRIGGERS> (e.g., decisions on ambiguous requirements, risk limit breaches, unexpected findings)

---

## Chain Workflows

**Chain 1 Name:** <CHAIN_1_NAME>

**Chain 1 Steps:** <CHAIN_1_STEP_1> → <CHAIN_1_STEP_2> → <CHAIN_1_STEP_3>

**Chain 1 Purpose:** <CHAIN_1_PURPOSE>

**Chain 2 Name:** <CHAIN_2_NAME>

**Chain 2 Steps:** <CHAIN_2_STEP_1> → <CHAIN_2_STEP_2>

**Chain 2 Purpose:** <CHAIN_2_PURPOSE>

---

## Additional Requirements

<List any specific requirements, constraints, or preferences>

Examples:
- All agents should use the delegate pattern with intercom check-back
- Create chain files for common workflows between domains
- Include sample prompts in the wiki for non-technical users
- Optimize for local LLM execution where possible

---

## Instructions for the Agent

Please create the complete project structure including:

1. Root AGENTS.md with identity and routing table for all domains listed above
2. .pi/APPEND_SYSTEM.md with project identity only
3. Domain AGENTS.md files — one per domain with conventions, rules, and QC checklists
4. Agent definitions in .pi/agents/ — one per domain with intercom configuration
5. Chain files for the workflows specified above
6. Wiki structure with home page, architecture docs, and domain sub-wikis
7. Sample prompts for each domain

Follow the project-blueprint skill instructions for the complete 10-phase setup process.

After creation, verify:
- Token budget: orchestrator under 2KB permanent, sub-agents under 6KB per invocation
- All routing table entries point to existing AGENTS.md files
- All agent definitions have inheritProjectContext: false and correct cwd
- Wiki navigation links all pages
- Chain files reference valid agents
```

---

## Placeholder Reference

**<PROJECT_NAME>** — Title Case, no spaces  
Example: `Healthcare Analytics Lab`

**<PROJECT_DESCRIPTION>** — 1-2 sentences  
Example: `Healthcare analytics for patient outcomes and billing`

**<DOMAIN_NAME>** — lowercase, hyphenated  
Examples: `patient-records`, `bookkeeping`

**<DOMAIN_DESCRIPTION>** — 1 sentence  
Example: `Managing patient data and HIPAA compliance`

**<DOMAIN_KEYWORDS>** — comma-separated  
Example: `patients, HIPAA, records, compliance`

**<DOMAIN_USERS>** — role descriptions  
Example: `Healthcare administrators, compliance officers`

**<WIKI_LOCATION>** — relative path  
Example: `./wiki/`

**<HTML_WIKI>** — yes or no  
Example: `yes`

**<ORCHESTRATOR_MODEL>** — model identifier  
Example: `ollama/gemma4:e4b`

**<SUB_AGENT_MODEL>** — model identifier  
Example: `anthropic/claude-sonnet-4`

**<FAST_MODEL>** — model identifier  
Example: `anthropic/claude-haiku-4-5`

**<CHECKBACK>** — yes or no  
Example: `yes`

**<CHAIN_NAME>** — lowercase, hyphenated  
Examples: `signal-to-trade`, `patient-to-billing`

---

## Complete Examples

### Example 1: Trading Project

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** Trading Laboratory

**Project Description:** Systematic trading workspace for stocks, options, and futures with automated bookkeeping and risk management

---

## Domain Configuration

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| bookkeeping | Trade logging, reconciliation, P&L calculation, and audit trails | trades, reconciliation, P&L, ledger, fills, executions | Trade analysts, accountants, auditors |
| position-management | Position sizing, order execution, risk controls, portfolio allocation | positions, orders, risk, sizing, allocation, stops | Traders, risk managers, portfolio managers |
| market-research | Signal generation, backtesting, market analysis, sentiment research | signals, backtesting, analysis, sentiment, research | Quant researchers, analysts, strategists |

---

## Wiki Configuration

**Wiki Location:** ./wiki/

**Build HTML Wiki:** yes

---

## Model Configuration

**Orchestrator Model:** ollama/gemma4:e4b

**Sub-Agent Model for Reasoning:** anthropic/claude-sonnet-4

**Sub-Agent Model for Fast Tasks:** anthropic/claude-haiku-4-5

---

## Intercom Configuration

**Sub-Agent Check-Back:** yes

**Check-Back Triggers:** Decisions on ambiguous requirements, risk limit breaches, threshold violations, unexpected findings

---

## Chain Workflows

**Chain 1 Name:** signal-to-trade

**Chain 1 Steps:** market-research → position-management

**Chain 1 Purpose:** Research signal, then evaluate and size position

**Chain 2 Name:** trade-to-log

**Chain 2 Steps:** position-management → bookkeeping

**Chain 2 Purpose:** Execute trade, then log in ledger

**Chain 3 Name:** full-trade-cycle

**Chain 3 Steps:** market-research → position-management → bookkeeping

**Chain 3 Purpose:** End-to-end from signal to ledger entry

---

## Additional Requirements

All agents should use the delegate pattern with intercom check-back. Include sample prompts in the wiki for non-technical users.
```

---

### Example 2: Healthcare Project

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** Healthcare Analytics Lab

**Project Description:** Healthcare analytics platform for patient outcomes research, billing optimization, and regulatory compliance

---

## Domain Configuration

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| patient-records | Managing patient data, HIPAA compliance, medical record integrity | patients, HIPAA, medical records, data privacy, compliance | Healthcare administrators, compliance officers, data analysts |
| billing | Insurance claims processing, invoicing, revenue cycle management | claims, invoices, insurance, revenue, payments | Billing specialists, insurance coordinators, finance team |
| compliance | Regulatory audit trails, reporting, policy enforcement | regulations, audit, reporting, policy, enforcement | Compliance officers, auditors, legal team |

---

## Wiki Configuration

**Wiki Location:** ./wiki/

**Build HTML Wiki:** yes

---

## Model Configuration

**Orchestrator Model:** ollama/gemma4:e4b

**Sub-Agent Model for Reasoning:** anthropic/claude-sonnet-4

**Sub-Agent Model for Fast Tasks:** anthropic/claude-haiku-4-5

---

## Intercom Configuration

**Sub-Agent Check-Back:** yes

**Check-Back Triggers:** HIPAA compliance issues, decisions on ambiguous requirements, regulatory violations, unexpected findings

---

## Chain Workflows

**Chain 1 Name:** patient-to-billing

**Chain 1 Steps:** patient-records → billing

**Chain 1 Purpose:** Process patient intake, generate billing records

**Chain 2 Name:** compliance-audit

**Chain 2 Steps:** patient-records → compliance

**Chain 2 Purpose:** Audit patient records for HIPAA compliance

**Chain 3 Name:** claims-processing

**Chain 3 Steps:** billing → compliance

**Chain 3 Purpose:** Process insurance claims with compliance check

---

## Additional Requirements

Add HIPAA compliance checklist to patient-records domain AGENTS.md. All agents should check back on compliance-related decisions.
```

---

### Example 3: Legal Project

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** Legal Practice Management

**Project Description:** Law firm practice management with case tracking, client billing, and document review automation

---

## Domain Configuration

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| case-management | Case tracking, client communications, court deadlines, matter management | cases, clients, deadlines, matters, litigation | Attorneys, paralegals, legal assistants |
| billing | Time tracking, client invoicing, trust accounting, payment processing | time, invoices, trust, payments, retainer | Billing specialists, accountants, managing partners |
| document-review | Document analysis, discovery, contract review, legal research | documents, discovery, contracts, research, review | Attorneys, paralegals, legal researchers |

---

## Wiki Configuration

**Wiki Location:** ./wiki/

**Build HTML Wiki:** yes

---

## Model Configuration

**Orchestrator Model:** ollama/gemma4:e4b

**Sub-Agent Model for Reasoning:** anthropic/claude-sonnet-4

**Sub-Agent Model for Fast Tasks:** anthropic/claude-haiku-4-5

---

## Intercom Configuration

**Sub-Agent Check-Back:** yes

**Check-Back Triggers:** Decisions on case strategy, billing disputes, privilege issues, court deadline conflicts

---

## Chain Workflows

**Chain 1 Name:** intake-to-case

**Chain 1 Steps:** case-management → billing

**Chain 1 Purpose:** New client intake, create case and billing record

**Chain 2 Name:** document-review-workflow

**Chain 2 Steps:** document-review → case-management

**Chain 2 Purpose:** Review discovery documents, update case file

---

## Additional Requirements

Include sample prompts for common legal workflows. All billing-related decisions should trigger intercom check-back.
```

---

### Example 4: E-commerce Project

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## Project Identity

**Project Name:** E-commerce Operations

**Project Description:** Online store operations with inventory management, order processing, and customer support automation

---

## Domain Configuration

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| inventory | Stock tracking, supplier management, reorder alerts, warehouse operations | inventory, stock, suppliers, warehouse, reorder | Inventory managers, warehouse staff, procurement |
| orders | Order processing, fulfillment, shipping, returns management | orders, fulfillment, shipping, returns, tracking | Order processors, fulfillment staff, customer service |
| customer-support | Customer inquiries, ticket management, returns, feedback analysis | customers, tickets, support, returns, feedback | Customer service reps, support managers |

---

## Wiki Configuration

**Wiki Location:** ./wiki/

**Build HTML Wiki:** yes

---

## Model Configuration

**Orchestrator Model:** ollama/gemma4:e4b

**Sub-Agent Model for Reasoning:** anthropic/claude-sonnet-4

**Sub-Agent Model for Fast Tasks:** anthropic/claude-haiku-4-5

---

## Intercom Configuration

**Sub-Agent Check-Back:** yes

**Check-Back Triggers:** Low stock alerts, high-value order decisions, customer escalation, return policy exceptions

---

## Chain Workflows

**Chain 1 Name:** order-fulfillment

**Chain 1 Steps:** orders → inventory

**Chain 1 Purpose:** Process order, update inventory

**Chain 2 Name:** return-processing

**Chain 2 Steps:** customer-support → inventory → orders

**Chain 2 Purpose:** Handle return, restock item, update order

---

## Additional Requirements

Include escalation procedures for high-value orders. All return policy exceptions should trigger intercom check-back.
```

---

## How to Use

### Option 1: Copy from File

```bash
# Open the template
cat technical-infrastructure/prompts/setup-wizard-template.md

# Copy the template section (between the markdown code blocks at the top)
# Fill in your details
# Paste into pi
```

### Option 2: Download from GitHub

```bash
curl -O https://raw.githubusercontent.com/carlosfrias/trading-workspace/main/technical-infrastructure/prompts/setup-wizard-template.md
```

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
│       ├── <chain1>.chain.md
│       └── ...
├── <domain1>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
├── <domain2>/
│   └── AGENTS.md                       # ~2-3 KB (self-contained)
└── wiki/
    └── <project-name>/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        └── <domain>/
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

**Problem:** Need to add a domain later

**Solution:** Use the domain management command:
```
Add a <domain-name> domain for <description> with keywords: <keywords>
```

---

## See Also

- [Quick Start Guide](../wiki/quick-start.md) — Complete step-by-step instructions
- [Setup Script](../scripts/project-blueprint-setup.sh) — Automated setup automation
- [Ollama Setup](../wiki/ollama-setup.md) — Local LLM installation and configuration
- [Project Blueprint Skill](https://github.com/carlosfrias/project-blueprint) — The underlying skill
