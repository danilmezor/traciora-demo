#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks the English call bank (calls/bank-en/) against calls/DESIGN.md section 6 and its own FORMAT.md, and assembles a sample.

    python3 checks/check_bank_en.py            # writes checks/bank_en_check.txt and calls/bank-en/assembled-sample.md

Checks: the count of every piece against DESIGN.md section 6; every slot used is declared in FORMAT.md; no digit, weekday,
month, 'tomorrow', spelled clock time or spelled money outside a slot; no advisor line repeated by another advisor; every
advisor has 8 checks x 3 levels x 4 wordings; every job block, voice and unclear opening is complete. Then 60 clean scripts
are assembled from the pieces with a fixed seed (slots filled from the catalogue, parc, cast, accounts and vendors) and the
share of exact duplicate lines across them is reported; it must be under 3 %. Exit code 1 when a check fails. Not product code.
"""
import glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
BANK = os.path.join(SEED, "calls", "bank-en")
OUT_TXT = os.path.join(HERE, "bank_en_check.txt")
OUT_MD = os.path.join(BANK, "assembled-sample.md")
RANDOM_SEED = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 20261113
N_SAMPLE = 60
DUP_LIMIT = 0.03
MIN_WORDS_FOR_DUP = 4

CHECKS = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")
SHORT = {"greeting": "g", "name_and_number": "n", "need_discovery": "d", "price_with_next_step": "p", "offered_time": "t",
         "asked_for_booking": "b", "recap": "r", "objection": "o"}
SLOTS = ("5", "6", "7", "29", "16", "17", "22", "23", "24")
EXISTING_KINDS = ("ready", "not_ready", "part_late", "extra_work", "booking_moved", "pick_up", "bill", "complaint", "comeback", "lost_item")
VOICE_ROLES = ("opener", "filler", "tail", "open_price", "open_booking", "give_car", "react_price", "react_no_price", "yes", "no", "maybe",
               "pick_of_two", "accept_one", "name_own_time", "pause", "decline", "will_call", "doubt_price", "doubt_time", "doubt_trust",
               "doubt_think", "after_answer_ok", "after_answer_unsure", "give_name", "give_number", "ask_duration", "backchannel", "thanks_bye")
MOVES = ("ack", "ask_what", "ask_name", "ask_number", "recognise", "lookup", "hold", "back_from_hold", "explain", "duration", "probe",
         "outbound_open", "closing_booked", "closing_open")
UNCLEAR_KINDS = {"vague": 6, "wrong_thing": 5, "two_in_one": 4, "wrong_way_round": 5}

out = []
fails = []


def say(line=""):
    out.append(line)


def check(ok, what):
    say(("  ok    " if ok else "  FAIL  ") + what)
    if not ok:
        fails.append(what)


def load(name):
    with open(os.path.join(BANK, name)) as f:
        return json.load(f)


ne = load("skeletons-new-enquiry.json")["skeletons"]
jb = load("job-blocks.json")
jobs = jb["jobs"]
ej = load("skeletons-existing-job.json")["skeletons"]
EJ_CALLBACK = load("skeletons-existing-job.json")["callback_recap"]
oth = load("skeletons-other.json")
voices = load("voices.json")["voices"]
unclear = load("unclear.json")["openings"]
adv = {}
for s in SLOTS:
    with open(os.path.join(BANK, "advisors", s + ".json")) as f:
        adv[s] = json.load(f)

# ------------------------------------------------------------------------------------------------- speech strings
SPEECH_JOB_KEYS = ("job_said", "since_answers", "explain", "price_statement", "depends", "inspection_line", "found")


def strings_in(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, list):
        for y in x:
            yield from strings_in(y)
    elif isinstance(x, dict):
        for y in x.values():
            yield from strings_in(y)


def speech():
    """(where, text) for every line of speech in the bank."""
    for j in jobs:
        for k in SPEECH_JOB_KEYS:
            for t in strings_in(j.get(k)):
                yield "job %s.%s" % (j["key"], k), t
        for c in j["customer_says"]:
            yield "job %s.customer_says" % j["key"], c["need"]
        for q in j["questions"]:
            for t in strings_in(q):
                yield "job %s.questions" % j["key"], t
        for o in j["objections"]:
            for k in ("customer", "probe", "probe_reply", "answer_2", "answer_1", "answer_0"):
                for t in strings_in(o[k]):
                    yield "job %s.objections" % j["key"], t
    for typ, lst in jb["generic_objections"].items():
        for o in lst:
            for k in ("customer", "probe", "probe_reply", "answer_2", "answer_1", "answer_0"):
                for t in strings_in(o[k]):
                    yield "generic_objections.%s" % typ, t
    for vk, v in voices.items():
        for r in VOICE_ROLES:
            for t in strings_in(v.get(r)):
                yield "voice %s.%s" % (vk, r), t
    groups = [("new", ne), ("existing", ej)] + [(k, oth[k]) for k in ("supplier", "wrong_number", "other", "outbound")]
    for g, lst in groups:
        for sk in lst:
            for b in sk["beats"]:
                for t in strings_in(b.get("say")):
                    yield "skeleton %s.%s" % (sk["id"], b["role"]), t
    for lv in ("0", "1", "2"):
        for t in EJ_CALLBACK[lv]:
            yield "skeleton existing.callback_recap", t
    for u in unclear:
        for k in ("opening", "second_answer", "advisor_second", "third_answer", "unresolved_end"):
            for t in strings_in(u[k]):
                yield "unclear %s.%s" % (u["id"], k), t
    for s, a in adv.items():
        for t in strings_in(a["checks"]):
            yield "advisor %s.checks" % s, t
        for t in strings_in(a["moves"]):
            yield "advisor %s.moves" % s, t
        for t in strings_in(a["fillers"]):
            yield "advisor %s.fillers" % s, t
        for t in strings_in(a["tokens"]):
            yield "advisor %s.tokens" % s, t


SPEECH = list(speech())

# ------------------------------------------------------------------------------------------------- 1. counts
say("English call bank: check")
say("=" * 100)
say()
say("1. Pieces against DESIGN.md section 6")
check(len(ne) == 14, "new-enquiry skeletons: %d (14)" % len(ne))
check(len({s['id'] for s in ne}) == len(ne), "new-enquiry skeleton ids are unique")
check(len(jobs) == 24, "job blocks: %d (24)" % len(jobs))
kinds = {}
for s in ej:
    kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
check(len(ej) == 30, "existing-job skeletons: %d (30)" % len(ej))
check(all(kinds.get(k) == 3 for k in EXISTING_KINDS) and set(kinds) == set(EXISTING_KINDS),
      "existing-job kinds, three each: %s" % ", ".join("%s %d" % (k, kinds.get(k, 0)) for k in EXISTING_KINDS))
for k, n in (("supplier", 8), ("wrong_number", 5), ("other", 6), ("outbound", 10)):
    check(len(oth[k]) == n, "%s skeletons: %d (%d)" % (k, len(oth[k]), n))
reasons = {}
for s in oth["outbound"]:
    reasons[s["reason"]] = reasons.get(s["reason"], 0) + 1
check(set(reasons) == {"ready", "approval", "callback", "supplier", "confirm"},
      "outbound reasons cover DESIGN.md section 2 (ready 35, approval 25, callback 18, supplier 12, confirm 10): %s" % reasons)
want_voices = {"terse", "chatty", "anxious", "price_shopper", "elderly", "driver", "dispatcher", "angry"}
check(set(voices) == want_voices, "customer voices: %d %s" % (len(voices), sorted(voices)))
check(len(unclear) == 20, "unclear openings: %d (20)" % len(unclear))
uk = {}
for u in unclear:
    uk[u["kind"]] = uk.get(u["kind"], 0) + 1
check(all(uk.get(k, 0) >= 3 for k in UNCLEAR_KINDS), "unclear kinds: %s" % uk)
check(len(adv) == 9, "advisor files: %d (slots %s)" % (len(adv), ", ".join(SLOTS)))
adv_lines = sum(len([t for t in strings_in(a["checks"])]) + len([t for t in strings_in(a["moves"])]) for a in adv.values())
check(adv_lines >= 864, "advisor phrase bank lines: %d (about 900: 9 x 8 x 3 x 4 = 864 check wordings plus greetings, closings, moves)" % adv_lines)
say()

# ------------------------------------------------------------------------------------------------- 2. completeness
say("2. Completeness of each piece")
bad = []
for s, a in adv.items():
    for c in CHECKS:
        for lv in ("0", "1", "2"):
            ws = a["checks"].get(c, {}).get(lv, [])
            if len(ws) != 4 or any(not isinstance(w, str) or not w.strip() for w in ws):
                bad.append("%s %s %s (%d)" % (s, c, lv, len(ws)))
    for m in MOVES:
        if len(a["moves"].get(m, [])) < 2:
            bad.append("%s moves.%s" % (s, m))
    if a.get("tier") not in ("exact", "warm", "curt"):
        bad.append("%s tier" % s)
check(not bad, "every advisor: 8 checks x 3 levels x 4 wordings, every move, a tier%s" % ("" if not bad else ": " + "; ".join(bad[:8])))
bad = []
for s, a in adv.items():
    g2 = a["checks"]["greeting"]["2"]
    first = a["name"].split()[0]
    if not all("Brennan" in w and first in w for w in g2):
        bad.append(s)
check(not bad, "greeting level 2 names the business and the advisor in every wording%s" % ("" if not bad else ": " + ", ".join(bad)))
bad = []
for s, a in adv.items():
    c = a["checks"]
    if not all("{customer_phone_said}" in w for w in c["name_and_number"]["2"]): bad.append("%s name 2 says the number back" % s)
    if any("{customer_phone_said}" in w for w in c["name_and_number"]["1"]): bad.append("%s name 1 must not repeat the number" % s)
    if not all("{time_1}" in w and "{time_2}" in w for w in c["offered_time"]["2"]): bad.append("%s time 2 has two options" % s)
    if any("{time_2}" in w for w in c["offered_time"]["1"]): bad.append("%s time 1 has one option" % s)
    if any("{time_1}" in w for w in c["offered_time"]["0"]): bad.append("%s time 0 offers no time" % s)
    if not all("{time_chosen}" in w for w in c["asked_for_booking"]["2"]): bad.append("%s booking 2 names the time" % s)
    if not all("{time_chosen}" in w and "{shop_address}" in w and "{job_said}" in w for w in c["recap"]["2"]): bad.append("%s recap 2 time, address, work" % s)
    if any("{shop_address}" in w for w in c["recap"]["1"]): bad.append("%s recap 1 leaves the address out" % s)
    if not all("{objection_answer}" in w for w in c["objection"]["2"]): bad.append("%s objection 2 carries the answer" % s)
    if not all(("{depends}" in w or "{inspection_line}" in w) for w in c["price_with_next_step"]["2"]): bad.append("%s price 2 says what it depends on" % s)
    if any("{depends}" in w or "{inspection_line}" in w for w in c["price_with_next_step"]["1"]): bad.append("%s price 1 is bare" % s)
    if any("{price" in w for w in c["price_with_next_step"]["0"]): bad.append("%s price 0 gives no price" % s)
    if not any("{inspection_line}" in w for w in c["price_with_next_step"]["2"]): bad.append("%s price 2 has an inspection wording" % s)
check(not bad, "each level's wordings carry what the rubric's anchor asks for%s" % ("" if not bad else ": " + "; ".join(bad[:10])))
bad = []
for j in jobs:
    ks = [c["kind"] for c in j["customer_says"]]
    if len(ks) < 6 or "vague" not in ks or "wrong" not in ks: bad.append("%s customer_says" % j["key"])
    if len(j["questions"]) < 3 or any(len(q["answers"]) < 2 for q in j["questions"]): bad.append("%s questions" % j["key"])
    if not j["price_statement"] or not j["depends"]: bad.append("%s price" % j["key"])
    if len(j["objections"]) < 3: bad.append("%s objections" % j["key"])
    for o in j["objections"]:
        if not all(o.get(k) for k in ("customer", "probe", "probe_reply", "answer_2", "answer_1", "answer_0")): bad.append("%s objection %s" % (j["key"], o.get("type")))
    for k in ("price", "price_alt", "inspection_price"):
        pass
check(not bad, "every job block: 6+ wordings with vague and wrong ones, 3 questions, price and what it depends on, 3 objections at 3 levels%s" % ("" if not bad else ": " + "; ".join(bad[:8])))
CAT = json.load(open(os.path.join(SEED, "catalogue.json")))
CATJ = {j["key"]: j for j in CAT["jobs"]}
bad = [j["key"] for j in jobs if any(v and v not in CATJ for v in j["catalogue"].values())]
check(not bad, "every job block's catalogue keys exist in catalogue.json%s" % ("" if not bad else ": " + ", ".join(bad)))
bad = []
for vk, v in voices.items():
    for r in VOICE_ROLES:
        if not v.get(r):
            bad.append("%s.%s" % (vk, r))
    for r in ("open_price", "open_booking"):
        if any("{need}" not in w for w in v.get(r, [])):
            bad.append("%s.%s without {need}" % (vk, r))
check(not bad, "every voice has every customer role (%d roles), and its openings carry {need}%s" % (len(VOICE_ROLES), "" if not bad else ": " + "; ".join(bad[:8])))
bad = []
for u in unclear:
    if not (u["opening"] and u["second_answer"] and u["unresolved_end"]): bad.append(u["id"])
    if set(u["advisor_second"]) != {"0", "1", "2"} or set(u["third_answer"]) != {"0", "1", "2"}: bad.append(u["id"] + " levels")
    if u["resolves_to"] != "need" and u["resolves_to"] not in {j["key"] for j in jobs}: bad.append(u["id"] + " resolves_to")
check(not bad, "every unclear opening has the caller's second and third answers and the advisor's second question at 0, 1, 2%s" % ("" if not bad else ": " + ", ".join(bad)))
say()

# ------------------------------------------------------------------------------------------------- 3. slots and typed amounts
say("3. Slots and typed amounts")
fmt = open(os.path.join(BANK, "FORMAT.md")).read()
table = fmt.split("## Slots", 1)[1].split("\n## ", 1)[0]
declared = set()
for row in table.splitlines():
    if row.startswith("| `{"):
        first = row.split("|")[1]
        declared |= set(re.findall(r"\{([a-z_0-9]+)\}", first))
used = {}
for where, t in SPEECH:
    for s in re.findall(r"\{([a-z_0-9]+)\}", t):
        used.setdefault(s, where)
undeclared = sorted(set(used) - declared)
check(not undeclared, "every slot used is declared in FORMAT.md (%d used, %d declared)%s" % (len(used), len(declared), "" if not undeclared else ": " + ", ".join("%s (%s)" % (s, used[s]) for s in undeclared)))
unused = sorted(declared - set(used))
say("        declared and not written as a slot in the bank (named in FORMAT.md's role tables): %s" % (", ".join(unused) or "none"))
NUMW = r"(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|noon|midnight)"
pat_digit = re.compile(r"\d")
pat_week = re.compile(r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mondays|Tuesdays|Wednesdays|Thursdays|Fridays|Saturdays|Sundays|January|February|March|April|June|July|August|September|October|November|December|tomorrow)\b", re.I)
pat_clock = re.compile(r"\b(at|by|till|until|around|before|after)\s+" + NUMW + r"(-thirty|-fifteen|-forty-five|\s+o'clock)?\b", re.I)
pat_money = re.compile(r"\b(dollars?|bucks|cents)\b", re.I)
bad = []
for where, t in SPEECH:
    bare = re.sub(r"\{[a-z_0-9]+\}", "", t)
    for name, p in (("digit", pat_digit), ("weekday, month or tomorrow", pat_week), ("clock time", pat_clock), ("money word", pat_money)):
        m = p.search(bare)
        if m:
            bad.append("%s: %s in %r" % (where, name, t))
check(not bad, "no digit, weekday, month, 'tomorrow', spelled clock time or money word outside a slot (%d lines read)%s" % (len(SPEECH), "" if not bad else ":\n          " + "\n          ".join(bad[:15])))
say()

# ------------------------------------------------------------------------------------------------- 4. advisors' own voices
say("4. Each advisor's lines are their own")


def norm(t):
    t = t.lower().replace("’", "'")
    t = re.sub(r"[^a-z0-9{}_' ]+", " ", t)
    return " ".join(t.split())


owner = {}
dups = []
for s, a in adv.items():
    seen = set()
    for t in list(strings_in(a["checks"])) + list(strings_in(a["moves"])):
        if t == "<skip>":
            continue
        n = norm(t)
        if n in seen:
            continue
        seen.add(n)
        if n in owner and owner[n] != s:
            dups.append("%r: slots %s and %s" % (t, owner[n], s))
        owner.setdefault(n, s)
check(not dups, "no line of one advisor is repeated by another, ignoring case and punctuation (%d distinct lines)%s" % (len(owner), "" if not dups else ":\n          " + "\n          ".join(dups[:20])))
say()

# ------------------------------------------------------------------------------------------------- 5. sample assembly
say("5. Sample assembly: %d clean scripts, random seed %d" % (N_SAMPLE, RANDOM_SEED))
rnd = random.Random(RANDOM_SEED)
CAST = json.load(open(os.path.join(SEED, "cast.json")))["people"]
PARC = json.load(open(os.path.join(SEED, "parc.json")))["configurations"]["en"]["models"]
ACC = json.load(open(os.path.join(SEED, "accounts.json")))["en"]["accounts"]
VEND = json.load(open(os.path.join(SEED, "vendors.json")))["en"]
person = {p["slot"]: p for p in CAST}
SITE_OF = {s: person[s]["site"] for s in SLOTS}
FIRST = {s: person[s]["en"]["customers_call"].split(";")[0].strip() for s in SLOTS}
SITE = {
    "main": dict(shop_address="twenty-one-oh-six East Main Street", shop_short="East Main", techs=["Kevin", "Luis", "Terry", "Hunter", "Cody", "Randy"],
                 manager="Greg", area="four two three", advisors=["5", "6", "7", "29"], weights=[34, 34, 26, 6]),
    "east": dict(shop_address="sixty-three-forty Bonny Oaks Drive", shop_short="Bonny Oaks", techs=["Andre", "Brandon", "Austin", "Jordan"],
                 manager="Greg", area="four two three", advisors=["16", "17"], weights=[55, 45]),
    "west": dict(shop_address="sixty-three-ninety-nine Charlotte Pike", shop_short="Charlotte Pike", techs=["Gary", "Shane", "Derek", "Tyler"],
                 manager="Dale", area="six one five", advisors=["22", "23", "24"], weights=[15, 47, 38]),
}
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def w2(n):
    if n < 20:
        return ONES[n]
    t, o = divmod(n, 10)
    return TENS[t] + ("-" + ONES[o] if o else "")


def w3(n):
    if n < 100:
        return w2(n)
    h, r = divmod(n, 100)
    if r == 0:
        return ONES[h] + " hundred"
    return ONES[h] + " " + ("oh-" + ONES[r] if r < 10 else w2(r))


def money(x):
    x = round(x, 2)
    d, c = int(x), int(round((x - int(x)) * 100))
    if d >= 1000:
        a, b = divmod(int(round(x)), 100)
        return w2(a) + " " + ("hundred" if b == 0 else ("oh-" + ONES[b] if b < 10 else w2(b)))
    if d >= 200 or c == 0:
        return w3(int(round(x)) if d >= 200 else d)
    return w3(d) + " " + ("oh-" + ONES[c] if c < 10 else w2(c))


def digits_said(s):
    names = "oh one two three four five six seven eight nine".split()
    return " ".join(names[int(ch)] for ch in s if ch.isdigit())


PARTS_CLASS = {"car": 1.0, "suv": 1.15, "truck": 1.3, "van": 1.3}


def price(key, cls, company=False):
    if not key:
        return None
    e = CATJ[key]["en"]
    f = (e.get("hours_by_class") or {}).get(cls) or 1.0
    if e["labour_pricing"] == "menu":
        lab = (e["labour_price_company"] if company else e["labour_price"])["after_rise"] * f
    else:
        lab = e["hours"] * f * (121.5 if company else 135.0)
    parts = 0.0
    for p in e["parts"]:
        opts = {o["tier"]: o for o in p["options"]}
        o = opts.get("standard") or list(opts.values())[0]
        parts += o["list_price"] * p["qty"] * (PARTS_CLASS[cls] if e.get("parts_scale_with_class") else 1.0)
    if company:
        parts *= 0.9
    parts += sum(fee.get("price", 0) for fee in e["fees"])
    return round(lab + parts, 2)


def duration(key):
    h = CATJ[key]["en"]["hours"] if key else 1.0
    if h <= 0.35: return "twenty minutes or so"
    if h <= 0.6: return "half an hour"
    if h <= 1.1: return "an hour"
    if h <= 1.6: return "an hour and a half"
    if h <= 2.2: return "a couple hours"
    if h <= 3.3: return "most of the morning"
    return "the better part of the day"


DAYS = ["tomorrow", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "this afternoon"]
HOURS = ["at seven-thirty", "at eight", "at nine", "at ten", "at eleven", "at one", "at one-thirty", "at two", "at three"]


def two_times():
    a = rnd.choice(DAYS)
    b = rnd.choice([d for d in DAYS if d != a] + [a])
    ha = rnd.choice(HOURS[:5] if a != "this afternoon" else HOURS[6:])
    hb = rnd.choice([h for h in (HOURS[:5] if b != "this afternoon" else HOURS[6:]) if not (b == a and h == ha)])
    return a + " " + ha, b + " " + hb


FN_M = "Dwayne Russell Kenny Clint Jerry Darrell Wesley Tony Randall Corey Lamar Glen Dewayne Rodney Scotty Jimmy Calvin Terrell Mitchell Rusty Duane Gordon Leon Kirk Darnell Jody Lyle Ervin Clayton Homer Roger Benny Alvin Cecil Floyd Marvin Troy Shannon Chuck Dewey Otis Garland Jessie Royce Elmer Larry Grady Buford Tyrone Keith Donnie".split()
FN_F = "Tammy Crystal Shelia Brandy Lisa Monica Rhonda Ashley Kendra LaToya Misty Paula Renee Wanda Heather Jolene Tracy Amber Gail Lori Bonnie Kristy Darlene Patsy Charlene Loretta Becky Trina Rita Vickie Dottie Kim Leann Stacy Marcy Tonia Lacey Jeanette Wilma Faye Robin Bridget Carrie Janice Melba Ruby Sabrina Yvonne Gloria Dana Krista Opal".split()
LN = "Cagle Lusk Haggard Moody Varner Bledsoe Crowe Rhea Shipley Duggan Puckett Hatfield Lovell Ogle Brewer Kilgore Talley Spurlock Whitson Yates Bales Grigsby Lyle Mayfield Neeley Orr Pendergrass Rakestraw Cofer Holcomb Ashburn Beasley Dalton Eldridge Farris Gaddis Helton Ingle Jolley Kyle Ledbetter McCoy Nance Overby Pack Quarles Raines Sexton Tipps Upchurch Vann Wooten Ayers Crisp Dodd Estes Frye".split()
MODELS = [m for m in PARC]
PHONES = list(range(10, 100))  # each sample caller a number of their own in the 555-01xx block
FN_F_CONTACT = {"Tina", "Linda", "Joyce", "Yolanda", "Denise", "Sherry", "Erin", "Marianne"}
ACC_USE = [a for a in ACC if a["id"] in ("A1", "A2", "A3", "A4")]


def said_model(name):
    """A model name as it is said: digits in words (F-150 -> F-one-fifty, 1500 -> fifteen hundred, CX-5 -> CX-five)."""
    def num(m):
        n = int(m.group(0))
        if n >= 1000 and n % 100 == 0:
            return w2(n // 100) + " hundred"
        if n >= 100:
            return ONES[n // 100] + "-" + (w2(n % 100) if n % 100 >= 10 else ("oh-" + ONES[n % 100] if n % 100 else "hundred"))
        return w2(n)
    name = name.split(" / ")[0].split("/")[0].strip()
    name = re.sub(r"(?<=[A-Za-z])(?=\d)", "-", name).replace("Model-", "Model ")
    return re.sub(r"\d+", num, name)


def draw_car(cls=None):
    pool = [m for m in MODELS if (cls is None or m["vehicle_class"] == cls)]
    m = rnd.choices(pool, weights=[x["share"] for x in pool])[0]
    y = rnd.randint(max(m["year_from"], 2006), min(m["year_to"] or 2024, 2024))
    return m, y


def styled(slot):
    st = adv[slot]["style_sheet"]
    if "first" in st:
        lam = rnd.random()
        return {c: [(1 - lam) * st["first"][c][i] + lam * st["last"][c][i] for i in range(3)] for c in CHECKS}
    return st


def deal(sheet, c):
    return rnd.choices([0, 1, 2], weights=sheet[c])[0]


def pick(lst, ctx=None):
    lst = [x for x in lst if x]
    if ctx is not None and ctx.get("_known") is False:
        lst = [x for x in lst if not re.search(r"\b(hon|buddy)\b", x)] or lst
    if ctx is not None:
        ok = [x for x in lst if all(ctx.get(s) is not None for s in re.findall(r"\{([a-z_0-9]+)\}", x))]
        lst = ok or lst
    return rnd.choice(lst) if lst else None


def vpick(role, ctx):
    """A voice's wording for a role: a list of wordings, or {"parts": [...]} joined one piece from each part."""
    if isinstance(role, dict):
        out = ""
        for part in role["parts"]:
            piece = rnd.choice(part)
            if not piece:
                continue
            if out and out.rstrip().endswith((",", "—")) and piece[:2] not in ("I ", "I'") and not piece.startswith("{"):
                piece = piece[0].lower() + piece[1:]
            out = (out + " " + piece).strip() if out else piece
        return out
    return pick(role, ctx)


