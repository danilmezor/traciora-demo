---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.shift_schedule

One row per rotation of one person (or of an open slot) on one template, as an RFC 5545 rule from valid_from to valid_to. Shifts made from it carry its id and an occurrence_key. A rotation is the plan's source, not the plan: read workforce.shift for what is planned on a day.
