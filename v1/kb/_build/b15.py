from kbb import *
import kbb, json, os
m = kbb._m
def nt(k, cls='car', tier='standard'): return kbb.num_total(k, tier, 'after_rise', cls)
CLS = ['car', 'suv', 'truck', 'van']
JOBS2 = [('front_pads_rotors', 'Front brake pads & rotors'), ('rear_pads_rotors', 'Rear brake pads & rotors'), ('front_brake_pads', 'Front brake pads'),
         ('front_struts_pair', 'Front struts, pair'), ('rear_shocks_pair', 'Rear shocks, pair'), ('wheel_bearing', 'Front wheel bearing, one side'),
         ('wheel_alignment', 'Four-wheel alignment'), ('new_tyres_fitted', 'Mount & balance 4 tires, labour only'), ('alternator', 'Alternator'), ('starter', 'Starter'),
         ('water_pump', 'Water pump'), ('radiator', 'Radiator'), ('spark_plugs', 'Spark plugs (4 / 6 / 8 / 8 cyl.)')]
rows = []; classfacts = []
for k, n in JOBS2:
    vals = []
    for c in CLS:
        if k == 'new_tyres_fitted':
            v = round(kbb.labour(k, 'after_rise', c) + 1e-9, 2)
        elif k == 'spark_plugs':
            n_plugs = {'car': 4, 'suv': 6, 'truck': 8, 'van': 8}[c]
            plug = next(o for o in JOBS[k]['parts'][0]['options'] if o['tier'] == 'standard' and not o.get('story'))
            unit = round(plug['list_price'] * CFG['parts_class_multiplier'][c] + 1e-9, 2)
            v = round(kbb.labour(k, 'after_rise', c) + round(n_plugs * unit + 1e-9, 2) + 1e-9, 2)
        else:
            v = nt(k, c)
        vals.append(v)
    classfacts.append({'catalogue_key': k, 'car': vals[0], 'suv': vals[1], 'truck': vals[2], 'van': vals[3]})
    rows.append(f"| {n} | {m(vals[0])} | {m(vals[1])} | {m(vals[2])} | {m(vals[3])} |")
menu = [('oil_service', 'Full synthetic oil & filter change, up to 5 qt'), ('tyre_rotation', 'Tire rotation'), ('wheel_balance', 'Balance 4 wheels'), ('tyre_repair', 'Flat repair'),
        ('wheel_alignment', 'Four-wheel alignment (car, SUV)'), ('brake_inspection', 'Brake inspection'), ('suspension_diag', 'Steering & suspension inspection'),
        ('ac_performance_check', 'A/C performance check'), ('check_engine_diag', 'Check engine light diagnosis, 1 hr'), ('electrical_diag', 'Electrical diagnosis, 1.5 hr'),
        ('brake_fluid_exchange', 'Brake fluid flush'), ('coolant_exchange', 'Coolant drain, flush & fill'), ('ac_recharge', 'A/C evacuate & recharge, R-134a'),
        ('ac_recharge_1234yf', 'A/C evacuate & recharge, R-1234yf'), ('pre_purchase_inspection', 'Pre-purchase inspection'), ('battery_replace', 'Battery, standard grade, installed')]
menurows = '\n'.join(f"| {n} | {m(nt(k))} |" for k, n in menu)

