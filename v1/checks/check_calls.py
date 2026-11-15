#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks the hand-written story calls of one language against calls/DESIGN.md, the seed files and the ledger.

    python3 checks/check_calls.py en > checks/calls_check_en.txt
    python3 checks/check_calls.py ru --product

The argument is the language folder under calls/ (calls/en, calls/ru). What depends on the language is in LANG below;
a language that is not there yet fails with a line saying what to add. Nothing else assumes English.

Per call file: the format; every quote on the stored line it names; the score from the levels by the rubric's weights;
the score inside the band of DESIGN.md section 6; names, plates, units, prices, desks and addresses against the seed
files and the ledger. Over the set: the recognition model of DESIGN.md section 4 at its stated rates, and the calls that
carry a clarification loop (design rule R13).

The product checkout is ../traciora beside this one; TRACIORA_PRODUCT overrides it, and so does a path after --product.
With --product the verdict of every judged call is derived again by the product's own judge.verdict (import only; run
with the product's interpreter and PYTHONPATH=apps/backend/src). Without it the score is checked by the formula.

Exit code 1 when a check fails. Not product code.
"""
import datetime, glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
PRODUCT = os.environ.get("TRACIORA_PRODUCT") or os.path.normpath(os.path.join(SEED, "..", "..", "traciora"))
CHECKS = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")
NEW_ENQUIRY_ONLY = ("name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "objection")
WEIGHTS = dict(zip(CHECKS, (1, 2, 2, 2, 3, 3, 1, 2)))
OUTCOMES = ("visit_agreed", "callback_promised", "customer_will_call", "no_visit")
TAGS = ("visit_agreed", "quoted", "callback_promised", "callback_kept", "callback_not_kept", "no_visit", "customer_angry", "complaint",
        "price_objection", "wrong_promise", "repeat_caller", "warranty", "other_language")
CALL_LOG_KEYS = ("callback_kept", "callback_not_kept", "repeat_caller")
ABOUT = 3.0  # "about N" in section 6 is read as N plus or minus this

# ---------------------------------------------------------------------------------------------------- per language
LANG = {
    "en": dict(
        column=0,  # which of the two rate columns of DESIGN.md section 4 is this language's
        profiles=dict(light=80, marked=15, heavy=3, none=2),
        word_diff=dict(light=(0.08, 0.16), marked=(0.11, 0.30), heavy=(0.30, 0.50), mean=(0.11, 0.17)),
        rates=dict(hesitations=0.90, fillers=0.30, names=0.12, first_names=0.03, plates=0.35, vins=0.70, order_numbers=0.20, trade_terms=0.08,
                   digits=0.85, money_wrong=0.06, phones_wrong=0.05, bursts=dict(light=0.3, marked=3, heavy=8), overlaps_per_min=1.2,
                   overlap_lost=0.50, overlap_joined=0.20, swap=dict(light=0.03, marked=0.15, heavy=0.35), hold=0.06, hold_stored=0.35,
                   bad_line=0.04, invented=0.015, asr_poor=0.09),
        design_rate_cells={"R2": "12 % of mentions; first names 3 %", "R3": "plate 35 %, VIN 70 %, order number 20 %", "R4": "8 % of listed terms",
                           "R5": "6 % of money and time mentions; phones 5 %", "R6": "light 0.3 bursts a call, marked 3, heavy 8",
                           "R7": "1.2 overlaps a minute", "R8": "light 3 % of calls, marked 15 %, heavy 35 %", "R9": "6 % of calls have a hold",
                           "R10": "4 % of calls", "R12": "1.5 % of calls"},
        words_per_s=(1.6, 2.6),
        phone=re.compile(r"\(?(\d{3})\)?[ -]555-(\d{4})"), fictional=lambda m: 100 <= int(m.group(2)) <= 199,
        phone_key=lambda m: m.group(1) + m.group(2),
        plate=re.compile(r"\b[A-Z]{3}-\d{4}\b"),
        said_tolerance=lambda x: max(3.5, 0.01 * x), tax=0.0925,
        own_lines=("423-555-0142", "423-555-0167", "615-555-0119"),
        nominal_t="2026-11-13",
        # the date each anchor of section 6 falls on for the nominal T (stories/TIMELINE.md, the first worked example)
        dates={1: ("2026-05-22", "2026-06-20"), 2: ("2026-06-21", "2026-07-20"), 3: ("2026-07-21", "2026-08-19"), 4: ("2026-08-20", "2026-09-18"),
               5: ("2026-09-19", "2026-10-18"), 6: ("2026-10-19", "2026-11-13"), 7: "2026-11-11", 8: "2026-10-26", 9: "2026-11-06", 10: "2026-11-10",
               11: "2026-11-11", 12: "2026-10-06", 13: "2026-09-02", 14: "2026-11-10", 15: "2026-11-09", 16: "2026-11-12", 17: "2026-06-30",
               18: "2026-07-01", 19: "2026-07-06", 20: "2026-07-09", 21: "2026-06-23", 22: "2026-09-08", 23: "2026-07-15", 24: "2026-10-14",
               25: "2026-10-28", 26: "2026-09-14", 27: "2026-10-19", 28: "2026-09-28", 29: "2026-09-04", 30: "2026-10-23", 31: "2026-09-28",
               32: "2026-11-03", 33: "2026-09-24", 34: "2026-10-26", 35: "2026-06-16", 36: "2026-10-30"},
        times={31: "08:10", 32: "07:40"},
        weekend_closed=True,
        weekdays=re.compile(r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"),
        not_in_seed=re.compile(r"Jersey Pike"),
    ),
    "ru": dict(
        column=1,
        profiles=dict(light=72, marked=20, heavy=6, none=2),
        word_diff=dict(light=(0.08, 0.18), marked=(0.14, 0.34), heavy=(0.35, 0.55), mean=(0.14, 0.22)),
        rates=dict(hesitations=0.85, fillers=0.25, names=0.15, first_names=0.04, plates=0.30, vins=0.70, order_numbers=0.20, trade_terms=0.14,
                   digits=0.80, money_wrong=0.09, phones_wrong=0.08, bursts=dict(light=0.3, marked=3, heavy=8), overlaps_per_min=1.5,
                   overlap_lost=0.50, overlap_joined=0.20, swap=dict(light=0.03, marked=0.15, heavy=0.35), hold=0.05, hold_stored=0.35,
                   bad_line=0.06, invented=0.0, asr_poor=0.14),
        design_rate_cells={"R2": "15 %; 4 %", "R3": "30 %, 70 %, 20 %", "R4": "14 %; script choice Latin 55 %", "R5": "9 %; 8 %", "R6": "same", "R7": "1.5",
                           "R8": "same", "R9": "5 %", "R10": "6 %", "R12": "0"},
        words_per_s=(1.3, 2.3),
        phone=re.compile(r"\+7[ (]*(\d{3,4})\)?[ ]*([\d-]{6,9})"), fictional=lambda m: m.group(1) in ("907", "935") or m.group(2)[0] in "01",
        phone_key=lambda m: m.group(1) + re.sub(r"\D", "", m.group(2)),
        plate=re.compile(r"\b[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\s?\d{2,3}\b"),
        said_tolerance=lambda x: max(100.0, 0.01 * x), tax=0.05,
        own_lines=("10-40-40", "10-40-41", "100-40-30"),
        nominal_t="2026-11-13",
        # the date each anchor of section 6 falls on for the nominal T (stories/TIMELINE.md, the second worked example). A weekday anchor
        # that falls on the advisor's day off under the two-on, two-off rota is moved to the advisor's first working day on or after it:
        # calls 13, 21, 23, 24, 25, 26, 30, 35 and 36 for this T. Call 15 keeps its card's day (west's 4th open day), though slot 23 is off then.
        dates={1: ("2026-05-22", "2026-06-20"), 2: ("2026-06-21", "2026-07-20"), 3: ("2026-07-21", "2026-08-19"), 4: ("2026-08-20", "2026-09-18"),
               5: ("2026-09-19", "2026-10-18"), 6: ("2026-10-19", "2026-11-13"), 7: "2026-11-09", 8: "2026-10-24", 9: "2026-11-04", 10: "2026-11-08",
               11: "2026-11-09", 12: "2026-10-06", 13: "2026-09-04", 14: "2026-11-08", 15: "2026-11-08", 16: "2026-11-12", 17: "2026-06-30",
               18: "2026-07-01", 19: "2026-07-06", 20: "2026-07-09", 21: "2026-06-24", 22: "2026-09-08", 23: "2026-07-16", 24: "2026-10-16",
               25: "2026-10-30", 26: "2026-09-16", 27: "2026-10-19", 28: "2026-10-20", 29: "2026-09-04", 30: "2026-10-24", 31: "2026-09-28",
               32: "2026-10-28", 33: "2026-09-24", 34: "2026-10-26", 35: "2026-06-18", 36: "2026-11-01"},
        times={31: "09:40", 32: "09:10"},
        weekend_closed=False,
        not_in_seed=re.compile(r"Соловь|927 000|917 000"),
        # the calls whose stored lines earn less than the speech: the sample (25) and the heavy call in Kazan (33)
        truth_differs={25: "the second time offered and the address were lost to noise", 33: "the manager's question about the time is unintelligible"},
        # the house number each shop's street is said with, on the manager's stored lines
        streets={"main": (r"Московск\w+ шоссе", "40"), "east": (r"Инженерн\w+ проезд\w*", "30"), "west": (r"Техническ\w+", "30")},
    ),
}

# ---------------------------------------------------------------------------------------------------- section 6
# What each call of calls/DESIGN.md section 6 must earn. `design` holds words that must stand in the row's last
# cell of the design, so a change of the design trips this table. Bands: (low, high), both ends inside.
def about(n):
    return (n - ABOUT, n + ABOUT)

EXPECT = {
    1: dict(story="S4", slot=6, score=(40.0, 40.0), outcome="customer_will_call", try_next="offered_time", design=["40.0", "customer_will_call", "offered time"]),
    2: dict(story="S4", slot=6, score=(50, 56), levels=dict(offered_time=1, asked_for_booking=1), design=["50 to 56", "time 1, booking 1"]),
    3: dict(story="S4", slot=6, score=(59, 64), outcome="visit_agreed", design=["59 to 64", "visit_agreed"]),
    4: dict(story="S4", slot=6, score=(66, 70), design=["66 to 70"]),
    5: dict(story="S4", slot=6, score=(85, 94), design=["85 to 94"]),
    6: dict(story="S4", slot=6, score=(71.9, 71.9), tags=["price_objection"], design=["71.9", "price_objection"]),
    7: dict(story="S4", slot=6, scored=True, auto_fails=[], design=["scored", "no auto-fail"]),
    8: dict(story="S7", slot=6, kind="outbound", design=["outbound: not judged"]),
    9: dict(story="S8", slot=7, score=(31.2, 31.25), exact=31.25, points=(10, 32), auto_fails=["wrong_promise"], outcome="visit_agreed",
            design=["31.25 (10 of 32 points)", "wrong_promise", "visit_agreed"]),
    10: dict(story="S8", slot=5, kind="no_score", call_type="existing_job", levels=dict(greeting=2, recap=2), tags=["complaint", "customer_angry"],
             outcome="callback_promised", callback="kept", design=["no score", "greeting 2, recap 2", "complaint", "customer_angry", "callback_promised", "kept inside 24 h"]),
    11: dict(story="S8", slot=4, kind="outbound", design=["outbound: not judged"]),
    12: dict(story="S12", slot=7, score=about(40), auto_fails=["wrong_promise"], design=["about 40", "wrong_promise"]),
    13: dict(story="people", slot=7, score=about(35), auto_fails=[], design=["about 35"]),
    14: dict(story="people", slot=7, score=about(56), auto_fails=[], design=["about 56"]),
    15: dict(story="S6", slot=23, score=(25.0, 25.0), auto_fails=["wrong_promise"], tags=["customer_angry"], design=["25.0", "wrong_promise", "customer_angry"]),
    16: dict(story="S6", slot=23, kind="no_score", call_type="existing_job", tags=["repeat_caller", "complaint"], outcome="customer_will_call",
             unclear=dict(resolved=False), design=["no score", "repeat_caller", "complaint", "customer_will_call"]),
    17: dict(story="S1", slot=22, kind="no_score", call_type="existing_job", tags=["complaint", "warranty"], outcome="callback_promised", callback="not_kept",
             design=["no score", "complaint", "warranty", "callback_promised", "callback_not_kept"]),
    18: dict(story="S1", kind="miss", first_desk="302", design=["no text", "waiting"]),
    19: dict(story="S1", kind="miss", first_desk="303", design=["no text", "waiting"]),
    20: dict(story="S1", kind="miss", first_desk="302", design=["no text", "waiting"]),
    21: dict(story="S1", slot=5, score=about(75), tags=["price_objection"], unclear=dict(resolved=True, asked_again=2), levels=dict(need_discovery=2),
             design=["about 75", "price_objection"]),
    22: dict(story="S1", slot=7, score=about(45), auto_fails=[], outcome="callback_promised", callback="not_kept", design=["about 45", "callback_not_kept"]),
    23: dict(story="S1", slot=6, score=about(60), design=["about 60"]),
    24: dict(story="S1", slot=6, score=about(80), design=["about 80"]),
    25: dict(story="S5", slot=16, score=(83.3, 83.3), truth_score=100.0, asr="poor", design=["83.3 on the lines, 100 in truth", "asr_quality: poor"]),
    26: dict(story="S5", slot=16, score_in=(93.8, 100.0), outcome="visit_agreed", design=["93.8 or 100", "visit_agreed"]),
    27: dict(story="S5", slot=16, score_in=(93.8, 100.0), outcome="visit_agreed", design=["93.8 or 100", "visit_agreed"]),
    28: dict(story="S5", slot=17, score=about(55), auto_fails=[], design=["about 55"]),
    29: dict(story="people", slot=5, kind="no_score", call_type="existing_job", tags=["complaint"], design=["no score", "complaint", "one `customer_angry`"]),
    30: dict(story="people", slot=6, kind="no_score", call_type="existing_job", tags=["complaint"], design=["no score", "complaint", "one `customer_angry`"]),
    31: dict(story="S3", slot=5, scored=True, tags=["repeat_caller"], design=["scored", "repeat_caller"]),
    32: dict(story="S3", slot=6, score=about(80), design=["about 80"]),
    33: dict(story="people", slot=22, score=about(45), design=["about 45"]),
    34: dict(story="people", slot=22, score=about(50), design=["about 50"]),
    35: dict(story="people", slot=24, score=about(62), design=["about 62"]),
    36: dict(story="people", slot=24, score=about(81), design=["about 81"]),
}
TRUTH_DIFFERS = {25: "the second time offered and the address were lost to noise", 30: "the middle of the summary is unintelligible"}
UNCLEAR = {16, 21}  # design rule R13: the hand-written calls that carry it (DESIGN.md section 2; ledger r13.story_items)

OUT = []
FAILS = []


def say(line=""):
    OUT.append(line)


def ok(what, good, detail=""):
    say(("  ok    " if good else "  FAIL  ") + what + ("" if good or not detail else "  -> " + str(detail)[:600]))
    if not good:
        FAILS.append(what)
    return good


def load(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return json.load(f)


def text(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return f.read()


def words(s):
    return [w for w in (x.strip(".,!?;:…—–-\"«»") for x in s.lower().split()) if w]


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def formula(levels):
    """The product's score: None under three scored checks, else the weighted share, one decimal (scorecard.py)."""
    if len(levels) < 3:
        return None, None
    exact = 100 * sum(WEIGHTS[k] * v / 2 for k, v in levels.items()) / sum(WEIGHTS[k] for k in levels)
    return round(exact, 1), exact


