#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks the Russian call bank (calls/bank-ru/) against calls/DESIGN.md section 6, calls/bank-en/FORMAT.md and its own
FORMAT.md ("Russian additions"), and assembles a sample. Modelled on check_bank_en.py.

    python3 checks/check_bank_ru.py      # writes checks/bank_ru_check.txt and calls/bank-ru/assembled-sample.md

Checks: the count of every piece; every slot and every form of a slot used is declared in bank-ru/FORMAT.md and, where the
form comes from a closed list, present in forms.json; gender markers are well formed; no digit, weekday, month, «завтра»,
spelled clock time or money word outside a slot; no Latin-script word in any line; no advisor line of three words or more
repeated by another advisor; every advisor has 8 checks x 3 levels x 4 wordings whose slots carry what the rubric's anchor
asks for. Then 60 clean scripts are assembled with a fixed seed (slots filled from the catalogue, parc, cast, accounts,
vendors and forms.json, with the form rules applied) and checked for unfilled slots, unresolved markers and repeated lines;
the share of exact duplicate lines must be under 3 %. Exit code 1 when a check fails. Not product code.
"""
import glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
BANK = os.path.join(SEED, "calls", "bank-ru")
DRY = "BANK_SEED" in os.environ                                    # another seed is a dry run: nothing is written
OUT_TXT = os.path.join(HERE, "bank_ru_check.txt")
OUT_MD = os.path.join(BANK, "assembled-sample.md")
RANDOM_SEED = int(os.environ.get("BANK_SEED", "20261113"))   # the sample of record is built with the default
N_SAMPLE = 60
DUP_LIMIT = 0.03
MIN_WORDS_FOR_DUP = 4
MIN_WORDS_OWN = 3

CHECKS = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")
SHORT = {"greeting": "g", "name_and_number": "n", "need_discovery": "d", "price_with_next_step": "p", "offered_time": "t",
         "asked_for_booking": "b", "recap": "r", "objection": "o"}
SLOTS = ("5", "6", "7", "29", "16", "17", "22", "23", "24")
EXISTING_KINDS = ("ready", "not_ready", "part_late", "extra_work", "booking_moved", "pick_up", "bill", "complaint", "comeback", "lost_item")
VOICE_ROLES = ("opener", "filler", "tail", "open_price", "open_booking", "give_car", "react_price", "react_no_price", "yes", "no", "maybe",
               "pick_of_two", "accept_one", "name_own_time", "pause", "decline", "will_call", "accept_callback", "doubt_price", "doubt_time",
               "doubt_trust", "doubt_think", "after_answer_ok", "after_answer_unsure", "give_name", "give_number", "ask_duration", "backchannel",
               "thanks_bye")
MOVES = ("ack", "ask_what", "ask_name", "ask_number", "recognise", "lookup", "hold", "back_from_hold", "explain", "duration", "probe",
         "outbound_open", "closing_booked", "closing_open", "closing_callback", "recap_step", "next_step")
UNCLEAR_KINDS = ("vague", "wrong_thing", "two_in_one", "wrong_way_round")
SLOT_RE = re.compile(r"\{([a-z_0-9]+)(?:\.([a-z_0-9]+))?\}")
MARK_RE = re.compile(r"\{([ac]):([^|{}]*)\|([^{}]*)\}")

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
JOB = {j["key"]: j for j in jobs}
ej = load("skeletons-existing-job.json")["skeletons"]
oth = load("skeletons-other.json")
voices = load("voices.json")["voices"]
unclear = load("unclear.json")["openings"]
FORMS = load("forms.json")
adv = {}
for s in SLOTS:
    with open(os.path.join(BANK, "advisors", s + ".json")) as f:
        adv[s] = json.load(f)

# ------------------------------------------------------------------------------------------------- speech strings
SPEECH_JOB_KEYS = ("job_said", "job_said_na", "job_inf", "job_do", "since_answers", "explain", "price_statement", "depends", "inspection_line", "found")


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
            for t in strings_in(sk.get("recap")):
                yield "skeleton %s.recap" % sk["id"], t
    for u in unclear:
        for k in ("opening", "ask", "second_answer", "advisor_second", "third_answer", "unresolved_end"):
            for t in strings_in(u.get(k)):
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
    for k in ("hello", "bye"):
        for t in FORMS["west_tatar"][k]:
            yield "forms.west_tatar." + k, t


SPEECH = [(w, t) for w, t in speech() if t != "<skip>"]

# ------------------------------------------------------------------------------------------------- 1. counts
say("Russian call bank: check")
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
      "outbound reasons cover DESIGN.md section 2 (RU: approval 35, ready 30, supplier 17, callback 10, confirm 8): %s" % reasons)
want_voices = {"terse", "chatty", "anxious", "price_shopper", "elderly", "driver", "dispatcher", "angry"}
check(set(voices) == want_voices, "customer voices: %d %s" % (len(voices), sorted(voices)))
check(len(unclear) == 20, "unclear openings: %d (20)" % len(unclear))
uk = {}
for u in unclear:
    uk[u["kind"]] = uk.get(u["kind"], 0) + 1
check(set(uk) == set(UNCLEAR_KINDS) and all(uk.get(k, 0) >= 3 for k in UNCLEAR_KINDS), "unclear kinds: %s" % uk)
check(len(adv) == 9, "advisor files: %d (slots %s)" % (len(adv), ", ".join(SLOTS)))
adv_check_lines = sum(len(list(strings_in(a["checks"]))) for a in adv.values())
adv_move_lines = sum(len(list(strings_in(a["moves"]))) for a in adv.values())
check(adv_check_lines == 864, "advisor check wordings: %d (9 x 8 x 3 x 4 = 864)" % adv_check_lines)
check(adv_check_lines + adv_move_lines >= 900, "advisor phrase bank lines with greetings, closings, holds and moves: %d (about 900 or more)" % (adv_check_lines + adv_move_lines))
say("        lines of speech in the whole bank: %d" % len(SPEECH))
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
    if a.get("gender") not in ("m", "f") or a.get("price_style") not in FORMS["money"]["styles"]:
        bad.append("%s gender or price_style" % s)
    if set(a.get("name_forms", {})) != {"nom", "gen", "dat", "acc", "ins"}:
        bad.append("%s name_forms" % s)
    if not a.get("fillers") or set(a.get("tokens", {})) != {"a_ok", "a_yes", "a_sorry"}:
        bad.append("%s fillers or tokens" % s)
check(not bad, "every advisor: 8 checks x 3 levels x 4 wordings, every move, a tier, a gender, a price style, name forms, fillers and tokens%s" % ("" if not bad else ": " + "; ".join(bad[:8])))
CAST = json.load(open(os.path.join(SEED, "cast.json")))["people"]
person = {p["slot"]: p for p in CAST}
bad = []
for s, a in adv.items():
    p = person[s]
    if p["site"] != a["site"] or (p["gender"] == "male") != (a["gender"] == "m"):
        bad.append("%s site or gender against cast.json" % s)
    names = set(p["ru"]["full_name"].split())
    for w in a["checks"]["greeting"]["2"]:
        if "Ермак" not in w or not (names & set(re.findall(r"[А-ЯЁа-яё]+", w))):
            bad.append("%s greeting 2: %s" % (s, w))
    for w in a["checks"]["greeting"]["0"]:
        if "Ермак" in w or (names & set(re.findall(r"[А-ЯЁа-яё]+", w))):
            bad.append("%s greeting 0 names somebody: %s" % (s, w))
check(not bad, "greeting level 2 names the business and the advisor in every wording, level 0 names neither; site and gender agree with cast.json%s" % ("" if not bad else ": " + "; ".join(bad[:6])))


def has(w, slot):
    return any(m.group(1) == slot for m in SLOT_RE.finditer(w))


bad = []
for s, a in adv.items():
    c = a["checks"]
    name = a["name_forms"]
    own = set(name.values()) | set(person[s]["ru"]["full_name"].split())
    if not all(has(w, "customer_phone_said") for w in c["name_and_number"]["2"]): bad.append("%s name 2 says the number back" % s)
    if any(has(w, "customer_phone_said") for w in c["name_and_number"]["1"]): bad.append("%s name 1 must not repeat the number" % s)
    if any(has(w, "car_model") for w in c["need_discovery"]["1"] + c["need_discovery"]["0"]): bad.append("%s need 0 and 1 cannot know the car" % s)
    if not all(has(w, "job_question") or "авно" in w or "огда" in w or "акого времени" in w for w in c["need_discovery"]["2"]): bad.append("%s need 2 asks a circumstance" % s)
    if not all(has(w, "time_1") and has(w, "time_2") for w in c["offered_time"]["2"]): bad.append("%s time 2 has two options" % s)
    if any(has(w, "time_2") for w in c["offered_time"]["1"]): bad.append("%s time 1 has one option" % s)
    if any(has(w, "time_1") for w in c["offered_time"]["0"]): bad.append("%s time 0 offers no time" % s)
    if not all(has(w, "time_chosen") and any(n in w for n in own) or (has(w, "time_chosen") and "сам" in w) for w in c["asked_for_booking"]["2"]): bad.append("%s booking 2 names the time and who takes it" % s)
    if any(has(w, "time_chosen") for w in c["asked_for_booking"]["1"] + c["asked_for_booking"]["0"]): bad.append("%s booking 0 and 1 name no time" % s)
    if not all(has(w, "time_chosen") and has(w, "shop_address") and (has(w, "job_said") or has(w, "job_do")) for w in c["recap"]["2"]): bad.append("%s recap 2 time, address, work" % s)
    if any(has(w, "shop_address") for w in c["recap"]["1"]) or not all(has(w, "time_chosen") for w in c["recap"]["1"]): bad.append("%s recap 1 has the time and leaves the address out" % s)
    if any(SLOT_RE.search(w) and not has(w, "comma_name") and not has(w, "name_comma") for w in c["recap"]["0"]): bad.append("%s recap 0 repeats nothing" % s)
    if not all(has(w, "objection_answer") for w in c["objection"]["2"]): bad.append("%s objection 2 carries the answer" % s)
    if any(has(w, "objection_answer") for w in c["objection"]["1"] + c["objection"]["0"]): bad.append("%s objection 0 and 1 are the advisor's own words" % s)
    if not all(((has(w, "depends") and has(w, "price_statement")) or has(w, "inspection_line")) and has(w, "next_step") for w in c["price_with_next_step"]["2"]): bad.append("%s price 2 says what it depends on and moves to a step" % s)
    if any(has(w, "depends") or has(w, "inspection_line") for w in c["price_with_next_step"]["1"]) or not all(has(w, "price_statement") for w in c["price_with_next_step"]["1"]): bad.append("%s price 1 is a bare price" % s)
    if any(has(w, "price_statement") or has(w, "price") or has(w, "inspection_line") for w in c["price_with_next_step"]["0"]): bad.append("%s price 0 gives no price" % s)
    if not any(has(w, "inspection_line") for w in c["price_with_next_step"]["2"]): bad.append("%s price 2 has an inspection wording" % s)
    b1 = c["asked_for_booking"]["1"]
    if not (all("запи" in w.lower() or "постав" in w.lower() for w in b1[:2]) and all("звон" in w.lower() or "набер" in w.lower() for w in b1[2:])):
        bad.append("%s booking 1: wordings 1-2 offer a booking, 3-4 promise a call" % s)
check(not bad, "each level's wordings carry what the rubric's anchor asks for%s" % ("" if not bad else ": " + "; ".join(bad[:10])))
bad = []
for j in jobs:
    ks = [c["kind"] for c in j["customer_says"]]
    if len(ks) < 6 or "vague" not in ks or "wrong" not in ks or "accurate" not in ks: bad.append("%s customer_says" % j["key"])
    if len(j["questions"]) < 3 or any(len(q["answers"]) < 2 for q in j["questions"]): bad.append("%s questions" % j["key"])
    if not j["price_statement"] or not j["depends"] or not j["explain"] or len(j["since_answers"]) < 2: bad.append("%s price, explain or since" % j["key"])
    if len(j["objections"]) < 3: bad.append("%s objections" % j["key"])
    for o in j["objections"]:
        if not all(o.get(k) for k in ("customer", "probe", "probe_reply", "answer_2", "answer_1", "answer_0")): bad.append("%s objection %s" % (j["key"], o.get("type")))
        if o["type"] not in ("price", "trust", "time", "think"): bad.append("%s objection type" % j["key"])
        if o["probe"][0].isupper() or o["probe"].startswith("а ") or not o["probe"].endswith("?"): bad.append("%s probe is a bare lower-case question" % j["key"])
    if not isinstance(j.get("symptom"), bool): bad.append("%s symptom flag" % j["key"])
    if j.get("part") is not None and set(j["part"]) != {"nom", "acc"}: bad.append("%s part forms" % j["key"])
    for k in ("job_said", "job_said_na", "job_inf", "job_do"):
        if len(j.get(k, [])) != len(j["job_said"]) or len(j.get(k, [])) < 2: bad.append("%s %s" % (j["key"], k))
    if any(not w.startswith("на ") and not w.startswith("к ") for w in j["job_said_na"]): bad.append("%s job_said_na starts with «на» or «к»" % j["key"])
    if any(not w.startswith("это ") or re.search(r"скорее всего|похоже|наверное|вероятно", w) for w in j["explain"]): bad.append("%s explain starts with «это» and carries no hedge of its own" % j["key"])
    if any(not (w[0].isupper() and w[-1] in ".!") for w in j["depends"]): bad.append("%s depends is a sentence" % j["key"])
    if any(w[0].isupper() and not w.startswith("ТО") and not w.startswith("ШРУС") and not w.startswith("ГРМ") for w in j["price_statement"] + j["explain"] + [c["need"] for c in j["customer_says"]]): bad.append("%s clause starts lower-case" % j["key"])
    if any(w.rstrip()[-1] in ".!?" for w in j["price_statement"] + j["explain"] + [c["need"] for c in j["customer_says"]] + [q["q"] for q in j["questions"]]): bad.append("%s clause has no final stop" % j["key"])
    if j["catalogue"]["price_alt"] and not all("{price_alt}" in w for w in j["price_statement"]): bad.append("%s price_alt in the price statement" % j["key"])
    if j["inspection_line"] and not ("{inspection_price}" in j["inspection_line"] or "{price}" in j["inspection_line"]): bad.append("%s inspection_line carries a price" % j["key"])
    if j["inspection_line"] and "{inspection_price}" in j["inspection_line"] and not j["catalogue"]["inspection_price"]: bad.append("%s inspection price key" % j["key"])
for typ in ("price", "trust", "time", "think", "compare"):
    if not jb["generic_objections"].get(typ): bad.append("generic_objections.%s" % typ)
check(not bad, "every job block: 6+ wordings (accurate, vague, wrong), 3 questions, price and what it depends on, 3 objections at 3 levels, the four Russian forms of its name; generic objections of all four types%s" % ("" if not bad else ": " + "; ".join(bad[:8])))
CAT = json.load(open(os.path.join(SEED, "catalogue.json")))
CATJ = {j["key"]: j for j in CAT["jobs"]}
bad = [j["key"] for j in jobs if any(v and v not in CATJ for v in j["catalogue"].values())]
check(not bad, "every job block's catalogue keys exist in catalogue.json%s" % ("" if not bad else ": " + ", ".join(bad)))
lead = sum(CATJ[k]["ru"]["share_of_orders"]["lead"] for j in jobs for k in (j["catalogue"]["price"], j["catalogue"]["price_alt"]) if k)
say("        the 24 blocks cover catalogue jobs that are the lead job on %.1f %% of Russian orders" % (100 * lead))
bad = []
for vk, v in voices.items():
    for r in VOICE_ROLES:
        if not v.get(r) or (r not in ("opener", "filler", "tail") and not r.startswith("doubt_") and len(v[r]) < 4):
            bad.append("%s.%s" % (vk, r))
    for r in ("open_price", "open_booking"):
        if any("{need}" not in w for w in v.get(r, [])):
            bad.append("%s.%s without {need}" % (vk, r))
    if not any("{car_make}" not in w for w in v["give_car"]):
        bad.append("%s.give_car needs a wording without the make" % vk)
check(not bad, "every voice has every customer role (%d roles, four or more wordings each), and its openings carry {need}%s" % (len(VOICE_ROLES), "" if not bad else ": " + "; ".join(bad[:8])))
bad = []
for u in unclear:
    if not (len(u["opening"]) >= 2 and len(u["second_answer"]) >= 2 and len(u["unresolved_end"]) >= 2): bad.append(u["id"])
    if set(u["advisor_second"]) != {"0", "1", "2"} or set(u["third_answer"]) != {"0", "1", "2"}: bad.append(u["id"] + " levels")
    if u["resolves_to"] != "need" and u["resolves_to"] not in JOB: bad.append(u["id"] + " resolves_to")
    if u["resolves_to"] == "need" and not all("{need}" in t for lv in ("0", "1", "2") for t in u["third_answer"][lv]): bad.append(u["id"] + " third answer carries {need}")
    if len(u["applies_to"]) != 1: bad.append(u["id"] + " applies to one kind of call")
    if u.get("existing_fits") and not set(u["existing_fits"]) <= set(EXISTING_KINDS): bad.append(u["id"] + " existing_fits")
    if "?" not in u["advisor_second"]["2"] or "?" in u["advisor_second"]["0"]: bad.append(u["id"] + " second question: level 2 asks, level 0 does not")
    if len(u["opening"]) != len(u["second_answer"]): bad.append(u["id"] + " opening and second answer are paired")
    if u.get("ask") and set(u["ask"]) != {"exact", "warm", "curt"}: bad.append(u["id"] + " ask tiers")
    if re.match(r"(Здравствуйте|Алло|Добрый)", u["opening"][0]): bad.append(u["id"] + " opening carries no greeting (the voice's opener brings it)")
check(not bad, "every unclear opening has the caller's second and third answers and the advisor's second question at 0, 1, 2 (level 2 asks, level 0 does not)%s" % ("" if not bad else ": " + ", ".join(bad)))
bad = []
for sk in ne:
    roles = [b["role"] for b in sk["beats"]]
    if roles[0] != "greeting" or roles[-1] != "closing" or "booking" not in roles: bad.append(sk["id"] + " frame")
    for b in sk["beats"]:
        if b["role"] == "say":
            if b["who"] == "A" and set(b["say"]) != {"exact", "warm", "curt"}: bad.append(sk["id"] + " tiers")
            if b["who"] == "C" and not isinstance(b["say"], list): bad.append(sk["id"] + " customer say")
        if b.get("check") and b["check"] not in CHECKS: bad.append(sk["id"] + " check")
for g in [ej] + [oth[k] for k in ("supplier", "wrong_number", "other", "outbound")]:
    for sk in g:
        for b in sk["beats"]:
            if b["role"] == "say" and b["who"] == "A" and set(b["say"]) != {"exact", "warm", "curt"}: bad.append(sk["id"] + " tiers")
for sk in ej:
    has_recap = any(b["role"] == "recap" for b in sk["beats"])
    if bool(sk.get("agreed")) != has_recap or (sk.get("recap_kind") == "callback") != (sk["outcome"] == "callback_promised"):
        bad.append(sk["id"] + " agreed, recap beat, recap_kind and outcome agree")
    if sk.get("recap") and (set(sk["recap"]) != {"do", "said"} or len(sk["recap"]["do"]) != len(sk["recap"]["said"])):
        bad.append(sk["id"] + " recap forms")
check(not bad, "skeletons: every new enquiry opens with the greeting, carries the booking beat and closes; advisor lines written in a skeleton have all three tiers; an existing-job skeleton's agreement, recap beat and outcome agree%s" % ("" if not bad else ": " + ", ".join(bad[:8])))
cover = []
for pa in (True, False):
    for d in (True, False):
        for kn in (True, False):
            for ot in (True, False):
                for bl in (0, 1, 2):
                    st0 = dict(price_asked=pa, doubt=d, known=kn, ot_na=ot)
                    if not any(all(sk["fits"][k] is None or sk["fits"][k] == st0[k] for k in st0) and bl in sk["fits"]["booking"] and not sk["job_filter"] for sk in ne):
                        cover.append("%s booking %d" % (",".join(k for k in st0 if st0[k]) or "plain", bl))
say("        scenario combinations (price asked, doubt, known, time named first, booking level) no unfiltered skeleton carries: %s" % (", ".join(cover) or "none"))
say()

# ------------------------------------------------------------------------------------------------- 3. slots, forms and typed amounts
say("3. Slots, their Russian forms, and typed amounts")
fmt = open(os.path.join(BANK, "FORMAT.md")).read()
table = fmt.split("## Slots", 1)[1].split("\n## ", 1)[0]
declared = {}
for row in table.splitlines():
    if row.startswith("| `{"):
        cells = row.split("|")
        names = re.findall(r"\{([a-z_0-9]+)\}", cells[1])
        forms = set(re.findall(r"`\.([a-z_0-9]+)`", cells[2]))
        for n in names:
            declared[n] = forms
used = {}
bad_forms = []
for where, t in SPEECH:
    for m in SLOT_RE.finditer(t):
        n, f = m.group(1), m.group(2)
        used.setdefault(n, where)
        if n in declared and f and f not in declared[n]:
            bad_forms.append("{%s.%s} (%s)" % (n, f, where))
undeclared = sorted(set(used) - set(declared))
check(not undeclared, "every slot used is declared in bank-ru/FORMAT.md with its Russian form (%d used, %d declared)%s" % (len(used), len(declared), "" if not undeclared else ": " + ", ".join("%s (%s)" % (s, used[s]) for s in undeclared)))
check(not bad_forms, "every form asked of a slot is one the slot declares%s" % ("" if not bad_forms else ": " + ", ".join(sorted(set(bad_forms))[:12])))
unused = sorted(set(declared) - set(used))
say("        declared and not used in a line (filled inside another slot or by the generator): %s" % (", ".join(unused) or "none"))
bad = []
for where, t in SPEECH:
    rest = MARK_RE.sub("", SLOT_RE.sub("", t))
    if "{" in rest or "}" in rest or "|" in rest:
        bad.append("%s: %r" % (where, t))
check(not bad, "every brace is a slot `{name}`, a slot form `{name.form}` or a gender marker `{a:он|она}` / `{c:он|она}`%s" % ("" if not bad else ":\n          " + "\n          ".join(bad[:10])))
nmark = sum(len(MARK_RE.findall(t)) for w, t in SPEECH)
say("        gender markers in the bank: %d" % nmark)
# closed lists
bad = []
PARC = json.load(open(os.path.join(SEED, "parc.json")))["configurations"]["ru"]["models"]
if [(m["make"], m["model"]) for m in PARC] != [(c["make"], c["model"]) for c in FORMS["cars"]]:
    bad.append("cars do not follow parc.json")
for c in FORMS["cars"]:
    if set(c["said"]) != {"nom", "gen", "dat", "acc", "ins", "prep"} or not all(c["said"].values()):
        bad.append("car %s %s" % (c["make"], c["model"]))
for k in ("parts", "lost_items", "bill_lines", "asked_for", "asked_for_person"):
    if any(set(x) != {"nom", "acc"} for x in FORMS[k]):
        bad.append(k)
for k, v in FORMS["hours"].items():
    if set(v) != {"v", "na", "k", "nom"}:
        bad.append("hour " + k)
for k, v in FORMS["days"].items():
    if not {"v", "na", "nom", "do"} <= set(v):
        bad.append("day " + k)
for site, v in FORMS["sites"].items():
    for s in v["advisors"] + v["techs"] + [v["manager"]]:
        if set(FORMS["people"].get(s, {})) != {"nom", "gen", "dat", "acc", "ins"}:
            bad.append("person " + s)
check(not bad, "forms.json: 78 cars in parc.json's order with six cases each; hours, days, years, units, people, parts and lost items carry the forms the slots declare%s" % ("" if not bad else ": " + ", ".join(bad[:8])))

NUM = r"(час|часу|часа|два|две|двух|двум|три|трёх|трём|четыре|четырёх|четырём|пять|пяти|шесть|шести|семь|семи|восемь|восьми|девять|девяти|десять|десяти|одиннадцать|одиннадцати|двенадцать|двенадцати|полдень|полудня|полночь)"
pat_digit = re.compile(r"\d")
pat_week = re.compile(r"(?<![а-яёА-ЯЁ])(завтра|послезавтра|понедельник\w*|вторник\w*|сред[ауые]|четверг\w*|пятниц\w*|суббот\w*|воскресень\w*|январ\w+|феврал\w+|март[ае]?|апрел\w+|ма[йяе]|июн\w+|июл\w+|август\w*|сентябр\w+|октябр\w+|ноябр\w+|декабр\w+)(?![а-яё])", re.I)
pat_clock = re.compile(r"(?<![а-яёА-ЯЁ])(в|к|до|с|на|после|около)\s+" + NUM + r"(?![а-яё])(?!\s+(раз|раза|дня|дней|захода|заход|недел|месяц|колес|колёс|оси|ось|мест|сторон|вариант|машин|с лишним раза|с половиной раза))", re.I)
pat_money = re.compile(r"(рубл|руб\.|₽|(?<![а-яё])тысяч(?!\s+километров)|(?<![а-яё])тыщ)", re.I)
pat_latin = re.compile(r"[A-Za-z]")
bad = []
latin = []
for where, t in SPEECH:
    bare = MARK_RE.sub(lambda m: m.group(2) + " " + m.group(3), SLOT_RE.sub(" ", t))
    for name, p in (("digit", pat_digit), ("weekday, month or «завтра»", pat_week), ("clock time", pat_clock), ("money word", pat_money)):
        m = p.search(bare)
        if m:
            bad.append("%s: %s (%s) in %r" % (where, name, m.group(0), t))
    if pat_latin.search(bare):
        latin.append("%s: %r" % (where, t))
check(not bad, "no digit, weekday, month, «завтра», spelled clock time or money word outside a slot (%d lines read)%s" % (len(SPEECH), "" if not bad else ":\n          " + "\n          ".join(bad[:15])))
check(not latin, "no Latin-script word in any line: makes, models and brands are written as they are said, in Cyrillic%s" % ("" if not latin else ":\n          " + "\n          ".join(latin[:10])))
story_names = "Тарасов Лаптев Хайруллин Ефимов Куликов Захаров Валиев Тихонов Ганин Пчелинцев Жуков Маркелов Белоглазов Айдаров Рожков Хабибуллин Сабиров Сафин Фомичёв Гизатуллин Кравцов Фаттахов Вершинин Рябов".split()
hits = [(w, t) for w, t in SPEECH if any(re.search(r"(?<![а-яё])" + n, t) for n in story_names)]
hits += [("forms.sample_names", n) for n in FORMS["sample_names"]["surname"] + FORMS["sample_names"]["surname_kazan"] if n in story_names]
check(not hits, "no line names a customer, a company contact or the mechanic of a story call%s" % ("" if not hits else ": " + "; ".join("%s %r" % h for h in hits[:5])))
say()

# ------------------------------------------------------------------------------------------------- 4. advisors' own voices
say("4. Each advisor's lines are their own")


def norm(t):
    t = t.lower().replace("ё", "е")
    t = re.sub(r"[^a-zа-я0-9{}_.|: ]+", " ", t)
    t = re.sub(r"(?<![a-z_])\.(?![a-z_])|(?<!\{[ac]):", " ", t)
    return " ".join(t.split())


def nwords(n):
    return len(n.split())


owner = {}
dups = []
short_shared = set()
for s, a in adv.items():
    seen = set()
    for t in list(strings_in(a["checks"])) + list(strings_in(a["moves"])):
        if t == "<skip>":
            continue
        n = norm(t)
        if n in seen:
            continue
        seen.add(n)
        if not SLOT_RE.sub("", n).strip():
            continue          # a bare slot: «{objection_answer}», «{job_duration}.»
        if n in owner and owner[n] != s:
            if nwords(n) >= MIN_WORDS_OWN:
                dups.append("%r: slots %s and %s" % (t, owner[n], s))
            else:
                short_shared.add(n)
        owner.setdefault(n, s)
check(not dups, "no line of three words or more of one advisor is repeated by another, ignoring case and punctuation (%d distinct lines)%s" % (len(owner), "" if not dups else ":\n          " + "\n          ".join(dups[:20])))
say("        one- and two-word lines that two advisors share (the language's own small change: «%s»): %d" % ("», «".join(sorted(short_shared)[:6]), len(short_shared)))
say()

# ------------------------------------------------------------------------------------------------- 5. sample assembly
say("5. Sample assembly: %d clean scripts, random seed %d" % (N_SAMPLE, RANDOM_SEED))
rnd = random.Random(RANDOM_SEED)
ACC = json.load(open(os.path.join(SEED, "accounts.json")))["ru"]["accounts"]
VEND = json.load(open(os.path.join(SEED, "vendors.json")))["ru"]
SITE = FORMS["sites"]
SITE_OF = {s: adv[s]["site"] for s in SLOTS}

ONES = ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять", "десять", "одиннадцать", "двенадцать", "тринадцать",
        "четырнадцать", "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят", "девяносто"]
HUND = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот"]
ORD_F = {1: "первая", 2: "вторая", 3: "третья", 4: "четвёртая", 5: "пятая", 6: "шестая", 7: "седьмая", 8: "восьмая", 9: "девятая", 10: "десятая",
         11: "одиннадцатая", 12: "двенадцатая", 13: "тринадцатая", 14: "четырнадцатая", 15: "пятнадцатая", 16: "шестнадцатая", 17: "семнадцатая",
         18: "восемнадцатая", 19: "девятнадцатая", 20: "двадцатая", 30: "тридцатая", 40: "сороковая", 50: "пятидесятая", 60: "шестидесятая",
         70: "семидесятая", 80: "восьмидесятая", 90: "девяностая", 100: "сотая", 200: "двухсотая", 300: "трёхсотая", 400: "четырёхсотая",
         500: "пятисотая", 600: "шестисотая", 700: "семисотая", 800: "восьмисотая", 900: "девятисотая"}


def w3(n, fem=False):
    """0..999 in words; fem for a count of thousands (одна, две)."""
    parts = []
    h, r = divmod(n, 100)
    if h:
        parts.append(HUND[h])
    if r >= 20:
        parts.append(TENS[r // 10])
        r = r % 10
    if r or not parts:
        w = ONES[r]
        if fem and r == 1:
            w = "одна"
        if fem and r == 2:
            w = "две"
        parts.append(w)
    return " ".join(parts)


def thousand_word(th):
    if th % 100 in (11, 12, 13, 14):
        return "тысяч"
    return {1: "тысяча", 2: "тысячи", 3: "тысячи", 4: "тысячи"}.get(th % 10, "тысяч")


def money_one(x, style, acc=False):
    """A sum said aloud; forms.json 'money' states the rule."""
    if style == "round":
        if x < 2000:
            x = int(round(x / 100.0) * 100)
            style = "short"
        else:
            half = int(round(x / 500.0))
            th, odd = divmod(half, 2)
            t = (w3(th, True) + " с половиной") if odd else (w3(th, True) + " " + thousand_word(th))
            return acc_form(t) if acc else t
    x = int(round(x / 10.0) * 10)
    th, r = divmod(x, 1000)
    if th == 0:
        t = w3(r)
    elif r == 0:
        t = ("тысяча" if th == 1 else w3(th, True) + " " + thousand_word(th))
    elif style == "short" and r >= 100:
        t = ("тысяча" if th == 1 else w3(th, True)) + " " + w3(r)
    else:
        t = ("тысяча" if th == 1 else w3(th, True) + " " + thousand_word(th)) + " " + w3(r)
    if acc:
        t = acc_form(t)
    if style == "full_rub":
        t += " рублей"
    return t


def acc_form(t):
    return re.sub(r"(?<![а-яё])тысяча(?![а-яё])", "тысячу", re.sub(r"(?<![а-яё])одна(?![а-яё])", "одну", t))


def money(x, style):
    return {"": money_one(x, style), "acc": money_one(x, style, True)}


def pairs_said(s):
    out_ = []
    for i in range(0, len(s), 2):
        p = s[i:i + 2]
        out_.append(("ноль " + ONES[int(p)]) if p[0] == "0" and len(p) == 2 else w3(int(p)))
    return " ".join(out_)


def phone_said():
    a, b, c = rnd.randint(200, 989), rnd.randint(10, 99), rnd.randint(10, 99)
    return "девятьсот семь, %s, %s, %s" % (w3(a), w3(b), w3(c))


def ord_fem(n):
    h, r = divmod(n, 100)
    if r == 0:
        return ORD_F[h * 100]
    head = [HUND[h]] if h else []
    if r in ORD_F:
        return " ".join(head + [ORD_F[r]])
    return " ".join(head + [TENS[r // 10], ORD_F[r % 10]])


def acc_fem(o):
    head, _, w = o.rpartition(" ")
    w = "третью" if w == "третья" else w[:-2] + "ую"
    return (head + " " if head else "") + w


HOUR_NOW = {"main": 1, "east": 1, "west": 0}
PARTS_CLASS = CAT["configurations"]["ru"]["parts_class_multiplier"]


def r10(x):
    return int(round(x / 10.0) * 10)


def price(key, cls, company=False):
    if not key:
        return None
    e = CATJ[key]["ru"]
    f = (e.get("hours_by_class") or {}).get(cls) or 1.0
    if e["labour_pricing"] == "menu":
        lab = (e["labour_price_company"] if company else e["labour_price"])["after_rise"] * f
    else:
        lab = e["hours"] * f * (1700 if company else 1900)
    parts = 0.0
    pm = PARTS_CLASS[cls] if e.get("parts_scale_with_class") else 1.0
    for p in e["parts"]:
        opts = {o["tier"]: o for o in p["options"] if not o.get("story")}
        o = opts.get("standard") or list(opts.values())[0]
        lp = o["list_price"] * pm * (0.9 if company else 1.0)
        if lp >= 10:
            lp = r10(lp)          # a part's list price is a round sum; a fluid sold by the gram is not
        parts += lp * p["qty"]
    parts += sum(fee.get("price", 0) for fee in e.get("fees") or [])
    return r10(lab + parts)


def duration(key):
    h = CATJ[key]["ru"]["hours"] if key else 1.0
    for lim, text in FORMS["durations"]:
        if h <= lim:
            return text
    return FORMS["durations"][-1][1]


def chosen_of_two(ctx, rnd):
    """Of two offered times the caller takes one; when both fall on one day `.day` names the hour: «в семь лучше», not «завтра лучше»."""
    t = dict(rnd.choice([ctx["time_1"], ctx["time_2"]]))
    if ctx["time_1"]["_"][0] == ctx["time_2"]["_"][0]:
        t["day"] = FORMS["hours"][t["_"][1]]["v"]
    return t


WD = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def day_key(offset, wd):
    if offset == 0:
        return "today"
    if offset == 1:
        return "next"
    return WD[(wd + offset) % 7]


def time_val(offset, hhmm, wd):
    d, h = FORMS["days"][day_key(offset, wd)], FORMS["hours"][hhmm]
    return {"": d["v"] + " " + h["v"], "v": d["v"] + " " + h["v"], "na": d["na"] + " " + h["na"], "nom": d["nom"] + ", " + h["nom"],
            "k": d["v"] + " " + h["k"], "day": d["v"], "do": d["do"], "_": (offset, hhmm)}


def two_times(wd, hour_now):
    slots = [k for k in FORMS["hours"] if k.endswith(":00")] * 4 + [k for k in FORMS["hours"] if k.endswith(":30")]
    opts = []
    for off in (0, 1, 1, 2, 3, 4):
        for _ in range(3):
            hh = rnd.choice(slots)
            if off == 0 and int(hh[:2]) < hour_now + 2:
                continue
            opts.append((off, hh))
    a = rnd.choice(opts)
    far = [o for o in opts if o[0] != a[0] or abs(int(o[1][:2]) - int(a[1][:2])) >= 3]     # two offers are two days or two parts of a day
    b = rnd.choice(far or [o for o in opts if o != a])
    a, b = sorted([a, b])
    return time_val(a[0], a[1], wd), time_val(b[0], b[1], wd)


NAMES = FORMS["sample_names"]
MODELS = list(zip(PARC, FORMS["cars"]))
ACC_AT = {"main": [a for a in ACC if a["id"] in ("A1", "A3", "A6")], "east": [a for a in ACC if a["id"] in ("A2", "A4")], "west": []}


def draw_car(cls=None, belt=False):
    pool = [(m, c) for m, c in MODELS if (cls is None or m["vehicle_class"] in cls) and (not belt or any(e["timing"] == "belt" for e in m["engines"]))]
    m, c = rnd.choices(pool, weights=[x[0]["share"] for x in pool])[0]
    y = rnd.randint(max(m["year_from"], 2003), min(m["year_to"] or 2025, 2025))
    return m, c, y


def styled(slot):
    st = adv[slot]["style_sheet"]
    if "first" in st:
        lam = rnd.random()
        return {c: [(1 - lam) * st["first"][c][i] + lam * st["last"][c][i] for i in range(3)] for c in CHECKS}
    return st


def deal(sheet, c):
    return rnd.choices([0, 1, 2], weights=sheet[c])[0]


def available(ctx, name, form):
    v = ctx.get(name)
    if v is None:
        return False
    if isinstance(v, dict):
        return (form or "") in v
    return not form


BAGS = {}


def pick(lst, ctx=None, key=None):
    """Deals a wording from a shuffled bag: no wording of a list is said again before the others have been.
    Only wordings whose slots the call can fill are dealt."""
    if not lst:
        return None
    key = key if key is not None else tuple(lst)      # the same list written into several skeletons is one bag
    ok = [x for x in lst if x]
    if ctx is not None:
        ok = [x for x in ok if all(available(ctx, m.group(1), m.group(2)) for m in SLOT_RE.finditer(x))] or ok
    if not ok:
        return None
    bag = BAGS.setdefault(key, [])
    cand = [x for x in bag if x in ok]
    if not cand:
        cand = ok[:]
        rnd.shuffle(cand)
        bag[:] = [x for x in bag if x not in ok] + cand
    bag.remove(cand[0])
    return cand[0]


def fill(t, ctx):
    def one(m):
        v = ctx.get(m.group(1))
        if v is None:
            return m.group(0)
        if isinstance(v, dict):
            return str(v.get(m.group(2) or "", m.group(0)))
        return m.group(0) if m.group(2) else str(v)
    for _ in range(4):
        n = SLOT_RE.sub(one, t)
        if n == t:
            break
        t = n
    return t


def genders(t, a_sex, c_sex):
    return MARK_RE.sub(lambda m: (m.group(2) if (a_sex if m.group(1) == "a" else c_sex) == "m" else m.group(3)), t)


def tidy(t):
    t = re.sub(r"\s+", " ", t.strip())
    t = re.sub(r"\s+([,.?!…:;])", r"\1", t)
    t = re.sub(r",\s*,", ",", t)
    t = re.sub(r"^[,—\s]+", "", t)
    t = re.sub(r"([?!…])\.(?!\.)", r"\1", t)
    t = re.sub(r"(?<!\.)\.\.(?!\.)", ".", t)
    t = re.sub(r"([.?!]) ([,.])", r"\1", t)
    if t and t[0].isalpha():
        t = t[0].upper() + t[1:]
    t = re.sub(r"(?<!\.\.)([.?!]\s+)([а-яё])", lambda m: m.group(1) + m.group(2).upper(), t)
    if t and t[-1] not in ".?!…—»" and not t.endswith("..."):
        t += "."
    return t


def lower_first(t):
    return t if (not t or t[0] == "{" or t[:5] in ("Ермак",)) else t[0].lower() + t[1:]


def make_ctx(slot, site, hour_now, wd, voice=None, cls=None, belt=False, company=None):
    a = adv[slot]
    info = SITE[site]
    kazan = site == "west" and rnd.random() < 0.6
    sx = (voice or {}).get("caller_sex") or rnd.choice("mf")
    first = rnd.choice(NAMES[("male" if sx == "m" else "female") + ("_kazan" if kazan else "")])
    last = rnd.choice(NAMES["surname_kazan" if kazan else "surname"]) + ("" if sx == "m" else "а")
    patr = rnd.choice(NAMES[("patronymic_male" if sx == "m" else "patronymic_female") + ("_kazan" if kazan else "")])
    style = a["price_style"]
    greet = FORMS["greet"]["morning" if hour_now < 12 else ("day" if hour_now < 17 else "evening")]
    others = [s for s in info["advisors"] if s != slot]
    elsewhere = [s for k, v in SITE.items() if k != site for s in v["advisors"] if s != "22"]
    man = info["manager"] if info["manager"] != slot else "4"
    eta_day = FORMS["days"][day_key(rnd.choice([1, 2, 3]), wd)]["v"]
    past = FORMS["days"][WD[(wd - rnd.choice([2, 3, 4])) % 7]]["past"]
    part = rnd.choice(FORMS["parts"])
    lost = rnd.choice(FORMS["lost_items"])
    bl = rnd.choice(FORMS["bill_lines"][:3])
    af, afp = rnd.choice(FORMS["asked_for"]), rnd.choice(FORMS["asked_for_person"])
    ctx = dict(
        _style=style, _a=a["gender"], _c=sx, _site=site, _wd=wd, _hour=hour_now,
        advisor_first=dict(a["name_forms"], **{"": a["name_forms"]["nom"]}),
        shop_address=info["shop_address"], shop_short={"": info["shop_short"]["nom"], "na": info["shop_short"]["na"]},
        shop_hours=FORMS["shop_hours"], closing_time=FORMS["closing_time"], warranty=FORMS["warranty"], greet=greet,
        tech_name=dict(FORMS["people"][rnd.choice(info["techs"])]), manager_name=dict(FORMS["people"][man]),
        other_advisor=dict(FORMS["people"][rnd.choice(elsewhere)]),
        customer_first=first, customer_last=last,
        customer_title=(first + " " + patr) if (voice or {}).get("about", "").startswith(("Пожилой", "Диспетчер")) else first,
        customer_phone_said=phone_said(), name_comma="", comma_name="", car_comma="",
        ready_time=rnd.choice(FORMS["ready_time"]), callback_time=rnd.choice(FORMS["callback_time"]),
        drop_day=rnd.choice(FORMS["drop_day"]).replace("<weekday.past>", past),
        part_eta=rnd.choice(FORMS["part_eta"]).replace("<day.v>", eta_day),
        part_name={"": part["nom"], "acc": part["acc"]}, lost_item={"": lost["nom"], "acc": lost["acc"]},
        bill_line={"": bl["nom"], "acc": bl["acc"]}, asked_for={"": af["nom"], "acc": af["acc"]}, asked_for_person={"": afp["nom"], "acc": afp["acc"]},
        competitor_place=rnd.choice(FORMS["competitor_place"]), delivery_window=rnd.choice(FORMS["delivery_window"]),
        order_ref_said=pairs_said(str(rnd.randint(1100, 9899))), vendor_rep=rnd.choice(FORMS["vendor_rep"]),
        objection_probe=None, objection_answer=None, time_chosen=None, job_question=None, advisor_heard=None,
    )
    for k in ("tech_name", "manager_name", "other_advisor"):
        ctx[k][""] = ctx[k]["nom"]
    vend = [v for v in VEND if site in v.get("serves", []) and v["id"] in ("V1", "V2", "V3", "V4", "V5")]
    ctx["vendor_name"] = rnd.choice(vend)["name"]
    if company:
        u = rnd.choice(company["fleet"])
        num = int(re.sub(r"\D", "", u["unit"]) or 1)
        fm = next(m for m in FORMS["fleet_models"] if m["match"] in u["model"])
        tail = int(re.sub(r"\D", "", u["plate"])[:3])
        of = ord_fem(tail)
        ctx.update(company_name=company["name"].replace("Автошкола «Первая передача»", "автошкола «Первая передача»"),
                   unit={"": FORMS["units"][str(num)]["nom"], "acc": FORMS["units"][str(num)]["acc"]},
                   plate_tail_said={"": of, "acc": acc_fem(of)}, car_make=None,
                   car_model=dict(fm["said"], **{"": fm["said"]["nom"]}),
                   car_year_short={"": FORMS["years"][str(u["year"])]["short"]["nom"], "gen": FORMS["years"][str(u["year"])]["short"]["gen"]},
                   car_year_said={"": FORMS["years"][str(u["year"])]["said"]["nom"], "gen": FORMS["years"][str(u["year"])]["said"]["gen"]}, cls="van")
    else:
        m, c, y = draw_car(cls, belt)
        ctx.update(car_make=c["make_said"] or None, car_model=dict(c["said"], **{"": c["said"]["nom"]}),
                   car_year_short={"": FORMS["years"][str(y)]["short"]["nom"], "gen": FORMS["years"][str(y)]["short"]["gen"]},
                   car_year_said={"": FORMS["years"][str(y)]["said"]["nom"], "gen": FORMS["years"][str(y)]["said"]["gen"]}, cls=m["vehicle_class"])
    return ctx


def set_job(ctx, job, company=False, second=False):
    cls = ctx["cls"] if ctx["cls"] in job["vehicle_classes"] else job["vehicle_classes"][0]
    cat = job["catalogue"]
    st = ctx["_style"]
    p = price(cat["price"], cls, company)
    pa = price(cat.get("price_alt"), cls, company)
    pi = price(cat.get("inspection_price"), cls, company)
    i = rnd.randrange(len(job["job_said"]))
    if second:
        ctx.update(second_job_said=job["job_said"][i], second_job_inf=job["job_inf"][i], second_price=money(p, st),
                   second_need=rnd.choice([c["need"] for c in job["customer_says"] if c["kind"] == "accurate"]))
        return
    ctx.update(price=money(p, st), price_alt=money(pa, st) if pa else None, inspection_price=money(pi, st) if pi else None,
               job_duration=duration(cat["price"]), competitor_price=money(int(round(p * 0.7 / 500.0)) * 500 or 500, "short"),
               job_said={"": job["job_said"][i], "na": job["job_said_na"][i]}, job_inf=job["job_inf"][i], job_do=job["job_do"][i],
               job_explain=rnd.choice(job["explain"]), inspection_line=job.get("inspection_line"), depends=None, price_statement=None)
    ctx["price_statement"] = pick(job["price_statement"], ctx)
    ctx["depends"] = pick(job["depends"], ctx)
    fj = rnd.choice([j for j in jobs if j.get("found") and j["key"] != job["key"] and cls in j["vehicle_classes"]
                     and price(j["catalogue"]["price_alt"] or j["catalogue"]["price"], cls, company) <= 15000])
    k = rnd.randrange(len(fj["job_said"]))
    fp = price(fj["catalogue"]["price_alt"] or fj["catalogue"]["price"], cls, company)
    ctx.update(found_job_said=fj["job_said"][k], found_job_inf=fj["job_inf"][k], found_reason=fj["found"], found_price=money(fp, st),
               bill_total=money(r10(p * 1.05), st), _found_total=money(r10((p + fp) * 1.05), st))


KIND_ORDER = ["vague", "wrong_thing", "two_in_one", "wrong_way_round"]
SAID_GREETINGS = {}


def greeting_line(slot, level, ctx):
    """The greeting is dealt by its rendered text: the hour changes «доброе утро» to «добрый день», and a person
    does not repeat one greeting while another of theirs is unused."""
    ws = adv[slot]["checks"]["greeting"][str(level)]
    used = SAID_GREETINGS.setdefault(slot, set())
    cand = [w for w in ws if tidy(fill(w, ctx)) not in used]
    if not cand:
        used -= {tidy(fill(w, ctx)) for w in ws}
        cand = list(ws)
    w = rnd.choice(cand)
    used.add(tidy(fill(w, ctx)))
    return w


def advisor_line(slot, check_key, level, ctx, prefer=None, avoid_skip=False):
    ws = list(adv[slot]["checks"][check_key][str(level)])
    if prefer:
        pr = [w for w in ws if prefer in w]
        if pr and (ctx.get(prefer.strip("{}")) is not None or prefer == "{job_question}"):
            ws = pr
    elif check_key == "price_with_next_step":
        ws = [w for w in ws if "{inspection_line}" not in w] or ws
    if avoid_skip:
        ws = [w for w in ws if w != "<skip>"] or ws
    return pick(ws, ctx, key=(slot, check_key, str(level)))


NO_ADV_FILLER = {"да", "нет", "ну", "так", "смотрите", "значит", "поняла", "понял", "да-да", "ага", "хорошо", "итак", "ой", "э-э", "секундочку",
                 "скорее", "похоже", "по", "тут", "вероятнее", "предварительно", "тогда", "сейчас", "одну", "подскажу", "конечно"}
NO_FILLER = {"да", "нет", "не", "ну", "ой", "а", "ага", "угу", "хорошо", "ладно", "так", "и", "хм", "ох", "нет-нет", "да-да", "алло"}
WHO = {"supplier": "Поставщик", "robot": "Автоинформатор", "staff": "Сотрудник", "machine": "Линия", "caller": "Звонящий", "customer": "Клиент"}
GREET_RE = re.compile(r"(?i)^((Алло|Ой|Да)[,!.]? )?(Здравствуйте|Здрасьте|Добрый день|Добрый|Доброго здоровья)(, [^.!?]*)?[.!]\s*")


def assemble(n, slot, ctype, force_unclear=None):
    site = SITE_OF[slot]
    a = adv[slot]
    first_name = a["name_forms"]["nom"]
    sheet = styled(slot)
    wd = rnd.randrange(7)
    hour_now = rnd.choice([9, 9, 10, 10, 11, 11, 12, 13, 14, 15, 16, 17, 18, 19])
    st = dict(L={}, price_asked=False, doubt=False, known=False, ot_na=False, agreed=False, unclear=None, prev_said=True, name_known=False,
              car_known=False, callback=False, recap_raw=None, tatar=False)
    lines = []
    ctx = None
    v = None
    pending_answers = []
    objection = None
    times = {"n": 0}

    def refresh():
        ctx["advisor_heard"] = first_name if st.get("heard") else None
        nm = ctx["customer_title"]
        ctx["name_comma"] = (nm + ", ") if st["name_known"] else ""
        ctx["comma_name"] = (", " + nm) if st["name_known"] else ""
        ctx["car_comma"] = (ctx["car_model"][""] + ", ") if st["car_known"] else ""

    def A(t, who=None):
        if t is None or t == "<skip>":
            st["prev_said"] = False
            return
        refresh()
        if st["tatar"] == "hello" and a["moves"].get("tatar"):
            t = rnd.choice(a["moves"]["tatar"]["hello"]) + " " + t
            st["tatar"] = True
        t = re.sub(r"\{(a_ok|a_yes|a_sorry)\}", lambda m: pick(a["tokens"][m.group(1)]), t)
        if lines and lines[-1][0] == (who or first_name) and len(lines[-1][1].split()) <= 2 and lines[-1][1].split()[0].strip(".,!?…:").lower() == t.split()[0].strip(".,!?…:").lower():
            lines.pop()                                  # a bare «Да-да.» before a line that opens with the same word
        lines.append((who or first_name, tidy(genders(fill(t, ctx), ctx["_a"], ctx["_c"]))))
        st["prev_said"] = True

    def AG(t):
        """A generic line of the advisor (a question, an offer) may take one of the person's own fillers: «Так, а машина какая у вас?»"""
        if t and t != "<skip>" and len(t.split()) > 3 and rnd.random() < 0.3 and t[0] != "{" and t.split()[0].strip(".,!?…:").lower() not in NO_ADV_FILLER:
            f = pick(a["fillers"])
            said = lines[-1][1].lower() if lines and lines[-1][0] != "Клиент" else ""
            if f.split()[0].strip(".,!?…:").lower() not in re.findall(r"[а-яё-]+", said):    # not «Понял, принял. Понял.»
                t = f + " " + (lower_first(t) if f[-1] == "," else t)
        A(t)

    def C(t, who="Клиент"):
        if t is None:
            return
        refresh()
        lines.append((who, tidy(genders(fill(t, ctx), ctx["_a"], ctx["_c"]))))

    def adv_tier(b, idx=None):
        lst = b["say"].get(a["tier"]) or b["say"].get("exact")
        if idx is not None:
            t = lst[idx % len(lst)]
        else:
            t = pick(lst, ctx)
        if t and "{advisor_first" in t:
            st["heard"] = True
        return t

    def voice_wrap(line, first, party_customer=True):
        if not party_customer or v is None:
            return line
        if first and v["opener"] and rnd.random() < 0.6:
            line = pick(v["opener"]) + " " + line
        elif rnd.random() < v["filler_rate"] and line[0] != "{" and line.split()[0].strip(".,!?…").lower() not in NO_FILLER:
            f = pick(v["filler"])
            line = f + " " + (lower_first(line) if f[-1] not in ".!?…" and not f.endswith("...") else line)
        if rnd.random() < v["tail_rate"] and line.rstrip()[-1] != "?":
            line = line.rstrip() + ("" if line.rstrip()[-1] in ".!?…" else ".") + " " + pick(v["tail"])
        return line

    def when_ok(cond):
        if not cond:
            return True
        expr = re.sub(r"\bL\.([a-z_]+)", r"LV('\1')", cond)
        env = dict(LV=lambda k: (st["L"].get(k) if st["L"].get(k) is not None else -1), price_asked=st["price_asked"], doubt=st["doubt"], known=st["known"],
                   ot_na=st["ot_na"], booked=st["L"].get("asked_for_booking") == 2, agreed=st["agreed"], unclear=st["unclear"] is not None,
                   prev_said=st["prev_said"])
        return bool(eval(expr, {"__builtins__": {}}, env))

    def tatar_open(line):
        if st["tatar"] == "start":
            hello = rnd.choice(FORMS["west_tatar"]["hello"])
            line2 = GREET_RE.sub("", line, count=1)
            st["tatar"] = "hello"
            return hello + " " + line2
        return line

    if ctype == "new_enquiry":
        for _ in range(500):
            st["known"] = rnd.random() < 0.35
            st["price_asked"] = rnd.random() < 0.60
            st["ot_na"] = rnd.random() < 0.15
            st["doubt"] = rnd.random() < 0.45
            L = {c: deal(sheet, c) for c in CHECKS}
            if not st["ot_na"] and rnd.random() < 0.7:
                L["asked_for_booking"] = L["offered_time"]
            if force_unclear == "unresolved":
                L["need_discovery"], L["asked_for_booking"] = rnd.choice([0, 1]), rnd.choice([0, 1])
            fits = []
            for sk in ne:
                f = sk["fits"]
                if all(f[k] is None or f[k] == st[k] for k in ("price_asked", "doubt", "known", "ot_na")) and L["asked_for_booking"] in f["booking"]:
                    if sk.get("vehicle_class") == "van" and not ACC_AT[site]:
                        continue
                    if force_unclear and (not any(b["role"] == "open" for b in sk["beats"]) or sk.get("vehicle_class") == "van"):
                        continue
                    fits.append(sk)
            if fits:
                break
        w = [sk.get("weight", 1.0) for sk in fits]
        sk = rnd.choices(fits, weights=w)[0]
        company = rnd.choice(ACC_AT[site]) if sk.get("vehicle_class") == "van" else None
        job_pool = [j for j in jobs if (sk["job_filter"] is None or j["key"] in sk["job_filter"]) and (j["key"] != "fleet_pm" or company)
                    and (sk["job_filter"] is not None or j["key"] != "seasonal_tyres")]
        job = rnd.choices(job_pool, weights=[j["lead_share"] * (4 if j["key"] == "fleet_pm" else 1) for j in job_pool])[0]
        if force_unclear:
            ops = [u for u in unclear if "new_enquiry" in u["applies_to"] and (u["resolves_to"] == "need" or (sk["job_filter"] is None or u["resolves_to"] in sk["job_filter"]))]
            ops = [u for u in ops if not company or u["resolves_to"] == "need"]
            kind = next((k for k in KIND_ORDER if any(u["kind"] == k for u in ops)), None)      # the sample shows each kind in turn
            if kind:
                KIND_ORDER.remove(kind); KIND_ORDER.append(kind)
                ops = [u for u in ops if u["kind"] == kind]
            st["unclear"] = rnd.choice(ops)
            if st["unclear"]["resolves_to"] != "need":
                job = JOB[st["unclear"]["resolves_to"]]
            st["unresolved"] = force_unclear == "unresolved"
        if company:
            vk = rnd.choice(["driver", "dispatcher"])
        else:
            vf = sk["voice_filter"] or ["terse", "chatty", "anxious", "price_shopper", "elderly", "angry"]
            vk = rnd.choices(vf, weights=[{"terse": 20, "chatty": 18, "anxious": 14, "price_shopper": 14, "elderly": 12, "angry": 8}.get(x, 10) for x in vf])[0]
        v = voices[vk]
        ctx = make_ctx(slot, site, hour_now, wd, voice=v, cls=job["vehicle_classes"], belt=(job["key"] == "timing_belt"), company=company)
        set_job(ctx, job, company=bool(company and company["id"] in ("A1", "A2")))
        if sk.get("second_job"):
            j2 = rnd.choice([j for j in jobs if j["key"] not in (job["key"], "fleet_pm", "pre_purchase", "seasonal_tyres", "timing_belt") and ctx["cls"] in j["vehicle_classes"]])
            set_job(ctx, j2, second=True)
        if st["known"]:
            L["name_and_number"] = None
        if not st["price_asked"]:
            L["price_with_next_step"] = None
        if st["ot_na"]:
            L["offered_time"] = None
        if not st["doubt"]:
            L["objection"] = None
        st["recap_raw"] = L["recap"]
        L["recap"] = L["recap"] if L["asked_for_booking"] == 2 else None
        st["L"] = L
        st["agreed"] = L["asked_for_booking"] == 2
        st["tatar"] = "start" if (site == "west" and not company and rnd.random() < FORMS["west_tatar"]["p"]) else False
        t1, t2 = two_times(wd, hour_now)
        ctx.update(time_1=t1, time_2=t2)
        if st["doubt"]:
            typ = sk["doubt"] or rnd.choice([o["type"] for o in job["objections"]])
            if typ in ("price", "compare") and (not st["price_asked"] or L["price_with_next_step"] == 0):
                typ = "think"            # a price doubt needs a price said
            cands = [o for o in job["objections"] if o["type"] == typ] or jb["generic_objections"].get(typ) or job["objections"]
            objection = dict(rnd.choice(cands))
            ctx.update(objection_probe=objection["probe"], objection_answer=objection["answer_2"])
        need_kind = "vague" if L["need_discovery"] == 0 else rnd.choices(["accurate", "vague", "wrong"], weights=[55, 30, 15])[0]
        ctx["need"] = pick([c["need"] for c in job["customer_says"] if c["kind"] == need_kind], ctx)
        head = dict(type="new_enquiry", skeleton=sk["id"], job=job["key"], voice=vk, levels=L, unclear=st["unclear"], unresolved=st.get("unresolved"))
        beats = list(sk["beats"])
        if need_kind == "wrong" and not any(b["role"] == "explain" for b in beats):
            # the caller asked for the wrong thing: the advisor says what it is before the price or the time names the real work
            at = next((i for i, b in enumerate(beats) if b["role"] == ("price" if st["price_asked"] else "offer_time")), None)
            if at is not None:
                beats.insert(at, {"who": "A", "role": "explain"})
        if st["price_asked"] and rnd.random() < (0.15 if slot in ("7", "17") else 0.05):
            for i, b in enumerate(beats):
                if b["role"] == "price":
                    beats.insert(i, {"who": "A", "role": "hold"})
                    break
        groups = {}
        first_c = True
        i = 0
        ended = False
        while i < len(beats) and not ended:
            b = beats[i]
            i += 1
            r = b["role"]
            g = b.get("group")
            if g:
                if g not in groups:
                    keep = rnd.random() < b.get("p", 1.0) and when_ok(b.get("when"))
                    if g.startswith("name"):
                        keep = keep and not st["known"] and (L["name_and_number"] or 0) >= 1
                    groups[g] = keep
                if not groups[g]:
                    continue
            else:
                if rnd.random() >= b.get("p", 1.0) or not when_ok(b.get("when")):
                    continue
            if st.get("unresolved") and st.get("ended_unclear"):
                break
            if b["who"] == "A":
                if r == "greeting":
                    A(greeting_line(slot, L["greeting"], ctx))
                    st["heard"] = L["greeting"] == 2
                elif r == "recognise":
                    if st["known"]:
                        st["name_known"] = True
                        A(pick(a["moves"]["recognise"], ctx))
                elif r == "ack": A(pick(a["moves"]["ack"], ctx))
                elif r == "ask_car":
                    if st["known"]: continue
                    AG(advisor_line(slot, "need_discovery", 1 if L["need_discovery"] >= 1 else 0, ctx))
                elif r == "ask_more":
                    if L["need_discovery"] < 2 or st["unclear"]: continue
                    ctx["job_question"] = ctx.get("job_question") or "?"
                    w = advisor_line(slot, "need_discovery", 2, ctx, prefer=(None if job.get("symptom", True) else "{job_question}"))
                    if "{job_question}" in w:
                        q = rnd.choice(job["questions"])
                        ctx["job_question"] = q["q"]
                        pending_answers[:] = q["answers"]
                    else:
                        pending_answers[:] = job["since_answers"]
                    AG(w)
                elif r == "explain": A(pick(a["moves"]["explain"], ctx))
                elif r == "price":
                    if not st["price_asked"]: continue
                    lv = L["price_with_next_step"]
                    ctx["next_step"] = "" if (st["ot_na"] and ctx.get("time_chosen")) else pick(a["moves"]["next_step"])
                    A(advisor_line(slot, "price_with_next_step", lv, ctx, prefer=("{inspection_line}" if sk.get("price_mode") == "inspection" and lv == 2 else None)))
                elif r == "offer_time":
                    if st["ot_na"]: continue
                    w = advisor_line(slot, "offered_time", L["offered_time"], ctx)
                    times["n"] = 0 if not w or w == "<skip>" else (2 if "{time_2" in w else (1 if "{time_1" in w else 0))
                    AG(w)
                elif r == "probe":
                    if st["doubt"] and L["objection"] == 2: A(pick(a["moves"]["probe"], ctx))
                elif r == "objection":
                    if not st["doubt"]: continue
                    lv = L["objection"]
                    own_fits = objection["type"] in ("price", "compare") or (lv == 0 and not objection.get("_asked"))
                    if lv in (0, 1) and (not own_fits or rnd.random() < 0.6):
                        A(objection["answer_%d" % lv])
                    else:
                        A(advisor_line(slot, "objection", lv, ctx))
                elif r == "booking":
                    bl = L["asked_for_booking"]
                    if bl == 2 and not ctx.get("time_chosen"):
                        ctx["time_chosen"] = ctx["time_1"]
                    if bl == 1:
                        w = pick(a["checks"]["asked_for_booking"]["1"], key=(slot, "asked_for_booking", "1"))
                        st["callback"] = a["checks"]["asked_for_booking"]["1"].index(w) >= 2
                        AG(w)
                    else:
                        A(advisor_line(slot, "asked_for_booking", bl, ctx))
                        st["heard"] = st.get("heard") or bl == 2
                elif r == "ask_name": AG(pick(a["moves"]["ask_name"], ctx))
                elif r == "ask_number": AG(pick(a["moves"]["ask_number"], ctx))
                elif r == "confirm_number":
                    if st["known"]: continue
                    lv = L["name_and_number"]
                    if lv == 0:
                        if L["asked_for_booking"] == 2: A(advisor_line(slot, "name_and_number", 0, ctx))
                    else:
                        A(advisor_line(slot, "name_and_number", lv, ctx))
                elif r == "duration": A(pick(a["moves"]["duration"], ctx))
                elif r == "recap":
                    if L["recap"] is not None:
                        A(advisor_line(slot, "recap", L["recap"], ctx))
                    elif st["agreed"] and st["callback"] and (st["recap_raw"] or 0) >= 1:
                        A(pick(a["moves"]["recap_step"], ctx))
                elif r == "hold":
                    A(pick(a["moves"]["hold"], ctx)); lines.append(("HOLD", "[удержание]")); A(pick(a["moves"]["back_from_hold"], ctx))
                elif r == "closing":
                    t = pick(a["moves"]["closing_booked" if L["asked_for_booking"] == 2 else ("closing_callback" if st["agreed"] and st["callback"] else "closing_open")], ctx)
                    if st["tatar"] is True and a["moves"].get("tatar"):
                        t = rnd.choice(a["moves"]["tatar"]["bye"])
                    A(t)
                elif r == "say":
                    if b.get("pair") == "prev" and "pair_idx" in st:
                        A(adv_tier(b, st["pair_idx"]))
                    else:
                        A(adv_tier(b))
            else:
                if r == "open":
                    if st["unclear"]:
                        u = st["unclear"]
                        k = rnd.randrange(len(u["opening"]))
                        C(tatar_open(voice_wrap(u["opening"][k], first_c))); first_c = False
                        A(pick(u["ask"][a["tier"]]) if u.get("ask") else pick(a["moves"]["ask_what"], ctx))
                        C(voice_wrap(u["second_answer"][k], False))
                        lv = str(L["need_discovery"])
                        A(u["advisor_second"][lv])
                        if st.get("unresolved"):
                            if L["asked_for_booking"] == 1:
                                A(a["checks"]["asked_for_booking"]["1"][rnd.randrange(2)])
                                C(voice_wrap(pick(u["unresolved_end"]), False))
                            else:
                                C(voice_wrap(pick(u["unresolved_end"]), False))
                                A(advisor_line(slot, "asked_for_booking", 0, ctx))
                            A(pick(a["moves"]["closing_open"], ctx))
                            ended = True
                            continue
                        C(voice_wrap(pick(u["third_answer"][lv]), False))
                    else:
                        C(tatar_open(pick(v["open_price"] if st["price_asked"] else v["open_booking"], ctx))); first_c = False
                elif r == "give_car":
                    if L["need_discovery"] >= 1 and not st["known"]:
                        C(pick(v["give_car"], ctx))
                        st["car_known"] = True
                elif r == "answer":
                    if L["need_discovery"] >= 2 and pending_answers and not st["unclear"]:
                        C(voice_wrap(pick(pending_answers), False))
                elif r == "react_price":
                    if st["price_asked"]:
                        C(pick(v["react_price"] if L["price_with_next_step"] else v["react_no_price"], ctx))
                elif r == "name_time_first":
                    ctx["time_chosen"] = ctx["time_1"]; C(pick(v["name_own_time"], ctx))
                elif r == "respond_offer":
                    bl = L["asked_for_booking"]
                    if bl == 2 and ctx.get("time_chosen") and st["ot_na"]:
                        continue
                    if b.get("force") == "pick_of_two" or (bl == 2 and times["n"] == 2):
                        ctx["time_chosen"] = chosen_of_two(ctx, rnd); C(pick(v["pick_of_two"], ctx))
                    elif bl == 2 and times["n"] == 1:
                        ctx["time_chosen"] = ctx["time_1"]; C(pick(v["accept_one"], ctx))
                    elif bl == 2:
                        ctx["time_chosen"] = ctx["time_1"]; C(pick(v["name_own_time"], ctx))
                    elif bl == 1:
                        C(pick(v["pause"], ctx))
                    else:
                        C(pick(v["will_call"], ctx))
                elif r == "after_booking":
                    if L["asked_for_booking"] == 1:
                        if st["callback"] and rnd.random() < 0.6:
                            st["agreed"] = True
                            C(pick(v["accept_callback"], ctx))
                        else:
                            st["callback"] = False
                            C(pick(v["decline"], ctx))
                elif r == "doubt":
                    if st["doubt"]:
                        t = pick(objection["customer"])
                        objection["_asked"] = "?" in t
                        lead = pick(v.get("doubt_" + objection["type"]) or v["doubt_price"])
                        if rnd.random() < 0.4 and lead.split()[0].strip(".,!?").lower() != t.split()[0].strip(".,!?").lower():
                            t = lead + " " + t
                        C(t)
                elif r == "probe_reply":
                    if st["doubt"] and L["objection"] == 2: C(pick(objection["probe_reply"], ctx))
                elif r == "after_objection":
                    if st["doubt"]: C(pick(v["after_answer_ok" if L["asked_for_booking"] >= 1 else "after_answer_unsure"], ctx))
                elif r == "give_name":
                    C(pick(v[r], ctx)); st["name_known"] = True
                elif r == "thanks_bye":
                    C(rnd.choice(FORMS["west_tatar"]["bye"]) if st["tatar"] is True else pick(v[r], ctx))
                elif r in ("give_number", "ask_duration", "backchannel", "yes", "no", "maybe"):
                    C(pick(v[r], ctx))
                elif r == "say":
                    line = pick(b["say"], ctx)
                    st["pair_idx"] = b["say"].index(line)
                    C(tatar_open(voice_wrap(line, first_c)) if first_c else voice_wrap(line, False)); first_c = False
                    if b.get("names"):
                        st["name_known"] = True
        return head, lines

    # ---- existing job, supplier, wrong number, other, outbound
    def vendors_here(s_):
        return [x for x in VEND if x["id"] in (s_.get("vendors") or []) and site in x.get("serves", [])]

    if ctype == "existing_job":
        pool = [s_ for s_ in ej if not (slot == "22" and s_["id"] == "EJ24")]
        sk = pick(pool, key="existing")
    else:
        pool = [s_ for s_ in oth[ctype] if not s_.get("vendors") or vendors_here(s_)]
        sk = pick(pool, key=ctype)
    pool = [j for j in jobs if j["key"] not in ("fleet_pm", "pre_purchase") and not (ctype != "outbound" and j["key"] == "seasonal_tyres")]
    if sk.get("kind") == "part_late" or sk["id"] in ("SU02", "SU05", "OB08", "OB09", "OT04"):
        pool = [j for j in pool if j.get("part")]
    job = rnd.choices(pool, weights=[j["lead_share"] for j in pool])[0]
    party = sk.get("party", "customer")
    party_customer = party in ("customer",) or ctype == "existing_job"
    vk = rnd.choices(["terse", "chatty", "anxious", "price_shopper", "elderly", "angry"],
                     weights=[20, 18, 12, 6, 12, (30 if sk.get("kind") in ("complaint", "comeback", "bill") or "repeat_caller" in sk.get("tags", []) else 6)])[0]
    if sk.get("voice_filter"):
        vk = rnd.choice(sk["voice_filter"])
    v = voices[vk]
    ctx = make_ctx(slot, site, hour_now, wd, voice=v, cls=job["vehicle_classes"], belt=(job["key"] == "timing_belt"))
    set_job(ctx, job)
    t1, t2 = two_times(wd, hour_now)
    late = [h for h in FORMS["hours"] if h.endswith(":00") and int(h[:2]) >= hour_now + 2]
    pick_time = time_val(0, rnd.choice(late), wd) if late and sk.get("agreed_time") != "next_day" and rnd.random() < 0.6 else time_val(1, rnd.choice(["10:00", "12:00", "17:00", "18:00", "09:00"]), wd)
    if sk.get("vendors"):
        ctx["vendor_name"] = rnd.choice(vendors_here(sk))["name"]
    ctx.update(time_1=t1, time_2=t2, old_time=time_val(1, rnd.choice(["09:00", "10:00", "11:00", "14:00", "16:00"]), wd), time_chosen=pick_time)
    ctx["need"] = rnd.choice([c["need"] for c in job["customer_says"] if c["kind"] == "accurate"])
    if job.get("part"):
        ctx["part_name"] = {"": job["part"]["nom"], "acc": job["part"]["acc"]}
    if sk["id"] in ("EJ10",):
        ctx["bill_total"] = ctx["_found_total"]
    L = {"greeting": deal(sheet, "greeting"), "recap": deal(sheet, "recap") if sk.get("agreed") else None, "need_discovery": deal(sheet, "need_discovery")}
    st["L"] = L
    st["agreed"] = bool(sk.get("agreed"))
    st["car_known"] = True
    if force_unclear:
        ops = [u for u in unclear if "existing_job" in u["applies_to"] and (not u.get("existing_fits") or sk["kind"] in u["existing_fits"])]
        st["unclear"] = rnd.choice(ops)
        st["unresolved"] = force_unclear == "unresolved"
        first_say = next(b for b in sk["beats"] if b["who"] == "C" and b["role"] == "say")
        ctx["need"] = rnd.choice(first_say["say"])
    head = dict(type=sk.get("type", ctype), skeleton=sk["id"], job=job["key"], voice=(vk if party_customer or party == "customer" else party), levels=L,
                unclear=st["unclear"], unresolved=st.get("unresolved"))
    first_c = True
    other_who = WHO["customer"] if party_customer else WHO[party]
    rc = sk.get("recap") or {}
    callback = sk.get("recap_kind") == "callback"
    for b in sk["beats"]:
        r = b["role"]
        if rnd.random() >= b.get("p", 1.0):
            continue
        if b["who"] == "A":
            if r == "greeting":
                A(greeting_line(slot, L["greeting"], ctx))
                st["heard"] = L["greeting"] == 2
            elif r == "lookup": A(pick(a["moves"]["lookup"], ctx))
            elif r == "outbound_open":
                st["name_known"] = True
                st["heard"] = True
                A(pick(a["moves"]["outbound_open"], ctx))
            elif r == "recap":
                if L["recap"] is None:
                    continue
                if callback:
                    if L["recap"] >= 1: A(pick(a["moves"]["recap_step"], ctx))
                else:
                    keep = (ctx["job_do"], ctx["job_said"])
                    if rc:
                        k = rnd.randrange(len(rc["do"]))
                        ctx["job_do"], ctx["job_said"] = rc["do"][k], {"": rc["said"][k], "na": rc["said"][k]}
                    A(advisor_line(slot, "recap", L["recap"], ctx))
                    ctx["job_do"], ctx["job_said"] = keep
            elif r == "closing": A(pick(a["moves"][{"visit_agreed": "closing_booked", "callback_promised": "closing_callback"}.get(sk.get("outcome"), "closing_open")], ctx))
            elif r == "say":
                A(adv_tier(b, st["pair_idx"]) if b.get("pair") == "prev" and "pair_idx" in st else adv_tier(b))
        else:
            if r == "say":
                if first_c and st["unclear"]:
                    u = st["unclear"]
                    k = rnd.randrange(len(u["opening"]))
                    C(voice_wrap(u["opening"][k], True))
                    A(pick(u["ask"][a["tier"]]) if u.get("ask") else pick(a["moves"]["ask_what"], ctx))
                    C(voice_wrap(u["second_answer"][k], False))
                    lv = str(L["need_discovery"] if not st.get("unresolved") else rnd.choice([0, 1]))
                    A(u["advisor_second"][lv])
                    first_c = False
                    if st.get("unresolved"):
                        C(voice_wrap(pick(u["unresolved_end"]), False))
                        A(pick(a["moves"]["closing_open"], ctx))
                        L["recap"] = None
                        break
                    C(voice_wrap(pick(u["third_answer"][lv]), False))
                    if b.get("names"):
                        st["name_known"] = True
                    continue
                line = pick(b["say"], ctx)
                st["pair_idx"] = b["say"].index(line)
                if ctype == "outbound" and first_c:
                    C(line, other_who)
                else:
                    C(voice_wrap(line, first_c and ctype != "outbound", party_customer), other_who)
                first_c = False
                if b.get("names"):
                    st["name_known"] = True
            elif r == "respond_offer":
                ctx["time_chosen"] = chosen_of_two(ctx, rnd); C(pick(v["pick_of_two"], ctx), other_who)
            elif r == "give_car":
                C(pick(v["give_car"], ctx), other_who)
            elif r in v:
                C(pick(v[r], ctx), other_who)
    return head, lines


