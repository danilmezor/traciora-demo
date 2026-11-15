-- assistant/metrics.sql: the queries behind the computed slots of the assistant's loaded texts (DESIGN.md section 2.5),
-- one a metric of metrics.json, each with the definition in its header. seeder/assistant.py runs the query of a slot's
-- metric at the slot's item's instant and formats its `value` with the slot's format.
-- A header is `-- <metric> | store: erp|core | <definition> | same as: <the statement or golden of the same definition>`.
-- The variables, each text, '' when the slot does not set it:
--   at        the item's instant (timestamptz). A shop row's time is its shop's wall clock, so a query compares it with
--             (:'at'::timestamptz AT TIME ZONE l.time_zone), the instant on that shop's clock
--   lo, hi    the slot's period as wall-clock times on each shop's own clock (hi exclusive); a period that reaches the
--             instant ends at it
--   sites     shop ids (erp) or core location ids (core), comma-separated; '' is every shop
--   advisor, closed_by, person, account, order   one employee (a core person in a core query), account or order
--             id; not_advisor, not_closed_by, not_person   everyone but that employee
--   pay, min, min_over, approved, after_payment, terms, plan, cfg, position, card   as metrics.json's
--             dimensions; plan is the ledger's s10.west_plan figure; position a core position name; card a work item id
--   zone      the home clock (geo.home_zone), the tenant's business day
-- A call's time is its site's wall clock (core.location.tz), the home clock for a call at no site. A scored call is the
-- current scorecard verdict with a score, produced by the instant, of a call whose person is the population's
-- (scorecard_reads.verdicts).
-- A status at the instant is the order's last order_status_history row at or before it. Money before tax is
-- total - tax_total (en: tax added on top; ru: VAT inside, so this is the before-VAT amount); the discount share is
-- discount_total over labor_total + parts_total + sublet_total + fees_total (dictionary, repair_order).
-- Not here: catalogue.list_price and catalogue.price_at_old_hour (v1/catalogue.json, priced in seeder/assistant.py:
-- labour of the job for class car at the hour in force on the instant's day, before or after the rise P, plus the
-- standard tier of each part line at today's list price) and tasks.next_run (the task's schedule, the product's
-- tasks.next_due after the instant).

-- orders.discounted | store: erp | paid orders (a payment row of kind payment received by the instant; pay=cash: of method cash) of customer-pay or any type, opened in the period, whose discount is at least min % (min) or above min_over % (min_over) of the bill before the discount; approved=no keeps those with no discount_approved_by_id, yes those with one | same as: erp s2.f1.discounted and s2.west.discounts_after (paid in cash, the share on labour, parts, sublet and fees), with the slot's own threshold and window
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int) AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND (:'pay' = '' OR p.method = :'pay')
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND o.discount_total > 0
  AND (nullif(:'min', '') IS NULL OR o.discount_total >= nullif(:'min', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total))
  AND (nullif(:'min_over', '') IS NULL OR o.discount_total > nullif(:'min_over', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total))
  AND (:'approved' = '' OR (o.discount_approved_by_id IS NOT NULL) = (:'approved' = 'yes'));

-- orders.cash | store: erp | paid orders of the population with a payment of method cash received by the instant, opened in the period | same as: erp s2.f1.cash_orders, with the slot's window
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int) AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone);

-- orders.discounted_share | store: erp | orders.discounted / orders.cash of the same population, in per cent | same as: erp s2.f1.discount_share, with the slot's own threshold and window
WITH cash AS (
    SELECT o.* FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
    WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int) AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
      AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
      AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'
                  AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone))
SELECT 100.0 * count(*) FILTER (WHERE discount_total > 0 AND discount_total >= nullif(:'min', '')::numeric / 100 * (labor_total + parts_total + sublet_total + fees_total))
       / nullif(count(*), 0) AS value
FROM cash;

-- orders.discount_money | store: erp | the discount_total of orders.discounted | same as: erp s2.f1.discount_total, with the slot's own threshold and window
SELECT coalesce(sum(o.discount_total), 0) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int) AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND (:'pay' = '' OR p.method = :'pay')
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND o.discount_total > 0 AND o.discount_total >= nullif(:'min', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total);

-- orders.on_walkin | store: erp | of orders.discounted, those whose customer is the shop's walk-in record | same as: erp s2.walkin (the walk-in record by its name)
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND (:'pay' = '' OR p.method = :'pay')
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND o.discount_total > 0 AND o.discount_total >= nullif(:'min', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total)
  AND c.name = CASE :'cfg' WHEN 'en' THEN 'WALK-IN CUSTOMER' ELSE 'Розничный покупатель' END;

-- orders.discount_pct | store: erp | one order's discount_total as a share of its bill before the discount, in per cent | same as: erp s2.west.discounts_after (unapproved_pcts)
SELECT 100.0 * o.discount_total / nullif(o.labor_total + o.parts_total + o.sublet_total + o.fees_total, 0) AS value
FROM shop.repair_order o WHERE o.repair_order_id = nullif(:'order', '')::int;

