from kbb import *

page('README.md', 'Brennan Auto Care knowledge base', 'J', 2,
 'Front page for staff: what each folder holds, who owns it, and the two house rules (prices, corrections).',
 f"""*Owner: {S(2,'full')} · Last reviewed {D('@belt_proposal')}*

This is where we keep how Brennan Auto Care works: three shops, one way of doing things. If you learned something the hard way, it belongs here, not in your head.

## Where things are

| Folder | What is in it | Who keeps it |
|---|---|---|
| [customers](customers/README.md) | Answers we give the public. The website assistant quotes these pages word for word, so they are written for customers. It also reads the service pages and the price list. | {S(2)} |
| [services](services/README.md) | What each job is, when a car needs it, what to ask, what customers push back on. | {S(5)} and {S(16)} |
| [prices](prices/price-list.md) | The price list and the labour rates. **The only place a price comes from.** | {S(2)} |
| [policies](policies/README.md) | Discounts, warranty, estimates, deposits, complaints. | {S(2)} |
| [accounts](accounts/company-account-terms.md) | Company accounts: terms, who may approve work, what each fleet expects. | {S(4)} |
| [how-to](how-to/README.md) | How we do the counter jobs: a call, a booking, an estimate, handing a car back, the till. | {S(4)} |
| [parts](parts/suppliers.md) | Suppliers, ordering, returns, what we stock. | {S(9)} |
| [shops](shops/README.md) | Each shop's own pages: hours, who is who, keys and alarms, local habits. | each shop |
| [team](team/who-is-who.md) | Who is who across the company, the staff handbook, first weeks for new people. | {S(2)} |
| [shop-floor](shop-floor/README.md) | For technicians: clocking in, inspections, checks before a car leaves. | {S(8)} |

Office and management pages exist too. You see them if your job needs them.

## Two rules

1. **Quote from the price list.** A price on a service page is there to explain the job. It may be old. The [price list](prices/price-list.md) is never old, because it is the page I change when a price changes.
2. **If a page is wrong, say so the same day.** Lead advisors and above can propose a correction from the page itself; {S(4)}, {S(22)} or I publish it. Everybody else: tell your lead. How: [Using and fixing this knowledge base](how-to/using-this-knowledge-base.md).
""",
 serves=['S12', 'operate:overview'],
 facts=['Ten staff folders are listed with what they hold and who keeps them; office and management folders exist and are rank-limited.',
        'Rule 1: prices are quoted from prices/price-list.md only; a price on a service page may be old.',
        'Rule 2: lead advisors and above (middle rank) can propose a correction; slots 4, 22 and 2 publish; others tell their lead.',
        'The website assistant reads customers/, shop-floor/, services/ and the price list (ledger s12.pages).',
        'kb_overview reads this file as the README of the root for staff; it is hidden from the public reader (seen_from junior on the file).'],
 new=['Folder owners: customers 2; services 5 and 16; prices 2; policies 2; accounts 4; how-to 4; parts 9; team 2; shop-floor 8 (designed, follows the cast biographies).'],
 rev=[(2, '@belt_proposal', 'added the section "Two rules" after the timing-belt complaint (S8); message: "Prices come from the price list. Said it twice now."')],
 ru=['Same structure. The Russian base has the same folders; name the owners by the same slots.'])

