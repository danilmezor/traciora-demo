-- calls/checks.sql: read-only proofs that the core database holds the calls step's story calls (calls/DESIGN.md section 1).
-- Run on the tenant's core database: python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --dsn <core DSN>
--   --file v1/calls/checks.sql. Every query returns one row: the statement's key and the value found.
-- The step's rows are those of the call log provider 'seed:pbx'. An answered call is found by its transcript, whose id
-- seeder/ids.py gives: uuid5 over 'seed:v1/<cfg>/call-transcript/<number>' (pgcrypto's sha1); a person by
-- 'seed:v1/<cfg>/person/<slot>'. Slots, desks and shops are the same in both configurations; scores are each file's.

SET default_transaction_read_only = on;

-- calls.handler | each answered story call (every file with a transcript) names the file's advisor slot: the call's person, attributed by the extension as its one person (pbx_extension, tier 5), and its one handler from the answer | expected: no call differs
-- want: value is None and row['calls'] == 33
WITH story(n, slot) AS (VALUES
    (1, '6'), (2, '6'), (3, '6'), (4, '6'), (5, '6'), (6, '6'), (7, '6'), (8, '6'), (9, '7'), (10, '5'), (11, '4'), (12, '7'),
    (13, '7'), (14, '7'), (15, '23'), (16, '23'), (17, '22'), (21, '5'), (22, '7'), (23, '6'), (24, '6'), (25, '16'),
    (26, '16'), (27, '16'), (28, '17'), (29, '5'), (30, '6'), (31, '5'), (32, '6'), (33, '22'), (34, '22'), (35, '24'),
    (36, '24')),
seeded AS (
    SELECT s.n, (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
                 FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || s.n, 'UTF8'), 'sha1') h) AS transcript,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
                 FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/' || s.slot, 'UTF8'), 'sha1') h) AS person
    FROM story s)
SELECT 'calls.handler' AS key,
       string_agg(s.n::text, ' ' ORDER BY s.n) FILTER (WHERE i.person_id IS DISTINCT FROM s.person
           OR i.attributed_by IS DISTINCT FROM 'pbx_extension' OR i.person_confidence_tier IS DISTINCT FROM 5
           OR (SELECT array_agg(p.person_id) FROM interactions.interaction_participant p WHERE p.interaction_id = i.id AND p.role = 'handler' AND p.from_at = i.answered_at) IS DISTINCT FROM ARRAY[s.person]) AS value,
       count(i.id) AS calls
FROM seeded s LEFT JOIN interactions.transcript t ON t.id = s.transcript LEFT JOIN interactions.interaction i ON i.id = t.interaction_id;

