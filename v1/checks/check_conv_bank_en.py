#!/usr/bin/env python3
"""Checks the English conversation bank (conversations/bank-en) and assembles a sample from it.

Counts against conversations/DESIGN.md section 5; every slot declared in bank-en/FORMAT.md; no typed money,
clock time or date; every page the assistant names is a public, current page under kb/en; no assistant line
books, quotes a price for an unseen car or promises a ready time; no advisor line shared with another advisor;
60 conversations built with a fixed seed into bank-en/assembled-sample.md, with the share of exact duplicate
messages under 3 %. Writes checks/conv_bank_en_check.txt and exits 0 when everything passes.
"""
import glob, json, os, random, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.dirname(HERE)
BANK = os.path.join(SEED, "conversations", "bank-en")
KB = os.path.join(SEED, "kb", "en")
OUT_TXT = os.path.join(HERE, "conv_bank_en_check.txt")
OUT_MD = os.path.join(BANK, "assembled-sample.md")
RANDOM_SEED = 20261113

lines_out, failures = [], []

def say(s=""):
    lines_out.append(s)

def ok(name, cond, detail=""):
    say(("PASS " if cond else "FAIL ") + name + ("" if cond or not detail else "  <- " + str(detail)[:600]))
    if not cond:
        failures.append(name)

def load(name):
    return json.load(open(os.path.join(BANK, name)))

reasons = load("reasons.json")["reasons"]
cust = load("customer-messages.json")
asst = load("assistant.json")
unclear = load("unclear.json")["loops"]
lan = load("labels-and-notes.json")
ADV_SLOTS = [5, 6, 7, 29, 16, 17, 22, 23, 24]
advisors = {s: load(os.path.join("advisors", f"{s}.json")) for s in ADV_SLOTS}
registry = json.load(open(os.path.join(SEED, "kb", "_build", "registry.json")))
catalogue = json.load(open(os.path.join(SEED, "catalogue.json")))
parc = json.load(open(os.path.join(SEED, "parc.json")))
cast = json.load(open(os.path.join(SEED, "cast.json")))
accounts = json.load(open(os.path.join(SEED, "accounts.json")))["en"]
named = json.load(open(os.path.join(SEED, "named_customers.json")))["en"]
format_md = open(os.path.join(BANK, "FORMAT.md")).read()

SLOT_RE = re.compile(r"\{([a-z_]+)\}")

