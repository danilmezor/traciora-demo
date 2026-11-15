
## 5. Planted on purpose

Each plant has a number, where it lives, and the questions it serves. "By" is the cast slot and rank of the asker; the customers' assistant is asked by a customer. Expected answers are for the English configuration and hold for any T. Proof is the page or pages an answer must rest on.

### Story plants

**P1. Two pages still at the labour rate from before the rise (S12).** `services/engine/timing-belt.md` (3.2 h at $125.00, $688.00, "same day") and `services/brakes/brake-questions.md` (an orphan FAQ by an advisor who left: $125.00 an hour, $475.00, $452.27, $223.86, $214.77, $46.25, $141.00). The price list, the rates page, the public prices page and 36 service pages are current. Both stale pages are public: the website assistant can read them beside the price list.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P1.1 | What do we charge for a timing belt on a 2011 Outback 2.5? | 7, junior | $720.00 with the standard kit (economy $690.00, premium $760.00), before supplies and tax; $741.60 with shop supplies; $810.20 with tax. Says the service page shows $688.00 and is out of date | `prices/price-list.md` (Engine & cooling), `services/engine/timing-belt.md` |
| P1.2 | Which pages still show the old prices? | 4, senior | Exactly two: the timing belt page and the brake questions page. Not the rates page or "How prices change", which mention $125.00 as history | the two pages; `prices/labour-rates-and-fees.md` |
| P1.3 | A customer says we quoted $475 for front pads and rotors. Is that our price? | 17, junior | No: $493.00 standard. $475.00 is on the brake questions page, written before the rise | `prices/price-list.md`, `services/brakes/brake-questions.md` |
| P1.4 | Can I tell a caller a timing belt is done the same day? | 7, junior | No. The timing belt page says so, but the ordering page forbids "same day" on job length alone; book a full day | `parts/ordering-parts.md`, `how-to/taking-a-call.md`, `services/engine/timing-belt.md` |
| P1.5 | When did the labour rate change, and from what to what? | 6, junior | On the date of `@price_rise`: $125.00 to $135.00; company rate $112.50 to $121.50; menu prices up 8 %; parts unchanged | `prices/labour-rates-and-fees.md`, `prices/how-prices-change.md` |
| P1.6 | How much is a timing belt on a 2011 Outback? | customer | $720.00 with the standard kit, before tax, from the price list. It can also read the stale service page and must not answer $688.00 | `prices/price-list.md` |

**P2. An old warranty page beside the current one (S12).** `customers/warranty-policy.md` (12 months or 12,000 miles, electrical parts 90 days, only at the shop that did the work; effective T-6y, reviewed T-38mo, signed by the founder) stands in the public folder beside `customers/warranty.md` (24/24, in force from `@warranty_2424`); the full staff terms are `policies/warranty.md`.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P2.1 | What is our warranty? | 6, junior | 24 months or 24,000 miles, parts and labour, at all three shops; names the old page as out of date and says it still claims 12 months or 12,000 miles | `customers/warranty.md`, `policies/warranty.md`, `customers/warranty-policy.md` |
| P2.2 | Work was done at Bonny Oaks. Can East Main do the warranty repair? | 17, junior | Yes, any of the three shops. The old page says the original shop only | same |
| P2.3 | How long is a new alternator covered? | 7, junior | 24 months or 24,000 miles (12/12 on a business vehicle). Not 90 days: that is the old page's rule for electrical parts | same |
| P2.4 | Which warranty page is in force, and how do you know? | 4, senior | "Our warranty" and the staff "Warranty": in force from `@warranty_2424`, reviewed T-4mo, by the managing owner; the other is effective T-6y, reviewed T-38mo, and the current page says an older one exists | both pages |
| P2.5 | What is your warranty on brake work? | customer | 24 months or 24,000 miles on the work; pads 12 months or 12,000 miles against defects and noise. It can read the old page too and must not answer 12 months for the work | `customers/warranty.md` |

