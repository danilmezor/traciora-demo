"""The Russian story calls read through the calls step's mapping, on the nominal dates their files were written for, and
grouped by the product's own call-log rule: nothing is written. Runs in the product's environment."""
import datetime as dt

from traciora.core.phonecalls.ingestion import call_log

from seeder import inputs
from seeder.core import calls as step


def test_the_russian_calls_map_to_the_counts_the_design_states():
    files = inputs.STORY_FILES[("calls", "ru")]
    built = {"calls": {str(n): {"day": d["call"]["nominal_date"]} for n, d in files.items()}, "stories": {}}
    found = step.calls("ru", built)
    legs = {n: x for n, _, _, x in found}
    shops = step.places("ru")
    group = {key: next(x["ext"] for x in p["extensions"] if x.get("slot") is None) for key, p in shops.items()}
    desks = {key: {x["ext"] for x in p["extensions"]} for key, p in shops.items()}

    assert len(found) == 36
    assert sum(len(x) for x in legs.values()) == 49
    misses = {n: x for n, x in legs.items() if all(leg.status == "no_answer" for leg in x)}
    morning = legs[16][1:]
    assert sorted(misses) == [18, 19, 20]
    for x in [*misses.values(), morning]:
        assert [leg.ring_s for leg in x] == [20, 15, 15, 15] and {leg.rang for leg in x[1:]} == {"301", "302", "303"}
        assert {leg.started_at - x[0].started_at for leg in x[1:]} == {dt.timedelta(seconds=20)}
    assert morning[0].rang == "302" and morning[0].started_at.strftime("%H:%M") == "10:05"
    assert morning[0].started_at.date() == legs[16][0].started_at.date() and morning[0].caller == legs[16][0].caller
    for n, d, _, x in found:
        assert {leg.rang for leg in x} <= desks[d["call"]["site"]]
        assert all((leg.caller if leg.kind == "outbound" else leg.dialled) == group[d["call"]["site"]] for leg in x)
    assert len({leg.dialled if leg.kind == "outbound" else leg.caller for x in legs.values() for leg in x}) == 28
    assert all(len(leg.caller if leg.kind != "outbound" else leg.dialled) == 11 for x in legs.values() for leg in x)

    grouped, waiting = call_log.group([leg for x in legs.values() for leg in x], now=dt.datetime(2027, 1, 1, tzinfo=dt.timezone.utc),
                                      internal_digits=step.Log.internal_digits, menu_line=None)
    assert (len(grouped), waiting) == (37, [])
    assert sum(c.missed for c in grouped) == 4 and sum(c.direction == "outbound" for c in grouped) == 2

    spoken = [d for _, d, _, _ in found if d.get("transcript")]
    assert len(spoken) == 33
    for d in spoken:
        text, segments = step.dialogue(d, {"manager": "manager", "customer": "customer"})
        assert len(text.splitlines()) == len(segments) and [s["sequence"] for s in segments] == list(range(len(segments)))
        assert {s["speaker_label"] for s in segments} <= {"manager", "customer"}
    verdicts = [d["verdict"] for d in spoken]
    assert sum(v["score"] is not None for v in verdicts) == 26
    assert sorted(d["number"] for d in spoken if not d["verdict"]["result_public"]["judged"]) == [8, 11]