-- orders.voided | store: erp | orders voided in the period by the instant (voided_at); after_payment=yes keeps those that hold a payment of method cash | same as: erp s2.f1.second (en), with the slot's window
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
  AND o.voided_at >= :'lo'::timestamp AND o.voided_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (:'after_payment' = '' OR EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'));

-- orders.voided_money | store: erp | the totals the orders of orders.voided still carry | same as: erp s2.f1.second (en), with the slot's window
SELECT coalesce(sum(o.total), 0) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
  AND o.voided_at >= :'lo'::timestamp AND o.voided_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (:'after_payment' = '' OR EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'));

-- orders.voided_max_per_advisor | store: erp | the largest orders.voided of any single advisor of the population | same as: erp s2.f1.second (en), per advisor
SELECT coalesce(max(n), 0) AS value FROM (
    SELECT count(*) AS n
    FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
    WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
      AND o.voided_at >= :'lo'::timestamp AND o.voided_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
      AND (:'after_payment' = '' OR EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'))
    GROUP BY o.advisor_id) x;

-- till.closes | store: erp | cash_drawer_close rows of the population whose business_date lies in the period and before the instant's day (en) | same as: erp s2.f1.third (en, of_days_he_closed), with the slot's window
SELECT count(*) AS value
FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id
WHERE (:'sites' = '' OR d.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'closed_by', '') IS NULL OR d.closed_by_id = nullif(:'closed_by', '')::int)
  AND d.business_date >= :'lo'::date AND d.business_date < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)::date;

-- till.short_days | store: erp | of till.closes, those whose difference is -min or lower (en) | same as: erp s2.f1.third (en, count) and golden shop-S02-west-leaks, with the slot's window
SELECT count(*) AS value
FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id
WHERE (:'sites' = '' OR d.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'closed_by', '') IS NULL OR d.closed_by_id = nullif(:'closed_by', '')::int)
  AND d.business_date >= :'lo'::date AND d.business_date < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)::date
  AND d.difference <= -nullif(:'min', '')::numeric;

-- till.short_money | store: erp | the sum of the differences of till.short_days, as a positive amount (en) | same as: erp s2.f1.third (en, total), with the slot's window
SELECT coalesce(-sum(d.difference), 0) AS value
FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id
WHERE (:'sites' = '' OR d.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'closed_by', '') IS NULL OR d.closed_by_id = nullif(:'closed_by', '')::int)
  AND d.business_date >= :'lo'::date AND d.business_date < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)::date
  AND d.difference <= -nullif(:'min', '')::numeric;

-- till.short_days_max_per_closer | store: erp | the largest till.short_days of any single closer of the population (en) | same as: erp s2.f1.third (en), per closer
SELECT coalesce(max(n), 0) AS value FROM (
    SELECT count(*) AS n
    FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id
    WHERE (:'sites' = '' OR d.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'not_closed_by', '') IS NULL OR d.closed_by_id <> nullif(:'not_closed_by', '')::int)
      AND d.business_date >= :'lo'::date AND d.business_date < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)::date
      AND d.difference <= -nullif(:'min', '')::numeric
    GROUP BY d.closed_by_id) x;

-- stock.issues_no_sale | store: erp | stock_movement issues recorded under the person with no order line, moved in the period (ru) | same as: erp s2.f1.second (ru, count), with the slot's window
SELECT count(*) AS value
FROM shop.stock_movement m JOIN shop.location l ON l.location_id = m.location_id
WHERE (:'sites' = '' OR m.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'person', '') IS NULL OR m.employee_id = nullif(:'person', '')::int)
  AND m.kind = 'issue' AND m.order_part_id IS NULL
  AND m.moved_at >= :'lo'::timestamp AND m.moved_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone);

-- stock.issues_no_sale_cost | store: erp | their cost, -quantity x unit_cost (ru) | same as: erp s2.f1.second (ru, total), with the slot's window
SELECT coalesce(sum(-m.quantity * m.unit_cost), 0) AS value
FROM shop.stock_movement m JOIN shop.location l ON l.location_id = m.location_id
WHERE (:'sites' = '' OR m.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'person', '') IS NULL OR m.employee_id = nullif(:'person', '')::int)
  AND m.kind = 'issue' AND m.order_part_id IS NULL
  AND m.moved_at >= :'lo'::timestamp AND m.moved_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone);

-- stock.issues_no_sale_max_per_person | store: erp | the largest stock.issues_no_sale of any single person of the population (ru) | same as: erp s2.f1.second (ru), per person
SELECT coalesce(max(n), 0) AS value FROM (
    SELECT count(*) AS n
    FROM shop.stock_movement m JOIN shop.location l ON l.location_id = m.location_id
    WHERE (:'sites' = '' OR m.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'not_person', '') IS NULL OR m.employee_id IS DISTINCT FROM nullif(:'not_person', '')::int) AND m.employee_id IS NOT NULL
      AND m.kind = 'issue' AND m.order_part_id IS NULL
      AND m.moved_at >= :'lo'::timestamp AND m.moved_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
    GROUP BY m.employee_id) x;

