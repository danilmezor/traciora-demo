# Seed v1: the master timeline (rule R6)

No date in the seed is "T minus n days, snapped". Every event is placed by one of the anchors below, and after placing them the seeder asserts the order and the gaps each card states. The anchors are ledger rows (`time.t_rule`, `time.anchors`, `roster.advisor_pattern`).

## Anchors

| Anchor | Meaning |
|---|---|
| T | an instant: date, local time, home zone. If the flagship is closed at the run instant (a closed date, before opening, after closing), T is the close of the flagship's last open day |
| W0, W-k, W+k | the ISO week (Monday to Sunday) that holds T; k weeks before; k weeks after |
| G | go-live: T-175 calendar days; if that is not a full open day, the next one. Always inside the junior's 180-day window |
| P | the last price rise: the first Monday on or after T-150 calendar days |
| full open day | a day every shop is open all day: a weekday that is not a closed date (en); any day that is not a closed date (ru). Saturday mornings are never anchors |
| the n-th full open day before or after D | counted from D, D not counted |
| slot N's n-th working day before or after T | days N is rostered. en advisors and every manager: full open days. ru advisors: two on, two off, phases fixed at T (slots 6, 29, 17, 24 work T, T+1, T+4, T+5 and so on; slots 5, 7, 16, 23 the days between) |
| the <weekday> of week T-k | that day of week W-k; if it is a closed date, the next full open day |
| slot N's first working day on or after D; last on or before D | ru advisors and mechanics: D when N is rostered on it, else the nearest day N is, forwards or backwards. en advisors and every manager: D |
| the compact steps of the seed files | written after a base, left to right (`workday/DESIGN.md` section 7): `>pN` slot N's next working day after; `>=pN` his first working day on or after; `<=pN` his last working day on or before; `>!pN` his next day off after; `>open`, `>=open`, `>=mon`, `>+nd`, `>-nd`. So slot 20's no-show is `east-2<=p20`: `east`'s 2nd full open day before T, then slot 20's last working day on or before it (`checks/check_workday.py` asserts that its card, stand-up note and feedback fall on the day `checks/timeline_examples.py` places) |
| the first day of a working pair of slot N on or after D | ru advisors: the first day on or after D on which N works and did not work the day before |
| T-n d | calendar days, for system facts only (G, P, the history, the windows of ranks) |

**Russian advisors work two on, two off, so a weekday of a week is not an anchor for them.** Every Russian story event that names an advisor is anchored to that person's working days: the n-th before or after T, or the first on or after (last on or before) the weekday the English card names. A missed call names the desk that was staffed. The worked examples print each such event for the nominal and the awkward T and assert that the person is rostered ("On shift").

When T is a Saturday in the English configuration, slot 6 has the Saturday turn at the flagship; `east` and `west` have no shifts, calls or briefs that day.

## The timeline

