from kbb import *

page('parts/suppliers.md', 'Suppliers', 'J', 9,
 'Who we buy from, what each delivers, when to order, and the parts manager\'s own notes on each.',
 f"""*{S(9,'full')}, parts · Last reviewed {D('T-3mo')}*

Chattanooga shops. Nashville is at the bottom.

| Supplier | For | Delivers to | Order by | Arrives | Terms | Phone |
|---|---|---|---|---|---|---|
| {V('V1')} | General line, domestic and import | East Main, Bonny Oaks | 8:00 / 11:00 / 2:00 | 8:30 / 11:30 / 2:30 run, about 45 minutes | 30 days | {V('V1','phone')} |
| {V('V3')} | Original-brand parts, Asian and European | All three shops | 10:00 for stocked lines | Same afternoon in Chattanooga if stocked. Otherwise next morning. Nashville always next morning | 30 days | {V('V3','phone')} |
| {V('V4')} | Batteries, starters, alternators, A/C parts, refrigerant | East Main, Bonny Oaks | 10:30 | Noon run | 30 days | {V('V4','phone')} |
| {V('V5')} | Tires, weights, valves | All three shops | 4:00 the day before | Chattanooga: every morning. Nashville: Tuesday and Friday only | 30 days | {V('V5','phone')} |

## Notes

- {V('V1')}: first call for anything. On the truck they said, nine times in ten. When they are out of a part they say so.
- {V('V3')}: dearer. Use for sensors, coils, timing kits, anything where the cheap one comes back. Aisin and Denso come from here.
- {V('V4')}: one run a day. Miss 10:30 and it is tomorrow.
- {V('V5')}: tires for Nashville come twice a week. Do not tell a Nashville customer "tomorrow" on a Wednesday.

## Nashville

Charlotte Pike orders its own parts. Its main supplier is {V('V2')}, {V('V2','phone')}, two runs a day, 15-day terms. I do not order for Nashville and I do not see their orders.

{V('V2')} says today and means tomorrow. Do not give a customer a time off their word. Their house-brand brake pads: see [Brake pads we fit](brake-pads-we-fit.md).

Moving Charlotte Pike onto {V('V1')} has been asked for. It is with {S(22)}.

Outside work (transmissions, glass, towing): [Sublet work](sublet-work.md).
""",
 serves=['S6', 'challenge:fact-in-table', 'challenge:kb-does-not-say', 'challenge:combine-kb-and-data'],
 facts=['V1 Sequoyah Parts Supply: general line; main and east; three runs (order by 8:00, 11:00, 14:00; runs at 8:30, 11:30, 14:30); 30 days; (423) 555-0197.',
        'V3 Ridge & Valley Import Parts: OE-brand Asian and European; all three shops; order by 10:00 for same-afternoon stocked lines in Chattanooga, else next morning; Nashville next morning; 30 days; (423) 555-0158.',
        'V4 Hiwassee Battery & Electric: batteries, electrical, A/C; main and east; order by 10:30 for the noon run; 30 days; (423) 555-0165.',
        'V5 Tellico Tire Distributors: tyres; order by 16:00 the day before; Chattanooga daily, Nashville Tuesday and Friday; 30 days; (423) 555-0177.',
        'V2 Harpeth Valley Parts Supply: west only; two runs a day; 15 days; (615) 555-0123; unreliable in the parts manager\'s words (S6: 62 % on the promised day against 93 % for V1; the page gives no percentages).',
        'Slot 9 does not order for Nashville. The supplier change for west "is with slot 22" (S6: the board task three weeks overdue).',
        'Not stated: who supplies batteries and A/C parts to Charlotte Pike (V4 serves main and east only).'],
 new=['Order-by and run times for V1, V3, V4, V5; Nashville tyre days Tuesday and Friday (vendors.json says "twice a week"). The ERP purchase orders should show these rhythms.'],
 rev=[(4, 'T-3mo', 'Marcus\'s update: Nashville section rewritten, the sentence about moving Charlotte Pike to Sequoyah added (Marcus is junior rank; published by slot 4); message: "Marcus\'s notes on Nashville."')],
 ru=['Russian suppliers from vendors.json ru (eight, same roles); delivery in Russian cities is by the supplier\'s courier several times a day or pickup from a warehouse; terms in days as in the file. The cheap pad brand is BREMHOF in the catalogue (Ronnex in vendors.json: see the contradiction note).'])