-- calls.clock | each call starts at its file's local start on its shop's clock (the morning miss before call 16 at the hour its note names), on the day the clock gives the call | expected: no hour differs, every day the clock's
-- want: row['wrong_time'] is None and row['calls'] == 37 and each(value, [f"{x}={a['calls'][int(x.rstrip('m'))]['day']}" for n in range(1, 37) for x in ([str(n), '16m'] if n == 16 else [str(n)])], sep=' ')
WITH story(n, en, en_ring, en_talk, ru, ru_ring, ru_talk) AS (VALUES
    ('1', '10:42', 9, 138, '11:20', 7, 147), ('2', '13:20', 7, 141, '14:05', 6, 121),
    ('3', '11:05', 5, 83, '17:40', 9, 95), ('4', '15:10', 8, 124, '12:15', 5, 130),
    ('5', '09:35', 4, 146, '13:30', 4, 115), ('6', '14:15', 6, 196, '15:40', 5, 158),
    ('7', '13:50', 5, 122, '15:10', 5, 113), ('8', '07:52', 12, 95, '14:20', 11, 105),
    ('9', '10:25', 31, 89, '12:35', 14, 99), ('10', '14:35', 6, 180, '15:40', 8, 215),
    ('11', '09:10', 9, 125, '10:15', 6, 153), ('12', '11:40', 14, 72, '16:25', 12, 91),
    ('13', '16:20', 17, 117, '10:40', 16, 72), ('14', '15:50', 6, 82, '10:20', 9, 91),
    ('15', '15:40', 21, 120, '16:10', 24, 113), ('16', '14:20', 24, 75, '15:25', 27, 95),
    ('16m', '09:12', 35, 0, '10:05', 35, 0), ('17', '10:40', 11, 181, '11:10', 19, 142),
    ('18', '08:05', 35, 0, '09:40', 35, 0), ('19', '13:40', 35, 0, '14:15', 35, 0),
    ('20', '16:15', 35, 0, '17:30', 35, 0), ('21', '09:50', 5, 184, '10:50', 7, 182),
    ('22', '10:15', 18, 114, '11:20', 15, 140), ('23', '10:05', 6, 97, '16:10', 6, 71),
    ('24', '14:30', 4, 128, '09:50', 4, 92), ('25', '09:12', 4, 173, '09:12', 4, 170),
    ('26', '10:20', 4, 220, '11:30', 5, 198), ('27', '11:15', 3, 144, '12:10', 3, 155),
    ('28', '13:15', 9, 135, '14:45', 11, 109), ('29', '11:30', 7, 149, '17:50', 6, 148),
    ('30', '16:40', 5, 157, '11:50', 5, 126), ('31', '08:10', 27, 172, '09:40', 22, 129),
    ('32', '07:40', 3, 133, '09:10', 3, 128), ('33', '09:20', 13, 77, '13:20', 17, 76),
    ('34', '14:05', 16, 83, '16:40', 13, 61), ('35', '11:10', 4, 119, '10:35', 4, 129),
    ('36', '10:30', 3, 129, '12:05', 3, 106)),
answered AS (
    SELECT n::text AS n, t.interaction_id AS id FROM generate_series(1, 36) n
    JOIN interactions.transcript t ON t.id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
          FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || n, 'UTF8'), 'sha1') h)),
missed AS (
    SELECT i.id, i.started_at, m.resolved_by_interaction_id AS resolver FROM interactions.interaction i
    JOIN interactions.missed_call m ON m.interaction_id = i.id
    WHERE i.id IN (SELECT interaction_id FROM interactions.call_leg WHERE provider = 'seed:pbx')),
labelled AS (
    SELECT n, id FROM answered
    UNION ALL SELECT '16m', x.id FROM missed x JOIN answered a ON a.id = x.resolver AND a.n = '16'
    UNION ALL SELECT (17 + row_number() OVER (ORDER BY x.started_at))::text, x.id FROM missed x WHERE x.resolver IS NULL),
call AS (
    SELECT s.*, l.id, i.started_at, i.answered_at, i.duration_s, z.tz FROM story s LEFT JOIN labelled l ON l.n = s.n
    LEFT JOIN interactions.interaction i ON i.id = l.id LEFT JOIN core.location z ON z.id = i.location_id)
SELECT 'calls.clock' AS key, string_agg(n || '=' || (started_at AT TIME ZONE tz)::date, ' ' ORDER BY rtrim(n, 'm')::int, n) AS value,
       string_agg(n, ' ') FILTER (WHERE to_char(started_at AT TIME ZONE tz, 'HH24:MI') <> CASE WHEN :'cfg' = 'en' THEN en ELSE ru END) AS wrong_time,
       count(id) AS calls
FROM call;

