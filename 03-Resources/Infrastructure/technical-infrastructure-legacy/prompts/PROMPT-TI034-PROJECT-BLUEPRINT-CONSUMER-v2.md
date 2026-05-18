# Project Blueprint — Consumer Acceptance Prompt

**Prompt ID:** TI-034
**Purpose:** Guide a first-time pi user from zero to a working model, then through acceptance testing of project-blueprint
**Audience:** Someone who just installed pi. No Ollama. No models. No cloud config.
**Status:** 🔄 **IN PROGRESS**
**File:** `technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md`

---

## First: The Decision Tree

Before anything else, pick a model path based on **time** and **comfort level**.

| If you want... | Choose | Effort |
|----------------|--------|--------|
| **Fastest setup** (2 minutes, zero local installs) | **Cloud Model** | Low |
| **Privacy** (no data leaves your machine) | **Local Model via Ollama** | Medium (install Ollama + pull model) |
| **Best of both** | **Hybrid** (start cloud, add local later) | Low now, medium later |

**For first-time users, we strongly recommend Cloud first.** You can add Ollama later.

---

## Phase -1: Get a Working Model (BLOCKING)

**DO NOT PROCEED** to skill installation until you have verified a working model.

### Option A: Cloud Model (Fastest — Recommended for First-Time Users)

**Pros:** No local setup, no hardware concerns, works immediately
**Cons:** Requires API key, costs $ per use

**Step 1: Enable a cloud provider in pi**

Run these commands in pi:

```bash
# Option A.1: Claude (Anthropic) — Recommended for complex tasks
# Get a key: https://console.anthropic.com/
pip3 install anthropic  # or: python3 -m pip install anthropic
# Then: pi settings → models → add "anthropic/claude-sonnet-4-6"

# Option A.2: Gemini (Google) — Good free tier
# Get a key: https://aistudio.google.com/app/apikey
# Then: pi settings → models → add "google/gemini-2.5-pro"

# Option A.3: GPT (OpenAI) — Familiar, reliable
# Get a key: https://platform.openai.com/
# Then: pi settings → models → add "openai/gpt-4o"
```

**Step 2: Verify the model works**

```bash
# Ask pi to use the model
pi "Hello, can you confirm you are working?"

# Expected: You get a response back. If not, check your API key.
```

**Step 3: Set as default (for this session)**

```bash
# In pi, set the model
/pi model anthropic/claude-sonnet-4-6
# or: /pi model google/gemini-2.5-pro
```

**Acceptance Criteria:**
- [ ] **AC-(-1).1a:** API key obtained and verified
- [ ] **AC-(-1).1b:** Model responds to a simple prompt
- [ ] **AC-(-1).1c:** Model can follow a 2-step instruction (e.g., "List 2 files, then tell me which is larger")

If cloud is working, **skip to Phase 0** below.

---

### Option B: Local Model via Ollama (Privacy — Requires Hardware Check)

**Pros:** No API costs, data stays local, works offline
**Cons:** Requires hardware check, download time, consumes RAM

**Step 1: Can your hardware run a local model?**

```bash
# Check available RAM
darwin:   sysctl hw.memsize | awk '{print $2/1024/1024/1024 " GB"}'
linux:    free -h | grep Mem
windows:  systeminfo | findstr "Total Physical Memory"
```

**Minimum viable local model (4-bit quantized):**

| Your RAM | Largest Model | Example | Speed |
|----------|---------------|---------|-------|
| 8 GB | ~3-4B | phi4:3b, gemma3:4b | Slow |
| 16 GB | ~7-8B | qwen3.5:8b, llama3.1:8b | Moderate |
| 32 GB | ~13-14B | qwen3.5:14b, gemma3:14b | Good |
| 64 GB+ | ~30-70B | qwen3.5:32b, mixtral:8x7b | Excellent |

**⚠️ Honest Assessment:** We have **no empirical evidence** which Ollama model size is *sufficient* for this acceptance prompt. The table above is based on general community wisdom, not benchmarks from this workspace. See "Future Work" below.

**Step 2: Install Ollama**

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download
```

**Step 3: Pull a model and test it**

```bash
# Pull a model appropriate for your RAM tier
# For 16 GB RAM (moderate): 8B models
ollama pull qwen3.5:8b
# or: ollama pull llama3.1:8b

# Start it
ollama run qwen3.5:8b "Can you confirm you are working?"

