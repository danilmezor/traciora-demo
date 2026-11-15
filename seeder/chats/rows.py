"""The story chats of `v1/conversations/<cfg>/` as the rows Chatwoot v4.18.0 and the product hold for them, without a
database: `build` maps each file to its Chatwoot rows (contact, contact inbox, conversation, messages, label taggings,
resolution events), its `bridge_threads` row and the draft history the product's store replays. `who` names what the
product made: Chatwoot's ids for the inboxes, the bot and each slot's agent, the names its activity lines carry.

The mapping, seed field to column (conversations/DESIGN.md section 1, read against Chatwoot's code at v4.18.0):
- An instant is `day` (the clock's anchor of the file) at `at` on the shop clock the file names, stored in UTC.
- Ids are `BASE` + rank: conversations and contact inboxes by opening, contacts by first chat, messages, taggings and
  events by time, so ids follow time as Chatwoot's do. A conversation's `uuid` is `ids.uuid("conversation", n, cfg)`.
- A web visitor's subject and visit are the seed's own: the files' placeholders become `ids` values (rule 6).
- Columns Chatwoot derives are derived as it does: `waiting_since` is set at creation and by a customer line when
  empty, cleared by a public reply of a person or the bot and by a resolution; `first_reply_created_at` is a person's
  first public reply; `last_activity_at` is the last message, activity lines included; `status_changed_at` the last
  status change; `priority` the level the product last wrote (normal is Chatwoot's medium); `agent_last_seen_at` leaves
  the file's unread count of customer lines after it; `cached_label_list` the labels at T, joined as acts-as-taggable
  does. An activity line is Chatwoot's English or account-locale sentence for the fact, written for the user whose token
  made the change in the product: the service administrator for priority, hand-off labels and reopening, the manager
  for their own reply's assignment and labels and for a resolution, `system` for the silent days.
- A resolution writes `conversation_resolved` with the assignee of that moment, as Chatwoot's listener does.
- Lines of one instant (a hand-off's note, label and status) are a microsecond apart, as Chatwoot's are by their own
  clock: its message pages are cut by `created_at`, and a tie at a cut drops a line.
- Files are pool keys without bytes (v1 has no pool), so no attachment row is written: a line keeps its text, and a line
  that is only a file is not loaded, since an empty bubble is worse than no line."""
import base64
import datetime as dt
import importlib.util
import re
from zoneinfo import ZoneInfo

from seeder import clock, ids, inputs

BASE = 100000
UTC = dt.timezone.utc
CHATWOOT_LEVEL = {"low": "low", "normal": "medium", "high": "high", "urgent": "urgent"}  # account_api.OURS_TO_CHATWOOT
PRIORITY = {"low": 0, "medium": 1, "high": 2, "urgent": 3}
STATUS = {"open": 0, "resolved": 1, "pending": 2, "snoozed": 3}
# Chatwoot's config/locales/en.yml, conversations.activity, at v4.18.0
SAID = {"self_assigned": "{user} self-assigned this conversation", "assigned": "Assigned to {to} by {user}",
        "label_added": "{user} added {labels}", "label_removed": "{user} removed {labels}",
        "priority_added": "{user} set the priority to {new}", "priority_updated": "{user} changed the priority from {old} to {new}",
        "open": "Conversation was reopened by {user}", "resolved": "Conversation was marked resolved by {user}",
        "auto_resolved_days": "Conversation was marked resolved by system due to {count} days of inactivity"}
OWN_TEXT = re.compile(r"\(n \d+\)")  # a discarded draft's reason naming the message the person wrote instead


def thresholds():
    """The designed priority thresholds in working minutes (first high, first urgent, later high, later urgent) the files'
    priority lines were derived with: `THRESHOLDS` of conversations/build/convlib.py."""
    spec = importlib.util.spec_from_file_location("convlib", inputs.SEED / "conversations" / "build" / "convlib.py")
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    return (*lib.THRESHOLDS["first"], *lib.THRESHOLDS["later"])


