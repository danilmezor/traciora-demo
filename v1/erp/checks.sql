-- checks.sql: read-only proofs that a loaded shop database matches the seed v1 ledger.
-- Every query returns one row: the ledger key and the value found. The line before it gives the
-- ledger key, the expected value (en, ru) and the tolerance. A build compares the two.
--
-- The build sets these psql variables from its manifest and timeline (stories/TIMELINE.md):
--   cfg       en | ru
--   size      full | small
--   T         T on the home clock, e.g. '2026-11-13 10:30'
--   G         go-live date;  P  the last price rise (date)
--   bought    west's purchase day;  s2_start  the first day of F1's 26 weeks
--   fired     F1's firing day;  rule_on  the day the discount rule took effect
--   leave_from, leave_to   the diagnostician's leave (s5.leave)
--   pub_week  the Monday of L, the week after the home shops' last roster publish (rule A of generator-spec.md)
-- Example: psql -X -v cfg=en -v size=full -v T='2026-11-13 10:30' -v G=2026-05-22 -v P=2026-06-22
--   -v bought=2025-09-15 -v s2_start=2025-12-15 -v fired=2026-06-15 -v rule_on=2026-06-16
--   -v leave_from=2026-08-31 -v leave_to=2026-09-11 -v pub_week=2026-11-16 -f checks.sql
-- "Orders" below are rows that are neither declined nor void unless a query says otherwise.
-- "Closed in the last 12 months" means first invoiced in the 12 months before T.
-- People are found by first and last name, accounts by their trade name, shops by name.

SET search_path = shop;
SET default_transaction_read_only = on;

-- geo.short_name | expected en={"main": "East Main", "east": "Bonny Oaks", "west": "Charlotte Pike"} ru={"main": "Московское шоссе", "east": "Инженерный", "west": "Техническая"} | tolerance exact
-- want: value == ', '.join(L[s] for s in ('main', 'east', 'west'))
SELECT 'geo.short_name' AS ledger_key, string_agg(name, ', ' ORDER BY location_id) AS value FROM shop.location;

-- geo.home_zone | expected en="America/New_York" ru="Europe/Ulyanovsk" | tolerance exact
-- want: same(value, L)
SELECT 'geo.home_zone' AS ledger_key, string_agg(DISTINCT time_zone, ', ') AS value FROM shop.location WHERE location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END));

-- geo.other_zone | expected en="America/Chicago" ru="Europe/Moscow" | tolerance exact
-- want: same(value, L)
SELECT 'geo.other_zone' AS ledger_key, time_zone AS value FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- site.bays.main | expected en=8 ru=6 | tolerance exact
-- want: same(value, L)
SELECT 'site.bays.main' AS ledger_key, bays AS value FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- site.bays.east | expected en=6 ru=4 | tolerance exact
-- want: same(value, L)
SELECT 'site.bays.east' AS ledger_key, bays AS value FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- site.bays.west | expected en=6 ru=4 | tolerance exact
-- want: same(value, L)
SELECT 'site.bays.west' AS ledger_key, bays AS value FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- tax.rate | expected en=9.25 ru=5.0 | tolerance exact | the home rate: the rate of main and east
-- want: same(value, L)
SELECT 'tax.rate' AS ledger_key, string_agg(DISTINCT l.tax_rate::text, ', ') AS value FROM shop.location l WHERE l.name IN (CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END, CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- tax.rate.main | expected en=9.25 ru=5.0 | tolerance exact | the shop's rate, and its orders off it (en every order; ru from 2025-01-01); expected 0
-- want: same(value, L) and row['orders_off_the_rate'] == 0
SELECT 'tax.rate.main' AS ledger_key, max(l.tax_rate) AS value,
       count(o.repair_order_id) FILTER (WHERE o.tax_rate <> l.tax_rate AND (:'cfg' = 'en' OR o.opened_at >= DATE '2025-01-01')) AS orders_off_the_rate
FROM shop.location l LEFT JOIN shop.repair_order o ON o.location_id = l.location_id WHERE l.name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END;

-- tax.rate.east | expected en=9.25 ru=5.0 | tolerance exact | the shop's rate, and its orders off it (en every order; ru from 2025-01-01); expected 0
-- want: same(value, L) and row['orders_off_the_rate'] == 0
SELECT 'tax.rate.east' AS ledger_key, max(l.tax_rate) AS value,
       count(o.repair_order_id) FILTER (WHERE o.tax_rate <> l.tax_rate AND (:'cfg' = 'en' OR o.opened_at >= DATE '2025-01-01')) AS orders_off_the_rate
FROM shop.location l LEFT JOIN shop.repair_order o ON o.location_id = l.location_id WHERE l.name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END;

-- tax.rate.west | expected en=9.75 ru=5.0 | tolerance exact | the shop's rate, and its orders off it (en every order; ru from 2025-01-01); expected 0
-- want: same(value, L) and row['orders_off_the_rate'] == 0
SELECT 'tax.rate.west' AS ledger_key, max(l.tax_rate) AS value,
       count(o.repair_order_id) FILTER (WHERE o.tax_rate <> l.tax_rate AND (:'cfg' = 'en' OR o.opened_at >= DATE '2025-01-01')) AS orders_off_the_rate
FROM shop.location l LEFT JOIN shop.repair_order o ON o.location_id = l.location_id WHERE l.name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END;

-- tax.ru_vat_from | expected en=null ru="2025-01-01" | tolerance exact | value = orders that break the date rule; expected 0 (ru only)
-- want: value == 0
SELECT 'tax.ru_vat_from' AS ledger_key,
       count(*) FILTER (WHERE o.opened_at < DATE '2025-01-01' AND o.tax_rate > 0)
     + count(*) FILTER (WHERE o.opened_at >= DATE '2025-01-01' AND o.tax_rate <> (SELECT l.tax_rate FROM shop.location l WHERE l.location_id = o.location_id)) AS value
FROM shop.repair_order o
WHERE :'cfg' = 'ru';

-- tax.ru_price_basis | expected en="every list and company-account price is before sales tax; the shop's rate (tax.rate.main, .east, .west) is added on the bill" ru="every customer pays the table price, VAT inside, on a bill dated from tax.ru_vat_from: a private or small-business customer and the walk-in record the list figure, an account billed on terms (A1 to A6) the same table (the company-account class for A1 and A2, the list figures for A3 to A6). Nothing is added on top for anyone. The amount before VAT of any bill is its total / 1.05, to the kopeck. A private or small-business customer's order, act and receipt show the total and «в том числе НДС 5 %»; an account's счёт and УПД show the amount before VAT, the VAT and the total as separate figures (t… | tolerance exact | value = orders off the tax rule: tax_included is false in en and true in ru on every order; ru VAT = total - round(total / 1.05, 2) from 2025-01-01; en tax added at the order's rate; expected 0, 0, 0
-- want: row['tax_included_off_the_rule'] == 0 and row['ru_vat_off_the_divisor'] == 0 and row['en_tax_off_the_rate'] == 0
SELECT 'tax.ru_price_basis' AS ledger_key,
       count(*) FILTER (WHERE o.tax_included <> (:'cfg' = 'ru')) AS tax_included_off_the_rule,
       count(*) FILTER (WHERE :'cfg' = 'ru' AND o.order_type = 'customer_pay' AND o.opened_at >= DATE '2025-01-01' AND o.tax_total <> o.total - round(o.total / 1.05, 2)) AS ru_vat_off_the_divisor,
       count(*) FILTER (WHERE :'cfg' = 'en' AND o.order_type = 'customer_pay' AND o.tax_total <> round((o.labor_total + o.parts_total + o.sublet_total + o.fees_total - o.discount_total) * o.tax_rate / 100, 2)) AS en_tax_off_the_rate
FROM shop.repair_order o;

-- tax.max_single_part | expected en=1600 ru=null | tolerance value at most the row
-- want: value is None if L is None else value is not None and value <= L
SELECT 'tax.max_single_part' AS ledger_key, max(unit_price) AS value FROM shop.order_part WHERE :'cfg' = 'en';

-- time.history_months | expected 24 | tolerance within 0.2 months
-- want: near(value, L, abs=0.2)
SELECT 'time.history_months' AS ledger_key,
       round((:'T'::date - min(o.opened_at)::date) / 30.44, 1) AS value
FROM shop.repair_order o WHERE o.location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END));

-- time.west_bought_months | expected 14 | tolerance within 0.2 months; the bulk load is the largest day of west customers
-- want: near(value, L, abs=0.2) and row['customers_loaded_that_day'] > (row['largest_other_day'] or 0)
SELECT 'time.west_bought_months' AS ledger_key,
       round((:'T'::date - min(o.opened_at)::date) / 30.44, 1) AS value,
       (SELECT count(*) FROM shop.customer c WHERE c.created_location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)
          AND c.created_at::date = (SELECT opened_on FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END))) AS customers_loaded_that_day,
       (SELECT max(n) FROM (SELECT count(*) AS n FROM shop.customer c WHERE c.created_location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)
          AND c.created_at::date <> (SELECT opened_on FROM shop.location WHERE location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)) GROUP BY c.created_at::date) d) AS largest_other_day
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- volume.orders_per_day.main | expected en=17.04 ru=12.98 | tolerance within 3 % at full size; × size.small.density at small size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_day.main' AS ledger_key,
       round(count(*)::numeric / NULLIF((SELECT count(*) FROM shop.cash_drawer_close d
            WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND d.business_date > :'T'::date - 365
              AND (:'cfg' = 'ru' OR extract(isodow FROM d.business_date) < 6)), 0), 2) AS value
FROM shop.repair_order o
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND o.status NOT IN ('declined', 'void')
  AND o.opened_at > :'T'::timestamp - interval '365 days'
  AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6);

-- volume.orders_per_day.east | expected en=10.98 ru=8.0 | tolerance within 3 % at full size; × size.small.density at small size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_day.east' AS ledger_key,
       round(count(*)::numeric / NULLIF((SELECT count(*) FROM shop.cash_drawer_close d
            WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND d.business_date > :'T'::date - 365
              AND (:'cfg' = 'ru' OR extract(isodow FROM d.business_date) < 6)), 0), 2) AS value
FROM shop.repair_order o
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.status NOT IN ('declined', 'void')
  AND o.opened_at > :'T'::timestamp - interval '365 days'
  AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6);

-- volume.orders_per_day.west | expected en=8.98 ru=7.0 | tolerance within 3 % at full size; × size.small.density at small size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_day.west' AS ledger_key,
       round(count(*)::numeric / NULLIF((SELECT count(*) FROM shop.cash_drawer_close d
            WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND d.business_date > :'T'::date - 365
              AND (:'cfg' = 'ru' OR extract(isodow FROM d.business_date) < 6)), 0), 2) AS value
FROM shop.repair_order o
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND o.status NOT IN ('declined', 'void')
  AND o.opened_at > :'T'::timestamp - interval '365 days'
  AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6);

-- volume.saturday_orders.main | expected en=5.15 ru=0 | tolerance within 5 % at full size (en only)
-- want: near(value, L, pct=5)
SELECT 'volume.saturday_orders.main' AS ledger_key,
       round(count(*)::numeric / NULLIF((SELECT count(*) FROM shop.cash_drawer_close d WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END)
            AND d.business_date > :'T'::date - 365 AND extract(isodow FROM d.business_date) = 6), 0), 2) AS value
FROM shop.repair_order o
WHERE :'cfg' = 'en' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND o.status NOT IN ('declined', 'void')
  AND o.opened_at > :'T'::timestamp - interval '365 days' AND extract(isodow FROM o.opened_at) = 6;

-- volume.orders_per_month.main | expected en=384.3 ru=392.9 | tolerance within 3 % at full size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_month.main' AS ledger_key, round(count(*) / 12.0, 1) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- volume.orders_per_month.east | expected en=233.2 ru=242.2 | tolerance within 3 % at full size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_month.east' AS ledger_key, round(count(*) / 12.0, 1) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- volume.orders_per_month.west | expected en=190.7 ru=211.9 | tolerance within 3 % at full size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_month.west' AS ledger_key, round(count(*) / 12.0, 1) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- volume.orders_per_month.company | expected en=808.2 ru=847.0 | tolerance within 3 % at full size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_per_month.company' AS ledger_key, round(count(*) / 12.0, 1) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- volume.orders_history | expected en=17490 ru=18209 | tolerance within 3 % at full size
-- want: near(value, L, pct=3)
SELECT 'volume.orders_history' AS ledger_key, count(*) AS value FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void');

-- volume.hours_per_order | band | expected en=2.5 ru=2.2 | tolerance ±8 % | definition: mean of the approved jobs' labour hours over customer-pay orders invoiced or paid | window: first invoiced in the 12 months before T | unit: hours per order | tax: none
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.hours_per_order' AS ledger_key, round(avg((SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved')), 3) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months';

-- volume.hours_per_order.main | band | expected en=2.456 ru=2.162 | tolerance ±8 % | definition: mean of the approved jobs' labour hours over customer-pay orders invoiced or paid at main | window: first invoiced in the 12 months before T | unit: hours per order | tax: none
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.hours_per_order.main' AS ledger_key, round(avg((SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved')), 3) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- volume.hours_per_order.east | band | expected en=2.683 ru=2.355 | tolerance ±8 % | definition: mean of the approved jobs' labour hours over customer-pay orders invoiced or paid at east | window: first invoiced in the 12 months before T | unit: hours per order | tax: none
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.hours_per_order.east' AS ledger_key, round(avg((SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved')), 3) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- volume.hours_per_order.west | band | expected en=2.364 ru=2.094 | tolerance ±8 % | definition: mean of the approved jobs' labour hours over customer-pay orders invoiced or paid at west | window: first invoiced in the 12 months before T | unit: hours per order | tax: none
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.hours_per_order.west' AS ledger_key, round(avg((SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved')), 3) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- volume.average_order | band | expected en=522.0 ru=11374.4 | tolerance ±8 % | definition: mean of total - tax_total over customer-pay orders invoiced or paid | window: first invoiced in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months';

-- volume.average_order.main | band | expected en=510.4 ru=11159 | tolerance ±8 % | definition: mean of total - tax_total over customer-pay orders invoiced or paid at main | window: first invoiced in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.average_order.main' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- volume.average_order.east | band | expected en=562.3 ru=12122 | tolerance ±8 % | definition: mean of total - tax_total over customer-pay orders invoiced or paid at east | window: first invoiced in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.average_order.east' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- volume.average_order.west | band | expected en=495.4 ru=10912 | tolerance ±8 % | definition: mean of total - tax_total over customer-pay orders invoiced or paid at west | window: first invoiced in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.average_order.west' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- volume.parts_per_order | band | expected en=242.8 ru=7569.1 | tolerance ±8 % | definition: mean of parts, sublet and fees over customer-pay orders invoiced or paid | window: first invoiced in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax (ru lines divided by 1 + rate)
-- want: band(value, L * 0.92, L * 1.08)
SELECT 'volume.parts_per_order' AS ledger_key,
       round(avg((o.parts_total + o.sublet_total + o.fees_total) * (CASE WHEN o.tax_included THEN 1 / (1 + o.tax_rate / 100) ELSE 1 END)), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months';

-- price.effective_rate | band | expected en=0.866 ru=1.007 | tolerance ±0.06, never above 1.0 in en | definition: labour less discounts over billed hours times the standard posted hour in force on the order's day, customer-pay orders invoiced or paid | window: first invoiced in the 12 months before T | unit: ratio | tax: as billed (ru VAT inside both) | eval_answer: false
-- want: band(value, L - 0.06, min(L + 0.06, 1.0) if cfg == 'en' else L + 0.06)
SELECT 'price.effective_rate' AS ledger_key,
       round(sum(o.labor_total - o.discount_total) / NULLIF(sum((SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') * (SELECT r.rate FROM shop.labor_rate r
             WHERE r.location_id = o.location_id AND r.price_class = 'standard' AND r.valid_from <= o.opened_at::date AND (r.valid_to IS NULL OR r.valid_to >= o.opened_at::date))), 0), 3) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > :'T'::timestamp - interval '12 months';

-- price.hour.posted | expected en=135.0 ru=1900 | tolerance exact
-- want: same(value, L)
SELECT 'price.hour.posted' AS ledger_key, string_agg(DISTINCT r.rate::text, ', ') AS value
FROM shop.labor_rate r WHERE r.price_class = 'standard' AND r.valid_to IS NULL;

-- price.hour.history | expected en=[["T-24 months", 125.0], ["P", 135.0]] ru=[["T-24 months", 1500], ["the first open day on or after T-18 months", 1620], ["the first full open day on or after T-335 days", 1760], ["P", 1900]] | tolerance exact | dates against TIMELINE anchors (T-24 months, P; ru also T-18 months, s2_start)
-- want: value is not None and len(value.split('; ')) == len(L) and all(same(p.split(' ')[1], r) for p, (_, r) in zip(value.split('; '), L)) and [p.split(' ')[0] for p in value.split('; ')] == [str(d) for d in ((a['history_start'], a['P']) if cfg == 'en' else (a['history_start'], a['ru_rise'], a['s2_start'], a['P']))]
SELECT 'price.hour.history' AS ledger_key, string_agg(r.valid_from || ' ' || r.rate, '; ' ORDER BY r.valid_from) AS value
FROM shop.labor_rate r WHERE r.price_class = 'standard' AND r.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- price.hour.company | expected en=121.5 ru=1700 | tolerance exact
-- want: same(value, L)
SELECT 'price.hour.company' AS ledger_key, string_agg(DISTINCT r.rate::text, ', ') AS value
FROM shop.labor_rate r WHERE r.price_class = 'company_account' AND r.valid_to IS NULL;

-- price.hour.company_history | expected en=[112.5, 121.5] ru=[1350, 1460, 1580, 1700] | tolerance exact
-- want: each(value, L)
SELECT 'price.hour.company_history' AS ledger_key, string_agg(r.rate::text, ', ' ORDER BY r.valid_from) AS value
FROM shop.labor_rate r WHERE r.price_class = 'company_account' AND r.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- price.rise.last_pct | expected en=8.0 ru=7.95 | tolerance exact
-- want: same(value, L)
SELECT 'price.rise.last_pct' AS ledger_key,
       round((max(r.rate) FILTER (WHERE r.valid_to IS NULL) / max(r.rate) FILTER (WHERE r.valid_to = :'P'::date - 1) - 1) * 100, 2) AS value
FROM shop.labor_rate r WHERE r.price_class = 'standard';

-- price.supplies.rate | expected en=5.0 ru=3.0 | tolerance exact | value = supplies fees off the rule; expected 0
-- want: value == 0
SELECT 'price.supplies.rate' AS ledger_key,
       count(*) FILTER (WHERE abs(f.amount - least(round((SELECT coalesce(sum(l.amount), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
               JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
          WHERE j.repair_order_id = f.repair_order_id AND j.status = 'approved' AND c.labor_pricing = 'hourly') * (CASE :'cfg' WHEN 'en' THEN 0.05 ELSE 0.03 END), 2),
                                                CASE :'cfg' WHEN 'en' THEN 35 ELSE 500 END)) > 0.01) AS value
FROM shop.order_fee f WHERE f.kind = 'shop_supplies';

-- price.supplies.cap | expected en=35.0 ru=500 | tolerance value at most the row
-- want: value is not None and value <= L
SELECT 'price.supplies.cap' AS ledger_key, max(f.amount) AS value FROM shop.order_fee f WHERE f.kind = 'shop_supplies';

-- price.discount_rule_pct | expected 10 | tolerance exact | value = discounts above 10 % with no approver since the rule; expected 2 (slot 23)
-- want: value == 2
SELECT 'price.discount_rule_pct' AS ledger_key, count(*) AS value
FROM shop.repair_order o
WHERE o.opened_at >= :'rule_on'::date AND o.discount_approved_by_id IS NULL AND o.order_type = 'customer_pay'
  AND o.discount_total > 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total);

-- mix.orders_with_rec | expected en=65.0 ru=60.0 | tolerance ±2 points
-- want: near(value, L, abs=2)
SELECT 'mix.orders_with_rec' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.order_job j WHERE j.repair_order_id = o.repair_order_id AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id)))
             / count(*), 1) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status NOT IN ('declined', 'void');

-- mix.pad_job_share | expected en=20.79 ru=12.2 | tolerance ±1 point
-- want: near(value, L, abs=1)
SELECT 'mix.pad_job_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
             WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors'))) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status NOT IN ('declined', 'void');

-- sold.main | expected en=51.44 ru=51.08 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'sold.main' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- sold.east | expected en=63.4 ru=62.45 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'sold.east' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- sold.west | expected en=46.55 ru=47.12 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'sold.west' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- sold.company | expected en=53.73 ru=53.34 | tolerance ±2 points
-- want: near(value, L, abs=2)
SELECT 'sold.company' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p05.sold_rec | expected 58 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p05.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Travis' ELSE 'Дмитрий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Burnette' ELSE 'Григорьев' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p06.sold_rec | expected 54 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p06.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Maya' ELSE 'Алина' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Torres' ELSE 'Хасанова' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p07.sold_rec | expected 35 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p07.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Caleb' ELSE 'Никита' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sutton' ELSE 'Ведяшкин' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p29.sold_rec | expected 50 | tolerance one case: round(n × the row / 100) ± 1
-- want: abs(row['count'] - round(row['n'] * L / 100)) <= 1
SELECT 'p29.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brenda' ELSE 'Татьяна' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Pickett' ELSE 'Пахомова' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p16.sold_rec | expected 71 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p16.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Angie' ELSE 'Светлана' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Holloway' ELSE 'Демидова' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p17.sold_rec | expected 52 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p17.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Josh' ELSE 'Артём' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tipton' ELSE 'Николаев' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p23.sold_rec | expected 38 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p23.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Chad' ELSE 'Вячеслав' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Binkley' ELSE 'Крюков' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p24.sold_rec | expected 57 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p24.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Jasmine' ELSE 'Камила' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Bolden' ELSE 'Шакирова' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- pF3.sold_rec | expected 50 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'pF3.sold_rec' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value,
       count(*) FILTER (WHERE j.status IN ('approved', 'declined')) AS n, count(*) FILTER (WHERE j.status = 'approved') AS count
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brad' ELSE 'Вадим' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Keller' ELSE 'Савельев' END) AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- p05.order_share | expected en=37 ru=32.5 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p05.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Travis' ELSE 'Дмитрий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Burnette' ELSE 'Григорьев' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- p06.order_share | expected en=37 ru=27.5 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p06.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Maya' ELSE 'Алина' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Torres' ELSE 'Хасанова' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- p07.order_share | expected en=20 ru=17.5 | tolerance ±2.0, at least 29 cases
-- want: near(value, L, abs=2.0)
SELECT 'p07.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Caleb' ELSE 'Никита' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sutton' ELSE 'Ведяшкин' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- p29.order_share | expected en=6 ru=22.5 | tolerance ±2.0, at least 84 cases
-- want: near(value, L, abs=2.0)
SELECT 'p29.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brenda' ELSE 'Татьяна' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Pickett' ELSE 'Пахомова' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- p16.order_share | expected en=60 ru=55 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p16.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Angie' ELSE 'Светлана' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Holloway' ELSE 'Демидова' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- p17.order_share | expected en=40 ru=45 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p17.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Josh' ELSE 'Артём' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tipton' ELSE 'Николаев' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- p23.order_share | expected en=55 ru=52 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p23.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Chad' ELSE 'Вячеслав' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Binkley' ELSE 'Крюков' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- p24.order_share | expected en=45 ru=48 | tolerance ±2.0, at least 25 cases
-- want: near(value, L, abs=2.0)
SELECT 'p24.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Jasmine' ELSE 'Камила' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Bolden' ELSE 'Шакирова' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- pF1.order_share | band | expected 33.3 | tolerance ±5 points | from the hire of slot 24 (10 months before T) to the firing, when west had three advisors | definition: the fired advisor's orders over west's orders not declined or void | window: from slot 24's hire to his firing | unit: % of orders | tax: none
-- want: band(value, L - 5, L + 5)
SELECT 'pF1.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)
  AND o.opened_at >= (SELECT hired_on FROM shop.employee WHERE employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Jasmine' ELSE 'Камила' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Bolden' ELSE 'Шакирова' END))
  AND o.opened_at < :'fired'::date;

