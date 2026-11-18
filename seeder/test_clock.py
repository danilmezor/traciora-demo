import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import pytest

from seeder import clock, inputs

sys.path.insert(0, str(inputs.SEED / "checks"))
import timeline_examples as tl  # noqa: E402

TUESDAY = dt.datetime(2026, 11, 10, 10, 30)
FUTURE = {"s16_block", "s16_due", "s16_meeting", "s14_open_shift", "stocktake", "week_off", "booking", "roster_end"}
RULE_A_ROWS = ("S13 stocktake, closed from 12:00", "S5 week off", "S16 block / due 12:00 / meeting 10:00")
RULE_A_CHECKS = {"stocktake on or after T's date", "week off on or after T's date", "conversation 08's chat <= booking < week off",
                 "booking within pub_week - 3 days to pub_week + 4 days"}


def j(*ds):
    return ", ".join(map(str, ds))


def rows(a):
    """The rows of timeline_examples.place, written from the clock's anchors."""
    s9 = a["s9_mondays"]
    return {
        "T": f"{a['T']:%a %Y-%m-%d %H:%M}", "W0": f"{a['W0']} to {a['W0'] + dt.timedelta(6)}",
        "ERP history starts (T-24 months, next full open day)": j(a["history_start"]), "west bought (T-14 months)": j(a["bought"]),
        "S2 begins: first full open day on or after T-335 d": j(a["s2_start"]), "F3 resigns: Mon W-30": j(a["f3_resigns"]),
        "A5 comebacks: Tue W-26, Tue W-22": j(*a["a5_comebacks"]), "G, go-live: T-175 d": j(a["G"]),
        "S9 series starts: first Monday on or after G": j(a["s9_first"]), "S2 found, owner's thread: 5th full open day after G": j(a["s2_found"]),
        "S2 follow-up thread: 5 more": j(a["s2_follow_up"]), "F1 fired: west's 15th full open day after G": j(a["fired"]),
        "discount rule page and team note: next day": j(a["rule_on"]), "P, price rise; A6's new contact: first Monday on or after T-150 d": j(a["P"]),
        "S1 call 21 (slot 5): Tue W-20; ru his first working day on or after": j(a["call21"]), "A5 last visit: Thu W-20": j(a["a5_last_visit"]),
        "A5 complaint call: Tue W-19": j(a["a5_complaint"]), "A5 three misses: +1, +6, +9 days": j(*a["a5_misses"]),
        "F2 fired: Mon W-17": j(a["f2_fired"]), "slot 14 starts: Mon W-15": j(a["slot14_starts"]), "slot 7 starts: Mon W-14": j(a["slot7_starts"]),
        "S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after": j(a["call23"], a["call24"]),
        "diagnostician's leave: Mon W-10 to Fri W-9": f"{a['leave_from']} to {a['leave_to']}",
        "S1 call 22 (slot 7): Tue W-9; ru his first working day on or after": j(a["call22"]), "S9 cancelled by the organiser": j(a["s9_cancelled"]),
        "S9 holiday Mondays (cancelled)": j(*a["s9_holidays"]) or "none",
        "supplier task created: Mon W-7; due: Mon W-3": f"{a['supplier_task']}; {a['supplier_due']}",
        "S3 call 31 (slot 5): Mon W-6; ru his first working day on or after": j(a["call31"]),
        "S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day": f"{a['s4_note1']}; {a['s4_note1_decided']}",
        "S9 moved to 10:00: Mon W-5": j(a["s9_moved"]), "slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after": j(a["call12"]),
        "senior's thread and task: Mon W-4": j(a["senior_thread"]), "S1 A6's web chat sent; first reply (slot 7)": f"{a['a6_chat_sent']}; {a['a6_chat_reply']}",
        "S3 fix: Mon W-3": j(a["s3_fix"]),
        "S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day": f"{a['s4_note2']}; {a['s4_note2_decided']}",
        "S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before": j(*a["s2_discounts"]),
        "S7 web chat 21:10: the evening before day A": j(a["s7_chat"]), "S7 day A (card taken, booked, confirming call)": j(a["s7_day_a"]),
        "S7 visit: her next working day": j(a["s7_visit"]), "S8 quote call, slot 7's second wrong price: his 5th working day back": j(a["s8_quote"]),
        "S8 car in: his 4th": j(a["s8_car_in"]), "S8 ready, bill, argument, complaint call": j(a["s8_ready"]), "S8 discount and call back": j(a["s8_discount"]),
        "S12 proposal: en next full open day; ru slot 5's first working day after": j(a["s12_proposal"]),
        "S10 report fails; S16 card given: Mon W-1": j(a["s10_report"]), "S6 car enters waiting_parts: T-9 d, snapped back": j(a["s6_waiting"]),
        "S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back": j(a["call15"]),
        "S6 missed call and call 16: en west's last full open day; ru slot 23's last working day": j(a["call16"]),
        "S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it": j(a["s14_no_show"]),
        "S7 return chat (web); S4 waiting note: slot 6's last working day": j(a["s7_return"]),
        "S4 nightly proposal: the pass after slot 5's last working day": j(a["s4_nightly"]),
        "S16 block / due 12:00 / meeting 10:00": f"{a['s16_block']} / {a['s16_due']} / {a['s16_meeting']}",
        "S14 open shift: Tue W+1": j(a["s14_open_shift"]), "S13 stocktake, closed from 12:00": j(a["stocktake"]),
        "S5 week off": f"{a['week_off']} to {a['week_off'] + dt.timedelta(6)}", "roster ends: T+14 d": j(a["roster_end"]),
        "last closed date before T": j(a["last_closed"]),
        "S9 counts": f"{len(s9)} occurrences: {len(a['s9_holidays'])} holiday, 1 cancelled, 1 moved, {len(a['s9_regular'])} regular; held {len(a['s9_regular']) + 1}",
    }


