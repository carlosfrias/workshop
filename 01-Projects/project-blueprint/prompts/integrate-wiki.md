---
description: Consolidate scattered or legacy wiki content into the domain-centric wiki structure
argument-hint: "[--scan-only]"
---
Integrate the project wiki into the domain-centric layout.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Integrate Wiki" section.

**Before modifying anything**, scan the project for scattered wiki content and report findings:
- Numbered pages at wiki root (00 — Home.md, 01 — Philosophy & Architecture.md, etc.)
- Wiki directories inside domain folders (./<domain>/wiki/, ./<domain>/docs/)
- Orphaned markdown files in the wiki

**If `--scan-only` flag is provided**, only scan and report — do not make any changes.

**Otherwise**, after scanning, ask me the interview questions the skill defines for integrate-wiki:
1. Migration strategy for legacy numbered pages (move to _meta/, archive, or delete)
2. Domain wiki content handling (move to central wiki or link)
3. Whether to preserve originals as backup

Then follow the skill's integrate steps, making sure to:
- Move numbered reference pages to `_meta/` (stripping the `NN — ` prefix)
- Consolidate in-domain wiki content to `wiki/<project>/<domain>/`
- Rebuild Home.md for domain-centric layout
- Update VitePress config if it exists
- Verify all links and report what was done