-- calls.timing | each call rang as long as its file's ring_s (to the answer, or to the end of its last desk's ring when nobody answered) and talked its talk_s (none on a miss) | expected: no call differs
-- want: value is None and row['calls'] == 37
WITH story(n, en, en_ring, en_talk, ru, ru_ring, ru_talk) AS (VALUES
    ('1', '10:42', 9, 138, '11:20', 7, 147), ('2', '13:20', 7, 141, '14:05', 6, 121),
    ('3', '11:05', 5, 83, '17:40', 9, 95), ('4', '15:10', 8, 124, '12:15', 5, 130),
    ('5', '09:35', 4, 146, '13:30', 4, 115), ('6', '14:15', 6, 196, '15:40', 5, 158),
    ('7', '13:50', 5, 122, '15:10', 5, 113), ('8', '07:52', 12, 95, '14:20', 11, 105),
    ('9', '10:25', 31, 89, '12:35', 14, 99), ('10', '14:35', 6, 180, '15:40', 8, 215),
    ('11', '09:10', 9, 125, '10:15', 6, 153), ('12', '11:40', 14, 72, '16:25', 12, 91),
    ('13', '16:20', 17, 117, '10:40', 16, 72), ('14', '15:50', 6, 82, '10:20', 9, 91),
    ('15', '15:40', 21, 120, '16:10', 24, 113), ('16', '14:20', 24, 75, '15:25', 27, 95),
    ('16m', '09:12', 35, 0, '10:05', 35, 0), ('17', '10:40', 11, 181, '11:10', 19, 142),
    ('18', '08:05', 35, 0, '09:40', 35, 0), ('19', '13:40', 35, 0, '14:15', 35, 0),
    ('20', '16:15', 35, 0, '17:30', 35, 0), ('21', '09:50', 5, 184, '10:50', 7, 182),
    ('22', '10:15', 18, 114, '11:20', 15, 140), ('23', '10:05', 6, 97, '16:10', 6, 71),
    ('24', '14:30', 4, 128, '09:50', 4, 92), ('25', '09:12', 4, 173, '09:12', 4, 170),
    ('26', '10:20', 4, 220, '11:30', 5, 198), ('27', '11:15', 3, 144, '12:10', 3, 155),
    ('28', '13:15', 9, 135, '14:45', 11, 109), ('29', '11:30', 7, 149, '17:50', 6, 148),
    ('30', '16:40', 5, 157, '11:50', 5, 126), ('31', '08:10', 27, 172, '09:40', 22, 129),
    ('32', '07:40', 3, 133, '09:10', 3, 128), ('33', '09:20', 13, 77, '13:20', 17, 76),
    ('34', '14:05', 16, 83, '16:40', 13, 61), ('35', '11:10', 4, 119, '10:35', 4, 129),
    ('36', '10:30', 3, 129, '12:05', 3, 106)),
answered AS (
    SELECT n::text AS n, t.interaction_id AS id FROM generate_series(1, 36) n
    JOIN interactions.transcript t ON t.id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
          FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || n, 'UTF8'), 'sha1') h)),
missed AS (
    SELECT i.id, i.started_at, m.resolved_by_interaction_id AS resolver FROM interactions.interaction i
    JOIN interactions.missed_call m ON m.interaction_id = i.id
    WHERE i.id IN (SELECT interaction_id FROM interactions.call_leg WHERE provider = 'seed:pbx')),
labelled AS (
    SELECT n, id FROM answered
    UNION ALL SELECT '16m', x.id FROM missed x JOIN answered a ON a.id = x.resolver AND a.n = '16'
    UNION ALL SELECT (17 + row_number() OVER (ORDER BY x.started_at))::text, x.id FROM missed x WHERE x.resolver IS NULL),
call AS (
    SELECT s.*, l.id, i.started_at, i.answered_at, i.duration_s, z.tz FROM story s LEFT JOIN labelled l ON l.n = s.n
    LEFT JOIN interactions.interaction i ON i.id = l.id LEFT JOIN core.location z ON z.id = i.location_id)
SELECT 'calls.timing' AS key,
       string_agg(n, ' ' ORDER BY rtrim(n, 'm')::int, n) FILTER (WHERE coalesce(duration_s, 0) <> CASE WHEN :'cfg' = 'en' THEN en_talk ELSE ru_talk END
           OR (SELECT round(extract(epoch FROM coalesce(c.answered_at, max(l.started_at + make_interval(secs => l.ring_s))) - c.started_at))::int
               FROM interactions.call_leg l WHERE l.interaction_id = c.id) IS DISTINCT FROM CASE WHEN :'cfg' = 'en' THEN en_ring ELSE ru_ring END) AS value,
       count(id) AS calls
FROM call c;