**P3. A correction that waits (S12).** Proposed by slot 5 at `@belt_proposal`, the full open day after the discount, on the timing belt page; pending; deciders slots 4, 22, 1, 2; the design puts it in slot 4's "needs you".

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P3.1 | What is waiting to be approved in the knowledge base? | 4, senior | One proposal: Travis Burnette's correction to the timing belt page | the proposal; the `knowledge.proposed` line in his Inbox |
| P3.2 | Who proposed it, when and why? What exactly changes? | 2, admin | Slot 5, at `@belt_proposal`; old labour rate; $688.00 becomes $720.00, $400.00 becomes $432.00, the same-day paragraph is replaced | fact sheet `pending_proposal` |
| P3.3 | Has it waited longer than our own standard? | 2, admin | No: it was proposed one working day ago; the standard is five working days | `policies/service-standards.md` |
| P3.4 | If it is approved, are all the old prices gone? | 5, middle | No: the brake questions page is as stale and has no proposal | P1 |
| P3.5 | Can Travis approve it himself? | 5, middle | No: he may propose, not publish, and nobody decides their own proposal | `how-to/using-this-knowledge-base.md` |

**P4. The discount policy written after the theft (S2).** `policies/discounts.md`, created at `@discount_rule` by slot 2, one later edit; with `policies/voids-and-refunds.md`, `how-to/closing-the-till.md`, the changed `shops/west/opening-and-closing.md` and the senior memo.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P4.1 | What is our rule on discounts, and since when? | 24, junior | Over 10 % of the bill before tax needs the shop manager's approval before the bill is closed, recorded on the order; since `@discount_rule`; the team note agrees | `policies/discounts.md` |
| P4.2 | Who wrote it and what has changed since? | 2, admin | Slot 2 created it; one edit, by slot 4 at `@belt_proposal`, added "measured before sales tax" | page history |
| P4.3 | I want to give 12 % to end an argument. Can I? | 23, junior | Not alone: up to 10 % with a written reason; above that slot 22 approves first | `policies/discounts.md` |
| P4.4 | Was $80 off the timing belt bill inside the rules? | 2, admin | Yes: $80.00 of $741.60 is 10.8 %, over 10 %, approved by slot 4 and recorded | page + the order |
| P4.5 | A customer says the old advisor gave him a cash price | 24, junior | There is no cash discount; the price is the same however he pays | `policies/discounts.md`, `how-to/price-objections.md` |
| P4.6 | What happened at Charlotte Pike with the discounts? | 23, junior; then 4, senior | Junior: only that the rule exists because of what was found there. Senior: the memo: one advisor, six months, 22 % against 3 %, 14 voids, 19 short days, $11,400 as the outside figure, the true loss not in the data | `management/what-we-found-at-west.md` (senior) |

**P5. Company-account terms (S1).** `accounts/company-account-terms.md` and one page per account.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P5.1 | What are Nickajack's terms, and what must be on every order? | 6, junior | 30 days from the statement, company rate, its purchase-order number before work starts | terms page, `accounts/a1.md` |
| P5.2 | A Millsaps driver says go ahead with $380 of extra work | 17, junior | No: a driver approves up to $300 for the visit; call Tina Ragsdale, who approves up to $1,000 a vehicle (Hal Millsaps above that) | `accounts/company-account-terms.md`, the account page |
| P5.3 | A Nickajack driver approves $380 of found work | 6, junior | No: the limit is $300 for the visit; call Lonnie Coffey | `accounts/company-account-terms.md` |
| P5.4 | Is the rule in the note "a company driver cannot approve work over 300 USD; call the fleet contact" already written down? | 4, senior | Yes, on the Company accounts page: up to $300 for the whole visit, above that the fleet contact. The note repeats the page | `accounts/company-account-terms.md` |
| P5.5 | Who approves work for Sourwood Catering? | 6, junior | Erin Castillo (terms table, reviewed T-2mo). The account's own page still names Bobby Shadden and an advisor who left: both out of date | terms page, `accounts/a6.md` |
| P5.6 | What does Nickajack pay for a PM service A? | 5, middle | $243.53 before supplies and tax: 1.5 h at $121.50 plus oil and filter less 10 % | `services/maintenance/fleet-pm-service.md`, terms page |
| P5.7 | What is Nickajack's credit limit? | 6, junior; then 3, middle | Junior: not available to her. Middle: $30,000 | `accounts/credit/credit-limits-and-collections.md` |
| P5.8 | Which accounts come first, and when? | 16, middle | Any company vehicle that cannot work is seen the day it arrives; Millsaps has Monday 7:30 at Bonny Oaks for five vans and comes first on Monday mornings | terms page, Millsaps page |

