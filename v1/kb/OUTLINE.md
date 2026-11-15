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

### `(root)/` · 1 · seen from worker (tenant setting); README.md itself junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Brennan Auto Care knowledge base | staff | 2 Claire Brennan | medium | 2 | S12 O:overview | Front page for staff: what each folder holds, who owns it, and the two house rules (prices, corrections). | customers/README, services/README, prices/price-list, policies/README, accounts/company-account-terms, how-to/README, parts/suppliers, shops/README, team/who-is-who, shop-floor/README, how-to/using-this-knowledge-base |

### `customers/` · 21 · seen from worker = public

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Customer answers | public | 2 Claire Brennan | short | 1 | S7 S13 V:public | Index of the public pages; the README the website assistant gets from kb_overview. | customers/hours-and-locations, customers/what-we-do, customers/prices-for-common-services, customers/estimates-and-approvals, customers/warranty, customers/dropping-off-and-picking-up, customers/payment, customers/towing, customers/bringing-your-own-parts, customers/if-something-is-not-right, customers/brake-noise, customers/check-engine-light, customers/air-conditioning, customers/battery, customers/tires, customers/maintenance-by-mileage, customers/pre-purchase-inspection, customers/hybrids-and-electric-cars, customers/company-vehicles |
| `air-conditioning.md` | Air conditioning not cold | public | 5 Travis Burnette | short | 1 | S11 C:customer-terms C:fact-in-table | Public page for the summer season: what the A/C check is, what a recharge costs for each refrigerant. | customers/maintenance-by-mileage |
| `battery.md` | Battery and starting trouble | public | 13 Terry Dotson | short | 1 | S11 C:customer-terms | Public page: free battery test, replacement price range, the cold-weeks rush. | - |
| `brake-noise.md` | Brake noise | public | 6 Maya Torres | medium | 2 | S7 C:customer-terms | What a customer with a brake noise is told, what the inspection costs and what a typical repair costs. The page the assistant answers S7 from. | customers/prices-for-common-services, customers/warranty |
| `bringing-your-own-parts.md` | Bringing your own parts | public | 1 Ray Brennan | short | 1 | C:combine-policy-and-price C:customer-terms | Public version of the customer-supplied parts policy, in the founder's words. | customers/warranty |
| `check-engine-light.md` | Check engine light | public | 5 Travis Burnette | short | 1 | C:customer-terms C:combine-policy-and-price | Public advice on a check engine light and what the diagnosis costs. | customers/towing |
| `company-vehicles.md` | Company vehicles | public | 2 Claire Brennan | short | 1 | S1 V:public | Public pointer for businesses; the terms themselves are staff-only. | - |
| `dropping-off-and-picking-up.md` | Dropping off, waiting, shuttle and pick-up | public | 6 Maya Torres | short | 1 | C:kb-does-not-say C:near-duplicate-shop-pages | Public logistics: key drop, waiting room, shuttle, after-hours pick-up. | - |
| `estimates-and-approvals.md` | Estimates and approvals | public | 2 Claire Brennan | short | 1 | S7 C:combine-policy-and-price C:three-page-procedure | Public promise on estimates: written, per job, nothing without approval. | customers/prices-for-common-services |
| `hours-and-locations.md` | Hours and locations | public | 2 Claire Brennan | short | 2 | S13 S9 S7 C:fact-in-table C:near-duplicate-shop-pages | The public truth about addresses, phones, hours, holidays and the stocktake afternoon. | customers/dropping-off-and-picking-up |
| `hybrids-and-electric-cars.md` | Hybrids and electric cars | public | 2 Claire Brennan | tiny | 1 | C:kb-does-not-say | The stated limit of what the shops do on hybrids and EVs. | - |
| `if-something-is-not-right.md` | If something isn't right | public | 4 Greg Whitaker | short | 1 | S8 S1 | Public complaints route. | - |
| `maintenance-by-mileage.md` | Maintenance by mileage | public | 5 Travis Burnette | short | 1 | C:customer-terms C:fact-in-table | Public explanation of oil service, filters and the 30/60/90K service. | - |
| `payment.md` | Paying your bill | public | 3 Donna Ledford | short | 1 | S2 C:combine-policy-and-price | Public payment terms: methods, when due, deposits, tax. | customers/company-vehicles |
| `pre-purchase-inspection.md` | Buying a used car: pre-purchase inspection | public | 5 Travis Burnette | short | 1 | smoke | Public description of the pre-purchase inspection. | - |
| `prices-for-common-services.md` | Prices for common services | public | 2 Claire Brennan | short | 2 | S7 S8 S12 C:fact-in-table C:combine-policy-and-price | Menu prices a customer may be told without seeing the car; public version of the price list. | customers/estimates-and-approvals |
| `tires.md` | Tires, flats and alignment | public | 15 Cody Gann | short | 1 | C:customer-terms C:fact-only-in-attachment | Public page for tire questions with menu prices. | - |
| `towing.md` | Towing | public | 4 Greg Whitaker | short | 1 | C:kb-does-not-say C:combine-policy-and-price | Public towing arrangement for the Chattanooga shops; Nashville is deliberately thin. | - |
| `warranty-policy.md` | Warranty policy **stale** | public | 1 Ray Brennan | short | 1 | S12 C:near-duplicate O:contradiction | The old warranty page nobody removed: 12/12. Stale on purpose (S12). | - |
| `warranty.md` | Our warranty | public | 2 Claire Brennan | medium | 1 | S12 S1 C:combine-policy-and-price C:kb-does-not-say C:near-duplicate | Public summary of the 24/24 warranty; the staff page has the full terms. | customers/bringing-your-own-parts |
| `what-we-do.md` | What we work on, and what we don't | public | 2 Claire Brennan | short | 1 | S7 C:kb-does-not-say | Scope of work for the public: services offered, and the work we send out or decline. | customers/hybrids-and-electric-cars |

### `shop-floor/` · 7 · seen from worker = public

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Shop floor | public | 8 Randy Elrod | tiny | 1 | V:worker C:kb-does-not-say S14 | Index for technicians; what a worker-rank person can read. | shop-floor/clocking-in-and-out, shop-floor/shift-changes-and-time-off, shop-floor/courtesy-inspection, shop-floor/before-a-car-leaves, shop-floor/when-a-car-comes-back, shop-floor/safety |
| `before-a-car-leaves.md` | Before a car leaves your bay | public | 8 Randy Elrod | short | 1 | S6 S14 V:worker | The foreman's final checks. | - |
| `clocking-in-and-out.md` | Clocking in and out | public | 4 Greg Whitaker | short | 2 | S14 V:worker | How technicians punch, the location check, what to do after a forgotten clock-out. | - |
| `courtesy-inspection.md` | The courtesy inspection | public | 8 Randy Elrod | short | 1 | C:three-page-procedure S7 V:worker | Step one of the inspection-to-approval procedure: what the technician checks and records. | how-to/writing-an-estimate |
| `safety.md` | Safety | public | 8 Randy Elrod | short | 1 | V:worker C:kb-does-not-say | Short safety rules, including who may touch hybrids and refrigerant. | - |
| `shift-changes-and-time-off.md` | Shift changes and time off | public | 4 Greg Whitaker | short | 1 | S14 S5 V:worker | How a technician asks for a shift change or a day off; what the planner needs. | - |
| `when-a-car-comes-back.md` | When a car comes back | public | 8 Randy Elrod | short | 1 | S6 S1 V:worker | What a technician does with a comeback. | - |

### `services/` · 2 · seen from worker = public

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Services | public | 5 Travis Burnette | short | 2 | S12 O:overview C:near-duplicate | Index of the service pages and how to use them on the phone. | prices/price-list, services/maintenance/oil-change, services/maintenance/filters-and-wipers, services/maintenance/spark-plugs, services/maintenance/coolant-service, services/maintenance/scheduled-maintenance, services/maintenance/fuel-system-service, services/maintenance/fleet-pm-service, services/brakes/brake-inspection, services/brakes/pads-and-rotors, services/brakes/calipers-and-drum-brakes, services/brakes/brake-fluid-flush, services/tires/rotation-balance-and-flat-repair, services/tires/alignment, services/tires/new-tires-and-tpms, services/diagnostics/check-engine-light, services/diagnostics/electrical-diagnosis, services/diagnostics/noises-and-vibrations, services/suspension/struts-and-shocks, services/suspension/front-end-parts, services/suspension/wheel-bearings-and-steering-racks, services/ac/ac-check-and-recharge, services/ac/ac-compressor-and-condenser, services/electrical/battery, services/electrical/alternator-and-starter, services/engine/timing-belt, services/engine/drive-belt, services/engine/cooling-system-repairs, services/engine/leaks-and-gaskets, services/engine/ignition-sensors-and-fuel-pump, services/engine/mounts-and-exhaust, services/transmission/transmission-fluid-service, services/transmission/clutch-and-cv-axles, services/transmission/transmission-rebuild, services/inspections/courtesy-inspection, services/inspections/pre-purchase-inspection, services/hybrids |
| `hybrids.md` | Hybrids | public | 10 Kevin Lawson | short | 1 | S5 C:combine-policy-and-price C:near-duplicate-shop-pages | What is and is not done on hybrids, for the counter. | customers/hybrids-and-electric-cars |

