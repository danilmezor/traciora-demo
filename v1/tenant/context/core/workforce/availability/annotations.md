---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.availability

One row per statement a person made about when they can work: kind unavailable, undesired or desired. Either a single on_date or a weekly day_mask with valid_from/valid_to; times empty mean the whole day. A week of leave is usually one unavailable row per date. Availability is a wish or a block, not a shift: check workforce.shift for what was planned.