-- labor.overclock_orders | store: erp | orders of the population opened in the period on which the technicians clocked more than one hour above the hours sold on the approved jobs (ru) | same as: erp s2.f1.third (ru, count), with the slot's window
SELECT count(*) AS value FROM (
    SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
         - (SELECT coalesce(sum(lb.hours), 0) FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h
    FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
    WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
      AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)) x
WHERE over_h > 1;

-- labor.overclock_hours | store: erp | clocked minus sold hours on the orders of labor.overclock_orders (ru) | same as: erp s2.f1.third (ru, hours), with the slot's window
SELECT coalesce(sum(over_h), 0) AS value FROM (
    SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
         - (SELECT coalesce(sum(lb.hours), 0) FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h
    FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
    WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
      AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)) x
WHERE over_h > 1;

-- labor.overclock_orders_max_per_advisor | store: erp | the largest labor.overclock_orders of any single advisor of the population (ru) | same as: erp s2.f1.third (ru), per advisor
SELECT coalesce(max(n), 0) AS value FROM (
    SELECT advisor_id, count(*) AS n FROM (
        SELECT o.advisor_id,
               (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
             - (SELECT coalesce(sum(lb.hours), 0) FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h
        FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
        WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
          AND (nullif(:'not_advisor', '') IS NULL OR o.advisor_id <> nullif(:'not_advisor', '')::int)
          AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)) x
    WHERE over_h > 1 GROUP BY advisor_id) y;

-- labor.overclock_money | store: erp | the hours of labor.overclock_hours at the standard labour hour of the order's shop in force on its day (ru) | same as: erp s2.total (ru, third part), with the slot's window
SELECT coalesce(sum(over_h * rate), 0) AS value FROM (
    SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
         - (SELECT coalesce(sum(lb.hours), 0) FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h,
           (SELECT r.rate FROM shop.labor_rate r WHERE r.location_id = o.location_id AND r.price_class = 'standard'
             AND r.valid_from <= o.opened_at::date AND (r.valid_to IS NULL OR r.valid_to >= o.opened_at::date)) AS rate
    FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
    WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
      AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
      AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)) x
WHERE over_h > 1;

-- leak.total | store: erp | story S2's estimate under one advisor in the period. en: orders.discount_money (pay=cash, min=10) + orders.voided_money (after_payment=yes) + till.short_money (closed_by the advisor, min=20); ru: orders.discount_money (pay=cash, min=10) + stock.issues_no_sale_cost (person the advisor) + labor.overclock_money | same as: erp s2.total, with the slot's window and the 10 % threshold of the slot's table (the statement counts discounts of 15 % and more without an approver)
SELECT
  (SELECT coalesce(sum(o.discount_total), 0) FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
   WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.advisor_id = nullif(:'advisor', '')::int
     AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
     AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash' AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)
     AND o.discount_total > 0 AND o.discount_total >= 0.10 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total))
+ CASE :'cfg' WHEN 'en' THEN
  (SELECT coalesce(sum(o.total), 0) FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
   WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.advisor_id = nullif(:'advisor', '')::int
     AND o.voided_at >= :'lo'::timestamp AND o.voided_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
     AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND p.method = 'cash'))
+ (SELECT coalesce(-sum(d.difference), 0) FROM shop.cash_drawer_close d JOIN shop.location l ON l.location_id = d.location_id
   WHERE (:'sites' = '' OR d.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND d.closed_by_id = nullif(:'advisor', '')::int
     AND d.business_date >= :'lo'::date AND d.business_date < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)::date AND d.difference <= -20)
  ELSE
  (SELECT coalesce(sum(-m.quantity * m.unit_cost), 0) FROM shop.stock_movement m JOIN shop.location l ON l.location_id = m.location_id
   WHERE (:'sites' = '' OR m.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND m.employee_id = nullif(:'advisor', '')::int AND m.kind = 'issue' AND m.order_part_id IS NULL
     AND m.moved_at >= :'lo'::timestamp AND m.moved_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone))
+ (SELECT coalesce(sum(over_h * rate), 0) FROM (
     SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0) FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id)
          - (SELECT coalesce(sum(lb.hours), 0) FROM shop.order_job j JOIN shop.order_labor lb ON lb.order_job_id = j.order_job_id WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h,
            (SELECT r.rate FROM shop.labor_rate r WHERE r.location_id = o.location_id AND r.price_class = 'standard'
              AND r.valid_from <= o.opened_at::date AND (r.valid_to IS NULL OR r.valid_to >= o.opened_at::date)) AS rate
     FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
     WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.advisor_id = nullif(:'advisor', '')::int
       AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)) x WHERE over_h > 1)
  END AS value;

-- orders.closed | store: erp | customer-pay orders first invoiced in the period, by the instant, whose status at the instant is invoiced or paid (warranty, goodwill and internal orders and voids left out) | same as: golden shop-revenue-last-week (its population), with the slot's window
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
JOIN LATERAL (SELECT min(h.changed_at) AS invoiced_at FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') i ON true
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.order_type = 'customer_pay'
  AND i.invoiced_at >= :'lo'::timestamp AND i.invoiced_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) IN ('invoiced', 'paid');