-- calls.count | the provider's calls: every leg in a call, 37 calls (35 inbound, 2 outbound), 33 answered, 4 missed (A5's three and call 16's morning miss) with a missed_call row each and the disposition no_answer, 49 legs (one an answered call, four a miss) | expected as stated
-- want: value == 37 and row['inbound'] == 35 and row['answered'] == 33 and row['missed'] == 4 and row['legs'] == 49 and row['loose'] == 0
WITH legs AS (SELECT * FROM interactions.call_leg WHERE provider = 'seed:pbx'),
calls AS (SELECT * FROM interactions.interaction WHERE id IN (SELECT interaction_id FROM legs))
SELECT 'calls.count' AS key, (SELECT count(*) FROM calls) AS value,
       (SELECT count(*) FROM calls WHERE direction = 'inbound') AS inbound,
       (SELECT count(*) FROM calls WHERE answered_at IS NOT NULL AND disposition IS NULL) AS answered,
       (SELECT count(*) FROM calls c JOIN interactions.missed_call m ON m.interaction_id = c.id
        WHERE c.disposition = 'no_answer' AND c.answered_at IS NULL AND c.channel = 'call' AND c.state = 'closed') AS missed,
       (SELECT count(*) FROM legs) AS legs, (SELECT count(*) FROM legs WHERE interaction_id IS NULL) AS loose;

-- calls.desks | each answered call was picked up at the file's desk (its answering leg's extension) and is at the file's shop (its location's config_key alias) | expected: no call differs
-- want: value is None and row['calls'] == 33
WITH story(n, desk, shop) AS (VALUES
    (1, '102', 'main'), (2, '102', 'main'), (3, '102', 'main'), (4, '102', 'main'), (5, '102', 'main'), (6, '102', 'main'),
    (7, '102', 'main'), (8, '102', 'main'), (9, '103', 'main'), (10, '101', 'main'), (11, '104', 'main'), (12, '103', 'main'),
    (13, '103', 'main'), (14, '103', 'main'), (15, '302', 'west'), (16, '302', 'west'), (17, '301', 'west'), (21, '101', 'main'),
    (22, '103', 'main'), (23, '102', 'main'), (24, '102', 'main'), (25, '201', 'east'), (26, '201', 'east'), (27, '201', 'east'),
    (28, '202', 'east'), (29, '101', 'main'), (30, '102', 'main'), (31, '101', 'main'), (32, '102', 'main'), (33, '301', 'west'),
    (34, '301', 'west'), (35, '303', 'west'), (36, '303', 'west')),
seeded AS (
    SELECT s.*, (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
                 FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || s.n, 'UTF8'), 'sha1') h) AS transcript
    FROM story s)
SELECT 'calls.desks' AS key,
       string_agg(s.n::text, ' ' ORDER BY s.n) FILTER (WHERE l.extension IS DISTINCT FROM s.desk OR a.value IS DISTINCT FROM s.shop) AS value,
       count(l.id) AS calls
FROM seeded s LEFT JOIN interactions.transcript t ON t.id = s.transcript LEFT JOIN interactions.interaction i ON i.id = t.interaction_id
LEFT JOIN interactions.call_leg l ON l.interaction_id = i.id AND l.status = 'answered'
LEFT JOIN core.location_alias a ON a.location_id = i.location_id AND a.namespace = 'config_key';

-- calls.lines | every leg of an inbound call dialled a pbx_extension alias of the call's shop (its group line, so the Calls page names the shop); an outbound leg keeps no line | expected: no leg differs, 49 legs
-- want: value == 0 and row['legs'] == 49
SELECT 'calls.lines' AS key, count(*) FILTER (WHERE NOT ok) AS value, count(*) AS legs
FROM (SELECT CASE WHEN i.direction = 'outbound' THEN l.line IS NULL
                  ELSE EXISTS (SELECT 1 FROM core.location_alias a WHERE a.namespace = 'pbx_extension' AND a.value = l.line AND a.location_id = i.location_id) END AS ok
      FROM interactions.call_leg l JOIN interactions.interaction i ON i.id = l.interaction_id WHERE l.provider = 'seed:pbx') x;