### `services/maintenance/` · 7 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `coolant-service.md` | Coolant service | public | 5 Travis Burnette | short | 2 | C:combine-policy-and-price smoke | Coolant drain, flush and fill. | services/engine/cooling-system-repairs |
| `filters-and-wipers.md` | Filters and wipers | public | 5 Travis Burnette | short | 2 | C:fact-in-table smoke | Engine air filter, cabin filter, wiper blades: small jobs sold from the inspection. | services/maintenance/fuel-system-service |
| `fleet-pm-service.md` | Fleet PM service A | public | 4 Greg Whitaker | short | 2 | S1 S16 C:combine-policy-and-price C:fact-only-in-attachment | The preventive-maintenance service for cargo vans; list price and what the company rate does to it. | accounts/company-account-terms, parts/fluids-and-capacities |
| `fuel-system-service.md` | Fuel system service | public | 5 Travis Burnette | short | 2 | C:customer-terms smoke | Induction cleaning and the fuel filter: when it helps and when it is snake oil. | services/diagnostics/check-engine-light |
| `oil-change.md` | Oil change | public | 5 Travis Burnette | medium | 2 | C:fact-in-table C:customer-terms smoke | The most common job: what it includes, the three oils, what to ask, the upsell that is not an upsell. | - |
| `scheduled-maintenance.md` | Scheduled maintenance: 30K, 60K, 90K | public | 5 Travis Burnette | short | 2 | C:combine-policy-and-price C:fact-in-table | The mileage service: what the labour covers and what is priced separately. | - |
| `spark-plugs.md` | Spark plugs and the "tune-up" | public | 5 Travis Burnette | medium | 2 | C:customer-terms C:combine-policy-and-price C:fact-in-table | What a customer means by a tune-up and what the plug job costs by engine. | services/diagnostics/check-engine-light, prices/labour-rates-and-fees, services/engine/ignition-sensors-and-fuel-pump |

### `services/brakes/` · 5 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `brake-fluid-flush.md` | Brake fluid flush | public | 16 Angie Holloway | short | 2 | smoke | Brake fluid exchange: why, when, how it is sold. | - |
| `brake-inspection.md` | Brake inspection | public | 16 Angie Holloway | short | 2 | S7 C:combine-policy-and-price | The inspection every brake complaint starts with. | policies/diagnostic-fees, customers/towing, services/brakes/pads-and-rotors |
| `brake-questions.md` | Brake questions **stale** | public | F3 Brad Keller | short | 1 | S12 S8 C:near-duplicate O:contradiction O:propose | An old FAQ by an advisor who has left: still carries the labour rate and brake prices from before the rise. Stale on purpose (S12). | - |
| `calipers-and-drum-brakes.md` | Calipers and drum brakes | public | 16 Angie Holloway | short | 2 | smoke C:customer-terms | The less common brake jobs: a seized caliper, rear shoes. | parts/returns-and-cores |
| `pads-and-rotors.md` | Pads and rotors | public | 16 Angie Holloway | medium | 2 | S7 S6 S12 C:fact-in-table C:customer-terms C:near-duplicate | The main brake job: pads alone or with rotors, the three parts tiers, what to say. | prices/labour-rates-and-fees, parts/brake-pads-we-fit, how-to/a-comeback-at-the-counter |

### `services/tires/` · 3 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `alignment.md` | Alignment | public | 5 Travis Burnette | short | 2 | C:customer-terms C:combine-policy-and-price | Four-wheel alignment: when, price by vehicle class, which rack. | - |
| `new-tires-and-tpms.md` | New tires and tire-pressure sensors | public | 5 Travis Burnette | medium | 2 | C:fact-in-table C:combine-kb-and-data C:kb-does-not-say | Selling and fitting tires; the fees; TPMS sensors. | services/tires/alignment |
| `rotation-balance-and-flat-repair.md` | Rotation, balance and flat repair | public | 5 Travis Burnette | short | 2 | smoke C:fact-in-table | The three small tire jobs. | services/brakes/brake-inspection, services/tires/new-tires-and-tpms |

### `services/diagnostics/` · 3 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `check-engine-light.md` | Check engine light | public | 10 Kevin Lawson | medium | 2 | S5 C:combine-policy-and-price C:customer-terms | How a check-engine job is booked and explained, in the diagnostician's exact voice. | policies/diagnostic-fees, services/diagnostics/electrical-diagnosis |
| `electrical-diagnosis.md` | Electrical diagnosis | public | 13 Terry Dotson | short | 2 | smoke C:customer-terms | Electrical faults without a warning light. | - |
| `noises-and-vibrations.md` | Noises and vibrations | public | 5 Travis Burnette | short | 2 | C:fact-in-table C:customer-terms | How a noise complaint is taken and inspected. | services/brakes/brake-inspection, services/suspension/front-end-parts, services/tires/rotation-balance-and-flat-repair |

### `services/suspension/` · 3 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `front-end-parts.md` | Front-end parts | public | 16 Angie Holloway | short | 2 | C:fact-in-table C:combine-policy-and-price | Sway bar links and bushings, control arms, ball joints, tie rods. | - |
| `struts-and-shocks.md` | Struts and shocks | public | 16 Angie Holloway | short | 2 | S7 C:customer-terms C:fact-in-table | Front struts and rear shocks: how they are found, sold in pairs, and often deferred. | services/tires/alignment |
| `wheel-bearings-and-steering-racks.md` | Wheel bearings and steering racks | public | 16 Angie Holloway | short | 2 | smoke C:customer-terms | Two bigger jobs: the humming bearing and the leaking rack. | - |

### `services/ac/` · 2 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `ac-check-and-recharge.md` | A/C check and recharge | public | 13 Terry Dotson | medium | 2 | S11 C:fact-in-table C:combine-policy-and-price C:customer-terms C:kb-does-not-say | The summer job: performance check, the two refrigerants, what a recharge can and cannot fix. | services/ac/ac-compressor-and-condenser |
| `ac-compressor-and-condenser.md` | A/C compressor and condenser | public | 13 Terry Dotson | short | 2 | C:combine-policy-and-price S11 | The two big A/C repairs. | - |

### `services/electrical/` · 2 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `alternator-and-starter.md` | Alternator and starter | public | 13 Terry Dotson | short | 2 | C:customer-terms smoke | Charging and starting repairs. | - |
| `battery.md` | Battery | public | 13 Terry Dotson | short | 2 | S11 C:fact-in-table C:combine-policy-and-price | Battery test and replacement; the November rush; bulbs. | services/electrical/alternator-and-starter |

### `services/engine/` · 6 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `cooling-system-repairs.md` | Cooling system repairs | public | 5 Travis Burnette | medium | 2 | C:fact-in-table C:combine-policy-and-price C:kb-does-not-say | Overheating and leaks: pressure test, water pump, thermostat, radiator. | customers/towing, services/engine/timing-belt, services/maintenance/coolant-service |
| `drive-belt.md` | Drive belt | public | 5 Travis Burnette | short | 2 | C:near-duplicate C:customer-terms | The serpentine belt: not the timing belt. | services/engine/timing-belt |
| `ignition-sensors-and-fuel-pump.md` | Ignition, sensors and fuel pump | public | 10 Kevin Lawson | medium | 2 | C:fact-in-table smoke | The repairs that most often follow a check-engine diagnosis. | - |
| `leaks-and-gaskets.md` | Leaks and gaskets | public | 5 Travis Burnette | short | 2 | C:kb-does-not-say C:customer-terms | Oil leaks, and the one gasket on the price list. | - |
| `mounts-and-exhaust.md` | Mounts and exhaust | public | 5 Travis Burnette | short | 2 | C:kb-does-not-say smoke | Engine mounts and the rear exhaust; what is not on the list. | services/diagnostics/check-engine-light |
| `timing-belt.md` | Timing belt **stale** | public | 5 Travis Burnette | medium | 1 | S12 S8 O:propose O:find-waiting O:contradiction C:combine-policy-and-price | The timing-belt job, as written before the price rise: old labour rate, old total, and a same-day promise. Stale on purpose (S12); a correction is proposed and waiting. | - |

### `services/transmission/` · 3 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `clutch-and-cv-axles.md` | Clutch and CV axles | public | 5 Travis Burnette | short | 2 | smoke C:customer-terms | Two driveline repairs. | - |
| `transmission-fluid-service.md` | Transmission fluid service | public | 5 Travis Burnette | short | 2 | C:customer-terms C:fact-in-table C:near-duplicate | Drain and fill against machine exchange, and gear oil; what customers call a flush. | services/transmission/transmission-rebuild |
| `transmission-rebuild.md` | Transmission rebuild | public | 5 Travis Burnette | short | 2 | C:kb-does-not-say C:combine-policy-and-price C:fact-in-table | The sublet rebuild: what we do, what the specialist does, price, time, deposit, warranty. | policies/deposits |

### `services/inspections/` · 2 · seen from inherits worker

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `courtesy-inspection.md` | Courtesy inspection | public | 16 Angie Holloway | short | 1 | C:three-page-procedure S7 S5 | The free inspection from the counter's side: how the result is presented. | shop-floor/courtesy-inspection, how-to/writing-an-estimate |
| `pre-purchase-inspection.md` | Pre-purchase inspection | public | 5 Travis Burnette | short | 2 | smoke C:combine-policy-and-price | Staff page for the used-car inspection. | customers/pre-purchase-inspection |

### `prices/` · 4 · seen from worker = public for the price list; the other three files junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `counter-price-sheet.pdf` | Counter price sheet | staff | 2 Claire Brennan | PDF, 2 pages, text | 2 | S12 C:fact-only-in-attachment C:fact-in-table | Printed price sheet for the counters: menu services on page 1, prices by vehicle class on page 2. | - |
| `how-prices-change.md` | How prices change | staff | 2 Claire Brennan | short | 1 | S12 S8 O:find-what-changed O:contradiction | The rule written after S8: who changes a price, which page changes first, and what happens to service pages and open estimates. | prices/price-list, prices/labour-rates-and-fees, customers/prices-for-common-services |
| `labour-rates-and-fees.md` | Labour rates, fees and vehicle classes | staff | 2 Claire Brennan | medium | 2 | S12 S1 C:fact-in-table C:combine-policy-and-price | The posted and company-account hour, shop supplies, tax, tire fees, and how a price is scaled for bigger vehicles. | - |
| `price-list.md` | Price list | public | 2 Claire Brennan | long | 3 | S8 S12 S7 C:fact-in-table C:combine-policy-and-price C:long-page-by-section C:kb-does-not-say | The current price of every catalogue job; the single page a price is quoted from. Long: over the read limit, so it is read by section. | prices/labour-rates-and-fees, prices/counter-price-sheet.pdf |

