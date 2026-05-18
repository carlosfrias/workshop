---
name: project-blueprint/wiki-integrate
description: Consolidate scattered or legacy wiki content into domain-centric structure.
---


## [S-TIGHT]

Consolidate scattered or legacy wiki content into domain-centric structure. Move numbered reference pages to _meta/, consolidate domain wikis into central location.
## Wiki Cross-Reference

After setup, update the project wiki to include:
- `_meta/` reference pages about the project architecture, agents, chains, and system design
- Sample prompts in `_meta/Sample Prompts` that would trigger domain agents for common tasks
- Home page Domain Index with links to each domain's wiki section
- Cross-references between domain wiki content and `_meta/` reference pages where relevant

---

## Integrate Wiki

Consolidates scattered or legacy wiki content into the domain-centric wiki structure. Use when a project was created before the domain-centric wiki layout, or when wikis exist inside domain folders instead of the central wiki.

### When to Use

- Existing project has numbered pages at wiki root (`00 — Home.md`, `01 — Philosophy & Architecture.md`, etc.)
- Domain folders contain their own wiki subdirectories (old pattern: `./<domain>/wiki/`)
- Wiki content is fragmented across multiple locations
- Migrating from an older project-blueprint version

### Integrate: Interview

Ask the user:
1. **Scan scope** — Scan the entire project for scattered wiki content, or focus on specific locations?
2. **Migration strategy** — For legacy numbered pages at wiki root:
   - **Move to `_meta/`** — Rename and relocate reference pages (architecture, agents, sample prompts). Default.
   - **Archive** — Move to `_meta/archive/` and create fresh reference pages from templates.
   - **Delete** — Remove legacy pages entirely and regenerate from templates.
3. **Domain wiki content** — If domains have their own wiki folders (e.g., `./<domain>/wiki/`), should the content be:
   - **Moved** to `wiki/<project>/<domain>/` (default — consolidates into central wiki)
   - **Linked** — Leave in place, add symlinks or navigation links from central wiki
4. **Preserve history** — Keep original files as backup before moving? Default: yes (copy, don't move).

### Integrate: Steps

1. **Scan for scattered wiki content** — Walk the project directory looking for:
   - Numbered pages at wiki root (pattern: `NN — *.md` in `wiki/<project>/`)
   - Wiki directories inside domain folders (pattern: `./<domain>/wiki/` or `./<domain>/docs/`)
   - Orphaned markdown files in `wiki/` that don't match the new structure
   - Activity logs in non-standard locations

2. **Create `_meta/` directory** — If it doesn't exist, create `wiki/<project>/_meta/`.

3. **Relocate numbered reference pages** — For each numbered page found at wiki root:
   - Strip the numbered prefix (e.g., `01 — Philosophy & Architecture.md` → `Architecture.md`)
   - Move or copy to `wiki/<project>/_meta/`
   - Update any internal wiki links that reference the old paths
   - Report what was moved

4. **Consolidate domain wiki content** — For each domain with wiki content inside its folder:
   - Identify wiki files in `./<domain>/wiki/` or similar
   - Ensure `wiki/<project>/<domain>/` exists
   - Move content to `wiki/<project>/<domain>/`, preserving directory structure
   - Verify Activity Log.md exists; create from template if missing
   - Remove the old in-domain wiki directory if content was moved successfully

5. **Rebuild Home.md** — Replace or update the wiki home page:
   - Create Domain Index table listing all domains with links to Activity Logs
   - Add Reference Documentation section linking to `_meta/` pages
   - Add Project Structure diagram reflecting the new layout
   - Add Token Budget summary

6. **Update VitePress config** — If `wiki-build/` exists:
   - Reorganize sidebar: domains first (expanded), `_meta/` reference collapsed
   - Update navigation links to reflect new `_meta/` paths
   - Remove references to old numbered page paths

7. **Verify integration** —
   - Confirm all numbered pages have been moved from wiki root
   - Confirm each domain has a wiki directory at `wiki/<project>/<domain>/`
   - Confirm `_meta/` contains all reference pages
   - Confirm Home.md links are valid
   - Confirm VitePress sidebar matches actual file layout
   - Grep for old numbered page paths (`01 — `, `02 — `, etc.) to find stale references

### Integrate: Expected Output

```
Wiki Integration Report
────────────────────────────────────────
Scanned: 4 locations with scattered content

Moved to _meta/:
  01 — Philosophy & Architecture.md → _meta/Architecture.md
  02 — Agent Definitions.md         → _meta/Agent Definitions.md
  03 — Chain Files.md               → _meta/Chain Files.md
  04 — System & Context Files.md    → _meta/System & Context Files.md
  05 — Sample Prompts.md            → _meta/Sample Prompts.md
  06 — Model Substitutions.md       → _meta/Model Substitutions.md

Domain wiki consolidated:
  ./bookkeeping/wiki/ → wiki/project/bookkeeping/ (3 files moved)
  ./market-research/docs/ → wiki/project/market-research/ (2 files moved)

Created:
  wiki/project/Home.md (replaced old 00 — Home.md)
  wiki/project/_meta/ (6 reference pages)

Updated:
  wiki/project/wiki-build/.vitepress/config.js (sidebar reorganized)

Stale references found: 0
────────────────────────────────────────
```

### Integrate: Critical Rules

- **Never delete wiki content without explicit user confirmation.** Always offer backup/preserve options.
- **Always scan before modifying.** Report what was found and get user approval before moving anything.
- **Numbered pages must lose their prefixes** when moved to `_meta/`. The `NN — ` prefix was for root-level ordering; it's meaningless inside `_meta/`.
- **Domain wiki content belongs in the central wiki** (`wiki/<project>/<domain>/`), not inside domain folders. This is the core principle: domains maintain their space on the wiki, not a private wiki.
- **Verify links after integration.** Moving files breaks internal wiki links. Update all references.

---

