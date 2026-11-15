# Data dictionary: the shop-management database (seed v1, schema `shop`)

The company's own shop system: orders, cars, parts and money for three shops, kept in a Postgres database of its own and read by the product as the source `erp`. 31 tables. Table and column names, statuses and every enumerated value are English codes in both configurations; free text (names, addresses, complaints, job and part descriptions, notes, reasons) is in the configuration's language and is marked **text (cfg)** below. The database carries no comments: this file, the generator spec and the context notes are where meaning lives.

Conventions that hold for every table:

- Keys are integers with no meaning; `<table>_id` is the primary key, `<thing>_id` a foreign key.
- Money is `numeric(12,2)` in the configuration's one currency (USD or RUB), never converted.
- Every `timestamp` is the wall-clock time of the shop where the thing happened, with no zone. The zone is `location.time_zone`. `west` is an hour behind `main` and `east` in both configurations. A `date` is that shop's calendar day.
- Mileages are miles in the English configuration and kilometres in the Russian one. No column says which.
- Phones are stored in E.164 (`+14235550142`, `+79073786035`).

Access by rank (tenant settings, not the database): workers have no data tools; junior and up read every table; `employee.pay_type` and the till counts (`cash_drawer_close.float_amount`, `expected_cash`, `counted_cash`, `difference`, `note`) are hidden below middle; customer phone, email and address (`customer.phone`, `email`, `address`, `customer_contact.phone`, `email`, `appointment.contact_phone`) are readable from junior in the demo tenant.

## Denormalisations kept

Real shop systems repeat facts. These are the ones this database keeps, each named by the design; no other column repeats another.

| # | Column(s) | Repeats | Why it stays |
|---|---|---|---|
| D1 | `repair_order.labor_total`, `parts_total`, `sublet_total`, `fees_total`, `discount_total`, `tax_total`, `total` | the sums of the order's lines (on a warranty or goodwill order `discount_total` is the whole amount of the lines and fees, so `total` is 0) | design 2.4: totals are stored on the order as well as on its lines, and a void keeps them |
| D2 | `repair_order.status` | the last `order_status_history` row of the order | design 2.2: the order has a status; the history has each change |
| D3 | `repair_order.voided_at` | the time of the order's `void` history row | design 2.2: the order carries its void fields |
| D4 | `statement.total` | the totals of the orders on the statement | design 2.2: a statement has its total |
| D5 | `cash_drawer_close.difference` | `counted_cash - expected_cash` | design 2.2: expected, counted, difference |
| D6 | `order_part.brand` | `part.brand` when `part_id` is set | design 2.2: a part line carries its brand; a typed line has no part to read it from |
| D7 | `order_labor.amount` | `hours * rate` on hourly-priced lines | a menu-priced line has a fixed amount that no product of columns gives |
| D8 | `stock_level.quantity_on_hand` | the sum of `stock_movement.quantity` for the shop and part | design 2.2: what a shop holds now, beside every movement |
| D9 | `labor_rate.valid_to` | the day before the next row's `valid_from` | design 2.2: a rate with the dates it held |

Document snapshots are not counted as denormalisations: a line copies the catalogue's name and price at the moment it was written (`order_job.description`, `order_part.description`, `order_part.unit_cost`, `unit_price`, `order_labor.rate`), and later catalogue changes do not touch it.

## The planted mess (story S15), by the columns where it lives

| Kind | What | Where |
|---|---|---|
| M1 | the same customer twice, the name spelled two ways, one phone (12 pairs); each record has its own row for the shared car | `customer.name`, `customer.phone`, `vehicle.vin`, `vehicle.plate` |
| M2 | cars without a VIN, the oldest (3 %) | `vehicle.vin` null |
| M3 | a mileage lower than the car's visit before, or ten times its neighbours (6 orders) | `repair_order.mileage_in`, `mileage_out` |
| M4 | orders never closed (3) | `repair_order.status` in an open status, `opened_at` long ago |
| M5 | the walk-in customer at `west` (240 orders at full size) | `customer.name`, `repair_order.customer_id`, `vehicle.customer_id` |
| M6 | payments that are not one to one | `payment.statement_id`, several `payment` rows on one order, `payment.kind = 'refund'` |
| M7 | parts typed by hand, no part number (9 % of part lines at `west`, 1 % at home) | `order_part.part_id` null |
| M8 | a car on the wrong customer (2 orders) | `repair_order.customer_id` <> `vehicle.customer_id` |
| M9 | voided orders keep their totals | `repair_order.status = 'void'` with D1 filled |
| M10 | times in each shop's own clock | every `timestamp`; `location.time_zone` |
| M11 | `west`'s customers loaded in bulk on the purchase day | a spike of `customer.created_at` with `created_location_id` = `west` |

