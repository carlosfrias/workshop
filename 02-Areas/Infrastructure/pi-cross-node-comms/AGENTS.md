# AGENTS.md — pi-cross-node-comms (Workshop)

**Documentation home:** `../../personal-vault/01-Projects/pi-cross-node-comms/`  
**Source upstream:** Extracted from `https://github.com/disler/pi-vs-claude-code`

## [S-TIGHT]

Cross-node pi communication package. Extracted `coms-net` extension and hub server from the pi-vs-cc mono-repo. Includes fleet-dispatcher cascade for bridge decompose-execute-verify to fleet nodes. Hub server is Dockerized (Bun-based container, docker compose managed).

## Fleet Standup Rules

1. **HUB FIRST, THEN PI** — Start the hub before launching any pi sessions. The extension reads `server.json` only at init time; no hot-reload.
2. **Local dev:** Run `scripts/standup-hub.sh` → then start pi (extension auto-discovers `~/.pi/coms-net/projects/<project>/server.json`)
3. **Production (lab):** Run Ansible `standup-fleet.yml` (6-phase: Docker hub → pi → Ollama → extension → systemd agents → validate)
4. **If hub started after pi:** Must restart pi entirely. `/reload` does NOT re-read `server.json` (tested 2026-05-24).
5. **Fixed port:** Local dev uses port 6420 to avoid ephemeral port confusion. Production uses port 8080 (Docker on fnet2)
6. **Remote agents ALWAYS need `--server-url` and `--auth-token`** — they cannot read fnet2's `server.json`
7. **Kill old hub before starting new** — `scripts/shutdown-hub.sh` or `pkill -f coms-net-server.ts`
8. **Token strategy:** Loopback auto-generates + writes `server.secret.json` (0600). For LAN/Docker, set `PI_COMS_NET_AUTH_TOKEN` explicitly.
9. **Shutdown fleet:** `scripts/shutdown-hub.sh` (local) or `ansible-playbook shutdown-fleet.yml` (production)

## Tech Stack

| Component | Technology | Entry |
|-----------|-----------|-------|
| Extension (client) | TypeScript | `src/index.ts` |
| Hub server | Bun / Docker | `server/coms-net-server.ts` → `Dockerfile` |
| Container orchestration | Docker Compose | `docker-compose.yml` |
| Theme utility | TypeScript | `src/themeMap.ts` |
| Node resolver | TypeScript | `src/resolve-node.ts` |
| Heartbeat tick | TypeScript | `src/heartbeat-tick.ts` |
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
│   ├── shutdown-fleet.yml   # 3-phase shutdown (stop agents → stop hub → verify)
│   ├── deploy-hub-to-fnet2.yml
│   ├── deploy-fleet.yml
│   ├── start-agents.yml
│   └── inventory.yml
├── src/
│   ├── index.ts             # Main extension (coms-net client)
│   ├── resolve-node.ts      # Node name resolution (flag > env > hostname > fallback)
│   ├── heartbeat-tick.ts    # Extracted heartbeat logic with stale-ctx protection
│   ├── themeMap.ts          # Theme defaults
│   └── skills/
│       └── pi-cross-node-comms/
│           └── SKILL.md     # Agent usage patterns
├── scripts/
│   ├── standup-hub.sh       # Local dev: kill old → start hub → verify → print URL
│   ├── shutdown-hub.sh      # Local dev: kill hub → clean state files
│   └── setup-hub-on-fnet2.sh # Legacy: manual hub setup on fnet2 (Bun-based)
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
| **Standup fleet (production)** | `ansible-playbook -i ansible/inventory.yml ansible/standup-fleet.yml` |
| **Standup fleet (playbook-executor)** | `scripts/run-playbook.sh "stand up the fleet"` |
| **Standup hub (local dev)** | `scripts/standup-hub.sh [--port PORT] [--project PROJECT]` |
| **Shutdown fleet (production)** | `ansible-playbook -i ansible/inventory.yml ansible/shutdown-fleet.yml` |
| **Shutdown fleet (playbook-executor)** | `scripts/run-playbook.sh "shutdown fleet"` |
| **Shutdown hub (local dev)** | `scripts/shutdown-hub.sh [--project PROJECT]` |
| **D-E-V cascade** | In pi session: decomposer → fleet-dispatcher → verifier → bookkeeping |
| Install extension | `pi install .` (from this directory) |
| Launch agent with extension | `pi -e src/index.ts --server-url http://host:port --auth-token TOKEN --name agent-name --project lab` |
| Launch with custom node name | `pi -e src/index.ts --node fnet2 --server-url ...` or `PI_COMS_NET_NODE=fnet2 pi -e src/index.ts ...` |

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