| Anchor | What | Story |
|---|---|---|
| T-24 months | the ERP history starts | |
| T-14 months | `west` is bought; its customers are loaded in bulk | S15 |
| the first full open day on or after T-335 d | the unapproved discounts at `west` begin; ru: the second price rise of the history | S2 |
| the Monday of week T-30 | an advisor at `main` (F3) resigns | |
| the Tuesdays of weeks T-26 and T-22 | two brake jobs on A5's vans come back at `west` | S1, S6 |
| G | Traciora goes live: roster, calls, conversations, board, memory, scheduled tasks start | |
| the first Monday on or after G | the Monday meeting's series starts | S9 |
| the 5th full open day after G | the missing money is found; the managing owner's first thread | S2 |
| the 15th full open day after G, and the next | the advisor at `west` (F1) is fired; the discount rule is written | S2, S12 |
| P | prices rise 8 %; A6's new contact starts | S1, S8, S12 |
| the Tuesday of week T-20 (ru: slot 5's first working day on or after it) | A6's first price call (call 21) | S1 |
| the Thursday of week T-20 | A5's last visit | S1 |
| the Tuesday of week T-19, then +1, +6, +9 days | A5's complaint call; its three unanswered calls | S1 |
| the Monday of week T-17 | the late mechanic at `main` (F2) is fired | S14 |
| the Mondays of weeks T-15 and T-14 | the apprentice and the newcomer advisor start at `main` | S8, S14 |
| the Monday of week T-10 to the Friday of week T-9 | the diagnostician is on leave | S5 |
| the Monday of week T-9 (T-10 if closed) | the Monday meeting is called off | S9 |
| the Monday of week T-7 | the supplier task is given to `west`'s manager | S6 |
| the Monday of week T-6 (ru: the person's first working day on or after it) | "I rang three times this morning" (call 31, slot 5); the junior's first team note is proposed | S3, S4 |
| the Monday and Tuesday of week T-5 | the meeting is moved to 10:00; the newcomer's first wrong price (call 12; ru: slot 7's first working day on or after the Tuesday) | S9, S12 |
| the Monday of week T-4 | the senior asks when the flagship misses calls | S3 |
| the Monday of week T-3 | the early desk shift begins; the supplier task falls due; the junior's second note is proposed (ru: her first working day on or after it) | S3, S6, S4 |
| the Wednesday of week T-3 and the Thursday of week T-1 (ru: slot 23's last working day on or before each) | the two discounts over 10 % nobody approved | S2 |
| slot 6's 14th (en) or 10th (ru) working day before T, the evening before it and her next working day | the private customer's web chat, booking and visit; under 30 days before T, inside the web chat's memory of a visitor | S7 |
| slot 7's 5th and 4th working days before T, then the next days of slots 5 and 4 | the newcomer's second wrong price (the timing belt, call 9), the late car, the argument, the discount | S8 |
| the full open day after the discount (ru: slot 5's first working day after it) | a correction to the stale page is proposed | S12 |
| the Monday of week T-1 | the weekly accounts report fails and is run again; the review card is given | S10, S16 |
| T-9 d, moved back to a full open day | the named car at `west` starts waiting for its part | S6 |
| `west`'s 4th full open day before T (ru: slot 23's 3rd working day before T) | call 15: a day promised with nothing behind it | S6 |
| `east`'s 2nd full open day before T (ru: slot 20's last working day on or before it) | a mechanic at `east` does not show up | S14 |
| `west`'s last full open day before T (ru: slot 23's last working day before T) | the waiting customer's missed call and call 16 | S6 |
| slot 6's last working day before T | the private customer comes back to the web chat; the junior's third note is proposed | S7, S4 |
| the first nightly pass after slot 5's last working day before T (the night before T's date when he worked the day before) | the nightly pass raises a proposal | S4 |
| T | today | |
| slot 6's 1st, 2nd and 3rd working days after T | her block for the review; the card is due; the review meeting | S16 |
| the Tuesday of week W+1 | an open shift nobody has taken | S14 |
| slot 16's last working day before her week off, in week W+1 (en the Wednesday; ru the Monday for the nominal T) | the regular's visit booked in the messenger chat of slot 16's last working day before T: en 13:00, ru 14:00 at `east`; the other time offered is with slot 17: the Friday of W+1 (en) or the Saturday of W+1 (ru) | S13 |
| the Thursday of week W+1 | the stocktake: every shop closes at noon | S13 |
| the Thursday of week W+1 to the Wednesday of week W+2 | the all-star advisor's week off, not covered | S5 |
| T+14 d | the roster ends; the week W+2 is a draft | |

Seasons and closed dates are not on this table: they stay where the calendar puts them (S11, S13).

## What the seeder asserts after placing the dates

- G is on or before the first Monday meeting; the money is found before F1 is fired; the rule is written before P; P is before A5's complaint call.
- A5: comebacks, then last visit, then complaint call, then three misses inside nine days; no answered call to or from its number afterwards.
- Slot 7 has been in post for at least 90 days at T, so every person row's window (the last 90 days) holds every current person.
- S8: quote, car in, ready one working day late, discount, all before T; the proposal after the discount. Call 12 (S12) is before call 9: it is slot 7's first wrong price, call 9 his second.
- Every story event that names a person falls on a day that person is rostered; in the Russian configuration this is asserted for each event of the "On shift" list.
- Slot 23's two unapproved discounts are inside the last 30 days, each before the Friday list of its own week.
- S7: chat, booking, visit, thanks, return chat, in that order; the first chat less than 30 days before T; the return chat open and owned by slot 6 at T.
- The fix is 21 to 27 days before T; the supplier task is 21 to 27 days overdue.
- S16: block, then due, then meeting; the meeting is not on the stocktake day.
- S5: exactly two published shifts of slot 16 inside her week off (ru: her two rota days from the Thursday to the Sunday of W+1); the stocktake day is in a week the home shops have published (`west` publishes W+1 on the Sunday evening of W0).
- A build fails if any assertion fails; the card is then changed, never the date by hand.

