# English call bank: format

The pieces from which the generator assembles the English background calls (`../DESIGN.md` sections 2, 3 and 6). Every line here is clean speech: the recognition model of section 4 is applied by the generator afterwards. The 33 story calls in `../en/` set the register; nothing here names a story's customer, dispute or date.

Check: `python3 ../../checks/check_bank_en.py` (output `../../checks/bank_en_check.txt`, sample `assembled-sample.md`).

## Files

| File | Holds |
|---|---|
| `skeletons-new-enquiry.json` | 14 skeletons of a first-time enquiry: who leads, where the doubt falls, how it ends |
| `job-blocks.json` | 24 job blocks (the jobs people phone about) and the generic time and think-it-over objections |
| `skeletons-existing-job.json` | 30 skeletons: ten kinds, three each |
| `skeletons-other.json` | supplier 8, wrong number 5, other 6, outbound 10 |
| `voices.json` | 8 customer voices |
| `unclear.json` | 20 unclear openings (design rule R13) |
| `advisors/<slot>.json` | the phrase bank of each of the nine advisors who answer phones |

## Lines

- A line is a JSON string of speech. Restarts and interruptions are written `I — I`, a trailing-off or a pause `...`. Nobody speaks in written sentences.
- Slots are written `{name}`. Every slot is in the table below; the check fails on any other.
- **No digits anywhere outside a slot.** No price, clock time, duration, weekday, month or date is typed: they are slots, rendered as speech by the generator (`four ninety-three`, `Thursday at eight`). Relative words that are always true on the call's day (`today`, `this morning`, `this afternoon`, `tonight`, `this week`, `yesterday`, `last week`) may be typed. `tomorrow`, weekday names and month names may not: they float (rule R6 of the seed design) and come from a slot.
- A line may be capitalised in the middle of a sentence after a slot is filled; the generator fixes capitals after `.`, `?`, `!` and at the start of a line.
- `"<skip>"` as a wording means the advisor says nothing at that beat (a level-0 absence).

## Slots

Where each value comes from: **cast** = `../../cast.json`; **catalogue** = `../../catalogue.json` (price on the call's day by its `price_history` rule, for the car's class and the parts tier); **parc** = `../../parc.json`; **accounts** = `../../accounts.json`; **vendors** = `../../vendors.json`; **ledger** = `../../ledger.json`; **scenario** = drawn by the generator for the call; **advisor** = the answering advisor's file here; **job** = the call's job block here. Money, times and numbers are rendered as speech.

