#!/usr/bin/env python3
"""Checks the Russian conversation bank (conversations/bank-ru) and assembles a sample from it.

Counts against conversations/DESIGN.md section 5; every slot declared in bank-ru/FORMAT.md; no typed money,
clock time or date; every page the assistant names is a public, current page under kb/ru and every figure
it quotes stands on that page; no assistant line books, quotes a price for an unseen car, promises a ready
time or claims to see the shop system; no advisor line shared with another advisor; no English sentence in a
message; 60 conversations built with a fixed seed into bank-ru/assembled-sample.md, with the share of exact
duplicate messages under 3 %. Writes checks/conv_bank_ru_check.txt and exits 0 when everything passes.
Modelled on check_conv_bank_en.py so that the two can be merged.
"""
import glob, json, os, random, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.dirname(HERE)
BANK = os.path.join(SEED, "conversations", "bank-ru")
KB = os.path.join(SEED, "kb", "ru")
OUT_TXT = os.path.join(HERE, "conv_bank_ru_check.txt")
OUT_MD = os.path.join(BANK, "assembled-sample.md")
RANDOM_SEED = 20261113
CHANNELS = ["web", "telegram", "vk", "avito"]
CH_RU = {"web": "чат на сайте", "telegram": "Telegram", "vk": "ВКонтакте", "avito": "Авито"}

lines_out, failures = [], []


def say(s=""):
    lines_out.append(s)


def ok(name, cond, detail=""):
    say(("PASS " if cond else "FAIL ") + name + ("" if cond or not detail else "  <- " + str(detail)[:700]))
    if not cond:
        failures.append(name)


def load(name):
    return json.load(open(os.path.join(BANK, name), encoding="utf-8"))


_reasons_file = load("reasons.json")
reasons = _reasons_file["reasons"]
EXCH = _reasons_file["exchanges"]
cust = load("customer-messages.json")
asst = load("assistant.json")
unclear = load("unclear.json")["loops"]
lan = load("labels-and-notes.json")
ADV_SLOTS = [5, 6, 7, 29, 16, 17, 22, 23, 24]
advisors = {s: load(os.path.join("advisors", "%d.json" % s)) for s in ADV_SLOTS}
registry = json.load(open(os.path.join(SEED, "kb", "_build", "registry-ru.json"), encoding="utf-8"))
catalogue = json.load(open(os.path.join(SEED, "catalogue.json"), encoding="utf-8"))
parc = json.load(open(os.path.join(SEED, "parc.json"), encoding="utf-8"))["configurations"]["ru"]
cast = {str(p["slot"]): p for p in json.load(open(os.path.join(SEED, "cast.json"), encoding="utf-8"))["people"]}
accounts = json.load(open(os.path.join(SEED, "accounts.json"), encoding="utf-8"))["ru"]["accounts"]
format_md = open(os.path.join(BANK, "FORMAT.md"), encoding="utf-8").read()

SLOT_RE = re.compile(r"\{([A-Za-z_]+)\}")
JOBS = {j["key"]: j for j in cust["jobs"]}
STEPS = {s["key"]: s for s in cust["steps"]}
FINDINGS = {f["key"]: f for f in cust["findings"]}
PICTURES = {p["key"]: p for p in cust["pictures"]}
STUBS = {s["key"]: s for s in cust["voice_stubs"]}
NON_TEXT = {"page", "item", "key", "id", "kind", "voice", "ch", "catalogue", "format", "who", "use", "draft", "reply",
            "draft_key", "outcome", "label", "what", "level", "how", "ends", "photo", "voice_stub", "by", "note",
            "draft_outcome", "files", "kinds", "reasons", "price_kind", "first_step", "shop", "name", "job",
            "guess_job", "quote", "g", "only", "decision", "intent", "advice", "when", "summary",
            "slot", "len", "seconds", "said_about", "page_item", "listing", "label_share", "shares", "sheet", "about",
            "voice_note", "gender", "make", "parc_model", "model", "city", "habits", "says", "shows", "labels", "priority",
            "keys", "if", "fits", "for_shops"}


# ------------------------------------------------------------------ text walkers
def texts(obj, path=""):
    """every string value under obj that is message text, with its path"""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            yield from texts(x, "%s[%d]" % (path, i))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in NON_TEXT:
                continue
            yield from texts(v, "%s.%s" % (path, k))


ALL = []  # (file, path, text)
cust_text = {"by_reason": cust["reasons"], "generic": cust["generic"],
             "jobs": [{k: j[k] for k in ("said", "said_inf", "said_acc", "symptom_said", "short", "staff_says")} for j in cust["jobs"]],
             "findings": [{k: f[k] for k in ("finding", "fix", "said", "why")} for f in cust["findings"]]}
for name, obj in [("reasons.json", {r: v["skeletons"] for r, v in reasons.items()}), ("customer-messages.json", cust_text),
                  ("assistant.json", {k: asst[k] for k in ("greetings", "sends", "handoff_notes", "drafts")}),
                  ("unclear.json", unclear), ("labels-and-notes.json", {"notes": lan["notes"], "acks": lan["acks"]})] + \
        [("advisors/%d.json" % s, {k: a[k] for k in ("signoff", "pickup", "replies", "moves", "edits", "notes")}) for s, a in advisors.items()]:
    for p, t in texts(obj):
        ALL.append((name, p, t))

# ------------------------------------------------------------------ 1. counts
say("1. counts against conversations/DESIGN.md section 5")
need = {"price": 8, "booking": 8, "status": 8, "symptom": 8}
bad, distinct, per = [], set(), []
for r, spec in reasons.items():
    for ch in CHANNELS:
        n = len(spec["skeletons"].get(ch, []))
        occurs = spec["shares"][ch] > 0
        if occurs and n < need.get(r, 5):
            bad.append("%s/%s: %d" % (r, ch, n))
        if not occurs and n:
            bad.append("%s/%s: skeletons on a channel with share 0" % (r, ch))
        distinct.update(s["id"] for s in spec["skeletons"].get(ch, []))
    per.append("%s %s" % (r, "/".join(str(len(spec["skeletons"].get(ch, []))) for ch in CHANNELS)))
ok("skeletons per reason and channel: 8 for price, booking, status, symptom; 5 for the other six", not bad, bad)
say("INFO web/telegram/vk/avito: " + "; ".join(per))
say("INFO %d distinct skeletons (section 5 asks 62 a language); a messenger skeleton may stand under several channels" % len(distinct))
ok("24 job blocks", len(cust["jobs"]) == 24, len(cust["jobs"]))
ok("8 customer voices", len(cust["voices"]) == 8)
ok("40 pictures and 6 voice stubs", len(cust["pictures"]) == 40 and len(cust["voice_stubs"]) == 6, (len(cust["pictures"]), len(cust["voice_stubs"])))
bad = []
for r, spec in reasons.items():
    for ch in CHANNELS:
        if spec["shares"][ch] > 0:
            n = sum(1 for o in cust["reasons"][r]["open"] if ch in o["ch"])
            if n < 10:
                bad.append("%s/%s: %d" % (r, ch, n))
ok("at least ten openings per reason and channel", not bad, bad)
say("INFO openings: %d; follow-up lines in named parts: %d; generic lines: %d" % (
    sum(len(v["open"]) for v in cust["reasons"].values()),
    sum(len(x) for v in cust["reasons"].values() for k, x in v.items() if k != "open"),
    sum(len(v) for v in cust["generic"].values())))
n_sends = sum(len(v) for v in asst["sends"].values()) + sum(len(v) for v in asst["greetings"].values())
ok("assistant: at least 20 moves with 3 wordings each", len(asst["sends"]) >= 20 and all(len(v) >= 3 for v in asst["sends"].values()),
   [k for k, v in asst["sends"].items() if len(v) < 3])
n_drafts = sum(len(x) for g in asst["drafts"].values() for x in g.values())
say("INFO assistant: %d moves, %d lines it sends, %d draft keys, %d draft lines, %d hand-off notes" % (
    len(asst["sends"]), n_sends, sum(len(g) for g in asst["drafts"].values()), n_drafts, sum(len(v) for v in asst["handoff_notes"].values())))
bad, n_adv_lines = [], 0
TWELVE = ["greet", "ask", "price", "offer_time", "confirm", "not_yet", "moved", "found_work", "decline_discount", "sorry", "close", "pass_on"]
for s, a in advisors.items():
    for reason, moves in a["replies"].items():
        for mv, ws in moves.items():
            n_adv_lines += len(ws)
            if len(ws) < 4:
                bad.append("%d %s.%s: %d" % (s, reason, mv, len(ws)))
    for mv in TWELVE:
        if len(a["moves"].get(mv, [])) < 3:
            bad.append("%d moves.%s" % (s, mv))
    n_adv_lines += sum(len(v) for k, v in a["moves"].items()) + len(a["pickup"]) + len(a["signoff"])
    kinds = Counter(e["outcome"] for e in a["edits"])
    if not all(kinds[k] for k in ("sent_as_is", "sent_edited", "discarded")):
        bad.append("%d edits lack an outcome: %s" % (s, dict(kinds)))
ok("nine advisors: every reply has four wordings, the twelve moves three, edits cover the three outcomes", not bad, bad)
say("INFO advisor lines: %d (section 5 asks about 320); edits: %d" % (n_adv_lines, sum(len(a["edits"]) for a in advisors.values())))
ok("unclear loops: at least 16 (section 5: 20), all four kinds", len(unclear) >= 20 and len({u["kind"] for u in unclear}) == 4,
   Counter(u["kind"] for u in unclear))
say("INFO unclear loops: %s" % dict(Counter(u["kind"] for u in unclear)))
ok("private notes: at least 30", len(lan["notes"]) >= 30, len(lan["notes"]))
ok("labels are the tenant's seven and the product's handoff",
   lan["labels"]["available"] == ["запись", "цена", "статус", "согласование", "жалоба", "юрлицо", "шины"] and lan["labels"]["product"] == "handoff")

# every reference resolves
bad = []
def adv_has(a, key):
    if key == "pickup":
        return bool(a["pickup"])
    if key.startswith("moves."):
        return key[6:] in a["moves"]
    r, _, m = key.partition(".")
    return m in a["replies"].get(r, {})
def draft_exists(key):
    r, _, m = key.partition(".")
    return m in asst["drafts"].get(r, {})
def pool(use):
    r, _, part = use.partition(".")
    if r == "generic":
        return cust["generic"].get(part)
    return cust["reasons"].get(r, {}).get(part)
