"""The step `chats`: the story chats of `v1/conversations/<cfg>/` in Chatwoot, the system of record for conversations,
and the product's own state for them in auth.db, in the load order of conversations/DESIGN.md section 2:
1. through the product: the channels' inboxes (`ChatwootClient.ensure_api_inbox`), the agent bot (`agent_bot`), the
   labels (`AccountApi.create_label`) and one agent-sync pass (`reconcile_agents`), whose `chatwoot_agents` give each
   slot's Chatwoot user; the service administrator (`AccountApi.profile`), named on every build after the tenant's
   assistant (`APP_TITLE` of the settings the tenant step writes), so a rebuilt demo never keeps an earlier demo's name;
2. the guard: Chatwoot's last migration is the one of v4.18.0, the version the rows of `rows.py` follow;
3. straight into Chatwoot's tables, in one transaction, because its API cannot write a past instant: contacts, contact
   inboxes, conversations (display id = id), messages, tags and taggings, `conversation_resolved` events; every
   sequence ends past the last id;
4. through the product's stores in auth.db: each chat's `bridge_threads` row (`RelayStore.save_thread`), every draft
   offered and decided at its own instant (`ConversationStore`), then the open set read from Chatwoot as the product's
   resync reads it, on the clock of T (`ConversationSync.resync`), with the time each open chat's owner took it.
`reset` removes the seed's conversations (found by their uuids) with everything in them, its contacts, and their rows in
auth.db. The inboxes, the bot, the labels and the agents stay: they are the product's, a deleted inbox takes whatever
else it holds, and one made again has a new id, so a repeat build would differ."""
import asyncio
import dataclasses
import json
import os
import sqlite3

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.types.json import Jsonb

from seeder import inputs, manifest
from seeder.chats import rows

MIGRATION = "20260831000000"  # Chatwoot v4.18.0's last migration
TABLES = ("contacts", "contact_inboxes", "conversations", "messages", "taggings", "reporting_events")
AUTH_TABLES = ("bridge_threads", "bridge_inbound", "bridge_outbound", "conversation_state", "conversation_draft", "draft_outcome", "compose_text", "agent_turn", "handoff_owed")


def chatwoot_dsn():
    """Chatwoot's database as its owner: the reader's address (CHATWOOT_DATABASE_URL) with the role `chatwoot` and
    CHATWOOT_DB_PASSWORD."""
    reader = conninfo_to_dict(os.environ["CHATWOOT_DATABASE_URL"])
    return make_conninfo(**(reader | {"user": "chatwoot", "password": os.environ["CHATWOOT_DB_PASSWORD"]}))


def guard(conn):
    version = conn.execute("SELECT max(version) FROM schema_migrations").fetchone()[0]
    trigger = conn.execute("SELECT 1 FROM pg_trigger WHERE tgname = 'conversations_before_insert_row_tr'").fetchone()
    if version != MIGRATION or not trigger:
        raise SystemExit(f"Chatwoot's last migration is {version}; the chats step writes the tables of v4.18.0 ({MIGRATION}) "
                         "with its display-id trigger and refuses another version")


def needs(cfg):
    """The inbox names, label titles and staff slots the configuration's files use."""
    inboxes, labels, slots = set(), set(), set()
    for f in inputs.STORY_FILES["conversations", cfg].values():
        (c,) = f["conversations"]
        inboxes.add(c["inbox"])
        for e in c["timeline"]:
            labels.update(x for x in (e.get("label"), e.get("label_added")) if x)
            slots.update(str(x) for x in (e.get("slot"), e.get("to"), e.get("by"), (e.get("outcome") or {}).get("by"))
                         if isinstance(x, int))
    return sorted(inboxes), sorted(labels), sorted(slots, key=lambda s: int(s))


