---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# work.event_series_exception

One row per changed occurrence of a series: action cancel (dropped) or replace (held at the replacement times). occurrence_key matches the occurrence row. The occurrence row itself already carries cancelled_at or the new times; use this table for the why and the when of the change.
