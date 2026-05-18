# Project Blueprint — Consumer Acceptance Prompt

| About | Details |
|-------|---------|
| **Prompt ID** | TI-034 |
| **Purpose** | Guide a first-time pi user from zero to a working model, then through acceptance testing of project-blueprint |
| **Audience** | Someone who just installed pi. No Ollama. No models. No cloud config. |
| **Status** | 🔄 **IN PROGRESS** |
| **File** | `technical-infrastructure/prompts/PROMPT-TI034-PROJECT-BLUEPRINT-CONSUMER.md` |

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

## Before You Start

**Blocking step:** You must have a verified working model before doing anything else.

---

### Option A: Cloud Setup

**Fastest path** — works in 2 minutes, no local installation needed. **Recommended for first-time users.**

**Pros:** No local setup, no hardware concerns, works immediately
**Cons:** Requires API key (even for free tiers — free models require registration)

**⚠️ Important:** Free tiers can change or require registration. Set up API keys now even if you plan to use free models.

---

#### Two Kinds of Cloud Providers

Pi has two provider types. This determines which file you need to create:

| Provider Type | What You Need | Why |
|---------------|---------------|-----|
| **Built-in** (Gemini, Claude, GPT) | `~/.pi/agent/auth.json` | These are pre-registered in pi |
| **Custom** (Ollama Cloud) | `~/.pi/agent/models.json` | Ollama is NOT pre-registered; you must define it |

---

#### Built-in Cloud Providers

These work immediately after you set an API key. Pick one.

**A.1: Gemini (Google) — Generous Free Tier — RECOMMENDED**

```bash
# Step 1: Get a free API key
# https://aistudio.google.com/app/apikey → "Create API Key"

# Step 2: Test immediately (one-shot, no files needed)
pi --provider google --api-key "YOUR_GEMINI_KEY" --model gemini-2.5-pro "Hello, are you working?"
```

Expected: You get a response. If you do, the model works.

---

**A.2: Claude (Anthropic) — High Quality**

```bash
# Step 1: Get a key
# https://console.anthropic.com/ → sign up (new accounts get $5 credit)

# Step 2: Test immediately
pi --provider anthropic --api-key "YOUR_ANTHROPIC_KEY" --model claude-sonnet-4-6 "Hello, are you working?"
```

---

**A.3: GPT (OpenAI) — Familiar, Reliable**

```bash
# Step 1: Get a key
# https://platform.openai.com/ → sign up (new accounts get $5 credit)

# Step 2: Test immediately
pi --provider openai --api-key "YOUR_OPENAI_KEY" --model gpt-4o "Hello, are you working?"
```

---

#### Custom Cloud Provider: Ollama Cloud

**⚠️ Ollama is NOT built into pi.** You must define it in `models.json` before use.

```bash
# Step 1: Get an API key
# https://ollama.com/ → sign in → https://ollama.com/settings

# Step 2: Export key and create auth.json + models.json (copy-paste ready)
mkdir -p ~/.pi/agent
export OLLAMA_API_KEY="your-key-here"

echo '{
  "ollama": {
    "type": "api_key",
    "key": "'$OLLAMA_API_KEY'"
  }
}' > ~/.pi/agent/auth.json
chmod 600 ~/.pi/agent/auth.json

cat > ~/.pi/agent/models.json << 'EOF'
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "placeholder-ignored",
      "models": [
        {
          "id": "qwen3.5:cloud",
          "name": "Qwen 3.5 Cloud",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000
        },
        {
          "id": "deepseek-v4-pro:cloud",
          "name": "DeepSeek V4 Pro",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000
        }
      ]
    }
  }
}
EOF

# Step 3: Test
pi --provider ollama --model qwen3.5:cloud "Hello, are you working?"
```

Expected: You get a response.

---

#### Store Your Key Permanently (All Providers)

After the one-shot test works, store the key so you don't need `--api-key` every time.

**For built-in providers** (Gemini, Claude, GPT):

```bash
mkdir -p ~/.pi/agent
echo '{
  "google": { "type": "api_key", "key": "YOUR_GEMINI_KEY" }
}' > ~/.pi/agent/auth.json
chmod 600 ~/.pi/agent/auth.json

# Now test without --api-key:
pi --provider google --model gemini-2.5-pro "Hello, are you working?"
```

**For Ollama Cloud:**

The key is already stored inside `models.json` (see Step 2 above). That's the only file you need. To run without `--api-key`:

```bash
pi --provider ollama --model qwen3.5:cloud "Hello, are you working?"
```

