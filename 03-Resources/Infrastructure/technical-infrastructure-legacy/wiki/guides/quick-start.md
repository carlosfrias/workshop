# Quick Start

**LEGACY — MIGRATE TO:** `personal-vault/03-Resources/Technical-Infrastructure/quick-start.md`: Fresh Project Setup

Complete step-by-step guide to set up a new AI-orchestrated project from scratch. Works for **any domain** (trading, healthcare, finance, legal, etc.).

**Time:** 10-15 minutes  
**Prerequisites:** pi installed, Node.js 18+, git (optional)

---

## Overview

This guide walks you through:

1. Creating a fresh project directory
2. Installing required packages (project-blueprint skill, extensions)
3. Running the interactive setup wizard
4. Configuring your domains
5. Verifying everything works

**No prior knowledge required.** The setup wizard asks questions and generates everything automatically.

---

## Step 1: Create Project Directory

```bash
# Choose a name for your project
PROJECT_NAME="my-project"

# Create the directory
mkdir -p ~/projects/$PROJECT_NAME
cd ~/projects/$PROJECT_NAME

# Initialize git (optional but recommended)
git init
```

---

## Step 2: Install Required Packages

### Option A: Install from npm (Recommended for Stability)

```bash
# Install the project-blueprint skill
pi install npm:project-blueprint

# Install required extensions
pi install npm:pi-subagents
pi install npm:pi-intercom
pi install npm:@yeliu84/pi-model-router
```

### Option B: Install from GitHub (Latest Version)

```bash
# Install the project-blueprint skill
pi install git:github.com/carlosfrias/project-blueprint

# Install required extensions
pi install npm:pi-subagents
pi install npm:pi-intercom
pi install npm:@yeliu84/pi-model-router
```

### Verify Installation

```bash
# List installed packages
pi list packages

# You should see:
# - project-blueprint (skill)
# - pi-subagents (extension)
# - pi-intercom (extension)
# - @yeliu84/pi-model-router (extension)
```

---

## Step 3: Run the Setup Wizard

The project-blueprint skill includes an interactive agent that asks questions and generates your project structure.

### Option A: Use the Template Prompt (Recommended)

**📥 Download Template:** `setup-wizard-template.md`

Copy and fill in the template at `technical-infrastructure/prompts/setup-wizard-template.md`:

```bash
# Open the template
cat ../technical-infrastructure/prompts/setup-wizard-template.md

# Copy the template section, fill in the placeholders, then paste into pi
```

**Key Feature:** Domain configuration uses a simple table where you add one row per domain. All other sections use simple fill-in-the-blank format.

---

### Example: Trading Workspace Configuration

**📥 Download the template first:** `setup-wizard-template.md`

Below is a complete example using the trading-workspace domains. Use this as a guide when filling in your own template.

**Project Identity:**
- **Project Name:** Trading Laboratory
- **Project Description:** Systematic trading workspace for stocks, options, and futures with automated bookkeeping and risk management

**Domain Configuration:**

| Domain Name | Description | Keywords (for routing) | Primary Users |
|-------------|-------------|------------------------|---------------|
| bookkeeping | Trade logging, reconciliation, P&L calculation, and audit trails | trades, reconciliation, P&L, ledger, fills, executions | Trade analysts, accountants, auditors |
| position-management | Position sizing, order execution, risk controls, portfolio allocation | positions, orders, risk, sizing, allocation, stops, exits | Traders, risk managers, portfolio managers |
| market-research | Signal generation, backtesting, market analysis, sentiment research | signals, backtesting, analysis, sentiment, research, data | Quant researchers, analysts, strategists |

**Wiki Configuration:**
- **Wiki Location:** ./wiki/
- **Build HTML Wiki:** yes

**Model Configuration:**
- **Orchestrator Model:** ollama/gemma4:e4b
- **Sub-Agent Model for Reasoning:** anthropic/claude-sonnet-4
- **Sub-Agent Model for Fast Tasks:** anthropic/claude-haiku-4-5

**Intercom Configuration:**
- **Sub-Agent Check-Back:** yes
- **Check-Back Triggers:** Decisions on ambiguous requirements, risk limit breaches, threshold violations, unexpected findings

**Chain Workflows:**
- **Chain 1 Name:** signal-to-trade
- **Chain 1 Steps:** market-research → position-management
- **Chain 1 Purpose:** Research signal, then evaluate and size position

- **Chain 2 Name:** trade-to-log
- **Chain 2 Steps:** position-management → bookkeeping
- **Chain 2 Purpose:** Execute trade, then log in ledger

- **Chain 3 Name:** full-trade-cycle
- **Chain 3 Steps:** market-research → position-management → bookkeeping
- **Chain 3 Purpose:** End-to-end from signal to ledger entry