note_keys = {n["key"] for n in lan["notes"]}
for r, spec in reasons.items():
    for ch, sks in spec["skeletons"].items():
        for sk in sks:
            for b in sk["beats"]:
                w = b["who"]
                if w == "customer":
                    uses = b.get("use", [])
                    for u in ([uses] if isinstance(uses, str) else uses):
                        if not pool(u):
                            bad.append("%s: pool %s" % (sk["id"], u))
                    if not b.get("use") and not b.get("alts"):
                        bad.append("%s: customer beat with nothing to say" % sk["id"])
                elif w == "assistant":
                    for u in b["use"]:
                        if u not in ("greet", "{price_move}", "{advice_move}", "{towing_move}") and u not in asst["sends"]:
                            bad.append("%s: assistant move %s" % (sk["id"], u))
                elif w == "handoff":
                    if b["note"] not in asst["handoff_notes"] or b["kind"] not in ("scheduling", "escalation"):
                        bad.append("%s: handoff %s" % (sk["id"], b))
                elif w == "staff":
                    d = b.get("draft")
                    if d and d != "{price_draft}" and not draft_exists(d):
                        bad.append("%s: draft %s" % (sk["id"], d))
                    rr = b.get("reply", [])
                    for k in ([rr] if isinstance(rr, str) else rr):
                        if k == "moves.call_me":
                            continue
                        for s, a in advisors.items():
                            if not adv_has(a, k):
                                bad.append("%s: advisor %d lacks %s" % (sk["id"], s, k))
                    for f in b.get("files", []):
                        if f not in PICTURES and f != "{finding_photo}":
                            bad.append("%s: file %s" % (sk["id"], f))
                elif w == "extra":
                    for k in b["keys"]:
                        if k not in EXCH:
                            bad.append("%s: exchange %s" % (sk["id"], k))
                elif w == "note" and b["use"] not in note_keys:
                    bad.append("%s: note %s" % (sk["id"], b["use"]))
                elif w == "activity" and b["what"] == "label_added" and b["label"] not in lan["labels"]["available"]:
                    bad.append("%s: label %s" % (sk["id"], b["label"]))
for j in cust["jobs"]:
    for p in j["photo"]:
        if p not in PICTURES:
            bad.append("job %s photo %s" % (j["key"], p))
    for f in j["finding"]:
        if f not in FINDINGS:
            bad.append("job %s finding %s" % (j["key"], f))
    if j["first_step"] and j["first_step"] not in STEPS:
        bad.append("job %s step %s" % (j["key"], j["first_step"]))
    if j["advice"] and "advice_" + j["advice"] not in asst["sends"]:
        bad.append("job %s advice %s" % (j["key"], j["advice"]))
cat_keys = {j["key"] for j in catalogue["jobs"]}
for x in cust["jobs"] + cust["steps"] + cust["findings"]:
    if x["catalogue"] not in cat_keys:
        bad.append("catalogue key %s" % x["catalogue"])
for f in cust["findings"]:
    if f["photo"] not in PICTURES:
        bad.append("finding photo %s" % f["photo"])
for r in cust["reasons"].values():
    for o in r["open"]:
        if o.get("voice_stub") and o["voice_stub"] not in STUBS:
            bad.append("stub %s" % o["voice_stub"])
        if o.get("photo") and o["photo"] != "{photo}" and o["photo"] not in PICTURES:
            bad.append("photo %s" % o["photo"])
for u in unclear:
    if u["job"] and u["job"] not in JOBS:
        bad.append("loop %s job %s" % (u["id"], u["job"]))
    g = u["guess_job"]
    if g and not (g in JOBS or g in STEPS or (g.startswith("catalogue:") and g[10:] in cat_keys)):
        bad.append("loop %s guess_job %s" % (u["id"], g))
for s, a in advisors.items():
    for e in a["edits"]:
        r, _, m = e["draft_key"].partition(".")
        if e["draft"] not in [x["text"] for x in asst["drafts"].get(r, {}).get(m, [])]:
            bad.append("advisor %d edit %s: the draft is not a wording of that key" % (s, e["draft_key"]))
ok("every pool, move, draft, note, picture, job and catalogue key a file names exists", not bad, bad[:12])
parc_models = {(m["make"], m["model"]) for m in parc["models"]}
form_models = {(c["make"], c["parc_model"]) for c in cust["forms"]["cars"]}
ok("forms.cars covers the 78 models of parc.json", parc_models == form_models, sorted(parc_models ^ form_models)[:6])

# ------------------------------------------------------------------ 2. slots
say("\n2. slots")
decl_part = format_md.split("## Slots", 1)[1].split("## Russian additions", 1)[0]
declared = set()
for ln in decl_part.split("\n"):
    if ln.startswith("| `"):  # a row of the slot table: the names are in its first cell
        declared.update(re.findall(r"`([a-z_]+)`", ln.split("|")[1]))
    elif ln.startswith("In `use`"):  # references a beat resolves, never text
        declared.update(re.findall(r"`\{([a-z_]+)\}`", ln))
MONEY = ["job_price", "job_total", "diag_price", "labour_price", "storage_price", "finding_price", "finding_b_price"]
declared |= {m + suf for m in MONEY for suf in ("_bare", "_num")}
used = Counter()
for name, p, t in ALL:
    for m in SLOT_RE.findall(t):
        used[m[0].lower() + m[1:]] += 1
undeclared = sorted(set(used) - declared)
ok("every slot a bank line uses is declared in bank-ru/FORMAT.md (%d slots used)" % len(used), not undeclared, undeclared)
say("INFO declared and read only by the generator's scenario, not by a bank line: " + ", ".join(sorted(declared - set(used) - {m + s for m in MONEY for s in ("_bare", "_num")})))
bad = [(n, p, t) for n, p, t in ALL if re.search(r"\[\[(?![^\]|]*\|[^\]|]*\]\])", t)]
ok("every gender choice is written [[m|f]]", not bad, bad[:3])

# ------------------------------------------------------------------ 3. digits
say("\n3. no typed money, hour or date")
def strip_slots(t):
    return SLOT_RE.sub("", t)
bad = []
for name, p, t in ALL:
    bare = re.sub(r"(?m)^[123]\. ", "", strip_slots(t))
    if re.search(r"\d", bare):
        bad.append((name, p, t[:90]))
ok("no digit outside a slot in any bank text (numbered-list markers excepted)", not bad, bad[:5])
bad = [(n, p, t[:80]) for n, p, t in ALL if re.search(r"₽|руб\b|рублей|\bтыс\b|\bтыщ", strip_slots(t))]
ok("no typed currency word or sign outside a slot", not bad, bad[:5])
quote_digits = sum(1 for g in list(asst["sends"].values()) + list(asst["greetings"].values()) + [x for d in asst["drafts"].values() for x in d.values()]
                   for l in g for v in l.get("quote", {}).values() if re.search(r"\d", v))
say("INFO figures live only in slot values: %d quoted page values in assistant.json, the forms tables, voice stub seconds" % quote_digits)

# ------------------------------------------------------------------ 4. pages
say("\n4. pages the assistant names")
def norm_sp(s):
    return re.sub(r"[    ]+", " ", s)
_pages = {}
def page_text(key):
    if key not in _pages:
        path = os.path.join(KB, key + ".md")
        _pages[key] = norm_sp(open(path, encoding="utf-8").read()) if os.path.exists(path) else None
    return _pages[key]
def page_public(key):
    e = registry.get(key + ".md")
    return bool(e) and e.get("visibility") == "public" and not e.get("stale_on_purpose") and page_text(key) is not None
asst_lines = []  # (where, line)
for g, ls in asst["greetings"].items():
    asst_lines += [("greetings." + g, l) for l in ls]
for mv, ls in asst["sends"].items():
    asst_lines += [("sends." + mv, l) for l in ls]
for r, g in asst["drafts"].items():
    for mv, ls in g.items():
        asst_lines += [("drafts.%s.%s" % (r, mv), l) for l in ls]
PAGE_SLOTS = {"page_price", "page_low", "page_high", "page_labour", "page_duration", "page_class", "page_price_class",
              "page_term", "page_term_b", "page_term_c", "open_time", "close_time", "shop_address", "shop_phone", "step_price"}
named_pages, bad, bad_quote, no_page = set(), [], [], []
for where, l in asst_lines:
    slots = {m[0].lower() + m[1:] for m in SLOT_RE.findall(l["text"])}
    pg = l.get("page")
    if slots & PAGE_SLOTS and not pg:
        no_page.append((where, l["text"][:70]))
    if pg and pg not in ("{job_page}", "{step_page}"):
        named_pages.add(pg)
        if not page_public(pg):
            bad.append((where, pg))
        else:
            for k, v in l.get("quote", {}).items():
                if norm_sp(v) not in page_text(pg):
                    bad_quote.append((where, pg, v))
                if k not in slots:
                    bad_quote.append((where, "quote for a slot the line does not hold", k))
            for sl in slots & {"page_term", "page_term_b", "page_term_c"}:
                if sl not in l.get("quote", {}):
                    bad_quote.append((where, "no quote for", sl))
for x in cust["jobs"] + cust["steps"]:
    named_pages.add(x["page"])
    if not page_public(x["page"]):
        bad.append(("job " + x["key"], x["page"]))
    elif norm_sp(x["page_item"]) not in page_text(x["page"]):
        bad_quote.append(("job " + x["key"], x["page"], x["page_item"]))
ok("every page key the assistant names is a public, current page under kb/ru (%d pages)" % len(named_pages), not bad, bad[:6])
ok("every line holding a page slot names its page", not no_page, no_page[:5])
ok("every quoted figure and every job's page item stands on the named page", not bad_quote, bad_quote[:6])
stale = sorted(k[:-3] for k, e in registry.items() if e.get("visibility") == "public" and e.get("stale_on_purpose"))
ok("no line rests on a page that is stale on purpose (%s)" % ", ".join(stale), not (named_pages & set(stale)))
say("INFO pages named: " + ", ".join(sorted(named_pages)))
public_customer = sorted(k[:-3] for k, e in registry.items() if e.get("visibility") == "public" and k.startswith("customers/") and not e.get("stale_on_purpose") and k != "customers/README.md")
say("INFO public customer pages no assistant line rests on: " + (", ".join(sorted(set(public_customer) - named_pages)) or "none"))

# ------------------------------------------------------------------ 5. the assistant stays inside its powers
say("\n5. the assistant never books, never prices an unseen car, never promises a time, never claims the shop system")
FORBIDDEN_SLOTS = {"job_price", "job_total", "diag_price", "labour_price", "storage_price", "finding_price", "finding_b_price",
                   "guess_price", "ready_time", "eta_day_on", "time_a", "time_b", "day_a", "day_a_on", "day_a_for", "day_b",
                   "day_b_on", "day_b_for", "duration", "name_addr", "colleague_first", "measure"}
FORBIDDEN_SLOTS |= {m + s for m in MONEY for s in ("_bare", "_num")}
ECHO_SLOTS = {"day_agreed", "day_agreed_on", "day_agreed_for", "time_agreed"}
bad, bad_echo = [], []
for where, l in asst_lines:
    slots = {m[0].lower() + m[1:] for m in SLOT_RE.findall(l["text"])}
    if slots & FORBIDDEN_SLOTS:
        bad.append((where, sorted(slots & FORBIDDEN_SLOTS)))
    if slots & ECHO_SLOTS and not l.get("echo"):
        bad_echo.append((where, l["text"][:60]))
    if l.get("echo") and not where.startswith("drafts."):
        bad_echo.append((where, "echo outside a draft"))