---

### Option B: Local Setup

**Prerequisites:**
- Ollama installed: https://ollama.com/download
- Hardware with 8GB+ RAM

**⚠️ Ollama is NOT built into pi.** You must define it in `models.json`.

```bash
# Step 1: Start Ollama locally
ollama serve

# Step 2: Pull a model
ollama pull qwen2.5-coder:7b

# Step 3: Export placeholder and create auth.json + models.json (copy-paste ready)
mkdir -p ~/.pi/agent
export OLLAMA_API_KEY="ollama"

echo '{
  "ollama": {
    "type": "api_key",
    "key": "'$OLLAMA_API_KEY'"
  }
}' > ~/.pi/agent/auth.json
chmod 600 ~/.pi/agent/auth.json

cat > ~/.pi/agent/models.json << 'EOF'
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434/v1",
      "api": "openai-completions",
      "apiKey": "placeholder-ignored",
      "compat": {
        "supportsDeveloperRole": false
      },
      "models": [
        {
          "id": "qwen2.5-coder:7b",
          "name": "Qwen 2.5 Coder 7B (Local)",
          "reasoning": false,
          "input": ["text"],
          "contextWindow": 128000,
          "maxTokens": 32000,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
EOF

# Step 4: Test
pi --provider ollama --model qwen2.5-coder:7b "Hello, are you working?"
```

**Note:** `apiKey` is required but ignored by local Ollama. The value "ollama" is a placeholder.

---

### Option C: Both (Start Simple)

1. Complete Option A now (pick one provider).
2. Later, install Ollama and run Option B.
3. pi uses whichever provider you specify with `--provider` and `--model`.

---

### Check Your Model

**Run this after any Option above.**

Copy and paste this exact prompt into your terminal (replace `--provider` and `--model` with yours):

```bash
pi --provider PROVIDER --model MODEL --api-key KEY "Run these 3 checks and report pass/fail for each:
1. Can you count from 1 to 5?
2. Can you write a single JSON object with one field called 'status' set to 'ok'? No markdown, just raw JSON.
3. Can you explain what a code review is in 2 sentences?
Report only: Test 1: PASS/FAIL, Test 2: PASS/FAIL, Test 3: PASS/FAIL."
```

**Expected result:**
- Test 1: PASS
- Test 2: PASS (must be valid JSON, no markdown code fences)
- Test 3: PASS

**If all 3 pass:** Your model is ready. Proceed to Phase 0.

**If any fail:** Try a larger model or a different provider.

---

## Phase 0: Install Dependent Skills

⚠️ **DO NOT SKIP** — project-blueprint needs these skills first.

Install in this order:

```bash
# 1. find-skill (helps discover other skills)
pi install git:git@github.com:carlosfrias/find-skill

# 2. librarian (research and source code navigation)
pi install git:git@github.com:carlosfrias/librarian

# 3. decomposition-skill (task breakdown for complex work)
pi install git:git@github.com:carlosfrias/decomposition-skill

# 4. pi-keyword-router (routing and context management)
pi install git:git@github.com:carlosfrias/pi-keyword-router
```

Verify each installed:

```bash
pi list
```

Expected: All four packages appear in the list.

**Best Practice Notes:**
- **Do NOT manually copy skills to `~/.pi/agent/skills/`**. The `pi install` command auto-discovers skills from `<repo>/skills/` inside the installed package.
- **`~/.pi/agent/skills/` is for manually created skills only.** Git-installed packages stay in `~/.pi/agent/git/` — pi scans them automatically.
- **No symlinks or file moves needed.** The architecture handles discovery from the package's install location.

---

## Phase 1: Install project-blueprint

```bash
pi install git:git@github.com:carlosfrias/project-blueprint
```

Verify:

```bash
pi list | grep project-blueprint
```

Expected: `github:carlosfrias/project-blueprint` appears.

---

## Phase 2-8: Acceptance Testing

### AC-1: Clean workspace root
- Run: `pi skill project-blueprint`
- Give it a test task (e.g., "create a wiki for my-project")
- **Expected:** No `technical-infrastructure/` folder in workspace root.
- **Expected:** No `templates/` folder in workspace root.

### AC-2: Templates stay in skill folder
- Check: `ls ~/.pi/agent/skills/project-blueprint/templates/`
- **Expected:** Templates exist in the skill directory, not root.

### AC-3: Session artifacts in .pi/sessions/
- Complete any pi session.
- Check: `ls .pi/sessions/`
- **Expected:** Session files (`.md`, `.jsonl`) are in `.pi/sessions/`.

