# Binary documents of the knowledge base

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
In force from {{@price_rise|date}} · Labour $135.00 an hour · Before sales tax (9.25 % in Chattanooga, 9.75 % at Charlotte Pike)

Menu and common services, car or small crossover:

| Service | Price |
|---|---:|
| Full synthetic oil & filter change, up to 5 qt | $90.95 |
| Tire rotation | $25.00 |
| Balance 4 wheels | $60.00 |
| Flat repair | $31.00 |
| Four-wheel alignment (car, SUV) | $119.95 |
| Brake inspection | $49.95 |
| Steering & suspension inspection | $49.95 |
| A/C performance check | $49.95 |
| Check engine light diagnosis, 1 hr | $135.00 |
| Electrical diagnosis, 1.5 hr | $202.50 |
| Brake fluid flush | $151.00 |
| Coolant drain, flush & fill | $193.00 |
| A/C evacuate & recharge, R-134a | $207.40 |
| A/C evacuate & recharge, R-1234yf | $278.80 |
| Pre-purchase inspection | $149.95 |
| Battery, standard grade, installed | $239.95 |

Battery, starting and charging test: free. Courtesy inspection: free.
Shop supplies: 5 % of labour on hourly jobs, at most $35.00 a bill. Menu jobs: none.
Tire fees: $4.85 a tire on new tires.
**Not on this sheet = not a price. Look it up in the price list or ask your lead.**

### Page 2

**By vehicle class** · standard parts · before supplies and tax

| Job | Car | SUV | Truck | Van |
|---|---:|---:|---:|---:|
| Front brake pads & rotors | $493.00 | $566.94 | $628.76 | $640.91 |
| Rear brake pads & rotors | $470.27 | $540.81 | $599.20 | $611.35 |
| Front brake pads | $234.86 | $270.76 | $298.57 | $305.32 |
| Front struts, pair | $841.90 | $968.19 | $1,076.93 | $1,094.48 |
| Rear shocks, pair | $339.28 | $390.18 | $432.96 | $441.06 |
| Front wheel bearing, one side | $420.27 | $483.31 | $534.20 | $546.35 |
| Four-wheel alignment | $119.95 | $119.95 | $137.94 | $149.94 |
| Mount & balance 4 tires, labour only | $100.00 | $110.00 | $125.00 | $125.00 |
| Alternator | $597.82 | $687.49 | $766.37 | $777.17 |
| Starter | $502.50 | $578.55 | $643.80 | $653.25 |
| Water pump | $507.27 | $583.36 | $641.90 | $659.45 |
| Radiator | $609.55 | $700.98 | $777.57 | $792.42 |
| Spark plugs (4 / 6 / 8 / 8 cyl.) | $222.28 | $474.54 | $442.96 | $469.96 |

Car: Camry, Civic, Outback, RAV4, Equinox. SUV: Explorer, Highlander, Odyssey, Grand Cherokee. Truck: F-150, Silverado, Tacoma, Tahoe. Van: Transit, ProMaster, Express, Sprinter.
Company-rate accounts (Nickajack Delivery, Millsaps Heating & Plumbing): price from the shop system, not from this sheet.
Printed {{@price_rise|date}}. Throw away any sheet with an earlier date.

---

## 2. `team/staff-handbook.docx`

*Word document, about nine pages, with real Word heading styles (Heading 1 for the title, Heading 2 for each numbered section) so that the extractor returns the section with every paragraph. First written by Ray Brennan; revised by Claire Brennan.*

# Brennan Auto Care · Staff handbook

Revised {{@golive+2w|date}}. This replaces every earlier handbook. A paper copy is in the binder in each break room.

## 1. Welcome

My father told his first hire two things: fix it right, and tell the customer the truth even when it costs you the job. That is still the whole handbook. The rest is detail. Ray Brennan and Claire Brennan

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

*Excel workbook, one sheet named "Fluids", header row frozen, kept by Marcus Gaines. The engine stores it and finds it by name; `kb_read` answers that its text cannot be extracted. It holds the thirteen rows of the PDF and two more, added after the PDF was printed. Drafting note, not part of the file: every quantity and specification in this table was written from memory and has not been checked against the makers' data; each row needs a specialist's read before seed v1 is fixed. The shop's own habit of billing the Camry at 5 quarts matches the catalogue.*

