from kbb import *
import kbb

def row(slot, job, ext=''):
    return f"| {S(slot,'full')} | {job} | {ext} |"

page('team/who-is-who.md', 'Who is who', 'J', 2,
 'The company directory: everyone who works here now, by shop, with role and extension. The page that is right when a shop page is not.',
 f"""*{S(2,'full')} · Last reviewed {D('T-1mo')}*

Twenty-nine of us.

## Owners and office

| Who | Job | Ext. |
|---|---|---|
{row(1,'Founder, owner','401')}
{row(2,'Managing owner','402')}
{row(3,'Office manager, bookkeeper (East Main)','111')}
{row(4,'Service manager, East Main and Bonny Oaks','104')}

## East Main, (423) 555-0142

| Who | Job | Ext. |
|---|---|---|
{row(5,'Lead service advisor','101')}
{row(6,'Service advisor','102')}
{row(7,'Service advisor','103')}
{row(29,'Service advisor, part-time: Saturdays and cover days','105')}
{row(8,'Shop foreman')}
{row(9,'Parts manager, both Chattanooga shops','112')}
{row(10,'Diagnostic technician')}
{row(11,'Technician')}
{row(12,'Technician')}
{row(13,'Electrical technician')}
{row(14,'Apprentice technician')}
{row(15,'Lube and tire technician')}

## Bonny Oaks, (423) 555-0167

| Who | Job | Ext. |
|---|---|---|
{row(16,'Lead service advisor','201')}
{row(17,'Service advisor','202')}
{row(18,'Lead technician')}
{row(19,'Technician')}
{row(20,'Technician')}
{row(21,'Technician, also at East Main')}

## Charlotte Pike, (615) 555-0119

| Who | Job | Ext. |
|---|---|---|
{row(22,'Shop manager','301')}
{row(23,'Service advisor','302')}
{row(24,'Service advisor','303')}
{row(25,'Technician')}
{row(26,'Technician')}
{row(27,'Technician')}
{row(28,'Technician, part-time')}

E-mail is first initial and last name at brennanautocare.example. Shop mailboxes: main@, east@, west@, accounting@.

In summer East Main has a seasonal helper for ten weeks from the first Monday of June.
""",
 serves=['S2', 'S14', 'challenge:fact-in-table', 'operate:contradiction', 'challenge:combine-kb-and-data'],
 facts=['29 active people by shop with role and extension, exactly as cast.json (slots 1 to 29).',
        'Charlotte Pike\'s counter is slots 23 and 24; slot F1 is not listed (fired at T-5 months). This contradicts shops/west/README.md, which is out of date.',
        'E-mail pattern and shop mailboxes from phones.md.',
        'Seasonal helper (slot F4) at East Main for ten weeks from the first Monday of June (cast).',
        'Former staff F1 to F4 are not on the page; the history shows them being removed.'],
 rev=[(2, '@f1_fired', 'Brent Lassiter removed; message: "Left the company."'),
      (2, '@f2_fired', 'Wes Tate removed; message: "Left the company."'),
      (2, '@newcomers', 'Caleb Sutton and Hunter Varnell added at East Main; message: "New people."'),
      (2, 'T-1mo', 'extensions checked against the phone system; message: "Extensions checked."')],
 ru=['Russian names by slot from cast.json; the Russian flagship has a fourth advisor (slot 29) once it is named. Seasonal: a tyre fitter for six weeks each tyre season.'])

page('team/meetings.md', 'Meetings', 'J', 2,
 'The standing meetings: the Monday managers\' meeting, the morning huddle.',
 f"""*{S(2,'full')} · Last reviewed {D('T-5mo')}*

We keep meetings few and short.

## Monday managers' meeting

- **Every Monday at 6:45, before the doors open, on video, 30 minutes.** I run it.
- Who: {S(4)}, {S(5)}, {S(16)}, {S(3)}, {S(22)} and me.
- What: last week by shop (cars, recommended work sold, missed calls, comebacks), this week's cover, anything about a company account.
- If Monday is a holiday there is no meeting that week.
- Accept or decline the invitation. If you decline, send your numbers before Monday.

## Morning huddle

Each shop, 7:20, five minutes, standing. The foreman or the shop manager says what is booked, who has what, what is waiting on parts. Technicians are paid for it.

## Reviews

- Comebacks: {S(4)} and {S(8)}, monthly.
- {A('A1')}: quarterly, with them.

There is no all-staff meeting. If I need to tell everyone something I come and tell you.
""",
 serves=['S9', 'S16', 'challenge:combine-kb-and-data'],
 facts=['Monday managers\' meeting: every Monday 6:45, before the shops open, video, 30 minutes, called by slot 2; invitees slots 4, 5, 16, 3, 22 (ledger s9.meeting). It ends at 7:15, before the 7:20 huddle, so no lead advisor is off a counter in the Monday rush.',
        'The page gives the time without a time zone. With shops/README.md (Charlotte Pike is an hour behind and opens at 7:30 its time) the meeting is at 5:45 for slot 22, an hour and three quarters before his shop opens: the S9 answer needs both pages.',
        'No meeting on a holiday Monday (design 7.2 S9: holiday Mondays are cancellations).',
        'Morning huddle 7:20 at each shop, five minutes, paid.',
        'Comeback review monthly (slots 4 and 8); A1 review quarterly.'],
 new=['Morning huddle at 7:20; meeting length 30 minutes. The calendar series for the Monday meeting should be 30 minutes.'],
 created=(2, '@golive+1w'),
 ru=['Russian meeting time set against the Russian opening hours (ledger s9.meeting): 8:15 in Ulyanovsk is 7:15 in Kazan, an hour and three quarters before opening. Планёрка each morning.'])

