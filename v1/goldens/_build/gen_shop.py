"""Writes v1/goldens/shop.en.yaml and shop.ru.yaml from one set of templates.

The rule of every golden: each choice its reference makes (which orders, which date, which window, how many rows, which
columns) is said in the question or in the shop's context (v1/erp/context/RULES.md and the table notes), the context an
agent reads; every column is something the question asks for, and the number of rows follows from the question. When a
reference and a rule disagree, the ledger decides which one changes.
"""
import json
import os

import yaml

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '')  # v1/goldens/


def seed(name):
    return json.load(open(os.path.join(OUT, '..', name), encoding='utf-8'))


LEDGER = {r['key']: r for r in seed('ledger.json')['rows']}
ACCOUNTS = {cfg: {a['id']: a['name'] for a in seed('accounts.json')[cfg]['accounts']} for cfg in ('en', 'ru')}
VENDORS = {cfg: {v['id']: v['name'] for v in seed('vendors.json')[cfg]} for cfg in ('en', 'ru')}
STAFF = {cfg: {p['slot']: p[cfg]['full_name'].split()[0] + ' ' + p[cfg]['full_name'].split()[-1] for p in seed('cast.json')['people']} for cfg in ('en', 'ru')}
NINE_DAYS = {cfg: seed('named_customers.json')[cfg]['S6_waiting_nine_days']['name'] for cfg in ('en', 'ru')}


def L(key, cfg):
    row = LEDGER[key]
    return row['value'] if 'value' in row else row[cfg]


def per_cfg(f):
    return {cfg: f(cfg) for cfg in ('en', 'ru')}

CFG = {
    'en': {
        '@TZ@': "'America/New_York'", '@CUR@': 'usd',
        '@MAIN@': "'East Main'", '@EAST@': "'Bonny Oaks'", '@WEST@': "'Charlotte Pike'",
        '@WALKIN@': "'WALK-IN CUSTOMER'",
        '@F1FIRST@': "'Brent'", '@F1LAST@': "'Lassiter'",
        '@F4FIRST@': "'Mason'", '@F4LAST@': "'Pruitt'",
        '@WD@': "extract(isodow FROM d.business_date) < 6",
    },
    'ru': {
        '@TZ@': "'Europe/Ulyanovsk'", '@CUR@': 'rub',
        '@MAIN@': "'Московское шоссе'", '@EAST@': "'Инженерный'", '@WEST@': "'Техническая'",
        '@WALKIN@': "'Розничный покупатель'",
        '@F1FIRST@': "'Артур'", '@F1LAST@': "'Назаров'",
        '@F4FIRST@': "'Рустам'", '@F4LAST@': "'Юсупов'",
        '@WD@': 'true',
    },
}

NOW = "(now() AT TIME ZONE @TZ@)"
TODAY = "date_trunc('day', now() AT TIME ZONE @TZ@)"
INV = """inv AS (
  SELECT h.repair_order_id, min(h.changed_at) AS invoiced_at
  FROM shop.order_status_history h
  WHERE h.status = 'invoiced'
  GROUP BY h.repair_order_id
)"""
REV = "o.order_type = 'customer_pay' AND o.status IN ('invoiced', 'paid')"
NET = "(CASE WHEN o.tax_included THEN 1 + o.tax_rate / 100 ELSE 1 END)"
BASE = "(o.labor_total + o.parts_total + o.sublet_total + o.fees_total)"
F1 = """f1 AS (
  SELECT employee_id, left_on FROM shop.employee
  WHERE first_name = @F1FIRST@ AND last_name = @F1LAST@
)"""
CASH = """EXISTS (SELECT 1 FROM shop.payment p WHERE p.repair_order_id = o.repair_order_id
                   AND p.kind = 'payment' AND p.method = 'cash')"""
F1_WINDOW = "o.opened_at >= f1.left_on - 182 AND o.opened_at < f1.left_on + 1"
DISC = f"""disc AS (
  SELECT coalesce(sum(o.discount_total), 0) AS v
  FROM shop.repair_order o JOIN f1 ON f1.employee_id = o.advisor_id
  JOIN LATERAL (SELECT min(h.changed_at) AS at FROM shop.order_status_history h
                WHERE h.repair_order_id = o.repair_order_id AND h.status = 'invoiced') inv ON true
  WHERE {REV} AND inv.at >= f1.left_on - 182 AND inv.at < f1.left_on + 1
)"""


def s(text):
    return text.replace('@NOW@', NOW).replace('@TODAY@', TODAY).replace('@INV@', INV) \
        .replace('@REV@', REV).replace('@NET@', NET).replace('@BASE@', BASE).strip() + '\n'


# Each golden: id, category, asker, question en, question ru ('' or verbatim), sql (str or {en, ru}),
# expected (dict; '@CUR@' replaced in column names), rule (str or {en, ru}), notes. A ledger row's band stays in
# erp/checks.sql: a golden is compared with the product's own tolerance.
# A golden whose answer a story or the ledger fixes names it from the seed files, for Gate 1 to check on the reference
# query's rows at the nominal T: expect_keys {column: {key: rows}} (each row holds one of the keys, each key in as many
# rows as given) and top {column: key or [keys]} (the first row holds it; a list, the first rows in order). A text key is
# held when the cell contains it, a number when it equals it; '@<anchor>' is a date of the clock's anchors at the build's
# T (seeder/clock.py), and as expect_keys of a column a list of dates, each held once.
G = []


def g(**kw):
    G.append(kw)


# ---------------------------------------------------------------- story questions (12)

g(id='shop-S01-accounts-lost', category='accounts', asker='2',
  en='Which company accounts have we lost or are losing?',
  ru='Кто из корпоративных у нас отвалился, а кого теряем сейчас?',
  sql=s("""
WITH acct AS (
  SELECT customer_id, name FROM shop.customer WHERE payment_terms_days IS NOT NULL
), visits AS (
  SELECT o.customer_id, o.opened_at
  FROM shop.repair_order o JOIN acct a ON a.customer_id = o.customer_id
  WHERE o.order_type = 'customer_pay' AND o.status NOT IN ('declined', 'void')
), per_account AS (
  SELECT a.name,
         count(v.opened_at) FILTER (WHERE v.opened_at >= @TODAY@ - interval '29 days') AS last_30,
         count(v.opened_at) FILTER (WHERE v.opened_at >= @TODAY@ - interval '89 days') AS last_90,
         count(v.opened_at) FILTER (WHERE v.opened_at >= @TODAY@ - interval '179 days'
                                      AND v.opened_at < @TODAY@ - interval '149 days') AS block_before
  FROM acct a LEFT JOIN visits v ON v.customer_id = a.customer_id
  GROUP BY a.customer_id, a.name
)
SELECT name AS account_name
FROM per_account
WHERE last_90 = 0 OR last_30 < block_before / 2.0
ORDER BY name
"""),
  expected={'columns': ['account_name'], 'nonempty': True},
  expect_keys=per_cfg(lambda c: {'account_name': {ACCOUNTS[c]['A5']: 1, ACCOUNTS[c]['A6']: 1}}),
  rule='acct.A5.visits, acct.A6.visits',
  notes='Accounts billed on terms only (not every company); their business is customer-pay orders, not declined or void. Lost and being lost as the context defines them (story S1.1), in calendar days to today.')

