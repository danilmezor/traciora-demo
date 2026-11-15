from kbb import *
import kbb

# ------------------------------------------------------------------ prices
CATS = [(c['key'], c['en']) for c in cat['categories']]
rows_fact = []
def table(ck):
    out = ['| Job | Hours | Labour | Economy | Standard | Premium | Parts in the standard quote |', '|---|---:|---:|---:|---:|---:|---|']
    for k, e in JOBS.items():
        if CATEGORY[k] != ck: continue
        eco, std, pre = (num_total(k, x) for x in ('economy', 'standard', 'premium'))
        labv = e['labour_price']['after_rise']
        rows_fact.append({'catalogue_key': k, 'name': e['name'], 'hours': e['hours'], 'labour': labv, 'labour_pricing': e['labour_pricing'], 'economy': eco, 'standard': std, 'premium': pre})
        name = e['name']
        sp = []
        for p in e['parts']:
            o = {x['tier']: x for x in p['options'] if not x.get('story')}
            op = o.get('standard') or list(o.values())[0]
            q = ('%g' % p['qty']) + ' ' + p['unit']
            sp.append(op['brand'] + ' ' + p['name'][0].lower() + p['name'][1:] + ', ' + q)
        if e['sublet']: sp.append('rebuild by the transmission specialist')
        sp = '; '.join(sp) if sp else 'labour only'
        if e['labour_pricing'] == 'menu': name += ' (menu)'
        if eco == std == pre:
            out.append(f"| {name} | {e['hours']:g} | {kbb._m(labv)} | | {kbb._m(std)} | | {sp} |")
        else:
            out.append(f"| {name} | {e['hours']:g} | {kbb._m(labv)} | {kbb._m(eco)} | {kbb._m(std)} | {kbb._m(pre)} | {sp} |")
    return '\n'.join(out)
body = f"""*Owner: {S(2,'full')} · In force from {D('@price_rise')} · This is the only page a price is quoted from.*

Every figure is before sales tax, for a **car or small crossover**. For a larger SUV, a pickup or a van, see the multipliers on [Labour rates, fees and vehicle classes](labour-rates-and-fees.md) or the printed [counter price sheet](counter-price-sheet.pdf).

How to read a row: *Labour* is the labour charge alone. *Standard* is the whole job with the parts we quote by default. *Economy* and *Premium* are the same job with the cheaper or the better parts, where we offer a choice. A row marked *(menu)* has a fixed price that does not follow the hourly rate and carries no shop supplies. Every other job adds shop supplies: 5 % of its labour, at most $35.00 on one bill.

Posted labour rate: **{rate()} an hour.**
"""
for ck, cn in CATS:
    body += f"\n## {cn}\n\n{table(ck)}\n"
    if ck == 'tyres_alignment':
        body += "\nMount and balance of four new tires includes the tire fees ($19.40 for four). Seasonal tire storage is $80.00 a season for a set of four; we store a handful of sets and do not advertise it.\n"
    if ck == 'transmission_driveline':
        body += f"\nThe rebuild itself is done by {V('V6')} and billed through us: $3,400.00 of the total is their work. Our labour is removing and refitting the transmission.\n"
    if ck == 'brakes':
        body += "\nPads, shoes and rotors are priced per axle. A caliper is priced per side.\n"
    if ck == 'battery_electrical':
        body += "\nThe battery test is free. Say so.\n"