FLUID = [
 ('Ford Transit-250 Cargo Van', '3.7L V6', '5W-20', '6.0', 'Orange (Motorcraft)', 'Mercon LV', 'Nickajack, Millsaps, Cumberland Bend, Sourwood'),
 ('Ford Transit Connect', '2.5L 4-cyl', '5W-20', '5.7', 'Orange (Motorcraft)', 'Mercon LV', 'Nickajack, Moccasin Bend, Sourwood'),
 ('Ram ProMaster 2500', '3.6L V6', '5W-20', '6.0', 'Purple (Mopar OAT)', 'ATF+4', 'Nickajack, Sourwood, Cumberland Bend'),
 ('Mercedes Sprinter 2500', '3.0L V6 diesel', '5W-30, MB 229.52 only', '13.0', 'Blue (MB)', 'Not serviced by us', 'Nickajack ND-34, ND-35'),
 ('Chevrolet Express 2500', '6.0L V8', '5W-30 dexos', '6.0', 'Orange (Dex-Cool)', 'Dexron VI', 'Millsaps, Cumberland Bend, Moccasin Bend MB-8'),
 ('Ford F-250 Super Duty', '6.2L V8 gas', '5W-20', '7.0', 'Orange (Motorcraft)', 'Mercon LV', 'Millsaps M-121 to M-123'),
 ('Ford F-150', '5.0L V8 (2017)', '5W-20', '7.7', 'Orange (Motorcraft)', 'Mercon LV', 'Cumberland Bend E-8'),
 ('Chevrolet Silverado 2500HD', '6.0L V8', '5W-30 dexos', '6.0', 'Orange (Dex-Cool)', 'Dexron VI', 'Cumberland Bend E-11'),
 ('Toyota Corolla', '1.8L 4-cyl', '0W-20', '4.4', 'Pink (Toyota SLLC)', 'CVT: Toyota CVT FE only', 'Missionary Ridge, Moccasin Bend MB-9'),
 ('Honda Civic', '2.0L 4-cyl', '0W-20', '4.4', 'Blue (Honda Type 2)', 'CVT: Honda HCF-2 only', 'Missionary Ridge Car 6'),
 ('Toyota Camry', '2.5L 4-cyl', '0W-20', '4.6 (bill 5)', 'Pink (Toyota SLLC)', 'Toyota WS', 'retail, the most common car we see'),
 ('Honda CR-V', '2.4L 4-cyl (2012-2014)', '0W-20', '4.4', 'Blue (Honda Type 2)', 'Honda DW-1', 'retail'),
 ('Subaru Outback', '2.5L (to 2012, timing belt engine)', '5W-30', '4.4', 'Blue (Subaru Super)', 'Subaru ATF-HP', 'retail'),
]
fl = '\n'.join('| ' + ' | '.join(r) + ' |' for r in FLUID)
fl_pdf = '\n'.join('| ' + ' | '.join(r) + ' |' for r in FLUID)
extra_xlsx = [('Hyundai Elantra', '2.0L 4-cyl', '0W-20', 'to be filled in', 'to be filled in', 'to be filled in', 'Missionary Ridge Car 3, Car 4'),
              ('Nissan Sentra', '2.0L 4-cyl', '0W-20', 'to be filled in', 'to be filled in', 'CVT: Nissan NS-3 only', 'Missionary Ridge Car 5, Car 8')]
fx = '\n'.join('| ' + ' | '.join(r) + ' |' for r in extra_xlsx)

