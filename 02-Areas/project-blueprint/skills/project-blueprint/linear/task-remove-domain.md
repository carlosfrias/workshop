# Linear Script: remove-domain (Project Blueprint)

**Target Tier:** <8K (Low Capacity)
**Token Budget:** ~1.5KB
**Objective:** Remove a domain entirely from an orchestrated project, updating all 5 touchpoints.

## Context
Removing a domain is DESTRUCTIVE and cannot be undone without version control. It touches the same 5 files as adding:
1. Directory: `<domain>/AGENTS.md` → DELETE
2. Agent definition: `.pi/agents/<domain>.md` → DELETE
3. Routing table: root `AGENTS.md` → REMOVE row
4. Chain files: `.pi/agents/*.chain.md` → UPDATE or DELETE
5. Wiki: `wiki/<project>/<domain>/` → DELETE

## Steps

### Phase 1: Confirmation
Before any deletion, confirm with the user:
1. Which domain to remove?
2. Delete chain files that only involve this domain's agent? (Yes/No)
3. Delete wiki content for this domain? (Yes/No — historical docs may be useful)
4. Does the domain folder contain DATA files (not just AGENTS.md)? If yes, confirm deletion.

### Phase 2: Remove Domain Files
- Delete `./<domain>/` directory (after data confirmation)
- Delete `.pi/agents/<domain>.md`

### Phase 3: Remove Chain References
- If a chain file ONLY involves this domain's agent → delete the chain file
- If this domain is ONE STEP in a multi-domain chain → remove just that step from the chain

### Phase 4: Update Routing Table
Remove the domain's row from root `AGENTS.md` routing table.

### Phase 5: Update Wiki
- Remove `wiki/<project>/<domain>/` directory (if confirmed)
- Remove domain from `Home.md` Domain Index table
- Remove from `_meta/Agent Definitions.md`
- Remove from `_meta/Sample Prompts.md`

### Phase 6: Verify
- [ ] Domain directory deleted
- [ ] Agent definition deleted
- [ ] Routing table has no entry for removed domain
- [ ] Chain files updated (no references to deleted agent)
- [ ] Wiki updated (no stale references)
- [ ] Grep project for domain name — no stale references remain
- [ ] Token budget recalculated (routing table shorter = orchestrator load smaller)

## Critical Rules
- ALWAYS confirm before deleting
- Chain files that reference deleted agents will FAIL at runtime — must update
- Stale routing entries cause orchestrator to read nonexistent files — must remove