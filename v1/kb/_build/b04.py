from kbb import *

page('policies/estimates-and-approvals.md', 'Estimates and approvals', 'J', 2,
 'Staff rules for estimates: how fast, what is on them, how approval is recorded, what happens to declined work.',
 f"""*{S(2,'full')} · In force from {D('T-26mo')} · Last reviewed {D('T-5mo')}*

What we promise customers is on the [public page](../customers/estimates-and-approvals.md). This is how we keep it.

## The estimate

- No repair without a written estimate on the order. An inspection or a diagnosis may start on the customer's word; nothing else.
- One line per job, from the catalogue. Parts at the standard tier unless the customer asked otherwise. Shop supplies and tax shown.
- **It goes to the customer the same working day the car was inspected.** A company account's estimate goes to its fleet contact within four working hours.
- It is good for 30 days.

## The approval

- Per job. Mark each job approved or declined; never approve the order as a lump.
- Record **who** approved, **how** (counter, phone, text, e-mail) and **when**. A phone approval: read the job and the amount back and write the name of the person who said yes.
- A company vehicle: the driver approves found work only up to $300 for the visit. Above it, the fleet contact: [Company accounts](../accounts/company-account-terms.md).
- No answer from the customer is not an approval. Chase it: [Getting approval](../how-to/getting-approval.md).

## When the job grows

Stop. New line on the order, new approval, then work. A bill never goes over what was approved, by any amount. If the technician already did it, that is our cost, not the customer's.

## Declined work

Mark it declined and tick *deferred* if it will still need doing. That raises the reminder. Say it on the invoice too: "Recommended, not done: rear shocks, leaking." The customer signs for the car knowing.

An estimate nobody answers for 30 days closes as declined.
""",
 serves=['S1', 'S7', 'S8', 'challenge:three-page-procedure', 'challenge:combine-policy-and-price'],
 facts=['No repair without a written estimate; inspection and diagnosis may start on the customer\'s word.',
        'One line per catalogue job; standard tier by default; supplies and tax shown.',
        'Estimate sent the same working day as the inspection; company accounts within four working hours (account A6\'s estimates waited two days and more: the story breaks this standard).',
        'Valid 30 days; unanswered after 30 days closes as declined (ERP repair_order status declined).',
        'Approval per job with who, how and when (ERP order_job: how and when approved).',
        'Drivers approve found work only up to 300 USD per visit (ledger s4.driver_limit).',
        'Never exceed the approved amount; unapproved work done is the shop\'s cost.',
        'Declined work marked deferred raises a reminder (ERP service_reminder) and is printed on the invoice.'],
 new=['Company-account estimates within four working hours. Reason: gives the A6 story a measurable standard.',
      'Unanswered estimates close as declined after 30 days: the ERP\'s estimate-to-declined transition should use this window.'],
 ru=['Russian trade: extra work is agreed by phone and written into the заказ-наряд; the customer signs the order and the act. Keep "same day" and the per-job approval.'])

