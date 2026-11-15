# Seed v1: the sixteen story cards

A story is a thread through several stores, so a question about it cannot be answered from one screen. The cards are the golden set: each question has one defensible answer, each number is a row of `../ledger.json`, each footprint is something the product can hold. `../checks/check_ledger.py` checks every ledger key a card names; `TIMELINE.md` places every date.

Questions are written as an English-speaking user would type them, with the English configuration's names. The Russian build asks the same questions in Russian with its own names and amounts; where the two builds differ in more than names, the card has a "Per market" block and the expected answer gives both.

## The card form

| Section | Holds |
|---|---|
| Title and path | happy, wrinkle or open decision |
| Who | cast slots with both names and ranks; customers and accounts by their keys in the seed files |
| When | every date as an anchor of rule R6, and what the seeder asserts after placing them |
| Wrinkle (or the story) | what is wrong on purpose, with its numbers |
| Per market | where the two configurations differ in more than names |
| Footprints | per store: the table or store, whether it is loaded as history or written as state at T, and what it holds |
| Ledger keys | the rows the story fixes |
| Questions | one row per question and asker: the question; who asks (slot and rank); the population, period and definition; the expected answer or the facts an answer must contain; where the proof lies; the kind; whether the small size keeps it |

Kinds of question: **value** (one figure or fact), **list**, **explanation** (scored against the listed facts), **action** (the assistant proposes or drafts; nothing is written unconfirmed), **nothing** (the right answer is that there is none), **cannot tell** (the honest answer is that the data does not hold it), **refusal** (by rank or by site), **smoke** (a one-screen question kept as a smoke test), **stale** (asked a day after T: the answer must say what moment its data is from).

"Emitted per build" means the seeder computes the expected answer for its T and writes it beside the data, with the window in which it holds.

## The rules, one line each

| Rule | In one line |
|---|---|
| R1 | History is loaded in bulk with its own ids and times; product commands write only the state at T; the build ends by reading everything back through the product's own reads. |
| R2 | T is an instant with a zone; on a closed day it is the close of the last open day. |
| R3 | Nothing calls a model at build time: verdicts, reports, briefs, run answers and threads are written by the seeder, prose fixed and numbers computed, stamped as seeded. |
| R4 | Every question names who asks; there is one expected answer per asker, and some questions exist to be refused. |
| R5 | Every question states its population, period and definition, or is scored against a list of facts. |
| R6 | Dates are working-day offsets of a named shop or person, or a weekday of a named week; the seeder asserts the order and gaps the card states. |
| R7 | Every ledger row is fixed, scales or a rate with a tolerance and a minimum count; a rate that cannot reach its count is planted as instances; the small size keeps the stories and the instance questions. |
| R8 | A seeded call carries its person and desk; missed-call rates are per desk, because a missed call has no person. |
| R9 | The tenant's settings are part of the seed and versioned; one phone rule in all stores: a customer's phone is shown from junior up. |
| R10 | A build is a function of seed version, configuration, size, T and a random seed, all in a manifest the agent cannot read. |
| R11 | The Russian configuration has its own rows where the trade differs: several price rises, its own leak signature, a 30-day comeback window, documents per order, shops open on public holidays. |
| R12 | Russian advisors work two on, two off at every desk, lead advisors included; the flagship has a fourth advisor (slot 29), part-time in the English configuration. |
| R13 | In a minority of calls and chats the customer is unclear and the advisor has to ask again (12 %); a few end unresolved (2 %); it is spread over call types and advisors, and applies to hand-written items only where a card says so (S1, S6, S7). |

## All questions

