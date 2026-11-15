from kbb import *

def C(aid, i, f='name'):
    c = ACCOUNTS[aid]['contacts'][i]
    return c[f]

page('accounts/company-account-terms.md', 'Company accounts', 'J', 2,
 'The terms every company account is served on: payment days, price class, priority, who may approve work. Story S1\'s page.',
 f"""*Terms set by {S(2,'full')} · Kept by {S(4,'full')} · Last reviewed {D('T-2mo')}*

A company account is a business we bill on a monthly statement instead of at the counter. We have six. Small businesses without an account are on [their own page](small-business-customers.md).

## The six accounts

| Account | Home shop | Pays in | Prices | Approves work | Purchase-order number |
|---|---|---|---|---|---|
| [{A('A1')}](a1.md) | East Main | 30 days | Company rate | {C('A1',0)}, fleet manager | **Required on every order** |
| [{A('A2')}](a2.md) | Bonny Oaks | 30 days | Company rate | {C('A2',0)}, dispatcher, up to $1,000 a vehicle; {C('A2',1)} above that | Not used |
| [{A('A3')}](a3.md) | East Main | 15 days | List | {C('A3',0)} | Not used |
| [{A('A4')}](a4.md) | Bonny Oaks | 15 days | List | {C('A4',1)} up to $500; {C('A4',0)} above that | Not used |
| [{A('A5')}](a5.md) | Charlotte Pike | 30 days | List | {C('A5',0)} | Not used |
| [{A('A6')}](a6.md) | East Main | 30 days | List | {C('A6',1)} | Not used |

## Payment

- {S(3)} issues each account's statement on the first working day of the month, for the month before. It lists every invoice by vehicle unit number.
- It is due 30 or 15 days from the statement date, as in the table.
- Nothing is collected at the counter and no deposit is taken.
- Interest of 1.5 % a month may be charged on a balance more than 30 days overdue. Whether it is charged is {S(2)}'s decision, not the counter's.

## Prices

"Company rate" is a price class, not a discount: labour at {rate('company_account')} an hour instead of {rate()}, and 10 % off the list price of parts. Menu-priced jobs are 10 % under the menu price. Shop supplies and tax apply as usual. Only {A('A1')} and {A('A2')} have it. Everybody else pays the price list.

## Priority

- A company vehicle that cannot work is looked at **the day it arrives**, ahead of retail cars that are waiting. Say so to the retail customer plainly if they ask; do not hide it.
- {A('A2')} has a standing slot every Monday at 7:30 at Bonny Oaks for five vans, and its vans come first on Monday mornings.
- Routine fleet maintenance is booked like any appointment.

## Who may approve work

1. Work the fleet contact booked is approved when it is booked.
2. Anything found beyond it: **a driver may say yes up to $300, for the whole visit, not per job.** Above $300 a driver cannot approve work: call the person in the "Approves work" column. Write who approved on the order.
3. If you cannot reach them, do the booked work, put the rest on an estimate and send it. The four-hour estimate standard applies.
4. A vehicle that is unsafe to drive is not released on a driver's say-so. Call the fleet contact and then {S(4)}.

## Also

- Every order carries the unit number and the mileage in.
- Company vehicles are in business use: warranty is 12 months or 12,000 miles ([Warranty](../policies/warranty.md)).
- No storage charges. A fleet vehicle sitting more than a week: tell {S(4)}.
- A complaint from a company account goes to {S(4)} the same day, whichever shop it came to.
- New accounts: [Opening a company account](opening-a-company-account.md). Credit limits and overdue balances are the office's.
""",
 serves=['S1', 'S4', 'S16', 'challenge:fact-in-table', 'challenge:combine-policy-and-price', 'operate:contradiction', 'challenge:policy-vs-team-note'],
 facts=['Six accounts with home shop and payment days as in accounts.json: A1 main 30, A2 east 30, A3 main 15, A4 east 15, A5 west 30, A6 main 30.',
        'Price class "company rate" (121.50 an hour, 10 % off parts list, menu jobs 10 % under menu) is held by A1 and A2 only (catalogue company_account_terms).',
        'Approvers: A1 Lonnie Coffey; A2 Tina Ragsdale up to 1,000 USD a vehicle, Hal Millsaps above; A3 Yolanda Fitch; A4 Rob Atchley up to 500, Denise Atchley above; A5 Wade Carlisle; A6 Erin Castillo (the new contact, since T-5 months).',
        'One driver limit for every account: 300 USD per visit; above it the fleet contact is called (ledger s4.driver_limit).',
        'A1 needs its purchase-order number on every order (design S1).',
        'Statements issued the first working day of the month for the month before, listing invoices by unit number; due 30 or 15 days from the statement date.',
        'Interest 1.5 % a month on balances over 30 days overdue, at slot 2\'s discretion.',
        'Priority: a company vehicle that cannot work is seen the day it arrives; A2 has a standing slot Monday 7:30 at east for five vans and comes first on Monday mornings (ledger acct.A2.weekly_slot).',
        'Approval order: booked work; driver up to the limit for the whole visit; above it the named approver; unreachable: booked work only and an estimate within four working hours; unsafe vehicles are not released on a driver\'s word.',
        'Warranty 12/12; no storage; complaints to slot 4 the same day.',
        'This page names Erin Castillo for A6; the account\'s own page still names Bobby Shadden: planted contradiction between two pages.',
        'Slot 6\'s waiting team note "a company driver cannot approve work over 300 USD; call the fleet contact" repeats what this page says.'],
 new=['The two-step approvers for A2 (the dispatcher up to 1,000 USD a vehicle, the president above) and A4 (the lead instructor up to 500, the owner above). Reason: the design asks for "who may approve work"; the ledger fixes only the driver limit.',
      'Statement on the first working day of the month; interest 1.5 % a month at discretion (no interest is charged in the data).'],
 rev=[(2, '@price_rise', 'company rate 112.50 to 121.50; message: "New prices from today."'),
      (4, 'T-4mo', 'added the purchase-order column and the Monday priority for Millsaps, moved here from team notes; message: "Customer facts belong on the account pages, not in notes."'),
      (4, 'T-2mo', 'Sourwood\'s approver changed from Bobby Shadden to Erin Castillo; message: "New fleet contact at Sourwood."')],
 ru=['Russian accounts are billed per order with closing documents (акт, счёт-фактура or УПД) and pay by bank transfer within the contract\'s days (30 or 14); no monthly statement, so "Payment" is rewritten (R11). The purchase-order number becomes «номер заявки» of the customer. Contract hour 1 700 RUB. Interest: пеня по договору.'])

