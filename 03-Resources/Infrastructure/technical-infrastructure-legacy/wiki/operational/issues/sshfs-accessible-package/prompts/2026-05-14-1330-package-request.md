# Prompt Capture — Package Request

**Captured:** 2026-05-14 13:30 ET
**Source:** User (via orchestrator session)
**Issue:** [sshfs-accessible-package](../0-ISSUE.md)
**Written via:** fnet2 SSHFS mount → orchestrator workspace

---

## Verbatim Prompt

> Please package SSHFS functionality as a standalone skill with a private git repository. Code workspace can be technical-infrastructure/packages/sshfs-accessible. The skill must be installable with `pi install` and updated with `pi update`. Ensure that the map of nodes that will be configured using sshfs is exposed in a json file that the user can update for installation or changing of the topology. Ensure that this backlog, session notes, full and comprehensive documentation is provided following the doc-standards skill and the documentation is kept on the technical-infrastructure/wiki/operational/. Route through labs for all work to the degree possible. Use the SSHFS functionality to mount necessary folders on lab nodes so that work can be carried out on those nodes. Commit and push to repo all updates.

## Parsed Requirements

1. Standalone skill with private git repo → `github.com/carlosfrias/sshfs-accessible`
2. Installable: `pi install`, updatable: `pi update`
3. User-editable `nodes.json` for topology
4. Documentation follows doc-standards LOD framework
5. Documentation in `technical-infrastructure/wiki/operational/`
6. Route work through lab nodes via SSHFS
7. Commit and push all changes
8. Scripts colocated with skill — no pollution outside package directory

## Lessons

- Pi packages support git installs via `pi install git:github.com/user/repo`
- Agent Skills standard requires SKILL.md with specific frontmatter
- Package is self-contained in `technical-infrastructure/packages/sshfs-accessible/`
- SSHFS mounts enable lab nodes to read/write documentation directly to workspace
- bash 3.2 (macOS default) lacks `mapfile`; use `while read` for portability