def subject(cfg, peer):
    """A web visitor's browser subject: 22 url-safe characters, as `secrets.token_urlsafe(16)` makes them."""
    return base64.urlsafe_b64encode(ids.uuid("web-visitor", peer, cfg).bytes).decode().rstrip("=")


def identity(cfg, c):
    """(peer id, thread key, contact identifier) of a file's conversation; a web chat's are the seed's own."""
    slug = c["bridge"].split(":")[0]
    peer, thread = c["peer"]["id"], c["thread_key"]
    if slug == "chat":
        peer, thread = subject(cfg, peer), str(ids.uuid("web-visit", thread, cfg))
    return peer, thread, f"{slug}_{peer}"  # bridge.contact_identifier for the account "default"


def identifiers():
    """Every contact identifier of both configurations' files."""
    return sorted({identity(cfg, f["conversations"][0])[2] for cfg in ("en", "ru") for f in inputs.STORY_FILES["conversations", cfg].values()})


def uuids():
    return [str(ids.uuid("conversation", n, cfg)) for cfg in ("en", "ru") for n in inputs.STORY_FILES["conversations", cfg]]


def build(cfg, at, who):
    """The rows of every story chat of `cfg` at the build instant `at`. `who`: `account`, `inboxes` (name: id), `bot`,
    `users` (slot: (Chatwoot user id, name)), `service` (the service administrator's name), `resolve_days`."""
    a = clock.anchors(cfg, at)
    zones = {p["key"]: ZoneInfo(p["tz"]) for p in inputs.load(f"tenant/roles-and-places.{cfg}.json")["places"]}
    home = ZoneInfo(inputs.value("geo.home_zone", cfg))
    t_end = a["T"].replace(tzinfo=home).astimezone(UTC).replace(tzinfo=None)
    chats = [read(n, f, cfg, a["conversations"][n]["days"], zones, who) for n, f in inputs.STORY_FILES["conversations", cfg].items()]
    late = [f"{c['n']}: {when}" for c in chats for when in [max(m["created_at"] for m in c["messages"])] if when > t_end]
    if late:
        raise SystemExit("story chats with a line after T: " + ", ".join(late))
    chats.sort(key=lambda c: (c["created_at"], c["n"]))
    contacts = {}
    for rank, c in enumerate(chats, 1):
        c["id"] = BASE + rank
        contact = contacts.setdefault(c["identifier"], {"id": BASE + len(contacts) + 1, "name": c["contact_name"], "identifier": c["identifier"],
                                                        "created_at": c["created_at"], "last_activity_at": None})
        c["contact_id"] = contact["id"]
        for m in c["messages"]:
            if m["sender_type"] == "Contact":
                m["sender_id"] = contact["id"]
        heard = [m["created_at"] for m in c["messages"] if m["message_type"] == 0]
        contact["last_activity_at"] = max([x for x in (contact["last_activity_at"], *heard) if x], default=None)
    messages = sorted(((m["created_at"], c["id"], i, m | {"conversation_id": c["id"]}) for c in chats for i, m in enumerate(c["messages"])),
                      key=lambda x: x[:3])
    taggings = sorted(((t, c["id"], label) for c in chats for label, t in c["tagged"].items()), key=lambda x: x[:2])
    events = sorted((e | {"conversation_id": c["id"], "inbox_id": c["inbox_id"]} for c in chats for e in c["resolutions"]),
                    key=lambda e: (e["created_at"], e["conversation_id"]))
    return {"chats": chats, "contacts": list(contacts.values()),
            "messages": [m | {"id": BASE + i} for i, (*_, m) in enumerate(messages, 1)],
            "taggings": [{"id": BASE + i, "created_at": t, "conversation_id": cid, "label": label} for i, (t, cid, label) in enumerate(taggings, 1)],
            "events": [e | {"id": BASE + i} for i, e in enumerate(events, 1)], "T": t_end, "day": a["T"].date()}