g(id='shop-S01-east-overdue', category='accounts', asker='16',
  en='Which accounts at Bonny Oaks have a bill overdue?',
  ru='У кого из корпоративных клиентов Инженерного есть просроченные счета?',
  sql=s("""
SELECT DISTINCT c.name AS account_name
FROM shop.statement s
JOIN shop.customer c ON c.customer_id = s.customer_id
JOIN shop.location l ON l.location_id = c.created_location_id
WHERE c.payment_terms_days IS NOT NULL
  AND l.name = @EAST@
  AND s.due_on < @TODAY@::date
  AND NOT EXISTS (SELECT 1 FROM shop.payment p WHERE p.statement_id = s.statement_id AND p.kind = 'payment')
ORDER BY c.name
"""),
  expected={'columns': ['account_name'], 'rows': 0},
  rule='acct.others_pay_on_time',
  notes='The right answer is none: an empty result, not a guess. An account belongs to the shop that created it; overdue = due day past with no payment.')

g(id='shop-S02-brent-cost', category='money', asker='2',
  en='What did Brent Lassiter cost us at Charlotte Pike in his last 26 weeks: the discounts he gave, the cash he took on '
     'orders he then voided, the days his till came up 20 dollars or more short, and the three together?',
  ru='Во что нам обошёлся Артур Назаров на Технической за последние 26 недель его работы, в ценах для клиента (с НДС): скидки, которые он дал; запчасти, выданные со склада на его имя без продажи, по себестоимости; часы, которые механики отметили в его нарядах больше чем на час сверх проданных, по цене нормо-часа на тот момент; и всё вместе?',
  sql={'en': s(f"""
WITH {F1}, {DISC}, voids AS (
  SELECT coalesce(sum(o.total), 0) AS v
  FROM shop.repair_order o JOIN f1 ON f1.employee_id = o.advisor_id
  WHERE o.status = 'void' AND {CASH} AND {F1_WINDOW}
), till AS (
  SELECT coalesce(-sum(d.difference), 0) AS v
  FROM shop.cash_drawer_close d JOIN f1 ON f1.employee_id = d.closed_by_id
  WHERE d.difference <= -20 AND d.business_date >= f1.left_on - 182 AND d.business_date <= f1.left_on
)
SELECT disc.v AS discounts_usd,
       voids.v AS voided_after_cash_usd,
       till.v AS till_short_usd,
       disc.v + voids.v + till.v AS estimated_total_usd
FROM disc, voids, till
"""), 'ru': s(f"""
WITH {F1}, {DISC}, stock AS (
  SELECT coalesce(sum(-m.quantity * m.unit_cost), 0) AS v
  FROM shop.stock_movement m JOIN f1 ON f1.employee_id = m.employee_id
  WHERE m.kind = 'issue' AND m.order_part_id IS NULL
    AND m.moved_at >= f1.left_on - 182 AND m.moved_at < f1.left_on + 1
), overrun AS (
  SELECT coalesce(sum(x.over_h * x.rate), 0) AS v
  FROM (
    SELECT (SELECT coalesce(sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600), 0)
            FROM shop.order_job j JOIN shop.time_entry t ON t.order_job_id = j.order_job_id
            WHERE j.repair_order_id = o.repair_order_id AND t.clock_out IS NOT NULL)
         - (SELECT coalesce(sum(l.hours), 0)
            FROM shop.order_job j JOIN shop.order_labor l ON l.order_job_id = j.order_job_id
            WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved') AS over_h,
           (SELECT r.rate FROM shop.labor_rate r
            WHERE r.location_id = o.location_id AND r.price_class = 'standard'
              AND r.valid_from <= o.opened_at::date
              AND (r.valid_to IS NULL OR r.valid_to >= o.opened_at::date)) AS rate
    FROM shop.repair_order o JOIN f1 ON f1.employee_id = o.advisor_id
    WHERE {F1_WINDOW}
  ) x
  WHERE x.over_h > 1
)
SELECT disc.v AS discounts_rub,
       round(stock.v, 2) AS stock_issued_without_sale_rub,
       round(overrun.v, 2) AS unbilled_clocked_hours_rub,
       round(disc.v + stock.v + overrun.v, 2) AS estimated_total_rub
FROM disc, stock, overrun
""")},
  expected={'columns': {'en': ['discounts_usd', 'voided_after_cash_usd', 'till_short_usd', 'estimated_total_usd'],
                        'ru': ['discounts_rub', 'stock_issued_without_sale_rub', 'unbilled_clocked_hours_rub', 'estimated_total_rub']},
            'rows': 1,
            'positive_columns': {'en': ['discounts_usd', 'voided_after_cash_usd', 'till_short_usd', 'estimated_total_usd'],
                                 'ru': ['discounts_rub', 'stock_issued_without_sale_rub', 'unbilled_clocked_hours_rub', 'estimated_total_rub']}},
  expect_keys=per_cfg(lambda c: {'estimated_total_@CUR@': {L('s2.total', c): 1}}),
  rule='s2.total',
  notes='Three non-overlapping components and their sum, an estimate (s2.total), all in the 26 weeks to his last day; his discounts are those of his revenue orders (every one of them planted: cash, 15 to 30 %, no approver). ru as billed, VAT inside (s2.amounts_basis). Void trap: a voided order keeps its total. ru: stock issued with no order line, at cost; clocked hours more than one hour past an order\'s sold hours, at the standard hour in force on its day.')

g(id='shop-S02-discount-rule-30d', category='money', asker='2',
  en='Which orders broke the discount rule in the last 30 days, and which advisor wrote each?',
  ru='Какие наряды за последние 30 дней нарушили правило по скидкам и кто из мастеров-приёмщиков оформил каждый?',
  sql=s("""
SELECT o.number AS order_number,
       e.first_name || ' ' || e.last_name AS advisor_name
FROM shop.repair_order o
JOIN shop.employee e ON e.employee_id = o.advisor_id
WHERE o.order_type = 'customer_pay'
  AND o.status NOT IN ('declined', 'void')
  AND o.discount_approved_by_id IS NULL
  AND o.discount_total > 0.10 * @BASE@
  AND o.opened_at >= @TODAY@ - interval '29 days'
ORDER BY o.opened_at
"""),
  expected={'columns': ['order_number', 'advisor_name'], 'nonempty': True},
  expect_keys=per_cfg(lambda c: {'advisor_name': {STAFF[c]['23']: L('s2.west.discounts_after', c)['unapproved_by_23']}}),
  rule='s2.west.discounts_after',
  notes='The rule: a discount above 10 % of the bill with no approver, on a customer-pay order not declined or void. Warranty and goodwill orders carry their whole amount in discount_total and are not discounts. The share is discount over the bill before discount, the same on gross (ru) or net (en) lines.')

g(id='shop-S02-west-leaks', category='money', asker='3',
  en='On which days was the Charlotte Pike till short by 20 dollars or more?',
  ru='Какие запчасти ушли со склада на Технической без продажи и в какие дни?',
  sql={'en': s("""
SELECT d.business_date AS business_day_yyyy_mm_dd
FROM shop.cash_drawer_close d
JOIN shop.location l ON l.location_id = d.location_id
WHERE l.name = @WEST@
  AND d.difference <= -20
ORDER BY d.business_date
"""), 'ru': s("""
SELECT m.moved_at::date AS issued_on_yyyy_mm_dd,
       p.description AS part_description
FROM shop.stock_movement m
JOIN shop.location l ON l.location_id = m.location_id
JOIN shop.part p ON p.part_id = m.part_id
WHERE l.name = @WEST@
  AND m.kind = 'issue'
  AND m.order_part_id IS NULL
ORDER BY m.moved_at
""")},
  expected={'columns': {'en': ['business_day_yyyy_mm_dd'], 'ru': ['issued_on_yyyy_mm_dd', 'part_description']},
            'rows': {'en': L('s2.f1.third', 'en')['count'], 'ru': L('s2.f1.second', 'ru')['count']}},
  rule={'en': 's2.f1.third', 'ru': 's2.f1.second'},
  notes={'en': 'Till counts are hidden below middle rank; the bookkeeper may read them. The whole history; no other day is 20 or more short.',
         'ru': 'An issue with no order line is stock that left without a sale; one row an issue. The whole history.'})

