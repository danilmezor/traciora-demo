---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# work.calendar_event

One row per diary entry. kind meeting (has participants), block (time set aside for a card, work_item_id), personal (one person's own entry). organiser_id owns it. start_local/end_local are wall clock in tz; start_at/end_at UTC. A meeting set in one shop's zone falls at another local hour in a shop an hour behind: convert with that shop's tz before you say "his time".

A weekly meeting is a series (series_id) with one row per occurrence (occurrence_key). cancelled_at set: called off, the row stays; held: not cancelled and not deleted, and start_at in the past. A moved occurrence keeps its occurrence_key and carries the new times.
