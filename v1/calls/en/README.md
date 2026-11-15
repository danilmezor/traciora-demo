# Story calls, English configuration

The hand-written calls of `../DESIGN.md` section 6: 33 with text and the three misses of account A5. One JSON file per call, `NN-<story>-<short-name>.json`, in the format of section 7 and of `../samples/`. Check: `python3 ../../checks/check_calls.py en` (output: `../../checks/calls_check_en.txt`).

## The calls

Score is the verdict on the stored lines. "No score" is the rubric's: an existing-job call has two checks, an outbound call is not judged.

| # | Story | Advisor (slot) | Score | What it shows |
|---|---|---|---:|---|
| 1 | S4 | Maya Torres (6) | 40.0 | P1: a price given, the caller let go (sample 1) |
| 2 | S4 | Maya Torres (6) | 53.3 | P2: she asks when would suit; "I work till six" gets no time, "I'll call you back" gets "no problem" |
| 3 | S4 | Maya Torres (6) | 63.6 | P3: the caller names the time himself; booked with no name, ends on "see you then" |
| 4 | S4 | Maya Torres (6) | 68.8 | P4: one time, the booking, a summary without the address; a doubt soothed, not answered |
| 5 | S4 | Maya Torres (6) | 92.9 | P5: two times before the price, a full summary; nobody pushes back |
| 6 | S4 | Maya Torres (6) | 71.9 | P6: booked, a doubt stepped over (sample 2) |
| 7 | S4 | Maya Torres (6) | 94.4 | a company driver approves 379.64 of found work, over the 300 limit; nothing on the scorecard is wrong |
| 8 | S7 | Maya Torres (6) | no score | outbound: she confirms the web-chat customer's booking |
| 9 | S8 | Caleb Sutton (7) | 31.2 | the timing belt at 688 against 720 and "back the same day"; `wrong_promise`; the customer books |
| 10 | S8 | Travis Burnette (5) | no score | the complaint: he owns the mistake, explains the bill, promises the senior's call and sums up; kept |
| 11 | S8 | Greg Whitaker (4) | no score | outbound: 80 dollars off, 722.80 out the door |
| 12 | S12 | Caleb Sutton (7) | 40.0 | front brakes at 475 from the stale page against 493; `wrong_promise`; the caller does not book |
| 13 | people | Caleb Sutton (7) | 34.6 | his first weeks: a hold to find the price, "just bring it by" |
| 14 | people | Caleb Sutton (7) | 56.2 | three months in: the price from the price list, one time, booked; still asks nothing, steps over a doubt |
| 15 | S6 | Chad Binkley (23) | 25.0 | a day promised with nothing behind it, added work not taken; `wrong_promise` (sample 3) |
| 16 | S6 | Chad Binkley (23) | no score | "the other thing": he does not ask what; left unclear (design rule R13); `dropped_customer` |
| 17 | S1 | Dale Hutchins (22) | no score | A5's manager on two brake comebacks and the bill; a call back promised and never made |
| 18 to 20 | S1 | first desks 302, 303, 302 | none | A5's three unanswered calls, 1, 6 and 9 days later; waiting |
| 21 | S1 | Travis Burnette (5) | 75.0 | A6's new contact: "the usual on the white van", two questions to find the van and the job; the price doubt gets "everything's gone up" (rule R13, resolved) |
| 22 | S1 | Caleb Sutton (7) | 46.4 | A6: a quote promised "today", sent two days late; `callback_not_kept` from the call log |
| 23 | S1 | Maya Torres (6) | 60.0 | A1's van booked without its purchase-order number |
| 24 | S1 | Maya Torres (6) | 80.0 | the same account three months on: the number asked for first |
| 25 | S5, S1 | Angie Holloway (16) | 83.3 | A2's van; a model call that recognition damaged: 100 on the speech (sample 4) |
| 26 | S5 | Angie Holloway (16) | 93.8 | a lower quote from another shop, found out and answered |
| 27 | S5 | Angie Holloway (16) | 100.0 | a regular asks for her; she has the note from the last visit |
| 28 | S5 | Josh Tipton (17) | 53.8 | her day off: "is Angie in?"; each thing done half, the customer will call her |
| 29 | people | Travis Burnette (5) | no score | slot 11's rushed work: a control arm and no alignment; rechecked the same day |
| 30 | people | Maya Torres (6) | no score | slot 11's rushed work: a customer on the hard shoulder, angry; the one heavily damaged recording |
| 31 | S3 | Travis Burnette (5) | 81.2 | before the fix: "I have called y'all three times this morning"; `repeat_caller` |
| 32 | S3 | Maya Torres (6) | 82.1 | since the fix: answered on the first ring at 07:40 |
| 33 | people | Dale Hutchins (22) | 44.4 | first-name terms, a good question, "whenever, I'm here" |
| 34 | people | Dale Hutchins (22) | 50.0 | no price over the phone, "whenever you get here" |
| 35 | people | Jasmine Bolden (24) | 60.0 | the bright spot, early: a careful intake and a caller let go |
| 36 | people | Jasmine Bolden (24) | 82.1 | four months on: two times with the price, booked and repeated |

## How the files were made

