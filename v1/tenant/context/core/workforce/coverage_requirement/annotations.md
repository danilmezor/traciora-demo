---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.coverage_requirement

One row per band a shop needs covered: position, weekdays (day_mask, Monday first), local start and end, min_count people. valid_from/valid_to date when the requirement held; a change of cover on a date is a new row from that date. Cover on a day: published shifts of that position overlapping the band, against min_count. required false: an aim, not a gap.