## Node Identity Rules

1. **Node must be a hostname or IP address** — never an agent name, generated ID, "unknown", or "undefined"
2. **Resolution priority:** `--node` flag > `PI_COMS_NET_NODE` env > `os.hostname()` > `"unknown"` fallback
3. Server validates at registration: `isValidNodeName()` rejects `agent-XXXXXX`, all-uppercase codes, fallback names
4. Widget shows `[?]` when node is invalid — never shows agent name in node position
5. `coms_net_list` output includes `@node` prefix only for valid hostnames/IPs
6. **Previous bug (fixed 2026-05-27):** `os.hostname()` was used directly with no override — every agent on `mac-orchestrator` showed that hostname. Now operators set `--node fnet2` or `PI_COMS_NET_NODE=fnet2` to override.
7. Audit log: When node resolution falls to "unknown", extension logs `node_resolution_fallback` event with source and attempted values
8. **SSE node propagation (fixed 2026-05-27):** `agent_updated` and `prompt` events now include `node` field. Previously, peer node was lost on heartbeat updates and inbound prompts showed no sender node.
9. **Inbound message format:** `[from [fnet3] planner @ /cwd]` — node prefix shown for known nodes, omitted for `?`

## Capability-Aware Routing

1. **Capabilities are advertised at registration** — `capabilities` field in AgentCard includes `video-inference`, `image-inference`, `audio-inference`, `file-system`
2. **Fleet-dispatcher filters by capability** — video tasks require `video-inference` capability peer
3. **No capable peer → immediate degradation to Tier 2 (intercom)** without attempting Tier 1
4. **Capability detection:** GPU (Metal/CUDA), ffmpeg, `PI_VISION_PROXY_VIDEO_MODEL` env var

## Cost-Control Hard Constraints

1. **`coms_net_await` timeout: 120s max** — never rely on the 30-minute default
2. **Always pass `timeout_ms` explicitly** to `coms_net_await`
3. **Pre-flight `coms_net_list`** before any Tier 1 dispatch
4. **Immediate degradation** on timeout — never retry same peer

## Must Never

- Commit `.env` files or auth tokens
- Store documentation here (docs live in personal-vault)
- Develop directly in `.pi/` folders — always work in workshop, commit, push, `pi update`
- Use `coms_net_await` without explicit `timeout_ms` parameter
- Display agent names as node identifiers in the TUI

## Test Command

```bash
bun test                    # full suite (250 tests, 15 files)
bun test tests/resolve-node.test.ts     # node resolution priority chain
bun test tests/node-identity.test.ts   # node validation logic
bun test tests/tui-footer-node.test.ts  # TUI node display
bun test tests/heartbeat-tick.test.ts  # heartbeat stale-ctx protection
bun test tests/inbound-prompt-node.test.ts  # sender_node in inbound prompts
bun test server/__tests__/server-sse-node.test.ts  # SSE events include node
bun test server/__tests__/node-name-integration.test.ts  # server node validation
```

## Conventions

- TypeScript, ES modules
- Server requires Bun runtime
- Extension requires pi peer dependencies
- **Release flow:** workshop → commit → push → `pi update` (no shortcuts)

## Cross-Reference

| Need | Go Here |
|------|---------|
| Full assessment, pros/cons | `../../personal-vault/01-Projects/pi-cross-node-comms/1-ASSESSMENT.md` |
| Current state, priorities | `../../personal-vault/01-Projects/pi-cross-node-comms/FOCUS.md` |
| LOD manifest (low-capacity loading) | `../../personal-vault/01-Projects/pi-cross-node-comms/wiki/reference/LOD-MANIFEST.md` |
| Unified prompt (v1) | `../../personal-vault/01-Projects/pi-cross-node-comms/threads/pi-cross-node-comms/prompts/01-unified-prompt-v1.md` |