### `policies/` · 13 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Policies | staff | 2 Claire Brennan | short | 1 | O:overview C:near-duplicate | Index of the policy pages. | policies/discounts, policies/warranty, policies/estimates-and-approvals, policies/diagnostic-fees, policies/customer-supplied-parts, policies/deposits, policies/cancellations-and-no-shows, policies/storage-of-uncollected-cars, policies/complaints, policies/voids-and-refunds, policies/customer-records, policies/service-standards |
| `cancellations-and-no-shows.md` | Cancellations and no-shows | staff | 4 Greg Whitaker | short | 1 | C:kb-does-not-say smoke | What happens when a booked customer does not come. | - |
| `complaints.md` | Complaints | staff | 4 Greg Whitaker | medium | 2 | S8 S1 C:fact-in-table C:combine-policy-and-price | Staff procedure for a complaint: who hears it, who decides, how fast. | policies/discounts |
| `customer-records.md` | Customer records | staff | 3 Donna Ledford | short | 1 | S15 S2 S7 | How a customer and a car are entered so that records do not multiply. | - |
| `customer-supplied-parts.md` | Customer-supplied parts | staff | 2 Claire Brennan | short | 1 | C:combine-policy-and-price S15 | Staff rules for fitting parts the customer brings. | customers/bringing-your-own-parts |
| `deposits.md` | Deposits | staff | 3 Donna Ledford | short | 1 | C:fact-in-table C:combine-policy-and-price S15 | When a deposit is taken, how much, and what is refunded. | policies/voids-and-refunds, parts/returns-and-cores |
| `diagnostic-fees.md` | Diagnostic and inspection fees | staff | 1 Ray Brennan | short | 2 | C:combine-policy-and-price C:customer-terms | Why diagnosis is charged and never credited; the founder's hobby-horse. | - |
| `discounts.md` | Discount policy | staff | 2 Claire Brennan | medium | 2 | S2 S8 C:policy-vs-team-note O:find-what-changed C:combine-policy-and-price | The discount rule created after story S2. | - |
| `estimates-and-approvals.md` | Estimates and approvals | staff | 2 Claire Brennan | medium | 1 | S1 S7 S8 C:three-page-procedure C:combine-policy-and-price | Staff rules for estimates: how fast, what is on them, how approval is recorded, what happens to declined work. | customers/estimates-and-approvals, accounts/company-account-terms, how-to/getting-approval |
| `service-standards.md` | Service standards | staff | 2 Claire Brennan | short | 2 | S3 S1 S6 S9 S12 C:fact-in-table C:combine-kb-and-data | One table of how fast the company promises to answer, call back, estimate and decide; the yardstick for several stories. | - |
| `storage-of-uncollected-cars.md` | Cars not collected | staff | 2 Claire Brennan | short | 1 | C:policy-vs-team-note O:contradiction S15 | Storage of finished cars: free days, daily charge, the 30-day step. Contradicted on purpose by a team note. | how-to/getting-approval |
| `voids-and-refunds.md` | Voids and refunds | staff | 2 Claire Brennan | short | 1 | S2 S15 O:find-what-changed | The rule on voiding orders and giving money back; written with the discount rule after S2. | - |
| `warranty.md` | Warranty | staff | 2 Claire Brennan | medium | 2 | S12 S1 S6 C:near-duplicate C:fact-in-table C:combine-policy-and-price C:kb-does-not-say | The current warranty in full, for staff: terms, exclusions, who decides, how a claim is written up. | shop-floor/when-a-car-comes-back, how-to/a-comeback-at-the-counter, customers/warranty |

### `accounts/` · 9 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `a1.md` | Nickajack Delivery | staff | 4 Greg Whitaker | medium | 2 | S1 S16 S4 C:fact-in-table | Standing instructions for the anchor account A1. | services/maintenance/fleet-pm-service, accounts/company-account-terms |
| `a2.md` | Millsaps Heating & Plumbing | staff | 16 Angie Holloway | short | 2 | S1 S5 C:combine-policy-and-price | Standing instructions for account A2, the happy path. | - |
| `a3.md` | Moccasin Bend Janitorial Services | staff | 5 Travis Burnette | short | 1 | S1 smoke | Standing instructions for account A3. | - |
| `a4.md` | Missionary Ridge Driving School | staff | 16 Angie Holloway | short | 1 | S1 C:combine-kb-and-data C:kb-does-not-say | Standing instructions for account A4; says seven cars, which is out of date by one. | - |
| `a5.md` | Cumberland Bend Electric **stale** | staff | 22 Dale Hutchins | tiny | 1 | S1 C:kb-does-not-say C:near-duplicate-shop-pages | Account A5 as Charlotte Pike wrote it before the account left: thin, and silent on everything that went wrong. | - |
| `a6.md` | Sourwood Catering Co. **stale** | staff | 5 Travis Burnette | short | 1 | S1 O:contradiction C:combine-kb-and-data | Account A6 as it stood eight months ago: names a fleet contact and an advisor who have both gone. | - |
| `company-account-terms.md` | Company accounts | staff | 2 Claire Brennan | medium | 4 | S1 S4 S16 C:fact-in-table C:combine-policy-and-price O:contradiction C:policy-vs-team-note | The terms every company account is served on: payment days, price class, priority, who may approve work. Story S1's page. | accounts/small-business-customers, accounts/a1, accounts/a2, accounts/a3, accounts/a4, accounts/a5, accounts/a6, policies/warranty, accounts/opening-a-company-account |
| `opening-a-company-account.md` | Opening a company account | staff | 2 Claire Brennan | short | 1 | S1 C:three-page-procedure | Who qualifies for an account and the steps to open one. | accounts/company-account-terms |
| `small-business-customers.md` | Small business customers | staff | 4 Greg Whitaker | short | 1 | S1 C:near-duplicate C:combine-policy-and-price | Businesses with a few vehicles and no account: how they differ from an account. | accounts/opening-a-company-account |

### `accounts/credit/` · 1 · seen from middle

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `credit-limits-and-collections.md` | Credit limits and collections | middle | 3 Donna Ledford | short | 1 | S1 S16 V:middle C:fact-in-table C:combine-kb-and-data | Middle rank and up: each account's credit limit and the steps taken when a statement is overdue. | - |

### `how-to/` · 15 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | How we do things | staff | 4 Greg Whitaker | short | 1 | O:overview C:three-page-procedure | Index of the counter procedures, in the order a job passes through them. | how-to/taking-a-call, how-to/price-objections, how-to/booking-a-visit, how-to/checking-a-car-in, how-to/company-vehicle-at-the-counter, shop-floor/courtesy-inspection, how-to/writing-an-estimate, how-to/getting-approval, parts/ordering-parts, how-to/handing-a-car-back, how-to/closing-the-till, how-to/a-comeback-at-the-counter, policies/complaints, how-to/missed-calls-and-call-backs, how-to/chats-and-messages, how-to/stocktake-day, how-to/using-this-knowledge-base |
| `a-comeback-at-the-counter.md` | A comeback at the counter | staff | 4 Greg Whitaker | medium | 1 | S6 S1 C:fact-in-table C:combine-policy-and-price | What an advisor does and says when a customer returns with the same problem. | shop-floor/when-a-car-comes-back |
| `booking-a-visit.md` | Booking a visit | staff | 5 Travis Burnette | medium | 2 | S4 S7 S5 C:three-page-procedure O:contradiction | How a booking is entered so the day works; step 6 is the read-back that the declined team note repeated (S4). | policies/customer-records, policies/cancellations-and-no-shows |
| `chats-and-messages.md` | Chats and messages | staff | 6 Maya Torres | medium | 1 | S7 S12 C:combine-kb-and-data V:public | How web chat and messenger conversations are answered alongside the assistant. | customers/README, prices/price-list |
| `checking-a-car-in.md` | Checking a car in | staff | 5 Travis Burnette | short | 1 | C:three-page-procedure S15 S7 | The counter's part of receiving a car: walk-round, mileage, the complaint, keys. | - |
| `closing-the-till.md` | Closing the till | staff | 3 Donna Ledford | short | 1 | S2 C:near-duplicate-shop-pages C:combine-policy-and-price | The company procedure for counting the cash drawer at the end of the day. | shops/main/opening-and-closing, shops/east/opening-and-closing, shops/west/opening-and-closing, policies/voids-and-refunds |
| `company-vehicle-at-the-counter.md` | A company vehicle at the counter | staff | 4 Greg Whitaker | short | 2 | S4 S1 C:combine-policy-and-price C:policy-vs-team-note | What changes when the car belongs to a company account: unit number, purchase order, who may approve. | accounts/company-account-terms, accounts/small-business-customers |
| `getting-approval.md` | Getting approval | staff | 16 Angie Holloway | medium | 1 | C:three-page-procedure S1 S7 C:fact-in-table | Step three of the inspection-to-approval procedure: sending the estimate, chasing it, recording the answer. | how-to/writing-an-estimate, how-to/company-vehicle-at-the-counter, parts/ordering-parts |
| `handing-a-car-back.md` | Handing a car back | staff | 5 Travis Burnette | short | 1 | S7 S8 C:three-page-procedure | The pick-up: walking the bill, old parts, deferred work, the next visit. | policies/complaints |
| `missed-calls-and-call-backs.md` | Missed calls and call backs | staff | 4 Greg Whitaker | medium | 2 | S3 S1 C:combine-kb-and-data | How the missed-call list is worked; the standard after the early desk shift. | shops/main/how-the-day-runs |
| `price-objections.md` | Price objections | staff | 16 Angie Holloway | medium | 1 | S4 S2 C:fact-in-table C:combine-policy-and-price C:customer-terms | What to say when a customer doubts the price; the weakest check on most scorecards. | policies/diagnostic-fees, policies/discounts |
| `stocktake-day.md` | Stocktake day | staff | 9 Marcus Gaines | medium | 2 | S13 C:combine-kb-and-data | What happens on the half-yearly stocktake afternoon (S13). | customers/hours-and-locations |
| `taking-a-call.md` | Taking a call | staff | 16 Angie Holloway | medium | 2 | S4 S3 S8 C:fact-in-table C:near-duplicate C:combine-kb-and-data | How an advisor handles a first call; teaches exactly what the call scorecard checks, in the best closer's voice. | prices/price-list, parts/ordering-parts, how-to/price-objections |
| `using-this-knowledge-base.md` | Using and fixing this knowledge base | staff | 2 Claire Brennan | medium | 2 | S12 S4 O:propose O:find-waiting O:find-what-changed | How to search, how to read a page's date, how a correction is proposed and decided. | prices/price-list, customers/README, how-to/README |
| `writing-an-estimate.md` | Writing an estimate | staff | 5 Travis Burnette | medium | 2 | C:three-page-procedure S8 S12 S7 | Step two of the inspection-to-approval procedure: turning inspection findings into an estimate. | shop-floor/courtesy-inspection, prices/price-list, prices/labour-rates-and-fees, how-to/getting-approval |