ok("no line of the assistant holds a shop-system slot (a job's price, a ready time, an offered time)", not bad, bad[:5])
ok("an agreed time appears only in a draft marked echo", not bad_echo, bad_echo[:5])
SENT = [(w, l["text"]) for w, l in asst_lines if not w.startswith("drafts.")]
BOOKS = re.compile(r"\b(записал вас|записала вас|вы записаны|запись подтвержда|забронировал|время за вами|ждём вас в |ждём вас к )", re.I)
bad = [(w, t[:70]) for w, t in SENT if BOOKS.search(t)]
ok("no line the assistant sends books a visit", not bad, bad[:5])
TIME_PROMISE = re.compile(r"(перезвонят|свяжутся|ответят|напишут)[^.!?]*(в течение|через|сегодня|завтра|утром|до конца|минут|час)", re.I)
bad = [(w, t[:90]) for w, t in SENT if TIME_PROMISE.search(t)]
ok("no line the assistant sends says when somebody will get back", not bad, bad[:5])
READY = re.compile(r"(будет готов|будет готова|сделают за|успеют|сегодня же|заберёте (сегодня|завтра))", re.I)
bad = [(w, t[:90]) for w, t in SENT if READY.search(t)]
ok("no line the assistant sends promises a ready time", not bad, bad[:5])
SEES = re.compile(r"(вижу (ваш|вашу|в системе|по базе|заказ)|по вашему заказ-наряду вижу|в системе (указано|написано)|посмотрел (в|по) (базе|системе)|нашёл вашу запись)", re.I)
bad = [(w, l["text"][:90]) for w, l in asst_lines if SEES.search(l["text"])]
ok("no line of the assistant claims to see an order, a booking or the shop system", not bad, bad[:5])
bad = []
for mv in ("price_depends", "price_depends_engine", "price_depends_to", "price_bigger", "exact_needs_person", "advice_none"):
    for l in asst["sends"][mv]:
        sl = {m[0].lower() + m[1:] for m in SLOT_RE.findall(l["text"])}
        if sl & {"page_price", "page_low", "page_high"} and mv not in ("price_depends_to",):
            bad.append((mv, l["text"][:60]))
