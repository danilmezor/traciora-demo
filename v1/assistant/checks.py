"""python v1/assistant/checks.py --cfg en|ru [--client-id demo]: what the assistant step wrote outside the core database
equals what its mapping builds from the seed files, the loaded people and the loaded data (seeder/assistant.py `records`,
its metrics read again): auth.db's `conversations` rows and their chat files (read back through the product's
FileBasedMemory), the jobs (`cron_prompt_jobs`) with their prompts, the runs (`cron_runs`) with their answers and
instructions, and the readers' `brief_seen_at`; that nothing the mapping holds back is stored, and nothing is held back
but for a metric with no data in this slice, the loaded data contradicting it (NOT_IN_V1), or (with its note turns
loaded) a metric with no definition; that no stored text of the step (chat files, titles, prompts, answers,
instructions, the notes' and proposals' sealed texts) carries a template (`{{`); that every note's chat has its
`conversations` row; and that each resolved figure a ledger row states for the same population and window agrees with
it (`AGREES`). The core rows are proved by assistant/checks.sql. Runs in the product's Python, in the install's working
directory. Prints a `HELD` line per item held back, then `ASSISTANT <cfg> PASS ...` or `ASSISTANT <cfg> FAIL ...` with
one line per difference."""
import argparse
import contextlib
import datetime as dt
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from seeder import assistant, ids, inputs, manifest  # noqa: E402


