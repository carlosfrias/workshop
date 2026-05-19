---
title: pi-keyword-router
description: Dynamic keyword-based model routing extension
---

# pi-keyword-router

**Type:** Extension  
**Install:** `pi install github:carlosfrias/pi-keyword-router`

Dynamically routes prompts to the appropriate model (local or cloud) based on prompt content, keywords, and domain.

## Route Reference

| Route | Provider | Model | Thinking | Priority | Key Triggers |
|-------|----------|-------|----------|----------|--------------|
| ultra-reasoning | ollama | kimi-k2.6 (1042B) | high | 2 | think deeply, comprehensive, thorough |
| reasoning | ollama | qwen3.5:397b (397B) | medium | 1 | analyze, evaluate, decide, research |
| coding | ollama | deepseek-v4-pro (158B) | medium | 0 | code, implement, develop, debug |
| vision | ollama | qwen3-vl:235b (235B) | medium | 0 | image, screenshot, chart |
| structured | ollama | gemma4:e4b (32B) | off | 0 | log, reconcile, parse, format |
| monitoring | ollama | qwen3.5:4b (4B) | off | 0 | status, check, ping, health |
| infrastructure | ollama | qwen3:8b (8B) | off | 0 | server, deploy, dns, network |
| (default) | ollama | gemma4:e4b (32B) | off | — | No keyword match |

## Quick Commands

| Command | Description |
|---------|-------------|
| `/model-route` | Show routing status, routes, and recent decisions |
| `/model-route-off` | Disable automatic routing for this session |
| `/model-route-on` | Re-enable automatic routing |

## Configuration

Global config: `~/.pi/agent/model-router.json`

Override per-project: `.pi/model-router.json`

## Repository

[github.com/carlosfrias/pi-keyword-router](https://github.com/carlosfrias/pi-keyword-router)