### `parts/` · 10 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `brake-pads-we-fit.md` | Brake pads we fit | staff | 9 Marcus Gaines | short | 1 | S6 S1 C:combine-kb-and-data C:fact-in-table | The pad lines by tier and the parts manager's warning about the Nashville supplier's house brand (S6). | - |
| `fleet-fluid-sheet.pdf` | Fleet fluid sheet (printed copy) | staff | 9 Marcus Gaines | PDF, 1 page landscape, text | 1 | C:fact-only-in-attachment C:fact-in-table S1 | A one-page print of the fluid sheet: the readable copy. | - |
| `fleet-fluid-sheet.xlsx` | Fleet fluid sheet (spreadsheet) | staff | 9 Marcus Gaines | XLSX, one sheet | 2 | C:unreadable-binary C:fact-only-in-attachment | The parts manager's working sheet of oil, coolant and transmission fluid by vehicle. Not readable by the assistant. | - |
| `fluids-and-capacities.md` | Fluids and capacities | staff | 9 Marcus Gaines | short | 1 | C:fact-only-in-attachment C:unreadable-binary O:contradiction | Pointer page: what fluid types we use and where the per-vehicle quantities are (only in the attached sheet). | parts/fleet-fluid-sheet.xlsx, parts/fleet-fluid-sheet.pdf |
| `ordering-parts.md` | Ordering parts for a job | staff | 9 Marcus Gaines | short | 1 | S8 S6 C:three-page-procedure | How a part gets from the order to the bay, and when an advisor may promise a time. | policies/deposits, parts/suppliers |
| `parts-tiers-and-brands.md` | Parts tiers and brands | staff | 9 Marcus Gaines | medium | 1 | S6 C:fact-in-table C:customer-terms | The three tiers and which brand we quote in each, by line. | prices/price-list |
| `returns-and-cores.md` | Returns and cores | staff | 9 Marcus Gaines | short | 1 | C:fact-in-table C:combine-policy-and-price | What can go back to a supplier, by when, and how cores work. | - |
| `stock-we-keep.md` | Stock we keep | staff | 9 Marcus Gaines | short | 1 | S13 C:kb-does-not-say C:combine-policy-and-price | What is on the shelf at the home shops, and how stock is counted. | how-to/stocktake-day, parts/fluids-and-capacities |
| `sublet-work.md` | Sublet work | staff | 9 Marcus Gaines | short | 1 | C:kb-does-not-say C:combine-policy-and-price S6 | Work we send out or bring in: transmission rebuilds, glass, towing. How it is ordered and billed. | prices/price-list, policies/deposits, services/transmission/transmission-fluid-service, customers/towing |
| `suppliers.md` | Suppliers | staff | 9 Marcus Gaines | medium | 2 | S6 C:fact-in-table C:kb-does-not-say C:combine-kb-and-data | Who we buy from, what each delivers, when to order, and the parts manager's own notes on each. | parts/brake-pads-we-fit, parts/sublet-work |

### `shops/` · 1 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Our three shops | staff | 2 Claire Brennan | medium | 1 | S9 S13 S15 C:fact-in-table C:near-duplicate-shop-pages O:contradiction | The three shops side by side: bays, people, hours, time zone, who runs each. | shops/main/README, shops/east/README, shops/west/README |

### `shops/main/` · 6 · seen from inherits junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | East Main | staff | 5 Travis Burnette | tiny | 1 | C:near-duplicate-shop-pages O:overview | Front page of the flagship's own pages. | shops/main/hours-and-getting-here, shops/main/who-is-who, shops/main/opening-and-closing, shops/main/how-the-day-runs, shops/main/saturdays |
| `hours-and-getting-here.md` | East Main: hours and getting here | staff | 5 Travis Burnette | short | 1 | C:near-duplicate-shop-pages S13 | East Main's hours, parking, shuttle and key drop for staff to tell customers. | customers/hours-and-locations |
| `how-the-day-runs.md` | East Main: how the day runs | staff | 5 Travis Burnette | medium | 2 | S3 S5 C:combine-kb-and-data | The flagship's local habits: the morning rush, lunch cover, diagnostics queue, Thursday. | - |
| `opening-and-closing.md` | East Main: opening and closing | staff | 4 Greg Whitaker | short | 2 | C:near-duplicate-shop-pages S3 S2 | Opening and closing checklist for the flagship: who, till float, where the deposit goes. | how-to/missed-calls-and-call-backs, how-to/closing-the-till, shops/main/saturdays |
| `saturdays.md` | East Main: Saturdays | staff | 4 Greg Whitaker | short | 1 | C:near-duplicate-shop-pages C:combine-policy-and-price S14 | What the Saturday morning shift takes and does not take. | - |
| `who-is-who.md` | East Main: who is who | staff | 5 Travis Burnette | medium | 3 | C:fact-in-table S3 S8 C:near-duplicate-shop-pages | People at the flagship with what each does and their extension. | - |

### `shops/east/` · 5 · seen from inherits junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Bonny Oaks | staff | 16 Angie Holloway | tiny | 1 | C:near-duplicate-shop-pages | Front page of the second home shop's pages. | shops/east/hours-and-getting-here, shops/east/who-is-who, shops/east/opening-and-closing, shops/east/how-the-day-runs |
| `hours-and-getting-here.md` | Bonny Oaks: hours and getting here | staff | 16 Angie Holloway | short | 1 | C:near-duplicate-shop-pages S13 | Bonny Oaks's hours, parking and key drop; no Saturday. | customers/hours-and-locations |
| `how-the-day-runs.md` | Bonny Oaks: how the day runs | staff | 16 Angie Holloway | short | 1 | S5 S4 C:combine-kb-and-data | The east shop's habits in its lead advisor's words: the photo before the price, Mondays, cover. | accounts/a2 |
| `opening-and-closing.md` | Bonny Oaks: opening and closing | staff | 16 Angie Holloway | short | 1 | C:near-duplicate-shop-pages S2 S1 | Opening and closing at Bonny Oaks: different float and deposit route from East Main. | how-to/closing-the-till |
| `who-is-who.md` | Bonny Oaks: who is who | staff | 16 Angie Holloway | short | 1 | S5 C:near-duplicate-shop-pages C:fact-in-table | People at Bonny Oaks. | - |

### `shops/west/` · 4 · seen from inherits junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Charlotte Pike **stale** | staff | 22 Dale Hutchins | tiny | 2 | S13 S2 C:near-duplicate-shop-pages O:contradiction C:combine-kb-and-data C:broken-link C:kb-does-not-say | The bought shop's front page as its manager wrote it thirteen months ago: thin and out of date on Saturday hours and on who works the counter. | shops/west/opening-and-closing, shops/west/parts, shops/west/answering-the-phone, shops/west/tow-trucks (one broken on purpose) |
| `answering-the-phone.md` | Charlotte Pike: answering the phone | staff | 24 Jasmine Bolden | short | 1 | S3 S4 C:near-duplicate S9 | The newest Nashville advisor's page on how the phone is answered there; the bright spot in a thin folder. | - |
| `opening-and-closing.md` | Charlotte Pike: opening and closing | staff | 22 Dale Hutchins | short | 2 | S2 C:near-duplicate-shop-pages O:find-what-changed | Charlotte Pike's short checklist, with the till rule the managing owner changed after S2. | how-to/closing-the-till |
| `parts.md` | Charlotte Pike: parts | staff | 22 Dale Hutchins | tiny | 1 | S6 C:near-duplicate-shop-pages O:contradiction S15 | How Nashville orders parts, in its manager's words. | - |

