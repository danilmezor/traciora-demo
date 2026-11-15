# Generator spec: the shop-management database (seed v1)

For the programmer who writes the ERP part of the seeder. Inputs: `schema.sql` and `dictionary.md` beside this file; `../ledger.json` (every number); the seed files `../cast.json`, `../accounts.json`, `../named_customers.json`, `../vendors.json`, `../catalogue.json`, `../parc.json`, `../mix.json`, `../phones.md`; the free texts `texts.json` beside this file; the story files' new facts `../checks/new_facts.json` (one ledger row per file, `nf.call.NN` and `nf.conv.NN`); `../stories/S01.md` to `S16.md` and `../stories/TIMELINE.md`; the story files, for the day only: `../calls/<cfg>/NN-*.json` (`call.day`, `floating_days`), `../conversations/<cfg>/NN-*.json` (`days`, `floating_days`); where `call.day` names a period, the day is T + `nominal_offset` moved to the named slot's first working day on or after it. A ledger key is written `` `key` ``; "the row" means its value in the configuration being built. The background numbers this spec needs are ledger rows too (section 11); nothing else is invented.

The output is one load file per table (COPY format), with the ids below, that loads into an empty `shop` schema and passes `checks.sql`.

## 1. Conventions

**Build inputs.** Configuration (`en` or `ru`), size (`full` or `small`), T, a random seed. T and every anchor (G, P, W0, W-k, full open day, slot N's n-th working day, the <weekday> of week T-k) follow `time.t_rule`, `time.anchors` and `stories/TIMELINE.md`; the generator computes them once and hands the same dates to every store.

**Week-bound events (rule A).** The home shops' roster publish is the last Thursday 12:00 publish on or before T. L is the week after that publish: W+1 at the nominal T, W0 on a build before Thursday noon. What the cards place in 'week W+1' as the published week goes to L: the stocktake (`site.stocktake`, the Thursday of L), slot 16's week off (from the Thursday of L) and the booking of `nf.conv.08` (her last working day before it). When the booking's day is not after T (a build before Thursday noon on which she has no working day between T and her week off), the visit has happened: the appointment is `arrived` and carries an ordinary order written by slot 16 for the job recommended at the last visit, at list, completed and paid that day. A2's Monday lists stay on the calendar. Weeks T-k do not move. The anchor function returns the Monday of L as pub_week (`:'pub_week'` in `checks.sql`).

**Each shop's own clock.** The generator works in local wall-clock time per shop: opening hours (`site.hours.weekday`, `site.open_days`), the morning block and every planted time of day are local. A timestamp is written as it reads on that shop's wall, with no zone (`timestamp`). Office events with no shop (statement issue, statement payments, the bookkeeper's actions) use `main`'s clock. T is an instant in the home zone; at `west` it reads T − `geo.zone_gap_hours`. Nothing in history is later than T on its own shop's clock; rows dated after T are only appointments booked before T, open purchase-order promises and service-reminder due dates.

**History window.** `main` and `east` from the first full open day on or after T − `time.history_months` months; `west` from the purchase day, T − `time.west_bought_months` months (`location.opened_on` of `west`). No order on a closed date (`site.closed_dates`), on a day the shop is shut (`site.open_days`: en `east` and `west` weekdays only, `main` also Saturday 08:00 to 13:00; ru every day) or outside opening hours, except the walk-out of a car after hours where a card says so.

**Ids.** Dense integers from 1 per table, in time order of the row's first timestamp (load order). They carry no meaning.

**Document numbers.** `repair_order.number`: en a company-wide running number from 104001 in `opened_at` order; ru `ЗН<d>-<six digits>` with d = 1 (`main`), 2 (`east`), 3 (`west`) and a running number per shop. `statement.number`: en `ST-<yyyymm>-<customer_id>`; ru `СЧ-<six digits>`. `purchase_order.number`: en `PO-<six digits>`; ru `ЗП-<six digits>`. Company customers' own order numbers in `repair_order.purchase_order_number`: A1 en `ND-6xxxx` (five digits; call 24's is ND-60418), ru `<n>/<month>` (call 24's is 247/10); A2 en `<4 digits><letter>` (call 25's is 4471B), ru none; others none.

**Money.** en: cents. ru: catalogue list prices are whole roubles rounded to 10, except a fluid or gas sold by measure (the catalogue's unit is a litre, gram or kilogram), which keeps the catalogue's unit price; computed amounts (supplies, tax, discounts) to kopecks. A company-account price is list × 0.9 and is not rounded again: cents (en), kopecks kept (ru) (`price.company_rounding`). Rounding happens per line; totals are sums of rounded lines.

**Prices on a date** (`catalogue.json` `price_history.rule`): hourly labour = hours × the hour of the customer's price class in force on the order's `opened_at` date (`price.hour.history`, `price.hour.company_history`; `labor_rate` rows); menu labour = the job's `labour_price.history` entry of that period (company class: `labour_price_company`); parts, fluids, fees and sublets = today's price on every order from G to T, and before G today's price × (1 − `price.parts_drift_year`/100)^(days before G / 365.25) (en 3, ru 12), cost moving with list. Vehicle class: hours × `hours_by_class`; parts × `configurations.<cfg>.parts_class_multiplier` when `parts_scale_with_class`. Company class (`customer.price_class = 'company_account'`, A1 and A2 only): 10 % off parts list and menu prices (`configurations.<cfg>.company_account_terms`). Story items carry the exact amounts of their ledger rows instead (`s7.bill`, `s8.*`, `s12.brake_price`, the facts of `nf.call.NN` and `nf.conv.NN`, call files' `scenario.facts.prices`).

**Tax** (`tax.rate.main`, `tax.rate.east`, `tax.rate.west`, `tax.ru_vat_from`, `tax.vat_divisor`, `tax.ru_price_basis`). `repair_order.tax_rate` = the rate of the order's shop: en 9.25 at `main` and `east`, 9.75 at `west` for its whole history (the 9.75 began before the shop's first order under the company); ru 0 before 2025-01-01 and 5 from that date (order date). `tax_included`: en false on every order (sales tax is added to the lines); ru true on every order, private customers, small businesses, the walk-in record and the six accounts billed on terms alike: the lines are the table prices (the account's own price class for A1 and A2) with VAT inside, and from 2025-01-01 the before-VAT amount is total / 1.05 to the kopeck (`tax.vat_divisor`); on an order before 2025-01-01 the rate and `tax_total` are 0. en orders: `tax_total` = round((labor + parts + sublet + fees − discount) × rate/100, 2), `total` = that sum + `tax_total`. ru orders: `total` = labor + parts + sublet + fees − discount, `tax_total` = `total` − round(`total` / 1.05, 2). An account's invoice and УПД (the `statement` row's documents) print the before-VAT amount, the VAT and the total as three figures; the database holds them as `total − tax_total`, `tax_total` and `total` of its orders.

**Shop supplies** (`price.supplies.rate`, `price.supplies.cap`): one `order_fee` of kind `shop_supplies` on every order with hourly-priced labour on approved jobs, rate × hourly labour, capped. Menu labour carries none.

**Names.** Employee names split from `cast.json` `full_name`: first token → `first_name`; with three tokens (ru patronymic) the middle one → `middle_name`; last token → `last_name`. `checks.sql` finds people by `first_name` and `last_name`.

**Dealt, not rolled** (`size.rate_rule`). For every rate row a person, shop or period gets exactly round(n × rate) events; the generator picks which cases at random with the build's seed.

## 2. Order of filling

1. `location`, `service_category`, `canned_job`, `labor_rate`, `vendor`, `part`, `referral_source`, `employee`.
2. Customers and vehicles that exist before any order: the six accounts with contacts and fleets, the 30 small businesses, the walk-in record, the pool of private customers at the history start, `west`'s bulk load (on its day), the named customers of the stories and calls.
3. The day plan: for every shop and open day, the planted orders of that day (section 5), then background orders to the day's count (section 4).
4. Per order, in time order: appointment, `repair_order` header, inspection and items, jobs, labour, parts, sublets, fees, status history, time entries, purchase orders and their lines, stock movements, payments; new customers and vehicles as their first order needs them.
5. Comebacks (they need the first orders), then statements and statement payments, then till closes (they need the day's cash payments), then service reminders, part returns, stock adjustments and transfers.
6. `stock_level` from the movements; denormalised totals (D1 to D9 of the dictionary) from the lines.
7. Assertions of section 7 and `checks.sql`; a failure stops the build.

## 3. Tables: where every column comes from

### location
Three rows. `name` = `geo.short_name`; `address`, `latitude`, `longitude` = `geo.address.<site>`; `phone` = phones.md, the shop's public line; `time_zone` = `geo.home_zone` (`main`, `east`), `geo.other_zone` (`west`); `tax_rate` = `tax.rate.<site>` (en `main` 9.25, `east` 9.25, `west` 9.75; ru 5 at every shop); `bays` = `site.bays.<site>`; `opened_on`: `main` T − 30 years (design 1.1), `east` T − 132 months (`proposed.cast.east_opened`), `west` the purchase day.

### employee
One row per person of `cast.json` slots 1 to 29 and F1 to F3, and one row per season F4 worked that overlaps the history (`season.hire`; en ten weeks from the first Monday of June, ru six weeks from the first Monday of April and of October). `location_id`: the person's `site` (null for slots 1 and 2); `role`: founder, managing_owner → `owner`; office_manager → `office`; service_manager, shop_manager → `manager`; lead_advisor, service_advisor → `advisor`; shop_foreman → `foreman`; parts_manager → `parts`; every technician role and seasonal_helper → `technician`. `title` = `cast.json` `roles.<role_key>.<cfg>`. `pay_type` (`kb.pay_types`, page "Pay and till", the same in both builds): technicians on line work → `flat_rate`; slots 10 and 13 → `salary`; slots 14, 15, 28 and F4 → `hourly`; every other role → `salary`. `hired_on` = T − `start_months_before_t` months (F4: the season's first day); `left_on`: F1 the firing day (`pF1.period`, `s2.dates`), F2 the Monday of week T-17 (`pF2.period`), F3 the Monday of week T-30 (`pF3.period`), F4 the season's last day; null otherwise.

### referral_source
The list of ledger row `erp.referral.mix` (section 11), names in the configuration's language.

### customer
- **The six accounts** (`accounts.json` `accounts`): `kind` company; `name` = `name` with `legal_form` as the market writes it (en "Nickajack Delivery LLC", ru «ООО «Симбирский гонец»»); `phone`, `address` from the file; `email` = `ap@` or the first contact's address; `price_class` company_account for A1 and A2, standard for the rest (`price.hour.company`); `payment_terms_days` = `acct.<id>.terms_days`; `credit_limit` = `kb.acct.credit_limits`; `created_location_id` = `acct.<id>.shop`; `created_at` before the history start (the first contact's `from_months_before_t`); `notes`: en the account's text of `kb.acct.standing_instructions` as written; ru the account's text of `erp.customer.account_notes`; null for an account neither row names.
- **Small business customers** (`accounts.json` `small_business_customers`, `proposed.accounts.small_business`): `kind` company; no terms, no credit limit (`acct.small.terms`); `created_location_id` = `home_shop`. Their orders are `acct.small.orders_share` of all orders, at their home shop.
- **The walk-in record** (`s2.walkin`): one row at `west`, `kind` person, `name` en "WALK-IN CUSTOMER", ru «Розничный покупатель», no phone, email or address, created in `west`'s bulk load.
- **Private customers at the history start**: a pool per home shop of size (that shop's private background orders per year × `erp.customer.returning_share`) / `erp.customer.visits_per_year` (section 11); `created_at` uniform over the ten years before the history start; `created_location_id` their shop.
- **`west`'s bulk load** (M11, `time.west_bought_months`): the pool of `west`, sized by the same formula, all with `created_at` on the purchase day between 08:00 and 09:00 and `created_location_id` = `west`; names written "LAST, FIRST" in capitals (en) or «ФАМИЛИЯ ИМЯ ОТЧЕСТВО» in capitals (ru) for the share of `erp.west.bulk_caps_share`; no earlier orders exist for any of them.
- **New private customers**: a background private order is by a returning customer with probability `erp.customer.returning_share`, else a new customer created at the order's `opened_at` minus 1 to 10 minutes at that shop.
- **Named customers** (`named_customers.json` S7, S8, S6_waiting_nine_days, the 24 records of `S15_duplicate_pairs`, the owners and recorded-under customers of `S15_car_on_the_wrong_customer`) and the invented people of the story files who have a booking, an order or history (`named_customers.json` `story_callers` and `story_chat_customers`, from `checks/new_facts.json`; section 5, "The story files' new facts"): name, phone and car as the files give them; a VIN and plate where the files give none are formed by the generator like any background car's.
- Every row: `name`: names from the generator's own lists (person: en "First Last", ru «Фамилия Имя Отчество»); `phone` per phones.md (en tier B for background, tier A for named; ru 907/935 mobiles; every background phone unique and never one of a named record: the pair test of M1 must find only the 12 pairs); `email` for `erp.customer.email_share` of persons; `address` for persons on company records only (private customers' addresses are not taken at the counter: null); `referral_source_id` per `erp.referral.mix`.

### customer_contact
Every contact of the six accounts in `accounts.json`: `name`, `role`, `phone`, `email`; `started_on` = T − `from_months_before_t` months; `ended_on` = T − `to_months_before_t` months or null. A6: Bobby Shadden / Геннадий Павлович Лукьянов ends the day before P and Erin Castillo / Дарья Олеговна Вершинина starts on P (card S01 wins over the file's "5 months").

### vehicle
- Accounts' fleets (`accounts.json` `fleet`): `vin`, `plate`, `year`, `make`, `model` from the file; `unit_number` = `unit`; `vehicle_class` from `parc.json` for that make and model (vans `van`); `engine` from `parc.json`'s first engine whose years contain the model year. A4's cars with `joined_fleet_months_before_t` get orders only after that date.
- Small businesses' vehicles from the file.
- Named cars from `named_customers.json` and the call files; S8's car `engine` "2.5i (EJ253)" / «1.6 16V (K4M)».
- Background cars drawn by `parc.json` `how_to_draw` (model by share, age by `age_weights`, engine by years); VIN formed as `accounts.json` `_meta.how_formed` describes; plates by `erp.vehicle.plates`: en one of Tennessee's two serial formats by its share, the serial drawn inside the issued ranges and outside the block BRC-2190 to BRC-8000, which belongs to the cars a story names; ru А123ВС and a region code of the shop of the customer's first order, by the row's shares. No two cars share a plate, the duplicate pairs of M1 aside.
- Per private customer `erp.vehicle.per_private_customer` cars on average; one car per walk-in order, owned by the walk-in record.
- **VIN null** (M2, `s15.mess.vin_missing_pct`): after all vehicles exist, the oldest 3 % of rows by `year` (ties broken at random) get `vin` null; the named cars with `vin` null are among them (they are old enough; assert it). No other row has a null VIN.
- **Duplicate pairs** (M1): each record of a pair has its own vehicle row for the pair's car, with the same VIN (or none) and plate. ru: a pair's first order is at a shop of its plate's region (73, 173: `main` or `east`; 16, 116, 716: `west`).

### service_category, canned_job
`service_category`: `catalogue.json` `categories` (`code` = key, `name` = cfg). `canned_job`: `catalogue.json` `jobs`: `code` = key, `name` = `<cfg>.name`, `hours` = `<cfg>.hours`, `labor_pricing` = `<cfg>.labour_pricing`, `menu_price` = `<cfg>.labour_price.after_rise` for menu jobs. 70 rows.

### labor_rate
Per shop and price class, one row per period of `price.hour.history` (standard) and `price.hour.company_history` (company_account), `valid_from` = the period's start (P and the Russian earlier rises as dated there; the first period from the history start), `valid_to` = the day before the next period, null for the current one. `west` gets only the periods in force from its purchase day (its first `valid_from` = the purchase day).

### vendor
`vendors.json`: `name` with `legal_form` as the market writes it, `kind` parts for suppliers (V1 to V5) and sublet for subcontractors and towing (en V6 to V8, ru V6 to V9), `payment_terms_days`, `phone`, `email`.

### part
One row per distinct (`brand`, `part_number`) among the options of the part slots of `catalogue.json` (`brand`, `part_number`, `description` = the slot's `name`, `unit`, `cost`, `list_price` for class `car`), plus, for slots of jobs with `parts_scale_with_class`, one row per other vehicle class with cost and list × `parts_class_multiplier` and a part number styled from the brand's `numbering` in `catalogue.json` `brands` (fluids keep no number); class variants get numbers unique within the brand. The S6 option (`story: "S6"`) is one of them. Parts not in the catalogue that a story names (S6's angle gear / pump) are not parts: they are typed lines.

### appointment
- **Background**: `erp.appointment.share_of_orders` of orders that are not comebacks, walk-in or account standing slots have an appointment that `arrived`; besides them, no-shows and cancellations at the rates of `erp.appointment.outcome` (they have no order). `source` per `erp.appointment.source`; `starts_at` on the order's day at a drop-off time of `kb.booking.slots` (en 07:30, 08:00, 08:30 for drop-offs; waiters 09:00 to 14:00), arrival hour following `mix.json` `hour_of_day`; `duration_min` = the lead job's hours × 60 rounded up to 30; `booked_at` 1 to 10 days before (`erp.appointment.lead_days`); `booked_by_id` an advisor of that shop on duty that day; `reason` the lead job's name or the complaint; `status` arrived (with `repair_order_id`), no_show, cancelled; at T, future rows `booked` or `confirmed` (`confirmed` when `starts_at` is within two days).
- **A2's standing slot** (`acct.A2.weekly_slot`): five appointments at `east` every Monday at opening (a holiday Monday moves to Tuesday, `kb.acct.standing_instructions`), past and the next two weeks; `source` messenger (the dispatcher's Telegram thread, `conv.story_threads`); `booked_at` the Friday before at 12:00 or earlier.
- **Stocktake day** (`kb.stocktake.rules`): no appointment starts after 10:30 (en) or 10:00 (ru) on the stocktake date; none on closed dates; none after 12:00 on it (`site.stocktake`).
- `contact_name` and `contact_phone` only on bookings made before a record existed: the first-time callers and chat customers of section 5, "The story files' new facts" (en calls 3, 4, 5, 6, 14, 26, 31, 32; ru calls 3, 4, 5, 14, 26, 31, 32, 36; the chats that book a new customer); en call 3's and ru call 3's have no name, ru chat 13's has no phone. At check-in `customer_id`, `vehicle_id` and `repair_order_id` are filled; `contact_name` and `contact_phone` stay. ru chat 13: the record («Саня», `phone` null) is made with the booking.

### repair_order
- `location_id`, `opened_at`: the day plan (section 4); the hour from `mix.json` `hour_of_day` (en) or its ru table, minutes uniform.
- `customer_id`, `vehicle_id`: section 4 and the stories; `customer_id` = `vehicle.customer_id` on every order except the two of M8.
- `advisor_id`: section 4.
- `order_type`: customer_pay; warranty or goodwill for comebacks (section 4.6).
- `status` and the history: section 4.5.
- `comeback_of_id`: section 4.6.
- `promised_at`: on appointment orders, the appointment's day at 17:00 (en) or 18:00 (ru) when the lead job's hours fit the day; null on the rest; story values where a card gives one (S8: the car-in day, "same day").
- `mileage_in`: the car's odometer on the day (section 4.4); `mileage_out` = `mileage_in` + 0 to 15 (road test), null while the car is in.
- `complaint`: the lead job's customer phrase from the configuration's phrase bank (the conversations' `job_blocks`, `conv.patterns`) or the story's words; null on comebacks and account standing jobs, which carry the job only.
- `purchase_order_number`: A1 and A2 orders (section 1), except call 23's A1 order.
- Totals (D1): from the approved jobs' lines (while every job is pending or declined, from all jobs: the estimate's value), fees and the tax rule of section 1.
- `discount_total`, `discount_reason`, `discount_approved_by_id`: section 4.7.
- `statement_id`: orders of the six accounts (section 4.8).
- `voided_at`, `voided_by_id`, `void_reason`: section 4.7.

### order_status_history
Section 4.5. One row per status entered, the first row (`estimate`) at `opened_at`.

### order_job
One row per job: the customer's jobs, the courtesy inspection, the inspection-raised jobs. `canned_job_id` from the job drawn; `description` = the canned job's name, with a short note on comebacks (`texts.json` `comeback_note`); `status`: customer jobs approved; courtesy and pre-purchase inspections approved; raised jobs approved or declined by the advisor's dealt rate (section 4.3); jobs of an estimate still open at T stay `pending`. `approval_method`: customer jobs `counter` (drop-off) or `phone` (booked by phone); raised jobs by `erp.approval.method` (en `phone` 50 %, `link` 35 %, `message` 10 %, `counter` 5 %; ru `phone` 45 %, `link` 10 %, `message` 40 %, `counter` 5 %); `decided_at` within the order's approval window (section 4.5); `authorized_by` on company orders (`kb.acct.approvers`: A2 the dispatcher up to 1,000 USD / 25,000 RUB, above it the president / director; A4 the lead instructor up to 500 / 12,000, above it the owner / director; others the fleet contact in post that day, from `customer_contact`), null on private orders; `approved_amount` = the job's line value at approval (equal to its lines) on approved jobs, except where a story sets it (S8: 688.00 / 15,552); `deferred` = declined and raised from a `bad` item.

### order_labor
One line per job with `hours` > 0 (none on tyre storage; the courtesy inspection per section 4.3). `technician_id` section 4.2, null on declined jobs; `hours` = canned hours × class multiplier (story values where given); `rate` = the price-class hour in force on the order's date (on a menu line the same hour; on an inside-tax order the hour as listed, VAT inside); `amount` = hours × rate (hourly) or the period's menu price (menu); `discount` section 4.7.

### order_part
One line per part slot of the job (`catalogue.json` `parts`), quantity = `qty` (fluids: `kb.fluids_billing`, quarts rounded up to the half quart, en). Tier per `mixrow.tier_mix` (`mix.json` `tier_mix`), except pad jobs at `west` (S6, section 5). `part_id` the option's part row for the car's class; `brand` = the part's brand (D6); `description` = the slot name; `unit_cost`, `unit_price` by the price rule (company class 10 % off); `vendor_id` the purchase order's vendor for special-order parts, null for stocked parts. **Typed by hand** (M7, `parts.typed_by_hand`): dealt to 9 % of part lines at `west` and 1 % at `main` and `east`: `part_id` null, `description` re-typed in the clerk's words (abbreviated, misspelt, no number), `brand` null on half of them; they have no stock movement.

### order_sublet
Jobs with `usually_sublet` (`catalogue.json`: transmission rebuild, ru steering rack): `vendor_id` the subcontractor (en V6; ru V6 for gearboxes, V9 for racks), `description`, `cost`, `price` from the job's `sublet`. Towing (`kb.towing`): only where a card or call names a tow (call 30 en: V8, cost 95 + 4 a mile over 10, price 0 at the shop's cost).

### order_fee
`shop_supplies` (section 1); `tyre_disposal` on `new_tyres_fitted` jobs (`kb.tyre_fees_each`: en 19.40 for four, ru 400); `tyre_storage` on `tyre_storage` jobs (catalogue fee: en 80, ru 3,000). `description` = the catalogue fee name or the supplies name of `configurations.<cfg>.shop_supplies.name`.

### inspection, inspection_item
An `inspection` on every order that carries `courtesy_inspection`, `brake_inspection` or `pre_purchase_inspection` (shares from `catalogue.json` `share_of_orders`), and on every comeback order (the first look, `kb.comeback_first_look`: technician slot 8 at `main`, 18 at `east`, 22 at `west`). `technician_id` otherwise the order's first technician; `completed_at` within the first working hour after check-in (`kb.inspection`: ten minutes of work).

Items: the checklist of the knowledge page "The courtesy inspection" (`kb.inspection`), eleven groups: tyres; brake pads; lights; wipers; battery; belts and hoses; fluids and filters; leaks underneath; shocks and struts; CV boots; exhaust. Each inspection-raised job gets its own item named "<group>: <job's part>" in its group (mapping by canned job in section 4.3), `result` `bad` for `erp.inspection.bad_share` (50 %) of raised jobs and `watch` for the rest, `measurement` on every `watch` item, drawn from `texts.json` `readings` for the item's group and result (the job `brake_fluid_exchange` reads "brake fluid"); on `bad` items both a `measurement` and `has_photo` true for the shop's share of `erp.inspection.bad_documented` (`main` 92 %, `east` 96 %, `west` 65 %, dealt per shop), and on the rest of its `bad` items one of the two or neither (the schema does not force them); `order_job_id` the job. Every group with no raised job gets one `good` item with no measurement. Pre-purchase inspections use the same groups.

### time_entry
One entry per approved labour line with a technician, clock_in inside the order's `in_progress` span, duration = sold hours × `erp.time.clocked_over_sold` for that technician (everyone 0.9, slot 11 0.75, slot 14 1.3); a second entry when the order went to `waiting_parts` while the job was open (the clock stops and starts again). An entry running at T (orders `in_progress` at T) has `clock_out` null. ru S2: the 22 orders of section 5 carry 61 hours more than sold.

### statement
Section 4.8.

### payment
Section 4.7 and 4.8. `taken_by_id`: the advisor on duty at the counter (the order's advisor when on shift); null for bank transfers and statement payments. `reference`: card receipt number, cheque number, transfer reference; null for cash.

### cash_drawer_close
Section 4.9.

### purchase_order, purchase_order_line, stock_level, stock_movement, part_return
Section 4.10.

### service_reminder
- `deferred_work`: one per deferred job: `customer_id`, `vehicle_id` of the order, `order_job_id`, `description` the job's name, `due_on` = the decision date, `created_on` = the decision date; `status`: `done` if a later order of the vehicle carries the same canned job (`done_repair_order_id`), else `sent` with `sent_on` = due_on + `erp.reminder.send_after_days`, if that is on or before T, else `pending`; `dismissed` when no later order came in 12 months.
- `maintenance_due`: one per approved `oil_service` job, `due_mileage` = `mileage_out` + the lower end of `kb.maintenance_intervals` oil (5,000 mi; 7,500 km), `due_on` null, `status` `done` when a later oil service exists, else `pending`.

## 4. Background orders

### 4.1 Volume per shop and day
For every open day: count = round(`volume.orders_per_day.<site>` × the day's seasonal index × `mix.json` `weekday.index`[weekday] × density), dealt so each month's sum matches; the day's seasonal index is the sum over the catalogue's jobs of lead share × the job's seasonal curve on that day (its mean over a month is `season.total`[month]; inside ru's tyre windows it averages 1.56 and peaks at `season.tyre.orders_in_window`); en `main` Saturdays `volume.saturday_orders.main` × density. The count includes every order of that day: planted, account, small business, walk-in, comeback. The generator places those first and fills the rest with background private orders. Monthly sums land on `volume.orders_per_month.<site>` (scales) and the history on `volume.orders_history`.

Seasonal mix: lead and add-on job weights × `mix.json` `seasonal.category_curve` and `job_curve` for the month; ru seasonal tyre jobs at `season.tyre.factor` inside `season.tyre.windows` (0.5 in the shoulder weeks, 0.053 otherwise); en air-conditioning and battery jobs follow `season.ac_curve` and `season.battery_curve`.

### 4.2 Who works it
**Advisor.** Advisors on duty that day by `roster.advisor_pattern` (en weekdays; ru two on, two off with the phases of `time.anchors`), the people in post by `hired_on` and `left_on`, and the days off the stories plant (slot 16's days off, `s5.days_off_so_far`). Each order goes to an advisor on duty in proportion to `pNN.order_share`, renormalised over those on duty and in post (`pF1.order_share` and `pF3.order_share` while F1 and F3 worked; slot 22 writes no orders). en slot 29 takes his `p29.order_share` on Saturdays and cover days only.

**Technician.** Mechanics on duty by `roster.mechanic_pattern` and their shares (`pNN.share.<site>`; slot 21 four days at `east`, one at `main`; slot 28 at 0.6), F2 until his firing, slot 14 from the Monday of week T-15, F4 in his weeks, slot 10 absent in `s5.leave`. Labour hours of a day are dealt to them in proportion to `pNN.billed_index` × share (`pF2.billed_index`, `pF4.billed_index` for those two), so each mechanic's hours over his worked days equal `pNN.billed_index` × `volume.norm.<site>`. A last pass moves whole background orders between mechanics on duty the same day until each index reads its ledger row as the statement reads it; it keeps the diagnostic caps and a wait's start, and the comebacks are dealt after it, on the mechanic who did the work, so each mechanic's orders that came back stand within one case of his share of his orders (F2 within half a case). Diagnostic lead jobs go first to slot 10 at `main` (up to four a day) and slot 18 at `east` (up to two), `kb.schedule.diagnostics_and_weekends`; en no diagnostic job of any kind on `main`'s Saturday, and the last car is checked in by 11:30 (`kb.schedule.diagnostics_and_weekends`). A pad job at `west` goes to slot 27 with probability `s6.p27_pad_share`.

### 4.3 What is on the order
- **Every job's share of orders stays `share_of_orders.total`.** A job reaches an order three ways: as the lead job (`lead`), raised from the inspection and sold, or added by the customer. Its sold raised share is `total` × `recommended_share` and its customer add-on share `addon` − `total` × `recommended_share`. For the jobs where that is negative (they lead more orders than their recommended share leaves room for), the customer add-on share is 0 and the sold raised share is `total` − `lead`; the sold raised share those jobs lose goes to the other jobs in proportion to their customer add-on share, which shrinks by the same amount. Raised jobs are drawn by the sold raised share, customer add-ons by the customer add-on share.
- Customer jobs: a lead job by `catalogue.json` `share_of_orders.lead` (seasonal weights), add-ons by the customer add-on share above, the count dealt so that, over a shop's orders of a month, priced jobs per order follow `mix.json` `jobs_per_order.distribution` once raised jobs are added, and dealt without regard to how many raised jobs an order sold or who its advisor is: the mean count of add-ons is the same for every advisor and day, so an advisor who sells more raised work writes larger orders (`s5.order_value_drop`); jobs not offered for the car's class (`hours_by_class` null) or engine (timing belt on non-belt engines, `parc.json`) are redrawn.
- Courtesy inspection on `share_of_orders.total` of orders (en 0.8, ru 0.7), a free job. en: one labour line of the job's 0.1 hour at no charge (`rate` 0, `amount` 0), by the order's technician with the most hours; the catalogue's billed hours per order count it. ru: no lines (the job's hours are 0). It has no time entry of its own.
- Raised jobs: on `mix.orders_with_rec` % of inspected orders, a count with mean `mix.rec_jobs_per_such_order`, each a catalogue job drawn by `share_of_orders.total` × `recommended_share`; approved or declined per the advisor: for every advisor and 30-day block the approved share of his raised jobs is `pNN.sold_rec` (dealt); en `east`: on slot 16's days off slot 17 decides all (`s5.east_without_16` = his 52); ru each of them alone on their rota days (`s5.east_with_16` 71 and 52).
- Group of each raised job for its inspection item: brakes → brake pads (pads, rotors, shoes, calipers, brake fluid under fluids and filters); tyres_alignment → tyres; suspension_steering → shocks and struts (links, bushings, arms, joints, rods, bearings, racks under shocks and struts); battery_electrical → battery (bulbs under lights); maintenance → fluids and filters (wipers under wipers, spark plugs and drive belts under belts and hoses); engine_cooling → belts and hoses (exhaust and leaks where the job is exhaust or a gasket); transmission_driveline → leaks underneath (CV axles under CV boots); air_conditioning → belts and hoses; diagnostics: `electrical_diag` → battery, `suspension_diag` → shocks and struts, `cooling_pressure_test` → belts and hoses (`check_engine_diag` is never raised).
- Value: the parts tier mix and the price rule give the average order. The ledger states these four on paying orders (`customer_pay`), while `mix.json`'s targets average over all orders with the free warranty and goodwill ones at nothing (`mix.realisation`); the build asserts `volume.average_order.<site>`, `volume.hours_per_order.<site>`, `volume.parts_per_order` and `price.effective_rate` within their tolerances (section 7).

### 4.4 Odometer
Each vehicle has an odometer at the history start = age in years × its yearly distance (fleets: `typical_yearly_miles` / `typical_yearly_km`; others `erp.vehicle.yearly_distance`), growing linearly with a ±10 % wobble per visit and never falling. `mileage_in` reads it on the order's day.

### 4.5 Status path and times
Every order starts `estimate` at `opened_at`. Approval window: customer jobs approved at check-in (`decided_at` = `opened_at` + 0 to 15 min); raised jobs decided after the inspection, within the same day for 90 % and the next morning for the rest (`kb` page "Getting approval": 2 hours, 16:00, next morning). History rows: `approved` at the first approval; `in_progress` when the first technician starts (diagnostic orders at `main`: after a wait with mean `s5.leave.wait_days_normal` days; in the leave weeks `s5.leave.wait_days_in_leave`); `waiting_parts` and back to `in_progress` when a special-order purchase order for the order arrives after work started (section 4.10); `waiting_sublet` for sublet jobs (`kb.sublet_times`: a rebuild 5 working days); `completed` when the last labour is done; `invoiced` at completion for counter customers and account orders; `paid` at the payment (counter orders: when the car is collected, the same day or the next morning) or, for account orders, when their statement is paid; warranty and goodwill orders go `invoiced` then `paid` at completion with no payment (section 4.6). Background voids (section 4.7) go `estimate` → `void`.

**Estimates that end declined** (`erp.estimate.declined_share`, `kb.estimate_validity_days`): of the background estimates (orders opened as an estimate), private customers' end `declined` at 6 % and those of accounts billed on terms at 2 %, dealt per customer kind; small businesses and the walk-in record pay at the counter and take the private rate. A declined estimate has every job `declined` (`approval_method` and `decided_at` set, `deferred` on jobs raised from a `bad` item): half of them at check-in, the other half expired after `kb.estimate_validity_days` (en 30, ru 14) with the decline written on the expiry day; an estimate opened less than that many days before T is declined at check-in, so none is open at T; history `estimate` → `declined`; no labour by a technician, no payment. Declined estimates are extra rows beyond the day's count of section 4.1 (they are not visits). A6 is above both rates: its own share is `s1.a6`, the four slow estimates of S01 among its 20 estimates of the last 150 days (20 %), and A6 has no other declined estimate.

**Re-billed orders** (`p07.rebilled` = 3): three orders of slot 7 are re-issued after invoicing, history `invoiced` → `completed` → `invoiced`: S8's (section 5) and two more after his start, each re-issued the same or the next day for a wrong part price (one `order_part.unit_price` corrected to the catalogue's price), no discount. No other order is invoiced twice.

At T the open statuses hold only: the planted cars in `waiting_parts` (`s6.waiting_at_t`), the three never-closed orders (M4), and today's orders in `estimate`, `approved`, `in_progress` or `completed` at the shops that are open at T. An order of an earlier day whose work its shop's mechanics cannot fit before T is not opened: its customer holds an `appointment` (`booked` or `confirmed`, by the rule of section 3) for the shop's next open day with room, on or after T's day, and the day it would have come has one order fewer (the Russian shops after a tyre window, when the work on hand exceeds the crews). Every background order opened more than 60 days before T is `invoiced` (account orders on an unpaid statement), `paid`, `void` or `declined` (`kb.month_end`).

### 4.6 Comebacks
- Per mechanic of the first order (the technician with the most hours on it): over the window of his row (`pNN.comebacks`: his orders of the last 12 months; slot 27 since the purchase; `pF2.comebacks` his last six months) round(n × rate) of his orders get a comeback, within one case as section 4.2 states; shop sums then follow `comeback.<site>` and `comeback.company`.
- Pad jobs first, exactly `s6.counts` (comebacks dealt per brand and fitter: slot 27 on other brands 9 / 183 en, 6 / 119 ru; slot 27 on the cheap brand 30 / 150, 20 / 98; his colleagues at `west` cheap 8 / 100, 5 / 65; colleagues at `west` other brands 2 / 122, 2 / 80; everyone but slot 27 on other brands at all shops 64 / 3,203, 39 / 1,940); then non-pad comebacks per mechanic to reach his row (`s6.rate.other_work.p27` for slot 27).
- The comeback: a new order at the same shop for the same customer and car, `comeback_of_id` = the first order, opened after a gap of `erp.comeback.gap_days`, never after T; `order_type` `warranty` inside the warranty (`comeback.definition`, `kb.warranty.detail`: en 24 months or 24,000 miles, pads 12 months or 12,000 miles; ru 30 days, the first order's `opened_at` to the comeback's `opened_at`; the gap is cut to fit), else en `goodwill`; ru a repeat after 30 days is a paid order and is never generated as a comeback; jobs = the repeated canned job with its lines at list (hours by the same or another mechanic of the shop, the first-look inspection by the shop's person of `kb.comeback_first_look`). Totals follow `erp.warranty_order_totals`: the lines keep their prices, `discount_total` = `labor_total + parts_total + sublet_total + fees_total` (each labour line's `discount` = its `amount`), `tax_total` 0, `total` 0, status `paid` at completion, no payment row, no discount approver.
- A comeback is dealt only to first orders that end at least the gap before T, so the rates hold on the window.

### 4.7 Payment, discounts and voids
- Counter orders: one `payment` of kind `payment`, method by `pay.mix` (en card 73, cash 17, check 1, account 9; ru card 54, cash 14, fast payment 23, invoice by bank transfer 9; dealt per shop and month; "account" and "invoice" are the statement-settled orders of section 4.8; for everyone but F1 the cash share is `pay.cash_share`; ru `fast_payment` and `bank_transfer` for small businesses' orders; en `check` on about 1 % of paid orders, drawn among companies' counter orders: no personal cheques, business cheques from account holders only, `kb.payment_rules`), amount = `total`, `received_at` at collection.
- Deposits (`kb.deposits`): on orders with a transmission or gearbox rebuild (en 1,700, ru 42,500), a `deposit` at booking or check-in; the balance is the `payment`. The deposit on special-order parts (half of the parts where they come to more than 300 USD / 10,000 RUB) belongs to the purchase orders whose promise is a special order of 2 working days or more, not the next run: section 4.10 writes it.
- Background discounts: `pay.background_discount_share` % of cash orders (everyone but F1) carry a discount of 10 % to under 15 % of the bill before the discount (`price.discount_base`: en before sales tax; ru as billed, discount and bill both with VAT inside), on labour lines, with a reason from `texts.json` `background_discount_reasons`; before the rule (the next full open day after F1's firing, `price.discount_rule_pct`) with no approver; after it, at `main` and `east`, approved by slot 4; at `west` after the rule only the four of `s2.west.discounts_after`. Other discounts (coupons): 5 % of the bill on non-cash orders, reason from `texts.json` `coupon_reasons`, as many as bring all discounts to `mixrow.discounts` (1 % of sales). A discount never exceeds the labour on the order.
- Background voids: `pay.void_rate` % of orders of every advisor but F1, `estimate` → `void` the same day, no payment, totals kept (M9), `void_reason` from `texts.json` `void_reasons`, `voided_by_id` the advisor.

### 4.8 Company accounts: visits, statements, days to pay
- Visits: exactly `acct.<id>.visits` orders in every 30-day block counted back from T (the first value for every block before T-150 d, then the five blocks to T), at `acct.<id>.shop`, on the account's vehicles in turn; A2: five slot vans each Monday (`acct.A2.weekly_slot`); the block's other 1 to 6 orders on Wednesday to Friday, never with a `messenger` appointment. The lists: A1 [24, 24, 24, 24, 24, 24], A2 [26, 26, 26, 26, 26, 26], A3 [5, 5, 5, 5, 5, 5], A4 [5, 5, 5, 6, 6, 6], A5 [7, 1, 0, 0, 0, 0], A6 [8, 6, 4, 3, 2, 1]. A5's blocks start at the purchase; its last visit is the one order of the block T-150 d to T-120 d, on the Thursday of week T-20 (`s1.a5`). A visit is an order that is not declined or void; A6's four declined estimates are not visits. Average order per account `acct.<id>.average_order`, before tax (ru: the account pays the table as it stands, VAT inside, so as billed it is the row × 1.05: A1 13,500, A2 9,200, A3 10,400, A4 7,500, A5 12,600, A6 10,900) (fleet jobs: `fleet_pm_van`, brakes, tyres; company class for A1 and A2; A1's maintenance priced as `kb.worked_answers` A1_maintenance_service). A6's orders before F3 left carry F3 as advisor (`kb.acct.a6_advisor`).
- en statements (`acct.ru_documents`, `kb.acct.billing`): on the first open day of each month, one statement per account for its orders invoiced in the month before; `due_on` = issued + terms; `total` = the sum of the orders' totals; `status`: `paid` when paid by T, else `overdue` past due, else `sent`. Every statement holds more than one order (`s15.mess`, payments not one to one: every statement payment settles several orders); the build writes one of them into its manifest as the planted instance, named by its statement number, and emits the count of statement payments. Payment: one `payment` per statement, settling all its orders, method `check` or `bank_transfer`, `received_at` = issued + days: A1 by `acct.A1.days_to_pay` (older statements 28 to 32 days; the newest that can be paid in 51 days by T − 1 day in 51, the two before it in 44 and 38; newer ones unpaid); A2, A3, A4, A6 inside their terms on every bill (`acct.others_pay_on_time`, day drawn by `erp.statement.pay_day`); A5's paid inside terms except the disputed one. The account's orders go to `paid` when the statement is paid.
- ru (`acct.ru_documents`, `kb.acct.billing`): one `statement` per closed order of an account, its счёт and УПД, issued the day the order is completed or the next working day; `total` = the order's total (VAT inside; the documents print the before-VAT amount, the VAT and the total); A1 paid per `acct.A1.days_to_pay` ru formula (unpaid for invoices under 60 days old); others inside terms (`erp.statement.pay_day`); one `payment` (`bank_transfer`) per paid invoice. The exception is the combined invoice of M6 (section 6): one invoice for three orders of A3 in one month, paid by one transfer, the only payment that settles several orders. The quarterly reconciliation is a document sent on request, not a row.
- Disputed (S01): en the statement of the month of the second comeback's first order, ru that order's invoice: `dispute_note` "Disputes the E-6 pad job: came back in three weeks" (ru «Оспаривает работы по Э-10: колодки вернулись через три недели»), unpaid, `overdue`.

### 4.9 Till
One `cash_drawer_close` per shop and open day (en `main` also on Saturdays). `closed_by_id`: the advisor on the closing shift, rotating evenly among those on duty (F1: exactly 65 closes in his 26 weeks, `s2.f1.third`); `second_counter_id` at `west` from the rule day on (`kb.till.west_since_the_rule`): slot 22 or the other advisor on duty; on a day with neither (a Russian weekend), slot 25 or, when he is off, the mechanic on duty with the lowest slot; `float_amount` = `kb.till.floats`; `expected_cash` = the day's cash payments minus cash refunds of that shop's orders; `counted_cash` = expected on `pay.till_exact_days` % of days, otherwise expected ± 0.01 to `kb.till.report_over` (en 5, ru 100); `note` = `texts.json` `till_note` when |difference| exceeds `kb.till.report_over`.

### 4.10 Parts: purchase orders, stock, returns
- **Stocked parts** (`erp.stock.stocked_jobs`): the parts of the high-running maintenance jobs and, at `main` only, refrigerant (`kb.stock.refrigerant`). They come from stock: each approved line with a stocked part writes an `issue` movement (−quantity, `order_part_id`, `employee_id` the order's advisor; at `main` and `east` the parts manager slot 9 when on duty), at the time the job starts.
- **Special orders**: every other catalogue part line of an approved job is bought for the order: one `purchase_order` per vendor and order (`repair_order_id` set), the vendor that carries the brand among those serving the shop (`vendors.json` `brands`, `serves`; `west`'s general parts and the cheap pads from V2, home shops' from V1), `ordered_at` at the decision of its lines' jobs (one purchase order per vendor and decision, never before the order was opened), `promised_at` by `kb.supplier_times` (the next run after its cut-off; special orders 2 to 5 working days, ru 2 to 10), `received_at` on the promised day for each vendor's own share of purchase orders, else 1 to 3 working days later: `parts.on_time.V1` 93, `parts.on_time.V2` 62, `parts.on_time.V3` en 88 ru 87, `parts.on_time.V4` en 90 ru 91, `parts.on_time.V5` en 84 ru 80 (dealt per vendor). A `receipt` movement (+quantity, `purchase_order_line_id`) at `received_at`, then the `issue` to the line. No work on a line starts before its part is received and no part is issued after the order is completed: an order starts after its last receipt unless it is one of those that wait. When a purchase order arrives after the order went `in_progress`, the order enters `waiting_parts` until `received_at`; the generator picks which orders start before their parts so that `parts.wait_over_a_day.west` (14) and `parts.wait_over_a_day.home` (4) % of orders spend more than a day in `waiting_parts`. Purchase orders per repair order total `parts.po_per_order` (0.6, with stock orders below); the build asserts it. The knob is the stocked list: `erp.stock.stocked_jobs` is extended with the next highest-running part slots until the ratio is inside its tolerance; the list goes to the manifest (filed in `PENDING.md` under the seeder's plans; not written in slice 1).
- **Special orders of 2 working days or more**: among the counter orders (not accounts: `kb.deposits`) that wait more than a day, those whose awaited part costs the customer more than 300 USD / 10,000 RUB; their purchase order is promised 2 to 5 (ru 2 to 10) working days ahead and the customer leaves the deposit of section 4.7 when the part is ordered. They are dealt evenly over the history so that the deposits number about 300 at full size (section 10).
- **Stock orders**: weekly per shop and vendor for the parts the week before gave out, `repair_order_id` null; each line brings the part back up to its par, counting what is on the shelf and on order, at least one unit (`erp.stock.reorder` names the weekly rhythm; the par is section 7b's); received by the vendor's rate. No shop and part is below zero on any day.
- **Transfers**: when a stocked part at `east` would go below zero, a `transfer_out` at `main` and a `transfer_in` at `east` on the 13:00 run (`kb.supplier_times`) of that day, same quantity, `note` null.
- **Returns** (`parts.returned_share`, `kb.returns`): dealt to that % of purchase-order lines: a `part_return` (`quantity` 1 or the line's, `amount` = quantity × unit_cost, `reason` from `texts.json` `part_return_reasons`, `returned_on` within the window: en 30, ru 14 days of receipt), a `vendor_return` movement (−quantity, `part_return_id`) when the part had gone into stock; `status` `credited` with `credited_on` 7 to 30 days later, `sent` when returned in the last 30 days before T, `rejected` for `erp.part_return.rejected_share`.
- **Adjustments**: at each half-yearly stocktake in the history (the Thursday of the same ISO week of the year as the next one, `site.stocktake`), `erp.stock.stocktake_adjust_share` % of stocked lines get an `adjustment` of ±1 unit; ru `west` from the rule: a weekly consumables write-off (`kb.till.west_since_the_rule`) of one unit of a fluid, `note` «списание расходников».
- `stock_level`: per shop and stocked part, the sum of its movements at T, floored at zero by an adjustment if needed; refrigerant only at `main`.

## 5. The stories, planted

Each item is the same in both sizes (rule R7) unless it says it scales. "Order" means a full order with jobs, lines, history, payment as section 4 builds it, overridden by what is stated.

### S01 Company accounts
| Rows | What |
|---|---|
| `customer`, `customer_contact`, `vehicle` | the six accounts, contacts with their dates (A6's change on P), the fleets (section 3) |
| `repair_order` per block | `acct.<id>.visits`, `acct.<id>.average_order`, `acct.<id>.shop` (section 4.8) |
| A5's first pad orders | two orders at `west` on E-2 and E-6 (ru Э-1, Э-10), each about three weeks before the Tuesdays of weeks T-26 and T-22 (21 days back, moved to a full open day), job `front_pads_rotors` or `front_brake_pads`, technician slot 27, the cheap brand from V2 (`s6.brand`); they are two of slot 27's cheap-pad comeback cases in `s6.counts` |
| A5's comebacks | warranty orders opened on the Tuesdays of weeks T-26 and T-22, `comeback_of_id` = those orders, the pad job redone free, first look by slot 22 (`s1.a5`) |
| A5's last visit | an order on the Thursday of week T-20, closed the same day: the one visit of the block T-150 d to T-120 d (`acct.A5.visits` [7, 1, 0, 0, 0, 0]); no A5 order after it |
| A5's disputed bill | section 4.8, unpaid at T. Slot 3's two outbound collection calls to A5's accounts office are core call-log rows, not shop-system rows |
| A6's slow estimates (`s1.a6`) | five estimates at `main` after P whose first decision comes two days or more after `opened_at` (history `estimate` then the decision ≥ 2 days later): call 22's (`nf.call.22`: en SC-4 front and rear brakes and SC-5 PM service, ru № 2 front pads and rotors 16,276 and № 5 ТО; opened on the Tuesday of week T-9, ru slot 7's first working day on or after it; sent two days later), the web chat's (`nf.conv.04`: en SC-4 front pads and rotors 640.91 and SC-9 battery 304.45 at list, ru № 7 discs and pads 16,276 and № 8 battery 11,274; opened on the chat's day in week T-4, declined by expiry, no order: its jobs are declined on the earlier of opened + `kb.estimate_validity_days` and the last full open day before T) and three more in the blocks after P; four end `declined` (every job declined, or expired: the decline is written on the earlier of the expiry day and the last full open day before T), one approved (it is one of the block's visits). The four declined ones are not visits. A two-van estimate is one `repair_order`: call 22's on SC-4 (ru № 2), the chat's on SC-9 (ru № 8, as `nf.conv.04` reads it), the other van's job on the same row. Both end declined; the approved one is among the three more |
| A6's call 21 | an appointment and order for SC-2 on the Thursday of week T-20 at 07:30, fleet PM service at list 270.59 (ru: car №1 the day after call 21, ТО 9,710 and a bulb 800; its previous ТО three months before at 9,500) |
| A1's calls 23 and 24 | en: ND-22 on the Thursday of week T-17 at 07:30, check-engine diagnosis, company rate, no purchase-order number; ND-08 on the Friday of week T-4 at 07:30, fleet PM and a wheel-balance check, purchase-order number ND-60418. ru: per the call files (request number 247/10 on call 24's order, none on call 23's) |
| A2's call 25 | en (`nf.call.25`): M-112, appointment and order at `east` on the day after the call at 07:30, front pads and rotors at the company price, purchase-order number 4471B, `authorized_by` the dispatcher. ru: car Т-17, appointment and order at `east` the day after the call at 09:00, clutch replacement at the company price, request number 118/11 |
| A2's earlier strut order (en, `nf.conv.05`) | M-112's front struts and alignment at `east` on the Monday of week T-15 (one of that week's five slot vans), 1,119.98 before tax, purchase-order number 4398A |
| A2's water pump (ru, `nf.conv.05`) | Т-09 (Largus) at `east` on its Monday slot of week T-16 for ТО; the inspection finds the pump leaking (a `bad` item; slot 17's promised call with the price was not made, so no job is raised on that order); the pump replaced on an order opened on slot 16's first working day after it, 12,279.80 at the company price, request number 96/07 |
| A2's Monday slot | section 3, appointment; the vans of the lists in `nf.conv.05`: en week T-22 M-103, M-107, M-110, M-114, M-121; week T-15 five vans with M-112; week T-5 M-104, M-106, M-111, M-115, M-119; week T-4 with M-108; week W+1 (appointments) M-102, M-109, M-113, M-116, M-122. ru week T-22 Т-02, Т-06, Т-11, Т-15, Т-22; week T-5 Т-04, Т-05, Т-13, Т-18, Т-24; week T-4 with Т-08; week W+1 Т-03, Т-07, Т-12, Т-16, Т-25. Other weeks: five vans in turn |

### S02 The fired advisor's missing money (`west`)
| Rows | What |
|---|---|
| `employee` F1 | `left_on` = the firing day |
| F1's orders | `s2.f1.orders` (scales) in the 26 weeks (`s2.weeks`, from the first full open day on or after T-335 d to the firing), advisor F1, of which `s2.f1.cash_orders` (scales) paid in cash |
| the discounts | `s2.f1.discounted` = 35 of his cash orders (his cash orders are every order of his with a cash `payment` row, the 14 en voids among them): a labour discount of 15 to 30 % of the bill before tax, mean 22.5 %, summing to `s2.f1.discount_total` (en 4,100; ru 96,000), `discount_approved_by_id` null, a reason ("regular customer", «постоянный клиент»), spread over the 26 weeks; chosen among orders whose labour covers the discount |
| en second way | 14 of his orders voided after a cash payment: history `paid` then `void` the same or next day, the `payment` row kept, `voided_by_id` F1, `void_reason` "customer changed mind", totals summing to 5,600 (`s2.f1.second`) |
| en third way | 19 of his 65 closes with `difference` of −20 or less, summing to −1,700 (`s2.f1.third`), `note` "not known" |
| ru second way | 46 `issue` movements at `west` with `employee_id` F1 and no `order_part_id`, at cost summing to 118,000 (`s2.f1.second`), spread over the 26 weeks |
| ru third way | 22 of his orders on which the time entries total 61 hours more than the sold hours (`s2.f1.third`; 61 × 1,760 = 107,360) |
| the walk-in record | `s2.walkin`: 49 of F1's planted orders (the 35 discounted and 14 more: en the voids, ru the first 14 of the unbilled-work orders) on the walk-in customer; background walk-in orders at full size F1 150 in all, slot 23 60, slot 24 30 (total `s2.walkin.total`, scales) |
| after the rule | `s2.west.discounts_after`: four cash orders at `west` with a discount of 10 % or more: two approved by slot 22, two of 12 % by slot 23 with no approver, en on the Wednesday of week T-3 and the Thursday of week T-1; ru on slot 23's last working day on or before each of those days (nominal T: Mon 2026-10-19 and Wed 2026-11-04) |

### S04 The junior operator (call 7)
The order approved over a driver's limit (`nf.call.07`, `s4.driver_limit` en 300, ru 8,000). en: A3's order on slot 6's 2nd working day before T for MB-6: oil service 90.95 and a right front CV axle 379.64 added on the driver's word (`order_job.authorized_by` "Ronnie Eaves (driver)", `approval_method` phone, technician slot 12), completed by 16:00; the added job is above the limit and the fleet contact was not asked. ru: A1's order for car № 12 on the call's day: fleet ТО at the company price 8,724 and added work at company prices 9,498.10 (ball joint 3,766.10, alignment 3,510, brake fluid 2,222; said as 9,500) approved by the driver Фёдор (`authorized_by`; `kb.acct.approvers` ru: drivers sign by power of attorney), not by the fleet contact.

### S05 The shop that leans on one person
| Rows | What |
|---|---|
| raised jobs at `east` | section 4.3: en on slot 16's six days off (`s5.days_off_so_far`) slot 17 decides at 52 %, on her days the shop is at `sold.east`; ru by rota day. `s5.rec_jobs_on_days_off` raised jobs on her days off (scales). The average order follows (`s5.order_value_drop`) |
| the diagnostician's leave | `s5.leave`: no labour of slot 10 from the Monday of week T-10 to the Friday of week T-9; diagnostic orders at `main` in those weeks wait `wait_days_in_leave` (2.5) days from `opened_at` to `in_progress`, normally `wait_days_normal` (0.5); 11 diagnostic orders opened at `east` for customers whose `created_location_id` is `main` (`orders_sent_to_east`); `main`'s billed hours in the two weeks `s5.leave_drop_pct` under the four weeks before: the day counts of section 4.1 at `main` on the leave's days are scaled so that `main`'s billed hours a week in the leave stand `s5.leave_drop_pct` under the mean week of the four weeks before, as the statement reads it (the season's step and a closed day inside either window are part of what is read); the eleven sent to `east` are among the orders not opened at `main`, and the month's sum is lower, not made up on its other days |

### S06 `west` waits for parts
| Rows | What |
|---|---|
| vendors and purchase orders | section 4.10 rates by vendor |
| pad jobs | every pad job at `west` (four pad jobs of `catalogue.json` `story_pins.S6`): the cheap option (`s6.brand`, vendor V2) on `s6.cheap_share` = 45 % of them for every mechanic; counts and comebacks exactly `s6.counts` |
| at T | `s6.waiting_at_t`: five orders at `west` in `waiting_parts` since 9, 6, 4, 2 and 1 calendar days before T, `main` 2 and 1, `east` 1, each count moved back to a full open day when it lands on a day the shops are shut (the clock's `s6_since`); no other order in `waiting_parts`; none of their waiting lines is a stocked part |
| the nine-day car | `named_customers.json` `S6_waiting_nine_days`: order opened before T-9 d with the S6 part (a typed line, no part number: "remanufactured angle gear" / «насос ЭГУР»), entered `waiting_parts` at T-9 d moved back to a full open day; two purchase orders to V2 for it (`nf.conv.06`): the first ordered on the day after the car came in and promised for 7 days before T (en a Friday; ru 6 days before T, a Saturday), `cancelled` after missing it; the second `ordered`, promised for `west`'s 4th full open day before T (call 15's day in en, the day after it in ru), not received by T; `promised_at` of the repair order = call 15's promised day for the car (call + 2 days); no job for the rear pads of call 15; the order (`s6.nine_day_order`, chosen by the builder's read and open to change): opened on `west`'s full open day before the waiting day; en job `cv_axle`, 3.0 h, typed part cost 760.00, price 1,380.00; ru `outer_tie_rod`, 2.0 h, cost 21,000, price 32,000 |

### S07 A private customer
`named_customers.json` S7 and her car (`mileage_in` = `mileage_at_first_visit_*`). An `appointment` at `main`, `source` web_chat, `booked_at` on day A (`s7.booking_day`) by slot 6, `starts_at` the visit day at `s7.thread.visit`, `status` arrived. The `repair_order`: advisor slot 6, technician slot 12, opened at the visit time; jobs `brake_inspection` (approved, counter, 49.95 / 700), `front_pads_rotors` (approved, `message`, 493.00 / 12,520, standard tier), `rear_shocks_pair` (declined, `message`, `deferred`, at today's list 339.28 / 11,720); an `inspection` (brought by the brake inspection) with the eleven groups: "Brake pads: front pads and rotors" `bad` with a measurement and a photo, pointing at the pads-and-rotors job; "Shocks and struts: rear shock absorbers" `bad` (seeping), pointing at the declined job, which is therefore deferred; the other groups `good`; supplies 12.15 / 102.60; totals and tax as `s7.bill` (en: `before_tax` 555.10, `tax` 51.35 at `tax.rate.main`, `with_tax` 606.45; ru: `list_total` = `with_tax` 13,322.60, VAT inside 634.41, `before_tax` 12,688.19); one `payment` by card for `s7.bill.with_tax` the same day; a `service_reminder` `deferred_work` for the shocks, `status` `sent`, `sent_on` = the visit day + `erp.reminder.send_after_days` (she came back herself on slot 6's last working day before T; no appointment exists at T).

### S08 A wrong price
`named_customers.json` S8. An `appointment` at `main`, `source` phone, booked by slot 7 at the quote call (`s8.dates.quote_call`), `starts_at` the car-in day 08:00. The `repair_order` opened at the quote call as an estimate, advisor slot 7, `promised_at` the car-in day 17:00 (en; ru 18:00); job `timing_belt_kit` approved by phone at the call with `approved_amount` = `s8.price_quoted` (688.00 / 15,552); lines at today's list (`s8.breakdown`: 3.2 h at `price.hour.posted`, kit, coolant; total `s8.price_now`), technician slot 12; `in_progress` after lunch on the car-in day; `completed` and `invoiced` on the ready day (`s8.bill_list` with supplies `s8.supplies`, no discount: en 741.60 before tax; ru 16,182.40 as billed, VAT inside, `s8.bill_before_tax` 15,411.81 before VAT); the customer leaves without paying; on slot 4's next working day: `completed`, then `invoiced` again with a labour discount `s8.discount` (en 80, ru 1,800), `discount_approved_by_id` slot 4, reason `texts.json` `s8_discount_reason` ("goodwill: wrong quote and late car"), and `paid` that afternoon, card, `s8.paid_with_tax` (en 722.80; ru 14,382.40, before VAT `s8.paid_before_tax` 13,697.52). It is one of slot 7's three re-billed orders (`p07.rebilled`, section 4.5). ru dates per the ru call files (Saturday intake, Sunday walk-out, Monday pickup about 18:00).

### S11 The season
Section 4.1 curves; F4's `employee` rows (one per season, section 3) and his labour at `main` in his weeks at `pF4.billed_index`, mostly tyre and oil jobs.

### S13 Changed hours
No order or appointment on closed dates; none after 12:00 on the stocktake day (future appointments).

### S14 Attendance (ERP side)
F2: `employee.left_on`; his orders' comebacks at `pF2.comebacks` (section 4.6). Slot 11's two complaint orders (calls 29 and 30, below).

### S15 The mess
Section 6.

### S16 The anchor's review
Nothing beyond S01's A1 rows. The attached statement is generated from those rows by the core loader.

### Slot 8's open second look (`board.second_look_open`)
en: Dogwood Lane Florals' 2019 ProMaster City (small business, `main`); ru: ИП Абрамова's LADA Largus. A rear-pad order on the van at `main` a few days before slot 5 writes the card (`workday/<cfg>/cards.json`, card `F-recheck-open`, created on slot 5's last working day before T), technician slot 14; then a `warranty` order at `main` (the pads are inside their warranty in both markets: `comeback.definition`) opened at opening on the card's due day (slot 8's next working day), `comeback_of_id` = the rear-pad order, the redone job at its prices under `erp.warranty_order_totals`, status `approved` at T (the card is unstarted). It is one of slot 14's dealt comebacks (`p14.comebacks`). When the due day falls after T, only the rear-pad order exists and the van has an appointment at opening on the due day.

### The uncollected car (`erp.uncollected_car`)
One counter order at `west` of a private regular (a background customer of `west` with earlier visits, drawn by the generator; not a company on terms, not a story's customer): opened, worked and `invoiced` on `west`'s 3rd full open day before T by the background's rules for its job, and not collected: no `payment` row and status `invoiced` at T. No storage fee (`kb.storage`: five free working days). It is the planted answer to "which counter orders are not yet paid"; a background order completed late the day before T may stand beside it until it is collected.

### The story files' new facts (`checks/new_facts.json`)
The facts of the story calls and conversations, as fix pass A froze them; one ledger row per file (`nf.call.NN`, `nf.conv.NN`). Invented people are in `named_customers.json` (`story_callers`, `story_chat_customers`): name, phone and car as given, the VIN and plate formed by the generator; facts about A1 to A6 are also in `accounts.json` (`from_story_files`). A person named on a call or in a chat is a customer record with those facts; a booking made before a record existed has `customer_id` null and `contact_phone` (and `contact_name` when the file gives one) until check-in. Days are the file's (the call's day, "call + n days", the weeks of `stories/TIMELINE.md`; ru rota anchors per FIX-B section 2). Each row below with shop-system rows has a query of the same key in `checks.sql`. Files not listed plant nothing in the shop system (the call log, Chatwoot and the picture pools carry them).

| Ledger row | en | ru |
|---|---|---|
| `nf.call.01`, `.02`, `.12`, `.13`, `.35` | none: first-time callers with no booking (call 1's "saved quote" is not a shop-system estimate) | none (call 02's saved calculation is not an estimate; 12, 13 and 35 have no booking) |
| `nf.call.03` | `appointment` at `main` on the call's day 12:30, `source` phone, `contact_phone` +14235550146, `contact_name` null; the record and the 2012 Toyota Tacoma made at check-in, an order that day | `appointment` at `main` the next day 10:00 (a waiter: the page takes waiters from 10:00, `kb.booking.slots`), `contact_name` null; the record (named on the order) and an `oil_service` order at 8,579.50 list |
| `nf.call.04`, `.05`, `.06`, `.14`, `.26`, `.32` | `appointment` with the file's shop, day, hour and job, `contact_phone` set until arrival: 04 `main` call + 1 d 10:00 check engine diagnosis; 05 `main` call + 4 d 13:30 alignment; 06 `main` call + 2 d 08:00 road test and wheel bearing; 14 `main` call + 2 d 08:00 rear pads and rotors; 26 `east` call + 1 d 07:30 steering and suspension inspection; 32 `main` that day 08:00 flat repair | 04 `main` next day 11:00 suspension diagnosis 800; 05 `main` the Friday after the call 09:00 sway bar links 3,700; 06 none; 14 `main` the Wednesday after the call 14:00 drive belt 2,750 (`contact_name` the first name only); 26 `east` next day 10:00 front struts 18,580 and alignment 3,000; 32 `main` next day 09:30 muffler 9,180 (first name only) |
| `nf.call.07` | S04 above (the order approved over the driver's limit) | S04 above |
| `nf.call.09`, `.10`, `.11` | S08 above (09: the appointment, `source` phone, booked by slot 7) | S08 above (09: the Saturday booking made without a name, `contact_name` null; 11: the timing belt by slot 12, paid about 18:00) |
| `nf.call.15`, `.16`, `.18` to `.20` | S06 and S01 (call log only) | the same |
| `nf.call.17` | S01: the comebacks are E-2 (week T-26) and E-6 (week T-22), warranty orders | S01: Э-1 and Э-10 |
| `nf.call.21` | S01: SC-2's appointment and fleet PM order | S01 / A6: car № 1 (Х176АХ73) the day after the call, fleet ТО 9,710 and a low-beam bulb 800 at list; its previous ТО about three months before at 9,500 (the old hour) |
| `nf.call.22` | S01: the estimate sent two days late | the same, № 2 and № 5 |
| `nf.call.23` | S01: ND-22, no purchase-order number | A1's car № 07 (Т198ОК73) the day after the call: fleet ТО at the company price 8,724, no request number |
| `nf.call.24` | S01: ND-08, purchase-order number ND-60418 | A1's car № 24 (Р358ТН173) on the call's day 14:00: front pads, request number 247/10 |
| `nf.call.25` | S01: M-112, purchase-order number 4471B | S01: Т-17, request number 118/11 |
| `nf.call.27` | a regular of `east` with history: her last oil service has a battery item `watch` ("weak", cfg), no job declined; `appointment` on the Tuesday of week T-3 at 07:30, charging-system test and battery | a regular of `east` (his own car with a hub job in its history); an `oil_service` order on the Thursday after the call 10:00, 9,890, for his daughter's 2020 Lada Granta, which is on his record (so M8 stays at two) |
| `nf.call.28` | a regular of `east` with history; no booking | the same |
| `nf.call.29` | an order at `main` on the Tuesday of week T-10, lower control arm, technician slot 11, no alignment; a warranty comeback on the Friday of week T-10 pointing at it, alignment, first look slot 8 | an order at `main` the day before the call, front pads and discs, slot 11; on the call's day a comeback pointing at it (wheel nuts not tightened, first look by the foreman), `warranty` (inside the 30 days of `comeback.definition`; the file calls it «гарантийный») |
| `nf.call.30` | a water-pump order completed and paid on the Friday of week T-3 (659.37 with tax), slot 11; a warranty comeback that evening (a loose hose clamp) with a tow `order_sublet` by V8, `price` 0 | an oil service at `main` two days before the call, slot 11; a `warranty` comeback on the call's day 14:00 (undertray bolts, drain plug) |
| `nf.call.31` | `appointment` at `main` on the Monday of week T-6 at 09:00 for a check engine diagnosis, technician slot 10 (the misses are call-log rows) | `appointment` at `main` that day 13:00, engine computer diagnosis 1,200 |
| `nf.call.33` | a customer of `west` with history: an earlier order with a lower ball joint item `watch`, its job declined | the caller's father, a long-standing customer of `west` with history; no booking |
| `nf.call.34` | the mother's record at `west` with her 2010 Toyota Camry and its history; no booking | a customer of `west` with history; no booking |
| `nf.call.36` | a front brake order at `west` a few months before; `appointment` on the Friday of week T-2 at 14:00, cooling system pressure test | `appointment` at `west` that day 16:00, alignment 3,450 (first name only) |
| `nf.conv.01`, `.03`, `.21`, `.27` | none (the call's hour; offered times; no appointment) | none |
| `nf.conv.02` | S07: the estimate link sent about 10:05; the payment `received_at` about 15:10; the seeping shock is the right rear (its item's wording) | S07: sent about 10:40; paid about 18:40; right rear |
| `nf.conv.04` | S01: the web chat's estimate (SC-4 and SC-9), declined on expiry | S01: № 7 and № 8 |
| `nf.conv.05` | S01: the Monday lists and M-112's strut order under 4398A | S01: the Monday lists and Т-09's water pump under 96/07 |
| `nf.conv.06` | S06: the two purchase orders and their promise dates | the same |
| `nf.conv.08` | a regular of `east` (2013 Buick Enclave) with rear brakes recommended and declined at her last visit (`deferred`); `appointment` in week W+1 at 13:00 as the file states it after fix pass B (the Wednesday, with slot 16; D15) | a regular of `east` (2017 Volkswagen Polo), rear pads recommended at her last ТО; `appointment` at 14:00 on slot 16's last working day before the Thursday of W+1 (D15) |
| `nf.conv.09` | an alternator order at `main` on the Thursday of week T-18: 766.37 at list, `total` 852.01 with supplies and tax | a front wheel-bearing order at `main` on slot 5's first working day on or after the Thursday of week T-18: 7,902 at list, `total` 8,019.99 with supplies, VAT inside |
| `nf.conv.10` | `appointment` and order at `main` on the Monday of week T-8 at 14:00, cooling system pressure test | an order at `main` for a clutch replacement on a 2018 Lada Granta with the customer's own Valeo kit (labour only; the kit is not a part line), booked by his call |
| `nf.conv.11` | an order at `main` on the Tuesday of week T-11: oil service; rear brake pads raised and approved (260.31), cabin air filter raised and declined (67.94), `approval_method` message | `appointment` and oil-service order at `main` on the Saturday of week T-11 at 10:00 |
| `nf.conv.12` | one `appointment` at `main` for an alignment, `starts_at` the Thursday of week T-4 at 08:00 (the move from the Monday rewrote it) | an order at `main` on slot 6's first working day on or after the Friday of week T-5: ТО; sway bar links raised and approved (4,463), wiper blades raised and declined (3,403) |
| `nf.conv.13` | `appointment` and oil-service order at `main` on the Friday of week T-12 at 08:30 | `appointment` at `main` the day after the chat at 09:00, `contact_name` «Саня», no phone; outer CV joint on a 2014 Renault Logan |
| `nf.conv.14` | `appointment` at `main` on the Wednesday of week T-3 at 10:00, brake fluid flush | `appointment` at `main` on slot 7's first working day on or after the Tuesday of week T-3 at 18:00, seasonal tyre change |
| `nf.conv.15` | front brakes at `east` in week T-16; a `warranty` order on the Wednesday of week T-15 at 13:00 pointing at it (an anti-rattle clip reseated) | an A/C recharge at `east` in week T-16; a `warranty` leak check the day after the chat at 09:30 pointing at it |
| `nf.conv.16` | `appointment` at `east` on the Wednesday of week T-7 at 08:30 (the chat file's hour), pre-purchase inspection | `appointment` at `east` on the Wednesday of week T-7 at 11:00, pre-purchase inspection, booked by slot 17 |
| `nf.conv.17` | sway bar links (220.26) raised at `east` at an oil service on the Thursday of week T-12 and declined the next day | none (he did not come) |
| `nf.conv.18` | an order at `east` on the Friday of week T-20 at 14:00: four customer-supplied tyres mounted and balanced (`new_tyres_fitted` labour 100.00, no part lines) and the disposal fee at 3.50 a tyre as the file states | `appointment` at `east` on the Wednesday of week T-4 at 18:30, tyre fitting |
| `nf.conv.19` | a walk-in order (no appointment) at `west` on the Tuesday of week T-16 for a regular's mother's Buick, on her record | the same for a regular's father's Niva |
| `nf.conv.20` | a water-pump order at `west`, collected on the Tuesday of week T-9, `shop_supplies` 17.55 | the same, supplies 125.40 (3 % of labour 4,180) |
| `nf.conv.22` | an order at `west` on the Wednesday of week T-5: rear brake pads at 3 mm raised (225.77) and declined | an order at `west` collected the day before the chat: front pads at 2 mm raised (4,560) and declined; the car drawn by the generator |
| `nf.conv.23` | an estimate at `west` on the Friday of week T-10: check engine diagnosis 135.00, ignition coil 153.86, spark plugs 222.28, supplies 16.88, `total` 579.50 at 9.75 % | an estimate at `west` on slot 24's first working day on or after the Friday of week T-10: pressure test 950, water pump 13,366, belt 3,313.50, with supplies, VAT inside |
| `nf.conv.24` | `appointment` at `west` on the Tuesday of week T-17 at 11:30, battery and charging test | `appointment` at `west` on slot 24's first working day on or after the Tuesday of week T-17 at 17:00, A/C recharge |
| `nf.conv.25` | `appointment` at `west` on the Thursday of week T-13 at 07:30, check engine diagnosis | `appointment` at `east` on the Thursday of week T-13 at 18:00, engine computer diagnosis, booked by slot 17 |
| `nf.conv.26` | a regular of `east`: tyres balanced in March, a battery light in June; `appointment` on the Thursday of week T-6 at 09:00, brake inspection | a regular of `main`: a tyre change in April, an alignment in May; `appointment` on the Thursday of week T-6 at 11:00, tyre change and alignment |

These orders count inside the day's volume, and their comebacks inside the dealt comebacks of their mechanics (slot 11 for calls 29 and 30). The background never gives a second customer the phone, car and day of one of these rows.

## 6. The planted mess (S15), kind by kind, and how it stays countable

| Kind | Produced | Kept countable by |
|---|---|---|
| M1 duplicates | the 24 records of `S15_duplicate_pairs`, each with the pair's phone, its own vehicle row for the shared car, `created_location_id` from the file, and orders on both records (record b created later than record a's first order) | every other phone in `customer` is unique; `checks.sql` counts phones held by more than one customer = 12 |
| M2 no VIN | section 3, vehicle | exactly the oldest 3 % of rows are null |
| M3 wrong mileage | six orders, one in each of the last six quarters before T: three with `mileage_in` lower than the same vehicle's previous order (a digit dropped), three ten times the previous reading (a digit added), each of those on the car's last visit so that no later order reads as lower; at mixed shops; `mileage_out` follows the same mistake | every other order's `mileage_in` is at least the vehicle's previous one and under 3 × it |
| M4 never closed | `west`: an order opened on the Wednesday of week T-22, `completed` the next day, never invoiced (the car left; `mileage_out` filled); `main`: an order opened on the Tuesday of week T-12 left `in_progress`; `east`: one opened on the Tuesday of week T-10 left `approved` (work never started) (`s15.dates`) | section 4.5: no other order older than 60 days is in an open status |
| M5 walk-in | S02 above | one customer named as the walk-in record |
| M6 not one to one | `s15.mess` payments_not_one_to_one. en: every statement payment settles the orders of its statement, always more than one (one payment, many orders); the manifest names one statement as the planted instance and the count of statement payments is emitted per build; one counter order paid in two parts (card and cash, two `payment` rows of kind `payment`, the same day); one `refund` (card, the original card receipt in `reference`) against a counter order on which the customer was overcharged. ru: exactly one: a bank transfer settling one invoice that carries three orders of A3 in one month (every other invoice is one closed order); one order paid in two parts; one refund | deposits are kind `deposit`, so "paid in two parts" = orders with two or more rows of kind `payment` = 1; refunds = rows of kind `refund` = 1; en statements with fewer than two orders = 0; ru statements with more than one order = 1 |
| M7 typed parts | section 3, order_part | dealt to the exact share per shop group |
| M8 wrong customer | `S15_car_on_the_wrong_customer` cases: case 1 an order of the car on the father's (en Harold Renfro) / husband's (ru) record while `vehicle.customer_id` is the owner's; case 2 an order of the company's vehicle on the owner's personal record | every other order has `customer_id` = `vehicle.customer_id` |
| M9 voids | sections 4.7 and S02 | voids keep D1 totals |
| M10 clocks | section 1 | `location.time_zone` is the only zone |
| M11 bulk load | section 3, customer | every `west` customer created before its first order, on the purchase day |

## 7. Background never makes a second answer

The build asserts each line; a failure stops it.

- S1.1: no customer with `payment_terms_days` other than A5 has no order in the last 90 days; none but A5 and A6 has last-30-day orders under half of a pre-T-150 block.
- S1.2: no A5 order after its last visit.
- S1.6: no account's background estimate waits two days or more for its first decision: A6's five are the only ones; A6's declined estimates are its four (`s1.a6`).
- S1.4 and S16.3: A1's statements follow `acct.A1.days_to_pay` only.
- S1.7: no statement of A2 or A4 is `overdue` at T.
- S2.1, S2.3, S2.5: no discount of 15 % or more by anyone but F1; no discount of 10 % or more without an approver after the rule except slot 23's two; at `west` after the rule exactly the four discounted cash orders; en no void with a payment except F1's 14.
- S2.8: en no till difference of −20 or less except F1's 19; ru no issue without an order line except F1's 46, and no order at `west` whose clocked hours exceed sold hours by more than 1 hour except F1's 22.
- S5.1, S5.3: `east`'s sold share by day follows the advisor on duty only; no diagnostic order at `east` for a `main` customer in the leave weeks except the eleven.
- S6.2: the waiting orders at T are exactly `s6.waiting_at_t`.
- S6.3: pad comebacks equal `s6.counts`.
- S7, S8: the named customers' phones are theirs alone; S8's job is the only approved job of slot 7 whose `approved_amount` differs from its lines; only slot 7's three orders are invoiced twice (`p07.rebilled`).
- S11: no seasonal tyre job outside the windows beyond the 0.053 base; no air-conditioning spike outside May to August.
- S14.5: F2's comebacks are `pF2.comebacks` of his last six months.
- S15.1 to S15.6: the counts of section 6; every warranty and goodwill order follows `erp.warranty_order_totals`, so a revenue or discount count that keeps `order_type = 'customer_pay'` never meets them.

## 7b. The generator's own choices

No story, ledger row or knowledge page fixes these; they are written here so that a build is explainable. A check never rests on one.

- Raised jobs on an order that carries any: 3 or 4, dealt so that the mean is `mix.rec_jobs_per_such_order`.
- A background void: 5 to 60 minutes after the order was opened, inside opening hours.
- Collection and payment: the day of completion when the order is completed at least 30 minutes before closing, else the next open morning within two hours of opening.
- The wait of a diagnostic order at `main`: uniform between 0 and twice the mean (`s5.leave.wait_days_normal`, `s5.leave.wait_days_in_leave`).
- An appointment is booked ahead by a number of days drawn evenly on each side of the median of `erp.appointment.lead_days`.
- A car's age counts from 1 July of the year before its model year.
- A payment's reference: six digits.
- ru order numbers: each shop's running number starts at 000001 on the first order of the history window; the dictionary's «ЗН1-004217» is an example of the form.
- F4's orders get no comeback; F2's orders before the window of `pF2.comebacks` come back at `comeback.main`.
- Rosters where the ledger gives a share and no day: slot 28's three working days and slot 21's day at `main` are drawn once per week; ru F1 and F3 follow the phase of the advisor each was replaced by (F1: slot 24's; F3: slot 7's); ru F2 kept the days off slot 14 has now; ru F4 is off on Sunday.
- A planted fact's times, readings, mileage and car class are the story file's wherever it states them (a chat's approval minute, "this morning", "after lunch", a reading in millimetres, an odometer, a price that fits one vehicle class); the generator draws only what the file leaves open, and draws a car of the class the file's price is for.
- A planted customer's earlier visits that no file dates ("a regular", "his last oil service"): their days and lead jobs are drawn like background visits of that customer, before the fact's own day.
- A relative no file names in full (en chat 19's mother, ru chat 19's father, ru call 33's father «Фарид») gets the story person's surname where one is given and whatever is missing from the generator's name lists; the car is on the relative's record, as the new-facts table says, and the caller's or writer's own record stays without it. en call 34: the record is Peggy Womack's and carries her son's number, the only contact the call gives.
- ru chat 10: the customer phones that afternoon; the appointment (`source` phone, booked by slot 5) and the clutch order are at `main` on slot 5's next working day after the chat, 09:00.
- en call 30's tow is inside the hook-up's included distance (`kb.towing`): the sublet's cost is the hook-up alone.
- Opening stock and the par: a stock order per shop and vendor received on the shop's last full open day before its history, each stocked part at its par: twice its mean weekly issues of the first twelve weeks, at least one, in whole units (no source gives a pack size), raised at `main` and `west` to the most the shelf gives out between two deliveries. `east` keeps the base par and draws on `main` by the transfer of section 4.10 on the last 13:00 run before it would go below zero. A stocktake finds one fewer only when there is one; the opening stock is not returned.
- Deliveries (`kb.supplier_times` gives runs and cut-offs, not minutes): an order placed by a run's cut-off arrives with that run, between the run's hour and an hour after it; a next-day delivery within an hour of opening. `west`'s 9:00 and 14:00 for V2 are cut-offs ("call by 9 for the morning one").
- An account's estimate that ends declined is declined at check-in, not by expiry: S1.6 keeps A6's five the only account estimates that wait two days.
- An account's month with a single order is billed with the next month's orders, so no statement settles one order alone (M6); the order stays `invoiced` meanwhile.
- ru A6's chat estimate (`nf.conv.04`) is written the next morning: the chat came after closing.
- en slot 29's cover (`cast.json`): two or three days a week from F3's `left_on` to slot 7's start; otherwise only a day another `main` advisor is absent.
- A raised job on an order of T's day is decided by T when the order came in two hours or more before T, else it is still with the customer at T; `pNN.sold_rec` is dealt on the decided jobs only.
- A comeback comes in after its first order's completion as built, at least the shortest gap of `erp.comeback.gap_days` later, on a day its advisor writes orders; a pad comeback is opened more than a week before T.
- An order carries at most one subcontractor's job: the car is away while it is done.
- A re-issued bill is billed and paid on the same day, and the parts step does not re-time its statuses.
- Slot 22's two approved discounts after the rule lie more than 14 days before T.

## 8. The two sizes

`size.small.density` = 0.25 scales every background count (orders a day, customers, vehicles, appointments, stock orders, `s2.f1.orders`, `s2.f1.cash_orders`, the background part of `s2.walkin.total`, `s6.west_orders`, `s6.counts` cases, `s5.rec_jobs_on_days_off`: `size.small.scales`). Fixed in both sizes (`size.small.fixed`): the cast, every planted order and row of sections 5 and 6, `acct.*.visits` and the statements they bring, `s2.f1.discounted` and the second and third ways, `s6.waiting_at_t`, prices and tax. Rate rows are dealt on the smaller n; those whose minimum count the small size cannot reach are not asserted there (`size.small.rate_rule`; `checks.sql` prints them as "full size only"). At small size the accounts are a larger share of orders, and F1's 35 discounts are most of his 40 cash orders: that is why `s2.f1.discount_share` and `acct.six.*` are full size only.

## 9. Dates relative to T, each shop's clock

Every planted date comes from `stories/TIMELINE.md` anchors computed once per build; background dates are drawn inside the history window on open days and hours of the shop. The local-clock rule of section 1 applies to every timestamp. When the build is run on a closed day, T is the close of the flagship's last open day (`time.t_rule`), and "today's orders" are that day's.

## 10. Rows per table at full size

Values with T = Fri 2026-11-13; O = `volume.orders_history` (en 17,490; ru 18,209). Shares from `catalogue.json` (`share_of_orders`), `mix.json` and the ledger; rows that rest on the background rows of section 11 are marked P (estimates until the generator counts them).

| Table | Formula | en | ru |
|---|---|---:|---:|
| location | 3 | 3 | 3 |
| employee | 32 people (slots 1 to 29, F1 to F3) + F4 seasons in the history (en 2: June 2025, June 2026; ru 5: Oct 2024, Apr and Oct 2025, Apr and Oct 2026) | 34 | 37 |
| referral_source | list of `erp.referral.mix` (P) | 8 | 8 |
| customer | 37 (6 accounts, 30 small, the walk-in) + home pools at start (private orders a year at `main` and `east`, en 6,484, ru 6,707, × returning share / visits a year: en 3,026, ru 3,114) + `west`'s bulk load (en 2,002 × 0.7 / 1.5 = 934; ru 2,238 × 0.65 / 1.4 = 1,039) + new private customers ((1 − returning share) × private orders: private orders = O − account visits 1,699 − small 1.4 % − walk-in 240 = en 15,306, ru 16,015; new en 4,592, ru 5,605) + named and callers (about 60) (all P) | ≈ 8,650 P | ≈ 9,850 P |
| customer_contact | `accounts.json` contacts | 15 | 16 |
| vehicle | fleets 98 + small 53 / 52 + private customers × 1.12 / 1.08 (P) + 240 walk-in cars + named | ≈ 10,050 P | ≈ 11,000 P |
| service_category | catalogue | 10 | 10 |
| canned_job | catalogue | 70 | 70 |
| labor_rate | en 3 shops × 2 classes × 2 periods; ru `main`, `east` 2 × 4, `west` 2 × 3 | 12 | 22 |
| vendor | vendors.json | 8 | 9 |
| part | distinct (brand, part number) of the catalogue options with the class variants of scaling slots, counted by the build | counted by the build | counted by the build |
| appointment | (O − comebacks 462 / 464 − walk-in 240 − A2's slot vans, about 520) × 0.65 / 0.55 arrived (P) / (1 − no-show − cancelled: 0.85 / 0.82) (P) + A2's slot vans; A2's other orders book as any order does | ≈ 12,950 P | ≈ 11,900 P |
| repair_order | O + declined estimates (`erp.estimate.declined_share`: private orders 15,306 / 16,015 × 6/94, accounts' visits 1,699 × 2/98, A6's four) | ≈ 18,510 | ≈ 19,270 |
| order_status_history | O × (6 rows of a paid path + 2 × share entering `waiting_parts`, about 0.1) | ≈ 108,400 | ≈ 112,900 |
| order_job | O × (jobs per order 2.623 / 2.365 + declined raised jobs 0.65 × 3.094 × (1 − 0.5373) = 0.931 / 0.6 × 3.14 × (1 − 0.5334) = 0.879 + courtesy 0.8 / 0.7) | 76,143 | 71,818 |
| order_labor | O × (jobs with hours 2.622 / 2.333 + declined raised jobs + en the courtesy line 0.8) | 76,128 | 58,498 |
| order_part | O × (part slots of sold jobs 2.487 / 2.183 + of declined raised jobs 0.932 / 0.864) | 59,807 | 55,494 |
| order_sublet | O × sublet job share 0.0023 / 0.0084, + 1 tow | 41 | 154 |
| order_fee | O × orders with hourly labour 0.788 / 0.835 + O × (`new_tyres_fitted` + `tyre_storage` shares: en 0.0318 + 0.0005, ru from the catalogue) | 14,354 | 15,924 |
| inspection | O × (courtesy 0.8 + 0.2 × (brake 0.0711 + pre-purchase 0.0136)); ru 0.7 + 0.3 × (0.0478 + 0.0116); + comebacks O × `comeback.company` | ≈ 14,750 | ≈ 13,540 |
| inspection_item | inspections × 11 groups + raised jobs beyond the first of a group (en O × 0.65 × (3.094 − 2.5), ru O × 0.6 × (3.14 − 2.5); 2.5 groups with a job per such order is an estimate) | ≈ 169,000 | ≈ 155,900 |
| time_entry | O × 2.622 / 2.333 approved lines × 1.1 (second entries) | ≈ 50,400 | ≈ 46,700 |
| statement | en: months with orders per account (A1 to A4, A6: 24; A5: 9) | 129 | — |
| statement (ru) | one per account order (A1 584, A2 633, A3 122, A4 125, A5 64, A6 171) − 2 for the combined invoice | — | ≈ 1,697 |
| payment | counter orders paid (O − account visits 1,699 − comebacks − background voids 0.3 %: en 15,277, ru 15,991) + deposits (rebuilds O × 0.0023 and special orders over the limit, about 300) + statement payments (en ≈ 125; ru one per paid invoice ≈ 1,640) + 1 split + 1 refund | ≈ 15,700 | ≈ 17,930 |
| cash_drawer_close | en `main` (21.24 + 4.35) × 24, `east` 21.24 × 24, `west` 21.24 × 14; ru 30.27 × (24 + 24 + 14) | 1,421 | 1,877 |
| purchase_order | O × `parts.po_per_order` 0.6 | 10,494 | 10,925 |
| purchase_order_line | special-order lines O × (2.487 − 1.216) / (2.183 − 1.024) + stock lines (P) | ≈ 27,600 P | ≈ 25,800 P |
| stock_level | stocked parts × shops (P) | ≈ 300 P | ≈ 300 P |
| stock_movement | receipts (= lines) + issues (≈ O × part slots of sold jobs × 0.97 not typed) + returns + transfers and adjustments | ≈ 72,700 P | ≈ 66,600 P |
| part_return | lines × `parts.returned_share` 6 / 4 % | ≈ 1,650 | ≈ 1,030 |
| service_reminder | deferred: O × 0.931 / 0.879 × `erp.inspection.bad_share` 0.5 (P) + maintenance due: O × oil service 0.3191 / 0.244 | ≈ 13,700 | ≈ 12,450 |
| **All** | the sum of the rows above; the part rows, a few hundred, are counted by the build | **≈ 749,000** | **≈ 721,000** |

Small size: background rows × 0.25 plus the fixed rows; about a third of full.

## 11. The background numbers: ledger rows

The 22 background numbers this spec once proposed are ledger rows, accepted as proposed in fix pass A (class designed; the ledger's `reasoning` keeps the why). The values below are the ledger's (`../ledger.md`); where they differ, the ledger wins. "same" = the Russian value equals the English.

| Ledger key | en | ru | Unit |
|---|---|---|---|
| `erp.customer.returning_share` | 70 | 65 | % of private background orders by a customer seen before |
| `erp.customer.visits_per_year` | 1.5 | 1.4 | visits a year of a returning private customer |
| `erp.customer.email_share` | 55 | 30 | % of private customers with an e-mail on record |
| `erp.west.bulk_caps_share` | 40 | same | % of bulk-loaded names written in capitals, surname first |
| `erp.vehicle.per_private_customer` | 1.12 | 1.08 | cars per private customer |
| `erp.vehicle.yearly_distance` | 11000 | 15000 | miles (en), km (ru) a private car is driven a year, for odometers |
| `erp.referral.mix` | {"Friend or family": 30, "Google": 25, "Drove by": 10, "Previous visit": 15, "Other": 5, "blank": 15} | {"Знакомые": 30, "Яндекс Карты": 20, "2ГИС": 15, "Avito": 5, "Проезжал мимо": 10, "blank": 20} | % of customers by how they found the shop; the bulk load is blank |
| `erp.appointment.share_of_orders` | 65 | 55 | % of orders, comebacks and the walk-in record left out, that came from a booking |
| `erp.appointment.outcome` | {"no_show": 10, "cancelled": 5} | {"no_show": 12, "cancelled": 6} | % of bookings that do not happen |
| `erp.appointment.source` | {"phone": 75, "web_chat": 10, "messenger": 5, "walk_in": 10} | {"phone": 55, "web_chat": 8, "messenger": 27, "walk_in": 10} | % of bookings by where they were made |
| `erp.appointment.lead_days` | {"min": 1, "max": 10, "median": 3} | {"min": 1, "max": 7, "median": 2} | days from booking to visit |
| `erp.approval.method` | {"phone": 50, "link": 35, "message": 10, "counter": 5} | {"phone": 45, "link": 10, "message": 40, "counter": 5} | % of decisions on raised jobs by how the customer answered |
| `erp.inspection.bad_share` | 50 | same | % of raised jobs whose inspection item is bad, the rest watch; a declined bad job is deferred |
| `erp.time.clocked_over_sold` | {"everyone": 0.9, "slot 11": 0.75, "slot 14": 1.3} | same | clocked hours over sold hours on a job |
| `erp.comeback.gap_days` | {"min": 2, "max": 120, "median": 21} | {"min": 2, "max": 30, "median": 10} | days from the first order's completion to its comeback |
| `erp.statement.pay_day` | {"A2": 25, "A3": 12, "A4": 13, "A5": 26, "A6": 27, "spread": 2} | {"A2": 25, "A3": 11, "A4": 12, "A5": 26, "A6": 27, "spread": 2} | days from a bill's issue to its payment, the accounts that pay inside their terms |
| `erp.reminder.send_after_days` | 14 | same | days after the decision a deferred-work reminder is sent |
| `erp.stock.stocked_jobs` | ["oil_service", "engine_air_filter", "cabin_air_filter", "wiper_blades", "headlight_bulb", "brake_fluid_exchange", "coolant_exchange", "battery_replace", "refrigerant jobs at main only"] | same | jobs whose parts come from the shelf, not from a purchase order |
| `erp.stock.reorder` | weekly: last week's issues rounded up to the pack | same | how stock purchase orders are made |
| `erp.stock.stocktake_adjust_share` | 8 | 10 | % of stocked lines adjusted by one unit at a half-yearly count |
| `erp.part_return.rejected_share` | 5 | 8 | % of returns the vendor refused |
| `p07.rebilled` | 3 | same | orders of slot 7 re-issued after invoicing |

Rows fix pass A added for the controller's answers on this schema, used in sections 3 to 5:

| Ledger key | en | ru | Unit |
|---|---|---|---|
| `erp.warranty_order_totals` | a warranty or goodwill order keeps its lines at their prices; the whole amount is in discount_total, total is 0, status paid, no payment row | same |  |
| `erp.estimate.declined_share` | {"private": 6.0, "accounts_on_terms": 2.0} | same | % of background estimates that end declined or expired, whole |
| `erp.inspection.bad_documented` | {"main": 92, "east": 96, "west": 65} | same | % of inspection items marked bad that carry both a measurement and a photo, by shop |
| `parts.on_time.V3` | 88 | 87 | % of purchase orders received on the promised day, vendor V3 |
| `parts.on_time.V4` | 90 | 91 | % of purchase orders received on the promised day, vendor V4 |
| `parts.on_time.V5` | 84 | 80 | % of purchase orders received on the promised day, vendor V5 |
