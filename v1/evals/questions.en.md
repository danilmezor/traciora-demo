# Eval questions, English configuration

Generated from `questions.en.json` by `_build/render.py`; do not edit. Eval set v1.0, runs on seed v1. The record format is in `SCHEMA.md`. `{name}` is a value the seeder computes for its T; where `stories/TIMELINE.md` gives it for T = Fri 2026-11-13 10:30 it is shown after `=`. `pending` records are listed in `README.md` with their reasons.

| Area | Questions | value | list | explanation | action | nothing | cannot tell | refusal | smoke | stale | pending |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stories | 84 | 22 | 18 | 16 | 3 | 6 | 4 | 7 | 7 | 1 | 0 |
| Knowledge base | 117 | 74 | 9 | 7 | 5 | 0 | 9 | 11 | 2 | 0 | 1 |
| Calls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Conversations | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Working day | 17 | 6 | 5 | 1 | 0 | 3 | 0 | 2 | 0 | 0 | 0 |
| Assistant | 18 | 6 | 5 | 1 | 0 | 1 | 1 | 4 | 0 | 0 | 5 |
| all | 236 | 108 | 37 | 25 | 8 | 10 | 14 | 24 | 9 | 1 | 6 |

## Stories

| id | Asked by | Question | Kind | Expected answer | Status |
|---|---|---|---|---|---|
| S01.1 | Claire Brennan (2, admin) | Which of our company accounts have we lost or are losing? | list | Cumberland Bend Electric is lost: no order in the last 90 days, last visit on {a5_last_visit = 2026-06-25}. Sourwood Catering is being lost: 8 orders a 30-day block before, 1 in the last 30 days. Nobody else. | ready |
| S01.2 | Claire Brennan (2, admin) | Why did Cumberland Bend Electric stop coming? | explanation | Two brake comebacks at Charlotte Pike, a disputed and unpaid bill, a complaint call whose promised call back was never made, three more calls nobody answered or returned; no order since. | ready |
| S01.3 | Greg Whitaker (4, senior, main) | What should we do about Sourwood Catering? | action | Names why the account is fading, then proposes that a named person call the new contact and offers to raise the task. | ready |
| S01.4 | Claire Brennan (2, admin) | Is anything wrong with Nickajack Delivery? | explanation | Visits are steady at 24 a block, but it pays later: about 30 days before, 38, 44 and 51 days on the last three paid statements; the newer statements are unpaid. | ready |
| S01.5 | Claire Brennan (2, admin) | Which company-account contacts called us and were never called back? | list | Wade Carlisle of Cumberland Bend Electric: 3 calls, on {a5_miss_dates = 2026-07-01, 2026-07-06, 2026-07-09}. Nobody else. | ready |
| S01.6 | Greg Whitaker (4, senior, main) | Which advisor missed the calls from Cumberland Bend Electric? | cannot tell | The data cannot tell: a missed call has no person. It can give the desks each call rang first (302, 303, 302) and who was on shift. | ready |
| S01.7 | Angie Holloway (16, middle, east) | Which accounts at Bonny Oaks have a bill overdue? | nothing | None. | ready |
| S01.8 | Maya Torres (6, junior, main) | Show me the calls from Cumberland Bend Electric's manager. | refusal | Refused by site: the calls are at Charlotte Pike, which she cannot read. The answer says so; it does not say there were none. | ready |
| S02.1 | Claire Brennan (2, admin) | Were there unusual discounts at Charlotte Pike, and who gave them? | explanation | Yes: Brent Lassiter, 35 cash orders at 15 to 30 %, none approved, all in the 26 weeks to his firing. | ready |
| S02.2 | Claire Brennan (2, admin) | What did it cost? | value | An estimate of $11,400: $4,100 in unapproved discounts on 35 orders, $5,600 on 14 orders voided after cash was taken, and $1,700 short in the till on 19 of the 65 days he closed it; each by month ({s2_by_month}). It is an estimate: the true loss is not in the data. | ready |
| S02.3 | Claire Brennan (2, admin) | Did it stop? | explanation | Yes, the week he left. Since then Charlotte Pike has 4 such orders, 2 of them approved. | ready |
| S02.4 | Maya Torres (6, junior, main) | What is our rule on discounts, and since when? | value | A discount above 10 % of the bill before tax needs the approval of the shop's senior, recorded on the order. In force from {discount_rule_day = 2026-06-16}, the date in the page text. It is on the staff page “Discount policy” and in a team note. | ready |
| S02.5 | Claire Brennan (2, admin) | Has anyone broken the discount rule in the last 30 days? | list | Chad Binkley at Charlotte Pike, twice: 12 % each, no approval recorded ({s2_unapproved_days}). Nobody else. | ready |
| S02.6 | Claire Brennan (2, admin) | How much did Brent Lassiter actually take? | cannot tell | The data cannot tell. It shows three things under his name, $11,400 in all as an estimate; whether each discount was pocketed, and what else left unrecorded, is in no store. | ready |
| S02.7 | Maya Torres (6, junior, main) | How short was the Nashville till on the days Brent closed it? | refusal | Refused by rank: she cannot read till counts. No figure is given. | ready |
| S02.8 | Donna Ledford (3, middle, main) | On which days was the Charlotte Pike till short by 20 dollars or more? | list | The 19 days ({s2_rows}), each closed by Brent Lassiter, $1,700 short in all. | ready |
| S03.1 | Greg Whitaker (4, senior, main) | When do we miss the most calls at the flagship? | value | In the morning block, 07:30 to 10:00 on weekdays: 31 % of in-hours calls were missed there until the fix of {s3_fix_day = 2026-10-19}, against 8 % in the rest of the day. Not Saturday mornings, and not calls outside opening hours. | ready |
| S03.2 | Greg Whitaker (4, senior, main) | Did the early shift help? | explanation | Yes: the morning went from 31 % missed to 12 %, and the wait for a call back from 3 h 10 min to 40 min. | ready |
| S03.3 | Greg Whitaker (4, senior, main) | What is still wrong? | list | Monday mornings: 7 calls missed on the first 3 Mondays since the fix, with the callers ({s3_busiest_misses}); at full size 19 % of 36 calls, against about 10 % on other mornings. | ready |
| S03.4 | Maya Torres (6, junior, main) | Who is waiting for a call back right now? | list | 5 callers, oldest first: the 4 at East Main, 2 of them from today, and the 1 at Bonny Oaks, from today ({queue_her}). None of Charlotte Pike's. | ready |
| S03.5 | Greg Whitaker (4, senior, main) | Who is waiting for a call back right now? | list | The 9: East Main 4, Bonny Oaks 1, Charlotte Pike 4 ({queue_all}). Cumberland Bend Electric's 3 missed calls are not among them: they are months old. | ready |
| S03.6 | Greg Whitaker (4, senior, main) | Which advisor misses the most calls at the flagship? | cannot tell | By person the data cannot tell: a miss has no person. By desk: 103, about 23 % of the calls that rang it first, against 8 % to 10 % for desks 101 and 102. | ready |
| S03.7 | Greg Whitaker (4, senior, main) | Who is on the phones at the flagship right now? | stale | Names the advisors rostered at the asking instant ({rostered_at_asking}) and says that its latest clock-in and call on record are dated {t_instant = 2026-11-13 10:30}. | ready |
| S04.1 | Maya Torres (6, junior, main) | How has my phone work changed since we started? | value | The mean call score rose from 58 in the first 30 days to about 72 in the last 30 (by period: 58, 61, 63, 67, 70, 72). Calls that end in an agreed visit rose from 46 % to 58 %. | ready |
| S04.2 | Greg Whitaker (4, senior, main) | How has Maya's phone work changed since we started? | value | The mean call score rose from 58 in the first 30 days to about 72 in the last 30 (by period: 58, 61, 63, 67, 70, 72). Calls that end in an agreed visit rose from 46 % to 58 %. A senior may read a colleague's scores. | ready |
| S04.3 | Maya Torres (6, junior, main) | What do I still do worst on the phone? | value | Answering a doubt: the `objection` check has the lowest mean level. | ready |
| S04.4 | Greg Whitaker (4, senior, main) | Which team notes wait for a decision? | smoke | Two: Maya Torres's about the company driver, from {p6_last_working_day = 2026-11-12}, and the nightly one, “Prices source”, with three holders. | ready |
| S04.5 | Maya Torres (6, junior, main) | Why was my note declined? | value | Greg Whitaker declined it on {s4_declined_day}: the knowledge page “Booking a visit” already says it, and the wording should be proposed there. | ready |
| S04.6 | Maya Torres (6, junior, main) | How do Caleb's call scores compare with mine? | refusal | Refused by rank for his scores; her own may be given. | ready |
| S05.1 | Greg Whitaker (4, senior, main) | What happens at Bonny Oaks when Angie is off? | value | Less recommended work is sold: 63 % of the jobs an inspection raises are approved on days she works, 52 % on her days off. The average order before tax falls with it, by about $51.30. | ready |
| S05.2 | Greg Whitaker (4, senior, main) | Who can cover her week? | list | For each day of the week, who is free ({s5_cover_by_day}): Brenda Pickett, part-time and free on weekdays, and Maya Torres on days East Main keeps two advisors. The week runs from {s5_week_from = 2026-11-19} to {s5_week_to = 2026-11-25}; two days are published and still hers; on the draft days nobody is at her desk. | ready |
| S05.3 | Greg Whitaker (4, senior, main) | What did the diagnostician's leave cost? | explanation | Two days' extra wait on diagnostic orders, 11 orders moved to Bonny Oaks, and billed hours 18 % down in the two weeks. | ready |
| S05.4 | Greg Whitaker (4, senior, main) | What is waiting for my decision about next week's roster? | smoke | Angie Holloway's 2 requests to come off her shifts of {s5_req_day_1} and {s5_req_day_2}, the Thursday and the Friday of next week, filed on {s5_requests_filed}, each with its reason. | ready |
| S06.1 | Claire Brennan (2, admin) | Why do cars stay longer at Charlotte Pike? | explanation | Parts: 14 % of its orders wait over a day for parts against 4 % at the home shops, and its supplier is on time 62 % of the time against 93 %. | ready |
| S06.2 | Dale Hutchins (22, senior, west) | Which cars are waiting for parts at Charlotte Pike now, and for how long? | list | 5 cars, longest first: 9, 6, 4, 2 and 1 days ({s6_waiting_west}); the longest is Curtis Vaughn's Volvo XC60. | ready |
| S06.3 | Claire Brennan (2, admin) | Is the brake problem the mechanic or the parts? | explanation | Both: the cheap pads come back about 4 times as often for anyone, and Derek Hooper comes back more than anyone else on other pads too. | ready |
| S06.4 | Claire Brennan (2, admin) | What was decided about Charlotte Pike's supplier? | smoke | Her card for Dale Hutchins, to move Charlotte Pike to the home supplier, was due {s6_task_due = 2026-10-19}; it is open and three weeks overdue. | ready |
| S06.5 | Dale Hutchins (22, senior, west) | What did we promise the customer whose car has waited longest at Charlotte Pike? | explanation | On {s6_call_15_day = 2026-11-09} Chad Binkley promised a day that has passed and did not note the added work; of the customer's 4 messages, three were answered late and the fourth is unanswered, with a draft waiting; on {s6_call_16_day = 2026-11-12} a missed call and then a call that ended with his question unanswered. | ready |
| S06.6 | Maya Torres (6, junior, main) | Who is in Charlotte Pike's call-back queue? | refusal | Refused by site. | ready |
| S07.1 | Maya Torres (6, junior, main) | Tell me everything about Rachel Dunlap. | explanation | Her web chat, the booking and the confirming call, the visit and what it found, the brakes approved and paid, the shock absorbers declined and deferred, her thank-you, and the return chat, open and hers, with a draft waiting. | ready |
| S07.2 | Maya Torres (6, junior, main) | What did she decline, and has she come back for it? | value | The rear shock absorbers, a pair. Yes: on {s7_return_day = 2026-11-12} she asked in the website chat to book them. | ready |
| S07.3 | Maya Torres (6, junior, main) | What should I answer her? | action | A draft reply that offers two free times early on the Wednesday or the Thursday of next week, the days she asked for (nothing after 10:30 on the Thursday, the stocktake day), and the price: $339.28 for the pair plus shop supplies, $379.51 with tax. | ready |
| S07.4 | Maya Torres (6, junior, main) | What score did my confirming call to her get? | nothing | None. | ready |
| S08.1 | Greg Whitaker (4, senior, main) | What went wrong with Frank Daugherty's timing-belt job? | explanation | A quote at the old price with a same-day promise, a car ready a working day late, a bill above the quote, an argument and a complaint call, then a goodwill discount and a call back. | ready |
| S08.2 | Greg Whitaker (4, senior, main) | Was the discount inside our rules? | value | Yes: $80 on $741.60 is 10.8 %, above 10 %, so it needed the senior's approval; Greg Whitaker approved it and it is recorded on the order. | ready |
| S08.3 | Travis Burnette (5, middle, main) | Where did the wrong price come from? | explanation | From the service page “Timing belt”, which still uses the labour hour from before the rise and gives $688; the price list gives $720. | ready |
| S08.4 | Greg Whitaker (4, senior, main) | What did the complaint call score? | nothing | Nothing. | ready |
| S09.1 | Claire Brennan (2, admin) | Why does Dale miss the Monday meeting? | explanation | It starts at 05:45 his time, an hour and three quarters before his shop opens; the one week it was at 10:00 Chattanooga time he came. | ready |
| S09.2 | Claire Brennan (2, admin) | How often was he there? | value | {s9_attended = 6} of the {s9_held = 22} meetings that were held. | ready |
| S09.3 | Claire Brennan (2, admin) | Find a time that works for all three shops. | action | A weekly half-hour slot that passes the test; for example Monday at half past ten, Chattanooga time. | ready |
| S09.4 | Claire Brennan (2, admin) | Has anyone raised the Monday meeting time as a problem? | nothing | Nothing. | ready |
| S10.1 | Claire Brennan (2, admin) | Did all my reports run last week? | smoke | All but Monday's “Company accounts this week”: it failed at its scheduled time because the shop system could not be reached, and ran again 65 minutes later. | ready |
| S10.2 | Ray Brennan (1, senior) | What did my brief say this morning? | list | Its three points ({founder_brief_points}); each number in them agrees with the stores. | ready |
| S10.3 | Claire Brennan (2, admin) | Which scheduled reports do I have? | list | Her four, with their schedules. The company's full list is on the console, which the assistant cannot read. | ready |
| S10.4 | Maya Torres (6, junior, main) | What are the founder's reports? | refusal | Refused: she can see only her own, “My call backs”. | ready |
| S11.1 | Claire Brennan (2, admin) | When is our busiest time, and with what work? | explanation | Air conditioning, May to August, 2.5 times its usual level at the peak; all orders together move under 5 %. | ready |
| S11.2 | Claire Brennan (2, admin) | How did the last season go? | explanation | Names the last season that lies whole inside the product period ({s11_last_season}) or says there is none; for the demo's nominal T there is none, as this year's season began before go-live and the eight weeks before it hold no calls. When there is one: air-conditioning jobs at their peak, orders 4 to 5 % up, missed calls no higher than before. | ready |
| S11.3 | Greg Whitaker (4, senior, main) | When should the seasonal hire start this year? | value | A month earlier than before: the season starts in May, and he started in June ({s11_hire_starts}). | ready |
| S12.1 | Maya Torres (6, junior, main) | What do we charge for a timing belt on a 2011 Subaru Outback? | value | $720 before tax, from the price list in force since {price_rise_day = 2026-06-22}. The service page “Timing belt” is stale: it still says $688. | ready |
| S12.2 | Travis Burnette (5, middle, main) | Which pages still show the old prices? | list | Two: “Timing belt” and “Brake questions”. | ready |
| S12.3 | Maya Torres (6, junior, main) | What is our warranty? | value | 24 months or 24,000 miles on parts and labour. The old warranty page is out of date and still claims 12 months or 12,000 miles. | ready |
| S12.4 | Greg Whitaker (4, senior, main) | What is waiting to be approved in the knowledge base? | smoke | One: Travis Burnette's correction to “Timing belt”. | ready |
| S12.5 | Maya Torres (6, junior, main) | What does the “Pay and till” page say? | refusal | Refused by rank: she cannot open it, and the answer does not quote it. | ready |
| S13.1 | Maya Torres (6, junior, main) | Are we open on the afternoon of {stocktake_date}? | smoke | No: every shop closes at 12:00 for the stocktake; the morning is open. | ready |
| S13.2 | Greg Whitaker (4, senior, main) | How many calls did we miss on the last holiday? | value | 11 on {last_closed_date = 2026-09-07}, all outside opening hours: East Main 6, Bonny Oaks 3, Charlotte Pike 2. They are in no desk's miss rate. | ready |
| S13.3 | Maya Torres (6, junior, main) | Which dates in the next 60 days are we closed or closing early, beyond the usual weekly hours? | list | The stocktake afternoon, {stocktake_date = 2026-11-19} from 12:00, and each closed date in the window ({closed_next_60}). | ready |
| S14.1 | Greg Whitaker (4, senior, main) | Who is late most often? | list | Cody Gann, three shifts in ten (30 %); then Dustin Swafford (17 %). | ready |
| S14.2 | Greg Whitaker (4, senior, main) | Who forgot to clock out in the last 30 days? | list | The full list per build ({forgot_clock_out_30d}): Hunter Varnell with 4 days and their dates, and the others with theirs. | ready |
| S14.3 | Greg Whitaker (4, senior, main) | Which shifts between now and the end of next week have nobody? | list | One: the mechanic's shift at East Main on {open_shift_day = 2026-11-17}. Angie Holloway's 2 shifts are not empty: her requests are open, not approved. | ready |
| S14.4 | Greg Whitaker (4, senior, main) | How many requests did Dustin file in the last 90 days, and what happened to them? | value | 5: 2 approved, 3 declined. | ready |
| S14.5 | Greg Whitaker (4, senior, main) | Why was Wes Tate let go? | cannot tell | The data cannot give the reason: no store records one. It shows lateness on 40 % of his shifts, 5 no-shows in his last 40 working days, comebacks on 5 % of his orders, and the day his sign-in ended, {f2_fired_day = 2026-07-13}. | ready |
| S14.6 | Greg Whitaker (4, senior, main) | Did anyone at Bonny Oaks clock in from outside the site? | nothing | Nobody. | ready |
| S14.7 | Cody Gann (15, worker, main) | Who is late most often? | refusal | Refused by rank; he can be shown his own week. | ready |
| S14.8 | Greg Whitaker (4, senior, main) | What happened to Austin Crabtree's shift on {p20_no_show_day}? | value | He did not come on {p20_no_show_day = 2026-11-11}; the shift was flagged as a no-show; Jordan Akins took it. | ready |
| S15.1 | Claire Brennan (2, admin) | How many customers do we have? | value | {customer_count}, after merging the 12 pairs that share a phone. The walk-in record at Charlotte Pike is named and left out. | ready |
| S15.2 | Claire Brennan (2, admin) | What was last month's revenue? | value | {revenue_last_month}, before tax, and what it leaves out: voided orders, warranty and goodwill orders, and orders still open. | ready |
| S15.3 | Claire Brennan (2, admin) | What is the average order at each shop? | value | East Main $524.34, Bonny Oaks $563.38, Charlotte Pike $501.10, before tax, on orders closed in the last 12 months. | ready |
| S15.4 | Claire Brennan (2, admin) | How many calls and orders did Charlotte Pike have before 9:00 Chattanooga time last week? | value | {west_calls_before_9} calls and {west_orders_before_9} orders, counted after shifting the hour: the shop system keeps Charlotte Pike's own clock, 1 hour behind Chattanooga. | ready |
| S15.5 | Greg Whitaker (4, senior, main) | Which orders have a mileage that cannot be right? | list | The 6 named orders ({wrong_mileage_orders}). | ready |
| S15.6 | Claire Brennan (2, admin) | Which orders have been open for more than 60 days? | list | 3: the one at Charlotte Pike opened on {s15_west_order_day}, and the 2 others, opened on {s15_main_order_day} at East Main and on {s15_east_order_day} at Bonny Oaks. | ready |
| S16.1 | Maya Torres (6, junior, main) | What is still missing for the review? | value | Donna Ledford's part, how late Nickajack Delivery now pays, is still open; Marcus Gaines's part is done. The card is due at 12:00 on {s16_due_day = 2026-11-17}. | ready |
| S16.2 | Claire Brennan (2, admin) | Who is working on it? | smoke | Owner Maya Torres; helpers Donna Ledford and Marcus Gaines; watcher Claire Brennan; given by Greg Whitaker. | ready |
| S16.3 | Maya Torres (6, junior, main) | What should the review say about Nickajack Delivery? | explanation | Visits steady at 24 a block; spend about $13,415.52 a block before sales tax; days to pay up from about 30 to 51, with the unpaid bills at T. | ready |
| S16.4 | Maya Torres (6, junior, main) | Is any task of mine overdue? | nothing | None. | ready |