### `team/` · 6 · seen from junior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `meetings.md` | Meetings | staff | 2 Claire Brennan | short | 1 | S9 S16 C:combine-kb-and-data | The standing meetings: the Monday managers' meeting, the morning huddle. | - |
| `new-advisor-first-two-weeks.md` | New advisor: the first two weeks | staff | 5 Travis Burnette | medium | 1 | S8 S4 C:three-page-procedure | Onboarding checklist for a new service advisor, written when the newcomer started. | prices/price-list, how-to/taking-a-call, how-to/booking-a-visit, how-to/checking-a-car-in, policies/discounts, policies/warranty |
| `new-technician-first-week.md` | New technician: the first week | staff | 8 Randy Elrod | short | 1 | S14 smoke | What a new technician is shown in the first week. | shop-floor/before-a-car-leaves |
| `staff-handbook.docx` | Staff handbook | staff | 2 Claire Brennan | DOCX with heading styles, about 9 pages | 2 | S14 C:fact-only-in-attachment V:worker C:kb-does-not-say | The employee handbook: attendance, pay periods, time off, holidays, allowances, conduct. | - |
| `the-call-in-eight-moves.pptx` | The call, in eight moves | staff | 16 Angie Holloway | PPTX, 10 titled slides | 1 | S4 C:fact-only-in-attachment C:near-duplicate | The lead advisor's ten-slide training deck on taking a call. | - |
| `who-is-who.md` | Who is who | staff | 2 Claire Brennan | medium | 5 | S2 S14 C:fact-in-table O:contradiction C:combine-kb-and-data | The company directory: everyone who works here now, by shop, with role and extension. The page that is right when a shop page is not. | - |

### `office/` · 4 · seen from middle

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `month-end-close.md` | Month-end close | middle | 3 Donna Ledford | medium | 2 | S2 S15 V:middle O:find-what-changed | The bookkeeper's month-end checklist; the check that caught the missing money. | office/statements-and-receivables, office/payroll-hours |
| `payroll-hours.md` | Payroll hours | middle | 3 Donna Ledford | short | 1 | S14 V:middle C:kb-does-not-say | How attendance becomes payroll hours. | - |
| `statements-and-receivables.md` | Statements and receivables | middle | 3 Donna Ledford | short | 1 | S1 S16 S15 V:middle | How company-account statements are issued and payments applied. | accounts/credit/credit-limits-and-collections |
| `till-and-deposits.md` | Till differences and deposits | middle | 3 Donna Ledford | short | 1 | S2 V:middle C:near-duplicate-shop-pages | The office side of the cash: the bag log, the bank, the differences book. | - |

### `management/` · 5 · seen from senior

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `comeback-review.md` | Comeback review | senior | 4 Greg Whitaker | short | 1 | S6 S14 V:senior C:fact-in-table C:combine-kb-and-data | Senior rank: how comebacks are counted and reviewed each month, and where the review is not happening. | - |
| `parts-pricing-matrix.md` | Parts pricing matrix | senior | 2 Claire Brennan | medium | 2 | V:senior C:fact-in-table C:combine-policy-and-price | Senior rank: the margins parts are priced at, by tier and kind. | - |
| `pay-and-till.md` | Pay and till | senior | 2 Claire Brennan | medium | 2 | V:senior S12 S2 C:kb-does-not-say C:fact-in-table | Senior rank: how each job is paid, without amounts, and who sees the till counts. The page a junior is refused (stories S12.5). | how-to/closing-the-till |
| `schedule-rules.md` | Schedule rules | senior | 4 Greg Whitaker | medium | 3 | S3 S5 S14 V:senior C:fact-in-table | Senior rank: the cover each shop needs and the rules the planner follows. | - |
| `what-we-found-at-west.md` | What we found at Charlotte Pike | senior | 2 Claire Brennan | medium | 2 | S2 V:senior C:combine-kb-and-data O:find-what-changed | Senior rank: the managing owner's memo on the discounts, voids and till shortages (S2) and what was changed. | policies/discounts, policies/voids-and-refunds, shops/west/opening-and-closing |

### `management/owners/` · 1 · seen from administrator

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `west-plan.md` | Charlotte Pike: the plan | admin | 2 Claire Brennan | medium | 1 | S6 S9 V:administrator C:fact-in-table | Administrator only: the managing owner's private plan for the bought shop. | - |

### `playbooks/` · 6 · seen from administrator (pinned by the product's import)

| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |
|---|---|---|---|---|---:|---|---|---|
| `README.md` | Playbooks | admin | 2 Claire Brennan | short | 1 | V:administrator O:overview | Index of the rank playbooks; states plainly that only the administrator can open them. | playbooks/technician, playbooks/advisor, playbooks/lead-and-office, playbooks/manager, playbooks/owner, shop-floor/README, how-to/README |
| `advisor.md` | Playbook: service advisors | admin | 2 Claire Brennan | medium | 3 | S4 S3 S7 V:administrator | Junior rank: what an advisor uses Traciora for, with the call scorecard as the centre. | how-to/taking-a-call, how-to/missed-calls-and-call-backs |
| `lead-and-office.md` | Playbook: lead advisors and the office | admin | 2 Claire Brennan | medium | 1 | S12 O:propose V:administrator | Middle rank: what the lead advisors and the office manager can do beyond an advisor. | - |
| `manager.md` | Playbook: managers | admin | 2 Claire Brennan | medium | 2 | S4 S5 S12 S14 O:find-waiting V:administrator | Senior rank: planning shifts, deciding notes and page changes, seeing colleagues' phone performance. | - |
| `owner.md` | Playbook: owner and administrator | admin | 2 Claire Brennan | medium | 2 | S10 S12 V:administrator C:fact-in-table | Administrator: the managing owner's own notes on running the product. | team/who-is-who, prices/how-prices-change |
| `technician.md` | Playbook: technicians | admin | 2 Claire Brennan | short | 2 | S14 V:administrator | Worker rank: what a technician does in Traciora and what the assistant will and will not answer. | - |

## 5. Planted on purpose

Each plant has a number, where it lives, and the questions it serves. "By" is the cast slot and rank of the asker; the customers' assistant is asked by a customer. Expected answers are for the English configuration and hold for any T. Proof is the page or pages an answer must rest on.

### Story plants

**P1. Two pages still at the labour rate from before the rise (S12).** `services/engine/timing-belt.md` (3.2 h at $125.00, $688.00, "same day") and `services/brakes/brake-questions.md` (an orphan FAQ by an advisor who left: $125.00 an hour, $475.00, $452.27, $223.86, $214.77, $46.25, $141.00). The price list, the rates page, the public prices page and 36 service pages are current. Both stale pages are public: the website assistant can read them beside the price list.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P1.1 | What do we charge for a timing belt on a 2011 Outback 2.5? | 7, junior | $720.00 with the standard kit (economy $690.00, premium $760.00), before supplies and tax; $741.60 with shop supplies; $810.20 with tax. Says the service page shows $688.00 and is out of date | `prices/price-list.md` (Engine & cooling), `services/engine/timing-belt.md` |
| P1.2 | Which pages still show the old prices? | 4, senior | Exactly two: the timing belt page and the brake questions page. Not the rates page or "How prices change", which mention $125.00 as history | the two pages; `prices/labour-rates-and-fees.md` |
| P1.3 | A customer says we quoted $475 for front pads and rotors. Is that our price? | 17, junior | No: $493.00 standard. $475.00 is on the brake questions page, written before the rise | `prices/price-list.md`, `services/brakes/brake-questions.md` |
| P1.4 | Can I tell a caller a timing belt is done the same day? | 7, junior | No. The timing belt page says so, but the ordering page forbids "same day" on job length alone; book a full day | `parts/ordering-parts.md`, `how-to/taking-a-call.md`, `services/engine/timing-belt.md` |
| P1.5 | When did the labour rate change, and from what to what? | 6, junior | On the date of `@price_rise`: $125.00 to $135.00; company rate $112.50 to $121.50; menu prices up 8 %; parts unchanged | `prices/labour-rates-and-fees.md`, `prices/how-prices-change.md` |
| P1.6 | How much is a timing belt on a 2011 Outback? | customer | $720.00 with the standard kit, before tax, from the price list. It can also read the stale service page and must not answer $688.00 | `prices/price-list.md` |

**P2. An old warranty page beside the current one (S12).** `customers/warranty-policy.md` (12 months or 12,000 miles, electrical parts 90 days, only at the shop that did the work; effective T-6y, reviewed T-38mo, signed by the founder) stands in the public folder beside `customers/warranty.md` (24/24, in force from `@warranty_2424`); the full staff terms are `policies/warranty.md`.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P2.1 | What is our warranty? | 6, junior | 24 months or 24,000 miles, parts and labour, at all three shops; names the old page as out of date and says it still claims 12 months or 12,000 miles | `customers/warranty.md`, `policies/warranty.md`, `customers/warranty-policy.md` |
| P2.2 | Work was done at Bonny Oaks. Can East Main do the warranty repair? | 17, junior | Yes, any of the three shops. The old page says the original shop only | same |
| P2.3 | How long is a new alternator covered? | 7, junior | 24 months or 24,000 miles (12/12 on a business vehicle). Not 90 days: that is the old page's rule for electrical parts | same |
| P2.4 | Which warranty page is in force, and how do you know? | 4, senior | "Our warranty" and the staff "Warranty": in force from `@warranty_2424`, reviewed T-4mo, by the managing owner; the other is effective T-6y, reviewed T-38mo, and the current page says an older one exists | both pages |
| P2.5 | What is your warranty on brake work? | customer | 24 months or 24,000 miles on the work; pads 12 months or 12,000 miles against defects and noise. It can read the old page too and must not answer 12 months for the work | `customers/warranty.md` |