page('accounts/a1.md', 'Nickajack Delivery', 'J', 4,
 'Standing instructions for the anchor account A1.',
 f"""*{S(4)} · Last reviewed {D('T-4mo')}*

Our largest customer. Thirty-five delivery vans, served at East Main. Treat every van as if {S(1)} were watching, because he asks.

## People

| Who | What for | Phone |
|---|---|---|
| {C('A1',0)}, fleet manager | Books vans, approves work | {C('A1',0,'phone')} |
| {C('A1',1)}, accounts payable | Statements, anything about a bill | {C('A1',1,'phone')} |
| {C('A1',2)}, director of operations | The quarterly review. Do not call him about a van | {C('A1',2,'phone')} |

## The purchase-order number

**Every order needs Nickajack's purchase-order number before the van is worked on.** {C('A1',0).split()[0]} gives it when he books. If a driver turns up without one, call {C('A1',0).split()[0]} and get it before you open the order. It goes in the purchase-order field, not in the notes. An invoice without it is sent back by their accounts payable and is not paid until it is fixed.

## The fleet

Ford Transit 250, Ram ProMaster 2500, Ford Transit Connect and two Mercedes Sprinters (units ND-34 and ND-35). Unit numbers are ND-01 to ND-35 and are on the driver's door.

- **Fleet PM service A** every 5,000 miles: [what it includes](../services/maintenance/fleet-pm-service.md). {C('A1',0).split()[0]} sends the units that are due each week.
- The Sprinters are diesel. We do their fluids, filters, brakes and tires. Engine and emissions work on them goes to the dealer; tell {C('A1',0).split()[0]}, do not attempt it.
- Vans are dropped by 7:30 and needed back by 3:00 for the afternoon routes. If one will not make 3:00, {C('A1',0).split()[0]} hears by noon.

## Approvals

A driver may approve up to $300 for the visit, as for every account. Above that, {C('A1',0)}. Terms, prices and the rest: [Company accounts](company-account-terms.md).

## The quarterly review

Every quarter {S(4)} and {S(2)} sit down with {C('A1',0)} and {C('A1',2)}. We bring: visits and spend by month, vans due for brakes and tires next quarter, comebacks, and how long statements are taking to be paid.
""",
 serves=['S1', 'S16', 'S4', 'challenge:fact-in-table'],
 facts=['Account A1: 35 vans, home shop main; contacts and phones from accounts.json (Lonnie Coffey fleet manager, Linda Qualls accounts payable, Stuart Haney director of operations).',
        'The purchase-order number is required before work, given by the fleet manager at booking, entered in the order\'s purchase-order field (ERP repair_order.purchase-order number); invoices without it are returned unpaid.',
        'Fleet: Transit 250, ProMaster 2500, Transit Connect, two Sprinters ND-34 and ND-35; units ND-01 to ND-35.',
        'Fleet PM service A every 5,000 miles; due units sent weekly.',
        'Sprinters are diesel: fluids, filters, brakes and tyres only.',
        'Drop by 7:30, back by 15:00; a late van is reported by noon.',
        'Driver limit 300 USD per visit (ledger s4.driver_limit).',
        'Quarterly review: slots 4 and 2 with Lonnie Coffey and Stuart Haney; agenda: visits and spend by month, vans due, comebacks, days to pay (S16: the review meeting of ledger s16.card).',
        'The page does not say that A1 pays later every month: that is in the data only.'],
 new=['PM interval 5,000 miles; drop 7:30 and back by 15:00; noon warning. Reason: standing instructions a fleet page needs; the ERP\'s PM orders for A1 should recur about every 5,000 miles per van.',
      'The Sprinters are diesel and limited to fluids, filters, brakes and tyres.'],
 rev=[(4, 'T-4mo', 'added the section "The purchase-order number", moved from a team note; message: "PO number rule lives here now."')],
 ru=['Russian anchor: «Симбирский гонец», служба доставки, 35 фургонов (ГАЗель etc. from the Russian accounts file). The purchase-order number is «номер заявки». Contacts from accounts.json ru.'])