-- pF3.order_share | expected 30 | tolerance ±2.0, at least 25 cases | while F3, 5 and 6 wrote main's orders
-- want: near(value, L, abs=2.0)
SELECT 'pF3.order_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brad' ELSE 'Вадим' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Keller' ELSE 'Савельев' END)) / NULLIF(count(*), 0), 1) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END)
  AND o.opened_at >= (SELECT hired_on FROM shop.employee WHERE employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Maya' ELSE 'Алина' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Torres' ELSE 'Хасанова' END))
  AND o.opened_at <= (SELECT left_on FROM shop.employee WHERE employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brad' ELSE 'Вадим' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Keller' ELSE 'Савельев' END));

-- p10.billed_index | band | expected 1.35 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p10.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Kevin' ELSE 'Андрей' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lawson' ELSE 'Шубин' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p11.billed_index | band | expected 1.3 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p11.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Dustin' ELSE 'Максим' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Swafford' ELSE 'Рябов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p12.billed_index | band | expected 1.0 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p12.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Luis' ELSE 'Алексей' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Herrera' ELSE 'Карпов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p13.billed_index | band | expected 0.9 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p13.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Terry' ELSE 'Ильдар' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Dotson' ELSE 'Нуруллин' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p14.billed_index | band | expected 0.65 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p14.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Hunter' ELSE 'Иван' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Varnell' ELSE 'Сурков' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p15.billed_index | band | expected 0.82 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p15.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Cody' ELSE 'Евгений' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Gann' ELSE 'Чугунов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p18.billed_index | band | expected 1.15 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p18.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 7.75 ELSE 150 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Andre' ELSE 'Валерий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Simmons' ELSE 'Егоров' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p19.billed_index | band | expected 1.0 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p19.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 7.75 ELSE 150 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Brandon' ELSE 'Роман' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sisk' ELSE 'Кудряшов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p20.billed_index | band | expected 0.93 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p20.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 7.75 ELSE 150 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Austin' ELSE 'Антон' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Crabtree' ELSE 'Блинов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p21.billed_index | band | expected 0.9 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p21.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 7.75 ELSE 150 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Jordan' ELSE 'Марат' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Akins' ELSE 'Аюпов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p25.billed_index | band | expected 1.15 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p25.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 5.9 ELSE 123 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Gary' ELSE 'Фарит' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tidwell' ELSE 'Зиннатуллин' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p26.billed_index | band | expected 1.0 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p26.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 5.9 ELSE 123 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Shane' ELSE 'Станислав' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Maddox' ELSE 'Орехов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p27.billed_index | band | expected 1.0 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p27.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 5.9 ELSE 123 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- p28.billed_index | band | expected 0.75 | tolerance ±0.15 | hours sold over worked days, against the site norm a day (ru: the month norm over 21.74 days); en weekdays only; divided by the shop's season: its billed hours per open day in the 90 days over the 12 months (hours, not orders: a season of short jobs raises the orders more than the work) | definition: the mechanic's approved labour hours a worked day over the site norm a day, divided by the shop's season | window: orders opened in the 90 days before T, en weekdays | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'p28.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)), 0)
             / (CASE :'cfg' WHEN 'en' THEN 5.9 ELSE 123 / 21.74 END)
             / NULLIF((SELECT (sum(sl.hours) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days') / NULLIF(count(DISTINCT s.opened_at::date) FILTER (WHERE s.opened_at > :'T'::timestamp - interval '90 days'), 0))
                           / NULLIF(sum(sl.hours) / NULLIF(count(DISTINCT s.opened_at::date), 0), 0)
                      FROM shop.repair_order s JOIN shop.order_job sj ON sj.repair_order_id = s.repair_order_id AND sj.status = 'approved' JOIN shop.order_labor sl ON sl.order_job_id = sj.order_job_id
                      WHERE s.location_id = m.location_id AND s.status NOT IN ('declined', 'void')
                        AND s.opened_at > :'T'::timestamp - interval '12 months' AND (:'cfg' = 'ru' OR extract(isodow FROM s.opened_at) < 6)), 0), 3) AS value
FROM shop.employee m JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE m.first_name = CASE :'cfg' WHEN 'en' THEN 'Tyler' ELSE 'Булат' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Jarrell' ELSE 'Гарипов' END AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
GROUP BY m.employee_id, m.location_id;

-- pF2.billed_index | band | expected 0.95 | tolerance ±0.15 | definition: the mechanic's approved labour hours a worked day over the site norm a day | window: his whole employment | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'pF2.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t WHERE t.technician_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Wes' ELSE 'Константин' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tate' ELSE 'Жарков' END)), 0) / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END), 3) AS value
FROM shop.order_labor l JOIN shop.order_job j ON j.order_job_id = l.order_job_id
WHERE l.technician_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Wes' ELSE 'Константин' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tate' ELSE 'Жарков' END) AND j.status = 'approved';

-- pF4.billed_index | band | expected 0.8 | tolerance ±0.15 | definition: the mechanic's approved labour hours a worked day over the site norm a day | window: his whole employment | unit: index | tax: none | eval_answer: false
-- want: band(value, L - 0.15, L + 0.15)
SELECT 'pF4.billed_index' AS ledger_key,
       round(sum(l.hours) / NULLIF((SELECT count(DISTINCT t.clock_in::date) FROM shop.time_entry t
             WHERE t.technician_id IN (SELECT employee_id FROM shop.employee e WHERE e.role = 'technician' AND e.left_on IS NOT NULL
               AND e.last_name = CASE :'cfg' WHEN 'en' THEN 'Pruitt' ELSE 'Юсупов' END)), 0) / (CASE :'cfg' WHEN 'en' THEN 6.75 ELSE 137 / 21.74 END), 3) AS value
FROM shop.order_labor l JOIN shop.order_job j ON j.order_job_id = l.order_job_id
WHERE j.status = 'approved' AND l.technician_id IN (SELECT employee_id FROM shop.employee e
      WHERE e.last_name = CASE :'cfg' WHEN 'en' THEN 'Pruitt' ELSE 'Юсупов' END);

-- p10.comebacks | expected 0.5 | tolerance ±1.0, at least 1000 cases
-- want: near(value, L, abs=1.0)
SELECT 'p10.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Kevin' ELSE 'Андрей' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lawson' ELSE 'Шубин' END);

-- p11.comebacks | expected 4.5 | tolerance ±1.0, at least 112 cases
-- want: near(value, L, abs=1.0)
SELECT 'p11.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Dustin' ELSE 'Максим' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Swafford' ELSE 'Рябов' END);

-- p12.comebacks | expected 2.0 | tolerance ±1.0, at least 250 cases
-- want: near(value, L, abs=1.0)
SELECT 'p12.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Luis' ELSE 'Алексей' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Herrera' ELSE 'Карпов' END);

-- p13.comebacks | expected 1.5 | tolerance ±1.0, at least 334 cases
-- want: near(value, L, abs=1.0)
SELECT 'p13.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Terry' ELSE 'Ильдар' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Dotson' ELSE 'Нуруллин' END);

-- p14.comebacks | expected 6.0 | tolerance one case: round(n × the row / 100) ± 1 | orders completed at least the shortest comeback gap (erp.comeback.gap_days, 2 days) before T
-- want: abs(row['count'] - round(row['n'] * L / 100)) <= 1
SELECT 'p14.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'completed') <= :'T'::timestamp - interval '2 days'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Hunter' ELSE 'Иван' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Varnell' ELSE 'Сурков' END);

-- p15.comebacks | expected 1.0 | tolerance ±1.0, at least 500 cases
-- want: near(value, L, abs=1.0)
SELECT 'p15.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Cody' ELSE 'Евгений' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Gann' ELSE 'Чугунов' END);

-- p18.comebacks | expected 1.5 | tolerance ±1.0, at least 334 cases
-- want: near(value, L, abs=1.0)
SELECT 'p18.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Andre' ELSE 'Валерий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Simmons' ELSE 'Егоров' END);

-- p19.comebacks | expected 2.5 | tolerance ±1.0, at least 200 cases
-- want: near(value, L, abs=1.0)
SELECT 'p19.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brandon' ELSE 'Роман' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sisk' ELSE 'Кудряшов' END);

-- p20.comebacks | expected 2.5 | tolerance ±1.0, at least 200 cases
-- want: near(value, L, abs=1.0)
SELECT 'p20.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Austin' ELSE 'Антон' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Crabtree' ELSE 'Блинов' END);

-- p21.comebacks | expected 2.0 | tolerance ±1.0, at least 250 cases
-- want: near(value, L, abs=1.0)
SELECT 'p21.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Jordan' ELSE 'Марат' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Akins' ELSE 'Аюпов' END);

-- p25.comebacks | expected 2.0 | tolerance ±1.0, at least 250 cases
-- want: near(value, L, abs=1.0)
SELECT 'p25.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Gary' ELSE 'Фарит' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tidwell' ELSE 'Зиннатуллин' END);

-- p26.comebacks | expected 3.0 | tolerance ±1.0, at least 167 cases
-- want: near(value, L, abs=1.0)
SELECT 'p26.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Shane' ELSE 'Станислав' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Maddox' ELSE 'Орехов' END);

-- p27.comebacks | expected en=6.93 ru=5.31 | tolerance ±1.0, at least 95 cases
-- want: near(value, L, abs=1.0)
SELECT 'p27.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at >= :'bought'::date
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- p28.comebacks | expected 3.0 | tolerance ±1.0, at least 167 cases
-- want: near(value, L, abs=1.0)
SELECT 'p28.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Tyler' ELSE 'Булат' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Jarrell' ELSE 'Гарипов' END);

-- pF2.comebacks | expected 5.0 | tolerance ±1.0, at least 100 cases
-- want: near(value, L, abs=1.0)
SELECT 'pF2.comebacks' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value,
       count(*) AS n, count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) AS count
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid')
  AND o.opened_at > (SELECT left_on FROM shop.employee WHERE employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Wes' ELSE 'Константин' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tate' ELSE 'Жарков' END)) - interval '6 months'
  AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Wes' ELSE 'Константин' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Tate' ELSE 'Жарков' END);

-- comeback.main | expected 2.41 | tolerance ±0.5 points
-- want: near(value, L, abs=0.5)
SELECT 'comeback.main' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END);

-- comeback.east | expected 2.1 | tolerance ±0.5 points
-- want: near(value, L, abs=0.5)
SELECT 'comeback.east' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END);

-- comeback.west | expected en=3.77 ru=3.32 | tolerance ±0.5 points
-- want: near(value, L, abs=0.5)
SELECT 'comeback.west' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at >= :'bought'::date AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- comeback.company | expected en=2.64 ru=2.55 | tolerance ±0.5 points
-- want: near(value, L, abs=0.5)
SELECT 'comeback.company' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- comeback.definition | expected en="an order that points at the order it repeats: of type warranty inside the warranty (24 months or 24,000 miles; pads 12 months or 12,000 miles), goodwill after it" ru="an order of type warranty that points at the order it repeats, opened within 30 days of it (the warranty on mechanical and electrical work); a repeat after day 30 is a paid order and is not a comeback" | tolerance exact | expected 0, 0, and ru 0 (no goodwill order in ru: the second look of board.second_look_open is a warranty order; the column counts ru only)
-- want: row['warranty_or_goodwill_without_first_order'] == 0 and row['ru_repeats_after_30_days'] == 0 and row['ru_goodwill_orders'] == 0
SELECT 'comeback.definition' AS ledger_key,
       count(*) FILTER (WHERE o.comeback_of_id IS NULL) AS warranty_or_goodwill_without_first_order,
       count(*) FILTER (WHERE :'cfg' = 'ru' AND o.opened_at::date - f.opened_at::date > 30) AS ru_repeats_after_30_days,
       count(*) FILTER (WHERE :'cfg' = 'ru' AND o.order_type = 'goodwill') AS ru_goodwill_orders
FROM shop.repair_order o LEFT JOIN shop.repair_order f ON f.repair_order_id = o.comeback_of_id
WHERE o.order_type IN ('warranty', 'goodwill');

-- acct.A1.visits | expected [24, 24, 24, 24, 24, 24] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A1.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A1.average_order | band | expected en=560 ru=12857.14 | tolerance ±20 % | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A1.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A1.terms_days | expected 30 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A1.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%');

-- acct.A1.vehicles | expected 35 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A1.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%');

-- acct.A1.shop | expected "main" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A1.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- acct.A2.visits | expected [26, 26, 26, 26, 26, 26] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A2.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A2.average_order | band | expected en=380 ru=8761.9 | tolerance ±20 % | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A2.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A2.terms_days | expected 30 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A2.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%');

-- acct.A2.vehicles | expected 25 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A2.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%');

-- acct.A2.shop | expected "east" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A2.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- acct.A3.visits | expected [5, 5, 5, 5, 5, 5] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A3.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A3.average_order | band | expected en=430 ru=9904.76 | tolerance ±20 % | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A3.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A3.terms_days | expected en=15 ru=14 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A3.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%');

-- acct.A3.vehicles | expected 9 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A3.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%');

-- acct.A3.shop | expected "main" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A3.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- acct.A4.visits | expected [5, 5, 5, 6, 6, 6] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A4.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A4.average_order | band | expected en=310 ru=7142.86 | tolerance ±20 % | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A4.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A4.terms_days | expected en=15 ru=14 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A4.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%');

-- acct.A4.vehicles | expected 8 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A4.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%');

-- acct.A4.shop | expected "east" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A4.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- acct.A5.visits | expected [7, 1, 0, 0, 0, 0] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A5.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A5.average_order | band | expected en=520 ru=12000.0 | tolerance ±20 % | A5: since the purchase | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A5.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A5.terms_days | expected 30 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A5.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%');

-- acct.A5.vehicles | expected 11 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A5.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%');

