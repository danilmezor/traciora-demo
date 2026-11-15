from kbb import *

page('customers/estimates-and-approvals.md', 'Estimates and approvals', 'W', 2,
 'Public promise on estimates: written, per job, nothing without approval.',
 f"""*In force from {D('T-26mo')} · Last reviewed {D('T-5mo')}*

1. **We look first.** A price for a repair comes after an inspection or a diagnosis, not before.
2. **You get it in writing.** The estimate lists each job separately with its parts, labour and tax, and the photos or measurements behind it.
3. **You approve job by job.** Say yes to the brakes and no to the shocks if you like. You can approve by replying to the text or e-mail we send, on the phone, or at the counter. We write down who approved and when.
4. **We do not go over.** If a job turns out to need more than you approved, we stop and ask. No approval, no extra work.
5. **Work you put off is not forgotten.** We note it on your car's record and remind you. No pressure.

An estimate is good for 30 days. After that parts prices may have moved and we re-check it.

Inspection and diagnosis fees are on our [price page](prices-for-common-services.md) and are charged whether or not you go ahead with the repair.
""",
 serves=['S7', 'challenge:combine-policy-and-price', 'challenge:three-page-procedure'],
 facts=['Estimate after inspection or diagnosis; written; each job priced separately with parts, labour, tax and evidence.',
        'Approval is per job (ERP order_job approved or declined), by text or e-mail reply, phone or in person; who and when is recorded.',
        'The approved amount is never exceeded without a new approval.',
        'Declined work is recorded as deferred and raises a reminder (ERP service_reminder).',
        'Estimates are valid 30 days.',
        'Inspection and diagnosis fees are charged regardless.'],
 new=['Estimate validity 30 days. Reason: needed by the deposit and price-change pages; common shop practice.',
      'Policy "in force from T-26mo": before the ERP history starts, so no order in the data predates it.'],
 ru=['Russian trade: the order (заказ-наряд) is signed by the customer; extra work is agreed by phone and added to the order. Estimate validity: write the Russian habit (often 7 to 14 days because parts prices move); propose 14 days as a new fact.'])

page('customers/warranty.md', 'Our warranty', 'W', 2,
 'Public summary of the 24/24 warranty; the staff page has the full terms.',
 f"""*In force from {D('@warranty_2424')} · Last reviewed {D('T-4mo')}*

**24 months or 24,000 miles, whichever comes first, on parts and labour**, for repairs we do with parts we supply. It starts on the date and mileage on your invoice and is good at all three Brennan Auto Care shops.

If a repair we did fails inside that time, bring the car and the invoice to any of our shops. We repair it again or replace the part at no charge.

## Shorter or different cover

- **Vehicles used for business** (delivery, service, hire): 12 months or 12,000 miles.
- **Brake pads and shoes:** 12 months or 12,000 miles against defects and noise. Pads wearing out with use is not a defect.
- **Wiper blades and bulbs:** 90 days.
- **Batteries and tires:** the maker's warranty. We handle the claim for you.
- **Work by a specialist we use** (transmission rebuilds, glass): the specialist's own warranty, which we pass on to you in writing with the job.
- **Parts you bring:** no warranty on the part or on our labour. See [Bringing your own parts](bringing-your-own-parts.md).

## Not covered

Damage from an accident, overheating or low oil after the repair, off-road or racing use, or another shop's work on the same repair. Towing and a rental car are not covered.

## Far from home

If you are more than 25 miles from any of our shops and a repair of ours fails, call us before anyone touches the car. We will arrange the repair or pay another shop for it, up to what you paid us for the original repair.
""",
 serves=['S12', 'S1', 'challenge:combine-policy-and-price', 'challenge:kb-does-not-say', 'challenge:near-duplicate'],
 facts=['24 months or 24,000 miles, whichever first, parts and labour, repairs with shop-supplied parts; from invoice date and mileage; honoured at all three shops (ledger: warranty on work).',
        'Commercial-use vehicles: 12 months or 12,000 miles.',
        'Brake pads and shoes: 12 months or 12,000 miles against defects and noise; wear is not a defect.',
        'Wiper blades and bulbs: 90 days.',
        'Batteries and tyres: maker\'s warranty, the shop handles the claim.',
        'Sublet work: the subcontractor\'s warranty, passed on in writing; its length is deliberately stated nowhere in the base.',
        'Customer-supplied parts: no warranty on part or labour.',
        'Not covered: accident, overheating or low oil after the repair, off-road or racing, another shop\'s work on the same repair, towing, rental.',
        'Over 25 miles from any shop: call first; cover up to the price of the original repair.'],
 new=['In force from {{@warranty_2424}} = T-26 months: before the two years of ERP history, so every order in the data is under 24/24.',
      'Commercial 12/12, pads 12/12, blades and bulbs 90 days, 25-mile rule, cap at the original repair price: designed after the network terms in us-shop.md (TechNet 24/24, Certified Auto Repair commercial 12/12, the 25-mile rule). ERP comeback orders of type warranty must respect these windows.'],
 ru=['Russian terms (ledger): 30 days on mechanical and electrical work; parts carry the maker\'s or seller\'s warranty; work with the customer\'s parts: on the work only, never on the part. No mileage rule and no 25-mile rule. The old page beside the current one must then differ in another way: for example 14 days before, 30 days now.'])