page('parts/ordering-parts.md', 'Ordering parts for a job', 'J', 9,
 'How a part gets from the order to the bay, and when an advisor may promise a time.',
 f"""*{S(9,'full')}, parts*

1. The part goes on the order from the catalogue: number, brand, tier. Not "front pads".
2. I order it. East Main: tell me or flag the order. Bonny Oaks: flag the order; I see it. If I am off, {S(5)} orders for East Main and {S(16)} for Bonny Oaks.
3. VIN first. Always. Half the wrong parts in this building were ordered off a year and a model.
4. I put the arrival time on the order when the supplier confirms it. Until that time is on the order, **there is no time**.
5. The part is "here" when it is on the shelf with the order number on it. Not when the truck is "on its way".
6. Bonny Oaks gets its parts direct from the supplier. Anything that has to move between the two shops goes on my 1:00 run.

## What the counter may promise

- Part on the shelf, technician free: a time today.
- Part confirmed for a run: a time after that run plus the job hours plus an hour.
- Part not confirmed: "I will call you by 2:00 with a time." Then call.
- Never "same day" because the job is only three hours.

## Special orders

Anything that is not a stocked line at the supplier. Takes 2 to 5 working days. Over $300 to the customer needs a deposit first: [Deposits](../policies/deposits.md). Tell the customer it cannot go back.

Cut-off times: [Suppliers](suppliers.md).
""",
 serves=['S8', 'S6', 'challenge:three-page-procedure'],
 facts=['Parts go on the order from the catalogue with number, brand and tier.',
        'Slot 9 orders for main and east; cover: slot 5 at main, slot 16 at east.',
        'VIN before ordering.',
        'Arrival time is on the order only when the supplier confirmed; a part is "here" when shelved with the order number.',
        'Inter-shop transfers go on the parts manager\'s 13:00 run (ERP stock_movement: transfers).',
        'Promise rules: on the shelf = a time today; confirmed for a run = that run plus job hours plus one hour; unconfirmed = a call by 14:00; never "same day" on job length alone (S8: slot 7 promised a 3.2-hour job the same day).',
        'Special orders take 2 to 5 working days; over 300 USD needs a deposit.'],
 new=['The 13:00 transfer run; the "run plus hours plus one hour" promise rule; special orders 2 to 5 working days.'],
 ru=['Russian: запчасти под заказ often take 1 to 14 days; customers frequently source parts themselves. Promise rule the same.'])

page('parts/returns-and-cores.md', 'Returns and cores', 'J', 9,
 'What can go back to a supplier, by when, and how cores work.',
 f"""*{S(9,'full')}, parts · Last reviewed {D('T-11mo')}*

## Returns

| Part | Goes back? | By when |
|---|---|---|
| Stocked line, unopened, clean box | Yes, full credit | 30 days |
| Opened but not fitted | Usually. Supplier's call | 30 days |
| Electrical part once fitted (sensor, module, coil, alternator) | No | |
| Special order | Sometimes, less up to 20 % | Ask before ordering |
| Fluids, cut hoses, anything greasy | No | |
| Defective (warranty) | Yes, with our order number and the fault written on the tag | Supplier's warranty period |

A part ordered for a job that did not happen comes back to the cage the same day with the order number on the box. Not on a bench, not in a bay. Parts on benches turn into parts nobody can return.

## Cores

Rebuilt parts (alternators, starters, calipers, steering racks, A/C compressors) carry a core charge until the old one goes back.

- Old part in the new part's box, drained, same day.
- Core goes back within 30 days or we eat the charge.
- The customer is not billed a core charge when the old part stays with us. If the customer wants the old part, they pay the core charge. Say so before the job.

Credits are checked against the supplier statements by the office at month end.
""",
 serves=['challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Return table: stocked unopened 30 days full credit; opened unfitted usually, 30 days; fitted electrical parts never; special orders less up to 20 %; fluids and cut or greasy parts never; defective parts under the supplier\'s warranty with the order number and fault on the tag.',
        'Unused parts return to the cage the same day with the order number (ERP part_return, stock_movement).',
        'Cores: reman alternators, starters, calipers, racks, compressors; old part back in the box, drained, same day; returned within 30 days; customer pays the core charge only if keeping the old part.',
        'Supplier credits are checked at month end by the office.',
        'Core charge amounts are not stated (planted gap; the catalogue has none).'],
 new=['30-day return and core windows; 20 % restocking ceiling (same as policies/deposits.md).'],
 ru=['Russian: возврат запчастей supplier by supplier; electrical parts non-returnable as well; cores (обменный фонд) are rare except for racks and turbochargers.'])