def fill(t, ctx):
    t = re.sub(r"\b(the|your|that|my) \{(job_said|found_job_said|second_job_said)\}",
               lambda m: m.group(1) + " " + re.sub(r"^(an?|the) ", "", str(ctx.get(m.group(2)) or "")) if ctx.get(m.group(2)) else m.group(0), t)
    for _ in range(4):
        n = re.sub(r"\{([a-z_0-9]+)\}", lambda m: str(ctx[m.group(1)]) if ctx.get(m.group(1)) is not None else m.group(0), t)
        if n == t:
            break
        t = n
    return t


def tidy(t):
    t = t.strip()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\b([Aa]) ([AEIOU][a-z])", lambda m: m.group(1) + "n " + m.group(2), t)
    t = re.sub(r"\b([Aa]) (F-|RX|MDX|RDX|SRX|XC|X[0-9]|eight|eleven|oh-)", lambda m: m.group(1) + "n " + m.group(2), t)
    t = re.sub(r"\ban ([AEIOU][a-z]*) ([A-Z])", lambda m: m.group(0), t)
    t = re.sub(r"— (We|That|That's|It|It's|If|The|This|Our|They|You|Your|Most|Some|Then)\b", lambda m: "— " + m.group(1).lower(), t)
    if t and t[0].isalpha():
        t = t[0].upper() + t[1:]
    t = re.sub(r"([.?!]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), t)
    t = re.sub(r"([?!])\s*\1", r"\1", t)
    t = re.sub(r"(?<!\.)\.\s+\.(?!\.)", ".", t)
    if t and t[-1] not in ".?!—-…" and not t.endswith("..."):
        t += "."
    return t


def swap_gender(t, sx):
    """A caller's words about a spouse follow the caller's sex."""
    if sx == "m":
        t = re.sub(r"\bhusband\b", "wife", t)
        t = re.sub(r"\b(Honey|Sweetheart), ", "", t)
        t = re.sub(r", (honey|sweetheart)\b", "", t)
        t = re.sub(r"\bThank you, (honey|sweetheart)\.", "Thank you.", t)
    else:
        t = re.sub(r"\bwife\b", "husband", t)
    return t


def voice_wrap(line, v, first, party_customer=True, tail=False):
    if not party_customer:
        return line
    lead_word = line.split(" ")[0].lower().strip(",.!?—")
    if first:
        if v["opener"] and rnd.random() < 0.6:
            line = rnd.choice(v["opener"]) + " " + line
    else:
        line = lead(line, v["filler"], v["filler_rate"])
    if (first or tail) and rnd.random() < v["tail_rate"]:
        tl = rnd.choice(v["tail"])
        line = line.rstrip(" .?!")
        line = line + tl if tl[0] in ",." else line + " " + tl
    return line


DISCOURSE = {"and", "but", "right", "sorry", "okay", "alright", "all", "well", "so", "now", "yeah", "yes", "uh", "um", "gotcha", "cool", "great", "perfect", "sure", "mm", "oh", "look", "listen", "man", "i", "yep", "hey", "hi", "hello", "thank", "thanks", "good", "brennan", "bonny", "charlotte", "front", "counter", "east"}


def lead(t, fillers, p):
    """The generator's spoken variation: a speaker's own discourse word before a generic line, at the speaker's rate.
    A line that already opens with a discourse word has it swapped for another of the speaker's, or dropped."""
    if not fillers or rnd.random() >= p or len(t.split()) <= 3 or t.startswith(("Bye", "Thank")):
        return t
    m = LEAD_RE.match(t)
    if m:
        rest = t[m.end():]
        if not rest:
            return t
        if rnd.random() < 0.5:
            return rest[0].upper() + rest[1:] if not rest.startswith("{") else rest
        f = rnd.choice(fillers)
        return f + " " + (rest[0].lower() + rest[1:] if rest[:2] not in ("I ", "I'") and not rest.startswith("{") else rest)
    w = re.sub(r"^[^A-Za-z{]+", "", t).split(" ")[0].lower().strip(",.!?—")
    if w in DISCOURSE or w.startswith("{"):
        return t
    f = rnd.choice(fillers)
    if f.strip(" .") == "":
        return f + t
    return f + " " + t[0].lower() + t[1:] if t[:2] != "I " and t[:2] != "I'" else f + " " + t


LEAD_RE = re.compile(r"^((Okay|Alright|All right|Well|So|Now|Yeah|Yes \{sir_maam\}|Uh|Um|Gotcha|Cool|Great|Perfect|Sure|Mm-hm|Mm|Oh|Yep|Good|Wonderful)[,.!]?\s+)+(?=[A-Za-z{])", re.I)


def address(t, terms, p):
    """The generator's spoken variation: a term of address before the line's last stop, at the speaker's rate."""
    if not terms or rnd.random() >= p or len(t.split()) > 12 or re.search(r"\{customer_first\}|\{customer_title\}|\{sir_maam\}|\bhon\b|\bbuddy\b|\bman\b|\bhoney\b", t):
        return t
    m = re.match(r"^(.*?)([.?!]*)$", t.rstrip(), re.S)
    body, stop = m.group(1), m.group(2) or "."
    last = body.split(" ")[-1] if body.split(" ") else ""
    if body.endswith((",", "—", "...", "}")) or (last[:1].isupper() and last not in ("I", "OK")):
        return t
    return body + rnd.choice(terms) + stop


def echo(job_said, tier):
    """The generator's spoken variation: the advisor says the job back before the first question."""
    j = re.sub(r"^(an?|the) ", "", job_said)
    if tier == "curt":
        return j[0].upper() + j[1:] + "."
    return rnd.choice(["%s, okay." % (j[0].upper() + j[1:]), "Okay, %s." % j, "%s, sure." % (j[0].upper() + j[1:]), "Alright, %s." % j])


def when_ok(cond, st):
    if not cond:
        return True
    expr = cond
    expr = re.sub(r"\bL\.([a-z_]+)", r"L['\1']", expr)
    expr = expr.replace("not ", " not ")
    env = dict(L=st["L"], price_asked=st["price_asked"], doubt=st["doubt"], known=st["known"], ot_na=st["ot_na"],
               booked=st["L"].get("asked_for_booking") == 2, agreed=st["agreed"], unclear=st["unclear"] is not None, prev_said=st["prev_said"])
    return bool(eval(expr, {"__builtins__": {}}, env))


def make_ctx(slot, site, cls_hint=None, company=None, sx=None):
    sx = sx or rnd.choice("mf")
    first = rnd.choice(FN_M if sx == "m" else FN_F)
    last = rnd.choice(LN)
    info = SITE[site]
    others = [FIRST[s] for s in info["advisors"] if s != slot]
    ctx = dict(sx=sx, advisor_first=FIRST[slot], shop_address=info["shop_address"], shop_short=info["shop_short"], shop_hours="seven-thirty to five-thirty",
               closing_time="five-thirty", tech_name=rnd.choice(info["techs"]), manager_name=("Greg" if slot == "22" else info["manager"]),
               other_advisor=rnd.choice(others) if others else "somebody", sir_maam="sir" if sx == "m" else "ma'am",
               customer_first=first, customer_last=last, customer_title=("Mr. " if sx == "m" else "Ms. ") + last,
               customer_phone_said="%s, five five five, oh one %s" % (info["area"], digits_said("%02d" % PHONES.pop(rnd.randrange(len(PHONES))))),
               customer_email_said="%s dot %s at gmail dot com" % (first.lower(), last.lower()),
               warranty="twenty-four months or twenty-four thousand miles", tow_name="Mowbray",
               ready_time=rnd.choice(["by four", "around three", "by two", "after lunch", "by the end of the day"]),
               callback_time=rnd.choice(["before noon", "by two", "this afternoon", "first thing in the morning"]),
               drop_day=rnd.choice(["Monday", "Tuesday", "Wednesday", "last week"]),
               part_eta=rnd.choice(["tomorrow morning", "Thursday", "Friday", "the first of next week"]),
               lost_item=rnd.choice(["pair of sunglasses", "phone charger", "garage door opener", "work badge", "toll tag"]),
               asked_for=rnd.choice(["Junior", "Tammy", "the tire store", "Ricky", "Darlene"]),
               competitor_place=rnd.choice(["a place out by my work", "the shop down the road", "a guy my brother uses", "the tire place on the corner"]),
               delivery_window=rnd.choice(["ten o'clock", "noon", "two o'clock", "afternoon"]),
               order_ref_said=digits_said(str(rnd.randint(41000, 49999))),
               a_ok="(token)", a_yes="(token)", a_sorry="(token)",  # filled from the advisor's tokens when the line is said
               )
    vend = [v for v in VEND if site in v.get("serves", []) and "supplier" in v["role"]]
    v = rnd.choice(vend)
    ctx.update(vendor_name=v["name"].split(" Supply")[0].replace(" Distributors", "").replace(" Inc.", ""),
               vendor_rep=rnd.choice(["Mike", "Donnie", "Shawn", "Kim", "Phil"]))
    if company:
        a = company
        u = rnd.choice(a["fleet"])
        num = re.sub(r"\D", "", u["unit"])
        c0 = a["contacts"][0]["name"].split()
        ctx["company_contact"] = (c0[0], c0[-1])
        ctx.update(company_name=a["name"].replace(" & ", " and ").replace(" Co.", ""), unit="unit " + w3(int(num)) if num else u["unit"],
                   plate_tail_said=digits_said(u["plate"].split("-")[-1]), po_said=digits_said(str(rnd.randint(4000, 9999))),
                   boss_first=a["contacts"][0]["name"].split()[0])
        m = {"model": u["model"].split()[0] if u["model"].split()[0] not in ("Express",) else "Express", "make": u["make"]}
        ctx.update(car_make=u["make"], car_model=said_model(re.sub(r"\s*(Cargo Van|[0-9]{3,4}|-[0-9]{3})\b", "", u["model"]).strip()), car_year_said=w2(u["year"] // 100) + "-" + w2(u["year"] % 100) if False else "twenty-" + w2(u["year"] % 100),
                   car_year_short=w2(u["year"] % 100), cls="van")
    else:
        m, y = draw_car(cls_hint)
        ctx.update(car_make=m["make"], car_model=(m["make"] + " " if m["model"][:1].isdigit() else "") + said_model(m["model"]), car_year_said="twenty-" + w2(y % 100) if y >= 2010 else "two thousand " + w2(y % 100),
                   car_year_short=("oh-" + ONES[y % 100]) if y % 100 < 10 else w2(y % 100), cls=m["vehicle_class"])
    return ctx


def set_job(ctx, job, company=False, prefix=""):
    cls = ctx["cls"]
    cat = job["catalogue"]
    p = price(cat["price"], cls, company)
    pa = price(cat.get("price_alt"), cls, company)
    pi = price(cat.get("inspection_price"), cls, company)
    if not prefix:
        ctx.update(price=money(p), price_alt=money(pa) if pa else None, inspection_price=(money(pi) if pi else "no charge") if cat.get("inspection_price") else None,
                   price_otd=money(p * 1.0925 + min(35, 0.05 * p)), job_duration=duration(cat["price"]),
                   competitor_price=money(round(p * 0.72 / 5) * 5), job_said=rnd.choice(job["job_said"]),
                   job_explain=rnd.choice(job["explain"]), inspection_line=job.get("inspection_line"), depends=None, price_statement=None)
        ctx["price_statement"] = pick(job["price_statement"], ctx)
        ctx["depends"] = pick(job["depends"], ctx)
        fj = rnd.choice([j for j in jobs if j.get("found") and j["key"] != job["key"]])
        ctx.update(found_job_said=rnd.choice(fj["job_said"]), found_reason=fj["found"], found_price=money(price(fj["catalogue"]["price"], cls, company)),
                   part_name=rnd.choice([pp["name"] for pp in CATJ[cat["price"]]["en"]["parts"]] or ["part"]).lower().split(" (")[0].split(",")[0] if CATJ[cat["price"]]["en"]["parts"] else "part")
        bt = p * 1.0925 + min(35, 0.05 * p)
        ctx.update(bill_total=money(bt), bill_line=rnd.choice(["the shop supplies", "the disposal fee", "the tax line"]))
    else:
        ctx.update(second_job_said=rnd.choice(job["job_said"]), second_price=money(p),
                   second_need=rnd.choice([c["need"] for c in job["customer_says"] if c["kind"] == "accurate"]))


def advisor_line(slot, check_key, level, ctx, prefer=None, avoid_skip=False):
    ws = list(adv[slot]["checks"][check_key][str(level)])
    if ctx.get("customer_first") is None:
        ws = [w for w in ws if not re.search(r"\b(hon|buddy)\b", w)] or ws
    if prefer:
        pr = [w for w in ws if prefer in w]
        if pr and (ctx.get(prefer.strip("{}")) is not None or prefer == "{job_question}"):
            ws = pr
    if avoid_skip:
        ws = [w for w in ws if w != "<skip>"] or ws
    return pick(ws, ctx)


def greet(slot, level, ctx):
    t = advisor_line(slot, "greeting", level, ctx)
    if level == 2 and rnd.random() < 0.6:
        t = rnd.choice(adv[slot]["greetings"])
    tails = adv[slot].get("greeting_tails") or []
    if level == 2 and adv[slot]["tier"] != "curt" and not re.match(r"(Good|Morning|Hi|Hey|Yeah|Uh)", t) and not re.search(r"morning|afternoon", t) and rnd.random() < 0.5:
        t = rnd.choice(["Good morning, ", "Good afternoon, ", "Morning, "]) + (t[0].lower() + t[1:] if t.startswith("Thank") else t)
    if level >= 1 and t.endswith("?") and ", " in t and rnd.random() < 0.5 and tails and re.search(r"(?i)(how|what) (can|may) I|how are you|what can I do", t[t.rindex(", "):]):
        t = t[:t.rindex(", ")] + "."
    if level >= 1 and "?" not in t and t.endswith((".", "!")) and tails and not re.search(r"(?i)help|what can i do", t):
        t = t + rnd.choice(tails)
    return t


def backchannel(lines, v, adv_name, p=0.6):
    """Where the advisor speaks twice running, the caller often says "Okay" or "Uh-huh" in between (story calls do; rule R7 later loses or joins half of them)."""
    if v is None:
        return lines
    out = []
    for i, (who, t) in enumerate(lines):
        out.append((who, t))
        if who == adv_name and i + 1 < len(lines) and lines[i + 1][0] == adv_name and rnd.random() < p:
            out.append(("Caller", tidy(vpick(v["backchannel"], {}))))
    return out


def assemble(n, slot, ctype):
    site = SITE_OF[slot]
    a = adv[slot]
    sheet = styled(slot)
    st = dict(L={}, price_asked=False, doubt=False, known=False, ot_na=False, agreed=False, unclear=None, prev_said=True, name_known=False)
    lines = []
    head = {}
    v = None
    ctx = None
    pending_answers = []
    objection = None
    times = {"n": 0}

    def vw():
        c = ctx if st["name_known"] else dict(ctx, customer_first=None, customer_title=None, customer_last=None)
        return dict(c, _known=st["known"])

    def A(t, vary=True):
        if t is None or t == "<skip>":
            st["prev_said"] = False
            return
        st["last_raw"] = t
        t = re.sub(r"\{(a_ok|a_yes|a_sorry)\}", lambda m: rnd.choice(a["tokens"][m.group(1)]), t)
        if vary:
            same = bool(lines) and lines[-1][0] == FIRST[slot]
            t = lead(t, a["fillers"], 0.15 if same else 0.5)
            if st.get("adv_addr", 0) < 2 and not (same and re.search(r"\b(%s|sir|ma'am|hon)\b" % re.escape(ctx["customer_first"]), lines[-1][1])):
                t2 = address(t, [x for x in a.get("address", []) if (st["name_known"] or "{customer_" not in x) and (st["known"] or "hon" not in x)], 0.35)
                st["adv_addr"] = st.get("adv_addr", 0) + (1 if t2 != t and "{customer_" in t2 else 0)
                t = t2
        lines.append((FIRST[slot], tidy(fill(t, ctx))))
        st["prev_said"] = True

    def C(t, who="Caller", vary=False):
        if t is None:
            return
        if who == "Caller":
            t = swap_gender(t, ctx.get("sx", "f"))
            if ctx.get("company_name"):
                t = re.sub(r"\bmy (car|truck)\b", "the van", t)
        if vary and v is not None:
            t = lead(t, v["filler"], v["filler_rate"] * 0.8)
            if st["L"].get("greeting") == 2 and v is not voices["terse"] and not st.get("cust_addr"):
                t2 = address(t, [", {advisor_first}"], 0.15)
                st["cust_addr"] = t2 != t
                t = t2
        lines.append((who, tidy(fill(t, ctx))))

    def closing_line():
        lst = a["moves"]["closing_booked" if st["agreed"] and not st.get("callback") else "closing_open"]
        if lines and lines[-1][0] == FIRST[slot] and ctx["customer_first"] in lines[-1][1]:
            lst = [x for x in lst if "{customer_" not in x] or lst
        return pick(lst, vw())

    def adv_tier(b):
        lst = b["say"].get(a["tier"]) or b["say"].get("exact")
        t = pick(lst, ctx)
        return t

    if ctype == "new_enquiry":
        while True:
            st["known"] = rnd.random() < 0.35
            st["price_asked"] = rnd.random() < 0.60
            st["ot_na"] = rnd.random() < 0.15
            st["doubt"] = rnd.random() < 0.45
            L = {c: deal(sheet, c) for c in CHECKS}
            if not st["ot_na"] and rnd.random() < 0.7:
                L["asked_for_booking"] = L["offered_time"]
            fits = []
            for sk in ne:
                if sk["id"] == "NE14" and not [x for x in ACC_USE if x["home_shop"] == site]:
                    continue  # no company account of this shop is used in the sample (A5, the west account, is a story's)
                f = sk["fits"]
                if all(f[k] is None or f[k] == st[k] for k in ("price_asked", "doubt", "known", "ot_na")) and L["asked_for_booking"] in f["booking"]:
                    fits.append(sk)
            if fits:
                break
        sk = rnd.choices(fits, weights=[x.get("weight", 1.0) for x in fits])[0]
        st["name_known"] = st["known"]
        company = None
        if sk["id"] == "NE14":
            company = rnd.choice([x for x in ACC_USE if x["home_shop"] == site])
        job_pool = [j for j in jobs if (sk["job_filter"] is None or j["key"] in sk["job_filter"]) and (j["key"] != "fleet_pm" or company)]
        if company:
            job_pool = [j for j in job_pool if "van" in j["vehicle_classes"]]
        job = rnd.choices(job_pool, weights=[j["lead_share"] for j in job_pool])[0]
        if rnd.random() < 0.12 and any(op for op in sk["beats"] if op["role"] == "open"):
            ops = [u for u in unclear if "new_enquiry" in u["applies_to"] and (u["job_filter"] is None or job["key"] in u["job_filter"])
                   and (u["resolves_to"] == "need" or (sk["job_filter"] is None or u["resolves_to"] in sk["job_filter"]))]
            if not company:
                ops = [u for u in ops if u["resolves_to"] != "fleet_pm" and u["id"] != "U14"]
            else:
                ops = [u for u in ops if u["resolves_to"] in ("need", "fleet_pm")]
            if ops:
                st["unclear"] = rnd.choice(ops)
                if st["unclear"]["resolves_to"] != "need":
                    job = [j for j in jobs if j["key"] == st["unclear"]["resolves_to"]][0]
                st["unresolved"] = rnd.random() < 1 / 6
                if st["unresolved"]:
                    L["need_discovery"] = rnd.choice([0, 1])
                    L["asked_for_booking"] = rnd.choice([0, 1])
        force_sx = "m" if st["unclear"] and st["unclear"]["id"] == "U12" else None
        ctx = make_ctx(slot, site, cls_hint=("van" if company else None), company=company, sx=force_sx)
        if job["key"] not in {"fleet_pm"} and ctx["cls"] not in job["vehicle_classes"]:
            ctx = make_ctx(slot, site, cls_hint=rnd.choice(job["vehicle_classes"]), company=company, sx=force_sx)
        set_job(ctx, job, company=bool(company))
        if sk.get("second_job"):
            j2 = rnd.choice([j for j in jobs if j["key"] not in (job["key"], "fleet_pm", "pre_purchase")])
            set_job(ctx, j2, prefix="second")
        if company:
            vk = rnd.choice(["driver", "dispatcher"])
            if vk == "dispatcher":
                f, l = ctx["company_contact"]
                ctx.update(customer_first=f, customer_last=l, customer_title=("Ms. " if f in FN_F_CONTACT else "Mr. ") + l,
                           sx="f" if f in FN_F_CONTACT else "m", sir_maam="ma'am" if f in FN_F_CONTACT else "sir")
        else:
            vf = sk["voice_filter"] or ["terse", "chatty", "anxious", "price_shopper", "elderly", "angry"]
            if not st["price_asked"]:
                vf = [x for x in vf if x != "price_shopper"] or vf
            vk = rnd.choices(vf, weights=[{"terse": 20, "chatty": 18, "anxious": 14, "price_shopper": 14, "elderly": 12, "angry": 8}.get(x, 10) for x in vf])[0]
        v = voices[vk]
        if st["known"]:
            L["name_and_number"] = None
        if not st["price_asked"]:
            L["price_with_next_step"] = None
        if st["ot_na"]:
            L["offered_time"] = None
        if not st["doubt"]:
            L["objection"] = None
        L["recap"] = L["recap"] if L["asked_for_booking"] == 2 else None
        st["L"] = L
        st["agreed"] = L["asked_for_booking"] == 2
        t1, t2 = two_times()
        ctx.update(time_1=t1, time_2=t2, time_chosen=None, objection_probe=None, objection_answer=None, job_question="(question)")
        if st["doubt"]:
            typ = sk["doubt"] or rnd.choice([o["type"] for o in job["objections"]])
            if typ == "price" and (not st["price_asked"] or L["price_with_next_step"] == 0):
                typ = "think"
            cands = [o for o in job["objections"] if o["type"] == typ] or jb["generic_objections"].get(typ) or job["objections"]
            objection = rnd.choice(cands)
            st["objection_generic_time"] = objection in jb["generic_objections"]["time"]
            ctx.update(objection_probe=objection["probe"], objection_answer=objection["answer_2"])
        need_kind = "vague" if L["need_discovery"] == 0 else None
        ctx["need"] = pick([c["need"] for c in job["customer_says"] if (need_kind is None or c["kind"] == need_kind)], ctx)
        head = dict(type="new_enquiry", skeleton=sk["id"], job=job["key"], voice=vk, levels=L, unclear=st["unclear"])
        beats = list(sk["beats"])
        if rnd.random() < (0.15 if slot in ("7", "17") else 0.05):
            for i, b in enumerate(beats):
                if b["role"] == "price":
                    beats.insert(i, {"who": "A", "role": "hold"})
                    break
        groups = {}
        first_c = True
        i = 0
        while i < len(beats):
            b = beats[i]
            i += 1
            r = b["role"]
            g = b.get("group")
            if g:
                if g not in groups:
                    keep = rnd.random() < b.get("p", 1.0) and when_ok(b.get("when"), st)
                    if g == "name":
                        keep = keep and not st["known"] and (L["name_and_number"] or 0) >= 1
                    groups[g] = keep
                if not groups[g]:
                    continue
            else:
                if rnd.random() >= b.get("p", 1.0) or not when_ok(b.get("when"), st):
                    continue
            if b["who"] == "A":
                if r == "greeting": A(greet(slot, L["greeting"], vw()), vary=False)
                elif r == "recognise":
                    if st["known"]: A(pick(a["moves"]["recognise"], vw()))
                elif r == "ack":
                    if not (st["unclear"] and lines and lines[-1][0] == "Caller" and False): A(pick(a["moves"]["ack"], vw()))
                elif r == "ask_car":
                    if st["known"] or (st["unclear"] and st.get("unresolved")): continue
                    w = advisor_line(slot, "need_discovery", 1 if L["need_discovery"] >= 1 else 0, vw())
                    if L["need_discovery"] >= 1 and not st["unclear"] and rnd.random() < (0.2 if a["tier"] == "curt" else 0.5):
                        m0 = LEAD_RE.match(w)
                        if m0:
                            w = w[m0.end():]
                        w = echo(job["job_said"][0], a["tier"]) + " " + w
                        A(w, vary=False)
                    else:
                        A(w)
                elif r == "ask_more":
                    if L["need_discovery"] < 2 or st.get("unresolved") or st["unclear"]: continue
                    w = advisor_line(slot, "need_discovery", 2, vw(), prefer=("{job_question}" if not job.get("symptom", True) else None))
                    if "{job_question}" in w:
                        q = rnd.choice(job["questions"])
                        ctx["job_question"] = q["q"]
                        pending_answers[:] = q["answers"]
                    else:
                        pending_answers[:] = job["since_answers"]
                    A(w)
                elif r == "explain":
                    if a["tier"] != "curt" or rnd.random() < 0.3: A(pick(a["moves"]["explain"], vw()))
                elif r == "price":
                    if not st["price_asked"] or st.get("unresolved"): continue
                    w = advisor_line(slot, "price_with_next_step", L["price_with_next_step"], vw(), prefer=("{inspection_line}" if sk.get("price_mode") == "inspection" else None))
                    if ctx.get("time_chosen"):
                        w = re.sub(r"\s*[^.?!]*(find you a time|schedule|get you in|what I've got|what I have open|on the book|grab you a time|find a time|get you right in|book that|when we've got)[^.?!]*[.?!]$", "", w).strip() or w
                    A(w)
                elif r == "offer_time":
                    if st["ot_na"] or st.get("unresolved"): continue
                    w = advisor_line(slot, "offered_time", L["offered_time"], vw())
                    times["n"] = 2 if "{time_2}" in w else (1 if "{time_1}" in w else 0)
                    A(w)
                elif r == "probe":
                    if st["doubt"] and L["objection"] == 2: A(pick(a["moves"]["probe"], vw()))
                elif r == "objection":
                    if not st["doubt"]: continue
                    lv = L["objection"]
                    if lv in (0, 1) and (rnd.random() < 0.6 or objection["type"] in ("time", "think")):
                        A(objection["answer_%d" % lv])
                    else:
                        A(advisor_line(slot, "objection", lv, vw()))
                elif r == "booking":
                    if L["asked_for_booking"] == 2 and not ctx.get("time_chosen"):
                        ctx["time_chosen"] = ctx["time_1"]
                    if L["asked_for_booking"] == 0 and not st["known"] and (L["name_and_number"] or 0) >= 1 and any(x.get("group") == "name" for x in beats[i:]):
                        ws = [w for w in a["checks"]["asked_for_booking"]["0"] if not re.search(r"(?i)bye|thanks for calling|thank you for calling|take care", w)]
                        A(pick(ws or a["checks"]["asked_for_booking"]["0"], vw()))
                    else:
                        A(advisor_line(slot, "asked_for_booking", L["asked_for_booking"], vw()))
                elif r == "ask_name": A(pick(a["moves"]["ask_name"], vw()))
                elif r == "ask_number": A(pick(a["moves"]["ask_number"], vw()))
                elif r == "confirm_number":
                    if st["known"]: continue
                    lv = L["name_and_number"]
                    if lv == 0:
                        if L["asked_for_booking"] == 2: A(advisor_line(slot, "name_and_number", 0, vw()))
                    else:
                        A(advisor_line(slot, "name_and_number", lv, vw()))
                elif r == "duration": A(pick(a["moves"]["duration"], vw()))
                elif r == "recap":
                    if L["recap"] is not None: A(advisor_line(slot, "recap", L["recap"], vw()))
                elif r == "hold":
                    A(pick(a["moves"]["hold"], vw())); lines.append(("HOLD", "[on hold]")); A(pick(a["moves"]["back_from_hold"], vw()))
                elif r == "closing": A(closing_line())
                elif r == "say":
                    if b.get("pair") == "prev" and "pair_idx" in st:
                        lst = b["say"].get(a["tier"]) or b["say"]["exact"]
                        A(lst[st["pair_idx"] % len(lst)])
                    else:
                        A(adv_tier(b))
            else:
                if r == "open":
                    if st["unclear"]:
                        u = st["unclear"]
                        C(voice_wrap(rnd.choice(u["opening"]), v, first_c)); first_c = False
                        A(pick(a["moves"]["ask_what"], vw()))
                        C(voice_wrap(rnd.choice(u["second_answer"]), v, False))
                        lv = str(L["need_discovery"])
                        A(u["advisor_second"][lv])
                        if st.get("unresolved"):
                            C(voice_wrap(rnd.choice(u["unresolved_end"]), v, False))
                            A(advisor_line(slot, "asked_for_booking", L["asked_for_booking"], vw()))
                            C(vpick(v["thanks_bye"], ctx), vary=True)
                            A(pick(a["moves"]["closing_open"], vw()))
                            break
                        C(voice_wrap(rnd.choice(u["third_answer"][lv]), v, False))
                    else:
                        role = v["open_price"] if st["price_asked"] else v["open_booking"]
                        if not first_c:
                            role = [x for x in role if "{company_name}" not in x and "this is" not in x.lower() and "it's {customer_first}" not in x] or role
                        C(vpick(role, ctx), vary=True); first_c = False
                elif r == "give_car":
                    if L["need_discovery"] >= 1 and not st["known"] and not st.get("unresolved"): C(vpick(v["give_car"], ctx), vary=True)
                elif r == "answer":
                    if L["need_discovery"] >= 2 and pending_answers and not st.get("unresolved") and not st["unclear"]:
                        C(voice_wrap(rnd.choice(pending_answers), v, False, tail=True))
                elif r == "react_price":
                    if st["price_asked"] and not st.get("unresolved"):
                        C(vpick(v["react_price"] if L["price_with_next_step"] else v["react_no_price"], ctx), vary=True)
                elif r == "name_time_first":
                    ctx["time_chosen"] = ctx["time_1"]; C(vpick(v["name_own_time"], ctx), vary=True)
                elif r == "respond_offer":
                    bl = L["asked_for_booking"]
                    if (b.get("force") == "pick_of_two" and "{time_2}" in (st.get("last_raw") or "")) or (bl == 2 and times["n"] == 2):
                        ctx["time_chosen"] = rnd.choice([ctx["time_1"], ctx["time_2"]]); C(vpick(v["pick_of_two"], ctx), vary=True)
                    elif bl == 2 and times["n"] == 1:
                        ctx["time_chosen"] = ctx["time_1"]; C(vpick(v["accept_one"], ctx), vary=True)
                    elif bl == 2:
                        ctx["time_chosen"] = ctx["time_1"]; C(vpick(v["name_own_time"], ctx), vary=True)
                    elif bl == 1:
                        C(vpick(v["pause"], ctx), vary=True)
                    else:
                        C(vpick(v["will_call"], ctx), vary=True)
                elif r == "after_booking":
                    if L["asked_for_booking"] == 1: C(vpick(v["decline"], ctx), vary=True)
                elif r == "doubt":
                    if st["doubt"]:
                        if objection["type"] == "time" and times["n"] == 0 and objection is jb["generic_objections"]["time"][1]:
                            objection = rnd.choice([jb["generic_objections"]["time"][0], jb["generic_objections"]["time"][2]])
                            ctx.update(objection_probe=objection["probe"], objection_answer=objection["answer_2"])
                        C(voice_wrap(rnd.choice(objection["customer"]), v, False, tail=True))
                elif r == "probe_reply":
                    if st["doubt"] and L["objection"] == 2: C(rnd.choice(objection["probe_reply"]))
                elif r == "after_objection":
                    if st["doubt"]:
                        ok = L["asked_for_booking"] >= 1 and (L["objection"] == 2 or (L["objection"] == 1 and rnd.random() < 0.5))
                        C(vpick(v["after_answer_ok" if ok else "after_answer_unsure"], ctx), vary=True)
                elif r in ("give_name", "give_number", "ask_duration", "thanks_bye", "backchannel", "yes", "no", "maybe"):
                    if r == "give_name": st["name_known"] = True
                    C(vpick(v[r], ctx), vary=True)
                elif r == "say":
                    idx = rnd.randrange(len(b["say"]))
                    st["pair_idx"] = idx
                    C(voice_wrap(b["say"][idx], v, first_c)); first_c = False
        return head, backchannel(lines, v, FIRST[slot])

    # ---- existing job, supplier, wrong number, other, outbound
    if ctype == "existing_job":
        sk = rnd.choice(ej)
        company = None
    else:
        sk = rnd.choice(oth[ctype])
        company = None
    job = rnd.choices([j for j in jobs if j["key"] != "fleet_pm"], weights=[j["lead_share"] for j in jobs if j["key"] != "fleet_pm"])[0]
    ctx = make_ctx(slot, site)
    if ctx["cls"] not in job["vehicle_classes"]:
        ctx = make_ctx(slot, site, cls_hint=rnd.choice(job["vehicle_classes"]))
    set_job(ctx, job)
    old = rnd.choice(["tomorrow at eight", "Thursday at ten", "Friday at one"])
    t1, t2 = two_times()
    while old in (t1, t2):
        t1, t2 = two_times()
    ctx.update(time_1=t1, time_2=t2, old_time=old,
               time_chosen=rnd.choice(["this afternoon", "around four", "first thing in the morning", "after lunch", "around three"]))
    if sk["id"] == "OB02":
        ctx.update(sx="f", sir_maam="ma'am", customer_title="Ms. " + ctx["customer_last"], customer_first=rnd.choice(FN_F))
    ctx["need"] = rnd.choice([c["need"] for c in job["customer_says"] if c["kind"] == "accurate"])
    L = {"greeting": deal(sheet, "greeting"), "recap": deal(sheet, "recap") if sk.get("agreed") else None, "need_discovery": deal(sheet, "need_discovery")}
    st["L"] = L
    st["agreed"] = bool(sk.get("agreed"))
    st["name_known"] = ctype in ("existing_job", "outbound")
    st["callback"] = sk.get("recap_kind") == "callback"
    if sk.get("agreed_time"):
        ctx["time_chosen"] = fill(sk["agreed_time"], ctx)
    vk = rnd.choices(["terse", "chatty", "anxious", "price_shopper", "elderly", "angry"],
                     weights=[20, 18, 12, 6, 12, (30 if sk.get("kind") in ("complaint", "comeback", "bill") else 6)])[0]
    v = voices[vk]
    party_customer = sk.get("party", "customer") == "customer"
    if ctype == "existing_job" and rnd.random() < 0.12:
        ops = [u for u in unclear if "existing_job" in u["applies_to"] and (sk["kind"] in u.get("existing_fits", []) or sk["id"] in u.get("existing_fits", []))]
        st["unclear"] = rnd.choice(ops) if ops else None
        st["unresolved"] = rnd.random() < 1 / 6
    head = dict(type=sk.get("type", ctype), skeleton=sk["id"], job=job["key"], voice=(vk if party_customer else sk.get("party")), levels=L, unclear=st["unclear"])
    first_c = True
    other_who = "Caller" if party_customer else {"supplier": "Supplier", "robot": "Recording", "staff": "Staff", "machine": "Line", "caller": "Caller"}[sk.get("party")]
    for b in sk["beats"]:
        r = b["role"]
        if b["who"] == "A":
            if r == "greeting": A(greet(slot, L["greeting"], vw()), vary=False)
            elif r == "lookup": A(pick(a["moves"]["lookup"], vw()))
            elif r == "outbound_open": A(pick(a["moves"]["outbound_open"], vw()))
            elif r == "recap":
                if L["recap"] is not None:
                    if sk.get("recap_kind") == "callback":
                        A(pick(EJ_CALLBACK[str(L["recap"])], vw()))
                    else:
                        A(advisor_line(slot, "recap", L["recap"], vw()))
            elif r == "closing": A(closing_line())
            elif r == "ask_car": A(advisor_line(slot, "need_discovery", 1, vw()))
            elif r == "say":
                if b.get("pair") == "prev" and "pair_idx" in st:
                    lst = b["say"].get(a["tier"]) or b["say"]["exact"]
                    A(lst[st["pair_idx"] % len(lst)])
                else:
                    A(adv_tier(b))
        else:
            if r == "say":
                if first_c and st["unclear"]:
                    u = st["unclear"]
                    ctx["need"] = fill(rnd.choice(b["say"]), ctx)
                    C(voice_wrap(rnd.choice(u["opening"]), v, True))
                    A(pick(a["moves"]["ask_what"], vw()))
                    C(voice_wrap(rnd.choice(u["second_answer"]), v, False))
                    lv = str(L["need_discovery"] if not st.get("unresolved") else rnd.choice([0, 1]))
                    A(u["advisor_second"][lv])
                    if st.get("unresolved"):
                        C(voice_wrap(rnd.choice(u["unresolved_end"]), v, False))
                        A(pick(a["moves"]["closing_open"], vw()))
                        L["recap"] = None
                        break
                    C(voice_wrap(rnd.choice(u["third_answer"][lv]), v, False))
                    first_c = False
                    continue
                st["pair_idx"] = rnd.randrange(len(b["say"]))
                line = b["say"][st["pair_idx"]]
                if ctype == "outbound" and first_c:
                    C(line, other_who)
                else:
                    C(voice_wrap(line, v, first_c and ctype != "outbound", party_customer), other_who)
                first_c = False
            elif r == "respond_offer":
                raw = st.get("last_raw") or ""
                if "{time_2}" in raw:
                    ctx["time_chosen"] = rnd.choice([ctx["time_1"], ctx["time_2"]]); C(vpick(v["pick_of_two"], ctx), vary=True)
                elif "{time_1}" in raw:
                    ctx["time_chosen"] = ctx["time_1"]; C(vpick(v["accept_one"], ctx), vary=True)
                else:
                    ctx["time_chosen"] = ctx["time_1"]; C(vpick(v["name_own_time"], ctx), vary=True)
            elif r == "open":
                C(vpick(v["open_price"], ctx), vary=True)
            elif r == "give_car":
                C(vpick(v["give_car"], ctx), vary=True)
            elif r in v:
                C(vpick(v[r], ctx), vary=True)
    return head, backchannel(lines, v if party_customer else None, FIRST[slot])


# which advisor answers
plan = [SLOTS[i % len(SLOTS)] for i in range(N_SAMPLE)]  # even, so each advisor has six or seven scripts to compare with the stories
types = ["new_enquiry"] * 40 + ["existing_job"] * 12 + ["supplier"] * 2 + ["wrong_number"] + ["other"] * 2 + ["outbound"] * 3
rnd.shuffle(types)
rnd.shuffle(plan)
scripts = []
def merge(lines):
    """One line per turn, as the stored transcript has it: back-to-back lines of one speaker are one turn."""
    outl = []
    for who, t in lines:
        if outl and outl[-1][0] == who and who != "HOLD":
            outl[-1] = (who, outl[-1][1] + " " + t)
        else:
            outl.append((who, t))
    return outl


for i in range(N_SAMPLE):
    head, lines = assemble(i + 1, plan[i], types[i])
    lines = merge(lines)
    scripts.append((plan[i], head, lines))

# unfilled slots, duplicates
unfilled = []
counts = {}
total = 0
total_all = 0
counts_all = {}
for slot, head, lines in scripts:
    for who, t in lines:
        if re.search(r"\{[a-z_0-9]+\}", t):
            unfilled.append(t)
        n = norm(t)
        total_all += 1
        counts_all[n] = counts_all.get(n, 0) + 1
        if len(n.split()) >= MIN_WORDS_FOR_DUP:
            total += 1
            counts[n] = counts.get(n, 0) + 1
dup = sum(c - 1 for c in counts.values() if c > 1)
dup_all = sum(c - 1 for c in counts_all.values() if c > 1)
share = dup / total if total else 0
check(not unfilled, "every slot of the 60 scripts is filled%s" % ("" if not unfilled else ": " + "; ".join(unfilled[:5])))
by_type = {}
for slot, head, lines in scripts:
    by_type[head["type"]] = by_type.get(head["type"], 0) + 1
say("        scripts by type: %s" % ", ".join("%s %d" % kv for kv in sorted(by_type.items())))
say("        scripts by advisor: %s" % ", ".join("%s %d" % (s, plan.count(s)) for s in SLOTS))
nunc = sum(1 for s, h, l in scripts if h["unclear"])
say("        with an unclear opening: %d" % nunc)
lens = [len(l) for s, h, l in scripts]
say("        lines per script: min %d, median %d, max %d" % (min(lens), sorted(lens)[len(lens) // 2], max(lens)))
check(share < DUP_LIMIT, "exact duplicate lines across the %d scripts: %d of %d lines of %d words or more = %.2f %% (limit %.0f %%)" % (N_SAMPLE, dup, total, MIN_WORDS_FOR_DUP, 100 * share, 100 * DUP_LIMIT))
say("        counting every line, backchannels included: %d of %d = %.2f %% (short lines like 'Okay.' repeat in any real set of calls)" % (dup_all, total_all, 100 * dup_all / total_all))
top = sorted(((c, n) for n, c in counts.items() if c > 1), reverse=True)[:8]
if top:
    say("        most repeated: " + "; ".join("%r x%d" % (n, c) for c, n in top))
say()

# write the sample
md = ["# Assembled sample: %d clean scripts" % N_SAMPLE, "",
      "Built by `checks/check_bank_en.py` from the pieces in this folder with random seed %d. Clean speech before the recognition model of DESIGN.md section 4. "
      "Header: type, skeleton, job block, customer voice, the dealt levels (g greeting, n name and number, d need, p price, t offered time, b booking, r recap, o objection; - = not applicable), and the unclear opening if one was laid over." % RANDOM_SEED, ""]
for i, (slot, head, lines) in enumerate(scripts, 1):
    lv = head["levels"]
    lvs = " ".join("%s%s" % (SHORT[c], "-" if lv.get(c) is None else lv.get(c)) for c in CHECKS if c in lv)
    unc = ""
    if head.get("unclear"):
        unc = " · unclear %s (%s)" % (head["unclear"]["id"], head["unclear"]["kind"])
    md.append("## %d. %s (%s) · %s · %s · %s · voice %s" % (i, adv[slot]["name"], slot, head["type"], head["skeleton"], head["job"], head["voice"]))
    md.append("")
    md.append("`%s`%s" % (lvs, unc))
    md.append("")
    for who, t in lines:
        md.append("- %s: %s" % (who if who != "HOLD" else "*hold*", t))
    md.append("")
if "--seed" not in sys.argv:
    with open(OUT_MD, "w") as f:
        f.write("\n".join(md))
say("Sample written to calls/bank-en/assembled-sample.md")
say()
say("RESULT " + ("PASS" if not fails else "FAIL (%d)" % len(fails)))
if "--seed" not in sys.argv:
    with open(OUT_TXT, "w") as f:
        f.write("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if fails else 0)