page('customers/dropping-off-and-picking-up.md', 'Dropping off, waiting, shuttle and pick-up', 'W', 6,
 'Public logistics: key drop, waiting room, shuttle, after-hours pick-up.',
 f"""## Dropping off

- **By appointment:** come at your time. An advisor walks round the car with you and writes down what you want looked at in your words.
- **Before we open or after we close:** every shop has a key drop box by the office door. Fill in the envelope (name, phone, what is wrong), put the key in it and drop it in the slot. We call you when we have looked at the car.

## Waiting

You are welcome to wait for an oil service, a tire rotation, a flat repair or an inspection: about an hour or less. There is coffee and Wi-Fi. For anything longer, leave the car.

## Shuttle

At **East Main and Bonny Oaks** our shuttle takes you home or to work within 5 miles of the shop, free. It leaves at 7:45 and 8:45 in the morning and brings customers back between 3:30 and 5:00. Tell us when you book.

Charlotte Pike does not run a shuttle.

## Picking up

We call or text when the car is ready and tell you the total. Pay at the counter and an advisor goes through the bill and shows you the old parts if you asked for them.

**After 5:30:** pay by phone before we close, and we leave your key in the lock box and text you the code.
""",
 serves=['challenge:kb-does-not-say', 'challenge:near-duplicate-shop-pages'],
 facts=['Key drop box by the office door at every shop; envelope with name, phone, complaint.',
        'Waiting is offered for jobs of about an hour or less: oil service, rotation, flat repair, inspection.',
        'Shuttle: East Main and Bonny Oaks only; free; within 5 miles; leaves 7:45 and 8:45; returns customers 15:30 to 17:00. Charlotte Pike has none.',
        'After-hours pick-up: pay by phone before closing, key in the lock box, code by text.',
        'Loaner or rental cars are not mentioned on any page: planted gap ("Do we have loaner cars?" has no answer in the base).'],
 new=['Shuttle radius 5 miles and the four times. Reason: a shuttle policy was asked for; morning runs fit the 7:30-9:00 arrival peak in mix.json.',
      'Lock box with a texted code for after-hours pick-up.'],
 ru=['Russian shops rarely run a shuttle; replace with what the Russian shop offers (a waiting area, the bus stop, a taxi called by the advisor). Record whatever is chosen as a new fact.'])