page('accounts/a2.md', 'Millsaps Heating & Plumbing', 'J', 16,
 'Standing instructions for account A2, the happy path.',
 f"""*{S(16)}, Bonny Oaks · Last reviewed {D('T-4mo')}*

Twenty-five vehicles, mostly service vans, a few trucks. They have been with us longer than I have, and they come every single week.

## The Monday slot

Every Monday at 7:30 we take **five Millsaps vans**. {C('A2',0)} in their dispatch sends me the unit numbers and what each one needs by Friday noon. On Monday mornings their vans go first, ahead of everything else at Bonny Oaks. If Monday is a holiday the slot moves to Tuesday.

Their technicians are on call, so a van that comes in Monday is back with them by 3:30 unless I have called {C('A2',0).split()[0]} by noon to say otherwise.

## Approvals

- The drivers drop the vans and leave. A driver may approve up to $300 like any account's driver, but they would rather not: call {C('A2',0).split()[0]}.
- {C('A2',0)} approves up to $1,000 a vehicle: {C('A2',0,'phone')}.
- Over $1,000, {C('A2',1)} himself: {C('A2',1,'phone')}. He answers.

## Billing

Company rate. {C('A2',2)} pays the statement and wants it on paper, mailed, with the invoices behind it. {S(3)} knows.

## Things I know about these vans

- Units are M-101 to M-125 and the number is on the rear door.
- The Express vans eat front brakes. Measure the pads at every visit and tell {C('A2',0).split()[0]} a visit ahead, so it is never a surprise.
- The ladder racks sit lower than our door at bay 2. Bay 1 or bay 4.

{S(16)}
""",
 serves=['S1', 'S5', 'challenge:combine-policy-and-price'],
 facts=['Account A2: 25 vehicles, home shop east; contacts from accounts.json (Tina Ragsdale dispatcher, Hal Millsaps president, Joyce Millsaps office manager).',
        'Standing slot Monday 7:30, five vans (ledger acct.A2.weekly_slot); unit numbers sent by Friday noon; priority on Monday mornings; a holiday Monday moves the slot to Tuesday.',
        'Vans back by 15:30 unless the dispatcher was called by noon.',
        'Drivers up to 300 USD like every account; the dispatcher up to 1,000 USD a vehicle; the president above.',
        'Company rate; paper statement mailed with invoices attached.',
        'Units M-101 to M-125.',
        'Voice: slot 16, first person, warm and exact, signed.'],
 new=['A holiday Monday moves the slot to Tuesday; back by 15:30; bay 1 or bay 4 because of the ladder racks (colour, no data footprint).',
      'Paper statements for A2.'],
 rev=[(4, 'T-4mo', 'Monday priority moved here from a team note, in Angie\'s words (she is middle rank: her proposal, approved by slot 4); message: "Monday slot written down."', {'kind': 'proposal', 'proposer_slot': '16', 'approver_slot': '4'})],
 ru=['«Сервисная компания (отопление и сантехника)» from accounts.json ru; contract hour; documents per order. Lead advisors in the Russian configuration work 2/2 (R12), so say who holds the Monday slot when slot 16 is off.'])