-- orders.revenue | store: erp | the bill of orders.closed, en before tax (total - tax_total), ru as billed with VAT inside (total), as metrics.json says; with order set, that order's bill | same as: golden shop-revenue-last-week (en; its population in ru), with the slot's window
SELECT coalesce(sum(CASE :'cfg' WHEN 'en' THEN o.total - o.tax_total ELSE o.total END), 0) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
JOIN LATERAL (SELECT min(h.changed_at) AS invoiced_at FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') i ON true
WHERE o.repair_order_id = nullif(:'order', '')::int
   OR (:'order' = '' AND (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.order_type = 'customer_pay'
       AND i.invoiced_at >= :'lo'::timestamp AND i.invoiced_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
       AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
            ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) IN ('invoiced', 'paid'));

-- plan.orders_share | store: erp | orders.closed of the period / the plan (ledger s10.west_plan.orders), in per cent | same as: golden shop-revenue-last-week (its population), with the slot's window
SELECT 100.0 * count(*) / nullif(:'plan', '')::numeric AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
JOIN LATERAL (SELECT min(h.changed_at) AS invoiced_at FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') i ON true
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.order_type = 'customer_pay'
  AND i.invoiced_at >= :'lo'::timestamp AND i.invoiced_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) IN ('invoiced', 'paid');

-- plan.revenue_share | store: erp | orders.revenue of the period (en before tax, ru with VAT inside) / the plan (ledger s10.west_plan.revenue), in per cent | same as: golden shop-revenue-last-week (en), with the slot's window
SELECT 100.0 * coalesce(sum(CASE :'cfg' WHEN 'en' THEN o.total - o.tax_total ELSE o.total END), 0) / nullif(:'plan', '')::numeric AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
JOIN LATERAL (SELECT min(h.changed_at) AS invoiced_at FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') i ON true
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.order_type = 'customer_pay'
  AND i.invoiced_at >= :'lo'::timestamp AND i.invoiced_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) IN ('invoiced', 'paid');

-- orders.average | store: erp | orders.revenue / orders.closed of the same population and period (en before tax, ru with VAT inside) | same as: erp volume.average_order (mean of total - tax_total over customer-pay orders invoiced or paid), with the slot's window
SELECT coalesce(sum(CASE :'cfg' WHEN 'en' THEN o.total - o.tax_total ELSE o.total END), 0) / nullif(count(*), 0) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
JOIN LATERAL (SELECT min(h.changed_at) AS invoiced_at FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') i ON true
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[])) AND o.order_type = 'customer_pay'
  AND i.invoiced_at >= :'lo'::timestamp AND i.invoiced_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) IN ('invoiced', 'paid');

-- rec.sold_share | store: erp | of the jobs recommended from an inspection item on orders opened in the period, those approved over those approved or declined (as decided by the instant), in per cent, counted in jobs | same as: erp sold.west and sold.east (dictionary, inspection_item), with the slot's window
SELECT 100.0 * count(*) FILTER (WHERE j.status = 'approved') / nullif(count(*) FILTER (WHERE j.status IN ('approved', 'declined')), 0) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND j.decided_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
  AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id);

-- orders.waiting_parts | store: erp | orders whose status at the instant is waiting_parts | same as: erp s6.waiting_at_t and golden shop-S06-west-waiting-parts (at T)
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) = 'waiting_parts';

-- orders.waiting_days_max | store: erp | of orders.waiting_parts, the most calendar days on the shop's clock from the order's last entry into waiting_parts to the instant | same as: erp s6.waiting_at_t and golden shop-S06-west-waiting-parts (at T)
SELECT max((:'at'::timestamptz AT TIME ZONE l.time_zone)::date
           - (SELECT max(h.changed_at)::date FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts'
              AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) = 'waiting_parts';

-- acct.visits | store: erp | customer-pay orders of the accounts billed on terms (terms=yes) or of one account, opened in the period, whose status at the instant is not declined or void | same as: erp acct.A1.visits to acct.A6.visits and golden shop-S01-accounts-lost (warranty comebacks and voids are not visits), with the slot's window
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE c.payment_terms_days IS NOT NULL AND (nullif(:'account', '') IS NULL OR c.customer_id = nullif(:'account', '')::int) AND o.order_type = 'customer_pay'
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) NOT IN ('declined', 'void');

-- acct.usual_visits | store: erp | the account's acct.visits over the 90 days before the period, scaled to the period's length (visits x period days / 90) | same as: erp acct.A1.visits (its population), over the window before the period
SELECT count(*) * extract(epoch FROM :'hi'::timestamp - :'lo'::timestamp) / 86400 / 90 AS value
FROM shop.repair_order o JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE c.payment_terms_days IS NOT NULL AND c.customer_id = nullif(:'account', '')::int AND o.order_type = 'customer_pay'
  AND o.opened_at >= :'lo'::timestamp - interval '90 days' AND o.opened_at < :'lo'::timestamp
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'lo'::timestamp
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) NOT IN ('declined', 'void');

