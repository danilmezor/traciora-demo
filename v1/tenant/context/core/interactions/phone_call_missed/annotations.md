<!-- extends config/sources/traciora/interactions/phone_call_missed/annotations.md; appended under "## Demo tenant, notes v1" -->

In-hours misses are those with out_of_hours false: use them for every miss rate, and report out-of-hours misses apart. A desk's miss rate is its misses over the in-hours inbound calls whose first leg rang that desk.

Time to a call back: resolved_at minus the missed call's phone_call.started_at, for resolved rows; give the median, not the mean, and say whether you counted clock time or the shop's open time.

Never returned: state waiting and no later answered call to or from the same number (check phone_call_leg tokens after the miss). A waiting row older than 7 days is outside the product's follow-up and is not on the To call back list, but it is still unreturned.

The call-back list now: waiting, dismissed_at empty, missed in the last 7 days, with a caller number on its first leg, at the shops the asker reads. A dismissed miss was taken off the list by a person; it was not returned.