page('customers/README.md', 'Customer answers', 'W', 2,
 'Index of the public pages; the README the website assistant gets from kb_overview.',
 f"""Everything in this folder may be told to a customer as written. Prices are before sales tax.

- [Hours and locations](hours-and-locations.md)
- [What we work on, and what we don't](what-we-do.md)
- [Prices for common services](prices-for-common-services.md)
- [Estimates and approvals](estimates-and-approvals.md)
- [Our warranty](warranty.md)
- [Dropping off, waiting, shuttle and pick-up](dropping-off-and-picking-up.md)
- [Paying your bill](payment.md)
- [Towing](towing.md)
- [Bringing your own parts](bringing-your-own-parts.md)
- [If something isn't right](if-something-is-not-right.md)

By problem:

- [Brake noise](brake-noise.md)
- [Check engine light](check-engine-light.md)
- [Air conditioning not cold](air-conditioning.md)
- [Battery and starting trouble](battery.md)
- [Tires, flats and alignment](tires.md)
- [Maintenance by mileage](maintenance-by-mileage.md)
- [Buying a used car: pre-purchase inspection](pre-purchase-inspection.md)
- [Hybrids and electric cars](hybrids-and-electric-cars.md)
- [Company vehicles](company-vehicles.md)

We cannot book an appointment from this page. Ask, and a service advisor will confirm a time with you.
""",
 serves=['S7', 'S13', 'visibility:public'],
 facts=['The folder is public: seen_from worker, which is the rank the customers\' assistant reads at.',
        'All prices on public pages are before sales tax.',
        'The assistant cannot book; an advisor confirms a time (product: the customer assistant can only hand over).'],
 ru=['Same list; add the two tyre-season pages the Russian base needs (seasonal changeover, tyre storage) to "By problem".'])

page('customers/hours-and-locations.md', 'Hours and locations', 'W', 2,
 'The public truth about addresses, phones, hours, holidays and the stocktake afternoon.',
 f"""*Last reviewed {D('@stocktake_notice')}*

## Our three shops

| Shop | Phone | Hours |
|---|---|---|
| East Main (Chattanooga) | (423) 555-0142 | Mon to Fri 7:30 a.m. to 5:30 p.m.; Sat 8:00 a.m. to 1:00 p.m. |
| Bonny Oaks (Chattanooga) | (423) 555-0167 | Mon to Fri 7:30 a.m. to 5:30 p.m. |
| Charlotte Pike (Nashville) | (615) 555-0119 | Mon to Fri 7:30 a.m. to 5:30 p.m. Central time |

- East Main: 2106 East Main St, Chattanooga, TN 37404
- Bonny Oaks: 6340 Bonny Oaks Drive, Chattanooga, TN 37416
- Charlotte Pike: 6399 Charlotte Pike, Nashville, TN 37209

All three are closed on Sunday. Only East Main is open on Saturday. Nashville is on Central time, an hour behind Chattanooga.

## Changed hours

**{D('@stocktake','day')}: all three shops close at 12:00 noon** for our twice-yearly parts count. We open at 7:30 a.m. as usual. A car that is ready that day should be picked up before noon, or the next morning. The key drop stays open.

## Holidays

We are closed on New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day and Christmas Day. When one of them falls on a weekend we close on the nearest weekday.

## After hours

Each shop has a key drop box by the office door. See [Dropping off and picking up](dropping-off-and-picking-up.md). If you call when we are closed, leave a message with your name and number and we call back the next morning we are open.
""",
 serves=['S13', 'S9', 'S7', 'challenge:fact-in-table', 'challenge:near-duplicate-shop-pages'],
 facts=['main: 2106 East Main St, Chattanooga, TN 37404; (423) 555-0142; Mon-Fri 7:30-17:30, Sat 8:00-13:00.',
        'east: 6340 Bonny Oaks Drive, Chattanooga, TN 37416 (ledger geo.address.east); (423) 555-0167; Mon-Fri 7:30-17:30; no Saturday.',
        'west: 6399 Charlotte Pike, Nashville, TN 37209; (615) 555-0119; Mon-Fri 7:30-17:30 Central; no Saturday.',
        'Closed Sundays. Nashville is one hour behind Chattanooga.',
        'Stocktake: on {{@stocktake}} (the Thursday of week W+1) every shop closes at 12:00 noon, opens 7:30 as usual; key drop stays open.',
        'After-hours calls are returned the next open morning.',
        'Closed dates (ledger site.closed_dates): New Year\'s Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Christmas Day; a weekend holiday is observed on the nearest weekday.',
        'The stocktake is the Thursday of week W+1 (ledger site.stocktake); the notice was added on the Monday of week W-1.'],
 new=['The stocktake is called "twice-yearly parts count" for customers.',
      'Shop short names: East Main, Bonny Oaks, Charlotte Pike (ledger geo.short_name).'],
 rev=[(4, '@stocktake_notice', 'added the section "Changed hours" for the stocktake afternoon; message: "Stocktake: all shops close at noon."')],
 ru=['Russian shops are open every day 9:00-20:00 and stay open on public holidays (design 7.2 S13), so the Holidays section says so instead of a list; the stocktake afternoon is the same event.',
     'Kazan is one hour behind Ulyanovsk.'])