-- acct.estimates_waiting | store: erp | the account's orders whose status at the instant is estimate (written, nothing approved: waiting for an answer) and that were opened more than two days before it | same as: none
SELECT count(*) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE c.payment_terms_days IS NOT NULL AND (nullif(:'account', '') IS NULL OR c.customer_id = nullif(:'account', '')::int)
  AND o.opened_at < (:'at'::timestamptz AT TIME ZONE l.time_zone) - interval '2 days'
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) = 'estimate';

-- acct.overdue_money | store: erp | the totals of the statements (en) or invoices (ru) of the accounts on terms, or of one, issued by the instant, past their due day at the instant (due_on before the instant's day on the home clock) and with no payment received by the instant | same as: golden shop-accounts-owed (overdue_usd: not paid, due_on before today)
SELECT coalesce(sum(s.total), 0) AS value
FROM shop.statement s JOIN shop.customer c ON c.customer_id = s.customer_id
WHERE c.payment_terms_days IS NOT NULL AND (nullif(:'account', '') IS NULL OR c.customer_id = nullif(:'account', '')::int)
  AND s.issued_on <= (:'at'::timestamptz AT TIME ZONE :'zone')::date AND s.due_on < (:'at'::timestamptz AT TIME ZONE :'zone')::date
  AND NOT EXISTS (SELECT 1 FROM shop.payment p WHERE p.statement_id = s.statement_id AND p.kind = 'payment' AND p.received_at <= :'at'::timestamptz AT TIME ZONE :'zone');

-- acct.days_since_visit | store: erp | calendar days on the shop's clock from the account's last visit (acct.visits' population) opened by the instant to the instant | same as: golden shop-S01-accounts-lost (last_order_on)
SELECT min((:'at'::timestamptz AT TIME ZONE l.time_zone)::date - o.opened_at::date) AS value
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
WHERE c.customer_id = nullif(:'account', '')::int AND o.order_type = 'customer_pay' AND o.opened_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
  AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
       ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) NOT IN ('declined', 'void');

-- acct.flagged | store: erp | accounts on terms (or one account) with no visit in the 30 days before the instant, an estimate waiting more than two days (acct.estimates_waiting) or a bill past its terms (acct.overdue_money) | same as: the three metrics above, at the instant
SELECT count(*) AS value
FROM shop.customer c
WHERE c.payment_terms_days IS NOT NULL AND (nullif(:'account', '') IS NULL OR c.customer_id = nullif(:'account', '')::int) AND (
      NOT EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
                  WHERE o.customer_id = c.customer_id AND o.order_type = 'customer_pay'
                    AND o.opened_at > (:'at'::timestamptz AT TIME ZONE l.time_zone) - interval '30 days' AND o.opened_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
                    AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
                         ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) NOT IN ('declined', 'void'))
   OR EXISTS (SELECT 1 FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
              WHERE o.customer_id = c.customer_id AND o.opened_at < (:'at'::timestamptz AT TIME ZONE l.time_zone) - interval '2 days'
                AND (SELECT h.status FROM shop.order_status_history h WHERE h.repair_order_id = o.repair_order_id AND h.changed_at <= :'at'::timestamptz AT TIME ZONE l.time_zone
                     ORDER BY h.changed_at DESC, h.order_status_history_id DESC LIMIT 1) = 'estimate')
   OR EXISTS (SELECT 1 FROM shop.statement s WHERE s.customer_id = c.customer_id
              AND s.issued_on <= (:'at'::timestamptz AT TIME ZONE :'zone')::date AND s.due_on < (:'at'::timestamptz AT TIME ZONE :'zone')::date
              AND NOT EXISTS (SELECT 1 FROM shop.payment p WHERE p.statement_id = s.statement_id AND p.kind = 'payment' AND p.received_at <= :'at'::timestamptz AT TIME ZONE :'zone')));