page('accounts/a3.md', 'Moccasin Bend Janitorial Services', 'J', 5,
 'Standing instructions for account A3.',
 f"""*Last reviewed {D('T-7mo')}*

Nine vehicles, served at East Main. Pays in 15 days, list prices.

- **Contact:** {C('A3',0)}, operations manager, {C('A3',0,'phone')}. She books and approves. {C('A3',1)} owns the company and stays out of it.
- Their crews work nights. Vans arrive between 7:30 and 8:00 after the shift and have to be ready by 4:00 to go back out.
- A driver may approve up to $300 for the visit. Over that, {C('A3',0).split()[0]}.
- Units are MB-1 to MB-9. MB-8 is the old Express van that carries the floor machines: it is heavy, check the rear springs and tires every visit.
- They ask for the economy line on brakes and filters. Quote standard anyway and let {C('A3',0).split()[0]} choose.
""",
 serves=['S1', 'smoke'],
 facts=['Account A3: nine vehicles MB-1 to MB-9, home shop main, net 15, list prices; contacts from accounts.json (Yolanda Fitch operations manager, Dennis Fitch owner).',
        'Vans arrive 7:30-8:00 and must be ready by 16:00.',
        'Driver limit 300 USD (the one company rule).',
        'MB-8 is the 2015 Express van (accounts.json): heavy use.',
        'They prefer economy parts; quote standard first.'],
 new=['Night crews, ready by 16:00, the economy preference (colour).'],
 ru=['«Клининговая компания» from accounts.json ru, 14 days.'])

