# English conversation bank: format

The bank a generator assembles background chats from (`../DESIGN.md` sections 4 and 5). English configuration only. Every file is JSON with a `format` key `bank-en/<file>/1`. Check: `../../checks/check_conv_bank_en.py`, output `../../checks/conv_bank_en_check.txt`, sample `assembled-sample.md`.

## Files

| File | Holds | Section 5 piece |
|---|---|---|
| `reasons.json` | per reason and channel, skeletons: ordered beats, each with message alternatives or a pool to draw from | skeletons (8 for price, booking, status, symptom; 5 for the other six; per channel the reason occurs on) |
| `customer-messages.json` | 24 job blocks; 8 customer voices; the picture pool and voice stubs; per reason at least ten openings and the turns that follow; generic follow-ups, nudges and closings | job blocks, customer voices, picture pool |
| `assistant.json` | what the assistant sends on the web chat (moves × wordings, each line carrying the public page it rests on); greetings; the hand-off notes; the drafts it writes on Telegram and on an owned web chat | assistant bank |
| `advisors/<slot>.json` | nine advisors: pick-up, replies per reason, the twelve moves, draft edits (draft, what was sent, outcome), sign-off, private notes | advisor bank |
| `unclear.json` | twenty R13 loops: opening, second and third customer message, the clarifying question at three levels, three endings | unclear openings |
| `labels-and-notes.json` | thirty private notes between staff, label use, priority changes | private notes |

## Slots

Written `{name}`. Nothing else in a bank text holds a digit (the one exception: `1.` and `2.` starting a line of a numbered list): no price, hour, date, mileage, phone or unit number is typed; the generator fills them. A slot's value is chosen once per conversation, so `{time_a}` is the same time in every line of one chat.

