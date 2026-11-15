---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# platform.activity

One row per line of an object's timeline. For a card: subject_type work_item, subject_id the card. verb created, assigned, moved (field state_id, old_identifier and new_identifier the states), completed, cancelled, reopened, commented, part_done, participant_added, attached, kept, refused. occurred_at is when it happened. A comment's words are not readable here; payload_public.mentions holds the ids of people a comment named. actor_kind says whether a person, the assistant on a person's behalf, or the system wrote it.

Cycle time of a card: created to the occurred_at of the line that moved it into a completed state. Last touch: the newest line of any verb, comments included.
