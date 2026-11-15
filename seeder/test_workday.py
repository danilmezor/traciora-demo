"""The workday step's mapping of `workday/<cfg>/` at the nominal T, without a database: every file is read through
`seeder.core.workday.plan` and gives the counts workday/DESIGN.md states. Runs in the product's Python (the series rule
is the product's `commands.work.occurrences`)."""
import datetime as dt

import pytest

from seeder import clock, inputs
from seeder.core import workday

NOMINAL = dt.datetime(2026, 11, 13, 10, 30)
ENTRIES = {"en": 21, "ru": 15}
ROTA_LINES = {"en": 5, "ru": 4}  # DESIGN.md section 4: the junior's shifts of next week, one line a shift


@pytest.mark.parametrize("cfg", ["ru", "en"])
def test_files_map(cfg):
    p = workday.plan(cfg, clock.anchors(cfg, NOMINAL))
    texts = [x[k] for x in p["cards"] for k in ("title", "description", "why_now", "origin_ref") if x[k]]
    texts += [s["body"] for x in p["cards"] for s in x["trail"] if s.get("body")]
    texts += [s["title"] for s in p["series"]] + [r["description"] for s in p["series"] for r in s["rows"] if r["description"]]
    texts += [e["title"] for e in p["entries"]] + [e["description"] for e in p["entries"] if e["description"]]
    assert len(inputs.load(f"workday/{cfg}/cards.json")["cards"]) == 26
    assert [x["key"] for x in p["cards"]] == [x["id"] for x in inputs.load(f"workday/{cfg}/cards.json")["cards"] if x["id"] != "H-east-waiting"]
    assert p["skipped"] == ["H-east-waiting: no seed file holds {visitor_name}"]
    assert not [t for t in texts if "{" in t]
    assert len(p["series"]) == 8 and all(s["rows"] for s in p["series"])
    assert len(p["entries"]) == ENTRIES[cfg]
    roster = p["roster"]
    assert [(q["key"], q["slot"], q["kind"]) for q in roster["requests"]] == [("R50", "16", "remove"), ("R51", "16", "remove")]
    published = {x["key"]: x for x in roster["shifts"] if x["status"] == "published"}
    assert all(q["shift"] in published for q in roster["requests"])
    assert sum(1 for x in roster["shifts"] if x["slot"] is None) == 1
    junior, senior = p["inbox"]["junior"], p["inbox"]["senior"]
    assert sum(1 for x in roster["shifts"] if x["slot"] == str(junior["slot"]) and x["week"] == 1 and x["status"] == "published") == ROTA_LINES[cfg]
    assert junior["counts"] == {"needs": 2, "update_items": 7, "update_lines": 6 + ROTA_LINES[cfg]}
    assert senior["counts"] == {"needs": 9, "update_items": 2, "update_lines": 2}
    assert sum(1 for x in junior["lines"] if x["half"] == "needs") == 2 and sum(1 for x in senior["lines"] if x["half"] == "needs") == 9
