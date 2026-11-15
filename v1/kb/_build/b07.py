from kbb import *

page('shops/README.md', 'Our three shops', 'J', 2,
 'The three shops side by side: bays, people, hours, time zone, who runs each.',
 f"""*{S(2,'full')} · Last reviewed {D('T-2mo')}*

| | East Main | Bonny Oaks | Charlotte Pike |
|---|---|---|---|
| City | Chattanooga | Chattanooga | Nashville |
| Ours since | {S(1)} opened it 30 years ago | Opened 11 years ago | Bought {D('@purchase','month')} |
| Bays | 8 | 6 | 6 |
| Technicians | 6 | 4 | 4 |
| Advisors | 3 | 2 | 2 |
| Run by | {S(4,'full')}, service manager | {S(4,'full')}; {S(16,'full')} leads the counter | {S(22,'full')}, shop manager |
| Hours | Mon to Fri 7:30 to 5:30, Sat 8:00 to 1:00 | Mon to Fri 7:30 to 5:30 | Mon to Fri 7:30 to 5:30 |
| Clock | Eastern | Eastern | **Central** |
| Main line | (423) 555-0142 | (423) 555-0167 | (615) 555-0119 |
| Pages | [East Main](main/README.md) | [Bonny Oaks](east/README.md) | [Charlotte Pike](west/README.md) |

## Things that follow from the table

- **Charlotte Pike is an hour behind.** When it is 8:00 in Chattanooga it is 7:00 there. Their 7:30 opening is our 8:30. Every time in their pages and their orders is their own clock; the phone system shows each call in your own time.
- East Main and Bonny Oaks are one crew in two buildings, fifteen minutes apart. {S(4)} plans both schedules together, {S(21)} works at both, and an advisor may be sent across for a day. {S(9)} buys parts for both and the office at East Main does the books for all three.
- Charlotte Pike is two hours' drive away. It has its own schedule, its own parts ordering and its own way of doing some things, written on its own pages. Where its page and a company policy disagree, the policy is right and the page is old.
- Only East Main opens on Saturday, works on hybrids and stocks the newer A/C refrigerant.

The Charlotte Pike column was added on {D('@purchase+1mo')}, a month after we bought the shop.
""",
 serves=['S9', 'S13', 'S15', 'challenge:fact-in-table', 'challenge:near-duplicate-shop-pages', 'operate:contradiction'],
 facts=['Bays 8 / 6 / 6; technicians 6 / 4 / 4; advisors 3 / 2 / 2 (ledger).',
        'East Main opened 30 years ago by slot 1; Bonny Oaks opened 11 years ago (cast: slot 16 opened its counter eleven years ago); Charlotte Pike bought at {{@purchase}} (T-14 months).',
        'Run by: slot 4 for main and east, slot 16 leads the east counter, slot 22 for west.',
        'Hours and main lines as on the public page; Charlotte Pike is on Central time, one hour behind; the times in its pages and orders are its own clock, and the phone system shows each call in the reader\'s own time (design 2.4; S15.4: calls are stored as instants, orders in local time).',
        'Main and east share staff (slot 21 floats; advisors are lent), parts (slot 9) and the office; fifteen minutes apart.',
        'Charlotte Pike is two hours\' drive (about 135 miles), with its own roster and parts ordering.',
        'Rule for conflicts: company policy beats a Charlotte Pike page.',
        'Saturday, hybrids and R-1234yf are East Main only.',
        'The Monday meeting at 6:45 Eastern is 5:45 at Charlotte Pike, an hour and three quarters before it opens: the page gives the fact, not the conclusion (S9).',
        'The Charlotte Pike column was added a month after the purchase (@purchase+1mo): a change from before go-live, so it is a sentence of the page and not a revision (ledger kb.history.before_go_live).'],
 new=['East Main and Bonny Oaks are fifteen minutes apart. Reason: staff sharing needs a plausible distance; the ledger puts the two addresses about 11 km apart by road (geo.address.east).'],
 ru=['Ульяновск: two shops (Московское шоссе; Инженерный, across the Volga, so more like 30-40 minutes apart: say what is true for the Russian addresses). Казань is an hour behind (UTC+3 against UTC+4), about 225 km by the Р-241. Hours 9:00-20:00 every day.'])