ok("where the price depends on the car the assistant names no repair price, only the first step or the public figure it is told to", not bad, bad)
bad = [(w, t[:70]) for w, t in SENT if re.search(r"\b(я (записал|посмотрела|записала|передала|поняла|уточнила))\b", t)]
ok("the assistant speaks of itself in one gender", not bad, bad[:3])
bad = [(w, t[:70]) for w, t in [(w, l["text"]) for w, l in asst_lines] if re.search(r"\b(ты|тебе|тебя|твой|твоя)\b", t, re.I)]
ok("the assistant is on «вы»", not bad, bad[:3])
canc = re.compile(r"(в целях|в связи с тем|данн(ый|ая|ое|ого) (вопрос|услуг)|осуществля|в настоящее время|благодарим за обращение|уважаем|к сожалению, вынужден|надлежащ|вышеуказан)", re.I)
bad = [(w, l["text"][:70]) for w, l in asst_lines if canc.search(l["text"])]
ok("no канцелярит in the assistant's lines", not bad, bad[:3])
advert = re.compile(r"(лучш(ие|ий|ая) (цены|сервис)|только у нас|спешите|выгодн|уникальн|акци[яи]\b|!!)", re.I)
bad = [(w, l["text"][:70]) for w, l in asst_lines if advert.search(l["text"])]
ok("no advertising tone in the assistant's lines", not bad, bad[:3])
words = [len(l["text"].split()) for w, l in asst_lines if w.startswith("sends.")]
say("INFO the assistant's sent lines: median %d words, longest %d" % (sorted(words)[len(words) // 2], max(words)))

# ------------------------------------------------------------------ 6. advisors are themselves
say("\n6. advisors")
def norm(t):
    return re.sub(r"\s+", " ", t.strip().lower())
owner, dup = {}, []
n_lines = 0
for s, a in advisors.items():
    own = set()
    for reason, moves in a["replies"].items():
        for mv, ws in moves.items():
            own.update(norm(w) for w in ws)
    for mv, ws in a["moves"].items():
        if mv == "greet":
            continue
        own.update(norm(w) for w in ws)
    own.update(norm(w) for w in a["pickup"] + a["signoff"] + a["notes"])
    own.update(norm(e["sent"]) for e in a["edits"] if e["sent"] and e["outcome"] != "sent_as_is")
    n_lines += len(own)
    for t in own:
        if t in owner and owner[t] != s:
            dup.append((owner[t], s, t))
        owner[t] = s
ok("no line written by two advisors (%d distinct lines; the bare greeting of the move greet is not counted)" % n_lines, not dup, dup[:10])
sheet = {5: (50, 10, 40, 14, 75), 6: (45, 40, 15, 4, 85), 7: (70, 15, 15, 9, 45), 29: (30, 20, 50, 12, 80), 16: (20, 60, 20, 6, 95),
         17: (40, 25, 35, 11, 60), 22: (5, 5, 90, 35, 25), 23: (15, 5, 80, 40, 30), 24: (35, 50, 15, 7, 85)}
bad = []
for s, a in advisors.items():
    d = a["sheet"]["draft_outcomes"]
    got = (d["sent_as_is"], d["sent_edited"], d["discarded"], a["sheet"]["first_reply_min"], a["sheet"]["ask_chance"])
    if got != sheet[s] or sum(got[:3]) != 100:
        bad.append((s, got))
    if a["name"] != cast[str(s)]["ru"]["full_name"]:
        bad.append((s, a["name"]))
ok("draft outcomes, first-reply minutes and chance to ask equal conversations/DESIGN.md section 4; names equal cast.json", not bad, bad)
def avg_words(a):
    ws = [len(w.split()) for moves in a["replies"].values() for v in moves.values() for w in v]
    return sum(ws) / len(ws)
say("INFO words per reply, mean: " + ", ".join("%d: %.1f" % (s, avg_words(a)) for s, a in advisors.items()))
ok("the weak desk is curt: slots 22 and 23 average under 5 words a reply, slots 16 and 24 over 12",
   avg_words(advisors[22]) < 5 and avg_words(advisors[23]) < 5 and avg_words(advisors[16]) > 12 and avg_words(advisors[24]) > 12)
rude = re.compile(r"(дурак|идиот|отстань|сам виноват|не ной|достал|заткн|хам|ерунд[уы] не)", re.I)
bad = [(s, w) for s in (22, 23) for moves in advisors[s]["replies"].values() for v in moves.values() for w in v if rude.search(w)]
ok("the weak desk is curt by omission, never rude", not bad, bad)
def cap_share(a):
    ws = [w for moves in a["replies"].values() for v in moves.values() for w in v if not w.startswith("{")]
    return sum(1 for w in ws if w[:1].isupper()) / len(ws)
ok("typing habits hold: slots 5, 22, 23 start lower-case, slot 29 never",
   cap_share(advisors[5]) < 0.05 and cap_share(advisors[22]) < 0.05 and cap_share(advisors[23]) < 0.05 and cap_share(advisors[29]) > 0.95,
   [(s, round(cap_share(a), 2)) for s, a in advisors.items()])
emoji = re.compile(r"[\U0001F300-\U0001FAFF]|\)\)|[^:]\)$")
bad = [(29, w) for moves in advisors[29]["replies"].values() for v in moves.values() for w in v if emoji.search(w)]
ok("slot 29 writes no smiley", not bad, bad[:3])
r16 = [w for moves in advisors[16]["replies"].values() for v in moves.values() for w in v]
n16 = sum("{name_addr}" in w for w in r16)
ok("slot 16 says the customer's name in at least 85 %% of her replies (%d of %d; twice in %d)" % (n16, len(r16), sum(w.count("{name_addr}") >= 2 for w in r16)),
   n16 >= 0.85 * len(r16))

# ------------------------------------------------------------------ 7. language
say("\n7. language")
LATIN_OK = {"wi", "fi", "qr", "vin", "next", "pro", "max", "plus", "sport", "land", "cruiser", "prado", "santa", "fe", "x", "trail",
            "tour", "classic", "ghbdtn", "ok", "do", "on", "mi", "travel", "legend", "rx", "cs", "cr", "v", "f"}
for c in cust["forms"]["cars"]:
    LATIN_OK.update(w.lower() for w in re.findall(r"[A-Za-z]+", c["make"] + " " + c["model"] + " " + c["parc_model"]))
    LATIN_OK.update(w.lower() for f in c["car_said"] for w in re.findall(r"[A-Za-z]+", f["nom"]))
bad = []
for name, p, t in ALL:
    runs = re.findall(r"(?:\b[A-Za-z]{2,}\b[ ,.!?]*){3,}", strip_slots(t))
    for r_ in runs:
        ws = [w.lower() for w in re.findall(r"[A-Za-z]+", r_)]
        if sum(1 for w in ws if w not in LATIN_OK) >= 2:
            bad.append((name, p, r_))
ok("no English sentence in any message (brand and model names excepted)", not bad, bad[:5])
latin_words = Counter(w.lower() for n, p, t in ALL for w in re.findall(r"[A-Za-z]{2,}", strip_slots(t)) if w.lower() not in LATIN_OK)
say("INFO other Latin-script words in the bank: " + (", ".join("%s×%d" % kv for kv in latin_words.most_common(12)) or "none"))
cust_lines = [t for n, p, t in ALL if n == "customer-messages.json" and (".by_reason" in p or ".generic" in p)]
lower = sum(1 for t in cust_lines if t[:1].islower() or t[:1] == "{" and t[1:2].islower())
say("INFO customer lines: %d; starting lower-case: %d %%; with «щас», «чет», «норм», «спс»: %d; with a bracket smiley: %d; ending without a full stop: %d %%" % (
    len(cust_lines), round(100 * lower / len(cust_lines)), sum(1 for t in cust_lines if re.search(r"\b(щас|чет|норм|спс|пасиб|плиз|оки|лады)\b", t)),
    sum(1 for t in cust_lines if re.search(r"\)+$|\($|\)\s", t)), round(100 * sum(1 for t in cust_lines if not t.rstrip().endswith(".")) / len(cust_lines))))
ok("customers type like people in a messenger: over half of their lines start lower-case", lower / len(cust_lines) > 0.5)
story_dir = os.path.join(SEED, "conversations", "ru")
story_lines = set()
for f in glob.glob(os.path.join(story_dir, "*.json")):
    for c in json.load(open(f, encoding="utf-8"))["conversations"]:
        for t in c["timeline"]:
            if t.get("kind") == "message" and t.get("from") == "customer" and t.get("text"):
                story_lines.add(norm(t["text"]))
bank_cust = {norm(t) for t in cust_lines if len(t.split()) >= 4}
both = sorted(bank_cust & story_lines)
ok("no customer line of four words or more repeats a line of the 27 story conversations", not both, both[:5])
en_bank = os.path.join(SEED, "conversations", "bank-en")
say("INFO nothing is read from conversations/bank-en but the format: this script opens no file there")

# ------------------------------------------------------------------ 8. sample assembly
say("\n8. sample assembly")
rng = random.Random(RANDOM_SEED)
use_count = Counter()


def tx(e):
    return e if isinstance(e, str) else e["text"]


def pick(cands, key):
    """the least used wording first, ties at random"""
    cands = list(cands)
    rng.shuffle(cands)
    best = min(cands, key=lambda c: use_count[(key, tx(c))])
    use_count[(key, tx(best))] += 1
    return best


# ---- price list and pages
PRICE_ROWS = {}
for ln in page_text("prices/price-list").split("\n"):
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) >= 6 and "₽" in cells[2]:
        PRICE_ROWS[cells[0]] = cells
def rub(s):
    return float(re.sub(r"[^\d,]", "", s).replace(",", ".")) if s and re.search(r"\d", s) else None
def money(x, style=""):
    whole = abs(x - round(x)) < 0.005
    if style == "bare":
        return ("%d" % round(x)) if whole else ("{:,.2f}".format(x).replace(",", " ").replace(".", ","))
    s = "{:,.0f}".format(x).replace(",", " ") if whole else "{:,.2f}".format(x).replace(",", " ").replace(".", ",")
    return s if style == "num" else s + " ₽"
CAT = {j["key"]: j for j in catalogue["jobs"]}
def price_row(cat_key):
    name = CAT[cat_key]["ru"]["name"]
    for k, cells in PRICE_ROWS.items():
        if k == name or k.startswith(name + " ("):
            return cells
    raise KeyError(name)
def job_money(cat_key):
    cells = price_row(cat_key)
    labour, std = rub(cells[2]), rub(cells[4])
    fixed = "(фикс.)" in cells[0]
    supplies = 0 if fixed else min(500.0, 0.03 * labour)
    return {"price": std, "labour": labour, "total": (std + supplies) * 1.05, "hours": float(cells[1].replace(",", "."))}
def duration_words(h):
    for lim, w in [(0.3, "минут двадцать"), (0.5, "около получаса"), (0.8, "минут сорок"), (1.2, "около часа"), (1.8, "около полутора часов"),
                   (2.5, "часа два"), (3.2, "около трёх часов"), (99, "целый день")]:
        if h <= lim:
            return w
PRICE_RE = re.compile(r"\d[\d ]*(?:,\d+)? ₽")
def page_values(page, item, vclass="car"):
    """the figures on the line of the page that holds the item"""
    out = {}
    if page == "prices/price-list":
        cells = PRICE_ROWS[[k for k in PRICE_ROWS if k.startswith(item)][0]]
        out.update(page_price=cells[4], page_low=cells[3] or cells[4], page_high=cells[5] or cells[4], page_labour=cells[2],
                   page_duration=duration_words(float(cells[1].replace(",", "."))))
        return out
    line = [ln for ln in page_text(page).split("\n") if norm_sp(item) in ln and PRICE_RE.search(ln)]
    if not line:
        return out
    prices = PRICE_RE.findall(line[0])
    out["page_price"] = prices[0]
    if len(prices) >= 2:
        out["page_low"], out["page_high"] = prices[0], prices[1]
    if page == "customers/seasonal-tyre-change" and len(prices) >= 4:
        idx = {"car": 0, "suv": 1, "truck": 2, "van": 3}[vclass]
        out["page_class"] = {"car": "легковой автомобиль", "suv": "кроссовер", "truck": "рамный внедорожник", "van": "фургон"}[vclass]
        out["page_price_class"] = prices[idx]
    return out
HOURS_PAGE = page_text("customers/hours-and-locations")
SHOP_FACTS = {"main": ("Московское шоссе, 40", "+7 (8422) 10-40-40"), "east": ("10-й Инженерный проезд, 30", "+7 (8422) 10-40-41"),
              "west": ("ул. Техническая, 30", "+7 (843) 100-40-30")}
ok("the sample's hours, addresses and phones stand on customers/hours-and-locations",
   all(a in HOURS_PAGE and p in HOURS_PAGE for a, p in SHOP_FACTS.values()) and "9:00" in HOURS_PAGE and "20:00" in HOURS_PAGE)
bad = []
for x in cust["jobs"] + cust["steps"]:
    v = page_values(x["page"], x["page_item"])
    if x.get("price_kind") in (None, "menu", "class", "list", "range", "depends") and "page_price" not in v:
        bad.append((x["key"], x["page"]))
ok("a price can be read off the page for every job block and first step that quotes one", not bad, bad)

# ---- people
MALE = ["Андрей", "Максим", "Рамиль", "Евгений", "Игорь", "Павел", "Ренат", "Виктор", "Станислав", "Булат", "Михаил", "Азат",
        "Кирилл", "Роман", "Юрий", "Алексей", "Владимир", "Ильшат", "Глеб", "Фанис", "Константин", "Радик", "Пётр", "Захар"]
FEMALE = ["Наталья", "Гульнара", "Екатерина", "Анна", "Юлия", "Лилия", "Мария", "Елена", "Алсу", "Вера", "Диана", "Зульфия",
          "Надежда", "Оксана", "Людмила", "Айгуль", "Полина", "Рената", "Дарина", "Венера", "Жанна", "Лейла", "Софья", "Тамара"]
PATR_M = ["Петрович", "Ринатович", "Николаевич", "Васильевич"]
PATR_F = ["Ивановна", "Ринатовна", "Николаевна", "Васильевна"]
SHOP_OF = {5: "main", 6: "main", 7: "main", 29: "main", 16: "east", 17: "east", 22: "west", 23: "west", 24: "west"}
ADV_SHARE = {5: 26, 6: 26, 7: 22, 29: 26, 16: 52, 17: 48, 22: 15, 23: 45, 24: 40}
FIRST = {s: cast[str(s)]["ru"]["full_name"].split()[0] for s in ADV_SLOTS}
ADDR = {5: "Дмитрий", 6: "Алина", 7: "Никита", 29: "Татьяна", 16: "Светлана", 17: "Артём", 22: "Ринат Фаридович", 23: "Вячеслав", 24: "Камила"}
MANAGER = {"main": "@Сергей Анатольевич Мельников", "east": "@Сергей Анатольевич Мельников", "west": "@Ринат Фаридович Галиев"}
DAYS = cust["forms"]["days"]
CLASS_OF = {(m["make"], m["model"]): m["vehicle_class"] for m in parc["models"]}
YEARS = {(m["make"], m["model"]): (m["year_from"], min(m["year_to"], 2026)) for m in parc["models"]}


def draw_car():
    while True:
        c = rng.choice(cust["forms"]["cars"])
        y0, y1 = YEARS[(c["make"], c["parc_model"])]
        year = rng.randint(max(y0, 2004), y1) if y1 >= 2004 else rng.randint(y0, y1)
        said = rng.choice(c["car_said"])
        make = {"Lada": "LADA"}.get(c["make"], c["make"])
        return {"make": make, "model": c["model"], "year": year, "said": said, "vclass": CLASS_OF[(c["make"], c["parc_model"])],
                "car": "%s %s %d" % (make, c["model"], year) if c["model"] not in ("УАЗ", "ГАЗель", "ГАЗель Next", "Соболь") else "%s %d" % (c["model"] if c["model"] != "УАЗ" else "УАЗ «Буханка»", year)}


def fits_when(sk, job, vclass, slot):
    w = sk.get("when", {})
    if "kinds" in w and (job is None or job["price_kind"] not in w["kinds"]):
        return False
    if "jobs" in w and (job is None or job["key"] not in w["jobs"]):
        return False
    if w.get("advice") and (job is None or not job["advice"]):
        return False
    if w.get("bigger") and vclass == "car":
        return False
    if "advisors" in w and slot is not None and str(slot) not in w["advisors"]:
        return False
    return True


def choose_job(sk, reason, vclass, forced=None):
    if forced:
        return JOBS[forced]
    cands = [j for j in cust["jobs"] if fits_when(sk, j, vclass, None)]
    if reason == "symptom":
        cands = [j for j in cands if j["advice"] and (j["first_step"] or j["key"] in STEPS)]
    if reason in ("status", "found_work", "complaint"):
        cands = [j for j in cands if j["price_kind"] in ("list", "menu", "range", "class")]
    if any(b.get("photo") for b in sk["beats"] if b["who"] == "customer"):
        cands = [j for j in cands if j["photo"]]
    return JOBS[pick([j["key"] for j in cands], "job")]


def scenario(reason, channel, sk, loop, forced_g=None):
    sc = {"reason": reason, "channel": channel}
    g = sc["g"] = forced_g or rng.choice("mf")
    first = pick(MALE if g == "m" else FEMALE, "name")
    sc["elderly"] = rng.random() < 0.12 and reason != "fleet"
    sc["first_name"] = first
    sc["name_addr"] = "%s %s" % (first, rng.choice(PATR_M if g == "m" else PATR_F)) if sc["elderly"] and channel in ("telegram", "vk") else first
    sc["name_typed"] = rng.choice([first, first.lower(), first, first.lower()])
    n = "%s%07d" % (rng.choice(["907", "935"]), rng.randint(1000000, 9999999))
    sc["phone_typed"] = rng.choice(["8" + n, "+7 %s %s-%s-%s" % (n[:3], n[3:6], n[6:8], n[8:]), "8 %s %s %s %s" % (n[:3], n[3:6], n[6:8], n[8:]), "+7" + n])
    car = draw_car()
    if sk.get("when", {}).get("bigger"):
        while car["vclass"] == "car":
            car = draw_car()
    sc["carinfo"] = car
    # the shop and the advisor
    cand_slots = [s for s in ADV_SLOTS if "advisors" not in sk.get("when", {}) or str(s) in sk["when"]["advisors"]]
    # the sample gives every advisor about the same number of chats, so that a reader can compare the nine voices
    slot = min(cand_slots, key=lambda s: (use_count[("slot", s)], rng.random()))
    use_count[("slot", slot)] += 1
    sc["slot"] = slot
    shop = sc["shop_key"] = SHOP_OF[slot]
    sf = cust["forms"]["shops"][shop]
    sc.update(shop=sf["shop"], shop_at=sf["shop_at"], shop_said=rng.choice(sf["shop_said"]), shop_said_at=rng.choice(sf["shop_said_at"]),
              shop_address=SHOP_FACTS[shop][0], shop_phone=SHOP_FACTS[shop][1])
    mates = [s for s in ADV_SLOTS if SHOP_OF[s] == shop and s != slot and s != 22]
    mate = rng.choice(mates)
    sc["colleague_first"] = FIRST[mate]
    full = cast[str(mate)]["ru"]["full_name"].split()
    sc["colleague_mention"] = "@" + (" ".join(full) if len(full) == 2 else full[0] + " " + full[-1])
    sc["manager_mention"] = MANAGER[shop]
    sc["advisor_addr"] = ADDR[slot]
    # the job
    forced = loop["job"] if loop and loop["job"] else None
    job = sc["jobinfo"] = choose_job(sk, reason, car["vclass"], forced)
    jm = job_money(job["catalogue"])
    stepkey = job["first_step"] or (job["key"] if job["key"] in STEPS else None)
    sc["stepinfo"] = STEPS[stepkey] if stepkey else None
    said = car["said"]
    sc.update(car=car["car"], car_make=car["make"], model=car["model"], car_year=str(car["year"]),
              car_said=said["nom"], car_said_acc=said["acc"], car_said_gen=said["gen"], car_said_dat=said["dat"], car_said_prep=said["prep"],
              car_gender=said["gender"],
              job=job["staff_says"]["nom"], job_acc=job["staff_says"]["acc"], job_short=job["short"],
              job_said=pick(job["said"], "said"), job_said_inf=pick(job["said_inf"], "said_inf"), job_said_acc=pick(job["said_acc"], "said_acc"),
              symptom_said=pick(job["symptom_said"], "symptom"), photo=rng.choice(job["photo"]) if job["photo"] else None,
              job_page=job["page"], duration=duration_words(jm["hours"]) if jm["hours"] else "минут десять")
    sc["page_duration"] = sc["duration"]
    for k, v in (("job_price", jm["price"]), ("job_total", jm["total"]), ("labour_price", jm["labour"]), ("storage_price", 3000.0)):
        sc[k], sc[k + "_bare"], sc[k + "_num"] = money(v), money(v, "bare"), money(v, "num")
    if sc["stepinfo"]:
        sm = job_money(sc["stepinfo"]["catalogue"])
        sc["step"] = sc["stepinfo"]["staff_says"]["nom"]
        sc["step_page"] = sc["stepinfo"]["page"]
        sc["step_price"] = page_values(sc["stepinfo"]["page"], sc["stepinfo"]["page_item"]).get("page_price")
        sc["diag_price"], sc["diag_price_bare"], sc["diag_price_num"] = money(sm["price"]), money(sm["price"], "bare"), money(sm["price"], "num")
    else:
        sc["step"] = "диагностика"
        sc["diag_price"], sc["diag_price_bare"], sc["diag_price_num"] = money(800), money(800, "bare"), money(800, "num")
    if reason == "symptom" and sc["stepinfo"]:
        # a symptom chat books the first step, not the repair nobody has diagnosed yet
        st = sc["stepinfo"]
        sm = job_money(st["catalogue"])
        sc.update(job=st["staff_says"]["nom"], job_acc=st["staff_says"]["acc"], job_short=st["staff_says"]["nom"],
                  duration=duration_words(sm["hours"]), page_duration=duration_words(sm["hours"]))
        for k, v in (("job_price", sm["price"]), ("job_total", sm["total"])):
            sc[k], sc[k + "_bare"], sc[k + "_num"] = money(v), money(v, "bare"), money(v, "num")
    sc.update(page_values(job["page"], job["page_item"], car["vclass"]))
    fs = [FINDINGS[k] for k in job["finding"]]
    rng.shuffle(fs)
    if len(fs) < 2:
        fs.append(FINDINGS["air_filter" if fs[0]["key"] != "air_filter" else "cabin_filter"])
    for pre, f in (("finding", fs[0]), ("finding_b", fs[1])):
        fm = job_money(f["catalogue"])
        sc[pre], sc[pre + "_fix"], sc[pre + "_why"], sc[pre + "_said"] = f["finding"], f["fix"], f["why"], f["said"]
        sc[pre + "_price"], sc[pre + "_price_bare"], sc[pre + "_price_num"] = money(fm["price"]), money(fm["price"], "bare"), money(fm["price"], "num")
    sc["finding_photo"] = fs[0]["photo"]
    sc["measure"] = rng.choice(["2 мм", "3 мм"])
    if loop and loop["guess_job"]:
        g_ = loop["guess_job"]
        ck = g_[10:] if g_.startswith("catalogue:") else (JOBS[g_]["catalogue"] if g_ in JOBS else STEPS[g_]["catalogue"])
        sc["guess_price"] = money(job_money(ck)["price"])
    # days and times
    dk = rng.sample(["tomorrow", "mon", "tue", "wed", "thu", "fri", "sat", "sun"], 4)
    a, b, v, appt = [DAYS[k] for k in dk]
    sc.update(day_a=a["nom"], day_a_on=a["on"], day_a_for=a["for"], day_b=b["nom"], day_b_on=b["on"], day_b_for=b["for"], _a=a, _b=b)
    ta, tb = rng.choice(["9:30", "10:00", "11:00", "12:30"]), rng.choice(["14:00", "15:30", "17:00", "18:30"])
    sc.update(time_a=ta, time_b=tb)
    first_taken = rng.random() < 0.6
    ag, tg = (a, ta) if first_taken else (b, tb)
    sc.update(day_agreed=ag["nom"], day_agreed_on=ag["on"], day_agreed_for=ag["for"], time_agreed=tg,
              time_agreed_said=rng.choice([tg, tg.split(":")[0] if tg.endswith(":00") else tg.replace(":", " "), tg]))
    sc.update(day_said=rng.choice([a["on"], a["on"], "на этой неделе", "на выходных"]), day_said_for=a["for"],
              time_said=rng.choice(["с утра", "после работы", "ближе к вечеру", "до обеда", "в первой половине дня"]))
    sc.update(appt_day_on=appt["on"], appt_day_for=appt["for"], appt_day_from=appt["from"],
              visit_day=rng.choice(["вчера", "позавчера", "в прошлую пятницу", "на прошлой неделе", "в понедельник"]),
              visit_date=rng.choice(["12 октября", "3 сентября", "28 августа", "19 июня"]),
              days_waiting=rng.choice(["третий день", "четвёртый день", "пятый день", "вторую неделю"]),
              ready_time=rng.choice(["сегодня к 17:00", "к 18:30", "завтра к обеду", "сегодня до 19:00", "завтра к 12:00"]),
              eta_day_on=v["on"], heard_price=rng.choice([money(jm["price"], "bare"), "%d тыщ" % max(1, round(jm["price"] / 1000))]),
              mileage_said=rng.choice(["120 тыс", "98 000", "150 тыщ"]), tyre_size_said=rng.choice(["r15", "r16", "185/65 r15", "205/55 r16", "r17"]),
              season_for="на зиму", open_time="9:00", close_time="20:00", voice_len="0:27")
    acc = rng.choice([x for x in accounts if x["name"] not in ("Тёплый контур", "Вкусный выезд", "Идель-Электромонтаж")])
    sc.update(company=acc["name"] if "«" in acc["name"] else "«%s»" % acc["name"], contact_first=first,
              unit=rng.choice(["№ 3", "№ 7", "№ 12"]), unit_b=rng.choice(["№ 5", "№ 9", "№ 14"]), po="%d/%02d" % (rng.randint(40, 180), rng.randint(6, 11)))
    sc["after_hours"] = rng.random() < (0.30 if channel == "web" else 0.12)
    hour = rng.choice([20, 21, 22, 23]) if sc["after_hours"] else rng.randint(9, 19)
    sc["hello"] = "Доброе утро" if hour < 11 else "Добрый день" if hour < 17 else "Добрый вечер"
    sc["hello_lc"] = sc["hello"].lower()
    return sc


GENDER_RE = re.compile(r"\[\[([^\]|]*)\|([^\]|]*)\]\]")
LOWER_TYPISTS = {5, 22, 23}


def fill(t, sc, extra=None):
    vals = dict(sc)
    if extra:
        vals.update(extra)
    def sub(m):
        name = m.group(1)
        key = name[0].lower() + name[1:]
        v = vals.get(key)
        if v is None:
            return m.group(0)
        v = str(v)
        return v[:1].upper() + v[1:] if name[0].isupper() else v
    for _ in range(2):  # a slot's value may hold a slot (a symptom that names the mileage)
        t = GENDER_RE.sub(lambda m: m.group(1 if sc["g"] == "m" else 2), t)
        t = SLOT_RE.sub(sub, t)
    return t


_GREET = r"(?:здравствуйте|добрый день|доброе утро|добрый вечер)"
_NAME = r"[А-ЯЁ][а-яё]+(?: [А-ЯЁ][а-яё]+)?"
GREET_RES = [re.compile(r"^%s, %s[!.]\s*" % (_NAME, _GREET), re.I), re.compile(r"^%s, %s[!.]\s*" % (_GREET, _NAME), re.I),
             re.compile(r"^%s[!.]\s*" % _GREET, re.I)]


def strip_greeting(t):
    """a second message in one conversation does not greet again"""
    for rx in GREET_RES:
        m = rx.match(t)
        if m and t[m.end():].strip():
            rest = t[m.end():]
            return rest[:1].upper() + rest[1:] if t[:1].isupper() else rest
    return t


def join_parts(parts):
    out = ""
    for i, p in enumerate(parts):
        if not p:
            continue
        if out:
            p = strip_greeting(p)
            if out[-1] not in ".!?…)":
                out += "."
            out += " "
        out += p
    return out


def entry_fits(e, sc, channel):
    if isinstance(e, str):
        return "{advisor_addr}" not in e or channel in ("telegram", "vk")
    if e.get("g") and e["g"] != sc["g"]:
        return False
    if e.get("voice_stub") and STUBS[e["voice_stub"]].get("g") not in (None, sc["g"]):
        return False
    if "{advisor_addr}" in e["text"] and channel not in ("telegram", "vk"):
        return False
    for o in e.get("only", []):
        if o == "masc_car" and sc["car_gender"] != "m":
            return False
        if o == "fem_car" and sc["car_gender"] != "f":
            return False
    jobs_only = [o for o in e.get("only", []) if o not in ("masc_car", "fem_car")]
    if jobs_only and sc["jobinfo"]["key"] not in jobs_only:
        return False
    return True


PURE_GREETING = re.compile(r"^(?:%s|привет|доброго времени суток)[!.)]*$" % _GREET, re.I)


def split_burst(text):
    """a thought in two messages: cut after the first sentence"""
    if len(text) < 25:
        return [text]
    m = re.search(r"[.!?)] (?=\S)", text)
    if not m:
        return [text]
    a, b = text[:m.start() + 1].strip(), text[m.end():].strip()
    if a.endswith(".") and not a.endswith(".."):
        a = a[:-1]
    if len(b.split()) < 2 or len(a.split()) < 2 or PURE_GREETING.match(a):
        return [text]
    return [a, b]


def set_agreed(sc, which):
    d, t = (sc["_a"], sc["time_a"]) if which == "a" else (sc["_b"], sc["time_b"])
    sc.update(day_agreed=d["nom"], day_agreed_on=d["on"], day_agreed_for=d["for"], time_agreed=t,
              time_agreed_said=rng.choice([t, t.split(":")[0] if t.endswith(":00") else t.replace(":", " "), t]))


def customer_msgs(b, reason, channel, sc, state):
    """the messages of one customer turn: [(text, attachment)]"""
    out = []
    uses = b.get("use", [])
    uses = [uses] if isinstance(uses, str) else list(uses)
    if uses == ["generic.pick_time"]:
        last = state.get("offered", "")
        has_a, has_b = sc["time_a"] in last, sc["time_b"] in last
        if has_a or has_b:
            set_agreed(sc, rng.choice("ab") if has_a and has_b else ("a" if has_a else "b"))
        else:
            set_agreed(sc, "a")
            uses = ["generic.when_free"]
    if uses and uses[0] in ("generic.pick_time", "generic.when_free") and rng.random() < 0.3:
        uses = uses + ["generic.pick_more"]
    if not uses:
        uses = [None]
    for u in uses:
        cands = [a if isinstance(a, dict) else {"text": a} for a in b.get("alts", [])] if (u is None or (b.get("alts") and len(uses) == 1)) else []
        opening = False
        if u:
            p = pool(u)
            opening = u.endswith(".open")
            p = [e if isinstance(e, dict) else {"text": e} for e in p]
            if opening:
                p = [o for o in p if channel in o["ch"] or b.get("stub")]
                kind = b.get("kind")
                p = [o for o in p if (o.get("kind") == kind if kind else not o.get("kind"))]
                p = [o for o in p if bool(o.get("two")) == bool(b.get("two"))]
                p = [o for o in p if bool(o.get("voice_stub")) == bool(b.get("stub"))]
                p = [o for o in p if entry_fits(o, sc, channel)]
                if b.get("photo"):
                    p = [o for o in p if o.get("photo")]
                else:
                    p = [o for o in p if o.get("photo") != "{photo}"] or p
                if b.get("voice"):
                    p = [o for o in p if o["voice"] == b["voice"]] or p
                elif sc["elderly"]:
                    p = [o for o in p if o["voice"] in ("elderly", "polite")] or p
                else:
                    p = [o for o in p if o["voice"] != "elderly"] or p
            cands += p
        cands = [c for c in cands if entry_fits(c, sc, channel)]
        cands = [c for c in cands if fill(c["text"], sc) not in state.setdefault("said", set())] or cands
        if not cands:
            continue
        e = pick(cands, "c:" + (u or "alts"))
        text = fill(e["text"], sc)
        att = None
        if e.get("photo"):
            key = sc["photo"] if e["photo"] == "{photo}" else e["photo"]
            att = "фото: %s (%s)" % (key, PICTURES[key]["shows"]) if key else None
        if e.get("voice_stub"):
            st = STUBS[e["voice_stub"]]
            att = "%s: %s, 0:%02d, %s" % ("аудиофайл" if channel == "web" else "голосовое", st["key"], st["seconds"], st["said"])
            text = ""
        parts = text.split("\n") if "\n" in text else [text]
        if len(parts) == 1 and u and not u.startswith("generic.") and rng.random() < 0.45:
            parts = split_burst(text)
        if opening and len(parts) == 1 and "{car_said" not in e["text"] and "{car}" not in e["text"] and not e.get("voice_stub") \
                and reason in ("price", "booking", "symptom") and not sc.get("_loop") and rng.random() < b.get("burst", 0.3):
            parts.append(fill(tx(pick([c for c in cust["generic"]["give_car"] if entry_fits(c, sc, channel)], "c:give_car")), sc))
        bp = cust["reasons"].get(reason, {}).get("burst") if opening else None
        if bp and len(parts) == 1 and not e.get("voice_stub") and not sc["elderly"] and e.get("voice") not in ("business", "one_word") and rng.random() < 0.4:
            bc = [c if isinstance(c, dict) else {"text": c} for c in bp]
            bc = [c for c in bc if entry_fits(c, sc, channel)]
            if bc:
                parts.append(fill(pick(bc, "c:burst:" + reason)["text"], sc))
        for i, ptxt in enumerate(parts):
            out.append((ptxt, att if i == 0 else None))
            state["said"].add(ptxt)
        if not state.get("customer_words"):
            state["customer_words"] = " ".join(parts) if parts[0] else "(голосовое сообщение)"
        if "{car" in e["text"] or u == "generic.give_car" or any(sc["car_said"] in x for x in parts):
            state["car_named"] = True
        if opening and (sc["shop_said"] in text or sc["shop_said_at"] in text):
            state["shop_given"] = True
    return out


def resolve_move(mv, sc):
    job = sc["jobinfo"]
    if mv == "{price_move}":
        pk = job["price_kind"]
        if pk in ("menu", "class"):
            return "price_class" if sc.get("page_price_class") and sc["carinfo"]["vclass"] != "car" else "price_menu"
        return {"list": "price_list", "range": "price_range", "depends": "price_depends", "depends_engine": "price_depends_engine",
                "depends_ac": "price_depends_ac", "depends_to": "price_depends_to"}[pk]
    if mv == "{advice_move}":
        return "advice_" + job["advice"] if job["advice"] else "advice_none"
    if mv == "{towing_move}":
        return "towing_kazan" if sc["shop_key"] == "west" else "towing_ulsk"
    return mv


def line_values(l, sc):
    extra = dict(l.get("quote", {}))
    if l.get("page") == "{step_page}" and sc["stepinfo"]:
        extra.update(page_values(sc["stepinfo"]["page"], sc["stepinfo"]["page_item"]))
    return extra


def assistant_text(uses, sc, state):
    parts = []
    for mv in uses:
        if mv == "greet":
            if state.get("greeted"):
                continue
            state["greeted"] = True
            l = pick(asst["greetings"]["after_hours" if sc["after_hours"] else "in_hours"], "a:greet")
        else:
            mv = resolve_move(mv, sc)
            if mv == "price_depends" and not sc["stepinfo"]:
                continue
            if mv == "ask_shop" and state.get("shop_given"):
                continue
            ls = [x for x in asst["sends"][mv] if sc["shop_key"] in x.get("for_shops", [sc["shop_key"]])]
            l = pick(ls, "a:" + mv)
        parts.append(fill(l["text"], sc, line_values(l, sc)))
    return " ".join(parts)


def resolve_draft(key, sc):
    job = sc["jobinfo"]
    if key in ("symptom.advise", "symptom.photo", "price.depends") and not sc["stepinfo"]:
        return "generic.ask_car"
    if key != "{price_draft}":
        return key
    pk = job["price_kind"]
    if pk in ("menu", "class"):
        return "price.quote_class" if sc.get("page_price_class") and sc["carinfo"]["vclass"] != "car" else "price.quote_menu"
    if pk == "list":
        return "price.quote_list"
    if pk == "range":
        return "price.range"
    return "price.depends" if sc["stepinfo"] else "generic.ask_car"


def draft_text(key, sc, state):
    key = resolve_draft(key, sc)
    r, _, m = key.partition(".")
    l = pick(asst["drafts"][r][m], "d:" + key)
    t = fill(l["text"], sc, line_values(l, sc))
    if state.get("shop_spoke"):
        t = strip_greeting(t)
    if state.get("car_named") and sc["car_year"] in " ".join(state.get("said", ())):
        t = re.sub(r"\s*[^.!?]*(год выпуска|[Кк]акого года)[^.!?]*\?$", "", t)  # the year is already in the chat
    state["draft_defers"] = bool(l.get("defers"))
    return key, t


def adv_text(slot, keys, sc, state):
    a = advisors[slot]
    keys = [keys] if isinstance(keys, str) else keys
    parts = []
    for k in keys:
        if k == "pickup":
            ws = a["pickup"]
        elif k.startswith("moves."):
            ws = a["moves"].get(k[6:])
        else:
            r, _, m = k.partition(".")
            ws = a["replies"][r][m]
        if not ws:
            continue
        if parts:  # not the first part of the message: prefer a wording that does not open with a name or a greeting
            ws = [w for w in ws if not re.match(r"(\{name_addr\}|\{Hello\}|\{hello_lc\}|Да, |Здравствуйте|Конечно)", w)] or ws
        parts.append(fill(pick(ws, "s%d:%s" % (slot, k)), sc))
    t = join_parts(parts)
    return strip_greeting(t) if state.get("staff_spoke") else t


def staff_name(slot):
    return "%s (%d)" % (FIRST[slot], slot)


OUTCOME_RU = {"sent_as_is": "отправлен как есть", "sent_edited": "отправлен с правкой", "discarded": "убран", "replaced_unseen": "заменён новым, его никто не видел"}


def say_staff(slot, text, out, public, state, files=()):
    fl = ""
    for f in files:
        fl += " [%s: %s]" % ("файл" if f == "estimate-pdf" else "фото", f)
    out.append("- **%s:** %s%s" % (staff_name(slot), text.replace("\n", "<br>"), fl))
    public.append(("staff", text))
    state["staff_spoke"] = state["shop_spoke"] = True
    state["last"] = "staff"
    state["last_shop_text"] = text
    state["shop_silent"] = False
    state["offered"] = state.get("offered", "") + " " + text


def staff_turn(b, sc, state, out, public, forced_draft=None):
    """one staff beat: the draft a customer turn raised, its outcome, what was sent"""
    slot = sc["slot"]
    a = advisors[slot]
    reply = b.get("reply")
    files = []
    for f in ([] if a["sheet"]["curt"] else b.get("files", [])):  # the curt desks attach nothing
        f = sc["finding_photo"] if f == "{finding_photo}" else f
        files.append("estimate-photo" if sc["channel"] == "avito" and f == "estimate-pdf" else f)
    sent = None
    dkey = forced_draft or b.get("draft")
    if dkey:
        key, dtext = dkey if isinstance(dkey, tuple) else draft_text(dkey, sc, state)
        d = a["sheet"]["draft_outcomes"]
        outcome = b.get("draft_outcome") or rng.choices(["sent_as_is", "sent_edited", "discarded"], weights=[d["sent_as_is"], d["sent_edited"], d["discarded"]])[0]
        if outcome == "sent_edited":
            rk = [reply] if isinstance(reply, str) else (reply or [])
            ed = [e for e in a["edits"] if e["draft_key"] == key and e["outcome"] == "sent_edited" and (not e.get("fits") or e["fits"] in rk or not rk)]
            if ed:
                sent = fill(ed[0]["sent"], sc)
                sent = strip_greeting(sent) if state.get("staff_spoke") else sent
            else:
                sent = adv_text(slot, reply, sc, state) if reply else dtext
        elif outcome == "sent_as_is":
            sent = dtext
        else:
            sent = adv_text(slot, reply, sc, state) if reply else None
        if sent == dtext:
            outcome = "sent_as_is"
        state["drafts"][outcome] += 1
        out.append("- *черновик, %s: %s*" % (OUTCOME_RU[outcome], dtext))
    elif reply:
        sent = adv_text(slot, reply, sc, state)
    if sent:
        say_staff(slot, sent, out, public, state, files if not (dkey and outcome == "sent_as_is" and state.get("draft_defers") and reply) else ())
        if dkey and outcome == "sent_as_is" and state.get("draft_defers") and reply:
            # the draft only promised an answer: a little later the person gives it
            say_staff(slot, adv_text(slot, [k for k in ([reply] if isinstance(reply, str) else reply) if k not in ("pickup", "moves.sorry")], sc, state), out, public, state, files)
    return sent


def emit_customer(msgs, out, public, state):
    for text, att in msgs:
        shown = text
        if att:
            shown = (text + " " if text else "") + "[%s]" % att
        out.append("- **клиент:** %s" % shown)
        if text:
            public.append(("customer", text))
    if msgs:
        state["last"] = "customer"


def say_assistant(text, out, public, state):
    out.append("- **ассистент:** %s" % text)
    public.append(("assistant", text))
    state["last"] = "assistant"
    state["shop_spoke"] = True
    state["last_shop_text"] = text


def lower_style(t):
    """a neutral line as slots 5, 22 and 23 would type it"""
    t = re.sub(r"(?:^|(?<=[.!?] ))([А-ЯЁ])(?=[а-яё ])", lambda m: m.group(1).lower(), t)
    return re.sub(r"(\d) ₽", r"\1", t).rstrip(".")


def own_question(slot, q, sc):
    """an advisor who put the draft aside asks in their own words"""
    a = advisors[slot]
    if a["sheet"]["curt"]:
        return fill(pick(a["moves"]["ask_lead"], "s%d:ask_lead" % slot), sc)
    leads = [l for l in a["moves"]["ask_lead"] if not any(re.search(root, l, re.I) and re.search(root, q[:30], re.I) for root in ("уточн", "подскаж"))]
    lead = fill(pick(leads or a["moves"]["ask_lead"], "s%d:ask_lead" % slot), sc)
    qq = fill(q, sc)
    if slot in LOWER_TYPISTS:
        qq = lower_style(qq)
    return lead + " " + qq


REPLY_ONLY = {"generic.ok", "generic.close", "generic.pick_time", "generic.close_coming", "generic.yes", "generic.no", "generic.thanks"}


def build(n, reason, channel, sk, loop=None, ending=None):
    web = channel == "web"
    forced_g = None
    stub_beats = [b for b in sk["beats"] if b["who"] == "customer" and b.get("stub")]
    if stub_beats:
        opts = [o for o in cust["reasons"][reason]["open"] if o.get("voice_stub")]
        gs = {STUBS[o["voice_stub"]].get("g") or o.get("g") for o in opts} - {None}
        forced_g = rng.choice(sorted(gs)) if gs else None
    sc = scenario(reason, channel, sk, loop, forced_g)
    slot = sc["slot"]
    state = {"drafts": Counter()}
    out, public = [], []
    beats = [b for b in sk["beats"] if b["who"] != "unclear"]
    handed = False
    ended = None
    i = 0
    # ---- an unclear customer is laid over the opening
    if loop:
        opens = [o for o in loop["open"] if "{advisor_addr}" not in o or channel in ("telegram", "vk")]
        otext = fill(pick(opens, "u:open"), sc)
        state["customer_words"] = otext
        emit_customer([(otext, None)], out, public, state)
        i = 1  # the skeleton's opening is replaced
        l1, l2 = loop["ask"]["level_1"][0], loop["ask"]["level_2"][0]
        if web:
            say_assistant(assistant_text(["greet"], sc, state) + " " + fill(l1, sc), out, public, state)
            if ending == "after_one":
                emit_customer([(fill(pick(loop["second_clear"], "u:clear"), sc), None)], out, public, state)
                state["asked_times"] = "один раз"
            else:
                second = fill(pick(loop["second_unclear"], "u:unclear"), sc)
                emit_customer([(second, None)], out, public, state)
                state["second_words"] = second
                say_assistant(fill(l2, sc), out, public, state)
                state["asked_times"] = "дважды"
                if ending == "after_two":
                    emit_customer([(fill(pick(loop["third"], "u:third"), sc), None)], out, public, state)
                else:
                    if loop["never_customer"] and rng.random() < 0.6:
                        emit_customer([(loop["never_customer"], None)], out, public, state)
                        say_assistant(loop["endings"]["never"], out, public, state)
                    ended = "остался неясным: клиент перестал отвечать, номера не оставил; чат остаётся у ассистента, закрыт через 7 дней тишины"
            if not ended:
                state["ack"] = loop["endings"]["after_one"]
        else:
            a = advisors[slot]
            asks = rng.random() * 100 < a["sheet"]["ask_chance"]
            d1 = ("unclear.level_1", fill(l1, sc))
            if asks:
                before = len(public)
                staff_turn({}, sc, state, out, public, forced_draft=d1)
                if len(public) == before:  # the row put the draft aside: the advisor asks in their own words
                    say_staff(slot, own_question(slot, l1, sc), out, public, state)
                state["asked_times"] = "один раз"
                if ending == "after_one":
                    emit_customer([(fill(pick(loop["second_clear"], "u:clear"), sc), None)], out, public, state)
                else:
                    emit_customer([(fill(pick(loop["second_unclear"], "u:unclear"), sc), None)], out, public, state)
            else:
                g0 = fill(loop["ask"]["level_0"][1 if a["sheet"]["curt"] else 0], sc)
                if a["sheet"].get("no_price"):
                    g0 = fill(pick(a["moves"]["guess_tail"], "s%d:guess_tail" % slot), sc)
                if slot in LOWER_TYPISTS and not a["sheet"]["curt"]:
                    g0 = lower_style(g0)
                out.append("- *черновик, %s: %s*" % (OUTCOME_RU["discarded"], d1[1]))
                state["drafts"]["discarded"] += 1
                say_staff(slot, g0, out, public, state)
                emit_customer([(fill(pick(loop["second_to_guess"], "u:guess"), sc), None)], out, public, state)
                state["asked_times"] = "ни разу"
            if not (asks and ending == "after_one"):
                # the second question, or the first one after a wrong guess
                d2 = ("unclear.level_2", fill(l2, sc))
                before = len(public)
                staff_turn({}, sc, state, out, public, forced_draft=d2)
                if len(public) == before:
                    if a["sheet"]["curt"]:
                        say_staff(slot, fill(pick(a["moves"]["guess_tail"], "s%d:guess_tail" % slot), sc), out, public, state)
                    else:
                        say_staff(slot, own_question(slot, l2, sc), out, public, state)
                if ending == "never":
                    if loop["never_customer"] and rng.random() < 0.6:
                        emit_customer([(loop["never_customer"], None)], out, public, state)
                    ended = "остался неясным: клиент перестал отвечать; закрыт через 7 дней тишины"
                else:
                    emit_customer([(fill(pick(loop["third"] if asks else loop["second_clear"], "u:third"), sc), None)], out, public, state)
            state["pending_draft"] = True
    # ---- the skeleton
    while i < len(beats) and not ended:
        b = beats[i]
        i += 1
        w = b["who"]
        if "p" in b and rng.random() > b["p"] and w != "end":
            continue
        if b.get("if") == "nocar" and state.get("car_named"):
            continue
        if w == "customer":
            uses = b.get("use", [])
            uses = [uses] if isinstance(uses, str) else uses
            if state.get("shop_silent") and uses and all(u in REPLY_ONLY for u in uses):
                continue  # the shop said nothing since the customer's last line: nothing to answer
            if uses == ["price.want_book"] and (sc["time_a"] in state.get("offered", "") or sc["time_b"] in state.get("offered", "")):
                if i < len(beats) and beats[i]["who"] == "staff":
                    i += 1  # the advisor has already offered times: no question, no second offer
                continue
            drafts_mode = not web or handed
            twice = state.get("last") == "customer" and drafts_mode and state.get("pending_draft")
            msgs = customer_msgs(b, reason, channel, sc, state)
            if not msgs:
                continue
            emit_customer(msgs, out, public, state)
            if "generic.give_shop" in uses:
                state["shop_given"] = True
            if twice:
                nxt = next((x for x in beats[i:] if x["who"] == "staff" and x.get("draft")), None)
                if nxt:
                    out.append("- *черновик к предыдущему сообщению, %s: %s*" % (OUTCOME_RU["replaced_unseen"], draft_text(nxt["draft"], sc, state)[1]))
                    state["drafts"]["replaced_unseen"] += 1
            if drafts_mode:
                state["pending_draft"] = True
        elif w == "assistant":
            if state.get("last") == "assistant":
                continue
            text = assistant_text(b["use"], sc, state)
            if state.get("ack"):
                text = state.pop("ack") + " " + text
            if text.strip():
                say_assistant(text, out, public, state)
        elif w == "handoff":
            key = "unclear" if loop else b["note"]
            note = fill(pick(asst["handoff_notes"][key], "n:" + key), sc,
                        {"customer_words": state.get("customer_words", ""), "clear_words": loop["reads"] if loop else "",
                         "asked_times": state.get("asked_times", "один раз"), "second_words": state.get("second_words", "")})
            out.append("- *передача заявки (%s), заметка ассистента: %s*" % (b["kind"], note))
            out.append("- (ярлык: handoff; карточка на доске: %s)" % ("запись, обычный приоритет" if b["kind"] == "scheduling" else "обращение, высокий приоритет"))
            handed = True
            state["pending_draft"] = False
        elif w == "staff":
            bb = dict(b)
            if bb.get("reroll"):
                d1, d2 = [DAYS[k] for k in rng.sample(["mon", "tue", "wed", "thu", "fri", "sat", "sun"], 2)]
                sc.update(day_a=d1["nom"], day_a_on=d1["on"], day_a_for=d1["for"], day_b=d2["nom"], day_b_on=d2["on"], day_b_for=d2["for"], _a=d1, _b=d2,
                          time_a=rng.choice(["9:00", "10:30", "11:30"]), time_b=rng.choice(["16:00", "17:30", "18:30"]))
            if bb.get("draft") and state.get("last") != "customer":
                continue  # an answer with nothing to answer
            if not state.get("pending_draft"):
                bb.pop("draft", None)
            if loop and bb.get("draft") == "booking.day_ok":
                bb["draft"] = "booking.ask_day"  # the unclear opening named no day
            before = len(public)
            staff_turn(bb, sc, state, out, public)
            if len(public) == before:
                state["shop_silent"] = True
            state["pending_draft"] = False
        elif w == "extra":
            if state.get("last") == "customer" or not (not web or handed):
                continue
            lst = state.get("last_shop_text", "")
            sk_drafts = {x.get("draft") for x in beats if x["who"] == "staff"}
            keys = [k for k in b["keys"] if k not in state.setdefault("exch", set()) and EXCH[k]["draft"] not in sk_drafts
                    and ("kinds" not in EXCH[k] or sc["jobinfo"]["price_kind"] in EXCH[k]["kinds"])
                    and ("jobs" not in EXCH[k] or sc["jobinfo"]["key"] in EXCH[k]["jobs"])
                    and not (k == "total" and any(sc[x] in lst for x in ("job_total", "job_total_bare", "job_total_num")))
                    and not (k == "how_long" and sc["duration"] in " ".join(t for _, t in public))
                    and not (k in ("vat", "own_parts") and not any(sc.get(x, "\0") in " ".join(t for _, t in public) for x in ("job_price", "job_price_bare", "job_price_num", "job_total", "job_total_bare", "job_total_num", "page_price")))
                    and not (k == "vat" and ("НДС" in state.get("last_shop_text", "") or "ндс" in state.get("last_shop_text", "")))
                    and not (k == "address" and sc["shop_address"] in " ".join(t for _, t in public))]
            if not keys:
                continue
            k = rng.choice(keys)
            state["exch"].add(k)
            msgs = customer_msgs({"who": "customer", "use": EXCH[k]["customer"]}, reason, channel, sc, state)
            if msgs:
                emit_customer(msgs, out, public, state)
                state["pending_draft"] = True
                staff_turn({"draft": EXCH[k]["draft"], "reply": EXCH[k]["reply"]}, sc, state, out, public)
                state["pending_draft"] = False
        elif w == "note":
            if not state.get("staff_spoke"):
                continue
            cands = [x for x in lan["notes"] if x["key"] == b["use"] and x["slot"] == slot]
            if cands and not (b["use"] == "to_manager" and slot == 22):
                out.append("- *заметка, %s: %s*" % (staff_name(slot), fill(pick([c["text"] for c in cands], "note"), sc, {"clear_words": loop["reads"] if loop else ""})))
                if b["use"] in ("ask_colleague", "next_shift"):
                    acks = [x for x in lan["acks"] if SHOP_OF[x["slot"]] == sc["shop_key"] and x["slot"] != slot and x["slot"] != 22]
                    if acks and rng.random() < 0.6:
                        k = rng.choice(acks)
                        out.append("- *заметка, %s: %s*" % (staff_name(k["slot"]), k["text"]))
                elif b["use"] == "to_manager" and sc["shop_key"] == "west" and rng.random() < 0.6:
                    out.append("- *заметка, %s: принял*" % staff_name(22))
        elif w == "activity":
            if b["what"] == "label_added":
                if state.get("staff_spoke") and rng.random() * 100 < advisors[slot]["sheet"]["label_share"]:
                    tyres = sc["jobinfo"]["key"] in ("seasonal_tyres", "wheel_swap", "tyre_storage", "puncture", "balance", "alignment")
                    label = "шины" if tyres and b["label"] in ("цена", "запись") else b["label"]
                    out.append("- (ярлык: %s, поставил слот %d)" % (label, slot))
            elif b["what"] == "priority" and state.get("staff_spoke"):
                out.append("- (приоритет: %s, поставил слот %d)" % ({"high": "высокий", "urgent": "срочный", "low": "низкий"}[b["level"]], slot))
        elif w == "end":
            if b["how"] == "person" and state.get("staff_spoke") and rng.random() * 100 < advisors[slot]["sheet"]["resolves"]:
                ended = "закрыл слот %d" % slot
            else:
                ended = "закрыт через 7 дней тишины"
    person = any(k == "staff" for k, _ in public)
    head = "### %d. %s · %s · `%s` · %s" % (n, reason, CH_RU[channel], sk["id"], sk["ends"])
    if person or not web:
        head += " · слот %d %s (%s)" % (slot, advisors[slot]["name"], sc["shop"])
    if sc["after_hours"]:
        head += " · вне часов работы"
    if loop:
        head += " · непонятный клиент: %s, %s" % (loop["id"], {"after_one": "ясно после одного вопроса", "after_two": "ясно после двух", "never": "так и не прояснилось"}[ending])
    meta = "%s, %s · %s" % (sc["name_addr"], {"m": "м", "f": "ж"}[sc["g"]], sc["car"])
    if reason not in ("hours", "spam", "moving", "fleet") or loop:
        meta += " · " + sc["job"]
    return {"head": head, "meta": meta, "lines": out + ["- — " + (ended or "закрыт через 7 дней тишины")], "public": public,
            "drafts": state["drafts"], "reason": reason, "channel": channel, "loop": loop, "ending": ending, "slot": slot, "id": sk["id"], "n": n}


# ---- the plan: every reason on every channel it occurs on, then by the design's shares
combos = [(r, ch) for r, spec in reasons.items() for ch in CHANNELS if spec["shares"][ch] > 0]
plan = list(combos)
SESSIONS = {"web": 5, "telegram": 11, "vk": 3, "avito": 5}
weights = [SESSIONS[ch] * reasons[r]["shares"][ch] for r, ch in combos]
while len(plan) < 60:
    plan.append(rng.choices(combos, weights=weights)[0])
rng.shuffle(plan)
# nine conversations carry a loop: three of each ending
loop_plan = {}
endings = ["after_one"] * 3 + ["after_two"] * 3 + ["never"] * 3
loops = list(unclear)
rng.shuffle(loops)
used_idx = set()
for ending in endings:
    for lp in loops:
        if lp["id"] in [v[0]["id"] for v in loop_plan.values()]:
            continue
        hit = None
        for idx, (r, ch) in enumerate(plan):
            if idx in used_idx or r not in lp["reasons"]:
                continue
            sks = [s for s in reasons[r]["skeletons"][ch] if any(b["who"] == "unclear" and lp["kind"] in b["kinds"] for b in s["beats"])
                   and (lp["job"] is None or fits_when(s, JOBS[lp["job"]], "car", None))]
            if sks:
                hit = (idx, sks)
                break
        if hit:
            used_idx.add(hit[0])
            loop_plan[hit[0]] = (lp, ending, hit[1])
            break
sk_use = Counter()
convs = []
for idx, (r, ch) in enumerate(plan):
    if idx in loop_plan:
        lp, ending, sks = loop_plan[idx]
        sk = min(sks, key=lambda s: (sk_use[s["id"]], rng.random()))
        sk_use[sk["id"]] += 1
        convs.append(build(idx + 1, r, ch, sk, lp, ending))
    else:
        sks = reasons[r]["skeletons"][ch]
        sk = min(sks, key=lambda s: (sk_use[s["id"]], rng.random()))
        sk_use[sk["id"]] += 1
        convs.append(build(idx + 1, r, ch, sk))

md = ["# Собранная выборка: 60 фоновых переписок (русская конфигурация)", "",
      "Собрано скриптом `checks/check_conv_bank_ru.py` из банка в этой папке, зерно случайности %d. Слоты заполнены пробными значениями, которые берёт сам скрипт: имена выдуманы, телефоны из кодов 907 и 935, машины из `parc.json`, цены из открытого прайс-листа для легкового автомобиля (поэтому у кроссоверов и фургонов суммы здесь занижены), адреса и часы со страницы «Адреса и часы работы». В настоящей сборке их даёт сценарий генератора. Курсивом идут черновики, заметки и передача заявки; клиент видит только обычные строки. Что читать в первую очередь: `_README.md`." % RANDOM_SEED, ""]
for c in convs:
    md += [c["head"], "", "*" + c["meta"] + "*", ""] + c["lines"] + [""]
open(OUT_MD, "w", encoding="utf-8").write("\n".join(md))

ok("60 conversations assembled with seed %d, written to conversations/bank-ru/assembled-sample.md" % RANDOM_SEED, len(convs) == 60)
seen = {(c["reason"], c["channel"]) for c in convs}
ok("every reason on every channel it occurs on is in the sample (%d of %d)" % (len(seen), len(combos)), seen == set(combos))
ok("all four channels: " + ", ".join("%s %d" % (CH_RU[ch], sum(1 for c in convs if c["channel"] == ch)) for ch in CHANNELS),
   all(any(c["channel"] == ch for c in convs) for ch in CHANNELS))
ok("all nine advisors speak in the sample: " + ", ".join("%d×%d" % (s, sum(1 for c in convs if c["slot"] == s and any(k == "staff" for k, _ in c["public"]))) for s in ADV_SLOTS),
   all(any(c["slot"] == s and any(k == "staff" for k, _ in c["public"]) for c in convs) for s in ADV_SLOTS))
le = Counter(c["ending"] for c in convs if c["loop"])
ok("unclear loops in the sample, each of the three endings: %s" % dict(le), all(le[e] >= 1 for e in ("after_one", "after_two", "never")))
left = [(c["n"], l[:80]) for c in convs for l in c["lines"] if SLOT_RE.search(l) or "[[" in l]
ok("no slot left unfilled in the sample", not left, left[:5])
empty = [c["n"] for c in convs if not c["public"]]
ok("no empty conversation", not empty, empty)
pub = [norm(t) for c in convs for k, t in c["public"]]
cnt = Counter(pub)
dups = len(pub) - len(cnt)
share = 100.0 * dups / len(pub)
sharing = 100.0 * sum(v for v in cnt.values() if v > 1) / len(pub)
ok("exact duplicate messages: %d of %d = %.2f%% (under 3 %%); messages sharing text with another: %.2f%%" % (dups, len(pub), share, sharing), share < 3.0,
   cnt.most_common(8))
say("INFO most repeated: " + "; ".join("«%s» ×%d" % (t, v) for t, v in cnt.most_common(6) if v > 1))
dr = Counter()
for c in convs:
    dr.update(c["drafts"])
say("INFO drafts in the sample: %s" % dict(dr))
lens = sorted(len(c["public"]) for c in convs)
alone = sorted(len(c["public"]) for c in convs if c["channel"] == "web" and not any(k == "staff" for k, _ in c["public"]))
handled = sorted(len(c["public"]) for c in convs if any(k == "staff" for k, _ in c["public"]))
say("INFO public lines a conversation, median: assistant alone %s, person-handled %s (design: 5 and 11, within 2)" % (
    alone[len(alone) // 2] if alone else "-", handled[len(handled) // 2] if handled else "-"))

# a second run with the design's own mix (not written anywhere): what lengths the bank gives when reasons and
# channels come in the shares of section 4
sim = []
for k in range(600):
    r, ch = rng.choices(combos, weights=weights)[0]
    sk = rng.choice(reasons[r]["skeletons"][ch])
    sim.append(build(0, r, ch, sk))
s_alone = sorted(len(c["public"]) for c in sim if c["channel"] == "web" and not any(k == "staff" for k, _ in c["public"]))
s_hand = sorted(len(c["public"]) for c in sim if any(k == "staff" for k, _ in c["public"]))
say("INFO 600 more conversations in the design's mix of reasons and channels (not written): public lines, median: assistant alone %d, "
    "person-handled %d; person-handled quartiles %d to %d (design: 5 and 11, within 2)" % (
        s_alone[len(s_alone) // 2], s_hand[len(s_hand) // 2], s_hand[len(s_hand) // 4], s_hand[3 * len(s_hand) // 4]))
web_sim = [c for c in sim if c["channel"] == "web"]
say("INFO in that run the web chat ends with the assistant alone in %d %% of sessions (design: 45 %%; a skeleton is drawn evenly here, the generator weighs them)" % (
    round(100.0 * sum(1 for c in web_sim if not any(k == "staff" for k, _ in c["public"])) / len(web_sim))))
left = [(c["id"], l[:80]) for c in sim for l in c["lines"] if SLOT_RE.search(l) or "[[" in l]
ok("no slot left unfilled in those 600 either", not left, left[:5])

# ------------------------------------------------------------------ report
say("\nfiles")
for f in sorted(glob.glob(os.path.join(BANK, "*.json")) + glob.glob(os.path.join(BANK, "advisors", "*.json"))):
    say("  %s  %s bytes" % (os.path.relpath(f, BANK), "{:,}".format(os.path.getsize(f))))
say("")
say("all checks pass" if not failures else "FAILED: %d check(s): %s" % (len(failures), "; ".join(failures)))
open(OUT_TXT, "w", encoding="utf-8").write("\n".join(lines_out) + "\n")
print("\n".join(lines_out))
sys.exit(1 if failures else 0)
