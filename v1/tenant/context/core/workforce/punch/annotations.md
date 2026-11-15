---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.punch

One row per clock-in (log_type in) or clock-out (out). shift_id is the shift it was matched to; shift_start_at and shift_end_at are that shift's times frozen at punch time, so later moves of the shift do not change lateness. at is the punch instant, UTC; business_day the shop's roster day.

exception_type: none; time (an in after the start plus grace, an out before the end minus grace, or an in far too early); location (further than the shop's checkin_radius_m); missing (a placeholder the shop's own check-in does not write). One exception per row and time beats location: a late punch from outside the shop says time, and its geo_distance_m tells you it was also far.

Late: log_type in and at > shift_start_at + the template's late_entry_grace_min (workforce.shift_template through the shop and position). Share late = late ins over shifts with an in, per person, in the period.
Forgotten clock-out: a published shift with an in and no out before the shop's day turned after its end. The person's later fix is an out with producer web_correction: that shift still counts as forgotten. auto_closed true is a clock-out the system wrote.
offshift true: a punch matched to no shift (worked on a day off).