-- acct.A5.shop | expected "west" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A5.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- acct.A6.visits | expected [8, 6, 4, 3, 2, 1] | tolerance exact | blocks b1..b5 exact; the earlier mean within 0.5
-- want: near(row['before_t150_per_block'], L[0], abs=0.5) and [row[f'b{i}'] for i in range(1, 6)] == L[1:]
SELECT 'acct.A6.visits' AS ledger_key,
       round(count(*) FILTER (WHERE o.opened_at <= :'T'::timestamp - interval '150 days'
             AND o.opened_at > greatest(:'T'::timestamp - interval '24 months', (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))))
             / NULLIF(extract(epoch FROM (:'T'::timestamp - interval '150 days') - greatest(:'T'::timestamp - interval '24 months',
                 (SELECT min(x.opened_at) FROM shop.repair_order x WHERE x.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%')))) / 86400 / 30, 0), 1) AS before_t150_per_block,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '150 days' AND o.opened_at <= :'T'::timestamp - interval '120 days') AS b1,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '120 days' AND o.opened_at <= :'T'::timestamp - interval '90 days') AS b2,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '90 days' AND o.opened_at <= :'T'::timestamp - interval '60 days') AS b3,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '60 days' AND o.opened_at <= :'T'::timestamp - interval '30 days') AS b4,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS b5
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%') AND o.status NOT IN ('declined', 'void') AND o.order_type = 'customer_pay';

-- acct.A6.average_order | band | expected en=450 ru=10380.95 | tolerance ±20 % | definition: mean of total - tax_total over the account's customer-pay orders invoiced or paid | window: opened in the 12 months before T | unit: USD (en), RUB (ru) per order | tax: before tax
-- want: band(value, L * 0.8, L * 1.2)
SELECT 'acct.A6.average_order' AS ledger_key, round(avg(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%') AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.A6.terms_days | expected 30 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A6.terms_days' AS ledger_key, payment_terms_days AS value FROM shop.customer WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%');

-- acct.A6.vehicles | expected 10 | tolerance exact
-- want: same(value, L)
SELECT 'acct.A6.vehicles' AS ledger_key, count(*) AS value FROM shop.vehicle WHERE customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%');

-- acct.A6.shop | expected "main" | tolerance exact | the short name of the shop
-- want: value == V('geo.short_name')[L]
SELECT 'acct.A6.shop' AS ledger_key, l.name AS value FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%') GROUP BY l.name ORDER BY count(*) DESC LIMIT 1;

-- kb.acct.credit_limits | expected en={"A1": 30000, "A2": 20000, "A3": 5000, "A4": 5000, "A5": 7500, "A6": 7500} ru={"A1": 700000, "A2": 450000, "A3": 120000, "A4": 120000, "A5": 180000, "A6": 180000} | tolerance exact
-- want: value is not None and len(value.split('; ')) == len(L) and dict((p.rsplit(' ', 1)[0], float(p.rsplit(' ', 1)[1])) for p in value.split('; ')) == L
SELECT 'kb.acct.credit_limits' AS ledger_key, string_agg(k || ' ' || credit_limit, '; ' ORDER BY k) AS value
FROM (SELECT c.credit_limit, coalesce(CASE WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%' THEN 'A1' WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%' THEN 'A2' WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%' THEN 'A3' WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%' THEN 'A4' WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%' THEN 'A5' WHEN c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%' THEN 'A6' END, c.name) AS k FROM shop.customer c WHERE c.credit_limit IS NOT NULL) x;

-- acct.small.terms | expected "the small business customers pay at the counter: no terms, no statement. Only A1 to A6 are billed on terms" | tolerance exact | expected 6: only A1 to A6 are billed on terms
-- want: value == 6
SELECT 'acct.small.terms' AS ledger_key, count(*) AS value FROM shop.customer WHERE payment_terms_days IS NOT NULL;

-- acct.small.orders_share | expected 1.4 | tolerance ±0.5, at least 358 cases
-- want: near(value, L, abs=0.5)
SELECT 'acct.small.orders_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE c.kind = 'company' AND c.payment_terms_days IS NULL) / count(*), 2) AS value
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- acct.six.orders_share_now | band | expected en=7.8 ru=5.04 | tolerance 2 to 15, whatever the season | full size only | the six's visits over all orders; a warranty comeback is not a visit (`acct.*.visits` count none) | definition: orders of the six accounts on terms, warranty comebacks left out, over all orders not declined or void | window: opened in the last 30 days | unit: % of orders | tax: none | eval_answer: false
-- want: band(value, 2, 15)
SELECT 'acct.six.orders_share_now' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.order_type <> 'warranty' AND o.customer_id IN ((SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '30 days';

-- acct.six.orders_share_before | band | expected en=9.28 ru=8.85 | tolerance 2 to 15, whatever the season | full size only | the six's visits over all orders; a warranty comeback is not a visit (`acct.*.visits` count none) | definition: orders of the six accounts on terms, warranty comebacks left out, over all orders not declined or void | window: opened from T-180 to T-150 days | unit: % of orders | tax: none | eval_answer: false
-- want: band(value, 2, 15)
SELECT 'acct.six.orders_share_before' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.order_type <> 'warranty' AND o.customer_id IN ((SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '180 days' AND o.opened_at <= :'T'::timestamp - interval '150 days';

-- acct.six.revenue_share_now | band | expected en=6.59 ru=6.61 | tolerance 2 to 15, whatever the season | full size only | definition: total - tax_total of the six accounts' customer-pay orders invoiced or paid over all such orders | window: opened in the last 30 days | unit: % of revenue | tax: before tax | eval_answer: false
-- want: band(value, 2, 15)
SELECT 'acct.six.revenue_share_now' AS ledger_key,
       round(100.0 * sum(o.total - o.tax_total) FILTER (WHERE o.customer_id IN ((SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))) / sum(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '30 days';

-- acct.six.revenue_share_before | band | expected en=8.12 ru=8.16 | tolerance 2 to 15, whatever the season | full size only | definition: total - tax_total of the six accounts' customer-pay orders invoiced or paid over all such orders | window: opened from T-180 to T-150 days | unit: % of revenue | tax: before tax | eval_answer: false
-- want: band(value, 2, 15)
SELECT 'acct.six.revenue_share_before' AS ledger_key,
       round(100.0 * sum(o.total - o.tax_total) FILTER (WHERE o.customer_id IN ((SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))) / sum(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '180 days' AND o.opened_at <= :'T'::timestamp - interval '150 days';

-- acct.big_two_share | band | expected en=5.53 ru=5.55 | tolerance 2 to 15, whatever the season | full size only | definition: total - tax_total at the company-account price class over all customer-pay orders invoiced or paid | window: opened in the last 30 days | unit: % of revenue | tax: before tax
-- want: band(value, 2, 15)
SELECT 'acct.big_two_share' AS ledger_key,
       round(100.0 * sum(o.total - o.tax_total) FILTER (WHERE c.price_class = 'company_account') / sum(o.total - o.tax_total), 2) AS value
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at > :'T'::timestamp - interval '30 days';

-- acct.A1.days_to_pay | expected en={"until": 30, "last_three_paid": [38, 44, 51], "rule": "statements are issued on the first open day of a month for the month before. The newest statement that can be paid in 51 days by T-1 day is paid in 51; the two before it in 44 and 38; older ones in 28 to 32. Newer ones are unpaid at T: overdue once past 30 days"} ru={"until": 30, "late": 50, "rule": "one invoice per order, issued when the order closes. An invoice issued x days before T is paid after 30 days for x of 150 or more, after 30 + 20 * (150 - x) / 90 days for x from 150 down to 60, and is unpaid at T for x under 60 (overdue once past 30 days)"} | tolerance ±3 days | en: 28 to 32 on older statements, then 38, 44, 51, then unpaid and overdue; ru: the formula of the row by invoice age
-- want: value is not None and (all((r == 'unpaid, ' + ('overdue' if (a['T'].date() - d).days > L['until'] else 'sent')) if i >= n else near(r, L['last_three_paid'][i - n + 3], abs=3) if i >= n - 3 else near(r, L['until'], abs=2) for ps in [[(date.fromisoformat(p.split(': ', 1)[0]), p.split(': ', 1)[1]) for p in value.split('; ')]] for n in [sum(d + timedelta(L['last_three_paid'][-1]) <= a['T'].date() - timedelta(1) for d, _ in ps)] for i, (d, r) in enumerate(ps)) if cfg == 'en' else all((r == 'unpaid, ' + ('overdue' if x > L['until'] else 'sent')) if x < 60 else near(r, L['until'] + (L['late'] - L['until']) * (150 - min(x, 150)) / 90, abs=3) for p in value.split('; ') for x in [(a['T'].date() - date.fromisoformat(p.split(': ', 1)[0])).days] for r in [p.split(': ', 1)[1]]))
SELECT 'acct.A1.days_to_pay' AS ledger_key,
       string_agg(s.issued_on || ': ' || coalesce((p.received_at::date - s.issued_on)::text, 'unpaid, ' || s.status), '; ' ORDER BY s.issued_on) AS value
FROM shop.statement s LEFT JOIN shop.payment p ON p.statement_id = s.statement_id AND p.kind = 'payment'
WHERE s.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Nickajack Delivery' ELSE 'Симбирский гонец' END || '%') AND s.issued_on > :'T'::date - 210;

-- acct.others_pay_on_time | expected "A2, A3, A4 and A6 pay inside their terms on every bill (erp.statement.pay_day); A5's last bill is disputed and unpaid; no account at east has a bill overdue at T" | tolerance exact | expected 0, 1, 1, 0
-- want: [row['late_bills_of_a2_a3_a4_a6'], row['a5_unpaid'], row['a5_disputed'], row['east_overdue']] == [0, 1, 1, 0]
SELECT 'acct.others_pay_on_time' AS ledger_key,
       count(*) FILTER (WHERE s.customer_id IN ((SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Moccasin Bend Janitorial Services' ELSE 'Чистый Венец' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Missionary Ridge Driving School' ELSE 'Автошкола «Первая передача»' END || '%'), (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%'))
             AND (s.status = 'overdue' OR EXISTS (SELECT 1 FROM shop.payment p WHERE p.statement_id = s.statement_id AND p.received_at::date > s.due_on))) AS late_bills_of_a2_a3_a4_a6,
       count(*) FILTER (WHERE s.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND s.status <> 'paid') AS a5_unpaid,
       count(*) FILTER (WHERE s.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND s.dispute_note IS NOT NULL) AS a5_disputed,
       count(*) FILTER (WHERE s.status = 'overdue' AND s.customer_id IN (SELECT customer_id FROM shop.customer WHERE created_location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END))) AS east_overdue
FROM shop.statement s;

-- acct.ru_documents | expected en="a monthly statement per account" ru="one invoice with its closing act per order (statement rows hold one order each); a reconciliation on request" | tolerance exact | ru: several = 1 (the combined invoice); en: one statement per account per month with orders
-- want: row['statements'] > 0 and (row['statements_with_several_orders'] == 1 if cfg == 'ru' else row['duplicate_account_months'] == 0)
SELECT 'acct.ru_documents' AS ledger_key,
       count(*) FILTER (WHERE n > 1) AS statements_with_several_orders,
       count(*) AS statements,
       count(*) - count(DISTINCT (customer_id, date_trunc('month', issued_on))) AS duplicate_account_months
FROM (SELECT s.statement_id, s.customer_id, s.issued_on, count(o.repair_order_id) AS n FROM shop.statement s LEFT JOIN shop.repair_order o ON o.statement_id = s.statement_id GROUP BY s.statement_id) x;

-- acct.A2.weekly_slot | expected {"day": "Monday 07:30 (en), Monday 09:00 (ru)", "vans": 5} | tolerance exact | every week five vans at opening (Tuesday after a holiday Monday)
-- want: row['weeks_with_a_slot'] > 0 and row['mondays_with_five'] == row['weeks_with_a_slot'] == (date.fromisoformat(row['last_week']) - date.fromisoformat(row['first_week'])).days // 7 + 1 and row['start_times'] == L['day'].split(', ')[0 if cfg == 'en' else 1].split(' ')[1] + ':00' and (row['tuesday_slot_mondays'] or '') == ', '.join(str(d) for d in a['closed_mondays'] if row['first_week'] <= str(d) <= row['last_week'])
SELECT 'acct.A2.weekly_slot' AS ledger_key,
       count(*) FILTER (WHERE n = 5) AS mondays_with_five, count(*) AS weeks_with_a_slot, min(first_start) AS earliest_start_time,
       (SELECT string_agg(DISTINCT a.starts_at::time::text, ', ') FROM shop.appointment a WHERE a.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%') AND a.source = 'messenger' AND extract(isodow FROM a.starts_at) IN (1, 2)) AS start_times,
       min(wk)::date AS first_week, max(wk)::date AS last_week,
       string_agg(wk::date::text, ', ' ORDER BY wk) FILTER (WHERE on_tuesday) AS tuesday_slot_mondays
FROM (SELECT date_trunc('week', a.starts_at) AS wk, count(*) AS n, min(a.starts_at::time) AS first_start, bool_and(extract(isodow FROM a.starts_at) = 2) AS on_tuesday
      FROM shop.appointment a WHERE a.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Millsaps Heating & Plumbing' ELSE 'Тёплый контур' END || '%') AND a.source = 'messenger' AND extract(isodow FROM a.starts_at) IN (1, 2)
      GROUP BY 1) x;

-- s1.a5 | expected {"comebacks": 2, "comeback_orders_opened": ["the Tuesday of week T-26", "the Tuesday of week T-22"], "comebacks_are": "pad jobs fitted by slot 27 with the cheap brand", "last_visit": "the Thursday of week T-20", "miss_days_after_the_call": [1, 6, 9], "complaint_call": "the Tuesday of week T-19, answered by slot 22, existing job, no score, callback promised and not kept", "misses": 3, "miss_span_days": 9, "miss_first_desks": [302, 303, 302], "answered_calls_after": 0, "disputed_bill": "the statement (en) or invoice (ru) that holds the second comeback's first order", "miss_first_desks_ru": "the … | tolerance exact | 2 comebacks on the Tuesdays of weeks T-26 and T-22; last visit the Thursday of week T-20
-- want: row['comebacks'] == L['comebacks'] and row['comeback_dates'] == ', '.join(str(d) for d in a['a5_comebacks']) and same(row['last_visit'], a['a5_last_visit'])
SELECT 's1.a5' AS ledger_key,
       (SELECT count(*) FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND o.comeback_of_id IS NOT NULL) AS comebacks,
       (SELECT string_agg(o.opened_at::date::text, ', ' ORDER BY o.opened_at) FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND o.comeback_of_id IS NOT NULL) AS comeback_dates,
       (SELECT max(o.opened_at)::date FROM shop.repair_order o WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Cumberland Bend Electric' ELSE 'Идель-Электромонтаж' END || '%') AND o.status <> 'void') AS last_visit;

-- s1.a6 | expected {"new_contact_from": "P (the day of the price rise)", "estimates_waited_two_days_or_more": 5, "estimates_declined_or_expired": 4, "price_calls": 2, "quote_chat_waited_days": 2} | tolerance exact | expected 5 and 4
-- want: row['estimates_waited_two_days'] == L['estimates_waited_two_days_or_more'] and row['then_declined_or_expired'] == L['estimates_declined_or_expired']
SELECT 's1.a6' AS ledger_key,
       count(*) FILTER (WHERE first_decision - o.opened_at >= interval '2 days') AS estimates_waited_two_days,
       count(*) FILTER (WHERE first_decision - o.opened_at >= interval '2 days' AND o.status = 'declined') AS then_declined_or_expired
FROM shop.repair_order o
CROSS JOIN LATERAL (SELECT min(j.decided_at) AS first_decision FROM shop.order_job j WHERE j.repair_order_id = o.repair_order_id) d
WHERE o.customer_id = (SELECT customer_id FROM shop.customer WHERE payment_terms_days IS NOT NULL AND name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%') AND o.opened_at >= :'P'::date;

-- kb.estimate_validity_days | expected en=30 ru=14 | tolerance value at most the row (en 30, ru 14)
-- want: value is not None and value <= L
SELECT 'kb.estimate_validity_days' AS ledger_key, max(h.changed_at::date - o.opened_at::date) AS value
FROM shop.repair_order o JOIN shop.order_status_history h ON h.repair_order_id = o.repair_order_id AND h.status = 'declined';

-- pay.mix | expected en={"card": 73, "cash": 17, "check": 1, "account": 9} ru={"card": 54, "cash": 14, "fast payment (СБП)": 23, "invoice (bank transfer)": 9} | tolerance ±2.0, at least 25 cases | en account = statement-settled; ru invoice = bank_transfer plus statement-settled
-- want: value is not None and all(sorted(m) == sorted(L) and all(near(m[k], L[k], abs=2) for k in L) for p in [dict((x.rsplit(' ', 1)[0], float(x.rsplit(' ', 1)[1])) for x in value.split(', '))] for m in [p if cfg == 'en' else {'card': p.get('card'), 'cash': p.get('cash'), 'fast payment (СБП)': p.get('fast_payment'), 'invoice (bank transfer)': p.get('bank_transfer', 0) + p.get('account', 0)} if set(p) <= {'card', 'cash', 'fast_payment', 'bank_transfer', 'account'} else {}])
SELECT 'pay.mix' AS ledger_key, string_agg(m || ' ' || pct, ', ' ORDER BY pct DESC) AS value
FROM (SELECT m, round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
      FROM (SELECT (CASE WHEN o.statement_id IS NOT NULL THEN 'account'
      ELSE (SELECT p.method FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' ORDER BY p.amount DESC LIMIT 1) END) AS m FROM shop.repair_order o
            WHERE o.status = 'paid' AND o.order_type = 'customer_pay' AND o.opened_at > :'T'::timestamp - interval '12 months') y
      GROUP BY m) x;

-- pay.cash_share | expected en=17 ru=14 | tolerance ±2 points
-- want: near(value, L, abs=2)
SELECT 'pay.cash_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE (CASE WHEN o.statement_id IS NOT NULL THEN 'account'
      ELSE (SELECT p.method FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' ORDER BY p.amount DESC LIMIT 1) END) = 'cash') / count(*), 1) AS value
FROM shop.repair_order o WHERE o.status IN ('paid', 'void') AND o.order_type = 'customer_pay' AND o.advisor_id <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment')
  AND o.opened_at > :'T'::timestamp - interval '12 months';

-- pay.background_discount_share | expected 3.0 | tolerance ±1.0, at least 167 cases | full size only
-- want: near(value, L, abs=1.0)
SELECT 'pay.background_discount_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.discount_total >= 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_total > 0) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o WHERE EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.advisor_id <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)
  AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date;

-- pay.void_rate | expected 0.3 | tolerance ±0.2, at least 1667 cases
-- want: near(value, L, abs=0.2)
SELECT 'pay.void_rate' AS ledger_key, round(100.0 * count(*) FILTER (WHERE o.status = 'void') / count(*), 2) AS value
FROM shop.repair_order o WHERE o.advisor_id <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END);

-- pay.till_exact_days | expected 92 | tolerance ±3.0, at least 63 cases
-- want: near(value, L, abs=3.0)
SELECT 'pay.till_exact_days' AS ledger_key, round(100.0 * count(*) FILTER (WHERE d.difference = 0) / count(*), 1) AS value
FROM shop.cash_drawer_close d WHERE d.business_date > :'T'::date - 365;

-- kb.till.floats | expected en={"main": 200, "east": 150, "west": 150} ru={"main": 5000, "east": 3000, "west": 3000} | tolerance exact
-- want: value is not None and sorted((p.rsplit(' ', 1)[0], float(p.rsplit(' ', 1)[1])) for p in value.split('; ')) == sorted((V('geo.short_name')[s], L[s]) for s in L)
SELECT 'kb.till.floats' AS ledger_key, string_agg(DISTINCT l.name || ' ' || d.float_amount, '; ') AS value
FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id;

-- kb.till.report_over | expected en=5 ru=100 | tolerance exact | value = closes beyond the reporting limit by anyone but F1; expected 0
-- want: value == 0
SELECT 'kb.till.report_over' AS ledger_key,
       count(*) FILTER (WHERE abs(d.difference) > (CASE :'cfg' WHEN 'en' THEN 5 ELSE 100 END) AND d.closed_by_id <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)) AS value
FROM shop.cash_drawer_close d;

-- kb.till.west_since_the_rule | expected en={"before": "one person counted; banking on Monday and Thursday", "since": "two counts; banking every working day"} ru={"before": "an open stockroom with a notebook; one count; banking on Monday and Thursday", "since": "parts issued only against an order line; clocked job time compared with sold hours every evening; stock issues reconciled with sales weekly; two counts; banking every day; consumables written off weekly over the manager's signature"} | tolerance exact | expected 0
-- want: value == 0
SELECT 'kb.till.west_since_the_rule' AS ledger_key,
       count(*) FILTER (WHERE d.second_counter_id IS NULL) AS west_closes_since_rule_without_second_count
FROM shop.cash_drawer_close d WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND d.business_date >= :'rule_on'::date;

-- s2.f1.orders | band | expected en=381.0 ru=423.4 | tolerance ±10 % | the visits he wrote, voids among them; a declined estimate is not a visit (the ledger's figure is the shop's orders a month × his share) | definition: orders the fired advisor wrote, declined estimates left out | window: his 26 weeks to the firing | unit: orders | tax: none
-- want: band(value, L * 0.9, L * 1.1)
SELECT 's2.f1.orders' AS ledger_key, count(*) AS value FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND o.status <> 'declined';

-- s2.f1.cash_orders | expected 160 | tolerance exact at full size; × 0.25 at small size
-- want: same(value, L)
SELECT 's2.f1.cash_orders' AS ledger_key, count(*) AS value FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash');

-- s2.f1.discounted | expected 35 | tolerance exact
-- want: same(value, L)
SELECT 's2.f1.discounted' AS ledger_key, count(*) AS value FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.discount_total >= 0.15 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_approved_by_id IS NULL;

-- s2.f1.discount_share | expected 21.9 | tolerance ±1 point | full size only
-- want: near(value, L, abs=1)
SELECT 's2.f1.discount_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.discount_total >= 0.15 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_approved_by_id IS NULL) / count(*), 1) AS value
FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash');

-- s2.f1.discount_total | expected en=4100 ru=96000 | tolerance exact
-- want: same(value, L)
SELECT 's2.f1.discount_total' AS ledger_key, sum(o.discount_total) AS value FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.discount_total >= 0.15 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_approved_by_id IS NULL;

-- s2.f1.second | expected en={"what": "orders voided after cash was taken", "count": 14, "total": 5600} ru={"what": "parts issued from stock under his name with no sale (stock movements with no order line)", "count": 46, "total": 118000} | tolerance exact
-- want: value is not None and same(value.split(' ')[0], L['count']) and value.split(' ')[1] == ('voids,' if cfg == 'en' else 'issues,') and same(value.split(', ')[1], L['total'])
SELECT 's2.f1.second' AS ledger_key,
       CASE :'cfg' WHEN 'en' THEN (SELECT count(*) || ' voids, ' || sum(o.total) FROM shop.repair_order o
                                   WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.status = 'void' AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'))
       ELSE (SELECT count(*) || ' issues, ' || sum(-m.quantity * m.unit_cost) FROM shop.stock_movement m
             WHERE m.kind = 'issue' AND m.order_part_id IS NULL AND m.employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)) END AS value;

-- s2.f1.third | expected en={"what": "days the till was short when he closed it", "count": 19, "of_days_he_closed": 65, "total": 1700} ru={"what": "orders with mechanics' clocked time far above the hours sold (work done past the order)", "count": 22, "hours": 61, "total": 107360} | tolerance exact | en short days -1,700 in all; ru 61 hours = 107,360 at 1,760
-- want: value is not None and (same(value.split(' ')[0], L['count']) and same(value.split(' ')[4], L['of_days_he_closed']) and same(value.split(', ')[1], -L['total']) if cfg == 'en' else same(value.split(' ')[0], L['count']) and same(value.split(', ')[1].split(' ')[0], L['hours']))
SELECT 's2.f1.third' AS ledger_key,
       CASE :'cfg' WHEN 'en' THEN (SELECT count(*) FILTER (WHERE d.difference <= -20) || ' short days of ' || count(*) || ' closed, '
                                          || coalesce(sum(d.difference) FILTER (WHERE d.difference <= -20), 0)
                                   FROM shop.cash_drawer_close d WHERE d.closed_by_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END))
       ELSE (SELECT count(*) || ' orders, ' || round(sum(over_h), 1) || ' hours'
             FROM (SELECT o.repair_order_id,
                          (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
                        - (SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h
                   FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date) x WHERE over_h > 1) END AS value;

-- s2.total | expected en=11400 ru=321360 | tolerance exact | the three components summed; an estimate, not a reading
-- want: same(value, L)
SELECT 's2.total' AS ledger_key,
       round(CASE :'cfg' WHEN 'en' THEN
            (SELECT sum(o.discount_total) FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.discount_total >= 0.15 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_approved_by_id IS NULL)
          + (SELECT sum(o.total) FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.status = 'void' AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'))
          - (SELECT sum(d.difference) FROM shop.cash_drawer_close d WHERE d.closed_by_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND d.difference <= -20)
       ELSE
            (SELECT sum(o.discount_total) FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.discount_total >= 0.15 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_approved_by_id IS NULL)
          + (SELECT sum(-m.quantity * m.unit_cost) FROM shop.stock_movement m WHERE m.kind = 'issue' AND m.order_part_id IS NULL AND m.employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END))
          + (SELECT sum(x.over_h * x.rate) FROM (SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
          - (SELECT coalesce(sum(l.hours), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h, (SELECT r.rate FROM shop.labor_rate r WHERE r.location_id = o.location_id AND r.price_class = 'standard'
          AND r.valid_from <= o.opened_at::date AND (r.valid_to IS NULL OR r.valid_to >= o.opened_at::date)) AS rate FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END) AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date) x WHERE x.over_h > 1)
       END, 2) AS value;

-- s2.west.discount_share_before | expected en=13.42 ru=13.84 | tolerance ±1 point | full size only
-- want: near(value, L, abs=1)
SELECT 's2.west.discount_share_before' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.discount_total >= 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_total > 0) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.opened_at >= :'s2_start'::date AND o.opened_at < :'fired'::date;

-- s2.west.discount_share_after | expected en=2.44 ru=2.67 | tolerance ±1 point | full size only
-- want: near(value, L, abs=1)
SELECT 's2.west.discount_share_after' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.discount_total >= 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_total > 0) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.opened_at >= :'fired'::date;

-- s2.west.discounts_after | expected {"orders": 4, "approved_by_22": 2, "unapproved_by_23": 2, "unapproved_pct_each": 12, "unapproved_when": "en: the Wednesday of week T-3 and the Thursday of week T-1. ru: slot 23's last working day on or before each. Both in the last 30 days, each inside the week of the Friday list that shows it"} | tolerance exact | 4, 2, 2; the Wednesday of week T-3 and the Thursday of week T-1
-- want: row['orders'] == L['orders'] and row['approved_by_22'] == L['approved_by_22'] and row['unapproved_by_23'] == L['unapproved_by_23'] and row['unapproved_days'] == ', '.join(str(d) for d in a['s2_discounts']) and each(row['unapproved_pcts'], [L['unapproved_pct_each']] * 2)
SELECT 's2.west.discounts_after' AS ledger_key,
       count(*) AS orders,
       count(*) FILTER (WHERE o.discount_approved_by_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Dale' ELSE 'Ринат' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hutchins' ELSE 'Галиев' END)) AS approved_by_22,
       count(*) FILTER (WHERE o.discount_approved_by_id IS NULL AND o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Chad' ELSE 'Вячеслав' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Binkley' ELSE 'Крюков' END)) AS unapproved_by_23,
       string_agg(o.opened_at::date::text, ', ' ORDER BY o.opened_at) FILTER (WHERE o.discount_approved_by_id IS NULL) AS unapproved_days,
       string_agg(round(100 * o.discount_total / (o.labor_total + o.parts_total + o.sublet_total + o.fees_total))::text, ', ' ORDER BY o.opened_at) FILTER (WHERE o.discount_approved_by_id IS NULL) AS unapproved_pcts
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash') AND o.discount_total >= 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AND o.discount_total > 0 AND o.opened_at >= :'fired'::date;

-- s2.walkin | expected {"fixed_orders": 49, "background_orders_at_full_size": 191, "by_advisor_at_full_size": {"F1": 150, "23": 60, "24": 30}} | tolerance exact | F1 150, slot 23 60, slot 24 30 at full size
-- want: value == ', '.join(f"{n} {L['by_advisor_at_full_size'][k]}" for k, n in zip(('F1', '23', '24'), ('Lassiter', 'Binkley', 'Bolden') if cfg == 'en' else ('Назаров', 'Крюков', 'Шакирова')))
SELECT 's2.walkin' AS ledger_key, string_agg(e.last_name || ' ' || n, ', ' ORDER BY n DESC) AS value
FROM (SELECT o.advisor_id, count(*) AS n FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
      WHERE c.name = CASE :'cfg' WHEN 'en' THEN 'WALK-IN CUSTOMER' ELSE 'Розничный покупатель' END GROUP BY o.advisor_id) x JOIN shop.employee e ON e.employee_id = x.advisor_id;

-- s2.walkin.total | expected 240 | tolerance 240 at full size; 49 + 191 × 0.25 at small size
-- want: same(value, L)
SELECT 's2.walkin.total' AS ledger_key, count(*) AS value FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.name = CASE :'cfg' WHEN 'en' THEN 'WALK-IN CUSTOMER' ELSE 'Розничный покупатель' END;

-- parts.po_per_order | expected 0.6 | tolerance within 5 %
-- want: near(value, L, pct=5)
SELECT 'parts.po_per_order' AS ledger_key,
       round((SELECT count(*) FROM shop.purchase_order)::numeric / (SELECT count(*) FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void')), 3) AS value;

-- parts.on_time.V1 | expected 93 | tolerance ±2.0, at least 72 cases
-- want: near(value, L, abs=2.0)
SELECT 'parts.on_time.V1' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / count(*), 1) AS value
FROM shop.purchase_order po WHERE po.vendor_id = (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sequoyah Parts Supply' ELSE 'АвтоДеталь-Венец' END || '%') AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL;

-- parts.on_time.V2 | expected 62 | tolerance ±3.0, at least 17 cases
-- want: near(value, L, abs=3.0)
SELECT 'parts.on_time.V2' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / count(*), 1) AS value
FROM shop.purchase_order po WHERE po.vendor_id = (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Harpeth Valley Parts Supply' ELSE 'Казань-АвтоСнаб' END || '%') AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL;

-- parts.on_time.V3 | expected en=88 ru=87 | tolerance ±4.0 | each vendor its own share
-- want: near(value, L, abs=4.0)
SELECT 'parts.on_time.V3' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / NULLIF(count(*), 0), 1) AS value
FROM shop.purchase_order po WHERE po.vendor_id = (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Ridge & Valley Import Parts' ELSE 'Симбирск-Комплект' END || '%') AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL;

-- parts.on_time.V4 | expected en=90 ru=91 | tolerance ±4.0 | each vendor its own share
-- want: near(value, L, abs=4.0)
SELECT 'parts.on_time.V4' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / NULLIF(count(*), 0), 1) AS value
FROM shop.purchase_order po WHERE po.vendor_id = (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Hiwassee Battery & Electric' ELSE 'ОйлТрейд-Симбирск' END || '%') AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL;

-- parts.on_time.V5 | expected en=84 ru=80 | tolerance ±4.0 | each vendor its own share
-- want: near(value, L, abs=4.0)
SELECT 'parts.on_time.V5' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / NULLIF(count(*), 0), 1) AS value
FROM shop.purchase_order po WHERE po.vendor_id = (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Tellico Tire Distributors' ELSE 'ШинТорг-Волга' END || '%') AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL;

-- parts.wait_over_a_day.west | expected 14 | tolerance ±2.0, at least 36 cases
-- want: near(value, L, abs=2.0)
SELECT 'parts.wait_over_a_day.west' AS ledger_key, round(100.0 * count(*) FILTER (WHERE (SELECT coalesce(sum(extract(epoch FROM (coalesce(nx.changed_at, :'T'::timestamp) - h.changed_at)) / 86400), 0)
          FROM shop.order_status_history h
          LEFT JOIN LATERAL (SELECT min(h2.changed_at) AS changed_at FROM shop.order_status_history h2
                             WHERE h2.repair_order_id = h.repair_order_id AND h2.changed_at > h.changed_at) nx ON true
          WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts') > 1) / count(*), 1) AS value
FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND o.status NOT IN ('declined', 'void') AND o.opened_at >= :'bought'::date;

-- parts.wait_over_a_day.home | expected 4 | tolerance ±1.0, at least 125 cases
-- want: near(value, L, abs=1.0)
SELECT 'parts.wait_over_a_day.home' AS ledger_key, round(100.0 * count(*) FILTER (WHERE (SELECT coalesce(sum(extract(epoch FROM (coalesce(nx.changed_at, :'T'::timestamp) - h.changed_at)) / 86400), 0)
          FROM shop.order_status_history h
          LEFT JOIN LATERAL (SELECT min(h2.changed_at) AS changed_at FROM shop.order_status_history h2
                             WHERE h2.repair_order_id = h.repair_order_id AND h2.changed_at > h.changed_at) nx ON true
          WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts') > 1) / count(*), 1) AS value
FROM shop.repair_order o WHERE o.location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END)) AND o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- parts.returned_share | expected en=6 ru=4 | tolerance ±1.5, at least 125 cases
-- want: near(value, L, abs=1.5)
SELECT 'parts.returned_share' AS ledger_key,
       round(100.0 * (SELECT count(DISTINCT purchase_order_line_id) FROM shop.part_return) / (SELECT count(*) FROM shop.purchase_order_line), 2) AS value;

-- parts.typed_by_hand | expected {"west": 9, "home": 1} | tolerance ±1.5, at least 500 cases
-- want: near(row['west'], L['west'], abs=1.5) and near(row['home'], L['home'], abs=1.5)
SELECT 'parts.typed_by_hand' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE p.part_id IS NULL AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)) / NULLIF(count(*) FILTER (WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)), 0), 2) AS west,
       round(100.0 * count(*) FILTER (WHERE p.part_id IS NULL AND o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)) / NULLIF(count(*) FILTER (WHERE o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)), 0), 2) AS home
FROM shop.order_part p JOIN shop.order_job j ON j.order_job_id = p.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE o.opened_at > :'T'::timestamp - interval '12 months';

-- s6.brand | expected en="Calder ValueStop" ru="BREMHOF" | tolerance exact | lines bought (a part issued to the line), lines_off_west 0, lines_not_from_v2 0
-- want: row['lines'] > 0 and row['lines_off_west'] == 0 and row['lines_not_from_v2'] == 0
SELECT 's6.brand' AS ledger_key,
       count(*) AS lines, count(*) FILTER (WHERE o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)) AS lines_off_west,
       count(*) FILTER (WHERE p.vendor_id IS DISTINCT FROM (SELECT vendor_id FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Harpeth Valley Parts Supply' ELSE 'Казань-АвтоСнаб' END || '%')) AS lines_not_from_v2
FROM shop.order_part p JOIN shop.order_job j ON j.order_job_id = p.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END
  AND EXISTS (SELECT 1 FROM shop.stock_movement m WHERE m.order_part_id = p.order_part_id);

-- s6.west_orders | band | expected en=2670 ru=2967 | tolerance ±10 % at full size | a count over a window that moves with the season
-- want: band(value, L * 0.9, L * 1.1)
SELECT 's6.west_orders' AS ledger_key, count(*) AS value FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND o.status NOT IN ('declined', 'void');

-- s6.p27_pad_share | expected 60 | tolerance ±3.0, at least 17 cases
-- want: near(value, L, abs=3.0)
SELECT 's6.p27_pad_share' AS ledger_key, round(100.0 * count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)) / count(*), 1) AS value FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- s6.cheap_share | expected 45 | tolerance ±3.0, at least 17 cases
-- want: near(row['slot_27'], L, abs=3) and near(row['colleagues'], L, abs=3)
SELECT 's6.cheap_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE cheap AND tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)) / NULLIF(count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)), 0), 1) AS slot_27,
       round(100.0 * count(*) FILTER (WHERE cheap AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)) / NULLIF(count(*) FILTER (WHERE tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)), 0), 1) AS colleagues
FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END);

-- s6.rate.good.others | expected 2.0 | tolerance ±0.7, at least 250 cases
-- want: near(value, L, abs=0.7)
SELECT 's6.rate.good.others' AS ledger_key, round(100.0 * count(*) FILTER (WHERE back) / count(*), 2) AS value FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE NOT cheap AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- s6.rate.good.p27 | expected 5.0 | tolerance ±1.5, at least 100 cases
-- want: near(value, L, abs=1.5)
SELECT 's6.rate.good.p27' AS ledger_key, round(100.0 * count(*) FILTER (WHERE back) / count(*), 2) AS value FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE NOT cheap AND tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- s6.rate.cheap.p27 | expected 20.0 | tolerance ±3.0, at least 60 cases
-- want: near(value, L, abs=3.0)
SELECT 's6.rate.cheap.p27' AS ledger_key, round(100.0 * count(*) FILTER (WHERE back) / count(*), 2) AS value FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE cheap AND tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- s6.rate.cheap.others | expected 8.0 | tolerance ±3.0, at least 60 cases
-- want: near(value, L, abs=3.0)
SELECT 's6.rate.cheap.others' AS ledger_key, round(100.0 * count(*) FILTER (WHERE back) / count(*), 2) AS value FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE cheap AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- s6.pad_factor | expected 4 | tolerance 3 to 5 at full size
-- want: value is not None and 3 <= value <= 5
SELECT 's6.pad_factor' AS ledger_key,
       round((count(*) FILTER (WHERE back AND cheap)::numeric / NULLIF(count(*) FILTER (WHERE cheap), 0))
           / NULLIF(count(*) FILTER (WHERE back AND NOT cheap)::numeric / NULLIF(count(*) FILTER (WHERE NOT cheap), 0), 0), 2) AS value
FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj WHERE tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END);

-- s6.counts | expected en={"pad_jobs": 555, "p27_orders": 742, "p27_good": 183, "p27_cheap": 150, "p27_other": 409, "others_good": 122, "others_cheap": 100, "comebacks_p27_good": 9, "comebacks_p27_cheap": 30, "comebacks_others_cheap": 8, "comebacks_others_good_at_west": 2, "good_pad_jobs_not_27_all_shops": 3203, "comebacks_good_not_27_all_shops": 64} ru={"pad_jobs": 362, "p27_orders": 824, "p27_good": 119, "p27_cheap": 98, "p27_other": 607, "others_good": 80, "others_cheap": 65, "comebacks_p27_good": 6, "comebacks_p27_cheap": 20, "comebacks_others_cheap": 5, "comebacks_others_good_at_west": 2, "good_pad_jobs_not_27_all_shops": 1940, "comebacks_good_not_27_all_shops": 39} | tolerance scales: compare at full size | every count exact at full size; comebacks dealt round(n x rate) at small size
-- want: all(row[k] == L[k] for k in list(row)[1:])
SELECT 's6.counts' AS ledger_key,
       count(*) FILTER (WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END)) AS pad_jobs,
       count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap) AS p27_good, count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap AND back) AS comebacks_p27_good,
       count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND cheap) AS p27_cheap, count(*) FILTER (WHERE tech = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND cheap AND back) AS comebacks_p27_cheap,
       count(*) FILTER (WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND cheap) AS others_cheap, count(*) FILTER (WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND cheap AND back) AS comebacks_others_cheap,
       count(*) FILTER (WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap) AS others_good, count(*) FILTER (WHERE loc = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) AND tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap AND back) AS comebacks_others_good_at_west,
       count(*) FILTER (WHERE tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap) AS good_pad_jobs_not_27_all_shops, count(*) FILTER (WHERE tech <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END) AND NOT cheap AND back) AS comebacks_good_not_27_all_shops
FROM (SELECT j.order_job_id AS job, o.repair_order_id AS ord, o.location_id AS loc, l.technician_id AS tech,
         EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Calder ValueStop' ELSE 'BREMHOF' END) AS cheap,
         EXISTS (SELECT 1 FROM shop.repair_order cb JOIN shop.order_job cj ON cj.repair_order_id = cb.repair_order_id
                 JOIN shop.canned_job cc ON cc.canned_job_id = cj.canned_job_id
                 WHERE cb.comeback_of_id = o.repair_order_id AND cc.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')) AS back
  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
  JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
  WHERE o.order_type = 'customer_pay' AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors')
    AND (o.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END) OR o.opened_at >= :'bought'::date)) pj;

-- s6.rate.other_work.p27 | expected 3.0 | tolerance ±1.0, at least 167 cases
-- want: near(value, L, abs=1.0)
SELECT 's6.rate.other_work.p27' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.repair_order cb WHERE cb.comeback_of_id = o.repair_order_id)) / NULLIF(count(*), 0), 2) AS value
FROM shop.repair_order o
WHERE o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at >= :'bought'::date AND (SELECT l.technician_id FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND l.technician_id IS NOT NULL
          GROUP BY l.technician_id ORDER BY sum(l.hours) DESC, l.technician_id LIMIT 1) = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Derek' ELSE 'Виталий' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Hooper' ELSE 'Сомов' END)
  AND NOT EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
                  WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND c.code IN ('front_brake_pads', 'front_pads_rotors', 'rear_brake_pads', 'rear_pads_rotors'));

-- s6.waiting_at_t | expected {"west_days": [9, 6, 4, 2, 1], "main_days": [2, 1], "east_days": [1], "nine_days": "the named customer of named_customers.json, S6_waiting_nine_days; calendar days since the status was set; a count that lands on a day the shops are shut (en weekends and closed dates) is moved back to a full open day, for every car: the 9 then reads 10 or 11 and the others move likewise, so questions name 'the car that has waited longest'"} | tolerance exact | west 9, 6, 4, 2, 1; main 2, 1; east 1 (calendar days)
-- want: value == '; '.join(f"{V('geo.short_name')[s]}: {', '.join(str((a['T'].date() - d).days) for d in a['s6_since'][s])}" for s in ('main', 'east', 'west'))
SELECT 's6.waiting_at_t' AS ledger_key, string_agg(name || ': ' || days, '; ' ORDER BY location_id) AS value
FROM (SELECT location_id, name, string_agg(d::text, ', ' ORDER BY d DESC) AS days
      FROM (SELECT l.location_id, l.name, :'T'::date - (SELECT max(h.changed_at)::date FROM shop.order_status_history h
                   WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts') AS d
            FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id WHERE o.status = 'waiting_parts') w
      GROUP BY location_id, name) x;

-- s5.east_with_16 | expected en=63.4 ru=71.0 | tolerance ±4 points | days with an order of slot 16 = her working days
-- want: near(value, L, abs=4)
SELECT 's5.east_with_16' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.opened_at >= :'G'::date AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id)
  AND o.opened_at::date IN (SELECT DISTINCT x.opened_at::date FROM shop.repair_order x WHERE x.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Angie' ELSE 'Светлана' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Holloway' ELSE 'Демидова' END));

-- s5.east_without_16 | expected 52.0 | tolerance ±4 points
-- want: near(value, L, abs=4)
SELECT 's5.east_without_16' AS ledger_key, round(100.0 * count(*) FILTER (WHERE j.status = 'approved') / NULLIF(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0), 2) AS value
FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.opened_at >= :'G'::date AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id)
  AND o.opened_at::date NOT IN (SELECT DISTINCT x.opened_at::date FROM shop.repair_order x WHERE x.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Angie' ELSE 'Светлана' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Holloway' ELSE 'Демидова' END));