g(id='shop-S06-west-waiting-parts', category='parts', asker='22',
  en='Whose cars are waiting for parts at Charlotte Pike now, and for how long?',
  ru='Чьи машины на Технической сейчас ждут запчасти и сколько дней?',
  sql=s("""
SELECT c.name AS customer_name,
       v.year AS vehicle_year,
       v.make AS vehicle_make,
       v.model AS vehicle_model,
       (now() AT TIME ZONE l.time_zone)::date
         - (SELECT max(h.changed_at)::date FROM shop.order_status_history h
            WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts') AS days_waiting_count
FROM shop.repair_order o
JOIN shop.location l ON l.location_id = o.location_id
JOIN shop.customer c ON c.customer_id = o.customer_id
JOIN shop.vehicle v ON v.vehicle_id = o.vehicle_id
WHERE l.name = @WEST@ AND o.status = 'waiting_parts'
ORDER BY days_waiting_count DESC, o.number
"""),
  expected={'columns': ['customer_name', 'vehicle_year', 'vehicle_make', 'vehicle_model', 'days_waiting_count'],
            'nonempty': True},
  top=per_cfg(lambda c: {'customer_name': NINE_DAYS[c]}),
  rule='s6.waiting_at_t',
  notes='Calendar days since the order last entered waiting_parts, counted on the shop\'s own clock.')

g(id='shop-S11-seasonal-hire-start', category='people', asker='4',
  en='For each season in our records, when did the air-conditioning season start, and when did our seasonal hire start?',
  ru='По каждому сезону в нашей базе: с какой недели начинался сезон шиномонтажа, весной и осенью, и когда выходил сезонный шиномонтажник?',
  sql={'en': s("""
WITH hist AS (
  SELECT min(o.opened_at)::date AS start_on FROM shop.repair_order o
), months AS (
  SELECT gs::date AS month_on
  FROM hist, generate_series(date_trunc('month', hist.start_on + interval '1 month' - interval '1 day'),
                             date_trunc('month', now() AT TIME ZONE @TZ@) - interval '1 month',
                             interval '1 month') AS gs
), ac AS (
  SELECT m.month_on, count(j.order_job_id) AS jobs
  FROM months m
  LEFT JOIN shop.repair_order o ON date_trunc('month', o.opened_at)::date = m.month_on
                               AND o.status NOT IN ('declined', 'void')
  LEFT JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id AND j.status = 'approved'
       AND j.canned_job_id IN (SELECT cj.canned_job_id FROM shop.canned_job cj
                               JOIN shop.service_category sc ON sc.service_category_id = cj.service_category_id
                               WHERE sc.code = 'air_conditioning')
  GROUP BY m.month_on
), seasons AS (
  SELECT y AS season_year
  FROM hist, generate_series(extract(year FROM hist.start_on)::int, extract(year FROM now() AT TIME ZONE @TZ@)::int) AS y
  WHERE make_date(y, 5, 1) >= hist.start_on AND make_date(y, 8, 31) < @NOW@::date
)
SELECT s.season_year,
       to_char(min(a.month_on), 'YYYY-MM') AS season_start_month_yyyy_mm,
       (SELECT min(e.hired_on) FROM shop.employee e
        WHERE e.first_name = @F4FIRST@ AND e.last_name = @F4LAST@
          AND extract(year FROM e.hired_on) = s.season_year) AS hire_started_on_yyyy_mm_dd
FROM seasons s
JOIN ac a ON extract(year FROM a.month_on) = s.season_year
WHERE a.jobs > 1.5 * (SELECT avg(jobs) FROM ac)
GROUP BY s.season_year
ORDER BY s.season_year
"""), 'ru': s("""
WITH hist AS (
  SELECT min(o.opened_at)::date AS start_on FROM shop.repair_order o
), weeks AS (
  SELECT gs::date AS week_on
  FROM hist, generate_series(date_trunc('week', hist.start_on + interval '6 days'),
                             date_trunc('week', now() AT TIME ZONE @TZ@) - interval '7 days',
                             interval '7 days') AS gs
), tyre AS (
  SELECT w.week_on, count(j.order_job_id) AS jobs
  FROM weeks w
  LEFT JOIN shop.repair_order o ON date_trunc('week', o.opened_at)::date = w.week_on
                               AND o.status NOT IN ('declined', 'void')
  LEFT JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id AND j.status = 'approved'
       AND j.canned_job_id IN (SELECT cj.canned_job_id FROM shop.canned_job cj
                               WHERE cj.code IN ('seasonal_tyre_change', 'seasonal_wheel_swap'))
  GROUP BY w.week_on
), seasons AS (
  SELECT y AS season_year, h AS season_month
  FROM hist,
       generate_series(extract(year FROM hist.start_on)::int, extract(year FROM now() AT TIME ZONE @TZ@)::int) AS y,
       (VALUES (4), (10)) AS v(h)
  WHERE make_date(y, h, 13) >= hist.start_on
    AND make_date(y, h + 1, CASE h WHEN 4 THEN 10 ELSE 9 END) < @NOW@::date
)
SELECT s.season_year,
       s.season_month AS season_month_1_12,
       min(t.week_on) AS season_start_week_yyyy_mm_dd,
       (SELECT min(e.hired_on) FROM shop.employee e
        WHERE e.first_name = @F4FIRST@ AND e.last_name = @F4LAST@
          AND extract(year FROM e.hired_on) = s.season_year
          AND (extract(month FROM e.hired_on) <= 6) = (s.season_month = 4)) AS hire_started_on_yyyy_mm_dd
FROM seasons s
JOIN tyre t ON extract(year FROM t.week_on) = s.season_year
           AND (extract(month FROM t.week_on) <= 6) = (s.season_month = 4)
WHERE t.jobs > 2 * (SELECT avg(jobs) FROM tyre)
GROUP BY s.season_year, s.season_month
ORDER BY s.season_year, s.season_month
""")},
  expected={'columns': {'en': ['season_year', 'season_start_month_yyyy_mm', 'hire_started_on_yyyy_mm_dd'],
                        'ru': ['season_year', 'season_month_1_12', 'season_start_week_yyyy_mm_dd', 'hire_started_on_yyyy_mm_dd']},
            'nonempty': True},
  expect_keys={'hire_started_on_yyyy_mm_dd': '@[d for d in f4_seasons if d >= history_start]'},  # seasons whole inside the history
  rule='season.hire',
  notes='The season as the context defines it: only seasons that lie whole inside the history count; the threshold is season.threshold (en month above 1.5 times the mean month of air-conditioning jobs, ru week above twice the mean week of seasonal tyre jobs), all shops. The hire has one employee row per season.')