# ---------------------------------------------------------------- East Main
page('shops/main/README.md', 'East Main', 'J', 5,
 'Front page of the flagship\'s own pages.',
 f"""2106 East Main St, Chattanooga. The first shop, the biggest, and where the office and the parts cage are.

- [Hours and getting here](hours-and-getting-here.md)
- [Who is who](who-is-who.md)
- [Opening and closing](opening-and-closing.md)
- [How the day runs](how-the-day-runs.md)
- [Saturdays](saturdays.md)

What is only here: {S(10)} and the hard diagnostics, hybrid work, the newer A/C refrigerant, the alignment rack with the long runways for crew-cab trucks, {S(3)}'s office, {S(9)}'s parts cage. If Bonny Oaks needs any of those, the car comes here.

{S(5)}
""",
 serves=['challenge:near-duplicate-shop-pages', 'operate:overview'],
 facts=['Address 2106 East Main St, Chattanooga.',
        'Only at East Main: slot 10 and hard diagnostics, hybrid work, R-1234yf, the long alignment rack, the office (slot 3), the parts cage (slot 9).'],
 new=['A long-runway alignment rack at East Main (colour; the founder started with "a borrowed alignment rack").'],
 ru=['Московское шоссе, 40.'])

page('shops/main/hours-and-getting-here.md', 'East Main: hours and getting here', 'J', 5,
 'East Main\'s hours, parking, shuttle and key drop for staff to tell customers.',
 f"""**Monday to Friday 7:30 to 5:30. Saturday 8:00 to 1:00.** Closed Sunday. Holidays and the stocktake afternoon: [Hours and locations](../../customers/hours-and-locations.md), which is the page that is kept right.

- Phone: (423) 555-0142. E-mail: main@brennanautocare.example.
- Customer parking is the six spaces in front. Fleet vans go round the back by bay 8; tell drivers, or they block the front.
- The key drop box is to the right of the office door.
- The shuttle leaves from the front door at 7:45 and 8:45. Whoever is on the lube bay drives it; in summer the helper does.
- Tow trucks unload at the side gate, not on the street.

Saying where we are on the phone: "East Main Street, about a mile east of downtown, on the left, the building with the blue bay doors."
""",
 serves=['challenge:near-duplicate-shop-pages', 'S13'],
 facts=['Hours Mon-Fri 7:30-17:30, Sat 8:00-13:00; the public hours page is the maintained one.',
        'Phone (423) 555-0142; main@brennanautocare.example.',
        'Six customer spaces in front; fleet vans at the back by bay 8; key drop right of the office door; shuttle from the front door at 7:45 and 8:45, driven by the lube technician (slot 15) or the summer helper (F4); tows unload at the side gate.',
        'Phone directions: about a mile east of downtown, on the left, blue bay doors.'],
 new=['Six parking spaces, blue bay doors, the side gate, "about a mile east of downtown" (to be checked against the real address before it is fixed).'],
 ru=['Directions for Московское шоссе in local terms.'])

