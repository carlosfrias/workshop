---
name: project-blueprint/domain-extract
description: Extract a domain as a self-contained package for reuse or new workspaces.
---


## [S-TIGHT]

Extract a domain as a self-contained package for reuse. Copy domain folder, agent definition, wiki content, chains, and optionally scaffold a new workspace.
## Extract Domain

Extracts a domain from the current project as a self-contained package that can seed a new workspace. This is the inverse of "Add a Domain" — instead of adding a domain to a project, you take one out to build something new.

### When to Use

- Building a new workspace around an existing domain's capability
- Sharing a domain pattern across projects
- Simplifying a project by splitting off an independent concern
- Creating a template from a well-functioning domain

### Extract: Interview

Ask the user:
1. **Which domain?** — Name of the domain to extract.
2. **Extract destination** — Where should the extracted package go? Default: `./extracted-<domain-name>/`
3. **Include wiki content?** — Should the domain's wiki content (`wiki/<project>/<domain>/`) be included? Default: yes.
4. **Include relevant _meta pages?** — Should reference pages from `_meta/` that relate to this domain be included? Default: yes (copies of architecture, agent definitions, sample prompts relevant to this domain).
5. **Include chains?** — Should chains that involve this domain be included? Options:
   - **All chains mentioning this domain** (default)
   - **Only single-domain chains** (chains where this domain is the sole participant)
   - **No chains**
6. **Generate workspace scaffold?** — Should the extraction create a minimal root `AGENTS.md`, `.pi/APPEND_SYSTEM.md`, and wiki structure so the package is immediately usable as a new workspace? Default: yes.
7. **Project name for new workspace** — If generating a scaffold, what should the new project be called? Default: same as the extracted domain name.

### Extract: Steps

1. **Create the extraction directory** — `mkdir -p <destination>`

2. **Copy the domain folder** — Copy `./<domain>/` (including `AGENTS.md` and all files) to `<destination>/<domain>/`.

3. **Copy the domain's agent definition** — Copy `.pi/agents/<domain>.md` to `<destination>/.pi/agents/<domain>.md`.

4. **Copy domain wiki content** — If the domain has wiki content at `wiki/<project>/<domain>/`, copy it to `<destination>/wiki/<new-project>/<domain>/`.

5. **Copy relevant _meta pages** — Copy `_meta/` pages that reference this domain:
   - `Agent Definitions.md` (extract only this domain's agent section)
   - `Sample Prompts.md` (extract only this domain's prompts)
   - `Architecture.md` (copy as-is, it's project-wide)
   - Any other `_meta/` pages that mention the domain
   Place them in `<destination>/wiki/<new-project>/_meta/`.

6. **Copy relevant chains** — For each chain that involves this domain:
   - If the chain only involves this domain, copy it entirely
   - If the chain involves other domains, copy it but mark other-domain steps as stubs with a comment indicating the original agent name.
   Place chains in `<destination>/.pi/agents/`.

7. **Generate workspace scaffold** (if requested) — Create:
   - `<destination>/AGENTS.md` — Minimal root routing table with just this domain
   - `<destination>/.pi/APPEND_SYSTEM.md` — Identity file
   - `<destination>/wiki/<new-project>/Home.md` — Wiki home with single domain
   - `<destination>/wiki/<new-project>/<domain>/Activity Log.md` — If not already present from wiki copy
   Use the standard templates (`AGENTS-root.md`, `APPEND_SYSTEM.md`, `wiki-home.md`) customized for a single-domain workspace.

8. **Verify extraction** —
   - Confirm the destination directory contains a complete, self-contained structure
   - Confirm all internal links and references point to valid files within the extraction
   - Confirm the domain `AGENTS.md` is self-contained (no references to the original project's files)
   - Confirm the agent definition has correct `cwd` and `name`
   - Confirm the routing table (if scaffolded) points to the domain
   - Run `ls -la` on the destination and report the structure

### Extract: Expected Output

```
Domain Extraction Report
────────────────────────────────────────
Extracted: bookkeeping
Destination: ./extracted-bookkeeping/

Copied:
  ./bookkeeping/                         → extracted-bookkeeping/bookkeeping/
  .pi/agents/bookkeeping.md              → extracted-bookkeeping/.pi/agents/bookkeeping.md
  wiki/project/bookkeeping/              → extracted-bookkeeping/wiki/bookkeeping/bookkeeping/

Chains copied:
  .pi/agents/bookkeeping-trade-log.chain.md (involves bookkeeping)

Generated scaffold:
  extracted-bookkeeping/AGENTS.md         (routing table with bookkeeping)
  extracted-bookbreaking/.pi/APPEND_SYSTEM.md
  extracted-bookkeeping/wiki/bookkeeping/Home.md
  extracted-bookkeeping/wiki/bookkeeping/_meta/Architecture.md
  extracted-bookkeeping/wiki/bookkeeping/_meta/Agent Definitions.md
  extracted-bookkeeping/wiki/bookkeeping/_meta/Sample Prompts.md

Verification: PASS
  All references point to valid files within extraction
  Domain AGENTS.md is self-contained
  Routing table correctly routes to ./bookkeeping/AGENTS.md
────────────────────────────────────────
```

### Extract: Critical Rules

- **Never modify the original project.** Extraction is a read + copy operation. The source project remains untouched.
- **The extracted domain must be self-contained.** After extraction, it should work as an independent workspace without references back to the source project.
- **All internal references must be localized.** Any paths, links, or references that pointed to the original project structure must be updated to work within the extraction.
- **Chains that span multiple domains require attention.** A chain that steps through both `bookkeeping` and `position-management` can't work if only `bookkeeping` is extracted. Mark the other-domain steps as stubs.
- **Wiki content must be re-rooted.** The domain's wiki content in the original project lives under `wiki/<old-project>/<domain>/`. In the extraction, it lives under `wiki/<new-project>/<domain>/`. All internal links must be updated.