page('customers/payment.md', 'Paying your bill', 'W', 3,
 'Public payment terms: methods, when due, deposits, tax.',
 f"""- **When:** payment is due when you pick up the car.
- **How:** credit and debit cards, or cash. We take checks from businesses that hold an account with us. We do not take personal checks.
- **Deposits:** we ask for a deposit before ordering a part we cannot send back (special-order and electrical parts) when it costs over $300, and before a transmission goes out for rebuild. The deposit comes off your bill.
- **Tax:** Tennessee sales tax applies to parts and to labour: 9.25 % at our two Chattanooga shops, 9.75 % at Charlotte Pike in Nashville.
- **Company accounts** are billed on a monthly statement. See [Company vehicles](company-vehicles.md).

There is no discount for paying cash. The price is the price.

Questions about a bill: call the shop, or our office at (423) 555-0142 and ask for accounting.
""",
 serves=['S2', 'challenge:combine-policy-and-price'],
 facts=['Payment due at pick-up; cards and cash; business checks from account holders only; no personal checks.',
        'Deposit before special-order or electrical (non-returnable) parts over 300 USD and before a transmission rebuild; amounts are on policies/deposits.md.',
        'Sales tax on parts and labour: 9.25 % at East Main and Bonny Oaks, 9.75 % at Charlotte Pike (ledger tax.rate.main, .east, .west).',
        'No cash discount (the public echo of the S2 rule).',
        'Accounting is reached through the main line (slot 3, extension 111).'],
 new=['No personal checks; business checks from account holders only.', 'Deposit threshold 300 USD.'],
 ru=['Russian payment: cards, cash, СБП (fast payments by QR), bank transfer for companies. VAT 5 % since 2025-01-01. No cash discount holds in both.'])

page('customers/towing.md', 'Towing', 'W', 4,
 'Public towing arrangement for the Chattanooga shops; Nashville is deliberately thin.',
 f"""## Chattanooga (East Main and Bonny Oaks)

If the car cannot be driven, call us and we send the tow company we work with. You do not pay the driver; the tow goes on your repair bill.

- Hook-up and the first 10 miles to either Chattanooga shop: $95
- Each mile after that: $4

After hours, the driver can leave the car on our lot. Put the key in the key drop, or call us in the morning.

## Nashville (Charlotte Pike)

Call the shop at (615) 555-0119 and we will give you the number of a tow company near you.
""",
 serves=['challenge:kb-does-not-say', 'challenge:combine-policy-and-price'],
 facts=['Chattanooga shops use vendor V8 (not named to customers): hook-up with the first 10 miles to either Chattanooga shop 95 USD, 4 USD per mile after; billed on the repair order as sublet.',
        'Nashville: no tow partner and no price stated anywhere in the base (vendors.json: V8 serves main and east only): planted gap.'],
 new=['Tow price: 95 USD including 10 miles, 4 USD per extra mile. Reason: a towing radius and price were asked for; light-duty local rates. The ERP needs matching order_sublet lines for towed cars.'],
 ru=['Russian towing: эвакуатор, a fixed price inside the city and per km outside; the Russian vendors file has the partner. Keep the Kazan gap.'])

page('customers/bringing-your-own-parts.md', 'Bringing your own parts', 'W', 1,
 'Public version of the customer-supplied parts policy, in the founder\'s words.',
 f"""You can. Here is how it works.

- We fit parts you bring at our normal labour rate.
- There is **no warranty** on the part or on our labour. If the part is wrong, does not fit or fails next month, the labour to do the job again is charged again.
- We will not fit customer-supplied **brake hydraulic parts** (calipers, hoses, master cylinders), **airbag or seat-belt parts**, or **tires more than six years old**. Those we supply ourselves or not at all.
- If the part in the box is plainly the wrong one or plainly junk, the technician will say so and may decline.

Why: when we supply the part we know where it came from, and if it fails we stand behind the whole job for [24 months](warranty.md). We cannot warranty what we did not choose.

*{S(1,'full')}*
""",
 serves=['challenge:combine-policy-and-price', 'challenge:customer-terms'],
 facts=['Customer parts are fitted at the posted labour rate.',
        'No warranty on part or labour; redo labour is charged again.',
        'Refused: brake hydraulic parts (calipers, hoses, master cylinders), airbag and seat-belt parts, tyres older than six years.',
        'A technician may decline a plainly wrong or poor part.',
        'Signed by the founder (slot 1): one of his hobby-horses.'],
 new=['The three refused groups and the six-year tyre age. Reason: a customer-supplied parts policy was asked for; these are the safety items shops usually refuse.'],
 ru=['Very common in Russia (ledger open row: customers bringing their own parts). Russian rule: warranty on the work only, never on the part; many shops add a higher hour for customer parts. If a surcharge is chosen, it is a new price and needs a catalogue row.'])

