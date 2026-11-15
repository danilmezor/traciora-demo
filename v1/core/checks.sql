-- core/checks.sql: read-only proofs that the core database holds the people step's shops, staff and sign-ins.
-- Run on the tenant's core database: python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --dsn <core DSN>
--   --file v1/core/checks.sql. Every query returns one row: the statement's key and the value found.
-- A cast slot's person is found by the id seeder/ids.py gives it: uuid5 over 'seed:v1/<cfg>/person/<slot>' (pgcrypto's
-- sha1). A shop is found by its key, the location's config_key alias. Slots, ranks, shop keys and extensions are the
-- same in both configurations (cast.json conventions); names, zones and addresses come from the ledger in the want line.
-- A person is employed at T when their last day is unknown or after T's date: active, and signing in when they hold a rank.

SET default_transaction_read_only = on;

-- people.cast | each slot of cast.json and tenant/ladder.json has its person: active exactly when employed at T, as its status says (F4, the seasonal hire: as his season says, NULL here), linked to a shop employee, its rank on its login and that login signing in exactly when the person is active, its postings (home first) under the position roles-and-places names for its role; one position per role, no position shared by two roles; no person outside the cast, no seeded person removed | expected: no slot differs, every slot found, none outside, none removed
-- want: value is None and row['found'] == row['slots'] == 33 and row['roles'] is None and row['outside'] == 0 and row['removed'] == 0
WITH cast_(slot, active, rank, postings, role) AS (VALUES
    ('1', true, 'senior', '', 'founder'), ('2', true, 'admin', '', 'managing_owner'),
    ('3', true, 'middle', 'main', 'office_manager'), ('4', true, 'senior', 'main east', 'service_manager'),
    ('5', true, 'middle', 'main', 'lead_advisor'), ('6', true, 'junior', 'main east', 'service_advisor'),
    ('7', true, 'junior', 'main', 'service_advisor'), ('8', true, 'junior', 'main', 'shop_foreman'),
    ('9', true, 'junior', 'main east', 'parts_manager'), ('10', true, 'worker', 'main', 'diagnostic_technician'),
    ('11', true, 'worker', 'main', 'technician'), ('12', true, 'worker', 'main', 'technician'),
    ('13', true, 'worker', 'main', 'electrical_technician'), ('14', true, 'worker', 'main', 'apprentice_technician'),
    ('15', true, 'worker', 'main', 'lube_tyre_technician'), ('16', true, 'middle', 'east', 'lead_advisor'),
    ('17', true, 'junior', 'east', 'service_advisor'), ('18', true, 'worker', 'east', 'lead_technician'),
    ('19', true, 'worker', 'east', 'technician'), ('20', true, 'worker', 'east', 'technician'),
    ('21', true, 'worker', 'east main', 'technician'), ('22', true, 'senior', 'west', 'shop_manager'),
    ('23', true, 'junior', 'west', 'service_advisor'), ('24', true, 'junior', 'west', 'service_advisor'),
    ('25', true, 'worker', 'west', 'technician'), ('26', true, 'worker', 'west', 'technician'),
    ('27', true, 'worker', 'west', 'technician'), ('28', true, 'worker', 'west', 'technician'),
    ('29', true, 'junior', 'main east', 'service_advisor'), ('F1', false, 'junior', 'west', 'service_advisor'),
    ('F2', false, 'worker', 'main', 'technician'), ('F3', false, NULL, 'main', 'service_advisor'),
    ('F4', NULL, 'worker', 'main', 'seasonal_helper')),
roles(role, en, ru) AS (VALUES
    ('founder', 'Founder, Owner', 'Основатель, владелец'), ('managing_owner', 'Managing Owner', 'Директор, совладелец'),
    ('office_manager', 'Office Manager / Bookkeeper', 'Бухгалтер'), ('service_manager', 'Service Manager', 'Руководитель сервиса'),
    ('lead_advisor', 'Lead Service Advisor', 'Старший мастер-приёмщик'), ('service_advisor', 'Service Advisor', 'Мастер-приёмщик'),
    ('shop_foreman', 'Shop Foreman', 'Мастер цеха'), ('parts_manager', 'Parts Manager', 'Менеджер по запчастям'),
    ('technician', 'Automotive Technician', 'Автомеханик'), ('diagnostic_technician', 'Diagnostic Technician', 'Автомеханик-диагност'),
    ('electrical_technician', 'Electrical Technician', 'Автоэлектрик'), ('lead_technician', 'Lead Technician', 'Старший автомеханик'),
    ('apprentice_technician', 'Apprentice Technician', 'Ученик автомеханика'), ('lube_tyre_technician', 'Lube and Tire Technician', 'Шиномонтажник'),
    ('shop_manager', 'Shop Manager', 'Руководитель СТО'), ('seasonal_helper', 'Seasonal Shop Helper', 'Шиномонтажник (сезонный)')),
