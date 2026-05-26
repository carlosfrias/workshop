# AGENTS.md — Bible Club

**Purpose:** Meeting scheduling, attendance tracking, and member communication for DCPS bible club.  
**Domain owner:** Nancy

---

## [S-TIGHT]

Bible club coordination: schedule meetings (date/time/location), track attendance (present/absent/member lookup), send member communications (email/sms templates). All ministry workflows in one self-contained domain.

---

## Conventions

- **Meeting times:** Local (America/New_York). Store as ISO 8601 with timezone offset.
- **Attendance status:** `present`, `absent`, `excused`, `late`.
- **Member roles:** `leader`, `student`, `parent`, `volunteer`.
- **Communication templates:** Greeting → Purpose → Details → Call-to-action → Closing.
- **Privacy:** Never expose member contact info outside authorized communications.

---

## Rules

### Must Always

1. **Confirm meeting details** — Date, time, location, topic before sending invites.
2. **Log attendance within 24h** of each meeting.
3. **Track excused absences** — Record reason if provided.
4. **Use templates for member communications** — Consistency + pastoral tone.
5. **Respect quiet hours** — No communications 9pm–7am local time unless urgent.

### Must Never

1. **Never share member contact lists** outside authorized ministry use.
2. **Never auto-add members** to communications without consent.
3. **Never use abbreviations for prayer requests** — Full context required.
4. **Never schedule during school holidays** without explicit approval.

---

## Quality Checklist

Before declaring a task complete:

- [ ] Meeting invites include: date, time, location, topic, what-to-bring
- [ ] Attendance records include: meeting ID, member ID, status, timestamp
- [ ] Communications include: clear subject, greeting, purpose, details, RSVP deadline
- [ ] Member data validated: name, role, contact method, consent status
- [ ] Privacy respected: no PII in logs, contact lists encrypted at rest

---

## Common Mistakes

| Symptom | Root Cause | Correct Approach |
|---------|-----------|-----------------|
| Meeting conflict with school event | Didn't check school calendar | Cross-reference DCPS academic calendar before scheduling |
| Member receives duplicate emails | List not deduplicated | Use member ID as unique key, dedupe before send |
| Attendance count doesn't match sign-in sheet | Manual entry error | Double-entry verification or photo backup |
| SMS sent during quiet hours | Timezone mismatch | Store member timezone preference, convert before send |

---

## Documentation Protocol

All work in this domain must be documented in the wiki:

1. **After each meeting:** Add entry to `Activity Log.md` with date, attendance count, key decisions
2. **After member communications:** Log template used, recipient count, response rate
3. **After schedule changes:** Record original + new details, reason for change, notification sent

**Activity Log format:**
```markdown
### YYYY-MM-DD — {Activity Type}

**Summary:** 1-2 sentences

**Details:**
- Item 1
- Item 2

**Next steps:** What happens next, who owns it
```

---

## Routing References

This domain is self-contained. For project-level routing, see root [AGENTS.md](../AGENTS.md).