body += f"""
## Not on this list

If a job is not here, there is no price for it yet. The ones we get asked about most that are still not priced: key and remote programming, wheel-lock removal when the key is lost, headlight lens restoration, trailer wiring, and anything on a diesel beyond fluids and filters. Do not guess and do not borrow a price from a similar job. Ask your lead advisor, who prices it from the labour guide at the posted rate and tells me so I can add it.
"""
USED['prices'] = [{'rule': 'one row per catalogue job, vehicle class car, after the rise, all three tiers; generated from catalogue.json', 'rows': rows_fact}] + USED['prices']
page('prices/price-list.md', 'Price list', 'W', 2,
 'The current price of every catalogue job; the single page a price is quoted from. Long: over the read limit, so it is read by section.',
 body, serves=['S8', 'S12', 'S7', 'challenge:fact-in-table', 'challenge:combine-policy-and-price', 'challenge:long-page-by-section', 'challenge:kb-does-not-say'],
 facts=['All 70 catalogue jobs in ten sections named after the catalogue categories; columns Job, Hours, Labour, Economy, Standard, Premium, Parts in the standard quote (brand, part, quantity from the standard tier of the catalogue).',
        'Class car only; other classes by multiplier or the PDF price sheet.',
        'Menu-priced rows are marked (menu) and carry no shop supplies; hourly rows add 5 % of labour, cap 35 USD per bill.',
        'Timing belt (Replace timing belt, tensioner, idlers & water pump) standard total is 720.00: the figure the stale service page gets wrong.',
        'Tyre fees 19.40 for four; tyre storage 80.00 a season; rebuild sublet price 3,400.00 by vendor V6.',
        'A job that is not on the list has no price: ask the lead advisor named unpriced jobs: key and remote programming, wheel-lock removal, headlight lens restoration, trailer wiring, diesel work beyond fluids and filters (planted: the honest answer to their price is that the base has none).'],
 new=['A job missing from the list is priced by the lead advisor from the labour guide at the posted rate and reported to slot 2.'],
 rev=[(2, '@price_rise', 'every labour figure and total replaced with the new list (posted hour 125.00 to 135.00, menu labour up 8 %; parts unchanged); message: "New prices from today. Labour hour $135."'),
      (2, '@belt_proposal', 'added the first line "This is the only page a price is quoted from" and the section "Not on this list"; message: "After the timing belt."')],
 ru=['Generate the same table from catalogue ru (after_rise). Columns: Работа, н/ч, Работа руб., Эконом, Стандарт, Премиум. The Russian list has several rises a year (R11): the page text may carry the date of the latest one only.'])