def agreements(cfg, a, resolved):
    """Each resolved figure against the ledger row that states it for the same population and window: (what, holds)."""
    def got(item, slot):
        return [r for r in resolved if r["item"].startswith(item) and r["slot"].startswith("{{=" + slot + "|")]

    out = []
    for r in got("s2-cost#1", "leak.total"):  # the thread's expect
        total = inputs.value("s2.total", cfg)
        out.append((f"s2-cost leak.total {r['value']}: at most s2.total {total}, at least 85 % of it", 0.85 * total <= r["value"] <= total))
    for r in got("s2-discounts#3", "orders.on_walkin"):  # s2: b, every planted discount of F1 on the walk-in record (s2.walkin)
        discounted = got("s2-discounts#2", "orders.discounted")[0]["value"]
        out.append((f"s2-discounts orders.on_walkin {r['value']}: all {discounted} of F1's discounts", r["value"] == discounted))
    for metric, key in (("catalogue.list_price", "s8.price_now"), ("catalogue.price_at_old_hour", "s8.price_quoted")):
        for r in got("s8-prices-source#1", metric):
            out.append((f"s8-prices-source {metric} {r['value']}: {key} {inputs.value(key, cfg)}", r["value"] == inputs.value(key, cfg)))
    unapproved = got("discounts-over-10", "orders.discounted|site=all&min_over=10&approved=no")
    for r in unapproved:  # each Friday list shows the unapproved discounts of its week (s2.west.discounts_after)
        friday = r["at"].date()
        days = [d for d in a["s2_discounts"] if friday - dt.timedelta(friday.weekday()) <= d <= friday]
        out.append((f"discounts-over-10 of {friday}: {r['value']} unapproved, s2.west.discounts_after has {len(days)} that week", r["value"] == len(days)))
    if a["T"].weekday() == 4 and a["T"].time() < dt.time(16):  # eval record A.12 is asked on a Friday before that day's run
        out.append((f"discounts-over-10: {sum(1 for r in unapproved if r['value'])} runs show an unapproved discount, A.12 says two",
                    sum(1 for r in unapproved if r["value"]) == 2))
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--client-id", default="demo")
    args = parser.parse_args()
    from traciora.core.agents.agent_memory import FileBasedMemory
    from traciora.core.auth.manager import AuthManager
    from traciora.core.commands.memory import PCOL
    from traciora.core.memory.store import COL
    from traciora.core.security import envelope
    from traciora.core.tools.workspace.scheduled_tasks.tasks import read_stored_text

    os.environ["SEED_AT"] = manifest.read(manifest.shop_dsn(args.client_id))["asked"]
    with assistant.mapping(args.cfg, args.client_id) as (conn, c):
        own = assistant.own(args.cfg)
        sealed = [envelope.decrypt(v, COL[k]).decode() for row in conn.execute(
            "SELECT subject_enc, text_enc, why_enc, how_to_apply_enc FROM platform.memory WHERE id = ANY(%s::uuid[])", (own["memory"],))
            for k, v in zip(("subject", "text", "why", "how_to_apply"), row)]
        sealed += [envelope.decrypt(v, PCOL[k]).decode() for row in conn.execute(
            "SELECT subject_enc, text_enc, why_enc, how_to_apply_enc, reason_enc FROM platform.proposal WHERE id = ANY(%s::uuid[])", (own["proposals"],))
            for k, v in zip(("subject", "text", "why", "how_to_apply", "reason"), row) if v is not None]
        sources = [str(r[0]) for r in conn.execute("SELECT source_conversation_id FROM platform.memory WHERE id = ANY(%s::uuid[]) AND scope = 'personal'",
                                                    (own["memory"],))]
        built = assistant.records(c)
    auth, memory, wrong = AuthManager(), FileBasedMemory(), []
    held_threads = {str(ids.uuid("thread", h["item"].removeprefix("thread "), args.cfg)) for h in built["held"] if h["loaded"] == "nothing"}
    stored_texts = list(sealed)
    with contextlib.closing(sqlite3.connect(auth.db_path)) as db:
        db.row_factory = sqlite3.Row
        for t in built["threads"]:
            row = db.execute("SELECT * FROM conversations WHERE id = ?", (t["id"],)).fetchone()
            want = {k: t[k] for k in ("manager_id", "title", "created_at", "replied_at", "read_at")}
            if row is None or {k: row[k] for k in want} != want or row["title_set_by_person"] != 0 or row["subject_json"] is not None:
                wrong.append(f"conversation {t['id']}: {dict(row) if row else 'missing'}")
            path = memory._get_file_path(t["id"])
            stored = memory._read_payload_strict(path) if path.exists() else {}
            stored_texts += [row["title"] if row else "", json.dumps(stored.get("messages"), ensure_ascii=False)]
            # what the product adds on reading a thread (the model's context archive, a later save time) is its own
            mine = {k: v for k, v in stored.items() if k != "last_updated"} | {"metadata": {k: stored.get("metadata", {}).get(k) for k in t["payload"]["metadata"]}}
            if mine != {k: v for k, v in t["payload"].items() if k != "last_updated"}:
                wrong.append(f"chat file of {t['id']}: {'differs' if path.exists() else 'missing'}")
        jobs = runs = 0
        for job in built["jobs"]:
            row = db.execute("SELECT * FROM cron_prompt_jobs WHERE slug LIKE ? AND created_by = ? AND name = ?",
                             (job["slug"] + "%", job["owner"], job["name"])).fetchone()
            if row is None or row["cron_expr"] != job["cron_expr"] or read_stored_text(auth, row["prompt_text"]) != job["prompt"] or row["output_kind"] != "store":
                wrong.append(f"job {job['key']}: {'differs' if row else 'missing'}")
                continue
            jobs += 1
            stored_texts.append(read_stored_text(auth, row["prompt_text"]))
            if row["id"] != job["id"] and not job["brief"]:
                wrong.append(f"job {job['key']}: id {row['id']}, not {job['id']}")
            for r in job["runs"]:
                got = db.execute("SELECT * FROM cron_runs WHERE id = ?", (r["id"],)).fetchone()
                fields = {k: v for k, v in r.items() if k not in ("key", "id", "answer", "instruction")}
                if got is None or {k: got[k] for k in fields} != fields or got["task_slug"] != row["slug"] or got["owner_id"] != job["owner"] or (
                        "instruction" in r and (read_stored_text(auth, got["answer_enc"]) if got["answer_enc"] else None,
                                                read_stored_text(auth, got["instruction_enc"])) != (r["answer"], r["instruction"])):
                    wrong.append(f"run {r['id']} of {job['key']}: {'differs' if got else 'missing'}")
                else:
                    runs += 1
                    stored_texts += [read_stored_text(auth, got[k]) for k in ("answer_enc", "instruction_enc") if got[k]]
            if job["seen"] and auth.brief_seen(job["owner"]) != job["seen"]:
                wrong.append(f"brief_seen_at of {job['key']}: {auth.brief_seen(job['owner'])}, not {job['seen']}")
        for cid in held_threads:
            if db.execute("SELECT 1 FROM conversations WHERE id = ?", (cid,)).fetchone():
                wrong.append(f"conversation {cid} is stored, but held back")
        rows = {r[0] for r in db.execute(f"SELECT id FROM conversations WHERE id IN ({','.join('?' * len(sources))})", sources)}
    unlinked = [s for s in sources if s not in rows]
    if unlinked:
        wrong.append(f"{len(unlinked)} notes name a chat with no conversations row: {unlinked[:3]}")
    templated = sum(1 for text in stored_texts if "{{" in text)
    if templated:
        wrong.append(f"{templated} stored texts carry a template")
    for h in built["held"]:
        print(f"HELD {h['item']}: {h['kind']} {h['why']} (loaded: {h['loaded']})")
        if not (h["kind"] in ("slice", "not in v1") or h["kind"] == "undefined" and h["loaded"] == "its note turns alone"):
            wrong.append(f"{h['item']} is held back for a reason not ruled: {h['kind']} {h['why']}")
    agree = 0
    for what, holds in agreements(args.cfg, c["a"], built["resolved"]):
        agree += holds
        if not holds:
            wrong.append(f"differs: {what}")
    want = sum(len(j["runs"]) for j in built["jobs"])
    line = (f"threads={len(built['threads'])} jobs={jobs}/{len(built['jobs'])} runs={runs}/{want} "
            f"seen={sum(1 for j in built['jobs'] if j['seen'])} slots={len(built['resolved'])} agree={agree} "
            f"texts={len(stored_texts)} held={len(built['held'])} ({', '.join(h['item'] for h in built['held'])})")
    print(f"ASSISTANT {args.cfg} {'FAIL' if wrong else 'PASS'} {line}")
    for problem in wrong:
        print(f"  {problem}")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