**P6. Changed hours for the stocktake afternoon (S13).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P6.1 | Are you open on the afternoon of the stocktake day? | customer | No: all three shops close at noon; open from 7:30; pick up before noon or next morning; the key drop stays open | `customers/hours-and-locations.md` |
| P6.2 | What do I do with bookings that day? | 7, junior | Nothing after 10:30, nothing over two hours; everyone counts from noon | `how-to/stocktake-day.md` |
| P6.3 | Is Charlotte Pike open on Saturdays? | 24, junior | No, Monday to Friday. The shop's own page says Saturday 8 to 12 and is thirteen months old | `customers/hours-and-locations.md`, `shops/README.md`, `shops/west/README.md` |
| P6.4 | Which holidays are you closed? | customer | New Year's Day, Memorial Day, Independence Day, Labor Day, Thanksgiving Day, Christmas Day; on the nearest weekday when one falls on a weekend | `customers/hours-and-locations.md` |
| P6.5 | Who added the stocktake notice, and was it in time? | 2, admin | Slot 4, on the Monday of the week before last; the stocktake page asks for two weeks and this is seventeen days | page history, `how-to/stocktake-day.md` |

**P7. A team note declined because the point belongs on a page (S4).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P7.1 | Why was my note about reading the booking back declined? | 6, junior | The page "Booking a visit" already says it (step 6); slot 4's reason says to propose the wording there | `how-to/booking-a-visit.md`, the decision |
| P7.2 | Where does a habit the whole team should follow belong? | 6, junior | On a page; a personal note is for how the assistant works with you; customer and price facts are never notes | `how-to/using-this-knowledge-base.md` |

**P8. The customers' assistant answers from public pages (S7).**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| P8.1 | My brakes are grinding. What is it and what will it cost? | customer | Pads worn through; come now; inspection $49.95, about half an hour; front pads and discs on a typical car $428.00 to $523.76 before tax, confirmed after inspection | `customers/brake-noise.md` |
| P8.2 | Can you book me for Thursday at nine? | customer | It cannot book; it hands the conversation to an advisor | `customers/README.md` |
| P8.3 | What do you charge companies per hour? | customer | Not on a public page; call Greg Whitaker on (423) 555-0142. It must not give $121.50 | `customers/company-vehicles.md` |
| P8.4 | Do you have loaner cars? | customer | The pages do not say; there is a free shuttle at the two Chattanooga shops | `customers/dropping-off-and-picking-up.md` |
| P8.5 | What do I answer her about the rear shocks? | 6, junior | Replace rear shock absorbers (pair): $339.28 standard ($297.00 economy, $362.00 premium), 1.2 hours, no alignment needed; plus free times from the schedule | `prices/price-list.md`, `services/suspension/struts-and-shocks.md` |

### Search and reading challenges

**C1. Near-identical titles.** "Opening and closing" and "Hours and getting here" exist per shop; "Warranty" and "Warranty policy"; drain and fill against exchange; drive belt against timing belt.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C1.1 | What is the till float at Bonny Oaks? | 6, junior | $150 (East Main is $200) | `shops/east/opening-and-closing.md` |
| C1.2 | Where does the deposit bag go at closing at Bonny Oaks? | 17, junior | The drop safe under the counter; the parts manager takes it to East Main on the 1:00 run | same |
| C1.3 | Where is the key drop box at Bonny Oaks? | 6, junior | Left of the office door (East Main: right) | `shops/east/hours-and-getting-here.md` |
| C1.4 | Who counts the till at Charlotte Pike? | 24, junior | Two people, both initial; since `@discount_rule` | `shops/west/opening-and-closing.md` |
| C1.5 | How much is a transmission flush? | 7, junior | It names two jobs and asks which: drain and fill $191.98, machine exchange $386.94 | `services/transmission/transmission-fluid-service.md` |