def timeline_md(cfg, when):
    """The worked example of stories/TIMELINE.md for one configuration and run instant, as {anchor: date}."""
    text = (inputs.SEED / "stories" / "TIMELINE.md").read_text(encoding="utf-8")
    block = text.split(f"### {cfg}, run at {when:%a %Y-%m-%d %H:%M}\n")[1].split("\nAsserted:")[0]
    return dict(re.findall(r"^\| (.+?) \| (.+?) \|$", block, re.M)[1:])


def place(cfg, when):
    """timeline_examples.place: its rows as {anchor: text} (S9 counts up to the occurrences held) and whether its checks hold."""
    table, order, shift = tl.place(cfg, when)
    want = {k: str(v) for k, v in table}
    want["S9 counts"] = want["S9 counts"].split("; slot 22")[0]
    return want, all(ok for _, ok in order) and all(ok for *_, ok in shift)


def failures(cfg, when):
    """The checks the anchors at `when` fail, as `place` names them; empty when they hold."""
    try:
        clock.place(cfg, when)
    except ValueError as e:
        return str(e).split(" fails: ")[1].split("; ")
    return []


@pytest.mark.parametrize("cfg", ("en", "ru"))
@pytest.mark.parametrize("when", tl.WHEN)
def test_anchors_are_the_worked_examples(cfg, when):
    got = rows(clock.place(cfg, when))
    md = timeline_md(cfg, when)
    md["S9 counts"] = md["S9 counts"].split("; slot 22")[0]
    assert got == place(cfg, when)[0] == md


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_a_year_of_instants_against_place(cfg):
    """Every anchor equals place's at six times of day over a year; the rows rule A moves are compared only from Thursday
    noon on. A build fails wherever place's own checks fail, and otherwise only on a check of rule A."""
    opening, closing = (tuple(map(int, x.split(":"))) for x in inputs.value("site.hours.weekday", cfg))
    times = [dt.time(opening[0] - 1, opening[1]), dt.time(*opening), dt.time(10, 30), dt.time(12), dt.time(*closing), dt.time(closing[0] + 1, closing[1])]
    for i in range(365):
        for hm in times:
            when = dt.datetime.combine(dt.date(2026, 3, 1) + dt.timedelta(i), hm)
            want, holds = place(cfg, when)
            failed = failures(cfg, when)
            assert holds or failed, when
            if failed:
                assert not holds or set(failed) <= RULE_A_CHECKS, (when, failed)
                continue
            got = rows(clock.place(cfg, when))
            t = dt.datetime.strptime(want["T"], "%a %Y-%m-%d %H:%M")
            if t < dt.datetime.combine(t.date() + dt.timedelta(3 - t.weekday()), dt.time(12)):
                for k in RULE_A_ROWS:
                    del got[k], want[k]
            assert got == want, when


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_the_publish_at_thursday_noon_moves_L(cfg):
    before, at = clock.place(cfg, dt.datetime(2026, 11, 19, 11, 59)), clock.place(cfg, dt.datetime(2026, 11, 19, 12))
    assert (before["pub_week"], before["stocktake"]) == (dt.date(2026, 11, 16), dt.date(2026, 11, 19))
    assert at["pub_week"] == dt.date(2026, 11, 23)