async def prepare(cfg, client_id, resolve_days):
    """Step 1, through the product: `who` for rows.build, each slot's manager id, auth.db, and the service
    administrator's Chatwoot user id."""
    import httpx

    from traciora.core.auth.manager import AuthManager
    from traciora.core.channels.chatwoot.account_api import AccountApi
    from traciora.core.channels.chatwoot.agent_sync import reconcile_agents
    from traciora.core.channels.chatwoot.agents import AgentStore
    from traciora.core.channels.chatwoot.assistant import BOT_NAME
    from traciora.core.channels.chatwoot.client import ChatwootClient
    from traciora.core.channels.chatwoot.config import ChatwootConnection
    from traciora.core.queries.runtime import CoreSqlRuntime

    inbox_names, titles, slots = needs(cfg)
    conn = ChatwootConnection.from_env()
    client = ChatwootClient(conn, bridge_name="seed")
    await client.startup()
    async with httpx.AsyncClient(timeout=30.0) as http:
        api = AccountApi(conn, http)
        try:
            inboxes = {name: await client.ensure_api_inbox(name) for name in inbox_names}
            bot = (await client.agent_bot(BOT_NAME))["id"]
            held = {label["title"] for label in await api.labels(conn.access_token)}
            for title in titles:
                if title not in held:
                    await api.create_label(conn.access_token, title)
            service = (await api.profile(conn.access_token))["id"]
        finally:
            await client.aclose()
    auth, core = AuthManager(), CoreSqlRuntime(client_id, max_size=2)
    try:
        if await reconcile_agents(auth, core_runtime=core, connection=conn) is None:
            raise SystemExit("the product's agent sync did not run: Chatwoot's connection or MEMORY_ENCRYPTION_KEY is missing")
    finally:
        core.close()
    agents = {a.manager_id: a for a in AgentStore(auth.db_path).all()}
    ladder = {s["slot"]: s for s in inputs.load("tenant/ladder.json")["slots"]}
    users, managers, missing = {}, {}, []
    for slot in slots:
        account = auth.get_manager_by_username(ladder[slot][f"username_{cfg}"])
        agent = account and agents.get(int(account["id"]))
        if not agent:
            missing.append(slot)
            continue
        users[slot], managers[slot] = (agent.chatwoot_user_id, agent.name), int(account["id"])
    if missing:
        raise SystemExit("slots the chats need with no active account or Chatwoot agent (run the step people): " + ", ".join(missing))
    return {"account": conn.account_id, "inboxes": inboxes, "bot": bot, "users": users,
            "service": inputs.load(f"tenant/settings.{cfg}.json")["APP_TITLE"], "resolve_days": resolve_days}, managers, auth.db_path, service


