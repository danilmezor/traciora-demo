---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.roster_publish

One row per publish of a shop's roster: range_start to range_end, who published it and published_at (UTC). How late a week was published: published_at against the start of range_start in the shop's zone. A week with no row is still a draft.