page('customers/if-something-is-not-right.md', "If something isn't right", 'W', 4,
 'Public complaints route.',
 f"""Tell us. We would rather hear it from you than read it somewhere.

1. Call the shop that did the work and ask for the service manager: {S(4,'full')} for East Main and Bonny Oaks, {S(22,'full')} for Charlotte Pike. Or tell any advisor and they will get him.
2. You will hear back within one working day, from a person who can fix it.
3. If the car needs to come back, we look at it first, ahead of the day's other work, and it does not cost you anything to have it looked at.

If you are still not satisfied, write to {S(2,'full')}, managing owner: cbrennan@brennanautocare.example.
""",
 serves=['S8', 'S1'],
 facts=['Complaints go to slot 4 (main, east) or slot 22 (west); reply within one working day.',
        'A returning car is looked at first and the look is free.',
        'Escalation: slot 2 by e-mail cbrennan@brennanautocare.example (pattern in phones.md).',
        'Account A5\'s manager called three times in nine days and was never called back: the story breaks this page\'s promise on purpose.'],
 new=['Reply within one working day. Reason: gives stories S1 and S8 a stated standard to be measured against.'],
 ru=['In Russia a written claim (претензия) has legal weight under the consumer law; say that a written claim is answered within 10 days by law and by phone the same day by the shop\'s own rule. Record as new facts.'])

# ---------------------------------------------------------------- shop-floor (worker rank)
page('shop-floor/README.md', 'Shop floor', 'W', 8,
 'Index for technicians; what a worker-rank person can read.',
 f"""For technicians. Short on purpose.

- [Clocking in and out](clocking-in-and-out.md)
- [Shift changes and time off](shift-changes-and-time-off.md)
- [The courtesy inspection](courtesy-inspection.md)
- [Before a car leaves your bay](before-a-car-leaves.md)
- [When a car comes back](when-a-car-comes-back.md)
- [Safety](safety.md)

The staff handbook is the binder in each break room. Pay and time-off questions go to {S(3)} in the office.

{S(8)}
""",
 serves=['visibility:worker', 'challenge:kb-does-not-say', 'S14'],
 facts=['Six pages for technicians.',
        'The staff handbook is not visible at worker rank: the page sends technicians to the paper binder and to slot 3.',
        'Product fact: the customers\' assistant reads at worker rank, so this folder is readable by it too; nothing here is confidential.'],
 new=['A paper handbook binder in each break room. Reason: the handbook file is staff (junior) rank, because anything at worker rank is readable by the website assistant.'],
 ru=['Same six pages.'])

page('shop-floor/clocking-in-and-out.md', 'Clocking in and out', 'W', 4,
 'How technicians punch, the location check, what to do after a forgotten clock-out.',
 f"""*{S(4)} · Last reviewed {D('T-2mo')}*

- Clock in on your phone **when you are at the shop**, not on the way. The app checks where you are. A punch from down the road is flagged and comes to me.
- Your shift start is the time on the schedule. Five minutes after it you are late, and the punch says so.
- Clock out when you leave. If you forgot, your Home screen asks you the next morning: put in the time you really left and send it. I approve it the same day.
- Do not ask someone else to punch for you, and do not punch for anyone.
- Clocked time is attendance. The time on a job is the job clock in the shop system, and that is separate: start and stop it per job as always.

If the app will not let you in, tell your foreman or shop manager before your shift starts, not after.
""",
 serves=['S14', 'visibility:worker'],
 facts=['Punch at the shop; the product checks location; a far punch is flagged (S14: slot 26 punched twice from 600 m).',
        'Late = more than five minutes after the scheduled start.',
        'A forgotten clock-out is corrected by the worker on Home the next morning and approved by the planner (S14: slot 14).',
        'Attendance (Traciora) and job time (ERP time_entry) are separate.'],
 new=['Lateness threshold of five minutes. Reason: the punches need a rule for "late"; must equal the roster\'s grace setting in core.'],
 created=(4, 'T-5.5mo'),
 rev=[(4, 'T-2mo', 'added the sentence about a punch from down the road after the two flagged punches at Charlotte Pike; message: "Clock in at the shop."')],
 ru=['Same rules. Distance in metres.'])

