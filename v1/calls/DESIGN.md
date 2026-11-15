# Calls and transcripts: design (seed v1)

Brought to the ledger and the story cards in the reconcile pass of 2026-11-13: every number here that is a ledger row is in `../ledger.json` under the key named beside it, and `../checks/check_files.py` fails on a difference. Rules R1 to R13 of the seed design are cited as "design rule Rn"; R1 to R12 in section 4 are this file's own recognition rules.

Paths without a root are in the product repository; `B` = `apps/backend/src/traciora/core/phonecalls`. Ledger = `../ledger.json`. Classes: **M** measured, **D** derived, **X** designed. Research on real recordings: the product's phone-call research (2026-10-24 error audit, 2026-10-25 restoration study).

Three facts of the product shape everything below:

- **The stored transcript is not a recogniser's output.** Several recognisers hear the call, and a language model restores one dialogue from their variants (`docs/features/call-pipeline.md:1078-1131`, `config/prompts/restoration_prompt.txt`). What is stored is that dialogue: one line per turn, the speaker as the role key `manager` or `customer`, no timing and no confidence (`B/ingestion/processing.py:195-228`; `apps/backend/schema/traciora-core.sql:1098-1106`). The recognisers' variants and the timed speaker turns stay in an encrypted file beside the call.
- **Only an inbound call of type `new_enquiry` can carry a score.** Six of the eight checks apply to new enquiries only; an `existing_job` call can be scored on `greeting` and `recap`, and under three scored checks the score is null (`config/defaults/phonecalls_scorecard.json`; `B/scorecard.py:19,26,174-184`; `B/judge.py:254-268`). Outbound and internal calls are not judged (`B/ingestion/processing.py:70`).
- **A level above 0 needs a quote on a manager's line**, found word for word (`B/judge.py:229-251`). So a line under the wrong speaker, or a garbled one, costs the check its evidence.

## 1. One call in the tables

| Table (schema line) | A seed fills | May stay empty |
|---|---|---|
| `interactions.interaction` (757) | `channel='call'`, `direction`, `state='closed'`, `started_at`, `ended_at`, `answered_at`, `duration_s` (talk), `location_id`, `person_id` with `attributed_by` and tier, `origin='connector'`; `disposition='no_answer'` on a miss, else null (`B/ingestion/call_log_store.py:448`) | `summary_enc`, `first_response_at`, `waiting_since` |
| `interaction_participant` (865) | one `handler` row from the answer | |
| `call_leg` (1487) | one row per desk rung: `status`, `ring_s`, `talk_s`, `extension`, `line`, `location_id`, sealed payload, `caller_token` or `callee_token`. Without a leg a call is not "logged" and is counted nowhere on the Calls screens (`B/call_log_reads.py:105-107`) | `recording_name_token` |
| `recording_run` (1252) | one succeeded row per provider with checkpoint `operation: call_log`, `since` = go-live, `read_at` = seed time; else the screens say the call log is not connected and show gaps (`B/call_log_reads.py:100`; `B/ingestion/call_log_store.py:782-815`) | |
| `media_object` (912) | `kind='recording'`, hash, duration; a transcript must point at one (1022, 1077) | `storage_ref_enc`: **no audio is needed**; the sheet draws a player only while the bytes are stored (`B/call_reads.py:440-472`) |
| `transcript` (1013) | `engine='ensemble'` (`processing.py:87`), `engine_version` = models, revisions and restoration fingerprint (`processing.py:178-187, 719-720`), `language`, `text` (the labelled dialogue), `pii_state='raw'` (`B/ingestion/repository.py:1462`), `word_count`, `duration_s` | `detector_version`, retention |
| `transcript_segment` (1090) | per line: `sequence` from 0, `speaker_label`, `text` | `start_ms`, `end_ms`, `confidence`, `person_id`: null, as the product writes them |
| `interaction_analysis` (1141) | `kind='scorecard'`, `result_public` = `Verdict.public` plus `media_version` (`B/judge.py:95-109`), `result_enc` = `Verdict.sealed` (`:111-120`), `score`, `prompt_version` (`processing.py:268`), `transcript_id`. An unjudged call gets `judged: false`, no score (`processing.py:773-782`) | |
| `missed_call` (1575) | on a miss only: section 5 | |
| `phone_day_report` (1650) | one sealed report per person and day with a judged customer call | proposal: write them for the last 14 days and the story days only |
| `recording_job`, `recording_export` | | empty: every read left-joins them (`call_reads.py:466`), and with no job the pipeline never re-judges a seeded call |

No command writes `call_leg` or `missed_call`; the product lands them from a call-log source (`call_log_store.py:193`). Proposal for the seeder's owner: serve the designed legs through that reader, one read per seeded day under `tenant_binding.at`, so calls, misses and follow-up come from the product's own rules.

The seed's verdict numbers are computed, not typed: the samples' `result_public` was produced by running the designed judge answer through `judge.verdict` itself.

## 2. Taxonomy

Inbound answered calls. Shares are of answered inbound calls; talk time is the median, in seconds; a turn lasts about 6 s (EN) or 5.5 s (RU).