## location

One row is a shop. Three rows: `main`, `east` and `west` of the design, named as staff call them.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `location_id` | integer | no | key |
| `name` | text | no | the short name staff use: the street the shop stands on ("East Main", "Bonny Oaks", "Charlotte Pike"; «Московское шоссе», «Инженерный», «Техническая»). Text (cfg) |
| `address` | text | no | street address with city and postcode, as written in the market. Text (cfg) |
| `phone` | text | no | the shop's public line, E.164 |
| `time_zone` | text | no | IANA zone of the shop's wall clock (`America/New_York`, `America/Chicago`; `Europe/Ulyanovsk`, `Europe/Moscow`). The only place a zone is stored |
| `tax_rate` | numeric(5,3) | no | the tax rate in per cent the shop charges today. English configuration: sales tax, 9.250 at the two Chattanooga shops (`main`, `east`) and 9.750 at the Nashville shop (`west`), which has had that rate for its whole history here. Russian configuration: VAT, 5.000 at every shop. Today's only: an order carries its own rate in `repair_order.tax_rate` |
| `bays` | smallint | no | working bays |
| `latitude` | numeric(9,6) | no | the shop's position |
| `longitude` | numeric(9,6) | no | the shop's position |
| `opened_on` | date | no | the first day the shop traded under this company; for `west` the day it was bought, which is also the day its records start here |

Traps: comparing times across shops without converting by `time_zone` (M10); taking `tax_rate` as the rate of an old order (the Russian VAT began on 2025-01-01).

## employee

One row is a member of staff as the shop system knows them: owners, office, managers, advisors, the foreman, the parts manager and technicians, current and former. They share no key with the product's people: match by name. A seasonal hire has one row per season he worked (a rehire is a new record).

| Column | Type | Null | Meaning |
|---|---|---|---|
| `employee_id` | integer | no | key |
| `location_id` | integer | yes | home shop; null for the two owners, who belong to no shop |
| `first_name` | text | no | given name. Text (cfg) |
| `middle_name` | text | yes | the patronymic in the Russian configuration where staff use one; null otherwise. Text (cfg) |
| `last_name` | text | no | family name. Text (cfg) |
| `role` | text | no | the system's role: `owner` = an owner of the company; `office` = bookkeeping and payroll; `manager` = runs one or more shops (the service manager of the home shops, the shop manager of `west`); `advisor` = writes orders at the counter (lead advisors included); `foreman` = runs the shop floor and rechecks comebacks; `technician` = works on cars, clocks job time; `parts` = buys and receives parts |
| `title` | text | no | the job title the company uses ("Lead Service Advisor", «Старший мастер-приёмщик»). Text (cfg) |
| `pay_type` | text | no | how the person is paid: `salary` = a fixed salary (with or without a bonus); `hourly` = paid for hours at work; `flat_rate` = paid for the hours sold on their jobs. Amounts are in payroll, not here. Hidden below middle rank |
| `hired_on` | date | no | the day the person joined the company (for people who came with `west`, the purchase day) |
| `left_on` | date | yes | the last day of employment; null while employed. No reason is recorded anywhere |

Traps: the people who left are still here and their orders still point at them; the seasonal fitter appears once per season; a manager or the foreman can appear as technician on a comeback recheck; `role` does not tell a lead advisor from an advisor (`title` does).

## referral_source

One row is an answer to "how did you hear about us", as the counter picks it from a list.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `referral_source_id` | integer | no | key |
| `name` | text | no | the answer as listed ("Friend or family", «Знакомые»). Text (cfg) |

Traps: most customers have none; the bulk-loaded `west` customers have the one the previous owner's system carried or none.

## customer

One row is a person or a company the shop does business with. Company accounts billed on terms carry payment terms and a credit limit; everyone else pays at the counter. One record is not a customer at all: `west`'s "Walk-in" (M5).