page('shop-floor/shift-changes-and-time-off.md', 'Shift changes and time off', 'W', 4,
 'How a technician asks for a shift change or a day off; what the planner needs.',
 f"""*{S(4)}*

- Ask in the app, on the shift you want changed. Not by text, not through somebody else.
- **Write the reason.** A request with no reason is not looked at.
- Ask at least 7 days ahead. Inside 7 days I will try, and the answer is usually no unless you bring me someone who will take the shift.
- There is no swap in the app. Ask for a change of date and name who takes the shift. "He said he would" is not a yes: I ask him.
- The schedule for a week is published by Thursday noon the week before. Once it is published it is the schedule.
- Sick: call the shop line before 7:00. A text to a friend is not calling in.

At Charlotte Pike, {S(22)} plans the schedule and answers requests.
""",
 serves=['S14', 'S5', 'visibility:worker'],
 facts=['Requests are made in the app on the shift; every request needs a written reason (design 7.2 S14).',
        'Notice: 7 days; the product has no swap (stories/S14: change of time, change of date, removal): a change of date is asked for and the reason names who takes the shift.',
        'The week\'s roster is published by Thursday noon of the week before (slot 22 publishes late: his character).',
        'Sick: call the shop line before 7:00.',
        'Slot 4 plans main and east; slot 22 plans west.'],
 new=['7 days\' notice; publish by Thursday noon; sick call before 7:00. Reason: the roster stories (late publishing, declined requests) need a stated rule; the shift planner\'s data must not contradict it.'],
 created=(4, 'T-5.5mo'),
 ru=['Russian mechanics work 5/2 with staggered days off, advisors 2/2: the page says so. Sick leave is a legal document (больничный): say to call before the shift and bring the sheet.'])

page('shop-floor/courtesy-inspection.md', 'The courtesy inspection', 'W', 8,
 'Step one of the inspection-to-approval procedure: what the technician checks and records.',
 f"""Every car that comes in for anything gets one, unless the advisor writes "no inspection" on the order. Ten minutes. It is how the customer finds out what the car needs and how we find the next job.

## What to check

Tires (tread depth in 32nds, all four, and the date code), brake pads through the wheel or with the wheel off if it is off anyway, lights, wipers, battery test, belts and hoses, fluid levels and condition, leaks underneath, shocks and struts, CV boots, exhaust.

## How to mark it

- **Good:** nothing to do.
- **Watch:** worn but safe. Write the measurement: "front pads 4 mm", not "pads getting low".
- **Bad:** needs doing now. Measurement **and a photo**. No photo, the advisor cannot sell it and I will send you back to take one.

Pick the catalogue job for every Watch and Bad line. Do not type a job by hand if it is in the list.

## Then

Close the inspection in the shop system. It goes to the advisor, who builds the estimate: [Writing an estimate](../how-to/writing-an-estimate.md). Do not tell the customer a price. Do not start anything that is not approved on the order.

{S(8)}
""",
 serves=['challenge:three-page-procedure', 'S7', 'visibility:worker'],
 facts=['Step 1 of 3 (then how-to/writing-an-estimate.md, then how-to/getting-approval.md).',
        'Done on every car unless the order says no inspection (mix: 80 % of orders).',
        'Three states: Good, Watch, Bad (ERP inspection_item); Watch and Bad need a measurement; Bad needs a photo.',
        'Each Watch or Bad line is tied to a catalogue job (ERP inspection_item.recommended job).',
        'Technicians give no prices and start nothing unapproved.',
        'The link to how-to/ is above worker rank: a worker (and the public assistant) sees the text but cannot open the target.'],
 new=['Ten minutes; tread in 32nds; photo required for Bad.'],
 ru=['Russian inspection is «осмотр по чек-листу»; free with service in 70 % of orders. Tread depth in mm.'])

