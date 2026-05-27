---
workbench: true
updated: {date}
project: {project_name}
---

# Workbench — {project_name}

> This is your desk. Messy is fine. When something solidifies, move it to the right filing cabinet: decisions → decision-log, tasks → tasks.md, questions → the thread.

---

## 🔨 Current work

<!-- What are you actively thinking about or working on right now? -->

---

## 💭 Working notes

<!-- Brain dumps, half-thoughts, sketches — whatever helps -->
<!-- ⚠️ NOT ready for processing. Agent must ASK before capturing these into PLAN/FOCUS. -->

---

## 📋 To sort

<!-- Stuff that needs a home but you're not sure where yet -->

---

## ✅ Recently done

<!-- Strike-through when complete: ~~like this~~ -->

---

## Processing Convention

When an agent joins this project and reads the WORKBENCH:

1. **Read** all sections above (Current work, Working notes, To sort, Recently done)
2. **Process Current work items:**
   - Solid items → capture into `PLAN.md` as tasks, update `FOCUS.md` active work
   - Decisions already made → capture into decision log or `FOCUS.md` decisions table
3. **Process 💭 Working notes with CARE:**
   - ⚠️ **Working notes are not well-formed.** Before processing, ASK the user:
     - "I see these working notes: [list]. Should I capture any of these into PLAN/FOCUS, or are they still half-formed?"
   - Only process what the user confirms
4. **Process 📋 To sort items:**
   - Determine if each item belongs in PLAN, FOCUS, a domain, or should stay in To sort
   - Move items that have a clear home to their destination
   - Leave ambiguous items in To sort
5. **Move processed items to ✅ Recently done**
   - Add a date stamp: `📅 YYYY-MM-DD`
   - Brief description of what was done and where it landed
6. **Update this WORKBENCH** after processing — remove captured items from their original sections

**Key rule:** Working notes (💭) require user confirmation before processing. Current work items (🔨) can be captured directly.

---

> 📋 **Checkbox states:** `[ ]` To Do | `[/]` In Progress | `[~]` Good Enough | `[x]` Done | `[>]` Deferred | `[!]` Blocked | `[-]` Cancelled — [[01-Projects/doc-standards/wiki/doc-standards/reference/Checkbox-State-Legend|full legend]]
