# Russian conversation bank: format

The bank a generator assembles background chats from (`../DESIGN.md` sections 4 and 5), Russian configuration: «Ермак-Сервис», four channels (`web`, `telegram`, `vk`, `avito`). It follows `../bank-en/FORMAT.md` (read in its state of 2026-11-14 00:01): the same files, the same keys, the same beats. This page lists the slots and then, under **Russian additions**, everything the English format does not have. Every file is JSON with a `format` key `bank-ru/<file>/1`.

Sources: `_src/*.txt` (plain text, one message per line) and `_src/build.py`, which writes the JSON; edit a line in the text and run `python3 _src/build.py`. Check: `../../checks/check_conv_bank_ru.py`, output `../../checks/conv_bank_ru_check.txt`, sample `assembled-sample.md`. For the native reader: `_README.md`.

## Files

| File | Holds | Section 5 piece |
|---|---|---|
| `reasons.json` | per reason: `label`, `shares` by channel, `alone_on_web`, `unclear_weight`, `skeletons` by channel; and `exchanges` | skeletons: 8 for price, booking, status, symptom, 5 for the other six, on each channel the reason occurs on. One skeleton may stand under several channels with the same `id` |
| `customer-messages.json` | 24 job blocks, first steps, findings, 8 voices, 40 pictures, 6 voice stubs, per reason the openings and the turns that follow, generic turns, `forms` | job blocks, customer voices, picture pool |
| `assistant.json` | greetings, what it sends on the web chat, hand-off notes, drafts | assistant bank |
| `advisors/<slot>.json` | nine advisors: sheet, pick-up, replies per reason, moves, draft edits, sign-off, notes | advisor bank |
| `unclear.json` | 22 R13 loops | unclear openings |
| `labels-and-notes.json` | private notes with their author's slot, short acknowledgements, label use, priority patterns | private notes |

## Slots

Written `{name}`. Nothing else in a bank text holds a digit, except `1.`, `2.`, `3.` starting a line of a numbered list (slot 24 writes by points).

