---
description: Add a new domain to an existing orchestrated project (creates folder, AGENTS.md, agent definition, routing entry, wiki updates)
argument-hint: "<domain-name> <keywords>"
---
Add a new domain called "$1" to this project with keywords: ${@:2}

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Add a Domain" section.

Before creating anything, ask me the interview questions the skill defines for adding a domain (description, who uses it, model, check-back, chains). Then follow the skill's add steps, making sure to update all five touchpoints: domain directory + AGENTS.md, agent definition, routing table, chain files, and wiki.