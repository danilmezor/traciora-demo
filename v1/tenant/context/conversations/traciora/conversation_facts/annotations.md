---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# traciora.conversation_facts

One row per conversation: inbox_id, assignee_id (the owner now), created_at, status as a word (open, resolved, pending, snoozed), first_answer_at (the first public reply by a person or the assistant). It counts conversations, not sessions: a messenger customer's later sessions are inside one row. created_at is UTC.