def read(n, f, cfg, days, zones, who):
    """One file's conversation: its columns, messages, label taggings, resolutions, thread and drafts."""
    (c,) = f["conversations"]
    zone, slug = zones[c["clock"].split()[0]], c["bridge"].split(":")[0]
    peer, thread, identifier = identity(cfg, c)
    service = who["service"]

    def when(e):
        local = dt.datetime.combine(days[e["day"]], dt.time.fromisoformat(e["at"]), zone)
        return local.astimezone(UTC).replace(tzinfo=None)

    def user(slot):
        return who["users"][str(slot)]

    def name(by):
        return service if by == "service" else user(by)[1]

    opened = when(c["opened"])
    state = {"status": c["opened"]["status"], "changed": opened, "waiting": opened, "first_reply": None, "assignee": None,
             "priority": None, "last_customer": None, "labelled": False}
    labels, tagged, messages, resolutions, drafts, owners = [], {}, [], [], [], []
    last = opened

    def line(t, content, sender_type=None, sender_id=None, message_type=2, private=False, attributes=None, source=None):
        if messages and t <= messages[-1]["created_at"]:  # Chatwoot pages by created_at: lines of one second keep their order
            t = messages[-1]["created_at"] + dt.timedelta(microseconds=1)
        messages.append({"content": content, "message_type": message_type, "private": private, "sender_type": sender_type,
                         "sender_id": sender_id, "source_id": source, "content_attributes": attributes or {}, "created_at": t})
        return t

    def status(t, to, content):
        t = line(t, content, attributes={"activity": {"type": "conversation_status_changed", "status": to}})
        state["status"], state["changed"] = to, t
        if to == "resolved":  # the listener's value: whole seconds from the chat's creation
            state["waiting"] = None
            resolutions.append({"created_at": t, "user_id": state["assignee"], "start": opened,
                                "value": int(t.replace(tzinfo=UTC).timestamp()) - int(opened.replace(tzinfo=UTC).timestamp())})

    def label(t, title, added, by):
        state["labelled"] = True
        t = line(t, SAID["label_added" if added else "label_removed"].format(user=by, labels=title))
        if added:
            labels.append(title)
            tagged[title] = t
        else:
            labels.remove(title)
            tagged.pop(title)

    for e in c["timeline"]:
        if e["kind"] == "outside":
            continue
        t = when(e)
        if t < last:
            raise SystemExit(f"conversation {n} ({cfg}): line {e['n']} is earlier than the line before it")
        last = t
        kind = e["kind"]
        if kind == "message" and not e["text"]:
            continue  # only a file, and v1 has no pool
        if kind == "message":
            text = e["text"]
            if e["from"] == "customer":
                if state["status"] == "resolved":
                    raise SystemExit(f"conversation {n} ({cfg}): customer line {e['n']} on a resolved chat with no reopening")
                key = f"{n}/{e['n']}"
                mid = f"{thread}:{ids.uuid('message', key, cfg)}" if slug == "chat" else str(ids.number("message", key, cfg, bits=52))
                t = line(t, text, "Contact", None, 0, source=f"{slug}:default:{mid}#0")  # bridge.source_id
                state["waiting"] = state["waiting"] or t
                state["last_customer"] = t
            elif e["from"] == "assistant":
                line(t, text, "AgentBot", who["bot"], 1)
                state["waiting"] = None
            else:
                t = line(t, text, "User", user(e["slot"])[0], 1)
                state["first_reply"] = state["first_reply"] or t
                state["waiting"] = None
        elif kind == "note":
            line(t, e["text"], *(("User", user(e["slot"])[0]) if e.get("slot") else ("AgentBot", who["bot"])), 1, True)
        elif kind == "handoff":
            note = e["note"]
            line(t, note["text"], "AgentBot", who["bot"], 1, True)
            label(t, e["label_added"], True, service)
            if e["status"] != "pending -> open":
                raise SystemExit(f"conversation {n} ({cfg}): hand-off {e['n']} moves the status {e['status']}")
            status(t, "open", SAID["open"].format(user=service))
        elif kind == "draft":
            drafts.append({"n": e["n"], "text": e["text"], "at": t, "outcome": e["outcome"] and {
                "kind": e["outcome"]["kind"], "at": when(e["outcome"]), "slot": e["outcome"]["by"],
                "own_text": bool(OWN_TEXT.search(e["outcome"].get("because") or ""))}})
        elif e["what"] == "assigned":
            state["assignee"] = user(e["to"])[0]
            said = SAID["self_assigned"] if e["by"] == e["to"] else SAID["assigned"]
            owners.append((e["to"], line(t, said.format(user=name(e["by"]), to=user(e["to"])[1]))))
        elif e["what"] in ("label_added", "label_removed"):
            label(t, e["label"], e["what"] == "label_added", name(e["by"]))
        elif e["what"] == "priority":
            old, new = state["priority"], CHATWOOT_LEVEL[e["to"]]
            if new != old:
                line(t, SAID["priority_updated" if old else "priority_added"].format(user=service, old=old, new=new))
                state["priority"] = new
        elif e["what"] == "reopened":
            status(t, "open", SAID["open"].format(user=service))
        elif e["what"] == "resolved":
            status(t, "resolved", SAID["resolved"].format(user=name(e["by"])) if e.get("by") else
                   SAID["auto_resolved_days"].format(count=who["resolve_days"]))
        else:
            raise SystemExit(f"conversation {n} ({cfg}): no Chatwoot line for the activity {e['what']}")

    at_t = c["state_at_t"]
    wanted = {"status": at_t["status"], "owner": at_t.get("owner"), "labels": sorted(at_t["labels"]),
              "waiting": when(at_t["waiting_since"]) if at_t.get("waiting_since") else None}
    found = {"status": state["status"], "owner": owners[-1][0] if owners else None, "labels": sorted(labels), "waiting": state["waiting"]}
    differ = [f"{k}: file {wanted[k]}, lines {found[k]}" for k in wanted if wanted[k] != found[k]]
    shown = CHATWOOT_LEVEL[at_t["priority"]["shown"]]
    if (state["priority"] or "medium") != shown:
        differ.append(f"priority: file {shown}, lines {state['priority']}")
    if differ:
        raise SystemExit(f"conversation {n} ({cfg}): its state at T differs from its lines: " + "; ".join(differ))
    heard = [m["created_at"] for m in messages if m["message_type"] == 0]
    unread = at_t.get("unread") or 0
    seen = max((m["created_at"] for m in messages if m["created_at"] < heard[-unread]), default=opened) if unread else messages[-1]["created_at"]
    return {"n": n, "uuid": str(ids.uuid("conversation", n, cfg)), "source_id": str(ids.uuid("contact-inbox", n, cfg)),
            "pubsub_token": ids.uuid("pubsub", n, cfg).hex[:24], "inbox": c["inbox"], "inbox_id": who["inboxes"][c["inbox"]],
            "bridge": c["bridge"], "thread_key": thread, "peer_id": peer, "identifier": identifier, "contact_name": c["contact"]["name"],
            "created_at": opened, "status": state["status"], "status_changed_at": state["changed"], "assignee_id": state["assignee"],
            "owner": owners[-1] if owners else None, "base_priority": at_t["priority"]["base"],
            "priority": PRIORITY.get(state["priority"]), "waiting_since": state["waiting"], "first_reply_created_at": state["first_reply"],
            "last_activity_at": messages[-1]["created_at"], "agent_last_seen_at": seen, "cached_label_list": ", ".join(labels) if state["labelled"] else None,
            "custom_attributes": avito(c), "last_customer_at": state["last_customer"], "messages": messages, "tagged": tagged,
            "resolutions": resolutions, "drafts": drafts, "draft_waiting": bool(at_t.get("draft_in_box"))}


def avito(c):
    """An Avito chat's listing, as the bridge sets it on the conversation (`_extract_ad_context` and the chat type)."""
    x = c.get("listing_context")
    if not x:
        return {}
    return {"source_channel": "Avito", "item_id": x["item_id"], "item_title": x["title"], "item_url": x["url"], "chat_type": c["thread_key"].split("-")[0]}
