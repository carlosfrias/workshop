# AGENTS.md — Email Ingestion

**Purpose:** Fetch emails via IMAP from configured accounts, normalize into inbox store.

---

## Summary

Connect to any IMAP server, fetch unread messages, parse headers + body, store in SQLite inbox. One fetcher per email account. Run via cron.

---

## Conventions

- **IMAP:** SSL on port 993. `imaplib.IMAP4_SSL`.
- **Environment variables:** `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_HOST`.
- **Folder:** `INBOX` by default. Configurable per account.
- **Body extraction:** Prefer `text/plain`, fallback to `text/html` stripped.

---

## Rules

### Must Always
1. Use environment variables for credentials — never hardcode
2. Deduplicate by IMAP UID (`source_id`) before inserting
3. Log fetch count + errors
4. Mark as read only after successful store

### Must Never
1. Never delete messages from the server
2. Never store raw credentials in the database
3. Never fetch without SSL

---

## Quality Checklist

- [ ] Credentials from env vars only
- [ ] IMAP SSL on port 993
- [ ] Deduplication by UID
- [ ] Body extraction handles both plain and HTML
- [ ] Errors logged, not swallowed