# ------------------------------------------------------------------ text walkers
def texts(obj, path=""):
    """every string value under obj that is message text, with its path"""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            yield from texts(x, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("page", "item", "key", "id", "kind", "voice", "ch", "catalogue", "format", "who", "use", "draft", "reply",
                     "draft_key", "outcome", "label", "what", "level", "how", "ends", "photo", "voice_stub", "by", "note",
                     "draft_outcome", "files", "kinds", "reasons", "price_kind", "first_step", "job_page", "status", "shop", "name", "for_shops", "for_skeletons", "channels", "job", "reroll"):
                continue
            yield from texts(v, f"{path}.{k}")

ALL = []  # (file, path, text)
for name, obj in [("reasons.json", reasons), ("customer-messages.json", {k: v for k, v in cust.items() if k not in ("about", "voices", "pictures")}),
                  ("assistant.json", {k: v for k, v in asst.items() if k != "about"}), ("unclear.json", unclear),
                  ("labels-and-notes.json", lan["notes"])] + [(f"advisors/{s}.json", {k: v for k, v in a.items() if k not in ("voice", "sheet", "format", "slot", "name", "shop")}) for s, a in advisors.items()]:
    for p, t in texts(obj):
        if name == "reasons.json" and (p.endswith(".summary") or ".label" in p or p.endswith(".about")):
            continue
        ALL.append((name, p, t))

# ------------------------------------------------------------------ 1. counts
say("1. counts against conversations/DESIGN.md section 5")
need = {"price": 8, "booking": 8, "status": 8, "symptom": 8}
total = Counter()
for r, spec in reasons.items():
    for ch in ("web", "telegram"):
        if spec["shares"].get(ch, 0) > 0:
            n = len(spec["skeletons"].get(ch, []))
            total[ch] += n
            ok(f"skeletons {r}/{ch}: {n} (at least {need.get(r, 5)})", n >= need.get(r, 5))
ok(f"skeletons: web {total['web']} (section 5: 62), telegram {total['telegram']} (57 without spam)", total["web"] >= 62 and total["telegram"] >= 57)
ok(f"job blocks: {len(cust['jobs'])} (24)", len(cust["jobs"]) >= 24)
ok(f"customer voices: {len(cust['voices'])} (8)", len(cust["voices"]) >= 8)
ok(f"pictures: {len(cust['pictures'])} (40), voice stubs: {len(cust['voice_stubs'])} (6)", len(cust["pictures"]) >= 40 and len(cust["voice_stubs"]) >= 6)
for r, spec in cust["reasons"].items():
    regs = Counter(o["voice"] for o in spec["open"])
    ok(f"customer openings {r}: {len(spec['open'])} (10), registers {len(regs)}", len(spec["open"]) >= 10 and len(regs) >= 4)
for g, n in [("nudge", 8), ("close", 40), ("give_number", 10), ("pick_time", 10), ("ok", 15), ("decline_handoff", 5)]:
    ok(f"customer generic.{g}: {len(cust['generic'][g])} ({n})", len(cust["generic"][g]) >= n)
kinds = Counter(l["kind"] for l in unclear)
ok(f"unclear loops: {len(unclear)} (16; section 5 asks 20), kinds {dict(kinds)}", len(unclear) >= 16 and set(kinds) == {"vague", "wrong_thing", "two_in_one", "wrong_way_round"})
ok("every loop has open, second (both readings), third, three ask levels, three endings",
   all(l["open"] and l["second_unclear"] and l["second_clear"] and l["third"] and all(l["ask"].get(f"level_{i}") for i in range(3))
       and all(l["endings"].get(e) for e in ("after_one", "after_two", "never")) for l in unclear))
sends = asst["sends"]
n_lines = sum(len(v) for v in sends.values())
ok(f"assistant moves: {len(sends)} (20), each 3 wordings, {n_lines} lines (60)", len(sends) >= 20 and all(len(v) >= 3 for v in sends.values()) and n_lines >= 60)
drafts_n = sum(len(m) for r in asst["drafts"].values() for m in r.values())
ok(f"assistant drafts: {drafts_n} lines over {len(asst['drafts'])} reasons, 3 wordings each", all(len(m) >= 3 for r in asst["drafts"].values() for m in r.values()))
TWELVE = {"greet": "pickup", "ask": "moves.ask", "price": "price.quote", "offer a time": "booking.offer", "confirm": "booking.confirm",
          "not yet": "status.not_yet", "moved": "moving.moved", "found work": "found_work.present", "decline a discount": "moves.decline_discount",
          "sorry": "complaint.sorry", "close": "moves.close", "pass on": "moves.pass_on"}

def adv_get(a, key):
    if key == "pickup":
        return a["pickup"]
    head, _, move = key.partition(".")
    if head == "moves":
        return a["moves"].get(move, [])
    return a["replies"].get(head, {}).get(move, [])

adv_total = 0
for s, a in advisors.items():
    reps = a["replies"]
    per_reason = all(len(reps.get(r, {})) >= 2 and all(len(v) >= 4 for v in reps[r].values()) for r in reasons if r != "spam")
    twelve = all(len(adv_get(a, k)) >= 3 for k in TWELVE.values())
    outs = {e["outcome"] for e in a["edits"]}
    n = len(a["pickup"]) + sum(len(v) for r in reps.values() for v in r.values()) + sum(len(v) for v in a["moves"].values())
    adv_total += n
    ok(f"advisor {s} {a['name']}: {n} lines; replies for 9 reasons x 2 moves x 4; the 12 moves; edits {sorted(outs)}; notes {len(a['notes'])}",
       per_reason and twelve and outs == {"sent_as_is", "sent_edited", "discarded"} and len(a["notes"]) >= 4 and len(a["pickup"]) >= 4)
ok(f"advisor bank: {adv_total} lines (ledger conv.patterns 290, section 5 about 320)", adv_total >= 320)
ok(f"private notes: {len(lan['notes'])} (30)", len(lan["notes"]) >= 30)

# every beat that is a message has alternatives
def pool(use, file):
    if file == "customer":
        head, _, part = use.partition(".")
        src = cust["generic"] if head == "generic" else cust["reasons"].get(head, {})
        return src.get(part, [])
    return sends.get(use, [])

bad_beats = []
for r, spec in reasons.items():
    for ch, sks in spec["skeletons"].items():
        for sk in sks:
            for b in sk["beats"]:
                if b["who"] == "customer" and not b.get("voice"):
                    n = len(b.get("alts", [])) + len(pool(b["use"], "customer") if b.get("use") else [])
                    if n < 2: bad_beats.append(sk["id"])
                if b["who"] == "assistant":
                    uses = b.get("use") or []
                    uses = [uses] if isinstance(uses, str) else uses
                    n = len(b.get("alts", [])) + (min(len(sends.get(u, [])) for u in uses) if uses else 0)
                    if n < 1 or any(u not in sends for u in uses): bad_beats.append(sk["id"] + ":" + str(uses))
                if b["who"] == "staff" and b.get("draft"):
                    rr, _, mm = b["draft"].partition(".")
                    if mm not in asst["drafts"].get(rr, {}): bad_beats.append(sk["id"] + ": draft " + b["draft"])
                if b["who"] == "note" and b["use"] not in {n["key"] for n in lan["notes"]}: bad_beats.append(sk["id"] + ": note " + b["use"])
                if b["who"] == "handoff" and b["note"] not in asst["handoff_notes"]: bad_beats.append(sk["id"] + ": handoff note")
ok("every message beat has alternatives and every pool, draft, note it names exists", not bad_beats, bad_beats[:6])

# ------------------------------------------------------------------ 2. slots
say("\n2. slots")
declared = set()
slot_section = format_md.split("## Slots", 1)[1].split("\n## ", 1)[0]
for line in slot_section.splitlines():
    if line.startswith("| `"):
        declared |= set(re.findall(r"`([a-z_]+)`", line.split("|")[1]))
used = Counter()
for f, p, t in ALL:
    for s in SLOT_RE.findall(t):
        used[s] += 1
for x in cust["jobs"]:
    for v in [*x["said"], *x["symptom_said"], *[f["text"] for f in x["finding"]]]:
        for s in SLOT_RE.findall(v): used[s] += 1
undeclared = sorted(set(used) - declared)
ok(f"{len(used)} slots used, every one declared in FORMAT.md ({len(declared)} declared)", not undeclared, undeclared)
say("INFO declared and read only by the generator's scenario, not by a bank line: " + ", ".join(sorted(declared - set(used))))

# ------------------------------------------------------------------ 3. digits
say("\n3. no typed money, hour or date")
def strip_slots(t):
    return SLOT_RE.sub("", t)
digit_hits = []
for f, p, t in ALL:
    for ln in strip_slots(t).split("\n"):
        ln2 = re.sub(r"^\d\.\s", "", ln)
        if re.search(r"\d", ln2):
            digit_hits.append(f"{f}{p}: {ln[:60]}")
money = [f"{f}{p}" for f, p, t in ALL if re.search(r"\$|\bdollars?\b|\bbucks\b|\bcents?\b", strip_slots(t), re.I)]
clock = [f"{f}{p}" for f, p, t in ALL if re.search(r"\b(noon|midnight|o'clock|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s*(thirty|fifteen|forty-five)?\s*(a\.?m\.?|p\.?m\.?)\b", strip_slots(t), re.I)
         or re.search(r"\b(at|by|till|til|until|before|after)\s+(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|noon)\b", strip_slots(t), re.I)]
ok(f"no digit in any bank text outside slots and list numbers ({len(ALL)} texts)", not digit_hits, digit_hits[:6])
ok("no money written in words or with a dollar sign outside slots", not money, money[:6])
ok("no clock hour written in words ('at four', 'noon a.m.')", not clock, clock[:6])

# ------------------------------------------------------------------ 4. pages
say("\n4. pages the assistant names")
public = {p[:-3] for p, r in registry.items() if r.get("visibility") == "public" and not r.get("stale_on_purpose") and not r.get("not_a_page") and p.endswith(".md")}
def page_text(key):
    return open(os.path.join(KB, key + ".md")).read()
page_refs = []  # (where, page, item, text)
for mv, ls in sends.items():
    for i, l in enumerate(ls): page_refs.append((f"sends.{mv}[{i}]", l.get("page"), l.get("item"), l["text"]))
for g, ls in asst["greetings"].items():
    for i, l in enumerate(ls): page_refs.append((f"greetings.{g}[{i}]", l.get("page"), l.get("item"), l["text"]))
for r, ms in asst["drafts"].items():
    for mv, ls in ms.items():
        for i, l in enumerate(ls): page_refs.append((f"drafts.{r}.{mv}[{i}]", l.get("page"), l.get("item"), l["text"]))
for r, spec in reasons.items():
    for ch, sks in spec["skeletons"].items():
        for sk in sks:
            for b in sk["beats"]:
                if b["who"] == "assistant":
                    for i, l in enumerate(b.get("alts", [])): page_refs.append((f"{sk['id']}.alts[{i}]", l.get("page"), l.get("item"), l["text"]))
PAGE_SLOTS = {"page_price", "page_low", "page_high", "page_item", "page_term", "open_time", "close_time", "sat_hours", "next_open", "shop_address", "shop_phone"}
bad_page = [w + " " + str(pg) for w, pg, it, t in page_refs if pg and pg != "{job_page}" and pg not in public]
no_page = [w for w, pg, it, t in page_refs if (set(SLOT_RE.findall(t)) & PAGE_SLOTS) and not pg]
bad_item = [w for w, pg, it, t in page_refs if it and pg and pg != "{job_page}" and it.lower() not in page_text(pg).lower()]
for j in cust["jobs"]:
    if j["page"] not in public: bad_page.append("job " + j["key"])
    elif j["page_item"].lower() not in page_text(j["page"]).lower(): bad_item.append("job " + j["key"])
named_pages = sorted({pg for w, pg, it, t in page_refs if pg and pg != "{job_page}"} | {j["page"] for j in cust["jobs"]})
ok(f"every page key named ({len(named_pages)}) is a public, current page in kb/_build/registry.json and on disk", not bad_page and all(os.path.exists(os.path.join(KB, p + ".md")) for p in named_pages), bad_page[:6])
ok("every assistant line holding a page slot names its page", not no_page, no_page[:6])
ok("every 'item' a line or a job block names is written on its page", not bad_item, bad_item[:6])
ok("the stale pages (old warranty, brake questions, timing belt) are never named", not ({"customers/warranty-policy", "services/brakes/brake-questions", "services/engine/timing-belt"} & set(named_pages)))

# ------------------------------------------------------------------ 5. the assistant stays inside its powers
say("\n5. the assistant never books, never prices an unseen car, never promises a time, never claims the shop system")
BOOK = re.compile(r"you'?re (all )?(set|booked)|\bi('ve| have)? booked\b|\bi'?ll book\b|\bbooked you\b|\bi can book\b|\bi'?ve (moved|cancelled|scheduled)|\bsee you (at|on|then|tomorrow)\b|\bwe'?ll see you\b|\byour appointment is\b", re.I)
READY = re.compile(r"\bready (by|at|in|around)\b|\bdone by\b|\bwill be (ready|done|finished) (by|at|today|tomorrow)|\bsame day\b|\btoday by\b", re.I)
SEES = re.compile(r"\bi'?ve found it\b|\bi can see (your|the)\b|\bi('ve| have) (checked|looked up)\b|\bi see (your|the) (order|repair|appointment|bill|invoice)|\bin our system\b(?! from here)", re.I)
FORBIDDEN_SLOTS = {"job_price", "job_total", "finding_price", "finding_b_price", "diag_price", "ready_time", "eta_day", "time_a", "time_b", "day_a", "day_b"}
assistant_lines = [(w, t, False) for w, pg, it, t in page_refs if not w.startswith("drafts.")]
assistant_lines += [(f"sends.handoff_done", l["text"], False) for l in sends["handoff_done"]]
assistant_lines += [(f"unclear.{l['id']}.ask.level_{i}", q, False) for l in unclear for i in (1, 2) for q in l["ask"][f"level_{i}"]]
assistant_lines += [(f"unclear.{l['id']}.endings.{e}", l["endings"][e], False) for l in unclear for e in l["endings"]]
draft_lines = []
for r, ms in asst["drafts"].items():
    for mv, ls in ms.items():
        for i, l in enumerate(ls): draft_lines.append((f"drafts.{r}.{mv}[{i}]", l["text"], bool(l.get("echo"))))
bad = []
for w, t, echo in assistant_lines:
    if BOOK.search(t) or READY.search(t) or SEES.search(t) or set(SLOT_RE.findall(t)) & (FORBIDDEN_SLOTS | {"time_agreed", "day_agreed"}):
        bad.append(f"{w}: {t[:70]}")
ok(f"{len(assistant_lines)} lines the assistant sends: no booking, no unseen-car price slot, no ready time, no claim to see the system", not bad, bad[:6])
badd = []
for w, t, echo in draft_lines:
    s = set(SLOT_RE.findall(t))
    if READY.search(t) or SEES.search(t) or s & FORBIDDEN_SLOTS or (not echo and (BOOK.search(t) or s & {"time_agreed", "day_agreed"})):
        badd.append(f"{w}: {t[:70]}")
ok(f"{len(draft_lines)} draft lines: the same, except that a draft may repeat a time a person set ('echo')", not badd, badd[:6])
promise_words = [w for w, t, e in assistant_lines if re.search(r"\b(call you|get back to you|reach out|contact you|hear from|be in touch|answer you)\b[^.]{0,50}\b(today|tonight|this (morning|afternoon)|tomorrow|within|in an? (hour|minute)|shortly|right away)\b", t, re.I)]
ok("the assistant gives no time for a call back: 'as soon as possible' only", not promise_words, promise_words[:6])

# ------------------------------------------------------------------ 6. advisors are themselves
say("\n6. advisors")
owner = defaultdict(set)
def norm(t): return re.sub(r"\s+", " ", t.strip().lower())
for s, a in advisors.items():
    own = list(a["pickup"]) + [x for r in a["replies"].values() for v in r.values() for x in v] + [x for v in a["moves"].values() for x in v] + list(a["notes"]) + [e["sent"] for e in a["edits"] if e["outcome"] != "sent_as_is"]
    for t in own: owner[norm(t)].add(s)
shared = {t: sorted(v) for t, v in owner.items() if len(v) > 1}
ok(f"no line written by two advisors ({len(owner)} distinct lines)", not shared, list(shared.items())[:5])
outcome_ok = all(sum(a["sheet"]["draft_outcomes"].values()) == 100 for a in advisors.values())
ok("each advisor's draft outcomes are their row of section 4 (sum 100)", outcome_ok)
DESIGN_ROWS = {5: (50, 10, 40), 6: (45, 40, 15), 7: (70, 15, 15), 29: (30, 20, 50), 16: (20, 60, 20), 17: (40, 25, 35), 22: (5, 5, 90), 23: (15, 5, 80), 24: (35, 50, 15)}
ok("draft outcome rows equal conversations/DESIGN.md section 4", all(tuple(advisors[s]["sheet"]["draft_outcomes"][k] for k in ("sent_as_is", "sent_edited", "discarded")) == DESIGN_ROWS[s] for s in ADV_SLOTS))
FIRST = {5: 14, 6: 4, 7: 9, 29: 20, 16: 6, 17: 11, 22: 35, 23: 40, 24: 7}
ok("first-reply minutes equal section 4", all(advisors[s]["sheet"]["first_reply_min"] == FIRST[s] for s in ADV_SLOTS))

# ------------------------------------------------------------------ 7. sample assembly
say("\n7. sample assembly")
rng = random.Random(RANDOM_SEED)
usage = Counter()

def pick(cands, key):
    """least used wording first, random among the least used"""
    cands = list(cands)
    if not cands: return None
    m = min(usage[(key, json.dumps(c, sort_keys=True))] for c in cands)
    best = [c for c in cands if usage[(key, json.dumps(c, sort_keys=True))] == m]
    c = rng.choice(best)
    usage[(key, json.dumps(c, sort_keys=True))] += 1
    return c

people = {p["slot"]: p for p in cast["people"]}
SITE_NAME = {"main": "East Main", "east": "Bonny Oaks", "west": "Charlotte Pike"}
SITE_OF = {5: "main", 6: "main", 7: "main", 29: "main", 16: "east", 17: "east", 22: "west", 23: "west", 24: "west"}
ADV_WEIGHT = {"main": [(6, 40), (5, 25), (7, 25), (29, 10)], "east": [(16, 60), (17, 40)], "west": [(24, 45), (23, 35), (22, 20)]}
SHOP_WEIGHT = [("main", 50), ("east", 30), ("west", 20)]
techs = defaultdict(list)
for p in cast["people"]:
    if p["status"] == "active" and "technician" in p["role_key"]:
        techs[p["site"]].append(p["en"]["colleagues_call"].split(";")[0])
HOURS = page_text("customers/hours-and-locations")
SHOP_ADDR = {"main": "2106 East Main St", "east": "6340 Bonny Oaks Drive", "west": "6399 Charlotte Pike"}
SHOP_PHONE = {"main": "(423) 555-0142", "east": "(423) 555-0167", "west": "(615) 555-0119"}
assert all(v in HOURS for v in [*SHOP_ADDR.values(), *SHOP_PHONE.values()])
SHOP_SAID = {"main": ["main st", "east main", "the one on main", "main street", "downtown one"], "east": ["bonny oaks", "the hixson one", "bonny oaks dr", "the one off bonny oaks"], "west": ["nashville", "charlotte pike", "the nashville one", "west nashville", "charlotte"]}
FIRST_NAMES_F = ["Tasha", "Brittany", "Kayla", "Crystal", "Amber", "Heather", "Destiny", "LaToya", "Misty", "Courtney", "Jessica", "Ashley", "Tiffany", "Rhonda", "Kendra", "Shelby", "Morgan", "Dana", "Paula", "Carla", "Wanda", "Bonnie", "Trina", "Felicia"]
FIRST_NAMES_M = ["Cody", "Dustin", "Jamal", "Terrence", "Bobby", "Wesley", "Kyle", "Marcus", "Jeremy", "Travon", "Brent", "Clint", "Darnell", "Hank", "Russell", "Eddie", "Lamar", "Jeff", "Scotty", "Tyrone", "Earl", "Randall", "Derrick", "Keith"]
LAST_NAMES = ["Pruett", "Hensley", "Gentry", "McAfee", "Lusk", "Crowder", "Varner", "Pickens", "Blevins", "Hollis", "Tackett", "Spurlock", "Whitlow", "Ogle", "Burchett", "Kilgore", "Moneyhun", "Rains", "Dotson", "Talley", "Sizemore", "Gamble", "Hixon", "Lowery", "Napier", "Cantrell", "Wyatt", "Shelton"]
story_names = {v["name"] for v in named.values() if isinstance(v, dict) and "name" in v}
DAYS = ["tomorrow", "Thursday", "Friday", "Monday", "Tuesday", "Wednesday"]
TIMES = ["7:30", "8:00", "9:00", "10:30", "11:15", "1:00", "2:15", "3:00", "3:45"]
DAY_SAID = ["tomorrow", "thursday", "friday", "monday", "this week", "tuesday", "wed", "next week"]
TIME_SAID = ["after lunch", "first thing", "in the morning", "around noon", "before work", "after work", "early", "late afternoon"]

def money(x):
    return "${:,.2f}".format(x)

CAT = {j["key"]: j for j in catalogue["jobs"]}
CFG = catalogue["configurations"]["en"]
def job_price(key, vclass):
    j = CAT[key]["en"]
    lab = j["labour_price"]["after_rise"]
    if j["labour_pricing"] == "hourly" and j.get("hours_by_class"):
        lab *= j["hours_by_class"].get(vclass) or 1.0
    parts = 0.0
    for prt in j["parts"]:
        opt = [o for o in prt["options"] if o["tier"] == "standard"] or prt["options"]
        parts += opt[0]["list_price"] * prt["qty"]
    if j.get("parts_scale_with_class"):
        parts *= CFG["parts_class_multiplier"].get(vclass) or 1.0
    fees = sum(f.get("price", 0) for f in j["fees"])
    sup = min(0.05 * lab, 35.0) if j["shop_supplies"] else 0.0
    before = round(lab + parts + fees, 2)
    return before, round((before + sup) * (1 + CFG["tax"]["rate"]), 2), j["hours"]

def duration_words(h):
    return "half an hour" if h <= 0.6 else "an hour" if h <= 1.3 else "a couple of hours" if h <= 2.5 else "most of the day"

def page_values(page, item):
    """the figures a page states beside an item"""
    txt = page_text(page)
    lines = txt.split("\n")
    idx = next((i for i, l in enumerate(lines) if item.lower() in l.lower()), None)
    if idx is None: return {}
    if page == "prices/price-list":
        cells = [c.strip() for c in lines[idx].split("|")]
        return {"page_price": cells[5] or cells[3]}
    found = []
    for l in lines[idx: idx + 9]:
        found += re.findall(r"\$[\d,]+(?:\.\d\d)?", l)
        if "free" in l.lower() and not found: return {"page_price": "free"}
        if len(found) >= 2: break
    v = {}
    if found: v["page_price"] = found[0]; v["page_low"] = found[0]; v["page_high"] = found[-1]
    return v

PAGE_TERM = {"customers/warranty": "24 months or 24,000 miles", "customers/dropping-off-and-picking-up": "5 miles",
             "customers/towing": "$95", "customers/company-vehicles": "(423) 555-0142",
             "customers/prices-for-common-services": "9.25 %"}
assert all(v in page_text(k) for k, v in PAGE_TERM.items())

parc_models = parc["configurations"]["en"]["models"]
def draw_car():
    m = rng.choices(parc_models, weights=[x["share"] for x in parc_models])[0]
    year = rng.randint(max(m["year_from"], 2004), min(m["year_to"] or 2025, 2025))
    model = m["model"].split(" / ")[0]
    said = rng.choice([f"{year} {model.lower()}", f"{str(year)[2:]} {model.lower()}", f"{model.lower()}", f"{m['make'].lower()} {model.lower()}", f"{year} {m['make'].lower()} {model.lower().replace('-', '')}"])
    miles = max(8, (2026 - year) * rng.randint(9, 14))
    return {"car": f"{year} {m['make']} {model}", "model": model, "car_said": said, "vclass": m["vehicle_class"],
            "mileage_said": rng.choice([f"{miles}k", f"{miles},{rng.randint(100, 999)}", f"like {miles}k"])}

ADVICE_JOBS = {"advice_brakes": ["brake_check", "front_brakes", "rear_brakes"], "advice_check_engine": ["check_engine"], "advice_leak": ["coolant_leak"],
               "advice_ac": ["ac"], "advice_battery": ["battery", "alternator"], "advice_tire": ["flat", "tpms"], "advice_shake": ["balance", "alignment", "suspension_check"],
               "advice_overheat": ["coolant_leak"], "towing": None}
JOBS = {j["key"]: j for j in cust["jobs"]}

def choose_job(sk, reason, forced=None):
    if forced: return JOBS[forced]
    moves = []
    for b in sk["beats"]:
        if b["who"] == "assistant":
            u = b.get("use") or []
            moves += [u] if isinstance(u, str) else u
    cands = list(JOBS.values())
    for mv in moves:
        if mv == "price_menu": cands = [j for j in cands if j["price_kind"] in ("menu", "list") and page_values(j["page"], j["page_item"]).get("page_price")]
        elif mv == "price_range": cands = [j for j in cands if j["price_kind"] == "range"]
        elif mv == "price_depends": cands = [j for j in cands if j["price_kind"] == "depends"]
        elif mv in ADVICE_JOBS and ADVICE_JOBS[mv]: cands = [j for j in cands if j["key"] in ADVICE_JOBS[mv]]
        elif mv == "quote_needs_look": cands = [j for j in cands if j["price_kind"] in ("depends", "range")]
    if reason == "symptom": cands = [j for j in cands if j["symptom_said"]] or cands
    if reason == "found_work" or any(b["who"] == "staff" and "found_work" in json.dumps(b.get("reply")) for b in sk["beats"]):
        cands = [j for j in cands if j["finding"]] or cands
    if any(b.get("photo") == "{photo}" for b in sk["beats"]): cands = [j for j in cands if j["photo"]] or cands
    return pick(cands, "job")

DIAG_NAME = {"brake_inspection": "brake inspection", "suspension_diag": "steering and suspension inspection", "battery_test": "battery and charging test", "check_engine_diag": "check engine diagnosis", "cooling_pressure_test": "cooling system pressure test", "ac_performance_check": "A/C performance check"}
FLEET_ACCTS = [a for a in accounts["accounts"] if a["id"] in ("A1", "A3", "A4")]  # not the story threads' A2, A5, A6

def scenario(reason, channel, sk, loop):
    job = choose_job(sk, reason, (loop.get("job") if loop else None) or sk.get("job"))
    shop = rng.choices([s for s, _ in SHOP_WEIGHT], weights=[w for _, w in SHOP_WEIGHT])[0]
    if sk["id"] in ("booking.web.4",): shop = "main"
    slot = rng.choices([s for s, _ in ADV_WEIGHT[shop]], weights=[w for _, w in ADV_WEIGHT[shop]])[0]
    if sk["id"] == "booking.web.4": slot = 29
    female = rng.random() < 0.55
    while True:
        first = rng.choice(FIRST_NAMES_F if female else FIRST_NAMES_M); last = rng.choice(LAST_NAMES)
        if f"{first} {last}" not in story_names: break
    acct = rng.choice(FLEET_ACCTS)
    if reason == "fleet":
        c0 = rng.choice(acct["contacts"]); first, last = c0["name"].split()[0], c0["name"].split()[-1]
    area = rng.choice(["615", "615", "629"]) if shop == "west" else rng.choice(["423", "423", "423", "706"])
    num = rng.randint(200, 9999)
    while num in (1212, 4334): num = rng.randint(200, 9999)
    n4 = f"{num:04d}"
    car = draw_car()
    vclass = car["vclass"]
    price, total, hours = job_price(job["catalogue"], vclass)
    first_step = job["first_step"] or job["catalogue"]
    diag = job_price(first_step, vclass)[0]
    fnd = job["finding"] or JOBS["oil_change"]["finding"]
    f1 = rng.choice(fnd)
    rest = [f for j in JOBS.values() for f in j["finding"] if f["catalogue"] != f1["catalogue"]]
    f2 = rng.choice([f for f in fnd if f is not f1 and f["catalogue"] != f1["catalogue"]] or rest)
    measure = rng.choice(["3 mm", "2 mm", "4 mm", "3/32", "4/32"])
    ti = sorted(rng.sample(range(len(TIMES) - 2), 2)); ta, tb = TIMES[ti[0]], TIMES[ti[1]]
    da, db = rng.sample(DAYS, 2)
    colleagues = [people[str(s)]["en"]["colleagues_call"].split(";")[0] for s, site in SITE_OF.items() if site == shop and s != slot]
    units = rng.sample([u["unit"] for u in acct["fleet"]], 2)
    pv = page_values(job["page"], job["page_item"])
    v = {
        "first_name": first, "last_name": last, "full_name": f"{first} {last}",
        "name_typed": rng.choice([f"{first} {last}", f"{first.lower()} {last.lower()}", first, f"{first} {last[0]}", f"{first.upper()} {last.upper()}"]),
        "phone_typed": rng.choice([f"{area} 555 {n4}", f"{area}555{n4}", f"({area})555-{n4}", f"{area}-555-{n4}", f"{area}.555.{n4}"]),
        "phone": f"({area}) 555-{n4}", "sir_maam": "ma'am" if female else "sir",
        **{k: car[k] for k in ("car", "model", "car_said", "mileage_said")},
        "job": job["staff_says"], "job_said": rng.choice(job["said"]), "symptom_said": rng.choice(job["symptom_said"] or ["acting funny"]),
        "photo": rng.choice(job["photo"] or ["dash-check-engine-steady"]), "voice_len": f"0:{rng.randint(9, 48):02d}",
        "shop": SITE_NAME[shop], "shop_said": rng.choice(SHOP_SAID[shop]), "shop_address": SHOP_ADDR[shop], "shop_phone": SHOP_PHONE[shop],
        "day_said": rng.choice(DAY_SAID), "time_said": rng.choice(TIME_SAID),
        "heard_price": rng.choice(["{}", "${}", "like {} bucks", "{} out the door"]).format(int(price * rng.uniform(0.6, 0.85))),
        "company": acct["name"], "contact_first": first if reason == "fleet" else acct["contacts"][0]["name"].split()[0], "unit": units[0], "unit_b": units[1],
        "po": f"{rng.randint(1000, 9999)}{rng.choice('ABCD')}",
        "appt_day": rng.choice(["Monday", "Tuesday", "tomorrow", "Thursday", "Friday"]), "visit_day": rng.choice(["last week", "Tuesday", "yesterday", "Monday", "Friday"]),
        "days_waiting": str(rng.randint(2, 6)),
        "advisor_first": people[str(slot)]["en"]["colleagues_call"].split(";")[0],
        "colleague_first": rng.choice(colleagues) if colleagues else "Greg",
        "tech_first": rng.choice(techs[shop]), "manager_first": "Dale" if shop == "west" else "Greg",
        "job_price": money(price), "job_total": money(total), "diag_price": money(diag) if diag else "free", "diag": DIAG_NAME.get(first_step, job["staff_says"]),
        "finding": f1["text"].replace("{measure}", measure), "finding_item": f1["item"], "finding_price": money(job_price(f1["catalogue"], vclass)[0]),
        "finding_b": f2["text"].replace("{measure}", measure), "finding_b_item": f2["item"], "finding_b_price": money(job_price(f2["catalogue"], vclass)[0]),
        "measure": measure, "day_a": da, "time_a": ta, "day_b": db, "time_b": tb, "day_agreed": da, "time_agreed": ta,
        "ready_time": rng.choice(TIMES[ti[1] + 1:] + ["5:00"]), "eta_day": rng.choice(["Thursday", "tomorrow", "early next week", "Friday", "Monday"]),
        "duration": duration_words(hours),
        "open_time": "7:30 a.m.", "close_time": "5:30 p.m.", "sat_hours": "8:00 a.m. to 1:00 p.m.",
        "next_open": rng.choice(["7:30 tomorrow", "7:30 Monday"] + (["8:00 Saturday"] if shop == "main" else [])),
        "job_page": job["page"], "page_item": job["page_item"][8:] if job["page_item"].startswith("Replace ") else job["page_item"],
        **pv,
    }
    if reason == "fleet":
        u = next(x for x in acct["fleet"] if x["unit"] == units[0])
        v["model"] = u["model"].split(" ")[0] if u["model"].startswith("Transit") else u["model"]; v["car"] = f"{u['year']} {u['make']} {u['model']}"
    v["job_said"] = v["job_said"].replace("{mileage_said}", car["mileage_said"].split(",")[0].replace("like ", ""))
    out_of_hours = channel == "web" and rng.random() < 0.30
    return {"job": job, "shop": shop, "slot": slot, "v": v, "out_of_hours": out_of_hours, "vclass": vclass, "sk": sk["id"]}

CASE_SLOTS = {"page_item", "finding", "finding_b", "finding_item", "finding_b_item", "job"}
START_CAP = {"day_a", "day_b", "day_agreed", "appt_day", "eta_day", "visit_day", "ready_time"}
def fill(t, v, page=None, item=None):
    vv = dict(v)
    if page and page != "{job_page}":
        if item: vv.update(page_values(page, item))
        if page in PAGE_TERM: vv["page_term"] = PAGE_TERM[page]
    has_caps = bool(re.search(r"(^|[.!?]\s+)[A-Z]", SLOT_RE.sub("x", t)))
    def rep(m):
        val = str(vv.get(m.group(1), m.group(0)))
        if m.group(1) in CASE_SLOTS and val and not val.startswith("{"):
            before = t[:m.start()]
            at_start = before.strip() == "" or re.search(r"[.!?]\s*$|\n\s*$|^\d\.\s$|\n\d\.\s$", before)
            if at_start and has_caps: val = val[0].upper() + val[1:]
            elif not at_start and val[:2] != val[:2].upper(): val = val[0].lower() + val[1:]
        elif m.group(1) in START_CAP and val and has_caps:
            before = t[:m.start()]
            if before.strip() == "" or re.search(r"[.!?]\s*$", before): val = val[0].upper() + val[1:]
        return val
    out = SLOT_RE.sub(rep, t)
    return re.sub(r"([ap]\.m\.)\.", r"\1", out)

def fits(l, sc, state):
    if sc["vclass"] != "car" and "car like yours" in l["text"]: return False
    if l.get("for_shops") and sc["shop"] not in l["for_shops"]: return False
    if l.get("for_skeletons") and sc["sk"] not in l["for_skeletons"]: return False
    if "{first_name}" in l["text"] and not state["name_known"]: return False
    return True

sends["ask_number_known"] = [l for l in sends["ask_number"] if "name" not in l["text"]]
PRICE_MOVES = {"price_menu", "price_range", "price_depends"}
def adapt(mv, sc):
    if mv in PRICE_MOVES:
        k = sc["job"]["price_kind"]
        mv = "price_range" if k == "range" else "price_depends" if k == "depends" else "price_menu"
        if not sc["v"].get("page_price"): mv = "price_depends_engine"
    return mv

def assistant_text(use, alts, sc, state):
    uses = use if isinstance(use, list) else ([use] if use else [])
    if state["name_known"] and "ask_number" in uses:
        uses = ["ask_number_known" if u == "ask_number" else u for u in uses]
    uses = [adapt(u, sc) for u in uses]
    if uses and "price_range" in uses and sc["vclass"] != "car":
        uses = uses + ["price_bigger_vehicle"]
    if len(uses) > 1 and not alts:
        parts = []
        for u in uses:
            ls = [l for l in sends[u] if fits(l, sc, state)] or sends[u]
            l = pick(ls, "send:" + u)
            parts.append(fill(l["text"], sc["v"], l.get("page"), l.get("item")))
        return " ".join(parts)
    cands = [("alt", a) for a in (alts or []) if fits(a, sc, state)] or [("alt", a) for a in (alts or [])]
    for u in uses:
        cands += [("send:" + u, l) for l in sends[u] if fits(l, sc, state)]
    named = [c for c in cands if "{first_name}" in c[1]["text"]]
    if state["name_known"] and named and rng.random() < 0.85: cands = named
    _, l = pick(cands, "assistant:" + json.dumps(uses))
    return fill(l["text"], sc["v"], l.get("page"), l.get("item"))

TWO_REF = ("first one", "second one", "earlier one", "later one")
def customer_text(b, reason, channel, sc, state):
    v = sc["v"]
    use = b.get("use") or ""
    cands = [("alt", a) for a in b.get("alts", [])]
    if use:
        head, _, part = use.partition(".")
        src = cust["generic"] if head == "generic" else cust["reasons"].get(head, {})
        items = list(src.get(part, []))
        if reason == "symptom" and use == "symptom.more": items += sc["job"].get("symptom_more", [])
        for x in items:
            if isinstance(x, dict):
                if x.get("ch") not in ("both", channel) or x.get("voice_stub"): continue
                if x.get("decision") == "question" or x.get("intent"): continue
                if x.get("job") and x["job"] != sc["job"]["key"]: continue
                if x.get("photo") and x["photo"] != "{photo}" and x["photo"] not in sc["job"]["photo"] and reason == "symptom": continue
            cands.append(("pool", x))
    def txt(c): return c[1] if isinstance(c[1], str) else c[1]["text"]
    if use == "generic.pick_time":
        last = state["last_staff"] or ""
        has_a, has_b = v["time_a"] in last, v["time_b"] in last
        keep = []
        for c in cands:
            t = txt(c)
            if any(w in t for w in TWO_REF) and not (has_a and has_b): continue
            if ("{time_agreed}" in t or "{day_agreed}" in t) and not (has_a or has_b): continue
            keep.append(c)
        if not keep: state["need_offer"] = True
        cands = keep or [("pool", x) for x in cust["generic"]["when_free"]]
    else:
        if not state["agreed"]:
            cands = [c for c in cands if "{time_agreed}" not in txt(c) and "{day_agreed}" not in txt(c)] or cands
    _, x = pick(cands, "cust:" + use + json.dumps(b.get("alts", []))[:40])
    photo = None
    if isinstance(x, dict):
        if x.get("decision"): state["decision"] = x["decision"]
        photo = x.get("photo"); x = x["text"]
    if use == "generic.pick_time":
        last = state["last_staff"] or ""
        if any(w in x for w in ("first one", "earlier one")): ag = (v["day_a"], v["time_a"])
        elif any(w in x for w in ("second one", "later one")): ag = (v["day_b"], v["time_b"])
        else:
            opts = [o for o, t in (((v["day_a"], v["time_a"]), v["time_a"]), ((v["day_b"], v["time_b"]), v["time_b"])) if t in last]
            ag = rng.choice(opts) if opts else (v["day_a"], v["time_a"])
        v["day_agreed"], v["time_agreed"] = ag
        state["agreed"] = True
    t = fill(x, v)
    if v["first_name"].lower() in t.lower(): state["name_known"] = True
    return t, photo

def adv_reply(slot, reply, reason):
    a = advisors[slot]
    parts = reply if isinstance(reply, list) else [reply]
    out = []
    for p in parts:
        ls = adv_get(a, p)
        if not ls: continue
        if out:
            heads = {" ".join(x.split()[:2]).lower() for x in out} | {"to confirm", "to confirm:"}
            fresh = [x for x in ls if " ".join(x.split()[:2]).lower().rstrip(",:") not in {h.rstrip(",:") for h in heads}
                     and not ("To confirm" in x and any("To confirm" in o for o in out))]
            ls = fresh or ls
            me = a["name"].split()[0]
            ls = [x for x in ls if me not in x] or ls
        out.append(pick(ls, f"adv{slot}:{p}"))
    if not out:
        out = [pick(a["moves"]["close"], f"adv{slot}:moves.close")]
    txt = out[0]
    for nxt in out[1:]:
        txt += (" " if txt.rstrip()[-1:] in ".!?" else ". ") + nxt
    return txt

def draft_text(key, sc):
    if key == "price.quote_list":
        k = sc["job"]["price_kind"]
        key = "price.quote_range" if k == "range" else "price.depends" if k == "depends" else key
    if key in ("price.quote_list", "price.depends", "price.quote_range", "symptom.advise") and not sc["v"].get("page_price"):
        key = "price.no_figure" if key.startswith("price") else key
    r, _, m = key.partition(".")
    l = pick(asst["drafts"][r][m], "draft:" + key)
    return fill(l["text"], sc["v"], l.get("page"), l.get("item")), l

def build(reason, channel, sk, loop, loop_plan):
    sc = scenario(reason, channel, sk, loop)
    v, slot = sc["v"], sc["slot"]
    a = advisors[slot]
    msgs = []
    state = {"assistant_spoke": False, "owned": channel == "telegram", "first_customer": None, "prefix": None, "stop": False, "burst": False,
             "unclear": None, "name_known": channel == "telegram", "agreed": False, "last_staff": None, "open_idx": None, "need_offer": False, "decision": "approve"}
    def say_customer(t, photo=None, voice=None):
        msgs.append({"kind": "msg", "who": "customer", "text": t, "photo": photo, "voice": voice})
        if state["first_customer"] is None and t: state["first_customer"] = t
    def say_assistant(t):
        if not state["assistant_spoke"]:
            g = pick(asst["greetings"]["after_hours" if sc["out_of_hours"] else "in_hours"], "greet")
            t = fill(g["text"], v, g.get("page")) + " " + t
            state["assistant_spoke"] = True
        if state["prefix"]: t = state["prefix"] + " " + t; state["prefix"] = None
        msgs.append({"kind": "msg", "who": "assistant", "text": t})
    def sign(t, own):
        return t + a["signoff"] if (a.get("signoff") and own) else t
    def post(t, own, files=None):
        t = sign(fill(t, v), own)
        msgs.append({"kind": "msg", "who": slot, "text": t, "files": files})
        state["last_staff"] = t; state["owned"] = True
    def last_is_customer():
        for m in reversed(msgs):
            if m["kind"] == "msg": return m["who"] == "customer"
        return False
    def staff(b):
        if b.get("draft") in ("generic.close", "generic.ack") and not last_is_customer(): return
        if state["decision"] == "decline":
            b = dict(b)
            if b.get("reply") == "found_work.confirm": b["reply"] = "found_work.declined"
            if b.get("draft") == "found_work.ack": b["draft"] = "found_work.decline_ack"
        rp = b["reply"] if isinstance(b["reply"], list) else [b["reply"]]
        if state["need_offer"] and any(x in ("booking.confirm", "symptom.confirm") for x in rp):
            state["need_offer"] = False
            staff({"who": "staff", "reply": "booking.offer", "draft": "booking.ask_day", "draft_outcome": "discarded"})
            t, ph = customer_text({"who": "customer", "use": "generic.pick_time"}, reason, channel, sc, state)
            say_customer(t)
            state["need_offer"] = False
        if b.get("reroll"):
            ti = sorted(rng.sample(range(len(TIMES)), 2)); v["time_a"], v["time_b"] = TIMES[ti[0]], TIMES[ti[1]]
            v["day_a"], v["day_b"] = rng.sample([d for d in DAYS if d not in (v["day_a"], v["day_b"])], 2)
        reply = adv_reply(slot, b["reply"], reason)
        if state["prefix"]:
            reply = state["prefix"] + " " + reply; state["prefix"] = None
        if b.get("draft"):
            if state["burst"] and rng.random() < 0.6:
                dt0, _ = draft_text(b["draft"], sc)
                msgs.append({"kind": "draft", "text": dt0, "outcome": "replaced_unseen"})
            state["burst"] = False
            dt, dl = draft_text(b["draft"], sc)
            oc = b.get("draft_outcome")
            if not oc:
                w = a["sheet"]["draft_outcomes"]
                oc = rng.choices(list(w), weights=list(w.values()))[0]
            follow = None
            if oc == "sent_as_is":
                sent, own = dt, False
                if dl.get("defers"): follow = reply
            elif oc == "sent_edited":
                ed = [e for e in a["edits"] if e["draft_key"] == b["draft"] and e["outcome"] == "sent_edited"]
                sent = fill(pick(ed, f"edit{slot}")["sent"], v, dl.get("page"), dl.get("item")) if ed and rng.random() < 0.5 else reply
                own = True
            else:
                sent, own = reply, True
            msgs.append({"kind": "draft", "text": dt, "outcome": oc})
            post(sent, own, b.get("files"))
            if follow: post(follow, True)
        else:
            post(reply, True, b.get("files"))
    def run_loop():
        ending = loop_plan
        state["unclear"] = (loop["id"], ending)
        if loop.get("decision"): state["decision"] = loop["decision"]
        if state["open_idx"] is not None:
            del msgs[state["open_idx"] + 1:]
            m = msgs[state["open_idx"]]
            m["text"] = fill(rng.choice(loop["open"]), v); m["photo"] = None; state["first_customer"] = m["text"]
        web = not state["owned"]
        def ask(level):
            q = fill(rng.choice(loop["ask"][f"level_{level}"]), v)
            if web:
                say_assistant(q); return
            if level > 0 and (slot in (22, 23) or ("symptom" in loop["reasons"] and rng.random() < 0.5)):
                q = fill(pick(adv_get(a, "moves.ask"), f"adv{slot}:moves.ask"), v)
            dt = fill(loop["ask"]["level_1"][0], v)
            msgs.append({"kind": "draft", "text": dt, "outcome": "sent_as_is" if q == dt else "discarded"})
            post(q, q != dt)
        guesses = (not web) and rng.random() * 100 >= a["sheet"]["ask_chance"]
        if guesses:
            ask(0)
            if ending == "never":
                say_customer(fill(rng.choice(loop["second_unclear"]), v)); state["stop"] = True; return
            say_customer("no " + fill(rng.choice(loop["third"]), v)); return
        ask(1)
        if ending == "after_one":
            say_customer(fill(rng.choice(loop["second_clear"]), v)); state["prefix"] = fill(loop["endings"]["after_one"], v) if web else None; return
        say_customer(fill(rng.choice(loop["second_unclear"]), v))
        if ending == "never":
            if web: say_assistant(fill(loop["endings"]["never"], v))
            state["stop"] = True; return
        ask(2)
        say_customer(fill(rng.choice(loop["third"]), v)); state["prefix"] = fill(loop["endings"]["after_two"], v) if web else None

    for b in sk["beats"]:
        if state["stop"]: break
        if b.get("p") is not None and rng.random() > b["p"]: continue
        w = b["who"]
        if w == "customer":
            if b.get("voice"):
                say_customer("", voice=b["voice"]); continue
            first_turn = state["first_customer"] is None
            t, photo = customer_text(b, reason, channel, sc, state)
            photo = (b.get("photo") and fill(b["photo"], v)) or (photo and fill(photo, v))
            say_customer(t, photo)
            if first_turn: state["open_idx"] = len(msgs) - 1
            burst_p = b.get("burst") if b.get("burst") is not None else (0.25 if (b.get("use") or "").endswith(".open") or (first_turn and b.get("alts")) else 0)
            if rng.random() < burst_p and not (first_turn and loop):
                more = cust["reasons"].get(reason, {}).get("burst") or cust["generic"]["nudge"]
                say_customer(fill(pick(more, "burst:" + reason), v)); state["burst"] = True
        elif w == "assistant":
            if b.get("use") == "closing" and not (msgs and msgs[-1]["kind"] == "msg" and msgs[-1]["who"] == "customer"): continue
            say_assistant(assistant_text(b.get("use"), b.get("alts"), sc, state)); state["burst"] = False
        elif w == "handoff":
            tmpl = pick(asst["handoff_notes"][b["note"]], "hnote:" + b["note"])
            fc = state["first_customer"] or ""
            vv = dict(v); vv["customer_words"] = fc if len(fc) <= 90 else fc[:90].rsplit(" ", 1)[0] + "..."
            msgs.append({"kind": "handoff", "text": fill(tmpl, vv), "type": b["kind"]})
            state["owned"] = True
        elif w == "staff":
            staff(b)
        elif w == "note":
            n = next(x for x in lan["notes"] if x["key"] == b["use"])
            msgs.append({"kind": "note", "who": slot, "text": fill(n["text"], v)})
        elif w == "activity":
            msgs.append({"kind": "activity", "text": b["what"] + (" " + b.get("label", "") if b.get("label") else "") + (" " + b.get("level", "") if b.get("level") else "")})
        elif w == "unclear":
            if loop: run_loop()
        elif w == "end":
            msgs.append({"kind": "end", "text": b["how"]})
    if state["stop"]:
        msgs.append({"kind": "end", "text": "ended unclear: the customer stopped answering"})
    return sc, msgs, state

# the plan: every reason on every channel it occurs on, then by share
combos = [(r, ch) for r, s in reasons.items() for ch in ("web", "telegram") if s["shares"].get(ch, 0) > 0]
plan = list(combos)
weights = [reasons[r]["shares"][ch] * (11 if ch == "web" else 5) for r, ch in combos]
while len(plan) < 60:
    plan.append(rng.choices(combos, weights=weights)[0])
rng.shuffle(plan)
unclear_capable = [i for i, (r, ch) in enumerate(plan) if any(b["who"] == "unclear" for sk in reasons[r]["skeletons"][ch] for b in sk["beats"])]
loop_slots = rng.sample(unclear_capable, min(9, len(unclear_capable)))
loop_endings = dict(zip(loop_slots, ["after_one"] * 4 + ["after_two"] * 3 + ["never"] * 2))

md = ["# Assembled sample: 60 background conversations (English)", "",
      f"Built by `checks/check_conv_bank_en.py` from the bank in this folder with random seed {RANDOM_SEED}. Slots are filled with sample values the check script draws (names invented, phones in the 555 range, cars from `parc.json`, prices from `catalogue.json` and the public pages); a real build takes them from the generator's scenario. Drafts and notes are shown in italics; only plain lines reach the customer.", ""]
public_msgs, leftover, n_unclear, per_reason = [], [], Counter(), Counter()
for i, (r, ch) in enumerate(plan, 1):
    sks = reasons[r]["skeletons"][ch]
    plan_loop = loop_endings.get(i - 1)
    cands = [s for s in sks if any(b["who"] == "unclear" for b in s["beats"])] if plan_loop else sks
    sk = pick(cands, f"sk:{r}:{ch}")
    loop = None
    if plan_loop:
        kinds = next(b["kinds"] for b in sk["beats"] if b["who"] == "unclear")
        lc = [l for l in unclear if r in l["reasons"] and ch in l.get("channels", ["web", "telegram"])]
        loop = pick([l for l in lc if l["kind"] in kinds] or lc or unclear, "loop")
    sc, msgs, st = build(r, ch, sk, loop, plan_loop)
    per_reason[(r, ch)] += 1
    a = advisors[sc["slot"]]
    person = any(m["kind"] == "msg" and isinstance(m["who"], int) for m in msgs)
    head = f"### {i}. {r} · {'web chat' if ch == 'web' else 'Telegram'} · `{sk['id']}` · {sk['ends'].replace('_', ' ')}"
    if person: head += f" · slot {sc['slot']} {a['name']} ({a['shop']})"
    if st["unclear"]: head += f" · unclear {st['unclear'][0]}, {st['unclear'][1].replace('_', ' ')}"; n_unclear[st["unclear"][1]] += 1
    if sc["out_of_hours"]: head += " · after hours"
    md += [head, ""]
    for m in msgs:
        k = m["kind"]
        if k == "msg":
            who = "customer" if m["who"] == "customer" else "assistant" if m["who"] == "assistant" else f"{advisors[m['who']]['name'].split()[0]} ({m['who']})"
            extra = ""
            if m.get("photo"): extra += f" [photo: {m['photo']}]"
            if m.get("voice"): extra += f" [voice message: {m['voice']}, {sc['v']['voice_len']}]"
            if m.get("files"): extra += " [" + ", ".join(m["files"]) + "]"
            text = m["text"].replace("\n", " / ")
            md.append(f"- **{who}:** {text}{extra}")
            if m["text"]: public_msgs.append(m["text"])
        elif k == "draft":
            md.append(f"- *draft, {m['outcome'].replace('_', ' ')}: {m['text']}*")
        elif k == "handoff":
            md.append(f"- *hand-over ({m['type']}), the bot's private note: {m['text']}*")
        elif k == "note":
            md.append(f"- *private note, {advisors[m['who']]['name'].split()[0]}: {m['text']}*")
        elif k == "activity":
            md.append(f"- ({m['text']})")
        elif k == "end":
            md.append(f"- — {m['text'].replace('_', ' ')}")
        if SLOT_RE.search(m.get("text", "")): leftover.append(f"{i}: {m['text'][:60]}")
    md.append("")

cnt = Counter(public_msgs)
excess = sum(c - 1 for c in cnt.values() if c > 1)
strict = sum(c for c in cnt.values() if c > 1)
share = excess / len(public_msgs)
strict_share = strict / len(public_msgs)
dups = [(t, c) for t, c in cnt.most_common() if c > 1]
md += ["## Duplicate messages", "", f"{len(public_msgs)} public messages; {excess} are exact repeats of an earlier one ({share:.1%}); {strict} messages share their text with another ({strict_share:.1%}).", ""]
md += [f"- {c} x `{t}`" for t, c in dups]
open(OUT_MD, "w").write("\n".join(md) + "\n")

ok(f"60 conversations assembled with seed {RANDOM_SEED}, written to conversations/bank-en/assembled-sample.md", len(plan) == 60)
ok(f"every reason on every channel it occurs on is in the sample ({len(set(per_reason))} of {len(combos)})", set(per_reason) == set(combos))
ok(f"both channels: web {sum(c for (r, ch), c in per_reason.items() if ch == 'web')}, Telegram {sum(c for (r, ch), c in per_reason.items() if ch == 'telegram')}", all(any(ch == c for r, c in per_reason) for ch in ("web", "telegram")))
ok(f"unclear loops in the sample: {dict(n_unclear)}", sum(n_unclear.values()) >= 6 and len(n_unclear) == 3)
ok("no slot left unfilled in the sample", not leftover, leftover[:5])
ok(f"exact duplicate messages: {excess} of {len(public_msgs)} = {share:.2%} (under 3 %); messages sharing text with another: {strict_share:.2%}", share < 0.03, dups[:8])

# ------------------------------------------------------------------ report
say("\nfiles")
for f in sorted(glob.glob(os.path.join(BANK, "**", "*.json"), recursive=True)):
    say(f"  {os.path.relpath(f, BANK)}  {os.path.getsize(f):,} bytes")
say(f"\n{len(failures)} failed" if failures else "\nall checks pass")
open(OUT_TXT, "w").write("\n".join(lines_out) + "\n")
print("\n".join(lines_out))
sys.exit(1 if failures else 0)