# which advisor answers: 3 calls each first, then by site traffic and the desk shares
plan = [s for s in SLOTS for _ in range(3)]
site_w = {"main": 45, "east": 30, "west": 25}
while len(plan) < N_SAMPLE:
    site = rnd.choices(list(site_w), weights=list(site_w.values()))[0]
    plan.append(rnd.choices(SITE[site]["advisors"], weights=SITE[site]["answered_share"])[0])
types = ["new_enquiry"] * 34 + ["existing_job"] * 15 + ["supplier"] * 3 + ["wrong_number"] * 2 + ["other"] * 2 + ["outbound"] * 4
rnd.shuffle(types)
rnd.shuffle(plan)
# design rule R13: 12 % of customer calls carry an unclear opening, one in six of them stays unclear (6 of the 49 here, 1 unresolved)
ne_idx = [i for i, t in enumerate(types) if t == "new_enquiry"]
ej_idx = [i for i, t in enumerate(types) if t == "existing_job"]
unclear_at = {i: "resolved" for i in rnd.sample(ne_idx, 4) + rnd.sample(ej_idx, 2)}
unclear_at[rnd.choice([i for i in unclear_at if types[i] == "new_enquiry"])] = "unresolved"
scripts = []
for i in range(N_SAMPLE):
    head, lines = assemble(i + 1, plan[i], types[i], unclear_at.get(i))
    scripts.append((plan[i], head, lines))


