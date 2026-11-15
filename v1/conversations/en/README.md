# Story conversations, English configuration (Brennan Auto Care)

The 27 hand-written conversations of `../DESIGN.md` section 6, one JSON file each, format `seed-conversation/1` (section 7). These files are the source of record; `../samples/` holds copies of five of them. `../../checks/check_conversations.py en` checks all of it and its output is `../../checks/conversations_check_en.txt`.

Read first: **03** (the live-demo chat: a draft waits for the junior operator), **06** (the car that has waited nine days: three late replies, a note, 'handled') and **04** beside **05** (the fading account's quote that waited two days; the healthy account's weekly list answered in six minutes).

## The conversations

| # | File | Story | Channel | Staff (slot) | Begins | State at T | Shows |
|---|---|---|---|---|---|---|---|
| 01 | `01-s7-web-after-hours.json` | S7 | web chat | Maya Torres (6) | 1 calendar day before slot 6's 14th working day before T (Sun 2026-10-25) | resolved by slot 6 | Website chat on a Sunday night: a noise, one question, the assistant hands over, the junior operator next morning |
| 02 | `02-s7-web-approval-and-thanks.json` | S7 | web chat | Maya Torres (6) | slot 6's 13th working day before T (Tue 2026-10-27) | resolved by slot 6 | The day of the visit: she approves the brakes and declines the shock absorbers in the website chat; her thanks the next morning |
| 03 | `03-s7-web-return-draft-waiting.json` | S7 | web chat | Maya Torres (6) | slot 6's last working day before T (Thu 2026-11-12) | open, slot 6, **draft waiting** | She comes back for the shock absorbers: the assistant prices and hands over, the junior operator takes the chat; at T her answer is unread and a draft waits |
| 04 | `04-s1-web-fleet-quote-waited.json` | S1 | web chat | Travis Burnette (5), Caleb Sutton (7) | the Tuesday of week T-4 (Tue 2026-10-13) | resolved by 7 silent days | The fading account's new fleet contact asks for a quote in the website chat; two days to a person's first reply |
| 05 | `05-s1-telegram-weekly-vans.json` | S1 | Telegram | Angie Holloway (16) | the Thursday of week T-23 (Thu 2026-06-04) | open, slot 16 | The healthy account: the dispatcher's Monday list, every week, in one Telegram conversation |
| 06 | `06-s6-web-west-nine-days.json` | S6 | web chat | Chad Binkley (23), Jasmine Bolden (24), Dale Hutchins (22) | 7 calendar days before T (Fri 2026-11-06) | open, slot 23, **draft waiting** | Nashville: the car that has waited nine days; its owner writes for the fourth time |
| 07 | `07-s13-web-stocktake-question.json` | S13 | web chat | the assistant alone | the Monday of week W0 (Mon 2026-11-09) | pending, the assistant's | The stocktake afternoon, asked on the website: the assistant answers alone |
| 08 | `08-s13-telegram-stocktake-regular.json` | S13 | Telegram | Angie Holloway (16) | slot 16's last working day before T (Thu 2026-11-12) | resolved by slot 16 | The stocktake afternoon, asked on Telegram: the assistant drafts and the advisor edits and sends |
| 09 | `09-people-p05-telegram-out-the-door.json` | people | Telegram | Travis Burnette (5) | the Thursday of week T-18 (Thu 2026-07-09) | resolved by 7 silent days | The lead advisor at the flagship on Telegram: is the truck done, and why is the number bigger |
| 10 | `10-people-p05-web-puddle-photo.json` | people | web chat | Travis Burnette (5) | the Monday of week T-8 (Mon 2026-09-14) | resolved by slot 5 | A photo instead of words: a puddle under the car, the assistant, and the lead advisor's comparison |
| 11 | `11-people-p06-telegram-found-work.json` | people | Telegram | Maya Torres (6) | the Tuesday of week T-11 (Tue 2026-08-25) | resolved by slot 6 | The junior operator on Telegram: found work, two photos, a yes and a no |
| 12 | `12-people-p06-web-moved-booking.json` | people | web chat | Maya Torres (6) | the Friday of week T-5 (Fri 2026-10-09) | resolved by slot 6 | A booking moved, and a price doubt the junior operator steps over |
| 13 | `13-people-p07-telegram-first-of-two.json` | people | Telegram | Caleb Sutton (7) | the Thursday of week T-12 (Thu 2026-08-20) | resolved by slot 7 | The newcomer on Telegram: two questions in one message, and he answers the first |
| 14 | `14-people-p07-web-sends-what-he-is-given.json` | people | web chat | Caleb Sutton (7) | the Tuesday of week T-3 (Tue 2026-10-20) | resolved by slot 7 | The newcomer takes a hand-over: 'should', and a draft that sends the customer back to him |
| 15 | `15-people-p16-telegram-brake-squeal.json` | people | Telegram | Angie Holloway (16) | the Wednesday of week T-15 (Wed 2026-07-29) | resolved by slot 16 | A complaint to the all-star: brakes that squeal a week after the job |
| 16 | `16-people-p16-web-pre-purchase.json` | people | web chat | Angie Holloway (16) | the Monday of week T-7 (Mon 2026-09-21) | resolved by slot 16 | After hours: a used car to be checked before it is bought |
| 17 | `17-people-p17-telegram-not-today.json` | people | Telegram | Josh Tipton (17) | the Friday of week T-12 (Fri 2026-08-21) | resolved by 7 silent days | The second advisor at Bonny Oaks, alone at the counter: the price before the need, and the first 'not today' accepted |
| 18 | `18-people-p17-web-own-tires.json` | people | web chat | Josh Tipton (17) | the Thursday of week T-20 (Thu 2026-06-25) | resolved by 7 silent days | Tires bought online: the assistant passes the question on, and the second advisor answers half of it now and half an hour later |
| 19 | `19-people-p22-telegram-bring-it-by.json` | people | Telegram | Dale Hutchins (22) | the Tuesday of week T-16 (Tue 2026-07-21) | resolved by 7 silent days | The Nashville manager and a man he has known for years |
| 20 | `20-people-p22-web-shop-supplies.json` | people | web chat | Dale Hutchins (22), Jasmine Bolden (24) | the Wednesday of week T-9 (Wed 2026-09-09) | resolved by slot 24 | A line on the bill nobody explained: the manager answers the next day, and the other advisor finishes the answer |
| 21 | `21-people-p23-telegram-anytime.json` | people | Telegram | Chad Binkley (23) | the Monday of week T-13 (Mon 2026-08-10) | resolved by 7 silent days | The weak desk on a booking: 'come by monday', 'anytime' |
| 22 | `22-people-p23-web-found-on-the-invoice.json` | people | web chat | Chad Binkley (23) | the Thursday of week T-5 (Thu 2026-10-08) | resolved by 7 silent days | Work recommended on the invoice and never said aloud: the customer asks the website |
| 23 | `23-people-p24-telegram-estimate-attached.json` | people | Telegram | Jasmine Bolden (24) | the Friday of week T-10 (Fri 2026-09-04) | resolved by slot 24 | The bright spot at Charlotte Pike: findings by number, the estimate attached, a total to the cent |
| 24 | `24-people-p24-web-same-day.json` | people | web chat | Jasmine Bolden (24) | the Tuesday of week T-17 (Tue 2026-07-14) | resolved by slot 24 | A dead battery at 7:41: the assistant passes it on, and the advisor finds two times in a full morning |
| 25 | `25-r13-web-one-question.json` | R13 | web chat | Jasmine Bolden (24) | the Wednesday of week T-13 (Wed 2026-08-12) | resolved by slot 24 | Unclear, then clear after one question: 'the thing where you hook it up to the computer' |
| 26 | `26-r13-telegram-two-questions.json` | R13 | Telegram | Angie Holloway (16) | the Wednesday of week T-6 (Wed 2026-09-30) | resolved by slot 16 | Unclear, then clear after two questions: 'the car is doing that thing again' |
| 27 | `27-r13-web-never-clear.json` | R13 | web chat | the assistant alone | the Wednesday of week T-2 (Wed 2026-10-28) | resolved by 7 silent days | Unclear and never cleared: 'how much for the 60' |

