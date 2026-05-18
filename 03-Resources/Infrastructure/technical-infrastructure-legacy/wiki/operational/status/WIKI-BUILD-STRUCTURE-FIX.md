# Wiki Build Structure Fix: wiki-build as Subdirectory

**Date:** 2026-05-07  
**Commit:** `5620dbf fix: place wiki-build as subdirectory of wiki directory`  
**Status:** ✅ **DEPLOYED**

---

## Problem Identified

The `wiki-build/` directory was being created **alongside** the wiki directory:

```
❌ OLD (Incorrect):
project-root/
├── wiki/
│   └── {project-name}/
│       └── *.md
└── wiki-build/           # Wrong location - sibling to wiki
    ├── .vitepress/
    └── dist/
```

This caused:
- Confusing directory structure
- Relative path issues in VitePress config
- Git ignore complications
- Harder to understand wiki organization

---

## Solution Implemented

The `wiki-build/` directory is now created **inside** the wiki directory as a subdirectory:

```
✅ NEW (Correct):
project-root/
└── wiki/
    └── {project-name}/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        ├── {domain1}/
        │   └── Activity Log.md
        └── wiki-build/           # Correct location - subdirectory
            ├── .vitepress/
            │   └── config.js
            ├── package.json
            └── dist/
```

---

## Changes Made

### 1. VitePress Configuration (`wiki-build-config.js`)

**Before:**
```javascript
srcDir: '{wiki_src_dir}',  // Had to point to parent directory
srcExclude: ['**/dist/**'],
```

**After:**
```javascript
srcDir: '.',               // Reads from current directory (parent of wiki-build)
srcExclude: ['**/wiki-build/**', '**/dist/**', '**/node_modules/**'],
```

**Impact:** VitePress now reads markdown files from the parent directory automatically.

---

### 2. Build Instructions (`wiki-build-README.md`)

**Before:**
```bash
cd wiki-build
npm install
npm run build
```

**After:**
```bash
cd wiki/{project-name}/wiki-build
npm install
npm run build
```

**Impact:** Clear path instructions for users.

---

### 3. Directory Structure Documentation

**Before:**
```
wiki-build/
├── .vitepress/
│   └── config.js
├── package.json
└── dist/
```

**After:**
```
wiki/
└── {project-name}/
    ├── 00 — Home.md
    ├── {domain1}/
    │   └── Activity Log.md
    └── wiki-build/
        ├── .vitepress/
        │   └── config.js
        ├── package.json
        └── dist/
```

**Impact:** Shows wiki-build as integrated part of wiki structure.

---

### 4. Git Ignore Instructions

**Before:**
```
wiki-build/dist/
wiki-build/node_modules/
```

**After:**
```
wiki/{project-name}/wiki-build/dist/
wiki/{project-name}/wiki-build/node_modules/
```

**Impact:** Correct paths for gitignore configuration.

---

### 5. Skill Implementation (`SKILL.md` Phase 8b)

Updated to reflect new structure:

**Before:**
> "create a `wiki-build/` directory **alongside** the markdown wiki"

**After:**
> "create a `wiki-build/` directory **inside the wiki directory** as a subdirectory"

**Impact:** Clear implementation instructions for agents.

---

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Organization** | Wiki and build separated | Build integrated under wiki |
| **Paths** | Complex relative paths | Simple `.` for srcDir |
| **Clarity** | Two sibling directories | One wiki directory with build |
| **Git Ignore** | Root-level paths | Scoped to wiki subdirectory |
| **User Experience** | Confusing structure | Intuitive hierarchy |

---

## Files Modified

| File | Changes |
|------|---------|
| `skills/project-blueprint/templates/wiki-build-config.js` | Changed `srcDir` to `.` and updated excludes |
| `skills/project-blueprint/templates/wiki-build-README.md` | Updated all paths and examples |
| `skills/project-blueprint/SKILL.md` | Updated Phase 8b instructions |

---

## Usage Example

When a user creates a new project:

```bash
pi skill project-blueprint

# Interview responses:
# Project name: "my-saas-platform"
# HTML wiki: yes
```

**Generated structure:**
```
my-saas-platform/
└── wiki/
    └── my-saas-platform/
        ├── 00 — Home.md
        ├── 01 — Philosophy & Architecture.md
        ├── bookkeeping/
        │   └── Activity Log.md
        └── wiki-build/              # ← Inside wiki directory
            ├── .vitepress/
            │   └── config.js
            ├── package.json
            └── README.md
```

**Build commands:**
```bash
cd wiki/my-saas-platform/wiki-build
npm install
npm run build
```

**Output:**
```
wiki/my-saas-platform/wiki-build/dist/  ← Ready to deploy
```

---

## Git Ignore Configuration

Add to project root `.gitignore`:

```bash
# Wiki build artifacts
wiki/*/wiki-build/dist/
wiki/*/wiki-build/node_modules/
```

Or for a specific project:

```bash
wiki/my-saas-platform/wiki-build/dist/
wiki/my-saas-platform/wiki-build/node_modules/
```

---

## Migration Guide (Existing Projects)

If you have an existing project with the old structure:

```bash
# 1. Move wiki-build into wiki directory
mv wiki-build wiki/{project-name}/

# 2. Update .gitignore
# Remove old entries:
#   wiki-build/dist/
#   wiki-build/node_modules/
# Add new entries:
#   wiki/{project-name}/wiki-build/dist/
#   wiki/{project-name}/wiki-build/node_modules/

# 3. Update VitePress config (if customized)
# Edit wiki/{project-name}/wiki-build/.vitepress/config.js
# Change srcDir if you modified it

# 4. Test build
cd wiki/{project-name}/wiki-build
npm install
npm run build
```

---

## Deployment Status

| Repository | Commit | Status |
|------------|--------|--------|
| `github.com:carlosfrias/project-blueprint` | `5620dbf` | ✅ Pushed |
| Tag | — | Patch fix (no new tag needed) |

---

## Testing Checklist

- [x] Templates updated with correct paths
- [x] SKILL.md Phase 8b updated
- [x] VitePress config uses `srcDir: '.'`
- [x] Git ignore instructions updated
- [x] Synced to standalone repository
- [ ] Test in new project creation
- [ ] Verify build works from new location
- [ ] Verify HTML output is correct

---

**Status:** ✅ **DEPLOYED TO STANDALONE REPO**  
**Next:** Test in fresh project creation workflow