-- calls.misses | account A5's unanswered calls after call 17 from its number (files 18 to 20): the calendar days after call 17 each falls on, its first desk, each ringing its first desk 20 s and then the shop's three desks 15 s together, all no_answer, each waiting, not out of hours, no attempt, not dismissed, with no recording or verdict; no answered call from that number after call 17; and call 16's morning miss: the same legs from desk 302, got through by call 16 when it was answered | expected: days 1 6 9, first desks 302 303 302 (en) or 303 302 303 (ru), every other fact as stated
-- want: each(value, ['1', '6', '9'], sep=' ') and each(row['desks'], ['302', '303', '302'] if cfg == 'en' else ['303', '302', '303'], sep=' ') and row['shaped'] == 3 and row['answered_after'] == 0 and row['morning'] == 1
WITH number AS (
    SELECT f.caller_token AS token, i.started_at, (i.started_at AT TIME ZONE z.tz)::date AS day
    FROM interactions.transcript t JOIN interactions.interaction i ON i.id = t.interaction_id JOIN core.location z ON z.id = i.location_id
    CROSS JOIN LATERAL (SELECT caller_token FROM interactions.call_leg WHERE interaction_id = i.id ORDER BY started_at LIMIT 1) f
    WHERE t.id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
          FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || 17, 'UTF8'), 'sha1') h)),
later AS (
    SELECT i.id, i.started_at, i.answered_at, m.state, m.out_of_hours, m.attempts, m.dismissed_at, m.interaction_id IS NOT NULL AS missed,
           a.value AS shop, (i.started_at AT TIME ZONE z.tz)::date - n.day AS days
    FROM number n JOIN interactions.interaction i ON i.started_at > n.started_at
    JOIN LATERAL (SELECT caller_token FROM interactions.call_leg WHERE interaction_id = i.id ORDER BY started_at LIMIT 1) f ON f.caller_token = n.token
    LEFT JOIN interactions.missed_call m ON m.interaction_id = i.id LEFT JOIN core.location z ON z.id = i.location_id
    LEFT JOIN core.location_alias a ON a.location_id = i.location_id AND a.namespace = 'config_key'
    WHERE i.id IN (SELECT interaction_id FROM interactions.call_leg WHERE provider = 'seed:pbx'))
SELECT 'calls.misses' AS key, (SELECT string_agg(days::text, ' ' ORDER BY started_at) FROM later WHERE missed) AS value,
       (SELECT string_agg((SELECT extension FROM interactions.call_leg WHERE interaction_id = x.id ORDER BY started_at, ring_s DESC LIMIT 1), ' ' ORDER BY x.started_at) FROM later x WHERE x.missed) AS desks,
       (SELECT count(*) FROM later WHERE answered_at IS NOT NULL) AS answered_after,
       (SELECT count(*) FROM later x WHERE x.missed AND x.state = 'waiting' AND x.out_of_hours = false AND x.attempts = 0 AND x.dismissed_at IS NULL
           AND x.shop = 'west' AND (SELECT array_agg(l.ring_s ORDER BY l.started_at, l.ring_s DESC) FROM interactions.call_leg l WHERE l.interaction_id = x.id
                AND l.status = 'no_answer' AND l.talk_s = 0 AND l.started_at = x.started_at + make_interval(secs => CASE WHEN l.ring_s = 20 THEN 0 ELSE 20 END)) = ARRAY[20, 15, 15, 15]
           AND (SELECT count(DISTINCT extension) FROM interactions.call_leg WHERE interaction_id = x.id AND started_at > x.started_at) = 3
           AND NOT EXISTS (SELECT 1 FROM interactions.media_object WHERE interaction_id = x.id)
           AND NOT EXISTS (SELECT 1 FROM interactions.interaction_analysis WHERE interaction_id = x.id)) AS shaped,
       (SELECT count(*) FROM interactions.missed_call m JOIN interactions.interaction x ON x.id = m.interaction_id
        JOIN interactions.transcript t ON t.interaction_id = m.resolved_by_interaction_id JOIN interactions.interaction c ON c.id = t.interaction_id
        WHERE t.id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
          FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || 16, 'UTF8'), 'sha1') h)
          AND m.state = 'got_through' AND m.resolved_at = c.answered_at AND m.attempts = 0 AND x.answered_at IS NULL
          AND (x.started_at AT TIME ZONE 'UTC')::date = (c.started_at AT TIME ZONE 'UTC')::date AND (SELECT extension FROM interactions.call_leg WHERE interaction_id = x.id ORDER BY started_at, ring_s DESC LIMIT 1) = '302'
          AND (SELECT array_agg(l.ring_s ORDER BY l.started_at, l.ring_s DESC) FROM interactions.call_leg l WHERE l.interaction_id = x.id
                AND l.status = 'no_answer' AND l.talk_s = 0 AND l.started_at = x.started_at + make_interval(secs => CASE WHEN l.ring_s = 20 THEN 0 ELSE 20 END)) = ARRAY[20, 15, 15, 15]
           AND (SELECT count(DISTINCT extension) FROM interactions.call_leg WHERE interaction_id = x.id AND started_at > x.started_at) = 3) AS morning;