page('policies/diagnostic-fees.md', 'Diagnostic and inspection fees', 'J', 1,
 'Why diagnosis is charged and never credited; the founder\'s hobby-horse.',
 f"""*{S(1,'full')} · Reviewed with {S(2)} {D('@price_rise')}*

We charge for finding out what is wrong. We always have.

- Check engine light: one hour, {t('check_engine_diag')}.
- Electrical fault: an hour and a half to start, {t('electrical_diag')}.
- Brakes, steering and suspension, A/C: an inspection at {t('brake_inspection')} each.
- Cooling system pressure test: {t('cooling_pressure_test')}.
- Battery and charging test: free. It takes ten minutes and sells batteries.
- The courtesy inspection with a service: free.

**The fee is not credited toward the repair, and it is not waived to win the job.** Finding the fault is the skilled part. Any shop can bolt on the alternator once somebody has worked out it is the alternator. When a customer asks "do you take it off if I do the work?", the answer is no, and here is what you got for it: the cause, in writing, with the test results. They can take that anywhere.

If the fault is not found in the time sold, call the customer before selling more time. Tell them what was tested and ruled out.

If we got the diagnosis wrong, the customer does not pay for the part that did not fix it. That is our mistake to eat.
""",
 serves=['challenge:combine-policy-and-price', 'challenge:customer-terms'],
 facts=['Fees from the catalogue: check_engine_diag, electrical_diag, brake_inspection (the same menu price as suspension_diag and ac_performance_check), cooling_pressure_test; battery_test and courtesy_inspection are free.',
        'The fee is never credited toward the repair and never waived.',
        'More diagnostic time needs the customer\'s approval.',
        'A wrong diagnosis: the customer does not pay for the part that did not fix it.',
        'Voice: slot 1, first person plural, short sentences.'],
 new=['No crediting of diagnostic fees. Reason: a crediting rule would need discount lines in the ERP on every diagnosed repair; "never credited" needs none.'],
 rev=[(2, '@price_rise', 'fees updated to the new list; message: "New prices from today."')],
 ru=['Russian shops often do credit diagnostics when the repair is done there; this company does not, and the founder says so. Russian fees from the catalogue (computer diagnostics 1 200, running gear 800, brakes 700, battery test 300).'])

page('policies/customer-supplied-parts.md', 'Customer-supplied parts', 'J', 2,
 'Staff rules for fitting parts the customer brings.',
 f"""*Last reviewed {D('T-9mo')}*

The public wording is on [Bringing your own parts](../customers/bringing-your-own-parts.md). Read it to the customer if they ask; do not improvise.

At the counter:

1. Say the three things before taking the keys: normal labour rate, no warranty on part or labour, and if the part is wrong the labour is charged again. Get a yes.
2. On the order, type the part on its own line with **"customer supplied"** in the description, price $0.00. It will have no part number. That is the one case where a hand-typed part line is right.
3. Write "Customer-supplied part: no warranty" in the order notes. It prints on the invoice.
4. We do not fit customer-supplied brake hydraulic parts, airbag or seat-belt parts, or tires over six years old. No exceptions at the counter; send the customer to {S(4)} or {S(22)} if they want to argue.
5. Shop supplies apply as on any hourly job.

If the customer's part turns out wrong and they want us to supply the right one, that is a new estimate at list price, and the job then carries the normal warranty.

A company account that supplies its own parts (none does today) would need it written into its account page first.
""",
 serves=['challenge:combine-policy-and-price', 'S15'],
 facts=['Three things said before taking the keys: normal labour rate, no warranty, labour charged again if the part is wrong.',
        'The part goes on the order as a hand-typed line with "customer supplied", price 0.00, no part number (the one legitimate hand-typed part line; ERP mess kind 7).',
        'Order note "Customer-supplied part: no warranty" prints on the invoice.',
        'Refused items as on the public page; exceptions only through slot 4 or 22.',
        'Shop supplies apply.',
        'No company account supplies its own parts.'],
 ru=['Frequent in Russia: add the Russian wording of the note printed on the act. If a higher hour for customer parts is chosen it is a new catalogue row.'])