page('customers/what-we-do.md', "What we work on, and what we don't", 'W', 2,
 'Scope of work for the public: services offered, and the work we send out or decline.',
 f"""We are a general repair and maintenance shop for cars, SUVs, pickups and work vans.

## What we do

- Maintenance by mileage: oil service, filters, fluids, spark plugs, belts
- Brakes
- Tires, balancing and four-wheel alignment
- Check engine light and electrical diagnosis
- Steering and suspension
- Air conditioning
- Batteries, starters and alternators
- Cooling system, timing belts, leaks, engine mounts, exhaust
- Transmission fluid service, clutches, CV axles
- Inspections before you buy a used car
- Service for company vehicles, on account for approved businesses

## What we send out

- **Transmission rebuilds.** We remove and refit the transmission; a transmission specialist in Chattanooga rebuilds it. One bill, ours.
- **Glass.** A glass company replaces windshields and door glass at our Chattanooga shops by appointment.

## What we don't do

- Body and paint work
- Repairs to the high-voltage system of hybrid and electric cars ([details](hybrids-and-electric-cars.md))
- Diesel engine overhaul
- Motorcycles, RVs and anything over one ton

If you are not sure, ask. If we can't do it we will tell you who can.
""",
 serves=['S7', 'challenge:kb-does-not-say'],
 facts=['Service list mirrors the ten catalogue categories.',
        'Transmission rebuilds are sublet to a transmission specialist in Chattanooga (vendor V6, not named to customers); glass is done on site by a glass company (V7) at the Chattanooga shops only.',
        'Emissions tests and state inspections are deliberately not mentioned anywhere in the base: a planted "the knowledge base does not say".'],
 new=['Not done: body and paint, hybrid/EV high-voltage repairs, diesel engine overhaul, motorcycles, RVs, vehicles over one ton. Reason: the design names the hybrid and EV limit; the rest is the usual line of a general repair shop.'],
 ru=['Add seasonal tyre changeover and tyre storage to the list (a large part of the Russian year). Glass: the Russian vendors file decides whether it is sublet.'])

page('customers/prices-for-common-services.md', 'Prices for common services', 'W', 2,
 'Menu prices a customer may be told without seeing the car; public version of the price list.',
 f"""*Prices in force from {D('@price_rise')}. Before sales tax. For a car or small crossover; larger SUVs, pickups and vans can cost more.*

| Service | Price |
|---|---|
| Full synthetic oil and filter change, up to 5 quarts | {t('oil_service')} |
| Same service with synthetic-blend oil | {t('oil_service','economy')} |
| Tire rotation | {t('tyre_rotation')} |
| Balance four wheels | {t('wheel_balance')} |
| Four-wheel alignment | {t('wheel_alignment')} |
| Flat repair (patch-plug and rebalance) | {t('tyre_repair')} |
| Brake inspection | {t('brake_inspection')} |
| Steering and suspension inspection (noise or vibration) | {t('suspension_diag')} |
| Check engine light diagnosis, first hour | {t('check_engine_diag')} |
| Air-conditioning performance check | {t('ac_performance_check')} |
| Battery, starting and charging test | Free |
| Pre-purchase inspection with road test and written report | {t('pre_purchase_inspection')} |
| Courtesy inspection with any service | Free |

## Repairs

We do not quote a repair we have not looked at. After an inspection you get a written estimate with each job priced separately, and nothing is done until you approve it. See [Estimates and approvals](estimates-and-approvals.md).

## What is added to a bill

- Tennessee sales tax on parts and labour: 9.25 % at East Main and Bonny Oaks, 9.75 % at Charlotte Pike.
- Shop supplies on repair work: 5 % of the labour, never more than $35.00 on one bill. Menu services in the table above carry none.
- New tires carry a disposal fee and the state tire fee.
""",
 serves=['S7', 'S8', 'S12', 'challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['The table repeats the current list (after the rise) for vehicle class car, standard tier unless stated.',
        'Sales tax on parts and labour, 9.25 % at the two Chattanooga shops and 9.75 % at Charlotte Pike (ledger tax.rate.main, .east, .west); shop supplies 5 % of hourly labour, cap 35.00 USD per bill; menu-priced services carry none (catalogue configurations.en).',
        'No repair is quoted unseen: the public page gives menu services only.'],
 rev=[(2, '@price_rise', 'every price replaced with the new list; message: "New prices from today."')],
 ru=['Russian menu: fixed prices exist for tyre fitting, alignment and diagnostics; oil service is priced by the hour there (catalogue ru). VAT 5 % is inside every Russian price and nothing is added on top (ledger tax.ru_price_basis); say so once.',
     'Shop supplies in Russia: 3 % of hourly work, at most 500 RUB.'])