page('prices/labour-rates-and-fees.md', 'Labour rates, fees and vehicle classes', 'J', 2,
 'The posted and company-account hour, shop supplies, tax, tire fees, and how a price is scaled for bigger vehicles.',
 f"""*Owner: {S(2,'full')} · In force from {D('@price_rise')}*

## Labour

| Rate | Per hour | Who pays it |
|---|---:|---|
| Posted rate | {rate()} | Everyone, unless the next line applies |
| Company-account rate | {rate('company_account')} | {A('A1')} and {A('A2')} only |

The posted rate was {rate('standard','before_rise')} until {D('@price_rise')}. Menu prices went up by the same 8 % that day. Parts did not change with the rate; they follow what we pay for them.

## Added to a bill

| Charge | Amount | On what |
|---|---|---|
| Shop supplies | 5 % of labour, at most $35.00 a bill | Hourly-priced jobs only. Menu jobs carry none |
| Tennessee sales tax | 9.25 % at East Main and Bonny Oaks; 9.75 % at Charlotte Pike | Parts, labour, fees and shop supplies |
| Tire disposal | $3.50 a tire | New tires |
| State tire fee | $1.35 a tire | New tires |

## Bigger vehicles

The price list is for a car. For the rest, multiply:

| Class | Examples | Labour on heavy jobs | Parts |
|---|---|---:|---:|
| Car | Camry, Civic, Outback, RAV4, Equinox | × 1 | × 1 |
| SUV | Explorer, Highlander, Odyssey, Grand Cherokee | × 1.15 | × 1.15 |
| Truck | F-150, Silverado, Tacoma, Tahoe | × 1.25 | × 1.3 |
| Van | Transit, ProMaster, Express, Sprinter | × 1.3 | × 1.3 |

"Heavy jobs" are brakes, struts and shocks, control arms, ball joints, wheel bearings, steering racks, A/C compressor and condenser, alternator, starter, water pump, thermostat, radiator, engine mounts, fuel pump, clutch, CV axles and transmission removal. Diagnosis and inspections cost the same on any class. On fluid and filter jobs the labour is the same, and the fluid and the filters take the parts multiplier.

Four jobs have their own labour multiplier:

| Job | SUV | Truck | Van |
|---|---:|---:|---:|
| Spark plugs (V6 and V8 take longer) | × 2.4 | × 1.6 | × 1.8 |
| Timing belt | × 1.5 | × 1.4 | not offered |
| Valve cover gasket | × 2 | × 1.4 | × 1.5 |
| Four-wheel alignment | × 1 | × 1.15 | × 1.25 |
| Mount and balance, seasonal changeover | × 1.1 | × 1.25 | × 1.25 |

Worked example: front pads and rotors on an F-150. Labour {lab('front_pads_rotors')} × 1.25 = {lab('front_pads_rotors', cls='truck')}. Standard parts {parts_total('front_pads_rotors')}, each part × 1.3 to the cent: {kbb._m(num_total('front_pads_rotors', 'standard', MODE, 'truck') - kbb.labour('front_pads_rotors', MODE, 'truck'))}. Total {t('front_pads_rotors', cls='truck')} before supplies and tax.
""",
 serves=['S12', 'S1', 'challenge:fact-in-table', 'challenge:combine-policy-and-price'],
 facts=['Posted hour 135.00 from {{@price_rise}}; 125.00 before. Company-account hour 121.50, held by accounts A1 and A2 only (catalogue company_account_terms).',
        'Menu prices rose 8 % the same day; parts did not move.',
        'Shop supplies 5 % of hourly labour, cap 35.00; sales tax on parts, labour, fees, supplies: 9.25 % in Chattanooga (East Main, Bonny Oaks), 9.75 % at Charlotte Pike in Nashville (ledger tax.rate.main, .east, .west).',
        'Tyre disposal 3.50 and Tennessee pre-disposal fee 1.35 per tyre (catalogue fee on new_tyres_fitted: 19.40 for four).',
        'Class multipliers: hours 1 / 1.15 / 1.25 / 1.3 on heavy jobs, parts 1 / 1.15 / 1.3 / 1.3 (catalogue.md and configurations.en.parts_class_multiplier). Fluid and filter jobs keep the car\'s labour and scale their parts (catalogue parts_scale_with_class), so a fluid job costs more on a truck (calls/en/28); diagnosis and inspections are flat.',
        'Own multipliers: spark_plugs 2.4/1.6/1.8; timing_belt_kit 1.5/1.4/not offered for vans; valve_cover_gasket 2.0/1.4/1.5; wheel_alignment 1.0/1.15/1.25; new_tyres_fitted and seasonal_tyre_change 1.1/1.25/1.25.',
        'The table titled "Four jobs" lists five rows: a deliberate small slip a careful reader notices.',
        'Worked example: F-150 front pads and rotors, standard: 243.00 x 1.25 = 303.75 labour; 250.00 with each part x 1.3 to the cent = 325.01 parts; 628.76.'],
 new=['The list of "heavy jobs" in words (derived from the jobs that carry hours_by_class in the catalogue).'],
 rev=[(2, '@price_rise', 'posted rate 125.00 to 135.00, company rate 112.50 to 121.50; message: "New prices from today. Labour hour $135."')],
 ru=['Russian rates 1 900 (posted) and 1 700 (contract) RUB from the rise; 1 760 and 1 580 before. Class multipliers differ: hours 1 / 1.15 / 1.3 / 1.3, parts 1 / 1.35 / 1.7 / 1.3. No sales tax; VAT 5 % inside every price. No tyre fees. Shop supplies 3 %, cap 500 RUB.'])