| Column | Type | Null | Meaning |
|---|---|---|---|
| `customer_id` | integer | no | key |
| `kind` | text | no | `person` = a private customer; `company` = a business, billed on terms or paying at the counter |
| `name` | text | no | as typed at the counter: "First Last" for people in the English configuration, «Фамилия Имя Отчество» in the Russian one; the bulk load wrote "LAST, FIRST" in capitals; companies by trade name. Text (cfg) |
| `phone` | text | yes | main phone, E.164; null on the walk-in record. The pair test for duplicates: two records with one phone are one customer (M1) |
| `email` | text | yes | e-mail |
| `address` | text | yes | postal address. Text (cfg) |
| `price_class` | text | no | which `labor_rate` and parts prices apply: `standard` = the posted price list; `company_account` = the negotiated class of the two big accounts (about 10 % under list) |
| `payment_terms_days` | smallint | yes | days to pay a bill; set only for the six accounts billed on terms; null = pays at the counter |
| `credit_limit` | numeric(12,2) | yes | the most the account may owe; set only for the six accounts billed on terms |
| `referral_source_id` | integer | yes | how they found the shop; null = not asked |
| `created_location_id` | integer | no | the shop where the record was made |
| `created_at` | timestamp | no | when the record was made (that shop's clock) |
| `notes` | text | yes | standing instructions and the drivers' authority list of a company account. Text (cfg) |

Traps: the 12 duplicate pairs (M1); the walk-in record is not a customer (M5); `west`'s customers all "created" on the purchase day with no earlier history (M11); a company's small vehicles are sometimes under the owner's personal record (M8); `kind = 'company'` is not the same as billed on terms (`payment_terms_days`).

## customer_contact

One row is a named person at a company customer, with the dates they held the role. A driver who is not a contact is not here.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `customer_contact_id` | integer | no | key |
| `customer_id` | integer | no | the company |
| `name` | text | no | full name. Text (cfg) |
| `role` | text | no | the job at the company ("Fleet Manager", «бухгалтер»). Text (cfg) |
| `phone` | text | yes | direct line or mobile, E.164 |
| `email` | text | yes | e-mail |
| `started_on` | date | no | first day in the role |
| `ended_on` | date | yes | last day in the role; null = still in it |

Traps: a contact who left keeps the row with `ended_on`; who the contact was on a date needs the dates.

## vehicle

One row is a car on a customer record: the VIN may be empty, the plate is as written, the unit number is a fleet's own.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `vehicle_id` | integer | no | key |
| `customer_id` | integer | no | the current owner on record |
| `vin` | text | yes | 17-character VIN; null when it was never read (M2: the oldest cars) |
| `plate` | text | yes | registration plate as typed; null if not recorded |
| `year` | smallint | no | model year |
| `make` | text | no | maker as typed ("Ford", «ГАЗ», "LADA"). Text (cfg) where the market writes it its own way |
| `model` | text | no | model as typed. Text (cfg) |
| `engine` | text | yes | engine as typed; null when not recorded |
| `vehicle_class` | text | no | the price class of the car for labour hours and parts: `car` = passenger cars and compact crossovers; `suv` = mid-size and large crossovers and minivans (ru: crossovers and unibody SUVs); `truck` = pickups and body-on-frame SUVs; `van` = commercial vans |
| `unit_number` | text | yes | a company fleet's own number for the vehicle ("ND-08", «12»); null for private cars |

Traps: a duplicate customer brings a duplicate vehicle with the same VIN and plate (M1); missing VINs (M2); an order's car may not belong to the order's customer (M8); the walk-in record owns many unrelated cars (M5).

## service_category

One row is a kind of work: maintenance, brakes, tyres and alignment, diagnostics, suspension and steering, air conditioning, battery and electrical, engine and cooling, transmission and driveline, inspections.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `service_category_id` | integer | no | key |
| `code` | text | no | stable English code (`maintenance`, `brakes`, `tyres_alignment`, `diagnostics`, `suspension_steering`, `air_conditioning`, `battery_electrical`, `engine_cooling`, `transmission_driveline`, `inspections`) |
| `name` | text | no | the name shown. Text (cfg) |

## canned_job

One row is a catalogue job (about seventy) with its standard hours.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `canned_job_id` | integer | no | key |
| `code` | text | no | stable English code, the catalogue key (`front_pads_rotors`, `timing_belt_kit`) |
| `service_category_id` | integer | no | its category |
| `name` | text | no | the job's name as printed on an order. Text (cfg) |
| `hours` | numeric(5,2) | no | standard hours for a car of class `car`; other classes take more |
| `labor_pricing` | text | no | `hourly` = labour is hours times the hour in force; `menu` = a fixed labour price that moves only at a price rise. Shop supplies are charged on hourly labour only |
| `menu_price` | numeric(12,2) | yes | today's fixed labour price, standard class, class `car`; null for hourly jobs |

Traps: `menu_price` and `hours` are today's; an old order's prices are on its lines, not here.

## labor_rate

One row is a posted labour hour for one shop and one price class, with the dates it held.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `labor_rate_id` | integer | no | key |
| `location_id` | integer | no | the shop |
| `price_class` | text | no | `standard` = the posted hour; `company_account` = the negotiated hour of the two big accounts |
| `rate` | numeric(10,2) | no | money per hour |
| `valid_from` | date | no | first day in force |
| `valid_to` | date | yes | last day in force; null = in force today (D9) |

Traps: the rate of a past order is the row in force on its date, not today's; the Russian configuration has several rises in the two years; `west` has rows only from its purchase.

## vendor

One row is a parts supplier or a subcontractor (transmission, glass, steering racks, towing), with its terms.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `vendor_id` | integer | no | key |
| `name` | text | no | trading name with its legal form as the trade writes it. Text (cfg) |
| `kind` | text | no | `parts` = sells parts the shop fits; `sublet` = does work for the shop (rebuilds, glass, racks, towing) billed as sublet |
| `payment_terms_days` | smallint | no | days the shop has to pay the vendor |
| `phone` | text | no | E.164 |
| `email` | text | yes | e-mail |

## part

One row is a catalogue part: number, brand, today's cost and list price. Fluids sold by volume have no number.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `part_id` | integer | no | key |
| `part_number` | text | yes | the maker's number; null for fluids and parts sold by description or size |
| `brand` | text | no | the brand ("Wagner ThermoQuiet", "Calder ValueStop", «BREMHOF») |
| `description` | text | no | what it is. Text (cfg) |
| `unit` | text | no | the unit it is sold in (`ea`, `qt`, `set`; «шт», «л», «компл»). Text (cfg) |
| `cost` | numeric(12,2) | no | today's purchase price |
| `list_price` | numeric(12,2) | no | today's list price for a standard customer |

Traps: prices here are today's. They have held since go-live (G, 175 days before T); before G they were lower each year by 3 % (en) or 12 % (ru), so a line older than G shows a lower price.

## appointment

One row is a booking: when, for whom, at which shop, where it came from, and whether it was kept.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `appointment_id` | integer | no | key |
| `location_id` | integer | no | the shop |
| `customer_id` | integer | yes | the customer; null when a first-time caller was booked before a record existed |
| `vehicle_id` | integer | yes | the car; null when not yet on record |
| `contact_name` | text | yes | the name given when there was no record; may be empty. Text (cfg) |
| `contact_phone` | text | yes | the phone given when there was no record, E.164 |
| `starts_at` | timestamp | no | when the car is due (shop clock) |
| `duration_min` | smallint | no | the time the booking holds, minutes |
| `source` | text | no | where it came from: `phone` = a call; `web_chat` = the website chat (booked by staff from the hand-over); `messenger` = Telegram, VK or Avito; `walk_in` = made at the counter in person |
| `status` | text | no | `booked` = made; `confirmed` = the customer confirmed; `arrived` = the car came (an order exists); `no_show` = did not come; `cancelled` = called off |
| `reason` | text | yes | what the customer asked for. Text (cfg) |
| `booked_at` | timestamp | no | when it was made |
| `booked_by_id` | integer | yes | the employee who made it |
| `repair_order_id` | integer | yes | the order opened when the car arrived |

Traps: many orders have no appointment (drop-ins); a booking's customer can be empty; future bookings exist (state at T).

## repair_order

One row is one visit of one car, from estimate to paid: the estimate, the order and the invoice are the same row with a status. Approval is per job. A comeback is a new order of type `warranty` or `goodwill` pointing at the order it repeats. A void keeps its lines and totals.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `repair_order_id` | integer | no | key |
| `number` | text | no | the document number as printed (en a running number; ru «ЗН1-004217», the shop's digit then a running number) |
| `location_id` | integer | no | the shop |
| `customer_id` | integer | no | the customer the order was opened for |
| `vehicle_id` | integer | no | the car |
| `advisor_id` | integer | no | the advisor who wrote the order |
| `order_type` | text | no | `customer_pay` = the customer pays; `warranty` = a repeat of earlier work redone free under warranty; `goodwill` = a repeat redone free outside the warranty's terms; `internal` = the shop's own work (allowed by the system; not used in v1) |
| `status` | text | no | the order's status now (D2): `estimate` = written, nothing approved; `approved` = at least one job approved, not started; `in_progress` = being worked; `waiting_parts` = stopped for parts; `waiting_sublet` = work out at a subcontractor; `completed` = work done, not invoiced; `invoiced` = invoiced, money due (an account order on a statement stays here until the statement is paid); `paid` = settled (a warranty or goodwill order reaches `paid` with no payment: its total is 0); `declined` = an estimate nobody approved, or one that expired; `void` = cancelled, keeps its totals. An open order is one whose status is not `invoiced`, `paid`, `void` or `declined` |
| `comeback_of_id` | integer | yes | the order this one repeats; set only on warranty and goodwill orders that are comebacks |
| `opened_at` | timestamp | no | when the order (or estimate) was written: the document's date |
| `promised_at` | timestamp | yes | when the car was promised to the customer; null if no promise |
| `mileage_in` | integer | yes | odometer at check-in (miles en, km ru) |
| `mileage_out` | integer | yes | odometer when the car left; null until it leaves |
| `complaint` | text | yes | what the customer said, as written at the counter. Text (cfg) |
| `purchase_order_number` | text | yes | the company customer's own order or request number ("ND-60418", «247/10») |
| `labor_total` | numeric(12,2) | no | labour of the order's live jobs, before discount (D1) |
| `parts_total` | numeric(12,2) | no | parts of the live jobs (D1) |
| `sublet_total` | numeric(12,2) | no | sublet prices of the live jobs (D1) |
| `fees_total` | numeric(12,2) | no | shop supplies and other fees (D1) |
| `discount_total` | numeric(12,2) | no | discounts, the sum of the labour lines' discounts (D1). On a warranty or goodwill order it is the whole amount, `labor_total + parts_total + sublet_total + fees_total`: the free work keeps its prices on the lines and is given away here |
| `tax_rate` | numeric(5,3) | no | the tax rate in per cent applied to this order: English configuration 9.250 at `main` and `east`, 9.750 at `west`; Russian configuration 0 before 2025-01-01 and 5.000 from that date (the order's date) |
| `tax_included` | boolean | no | how tax sits in the line prices: `false` = lines are before tax and the sales tax `tax_total` is added to them (every English order); `true` = lines are the table prices and the VAT is inside them, `tax_total` being the part of the total that is VAT (every Russian order, private customers, small businesses and the accounts billed on terms alike; on an order before 2025-01-01 the rate is 0 and so is `tax_total`). The before-VAT amount of a Russian order is `total / 1.05` to the kopeck; an account's invoice and УПД print the before-VAT amount, the VAT and the total as three figures |
| `tax_total` | numeric(12,2) | no | the tax on the order (D1): en the sales tax added; ru the VAT inside the total, `total - round(total / 1.05, 2)` |
| `total` | numeric(12,2) | no | what the customer owes: `labor_total + parts_total + sublet_total + fees_total - discount_total`, plus `tax_total` when `tax_included` is false (D1); 0 on a warranty or goodwill order. The amount before tax is always `total - tax_total` |
| `discount_reason` | text | yes | the written reason for a discount. Text (cfg) |
| `discount_approved_by_id` | integer | yes | who approved the discount; required for a discount above 10 % of the bill before tax from the next full open day after F1's firing; empty before the rule |
| `statement_id` | integer | yes | the statement (en) or invoice (ru) that bills this order to a company account; null for orders paid at the counter |
| `voided_at` | timestamp | yes | when it was voided (D3) |
| `voided_by_id` | integer | yes | who voided it |
| `void_reason` | text | yes | the reason given. Text (cfg) |

Traps: a void keeps its totals (M9); a warranty or goodwill order keeps its lines at their prices, holds the whole amount in `discount_total`, has `total` 0, status `paid` and no payment row: it is not revenue and its "discount" is not a discount; declined estimates carry their estimate's value; an open order is one not `invoiced`, `paid`, `void` or `declined`; an account order sits at `invoiced` until its statement is paid; the three never-closed orders (M4); wrong mileages (M3); a car on the wrong customer (M8); the walk-in record (M5); `opened_at` is in the shop's own clock (M10); the discount percentage is `discount_total` over the bill before the discount, `labor_total + parts_total + sublet_total + fees_total`; both carry the tax when `tax_included`, so the share needs no conversion; totals include only approved jobs once any job is approved.

## order_status_history

One row is a change of an order's status, with its time. The order's current status is its last row.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_status_history_id` | integer | no | key |
| `repair_order_id` | integer | no | the order |
| `status` | text | no | the status entered, the same values as `repair_order.status`: `estimate`, `approved`, `in_progress`, `waiting_parts`, `waiting_sublet`, `completed`, `invoiced`, `paid`, `declined`, `void` |
| `changed_at` | timestamp | no | when (shop clock) |

Traps: an order can enter `waiting_parts` several times; a re-issued bill shows `invoiced`, then `completed` again, then `invoiced` again; time in a status is the gap to the next row, and the last row runs to T.

## order_job

One row is one job on an order: what it is, whether the customer approved or declined it, how and when, and whether a declined job was deferred.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_job_id` | integer | no | key |
| `repair_order_id` | integer | no | the order |
| `canned_job_id` | integer | no | the catalogue job |
| `description` | text | no | the job as printed on the order (the catalogue name, sometimes with a note). Text (cfg) |
| `status` | text | no | `pending` = waiting for the customer; `approved` = the customer said yes; `declined` = the customer said no |
| `approval_method` | text | yes | how the decision was given: `counter` = in person; `phone` = on a call; `link` = from the estimate link sent by text or e-mail; `message` = in a chat or messenger; null while pending |
| `decided_at` | timestamp | yes | when the customer approved or declined; null while pending |
| `authorized_by` | text | yes | the customer-side person who decided (a fleet contact, a driver, a relative). Text (cfg) |
| `approved_amount` | numeric(12,2) | yes | the amount the customer agreed to when approving (the estimate); may differ from the lines when a price changed after |
| `deferred` | boolean | no | true = declined but still needed: a reminder was raised |

Traps: whether a job was recommended by the shop is told by an `inspection_item` pointing at it, not by this table; declined jobs keep their labour and part lines, which the order's totals leave out; the courtesy inspection is a free job with no lines.

## order_labor

One row is a labour line: hours sold, the rate, the technician, the discount. Sold hours, not clocked hours (those are `time_entry`).

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_labor_id` | integer | no | key |
| `order_job_id` | integer | no | the job |
| `technician_id` | integer | yes | who did the work; null on a job that was declined or not yet assigned |
| `hours` | numeric(5,2) | no | hours sold |
| `rate` | numeric(10,2) | no | the hour the line was priced at (the class's hour in force on the order's date; gross of tax when the order's `tax_included` is true) |
| `amount` | numeric(12,2) | no | the line's labour before discount: `hours * rate` for hourly jobs, the menu price for menu jobs (D7) |
| `discount` | numeric(12,2) | no | discount given on this line |

Traps: lines of declined jobs are not sold hours; a comeback's lines carry hours the customer does not pay for; `rate` is not always today's `labor_rate`.

## order_part

One row is a part line: a catalogue part or one typed by hand, its brand, quantity, cost and price, and the vendor it came from.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_part_id` | integer | no | key |
| `order_job_id` | integer | no | the job |
| `part_id` | integer | yes | the catalogue part; null when typed by hand (M7) |
| `description` | text | no | the part as printed. Text (cfg) |
| `brand` | text | yes | the brand (D6); may be empty on a typed line |
| `quantity` | numeric(8,2) | no | quantity in the part's unit |
| `unit_cost` | numeric(12,2) | no | what the shop paid, per unit |
| `unit_price` | numeric(12,2) | no | what the customer is charged, per unit (company class 10 % under list; gross of tax when `tax_included`) |
| `vendor_id` | integer | yes | the supplier it was bought from; null when it came from stock bought earlier |

Traps: typed lines have no part number and no part to join to (M7); the brand is the column that tells a cheap pad from a good one; part lines of declined jobs are not sales.

## order_sublet

One row is work sent to a subcontractor: what, to whom, its cost and its price.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_sublet_id` | integer | no | key |
| `order_job_id` | integer | no | the job |
| `vendor_id` | integer | no | the subcontractor |
| `description` | text | no | the work sent out. Text (cfg) |
| `cost` | numeric(12,2) | no | what the subcontractor charges the shop |
| `price` | numeric(12,2) | no | what the customer is charged; 0 when the shop bears it (a tow at the shop's cost) |

## order_fee

One row is a charge on an order that is neither labour nor a part: shop supplies, tyre disposal, tyre storage.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `order_fee_id` | integer | no | key |
| `repair_order_id` | integer | no | the order |
| `kind` | text | no | `shop_supplies` = a share of hourly labour up to a cap (5 % up to 35 USD; 3 % up to 500 RUB); `tyre_disposal` = disposal of old tyres (en with the state fee); `tyre_storage` = a season's storage of a set |
| `description` | text | no | as printed. Text (cfg) |
| `amount` | numeric(12,2) | no | the charge |

## inspection

One row is the inspection of the car on an order: the courtesy inspection most cars get, a brake inspection or a pre-purchase inspection.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `inspection_id` | integer | no | key |
| `repair_order_id` | integer | no | the order (one inspection per order) |
| `technician_id` | integer | no | who inspected |
| `completed_at` | timestamp | no | when it was closed and went to the advisor |

## inspection_item

One row is one checked component: good, watch or bad, and the job recommended from it.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `inspection_item_id` | integer | no | key |
| `inspection_id` | integer | no | the inspection |
| `component` | text | no | what was checked, from the shop's checklist ("Front brake pads", «Передние колодки»). Text (cfg) |
| `result` | text | no | `good` = nothing to do; `watch` = worn but safe, measured; `bad` = needs doing now |
| `measurement` | text | yes | the reading as written ("4 mm", "3/32 in"). The shop's checklist asks for one on every `bad` finding; the system does not enforce it, and some `bad` rows lack it. Text (cfg) |
| `has_photo` | boolean | no | a photo is attached. Asked for on every `bad` finding, not enforced |
| `order_job_id` | integer | yes | the job raised from this finding; null when no job was raised |

Traps: "recommended work" is the jobs these rows point at; sold share = approved over approved plus declined among them, never over every job; whether a `bad` finding was documented (a measurement and a photo) differs by shop.

## time_entry

One row is a technician's clocked time on a job (job time, not attendance: attendance is in the product).

| Column | Type | Null | Meaning |
|---|---|---|---|
| `time_entry_id` | integer | no | key |
| `technician_id` | integer | no | who clocked |
| `order_job_id` | integer | no | the job |
| `clock_in` | timestamp | no | start (shop clock) |
| `clock_out` | timestamp | yes | end; null while the clock still runs at T |

Traps: clocked hours are not sold hours; efficiency is sold over clocked for the same jobs; a job can have several entries.

## statement

One row is a bill to a company account billed on terms. English configuration: a monthly statement of the month before's invoices. Russian configuration: one row per closed order of an account, its invoice (счёт) with its closing document (УПД), printing the before-VAT amount, the VAT and the total; once, one invoice covers three orders together. The quarterly reconciliation sent to an account is not a row.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `statement_id` | integer | no | key |
| `customer_id` | integer | no | the account |
| `number` | text | no | the document number as printed |
| `issued_on` | date | no | the day it was issued |
| `due_on` | date | no | `issued_on` plus the account's terms |
| `total` | numeric(12,2) | no | the sum of its orders' totals (D4); in the Russian configuration VAT is inside it, as in the orders' totals |
| `status` | text | no | `open` = prepared, not sent; `sent` = sent, not yet due or due today; `paid` = settled; `overdue` = past `due_on` and unpaid |
| `dispute_note` | text | yes | the customer disputes the bill or a line on it, with what; null = no dispute. Text (cfg) |

Traps: days to pay are the payment's date minus `issued_on`; a disputed bill is still `overdue`; in the Russian configuration a statement is one order's invoice, so "statements per month" mean different things in the two builds.

## payment

One row is money in or back: amount, method, the order or the statement it settles, deposit or refund, who took it. A payment settles one order or one statement, never both.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `payment_id` | integer | no | key |
| `repair_order_id` | integer | yes | the order it settles; null when it settles a statement |
| `statement_id` | integer | yes | the statement it settles; null when it settles an order |
| `kind` | text | no | `payment` = money in against the order or statement; `deposit` = money in before the work (special-order parts, rebuilds); `refund` = money given back (the amount is positive) |
| `method` | text | no | `cash`; `card`; `check` = a cheque; `bank_transfer` = a transfer or ACH; `fast_payment` = the Russian fast payment system (СБП) |
| `amount` | numeric(12,2) | no | always positive, whatever the kind |
| `received_at` | timestamp | no | when (shop clock; the office's for statement payments) |
| `taken_by_id` | integer | yes | the employee who took it; null for transfers |
| `reference` | text | yes | cheque number, transfer reference or receipt number |

Traps: one statement payment settles every order of its statement (M6: in the English configuration every statement payment covers several orders; in the Russian one an invoice holds one order, so this happens once, on the invoice for three orders); an order can have a deposit and a payment, or two payments (M6); a refund is positive and must be subtracted (M6); a voided order can still have a payment row; a warranty or goodwill order has no payment.

## cash_drawer_close

One row is the till count at the end of a shop's day: what the system expected, what was counted, the difference.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `cash_drawer_close_id` | integer | no | key |
| `location_id` | integer | no | the shop |
| `business_date` | date | no | the shop's day |
| `closed_by_id` | integer | no | the advisor who closed the till |
| `second_counter_id` | integer | yes | the second person who counted; set at `west` since the discount rule |
| `float_amount` | numeric(12,2) | no | the float left in the drawer, not part of the day's cash |
| `expected_cash` | numeric(12,2) | no | the day's cash the system expects from the cash payments and refunds, float excluded |
| `counted_cash` | numeric(12,2) | no | the cash counted, float excluded |
| `difference` | numeric(12,2) | no | `counted_cash - expected_cash` (D5); negative = short |
| `note` | text | yes | the reason written on the count sheet when over the reporting limit. Text (cfg) |

Hidden below middle rank: every money column and the note.

## purchase_order

One row is an order to a vendor: for one repair order (a special order) or for stock, with ordered, promised and received times.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `purchase_order_id` | integer | no | key |
| `number` | text | no | the shop's number for it |
| `location_id` | integer | no | the shop it is for |
| `vendor_id` | integer | no | the vendor |
| `repair_order_id` | integer | yes | the repair order the parts are for; null for stock |
| `status` | text | no | `ordered` = placed, nothing received; `partial` = some lines received; `received` = all received; `cancelled` = called off (a vendor who cannot deliver is replaced by a new purchase order) |
| `ordered_at` | timestamp | no | when placed |
| `promised_at` | timestamp | no | the delivery the vendor promised |
| `received_at` | timestamp | yes | when the last line arrived; null until then |

Traps: on time = received on the promised day; cancelled orders are not late deliveries; a car whose part was promised twice has two purchase orders.

## purchase_order_line

One row is a part on a purchase order, with the quantity ordered and received.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `purchase_order_line_id` | integer | no | key |
| `purchase_order_id` | integer | no | the purchase order |
| `part_id` | integer | yes | the catalogue part; null for a part not in the catalogue |
| `description` | text | no | as ordered. Text (cfg) |
| `quantity_ordered` | numeric(8,2) | no | quantity ordered |
| `quantity_received` | numeric(8,2) | no | quantity received so far |
| `unit_cost` | numeric(12,2) | no | price agreed per unit |

## stock_level

One row is what a shop holds of a part now.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `stock_level_id` | integer | no | key |
| `location_id` | integer | no | the shop |
| `part_id` | integer | no | the part |
| `quantity_on_hand` | numeric(10,2) | no | on the shelf at T (D8) |

Traps: only stocked parts have a row; a shop with no row for a part holds none.

## stock_movement

One row is a change in a shop's stock: a receipt, an issue to an order, a transfer between shops, a return to the vendor, an adjustment.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `stock_movement_id` | integer | no | key |
| `location_id` | integer | no | the shop whose stock changed |
| `part_id` | integer | no | the part |
| `kind` | text | no | `receipt` = in from a purchase order; `issue` = out to an order line (or, wrongly, to none); `transfer_in` / `transfer_out` = between shops, one row at each; `vendor_return` = back to the vendor; `adjustment` = a count correction or a write-off |
| `quantity` | numeric(10,2) | no | signed: positive in, negative out |
| `unit_cost` | numeric(12,2) | no | cost per unit at the time |
| `moved_at` | timestamp | no | when (shop clock) |
| `employee_id` | integer | yes | who recorded it |
| `order_part_id` | integer | yes | the order line an issue went to; null on an issue means parts left with no sale |
| `purchase_order_line_id` | integer | yes | the purchase-order line a receipt came from |
| `part_return_id` | integer | yes | the return a vendor return belongs to |
| `note` | text | yes | the reason for an adjustment. Text (cfg) |

Traps: an issue with no order line is stock that left without a sale; a transfer appears twice, once per shop.

## part_return

One row is a part sent back to a vendor and whether it was credited.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `part_return_id` | integer | no | key |
| `purchase_order_line_id` | integer | no | the line the part was bought on |
| `quantity` | numeric(8,2) | no | quantity sent back |
| `amount` | numeric(12,2) | no | the credit asked for |
| `reason` | text | no | why. Text (cfg) |
| `returned_on` | date | no | the day it left |
| `status` | text | no | `sent` = sent, no answer yet; `credited` = the vendor credited it; `rejected` = the vendor refused |
| `credited_on` | date | yes | when credited |

## service_reminder

One row is deferred work or due maintenance to remind a customer of, and what became of it.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `service_reminder_id` | integer | no | key |
| `customer_id` | integer | no | whom to remind |
| `vehicle_id` | integer | no | the car |
| `order_job_id` | integer | yes | the declined, deferred job it comes from; null for maintenance due |
| `kind` | text | no | `deferred_work` = a job the customer declined and still needs; `maintenance_due` = the next oil service by mileage |
| `description` | text | no | what to remind of. Text (cfg) |
| `due_on` | date | yes | when it is due by date; null when due by mileage only |
| `due_mileage` | integer | yes | the odometer at which it is due; null when due by date only |
| `status` | text | no | `pending` = not yet sent; `sent` = the reminder went out; `done` = the work was done on a later order; `dismissed` = closed without the work |
| `sent_on` | date | yes | when it was sent |
| `done_repair_order_id` | integer | yes | the later order that did the work |
| `created_on` | date | no | when it was raised |

Traps: a customer who asked to book in a chat is still `sent` here until an order or appointment exists.