-- s5.order_value_drop | contrast | expected 40 % of the card's figure or more (the card: en 51.3, ru 1681) | full size only | the raised work sold per order at east, before tax, on her days less on the others: the rest of an order does not depend on the advisor
-- want: value is not None and value >= 0.4 * L
SELECT 's5.order_value_drop' AS ledger_key, round(avg(v.sold) FILTER (WHERE v.her_day) - avg(v.sold) FILTER (WHERE NOT v.her_day), 2) AS value
FROM (SELECT o.opened_at::date IN (SELECT DISTINCT x.opened_at::date FROM shop.repair_order x WHERE x.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Angie' ELSE 'Светлана' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Holloway' ELSE 'Демидова' END)) AS her_day,
             coalesce((SELECT sum(j.approved_amount) FROM shop.order_job j JOIN shop.inspection_item it ON it.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved'), 0)
               / (CASE WHEN o.tax_included THEN 1 + o.tax_rate / 100 ELSE 1 END) AS sold
      FROM shop.repair_order o WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid') AND o.opened_at >= :'G'::date) v;

-- s5.leave | expected {"who": 10, "from": "the Monday of week T-10", "to": "the Friday of week T-9", "orders_sent_to_east": 11, "wait_days_normal": 0.5, "wait_days_in_leave": 2.5, "recovered_share": 0.17} | tolerance exact | the 11 orders sent to east; the waits are s5.leave:wait_in_leave, s5.leave:wait_normal and s5.leave:waits
-- want: row['orders_sent_to_east'] == L['orders_sent_to_east']
SELECT 's5.leave' AS ledger_key,
       (SELECT count(*) FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
         WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND c.created_location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id JOIN shop.service_category sc ON sc.service_category_id = c.service_category_id
               WHERE j.repair_order_id = o.repair_order_id AND sc.code = 'diagnostics')
           AND o.opened_at::date BETWEEN :'leave_from'::date AND :'leave_to'::date) AS orders_sent_to_east;

-- s5.leave:wait_in_leave | band | expected 2.5 | tolerance ±0.75 days (about 30 orders: one order's wait spreads 1.4 days, their mean 0.26) | definition: mean days from opening to the first in_progress, main's orders with an approved diagnostic job (a declined one waits for nobody) | window: orders opened in the diagnostician's leave | unit: days | tax: none
-- want: band(value, V('s5.leave')['wait_days_in_leave'] - 0.75, V('s5.leave')['wait_days_in_leave'] + 0.75)
SELECT 's5.leave:wait_in_leave' AS ledger_key,
       (SELECT round(avg(extract(epoch FROM (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'in_progress') - o.opened_at) / 86400)::numeric, 2) FROM shop.repair_order o
         WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id JOIN shop.service_category sc ON sc.service_category_id = c.service_category_id
               WHERE j.repair_order_id = o.repair_order_id AND sc.code = 'diagnostics' AND j.status = 'approved') AND o.opened_at::date BETWEEN :'leave_from'::date AND :'leave_to'::date) AS value;

-- s5.leave:wait_normal | band | expected 0.5 | tolerance ±0.2 days | definition: mean days from opening to the first in_progress, main's orders with an approved diagnostic job | window: orders opened in the 12 months before T, outside the diagnostician's leave | unit: days | tax: none
-- want: band(value, V('s5.leave')['wait_days_normal'] - 0.2, V('s5.leave')['wait_days_normal'] + 0.2)
SELECT 's5.leave:wait_normal' AS ledger_key,
       (SELECT round(avg(extract(epoch FROM (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'in_progress') - o.opened_at) / 86400)::numeric, 2) FROM shop.repair_order o
         WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id JOIN shop.service_category sc ON sc.service_category_id = c.service_category_id
               WHERE j.repair_order_id = o.repair_order_id AND sc.code = 'diagnostics' AND j.status = 'approved') AND o.opened_at > :'T'::timestamp - interval '12 months'
           AND o.opened_at::date NOT BETWEEN :'leave_from'::date AND :'leave_to'::date) AS value;

-- s5.leave:waits | contrast | expected the wait in the leave three times the normal wait or more (the card: 2.5 days against 0.5) | main's orders with an approved diagnostic job, as s5.leave:wait_in_leave and s5.leave:wait_normal read them
-- want: row['in_leave'] is not None and row['normal'] is not None and row['in_leave'] >= 3 * row['normal']
SELECT 's5.leave:waits' AS ledger_key,
       (SELECT round(avg(extract(epoch FROM (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'in_progress') - o.opened_at) / 86400)::numeric, 2) FROM shop.repair_order o
         WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id JOIN shop.service_category sc ON sc.service_category_id = c.service_category_id
               WHERE j.repair_order_id = o.repair_order_id AND sc.code = 'diagnostics' AND j.status = 'approved') AND o.opened_at::date BETWEEN :'leave_from'::date AND :'leave_to'::date) AS in_leave,
       (SELECT round(avg(extract(epoch FROM (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'in_progress') - o.opened_at) / 86400)::numeric, 2) FROM shop.repair_order o
         WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id JOIN shop.service_category sc ON sc.service_category_id = c.service_category_id
               WHERE j.repair_order_id = o.repair_order_id AND sc.code = 'diagnostics' AND j.status = 'approved') AND o.opened_at > :'T'::timestamp - interval '12 months'
           AND o.opened_at::date NOT BETWEEN :'leave_from'::date AND :'leave_to'::date) AS normal;

-- volume.east.first_half_year.check_in_to_work | band | expected no design figure: the build's value is the outcome, in manifest.<cfg>.json | tolerance none: the band only bounds what the measure can read, 0 days to the window's 183 | definition: the highest monthly mean of days from an order's opening to its first in_progress at east; the third column names that month | window: orders opened from T-24 months to T-18 months, neither declined nor void | unit: days | tax: none | eval_answer: false
-- want: band(value, 0, 183)
SELECT 'volume.east.first_half_year.check_in_to_work' AS ledger_key, m.days AS value, m.month
FROM (SELECT to_char(date_trunc('month', o.opened_at), 'YYYY-MM') AS month,
             round(avg(extract(epoch FROM (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'in_progress') - o.opened_at) / 86400)::numeric, 2) AS days
      FROM shop.repair_order o
      WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END) AND o.status NOT IN ('declined', 'void')
        AND o.opened_at >= :'T'::timestamp - interval '24 months' AND o.opened_at < :'T'::timestamp - interval '18 months'
      GROUP BY 1) m
ORDER BY m.days DESC NULLS LAST LIMIT 1;

-- s5.leave_drop_pct | contrast | expected 8 or more (the card: 18.1) | main's billed hours a week in the leave, per cent under the four weeks before
-- want: value is not None and value >= 8
SELECT 's5.leave_drop_pct' AS ledger_key,
       round(100 * (1 - (sum(l.hours) FILTER (WHERE o.opened_at::date BETWEEN :'leave_from'::date AND :'leave_to'::date) / 2)
                      / NULLIF(sum(l.hours) FILTER (WHERE o.opened_at::date BETWEEN :'leave_from'::date - 28 AND :'leave_from'::date - 1) / 4, 0)), 1) AS value
FROM shop.order_labor l JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND j.status = 'approved';

-- season.total | expected en=[0.981, 0.96, 0.984, 1.002, 1.036, 1.046, 1.04, 1.021, 0.969, 0.972, 1.001, 0.985] ru=[0.666, 0.869, 0.888, 1.354, 1.238, 0.989, 0.954, 0.924, 0.894, 1.294, 1.077, 0.849] | tolerance ±0.05 index points, at least 1000 cases; a month that holds days of the diagnostician's leave may read up to 0.12 lower (generator-spec S05: main's day counts there are scaled down and the month's sum is lower, not made up on its other days) | orders per open day by calendar month, home shops, over the 23 whole months before T's month (the history's first month is partial), mean 1
-- want: value is not None and [p.split(':')[0] for p in value.split(' ')] == [str(m) for m in range(1, 13)] and all(-(0.12 if m in (a['leave_from'].month, a['leave_to'].month) else 0.05) <= float(p.split(':')[1]) - L[m - 1] <= 0.05 for m, p in enumerate(value.split(' '), 1))
WITH orders AS (
       SELECT extract(month FROM o.opened_at)::int AS m, count(*) AS n FROM shop.repair_order o
       WHERE o.location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END)) AND o.status NOT IN ('declined', 'void')
         AND o.opened_at >= date_trunc('month', :'T'::timestamp) - interval '23 months' AND o.opened_at < date_trunc('month', :'T'::timestamp)
         AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6) GROUP BY 1),
     days AS (
       SELECT extract(month FROM d.business_date)::int AS m, count(*) AS n FROM shop.cash_drawer_close d
       WHERE d.location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END)) AND d.business_date >= date_trunc('month', :'T'::timestamp) - interval '23 months' AND d.business_date < date_trunc('month', :'T'::timestamp)
         AND (:'cfg' = 'ru' OR extract(isodow FROM d.business_date) < 6) GROUP BY 1),
     per_day AS (SELECT orders.m, orders.n::numeric / days.n AS r FROM orders JOIN days ON days.m = orders.m)
SELECT 'season.total' AS ledger_key, string_agg(m || ':' || round(r / (SELECT avg(r) FROM per_day), 3), ' ' ORDER BY m) AS value FROM per_day;

-- season.ac_curve | expected en=[0.149, 0.149, 0.447, 0.845, 1.889, 2.485, 2.485, 2.087, 0.895, 0.298, 0.099, 0.099] ru=[0.05, 0.05, 0.199, 0.894, 2.583, 2.881, 2.583, 1.689, 0.596, 0.199, 0.099, 0.099] | tolerance ±0.3 index points, at least 40 cases | jobs by calendar month at the home shops (west joins the history at its purchase), over the 12 whole months before T's month (each month once: the jobs grow from one year to the next, so a month counted in two years would weigh the later more), over the mean month (open days not weighted); a month without a job reads 0
-- want: value is not None and [p.split(':')[0] for p in value.split(' ')] == [str(m) for m in range(1, 13)] and each(', '.join(p.split(':')[1] for p in value.split(' ')), L, abs=0.3)
SELECT 'season.ac_curve' AS ledger_key, string_agg(m || ':' || r, ' ' ORDER BY m) AS value
FROM (SELECT m, round(n / avg(n) OVER (), 3) AS r
      FROM (SELECT g.m, coalesce(avg(w.jobs), 0) AS n
            FROM generate_series(1, 12) AS g(m) LEFT JOIN (SELECT date_trunc('month', o.opened_at) AS month_on, count(*)::numeric AS jobs
                  FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
                  WHERE j.status = 'approved' AND c.code IN ('ac_performance_check', 'ac_recharge', 'ac_recharge_1234yf', 'ac_compressor', 'ac_condenser', 'ac_evaporator_cleaning')
                    AND o.location_id IN ((SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END), (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'Bonny Oaks' ELSE 'Инженерный' END))
                    AND o.opened_at >= date_trunc('month', :'T'::timestamp) - interval '12 months' AND o.opened_at < date_trunc('month', :'T'::timestamp) GROUP BY 1) w ON extract(month FROM w.month_on)::int = g.m
            GROUP BY 1) x) y;

-- season.battery_curve | expected en=[1.45, 1.1, 0.8, 0.7, 0.7, 0.85, 0.95, 0.9, 0.75, 1.0, 1.5, 1.3] ru=[1.502, 1.251, 0.951, 0.751, 0.651, 0.651, 0.651, 0.701, 0.851, 1.101, 1.402, 1.552] | tolerance ±0.3 index points, at least 40 cases | jobs by month over the mean month (open days not weighted)
-- want: value is not None and [p.split(':')[0] for p in value.split(' ')] == [str(m) for m in range(1, 13)] and each(', '.join(p.split(':')[1] for p in value.split(' ')), L, abs=0.3)
SELECT 'season.battery_curve' AS ledger_key, string_agg(m || ':' || r, ' ' ORDER BY m) AS value
FROM (SELECT m, round(n / avg(n) OVER (), 3) AS r FROM (SELECT extract(month FROM o.opened_at)::int AS m, count(*)::numeric AS n
      FROM shop.repair_order o JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
      WHERE j.status = 'approved' AND c.code IN ('battery_test', 'battery_replace') AND o.opened_at > :'T'::timestamp - interval '730 days' GROUP BY 1) x) y;

-- season.tyre.share_of_orders | expected en=0.2 ru=10.2 | tolerance ±1.0, at least 2500 cases
-- want: near(value, L, abs=1.0)
SELECT 'season.tyre.share_of_orders' AS ledger_key, round(100.0 * count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
               WHERE j.repair_order_id = o.repair_order_id AND c.code IN ('seasonal_tyre_change', 'seasonal_wheel_swap'))) / count(*), 2) AS value
FROM shop.repair_order o WHERE o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '12 months';

-- season.tyre.orders_in_window | band | expected en=null ru=1.64 | tolerance ±0.2 (ru only) | definition: orders per open day in the tyre windows (04-13 to 05-10, 10-13 to 11-09) over orders per open day (ru only) | window: opened in the 730 days before T | unit: ratio | tax: none
-- want: value is None if L is None else band(value, L - 0.2, L + 0.2)
SELECT 'season.tyre.orders_in_window' AS ledger_key,
       round((count(*) FILTER (WHERE to_char(o.opened_at, 'MM-DD') BETWEEN '04-13' AND '05-10' OR to_char(o.opened_at, 'MM-DD') BETWEEN '10-13' AND '11-09')::numeric
              / NULLIF(count(DISTINCT o.opened_at::date) FILTER (WHERE to_char(o.opened_at, 'MM-DD') BETWEEN '04-13' AND '05-10' OR to_char(o.opened_at, 'MM-DD') BETWEEN '10-13' AND '11-09'), 0))
           / NULLIF(count(*)::numeric / NULLIF(count(DISTINCT o.opened_at::date), 0), 0), 2) AS value