page('policies/deposits.md', 'Deposits', 'J', 3,
 'When a deposit is taken, how much, and what is refunded.',
 f"""*{S(3,'full')}, office · Last reviewed {D('T-8mo')}*

A deposit is taken before we spend money we cannot get back.

| When | Deposit |
|---|---|
| A special-order part, or any electrical part once ordered, that costs the customer more than $300 | Half the price of the part |
| A transmission going out for rebuild | $1,700.00, which is half of the specialist's price |
| Four or more tires in a size we do not normally stock | Half the price of the tires |
| A company account | None. It goes on the statement |

Enter the deposit as a payment on the order, marked *deposit*. It comes off the final bill automatically. Give the customer the receipt.

## Refunds

- The customer cancels before the part has shipped: the whole deposit back.
- After it has shipped: the deposit less whatever the supplier charges us to take it back, which can be up to 20 % of the part's price. If the supplier will not take it back, the part is the customer's and the deposit is kept.
- A refund goes back the way the deposit came: card to card, cash to cash. A cash refund needs the shop manager: see [Voids and refunds](voids-and-refunds.md).

Suppliers' return rules are on [Returns and cores](../parts/returns-and-cores.md).

Please do not take a deposit "to hold an appointment". We do not charge for appointments.
""",
 serves=['challenge:fact-in-table', 'challenge:combine-policy-and-price', 'S15'],
 facts=['Deposit of half the part price for special-order parts and ordered electrical parts over 300 USD.',
        'Transmission rebuild: 1,700.00, half of the specialist\'s price (catalogue transmission_rebuild sublet price 3,400.00).',
        'Four or more tyres in a non-stocked size: half the tyre price. Company accounts: none.',
        'Entered as a payment marked deposit (ERP payment: deposit).',
        'Refund in full before shipping; after shipping less the supplier\'s restocking charge of up to 20 %; non-returnable parts become the customer\'s.',
        'Refunds return by the original method; cash refunds need the shop manager.',
        'No deposit for appointments.',
        'Voice: slot 3, formal, complete sentences.'],
 new=['Deposit amounts and the 20 % restocking ceiling. Reason: a deposit policy was asked for; the ERP\'s deposit payments must follow these rules (half, 1,700 for a rebuild).'],
 ru=['Russian: предоплата за запчасти под заказ, usually 50 to 100 %; refunds for goods made to order follow the consumer law. Amounts in RUB from the Russian catalogue (rebuild sublet price there).'])

page('policies/cancellations-and-no-shows.md', 'Cancellations and no-shows', 'J', 4,
 'What happens when a booked customer does not come.',
 f"""*{S(4)} · Last reviewed {D('T-5mo')}*

About one booking in eight does not show. That is normal. Here is how we keep it from wrecking the day.

- **Confirm the day before.** A call or a text for every timed appointment, by 3:00. A confirmed booking is marked confirmed.
- **Thirty minutes.** A customer more than 30 minutes late with no word loses the slot. Mark the appointment no-show and give the bay to the next car. If they turn up later, they wait like a walk-in, and we are nice about it.
- **Call a no-show once**, the same day: "We missed you this morning, do you want another time?" Half of them rebook.
- **Two no-shows in twelve months:** no more timed appointments for that customer. They are welcome to drop the car off in the morning and we get to it when we can. Put it in the customer notes so the next advisor knows.
- **No fee.** We do not charge for a missed appointment and we do not take deposits to hold one.
- A customer who cancels is thanked for calling. Offer the next time before they hang up.

Parts ordered for a no-show: tell {S(9)} the same day so they go back while they still can.
""",
 serves=['challenge:kb-does-not-say', 'smoke'],
 facts=['About one booking in eight is not kept (ledger: appointments not kept 12 %).',
        'Confirmation the day before by 15:00; confirmed bookings are marked confirmed (ERP appointment status).',
        '30 minutes late without word = no-show (ERP appointment no_show).',
        'One call to a no-show the same day.',
        'Two no-shows in twelve months: drop-off only, noted on the customer.',
        'No fee and no deposit for appointments.',
        'Parts ordered for a no-show are reported to slot 9 the same day.'],
 new=['Confirmation by 15:00; the 30-minute rule; two strikes in twelve months. Reason: a no-show policy was asked for.'],
 ru=['Russian no-show share 10 % (ledger). Confirmation by messenger is the norm.'])