def near_rate(k, n, p):
    """A rate read on a small set: inside half to double of the design's rate (DESIGN.md section 8), or within one case of it."""
    if n == 0:
        return True
    if p >= 0.5:
        return abs(k / n - p) <= 0.15 or abs(k - n * p) <= 1.0
    return p / 2 <= k / n <= 2 * p or abs(k - n * p) <= 1.0


def design_rows(md):
    """Section 6's table: number -> (story, slot cell, day, call, verdict)."""
    part = md.split("## 6.")[1].split("## 7.")[0]
    out = {}
    for line in part.split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not re.match(r"\d", cells[0]):
            continue
        m = re.fullmatch(r"(\d+)(?:\s*(to|,)\s*(\d+))?", cells[0])
        if not m:
            continue
        a, b = int(m.group(1)), int(m.group(3) or m.group(1))
        nums = list(range(a, b + 1))
        for i, n in enumerate(nums):
            out[n] = dict(story=cells[1], slot=cells[2], day=cells[3], call=cells[4], verdict=cells[5], position=i, of=len(nums))
    return out


# The Russian misses ring the desk of the advisor on shift that day (ledger s1.a5 miss_first_desks_ru): for the nominal T, 303, 302, 303.
RU_MISS_DESKS = {18: "303", 19: "302", 20: "303"}