page('customers/brake-noise.md', 'Brake noise', 'W', 6,
 'What a customer with a brake noise is told, what the inspection costs and what a typical repair costs. The page the assistant answers S7 from.',
 f"""*Written by {S(6)} at East Main · Last reviewed {D('T-3mo')}*

A noise from the brakes is worth an inspection. Some noises can wait a week. One cannot.

## What the noise usually means

| What you hear or feel | What it usually is | How soon |
|---|---|---|
| A high squeal that goes away when you press the pedal | The wear indicator: a small metal tab that touches the disc when the pads are nearly gone | This week |
| Grinding, metal on metal | The pads are worn through and the backing plate is on the disc | Now. Every stop is damaging the disc |
| A squeal on the first few stops on a damp morning | Surface rust on the discs. It clears itself | No visit needed |
| The pedal or steering wheel shakes when you brake | Discs worn unevenly | Soon |
| The car pulls to one side when braking | A sticking caliper or a hose | Soon |

## What we do

A [brake inspection](prices-for-common-services.md) is {t('brake_inspection')} and takes about half an hour. We take the wheels off, measure the pads and discs, check the hoses and the fluid, and send you photos with the measurements. Then you decide.

## What a repair costs

For a typical car, front pads and discs together run from {t('front_pads_rotors','economy')} to {t('front_pads_rotors','premium')} before tax, depending on the parts you choose. We tell you the exact figure for your car after the inspection, and we do not replace discs that still measure good.

Brake work carries [our warranty](warranty.md).

## Booking

Tell us the car, what you hear and when you can come. Morning drop-off at 7:30 gets most brake jobs back the same day.
""",
 serves=['S7', 'challenge:customer-terms'],
 facts=['Customers say "discs" or "rotors", "grinding", "squeal"; the trade name on the order is "Replace front brake pads & rotors".',
        'Brake inspection is 0.5 h; wheels off, pads and discs measured, hoses and fluid checked, photos sent.',
        'A typical front pads-and-rotors job on a car costs from the economy to the premium total of the catalogue.',
        'Same-day return for most brake jobs when dropped at 7:30 (hours 1.8).'],
 new=['The five noise rows and their urgency are the trade\'s common advice, chosen for the page.'],
 created=(4, 'T-4mo', 'edit'),
 rev=[(4, 'T-3mo', 'added the table of noises on Maya\'s draft; message: "Maya\'s table. Customers ask this every day."')],
 ru=['Words differ: «скрип», «скрежет», «бьёт руль при торможении»; the job is «Замена передних тормозных дисков и колодок». Prices from the Russian catalogue.',
     'Juniors cannot publish, so the page was published by slot 4 from slot 6\'s draft in both configurations.'])