**P3. A correction that waits (S12).** Proposed by slot 5 at `@belt_proposal`, the full open day after the discount, on the timing belt page; pending; deciders slots 4, 22, 1, 2; the design puts it in slot 4's "needs you".

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P3.1 | What is waiting to be approved in the knowledge base? | 4, senior | One proposal: Travis Burnette's correction to the timing belt page | the proposal; the `knowledge.proposed` line in his Inbox |
| P3.2 | Who proposed it, when and why? What exactly changes? | 2, admin | Slot 5, at `@belt_proposal`; old labour rate; $688.00 becomes $720.00, $400.00 becomes $432.00, the same-day paragraph is replaced | fact sheet `pending_proposal` |
| P3.3 | Has it waited longer than our own standard? | 2, admin | No: it was proposed one working day ago; the standard is five working days | `policies/service-standards.md` |
| P3.4 | If it is approved, are all the old prices gone? | 5, middle | No: the brake questions page is as stale and has no proposal | P1 |
| P3.5 | Can Travis approve it himself? | 5, middle | No: he may propose, not publish, and nobody decides their own proposal | `how-to/using-this-knowledge-base.md` |

**P4. The discount policy written after the theft (S2).** `policies/discounts.md`, created at `@discount_rule` by slot 2, one later edit; with `policies/voids-and-refunds.md`, `how-to/closing-the-till.md`, the changed `shops/west/opening-and-closing.md` and the senior memo.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P4.1 | What is our rule on discounts, and since when? | 24, junior | Over 10 % of the bill before tax needs the shop manager's approval before the bill is closed, recorded on the order; since `@discount_rule`; the team note agrees | `policies/discounts.md` |
| P4.2 | Who wrote it and what has changed since? | 2, admin | Slot 2 created it; one edit, by slot 4 at `@belt_proposal`, added "measured before sales tax" | page history |
| P4.3 | I want to give 12 % to end an argument. Can I? | 23, junior | Not alone: up to 10 % with a written reason; above that slot 22 approves first | `policies/discounts.md` |
| P4.4 | Was $80 off the timing belt bill inside the rules? | 2, admin | Yes: $80.00 of $741.60 is 10.8 %, over 10 %, approved by slot 4 and recorded | page + the order |
| P4.5 | A customer says the old advisor gave him a cash price | 24, junior | There is no cash discount; the price is the same however he pays | `policies/discounts.md`, `how-to/price-objections.md` |
| P4.6 | What happened at Charlotte Pike with the discounts? | 23, junior; then 4, senior | Junior: only that the rule exists because of what was found there. Senior: the memo: one advisor, six months, 22 % against 3 %, 14 voids, 19 short days, $11,400 as the outside figure, the true loss not in the data | `management/what-we-found-at-west.md` (senior) |

**P5. Company-account terms (S1).** `accounts/company-account-terms.md` and one page per account.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P5.1 | What are Nickajack's terms, and what must be on every order? | 6, junior | 30 days from the statement, company rate, its purchase-order number before work starts | terms page, `accounts/a1.md` |
| P5.2 | A Millsaps driver says go ahead with $380 of extra work | 17, junior | No: a driver approves up to $300 for the visit; call Tina Ragsdale, who approves up to $1,000 a vehicle (Hal Millsaps above that) | `accounts/company-account-terms.md`, the account page |
| P5.3 | A Nickajack driver approves $380 of found work | 6, junior | No: the limit is $300 for the visit; call Lonnie Coffey | `accounts/company-account-terms.md` |
| P5.4 | Is the rule in the note "a company driver cannot approve work over 300 USD; call the fleet contact" already written down? | 4, senior | Yes, on the Company accounts page: up to $300 for the whole visit, above that the fleet contact. The note repeats the page | `accounts/company-account-terms.md` |
| P5.5 | Who approves work for Sourwood Catering? | 6, junior | Erin Castillo (terms table, reviewed T-2mo). The account's own page still names Bobby Shadden and an advisor who left: both out of date | terms page, `accounts/a6.md` |
| P5.6 | What does Nickajack pay for a PM service A? | 5, middle | $243.53 before supplies and tax: 1.5 h at $121.50 plus oil and filter less 10 % | `services/maintenance/fleet-pm-service.md`, terms page |
| P5.7 | What is Nickajack's credit limit? | 6, junior; then 3, middle | Junior: not available to her. Middle: $30,000 | `accounts/credit/credit-limits-and-collections.md` |
| P5.8 | Which accounts come first, and when? | 16, middle | Any company vehicle that cannot work is seen the day it arrives; Millsaps has Monday 7:30 at Bonny Oaks for five vans and comes first on Monday mornings | terms page, Millsaps page |

**P6. Changed hours for the stocktake afternoon (S13).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P6.1 | Are you open on the afternoon of the stocktake day? | customer | No: all three shops close at noon; open from 7:30; pick up before noon or next morning; the key drop stays open | `customers/hours-and-locations.md` |
| P6.2 | What do I do with bookings that day? | 7, junior | Nothing after 10:30, nothing over two hours; everyone counts from noon | `how-to/stocktake-day.md` |
| P6.3 | Is Charlotte Pike open on Saturdays? | 24, junior | No, Monday to Friday. The shop's own page says Saturday 8 to 12 and is thirteen months old | `customers/hours-and-locations.md`, `shops/README.md`, `shops/west/README.md` |
| P6.4 | Which holidays are you closed? | customer | New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Christmas Day; on the nearest weekday when one falls on a weekend | `customers/hours-and-locations.md` |
| P6.5 | Who added the stocktake notice, and was it in time? | 2, admin | Slot 4, on the Monday of the week before last; the stocktake page asks for two weeks and this is seventeen days | page history, `how-to/stocktake-day.md` |

**P7. A team note declined because the point belongs on a page (S4).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P7.1 | Why was my note about reading the booking back declined? | 6, junior | The page "Booking a visit" already says it (step 6); slot 4's reason says to propose the wording there | `how-to/booking-a-visit.md`, the decision |
| P7.2 | Where does a habit the whole team should follow belong? | 6, junior | On a page; a personal note is for how the assistant works with you; customer and price facts are never notes | `how-to/using-this-knowledge-base.md` |

**P8. The customers' assistant answers from public pages (S7).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P8.1 | My brakes are grinding. What is it and what will it cost? | customer | Pads worn through; come now; inspection $49.95, about half an hour; front pads and discs on a typical car $428.00 to $523.76 before tax, confirmed after inspection | `customers/brake-noise.md` |
| P8.2 | Can you book me for Thursday at nine? | customer | It cannot book; it hands the conversation to an advisor | `customers/README.md` |
| P8.3 | What do you charge companies per hour? | customer | Not on a public page; call Greg Whitaker on (423) 555-0142. It must not give $121.50 | `customers/company-vehicles.md` |
| P8.4 | Do you have loaner cars? | customer | The pages do not say; there is a free shuttle at the two Chattanooga shops | `customers/dropping-off-and-picking-up.md` |
| P8.5 | What do I answer her about the rear shocks? | 6, junior | Replace rear shock absorbers (pair): $339.28 standard ($297.00 economy, $362.00 premium), 1.2 hours, no alignment needed; plus free times from the schedule | `prices/price-list.md`, `services/suspension/struts-and-shocks.md` |

### Search and reading challenges

**C1. Near-identical titles.** "Opening and closing" and "Hours and getting here" exist per shop; "Warranty" and "Warranty policy"; drain and fill against exchange; drive belt against timing belt.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C1.1 | What is the till float at Bonny Oaks? | 6, junior | $150 (East Main is $200) | `shops/east/opening-and-closing.md` |
| C1.2 | Where does the deposit bag go at closing at Bonny Oaks? | 17, junior | The drop safe under the counter; the parts manager takes it to East Main on the 1:00 run | same |
| C1.3 | Where is the key drop box at Bonny Oaks? | 6, junior | Left of the office door (East Main: right) | `shops/east/hours-and-getting-here.md` |
| C1.4 | Who counts the till at Charlotte Pike? | 24, junior | Two people, both initial; since `@discount_rule` | `shops/west/opening-and-closing.md` |
| C1.5 | How much is a transmission flush? | 7, junior | It names two jobs and asks which: drain and fill $191.98, machine exchange $386.94 | `services/transmission/transmission-fluid-service.md` |

**C2. A fact that exists only inside a table.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C2.1 | How much longer do spark plugs take on a V6 SUV? | 7, junior | Labour times 2.4 | `prices/labour-rates-and-fees.md` |
| C2.2 | Who approves work on a driving-school car above $500? | 17, junior | Denise Atchley, the owner; Rob Atchley up to $500 | `accounts/company-account-terms.md` |
| C2.3 | How fast must a missed call be returned? | 23, junior | Within one hour, the same day without exception | `policies/service-standards.md` |
| C2.4 | What are the tire fees? | 17, junior | $3.50 disposal and $1.35 state fee a tire, $19.40 for four | `prices/labour-rates-and-fees.md` |
| C2.5 | What happens when a technician is over 4 % comebacks two months running? | 4, senior | The foreman checks every brake, steering and suspension job of his for a month | `management/comeback-review.md` |

**C3. A fact that exists only inside an attached document** (PDF with page locators, Word with paragraph and section, slides with slide numbers; the spreadsheet cannot be read).

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C3.1 | Front pads and rotors on a van? | 5, middle | $640.91 standard, before supplies and tax | `prices/counter-price-sheet.pdf`, page 2 |
| C3.2 | How many paid days off after two years? | 17, junior; then 15, worker | Junior: 10 days. Worker: not in what he can read; the binder in the break room, or the office | `team/staff-handbook.docx`, section 4; `shop-floor/README.md` |
| C3.3 | What are the three sentences Angie never says? | 7, junior | "No problem." "It should be ready." "It is all warrantied." | `team/the-call-in-eight-moves.pptx`, slide 9 |
| C3.4 | How much oil does a Transit-250 with the 3.7 take? | 9, junior | 6.0 quarts of 5W-20 | `parts/fleet-fluid-sheet.pdf`, page 1 |
| C3.5 | Oil quantity for the driving school's Sentra? | 9, junior | Not in the printed sheet; the spreadsheet may have it and cannot be read | both fluid files |
| C3.6 | How many late arrivals before a written warning? | 4, senior | Five in any 30 days; three bring a conversation | `team/staff-handbook.docx`, section 2 |