page('shops/main/who-is-who.md', 'East Main: who is who', 'J', 5,
 'People at the flagship with what each does and their extension.',
 f"""*Last reviewed {D('T-1mo')}*

| Who | Job | Ext. | Ask them about |
|---|---|---|---|
| {S(4,'full')} | Service manager, both Chattanooga shops | 104 | Schedules, discounts over 10 %, complaints, company accounts |
| {S(5,'full')} | Lead advisor | 101 | Estimates, anything at the counter, pricing a job that is not on the list |
| {S(6,'full')} | Service advisor | 102 | Chats and messages; she speaks Spanish |
| {S(7,'full')} | Service advisor | 103 | New this quarter. Be kind, and check his quotes |
| {S(29,'full')} | Service advisor, part-time | 105 | Saturdays and cover days. Seventeen years here: ask her about any regular |
| {S(3,'full')} | Office manager, bookkeeper | 111 | Bills, statements, refunds, payroll hours |
| {S(9,'full')} | Parts manager | 112 | Parts for East Main and Bonny Oaks |
| {S(8,'full')} | Shop foreman | | Who works on what, comebacks, road tests |
| {S(10,'full')} | Diagnostic technician | | Check engine, electrical, hybrids |
| {S(13,'full')} | Electrical technician | | Charging, wiring, A/C |
| {S(11,'full')} | Technician | | Brakes, suspension, heavy line work |
| {S(12,'full')} | Technician | | Maintenance, brakes, cooling, timing belts; he also speaks Spanish |
| {S(14,'full')} | Apprentice | | Works under {S(12)} |
| {S(15,'full')} | Lube and tire | | Oil services, tires, the shuttle |

The main line rings the counter: whoever is next, then all three desks. The foreman and the technicians have no extension. Walk back.

{S(21,'full')} from Bonny Oaks is here two or three days most weeks.

The owners: {S(1,'full')} (ext. 401) is in on Thursdays. {S(2,'full')} (ext. 402) is usually on her laptop somewhere; message her.
""",
 serves=['challenge:fact-in-table', 'S3', 'S8', 'challenge:near-duplicate-shop-pages'],
 facts=['Fourteen people at main with role and extension from cast.json: 104, 101, 102, 103, 105, 111, 112; the foreman and technicians have none.',
        'Slot 6 and slot 12 speak Spanish (cast biographies).',
        'Ring plan: the next desk, then all three (calls design).',
        'Slot 21 is at main two or three days most weeks.',
        'Owners: slot 1 ext. 401, in on Thursdays; slot 2 ext. 402.',
        'Slot 29 is the part-time fourth advisor: Saturday mornings and cover days (cast).'],
 rev=[(4, '@newcomers', 'Caleb Sutton and Hunter Varnell added, Wes Tate removed; message: "New people."'),
      (4, 'T-1mo', 'Travis\'s update (middle rank: proposed by slot 5, approved by slot 4): the "Ask them about" column; message: "So new people know who to ask."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})],
 ru=['Russian names by slot. In the Russian configuration the flagship has a fourth advisor (slot 29) because desks run 2/2 (R12).'])

page('shops/main/opening-and-closing.md', 'East Main: opening and closing', 'J', 4,
 'Opening and closing checklist for the flagship: who, till float, where the deposit goes.',
 f"""*{S(4)} · Last reviewed {D('@early_desk')}*

## Opening

Doors open at 7:30. Since {D('@early_desk')} the first desk shift of the day starts at opening and is on the schedule as the early desk: that advisor is logged in and on the phone when the door is unlocked.

1. Alarm off. The code is given in person, never written down, and that includes here.
2. Empty the **key drop box** first. Each envelope becomes an order before the phones start.
3. Listen to the voicemail and work the missed-call list: [Missed calls and call backs](../../how-to/missed-calls-and-call-backs.md).
4. Count the till float: **$200**. Write it on the count sheet.
5. Coffee on, waiting room lights, front door at 7:30 sharp. People are standing there at 7:25.

{S(8)} opens the bays and the compressor. That is his, not the counter's.

## Closing

Last advisor out, normally 5:30.

1. Every customer car is inside or locked on the lot, keys in the key cabinet, cabinet locked.
2. Close the till: [Closing the till](../../how-to/closing-the-till.md). Float of $200 stays in the drawer. The rest goes in the deposit bag.
3. **The deposit bag goes in the office safe.** {S(3)} banks it the next morning.
4. Check the key drop box is empty and its slot is clear.
5. Bay doors down, compressor off (ask the last technician), lights, alarm on.

Saturday is the same, with two at the desk: [Saturdays](saturdays.md).
""",
 serves=['challenge:near-duplicate-shop-pages', 'S3', 'S2'],
 facts=['Doors at 7:30; the early desk shift starts at opening (stories/S03: "a desk shift from opening") and exists since {{@early_desk}} = the Monday of week T-3.',
        'Opening order: alarm, key drop box, voicemail and missed calls, till float 200 USD, front door.',
        'The foreman opens the bays and compressor.',
        'Closing: cars in or locked, keys in the cabinet; till closed with 200 USD left as float; deposit bag in the office safe, banked next morning by slot 3; key drop empty; bays, compressor, lights, alarm.',
        'The alarm code is never written down.'],
 new=['Till float at East Main 200 USD; the deposit goes to the office safe and is banked by slot 3 next morning. The ERP cash_drawer_close expected figure excludes or includes the float consistently with how-to/closing-the-till.md.',
      ],
 rev=[(4, '@early_desk', 'opening section rewritten for the early desk shift, missed-call list added as step 3; message: "Early desk from today."')],
 ru=['Opening 9:00; early desk from 8:30 (new fact, mirrors S3 in the Russian hours 9:00-11:30). Float in RUB as a new fact (for example 5 000).'])

page('shops/main/how-the-day-runs.md', 'East Main: how the day runs', 'J', 5,
 'The flagship\'s local habits: the morning rush, lunch cover, diagnostics queue, Thursday.',
 f"""*{S(5)} · Last reviewed {D('@early_desk')}*

**7:30 to 10:00 is the whole game.** Four cars in ten arrive in the first hour and a half, and that is also when the phone rings most. It used to be one advisor checking cars in while the phone rang out. Since {D('@early_desk')} there are two of us at the desk for those hours: one takes the line of people, the other takes the phone and does nothing else. Do not both go out to the lot.

- Mondays are the worst morning. If you are the phone person on a Monday, you do not leave the desk until 10:00, for anything.
- {S(8)} hands out the work at 7:30 from the day's appointments. A car that was not booked goes to him before you promise it to anyone.
- **Diagnostics go to {S(10)}** and he takes about four a day. Book check-engine and electrical jobs into his column, not "any tech". When his column is full it is full: offer the next day, or Bonny Oaks, where {S(18)} takes overflow.
- Lunch is staggered between 11:30 and 1:30. The desk is never empty and the phone is never on voicemail in opening hours.
- Parts runs land about 9:15, 12:15 and 3:15. Call customers about "is my car ready" after a run, not before.
- Ready calls go out by 4:30. After 5:00 people are driving and do not answer.
- Thursday mornings {S(1)} is in the waiting room with a coffee, talking to whoever is there. Customers like it. If he quotes anybody a price, it does not count; he knows.
""",
 serves=['S3', 'S5', 'challenge:combine-kb-and-data'],
 facts=['The rush is 7:30 to 10:00; about four cars in ten arrive by 9:00 (mix.json hour curve: 16 % at 7:30 plus 24 % at 8:00).',
        'Since {{@early_desk}} two advisors cover the desk in those hours: one for the counter, one for the phone only (S3: required cover raised from one to two).',
        'Mondays are the worst morning (S3: still 19 % missed).',
        'The foreman hands out work at 7:30.',
        'Diagnostics go to slot 10, about four a day; overflow to slot 18 at Bonny Oaks (S5: eleven orders moved to east during his leave).',
        'Lunch staggered 11:30-13:30; parts land about 9:15, 12:15, 15:15; ready calls by 16:30.',
        'Slot 1 is in on Thursday mornings and his prices do not count.'],
 new=['Slot 10 takes about four diagnostic jobs a day. Reason: gives his leave a capacity to be missed; the ERP\'s diagnostic orders per day at main should fit.'],
 rev=[(4, '@early_desk', 'Travis\'s rewrite of the first paragraph for the early desk (proposed by slot 5, approved by slot 4); message: "Two at the desk in the morning."', {'kind': 'proposal', 'proposer_slot': '5', 'approver_slot': '4'})],
 ru=['Rush 9:00-11:30 (design S3). Arrival curve from mix.json ru.'])

page('shops/main/saturdays.md', 'East Main: Saturdays', 'J', 4,
 'What the Saturday morning shift takes and does not take.',
 f"""*{S(4)}*

Saturday 8:00 to 1:00, East Main only. Two at the desk: {S(29)} every Saturday, and one of the three weekday advisors in turn. Two technicians, in turn. The turn is on the schedule; to give up your Saturday, ask for a change of date in the app and name who takes the shift.

**We take:** oil services, tires, rotations, batteries, wipers and bulbs, brake jobs that were inspected during the week and have their parts on the shelf, and pick-ups of cars finished on Friday.

**We do not take:** diagnostics ({S(10)} does not work Saturdays), anything that needs a part ordered that morning (one parts run, at 9:00, and it is not guaranteed), anything over three hours.

- The last car in is 11:30.
- If a Saturday customer needs a diagnosis, book Monday with {S(10)}'s column and say so plainly. Do not let a technician "have a quick look" that turns into a car stuck on a lift over the weekend.
- Company vehicles are welcome on Saturday for maintenance. Driver limits apply as on any day.
- Bonny Oaks' phone is forwarded to East Main on Saturday mornings. Take the message and book into Bonny Oaks' Monday.
""",
 serves=['challenge:near-duplicate-shop-pages', 'challenge:combine-policy-and-price', 'S14'],
 facts=['Saturday 8:00-13:00 at East Main only; two at the desk (slot 29 every Saturday plus one advisor in turn: stories/S03) and two technicians in turn.',
        'Taken: maintenance, tyres, batteries, small items, pre-inspected brake jobs with parts on the shelf, pick-ups.',
        'Not taken: diagnostics (slot 10 does not work Saturdays), jobs needing a part ordered that morning (one run at 9:00), jobs over three hours.',
        'Last car in at 11:30.',
        'Bonny Oaks\'s line forwards to East Main on Saturday mornings.'],
 new=['No diagnostics on Saturdays; last car 11:30; one parts run at 9:00; Bonny Oaks\'s Saturday forwarding. The ERP should hold no diagnostic lead jobs on Saturdays and the call log should attribute Saturday calls on the east line to main.'],
 ru=['Russian shops open every day; this page becomes "weekends" (Sat index 1.10, Sun 0.82 in mix.json ru) with the 2/2 desks.'])

# ---------------------------------------------------------------- Bonny Oaks
page('shops/east/README.md', 'Bonny Oaks', 'J', 16,
 'Front page of the second home shop\'s pages.',
 f"""Our second Chattanooga shop, six bays, open eleven years. Smaller than East Main and, I will say it, tidier.

- [Hours and getting here](hours-and-getting-here.md)
- [Who is who](who-is-who.md)
- [Opening and closing](opening-and-closing.md)
- [How the day runs](how-the-day-runs.md)

What we send to East Main: hybrids, the hardest electrical faults, newer cars that need an A/C recharge, crew-cab trucks for alignment. Everything else we do here.

{S(16)}
""",
 serves=['challenge:near-duplicate-shop-pages'],
 facts=['Six bays, open eleven years.',
        'Sent to East Main: hybrids, the hardest electrical faults, R-1234yf recharges, crew-cab alignments.',
        'Voice: slot 16, signed "Angie".'],
 ru=['«Инженерный» shop.'])

page('shops/east/hours-and-getting-here.md', 'Bonny Oaks: hours and getting here', 'J', 16,
 'Bonny Oaks\'s hours, parking and key drop; no Saturday.',
 f"""**Monday to Friday 7:30 to 5:30.** We are not open on Saturday; East Main is, and our phone goes there on Saturday mornings. Holidays and changed hours are on [Hours and locations](../../customers/hours-and-locations.md).

- 6340 Bonny Oaks Drive, Chattanooga, TN 37416.
- Phone: (423) 555-0167. E-mail: east@brennanautocare.example.
- Park in front, any space. Millsaps vans and other fleet vehicles use the side lot.
- The key drop box is to the **left** of the office door, under the light.
- The shuttle leaves at 7:45 and 8:45, same as East Main. {S(19)} or {S(21)} drives.
- There is no parts counter here. Parts questions go to {S(9)} at East Main, ext. 112.

{S(16)}
""",
 serves=['challenge:near-duplicate-shop-pages', 'S13'],
 facts=['Hours Mon-Fri 7:30-17:30; no Saturday; the line forwards to East Main on Saturday mornings.',
        '6340 Bonny Oaks Drive, Chattanooga, TN 37416 (ledger geo.address.east). Phone (423) 555-0167; east@brennanautocare.example.',
        'Fleet vehicles use the side lot; key drop left of the office door (East Main: right); shuttle 7:45 and 8:45 driven by slot 19 or 21; no parts counter.'],
 new=['Key drop on the left at Bonny Oaks, on the right at East Main: a small difference planted for the near-identical pages.'],
 ru=['10-й Инженерный проезд, 30.'])

page('shops/east/who-is-who.md', 'Bonny Oaks: who is who', 'J', 16,
 'People at Bonny Oaks.',
 f"""*Last reviewed {D('T-2mo')}*

| Who | Job | Ext. |
|---|---|---|
| {S(16,'full')} | Lead advisor | 201 |
| {S(17,'full')} | Service advisor | 202 |
| {S(18,'full')} | Lead technician | |
| {S(19,'full')} | Technician | |
| {S(20,'full')} | Technician | |
| {S(21,'full')} | Technician, here and at East Main | |

{S(4,'full')} is our manager. He is here on Tuesdays and Thursdays and on the phone the rest of the time (East Main ext. 104).

{S(18)} checks every brake and suspension job before it leaves, whoever did it.

When I am off, {S(17)} has the counter. {S(6)} from East Main comes over on some of those days. If you are covering, my notes on the regulars are in the customer notes, not in my head. Read them before you call anybody.

{S(16)}
""",
 serves=['S5', 'challenge:near-duplicate-shop-pages', 'challenge:fact-in-table'],
 facts=['Six people at east with extensions 201 and 202 (cast.json).',
        'Slot 4 is on site Tuesdays and Thursdays.',
        'Slot 18 checks every brake and suspension job before it leaves (cast: why east has the fewest comebacks).',
        'When slot 16 is off, slot 17 has the counter; slot 6 comes over on some days (S5).'],
 new=['Slot 4 is at Bonny Oaks on Tuesdays and Thursdays. His shifts in the roster should place him so.'],
 ru=['Russian names by slot; lead advisors work 2/2 in the Russian configuration.'])

page('shops/east/opening-and-closing.md', 'Bonny Oaks: opening and closing', 'J', 16,
 'Opening and closing at Bonny Oaks: different float and deposit route from East Main.',
 f"""*{S(16)} · Last reviewed {D('T-5mo')}*

## Opening

Doors at 7:30. Be at the desk and logged in before them.

1. Alarm off.
2. Key drop box, to the left of the door. Envelopes into orders.
3. Voicemail, then the missed-call list. Saturday's messages for us are on East Main's list; ask them on Monday morning if nothing came across.
4. Count the float: **$150**.
5. Lights, coffee, door.

{S(18)} opens the bays.

## Closing

1. Cars in or locked. Keys in the cabinet.
2. Close the till: [Closing the till](../../how-to/closing-the-till.md). $150 stays in the drawer.
3. **The deposit bag goes in the drop safe under the counter.** We have no office here. {S(9)} takes it to East Main on his 1:00 run the next working day and {S(3)} banks it with theirs. He signs the bag log when he takes it.
4. Bay doors, compressor, lights, alarm.

Leave the bays and the side lot clear on Friday night: five Millsaps vans arrive at 7:30 on Monday.

{S(16)}
""",
 serves=['challenge:near-duplicate-shop-pages', 'S2', 'S1'],
 facts=['Doors 7:30.',
        'Float 150 USD (East Main 200).',
        'Deposit bag goes into the drop safe under the counter; slot 9 carries it to East Main on the 13:00 run next working day and signs the bag log; slot 3 banks it.',
        'Saturday messages for Bonny Oaks are on East Main\'s list.',
        'Bays and side lot are left clear on Friday night for A2\'s five vans on Monday.',
        'Slot 18 opens the bays.'],
 new=['Float 150 USD at Bonny Oaks; drop safe; the bag travels on the parts run. The ERP till closes for east use a 150 float.'],
 ru=['Float in RUB (for example 3 000); инкассация: the bag goes to the main shop with the parts run.'])

page('shops/east/how-the-day-runs.md', 'Bonny Oaks: how the day runs', 'J', 16,
 'The east shop\'s habits in its lead advisor\'s words: the photo before the price, Mondays, cover.',
 f"""*{S(16)} · Last reviewed {D('T-2mo')}*

A few things we do here that I would like done the same way when I am not in the building.

**Photo before price.** Nobody at this counter says a number until the customer has seen the part or the picture. "Here is your front pad, here is a new one" does more than any explanation. The technicians know: no photo, I send them back.

**Ask for the yes.** After the price, I offer two times. "I can do it this afternoon while it is here, or Thursday morning. Which is better?" If you stop at the price, the customer says "let me think about it", and that is the last we hear.

**Declined is not gone.** Whatever was declined last visit is the first thing I look at when the car is booked again. It is in the history. Mention it at drop-off, not at pick-up.

**Mondays** belong to Millsaps until about 10:00: [their page](../../accounts/a2.md). Book retail customers from 9:30 on Mondays if you can.

**Diagnostics.** {S(18)} takes them here, and takes East Main's overflow when {S(10)} is full. Two a day is his limit alongside the rest.

**The phone.** Two of us, and one of us is always with a customer. If you are alone at the counter and the phone rings, say "one moment" to the person in front of you and answer it. A person in the room will wait thirty seconds. A caller will not.

{S(16)}
""",
 serves=['S5', 'S4', 'challenge:combine-kb-and-data'],
 facts=['House rules of slot 16: photo before price; two times offered after the price; declined work raised at the next drop-off.',
        'Mondays belong to account A2 until about 10:00; retail from 9:30.',
        'Slot 18 takes diagnostics at east, two a day, plus overflow from main.',
        'The phone is answered even with a customer present.',
        'These habits are what the scorecard rewards (offered_time, asked_for_booking) and why east sells more recommended work with her (63 % with her, 52 % without per design 7.2).'],
 new=['Slot 18\'s limit of two diagnostic jobs a day.'],
 ru=['Same habits in slot 16\'s Russian voice.'])

# ---------------------------------------------------------------- Charlotte Pike
page('shops/west/README.md', 'Charlotte Pike', 'J', 22,
 'The bought shop\'s front page as its manager wrote it thirteen months ago: thin and out of date on Saturday hours and on who works the counter.',
 f"""*{S(22)} · {D('T-13mo')}*

6399 Charlotte Pike, Nashville. Six bays. Been a repair shop on this spot a long time and most of our customers have been coming just as long.

Open Monday to Friday 7:30 to 5:30, Saturday 8 to 12.

Phone (615) 555-0119.

Counter: {PEOPLE['F1']['en']['full_name'].split()[0]} and {S(23)}.
Shop: {S(25)}, {S(27)}, {S(26)}.

We know our customers. Ask before you change something that works.

- [Opening and closing](opening-and-closing.md)
- [Parts](parts.md)
- [Answering the phone](answering-the-phone.md)
- [Tow trucks we use](tow-trucks.md)
""",
 broken=['shops/west/tow-trucks.md'],
 serves=['S13', 'S2', 'challenge:near-duplicate-shop-pages', 'operate:contradiction', 'challenge:combine-kb-and-data', 'challenge:broken-link', 'challenge:kb-does-not-say'],
 facts=['STALE ON PURPOSE in two places. (1) Saturday 8 to 12: Charlotte Pike has not opened on Saturdays since the purchase; the public hours page and shops/README.md say Monday to Friday. (2) The counter: names Brent (slot F1, fired at T-5 months) and omits slot 24 (hired T-10 months, cast.json) and slot 28 (hired T-9 months); team/who-is-who.md is right.',
        'Address 6399 Charlotte Pike, Nashville; six bays; (615) 555-0119.',
        'Written by slot 22 at T-13 months; the link to answering-the-phone.md was added later by slot 2.',
        'BROKEN LINK ON PURPOSE: "Tow trucks we use" points to tow-trucks.md, a page that was never written. kb_links reports it as missing. Nashville\'s tow partner is stated nowhere.',
        'Voice: slot 22, curt, proprietary.'],
 new=['Charlotte Pike opened on Saturday mornings under its previous owner and stopped at the purchase. Reason: gives the bought shop\'s page a plausible way to be wrong about hours. No Saturday orders at west in the ERP after T-14 months (its records start that day anyway).'],
 stale='S13/S2: Saturday hours and counter staff out of date',
 rev=[(2, 'T-2mo', 'one line added: the link to "Answering the phone"; nothing else touched; message: "Link to Jasmine\'s page."')],
 ru=['Казань, Техническая, 30. Russian shops open every day, so the stale fact is different: for example the page says 9:00-19:00 while the company\'s hours are 9:00-20:00. The fired advisor is Артур.'])

page('shops/west/opening-and-closing.md', 'Charlotte Pike: opening and closing', 'J', 22,
 'Charlotte Pike\'s short checklist, with the till rule the managing owner changed after S2.',
 f"""*{S(22)} · changed by {S(2,'full')} {D('@discount_rule')}*

Open at 7:30. Whoever is first unlocks and empties the key box.

Float is $150.

Close at 5:30. Cars locked, keys in the cabinet.

**The till is counted by two people, every day, and both initial the count sheet.** The advisor who closes counts; {S(22)} counts again. If {S(22)} is out, the second count is the other advisor's. A difference of more than $5 either way is written on the sheet with the reason and reported to the office at East Main the same evening.

**The deposit goes to the bank every working day**, by {S(22)}.

Company procedure: [Closing the till](../../how-to/closing-the-till.md).
""",
 serves=['S2', 'challenge:near-duplicate-shop-pages', 'operate:find-what-changed'],
 facts=['Opens 7:30; first in unlocks and empties the key box; float 150 USD; closes 17:30.',
        'Since {{@discount_rule}}: the till is counted by two people daily, both initial; differences over 5 USD are written with a reason and reported to the office the same evening; the deposit is banked every working day by slot 22.',
        'The history shows what it said before: "Whoever closes counts the drawer. Bank Monday and Thursday." (the arrangement under which slot F1 closed the till short on 19 days).',
        'All times are Central.'],
 new=['Before the change: one person counted and the bank run was Monday and Thursday. After: two counts and daily banking. ERP cash_drawer_close rows at west after T-5 months should show small differences only.',
      'Float 150 USD at Charlotte Pike.'],
 rev=[(2, '@discount_rule', 'replaced "Whoever closes counts the drawer. Bank Monday and Thursday." with the two-person count and daily banking; message: "Two counts, every day. Deposit daily."')],
 ru=['Same change. Russian cash handling: Z-отчёт at the register at closing, инкассация daily.'])

page('shops/west/parts.md', 'Charlotte Pike: parts', 'J', 22,
 'How Nashville orders parts, in its manager\'s words.',
 f"""*{S(22)} · {D('T-12mo')}*

We order from {V('V2')}, {V('V2','phone')}. Have for years. Two trucks a day, call by 9 for the morning one and by 2 for the afternoon.

Import stuff from {V('V3')}, comes next morning.

Tires from {V('V5')}, Tuesdays and Fridays.

The advisor who wrote the job orders the part. Write the part on the order.

If it's not here when they said, call them, don't call the customer till you know.
""",
 serves=['S6', 'challenge:near-duplicate-shop-pages', 'operate:contradiction', 'S15'],
 facts=['West orders from V2 Harpeth Valley Parts Supply, (615) 555-0123: two runs, order by 9:00 and 14:00 (Central).',
        'Import parts from V3 next morning; tyres from V5 Tuesday and Friday.',
        'The advisor who wrote the job orders the part (there is no parts manager at west).',
        'Says nothing about part numbers, tiers or the house-brand pads; parts are often typed by hand at west (ERP mess kind 7: 9 % of part lines).',
        'Disagrees in spirit with parts/suppliers.md and parts/brake-pads-we-fit.md, where the parts manager wants west moved to V1 (S6).'],
 new=['Order-by times at west: 9:00 and 14:00 Central.'],
 ru=['Old supplier from vendors.json ru.'])

page('shops/west/answering-the-phone.md', 'Charlotte Pike: answering the phone', 'J', 24,
 'The newest Nashville advisor\'s page on how the phone is answered there; the bright spot in a thin folder.',
 f"""*Written by {S(24,'full')} · published by {S(2,'full')} {D('T-2mo')}*

How I answer, and how I would love for all of us to.

**The greeting:** "Thank you for calling Brennan Auto Care on Charlotte Pike, this is {S(24)}." Our name, where we are, your name. Callers who dialed the wrong shop find out in the first breath.

**Then, every call:**

1. Their name, and "is this the best number for you?" Read the number back.
2. The car: year, make, model. And what it is doing, in their words. One more question than feels necessary.
3. If they ask a price, give it from the price list **with a time attached**: "A brake inspection is {t('brake_inspection')}, and I could get you in tomorrow at 7:30."
4. Offer two times. Not "when would you like to come in".
5. Say the booking back: day, time, Charlotte Pike, what we are doing.

**If a customer is standing in front of you:** "Excuse me one second," answer, take the name and number, and promise a call back within the hour. Then call back within the hour. A phone that rings out is a customer who calls the next shop.

**"What I can do is."** We cannot always say yes. We can always say what we can do.

We are on Central time. If Chattanooga says "call me at nine", ask which nine.
""",
 serves=['S3', 'S4', 'challenge:near-duplicate', 'S9'],
 facts=['Greeting: company name, shop, own name.',
        'Five steps: name and number read back; car and problem with one extra question; price from the price list with a time attached (example: brake inspection 49.95 and a time tomorrow at 7:30); two times offered; booking read back.',
        'With a customer present: answer, take name and number, call back within the hour.',
        'The steps are the scorecard\'s checks (greeting, name_and_number, need_discovery, price_with_next_step, offered_time, asked_for_booking, recap).',
        'Central time reminder.',
        'Juniors cannot publish: written by slot 24, published by slot 2 at T-2 months.',
        'Near-duplicate of how-to/taking-a-call.md in subject; they agree.'],
 created=(2, 'T-2mo'),
 ru=['Greeting «Ермак-Сервис на Технической, Камила, здравствуйте». Kazan is an hour behind Ulyanovsk.'])