page('customers/check-engine-light.md', 'Check engine light', 'W', 5,
 'Public advice on a check engine light and what the diagnosis costs.',
 f"""## Steady or flashing

- **Steady light, car drives normally:** safe to drive. Book a diagnosis within a week or two. Check that the gas cap is tight first; a loose cap is the cheapest cause there is.
- **Flashing light, or the engine shakes:** the engine is misfiring. Drive as little as you can and come in. A misfire can ruin the catalytic converter, and that is an expensive part.
- **Light on with the temperature gauge high or the oil light on:** stop the engine. Call us or [have it towed](towing.md).

## What the diagnosis is

Reading the code takes a minute and tells us where to look, not what is wrong. Our diagnosis is one hour of a technician's time, {t('check_engine_diag')}: scan, test the circuit or the part the code points at, and tell you what failed and what it costs to fix. Most faults are found in that hour. If yours needs more time we call you before going on.

The diagnosis fee is charged whether or not you go ahead with the repair.

Electrical faults with no warning light (a window that stopped, a drain on the battery) are a different job: see an advisor.
""",
 serves=['challenge:customer-terms', 'challenge:combine-policy-and-price'],
 facts=['Diagnosis = catalogue job check_engine_diag, 1.0 h at the posted hour.',
        'The fee is charged whether or not the repair is approved; it is not credited (policies/diagnostic-fees.md).',
        'More than one hour needs the customer\'s approval first.'],
 ru=['Russian computer diagnostics is a fixed 0.5 h job (1 200 RUB in the catalogue), cheaper relative to the hour; say what it includes.'])

page('customers/air-conditioning.md', 'Air conditioning not cold', 'W', 5,
 'Public page for the summer season: what the A/C check is, what a recharge costs for each refrigerant.',
 f"""From May to August this is what a lot of our phone calls are about.

## Start with a check

An A/C performance check is {t('ac_performance_check')}. We measure vent temperature and system pressures and look for leaks with a UV light. It tells us whether the system is just low or something has failed.

## Recharge

Customers call it "freon" or "a recharge". On the bill it is *evacuate and recharge*: we recover what is in the system, pull a vacuum to check it holds, and refill by weight.

| Your car uses | Typical cars | Price |
|---|---|---|
| R-134a | Most cars up to about 2016 | {t('ac_recharge')} |
| R-1234yf | Most cars from about 2017 on | {t('ac_recharge_1234yf')} |

The newer refrigerant costs several times more per pound, which is the whole difference. The label under the hood says which one your car takes.

A system that was empty has a leak. A recharge without finding the leak lasts weeks, not years, and we will tell you so before you pay for it.

## Musty smell

A sour smell when the A/C starts is growth on the evaporator. A cleaning service is {t('ac_evaporator_cleaning')}, and a fresh [cabin air filter](maintenance-by-mileage.md) usually goes with it.
""",
 serves=['S11', 'challenge:customer-terms', 'challenge:fact-in-table'],
 facts=['Season: May to August (design S11).',
        'Customer words "freon", "recharge" = catalogue jobs ac_recharge / ac_recharge_1234yf "A/C evacuate & recharge".',
        'R-134a: most cars up to about 2016; R-1234yf: most from about 2017 (rule of thumb; the under-hood label decides).',
        'An empty system has a leak; the advisor must say so before selling a recharge.'],
 new=['The 2016/2017 rule of thumb for refrigerant is a designed simplification; the reference vehicles in the catalogue are a 2015 Camry (R-134a) and a 2019 CR-V (R-1234yf).'],
 ru=['Russian season May to August as well (curve in catalogue.md). Customers say «заправить кондиционер», «фреон».'])

