-- conversations/checks.sql: read-only proofs that Chatwoot's database holds the chats step's story chats as Chatwoot
-- v4.18.0 would have written them. Run on Chatwoot's database as its owner:
--   python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --dsn <Chatwoot DSN> --file v1/conversations/checks.sql
-- (seeder.chats.chatwoot_dsn() gives the DSN from the install's environment). Every query returns one row: the
-- statement's key and the value found. A story chat is found by the uuid seeder/ids.py gives it: uuid5 over
-- 'seed:v1/<cfg>/conversation/<file number>' (pgcrypto's sha1). Times in Chatwoot are UTC; T is on the home clock.
-- Lines the running product adds after T (its priority clock) are left out where a count would see them.

SET default_transaction_read_only = on;

-- chats.inboxes | the story chats by inbox | expected en "Chat 16, Telegram 11", ru "Avito 5, Chat 11, Telegram 8, VK 3"
-- want: value == {'en': 'Chat 16, Telegram 11', 'ru': 'Avito 5, Chat 11, Telegram 8, VK 3'}[cfg]
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'chats.inboxes' AS key, string_agg(name || ' ' || k, ', ' ORDER BY name) AS value
FROM (SELECT i.name, count(*) AS k FROM seeded s JOIN inboxes i ON i.id = s.inbox_id GROUP BY i.name) x;

-- chats.at_t | the chats open, pending or snoozed at T by file number, and the resolved ones | expected "3 open, 5 open, 6 open, 7 pending", 23 resolved of 27
-- want: value == '3 open, 5 open, 6 open, 7 pending' and row['resolved'] == 23 and row['chats'] == 27
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'chats.at_t' AS key,
       string_agg(n || ' ' || CASE status WHEN 0 THEN 'open' WHEN 2 THEN 'pending' WHEN 3 THEN 'snoozed' END, ', ' ORDER BY n) FILTER (WHERE status <> 1) AS value,
       count(*) FILTER (WHERE status = 1) AS resolved, count(*) AS chats
FROM seeded;

-- chats.unread | the live chats' unread customer lines as Chatwoot counts them (after agent_last_seen_at, at most 10) | expected "3 2, 5 0, 6 2, 7 0"
-- want: value == '3 2, 5 0, 6 2, 7 0'
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'chats.unread' AS key,
       string_agg(n || ' ' || least(10, (SELECT count(*) FROM messages m WHERE m.conversation_id = s.id AND m.message_type = 0
                                                                    AND m.created_at > s.agent_last_seen_at)), ', ' ORDER BY n) AS value
FROM seeded s WHERE status <> 1;

-- chats.lines | the story chats' lines up to T by kind, as the product's message_facts names them; a customer line that is only a file is not loaded (en two, ru one) | expected en "customer 121, assistant 41, manager 73, note 18", ru "customer 113, assistant 28, manager 77, note 14"
-- want: value == {'en': 'customer 121, assistant 41, manager 73, note 18', 'ru': 'customer 113, assistant 28, manager 77, note 14'}[cfg]
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid),
kinds AS (
    SELECT CASE WHEN m.message_type = 0 THEN 'customer' WHEN m.private THEN 'note' WHEN m.sender_type = 'AgentBot' THEN 'assistant' ELSE 'manager' END AS kind
    FROM seeded s JOIN messages m ON m.conversation_id = s.id
    WHERE m.message_type IN (0, 1) AND m.created_at <= (:'T')::timestamp AT TIME ZONE (CASE :'cfg' WHEN 'en' THEN 'America/New_York' ELSE 'Europe/Ulyanovsk' END) AT TIME ZONE 'UTC')
SELECT 'chats.lines' AS key, 'customer ' || count(*) FILTER (WHERE kind = 'customer') || ', assistant ' || count(*) FILTER (WHERE kind = 'assistant')
       || ', manager ' || count(*) FILTER (WHERE kind = 'manager') || ', note ' || count(*) FILTER (WHERE kind = 'note') AS value
FROM kinds;

-- inv.chats.empty | story chat lines with neither words nor a file: v1 has no attachment pool, so a line that is only a file is not loaded | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.empty' AS key, count(*) AS value
FROM seeded s JOIN messages m ON m.conversation_id = s.id
WHERE coalesce(m.content, '') = '' AND NOT EXISTS (SELECT 1 FROM attachments a WHERE a.message_id = m.id);

-- chats.service_agent | the name of the chats' account's administrator, the service user the product acts as (each manager is an agent), as the tenant's assistant (settings APP_TITLE) | expected en "Brennan Auto Care AI assistant", ru "ИИ-ассистент «Ермак-Сервис»"
-- want: value == {'en': 'Brennan Auto Care AI assistant', 'ru': 'ИИ-ассистент «Ермак-Сервис»'}[cfg]
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'chats.service_agent' AS key, string_agg(u.name, ', ' ORDER BY u.id) AS value
FROM users u JOIN account_users au ON au.user_id = u.id
WHERE au.role = 1 AND u.email LIKE 'assistant@%' AND au.account_id IN (SELECT account_id FROM seeded);

-- inv.chats.display_id | story chats whose display id is not their id (the product keeps display ids, its views read ids) | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.display_id' AS key, count(*) FILTER (WHERE id <> display_id) AS value FROM seeded;

-- inv.chats.parties | story chats without their contact inbox (same contact and inbox), or with a line whose sender is not the chat's contact, an agent of the account or the account's bot | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.parties' AS key,
       count(*) FILTER (WHERE NOT EXISTS (SELECT 1 FROM contact_inboxes ci WHERE ci.id = s.contact_inbox_id AND ci.contact_id = s.contact_id AND ci.inbox_id = s.inbox_id))
     + count(*) FILTER (WHERE EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = s.id AND NOT (
           m.message_type = 2 AND m.sender_type IS NULL
        OR m.sender_type = 'Contact' AND m.sender_id = s.contact_id
        OR m.sender_type = 'User' AND EXISTS (SELECT 1 FROM account_users u WHERE u.user_id = m.sender_id AND u.account_id = s.account_id)
        OR m.sender_type = 'AgentBot' AND EXISTS (SELECT 1 FROM agent_bots b WHERE b.id = m.sender_id AND b.account_id = s.account_id)))) AS value
