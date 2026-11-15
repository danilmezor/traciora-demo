---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# traciora.resolutions

One row per time a conversation was resolved: resolved_at, user_id (the person who resolved it; empty when the system resolved it after the tenant's silent days, 7), opened_at (the conversation's creation). A conversation can be resolved many times (a messenger chat reopens). Sessions of a conversation are the spans between its resolutions.