FROM shop.repair_order o WHERE :'cfg' = 'ru' AND o.status NOT IN ('declined', 'void') AND o.opened_at > :'T'::timestamp - interval '730 days';

-- season.hire | expected en="F4: ten weeks from the first Monday of June" ru="F4: six weeks from the first Monday of April and six weeks from the first Monday of October" | tolerance exact | en ten weeks from the first Monday of June; ru six weeks from the first Monday of April and of October; one row per season
-- want: value is not None and [p.split('..')[0] for p in value.split('; ')] == [str(d) for d in a['f4_seasons']]
SELECT 'season.hire' AS ledger_key, string_agg(e.hired_on || '..' || coalesce(e.left_on::text, ''), '; ' ORDER BY e.hired_on) AS value
FROM shop.employee e WHERE e.last_name = CASE :'cfg' WHEN 'en' THEN 'Pruitt' ELSE 'Юсупов' END;

-- kb.pay_types | expected en="flat rate for the line technicians; salary for slots 10 and 13; hourly for slots 14, 15, 28 and F4" ru=null | tolerance exact | flat rate for line technicians, salary for slots 10 and 13, hourly for 14, 15, 28 and F4
-- want: value == f"flat_rate 10, hourly {3 + len(a['f4_seasons'])}, salary 2"
SELECT 'kb.pay_types' AS ledger_key, string_agg(pay_type || ' ' || n, ', ' ORDER BY pay_type) AS value
FROM (SELECT pay_type, count(*) AS n FROM shop.employee WHERE role = 'technician' GROUP BY pay_type) x;

-- kb.stock.refrigerant | expected "at the flagship only; a new car at another shop goes there or waits for a cylinder" | tolerance exact | refrigerant stock outside main; expected 0
-- want: value == 0
SELECT 'kb.stock.refrigerant' AS ledger_key, count(*) FILTER (WHERE s.location_id <> (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND s.quantity_on_hand > 0) AS value
FROM shop.stock_level s JOIN shop.part p ON p.part_id = s.part_id
WHERE p.part_id IN (SELECT op.part_id FROM shop.order_part op JOIN shop.order_job j ON j.order_job_id = op.order_job_id JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id
                    WHERE c.code IN ('ac_recharge', 'ac_recharge_1234yf') AND op.description ILIKE ANY (ARRAY['%refrigerant%', '%хладагент%', '%фреон%', '%R-134a%', '%1234yf%']));

-- s7.bill | expected en={"inspection": 49.95, "front_pads_rotors": 493.0, "supplies": 12.15, "list_total": 555.1, "before_tax": 555.1, "tax": 51.35, "with_tax": 606.45, "declined_rear_shocks": 339.28, "declined_with_supplies": 347.38, "declined_before_tax": 347.38, "declined_with_tax": 379.51} ru={"inspection": 700, "front_pads_rotors": 12520, "supplies": 102.6, "list_total": 13322.6, "before_tax": 12688.19, "tax": 634.41, "with_tax": 13322.6, "declined_rear_shocks": 11720, "declined_with_supplies": 11811.2, "declined_before_tax": 11248.76, "declined_with_tax": 11811.2} | tolerance exact | before_tax, with_tax (= paid) and supplies as s7.bill; ru: with_tax = list_total, VAT inside
-- want: same(row['before_tax'], L['before_tax']) and same(row['with_tax'], L['with_tax']) and same(row['paid'], L['with_tax']) and same(row['supplies'], L['supplies']) and row['shocks_deferred'] == 't'
SELECT 's7.bill' AS ledger_key,
       o.total - o.tax_total AS before_tax, o.total AS with_tax,
       (SELECT sum(p.amount) FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment') AS paid,
       (SELECT f.amount FROM shop.order_fee f WHERE f.repair_order_id = o.repair_order_id AND f.kind = 'shop_supplies') AS supplies,
       (SELECT j.deferred FROM shop.order_job j JOIN shop.canned_job c ON c.canned_job_id = j.canned_job_id WHERE j.repair_order_id = o.repair_order_id AND c.code = 'rear_shocks_pair') AS shocks_deferred
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550131' ELSE '+79073786035' END;

-- s8.price_now | expected en=720.0 ru=16000 | tolerance exact
-- want: same(value, L)
SELECT 's8.price_now' AS ledger_key,
       (SELECT sum(l.amount) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id WHERE j.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days'))
     + (SELECT sum(p.quantity * p.unit_price) FROM shop.order_job j JOIN shop.order_part p ON p.order_job_id = j.order_job_id WHERE j.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days')) AS value;

-- s8.price_now:shop_list | expected the list price of s8.price_now on every timing-belt job billed at list from P: a car, the standard kit, a customer of the standard price class | tolerance exact | each job's labour and part lines before any discount; the coolant by the litre at the catalogue's unit price (spec section 1, "Money")
-- want: row['jobs'] >= 1 and same(value, V('s8.price_now'))
SELECT 's8.price_now:shop_list' AS ledger_key, string_agg(DISTINCT t.total::text, ', ') AS value, count(*) AS jobs
FROM (SELECT (SELECT coalesce(sum(l.amount), 0) FROM shop.order_labor l WHERE l.order_job_id = j.order_job_id)
             + (SELECT coalesce(sum(round(p.quantity * p.unit_price, 2)), 0) FROM shop.order_part p WHERE p.order_job_id = j.order_job_id) AS total
      FROM shop.order_job j JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
      JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.customer c ON c.customer_id = o.customer_id
      WHERE k.code = 'timing_belt_kit' AND o.order_type = 'customer_pay' AND c.price_class = 'standard' AND o.status NOT IN ('declined', 'void') AND o.opened_at::date >= :'P'::date
        AND v.vehicle_class = 'car' AND EXISTS (SELECT 1 FROM shop.order_part p WHERE p.order_job_id = j.order_job_id AND p.brand = CASE :'cfg' WHEN 'en' THEN 'Gates PowerGrip Premium' ELSE 'SKF' END)) t;

-- price.company_rounding:r1234yf_recharge | expected every R-1234yf recharge billed at list from P at the price golden KB.C6.2 states: ru 10 800 (the menu price 2 500, 500 g at 16 and the oil charge 300), en 278.80 (162.00, 1.1 lb at 98.00 and 9.00) | tolerance exact | a customer of the standard price class; each job's labour and part lines before any discount; none in a build is no failure (the gas is a summer job)
-- want: row['jobs'] == 0 or same(value, 278.8 if cfg == 'en' else 10800)
SELECT 'price.company_rounding:r1234yf_recharge' AS ledger_key, string_agg(DISTINCT t.total::text, ', ') AS value, count(*) AS jobs
FROM (SELECT (SELECT coalesce(sum(l.amount), 0) FROM shop.order_labor l WHERE l.order_job_id = j.order_job_id)
             + (SELECT coalesce(sum(round(p.quantity * p.unit_price, 2)), 0) FROM shop.order_part p WHERE p.order_job_id = j.order_job_id) AS total
      FROM shop.order_job j JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
      JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.customer c ON c.customer_id = o.customer_id
      WHERE k.code = 'ac_recharge_1234yf' AND o.order_type = 'customer_pay' AND c.price_class = 'standard' AND o.status NOT IN ('declined', 'void') AND o.opened_at::date >= :'P'::date) t;

-- s8.price_quoted | expected en=688.0 ru=15552 | tolerance exact
-- want: same(value, L)
SELECT 's8.price_quoted' AS ledger_key, j.approved_amount AS value FROM shop.order_job j WHERE j.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days') AND j.approved_amount IS NOT NULL;

-- s8.supplies | expected en=21.6 ru=182.4 | tolerance exact
-- want: same(value, L)
SELECT 's8.supplies' AS ledger_key, f.amount AS value FROM shop.order_fee f WHERE f.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days') AND f.kind = 'shop_supplies';

-- s8.bill_before_tax | expected en=741.6 ru=15411.81 | tolerance exact
-- want: same(value, L)
SELECT 's8.bill_before_tax' AS ledger_key, round((o.labor_total + o.parts_total + o.sublet_total + o.fees_total) * (CASE WHEN o.tax_included THEN 1 / (1 + o.tax_rate / 100) ELSE 1 END), 2) AS value FROM shop.repair_order o WHERE o.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s8.discount | expected en=80 ru=1800 | tolerance exact | approved by slot 4
-- want: same(value, L) and row['approved_by'] == ('Whitaker' if cfg == 'en' else 'Мельников')
SELECT 's8.discount' AS ledger_key, o.discount_total AS value, (SELECT e.last_name FROM shop.employee e WHERE e.employee_id = o.discount_approved_by_id) AS approved_by
FROM shop.repair_order o WHERE o.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s8.discount_pct | expected en=10.79 ru=11.12 | tolerance exact
-- want: same(value, L)
SELECT 's8.discount_pct' AS ledger_key, round(100 * o.discount_total / (o.labor_total + o.parts_total + o.sublet_total + o.fees_total), 2) AS value FROM shop.repair_order o WHERE o.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s8.paid_with_tax | expected en=722.8 ru=14382.4 | tolerance exact
-- want: same(value, L)
SELECT 's8.paid_with_tax' AS ledger_key, sum(p.amount) AS value FROM shop.payment p WHERE p.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days') AND p.kind = 'payment';

-- s8.bill_list | expected en=741.6 ru=16182.4 | tolerance exact | the bill as billed before the discount (en before sales tax; ru VAT inside)
-- want: same(value, L)
SELECT 's8.bill_list' AS ledger_key, o.labor_total + o.parts_total + o.sublet_total + o.fees_total AS value FROM shop.repair_order o WHERE o.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s8.paid_before_tax | expected en=661.6 ru=13697.52 | tolerance exact
-- want: same(value, L)
SELECT 's8.paid_before_tax' AS ledger_key, o.total - o.tax_total AS value FROM shop.repair_order o WHERE o.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s8.dates | expected {"quote_call": "slot 7's 5th working day before T", "car_in": "slot 7's 4th working day before T, promised the same day", "ready_bill_argument_complaint_call": "the next open weekday after that on which slot 5 works", "discount_and_call_back": "slot 4's next working day after that", "call_times_local": {"en": {"call_9": "10:25", "call_10": "14:35", "call_11": "09:10"}, "ru": {"call_9": "12:35", "call_10": "15:40", "call_11": "10:15"}}, "order": "call 9 is slot 7's second wrong price by date; call 12 (S12, the Tuesday of week T-5) is the first", "slot_7_note": "his 'Prices source' note: the day… | tolerance exact | estimate and approval at the quote call; invoiced twice; paid on slot 4's next working day
-- want: value is not None and [p.split(' ')[:2] for p in value.split('; ')[:2]] == [['estimate', str(a['s8_quote'])], ['approved', str(a['s8_quote'])]] and [p.split(' ')[1] for p in value.split('; ') if p.startswith('in_progress ')] == [str(a['s8_car_in'])] and [p.split(' ')[1] for p in value.split('; ') if p.startswith('invoiced ')] == [str(a['s8_ready']), str(a['s8_discount'])] and value.split('; ')[-1].split(' ')[:2] == ['paid', str(a['s8_discount'])]
SELECT 's8.dates' AS ledger_key, string_agg(h.status || ' ' || h.changed_at, '; ' ORDER BY h.changed_at) AS value
FROM shop.order_status_history h WHERE h.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = CASE :'cfg' WHEN 'en' THEN '+14235550172' ELSE '+79076418755' END AND o.opened_at > :'T'::timestamp - interval '30 days');

-- s15.mess | expected {"duplicate_pairs": 12, "pair_test": "same phone; every background phone is unique", "vin_missing_pct": 3, "wrong_mileage_orders": 6, "never_closed": {"west_open_since_weeks": 22, "others_over_60_days": 2}, "payments_not_one_to_one": {"statement_paying_several_orders": "en: every statement payment settles several orders; the planted instance is named by its statement and the count is emitted per build. ru: exactly one, a bank transfer paying a combined invoice for three orders", "order_paid_in_two_parts": 1, "refund": 1}, "wrong_customer_orders": 2, "times": "each shop's own wall clock, no zon… | tolerance exact | 12; 3 ±0.5; 3; 2; 1; 1; en every statement payment (emitted), ru 1
-- want: row['duplicate_pairs'] == L['duplicate_pairs'] and near(row['vin_missing_pct'], L['vin_missing_pct'], abs=0.5) and row['never_closed_over_60_days'] == 1 + L['never_closed']['others_over_60_days'] and row['wrong_customer_orders'] == L['wrong_customer_orders'] and row['orders_paid_in_parts'] == L['payments_not_one_to_one']['order_paid_in_two_parts'] and row['refunds'] == L['payments_not_one_to_one']['refund'] and (row['payments_settling_several_orders'] == row['statement_payments'] > 0 if cfg == 'en' else row['payments_settling_several_orders'] == 1)
SELECT 's15.mess' AS ledger_key,
       (SELECT count(*) FROM (SELECT phone FROM shop.customer WHERE phone IS NOT NULL GROUP BY phone HAVING count(*) > 1) d) AS duplicate_pairs,
       (SELECT round(100.0 * count(*) FILTER (WHERE vin IS NULL) / count(*), 2) FROM shop.vehicle) AS vin_missing_pct,
       (SELECT count(*) FROM shop.repair_order o WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined') AND o.opened_at < :'T'::timestamp - interval '60 days') AS never_closed_over_60_days,
       (SELECT count(*) FROM shop.repair_order o JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE o.customer_id <> v.customer_id) AS wrong_customer_orders,
       (SELECT count(*) FROM (SELECT repair_order_id FROM shop.payment WHERE kind = 'payment' AND repair_order_id IS NOT NULL GROUP BY 1 HAVING count(*) > 1) x) AS orders_paid_in_parts,
       (SELECT count(*) FROM shop.payment WHERE kind = 'refund') AS refunds,
       (SELECT count(*) FROM shop.payment p WHERE p.statement_id IS NOT NULL AND (SELECT count(*) FROM shop.repair_order o WHERE o.statement_id = p.statement_id) > 1) AS payments_settling_several_orders,
       (SELECT count(*) FROM shop.payment p WHERE p.statement_id IS NOT NULL) AS statement_payments;

-- s15.mess | expected {"duplicate_pairs": 12, "pair_test": "same phone; every background phone is unique", "vin_missing_pct": 3, "wrong_mileage_orders": 6, "never_closed": {"west_open_since_weeks": 22, "others_over_60_days": 2}, "payments_not_one_to_one": {"statement_paying_several_orders": "en: every statement payment settles several orders; the planted instance is named by its statement and the count is emitted per build. ru: exactly one, a bank transfer paying a combined invoice for three orders", "order_paid_in_two_parts": 1, "refund": 1}, "wrong_customer_orders": 2, "times": "each shop's own wall clock, no zon… | tolerance exact | 6: below the visit before, or ten times it (the ten-times readings are each car's last visit, so no later order reads as lower)
-- want: value == L['wrong_mileage_orders']
SELECT 's15.mess:wrong_mileage' AS ledger_key, count(*) AS value
FROM (SELECT o.mileage_in, lag(o.mileage_in) OVER (PARTITION BY o.vehicle_id ORDER BY o.opened_at) AS prev_in, o.opened_at
      FROM shop.repair_order o WHERE o.mileage_in IS NOT NULL) x
WHERE x.opened_at > :'T'::timestamp - interval '24 months'
  AND (x.mileage_in < x.prev_in OR x.mileage_in > 3 * x.prev_in);

-- s15.dates | expected {"west_order_never_closed": "opened the Wednesday of week T-22, status completed since the next day", "two_more_open": "opened the Tuesdays of weeks T-12 (main) and T-10 (east)", "wrong_mileages": "one in each of the last six quarters"} | tolerance exact | west completed, the Wednesday of week T-22; main in_progress, the Tuesday of week T-12; east approved, the Tuesday of week T-10
-- want: value is not None and value.split('; ') == [f"{V('geo.short_name')['west']} completed {a['week_day'](-22, 2)}", f"{V('geo.short_name')['main']} in_progress {a['week_day'](-12, 1)}", f"{V('geo.short_name')['east']} approved {a['week_day'](-10, 1)}"]
SELECT 's15.dates' AS ledger_key, string_agg(l.name || ' ' || o.status || ' ' || o.opened_at::date, '; ' ORDER BY o.opened_at) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined') AND o.opened_at < :'T'::timestamp - interval '60 days';

-- kb.month_end | expected en={"orders_open_over_days_go_to_slot_2": 60, "sales_tax_return_by": "the 20th of the following month (as generally known; not read on the state's page)"} ru={"orders_open_over_days_go_to_slot_2": 60, "vat_return": "once a quarter, by the 25th of the month after it"} | tolerance exact | orders open over 60 days: 3
-- want: value == 3
SELECT 'kb.month_end' AS ledger_key, count(*) AS value FROM shop.repair_order o
WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined') AND o.opened_at < :'T'::timestamp - interval '60 days';

-- s2.dates | expected {"found": "the 5th full open day after G (the bookkeeper's check of tills against payments)", "owner_thread": "the same day", "follow_up_thread": "5 full open days later", "fired": "the 15th full open day after G", "rule_page_and_note": "the next full open day", "note_rank": "the team note is proposed by slot 2 (administrator rank); slot 4 lowers it to junior when he approves it, so a junior reads it (S2.4)", "friday_list": "slot 2's 'Discounts over 10 %' is created on the rule's day"} | tolerance exact | nothing of his after the firing
-- want: same(row['left_on'], a['fired']) and row['last_order_of_f1'] is not None and date.fromisoformat(row['last_order_of_f1']) <= a['fired']
SELECT 's2.dates' AS ledger_key, min(o.opened_at)::date AS first_planted_order, max(o.opened_at)::date AS last_order_of_f1,
       (SELECT left_on FROM shop.employee WHERE employee_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END)) AS left_on
FROM shop.repair_order o WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END);

-- erp.warranty_order_totals | expected "a warranty or goodwill order keeps its lines at their prices; the whole amount is in discount_total, total is 0, status paid, no payment row" | tolerance exact | value = warranty and goodwill orders off the convention: totals, invoiced but not paid, with a payment, with a discount approver; expected 0, 0, 0, 0
-- want: row['totals_off'] == 0 and row['invoiced_not_paid'] == 0 and row['with_a_payment'] == 0 and row['with_an_approver'] == 0
SELECT 'erp.warranty_order_totals' AS ledger_key,
       count(*) FILTER (WHERE o.total <> 0 OR o.tax_total <> 0 OR o.discount_total <> o.labor_total + o.parts_total + o.sublet_total + o.fees_total) AS totals_off,
       count(*) FILTER (WHERE o.status = 'invoiced') AS invoiced_not_paid,
       count(*) FILTER (WHERE EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id)) AS with_a_payment,
       count(*) FILTER (WHERE o.discount_approved_by_id IS NOT NULL) AS with_an_approver
FROM shop.repair_order o WHERE o.order_type IN ('warranty', 'goodwill');

-- erp.estimate.declined_share | expected {"private": 6.0, "accounts_on_terms": 2.0} | tolerance ±1.5, at least 34 cases | % of the last 12 months' estimates that ended declined: customers paying at the counter, accounts billed on terms (A6 left out: s1.a6)
-- want: near(row['private'], L['private'], abs=1.5) and near(row['accounts_on_terms'], L['accounts_on_terms'], abs=1.5)
SELECT 'erp.estimate.declined_share' AS ledger_key,
       round(100.0 * count(*) FILTER (WHERE o.status = 'declined' AND c.payment_terms_days IS NULL) / NULLIF(count(*) FILTER (WHERE c.payment_terms_days IS NULL), 0), 1) AS private,
       round(100.0 * count(*) FILTER (WHERE o.status = 'declined' AND c.payment_terms_days IS NOT NULL) / NULLIF(count(*) FILTER (WHERE c.payment_terms_days IS NOT NULL), 0), 1) AS accounts_on_terms
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE o.order_type = 'customer_pay' AND o.status <> 'void' AND o.opened_at > :'T'::timestamp - interval '12 months'
  AND c.name NOT LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Sourwood Catering Co.' ELSE 'Вкусный выезд' END || '%';

-- erp.inspection.bad_documented | expected {"main": 92, "east": 96, "west": 65} | tolerance ±5, at least 10 cases | % of bad findings with both a measurement and a photo, by shop
-- want: value is not None and [p.rsplit(' ', 1)[0] for p in value.split(', ')] == [V('geo.short_name')[s] for s in ('main', 'east', 'west')] and each(', '.join(p.rsplit(' ', 1)[1] for p in value.split(', ')), [L[s] for s in ('main', 'east', 'west')], abs=5)
SELECT 'erp.inspection.bad_documented' AS ledger_key, string_agg(x.name || ' ' || x.pct, ', ' ORDER BY x.location_id) AS value
FROM (SELECT l.location_id, l.name, round(100.0 * count(*) FILTER (WHERE it.measurement IS NOT NULL AND it.has_photo) / count(*), 1) AS pct
      FROM shop.inspection_item it JOIN shop.inspection i ON i.inspection_id = it.inspection_id
      JOIN shop.repair_order o ON o.repair_order_id = i.repair_order_id JOIN shop.location l ON l.location_id = o.location_id
      WHERE it.result = 'bad' GROUP BY l.location_id, l.name) x;

-- p07.rebilled | expected 3 | tolerance exact | orders invoiced more than once: slot 7's (S8's among them), everyone else's; expected 3, 0
-- want: row['slot_7'] == L and row['others'] == 0
SELECT 'p07.rebilled' AS ledger_key,
       count(*) FILTER (WHERE o.advisor_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Caleb' ELSE 'Никита' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sutton' ELSE 'Ведяшкин' END)) AS slot_7,
       count(*) FILTER (WHERE o.advisor_id <> (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Caleb' ELSE 'Никита' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Sutton' ELSE 'Ведяшкин' END)) AS others
FROM shop.repair_order o WHERE (SELECT count(*) FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') > 1;

-- board.second_look_open | expected en="slot 8's open card needs one warranty order on a job of slot 14: Dogwood Lane Florals' ProMaster City; when the card's due day falls after T, an appointment at opening on that day instead" ru="slot 8's open card needs one warranty order on a job of slot 14: ИП Абрамова's Largus; when the card's due day falls after T, an appointment at opening on that day instead" | tolerance exact | warranty orders at main pointing at slot 14's order on the florist's van, plus the van's appointment at opening on a day after T (the card's due day after T); expected 1
-- want: value == 1
SELECT 'board.second_look_open' AS ledger_key, count(*) + (SELECT count(*) FROM shop.appointment a JOIN shop.customer c ON c.customer_id = a.customer_id
         WHERE a.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END)
           AND c.name LIKE CASE :'cfg' WHEN 'en' THEN '%Dogwood Lane Florals%' ELSE '%Абрамова%' END AND a.starts_at > :'T'::timestamp
           AND a.starts_at::time = CASE :'cfg' WHEN 'en' THEN time '07:30' ELSE time '09:00' END AND a.status IN ('booked', 'confirmed')) AS value
FROM shop.repair_order o JOIN shop.repair_order f ON f.repair_order_id = o.comeback_of_id JOIN shop.customer c ON c.customer_id = f.customer_id
WHERE o.order_type = 'warranty' AND o.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END)
  AND c.name LIKE CASE :'cfg' WHEN 'en' THEN '%Dogwood Lane Florals%' ELSE '%Абрамова%' END
  AND EXISTS (SELECT 1 FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = f.repair_order_id AND lb.technician_id = (SELECT employee_id FROM shop.employee WHERE first_name = CASE :'cfg' WHEN 'en' THEN 'Hunter' ELSE 'Иван' END AND last_name = CASE :'cfg' WHEN 'en' THEN 'Varnell' ELSE 'Сурков' END));

