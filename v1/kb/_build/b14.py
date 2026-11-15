from kbb import *
import kbb, json
REV = lambda: D('@price_rise+3wd:main')
RISE = [(4, '@price_rise+3wd:main', 'Travis\'s pass after the price rise: every dollar figure brought to the new list (proposed by slot 5, approved by slot 4); message: "New labour rate."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})]

# ---------------------------------------------------------------- engine: the stale page
OLD_PRICE = f"""Labour is {hrs('timing_belt_kit')} hours at {rate('standard','before_rise')}, {lab('timing_belt_kit','before_rise')}. The Gates kit with the pump is {part('timing_belt_kit',0)} and a gallon of coolant {part('timing_belt_kit',1)}. **{told('timing_belt_kit')}** before supplies and tax. With the Aisin kit, {told('timing_belt_kit','premium')}."""
OLD_SAMEDAY = """**Same day.** If the car is here by 8:00 it goes home that afternoon. Tell the customer so; it is a selling point against the dealer, who keeps it two days."""
OLD_DATE = f"""*{S(5,'full')} · Last reviewed {D('T-9mo')}*"""
p = page('services/engine/timing-belt.md', 'Timing belt', 'W', 5,
 'The timing-belt job, as written before the price rise: old labour rate, old total, and a same-day promise. Stale on purpose (S12); a correction is proposed and waiting.',
 f"""{OLD_DATE}

On the order: **Replace timing belt, tensioner, idlers & water pump**.

## What it is

The timing belt keeps the valves and the pistons from meeting. It is like a bicycle chain, only when this one snaps the engine keeps turning for a moment and the valves hit the pistons. On most of the engines that have a belt, that is the end of the engine. There is no warning. It does not squeal first.

So it is replaced on mileage, not on condition: usually between 60,000 and 105,000 miles, or seven to ten years, whichever comes first. The maker's schedule says which. The Subaru 2.5 is 105,000.

Not every engine has one. Many have a chain, which is not serviced. Look it up before you say anything to a customer who asks.

## What we replace

The belt, the tensioner, the idler pulleys and the water pump, as a kit. The pump is driven by the belt and sits behind it. A pump that fails a year later means paying for this whole job again, so we do not do a belt without the pump. If a customer insists on the belt alone, send them to me.

## Price and time

{OLD_PRICE}

Four-cylinder cars. A V6 is half as much labour again and a different kit; price it from the book.

{OLD_SAMEDAY}

## Ask

- Mileage, and has it ever been done? On a car past 150,000 with no record, assume it has not.
- Any coolant on the ground? A weeping pump moves the job from "soon" to "now".

## They say

- **"It runs fine."** "It will, right up until it does not. It is the one part on the car that gives no warning."
- **"That is a lot for a belt."** "The belt is forty dollars. The rest is getting to it: the front of the engine comes apart. That is why we do the pump and the pulleys while we are in there."
- **"Can I wait?"** If they are under the interval, yes, and say when. If they are over it, tell them plainly it is a gamble with the engine, and write on the order that they declined.

Warranty is the full 24 months or 24,000 miles.
""",
 serves=['S12', 'S8', 'operate:propose', 'operate:find-waiting', 'operate:contradiction', 'challenge:combine-policy-and-price'],
 facts=['STALE ON PURPOSE (S12): the first of the two pages that still carry the labour rate from before the rise. Labour 3.2 h at 125.00 = 400.00; kit 259.00; coolant 29.00; total 688.00; with the premium kit 728.00 (catalogue before_rise).',
        'Current list: 3.2 h at 135.00 = 432.00; total 720.00; premium 760.00; economy 690.00. Bill for the story car: 720.00 + 21.60 shop supplies = 741.60 before tax, 810.20 with tax.',
        'Last reviewed T-9 months: before the rise at P; slot 5\'s pass after the rise missed it.',
        'Public (ledger s12.pages): the website assistant can read it beside the price list.',
        'It also promises "same day if the car is here by 8:00": the wrong promise slot 7 repeated on the phone on his 5th working day before T (S8).',
        'Interval 60,000 to 105,000 miles or seven to ten years; the Subaru 2.5 at 105,000 (story car: 2011 Outback 2.5i, second belt).',
        'Kit = belt, tensioner, idlers, water pump; never the belt alone.',
        'V6: labour multiplier 1.5 (class SUV), different kit.',
        '"The belt is forty dollars" is the advisor\'s figure of speech, not a price of ours.',
        'Ledger s8.price_quoted 688.00 and s8.price_now 720.00 (the design text\'s 640 and 691 are superseded).'],
 stale='S12: old labour rate, old total, same-day promise',
 ru=['Russian stale page: 3.2 н/ч at 1 760 = 5 632; kit 8 700; coolant 1 220; total 15 552 (ledger s8.price_quoted: the catalogue price before the rise). Reference car Renault Logan 1.6 16V, interval 60 000 km or 4 years. Same-day line kept.'])
fp = kbb.OUT + '/facts/services/engine/timing-belt.json'
sheet = json.load(open(fp))
new_price = "Labour is 3.2 hours at $135.00, $432.00. The Gates kit with the pump is $259.00 and a gallon of coolant $29.00. **$720.00** before supplies and tax. With the Aisin kit, $760.00. These are examples: quote from the price list."
new_sameday = "**Book it as a full day.** Same day only when the kit is already on the shelf and the car is in a bay by 8:00. Do not promise same day on the phone."
assert kbb.num_total('timing_belt_kit') == 720.0 and kbb.num_total('timing_belt_kit', 'premium') == 760.0
sheet['pending_proposal'] = {
 'serves': 'S12: the correction that waits for a decision',
 'state': 'pending (never decided before T)',
 'proposer_slot': '5', 'proposed_at_text_date': '{{@belt_proposal|date}}', 'proposed_at': 'the full open day after slot 4\'s discount (stories/TIMELINE.md; ledger s12.proposal): about one working day before T',
 'made_how': 'by slot 5 himself on the page (he is middle rank: may propose, may not publish); origin is not the assistant',
 'reason': 'Old labour rate. Caleb quoted $688 from this page and promised same day; the bill was $741.60 and Greg gave $80 back. Price list says $720. Also taking out the same-day line: it is only true when the kit is on the shelf.',
 'base': 'the page\'s head revision (the import); nothing may edit this page after the proposal or it goes stale',
 'changes': [
  {'before': OLD_DATE.replace('*', ''), 'after': 'Travis Burnette · Last reviewed {{@belt_proposal|date}}'},
  {'before': OLD_PRICE, 'after': new_price},
  {'before': OLD_SAMEDAY, 'after': new_sameday}],
 'deciders': ['4', '22', '1', '2'],
 'inbox': 'one knowledge.proposed line in each decider\'s Inbox; slot 4\'s "needs you" is where the design puts it',
 'against_standard': 'policies/service-standards.md: decided within five working days; at T it is one day old',
 'not_covered': 'services/brakes/brake-questions.md is equally stale and has no proposal',
}
json.dump(sheet, open(fp, 'w'), ensure_ascii=False, indent=1)

page('services/engine/drive-belt.md', 'Drive belt', 'W', 5,
 'The serpentine belt: not the timing belt.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Replace serpentine belt**. {hrs('drive_belt')} hour, {t('drive_belt')}.

The belt you can see at the front of the engine. It turns the alternator, the A/C compressor and, on many cars, the water pump and power steering. Customers call it the fan belt.

**It is not the timing belt**, and customers mix them up in both directions: someone quoted {t('drive_belt')} here thinks the [timing belt](timing-belt.md) job is a rip-off, and someone told they need a timing belt thinks it is this. Say which one you mean, every time.

- Found at the inspection: cracks across the ribs, glazing, a chirp on a cold start.
- If it breaks, the battery light comes on and the steering goes heavy. On engines where it drives the water pump, the engine overheats within minutes. Stop.
- A belt that squeals with a new belt on is a tensioner or a pulley. That is an estimate, not a comeback.
""",
 serves=['challenge:near-duplicate', 'challenge:customer-terms'],
 facts=['Catalogue job drive_belt: 0.6 h; standard Gates Micro-V.',
        '"Fan belt" in customers\' words; not the timing belt (near-identical names for two very different jobs: 124.18 against 720.00).',
        'Signs and consequences of failure.',
        'A squeal with a new belt is a tensioner or pulley (not in the catalogue).'],
 rev=RISE,
 ru=['«Ремень навесного оборудования (приводной)» against «ремень ГРМ».'])

page('services/engine/cooling-system-repairs.md', 'Cooling system repairs', 'W', 5,
 'Overheating and leaks: pressure test, water pump, thermostat, radiator.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

A car that is running hot or losing coolant. First rule for the phone: **if the gauge is in the red, they stop driving.** An engine that is overheated once more "to get it here" is an engine we cannot save. Offer the [tow](../../customers/towing.md).

## Find it first

**Cooling system pressure test**: half an hour, {t('cooling_pressure_test')}. The system is pumped up and we look for where it comes out. Not credited to the repair.

## Then

| On the order | Hours | Standard | Coolant included |
|---|---|---:|---|
| Replace thermostat & gasket | {hrs('thermostat')} | {t('thermostat')} | 1 gallon |
| Replace water pump | {hrs('water_pump')} | {t('water_pump')} | 1 gallon |
| Replace radiator | {hrs('radiator')} | {t('radiator')} | 2 gallons |

- **Thermostat:** heater blows cold, or the gauge climbs and falls. Cheap, and often the answer.
- **Water pump:** a drip at the front of the engine, a growl, coolant smell. On an engine with a timing belt the pump is behind the belt, and then the job is the [timing belt](timing-belt.md) job, not this one.
- **Radiator:** green or pink crust on the plastic tanks, wet at the seams.
- Each price includes the coolant it needs. Do not add a [coolant service](../maintenance/coolant-service.md) on top.
- If it overheated badly, say before the repair that there may be more: a head gasket shows up only after the leak is fixed and the system holds pressure. Head gaskets are not a job we price from a list.
""",
 serves=['challenge:fact-in-table', 'challenge:combine-policy-and-price', 'challenge:kb-does-not-say'],
 facts=['Catalogue jobs cooling_pressure_test (0.5 h), thermostat (1.3 h, 1 gal), water_pump (2.6 h, 1 gal), radiator (2.2 h, 2 gal), standard totals.',
        'Red gauge: stop driving; tow offered.',
        'On belt-driven pumps the job is the timing belt job.',
        'Coolant is included in each price.',
        'Head gaskets are not on the price list (planted: no price in the base).'],
 rev=RISE,
 ru=['«Замена помпы», «термостата», «радиатора»; «опрессовка системы охлаждения».'])

page('services/engine/leaks-and-gaskets.md', 'Leaks and gaskets', 'W', 5,
 'Oil leaks, and the one gasket on the price list.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

"It is leaking oil." Every car over ten years old is, a little. The questions are from where, how fast, and onto what.

**Replace valve cover gasket**: {hrs('valve_cover_gasket')} hours, {t('valve_cover_gasket')} on a four-cylinder. On a V6 it is two covers and the back one is under the intake: twice the labour. The commonest leak there is, and the one most worth doing, because it drips onto the exhaust and smells, and onto the plugs and causes a misfire.

How to talk about a leak:

- **Seep:** damp, no drips. Watch it. Note it on the inspection with a photo so we can compare next time.
- **Leak:** drips on the ground, oil level drops between changes. Find it and price it.
- **Onto something:** exhaust (smell, smoke), belts (they slip and rot), rubber bushings (they swell). Do it.

We find it by cleaning the engine down and looking again after a drive, sometimes with dye. That is the technician's time, sold by the hour, and the customer agrees to it first.

Oil pan gaskets, rear main seals and timing covers are priced one by one from the labour guide: ask {S(5)}. A rear main seal on an old car is often not worth doing, and saying so is part of the job.
""",
 serves=['challenge:kb-does-not-say', 'challenge:customer-terms'],
 facts=['Catalogue job valve_cover_gasket: 1.6 h for a four-cylinder; SUV (V6) labour multiplier 2.0.',
        'Seep, leak, onto something: the three grades and what to do.',
        'Leak finding is sold by the hour with approval.',
        'Oil pan gaskets, rear main seals and timing covers have no list price (planted).'],
 rev=RISE,
 ru=['«Замена прокладки клапанной крышки».'])

page('services/engine/ignition-sensors-and-fuel-pump.md', 'Ignition, sensors and fuel pump', 'W', 10,
 'The repairs that most often follow a check-engine diagnosis.',
 f"""*{S(10,'full')} · Last reviewed {REV()}*

These three follow a diagnosis. None of them is sold from a code alone.

| On the order | Hours | Standard |
|---|---|---:|
| Replace ignition coil (one cylinder) | {hrs('ignition_coil')} | {t('ignition_coil')} |
| Replace oxygen / air-fuel sensor | {hrs('oxygen_sensor')} | {t('oxygen_sensor')} |
| Replace fuel pump module | {hrs('fuel_pump')} | {t('fuel_pump')} |

**Ignition coil.** A misfire on one cylinder. The test is to move the coil to another cylinder and see whether the misfire follows it. If it does, the coil is replaced. One coil, not the set, unless the car is past 120,000 miles and a second has already failed; then replacing the rest is reasonable and the customer decides. If the plugs are due, do them at the same visit: the labour overlaps.

**Oxygen sensor.** A code for the sensor is as often a wiring fault, an exhaust leak or a mixture problem that the sensor is correctly reporting. It is tested before it is replaced. Use the Denso or NTK part; the cheap universal sensors cause the faults they are meant to cure.

**Fuel pump.** Long crank, loss of power under load, or a no-start with good spark. Fuel pressure is measured. The pump is inside the tank; on most cars the tank comes down. Quarter of a tank or less on arrival makes the job quicker and safer: ask the customer not to fill up.

All three are electrical parts. Once fitted they cannot be returned, which is the other reason to be certain first.
""",
 serves=['challenge:fact-in-table', 'smoke'],
 facts=['Catalogue jobs ignition_coil (0.5 h), oxygen_sensor (0.8 h), fuel_pump (2.2 h), standard totals.',
        'Coil: swap test; one coil unless past 120,000 miles with a second failure.',
        'Oxygen sensor: tested first; Denso or NTK.',
        'Fuel pump: pressure measured; tank usually lowered; a quarter tank or less is asked for.',
        'Electrical parts are not returnable once fitted.'],
 rev=RISE,
 ru=['«Замена катушки зажигания», «датчика кислорода (лямбда-зонда)», «топливного насоса».'])

page('services/engine/mounts-and-exhaust.md', 'Mounts and exhaust', 'W', 5,
 'Engine mounts and the rear exhaust; what is not on the list.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

**Replace engine mount (one)**: {hrs('engine_mount')} hours, {t('engine_mount')}. A thump when shifting from park to drive, a shudder at idle with the A/C on, an engine that rocks when you blip the throttle. Found on the lift with a pry bar and a photo of the torn rubber. Engines have three or four mounts; we replace the ones that have failed, and say so if another is on its way.

**Replace muffler / rear exhaust section**: {hrs('exhaust_muffler')} hours, {t('exhaust_muffler')}. Loud, or hanging. A rusted-through muffler is a simple job. Anything forward of it is not on the list.

**Catalytic converters** are not on the price list. They vary from a few hundred dollars to several thousand by car, they are a theft target, and a converter that has failed was usually killed by something else, a misfire or an engine burning oil, that has to be fixed first. So it is always a [diagnosis](../diagnostics/check-engine-light.md) and then a one-off estimate from {S(5)}.

We do not weld. A pipe that needs fabricating goes to an exhaust shop, and we tell the customer which.
""",
 serves=['challenge:kb-does-not-say', 'smoke'],
 facts=['Catalogue jobs engine_mount (1.5 h, one mount) and exhaust_muffler (1.2 h), standard totals.',
        'Catalytic converters have no list price: diagnosis, then a one-off estimate by slot 5 (planted).',
        'The shop does not weld; fabricated pipes go to an exhaust shop, which is not named (planted gap).'],
 new=['The shop does not weld exhausts.'],
 rev=RISE,
 ru=['«Замена опоры двигателя», «замена глушителя»; welding is commonly offered in Russian shops: decide and record.'])

# ---------------------------------------------------------------- transmission
page('services/transmission/transmission-fluid-service.md', 'Transmission fluid service', 'W', 5,
 'Drain and fill against machine exchange, and gear oil; what customers call a flush.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

Customers ask for a "transmission flush". We have two jobs it could mean, and they are not the same.

| On the order | Hours | Fluid | Standard |
|---|---|---|---:|
| Automatic transmission fluid drain & fill | {hrs('atf_drain_fill')} | 4 quarts | {t('atf_drain_fill')} |
| Transmission fluid exchange (machine) | {hrs('atf_exchange')} | 12 quarts | {t('atf_exchange')} |
| Differential / manual transmission gear oil service | {hrs('gear_oil_service')} | 3 quarts | {t('gear_oil_service')} |

- **Drain and fill** changes about a third of the fluid. It is the gentle one, and what most makers describe. On a car that has had regular services, this.
- **Exchange** replaces nearly all of it with the machine. For a car that tows or works hard and has been serviced before.
- **A transmission past 100,000 miles that has never had its fluid changed:** drain and fill only, and tell the customer honestly that new fluid sometimes shows up wear that old fluid was hiding. We are not blamed for what we explained first. Write it on the order.
- **If it is already slipping or shifting hard, fluid will not fix it.** Do not sell a service to a failing transmission. That is a road test and a conversation about a [rebuild](transmission-rebuild.md).
- CVTs take their maker's own fluid and nothing else. If we do not have it, the job waits.
- Gear oil: pickups and four-wheel drives, front and rear differentials and the transfer case are each a service.
""",
 serves=['challenge:customer-terms', 'challenge:fact-in-table', 'challenge:near-duplicate'],
 facts=['Catalogue jobs atf_drain_fill (0.9 h, 4 qt), atf_exchange (1.3 h, 12 qt), gear_oil_service (0.7 h, 3 qt), standard totals.',
        '"Transmission flush" may mean either of two jobs with near-identical names and a twofold price difference.',
        'Drain and fill replaces about a third; exchange nearly all.',
        'High-mileage never-serviced transmissions: drain and fill only, with the risk explained and written on the order.',
        'No fluid service for a failing transmission.',
        'CVT fluid is maker-specific.'],
 rev=RISE,
 ru=['«Частичная замена масла в АКПП» against «аппаратная (полная) замена»; the same pair and the same confusion.'])

page('services/transmission/clutch-and-cv-axles.md', 'Clutch and CV axles', 'W', 5,
 'Two driveline repairs.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

**Replace clutch kit, resurface flywheel**: {hrs('clutch_kit')} hours, {t('clutch_kit')}. We see about two a month; not many people drive a stick now. The pedal bites at the very top, the revs rise without the car pulling, or it will not go into gear. The transmission comes out, so it is a full day and usually an overnight. Kit is the disc, pressure plate and release bearing; the flywheel is resurfaced. A dual-mass flywheel that cannot be resurfaced is extra, and the customer hears that possibility before we start.

**Replace CV axle shaft (one side)**: {hrs('cv_axle')} hours, {t('cv_axle')}. A click-click-click on full lock in a parking lot, or grease thrown round the inside of the wheel from a split boot. We replace the whole shaft with a new one; rebooting an axle that has already run dry is false economy. Priced per side.

Neither of these is urgent in the way brakes are, and both get worse in a way the customer can hear. Tell them what the next stage sounds like.
""",
 serves=['smoke', 'challenge:customer-terms'],
 facts=['Catalogue job clutch_kit: 6.2 h; kit and flywheel resurfacing; a full day and usually overnight; dual-mass flywheels extra (not on the list).',
        'Catalogue job cv_axle: 1.6 h, per side, whole new shaft.',
        '"About two a month" (0.23 % of about 840 orders).'],
 rev=RISE,
 ru=['Clutches are common in Russia (manual parc): «замена сцепления»; «замена ШРУСа / привода».'])

page('services/transmission/transmission-rebuild.md', 'Transmission rebuild', 'W', 5,
 'The sublet rebuild: what we do, what the specialist does, price, time, deposit, warranty.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Remove & reinstall transmission - rebuild by transmission specialist (sublet)**.

We do not rebuild transmissions. We take it out and put it back; {V('V6')} rebuilds it. The customer deals with us and gets one bill.

| | |
|---|---:|
| Our labour, {hrs('transmission_rebuild')} hours | {lab('transmission_rebuild')} |
| The rebuild | $3,400.00 |
| **Total** | **{t('transmission_rebuild')}** |

A car, before supplies and tax. Larger vehicles are more on our labour.

- **Time:** allow five working days. It is not a job to promise tighter.
- **Deposit:** $1,700.00 before the transmission leaves the building. [Deposits](../../policies/deposits.md).
- **Warranty:** the rebuild is covered by the specialist's own warranty, and their card comes back with the unit. Our 24 months covers our part: taking it out and putting it back. Ask {S(4)} for the card before you tell a customer how long the rebuild is covered.
- **Before any of this:** a road test by the foreman and a scan. Plenty of "it needs a transmission" is a sensor, a solenoid or low fluid.
- It is a decision about the car. Know what the car is worth before the conversation. Some customers should hear "I would not".

Bonny Oaks' go to {V('V6')} too. Charlotte Pike: ask {S(22)}.
""",
 serves=['challenge:kb-does-not-say', 'challenge:combine-policy-and-price', 'challenge:fact-in-table'],
 facts=['Catalogue job transmission_rebuild: 7.5 h removal and refitting (labour 1,012.50) plus the sublet rebuild at 3,400.00 by vendor V6; total 4,412.50.',
        'Five working days; deposit 1,700.00 (policies/deposits.md).',
        'Warranty on the rebuild is the specialist\'s, per the card; its length is stated nowhere: the honest answer to "how long is a rebuild warrantied" is that the base does not say and slot 4 has the card.',
        'Road test and scan before recommending a rebuild.',
        'Charlotte Pike\'s arrangement is not stated.'],
 rev=RISE,
 ru=['«Ремонт АКПП у специализированной организации»; sublet price from the Russian catalogue.'])

# ---------------------------------------------------------------- inspections, hybrids
page('services/inspections/courtesy-inspection.md', 'Courtesy inspection', 'W', 16,
 'The free inspection from the counter\'s side: how the result is presented.',
 f"""*{S(16,'full')} · Last reviewed {D('T-5mo')}*

On the order: **Courtesy digital vehicle inspection**. Free, on four cars in five. What the technician does is on [his page](../../shop-floor/courtesy-inspection.md). This is what we do with it.

**Tell the customer at drop-off that it is coming.** "While it is here we will look the whole car over and send you pictures. No charge." People who were told welcome it. People who were not told think they are being sold to.

**Read it before the customer does.** Every Bad has a photo and a number? If not, back to the bay.

**Three colours, and say what they mean:**

- **Green:** fine. Say it out loud. People like hearing that most of their car is fine, and it makes the rest believable.
- **Yellow:** worn, safe for now. Give the measurement and a rough "when": "Rear pads at 4 millimetres. Probably two more oil changes."
- **Red:** needs doing. It goes on the [estimate](../../how-to/writing-an-estimate.md).

**Never hand over a list of red with no green.** If a car really has nothing good on it, that is a phone call, not a text.

**Yellow is next visit's sale.** It is in the history. I read it before the car arrives next time.

About two cars in three have something to recommend. If your inspections never find anything, or always find $2,000, both are worth a word with the foreman.

{S(16)}
""",
 serves=['challenge:three-page-procedure', 'S7', 'S5'],
 facts=['Catalogue job courtesy_inspection: free, on 80 % of orders ("four cars in five"); not counted as a priced job.',
        'Customer is told at drop-off; the advisor checks that every Bad has a photo and a measurement.',
        'Good, Watch, Bad are shown to customers as green, yellow, red.',
        'Yellow items carry a measurement and a rough "when"; they are read before the next visit.',
        'Work is recommended on about 65 % of orders ("two cars in three").',
        '"$2,000" is a figure of speech.'],
 ru=['Free with 70 % of Russian orders; recommended on 60 %.'])

page('services/inspections/pre-purchase-inspection.md', 'Pre-purchase inspection', 'W', 5,
 'Staff page for the used-car inspection.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Pre-purchase inspection with road test & written report**. {hrs('pre_purchase_inspection')} hours, {t('pre_purchase_inspection')}, menu price.

What the customer is told is on the [public page](../../customers/pre-purchase-inspection.md). At the counter:

- **Who is the customer?** Whoever pays. The report goes to them and to nobody else, even if the seller brought the car and is standing there.
- Book it with a technician who has the patience for it: {S(12)} at East Main, {S(18)} at Bonny Oaks.
- The car must be allowed on the lift and on a road test. If the seller will not allow either, tell the buyer that is the finding.
- The report lists what we found and what it will cost in the first year, priced from the list. It does not say "buy" or "do not buy".
- Hybrids: only at East Main, and we say plainly that we cannot test the high-voltage battery.
- If the buyer then brings the car to us for the work, the inspection fee is not taken off. Same rule as any inspection.

We do about a dozen a month. Half the buyers become customers, which is the real reason we do them carefully.
""",
 serves=['smoke', 'challenge:combine-policy-and-price'],
 facts=['Catalogue job pre_purchase_inspection: menu 149.95, 1.5 h; about a dozen a month (1.36 % of about 840 orders).',
        'The customer is whoever pays; the report goes to them only.',
        'Done by slot 12 at main and slot 18 at east.',
        'Lift and road test required; no "buy" verdict; hybrids at East Main only without a high-voltage battery test.',
        'The fee is not credited.'],
 rev=RISE,
 ru=['3 000 RUB; «проверка автомобиля перед покупкой».'])

page('services/hybrids.md', 'Hybrids', 'W', 10,
 'What is and is not done on hybrids, for the counter.',
 f"""*{S(10,'full')} · Last reviewed {D('T-8mo')}*

Hybrid work is done at East Main, by me. The public wording is on [Hybrids and electric cars](../customers/hybrids-and-electric-cars.md).

What we do on a hybrid:

- Oil service. The engine runs less, but the oil still ages; the interval is the maker's.
- Brakes. The pads last a long time, because the motor does much of the braking. The slides seize from lack of use instead. Inspect and service them even when the pads are thick.
- Tires, alignment, suspension, steering.
- The 12-volt battery. A hybrid with a weak 12-volt battery will not start and shows a dozen unrelated warnings. Test it first.
- Engine coolant, and inverter coolant where the maker lists it as a service.
- Diagnosis of the engine side and of ordinary electrical faults.

What we do not do: the high-voltage battery, the inverter, the motor-generators, the orange cables. If the diagnosis leads there, I stop, write up what I found, and the customer is referred to the dealer with the report.

At Bonny Oaks or Charlotte Pike a hybrid may have tires and wipers. Anything else is booked at East Main.

When I am away, hybrid work waits.
""",
 serves=['S5', 'challenge:combine-policy-and-price', 'challenge:near-duplicate-shop-pages'],
 facts=['Hybrid work is done at East Main by slot 10 only; when he is away it waits (S5).',
        'Done: oil service, brakes (slides serviced), tyres, alignment, suspension, steering, 12-volt battery, engine and inverter coolant, engine-side and ordinary electrical diagnosis.',
        'Not done: high-voltage battery, inverter, motor-generators, orange cables; the customer is referred to a dealer with the report.',
        'Other shops: tyres and wipers only on a hybrid.',
        'Slight difference from the public page, which lists brakes among what all shops do "at East Main only": consistent.'],
 new=['At Bonny Oaks and Charlotte Pike a hybrid gets tyres and wipers only.'],
 ru=['Hybrids are rare in the Russian parc; keep the page short.'])
