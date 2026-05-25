---
description: Rename an existing domain across all project files (folder, agent, routing table, chains, wiki)
argument-hint: "<old-name> <new-name>"
---
Rename the domain "$1" to "$2" across this project.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Rename a Domain" section.

Before making changes, ask me the interview questions the skill defines for renaming (new keywords, new description). Then follow the skill's rename steps, making sure to update all five touchpoints: domain directory + AGENTS.md, agent definition (name + cwd), routing table, chain files, and wiki. After renaming, grep for the old name to confirm no stale references remain.