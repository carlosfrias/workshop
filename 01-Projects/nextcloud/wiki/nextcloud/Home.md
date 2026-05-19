# NextCloud — Wiki Home

This wiki documents the NextCloud installation project for the home lab. Domains are the primary content — each domain owns its section and maintains it.

## Domain Index

| Domain | Activity Log | Description |
|--------|-------------|-------------|
| Infrastructure | [infrastructure/Activity Log](infrastructure/Activity%20Log.md) | Ansible, Docker, deployment, operations |
| Research | [research/Activity Log](research/Activity%20Log.md) | Knowledge gathering, how-to notes, Ansible role evaluation |

## Project Status

| Item | Status | Notes |
|------|--------|-------|
| TI-006: NextCloud Installation | 🟡 Proposed | Backlog item, priority Low |
| Designated node: fnet2 | ✅ Designated | 192.168.0.142, 31GB RAM, Intel i7 |
| Docker installed on fnet2 | ✅ Done | Prerequisites in autoinstall |
| Ansible access to fnet2 | ✅ Done | SSH key-based auth |
| NextCloud deployed | ❌ Not started | This is TI-006 |
| DNS configured (nextcloud.home) | ❌ Not started | Depends on dnsmasq setup |
| External access (OPNsense) | ❌ Deferred | TI-008, requires hardware |

## Architecture Summary

```
                      ┌─────────────────────┐
                      │  Lab Network         │
                      │  192.168.0.0/24      │
                      │                      │
                      │  ┌─────────────┐     │
  Client Devices ─────┤  │  fnet2      │     │
  (Desktop, Phone) ────┤  │  NextCloud  │     │
                      │  │  :8080       │     │
                      │  └─────────────┘     │
                      │                      │
                      │  ┌─────────────┐     │
                      │  │  fnet3      │     │
                      │  │  ChromaDB   │     │
                      │  └─────────────┘     │
                      │                      │
                      │  ┌─────────────┐     │
                      │  │  Orchestrator│    │
                      │  │  Ansible    │     │
                      │  └─────────────┘     │
                      └─────────────────────┘
```

## Token Budget

| Role | Size | Content |
|------|------|---------|
| Orchestrator (permanent) | ~1.2KB | Identity + routing table |
| Sub-agent (infrastructure) | ~4.5KB | Full domain context, loaded once |

## Reference Documentation

Project-level reference pages live in [_meta/](_meta/):

- [Architecture](_meta/Architecture.md) — System design, stack decisions, network layout
- [Agent Definitions](_meta/Agent%20Definitions.md) — Agent configs and usage
- [Sample Prompts](_meta/Sample%20Prompts.md) — Ready-to-use prompts for common tasks

## Related Resources

| Resource | Location |
|----------|----------|
| Lab hardware specs | `../../../../03-Resources/Infrastructure/lab-specs/` |
| TI-006 Backlog entry | `../../../../03-Resources/Infrastructure/technical-infrastructure-legacy/wiki/operational/BACKLOG.md` |
| Vault knowledge notes | `../../../../../personal-vault/01-Projects/nextcloud/` |