def test_thanksgiving_week_en():
    """Thanksgiving (Thu 2026-11-26) closes the stocktake's Thursday: the stocktake goes to the Tuesday, the week off starts
    on the Wednesday; from the Wednesday on, until the next publish, the anchors have the stocktake behind them and the
    build falls back to the Tuesday."""
    for day in (20, 21, 23, 24):
        a = clock.place("en", dt.datetime(2026, 11, day, 10, 30))
        assert (a["pub_week"], a["stocktake"], a["week_off"]) == (dt.date(2026, 11, 23), dt.date(2026, 11, 24), dt.date(2026, 11, 25)), day
    assert clock.anchors("en", dt.datetime(2026, 11, 22, 10, 30))["T"] == dt.datetime(2026, 11, 21, 13)
    for day in (25, 26):
        assert failures("en", dt.datetime(2026, 11, day, 10, 30)) == ["stocktake on or after T's date"], day
        assert clock.anchors("en", dt.datetime(2026, 11, day, 10, 30))["at"] == dt.datetime(2026, 11, 22, 10, 30), day
    assert clock.place("en", dt.datetime(2026, 11, 27, 10, 30))["stocktake"] == dt.date(2026, 12, 3)


def test_new_years_eve_ru():
    """1 and 2 January close the Thursday and the Friday: the stocktake is the Tuesday (30 December), the week off starts on
    the Wednesday, and a build on the Wednesday has its stocktake behind it."""
    a = clock.anchors("ru", dt.datetime(2025, 12, 30, 10, 30))
    assert (a["pub_week"], a["stocktake"], a["week_off"]) == (dt.date(2025, 12, 29), dt.date(2025, 12, 30), dt.date(2025, 12, 31))
    assert failures("ru", dt.datetime(2025, 12, 31, 10, 30)) == ["stocktake on or after T's date"]