seeded AS (
    SELECT c.*, encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
    FROM cast_ c, LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/' || c.slot, 'UTF8'), 'sha1') AS h) d),
found AS (
    SELECT s.slot, p.id IS NOT NULL AS present,
           p.active = (p.ended_on IS NULL OR p.ended_on > (:'T')::timestamp::date) AND p.active = coalesce(s.active, p.active)
               AND p.attrs_public ->> 'employee_id' ~ '^[0-9]+$' AS person_ok,
           a.key IS NOT DISTINCT FROM s.rank AND l.active IS NOT DISTINCT FROM CASE WHEN s.rank IS NOT NULL THEN p.active END AS login_ok,
           coalesce((SELECT string_agg(k.value, ' ' ORDER BY pl.is_home DESC, k.value) FROM identity.person_location pl
                     JOIN core.location_alias k ON k.location_id = pl.location_id AND k.namespace = 'config_key' WHERE pl.person_id = p.id), '') = s.postings
               AND NOT EXISTS (SELECT 1 FROM identity.person_location pl JOIN core.position n ON n.id = pl.position_id JOIN roles r ON r.role = s.role
                               WHERE pl.person_id = p.id AND n.name <> CASE :'cfg' WHEN 'en' THEN r.en ELSE r.ru END) AS postings_ok
    FROM seeded s LEFT JOIN identity.person p ON p.id = s.id LEFT JOIN identity.login l ON l.person_id = s.id LEFT JOIN core.access_level a ON a.id = l.access_level_id),
held AS (SELECT DISTINCT s.role, pl.position_id FROM seeded s JOIN identity.person_location pl ON pl.person_id = s.id)
SELECT 'people.cast' AS key,
       string_agg(slot || ':' || concat_ws(',', CASE WHEN NOT present THEN 'absent' END, CASE WHEN NOT person_ok THEN 'person' END,
                                           CASE WHEN NOT login_ok THEN 'login' END, CASE WHEN NOT postings_ok THEN 'postings' END), ' ')
           FILTER (WHERE NOT (present AND person_ok AND login_ok AND postings_ok)) AS value,
       count(*) FILTER (WHERE present) AS found, count(*) AS slots,
       (SELECT string_agg(DISTINCT role, ' ') FROM (SELECT role FROM held GROUP BY role HAVING count(*) <> 1
                                                    UNION SELECT h.role FROM held h JOIN held o ON o.position_id = h.position_id AND o.role <> h.role) r) AS roles,
       (SELECT count(*) FROM identity.person WHERE id NOT IN (SELECT id FROM seeded)) AS outside,
       (SELECT count(*) FROM identity.person WHERE id IN (SELECT id FROM seeded) AND removed_at IS NOT NULL) AS removed
FROM found;

-- people.count | the seeded people (a person linked to a shop employee): active ones, the ones employed at T (last day unknown or after T's date), and former ones (inactive, ended by T) | expected 33, active exactly the employed, the rest former
-- want: value == 33 and row['active'] == row['employed'] and row['active'] + row['former'] == value
SELECT 'people.count' AS key, count(*) AS value, count(*) FILTER (WHERE active) AS active,
       count(*) FILTER (WHERE ended_on IS NULL OR ended_on > (:'T')::timestamp::date) AS employed,
       count(*) FILTER (WHERE NOT active AND ended_on <= (:'T')::timestamp::date) AS former
FROM identity.person WHERE attrs_public ->> 'employee_id' IS NOT NULL;

-- people.signins | the seeded people's live sign-ins, the seeded people employed at T who hold a rank (F3 holds none), and any live sign-in of a former person | expected the live sign-ins equal the employed with a login, none of a former person
-- want: value == row['employed'] and row['former_signing_in'] == 0
SELECT 'people.signins' AS key, count(*) FILTER (WHERE l.active AND p.active) AS value,
       count(*) FILTER (WHERE p.ended_on IS NULL OR p.ended_on > (:'T')::timestamp::date) AS employed,
       count(*) FILTER (WHERE l.active AND NOT p.active) AS former_signing_in
FROM identity.login l JOIN identity.person p ON p.id = l.person_id WHERE p.attrs_public ->> 'employee_id' IS NOT NULL;

-- people.link | each seeded person names a shop employee, no two the same | expected 33 distinct employees
-- want: value == row['people'] == 33
SELECT 'people.link' AS key, count(DISTINCT attrs_public ->> 'employee_id') AS value, count(*) AS people
FROM identity.person WHERE attrs_public ->> 'employee_id' IS NOT NULL;

-- people.dates | the planted days: slot 7 and slot 14 start on their anchors, the people who came with west (22, 23, 25, 26, 27, F1) on the purchase day, F1, F2 and F3 end on theirs | expected the anchors
-- want: same(value, str(a['slot7_starts'])) and same(row['s14'], str(a['slot14_starts'])) and same(row['west'], str(a['bought'])) and same(row['f1'], str(a['fired'])) and same(row['f2'], str(a['f2_fired'])) and same(row['f3'], str(a['f3_resigns']))
WITH seeded AS (
    SELECT s.slot, encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
    FROM unnest(ARRAY['7', '14', '22', '23', '25', '26', '27', 'F1', 'F2', 'F3']) s(slot),
         LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/' || s.slot, 'UTF8'), 'sha1') AS h) d),
dated AS (SELECT s.slot, p.started_on::text AS started, p.ended_on::text AS ended FROM seeded s JOIN identity.person p ON p.id = s.id)
SELECT 'people.dates' AS key, (SELECT started FROM dated WHERE slot = '7') AS value, (SELECT started FROM dated WHERE slot = '14') AS s14,
       (SELECT string_agg(DISTINCT started, ', ') FROM dated WHERE slot IN ('22', '23', '25', '26', '27', 'F1')) AS west,
       (SELECT ended FROM dated WHERE slot = 'F1') AS f1, (SELECT ended FROM dated WHERE slot = 'F2') AS f2, (SELECT ended FROM dated WHERE slot = 'F3') AS f3;

-- places.keys | the shops' keys, each on one location (config_key aliases) | expected main, east, west
-- want: value == 'east main west' and row['locations'] == 3
SELECT 'places.keys' AS key, string_agg(value, ' ' ORDER BY value) AS value, count(DISTINCT location_id) AS locations FROM core.location_alias WHERE namespace = 'config_key';

-- places.main | the shop main: name, zone, address, check-in point and radius as the ledger has them (geo.*), and its extensions (roles-and-places: the group line and the desks)
-- want: same(value, V('geo.short_name')['main']) and same(row['tz'], V('geo.home_zone')) and same(row['address'], V('geo.address.main').rsplit(' (', 1)[0]) and all(near(row[k], v, abs=0.000001) for k, v in zip(('lat', 'lon'), V('geo.address.main').rsplit('(', 1)[1].rstrip(')').split(', '))) and same(row['radius'], V('geo.checkin_radius_m')) and same(row['extensions'], '100 101 102 103 104 105 111 112')
SELECT 'places.main' AS key, l.name AS value, l.tz, l.address_raw AS address, l.latitude AS lat, l.longitude AS lon, l.checkin_radius_m AS radius,
       (SELECT string_agg(e.value, ' ' ORDER BY e.value) FROM core.location_alias e WHERE e.location_id = l.id AND e.namespace = 'pbx_extension') AS extensions
FROM core.location l JOIN core.location_alias k ON k.location_id = l.id AND k.namespace = 'config_key' AND k.value = 'main';

-- places.east | the shop east: name, zone, address, check-in point and radius as the ledger has them (geo.*), and its extensions (roles-and-places: the group line and the desks)
-- want: same(value, V('geo.short_name')['east']) and same(row['tz'], V('geo.home_zone')) and same(row['address'], V('geo.address.east').rsplit(' (', 1)[0]) and all(near(row[k], v, abs=0.000001) for k, v in zip(('lat', 'lon'), V('geo.address.east').rsplit('(', 1)[1].rstrip(')').split(', '))) and same(row['radius'], V('geo.checkin_radius_m')) and same(row['extensions'], '200 201 202')
SELECT 'places.east' AS key, l.name AS value, l.tz, l.address_raw AS address, l.latitude AS lat, l.longitude AS lon, l.checkin_radius_m AS radius,
       (SELECT string_agg(e.value, ' ' ORDER BY e.value) FROM core.location_alias e WHERE e.location_id = l.id AND e.namespace = 'pbx_extension') AS extensions
FROM core.location l JOIN core.location_alias k ON k.location_id = l.id AND k.namespace = 'config_key' AND k.value = 'east';

-- places.west | the shop west: name, zone, address, check-in point and radius as the ledger has them (geo.*), and its extensions (roles-and-places: the group line, the desks and F1's retired 304)
-- want: same(value, V('geo.short_name')['west']) and same(row['tz'], V('geo.other_zone')) and same(row['address'], V('geo.address.west').rsplit(' (', 1)[0]) and all(near(row[k], v, abs=0.000001) for k, v in zip(('lat', 'lon'), V('geo.address.west').rsplit('(', 1)[1].rstrip(')').split(', '))) and same(row['radius'], V('geo.checkin_radius_m')) and same(row['extensions'], '300 301 302 303 304')
SELECT 'places.west' AS key, l.name AS value, l.tz, l.address_raw AS address, l.latitude AS lat, l.longitude AS lon, l.checkin_radius_m AS radius,
       (SELECT string_agg(e.value, ' ' ORDER BY e.value) FROM core.location_alias e WHERE e.location_id = l.id AND e.namespace = 'pbx_extension') AS extensions
FROM core.location l JOIN core.location_alias k ON k.location_id = l.id AND k.namespace = 'config_key' AND k.value = 'west';

-- places.weeks | each shop's regular week, day by day, as roles-and-places.<cfg>.json gives it (copied here for both configurations) | expected: no shop differs, three shops
-- want: value is None and row['shops'] == 3
WITH weeks(cfg, shop, week) AS (VALUES
    ('en', 'main', '{"mon": [["07:30", "17:30"]], "tue": [["07:30", "17:30"]], "wed": [["07:30", "17:30"]], "thu": [["07:30", "17:30"]], "fri": [["07:30", "17:30"]], "sat": [["08:00", "13:00"]], "sun": []}'::jsonb),
    ('en', 'east', '{"mon": [["07:30", "17:30"]], "tue": [["07:30", "17:30"]], "wed": [["07:30", "17:30"]], "thu": [["07:30", "17:30"]], "fri": [["07:30", "17:30"]], "sat": [], "sun": []}'::jsonb),
    ('en', 'west', '{"mon": [["07:30", "17:30"]], "tue": [["07:30", "17:30"]], "wed": [["07:30", "17:30"]], "thu": [["07:30", "17:30"]], "fri": [["07:30", "17:30"]], "sat": [], "sun": []}'::jsonb),
    ('ru', 'main', '{"mon": [["09:00", "20:00"]], "tue": [["09:00", "20:00"]], "wed": [["09:00", "20:00"]], "thu": [["09:00", "20:00"]], "fri": [["09:00", "20:00"]], "sat": [["09:00", "20:00"]], "sun": [["09:00", "20:00"]]}'::jsonb),
    ('ru', 'east', '{"mon": [["09:00", "20:00"]], "tue": [["09:00", "20:00"]], "wed": [["09:00", "20:00"]], "thu": [["09:00", "20:00"]], "fri": [["09:00", "20:00"]], "sat": [["09:00", "20:00"]], "sun": [["09:00", "20:00"]]}'::jsonb),
    ('ru', 'west', '{"mon": [["09:00", "20:00"]], "tue": [["09:00", "20:00"]], "wed": [["09:00", "20:00"]], "thu": [["09:00", "20:00"]], "fri": [["09:00", "20:00"]], "sat": [["09:00", "20:00"]], "sun": [["09:00", "20:00"]]}'::jsonb))
SELECT 'places.weeks' AS key, string_agg(w.shop, ' ' ORDER BY w.shop) FILTER (WHERE l.business_hours IS DISTINCT FROM w.week) AS value, count(l.id) AS shops
FROM weeks w LEFT JOIN core.location_alias k ON k.namespace = 'config_key' AND k.value = w.shop LEFT JOIN core.location l ON l.id = k.location_id
WHERE w.cfg = :'cfg';

-- places.dated | each shop's dated hours: a closed row with a reason on every closed date from T's date to 60 days on (ledger site.closed_dates: en the six holidays, observed on the Friday before a Saturday and the Monday after a Sunday; ru 1 and 2 January), no other closed row in that window, and the stocktake (ledger site.stocktake): open at the weekday's opening, closing at its closes_at | expected: no shop differs; the stocktake rows of the three shops on the anchor
-- want: value is None and same(row['stocktake'], f"{a['stocktake']} {V('site.hours.weekday')[0]}-{V('site.stocktake')['closes_at'].split()[0]}") and row['stocktakes'] == 3 and row['unreasoned'] == 0
WITH days AS (
    SELECT d::date AS d, extract(year FROM d)::int AS y FROM generate_series((:'T')::timestamp::date, (:'T')::timestamp::date + 60, interval '1 day') d),
shut AS (
    SELECT d FROM days WHERE CASE :'cfg' WHEN 'ru' THEN to_char(d, 'MM-DD') IN ('01-01', '01-02') ELSE
        d IN (SELECT CASE extract(isodow FROM f) WHEN 6 THEN f - 1 WHEN 7 THEN f + 1 ELSE f END
              FROM unnest(ARRAY[make_date(y, 1, 1), make_date(y, 7, 4), make_date(y, 12, 25), make_date(y + 1, 1, 1)]) f)
        OR (extract(month FROM d) = 5 AND extract(isodow FROM d) = 1 AND extract(day FROM d) >= 25)
        OR (extract(month FROM d) = 9 AND extract(isodow FROM d) = 1 AND extract(day FROM d) <= 7)
        OR (extract(month FROM d) = 11 AND extract(isodow FROM d) = 4 AND extract(day FROM d) BETWEEN 22 AND 28) END),
shops AS (SELECT k.value AS shop, k.location_id FROM core.location_alias k WHERE k.namespace = 'config_key')
SELECT 'places.dated' AS key,
       (SELECT string_agg(shop, ' ' ORDER BY shop) FROM shops s WHERE
            (SELECT coalesce(string_agg(d::text, ' ' ORDER BY d), '') FROM shut) IS DISTINCT FROM
            (SELECT coalesce(string_agg(e.on_date::text, ' ' ORDER BY e.on_date), '') FROM core.location_hours_exception e
             WHERE e.location_id = s.location_id AND e.kind = 'closed' AND e.on_date BETWEEN (:'T')::timestamp::date AND (:'T')::timestamp::date + 60)) AS value,
       (SELECT string_agg(DISTINCT e.on_date || ' ' || to_char(e.open_local, 'HH24:MI') || '-' || to_char(e.close_local, 'HH24:MI'), ', ')
        FROM core.location_hours_exception e JOIN shops s ON s.location_id = e.location_id WHERE e.kind = 'hours') AS stocktake,
       (SELECT count(*) FROM core.location_hours_exception e JOIN shops s ON s.location_id = e.location_id WHERE e.kind = 'hours') AS stocktakes,
       (SELECT count(*) FROM core.location_hours_exception e JOIN shops s ON s.location_id = e.location_id WHERE e.reason IS NULL) AS unreasoned;

-- people.postings | the seeded people with a posting: each with exactly one home posting, starting on the person's started_on; a former person with no posting open at T | expected 0 and 0, of 31 posted people (slots 1 and 2 have none)
-- want: value == 0 and row['former_open'] == 0 and row['posted'] == 31
SELECT 'people.postings' AS key, count(*) FILTER (WHERE homes <> 1 OR home_from IS DISTINCT FROM started_on) AS value,
       count(*) FILTER (WHERE NOT active AND open_postings > 0) AS former_open, count(*) AS posted
FROM (SELECT p.active, p.started_on, count(*) FILTER (WHERE pl.is_home) AS homes, min(pl.valid_from) FILTER (WHERE pl.is_home) AS home_from,
             count(*) FILTER (WHERE pl.valid_to IS NULL OR pl.valid_to > (:'T')::timestamp::date) AS open_postings
      FROM identity.person p JOIN identity.person_location pl ON pl.person_id = p.id
      WHERE p.attrs_public ->> 'employee_id' IS NOT NULL GROUP BY p.id) x;