**Additional Requirements:**
All agents should use the delegate pattern with intercom check-back. Include sample prompts in the wiki for non-technical users.

---

**To use this example:**

1. **📥 Download the template:** `setup-wizard-template.md`
2. **Copy the template section** (between the markdown code blocks at the top of the file)
3. **Fill in your details** using the trading-workspace example above as a guide
4. **Paste into pi** — the agent will create your complete project structure

### Option B: Interactive Wizard

In pi, run:

```
Set up a new project for my <domain> with <features>
```

**Examples:**

| Domain | Prompt |
|--------|--------|
| **Trading** | "Set up a new project for my trading laboratory with bookkeeping, position management, and market research" |
| **Healthcare** | "Set up a new project for my healthcare analytics with patient records, billing, and compliance" |
| **Legal** | "Set up a new project for my law firm with case management, billing, and document review" |
| **E-commerce** | "Set up a new project for my online store with inventory, orders, and customer support" |

### The Wizard Asks

The agent will ask you these questions:

1. **Project name** — Used for wiki title and root identity
2. **Project description** — One or two sentences
3. **Domains** — For each domain:
   - Domain name (lowercase, e.g., `bookkeeping`, `compliance`)
   - Domain description (1-2 sentences)
   - Domain keywords (for routing, e.g., "trade logging, reconciliation")
   - Who uses this domain? (e.g., "trade analysts", "compliance officers")
4. **Wiki location** — Default: `./wiki/`
5. **HTML wiki** — Build browser-friendly version? Default: yes
6. **Models** — Which models for orchestrator and sub-agents? (defaults provided)
7. **Check-back behavior** — Should sub-agents check back via intercom? Default: yes

### Example Session

**📥 Download the Template:** `project-setup-template.md`

Below is a complete example of a filled-in template. Copy the template, fill in your details using this as a guide, and paste into pi.

<details>
<summary><strong>Click to expand: Example Filled Template (Healthcare Project)</strong></summary>

```markdown
Set up a complete AI-orchestrated project with the following configuration:

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Project Name** | Healthcare Analytics Lab |
| **Project Description** | Healthcare analytics platform for patient outcomes research, billing optimization, and regulatory compliance reporting |

---

## 2. Domain Configuration

| Domain | Name | Description | Keywords (for routing) | Primary Users |
|--------|------|-------------|------------------------|---------------|
| **Domain 1** | patient-records | Managing patient data, HIPAA compliance, medical record integrity | patients, HIPAA, medical records, data privacy, compliance | Healthcare administrators, compliance officers, data analysts |
| **Domain 2** | billing | Insurance claims processing, invoicing, revenue cycle management | claims, invoices, insurance, revenue, payments | Billing specialists, insurance coordinators, finance team |
| **Domain 3** | compliance | Regulatory audit trails, reporting, policy enforcement | regulations, audit, reporting, policy, enforcement | Compliance officers, auditors, legal team |

---

## 3. Wiki Configuration

| Field | Value |
|-------|-------|
| **Wiki Location** | ./wiki/ |
| **Build HTML Wiki** | yes |

---

## 4. Model Configuration

| Field | Value |
|-------|-------|
| **Orchestrator Model** | ollama/gemma4:e4b |
| **Sub-Agent Model (Reasoning)** | anthropic/claude-sonnet-4 |
| **Sub-Agent Model (Fast)** | anthropic/claude-haiku-4-5 |

---

## 5. Intercom Configuration

| Field | Value |
|-------|-------|
| **Sub-Agent Check-Back** | yes |
| **Check-Back Triggers** | Decisions on ambiguous requirements, HIPAA compliance issues, risk limit breaches, unexpected findings |

---

## 6. Chain Workflows

| Chain Name | Step 1 | Step 2 | Step 3 | Purpose |
|------------|--------|--------|--------|---------|
| patient-to-billing | patient-records | billing | — | Process patient intake, generate billing records |
| compliance-audit | patient-records | compliance | — | Audit patient records for HIPAA compliance |
| claims-processing | billing | compliance | — | Process insurance claims with compliance check |

---

## 7. Additional Requirements

- All agents should use the delegate pattern with intercom check-back
- Create chain files for common workflows between domains
- Include sample prompts in the wiki for non-technical users
- Add HIPAA compliance checklist to patient-records domain AGENTS.md

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

</details>

**To use this example:**

1. **Download the template:** `project-setup-template.md`
2. **Copy the template section** (between the markdown code blocks at the top of the file)
3. **Fill in your details** using the example above as a guide
4. **Paste into pi** — the agent will create your complete project structure

---

## Step 4: What Gets Created

After the wizard completes, your project structure looks like:

```
my-project/
├── AGENTS.md                          # Root: identity + routing table
├── .pi/
│   ├── APPEND_SYSTEM.md               # Identity only
│   └── agents/                        # Agent definitions + chains
│       ├── <domain1>.md
│       ├── <domain2>.md
│       ├── <domain1>-to-<domain2>.chain.md
│       └── ...
├── <domain1>/
│   └── AGENTS.md                       # Self-contained domain context
├── <domain2>/
│   └── AGENTS.md                       # Self-contained domain context
└── wiki/
    └── <project-name>/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        ├── <domain1>/
        │   └── Activity Log.md
        └── <domain2>/
            └── Activity Log.md