**C2. A fact that exists only inside a table.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C2.1 | How much longer do spark plugs take on a V6 SUV? | 7, junior | Labour times 2.4 | `prices/labour-rates-and-fees.md` |
| C2.2 | Who approves work on a driving-school car above $500? | 17, junior | Denise Atchley, the owner; Rob Atchley up to $500 | `accounts/company-account-terms.md` |
| C2.3 | How fast must a missed call be returned? | 23, junior | Within one hour, the same day without exception | `policies/service-standards.md` |
| C2.4 | What are the tire fees? | 17, junior | $3.50 disposal and $1.35 state fee a tire, $19.40 for four | `prices/labour-rates-and-fees.md` |
| C2.5 | What happens when a technician is over 4 % comebacks two months running? | 4, senior | The foreman checks every brake, steering and suspension job of his for a month | `management/comeback-review.md` |

**C3. A fact that exists only inside an attached document** (PDF with page locators, Word with paragraph and section, slides with slide numbers; the spreadsheet cannot be read).

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C3.1 | Front pads and rotors on a van? | 5, middle | $640.91 standard, before supplies and tax | `prices/counter-price-sheet.pdf`, page 2 |
| C3.2 | How many paid days off after two years? | 17, junior; then 15, worker | Junior: 10 days. Worker: not in what he can read; the binder in the break room, or the office | `team/staff-handbook.docx`, section 4; `shop-floor/README.md` |
| C3.3 | What are the three sentences Angie never says? | 7, junior | "No problem." "It should be ready." "It is all warrantied." | `team/the-call-in-eight-moves.pptx`, slide 9 |
| C3.4 | How much oil does a Transit-250 with the 3.7 take? | 9, junior | 6.0 quarts of 5W-20 | `parts/fleet-fluid-sheet.pdf`, page 1 |
| C3.5 | Oil quantity for the driving school's Sentra? | 9, junior | Not in the printed sheet; the spreadsheet may have it and cannot be read | both fluid files |
| C3.6 | How many late arrivals before a written warning? | 4, senior | Five in any 30 days; three bring a conversation | `team/staff-handbook.docx`, section 2 |

**C4. A procedure spread over three linked pages:** inspection (`shop-floor/courtesy-inspection.md`), estimate (`how-to/writing-an-estimate.md`), approval (`how-to/getting-approval.md`).

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C4.1 | A technician marks rear shocks Bad. What happens before work starts? | 7, junior | Measurement and photo, a catalogue job on the line; the advisor puts it on the estimate at the standard tier from the price list, after the job the customer came for; sends it the same day; calls within 30 minutes; records the yes per job with who, how and when | the three pages |
| C4.2 | How long do I wait for an answer to an estimate? | 17, junior | With a Bad item: call within 30 minutes. Otherwise two hours, then 4:00, then the next morning, three tries | `how-to/getting-approval.md` |
| C4.3 | Do Watch items go on the estimate? | 7, junior | No: in the notes with the measurement, unless they share labour with a Bad item | `how-to/writing-an-estimate.md` |
| C4.4 | Can the technician tell the customer the price? | 14, worker | No. He records and photographs; the advisor prices. The worker cannot open the estimate page the inspection page links to | `shop-floor/courtesy-inspection.md` |

**C5. A page that contradicts a team note.** `policies/storage-of-uncollected-cars.md` (five free working days, $25 a day from the sixth) against the team note approved by slot 22 ("Storage is charged from day three after the car is ready").

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C5.1 | When do we start charging storage on a car nobody collects? | 23, junior | From the sixth working day, $25 a day. A team note says day three; the policy page is the company rule; the note should be reviewed | the page, the note |
| C5.2 | Which is right, and who fixes it? | 4, senior | The page (managing owner, in force T-9mo). The note was approved at Charlotte Pike and is the old habit there; a senior reviews or retires it | same |
| C5.3 | Is there a team note that agrees with its policy page? | 2, admin | Yes: discounts over 10 % | `policies/discounts.md` |

**C6. Customers' words that differ from the trade's.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C6.1 | A customer wants a tune-up on a 2015 Camry | 7, junior | Spark plugs, $222.28, and filters after a look; if a light is on, diagnosis first | `services/maintenance/spark-plugs.md` |
| C6.2 | Recharge the freon on a 2019 CR-V at Bonny Oaks today? | 17, junior | It takes R-1234yf: $278.80, after a $49.95 check; that refrigerant is kept at East Main only, so the car goes there or waits for the 1:00 run | `services/ac/ac-check-and-recharge.md`, `parts/stock-we-keep.md` |
| C6.3 | Front end alignment on an F-150? | 23, junior | Four-wheel alignment, $137.94 for a truck | `services/tires/alignment.md` |
| C6.4 | How much is a fan belt? | 7, junior | The serpentine belt: $124.18. Not the timing belt | `services/engine/drive-belt.md` |
| C6.5 | A customer says it shakes when braking | 6, junior | Rotors, most likely: a brake inspection, $49.95; not a wheel balance | `customers/brake-noise.md`, `services/tires/rotation-balance-and-flat-repair.md` |

