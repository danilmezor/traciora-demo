# The shop system (source `erp`): rules, v1

This is the company's own shop-management database, schema `shop`: orders, cars, customers, parts and money for the three shops. It is read-only. It is true as of the moment the data was last loaded; say so when an answer depends on "now".

## Shops and clocks

- Three shops in `location`. Staff call them by the street (`location.name`). Two are in the home city; the third, bought later, is in another city and time zone.
- **Every timestamp is the shop's own wall-clock time, with no zone.** The zone is `location.time_zone` and nowhere else. The bought shop reads one hour behind the other two.
- To compare shops at the same moment, convert each shop's times with its zone first: `opened_at AT TIME ZONE l.time_zone`. To compare "before 9:00 at each shop", do not convert.
- The bought shop's records start the day it was bought (`location.opened_on`). Its customers were loaded that day in one batch, so their `created_at` is that day whatever their real history.

## Periods

- Weeks run Monday to Sunday, and a current period counts up to now. **This week**, **this month**, **this year**, "so far": from the period's first day to now. **Last week**, **last month**: the whole calendar week or month before the current one.
- **The last N days** are today and the N − 1 days before it: `>= :today - (N - 1)`. **The last N months** (the last 12 months, the past year) start on the same date N months before today: `>= :today - interval 'N months'`. Both run to now.
- `:today` and now are the home zone's (the zone of the two home-city shops) for a question about the company or about several shops, shop by shop included; a question about one shop alone reads that shop's zone.
- No period said: the whole history.
- The date that puts a row in a period: revenue and every other money of orders, the first invoice (below); a visit, a discount against the rule, recommended work, a comeback, warranty and goodwill work and its value, `opened_at`; a payment, `received_at`; a booking, `starts_at`; a bill, `issued_on`; a till count, `business_date`.
- How long something has waited, or how many days since it happened, is counted in calendar days: today's date minus the day it happened, on the shop's own calendar. "More than 60 days" means that difference is over 60.

## Money