### AC-4: skill reference file created
- Check: `ls ~/.pi/agent/skills/project-blueprint.md`
- **Expected:** A `.md` skill reference file exists.

### AC-5: no root pollution (Final Summary.md)
- Run a task that would previously create `Final Summary.md` in root.
- **Expected:** No `Final Summary.md` in workspace root. It should be in `.pi/sessions/`.

### AC-6: question storage works
- Ask pi a complex question during a session.
- End the session.
- Check the session file in `.pi/sessions/`.
- **Expected:** The question is stored and retrievable.

### AC-7: Vitepress wiki scaffold
- Run: `pi skill project-bluepress`
- Task: "Set up a Vitepress wiki for my project"
- **Expected:** A `wiki/` directory with `.vitepress/config.js` and `index.md` is created.

### AC-8: Backlog integration
- Run: `pi skill project-blueprint`
- Task: "Create a backlog item for 'test item'"
- **Expected:** A properly formatted backlog entry is created in the wiki.

---

## What Changed and Why

### Problem with v1
v1 assumed the user already had a working model and Ollama installed. It skipped the most critical step: getting ANY model running.

### How this version fixes it
- **Phase -1** is now a blocking prerequisite with multiple paths (cloud, local, hybrid).
- **Cloud-first** for new users who have no local setup.
- **Provider-agnostic** — any working model is acceptable.
- **Honest assessment** about what we don't know (no benchmark data for this prompt).

### Key design decisions
1. **Use CLI flags for testing** — no file creation needed to get started.
2. **auth.json for built-in providers** — Gemini, Claude, GPT use this.
3. **models.json for custom providers** — Ollama (local or cloud) MUST have this.
4. **Multi-provider support** — Ollama Cloud, Gemini, Claude, GPT.

---

## Troubleshooting

### "I don't have an API key for ANY cloud provider"
**Option A:** Use the Gemini free tier — it requires only a Google account and gives you a generous free allowance.
**Option B:** Install Ollama and use a small local model (see Option B).

### "`pi` gives an error about no model configured"
You haven't specified `--provider` and `--model`. Pi needs both:
```bash
pi --provider PROVIDER --model MODEL --api-key KEY "your prompt"
```

### "`pi` says 'No API key found for PROVIDER'"
Either:
1. Use `--api-key YOUR_KEY` in the command, or
2. For built-in providers (Gemini, Claude, GPT): create `~/.pi/agent/auth.json`.
3. For Ollama Cloud: check that your key is in `~/.pi/agent/models.json` under the `apiKey` field.

### "My model passes Test 1 but fails Test 2 (structured output)"
The model cannot reliably produce JSON. Try a larger model or a different provider. Gemini 2.5 Pro, Claude Sonnet, and GPT-4o generally handle structured output well.

---

## Honest Assessment: What We Know vs What We Don't

### What We Know (Evidence-Based)
1. pi requires `--provider` and `--model` flags (or a configured default).
2. The `--api-key` flag works for immediate testing.
3. `auth.json` is the persistent credential store for built-in providers (Gemini, Claude, GPT, etc.).
4. `models.json` is REQUIRED for custom providers like Ollama (local or cloud). It is NOT "advanced" — it's mandatory for Ollama.
5. A model must pass 3 capability tests before skill installation.

### What We Don't Know (Acknowledged Gap)
1. **No empirical benchmark data** for which models complete TI-034 successfully.
   - The table above is empty because we have not run the acceptance test on multiple models.
   - After YOU run it, please record: which model, pass/fail per AC, total score.
2. **No data on minimum viable model size** for project-blueprint tasks.
   - Could a 3.5B model complete AC-1 through AC-8? Unknown.
3. **No data on cloud vs local reliability** for skill installation.

### Our Lab (Reference Only, NOT Prescriptive)
- We tested on a machine with 31GB RAM. This is NOT representative of consumer hardware.
- Hardware requirements cannot be inferred from our setup.

---

## Future Work: Empirical Benchmarking

After running TI-034, please contribute your results:

| Model | Provider | RAM/Screen | AC-1 | AC-2 | AC-3 | AC-4 | AC-5 | AC-6 | AC-7 | AC-8 | Total |
|-------|----------|------------|------|------|------|------|------|------|------|------|-------|
| | | | | | | | | | | | |

Open a PR to `github:carlosfrias/project-blueprint` with your results.

---

**End of Prompt**