-- The story files' new facts (checks/new_facts.json; erp/generator-spec.md section 5, "The story files' new facts").
-- One query per ledger row nf.call.NN / nf.conv.NN that plants shop-system rows; value = the planted facts found. Dates are
-- the weeks of stories/TIMELINE.md; a Russian rota anchor is read as a window of four days from its weekday.

-- nf.call.03 | expected en=["An invented first-time caller, Dwight Sizemore, 423-555-0146, 2012 Toyota Tacoma: an appointment at main for the call's day at 12:30, source phone, with no customer name on it; the customer record is made at check-in."] ru=["Новый клиент на Renault Duster 2018, телефон +7 907 318-62-88. Имя на звонке не спрошено; в наряде на следующий день он Ринат Хайруллин. Запись на следующий день, 10:00: замена масла и фильтра, 8 579,50 по прайсу."] | tolerance exact | value = appointment without a name, then the record and the order at check-in: en 2, ru 2
-- want: value == 2
SELECT 'nf.call.03' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550146' OR c.phone = '+14235550146') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '12:30' AND a.contact_name IS NULL AND a.source = 'phone'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+14235550146' AND v.model ILIKE '%Tacoma%' AND v.year = 2012 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79073186288' OR c.phone = '+79073186288') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '10:00' AND a.contact_name IS NULL))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79073186288' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('oil_service')))::int END AS value;

-- nf.call.04 | expected en=["An invented first-time caller, Carla Jenkins, 423-555-0157, 2015 Hyundai Sonata: an appointment at main on call+1d at 10:00 for a check engine diagnosis."] ru=["Новая клиентка Наталья Ефимова, Volkswagen Polo седан 2016, телефон +7 907 830-66-80. Запись на следующий день, 11:00: диагностика ходовой, 800."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.04' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550157' OR c.phone = '+14235550157') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '10:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79078306680' OR c.phone = '+79078306680') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '11:00'))::int END AS value;

-- nf.call.05 | expected en=["An invented first-time caller, Stephanie Vandergriff, 423-555-0191, 2017 Honda Odyssey: an appointment at main on call+4d at 13:30 for a four-wheel alignment."] ru=["Новый клиент Андрей Куликов, Lada Granta 2018, телефон +7 907 211-68-27. Запись на пятницу после звонка (через пять дней), 9:00: замена передних стоек стабилизатора, 3 700."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.05' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550191' OR c.phone = '+14235550191') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '13:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79072116827' OR c.phone = '+79072116827') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '09:00'))::int END AS value;

-- nf.call.06 | expected en=["An invented first-time caller, Wendell Boyd, 423-555-0188, 2015 Chevrolet Equinox: an appointment at main on call+2d at 08:00 for a road test and a right front wheel bearing."] ru=null | tolerance exact | value = the booking (en only): en 1, ru 0
-- want: value == (1 if cfg == 'en' else 0)
SELECT 'nf.call.06' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550188' OR c.phone = '+14235550188') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '08:00'))::int ELSE 0 END AS value;

-- nf.call.07 | expected en=["Ronnie Eaves, a driver of account A3 (not a contact), mobile 423-555-0116, drives unit MB-6.", "An order at main on slot 6's 2nd working day before T for MB-6: oil service 90.95 and, added on the driver's word, a right front CV axle 379.64 (technician slot 12); completed by 16:00 the same day.", "An outbound 'car ready' call from desk 102 to the driver at 15:52 that day (it keeps the promise of this call).", "The fleet contact of A3 was not called about the added work."] ru=["Фёдор, водитель «Симбирского гонца» (A1), машина № 12 (ГАЗель Next 2022, А867СР73), телефон +7 907 351-38-85.", "В день звонка у A1 открыт наряд на № 12: ТО коммерческого автомобиля по договорной цене (8 724) и добавленные по звонку работы на 9 500: замена левой шаровой опоры, сход-развал, замена тормозной жидкости. Работы согласовал водитель, а не Кравцов.", "Исходящий звонок с 102 на номер водителя около 17:50 того же дня: машина готова (обещанный звонок выполнен)."] | tolerance exact | value = the order approved by the driver over his limit: en 2, ru 2
-- want: value == 2
SELECT 'nf.call.07' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'MB-6' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('cv_axle') AND j.status = 'approved' AND j.approval_method = 'phone' AND j.authorized_by ILIKE '%Eaves%'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'MB-6' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('oil_service') AND j.status = 'approved'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'А867СР73' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('ball_joint') AND j.status = 'approved' AND j.authorized_by ILIKE '%Фёдор%'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'А867СР73' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('fleet_pm_van') AND j.status = 'approved'))::int END AS value;

-- nf.call.09 | expected en=["An appointment at main for Frank Daugherty on slot 7's 4th working day before T at 08:00, source phone, taken by slot 7, with the estimate at 688.00 (card S08's 'estimate at the quoted price')."] ru=["Запись Фомичёва на субботу оформлена без имени, по номеру телефона; имя появляется в наряде при приёмке."] | tolerance exact | value = S8's booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.09' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550172' OR c.phone = '+14235550172') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '08:00' AND a.source = 'phone'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79076418755' OR c.phone = '+79076418755') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.source = 'phone' AND a.contact_name IS NULL))::int END AS value;

-- nf.call.14 | expected en=["An invented first-time caller, Kayla Thornton, 423-555-0109, 2017 Nissan Rogue: an appointment at main on call+2d at 08:00 for rear pads and rotors (the day before T for the nominal T)."] ru=["Новый клиент Алексей Тихонов, Škoda Rapid 2017, телефон +7 907 504-97-29 (на звонке взято только имя). Запись на среду после звонка (через три дня), 14:00: замена ремня привода навесных агрегатов, 2 750."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.14' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550109' OR c.phone = '+14235550109') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '08:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79075049729' OR c.phone = '+79075049729') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '14:00'))::int END AS value;

-- nf.call.17 | expected en=["Which van is which: the first comeback (the Tuesday of week T-26) is E-2, the second (the Tuesday of week T-22) is E-6; each came back about three weeks after its pad job, so the first orders are about three weeks before those days and the disputed line is E-6's pad job.", "Both comebacks were done without charge (warranty orders).", "Slot 27 told A5's driver the noise was 'just bedding in'."] ru=null | tolerance exact | value = A5's two comebacks on their vans: en 2, ru 2 (the first is the Tuesday of week T-26, before G, so the window is the history's)
-- want: value == 2
SELECT 'nf.call.17' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number = 'E-2' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number = 'E-6' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number = 'Э-1' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number = 'Э-10' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int END AS value;

-- nf.call.21 | expected en=["An appointment at main for SC-2 on call+2d at 07:30 (the Thursday of week T-20): fleet PM service A at list, 270.59; it is one of A6's visits in its first 30-day block after the rise.", "Several of A6's vans are white (he says 'about five'); no colour is recorded in accounts.json.", "Her predecessor left her a sheet with 'usual, 255' against the van."] ru=["У A6 наряд на машину № 1 (Х176АХ73) на следующий день после звонка: ТО коммерческого автомобиля 9 710 и замена лампы ближнего света 800, по прайсу.", "Предыдущее ТО этой машины было примерно за три месяца до звонка, по старому нормо-часу: 9 500."] | tolerance exact | value = A6's order: en 2, ru 2
-- want: value == 2
SELECT 'nf.call.21' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE v.unit_number = 'SC-2' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '07:30'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'SC-2' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('fleet_pm_van') AND j.status = 'approved'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'Х176АХ73' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('fleet_pm_van') AND j.status = 'approved'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'Х176АХ73' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('headlight_bulb') AND j.status = 'approved'))::int END AS value;

-- nf.call.22 | expected en=["An estimate for A6 at main opened on this call's day for SC-4 (front and rear brakes) and SC-5 (PM service) and sent on call+2d; it is the 'quote sent two days late' of card S01.", "Her e-mail is the account's own, ecastillo@sourwoodcatering.example; the account still held her predecessor's."] ru=["Смета для «Вкусного выезда» на две машины (№ 2: передние колодки и диски, 16 276; № 5: ТО) отправлена через два дня после звонка. Звонка клиенту в течение 24 часов не было."] | tolerance exact | value = the estimate sent two days late: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.22' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number IN ('SC-4', 'SC-5') AND c.name LIKE '%Sourwood Catering%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND (SELECT min(x.decided_at) FROM shop.order_job x WHERE x.repair_order_id = o.repair_order_id) >= o.opened_at + interval '2 days'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.unit_number IN ('2', '5') AND c.name LIKE '%Вкусный выезд%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND (SELECT min(x.decided_at) FROM shop.order_job x WHERE x.repair_order_id = o.repair_order_id) >= o.opened_at + interval '2 days'))::int END AS value;

-- nf.call.23 | expected en=["An appointment and an order at main for ND-22 on call+1d at 07:30 (the Thursday of week T-17), opened with no purchase-order number: check engine diagnosis at the company-account rate."] ru=["У A1 наряд на машину № 07 (Т198ОК73) на следующий день после звонка: ТО коммерческого автомобиля по договорной цене 8 724, без номера заявки клиента."] | tolerance exact | value = the order without a purchase-order number: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.23' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'ND-22' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('check_engine_diag') AND o.purchase_order_number IS NULL))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'Т198ОК73' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('fleet_pm_van') AND o.purchase_order_number IS NULL))::int END AS value;

-- nf.call.24 | expected en=["A purchase-order number of A1, ND-60418, on an appointment and an order at main for ND-08 on call+2d at 07:30 (the Friday of week T-4): fleet PM service A and a wheel-balance check, at the company-account rate.", "The bookkeeper (slot 3) has told the desk not to open A1 orders without a purchase-order number; two front tires were fitted to ND-08 by another business about a month before."] ru=["У A1 наряд на машину № 24 (Р358ТН173) в день звонка, 14:00: замена передних колодок, номер заявки клиента 247/10."] | tolerance exact | value = A1's purchase-order number: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.24' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'ND-08' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('fleet_pm_van') AND o.purchase_order_number = 'ND-60418'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.plate = 'Р358ТН173' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('front_brake_pads') AND o.purchase_order_number = '247/10'))::int END AS value;

-- nf.call.25 | expected en=["A driver of account A2 called Darnell (first name only), who drives unit M-112.", "A purchase-order number of A2, 4471B, on an appointment and an order at east for M-112 on call+1d at 07:30: front pads and rotors at the company-account price.", "M-112 had front struts fitted at east some months before; the unit is white."] ru=["Рамиль, сотрудник «Тёплого контура» (A2), который ведёт машины компании, телефон +7 907 471-16-40, и водитель Ильдус.", "Номер заявки клиента 118/11 на замену сцепления машины Т-17; запись на следующий день, 9:00."] | tolerance exact | value = A2's purchase-order number: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.25' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'M-112' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('front_pads_rotors') AND o.purchase_order_number = '4471B'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'Т-17' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('clutch_kit') AND o.purchase_order_number = '118/11'))::int END AS value;

-- nf.call.26 | expected en=["An invented first-time caller, Gerald Massengill, 423-555-0170, 2014 Toyota Highlander: an appointment at east on call+1d at 07:30 for a steering and suspension inspection."] ru=["Новый клиент Сергей Ганин, Kia Ceed 2014, телефон +7 907 913-73-68. Запись на следующий день, 10:00: замена передних стоек (18 580) и сход-развал (3 000)."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.26' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550170' OR c.phone = '+14235550170') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '07:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79079137368' OR c.phone = '+79079137368') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '10:00'))::int END AS value;

-- nf.call.27 | expected en=["A regular of east, Carolyn Bivens, 423-555-0152, 2015 Buick Enclave, with a history at the shop: at her last oil service the battery test was recorded as weak (a note on that order).", "An appointment at east on call+1d at 07:30 (the Tuesday of week T-3) for a charging-system test and a battery."] ru=["Постоянный клиент восточного сервиса Николай Иванович Пчелинцев (УАЗ Патриот; последняя работа по нему: ступица), телефон +7 907 552-45-96.", "Наряд на Lada Granta 2020 его дочери Анастасии в четверг после звонка, 10:00: замена масла и фильтров, 9 890; плательщик Пчелинцев."] | tolerance exact | value = the booking and the history: en 2, ru 1
-- want: value == (2 if cfg == 'en' else 1)
SELECT 'nf.call.27' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550152' OR c.phone = '+14235550152') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '07:30'))::int + (EXISTS (SELECT 1 FROM shop.inspection_item it JOIN shop.inspection i ON i.inspection_id = it.inspection_id JOIN shop.repair_order o ON o.repair_order_id = i.repair_order_id JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+14235550152' AND it.result = 'watch' AND it.component ILIKE '%batter%'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79075524596' AND v.model ILIKE '%Granta%' AND v.year = 2020 AND v.customer_id = c.customer_id AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('oil_service')))::int END AS value;

-- nf.call.28 | expected en=["A regular of east, Roy Standifer, 423-555-0128, 2013 GMC Sierra 1500, with a history at the shop; slot 16 had told him to ring about the transmission service.", "The wording of the shop's hold message: 'Thank you for holding. Someone will be right with you.'", "No booking is made on this call."] ru=["Постоянная клиентка восточного сервиса Людмила Аркадьевна Жукова (Toyota Corolla 2014), телефон +7 907 423-30-82. Перезвонила ли она в четверг, история не говорит."] | tolerance exact | value = a regular with history: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.28' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+14235550128' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+79074233082' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date))::int END AS value;

-- nf.call.29 | expected en=["A customer of main, Phil Cantrell, 423-555-0161, 2014 Chevrolet Malibu: an order on the Tuesday of week T-10 for a front lower control arm (technician slot 11, no alignment on it), and a comeback order on the Friday of week T-10 pointing at it (alignment, no charge, rechecked by slot 8).", "At pick-up slot 11 told him 'it's fixed, I don't know what else to tell you'."] ru=["Клиент Денис Маркелов, Mitsubishi Lancer X 2011, телефон +7 907 461-14-93.", "Накануне звонка (четверг) у него наряд на главной площадке: замена передних колодок и дисков, механик Максим Рябов (место 11).", "В день звонка гарантийный наряд, указывающий на вчерашний: гайки левого переднего колеса не были затянуты; мастер цеха снял оба передних колеса, проверил шпильки и диски, протянул гайки. Эвакуатор не понадобился."] | tolerance exact | value = the order and its comeback: en 2, ru 2
-- want: value == 2
SELECT 'nf.call.29' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+14235550161' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 69) BETWEEN 0 AND 4 AND ((o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 69) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 69) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 69)))) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE (z.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 69) BETWEEN 0 AND 4 AND (z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 69) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 69))))))) AND k.code IN ('lower_control_arm')))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+14235550161' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 66) BETWEEN 0 AND 4 AND ((o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 66) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66)))) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE (z.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 66) BETWEEN 0 AND 4 AND (z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66))))))) AND k.code IN ('wheel_alignment') AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79074611493' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('front_pads_rotors')))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+79074611493' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int END AS value;

-- nf.call.30 | expected en=["A customer of main, Tasha Underwood, 423-555-0199, 2013 Hyundai Santa Fe: a water-pump order completed and paid on the Friday of week T-3 (technician slot 11; 659.37 with tax) and a comeback order the same evening pointing at it (a loose hose clamp; no charge).", "A tow by vendor V8 from the highway to main that evening, at the shop's cost.", "Two outbound calls to her after this one: desk 102 at 16:46 and desk 104 at 17:05."] ru=["Клиентка Ирина Белоглазова, Nissan Qashqai 2016, телефон +7 907 705-78-26.", "За два дня до звонка (четверг) у неё наряд на главной площадке: замена масла и фильтра, механик Максим Рябов (место 11).", "В день звонка, 14:00, гарантийный наряд, указывающий на тот: защита двигателя закреплена на все болты, пробка поддона проверена."] | tolerance exact | value = the order, its comeback (en and the tow): en 3, ru 2
-- want: value == (3 if cfg == 'en' else 2)
SELECT 'nf.call.30' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+14235550199' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND ((o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17)))) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE (z.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND (z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17))))))) AND k.code IN ('water_pump') AND o.total = 659.37))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+14235550199' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND ((o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17)))) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE (z.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 17) BETWEEN 0 AND 4 AND (z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 17))))))) AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int + (EXISTS (SELECT 1 FROM shop.order_sublet sb JOIN shop.order_job j ON j.order_job_id = sb.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+14235550199' AND sb.price = 0))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79077057826' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('oil_service')))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+79077057826' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int END AS value;

-- nf.call.31 | expected en=["Three missed calls at main from 423-555-0137 on the Monday of week T-6 at 07:34, 07:46 and 07:58, each resolved by this call (got_through); they are among the morning misses of the period before the fix.", "An invented first-time caller, Tamika Ellison, 2017 Hyundai Elantra: an appointment at main that day at 09:00 for a check engine diagnosis (technician slot 10), and a ride back to her work."] ru=["Клиент Тимур Айдаров, Chevrolet Cruze 2013, телефон +7 907 274-37-28.", "Два пропущенных с его номера в то же утро, 09:06 и 09:21, первый стол 101; оба сняты этим звонком (got_through).", "Запись в тот же день на 13:00: компьютерная диагностика двигателя, 1 200."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.31' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550137' OR c.phone = '+14235550137') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 42) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 42) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 42)))) AND a.starts_at::time = '09:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79072743728' OR c.phone = '+79072743728') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '13:00'))::int END AS value;

-- nf.call.32 | expected en=["An invented first-time caller, Jared Scruggs, 423-555-0181, 2019 Toyota RAV4: an appointment at main that day at 08:00 for a flat repair."] ru=["Новый клиент Вадим Рожков, Renault Sandero 2016, телефон +7 907 610-96-87 (на звонке взято только имя). Запись на следующий день, 9:30: замена основного глушителя, 9 180."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.32' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550181' OR c.phone = '+14235550181') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '08:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79076109687' OR c.phone = '+79076109687') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '09:30'))::int END AS value;

-- nf.call.33 | expected en=["A long-standing customer of west, Harlan Pewitt, 615-555-0126, 2008 Chevrolet Silverado 1500, with a history at the shop (a lower ball joint was pointed out at an earlier visit). No booking is made on this call."] ru=["Клиент казанского сервиса Ленар, Lada Priora 2012, телефон +7 907 877-40-74; его отец Фарид давно обслуживается на Технической. Позвонил ли он снова, история не говорит."] | tolerance exact | value = the earlier finding (en only): en 1, ru 0
-- want: value == (1 if cfg == 'en' else 0)
SELECT 'nf.call.33' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.inspection_item it JOIN shop.order_job j ON j.order_job_id = it.order_job_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+16155550126' AND it.result = 'watch' AND k.code = 'ball_joint' AND j.status = 'declined'))::int ELSE 0 END AS value;

-- nf.call.34 | expected en=["A long-standing customer of west, Peggy Womack, 2010 Toyota Camry; her son Jeff Womack rings from 615-555-0171. No booking is made on this call."] ru=["Клиент казанского сервиса Рашид, Toyota Camry 2012, телефон +7 907 412-16-80. Позвонил ли он снова, история не говорит."] | tolerance exact | value = a customer with history: en 1, ru 1
-- want: value == 1
SELECT 'nf.call.34' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.name ILIKE '%Womack%' AND v.model ILIKE '%Camry%' AND v.year = 2010 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.phone = '+79074121680' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date))::int END AS value;

-- nf.call.36 | expected en=["A returning customer of west, Keisha Abernathy, 629-555-0112, 2016 Jeep Grand Cherokee, with a front brake order at west a few months before; an appointment at west on the Friday of week T-2 at 14:00 for a cooling system pressure test."] ru=["Новый клиент Эдуард Сабиров, Haval Jolion 2022, телефон +7 907 411-81-94 (на звонке названо только имя). Запись в день звонка, 16:00: сход-развал, 3 450."] | tolerance exact | value = the history and the booking: en 2, ru 1
-- want: value == (2 if cfg == 'en' else 1)
SELECT 'nf.call.36' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+16295550112' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND o.opened_at::date BETWEEN :'T'::date - 760 AND :'T'::date AND k.code IN ('front_brake_pads', 'front_pads_rotors')))::int + (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+16295550112' OR c.phone = '+16295550112') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 10) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 10) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 10)))) AND a.starts_at::time = '14:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79074118194' OR c.phone = '+79074118194') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '16:00'))::int END AS value;

-- nf.conv.02 | expected en=["The estimate reached her by e-mail from the shop system at about 10:05 on the day of the visit (rdunlap@inbox.example).", "The car was ready by 3:00; the order was closed and paid at about 15:10.", "The seeping shock absorber is the right rear one."] ru=["Смета ушла ей на электронную почту из учётной системы около 10:40 в день визита (o.timofeeva@pochta.example).", "Машина была готова к 15:00; наряд закрыт и оплачен около 18:40.", "Запотел правый задний амортизатор.", "На «спасибо» ответил слот 7 (его смена), чат закрыла слот 6 на следующий свой рабочий день."] | tolerance exact | value = S7's payment at the chat's hour: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.02' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.payment p JOIN shop.repair_order o ON o.repair_order_id = p.repair_order_id JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+14235550131' AND p.kind = 'payment' AND p.received_at::time BETWEEN '15:00' AND '15:20'))::int ELSE (EXISTS (SELECT 1 FROM shop.payment p JOIN shop.repair_order o ON o.repair_order_id = p.repair_order_id JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+79073786035' AND p.kind = 'payment' AND p.received_at::time BETWEEN '18:30' AND '18:50'))::int END AS value;

-- nf.conv.04 | expected en=["The quote is for SC-4 (front brake pads and rotors, 640.91 at list) and SC-9 (battery, 304.45 at list); it was asked for the owner's sign-off on the Friday of week T-4.", "ERP: the estimate made from this chat is proposed as one of A6's five slow estimates (ledger s1.a6), expired; no order followed.", "The file Sourwood_quote_SC4_SC9.pdf (picture pool 'estimate-pdf').", "SC-4's brakes were quoted once before, after call 22 (the Tuesday of week T-9), and not booked; this quote, front pads and rotors only, is A6's second estimate on SC-4."] ru=["Смета — на машины № 7 (Ford Transit: передние диски и колодки, 16 276 по прайсу) и № 8 (Citroën Jumper: аккумулятор, 11 274 по прайсу); нужна к согласованию у директора в пятницу недели T-4.", "ERP: смету из этого чата предлагается считать одной из пяти «медленных» смет A6 (ledger s1.a6), просрочена; заказа не было.", "Файл Smeta_Vkusny_vyezd_Transit_Jumper.pdf (пул 'estimate-pdf').", "Запрос пришёл во вторник в 20:41, после закрытия: так день карточки сохранён, а первая реплика человека приходится на смену слотов 5 и 7.", "Смета звонка 22 (неделя T-9) была на машины № 2 (передние колодки и … | tolerance exact | value = the chat's estimate, expired: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.04' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'SC-9' AND c.name LIKE '%Sourwood Catering%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('battery_replace') AND o.status = 'declined'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = '8' AND c.name LIKE '%Вкусный выезд%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('battery_replace') AND o.status = 'declined'))::int END AS value;

-- nf.conv.05 | expected en=["The Monday lists: week T-22: M-103, M-107, M-110, M-114, M-121; week T-15: five vans, M-112 among them; week T-5: M-104, M-106, M-111, M-115, M-119 (M-108 swapped out); week T-4: M-108 added; week W+1: M-102, M-109, M-113, M-116, M-122.", "M-112's front struts and alignment were done on the Monday of week T-15 for 1,119.98 before tax under purchase order 4398A (the 'front struts back in the summer' of story call 25).", "M-110 pulled to the right in week T-22; M-113's heater is weak in week W0; M-122's rear brakes were low at its last service.", "The photo M112_front_strut.jpg (picture pool '… ru=["Заявки на понедельник: неделя T-22: Т-02, Т-06, Т-11, Т-15, Т-22; неделя T-5: Т-04, Т-05, Т-13, Т-18, Т-24 (Т-08 заменён); неделя T-4: добавлен Т-08; неделя W+1: Т-03, Т-07, Т-12, Т-16, Т-25.", "Largus Т-09 приехал в понедельник недели T-16 на ТО, у него нашли течь помпы; слот 17 обещал перезвонить с ценой и не перезвонил; помпу заменили в первый рабочий день слота 16 после этого, 12 279,80 по договору, заявка 96/07.", "ГАЗель Т-15 тянуло вправо (неделя T-22); у Granta Т-12 слабо греет печка (неделя W0); у Duster Т-25 задние колодки были на исходе на прошлом ТО; Т-08 в начале октября работал… | tolerance exact | value = A2's earlier order: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.05' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'M-112' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 105) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 105) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 105)))) AND k.code IN ('front_struts_pair') AND o.purchase_order_number = '4398A' AND o.total - o.tax_total = 1119.98))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE v.unit_number = 'Т-09' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('water_pump') AND o.purchase_order_number = '96/07' AND o.total = 12279.80))::int END AS value;