-- calls.numbers | the outside number of each call, read as its first leg's phone token: the calls that share one are the calls whose files give one number (S8's three, S6's two and its morning miss, A5's four, A6's two, A1's two), and every other call has a number of its own | expected 28 numbers over 37 calls, grouped as the files group them
-- want: value == '9 10 11|15 16 16m|17 18 19 20|21 22|23 24' and row['numbers'] == 28 and row['calls'] == 37
WITH story(n, en, en_ring, en_talk, ru, ru_ring, ru_talk) AS (VALUES
    ('1', '10:42', 9, 138, '11:20', 7, 147), ('2', '13:20', 7, 141, '14:05', 6, 121),
    ('3', '11:05', 5, 83, '17:40', 9, 95), ('4', '15:10', 8, 124, '12:15', 5, 130),
    ('5', '09:35', 4, 146, '13:30', 4, 115), ('6', '14:15', 6, 196, '15:40', 5, 158),
    ('7', '13:50', 5, 122, '15:10', 5, 113), ('8', '07:52', 12, 95, '14:20', 11, 105),
    ('9', '10:25', 31, 89, '12:35', 14, 99), ('10', '14:35', 6, 180, '15:40', 8, 215),
    ('11', '09:10', 9, 125, '10:15', 6, 153), ('12', '11:40', 14, 72, '16:25', 12, 91),
    ('13', '16:20', 17, 117, '10:40', 16, 72), ('14', '15:50', 6, 82, '10:20', 9, 91),
    ('15', '15:40', 21, 120, '16:10', 24, 113), ('16', '14:20', 24, 75, '15:25', 27, 95),
    ('16m', '09:12', 35, 0, '10:05', 35, 0), ('17', '10:40', 11, 181, '11:10', 19, 142),
    ('18', '08:05', 35, 0, '09:40', 35, 0), ('19', '13:40', 35, 0, '14:15', 35, 0),
    ('20', '16:15', 35, 0, '17:30', 35, 0), ('21', '09:50', 5, 184, '10:50', 7, 182),
    ('22', '10:15', 18, 114, '11:20', 15, 140), ('23', '10:05', 6, 97, '16:10', 6, 71),
    ('24', '14:30', 4, 128, '09:50', 4, 92), ('25', '09:12', 4, 173, '09:12', 4, 170),
    ('26', '10:20', 4, 220, '11:30', 5, 198), ('27', '11:15', 3, 144, '12:10', 3, 155),
    ('28', '13:15', 9, 135, '14:45', 11, 109), ('29', '11:30', 7, 149, '17:50', 6, 148),
    ('30', '16:40', 5, 157, '11:50', 5, 126), ('31', '08:10', 27, 172, '09:40', 22, 129),
    ('32', '07:40', 3, 133, '09:10', 3, 128), ('33', '09:20', 13, 77, '13:20', 17, 76),
    ('34', '14:05', 16, 83, '16:40', 13, 61), ('35', '11:10', 4, 119, '10:35', 4, 129),
    ('36', '10:30', 3, 129, '12:05', 3, 106)),
answered AS (
    SELECT n::text AS n, t.interaction_id AS id FROM generate_series(1, 36) n
    JOIN interactions.transcript t ON t.id = (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
          FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || n, 'UTF8'), 'sha1') h)),
missed AS (
    SELECT i.id, i.started_at, m.resolved_by_interaction_id AS resolver FROM interactions.interaction i
    JOIN interactions.missed_call m ON m.interaction_id = i.id
    WHERE i.id IN (SELECT interaction_id FROM interactions.call_leg WHERE provider = 'seed:pbx')),