page('accounts/a4.md', 'Missionary Ridge Driving School', 'J', 16,
 'Standing instructions for account A4; says seven cars, which is out of date by one.',
 f"""*{S(16)}, Bonny Oaks · Last reviewed {D('T-6mo')}*

Seven training cars, Corollas, Elantras, a Sentra and a Civic, and they are growing. Pays in 15 days, list prices.

- **Contact:** {C('A4',1)}, lead instructor, looks after the cars: {C('A4',1,'phone')}. He approves up to $500. Above that it is {C('A4',0)}, the owner: {C('A4',0,'phone')}.
- The instructors who drop the cars may approve up to $300, the same as any company driver. They usually ring {C('A4',1).split()[0]} anyway.
- Learners are hard on brakes, clutches (none of theirs are manual, thank goodness), tires and curbs. Brakes are measured at every oil service and alignment is checked whenever a tire shows edge wear.
- **The instructor's brake pedal** on the passenger side is fitted by an outside company. We check that it moves freely and returns, and we write it on the inspection. We do not adjust or repair it. If it is not right, the car does not go back out: call {C('A4',1).split()[0]}.
- A car can never be off the road on a Saturday: that is their busiest day. Book their work Monday to Thursday.

{S(16)}
""",
 serves=['S1', 'challenge:combine-kb-and-data', 'challenge:kb-does-not-say'],
 facts=['Account A4: home shop east, net 15, list prices; contacts from accounts.json (Rob Atchley lead instructor, Denise Atchley owner).',
        'STALE BY ONE ON PURPOSE: the page says seven cars (true at its review date T-6 months: six cars plus the one that joined at T-8 months); the ERP has eight since T-3 months (accounts.json: Car 8 joined 3 months before T).',
        'Rob Atchley approves up to 500 USD; the owner above; instructors up to 300 USD like every company driver.',
        'The dual-control brake pedal is fitted by an outside company; the shop checks free movement and return and records it; it does not adjust or repair it; who the outside company is, is not stated (planted gap).',
        'Work is booked Monday to Thursday; Saturday is the school\'s busiest day.'],
 new=['The dual-control pedal rule; Monday-to-Thursday booking. Reason: what makes a driving school a different customer.'],
 ru=['«Автошкола»: dual controls are legally required on Russian training cars and include a second clutch pedal on manuals; most Russian training cars are manual (Granta, Logan, Solaris), so the clutch remark is reversed: clutches wear fast. Fleet count: one fewer than the ERP, same staleness.'])

page('accounts/a5.md', 'Cumberland Bend Electric', 'J', 22,
 'Account A5 as Charlotte Pike wrote it before the account left: thin, and silent on everything that went wrong.',
 f"""*{S(22)} · {D('T-13mo')}*

Electrical contractor. 11 vans and trucks. Been coming here since before the sale.

{C('A5',0)} runs operations, {C('A5',0,'phone')}. {C('A5',1)} does the books.

Net 30.

They like Fridays.
""",
 serves=['S1', 'challenge:kb-does-not-say', 'challenge:near-duplicate-shop-pages'],
 facts=['Account A5: 11 vehicles, home shop west, net 30; contacts from accounts.json (Wade Carlisle operations manager, Sherry Lane bookkeeper).',
        'Written by slot 22 at T-13 months, a month after the purchase, and not touched since.',
        'The page says nothing about the two brake comebacks, the disputed bill, the three unreturned calls or that the account has not visited for four and a half months: the knowledge base does not know the account left.',
        'The driver limit (300 USD) is on the Company accounts page only.',
        'Voice: slot 22, five lines, no verbs to spare.'],
 stale='S1: silent about the account leaving',
 ru=['«Электромонтажная компания» «Идель-Электромонтаж» from accounts.json ru; same five lines in slot 22\'s Russian voice.'])