**C4. A procedure spread over three linked pages:** inspection (`shop-floor/courtesy-inspection.md`), estimate (`how-to/writing-an-estimate.md`), approval (`how-to/getting-approval.md`).

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C4.1 | A technician marks rear shocks Bad. What happens before work starts? | 7, junior | Measurement and photo, a catalogue job on the line; the advisor puts it on the estimate at the standard tier from the price list, after the job the customer came for; sends it the same day; calls within 30 minutes; records the yes per job with who, how and when | the three pages |
| C4.2 | How long do I wait for an answer to an estimate? | 17, junior | With a Bad item: call within 30 minutes. Otherwise two hours, then 4:00, then the next morning, three tries | `how-to/getting-approval.md` |
| C4.3 | Do Watch items go on the estimate? | 7, junior | No: in the notes with the measurement, unless they share labour with a Bad item | `how-to/writing-an-estimate.md` |
| C4.4 | Can the technician tell the customer the price? | 14, worker | No. He records and photographs; the advisor prices. The worker cannot open the estimate page the inspection page links to | `shop-floor/courtesy-inspection.md` |

**C5. A page that contradicts a team note.** `policies/storage-of-uncollected-cars.md` (five free working days, $25 a day from the sixth) against the team note approved by slot 22 ("Storage is charged from day three after the car is ready").

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C5.1 | When do we start charging storage on a car nobody collects? | 23, junior | From the sixth working day, $25 a day. A team note says day three; the policy page is the company rule; the note should be reviewed | the page, the note |
| C5.2 | Which is right, and who fixes it? | 4, senior | The page (managing owner, in force T-9mo). The note was approved at Charlotte Pike and is the old habit there; a senior reviews or retires it | same |
| C5.3 | Is there a team note that agrees with its policy page? | 2, admin | Yes: discounts over 10 % | `policies/discounts.md` |

**C6. Customers' words that differ from the trade's.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C6.1 | A customer wants a tune-up on a 2015 Camry | 7, junior | Spark plugs, $222.28, and filters after a look; if a light is on, diagnosis first | `services/maintenance/spark-plugs.md` |
| C6.2 | Recharge the freon on a 2019 CR-V at Bonny Oaks today? | 17, junior | It takes R-1234yf: $278.80, after a $49.95 check; that refrigerant is kept at East Main only, so the car goes there or waits for the 1:00 run | `services/ac/ac-check-and-recharge.md`, `parts/stock-we-keep.md` |
| C6.3 | Front end alignment on an F-150? | 23, junior | Four-wheel alignment, $137.94 for a truck | `services/tires/alignment.md` |
| C6.4 | How much is a fan belt? | 7, junior | The serpentine belt: $124.18. Not the timing belt | `services/engine/drive-belt.md` |
| C6.5 | A customer says it shakes when braking | 6, junior | Rotors, most likely: a brake inspection, $49.95; not a wheel balance | `customers/brake-noise.md`, `services/tires/rotation-balance-and-flat-repair.md` |

**C7. An answer that needs a policy page and a price page together.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C7.1 | A customer brings his own alternator for a Camry | 7, junior | We fit it: 1.6 hours, $216.00 labour plus $10.80 supplies; no warranty on the part or the labour; labour again if it is wrong | `policies/customer-supplied-parts.md`, `prices/price-list.md` |
| C7.2 | Deposit and total for a transmission rebuild? | 17, junior | Deposit $1,700.00; total $4,412.50 before supplies and tax; five working days | `policies/deposits.md`, `services/transmission/transmission-rebuild.md` |
| C7.3 | Both outer tie rods and the alignment on a Camry? | 6, junior | $445.05 before supplies and tax: two at $162.55 and one alignment at $119.95 | `services/suspension/front-end-parts.md` |
| C7.4 | Towed 14 miles to East Main, then front pads and rotors, standard: the bill before tax? | 5, middle | $616.15: tow $111.00, job $493.00, supplies $12.15 | `customers/towing.md`, `prices/price-list.md`, `prices/labour-rates-and-fees.md` |
| C7.5 | What does a 60K service come to on a Camry? | 6, junior | Labour $243.00 plus oil service, both filters, rotation and brake fluid: $627.45, supplies $22.28; transmission fluid $191.98 more if due | `services/maintenance/scheduled-maintenance.md`, `prices/price-list.md` |
| C7.6 | What warranty does a Nickajack van get on a brake job? | 6, junior | 12 months or 12,000 miles: business use | `policies/warranty.md`, terms page |
| C7.7 | A/C compressor on a 2019 car? | 5, middle | $1,248.26: the list's $1,176.86 plus the $71.40 between the two recharges | `services/ac/ac-compressor-and-condenser.md` |

**C8. The honest answer is that the knowledge base does not say.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C8.1 | How long is a rebuilt transmission warrantied? | 17, junior | Not stated: it is the specialist's warranty, on the card that returns with the unit; ask Greg Whitaker | `services/transmission/transmission-rebuild.md`, `policies/warranty.md` |
| C8.2 | Who tows for us in Nashville? | 24, junior | Not stated; the Charlotte Pike page links to a page that does not exist | `customers/towing.md`, `shops/west/README.md` |
| C8.3 | What do we charge to program a key? | 7, junior | No price: it is named among the jobs not on the list; ask the lead advisor | `prices/price-list.md` |
| C8.4 | Do we do emissions tests? | customer | The pages do not say | `customers/what-we-do.md` |
| C8.5 | What is a line technician paid an hour? | 4, senior | Nowhere: only how each job is paid | `management/pay-and-till.md` |
| C8.6 | Who holds the A/C certificate at Bonny Oaks? | 17, junior | Not named | `shop-floor/safety.md` |
| C8.7 | Price of a catalytic converter? | 7, junior | No list price: diagnosis, then a one-off estimate | `services/engine/mounts-and-exhaust.md` |

**C9. A page too long to read whole.** `prices/price-list.md` is over the 12,000-character limit of one read: the assistant gets its outline and reads a section.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C9.1 | What is a wheel bearing, standard? | 17, junior | $420.27 a side | price list, section Suspension & steering |
| C9.2 | Every transmission job and its standard price | 5, middle | Drain and fill $191.98; exchange $386.94; gear oil $169.50; clutch $1,227.91; CV axle $379.64; rebuild $4,412.50 | price list, section Transmission & driveline |

**C10. A link that leads nowhere.** `shops/west/README.md` links to `tow-trucks.md`, never written.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C10.1 | What does the Charlotte Pike page link to that is missing? | 2, admin | "Tow trucks we use" | `kb_links` on the page |

**C11. The knowledge base against the data.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C11.1 | How many cars does the driving school have? | 16, middle | The page says seven and is six months old; the shop system has eight | `accounts/a4.md`, ERP |
| C11.2 | Who works the counter at Charlotte Pike? | 2, admin | Chad Binkley and Jasmine Bolden; the shop's own page names an advisor who left five months ago | `team/who-is-who.md`, `shops/west/README.md` |
| C11.3 | Are we meeting our call-back standard at each shop? | 2, admin | Standard one hour: East Main about 40 minutes, Bonny Oaks 45, Charlotte Pike four and a half hours | `policies/service-standards.md`, calls |
| C11.4 | Does the knowledge base know Cumberland Bend left? | 4, senior | No: its page is thirteen months old and says nothing; the data shows no visit for four and a half months | `accounts/a5.md`, ERP |
| C11.5 | What does our own material say about why Sourwood is fading? | 2, admin | Its page names a contact who left Sourwood and an advisor who left us; nobody rewrote it; the estimate standard (four working hours) was missed | `accounts/a6.md`, `policies/estimates-and-approvals.md`, ERP |

**C12. Questions that must be refused by rank** (design R4). A hidden page answers exactly as a missing one.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C12.1 | How many vacation days do I get? | 15, worker | Not in what he may read: the binder, or the office | `shop-floor/README.md` |
| C12.2 | What margin do we make on parts? | 6, junior | Not available at her rank | `management/parts-pricing-matrix.md` |
| C12.3 | What is the plan for my shop? | 22, senior | Nothing found: the plan is the administrator's | `management/owners/west-plan.md` |
| C12.4 | Sourwood's credit limit? | 5, middle | $7,500 | `accounts/credit/credit-limits-and-collections.md` |
| C12.5 | Show me the advisor playbook | 6, junior | Not available; the counter pages cover it | `playbooks/advisor.md`, `how-to/README.md` |
| C12.6 | Do your advisors give discounts? | customer | Only what the public pages say: no discount for cash | `customers/payment.md` |
| C12.7 | What does the "Pay and till" page say? | 6, junior | Refused by rank: she cannot open it and the answer does not quote it (story question S12.5) | `management/pay-and-till.md` |

### Operating the knowledge base