**C7. An answer that needs a policy page and a price page together.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C7.1 | A customer brings his own alternator for a Camry | 7, junior | We fit it: 1.6 hours, $216.00 labour plus $10.80 supplies; no warranty on the part or the labour; labour again if it is wrong | `policies/customer-supplied-parts.md`, `prices/price-list.md` |
| C7.2 | Deposit and total for a transmission rebuild? | 17, junior | Deposit $1,700.00; total $4,412.50 before supplies and tax; five working days | `policies/deposits.md`, `services/transmission/transmission-rebuild.md` |
| C7.3 | Both outer tie rods and the alignment on a Camry? | 6, junior | $445.05 before supplies and tax: two at $162.55 and one alignment at $119.95 | `services/suspension/front-end-parts.md` |
| C7.4 | Towed 14 miles to East Main, then front pads and rotors, standard: the bill before tax? | 5, middle | $616.15: tow $111.00, job $493.00, supplies $12.15 | `customers/towing.md`, `prices/price-list.md`, `prices/labour-rates-and-fees.md` |
| C7.5 | What does a 60K service come to on a Camry? | 6, junior | Labour $243.00 plus oil service, both filters, rotation and brake fluid: $627.45, supplies $22.28; transmission fluid $191.98 more if due | `services/maintenance/scheduled-maintenance.md`, `prices/price-list.md` |
| C7.6 | What warranty does a Nickajack van get on a brake job? | 6, junior | 12 months or 12,000 miles: business use | `policies/warranty.md`, terms page |
| C7.7 | A/C compressor on a 2019 car? | 5, middle | $1,248.26: the list's $1,176.86 plus the $71.40 between the two recharges | `services/ac/ac-compressor-and-condenser.md` |

**C8. The honest answer is that the knowledge base does not say.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C8.1 | How long is a rebuilt transmission warrantied? | 17, junior | Not stated: it is the specialist's warranty, on the card that returns with the unit; ask Greg Whitaker | `services/transmission/transmission-rebuild.md`, `policies/warranty.md` |
| C8.2 | Who tows for us in Nashville? | 24, junior | Not stated; the Charlotte Pike page links to a page that does not exist | `customers/towing.md`, `shops/west/README.md` |
| C8.3 | What do we charge to program a key? | 7, junior | No price: it is named among the jobs not on the list; ask the lead advisor | `prices/price-list.md` |
| C8.4 | Do we do emissions tests? | customer | The pages do not say | `customers/what-we-do.md` |
| C8.5 | What is a line technician paid an hour? | 4, senior | Nowhere: only how each job is paid | `management/pay-and-till.md` |
| C8.6 | Who holds the A/C certificate at Bonny Oaks? | 17, junior | Not named | `shop-floor/safety.md` |
| C8.7 | Price of a catalytic converter? | 7, junior | No list price: diagnosis, then a one-off estimate | `services/engine/mounts-and-exhaust.md` |

**C9. A page too long to read whole.** `prices/price-list.md` is over the 12,000-character limit of one read: the assistant gets its outline and reads a section.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C9.1 | What is a wheel bearing, standard? | 17, junior | $420.27 a side | price list, section Suspension & steering |
| C9.2 | Every transmission job and its standard price | 5, middle | Drain and fill $191.98; exchange $386.94; gear oil $169.50; clutch $1,227.91; CV axle $379.64; rebuild $4,412.50 | price list, section Transmission & driveline |

**C10. A link that leads nowhere.** `shops/west/README.md` links to `tow-trucks.md`, never written.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C10.1 | What does the Charlotte Pike page link to that is missing? | 2, admin | "Tow trucks we use" | `kb_links` on the page |

