---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.shift

One row per planned shift of one person (or of nobody) at one shop. status draft: managers only; published: the staff see it; cancelled: withdrawn after publishing. deleted_at set: a removed draft, never count it. person_id empty: an open shift nobody holds. start_local/end_local are the shop's wall clock in tz; start_at/end_at are their UTC copies. business_day is the roster day.

Who is rostered at an instant: published, not deleted, person set, start_at <= instant < end_at. Open shifts in a window: published, person_id null, not deleted. A shift with an open removal request still stands until the request is approved. Leave and days off have no row of their own: they are days with no shift (and, when the person said so, availability rows).
