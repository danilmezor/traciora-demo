-- assistant/checks.sql: read-only proofs that the core database holds the assistant step's notes, team notes and proposals.
-- Run on the tenant's core database: python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --dsn <core DSN>
--   --file v1/assistant/checks.sql. Every query returns one row: the statement's key and the value found.
-- A seeded note carries release_sha_written 'seed-v1+<product commit>'. A proposal, a thread and a person are found by
-- the id seeder/ids.py gives them: uuid5 over 'seed:v1/<cfg>/<kind>/<key>' (pgcrypto's sha1). T is read on the clock of
-- the shop keyed main. Counts are those of assistant/ledger_rows.json and DESIGN.md sections 3 and 8; the auth.db rows
-- and the chat files are proved by assistant/checks.py.

SET default_transaction_read_only = on;

-- assistant.notes | the personal notes: 62 rows, 52 active, 4 dormant, 6 archived (3 replaced by a successor of the same owner, class and subject, 3 deleted), live ones held by 12 people (mem.personal_live, mem.personal_ended, mem.personal_per_person) | expected 62, 52, 4, 6, 3, 12
-- want: value == 62 and (row['active'], row['dormant'], row['archived'], row['replaced'], row['holders']) == (52, 4, 6, 3, 12)
SELECT 'assistant.notes' AS key, count(*) AS value,
       count(*) FILTER (WHERE m.state = 'active') AS active, count(*) FILTER (WHERE m.state = 'dormant') AS dormant,
       count(*) FILTER (WHERE m.state = 'archived') AS archived,
       count(*) FILTER (WHERE m.state = 'archived' AND n.login_id = m.login_id AND n.memory_class = m.memory_class AND n.subject_token = m.subject_token) AS replaced,
       count(DISTINCT m.login_id) FILTER (WHERE m.state <> 'archived') AS holders
FROM platform.memory m LEFT JOIN platform.memory n ON n.id = m.superseded_by
WHERE m.scope = 'personal' AND m.release_sha_written LIKE 'seed-v1+%';

-- assistant.team | the team notes: 14, 13 active and 1 unverified; visible from junior 11, middle 2, senior 1 (mem.team_notes) | expected 14, 13, 1, 11, 2, 1
-- want: value == 14 and (row['active'], row['unverified'], row['junior'], row['middle'], row['senior']) == (13, 1, 11, 2, 1)
SELECT 'assistant.team' AS key, count(*) AS value,
       count(*) FILTER (WHERE m.state = 'active') AS active, count(*) FILTER (WHERE m.state = 'unverified') AS unverified,
       count(*) FILTER (WHERE r.key = 'junior') AS junior, count(*) FILTER (WHERE r.key = 'middle') AS middle,
       count(*) FILTER (WHERE r.key = 'senior') AS senior
FROM platform.memory m JOIN core.access_level r ON r.rank = m.min_rank AND r.active
WHERE m.scope = 'business' AND m.release_sha_written LIKE 'seed-v1+%';

-- assistant.proposals | the 19 proposals P01 to P19: 14 approved, each published as a seeded team note it carries the subject of, decided by someone other than its proposer; 3 rejected, each with a reason, one of them withdrawn (decided by its proposer); 2 waiting (mem.proposals) | expected 19, 14, 14, 3, 1, 2
-- want: value == 19 and (row['approved'], row['published'], row['rejected'], row['withdrawn'], row['waiting'], row['own_approval']) == (14, 14, 3, 1, 2, 0)
WITH ours AS (
    SELECT encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
    FROM generate_series(1, 19) n,
         LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/proposal/P' || lpad(n::text, 2, '0'), 'UTF8'), 'sha1') AS h) d)
SELECT 'assistant.proposals' AS key, count(p.id) AS value,
       count(*) FILTER (WHERE p.status = 'approved') AS approved,
       count(*) FILTER (WHERE p.status = 'approved' AND m.state IN ('active', 'unverified') AND m.subject_token = p.subject_token
                          AND m.release_sha_written LIKE 'seed-v1+%') AS published,
       count(*) FILTER (WHERE p.status = 'rejected' AND p.reason_enc IS NOT NULL) AS rejected,
       count(*) FILTER (WHERE p.status = 'rejected' AND p.approver_login_id = p.owner_login_id) AS withdrawn,
       count(*) FILTER (WHERE p.status = 'proposed') AS waiting,
       count(*) FILTER (WHERE p.status = 'approved' AND p.approver_login_id = p.owner_login_id) AS own_approval
FROM ours o JOIN platform.proposal p ON p.id = o.id
LEFT JOIN platform.memory m ON 'memory:' || m.id = p.published_as;

-- assistant.visible | A.5: the team notes a junior, a middle and a senior see (min_rank at or below their rank) | expected 11, 13, 14
-- want: (row['junior'], row['middle'], row['senior']) == (11, 13, 14) and value == 14
SELECT 'assistant.visible' AS key, count(*) FILTER (WHERE m.min_rank <= (SELECT rank FROM core.access_level WHERE key = 'senior')) AS value,
       count(*) FILTER (WHERE m.min_rank <= (SELECT rank FROM core.access_level WHERE key = 'junior')) AS junior,
       count(*) FILTER (WHERE m.min_rank <= (SELECT rank FROM core.access_level WHERE key = 'middle')) AS middle,
       count(*) FILTER (WHERE m.min_rank <= (SELECT rank FROM core.access_level WHERE key = 'senior')) AS senior
FROM platform.memory m
WHERE m.scope = 'business' AND m.state IN ('active', 'unverified') AND m.release_sha_written LIKE 'seed-v1+%';

-- assistant.junior | A.1: slot 6, the junior, keeps six live personal notes | expected 6
-- want: value == 6
SELECT 'assistant.junior' AS key, count(*) AS value
FROM platform.memory m JOIN identity.login l ON l.id = m.login_id,
     LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/6', 'UTF8'), 'sha1') AS h) d
WHERE l.person_id = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid
  AND m.scope = 'personal' AND m.state IN ('active', 'dormant') AND m.release_sha_written LIKE 'seed-v1+%';

-- assistant.nightly | the night's proposal (mem.nightly): waiting, no owner, three holders, the middle rank as its floor, a night on or before T's date; its subject is held by exactly three logins' live personal notes, and no other subject by three or more | expected 1, 3, 3, 0
-- want: value == 1 and (row['holders'], row['held_by'], row['crowded']) == (3, 3, 0) and row['floor'] == 'middle' and row['night_ok']
WITH live AS (SELECT subject_token, count(DISTINCT login_id) AS n FROM platform.memory
              WHERE scope = 'personal' AND state IN ('active', 'dormant') AND release_sha_written LIKE 'seed-v1+%' GROUP BY subject_token),
night AS (SELECT p.* FROM platform.proposal p WHERE p.holders_count IS NOT NULL AND p.owner_login_id IS NULL AND p.status = 'proposed')
SELECT 'assistant.nightly' AS key, (SELECT count(*) FROM night) AS value, max(n.holders_count) AS holders,
       max(l.n) AS held_by, (SELECT count(*) FROM live WHERE live.n >= 3 AND live.subject_token NOT IN (SELECT subject_token FROM night)) AS crowded,
       max(r.key) AS floor, bool_and(n.dream_night <= (:'T')::date) AS night_ok
FROM night n LEFT JOIN live l ON l.subject_token = n.subject_token LEFT JOIN core.access_level r ON r.rank = n.min_rank AND r.active;

-- assistant.waiting | A.7: what of the seed's waits for a senior in Memory at T: two open proposals (of P01 to P19) and one team note to check | expected 2 and 1
-- want: value == 2 and row['to_check'] == 1
WITH ours AS (
    SELECT encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
    FROM generate_series(1, 19) n,
         LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/proposal/P' || lpad(n::text, 2, '0'), 'UTF8'), 'sha1') AS h) d)
SELECT 'assistant.waiting' AS key, (SELECT count(*) FROM platform.proposal WHERE status = 'proposed' AND id IN (SELECT id FROM ours)) AS value,
       (SELECT count(*) FROM platform.memory WHERE scope = 'business' AND state = 'unverified' AND release_sha_written LIKE 'seed-v1+%') AS to_check;

-- assistant.rule | the discount rule (P02) published as a team note on the rule's day (rule_on), and the S4 note proposals of slot 6 decided on slot 4's next working day (P01 approved, P07 declined); the dates on the clock of the shop keyed main | expected the anchors
-- want: value == str(a['rule_on']) and row['p01'] == str(a['s4_note1_decided']) and row['p07'] == str(a['s4_note2_decided'])
WITH zone AS (SELECT l.tz FROM core.location l JOIN core.location_alias a ON a.location_id = l.id WHERE a.namespace = 'config_key' AND a.value = 'main'),
ids_ AS (SELECT k, encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
         FROM unnest(ARRAY['P01', 'P02', 'P07']) k,
              LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/proposal/' || k, 'UTF8'), 'sha1') AS h) d)
SELECT 'assistant.rule' AS key,
       (SELECT (m.approved_at AT TIME ZONE z.tz)::date::text FROM ids_ i JOIN platform.proposal p ON p.id = i.id
        JOIN platform.memory m ON 'memory:' || m.id = p.published_as, zone z WHERE i.k = 'P02') AS value,
       (SELECT (p.decided_at AT TIME ZONE z.tz)::date::text FROM ids_ i JOIN platform.proposal p ON p.id = i.id, zone z WHERE i.k = 'P01' AND p.status = 'approved') AS p01,
       (SELECT (p.decided_at AT TIME ZONE z.tz)::date::text FROM ids_ i JOIN platform.proposal p ON p.id = i.id, zone z WHERE i.k = 'P07' AND p.status = 'rejected') AS p07;

-- assistant.sources | each personal note names its chat: the ten notes saved in a hand-written thread name that thread's id, every other names a chat id of its own (the background threads are not loaded); a note's source time is not after it starts | expected 10 and 0
-- want: value == 10 and row['unsourced'] == 0
WITH threads AS (
    SELECT encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
    FROM unnest(ARRAY['s2-discounts', 's2-cost', 's2-rule', 's3-missed-calls', 's4-default-shop', 's4-money-dates', 's4-short-answers', 's4-two-times',
                      's4-call-summary', 's4-prices-source', 's4-first-call-proposal', 's4-readback-proposal', 's4-driver-proposal',
                      's8-prices-source', 's12-prices-source']) k,
         LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/thread/' || k, 'UTF8'), 'sha1') AS h) d)
SELECT 'assistant.sources' AS key, count(*) FILTER (WHERE m.source_conversation_id IN (SELECT id FROM threads)) AS value,
       count(*) FILTER (WHERE m.source_conversation_id IS NULL OR m.source_at IS NULL OR m.source_at > m.valid_from) AS unsourced
FROM platform.memory m WHERE m.scope = 'personal' AND m.release_sha_written LIKE 'seed-v1+%';

-- inv.assistant.night | where the night's rules leave the rows (DESIGN.md section 3): no active personal note unused for 90 days before T, no dormant one outside 90 to 180 days, no active team note whose check is due by T, no unverified one whose check is not | expected 0
-- want: value == 0
WITH zone AS (SELECT l.tz FROM core.location l JOIN core.location_alias a ON a.location_id = l.id WHERE a.namespace = 'config_key' AND a.value = 'main'),
t AS (SELECT (:'T')::timestamp AT TIME ZONE z.tz AS at FROM zone z)
SELECT 'inv.assistant.night' AS key, count(*) AS value
FROM platform.memory m, t
WHERE m.release_sha_written LIKE 'seed-v1+%' AND (
      (m.scope = 'personal' AND m.state = 'active' AND greatest(m.last_used_at, m.valid_from) <= t.at - interval '90 days')
   OR (m.scope = 'personal' AND m.state = 'dormant' AND NOT greatest(m.last_used_at, m.valid_from) BETWEEN t.at - interval '180 days' AND t.at - interval '90 days')
   OR (m.scope = 'business' AND m.state = 'active' AND m.next_retest_at <= t.at)
   OR (m.scope = 'business' AND m.state = 'unverified' AND m.next_retest_at > t.at));

-- assistant.supplier_overdue | briefs 1 and 2 read board.days_overdue of card S06-supplier: open at T and three weeks past its deadline, the Monday of week T-3 (ledger s6.supplier_task: 21 to 27 days) | expected 21 to 27
-- want: 21 <= value <= 27
WITH zone AS (SELECT l.tz FROM core.location l JOIN core.location_alias a ON a.location_id = l.id WHERE a.namespace = 'config_key' AND a.value = 'main'),
card AS (SELECT encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
         FROM (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/card/S06-supplier', 'UTF8'), 'sha1') AS h) d)
SELECT 'assistant.supplier_overdue' AS key,
       CASE WHEN w.due_at < (:'T')::timestamp AT TIME ZONE z.tz THEN ((:'T')::timestamp AT TIME ZONE z.tz AT TIME ZONE w.due_tz)::date - w.due_local::date END AS value
FROM card c JOIN work.work_item w ON w.id = c.id JOIN work.work_state st ON st.id = w.state_id, zone z
WHERE w.deleted_at IS NULL AND st.state_group NOT IN ('completed', 'cancelled');

-- assistant.east_desk | brief 4's desk point, loaded where the roster shows the desk short (ru): roster.uncovered_days for the desk at east over the next two weeks counts the draft days of slot 16's week off on which she would work (her rota, two on and two off from T), Monday to Wednesday of week W+2, and no other day (S05, ledger s5.week_off, card G-cover-week-off). In English the one cover band shows no day short and the point is not in v1 (seeder/assistant.py NOT_IN_V1) | expected ru the want's count, none outside her week off; en not read
-- want: cfg == 'en' or (row['outside'] == 0 and value == sum(1 for i in range(7) if (a['week_off'] + timedelta(i)).weekday() < 3 and (a['week_off'] + timedelta(i) - a['T'].date()).days % 4 in (2, 3)))
WITH zone AS (SELECT l.tz FROM core.location l JOIN core.location_alias a ON a.location_id = l.id WHERE a.namespace = 'config_key' AND a.value = 'main'),
sixteen AS (SELECT encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid AS id
            FROM (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/person/16', 'UTF8'), 'sha1') AS h) d),
desk AS (SELECT DISTINCT sh.location_id, sh.position_id FROM workforce.shift sh JOIN sixteen s ON s.id = sh.person_id
         JOIN core.location_alias a ON a.location_id = sh.location_id WHERE a.namespace = 'config_key' AND a.value = 'east' AND sh.deleted_at IS NULL),
away AS (SELECT min(av.on_date) AS first, max(av.on_date) AS last FROM workforce.availability av JOIN sixteen s ON s.id = av.person_id WHERE av.kind = 'unavailable' AND av.on_date IS NOT NULL),
open_days AS (
    SELECT DISTINCT g.d::date AS d
    FROM desk k, zone z, generate_series((:'T')::date, (:'T')::date + 14, interval '1 day') g(d)
    JOIN workforce.coverage_requirement cr ON cr.active AND cr.required AND get_bit(cr.day_mask, extract(isodow FROM g.d)::int - 1) = 1
         AND (cr.valid_from IS NULL OR cr.valid_from <= g.d::date) AND (cr.valid_to IS NULL OR cr.valid_to >= g.d::date)
    JOIN core.location l ON l.id = cr.location_id
    WHERE cr.location_id = k.location_id AND cr.position_id = k.position_id
      AND jsonb_array_length(coalesce(l.business_hours -> lower(to_char(g.d, 'Dy')), '[]'::jsonb)) > 0
      AND NOT EXISTS (SELECT 1 FROM core.location_hours_exception e WHERE e.location_id = l.id AND e.on_date = g.d::date AND e.kind = 'closed')
      AND NOT EXISTS (SELECT 1 FROM workforce.shift s
                      WHERE s.location_id = cr.location_id AND s.position_id = cr.position_id AND s.person_id IS NOT NULL AND s.deleted_at IS NULL
                        AND s.status <> 'cancelled' AND s.business_day = g.d::date
                        AND s.start_local < g.d::date + CASE WHEN cr.end_time_local <= cr.start_time_local THEN 1 ELSE 0 END + cr.end_time_local
                        AND s.end_local > g.d::date + cr.start_time_local))
SELECT 'assistant.east_desk' AS key, count(*) AS value, count(*) FILTER (WHERE o.d NOT BETWEEN w.first AND w.last) AS outside
FROM open_days o, away w;