page('customers/battery.md', 'Battery and starting trouble', 'W', 13,
 'Public page: free battery test, replacement price range, the cold-weeks rush.',
 f"""A slow crank on a cold morning is the battery telling you it is nearly done. The first cold weeks of November fill our lot with them.

- **Test:** free, ten minutes, no appointment. We test the battery, the starter draw and the alternator output and give you the printout.
- **Replacement:** {t('battery_replace','economy')} to {t('battery_replace','premium')} installed, for the common size. The price depends on the grade; cars with stop-start need the AGM type, which is the top of that range. We clean the terminals and recycle the old battery.
- **Not the battery?** If the battery tests good and the car still will not start, it is the starter, the alternator or a drain. An advisor will explain what the test showed.

Batteries carry the maker's free-replacement period, printed on the label. Keep your receipt.
""",
 serves=['S11', 'challenge:customer-terms'],
 facts=['Battery test is free (catalogue battery_test, 0.1 h, price 0).',
        'Replacement range = economy to premium totals of battery_replace (group 24F reference).',
        'Battery rush: first cold weeks, November (design S11, curve battery).',
        'Battery warranty: the maker\'s free-replacement period on the label (policies/warranty.md).'],
 ru=['In Russia the battery test is a paid 300 RUB job (catalogue ru battery_test). Rush months: December to February.'])

page('customers/tires.md', 'Tires, flats and alignment', 'W', 15,
 'Public page for tire questions with menu prices.',
 f"""## Flat or slow leak

A nail in the tread can usually be repaired: patch-plug from the inside and rebalance, {t('tyre_repair')}. A hole in the sidewall or shoulder cannot be repaired safely, and we will show you why.

## New tires

We fit the tires we sell. Four tires for a typical sedan, mounted and balanced, run from about {t('new_tyres_fitted','economy')} to {t('new_tyres_fitted','premium')} depending on the brand. That includes the disposal and state tire fees. Most sizes arrive the next morning.

## Rotation and balance

Rotation is {t('tyre_rotation')} and should happen with every other oil change. Balancing four wheels is {t('wheel_balance')}; ask for it if the steering wheel shakes at highway speed.

## Alignment

A four-wheel alignment is {t('wheel_alignment')}. Get one with new tires, after a hard pothole hit, or when the car drifts or the steering wheel sits off-centre.

## Tire pressure light

If the light stays on after you set the pressures, a sensor in one wheel has probably died. Replacing one sensor is about {t('tpms_sensor')}.
""",
 serves=['challenge:customer-terms', 'challenge:fact-only-in-attachment'],
 facts=['Flat repair = patch-plug, rebalance; sidewall or shoulder damage is not repairable.',
        'New tyres range: economy to premium totals of new_tyres_fitted (215/55R17 reference), fees included.',
        'Rotation advised every other oil change.',
        'Most tyre sizes arrive next morning (vendor V5: daily run in Chattanooga).'],
 new=['"Most sizes arrive the next morning" is true for the Chattanooga shops; Charlotte Pike gets tyres twice a week (vendors.json V5). The public page does not say so: planted, see parts/suppliers.md.'],
 ru=['The Russian page is a different page: seasonal changeover twice a year, storage per season, studded tyres. Write it from the Russian catalogue (seasonal_tyre_change, seasonal_wheel_swap, tyre_storage).'])

page('customers/maintenance-by-mileage.md', 'Maintenance by mileage', 'W', 5,
 'Public explanation of oil service, filters and the 30/60/90K service.',
 f"""Your owner's manual has the schedule for your car, and it wins over anything here. This is what most cars need.

| When | What |
|---|---|
| Every 5,000 to 7,500 miles | Full synthetic oil and filter, {t('oil_service')}. Tire rotation every other time |
| Every 15,000 to 30,000 miles | Engine air filter and cabin air filter. We show you the old one before we change it |
| Every 30,000 miles | Scheduled maintenance service: inspect, adjust and lubricate by the maker's list |
| Every 2 to 3 years | Brake fluid |
| 60,000 to 100,000 miles | Spark plugs, coolant, transmission fluid, drive belt |
| About 100,000 miles, some engines | Timing belt. Not every engine has one; many have a chain that is not serviced |

People ask for a "tune-up". Modern cars have nothing to tune: what the word means today is spark plugs and filters, and an inspection.

With every service we do a free courtesy inspection and send you the result with photos: green, yellow, red. Yellow means watch it. Red means we recommend doing it now, and we will give you a price. You decide.
""",
 serves=['challenge:customer-terms', 'challenge:fact-in-table'],
 facts=['Intervals are the trade\'s rule of thumb; the owner\'s manual wins.',
        '"Tune-up" in customers\' words = spark plugs, filters and an inspection.',
        'Courtesy inspection is free with every service; three states shown to the customer as green, yellow, red (ERP inspection_item: good, watch, bad).'],
 new=['Interval table (5,000-7,500 miles oil; 15-30K filters; 30K scheduled service; brake fluid 2-3 years; 60-100K plugs, coolant, ATF, belt; about 100K timing belt). Reason: needed for the page; standard advice, no catalogue row.'],
 ru=['Russian intervals in km: oil every 7 500 to 10 000 km (older parc, short trips), scheduled ТО every 15 000 km. "Tune-up" has no Russian twin; use «ТО» and what customers call «плановое ТО».'])