def test_the_en_saturday_morning():
    assert clock.anchors("en", dt.datetime(2026, 11, 14, 12, 59))["T"] == dt.datetime(2026, 11, 14, 12, 59)
    assert clock.anchors("en", dt.datetime(2026, 11, 14, 13, 1))["T"] == dt.datetime(2026, 11, 14, 13)


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_story_days_fall_on_their_nominal_dates(cfg):
    a = clock.anchors(cfg, dt.datetime(2026, 11, 13, 10, 30))
    for n, f in inputs.STORY_FILES["calls", cfg].items():
        assert str(a["calls"][n]["day"]) == f["call"]["nominal_date"], f"call {n}"
    for n, f in inputs.STORY_FILES["conversations", cfg].items():
        assert {k: f"{d:%a} {d}" for k, d in a["conversations"][n]["days"].items()} == {k: v["nominal"] for k, v in f["days"].items()}, f"conversation {n}"


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_tuesday_calendar_anchors(cfg):
    a = clock.place(cfg, TUESDAY)
    T, L = a["T"].date(), a["pub_week"]
    for name, v in a.items():
        if name in ("T", "at", "asked", "calls", "conversations", "week_day", "works") or name in FUTURE:
            continue
        days = [d for site in v.values() for d in site] if isinstance(v, dict) else v if isinstance(v, (tuple, list)) else [v]  # s6_since: days per shop
        for d in days:
            assert isinstance(d, dt.date) and d <= T, name
    assert all(c["day"] <= T for c in a["calls"].values())
    assert all(d <= T for c in a["conversations"].values() for k, d in c["days"].items() if k == "T" or k.startswith("T-"))
    assert L == dt.date(2026, 11, 9) and L <= a["stocktake"] <= L + dt.timedelta(6) and T <= a["stocktake"] and T <= a["week_off"]
    named = 0
    for n, f in inputs.STORY_FILES["conversations", cfg].items():
        for k, day in f["days"].items():
            d, what = a["conversations"][n]["days"][k], day.get("what", "")
            if re.search(r"(?:^|; )the stocktake\b", what):
                assert d == a["stocktake"], (n, k)
            elif re.search(r"\bbefore the stocktake\b", what):
                assert d < a["stocktake"], (n, k)
            elif re.search(r"\bafter the stocktake\b", what):
                assert d > a["stocktake"], (n, k)
            else:
                continue
            named += 1
    assert named == {"en": 5, "ru": 3}[cfg]
    conv8 = a["conversations"][8]["days"]
    booking = next(conv8[k] for k, day in inputs.STORY_FILES["conversations", cfg][8]["days"].items() if "her appointment" in day["what"])
    assert booking == a["booking"] and conv8["T-1d"] <= booking < a["week_off"] and L - dt.timedelta(3) <= booking <= L + dt.timedelta(4)


def test_en_conversation_6_falls_back_when_open_days_cross_the_messages():
    asked = dt.datetime(2026, 11, 18, 15, 59)
    invalid = clock.place("en", asked)["conversations"][6]["days"]
    assert invalid["T-4d"] < invalid["T-5d"]
    a = clock.anchors("en", asked)
    days = a["conversations"][6]["days"]
    assert a["asked"] == asked and a["T"] == dt.datetime(2026, 11, 14, 13)
    assert days["T-5d"] < days["T-4d"] == a["calls"][15]["day"] < days["T-3d"]


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_the_anchors_erp_checks_read(cfg):
    """price.hour.history's ru rise, generator-spec.md's F4 seasons (en 2, ru 5), M4's never-closed days, the closed Mondays."""
    a, D = clock.anchors(cfg, dt.datetime(2026, 11, 13, 10, 30)), dt.date
    assert a["ru_rise"] == D(2025, 5, 13)
    assert a["f4_seasons"] == ([D(2025, 6, 2), D(2026, 6, 1)] if cfg == "en" else [D(2024, 10, 7), D(2025, 4, 7), D(2025, 10, 6), D(2026, 4, 6), D(2026, 10, 5)])
    assert [a["week_day"](-22, 2), a["week_day"](-12, 1), a["week_day"](-10, 1)] == [D(2026, 6, 10), D(2026, 8, 18), D(2026, 9, 1)]
    assert a["closed_mondays"] == ([D(2025, 5, 26), D(2025, 9, 1), D(2026, 5, 25), D(2026, 9, 7)] if cfg == "en" else [])


def test_cli_prints_the_header_example():
    out = subprocess.run([sys.executable, "-m", "seeder", "clock", "--cfg", "en", "--at", "2026-11-13 10:30"],
                         cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True, check=True).stdout
    header = (inputs.SEED / "erp" / "checks.sql").read_text(encoding="utf-8").split("-- Example:")[1].split("-f checks.sql")[0]
    example = dict(re.findall(r"-v (\w+)=('[^']*'|\S+)", header))
    assert out.split() == ["cfg=en", "size=full", "T=2026-11-13", "10:30"] + [f"{k}={v}" for k, v in example.items() if k not in ("cfg", "size", "T")]
    assert example["T"] == "'2026-11-13 10:30'"
