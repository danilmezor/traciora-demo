"""What proves the chats step beyond Chatwoot's tables (checks.sql has those): the product's auth.db and the levels the
product works from, against the files. Run with the install's Python, the install's environment loaded (as the step runs):
    python <seed>/v1/conversations/checks.py --cfg en|ru [--client-id demo]
Checks: per live chat the last priority line at or before T is the file's; the priority thresholds of T's date are the
designed ones; the draft outcomes count as the files' do; a draft waits exactly where a file says, with its words; one
bridge thread per chat, its bridge and the chat's inbox the file's; story S7's chats share one contact; owners and labels
at T are the files'. One line out: CHATS <cfg> PASS ... or FAIL with the reasons; exit 0 or 1."""
import argparse
import collections
import datetime as dt
import re
import sqlite3
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))  # the seed checkout, for seeder

from seeder import clock, ids, inputs, manifest  # noqa: E402
from seeder.chats import chatwoot_dsn, rows  # noqa: E402


def main():
    parser = argparse.ArgumentParser(prog="v1/conversations/checks.py")
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--client-id", default="demo")
    args = parser.parse_args()
    cfg = args.cfg
    from traciora.core.auth.manager import AuthManager
    from traciora.core.channels.chatwoot.agents import AgentStore
    from traciora.core.channels.chatwoot.conversations_store import ConversationStore

    a = clock.anchors(cfg, dt.datetime.strptime(manifest.read(manifest.shop_dsn(args.client_id))["asked"], manifest.FORMAT))
    t_end = a["T"].replace(tzinfo=ZoneInfo(inputs.value("geo.home_zone", cfg))).astimezone(rows.UTC).replace(tzinfo=None)
    files = {n: f for n, f in inputs.STORY_FILES["conversations", cfg].items()}
    with psycopg.connect(chatwoot_dsn()) as conn:
        held = {str(r[0]): r[1:] for r in conn.execute(
            "SELECT c.uuid, c.id, c.contact_id, c.assignee_id, c.cached_label_list, i.name FROM conversations c JOIN inboxes i ON i.id = c.inbox_id")}
        chats = {n: held.get(str(ids.uuid("conversation", n, cfg))) for n in files}
        levels = {n: [m[0] for m in conn.execute(
            "SELECT content FROM messages WHERE conversation_id = %s AND message_type = 2 AND content ~ ' the priority ' AND created_at <= %s"
            " ORDER BY created_at DESC LIMIT 1", (c[0], t_end))] for n, c in chats.items() if c}
    failed = [f"{n}: not in Chatwoot" for n, c in chats.items() if c is None]
    if failed:
        return report(cfg, failed, 0)
    auth = AuthManager()
    store, lite = ConversationStore(auth.db_path), sqlite3.connect(auth.db_path)
    agents = {x.manager_id: x.chatwoot_user_id for x in AgentStore(auth.db_path).all()}
    ladder = {s["slot"]: s for s in inputs.load("tenant/ladder.json")["slots"]}
    cids = [c[0] for c in chats.values()]
    marks = ",".join("?" * len(cids))
    threads = {r[0]: r[1] for r in lite.execute(f"SELECT conversation_id, bridge FROM bridge_threads WHERE conversation_id IN ({marks})", cids)}
    outcomes = collections.Counter(r[0] for r in lite.execute(f"SELECT outcome FROM draft_outcome WHERE conversation_id IN ({marks})", cids))
    wanted_outcomes = collections.Counter()

    def agent(slot):
        account = auth.get_manager_by_username(ladder[str(slot)][f"username_{cfg}"])
        return agents.get(int(account["id"])) if account else None

    for n, f in files.items():
        (c,) = f["conversations"]
        cid, contact, assignee, label_list, inbox = chats[n]
        at_t, timeline = c["state_at_t"], c["timeline"]
        drafts = {e["id"]: e for e in timeline if e["kind"] == "draft"}
        wanted_outcomes.update(e["outcome"]["kind"] for e in drafts.values() if e["outcome"])
        if at_t["status"] != "resolved":
            last = [e for e in timeline if e["kind"] == "activity" and e["what"] == "priority"][-1:]
            want = f" to {rows.CHATWOOT_LEVEL[last[0]['to']]}" if last else None
            got = re.search(r" to \w+$", levels[n][0]).group(0) if levels[n] else None
            if got != want:
                failed.append(f"{n}: last priority line before T ends '{got}', the file's '{want}'")
        box = store.draft(cid).text
        text = drafts[at_t["draft_in_box"]]["text"] if at_t.get("draft_in_box") else ""
        if box != text:
            failed.append(f"{n}: the reply box holds {box[:40]!r}, the file {text[:40]!r}")
        if threads.get(cid) != c["bridge"] or inbox != c["inbox"]:
            failed.append(f"{n}: thread {threads.get(cid)} in inbox {inbox}, the file {c['bridge']} in {c['inbox']}")
        if assignee != (agent(at_t["owner"]) if at_t.get("owner") else None):
            failed.append(f"{n}: assignee {assignee}, the file's owner slot {at_t.get('owner')}")
        if sorted(filter(None, (label_list or "").split(", "))) != sorted(at_t["labels"]):
            failed.append(f"{n}: labels {label_list!r}, the file's {at_t['labels']}")
    if outcomes != wanted_outcomes:
        failed.append(f"draft outcomes {dict(sorted(outcomes.items()))}, the files' {dict(sorted(wanted_outcomes.items()))}")
    if len(threads) != len(files):
        failed.append(f"{len(threads)} bridge threads for {len(files)} chats")
    s7 = {chats[n][1] for n, f in files.items() if f["story"] == "S7"}
    if len(s7) != 1 or sum(f["story"] == "S7" for f in files.values()) != 3:
        failed.append(f"story S7's chats on the contacts {sorted(s7)}")
    day = store.thresholds(a["T"].date())
    if day is None or (day.first_high, day.first_urgent, day.later_high, day.later_urgent) != rows.thresholds():
        failed.append(f"the thresholds of {a['T'].date()} are {day}, the designed {rows.thresholds()}")
    return report(cfg, failed, len(files), outcomes)


def report(cfg, failed, chats, outcomes=None):
    if failed:
        print(f"CHATS {cfg} FAIL " + "; ".join(failed))
        return 1
    print(f"CHATS {cfg} PASS chats={chats} threads={chats} outcomes=" + ",".join(f"{k}:{v}" for k, v in sorted(outcomes.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