-- bookings.count | store: erp | appointments at the shop that start on the period's day, booked by the instant and not cancelled | same as: none
SELECT count(*) AS value
FROM shop.appointment a JOIN shop.location l ON l.location_id = a.location_id
WHERE (:'sites' = '' OR a.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND a.starts_at >= :'lo'::timestamp AND a.starts_at < :'hi'::timestamp
  AND a.booked_at <= :'at'::timestamptz AT TIME ZONE l.time_zone AND a.status <> 'cancelled';

-- bookings.first | store: erp | the first of bookings.count: its time, the customer (the record's name, else the name given) and what was asked for, in one line | same as: none
SELECT to_char(a.starts_at, 'HH24:MI') || '|' || coalesce(c.name, a.contact_name, '') || '|' || coalesce(a.reason, '') AS value
FROM shop.appointment a JOIN shop.location l ON l.location_id = a.location_id LEFT JOIN shop.customer c ON c.customer_id = a.customer_id
WHERE (:'sites' = '' OR a.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND a.starts_at >= :'lo'::timestamp AND a.starts_at < :'hi'::timestamp
  AND a.booked_at <= :'at'::timestamptz AT TIME ZONE l.time_zone AND a.status <> 'cancelled'
ORDER BY a.starts_at, a.appointment_id LIMIT 1;

-- rows.advisor | store: erp | the advisors with an order of the block's population in the period, by name (first and last) | same as: none
SELECT DISTINCT o.advisor_id AS key, e.first_name || ' ' || e.last_name AS name
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.employee e ON e.employee_id = o.advisor_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND (:'pay' = '' OR p.method = :'pay')
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone);

-- rows.order | store: erp | the orders of orders.discounted for the block's population: shop, advisor, day opened, customer and who approved the discount | same as: orders.discounted
SELECT o.repair_order_id AS key, l.name AS site, e.first_name || ' ' || e.last_name AS advisor, o.opened_at::date AS date, c.name AS customer,
       a.first_name || ' ' || a.last_name AS approver
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id JOIN shop.customer c ON c.customer_id = o.customer_id
JOIN shop.employee e ON e.employee_id = o.advisor_id LEFT JOIN shop.employee a ON a.employee_id = o.discount_approved_by_id
WHERE (:'sites' = '' OR o.location_id = ANY(string_to_array(:'sites', ',')::int[]))
  AND (nullif(:'advisor', '') IS NULL OR o.advisor_id = nullif(:'advisor', '')::int)
  AND o.opened_at >= :'lo'::timestamp AND o.opened_at < least(:'hi'::timestamp, :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id AND p.kind = 'payment' AND (:'pay' = '' OR p.method = :'pay')
              AND p.received_at <= :'at'::timestamptz AT TIME ZONE l.time_zone)
  AND o.discount_total > 0
  AND (nullif(:'min', '') IS NULL OR o.discount_total >= nullif(:'min', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total))
  AND (nullif(:'min_over', '') IS NULL OR o.discount_total > nullif(:'min_over', '')::numeric / 100 * (o.labor_total + o.parts_total + o.sublet_total + o.fees_total));

-- rows.account | store: erp | the accounts billed on terms, by name | same as: golden shop-accounts-owed (its population)
SELECT c.customer_id AS key, c.name AS name FROM shop.customer c WHERE c.payment_terms_days IS NOT NULL;

-- roster.gaps | store: core | the seats short at the bands of cover required on the period's day at the sites (a requirement active, in force that day and naming its weekday): per band, min_count less the published shifts, published by the instant, with a person of the band's position at the site that overlap the band on its day's wall clock, when that is more than none; with position and band set, that band's | same as: the product's roster coverage (queries/roster.py _coverage_day), counting published shifts only
SELECT coalesce(sum(greatest(cr.min_count - (
           SELECT count(*) FROM workforce.shift s JOIN workforce.roster_publish rp ON rp.id = s.roster_publish_id
           WHERE s.location_id = cr.location_id AND s.position_id = cr.position_id AND s.person_id IS NOT NULL AND s.deleted_at IS NULL
             AND s.status = 'published' AND rp.published_at <= :'at'::timestamptz AND s.business_day = :'lo'::date
             AND s.start_local < :'lo'::date + CASE WHEN cr.end_time_local <= cr.start_time_local THEN 1 ELSE 0 END + cr.end_time_local
             AND s.end_local > :'lo'::date + cr.start_time_local), 0)), 0) AS value
FROM workforce.coverage_requirement cr JOIN core.position pos ON pos.id = cr.position_id
WHERE (:'sites' = '' OR cr.location_id = ANY(string_to_array(:'sites', ',')::uuid[])) AND cr.active AND cr.required
  AND get_bit(cr.day_mask, extract(isodow FROM :'lo'::date)::int - 1) = 1
  AND (cr.valid_from IS NULL OR cr.valid_from <= :'lo'::date) AND (cr.valid_to IS NULL OR cr.valid_to >= :'lo'::date)
  AND (:'position' = '' OR pos.name = :'position') AND (:'band' = '' OR cr.id = nullif(:'band', '')::uuid);

-- roster.on_shift | store: core | the people with a shift on the period's day at the site, published by the instant (not cancelled or deleted) | same as: roster.gaps (its shifts)
SELECT count(DISTINCT s.person_id) AS value
FROM workforce.shift s JOIN workforce.roster_publish rp ON rp.id = s.roster_publish_id
WHERE (:'sites' = '' OR s.location_id = ANY(string_to_array(:'sites', ',')::uuid[])) AND s.person_id IS NOT NULL AND s.deleted_at IS NULL
  AND s.status = 'published' AND rp.published_at <= :'at'::timestamptz AND s.business_day = :'lo'::date;

-- roster.requests_open | store: core | shift change requests on a shift at the sites filed by the instant and open at it (status open, or decided after it) | same as: the product's shift requests (queries/roster.py _REQUESTS, status open)
SELECT count(*) AS value
FROM workforce.shift_change_request r JOIN workforce.shift s ON s.id = r.shift_id
WHERE (:'sites' = '' OR s.location_id = ANY(string_to_array(:'sites', ',')::uuid[])) AND r.filed_at <= :'at'::timestamptz
  AND (r.status = 'open' OR r.decided_at > :'at'::timestamptz);

-- rows.gap | store: core | the bands of roster.gaps that are short, each with its site, position and hours | same as: roster.gaps
SELECT * FROM (
    SELECT cr.id AS key, l.name AS site, l.id AS site_id, pos.name AS position, cr.start_time_local AS starts, cr.end_time_local AS ends,
           cr.min_count - (
               SELECT count(*) FROM workforce.shift s JOIN workforce.roster_publish rp ON rp.id = s.roster_publish_id
               WHERE s.location_id = cr.location_id AND s.position_id = cr.position_id AND s.person_id IS NOT NULL AND s.deleted_at IS NULL
                 AND s.status = 'published' AND rp.published_at <= :'at'::timestamptz AND s.business_day = :'lo'::date
                 AND s.start_local < :'lo'::date + CASE WHEN cr.end_time_local <= cr.start_time_local THEN 1 ELSE 0 END + cr.end_time_local
                 AND s.end_local > :'lo'::date + cr.start_time_local) AS short
    FROM workforce.coverage_requirement cr JOIN core.position pos ON pos.id = cr.position_id JOIN core.location l ON l.id = cr.location_id
    WHERE (:'sites' = '' OR cr.location_id = ANY(string_to_array(:'sites', ',')::uuid[])) AND cr.active AND cr.required
      AND get_bit(cr.day_mask, extract(isodow FROM :'lo'::date)::int - 1) = 1
      AND (cr.valid_from IS NULL OR cr.valid_from <= :'lo'::date) AND (cr.valid_to IS NULL OR cr.valid_to >= :'lo'::date)) x
WHERE short > 0;

-- roster.free_people | store: core | the people posted at the band's site in its position on the period's day (person_location in force, person active) with no shift that day at any site (draft or published, not cancelled) and no unavailability on that day that overlaps the band; their ids, named by seeder/assistant.py from cast.json | same as: the product's roster candidates (queries/roster.py _CANDIDATES), keeping the free
SELECT string_agg(p.id::text, ',' ORDER BY p.id) AS value
FROM workforce.coverage_requirement cr
JOIN identity.person_location pl ON pl.location_id = cr.location_id AND pl.position_id = cr.position_id
JOIN identity.person p ON p.id = pl.person_id AND p.active
WHERE cr.id = nullif(:'band', '')::uuid
  AND (pl.valid_from IS NULL OR pl.valid_from <= :'lo'::date) AND (pl.valid_to IS NULL OR pl.valid_to >= :'lo'::date)
  AND NOT EXISTS (SELECT 1 FROM workforce.shift s WHERE s.person_id = p.id AND s.business_day = :'lo'::date AND s.status <> 'cancelled' AND s.deleted_at IS NULL)
  AND NOT EXISTS (SELECT 1 FROM workforce.availability av WHERE av.person_id = p.id AND av.kind = 'unavailable'
                  AND (av.on_date = :'lo'::date OR (av.day_mask IS NOT NULL AND get_bit(av.day_mask, extract(isodow FROM :'lo'::date)::int - 1) = 1
                       AND (av.valid_from IS NULL OR av.valid_from <= :'lo'::date) AND (av.valid_to IS NULL OR av.valid_to >= :'lo'::date)))
                  AND (av.start_time_local IS NULL OR (av.start_time_local < cr.end_time_local AND av.end_time_local > cr.start_time_local)));

-- roster.uncovered_days | store: core | the days of the period on which the shop is open (its weekday has hours in core.location.business_hours and no closed row in core.location_hours_exception) and a band of cover required at the site for the position is in force and no shift with a person of that position at that site, draft or published, not cancelled or deleted, overlaps it (a shift's created_at is the build's, not history's) | same as: none
SELECT count(DISTINCT d) AS value
FROM generate_series(:'lo'::timestamp, :'hi'::timestamp - interval '1 day', interval '1 day') g(d)
JOIN workforce.coverage_requirement cr ON cr.active AND cr.required AND get_bit(cr.day_mask, extract(isodow FROM g.d)::int - 1) = 1
     AND (cr.valid_from IS NULL OR cr.valid_from <= g.d::date) AND (cr.valid_to IS NULL OR cr.valid_to >= g.d::date)
JOIN core.position pos ON pos.id = cr.position_id
JOIN core.location l ON l.id = cr.location_id
WHERE (:'sites' = '' OR cr.location_id = ANY(string_to_array(:'sites', ',')::uuid[])) AND pos.name = :'position'
  AND jsonb_array_length(coalesce(l.business_hours -> lower(to_char(g.d, 'Dy')), '[]'::jsonb)) > 0
  AND NOT EXISTS (SELECT 1 FROM core.location_hours_exception e WHERE e.location_id = l.id AND e.on_date = g.d::date AND e.kind = 'closed')
  AND NOT EXISTS (SELECT 1 FROM workforce.shift s
                  WHERE s.location_id = cr.location_id AND s.position_id = cr.position_id AND s.person_id IS NOT NULL AND s.deleted_at IS NULL
                    AND s.status <> 'cancelled' AND s.business_day = g.d::date
                    AND s.start_local < g.d::date + CASE WHEN cr.end_time_local <= cr.start_time_local THEN 1 ELSE 0 END + cr.end_time_local
                    AND s.end_local > g.d::date + cr.start_time_local);

-- board.days_overdue | store: core | calendar days on the card's own clock (due_tz) from its deadline's day to the instant's day, while the card is open (its state outside the completed and cancelled groups) and past its deadline at the instant | same as: none
SELECT CASE WHEN w.due_at < :'at'::timestamptz THEN (:'at'::timestamptz AT TIME ZONE w.due_tz)::date - w.due_local::date END AS value
FROM work.work_item w JOIN work.work_state st ON st.id = w.state_id
WHERE w.id = nullif(:'card', '')::uuid AND w.deleted_at IS NULL AND st.state_group NOT IN ('completed', 'cancelled');

-- calls.scored | store: core | the person's scored calls that rang in the period | same as: the product's verdicts (scorecard_reads.verdicts), with a score
SELECT count(*) AS value
FROM interactions.interaction_analysis a JOIN interactions.interaction i ON i.id = a.interaction_id LEFT JOIN core.location l ON l.id = i.location_id
WHERE a.kind = 'scorecard' AND a.is_current AND a.score IS NOT NULL AND a.produced_at <= :'at'::timestamptz AND i.person_id = nullif(:'person', '')::uuid
  AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') >= :'lo'::timestamp AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') < :'hi'::timestamp;

-- calls.score_mean | store: core | the mean score of calls.scored | same as: the product's verdicts (their score)
SELECT avg(a.score) AS value
FROM interactions.interaction_analysis a JOIN interactions.interaction i ON i.id = a.interaction_id LEFT JOIN core.location l ON l.id = i.location_id
WHERE a.kind = 'scorecard' AND a.is_current AND a.score IS NOT NULL AND a.produced_at <= :'at'::timestamptz AND i.person_id = nullif(:'person', '')::uuid
  AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') >= :'lo'::timestamp AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') < :'hi'::timestamp;

-- calls.visit_share | store: core | of calls.scored, those whose outcome is visit_agreed, in per cent | same as: the product's outcomes (scorecard_reads.outcomes, visit_agreed)
SELECT 100.0 * count(*) FILTER (WHERE a.result_public ->> 'outcome' = 'visit_agreed') / nullif(count(*), 0) AS value
FROM interactions.interaction_analysis a JOIN interactions.interaction i ON i.id = a.interaction_id LEFT JOIN core.location l ON l.id = i.location_id
WHERE a.kind = 'scorecard' AND a.is_current AND a.score IS NOT NULL AND a.produced_at <= :'at'::timestamptz AND i.person_id = nullif(:'person', '')::uuid
  AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') >= :'lo'::timestamp AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') < :'hi'::timestamp;

