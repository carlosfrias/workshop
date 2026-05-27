# AGENTS.md — Telegram Ingestion

**Purpose:** Receive messages via Telegram Bot API (polling), normalize into inbox store.

---

## Summary

Poll Telegram Bot API for new messages. Store username, text, timestamp in SQLite inbox. Minimal setup — register bot with @BotFather, set token as env var.

---

## Conventions

- **Bot token:** `TELEGRAM_BOT_TOKEN` environment variable.
- **Polling interval:** 30 seconds. Configurable.
- **Message format:** `from.username`, `text`, `date` (Unix timestamp).
- **Deduplication:** By `update_id` from Telegram API.

---

## Rules

### Must Always
1. Use environment variable for bot token
2. Track `last_update_id` to avoid re-processing
3. Store raw message + parsed fields
4. Handle rate limits (429) with backoff

### Must Never
1. Never expose bot token in code or logs
2. Never respond to messages unless explicitly configured
3. Never store media without user consent

---

## Quality Checklist

- [ ] Bot token from env var only
- [ ] `last_update_id` tracked persistently
- [ ] Rate limit handling
- [ ] Deduplication by update_id