## How a file reads

- `scenario`: who writes, what happens, the facts the lines rest on; `unclear` only where rule R13 applies (files 01, 25, 26, 27). `scenario.facts.prices` lists every amount a line says, with the catalogue job, vehicle class and price class it is computed from; `numbers` lists every other number of 20 or more.
- `days`: every day used, as an anchor of rule R6 (`rule` is the machine form) with the date it falls on for the nominal T. `floating_days`: every weekday word and 'today', 'tomorrow', 'yesterday' in the text, with the day it means.
- `conversations[].timeline`: `message` (customer, assistant, staff slot), `note` (private), `draft` with its `outcome`, `handoff` (the tool's arguments, the bot's private note, the board card), `activity`, `outside` (a call or an ERP event, for the reader). Activity lines marked `derived` are the ones the product writes by itself: assigned on the first reply, the handoff label taken off, reopened, and the priority lines of the wait.
- `state_at_t`, `reads_back`: what the Conversations screen and Stats must show. `truth`: the reason (the ledger's taxonomy), who handled it, the outcome, the facts an answer may rest on, the card questions it serves. `new_facts`: what the file invented.

## Conventions the seeder should know

- **Priority lines are derived with designed thresholds**: a chat nobody has answered turns High after 12 working minutes and Urgent after 36; a later message after 24 and 72. The product computes its own from 28 days of replies; the seeder must recompute these lines and the shown level at T (DESIGN.md section 2).
- **Prices are today's list** (class car unless the file says otherwise; the company-account class for A2), with the labour hour after the last rise. Every dated chat is after P. Parts are not drifted back in time, as in the story calls (`../../PENDING.md`).
- **Waits** are in working minutes on the shop's own clock (07:30 to 17:30 weekdays; East Main also Saturday 08:00 to 13:00); the Charlotte Pike chats are on Central time. A wait starts at the hand-off or at the first unanswered customer line.
- **A drafts chat never ends with a draft in the box** unless it is open at T: the last draft is sent, edited, written over or cleared before the chat is resolved, because what Chatwoot's auto-resolve does to a waiting draft was not read in the product.
- **Invented customers' phone numbers are tier B** of `../../phones.md` (NPA-555-0200 and up), so they cannot collide with the tier-A numbers the story calls gave their own invented callers.

## Where a file could not be made to agree, and what was done

- **File 07, the day.** DESIGN.md section 6 puts S13's web question on the 2nd full open day before T; card S13 puts it on the Monday of week W0 when that is before T. The card is followed. The card's footprint calls the chat resolved; the ledger (`conv.open_at_t`) names it as pending, and it is pending: fewer than seven silent days have passed.
- **File 01, 'in the morning'.** Card S07 has the assistant tell her someone will confirm a time in the morning. The product's sentence for a hand-off names no time (`escalation.said.handover`), so the assistant says the shops open at 7:30 and that somebody will get back to her as soon as possible.
- **File 06, the first date.** With the card's days (7, 5, 3, 1) the first chat message is on the Friday, so the 'Friday' of call 15 ('Fella told me Friday') cannot have been given in the chat: it was given when the part was ordered, the day after the car came in.

## New facts other stores must carry

| File | New fact |
|---|---|
| 01 | The photo IMG_4412.jpg (picture pool 'dash-red-brake-lamp'). |
| 02 | The estimate reached her by e-mail from the shop system at about 10:05 on the day of the visit (rdunlap@inbox.example). |
| 02 | The car was ready by 3:00; the order was closed and paid at about 15:10. |
| 02 | The seeping shock absorber is the right rear one. |
| 03 | Maya offered drop-offs on the Monday of week W+1 at 8:00 and the Tuesday at 8:30; the customer is out of town on both days. |
| 03 | A shock-absorber job is spoken of as 'about an hour and a half' (catalogue: 1.2 billed hours). |
| 04 | The quote is for SC-4 (front brake pads and rotors, 640.91 at list) and SC-9 (battery, 304.45 at list); it was asked for the owner's sign-off on the Friday of week T-4. |
| 04 | ERP: the estimate made from this chat is proposed as one of A6's five slow estimates (ledger s1.a6), expired; no order followed. |
| 04 | The file Sourwood_quote_SC4_SC9.pdf (picture pool 'estimate-pdf'). |
| 04 | SC-4's brakes were quoted once before, after call 22 (the Tuesday of week T-9), and not booked; this quote, front pads and rotors only, is A6's second estimate on SC-4. |
| 05 | The Monday lists: week T-22: M-103, M-107, M-110, M-114, M-121; week T-15: five vans, M-112 among them; week T-5: M-104, M-106, M-111, M-115, M-119 (M-108 swapped out); week T-4: M-108 added; week W+1: M-102, M-109, M-113, M-116, M-122. |
| 05 | M-112's front struts and alignment were done on the Monday of week T-15 for 1,119.98 before tax under purchase order 4398A (the 'front struts back in the summer' of story call 25). |
| 05 | M-110 pulled to the right in week T-22; M-113's heater is weak in week W0; M-122's rear brakes were low at its last service. |
| 05 | The photo M112_front_strut.jpg (picture pool 'worn-part-strut'). |
| 05 | The contact's picture: a golden retriever looking out of a truck window. |
| 06 | The first date, Friday, was given to him when the part was ordered, on the day after the car came in, outside the chat and outside any hand-written call (call 15: 'Fella told me Friday'). |
| 06 | ERP: the purchase order for the angle gear was promised for 7 days before T, then for west's 4th full open day before T; on the day of message 3 the supplier said 'early next week' with no tracking number. |
| 06 | Chad repeated call 15's promise in writing at 17:21 on the day of the call. |
| 06 | He has a rental car since 8 days before T. |
| 06 | The missed call is at 09:12 and call 16 at 14:20, as story call 16 has them; message 4 is written after call 16. |
| 08 | Patsy Greer, a regular of the Bonny Oaks shop, 2013 Buick Enclave, rear brakes recommended at her last visit; an appointment on the Wednesday of week W+1 at 13:00. |
| 08 | Angie offers no time of her own inside the week she has asked off (S5): the Wednesday before it with her, or the Friday with Josh (slot 17). |
| 08 | The contact's picture: a white Buick Enclave under a carport. |
| 09 | Darryl Poteet, 2011 Chevrolet Silverado 1500, alternator replaced on the Thursday of week T-18 at main: 766.37 at list, 852.01 with shop supplies and tax; he was given the pre-tax figure on the phone that morning. |
| 09 | The contact's picture: a red Chevrolet Silverado at a boat ramp. |
| 10 | Kim Arnett, (423) 555-0274 (tier B of phones.md), 2012 Ford Escape; a cooling system pressure test at main on the Monday of week T-8 at 14:00. |
| 10 | The photo IMG_2087.jpg (picture pool 'puddle-under-car'). |
| 11 | Shonda Ellis (Telegram name 'Shonda E.'), 2015 Kia Sorento, at main on the Tuesday of week T-11: oil change; rear brake pads approved, 260.31; cabin air filter declined, 67.94. |
| 11 | The photos sorento_rear_pad.jpg and sorento_cabin_filter.jpg (picture pools 'worn-pad', 'dirty-cabin-filter'). |
| 11 | The contact has no picture. |
| 12 | Reggie Dorsey, (423) 555-0318 (tier B), an alignment at main moved from the Monday to the Thursday of week T-4, 08:00. |
| 13 | Brianna Cagle (Telegram name 'Brianna C.'), 2016 Nissan Altima, an oil change at main on the Friday of week T-12 at 08:30. |
| 13 | The contact has no picture. |
| 14 | Jerome Purcell, (423) 555-0391 (tier B), 2017 Toyota Camry, a brake fluid flush at main on the Wednesday of week T-3 at 10:00. |
| 15 | Gloria Yancey, 2014 Toyota Highlander: front brakes at east in week T-16; a no-charge brake noise check on the Wednesday of week T-15 at 13:00 (an anti-rattle clip reseated): a warranty order pointing at the first one. |
| 15 | The contact's picture: sunrise over a lake. |
| 16 | Tasha Reed, (423) 555-0407 (tier B): a pre-purchase inspection of a 2015 Honda Pilot at east on the Wednesday of week T-7 at 08:30. |
| 17 | Dwight Hensley, 2013 Ford F-150: front sway bar links (220.26) recommended at east at an oil change on the Thursday of week T-12 and declined the next day. |
| 17 | The contact's picture: a blue F-150 with a boat trailer. |
| 18 | Hector Ortega, (423) 555-0452 (tier B): four customer-supplied tires mounted and balanced at east on the Friday of week T-20 at 14:00, 100.00 plus disposal at 3.50 a tire. |
| 18 | The shop mounts tires a customer brings (said by slot 17; the public pages do not say). |
| 19 | Buddy Carver, a regular of west, brings his mother's Buick (a whine when turning, a repeat) as a walk-in on the Tuesday of week T-16. |
| 19 | The contact has no picture. |
| 20 | Sharon Whitfield, (615) 555-0236 (tier B): a water pump replaced at west, picked up on the Tuesday of week T-9; the bill carries shop supplies of 17.55. |
| 21 | Terrence Boyd (Telegram name 'T Boyd'), 2010 Honda Accord, asked west for a Saturday oil change on the Monday of week T-13; no appointment was made. |
| 21 | The contact's picture: a brown pit bull on a porch. |
| 22 | Monica Reyes, (615) 555-0289 (tier B), 2016 Hyundai Tucson, at west on the Wednesday of week T-5: rear brake pads at 3 mm recommended on the invoice (225.77), not sold. |
| 23 | Latoya Greene, 2014 Chevrolet Equinox, 96,000 miles, at west on the Friday of week T-10: check engine diagnosis 135.00, ignition coil 153.86, spark plugs 222.28; 579.50 with shop supplies (16.88) and Nashville's sales tax (tax.rate.west, 9.75 %). |
| 23 | The file Estimate_Equinox_Greene.pdf (picture pool 'estimate-pdf'). |
| 23 | The contact's picture: a gray Chevrolet Equinox in a parking garage. |
| 24 | Deion Marshall, (615) 555-0347 (tier B), 2017 Kia Soul: a battery and charging test at west on the Tuesday of week T-17 at 11:30. |
| 25 | Kenny Dillard, (615) 555-0412 (tier B), 2013 Dodge Charger: a check engine diagnosis at west on the Thursday of week T-13 at 07:30. |
| 26 | Dot Kirby, 2012 Toyota Camry, a regular of east: tires balanced in March for a highway shake, a battery light in June; a brake inspection on the Thursday of week T-6 at 09:00. |
| 26 | The contact has no picture. |

## How the files were made

`../build/` holds the sources (`src_en_a.py`, `src_en_b.py`), the library that derives numbering, activity lines, outcomes, waits and the state at T (`convlib.py`), and `build.py`. A JSON file edited by hand is not read back by the builder; the checker reads only the JSON.