page('parts/stock-we-keep.md', 'Stock we keep', 'J', 9,
 'What is on the shelf at the home shops, and how stock is counted.',
 f"""*{S(9,'full')}, parts · Last reviewed {D('T-6mo')}*

On the shelf at East Main and Bonny Oaks, always:

- Bulk oil: 0W-20 and 5W-30 full synthetic, synthetic blend. Quarts of the premium oil.
- Oil filters for the twenty fitments we see most. Air and cabin filters for the top ten.
- Wiper blades, common bulbs (H11, 9005, 9006, 3157, 7443).
- Batteries: groups 24F, 35, 51R, 65 and H6.
- Brake pads, standard line, for the twelve fitments we see most. Rotors come on the next run.
- Brake fluid DOT 3, coolant (Asian pink, Asian blue, orange, universal), ATF in the four common types, 75W-90 gear oil.
- R-134a at both shops. **R-1234yf at East Main only.** A newer car that needs an A/C recharge at Bonny Oaks either goes to East Main or waits for a bottle on the 1:00 run.
- Tire repair units, valve stems, wheel weights.

Everything else comes on a run. That is on purpose: a part on our shelf is our money sitting still.

Charlotte Pike keeps its own stock and its own count.

## Counting

- I spot-count ten lines a week.
- **Full stocktake twice a year.** All three shops close at noon that day and everybody counts: [Stocktake day](../how-to/stocktake-day.md).
- Something used and not on an order is the reason counts are wrong. If you take it off the shelf, it goes on an order: a customer's, or the shop's own.

Fluid quantities by vehicle: [Fluids and capacities](fluids-and-capacities.md).
""",
 serves=['S13', 'challenge:kb-does-not-say', 'challenge:combine-policy-and-price'],
 facts=['Stocked lines listed for main and east; R-1234yf is stocked at East Main only.',
        'Battery groups 24F, 35, 51R, 65, H6; bulbs H11, 9005, 9006, 3157, 7443.',
        'Weekly spot count of ten lines; full stocktake twice a year with all shops closed from noon (S13).',
        'Anything taken from the shelf goes on an order (customer or internal; ERP order type internal).',
        'Charlotte Pike keeps its own stock; what it keeps is not stated.'],
 new=['R-1234yf at East Main only. Reason: gives a question that joins this page to the A/C service page ("can Bonny Oaks recharge a 2019 CR-V today?"). ERP stock_level should show no R-1234yf at east or west.'],
 ru=['Stocked lines the Russian shop keeps: масла на розлив, фильтры, колодки ходовых моделей, АКБ 60 and 75 А·ч, антифриз G11/G12, грузики, вентили; seasonal: bags for tyre storage.'])