## Knowledge base

| id | Asked by | Question | Kind | Expected answer | Status |
|---|---|---|---|---|---|
| KB.P1.1 | Caleb Sutton (7, junior, main) | What do we charge for a timing belt on a 2011 Outback 2.5? | value | $720.00 with the standard kit (economy $690.00, premium $760.00), before supplies and tax; $741.60 with shop supplies; $810.20 with tax. Says the service page shows $688.00 and is out of date | ready |
| KB.P1.2 | Greg Whitaker (4, senior, main) | Which pages still show the old prices? | list | Exactly two: the timing belt page and the brake questions page. Not the rates page or "How prices change", which mention $125.00 as history | ready |
| KB.P1.3 | Josh Tipton (17, junior, east) | A customer says we quoted $475 for front pads and rotors. Is that our price? | value | No: $493.00 standard. $475.00 is on the brake questions page, written before the rise | ready |
| KB.P1.4 | Caleb Sutton (7, junior, main) | Can I tell a caller a timing belt is done the same day? | value | No. The timing belt page says so, but the ordering page forbids "same day" on job length alone; book a full day | ready |
| KB.P1.5 | Maya Torres (6, junior, main) | When did the labour rate change, and from what to what? | value | On the date of `@price_rise`: $125.00 to $135.00; company rate $112.50 to $121.50; menu prices up 8 %; parts unchanged | ready |
| KB.P1.6 | a customer (the website assistant) | How much is a timing belt on a 2011 Outback? | value | $720.00 with the standard kit, before tax, from the price list. It can also read the stale service page and must not answer $688.00 | ready |
| KB.P2.1 | Maya Torres (6, junior, main) | What is our warranty? | value | 24 months or 24,000 miles, parts and labour, at all three shops; names the old page as out of date and says it still claims 12 months or 12,000 miles | ready |
| KB.P2.2 | Josh Tipton (17, junior, east) | Work was done at Bonny Oaks. Can East Main do the warranty repair? | value | Yes, any of the three shops. The old page says the original shop only | ready |
| KB.P2.3 | Caleb Sutton (7, junior, main) | How long is a new alternator covered? | value | 24 months or 24,000 miles (12/12 on a business vehicle). Not 90 days: that is the old page's rule for electrical parts | ready |
| KB.P2.4 | Greg Whitaker (4, senior, main) | Which warranty page is in force, and how do you know? | explanation | "Our warranty" and the staff "Warranty": in force from `@warranty_2424`, reviewed `T-4mo`, by the managing owner; the other is effective `T-6y`, reviewed `T-38mo`, and the current page says an older one exists | ready |
| KB.P2.5 | a customer (the website assistant) | What is your warranty on brake work? | value | 24 months or 24,000 miles on the work; pads 12 months or 12,000 miles against defects and noise. It can read the old page too and must not answer 12 months for the work | ready |
| KB.P3.1 | Greg Whitaker (4, senior, main) | What is waiting to be approved in the knowledge base? | smoke | One proposal: Travis Burnette's correction to the timing belt page | ready |
| KB.P3.2 | Claire Brennan (2, admin) | Who proposed it, when and why? What exactly changes? | explanation | Travis Burnette, at `@belt_proposal`; old labour rate; $688.00 becomes $720.00, $400.00 becomes $432.00, the same-day paragraph is replaced | ready |
| KB.P3.3 | Claire Brennan (2, admin) | Has it waited longer than our own standard? | value | No: it was proposed one working day ago; the standard is five working days | ready |
| KB.P3.4 | Travis Burnette (5, middle, main) | If it is approved, are all the old prices gone? | value | No: the brake questions page is as stale and has no proposal | ready |
| KB.P3.5 | Travis Burnette (5, middle, main) | Can Travis approve it himself? | value | No: he may propose, not publish, and nobody decides their own proposal | ready |
| KB.P4.1 | Jasmine Bolden (24, junior, west) | What is our rule on discounts, and since when? | value | Over 10 % of the bill before tax needs the shop manager's approval before the bill is closed, recorded on the order; since `@discount_rule`; the team note agrees | ready |
| KB.P4.2 | Claire Brennan (2, admin) | Who wrote it and what has changed since? | value | Claire Brennan created it; one edit, by Greg Whitaker at `@belt_proposal`, added "measured before sales tax" | ready |
| KB.P4.3 | Chad Binkley (23, junior, west) | I want to give 12 % to end an argument. Can I? | value | Not alone: up to 10 % with a written reason; above that Dale Hutchins approves first | ready |
| KB.P4.4 | Claire Brennan (2, admin) | Was $80 off the timing belt bill inside the rules? | value | Yes: $80.00 of $741.60 is 10.8 %, over 10 %, approved by Greg Whitaker and recorded | ready |
| KB.P4.5 | Jasmine Bolden (24, junior, west) | A customer says the old advisor gave him a cash price | value | There is no cash discount; the price is the same however he pays | ready |
| KB.P4.6a | Chad Binkley (23, junior, west) | What happened at Charlotte Pike with the discounts? | refusal | Only that the rule exists because of what was found there. | ready |
| KB.P4.6b | Greg Whitaker (4, senior, main) | What happened at Charlotte Pike with the discounts? | explanation | The memo: one advisor, six months, 22 % against 3 %, 14 voids, 19 short days, $11,400 as the outside figure, the true loss not in the data | ready |
| KB.P5.1 | Maya Torres (6, junior, main) | What are Nickajack's terms, and what must be on every order? | value | 30 days from the statement, company rate, its purchase-order number before work starts | ready |
| KB.P5.2 | Josh Tipton (17, junior, east) | A Millsaps driver says go ahead with $380 of extra work | value | No: a driver approves up to $300 for the visit; call Tina Ragsdale, who approves up to $1,000 a vehicle (Hal Millsaps above that) | ready |
| KB.P5.3 | Maya Torres (6, junior, main) | A Nickajack driver approves $380 of found work | value | No: the limit is $300 for the visit; call Lonnie Coffey | ready |
| KB.P5.4 | Greg Whitaker (4, senior, main) | Is the rule in the note "a company driver cannot approve work over 300 USD; call the fleet contact" already written down? | value | Yes, on the Company accounts page: up to $300 for the whole visit, above that the fleet contact. The note repeats the page | ready |
| KB.P5.5 | Maya Torres (6, junior, main) | Who approves work for Sourwood Catering? | value | Erin Castillo (terms table, reviewed `T-2mo`). The account's own page still names Bobby Shadden and an advisor who left: both out of date | ready |
| KB.P5.6 | Travis Burnette (5, middle, main) | What does Nickajack pay for a PM service A? | value | $243.53 before supplies and tax: 1.5 h at $121.50 plus oil and filter less 10 % | ready |
| KB.P5.7a | Maya Torres (6, junior, main) | What is Nickajack's credit limit? | refusal | Not available to her. | ready |
| KB.P5.7b | Donna Ledford (3, middle, main) | What is Nickajack's credit limit? | value | $30,000 | ready |
| KB.P5.8 | Angie Holloway (16, middle, east) | Which accounts come first, and when? | value | Any company vehicle that cannot work is seen the day it arrives; Millsaps has Monday 7:30 at Bonny Oaks for five vans and comes first on Monday mornings | ready |
| KB.P6.1 | a customer (the website assistant) | Are you open on the afternoon of the stocktake day? | value | No: all three shops close at noon; open from 7:30; pick up before noon or next morning; the key drop stays open | ready |
| KB.P6.2 | Caleb Sutton (7, junior, main) | What do I do with bookings that day? | value | Nothing after 10:30, nothing over two hours; everyone counts from noon | ready |
| KB.P6.3 | Jasmine Bolden (24, junior, west) | Is Charlotte Pike open on Saturdays? | value | No, Monday to Friday. The shop's own page says Saturday 8 to 12 and is thirteen months old | ready |
| KB.P6.4 | a customer (the website assistant) | Which holidays are you closed? | list | New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Christmas Day; on the nearest weekday when one falls on a weekend | ready |
| KB.P6.5 | Claire Brennan (2, admin) | Who added the stocktake notice, and was it in time? | value | Greg Whitaker, on the Monday of the week before last; the stocktake page asks for two weeks and this is seventeen days | ready |
| KB.P7.1 | Maya Torres (6, junior, main) | Why was my note about reading the booking back declined? | value | The page "Booking a visit" already says it (step 6); Greg Whitaker's reason says to propose the wording there | ready |
| KB.P7.2 | Maya Torres (6, junior, main) | Where does a habit the whole team should follow belong? | value | On a page; a personal note is for how the assistant works with you; customer and price facts are never notes | ready |
| KB.P8.1 | a customer (the website assistant) | My brakes are grinding. What is it and what will it cost? | value | Pads worn through; come now; inspection $49.95, about half an hour; front pads and discs on a typical car $428.00 to $523.76 before tax, confirmed after inspection | ready |
| KB.P8.2 | a customer (the website assistant) | Can you book me for Thursday at nine? | action | It cannot book; it hands the conversation to an advisor | ready |
| KB.P8.3 | a customer (the website assistant) | What do you charge companies per hour? | refusal | Not on a public page; call Greg Whitaker on (423) 555-0142. It must not give $121.50 | ready |
| KB.P8.4 | a customer (the website assistant) | Do you have loaner cars? | cannot tell | The pages do not say; there is a free shuttle at the two Chattanooga shops | ready |
| KB.P8.5 | Maya Torres (6, junior, main) | What do I answer her about the rear shocks? | value | Replace rear shock absorbers (pair): $339.28 standard ($297.00 economy, $362.00 premium), 1.2 hours, no alignment needed; plus free times from the schedule | ready |
| KB.C1.1 | Maya Torres (6, junior, main) | What is the till float at Bonny Oaks? | value | $150 (East Main is $200) | ready |
| KB.C1.2 | Josh Tipton (17, junior, east) | Where does the deposit bag go at closing at Bonny Oaks? | value | The drop safe under the counter; the parts manager takes it to East Main on the 1:00 run | ready |
| KB.C1.3 | Maya Torres (6, junior, main) | Where is the key drop box at Bonny Oaks? | value | Left of the office door (East Main: right) | ready |
| KB.C1.4 | Jasmine Bolden (24, junior, west) | Who counts the till at Charlotte Pike? | value | Two people, both initial; since `@discount_rule` | ready |
| KB.C1.5 | Caleb Sutton (7, junior, main) | How much is a transmission flush? | value | It names two jobs and asks which: drain and fill $191.98, machine exchange $386.94 | ready |
| KB.C2.1 | Caleb Sutton (7, junior, main) | How much longer do spark plugs take on a V6 SUV? | value | Labour times 2.4 | ready |
| KB.C2.2 | Josh Tipton (17, junior, east) | Who approves work on a driving-school car above $500? | value | Denise Atchley, the owner; Rob Atchley up to $500 | ready |
| KB.C2.3 | Chad Binkley (23, junior, west) | How fast must a missed call be returned? | value | Within one hour, the same day without exception | ready |
| KB.C2.4 | Josh Tipton (17, junior, east) | What are the tire fees? | value | $3.50 disposal and $1.35 state fee a tire, $19.40 for four | ready |
| KB.C2.5 | Greg Whitaker (4, senior, main) | What happens when a technician is over 4 % comebacks two months running? | value | The foreman checks every brake, steering and suspension job of his for a month | ready |
| KB.C3.1 | Travis Burnette (5, middle, main) | Front pads and rotors on a van? | value | $640.91 standard, before supplies and tax | ready |
| KB.C3.2a | Josh Tipton (17, junior, east) | How many paid days off after two years? | value | 10 days. | ready |
| KB.C3.2b | Cody Gann (15, worker, main) | How many paid days off after two years? | refusal | Not in what he can read; the binder in the break room, or the office | ready |
| KB.C3.3 | Caleb Sutton (7, junior, main) | What are the three sentences Angie never says? | list | "No problem." "It should be ready." "It is all warrantied." | ready |
| KB.C3.4 | Marcus Gaines (9, junior, main) | How much oil does a Transit-250 with the 3.7 take? | value | 6.0 quarts of 5W-20 | pending |
| KB.C3.5 | Marcus Gaines (9, junior, main) | Oil quantity for the driving school's Sentra? | cannot tell | Not in the printed sheet; the spreadsheet may have it and cannot be read | ready |
| KB.C3.6 | Greg Whitaker (4, senior, main) | How many late arrivals before a written warning? | value | Five in any 30 days; three bring a conversation | ready |
| KB.C4.1 | Caleb Sutton (7, junior, main) | A technician marks rear shocks Bad. What happens before work starts? | explanation | Measurement and photo, a catalogue job on the line; the advisor puts it on the estimate at the standard tier from the price list, after the job the customer came for; sends it the same day; calls within 30 minutes; records the yes per job with who, how and when | ready |
| KB.C4.2 | Josh Tipton (17, junior, east) | How long do I wait for an answer to an estimate? | value | With a Bad item: call within 30 minutes. Otherwise two hours, then 4:00, then the next morning, three tries | ready |
| KB.C4.3 | Caleb Sutton (7, junior, main) | Do Watch items go on the estimate? | value | No: in the notes with the measurement, unless they share labour with a Bad item | ready |
| KB.C4.4 | Hunter Varnell (14, worker, main) | Can the technician tell the customer the price? | value | No. He records and photographs; the advisor prices. The worker cannot open the estimate page the inspection page links to | ready |
| KB.C5.1 | Chad Binkley (23, junior, west) | When do we start charging storage on a car nobody collects? | value | From the sixth working day, $25 a day. A team note says day three; the policy page is the company rule; the note should be reviewed | ready |
| KB.C5.2 | Greg Whitaker (4, senior, main) | Which is right, and who fixes it? | explanation | The page (managing owner, in force `T-9mo`). The note was approved at Charlotte Pike and is the old habit there; a senior reviews or retires it | ready |
| KB.C5.3 | Claire Brennan (2, admin) | Is there a team note that agrees with its policy page? | value | Yes: discounts over 10 % | ready |
| KB.C6.1 | Caleb Sutton (7, junior, main) | A customer wants a tune-up on a 2015 Camry | value | Spark plugs, $222.28, and filters after a look; if a light is on, diagnosis first | ready |
| KB.C6.2 | Josh Tipton (17, junior, east) | Recharge the freon on a 2019 CR-V at Bonny Oaks today? | value | It takes R-1234yf: $278.80, after a $49.95 check; that refrigerant is kept at East Main only, so the car goes there or waits for the 1:00 run | ready |
| KB.C6.3 | Chad Binkley (23, junior, west) | Front end alignment on an F-150? | value | Four-wheel alignment, $137.94 for a truck | ready |
| KB.C6.4 | Caleb Sutton (7, junior, main) | How much is a fan belt? | value | The serpentine belt: $124.18. Not the timing belt | ready |
| KB.C6.5 | Maya Torres (6, junior, main) | A customer says it shakes when braking | value | Rotors, most likely: a brake inspection, $49.95; not a wheel balance | ready |
| KB.C7.1 | Caleb Sutton (7, junior, main) | A customer brings his own alternator for a Camry | value | We fit it: 1.6 hours, $216.00 labour plus $10.80 supplies; no warranty on the part or the labour; labour again if it is wrong | ready |
| KB.C7.2 | Josh Tipton (17, junior, east) | Deposit and total for a transmission rebuild? | value | Deposit $1,700.00; total $4,412.50 before supplies and tax; five working days | ready |
| KB.C7.3 | Maya Torres (6, junior, main) | Both outer tie rods and the alignment on a Camry? | value | $445.05 before supplies and tax: two at $162.55 and one alignment at $119.95 | ready |
| KB.C7.4 | Travis Burnette (5, middle, main) | Towed 14 miles to East Main, then front pads and rotors, standard: the bill before tax? | value | $616.15: tow $111.00, job $493.00, supplies $12.15 | ready |
| KB.C7.5 | Maya Torres (6, junior, main) | What does a 60K service come to on a Camry? | value | Labour $243.00 plus oil service, both filters, rotation and brake fluid: $627.45, supplies $22.28; transmission fluid $191.98 more if due | ready |
| KB.C7.6 | Maya Torres (6, junior, main) | What warranty does a Nickajack van get on a brake job? | value | 12 months or 12,000 miles: business use | ready |
| KB.C7.7 | Travis Burnette (5, middle, main) | A/C compressor on a 2019 car? | value | $1,248.26: the list's $1,176.86 plus the $71.40 between the two recharges | ready |
| KB.C8.1 | Josh Tipton (17, junior, east) | How long is a rebuilt transmission warrantied? | cannot tell | Not stated: it is the specialist's warranty, on the card that returns with the unit; ask Greg Whitaker | ready |
| KB.C8.2 | Jasmine Bolden (24, junior, west) | Who tows for us in Nashville? | cannot tell | Not stated; the Charlotte Pike page links to a page that does not exist | ready |
| KB.C8.3 | Caleb Sutton (7, junior, main) | What do we charge to program a key? | cannot tell | No price: it is named among the jobs not on the list; ask the lead advisor | ready |
| KB.C8.4 | a customer (the website assistant) | Do we do emissions tests? | cannot tell | The pages do not say | ready |
| KB.C8.5 | Greg Whitaker (4, senior, main) | What is a line technician paid an hour? | cannot tell | Nowhere: only how each job is paid | ready |
| KB.C8.6 | Josh Tipton (17, junior, east) | Who holds the A/C certificate at Bonny Oaks? | cannot tell | Not named | ready |
| KB.C8.7 | Caleb Sutton (7, junior, main) | Price of a catalytic converter? | cannot tell | No list price: diagnosis, then a one-off estimate | ready |
| KB.C9.1 | Josh Tipton (17, junior, east) | What is a wheel bearing, standard? | value | $420.27 a side | ready |
| KB.C9.2 | Travis Burnette (5, middle, main) | Every transmission job and its standard price | list | Drain and fill $191.98; exchange $386.94; gear oil $169.50; clutch $1,227.91; CV axle $379.64; rebuild $4,412.50 | ready |
| KB.C10.1 | Claire Brennan (2, admin) | What does the Charlotte Pike page link to that is missing? | value | "Tow trucks we use" | ready |
| KB.C11.1 | Angie Holloway (16, middle, east) | How many cars does the driving school have? | value | The page says seven and is six months old; the shop system has eight | ready |
| KB.C11.2 | Claire Brennan (2, admin) | Who works the counter at Charlotte Pike? | list | Chad Binkley and Jasmine Bolden; the shop's own page names an advisor who left five months ago | ready |
| KB.C11.3 | Claire Brennan (2, admin) | Are we meeting our call-back standard at each shop? | value | Standard one hour: East Main about 40 minutes, Bonny Oaks 45, Charlotte Pike four and a half hours | ready |
| KB.C11.4 | Greg Whitaker (4, senior, main) | Does the knowledge base know Cumberland Bend left? | value | No: its page is thirteen months old and says nothing; the data shows no visit for four and a half months | ready |
| KB.C11.5 | Claire Brennan (2, admin) | What does our own material say about why Sourwood is fading? | explanation | Its page names a contact who left Sourwood and an advisor who left us; nobody rewrote it; the estimate standard (four working hours) was missed | ready |
| KB.C12.1 | Cody Gann (15, worker, main) | How many vacation days do I get? | refusal | Not in what he may read: the binder, or the office | ready |
| KB.C12.2 | Maya Torres (6, junior, main) | What margin do we make on parts? | refusal | Not available at her rank | ready |
| KB.C12.3 | Dale Hutchins (22, senior, west) | What is the plan for my shop? | refusal | Nothing found: the plan is the administrator's | ready |
| KB.C12.4 | Travis Burnette (5, middle, main) | Sourwood's credit limit? | value | $7,500 | ready |
| KB.C12.5 | Maya Torres (6, junior, main) | Show me the advisor playbook | refusal | Not available; the counter pages cover it | ready |
| KB.C12.6 | a customer (the website assistant) | Do your advisors give discounts? | value | Only what the public pages say: no discount for cash | ready |
| KB.C12.7 | Maya Torres (6, junior, main) | What does the "Pay and till" page say? | refusal | Refused by rank: she cannot open it and the answer does not quote it (story question S12.5) | ready |
| KB.O1 | Travis Burnette (5, middle, main) | Fix the brake questions page: put in today's prices | action | A card showing the seven figures changed, his reason; on confirm, a proposal; the deciders are told | ready |
| KB.O2 | Maya Torres (6, junior, main) | Fix the brake questions page: put in today's prices | refusal | A card with no confirm: a lead advisor can propose it, a manager can publish it | ready |
| KB.O3 | Greg Whitaker (4, senior, main) | Put Erin Castillo on Sourwood's page and take Brad off | action | A card in publish mode; on confirm, a revision by him | ready |
| KB.O4 | a customer (the website assistant) | Change your opening hours page | refusal | Refused: staff only | ready |
| KB.O5 | Claire Brennan (2, admin) | Take the old warranty page down | action | The assistant can suggest text, not delete: it offers to mark the page superseded at the top, or she deletes it on the page | ready |
| KB.O6 | Claire Brennan (2, admin) | What changed on the discount policy since it was written? | value | One edit, by Greg Whitaker: the before-tax line | ready |
| KB.O7 | Claire Brennan (2, admin) | What changed on Charlotte Pike's opening and closing page, who did it and why? | explanation | Claire Brennan replaced one count and banking twice a week with two counts and daily banking; "Two counts, every day." | ready |
| KB.O8 | Angie Holloway (16, middle, east) | What changed on the pads and rotors page at the price rise? | value | Her own proposal, approved by Greg Whitaker: the labour-dependent figures, for example $475.00 to $493.00 | ready |
| KB.O9 | Claire Brennan (2, admin) | Who came off Who is who in the last six months, and who went on? | list | Off: Brent Lassiter, Wes Tate. On: Caleb Sutton, Hunter Varnell (Jasmine Bolden started ten months before T and came with the import) | ready |
| KB.O10 | Claire Brennan (2, admin) | Which pages were changed because of the timing belt complaint? | list | The root README, the price list, "How prices change" (new), discounts, complaints, writing an estimate, using the knowledge base, the owner playbook | ready |
| KB.O11 | Greg Whitaker (4, senior, main) | What is waiting for a decision? | smoke | One proposal: Travis Burnette's correction to the timing belt page | ready |
| KB.O12 | Claire Brennan (2, admin) | Find pages that contradict each other | list | At least: "Our warranty" against "Warranty policy", both public; price list against the two stale pages; terms table against Sourwood's page; Who is who and the hours page against Charlotte Pike's page; the public tires page ("next morning") against the suppliers page (Nashville twice a week); the timing belt page's same-day line against the ordering page | ready |
| KB.O13 | Greg Whitaker (4, senior, main) | Which page has nobody keeping it? | value | The brake questions page: signed BK, an advisor who left; no index links to it | ready |
| KB.O14 | Travis Burnette (5, middle, main) | Which pages link to the price list? | list | Ten pages, more than link to any other page: the README, the services index, the rates page, "How prices change", the estimate and chat pages, the new-advisor page and three more | ready |
| KB.O15 | Angie Holloway (16, middle, east) | A customer was told tires arrive next morning in Nashville. Propose the fix | action | A proposal on `customers/tires.md` adding that Nashville deliveries are Tuesday and Friday | ready |

