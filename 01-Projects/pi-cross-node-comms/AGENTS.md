# AGENTS.md — pi-cross-node-comms (Workshop)

**Documentation home:** `../../personal-vault/01-Projects/pi-cross-node-comms/`  
**Source upstream:** Extracted from `https://github.com/disler/pi-vs-claude-code`

## [S-TIGHT]

Cross-node pi communication package. Extracted `coms-net` extension and hub server from the pi-vs-cc mono-repo. Includes fleet-dispatcher cascade for bridge decompose-execute-verify to fleet nodes. Hub server is Dockerized (Bun-based container, docker compose managed).

## Tech Stack

| Component | Technology | Entry |
|-----------|-----------|-------|
| Extension (client) | TypeScript | `src/index.ts` |
| Hub server | Bun / Docker | `server/coms-net-server.ts` → `Dockerfile` |
| Container orchestration | Docker Compose | `docker-compose.yml` |
| Theme utility | TypeScript | `src/themeMap.ts` |
| Fleet-Dispatcher | Agent definition | `../../workshop/.pi/agents/fleet-dispatcher.md` |

## Directory Structure

```
pi-cross-node-comms/
├── Dockerfile              # Hub container image
├── docker-compose.yml      # Hub container config
├── .dockerignore            # Build context filter
├── AGENTS.md                ← YOU ARE HERE
├── README.md                ← Quick start
├── package.json
├── ansible/
│   ├── standup-fleet.yml    # 6-phase unified playbook (hub+pi+ollama+ext+agents+prune)
│   ├── deploy-hub-to-fnet2.yml
│   ├── deploy-fleet.yml
│   ├── start-agents.yml
│   └── inventory.yml
├── src/
│   ├── index.ts             # Main extension (coms-net client)
│   ├── themeMap.ts          # Theme defaults
│   └── skills/
│       └── pi-cross-node-comms/
│           └── SKILL.md     # Agent usage patterns
├── scripts/
│   └── setup-hub-on-fnet2.sh
└── server/
    └── coms-net-server.ts   # Bun HTTP/SSE hub server
```

## D-E-V Fleet Cascade

The decompose-execute-verify pipeline routes execution through a three-tier cascade:

1. **Tier 1 (fleet):** `coms_net_send/await` to remote pi agents on fnet3–7
2. **Tier 2 (intercom):** `intercom ask` to local pi sessions
3. **Tier 3 (subagent):** Built-in `subagent()` tool (always available)

The cascade is per-sub-task. Decomposer plans are tier-agnostic. Verifier is tier-agnostic. Only the fleet-dispatcher changes the dispatch mechanism.

## Entry Points

| Task | Command |
|------|--------|
| **Standup fleet (unified)** | `./scripts/run-playbook.sh "stand up the fleet"` or `ansible-playbook -i ansible/inventory.yml ansible/standup-fleet.yml` (Phase 1 now deploys hub via Docker) |
| **D-E-V cascade** | In pi session: decomposer → fleet-dispatcher → verifier → bookkeeping |
| Start hub server | `docker compose up -d` (from this directory) or `PI_COMS_NET_AUTH_TOKEN=<token> docker compose up -d` |
| Install extension | `pi install .` (from this directory) |
| Launch agent with extension | `pi --server-url http://host:port --name agent-name --project lab` |

## Prompt

| Prompt | File |
|--------|------|
| Unified prompt (v2 — current) | `../../personal-vault/01-Projects/pi-cross-node-comms/threads/pi-cross-node-comms/prompts/02-unified-prompt-v2.md` |
| Unified prompt (v1 — preserved) | `../../personal-vault/01-Projects/pi-cross-node-comms/threads/pi-cross-node-comms/prompts/01-unified-prompt-v1.md` |

## Two Locations Mandate

| Location | Purpose | Path |
|----------|---------|------|
| **Workspace Root** | Code, config, agents, playbooks | `./` (this directory) |
| **Documentation Home** | Wiki, threads, sessions, FOCUS.md | `../../personal-vault/01-Projects/pi-cross-node-comms/` |

**Rule:** Documentation NEVER lives in the code tree. All docs live in personal-vault. Code NEVER lives in personal-vault.

## Conventions

- TypeScript, ES modules
- Server requires Bun runtime
- Extension requires pi peer dependencies

## Must Never

- Commit `.env` files or auth tokens
- Store documentation here (docs live in personal-vault)

## Cross-Reference

| Need | Go Here |
|------|---------|
| Full assessment, pros/cons | `../../personal-vault/01-Projects/pi-cross-node-comms/1-ASSESSMENT.md` |
| Current state, priorities | `../../personal-vault/01-Projects/pi-cross-node-comms/FOCUS.md` |
| LOD manifest (low-capacity loading) | `../../personal-vault/01-Projects/pi-cross-node-comms/wiki/reference/LOD-MANIFEST.md` |
| Unified prompt (v1) | `../../personal-vault/01-Projects/pi-cross-node-comms/threads/pi-cross-node-comms/prompts/01-unified-prompt-v1.md` |