| Slot | Value | Source |
|---|---|---|
| `first_name` | the customer's first name, as the assistant uses it once the customer typed it | scenario: an invented customer, never one of `named_customers.json` |
| `name_addr` | how this advisor addresses the customer: the first name, or name and patronymic for an older customer known on a messenger | scenario |
| `name_typed`, `phone_typed` | the name and the number as the customer types them (`ольга`, `89073786035`, `8 907 215 63 08`) | scenario, `phones.md` (codes 907 and 935) |
| `advisor_addr` | how a customer addresses the advisor (`Алина`, `Светлана`, `Ринат Фаридович`): Telegram and VK only | `cast.json` `ru.customers_call` |
| `car` | the car as staff and the assistant write it (`Hyundai Solaris 2016`) | `parc.json` |
| `car_make`, `model` | the make and the model in Latin letters, as the price list writes them | `forms.cars` |
| `car_said`, `car_said_acc`, `car_said_gen`, `car_said_dat`, `car_said_prep` | the car as the customer types it, in five cases (`солярис`, `на гранту`, `для гранты`, `по гранте`, `на гранте`) | `forms.cars[].car_said` |
| `car_year` | the model year as typed (`2016`) | scenario |
| `mileage_said`, `tyre_size_said`, `season_for` | `120 тыс`; `r15`, `185/65 r15`; `на зиму` or `на лето` | scenario |
| `job`, `job_acc` | the job in staff words, nominative and accusative | job block `staff_says` |
| `job_short` | the job as an advisor shortens it in a chat | job block `short` |
| `job_said`, `job_said_inf`, `job_said_acc` | the job in the customer's words: a noun phrase («замена масла»), an infinitive («масло поменять»), after «на» («замену масла») | job block `said`, `said_inf`, `said_acc` |
| `symptom_said` | what the car does, in the customer's words, a whole clause | job block `symptom_said` |
| `photo`, `voice_len` | a picture's pool key; seconds of a voice message | `pictures`, `voice_stubs` |
| `shop`, `shop_at`, `shop_address`, `shop_phone` | the shop: its short name, «где» (`на Московском шоссе`, `в Новом городе`, `на Технической`), street address, phone | `forms.shops`, page `customers/hours-and-locations` |
| `shop_said`, `shop_said_at` | the shop as a customer names it (`московское`, `на технической`) | `forms.shops` |
| `day_said`, `day_said_for`, `time_said` | when the customer wants to come, as whole phrases: `в субботу`, `на субботу`, `после работы` | scenario |
| `heard_price` | a figure the customer types back (`7900`, `6 тыщ`) | scenario |
| `company`, `contact_first`, `unit`, `unit_b`, `po` | a company account, its contact, its vehicles, a request number (`96/07`) | `accounts.json`, scenario |
| `appt_day_on`, `appt_day_for`, `appt_day_from` | the customer's existing booking: `в четверг`, `на четверг`, `с четверга` | scenario (ERP appointment) |
| `visit_day`, `visit_date`, `days_waiting` | when the shop last worked on the car (`в прошлый вторник`), the same as a date (`12 октября`), how long the car has been in (`пятый день`) | scenario (ERP order) |
| `colleague_first`, `colleague_mention`, `manager_mention` | another advisor at the shop; the same and the service manager as a mention in a note (`@Никита Ведяшкин`) | `cast.json` |
| `job_price`, `job_total`, `diag_price`, `labour_price`, `storage_price` | the job before VAT; with shop supplies and VAT; the first step; labour only (customer's own parts); tyre storage | `catalogue.json` |
| `finding`, `finding_fix`, `finding_why`, `finding_said`, `finding_price`, `finding_photo`, `finding_b`, `finding_b_fix`, `finding_b_said`, `finding_b_price`, `measure` | found work: what was seen, the job that fixes it, why it matters, how the customer names it when answering, its price, its photo; a second finding; a measurement (`2 мм`) | `findings`, `catalogue.json` |
| `guess_price` | in an unclear loop, the price of the job the first reading names | `unclear.json` `guess_job` |
| `day_a`, `day_a_on`, `day_a_for`, `time_a`, `day_b`, `day_b_on`, `day_b_for`, `time_b` | two times an advisor offers | scenario |
| `day_agreed`, `day_agreed_on`, `day_agreed_for`, `time_agreed`, `time_agreed_said` | the time the customer took; the last as the customer types the hour (`10`, `12 30`) | scenario |
| `ready_time`, `eta_day_on` | when the car will be ready, a whole phrase (`сегодня к 17:00`); when a part is due (`в понедельник`) | scenario (ERP) |
| `duration` | how long a job takes, in words (`около часа`) | `catalogue.json` hours |
| `step`, `step_price`, `step_page` | the first step of a job (a diagnosis), its price as the page states it, the page | `steps` |
| `page_price`, `page_low`, `page_high`, `page_labour`, `page_duration`, `page_class`, `page_price_class` | a price, a range, labour only, a duration, the customer's vehicle class and that class's price, each exactly as the page of the line states it | the line's `page` and the job block's `page_item` |
| `page_term`, `page_term_b`, `page_term_c` | a term the page states | the line's `quote` |
| `open_time`, `close_time` | opening and closing | page `customers/hours-and-locations` |
| `job_page` | the page key the job block names for its price | job block `page` |
| `hello`, `hello_lc` | the greeting for the hour: `Добрый день`, `добрый вечер` | the clock |
| `customer_words`, `second_words`, `clear_words`, `asked_times` | in a hand-off note: the customer's first message, their second, what it turned out to be, `один раз` or `дважды` | the conversation |

In `use`, `draft` and `files` (never in a text): `{price_move}`, `{advice_move}`, `{towing_move}`, `{price_draft}`, `{finding_photo}`, `{photo}`.

## Russian additions

**Grammar**

1. **Case suffixes.** A slot that names a car, a job or a day comes in forms: `_acc`, `_gen`, `_dat`, `_prep` (cars, jobs), `_on` «когда», `_for` «на когда», `_from` «с какого» (days), `_at` «где» (shops). `forms` in `customer-messages.json` holds them: `forms.cars` (the 78 models of `parc.json`, each with the ways a customer types it and one Cyrillic staff form, declined, with `gender`), `forms.days`, `forms.shops`. A person's name is used only in the nominative.
2. **Capital letter.** `{Job}`, `{Hello}`, `{Day_a}`, `{Finding}`, `{Symptom_said}`: the same slot with its first letter in upper case, for the start of a sentence.
3. **Customer's gender.** `[[он|она]]` inside a text picks by the customer's gender (`[[забрал|забрала]]`). A pool entry is a string, or an object `{"text", "g": "m"|"f"}` when the whole line fits one gender. A voice stub carries `g` too.
4. **A number carries its noun.** `days_waiting` is `пятый день`, `duration` is `около часа`, a price is `4 560 ₽`: no text follows a slot with «дней», «рублей», «минут». A day slot carries its preposition (`day_a_for` is `на пятницу`).
5. **Money as a person types it.** `<price>_bare` is the figure with no space and no sign (`10450`: slots 5, 22, 23), `<price>_num` with a space and no sign (`3 700`: slot 17). For `job_price`, `job_total`, `diag_price`, `labour_price`, `storage_price`, `finding_price`, `finding_b_price`.
6. **Greeting by the hour**: `hello`, `hello_lc`. No bank line types «добрый день».
7. **A second message does not greet again.** When one message is joined from several moves, or a reply or draft follows an earlier line of the shop, a leading greeting is dropped; a part that does not end with a mark gets a full stop before the next.

**Customer messages**

8. `ch` is a list of channels. An entry holding `{advisor_addr}` fits Telegram and VK only.
9. Job block: `staff_says` is `{nom, acc}`; `short`; `said`, `said_inf`, `said_acc`; `advice` (which `advice_*` move answers its symptom); `listing` (the title of the shop's Avito listing the chat starts from: it goes into the conversation's attributes, not into a message); `finding` is a list of keys into `findings`. `price_kind`: `menu`, `class` (the page gives a price per vehicle class), `list` (the public price list's standard column), `range`, `depends` (first step only), `depends_engine`, `depends_ac`, `depends_to`.
10. `steps`: first steps that are not job blocks. `findings`: `{key, catalogue, finding, fix, said, why, photo}`.
11. An opening may carry `kind` (hours: `time`, `address`, `do_yes`, `do_no`, `do_sublet`, `do_hybrid`, `pay`; status: `part`; found work: `yes`, `one`, `ask`, `no`, with the English `decision`; moving: `move`, `cancel`, `late`, with `intent`; complaint: `comeback`, `bill`, `service`, `damage`; fleet: `units`, `docs`; spam: `seller`, `wrong`, `job`, `noise`), `only` (job keys, or `masc_car`, `fem_car`: the customer's word for the car has that gender), `burst` (the text holds a line break: two messages). A reason has named parts besides `open`, `more` and `burst` (`price.vat`, `price.own_parts`, `status.pickup_late`): a skeleton names the part whose answer it carries.
12. `generic` adds `give_phone`, `give_name`, `give_tyres`, `yes`, `no`, `ask_address`, `ask_pay`, `ask_storage`, `pick_more` (a second message after a time is taken). `when_free` is used when no time was offered: the customer proposes one.
13. A voice stub has a fixed `seconds`.

**Assistant**

14. `quote` on a line: `{slot: text}`, each value exactly as the named page writes it; the check finds every value in the page. A job-based line (`"page": "{job_page}"` or `"{step_page}"`) takes its figures from the job block's `page_item` row. The English `item` is not used.
15. Moves `greet` (the greeting for the clock: in hours, after hours, returning; once a conversation), `{price_move}`, `{advice_move}`, `{towing_move}` resolve from the job block and the shop. A move or a draft that needs a first step is skipped or replaced by `generic.ask_car` for a job without one.
16. Hand-off notes `unclear` and `unclear_never` for R13.
17. Draft group `tyres` (seasonal storage). Drafts with `defers` are set by key (`status.dont_have`, `status.part`, `status.sorry_wait`, `status.total`, `found_work.can_wait`, `found_work.total`, `complaint.service`).

**Advisors**

18. `sheet.curt` (slots 22, 23: they take the second wording of a loop's `level_0` and answer a clarifying moment with `ask_lead` alone), `sheet.no_price` (slot 22: on a guess he names no price and says his `guess_tail`). `moves` adds `sorry`, `thanks_reply`, `ask_lead` and `guess_tail` (said before a clarifying question and after a guess), `call_me` (slot 5). The moves `price`, `offer_time`, `confirm`, `not_yet`, `moved`, `found_work`, `decline_discount` repeat the first three wordings of the reply they are (`price.quote`, `booking.offer`, `booking.confirm`, `status.not_yet`, `moving.moved`, `found_work.present`, `price.objection`). Replies add the group `tyres`.
19. An edit may carry `fits` (the reply key it is consistent with: it is used only where the skeleton's beat names that reply, because an edit states facts). An edit with `"sent": null` and `discarded`: the draft was cleared and nothing was sent.

**Skeletons**

20. `when`: `kinds` (the job's `price_kind`), `jobs`, `advice` (the job has an advice move), `two`, `photo`, `bigger` (the car is not of class `car`), `advisors` (the slots the skeleton is written for: «answers the first of two questions»).
21. Customer beat: `use` may be a list (the parts are sent as separate messages), `kind`, `two`, `photo`, `stub`, `voice`. Without `kind` the beat draws openings that have none. `if: "nocar"` on a beat: only when the customer has not named the car yet.
22. Staff beat without `reply`: the draft goes as it is or edited; if the advisor's row discards it, nothing is sent, and the customer's next «ок» is skipped.
23. `extra` beat: `{"who": "extra", "keys": [...], "p"}`, a point where one exchange from `reasons.json` `exchanges` may be laid in: a customer question (`customer`: a pool), the draft it raises and the advisor's `reply`. Keys: `vat`, `own_parts`, `how_long`, `wait`, `total`, `storage`, `address`, `pay`. The build puts two such points into every person-handled skeleton of price, booking, symptom, status and moving that has none of its own. An exchange is not drawn twice in a conversation, nor when its answer was already given.
24. `activity` `priority` carries `level`; `end.how` is `person` (the advisor's `resolves` share, else seven silent days) or `inactivity`.

**Unclear loops**

25. `second_to_guess` (what the customer answers to a level-0 guess), `job` and `guess_job` (a job block, a step, or `catalogue:<key>`), `reads` (what it turned out to be, for the note), `never_customer` (the last thing the customer types before going silent, or null). `level_0` holds two wordings: plain and curt. `endings` hold what the one who asked says: the acknowledgement once it is clear, and the last line when it never is.

**Labels and notes**

26. A note carries `slot`: the generator takes the note of the person who handles the chat. `acks` are one-line answers to a colleague's note; `labels.use` says when each label is put.
