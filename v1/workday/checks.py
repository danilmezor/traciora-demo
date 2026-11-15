"""python v1/workday/checks.py --cfg en|ru --client-id ID [--at 'YYYY-MM-DD HH:MM']: what depends on the build day,
compared with the plan seeder.core.workday gives for the T in force (default: the shop database's build): which cards
exist, each card's column, owner, deadline and timeline (verbs and authors in order, the first line at its creation),
the board's open cards by owner, the two operators' unread Updates from this step's rows against inbox.json read
through the product's tray, the clock-ins at T, the stocktake day, slot 21's cover, the deadlines the product gives a
hand-over and S16-review's. Runs in the product's Python with the seed checkout on PYTHONPATH. Prints
`WORKDAY <cfg> PASS ...`, or `WORKDAY <cfg> FAIL ...` and one line per reason."""
import argparse
import datetime as dt
import os
import sys

from seeder import clock, manifest
from seeder.core import workday


def lines_of(card, st):
    """The timeline the plan gives a card: (instant, verb, actor), the attached file excepted."""
    return [(s["when"], s["verb"], st.actor(s["by"])) for s in card["trail"] if s["verb"] != "attached"]


def main():
    parser = argparse.ArgumentParser(prog="v1/workday/checks.py")
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--client-id", default="demo")
    parser.add_argument("--at", help="the build instant on the home clock (default: the shop database's)")
    args = parser.parse_args()
    from traciora.core.core_db.engine import connect, tenant_dsn
    from traciora.core.queries.scope import Scope
    from traciora.core.queries.work_board import my_activity
    from traciora.core.security import tenant_binding
    from traciora.core.tools.utilities.escalation_tools import _deadline

    cfg = args.cfg
    os.environ["SEED_AT"] = args.at or manifest.read(manifest.shop_dsn(args.client_id))["asked"]
    a = clock.anchors(cfg, manifest.at())
    p = workday.plan(cfg, a)
    c, wrong = p["clock"], []
    tenant = tenant_binding.for_client(args.client_id)
    with tenant_binding.bound(tenant), connect(tenant_dsn(args.client_id)) as conn:
        st = workday.Store(conn, cfg)
        planned = {st.id("card", x["key"]): x for x in p["cards"]}
        held = {str(r[0]): r for r in conn.execute(
            "select wi.id, ws.state_group, wi.owner_id::text, wi.location_id::text, wi.due_local, wi.due_tz, wi.created_at"
            " from work.work_item wi join work.work_state ws on ws.id = wi.state_id where wi.id = any(%s::uuid[])",
            (workday.keys(cfg)["card"],)).fetchall()}
        wrong += [f"card {x['key']} absent" for cid, x in planned.items() if cid not in held]
        wrong += [f"card {cid} present, not in the plan for this T" for cid in held if cid not in planned]
        open_by, lines = {}, 0
        for cid, card in planned.items():
            if cid not in held:
                continue
            _, group, owner, site, due_local, due_tz, created = held[cid]
            state, who, due = card["first"], None, card["due"]
            for s in card["trail"]:
                state = "completed" if s["verb"] == "completed" else s["to"] if s["verb"] == "moved" else state
                who = st.person(s["to"]) if s["verb"] == "assigned" else who
                due = s["due"] if s["verb"] == "rescheduled" else due
            if (group, owner, site, (due_local, due_tz) if due_local else None) != (state, who, st.sites[card["site"]], due):
                wrong.append(f"card {card['key']}: {group} {owner} {due_local} {due_tz}, plan {state} {who} {due}")
            told = sorted(tuple(r) for r in conn.execute("select occurred_at, verb, actor_id::text from platform.activity"
                                                          " where subject_type = 'work_item' and subject_id = %s", (cid,)))
            want = sorted(lines_of(card, st))
            if told != want or not told or told[0][0] != created:
                wrong.append(f"card {card['key']}: timeline {[r[1] for r in told]}, plan {[x[1] for x in want]}")
            lines += len(told)
            if state not in ("completed", "cancelled") and who:
                open_by[who] = open_by.get(who, 0) + 1
        board = dict(conn.execute("select wi.owner_id::text, count(*) from work.work_item wi join work.work_state ws on ws.id = wi.state_id"
                                  " where wi.id = any(%s::uuid[]) and ws.state_group not in ('completed', 'cancelled')"
                                  " and wi.owner_id is not null group by 1", (list(planned),)).fetchall())
        if board != open_by:
            wrong.append(f"board open by owner {board}, plan {open_by}")

        cards = list(planned)
        events = [st.id("calendar", f"{s['key']}:{row['key']}") for s in p["series"] for row in s["rows"]] + [st.id("calendar", e["key"]) for e in p["entries"]]
        shifts = [st.id("shift", x["key"]) for x in p["roster"]["shifts"]]
        unread = {}
        for side in ("junior", "senior"):
            slot = p["inbox"][side]["slot"]
            person = st.person(slot)
            login = conn.execute("select id::text from identity.login where person_id = %s", (person,)).fetchone()[0]
            scope = Scope(actor_id=st.actor(slot), purpose="display", actor_kind="person", login_id=login, date_to=c.T)
            with tenant_binding.at(c.t):
                tray = my_activity(conn, scope, person_id=person, plans=side == "senior", limit=200)
            ours = {r[0] for r in conn.execute(workday.LINES, {
                "p": person, "actor": st.actor(slot), "cards": cards, "events": events, "shifts": shifts, "today": c.T.isoformat(),
                "until": c.T.isoformat(), "sites": list(st.sites.values()), "fix": p["roster"]["fix"], "plans": side == "senior"}).fetchall()}
            pushed = {f"punch_fix:{x}" for x in workday.keys(cfg)["punch_fix"]}
            got = {x["id"] for x in tray["items"] if x["kind"] == "inform" and not x["read"] and (x["id"] in ours or x["id"] in pushed)}
            want = workday.unread(st, p, side) | ({f"punch_fix:{x}" for x in workday.keys(cfg)["punch_fix"]} if side == "senior" else set())
            if got != want:
                wrong.append(f"{side} unread updates: {len(got)} ({sorted(got - want)[:3]} extra, {sorted(want - got)[:3]} missing)")
            unread[side] = len(got)

        clocked = {str(r[0]) for r in conn.execute("select shift_id from workforce.punch where log_type = 'in' and shift_id = any(%s::uuid[])", (shifts,))}
        due_in = [x for x in p["roster"]["shifts"] if x["slot"] and x["status"] == "published" and not x["cancel"]
                  and x["start"].replace(tzinfo=c.zone(x["site"])) <= c.t < x["end"].replace(tzinfo=c.zone(x["site"]))]
        for x in due_in:
            if (st.id("shift", x["key"]) in clocked) == x["late"]:
                wrong.append(f"shift {x['key']}: {'clocked in' if x['late'] else 'no clock-in'} at T")
        late = [x["slot"] for x in due_in if x["late"]]
        for key, end in conn.execute("select id::text, end_local from workforce.shift where id = any(%s::uuid[]) and business_day = %s",
                                     (shifts, a["stocktake"])):
            if end.time() > dt.time(12):
                wrong.append(f"stocktake shift {key} ends at {end:%H:%M}")
        for x in p["roster"]["shifts"]:
            if x.get("covered"):
                row = conn.execute("select s.start_local, rp.published_at, rp.range_start, rp.range_end from workforce.shift s"
                                   " join workforce.roster_publish rp on rp.id = s.roster_publish_id where s.id = %s", (st.id("shift", x["key"]),)).fetchone()
                held_21 = conn.execute("select count(*) filter (where status <> 'cancelled') from workforce.shift where person_id = %s"
                                       " and business_day = %s and id <> %s", (st.person("21"), x["day"], st.id("shift", x["key"]))).fetchone()[0]
                if row is None or row[0] != x["covered"].replace(tzinfo=None) or row[1] != x["covered"] or not row[2] <= x["day"] <= row[3] or held_21:
                    wrong.append(f"cover {x['key']}: {row}, other live shifts that day {held_21}")
        for cid, card in planned.items():
            if card["origin"] == "model" and cid in held:
                due = _deadline(conn, st.sites[card["site"]], held[cid][6], tenant)
                rescheduled = conn.execute("select old_value_public ->> 'due_local' from platform.activity where subject_id = %s and verb = 'rescheduled'",
                                           (cid,)).fetchone()
                given = (dt.datetime.fromisoformat(rescheduled[0]), held[cid][5] or due[1]) if rescheduled else (held[cid][4], held[cid][5])
                if given != due:
                    wrong.append(f"hand-over {card['key']} due {given}, the product's {due}")
        review = st.id("card", "S16-review")
        if review in held and held[review][4] != dt.datetime.combine(a["s16_due"], dt.time(12)):
            wrong.append(f"S16-review due {held[review][4]}, want {a['s16_due']} 12:00")
    print(f"WORKDAY {cfg} {'FAIL' if wrong else 'PASS'} T={c.t:%Y-%m-%d %H:%M} cards={len(held)}/{len(planned)} lines={lines}"
          f" open={sum(open_by.values())} unread=junior:{unread['junior']},senior:{unread['senior']} clocked_in={len(due_in) - len(late)}"
          f" late={','.join(late) or '-'}")
    for reason in wrong:
        print(f"  {reason}")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