FROM seeded s;

-- inv.chats.waiting_since | story chats whose waiting_since is not Chatwoot's: none when resolved, else the first customer line after the last public reply of a person or the bot, or the chat's creation when nobody replied | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.waiting_since' AS key,
       count(*) FILTER (WHERE s.waiting_since IS DISTINCT FROM CASE WHEN s.status = 1 THEN NULL WHEN r.last_reply IS NULL THEN s.created_at
           ELSE (SELECT min(m.created_at) FROM messages m WHERE m.conversation_id = s.id AND m.message_type = 0 AND m.created_at > r.last_reply) END) AS value
FROM seeded s
CROSS JOIN LATERAL (SELECT max(m.created_at) AS last_reply FROM messages m
                    WHERE m.conversation_id = s.id AND m.message_type = 1 AND NOT m.private AND m.sender_type IN ('User', 'AgentBot')) r;

-- inv.chats.first_reply | story chats whose first_reply_created_at is not a person's first public reply | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.first_reply' AS key,
       count(*) FILTER (WHERE s.first_reply_created_at IS DISTINCT FROM (SELECT min(m.created_at) FROM messages m
           WHERE m.conversation_id = s.id AND m.message_type = 1 AND NOT m.private AND m.sender_type = 'User')) AS value
FROM seeded s;

-- inv.chats.last_activity | story chats whose last_activity_at is not their last line, activity lines included | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.last_activity' AS key,
       count(*) FILTER (WHERE s.last_activity_at IS DISTINCT FROM (SELECT max(m.created_at) FROM messages m WHERE m.conversation_id = s.id)) AS value
FROM seeded s;