## Worked examples

Produced by `checks/timeline_examples.py`. The first run instant is the day this was written; the second is awkward on purpose: a Saturday that is the day after New Year's Day. In the English configuration the flagship is open that morning, so T is the run instant and the other two shops have no "today"; in the Russian configuration 2 January is a closed date, so T is the close of 31 December.

### en, run at Fri 2026-11-13 10:30

| Anchor | Date |
|---|---|
| T | Fri 2026-11-13 10:30 |
| W0 | 2026-11-09 to 2026-11-15 |
| ERP history starts (T-24 months, next full open day) | 2024-11-13 |
| west bought (T-14 months) | 2025-09-15 |
| S2 begins: first full open day on or after T-335 d | 2025-12-15 |
| F3 resigns: Mon W-30 | 2026-04-13 |
| A5 comebacks: Tue W-26, Tue W-22 | 2026-05-12, 2026-06-09 |
| G, go-live: T-175 d | 2026-05-22 |
| S9 series starts: first Monday on or after G | 2026-05-25 |
| S2 found, owner's thread: 5th full open day after G | 2026-06-01 |
| S2 follow-up thread: 5 more | 2026-06-08 |
| F1 fired: west's 15th full open day after G | 2026-06-15 |
| discount rule page and team note: next day | 2026-06-16 |
| P, price rise; A6's new contact: first Monday on or after T-150 d | 2026-06-22 |
| S1 call 21 (slot 5): Tue W-20; ru his first working day on or after | 2026-06-23 |
| A5 last visit: Thu W-20 | 2026-06-25 |
| A5 complaint call: Tue W-19 | 2026-06-30 |
| A5 three misses: +1, +6, +9 days | 2026-07-01, 2026-07-06, 2026-07-09 |
| F2 fired: Mon W-17 | 2026-07-13 |
| slot 14 starts: Mon W-15 | 2026-07-27 |
| slot 7 starts: Mon W-14 | 2026-08-03 |
| S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after | 2026-07-15, 2026-10-14 |
| diagnostician's leave: Mon W-10 to Fri W-9 | 2026-08-31 to 2026-09-11 |
| S1 call 22 (slot 7): Tue W-9; ru his first working day on or after | 2026-09-08 |
| S9 cancelled by the organiser | 2026-08-31 |
| S9 holiday Mondays (cancelled) | 2026-05-25, 2026-09-07 |
| supplier task created: Mon W-7; due: Mon W-3 | 2026-09-21; 2026-10-19 |
| S3 call 31 (slot 5): Mon W-6; ru his first working day on or after | 2026-09-28 |
| S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day | 2026-09-28; 2026-09-29 |
| S9 moved to 10:00: Mon W-5 | 2026-10-05 |
| slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after | 2026-10-06 |
| senior's thread and task: Mon W-4 | 2026-10-12 |
| S1 A6's web chat sent; first reply (slot 7) | 2026-10-13; 2026-10-15 |
| S3 fix: Mon W-3 | 2026-10-19 |
| S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day | 2026-10-19; 2026-10-20 |
| S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before | 2026-10-21, 2026-11-05 |
| S7 web chat 21:10: the evening before day A | 2026-10-25 |
| S7 day A (card taken, booked, confirming call) | 2026-10-26 |
| S7 visit: her next working day | 2026-10-27 |
| S8 quote call, slot 7's second wrong price: his 5th working day back | 2026-11-06 |
| S8 car in: his 4th | 2026-11-09 |
| S8 ready, bill, argument, complaint call | 2026-11-10 |
| S8 discount and call back | 2026-11-11 |
| S12 proposal: en next full open day; ru slot 5's first working day after | 2026-11-12 |
| S10 report fails; S16 card given: Mon W-1 | 2026-11-02 |
| S6 car enters waiting_parts: T-9 d, snapped back | 2026-11-04 |
| S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back | 2026-11-09 |
| S6 missed call and call 16: en west's last full open day; ru slot 23's last working day | 2026-11-12 |
| S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it | 2026-11-11 |
| S7 return chat (web); S4 waiting note: slot 6's last working day | 2026-11-12 |
| S4 nightly proposal: the pass after slot 5's last working day | 2026-11-13 |
| S16 block / due 12:00 / meeting 10:00 | 2026-11-16 / 2026-11-17 / 2026-11-18 |
| S14 open shift: Tue W+1 | 2026-11-17 |
| S13 stocktake, closed from 12:00 | 2026-11-19 |
| S5 week off | 2026-11-19 to 2026-11-25 |
| roster ends: T+14 d | 2026-11-27 |
| last closed date before T | 2026-09-07 |
| S9 counts | 25 occurrences: 2 holiday, 1 cancelled, 1 moved, 21 regular; held 22; slot 22 declined 8, accepted 14, came 6 |