# Expected: You get a response.
```

**Step 4: Configure pi to use Ollama**

Add to `~/.pi/agent/settings.json`:

```json
{
  "provider": "ollama",
  "model": "qwen3.5:8b",
  "baseUrl": "http://localhost:11434"
}
```

**Step 5: Verify via pi**

```bash
pi "Hello, can you confirm you are working?"
# Expected: Response comes from your local qwen3.5:8b
```

**Acceptance Criteria:**
- [ ] **AC-(-1).2a:** Ollama installed and `ollama list` works
- [ ] **AC-(-1).2b:** A model downloaded and responds to prompt
- [ ] **AC-(-1).2c:** pi can successfully route to Ollama
- [ ] **AC-(-1).2d:** Model can follow a 2-step instruction

---

### Option C: Hybrid (Recommended Long-Term)

Use **cloud for acceptance testing** (today) and **add Ollama later** (tomorrow).

This is what we recommend for almost everyone:
1. Today: Get cloud working (5 minutes, guaranteed)
2. Run all acceptance tests with cloud model
3. Tomorrow: Install Ollama if you want local models
4. Future: Configure pi-keyword-router to auto-route

**Why this works:** You aren't blocked by model setup. You get immediate results. You can optimize later.

---

## Phase -1: Model Capability Test (After Model is Working)

Now that you have *some* model, verify it can handle this prompt's complexity.

**Test 1: Can it follow instructions?**

```
"Execute these steps and report back:
1. Create a directory /tmp/test-123
2. Create a file inside called hello.txt with content 'Hello World'
3. Verify the file exists
4. Report the full path"
```

**Expected:** Model creates directory and file, verifies existence, reports path.
**If it fails:** Try a different model (cloud models almost always pass; 3B local models often fail).

**Test 2: Can it reason about pass/fail?**

```
"A workspace root contains these files: AGENTS.md, .pi/, templates/, Final Summary.md.
Which of these should NOT be in the root directory? Explain your reasoning."
```

**Expected:** Identifies `templates/` and `Final Summary.md` as pollutants.
**If it fails:** Model lacks reasoning for this task. Switch to a larger model.

**Test 3: Can it produce structured output?**

```
"Produce a markdown checklist with 5 items numbered 1-5, each marked PASS or FAIL."
```

**Expected:** Well-formatted checklist.
**If it fails:** Model struggles with formatting. Usually a minor issue, but note it.

**Final Gate:**
- [ ] **AC-(-1).3:** All 3 capability tests pass → **Proceed to Phase 0**
- [ ] **AC-(-1).4:** Any test fails → **Stop. Upgrade model or switch provider.**

---

## Phase 0: Install Dependent Skills (PREREQUISITE)

Now that your model is working → install skills.

```bash
# Install skill discovery and research tools
pi install github:carlosfrias/find-skill
pi install github:carlosfrias/librarian

# Install project-blueprint dependencies
pi install github:carlosfrias/decomposition-skill
pi install github:carlosfrias/pi-keyword-router

# Verify all skills installed
pi skill list | grep -E "(find-skill|librarian|decomposition-skill|pi-keyword-router)"
# Expected: 4 skills listed
```

---

## Phase 1: Install project-blueprint

```bash
# Install project-blueprint from GitHub
pi install github:carlosfrias/project-blueprint

# Verify installation
pi skill list | grep project-blueprint

# Verify all skills (dependencies + project-blueprint)
pi skill list | grep -E "(find-skill|librarian|decomposition-skill|pi-keyword-router|project-blueprint)"
# Expected: 5 skills listed
```

---

## Phase 2-8: Acceptance Testing

Continue with the existing acceptance criteria from the previous version of this prompt.

---

## What Changed and Why

### Problem with Previous Version
The previous prompt asked users to:
1. Install project-blueprint ← but this requires a model
2. Run acceptance tests ← but this requires a capable model
3. Check if model works ← buried deep in the prompt

A new user would get stuck immediately because none of the steps work without a model.

### How This Version Fixes It
1. **Decision tree at the top** — User picks cloud or local based on their situation
2. **Model setup comes FIRST** — No work happens without a verified working model
3. **Cloud is the fast path** — Gets users unblocked in 2 minutes
4. **Local is the slow path** — Hardware check first, prevents frustration
5. **Capability gate** — Tests the model before asking it to do real work
6. **Honest assessment** — RAM table is labeled as community wisdom, not benchmark

---

## Troubleshooting

### "I don't have an API key for ANY cloud provider"

**Quick fix:** Use Gemini (Google) — generous free tier.

1. Go to https://aistudio.google.com/app/apikey
2. Create key (free)
3. Add to pi: `/pi model google/gemini-2.5-pro`
4. Test: `pi "Hello?"`

### "Ollama is installed but `ollama run` hangs"

**Likely causes:**
- Not enough RAM → Use smaller model (3B instead of 8B)
- Ollama service not running → `ollama serve` or restart
- Firewall blocking → Check port 11434

**Quick fix:** Switch to cloud model for today. Debug Ollama tomorrow.

### "My model passes Test 1 but fails Test 3 (structured output)"

**This is usually acceptable.** Structured output is nice-to-have. What matters:
- Must pass: **Test 1** (follow instructions) and **Test 2** (reason about pass/fail)
- Nice to have: **Test 3** (structured output)

If Tests 1-2 pass, proceed. Note the formatting limitation in your report.

---

## Future Work

**Empirical benchmarking needed:**

| Model | Size | Type | Can follow instructions? | Can reason about pass/fail? | Can format output? |
|-------|------|------|------------------------|------------------------------|-------------------|
| ??? | ??? | ??? | ??? | ??? | ??? |

**This table is intentionally empty.** We have collected zero benchmark data for TI-034. The goal is to fill this table over time.

**How to contribute:**
1. Run TI-034 with your model
2. Fill in the table above
3. Submit results to `technical-infrastructure/operational/testing/ti034-model-benchmarks.json`

Once we have 5-10 data points, we can retire "community wisdom" recommendations and replace them with evidence.

---

**Version:** 2.0.0
**Created:** 2026-05-06
**Updated:** 2026-05-06 — Redesigned for first-time users with zero model infrastructure
**Author:** Trading Desk Agent