doc = f"""# Binary documents of the knowledge base

Five files are not Markdown. Each is drafted here as Markdown; a later step converts it to the stated format and puts it at the stated path beside the pages. Placeholders follow the grammar in `OUTLINE.md`. What the knowledge engine does with each format (read in its `docs/search.md`): **PDF, DOCX and PPTX are extracted to text** and searched, with a locator per segment (PDF: page; DOCX: paragraph and section heading; PPTX: slide and slide title). **XLSX is not extracted**: the file is found by its name and cannot be read by the assistant. There is no OCR, so the PDFs must be text PDFs, not scans. The italic paragraph under each file's heading describes the file for the converter and is not part of the file.

| # | Path | Format | Visibility | Pages or slides | Facts that exist only here |
|---|---|---|---|---|---|
| 1 | `prices/counter-price-sheet.pdf` | PDF, US letter, text | staff | 2 pages | prices by vehicle class for thirteen common jobs (page 2) |
| 2 | `team/staff-handbook.docx` | Word | staff | about 9 pages, 12 headings | time off, paid holidays, the lateness ladder, allowances, notice |
| 3 | `parts/fleet-fluid-sheet.xlsx` | Excel, one sheet "Fluids" | staff | 15 rows | unreadable by the assistant; two rows the PDF lacks |
| 4 | `parts/fleet-fluid-sheet.pdf` | PDF, landscape, text | staff | 1 page | oil quantity and specification, coolant and transmission fluid by vehicle |
| 5 | `team/the-call-in-eight-moves.pptx` | PowerPoint | staff | 10 slides | the lead advisor's "three sentences I never say" (slide 9), her doubt script (slide 8) |

---

## 1. `prices/counter-price-sheet.pdf`

*The sheet taped beside each counter terminal. Two pages. Page 1 and page 2 must be separate PDF pages, because the eval questions rely on the page locator.*

### Page 1

**Brennan Auto Care · Counter price sheet**
In force from {D('@price_rise')} · Labour {rate()} an hour · Before sales tax (9.25 % in Chattanooga, 9.75 % at Charlotte Pike)

Menu and common services, car or small crossover:

| Service | Price |
|---|---:|
{menurows}

Battery, starting and charging test: free. Courtesy inspection: free.
Shop supplies: 5 % of labour on hourly jobs, at most $35.00 a bill. Menu jobs: none.
Tire fees: $4.85 a tire on new tires.
**Not on this sheet = not a price. Look it up in the price list or ask your lead.**

### Page 2

**By vehicle class** · standard parts · before supplies and tax

| Job | Car | SUV | Truck | Van |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

Car: Camry, Civic, Outback, RAV4, Equinox. SUV: Explorer, Highlander, Odyssey, Grand Cherokee. Truck: F-150, Silverado, Tacoma, Tahoe. Van: Transit, ProMaster, Express, Sprinter.
Company-rate accounts ({A('A1')}, {A('A2')}): price from the shop system, not from this sheet.
Printed {D('@price_rise')}. Throw away any sheet with an earlier date.

---

## 2. `team/staff-handbook.docx`

*Word document, about nine pages, with real Word heading styles (Heading 1 for the title, Heading 2 for each numbered section) so that the extractor returns the section with every paragraph. First written by {S(1,'full')}; revised by {S(2,'full')}.*

# Brennan Auto Care · Staff handbook

Revised {D('@golive+2w')}. This replaces every earlier handbook. A paper copy is in the binder in each break room.

## 1. Welcome

My father told his first hire two things: fix it right, and tell the customer the truth even when it costs you the job. That is still the whole handbook. The rest is detail. {S(1,'full')} and {S(2,'full')}

## 2. Hours and attendance

The shops are open Monday to Friday, 7:30 to 5:30. East Main is also open Saturday, 8:00 to 1:00. Your own hours are on the schedule in Traciora, which is published by Thursday noon for the following week.

Clock in when you arrive at the shop and out when you leave. You are late if you clock in more than five minutes after your shift starts.

Lateness is counted over any 30 days:

- Three late arrivals: your manager talks to you. Nothing is written.
- Five late arrivals: a written warning.
- A second written warning within six months: your job is reviewed, and it may end.

Not coming in without calling is different. Call the shop before 7:00. Two days absent without a call in twelve months may end your employment.

## 3. Pay

You are paid every second Friday for the two weeks that ended the Saturday before. How your job is paid (hourly, flat rate or salary) is in your offer letter. Overtime for hourly staff is paid after 40 hours in a week and must be agreed beforehand.

## 4. Time off

Paid time off, for full-time staff:

| Length of service | Days a year |
|---|---|
| First 90 days | None |
| After 90 days, in the first year | 5 |
| From 1 year | 10 |
| From 5 years | 15 |
| From 15 years | 20 |

Ask in Traciora at least 14 days ahead for a week or more, 7 days for a day or two. No more than one person from a counter and two from a shop floor may be off in the same week. Unused days do not carry over; up to five are paid out in January.

Part-time staff earn time off in proportion to their hours.

## 5. Paid holidays

New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Christmas Day. Six days. When one falls on a weekend we close on the nearest weekday. You are paid for them after 90 days with us.

## 6. If you are sick

Call the shop line before 7:00. You have three paid sick days a year; after that, sick days come out of your time off or are unpaid. More than three days in a row needs a doctor's note.

## 7. Appearance

Technicians: we supply five shirts and five pairs of trousers and launder them weekly. Safety glasses in the bays. Boots are yours; we pay $100 a year toward them. Counter staff: a company shirt, which we supply, and no caps.

## 8. Tools

Technicians bring their own hand tools. The shop supplies lifts, scan tools, the alignment racks, A/C machines, torque wrenches and specialty tools. After your first year we pay $400 a year toward your tools, on receipts. Shop tools go back where they live.

## 9. Training

We pay the test fee for every ASE certificate you pass. Classes we send you to are paid time. A/C work needs the refrigerant certificate; we pay for that course.

## 10. Customers' cars and customers' money

A customer's car is driven for a road test and to move it, nothing else. Never without an order open. Nothing of yours is repaired in a bay without the foreman's permission and an order.

Staff pay cost plus 10 % on parts and nothing for their own labour after hours, with the foreman's permission, on their own car only.

Money: only advisors and managers handle payments. Nobody takes cash for work that is not on an order.

## 11. Phones

Personal phones stay in your pocket in the bays and off the counter. Taking a photo for an inspection is the work phone's job.

## 12. Leaving

We ask for two weeks' notice. Shop shirts, keys and anything of ours come back on your last day. Unused time off that you have earned is paid.

---

## 3. `parts/fleet-fluid-sheet.xlsx`

*Excel workbook, one sheet named "Fluids", header row frozen, kept by {S(9,'full')}. The engine stores it and finds it by name; `kb_read` answers that its text cannot be extracted. It holds the thirteen rows of the PDF and two more, added after the PDF was printed. Drafting note, not part of the file: every quantity and specification in this table was written from memory and has not been checked against the makers' data; each row needs a specialist's read before seed v1 is fixed. The shop's own habit of billing the Camry at 5 quarts matches the catalogue.*

| Vehicle | Engine | Oil | Quarts with filter | Coolant | Transmission fluid | Seen in |
|---|---|---|---|---|---|---|
{fl}
{fx}

Cell A18: "Updated {D('T-2mo')} MG. Elantra and Sentra to finish."

---

## 4. `parts/fleet-fluid-sheet.pdf`

*One landscape page, a text PDF printed from the spreadsheet on {D('T-6mo')} and pinned up in the lube bays. It has the first thirteen rows and not the last two.*

**Fleet fluid sheet · Brennan Auto Care parts** · printed {D('T-6mo')} · MG

| Vehicle | Engine | Oil | Quarts with filter | Coolant | Transmission fluid | Seen in |
|---|---|---|---|---|---|---|
{fl_pdf}

Read the cap before you pour. Bill what went in, rounded up to the half quart. CVT fluid is never ATF.

---

## 5. `team/the-call-in-eight-moves.pptx`

*PowerPoint, ten slides, each with a title (the extractor returns the slide number and its title). {S(16,'full')}'s training deck for new advisors, made {D('T-4mo')} when the call scorecard came in. Speaker notes are not extracted, so nothing that matters may be only in the notes.*

**Slide 1 · The call, in eight moves**
{S(16,'full')}, Bonny Oaks. For new advisors.

**Slide 2 · Two minutes**
A first-time caller decides in about two minutes. They have another number ready. Half of the callers we miss never call again.

**Slide 3 · The eight**
1 Greeting. 2 Name and number. 3 What is going on. 4 Price with a next step. 5 Offer a time. 6 Ask for the booking. 7 Recap. 8 Answer the doubt. Five and six are worth the most.

**Slide 4 · Hello**
"Brennan Auto Care, this is Angie." Smile first. Then their name, and use it twice in the first minute.

**Slide 5 · Find out**
The car. What it is doing. One more question than you need. Never price "brakes" without the car.

**Slide 6 · The price is not the end**
"It is $49.95 for the inspection, and I could get you in Friday at eight." A price with nothing after it is a goodbye.

**Slide 7 · Two times, then be quiet**
"Tomorrow at 7:30 or Friday at 1:00?" Then stop talking. Then: "I have you down. Ask for me." Then say it all back.

**Slide 8 · When they doubt the price**
"Compared with what?" Then what is in our number: the parts by name, the labour, 24 months or 24,000 miles (pads and work vehicles 12 months). Cheaper is a cheaper part, said out loud. Never a quiet discount.

**Slide 9 · Three sentences I never say**
1. "No problem."
2. "It should be ready."
3. "It is all warrantied."
The first one sounds like there was a problem. The second is a promise I cannot keep. The third does not answer anything.

**Slide 10 · Listen**
Ask {S(4)} for five of my calls. Write down what I do after I say the price. Then let me listen to five of yours.
"""
open(kbb.OUT + '/en/_binaries.md', 'w').write(doc)