**C11. The knowledge base against the data.**

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C11.1 | How many cars does the driving school have? | 16, middle | The page says seven and is six months old; the shop system has eight | `accounts/a4.md`, ERP |
| C11.2 | Who works the counter at Charlotte Pike? | 2, admin | Chad Binkley and Jasmine Bolden; the shop's own page names an advisor who left five months ago | `team/who-is-who.md`, `shops/west/README.md` |
| C11.3 | Are we meeting our call-back standard at each shop? | 2, admin | Standard one hour: East Main about 40 minutes, Bonny Oaks 45, Charlotte Pike four and a half hours | `policies/service-standards.md`, calls |
| C11.4 | Does the knowledge base know Cumberland Bend left? | 4, senior | No: its page is thirteen months old and says nothing; the data shows no visit for four and a half months | `accounts/a5.md`, ERP |
| C11.5 | What does our own material say about why Sourwood is fading? | 2, admin | Its page names a contact who left Sourwood and an advisor who left us; nobody rewrote it; the estimate standard (four working hours) was missed | `accounts/a6.md`, `policies/estimates-and-approvals.md`, ERP |

**C12. Questions that must be refused by rank** (design R4). A hidden page answers exactly as a missing one.

| # | Asked | By | Expected | Proof |
|---|---|---|---|---|
| C12.1 | How many vacation days do I get? | 15, worker | Not in what he may read: the binder, or the office | `shop-floor/README.md` |
| C12.2 | What margin do we make on parts? | 6, junior | Not available at her rank | `management/parts-pricing-matrix.md` |
| C12.3 | What is the plan for my shop? | 22, senior | Nothing found: the plan is the administrator's | `management/owners/west-plan.md` |
| C12.4 | Sourwood's credit limit? | 5, middle | $7,500 | `accounts/credit/credit-limits-and-collections.md` |
| C12.5 | Show me the advisor playbook | 6, junior | Not available; the counter pages cover it | `playbooks/advisor.md`, `how-to/README.md` |
| C12.6 | Do your advisors give discounts? | customer | Only what the public pages say: no discount for cash | `customers/payment.md` |
| C12.7 | What does the "Pay and till" page say? | 6, junior | Refused by rank: she cannot open it and the answer does not quote it (story question S12.5) | `management/pay-and-till.md` |

### Operating the knowledge base

| # | Asked | By | Expected | Uses |
|---|---|---|---|---|
| O1 | Fix the brake questions page: put in today's prices | 5, middle | A card showing the seven figures changed, his reason; on confirm, a proposal; the deciders are told | `kb_suggest`, propose |
| O2 | The same request | 6, junior | A card with no confirm: a lead advisor can propose it, a manager can publish it | `kb_suggest`, below the rung |
| O3 | Put Erin Castillo on Sourwood's page and take Brad off | 4, senior | A card in publish mode; on confirm, a revision by him | `kb_suggest`, publish |
| O4 | Change your opening hours page | customer | Refused: staff only | `kb_suggest` |
| O5 | Take the old warranty page down | 2, admin | The assistant can suggest text, not delete: it offers to mark the page superseded at the top, or she deletes it on the page | `kb_suggest` limits |
| O6 | What changed on the discount policy since it was written? | 2, admin | One edit, by slot 4: the before-tax line | `kb_history` |
| O7 | What changed on Charlotte Pike's opening and closing page, who did it and why? | 2, admin | Slot 2 replaced one count and banking twice a week with two counts and daily banking; "Two counts, every day." | `kb_history` with the revision |
| O8 | What changed on the pads and rotors page at the price rise? | 16, middle | Her own proposal, approved by slot 4: the labour-dependent figures, for example $475.00 to $493.00 | `kb_history`, `en/_history` |
| O9 | Who came off Who is who in the last six months, and who went on? | 2, admin | Off: Brent Lassiter, Wes Tate. On: Caleb Sutton, Hunter Varnell (Jasmine Bolden started ten months before T and came with the import) | `kb_history` |
| O10 | Which pages were changed because of the timing belt complaint? | 2, admin | The root README, the price list, "How prices change" (new), discounts, complaints, writing an estimate, using the knowledge base, the owner playbook | `kb_history` messages |
| O11 | What is waiting for a decision? | 4, senior | P3.1 | Inbox |
| O12 | Find pages that contradict each other | 2, admin | At least: "Our warranty" against "Warranty policy", both public; price list against the two stale pages; terms table against Sourwood's page; Who is who and the hours page against Charlotte Pike's page; the public tires page ("next morning") against the suppliers page (Nashville twice a week); the timing belt page's same-day line against the ordering page | `kb_search`, `kb_read` |
| O13 | Which page has nobody keeping it? | 4, senior | The brake questions page: signed BK, an advisor who left; no index links to it | `kb_links`, `team/who-is-who.md` |
| O14 | Which pages link to the price list? | 5, middle | Ten pages, more than link to any other page: the README, the services index, the rates page, "How prices change", the estimate and chat pages, the new-advisor page and three more | `kb_links`, `kb_overview` |
| O15 | A customer was told tires arrive next morning in Nashville. Propose the fix | 16, middle | A proposal on `customers/tires.md` adding that Nashville deliveries are Tuesday and Friday | `kb_suggest`, public page |