Asserted: found<fired holds; fired<P holds; P<complaint holds; P<call 21 holds; call 12<call 9 holds; quote<car<ready<discount<T holds; slot 7 in post 90 days holds; block<due<meeting holds; S7 first chat under 30 days before T holds; stocktake in a published week holds; call 15<call 16<T holds; slot 23's discounts in the last 30 days, each before its week's Friday list holds; A6's chat waits two days holds; S12 proposal after the discount, before T holds; nightly proposal on or before T's date holds

On shift: 36 story events, each on a day its named person is rostered holds

### ru, run at Fri 2026-11-13 10:30

| Anchor | Date |
|---|---|
| T | Fri 2026-11-13 10:30 |
| W0 | 2026-11-09 to 2026-11-15 |
| ERP history starts (T-24 months, next full open day) | 2024-11-13 |
| west bought (T-14 months) | 2025-09-13 |
| S2 begins: first full open day on or after T-335 d | 2025-12-13 |
| F3 resigns: Mon W-30 | 2026-04-13 |
| A5 comebacks: Tue W-26, Tue W-22 | 2026-05-12, 2026-06-09 |
| G, go-live: T-175 d | 2026-05-22 |
| S9 series starts: first Monday on or after G | 2026-05-25 |
| S2 found, owner's thread: 5th full open day after G | 2026-05-27 |
| S2 follow-up thread: 5 more | 2026-06-01 |
| F1 fired: west's 15th full open day after G | 2026-06-06 |
| discount rule page and team note: next day | 2026-06-07 |
| P, price rise; A6's new contact: first Monday on or after T-150 d | 2026-06-22 |
| S1 call 21 (slot 5): Tue W-20; ru his first working day on or after | 2026-06-24 |
| A5 last visit: Thu W-20 | 2026-06-25 |
| A5 complaint call: Tue W-19 | 2026-06-30 |
| A5 three misses: +1, +6, +9 days | 2026-07-01, 2026-07-06, 2026-07-09 |
| F2 fired: Mon W-17 | 2026-07-13 |
| slot 14 starts: Mon W-15 | 2026-07-27 |
| slot 7 starts: Mon W-14 | 2026-08-03 |
| S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after | 2026-07-16, 2026-10-16 |
| diagnostician's leave: Mon W-10 to Fri W-9 | 2026-08-31 to 2026-09-11 |
| S1 call 22 (slot 7): Tue W-9; ru his first working day on or after | 2026-09-08 |
| S9 cancelled by the organiser | 2026-09-07 |
| S9 holiday Mondays (cancelled) | none |
| supplier task created: Mon W-7; due: Mon W-3 | 2026-09-21; 2026-10-19 |
| S3 call 31 (slot 5): Mon W-6; ru his first working day on or after | 2026-09-28 |
| S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day | 2026-09-30; 2026-10-01 |
| S9 moved to 10:00: Mon W-5 | 2026-10-05 |
| slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after | 2026-10-06 |
| senior's thread and task: Mon W-4 | 2026-10-12 |
| S1 A6's web chat sent; first reply (slot 7) | 2026-10-13; 2026-10-15 |
| S3 fix: Mon W-3 | 2026-10-19 |
| S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day | 2026-10-20; 2026-10-21 |
| S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before | 2026-10-19, 2026-11-04 |
| S7 web chat 21:10: the evening before day A | 2026-10-23 |
| S7 day A (card taken, booked, confirming call) | 2026-10-24 |
| S7 visit: her next working day | 2026-10-25 |
| S8 quote call, slot 7's second wrong price: his 5th working day back | 2026-11-04 |
| S8 car in: his 4th | 2026-11-07 |
| S8 ready, bill, argument, complaint call | 2026-11-08 |
| S8 discount and call back | 2026-11-09 |
| S12 proposal: en next full open day; ru slot 5's first working day after | 2026-11-11 |
| S10 report fails; S16 card given: Mon W-1 | 2026-11-02 |
| S6 car enters waiting_parts: T-9 d, snapped back | 2026-11-04 |
| S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back | 2026-11-08 |
| S6 missed call and call 16: en west's last full open day; ru slot 23's last working day | 2026-11-12 |
| S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it | 2026-11-11 |
| S7 return chat (web); S4 waiting note: slot 6's last working day | 2026-11-10 |
| S4 nightly proposal: the pass after slot 5's last working day | 2026-11-13 |
| S16 block / due 12:00 / meeting 10:00 | 2026-11-14 / 2026-11-17 / 2026-11-18 |
| S14 open shift: Tue W+1 | 2026-11-17 |
| S13 stocktake, closed from 12:00 | 2026-11-19 |
| S5 week off | 2026-11-19 to 2026-11-25 |
| roster ends: T+14 d | 2026-11-27 |
| last closed date before T | 2026-01-02 |
| S9 counts | 25 occurrences: 0 holiday, 1 cancelled, 1 moved, 23 regular; held 24; slot 22 declined 9, accepted 15, came 7 |