## Calls

The file words no question; section 4 names one without wording it ("that difference is planted, counted and an eval question in itself").

## Conversations

The file words no question.

## Working day

| id | Asked by | Question | Kind | Expected answer | Status |
|---|---|---|---|---|---|
| WD.01 | Greg Whitaker (4, senior, main) | Who has not clocked in for a shift that has started? | value | Tyler Jarrell at Charlotte Pike, whose shift started at {w1_shift_start}. Nobody else. | ready |
| WD.02 | Greg Whitaker (4, senior, main) | Which weeks of the roster are not published yet? | list | At East Main and Bonny Oaks the week after next is a draft; at Charlotte Pike next week is. | ready |
| WD.03 | Claire Brennan (2, admin) | When does Charlotte Pike publish its roster? | explanation | On the Sunday evening before the week, every week; the home shops publish on the Thursday before, before noon. The standard is Thursday 12:00. | ready |
| WD.04 | Greg Whitaker (4, senior, main) | What did Cody ask for, and what was decided? | value | 4 requests: three changes of hours, two approved and one declined with Greg Whitaker's note, and one day off he took back himself. | ready |
| WD.05 | Claire Brennan (2, admin) | Which shift requests at Charlotte Pike were never answered? | list | Six: two of Chad Binkley's, one of Jasmine Bolden's, one of Shane Maddox's and two of Tyler Jarrell's, with their days ({w5_requests}). | ready |
| WD.06 | Luis Herrera (12, worker, main) | Show me Dustin's shift requests. | refusal | Refused by rank; his own can be shown. | ready |
| WD.07 | Dale Hutchins (22, senior, west) | Was Shane late on the days he clocked in from outside the site? | value | No: both times he was on time, 600 metres away. | ready |
| WD.08 | Maya Torres (6, junior, main) | What is on my board? | list | 6: the review, high priority; 2 due today; three more. None overdue. | ready |
| WD.09 | Greg Whitaker (4, senior, main) | Which cards have gone quiet? | list | Two: his alignment-rack card and Dale Hutchins's regulars list. | ready |
| WD.10 | Maya Torres (6, junior, main) | Is any customer waiting for a person at my shop? | nothing | None. | ready |
| WD.11 | Greg Whitaker (4, senior, main) | Is any customer waiting for a person? | value | One, at Bonny Oaks, waiting since {w11_since}. | ready |
| WD.12 | Maya Torres (6, junior, main) | Give Donna a task: the days-to-pay table by Monday. | refusal | Refused: a junior may not put work on a middle. It can offer a comment on the review card. | ready |
| WD.13 | Claire Brennan (2, admin) | How did Dale do with the tasks I gave him? | value | 12: 6 closed on time, 3 late, 3 open and overdue. | ready |
| WD.14 | Marcus Gaines (9, junior, main) | Did anyone decline the stocktake? | nothing | Nobody. | ready |
| WD.15 | Greg Whitaker (4, senior, main) | What needs me? | list | Nine lines in the tray's order, the hand-over first ({w15_lines}). | ready |
| WD.16 | Greg Whitaker (4, senior, main) | Is any card of mine overdue? | nothing | None. | ready |
| WD.17 | Angie Holloway (16, middle, east) | Who covered Austin's shift? | value | Jordan Akins, on a shift of his own published that morning, {p20_no_show_day = 2026-11-11}; Austin Crabtree's shift has no punch. | ready |