g(id='shop-S15-customer-count', category='customers', asker='2',
  en='How many customers do we have?',
  ru='Сколько у нас клиентов?',
  sql=s("""
SELECT count(DISTINCT coalesce(c.phone, 'id:' || c.customer_id)) AS customers_count
FROM shop.customer c
WHERE c.name <> @WALKIN@
"""),
  expected={'columns': ['customers_count'], 'rows': 1},
  rule='s15.mess',
  notes='Duplicate trap: two records with one phone are one customer. The walk-in record is not a customer.')

g(id='shop-S15-revenue-last-month', category='revenue', asker='2',
  en="What was last month's revenue?",
  ru='Какая у нас выручка за прошлый месяц?',
  sql=s("""
WITH @INV@
SELECT round(sum(o.total - o.tax_total), 2) AS revenue_before_tax_@CUR@
FROM shop.repair_order o JOIN inv ON inv.repair_order_id = o.repair_order_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@) - interval '1 month'
  AND inv.invoiced_at < date_trunc('month', now() AT TIME ZONE @TZ@)
"""),
  expected={'columns': ['revenue_before_tax_@CUR@'], 'rows': 1},
  rule='erp/context/RULES.md#money',
  notes='Void, warranty and goodwill traps: voids keep totals, free work totals zero; open orders are not revenue. Tax: before tax is total - tax_total in both installs.')

g(id='shop-S15-average-order-by-shop', category='revenue', asker='2',
  en='What has the average order been at each shop over the last 12 months?',
  ru='Какой средний наряд был в каждом сервисе за последние 12 месяцев?',
  sql=s("""
WITH @INV@
SELECT l.name AS shop_name,
       round(avg(o.total - o.tax_total), 2) AS average_order_before_tax_@CUR@
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.location l ON l.location_id = o.location_id
WHERE @REV@
  AND inv.invoiced_at >= @TODAY@ - interval '12 months'
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'average_order_before_tax_@CUR@'], 'rows': 3},
  expect_keys=per_cfg(lambda c: {'shop_name': {L('geo.short_name', c)[s]: 1 for s in ('main', 'east', 'west')}}),
  rule='volume.average_order',
  notes='Closed orders of the last 12 months before tax; the never-closed orders, voids and free warranty work are out.')

g(id='shop-S15-wrong-mileage', category='quality', asker='4',
  en='Which orders have a mileage that cannot be right?',
  ru='В каких нарядах пробег явно неверный?',
  sql=s("""
WITH seq AS (
  SELECT o.number, o.opened_at, o.mileage_in,
         lag(o.mileage_in) OVER (PARTITION BY o.vehicle_id ORDER BY o.opened_at) AS prev_in
  FROM shop.repair_order o
  WHERE o.mileage_in IS NOT NULL
)
SELECT number AS order_number
FROM seq
WHERE mileage_in < prev_in OR mileage_in >= 10 * prev_in
ORDER BY opened_at
"""),
  expected={'columns': ['order_number'], 'rows': per_cfg(lambda c: L('s15.mess', c)['wrong_mileage_orders'])},
  rule='s15.mess',
  notes='A reading below the car\'s previous one, or ten times it or more; the whole history. The ten-times readings are each car\'s last visit.')

g(id='shop-S15-open-over-60-days', category='orders', asker='2',
  en='Which orders have been open for more than 60 days?',
  ru='Какие наряды открыты больше 60 дней?',
  sql=s("""
SELECT o.number AS order_number
FROM shop.repair_order o
WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined')
  AND o.opened_at::date < @TODAY@::date - 60
ORDER BY o.opened_at
"""),
  expected={'columns': ['order_number'],
            'rows': per_cfg(lambda c: 1 + L('s15.mess', c)['never_closed']['others_over_60_days'])},
  rule='s15.dates',
  notes='Never-closed orders trap (west since the Wednesday of week T-22, main and east since the Tuesdays of T-12 and T-10); an account order waiting at invoiced on an unpaid or disputed statement is money owed, not open. Calendar days to today.')

# ---------------------------------------------------------------- new manager questions (28)

g(id='shop-revenue-last-week', category='revenue', asker='2',
  en='How much did we make last week?', ru='Сколько мы заработали за прошлую неделю?',
  sql=s("""
WITH @INV@
SELECT round(sum(o.total - o.tax_total), 2) AS revenue_before_tax_@CUR@
FROM shop.repair_order o JOIN inv ON inv.repair_order_id = o.repair_order_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('week', now() AT TIME ZONE @TZ@) - interval '7 days'
  AND inv.invoiced_at < date_trunc('week', now() AT TIME ZONE @TZ@)
"""),
  expected={'columns': ['revenue_before_tax_@CUR@'], 'rows': 1},
  rule='erp/context/RULES.md#money',
  notes='Void, warranty/goodwill and tax traps: voids keep totals, free work is not revenue, revenue is before tax (en tax on top, ru VAT inside). Monday to Sunday before this week.')

g(id='shop-revenue-30d-by-shop', category='revenue', asker='2',
  en="What's revenue been the last 30 days at each shop?", ru='Какая выручка у каждого сервиса за последние 30 дней?',
  sql=s("""
WITH @INV@
SELECT l.name AS shop_name,
       round(sum(o.total - o.tax_total), 2) AS revenue_before_tax_@CUR@
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.location l ON l.location_id = o.location_id
WHERE @REV@
  AND inv.invoiced_at >= @TODAY@ - interval '29 days'
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'revenue_before_tax_@CUR@'], 'rows': 3},
  rule='erp/context/RULES.md#money',
  notes='Today and the 29 days before it, on the home calendar; dated by first invoice.')

g(id='shop-revenue-12-months', category='revenue', asker='2',
  en='What did we bring in over the last 12 months?', ru='Сколько мы выручили за последние 12 месяцев?',
  sql=s("""
WITH @INV@
SELECT round(sum(o.total - o.tax_total), 2) AS revenue_before_tax_@CUR@
FROM shop.repair_order o JOIN inv ON inv.repair_order_id = o.repair_order_id
WHERE @REV@
  AND inv.invoiced_at >= @TODAY@ - interval '12 months'
"""),
  expected={'columns': ['revenue_before_tax_@CUR@'], 'rows': 1},
  rule='volume.revenue_year.company',
  notes='Before tax; voids, declined estimates, open orders and free warranty work left out.')

