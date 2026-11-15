-- workday/checks.sql: read-only proofs that the core database holds the workday step's cards, calendar, roster weeks,
-- open requests and the two operators' Inbox (workday/DESIGN.md). Run on the tenant's core database:
--   python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --dsn <core DSN> --file v1/workday/checks.sql
-- What depends on the build day (which cards exist and their trails, the board, the Inbox, the clock-ins, the
-- stocktake, the cover, the deadlines) is proved by v1/workday/checks.py against the plan for the T in force.
-- A seeded row is found by the id seeder/ids.py gives it: uuid5 over 'seed:v1/<cfg>/<kind>/<key>' (pgcrypto's sha1);
-- a card by its id in cards.json, a person by their cast slot, a shift by '<slot>:W<+k>.<day>'. A shop is found by its
-- key, the location's config_key alias. The card file's ids, states, owners and shops are the same in both
-- configurations; nothing here is a word of either language.

SET default_transaction_read_only = on;

-- workday.cards.absent | H-east-waiting is not in the core: it rests on a chat of the bank, which this plan leaves out, and no seed file names its visitor; every other card and its trail are proved per build by v1/workday/checks.py | expected 0
-- want: value == 0
SELECT 'workday.cards.absent' AS key, count(*) AS value FROM work.work_item
WHERE id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/card/H-east-waiting', 'UTF8'), 'sha1') h);

-- workday.handovers | the assistant's hand-over cards (S07's two): origin model, raised on a customer.handover_requested event they name as their trigger, whose session is the chat in their origin_ref, under the tenant's hand-over template | expected 2
-- want: value == 2
SELECT 'workday.handovers' AS key, count(*) AS value
FROM work.work_item wi
JOIN work.work_item_source s ON s.work_item_id = wi.id AND s.role = 'trigger'
JOIN platform.event e ON e.id = s.event_id AND e.type = 'customer.handover_requested'
JOIN work.work_item_template t ON t.id = wi.work_item_template_id
WHERE wi.origin = 'model' AND wi.origin_ref = 'chat:' || (e.payload_public ->> 'session_id') AND e.subject_id = wi.id;

-- workday.quiet | the two quiet cards (Q-04-rack, Q-22-regulars): open, nothing on their timeline for seven days before T, and one board.quiet line pushed to their owner after their newest line, still unread | expected 2
-- want: value == 2
WITH card(key) AS (VALUES ('Q-04-rack'), ('Q-22-regulars')),
ids AS (
    SELECT (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/card/' || c.key, 'UTF8'), 'sha1') h) AS id
    FROM card c)
SELECT 'workday.quiet' AS key, count(*) AS value
FROM ids i JOIN work.work_item wi ON wi.id = i.id JOIN work.work_state ws ON ws.id = wi.state_id
CROSS JOIN LATERAL (SELECT max(occurred_at) AS last FROM platform.activity WHERE subject_type = 'work_item' AND subject_id = wi.id) a
WHERE ws.state_group NOT IN ('completed', 'cancelled')
  AND a.last < (:'T')::timestamp AT TIME ZONE (SELECT tz FROM core.location l JOIN core.location_alias k ON k.location_id = l.id AND k.namespace = 'config_key' AND k.value = 'main') - interval '7 days'
  AND EXISTS (SELECT 1 FROM platform.notification_queue q JOIN platform.notification_type nt ON nt.id = q.notification_type_id
              WHERE nt.type = 'board.quiet' AND q.person_id = wi.owner_id AND q.context_public ->> 'task_id' = wi.id::text
                AND q.send_at > a.last AND q.read_at IS NULL);

-- workday.series | the series rows (en: the managers' meeting, three weekly call reviews, three huddles; ru: the meeting and the huddles, the call reviews being single entries): every occurrence stands on a day its rule names (moved ones by their occurrence key), one per rule day from its first day to its last, the last within two weeks after T | expected: no series differs; 7 en, 4 ru
-- want: value is None and row['series'] == (7 if cfg == 'en' else 4)
WITH s AS (
    SELECT es.id, es.starts_on, es.materialised_through, string_to_array(substring(es.rrule FROM 'BYDAY=([A-Z,]+)'), ',') AS days
    FROM work.event_series es WHERE EXISTS (SELECT 1 FROM work.calendar_event ce WHERE ce.series_id = es.id)),
got AS (
    SELECT s.id, count(*) AS n, bool_and(substring(to_char(ce.occurrence_key::timestamp, 'DY') FROM 1 FOR 2) = ANY(s.days)) AS on_rule,
           max(ce.occurrence_key::timestamp)::date AS last, min(ce.occurrence_key::timestamp)::date AS first
    FROM s JOIN work.calendar_event ce ON ce.series_id = s.id GROUP BY s.id),
want_ AS (
    SELECT s.id, count(*) AS n FROM s, generate_series(s.starts_on, s.materialised_through, interval '1 day') d
    WHERE substring(to_char(d, 'DY') FROM 1 FOR 2) = ANY(s.days) GROUP BY s.id)
SELECT 'workday.series' AS key,
       string_agg(g.id::text, ' ') FILTER (WHERE g.n <> w.n OR NOT g.on_rule OR g.last <> s.materialised_through OR g.first <> s.starts_on
                                          OR g.last > (:'T')::timestamp::date + 14 OR g.last < (:'T')::timestamp::date + 7) AS value,
       count(*) AS series
FROM got g JOIN want_ w ON w.id = g.id JOIN s ON s.id = g.id;

-- workday.s09 | the managers' meeting (S09-managers-meeting): its cancelled occurrences (en the closed Mondays and the one called off, ru the one called off), the one moved to 10:00, slot 22's answers on the held regular ones in the order of ledger s9.pattern, and on the two future ones: slots 4, 3, 5, 16 answered, slot 22 not | expected as the want computes
-- want: value == len([m for m in a['closed_mondays'] if m >= a['s9_first']]) + 1 and row['moved'] == 1 and row['future_answered'] == 8 and row['future_22'] == 0 and [V('s9.pattern')['slot_22_on_regular_occurrences_in_order'][i % len(V('s9.pattern')['slot_22_on_regular_occurrences_in_order'])].split(',')[0] for i in range(row['regular'])].count('declined') == row['declined_22'] and row['regular'] > 0
WITH ids AS (
    SELECT (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/series/S09-managers-meeting', 'UTF8'), 'sha1') h) AS series,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/22', 'UTF8'), 'sha1') h) AS p22),