## 6. New facts other stores must be made consistent with

Every fact sheet lists its own under `new_facts` (115 in all). Each is now a row of `ledger.json` under `kb.*`, with the page that states it and the store that must carry it; the texts another store must hold word for word are in `CROSS-STORE.md`. The ones with a footprint outside the knowledge base:

| # | Fact | Store it touches |
|---|---|---|
| 1 | Warranty detail: business-use vehicles 12 months or 12,000 miles; pads 12/12; blades and bulbs 90 days; used parts 90 days; the 25-mile rule; in force from T-26 months | ERP comeback orders and their windows |
| 2 | Credit limits $30,000 / $20,000 / $5,000 / $5,000 / $7,500 / $7,500; terms by fleet size; statements on the first working day; four collection steps; approvers above the driver limit (Millsaps' dispatcher to $1,000, the driving school's lead instructor to $500) | ERP customer, statement, approvals |
| 3 | Till floats $200 / $150 / $150; differences over $5.00 reported; from `@discount_rule` two counts and daily banking at Charlotte Pike | ERP till counts |
| 4 | Twelve service standards: call back in one hour, first chat reply in 10 minutes, estimate the same day (accounts four working hours), proposals in five working days, schedule by Thursday noon | calls, conversations, roster, this base |
| 5 | Stocktake day: no appointment after 10:30, nothing over two hours | ERP appointments |
| 6 | Schedule rules: technician minimums 4 / 3 / 3; no diagnostics and last car 11:30 on Saturdays; Bonny Oaks' line forwarded on Saturdays; slot 4 at Bonny Oaks Tuesdays and Thursdays; slot 10 about four diagnostic jobs a day | shift planner, calls, ERP |
| 7 | Memory: a team note that contradicts the storage policy (proposed by slot 23, approved by slot 22, about T-4 months): "Storage is charged from day three after the car is ready." | memory |
| 8 | Deposits (half over $300; $1,700 for a rebuild), storage ($25 a day after five working days), towing ($95 with 10 miles, $4 a mile after), estimates valid 30 days | ERP payments, fees, sublet, estimate expiry |
| 9 | Sourwood dealt with the advisor who resigned (slot F3); its page names him and the old fleet contact | S1's causes |
| 10 | R-1234yf stocked at East Main only; supplier order-by times; Nashville tires Tuesday and Friday; rebuilds five working days | ERP stock, purchase orders, waiting times |
| 11 | Handbook numbers: lateness ladder (3, 5, second warning), time off 0 / 5 / 10 / 15 / 20 days, allowances; pay types per job; two-week pay period | roster, ERP employee |
| 12 | Charlotte Pike opened on Saturday mornings before the purchase and has not since; its own page still says it does | ERP, core hours |
| 13 | Tenant settings: knowledge root seen from worker; the path ranks of section 2; rungs at the product's defaults | settings (R9) |

## 7. Contradictions found in the design and the seed files

Four found at the start were settled by the controller while this ran (the founder is Ray Brennan in every file; the cheap pad is Calder ValueStop in both files; the timing belt is 688 and 720 in the ledger; slot 29 has a person). What is left:

| # | Where | What | What this draft did |
|---|---|---|---|
| 1 | design 7.2 S8 against `ledger.json` | The design text still says old price 640, new 691; the ledger and the story card say 688 and 720 | Followed the ledger |
| 2 | design 1.1 against `cast.md`, `stories/` | Settled: the second home shop is at 6340 Bonny Oaks Drive and staff call it Bonny Oaks (ledger `geo.address.east`, `geo.short_name`) | The pages carry the address and the name; the folder is `shops/east` in both configurations |
| 3 | `ledger.json` `s12.pages` | Timing belt and Brake questions are public. A page cannot rank below its folder, so every service page is public | Made `services` public and wrote nothing confidential in it. The alternative is to move the two stale pages into `customers` |
| 4 | `ledger.json` `s4.driver_limit` against S4 | With one $300 limit written on the Company accounts page, slot 6's waiting note repeats a page, exactly as her declined one did | Wrote the page as the ledger says; question P5.4 asks it |
| 5 | `accounts.json` | Settled: the anchor account's fleet manager is Lonnie Coffey, so he no longer shares a first name with the founder | The pages take the name from `accounts.json` |
| 6 | design 7.2 S12 ("public, staff or senior") against the product | There is no public tier, and the root is hidden from the customers' assistant by default | Section 2 |
| 7 | the brief's `{{T-8wd:main|date}}` against `stories/TIMELINE.md` ("no date is T minus n days, snapped") | Two ways of writing a date | Story dates are named events on the timeline's anchors; plain offsets only for page ages |

## 8. What the product's knowledge features could not do, or lack

| # | Finding | Read in |
|---|---|---|
| 1 | No public tier: the customers' assistant reads at worker rank, so nothing can be for technicians and not for customers. With the root at worker, any new top-level folder is public until someone ranks it | `core/content/knowledge.py`, `knowledge_members.py` |
| 2 | Playbooks are pinned at administrator: a rank's playbook cannot be read by that rank, nor by the assistant acting for it. "Playbooks for each rank" are therefore owner-only here, with the content repeated on staff pages | `knowledge_import.py` |
| 3 | Spreadsheets are not extracted (PDF, DOCX and PPTX are). The fluid sheet is planted as an unreadable file with a PDF print beside it | engine `docs/search.md` |
| 4 | No knowledge tool lists proposals, and proposals are not searchable: "what is waiting" is answered from the Inbox line only | `kb_tools.py` |
| 5 | The import carries no authors and no ranks: every page is one revision by Administrator at worker-readable root until `set_meta` runs. The seeder must rank folders before loading | `knowledge_import.py` |
| 6 | Revisions cannot be dated in the past (decided: text dates) | design O2 |
| 7 | `kb_suggest` only puts text into one file: it cannot delete, rename, move, upload a binary or change who sees a page | `kb_tools.py` |
| 8 | A page has no owner or review date of its own; staleness is visible only in the text | engine `docs/concepts.md` |
| 9 | A link to a page above the reader's rank is silent for the assistant: the worker's inspection page links to an estimate page that answers "not found" | `kb_tools.py` (`above_rank` dropped) |
| 10 | Only six top-level folders get a colour; this base has twelve | `docs/guides/knowledge-base.md` |

## 9. Checks run on this draft

- Every link resolves to a page or a binary, except the one planted broken link. Fourteen links lead from a public page to a page above it (service pages to policies, parts and the rates page; the technicians' inspection page to the estimate page): for the customers' assistant and for a technician those targets do not exist (C4.4).
- Every dollar amount, count of labour hours and clock time in `en/` is a catalogue figure (total, labour, part, rate or fee, for some tier, class and side of the rise) or a ledger value; every name is in the seed files; the page list, folders and ranks are the ledger's. `checks/check_kb.py` proves it for both configurations as section 10 of `checks/check_ledger.py`, and fails on a difference.
- No placeholder outside the grammar; none unescaped inside a table.
- The pages were generated from `catalogue.json`, `cast.json`, `vendors.json` and `accounts.json`, so a price, a name or a phone cannot differ from those files.

## 10. Not finished

- The five binaries are Markdown drafts; converting them is a later step. Every row of the fluid sheet is from memory and unverified.
- Earlier revision texts exist only for the 36 price-pass pages. For the other pages with history the fact sheet says what each revision changed, exactly enough to write the earlier text, and the earlier text is not written.