-- inv.chats.resolutions | story chats whose conversation_resolved events are not one per resolved status line, at its instant, for the chat's assignee once a self-assignment line precedes it (none before), its value the whole seconds since the chat opened; or whose resolved line lacks the product's resolved words ("resolv") | expected 0, 27 events
-- want: value == 0 and row['events'] == 27
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid),
resolved AS (
    SELECT m.conversation_id, m.created_at, m.content FROM seeded s JOIN messages m ON m.conversation_id = s.id
    WHERE m.message_type = 2 AND (m.content_attributes #>> '{}')::jsonb #>> '{activity,status}' = 'resolved')
SELECT 'inv.chats.resolutions' AS key,
       (SELECT count(*) FROM resolved r WHERE r.content !~ 'resolv' OR NOT EXISTS (SELECT 1 FROM reporting_events e
            WHERE e.conversation_id = r.conversation_id AND e.name = 'conversation_resolved' AND e.created_at = r.created_at))
     + (SELECT count(*) FROM seeded s JOIN reporting_events e ON e.conversation_id = s.id AND e.name = 'conversation_resolved'
        WHERE NOT EXISTS (SELECT 1 FROM resolved r WHERE r.conversation_id = s.id AND r.created_at = e.created_at)
           OR e.event_start_time <> s.created_at OR e.inbox_id <> s.inbox_id
           OR e.value <> extract(epoch FROM date_trunc('second', e.created_at)) - extract(epoch FROM date_trunc('second', s.created_at))
           OR e.user_id IS DISTINCT FROM CASE WHEN EXISTS (SELECT 1 FROM messages m WHERE m.conversation_id = s.id AND m.message_type = 2
                  AND m.content LIKE '% self-assigned this conversation' AND m.created_at < e.created_at) THEN s.assignee_id END)
     + (SELECT count(*) FROM seeded s WHERE s.status = 1 AND NOT EXISTS (SELECT 1 FROM resolved r WHERE r.conversation_id = s.id)) AS value,
       (SELECT count(*) FROM seeded s JOIN reporting_events e ON e.conversation_id = s.id AND e.name = 'conversation_resolved') AS events;

-- inv.chats.labels | story chats whose cached label list is not their label taggings, or a tag whose count is not its taggings | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.labels' AS key,
       (SELECT count(*) FROM seeded s WHERE coalesce((SELECT string_agg(x, ',' ORDER BY x) FROM unnest(string_to_array(nullif(s.cached_label_list, ''), ', ')) x), '')
            <> coalesce((SELECT string_agg(g.name, ',' ORDER BY g.name) FROM taggings t JOIN tags g ON g.id = t.tag_id
                         WHERE t.taggable_type = 'Conversation' AND t.taggable_id = s.id AND t.context = 'labels'), ''))
     + (SELECT count(*) FROM tags g WHERE g.taggings_count <> (SELECT count(*) FROM taggings t WHERE t.tag_id = g.id)) AS value;

-- inv.chats.owner | story chats whose assignee is not the agent of their last self-assignment line (every story assignment is a manager's first reply) | expected 0
-- want: value == 0
WITH seeded AS (
    SELECT n, c.* FROM generate_series(1, 27) n
    CROSS JOIN LATERAL (SELECT digest(decode('6ba7b8119dad11d180b400c04fd430c8', 'hex') || convert_to('seed:v1/' || :'cfg' || '/conversation/' || n, 'UTF8'), 'sha1') AS h) d
    JOIN conversations c ON c.uuid = encode(set_byte(set_byte(substring(d.h FROM 1 FOR 16), 6, (get_byte(d.h, 6) & 15) | 80), 8, (get_byte(d.h, 8) & 63) | 128), 'hex')::uuid)
SELECT 'inv.chats.owner' AS key,
       count(*) FILTER (WHERE (SELECT u.name || ' self-assigned this conversation' FROM users u WHERE u.id = s.assignee_id)
           IS DISTINCT FROM (SELECT m.content FROM messages m WHERE m.conversation_id = s.id AND m.message_type = 2
                             AND m.content LIKE '% self-assigned this conversation' ORDER BY m.created_at DESC LIMIT 1)) AS value
FROM seeded s;
