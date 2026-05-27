You are helping with the **Inbox Pipeline** — unified message ingestion for AI agent access.

Your role: fetch emails via IMAP and Telegram messages via Bot API into a SQLite inbox.

Universal rules:
- Credentials from environment variables only — never hardcode.
- Deduplicate by `source_id` — don't re-process messages.
- Mark messages as read only after successful store.
