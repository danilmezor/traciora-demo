from kbb import *
import kbb
REV = lambda: D('@price_rise+3wd:main')
RISE = [(4, '@price_rise+3wd:main', 'Travis\'s pass after the price rise: every dollar figure brought to the new list (proposed by slot 5, approved by slot 4); message: "New labour rate."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})]
RISE16 = [(4, '@price_rise+3wd:main', 'Angie\'s pass after the price rise: every dollar figure brought to the new list (proposed by slot 16, approved by slot 4); message: "New labour rate."', {'kind': 'proposal', 'proposer_slot': '16', 'approver_slot': '4'})]
def three(key, cls='car'):
    return f"{t(key,'economy',cls)} / {t(key,'standard',cls)} / {t(key,'premium',cls)}"

page('services/README.md', 'Services', 'W', 5,
 'Index of the service pages and how to use them on the phone.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

One page per kind of job. Each says what the job is, when a car needs it, what to ask the customer, how long it takes and what customers push back on. They are written for the counter, not for the bay.

**The prices on these pages are examples**: a car, standard parts, before supplies and tax. They are here so you can explain the job. Quote from the [price list](../prices/price-list.md).

| Folder | Pages |
|---|---|
| maintenance | [Oil change](maintenance/oil-change.md) · [Filters and wipers](maintenance/filters-and-wipers.md) · [Spark plugs and the "tune-up"](maintenance/spark-plugs.md) · [Coolant service](maintenance/coolant-service.md) · [Scheduled maintenance 30/60/90K](maintenance/scheduled-maintenance.md) · [Fuel system service](maintenance/fuel-system-service.md) · [Fleet PM service A](maintenance/fleet-pm-service.md) |
| brakes | [Brake inspection](brakes/brake-inspection.md) · [Pads and rotors](brakes/pads-and-rotors.md) · [Calipers and drum brakes](brakes/calipers-and-drum-brakes.md) · [Brake fluid flush](brakes/brake-fluid-flush.md) |
| tires | [Rotation, balance and flat repair](tires/rotation-balance-and-flat-repair.md) · [Alignment](tires/alignment.md) · [New tires and tire-pressure sensors](tires/new-tires-and-tpms.md) |
| diagnostics | [Check engine light](diagnostics/check-engine-light.md) · [Electrical diagnosis](diagnostics/electrical-diagnosis.md) · [Noises and vibrations](diagnostics/noises-and-vibrations.md) |
| suspension | [Struts and shocks](suspension/struts-and-shocks.md) · [Front-end parts](suspension/front-end-parts.md) · [Wheel bearings and steering racks](suspension/wheel-bearings-and-steering-racks.md) |
| ac | [A/C check and recharge](ac/ac-check-and-recharge.md) · [A/C compressor and condenser](ac/ac-compressor-and-condenser.md) |
| electrical | [Battery](electrical/battery.md) · [Alternator and starter](electrical/alternator-and-starter.md) |
| engine | [Timing belt](engine/timing-belt.md) · [Drive belt](engine/drive-belt.md) · [Cooling system repairs](engine/cooling-system-repairs.md) · [Leaks and gaskets](engine/leaks-and-gaskets.md) · [Ignition, sensors and fuel pump](engine/ignition-sensors-and-fuel-pump.md) · [Mounts and exhaust](engine/mounts-and-exhaust.md) |
| transmission | [Transmission fluid service](transmission/transmission-fluid-service.md) · [Clutch and CV axles](transmission/clutch-and-cv-axles.md) · [Transmission rebuild](transmission/transmission-rebuild.md) |
| inspections | [Courtesy inspection](inspections/courtesy-inspection.md) · [Pre-purchase inspection](inspections/pre-purchase-inspection.md) |

Also: [Hybrids](hybrids.md).
""",
 serves=['S12', 'operate:overview', 'challenge:near-duplicate'],
 facts=['37 service pages in ten folders plus hybrids.md; each written for the counter.',
        'Prices on service pages are examples (car, standard parts, before supplies and tax); quotes come from the price list.',
        'The old page services/brakes/brake-questions.md is not in this index (orphan: its author left).'],
 rev=RISE,
 ru=['Russian folders the same; tyres folder gains seasonal changeover and storage pages.'])

page('services/maintenance/oil-change.md', 'Oil change', 'W', 5,
 'The most common job: what it includes, the three oils, what to ask, the upsell that is not an upsell.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Full synthetic oil & filter change**. One car in three that comes through the door is here for this.

## What it is

Drain, new filter, up to 5 quarts of oil, reset the reminder, top up the washer, set the tire pressures, and the courtesy inspection. Half an hour of work; allow 45 minutes with the inspection. Customers can wait.

## The three prices

| Oil | Filter | Price |
|---|---|---:|
| Synthetic blend | ECOGARD | {t('oil_service','economy')} |
| Full synthetic (what we quote) | WIX | {t('oil_service')} |
| Mobil 1 Extended Performance | Original | {t('oil_service','premium')} |

It is a menu price: no shop supplies. Engines that take more than 5 quarts pay {part('oil_service',0)} for each extra quart of the standard oil. Trucks and V8s usually do.

## Ask

- Year, make, model, engine. The engine decides the quarts and the filter.
- Mileage now, and at the last change if they know.
- "Is anything else going on with it?" This is the cheapest visit to find the expensive problem on.

## Say

- "About 45 minutes, and we will look the car over and send you pictures."
- Tire rotation is {t('tyre_rotation')} while it is on the lift. Every other oil change.
- If they ask how often: the manual, and for most cars that is 5,000 to 7,500 miles. Not 3,000. We do not sell people oil changes they do not need.

## They say

- **"The quick-lube place is $40."** "For blend oil and whatever filter is on the shelf, and nobody looks at your brakes. Ours with blend is {t('oil_service','economy')}, and a technician inspects the car."
- **"Do I need synthetic?"** If the cap or the manual says 0W-20, yes: that only comes as synthetic. Otherwise it is their choice, and blend is fine on an older engine.
""",
 serves=['challenge:fact-in-table', 'challenge:customer-terms', 'smoke'],
 facts=['Catalogue job oil_service: menu price, 0.5 h, 5 qt; carried by 31.9 % of orders ("one car in three").',
        'Three tiers: blend with ECOGARD filter; full synthetic with WIX (default); Mobil 1 with original filter.',
        'Extra quarts at the standard oil\'s list price per quart.',
        'Allow 45 minutes with the inspection; waiters welcome.',
        'Rotation offered every other oil change.',
        'Interval advice 5,000 to 7,500 miles, "not 3,000".',
        'The competitor price "$40" is a customer\'s words.'],
 rev=RISE,
 ru=['Russian oil service is priced by the hour (0.7 н/ч) with 4 l; brands Лукойл / Shell; interval 7 500 to 10 000 km; «в гараже дешевле» is the objection.'])

page('services/maintenance/filters-and-wipers.md', 'Filters and wipers', 'W', 5,
 'Engine air filter, cabin filter, wiper blades: small jobs sold from the inspection.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

Three small jobs that almost always come from the inspection, not from the customer.

| Job | Time | Standard | Economy to premium |
|---|---|---:|---|
| Engine air filter | {hrs('engine_air_filter')} h | {t('engine_air_filter')} | {t('engine_air_filter','economy')} to {t('engine_air_filter','premium')} |
| Cabin air filter | {hrs('cabin_air_filter')} h | {t('cabin_air_filter')} | {t('cabin_air_filter','economy')} to {t('cabin_air_filter','premium')} |
| Wiper blades, pair | fitted free | {t('wiper_blades')} | {t('wiper_blades','economy')} to {t('wiper_blades','premium')} |

- **Show the old one.** A grey cabin filter full of leaves sells itself. A clean one means we do not recommend it, and the customer remembers that we did not.
- Cabin filter: every 15,000 to 30,000 miles, sooner for anyone who parks under trees. If the A/C smells, this first.
- Wipers streaking or chattering. There is no labour charge to fit them.
- Customers know they can buy a filter at the parts store for less. Say so first: "You can do this one yourself for about half. If you would rather we did it while it is here, it is ten minutes."

Fuel filter is a different job on a different page: [Fuel system service](fuel-system-service.md).
""",
 serves=['challenge:fact-in-table', 'smoke'],
 facts=['Catalogue jobs engine_air_filter (0.2 h), cabin_air_filter (0.3 h), wiper_blades (menu, no labour).',
        'Sold mostly from the inspection (recommended share 0.80 to 0.85).',
        'Show the old filter; do not recommend a clean one.',
        'Cabin filter interval 15,000 to 30,000 miles.',
        'Advisors say up front that the customer can do it for less.'],
 rev=RISE,
 ru=['Same jobs; Russian wiper price is high relative to labour (2 570 RUB standard).'])

page('services/maintenance/spark-plugs.md', 'Spark plugs and the "tune-up"', 'W', 5,
 'What a customer means by a tune-up and what the plug job costs by engine.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

Nobody under fifty has tuned a car. When a customer asks for a **tune-up**, they mean: it does not run like it used to, make it right. What we actually sell is spark plugs, filters and an inspection, and, if there is a light on, a [diagnosis](../diagnostics/check-engine-light.md) first.

## Spark plugs

On the order: **Replace spark plugs**. Iridium plugs last 60,000 to 100,000 miles and then the engine starts to stumble on cold mornings and use more gas.

- Four-cylinder car: {hrs('spark_plugs')} hour, {t('spark_plugs')} with NGK plugs.
- **A V6 is not the same job.** The back three plugs are under the intake manifold, and it comes off. Labour is {lab('spark_plugs', cls='suv')} instead of {lab('spark_plugs')}, plus two more plugs. Price it by the [class table](../../prices/labour-rates-and-fees.md), not by this page.
- Trucks and vans with V8s: in between.

## Ask

- How many cylinders? If they do not know: year, make, model, and look it up.
- Is the check engine light on? If it is, book the diagnosis, not the plugs. Plugs on a car with a bad coil is money spent twice.
- When were they last done? "Never" at 120,000 miles is common.

## They say

- **"I just want a tune-up, how much?"** "On a modern car that is plugs and filters. For your four-cylinder the plugs are {t('spark_plugs')}. Let us look at the filters when it is here; they may be fine."
- **"Why is my V6 double?"** "Half the plugs are under the intake. It is two and a half hours instead of one."

If one coil has failed: [Ignition, sensors and fuel pump](../engine/ignition-sensors-and-fuel-pump.md).
""",
 serves=['challenge:customer-terms', 'challenge:combine-policy-and-price', 'challenge:fact-in-table'],
 facts=['"Tune-up" = spark plugs, filters, inspection; a warning light means diagnosis first.',
        'Catalogue job spark_plugs: 1.0 h for a four-cylinder car; standard NGK; iridium plugs last 60,000 to 100,000 miles.',
        'V6 (class SUV) labour multiplier 2.4: labour at the SUV figure, plus two more plugs; trucks 1.6, vans 1.8.',
        'The V6 total is not printed: it must be computed from the class table (six plugs: 135.00 x 2.4 = 324.00 labour; six plugs at 21.82 x 1.15 to the cent, 25.09 each = 150.54; total 474.54 before supplies and tax).'],
 new=['Expected answer for "spark plugs on a V6 SUV, standard": 474.54 USD = labour 324.00 + six plugs at 25.09 (21.82 x 1.15 to the cent). The catalogue prices four plugs; the per-plug count for six cylinders is the reader\'s arithmetic and should be confirmed as the seeder prices it.'],
 rev=RISE,
 ru=['Russian: «замена свечей» is 0.6 н/ч for four; no "tune-up" word; customers say «троит», «плохо заводится».'])

page('services/maintenance/coolant-service.md', 'Coolant service', 'W', 5,
 'Coolant drain, flush and fill.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Coolant drain, flush & fill**. {hrs('coolant_exchange')} hour, {t('coolant_exchange')}, two gallons of the right coolant.

Coolant wears out: the additives that stop corrosion are used up in about five years or 100,000 miles on modern long-life coolant, sooner on older green. Old coolant eats water pumps and radiators from the inside.

- Sold from the inspection: the technician tests it with a strip and notes the result.
- **The right coolant matters.** Pink for Toyota, blue for Honda and Subaru, orange for GM. Never "universal" in a car under ten years old.
- If the coolant is low, that is a leak, not a service. Pressure test first ({t('cooling_pressure_test')}): [Cooling system repairs](../engine/cooling-system-repairs.md).
- Any job that opens the cooling system (water pump, thermostat, radiator, timing belt on some engines) already includes coolant. Do not sell this on top.
""",
 serves=['challenge:combine-policy-and-price', 'smoke'],
 facts=['Catalogue job coolant_exchange: 1.0 h, 2 gallons, one price in all tiers.',
        'Long-life coolant about five years or 100,000 miles.',
        'Coolant by maker: pink Toyota, blue Honda and Subaru, orange GM.',
        'Low coolant means a leak: pressure test first.',
        'Jobs that open the cooling system include coolant; the service is not added on top.'],
 new=['Five years or 100,000 miles as the interval (common long-life coolant advice).'],
 rev=RISE,
 ru=['«Замена антифриза»; G11 / G12 / G12++ by maker.'])

page('services/maintenance/scheduled-maintenance.md', 'Scheduled maintenance: 30K, 60K, 90K', 'W', 5,
 'The mileage service: what the labour covers and what is priced separately.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Scheduled maintenance service (30K / 60K / 90K) - inspect, adjust, lubricate**. {hrs('scheduled_maintenance')} hours, {t('scheduled_maintenance')} labour.

What that buys: the maker's inspection list for that mileage, done properly. Brakes measured with the wheels off, suspension and steering checked on the lift, hinges and latches lubricated, fluids checked and topped, battery tested, road test, and the reminder reset.

**It does not include the parts and fluids the list calls for.** Those are separate lines, priced from the list, and they differ by mileage:

| At | Usually also due |
|---|---|
| 30,000 | Oil service, engine and cabin air filters, tire rotation |
| 60,000 | The 30K items, plus brake fluid, and on many cars transmission fluid |
| 90,000 | The 30K items, plus spark plugs and coolant if not done; ask about the timing belt |

So a 60K service is not {t('scheduled_maintenance')}. Add it up for the customer before they come, from the price list, so the number at the counter is the number they heard.

- Look up the car's own schedule. The table is a habit, not a rule.
- People with a new car under the maker's warranty ask whether they have to go to the dealer. They do not. Keep the invoice.
""",
 serves=['challenge:combine-policy-and-price', 'challenge:fact-in-table'],
 facts=['Catalogue job scheduled_maintenance: 1.8 h, labour only, no parts.',
        'Labour covers the maker\'s inspection list; parts and fluids are separate catalogue lines.',
        'Typical extras: 30K oil service, both air filters, rotation; 60K adds brake fluid and often transmission fluid; 90K adds spark plugs, coolant, and the timing belt question.',
        'A full 60K quote must be added up from the price list (for example: 243.00 + 90.95 + 53.14 + 64.36 + 25.00 + 151.00 = 627.45 before supplies and tax, with transmission drain and fill 191.98 more).'],
 new=['The 30/60/90K table of typical extras.'],
 rev=RISE,
 ru=['«ТО по регламенту», every 15 000 km; ТО-1, ТО-2 etc.'])

page('services/maintenance/fuel-system-service.md', 'Fuel system service', 'W', 5,
 'Induction cleaning and the fuel filter: when it helps and when it is snake oil.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

Two jobs.

**Fuel induction & injector cleaning service**: {hrs('fuel_system_cleaning')} h, {t('fuel_system_cleaning')}. Cleaner run through the intake and the injectors. It helps direct-injection engines past 60,000 miles that idle rough or hesitate, because their intake valves coke up. It does nothing for a car that runs fine, and we do not sell it to one.

**Replace fuel filter**: {hrs('fuel_filter')} h, {t('fuel_filter')}. Only on vehicles that have a serviceable one, which today means older trucks and some imports. Most cars built since about 2010 have the filter inside the tank for life. If the catalogue does not offer it for the car, the car does not have one.

Customers ask for "injector cleaner" because a bottle at the parts store promised a lot. Be straight: if there is a drivability complaint, the first job is a [diagnosis](../diagnostics/check-engine-light.md), not a cleaning.
""",
 serves=['challenge:customer-terms', 'smoke'],
 facts=['Catalogue jobs fuel_system_cleaning (0.8 h) and fuel_filter (0.7 h; reference vehicle a 2010 F-150).',
        'Cleaning is for direct-injection engines past 60,000 miles with symptoms; not sold to a car that runs fine.',
        'Serviceable fuel filters are on older trucks and some imports; most cars since about 2010 have none.',
        'A drivability complaint gets a diagnosis first.'],
 rev=RISE,
 ru=['«Промывка форсунок», «замена топливного фильтра» (common on Russian parc: many cars still have a serviceable filter).'])

page('services/maintenance/fleet-pm-service.md', 'Fleet PM service A', 'W', 4,
 'The preventive-maintenance service for cargo vans; list price and what the company rate does to it.',
 f"""*{S(4)} · Last reviewed {REV()}*

On the order: **Fleet PM service A - cargo van (oil & filter, chassis lube, 50-point inspection)**. Vans only. {hrs('fleet_pm_van', cls='van')} hours.

## What is in it

- Oil and filter: 6 quarts of full synthetic, {part('fleet_pm_van',0)} a quart, and a {part('fleet_pm_van',1)} filter.
- Chassis lube where there are fittings. Door hinges, sliding-door track, rear door checks.
- The 50-point inspection: brakes measured at all four wheels, tires with tread depth and age, lights including the cargo light, belts, hoses, leaks, battery test, wipers, horn, steering play, load-floor and bulkhead fixings.
- The fleet sheet filled in: unit number, mileage, what is due before the next PM.

## Price

List: labour {lab('fleet_pm_van', cls='van')} plus oil and filter, **{t('fleet_pm_van', cls='van')}** before supplies and tax.

Accounts on the company rate pay the company labour rate and 10 % less for the oil and filter: see [Company accounts](../../accounts/company-account-terms.md). Work it out from there; it is not a figure to quote from memory.

## How it runs

- Every 5,000 miles for the delivery fleets. The fleet manager sends the units due.
- The van is back the same day. A PM is never the reason a van misses its route.
- **Anything found is an estimate to the fleet contact**, not a conversation with the driver beyond his limit.
- Quarts by van: [Fluids and capacities](../../parts/fluids-and-capacities.md).
""",
 serves=['S1', 'S16', 'challenge:combine-policy-and-price', 'challenge:fact-only-in-attachment'],
 facts=['Catalogue job fleet_pm_van: vans only, 1.5 h; 6 qt of standard oil and a filter.',
        'List price 270.59 (labour 202.50 + oil 54.00 + filter 14.09).',
        'The company-rate price is deliberately not printed: 1.5 h x 121.50 = 182.25 labour + 0.9 x 68.09 = 61.28 parts = 243.53 before supplies and tax (shop supplies 5 % of 182.25 = 9.11).',
        'Contents of the 50-point inspection and the fleet sheet.',
        'Interval 5,000 miles; same-day return; findings go to the fleet contact as an estimate.'],
 new=['Expected answer for "what does Nickajack pay for a PM service A": 243.53 USD before shop supplies and tax (252.64 with supplies 9.11; 276.01 with tax at 9.25 %, the rate of East Main, the account\'s home shop).'],
 rev=RISE,
 ru=['«ТО коммерческого автомобиля», 9 710 RUB list; contract hour 1 700; compute the contract price the same way.'])

# ---------------------------------------------------------------- brakes
page('services/brakes/brake-inspection.md', 'Brake inspection', 'W', 16,
 'The inspection every brake complaint starts with.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

Every brake complaint starts here. On the order: **Brake system inspection**, {t('brake_inspection')}, half an hour. Menu price.

Wheels off, all four. Pads and rotors measured in millimetres, hoses and lines looked at, calipers checked for sticking slides, fluid tested, a short road test if it is safe to drive. The customer gets the measurements and the photos.

Book this, not "brakes". We do not know what a car needs until the wheels are off, and neither does the customer, whatever the last shop told them.

- If the car is already in for a service and the technician sees thin pads through the wheel, that is the free courtesy inspection doing its job. There is no inspection charge for that.
- The fee is not taken off the repair. [Why](../../policies/diagnostic-fees.md).
- Grinding, a pedal that sinks, or a brake warning light: tell the customer not to drive it far, and offer the [tow](../../customers/towing.md).

What comes next is usually [pads and rotors](pads-and-rotors.md).

{S(16)}
""",
 serves=['S7', 'challenge:combine-policy-and-price'],
 facts=['Catalogue job brake_inspection: menu 49.95, 0.5 h; wheels off, measurements in mm, hoses, slides, fluid, road test, photos.',
        'Thin pads seen during the courtesy inspection carry no inspection charge.',
        'The fee is not credited.',
        'S7: the customer\'s first visit began with this job.'],
 rev=RISE16,
 ru=['«Диагностика тормозной системы», 700 RUB.'])

page('services/brakes/pads-and-rotors.md', 'Pads and rotors', 'W', 16,
 'The main brake job: pads alone or with rotors, the three parts tiers, what to say.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

The brake job. Priced per axle.

## What we sell

| On the order | Hours | Economy / Standard / Premium |
|---|---|---|
| Replace front brake pads & rotors | {hrs('front_pads_rotors')} | {three('front_pads_rotors')} |
| Replace rear brake pads & rotors | {hrs('rear_pads_rotors')} | {three('rear_pads_rotors')} |
| Replace front brake pads, clean & lube hardware | {hrs('front_brake_pads')} | {three('front_brake_pads')} |
| Replace rear brake pads, clean & lube hardware | {hrs('rear_brake_pads')} | {three('rear_brake_pads')} |

A car, before supplies and tax. SUVs, trucks and vans are more: [class table](../../prices/labour-rates-and-fees.md).

## Pads alone, or with rotors?

We measure the rotors. If they are above the minimum thickness stamped on them, smooth and not pulsing, pads alone is the honest job and I sell it gladly. If they are under size, scored or blue, new pads on them will squeal and be back in a month. Then it is pads and rotors, and I show the customer the measurement. We do not machine rotors; on a modern thin rotor there is nothing to machine.

## Which pads

Standard is the Wagner ThermoQuiet and it is what I would put on my own car. Premium is the Akebono: less dust, lasts longer, worth it for someone who keeps the car. Economy is the ACDelco and it is a decent pad. More: [Brake pads we fit](../../parts/brake-pads-we-fit.md).

## On the phone

- Never a price without the car and without saying "if". "If it needs front pads and rotors, on your Camry that is {t('front_pads_rotors')}. If the rotors measure good, it is {t('front_brake_pads')}. The inspection tells us which."
- Then a time. Dropped off at 7:30, a brake job is back the same afternoon when the parts are on the shelf, and for the common cars they are.

## At the counter

Photo first. The old pad beside a new one. Then the price. Then: "I can have it done by three today, or first thing Thursday."

## They say

- **"The other shop said $199 for brakes."** "Pads only, per axle, with their cheapest pad, and the rotors are extra when they get the wheels off. Ours with the economy pad is {t('front_brake_pads','economy')}. Do you want me to price it both ways?"
- **"Can you just do the pads?"** "If the rotors measure good, yes, and I will tell you. If they do not, I would rather you did nothing than waste the pads."
- **"They are squealing but they were done last year."** Where? By us: [comeback](../../how-to/a-comeback-at-the-counter.md), no charge to look. Elsewhere: inspection.

Brake work is warrantied 24 months or 24,000 miles; the pads themselves 12 months or 12,000 against defects and noise. Wear is not a defect.

{S(16)}
""",
 serves=['S7', 'S6', 'S12', 'challenge:fact-in-table', 'challenge:customer-terms', 'challenge:near-duplicate'],
 facts=['Four catalogue jobs with hours and the three tier totals (front_pads_rotors, rear_pads_rotors, front_brake_pads, rear_brake_pads), class car.',
        'Pads alone when rotors measure above minimum thickness and are smooth; otherwise pads and rotors; rotors are not machined.',
        'Pad lines: Wagner ThermoQuiet (standard), Akebono ProACT (premium), ACDelco Silver (economy).',
        'Phone rule: a conditional price with the car named, then a time; same-afternoon return from a 7:30 drop when parts are on the shelf.',
        'Counter rule: photo, price, two times.',
        'Warranty: work 24/24; pads 12/12 against defects and noise.',
        'This page is current; services/brakes/brake-questions.md gives the same four jobs at the old labour rate (S12).',
        'S7: front pads and rotors approved at the standard total; rear shocks declined.',
        'The competitor figure "$199" is a customer\'s words.'],
 new=['The shop does not machine rotors (no catalogue job exists for it).'],
 rev=RISE16,
 ru=['«Замена передних тормозных дисков и колодок»; проточка дисков is common in Russia: say the shop does not do it or add a catalogue row. Prices in RUB by tier.'])

page('services/brakes/calipers-and-drum-brakes.md', 'Calipers and drum brakes', 'W', 16,
 'The less common brake jobs: a seized caliper, rear shoes.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

**Replace front brake caliper (one side), bleed**: {hrs('brake_caliper')} hours, {t('brake_caliper')} with a remanufactured caliper. Priced per side. A caliper is replaced when it leaks or when the piston or slides have seized: the signs are one pad worn to nothing while the other looks new, a wheel that is hot after a drive, or the car pulling under braking. It is usually found during a pad job, which is why the customer hears about it by phone and not at the start. Have the photo.

We replace the one that failed. If the other side is the same age and the boot is torn, we say so and let the customer choose.

**Replace rear brake shoes & hardware (drum)**: {hrs('rear_brake_shoes')} hours, {t('rear_brake_shoes')}. Smaller and older cars and some trucks still have drums at the back. Shoes last a long time, often 100,000 miles, so the customer has usually never heard of them. "It is the same job as pads, on the older kind of brake. More fiddly, which is why it is two hours."

A caliper carries a core charge to us until the old one goes back. The customer does not see it: [Returns and cores](../../parts/returns-and-cores.md).

{S(16)}
""",
 serves=['smoke', 'challenge:customer-terms'],
 facts=['Catalogue job brake_caliper: 1.3 h, per side, reman caliper standard; signs of a seized caliper.',
        'Catalogue job rear_brake_shoes: 2.0 h; shoes last about 100,000 miles.',
        'Only the failed caliper is replaced; the other side is mentioned.',
        'Caliper cores are not billed to the customer.'],
 rev=RISE16,
 ru=['«Замена суппорта», «замена задних колодок (барабанные тормоза)»; drums are common on the Russian parc (Granta, Logan, Solaris).'])

page('services/brakes/brake-fluid-flush.md', 'Brake fluid flush', 'W', 16,
 'Brake fluid exchange: why, when, how it is sold.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

On the order: **Brake fluid flush**. {hrs('brake_fluid_exchange')} hour, {t('brake_fluid_exchange')}.

Brake fluid takes up water from the air. Wet fluid boils on a long downhill, and Signal Mountain and Lookout Mountain are both long downhills. It also rusts calipers and the ABS unit from the inside. Every two to three years, whatever the mileage.

- The technician tests the fluid with a meter at the inspection and writes the percentage. Over 3 % water is a recommendation. Show the customer the number.
- It is sold nine times in ten from the inspection. Nobody calls up asking for it.
- A caliper or hose job includes bleeding that corner, not a full flush. If the fluid is old, sell both together: the system is open anyway.

{S(16)}
""",
 serves=['smoke'],
 facts=['Catalogue job brake_fluid_exchange: 1.0 h; recommended share 0.9 ("nine times in ten from the inspection").',
        'Interval two to three years; tested with a meter; over 3 % water is a recommendation.',
        'Local colour: Signal Mountain and Lookout Mountain (real places near Chattanooga).',
        'A caliper job bleeds one corner only.'],
 new=['The 3 % water threshold.'],
 rev=RISE16,
 ru=['«Замена тормозной жидкости», every two years; replace the mountain line with a local equivalent or drop it.'])

page('services/brakes/brake-questions.md', 'Brake questions', 'W', 'F3',
 'An old FAQ by an advisor who has left: still carries the labour rate and brake prices from before the rise. Stale on purpose (S12).',
 f"""*BK · {D('T-9mo')}*

Quick answers for the phone. Rate is {rate('standard','before_rise')}/hr.

**How much for brakes?**
Front pads and rotors, most cars: {told('front_pads_rotors')} with the Wagner pads. 1.8 hrs at {rate('standard','before_rise')} plus parts.
Rear pads and rotors: {told('rear_pads_rotors')}.
Pads only, front: {told('front_brake_pads')}. Rear: {told('rear_brake_pads')}.
Trucks more. Always say "most cars".

**How much to look at them?**
Inspection {told('brake_inspection')}. Half an hour.

**How long does it take?**
Pads and rotors, two hours a pair. In by 8, out by lunch.

**Do you turn rotors?**
No. We replace.

**Brake fluid?**
Flush is {told('brake_fluid_exchange')}. Every 2-3 yrs.

**Squeal after new pads?**
Normal for a few days while they bed in. If it is still there after a week, bring it back, no charge to look.

**Warranty?**
24/24 on the work. Pads 12/12.

**Lifetime pads?**
We don't do lifetime pads. The places that do make it back on the rotors.

BK
""",
 serves=['S12', 'S8', 'challenge:near-duplicate', 'operate:contradiction', 'operate:propose'],
 facts=['STALE ON PURPOSE (S12): the second of the two pages that still carry the labour rate from before the rise. Labour rate 125.00; front pads and rotors 475.00; rear pads and rotors 452.27; front pads 223.86; rear pads 214.77; inspection 46.25; fluid flush 141.00 (all catalogue before_rise totals, standard tier, class car).',
        'Current figures on the price list: 493.00; 470.27; 234.86; 225.77; 49.95; 151.00.',
        'Written by slot F3 (Brad Keller, resigned the Monday of week T-30), signed "BK", dated T-9 months; nobody owns it and no index links to it.',
        'Public (ledger s12.pages): the website assistant can read it and could quote the old figures to a customer.',
        'Story call 12 (the Tuesday of week T-5): slot 7 priced front brakes from this page (475.00 against 493.00: ledger s12.brake_price); his second wrong promise.',
        'No correction has been proposed for this page: only the timing belt page has one waiting.',
        'Its other answers (no rotor turning, 24/24, pads 12/12, no lifetime pads) agree with the current pages.'],
 stale='S12: old labour rate and brake prices',
 ru=['Russian stale page at 1 760 руб./н-ч with the before_rise totals of the same four jobs; signed by slot F3\'s initials (ВС).'])
