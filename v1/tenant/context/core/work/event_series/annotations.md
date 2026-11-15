---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# work.event_series

One row per standing series: an RFC 5545 rule from starts_on to ends_on. Its occurrences are work.calendar_event rows with this series_id; count meetings from those rows, not from the rule.