def binfact(path, title, vis, by, purpose, serves, fmt, facts, new, rev, ru, only_here):
    sheet = {'path': path, 'title': title, 'kind': 'binary', 'format': fmt, 'visibility': VIS[vis], 'seen_from': SEEN[vis], 'voice_of_slot': str(by),
             'purpose': purpose, 'serves': serves, 'draft': 'en/_binaries.md', 'facts': facts, 'facts_only_in_this_file': only_here,
             'new_facts': new, 'revisions': rev, 'has_history': len(rev) > 1, 'notes_for_russian_writer': ru}
    fp = kbb.OUT + '/facts/' + path + '.json'; os.makedirs(os.path.dirname(fp), exist_ok=True)
    json.dump(sheet, open(fp, 'w'), ensure_ascii=False, indent=1)
    reg = json.load(open(kbb.REG))
    reg[path] = {'title': title, 'visibility': VIS[vis], 'voice_of_slot': str(by), 'purpose': purpose, 'serves': serves, 'length_class': 'binary: ' + fmt,
                 'links_to': [], 'has_history': len(rev) > 1, 'stale_on_purpose': None, 'broken_links_on_purpose': [], 'n_new': len(new), 'n_rev': len(rev)}
    json.dump(reg, open(kbb.REG, 'w'), ensure_ascii=False, indent=1)