```

### Key Files

| File | Purpose | Size |
|------|---------|------|
| `AGENTS.md` (root) | Identity + routing table | ~1.2 KB |
| `.pi/APPEND_SYSTEM.md` | Identity only | ~200 B |
| `<domain>/AGENTS.md` | Domain context (rules, QC, conventions) | ~2-3 KB each |
| `.pi/agents/<domain>.md` | Agent definition with intercom | ~2 KB each |
| `.pi/agents/*.chain.md` | Multi-step workflows | ~500 B each |

---

## Step 5: Configure Your Domains

The wizard creates domains based on your answers. You can add, rename, or remove domains later.

### Add a Domain

```
Add a <domain-name> domain for <description> with keywords: <keyword1>, <keyword2>
```

**Example:**
```
Add a compliance domain for regulatory audit trails with keywords: regulations, audit, reporting
```

### Rename a Domain

```
Rename the <old-name> domain to <new-name>
```

**Example:**
```
Rename the bookkeeping domain to accounting
```

### Remove a Domain

```
Remove the <domain-name> domain
```

**Example:**
```
Remove the network domain
```

---

## Step 6: Verify Setup

### Check Routing Table

```bash
# Read the root AGENTS.md
cat AGENTS.md

# Look for the routing table:
## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| <your-domain-keywords> | `./<domain>/AGENTS.md` |
```

### Test a Sub-Agent

```
# Try a simple task in your first domain
<Domain-specific task, e.g., "Log a test transaction in the ledger">
```

### Check Intercom

```
# List active sessions
intercom({ action: "status" })

# Should show:
# Connected: Yes
# Session ID: <id>
```

### Verify Token Budget

```bash
# Orchestrator load (permanent)
wc -c AGENTS.md .pi/APPEND_SYSTEM.md
# Should be ~1.2 KB total

# Sub-agent load (per invocation)
wc -c <domain>/AGENTS.md
# Should be ~2-3 KB per domain
```

---

## Step 7: Start Using Your Project

### Example Workflows

#### Single Agent Task

```
<Domain task>
# e.g., "Reconcile today's transactions" (bookkeeping)
# e.g., "Review this contract for compliance issues" (legal)
```

#### Chain Workflow

```
/chain <domain1>-to-<domain2> <task>
# e.g., "/chain patient-to-billing Process a new patient intake"
```

#### Parallel Execution

```
/parallel <agent> "<task1>" -> <agent> "<task2>"
# e.g., "/parallel scout "Find all patient records" -> scout "Find all billing records""
```

---

## Troubleshooting

### Problem: "Skill not found: project-blueprint"

**Solution:**
```bash
pi install npm:project-blueprint
# or
pi install git:github.com/carlosfrias/project-blueprint
```

### Problem: "Extension not found: pi-subagents"

**Solution:**
```bash
pi install npm:pi-subagents
```

### Problem: Routing table not working

**Solution:**
1. Check `AGENTS.md` has a routing table section
2. Verify domain `AGENTS.md` files exist
3. Run `/reload` in pi

### Problem: Intercom not connecting

**Solution:**
```bash
# Check intercom config
cat ~/.pi/agent/intercom/config.json

# Should have:
{ "enabled": true, ... }

# Restart pi
```

---

## Next Steps

- **[Getting Started](getting-started.md)** — Overview of the workspace architecture
- **[Publishing Workflow](publishing-workflow.md)** — How to publish your own extensions
- **[Sub-Agent Packages Reference](../reference/subagent-packages-reference.md)** — pi-subagents vs pi-interactive-subagents
- **[Real-Time Control Patterns](../reference/real-time-control-patterns.md)** — Intercom ask/send patterns

---

## Quick Reference Card

```bash
# Create project
mkdir ~/projects/my-project && cd ~/projects/my-project
git init

# Install packages
pi install npm:project-blueprint
pi install npm:pi-subagents
pi install npm:pi-intercom
pi install npm:@yeliu84/pi-model-router

# Run setup wizard
"Set up a new project for my <domain> with <features>"

# Verify
cat AGENTS.md
pi list packages
intercom({ action: "status" })
```

---

## Support

- **GitHub Issues:** https://github.com/carlosfrias/project-blueprint/issues
- **Documentation:** This wiki
- **Community:** pi Discord server