page('team/new-advisor-first-two-weeks.md', 'New advisor: the first two weeks', 'J', 5,
 'Onboarding checklist for a new service advisor, written when the newcomer started.',
 f"""*{S(5,'full')} · {D('@newcomers')}*

For whoever is new at the counter, and whoever is training them.

## Week one: watch and read

- You sit beside a lead advisor. You do not quote a price or promise a time on your own this week. Nobody will mind you saying "let me check that".
- Read, in this order: the [price list](../prices/price-list.md), [Taking a call](../how-to/taking-a-call.md), [Booking a visit](../how-to/booking-a-visit.md), [Checking a car in](../how-to/checking-a-car-in.md), [Discount policy](../policies/discounts.md), [Warranty](../policies/warranty.md).
- Listen to five of {S(16)}'s calls. Write down what she does after she says the price.
- Half a day in the shop with {S(8)}: an oil service, a brake inspection, a tire off the rim. You will explain these fifty times a day.
- Half a day with {S(9)} in the parts cage.
- Check in ten cars with someone watching.

## Week two: do it, with a net

- You take calls. Your lead listens to three a day and tells you one thing to fix.
- You write estimates. Your lead reads every one before it goes.
- You close the till once, with {S(3)} beside you.
- You answer chats. Read the draft before you send it.

## Before you are on your own

- [ ] You can find any price in under a minute, and you know the service pages are not where prices live.
- [ ] You know what you may promise about time, and what you may not.
- [ ] You know the 10 % rule and who approves above it.
- [ ] You have never used the Walk-in customer.
- [ ] You know which shop you are in when you answer the phone.

It takes about three months to be good at this. Everybody's first month has a wrong price in it. Tell your lead the same hour, and it is a small thing.
""",
 serves=['S8', 'S4', 'challenge:three-page-procedure'],
 facts=['Week one: shadow a lead; no solo quotes or promises; six pages to read in order; five of slot 16\'s calls; half days with slot 8 and slot 9; ten supervised check-ins.',
        'Week two: calls with three reviewed a day; every estimate read by the lead; one till close with slot 3; chats.',
        'Sign-off list of five points (prices, promises, the 10 % rule, the Walk-in record, which shop).',
        'Written the week slot 7 started (the Monday of week T-14); it says the service pages are not where prices live, about eleven weeks before he quoted from one (S8 at T-12 days): he had been told.'],
 created=(4, '@newcomers', 'proposal', {'proposer_slot': '5', 'approver_slot': '4', 'author_slot': '5'}),
 ru=['Same plan; Russian new advisor is slot 7.'])

page('team/new-technician-first-week.md', 'New technician: the first week', 'J', 8,
 'What a new technician is shown in the first week.',
 f"""*{S(8)}*

Day one:
- Your bay, your lift, the lift points poster. Where the torque wrenches live. They go back there.
- The app: clock in at the shop, clock out when you leave. Your schedule is in it.
- The shop system: your jobs, the job clock, the inspection.
- Safety walk with me. Eye wash, extinguishers, spill kit.

This week:
- You work beside {S(12)} at East Main, {S(18)} at Bonny Oaks, {S(25)} at Charlotte Pike.
- Three inspections with photos that an advisor says he can sell from.
- A brake job start to finish with me watching the last ten minutes.
- You read [Before a car leaves your bay](../shop-floor/before-a-car-leaves.md). Then you do it every time.

What I do not want to hear: "the gun was set right", "I thought he checked it", "it was like that".

What I want to hear: "I am not sure about this one, come and look."
""",
 serves=['S14', 'smoke'],
 facts=['Day one: bay, lift points, torque wrenches, the app (punches, schedule), the shop system (jobs, job clock, inspection), safety walk.',
        'First week: paired with slot 12 (main), 18 (east) or 25 (west); three sellable inspections; one supervised brake job; the final-check page.',
        'Voice: slot 8, terse.'],
 ru=['Same; the mentor slots are the same.'])