page('policies/storage-of-uncollected-cars.md', 'Cars not collected', 'J', 2,
 'Storage of finished cars: free days, daily charge, the 30-day step. Contradicted on purpose by a team note.',
 f"""*{S(2,'full')} · In force from {D('T-9mo')}*

A finished car that sits on the lot costs us a parking space and worries the insurer.

- **Free for five working days** after we tell the customer it is ready. "Told" means we spoke to them or they answered a message, and the order says when.
- **From the sixth working day: $25 a day**, added to the order as a storage fee. Tell the customer on day three that it starts on day six. No surprises.
- Call on day one, day three and day five. Write each call on the order.
- A car waiting on the customer's decision (estimate sent, no answer) is not "ready". The five days do not run, but chase the answer: [Getting approval](../how-to/getting-approval.md).
- **Thirty days:** tell {S(3)}. She sends the certified letter and starts the paperwork. Advisors do not mention liens or selling the car to a customer, ever.
- {S(4)} or {S(22)} may waive storage for a reason (hospital, deployment). It is written on the order like any discount.

Company accounts are not charged storage. If a fleet vehicle sits more than a week, tell {S(4)}.
""",
 serves=['challenge:policy-vs-team-note', 'operate:contradiction', 'S15'],
 facts=['Free for five working days after the customer was told the car is ready; from the sixth working day 25 USD a day as a storage fee (ERP order_fee).',
        'Warn on day three; calls on days one, three and five, each written on the order.',
        'A car awaiting an estimate decision is not "ready".',
        'At 30 days slot 3 sends a certified letter and starts the lien paperwork; advisors never mention liens.',
        'Slot 4 or 22 may waive storage with a written reason.',
        'Company accounts are not charged storage.',
        'CONTRADICTION PLANTED: a team note in memory, approved by slot 22, says "Storage is charged from day three after the car is ready". The policy page (slot 2, in force from T-9 months) is the company rule; the note is the old Charlotte Pike habit.',
        'ERP mess kind 4 (an order at west open five months after the car left) is a different thing: an unclosed order, not an uncollected car.'],
 new=['Storage: five free working days, 25 USD a day, letter at 30 days. Reason: a storage policy was asked for. No storage fee is planted in the ERP; if one is wanted it follows this page.',
      'NEW FACT FOR THE MEMORY STORE: one active team note, proposed by slot 23 and approved by slot 22 at about T-4 months: subject "Uncollected cars", text "Storage is charged from day three after the car is ready." It must pass the note gate (no customer data).'],
 ru=['Russian: платная стоянка after N days is written into the order form the customer signs. Choose RUB amounts as new facts (for example 5 free days, then 300 RUB a day).'])

page('policies/complaints.md', 'Complaints', 'J', 4,
 'Staff procedure for a complaint: who hears it, who decides, how fast.',
 f"""*{S(4)} · Last reviewed {D('@belt_proposal')}*

A complaint is a customer giving us a second chance. Most do not bother; they just leave.

## At the counter or on the phone

1. Let them finish. Do not explain, do not defend the technician, do not say "no problem".
2. Say what you heard back to them in one sentence.
3. Say what happens next and when: "{S(4)} will call you before noon tomorrow." Then make that true.
4. Write it on the order, in their words.
5. Raise a card on the board for the shop manager, high priority, with the order number. Do it before you take the next call.

## Who decides what

| What the customer needs | Who |
|---|---|
| An apology, an explanation of the bill | The advisor who has them |
| Money off, up to 10 % of the bill | The advisor, with the reason on the order |
| Money off over 10 %, a free redo outside warranty, a refund | {S(4)} for Chattanooga, {S(22)} for Nashville: [Discount policy](discounts.md) |
| A complaint about a technician's work | The foreman looks at the car. Nobody discusses the technician with the customer |
| A complaint about an advisor | {S(4)} or {S(22)}, not the advisor's colleague |
| A company account | Always {S(4)}, the same day, whatever the size |

## How fast

The customer hears from the person who can fix it **within one working day**. A promised call back is kept that day even if there is nothing new to say.

## Afterwards

Close the card with what was done. If the same thing happens twice it is not a complaint any more, it is how we work, and it goes on this knowledge base or to {S(2)}.
""",
 serves=['S8', 'S1', 'challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Five counter steps; the complaint is written on the order and raised as a high-priority card for the shop manager (S8: the lead advisor raised the card, the senior took it).',
        'Decision table: apology by the advisor; up to 10 % by the advisor; over 10 %, free redo outside warranty and refunds by slot 4 (Chattanooga) or slot 22 (Nashville); technician complaints to the foreman; advisor complaints to slot 4 or 22; company accounts always slot 4 the same day.',
        'Reply by the person who can fix it within one working day; promised calls back kept the same day.',
        'Account A5 is served at west, so the rule "a company account: always slot 4" was not followed there: its complaint call was taken by slot 22 and never returned (S1).'],
 new=['Company-account complaints go to slot 4 whatever the shop. Reason: makes the A5 failure a breach of a written rule rather than of good manners.'],
 rev=[(4, '@belt_proposal', 'added step 5 (raise a card before the next call) after the timing-belt complaint; message: "Card first, then the next call."')],
 ru=['Add the written claim (претензия): accepted at any shop, registered, passed to the service manager the same day.'])

