"""The assistant step's mapping reads every file of `assistant/<cfg>/` into the rows DESIGN.md counts, for both
configurations, writing nothing: every computed slot resolves through a query of metrics.sql (here a stand-in reader
that gives each metric a fixed value) and renders in its format, no text it would write carries a template, what it
holds back is counted with its reason, every wording of every item renders or is held for a ruled reason, and every
query of metrics.sql is read by one of them. Each slot stands in
with ids of its own and no shifts. Needs the product on the path (run it in the install's Python)."""
import datetime as dt
import json
from collections import Counter
from decimal import Decimal
from functools import cache
from zoneinfo import ZoneInfo

import pytest

from seeder import assistant, clock, ids, inputs

AT = dt.datetime(2026, 11, 13, 10, 30)
ROWS = {"rows.advisor": [{"key": 11, "name": "Advisor One"}, {"key": 12, "name": "Advisor Two"}],
        "rows.order": [{"key": 1, "site": "Shop", "advisor": "Advisor One", "date": dt.date(2026, 11, 4), "customer": "Customer", "approver": None}],
        "rows.account": [{"key": 5, "name": "Account"}],
        "rows.gap": [{"key": "band", "site": "Shop", "site_id": "site", "position": "Position", "starts": dt.time(7, 30), "ends": dt.time(10), "short": 1}]}


@cache
def build(cfg):
    ladder = inputs.load("tenant/ladder.json")
    ranks = {x["key"]: x["rank"] for x in ladder["access_levels"]["levels"]}
    zone = ZoneInfo(inputs.value("geo.home_zone", cfg))
    who = {s["slot"]: {"login": str(ids.uuid("login", s["slot"], cfg)), "actor": str(ids.uuid("actor", s["slot"], cfg)), "account": n,
                       "rank": ranks[s["rank"]], "zone": zone, "shifts": []}
           for n, s in enumerate((s for s in ladder["slots"] if s["rank"] != "none"), 1)}
    who["agent"] = {"actor": str(ids.uuid("actor", "agent", cfg))}
    asked = Counter()

    def measure(metric, variables, many=False):
        asked[metric] += 1
        if many:
            return ROWS[metric]
        return {"calls.oldest_waiting": dt.datetime(2026, 11, 12, 15, 5, tzinfo=dt.timezone.utc), "bookings.first": "08:00|Customer|Brakes",
                "roster.free_people": "", "calls.worst_check": "recap", "calls.best_check": "greeting"}.get(metric, Decimal("3.456"))

    slots = [s["slot"] for s in ladder["slots"]] + ["F1"]
    found = {store: {"sites": {k: str(n) for n, k in enumerate(("main", "east", "west"), 1)}, "people": {s: str(n) for n, s in enumerate(slots, 1)}}
             for store in ("erp", "core")}
    c = assistant.context(cfg, clock.anchors(cfg, AT), who, "test", zone, measure, found) | {"ranks": ranks}
    return c, assistant.records(c), asked


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_every_file_maps_to_the_counts_of_the_design(cfg):
    c, built, asked = build(cfg)
    want = {k: assistant.LEDGER[k]["value"] for k in ("ask.handwritten", "mem.personal_live", "mem.personal_ended", "mem.team_notes",
                                                      "mem.proposals", "sched.brief_jobs")}
    personal = Counter(r["state"] for r in built["notes"] if r["scope"] == "personal")
    business = [r for r in built["notes"] if r["scope"] == "business"]
    status = Counter(r["status"] for r in built["proposals"])
    level = {v: k for k, v in c["ranks"].items()}
    tasks = [j for j in built["jobs"] if not j["brief"]]
    briefs = [j for j in built["jobs"] if j["brief"]]
    held = {h["item"]: h for h in built["held"]}
    assert built["wrong"] == []
    assert all(h["kind"] in ("slice", "undefined", "not in v1", "words") and (h["kind"] != "words" or cfg == "ru") for h in built["held"]), built["held"]
    assert set(asked) <= set(assistant.QUERIES), set(asked) - set(assistant.QUERIES)
    auto = sum(1 for n in c["files"]["notes"]["notes"] if "auto" in n["source"])
    whole = [h for h in held.values() if h["item"].startswith("thread ") and h["loaded"] == "nothing"]
    assert len(built["threads"]) + len(whole) == want["ask.handwritten"] + auto
    assert all(t["payload"]["messages"][-1]["type"] == "AIMessage" for t in built["threads"])
    assert (personal["active"], personal["dormant"], personal["archived"]) == (
        want["mem.personal_live"]["active"], want["mem.personal_live"]["dormant"], want["mem.personal_ended"]["all"])
    assert (len(business), Counter(r["state"] for r in business), Counter(level[r["min_rank"]] for r in business)) == (
        want["mem.team_notes"]["all"], {"active": want["mem.team_notes"]["active"], "unverified": want["mem.team_notes"]["unverified"]},
        want["mem.team_notes"]["visible_from"])
    assert (len(built["proposals"]), status["approved"], status["rejected"], status["proposed"]) == (
        want["mem.proposals"]["all"], want["mem.proposals"]["approved"], want["mem.proposals"]["declined"] + want["mem.proposals"]["withdrawn"],
        want["mem.proposals"]["waiting"])
    not_made = [h["item"] for h in held.values() if h["item"].startswith("job ")]
    assert len(tasks) + sum(1 for h in not_made if not h.startswith("job brief-")) == len(inputs.value("s10.tasks", cfg))
    assert len(briefs) + sum(1 for h in not_made if h.startswith("job brief-")) == want["sched.brief_jobs"]
    assert all(dt.datetime.fromisoformat((j["runs"] or j.get("held"))[-1]["due_at"]) <= c["T"] for j in tasks)
    written = [built["threads"], [{k: r[k] for k in ("subject", "text", "why", "how_to_apply") if r.get(k)} for r in built["notes"] + built["proposals"]],
               [{k: j[k] for k in ("name", "prompt")} for j in built["jobs"]], [j["runs"] for j in built["jobs"]]]
    assert "{{" not in json.dumps(written, ensure_ascii=False, default=str)
    print(f"\nASSISTANT MAPPING {cfg} threads={len(built['threads'])} notes={sum(personal.values())} team={len(business)} "
          f"proposals={len(built['proposals'])} tasks={len(tasks)} briefs={len(briefs)} runs={sum(len(j['runs']) for j in built['jobs'])} "
          f"slots={len(built['resolved'])} metrics={len(set(asked))} held={len(built['held'])}")
    for h in built["held"]:
        print(f"  held {h['item']}: {h['kind']} {h['why']} (loaded: {h['loaded']})")