Asserted: found<fired holds; fired<P holds; P<complaint holds; P<call 21 holds; call 12<call 9 holds; quote<car<ready<discount<T holds; slot 7 in post 90 days holds; block<due<meeting holds; S7 first chat under 30 days before T holds; stocktake in a published week holds; call 15<call 16<T holds; slot 23's discounts in the last 30 days, each before its week's Friday list holds; A6's chat waits two days holds; S12 proposal after the discount, before T holds; nightly proposal on or before T's date holds

On shift: 41 story events, each on a day its named person is rostered holds

### en, run at Sat 2027-01-02 10:30

| Anchor | Date |
|---|---|
| T | Sat 2027-01-02 10:30 |
| W0 | 2026-12-28 to 2027-01-03 |
| ERP history starts (T-24 months, next full open day) | 2025-01-02 |
| west bought (T-14 months) | 2025-11-03 |
| S2 begins: first full open day on or after T-335 d | 2026-02-02 |
| F3 resigns: Mon W-30 | 2026-06-01 |
| A5 comebacks: Tue W-26, Tue W-22 | 2026-06-30, 2026-07-28 |
| G, go-live: T-175 d | 2026-07-13 |
| S9 series starts: first Monday on or after G | 2026-07-13 |
| S2 found, owner's thread: 5th full open day after G | 2026-07-20 |
| S2 follow-up thread: 5 more | 2026-07-27 |
| F1 fired: west's 15th full open day after G | 2026-08-03 |
| discount rule page and team note: next day | 2026-08-04 |
| P, price rise; A6's new contact: first Monday on or after T-150 d | 2026-08-10 |
| S1 call 21 (slot 5): Tue W-20; ru his first working day on or after | 2026-08-11 |
| A5 last visit: Thu W-20 | 2026-08-13 |
| A5 complaint call: Tue W-19 | 2026-08-18 |
| A5 three misses: +1, +6, +9 days | 2026-08-19, 2026-08-24, 2026-08-27 |
| F2 fired: Mon W-17 | 2026-08-31 |
| slot 14 starts: Mon W-15 | 2026-09-14 |
| slot 7 starts: Mon W-14 | 2026-09-21 |
| S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after | 2026-09-02, 2026-12-02 |
| diagnostician's leave: Mon W-10 to Fri W-9 | 2026-10-19 to 2026-10-30 |
| S1 call 22 (slot 7): Tue W-9; ru his first working day on or after | 2026-10-27 |
| S9 cancelled by the organiser | 2026-10-26 |
| S9 holiday Mondays (cancelled) | 2026-09-07 |
| supplier task created: Mon W-7; due: Mon W-3 | 2026-11-09; 2026-12-07 |
| S3 call 31 (slot 5): Mon W-6; ru his first working day on or after | 2026-11-16 |
| S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day | 2026-11-16; 2026-11-17 |
| S9 moved to 10:00: Mon W-5 | 2026-11-23 |
| slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after | 2026-11-24 |
| senior's thread and task: Mon W-4 | 2026-11-30 |
| S1 A6's web chat sent; first reply (slot 7) | 2026-12-01; 2026-12-03 |
| S3 fix: Mon W-3 | 2026-12-07 |
| S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day | 2026-12-07; 2026-12-08 |
| S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before | 2026-12-09, 2026-12-24 |
| S7 web chat 21:10: the evening before day A | 2026-12-10 |
| S7 day A (card taken, booked, confirming call) | 2026-12-11 |
| S7 visit: her next working day | 2026-12-14 |
| S8 quote call, slot 7's second wrong price: his 5th working day back | 2026-12-24 |
| S8 car in: his 4th | 2026-12-28 |
| S8 ready, bill, argument, complaint call | 2026-12-29 |
| S8 discount and call back | 2026-12-30 |
| S12 proposal: en next full open day; ru slot 5's first working day after | 2026-12-31 |
| S10 report fails; S16 card given: Mon W-1 | 2026-12-21 |
| S6 car enters waiting_parts: T-9 d, snapped back | 2026-12-24 |
| S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back | 2026-12-28 |
| S6 missed call and call 16: en west's last full open day; ru slot 23's last working day | 2026-12-31 |
| S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it | 2026-12-30 |
| S7 return chat (web); S4 waiting note: slot 6's last working day | 2026-12-31 |
| S4 nightly proposal: the pass after slot 5's last working day | 2027-01-01 |
| S16 block / due 12:00 / meeting 10:00 | 2027-01-04 / 2027-01-05 / 2027-01-06 |
| S14 open shift: Tue W+1 | 2027-01-05 |
| S13 stocktake, closed from 12:00 | 2027-01-07 |
| S5 week off | 2027-01-07 to 2027-01-13 |
| roster ends: T+14 d | 2027-01-16 |
| last closed date before T | 2027-01-01 |
| S9 counts | 25 occurrences: 1 holiday, 1 cancelled, 1 moved, 22 regular; held 23; slot 22 declined 8, accepted 15, came 7 |