g(id='shop-average-order-this-month', category='revenue', asker='2',
  en="What's the average ticket at each shop so far this month?", ru='Какой средний чек в каждом сервисе с начала месяца?',
  sql=s("""
WITH @INV@
SELECT l.name AS shop_name,
       round(avg(o.total - o.tax_total), 2) AS average_order_before_tax_@CUR@
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.location l ON l.location_id = o.location_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@)
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'average_order_before_tax_@CUR@'], 'nonempty': True},
  rule='erp/context/RULES.md#money',
  notes='Free warranty orders (total 0) would drag the average down if counted.')

g(id='shop-top-jobs-90d', category='revenue', asker='4',
  en='What were the ten jobs that brought in the most money over the last 90 days?', ru='Какие десять работ принесли больше всего денег за последние 90 дней?',
  sql=s("""
WITH @INV@, jobs AS (
  SELECT j.order_job_id, j.canned_job_id, @NET@ AS divisor
  FROM shop.repair_order o
  JOIN inv ON inv.repair_order_id = o.repair_order_id
  JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  WHERE @REV@
    AND j.status = 'approved'
    AND inv.invoiced_at >= @TODAY@ - interval '89 days'
), job_money AS (
  SELECT jb.canned_job_id,
         ((SELECT coalesce(sum(l.amount - l.discount), 0) FROM shop.order_labor l WHERE l.order_job_id = jb.order_job_id)
        + (SELECT coalesce(sum(p.quantity * p.unit_price), 0) FROM shop.order_part p WHERE p.order_job_id = jb.order_job_id)
        + (SELECT coalesce(sum(sb.price), 0) FROM shop.order_sublet sb WHERE sb.order_job_id = jb.order_job_id))
         / jb.divisor AS amount
  FROM jobs jb
)
SELECT cj.name AS job_name,
       round(sum(jm.amount), 2) AS revenue_before_tax_@CUR@
FROM job_money jm JOIN shop.canned_job cj ON cj.canned_job_id = jm.canned_job_id
GROUP BY cj.canned_job_id, cj.name
ORDER BY revenue_before_tax_@CUR@ DESC
LIMIT 10
"""),
  expected={'columns': ['job_name', 'revenue_before_tax_@CUR@'], 'rows': 10},
  rule='mixrow.category_revenue',
  notes='Tax trap: ru line prices hold VAT and are divided by 1 + rate; declined jobs keep their lines and are left out; order-level fees are not a job\'s.')

g(id='shop-cars-per-day', category='orders', asker='2',
  en='On average, how many cars a weekday has each shop had over the last 12 months?', ru='Сколько машин в день в среднем принимал каждый сервис за последние 12 месяцев?',
  sql=s("""
WITH days AS (
  SELECT d.location_id, d.business_date
  FROM shop.cash_drawer_close d
  WHERE d.business_date >= @TODAY@ - interval '12 months'
    AND @WD@
), visits AS (
  SELECT o.location_id, o.opened_at::date AS day_on, count(*) AS n
  FROM shop.repair_order o
  WHERE o.status NOT IN ('declined', 'void')
    AND o.opened_at >= @TODAY@ - interval '12 months'
  GROUP BY o.location_id, o.opened_at::date
)
SELECT l.name AS shop_name,
       round(coalesce(sum(v.n), 0)::numeric / count(*), 2) AS cars_per_day_avg
FROM days
JOIN shop.location l ON l.location_id = days.location_id
LEFT JOIN visits v ON v.location_id = days.location_id AND v.day_on = days.business_date
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'cars_per_day_avg'], 'rows': 3},
  rule='volume.orders_per_day.main, volume.orders_per_day.east, volume.orders_per_day.west',
  notes='Visits on the shop\'s working days (a till count) over those days, the last 12 months; en asks for a weekday, so Monday to Friday only (the flagship\'s Saturday morning is left out), ru every open day.')

g(id='shop-busiest-weekday', category='orders', asker='4',
  en="What's our busiest day of the week, and how many cars a day do we see on it?", ru='В какой день недели у нас больше всего машин и сколько их в такой день в среднем?',
  sql=s("""
WITH days AS (
  SELECT DISTINCT d.business_date AS day_on
  FROM shop.cash_drawer_close d
), per_day AS (
  SELECT days.day_on, count(o.repair_order_id) AS n
  FROM days
  LEFT JOIN shop.repair_order o ON o.opened_at::date = days.day_on AND o.status NOT IN ('declined', 'void')
  GROUP BY days.day_on
)
SELECT extract(isodow FROM day_on)::int AS weekday_iso_1_7,
       round(avg(n), 2) AS cars_per_day_avg
FROM per_day
GROUP BY 1
ORDER BY cars_per_day_avg DESC
LIMIT 1
"""),
  expected={'columns': ['weekday_iso_1_7', 'cars_per_day_avg'], 'rows': 1},
  rule='mixrow.weekday',
  notes='All history, the company together: visits a working day (a date any shop has a till count), each order on its own shop\'s calendar day.')