-- nf.conv.06 | expected en=["The first date, Friday, was given to him when the part was ordered, on the day after the car came in, outside the chat and outside any hand-written call (call 15: 'Fella told me Friday').", "ERP: the purchase order for the angle gear was promised for 7 days before T, then for west's 4th full open day before T; on the day of message 3 the supplier said 'early next week' with no tracking number.", "Chad repeated call 15's promise in writing at 17:21 on the day of the call.", "He has a rental car since 8 days before T.", "The missed call is at 09:12 and call 16 at 14:20, as story call 16 has th… ru=["Первый срок, суббота, ему назвали в день заказа насоса (на следующий день после приёма машины), вне чата и вне написанных звонков (звонок 15: «Мне сначала сказали — в субботу»).", "ERP: заказ поставщику на насос ЭГУР обещан на субботу (6 дней до T), перенесён на понедельник (4 дня до T); в день третьего сообщения поставщик говорит «на следующей неделе» и не даёт трек-номер.", "Первое сообщение пришло в 20:41, после закрытия, в день смены слота 24; первым ответил слот 23 на следующий день, в свою смену, и чат стал его.", "Во вторник ему нужно было ехать в Набережные Челны; на такси он, по его… | tolerance exact | value = the nine-day car's two purchase orders and their promise dates: en 3, ru 3
-- want: value == 3
SELECT 'nf.conv.06' AS ledger_key, CASE :'cfg' WHEN 'en' THEN ((SELECT count(*) FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+16155550115' AND o.status = 'waiting_parts')) = 2)::int + (EXISTS (SELECT 1 FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+16155550115' AND o.status = 'waiting_parts') AND po.status = 'cancelled' AND po.promised_at::date = :'T'::date - 7))::int + (EXISTS (SELECT 1 FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+16155550115' AND o.status = 'waiting_parts') AND po.status = 'ordered' AND po.received_at IS NULL AND po.promised_at::date < :'T'::date))::int ELSE ((SELECT count(*) FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+79075269879' AND o.status = 'waiting_parts')) = 2)::int + (EXISTS (SELECT 1 FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+79075269879' AND o.status = 'waiting_parts') AND po.status = 'cancelled' AND po.promised_at::date = :'T'::date - 6))::int + (EXISTS (SELECT 1 FROM shop.purchase_order po WHERE po.repair_order_id = (SELECT o.repair_order_id FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id WHERE c.phone = '+79075269879' AND o.status = 'waiting_parts') AND po.status = 'ordered' AND po.received_at IS NULL AND po.promised_at::date < :'T'::date))::int END AS value;

-- nf.conv.08 | expected en=["Patsy Greer, a regular of the Bonny Oaks shop, 2013 Buick Enclave, rear brakes recommended at her last visit; an appointment on the Wednesday of week W+1 at 13:00.", "Angie offers no time of her own inside the week she has asked off (S5): the Wednesday before it with her, or the Friday with Josh (slot 17).", "The contact's picture: a white Buick Enclave under a carport."] ru=["Марина Захарова, постоянная клиентка east, Volkswagen Polo 2017 (в образце была Kia Rio 2017: такая же машина в named_customers.json записана на другую Марину того же сервиса), задние колодки рекомендованы на прошлом ТО; запись на понедельник недели W+1, 14:00, принимает слот 16.", "«Принимаю я» сказано про понедельник, её последний рабочий день перед неделей отпуска (S5); на дни внутри этой недели она никого на себя не записывает и вторым временем называет субботу у Артёма (слот 17), его смену.", "Картинка контакта: набережная Волги зимой."] | tolerance exact | value = the booking in W+1: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.08' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Greer%' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND a.starts_at::date BETWEEN :'pub_week'::date AND :'pub_week'::date + 4 AND a.starts_at::time = '13:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Захарова%' AND v.model ILIKE '%Polo%' AND v.year = 2017 AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND a.starts_at::date BETWEEN :'pub_week'::date - 3 AND :'pub_week'::date + 4 AND a.starts_at::time = '14:00'))::int END AS value;

-- nf.conv.09 | expected en=["Darryl Poteet, 2011 Chevrolet Silverado 1500, alternator replaced on the Thursday of week T-18 at main: 766.37 at list, 852.01 with shop supplies and tax; he was given the pre-tax figure on the phone that morning.", "The contact's picture: a red Chevrolet Silverado at a boat ramp."] ru=["Ильнур Сабиров (в Telegram «Ильнур»), Renault Duster 2014: замена переднего левого ступичного подшипника на main в первый рабочий день слота 5 начиная с четверга недели T-18: 7 902 по прайсу, 8 019,99 с расходными материалами (НДС в том числе); утром по телефону ему назвали сумму без расходных материалов.", "Картинка контакта: белый Duster у реки."] | tolerance exact | value = the order and its total: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.09' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Poteet%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 123) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 123) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 123)))) AND k.code IN ('alternator') AND o.total = 852.01))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Сабиров%' AND v.model ILIKE '%Duster%' AND v.year = 2014 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 123) AND (date_trunc('week', :'T'::timestamp)::date - 123) + 3 AND k.code IN ('wheel_bearing') AND o.total = 8019.99))::int END AS value;

-- nf.conv.10 | expected en=["Kim Arnett, (423) 555-0274 (tier B of phones.md), 2012 Ford Escape; a cooling system pressure test at main on the Monday of week T-8 at 14:00.", "The photo IMG_2087.jpg (picture pool 'puddle-under-car')."] ru=["Объявление сервиса на Авито «Замена сцепления: Granta, Vesta, Largus, Logan. Московское шоссе» (идентификаторы под .example).", "Руслан, LADA Granta 2018, 8 кл., свой комплект сцепления Valeo; запись — по его звонку (звонок в набор звонков не входит).", "У контакта нет картинки."] | tolerance exact | value = the booking or the order: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.10' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550274' OR c.phone = '+14235550274') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 56) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 56) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 56)))) AND a.starts_at::time = '14:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Руслан%' AND v.model ILIKE '%Granta%' AND v.year = 2018 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('clutch_kit')))::int END AS value;

-- nf.conv.11 | expected en=["Shonda Ellis (Telegram name 'Shonda E.'), 2015 Kia Sorento, at main on the Tuesday of week T-11: oil change; rear brake pads approved, 260.31; cabin air filter declined, 67.94.", "The photos sorento_rear_pad.jpg and sorento_cabin_filter.jpg (picture pools 'worn-pad', 'dirty-cabin-filter').", "The contact has no picture."] ru=["Ксения Мартынова, LADA Vesta 2019: замена масла на main в субботу недели T-11, 10:00.", "Картинка контакта: рыжий кот на подоконнике."] | tolerance exact | value = the raised jobs or the booking: en 2, ru 1
-- want: value == (2 if cfg == 'en' else 1)
SELECT 'nf.conv.11' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Ellis%' AND v.model ILIKE '%Sorento%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 76) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 76) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 76)))) AND k.code IN ('rear_brake_pads') AND j.status = 'approved'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Ellis%' AND v.model ILIKE '%Sorento%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 76) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 76) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 76)))) AND k.code IN ('cabin_air_filter') AND j.status = 'declined'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Мартынова%' AND v.model ILIKE '%Vesta%' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 72) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 72) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 72)))) AND a.starts_at::time = '10:00'))::int END AS value;

-- nf.conv.12 | expected en=["Reggie Dorsey, (423) 555-0318 (tier B), an alignment at main moved from the Monday to the Thursday of week T-4, 08:00."] ru=["Эльвира Насибуллина (в Telegram «Эльвира»), Kia Sportage 2017, main, первый рабочий день слота 6 начиная с пятницы недели T-5: ТО; стойки стабилизатора согласованы, 4 463; щётки стеклоочистителя — отказ, 3 403.", "Фото sportage_stoyka.jpg и sportage_schetki.jpg (пулы 'worn-part-sway-link', 'worn-wiper').", "У контакта нет картинки."] | tolerance exact | value = the moved booking or the raised jobs: en 1, ru 2
-- want: value == (1 if cfg == 'en' else 2)
SELECT 'nf.conv.12' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550318' OR c.phone = '+14235550318') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 25) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 25) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 25)))) AND a.starts_at::time = '08:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Насибуллина%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 31) AND (date_trunc('week', :'T'::timestamp)::date - 31) + 3 AND k.code IN ('sway_bar_links') AND j.status = 'approved'))::int + (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Насибуллина%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND o.opened_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 31) AND (date_trunc('week', :'T'::timestamp)::date - 31) + 3 AND k.code IN ('wiper_blades') AND j.status = 'declined'))::int END AS value;

-- nf.conv.13 | expected en=["Brianna Cagle (Telegram name 'Brianna C.'), 2016 Nissan Altima, an oil change at main on the Friday of week T-12 at 08:30.", "The contact has no picture."] ru=["Объявление сервиса на Авито «Ремонт ходовой: ШРУСы, стойки, рычаги, ступичные подшипники. Московское шоссе».", "«Саня», Renault Logan 2014: замена левого наружного ШРУСа на main на следующий день после чата, 09:00; запись без телефона.", "Картинка контакта: серебристый Logan у гаражей."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.13' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Cagle%' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 80) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 80) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 80)))) AND a.starts_at::time = '08:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND a.starts_at::time = '09:00' AND a.contact_name = 'Саня' AND a.contact_phone IS NULL))::int END AS value;

-- nf.conv.14 | expected en=["Jerome Purcell, (423) 555-0391 (tier B), 2017 Toyota Camry, a brake fluid flush at main on the Wednesday of week T-3 at 10:00."] ru=["Денис, +7 907 215-63-08, Kia Rio R15: сезонная замена шин на main в первый рабочий день слота 7 начиная со вторника недели T-3, 18:00; спросил про хранение летних колёс (3 000 за сезон)."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.14' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550391' OR c.phone = '+14235550391') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'East Main') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 19) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 19) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 19)))) AND a.starts_at::time = '10:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79072156308' OR c.phone = '+79072156308') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND a.starts_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 20) AND (date_trunc('week', :'T'::timestamp)::date - 20) + 3 AND a.starts_at::time = '18:00'))::int END AS value;

-- nf.conv.15 | expected en=["Gloria Yancey, 2014 Toyota Highlander: front brakes at east in week T-16; a no-charge brake noise check on the Wednesday of week T-15 at 13:00 (an anti-rattle clip reseated): a warranty order pointing at the first one.", "The contact's picture: sunrise over a lake."] ru=["Галина Петровна Сорокина, LADA Granta 2020, east: заправка кондиционера на неделе T-16; бесплатная проверка на утечку по гарантии на следующий день после чата, 09:30 (гарантийный заказ со ссылкой на первый).", "Картинка контакта: куст сирени у забора."] | tolerance exact | value = the warranty order: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.15' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.model ILIKE '%Highlander%' AND v.year = 2014 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 103) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 103) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 103)))) AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE c.name ILIKE '%Сорокина%' AND v.model ILIKE '%Granta%' AND v.year = 2020 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND o.comeback_of_id IS NOT NULL AND o.order_type = 'warranty' AND o.total = 0))::int END AS value;

-- nf.conv.16 | expected en=["Tasha Reed, (423) 555-0407 (tier B): a pre-purchase inspection of a 2015 Honda Pilot at east on the Wednesday of week T-7 at 08:30."] ru=["Антон, +7 907 441-09-27: диагностика перед покупкой Skoda Octavia 2014 на east в среду недели T-7, 11:00; принимает слот 17."] | tolerance exact | value = the pre-purchase booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.16' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+14235550407' OR c.phone = '+14235550407') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 47) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 47) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 47)))) AND a.starts_at::time = '08:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79074410927' OR c.phone = '+79074410927') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 47) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 47) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 47)))) AND a.starts_at::time = '11:00'))::int END AS value;

-- nf.conv.17 | expected en=["Dwight Hensley, 2013 Ford F-150: front sway bar links (220.26) recommended at east at an oil change on the Thursday of week T-12 and declined the next day.", "The contact's picture: a blue F-150 with a boat trailer."] ru=["Вадим Корнеев («ВКонтакте»), Chevrolet Cruze 2012: спрашивал сход-развал на east (3 000) после удара о яму; не приехал.", "Картинка контакта: чёрный Cruze на парковке."] | tolerance exact | value = the declined raised job (en only): en 1, ru 0
-- want: value == (1 if cfg == 'en' else 0)
SELECT 'nf.conv.17' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Hensley%' AND v.model ILIKE '%F-150%' AND v.year = 2013 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 81) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 81) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 81)))) AND k.code IN ('sway_bar_links') AND j.status = 'declined'))::int ELSE 0 END AS value;

-- nf.conv.18 | expected en=["Hector Ortega, (423) 555-0452 (tier B): four customer-supplied tires mounted and balanced at east on the Friday of week T-20 at 14:00, 100.00 plus disposal at 3.50 a tire.", "The shop mounts tires a customer brings (said by slot 17; the public pages do not say)."] ru=["Объявление сервиса на Авито «Шиномонтаж, балансировка, сезонное хранение шин. Новый город».", "«Олег», кроссовер R16: шиномонтаж на east в среду недели T-4, 18:30; спрашивал про хранение.", "У контакта нет картинки."] | tolerance exact | value = the order or the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.18' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+14235550452' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 136) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 136) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 136)))) AND k.code IN ('new_tyres_fitted')))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 26) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 26) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 26)))) AND a.starts_at::time = '18:30' AND (a.contact_name ILIKE 'Олег%' OR c.name ILIKE '%Олег%')))::int END AS value;

-- nf.conv.19 | expected en=["Buddy Carver, a regular of west, brings his mother's Buick (a whine when turning, a repeat) as a walk-in on the Tuesday of week T-16.", "The contact has no picture."] ru=["Марат Нуриев, давний клиент west, отцовская «Нива» (перегрев, повторно), визит без записи во вторник недели T-16.", "Картинка контакта: река, камыши и закат."] | tolerance exact | value = the walk-in visit: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.19' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE v.make ILIKE '%Buick%' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 111) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 111) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 111)))) AND NOT EXISTS (SELECT 1 FROM shop.appointment x WHERE x.repair_order_id = o.repair_order_id)))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id WHERE (v.model ILIKE '%Нива%' OR v.model ILIKE '%Niva%') AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 111) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 111) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 111)))) AND NOT EXISTS (SELECT 1 FROM shop.appointment x WHERE x.repair_order_id = o.repair_order_id)))::int END AS value;

-- nf.conv.20 | expected en=["Sharon Whitfield, (615) 555-0236 (tier B): a water pump replaced at west, picked up on the Tuesday of week T-9; the bill carries shop supplies of 17.55."] ru=["Фарид, +7 907 551-34-26: замена помпы на west, машину забрал во вторник недели T-9; в наряде расходные материалы 125,40 (3 % от работы 4 180)."] | tolerance exact | value = the supplies on the bill: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.20' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+16155550236' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('water_pump') AND EXISTS (SELECT 1 FROM shop.order_fee f WHERE f.repair_order_id = o.repair_order_id AND f.kind = 'shop_supplies' AND f.amount = 17.55)))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79075513426' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('water_pump') AND EXISTS (SELECT 1 FROM shop.order_fee f WHERE f.repair_order_id = o.repair_order_id AND f.kind = 'shop_supplies' AND f.amount = 125.40)))::int END AS value;

-- nf.conv.22 | expected en=["Monica Reyes, (615) 555-0289 (tier B), 2016 Hyundai Tucson, at west on the Wednesday of week T-5: rear brake pads at 3 mm recommended on the invoice (225.77), not sold."] ru=["Регина, +7 907 612-05-84: машину забрала на west накануне чата; в наряде рекомендация «замена передних тормозных колодок, остаток 2 мм» (4 560), не продана. Марка машины в чате не названа."] | tolerance exact | value = the recommendation not sold: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.22' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+16155550289' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 33) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 33) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 33)))) AND k.code IN ('rear_brake_pads') AND j.status = 'declined'))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.phone = '+79076120584' AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN :'G'::date AND :'T'::date + 14 AND k.code IN ('front_brake_pads') AND j.status = 'declined'))::int END AS value;

-- nf.conv.23 | expected en=["Latoya Greene, 2014 Chevrolet Equinox, 96,000 miles, at west on the Friday of week T-10: check engine diagnosis 135.00, ignition coil 153.86, spark plugs 222.28; 579.50 with shop supplies (16.88) and Nashville's sales tax (tax.rate.west, 9.75 %).", "The file Estimate_Equinox_Greene.pdf (picture pool 'estimate-pdf').", "The contact's picture: a gray Chevrolet Equinox in a parking garage."] ru=["Тимур Валеев, Hyundai Creta 2018, west, первый рабочий день слота 24 начиная с пятницы недели T-10: опрессовка 950, замена помпы 13 366, замена ремня 3 313,50; итог с расходными материалами в чате: 17 836,41, НДС в том числе.", "Файл Smeta_Creta_Valeev.pdf (пул 'estimate-pdf').", "Картинка контакта: белая Creta у подъезда."] | tolerance exact | value = the estimate: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.23' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Greene%' AND v.model ILIKE '%Equinox%' AND v.year = 2014 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (o.opened_at::date - (date_trunc('week', :'T'::timestamp)::date - 66) BETWEEN 0 AND 4 AND (o.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 66)))) AND k.code IN ('check_engine_diag') AND o.total = 579.50))::int ELSE (EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id JOIN shop.canned_job k ON k.canned_job_id = j.canned_job_id WHERE c.name ILIKE '%Валеев%' AND v.model ILIKE '%Creta%' AND v.year = 2018 AND o.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND o.opened_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 66) AND (date_trunc('week', :'T'::timestamp)::date - 66) + 3 AND k.code IN ('water_pump')))::int END AS value;

-- nf.conv.24 | expected en=["Deion Marshall, (615) 555-0347 (tier B), 2017 Kia Soul: a battery and charging test at west on the Tuesday of week T-17 at 11:30."] ru=["Объявление сервиса на Авито «Заправка и ремонт автокондиционеров. Казань, Техническая».", "«Айдар», Hyundai Solaris 2019: заправка кондиционера на west в первый рабочий день слота 24 начиная со вторника недели T-17, 17:00.", "У контакта нет картинки."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.24' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+16155550347' OR c.phone = '+16155550347') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 118) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 118) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 118)))) AND a.starts_at::time = '11:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE v.model ILIKE '%Solaris%' AND v.year = 2019 AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Техническая') AND a.starts_at::date BETWEEN (date_trunc('week', :'T'::timestamp)::date - 118) AND (date_trunc('week', :'T'::timestamp)::date - 118) + 3 AND a.starts_at::time = '17:00'))::int END AS value;

-- nf.conv.25 | expected en=["Kenny Dillard, (615) 555-0412 (tier B), 2013 Dodge Charger: a check engine diagnosis at west on the Thursday of week T-13 at 07:30."] ru=["Сергей, +7 907 302-71-45, LADA Priora 2012: компьютерная диагностика двигателя на east в четверг недели T-13, 18:00; принимает слот 17."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.25' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+16155550412' OR c.phone = '+16155550412') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Charlotte Pike') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 88) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 88) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 88)))) AND a.starts_at::time = '07:30'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE (a.contact_phone = '+79073027145' OR c.phone = '+79073027145') AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Инженерный') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 88) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 88) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 88)))) AND a.starts_at::time = '18:00'))::int END AS value;

-- nf.conv.26 | expected en=["Dot Kirby, 2012 Toyota Camry, a regular of east: tires balanced in March for a highway shake, a battery light in June; a brake inspection on the Thursday of week T-6 at 09:00.", "The contact has no picture."] ru=["Николай Иванович Кузьмин (в Telegram «Николай Иванович»), Toyota Corolla 2010, постоянный клиент main: в апреле сезонная замена шин, в мае сход-развал; запись на четверг недели T-6, 11:00: сезонная замена шин и сход-развал.", "У контакта нет картинки."] | tolerance exact | value = the booking: en 1, ru 1
-- want: value == 1
SELECT 'nf.conv.26' AS ledger_key, CASE :'cfg' WHEN 'en' THEN (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Kirby%' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Bonny Oaks') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 39) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 39) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 39)))) AND a.starts_at::time = '09:00'))::int ELSE (EXISTS (SELECT 1 FROM shop.appointment a LEFT JOIN shop.customer c ON c.customer_id = a.customer_id LEFT JOIN shop.vehicle v ON v.vehicle_id = a.vehicle_id WHERE c.name ILIKE '%Кузьмин%' AND a.location_id = (SELECT l.location_id FROM shop.location l WHERE l.name = 'Московское шоссе') AND (a.starts_at::date - (date_trunc('week', :'T'::timestamp)::date - 39) BETWEEN 0 AND 4 AND (a.starts_at::date = (date_trunc('week', :'T'::timestamp)::date - 39) OR NOT EXISTS (SELECT 1 FROM shop.repair_order z WHERE z.opened_at::date = (date_trunc('week', :'T'::timestamp)::date - 39)))) AND a.starts_at::time = '11:00'))::int END AS value;

-- Invariants: physical sense of the shop's records, each a count that must be 0. They read no ledger row; the
-- shop clock is each shop's own (T on it is T on the home clock moved into the shop's zone).

