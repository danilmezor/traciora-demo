# The working day in the core database: design (seed v1)

Shift planner and punches, task board, calendar, Inbox, console data. Files: `roster.json` (templates, cover, rota, publishes, state at T), `en/` and `ru/` (`cards.json`, `calendar.json`, `shift_requests.json`, `feedback.json`, `alerts.json`, `inbox.json`, `banks.json`), built by `_build/build.py`; `../checks/check_workday.py en|ru` passes for both (2,415 and 2,411 checks; nominal T and the awkward T of `stories/TIMELINE.md`).

Paths without a root are in the product repository. `B` = `apps/backend/src/traciora/core`, `SQL` = `apps/backend/schema/traciora-core.sql`. Rule R1 holds throughout: history is rows a loader writes with its own `id` (version 7, from the row's instant), `created_at`, `updated_at`; every `created_at` defaults to `now()` and `core.touch_mutable_row` (`SQL:4031`) forces `updated_at` on an update, so nothing historical goes through a command. The append-only tables (`punch`, `roster_publish`, `event`, `activity`, `pii_access_log`, `SQL:4201-4217`) are inserted once and never touched.

## 1. Shift planner and punches

| Thing | What the loader writes | Reference |
|---|---|---|
| Templates | `workforce.shift_template` per shop, `roster.json` `templates`: en desk early 07:30-16:00 and late 09:00-17:30, bay 07:30-16:00, Saturday 08:00-13:00 at `main`; ru desk 09:00-20:00, bay 09:00-18:00. Every template: check-in from 15 min before, late after 5 min (`late.grace_min`). ru `main` keeps the retired "Приёмка с 11:30" (`active = false` from the fix) | `SQL:1715`; `B/commands/roster.py:68` |
| Cover rules | `workforce.coverage_requirement` from `kb.schedule.minimums`. The fix of S03 is two rows with dates: desk at `main` `min_count` 1 with `valid_to` the day before the Monday of week T-3; 2 for the morning block and 1 for the rest with `valid_from` that Monday | `SQL:2051`; card S03 |
| Rotations | `workforce.shift_schedule`, one row per person and rule: en weekly `BYDAY`; ru advisors two rows each, `FREQ=DAILY;INTERVAL=4` from the first and the second day of the pair; ru mechanics weekly `BYDAY` from their days off. en Saturdays at `main`: slot 29 every week, advisors 5, 6, 7 in turn (`INTERVAL=3`), two technician crews on alternate weeks | `SQL:1779`; `docs/features/roster.md:197-203` |
| Shifts | `workforce.shift` for every rostered day from G to T+14 d with `shift_schedule_id` and `occurrence_key`, `status`, `roster_publish_id`. About 3,800 (en) and 3,300 (ru). Sickness and agreed absence: `status = 'cancelled'` with the publish kept, or an approved `remove` request; dealt per person from `pNN.absent`. Leave: no shifts on those dates | `SQL:1875`; exclusion `shift_person_no_overlap` `:1963` |
| Publishes | `workforce.roster_publish`, one per site and week, with `diff_public` counts and `diff_enc` (the next publish reads its predecessor's snapshot). Home shops (`main`, `east`) by slot 4 on the Thursday before, 11:20 to 11:55; `west` by slot 22 on the Sunday evening before, about 20:40 his time. Extra rows: the republish of week T-3 at `main` on the fix day; a one-shift publish for slot 21 on the no-show day. `platform.event` `shift.published` and `platform.activity` `published` per shift, dated by the publish | `SQL:1833`; `roster.py:75-146`; `B/queries/work_board.py:3099-3141` (a tray line per published shift) |
| Punches | `workforce.punch`, an `in` and an `out` per worked shift, `producer = 'app'`, frozen `shift_start_at`/`shift_end_at`. On time: in from 12 min before to 4 after. **Late** (dealt: round(shifts x `pNN.late`)): in 6 to 25 min after the start, `exception_type = 'time'`. **Far**: slot 26's two, on time, `geo_distance_m = 600`, `exception_type = 'location'` (time beats location, so a late far punch would read `time`). **Forgotten clock-out** (dealt from `pNN.forgot_clock_out`): no `out` row that day; the correction is an `out` row with `producer = 'web_correction'`, `at` the stated hour, written at the person's next clock-in, plus a `punch.corrected` line to the site's seniors and admins. `exception_type = 'missing'` is never written (section 10) | `SQL:2197`; `roster.py:249-370`; `B/tools/workspace/home_sql.py:429-490` |
| No-shows | `platform.event` `shift.no_show`, producer `attendance`, `occurred_at` the start plus grace plus up to 15 min, `person_id` the absentee; the shift stays his, with no punch. The eight of `s14.no_shows_sum`. Slot 20's: slot 21 gets a shift of his own at `east` from 55 min after opening (in en his `main` shift of that day is called off) | `roster.py:375-425`; `B/packs.py:239` |
| Availability | `workforce.availability`: `unavailable` per date for the leave of slot 10 and the week off of slot 16 (and her six en days off); weekly `undesired` for slot 21 (Fridays), slot 13 (en Wednesday after 15:00, ru Friday 12:00-13:30), slot 28 (class days) | `SQL:1992` |
| Requests | `workforce.shift_change_request` x 64 from `<lang>/shift_requests.json`, `reason_enc`, `filed_at`, the decision with `decision_note_enc`; per request the activity rows `change_requested` (payload `request_id`, `kind`, the shift as asked), `change_decided` / `change_withdrawn` / `change_expired`. An approval applies as a draft and reaches the person with the next publish. Approved removals count in `pNN.absent` | `SQL:2115`; `roster.py:905-1184` |

**The 64.** By status 35 approved, 16 declined, 9 expired, 2 withdrawn, 2 open in both languages. Kinds: en 28 `change_time`, 30 `remove`, 6 `change_date` (a full-time weekday worker has no free day to move to: only the part-timer and Saturday turns); ru 27, 26, 11 (a rota day moved to a day off). Home requests are decided by slot 4 within a working day; of `west`'s thirteen, six expire unanswered and one is approved by slot 2 on a visit.

**At T.** Everyone whose shift holds T has an `in` punch and no `out`, except slot 28: his shift at `west` on T's date starts at the last quarter-hour at least 15 minutes before T and he has not clocked in (Home state `late`, `home_sql.py:64-78`). If `west` is closed at T or T is within two hours of its close, nobody is late. Home shops: W0 and W+1 published, W+2 draft to T+14 d. `west`: W0 published, W+1 a draft (it is published on Sunday). One open shift (technician, `main`, the Tuesday of W+1, published, `person_id` null). Slot 16: two published shifts inside her week off with requests R50, R51 open; her desk empty in the draft. The stocktake day's shifts end at 12:00.

## 2. Task board

| Kind | `kind`, `origin`, `origin_ref` | State it starts in | Since G (`board.cards_since_g`) |
|---|---|---|---:|
| Call back a missed caller | `follow_up`, `human`, `calls:claim`, template "Missed call callback", `interaction_id` the miss, owner the claimer | started | 700 |
| Customer hand-over | `escalation` high (or `task` normal when scheduling), `model`, `chat:<session>`, template "Customer handover", unowned, a `work_item_source` trigger on its `customer.handover_requested` event | backlog | 300 |
| Task made or handed out | `task`, `human` | default (To do) | 250 |
| Raised by the assistant after a yes | `task`, `model`, `ask:<thread>`, `via = 'agent'`, `actor_kind = 'agent_on_behalf_of'` | default | 80 |

**Trail.** The board reads everything from `platform.activity` (`SQL:3090`): `closed_at` is the `occurred_at` of the row that moved the card into its terminal column (`docs/features/task-board.md:101-105`), quiet is the newest row (`work_board.py:687`), the tray is rows by somebody else. Per card the loader writes, each with its own `occurred_at` and a `platform.event` where the command emits one (`B/commands/work.py:189-660`): `created`; `assigned` (`new_identifier` the owner; `payload_public.batch` in a hand-out); `participant_added`; `moved` / `completed` / `cancelled` / `reopened` (`field = 'state_id'`, old and new state); `comment` (`payload_enc` the words, `payload_public.mentions` the person ids); `part_done` with `work_participant.completed_at`; `attached` with its `interactions.media_object`; field edits; `kept`. A claim card is created and completed inside 30 minutes, or called off when it lapsed (6 %).

**A hand-over card's due date is the product's.** This was read in the product at commit `af75145b8`.
- `forward_to_manager` writes every hand-over card with a deadline (`B/tools/utilities/escalation_tools.py:156-159`, `:198`, `:218-220`): the close of the business day at the card's site, on that site's clock. A request that lands after closing is due at the next open day's close. A card with no site takes the tenant's first site (`_deadline`, `:230-270`).
- A person may clear or move the deadline with a card edit. The edit writes one `rescheduled` line on the timeline (`B/commands/work.py:240-246`; the pair `due_local` and `due_tz` is set or cleared together, `:278-281`).
- So the seed gives every hand-over card the product's due date:
  - S07's first card: raised at the chat's hand-over (21:15, after hours) and due at day A's close.
  - S07's return card: raised at 15:41 and due at that day's close (`p6-1@close`). Slot 6 takes it at 16:05 and clears the due date in the same minute (a `rescheduled` step: the booking waits on the customer's answer). It is therefore open at T with no due date and not overdue (`board.open_at_t`).
- A bank hand-over card takes the same due date: its site's close on the day it lands, or the next open day's close after hours.

**Priorities.** Created urgent 4 %, high 18 %, normal 68 %, low 10 % (hand-overs high by their template). The loader walks cards in time order and never leaves more than three urgent open at a site (`TRACIORA_BOARD_URGENT_LIMIT`); `west` meets the limit six times since G, and each time the oldest urgent card steps down to high in the same group (`reprioritised`). At T: `main` 2 urgent, `east` 1, `west` 3.

**People.** Closed by the due time: `pNN.tasks_on_time` (slot 16 95 %, 5 90 %, 24 88 %, 6 and 29 85 %, 17 80 %, 7 70 %, 23 60 %, 22 50 %). Quiet spells (seven days with no line) per ten cards owned: slot 22 four, 23 three, 7 two, everyone else under one. Each spell is one `board.quiet` line pushed at 05:30 (`B/commands/nudges.py:72-89`); slots 22 and 23 answer one in three, the others "Keep it" within a day.

**At T: 45 open** (`cards.json`: 21 hand-written, 24 from the banks, `bank_open_at_t`).

| Owner | Open | Which |
|---|---:|---|
| 6 (junior operator) | 6 | the review (high, started, due her 2nd working day at 12:00); the Clabough estimate and "confirm the next day's drop-offs" (due today); the rear shocks of S07 (raised by the assistant); purchase-order numbers (from slot 3); saved replies (low). None overdue |
| 4 (senior operator) | 9 | cover for the week off (high); the no-show talk; the open shift; the stocktake; the alignment rack (quiet); two from slot 2 (the 90-day review, a standing cover answer); two weekly ones due on the Friday of W0 |
| 22 | 5 | the A5 call-back (S01), the supplier (S06), the regulars list (quiet): all overdue; two from the banks |
| 5, 23 | 4 each | slot 5's include the card that mentions slot 6; slot 23 has two overdue |
| 7, 16, 17 | 3 each | one overdue each for 7 and 17 |
| 29, 24 | 2 each | |
| 3, 8, 9 | 1 each | slot 8's is a second look at a job of slot 14 |
| nobody | 1 | a hand-over at `east`, 40 minutes old |

Planted: S01, S06, S16; exactly two quiet cards (`Q-04-rack`, `Q-22-regulars`); exactly one unowned. Every other open card has a line inside six days. No claim card is open (a live claim would lapse). The senior "sees his team's" through the board's `team` filter: 35 cards.

## 3. Calendar

| Series | Organiser, invitees | Rule |
|---|---|---|
| Managers' meeting (S09) | slot 2; 4, 5, 16, 3, 22 | weekly, Monday 08:00-08:30 (en) / 09:30-10:00 (ru) home time, no site. `event_series_exception`: `cancel` on the called-off Monday and on closed Mondays (en), `replace` to 10:00 in week T-5. Answers per occurrence: slot 22 by the cycle of `s9.pattern`; ru leads accept on their working Mondays and decline the others |
| Call review (S04) | slot 4; one junior each | en three weekly series (6 and 7 Wednesday, 17 Thursday at `east`). ru single entries, one a week on the junior's first working weekday (6, 7, 17, 29): a weekly rule cannot follow two-on, two-off |
| Morning huddle | slots 8, 18, 22; no invitees | `weekdays`, ten minutes before opening; the organiser's note of three lines is the occurrence's description |

Occurrences are `work.calendar_event` rows with `series_id` and `occurrence_key`, written from the series' start to T+14 d (`materialised_through`), each with its `calendar_event_participant` rows: `response`, `responded_at`, and `attended` on past ones (`SQL:2390-2760`; `work.py:685-1110`). Single entries (`calendar.json` `entries`): the review meeting and the junior's block on the review card (`kind = 'block'`, `work_item_id`), the stocktake, six interviews, two supplier visits, a safety session, the leave of slot 10 and the week off of slot 16 (`personal`, all day, `out_of_office`), en her six days off. Background: personal entries (about 60 per configuration) and blocks on one manager card in seven. About 535 entries per configuration.

**Zones.** An entry's `tz` is its site's `core.location.tz` (`west`'s for the `west` huddle), the home zone at no site. The managers' meeting is stored once, in the home zone; "07:00 his time" is arithmetic over `core.location.tz`, not something a screen shows (section 10).

**Two weeks ahead.** Both future Mondays exist; slots 4, 3, 5, 16 have answered, slot 22 neither. The review meeting, the block, the stocktake and the week off are in place.

## 4. Inbox

Derived, never loaded: `activity`, `diary`, `rota`, `due`, `rota_news`, `handover` lines (`work_board.py:2999-3288`). Loaded:

- **Read marks**: `platform.notification_queue` rows of type `board.inbox`, key `<person>:<line id>`, `sent_at = delivered_at = read_at` (`B/commands/notifications/inbox.py:53-84`). A line id is the activity row, the participant row, the shift, `due:<card>:<day>` or `handover:<card>`, so the loader derives the keys from its own ids. Every derived line older than the person's last visit gets one, read after a per-person delay (slot 6 20 minutes, slot 4 an hour, slot 1 a day, mechanics at their next clock-in), except the lines below. About 30,000 rows.
- **Pushed lines**: a row under its own type with `send_at` its own instant, `context_public`, words sealed in `context_enc`, `read_at` on the same row (`inbox.py:87-112`; read by `work_board.py:3289-3377`).

| Type (`B/packs.py:269-327`) | In the seed |
|---|---|
| `scheduled_task.ran`, `.failed` | every run of the seven tasks; the failure of S10 with `settled_at` after the rerun |
| `scheduled_task.removed` | once: slot 2 deletes a task slot 22 made in week T-20 and never opened |
| `board.quiet`, `board.given` | section 2; four hand-outs by the assistant for slot 4 ("Hand out 7") |
| `memory.proposed`, `.decided`, `.unverified` | S04's four proposals and the nine decided in history; one `unverified` in week T-11, kept by slot 4 |
| `punch.corrected` | every correction, to the site's seniors and admins |
| `knowledge.proposed`, `.decided` | slot 5's waiting correction; three decided in history |
| `tool.proposed` | once: slot 2 proposes a card over MCP in week T-8 and approves it |
| `conversation.new`, `.message`, `.mention` | written by the conversations loader |
| `calendar.google_lost` | once: slot 2 tried the import in week T-22, the grant was refused, she disconnected (the feature is off at T) |
| `ops.alert`, `push.canary`, `utility.timer`, `task.assigned`, `task.mention`, `assistant.completed` | push rows for the three people with a subscription (slots 4, 6, 15) and `platform.notification_alert` rows, last 14 days; `ops.alert` for slot 2 on every error or critical alert |
| `ops.feedback`, `ops.data_sharing` | none: reporting to the Traciora server is off for the demo tenant |

**The junior operator at T** (`inbox.json`): Needs you 2, the two cards due today. Unread Updates, the design's seven items: (1) the review card given; (2) her declined note; (3) next week's shifts published, which the product writes as one line a shift: 5 lines (en), 4 (ru); (4) the review meeting's invitation, answered accepted; (5) slot 5's mention; (6) the S07 customer's message; (7) this morning's "My call backs". 11 lines (en), 10 (ru).

**The senior operator at T**: Needs you 9, in the tray's order: the hand-over at `east`; two cards due today; requests R50 and R51; the two team notes; the knowledge correction; the quiet card. Unread Updates 2: slot 14's corrected clock-out; yesterday's "Tomorrow's gaps in cover". The design's "flagged no-show" cannot be a line (section 10). The two due-today lines exist when T's date is the Friday of W0.

## 5. Console

| Thing | What is loaded |
|---|---|
| Job history | `platform.job_run` (`SQL:3657`) for the jobs the tenant runs (`B/scheduling/cron_store.py:27-88`): `artifacts_purge`, `attachments_sweep`, `loop_automations`, `attendance_no_shows`, `roster_materialise`, `brief_tick`, `memory.dream`, `metric_rollup`, `context_sync`, `phonecalls_transcribe`, `phonecalls_analyse`. Rows for the last 90 days, which is what the product keeps; before that only `platform.metric_rollup` day and week rows of runs and outcomes back to G. Failed runs are exactly those behind the `job_failed` and `rollup_failed` alerts |
| Alerts | `platform.alert` x 25 (`alerts.json`), category operations, `rule_id` and `fingerprint`, the summary rendered from the product's own `alert.<rule>.summary` in the tenant's language. 12 warnings, 12 errors, 1 critical (ru 11, 13, 1: two channel alerts for VK and Avito); 23 resolved, 1 dismissed, 1 open: `push_silent_subscriptions`, a warning. S10: `job_failed` on `context_sync`, acknowledged by slot 2, resolved by her Run now |
| Usage and cost | `platform.usage_event` per signed-in day and `platform.metric_rollup`; proposed rates in section 8. Model cost per day is computed from the seeded runs, threads and drafts at the catalogue price of the release |
| Feedback | `platform.feedback_report` x 9 (`feedback.json`), direct rows: open 3, seen 2, resolved 3, wont_fix 1; the three of S10 on their Wednesdays; `status_by` slot 2 |
| Personal-data log | `platform.pii_access_log` (`SQL:3905`): one row per audited read, purposes `display`, `call_lookup`, `analysis`, `self_service`, `knowledge_history`; generated from the same per-person screen opens as the usage events, last 90 days |
| Scorecard wording | one edit of the tenant's `PHONECALLS_SCORECARD` on the Monday of week T-12: the anchor text of the `recap` check. `Scorecard.version` changes, `weights_version` does not (`B/phonecalls/scorecard.py:64-79`); verdicts before carry the old version, and none is rescored |

## 6. Hand-written and from banks

| Hand-written | Count (each language) | Story, people, anchor |
|---|---:|---|
| Cards with trails | 26 | S16 review (4, 6, 3, 9, 2; Monday W-1); S06 supplier (2, 22; Monday W-7, due Monday W-3); S01 call-back (2, 22; Monday W-18); S08 complaint and "prices" (5, 4, 7; slot 7's 4th working day back and the two days after); S03 early desk (4; Monday W-4 to W-3); S07 hand-over (assistant, 6; day A); call 29's second look (5, 8; Friday W-10); two quiet cards; the unowned hand-over; the junior's other five; the senior's other eight; slot 5's mention; slot 8's open second look |
| Shift requests | 64 | every person with a `pNN.requests` row |
| Series and entries | 8 series; 21 entries (en), 15 (ru) | section 3 |
| Notes | 4 huddle notes, 6 call-review notes | the no-show day, the fix day, the first day of the leave, `west`'s last day before T; one review per score period of slot 6 |
| Feedback | 9 | slots 3, 15, 14, 5, 6, 22, 16, 24, 4 |
| Alerts | 25 | product wording, designed parameters |
| Inbox at T | 2 | slots 6 and 4 |

| Bank (`banks.json`) | Patterns | Feeds |
|---|---:|---|
| Manager tasks | 60 (en), 62 (ru) | 250 cards |
| Assistant-raised tasks | 18 | 80 cards |
| Call-back closing lines | 14 | one claim card in three |
| Hand-over lines and stand-in customer words | 12 + 18 | 300 cards; the customer's words are the chat's |
| Comments: progress, done, blocked, mention | 24, 14, 10, 8 | about 900 comments |
| Calendar titles | 16 meetings, 8 blocks, 24 personal | single entries |
| Huddle lines by theme | 52 in 5 themes | a note is three lines from three themes: about 375 notes |
| Call-review lines | 16 strengths, 16 "try next", 4 numbers | by the weakest and strongest check of that person's week |

A pattern is not reused for one owner inside 30 days. Slots come from the seed files and the row itself.

## 7. Formats

Dates are anchors (rule R6). **Base**: `T`, `G`, `W-3.mon` (that weekday of week W-3; a closed date moves to the next full open day), `p6-2` (slot 6's 2nd working day before T), `east-2` (the shop's 2nd full open day before T), `S5`, `stock`, `S16meet`, `S9cancel`. **Hops**, left to right: `>p4` his next working day after; `>=p4` his first working day on or after; `<=p20` his last working day on or before (slot 20's no-show is `east-2<=p20` in the Russian configuration, `stories/TIMELINE.md`); `>!p6` her next day off after; `>open`, `>=open`, `>=mon`, `>+6d`, `>-1d`. **Time**: `@HH:MM` on the actor's shop's wall clock, `@o+1:10` after its opening, `@c-0:40` before its close, `@T-0:40` before T, `@close`. Texts may hold `{day:ANCHOR}`, `{month:ANCHOR}`, `{ledger:key}`.

```json
{"id": "S16-review", "story": "S16", "kind": "task", "origin": "human", "site": "main", "priority": "high",
 "title": "...", "description": "...", "why_now": "...",
 "created": {"by": 4, "at": "W-1.mon@o+1:10"}, "owner": 6, "due": "p6+2@12:00", "state_at_t": "started",
 "participants": [{"slot": 9, "role": "participant", "added_by": 4, "part_done_at": "W-1.thu@o+6:20"}],
 "trail": [{"at": "W-1.mon@o+1:10", "by": 4, "verb": "created"},
           {"at": "p4-1@c-0:40", "by": 4, "verb": "comment", "mentions": [3], "body": "@Donna Ledford: ..."}]}

{"id": "S09-managers-meeting", "kind": "meeting", "organiser": 2, "site": null, "repeat": "weekly",
 "rrule": "FREQ=WEEKLY;BYDAY=MO", "starts": "G>=mon", "written_through": "T>+14d", "start": "08:00", "end": "08:30",
 "invitees": [{"slot": 22, "role": "required", "rule": "..."}],
 "exceptions": [{"occurrence": "W-5.mon", "action": "replace", "start": "10:00", "end": "10:30"}]}

{"id": "S16-block", "kind": "block", "organiser": 6, "card": "S16-review", "start": "p6+1@14:00", "end": "p6+1@15:30",
 "booked": "p6-1@o+6:00", "show_as": "busy", "invitees": []}

{"id": "R08", "slot": "11", "kind": "change_date", "shift": "W-8.sat", "proposed": {"date": "W-7.sat"},
 "reason": "cant sat. swap w luis?", "filed": {"days_before_shift": 9, "at": "13:02"}, "status": "declined",
 "decided": {"by": 4, "working_days_after_filing": 0, "at": "c-0:50", "note": "Luis worked your last two. ..."}}

{"id": "FB9", "slot": 4, "category": "missing_feature", "severity": "annoying", "status": "open",
 "sent": "east-2@c-1:00", "status_set": null, "screen": "planner", "summary": "..."}

{"id": "AL22", "rule_id": "job_failed", "subject": "context_sync", "severity": "error", "category": "operations",
 "params": {"job": "context_sync", "error": "OperationalError"}, "summary": "Job context_sync failed (OperationalError)",
 "opened": "W-1.mon@07:56", "status_at_t": "resolved", "closed": "W-1.mon@08:48",
 "acknowledged": {"by": 2, "at": "W-1.mon@08:18"}}
```

`"by": "A"` is the assistant, `"A:6"` the assistant on behalf of slot 6.

## 8. Ledger rows

**Proposed** (designed unless said):

| Key | Value | Mark |
|---|---|---|
| `roster.mechanic_days_off` (ru) | 10 Sat Sun; 11 and 13 Wed Thu; 12 and 14 Mon Tue; 15 Fri Sat; 18, 19, 25 Sat Sun; 20 Thu Fri; 21 Mon Wed (Tuesday at `main`); 26 Sun Mon; 27 Wed Thu; 28 works Fri Sat Sun. Every weekday keeps the minimum of `kb.schedule.minimums` | fixed |
| `roster.saturday` (en) | advisors 5, 6, 7 in turn with slot 29; technician crews 11, 13, 15 and 12, 14, 21 on alternate weeks | fixed |
| `roster.publish` | home shops Thursday 11:20-11:55 by slot 4; `west` Sunday about 20:40 by slot 22; at T `west`'s W+1 is a draft | fixed |
| `roster.late_at_t` | slot 28, rule of section 1 | fixed |
| `roster.shifts` | derived: about 3,800 (en), 3,300 (ru), G to T+14 d | fixed |
| `punch.on_time_window_min` | -12 to +4 around the start; late 6 to 25 after | rate, ±2 |
| `s14.requests.by_kind` | en 28 / 6 / 30, ru 27 / 11 / 26 (time / date / remove); `west`: 6 expired, 6 approved (1 by slot 2), 1 declined | fixed |
| `board.open_at_t.by_owner` | the table of section 2 | fixed |
| `board.priority_mix` | urgent 4, high 18, normal 68, low 10 %; six step-downs at `west` | rate, ±3, at least 17 |
| `board.quiet` | two quiet cards at T; spells per ten cards: slot 22 four, 23 three, 7 two | fixed; rate |
| `board.second_look_open` | slot 8's open card needs one warranty order on a job of slot 14 (en Dogwood Lane Florals' ProMaster City, ru ИП Абрамова's Largus): the pads are inside their warranty; when the card's due day falls after T, an appointment at opening on that day instead | fixed |
| `calendar.entries` | managers' meeting 25; call reviews about 75; huddles about 375; singles about 60 | scales (huddle notes), fixed (the rest) |
| `inbox.at_t` | junior: needs 2, items 7, lines 11 (en) / 10 (ru); senior: needs 9, updates 2 | fixed |
| `console.alerts` | 25 by rule as `alerts.json`; one open warning | fixed |
| `console.feedback` | 9: open 3, seen 2, resolved 3, wont_fix 1 | fixed |
| `console.context_sync_at` | 07:55 (en), 08:55 (ru): five minutes before slot 2's Monday report | fixed |
| `console.usage` | signed-in people on a working day 22 of 28; screen opens per person and day: advisors 60, managers 40, mechanics 6; phone share 45 % | rate, ±5 |
| `console.push_subscriptions` | slots 4, 6, 15 | fixed |

**Relied on**: `time.*`, `site.hours.weekday`, `site.open_days`, `site.closed_dates`, `site.stocktake`, `site.morning_block`, `roster.advisor_pattern`, `roster.manager_pattern`, `roster.mechanic_pattern`, `late.grace_min`, `geo.checkin_radius_m`, `pNN.late`, `pNN.forgot_clock_out`, `pNN.absent`, `pNN.no_shows`, `pNN.requests`, `pNN.tasks_on_time`, `p22.owner_tasks`, `s14.requests`, `s14.instances`, `s14.dates`, `s5.week_off`, `s5.leave`, `s5.days_off_so_far`, `s3.fix`, `s9.meeting`, `s9.pattern`, `s16.card`, `s6.supplier_task`, `s8.*`, `s12.brake_price`, `s12.proposal`, `s4.notes`, `s10.tasks`, `s10.failure`, `s10.feedback`, `board.cards_since_g`, `board.open_at_t`, `calls.queue_at_t`, `calls.claims`, `kb.schedule.minimums`, `kb.schedule.rules`, `kb.standards`, `kb.stocktake.rules`, `kb.desk_habits`, `kb.day_times`.

## 9. Eval questions this part supports

| # | Question | Asked by | Population, period, definition | Expected | Proof | Kind |
|---|---|---|---|---|---|---|
| W1 | Who has not clocked in for a shift that has started? | 4 (senior) | Published shifts at every site whose start plus grace is before the asking instant, with no clock-in | Slot 28 at `west`, with the start of his shift. Nobody else | `workforce.shift`, `punch` | value |
| W2 | Which weeks of the roster are not published yet? | 4 (senior) | Shifts from T to T+14 d by site and status | Home shops: W+2 is a draft. `west`: W+1 is a draft | `shift.status`, `roster_publish` | list |
| W3 | When does Charlotte Pike publish its roster? | 2 (admin) | `roster_publish` rows since G by site: the publishing instant against the week it covers | On the Sunday evening before the week, every week; the home shops on the Thursday before noon. The standard is Thursday noon | `roster_publish.published_at` | explanation |
| W4 | What did Cody ask for, and what was decided? | 4 (senior) | Slot 15's requests since G | Four: three changes of hours (two approved, one declined with slot 4's words), one day off he took back | `shift_change_request` | value |
| W5 | Which shift requests at Charlotte Pike were never answered? | 2 (admin) | Requests since G on `west` shifts with status expired | Six: R53, R54 (slot 23), R56 (24), R58 (26), R61, R64 (28), with their days | `shift_change_request` | list |
| W6 | Show me Dustin's shift requests. | 12 (worker) | A worker reads his own requests | Refused by rank; his own can be shown | tool floors | refusal |
| W7 | Was Shane late on the days he clocked in from outside the site? | 22 (senior) | Slot 26's clock-ins with a location exception | No: both on time, 600 metres away | `punch.exception_type`, `geo_distance_m` | value |
| W8 | What is on my board? | 6 (junior) | Her open cards at T | Six: the review (high); two due today; three more. None overdue | `work.work_item` | list |
| W9 | Which cards have gone quiet? | 4 (senior) | Open cards with no timeline line for seven days, not due further ahead | Two: his alignment-rack card and slot 22's regulars list | `platform.activity` | list |
| W10 | Is any customer waiting for a person at my shop? | 6 (junior, `main`) | Unowned hand-over cards at the sites she reads | None: the one waiting is at `east` | `work_item` by site | nothing |
| W11 | Is any customer waiting for a person? | 4 (senior) | The same, all sites | One at `east`, since 40 minutes before T | the same | value |
| W12 | Give Donna a task: the days-to-pay table by Monday. | 6 (junior) | The rank rule | Refused: a junior may not put work on a middle. It can offer a comment on the review card | `work_board.py:2052` | refusal |
| W13 | How did Dale do with the tasks Claire gave him? | 2 (admin) | Cards created by slot 2 and owned by slot 22 since G | Twelve: six closed on time, three late, three open and overdue | `work_item`, `activity` | value |
| W14 | Did anyone decline the stocktake? | 9 (junior) | The entry's invitations | Nobody: all three accepted | `calendar_event_participant` | nothing |
| W15 | What needs me? | 4 (senior) | His Needs you at T | Nine lines in the tray's order; the hand-over first | the tray read as him | list |
| W16 | Is any card of mine overdue? | 4 (senior) | His open cards at T | None overdue; two are due today (when T's date is the Friday of W0) and one has gone quiet | `work_item`, `activity` | nothing |
| W17 | Who covered Austin's shift? | 16 (middle, `east`) | Shifts and punches at `east` on the no-show day | Slot 21, on a shift of his own published that morning; slot 20's shift has no punch | `shift`, `punch`, `event` | value |

## 10. Product gaps met

1. **A no-show reaches nobody.** `shift.no_show` is an event with no reader: no tray source, no Home panel (`packs.py:239`; `work_board.py:3158-3211`). The senior's "flagged no-show" line does not exist.
2. **An invitation to a series is answered one occurrence at a time** (`work.py:1009-1056`), and a series is written a year ahead: 52 lines in Needs you per invitee. The seed writes two weeks ahead.
3. **One tray line and one push per published shift** (`work_board.py:3113-3141`): "next week's shifts" is five lines.
4. **The calendar says the product keeps one time zone** (`docs/features/calendar.md:161-163`), while `core.location.tz` is per site (`B/commands/locations.py:74-97`). No screen shows the meeting at `west`'s hour.
5. **No alert rule says a data source cannot be reached** (`observability/rules.py:929-961`).
6. **`punch.exception_type = 'missing'` and `auto_closed` are never written**; a forgotten clock-out is the absence of a row.
7. **Job runs are kept 90 days** (`docs/features/console.md:646`), not six months.
8. **The planner's "who is in" is not built** (`docs/features/roster.md:195`): being late is on the late person's own Home only.
9. **The tray is computed over the whole history on every read** (`since` defaults to none): six months need about 30,000 read rows to look read.
10. **A feedback report's status**: the tenant's Reports view is read-only (`console.md:485`); who sets a status at a tenant was not found.
11. **A quiet card is asked about once per spell**: slot 22's has been silent for three weeks since its one line.
12. **`conversation.new` goes to every manager at once** (the complaint of FB8).