occ AS (
    SELECT ce.*, ce.occurrence_key::timestamp::date AS day, ex.action
    FROM ids JOIN work.calendar_event ce ON ce.series_id = ids.series
    LEFT JOIN work.event_series_exception ex ON ex.series_id = ce.series_id AND ex.occurrence_key = ce.occurrence_key)
SELECT 'workday.s09' AS key,
       count(*) FILTER (WHERE cancelled_at IS NOT NULL AND action = 'cancel') AS value,
       count(*) FILTER (WHERE action = 'replace' AND start_local::time = '10:00') AS moved,
       count(*) FILTER (WHERE action IS NULL AND day < (:'T')::timestamp::date) AS regular,
       (SELECT count(*) FROM occ o JOIN work.calendar_event_participant p ON p.event_id = o.id, ids
        WHERE o.action IS NULL AND o.day < (:'T')::timestamp::date AND p.person_id = ids.p22 AND p.response = 'declined') AS declined_22,
       (SELECT count(*) FROM occ o JOIN work.calendar_event_participant p ON p.event_id = o.id, ids
        WHERE o.day > (:'T')::timestamp::date AND p.person_id <> ids.p22 AND p.response <> 'invited') AS future_answered,
       (SELECT count(*) FROM occ o JOIN work.calendar_event_participant p ON p.event_id = o.id, ids
        WHERE o.day > (:'T')::timestamp::date AND p.person_id = ids.p22 AND p.response <> 'invited') AS future_22
FROM occ;

-- workday.entries | the single entries of calendar.json (21 en, 15 ru): each present with its kind, organiser, all-day flag and show-as; the junior's block on the review card; every invitee of the review meeting and of the stocktake accepted | expected: no entry differs
-- want: value is None and row['found'] == (21 if cfg == 'en' else 15)
WITH entry(key, kind, organiser, all_day, show_as) AS (VALUES
    ('S16-meeting', 'meeting', '4', false, 'busy'), ('S16-block', 'block', '6', false, 'busy'),
    ('S05-leave-10', 'personal', '10', true, 'out_of_office'), ('S05-week-off-16', 'personal', '16', true, 'out_of_office'),
    ('S13-stocktake', 'meeting', '9', false, 'busy'), ('TRN-hybrid-10', 'personal', '10', true, 'out_of_office'),
    ('TRN-lifts', 'meeting', '8', false, 'busy'), ('SUP-home-supplier', 'meeting', '9', false, 'busy'),
    ('SUP-tyres', 'meeting', '9', false, 'busy'), ('INT-tech-1', 'meeting', '4', false, 'busy'), ('INT-tech-2', 'meeting', '4', false, 'busy'),
    ('INT-tech-3', 'meeting', '4', false, 'busy'), ('INT-adv-1', 'meeting', '4', false, 'busy'), ('INT-adv-2', 'meeting', '4', false, 'busy'),
    ('INT-adv-3', 'meeting', '4', false, 'busy'), ('S05-day-off-16-1', 'personal', '16', true, 'out_of_office'),
    ('S05-day-off-16-2', 'personal', '16', true, 'out_of_office'), ('S05-day-off-16-3', 'personal', '16', true, 'out_of_office'),
    ('S05-day-off-16-4', 'personal', '16', true, 'out_of_office'), ('S05-day-off-16-5', 'personal', '16', true, 'out_of_office'),
    ('S05-day-off-16-6', 'personal', '16', true, 'out_of_office')),