-- calls.worst_check | store: core | of the checks scored on calls.scored, the one with the lowest mean level (a tie by key), as its key; named by seeder/assistant.py from the tenant's scorecard | same as: the product's verdicts (result_public checks)
SELECT c ->> 'key' AS value
FROM interactions.interaction_analysis a JOIN interactions.interaction i ON i.id = a.interaction_id LEFT JOIN core.location l ON l.id = i.location_id CROSS JOIN LATERAL jsonb_array_elements(a.result_public -> 'checks') c
WHERE a.kind = 'scorecard' AND a.is_current AND a.score IS NOT NULL AND a.produced_at <= :'at'::timestamptz AND i.person_id = nullif(:'person', '')::uuid
  AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') >= :'lo'::timestamp AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') < :'hi'::timestamp
GROUP BY c ->> 'key' ORDER BY avg((c ->> 'level')::numeric), c ->> 'key' LIMIT 1;

-- calls.best_check | store: core | of the checks scored on calls.scored, the one with the highest mean level (a tie by key), as its key; named by seeder/assistant.py from the tenant's scorecard | same as: the product's verdicts (result_public checks)
SELECT c ->> 'key' AS value
FROM interactions.interaction_analysis a JOIN interactions.interaction i ON i.id = a.interaction_id LEFT JOIN core.location l ON l.id = i.location_id CROSS JOIN LATERAL jsonb_array_elements(a.result_public -> 'checks') c
WHERE a.kind = 'scorecard' AND a.is_current AND a.score IS NOT NULL AND a.produced_at <= :'at'::timestamptz AND i.person_id = nullif(:'person', '')::uuid
  AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') >= :'lo'::timestamp AND i.started_at AT TIME ZONE coalesce(l.tz, :'zone') < :'hi'::timestamp
GROUP BY c ->> 'key' ORDER BY avg((c ->> 'level')::numeric) DESC, c ->> 'key' LIMIT 1;
