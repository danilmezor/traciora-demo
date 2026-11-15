---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# traciora.reply_episodes

One row per customer ask: asked_at is the first customer message after the last public reply, answered_at the first public reply after it (empty: still unanswered), answered_by the Chatwoot user id when a person answered, answered_by_kind manager or assistant. Wait = answered_at minus asked_at. A person's reply speed: episodes they answered, median wait; episodes the assistant answered are not theirs. Unanswered now: answered_at empty.