| Slot | Value | Source |
|---|---|---|
| `first_name`, `last_name`, `full_name` | the customer | generator's scenario: an invented customer, never one of `named_customers.json`, never a real person |
| `name_typed` | the name as the customer types it (`kim ledford`, `Kim`, `KIM L`) | scenario, from the customer's name |
| `phone_typed` | the customer's number as typed (`423 555 0274`, `4235550274`, `(423)555-0274`) | scenario, `phones.md` tier B |
| `phone` | the customer's number as staff write it (`(423) 555-0274`) | scenario, from `phone_typed` |
| `sir_maam` | `sir` or `ma'am`, as the customer reads | scenario |
| `customer_words` | the customer's own words, quoted in the hand-off note | the conversation's first customer line |
| `car` | the car as staff write it (`2014 Honda CR-V`) | `parc.json` model and year |
| `model` | the model as staff say it (`CR-V`) | `parc.json` |
| `car_said` | the car as a customer types it (`2014 crv`, `the silverado`, `my tahoe`) | `parc.json`, lower-cased and shortened by the generator |
| `mileage_said` | the miles as typed (`120k`, `98,000`) | scenario, from the car's age |
| `job` | the job in staff chat words | job block `staff_says` (`customer-messages.json`), catalogue key |
| `job_said` | the job in the customer's words | job block `said` |
| `symptom_said` | what the car does, in the customer's words | job block `symptom_said` |
| `photo` | a picture's pool key; the message carries the file | `customer-messages.json` `pictures`, or the job block's `photo` |
| `voice_len` | seconds of a voice message | `customer-messages.json` `voice_stubs` |
| `shop` | the shop's short name (`East Main`, `Bonny Oaks`, `Charlotte Pike`) | `cast.json` site of the advisor; the customer's shop |
| `shop_said` | the shop as a customer names it (`main st`, `bonny oaks`, `the nashville one`) | `shop_said` list below |
| `shop_address`, `shop_phone` | the shop's street address and phone | page `customers/hours-and-locations` |
| `day_said`, `time_said` | when the customer wants to come, in their words (`tuesday`, `after lunch`, `first thing`) | scenario |
| `heard_price` | a figure the customer types back (a phone quote, another shop's price) | scenario, typed as the customer types money (`89`, `$89`, `like 90 bucks`) |
| `company`, `contact_first`, `unit`, `unit_b`, `po` | a company account, its contact, its unit numbers, a PO number | `accounts.json` (an account not in a story thread that day), scenario |
| `appt_day` | the day of the customer's existing booking | scenario (ERP appointment) |
| `visit_day` | when the shop last did work on the car (`last tuesday`) | scenario (ERP order) |
| `advisor_first` | the advisor writing, first name | `cast.json` `en.colleagues_call` |
| `colleague_first` | another person at the same shop | `cast.json` |
| `tech_first` | a technician at the shop | `cast.json` |
| `manager_first` | the service manager for the shop (Greg, or Dale at Charlotte Pike) | `cast.json` slots 4 and 22 |
| `job_price` | the job's price for this car class on that day, before tax | `catalogue.json` (labour after the rise, standard parts, class multiplier) |
| `job_total` | the same out the door: shop supplies and tax | `catalogue.json`, `configurations.en.shop_supplies` and `tax` |
| `diag`, `diag_price` | the first step (inspection, diagnosis, check) in staff words, and its price | `catalogue.json`, the job block's `first_step`, or the job itself |
| `finding`, `finding_price`, `finding_b`, `finding_b_price` | work the technician found, in chat words, and its catalogue price | job blocks `finding` (`text` and its `catalogue` key), `catalogue.json` |
| `finding_item`, `finding_b_item` | the same finding as a thing to approve (`rear brake pads`), for 'go ahead with the {finding_item}' | job blocks `finding.item` |
| `measure` | a measurement as staff write it (`3 mm`, `4/32`) | scenario |
| `day_a`, `time_a`, `day_b`, `time_b` | two times an advisor offers | scenario (the shop's schedule) |
| `day_agreed`, `time_agreed` | the time the customer took, as the advisor set it | scenario |
| `ready_time` | when the car will be ready, as staff say it | scenario (ERP) |
| `eta_day` | when a part is due, as staff say it | scenario (ERP) |
| `duration` | how long a job takes, in words (`about an hour`) | `catalogue.json` hours |
| `page_price` | a price exactly as the named public page states it | the page in the line's `page` key |
| `page_low`, `page_high` | a range exactly as the page states it | the line's `page` |
| `page_item` | the item's name as the page writes it | the line's `page` |
| `page_term` | a term the page states (the warranty's months and miles, the shuttle's radius, the tow's hook-up) | the line's `page` |
| `open_time`, `close_time`, `sat_hours` | opening, closing, Saturday hours | page `customers/hours-and-locations` |
| `next_open` | when the shops next open (`7:30 tomorrow`, `8:00 Saturday`) | page `customers/hours-and-locations` and the clock |
| `job_page` | the page key the job block names for its price | job block `page` |

`shop_said`: East Main: `main st`, `east main`, `the one on main`, `main street`, `downtown one`; Bonny Oaks: `bonny oaks`, `the hixson one`, `bonny oaks dr`, `the one off bonny oaks`; Charlotte Pike: `nashville`, `charlotte pike`, `the nashville one`, `west nashville`, `charlotte`.

**Assistant slots.** A line the assistant sends may hold only the customer's own slots (`first_name`, `car`, `model`, `car_said`, `job`, `job_said`, `shop`, `shop_said`), the page slots (`page_*`, `open_time`, `close_time`, `sat_hours`, `next_open`, `shop_address`, `shop_phone`) and `manager_first` where a page names him. Any line holding a page slot carries `"page"` and, when the page states more than one figure, `"item"`, the words on the page the figure stands beside: a public page key (path under `kb/en/` without `.md`, visibility public and not stale in `kb/_build/registry.json`), or `{job_page}`, resolved from the job block. `job_price`, `job_total`, `ready_time`, `eta_day`, `time_a`, `time_agreed` never appear in a line the assistant sends. A Telegram draft may repeat `day_agreed` and `time_agreed` only after a person set them (`"echo": true`).

Other keys a line may carry: `for_shops` (the line fits only these shops: the towing lines), `for_skeletons` (only these skeletons), `echo` (a draft repeating a time a person set). A job block carries `symptom_more` (follow-ups that fit that job); a reason in `customer-messages.json` carries `burst` (the second message of a two-line thought) and `more`; `generic` has `close` (neutral), `close_coming` (on the way, see you then), `close_defer` (will think about it), `thanks` (after a hand-over), `when_free` (when no time was offered yet). An unclear loop may carry `job` (the job block it is about), `channels` and `decision`. A moving opening may carry `intent` (`late`, `cancel`, `add`): those are drawn only by skeletons that write their own openings. A draft line may carry `defers` (it promises an answer: when it is sent as is, the person's own answer follows it). A found-work opening carries `decision` (`approve`, `decline`, `question`): the advisor's `found_work.confirm` or `found_work.declined` and the draft `found_work.ack` or `found_work.decline_ack` follow it; a `question` opening is used only where the skeleton writes its own answer.

## Beats (`reasons.json`)

A skeleton is `{"id", "ends", "summary", "beats": [...]}`, plus `job` when its own wordings name the job (the A/C, a nail in the tread). `ends`: `alone` (the assistant ends it), `handed_over`, `abandoned` (the customer left before giving a number), `declined` (the customer said they would call), `person` (a person ends it, Telegram), `silent` (the customer stops answering; Chatwoot resolves after seven days).

| `who` | Keys | Meaning |
|---|---|---|
| `customer` | `use` (a pool in `customer-messages.json`: `<reason>.<part>` or `generic.<part>`), `alts` (this skeleton's own wordings), `photo`, `voice`, `burst` (chance the turn is two or three messages), `p` (chance the beat happens) | the customer's turn |
| `assistant` | `use` (a move in `assistant.json` `sends`), `alts` (each `{"text", "page"}`) | the assistant sends, web chat before a hand-off |
| `handoff` | `kind` (`scheduling` or `escalation`), `note` (a key in `assistant.json` `handoff_notes`) | `forward_to_manager`: the product's sentence to the customer, the bot's private note, label `handoff`, a board card |
| `staff` | `reroll` (the advisor offers two new times: after the customer refused the first two), `draft` (a key in `assistant.json` `drafts`, or absent on a staff-initiated line), `reply` (a move in the advisor's file, or a list of moves sent as one message: `pickup` then `booking.offer`), `draft_outcome` (forces the outcome: the thanks draft a person writes over), `files` (picture pool keys) | a person's turn. With a draft, the advisor's `draft_outcomes` row decides: `sent_as_is` sends the draft; `sent_edited` sends the advisor's edit of it (`edits`, else their `reply`); `discarded` sends their own `reply` |
| `note` | `use` (a key in `labels-and-notes.json` `notes`) | a private note |
| `activity` | `what` (`label_added`, `priority`, `resolved`, `assigned`), `label`, `level` | a small line, stored as a fact |
| `unclear` | `kinds` | where an R13 loop from `unclear.json` may be laid in |
| `end` | `how` | how the session closes |

`alts` and `use` together: the generator draws from both, the least used wording first, so a day's list repeats nothing. An assistant beat whose `use` is a list sends the moves as one message. A reply move an advisor does not have (`moves.call_me` is slot 5's, `moves.warm` slot 22's) is skipped; the job block is the one whose `price_kind` or advice fits the skeleton's assistant moves.

## Advisors (`advisors/<slot>.json`)

`slot`, `name`, `shop`, `voice` (the cast note, shortened), `sheet` (draft outcomes, first-reply minutes, chance to ask, label and resolve shares, from `../DESIGN.md` section 4), `signoff`, `pickup` (first line after a hand-over), `replies` (`<reason>.<move>`, four wordings at least), `moves` (the twelve moves of section 5 and their wordings), `edits` (`{"draft_key", "draft", "sent", "outcome"}`), `notes` (private notes they write).

## Unclear loops (`unclear.json`)

Each `{"id", "kind", "reasons", "open", "second", "third", "ask": {"level_0", "level_1", "level_2"}, "endings": {"after_one", "after_two", "never"}}`. Level 0 answers the first reading (a guess), level 1 is a plain question, level 2 offers two readings. The assistant asks level 1, then level 2; an advisor asks at the level their `ask_chance` draws. `after_one`: the customer's `second` makes it clear. `after_two`: `second` is still unclear, `third` makes it clear. `never`: the customer stops after `second`.
