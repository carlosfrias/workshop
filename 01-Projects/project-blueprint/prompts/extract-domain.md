---
description: Extract a domain from the current project as a self-contained package for a new workspace
argument-hint: "<domain-name> [destination]"
---
Extract the domain "$1" from this project as a self-contained package.

Read the skill at ~/.pi/agent/skills/project-blueprint/SKILL.md for full instructions, specifically the "Extract Domain" section.

**Before extracting**, ask me the interview questions the skill defines:
1. Which domain to extract? (default: "$1")
2. Extract destination? (default: `./extracted-<domain-name>/`)
3. Include wiki content? (default: yes)
4. Include relevant _meta pages? (default: yes)
5. Include chains involving this domain? (default: all chains mentioning domain)
6. Generate workspace scaffold? (default: yes)
7. Project name for new workspace? (default: same as domain name)

Then follow the skill's extract steps, making sure to:
- Copy the domain folder and agent definition
- Copy domain wiki content
- Copy relevant _meta and chain files
- Generate workspace scaffold (root AGENTS.md, APPEND_SYSTEM.md, wiki Home.md)
- Verify the extraction is self-contained with no references back to the source project
- Report the extraction summary