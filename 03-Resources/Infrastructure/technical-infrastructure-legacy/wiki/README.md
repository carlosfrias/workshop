# Technical Infrastructure Wiki

Documentation for extensions, skills, and agents published from this workspace.

## Navigation

### Quick Start
- **[Quick Start Guide](guides/quick-start.md)** — Step-by-step fresh project setup (10-15 min)
- **Setup Script** `scripts/project-blueprint-setup.sh` — Automated setup script
- **[Ollama Setup](guides/ollama-setup.md)** — Local LLM installation and model configuration
- **[Dictation Setup](guides/dictation-setup.md)** — Local speech-to-text with Whisper.cpp + Hammerspoon
- **[Local Network Orchestration](operational/planning/PLAN-2026-05-01-1547.md)** — Task distribution across lab nodes

### Model Operations
- **[Model Routing Guide](reference/model-routing-guide.md)** — Logic for automatic cloud/local switching and tiers
- **[LLM Cost Projections](reference/llm-cost-projections.md)** — Financial modeling for consumption-based pricing
- **[Ollama Setup](guides/ollama-setup.md)** — Local LLM installation and model configuration

### Getting Started
- **[Getting Started](guides/getting-started.md)** — Overview and quick start
- **[Publishing Workflow](guides/publishing-workflow.md)** — How to publish packages (local → GitHub → npm)
- **[Wiki Separation Plan](operational/planning/wiki-separation-plan.md)** — Architecture for wiki-per-workspace

### Published Packages

#### Extensions
- **[pi-keyword-router](products/pi-keyword-router)** — Dynamic keyword-based model routing
  - Installation: `pi install github:carlosfrias/pi-keyword-router`
  - Repository: https://github.com/carlosfrias/pi-keyword-router

#### Skills
- **[project-blueprint](products/project-blueprint)** — Project scaffolding skill
  - Installation: `pi install github:carlosfrias/project-blueprint`
  - Repository: https://github.com/carlosfrias/project-blueprint

#### Agent Packages
- **[trading-agents](products/trading-agents)** — Reusable agent definitions (decomposer, verifier)
  - Status: Planned
  - Repository: TBD

### Architecture Documentation
- **[Decompose → Execute → Verify Pattern](reference/decompose-execute-verify-pattern.md)** — Cost-optimized execution architecture

### Reference Documentation
- **[Sub-Agent Packages Reference](reference/subagent-packages-reference.md)** — Feature comparison of pi-subagents and pi-interactive-subagents
- **[Real-Time Control Patterns](reference/real-time-control-patterns.md)** — Control spectrum from autonomous to supervised
- **[pi-intercom Setup](guides/pi-intercom-setup.md)** — Installation, configuration, and bridge setup
- **[pi-subagents Configuration](reference/pi-subagents-config-reference.md)** — Config file reference and agent overrides

### Infrastructure
- **[Multi-Node Cluster Setup](guides/multi-node-setup-2026-04-26.md)** — 7-node pi cluster deployment with intercom coordination
- **[Static IP Configuration](guides/static-ip-configuration.md)** — DHCP reservation setup for TP-Link AX6000 router

### Tools
- **[Tools Directory](tools/)** — External tools that integrate with pi
  - **[Zellij](tools/zellij.md)** — Modern terminal multiplexer (tmux alternative)

## For Consumers

If you're using these packages in a trading workspace, see:
- **Trading Workspace Wiki** — `wiki/trading-desk/` in the trading-workspace
- **Model Assignment Strategy** — How to use keyword routing for trading tasks

## For Contributors

1. Develop locally in `technical-infrastructure/`
2. Test in trading-workspace: `pi install ../technical-infrastructure/extensions/<name>`
3. Publish to GitHub
4. Update this wiki

## Quick Links

| Task | Documentation |
|------|---------------|
| Install an extension | [Getting Started](guides/getting-started.md) |
| Publish a new version | [Publishing Workflow](guides/publishing-workflow.md) |
| Understand the architecture | [Decompose → Execute → Verify](reference/decompose-execute-verify-pattern.md) |
| Separate wikis by workspace | [Wiki Separation Plan](operational/planning/wiki-separation-plan.md) |