page('customers/pre-purchase-inspection.md', 'Buying a used car: pre-purchase inspection', 'W', 5,
 'Public description of the pre-purchase inspection.',
 f"""Before you buy a used car, let us look at it. {t('pre_purchase_inspection')}, about an hour and a half.

You get a written report: a road test, a scan for stored fault codes, the underside on a lift (leaks, rust, accident repair), brakes and tires measured, fluids, belts, battery test, and our estimate of what it will need in the first year.

The seller can bring the car or you can. We give the report to whoever paid for it. We do not tell you whether to buy; we tell you what you are buying.
""",
 serves=['smoke'],
 facts=['Catalogue job pre_purchase_inspection: menu price, 1.5 h.',
        'Report contents: road test, code scan, underside on a lift, brakes and tyres measured, fluids, belts, battery test, first-year estimate.',
        'The report goes to whoever paid.'],
 ru=['Russian price 3 000 RUB (catalogue.md). Customers call it «проверка перед покупкой», «автоподбор» is a different service.'])

page('customers/hybrids-and-electric-cars.md', 'Hybrids and electric cars', 'W', 2,
 'The stated limit of what the shops do on hybrids and EVs.',
 f"""**Hybrids:** we do the ordinary service: oil, filters, brakes, tires, alignment, suspension, the 12-volt battery, coolant. Hybrid work is done at East Main only. We do not repair the high-voltage battery, the inverter or the drive motor; for those we will point you to a dealer.

**Electric cars:** tires, alignment and brakes. Nothing else.
""",
 serves=['challenge:kb-does-not-say'],
 facts=['Hybrids: basic service only; high-voltage battery, inverter and drive motor are not repaired (design 1.5).',
        'EVs: tyres and brakes (design 1.5); alignment added as part of tyre work.',
        'Hybrid work is done at East Main only, because slot 10 is the only technician trusted with hybrids (cast).'],
 new=['"Hybrid work is done at East Main only" for customers. Reason: follows from the cast; makes a question about a hybrid at Bonny Oaks or Charlotte Pike answerable.'],
 ru=['Same limits. The trusted technician is slot 10 at the main shop.'])

page('customers/company-vehicles.md', 'Company vehicles', 'W', 2,
 'Public pointer for businesses; the terms themselves are staff-only.',
 f"""We look after work vans, pickups and company cars for businesses around Chattanooga and Nashville, from one truck to thirty-five vans.

- A business with five or more vehicles can apply for an account and pay on a monthly statement.
- Smaller businesses are welcome and pay at pick-up like anyone else. We keep each vehicle's history under your company name.
- A work vehicle that is off the road gets looked at ahead of the line.

To set up an account, call {S(4,'full')}, service manager, at (423) 555-0142.
""",
 serves=['S1', 'visibility:public'],
 facts=['Accounts are offered from five vehicles (accounts/opening-a-company-account.md).',
        'Largest fleet is 35 vans (account A1, not named to the public).',
        'Contact for new accounts: slot 4 on the main line.',
        'Terms, rates and approval limits are not on any public page: a customer asking the assistant for fleet rates gets "ask the service manager".'],
 new=['Account threshold of five vehicles. Reason: the six named accounts have 8 to 35 vehicles and the small business customers 1 to 3; five separates them.'],
 ru=['Russian companies are billed per order with a closing document each time, not on a monthly statement (design R11): say "по договору, с отсрочкой платежа".'])