Asserted: found<fired holds; fired<P holds; P<complaint holds; P<call 21 holds; call 12<call 9 holds; quote<car<ready<discount<T holds; slot 7 in post 90 days holds; block<due<meeting holds; S7 first chat under 30 days before T holds; stocktake in a published week holds; call 15<call 16<T holds; slot 23's discounts in the last 30 days, each before its week's Friday list holds; A6's chat waits two days holds; S12 proposal after the discount, before T holds; nightly proposal on or before T's date holds

On shift: 36 story events, each on a day its named person is rostered holds

### ru, run at Sat 2027-01-02 10:30

| Anchor | Date |
|---|---|
| T | Thu 2026-12-31 20:00 |
| W0 | 2026-12-28 to 2027-01-03 |
| ERP history starts (T-24 months, next full open day) | 2024-12-28 |
| west bought (T-14 months) | 2025-10-28 |
| S2 begins: first full open day on or after T-335 d | 2026-01-30 |
| F3 resigns: Mon W-30 | 2026-06-01 |
| A5 comebacks: Tue W-26, Tue W-22 | 2026-06-30, 2026-07-28 |
| G, go-live: T-175 d | 2026-07-09 |
| S9 series starts: first Monday on or after G | 2026-07-13 |
| S2 found, owner's thread: 5th full open day after G | 2026-07-14 |
| S2 follow-up thread: 5 more | 2026-07-19 |
| F1 fired: west's 15th full open day after G | 2026-07-24 |
| discount rule page and team note: next day | 2026-07-25 |
| P, price rise; A6's new contact: first Monday on or after T-150 d | 2026-08-03 |
| S1 call 21 (slot 5): Tue W-20; ru his first working day on or after | 2026-08-11 |
| A5 last visit: Thu W-20 | 2026-08-13 |
| A5 complaint call: Tue W-19 | 2026-08-18 |
| A5 three misses: +1, +6, +9 days | 2026-08-19, 2026-08-24, 2026-08-27 |
| F2 fired: Mon W-17 | 2026-08-31 |
| slot 14 starts: Mon W-15 | 2026-09-14 |
| slot 7 starts: Mon W-14 | 2026-09-21 |
| S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after | 2026-09-02, 2026-12-03 |
| diagnostician's leave: Mon W-10 to Fri W-9 | 2026-10-19 to 2026-10-30 |
| S1 call 22 (slot 7): Tue W-9; ru his first working day on or after | 2026-10-27 |
| S9 cancelled by the organiser | 2026-10-26 |
| S9 holiday Mondays (cancelled) | none |
| supplier task created: Mon W-7; due: Mon W-3 | 2026-11-09; 2026-12-07 |
| S3 call 31 (slot 5): Mon W-6; ru his first working day on or after | 2026-11-16 |
| S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day | 2026-11-17; 2026-11-18 |
| S9 moved to 10:00: Mon W-5 | 2026-11-23 |
| slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after | 2026-11-24 |
| senior's thread and task: Mon W-4 | 2026-11-30 |
| S1 A6's web chat sent; first reply (slot 7) | 2026-12-04; 2026-12-06 |
| S3 fix: Mon W-3 | 2026-12-07 |
| S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day | 2026-12-07; 2026-12-08 |
| S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before | 2026-12-09, 2026-12-22 |
| S7 web chat 21:10: the evening before day A | 2026-12-10 |
| S7 day A (card taken, booked, confirming call) | 2026-12-11 |
| S7 visit: her next working day | 2026-12-12 |
| S8 quote call, slot 7's second wrong price: his 5th working day back | 2026-12-22 |
| S8 car in: his 4th | 2026-12-25 |
| S8 ready, bill, argument, complaint call | 2026-12-26 |
| S8 discount and call back | 2026-12-28 |
| S12 proposal: en next full open day; ru slot 5's first working day after | 2026-12-29 |
| S10 report fails; S16 card given: Mon W-1 | 2026-12-21 |
| S6 car enters waiting_parts: T-9 d, snapped back | 2026-12-22 |
| S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back | 2026-12-26 |
| S6 missed call and call 16: en west's last full open day; ru slot 23's last working day | 2026-12-30 |
| S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it | 2026-12-29 |
| S7 return chat (web); S4 waiting note: slot 6's last working day | 2026-12-28 |
| S4 nightly proposal: the pass after slot 5's last working day | 2026-12-31 |
| S16 block / due 12:00 / meeting 10:00 | 2027-01-04 / 2027-01-05 / 2027-01-08 |
| S14 open shift: Tue W+1 | 2027-01-05 |
| S13 stocktake, closed from 12:00 | 2027-01-07 |
| S5 week off | 2027-01-07 to 2027-01-13 |
| roster ends: T+14 d | 2027-01-14 |
| last closed date before T | 2026-01-02 |
| S9 counts | 25 occurrences: 0 holiday, 1 cancelled, 1 moved, 23 regular; held 24; slot 22 declined 9, accepted 15, came 7 |

Asserted: found<fired holds; fired<P holds; P<complaint holds; P<call 21 holds; call 12<call 9 holds; quote<car<ready<discount<T holds; slot 7 in post 90 days holds; block<due<meeting holds; S7 first chat under 30 days before T holds; stocktake in a published week holds; call 15<call 16<T holds; slot 23's discounts in the last 30 days, each before its week's Friday list holds; A6's chat waits two days holds; S12 proposal after the discount, before T holds; nightly proposal on or before T's date holds

On shift: 41 story events, each on a day its named person is rostered holds
