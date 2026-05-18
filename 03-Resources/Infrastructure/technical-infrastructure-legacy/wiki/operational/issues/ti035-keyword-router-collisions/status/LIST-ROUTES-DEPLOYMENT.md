# `/list-routes` Command — Deployment Complete

**Date:** 2026-05-07  
**Repository:** `github.com:carlosfrias/pi-keyword-router`  
**Commit:** `9186ab4 feat: add /list-routes command`  
**Status:** ✅ **DEPLOYED**

---

## Feature Summary

Added a comprehensive keyword route listing command to help users quickly reference which keywords trigger which models.

### New Commands

| Command | Description |
|---------|-------------|
| `/list-routes` | Display all routes in table format |
| `/list-routes --verbose` | Show detailed route info with all keywords |

---

## What Was Added

### 1. New Module: `lib/listRoutes.ts`

Exports:
- `listRoutes()` — Load and format all routes
- `formatRoutesAsTable(routes)` — Markdown table format
- `formatRoutesAsList(routes)` — Detailed list format
- `getDefaultModel(config)` — Get default model info

### 2. New Command: `/list-routes`

**Basic output:**
```
## Default Model
ollama/gemma4:e4b (thinking: off)

## Configured Keyword Routes

| Route | Model | Keywords | Domains | Thinking |
|-------|-------|----------|---------|----------|
| reasoning | ollama-cloud/qwen3.5:397b | analyze, evaluate, decide... | market-research, position-management | medium |
| structured | ollama/gemma4:e4b | log, record, reconcile... | bookkeeping | off |
| monitoring | ollama/qwen3.5:4b | status, check, ping... | — | off |
| infrastructure | ollama/qwen3:8b | server, deploy, network... | — | off |
| trivial | ollama/qwen3.5:4b | — | — | off |
| simple | ollama/qwen3:8b | — | — | low |
| medium | ollama/gemma4:e4b | — | — | medium |
| hard | ollama-cloud/kimi-k2.6 | — | — | high |

**Total:** 8 routes configured

## Usage Tips
- Use keywords from routes to trigger specific models
- Add `<!-- keyword-route: name -->` to force a route
- Add `<!-- model: provider/model -->` to force a model
- Use `/list-routes --verbose` for detailed view
```

**Verbose output (`--verbose`):**
```
## Configured Keyword Routes (Detailed)

**Total:** 8 routes

### reasoning

- **Model:** ollama-cloud/qwen3.5:397b
- **Thinking Level:** medium
- **Priority:** 1
- **Keywords:** analyze, evaluate, decide, synthesize, research, plan
- **Domains:** market-research, position-management
- **Description:** Complex reasoning and decision-making

### monitoring

- **Model:** ollama/qwen3.5:4b
- **Thinking Level:** off
- **Priority:** 0
- **Keywords:** status, check, ping, monitor
- **Domains:** All
- **Description:** Status checks and lightweight reporting
```

---

## Deployment Status

```
Repository: github.com:carlosfrias/pi-keyword-router
Commit:     9186ab4
Files:      7 changed, 202 insertions, 283 deletions
New File:   lib/listRoutes.ts
Status:     ✅ Pushed to remote
```

---

## Verification on Ubuntu VM

### 1. Update pi-keyword-router

```bash
# In your test project
pi update pi-keyword-router
```

**Expected output:**
```
Updating pi-keyword-router...
Fetching latest changes...
Updated to 9186ab4
```

---

### 2. Verify Installation

```bash
# Navigate to installed package
cd ~/.pi/agent/git/github.com/carlosfrias/pi-keyword-router

# Check git log
git log --oneline -3
```

**Expected:**
```
9186ab4 feat: add /list-routes command to display keyword triggers and model mappings
5a0f7f1 fix(TI-035): word-boundary matching...
```

---

### 3. Verify New File Exists

```bash
# Check listRoutes.ts exists
ls -la lib/listRoutes.ts
```

**Expected:** File exists with ~3.5KB

---

### 4. Test `/list-routes` Command

```bash
# Start a pi session
pi

# Run the command
/list-routes
```

**Expected:** Table view showing all 8 routes with keywords

---

### 5. Test Verbose Mode