def load(conn, built, account):
    """Step 3: every row into Chatwoot's tables, in the caller's transaction; the rows written."""
    chats = built["chats"]
    mine = {"contacts": [x["id"] for x in built["contacts"]], "contact_inboxes": [c["id"] for c in chats], "conversations": [c["id"] for c in chats],
            "messages": [m["id"] for m in built["messages"]], "taggings": [x["id"] for x in built["taggings"]],
            "reporting_events": [e["id"] for e in built["events"]]}
    taken = [f"{table} {', '.join(map(str, found))}" for table in TABLES
             for found in [[r[0] for r in conn.execute(f"SELECT id FROM {table} WHERE id = ANY(%s) ORDER BY id", (mine[table],))]] if found]
    if taken:
        raise SystemExit("ids the chats step writes are held by rows it did not write (or the step ran before: use --replace): " + "; ".join(taken))
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO contacts (id, name, account_id, identifier, created_at, updated_at, last_activity_at, location, country_code)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, NULL, NULL)",
        [(x["id"], x["name"], account, x["identifier"], x["created_at"], x["last_activity_at"] or x["created_at"], x["last_activity_at"])
         for x in built["contacts"]])
    cur.executemany(
        "INSERT INTO contact_inboxes (id, contact_id, inbox_id, source_id, pubsub_token, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        [(c["id"], c["contact_id"], c["inbox_id"], c["source_id"], c["pubsub_token"], c["created_at"], c["created_at"]) for c in chats])
    for c in chats:
        conn.execute("SELECT setval(%s, %s, false)", (f"conv_dpid_seq_{account}", c["id"]))
        display = conn.execute(
            "INSERT INTO conversations (id, account_id, inbox_id, status, assignee_id, created_at, updated_at, contact_id, contact_inbox_id,"
            " uuid, last_activity_at, agent_last_seen_at, assignee_last_seen_at, custom_attributes, first_reply_created_at, priority,"
            " waiting_since, cached_label_list, status_changed_at)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING display_id",
            (c["id"], account, c["inbox_id"], rows.STATUS[c["status"]], c["assignee_id"], c["created_at"], c["last_activity_at"], c["contact_id"],
             c["id"], c["uuid"], c["last_activity_at"], c["agent_last_seen_at"], c["agent_last_seen_at"] if c["assignee_id"] else None,
             Jsonb(c["custom_attributes"]), c["first_reply_created_at"], c["priority"], c["waiting_since"], c["cached_label_list"],
             c["status_changed_at"])).fetchone()[0]
        if display != c["id"]:
            raise SystemExit(f"conversation {c['id']} got the display id {display}: Chatwoot's display-id trigger changed")
    inbox = {c["id"]: c["inbox_id"] for c in chats}
    with cur.copy("COPY messages (id, content, processed_message_content, account_id, inbox_id, conversation_id, message_type, created_at,"
                  " updated_at, private, status, source_id, content_type, content_attributes, sender_type, sender_id) FROM STDIN") as copy:
        for m in built["messages"]:
            copy.write_row((m["id"], m["content"], m["content"], account, inbox[m["conversation_id"]], m["conversation_id"], m["message_type"],
                            m["created_at"], m["created_at"], m["private"], 0, m["source_id"], 0, stored(m["content_attributes"]),
                            m["sender_type"], m["sender_id"]))
    titles = sorted({x["label"] for x in built["taggings"]})
    cur.executemany("INSERT INTO tags (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", [(t,) for t in titles])
    tag = dict(conn.execute("SELECT name, id FROM tags WHERE name = ANY(%s)", (titles,)).fetchall())
    cur.executemany("INSERT INTO taggings (id, tag_id, taggable_type, taggable_id, context, created_at) VALUES (%s, %s, 'Conversation', %s, 'labels', %s)",
                    [(x["id"], tag[x["label"]], x["conversation_id"], x["created_at"]) for x in built["taggings"]])
    count_tags(conn, list(tag.values()))
    cur.executemany(
        "INSERT INTO reporting_events (id, name, value, value_in_business_hours, account_id, inbox_id, user_id, conversation_id, created_at,"
        " updated_at, event_start_time, event_end_time) VALUES (%s, 'conversation_resolved', %s, 0, %s, %s, %s, %s, %s, %s, %s, %s)",
        [(e["id"], e["value"], account, e["inbox_id"], e["user_id"], e["conversation_id"], e["created_at"], e["created_at"], e["start"],
          e["created_at"]) for e in built["events"]])
    for table in TABLES:
        conn.execute(f"SELECT setval('{table}_id_seq', GREATEST((SELECT max(id) FROM {table}), (SELECT last_value FROM {table}_id_seq)))")
    conn.execute(f"SELECT setval('conversations_id_seq', v), setval('conv_dpid_seq_{account}', v) FROM (SELECT GREATEST("
                 f"(SELECT last_value FROM conversations_id_seq), (SELECT max(display_id) FROM conversations WHERE account_id = %s)) AS v) s", (account,))
    return sum(len(v) for v in mine.values())


def stored(attributes):
    """`messages.content_attributes` as Chatwoot keeps it: a json column under `store ..., coder: JSON`, so the object
    is a JSON string inside the JSON value."""
    return json.dumps(json.dumps(attributes) if attributes else {})


def count_tags(conn, tag_ids):
    conn.execute("UPDATE tags SET taggings_count = (SELECT count(*) FROM taggings WHERE tag_id = tags.id) WHERE id = ANY(%s)", (tag_ids,))


def epoch(t):
    return t.replace(tzinfo=rows.UTC).timestamp()


async def resync(client_id, db_path, T):
    """The open set as the product's resync writes it, on the clock of T."""
    import httpx

    from traciora.core.auth.manager import AuthManager
    from traciora.core.channels.chatwoot.account_api import AccountApi
    from traciora.core.channels.chatwoot.config import ChatwootConnection
    from traciora.core.channels.chatwoot.conversations_store import ConversationStore
    from traciora.core.channels.chatwoot.events import EventHub
    from traciora.core.channels.chatwoot.hours import working_hours
    from traciora.core.channels.chatwoot.relay_store import RelayStore
    from traciora.core.channels.chatwoot.sync import ConversationSync
    from traciora.core.queries.runtime import CoreSqlRuntime

    conn, core = ChatwootConnection.from_env(), CoreSqlRuntime(client_id, max_size=2)
    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            sync = ConversationSync(AccountApi(conn, http), conn.access_token, ConversationStore(db_path), RelayStore(db_path), EventHub(),
                                    lambda day: working_hours(core, on_date=day), lambda: T, core_runtime=core, auth_manager=AuthManager())
            try:
                return await sync.resync(since=None)
            finally:
                await sync.aclose()
    finally:
        core.close()


def step(cfg, client_id, replace):
    from traciora.core.channels.chatwoot.conversations_store import ConversationStore, Thresholds
    from traciora.core.channels.chatwoot.relay_store import RelayStore

    built_at = manifest.read(manifest.shop_dsn(client_id))
    if built_at.get("cfg") != cfg:
        raise SystemExit(f"the shop database is built for {built_at.get('cfg')}, not {cfg}")
    dsn = chatwoot_dsn()
    with psycopg.connect(dsn) as conn:
        guard(conn)
        account = int(os.environ["CHATWOOT_ACCOUNT_ID"])
        minutes, locale = conn.execute("SELECT (settings ->> 'auto_resolve_after')::int, locale FROM accounts WHERE id = %s", (account,)).fetchone()
    if locale != 0:
        raise SystemExit(f"Chatwoot's account has the locale {locale}; the chats' activity lines are its English (0) sentences")
    days = inputs.value("conv.auto_resolve_days", cfg)
    if minutes != days * 1440:
        raise SystemExit(f"Chatwoot's account resolves a silent chat after {minutes} minutes; the chats are written for {days} days")
    if replace:
        reset(cfg, client_id)
    who, managers, db_path, service = asyncio.run(prepare(cfg, client_id, days))
    built = rows.build(cfg, manifest.at(), who)
    with psycopg.connect(dsn) as conn:
        conn.execute("UPDATE users SET name = %s WHERE id = %s", (who["service"], service))
        written = 1 + load(conn, built, account)
    threads, store = RelayStore(db_path), ConversationStore(db_path)
    threads.init()
    store.init()
    for c in built["chats"]:
        threads.save_thread(c["bridge"], c["thread_key"], peer_id=c["peer_id"], contact_id=c["contact_id"], conversation_id=c["id"],
                            now=epoch(c["last_customer_at"]))
        written += 1 + replay(store, c, managers)
    store.set_thresholds(built["day"], Thresholds(*rows.thresholds(), 0))  # the day's thresholds the files' levels follow
    asyncio.run(resync(client_id, db_path, epoch(built["T"])))
    for c in built["chats"]:
        row = store.get(c["id"])
        if c["status"] == "resolved":
            continue
        if row is None:
            raise SystemExit(f"conversation {c['n']} ({cfg}) is {c['status']} at T and the product's resync did not list it")
        store.upsert(dataclasses.replace(row, base_priority=c["base_priority"], owner_since=epoch(c["owner"][1]) if c["owner"] else None))
        written += 1
    return written


def replay(store, c, managers):
    """Every draft of a chat offered and decided through the product's store at its own instants; the drafts. Before each
    step the reply box must hold what the file says: the draft an outcome decides, and before a new draft only one the
    file calls replaced_unseen."""
    actions = []
    for i, d in enumerate(c["drafts"]):
        actions.append((d["at"], 2 * i, "offer", d))
        if d["outcome"] and d["outcome"]["kind"] != "replaced_unseen":
            actions.append((d["outcome"]["at"], 2 * i + 1, d["outcome"]["kind"], d))
    for at, _, what, d in sorted(actions, key=lambda x: x[:2]):
        now, cid = epoch(at), c["id"]
        box = store.draft(cid)
        held = next((x for x in c["drafts"] if box.text and epoch(x["at"]) == box.created_at), None)
        if what == "offer" and held and (held["outcome"] or {}).get("kind") != "replaced_unseen" or what != "offer" and held is not d:
            raise SystemExit(f"conversation {c['n']}: at draft line {d['n']} ({what}) the reply box holds "
                             f"{'line ' + str(held['n']) if held else 'nothing'}, against its file")
        manager = managers[str(d["outcome"]["slot"])] if what != "offer" else None
        if what == "offer":
            store.offer_draft(cid, d["text"], now=now)
        elif what in ("sent_as_is", "sent_edited"):
            store.draft_sent(cid, manager, edited=what == "sent_edited", now=now)
        elif d["outcome"]["own_text"]:
            store.own_text_sent(cid, manager, now=now)
        else:
            store.clear_draft(cid, manager, now=now)
    waiting = bool(store.draft(c["id"]).text)
    if waiting != c["draft_waiting"]:
        raise SystemExit(f"conversation {c['n']}: a draft {'waits' if waiting else 'does not wait'} in the box at T, against its file")
    return len(c["drafts"])


def reset(cfg, client_id):
    """The seed's conversations (both configurations' uuids) with their messages, taggings, events and contact inboxes, its
    contacts no other conversation holds, and those conversations' rows in auth.db."""
    from traciora.core.auth.manager import AuthManager

    with psycopg.connect(chatwoot_dsn()) as conn:
        guard(conn)
        ids = [r[0] for r in conn.execute("SELECT id FROM conversations WHERE uuid = ANY(%s::uuid[])", (rows.uuids(),))]
        tags = [r[0] for r in conn.execute("SELECT DISTINCT tag_id FROM taggings WHERE taggable_type = 'Conversation' AND taggable_id = ANY(%s)", (ids,))]
        conn.execute("DELETE FROM taggings WHERE taggable_type = 'Conversation' AND taggable_id = ANY(%s)", (ids,))
        count_tags(conn, tags)
        for table in ("messages", "reporting_events"):
            conn.execute(f"DELETE FROM {table} WHERE conversation_id = ANY(%s)", (ids,))
        held = conn.execute("DELETE FROM conversations WHERE id = ANY(%s) RETURNING contact_inbox_id", (ids,)).fetchall()
        conn.execute("DELETE FROM contact_inboxes WHERE id = ANY(%s)", ([r[0] for r in held],))
        conn.execute("DELETE FROM contacts c WHERE identifier = ANY(%s) AND account_id = %s AND NOT EXISTS"
                     " (SELECT 1 FROM conversations v WHERE v.contact_id = c.id)", (rows.identifiers(), int(os.environ["CHATWOOT_ACCOUNT_ID"])))
    db = sqlite3.connect(AuthManager().db_path)
    try:
        with db:
            known = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            marks = ",".join("?" * len(ids))
            for table in AUTH_TABLES:
                if ids and table in known:
                    db.execute(f"DELETE FROM {table} WHERE conversation_id IN ({marks})", ids)
    finally:
        db.close()
