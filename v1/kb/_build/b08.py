from kbb import *

page('how-to/README.md', 'How we do things', 'J', 4,
 'Index of the counter procedures, in the order a job passes through them.',
 f"""The counter jobs, in the order a car goes through them.

1. [Taking a call](taking-a-call.md), and when the customer pushes back: [Price objections](price-objections.md)
2. [Booking a visit](booking-a-visit.md)
3. [Checking a car in](checking-a-car-in.md). A company vehicle: [also this](company-vehicle-at-the-counter.md)
4. The technician's [courtesy inspection](../shop-floor/courtesy-inspection.md)
5. [Writing an estimate](writing-an-estimate.md)
6. [Getting approval](getting-approval.md)
7. Parts: [Ordering parts for a job](../parts/ordering-parts.md)
8. [Handing a car back](handing-a-car-back.md)
9. [Closing the till](closing-the-till.md)

When it goes wrong: [A comeback at the counter](a-comeback-at-the-counter.md) and [Complaints](../policies/complaints.md).

Around the edges: [Missed calls and call backs](missed-calls-and-call-backs.md), [Chats and messages](chats-and-messages.md), [Stocktake day](stocktake-day.md), [Using and fixing this knowledge base](using-this-knowledge-base.md).

{S(4)}
""",
 serves=['operate:overview', 'challenge:three-page-procedure'],
 facts=['Nine steps from the call to the till, each a page; steps 4, 5 and 6 are the procedure spread over three pages (inspection, estimate, approval).',
        'Four side pages and two "when it goes wrong" pages.'],
 ru=['Same order.'])

page('how-to/taking-a-call.md', 'Taking a call', 'J', 16,
 'How an advisor handles a first call; teaches exactly what the call scorecard checks, in the best closer\'s voice.',
 f"""*{S(16,'full')} with {S(4,'full')} · Last reviewed {D('T-4mo')}*

A caller who has never been here is choosing between us and the next number on the list. They decide in about two minutes. Your calls are scored on eight things, and these are the eight, because they are what makes a caller into a customer.

## The eight

| # | What | What it sounds like | Weight |
|---|---|---|---|
| 1 | **Greeting** with our name and yours | "Brennan Auto Care, this is Maya." | 1 |
| 2 | **Name and number**, read back | "And the best number for you? ...0142, perfect." | 2 |
| 3 | **Find out what is going on.** The car, and one question more than you need | "How long has it been doing that? Does it change when you brake?" | 2 |
| 4 | **A price with a next step attached** | "It is $49.95 for the inspection, and I could get you in Friday at eight." | 2 |
| 5 | **Offer a time. Two of them** | "Tomorrow at 7:30 or Friday at 1:00?" | 3 |
| 6 | **Ask for the booking** and take it | "I have you down for Friday at eight. Ask for Maya." | 3 |
| 7 | **Recap:** day, time, which shop, what we are doing | "Friday at eight, East Main Street, front brakes inspected." | 1 |
| 8 | **Answer the doubt**, if there is one | "Did somebody quote it lower? Here is what is in that number." | 2 |

Five and six count the most, and they are the two people skip. A call that ends "okay, thanks for calling" after a price has failed at both, however friendly it was.

Not every check fits every call. A regular whose number we have does not need to spell it. Someone who names their own time has done number five for you.

## The three ways to fail a call outright

- **A wrong promise.** A price that is not on the [price list](../prices/price-list.md). "Same day" before parts and a technician are confirmed: [what you may promise](../parts/ordering-parts.md). If you do not know, say "let me check and call you back by two" and call back by two.
- **Dropping the customer.** A hold that never comes back, a transfer to nobody, a hang-up.
- **A call back you promised and did not make.**

## Things I have learned

- Smile before you pick up. They hear it.
- The first price a caller asks for is not their real question. Their real question is "can I trust you with my car". Answer that one by asking about the car.
- Never price "brakes" without the car. Pads on a Corolla and pads on an F-250 are different jobs.
- When you offer two times, stop talking. Let them pick.
- If they say "I will call you back", ask "would it help if I held Friday at eight for you until tomorrow noon?" Then hold it.
- If the call is about a car that is already here, start with their name and end with what happens next and when.

How to answer a doubt about price: [Price objections](price-objections.md).

{S(16)}
""",
 serves=['S4', 'S3', 'S8', 'challenge:fact-in-table', 'challenge:near-duplicate', 'challenge:combine-kb-and-data'],
 facts=['The eight scorecard checks with their weights (calls design): greeting 1, name and number 2, need discovery 2, price with next step 2, offered time 3, asked for booking 3, recap 1, objection 2.',
        'Example lines are the level-2 lines of the calls design.',
        'Checks 5 and 6 carry the most weight; a call that ends on the price fails both.',
        'Checks do not apply when the customer is known, names a time, or raises no doubt.',
        'Automatic fails: wrong promise, dropped customer, promised call back not kept.',
        'Inspection price in the example line is the brake inspection menu price.',
        'Slot 6\'s weakest check is the objection (S4); slot 7\'s two wrong promises (S8, S12) are the first automatic fail.',
        'The approved team note "offer a time before the price on a first call" is about order and is deliberately not on this page; the page says "a price with a next step attached".'],
 new=['Holding a slot "until tomorrow noon" for an undecided caller (habit, no data footprint).'],
 rev=[(4, 'T-4mo', 'Angie\'s rewrite of the whole page around the eight checks when the scorecard came in (proposed by slot 16, approved by slot 4); message: "The call, in eight moves."', {'kind': 'proposal', 'proposer_slot': '16', 'approver_slot': '4'})],
 ru=['Example lines from the Russian side of the calls design («Ермак-Сервис, Алина, здравствуйте», «Завтра к девяти или в пятницу к девяти?»). Same weights.'])
