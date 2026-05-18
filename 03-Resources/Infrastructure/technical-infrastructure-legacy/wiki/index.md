---
layout: home
title: Technical Infrastructure Wiki
titleTemplate: Carlos' Desktop
hero:
  name: Technical Infrastructure
  text: Extensions, Skills & Agents
  tagline: The factory for publishable packages in Carlos' Desktop
  actions:
    - theme: brand
      text: Get Started
      link: /technical-infrastructure/guides/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/carlosfrias/trading-workspace
features:
  - title: pi-keyword-router
    details: Dynamic keyword-based model routing — automatically routes prompts to local or cloud models
    link: /technical-infrastructure/products/pi-keyword-router
  - title: project-blueprint
    details: Scaffold new projects with sub-agent orchestration, structural routing, and domain directories
    link: /technical-infrastructure/products/project-blueprint
  - title: Decompose → Execute → Verify
    details: Cost-optimized architecture using cloud decomposition, local execution, and cloud verification
    link: /technical-infrastructure/reference/decompose-execute-verify-pattern
  - title: Voice Input (Voxtype)
    details: Push-to-talk voice-to-text integration for hands-free trading commands via Voxtype + Whisper
    link: /technical-infrastructure/guides/voice-input-guide
  - title: playbook-trigger
    details: Standalone keyword-triggered Ansible playbook execution for low-capacity LLMs (2-4B params)
    link: /technical-infrastructure/products/playbook-trigger
---

# Welcome

This wiki documents the **technical-infrastructure** workspace — the factory for extensions, skills, and agents used across Carlos' Desktop.

## Quick Links

| I want to... | Start here |
|--------------|------------|
| Install an extension | [Getting Started](/technical-infrastructure/guides/getting-started) |
| Publish a package | [Publishing Workflow](/technical-infrastructure/guides/publishing-workflow) |
| Understand the architecture | [Decompose → Execute → Verify](/technical-infrastructure/reference/decompose-execute-verify-pattern) |
| Browse model routing | [Model Routing Guide](/technical-infrastructure/reference/model-routing-guide) |
| Set up local LLMs | [Ollama Setup](/technical-infrastructure/guides/ollama-setup) |

## Published Packages

| Package | Type | Install |
|---------|------|---------|
| **pi-keyword-router** | Extension | `pi install github:carlosfrias/pi-keyword-router` |
| **project-blueprint** | Skill | `pi install github:carlosfrias/project-blueprint` |
| **playbook-trigger** | Skill | `pi install github:carlosfrias/playbook-trigger-skill` |
| **trading-agents** | Agent Package | Planned |

## For Consumers

If you're using these packages in Carlos' Desktop, see the [Trading Workspace Wiki](https://github.com/carlosfrias/trading-workspace/tree/main/wiki) for trading-specific usage guides.

## For Contributors

1. Develop locally in `technical-infrastructure/`
2. Test in trading-workspace
3. Publish to GitHub
4. Documentation is auto-published here

## Recent Updates

- **2026-05-10**: Added [Voice Input Guide](/technical-infrastructure/guides/voice-input-guide) — hands-free trading commands via Voxtype