- **Verdicts are derived, not typed.** Each `verdict` is what the product's `judge.verdict` makes of the file's `judge_answer` and stored lines (imported read-only), as in the samples. `check_calls.py en --product <repository>` derives all 31 again.
- **Prices** are `catalogue.json`'s for the car's class, the parts tier and the price class at the labour hour in force on the call's day, with today's parts, as the samples and cards S07, S08 and S12 have them. The catalogue's parts drift of 3 % a year is not applied (it would move the earliest call's prices by under 1 %). Each file states its figures in `scenario.facts.prices`.
- **Recognition** follows `../DESIGN.md` section 4. Each file's `recognition.counts` holds what the set's rates are read on: hesitations and fillers said and dropped, mentions and errors of names, plates, order numbers, trade words, numbers and phones, overlaps, noise bursts, swapped turns. Profiles: 27 light, 5 marked (14, 17, 25, 31, 33), 1 heavy (30); `asr_quality` poor in 17, 25 and 30.
- **The four samples** are calls 1, 6, 15 and 25, copied with two corrections listed in each file's `brought_into_line`: in call 1 the script still spelled out the caller's old number; in call 6 the coaching line priced the hub at 210 where the catalogue has 177.27.
- Files beyond the samples' keys: `number`, `story`, `recognition.counts`, `scenario.facts.prices`, `scenario.unclear` (calls 16 and 21), `call_log` (what the call log adds: a call back kept or not, an earlier miss), `day_report` (calls without a score), `new_facts`.

## New facts other stores must carry

Each file lists its own under `new_facts`. Collected:

**Callers the seed files do not have.** First-time callers with no order: Sharon Kessler (1), Tonya Hensley (2), Vernon Lowery (12), Earl Blevins (13, a 706 number), Brianna Gentry (35). First-time callers with an appointment: Dwight Sizemore (3, booked without a name), Carla Jenkins (4), Stephanie Vandergriff (5), Wendell Boyd (6), Kayla Thornton (14), Gerald Massengill (26), Tamika Ellison (31), Jared Scruggs (32). Customers with a history: Carolyn Bivens and Roy Standifer at `east` (27, 28), Phil Cantrell and Tasha Underwood at `main` (29, 30), Harlan Pewitt, Peggy Womack with her son Jeff, and Keisha Abernathy at `west` (33, 34, 36). Their numbers, cars and bookings are in the files.

**Company accounts.**
- A3: a driver, Ronnie Eaves, mobile 423-555-0116, unit MB-6; an order on slot 6's 2nd working day before T with an oil service and a CV axle (379.64) added on his word; the fleet contact was not called (7).
- A5: the first comeback is unit E-2, the second E-6, each about three weeks after its pad job, both redone free; the disputed line is E-6's pad job (17). The three misses at 08:05, 13:40 and 16:15 Central (18 to 20).
- A6: an appointment for SC-2 on the Thursday of week T-20, PM service at list (21); an estimate for SC-4 and SC-5 opened on the Tuesday of week T-9 and sent two days later (22); the account kept the former contact's e-mail. Several of its vans are white.
- A1: an order for ND-22 on the Thursday of week T-17 with no purchase-order number (23); purchase order ND-60418 on an order for ND-08 on the Friday of week T-4 (24).
- A2: a driver called Darnell, purchase order 4471B, unit M-112 white with front struts fitted earlier (25, as in the sample).

**Story S8.** The appointment at 688.00 for slot 7's 4th working day before T at 08:00 (9). The car went on the lift after lunch that day; the customer left without paying when it was ready and the car stayed overnight; slot 4 was at `east` that day (10). Slot 4 listened to call 9, and the customer paid 722.80 the afternoon of call 11 (11).

**Slot 11's two complaints.** A control-arm order on the Tuesday of week T-10 with no alignment, and its comeback on the Friday (29). A water-pump order on the Friday of week T-3 (659.37 with tax), a tow by vendor V8 and a comeback that evening for a loose hose clamp (30).

**Calls around the story calls.** An outbound "car ready" call to A3's driver at 15:52 (7). Slot 4's call back is call 11 (10). Two outbound calls after call 30, at 16:46 from desk 102 and 17:05 from desk 104. Three misses at `main` at 07:34, 07:46 and 07:58 before call 31, first desk 101, all `got_through`. The miss before call 16 at 09:12 Central, first desk 302.

**The shop.** The hold message: "Thank you for holding. Someone will be right with you." (28). The bookkeeper has told the desk not to open A1 orders without a purchase-order number (24).

## Where a call and a card or the rubric do not meet

- **Call 9's score.** 10 of 32 points is 31.25; the product rounds a score to one decimal, so the stored score is 31.2, the ledger's `s8.quote_call_score`.
- **His first wrong price.** Call 12 (the Tuesday of week T-5) is slot 7's first wrong price and call 9 (his 5th working day before T, a month later) his second, as the cards and `TIMELINE.md` say.
- **Call 16** ends with the customer's question unanswered and carries the auto-fail `dropped_customer` (card S06).
- **Calls 33 and 34** take the summary as not applicable (a step with no day). A judge that scores it 0 gives 40.0 and 45.8, still inside their bands (38 to 48, 44 to 54).
- **Conversations sample `en-2-fleet-quote-waited`** was written before card S01 and holds call 22 inside a messenger thread about other vans. Call 22 here follows the card.