g(id='shop-open-orders-now', category='orders', asker='4',
  en='How many jobs are still open at each shop?', ru='Сколько нарядов сейчас висит открытыми в каждом сервисе?',
  sql=s("""
SELECT l.name AS shop_name,
       count(*) AS open_orders_count
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.status NOT IN ('invoiced', 'paid', 'void', 'declined')
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'open_orders_count'], 'nonempty': True},
  rule='erp/context/RULES.md#orders',
  notes='Open-order trap: an account order sitting at invoiced is money owed, not an open job; the never-closed orders are open.')

g(id='shop-west-early-arrivals', category='orders', asker='2',
  en='How many cars came into Charlotte Pike before 9 our time last week?', ru='Сколько машин на прошлой неделе приехало на Техническую раньше девяти по нашему времени?',
  sql=s("""
WITH arrivals AS (
  SELECT (o.opened_at AT TIME ZONE l.time_zone) AT TIME ZONE @TZ@ AS home_time
  FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
  WHERE l.name = @WEST@ AND o.status NOT IN ('declined', 'void')
)
SELECT count(*) AS orders_count
FROM arrivals
WHERE home_time >= date_trunc('week', now() AT TIME ZONE @TZ@) - interval '7 days'
  AND home_time < date_trunc('week', now() AT TIME ZONE @TZ@)
  AND extract(hour FROM home_time) < 9
"""),
  expected={'columns': ['orders_count'], 'rows': 1},
  rule='geo.zone_gap_hours',
  notes="Clock trap: the shop's timestamps are its own wall clock, an hour behind home; 9:00 home time is 8:00 there. A car that came in is a visit: not declined, not void.")

g(id='shop-new-vs-returning-this-month', category='customers', asker='2',
  en="How many new customers have we had this month, against ones who've been in before?", ru='Сколько в этом месяце новых клиентов и сколько тех, кто уже был у нас раньше?',
  sql=s("""
WITH person AS (
  SELECT c.customer_id, coalesce(c.phone, 'id:' || c.customer_id) AS person_key
  FROM shop.customer c
  WHERE c.name <> @WALKIN@
), visits AS (
  SELECT p.person_key, o.opened_at
  FROM shop.repair_order o JOIN person p ON p.customer_id = o.customer_id
  WHERE o.status NOT IN ('declined', 'void')
), first_visit AS (
  SELECT person_key, min(opened_at) AS first_at FROM visits GROUP BY person_key
), this_month AS (
  SELECT DISTINCT person_key FROM visits
  WHERE opened_at >= date_trunc('month', now() AT TIME ZONE @TZ@)
)
SELECT count(*) FILTER (WHERE f.first_at >= date_trunc('month', now() AT TIME ZONE @TZ@)) AS new_customers_count,
       count(*) FILTER (WHERE f.first_at < date_trunc('month', now() AT TIME ZONE @TZ@)) AS returning_customers_count
FROM this_month t JOIN first_visit f ON f.person_key = t.person_key
"""),
  expected={'columns': ['new_customers_count', 'returning_customers_count'], 'rows': 1},
  rule='erp.customer.returning_share',
  notes='Duplicate trap (merge by phone), walk-in record left out, and new means first visit, not created_at (the bought shop\'s customers were all created on one day).')

g(id='shop-top-customers', category='customers', asker='2',
  en='Who are our ten best customers of all time?', ru='Кто наши десять лучших клиентов за всё время?',
  sql=s("""
WITH @INV@, person AS (
  SELECT c.customer_id, c.name, coalesce(c.phone, 'id:' || c.customer_id) AS person_key
  FROM shop.customer c
  WHERE c.name <> @WALKIN@
)
SELECT min(p.name) AS customer_name
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN person p ON p.customer_id = o.customer_id
WHERE @REV@
GROUP BY p.person_key
ORDER BY sum(o.total - o.tax_total) DESC
LIMIT 10
"""),
  expected={'columns': ['customer_name'], 'rows': 10},
  top=per_cfg(lambda c: {'customer_name': ACCOUNTS[c]['A1']}),
  rule='acct.A1.average_order',
  notes='Best = the most revenue, all history. Walk-in trap: the counter-sales record holds hundreds of orders and is not a customer; duplicate records merged by phone.')

g(id='shop-no-shows-west-last-month', category='customers', asker='22',
  en='How many no-shows did Charlotte Pike have last month?', ru='Сколько в прошлом месяце было неявок на Технической?',
  sql=s("""
SELECT count(*) FILTER (WHERE a.status = 'no_show') AS no_shows_count
FROM shop.appointment a JOIN shop.location l ON l.location_id = a.location_id
WHERE l.name = @WEST@
  AND a.starts_at >= date_trunc('month', now() AT TIME ZONE l.time_zone) - interval '1 month'
  AND a.starts_at < date_trunc('month', now() AT TIME ZONE l.time_zone)
"""),
  expected={'columns': ['no_shows_count'], 'rows': 1},
  rule='erp.appointment.outcome',
  notes='The calendar month before this one, on the shop\'s own clock, by the booking\'s start.')

g(id='shop-oil-price', category='parts', asker='6',
  en='What does a quart of each motor oil we use in oil changes cost for a passenger car today?', ru='Сколько сегодня стоит литр каждого моторного масла, которое мы льём при замене масла, для легкового автомобиля?',
  sql=s("""
SELECT p.brand AS oil_brand,
       min(p.list_price) AS list_price_@CUR@_per_unit
FROM shop.part p
WHERE p.part_number IS NULL
  AND EXISTS (SELECT 1 FROM shop.order_part op
              JOIN shop.order_job j ON j.order_job_id = op.order_job_id
              JOIN shop.canned_job cj ON cj.canned_job_id = j.canned_job_id
              WHERE cj.code = 'oil_service' AND op.part_id = p.part_id)
GROUP BY p.brand
ORDER BY list_price_@CUR@_per_unit, p.brand
"""),
  expected={'columns': ['oil_brand', 'list_price_@CUR@_per_unit'], 'rows': 3},
  rule='erp/context/RULES.md#money',
  notes="Today's list price per unit (quart or litre) of the oils the oil service uses; fluids carry no part number; the lowest row per brand is the passenger-car price.")

g(id='shop-oil-change-price', category='parts', asker='6',
  en="What's the labor on an oil change?", ru='Сколько стоит работа по замене масла, без самого масла?',
  sql=s("""
SELECT CASE WHEN cj.labor_pricing = 'menu' THEN cj.menu_price
            ELSE round(cj.hours * r.rate, 2) END AS oil_change_labour_@CUR@
FROM shop.canned_job cj
CROSS JOIN shop.labor_rate r
JOIN shop.location l ON l.location_id = r.location_id
WHERE cj.code = 'oil_service'
  AND l.name = @MAIN@
  AND r.price_class = 'standard'
  AND r.valid_to IS NULL
"""),
  expected={'columns': ['oil_change_labour_@CUR@'], 'rows': 1},
  rule='price.hour.posted',
  notes="Today's price for a passenger car at the asker's shop: en a menu price, ru hours times the posted hour (VAT inside).")

g(id='shop-parts-waiting', category='parts', asker='4',
  en='How many cars are waiting on parts right now at each shop, and how many days has the longest been waiting?', ru='Сколько машин сейчас ждут запчасти в каждом сервисе и сколько дней ждёт самая давняя?',
  sql=s("""
SELECT l.name AS shop_name,
       count(*) AS cars_waiting_count,
       max((now() AT TIME ZONE l.time_zone)::date
           - (SELECT max(h.changed_at)::date FROM shop.order_status_history h
              WHERE h.repair_order_id = o.repair_order_id AND h.status = 'waiting_parts')) AS longest_wait_days
FROM shop.repair_order o JOIN shop.location l ON l.location_id = o.location_id
WHERE o.status = 'waiting_parts'
GROUP BY l.location_id, l.name
ORDER BY cars_waiting_count DESC, l.location_id
"""),
  expected={'columns': ['shop_name', 'cars_waiting_count', 'longest_wait_days'], 'nonempty': True},
  top=per_cfg(lambda c: dict(zip(('shop_name', 'cars_waiting_count'), map(list, zip(*sorted(
      ((L('geo.short_name', c)[s], len(L('s6.waiting_at_t', c)[f'{s}_days'])) for s in ('main', 'east', 'west')), key=lambda x: -x[1])))))),
  rule='s6.waiting_at_t',
  notes="Calendar days since the order last entered waiting_parts, on each shop's own calendar.")

g(id='shop-supplier-late', category='parts', asker='4',
  en='How often is each supplier late?', ru='Как часто опаздывает каждый поставщик?',
  sql=s("""
SELECT v.name AS vendor_name,
       round(count(*) FILTER (WHERE po.received_at::date > po.promised_at::date)::numeric / count(*), 3) AS late_share_float_0_1
FROM shop.purchase_order po JOIN shop.vendor v ON v.vendor_id = po.vendor_id
WHERE po.status = 'received'
GROUP BY v.vendor_id, v.name
ORDER BY late_share_float_0_1 DESC, v.name
"""),
  expected={'columns': ['vendor_name', 'late_share_float_0_1'], 'nonempty': True},
  top=per_cfg(lambda c: {'vendor_name': VENDORS[c]['V2']}),
  rule='parts.on_time.V2',
  notes='All history; late = received on a later day than promised, over received purchase orders; cancelled orders are not late deliveries.')

g(id='shop-parts-margin-last-month', category='parts', asker='2',
  en='What was our margin on parts last month?', ru='Какая была маржа на запчастях в прошлом месяце?',
  sql=s("""
WITH @INV@
SELECT round(1 - sum(p.quantity * p.unit_cost) / nullif(sum(p.quantity * p.unit_price / @NET@), 0), 4) AS parts_margin_float_0_1
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id AND j.status = 'approved'
JOIN shop.order_part p ON p.order_job_id = j.order_job_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@) - interval '1 month'
  AND inv.invoiced_at < date_trunc('month', now() AT TIME ZONE @TZ@)
"""),
  expected={'columns': ['parts_margin_float_0_1'], 'rows': 1},
  rule='mixrow.parts_margin',
  notes='The company together, revenue\'s orders dated by first invoice. Tax trap: ru part prices hold VAT, divided out before the margin; part lines of declined jobs are not sales; discount_total is the labour lines\'.')

g(id='shop-mechanic-billed-hours', category='people', asker='4',
  en='How many hours did each mechanic bill last month?', ru='Сколько нормо-часов закрыл каждый механик в прошлом месяце?',
  sql=s("""
WITH @INV@
SELECT e.first_name || ' ' || e.last_name AS technician_name,
       sum(lab.hours) AS billed_hours
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id AND j.status = 'approved'
JOIN shop.order_labor lab ON lab.order_job_id = j.order_job_id
JOIN shop.employee e ON e.employee_id = lab.technician_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@) - interval '1 month'
  AND inv.invoiced_at < date_trunc('month', now() AT TIME ZONE @TZ@)
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY billed_hours DESC, technician_name
"""),
  expected={'columns': ['technician_name', 'billed_hours'], 'nonempty': True},
  rule='erp/context/RULES.md#orders',
  notes='Billed hours: sold hours of revenue\'s orders dated by first invoice. Warranty trap: comeback lines carry hours nobody pays for; sold hours, not clocked; declined jobs\' lines left out.')

g(id='shop-recommended-sold-by-advisor', category='people', asker='4',
  en='How much of the recommended work has each advisor sold over the last 90 days?', ru='Какую часть рекомендаций продал каждый приёмщик за последние 90 дней?',
  sql=s("""
