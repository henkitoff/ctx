---
# Knowledge Distillate — <% tp.date.now("YYYY-MM-DD") %>
#
# Agents read knowledge/LATEST.yaml at every session start.
# This Obsidian template creates the YAML structure ready to fill in.
#
# Tip: use the script instead for automatic archiving of the previous LATEST:
#   python scripts/new_knowledge.py "<% tp.file.title %>"
#
# After filling in: save this file as knowledge/LATEST.yaml
# (overwrite the placeholder — the script archives the old one automatically)

date: "<% tp.date.now("YYYY-MM-DD") %>"
topic: "<% tp.file.title %>"

milestone: "One sentence: what is now true that was not true before this session"

blockers_resolved:
  - ""

cross_session_patterns:
  - ""
  # Non-obvious learnings future agents MUST know.
  # e.g. "Module X must start before Y, even though Y doesn't import X"
  # These are the highest-value entries — spend time here.

next_session_hints:
  - "Priority 1: most important next action, and why"
  - "Priority 2: second priority"

open_items:
  - item: "Short description of deferred work"
    why_deferred: "Explicit reason — not just 'not done yet'"
    trigger: "What would make this urgent"

units_completed:
  - ""

metrics: {}

tags: [ctx/knowledge]

---

> **How to use this note:**
> 1. Fill in every field above — especially `cross_session_patterns`
> 2. Save this note's content (without the `---` explanation block below) as `knowledge/LATEST.yaml`
> 3. Or run `python scripts/new_knowledge.py "topic"` — it does steps 1–2 with auto-archiving
>
> **What NOT to put here:**
> - What files changed → use `git log`
> - How a function works → read the code
> - Anything derivable from current codebase state