| Why people call | Rubric type | EN % | RU % | Talk EN / RU | Turns EN / RU |
|---|---|---:|---:|---:|---:|
| what a job costs | `new_enquiry` | 30 | 28 | 140 / 115 | 24 / 20 |
| to book, or whether there is a slot | `new_enquiry` | 30 | 22 | 150 / 120 | 26 / 22 |
| can you do it, hours, where you are | `new_enquiry`, mostly `no_visit: info_only` | 12 | 12 | 60 / 50 | 10 / 9 |
| is it ready, has the part come, pick-up | `existing_job` | 10 | 13 | 70 / 60 | 12 / 11 |
| extra work found, a booking moved | `existing_job`; `new_enquiry` when new work is asked for (judge's rule 0) | 6 | 9 | 110 / 95 | 18 / 16 |
| complaint, comeback, the bill | `existing_job` | 4 | 6 | 220 / 190 | 34 / 30 |
| supplier, delivery, sales | `supplier` | 4 | 5 | 55 / 45 | 9 / 8 |
| wrong number | `wrong_number` | 1.5 | 2 | 15 | 4 |
| silence, a robot, staff | `other` | 2.5 | 3 | 12 | 2 |

- EN is anchored on the one measured split: price 30, booking 30, general questions 26, service issues 6, other 8 (In Motion Brands via Auto Service World 2026, read; `us-shop.md` section 5). RU has no source and is designed: more status and approval calls, because parts wait longer and extra work is agreed by voice.
- So `new_enquiry` is 72 % (EN) and 62 % (RU) of answered inbound calls: the only calls that feed a person's score.
- **Outcomes** follow from the advisor's level on `asked_for_booking`, never drawn apart: level 2 is `visit_agreed` (92 %) or a dated `callback_promised` (8 %); level 1 is `customer_will_call` or an undated `callback_promised`, half each; level 0 is `customer_will_call` when a doubt was voiced, else `no_visit`.
- **Unclear customers (design rule R13).** In 12 % of answered customer calls (new enquiry or existing job) the customer says what they want vaguely or the wrong way round and the advisor has to ask again, sometimes twice (`r13.calls.clarification_loop`); 2 % end with the request still unclear (`r13.calls.unresolved`). It is a property of the caller, spread over the call types and over every advisor, each advisor's own share within 4 points of the row. A good advisor's second question is the evidence for `need_discovery` at level 2 and never changes the dealt levels; a call that ends unclear takes `need_discovery` at level 0 or 1 out of the advisor's dealt levels and ends as `customer_will_call` or `no_visit`. Hand-written calls carry it only where a card says so: call 21 (S1, resolved after two questions) and call 16 (S6, left unclear) (`r13.story_items`).
- **Outbound** (transcribed, never judged): 1.2 per order (EN), 1.6 (RU) (`calls.outbound_per_order`). EN: car ready 35 %, approval of found work 25 %, calling a missed caller back 18 %, supplier 12 %, confirming a booking 10 %. RU: approval 35, ready 30, supplier 17, call back 10, confirm 8. Seven in ten are answered; the rest are the unanswered attempts the queue counts.
- **Who answers.** Each advisor has a desk extension (`pNN.desk`): 101 (slot 5), 102 (6), 103 (7) and 105 (29) at `main`; 201 (16) and 202 (17) at `east`; 301 (22), 302 (23) and 303 (24) at `west`. Desk 304 was F1's and rang until the day he was fired (`pF1.desk`). A site's public line rings one desk first (the next in turn among those on duty) for 20 s, then every desk for 15 s. Answered calls split by the ledger's `pNN.answered_share`: at `main` 34 / 34 / 26 / 6 % (EN: slot 29 is part-time) and 26 / 26 / 22 / 26 % (RU), at `east` 55 / 45 and 52 / 48, at `west` the shop manager (22) takes 15 %, 23 takes 47 % (RU 45) and 24 takes 38 % (RU 40).
- **Season** (S11): the extra calls are bookings of one pattern (tyre change in RU, air conditioning in EN), 60 s, added on top of the mix.

## 3. How a transcript is built

`transcript = recognition( speech( scenario, style sheet, market ) )`

1. **Scenario**: who calls (first-time, known, company contact, driver), which car from `parc.json`, which job from `catalogue.json` with its price on the call's day (`catalogue.json` `price_history`), what they want, whether the caller is unclear and how that ends (design rule R13), and the customer's side of each check: is the customer known (35 % of new enquiries: `name_and_number` N/A), do they ask the price (60 %; else `price_with_next_step` N/A), do they name a time first or need no visit (15 %: `offered_time` N/A), do they voice a doubt (45 %; else `objection` N/A).
2. **Style sheet**: for the advisor, the chance of level 0, 1 or 2 on each check. Levels are **dealt, not rolled**: for a person's month, each level is given to `round(calls × share)` calls, so the month's mean is the sheet's within rounding. `offered_time` and `asked_for_booking` take the same rank in 70 % of calls (a call with no next step fails both). `recap` applies when a booking was taken (level 2) and in half of level 1 (a step with no date was agreed).
3. **Market language**: the script is written in the market's own speech from phrase banks per advisor and per level, never translated. The table shows what a level sounds like.

| Check (weight) | 0 | 1 | 2 |
|---|---|---|---|
| `greeting` (1) | "Hello?" · «Да, слушаю.» | "Brennan Auto Care." · «Ермак-Сервис.» | "Brennan Auto Care, this is Maya." · «Ермак-Сервис, Алина, здравствуйте.» |
| `name_and_number` (2) | never asks | takes the number, "Got it." · «Ага, записала.» | "…0174? Perfect." · «Номер этот, с которого звоните? Девятьсот двадцать семь…» |
| `need_discovery` (2) | prices "brakes" without asking the car | "What kind of car?" and no more · «Машина какая?» | "How long's it been doing that?" · «А давно так? Масло когда меняли?» |
| `price_with_next_step` (2) | "Can't say over the phone." · «По телефону не скажу, приезжайте.» | "Two-forty." · «Девятьсот. Работа.» | "…four sixty-five if it's the hub, and I could get you in Friday at eight." · «…если диски под замену, одиннадцать двести; могу принять в субботу в десять.» |
| `offered_time` (3) | "We're open till five-thirty." · «Работаем до восьми.» | "When did you want to bring it?" · «Есть суббота, десять.» | "Tomorrow at 7:30 or Friday at 1?" · «Завтра к девяти или в пятницу к девяти?» |
| `asked_for_booking` (3) | "Okay, sounds good, thanks for calling." · «Хорошо, звоните.» | "Want me to put you down?" "I'll call you." · «Мы вам наберём.» | "I've got you down for Friday at eight, ask for Maya." · «Записала: суббота, десять, принимаю я.» |
| `recap` (1) | "See you then." · «Всё, ждём.» | "So, Friday at eight." · «Значит, в субботу в десять.» | time, address, work · «Суббота, десять, Московское шоссе, сорок, передние тормоза.» |
| `objection` (2) | "Yeah… so, Friday at eight?" · «Ну, да. Так, в субботу удобно?» | "It's all warrantied." · «Ну, у нас гарантия.» | "Did somebody quote it lower? Here's what's in that number." · «А с чем сравниваете? Смотрите, из чего сумма.» |

### Style sheets

Cells are the chances of level 0 / 1 / 2, in per cent. "Expected" is the mean score of the person's scored calls: over the 16 combinations of the four N/A cases above, the three booking levels and whether `recap` applies, the mean of `100 × Σ(weight × level ÷ 2) ÷ Σ weight` over the checks that apply, with the rubric's weights 1, 2, 2, 2, 3, 3, 1, 2.

| Slot | greeting | name and number | need | price | offered time | booking | recap | objection | Expected | Ledger |
|---|---|---|---|---|---|---|---|---|---:|---:|
| 5 lead, `main` | 0/10/90 | 5/30/65 | 0/35/65 | 5/30/65 | 10/40/50 | 5/25/70 | 20/30/50 | 15/45/40 | 77.9 | 78 |
| 6 junior operator, month 1 | 0/10/90 | 15/35/50 | 5/35/60 | 5/65/30 | 45/40/15 | 25/25/50 | 65/25/10 | 55/35/10 | 57.9 | 58 |
| 6 junior operator, month 6 | 0/5/95 | 5/50/45 | 0/35/65 | 5/40/55 | 10/55/35 | 10/27/63 | 15/35/50 | 45/45/10 | 71.9 | 72 |
| 7 newcomer | 5/25/70 | 45/40/15 | 20/50/30 | 25/55/20 | 45/45/10 | 35/40/25 | 70/20/10 | 60/30/10 | 43.9 | 44 |
| 29 fourth advisor, `main` | 0/10/90 | 10/40/50 | 0/30/70 | 5/50/45 | 25/50/25 | 15/35/50 | 50/30/20 | 30/45/25 | 66.0 | 66 |
| 16 lead, all-star | 0/5/95 | 0/20/80 | 0/15/85 | 0/20/80 | 5/30/65 | 5/20/75 | 5/25/70 | 5/45/50 | 86.0 | 86 |
| 17 | 5/20/75 | 20/45/35 | 5/45/50 | 10/50/40 | 25/50/25 | 20/30/50 | 45/30/25 | 35/45/20 | 61.0 | 61 |
| 22 shop manager | 30/55/15 | 50/40/10 | 5/40/55 | 15/65/20 | 40/45/15 | 20/50/30 | 75/20/5 | 40/40/20 | 48.0 | 48 |
| 23 weak desk | 20/65/15 | 55/35/10 | 15/65/20 | 25/60/15 | 45/45/10 | 35/40/25 | 80/15/5 | 65/30/5 | 39.0 | 39 |
| 24, month 1 | 0/15/85 | 10/40/50 | 5/40/55 | 5/50/45 | 20/50/30 | 15/35/50 | 35/35/30 | 30/45/25 | 66.1 | 66 |
| 24, month 6 | 0/10/90 | 5/35/60 | 0/35/65 | 5/35/60 | 10/50/40 | 10/30/60 | 20/40/40 | 20/45/35 | 74.0 | 74 |

The cells are the ledger rows `pNN.check.<check>` (`p06.check.first.*`, `p06.check.last.*` and the same for slot 24); "Ledger" is `pNN.call_score`, or the first and last value of `pNN.score_path`. Slot 29's sheet was added with the slot: a steady old hand, weak on the summary.

- **A trend is a mix of two sheets.** Month m uses `(1 − λ) × first + λ × last`. Slot 6: λ = 0.00, 0.22, 0.37, 0.65, 0.87, 1.00 gives 58, 61, 63, 67, 70, 72 (S4). Slot 24: λ = 0.00, 0.12, 0.37, 0.49, 0.74, 1.00 gives 66, 67, 69, 70, 72, 74, mean 70. Slot 7: his three months run 41, 44, 47 by mixing his sheet with slot 17's (λ = −0.17, 0, 0.18).
- **Slot 6's booking column is S4's own number.** A first-time call ends in a visit when booking is level 2 and it is a visit (92 %): 50 % × 0.92 = 46 % in month 1, 63 % × 0.92 = 58 % in month 6.
- **What each sheet says in words.** 5: complete and brisk, soft only on doubts. 6: warm, always names herself, good questions; early she quotes and stops, which is level 0 on time and booking in one call in five; her doubt-handling barely moves. 7: says the script's greeting, asks little, prices from memory. 29: unhurried and complete, asks what the car is doing before any price, reads the booking back though seldom the address. 16: two times offered, the booking and the summary almost always. 17: does each thing half. 22: answers "Yeah, Brennan's", knows the caller, agrees "just bring it by". 23: the company's name, a bare price, lets the caller go. 24: careful, getting firmer on times.
- **Auto-fails** (share of a person's judged calls): `wrong_promise` 23: 4 %, 22: 2 %, 17: 0.5 %, others 0, and slot 7 has exactly two, both planted (S8, S12). `dropped_customer` 23: 3 %, 7: 2 %, 22: 1 %, others 0. Promised callbacks not kept (the call log's auto-fail): 16: 3 %, 5: 8 %, 6 and 24: 12 %, 29: 15 %, 17: 20 %, 7: 30 %, 22: 45 %, 23: 50 %; company about 22 % (CallRevu mid-2026, dealers: 22.4 %, read; M as a shape). Where a person's base is too small for a rate the ledger plants named instances instead (design rule R7): slot 17's and 22's wrong promises, 22's dropped customers, 16's and 29's callbacks (`pNN.wrong_promise`, `pNN.dropped_customer`, `pNN.callback_not_kept`).

### Assembler rules (for the generator)

The background calls are assembled from the banks `bank-en/` and `bank-ru/`. The banks' sample assemblers apply part of these rules; the generator applies all of them, and its own test suite runs the test named with each rule on calls assembled over many random seeds (at least 40 seeds of 60 calls per language), never on one fixed seed. These rules come from reading the two call banks' assembled samples (2026-11-14).

1. **One price per job per call, and its tax basis said.** A job's price is drawn once per call (`catalogue.json` on the call's day, for the car's class and the parts tier), and every line that names it (the price statement, a recap, a found-work line, an objection answer) gives that figure. English lines give the list price before tax; a line with `{price_otd}` gives the figure with shop supplies and sales tax and says so. Russian lines give the price as paid, VAT inside. A caller's answer does not change the price line: when the answer rules out a part that the price statement names (Russian sample 46: «помпу недавно меняли», then a price that names the pump), the generator takes a price statement that does not name that part, or an answer that does not rule it out. The generator owns the list of answers that rule out a part; the known case is the water pump. *Test:* in every call, each job carries one money value; no call holds an answer and a price statement that the list marks as contradicting each other.
2. **A speaker says a beat once.** A beat (a role of the skeleton: the greeting, the price, the offered times, the booking, the recap, the closing, the caller's request) is spoken once per call by its speaker. Assembly must not stitch in a second line that does the same work, and a speaker never repeats their own line. *Test:* no role other than `backchannel`, `filler` and `hold` occurs twice for one speaker in a call; no two lines of one speaker in a call are equal, ignoring case and punctuation.
3. **A follow-up only where its premise was said.** A line that refers back is kept only when what it refers to was said earlier in the same call: a recap or a "see you then" needs a booked time; an objection answer needs a doubt; a price doubt needs a price (the bank already turns a price doubt into `think` when no price was given); a callback recap needs a promised callback; "like I said" needs the thing said. *Test:* every line whose role needs a premise (the generator's table: role and the earlier role it needs) has that premise earlier in the call.
4. **A caller's urgency is one value per call.** The scenario draws it once (today, this week, no hurry). Every caller line that speaks of time (voice lines, `since_answers`, `name_own_time`, `decline`, `after_answer_*`) comes from wordings that agree with it, so "as soon as possible" and "I'll wait till it gets worse" never meet in one call. The banks carry no urgency mark, so the generator marks every wording that speaks of time and draws only those that agree. *Test:* no call holds two marked lines of different urgency.
5. **The advisor's closing matches the call's outcome.** `closing_booked` («ждём вас») only when a visit was agreed. A closing that promises a call back (`moves.closing_callback` in Russian, and the English wordings that promise one) only when the outcome is `callback_promised` and the promise was made earlier in the call. `closing_open` in every other case. Nobody is promised a call back they did not ask for. *Test:* each call's closing is of the kind its outcome names (visit_agreed: booked; callback_promised: callback; others: open).
6. **Duplicate lines are measured over many seeds.** The share of lines of four words or more that repeat an earlier line of the same advisor's set depends on the seed. In English it is 1.88 % with the bank's fixed seed, about 2.2 % on average, and two seeds of forty went over 3 %. Counted with backchannels it is 8.5 %. Backchannels and other lines of fewer than four words are left out, as they repeat in life. *Test:* over at least 40 seeds, the mean share is at most 2.5 % and no seed is above 4 %, in each language.
7. **Gearbox-bound jobs go only on a car with a matching gearbox.** This is a restriction. `parc.json` gets no transmission field: each of its 156 model rows would need a sourced gearbox mix by year, which is not trivial. The restriction:
   - The Russian `clutch` block is drawn only for a model sold with a manual gearbox in Russia over its listed years: every Lada, УАЗ, ГАЗ and Datsun model; Daewoo Nexia and Matiz; Renault Logan, Sandero and Duster; Hyundai Solaris and Accent (ТагАЗ); Kia Rio; Volkswagen Polo седан; Skoda Rapid; Chevrolet Lacetti, Aveo and Cruze; Ford Focus and Transit; Peugeot Boxer; Fiat Ducato; Mercedes-Benz Sprinter Classic.
   - The Russian `atf_service` block and the English chat block `atf_drain_fill` are never drawn for a model sold without an automatic over its listed years: Lada 2104–2107, Samara, 2110, Niva Legend and Niva Travel; УАЗ «Буханка»; ГАЗель (3302 / 2705) and Соболь; Daewoo Nexia; Peugeot Boxer; Mercedes-Benz Sprinter Classic. The lists are designed from general market knowledge, not read on a source; the generator's owner may widen them.
   - Neither block is drawn for an electric car (engine `timing: none`). The timing-belt block keeps its own rule: belt engines only.
   *Test:* no assembled call or chat puts a clutch job on a model outside the first list, or a transmission-fluid job on a model of the second list or on an electric car.
8. **A company's caller comes from `accounts.json`.** On a company call (skeleton NE11, the dispatcher and driver voices, a fleet unit), the caller is a contact of that account who is in post on the call's day (`contacts`, `from_months_before_t`, `to_months_before_t`). The unit and the plate come from the account's `fleet`, and `{boss_first}` is the account's fleet contact. A small business has no contacts listed: its caller is an invented name, kept for that business across all its calls. *Test:* every company call's caller is a contact of its account, in post that day.
9. **Lengths: designed against assembled.**
   - Designed (section 2 and ledger `calls.reasons`): a new enquiry runs 24 to 26 turns in English and 20 to 22 in Russian; an existing-job call runs 12 and 11.
   - Assembled: the English bank's sample comes out at about 19 and 9.
   - **The generator must reach the designed lengths.** They are the ledger's, and the Russian ones rest on measured recordings (119 s and 207 words a call). It adds what the bank leaves out: backchannels and overlaps as rule R7 counts them, holds of rule R9, a second discovery question where the level allows it, and the caller's restarts.
   *Test:* over many seeds, the median turns and talk seconds per reason are within 15 % of `calls.reasons`.
10. **A recap at booking level 1.** Step 2 above and the scoring model behind each sheet's "Expected" column give a recap to half of the level-1 calls: those that end with an undated `callback_promised`. The English bank marks recap not applicable at level 1, because every one of its recap wordings names a booked time. The design stands and the bank is short of wordings. A level-1 call that ends `callback_promised` takes a step recap (who calls, about what, no date): the existing-job skeletons' `callback_recap` in English, `moves.recap_step` in Russian. *Test:* of the level-1 new enquiries, 50 ± 5 % carry a recap; every one of them ends `callback_promised`, and none names a time.
11. **Status, supplier and outbound lines are shared within a tier.** They are written once per tier (exact, warm, curt) and coloured by each advisor's own tokens, fillers and address, so the advisors of one tier share them. Accepted: a reader hears one advisor's day, and the advisor's own words set the lines apart. *Test:* rule 6 counts these lines per advisor.
12. **A voice's tail goes only where it fits.** A voice `tail` or insert goes only on the caller's first line, an answer or a doubt. It never follows a status answer, a yes or a no, or a goodbye («Вот такие дела» in Russian sample 49 is the case to avoid), and a call holds at most one. *Test:* tails land only on those roles, at most one a call.

**The two banks' formats differ, and must be reconciled into one format document before a generator is planned.** `bank-ru/FORMAT.md` says it follows `bank-en/FORMAT.md` but departs from it. Neither bank is edited here. Each bank's JSON files are its source; the Russian bank's generating scripts were not kept. The differences:

- **The Russian bank adds:**
  - `forms.json`, the closed lists of case forms: 78 cars in six cases, people, days, hours, years, units, parts and lost items, with the number rules. Slots ask for a form as `{slot.form}` (`.gen`, `.dat`, `.acc`, `.ins`, `.prep`, `.na`, `.v`, `.k`, `.nom`, `.day`, `.do`).
  - Gender markers: `{a:…|…}` by the advisor and `{c:…|…}` by the caller, and the voice key `caller_sex`.
  - State-dependent slots: `{name_comma}`, `{comma_name}`, `{car_comma}` and `{advisor_heard}`, with the beat key `names`.
  - Numbers said aloud by the advisor's `price_style` (`short`, `full`, `full_rub`, `round`). A phone is said in groups 3-3-2-2, a plate as an ordinal, an hour from `forms.json`.
  - Four forms of a job's name (`job_said_na`, `job_inf`, `job_do`), and the job keys `part` and `symptom`.
  - A positional `asked_for_booking["1"]`: wordings 1 and 2 are declined, wordings 3 and 4 are an undated promise. With it come `moves.recap_step`, `moves.next_step` with `{next_step}`, and `moves.closing_callback`.
  - Objection wordings at levels 0 and 1 written for «дорого», and `generic_objections.compare`.
  - Advisor keys `gender`, `price_style`, `name_forms` and `moves.tatar`.
  - Skeleton keys: `vendors`; `voice_filter` and `recap` (`do`, `said`) on existing-job skeletons; `agreed_time: "next_day"`.
  - Unclear-opening keys: `ask`, and `opening[i]` paired with `second_answer[i]`.
  - `west_tatar`.
  - The shuffled-bag dealing of wordings, and the filler rules, written as format.
  - Slots of its own: `{greet}`, `{job_inf}`, `{job_do}`, `{second_job_inf}`, `{found_job_inf}`, `{asked_for_person}`.
- **The English format has, and the Russian bank does not use:**
  - the advisor keys `greetings`, `greeting_tails` and `address`;
  - the voice form `{"parts": …}`;
  - `callback_recap` and the `agreed_time` phrases;
  - the slots `{sir_maam}`, `{customer_email_said}`, `{price_otd}`, `{tow_name}`, `{po_said}`, `{boss_first}` and `{day_next}`.

## 4. The imperfection model

The seeder runs no recogniser. It applies rules to the clean script and writes what the restoration would have left. A call draws a **profile**, which is the restoration's own tier (`config/defaults/restorer_thresholds.json`: consensus above 0.55, from 0.2, below):

| Profile | Consensus | Looks like | EN % | RU % |
|---|---|---|---:|---:|
| light | > 0.55 | fluent lines; wrong names and numbers here and there | 80 | 72 |
| marked | 0.2 to 0.55 | `{?likely: …}` around doubtful spans (`fragment_restoration_task_medium.txt`), lost words, a speaker swap | 15 | 20 |
| heavy | < 0.2 | `[unintelligible]` for what the models disagree on (`…task_low.txt`) | 3 | 6 |
| no conversation | | `[NO CONVERSATION]`, no line, unjudged with `reason: no_conversation` | 2 | 2 |

RU shares lean on the real recordings: 44 of 52 rated good, 6 hard to hear, 2 noisy; 43 of 50 hold an unintelligible stretch (error audit, M). EN has no measurement (X). Recognisers switched on in the demo tenant: `parakeet` + `faster_whisper` (EN), `tone` + `gigaam` (RU, the pair measured with restoration: 24.3 % word error against 27.5 % for the better recogniser alone).

| # | Kind | Rule applied to the script | Rate EN | Rate RU | Judgeable? |
|---|---|---|---:|---:|---|
| R1 | Speech thinned | "uh", "um", «э-э», «м-м» dropped; "well", "you know", «ну», «вот», «значит» kept; restarts closed; grammar mended ("a airplane" to "an airplane"); small slips of form («заодно» to «за одно») | 90 % of hesitations, 30 % of fillers | 85 %, 25 % | yes |
| R2 | Names | a surname, company or street to a neighbour in sound, each mention drawn apart, so one call spells it two ways (Vaughn / Vaughan; «Сафина» / «Савина»); a company's name heard as plain words («тёплый контур») | 12 % of mentions; first names 3 % | 15 %; 4 % | yes |
| R3 | Spelled strings | plates, VINs, part and order numbers: one character swapped (B/P, «эм»/«эн»), dropped or regrouped | plate 35 %, VIN 70 %, order number 20 % | 30 %, 70 %, 20 % | yes |
| R4 | Trade words, makes, models | to a common word that sounds alike (caliper / caliber, pinion / opinion, «маховик» / «моховик»); a model that is also a word in lower case («фокус», «газель»); RU: a name said in English comes out in Latin or Cyrillic by turns («Kia Rio», «Next», «TSI») | 8 % of listed terms | 14 %; script choice Latin 55 % | yes |
| R5 | Numbers | digits for money, times, years and phones in 85 % (EN) and 80 % (RU) of mentions, words otherwise; an error splits or merges: "four eighty-six" to "$4.86", «двадцать семь четыреста» to «20 7400», «пять-тридцать» to «5-30»; a phone loses or changes a digit | 6 % of money and time mentions; phones 5 % | 9 %; 8 % | yes: a garbled price is still a price; the ERP holds the true one |
| R6 | Words lost under noise | a burst takes 2 to 8 words in a row: gone without a trace (45 %), marked `{?likely: …}` (40 %), or replaced by a plausible wrong phrase (15 %) | light 0.3 bursts a call, marked 3, heavy 8 | same | costs a level when it hits a check's line (sample 4) |
| R7 | Two at once | a backchannel said over the other is lost (50 %) or the neighbouring turns of one speaker join into one line (20 %) | 1.2 overlaps a minute | 1.5 | yes |
| R8 | Speakers swapped | a run of 2 to 4 short turns under the wrong role, never the first two lines unless heavy | light 3 % of calls, marked 15 %, heavy 35 % | same | a check whose only evidence is in the run comes out unverified or lower |
| R9 | Hold | the hold message or music as one or two lines under `manager` (35 %) or nothing (65 %) | 6 % of calls have a hold | 5 % | yes |
| R10 | Bad mobile line | the caller's sentence ends clipped; "hello? can you hear me" is in the script itself | 4 % of calls | 6 % | marked or heavy |
| R11 | Profanity | the customer's, in status and complaint calls; kept as said (60 %), softened to a near word (25 %), dropped (15 %). Staff never swear at a customer | 4 % of existing-job calls | 7 % | yes; tag `customer_angry` |
| R12 | Invented line | a stock phrase over silence at the end ("Thank you.") where a Whisper model is on | 1.5 % of calls | 0 | yes |

- **Word difference** between script and stored lines, digits counted as different from words. EN: light 12 % (8 to 16), marked 20 % (11 to 30), heavy 40 %; mean about 14 % (X). RU: light 14 % (8 to 18), marked 24 % (14 to 34), heavy 45 %; mean about 18 %, under the 24.3 % measured on real calls, whose references also miss speech.
- **`asr_quality`** is `poor` when a rule of kind R6, R8 or R10 lands on a line that holds a check's evidence, or when one line in seven or more carries a marker; every heavy call is poor. Else `ok`. Damage is placed so that 40 % of marked calls are poor: 9 % of judged calls (EN), 14 % (RU).
- **Truth beside verdict.** A call file keeps the levels the clean script earns (`truth`) and the levels the stored lines earn (`verdict`). They differ only where recognition took the evidence; that difference is planted, counted and an eval question in itself.
- **Days float.** A call's day is an anchor of design rule R6, as in `../stories/TIMELINE.md`: a working day of the advisor counted from T, a weekday of a named week, or a period of the junior's path; never a bare count of days. So a weekday said aloud cannot be typed. A call file lists each such word with its offset from the call's day and, in Russian, its form («в субботу», «к понедельнику»); the seeder renders it. Offsets count days the site is open.

## 5. Missed calls and the callback queue

- **A miss leaves**: the `interaction` (`answered_at` null, `disposition='no_answer'`), a `no_answer` or `busy` leg for every desk it rang, and a `missed_call` row in state `waiting` with `out_of_hours` set from the site's hours and exceptions. No recording, transcript or verdict.
- **It is resolved** by the first later call with the same number that a person answered: outbound makes it `called_back`, inbound `got_through`; unanswered calls back before it count as `attempts` (`call-pipeline.md:148-160`). The product recomputes this only for misses of the last 7 days, so the seeder applies the same rule over the whole history.
- **The queue** is the waiting, undismissed misses of the last 7 days whose first leg keeps a caller number (`B/ingestion/call_log.py:31`; `apps/backend/src/traciora/api/routes/calls.py:71-75`; `B/claims.py:31-35`). A claim is a card on the claimer's board from the "Missed call callback" template, `kind='follow_up'`, `origin_ref='calls:claim'`, the miss as its `interaction_id`; it lapses after 30 minutes and is completed or called off by the next read (`B/claims.py:27, 123-131`). A dismissal stamps `dismissed_at` and `dismissed_by`.
- **At T the queue holds** nine callers: four from today, five older, none with a live claim (a live claim would lapse half an hour after seeding). History holds completed and called-off claim cards: 35 % of misses that were called back went through a claim; 6 % of claims lapsed.
- **S3** is the miss chance by desk and hour, and the follow-up drawn per miss:

| `main`, weekday | Missed, first 2.5 h | Missed, rest of day | Called back or got through, median | Never |
|---|---:|---:|---:|---:|
| G to the fix (the Monday of week T-3) | 31 % | 8 % | 3 h 10 | 18 % |
| since the fix | 12 % | 8 % | 40 min | two named callers |

  Ledger: `calls.main.before.*`, `calls.main.since.*`, `calls.callback.main.before`, `calls.callback.main.after`. Two things of the first draft were too small to be rates and are planted as instances (design rule R7). "Never called back 5 %" since the fix would be read on about 30 misses: it is two named callers, missed between the fix and T-7 days and never called back. "Mondays 19 %" is the market's busiest weekday, Monday in the English configuration and Tuesday in the Russian: on its first three mornings since the fix seven named calls are missed, 19 % of 36 at full size, against about 10 % on the other mornings (`calls.busiest_mornings_since_fix`). A desk's rate is the shop's block rate times the desk's factor (`calls.desk.<ext>.<regime>.factor`); desk 103 misses 1.7 times the shop's rate (RU 1.65). Inside a Russian tyre window every rate is 1.25 times its row (`calls.season_miss_factor`).

  Elsewhere (X): `east` 45 min and 8 % never; `west` 4 h 30 and 30 % never (`calls.callback.east`, `calls.callback.west`). Of resolved misses, 70 % are `called_back`, 30 % `got_through`. The Car Wars figure "52 % do not call again" (dealers, read) bounds `got_through`.
- **S1.** A5's manager: an answered complaint call first, then three misses in nine days from the same number, and no answered call to or from that number afterwards, or the product's rule would mark them resolved. They stay `waiting` in the table and are found by a query; they are **not** on the To call back screen, which shows seven days. The complaint call is on the Tuesday of week T-19 and the misses 1, 6 and 9 calendar days after it (`s1.a5`).
- **S13.** Misses on the last holiday carry `out_of_hours = true` and are left out of every desk's rate.

## 6. Story calls and background calls

Written by hand, once per language (33 calls with text, three misses without). "No score" means the rubric gives none. Days are anchors of design rule R6, the same as on the cards and in `../stories/TIMELINE.md`; P1 to P6 are the junior's 30-day score periods counted from G; "(RU: on or after)" moves a weekday anchor to the advisor's first working day on or after it, because Russian advisors work two on, two off.

| # | Story | Slot | Day | Call | Verdict it must earn |
|---|---|---|---|---|---|
| 1 | S4 | 6 | a working day of hers in P1 | price given, caller let go (sample 1) | 40.0; `customer_will_call`; try next: offered time |
| 2 | S4 | 6 | in P2 | asks "when would suit you", caller pauses | 50 to 56; time 1, booking 1 |
| 3 | S4 | 6 | in P3 | caller names the time himself; no name taken, no summary | 59 to 64; `visit_agreed` |
| 4 | S4 | 6 | in P4 | one time offered, booked, summary without the address | 66 to 70 |
| 5 | S4 | 6 | in P5 | two times before the price, full summary, no doubt voiced | 85 to 94 |
| 6 | S4 | 6 | in P6 | booked, a doubt stepped over (sample 2) | 71.9; `price_objection` |
| 7 | S4 | 6 | her 2nd working day before T | a company driver says "go ahead" to 380 USD (RU 9,500 RUB) of found work, over the limit of 300 USD (8,000 RUB) | scored; no auto-fail; the wrinkle is the rule in her note |
| 8 | S7 | 6 | day A of S7: her 14th working day before T (RU: her 10th) | she rings to confirm the booking | outbound: not judged |
| 9 | S8 | 7 | slot 7's 5th working day before T | timing belt at the old price (688 USD against 720; RU 15,552 against 16,000), "same day" | 31.25 (10 of 32 points); `wrong_promise`; `visit_agreed` |
| 10 | S8 | 5 | the day the car is ready: the next full open day after slot 7's 4th working day before T on which slot 5 works | the customer's complaint | `existing_job`: no score; greeting 2, recap 2; `complaint`, `customer_angry`; `callback_promised`, kept inside 24 h |
| 11 | S8 | 4 | slot 4's next working day | the senior rings back, 80 USD off (RU 1,800 RUB) | outbound: not judged |
| 12 | S12 | 7 | the Tuesday of week T-5 | brake job priced from the stale page (475 USD against 493; RU 12,268 against 12,520) | about 40; `wrong_promise` (his second) |
| 13, 14 | people | 7 | the Wednesday of week T-10; his 3rd working day before T | his first weeks; improving | about 35; about 56 |
| 15 | S6 | 23 | `west`'s 4th full open day before T | a day promised with nothing behind it, added work not taken (sample 3) | 25.0; `wrong_promise`; `customer_angry` |
| 16 | S6 | 23 | `west`'s last full open day before T | the same customer after a missed call that morning; he is unclear and is not asked again (design rule R13) | `existing_job`: no score; `repeat_caller`, `complaint`; `customer_will_call` |
| 17 | S1 | 22 | the Tuesday of week T-19 | A5's manager on the two comebacks and the bill | no score; `complaint`, `warranty`; `callback_promised`, then `callback_not_kept` |
| 18 to 20 | S1 | `west`, first desks 302, 303, 302 | 1, 6 and 9 calendar days after call 17 | A5's three misses | no text; `waiting` |
| 21, 22 | S1 | 5, 7 | the Tuesday of week T-20; the Tuesday of week T-9 | A6's new contact asks why the price rose, and it takes two questions to learn which van and what job (design rule R13); a quote promised and sent two days late | about 75, `price_objection`; about 45, `callback_not_kept` |
| 23, 24 | S1 | 6 | the Wednesdays of weeks T-17 and T-4 | A1 van booked without the order number; with it asked first | about 60; about 80 |
| 25 | S5, S1 | 16 | the Wednesday of week T-2 (RU: on or after) | A2 van booked; recognition damage (sample 4) | 83.3 on the lines, 100 in truth; `asr_quality: poor` |
| 26, 27 | S5 | 16 | the Mondays of weeks T-8 and T-3 (RU: on or after) | a price doubt answered in full; a regular asks for her | 93.8 or 100; both `visit_agreed` |
| 28 | S5 | 17 | the Monday of week T-6, a day slot 16 is off (RU: slot 17's 12th working day before T) | her day off: "is she in?" | about 55 |
| 29, 30 | people | 5, 6 | the Fridays of weeks T-10 and T-3 (RU: on or after) | two customers about mechanic 11's rushed work | no score; `complaint`; one `customer_angry` |
| 31 | S3 | 5 | the Monday of week T-6, 08:10 (RU 09:40) | "I rang three times this morning" | scored; `repeat_caller` |
| 32 | S3 | 6 | slot 6's 8th working day before T, 07:40 (RU 09:10), ten minutes after opening | the early desk answers at once | about 80 |
| 33, 34 | people | 22 | the Thursday of week T-7; the Monday of week T-2 | first-name terms, "just bring it by" | about 45; about 50 |
| 35, 36 | people | 24 | the Tuesday of week T-21; the Friday of week T-2 (RU: on or after) | the bright spot, then firmer | about 62; about 81 |

**Background calls** are assembled from patterns. At full size one configuration holds 9,336 inbound calls in opening hours (EN, 2.0 an order) or 11,195 (RU, 2.2 an order), 8,094 and 9,405 of them answered, plus 5,576 and 7,791 outbound (`calls.inbound_per_order`, `calls.inbound_product_period`, `calls.answered_product_period`, `calls.outbound_product_period`). Of the answered customer calls 12 % carry a clarification loop and 2 % end unclear (design rule R13: `r13.calls.clarification_loop`, `r13.calls.unresolved`). A reader sees one person's day, 12 to 15 calls, so no two calls of a type in a day may share a skeleton: with 6 of a type a day that needs 75 or more combinations per type.

| Piece | Count per language | Gives |
|---|---:|---|
| new-enquiry skeletons (who leads, where the doubt falls, how it ends) | 14 | × 24 job blocks = 336 |
| job blocks (the questions, the price and what it depends on, for the 24 jobs people phone about) | 24 | |
| existing-job skeletons (ready, not ready, part late, extra work, booking moved, pick-up, bill, complaint, comeback, lost item) × 3 | 30 | |
| supplier 8, wrong number 5, other 6, outbound 10 | 29 | |
| customer voices (terse, chatty, anxious, price-shopper, elderly, driver, dispatcher, angry) | 8 | × every skeleton |
| unclear openings (vague, the wrong thing named, two requests in one, the wrong way round), each with the caller's second and third answer and the advisor's second question at levels 0, 1 and 2 | 20 | design rule R13: laid over any new-enquiry or existing-job skeleton, in 12 % of customer calls; in one in six of them the request stays unclear |
| advisor phrase bank: 9 advisors (slots 5, 6, 7, 29, 16, 17, 22, 23, 24) × 8 checks × 3 levels × 4 wordings, plus greetings and closings | about 900 lines | the person's voice |

Each language's banks are written in that language from nothing. The 33 story calls, four of them the samples here, set their tone.

## 7. File format for a hand-written call

One JSON file per call and language, `format: "seed-call/1"`; the eight files in `samples/` are the reference for the format. The story calls in `en/` and `ru/` are the source of their content. `_generators/ru` and the samples `ru-2` and `ru-3` are behind them, as they predate fix pass B, and nothing reads them as content.

| Key | Holds |
|---|---|
| `call` | `day` (an anchor of design rule R6, with `nominal_date` for the T the text was written for), local start, site, direction, line (the site's group line), answering desk, ring and talk seconds, caller's number, `repeat_caller` |
| `cast`, `scenario` | slots and names; who calls, the car, the job, what they want, what happens, the facts the speech rests on (prices, dates) |
| `floating_days` | every weekday word in the text with its offset from the call's day and, in Russian, its form |
| `script` | the clean speech: `n`, `who`, `at_s` (seconds from the answer), `said`, `overlap` |
| `recognition` | profile, consensus, tier, and every rule applied with the turn, what was said and what was stored |
| `transcript` | `engine`, `engine_version`, `language`, `pii_state`, and `segments` in the product's shape: `sequence`, `speaker_label`, `start_ms` and `end_ms` (null), `text`, `confidence` (null) |
| `judge_answer` | the judge's JSON answer as `scorecard_judge_prompt.txt` asks for it, with quotes |
| `verdict` | `result_public` and the plain form of `result_enc`, derived from `judge_answer` by `judge.verdict`; `score` |
| `truth` | the levels and the score the clean script earns |
| `why` | one line per check, and the two checks that carry the score |

Timing lives on the script (`at_s`); the stored lines have none because the product's have none. `scorecard`, `weights`, `prompt_version` and the restoration fingerprint are computed by the product's functions when the seed is built.

## 8. Ledger rows proposed

Merged: the ledger's decision on each row is in `ledger.json` under `proposed.calls.*` and in the rows named there. Where the ledger adjusted a row the table below carries the ledger's value.

| Key | English | Russian | Class | Basis |
|---|---|---|---|---|
| call types, share of answered inbound | 72 / 20 / 4 / 1.5 / 2.5 | 62 / 28 / 5 / 2 / 3 | X on M | section 2; EN split read on Auto Service World 2026 |
| reasons inside the types | table in section 2 | same | X | accepted ± 5 points a row |
| talk time and turns by reason | table in section 2 | same | X; RU on M | real recordings: 119 s a recording, 207 words a call, 1.74 words a second |
| words a second of talk | 2.1 | 1.75 | X / M | same |
| outbound calls per order | 1.2 | 1.6 | X | approval by phone 28 % of estimates in EN (MOTOR 2026, 14 shops, read); range 0.8 to 2 |
| outbound answered | 70 % | 70 % | X | range 60 to 80 |
| customer known, of new enquiries | 35 % | 35 % | X | 73 % of owners call their customers repeat (AutoZone 2025, read); range 25 to 45 |
| price asked, of new enquiries | 60 % | 60 % | D / X | EN: (30 + a third of bookings + 5) ÷ 72; RU set equal so one sheet serves both |
| time named first or no visit needed | 15 % | 15 % | X | range 10 to 25 |
| doubt voiced | 45 % | 45 % | X | range 35 to 55 |
| booking level 2 that is a visit | 92 % | 92 % | X | makes S4's 46 % and 58 % |
| a step agreed at booking level 1 | 50 % | 50 % | X | |
| time and booking at the same rank | 70 % of calls | same | X | a call with no next step fails both |
| style sheets | table in section 3 | same | X | characters of design 1.4.1; expected within 0.2 of the ledger |
| monthly scores | 6: 58, 61, 63, 67, 70, 72 · 24: 66, 67, 69, 70, 72, 74 · 7: 41, 44, 47 | same | design S4 / X | ledger `p06.score_path`, `p24.score_path`, `p07.score_path` |
| a month's mean against its target | ± 0.5 full size, ± 1.5 small | same | X | levels dealt by share |
| auto-fail shares by person | section 3 | same | X; company callbacks on M | CallRevu 22.4 % |
| recognisers on | parakeet, faster_whisper | tone, gigaam | X | RU pair measured |
| recognition profiles | 80 / 15 / 3 / 2 | 72 / 20 / 6 / 2 | X / X on M | error audit |
| rules R1 to R12 | section 4 | section 4 | X | each rate accepted within half to double |
| word difference by profile | 12 / 20 / 40 % | 14 / 24 / 45 % | X; RU bounded by M | 24.3 % measured after restoration |
| `asr_quality: poor`, of judged calls | 9 % | 14 % | D | heavy + 40 % of marked |
| desks and lines | group lines 100 (`main`), 200 (`east`), 300 (`west`), as `tenant/roles-and-places.<cfg>.json`; desks 101, 102, 103, 105; 201, 202; 301, 302, 303; 304 until F1 was fired | same | X | three-digit extensions, the product's default; adjusted by the ledger for slot 29 and F1 |
| ring plan | one desk 20 s, then all 15 s | same | X | |
| answered at `west` by 22 / 23 / 24 | 15 / 47 / 38 % | 15 / 45 / 40 % | X | 22 "answers the phone" |
| follow-up of a miss outside S3 | `east` 45 min, 8 % never; `west` 4 h 30, 30 % never | same | X | |
| resolved misses called back / got through | 70 / 30 % | same | X | |
| claims | 35 % of called-back misses; 6 % lapse | same | X | |
| queue at T | 9 waiting: 4 today, 5 older | same | X | |
| calls with a hold; bad line; profanity | 6 %; 4 %; 4 % of existing-job calls | 5 %; 6 %; 7 % | X | |
| hand-written calls | 33 with text, 3 without | same | X | section 6 |
| inbound calls in opening hours per order | 2.0 | 2.2 | X | the first draft's Russian 1.4 counted enquiry calls only |
| unclear customers (design rule R13) | 12 % with a loop, 2 % left unclear | same | X | owner, 2026-11-13 |
| pattern counts | section 6 | same | X | 75 combinations a type a day at least |
| day reports written | last 14 days and story days | same | X | proposal |

## Settled since the draft

1. **Scores the rubric cannot give.** The cards dropped them: S7's confirming call is outbound and unjudged, S8's complaint call is an `existing_job` call with two checks and no score (`s8.quote_call_score` is the quote call's). The weak desk's S6 call 15 carries a score because the customer also asks for new work (sample 3).
2. **Sample 1 cannot be in the high 50s.** It earns 40.0; her first-period mean of 58 comes from the mix (`p06.score_path`).
3. **The queue shows seven days.** A5's three misses stay `waiting` in the table and are not on the To call back screen; the cards ask for them by a query (S1.5).
4. **Per-person attribution.** The seed writes `person_id` itself with `attributed_by='pbx_extension'`, one desk per advisor (design rule R8). A miss has no person: its rate is its first desk's.
5. **Missed shares add up.** The ledger has one model: the chance of a miss by desk and block (`calls.desk.*`), closing to 13.3 % (EN) and 15.99 % (RU) for the company (`calls.company.miss_w90`).
6. **Russian calls per order** are 2.2 in opening hours (`calls.inbound_per_order`); 1.4 counted enquiry calls only.
7. **Slots 24, 7 and 29** have their rows (`p24.score_path`, `p07.score_path`, `p29.check.*`).
8. **Names in the samples.** The samples carry the seed's people, companies, cars, plates, phones and prices: the cast (`cast.json`), account A2 (`accounts.json`), the S6 customer (`named_customers.json`) and `catalogue.json`. A Nashville caller has a 615 number.

## Not in this plan

- A call for S2 (a `west` customer asking for "the cash discount the other guy gave"). Fits the story; not in its footprints.
- Speaker identification, audio files, a Russian wording of the scorecard, day-report texts.