def turns(lines):
    """Consecutive lines of one speaker are one turn."""
    res = []
    for who, t in lines:
        if res and res[-1][0] == who and who != "HOLD":
            res[-1] = (who, res[-1][1] + " " + t)
        else:
            res.append((who, t))
    return res


def norm_line(t):
    t = t.lower().replace("ё", "е")
    return " ".join(re.sub(r"[^а-яa-z0-9 ]+", " ", t).split())


unfilled, unmarked, odd = [], [], []
counts, counts_all, counts_turn = {}, {}, {}
total = total_all = total_turn = 0
for slot, head, lines in scripts:
    for who, t in lines:
        if SLOT_RE.search(t) or "{" in t or "}" in t or "<" in t or "None" in t:
            unfilled.append(t)
        if MARK_RE.search(t) or "|" in t:
            unmarked.append(t)
        if re.search(r"\d", t) or re.search(r",\s*[.?!]|\s[,.]|\.\.\.\.|,,|^[а-яё]", t) or re.search(r"[A-Za-z]", t):
            odd.append(t)
        n = norm_line(t)
        total_all += 1
        counts_all[n] = counts_all.get(n, 0) + 1
        if len(n.split()) >= MIN_WORDS_FOR_DUP:
            total += 1
            counts[n] = counts.get(n, 0) + 1
    for who, t in turns(lines):
        n = norm_line(t)
        if len(n.split()) >= MIN_WORDS_FOR_DUP:
            total_turn += 1
            counts_turn[n] = counts_turn.get(n, 0) + 1