# the example price in the table must come from the catalogue
import kbb
assert kbb.num_total('brake_inspection') == 49.95

page('how-to/price-objections.md', 'Price objections', 'J', 16,
 'What to say when a customer doubts the price; the weakest check on most scorecards.',
 f"""*{S(16,'full')} · Last reviewed {D('T-4mo')}*

A doubt about the price is a question, not a no. Most of us answer it by soothing ("I totally understand") or by repeating the time ("so, Friday at eight?"). Neither answers it.

The move is always the same: **find out what they are comparing with, then say what is in our number.**

| They say | You say |
|---|---|
| "That is a lot more than I expected." | "What were you expecting? ... Okay. Here is what is in ours:" then the parts by name, the labour, the warranty |
| "The other place said $300." | "For pads and rotors, or pads alone? Which pads?" Usually it is pads alone, or the cheapest pad. Then: "Ours at that level would be..." and give the economy price from the list |
| "Can you do it any cheaper?" | "I can do it with the economy parts for [price]. Same labour, same warranty on our work. What I would not do is skip the rotors if they are under size." That is a different job, not a discount |
| "I will think about it." | "Of course. What would help you decide: the price, or whether it really needs doing?" Then answer that. Then offer to hold a time |
| "Do I really need it now?" | The photo and the number. "Your pads are at 2 millimetres; new is 10. I would not go another month." If it can wait, say it can wait. They will believe you next time |
| "Why do I pay for diagnosis if I am getting it fixed here?" | "Because finding it is the skilled part, and you get the result in writing whatever you decide." [Diagnostic fees](../policies/diagnostic-fees.md) |
| "The dealer said it needs X." | "We will look at it ourselves first. If they are right you have lost nothing." |
| "Somebody here used to give me a cash price." | "We do not have one. The price is the same however you pay." [Discount policy](../policies/discounts.md) |

Rules:

- **We do not match prices.** We explain ours. A customer who only wants the lowest number is allowed to go and get it.
- Cheaper means a cheaper tier of parts, said out loud, never a quiet discount. You may give up to 10 % for a reason and the reason goes on the order.
- "It is all warrantied" is not an answer. Say what the warranty is: 24 months or 24,000 miles, parts and labour (pads and work vehicles 12 months).
- If you do not know why our price is what it is, find out before the next call. {S(5)} and I will always explain a line.

{S(16)}
""",
 serves=['S4', 'S2', 'challenge:fact-in-table', 'challenge:combine-policy-and-price', 'challenge:customer-terms'],
 facts=['Method: find the comparison, then say what is in the number.',
        'Eight objections with answers in one table; the answers point to the economy tier, the photo and measurement, the diagnostic-fee policy and the no-cash-price rule.',
        'Rules: no price matching; cheaper = a cheaper parts tier, never a quiet discount; up to 10 % with a reason on the order; say the warranty terms.',
        'The quoted competitor figure "$300" is a customer\'s words in an example, not a price of ours.',
        '"Pads at 2 millimetres; new is 10" is an example measurement.',
        'The calls design\'s level-2 objection line ("Did somebody quote it lower? Here\'s what\'s in that number") is this page\'s method.'],
 new=['No price matching. Reason: an objection page needs a stated position; it creates no ERP footprint.'],
 created=(4, 'T-4mo', 'proposal', {'proposer_slot': '16', 'approver_slot': '4', 'author_slot': '16'}),
 ru=['Russian objections: «дорого», «в гараже дешевле», «у официалов сказали», «а со своими запчастями?» (very common: point to the customer-parts page), «скидку сделаете?». Same method.'])