page('parts/parts-tiers-and-brands.md', 'Parts tiers and brands', 'J', 9,
 'The three tiers and which brand we quote in each, by line.',
 f"""*{S(9,'full')}, parts*

Three tiers. Quote **standard**. Offer premium when the customer keeps cars a long time. Economy when they ask for cheaper, not before.

| Line | Economy | Standard | Premium |
|---|---|---|---|
| Brake pads | ACDelco Silver | Wagner ThermoQuiet | Akebono ProACT |
| Rotors | Centric C-TEK | Bosch QuietCast | Centric Premium |
| Struts and shocks | FCS, Gabriel | Monroe | KYB |
| Chassis (links, ball joints, tie rods, arms) | Mevotech | Moog | Original (Toyota Genuine, Motorcraft) |
| Filters | ECOGARD | WIX | Original |
| Belts, timing kits, water pumps | Dayco, GMB | Gates | Aisin |
| Plugs, coils, sensors | Autolite, Delphi, Bosch | NGK / NTK, Standard Motor Products | Denso |
| Batteries | Interstate MT | Interstate MTP | Interstate MTX (AGM) |
| Engine oil | Synthetic blend (bulk) | Full synthetic (bulk) | Mobil 1 Extended Performance |
| Tires | Milestar | Hankook | Michelin |

Some jobs have one option only: fluids, refrigerant, the drum hardware kit.

Rules:

- The tier is per job, not per order. Premium pads and economy wipers on one bill is fine.
- Do not mix tiers inside an axle or a pair.
- Original parts on anything electronic that failed twice with aftermarket.
- Stop-start cars get the AGM battery. Not a choice.
- A brand that is not in this table is not one we chose. If a supplier substitutes, call me before it is fitted.

Prices by tier are on the [price list](../prices/price-list.md).
""",
 serves=['S6', 'challenge:fact-in-table', 'challenge:customer-terms'],
 facts=['Default quote is the standard tier; premium offered to long-term keepers; economy on request.',
        'Brand table by line and tier, taken from the catalogue\'s brands and part options (pads ACDelco Silver / Wagner ThermoQuiet / Akebono ProACT; rotors Centric C-TEK / Bosch QuietCast / Centric Premium; struts FCS, Gabriel / Monroe / KYB; chassis Mevotech / Moog / original; filters ECOGARD / WIX / original; belts and kits Dayco, GMB / Gates / Aisin; ignition and sensors Autolite, Delphi, Bosch / NGK-NTK, Standard Motor Products / Denso; batteries Interstate MT / MTP / MTX; oil blend / full synthetic / Mobil 1; tyres Milestar / Hankook / Michelin).',
        'Tier is per job; no mixing inside an axle or pair; stop-start cars take AGM.',
        'A brand not in the table was not chosen: substitution needs a call to slot 9 (the cheap Nashville pad is not in the table).'],
 ru=['Russian tiers and brands from catalogue ru (for example BIG Filter / MANN / original; Лукойл Люкс / Genesis / Shell). Mark-ups differ and are on the management page.'])

page('parts/brake-pads-we-fit.md', 'Brake pads we fit', 'J', 9,
 'The pad lines by tier and the parts manager\'s warning about the Nashville supplier\'s house brand (S6).',
 f"""*{S(9,'full')}, parts · Last reviewed {D('T-3mo')}*

Front pad set, the common Camry fitment, list price:

| Tier | Pad | Set |
|---|---|---:|
| Premium | Akebono ProACT | {part('front_brake_pads',0,'premium')} |
| Standard | Wagner ThermoQuiet | {part('front_brake_pads',0,'standard')} |
| Economy | ACDelco Silver | {part('front_brake_pads',0,'economy')} |

All three are ceramic, come with hardware or we add it, and I have no comeback problem with any of them.

## Calder ValueStop

{V('V2')}'s house line. $39.00 a set for the same fitment. **Not ordered and not fitted at East Main or Bonny Oaks.**

Charlotte Pike fits them, because they are what {V('V2')} sends when the order says "economy pads". They are hard, they squeal, and the ones I have seen back were glazed or worn out at half the miles.

If a customer in Nashville wants the cheapest pad, the cheapest pad we should be fitting is the ACDelco. It costs the customer $21.00 more a set.

This needs deciding above me.
""",
 serves=['S6', 'S1', 'challenge:combine-kb-and-data', 'challenge:fact-in-table'],
 facts=['Front pad set list prices by tier from catalogue front_brake_pads (reference fitment FMSI D1222): premium 100.00, standard 86.36, economy 60.00.',
        'The cheap pad: Calder ValueStop, 39.00 a set (catalogue option marked story S6), the house line of vendor V2; fitted at west only.',
        'Economy ACDelco costs 21.00 more a set than the cheap pad (60.00 - 39.00).',
        'The parts manager\'s opinion: hard, squeal, wear out at half the miles (S6: they come back four times as often; the page gives no rate).',
        '"This needs deciding above me": nothing has been decided (S6).',
        'BRAND NAME CONFLICT: catalogue.json calls the pad Calder ValueStop; vendors.json calls the house brand RoadCrest. The page follows the catalogue.'],
 new=['The 21.00 difference is arithmetic on catalogue prices, not a new price.'],
 created=(4, 'T-3mo'),
 ru=['BREMHOF in catalogue ru at 1 250 RUB a set (Ronnex in vendors.json ru). Russian tier brands for pads from the catalogue.'])