# ----------------------------------------------------------------- office (middle)
page('office/month-end-close.md', 'Month-end close', 'M', 3,
 'The bookkeeper\'s month-end checklist; the check that caught the missing money.',
 f"""*{S(3,'full')} · Last reviewed {D('T-5mo')}*

I close the month in the first three working days of the next one. The steps are in this order for a reason.

1. **Open orders.** Every order still open from before the last week of the month is either finished and invoiced, or has a reason. I ask each shop manager for the reasons. An order open more than 60 days is reported to {S(2)}.
2. **Till counts.** For each shop: every day has a count, and the differences for the month are added up by shop and by the person who closed. A few dollars either way is ordinary. I look for the same name short again and again.
3. **Voids.** The list of every voided order, with who voided it and whether a payment had been taken. Since {D('@discount_rule')}, a paid order voided by anyone but a shop manager is reported the same day.
4. **Discounts.** Every bill with more than 10 % off has an approver. {S(2)} receives the same list each Friday.
5. **Cash orders on the Walk-in customer.** There should be none.
6. **Supplier statements** against what we received: credits for returns and cores are there, or I ask {S(9)}.
7. **Company-account statements** go out on the first working day: [Statements and receivables](statements-and-receivables.md).
8. **Payroll hours** for the last period: [Payroll hours](payroll-hours.md).
9. **Sales tax** return, filed and paid by the 20th.

Steps 2 to 5 were added to this list, or made stricter, in {D('@discount_rule','month')}. Before that I looked at the till totals by shop only. Looking at them by person is what showed the problem at Charlotte Pike.
""",
 serves=['S2', 'S15', 'visibility:middle', 'operate:find-what-changed'],
 facts=['Close in the first three working days of the next month; nine ordered steps.',
        'Open orders need a reason; over 60 days are reported to slot 2 (ERP mess kind 4: one order at west open five months, two more over sixty days).',
        'Till differences are summed by shop and by closer (how the 19 short days of slot F1 showed).',
        'Void list with voider and payment; discounts over 10 % have an approver; no cash orders on the Walk-in customer; supplier credits; statements on the first working day; payroll hours; sales tax by the 20th.',
        'Steps 2 to 5 were added or tightened in the month of {{@discount_rule}}.',
        'Seen from middle rank.'],
 new=['Orders open more than 60 days are reported to slot 2 (matches the "over sixty days" of S15 kind 4).',
      'Sales tax return by the 20th of the following month (Tennessee\'s due date as generally known; to be re-read on the state\'s page with the tax rows of the ledger).'],
 rev=[(2, '@discount_rule', 'Donna\'s steps 2 to 5 (proposed by slot 3, approved by slot 2); message: "Till by person, voids, discounts, walk-in."', {'kind': 'proposal', 'proposer_slot': '3', 'approver_slot': '2'})],
 ru=['Russian month end: закрытие месяца в 1С, акты сверки with suppliers, НДС 5 % (УСН) and the cash book; no sales tax.'])

page('office/statements-and-receivables.md', 'Statements and receivables', 'M', 3,
 'How company-account statements are issued and payments applied.',
 f"""*{S(3,'full')} · Last reviewed {D('T-3mo')}*

## Issuing

- First working day of the month, one statement per account, for every invoice of the month before.
- Before {A('A1')}'s statement goes: every invoice has their purchase-order number. One without it is held back and I ask the advisor who wrote it. Their accounts payable returns the whole statement otherwise.
- {A('A2')} receives theirs on paper, by post, with the invoices attached. Everyone else by e-mail to the address on the account.

## Applying payments

- A payment is applied to the **statement**, not to single orders. One check commonly pays twenty invoices.
- A short payment: apply it, note which invoices were left out, and ask why the same day. It is usually a missing purchase-order number or a disputed line.
- A disputed invoice goes to {S(4)} with the order number the day it is raised. The rest of the statement stays due.

## Each Monday

I read the list of what is owed, oldest first, and work it by [the steps](../accounts/credit/credit-limits-and-collections.md): day 1, 10, 20 and 45.

I keep a note for each account of the date each statement was paid. If you need to know how quickly an account pays, the shop system has the dates; ask it, or ask me.
""",
 serves=['S1', 'S16', 'S15', 'visibility:middle'],
 facts=['One statement per account on the first working day for the previous month (ERP statement).',
        'A1\'s invoices need the purchase-order number before the statement goes; A2 gets paper by post; others by e-mail.',
        'Payments are applied to the statement, not to single orders (design 2.4; ERP mess kind 6).',
        'Short payments are applied, noted and queried the same day; disputed invoices go to slot 4.',
        'Receivables are reviewed every Monday against the four collection steps.',
        'Days-to-pay is in the data (statement issued and paid dates), not on the page.'],
 ru=['Russian: акты and счета per order; акт сверки quarterly; payments by платёжное поручение naming the invoice numbers.'])

