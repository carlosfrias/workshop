# Linear Script: add-domain (Project Blueprint)

**Target Tier:** <8K (Low Capacity)
**Token Budget:** ~1.5KB
**Objective:** Add a new domain to an existing orchestrated project, updating all 5 touchpoints.

## Context
Every domain touches 5 files that must stay in sync:
1. Directory: `<domain>/AGENTS.md`
2. Agent definition: `.pi/agents/<domain>.md`
3. Routing table: root `AGENTS.md`
4. Chain files: `.pi/agents/*.chain.md` (if domain joins workflows)
5. Wiki: `wiki/<project>/<domain>/`

Rules: `inheritProjectContext: false`, `cwd: ./<domain>`, domain AGENTS.md must be self-contained.

## Steps

### Phase 1: Interview
Ask the user:
1. Domain name (lowercase, single word, e.g., `compliance`)
2. Domain description (1-2 sentences)
3. Domain keywords (for routing, e.g., "regulations, audit")
4. Model for this domain's agent? (default: same as existing)
5. Check-back via intercom? (default: same as existing)
6. Chain workflows with other domains? (default: none)

### Phase 2: Create Domain Files
Create `<domain>/AGENTS.md` with:
- Title: "# AGENTS.md — <Domain Name>"
- Sections: Purpose, Conventions, Rules, Quality Checklist, Documentation Protocol
- Content from user's description and keywords

Create `.pi/agents/<domain>.md` with:
- Frontmatter: `name: <domain>`, `cwd: ./<domain>`, `inheritProjectContext: false`, `systemPromptMode: replace`
- Model: user's choice or default

### Phase 3: Update Routing
Add row to root `AGENTS.md` routing table:
`| <keywords> | ./<domain>/AGENTS.md |`

### Phase 4: Update Wiki
- Add domain to `wiki/<project>/Home.md` Domain Index table
- Create `wiki/<project>/<domain>/Activity Log.md`
- Update `_meta/Agent Definitions.md`

### Phase 5: Update Chains (if needed)
If domain joins workflows, create or update `.pi/agents/*.chain.md`.

### Phase 6: Verify
- [ ] All 5 touchpoints updated
- [ ] `inheritProjectContext: false` on new agent
- [ ] `cwd: ./<domain>` correct
- [ ] Routing table has new entry
- [ ] No duplicate content from other domains
- [ ] Wiki updated with new domain section