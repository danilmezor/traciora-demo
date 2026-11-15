from kbb import *
import kbb
REV = lambda: D('@price_rise+3wd:main')
RISE = [(4, '@price_rise+3wd:main', 'Travis\'s pass after the price rise: every dollar figure brought to the new list (proposed by slot 5, approved by slot 4); message: "New labour rate."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})]
RISE16 = [(4, '@price_rise+3wd:main', 'Angie\'s pass after the price rise: every dollar figure brought to the new list (proposed by slot 16, approved by slot 4); message: "New labour rate."', {'kind': 'proposal', 'proposer_slot': '16', 'approver_slot': '4'})]

# ---------------------------------------------------------------- tires
page('services/tires/rotation-balance-and-flat-repair.md', 'Rotation, balance and flat repair', 'W', 5,
 'The three small tire jobs.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

All three are menu prices, done by the lube and tire bay while the customer waits.

| Job | Time | Price |
|---|---|---:|
| Tire rotation | 20 minutes | {t('tyre_rotation')} |
| Balance 4 wheels | 35 minutes | {t('wheel_balance')} |
| Flat repair: patch-plug, rebalance | 20 minutes | {t('tyre_repair')} |

- **Rotation** with every other oil change. Nearly one order in four has one on it. Lugs are torqued by hand and the customer is told so.
- **Balance** when the wheel shakes at 55 to 70 mph. A shake only under braking is rotors, not balance: [Brake inspection](../brakes/brake-inspection.md).
- **Flat repair** only in the tread, only a hole smaller than a pencil, only from the inside with a patch-plug. Never a plug from outside, never the sidewall or shoulder. If it cannot be repaired the customer is shown why, and the next page is [New tires](new-tires-and-tpms.md).
- A tire driven on flat for any distance is usually ruined inside. Look before you promise a repair.
""",
 serves=['smoke', 'challenge:fact-in-table'],
 facts=['Menu jobs tyre_rotation (0.3 h), wheel_balance (0.6 h), tyre_repair (0.3 h).',
        'Rotation rides on 23.4 % of orders ("nearly one in four").',
        'Balance for a shake at 55 to 70 mph; a shake under braking is rotors.',
        'Repair rules: tread only, small hole, patch-plug from inside.'],
 rev=RISE,
 ru=['Russian: балансировка and ремонт прокола are per wheel; rotation is rare (0.5 % of orders).'])

page('services/tires/alignment.md', 'Alignment', 'W', 5,
 'Four-wheel alignment: when, price by vehicle class, which rack.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Four-wheel alignment**. One hour, {t('wheel_alignment')} for a car or SUV. Pickups {t('wheel_alignment', cls='truck')}, vans {t('wheel_alignment', cls='van')}. Menu price, with the before-and-after printout.

Customers say "front end alignment". It is all four wheels on anything built this century.

When:

- With new tires. Always offer it; a bad alignment eats a new set in a year.
- After any steering or suspension part is replaced: tie rods, control arms, struts. It is part of that job's estimate, not an afterthought.
- The car pulls, the steering wheel is off-centre, or a tire is worn on one edge.
- After a kerb or a pothole hard enough to remember.

We cannot align a car with worn parts: the settings will not hold. If the technician finds a loose tie rod or ball joint on the rack, the alignment stops and the customer gets an estimate. They pay for the alignment once, after the repair.

Crew-cab and long-wheelbase trucks go on the long rack at East Main.
""",
 serves=['challenge:customer-terms', 'challenge:combine-policy-and-price'],
 facts=['Catalogue job wheel_alignment: menu 119.95; multipliers SUV 1.0, truck 1.15 (137.94), van 1.25 (149.94).',
        '"Front end alignment" in customers\' words.',
        'Offered with new tyres; included in estimates for tie rods, control arms and struts; symptoms listed.',
        'An alignment stopped for worn parts is charged once, after the repair.',
        'Long vehicles go to East Main.'],
 rev=RISE,
 ru=['«Сход-развал», 3 000 RUB for two axles.'])

page('services/tires/new-tires-and-tpms.md', 'New tires and tire-pressure sensors', 'W', 5,
 'Selling and fitting tires; the fees; TPMS sensors.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

## New tires

On the order: **Mount & balance 4 new tires**, plus the tires. Mounting and balancing four is {lab('new_tyres_fitted')}. On the common sedan size a set fitted comes to:

| Tier | Tire | Each | Set of four, fitted |
|---|---|---:|---:|
| Economy | Milestar | {part('new_tyres_fitted',0,'economy')} | {t('new_tyres_fitted','economy')} |
| Standard | Hankook Kinergy | {part('new_tyres_fitted',0,'standard')} | {t('new_tyres_fitted','standard')} |
| Premium | Michelin Defender | {part('new_tyres_fitted',0,'premium')} | {t('new_tyres_fitted','premium')} |

The fitted price includes $19.40 of tire fees for four. Every other size is a call to {S(9)} for price and arrival.

- Read the size off the sidewall, not off the door sticker; cars get re-shod.
- We sell tires in pairs or fours, not singles, unless the other three are nearly new.
- Offer the [alignment](alignment.md). Say why.
- Tires arrive next morning in Chattanooga. **In Nashville they come Tuesdays and Fridays.**
- We do not fit tires the customer brings if they are more than six years old by the date code.

## Tire-pressure sensors

**Replace TPMS sensor & relearn (one wheel)**: half an hour, {t('tpms_sensor')}. The batteries inside die at about ten years, one wheel after another. When one goes on a ten-year-old car, tell the customer the others are the same age. Cheapest to do with new tires, when the tire is off anyway.

## Seasonal changeover

A few customers who drive to the mountains keep winter tires. Changeover is on the price list. Storage we do for a handful of sets; ask {S(9)} before offering it.
""",
 serves=['challenge:fact-in-table', 'challenge:combine-kb-and-data', 'challenge:kb-does-not-say'],
 facts=['Catalogue job new_tyres_fitted: menu labour 100.00 for four; tyres 215/55R17 by tier (Milestar, Hankook Kinergy, Michelin Defender); fees 19.40 included.',
        'Other sizes are priced by slot 9 (not on the page).',
        'Sold in pairs or fours; alignment offered; customer tyres over six years old refused.',
        'Arrival: next morning in Chattanooga; Tuesdays and Fridays in Nashville (contradicts the public tyres page\'s "most sizes arrive the next morning" for Nashville callers).',
        'TPMS sensor: 0.5 h; batteries last about ten years.',
        'Seasonal changeover and storage exist and are rare (under 0.2 % of orders).'],
 rev=RISE,
 ru=['Write the Russian tyre pages from the Russian catalogue: шиномонтаж 4 колёс 3 000, сезонное хранение 3 000 за сезон; two seasons at six times the yearly mean.'])

# ---------------------------------------------------------------- diagnostics
page('services/diagnostics/check-engine-light.md', 'Check engine light', 'W', 10,
 'How a check-engine job is booked and explained, in the diagnostician\'s exact voice.',
 f"""*{S(10,'full')} with {S(5,'full')} · Last reviewed {REV()}*

On the order: **Check engine light - scan, test & diagnose (1 hr)**. One hour, {t('check_engine_diag')}.

## What the hour is

1. Read the stored codes and the freeze-frame data: what the engine was doing when the fault set.
2. Test the circuit or component the code points to. A code names a system, not a part. P0171 says the engine is running lean. It does not say why.
3. Confirm the cause, so that the part we recommend is the part that failed.
4. Write down what was tested, what it showed and what that rules out.

Most faults are found inside the hour. An intermittent fault may not be: it has to be present to be tested.

## Booking

- Into the diagnostic column: {S(10)} at East Main, about four a day; {S(18)} at Bonny Oaks, two.
- Ask: is the light steady or flashing; does the car drive differently; when did it start; was anything done to the car just before. Write the answers on the order. They save me twenty minutes.
- A flashing light with a shaking engine is a misfire. Advise the customer to drive as little as possible.
- The parts store will read the code for free. Customers arrive with a code and a part already bought. Explain, politely, that we still diagnose: we do not fit parts on a code.

## Money

- The fee is charged whether or not the repair is done here and is not credited: [Diagnostic and inspection fees](../../policies/diagnostic-fees.md).
- More time needs the customer's approval first. Say what has been ruled out so far.
- Do not quote the repair before the diagnosis. The same code has a $25 cause and a $1,300 cause.

Electrical faults without a light: [Electrical diagnosis](electrical-diagnosis.md).
""",
 serves=['S5', 'challenge:combine-policy-and-price', 'challenge:customer-terms'],
 facts=['Catalogue job check_engine_diag: 1.0 h at the posted hour; carried by 11.4 % of orders.',
        'Four steps: codes and freeze-frame, test the circuit, confirm the cause, write what was tested and ruled out (slot 10\'s way of explaining: cast).',
        'Booked into the diagnostic column: slot 10 about four a day at main; slot 18 two at east.',
        'Questions for the customer: steady or flashing, drives differently, when, what was done before.',
        'Fee not credited; more time needs approval; no repair quote before diagnosis.',
        '"$25" and "$1,300" are illustrative causes (a fuel cap and a catalytic converter in the research\'s list), not shop prices.',
        'Voice: slot 10: ordered, exact, no slang.'],
 rev=RISE,
 ru=['«Компьютерная диагностика двигателя», 0.5 н/ч, 1 200 RUB.'])

page('services/diagnostics/electrical-diagnosis.md', 'Electrical diagnosis', 'W', 13,
 'Electrical faults without a warning light.',
 f"""*{S(13,'full')}, as told to {S(5)} · Last reviewed {REV()}*

On the order: **Electrical system diagnosis**. We sell an hour and a half to start, {t('electrical_diag')}.

This is for the fault with no code to follow: a battery that is flat every Monday, a window that works when it wants to, lights that flicker, a blower that quit, something that only happens in the rain.

- Electrical work is slow because it is honest work with a meter, one circuit at a time. I would want to check it before I say what it is.
- Ask the customer when it happens and what else is on when it does. "Every time" and "only when it rains" are different faults.
- A battery that goes flat: test the battery first. It is free and it is the battery half the time. If the battery is good, it is a drain, and a drain test means the car stays overnight.
- Anything added to the car matters: a remote starter, a stereo, a trailer plug, a dash camera. Ask, and write it down.
- If an hour and a half does not find it, I stop and the advisor calls. I say what I have ruled out.

At East Main it comes to me, or to {S(10)} when it is in the modules. At Bonny Oaks, {S(18)}. Hybrids are {S(10)}'s only.
""",
 serves=['smoke', 'challenge:customer-terms'],
 facts=['Catalogue job electrical_diag: 1.5 h.',
        'For faults with no code: drains, intermittent windows, flickering lights, blowers, wet-weather faults.',
        'Battery test first (free); a drain test keeps the car overnight.',
        'Aftermarket additions are asked about.',
        'Who: slot 13 at main, slot 10 for module faults and hybrids, slot 18 at east.',
        'Voice: slot 13, slow and courteous, dictated to slot 5 (he "does not chat").'],
 rev=RISE,
 ru=['«Поиск неисправности электрооборудования», 1.5 н/ч.'])

page('services/diagnostics/noises-and-vibrations.md', 'Noises and vibrations', 'W', 5,
 'How a noise complaint is taken and inspected.',
 f"""*{S(5,'full')} · Last reviewed {REV()}*

On the order: **Steering & suspension inspection - noise / vibration**. Half an hour, {t('suspension_diag')}, menu price.

A noise is the hardest thing to book, because the customer's "clunk" is the technician's "which clunk". Get it out of them before the car arrives:

| Ask | Because |
|---|---|
| Over bumps, or on smooth road? | Bumps: links, bushings, struts. Smooth: bearings, tires |
| Turning, or straight? | Turning: CV axle, wheel bearing, strut mount |
| Braking? | Then it is a [brake inspection](../brakes/brake-inspection.md) |
| Faster with speed? | A hum that rises with speed is a bearing or a tire |
| Front or back, left or right? | They usually know |
| Cold only? | Bushings and belts complain in the cold |

Then offer the ride: "Can you take a short drive with the technician when you drop it off?" Two minutes in the car beats ten minutes of description.

What it usually turns out to be, in order: sway bar links, struts or shocks, a wheel bearing, control arm bushings. See [Front-end parts](../suspension/front-end-parts.md).

A vibration at highway speed with nothing loose is a balance: [Rotation, balance and flat repair](../tires/rotation-balance-and-flat-repair.md).
""",
 serves=['challenge:fact-in-table', 'challenge:customer-terms'],
 facts=['Catalogue job suspension_diag: menu 49.95, 0.5 h.',
        'Six questions with what each answer points to.',
        'A ride with the technician is offered at drop-off.',
        'Usual causes in order: sway bar links, struts or shocks, wheel bearing, control arm bushings.'],
 rev=RISE,
 ru=['«Диагностика ходовой части», 800 RUB; carried by 12.9 % of Russian orders (roads).'])

# ---------------------------------------------------------------- suspension
page('services/suspension/struts-and-shocks.md', 'Struts and shocks', 'W', 16,
 'Front struts and rear shocks: how they are found, sold in pairs, and often deferred.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

| On the order | Hours | Economy / Standard / Premium |
|---|---|---|
| Replace front strut assemblies (pair) | {hrs('front_struts_pair')} | {t('front_struts_pair','economy')} / {t('front_struts_pair')} / {t('front_struts_pair','premium')} |
| Replace rear shock absorbers (pair) | {hrs('rear_shocks_pair')} | {t('rear_shocks_pair','economy')} / {t('rear_shocks_pair')} / {t('rear_shocks_pair','premium')} |

Always in pairs across the axle. Front struts need an [alignment](../tires/alignment.md) afterwards, {t('wheel_alignment')}; put it on the estimate. Rear shocks do not.

**How they are found.** Nobody phones to say their shocks are worn; it happens too slowly to notice. The technician sees oil on the shock body at the inspection, or the tires are wearing in cups. Photo of the wet shock, every time.

**How to say it.** "This one is leaking. It is not dangerous this week. It makes the car take longer to stop on a rough road and it wears the tires. I would do them in the next couple of months."

**It is the job people put off**, and that is fine. Mark it declined and deferred. It comes back as a reminder, and when they are next in for an oil change it is the first thing I mention, at drop-off. About half of them say yes the second time.

Customers call all of them "shocks". A strut is a shock that also holds the car up, which is why it costs more and needs the alignment.

{S(16)}
""",
 serves=['S7', 'challenge:customer-terms', 'challenge:fact-in-table'],
 facts=['Catalogue jobs front_struts_pair (2.6 h) and rear_shocks_pair (1.2 h), three tier totals each.',
        'Sold in pairs; front struts need an alignment (119.95) on the estimate; rear shocks do not.',
        'Found at the inspection (oil on the body, cupped tyres); photo required.',
        'Often declined and deferred; raised again at the next drop-off.',
        'S7: the customer declined rear shocks at 339.28 (standard) and asked to book them at T-3 days; the answer to her uses this page for the job and the price list for the price.',
        '"About half say yes the second time" is the advisor\'s impression, not a ledger row.'],
 rev=RISE16,
 ru=['«Замена амортизаторов»; rear pair 11 720 RUB (catalogue.md).'])

page('services/suspension/front-end-parts.md', 'Front-end parts', 'W', 16,
 'Sway bar links and bushings, control arms, ball joints, tie rods.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

The parts that clunk. All found on the lift, all shown to the customer by moving the wheel or the bar while they watch or on a short video.

| On the order | Hours | Standard | Priced | Alignment after? |
|---|---|---:|---|---|
| Replace front sway bar links | {hrs('sway_bar_links')} | {t('sway_bar_links')} | Pair | No |
| Replace front sway bar bushings | {hrs('sway_bar_bushings')} | {t('sway_bar_bushings')} | Set | No |
| Replace outer tie rod end | {hrs('outer_tie_rod')} | {t('outer_tie_rod')} | Each side | **Yes** |
| Replace lower ball joint | {hrs('ball_joint')} | {t('ball_joint')} | Each side | **Yes** |
| Replace front lower control arm | {hrs('lower_control_arm')} | {t('lower_control_arm')} | Each side | **Yes** |

- Links are the cheap, common one: a rattle over small bumps. Replace both.
- A loose tie rod or ball joint is a safety item. Say so in those words, once, without drama: "This is the joint that steers the wheel. I would not leave it."
- On many cars the ball joint comes with the control arm; then the arm is the job and the ball joint line is not used.
- Add the alignment, {t('wheel_alignment')}, to anything marked Yes. One alignment covers everything done that visit.
- Standard is Moog. On a car over 150,000 miles, do not talk anyone into the original part.

{S(16)}
""",
 serves=['challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Five catalogue jobs with hours, standard totals, pricing unit and whether an alignment follows: sway_bar_links (pair, no), sway_bar_bushings (set, no), outer_tie_rod (side, yes), ball_joint (side, yes), lower_control_arm (side, yes).',
        'One alignment covers everything done in a visit.',
        'Tie rods and ball joints are safety items.',
        'Standard brand Moog.',
        'A combined quote needs this table and the alignment price: for example both outer tie rods plus alignment = 2 x 162.55 + 119.95 = 445.05 before supplies and tax.'],
 rev=RISE16,
 ru=['«Стойки стабилизатора», «рулевые наконечники», «шаровые опоры», «рычаги»; much more common in Russia (suspension 12.8 % of orders).'])

page('services/suspension/wheel-bearings-and-steering-racks.md', 'Wheel bearings and steering racks', 'W', 16,
 'Two bigger jobs: the humming bearing and the leaking rack.',
 f"""*{S(16,'full')} · Last reviewed {REV()}*

**Replace front wheel bearing / hub assembly (one side)**: {hrs('wheel_bearing')} hours, {t('wheel_bearing')}. The hum that gets louder with speed and changes when the car leans in a curve. Priced per side; we replace the one that is noisy. The technician confirms which side on a road test, because customers and advisors both guess wrong.

**Replace rack & pinion assembly**: {hrs('steering_rack')} hours, {t('steering_rack')} with a new aftermarket rack, {t('steering_rack','economy')} remanufactured. Fluid on the garage floor under the front, steering that is heavy or notchy. It is a half-day job and needs an alignment after. Parts are usually next-day, so this is booked, not squeezed in. A remanufactured rack carries a core.

With either, the customer is deciding about a car, not a part. If the car is worth $3,000 and the rack is $1,200, say what you would want to know in their place, and let them think. I have never lost a customer by telling them not to spend money.

{S(16)}
""",
 serves=['smoke', 'challenge:customer-terms'],
 facts=['Catalogue job wheel_bearing: 1.8 h, per side; the side is confirmed on a road test.',
        'Catalogue job steering_rack: 4.2 h; standard new aftermarket, economy reman (core); alignment after; parts next-day.',
        '"$3,000" and "$1,200" are round illustrative figures in the advisor\'s speech.'],
 rev=RISE16,
 ru=['«Замена ступичного подшипника», «замена рулевой рейки» (ремонт рейки is a common cheaper alternative in Russia: say whether the shop offers it).'])

# ---------------------------------------------------------------- ac
page('services/ac/ac-check-and-recharge.md', 'A/C check and recharge', 'W', 13,
 'The summer job: performance check, the two refrigerants, what a recharge can and cannot fix.',
 f"""*{S(13,'full')} with {S(5,'full')} · Last reviewed {REV()}*

From May to August this is two and a half times its usual volume, and half of those calls start with "it just needs some freon".

## The jobs

| On the order | Hours | Price |
|---|---|---:|
| A/C performance check | {hrs('ac_performance_check')} | {t('ac_performance_check')} |
| A/C evacuate & recharge (R-134a) | {hrs('ac_recharge')} | {t('ac_recharge')} |
| A/C evacuate & recharge (R-1234yf) | {hrs('ac_recharge_1234yf')} | {t('ac_recharge_1234yf')} |
| A/C evaporator cleaning & deodorizer service | {hrs('ac_evaporator_cleaning')} | {t('ac_evaporator_cleaning')} |

## Which refrigerant

The label under the hood says. As a guide, cars up to about 2016 use R-134a and most from 2017 use R-1234yf. The newer one costs us several times more a pound; that is the whole price difference, and the customer should hear that it is not our choice.

**R-1234yf is kept at East Main only.** A newer car at Bonny Oaks is sent to East Main or waits for a bottle on the 1:00 run. Charlotte Pike: ask before you book one.

## How to sell it straight

- Start with the check, not the recharge. It tells us whether the system is low, and a system that is low has a leak.
- A recharge on a leaking system works for a few weeks. If the customer wants that for a trip, fine: they hear it first, and it is written on the order. No warranty on a recharge that was not preceded by a repair.
- The dye goes in with every recharge. If it comes back warm, the dye shows where.
- A system that is full and still warm is a compressor, a blend door or a fan: [A/C compressor and condenser](ac-compressor-and-condenser.md).

Refrigerant is recovered with the machine, never let go. Only the technicians who hold the certificate open a system.
""",
 serves=['S11', 'challenge:fact-in-table', 'challenge:combine-policy-and-price', 'challenge:customer-terms', 'challenge:kb-does-not-say'],
 facts=['Season May to August at 2.5 times the yearly mean at the peak (design S11).',
        'Four catalogue jobs with hours and prices: ac_performance_check (menu 49.95), ac_recharge (1.2 h), ac_recharge_1234yf (1.2 h), ac_evaporator_cleaning (menu).',
        'R-134a up to about 2016, R-1234yf from about 2017; the label decides.',
        'R-1234yf is stocked at East Main only (parts/stock-we-keep.md); whether Charlotte Pike can recharge it is not stated.',
        'Check first; a low system has a leak; a recharge without a repair carries no warranty and that is written on the order.',
        'Only certified technicians open a system (names not given anywhere).'],
 new=['No warranty on a recharge not preceded by a repair (an exception the warranty page does not list: a small planted inconsistency between a service page and the policy).'],
 rev=RISE,
 ru=['«Заправка кондиционера»; R-134a dominates the Russian parc; R-1234yf is rare.'])

page('services/ac/ac-compressor-and-condenser.md', 'A/C compressor and condenser', 'W', 13,
 'The two big A/C repairs.',
 f"""*{S(13,'full')} with {S(5,'full')} · Last reviewed {REV()}*

**Replace A/C compressor, receiver-drier & expansion valve; evacuate & recharge**: {hrs('ac_compressor')} hours, {t('ac_compressor')}. When a compressor fails it sheds metal into the system. That is why the drier and the expansion valve go with it and are on the same line: a new compressor on a dirty system fails again, and the maker will not honour it. The recharge is included.

**Replace A/C condenser; evacuate & recharge**: {hrs('ac_condenser')} hours, {t('ac_condenser')}. The condenser sits in front of the radiator and takes every stone on the interstate. A leak there shows as dye on the fins. Recharge included.

- Both prices are for R-134a cars. A car on R-1234yf costs more by the difference between the two recharges; price it from the list.
- Compressors and condensers come from {V('V4')} on the noon run. Order by 10:30 or it is tomorrow.
- A compressor is an electrical part once fitted: it cannot go back. Diagnose first, then order.
- In July, be honest about the wait. Four hours of work that starts when the part arrives at 12:30 is a next-morning pick-up.
""",
 serves=['challenge:combine-policy-and-price', 'S11'],
 facts=['Catalogue job ac_compressor: 3.6 h; includes receiver-drier, expansion valve and recharge.',
        'Catalogue job ac_condenser: 2.8 h; recharge included.',
        'Prices assume R-134a; R-1234yf cars cost more by the difference between the two recharges (278.80 - 207.40 = 71.40).',
        'Parts from V4 on the noon run, order by 10:30; compressors are not returnable once fitted.',
        'A job started at 12:30 is a next-morning pick-up.'],
 new=['Expected answer for "A/C compressor on a 2019 car with R-1234yf": 1,176.86 + 71.40 = 1,248.26 before supplies and tax (reader\'s arithmetic; the catalogue has no such row, so the seeder must price it the same way or the page line changes).'],
 rev=RISE,
 ru=['«Замена компрессора кондиционера», «замена радиатора кондиционера».'])

# ---------------------------------------------------------------- electrical
page('services/electrical/battery.md', 'Battery', 'W', 13,
 'Battery test and replacement; the November rush; bulbs.',
 f"""*{S(13,'full')} with {S(5,'full')} · Last reviewed {REV()}*

## Test

**Battery, starting & charging system test**: free, ten minutes, on every car at the inspection. In the first cold weeks of November we do it at the door before the customer has finished parking. A battery that tests weak in October is a no-start in December; tell them now.

## Replace

**Replace battery, clean terminals**: menu labour {lab('battery_replace')}, no shop supplies.

| Grade | Battery | Installed |
|---|---|---:|
| Economy | Interstate MT | {t('battery_replace','economy')} |
| Standard | Interstate MTP | {t('battery_replace')} |
| Premium | Interstate MTX, AGM | {t('battery_replace','premium')} |

For the common 24F size. Other sizes differ a little; the price list has the one, the shop system has the rest.

- **Stop-start cars and most cars with the battery in the trunk take AGM.** That is not an upsell, it is the right part.
- Some newer cars need the new battery registered with a scan tool. It is included.
- The old battery is recycled. No core to the customer.
- Warranty is the maker's, on the label. We handle it.
- If the battery tests good and the car still cranks slowly: [Alternator and starter](alternator-and-starter.md).

## Bulbs

**Replace headlight bulb (one side)**: {t('headlight_bulb')}. Some cars need the bumper loosened; then it is more, and the customer is told first. Bulbs are warrantied 90 days.
""",
 serves=['S11', 'challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Catalogue job battery_test: free, 0.1 h, done at the inspection.',
        'Battery rush: first cold weeks of November (design S11).',
        'Catalogue job battery_replace: menu labour 24.95; Interstate MT / MTP / MTX for group 24F.',
        'AGM for stop-start cars; registration included; old battery recycled.',
        'Warranty per the maker\'s label.',
        'Catalogue job headlight_bulb: 0.3 h, standard total; bulbs 90 days.'],
 rev=RISE,
 ru=['«Проверка АКБ» is paid (300 RUB); «замена АКБ» 8 760 RUB standard; rush December to February.'])

page('services/electrical/alternator-and-starter.md', 'Alternator and starter', 'W', 13,
 'Charging and starting repairs.',
 f"""*{S(13,'full')} with {S(5,'full')} · Last reviewed {REV()}*

| On the order | Hours | Economy / Standard / Premium |
|---|---|---|
| Replace alternator | {hrs('alternator')} | {t('alternator','economy')} / {t('alternator')} / {t('alternator','premium')} |
| Replace starter motor | {hrs('starter')} | {t('starter','economy')} / {t('starter')} / {t('starter','premium')} |

Both are remanufactured units and both carry a core, which the customer does not see.

**Which is it?** The customer cannot tell and should not be asked to.

- Clicks and will not crank, lights bright: starter.
- Cranks slowly, lights dim: battery, or an alternator that has not been charging it.
- Battery light on while driving: alternator, or its belt.
- Started fine yesterday, dead today, fine after a jump, dead again tomorrow: test all three, and think about a drain.

So the first job is always the free test. I would want the printout in my hand before anybody says "alternator" to a customer. An alternator fitted to a car that needed a battery is our mistake and our money.

These are electrical parts: once fitted they do not go back to the supplier. They come from {V('V4')}, noon run.
""",
 serves=['challenge:customer-terms', 'smoke'],
 facts=['Catalogue jobs alternator (1.6 h) and starter (1.5 h), three tier totals; reman units with cores.',
        'Symptoms table for starter, battery, alternator, drain.',
        'The free test comes first; a wrong diagnosis is the shop\'s cost (warranty page).',
        'Non-returnable once fitted; supplied by V4 on the noon run.'],
 rev=RISE,
 ru=['«Замена генератора», «замена стартера»; repair of the unit (ремонт генератора) is a common Russian alternative.'])