page('policies/voids-and-refunds.md', 'Voids and refunds', 'J', 2,
 'The rule on voiding orders and giving money back; written with the discount rule after S2.',
 f"""*{S(2,'full')} · In force from {D('@discount_rule')}*

## Voids

- An order with **no payment** on it may be voided by the advisor who opened it, with a reason: wrong customer, duplicate, opened by mistake.
- An order with **a payment** on it is never voided at the counter. If it is wrong, the shop manager voids it, with a reason, after {S(3)} has seen where the money went.
- A voided order keeps its lines and its totals in the system. Voiding does not make it disappear, and it is not meant to.

## Refunds

- Back the way the money came. Card to the same card. Cash to cash.
- A cash refund of any size is counted out by the shop manager, not the advisor, and written in the till log.
- A refund is entered as a refund against the order. It is never done by voiding the order and writing a new one.

## Why

Voiding an order after the customer has paid cash is the simplest way to take money out of a shop. It will be noticed: {S(3)} reads the void list every week and matches it to the till.
""",
 serves=['S2', 'S15', 'operate:find-what-changed'],
 facts=['Unpaid orders may be voided by their advisor with a reason; paid orders only by the shop manager after slot 3 has traced the payment.',
        'Voids keep their lines and totals (design 2.4; ERP mess kind 9).',
        'Refunds return by the original method; cash refunds are counted out by the shop manager and logged; a refund is a refund entry, not a void plus a new order (ERP payment: refund).',
        'Slot 3 reads the void list weekly against the till.',
        'Created the same day as the discount rule.'],
 new=['The void and refund rules. Reason: the story names voids after payment as the second leak; a written rule lets "does anyone break it today" be asked of voids too. No violation after the rule is planted.'],
 created=(2, '@discount_rule'),
 ru=['Russian equivalent: сторнирование and возврат through the cash register with a return receipt (чек возврата, 54-ФЗ). The Russian leak is work past the order, so add: every job has an order before the car is touched.'])