IMP = {'n': 1, 'kind': 'import', 'author': 'operator (History shows "Administrator")', 'text_date': '{{@golive|date}}', 'what': 'the file as it stood on the shared drive'}
binfact('prices/counter-price-sheet.pdf', 'Counter price sheet', 'J', 2, 'Printed price sheet for the counters: menu services on page 1, prices by vehicle class on page 2.',
 ['S12', 'challenge:fact-only-in-attachment', 'challenge:fact-in-table'], 'PDF, 2 pages, text',
 ['Page 1: sixteen menu and common services at the current list (class car), labour hour 135.00, supplies and tire-fee notes (4.85 a tire = 3.50 + 1.35).',
  'Page 2: thirteen jobs priced for car, SUV, truck and van, standard parts.',
  {'by_class_table': classfacts},
  'Spark plugs by class assume 4 / 6 / 8 / 8 cylinders at 21.82 a plug (standard) times the parts class multiplier, plus labour times the job multiplier.',
  'Printed on the day of the rise; replaces earlier sheets.'],
 ['The spark-plug row prices 6 and 8 plugs for SUV, truck and van; the catalogue prices four. The seeder must price a V6 or V8 plug job the same way (per-plug quantity by cylinders) or this row changes.'],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '2', 'text_date': '{{@price_rise|date}}', 'what': 'the sheet reprinted at the new prices and uploaded over the old file; message: "New prices from today."'}],
 ['Russian price sheet from the Russian catalogue with its class multipliers (hours 1 / 1.15 / 1.3 / 1.3; parts 1 / 1.35 / 1.7 / 1.3); no tire fees; prices with VAT inside.'],
 ['every SUV, truck and van price (the Markdown pages give multipliers and one worked example only)'])
binfact('team/staff-handbook.docx', 'Staff handbook', 'J', 2, 'The employee handbook: attendance, pay periods, time off, holidays, allowances, conduct.',
 ['S14', 'challenge:fact-only-in-attachment', 'visibility:worker', 'challenge:kb-does-not-say'], 'DOCX with heading styles, about 9 pages',
 ['Twelve sections: Welcome; Hours and attendance; Pay; Time off; Paid holidays; If you are sick; Appearance; Tools; Training; Customers\' cars and customers\' money; Phones; Leaving.',
  'Late = more than five minutes. Ladder over any 30 days: three lates a talk; five a written warning; a second written warning within six months a review that may end the job. Two days absent without a call in twelve months may end employment.',
  'Paid every second Friday for the two weeks ended the Saturday before.',
  'Paid time off: none in the first 90 days; 5 days after 90 days; 10 from one year; 15 from five years; 20 from fifteen years. Notice 14 days for a week or more, 7 days for a day or two. One person per counter and two per shop floor off in a week. No carry-over; up to five days paid out in January.',
  'Six paid holidays (the closed dates of the ledger), after 90 days.',
  'Three paid sick days; a doctor\'s note after three days in a row.',
  'Uniforms supplied (five sets, laundered weekly); boots allowance 100 USD a year; tool allowance 400 USD a year after the first year; ASE test fees paid on a pass; refrigerant certificate course paid.',
  'Staff parts at cost plus 10 %, own car only, with the foreman\'s permission.',
  'Two weeks\' notice.',
  'Seen from junior: technicians (worker rank) and the website assistant cannot read it; the paper binder is their copy.'],
 ['Every number in the handbook is a new fact: the lateness ladder (3, 5, second warning in six months), no-call rule (two in twelve months), time off 0 / 5 / 10 / 15 / 20 days, notice 14 and 7 days, five days paid out, three sick days, 100 USD boots, 400 USD tools, cost plus 10 %. Reason: a handbook was asked for; the ladder is set so that slot F2 (late four shifts in ten, two written warnings, five absences) is clearly over it and slot 15 (late three shifts in ten, never warned) is over it too, which is the point of his story.',
  'Leave of slot 10 (two weeks) and slot 16 (a week) fits their length of service (15 and 10 days or more).'],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '2', 'text_date': '{{@golive+2w|date}}', 'what': 'the revision the text is dated by, uploaded over the old file two weeks after go-live: the schedule and time-off requests are in Traciora; section 10 gained the sentence "Nobody takes cash for work that is not on an order."; message: "Revised: the schedule and time off are in Traciora; one line added to section 10."'}],
 ['Russian handbook is «Правила внутреннего трудового распорядка» and differs by law: 28 calendar days of paid leave for everyone, sick leave by больничный paid by the state fund, pay twice a month, discipline by the Labour Code (замечание, выговор, увольнение; прогул = absence over four hours). Write those; keep allowances as new facts in RUB.'],
 ['time-off table', 'paid holidays as a staff benefit', 'lateness ladder', 'allowances', 'staff parts price', 'notice period'])