page('prices/how-prices-change.md', 'How prices change', 'J', 2,
 'The rule written after S8: who changes a price, which page changes first, and what happens to service pages and open estimates.',
 f"""*{S(2,'full')} · {D('@belt_proposal')}*

I set the labour rate and the menu prices. {S(9)} sets parts prices from cost, by the matrix. Nobody else changes a price.

When a price changes:

1. The [price list](price-list.md) and the [rates page](labour-rates-and-fees.md) change that morning, before we open.
2. The public [prices page](../customers/prices-for-common-services.md) changes the same morning.
3. Every service page that shows a dollar figure is checked within five working days by whoever keeps it. {S(5)} keeps the East Main service pages, {S(16)} the brake and suspension pages.
4. A written estimate we already gave is honoured at its price for its 30 days.

Step 3 is the one we missed. After the rise on {D('@price_rise')} the timing belt page kept the old labour rate, an advisor quoted from it, and it cost us a discount and an unhappy customer. If you find another page like it, do not work around it: propose the fix the same day. The correction to the timing belt page has been proposed and is {S(4)}'s to decide.

## The record

| Date | What changed |
|---|---|
| {D('@price_rise')} | Posted labour rate $125.00 to $135.00. Company-account rate $112.50 to $121.50. Menu prices up 8 %. Parts unchanged |
""",
 serves=['S12', 'S8', 'operate:find-what-changed', 'operate:contradiction'],
 facts=['Slot 2 sets labour and menu prices; slot 9 sets parts prices from cost by the matrix.',
        'Order of change: price list and rates page the same morning; public prices page the same morning; service pages within five working days; open written estimates honoured for 30 days.',
        'Service-page keepers: slot 5 (East Main service pages), slot 16 (brake and suspension pages).',
        'The page admits the timing belt page was missed and says its correction is proposed and is slot 4\'s to decide (why slot 2, who can also decide, has not). It does not know about the brake questions page, which is still stale: the second stale page is for the agent to find.',
        'The record table has one row: the rise at {{@price_rise}}. Inside the table the placeholder bar is escaped (grammar rule).'],
 new=['Five working days to review service pages after a price change.'],
 created=(2, '@belt_proposal'),
 ru=['Russian shop: several rises a year (R11), so the record table has more rows; the Russian writer takes them from the Russian ledger once it lists them, and until then writes the latest one only.'])

# ------------------------------------------------------------------ policies
page('policies/README.md', 'Policies', 'J', 2,
 'Index of the policy pages.',
 f"""What we have decided, written down so it is the same at all three shops. If a policy and a habit disagree, the policy wins. If the policy is wrong, tell me.

| Page | In one line |
|---|---|
| [Discount policy](discounts.md) | Over 10 % needs the shop manager, on the order |
| [Warranty](warranty.md) | 24 months or 24,000 miles |
| [Estimates and approvals](estimates-and-approvals.md) | In writing, per job, never over |
| [Diagnostic and inspection fees](diagnostic-fees.md) | Charged, not credited |
| [Customer-supplied parts](customer-supplied-parts.md) | Fitted, not warrantied |
| [Deposits](deposits.md) | Before special orders and rebuilds |
| [Cancellations and no-shows](cancellations-and-no-shows.md) | No fee; two strikes |
| [Cars not collected](storage-of-uncollected-cars.md) | Five free days |
| [Complaints](complaints.md) | Heard the same day, answered within one |
| [Voids and refunds](voids-and-refunds.md) | A paid order is never voided at the counter |
| [Customer records](customer-records.md) | One customer, one record, a real name |
| [Service standards](service-standards.md) | How fast we answer, call back and estimate |

{S(2,'full')}
""",
 serves=['operate:overview', 'challenge:near-duplicate'],
 facts=['Twelve policy pages listed, each with a one-line summary.',
        'The old page customers/warranty-policy.md is in no index: it is found only by search or by the folder listing.',
        'Policy beats habit.'],
 ru=['Same index.'])