page('accounts/a6.md', 'Sourwood Catering Co.', 'J', 5,
 'Account A6 as it stood eight months ago: names a fleet contact and an advisor who have both gone.',
 f"""*Last reviewed {D('T-8mo')}*

Ten vehicles: cargo vans, two box trucks with refrigeration, and the owner's Sienna. Served at East Main. Pays in 30 days, list prices.

- **Contact:** {C('A6',0)}, kitchen and fleet manager, {C('A6',0,'phone')}. He texts the main line when a van needs to come in and he answers an estimate within the hour.
- **At our end, {PEOPLE['F3']['en']['full_name'].split()[0]} looks after Sourwood.** {C('A6',0).split()[0]} asks for him by name. If {PEOPLE['F3']['en']['full_name'].split()[0]} is off, {S(5)}.
- {C('A6',2)} owns the company and pays the statement herself. Bills go to her, not to the kitchen.
- Everything has to be back **before noon on Friday**. Their work is weekend events. A van still on a lift on Friday afternoon is a cancelled wedding.
- The refrigeration units on SC-8 and SC-9 are not ours to touch. We service the trucks, not the boxes.
- A driver may approve up to $300 for the visit.

Units are SC-1 to SC-10.
""",
 serves=['S1', 'operate:contradiction', 'challenge:combine-kb-and-data'],
 facts=['Account A6: ten vehicles SC-1 to SC-10, home shop main, net 30, list prices; SC-8 and SC-9 are the two Express 3500 cutaways (accounts.json), described as refrigerated box trucks; SC-10 the owner\'s Sienna.',
        'STALE ON PURPOSE: names Bobby Shadden as the fleet contact (he held the role until T-5 months; Erin Castillo since) and Brad (slot F3, resigned T-7 months) as the advisor who looks after the account. Reviewed T-8 months, before both changes.',
        'It contradicts accounts/company-account-terms.md, which names Erin Castillo.',
        'Marianne Tolliver, owner, pays the statement.',
        'Everything back before Friday noon; refrigeration units not serviced; driver limit 300 USD.',
        'Evidence for "what should we do about A6": the account lost the advisor it dealt with and its own contact changed, and nobody rewrote this page.'],
 new=['Slot F3 was A6\'s named advisor. Reason: the cast says several accounts "dealt only with him"; tying A6 to him gives the fading account a cause the agent can find in the knowledge base. Story S1 gains a fourth cause beside the new contact, the waiting estimates and the price rise.',
      'Friday-noon deadline; refrigeration units not serviced.'],
 stale='S1: fleet contact and advisor both gone',
 ru=['«Вкусный выезд», кейтеринг; old and new contact and slot F3\'s Russian name (Вадим Савельев) from the Russian files.'])

page('accounts/small-business-customers.md', 'Small business customers', 'J', 4,
 'Businesses with a few vehicles and no account: how they differ from an account.',
 f"""*{S(4)}*

About thirty local businesses bring us one to three vehicles each: landscapers, a pest-control firm, plumbers, a florist. They are **not** company accounts.

- They pay at pick-up like anyone else. List prices. No statement, no terms.
- The vehicle goes under the business's name, not the driver's, so the history stays with the truck when the driver changes.
- Whoever is standing at the counter approves the work, unless the owner has told us otherwise; then it is in the customer notes.
- Deposits and storage apply as for private customers.
- The warranty is the business-use one: 12 months or 12,000 miles.
- A work truck that is their only truck: we try to turn it the same day. We do not promise it.

A business that reaches five vehicles can apply for an account: [Opening a company account](opening-a-company-account.md).
""",
 serves=['S1', 'challenge:near-duplicate', 'challenge:combine-policy-and-price'],
 facts=['About thirty small business customers with one to three vehicles (accounts.json: 30).',
        'They pay at pick-up at list prices; no statement; vehicle under the business name.',
        'The person at the counter approves unless the customer notes say otherwise.',
        'Deposits and storage as for private customers; warranty 12/12 (business use).',
        'Same-day turnaround is attempted, not promised.',
        '"Lost or losing" questions are asked of accounts billed on terms only (design 7.2): this page draws that line.'],
 ru=['Russian small businesses often pay by bank transfer on an invoice (безнал) even without a contract; say so.'])

