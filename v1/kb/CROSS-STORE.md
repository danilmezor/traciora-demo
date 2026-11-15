# What the knowledge base expects other stores to hold

The pages point at things that live outside the knowledge engine: team notes, scheduled reports, a pending proposal, hours, settings. Each is listed here with the exact wording the other store must carry, per configuration. Facts with numbers are ledger rows `kb.*` (each names its page and its store); this file holds the texts.

Where a text is quoted from a story card it is marked "card"; where the knowledge base introduced it, "kb".

## 1. Team notes (core `platform.memory`, business scope; `platform.proposal`)

Every note must pass the product's note gate (subject of at most six words, text of at most forty, no personal data, plate or phone).

| # | Note | English | Russian | State at T | Source | Why the knowledge base needs it |
|---|---|---|---|---|---|---|
| 1 | The note that contradicts the storage page | subject "Uncollected cars"; text "Storage is charged from day three after the car is ready." | subject «Невостребованные автомобили»; text «Хранение берём с третьего дня после готовности машины.» | active; proposed by slot 23, approved by slot 22, about T-4 months | kb, ledger `kb.team_note.storage` | Deliberate contradiction: `policies/storage-of-uncollected-cars.md` gives five free days and a daily charge from the sixth (en working days, 25 USD; ru days, 300 RUB). Questions C5.1 to C5.3 |
| 2 | The note that agrees with its page | "A discount above 10 % needs the shop senior's approval, recorded on the order" | «Скидку больше 10 % согласует руководитель сервиса, с отметкой в наряде» | active; proposed by slot 2, so born at administrator rank; approved by slot 4, who lowered its rank to junior on approval, so every advisor reads it; on the day of `@discount_rule` | card S02 (English); the Russian wording follows `ru/policies/discounts.md` | `policies/discounts.md` says the same; question C5.3 asks for a note that agrees with its page |
| 3 | Slot 6's approved proposal | "On a first call, offer a time before the price" | «На первом звонке сначала предложить время, потом назвать цену» | approved by slot 4 the open day after the Monday of week T-6 | card S04 (English) | `how-to/taking-a-call.md` has the move "Offer a time. Two of them" |
| 4 | Slot 6's declined proposal | "Read the booking back before hanging up"; slot 4's reason: "the page 'Booking a visit' already says this; propose the wording there" | «Проговорить запись перед тем, как положить трубку»; причина: «На странице „Запись на ремонт“ это уже есть; предложите формулировку туда» | declined by slot 4 on `@note_declined` | card S04 (English) | Step 6 of `how-to/booking-a-visit.md` is the read-back; `how-to/using-this-knowledge-base.md` says where a team habit belongs. Questions P7.1, P7.2 |
| 5 | Slot 6's waiting proposal | "A company driver cannot approve work over 300 USD; call the fleet contact" | «Водитель организации не согласует работы дороже 8 000 ₽; звонить ответственному» | waiting since her last working day before T | card S04; ledger `s4.driver_limit` | The limit is already on `accounts/company-account-terms.md`, so the note repeats a page, as her declined one did. Question P5.4 |
| 6 | The personal note three people hold | subject "Prices source"; text "Take prices from the price list page, never from a service page" | тема «Откуда брать цены»; текст «Цены брать со страницы прайс-листа, а не со страницы услуги» | active for slots 5, 6 and 7; the nightly proposal waits since the night before T | card S04, S08 (English) | `README.md`, `how-to/writing-an-estimate.md` and `how-to/using-this-knowledge-base.md` were edited to say it after the timing-belt complaint (question O10) |

The Russian wordings of notes 2 to 6 are written here for the first time: the cards give them in English only. The memory store's Russian rows (`assistant/ru/team.json`) carry exactly these texts; a change to one is made here and there together.

## 2. The memo

`management/what-we-found-at-west.md` (senior rank) is the only memo. It lives in the knowledge base; the shop-system database must give the same numbers when asked.

| What the memo says | English | Russian | Ledger |
|---|---|---|---|
| Share of the fired advisor's cash orders with an unapproved discount of 15 to 30 %, against everyone else | 22 % against 3 % | 22 % against 3 % | `s2.f1.discount_share`, `pay.background_discount_share` |
| Share of the bought shop's cash orders with a discount of 10 % or more, before and since (in the section "Since", added by slot 2 on `@early_desk+1w`) | "from 13.4 % to 2.4 %" | «с 13,8 до 2,7 %» | `s2.west.discount_share_before`, `s2.west.discount_share_after` |
| The second and third ways | "Orders voided after the customer had paid. 14 in six months."; "The drawer was short on 19 of the days he closed it."; the three together "$11,400" | parts issued with no sale and work past the order; since the rule: «Выдач без наряда и нарядов с лишним временем с тех пор не было» | `s2.f1.second`, `s2.f1.third`, `s2.total` |
| The weekly list | "I get a list of discounts over 10 % every Friday." | «Список скидок больше 10 % я получаю каждую пятницу.» | `s10.tasks` |

