# Wiki-Build Fix: Verification Guide for Ubuntu VM

**Date:** 2026-05-07  
**Commit:** `934e0eb fix: wiki-build templates - create as wiki subdirectory`  
**Status:** ✅ **PUSHED TO REMOTE**

---

## Remote Repository Status

```
Repository: github.com:carlosfrias/project-blueprint
Branch:     main
Latest:     934e0ebfd5ae864c3b65bdf6a324ffcd3c34060d
Status:     ✅ Pushed and available
```

---

## Step-by-Step Verification on Ubuntu VM

### 1. Update project-blueprint

```bash
# Navigate to your test project
cd ~/your-test-project

# Update project-blueprint package
pi update project-blueprint
```

**Expected output:**
```
Updating project-blueprint...
Fetching latest changes...
Already up to date. (or shows update progress)
```

---

### 2. Verify Package Location and Version

```bash
# Navigate to installed package
cd ~/.pi/agent/git/github.com/carlosfrias/project-blueprint

# Check git log shows the fix
git log --oneline -3
```

**Expected output:**
```
934e0eb fix: wiki-build templates - create as wiki subdirectory
6e25635 feat: add /list-domain command (PB-001)
4a58c23 feat: Add prompt-header template
```

---

### 3. Verify Template Files

```bash
# Check wiki-build-config.js has correct srcDir
cat skills/project-blueprint/templates/wiki-build-config.js | grep -A2 "srcDir"
```

**Expected output:**
```javascript
  // Source directory: parent directory (where markdown files live)
  srcDir: '.',
  srcExclude: ['**/wiki-build/**', '**/dist/**', '**/node_modules/**'],
```

**❌ If you still see `srcDir: '{wiki_src_dir}'`**, the update didn't work - see troubleshooting below.

---

### 4. Verify SKILL.md Phase 8b

```bash
# Check SKILL.md has correct instructions
grep -A5 "Phase 8b" skills/project-blueprint/SKILL.md | head -10
```

**Expected output:**
```
### Phase 8b: Create HTML Wiki Build (Optional)

If the user wants an HTML wiki, create a `wiki-build/` directory **inside the wiki directory** as a subdirectory:

wiki/
└── {project-name}/
    └── wiki-build/
```

---

### 5. Test New Project Creation

```bash
# Create fresh test directory
mkdir -p ~/test-wiki-build
cd ~/test-wiki-build

# Run project-blueprint
pi skill project-blueprint

# During interview, answer:
# - Project name: "test-wiki-structure"
# - HTML wiki: yes
```

---

### 6. Verify Generated Structure

```bash
# Check the wiki directory structure
tree wiki/test-wiki-structure/
```

**Expected structure:**
```
wiki/test-wiki-structure/
├── 00 — Home.md
├── 01 — Philosophy & Architecture.md
├── bookkeeping/
│   └── Activity Log.md
└── wiki-build/              # ✅ Should be INSIDE wiki directory
    ├── .vitepress/
    │   └── config.js
    ├── package.json
    └── README.md
```

**❌ WRONG (old structure):**
```
wiki/test-wiki-structure/
└── 00 — Home.md

wiki-build/                  # ❌ Wrong - sibling directory
└── .vitepress/
```

---

### 7. Verify VitePress Config

```bash
# Check the generated config
cat wiki/test-wiki-structure/wiki-build/.vitepress/config.js | head -15
```

**Expected output:**
```javascript
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'test-wiki-structure',
  description: '...',

  // Source directory: parent directory (where markdown files live)
  srcDir: '.',
  srcExclude: ['**/wiki-build/**', '**/dist/**', '**/node_modules/**'],
  ...
```

---

### 8. Test Build

```bash
# Navigate to wiki-build
cd wiki/test-wiki-structure/wiki-build

# Install dependencies
npm install

# Build
npm run build
```

**Expected output:**
```
vitepress v1.x.x
building client + server bundles...
✓ building client + server bundles...
building client + server bundles...
✓ building client + server bundles...
rendering pages...
✓ rendering pages...
build complete in xxxs
```

**Output directory:**
```
wiki/test-wiki-structure/wiki-build/dist/
```

---

## Troubleshooting

### Issue: `pi update` shows "Already up to date" but files are old

**Solution:** Force pull the latest changes

```bash
cd ~/.pi/agent/git/github.com/carlosfrias/project-blueprint
git fetch origin
git reset --hard origin/main
git log --oneline -3  # Should show 934e0eb
```

---

### Issue: Templates still show old srcDir

**Solution:** Verify the template file was updated

```bash
# Check file modification time
ls -la skills/project-blueprint/templates/wiki-build-config.js

# Check content
cat skills/project-blueprint/templates/wiki-build-config.js | grep srcDir

# If still wrong, manually pull
cd ~/.pi/agent/git/github.com/carlosfrias/project-blueprint
git pull origin main
```

---

### Issue: wiki-build created as sibling instead of subdirectory

**Root Cause:** Old cached templates or skill not reloaded

**Solution:**

```bash
# 1. Verify standalone repo is updated
cd ~/.pi/agent/git/github.com/carlosfrias/project-blueprint
git log --oneline -1  # Should be 934e0eb

# 2. Force reload pi
exit
pi

# 3. Try project creation again
cd ~/test-wiki-build-2
pi skill project-blueprint
```

---

### Issue: Build fails with "srcDir not found"

**Solution:** Check VitePress config path

```bash
# The config should use relative paths
cat wiki/test-wiki-structure/wiki-build/.vitepress/config.js | grep srcDir

# Should be: srcDir: '.'
# NOT: srcDir: '../' or srcDir: '{wiki_src_dir}'
```

---

## Success Criteria

✅ All of these must be true:

- [ ] `git log` shows commit `934e0eb`
- [ ] Template `wiki-build-config.js` has `srcDir: '.'`
- [ ] SKILL.md Phase 8b mentions "inside the wiki directory"
- [ ] New project creates `wiki/{name}/wiki-build/` (not sibling)
- [ ] VitePress build succeeds from new location
- [ ] dist/ folder is at `wiki/{name}/wiki-build/dist/`

---

## Commit Reference

```
Commit: 934e0ebfd5ae864c3b65bdf6a324ffcd3c34060d
Author: AI Agent (Trading Desk)
Date:   2026-05-07
Message: fix: wiki-build templates - create as wiki subdirectory

CRITICAL FIX: Ensures wiki-build is created under wiki/{project-name}/

Changes:
- wiki-build-config.js: srcDir: '.' (reads from parent dir)
- wiki-build-README.md: updated paths to wiki/{project-name}/wiki-build/
- SKILL.md Phase 8b: correct directory structure instructions
```

---

## Remote Verification

```bash
# Verify commit is on remote
git ls-remote origin main
# Expected: 934e0ebfd5ae864c3b65bdf6a324ffcd3c34060d	refs/heads/main

# Or check via GitHub API
curl -s https://api.github.com/repos/carlosfrias/project-blueprint/git/refs/heads/main
```

---

**Status:** 🟢 **READY FOR TESTING**  
**Next:** Run verification steps on Ubuntu VM
