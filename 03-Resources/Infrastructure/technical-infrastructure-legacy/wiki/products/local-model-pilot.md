---
title: local-model-pilot
description: Configure Ollama local LLM routing for Apple Silicon
---

# local-model-pilot

**Type:** Skill  
**Install:** `pi install github:carlosfrias/local-model-pilot`

Configure Ollama local LLM model routing for pi on Apple Silicon Macs.

## What It Does

1. **Detects hardware** — Scans RAM and CPU to determine safe model size limits
2. **Inventories models** — Extracts specs from installed Ollama models
3. **Generates configs** — Creates validated `models.json` and `model-router.json`
4. **Validates output** — Ensures all fields match `ollama show` exactly

## Recommended Configuration (16 GB Mac)

| Role | Model | Size | Capabilities |
|------|-------|------|--------------|
| Flagship | gemma4:e4b | 9.6 GB | tools + thinking + vision |
| Generalist | qwen3:8b | 5.2 GB | tools + thinking |
| Fast responder | qwen3.5:4b | 3.4 GB | tools + thinking + vision |

## Prerequisites

- Ollama installed and running
- macOS with Apple Silicon (M1/M2/M3/M4)
- Python 3 for validation scripts

## Repository

[github.com/carlosfrias/local-model-pilot](https://github.com/carlosfrias/local-model-pilot)