page('policies/customer-records.md', 'Customer records', 'J', 3,
 'How a customer and a car are entered so that records do not multiply.',
 f"""*{S(3,'full')}, office · Last reviewed {D('T-5mo')}*

One customer, one record. One car, one owner. The statements, the reminders and every report depend on it.

- **Search by phone number before you create anybody.** Not by name: names are spelled three ways. If the phone is already there, that is your customer, however the name looks.
- Take a first name, a last name and a mobile number. "Mike, truck" is not a customer.
- **Do not use the "Walk-in" customer.** Every order belongs to a real person or company. A customer who will not give a name still gets a record: "Declined name", with the plate.
- The VIN goes on every car. Scan it from the door jamb. On cars too old to scan, read it off the dash and type it. If it truly cannot be read, say so in the notes.
- Mileage in and mileage out on every order, read from the dash, not from the last visit.
- Check that the car is on the right customer before you open the order. Families share cars; companies sell them to employees.
- A company's vehicle goes under the company, with its unit number, never under the driver.
- If you find a duplicate, do not fix it yourself. Send both names to me and I merge them, so the history comes along.

Thank you.
""",
 serves=['S15', 'S2', 'S7'],
 facts=['Search by phone before creating (design 7.2 S15: the pair test is "same phone").',
        'First name, last name, mobile; no "Walk-in" customer (S2; ERP mess kind 5); nameless customers are entered as "Declined name" with the plate.',
        'VIN on every car (mess kind 2: 3 % of cars, the oldest, have none); mileage in and out read from the dash (mess kind 3); car on the right customer (mess kind 8).',
        'Company vehicles under the company with the unit number.',
        'Duplicates are merged by slot 3 only (12 named pairs remain unmerged in the ERP).'],
 new=['"Declined name" as the label for a customer who will not give one.'],
 ru=['Russian records: ФИО and mobile; companies by ИНН; plates instead of unit numbers. VIN may be absent on old cars as well.'])

page('policies/service-standards.md', 'Service standards', 'J', 2,
 'One table of how fast the company promises to answer, call back, estimate and decide; the yardstick for several stories.',
 f"""*{S(2,'full')} · In force from {D('T-5mo')} · Last reviewed {D('@early_desk')}*

These are the numbers I look at. They are the same for all three shops.

| What | Standard |
|---|---|
| A ringing phone | Answered by a person before it rolls to the second desk: inside 20 seconds |
| A missed call | Called back within one hour, the same day without exception |
| A voicemail or message left when we were closed | Returned in the first hour we are open |
| A web chat or messenger message, in opening hours | First reply within 10 minutes |
| An estimate | Sent the same working day the car was inspected |
| A company account's estimate | To the fleet contact within four working hours |
| A promised call back | Made the day it was promised |
| "Your car is ready" | The call or text goes out when it is ready, and before 4:30 |
| A complaint | The customer hears from the person who can fix it within one working day |
| A comeback | Looked at the day it arrives, first |
| The week's schedule | Published by Thursday noon the week before |
| A proposed correction to this knowledge base | Decided within five working days |

How we are doing against each one is in the reports, not on this page.
""",
 serves=['S3', 'S1', 'S6', 'S9', 'S12', 'challenge:fact-in-table', 'challenge:combine-kb-and-data'],
 facts=['Twelve standards, each one row: phone answered inside 20 s (ring plan: one desk 20 s, then all); missed call returned within one hour; out-of-hours messages returned in the first open hour; chat first reply within 10 minutes; estimate the same working day; company estimates within four working hours; promised call backs the same day; ready calls before 16:30; complaints within one working day; comebacks seen the day they arrive; roster by Thursday noon; knowledge-base proposals decided within five working days.',
        'Every standard exists only in this table.',
        'Measured against the stories: main call backs median 40 minutes since the early desk (met), west 4 h 30 (missed), east 45 minutes (met); slot 22 and 23 first chat reply 35 and 40 minutes (missed); the timing-belt proposal was made one full open day before T (inside the standard).'],
 new=['The twelve standards. Reason: the stories give measurements (call-back medians, chat reply medians, late rosters, waiting estimates) and nothing to measure them against; each number here was chosen so that the home shops mostly meet it and Charlotte Pike does not.'],
 created=(2, 'T-5mo'),
 rev=[(2, '@early_desk', 'missed-call standard tightened from two hours to one when the early desk shift started; message: "One hour, now that the mornings are covered."')],
 ru=['Same table. Chat channels: web chat, Telegram, VK, Avito (design O3). Opening hours 9:00-20:00, so "before 16:30" becomes "before 19:00".'])