SELECT e.first_name || ' ' || e.last_name AS advisor_name,
       round(count(*) FILTER (WHERE j.status = 'approved')::numeric / count(*), 3) AS sold_share_float_0_1
FROM shop.repair_order o
JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
JOIN shop.employee e ON e.employee_id = o.advisor_id
WHERE o.status <> 'void'
  AND j.status IN ('approved', 'declined')
  AND EXISTS (SELECT 1 FROM shop.inspection_item ii WHERE ii.order_job_id = j.order_job_id)
  AND o.opened_at >= @TODAY@ - interval '89 days'
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY sold_share_float_0_1 DESC, advisor_name
"""),
  expected={'columns': ['advisor_name', 'sold_share_float_0_1'], 'nonempty': True},
  top=per_cfg(lambda c: {'advisor_name': STAFF[c]['16']}),
  rule='sold.company',
  notes='Recommended = raised from an inspection item; share over approved plus declined among those jobs, never over every job.')

g(id='shop-tech-efficiency-this-month', category='people', asker='4',
  en='How efficient are the techs this month?', ru='Какая эффективность у механиков в этом месяце?',
  sql=s("""
WITH @INV@, jobs AS (
  SELECT j.order_job_id
  FROM shop.repair_order o
  JOIN inv ON inv.repair_order_id = o.repair_order_id
  JOIN shop.order_job j ON j.repair_order_id = o.repair_order_id
  WHERE @REV@
    AND j.status = 'approved'
    AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@)
), sold AS (
  SELECT lab.technician_id, sum(lab.hours) AS h
  FROM shop.order_labor lab JOIN jobs ON jobs.order_job_id = lab.order_job_id
  WHERE lab.technician_id IS NOT NULL
  GROUP BY lab.technician_id
), clocked AS (
  SELECT t.technician_id, sum(extract(epoch FROM t.clock_out - t.clock_in) / 3600) AS h
  FROM shop.time_entry t JOIN jobs ON jobs.order_job_id = t.order_job_id
  WHERE t.clock_out IS NOT NULL
  GROUP BY t.technician_id
)
SELECT e.first_name || ' ' || e.last_name AS technician_name,
       round(s.h / nullif(c.h, 0), 3) AS sold_over_clocked_float
FROM sold s
JOIN clocked c ON c.technician_id = s.technician_id
JOIN shop.employee e ON e.employee_id = s.technician_id
ORDER BY sold_over_clocked_float DESC, technician_name
"""),
  expected={'columns': ['technician_name', 'sold_over_clocked_float'], 'nonempty': True},
  rule='erp.time.clocked_over_sold',
  notes='Sold hours over clocked hours on the approved jobs of revenue\'s orders first invoiced this month, each technician his own; a clock still running is left out.')

g(id='shop-comebacks-by-mechanic', category='quality', asker='2',
  en='How many comebacks has each mechanic had over the last 12 months?', ru='Сколько возвратов было у каждого механика за последние 12 месяцев?',
  sql=s("""
WITH came_back AS (
  SELECT o.repair_order_id,
         (SELECT lab.technician_id
          FROM shop.order_job j JOIN shop.order_labor lab ON lab.order_job_id = j.order_job_id
          WHERE j.repair_order_id = o.repair_order_id AND j.status = 'approved' AND lab.technician_id IS NOT NULL
          GROUP BY lab.technician_id
          ORDER BY sum(lab.hours) DESC, lab.technician_id
          LIMIT 1) AS technician_id
  FROM shop.repair_order o
  WHERE @REV@
    AND o.opened_at >= @TODAY@ - interval '12 months'
    AND EXISTS (SELECT 1 FROM shop.repair_order cb
                WHERE cb.comeback_of_id = o.repair_order_id AND cb.status <> 'void'
                  AND cb.order_type IN ('warranty', 'goodwill'))
)
SELECT e.first_name || ' ' || e.last_name AS technician_name,
       count(*) AS comebacks_count
FROM came_back b
JOIN shop.employee e ON e.employee_id = b.technician_id
GROUP BY e.employee_id, e.first_name, e.last_name
ORDER BY comebacks_count DESC, technician_name
"""),
  expected={'columns': ['technician_name', 'comebacks_count'], 'nonempty': True},
  rule='comeback.definition',
  notes='Counted on the paid orders opened in the last 12 months that came back (any warranty or goodwill repeat; ru has warranty repeats within 30 days only), each charged to the technician with the most sold hours on it, as the people rows pNN.comebacks count them.')

g(id='shop-free-work-this-year', category='quality', asker='2',
  en='How much warranty and goodwill work have we done free this year, at its prices?', ru='На какую сумму мы с начала года бесплатно сделали работ по гарантии и в порядке компенсации, по ценам этих работ?',
  sql=s("""
SELECT round(coalesce(sum(@BASE@ / @NET@), 0), 2) AS free_work_before_tax_@CUR@
FROM shop.repair_order o
WHERE o.order_type IN ('warranty', 'goodwill')
  AND o.status <> 'void'
  AND o.opened_at >= date_trunc('year', now() AT TIME ZONE @TZ@)
"""),
  expected={'columns': ['free_work_before_tax_@CUR@'], 'rows': 1},
  rule='erp.warranty_order_totals',
  notes='Warranty trap: these orders total 0; the value of the free work is in the lines (labour + parts + sublet + fees), ru with VAT divided out.')

g(id='shop-accounts-owed', category='accounts', asker='3',
  en='What do our company accounts owe right now, and how fast have they paid over the last six months?', ru='Какая сейчас дебиторка по корпоративным клиентам и за сколько дней в среднем они платили последние полгода?',
  sql=s("""
WITH paid AS (
  SELECT p.statement_id, min(p.received_at)::date AS paid_on
  FROM shop.payment p
  WHERE p.statement_id IS NOT NULL AND p.kind = 'payment'
  GROUP BY p.statement_id
)
SELECT c.name AS account_name,
       (SELECT coalesce(sum(o.total), 0) FROM shop.repair_order o
        WHERE o.customer_id = c.customer_id AND o.order_type = 'customer_pay' AND o.status = 'invoiced') AS owed_@CUR@,
       (SELECT round(avg(pd.paid_on - s.issued_on), 2)
        FROM shop.statement s JOIN paid pd ON pd.statement_id = s.statement_id
        WHERE s.customer_id = c.customer_id AND s.issued_on >= @TODAY@ - interval '6 months') AS days_to_pay_avg
FROM shop.customer c
WHERE c.payment_terms_days IS NOT NULL
ORDER BY owed_@CUR@ DESC, account_name
"""),
  expected={'columns': ['account_name', 'owed_@CUR@', 'days_to_pay_avg'], 'rows': 6},
  rule='acct.A1.days_to_pay',
  notes='The six accounts billed on terms (not every company). Owed: the totals of their orders still at invoiced, billed or not yet (en: the current month is on no statement yet). Days to pay = first payment date minus the issue date, over bills issued in the last six months and paid; a disputed bill is still owed.')

g(id='shop-account-revenue', category='accounts', asker='2',
  en='How much did each company account bring in over the last 12 months?', ru='Сколько принёс каждый корпоративный клиент за последние 12 месяцев?',
  sql=s("""