binfact('parts/fleet-fluid-sheet.xlsx', 'Fleet fluid sheet (spreadsheet)', 'J', 9, 'The parts manager\'s working sheet of oil, coolant and transmission fluid by vehicle. Not readable by the assistant.',
 ['challenge:unreadable-binary', 'challenge:fact-only-in-attachment'], 'XLSX, one sheet',
 ['Fifteen rows: the thirteen of the PDF plus Hyundai Elantra and Nissan Sentra (the driving school\'s cars), which are unfinished.',
  'Product fact: the knowledge engine does not extract XLSX. kb_search finds the file by name; kb_read refuses with "not extracted".',
  'The honest answer to a question whose answer is only in the two extra rows is that the spreadsheet cannot be read.'],
 ['All quantities and specifications are recalled, not verified: see the drafting note in en/_binaries.md, which is not part of the file.'],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '4', 'text_date': '{{T-2mo|date}}', 'what': 'Marcus\'s updated file with the two driving-school rows (uploaded by slot 4; juniors cannot publish); message: "Marcus\'s sheet, two new cars."'}],
 ['Litres; the Russian fleets\' models from accounts.json ru.'], ['rows for Hyundai Elantra and Nissan Sentra'])
binfact('parts/fleet-fluid-sheet.pdf', 'Fleet fluid sheet (printed copy)', 'J', 9, 'A one-page print of the fluid sheet: the readable copy.',
 ['challenge:fact-only-in-attachment', 'challenge:fact-in-table', 'S1'], 'PDF, 1 page landscape, text',
 ['Thirteen rows: vehicle, engine, oil, quarts with filter, coolant, transmission fluid, where seen.',
  {'rows': [dict(zip(['vehicle', 'engine', 'oil', 'quarts_with_filter', 'coolant', 'transmission_fluid', 'seen_in'], r)) for r in FLUID]},
  'Printed T-6 months; older than the spreadsheet by two rows.',
  'The Sprinter takes 13.0 quarts of MB 229.52 oil, which is not stocked: agrees with the Nickajack page (Sprinters: fluids and filters only, oil ordered with the job).'],
 ['All thirteen rows are recalled, not verified.'], [IMP],
 ['Litres; Russian models.'], ['every quantity and specification'])
binfact('team/the-call-in-eight-moves.pptx', 'The call, in eight moves', 'J', 16, 'The lead advisor\'s ten-slide training deck on taking a call.',
 ['S4', 'challenge:fact-only-in-attachment', 'challenge:near-duplicate'], 'PPTX, 10 titled slides',
 ['Slides: title; two minutes; the eight; hello; find out; the price is not the end; two times; when they doubt the price; three sentences I never say; listen.',
  'Slide 9: "No problem." "It should be ready." "It is all warrantied.", each with her reason.',
  'Slide 6 uses the brake inspection price 49.95.',
  'Agrees with how-to/taking-a-call.md and how-to/price-objections.md; says nothing they contradict.',
  'Speaker notes are not extracted.'],
 [], [{'n': 1, 'kind': 'edit', 'author_slot': '4', 'text_date': '{{T-4mo|date}}', 'what': 'file uploaded for Angie (binary uploads are edits: published by slot 4); message: "Angie\'s training deck."'}],
 ['Russian deck in slot 16\'s voice; the three sentences: «Без проблем», «Должно быть готово», «У нас на всё гарантия».'], ['the three sentences of slide 9'])
print('ok')
