# Knowledge base of seed v1: outline

Company: Brennan Auto Care (English configuration). The pages agree with `ledger.json` and `stories/`, which are the source of truth: `checks/check_kb.py` fails when they do not. What the knowledge base introduced is in the ledger under `kb.*`; what other stores must hold word for word is in `CROSS-STORE.md`.

| | |
|---|---|
| Pages (Markdown) | 152, all written: `en/<path>.md`, one fact sheet each in `facts/<path>.json` |
| Binary documents | 5, drafted in `en/_binaries.md`, one fact sheet each in `facts/<path>.<ext>.json` |
| Folders | 28 (12 top-level) |
| By visibility | public 67 · staff 68 (+ 5 binaries) · middle 5 · senior 5 · administrator 7 |
| Pages with history (more than the go-live import, or created after it) | 87 |
| Pages stale on purpose | 6 |
| Length | 7 tiny · 98 short · 46 medium · 1 long (the price list, over the read limit) · about 37,000 words |
| Planted challenges | 20, with 99 eval questions; 15 more on operating the base |
| First-revision texts | `en/_history/`: the text before the price rise of the 36 pages whose only later change is the price pass |
| Builder | `_build/`: the scripts that wrote every page and fact sheet from the seed files; `python3 _build/build.py` rebuilds both configurations and checks them. Rerun it after any change to the catalogue, cast, vendors or accounts; `python3 checks/check_ledger.py` then proves the pages against the ledger |

## 1. Placeholders

Every date in a page is a placeholder the seeder fills before the page is loaded. Nothing else in a page is a placeholder.

`{{<when>|<format>}}`

| Part | Forms | Meaning |
|---|---|---|
| `<when>` | `@price_rise` | a named event, placed by the anchors of `stories/TIMELINE.md` (table below). Every date a story depends on is an event |
| | `@price_rise+3wd:main`, `@golive+2w`, `@purchase+1mo` | an event moved on: `wd:<shop>` counts full open days of that shop, `w` weeks, `mo` months |
| | `T-9mo`, `T-6y`, `T+2mo` | T moved by calendar months or years. Used only for the age of a page that no story depends on ("Last reviewed") |
| `<format>` | `date` | March 4, 2026 |
| | `day` | Wednesday, March 4 |
| | `month` | March 2026 |
| | `season` | spring, summer, fall or winter of that date |

Inside a Markdown table cell the bar is escaped, `{{@purchase\|month}}`, so the table survives; the seeder accepts both spellings.

| Event | Anchor (`stories/TIMELINE.md`) | Story |
|---|---|---|
| `@warranty_2424` | T-26 months: the 24/24 warranty comes into force, before the ERP's two years | new fact |
| `@purchase` | T-14 months: Charlotte Pike is bought | |
| `@leak_start` | the first full open day on or after T-335 d | S2 |
| `@golive` | G | |
| `@money_found` | the 5th full open day after G | S2 |
| `@f1_fired` | the 15th full open day after G | S2 |
| `@discount_rule` | the 16th: the next full open day after the firing; discount, void and till rules | S2, S12 |
| `@price_rise` | P: labour hour 125.00 to 135.00 | S8, S12 |
| `@f2_fired` | the Monday of week T-17 | S14 |
| `@newcomers` | the Monday of week T-14: the newcomer advisor's first day | S8 |
| `@diag_back` | the Monday of week T-8, after the diagnostician's leave | S5 |
| `@early_desk`, `@supplier_due` | the Monday of week T-3 | S3, S6 |
| `@note_declined` | the day slot 4 declined slot 6's second team note (week T-3) | S4 |
| `@belt_proposal` | the full open day after the discount on the timing-belt bill | S8, S12 |
| `@stocktake_notice` | the Monday of week W-1 | S13 |
| `@stocktake` | the Thursday of week W+1: every shop closes at noon | S13 |

## 2. Who may read what

The product has no "public" tier of its own. The customers' assistant reads as the member `assistant-public` at **worker** rank, and the tenant root is seen from **junior** unless the setting `TRACIORA_KNOWLEDGE_ROOT_SEEN_FROM` says otherwise (`core/commands/knowledge_members.py`, `core/content/knowledge.py`). So:

| Tier in this outline | Engine `seen_from` | Who reads it |
|---|---|---|
| public | worker | the website assistant, technicians, everyone above |
| staff | junior | advisors, foreman, parts manager and up |
| middle | middle | lead advisors, office manager and up |
| senior | senior | service manager, shop manager, founder, managing owner |
| administrator | administrator | the managing owner |

What the seeder must do, in this order: set the tenant's root to `worker`; create the folders and set `seen_from` (table below) **before** any file lands, as the product's import does for `playbooks`; then load the files. `en/playbooks/*` goes to the tenant's `playbooks/` directory, everything else to `knowledge_base/`.

| Path | `seen_from` |
|---|---|
| `customers`, `shop-floor`, `services`, `prices` | worker (inherited from the root) |
| `README.md` at the root; `prices/labour-rates-and-fees.md`, `prices/how-prices-change.md`, `prices/counter-price-sheet.pdf` (set on the files) | junior |
| `policies`, `accounts`, `how-to`, `parts`, `shops`, `team` | junior |
| `accounts/credit`, `office` | middle |
| `management` | senior |
| `management/owners` | administrator |
| `playbooks` | administrator (pinned by the product) |

The eleven pages of ledger row `s12.pages`, by name:

| Ledger | Page here | Readers |
|---|---|---|
| Price list | `prices/price-list.md` | public |
| Timing belt | `services/engine/timing-belt.md` | public, stale |
| Brake questions | `services/brakes/brake-questions.md` | public, stale |
| Warranty | `customers/warranty.md` ("Our warranty"); the full terms for staff are `policies/warranty.md` | public |
| Warranty (old) | `customers/warranty-policy.md` ("Warranty policy") | public, out of date |
| Booking a visit | `how-to/booking-a-visit.md` | staff |
| Discount policy | `policies/discounts.md` | staff |
| Company accounts | `accounts/company-account-terms.md` | staff |
| Suppliers | `parts/suppliers.md` | staff |
| Staff handbook | `team/staff-handbook.docx` | staff |
| Pay and till | `management/pay-and-till.md` | senior |

Consequences, used on purpose: because Timing belt and Brake questions are public, the whole `services` folder is: 38 pages written for the counter, with nothing confidential in them, that the website assistant can quote, the two stale ones included. `shop-floor` is written for technicians and is readable by the website assistant too. The staff handbook is at staff rank, with a paper binder for technicians.

## 3. Revisions and proposals

- **Revision 1 of a page that existed at go-live** is the product's import ("Imported from the tenant's files", shown as Administrator). The page's own "Last reviewed" line carries its real age.
- **Later revisions** are written by the seeder as the named person. Rungs are the product's defaults: propose from middle (slots 3, 5, 16), publish and decide from senior (slots 1, 4, 22) and the administrator (slot 2). A page in a junior's voice (slots 6, 8, 9, 24) is therefore published by a senior and says so. A change by a middle-rank person is a proposal approved by a senior: the fact sheet gives `proposer_slot` and `approver_slot`.
- Each fact sheet carries: `facts` (statements), `tables` and `list_items` (every table row and list item of the page as data, by section), `prices` (each with its catalogue key, tier, class and side of the rise), `people` (by cast slot), `vendors`, `accounts`, `dates` (placeholders), `new_facts`, `revisions`, and `notes_for_russian_writer`. The Russian writer works from the sheet.
- Each fact sheet's `revisions` lists, in order: kind, author slot, the date the text claims, what changed, and the revision message. The engine stamps every revision with the build day (design O2), so the order and the messages are what an agent reads, and the dates are in the page text.
- **One proposal is pending at T** and only one: slot 5's correction to `services/engine/timing-belt.md` (exact before and after text in its fact sheet under `pending_proposal`). Nothing may edit that page after the proposal is made, or it goes stale.
- 36 pages changed only at the price pass after the rise; their revision 1 text is in `en/_history/<path>`, generated from the catalogue's before-rise figures.

## 4. The tree

Columns: *Vis.* tier; *Voice* the cast slot whose voice the page is in; *Len.* length class; *Rev.* number of revisions to seed; *Serves* stories (S), planted challenges (C:), operating questions (O:), rank tests (V:); *Links to* the pages it links to (without `.md`).