page('accounts/opening-a-company-account.md', 'Opening a company account', 'J', 2,
 'Who qualifies for an account and the steps to open one.',
 f"""*{S(2,'full')} · Last reviewed {D('T-10mo')}*

1. **Five vehicles or more**, and at least six months as a customer paying at the counter.
2. The business fills in the credit application ({S(3)} has the form) and names one person who approves work and one who pays bills. They may be the same person.
3. I approve it and set the credit limit. Nobody else opens an account.
4. Terms: **15 days** for a fleet of fewer than ten vehicles, **30 days** from ten up.
5. {S(4)} writes the account's page in this folder and adds the row to the [terms table](company-account-terms.md): approver, anything the shop needs to know. No page, no account.
6. {S(3)} sets the customer up in the shop system with its terms. From that day its vehicles are not charged at the counter.

The company rate is not part of opening an account. Two customers have it, by agreement with me, and that is not a thing to offer.
""",
 serves=['S1', 'challenge:three-page-procedure'],
 facts=['Threshold: five vehicles and six months as a paying customer.',
        'Credit application names an approver and a payer.',
        'Slot 2 approves and sets the credit limit.',
        'Terms: 15 days under ten vehicles, 30 days from ten (matches A3 with 9 and A4 with 8 at 15 days; A5 with 11, A6 with 10, A1 and A2 at 30).',
        'Slot 4 writes the account page and the terms-table row; slot 3 sets terms in the shop system (ERP customer: payment terms and credit limit).',
        'The company rate is by agreement with slot 2 only.'],
 new=['The fleet-size rule for terms (15 days under ten vehicles, 30 from ten). Reason: explains the two payment terms in accounts.json with one rule.',
      'Six months as a counter customer before an account.'],
 ru=['Russian: договор на обслуживание with отсрочка платежа 14 or 30 days; the company gives its реквизиты (ИНН, КПП) instead of a credit application.'])

page('accounts/credit/credit-limits-and-collections.md', 'Credit limits and collections', 'M', 3,
 'Middle rank and up: each account\'s credit limit and the steps taken when a statement is overdue.',
 f"""*{S(3,'full')}, office · Last reviewed {D('T-3mo')}*

This page is for the office and the managers. Please do not read limits out to a customer or a driver.

## Credit limits

| Account | Limit |
|---|---:|
| {A('A1')} | $30,000 |
| {A('A2')} | $20,000 |
| {A('A3')} | $5,000 |
| {A('A4')} | $5,000 |
| {A('A5')} | $7,500 |
| {A('A6')} | $7,500 |

The limit is the most an account may owe us at one time, statements and unbilled work together. {S(2)} sets it at about two months of the account's usual billing. If an order would take an account over its limit, the advisor calls me before the work starts.

## When a statement is overdue

| Days past the due date | What I do |
|---|---|
| 1 | Send the statement again by e-mail with a polite line |
| 10 | Telephone the person who pays the bills |
| 20 | Telephone again, and send a letter. Tell {S(2)} |
| 45 | No new work is started for the account without {S(2)}'s approval |

A dispute about one invoice does not stop the clock on the others. A disputed invoice is passed to {S(4)} the day it is raised, with the order number.

No account has been stopped at 45 days. {A('A1')} would not be stopped without {S(2)} and {S(1)} both saying so.
""",
 serves=['S1', 'S16', 'visibility:middle', 'challenge:fact-in-table', 'challenge:combine-kb-and-data'],
 facts=['Credit limits: A1 30,000; A2 20,000; A3 5,000; A4 5,000; A5 7,500; A6 7,500 USD (ERP customer.credit_limit).',
        'Limit = most owed at once, about two months of usual billing; over-limit orders need a call to slot 3 first.',
        'Collections: day 1 e-mail; day 10 call; day 20 second call, letter and slot 2 told; day 45 no new work without slot 2.',
        'Disputed invoices go to slot 4 the day they are raised.',
        'No account has ever been stopped.',
        'A1 now pays in about 50 days on 30-day terms, so about 20 days past due: by this page slot 3 should be at the "day 20" step (S16: her part of the review is not done).',
        'A5\'s disputed bill (T-4.5 months) should have gone to slot 4 that day.',
        'Hidden below middle: a junior or worker asking for a credit limit gets "not found".'],
 new=['The six credit limits and the four collection steps. Reason: the ERP customer table has a credit limit and the design sets none; a middle-rank page makes a rank test.',
      'Folder accounts/credit is seen from middle.'],
 ru=['Limits in RUB as new facts (about two months of billing per account). Collections in Russia: акт сверки, претензионное письмо before court; days the same.'])