page('office/payroll-hours.md', 'Payroll hours', 'M', 3,
 'How attendance becomes payroll hours.',
 f"""*{S(3,'full')} · Last reviewed {D('T-5mo')}*

Pay periods are two weeks, Sunday to Saturday. Pay day is the Friday after.

- Hours come from the punches in Traciora. I take them on the Monday after the period ends.
- **A punch that is missing or was corrected must be approved by the person who plans that shop's schedule before Monday noon**: {S(4)} for East Main and Bonny Oaks, {S(22)} for Charlotte Pike. An unapproved correction is paid as the schedule says and put right the following period.
- Late arrivals do not reduce pay by the minute. They are counted, and the count goes to the planner.
- Flat-rate technicians are paid on the hours sold on their jobs, which I take from the shop system, not from the punches. Their punches are still attendance.
- Hourly staff past 40 hours in a week are paid overtime. Overtime needs the planner's yes beforehand.

Rates of pay are not on this page or any other.

Questions about your own pay: come and see me, or ext. 111.
""",
 serves=['S14', 'visibility:middle', 'challenge:kb-does-not-say'],
 facts=['Two-week pay periods, Sunday to Saturday; pay day the following Friday.',
        'Hours from Traciora punches, taken the Monday after; corrections must be approved by the planner (slot 4 or 22) before Monday noon.',
        'Lateness is counted, not docked.',
        'Flat-rate technicians are paid on sold hours from the shop system (ERP order_labor), not on punches.',
        'Overtime past 40 hours a week with prior approval.',
        'Pay rates are stated nowhere (planted gap; staff pay is hidden below senior in the ERP).'],
 new=['Two-week Sunday-to-Saturday pay period, pay on the following Friday.'],
 ru=['Russian pay twice a month by law (аванс and зарплата); сдельная оплата for mechanics from нормо-часы; табель учёта рабочего времени.'])

page('office/till-and-deposits.md', 'Till differences and deposits', 'M', 3,
 'The office side of the cash: the bag log, the bank, the differences book.',
 f"""*{S(3,'full')} · In force from {D('@discount_rule')}*

- Each shop's deposit bag has a line in the bag log: date, amount on the bag, who sealed it, who carried it, who received it.
- East Main's bag is in the office safe overnight and I bank it the next morning with Bonny Oaks', which arrives on the 1:00 parts run. Charlotte Pike banks its own every working day and {S(22)} sends me a photo of the slip.
- I match each bank slip to the shop system's cash for that day. A bag that does not match its own count sheet is opened with a second person present.
- Differences go in the differences book by date, shop and the person who closed.

What I look for at month end:

1. The same closer short on many days.
2. Cash orders with a discount, more at one counter than the others.
3. Orders voided after a payment.
4. Many small cash orders under a customer with no name.

In the {D('@money_found','season')} I found all four at one counter.
""",
 serves=['S2', 'visibility:middle', 'challenge:near-duplicate-shop-pages'],
 facts=['Bag log columns: date, amount, sealer, carrier, receiver.',
        'East Main\'s bag is banked next morning with Bonny Oaks\'s (arriving on the 13:00 run); Charlotte Pike banks daily and sends a photo of the slip.',
        'Bank slips are matched to the day\'s cash; mismatched bags are opened with a second person.',
        'Differences book by date, shop and closer.',
        'Four signals: repeated shorts by one closer; discounted cash orders concentrated at one counter; voids after payment; many small cash orders on a nameless customer.',
        'The season is that of the day the money was found (the 5th full open day after go-live).'],
 new=['Placeholder format "season" (spring, summer, fall, winter of a date) is needed for this sentence.'],
 created=(2, '@discount_rule', 'proposal', {'proposer_slot': '3', 'approver_slot': '2', 'author_slot': '3'}),
 ru=['Russian: инкассация and the cash book (кассовая книга).'])