page('policies/discounts.md', 'Discount policy', 'J', 2,
 'The discount rule created after story S2.',
 f"""*{S(2,'full')} · In force from {D('@discount_rule')} · Last changed {D('@belt_proposal')}*

## The rule

- **Up to 10 % of the bill:** an advisor may give it. Write the reason on the order.
- **More than 10 %:** the shop manager approves it **before** the bill is closed, and the order shows who approved. That is {S(4)} for East Main and Bonny Oaks and {S(22)} for Charlotte Pike. If he is out, call me. A lead advisor cannot approve it.
- The 10 % is measured on the bill **before sales tax**, labour and parts together.
- Anything that makes the bill smaller is a discount: money off a line, hours cut "to help", a part given away, a fee left off.

## What is not allowed at any percentage

- **A discount for cash.** There is none. If a customer says somebody here used to give one, the answer is that the price is the price.
- Rounding a bill down to end a conversation.
- A discount with no reason written.

## What is not a discount

- The company-account rate that {A('A1')} and {A('A2')} pay. That is a price class.
- A warranty repair. That is a warranty order with no charge, tied to the first order.
- Goodwill: when we got something wrong and make it right. Goodwill over 10 % follows the same rule as any discount: the shop manager, on the order.

## How I check

Every Friday I get a list of every bill with more than 10 % off and who approved it. A line on that list with no approver is a conversation with me on Monday.

This rule exists because of what was found at Charlotte Pike. It applies to everybody.
""",
 serves=['S2', 'S8', 'challenge:policy-vs-team-note', 'operate:find-what-changed', 'challenge:combine-policy-and-price'],
 facts=['In force from {{@discount_rule}} (T-5 months), created by slot 2 (design S2).',
        'Up to and including 10 %: the advisor, with a written reason. Over 10 %: the shop manager before the bill is closed, recorded on the order (ERP repair_order: who approved a discount).',
        'Approvers: slot 4 for main and east, slot 22 for west; slot 2 as fallback; lead advisors cannot approve.',
        'The 10 % is measured on the bill before sales tax (design 7.2 S8).',
        'No cash discount; no rounding down; no discount without a reason.',
        'Company-account price class, warranty orders and goodwill are defined; goodwill over 10 % needs the same approval.',
        'Slot 2\'s Friday report "Discounts over 10 %" (design S10) is the check.',
        'S8: 80 USD off a bill of 741.60 before tax is 10.8 %, approved by slot 4 and recorded: inside the rule. Slot 23 gave 12 % twice last month with no approver: outside it.',
        'The team note "discounts above 10 % need the shop manager\'s approval" (S2) agrees with this page.'],
 new=['The advisor\'s own limit is "up to 10 % with a written reason"; lead advisors cannot approve over 10 %; slot 2 is the fallback approver. Reason: the design gives only the 10 % line.',
      'Definition of what counts as a discount (hours cut, a part given away, a fee left off).'],
 created=(2, '@discount_rule'),
 rev=[(4, '@belt_proposal', 'added the line "The 10 % is measured on the bill before sales tax" after the timing-belt discount (stories/S02: revisions as slot 2, then slot 4); message: "Before tax. It came up on the timing belt bill."')],
 ru=['Same rule and percentages. The Russian leak looks different (R11: work done past the order, parts written off with no sale), so the list "what is not allowed" adds: work without an order, a part issued without an order line. Approvers: slots 4 and 22.'])