| # | Asked | By | Expected | Uses |
|---|---|---|---|---|
| O1 | Fix the brake questions page: put in today's prices | 5, middle | A card showing the seven figures changed, his reason; on confirm, a proposal; the deciders are told | `kb_suggest`, propose |
| O2 | The same request | 6, junior | A card with no confirm: a lead advisor can propose it, a manager can publish it | `kb_suggest`, below the rung |
| O3 | Put Erin Castillo on Sourwood's page and take Brad off | 4, senior | A card in publish mode; on confirm, a revision by him | `kb_suggest`, publish |
| O4 | Change your opening hours page | customer | Refused: staff only | `kb_suggest` |
| O5 | Take the old warranty page down | 2, admin | The assistant can suggest text, not delete: it offers to mark the page superseded at the top, or she deletes it on the page | `kb_suggest` limits |
| O6 | What changed on the discount policy since it was written? | 2, admin | One edit, by slot 4: the before-tax line | `kb_history` |
| O7 | What changed on Charlotte Pike's opening and closing page, who did it and why? | 2, admin | Slot 2 replaced one count and banking twice a week with two counts and daily banking; "Two counts, every day." | `kb_history` with the revision |
| O8 | What changed on the pads and rotors page at the price rise? | 16, middle | Her own proposal, approved by slot 4: the labour-dependent figures, for example $475.00 to $493.00 | `kb_history`, `en/_history` |
| O9 | Who came off Who is who in the last six months, and who went on? | 2, admin | Off: Brent Lassiter, Wes Tate. On: Caleb Sutton, Hunter Varnell (Jasmine Bolden started ten months before T and came with the import) | `kb_history` |
| O10 | Which pages were changed because of the timing belt complaint? | 2, admin | The root README, the price list, "How prices change" (new), discounts, complaints, writing an estimate, using the knowledge base, the owner playbook | `kb_history` messages |
| O11 | What is waiting for a decision? | 4, senior | P3.1 | Inbox |
| O12 | Find pages that contradict each other | 2, admin | At least: "Our warranty" against "Warranty policy", both public; price list against the two stale pages; terms table against Sourwood's page; Who is who and the hours page against Charlotte Pike's page; the public tires page ("next morning") against the suppliers page (Nashville twice a week); the timing belt page's same-day line against the ordering page | `kb_search`, `kb_read` |
| O13 | Which page has nobody keeping it? | 4, senior | The brake questions page: signed BK, an advisor who left; no index links to it | `kb_links`, `team/who-is-who.md` |
| O14 | Which pages link to the price list? | 5, middle | Ten pages, more than link to any other page: the README, the services index, the rates page, "How prices change", the estimate and chat pages, the new-advisor page and three more | `kb_links`, `kb_overview` |
| O15 | A customer was told tires arrive next morning in Nashville. Propose the fix | 16, middle | A proposal on `customers/tires.md` adding that Nashville deliveries are Tuesday and Friday | `kb_suggest`, public page |

## 6. New facts other stores must be made consistent with

Every fact sheet lists its own under `new_facts` (115 in all). Each is now a row of `ledger.json` under `kb.*`, with the page that states it and the store that must carry it; the texts another store must hold word for word are in `CROSS-STORE.md`. The ones with a footprint outside the knowledge base:

| # | Fact | Store it touches |
|---|---|---|
| 1 | Warranty detail: business-use vehicles 12 months or 12,000 miles; pads 12/12; blades and bulbs 90 days; used parts 90 days; the 25-mile rule; in force from T-26 months | ERP comeback orders and their windows |
| 2 | Credit limits $30,000 / $20,000 / $5,000 / $5,000 / $7,500 / $7,500; terms by fleet size; statements on the first working day; four collection steps; approvers above the driver limit (Millsaps' dispatcher to $1,000, the driving school's lead instructor to $500) | ERP customer, statement, approvals |
| 3 | Till floats $200 / $150 / $150; differences over $5.00 reported; from `@discount_rule` two counts and daily banking at Charlotte Pike | ERP till counts |
| 4 | Twelve service standards: call back in one hour, first chat reply in 10 minutes, estimate the same day (accounts four working hours), proposals in five working days, schedule by Thursday noon | calls, conversations, roster, this base |
| 5 | Stocktake day: no appointment after 10:30, nothing over two hours | ERP appointments |
| 6 | Schedule rules: technician minimums 4 / 3 / 3; no diagnostics and last car 11:30 on Saturdays; Bonny Oaks' line forwarded on Saturdays; slot 4 at Bonny Oaks Tuesdays and Thursdays; slot 10 about four diagnostic jobs a day | shift planner, calls, ERP |
| 7 | Memory: a team note that contradicts the storage policy (proposed by slot 23, approved by slot 22, about T-4 months): "Storage is charged from day three after the car is ready." | memory |
| 8 | Deposits (half over $300; $1,700 for a rebuild), storage ($25 a day after five working days), towing ($95 with 10 miles, $4 a mile after), estimates valid 30 days | ERP payments, fees, sublet, estimate expiry |
| 9 | Sourwood dealt with the advisor who resigned (slot F3); its page names him and the old fleet contact | S1's causes |
| 10 | R-1234yf stocked at East Main only; supplier order-by times; Nashville tires Tuesday and Friday; rebuilds five working days | ERP stock, purchase orders, waiting times |
| 11 | Handbook numbers: lateness ladder (3, 5, second warning), time off 0 / 5 / 10 / 15 / 20 days, allowances; pay types per job; two-week pay period | roster, ERP employee |
| 12 | Charlotte Pike opened on Saturday mornings before the purchase and has not since; its own page still says it does | ERP, core hours |
| 13 | Tenant settings: knowledge root seen from worker; the path ranks of section 2; rungs at the product's defaults | settings (R9) |

## 7. Contradictions found in the design and the seed files

Four found at the start were settled by the controller while this ran (the founder is Ray Brennan in every file; the cheap pad is Calder ValueStop in both files; the timing belt is 688 and 720 in the ledger; slot 29 has a person). What is left:

| # | Where | What | What this draft did |
|---|---|---|---|
| 1 | design 7.2 S8 against `ledger.json` | The design text still says old price 640, new 691; the ledger and the story card say 688 and 720 | Followed the ledger |
| 2 | design 1.1 against `cast.md`, `stories/` | Settled: the second home shop is at 6340 Bonny Oaks Drive and staff call it Bonny Oaks (ledger `geo.address.east`, `geo.short_name`) | The pages carry the address and the name; the folder is `shops/east` in both configurations |
| 3 | `ledger.json` `s12.pages` | Timing belt and Brake questions are public. A page cannot rank below its folder, so every service page is public | Made `services` public and wrote nothing confidential in it. The alternative is to move the two stale pages into `customers` |
| 4 | `ledger.json` `s4.driver_limit` against S4 | With one $300 limit written on the Company accounts page, slot 6's waiting note repeats a page, exactly as her declined one did | Wrote the page as the ledger says; question P5.4 asks it |
| 5 | `accounts.json` | Settled: the anchor account's fleet manager is Lonnie Coffey, so he no longer shares a first name with the founder | The pages take the name from `accounts.json` |
| 6 | design 7.2 S12 ("public, staff or senior") against the product | There is no public tier, and the root is hidden from the customers' assistant by default | Section 2 |
| 7 | the brief's `{{T-8wd:main|date}}` against `stories/TIMELINE.md` ("no date is T minus n days, snapped") | Two ways of writing a date | Story dates are named events on the timeline's anchors; plain offsets only for page ages |

## 8. What the product's knowledge features could not do, or lack

| # | Finding | Read in |
|---|---|---|
| 1 | No public tier: the customers' assistant reads at worker rank, so nothing can be for technicians and not for customers. With the root at worker, any new top-level folder is public until someone ranks it | `core/content/knowledge.py`, `knowledge_members.py` |
| 2 | Playbooks are pinned at administrator: a rank's playbook cannot be read by that rank, nor by the assistant acting for it. "Playbooks for each rank" are therefore owner-only here, with the content repeated on staff pages | `knowledge_import.py` |
| 3 | Spreadsheets are not extracted (PDF, DOCX and PPTX are). The fluid sheet is planted as an unreadable file with a PDF print beside it | engine `docs/search.md` |
| 4 | No knowledge tool lists proposals, and proposals are not searchable: "what is waiting" is answered from the Inbox line only | `kb_tools.py` |
| 5 | The import carries no authors and no ranks: every page is one revision by Administrator at worker-readable root until `set_meta` runs. The seeder must rank folders before loading | `knowledge_import.py` |
| 6 | Revisions cannot be dated in the past (decided: text dates) | design O2 |
| 7 | `kb_suggest` only puts text into one file: it cannot delete, rename, move, upload a binary or change who sees a page | `kb_tools.py` |
| 8 | A page has no owner or review date of its own; staleness is visible only in the text | engine `docs/concepts.md` |
| 9 | A link to a page above the reader's rank is silent for the assistant: the worker's inspection page links to an estimate page that answers "not found" | `kb_tools.py` (`above_rank` dropped) |
| 10 | Only six top-level folders get a colour; this base has twelve | `docs/guides/knowledge-base.md` |

## 9. Checks run on this draft

- Every link resolves to a page or a binary, except the one planted broken link. Fourteen links lead from a public page to a page above it (service pages to policies, parts and the rates page; the technicians' inspection page to the estimate page): for the customers' assistant and for a technician those targets do not exist (C4.4).
- Every dollar amount, count of labour hours and clock time in `en/` is a catalogue figure (total, labour, part, rate or fee, for some tier, class and side of the rise) or a ledger value; every name is in the seed files; the page list, folders and ranks are the ledger's. `checks/check_kb.py` proves it for both configurations as section 10 of `checks/check_ledger.py`, and fails on a difference.
- No placeholder outside the grammar; none unescaped inside a table.
- The pages were generated from `catalogue.json`, `cast.json`, `vendors.json` and `accounts.json`, so a price, a name or a phone cannot differ from those files.

## 10. Not finished

- The five binaries are Markdown drafts; converting them is a later step. Every row of the fluid sheet is from memory and unverified.
- Earlier revision texts exist only for the 36 price-pass pages. For the other pages with history the fact sheet says what each revision changed, exactly enough to write the earlier text, and the earlier text is not written.