labelled AS (
    SELECT n, id FROM answered
    UNION ALL SELECT '16m', x.id FROM missed x JOIN answered a ON a.id = x.resolver AND a.n = '16'
    UNION ALL SELECT (17 + row_number() OVER (ORDER BY x.started_at))::text, x.id FROM missed x WHERE x.resolver IS NULL),
call AS (
    SELECT s.*, l.id, i.started_at, i.answered_at, i.duration_s, z.tz FROM story s LEFT JOIN labelled l ON l.n = s.n
    LEFT JOIN interactions.interaction i ON i.id = l.id LEFT JOIN core.location z ON z.id = i.location_id),
numbered AS (
    SELECT l.n, coalesce(f.caller_token, f.callee_token) AS token FROM labelled l
    CROSS JOIN LATERAL (SELECT caller_token, callee_token FROM interactions.call_leg WHERE interaction_id = l.id ORDER BY started_at LIMIT 1) f),
groups AS (SELECT string_agg(n, ' ' ORDER BY rtrim(n, 'm')::int, n) AS calls, min(rtrim(n, 'm')::int) AS first, count(*) AS size FROM numbered GROUP BY token)
SELECT 'calls.numbers' AS key, (SELECT string_agg(calls, '|' ORDER BY first) FROM groups WHERE size > 1) AS value,
       (SELECT count(*) FROM groups) AS numbers, (SELECT count(token) FROM numbered) AS calls;

-- calls.transcripts | each answered call has one current transcript, on a recording of its own interaction with no audio stored, engine 'ensemble', in the configuration's language, raw, as long as the call's talk, its segments numbered from 0 without a gap, each a manager's or a customer's line with words and no timing | expected: no call differs
-- want: value is None and row['calls'] == 33
WITH seeded AS (
    SELECT n, (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
               FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || n, 'UTF8'), 'sha1') h) AS transcript
    FROM generate_series(1, 36) n WHERE n NOT BETWEEN 18 AND 20)
SELECT 'calls.transcripts' AS key,
       string_agg(s.n::text, ' ' ORDER BY s.n) FILTER (WHERE NOT (t.is_current AND t.engine = 'ensemble' AND t.language = :'cfg' AND t.pii_state = 'raw'
           AND t.engine_version LIKE '%|restore=%' AND t.engine_version NOT LIKE '%<%' AND t.duration_s = i.duration_s
           AND m.kind = 'recording' AND m.storage_ref_enc IS NULL AND m.interaction_id = i.id
           AND (SELECT count(*) FROM interactions.transcript o WHERE o.interaction_id = i.id AND o.is_current) = 1
           AND (SELECT bool_and(g.speaker_label IN ('manager', 'customer') AND g.text <> '' AND g.start_ms IS NULL) AND max(g.sequence) + 1 = count(*)
                FROM interactions.transcript_segment g WHERE g.transcript_id = t.id))) AS value,
       count(t.id) AS calls
FROM seeded s LEFT JOIN interactions.transcript t ON t.id = s.transcript LEFT JOIN interactions.interaction i ON i.id = t.interaction_id
LEFT JOIN interactions.media_object m ON m.id = t.media_id;

-- calls.verdicts | each answered call has one current scorecard verdict, on its current transcript, under the product's prompt version and scorecard (its key and weights present), on the call's shop's line, with the file's score (none where the rubric gives none); judged except the two outbound calls (8, 11); sealed quotes on every judged one | expected: no call differs
-- want: value is None and row['calls'] == 33 and row['unjudged'] == '8 11'
WITH story(n, en, ru) AS (VALUES
    (1, 40.0, 40.0), (2, 53.3, 53.3), (3, 63.6, 63.6), (4, 68.8, 68.8), (5, 92.9, 92.9), (6, 71.9, 71.9), (7, 94.4, 94.4),
    (8, NULL, NULL), (9, 31.2, 31.2), (10, NULL, NULL), (11, NULL, NULL), (12, 40.0, 40.0), (13, 34.6, 36.7), (14, 56.2, 56.2),
    (15, 25.0, 25.0), (16, NULL, NULL), (17, NULL, NULL), (21, 75.0, 75.0), (22, 46.4, 46.4), (23, 60.0, 62.5), (24, 80.0, 80.0),
    (25, 83.3, 83.3), (26, 93.8, 100.0), (27, 100.0, 100.0), (28, 53.8, 53.3), (29, NULL, NULL), (30, NULL, NULL),
    (31, 81.2, 84.4), (32, 82.1, 81.2), (33, 44.4, 45.5), (34, 50.0, 50.0), (35, 60.0, 60.0), (36, 82.1, 81.2)),
