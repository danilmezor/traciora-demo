---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# core.location_hours_exception

One row per shop and date on which the shop does not keep its weekly hours. on_date is the shop's own calendar date. kind closed: no hours that day (open_local and close_local empty). kind hours: open only from open_local to close_local that day. A company-wide closure is one row per shop. reason is the tenant's word for it.

"Are we open on <date>": the exception row if there is one, else that weekday of core.location.business_hours. "Which days are we closed in the next N days": closed rows in the window, plus rows of kind hours that end the day early (say they are part-day), plus weekdays the weekly hours mark closed if the question means every closed day. Calls on a closed date are out of hours (phone_call_missed.out_of_hours true) and count in no desk's rate.
