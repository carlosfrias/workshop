---
description: Remove a domain entirely from the project (folder, agent, routing entry, chains, wiki — with confirmation)
argument-hint: "<domain-name>"
---
Remove the domain "$1" entirely from this project.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Remove a Domain" section.

Before deleting anything, ask me the confirmation questions the skill defines: should chains be removed or updated, should wiki content be removed, and has the domain's data been preserved. Then follow the skill's remove steps, making sure to update all five touchpoints: domain directory, agent definition, routing table, chain files, and wiki. After removal, verify no stale references remain.