def main():
    argv, product, args = sys.argv[1:], None, []
    while argv:
        a = argv.pop(0)
        if a == "--product":
            product = argv.pop(0) if argv and not argv[0].startswith("--") else PRODUCT
        elif not a.startswith("--"):
            args.append(a)
    if len(args) != 1:
        print(__doc__)
        return 2
    lang = args[0].strip("/").split("/")[-1]
    folder = os.path.join(SEED, "calls", lang)
    say(f"check_calls.py {lang}: the hand-written story calls in calls/{lang}/ against calls/DESIGN.md, the seed files and the ledger")
    if lang not in LANG:
        ok(f"language '{lang}' has its table in LANG (rates of DESIGN.md section 4, phone and plate forms, nominal dates)", False, "add it to check_calls.py")
        print("\n".join(OUT))
        return 1
    L = LANG[lang]
    ledger = {r["key"]: r for r in load("ledger.json")["rows"]}
    val = lambda k: ledger[k]["value"] if "value" in ledger[k] else ledger[k][lang]
    CAST = {p["slot"]: p for p in load("cast.json")["people"]}
    ACC, NAMED, VEND, CAT = load("accounts.json")[lang], load("named_customers.json")[lang], load("vendors.json")[lang], load("catalogue.json")
    design = text("calls/DESIGN.md")
    rows6 = design_rows(design)
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    calls = {}

    # ------------------------------------------------------------------------------------------------ 1. files
    say("\n1. Files and format")
    bad = []
    for f in files:
        name = os.path.basename(f)
        m = re.fullmatch(r"(\d\d)-([A-Za-z0-9]+)-([a-z0-9-]+)\.json", name)
        if not m:
            bad.append(name + ": name is not NN-<story>-<short-name>.json")
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError as e:
            bad.append(f"{name}: not JSON ({e})")
            continue
        n = int(m.group(1))
        if d.get("number", n) != n or d.get("story", m.group(2)) != m.group(2):
            bad.append(name + ": number or story differs from the file name")
        if n in calls:
            bad.append(name + ": a second file for call " + str(n))
        d["_name"], d["_n"], d["_story"] = name, n, m.group(2)
        calls[n] = d
    ok(f"{len(files)} files named NN-<story>-<short-name>.json, each valid JSON with its number and story", not bad, "; ".join(bad))
    missing = [n for n in range(1, 37) if n not in calls]
    ok("every call of section 6 is there once: 1 to 36", not missing and len(calls) == 36, f"missing {missing}")
    texted = {n: d for n, d in calls.items() if d.get("transcript")}
    misses = {n: d for n, d in calls.items() if not d.get("transcript")}
    ok("33 calls with text and 3 misses without (ledger proposed.calls.handwritten)", len(texted) == 33 and sorted(misses) == [18, 19, 20], f"{len(texted)} with text; without: {sorted(misses)}")

    bad = []
    need = ("format", "id", "configuration", "title", "purpose", "cast", "call", "scenario", "floating_days", "script", "recognition", "transcript", "judge_answer", "verdict", "truth", "why")
    for n, d in sorted(calls.items()):
        nm = d["_name"]
        miss = [k for k in need if k not in d]
        if miss:
            bad.append(f"{nm}: no {miss}")
            continue
        if d["format"] != "seed-call/1" or d["configuration"] != lang:
            bad.append(nm + ": format or configuration")
        c = d["call"]
        for k in ("day", "nominal_date", "local_start", "site", "direction", "line", "ring_s", "talk_s", "repeat_caller"):
            if k not in c:
                bad.append(f"{nm}: call.{k}")
        if "new_facts" not in d:
            bad.append(nm + ": no new_facts list (rule 5 of the brief)")
        if n in misses:
            if d["script"] or d["recognition"] or d["judge_answer"] or d["verdict"]:
                bad.append(nm + ": a miss carries no script, recognition, judge answer or verdict")
            continue
        last = -1.0
        for i, t in enumerate(d["script"], 1):
            if t.get("n") != i or t.get("who") not in ("advisor", "customer", "hold") or not isinstance(t.get("said"), str) or not t["said"].strip():
                bad.append(f"{nm}: script turn {i}")
            if not isinstance(t.get("at_s"), (int, float)) or t["at_s"] < last:
                bad.append(f"{nm}: at_s of turn {i}")
            last = t.get("at_s", last)
        if d["script"] and d["script"][0]["at_s"] != 0:
            bad.append(nm + ": the first turn is not at 0 s")
        if not (last <= c["talk_s"] <= last + 15):
            bad.append(f"{nm}: talk_s {c['talk_s']} against the last turn at {last}")
        tr = d["transcript"]
        if tr.get("engine") != "ensemble" or tr.get("language") != lang or tr.get("pii_state") != "raw" or not str(tr.get("engine_version", "")).count("|") >= 2:
            bad.append(nm + ": transcript engine, version, language or pii_state")
        for i, s in enumerate(tr["segments"]):
            if s.get("sequence") != i or s.get("speaker_label") not in ("manager", "customer") or not str(s.get("text", "")).strip():
                bad.append(f"{nm}: segment {i}")
            if any(s.get(k, 0) is not None for k in ("start_ms", "end_ms", "confidence")):
                bad.append(f"{nm}: segment {i} carries timing or confidence; the product stores none")
        stored_words = sum(len(s["text"].split()) for s in tr["segments"])
        if abs(tr.get("word_count", -99) - (stored_words + len(tr["segments"]))) > max(6, 0.03 * stored_words):
            bad.append(f"{nm}: transcript.word_count {tr.get('word_count')} against {stored_words} words in {len(tr['segments'])} labelled lines")
        if tr.get("duration_s") != float(c["talk_s"]):
            bad.append(nm + ": transcript.duration_s is not the talk time")
        rate = len(words(" ".join(t["said"] for t in d["script"] if t["who"] != "hold"))) / max(1, c["talk_s"] - sum(t.get("hold_s", 0) for t in d["script"]))
        if not L["words_per_s"][0] <= rate <= L["words_per_s"][1]:
            bad.append(f"{nm}: {rate:.2f} words a second of talk")
        if not isinstance(d["why"], dict) or (d["call"]["direction"] == "inbound" and "carried_by" not in d["why"]):
            bad.append(nm + ": why")
    ok("every file has the keys of DESIGN.md section 7; scripts are numbered with rising times; stored lines are in the product's shape (no timing, no confidence); word counts and talk time agree", not bad, "; ".join(bad[:8]))

    # ------------------------------------------------------------------------------------------------ 2. section 6
    say("\n2. Section 6: who, the verdict each call must earn")
    bad = []
    for n in range(1, 37):
        if n not in rows6:
            bad.append(f"call {n} is not in the design's table")
            continue
        r, e = rows6[n], EXPECT[n]
        stories = [s.strip() for s in r["story"].split(",")]
        if e["story"] not in stories:
            bad.append(f"call {n}: design story {r['story']}, table {e['story']}")
        cell = r["verdict"]
        for part in e["design"]:
            if part not in cell:
                bad.append(f"call {n}: the design's verdict cell no longer says '{part}'")
        slots = re.findall(r"\d+", r["slot"])
        if e.get("kind") == "miss":
            if e["first_desk"] != slots[r["position"]]:
                bad.append(f"call {n}: first desk")
        elif str(e["slot"]) != (slots[r["position"]] if len(slots) == r["of"] else slots[0]):
            bad.append(f"call {n}: design slot {r['slot']}, table {e['slot']}")
    ok("this script's table of expectations is the table of DESIGN.md section 6 (story, slot or first desk, the words of each verdict cell)", not bad, "; ".join(bad[:8]))

    bad, lines = [], []
    judged = {}
    for n, d in sorted(calls.items()):
        e, nm = EXPECT[n], d["_name"]
        if d["_story"] != e["story"]:
            bad.append(f"{nm}: story {d['_story']}, section 6 says {e['story']}")
        kind = e.get("kind", "scored")
        if kind == "miss":
            c = d["call"]
            want_desk = RU_MISS_DESKS.get(n, e["first_desk"]) if lang == "ru" else e["first_desk"]
            if c.get("answered") is not False or c.get("first_desk") != want_desk or (d.get("missed_call") or {}).get("state") != "waiting" or c["talk_s"] != 0:
                bad.append(f"{nm}: a miss is unanswered, rings desk {want_desk} first and stays waiting")
            lines.append((n, e["story"], "-", "miss", "no text; waiting"))
            continue
        adv = d["cast"]["advisor"]
        if adv.get("slot") != e["slot"]:
            bad.append(f"{nm}: slot {adv.get('slot')}, section 6 says {e['slot']}")
        v = d["verdict"]
        pub = v["result_public"]
        if kind == "outbound":
            if d["call"]["direction"] != "outbound" or pub.get("judged") is not False or v["score"] is not None or pub.get("checks") or d["judge_answer"]:
                bad.append(f"{nm}: an outbound call is not judged")
            lines.append((n, e["story"], e["slot"], "no score", "outbound: not judged"))
            continue
        judged[n] = d
        if d["call"]["direction"] != "inbound" or pub.get("judged") is not True:
            bad.append(f"{nm}: an inbound call is judged")
        score = v["score"]
        levels = {c["key"]: c["level"] for c in pub["checks"]}
        if kind == "no_score":
            if score is not None or pub["call_type"] != "existing_job" or len(levels) >= 3:
                bad.append(f"{nm}: section 6 says no score (an existing-job call)")
        else:
            if score is None or pub["call_type"] != "new_enquiry":
                bad.append(f"{nm}: section 6 wants a scored new enquiry")
            elif "score" in e and not (e["score"][0] - 1e-9 <= score <= e["score"][1] + 1e-9):
                bad.append(f"{nm}: score {score} outside {e['score']}")
            elif "score_in" in e and score not in e["score_in"]:
                bad.append(f"{nm}: score {score} is not one of {e['score_in']}")
        if "exact" in e:
            exact = formula(levels)[1]
            pts = sum(WEIGHTS[k] * lv for k, lv in levels.items()), 2 * sum(WEIGHTS[k] for k in levels)
            if exact is None or abs(exact - e["exact"]) > 1e-9 or pts != e["points"]:
                bad.append(f"{nm}: the levels give {exact} ({pts[0]} of {pts[1]} points), section 6 says {e['exact']} ({e['points'][0]} of {e['points'][1]})")
        for k, lv in e.get("levels", {}).items():
            if levels.get(k) != lv:
                bad.append(f"{nm}: {k} at {levels.get(k)}, section 6 says {lv}")
        if "outcome" in e and pub["outcome"] != e["outcome"]:
            bad.append(f"{nm}: outcome {pub['outcome']}, section 6 says {e['outcome']}")
        for t in e.get("tags", []):
            if t not in pub["tags"]:
                bad.append(f"{nm}: tag {t} is missing")
        fails = sorted(a["key"] for a in pub["auto_fails"])
        if "auto_fails" in e and fails != sorted(e["auto_fails"]):
            bad.append(f"{nm}: auto-fails {fails}, section 6 says {e['auto_fails']}")
        if "asr" in e and pub["asr_quality"] != e["asr"]:
            bad.append(f"{nm}: asr_quality {pub['asr_quality']}")
        if "try_next" in e and pub["try_next_check"] != e["try_next"]:
            bad.append(f"{nm}: try next {pub['try_next_check']}")
        if "truth_score" in e and d["truth"].get("score") != e["truth_score"]:
            bad.append(f"{nm}: truth score {d['truth'].get('score')}, section 6 says {e['truth_score']}")
        if "callback" in e:
            log = d.get("call_log") or {}
            kept = str(log.get("callback", "")).startswith("kept")
            if not log.get("callback_promised") or kept != (e["callback"] == "kept") or (log.get("auto_fail") == "callback_not_kept") != (e["callback"] == "not_kept"):
                bad.append(f"{nm}: the call log's follow-up (call_log) does not say the call back was {e['callback']}")
        if kind == "no_score" and "day_report" not in d:
            bad.append(f"{nm}: a call without a score still says what the day report would say (day_report)")
        band = e.get("score") or e.get("score_in") or ("scored" if e.get("scored") else "no score")
        lines.append((n, e["story"], e["slot"], "no score" if score is None else score,
                      f"{pub['call_type']}; {pub['outcome']}; tags {','.join(pub['tags']) or '-'}; auto-fails {','.join(fails) or '-'}; asr {pub['asr_quality']}; wanted {band}"))
    angry = [n for n in (29, 30) if n in judged and "customer_angry" in judged[n]["verdict"]["result_public"]["tags"]]
    if len(angry) != 1:
        bad.append(f"calls 29 and 30: exactly one carries customer_angry, found {angry}")
    ok("every call is by the slot of section 6 and earns its verdict: the score inside its band, or no score; the outcome, tags, auto-fails, quality and call-back state the row names", not bad, "; ".join(bad[:8]))
    say("        #  story   slot  score     verdict on the stored lines")
    for n, story, slot, score, rest in lines:
        say(f"       {n:2d}  {story:6s}  {str(slot):4s}  {str(score):8s}  {rest}")

    # ------------------------------------------------------------------------------------------------ 3. the score
    say("\n3. The score follows from the levels by the rubric's weights")
    md_w = dict(re.findall(r"\| `(\w+)` \((\d)\) \|", design))
    ok("weights 1, 2, 2, 2, 3, 3, 1, 2 are those of DESIGN.md section 3", {k: int(v) for k, v in md_w.items()} == WEIGHTS, md_w)
    card_path = os.path.join(product or PRODUCT, "config", "defaults", "phonecalls_scorecard.json")
    if os.path.exists(card_path):
        card = json.load(open(card_path, encoding="utf-8"))
        ok("and those of the product's default scorecard (config/defaults/phonecalls_scorecard.json), with the same checks in the same order",
           [(c["key"], c["weight"]) for c in card["checks"]] == [(k, WEIGHTS[k]) for k in CHECKS])
    else:
        say("  note  the product's scorecard file was not found; the weights are checked against the design only")
    bad = []
    for n, d in sorted(judged.items()):
        nm, ja, v = d["_name"], d["judge_answer"], d["verdict"]
        pub = v["result_public"]
        levels = {c["key"]: c["level"] for c in pub["checks"]}
        if [(c["key"], c["level"], c["segment"]) for c in ja["checks"]] != [(c["key"], c["level"], c["segment"]) for c in pub["checks"]]:
            bad.append(nm + ": the verdict's checks are not the judge answer's")
        if [c["key"] for c in pub["checks"]] != [k for k in CHECKS if k in levels]:
            bad.append(nm + ": checks are not in the scorecard's order")
        want = formula(levels)[0]
        if v["score"] != want or pub["score"] != want or pub["applicable"] != len(levels):
            bad.append(f"{nm}: score {v['score']} / {pub['score']}, the levels give {want} over {len(levels)} checks")
        na = [x["key"] for x in ja.get("na", [])]
        if sorted(pub["na"]) != sorted(na) or pub["unverified"]:
            bad.append(nm + ": N/A list, or an unverified check")
        new = pub["call_type"] == "new_enquiry"
        napp = [] if new else list(NEW_ENQUIRY_ONLY)
        if sorted(pub["not_applicable"]) != sorted(napp):
            bad.append(nm + ": not_applicable is not the new-enquiry-only checks of an existing-job call")
        covered = set(levels) | set(na) | set(pub["not_applicable"])
        if covered != set(CHECKS) or len(levels) + len(na) + len(pub["not_applicable"]) != 8:
            bad.append(f"{nm}: the eight checks are not each scored, N/A or not applicable once ({sorted(set(CHECKS) - covered)})")
        tags = list(pub["tags"])
        want_tags = ([pub["outcome"]] if pub["outcome"] in TAGS else []) + [t for t in ja["tags"]] + (["repeat_caller"] if d["call"]["repeat_caller"] else [])
        if tags != want_tags or any(t in CALL_LOG_KEYS or t in OUTCOMES for t in ja["tags"]) or any(t not in TAGS for t in tags):
            bad.append(f"{nm}: tags {tags}; the product would make {want_tags} (the outcome first, the judge's tags, repeat_caller from the call log)")
        if pub["outcome"] not in OUTCOMES or (pub["outcome"] != "no_visit") != (pub["no_visit_reason"] is None):
            bad.append(nm + ": outcome or no-visit reason")
        if pub.get("scheme") != "scorecard" or pub.get("line") != d["call"]["line"] or pub.get("asr_quality") not in ("ok", "poor"):
            bad.append(nm + ": result_public scheme, line or asr_quality")
        enc = v["result_enc_plain"]
        if set(enc["checks"]) != set(levels) or set(enc["na"]) != set(na) or set(enc["auto_fails"]) != {a["key"] for a in pub["auto_fails"]}:
            bad.append(nm + ": the sealed part does not hold a quote per scored check, a reason per N/A and a quote per auto-fail")
        tl = d["truth"].get("levels") or {}
        t_scored = {k: x for k, x in tl.items() if isinstance(x, int)}
        if set(tl) != set(CHECKS):
            bad.append(nm + ": truth.levels does not name the eight checks")
        elif d["truth"].get("score") != formula(t_scored)[0]:
            bad.append(f"{nm}: truth.score {d['truth'].get('score')}, the truth's levels give {formula(t_scored)[0]}")
        elif (t_scored != levels) != (n in L.get("truth_differs", TRUTH_DIFFERS)):
            td = L.get("truth_differs", TRUTH_DIFFERS)
            bad.append(f"{nm}: truth and verdict " + ("should differ: " + td[n] if n in td else "differ, and section 6 plants no difference here"))
        for k in CHECKS:
            if k in levels and k not in d["why"]:
                bad.append(f"{nm}: no 'why' for {k}")
        for k in d["why"].get("carried_by", []):
            if k not in levels:
                bad.append(f"{nm}: carried_by names {k}, which is not scored")
    ok("for each judged call: levels equal the judge answer's; score = round(100 x sum(weight x level / 2) / sum(weight), 1), none under three scored checks; "
       "each of the eight checks is scored, N/A or not applicable; tags as the product builds them; truth differs from the verdict only in calls "
       + " and ".join(str(x) for x in sorted(L.get("truth_differs", TRUTH_DIFFERS))) + "; a 'why' per scored check",
       not bad, "; ".join(bad[:8]))

    derived = None
    if product:
        try:
            sys.path.insert(0, os.path.join(product, "apps", "backend", "src"))
            from traciora.core.phonecalls import judge, scorecard as sc
            cardobj = sc.parse(json.load(open(card_path, encoding="utf-8")))
            bad = []
            for n, d in sorted(judged.items()):
                segs = d["transcript"]["segments"]
                c = d["call"]
                facts = judge.CallFacts(direction=c["direction"], started_local=c["local_start"], line=c["line"], answered_by=str(c.get("answered_by")),
                                        ring_s=c["ring_s"], talk_s=c["talk_s"], repeat_caller=bool(c["repeat_caller"]))
                v = judge.verdict(d["judge_answer"], [judge.Line(s["sequence"], s["speaker_label"], s["text"]) for s in segs], cardobj, facts)
                pub = dict(v.public(cardobj, line=c["line"]), media_version=1)
                if pub != d["verdict"]["result_public"] or v.sealed() != d["verdict"]["result_enc_plain"] or v.score != d["verdict"]["score"]:
                    bad.append(d["_name"])
            derived = len(judged) - len(bad)
            ok(f"--product: judge.verdict of the product makes the stored verdict from the judge answer and the stored lines, for all {len(judged)} judged calls", not bad, "; ".join(bad))
        except Exception as e:  # the import needs the product's interpreter
            ok("--product: the product's judge could be imported", False, repr(e))
    else:
        say("  note  run with --product (the product's interpreter, PYTHONPATH=apps/backend/src) to derive every verdict again by the product's own judge.verdict")

    # ------------------------------------------------------------------------------------------------ 4. quotes
    say("\n4. Quotes")
    bad = []
    for n, d in sorted(judged.items()):
        nm, ja = d["_name"], d["judge_answer"]
        segs = {s["sequence"]: s for s in d["transcript"]["segments"]}
        alltext = " ".join(s["text"] for s in d["transcript"]["segments"])
        def on_line(row, what, staff):
            s = segs.get(row.get("segment"))
            q = row.get("quote", "")
            if s is None or q not in s["text"]:
                bad.append(f"{nm}: the quote of {what} is not on line {row.get('segment')}")
                return
            whole = re.sub(r"[^\w\s]+", " ", q.casefold()).split() == re.sub(r"[^\w\s]+", " ", s["text"].casefold()).split()
            if not whole and len(q.split()) < 3:
                bad.append(f"{nm}: the quote of {what} is a fragment under three words")
            if staff and s["speaker_label"] != "manager":
                bad.append(f"{nm}: the quote of {what} is on the customer's line; above level 0 it must be the manager's")
        for c in ja["checks"]:
            on_line(c, c["key"], c["level"] > 0)
        for a in ja["auto_fails"]:
            on_line(a, a["key"], False)
        if ja.get("strength"):
            on_line(ja["strength"], "the strength", True)
        else:
            bad.append(nm + ": no strength")
        tn = ja.get("try_next")
        if tn:
            if tn["check"] not in {c["key"] for c in ja["checks"]} or tn["instead_of"] not in alltext or not tn["say"].strip():
                bad.append(nm + ": try_next names a check that is not scored, or words that are not in the transcript")
        for grp in ("checks", "auto_fails"):
            for k, q in d["verdict"]["result_enc_plain"][grp].items():
                if q not in alltext:
                    bad.append(f"{nm}: the stored quote of {k} is not in the transcript")
    nq = sum(len(d["judge_answer"]["checks"]) + len(d["judge_answer"]["auto_fails"]) + 1 for d in judged.values())
    ok(f"all {nq} quotes of the judge answers (checks, auto-fails, strengths) sit word for word on the stored line they name; above level 0 that line is the manager's; "
       "each coaching line quotes the transcript", not bad, "; ".join(bad[:8]))

    # ------------------------------------------------------------------------------------------------ 5. seed facts
    say("\n5. Names, numbers, plates, units, prices, desks and addresses against the seed files and the ledger")
    site_line = {p["key"]: next(x["ext"] for x in p["extensions"] if x["kind"] == "group line") for p in load(f"tenant/roles-and-places.{lang}.json")["places"]}
    desks = {s: str(val(f"p{int(s):02d}.desk")) for s in CAST if s.isdigit() and f"p{int(s):02d}.desk" in ledger}
    # story_callers and the accounts' from_story_files are the register of this set's own new facts (fix pass A); every other section is somebody else
    seed_text = json.dumps([dict(ACC, accounts=[{k: v for k, v in a.items() if k != "from_story_files"} for a in ACC["accounts"]]), {k: v for k, v in NAMED.items() if k != "story_callers"}, VEND], ensure_ascii=False) + json.dumps([{k: v for k, v in p.items() if k in (lang, "slot")} for p in CAST.values()], ensure_ascii=False)
    seed_phones = {L["phone_key"](m) for m in L["phone"].finditer(seed_text)}
    seed_names = set(re.findall(r'"(?:name|full_name)": "([^"]+)"', seed_text))
    seed_surnames = {x.split()[-1] for x in seed_names if " " in x and not re.search(r"\d|&|,", x)}
    staff_surnames = {p[lang]["full_name"].split()[-1] for p in CAST.values()}
    plates = {}
    for a in ACC["accounts"]:
        for v in a["fleet"]:
            plates[v["plate"]] = (a["id"], v)
    for key, c in NAMED.items():
        if isinstance(c, dict) and isinstance(c.get("car"), dict):
            plates[c["car"]["plate"]] = (key, c["car"])

    def resolve(ref):
        m = re.match(r"(\w+)\.json " + lang + r"\.(\w+)(?: contacts\[(\d+)\])?", ref)
        if not m:
            return None
        fname, key, idx = m.groups()
        if fname == "accounts":
            acc = next((a for a in ACC["accounts"] if a["id"] == key), None)
            return (acc["contacts"][int(idx)] if idx is not None else acc) if acc else None
        if fname == "named_customers":
            return NAMED.get(key)
        if fname == "vendors":
            return next((v for v in VEND if v["id"] == key), None)
        return None

    bad, by_phone = [], {}
    for n, d in sorted(calls.items()):
        nm, c = d["_name"], d["call"]
        adv = d["cast"].get("advisor")
        site = c["site"]
        if c["line"] != site_line[site]:
            bad.append(f"{nm}: line {c['line']} is not {site}'s")
        if adv:
            p = CAST[str(adv["slot"])]
            full = p[lang]["full_name"]
            if adv["name"] not in (full, " ".join([full.split()[0], full.split()[-1]])):
                bad.append(f"{nm}: advisor {adv['name']} is not slot {adv['slot']} ({full})")
            if site != p["site"] and site not in p.get("also_sites", []):
                bad.append(f"{nm}: slot {adv['slot']} does not work at {site}")
            ext = c.get("answered_by") if c["direction"] == "inbound" else c.get("placed_from")
            want = desks.get(str(adv["slot"]), str(p["extension"]))
            if str(ext) != want:
                bad.append(f"{nm}: desk {ext}, slot {adv['slot']}'s is {want}")
        for mnt in d["cast"].get("mentioned", []):
            if "slot" in mnt and CAST[str(mnt["slot"])][lang]["full_name"] != mnt["name"]:
                bad.append(f"{nm}: {mnt['name']} is not slot {mnt['slot']}")
            if "ref" in mnt and (resolve(mnt["ref"]) or {}).get("name") != mnt["name"]:
                bad.append(f"{nm}: {mnt['name']} is not {mnt['ref']}")
        cust = d["cast"]["customer"]
        phone = c.get("caller_phone") or c.get("callee_phone")
        pm = L["phone"].search(phone or "")
        if not pm or not L["fictional"](pm):
            bad.append(f"{nm}: {phone} is not a fictional number of phones.md")
            continue
        key = L["phone_key"](pm)
        if phone in L["own_lines"] or any(o in phone for o in L["own_lines"]):
            bad.append(f"{nm}: the caller's number is one of the shops' own lines")
        by_phone.setdefault(key, set()).add(cust["name"])
        if "ref" in cust:
            who = resolve(cust["ref"])
            if not who or who.get("name") != cust["name"]:
                bad.append(f"{nm}: {cust['name']} is not {cust['ref']}")
            elif L["phone_key"](L["phone"].search(who["phone"])) != key:
                bad.append(f"{nm}: {phone} is not the number of {cust['ref']} ({who['phone']})")
            if "account" in cust and not cust["ref"].startswith(f"accounts.json {lang}.{cust['account']}"):
                bad.append(f"{nm}: account {cust['account']} against {cust['ref']}")
        elif cust.get("invented"):
            if key in seed_phones:
                bad.append(f"{nm}: {phone} belongs to somebody in the seed files; an invented caller needs a free number")
            if cust["name"] in seed_names or cust["name"].split()[-1] in staff_surnames:
                bad.append(f"{nm}: the invented caller {cust['name']} shares a name with somebody in the seed files")
            if "account" in cust and not any(a["id"] == cust["account"] and a["name"] == cust.get("company") for a in ACC["accounts"]):
                bad.append(f"{nm}: company {cust.get('company')} is not account {cust.get('account')}")
        else:
            bad.append(f"{nm}: the customer is neither a reference into the seed files nor marked invented")
        if L["not_in_seed"].search(json.dumps(d, ensure_ascii=False)):
            bad.append(nm + ": a name or number the seed does not have")
    for key, names in by_phone.items():
        if len(names) > 1:
            bad.append(f"one number, several callers: {sorted(names)}")
    people = {}
    for n, d in calls.items():
        people.setdefault(d["cast"]["customer"]["name"], set()).add(d["call"].get("caller_phone") or d["call"].get("callee_phone"))
    for name, phs in people.items():
        if len(phs) > 1:
            bad.append(f"{name} has several numbers: {sorted(phs)}")
    ok("advisors are the cast's people at their own desks, lines and shops; customers and contacts are the seed files' (name and number) or invented with a free fictional number and a name nobody in the seed has; "
       "one caller, one number across the set", not bad, "; ".join(bad[:8]))

    bad, nplates, nunits = [], 0, 0
    for n, d in sorted(calls.items()):
        nm = d["_name"]
        blob = json.dumps(d, ensure_ascii=False)
        owner = None
        cust = d["cast"]["customer"]
        if cust.get("account"):
            owner = cust["account"]
        elif "ref" in cust and "named_customers" in cust["ref"]:
            owner = cust["ref"].split(".")[-1]
        for pl in set(L["plate"].findall(blob)):
            nplates += 1
            if pl not in plates:
                bad.append(f"{nm}: plate {pl} is on no car of the seed files")
            elif owner and plates[pl][0] != owner:
                bad.append(f"{nm}: plate {pl} belongs to {plates[pl][0]}, the caller is {owner}")
        veh = str(d["scenario"].get("vehicle", ""))
        if n in misses:
            continue
        if cust.get("account"):
            acc = next(a for a in ACC["accounts"] if a["id"] == cust["account"])
            fleet = {v["unit"]: v for v in acc["fleet"]}
            for unit in set(re.findall(r"\b(?:" + "|".join(re.escape(u) for u in fleet) + r")\b", veh)):
                nunits += 1
                v = fleet[unit]
                near = veh[veh.index(unit):veh.index(unit) + 90]
                if str(v["year"]) not in near or v["make"].split()[0] not in near or v["plate"] not in near:
                    bad.append(f"{nm}: unit {unit} is a {v['year']} {v['make']} {v['model']}, {v['plate']}")
            if not re.search("|".join(re.escape(u) for u in fleet), veh):
                bad.append(f"{nm}: a call of account {cust['account']} names no unit of its fleet")
        elif "ref" in cust and "named_customers" in cust["ref"]:
            car = resolve(cust["ref"])["car"]
            if str(car["year"]) not in veh or car["make"] not in veh or car["plate"] not in veh:
                bad.append(f"{nm}: the car is a {car['year']} {car['make']} {car['model']}, {car['plate']}")
    ok(f"{nplates} plates and {nunits} fleet units named in the files are the seed files' cars, on the caller's own account or record, with the year, make and plate of the file", not bad, "; ".join(bad[:8]))

    cfg = CAT["configurations"][lang]
    jobs = {j["key"]: j[lang] for j in CAT["jobs"]}

    def list_price(job, cls, tier, company, when):
        j = jobs[job]
        # the shop system's arithmetic (seeder/erp/orders.py: price): hourly labour is the sold hours to the hundredth x
        # the hour, to the cent; a part line is its quantity x the unit price (class multiplier and company terms on the
        # unit) to the cent
        hm = (j["hours_by_class"] or {}).get(cls, 1.0) if j["hours_by_class"] else 1.0
        if j["labour_pricing"] == "hourly":
            lab = round(round(j["hours"] * hm + 1e-9, 2) * cfg["labour_rate"]["company_account" if company else "standard"][when] + 1e-9, 2)
        else:
            lab = (j["labour_price_company"] if company else j["labour_price"])[when] * hm
        parts = 0.0
        for slot in j["parts"]:
            opts = {o["tier"]: o for o in slot["options"] if not o.get("story")}
            o = opts.get(tier) or opts.get("standard") or next(iter(opts.values()))
            unit = round(o["list_price"] * (cfg["parts_class_multiplier"][cls] if j["parts_scale_with_class"] else 1.0) + 1e-9, 2)
            if company:
                unit = round(unit * (1 - cfg["company_account_terms"]["parts_discount"]) + 1e-9, 2)
            parts += round(slot["qty"] * unit + 1e-9, 2)
        total = lab + parts + sum(f["price"] for f in j["fees"]) + (j["sublet"]["price"] if j["sublet"] else 0.0)
        sup = min(cfg["shop_supplies"]["rate_of_hourly_labour"] * lab, cfg["shop_supplies"]["cap_per_order"]) if j["labour_pricing"] == "hourly" else 0.0
        return round(total, 2), round(sup, 2)

    bad, nprices, nledger = [], 0, 0
    money_key = next((k for k in ("usd", "rub") if any(k in r for d in texted.values() for r in d["scenario"].get("facts", {}).get("prices", []))), "usd")
    for n, d in sorted(texted.items()):
        nm, facts = d["_name"], d["scenario"].get("facts", {})
        date = datetime.date.fromisoformat(d["call"]["nominal_date"])
        t0 = date + datetime.timedelta(days=int(re.search(r"T-(\d+)d", d["call"]["nominal_offset"]).group(1)))
        p_day = t0 - datetime.timedelta(days=150)
        p_day += datetime.timedelta(days=(7 - p_day.weekday()) % 7)
        when = "after_rise" if date >= p_day else "before_rise"
        for r in facts.get("prices", []):
            nprices += 1
            company = r["price_class"] == "company_account"
            usd, sup = list_price(r["job"], r["vehicle_class"], r["parts_tier"], company, when)
            hour = cfg["labour_rate"]["company_account" if company else "standard"][when]
            if abs(usd - r[money_key]) > 0.005 or r.get("labour_hour_" + money_key) != hour:
                bad.append(f"{nm}: {r['job']} ({r['vehicle_class']}, {r['parts_tier']}, {r['price_class']}) is {usd} at the hour of {hour}, the file says {r[money_key]} at {r.get('labour_hour_' + money_key)}")
            otd = round((usd + sup) * (1 + L["tax"]), 2)
            if "out_the_door_" + money_key in r and abs(otd - r["out_the_door_" + money_key]) > 0.005:
                bad.append(f"{nm}: {r['job']} out the door is {otd}")
            if "said_usd" in r or "said_" + money_key in r:
                said = r.get("said_" + money_key, r.get("said_usd"))
                base = otd if r.get("said_as") == "out the door" else usd
                if abs(said - base) > L["said_tolerance"](base):
                    bad.append(f"{nm}: '{r.get('said')}' ({said}) against {base}")
        if "quoted" in (d["verdict"]["result_public"].get("tags") or []) and not facts.get("prices"):
            bad.append(f"{nm}: a price is said on the call (tag quoted) and the file states none in scenario.facts.prices")
        for key, v in (facts.get("ledger") or {}).items():
            nledger += 1
            if key not in ledger or val(key) != v:
                bad.append(f"{nm}: ledger {key} is {val(key) if key in ledger else 'missing'}, the file says {v}")
    ok(f"{nprices} prices are catalogue.json's for the car's class, the parts tier and the price class at the hour in force on the call's day, and each figure said aloud is that price in round speech; "
       f"{nledger} story amounts are the ledger's rows", not bad, "; ".join(bad[:8]))

    bad = []
    addr = {s: val(f"geo.address.{s}") for s in ("main", "east", "west")}
    short = val("geo.short_name")
    street = {s_: (re.match(r"(\d+)", addr[s_]).group(1), short[s_]) for s_ in addr} if lang == "en" else {}
    for n, d in sorted(texted.items()):
        nm, site = d["_name"], d["call"]["site"]
        spoken = " ".join(s["text"] for s in d["transcript"]["segments"] if s["speaker_label"] == "manager")
        for other, (num, name) in street.items():
            for m in re.finditer(r"\b(\d{3,5}) " + re.escape(name), spoken):
                if other != site or m.group(1) != num:
                    bad.append(f"{nm}: the advisor at {site} says '{m.group(0)}'; the shop is at {addr[site]}")
        # a language whose address is said street first, house number after it ("Московское шоссе, 40")
        for other, (name, num) in L.get("streets", {}).items():
            for m in re.finditer(name + r",? (?:дом )?(\d{1,3})\b", spoken):
                if other != site or m.group(1) != num or num not in addr[site]:
                    bad.append(f"{nm}: the advisor at {site} says '{m.group(0)}'; the shop is at {addr[site]}")
    if not street and not L.get("streets"):
        say("  note  no address pattern for this language: the addresses said are not checked")
    hours = val("site.hours.weekday")
    for n, d in sorted(calls.items()):
        c, nm = d["call"], d["_name"]
        if not (hours[0] <= c["local_start"] <= hours[1]):
            bad.append(f"{nm}: {c['local_start']} is outside opening hours {hours}")
        if re.search(r"T-\d+ ?d", c["day"]) or "rule R6" not in c["day"]:
            bad.append(f"{nm}: call.day is not an anchor of rule R6")
        want = L["dates"].get(n)
        if want:
            dt = c["nominal_date"]
            if (isinstance(want, tuple) and not want[0] <= dt <= want[1]) or (isinstance(want, str) and dt != want):
                bad.append(f"{nm}: nominal date {dt}, the anchor falls on {want}")
        if L["weekend_closed"] and datetime.date.fromisoformat(c["nominal_date"]).weekday() > 4:
            bad.append(f"{nm}: {c['nominal_date']} is not a weekday")
        if n in L["times"] and c["local_start"] != L["times"][n]:
            bad.append(f"{nm}: starts {c['local_start']}, section 6 says {L['times'][n]}")
        t0 = datetime.date.fromisoformat(L["nominal_t"])
        if c.get("nominal_offset") != f"T-{(t0 - datetime.date.fromisoformat(c['nominal_date'])).days}d":
            bad.append(f"{nm}: nominal_offset against nominal_date")
        for fd in d.get("floating_days", []):
            if not re.fullmatch(r"call(?:[+-]\d+d)?|any", fd.get("day", "")):
                bad.append(f"{nm}: floating day {fd}")
        if L.get("weekdays") and n in texted:
            listed = " ".join(fd.get("word", "") for fd in d.get("floating_days", []))
            spoken = " ".join(t["said"] for t in d["script"]) + " " + json.dumps(d.get("judge_answer") or {}, ensure_ascii=False)
            for w in sorted(set(L["weekdays"].findall(spoken))):
                if w not in listed:
                    bad.append(f"{nm}: the weekday word '{w}' is said and is not in floating_days")
    if not L["dates"]:
        say("  note  no table of nominal dates for this language: the dates the anchors fall on are not checked")
    first = [calls[n]["call"].get("first_desk") for n in (18, 19, 20) if n in calls]
    want_first = [RU_MISS_DESKS[n] for n in (18, 19, 20)] if lang == "ru" else [str(x) for x in val("s1.a5")["miss_first_desks"]]
    if first != want_first:
        bad.append(f"A5's misses rang {first} first; the ledger says {want_first}")
    if 17 in calls and all(n in calls for n in (18, 19, 20)):
        base = datetime.date.fromisoformat(calls[17]["call"]["nominal_date"])
        gaps = [(datetime.date.fromisoformat(calls[n]["call"]["nominal_date"]) - base).days for n in (18, 19, 20)]
        if gaps != val("s1.a5")["miss_days_after_the_call"]:
            bad.append(f"A5's misses are {gaps} days after call 17; the ledger says {val('s1.a5')['miss_days_after_the_call']}")
    ok("addresses said are the shop's own; every call is inside opening hours, on its rule-R6 anchor and on the date that anchor falls on for the nominal T; every weekday said aloud is listed with its offset; "
       "A5's three misses ring the ledger's desks first, 1, 6 and 9 days after call 17", not bad, "; ".join(bad[:8]))

    bad = []
    wp = {}
    for n, d in judged.items():
        for a in d["verdict"]["result_public"]["auto_fails"]:
            wp.setdefault((d["cast"]["advisor"]["slot"], a["key"]), []).append(n)
    if len(wp.get((7, "wrong_promise"), [])) != val("p07.wrong_promise"):
        bad.append(f"slot 7 has {wp.get((7, 'wrong_promise'), [])} with wrong_promise; the ledger plants exactly {val('p07.wrong_promise')}")
    for (slot, key), ns in wp.items():
        if slot in (5, 6, 16, 24, 29):
            bad.append(f"slot {slot} carries {key} in calls {ns}; the ledger gives that slot none")
    if 7 in calls:
        f7 = calls[7]["scenario"].get("facts", {})
        if f7.get("driver_limit_usd", f7.get("driver_limit")) != val("s4.driver_limit") or not f7.get("found_work_usd", f7.get("found_work", 0)) > val("s4.driver_limit"):
            bad.append("call 7: the found work is not over the ledger's driver limit")
    ok("auto-fails by person agree with the ledger: slot 7 has exactly its two planted wrong promises, and the slots the ledger gives none have none; call 7's found work is over the driver's limit", not bad, "; ".join(bad))

    # ------------------------------------------------------------------------------------------------ 6. recognition
    say("\n6. The recognition model of DESIGN.md section 4, over the set")
    R = L["rates"]
    bad = []
    for key, cell in L["design_rate_cells"].items():
        row = next((ln for ln in design.split("\n") if ln.startswith(f"| {key} |")), "")
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[3 + L["column"]] != cell:
            bad.append(f"{key}: the design's rate cell is '{cells[3 + L['column']] if len(cells) >= 5 else row}', this script holds '{cell}'")
    prof_md = {}
    for ln in design.split("\n"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0] in ("light", "marked", "heavy", "no conversation"):
            prof_md[cells[0].split()[0] if cells[0] != "no conversation" else "none"] = int(cells[3 + L["column"]])
    if prof_md != L["profiles"] or list(val("calls.recognition.profiles")) != [L["profiles"][k] for k in ("light", "marked", "heavy", "none")]:
        bad.append(f"profiles: design {prof_md}, ledger {val('calls.recognition.profiles')}, this script {L['profiles']}")
    if abs(val("calls.recognition.asr_poor") - R["asr_poor"] * 100) > 1e-9:  # 0.14 * 100 is not exactly 14 in floating point
        bad.append("asr_poor against the ledger")
    ok("the rates this script holds for the language are the cells of the design's tables and the ledger's rows (profiles, rules R2 to R12, asr_quality poor)", not bad, "; ".join(bad))

    N = len(texted)
    byp = {}
    bad = []
    for n, d in sorted(texted.items()):
        r, nm = d["recognition"], d["_name"]
        byp.setdefault(r["profile"], []).append(n)
        tier = {"light": ("high", 0.55, 1.0), "marked": ("medium", 0.2, 0.55), "heavy": ("low", 0.0, 0.2)}.get(r["profile"])
        if not tier or r["restoration_tier"] != tier[0] or not (tier[1] <= r["consensus_score"] <= tier[2]):
            bad.append(f"{nm}: profile {r['profile']}, tier {r['restoration_tier']}, consensus {r['consensus_score']}")
        if "counts" not in r:
            bad.append(f"{nm}: recognition.counts is missing (mentions and errors per rule; see calls/en/README.md)")
    ok("each call's profile, restoration tier and consensus score agree (above 0.55, from 0.2, below); each carries its counts", not bad, "; ".join(bad[:8]))
    have_counts = all("counts" in d["recognition"] for d in texted.values())

    exp = {k: N * L["profiles"][k] / 100 for k in ("light", "marked", "heavy")}
    got = {k: len(byp.get(k, [])) for k in ("light", "marked", "heavy")}
    ok(f"profiles: light {got['light']}, marked {got['marked']}, heavy {got['heavy']} of {N}; the design's shares give {exp['light']:.1f}, {exp['marked']:.1f}, {exp['heavy']:.1f} "
       f"(and {N * L['profiles']['none'] / 100:.1f} with no conversation, which a call with text cannot be)",
       all(abs(got[k] - exp[k]) <= 1.0 for k in exp), f"marked: {byp.get('marked')}, heavy: {byp.get('heavy')}")
    poor = [n for n, d in judged.items() if d["verdict"]["result_public"]["asr_quality"] == "poor"]
    bad = [n for n in poor if texted[n]["recognition"]["profile"] == "light"] + [n for n in byp.get("heavy", []) if n in judged and n not in poor]
    ok(f"asr_quality poor: {len(poor)} of {len(judged)} judged calls ({100 * len(poor) / len(judged):.1f} %; the design: {R['asr_poor'] * 100:g} %); every heavy call is poor and no light call is "
       f"(calls {sorted(poor)})", abs(len(poor) - R["asr_poor"] * len(judged)) <= 1.0 and not bad, bad)

    bad, diffs = [], {}
    for n, d in sorted(texted.items()):
        r = d["recognition"]
        sw = words(" ".join(t["said"] for t in d["script"] if t["who"] != "hold"))
        tw = words(" ".join(s["text"] for s in d["transcript"]["segments"]))
        diff = lev(sw, tw) / len(sw)
        diffs[n] = diff
        if abs(diff - r["strict_word_difference"]) > 0.025 or abs(len(sw) - r["script_words"]) > 3 or abs(len(tw) - r["stored_words"]) > 6:
            bad.append(f"{d['_name']}: states {r['strict_word_difference']} over {r['script_words']} and {r['stored_words']} words; counted {diff:.3f} over {len(sw)} and {len(tw)}")
        lo, hi = L["word_diff"][r["profile"]]
        if not lo - 0.01 <= diff <= hi + 0.01:  # a point of slack: the samples' own figures were counted a little differently
            bad.append(f"{d['_name']}: word difference {diff:.3f} is outside {r['profile']}'s {lo} to {hi}")
    mean = sum(diffs.values()) / len(diffs)
    means = {k: sum(diffs[n] for n in ns) / len(ns) for k, ns in byp.items()}
    ok("word difference between script and stored lines (digits count as different from words): " + ", ".join(f"{k} {100 * v:.1f} %" for k, v in sorted(means.items()))
       + f"; mean {100 * mean:.1f} %; each call inside its profile's range and equal to the figure its file states",
       not bad and L["word_diff"]["mean"][0] <= mean <= L["word_diff"]["mean"][1], "; ".join(bad[:8]) or f"mean {mean:.3f} outside {L['word_diff']['mean']}")

    if have_counts:
        C = {n: d["recognition"]["counts"] for n, d in texted.items()}
        tot = lambda k, f: sum(c[k][f] for c in C.values())
        # an entry marked "error": false is a rendering that is not a mistake (Russian: a name in the other script, the company's
        # hyphen, a spelled string heard right); for rules R2 to R4 only the mistakes stand against the counts of wrong mentions
        rules = lambda d, r: [a for a in d["recognition"]["applied"] if a["rule"] == r and not (r in ("R2", "R3", "R4") and a.get("error") is False)]
        bad = []
        for n, d in sorted(texted.items()):
            c, nm = C[n], d["_name"]
            script = " ".join(t["said"] for t in d["script"])
            if sum(1 for t in d["script"] if t.get("overlap")) != c["overlaps"]["said"]:
                bad.append(f"{nm}: overlaps in the script against the count")
            pairs = (("R2", c["names"]["wrong"] + c["first_names"]["wrong"]), ("R4", c["trade_terms"]["wrong"]), ("R8", c["speaker_swap_turns"]),
                     ("R9", int(c["hold"])), ("R12", c["invented_lines"]), ("R11", c["profanity"]),
                     ("R3", c["plates"]["wrong"] + c["vins"]["wrong"] + c["order_numbers"]["wrong"]))
            for rule, k in pairs:
                if bool(rules(d, rule)) != bool(k):
                    bad.append(f"{nm}: rule {rule} in 'applied' against a count of {k}")
            if bool(c["noise_bursts"]) != bool(rules(d, "R6") or rules(d, "R10")):
                bad.append(f"{nm}: noise bursts against rules R6 and R10 in 'applied'")
            if c["hold"] != any(t["who"] == "hold" for t in d["script"]):
                bad.append(f"{nm}: hold")
            if c["speaker_swap_turns"] and not 2 <= c["speaker_swap_turns"] <= 4:
                bad.append(f"{nm}: a swap is a run of 2 to 4 turns")
            for k in ("names", "first_names", "plates", "vins", "order_numbers", "trade_terms", "phones"):
                if c[k]["wrong"] > c[k]["mentions"]:
                    bad.append(f"{nm}: more wrong {k} than mentions")
            if c["money_time"]["as_digits"] > c["money_time"]["mentions"] or c["hesitations"]["dropped"] > c["hesitations"]["said"]:
                bad.append(f"{nm}: counts of numbers or hesitations")
            for a in d["recognition"]["applied"]:
                turns = a.get("script_turns") or ([a["script_turn"]] if a.get("script_turn") else [])
                if any(not 1 <= t <= len(d["script"]) for t in turns):
                    bad.append(f"{nm}: rule {a['rule']} names a turn the script does not have")
                if a["rule"] in ("R2", "R3", "R4") and isinstance(a.get("said"), str) and a["said"] and a["said"] not in script:
                    bad.append(f"{nm}: rule {a['rule']} says '{a['said']}' was said; it is not in the script")
        ok("each file's counts agree with its script and its list of applied rules (overlaps, swaps of 2 to 4 turns, hold, names, terms, spelled strings, invented lines)", not bad, "; ".join(bad[:8]))

        def rate(label, k, n, p, unit="of mentions"):
            good = near_rate(k, n, p)
            ok(f"{label}: {k} of {n} ({(100 * k / n if n else 0):.1f} %; the design: {100 * p:g} % {unit})", good and (n > 0 or p == 0))
        rate("R1 hesitations dropped", tot("hesitations", "dropped"), tot("hesitations", "said"), R["hesitations"], "of hesitations")
        rate("R1 fillers dropped", tot("fillers", "dropped"), tot("fillers", "said"), R["fillers"], "of fillers")
        rate("R2 surnames, companies and streets heard wrong", tot("names", "wrong"), tot("names", "mentions"), R["names"])
        rate("R2 first names heard wrong", tot("first_names", "wrong"), tot("first_names", "mentions"), R["first_names"])
        rate("R3 plates with a character wrong, dropped or regrouped", tot("plates", "wrong"), tot("plates", "mentions"), R["plates"])
        rate("R3 order numbers", tot("order_numbers", "wrong"), tot("order_numbers", "mentions"), R["order_numbers"])
        if tot("vins", "mentions"):
            rate("R3 VINs", tot("vins", "wrong"), tot("vins", "mentions"), R["vins"])
        else:
            say("  note  R3 VINs: no VIN is read out in the set, so the 70 % has nothing to be read on")
        rate("R4 trade words, makes and models replaced", tot("trade_terms", "wrong"), tot("trade_terms", "mentions"), R["trade_terms"], "of listed terms")
        nm_, nd_ = tot("money_time", "mentions"), tot("money_time", "as_digits")
        ok(f"R5 money, times and years as digits: {nd_} of {nm_} ({100 * nd_ / nm_:.1f} %; the design: {100 * R['digits']:g} %, words otherwise)", R["digits"] - 0.12 <= nd_ / nm_ <= min(1.0, R["digits"] + 0.12))
        rate("R5 money and time mentions with a wrong value", tot("money_time", "wrong"), nm_, R["money_wrong"])
        rate("R5 phone numbers that lose or change a digit", tot("phones", "wrong"), tot("phones", "mentions"), R["phones_wrong"])
        for prof in ("light", "marked", "heavy"):
            ns = byp.get(prof, [])
            if ns:
                k = sum(C[n]["noise_bursts"] for n in ns)
                ok(f"R6 noise bursts in {prof} calls: {k} in {len(ns)} calls ({k / len(ns):.2f} a call; the design: {R['bursts'][prof]:g})",
                   R["bursts"][prof] / 2 <= k / len(ns) <= 2 * R["bursts"][prof] or abs(k - R["bursts"][prof] * len(ns)) <= 1.0)
        minutes = sum(d["call"]["talk_s"] for d in texted.values()) / 60
        ov, lost, joined = (sum(c["overlaps"][f] for c in C.values()) for f in ("said", "lost", "joined"))
        ok(f"R7 overlaps: {ov} in {minutes:.0f} minutes of talk ({ov / minutes:.2f} a minute; the design: {R['overlaps_per_min']:g})", R["overlaps_per_min"] / 2 <= ov / minutes <= 2 * R["overlaps_per_min"])
        rate("R7 backchannels lost", lost, ov, R["overlap_lost"], "of overlaps")
        rate("R7 neighbouring turns joined", joined, ov, R["overlap_joined"], "of overlaps")
        for prof in ("light", "marked", "heavy"):
            ns = byp.get(prof, [])
            if ns:
                k = sum(1 for n in ns if C[n]["speaker_swap_turns"])
                ok(f"R8 speaker swaps in {prof} calls: {k} of {len(ns)} (the design: {100 * R['swap'][prof]:g} % of calls)", abs(k - R["swap"][prof] * len(ns)) <= 1.0)
        holds = [n for n in C if C[n]["hold"]]
        stored = [n for n in holds if any(a.get("stored") for a in rules(texted[n], "R9"))]
        rate("R9 calls with a hold", len(holds), N, R["hold"], "of calls")
        rate("R9 holds stored as a line of the manager's", len(stored), len(holds), R["hold_stored"], "of holds")
        badl = [n for n in C if C[n]["bad_line"]]
        rate("R10 bad mobile line", len(badl), N, R["bad_line"], "of calls")
        ok("R10 a call on a bad line is marked or heavy", all(texted[n]["recognition"]["profile"] != "light" for n in badl), badl)
        prof = [n for n in C if C[n]["profanity"]]
        ok(f"R11 profanity is the customer's, never the staff's: {len(prof)} call(s) carry it (calls {prof}); the design's 4 % is of existing-job calls in the whole seed, and the story set holds its angriest callers",
           len(prof) <= 2 and all(all(a.get("script_turn") is None or texted[n]["script"][a["script_turn"] - 1]["who"] == "customer" for a in rules(texted[n], "R11")) for n in prof))
        inv = [n for n in C if C[n]["invented_lines"]]
        rate("R12 a line the recogniser invented", len(inv), N, R["invented"], "of calls")
    else:
        ok("per-rule rates (R1 to R12)", False, "not checked: some files have no recognition.counts")

    # ------------------------------------------------------------------------------------------------ 7. rule R13
    say("\n7. Unclear customers (design rule R13)")
    unclear = {n: d["scenario"]["unclear"] for n, d in texted.items() if d["scenario"].get("unclear")}
    named = sorted(int(x) for x in re.findall(r"call (\d+) \(S\d", design.split("Unclear customers (design rule R13)")[1].split("\n")[0]))
    ok(f"the design names calls {named} as the hand-written calls that carry it, and this script expects {sorted(UNCLEAR)}", named == sorted(UNCLEAR))
    ok(f"exactly those calls carry a clarification loop: {sorted(unclear)} of {N} calls with text ({100 * len(unclear) / N:.0f} %; the ledger's {val('r13.calls.clarification_loop'):g} % is the background's rate, "
       "and the hand-written set carries it only where a card says so)", sorted(unclear) == sorted(UNCLEAR))
    bad = []
    for n, u in unclear.items():
        e = EXPECT[n].get("unclear", {})
        if u.get("resolved") != e.get("resolved"):
            bad.append(f"call {n}: resolved {u.get('resolved')}")
        if "asked_again" in e and u.get("asked_again") != e["asked_again"]:
            bad.append(f"call {n}: asked again {u.get('asked_again')} times")
        if u.get("resolved") is False and (u.get("asked_again") != 0 or calls[n]["verdict"]["result_public"]["outcome"] not in ("customer_will_call", "no_visit")):
            bad.append(f"call {n}: left unclear means nobody asked again and the call ends as customer_will_call or no_visit")
    unres = sorted(n for n, u in unclear.items() if u.get("resolved") is False)
    ok(f"call 21 is made clear after two questions and its need-discovery check is at level 2; call 16 is left unclear, not asked again, and ends as customer_will_call (left unclear: {unres})", not bad and unres == [16], "; ".join(bad))

    # ------------------------------------------------------------------------------------------------ summary
    say("")
    how = (f"{derived} of {len(judged)} verdicts derived again by the product's judge.verdict" if derived is not None else f"{len(judged)} scores checked by the formula")
    say(f"{len(texted)} calls with text, {len(misses)} misses; {len(judged)} judged, {len(texted) - len(judged)} outbound; {how}.")
    say("RESULT " + ("PASS" if not FAILS else f"FAIL ({len(FAILS)}): " + "; ".join(x[:70] for x in FAILS[:6])))
    print("\n".join(OUT))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