| Vehicle | Engine | Oil | Quarts with filter | Coolant | Transmission fluid | Seen in |
|---|---|---|---|---|---|---|
| Ford Transit-250 Cargo Van | 3.7L V6 | 5W-20 | 6.0 | Orange (Motorcraft) | Mercon LV | Nickajack, Millsaps, Cumberland Bend, Sourwood |
| Ford Transit Connect | 2.5L 4-cyl | 5W-20 | 5.7 | Orange (Motorcraft) | Mercon LV | Nickajack, Moccasin Bend, Sourwood |
| Ram ProMaster 2500 | 3.6L V6 | 5W-20 | 6.0 | Purple (Mopar OAT) | ATF+4 | Nickajack, Sourwood, Cumberland Bend |
| Mercedes Sprinter 2500 | 3.0L V6 diesel | 5W-30, MB 229.52 only | 13.0 | Blue (MB) | Not serviced by us | Nickajack ND-34, ND-35 |
| Chevrolet Express 2500 | 6.0L V8 | 5W-30 dexos | 6.0 | Orange (Dex-Cool) | Dexron VI | Millsaps, Cumberland Bend, Moccasin Bend MB-8 |
| Ford F-250 Super Duty | 6.2L V8 gas | 5W-20 | 7.0 | Orange (Motorcraft) | Mercon LV | Millsaps M-121 to M-123 |
| Ford F-150 | 5.0L V8 (2017) | 5W-20 | 7.7 | Orange (Motorcraft) | Mercon LV | Cumberland Bend E-8 |
| Chevrolet Silverado 2500HD | 6.0L V8 | 5W-30 dexos | 6.0 | Orange (Dex-Cool) | Dexron VI | Cumberland Bend E-11 |
| Toyota Corolla | 1.8L 4-cyl | 0W-20 | 4.4 | Pink (Toyota SLLC) | CVT: Toyota CVT FE only | Missionary Ridge, Moccasin Bend MB-9 |
| Honda Civic | 2.0L 4-cyl | 0W-20 | 4.4 | Blue (Honda Type 2) | CVT: Honda HCF-2 only | Missionary Ridge Car 6 |
| Toyota Camry | 2.5L 4-cyl | 0W-20 | 4.6 (bill 5) | Pink (Toyota SLLC) | Toyota WS | retail, the most common car we see |
| Honda CR-V | 2.4L 4-cyl (2012-2014) | 0W-20 | 4.4 | Blue (Honda Type 2) | Honda DW-1 | retail |
| Subaru Outback | 2.5L (to 2012, timing belt engine) | 5W-30 | 4.4 | Blue (Subaru Super) | Subaru ATF-HP | retail |
| Hyundai Elantra | 2.0L 4-cyl | 0W-20 | to be filled in | to be filled in | to be filled in | Missionary Ridge Car 3, Car 4 |
| Nissan Sentra | 2.0L 4-cyl | 0W-20 | to be filled in | to be filled in | CVT: Nissan NS-3 only | Missionary Ridge Car 5, Car 8 |

Cell A18: "Updated {{T-2mo|date}} MG. Elantra and Sentra to finish."

---

## 4. `parts/fleet-fluid-sheet.pdf`

*One landscape page, a text PDF printed from the spreadsheet on {{T-6mo|date}} and pinned up in the lube bays. It has the first thirteen rows and not the last two.*

**Fleet fluid sheet · Brennan Auto Care parts** · printed {{T-6mo|date}} · MG

| Vehicle | Engine | Oil | Quarts with filter | Coolant | Transmission fluid | Seen in |
|---|---|---|---|---|---|---|
| Ford Transit-250 Cargo Van | 3.7L V6 | 5W-20 | 6.0 | Orange (Motorcraft) | Mercon LV | Nickajack, Millsaps, Cumberland Bend, Sourwood |
| Ford Transit Connect | 2.5L 4-cyl | 5W-20 | 5.7 | Orange (Motorcraft) | Mercon LV | Nickajack, Moccasin Bend, Sourwood |
| Ram ProMaster 2500 | 3.6L V6 | 5W-20 | 6.0 | Purple (Mopar OAT) | ATF+4 | Nickajack, Sourwood, Cumberland Bend |
| Mercedes Sprinter 2500 | 3.0L V6 diesel | 5W-30, MB 229.52 only | 13.0 | Blue (MB) | Not serviced by us | Nickajack ND-34, ND-35 |
| Chevrolet Express 2500 | 6.0L V8 | 5W-30 dexos | 6.0 | Orange (Dex-Cool) | Dexron VI | Millsaps, Cumberland Bend, Moccasin Bend MB-8 |
| Ford F-250 Super Duty | 6.2L V8 gas | 5W-20 | 7.0 | Orange (Motorcraft) | Mercon LV | Millsaps M-121 to M-123 |
| Ford F-150 | 5.0L V8 (2017) | 5W-20 | 7.7 | Orange (Motorcraft) | Mercon LV | Cumberland Bend E-8 |
| Chevrolet Silverado 2500HD | 6.0L V8 | 5W-30 dexos | 6.0 | Orange (Dex-Cool) | Dexron VI | Cumberland Bend E-11 |
| Toyota Corolla | 1.8L 4-cyl | 0W-20 | 4.4 | Pink (Toyota SLLC) | CVT: Toyota CVT FE only | Missionary Ridge, Moccasin Bend MB-9 |
| Honda Civic | 2.0L 4-cyl | 0W-20 | 4.4 | Blue (Honda Type 2) | CVT: Honda HCF-2 only | Missionary Ridge Car 6 |
| Toyota Camry | 2.5L 4-cyl | 0W-20 | 4.6 (bill 5) | Pink (Toyota SLLC) | Toyota WS | retail, the most common car we see |
| Honda CR-V | 2.4L 4-cyl (2012-2014) | 0W-20 | 4.4 | Blue (Honda Type 2) | Honda DW-1 | retail |
| Subaru Outback | 2.5L (to 2012, timing belt engine) | 5W-30 | 4.4 | Blue (Subaru Super) | Subaru ATF-HP | retail |

Read the cap before you pour. Bill what went in, rounded up to the half quart. CVT fluid is never ATF.

---

## 5. `team/the-call-in-eight-moves.pptx`

*PowerPoint, ten slides, each with a title (the extractor returns the slide number and its title). Angie Holloway's training deck for new advisors, made {{T-4mo|date}} when the call scorecard came in. Speaker notes are not extracted, so nothing that matters may be only in the notes.*

**Slide 1 · The call, in eight moves**
Angie Holloway, Bonny Oaks. For new advisors.

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
Ask Greg for five of my calls. Write down what I do after I say the price. Then let me listen to five of yours.
