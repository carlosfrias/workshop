---
prompt_thread: active
---

# Project Blueprint

[![Status](https://img.shields.io/badge/status-ready-green)](https://github.com/carlosfrias/project-blueprint)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**Set up a new project with smart AI agents, organized folders, and built-in documentation — one command does it all.**

Project Blueprint is the **source of truth** for creating AI-orchestrated projects with structural routing, self-contained domains, and self-documenting wikis.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [Create a New Project](#create-a-new-project)
  - [Manage Domains](#manage-domains)
  - [Custom Agents](#custom-agents)
- [Architecture](#architecture)
- [What's Included](#whats-included)
- [Step-by-Step Guide](#step-by-step-guide)
- [Wiki Documentation](#wiki-documentation)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## What It Does

Project Blueprint sets up a complete AI-orchestrated project structure with:

### 1. Structural Routing
- **Routing table** in root `AGENTS.md` that any harness can follow (pi, Cursor, Claude Code, etc.)
- **Keyword-based dispatch** — No harness-specific configuration needed
- **Domain routing** — Automatic agent selection based on task keywords

### 2. Self-Contained Domains
- **One `AGENTS.md` per domain** — All context, rules, and quality checks in one file
- **No supplementary files** — Clean, maintainable structure
- **Domain isolation** — Each domain is independently understandable

### 3. Agent Definitions
- **`.pi/agents/` files** — Configurable per domain
- **`inheritProjectContext: false`** — Sub-agents discover context independently
- **`cwd` per domain** — Agents work in correct directory

### 4. Chain Files
- **Multi-step workflows** — Connect agents in pipelines
- **Reusable patterns** — Basic chains for common workflows
- **Template variables** — Pass context between steps

### 5. Wiki Documentation
- **Domain-centric** — Domains are the primary wiki content, not reference docs
- **Auto-generated** — Created during project setup
- **Activity logs** — Each domain tracks its own changes
- **Reference docs** — Architecture, agents, sample prompts in `_meta/` (reachable, non-central)
- **Sample prompts** — Ready-to-use examples

### 6. Minimal Orchestrator Load
- **~1.2KB permanent context** — Routing table only
- **~4-5KB per sub-agent invocation** — Domain context loaded on demand
- **No redundancy** — Context discovered, not inherited

---

## Quick Start

> 📖 **Prefer a standalone guide?** See [QUICKSTART.md](QUICKSTART.md) for a focused 5-minute walkthrough.

### Install

```bash
# From GitHub (recommended)
pi install git:git@github.com:carlosfrias/project-blueprint.git

# From GitHub (HTTPS)
pi install git:https://github.com/carlosfrias/project-blueprint.git

# From local path (development only)
pi install ./project-blueprint
```

### Create a New Project

```bash
# Navigate to your new project directory
cd ~/my-new-project

# Run project-blueprint
pi skill project-blueprint
```

The agent will:
1. Interview you about your project
2. Generate domain structure
3. Create agent definitions
4. Set up routing table
5. Build wiki documentation

### Manage Domains

```bash
# List all configured domains
/list-domain

# List with full metadata
/list-domain --verbose

# Add a new domain
/add-domain billing "invoice, payment, subscription, revenue"

# Rename a domain
/rename-domain auth authentication

# Remove a domain
/remove-domain legacy-module
```

---

## Installation

### Prerequisites

**Required**:
- ✅ **pi** installed with sub-agent support (v1.0+)
- ✅ **Git** (for version control, optional but recommended)

**Optional**:
- 📦 **Node.js** (v18+) — For HTML wiki build with VitePress
- 📦 **pi-model-router** extension — For automatic model routing (recommended)
- 📦 **pi-keyword-router** extension — For keyword-based routing (recommended for production)
- 📦 **find-skill** — For discovering and installing agent skills (recommended)
- 📦 **librarian** — For researching open-source libraries with citations (recommended)
- 📦 **decompose-execute-verify** — For cost-optimized task execution (recommended for high-volume)

### Dependency Installation

#### Step 1: Install pi (Required)

If you haven't installed pi yet:

```bash
# Install pi from official source
curl -fsSL https://pi.dev/install | sh

# Verify installation
pi --version
```

**Documentation**: [pi documentation](https://github.com/mariozechner/pi-coding-agent)

#### Step 2: Install pi-model-router Extension (Recommended)

For automatic model selection based on task complexity:

```bash
# Install the extension
pi install npm:@yeliu84/pi-model-router

# Configure in ~/.pi/agent/settings.json
{
  "defaultProvider": "router",
  "defaultModel": "auto"
}
```

**Documentation**: [pi-model-router](https://github.com/mariozechner/pi-coding-agent/blob/master/docs/model-router.md)

#### Step 3: Install project-blueprint

```bash
# From GitHub
pi install github:carlosfrias/project-blueprint

# Or from local path (development)
cd /path/to/agent-workspace/project-blueprint
pi install ./project-blueprint
```

#### Step 4: Install Optional Dependencies

**pi-keyword-router** (Recommended for production):
```bash
pi install github:carlosfrias/pi-keyword-router
```

Enables keyword-based model routing in your generated projects.

**Documentation**: [pi-keyword-router](https://github.com/carlosfrias/pi-keyword-router)

**decompose-execute-verify** (Recommended for high-volume usage):
```bash
pi install github:carlosfrias/decompose-execute-verify
```

Enables 75-85% cost reduction through decompose → execute → verify pattern.

**Documentation**: [decompose-execute-verify](https://github.com/carlosfrias/decompose-execute-verify)

**find-skill** (Recommended for skill discovery):
```bash
pi install github:carlosfrias/find-skill
```

Discover and install agent skills from curated registries.

**Documentation**: [find-skill](https://github.com/carlosfrias/find-skill)

**librarian** (Recommended for library research):
```bash
pi install github:carlosfrias/librarian
```

Research open-source libraries with evidence-backed answers and GitHub permalinks.

**Documentation**: [librarian](https://github.com/carlosfrias/librarian)

**Node.js** (For HTML wiki build):
```bash
# Install Node.js (v18+)
curl -fsSL https://nodejs.org/install.sh | sh

# Verify installation
node --version  # Should be v18 or higher
npm --version
```

### Verify Installation

```bash
# Check project-blueprint skill is installed
pi skill list | grep project-blueprint

# Check templates exist
ls ~/.pi/agent/skills/project-blueprint/templates/

# Should show:
# AGENTS-root.md  AGENTS-domain.md  agent.md  chain-basic.md
# wiki-home.md  wiki-activity-log.md  wiki-domain.md

# Check pi-model-router extension (if installed)
pi extension list | grep model-router
```

### Install Options

#### Option 1: Local Installation (Development)

```bash
cd /path/to/agent-workspace/project-blueprint
pi install ./project-blueprint
```

#### Option 2: GitHub Installation (Production)

```bash
pi install github:carlosfrias/project-blueprint
```

#### Option 3: npm Installation (When Published)

```bash
pi install npm:project-blueprint
```

### Verify Installation

```bash
# Check skill is installed
pi skill list | grep project-blueprint

# Check templates exist
ls ~/.pi/agent/skills/project-blueprint/templates/
```

---

## Usage

### Create a New Project

#### Method 1: Natural Language

```
"Set up a new project for my healthcare analytics platform with patient management, billing, and HIPAA compliance"
```

#### Method 2: Slash Command

```bash
/new-project healthcare analytics with billing and compliance
```

#### Method 3: Agent Invocation

```typescript
subagent({
  agent: "project-builder",
  task: "Create a new project for healthcare analytics with patient management, billing, and HIPAA compliance"
})
```

#### What Gets Created

```
my-healthcare-project/
├── AGENTS.md                    # Root routing table
├── .pi/
│   ├── APPEND_SYSTEM.md        # Identity file
│   └── agents/                  # Agent definitions
│       ├── patient-management.md
│       ├── billing.md
│       └── compliance.md
├── patient-management/
│   └── AGENTS.md                # Self-contained domain context
├── billing/
│   └── AGENTS.md
├── compliance/
│   └── AGENTS.md
└── wiki/
    └── my-healthcare-project/
        ├── Home.md              # Domain index + navigation
        ├── patient-management/ # Domain wiki — front and center
        │   └── Activity Log.md
        ├── billing/             # Domain wiki
        │   └── Activity Log.md
        ├── compliance/          # Domain wiki
        │   └── Activity Log.md
        └── _meta/              # Reference docs (reachable, non-central)
            ├── Architecture.md
            ├── Agent Definitions.md
            └── Sample Prompts.md
```

### Manage Domains

#### Add a Domain

```bash
/add-domain <name> <keywords>
```

**Example**:
```bash
/add-domain reporting "report, analytics, dashboard, metrics, kpi"
```

**What happens**:
1. Creates `reporting/` directory
2. Generates `reporting/AGENTS.md` with routing rules
3. Creates `reporting/` agent definition in `.pi/agents/`
4. Updates root `AGENTS.md` routing table
5. Adds wiki documentation
6. Creates sample chain (if applicable)

#### Rename a Domain

```bash
/rename-domain <old-name> <new-name>
```

**Example**:
```bash
/rename-domain auth authentication
```

**What happens**:
1. Renames directory from `auth/` to `authentication/`
2. Updates all references in routing table
3. Updates agent definitions
4. Updates wiki links
5. Updates chain files

#### Remove a Domain

```bash
/remove-domain <name>
```

**Example**:
```bash
/remove-domain legacy-module
```

**What happens**:
1. Prompts for confirmation
2. Removes domain directory
3. Removes from routing table
4. Removes agent definitions
5. Archives wiki documentation
6. Updates chains that referenced the domain

#### Integrate Wiki

Consolidates scattered or legacy wiki content into the domain-centric layout. Use when upgrading from an older project-blueprint version.

```bash
/integrate-wiki            # Scan and integrate
/integrate-wiki --scan-only  # Report findings only
```

**What happens** (without `--scan-only`):
1. Scans for numbered pages at wiki root (e.g., `01 — Philosophy & Architecture.md`)
2. Scans for wiki content inside domain folders (e.g., `./bookkeeping/wiki/`)
3. Moves numbered reference pages to `_meta/` (strips `NN — ` prefix)
4. Consolidates in-domain wiki content to `wiki/<project>/<domain>/`
5. Rebuilds `Home.md` for domain-centric layout
6. Updates VitePress config sidebar
7. Verifies all links are valid

#### Extract Domain

Extracts a domain as a self-contained package that can seed a new workspace. **Never modifies the original project** — read + copy only.

```bash
/extract-domain bookkeeping
/extract-domain compliance ./new-compliance-workspace
```

**What happens**:
1. Copies domain folder and `AGENTS.md`
2. Copies agent definition from `.pi/agents/`
3. Copies domain wiki content from `wiki/<project>/<domain>/`
4. Copies relevant `_meta/` pages and chains
5. Generates minimal workspace scaffold (root `AGENTS.md`, `APPEND_SYSTEM.md`, wiki `Home.md`)
6. Verifies extraction is self-contained with no references back to source project

### Custom Agents

#### Create a Custom Agent

```bash
# In your project directory
cat > .pi/agents/my-custom-agent.md << 'EOF'
---
name: my-custom-agent
description: What this agent does
model: ollama/qwen3.5:cloud
thinking: medium
tools: read, write, bash
cwd: ./my-domain
inheritProjectContext: false
---

Your custom system prompt here.
EOF
```

#### Use in a Chain

```bash
cat > .pi/agents/my-chain.chain.md << 'EOF'
---
name: my-custom-chain
description: What this chain does
steps:
  - agent: my-custom-agent
    task: "Do something"
  - agent: verifier
    task: "Verify the output"
---
```

---

## Architecture

Project Blueprint is based on **three core principles**:

### 1. Structural Routing

**Problem**: Harness-specific configuration (e.g., pi-only, Cursor-only) creates vendor lock-in.

**Solution**: Routing table in `AGENTS.md` — a plain markdown file that any harness can read.

**Example**:
```markdown
## Routing Table

| Keywords | Agent | Domain |
|----------|-------|--------|
| patient, admission, discharge | patient-manager | patient-management |
| invoice, payment, subscription | billing-agent | billing |
| HIPAA, compliance, audit | compliance-checker | compliance |
```

**Benefits**:
- Works in pi, Cursor, Claude Code, or any harness that reads markdown
- No JSON config files
- Human-readable and editable
- Version control friendly

### 2. Self-Contained Domains

**Problem**: Context scattered across multiple files, hard to maintain.

**Solution**: One `AGENTS.md` per domain folder with everything needed.

**Example** (`billing/AGENTS.md`):
```markdown
# Billing Domain

Managing invoices, payments, subscriptions, and revenue recognition.

## Conventions
- All amounts in USD
- Timestamps in UTC
- Invoice IDs: INV-YYYY-NNNNN

## Rules
### Must Always
- Validate payment before confirming
- Log all transactions
- Send receipts

### Must Never
- Store raw credit card numbers
- Modify past invoices
- Process without audit trail

## Quality Checklist
- [ ] Payment validated
- [ ] Transaction logged
- [ ] Receipt sent
- [ ] Audit trail complete
```

**Benefits**:
- All context in one place
- Easy to understand domain scope
- Simple to maintain
- No cross-references needed

### 3. `inheritProjectContext: false`

**Problem**: Sub-agents inherit full project context, causing redundancy and confusion.

**Solution**: Each sub-agent discovers context independently via domain `AGENTS.md`.

**Agent Definition**:
```yaml
name: billing-agent
inheritProjectContext: false
cwd: ./billing
```

**Benefits**:
- No context duplication
- Agents see only relevant domain context
- Clearer agent boundaries
- Better performance (less context to process)

See [`skills/project-blueprint/references/architecture.md`](skills/project-blueprint/references/architecture.md) for the full architectural rationale with 7 key decisions.

---

## What's Included

```
project-blueprint/
├── package.json
├── README.md                       # This file
├── BUILD.md                        # Complete build instructions
├── skills/project-blueprint/
│   ├── SKILL.md                    # Full 10-phase setup + domain management
│   ├── templates/                  # Scaffolding templates
│   │   ├── AGENTS-root.md          # Root routing table template
│   │   ├── AGENTS-domain.md        # Domain AGENTS.md template
│   │   ├── AGENT-domain.md         # Agent definition template
│   │   ├── APPEND_SYSTEM.md        # Identity file template
│   │   ├── chain-basic.md          # Basic chain template
│   │   ├── wiki-home.md            # Wiki home page (domain-centric layout)
│   │   ├── wiki-page-stub.md       # Generic wiki page template
│   │   ├── wiki-activity-log.md    # Activity log template
│   │   ├── wiki-build-README.md    # HTML wiki build instructions
│   │   ├── wiki-build-config.js    # VitePress config template
│   │   ├── wiki-build-package.json # VitePress package.json
│   │   └── prompt-header.md        # Prompt header format
│   └── references/
│       └── architecture.md         # 9 architectural decisions with rationale
├── prompts/
│   ├── README.md                  # Prompt template docs
│   ├── new-project.md             # /new-project <description>
│   ├── add-domain.md              # /add-domain <name> <keywords>
│   ├── rename-domain.md           # /rename-domain <old> <new>
│   ├── remove-domain.md           # /remove-domain <name>
│   ├── list-domain.md             # /list-domain [--verbose]
│   ├── integrate-wiki.md          # /integrate-wiki [--scan-only]
│   └── extract-domain.md          # /extract-domain <name> [destination]
└── agents/
    ├── README.md                  # Agent documentation
    └── project-builder.md         # Guided, interactive scaffolding agent
```

---

## Step-by-Step Guide

### Phase 1: Installation

```bash
# 1. Install project-blueprint skill
pi install github:carlosfrias/project-blueprint

# 2. Verify installation
pi skill list | grep project-blueprint
```

### Phase 2: Project Creation

```bash
# 1. Create project directory
mkdir my-new-project
cd my-new-project

# 2. Initialize git (optional but recommended)
git init

# 3. Run project-blueprint
pi skill project-blueprint
```

### Phase 3: Interview

The `project-builder` agent will ask:

1. **Project name and description**
   ```
   What is your project called?
   One-sentence description?
   ```

2. **Domain identification**
   ```
   What are the main domains/areas of your project?
   Example: user-management, billing, reporting, compliance
   ```

3. **Domain keywords** (for each domain)
   ```
   For 'billing', what keywords should route to this domain?
   Example: invoice, payment, subscription, revenue
   ```

4. **Agent requirements**
   ```
   What agents do you need in each domain?
   Example: billing-agent, invoice-generator, payment-processor
   ```

5. **Workflow chains**
   ```
   What multi-step workflows do you need?
   Example: invoice → payment → receipt
   ```

6. **Wiki preferences**
   ```
   Do you want HTML wiki build (VitePress)?
   Do you want activity logging enabled?
   ```

### Phase 4: Generation

The agent generates:

1. **Root `AGENTS.md`** with routing table
2. **Domain directories** with `AGENTS.md` files
3. **Agent definitions** in `.pi/agents/`
4. **Chain files** for workflows
5. **Wiki documentation**
6. **README.md** for the project

### Phase 5: Verification

```bash
# Check structure
tree -L 2

# Verify routing table
cat AGENTS.md | grep -A20 "Routing Table"

# Test an agent
/run billing-agent "Generate test invoice"
```

### Phase 6: Customization

```bash
# Edit domain AGENTS.md
nano billing/AGENTS.md

# Add custom agent
nano .pi/agents/my-agent.md

# Create custom chain
nano .pi/agents/my-chain.chain.md
```

### Phase 7: Usage

```bash
# Use domain agents
/run billing-agent "Create invoice for customer X"

# Use chains
/chain invoice-to-payment "Process invoice INV-2026-001"

# Check wiki
open wiki/README.md
```

### Phase 8: Domain Management

```bash
# Add domain as project grows
/add-domain analytics "report, metrics, dashboard, kpi"

# Rename if needed
/rename-domain auth authentication

# Remove obsolete domains
/remove-domain legacy-feature
```

### Phase 9: Wiki Maintenance

```bash
# Update a domain's activity log
echo "### 2026-04-24 - Added analytics domain" >> wiki/<project>/analytics/Activity Log.md

# Integrate legacy wiki content after upgrading project-blueprint
/integrate-wiki

# Extract a domain for a new workspace
/extract-domain bookkeeping

# Rebuild HTML wiki (if using VitePress)
npm run wiki:build
```

### Phase 10: Version Control

```bash
# Commit project structure
git add .
git commit -m "Initial project structure with project-blueprint"

# Push to remote
git remote add origin git@github.com:user/repo.git
git push -u origin main
```

---

## Wiki Documentation

**Main Wiki**: [wiki/README.md](wiki/README.md)

The project-blueprint wiki contains comprehensive documentation with step-by-step guides:

### Wiki Sections

- **[Installation Guide](wiki/README.md#installation-guide)** — Complete installation with dependency setup
- **[Dependencies](wiki/README.md#dependencies)** — Required and optional dependencies with links to their docs
- **[Usage Guide](wiki/README.md#usage-guide)** — Creating projects, managing domains, agents, chains
- **[Architecture](wiki/README.md#architecture)** — Detailed explanation of the three core principles
- **[Templates](wiki/README.md#templates)** — Template documentation and customization
- **[Best Practices](wiki/README.md#best-practices)** — Guidelines for domain, agent, and chain design
- **[Troubleshooting](wiki/README.md#troubleshooting)** — Common issues and solutions
- **[Examples](wiki/README.md#examples)** — Real-world project examples

### Dependency Documentation Links

Project Blueprint integrates with several dependencies. Direct links to their comprehensive documentation:

| Dependency | Purpose | Documentation |
|------------|---------|---------------|
| **pi** | Core AI agent harness | [pi Documentation](https://github.com/mariozechner/pi-coding-agent) |
| **pi-subagents** | Multi-agent orchestration, chains, parallel execution | [pi-subagents](https://github.com/nicobailon/pi-subagents) |
| **pi-intercom** | Agent-to-agent communication bridge | [pi-intercom](https://github.com/carlosfrias/pi-intercom) |
| **pi-model-router** | Automatic model selection | [Model Router Docs](https://github.com/mariozechner/pi-coding-agent/blob/master/docs/model-router.md) |
| **pi-keyword-router** | Keyword-based routing | [Keyword Router Wiki](https://github.com/carlosfrias/pi-keyword-router) |
| **find-skill** | Discover and install agent skills | [Find Skill Wiki](https://github.com/carlosfrias/find-skill) |
| **librarian** | Research open-source libraries with source citations | [Librarian Wiki](https://github.com/carlosfrias/librarian) |
| **decompose-execute-verify** | Cost-optimized task execution | [Decompose-Execute-Verify Pattern Wiki](https://github.com/carlosfrias/decompose-execute-verify) |
| **local-model-pilot** | Ollama configuration | [Local Model Pilot Wiki](https://github.com/carlosfrias/local-model-pilot) |
| **trading-lab-architecture** | Multi-node orchestration | [Trading Lab Architecture](https://github.com/carlosfrias/trading-lab-architecture) |

### Wiki Structure

The generated wiki uses a **domain-centric layout** where domains are the primary content at the root level:

- **Home Page** (`wiki/<project>/Home.md`) — Domain index and navigation
- **Domain Wikis** (`wiki/<project>/<domain>/`) — Each domain has its own wiki section with activity log
- **Reference Docs** (`wiki/<project>/_meta/`) — Architecture, agent definitions, sample prompts (reachable, non-central)

### Wiki Features

#### Activity Logging

Every significant change is logged:

```markdown
## 2026-04-24

### Added
- analytics domain with reporting agents
- invoice-to-payment chain
- custom billing-agent configuration

### Changed
- Updated routing table with new keywords
- Modified billing AGENTS.md quality checks

### Removed
- legacy-reporting domain (superseded by analytics)
```

#### HTML Build (Optional)

If you enable VitePress:

```bash
# Install dependencies
npm install

# Build HTML wiki
npm run wiki:build

# Preview locally
npm run wiki:dev
```

Output in `wiki-build/` — deployable to GitHub Pages, Netlify, etc.

### Wiki Templates

All wiki pages use templates from `skills/project-blueprint/templates/`:

- `wiki-home.md` — Home page structure
- `wiki-activity-log.md` — Activity log format
- `wiki-domain.md` — Domain documentation template
- `wiki-build-README.md` — HTML wiki instructions

---

## Examples

### Example 1: E-Commerce Platform

```bash
/new-project e-commerce platform with product catalog, shopping cart, payments, and shipping
```

**Domains created**:
- `product-catalog/` — Products, categories, inventory
- `shopping-cart/` — Cart management, promotions
- `payments/` — Payment processing, refunds
- `shipping/` — Shipping rates, tracking, delivery

**Agents created**:
- `product-manager` — Manage product listings
- `cart-agent` — Handle shopping cart operations
- `payment-processor` — Process payments
- `shipping-calculator` — Calculate shipping rates

**Chains created**:
- `checkout-flow` — cart → payment → shipping → confirmation
- `refund-flow` — refund-request → validation → processing → notification

### Example 2: Healthcare Analytics

```bash
/new-project healthcare analytics with patient management, billing, and HIPAA compliance
```

**Domains created**:
- `patient-management/` — Patient records, admissions, discharges
- `billing/` — Invoices, insurance claims, payments
- `compliance/` — HIPAA audits, security, reporting

**Key features**:
- HIPAA compliance checks in every domain
- Audit trail for all operations
- Encrypted data handling

### Example 3: SaaS Application

```bash
/new-project SaaS platform with user management, subscriptions, and analytics
```

**Domains created**:
- `user-management/` — Authentication, authorization, profiles
- `subscriptions/` — Plans, billing, upgrades, downgrades
- `analytics/` — Usage metrics, reporting, dashboards

**Chains created**:
- `signup-flow` — registration → verification → onboarding
- `upgrade-flow` — plan-change → proration → activation

---

## Troubleshooting

### Issue: Skill Not Found

```bash
pi skill project-blueprint
# Error: skill not found
```

**Solution**:
```bash
# Reinstall skill
pi install github:carlosfrias/project-blueprint

# Verify installation
pi skill list | grep project-blueprint
```

### Issue: Routing Not Working

**Symptoms**: Tasks not routing to correct domain agents

**Solution**:
```bash
# Check routing table
cat AGENTS.md | grep -A30 "Routing Table"

# Verify keywords match your task
# Example: If task mentions "invoice", ensure "invoice" is in billing keywords

# Update routing table if needed
nano AGENTS.md
```

### Issue: Agent Not Found

**Symptoms**: `/run agent-name` fails

**Solution**:
```bash
# Check agent definition exists
ls .pi/agents/ | grep agent-name

# Verify agent syntax
cat .pi/agents/agent-name.md

# Reload agents (restart pi session)
exit
pi
```

### Issue: Wiki Not Generated

**Symptoms**: `wiki/` directory empty or missing

**Solution**:
```bash
# Re-run project-blueprint
pi skill project-blueprint

# Or manually create wiki structure
mkdir -p wiki/domains wiki/agents wiki/chains
```

### Issue: Domain Management Commands Fail

**Symptoms**: `/add-domain`, `/rename-domain` don't work

**Solution**:
```bash
# Ensure you're in project root
pwd
# Should show /path/to/your/project

# Check prompts are installed
ls ~/.pi/agent/skills/project-blueprint/prompts/

# Reinstall if missing
pi install github:carlosfrias/project-blueprint --force
```

---

## Contributing

### Development Workflow

1. **Fork the repository**
   ```bash
   git clone git@github.com:your-username/project-blueprint.git
   ```

2. **Make changes**
   - Edit templates in `skills/project-blueprint/templates/`
   - Update prompts in `prompts/`
   - Modify agent in `agents/project-builder.md`

3. **Test locally**
   ```bash
   # Install your local version
   pi install ./project-blueprint
   
   # Test in a new project
   mkdir /tmp/test-project
   cd /tmp/test-project
   pi skill project-blueprint
   ```

4. **Submit pull request**
   - Describe changes
   - Include test results
   - Update documentation if needed

### Publishing Workflow

1. **Update version** in `package.json`
2. **Update changelog** in `CHANGELOG.md`
3. **Test thoroughly** in multiple projects
4. **Push to GitHub**
   ```bash
   git push origin main
   ```
5. **Create release** on GitHub (optional)
6. **Publish to npm** (optional)
   ```bash
   npm publish
   ```

### Template Development

Templates are in `skills/project-blueprint/templates/`:

- **Test each template** by generating a project
- **Keep templates minimal** — only essential content
- **Use variables** for project-specific values
- **Document template variables** in comments

---

## Integration

Project Blueprint integrates with:

### pi-keyword-router

Automatic model routing based on prompt keywords:

```bash
# Install keyword router
pi install github:carlosfrias/pi-keyword-router

# Configure in .pi/settings.json
{
  "defaultProvider": "router",
  "defaultModel": "auto"
}
```

See [pi-keyword-router documentation](https://github.com/carlosfrias/pi-keyword-router) for details.

### Decompose-Execute-Verify Pattern

Cost-optimized task execution:

```bash
# Install decompose-execute-verify skill
pi install github:carlosfrias/decompose-execute-verify

# Use in chains
/chain decomposed-task "Complex multi-step task"
```

See [decompose-execute-verify documentation](https://github.com/carlosfrias/decompose-execute-verify) for details.

### Trading Lab Architecture

For multi-node deployments:

```bash
# See trading-lab-architecture
git clone git@github.com:carlosfrias/trading-lab-architecture.git
```

Project Blueprint provides the project structure; Trading Lab provides the multi-node orchestration.

---

## License

MIT License — See [LICENSE](LICENSE) file for details.

---

## Support

- **Documentation**: See [Wiki](wiki/README.md)
- **Issues**: [GitHub Issues](https://github.com/carlosfrias/project-blueprint/issues)
- **Discussions**: [GitHub Discussions](https://github.com/carlosfrias/project-blueprint/discussions)
- **Examples**: See `examples/` directory (when available)

---

## Changelog

### v1.2.1 (2026-05-08)

- **Comprehensive dependency listing** — Added all peer dependencies to package.json: `pi-subagents`, `pi-intercom`, `pi-keyword-router`, `find-skill`, `librarian`, `decompose-execute-verify`
- **Removed hard dependency on decompose-execute-verify** from SKILL.md — now listed as optional peer dependency only
- **Updated dependency table in README.md** — Added `pi-subagents`, `pi-intercom`, `find-skill`, `librarian`; removed old `decomposition-skill` references
- **Updated install instructions** — Added `find-skill` and `librarian` install commands to README.md Step 4
- **Updated compatibility lines** in SKILL.md, BUILD.md — now list all peer packages
- **Clean separation** — project-blueprint no longer assumes decompose-execute-verify is pre-installed

### v1.1.0 (2026-05-08)

- **Domain-centric wiki layout** — Domains are now the primary content at wiki root; project-level reference docs moved to `_meta/` subdirectory
- `/integrate-wiki` command — Consolidates scattered or legacy wiki content (numbered pages, in-domain wikis) into domain-centric layout
- `/extract-domain` command — Extracts a domain as a self-contained package that can seed a new workspace
- Updated wiki home page template — Domain Index table replaces numbered page list; reference docs linked from `_meta/`
- Updated VitePress config template — Domains shown first in sidebar, reference docs collapsed
- Added architecture decision #8 (why domains are central in the wiki) and #9 (why integrate/extract operations)
- Updated all documentation (README, prompts, skills, templates) for new wiki structure

### v1.0.1 (2026-05-07)

- Added `/list-domain` command to list all configured domains with keywords and metadata
- Added `--verbose` flag to `/list-domain` for full metadata output (directory paths, agent files, domain context files)
- Added comprehensive acceptance test suite for domain listing functionality
- Updated SKILL.md with "List Domains" section in Domain Management operations
- Updated all documentation (README, prompts README, product wiki) with `/list-domain` examples

### v1.0.0 (2026-04-24)

- Initial release
- Structural routing with `AGENTS.md`
- Self-contained domain folders
- Sub-agent orchestration with `inheritProjectContext: false`
- Auto-generated wiki documentation
- Domain management commands (`/add-domain`, `/rename-domain`, `/remove-domain`)
- Integration with pi-keyword-router and decompose-execute-verify

---

**Repository**: https://github.com/carlosfrias/project-blueprint  
**Author**: Carlos Frias  
**Version**: 1.2.1  
**Last Updated**: 2026-05-08