page('policies/warranty.md', 'Warranty', 'J', 2,
 'The current warranty in full, for staff: terms, exclusions, who decides, how a claim is written up.',
 f"""*{S(2,'full')} · In force from {D('@warranty_2424')} · Last reviewed {D('T-4mo')}*

## Terms

**24 months or 24,000 miles, whichever comes first, parts and labour**, on repairs done with parts we supplied. It runs from the date and mileage on the invoice. Any of our three shops honours a repair done at any other.

| Case | Cover |
|---|---|
| Repairs with our parts, private vehicle | 24 months / 24,000 miles |
| Vehicle in business use (any company account, any van or truck used for work) | 12 months / 12,000 miles |
| Brake pads and shoes | 12 months / 12,000 miles against defects and noise. Wear is not a defect |
| Wiper blades, bulbs | 90 days |
| Batteries | The maker's free-replacement period on the label |
| Tires | The maker's warranty; we file the claim |
| Sublet work (transmission rebuild, glass) | The subcontractor's warranty, in writing, handed over with the invoice |
| Used parts the customer asked for | 90 days, part only |
| Customer-supplied parts | None, on the part or the labour |
| Diagnosis | If our diagnosis was wrong, the customer does not pay for the part that did not fix it |

## Not covered

Accident damage. Overheating or running low on oil after the repair. Racing, off-road. Another shop's work on the same repair. Towing and rental cars, unless {S(4)} or {S(22)} decides otherwise as goodwill.

## More than 25 miles away

The customer calls us first. We arrange the repair or pay another shop, up to the price of the original repair. Without the call first we may still help, and it is {S(4)}'s decision.

## Writing it up

1. New order, type **warranty**, tied to the original order. Never reopen the old one.
2. The foreman looks at the car first: [When a car comes back](../shop-floor/when-a-car-comes-back.md).
3. Covered: no charge, and say so plainly. Not covered: explain why, with the invoice in your hand, and give an estimate like any other job.
4. Unsure whether it is covered: do not decide at the counter. {S(4)} for Chattanooga, {S(22)} for Nashville, the same day.

The counter script and the hard cases are on [A comeback at the counter](../how-to/a-comeback-at-the-counter.md).

There is an older warranty page still standing among the customer answers. This page and [Our warranty](../customers/warranty.md) are the ones in force.
""",
 serves=['S12', 'S1', 'S6', 'challenge:near-duplicate', 'challenge:fact-in-table', 'challenge:combine-policy-and-price', 'challenge:kb-does-not-say'],
 facts=['Same headline terms as customers/warranty.md, plus the cover table (ten rows).',
        'Business-use vehicles (every company account) 12 months / 12,000 miles: the row that decides account A5\'s brake comebacks (inside 12/12 anyway) and any fleet question.',
        'Used parts at the customer\'s request: 90 days, part only. Wrong diagnosis: the customer does not pay for the part that did not fix the fault.',
        'Sublet warranty length is not stated (planted gap).',
        'Write-up: new order of type warranty tied to the original; the foreman looks first; borderline cases decided by slot 4 or slot 22 the same day.',
        'The last line admits an older page still stands among the customer answers, without naming or removing it.',
        'Readers (ledger s12.pages): the current warranty is public (customers/warranty.md, with this staff page behind it); the old page is public too.'],
 new=['Used parts 90 days part only; the wrong-diagnosis rule. Reason: common trade terms; no story depends on them.'],
 rev=[(2, 'T-4mo', 'added the row for vehicles in business use and the closing line about the older page; message: "Fleet cover spelled out. Old page still to be removed."')],
 ru=['Write the Russian terms: 30 days on mechanical and electrical work (ledger); spare parts by the supplier\'s warranty; customer parts: work only. The comeback window in the ERP matches 30 days (R11). There is no business-use tier in the Russian trade.'])

page('customers/warranty-policy.md', 'Warranty policy', 'W', 1,
 'The old warranty page nobody removed: 12/12. Stale on purpose (S12).',
 f"""*Effective {D('T-6y')} · Reviewed {D('T-38mo')}*

All repair work performed by Brennan Auto Care is guaranteed for **12 months or 12,000 miles**, whichever comes first, parts and labor.

- Electrical parts (starters, alternators, sensors, switches): 90 days.
- Batteries: per the manufacturer's label.
- Brake pads: guaranteed against defects for 12 months. Normal wear excepted.
- Used parts installed at the customer's request are not guaranteed.

Warranty work is performed at the shop that did the original repair. Please bring your invoice.

The warranty does not cover damage caused by accident, abuse, neglect, or continued driving after a failure. Towing is not included.

If a customer is unhappy with a warranty decision, send them to me.

{S(1,'full')}
""",
 serves=['S12', 'challenge:near-duplicate', 'operate:contradiction'],
 facts=['STALE ON PURPOSE. States 12 months / 12,000 miles; electrical parts 90 days; warranty only at the shop that did the repair; used parts not guaranteed; complaints to the founder.',
        'It contradicts customers/warranty.md and policies/warranty.md on four points: the term (12/12 against 24/24), electrical parts (90 days against the full term), where it is honoured (the original shop against all three), used parts (none against 90 days).',
        'Its own dates give it away: effective {{T-6y}}, reviewed {{T-38mo}}, both before the current page came into force at {{@warranty_2424}} (T-26 months).',
        'Signed by slot 1; American spelling "labor" as the founder writes.',
        'Not linked from any page; found by search ("warranty") and in the folder listing of customers/ beside warranty.md ("Our warranty"). It is public (ledger s12.pages): the website assistant can read it.'],
 stale='S12: the old warranty page beside the current one',
 ru=['The Russian old page: for example 14 days on work and "по месту ремонта" against the current 30 days at any of the three shops; signed by slot 1.'])