WITH @INV@
SELECT c.name AS account_name,
       coalesce(round(sum(o.total - o.tax_total), 2), 0) AS revenue_before_tax_@CUR@
FROM shop.customer c
LEFT JOIN (shop.repair_order o JOIN inv ON inv.repair_order_id = o.repair_order_id)
       ON o.customer_id = c.customer_id
      AND @REV@
      AND inv.invoiced_at >= @TODAY@ - interval '12 months'
WHERE c.payment_terms_days IS NOT NULL
GROUP BY c.customer_id, c.name
ORDER BY revenue_before_tax_@CUR@ DESC, account_name
"""),
  expected={'columns': ['account_name', 'revenue_before_tax_@CUR@'], 'rows': 6},
  top=per_cfg(lambda c: {'account_name': ACCOUNTS[c]['A1']}),
  rule='acct.A1.average_order',
  notes='Before tax, every account billed on terms, one with nothing at 0; the most visits (A2) is not the most money (A1).')

g(id='shop-unpaid-orders', category='money', asker='3',
  en="Which orders haven't been paid yet, leaving out the company accounts?", ru='Какие наряды до сих пор не оплачены, не считая корпоративных клиентов?',
  sql=s("""
WITH @INV@, paid AS (
  SELECT p.repair_order_id, sum(CASE WHEN p.kind = 'refund' THEN -p.amount ELSE p.amount END) AS amount
  FROM shop.payment p
  WHERE p.repair_order_id IS NOT NULL
  GROUP BY p.repair_order_id
)
SELECT o.number AS order_number
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
JOIN shop.customer c ON c.customer_id = o.customer_id
LEFT JOIN paid pd ON pd.repair_order_id = o.repair_order_id
WHERE o.status = 'invoiced'
  AND o.order_type = 'customer_pay'
  AND c.payment_terms_days IS NULL
  AND o.total - coalesce(pd.amount, 0) > 0
ORDER BY inv.invoiced_at, o.number
"""),
  expected={'columns': ['order_number'], 'nonempty': True},
  rule='erp/context/RULES.md#payments',
  notes='Payments trap: deposits count, refunds are positive and are subtracted; a voided order can carry a payment and is not owed.')

g(id='shop-discounts-this-month', category='money', asker='2',
  en='How much have we given away in discounts this month?', ru='На какую сумму мы дали скидок с начала месяца?',
  sql=s("""
WITH @INV@
SELECT round(coalesce(sum(o.discount_total / @NET@), 0), 2) AS discounts_before_tax_@CUR@
FROM shop.repair_order o
JOIN inv ON inv.repair_order_id = o.repair_order_id
WHERE @REV@
  AND inv.invoiced_at >= date_trunc('month', now() AT TIME ZONE @TZ@)
"""),
  expected={'columns': ['discounts_before_tax_@CUR@'], 'rows': 1},
  rule='erp/context/RULES.md#money',
  notes="The company together, revenue's orders dated by first invoice, before tax. Warranty trap: a warranty or goodwill order's discount_total is the whole free amount, not a discount; voids left out.")

g(id='shop-cash-last-week', category='money', asker='3',
  en='How much cash did each shop take in last week?', ru='Сколько наличными приняли в каждом сервисе за прошлую неделю?',
  sql=s("""
SELECT l.name AS shop_name,
       sum(CASE WHEN p.kind = 'refund' THEN -p.amount ELSE p.amount END) AS cash_taken_@CUR@
FROM shop.payment p
JOIN shop.repair_order o ON o.repair_order_id = p.repair_order_id
JOIN shop.location l ON l.location_id = o.location_id
WHERE p.method = 'cash'
  AND p.received_at >= date_trunc('week', now() AT TIME ZONE @TZ@) - interval '7 days'
  AND p.received_at < date_trunc('week', now() AT TIME ZONE @TZ@)
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'cash_taken_@CUR@'], 'rows': 3},
  rule='erp/context/RULES.md#payments',
  notes='Payments trap: refunds are stored positive and must be subtracted; payments, not till counts (hidden below middle).')

g(id='shop-labour-rate', category='money', asker='4',
  en="What are our hourly labor rates right now at each shop, the standard rate and the negotiated one?", ru='Какой у нас сейчас нормо-час в каждом сервисе, обычный и договорной?',
  sql=s("""
SELECT l.name AS shop_name,
       max(r.rate) FILTER (WHERE r.price_class = 'standard') AS standard_rate_@CUR@,
       max(r.rate) FILTER (WHERE r.price_class = 'company_account') AS negotiated_rate_@CUR@
FROM shop.labor_rate r JOIN shop.location l ON l.location_id = r.location_id
WHERE r.valid_to IS NULL
GROUP BY l.location_id, l.name
ORDER BY l.location_id
"""),
  expected={'columns': ['shop_name', 'standard_rate_@CUR@', 'negotiated_rate_@CUR@'], 'rows': 3},
  expect_keys=per_cfg(lambda c: {'standard_rate_@CUR@': {L('price.hour.posted', c): 3},
                                 'negotiated_rate_@CUR@': {L('price.hour.company', c): 3}}),
  rule='price.hour.posted',
  notes='The row in force today; old orders carry the rate of their own date. ru: the hour holds VAT.')


def pick(value, cfg):
    return value[cfg] if isinstance(value, dict) and set(value) == {'en', 'ru'} else value


def subst(text, cfg):
    for key, val in CFG[cfg].items():
        text = text.replace(key, val)
    assert '@' not in text.replace("'@", ''), text
    return text


class Literal(str):
    pass


def literal(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(Literal, literal)


def build(cfg):
    out = []
    for q in G:
        expected = {}
        for key, val in q['expected'].items():
            val = pick(val, cfg)
            if key == 'columns':
                val = [subst(c, cfg) for c in val]
            expected[key] = val
        rule = pick(q['rule'], cfg)
        names = {}
        for name in ('expect_keys', 'top'):
            if name in q:
                names[name] = {subst(column, cfg): val for column, val in pick(q[name], cfg).items()}
        out.append({
            'id': q['id'],
            'question': q['en'] if cfg == 'en' else q['ru'],
            'asker': q['asker'],
            'sql': Literal(subst(pick(q['sql'], cfg), cfg)),
            'expected': expected,
            'rule': rule,
            **names,
            'category': q['category'],
            'notes': pick(q['notes'], cfg),
        })
    return out


if __name__ == '__main__':
    assert len(G) == 40 and len({q['id'] for q in G}) == 40
    for cfg in ('en', 'ru'):
        head = ('# Shop goldens, seed v1, %s configuration: manager questions with reference SQL on schema shop.\n'
                '# Each choice a reference makes (which orders, which date, which window, how many rows, which columns) is\n'
                '# said in its question or in the shop context (v1/erp/context/); every column is asked for by the question.\n'
                '# Written by _build/gen_shop.py: change the generator, never this file.\n'
                % ('English' if cfg == 'en' else 'Russian'))
        if cfg == 'ru':
            head += '# An empty question waits for a Russian writer; the SQL is final.\n'
        body = yaml.dump({'questions': build(cfg)}, allow_unicode=True, sort_keys=False, width=120)
        with open(OUT + 'shop.%s.yaml' % cfg, 'w', encoding='utf-8') as fh:
            fh.write(head + body)
    print('written')