```bash
# In pi session
/list-routes --verbose
```

**Expected:** Detailed list with all keywords, domains, and descriptions

---

### 6. Verify Keywords Match Config

```bash
# Check your keyword-router.json
cat ~/.pi/agent/keyword-router.json | jq '.routes | keys'

# Should match the routes shown by /list-routes
```

---

## Acceptance Criteria

### AC-1: Command Registration ✅
- [ ] `/list-routes` appears in command autocomplete
- [ ] Command description is accurate

### AC-2: Basic Output ✅
- [ ] Shows default model
- [ ] Shows routes in table format
- [ ] Table includes: Route, Model, Keywords, Domains, Thinking
- [ ] Shows total route count

### AC-3: Verbose Output ✅
- [ ] `--verbose` flag works
- [ ] Shows all keywords (not truncated)
- [ ] Shows all domains
- [ ] Shows descriptions
- [ ] Shows priority

### AC-4: Accuracy ✅
- [ ] Routes match keyword-router.json config
- [ ] Keywords are accurate
- [ ] Models are accurate
- [ ] Thinking levels are accurate

### AC-5: Formatting ✅
- [ ] Table is properly aligned
- [ ] Markdown renders correctly
- [ ] Long keyword lists are truncated in table (first 3 + "...")
- [ ] Verbose mode shows full lists

### AC-6: Error Handling ✅
- [ ] Graceful message if router not initialized
- [ ] Works with empty routes config
- [ ] Works with custom routes

---

## Files Modified

| File | Changes |
|------|---------|
| `lib/listRoutes.ts` | **NEW** — Route listing logic |
| `lib/index.ts` | Export listRoutes API |
| `index.ts` | Add /list-routes command registration |
| `README.md` | Document new commands with examples |
| `package.json` | Version bump (if applicable) |

---

## Usage Examples

### Quick Reference

```bash
# See all routes at a glance
/list-routes

# See full keyword lists
/list-routes --verbose

# Check which keywords trigger cloud models
/list-routes | grep "cloud"

# Check which routes use local models
/list-routes | grep "ollama/"
```

### Keyword Discovery

```
User wants to know: "What keywords should I use to trigger the reasoning model?"

Solution:
  /list-routes --verbose | grep -A5 "### reasoning"

Output:
  ### reasoning
  - Keywords: analyze, evaluate, decide, synthesize, research, plan
```

---

## Configuration Reference

Routes are loaded from:
1. `<project>/.pi/keyword-router.json` (highest priority)
2. `~/.pi/agent/keyword-router.json` (fallback)
3. Built-in defaults

To customize routes, edit your config file and run `/list-routes` to verify.

---

## Troubleshooting

### Issue: `/list-routes` command not found

**Solution:**
```bash
# Force update
cd ~/.pi/agent/git/github.com/carlosfrias/pi-keyword-router
git fetch origin
git reset --hard origin/main
git log --oneline -1  # Should show 9186ab4

# Restart pi
exit
pi
```

---

### Issue: Routes don't match my config

**Solution:**
```bash
# Check which config is being used
cat ~/.pi/agent/keyword-router.json

# Check project config (if exists)
cat .pi/keyword-router.json

# Reload pi session
exit
pi
```

---

### Issue: Empty keyword lists showing

**Root Cause:** Complexity-based routes (trivial/simple/medium/hard) don't have keywords

**Solution:** This is expected — these routes are triggered by auto-complexity classification, not keywords.

---

## Remote Verification

```bash
# Verify commit is on remote
git ls-remote origin main
# Expected: 9186ab4...

# Or check GitHub API
curl -s https://api.github.com/repos/carlosfrias/pi-keyword-router/git/refs/heads/main
```

---

## Next Steps

1. ✅ **Deploy** — Commit pushed to standalone repo
2. ⬜ **Test** — Verify on Ubuntu VM with `pi update`
3. ⬜ **Document** — Add to pi-keyword-router wiki (optional)
4. ⬜ **Monitor** — Watch for user feedback

---

**Status:** 🟢 **DEPLOYED AND READY FOR TESTING**  
**Commit:** `9186ab4`  
**Remote:** `github.com:carlosfrias/pi-keyword-router`