ids AS (
    SELECT e.*, (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
                 FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/calendar/' || e.key, 'UTF8'), 'sha1') h) AS id,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/' || e.organiser, 'UTF8'), 'sha1') h) AS organiser_id,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/card/S16-review', 'UTF8'), 'sha1') h) AS review
    FROM entry e),
found AS (
    SELECT i.key, ce.id IS NOT NULL AS present,
           ce.kind = i.kind AND ce.organiser_id = i.organiser_id AND ce.all_day = i.all_day AND ce.show_as = i.show_as
               AND (i.key <> 'S16-block' OR ce.work_item_id = i.review)
               AND (i.key NOT IN ('S16-meeting', 'S13-stocktake') OR NOT EXISTS (
                   SELECT 1 FROM work.calendar_event_participant p WHERE p.event_id = ce.id AND p.response <> 'accepted')) AS ok
    FROM ids i LEFT JOIN work.calendar_event ce ON ce.id = i.id)
SELECT 'workday.entries' AS key,
       string_agg(key || ':' || CASE WHEN NOT present THEN 'absent' ELSE 'differs' END, ' ' ORDER BY key)
           FILTER (WHERE present AND NOT ok OR NOT present AND (:'cfg' = 'en' OR key NOT LIKE 'S05-day-off-16-%')) AS value,
       count(*) FILTER (WHERE present) AS found
FROM found;

-- workday.coach | the call reviews (COACH-6, COACH-7, COACH-17, COACH-29): organised by slot 4 with its one invitee, who accepted every occurrence, never two in one week | expected: none differs, all four with entries
-- want: value is None and row['reviews'] == 4
WITH coach(key, slot) AS (VALUES ('COACH-6', '6'), ('COACH-7', '7'), ('COACH-17', '17'), ('COACH-29', '29')),
keyed AS (
    SELECT c.key, c.slot, x.n FROM coach c, (SELECT n::text FROM generate_series(0, 199) n) x
    UNION ALL SELECT c.key, c.slot, NULL FROM coach c),
ids AS (
    SELECT k.key, k.slot, k.n,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || CASE WHEN k.n IS NULL THEN '/series/' || k.key ELSE '/calendar/' || k.key || ':' || k.n END, 'UTF8'), 'sha1') h) AS id,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/' || k.slot, 'UTF8'), 'sha1') h) AS invitee,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/4', 'UTF8'), 'sha1') h) AS organiser
    FROM keyed k),
held AS (
    SELECT i.key, ce.id, ce.organiser_id = i.organiser AS by4, date_trunc('week', ce.start_local) AS week,
           (SELECT array_agg(p.person_id::text || ':' || p.response) FROM work.calendar_event_participant p WHERE p.event_id = ce.id) = ARRAY[i.invitee::text || ':accepted'] AS answered
    FROM ids i JOIN work.calendar_event ce ON (i.n IS NULL AND ce.series_id = i.id) OR (i.n IS NOT NULL AND ce.id = i.id))
SELECT 'workday.coach' AS key,
       string_agg(DISTINCT key, ' ') FILTER (WHERE NOT by4 OR NOT answered OR key IN (SELECT key FROM held GROUP BY key, week HAVING count(*) > 1)) AS value,
       count(DISTINCT key) AS reviews
FROM held;

-- workday.roster.weeks | the shifts from the Monday of T's week to T+14 days, by shop and week: published exactly in the published weeks (home shops up to the week of the last Thursday publish, west only the current week), each published shift under a publish that covers its day, made before T, no draft under one | expected: no shop-week differs, and shifts at all three shops
-- want: value is None and row['sites'] == 3 and row['shifts'] > 0
WITH w0 AS (SELECT date_trunc('week', (:'T')::timestamp)::date AS monday),
s AS (
    SELECT k.value AS site, (sh.business_day - w0.monday) / 7 AS week, sh.status, sh.business_day, rp.range_start, rp.range_end, rp.published_at
    FROM workforce.shift sh CROSS JOIN w0
    JOIN core.location_alias k ON k.location_id = sh.location_id AND k.namespace = 'config_key'
    LEFT JOIN workforce.roster_publish rp ON rp.id = sh.roster_publish_id
    WHERE sh.deleted_at IS NULL AND sh.business_day BETWEEN w0.monday AND (:'T')::timestamp::date + 14),