| Slot | Value | Source |
|---|---|---|
| `{advisor_first}` | the answering advisor's first name | cast `en.customers_call` |
| `{shop_address}` | the site's address said aloud: `twenty-one-oh-six East Main Street`, `sixty-three-forty Bonny Oaks Drive`, `sixty-three-ninety-nine Charlotte Pike` | ledger `geo.address.*` |
| `{shop_short}` | `East Main`, `Bonny Oaks`, `Charlotte Pike` | ledger `geo.short_name` |
| `{shop_hours}` | weekday hours said aloud, `seven-thirty to five-thirty` | ledger `site.hours.weekday` |
| `{closing_time}` | closing hour said aloud, `five-thirty` | ledger `site.hours.weekday` |
| `{tech_name}` | first name of a technician at the site; never slot 11 in a complaint or comeback skeleton | cast |
| `{manager_name}` | `Greg` at `main` and `east`; `Dale` at `west` (never in Dale's own lines) | cast slots 4, 22 |
| `{other_advisor}` | first name of another advisor on duty at the site | cast |
| `{sir_maam}` | `sir` or `ma'am` by the caller's sex | scenario |
| `{customer_first}`, `{customer_last}` | the caller's names (invented, or a seed customer's) | scenario |
| `{customer_title}` | `Mr. Boyd`, `Ms. Kessler` | scenario |
| `{customer_phone_said}` | the caller's number in words, `four two three, five five five, oh one seven four` (423 at the Chattanooga shops, 615 at `west`; the 555-01xx block) | scenario |
| `{customer_email_said}` | an e-mail address said aloud | scenario |
| `{car_year_said}`, `{car_year_short}` | `twenty-fifteen`, `fifteen` | parc (model years) |
| `{car_make}`, `{car_model}` | `Toyota`, `Camry` | parc |
| `{company_name}` | a company account's name as its people say it | accounts |
| `{unit}` | the unit as the account says it, `unit one-twelve`, `number eight` | accounts fleet |
| `{plate_tail_said}` | last four of the plate in words | accounts fleet |
| `{po_said}` | a purchase-order number in words | scenario (accounts that use them) |
| `{boss_first}` | first name of the account's fleet contact (driver voice) | accounts contacts |
| `{need}` | the customer's own words for the need (one of the job's `customer_says`) | job |
| `{job_said}` | the job as a shop says it | job `job_said` |
| `{job_question}`, `{job_answer}` | an advisor's discovery question and the caller's answer to it | job `questions` |
| `{since_answer}` | how long it has been going on, in the caller's words | job `since_answers` |
| `{job_explain}` | what the trouble probably is, in the advisor's words | job `explain` |
| `{price_statement}` | the price said as a clause, itself carrying `{price}` or `{price_alt}` | job `price_statement` |
| `{depends}` | what the price depends on, a sentence | job `depends` |
| `{inspection_line}` | why only an inspection sets the exact price, with `{inspection_price}` or `{price}` | job `inspection_line` |
| `{price}` | the job's list price, before tax | catalogue: the job's `catalogue.price` key |
| `{price_alt}` | the cheaper alternative's price | catalogue: `catalogue.price_alt` |
| `{inspection_price}` | the inspection or test that sets the price | catalogue: `catalogue.inspection_price`; `no charge` when it is 0 |
| `{price_otd}` | `{price}` with shop supplies and sales tax | catalogue, ledger tax rate |
| `{job_duration}` | how long the job takes, `an hour and a half` (no "about") | catalogue hours |
| `{objection_probe}`, `{objection_answer}` | the advisor's question about a doubt and the level-2 answer | job `objections` or `generic_objections` |
| `{competitor_price}`, `{competitor_place}` | a lower quote the caller heard and where (`a place out by my work`; never a named business) | scenario |
| `{warranty}` | `twenty-four months or twenty-four thousand miles` | ledger `s12.warranty.current` |
| `{second_need}`, `{second_job_said}`, `{second_price}` | a second job block's wording, name and price (skeleton NE13) | job (a second block) |
| `{time_1}`, `{time_2}` | two open slots, day and hour said aloud, `tomorrow at eight`, `Thursday at one-thirty` | scenario (the site's open days and hours) |
| `{time_chosen}` | the slot agreed: `{time_1}`, `{time_2}` or one the caller named | scenario |
| `{old_time}` | an appointment already on the book | scenario |
| `{ready_time}` | when the car will be done, with its own preposition: `by four`, `around three`, `after lunch` | scenario |
| `{callback_time}` | when someone calls back, with its own preposition: `before noon`, `by two`, `this afternoon` | scenario |
| `{drop_day}` | the day the car was dropped off, `Tuesday` | scenario |
| `{part_name}`, `{part_eta}` | the part waited on and when it is due | catalogue parts; scenario |
| `{found_job_said}`, `{found_reason}`, `{found_price}` | work found on inspection: its name, what was seen, its price | job (another block's `job_said` and `found`); catalogue |
| `{bill_total}`, `{bill_line}` | the bill out the door; one line of it | scenario from catalogue |
| `{lost_item}` | an item left in or missing from a car | scenario |
| `{vendor_name}`, `{vendor_rep}`, `{delivery_window}`, `{order_ref_said}` | supplier, its caller's first name, a delivery run, an order or invoice number in words | vendors; scenario |
| `{tow_name}` | the towing partner as staff say it, `Mowbray` | vendors V8 |
| `{asked_for}` | who or what a wrong-number caller wanted | scenario |
| `{a_ok}`, `{a_yes}`, `{a_sorry}` | the advisor's own acknowledgement, agreement and apology words | advisor `tokens` |

Slots nest one level: a job field put into an advisor's wording may carry `{price}`, `{car_model}` and the like, which are filled in a second pass.

## Skeletons (`skeletons-*.json`)

```json
{"id": "NE01", "kind": "new_enquiry", "title": "...", "leads": "advisor", "doubt": null,
 "fits": {"price_asked": true, "doubt": false, "known": null, "ot_na": false, "booking": [0, 1, 2]},
 "job_filter": null, "voice_filter": null, "turns": "20-28",
 "beats": [{"who": "A", "role": "greeting", "check": "greeting"}, {"who": "C", "role": "open"}, ...]}
```

- `who`: `A` advisor, `C` customer (or the other party: a supplier's rep, a wrong-number caller), `H` hold (one line `[on hold]`, which the generator writes under `manager` in 35 % of holds and drops otherwise, rule R9).
- `check`: the rubric check an advisor's line can serve; its level is the call's dealt level.
- `fits`: the scenario a skeleton can carry. `null` = either. `booking` lists the `asked_for_booking` levels it ends correctly with.
- `when`: a condition; the beat is dropped when false. Terms joined by `and` / `or`: a flag (`price_asked`, `doubt`, `known`, `ot_na`, `booked` = booking at level 2, `agreed` = something agreed, `unclear`, `prev_said` = the advisor's beat just before was not skipped) or `not <flag>`, or `L.<check> <op> <n>` on a dealt level.
- `p`: chance the beat (or its `group`) is kept. Beats sharing a `group` are kept or dropped together.
- `say`: the line written in the skeleton. For a customer or other party a list of variants. For an advisor an object by tier, `{"exact": [...], "warm": [...], "curt": [...]}`; a tier's list may be `["<skip>"]`. The advisor's `tier` picks the list; their `tokens` fill `{a_ok}`, `{a_yes}`, `{a_sorry}`.
- `doubt`: which objection type the skeleton's doubt beat takes (`price`, `time`, `trust`, `think`). A price doubt needs a price said: when the price was not asked or was not given (level 0) the doubt becomes `think`. A doubt about the offered times needs a time offered: with none, a generic time doubt about getting there is taken.
- `weight`: relative chance of a new-enquiry skeleton among those that fit the scenario (default 1).
- `pair: "prev"`: an advisor `say` whose variants answer the caller's variants of the `say` just before, by position.
- `force: "pick_of_two"` on `respond_offer`: the caller picks a time; two offered in the advisor's last line give `pick_of_two`, one gives `accept_one`, none gives `name_own_time`.
- `outcome`: for new enquiries the outcome follows the booking level (DESIGN.md section 2); other kinds state `type` and `outcome`.
- Existing-job skeletons also carry `agreed` (recap applies), `agreed_time` (what `{time_chosen}` is: `{ready_time}` for a car not ready, a fixed phrase for a morning pick-up; else a pick-up time the scenario draws) and `recap_kind: "callback"`, which takes the recap from the file's `callback_recap` (who calls, when, about what) and closes with `closing_open`.

### Advisor roles (`who: A`)

| Role | Text from | Dropped when |
|---|---|---|
| `greeting` | `checks.greeting[L]`; at level 2 also the advisor's `greetings` list (60 %) | |
| `recognise` | `moves.recognise` | not `known` |
| `ack`, `ask_what`, `lookup`, `explain`, `duration`, `outbound_open` | `moves.<role>` (`explain` takes `{job_explain}`) | |
| `ask_car` | `checks.need_discovery["1"]`, or `["0"]` when L.need = 0 | `known` |
| `ask_more` | `checks.need_discovery["2"]`; for a job with `symptom: false` only wordings carrying `{job_question}` ("how long has it been doing that" does not fit an oil change) | L.need < 2, or an unclear opening was resolved at level 2 (its second question is the evidence) |
| `price` | `checks.price_with_next_step[L]`; `price_mode: "inspection"` prefers a wording with `{inspection_line}`; when a time is already agreed the wording's closing offer is dropped (the agreed time is the step) | not `price_asked` |
| `offer_time` | `checks.offered_time[L]` | `ot_na` |
| `probe` | `moves.probe` with the objection's probe | not `doubt`, or L.objection < 2 |
| `objection` | `checks.objection[L]` with `{objection_answer}`; at levels 0 and 1 the objection's own `answer_0` / `answer_1` in 60 % of calls, always for `time` and `think` doubts (the advisors' general phrases speak of price and warranty) | not `doubt` |
| `booking` | `checks.asked_for_booking[L]`; at level 0 with the name still to be taken, a wording without a goodbye | |
| `ask_name`, `ask_number` | `moves.ask_name`, `moves.ask_number` | `known`, or L.name = 0 |
| `confirm_number` | `checks.name_and_number[L]`; at level 0 only when booked, unless `<skip>` | `known` |
| `recap` | `checks.recap[L]` (every wording names the agreed time) | recap does not apply: nothing agreed. DESIGN.md section 3 lets recap apply to half of booking-level-1 calls (a step with no date); these wordings carry a dated booking, so a level-1 call is given no recap |
| `hold` | `moves.hold`, then an `H` line, then `moves.back_from_hold` | |
| `closing` | `moves.closing_booked` when something was agreed, else `moves.closing_open` | |
| `say` | the skeleton's tiered text | |

### Customer roles (`who: C`)

| Role | Text from |
|---|---|
| `open` | voice `open_price` (price asked) or `open_booking`, with `{need}`; when L.need = 0 a `vague` wording of the job |
| `give_car` | voice `give_car` (dropped when L.need = 0 or known) |
| `answer` | the job's answer to the question just asked (`{job_answer}`), or `{since_answer}` when the advisor asked how long; voice `filler` before it at the voice's rate (dropped when L.need < 2) |
| `react_price` | voice `react_price`, or `react_no_price` when L.price = 0 |
| `name_time_first` | voice `name_own_time` |
| `respond_offer` | booked: voice `pick_of_two` (two times offered), `accept_one` (one), `name_own_time` (none, or "when suits"); booking 1: voice `pause`; booking 0: voice `will_call` |
| `after_booking` | voice `decline` when booking = 1, else dropped |
| `doubt` | the objection's `customer` line (job or generic), voice filler before it |
| `probe_reply` | the objection's `probe_reply` (only when L.objection = 2) |
| `after_objection` | voice `after_answer_ok` when booking ≥ 1 and the doubt was answered (level 2; half of level 1), else `after_answer_unsure` |
| `give_name`, `give_number`, `ask_duration`, `thanks_bye`, `backchannel`, `yes`, `no`, `maybe` | voice lists |
| `say` | the skeleton's variants, voice `opener` before the caller's first line, else voice `filler` at the voice's rate; voice `tail` only on the first line, an `answer` and a `doubt` |

### Spoken variation and consistency (the generator's rules; the sample assembler in the check applies them)

- **Discourse word.** A generic line (an advisor's check wording or move, a voice line) takes, at the speaker's rate (advisor 0.5, 0.15 right after their own line; caller the voice's `filler_rate`), one of the speaker's own `fillers` before it; a line that already opens with a discourse word (okay, alright, so, well, yeah, uh, gotcha…) has it swapped for another of the speaker's or dropped. Never on lines of three words or fewer.
- **Address.** An advisor adds one of their `address` terms before the line's last stop (0.35; a customer's name at most twice a call, only once the name is known; `hon` and `buddy` only to a known customer). A caller who heard the advisor's name may use it once.
- **Echo.** Before the first car question an advisor may say the job back ("Front brakes, okay."): 0.5, curt advisors 0.2.
- **Greeting.** Level 2 may take "Good morning," or "Good afternoon," before it (not curt advisors, not a greeting that names the time of day); a greeting ending in a statement takes one of the advisor's `greeting_tails`.
- **The name is not used before it is given.** Until the caller gives a name (or is known), wordings with `{customer_first}`, `{customer_last}`, `{customer_title}` are not drawn.
- **Words follow the caller.** A caller's "husband" or "wife" follows the caller's sex; a company caller's "my car" is "the van"; "the {job_said}" drops the job's own article.
- **One line per turn.** Back-to-back lines of one speaker are one stored line, as the product stores them.

## Job blocks (`job-blocks.json`)

```json
{"key": "front_brakes", "catalogue": {"price": "front_pads_rotors", "price_alt": "front_brake_pads", "inspection_price": "brake_inspection"},
 "lead_share": 0.0749, "vehicle_classes": ["car", "suv", "truck", "van"],
 "job_said": [...], "customer_says": [{"kind": "accurate|vague|wrong", "need": "..."}],
 "questions": [{"q": "...", "answers": [...]}], "since_answers": [...], "explain": [...],
 "price_statement": [...], "depends": [...], "inspection_line": "... or null",
 "objections": [{"type": "price|trust|time|think", "customer": [...], "probe": "...", "probe_reply": [...],
                 "answer_2": "...", "answer_1": "...", "answer_0": "..."}],
 "found": "what a tech sees when this work turns up on another job, or null",
 "symptom": true}
```

`symptom: false` marks maintenance and purchase jobs (oil service, scheduled maintenance, fleet PM, pre-purchase, tires), where no symptom is asked about. `customer_says` and `questions` are lower-case clauses with no final stop, so a voice frame or an advisor wording can carry them. `answer_2` finds out the doubt's reason and answers it (rubric level 2), `answer_1` is a general phrase (level 1), `answer_0` steps over it (level 0). A skeleton whose doubt type the job lacks takes `generic_objections.<type>`.

## Voices (`voices.json`)

Each voice has: `about`; `filler_rate` and `tail_rate`; and lists for every customer role above plus `opener`, `filler`, `tail`. A role is a list of wordings, or `{"parts": [[...], [...]]}`: one piece from each part joined by a space (an empty piece allowed), used for the lines every call has (goodbyes, "let me check my week", "I'll call y'all back") so they do not repeat. A voice applied to any skeleton changes every customer line: generic lines come wholly from the voice; written lines take its opener, filler or tail.

## Unclear openings (`unclear.json`)

```json
{"id": "U01", "kind": "vague|wrong_thing|two_in_one|wrong_way_round", "applies_to": ["new_enquiry", "existing_job"],
 "resolves_to": "need | <job key>", "job_filter": [...] or null, "existing_fits": [existing-job kinds or skeleton ids],
 "opening": [...], "second_answer": [...],
 "advisor_second": {"0": "...", "1": "...", "2": "..."},
 "third_answer": {"0": [...], "1": [...], "2": [...]}, "unresolved_end": [...]}
```

Laid over a skeleton in 12 % of customer calls (DESIGN.md section 2): it replaces the caller's opening with `opening`, the advisor's `moves.ask_what`, `second_answer`, `advisor_second` at the call's dealt `need_discovery` level, and `third_answer` at that level; then the skeleton goes on. `resolves_to: need` means the third answer carries the job's `{need}` (on an existing-job call, the skeleton's own first line); a job key means the call's job is that one. `job_filter` limits an opening to jobs it can lead to; `existing_fits` names the existing-job kinds or skeletons it can open. In one of six such calls (2 % of customer calls) the request stays unclear: the call jumps to `asked_for_booking` at 0 or 1, the caller's `unresolved_end`, and the closing.

## Advisor files (`advisors/<slot>.json`)

```json
{"slot": 6, "name": "Maya Torres", "site": "main", "tier": "warm", "style_sheet": {...},
 "habits": [...], "fillers": [...], "tokens": {"a_ok": [...], "a_yes": [...], "a_sorry": [...]},
 "greeting_tails": [...], "address": [...], "greetings": [...],
 "checks": {"greeting": {"0": [4], "1": [4], "2": [4]}, ... eight checks},
 "moves": {"ack": [...], "ask_what": [...], "ask_name": [...], "ask_number": [...], "recognise": [...], "lookup": [...],
           "hold": [...], "back_from_hold": [...], "explain": [...], "duration": [...], "probe": [...],
           "outbound_open": [...], "closing_booked": [...], "closing_open": [...]}}
```

- `checks.greeting["2"]` and `greetings` are the person's greetings (all name the business and the person: level 2); `moves.closing_*` the closings; `moves.hold` the hold lines.
- `style_sheet`: the chances of level 0 / 1 / 2 per check from DESIGN.md section 3 (slots 6 and 24 carry `first` and `last`).
- What each level must earn, by the rubric's own words (`config/defaults/phonecalls_scorecard.json`): greeting 2 = the business and their own name in the first line; name 2 = name and number taken and the number said back (the wording at this beat is the say-back); need 1 = the car asked and no more, need 2 = a circumstance asked after the car; price 2 = a price or the inspection that sets it, what it depends on, and a step; offered time 2 = two day-and-hour options, 1 = one option or "when suits"; booking 2 = the booking with the time and who takes it; recap 2 = time, address and work, 1 = part of it; objection 2 = the doubt's reason found and answered (with the `probe` beat before it), 1 = a general phrase, 0 = stepped over.
- `tier` (`exact`, `warm`, `curt`) chooses the tiered text of existing-job, other and outbound skeletons.
- No advisor line repeats another advisor's, ignoring case and punctuation.