## Assistant

| id | Asked by | Question | Kind | Expected answer | Status |
|---|---|---|---|---|---|
| AS.01 | Maya Torres (6, junior, main) | Which notes do you keep about how I work? | list | Her 6, by subject: Reply drafts, Answer length, Prices source, Default shop, Call summaries, Money and dates. | ready |
| AS.02 | Maya Torres (6, junior, main) | Where did my note about prices come from? | value | From her chat “Front pads and rotors, Camry” of {a2_chat_day}, after an answer quoted the page “Brake questions”. | ready |
| AS.03 | Caleb Sutton (7, junior, main) | What notes do you keep about Maya? | refusal | Refused: a personal note is its owner's. | ready |
| AS.04 | Claire Brennan (2, admin) | What notes do you keep about Maya? | refusal | Refused in Ask; the console's Memory view shows them and counts the read. | ready |
| AS.05a | Maya Torres (6, junior, main) | Which team notes can I see? | list | 11 ({a5_notes}). She does not see “Money in answers”, “Declined work” or “Desks, not people”. | pending |
| AS.05b | Travis Burnette (5, middle, main) | Which team notes can I see? | list | 13 ({a5_notes}). | pending |
| AS.05c | Greg Whitaker (4, senior, main) | Which team notes can I see? | list | All 14 ({a5_notes}). | pending |
| AS.06 | Greg Whitaker (4, senior, main) | Which three advisors hold the note about price sources? | cannot tell | The data cannot tell him: the proposal carries a count of three and no names. | ready |
| AS.07 | Dale Hutchins (22, senior, west) | What waits for my decision in Memory? | list | Two proposals, company drivers and price sources, and one team note to check, “Missed callers”. | ready |
| AS.08 | Claire Brennan (2, admin) | Why was Jasmine's note about answering the phone declined? | value | Dale Hutchins declined it the day it was proposed, {a8_day}: “Folks here know who they called. Not needed.” | pending |
| AS.09 | Travis Burnette (5, middle, main) | Do I have a team note waiting for a decision? | nothing | None. | ready |
| AS.10 | Greg Whitaker (4, senior, main) | What did my note “The shop” say before I changed it? | value | “'The shop' means East Main”, replaced on {a10_day}. | ready |
| AS.11 | Claire Brennan (2, admin) | Which of my notes have gone unused? | value | One: “Tables as files”, unused for over ninety days and still recallable. | ready |
| AS.12 | Claire Brennan (2, admin) | How often did the Friday list show a discount nobody approved? | value | Twice, on the Fridays of {a12_fridays}: Chad Binkley, 12 % each. | ready |
| AS.13 | Maya Torres (6, junior, main) | What did Greg's brief say this morning? | refusal | Refused: she reads her own. | ready |
| AS.14 | Ray Brennan (1, senior) | Why did I get no second brief today? | value | It was skipped ({a14_skipped_run}): the brief before it had not been opened. | ready |
| AS.15 | Greg Whitaker (4, senior, main) | Did all of Claire's reports run last week? | refusal | Refused: he reads his own, “Tomorrow's gaps in cover”. | ready |
| AS.16 | Greg Whitaker (4, senior, main) | Is there a team rule about promising a pickup day, and was it kept? | explanation | Yes, the team note “Parts promises”, approved on {a16_approved_day}; it was broken twice, by Caleb Sutton's same-day promise and by the day Chad Binkley promised. | pending |