judged AS (
    SELECT site, week, bool_and(CASE WHEN (site = 'west' AND week = 0) OR (site <> 'west' AND week <= ((:'pub_week')::date - (SELECT monday FROM w0)) / 7)
                                     THEN status IN ('published', 'cancelled') AND business_day BETWEEN range_start AND range_end
                                          AND published_at <= (:'T')::timestamp AT TIME ZONE (SELECT tz FROM core.location l JOIN core.location_alias k ON k.location_id = l.id AND k.namespace = 'config_key' AND k.value = 'main')
                                     ELSE status = 'draft' AND range_start IS NULL END) AS ok, count(*) AS n
    FROM s GROUP BY site, week)
SELECT 'workday.roster.weeks' AS key, string_agg(site || ':W+' || week, ' ' ORDER BY site, week) FILTER (WHERE NOT ok) AS value,
       count(DISTINCT site) AS sites, sum(n) AS shifts
FROM judged;

-- workday.roster.open | the one shift with nobody on it between T and T+14 days: at main, on the Tuesday of week W+1, published when that week is | expected 1, on that day
-- want: value == 1 and row['day'] == str(a['W0'] + timedelta(8)) and row['status'] == ('published' if a['pub_week'] > a['W0'] else 'draft')
SELECT 'workday.roster.open' AS key, count(*) AS value, min(sh.business_day)::text AS day, min(sh.status) AS status
FROM workforce.shift sh JOIN core.location_alias k ON k.location_id = sh.location_id AND k.namespace = 'config_key' AND k.value = 'main'
WHERE sh.person_id IS NULL AND sh.deleted_at IS NULL AND sh.business_day BETWEEN (:'T')::timestamp::date AND (:'T')::timestamp::date + 14;

-- workday.roster.week_off | slot 16's week off: unavailable on its seven dates; inside it her published shifts stand (two), each with her open request to come off it, and no draft shift of hers | expected 7 dates from the week off's first day, 2 published shifts with open requests, no draft
-- want: value == 7 and row['first'] == str(a['week_off']) and row['published'] == 2 and row['asked'] == 2 and row['drafts'] == 0
WITH p AS (
    SELECT (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/16', 'UTF8'), 'sha1') h) AS id),
away AS (SELECT a.on_date FROM workforce.availability a, p WHERE a.person_id = p.id AND a.kind = 'unavailable' AND a.on_date IS NOT NULL)
SELECT 'workday.roster.week_off' AS key, (SELECT count(*) FROM away) AS value, (SELECT min(on_date)::text FROM away) AS first,
       count(*) FILTER (WHERE sh.status = 'published') AS published,
       count(*) FILTER (WHERE sh.status = 'published' AND EXISTS (
           SELECT 1 FROM workforce.shift_change_request r WHERE r.shift_id = sh.id AND r.person_id = p.id AND r.status = 'open' AND r.kind = 'remove')) AS asked,
       count(*) FILTER (WHERE sh.status = 'draft') AS drafts
FROM workforce.shift sh, p
WHERE sh.person_id = p.id AND sh.deleted_at IS NULL AND sh.business_day IN (SELECT on_date FROM away);

-- workday.requests | the open shift requests in the core: R50 and R51, slot 16's, to come off a published shift, filed before the shift's day, each told to the planners by one change_requested line in her name | expected 2
-- want: value == 2 and row['told'] == 2
WITH p AS (
    SELECT (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/16', 'UTF8'), 'sha1') h) AS id)
SELECT 'workday.requests' AS key, count(*) FILTER (WHERE r.person_id = p.id AND r.kind = 'remove' AND sh.status = 'published' AND r.filed_at::date < sh.business_day) AS value,
       count(*) FILTER (WHERE EXISTS (SELECT 1 FROM platform.activity a JOIN identity.login l ON l.actor_id = a.actor_id AND l.person_id = p.id
                                      WHERE a.verb = 'change_requested' AND a.payload_public ->> 'request_id' = r.id::text)) AS told
FROM workforce.shift_change_request r JOIN workforce.shift sh ON sh.id = r.shift_id, p
WHERE r.status = 'open';