dup = sum(c - 1 for c in counts.values() if c > 1)
dup_all = sum(c - 1 for c in counts_all.values() if c > 1)
dup_turn = sum(c - 1 for c in counts_turn.values() if c > 1)
share = dup / total if total else 0
check(not unfilled, "every slot of the 60 scripts is filled%s" % ("" if not unfilled else ": " + "; ".join(unfilled[:5])))
check(not unmarked, "every gender marker of the 60 scripts is resolved%s" % ("" if not unmarked else ": " + "; ".join(unmarked[:5])))
check(not odd, "no assembled line carries a digit, a Latin letter, a lower-case start or broken punctuation%s" % ("" if not odd else ": " + "; ".join(odd[:6])))
by_type = {}
for slot, head, lines in scripts:
    by_type[head["type"]] = by_type.get(head["type"], 0) + 1
say("        scripts by type: %s" % ", ".join("%s %d" % kv for kv in sorted(by_type.items())))
say("        scripts by advisor: %s" % ", ".join("%s %d" % (s, plan.count(s)) for s in SLOTS))
nunc = sum(1 for s, h, l in scripts if h["unclear"])
say("        with an unclear opening: %d, of them left unclear: %d" % (nunc, sum(1 for s, h, l in scripts if h.get("unresolved"))))
sk_used = {h["skeleton"] for s, h, l in scripts}
jb_used = {h["job"] for s, h, l in scripts if h["type"] == "new_enquiry"}
vo_used = {h["voice"] for s, h, l in scripts}
say("        pieces seen in the sample: %d skeletons, %d job blocks in new enquiries, %d voices" % (len(sk_used), len(jb_used), len(vo_used & set(voices))))
lens = [len(turns(l)) for s, h, l in scripts]
say("        turns per script: min %d, median %d, max %d" % (min(lens), sorted(lens)[len(lens) // 2], max(lens)))
check(share < DUP_LIMIT, "exact duplicate lines across the %d scripts: %d of %d lines of %d words or more = %.2f %% (limit %.0f %%)" % (N_SAMPLE, dup, total, MIN_WORDS_FOR_DUP, 100 * share, 100 * DUP_LIMIT))
say("        the same count over turns (consecutive lines of one speaker joined, as the sample prints them): %d of %d = %.2f %%" % (dup_turn, total_turn, 100.0 * dup_turn / max(total_turn, 1)))
say("        counting every line, one-word replies included: %d of %d = %.2f %% («Угу.», «Да.», «Хорошо.» repeat in any real set of calls)" % (dup_all, total_all, 100.0 * dup_all / total_all))
top = sorted(((c, n) for n, c in counts.items() if c > 1), reverse=True)[:int(os.environ.get("TOP", "8"))]
if top:
    say("        most repeated: " + "; ".join("%r x%d" % (n, c) for c, n in top))
say()

# write the sample
md = ["# Пробная сборка: %d чистых сценариев" % N_SAMPLE, "",
      "Собрано `checks/check_bank_ru.py` из частей этой папки, случайное зерно %d. Это чистая речь, до модели ошибок распознавания (DESIGN.md, раздел 4). "
      "Реплики одного говорящего, идущие подряд, склеены в одну. В заголовке: тип звонка, скелет, блок работы, голос клиента, выпавшие уровни "
      "(g приветствие, n имя и номер, d выяснение потребности, p цена, t предложенное время, b запись, r итог, o сомнение; «-» — проверка неприменима) "
      "и неясное начало, если оно наложено. Какие десять читать первыми: `_README.md`." % RANDOM_SEED, ""]
for i, (slot, head, lines) in enumerate(scripts, 1):
    lv = head["levels"]
    lvs = " ".join("%s%s" % (SHORT[c], "-" if lv.get(c) is None else lv.get(c)) for c in CHECKS if c in lv)
    unc = ""
    if head.get("unclear"):
        unc = " · неясное начало %s (%s)%s" % (head["unclear"]["id"], head["unclear"]["kind"], ", осталось неясным" if head.get("unresolved") else "")
    md.append("## %d. %s (%s) · %s · %s · %s · голос %s" % (i, adv[slot]["name"], slot, head["type"], head["skeleton"], head["job"], head["voice"]))
    md.append("")
    md.append("`%s`%s" % (lvs, unc))
    md.append("")
    for who, t in turns(lines):
        md.append("- %s: %s" % (who if who != "HOLD" else "*удержание*", t))
    md.append("")
if not DRY:
    with open(OUT_MD, "w") as f:
        f.write("\n".join(md))
say("Sample written to calls/bank-ru/assembled-sample.md")
say()
say("RESULT " + ("PASS" if not fails else "FAIL (%d)" % len(fails)))
if not DRY:
    with open(OUT_TXT, "w") as f:
        f.write("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if fails else 0)