seeded AS (
    SELECT s.n, CASE WHEN :'cfg' = 'en' THEN s.en ELSE s.ru END AS score,
           (SELECT encode(set_byte(set_byte(substring(h FROM 1 FOR 16), 6, (get_byte(h, 6) & 15) | 80), 8, (get_byte(h, 8) & 63) | 128), 'hex')::uuid
            FROM digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/call-transcript/' || s.n, 'UTF8'), 'sha1') h) AS transcript
    FROM story s)
SELECT 'calls.verdicts' AS key,
       string_agg(s.n::text, ' ' ORDER BY s.n) FILTER (WHERE a.id IS NULL OR a.score IS DISTINCT FROM s.score
           OR (a.prompt_version LIKE 'scorecard:' || (a.result_public ->> 'scorecard') || '|prompt:%') IS NOT TRUE OR NOT a.result_public ? 'weights'
           OR NOT EXISTS (SELECT 1 FROM core.location_alias z JOIN interactions.interaction i ON i.location_id = z.location_id
                          WHERE i.id = t.interaction_id AND z.namespace = 'pbx_extension' AND z.value = a.result_public ->> 'line')
           OR (a.result_public ->> 'judged')::boolean IS DISTINCT FROM (a.result_enc IS NOT NULL)
           OR (SELECT count(*) FROM interactions.interaction_analysis o WHERE o.interaction_id = t.interaction_id AND o.kind = 'scorecard' AND o.is_current) <> 1) AS value,
       count(a.id) AS calls,
       string_agg(s.n::text, ' ' ORDER BY s.n) FILTER (WHERE (a.result_public ->> 'judged')::boolean IS NOT TRUE) AS unjudged
FROM seeded s LEFT JOIN interactions.transcript t ON t.id = s.transcript AND t.is_current
LEFT JOIN interactions.interaction_analysis a ON a.transcript_id = t.id AND a.kind = 'scorecard' AND a.is_current;

-- calls.read | the call log's reads: every one succeeded, each from where the one before it stopped (no span unread between the first read and T), the last at T on the home clock (the main shop's zone) | expected one read a call day and the last at T
-- want: value == row['days'] + 1 and row['failed'] == 0 and row['unread'] == 0 and row['last_at_t'] == 1
WITH reads AS (
    SELECT status, (checkpoint ->> 'since')::timestamptz AS since, (checkpoint ->> 'read_at')::timestamptz AS read_at,
           lag((checkpoint ->> 'read_at')::timestamptz) OVER (ORDER BY (checkpoint ->> 'read_at')::timestamptz) AS before
    FROM interactions.recording_run WHERE provider = 'seed:pbx' AND checkpoint ->> 'operation' = 'call_log'),
home AS (SELECT l.tz FROM core.location l JOIN core.location_alias a ON a.location_id = l.id AND a.namespace = 'config_key' AND a.value = 'main')
SELECT 'calls.read' AS key, count(*) AS value,
       (SELECT count(DISTINCT (i.started_at AT TIME ZONE (SELECT tz FROM home))::date) FROM interactions.interaction i
        WHERE i.id IN (SELECT interaction_id FROM interactions.call_leg WHERE provider = 'seed:pbx')) AS days,
       count(*) FILTER (WHERE status <> 'succeeded') AS failed,
       count(*) FILTER (WHERE before IS NOT NULL AND since <> before) AS unread,
       (max(read_at) = ((:'T')::timestamp AT TIME ZONE (SELECT tz FROM home)))::int AS last_at_t
FROM reads;
