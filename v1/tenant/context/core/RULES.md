<!-- extends config/sources/traciora/RULES.md; appended under "## Demo tenant, notes v1" -->

## What lives where

- Here: staff and their postings, the shops and their dated hours, calls and missed calls, the roster and punches, shift requests, the board and its trail, the calendar, pushed Inbox lines and the product's events.
- Not here: customers, cars, orders, money, parts (the `erp` source); chats (the `chatwoot` source); personal and team notes and their proposals (the memory tools); scheduled tasks and their runs (the scheduled-task tools); knowledge pages (the knowledge tools).
- No core row carries a key into another source. A customer is matched across sources by phone: read the number in the `erp` source or in a chat, then `phone('<number>')` against a call leg's tokens.

## Shops and clocks

- Every instant here is UTC. Turn it into a shop's local time with that shop's `core.location.tz` before you group by hour, day or weekday. The shops do not share one zone: a call at 08:30 home time is 07:30 at a shop an hour behind.
- "Today", "yesterday", "last week", "the last 30 days" are counted in business days of the shop concerned; for a question about the whole company use the tenant's home zone and say so.
- Opening hours are `core.location.business_hours` by weekday, overridden for one date by `core.location_hours_exception`. A shop that is closed on a weekday in its hours is closed every week; a closed date is a row.
- In-hours means inside that shop's hours on that date, exceptions applied. A call or a punch outside them is out of hours.

## People

- A person is `identity.person`; a login is not a person and a role is not a rank. `display_name_enc` comes back as plain text in results but cannot be filtered in SQL: read the people of the shop or the period, then pick by name in the result.
- Someone who left has `active` false and an `ended_on`; their calls, shifts and punches stay. "On staff now" is active with no `ended_on`.
- Where someone may work is `identity.person_location` (one row per shop; `is_home` marks the home shop). A person can be posted at two shops.

## Desks and phones

- A desk is a PBX extension. `core.location_alias` with namespace `pbx_extension` says which shop an extension or a group line belongs to; `config_key` gives each shop's short key.
- A group line rings the desks of its shop; each ring of one desk is one leg. The desk a call rang first is the extension of its earliest leg.
- A missed call has no person: nobody answered it. Never name a person as having missed a call. Attribute misses to the desk that rang first, and if the question is about people, say which desks they were and who was rostered there, and that the data cannot say who failed to pick up.
- A call is attributed to the person on duty at the desk that answered (`phone_call.person_id`, `attributed_by`); that is a presumption from the roster or the extension, not a voice match.

## Attendance (from middle rank up)

- A late arrival is an `in` punch after its shift's start plus the template's `late_entry_grace_min`. Count lateness as late `in` punches over the person's punched shifts in the period, not over all punches.
- A forgotten clock-out is a shift with an `in` punch and no `out` punch by the time the shop's day turned. Afterwards the person fixes it with an `out` punch whose `producer` is `web_correction`; count the shift as a forgotten clock-out whether or not it was corrected.
- A no-show is a `shift.no_show` event in `platform.event`, written for a published shift nobody clocked into. The shift itself carries no absent status.
- A punch from outside the shop is `exception_type = 'location'`, or, when it was also late, a `'time'` punch whose `geo_distance_m` exceeds the shop's `checkin_radius_m`: lateness wins the one exception slot.
- "Who is on now" is a question about the present: the roster says who is due; the latest punch says who came. Say the instant of the latest punch and call on record; if it is not today, say the data stops there.

## The board and the calendar

- A card is `work.work_item`; its history is `platform.activity` (subject_type `work_item`). The card's state is authoritative; the trail says when and by whom it moved.
- A card is closed when it moved into a state of group `completed` or `cancelled`; its closing time is the `occurred_at` of that activity line. Overdue: open past `due_at`, or closed after it. Quiet: open, no activity line for the tenant's quiet days (7), and not due further ahead than that.
- A meeting is `work.calendar_event` of kind `meeting`; a weekly meeting is a series whose occurrences are rows. A cancelled occurrence keeps its row with `cancelled_at`. Attendance is on `calendar_event_participant`; the organiser is not a participant row.

## Counting carefully

- State the population, the period and the date column you used. A `LIMIT` reached is not a total.
- A rate is N of M with both numbers given. Under eight cases say "too few to rate" and give the counts.
- When the honest answer is that the data does not record something (a reason someone was let go, who failed to answer a missed call), say that, and give what the data does show.