page('parts/sublet-work.md', 'Sublet work', 'J', 9,
 'Work we send out or bring in: transmission rebuilds, glass, towing. How it is ordered and billed.',
 f"""*{S(9,'full')}, parts · Last reviewed {D('T-9mo')}*

Sublet is work somebody else does and we bill. It goes on the order as a sublet line: their work, our price. Never as a part.

## Transmissions: {V('V6')}

- {V('V6','phone')}. East Main and Bonny Oaks.
- We remove the transmission. They collect it, rebuild it and bring it back. **Five working days** door to door is normal; do not promise less.
- Customer price for the rebuild is on the [price list](../prices/price-list.md) with our removal and refitting labour. Deposit before it leaves: [Deposits](../policies/deposits.md).
- Their warranty card comes back with the unit. Staple it to the invoice. The customer's cover on the rebuild is what that card says.
- A transmission that only needs fluid is ours: [Transmission fluid service](../services/transmission/transmission-fluid-service.md).

## Glass: {V('V7')}

- {V('V7','phone')}. They come to East Main and Bonny Oaks. Book them a day ahead; the car stays put for an hour after for the adhesive.
- Cars with a camera behind the windshield need recalibrating. They do it. It adds time; ask them how long when you book.
- We bill what they bill us plus our handling. Get their figure before quoting; there is no list price for glass.

## Towing: {V('V8')}

- {V('V8','phone')}. Chattanooga side only.
- Prices are on the public [Towing](../customers/towing.md) page. The tow goes on the repair order as a sublet line.
- They bill us monthly.

## Nashville

Charlotte Pike makes its own arrangements. Ask {S(22)}.
""",
 serves=['challenge:kb-does-not-say', 'challenge:combine-policy-and-price', 'S6'],
 facts=['Sublet work is billed as a sublet line, never as a part (ERP order_sublet).',
        'V6 Coulter Transmission & Driveline, (423) 555-0134, main and east: rebuild takes five working days door to door; deposit before it leaves; warranty per the card returned with the unit (length not stated anywhere).',
        'V7 Walden Auto Glass, (423) 555-0130, on site at main and east, booked a day ahead; one hour cure; camera recalibration by them; no list price for glass.',
        'V8 Mowbray Towing & Recovery, (423) 555-0139, Chattanooga only; monthly billing; prices on the public towing page.',
        'Nashville\'s sublet partners are not stated.'],
 new=['Five working days for a rebuild; one hour cure for glass. Reason: promise times need a number; the ERP\'s waiting_sublet durations should centre on five working days.'],
 ru=['Russian subcontractors from vendors.json ru (АКПП, стёкла, эвакуатор).'])

page('parts/fluids-and-capacities.md', 'Fluids and capacities', 'J', 9,
 'Pointer page: what fluid types we use and where the per-vehicle quantities are (only in the attached sheet).',
 f"""*{S(9,'full')}, parts*

What goes in is on the cap, the dipstick or the label under the hood. Read it. Wrong fluid is the dearest mistake a lube bay can make.

The quantities and specs for the vehicles we see every week, mostly the company fleets, are in my sheet:

- [Fleet fluid sheet (spreadsheet)](fleet-fluid-sheet.xlsx). The working copy. I update this one.
- [Fleet fluid sheet (printed copy)](fleet-fluid-sheet.pdf). Same sheet, printed for the lube bays.

If the two ever differ, the spreadsheet is right and the print is old.

Rules that are not in the sheet:

- Bill the quarts that went in, rounded up to the half quart. Not the sheet's number if the engine took less.
- CVT fluid is not ATF. Honda, Nissan, Subaru and Toyota CVTs each take their own. If it is not on the shelf, it is not going in.
- Coolant is topped up with the same type and colour. No mixing.
- Brake fluid from a sealed bottle only.
""",
 serves=['challenge:fact-only-in-attachment', 'challenge:unreadable-binary', 'operate:contradiction'],
 facts=['The per-vehicle quantities and specs exist only in the two attachments: fleet-fluid-sheet.xlsx (working copy) and fleet-fluid-sheet.pdf (print).',
        'Product fact: the engine extracts text from PDF, DOCX and PPTX, not from XLSX. The spreadsheet is found by name and cannot be read; the PDF can, with page locators.',
        'If they differ the spreadsheet wins (the PDF is one revision behind on purpose: see en/_binaries.md).',
        'Rules: bill the quarts used rounded up to the half quart; CVT fluid is maker-specific; no mixing coolant; sealed brake fluid only.'],
 new=['Billing rule: quarts used, rounded up to the half quart. The catalogue bills 5 qt on the Camry oil service and 6 qt on the fleet PM, consistent with rounding up.'],
 ru=['Litres. Russian sheet covers the Russian fleets\' models (ГАЗель NEXT, Largus, Solaris etc.).'])