page('shop-floor/before-a-car-leaves.md', 'Before a car leaves your bay', 'W', 8,
 'The foreman\'s final checks.',
 f"""Every car, every time. I road-test what I can, not all of them.

1. Wheels off today? **Torque the lugs with the torque wrench**, by hand, to the spec. Not the gun.
2. Brake job? Pump the pedal before you move the car. Clean and lube the slides. Check the fluid level.
3. Caps on: oil, coolant, brake fluid, washer. Dipstick in.
4. Nothing left under the hood. Count your tools.
5. Start it, look underneath for drips.
6. Drive it round the building at least. Brakes, steering, suspension and anything that made a noise gets a real road test.
7. Reset the oil light. Set the tire pressures to the door sticker.
8. Old parts in the box if the order says the customer wants them.
9. Wipe the wheel, the shifter and the door handle. Take the seat cover and mat out.
10. Stop your job clock. Write what you did and what you saw on the order.

A car that comes back for something on this list is a conversation with me.

{S(8)}
""",
 serves=['S6', 'S14', 'visibility:worker'],
 facts=['Ten checks; lugs torqued by hand with a torque wrench; brake slides cleaned and lubricated (slot 27 skips this: S6).',
        'The foreman (slot 8) road-tests some cars.',
        'The job clock is stopped per job (ERP time_entry).'],
 ru=['Same list. Torque in N·m.'])

page('shop-floor/when-a-car-comes-back.md', 'When a car comes back', 'W', 8,
 'What a technician does with a comeback.',
 f"""A comeback is a car back for the same thing we were paid to fix.

- It goes to the front of the line. The customer has already paid once.
- The advisor opens a new order marked warranty and tied to the first one. You do not work on it under the old order.
- **The foreman looks first**, with the tech who did the job if he is in. At Bonny Oaks that is {S(18)}; at Charlotte Pike it is {S(22)}.
- Write what you found, plainly. "Slide pins dry, pad hung up" is useful. "Customer states noise" is not.
- Nobody argues with the customer about whose fault it is. Not at the car, not at the counter.

We count comebacks per technician every month. Everybody has some. The number is for getting better, and I will show you yours if you ask.

{S(8)}
""",
 serves=['S6', 'S1', 'visibility:worker'],
 facts=['Comeback = a new order of type warranty tied to the original (design 2.3).',
        'It goes first; the foreman looks first: slot 8 at main, slot 18 (lead technician) at east, slot 22 at west.',
        'Comebacks are counted per technician monthly.',
        'Slot 27 at west "has never been shown his own numbers" (cast): the page\'s promise is not kept there.'],
 new=['Who looks first at each shop.'],
 ru=['Same. The Russian comeback window follows the 30-day warranty.'])

page('shop-floor/safety.md', 'Safety', 'W', 8,
 'Short safety rules, including who may touch hybrids and refrigerant.',
 f"""- Safety glasses on in the bays. Always.
- Lift: arms on the maker's lift points, rock the car at knee height before it goes up, locks down before you go under.
- Never under a car on a jack alone. Stands.
- **Orange cables are high voltage.** Hybrid work is {S(10)}'s, at East Main, and nobody else's. If a hybrid is in your bay for brakes or tires, you do brakes or tires and touch nothing orange.
- Refrigerant is recovered with the machine, never vented. A/C work goes to the technicians who hold the certificate: ask your foreman who that is at your shop.
- Battery acid, brake cleaner near a flame, a spinning belt: you know. Act like you know.
- A spill gets cleaned up now, by whoever is nearest.
- If you are hurt, however small, tell your foreman the same day so it is written down.

{S(8)}
""",
 serves=['visibility:worker', 'challenge:kb-does-not-say'],
 facts=['Hybrids: slot 10 only, at East Main.',
        'Refrigerant: recovered by machine; only certified technicians do A/C work; the page names nobody (planted gap: "who is certified for A/C at Bonny Oaks?" is not in the base).',
        'Injuries are reported to the foreman the same day.'],
 ru=['Same. Russian shops have a formal safety briefing log (журнал инструктажа): mention signing it.'])