@cache
def every_wording(cfg):
    """Every text of every item rendered at T, whichever case or wording a build would pick: each task's prompt and
    every wording of every case, each brief point, each turn of each thread. Returns the kinds held back."""
    c, _, _ = build(cfg)
    c, f, held = c | {"resolved": []}, c["files"], []
    texts = ([(t["prompt"], None) for t in f["tasks"]["tasks"]]
             + [(w, t.get("blocks")) for t in f["tasks"]["tasks"] for wordings in t["cases"].values() for w in wordings]
             + [(p, None) for b in f["tasks"]["briefs"]["at_t"] for p in b["points"]]
             + [(turn[k], turn.get("blocks")) for t in f["threads"]["threads"] for turn in t["turns"] for k in ("user", "assistant")])
    for text, blocks in texts:
        try:
            assert "{{" not in assistant.fill(c, text, c["a"]["T"].date(), "every wording", c["T"], c["home"], blocks)
        except assistant.Held as why:
            held.append(why.kind)
    return Counter(held), len(texts)


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_every_wording_renders(cfg):
    """A build at another T may pick any case and wording: every one resolves or is held for a ruled reason."""
    held, n = every_wording(cfg)
    assert set(held) <= ({"slice", "undefined", "words"} if cfg == "ru" else {"slice", "undefined"}), held
    print(f"\nASSISTANT WORDINGS {cfg} texts={n} held={dict(held)}")


def test_every_query_is_read_by_a_loaded_item():
    """No query of metrics.sql is dead: each is read by some wording of an item of one configuration or the other."""
    read = set().union(*(build(cfg)[2] for cfg in ("en", "ru") if every_wording(cfg)))
    assert set(assistant.QUERIES) - read == set()


def test_formats():
    at = dt.datetime(2026, 3, 4, 13, 40, tzinfo=dt.timezone.utc)
    en = [(Decimal("11400"), "money0"), (Decimal("688"), "money"), (Decimal("21.94"), "pct"), (1, "n:car/cars"), (3, "n:car/cars"),
          (Decimal("3.25"), "score"), (at, "daytime"), (None, "int")]
    ru = [(Decimal("321360"), "money0"), (Decimal("15552"), "money"), (21, "n:день/дня/дней"), (22, "n:день/дня/дней"), (11, "n:день/дня/дней"),
          (at, "daytime"), (at, "since_daytime")]
    assert [assistant.value_text("en", v, f, ZoneInfo("America/New_York")) for v, f in en] == [
        "$11,400", "$688.00", "22 %", "1 car", "3 cars", "3.3", "Wednesday at 8:40 a.m.", "—"]
    assert [assistant.value_text("ru", v, f, ZoneInfo("Europe/Ulyanovsk")) for v, f in ru] == [
        "321 360 ₽", "15 552,00 ₽", "21 день", "22 дня", "11 дней", "в среду, 4 марта, в 17:40", "со среды, с 17:40"]