page('how-to/booking-a-visit.md', 'Booking a visit', 'J', 5,
 'How a booking is entered so the day works; step 6 is the read-back that the declined team note repeated (S4).',
 f"""*{S(5,'full')} · Last reviewed {D('T-2mo')}*

A booking is a promise about a bay and a technician, so it has to be true.

1. **Find the customer by phone number.** Do not make a new one if the phone is already there: [Customer records](../policies/customer-records.md).
2. **Which shop.** Say it out loud. People book East Main and drive to Bonny Oaks.
3. **The car and the complaint**, in their words. "Grinding from the front when braking, started Tuesday." Not "brakes".
4. **Pick the job from the catalogue** so the booking has hours on it. A noise or a light is an inspection or a diagnosis, not a repair.
5. **Pick the slot.**
   - Drop-off appointments at 7:30, 8:00 and 8:30. Waiters between 9:00 and 2:00, for jobs of an hour or less.
   - Check-engine and electrical work goes in the diagnostic column ({S(10)} at East Main, {S(18)} at Bonny Oaks). When the column is full, offer the next day.
   - Do not book a job longer than three hours after 1:00.
   - Mondays at Bonny Oaks before 9:30 belong to Millsaps.
6. **Read it back:** day, time, which shop, what we are doing. Every booking, every time, even to a regular. "So that is Friday at eight, East Main Street, for a brake inspection."
7. **Where it came from:** phone, web chat, messenger or walk-in. Fill it in. It is how we know what the chat is worth.
8. Shuttle needed? Say the times. Company vehicle? Unit number, and for Nickajack the purchase-order number.

The day before, every timed appointment gets a confirmation call or text by 3:00: [Cancellations and no-shows](../policies/cancellations-and-no-shows.md).

**From the website assistant.** The assistant cannot book. When a customer in the web chat wants a time, it hands the conversation over and a card lands on the board: who, what car, what they want, the times they offered. Whoever picks up the card books it here and answers the customer in the same conversation.
""",
 serves=['S4', 'S7', 'S5', 'challenge:three-page-procedure', 'operate:contradiction'],
 facts=['Eight steps: find by phone; which shop; car and complaint in the customer\'s words; job from the catalogue; slot rules; read-back; source; shuttle and fleet details.',
        'Slots: drop-offs 7:30, 8:00, 8:30; waiters 9:00-14:00 for jobs of an hour or less; diagnostics in slot 10\'s or slot 18\'s column; nothing over three hours after 13:00; Monday before 9:30 at east is A2\'s.',
        'Step 6, the read-back (day, time, shop, work), is the point of slot 6\'s team note "Read the booking back before hanging up", proposed on the Monday of week T-3 and declined by slot 4: "the page \'Booking a visit\' already says this; propose the wording there" (stories/S04, ledger s4.notes).',
        'Source of the booking is recorded (ERP appointment: phone, web chat, messenger, walk-in).',
        'The assistant cannot book; it raises a hand-over card and an advisor books (design 7.2 S7).',
        'Confirmation the day before by 15:00.'],
 new=['Slot rules: drop-offs at 7:30, 8:00, 8:30; waiters 9:00-14:00; nothing over three hours after 13:00. ERP appointment times should follow them.'],
 rev=[(4, 'T-2mo', 'Travis\'s addition of the paragraph "From the website assistant" (proposed by slot 5, approved by slot 4); message: "How chat bookings reach us."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})],
 ru=['Russian slots through the day 9:00-19:00; sources add VK and Avito. Same step 6.'])

page('how-to/checking-a-car-in.md', 'Checking a car in', 'J', 5,
 'The counter\'s part of receiving a car: walk-round, mileage, the complaint, keys.',
 f"""*{S(5,'full')}*

Five minutes at the car save an hour of arguing at pick-up.

1. **Walk round it with the customer.** Dents, scratches, cracked glass, warning lights on the dash: say them out loud and note them. Take four photos, one per corner.
2. **Mileage** off the dash, typed, not guessed. If it is lower than last time, look again; you have probably dropped a digit.
3. **The complaint in their words**, and when it happens: cold, hot, braking, turning, at speed. If they can, ride with the technician for the noise.
4. **What they are not asking for.** "Anything else it is doing?" You would be surprised.
5. **How to reach them today**, and until when. Text or call. Who else may approve work.
6. **The inspection:** tell them it is free and that they will get photos. Almost nobody says no.
7. **Keys:** tag with the order number, on the board. Wheel-lock key? Ask now, not when the wheels are coming off.
8. **A time for the first call from us.** "You will hear from me by eleven with what we found." Then they do.
9. Open the order from the appointment. Check it is the right car on the right customer.

Do not promise when it will be done at this point. You do not know yet. Promise when you will call.
""",
 serves=['challenge:three-page-procedure', 'S15', 'S7'],
 facts=['Nine steps: walk-round with four corner photos; mileage from the dash (ERP mess kind 3); complaint in the customer\'s words with conditions; "anything else"; contact and who else may approve; the free inspection; keys tagged, wheel-lock key asked for; a time for the first call; order opened from the appointment with car and customer checked (mess kind 8).',
        'No completion time is promised at check-in; a call time is.'],
 ru=['Russian: акт приёма-передачи автомобиля signed with damage noted; mileage in km.'])

page('how-to/company-vehicle-at-the-counter.md', 'A company vehicle at the counter', 'J', 4,
 'What changes when the car belongs to a company account: unit number, purchase order, who may approve.',
 f"""*{S(4)} · Last reviewed {D('T-4mo')}*

When a driver puts keys on the counter, the customer is not the driver. It is the company.

1. **Whose is it?** Find the vehicle by plate or unit number. It must be under the company, with the unit number.
2. **Is it an account?** The six are in the [terms table](../accounts/company-account-terms.md). Anybody else is a [small business customer](../accounts/small-business-customers.md) and pays at pick-up.
3. **Nickajack: purchase-order number first.** No number, call their fleet manager before the order is opened.
4. **What was booked?** Do that. It is approved.
5. **What else did we find?** A driver may approve up to **$300 for the whole visit**. One limit, every account.
   - Inside it: the driver may say yes. Write the driver's name as the approver.
   - Over it, a driver cannot approve the work: call the person in the "Approves work" column. Not the driver's supervisor, not whoever answers their main line.
   - Nobody reachable: booked work only. Estimate to the fleet contact within four working hours.
6. **Nothing is paid at the counter.** It goes on the statement.
7. If the driver is unhappy about waiting for an approval, that is fine. It is his company's rule, written down by his own boss.

A driver saying "go ahead, they will be fine with it" is not an approval over the limit, however sure he sounds.
""",
 serves=['S4', 'S1', 'challenge:combine-policy-and-price', 'challenge:policy-vs-team-note'],
 facts=['The customer is the company; the vehicle is found by plate or unit number.',
        'Six accounts are in the terms table; others are small business customers.',
        'A1 needs its purchase-order number before the order is opened.',
        'Booked work is approved; a driver approves found work up to 300 USD per visit (ledger s4.driver_limit); over it the named approver is called; unreachable: booked work only and an estimate within four working hours.',
        'Nothing is paid at the counter for an account.',
        'Story call 7: a company driver says "go ahead" to 380 USD of found work: over the limit, so the fleet contact is called.'],
 rev=[(4, 'T-4mo', 'rewritten around the driver limit when it was written into the Company accounts page; message: "Driver limit."')],
 ru=['Russian drivers bring a доверенность or the company sends a заявка; approval by the company\'s responsible person.'])

page('how-to/writing-an-estimate.md', 'Writing an estimate', 'J', 5,
 'Step two of the inspection-to-approval procedure: turning inspection findings into an estimate.',
 f"""*{S(5,'full')} · Last reviewed {D('@belt_proposal')}*

You have the technician's [inspection](../shop-floor/courtesy-inspection.md): what is Good, what is Watch, what is Bad, with measurements and photos. Now it becomes an estimate.

1. **Start with what the customer came for.** That job first, even if the inspection found something bigger.
2. **Every Bad line becomes a job on the estimate.** Pick it from the catalogue. If the technician typed a job by hand that is in the catalogue, change it to the catalogue job.
3. **Watch lines do not go on the estimate as jobs.** They go in the notes with the measurement, so the customer sees them and we find them next visit. Exception: a Watch item that shares labour with a Bad one. Say so: "while we are in there".
4. **Price from the [price list](../prices/price-list.md). Nowhere else.** Not from memory, not from the last invoice, and not from a service page: those explain the job, and they can be out of date. The shop system prices a catalogue job for you; check it against the list if it looks odd.
5. **Standard tier** unless the customer asked otherwise. Have the economy and premium figures ready; do not lead with them.
6. **Vehicle class.** A pickup or a van is not a car: [multipliers](../prices/labour-rates-and-fees.md).
7. **Order the jobs** by what matters: safety, then what will strand them, then what will cost more if left, then the rest.
8. Shop supplies and tax are added by the system. Read the customer the total with tax, because that is what they pay.
9. **Parts:** ask {S(9)} whether they are on the shelf or on a run before you talk about time.
10. Send it the same working day. Then [get the approval](getting-approval.md).

If the estimate is over $1,000, have your lead look at it before it goes. Not for permission. A second pair of eyes catches the wrong part.
""",
 serves=['challenge:three-page-procedure', 'S8', 'S12', 'S7'],
 facts=['Step 2 of 3 (after shop-floor/courtesy-inspection.md, before how-to/getting-approval.md).',
        'The requested job first; every Bad line becomes a catalogue job; Watch lines go in the notes with the measurement, except when they share labour with a Bad item.',
        'Prices come from the price list only; service pages can be out of date (the rule slot 7 broke, S8).',
        'Standard tier by default; vehicle class multipliers; ordering by safety, breakdown risk, cost of delay.',
        'The total is read with tax.',
        'Parts availability checked with slot 9 before any time is mentioned.',
        'Sent the same working day.',
        'Estimates over 1,000 USD get a second look from the lead advisor.'],
 new=['The 1,000 USD second-look rule (habit, no data footprint).'],
 rev=[(4, '@belt_proposal', 'step 4 rewritten after the timing-belt complaint (proposed by slot 5, approved by slot 4): "not from a service page" added; message: "Price list only."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})],
 ru=['Russian estimate = предварительный заказ-наряд (смета); parts tier naming from the Russian catalogue.'])

page('how-to/getting-approval.md', 'Getting approval', 'J', 16,
 'Step three of the inspection-to-approval procedure: sending the estimate, chasing it, recording the answer.',
 f"""*{S(16,'full')} · Last reviewed {D('T-5mo')}*

The estimate is written ([how](writing-an-estimate.md)). Nothing is sold until somebody says yes, and nothing is started until the yes is on the order.

## Send, then call

1. Send the estimate by text or e-mail with the photos. The customer can approve each job from the link.
2. **If anything on it is Bad, call within 30 minutes of sending.** Do not wait for them to open it. "I have sent you the pictures. The short version is..." Photo before price, then the price, then two times.
3. If everything is routine and they said "just text me", let the text do its work for two hours.

## Chase

| When | What |
|---|---|
| 2 hours, no answer | Call. No answer: a short voicemail and a text saying you called |
| 4:00 the same day | Call again. Tell them where the car is: in a bay, or outside and locked |
| Next morning, first hour | Third and last call. After this the car is waiting on them, and that is written on the order |

A car that sits on a lift waiting for an answer costs a technician his afternoon. If there is no answer by the 4:00 call, ask the foreman whether to pull it out.

## Record

- Mark **each job** approved or declined. Not the order.
- Who said yes, how (link, phone, counter), and the time. For a phone yes, read the job and amount back first.
- Company vehicles: the driver limit, then the fleet contact. [The rule](company-vehicle-at-the-counter.md).
- Declined and still needed: tick deferred. It will come back as a reminder, and it is the first thing to raise next visit.

## Then

Approved jobs go to the foreman's board and the parts to {S(9)}. Tell the customer when you will call next, not when it will be done, unless the parts are on the shelf: [what you may promise](../parts/ordering-parts.md).

{S(16)}
""",
 serves=['challenge:three-page-procedure', 'S1', 'S7', 'challenge:fact-in-table'],
 facts=['Step 3 of 3.',
        'Estimate sent by text or e-mail with photos and an approval link per job.',
        'A Bad item is followed by a call within 30 minutes of sending; routine estimates wait two hours.',
        'Chase table: 2 hours (call, voicemail, text); 16:00 the same day; first hour next morning (third and last).',
        'A car waiting on a lift is raised with the foreman after the 16:00 call.',
        'Each job marked approved or declined with who, how, when (ERP order_job); phone approvals read back; deferred work ticked.',
        'Approved jobs go to the foreman and the parts to slot 9; the next call time is promised, not the finish.',
        'S7: the customer approved the brakes by message and declined the shock absorber (deferred, reminder).'],
 new=['The 30-minute call and the three-step chase (2 hours, 16:00, next morning).'],
 ru=['Russian approval is mostly by phone (calls design: outbound approval calls 35 %); messengers carry the photos.'])

page('how-to/handing-a-car-back.md', 'Handing a car back', 'J', 5,
 'The pick-up: walking the bill, old parts, deferred work, the next visit.',
 f"""*{S(5,'full')}*

The customer remembers two moments: the phone call with the price and the two minutes at pick-up. This is the second.

1. **Have the car out front** and the invoice ready before they arrive. Check the car yourself: clean wheel, no warning lights, seat cover out.
2. **Walk the invoice** line by line, in plain words. What they came for, what we found, what we did. Parts and labour for each. Then supplies, tax, total. The total should be the number they approved. If it is not, you should have called them before now.
3. **Old parts.** If they asked, show them. If they did not ask and the part tells the story (a pad worn to the metal), show it anyway.
4. **What was not done.** Read the declined and Watch items out, with the measurement. "Rear shocks are leaking. Not dangerous this month. I would do them before winter." It is on the invoice; say it as well.
5. **The warranty** in one sentence: 24 months or 24,000 miles on what we did today (pads and work vehicles 12 months).
6. **Next visit.** When the next oil service is due, and anything deferred. Offer to book it now.
7. **Payment**, receipt, keys. Company accounts sign and go; it is on the statement.
8. "If anything does not feel right, call me, not the internet." And give them your name again.

If the customer is unhappy at the counter, do not fix it with the bill. [Complaints](../policies/complaints.md).
""",
 serves=['S7', 'S8', 'challenge:three-page-procedure'],
 facts=['Eight steps: car ready and checked; invoice walked line by line, total equals the approved amount; old parts shown; declined and Watch items read out; warranty in one sentence; next visit offered; payment (accounts sign); a named person to call.',
        'S8: the argument at the desk at T-9 days happened at this step, with a bill above the quote.',
        'S7: the declined rear shocks were read out and deferred.'],
 ru=['Russian: the customer signs the акт выполненных работ; old parts are returned by default if asked at check-in.'])

page('how-to/closing-the-till.md', 'Closing the till', 'J', 3,
 'The company procedure for counting the cash drawer at the end of the day.',
 f"""*{S(3,'full')}, office · In force from {D('@discount_rule')}*

The till is closed by the advisor on the closing shift, at every shop, every day we are open.

1. Print the day's payment report from the shop system. It shows the cash the system expects.
2. Count the drawer. Take out the float (East Main $200, Bonny Oaks $150, Charlotte Pike $150). What is left is the day's cash.
3. Enter the counted amount. The system shows the difference.
4. **A difference of more than $5.00, over or short:** write the reason on the count sheet if you know it, and "not known" if you do not. Tell your shop manager before you leave. He tells me the same evening.
5. Card slips and checks go in the bag with the cash and the count sheet. Seal it. Write the amount and your initials on the bag.
6. The bag goes where your shop's page says: [East Main](../shops/main/opening-and-closing.md), [Bonny Oaks](../shops/east/opening-and-closing.md), [Charlotte Pike](../shops/west/opening-and-closing.md).

Please note:

- At Charlotte Pike the drawer is counted by two people and both initial the sheet.
- Nothing is paid out of the till. No parts, no lunches, no change for the machine. Petty cash is separate and I hold it.
- An order is never voided to make the till agree. [Voids and refunds](../policies/voids-and-refunds.md).
- A small difference is ordinary. The same person short week after week is not, and I see it at month end.

Thank you.
""",
 serves=['S2', 'challenge:near-duplicate-shop-pages', 'challenge:combine-policy-and-price'],
 facts=['Closed daily by the advisor on the closing shift at each shop (ERP cash_drawer_close: expected, counted, difference).',
        'Floats: East Main 200, Bonny Oaks 150, Charlotte Pike 150 USD; the float is removed before the count is entered, so "expected" is the day\'s cash without the float.',
        'Differences over 5.00 either way are written with a reason and reported to the shop manager, who tells slot 3 the same evening.',
        'Slips, checks and count sheet go in the sealed, initialled bag; where the bag goes is on each shop\'s own page.',
        'Charlotte Pike: two counts.',
        'Nothing is paid out of the till; no void to make the till agree.',
        'Slot 3 reviews differences at month end (how S2 was caught).'],
 new=['The 5.00 USD reporting threshold; the three floats in one sentence. The till counts in the ERP: "short" days of slot F1 exceed the threshold; ordinary days stay inside it.'],
 created=(2, '@discount_rule'),
 ru=['Russian: закрытие смены на кассе (Z-отчёт), сверка наличных; floats in RUB; the threshold for example 300 RUB.'])

page('how-to/missed-calls-and-call-backs.md', 'Missed calls and call backs', 'J', 4,
 'How the missed-call list is worked; the standard after the early desk shift.',
 f"""*{S(4)} · Last reviewed {D('@early_desk')}*

Half the people whose call we miss never ring again. They ring somebody else.

- The **To call back** list shows every caller we missed in the last seven days who has not been reached since. Oldest first.
- **Claim a caller before you dial**, so two of us do not ring the same person. A claim puts a card on your board. If you have not called within 30 minutes the claim lapses and the caller goes back on the list.
- **Standard: called back within one hour**, and the same day without exception.
- No answer: leave a short message with your name and our number. Try again after two hours and once more the next morning. Three tries.
- If they got through to someone else in the meantime, the list clears it by itself.
- Dismiss only wrong numbers, robots and suppliers. Never a customer.
- A call missed while we were closed is not held against anybody's desk. It is still a customer: the early desk works those first.

**East Main mornings.** From 7:30 to 10:00 one of the two advisors at the desk is on the phone and nothing else: [How the day runs](../shops/main/how-the-day-runs.md). Before {D('@early_desk')} we were missing nearly one call in three in those hours.

**A call back you promised** ("I will ring you by two") is not on any list. It is on you. Put it in your calendar while you are still on the phone.

Callers who fell off the seven-day list without being reached are still in the call history. {S(4)} looks for those on Fridays.
""",
 serves=['S3', 'S1', 'challenge:combine-kb-and-data'],
 facts=['The To call back list shows missed callers of the last seven days not reached since (product: the queue shows seven days).',
        'Claiming raises a card on the claimer\'s board; the claim lapses after 30 minutes (product).',
        'Standard: one hour, same day; three tries (message on the first, again after two hours, next morning).',
        'A later answered call clears the miss automatically; only wrong numbers, robots and suppliers are dismissed.',
        'Out-of-hours misses are not counted against a desk (S13) and are worked first by the early desk.',
        'East Main 7:30-10:00: one advisor is phone-only; before {{@early_desk}} "nearly one call in three" was missed in those hours (S3: 31 %).',
        'Promised call backs are the advisor\'s own; the calendar is suggested.',
        'Callers older than seven days stay in the call history (S1: account A5\'s three misses are found there, not in the queue); slot 4 looks on Fridays.'],
 new=['Slot 4 checks the call history on Fridays for callers who fell off the list. Reason: explains how A5\'s misses could be found; it does not say he found them.'],
 rev=[(4, '@early_desk', 'standard changed from two hours to one, the East Main paragraph added; message: "Early desk from today."')],
 ru=['Same product rules; Russian rush 9:00-11:30.'])

page('how-to/chats-and-messages.md', 'Chats and messages', 'J', 6,
 'How web chat and messenger conversations are answered alongside the assistant.',
 f"""*Written by {S(6)} · published by {S(4)} {D('T-3mo')}*

We get messages two ways: the **web chat** on our site and **Telegram**.

## What the assistant does

- **Web chat:** the assistant answers by itself, from the pages customers may be shown: [Customer answers](../customers/README.md), the service pages and the price list. Nothing else. It can explain a service, give a menu price, say our hours. It cannot see a customer's car or history and it cannot book. When the customer wants a time, or asks something that is not on those pages, it hands the conversation to us and a card appears on the board.
- **Telegram:** the assistant only drafts. Nothing goes out until one of us reads the draft, fixes it and sends it.

## What we do

- First reply within **10 minutes** in opening hours. A handed-over chat is a customer who has already waited.
- Open the conversation, read all of it, then answer. Do not make them repeat what they told the assistant.
- Find them by phone number. A chat, a call and a visit are one person; put them on one customer record.
- A draft is a start. Check every price in it against the [price list](../prices/price-list.md) and every time against the schedule before you press send. You are the one sending it.
- Repair prices are not given in a chat for a car we have not seen. Menu prices and "from... to" ranges that are on the public pages are fine.
- One question per message is how customers write. Answer all of them, not the first.
- When it is booked, say the booking back in the chat: day, time, shop, the work.
- Close the conversation when it is done, so the open list is the list of people waiting.

If the assistant said something wrong, tell {S(4)} the same day with the conversation. Usually the page it read is wrong, and the page is what gets fixed.
""",
 serves=['S7', 'S12', 'challenge:combine-kb-and-data', 'visibility:public'],
 facts=['Channels in the English configuration: web chat and Telegram (design O3).',
        'Web chat: the assistant sends, from the public pages only (customers/, services/, the price list; also shop-floor/, which is at the same rank); it cannot see customer data or book; it hands over with a card.',
        'Telegram: the assistant drafts; a person sends (S7: the open Telegram conversation with a draft waiting).',
        'First reply within 10 minutes; read the whole thread; one contact per phone (S7: one person across three stores by her phone).',
        'Drafts are checked against the price list and the schedule.',
        'No repair prices in chat for an unseen car; menu prices and public ranges are fine.',
        'Booked work is read back in the chat; conversations are closed when done.',
        'A wrong answer from the assistant usually means a wrong page.',
        'Juniors cannot publish: slot 6\'s text, published by slot 4.'],
 created=(4, 'T-3mo'),
 ru=['Channels: web chat, Telegram, VK, Avito (design O3). Say which channels the assistant sends in and which it drafts in, per the tenant settings of the Russian configuration.'])

page('how-to/a-comeback-at-the-counter.md', 'A comeback at the counter', 'J', 4,
 'What an advisor does and says when a customer returns with the same problem.',
 f"""*{S(4)} · Last reviewed {D('T-4mo')}*

"I was just here and it is doing it again."

1. **"Thank you for bringing it straight back."** Mean it. The ones who do not come back are the ones we lose.
2. Find the first order. Read what was done and who did it before you say anything about the cause.
3. **Open a new order, type warranty, tied to the first one.** Do not reopen the old order and do not write it up as a new customer-pay job "until we know".
4. It goes to the front of the line. The foreman looks first: [When a car comes back](../shop-floor/when-a-car-comes-back.md).
5. Tell the customer when they will hear: today, with a time.
6. Do not guess the cause at the counter and do not blame the part, the technician or the customer. "We will find out and I will call you by two."

## After the foreman has looked

| What he found | What happens |
|---|---|
| Our work or our part, inside the warranty | Fixed at no charge. Say so before they ask. Offer the shuttle |
| Our work, outside the warranty | {S(4)} or {S(22)} decides. Usually we fix it: goodwill order |
| A different fault with the same symptom | Explain with the old part or a photo. Estimate like any job. No charge for the look |
| The customer's own part | Labour is charged again. This was said at the start; say it kindly |
| Not sure | It is {S(4)}'s call, not yours. The same day |

The inspection of a comeback is never charged, whatever it turns out to be.

A second comeback on the same repair goes straight to {S(4)} or {S(22)}, with both orders.
""",
 serves=['S6', 'S1', 'challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Six counter steps; the new order is of type warranty tied to the original (design 2.3).',
        'Outcome table: our fault inside warranty = free; outside warranty = goodwill decided by slot 4 or 22; a different fault = estimate, no charge for the look; customer\'s part = labour charged again; unsure = slot 4 the same day.',
        'A comeback inspection is never charged.',
        'A second comeback on the same repair goes to slot 4 or slot 22 with both orders (A5\'s two vans came back at west: S1, S6).'],
 new=['The look at a comeback is free; second comebacks escalate.'],
 ru=['Same; the window is 30 days.'])

page('how-to/stocktake-day.md', 'Stocktake day', 'J', 9,
 'What happens on the half-yearly stocktake afternoon (S13).',
 f"""*{S(9,'full')}, parts · Next count: {D('@stocktake','day')}*

Twice a year we count every part in all three shops. **All shops close to customers at 12:00 noon that day.**

## Before the day

- The date goes on the public [hours page](../customers/hours-and-locations.md) and on the door two weeks ahead.
- No appointment is booked that day after 10:30. Nothing over two hours is booked at all.
- Cars finished that morning are picked up before noon or the next day. Tell customers when they book and again on the ready call.
- I order nothing that morning that is not for a car in a bay.

## On the day

- 12:00: doors locked, phones to the closed message. The key drop stays open.
- Nobody is on the desk. Everybody is on the schedule as stocktake and everybody counts, advisors too.
- Pairs: one counts, one writes. Never count alone and never count your own bay.
- Count sheets are by shelf. Count what is there, not what the sheet says should be.
- Parts already pulled for a car in a bay get a tag with the order number and are counted as issued.
- No part leaves a shelf during the count. A car that needs one waits.
- Any line that differs by more than $50 is counted again by a different pair.
- We are done about 4:00.

## Charlotte Pike

Counts its own stock the same afternoon, on its own clock. {S(22)} sends me the sheets by 5:00 Central.

## After

Differences go to {S(3)} and {S(2)} within the week. Stock that is on the system and not on the shelf is the number I care about.
""",
 serves=['S13', 'challenge:combine-kb-and-data'],
 facts=['Twice a year; all three shops close to customers at 12:00 noon on {{@stocktake}} (the Thursday of week W+1, ledger site.stocktake).',
        'Announced on the public hours page and the door two weeks ahead.',
        'No appointment after 10:30 that day; nothing over two hours.',
        'Pick-ups before noon or the next day; key drop stays open; phones on the closed message.',
        'No desk shifts: everyone is scheduled as stocktake (design S13: no desk shifts that afternoon).',
        'Pairs count; nobody counts their own bay; lines differing by more than 50 USD are recounted.',
        'Done about 16:00; west counts on its own clock and sends sheets by 17:00 Central.',
        'Differences reported to slots 3 and 2 within the week (ERP stock_movement: adjustments).',
        'The public page gained its notice on the Monday of week W-1, seventeen days ahead of the Thursday of week W+1.'],
 new=['No appointments after 10:30 on the day; the 50 USD recount rule. ERP appointments on the stocktake day must stop at 10:30.'],
 rev=[(4, '@stocktake_notice', 'date of the next count filled in (Marcus\'s page, published by slot 4); message: "Stocktake date."')],
 ru=['Инвентаризация; Russian shops close at 14:00 or as the Russian design sets it; the Russian rule on recount in RUB.'])

page('how-to/using-this-knowledge-base.md', 'Using and fixing this knowledge base', 'J', 2,
 'How to search, how to read a page\'s date, how a correction is proposed and decided.',
 f"""*{S(2,'full')} · Last reviewed {D('@belt_proposal')}*

## Finding things

Search for the word the customer used. If that finds nothing, try the word on the invoice: customers say "tune-up", "freon", "front end"; the pages say spark plugs, A/C recharge, alignment.

You can also ask the assistant. It reads these pages for you and tells you which page it read. It sees what you may see and nothing more.

## Before you trust a page

Look at the line under the title. *Last reviewed* tells you how old it is. A page reviewed before {D('@price_rise')} was written at the old labour rate. A page with no date at all is older than you think.

**Prices are quoted from the [price list](../prices/price-list.md), whatever a service page says.**

## Fixing a page

| You are | You can |
|---|---|
| A lead advisor, the office manager, or above | **Propose** a change: on the page, or ask the assistant to draft it and confirm the card. Say why |
| {S(4)}, {S(22)}, {S(1)} or me | **Publish** a change, and approve or decline a proposal |
| Anyone else | Tell your lead advisor what is wrong and where. Today |

A proposal shows the exact words that change. It waits in the Inbox of the people who can decide it. We decide within five working days, and if we decline we say why.

Every page keeps its history: who changed what, and their reason.

## What goes where

- Something every customer may be told: [Customer answers](../customers/README.md). Write it for a customer; the website assistant quotes it. It reads the service pages and the price list as well, so a wrong figure there can reach a customer.
- How we do a job: [How we do things](README.md).
- A fact about one company account: that account's page.
- No private customer's name, phone or car on any page. That lives in the shop system.
- A habit of yours that works: a note to yourself. If the whole team should do it, it becomes a line on a page here.
""",
 serves=['S12', 'S4', 'operate:propose', 'operate:find-waiting', 'operate:find-what-changed'],
 facts=['Search with the customer\'s word, then the invoice word.',
        'The assistant reads only what the asking person may see and names the page it read.',
        'Check the "Last reviewed" line; pages reviewed before {{@price_rise}} carry the old labour rate.',
        'Rungs (product defaults): propose from middle rank (lead advisors, office manager); publish and decide from senior rank (slots 4, 22, 1) and the administrator (slot 2); others tell their lead.',
        'A proposal shows the exact change, waits in the deciders\' Inbox, is decided within five working days, and a decline carries a reason.',
        'Every page keeps its history.',
        'Placement rules: public answers in customers/; procedures in how-to/; account facts on account pages; no private customer data; team-wide habits become page lines (the reason slot 6\'s note was declined).'],
 rev=[(2, '@belt_proposal', 'added the section "Before you trust a page"; message: "Read the date line."')],
 ru=['Same rungs.'])