-- inv.time_overlap | expected 0 | tolerance exact | a mechanic's time entry that starts before one of his earlier entries ends (a running clock ends at T)
-- want: value == 0
SELECT 'inv.time_overlap' AS ledger_key, count(*) AS value
FROM (SELECT t.clock_in, max(coalesce(t.clock_out, :'T'::timestamp)) OVER (PARTITION BY t.technician_id ORDER BY t.clock_in, t.time_entry_id ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS busy_until
      FROM shop.time_entry t) x
WHERE x.clock_in < x.busy_until;

-- inv.day_over_shift | expected 0 | tolerance exact | a mechanic's day, first clock-in to last clock-out, longer than his shift (ledger roster.mechanic_pattern: en 07:30-16:00, Saturday 08:00-13:00; ru 09:00-18:00)
-- want: value == 0
SELECT 'inv.day_over_shift' AS ledger_key, count(*) AS value
FROM (SELECT t.clock_in::date AS d, max(coalesce(t.clock_out, :'T'::timestamp)) - min(t.clock_in) AS span FROM shop.time_entry t GROUP BY t.technician_id, t.clock_in::date) x
WHERE x.span > CASE WHEN :'cfg' = 'ru' THEN interval '9 hours' WHEN extract(isodow FROM x.d) = 6 THEN interval '5 hours' ELSE interval '8 hours 30 minutes' END;

-- inv.work_outside_employment | expected 0 | tolerance exact | time entries, labour lines and orders written by someone on a day before his hired_on or after his left_on
-- want: value == 0
SELECT 'inv.work_outside_employment' AS ledger_key,
       (SELECT count(*) FROM shop.time_entry t JOIN shop.employee e ON e.employee_id = t.technician_id WHERE t.clock_in::date < e.hired_on OR t.clock_in::date > e.left_on)
     + (SELECT count(*) FROM shop.order_labor l JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
         JOIN shop.employee e ON e.employee_id = l.technician_id WHERE o.opened_at::date > e.left_on)
     + (SELECT count(*) FROM shop.repair_order o JOIN shop.employee e ON e.employee_id = o.advisor_id WHERE o.opened_at::date < e.hired_on OR o.opened_at::date > e.left_on) AS value;

-- inv.status_outside_hours | expected 0 | tolerance exact | a status change on a day the shop did not trade (no till close; T's own day trades) or outside its hours (ledger site.hours.weekday, site.open_days); an account order paid by its statement is the office's event (inv.office_on_closed_day)
-- want: value == 0
SELECT 'inv.status_outside_hours' AS ledger_key, count(*) AS value
FROM shop.order_status_history h JOIN shop.repair_order o ON o.repair_order_id = h.repair_order_id JOIN shop.location l ON l.location_id = o.location_id
WHERE NOT (h.status = 'paid' AND o.statement_id IS NOT NULL) AND (NOT (EXISTS (SELECT 1 FROM shop.cash_drawer_close d WHERE d.location_id = o.location_id AND d.business_date = h.changed_at::date)
           OR h.changed_at::date = ((:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone)::date)
   OR h.changed_at::time < CASE WHEN :'cfg' = 'ru' THEN time '09:00' WHEN extract(isodow FROM h.changed_at) = 6 THEN time '08:00' ELSE time '07:30' END
   OR h.changed_at::time > CASE WHEN :'cfg' = 'ru' THEN time '20:00' WHEN extract(isodow FROM h.changed_at) = 6 THEN time '13:00' ELSE time '17:30' END);

-- inv.office_on_closed_day | expected 0 | tolerance exact | a statement payment received on a Saturday, a Sunday or a closed date (a weekday the flagship did not trade): the office books bills on its working days; T's own day is open and has no till close yet
-- want: value == 0
SELECT 'inv.office_on_closed_day' AS ledger_key, count(*) AS value
FROM shop.payment p
WHERE p.statement_id IS NOT NULL
  AND (extract(isodow FROM p.received_at) IN (6, 7) OR p.received_at::date < :'T'::timestamp::date AND NOT EXISTS (SELECT 1 FROM shop.cash_drawer_close d WHERE d.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END) AND d.business_date = p.received_at::date));

-- inv.issue_before_receipt | expected 0 | tolerance exact | a part issued to an order before the purchase order bought for that order and part was received
-- want: value == 0
SELECT 'inv.issue_before_receipt' AS ledger_key, count(*) AS value
FROM shop.stock_movement m JOIN shop.order_part op ON op.order_part_id = m.order_part_id JOIN shop.order_job j ON j.order_job_id = op.order_job_id
WHERE m.kind = 'issue'
  AND EXISTS (SELECT 1 FROM shop.purchase_order po JOIN shop.purchase_order_line pl ON pl.purchase_order_id = po.purchase_order_id
              WHERE po.repair_order_id = j.repair_order_id AND pl.part_id = m.part_id AND po.status <> 'cancelled')
  AND NOT EXISTS (SELECT 1 FROM shop.purchase_order po JOIN shop.purchase_order_line pl ON pl.purchase_order_id = po.purchase_order_id
                  WHERE po.repair_order_id = j.repair_order_id AND pl.part_id = m.part_id AND po.received_at <= m.moved_at);

-- inv.issue_after_completed | expected 0 | tolerance exact | a part issued to an order after the order was first completed
-- want: value == 0
SELECT 'inv.issue_after_completed' AS ledger_key, count(*) AS value
FROM shop.stock_movement m JOIN shop.order_part op ON op.order_part_id = m.order_part_id JOIN shop.order_job j ON j.order_job_id = op.order_job_id
WHERE m.kind = 'issue' AND m.moved_at > (SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = j.repair_order_id AND h.status = 'completed');

-- inv.stock_below_zero | expected 0 | tolerance exact | a shop's running stock of a part below zero at the end of a day it moved (the sum of its movements so far)
-- want: value == 0
SELECT 'inv.stock_below_zero' AS ledger_key, count(*) FILTER (WHERE x.on_hand < 0) AS value, count(*) AS part_days
FROM (SELECT sum(sum(m.quantity)) OVER (PARTITION BY m.location_id, m.part_id ORDER BY m.moved_at::date) AS on_hand
      FROM shop.stock_movement m GROUP BY m.location_id, m.part_id, m.moved_at::date) x;

-- inv.payment_before_open | expected 0 | tolerance exact | money received for an order before the order was opened, or for a statement before it was issued; a deposit at booking is allowed (generator-spec 4.7): after the booking, by card or transfer, or in cash at a walk-in booking
-- want: value == 0
SELECT 'inv.payment_before_open' AS ledger_key,
       (SELECT count(*) FROM shop.payment p JOIN shop.repair_order o ON o.repair_order_id = p.repair_order_id
         WHERE p.received_at < o.opened_at
           AND NOT (p.kind = 'deposit' AND EXISTS (SELECT 1 FROM shop.appointment a WHERE a.repair_order_id = o.repair_order_id AND a.booked_at <= p.received_at AND (p.method <> 'cash' OR a.source = 'walk_in'))))
     + (SELECT count(*) FROM shop.payment p JOIN shop.statement s ON s.statement_id = p.statement_id WHERE p.received_at::date < s.issued_on) AS value;

-- inv.customer_after_first_order | expected 0 | tolerance exact | a customer record created after his first order was opened
-- want: value == 0
SELECT 'inv.customer_after_first_order' AS ledger_key, count(*) AS value
FROM shop.customer c WHERE c.created_at > (SELECT min(o.opened_at) FROM shop.repair_order o WHERE o.customer_id = c.customer_id);

-- inv.comeback_before_done | expected 0 | tolerance exact | a comeback opened before the order it repeats was first completed
-- want: value == 0
SELECT 'inv.comeback_before_done' AS ledger_key, count(*) AS value
FROM shop.repair_order cb
WHERE cb.comeback_of_id IS NOT NULL
  AND cb.opened_at < coalesce((SELECT min(h.changed_at) FROM shop.order_status_history h WHERE h.repair_order_id = cb.comeback_of_id AND h.status = 'completed'), 'infinity');

-- inv.order_totals_off_lines | expected 0 | tolerance exact | an order whose totals differ from its live lines (dictionary D1: the approved jobs once one is approved, else every job; a warranty or goodwill order discounts the whole amount; tax on top when not included)
-- want: value == 0
SELECT 'inv.order_totals_off_lines' AS ledger_key, count(*) AS value
FROM (SELECT o.*, (SELECT coalesce(sum(l.amount), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND (j.status = 'approved' OR NOT x.any_approved)) AS labour,
             (SELECT coalesce(sum(l.discount), 0) FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND (j.status = 'approved' OR NOT x.any_approved)) AS line_discount,
             (SELECT coalesce(sum(round(p.quantity * p.unit_price, 2)), 0) FROM shop.order_job j JOIN shop.order_part p ON p.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND (j.status = 'approved' OR NOT x.any_approved)) AS parts,
             (SELECT coalesce(sum(s.price), 0) FROM shop.order_job j JOIN shop.order_sublet s ON s.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND (j.status = 'approved' OR NOT x.any_approved)) AS sublet,
             (SELECT coalesce(sum(f.amount), 0) FROM shop.order_fee f WHERE f.repair_order_id = o.repair_order_id) AS fees
      FROM shop.repair_order o CROSS JOIN LATERAL (SELECT EXISTS (SELECT 1 FROM shop.order_job j WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS any_approved) x) t
WHERE t.labor_total <> t.labour OR t.parts_total <> t.parts OR t.sublet_total <> t.sublet OR t.fees_total <> t.fees
   OR t.discount_total <> CASE WHEN t.order_type IN ('warranty', 'goodwill') THEN t.labour + t.parts + t.sublet + t.fees ELSE t.line_discount END
   OR t.total <> t.labor_total + t.parts_total + t.sublet_total + t.fees_total - t.discount_total + CASE WHEN t.tax_included THEN 0 ELSE t.tax_total END;

-- inv.statement_total_off | expected 0 | tolerance exact | a statement whose total differs from the totals of its orders (dictionary D4)
-- want: value == 0
SELECT 'inv.statement_total_off' AS ledger_key, count(*) AS value
FROM shop.statement s WHERE s.total <> (SELECT coalesce(sum(o.total), 0) FROM shop.repair_order o WHERE o.statement_id = s.statement_id);

-- inv.after_t | expected 0 | tolerance exact | anything dated after T on the shop's clock: an order opened, a status change, a clock-in, a payment, a delivery, a stock movement, or an appointment after T with an order or a kept or missed visit
-- want: all(v == 0 for v in list(row.values())[1:])
SELECT 'inv.after_t' AS ledger_key,
       (SELECT count(*) FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id WHERE o.opened_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS orders,
       (SELECT count(*) FROM shop.order_status_history h JOIN shop.repair_order o ON o.repair_order_id = h.repair_order_id JOIN shop.location l ON l.location_id = o.location_id WHERE h.changed_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS statuses,
       (SELECT count(*) FROM shop.time_entry t JOIN shop.order_job j ON j.order_job_id = t.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id JOIN shop.location l ON l.location_id = o.location_id
         WHERE greatest(t.clock_in, t.clock_out) > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS clocks,
       (SELECT count(*) FROM shop.payment p LEFT JOIN shop.repair_order o ON o.repair_order_id = p.repair_order_id
         JOIN shop.location l ON l.location_id = coalesce(o.location_id, (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END))
         WHERE p.received_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS payments,
       (SELECT count(*) FROM shop.purchase_order po JOIN shop.location l ON l.location_id = po.location_id WHERE po.received_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS deliveries,
       (SELECT count(*) FROM shop.stock_movement m JOIN shop.location l ON l.location_id = m.location_id WHERE m.moved_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone) AS movements,
       (SELECT count(*) FROM shop.appointment a JOIN shop.location l ON l.location_id = a.location_id
         WHERE a.starts_at > (:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone
           AND (a.repair_order_id IS NOT NULL OR a.status IN ('arrived', 'no_show'))) AS appointments;

-- inv.open_from_earlier_day | expected 0 | tolerance exact | an order opened before T's day and open at T, other than the planted ones: the cars waiting for parts (s6.waiting_at_t), the orders open over 60 days (s15.dates) and slot 8's second look (board.second_look_open, the warranty order of en Dogwood Lane Florals, ru ИП Абрамова)
-- want: value == 0
SELECT 'inv.open_from_earlier_day' AS ledger_key, count(*) AS value, string_agg(o.number || ' ' || o.status, ', ' ORDER BY o.opened_at) AS orders
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined', 'waiting_parts')
  AND NOT (o.order_type = 'warranty' AND c.name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Dogwood Lane Florals' ELSE 'Абрамова' END || '%')
  AND o.opened_at::date < ((:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone)::date
  AND o.opened_at >= :'T'::timestamp - interval '60 days';

-- inv.status_not_last_row | expected 0 | tolerance exact | an order whose status is not its last status history row (dictionary D2), or whose history is out of order (a status before the order was opened); and jobs decided before their order was opened
-- want: value == 0 and row['jobs'] == 0
SELECT 'inv.status_not_last_row' AS ledger_key,
       (SELECT count(*) FROM shop.repair_order o
         WHERE o.status IS DISTINCT FROM (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1)
            OR EXISTS (SELECT 1 FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at < o.opened_at)) AS value,
       (SELECT count(*) FROM shop.order_job j JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id WHERE j.decided_at < o.opened_at) AS jobs;

-- inv.status_path | expected 0 | tolerance exact | orders whose statuses do not follow generator-spec 4.5: estimate first; estimate to approved, declined or void; approved to in_progress; in_progress to waiting_parts, waiting_sublet or completed; waiting_parts and waiting_sublet back to in_progress; completed to invoiced; invoiced to paid, or back to completed (a re-billed order); paid to void only on the fired advisor's planted voids (s2.f1.second)
-- want: value == 0
SELECT 'inv.status_path' AS ledger_key, count(DISTINCT x.repair_order_id) AS value
FROM (SELECT h.repair_order_id, h.status, lag(h.status, 1, 'start') OVER (PARTITION BY h.repair_order_id ORDER BY h.changed_at, h.order_status_history_id) AS prev
      FROM shop.order_status_history h) x
JOIN shop.repair_order o ON o.repair_order_id = x.repair_order_id JOIN shop.employee e ON e.employee_id = o.advisor_id
WHERE (x.prev, x.status) NOT IN (('start', 'estimate'), ('estimate', 'approved'), ('estimate', 'declined'), ('estimate', 'void'), ('approved', 'in_progress'),
                                 ('in_progress', 'waiting_parts'), ('in_progress', 'waiting_sublet'), ('in_progress', 'completed'), ('waiting_parts', 'in_progress'),
                                 ('waiting_sublet', 'in_progress'), ('completed', 'invoiced'), ('invoiced', 'paid'), ('invoiced', 'completed'))
  AND NOT ((x.prev, x.status) = ('paid', 'void') AND e.first_name = CASE :'cfg' WHEN 'en' THEN 'Brent' ELSE 'Артур' END AND e.last_name = CASE :'cfg' WHEN 'en' THEN 'Lassiter' ELSE 'Назаров' END);

-- inv.clock_before_open | expected 0 | tolerance exact | a clock-in on a job before its order was opened
-- want: value == 0
SELECT 'inv.clock_before_open' AS ledger_key, count(*) AS value
FROM shop.time_entry t JOIN shop.order_job j ON j.order_job_id = t.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
WHERE t.clock_in < o.opened_at;

-- inv.stock_outside_hours | expected 0 | tolerance exact | a stock movement or a purchase order received on a day its shop did not trade or outside its hours (ledger site.hours.weekday, site.open_days), leaving out each shop's opening-stock day (its first movement) and T's day
-- want: value == 0
SELECT 'inv.stock_outside_hours' AS ledger_key, count(*) AS value
FROM (SELECT m.location_id, m.moved_at AS at FROM shop.stock_movement m
      UNION ALL SELECT po.location_id, po.received_at FROM shop.purchase_order po WHERE po.received_at IS NOT NULL) e
JOIN shop.location l ON l.location_id = e.location_id
WHERE e.at::date > (SELECT min(m.moved_at)::date FROM shop.stock_movement m WHERE m.location_id = e.location_id)
  AND e.at::date < ((:'T'::timestamp AT TIME ZONE CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE l.time_zone)::date
  AND (NOT EXISTS (SELECT 1 FROM shop.cash_drawer_close d WHERE d.location_id = e.location_id AND d.business_date = e.at::date)
       OR e.at::time < CASE WHEN :'cfg' = 'ru' THEN time '09:00' WHEN extract(isodow FROM e.at) = 6 THEN time '08:00' ELSE time '07:30' END
       OR e.at::time > CASE WHEN :'cfg' = 'ru' THEN time '20:00' WHEN extract(isodow FROM e.at) = 6 THEN time '13:00' ELSE time '17:30' END);

-- inv.tax_off_formula | expected 0 | tolerance exact | an order whose tax_total is not its formula (dictionary repair_order.tax_total): en the order's rate on the amount before tax, rounded to the cent; ru the VAT inside, total - round(total / (1 + rate / 100), 2); 0 on warranty and goodwill orders
-- want: value == 0
SELECT 'inv.tax_off_formula' AS ledger_key, count(*) AS value
FROM shop.repair_order o
WHERE o.tax_total <> CASE WHEN o.order_type IN ('warranty', 'goodwill') THEN 0
                          WHEN o.tax_included THEN o.total - round(o.total / (1 + o.tax_rate / 100), 2)
                          ELSE round((o.labor_total + o.parts_total + o.sublet_total + o.fees_total - o.discount_total) * o.tax_rate / 100, 2) END;

-- inv.clock_outside_shift | expected 0 | tolerance exact | a clock entry outside the mechanics' shift window (ledger roster.mechanic_pattern: en 07:30-16:00, Saturday 08:00-13:00; ru 09:00-18:00), or running past midnight
-- want: value == 0
SELECT 'inv.clock_outside_shift' AS ledger_key, count(*) AS value
FROM shop.time_entry t
WHERE t.clock_in::time < CASE WHEN :'cfg' = 'ru' THEN time '09:00' WHEN extract(isodow FROM t.clock_in) = 6 THEN time '08:00' ELSE time '07:30' END
   OR coalesce(t.clock_out, :'T'::timestamp)::time > CASE WHEN :'cfg' = 'ru' THEN time '18:00' WHEN extract(isodow FROM t.clock_in) = 6 THEN time '13:00' ELSE time '16:00' END
   OR t.clock_out::date > t.clock_in::date
   OR :'cfg' = 'en' AND extract(isodow FROM t.clock_in) = 7;

-- inv.comeback_mismatch | expected 0 | tolerance exact | a comeback at another shop, for another car or customer than the order it repeats, or not of type warranty or goodwill (generator-spec 4.6)
-- want: value == 0
SELECT 'inv.comeback_mismatch' AS ledger_key, count(*) AS value
FROM shop.repair_order cb JOIN shop.repair_order f ON f.repair_order_id = cb.comeback_of_id
WHERE cb.location_id <> f.location_id OR cb.vehicle_id <> f.vehicle_id OR cb.customer_id <> f.customer_id OR cb.order_type NOT IN ('warranty', 'goodwill');

-- Contrasts: what a story claims, as an inequality that holds on every build; each is named after the ledger row of
-- its story, with what it claims after the colon. acct.six.orders_share_now:visits, among them, is an exact count.

-- p10.billed_index:leads_main | contrast | expected slot 10 (the diagnostician) 15 % or more above main's mean and in its top two, slot 14 (the apprentice) lowest | main's standing technicians (the seasonal helper's row, pF4.billed_index, is read over his whole employment, not the 90 days) with 20 worked days or more in the 90 days, by billed hours a worked day as pNN.billed_index reads them (the shop's norm and season divide them all alike); the designed gap of slot 10 to slot 11 (0.05) is inside the noise, so "highest" is not claimed
-- want: row['slot_10'] in row['top_two'].split(', ') and row['slot_10_over_mean'] is not None and row['slot_10_over_mean'] >= 1.15 and row['lowest'] == row['slot_14']
SELECT 'p10.billed_index:leads_main' AS ledger_key, string_agg(x.name || ' ' || round(x.hours / x.days, 2), ', ' ORDER BY x.hours / x.days DESC) AS value,
       array_to_string((array_agg(x.name ORDER BY x.hours / x.days DESC))[1:2], ', ') AS top_two, (array_agg(x.name ORDER BY x.hours / x.days))[1] AS lowest,
       round(max(x.hours / x.days) FILTER (WHERE x.name = CASE :'cfg' WHEN 'en' THEN 'Kevin Lawson' ELSE 'Андрей Шубин' END) / avg(x.hours / x.days), 3) AS slot_10_over_mean,
       CASE :'cfg' WHEN 'en' THEN 'Kevin Lawson' ELSE 'Андрей Шубин' END AS slot_10, CASE :'cfg' WHEN 'en' THEN 'Hunter Varnell' ELSE 'Иван Сурков' END AS slot_14
FROM (SELECT m.first_name || ' ' || m.last_name AS name, sum(l.hours) AS hours, d.days
      FROM shop.employee m
      CROSS JOIN LATERAL (SELECT count(DISTINCT t.clock_in::date) AS days FROM shop.time_entry t
                          WHERE t.technician_id = m.employee_id AND t.clock_in > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM t.clock_in) < 6)) d
      JOIN shop.order_labor l ON l.technician_id = m.employee_id JOIN shop.order_job j ON j.order_job_id = l.order_job_id JOIN shop.repair_order o ON o.repair_order_id = j.repair_order_id
      WHERE m.role = 'technician' AND m.left_on IS NULL AND m.location_id = (SELECT location_id FROM shop.location WHERE name = CASE :'cfg' WHEN 'en' THEN 'East Main' ELSE 'Московское шоссе' END)
        AND d.days >= 20 AND j.status = 'approved' AND o.opened_at > :'T'::timestamp - interval '90 days' AND (:'cfg' = 'ru' OR extract(isodow FROM o.opened_at) < 6)
      GROUP BY m.employee_id, m.first_name, m.last_name, d.days) x;

-- acct.six.orders_share_now:visits | expected the sums of acct.A1.visits to acct.A6.visits: the first value in the block T-180 to T-150 days, the last in the last 30 days (75 and 62) | tolerance exact | the six accounts' visits as their acct.*.visits count them (orders not declined or void, warranty comebacks left out), the counts their shares are dealt from
-- want: row['before'] == sum(V(f'acct.A{i}.visits')[0] for i in range(1, 7)) and row['now'] == sum(V(f'acct.A{i}.visits')[5] for i in range(1, 7))
SELECT 'acct.six.orders_share_now:visits' AS ledger_key,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '180 days' AND o.opened_at <= :'T'::timestamp - interval '150 days') AS before,
       count(*) FILTER (WHERE o.opened_at > :'T'::timestamp - interval '30 days') AS now
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE c.payment_terms_days IS NOT NULL AND o.status NOT IN ('declined', 'void') AND o.order_type <> 'warranty';

-- parts.wait_over_a_day.west:over_home | contrast | expected above 0 | west's share of orders that waited for parts over a day less the home shops' share, in points (as parts.wait_over_a_day.west and .home)
-- want: value is not None and value > 0
SELECT 'parts.wait_over_a_day.west:over_home' AS ledger_key, round(x.west - x.home, 1) AS value, round(x.west, 1) AS west, round(x.home, 1) AS home
FROM (SELECT 100.0 * count(*) FILTER (WHERE w.west AND w.long_wait) / NULLIF(count(*) FILTER (WHERE w.west), 0) AS west,
             100.0 * count(*) FILTER (WHERE NOT w.west AND w.long_wait) / NULLIF(count(*) FILTER (WHERE NOT w.west), 0) AS home
      FROM (SELECT l.name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END AS west,
                   (SELECT coalesce(sum(extract(epoch FROM (coalesce(nx.changed_at, :'T'::timestamp) - h.changed_at)) / 86400), 0)
                    FROM shop.order_status_history h
                    LEFT JOIN LATERAL (SELECT min(h2.changed_at) AS changed_at FROM shop.order_status_history h2
                                       WHERE h2.repair_order_id = h.repair_order_id AND h2.changed_at > h.changed_at) nx ON true
                    WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts') > 1 AS long_wait
            FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
            WHERE o.status NOT IN ('declined', 'void')
              AND (l.name = CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END AND o.opened_at >= :'bought'::date
                   OR l.name <> CASE :'cfg' WHEN 'en' THEN 'Charlotte Pike' ELSE 'Техническая' END AND o.opened_at > :'T'::timestamp - interval '12 months')) w) x;

-- parts.on_time.V2:worst | contrast | expected V2 | the parts vendor with the lowest on-time share (as parts.on_time.V1 to V5: received on or before the promised day)
-- want: row['v2'] is not None and row['worst'] == row['v2']
SELECT 'parts.on_time.V2:worst' AS ledger_key, string_agg(x.name || ' ' || x.on_time, ', ' ORDER BY x.on_time) AS value,
       (array_agg(x.name ORDER BY x.on_time, x.name))[1] AS worst,
       (SELECT name FROM shop.vendor WHERE name LIKE '%' || CASE :'cfg' WHEN 'en' THEN 'Harpeth Valley Parts Supply' ELSE 'Казань-АвтоСнаб' END || '%') AS v2
FROM (SELECT v.name, round(100.0 * count(*) FILTER (WHERE po.received_at::date <= po.promised_at::date) / count(*), 1) AS on_time
      FROM shop.purchase_order po JOIN shop.vendor v ON v.vendor_id = po.vendor_id
      WHERE v.kind = 'parts' AND po.status IN ('received', 'partial') AND po.received_at IS NOT NULL
      GROUP BY v.vendor_id, v.name) x;