<!-- questions:start -->
| # | Story | Question | Asked by | Kind | Small size |
|---|---|---|---|---|---|
| S1.1 | Company accounts: one left, one fading, the anchor paying late | Which of our company accounts have we lost or are losing? | 2 (admin) | list | yes |
| S1.2 | Company accounts: one left, one fading, the anchor paying late | Why did Cumberland Bend Electric stop coming? | 2 (admin) | explanation | yes |
| S1.3 | Company accounts: one left, one fading, the anchor paying late | What should we do about Sourwood Catering? | 4 (senior) | action | yes |
| S1.4 | Company accounts: one left, one fading, the anchor paying late | Is anything wrong with Nickajack Delivery? | 2 (admin) | explanation | yes |
| S1.5 | Company accounts: one left, one fading, the anchor paying late | Which company-account contacts called us and were never called back? | 2 (admin) | list | yes |
| S1.6 | Company accounts: one left, one fading, the anchor paying late | Which advisor missed the calls from Cumberland Bend Electric? | 4 (senior) | cannot tell | yes |
| S1.7 | Company accounts: one left, one fading, the anchor paying late | Which accounts at Bonny Oaks have a bill overdue? | 16 (middle, `east`) | nothing | yes |
| S1.8 | Company accounts: one left, one fading, the anchor paying late | Show me the calls from Cumberland Bend Electric's manager. | 6 (junior, `main`) | refusal | yes |
| S2.1 | The fired advisor's missing money at `west` | Were there unusual discounts at `west`, and who gave them? | 2 (admin) | explanation | no |
| S2.2 | The fired advisor's missing money at `west` | What did it cost? | 2 (admin) | value | yes |
| S2.3 | The fired advisor's missing money at `west` | Did it stop? | 2 (admin) | explanation | yes |
| S2.4 | The fired advisor's missing money at `west` | What is our rule on discounts, and since when? | 6 (junior) | value | yes |
| S2.5 | The fired advisor's missing money at `west` | Has anyone broken the discount rule in the last 30 days? | 2 (admin) | list | yes |
| S2.6 | The fired advisor's missing money at `west` | How much did Brent Lassiter actually take? | 2 (admin) | cannot tell | yes |
| S2.7 | The fired advisor's missing money at `west` | How short was the Nashville till on the days Brent closed it? | 6 (junior) | refusal | yes |
| S2.8 | The fired advisor's missing money at `west` | On which days was `west`'s till short by 20 dollars or more? | 3 (middle) | list | yes |
| S3.1 | The flagship's morning phones | When do we miss the most calls at the flagship? | 4 (senior) | value | yes |
| S3.2 | The flagship's morning phones | Did the early shift help? | 4 (senior) | explanation | no |
| S3.3 | The flagship's morning phones | What is still wrong? | 4 (senior) | list | yes |
| S3.4 | The flagship's morning phones | Who is waiting for a call back right now? | 6 (junior, `main`) | list | yes |
| S3.5 | The flagship's morning phones | Who is waiting for a call back right now? | 4 (senior) | list | yes |
| S3.6 | The flagship's morning phones | Which advisor misses the most calls at the flagship? | 4 (senior) | cannot tell | yes |
| S3.7 | The flagship's morning phones | Who is on the phones at the flagship right now? | 4 (senior), asked one day after T | stale | yes |
| S4.1 | The junior operator gets better | How has my phone work changed since we started? | 6 (junior) | value | yes |
| S4.2 | The junior operator gets better | How has Maya's phone work changed since we started? | 4 (senior) | value | yes |
| S4.3 | The junior operator gets better | What do I still do worst on the phone? | 6 (junior) | value | yes |
| S4.4 | The junior operator gets better | Which team notes wait for a decision? | 4 (senior) | smoke | yes |
| S4.5 | The junior operator gets better | Why was my note declined? | 6 (junior) | value | yes |
| S4.6 | The junior operator gets better | How do Caleb's call scores compare with mine? | 6 (junior) | refusal | yes |
| S5.1 | The shop that leans on one person | What happens at Bonny Oaks when Angie is off? | 4 (senior) | value | yes |
| S5.2 | The shop that leans on one person | Who can cover her week? | 4 (senior) | list | yes |
| S5.3 | The shop that leans on one person | What did the diagnostician's leave cost? | 4 (senior) | explanation | yes |
| S5.4 | The shop that leans on one person | What is waiting for my decision about next week's roster? | 4 (senior) | smoke | yes |
| S6.1 | `west` waits for parts | Why do cars stay longer at `west`? | 2 (admin) | explanation | yes |
| S6.2 | `west` waits for parts | Which cars are waiting for parts at `west` now, and for how long? | 22 (senior) | list | yes |
| S6.3 | `west` waits for parts | Is the brake problem the mechanic or the parts? | 2 (admin) | explanation | no |
| S6.4 | `west` waits for parts | What was decided about `west`'s supplier? | 2 (admin) | smoke | yes |
| S6.5 | `west` waits for parts | What did we promise the customer whose car has waited longest at `west`? | 22 (senior) | explanation | yes |
| S6.6 | `west` waits for parts | Who is in `west`'s call-back queue? | 6 (junior, `main`) | refusal | yes |
| S7.1 | A private customer, start to finish | Tell me everything about Rachel Dunlap. | 6 (junior) | explanation | yes |
| S7.2 | A private customer, start to finish | What did she decline, and has she come back for it? | 6 (junior) | value | yes |
| S7.3 | A private customer, start to finish | What should I answer her? | 6 (junior) | action | yes |
| S7.4 | A private customer, start to finish | What score did my confirming call to her get? | 6 (junior) | nothing | yes |
| S8.1 | A wrong price promised by the newcomer | What went wrong with Frank Daugherty's timing-belt job? | 4 (senior) | explanation | yes |
| S8.2 | A wrong price promised by the newcomer | Was the discount inside our rules? | 4 (senior) | value | yes |
| S8.3 | A wrong price promised by the newcomer | Where did the wrong price come from? | 5 (middle) | explanation | yes |
| S8.4 | A wrong price promised by the newcomer | What did the complaint call score? | 4 (senior) | nothing | yes |
| S9.1 | The meeting across the time zone | Why does Dale miss the Monday meeting? | 2 (admin) | explanation | yes |
| S9.2 | The meeting across the time zone | How often was he there? | 2 (admin) | value | yes |
| S9.3 | The meeting across the time zone | Find a time that works for all three shops. | 2 (admin) | action | yes |
| S9.4 | The meeting across the time zone | Has anyone raised the Monday meeting time as a problem? | 2 (admin) | nothing | yes |
| S10.1 | The owners' pulse | Did all my reports run last week? | 2 (admin) | smoke | yes |
| S10.2 | The owners' pulse | What did my brief say this morning? | 1 (senior) | list | yes |
| S10.3 | The owners' pulse | Which scheduled reports do I have? | 2 (admin) | list | yes |
| S10.4 | The owners' pulse | What are the founder's reports? | 6 (junior) | refusal | yes |
| S11.1 | The season | When is our busiest time, and with what work? | 2 (admin) | explanation | no |
| S11.2 | The season | How did the last season go? | 2 (admin) | explanation | no |
| S11.3 | The season | When should the seasonal hire start this year? | 4 (senior) | value | no |
| S12.1 | The knowledge base that disagrees with itself | What do we charge for a timing belt on a 2011 Subaru Outback? | 6 (junior) | value | yes |
| S12.2 | The knowledge base that disagrees with itself | Which pages still show the old prices? | 5 (middle) | list | yes |
| S12.3 | The knowledge base that disagrees with itself | What is our warranty? | 6 (junior) | value | yes |
| S12.4 | The knowledge base that disagrees with itself | What is waiting to be approved in the knowledge base? | 4 (senior) | smoke | yes |
| S12.5 | The knowledge base that disagrees with itself | What does the "Pay and till" page say? | 6 (junior) | refusal | yes |
| S13.1 | Changed hours next week | Are we open on the afternoon of the stocktake day? (the date is typed; old: are we open on that afternoon) | 6 (junior) | smoke | yes |
| S13.2 | Changed hours next week | How many calls did we miss on the last holiday? | 4 (senior) | value | yes |
| S13.3 | Changed hours next week | Which dates in the next 60 days are we closed or closing early, beyond the usual weekly hours? | 6 (junior) | list | yes |
| S14.1 | Attendance | Who is late most often? | 4 (senior) | list | yes |
| S14.2 | Attendance | Who forgot to clock out in the last 30 days? | 4 (senior) | list | yes |
| S14.3 | Attendance | Which shifts between now and the end of next week have nobody? | 4 (senior) | list | yes |
| S14.4 | Attendance | How many requests did Dustin file in the last 90 days, and what happened to them? | 4 (senior) | value | yes |
| S14.5 | Attendance | Why was Wes Tate let go? | 4 (senior) | cannot tell | yes |
| S14.6 | Attendance | Did anyone at Bonny Oaks clock in from outside the site? | 4 (senior) | nothing | yes |
| S14.7 | Attendance | Who is late most often? | 15 (worker) | refusal | yes |
| S14.8 | Attendance | What happened to Austin Crabtree's shift two working days ago? (the date is typed) | 4 (senior) | value | yes |
| S15.1 | The ERP's own mess | How many customers do we have? | 2 (admin) | value | yes |
| S15.2 | The ERP's own mess | What was last month's revenue? | 2 (admin) | value | yes |
| S15.3 | The ERP's own mess | What is the average order at each shop? | 2 (admin) | value | yes |
| S15.4 | The ERP's own mess | How many calls and orders did `west` have before 9:00 home time last week? | 2 (admin) | value | yes |
| S15.5 | The ERP's own mess | Which orders have a mileage that cannot be right? | 4 (senior) | list | yes |
| S15.6 | The ERP's own mess | Which orders have been open for more than 60 days? | 2 (admin) | list | yes |
| S16.1 | Preparing the anchor account's review | What is still missing for the review? | 6 (junior) | value | yes |
| S16.2 | Preparing the anchor account's review | Who is working on it? | 2 (admin) | smoke | yes |
| S16.3 | Preparing the anchor account's review | What should the review say about Nickajack Delivery? | 6 (junior) | explanation | yes |
| S16.4 | Preparing the anchor account's review | Is any task of mine overdue? | 6 (junior) | nothing | yes |

84 questions in 16 cards; the small size keeps 78 and drops 6.

| Kind | Questions |
|---|---:|
| value | 22 |
| list | 18 |
| explanation | 16 |
| action | 3 |
| nothing | 6 |
| cannot tell | 4 |
| refusal | 7 |
| smoke | 7 |
| stale | 1 |
| all | 84 |
<!-- questions:end -->