- One currency per install, never converted. Shown with two decimals.
- **Revenue** = orders of type `customer_pay` with status `invoiced` or `paid`, dated by when they were first invoiced (`order_status_history`, status `invoiced`), counted before tax: `total - tax_total`. Leave out voids, declined estimates, orders still open, and warranty and goodwill orders. Say what you left out.
- **Every other money of a period** is taken over revenue's orders and dated the same way: discounts given, labour, parts sales and their margin, a job's money, the average order, billed hours.
- Money earned, given away or spent is before tax. For an order, `total - tax_total`. A line, a discount or the value of free work on an order with `tax_included` true is divided by `1 + tax_rate / 100` (the order's own rate).
- A balance owed, cash taken and today's prices are as the customer pays them: an order's `total`, a payment's `amount`, the price list's own figures (English install: before sales tax, which is added on the bill; Russian install: VAT inside).
- `tax_included` tells how tax sits in an order's prices. `false` (the English install): lines are before tax and the shop's sales tax is added to them; each shop has its own rate (`location.tax_rate`, and the order's own `tax_rate`). `true` (the Russian install, every customer including company accounts): the line prices are the price-list prices with VAT inside, and `tax_total` is the VAT in the total; bills before 2025-01-01 carry no VAT.
- The **average order** (the average ticket) is revenue over the number of revenue's orders.
- `discount_total` is the sum of the order's labour lines' `discount`; part, sublet and fee lines carry no discount. Labour money is `order_labor.amount - discount`, parts sales `quantity * unit_price`, a sublet its `price`.
- A **job's money** is its own lines: its labour less discounts, its parts and its sublets. Fees (`order_fee`) belong to the order, not to a job. Jobs are told apart by the price-list job (`order_job.canned_job_id`, named in `canned_job.name`).
- The **parts margin** is 1 − cost ÷ sales over the part lines of approved jobs: cost `quantity * unit_cost`, sales `quantity * unit_price` before tax.
- A discount's size is its share of the bill before the discount: `discount_total` over `labor_total + parts_total + sublet_total + fees_total`. Both carry the tax when `tax_included`, so the share needs no conversion. Warranty and goodwill orders are not discounts: leave them out of any count of discounts (`order_type = 'customer_pay'`).
- **The discount rule**: a discount above 10 % of the bill needs a manager's approval, recorded in `discount_approved_by_id`. A `customer_pay` order, neither declined nor void, with such a discount and no approver breaks the rule. Orders from before the rule leave the approver empty.
- Prices change over time. A line keeps the price it was written at (`order_labor.rate`, `order_part.unit_price`). Today's prices are in `labor_rate` (the row with `valid_to` null, one per shop and price class: `standard`, and `company_account` for the accounts on negotiated rates), `canned_job` and `part`. A job's labour price today is its `menu_price` when `labor_pricing = 'menu'`, else its `hours` times today's `standard` hour.
- The same part for a bigger vehicle class is a separate `part` row at a higher price; the lowest is the passenger car's.

## Orders

- One `repair_order` row is the estimate, the order and the invoice, moving through statuses: `estimate` → `approved` → `in_progress` (↔ `waiting_parts`, `waiting_sublet`) → `completed` → `invoiced` → `paid`; or `declined` (an estimate nobody approved), or `void`.
- **A void keeps its lines and totals.** Always filter `status <> 'void'` before summing money or counting orders.
- A **visit** is one car coming in: an order that is neither declined nor void, warranty and goodwill orders included. A declined estimate is not a visit. Cars, drop-offs and how busy a shop or a weekday is are counted in visits.
- A shop's **working days** are the days it has a till count (`cash_drawer_close`). A figure a day is over working days: the visits of a shop's working days ÷ its working days; for the company together, a day is a date on which any shop worked.
- An order of a company account billed on terms stays `invoiced` until its statement is paid. That is money owed, not an open job.
- Approval is per job (`order_job.status`). The order's totals count only approved jobs once anything is approved. Declined jobs keep their labour and part lines: filter `order_job.status = 'approved'` when you sum lines.
- **Recommended work** is a job raised from the inspection: an `inspection_item` points at it (`inspection_item.order_job_id`). Share sold = approved ÷ (approved + declined) among those jobs, on orders that are not void; an advisor's are the jobs of the orders they wrote (`repair_order.advisor_id`).
- Sold hours are `order_labor.hours` on approved jobs. Clocked hours are `time_entry`. They differ.
- **Billed hours** are the sold hours of revenue's orders, dated as revenue, each line's hours charged to its technician.
- **Efficiency** is sold hours ÷ clocked hours on the same jobs: per technician, their sold hours on the approved jobs of revenue's orders in the period (dated as revenue) over their finished clock entries (`clock_out` set) on those jobs.
- An **order's technician**, where one person is wanted for the whole order, is the one with the most sold hours on it.
- Time in a status comes from `order_status_history`: the gap to the next row; the last row runs to now. An order waiting now has waited since it last entered that status.
- An **open order** is one whose status is not `invoiced`, `paid`, `void` or `declined`. The office reviews any open more than 60 days.
- A `bad` inspection finding should carry a measurement and a photo; the system does not enforce it, and not every shop keeps it.

## Warranty, goodwill, comebacks

- A **comeback** is a new order of type `warranty` or `goodwill` whose `comeback_of_id` points at the order it repeats. The repeated order's technician is the one who did the original work.
- The comebacks of a period are counted on the orders of the period: the paid orders (`customer_pay`, `invoiced` or `paid`) opened in it that later came back, each charged to that order's technician.
- A warranty or goodwill order keeps its lines at their prices; the whole amount is in `discount_total`, `total` is 0, the status is `paid` and there is no payment row. The value of the free work is `labor_total + parts_total + sublet_total + fees_total`. They are not revenue.

## Payments

- A `payment` settles one order or one statement. One statement payment can cover many orders: to see which, go statement → its orders (`repair_order.statement_id`).
- An order can have several payments (a deposit and the balance, or a split). `kind` tells `payment`, `deposit` and `refund`. **Amounts are always positive**: subtract refunds.
- A voided order can still carry a payment.
- An order is **unpaid** when it is `invoiced` and its payments (deposits counted, refunds subtracted) fall short of its `total`.
- What a company account **owes** now is the `total` of its orders still at `invoiced`, whether their bill has been issued yet or not. A bill is **overdue** when its `due_on` is past and no payment for it has come.
- Days to pay a bill = the date of its first payment minus `statement.issued_on`. How fast an account paid over a period is the mean over its bills issued in the period that are paid.

## Customers and cars

- **Duplicates exist.** The same person can have two records with the name spelled differently. Two records with the same phone are one customer. Merge by phone, never by name.
- **The walk-in record**: one customer record at the bought shop holds counter sales with no real customer ("WALK-IN CUSTOMER" / «Розничный покупатель»). It is not a customer; leave it out of customer counts and say so.
- A **company account** (an account, a corporate customer) is a customer billed on terms: `payment_terms_days` set. Other companies pay at the counter. `price_class = 'company_account'` is a price list some accounts get, not the test of an account. A customer belongs to the shop that created the record (`created_location_id`).
- The business a customer or an account gives (how often they come, what they bring in) is their `customer_pay` orders that are neither declined nor void.
- An account is **lost** after 90 days with no order; it is **being lost** when its last 30 days hold under half the orders of the 30 days that ended 150 days ago.
- A **new customer** in a period is one whose first visit ever falls in it; the others who visited in it are returning. The best customers are those who brought in the most revenue.
- A car belongs to `vehicle.customer_id`; an order's `customer_id` is who it was opened for. They usually match; when they do not, the car was booked under the wrong person.
- Some old cars have no VIN. Mileage is miles or kilometres depending on the install; a reading lower than the car's previous one, or ten times it or more, is a typing mistake.

## Parts and suppliers

- A supplier is late on a received purchase order when it arrived on a later day than promised. How often a supplier is late = its late purchase orders ÷ its received ones; cancelled ones and those not yet received do not count.

## Staff

- `employee` is the shop system's own list, current and former (`left_on`). It shares no key with the people in the product: match by first and last name. A seasonal worker has one row per season.
- Pay type and till counts are hidden from lower ranks.

## Seasons

- The busy season starts in the first month (English install: air-conditioning jobs, the service category whose `code` is 'air_conditioning') or the first week (Russian install: seasonal tyre and wheel changes, the price-list jobs whose `code` is 'seasonal_tyre_change' or 'seasonal_wheel_swap') whose approved jobs of that kind, at all shops, on orders neither declined nor void, number more than 1.5 times (English) or twice (Russian) the mean month or week of the whole history. Only whole months or weeks count, up to the last one before the current, and only seasons the history covers whole: English May to August; Russian 13 April to 10 May and 13 October to 9 November, a week counting for the spring when it starts in the first half of the year.

## Statements

- English install: one statement a month per account, for the month before; its payment covers all its orders. Russian install: one invoice per closed order of an account (rarely one for several), showing the amount before VAT, the VAT and the total. Do not compare "statements a month" across the two.
- `dispute_note` set means the customer disputes the bill.
