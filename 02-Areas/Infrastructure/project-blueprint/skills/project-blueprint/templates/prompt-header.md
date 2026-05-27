# {prompt_title}

| About | Details |
|-------|---------|
| **Prompt ID** | {prompt_id} |
| **Purpose** | {purpose} |
| **Audience** | {audience} |
| **Status** | {status} |
| **File** | `{file_path}` |

---

## Usage

### Standalone Mode
Copy this entire prompt and paste into pi:

```
{standalone_prompt}
```

### Embedded Mode
This prompt is also embedded in the wiki at:
- [`{wiki_path}`]({wiki_link})

---

## Header Style

Phase and Option headings follow the natural-header pattern:

- **Short, scannable headings** — no parenthetical details, ratings, or descriptions in the header line
- **Details in a bold paragraph below** — move recommendations, speed claims, and prerequisites out of the heading

**Example:**

```markdown
### Option A: Cloud Setup

**Fastest path** — works in 2 minutes, no local installation needed. **Recommended for first-time users.**
```

---

## Acceptance Criteria

{acceptance_criteria}

---

## References

| File | Purpose | Location |
|------|---------|----------|
| **Master Prompt** | Canonical version | `{master_path}` |
| **Wiki Page** | Embedded reference | `{wiki_path}` |
| **Backlog Entry** | Tracking | `{backlog_path}` |

---

**Version:** {version}
**Created:** {created_date}
**Updated:** {updated_date}
**Author:** {author}
