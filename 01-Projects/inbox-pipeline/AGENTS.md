# AGENTS.md — Inbox Pipeline

**Purpose:** Unified message ingestion from email (IMAP) and Telegram into an agent-accessible inbox.  
**Last updated:** 2026-05-25

---

## Summary

Ingest email and Telegram messages into a structured SQLite inbox. Agents query via read-only access. Pipeline is provider-agnostic — IMAP for email, Bot API for Telegram.

---

## Conventions

- **Timestamps:** ISO 8601 UTC in store. Display in local when human-facing.
- **Message IDs:** Preserve provider IDs (`source_id`) for deduplication.
- **Credentials:** From environment variables only. Never hardcoded.
- **Store location:** `./data/inbox.db` — created automatically on first run.

---

## Domain Routing

| Keywords | Read this file |
|----------|---------------|
| email, IMAP, gmail, outlook, fetch mail | `./email-ingestion/AGENTS.md` |
| telegram, bot, message, chat, webhook | `./telegram-ingestion/AGENTS.md` |
| inbox, store, database, schema, query | `./scripts/inbox_store.py` |
| wiki, documentation, architecture | `../../personal-vault/01-Projects/inbox-pipeline/wiki/inbox-pipeline/Home.md` |

---

## Cross-References

- [Vault docs](../../personal-vault/01-Projects/inbox-pipeline/) — PLAN, FOCUS, WORKBENCH, wiki
- [email-ingestion](./email-ingestion/AGENTS.md) — IMAP fetch domain
- [telegram-ingestion](./telegram-ingestion/AGENTS.md) — Bot API domain
