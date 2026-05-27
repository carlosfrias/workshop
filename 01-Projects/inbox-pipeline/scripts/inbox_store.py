"""
Inbox Store — SQLite schema and helpers for unified message storage.

Schema:
    inbox(id, source, source_id, from_addr, subject, body, received_at, agent_read, priority)

Usage:
    from inbox_store import InboxStore
    store = InboxStore("data/inbox.db")
    store.insert_email(uid, sender, subject, body)
    store.insert_telegram(update_id, username, text, timestamp)
"""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.environ.get("INBOX_DB_PATH", "data/inbox.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    from_addr TEXT,
    subject TEXT,
    body TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    agent_read INTEGER DEFAULT 0,
    priority INTEGER DEFAULT 0,
    UNIQUE(source, source_id)
);
"""

class InboxStore:
    def __init__(self, db_path=DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def insert_message(self, source, source_id, from_addr=None, subject=None, body=None, received_at=None):
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO inbox (source, source_id, from_addr, subject, body, received_at) VALUES (?,?,?,?,?,?)",
                (source, str(source_id), from_addr, subject, body, received_at or datetime.now(timezone.utc).isoformat())
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Store error: {e}")
            return False

    def get_unread(self, limit=50):
        return self.conn.execute(
            "SELECT id, source, from_addr, subject, body, received_at FROM inbox WHERE agent_read=0 ORDER BY priority DESC, received_at ASC LIMIT ?",
            (limit,)
        ).fetchall()

    def mark_read(self, msg_id):
        self.conn.execute("UPDATE inbox SET agent_read=1 WHERE id=?", (msg_id,))
        self.conn.commit()