## 3. Scheduled reports (auth.db `cron_prompt_jobs`; ledger `s10.tasks`)

The page's name for a report is the name the person sees on the task. Times are in the home zone.

| Owner | Page | English name on the page, time | Russian name on the page, time |
|---|---|---|---|
| slot 2 | `playbooks/owner.md` | "company accounts this week", Monday 8:00 | «Корпоративные клиенты за неделю», понедельник 9:00 |
| slot 2 | `playbooks/owner.md`, the memo | "discounts over 10 %", Friday 4:00 p.m. | «Скидки больше 10 %», пятница 18:00 |
| slot 2 | `playbooks/owner.md` | "Charlotte Pike against plan", Monday 9:00 (the ledger names it by its site key, "west against plan") | «Казань: план и факт», понедельник 10:00 |
| slot 2 | `playbooks/owner.md` | "missed calls today", daily 6:00 p.m. | «Пропущенные звонки за день», каждый день 20:15 |
| slot 4 | `playbooks/manager.md` | "Tomorrow's gaps in cover", daily 4:30 p.m. | «Завтрашние пробелы в графике», каждый день 18:30 |

The owner playbook also says a failed run shows in her Inbox and is run again from there: `s10.failure`.

## 4. The pending proposal (knowledge engine proposal; core `platform.notification_queue`, `knowledge.proposed`)

One proposal waits at T: slot 5's correction to `services/engine/timing-belt.md`, for slot 4. The exact before and after text of each change is on the page's sheet (`facts/services/engine/timing-belt.json` and `facts-ru/…`, field `pending_proposal`). Nothing may edit that page after the proposal is made.

| | English | Russian |
|---|---|---|
| The proposer's reason | "Old labour rate. Caleb quoted $688 from this page and promised same day; the bill was $741.60 and Greg gave $80 back. Price list says $720. Also taking out the same-day line: it is only true when the kit is on the shelf." | «Старый нормо-час. Никита назвал с этой страницы 15 552 ₽ и пообещал отдать машину в тот же день; в наряде вышло 16 182,40 ₽, и Сергей Анатольевич вернул 1 800 ₽. В прайсе — 16 000 ₽. Заодно убираю строку про «в тот же день»: это правда, только когда комплект на полке.» |
| Made on | `@belt_proposal`: the full open day after the discount | `@belt_proposal`: slot 5's first working day after the discount (he works two on, two off) |

## 5. Revision authors and messages (knowledge engine history)

Every later revision of a page is written by the seeder as the named person, in order, with the message on the page's sheet (`revisions`: `what` and, in Russian, `message_ru`). The engine stamps each with the build day; the true dates are in the page text. `team/who-is-who.md` has four later revisions in both configurations: slot F1 removed, slot F2 removed, slots 7 and 14 added, extensions checked.

## 6. Hours (core `core.location`, `core.location_hours_exception`)

| Text on the page | Page | Store |
|---|---|---|
| en: "all three shops close at 12:00 noon for our twice-yearly parts count. We open at 7:30 a.m. as usual." ru: the same event, every shop closes at 12:00 | `customers/hours-and-locations.md`, added by slot 4 on `@stocktake_notice` | an exception on the Thursday of week W+1 for three sites (`site.stocktake`); no shift after 12:00 |
| en: the six closed dates, a weekend holiday observed on the nearest weekday. ru: «1 и 2 января» only | `customers/hours-and-locations.md` | `site.closed_dates` |
| The bought shop's own page: en Saturday 8:00 to 12:00, ru closing at 19:00 | `shops/west/README.md`, stale on purpose | must not be true in the store (`kb.west_old_hours`) |

## 7. Phones and addresses (phones.md, `geo.address.*`)

The public pages give the shops' lines and addresses as phones.md and the ledger hold them: (423) 555-0142, (423) 555-0167, (615) 555-0119; +7 (8422) 10-40-40, +7 (8422) 10-40-41, +7 (843) 100-40-30. `customers/company-vehicles.md` sends a company to slot 4 on the flagship's line.

## 8. Tenant settings

Ledger `kb.settings`: the knowledge root is seen from worker; folders are ranked before files land (`kb.pages.*`, `kb.file_ranks`); proposing from middle, publishing from senior; `playbooks/` pinned at administrator by the product. The assistant's mode per channel is `conv.assistant_mode`: `how-to/chats-and-messages.md` and `playbooks/advisor.md` say it sends in the web chat and only drafts on Telegram (and on VK and Avito in Russian).

## 9. The shop-system database, the roster and the call scripts

Not texts but values: each is a `kb.*` ledger row whose `store` field names where it must appear (credit limits, floats, deposits, towing lines, estimate expiry, appointment rules, cover minimums, supplier order times, stock of R-1234yf at the flagship only, pay types, the handbook's leave and lateness numbers). Rows whose reasoning begins "DELIBERATE GAP" are the ones where the store must *not* agree with the page; the gap is a planted question.
