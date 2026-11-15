#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checks the hand-written story conversations of one language against conversations/DESIGN.md, the seed files and the ledger.

    python3 checks/check_conversations.py en > checks/conversations_check_en.txt
    python3 checks/check_conversations.py ru > checks/conversations_check_ru.txt

The argument is the language folder under conversations/ (conversations/en, conversations/ru). What depends on the
language is in LANG below. Nothing here reads the builder under conversations/build: the files are checked as they stand.

Per file: the format; the days against their anchors of rule R6 and the weekday words against the days; the order and
the times of the lines; who may speak in which state of the chat (the assistant sends only in a web chat that is its
own, drafts everywhere else); each draft's outcome against what was sent; each wait in working minutes, and each
person's waits against that person's ledger row; names, phones, units, plates, prices and channel identities against
the seed files and the ledger. Over the set: the 27 conversations of DESIGN.md section 6, the open set at T that the
ledger names (conv.open_at_t), the live-demo rule (conv.live_demo), the hand-written rule-R13 items, the pictures of
contacts, and the copies under conversations/samples.

Exit code 1 when a check fails. Not product code.
"""
import datetime as dt
import glob
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
CONV = os.path.join(SEED, "conversations")
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ORDER = ["low", "normal", "high", "urgent"]
KINDS = ("message", "note", "draft", "handoff", "activity", "outside")
REASONS_EXTRA = ()
STORIES = {1: "S7", 2: "S7", 3: "S7", 4: "S1", 5: "S1", 6: "S6", 7: "S13", 8: "S13"}
STORIES.update({n: "people" for n in range(9, 25)})
STORIES.update({n: "R13" for n in range(25, 28)})
PEOPLE_SLOTS = (5, 6, 7, 16, 17, 22, 23, 24)
EN_CLOSED = {dt.date(2026, 5, 25), dt.date(2026, 7, 3), dt.date(2026, 9, 7), dt.date(2026, 11, 26)}  # the closed dates of the nominal year
SAMPLES = {1: "{l}-1-web-after-hours.json", 4: "{l}-2-fleet-quote-waited.json", 6: "{l}-3-west-nine-days.json",
           7: "{l}-4a-stocktake-web.json", 8: "{l}-4b-stocktake-messenger.json"}

# ---------------------------------------------------------------------------------------------------- per language
LANG = {
    "en": dict(
        channels=("chat", "telegram"), channel_of={5: "telegram", 8: "telegram", 26: "telegram"},
        visitor="Website visitor", said_handoff="as soon as possible",
        phone=re.compile(r"\(?\b(\d{3})\)?[ -]?555[ -]?(\d{4})\b"),
        day_words={"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
                   "mon": 0, "tues": 1, "wed": 2, "thurs": 3},
        relative={"tomorrow": 1, "today": 0, "tonight": 0, "yesterday": -1},
        word=lambda w: r"(?<![A-Za-z])%s(?![A-Za-z])" % w,
        addresses={"East Main": "2106", "Bonny Oaks": "6340", "Charlotte Pike": "6399"},
        unit=re.compile(r"\b(?:M-\d{3}|SC-\d{1,2})\b"), plate=re.compile(r"\b[A-Z]{3}-\d{4}\b"),
        money=re.compile(r"\$\s?\d[\d,]*(?:\.\d\d)?"),
        strip=[r"\b\d{1,2}:\d{2}\b", r"\b(?:19|20)\d{2}\b", r"\bPO \w+\b", r"\b\d{1,2}(?:st|nd|rd|th)\b", r"\b(?:2106|6340|6399)\b", r"\b112\b", r"\b\d{2,3}K\b"],
        person_words=("man", "woman", "person", "people", "girl", "boy", "child", "selfie", "face", "portrait", "driver at"),
        old_names=("Jersey Pike",),
        cyrillic=False,
    ),
    "ru": dict(
        channels=("chat", "telegram", "vk", "avito"), channel_of={5: "telegram", 8: "vk", 26: "telegram", 27: "avito"},
        visitor="Посетитель сайта", said_handoff="в ближайшее время",
        phone=re.compile(r"(?:\+7|8)[ (]*(\d{3,4})[ )]*(\d[\d -]{5,9}\d)"),
        day_words={"понедельник": 0, "вторник": 1, "сред": 2, "четверг": 3, "пятниц": 4, "суббот": 5, "воскресень": 6},
        relative={"завтра": 1, "сегодня": 0, "вчера": -1},
        word=lambda w: (r"(?<![А-Яа-яЁё])%s[а-яё]{0,3}(?![А-Яа-яЁё])" % w) if w not in ("завтра", "сегодня", "вчера") else (r"(?<![А-Яа-яЁё])%s(?![А-Яа-яЁё])" % w),
        addresses={"Московское шоссе": "40", "Инженерн": "30", "Техническая": "30"},
        unit=re.compile(r"\bТ-\d{2}\b"), plate=re.compile(r"\b[АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3}\b"),
        money=re.compile(r"\d[\d  ]*(?:,\d\d)?\s?(?:₽|руб|р\b)"),
        strip=[r"\b\d{1,2}:\d{2}\b", r"\b(?:19|20)\d{2}\b", r"\b\d{1,2}[ -]?(?:го|е|й)\b", r"\b\d{1,2} (?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b",
               r"шоссе, 40", r"проезд[а-я]*, 30", r"Техническая, 30", r"\b5W-40\b", r"R134a", r"\b[rR]1[3-9]\b", r"\b96/07\b", r"\b\d{2} 00\b"],
        person_words=("человек", "мужчина", "женщина", "девушка", "парень", "ребёнок", "селфи", "лицо", "портрет"),
        old_names=(),
        cyrillic=True,
    ),
}

OUT, FAILS = [], []


def say(line=""):
    OUT.append(line)


def ok(what, good, detail=""):
    say(("  ok    " if good else "  FAIL  ") + what + ("" if good or not detail else "  -> " + str(detail)[:900]))
    if not good:
        FAILS.append(what)
    return good


def load(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------------------------------- the calendar
def closed(cfg, d):
    return d in EN_CLOSED if cfg == "en" else (d.month, d.day) in ((1, 1), (1, 2))


def full_open(cfg, d):
    return not closed(cfg, d) and (cfg == "ru" or d.weekday() < 5)


def hours(cfg, site, d, row):
    if closed(cfg, d):
        return None
    lo, hi = [int(x[:2]) * 60 + int(x[3:]) for x in row]
    if cfg == "ru":
        return lo, hi
    if d.weekday() < 5:
        return lo, hi
    if d.weekday() == 5 and site == "main":
        return 8 * 60, 13 * 60
    return None


class Cal:
    def __init__(self, cfg, ledger):
        self.cfg = cfg
        self.row = ledger["site.hours.weekday"][cfg]
        pattern = ledger["roster.advisor_pattern"]["ru"]
        self.phase = {}
        for letter, mods in (("A", (2, 3)), ("B", (0, 1))):
            assert "Phase %s works d mod 4 in {%d, %d}" % (letter, mods[0], mods[1]) in pattern.replace("phase A", "Phase A"), "the rota's wording changed in the ledger"
        for slot, letter in re.findall(r"(\d+)(?: and \d+)? (?:are |)phase ([AB])", pattern):
            self.phase[int(slot)] = letter
        for a, b, letter in re.findall(r"(\d+) and (\d+) (?:are )?phase ([AB])", pattern):
            self.phase[int(a)] = self.phase[int(b)] = letter
        self.managers = [int(x) for x in re.findall(r"\d+", ledger["roster.manager_pattern"]["ru"])]
        t = dt.datetime.strptime(ledger["_nominal"], "%Y-%m-%d %H:%M")
        self.t = t

    def hours(self, site, d):
        return hours(self.cfg, site, d, self.row)

    def works(self, slot, d):
        if self.cfg == "en":
            return full_open("en", d)
        if closed("ru", d):
            return False
        if slot in self.managers:
            return d.weekday() < 5
        n = (d - self.t.date()).days % 4
        return n in ((2, 3) if self.phase[slot] == "A" else (0, 1))

    def t_at(self, site):
        return self.t - dt.timedelta(hours=1) if site == "west" else self.t

    def is_open(self, site, a):
        h = self.hours(site, a.date())
        m = a.hour * 60 + a.minute + a.second / 60
        return bool(h) and h[0] <= m < h[1]

    def working(self, site, a, b):
        total, d = 0.0, a.date()
        while d <= b.date():
            h = self.hours(site, d)
            if h:
                lo = max(a, dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[0]))
                hi = min(b, dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[1]))
                if hi > lo:
                    total += (hi - lo).total_seconds() / 60
            d += dt.timedelta(days=1)
        return total

    def resolve(self, rule):
        t, kind = self.t.date(), rule["kind"]
        if kind == "T":
            d = t
        elif kind == "calendar":
            d = t + dt.timedelta(days=rule["days"])
        elif kind == "weekday_of_week":
            d = t - dt.timedelta(days=t.weekday()) - dt.timedelta(weeks=rule["week"]) + dt.timedelta(days=WEEKDAYS.index(rule["weekday"]))
            while closed(self.cfg, d):
                d += dt.timedelta(days=1)
            if rule.get("on_or_after_for_slot"):
                while not self.works(rule["on_or_after_for_slot"], d):
                    d += dt.timedelta(days=1)
        elif kind in ("slot_working_day", "open_day"):
            d, n, step = t, abs(rule["n"]), (1 if rule["n"] > 0 else -1)
            while n:
                d += dt.timedelta(days=step)
                if (self.works(rule["slot"], d) if kind == "slot_working_day" else full_open(self.cfg, d)):
                    n -= 1
        else:
            raise ValueError(kind)
        return d + dt.timedelta(days=rule.get("plus_days", 0))


def offset(label):
    return 0 if label == "T" else int(label[1:-1])


def label_of(n):
    return "T" if n == 0 else "T%+dd" % n


# ---------------------------------------------------------------------------------------------------- prices
class Prices:
    def __init__(self, cfg):
        self.cfg = cfg
        cat = load("catalogue.json")
        self.jobs = {j["key"]: j[cfg] for j in cat["jobs"]}
        self.conf = cat["configurations"][cfg]

    def parts(self, job, cls, tier="standard", klass="list"):
        j = self.jobs[job]
        # the shop system's arithmetic (seeder/erp/orders.py: price): hourly labour is the sold hours to the hundredth x
        # the hour, to the cent; a part line is its quantity x the unit price (class multiplier and company terms on the
        # unit) to the cent
        hm = (j.get("hours_by_class") or {}).get(cls, 1) if j.get("hours_by_class") else 1
        if j.get("labour_pricing") == "hourly":
            lab = round(round(j["hours"] * hm + 1e-9, 2) * self.conf["labour_rate"]["company_account" if klass == "company" else "standard"]["after_rise"] + 1e-9, 2)
        else:
            lab = (j["labour_price_company"] if klass == "company" else j["labour_price"])["after_rise"] * hm
        pm = self.conf["parts_class_multiplier"][cls] if j.get("parts_scale_with_class") else 1
        parts = 0.0
        for p in j["parts"]:
            opts = {o["tier"]: o for o in p["options"] if not o.get("story")}
            o = opts.get(tier) or opts.get("standard") or list(opts.values())[0]
            unit = round(o["list_price"] * pm + 1e-9, 2)
            parts += round(p["qty"] * (round(unit * 0.9 + 1e-9, 2) if klass == "company" else unit) + 1e-9, 2)
        other = sum(f.get("price", 0) for f in j.get("fees", []))
        other += (j.get("sublet") or {}).get("price", 0) if j.get("usually_sublet") else 0
        if klass == "company":
            other *= 0.9
        other += parts
        return lab, other, bool(j.get("shop_supplies"))

    def amount(self, src, ledger, declared):
        rate, cap, tax = self.conf["shop_supplies"]["rate_of_hourly_labour"], self.conf["shop_supplies"]["cap_per_order"], self.conf["tax"]["rate"]
        tax = (self.conf["tax"].get("rate_by_shop") or {}).get(src.get("tax_shop"), tax)  # the shop named on the price row; the home rate otherwise
        if "ledger" in src:
            key, _, field = src["ledger"].rpartition(".")
            return ledger[key][self.cfg][field]
        if "sum_of_said" in src:
            return round(sum(declared[s] for s in src["sum_of_said"]), 2)
        if "shop_supplies_of" in src:
            lab, _, _ = self.parts(src["shop_supplies_of"], src["class"])
            return round(lab * rate + 1e-9, 2)
        if "labour_of" in src:
            return round(self.parts(src["labour_of"], src["class"])[0] + 1e-9, 2)
        if "sum_of" in src:
            total, lab_sum = 0.0, 0.0
            for part in src["sum_of"]:
                lab, other, sup = self.parts(part["catalogue"], part["class"])
                total += lab + other
                lab_sum += lab if sup else 0
            if src["with_supplies"]:
                total += min(round(lab_sum * rate + 1e-9, 2), cap)
            if src["with_tax"]:
                total *= 1 + tax
            return round(total + 1e-9, 2)
        lab, other, sup = self.parts(src["catalogue"], src["class"], src["tier"], src["price_class"])
        total = lab + other
        if src["with_supplies"] and sup:
            total += round(lab * rate, 2)
        if src["with_tax"]:
            total *= 1 + tax
        return round(total + 1e-9, 2)


def number_in(said):
    m = re.search(r"\d[\d  ,.]*\d|\d", said)
    if not m:
        return None
    s = m.group(0).replace(" ", "").replace(" ", "")
    if re.search(r",\d\d$", s) and "." not in s:
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------------- one file
def texts_of(conv, public_only=False):
    """(item, text) for every piece of written text in a conversation."""
    out = []
    for it in conv["timeline"]:
        if it["kind"] == "message":
            out.append((it, it["text"]))
        elif it["kind"] in ("draft", "note") and not public_only:
            out.append((it, it["text"]))
        elif it["kind"] == "handoff" and not public_only:
            out.append((it, it["note"]["text"]))
    return out


def instant(cal, it):
    parts = [int(x) for x in it["at"].split(":")]
    while len(parts) < 3:
        parts.append(0)
    return dt.datetime.combine(cal.t.date() + dt.timedelta(days=offset(it["day"])), dt.time(*parts))


def site_of(conv):
    return conv["clock"].split(" ")[0]


def simulate(cal, lang, doc, conv, problems):
    """Walks the timeline as the product would and returns what it leaves: status, owner, labels, waits, drafts."""
    mode, site = conv["assistant_mode"], site_of(conv)
    status = "pending" if mode == "sends" else "open"
    owner, labels, box = None, [], None
    wait_start, session_person = None, False
    last_customer, burst_open = None, False
    waits, resolutions, history = [], [], []
    last_public = None
    items = conv["timeline"]
    by_n = {it["n"]: it for it in items}
    fid = doc["id"]

    def bad(msg):
        problems.append("%s %s: %s" % (fid, conv["key"], msg))

    for it in items:
        t, k = instant(cal, it), it["kind"]
        if k == "message" and it["from"] == "customer":
            if status == "resolved":
                bad("n %d: a customer line after a resolution with no 'reopened' line before it" % it["n"])
            if status == "open" and wait_start is None:
                wait_start = (t, it["n"])
            last_customer, burst_open, last_public = t, True, it
        elif k == "activity" and it["what"] == "reopened":
            if status != "resolved":
                bad("n %d: reopened but the chat was not resolved" % it["n"])
            status = "open" if (owner or mode == "drafts" or "handoff" in labels) else "pending"
            session_person = False
        elif k == "message" and it["from"] == "assistant":
            if not (mode == "sends" and status == "pending" and owner is None and "handoff" not in labels):
                bad("n %d: the assistant sends in a chat that is not its own (mode %s, status %s, owner %s)" % (it["n"], mode, status, owner))
            if last_customer is None or not (12 <= (t - last_customer).total_seconds() <= 75):
                bad("n %d: the assistant's reply is not 12 to 75 s after the customer's last line" % it["n"])
            burst_open, last_public = False, it
        elif k == "handoff":
            if not (mode == "sends" and status == "pending"):
                bad("n %d: a hand-off outside a web chat the assistant holds" % it["n"])
            tool = it["tool"]
            if tool["name"] != "forward_to_manager" or not tool["arguments"]["name"] or not tool["arguments"]["phone"]:
                bad("n %d: the hand-off needs a name and a phone" % it["n"])
            if it["note"]["text"] != tool["arguments"]["context"] or not it["note"]["private"]:
                bad("n %d: the private note is not the tool's context" % it["n"])
            want = ("task", "normal") if tool["type"] == "scheduling" else ("escalation", "high")
            if (it["card"]["kind"], it["card"]["priority"]) != want or it["card"]["owner"] is not None:
                bad("n %d: the card of a %s hand-off is %s at %s, unowned" % (it["n"], tool["type"], want[0], want[1]))
            prev = [x for x in items if x["n"] < it["n"] and x["kind"] == "message" and x["from"] == "assistant"]
            if not prev or lang["said_handoff"] not in prev[-1]["text"]:
                bad("n %d: the assistant's line before the hand-off does not carry the product's sentence (%s)" % (it["n"], lang["said_handoff"]))
            if abs((t - instant(cal, prev[-1])).total_seconds()) > 5 if prev else True:
                bad("n %d: the hand-off is not at the instant of the assistant's line" % it["n"])
            labels.append("handoff")
            status = "open"
            wait_start = (t, it["n"])
        elif k == "draft":
            if not (status == "open" and (mode == "drafts" or owner is not None or "handoff" in labels)):
                bad("n %d: a draft where the assistant would send or the chat is not open" % it["n"])
            lo = 35 if mode == "drafts" else 15
            if last_customer is None or not burst_open or not (lo <= (t - last_customer).total_seconds() <= 100):
                bad("n %d: a draft must follow a customer line by %d to 100 s" % (it["n"], lo))
            if box is not None:
                o = box.get("outcome") or {}
                if o.get("kind") != "replaced_unseen" or o.get("by") is not None or (o.get("day"), o.get("at")) != (it["day"], it["at"]):
                    bad("n %d: the draft %s it replaces must be replaced_unseen, by nobody, at this instant" % (it["n"], box["id"]))
            box = it
            o = it.get("outcome")
            if o and o["kind"] == "discarded" and "cleared" in o.get("because", ""):
                box = None
            burst_open = False
        elif k == "message" and it["from"] == "staff":
            slot = it["slot"]
            if burst_open and status == "open" and (mode == "drafts" or owner is not None or "handoff" in labels):
                bad("n %d: a person replies before the draft for the customer's last lines appeared" % it["n"])
            if owner is None:
                prev = by_n.get(it["n"] - 1) or {}
                if not (prev.get("kind") == "activity" and prev.get("what") == "assigned" and prev.get("to") == slot):
                    bad("n %d: the first reply must be preceded by the 'assigned' line (ownership: first reply)" % it["n"])
                owner = slot
                history.append(slot)
            if box is not None:
                o = box.get("outcome") or {}
                if o.get("kind") == "sent_as_is":
                    good = o.get("became") == it["n"] and box["text"] == it["text"]
                elif o.get("kind") == "sent_edited":
                    good = o.get("became") == it["n"] and box["text"] != it["text"]
                elif o.get("kind") == "discarded":
                    good = True
                else:
                    good = False
                if not good or o.get("by") != slot or (o.get("day"), o.get("at")) != (it["day"], it["at"]):
                    bad("n %d: the outcome of draft %s (%s) does not agree with this line" % (it["n"], box["id"], o.get("kind")))
                box = None
            if "handoff" in labels:
                nxt = by_n.get(it["n"] + 1) or {}
                if not (nxt.get("kind") == "activity" and nxt.get("what") == "label_removed" and nxt.get("label") == "handoff"):
                    bad("n %d: a person's reply takes the handoff label off, and the line for it is missing" % it["n"])
                labels.remove("handoff")
            if wait_start is not None:
                waits.append(dict(n=it["n"], slot=slot, start=wait_start[0], start_n=wait_start[1], end=t, kind="first" if not session_person else "later",
                                  late=it.get("late"), working=cal.working(site, wait_start[0], t)))
            status, wait_start, session_person, burst_open, last_public = "open", None, True, False, it
        elif k == "activity":
            w = it["what"]
            if w == "label_added":
                labels.append(it["label"])
            elif w == "resolved":
                if box is not None:
                    bad("n %d: resolved with a draft still in the box" % it["n"])
                status, wait_start = "resolved", None
                resolutions.append(it)
            elif w == "assigned" and owner is None and it.get("how") != "first reply":
                owner = it["to"]
    return dict(status=status, owner=owner, labels=labels, box=box, waits=waits, resolutions=resolutions, wait_start=wait_start, last_public=last_public)


def main():
    cfg = (sys.argv[1:] or ["en"])[0].strip("/").split("/")[-1]
    if cfg not in LANG:
        print("check_conversations.py: no language table for %r; add it to LANG" % cfg)
        sys.exit(1)
    lang = LANG[cfg]
    folder = os.path.join(CONV, cfg)
    rows = {r["key"]: r for r in load("ledger.json")["rows"]}
    ledger = {k: (r["value"] if "value" in r else {"en": r.get("en"), "ru": r.get("ru")}) for k, r in rows.items()}
    get = lambda key: ledger[key][cfg] if isinstance(ledger[key], dict) and set(ledger[key]) == {"en", "ru"} else ledger[key]
    ledger["_nominal"] = "2026-11-13 10:30"
    cal = Cal(cfg, ledger)
    prices = Prices(cfg)
    cast = {int(p["slot"]): p for p in load("cast.json")["people"] if p["slot"].isdigit()}
    accounts = {a["id"]: a for a in load("accounts.json")[cfg]["accounts"]}
    named = load("named_customers.json")[cfg]
    design = open(os.path.join(CONV, "DESIGN.md"), encoding="utf-8").read()

    say("check_conversations.py %s: the hand-written story conversations in conversations/%s/ against conversations/DESIGN.md, the seed files and the ledger" % (cfg, cfg))
    say()
    # ------------------------------------------------------------------------------------------------ 1
    say("1. Files and format")
    paths = sorted(glob.glob(os.path.join(folder, "*.json")))
    docs, bad = [], []
    for p in paths:
        name = os.path.basename(p)
        m = re.fullmatch(r"(\d\d)-([a-z0-9]+)-([a-z0-9-]+)\.json", name)
        try:
            d = json.load(open(p, encoding="utf-8"))
        except ValueError as e:
            bad.append("%s: %s" % (name, e))
            continue
        if not m or d.get("number") != int(m.group(1)) or d.get("story", "").lower() != m.group(2) or d.get("id") != name[:-5]:
            bad.append(name)
        docs.append(d)
    docs.sort(key=lambda d: d["number"])
    ok("%d files named NN-<story>-<short-name>.json (Latin names), each valid JSON carrying its number, story and id" % len(paths), not bad and len(paths) > 0, bad)
    nums = [d["number"] for d in docs]
    ok("every conversation of DESIGN.md section 6 is there once: 1 to 27 (ledger conv.handwritten = %s)" % get("conv.handwritten"), nums == list(range(1, 28)) and get("conv.handwritten") == 27, nums)
    ok("each file is of the story section 6 gives its number (S7 ×3, S1 ×2, S6, S13 ×2, people ×16, R13 ×3)", all(d["story"] == STORIES.get(d["number"]) for d in docs),
       [(d["number"], d["story"]) for d in docs if d["story"] != STORIES.get(d["number"])])
    need = ("format", "id", "configuration", "number", "story", "title", "demonstrates", "nominal_t", "cast", "scenario", "days", "floating_days", "conversations", "truth", "why", "new_facts")
    cneed = ("key", "channel", "bridge", "inbox", "assistant_mode", "clock", "thread_key", "peer", "contact", "opened", "timeline", "assignee_history", "state_at_t", "reads_back")
    bad = []
    for d in docs:
        if any(k not in d for k in need) or d["format"] != "seed-conversation/1" or d["configuration"] != cfg or not d["nominal_t"].startswith(ledger["_nominal"]):
            bad.append(d["id"])
        for c in d["conversations"]:
            if any(k not in c for k in cneed):
                bad.append(d["id"] + " " + c.get("key", "?"))
            ns = [it.get("n") for it in c["timeline"]]
            if ns != list(range(1, len(ns) + 1)) or any(it.get("kind") not in KINDS or "day" not in it or "at" not in it for it in c["timeline"]):
                bad.append(d["id"] + " timeline")
    ok("every file has the keys of DESIGN.md section 7 (and truth, new_facts, days); every timeline is numbered from 1 with a kind, a day and a time on each line", not bad, bad)
    bad = []
    for d in docs:
        for c in d["conversations"]:
            for it, text in texts_of(c):
                has = bool(re.search("[А-Яа-яЁё]", text))
                if lang["cyrillic"] and text and not has and re.search("[A-Za-z]{4,}", text):
                    bad.append("%s n %d" % (d["id"], it["n"]))
                if not lang["cyrillic"] and has:
                    bad.append("%s n %d" % (d["id"], it["n"]))
    ok("every line a person or the assistant wrote is in the configuration's language", not bad, bad)
    say()

    # ------------------------------------------------------------------------------------------------ 2
    say("2. Days and times (rule R6)")
    bad, n_days = [], 0
    for d in docs:
        used = {it["day"] for c in d["conversations"] for it in c["timeline"]}
        for lab in used:
            if lab not in d["days"]:
                bad.append("%s: %s has no anchor" % (d["id"], lab))
        for lab, row in d["days"].items():
            n_days += 1
            day = cal.resolve(row["rule"])
            if label_of((day - cal.t.date()).days) != lab or row["nominal"] != "%s %s" % (WEEKDAYS[day.weekday()], day.isoformat()):
                bad.append("%s: %s is not where its anchor '%s' falls (%s)" % (d["id"], lab, row["anchor"], day))
    ok("every day of every timeline has an anchor, and each of the %d anchors falls on its day for the nominal T (weekday of a week, a slot's working day by the rota, a shop's open day, calendar days where a card states them)" % n_days, not bad, bad)
    bad = []
    for d in docs:
        for c in d["conversations"]:
            ts = [instant(cal, it) for it in c["timeline"]]
            if any(b < a for a, b in zip(ts, ts[1:])):
                bad.append("%s %s: times go backwards" % (d["id"], c["key"]))
            if ts and ts[-1] > cal.t_at(site_of(c)):
                bad.append("%s %s: a line after T" % (d["id"], c["key"]))
            first = c["timeline"][0]
            if (c["opened"]["day"], c["opened"]["at"]) != (first["day"], first["at"]) or c["opened"]["arrived_closed"] != (not cal.is_open(site_of(c), ts[0])):
                bad.append("%s %s: 'opened' is not the first line, or arrived_closed is wrong" % (d["id"], c["key"]))
    ok("in every conversation the lines are in time order, none is dated after T on the shop's own clock, and 'opened' is the first line with arrived_closed by the shop's hours", not bad, bad)
    bad, n_words = [], 0
    for d in docs:
        fd = d["floating_days"]
        for c in d["conversations"]:
            for it, text in texts_of(c):
                low = text.lower()
                for word, shift in list(lang["day_words"].items()) + list(lang["relative"].items()):
                    for m in re.finditer(lang["word"](word), low):
                        n_words += 1
                        rows_ = [r for r in fd if r["said_on"] == it["day"] and m.group(0) in r["word"].lower()]
                        if not rows_:
                            bad.append("%s n %d: '%s' is in no floating_days row said on %s" % (d["id"], it["n"], m.group(0), it["day"]))
                            continue
                        good = False
                        for r in rows_:
                            labs = re.findall(r"T(?:[+-]\d+d)?(?![\w-])", r["day"])
                            days_ = [cal.t.date() + dt.timedelta(days=offset(x)) for x in labs if re.fullmatch(r"T([+-]\d+d)?", x)]
                            named_wd = [WEEKDAYS.index(x[:3]) for x in re.findall(r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", r["day"])]
                            if word in lang["relative"]:
                                want = offset(it["day"]) + shift
                                good = good or not days_ or any((x - cal.t.date()).days == want for x in days_) or bool(named_wd) or "next day" in r["day"] or "day before" in r["day"]
                                if days_ and not any((x - cal.t.date()).days == want for x in days_) and not named_wd:
                                    good = False
                            else:
                                wd = lang["day_words"][word]
                                good = good or (not days_ and not named_wd) or any(x.weekday() == wd for x in days_) or wd in named_wd
                        if not good:
                            bad.append("%s n %d: '%s' said on %s does not fall on the day its floating_days row gives" % (d["id"], it["n"], m.group(0), it["day"]))
    ok("every weekday word and every 'today', 'tomorrow', 'yesterday' in a line (%d of them) has a floating_days row said on that day, and the row's day is that weekday or that offset" % n_words, not bad, bad)
    say()

    # ------------------------------------------------------------------------------------------------ 3
    say("3. Who speaks in which state: the assistant's mode, hand-offs, drafts and their outcomes")
    modes = get("conv.assistant_mode")
    want_mode = {"chat": modes["web chat"], "telegram": modes.get("Telegram"), "vk": modes.get("VK"), "avito": modes.get("Avito")}
    bad = []
    for d in docs:
        for c in d["conversations"]:
            ch = c["channel"]
            if ch not in lang["channels"] or c["assistant_mode"] != want_mode[ch] or c["bridge"] != ch + ":default" or c["inbox"].lower() != ch:
                bad.append("%s %s: %s %s" % (d["id"], c["key"], ch, c["assistant_mode"]))
            want_ch = lang["channel_of"].get(d["number"], "chat")
            if d["story"] != "people" and ch != want_ch:
                bad.append("%s: section 6 puts it on %s" % (d["id"], want_ch))
    ok("each chat is on a channel of this configuration (%s) in the ledger's mode (conv.assistant_mode: web chat sends, the messengers draft), and the story and R13 chats are on the channels section 6 names" % ", ".join(lang["channels"]), not bad, bad)
    problems, sims, n_drafts, n_hand = [], {}, 0, 0
    for d in docs:
        for c in d["conversations"]:
            sims[(d["number"], c["key"])] = simulate(cal, lang, d, c, problems)
            n_drafts += sum(1 for it in c["timeline"] if it["kind"] == "draft")
            n_hand += sum(1 for it in c["timeline"] if it["kind"] == "handoff")
    ok("walked as the product would: the assistant sends only in a web chat that is its own and within 12 to 75 s; %d hand-offs are made by the assistant with a name, a phone, the private note, the right card and the product's sentence; "
       "%d drafts stand only where the assistant may not send, follow the customer by 15 (web) or 35 (messenger) to 100 s, and each outcome agrees with the line it names (sent as it was: the same words; edited: other words; discarded: the person's own line or a clear; replaced: by the next draft, by nobody)" % (n_hand, n_drafts),
       not problems, problems)
    bad = []
    for d in docs:
        for c in d["conversations"]:
            sim = sims[(d["number"], c["key"])]
            st, rb = c["state_at_t"], c["reads_back"]
            drafts = [it for it in c["timeline"] if it["kind"] == "draft"]
            got = [(x["draft"], x["outcome"], x["manager"]) for x in rb["draft_outcomes"]]
            want = [(it["id"], it["outcome"]["kind"], it["outcome"]["by"]) for it in drafts if it.get("outcome")]
            if got != want:
                bad.append("%s: reads_back.draft_outcomes is not the timeline's" % d["id"])
            waiting = [it["id"] for it in drafts if not it.get("outcome")]
            if (waiting[0] if waiting else None) != st["draft_in_box"] or len(waiting) > 1:
                bad.append("%s: draft_in_box" % d["id"])
            if waiting and not (c["channel"] == "chat" and sim["status"] == "open" and drafts[-1]["id"] == waiting[0]):
                bad.append("%s: a draft without an outcome may only be the last one of an open web chat" % d["id"])
            if (sim["status"], sim["owner"], sorted(sim["labels"])) != (st["status"], st["owner"], sorted(st["labels"])):
                bad.append("%s: state_at_t says %s/%s/%s, the timeline leaves %s/%s/%s" % (d["id"], st["status"], st["owner"], st["labels"], sim["status"], sim["owner"], sim["labels"]))
            res = [(r["day"], r["at"], r["by"]) for r in rb["resolutions"]]
            if res != [(r["day"], r["at"], r["by"]) for r in sim["resolutions"]]:
                bad.append("%s: reads_back.resolutions" % d["id"])
            for r in sim["resolutions"]:
                if r["by"] is None:
                    lastmsg = max(instant(cal, it) for it in c["timeline"] if it["kind"] in ("message", "note") and it["n"] < r["n"])
                    if abs((instant(cal, r) - lastmsg).total_seconds() - 7 * 86400) > 60 or get("conv.auto_resolve_days") != 7:
                        bad.append("%s: a resolution by nobody must come 7 days after the last line" % d["id"])
            pr = [it for it in c["timeline"] if it["kind"] == "activity" and it["what"] == "priority"]
            shown = "normal"
            for it in pr:
                if it["from"] != shown:
                    bad.append("%s n %d: priority line starts from %s, the chat was at %s" % (d["id"], it["n"], it["from"], shown))
                shown = it["to"]
            if sim["status"] != "resolved" and shown != st["priority"]["shown"]:
                bad.append("%s: shown priority" % d["id"])
            kinds = {"customer": 0, "assistant": 0, "manager": 0, "note": 0}
            for it in c["timeline"]:
                if it["kind"] == "message":
                    kinds[{"customer": "customer", "assistant": "assistant", "staff": "manager"}[it["from"]]] += 1
                elif it["kind"] in ("note", "handoff"):
                    kinds["note"] += 1
            if rb["message_kinds"] != kinds:
                bad.append("%s: message_kinds" % d["id"])
    ok("state_at_t and reads_back are what the timeline leaves: status, owner, labels, the draft in the box, the outcome rows, the resolutions (a resolution by nobody exactly 7 silent days after the last line), the priority lines in order, the message kinds", not bad, bad)
    say()

    # ------------------------------------------------------------------------------------------------ 4
    say("4. Waits, and each person's waits against the ledger (pNN.first_reply_min, conv.later_reply_factor, conv.slowest_tenth)")
    bad, per, staff_days = [], {}, []
    for d in docs:
        for c in d["conversations"]:
            sim = sims[(d["number"], c["key"])]
            mine = {w["answered"]: w for w in c["reads_back"]["waits"] if w.get("by") not in (None, "assistant") and "working_minutes" in w}
            for w in sim["waits"]:
                got = mine.get(w["n"])
                if not got or abs(got["working_minutes"] - w["working"]) > 0.15 or got["by"] != w["slot"] or got["reply"] != w["kind"]:
                    bad.append("%s n %d: the wait is %.1f working minutes by slot %s (%s)" % (d["id"], w["n"], w["working"], w["slot"], w["kind"]))
                per.setdefault(w["slot"], []).append(dict(w, file=d["number"]))
            if len(mine) != len(sim["waits"]):
                bad.append("%s: reads_back.waits lists %d waits answered by people, the timeline has %d" % (d["id"], len(mine), len(sim["waits"])))
            for it in c["timeline"]:
                if it["kind"] in ("message", "note") and it.get("from") == "staff":
                    t = instant(cal, it)
                    if not cal.works(it["slot"], t.date()) or not cal.is_open(site_of(c), t):
                        staff_days.append("%s n %d: slot %d writes on %s %s, outside the rota or the shop's hours" % (d["id"], it["n"], it["slot"], WEEKDAYS[t.weekday()], t))
    ok("every wait answered by a person is recomputed in working minutes on the shop's hours (%s to %s) and equals reads_back.waits, with its first-or-later kind" % tuple(get("site.hours.weekday")), not bad, bad)
    ok("every line a person wrote falls in the shop's opening hours on a day that person works (%s)" % ("ru: two on, two off by roster.advisor_pattern; managers on weekdays" if cfg == "ru" else "en: full open days"), not staff_days, staff_days)
    say("        slot  row  first replies (working min; * = marked late)            later replies")
    bad, factor = [], get("conv.later_reply_factor")
    for slot in sorted(per):
        m = ledger["p%02d.first_reply_min" % slot][cfg]
        firsts = [w for w in per[slot] if w["kind"] == "first"]
        laters = [w for w in per[slot] if w["kind"] == "later"]
        say("        %-4d  %-3d  %-58s %s" % (slot, m, " ".join("%.1f%s" % (w["working"], "*" if w["late"] else "") for w in firsts), " ".join("%.1f%s" % (w["working"], "*" if w["late"] else "") for w in laters)))
        for w in per[slot]:
            top = 2.5 * m
            if w["late"]:
                story = w["late"].startswith("story")
                if not story and w["working"] <= top:
                    bad.append("file %d n %d: marked late at %.1f min, inside slot %d's ordinary range" % (w["file"], w["n"], w["working"], slot))
                if not story and slot not in (22, 23) and w["working"] > 5.5 * m and "nothing to answer" not in w["late"]:
                    bad.append("file %d n %d: %.1f min is past five times slot %d's row" % (w["file"], w["n"], w["working"], slot))
                if not story and slot in (22, 23) and w["working"] > top:
                    same_day_close = w["end"].date() == w["start"].date() and (cal.hours("west", w["end"].date())[1] - (w["end"].hour * 60 + w["end"].minute)) <= 90
                    nxt = w["start"].date() + dt.timedelta(days=1)
                    while not cal.works(slot, nxt):
                        nxt += dt.timedelta(days=1)
                    if not (same_day_close or w["end"].date() == nxt):
                        bad.append("file %d n %d: slot %d's slow reply is neither at closing time nor on his next working day" % (w["file"], w["n"], slot))
            elif w["kind"] == "first" and not (0.3 * m <= w["working"] <= top):
                bad.append("file %d n %d: first reply %.1f min, slot %d's row is %d (range %.1f to %.1f, or mark it late)" % (w["file"], w["n"], w["working"], slot, m, 0.3 * m, top))
            elif w["kind"] == "later" and w["working"] > top:
                bad.append("file %d n %d: later reply %.1f min, slot %d's row is %d" % (w["file"], w["n"], w["working"], slot, m))
        plain = [w["working"] for w in firsts if not w["late"]]
        if len(plain) >= 2 and not (0.6 * m <= statistics.median(plain) <= 1.6 * m):
            bad.append("slot %d: the median of his or her ordinary first replies is %.1f, the row is %d" % (slot, statistics.median(plain), m))
        plain = [w["working"] for w in laters if not w["late"]]
        if len(plain) >= 2 and statistics.median(plain) > m:
            bad.append("slot %d: later replies in an exchange run at %.1f min, above the first-reply row %d (the ledger: %.1f of it)" % (slot, statistics.median(plain), m, factor))
    ok("each person's waits fall inside that person's ledger row: an ordinary first reply between 0.3 and 2.5 times the row and their median within 0.6 to 1.6 of it; later replies under 2.5 times the row with a median under it; "
       "a reply marked late is the slowest tenth (up to 5 times the row; slots 22 and 23: at closing time or the next working day) or a wait a card states (S1, S6, S7)", not bad, bad)
    out_rows = get("conv.draft_outcomes")
    say("        slot  drafts acted on: sent as is / edited / discarded (the ledger's row, %)       replaced unseen")
    bad = []
    for slot in sorted({o["manager"] for d in docs for c in d["conversations"] for o in c["reads_back"]["draft_outcomes"] if o["manager"]}):
        got = [o["outcome"] for d in docs for c in d["conversations"] for o in c["reads_back"]["draft_outcomes"] if o["manager"] == slot]
        n = len(got)
        share = [100.0 * got.count(k) / n for k in ("sent_as_is", "sent_edited", "discarded")]
        row = out_rows[str(slot)]
        say("        %-4d  %2d: %3.0f / %3.0f / %3.0f   (%s)" % (slot, n, share[0], share[1], share[2], " / ".join(str(x) for x in row)))
        tol = max(10.0, 100.0 / (n ** 0.5))
        if n >= 4 and any(abs(a - b) > tol for a, b in zip(share, row)):
            bad.append("slot %d: %s against %s (tolerance %.0f points on %d drafts)" % (slot, [round(x) for x in share], row, tol, n))
        if n >= 3 and got.count(("sent_as_is", "sent_edited", "discarded")[row.index(max(row))]) == 0:
            bad.append("slot %d never does what the row says he or she does most" % slot)
    unseen = sum(1 for d in docs for c in d["conversations"] for o in c["reads_back"]["draft_outcomes"] if o["outcome"] == "replaced_unseen")
    say("        replaced before anyone acted: %d of %d drafts (the ledger: %s %% of all drafts in the whole seed)" % (unseen, n_drafts, get("conv.draft_replaced_unseen")))
    ok("each person's draft outcomes lean the way the ledger's sheet does (conv.draft_outcomes; the tolerance widens with the few drafts a hand-written set holds: 10 points or 100/sqrt(n))", not bad, bad)
    share_rows, bad = get("conv.label_share"), []
    topic = set(share_rows["labels"][cfg])
    sessions = {}
    for d in docs:
        for c in d["conversations"]:
            sim = sims[(d["number"], c["key"])]
            if sim["owner"]:
                s = sessions.setdefault(sim["owner"], dict(n=0, labelled=0, resolved=0))
                s["n"] += 1
                s["labelled"] += any(it["kind"] == "activity" and it["what"] == "label_added" and it.get("by") == sim["owner"] for it in c["timeline"])
                s["resolved"] += any(r["by"] == sim["owner"] for r in sim["resolutions"])
            for lab in c["state_at_t"]["labels"]:
                if lab not in topic and lab != "handoff":
                    bad.append("%s: label %s is not the tenant's" % (d["id"], lab))
            for it in c["timeline"]:
                if it["kind"] == "activity" and it["what"] == "label_added" and it["label"] not in topic:
                    bad.append("%s: label %s is not the tenant's" % (d["id"], it["label"]))
    for slot, s in sorted(sessions.items()):
        if slot in share_rows["almost_never"] and (s["labelled"] or s["resolved"]):
            bad.append("slot %d labels or resolves, and the ledger says almost never" % slot)
        if slot in share_rows["nearly_always"] and s["labelled"] < 0.7 * s["n"]:
            bad.append("slot %d labels %d of %d chats, and the ledger says nearly always" % (slot, s["labelled"], s["n"]))
    say("        chats owned / with a topic label / resolved by the owner: " + "; ".join("slot %d: %d / %d / %d" % (k, v["n"], v["labelled"], v["resolved"]) for k, v in sorted(sessions.items())))
    ok("labels are the tenant's (%s); slots %s label nearly every chat they own and slots %s label and resolve none (conv.label_share, conv.resolved_by_person)" % (", ".join(share_rows["labels"][cfg]), share_rows["nearly_always"], share_rows["almost_never"]), not bad, bad)
    say()

    # ------------------------------------------------------------------------------------------------ 5
    say("5. Names, phones, units, prices and channel identities against the seed files")
    bad = []
    for d in docs:
        for row in d["cast"].get("staff", []):
            full = cast[row["slot"]][cfg]["full_name"].split()
            if row["name"].split() not in (full, [full[0], full[-1]]):
                bad.append("%s: slot %d is %s" % (d["id"], row["slot"], " ".join(full)))
        slots = {row["slot"] for row in d["cast"].get("staff", [])}
        for c in d["conversations"]:
            for it in c["timeline"]:
                if it.get("from") == "staff" and it["slot"] not in slots:
                    bad.append("%s n %d: slot %d is not in the file's cast" % (d["id"], it["n"], it["slot"]))
                if it["kind"] == "note":
                    for mslot in it.get("mentions", []):
                        if "@" + cast[mslot][cfg]["full_name"] not in it["text"] and "@" + " ".join([cast[mslot][cfg]["full_name"].split()[0], cast[mslot][cfg]["full_name"].split()[-1]]) not in it["text"]:
                            bad.append("%s n %d: the mention of slot %d is not that person's name" % (d["id"], it["n"], mslot))
        cu = d["cast"].get("customer") or {}
        ref = cu.get("ref")
        if ref:
            src, _, path = ref.partition(" ")
            if src == "named_customers.json":
                rec = named[path.split(".", 1)[1]]
            else:
                acc, idx = re.fullmatch(r"\w+\.(A\d) contacts\[(\d)\]", path).groups()
                rec = accounts[acc]["contacts"][int(idx)]
                if accounts[acc]["name"] not in cu.get("company", ""):
                    bad.append("%s: the company is %s" % (d["id"], accounts[acc]["name"]))
            if rec["name"] != cu["name"] or rec["phone"] != cu["phone"]:
                bad.append("%s: %s is %s, %s in the seed files" % (d["id"], ref, rec["name"], rec["phone"]))
        elif not cu.get("invented"):
            bad.append("%s: the customer is neither a reference into the seed files nor marked invented" % d["id"])
        for extra in d["cast"].get("named_in_a_line", []) + d["cast"].get("named_in_a_note", []):
            if "slot" in extra:
                full = cast[extra["slot"]][cfg]["full_name"].split()
                if extra["name"].split() not in (full, [full[0], full[-1]]):
                    bad.append("%s: slot %d is %s" % (d["id"], extra["slot"], " ".join(full)))
            if extra.get("ref"):
                acc, idx = re.fullmatch(r"accounts\.json \w+\.(A\d) contacts\[(\d)\]", extra["ref"]).groups()
                if accounts[acc]["contacts"][int(idx)]["name"] != extra["name"]:
                    bad.append("%s: %s" % (d["id"], extra["ref"]))
            if extra.get("vendor"):
                v = [x for x in load("vendors.json")[cfg] if x["id"] == extra["vendor"]][0]
                if v["name"] != extra["name"]:
                    bad.append("%s: vendor %s is %s" % (d["id"], extra["vendor"], v["name"]))
    ok("staff are the slots of cast.json under their names, every line is by a slot of the file's cast, mentions carry the person's name; customers are the named ones of named_customers.json and accounts.json (name and phone) or are marked invented", not bad, bad)

    def digits(s):
        return re.sub(r"\D", "", s)

    seed_text = json.dumps(load("accounts.json")[cfg], ensure_ascii=False) + json.dumps(named, ensure_ascii=False) + json.dumps(load("vendors.json")[cfg], ensure_ascii=False) + open(os.path.join(SEED, "phones.md"), encoding="utf-8").read()
    seed_phones = {digits(m.group(0))[-10:] for m in lang["phone"].finditer(seed_text)}
    bad, n_ph, new_ph = [], 0, set()
    for d in docs:
        cu = d["cast"].get("customer") or {}
        mine = digits(cu.get("phone", ""))[-10:]
        for c in d["conversations"]:
            for it, text in texts_of(c):
                found = [digits(m.group(0))[-10:] for m in lang["phone"].finditer(text)] + [x[-10:] for x in re.findall(r"(?<!\d)(?:8|1)?\d{10}(?!\d)", text)]
                if cfg == "ru":
                    found += ["8422" + digits(x) for x in re.findall(r"(?<!\d)10-40-4\d(?!\d)", text)]
                for ph in set(found):
                    n_ph += 1
                    if cfg == "en":
                        fict = ph[3:6] == "555" and ph[6:] not in ("1212", "4334") and int(ph[6:]) >= 100
                        known = ph in seed_phones or int(ph[6:]) >= 200
                    else:
                        fict = ph[:3] in ("907", "935") or (ph[:4] == "8422" and ph[4] in "01") or (ph[:3] == "843" and ph[3] in "01")
                        known = True
                    if not fict or not known:
                        bad.append("%s n %d: %s is not a number of phones.md's scheme (or is a reserved tier-A number no seed file gives)" % (d["id"], it["n"], ph))
                    if ph not in seed_phones:
                        new_ph.add(ph)
                    if ph not in seed_phones and ph != mine:
                        bad.append("%s n %d: %s is neither a seed number nor the file's customer's" % (d["id"], it["n"], ph))
            for it in c["timeline"]:
                if it["kind"] == "handoff":
                    hp = digits(it["tool"]["arguments"]["phone"])[-10:]
                    earlier = " ".join(digits(x["text"]) for x in c["timeline"] if x["n"] < it["n"] and x["kind"] == "message")
                    if hp != mine or hp not in earlier:
                        bad.append("%s n %d: the hand-off's phone is not the customer's, or was not said in the chat before it" % (d["id"], it["n"]))
            if c["channel"] != "chat" and c["contact"]["phone"] is not None:
                bad.append("%s: a messenger contact carries a phone only when the channel gave one" % d["id"])
    ok("%d phone numbers in the lines: each is fictional by phones.md (en: the 555 exchange, tier A only for numbers the seed files give, tier B otherwise; ru: codes 907 and 935, city numbers beginning with 0 or 1), each is a seed number or the file's own customer's; "
       "a hand-off carries the number the customer typed (or confirmed) in that chat; %d numbers are new to the seed" % (n_ph, len(new_ph)), not bad, bad)

    fleets = {aid: ({v["unit"] for v in a["fleet"]}, {v["plate"] for v in a["fleet"]}) for aid, a in accounts.items()}
    bad, n_units = [], 0
    for d in docs:
        cu = d["cast"].get("customer") or {}
        m = re.search(r"\.(A\d) contacts", cu.get("ref", ""))
        if not m:
            continue
        units, plates = fleets[m.group(1)]
        for c in d["conversations"]:
            for it, text in texts_of(c):
                for u in lang["unit"].findall(text):
                    n_units += 1
                    if u not in units:
                        bad.append("%s n %d: unit %s is not in %s's fleet" % (d["id"], it["n"], u, m.group(1)))
                for p in lang["plate"].findall(text):
                    n_units += 1
                    if p not in plates:
                        bad.append("%s n %d: plate %s is not in %s's fleet" % (d["id"], it["n"], p, m.group(1)))
        for v in d["scenario"].get("vehicles", []) if isinstance(d["scenario"].get("vehicles"), list) else []:
            for p in lang["plate"].findall(v):
                if p not in plates:
                    bad.append("%s: scenario plate %s" % (d["id"], p))
    ok("%d unit numbers and plates in the company accounts' chats are vehicles of that account's fleet in accounts.json" % n_units, not bad, bad)

    bad, n_pr, declared_all = [], 0, 0
    for d in docs:
        facts = d["scenario"].get("facts", {})
        decl = {}
        for p in facts.get("prices", []):
            declared_all += 1
            want = prices.amount(p["from"], ledger, decl)
            decl[p["said"]] = p["amount"]
            num = number_in(p["said"])
            if abs(want - p["amount"]) > 0.005:
                bad.append("%s: %s is declared %.2f, the catalogue or the ledger gives %.2f" % (d["id"], p["said"], p["amount"], want))
            if num is None or (abs(num - p["amount"]) > 0.005 and abs(num - round(p["amount"])) > 0.5 and abs(num - p["amount"]) > 2.5):
                bad.append("%s: '%s' does not say %.2f" % (d["id"], p["said"], p["amount"]))
        allowed = sorted(list(decl) + [x["said"] for x in facts.get("numbers", [])], key=len, reverse=True)
        acc_ref = re.search(r"\.(A\d) contacts", (d["cast"].get("customer") or {}).get("ref", ""))
        # a dispatcher writes a unit by its number alone ("113's driver"): such a number is a unit of that account's fleet
        short_units = sorted({re.sub(r"^\D+", "", u) for u in fleets[acc_ref.group(1)][0]} if acc_ref else [], key=len, reverse=True)
        short_units = [u for u in short_units if len(u) >= 3]
        whole = " ".join(json.dumps(c["timeline"], ensure_ascii=False) for c in d["conversations"])
        for s in allowed:
            if s not in whole:
                bad.append("%s: '%s' is declared and never said" % (d["id"], s))
        for c in d["conversations"]:
            for it, text in texts_of(c):
                work = text
                for f_ in it.get("files", []) if it["kind"] == "message" else []:
                    work += " " + f_.get("shows", "")
                for s in allowed:
                    n_pr += work.count(s)
                    work = work.replace(s, " ")
                for m in lang["phone"].finditer(work):
                    work = work.replace(m.group(0), " ")
                work = re.sub(r"(?<!\d)(?:8|1)?\d{10}(?!\d)", " ", work)
                work = lang["unit"].sub(" ", lang["plate"].sub(" ", work))
                for u in short_units:
                    work = re.sub(r"(?<![\w.,$-])%s(?![\w.,-])" % re.escape(u), " ", work)
                for pat in lang["strip"]:
                    work = re.sub(pat, " ", work)
                for m in lang["money"].finditer(work):
                    bad.append("%s n %d: the amount %s is not declared under scenario.facts.prices" % (d["id"], it["n"], m.group(0)))
                for m in re.finditer(r"(?<![\w.,-])\d[\d,.]*\d|(?<![\w.,-])\d", lang["money"].sub(" ", work)):
                    v = number_in(m.group(0))
                    if v is not None and v >= 20:
                        bad.append("%s n %d: the number %s is neither a declared price nor a declared number" % (d["id"], it["n"], m.group(0)))
    ok("%d prices are declared and each is recomputed from catalogue.json (list or company-account class, vehicle class, shop supplies, tax) or read from the ledger; every amount and every number of 20 or more in a line, a draft, a note or a file's description (%d uses) is a declared price or a declared number; times, dates, phones, units and addresses apart" % (declared_all, n_pr), not bad, bad)

    bad = []
    for d in docs:
        for c in d["conversations"]:
            for it, text in texts_of(c):
                for street, num in lang["addresses"].items():
                    for m in re.finditer(r"(\d{2,5})\s+%s|%s[а-яё ]*,\s*(\d{1,4})" % (re.escape(street), re.escape(street)), text):
                        got = m.group(1) or m.group(2)
                        if got != num:
                            bad.append("%s n %d: %s %s" % (d["id"], it["n"], street, got))
                for old in lang["old_names"]:
                    if old in text:
                        bad.append("%s n %d: the old name %s" % (d["id"], it["n"], old))
    addr = "; ".join("%s: %s" % (k, get("geo.address." + k).split(" (")[0]) for k in ("main", "east", "west"))
    ok("street numbers said with a shop's street are the ledger's (%s); no placeholder name of the east shop is left" % addr, not bad and all(v in addr for v in lang["addresses"].values()), bad)

    ids = get("conv.fictional_ids")
    bad, seen_threads, peers = [], {}, {}
    for d in docs:
        for c in d["conversations"]:
            ch, peer, ct = c["channel"], c["peer"], c["contact"]
            if ct["identifier"] != "%s_%s" % (ch, peer["id"]) or ct["name"] != peer["name"]:
                bad.append("%s: contact identifier or name" % d["id"])
            if ch == "chat":
                good = re.fullmatch(r"seedv1-browser-%s-\d{4}" % cfg, peer["id"]) and re.fullmatch(r"5eedc0de-\d{4}-4e00-8000-[0-9a-f]{12}", c["thread_key"]) and peer["name"] == lang["visitor"] and ct["phone"] is None and not ct["avatar"]["has"]
            elif ch == "telegram":
                good = peer["id"].isdigit() and int(peer["id"]) >= ids["telegram_peers_from"] and int(peer["id"]) > 2 ** 52 and c["thread_key"] == peer["id"]
            elif ch == "vk":
                good = peer["id"].isdigit() and ids["vk_peers"][0] <= int(peer["id"]) <= ids["vk_peers"][1] and c["thread_key"] == peer["id"]
            else:
                lc = c.get("listing_context", {})
                good = c["thread_key"].startswith("u2i-seedv1-") and re.fullmatch(r"900\d{12}", peer["id"]) and re.fullmatch(r"900\d{12}", lc.get("item_id", "")) and ".example/" in lc.get("url", "")
            if not good:
                bad.append("%s: the %s identity is not of the fictional form" % (d["id"], ch))
            if c["thread_key"] in seen_threads:
                bad.append("%s: thread key used by %s too" % (d["id"], seen_threads[c["thread_key"]]))
            seen_threads[c["thread_key"]] = d["id"]
            peers.setdefault(peer["id"], []).append(d["number"])
    shared = {k: v for k, v in peers.items() if len(v) > 1}
    ok("channel identities cannot be real accounts (ledger conv.fictional_ids: Telegram peers above 2^52, VK peers %d to %d, Avito chats u2i-seedv1-… with 15-digit ids from 900 and links under .example, web visitors seedv1-browser-…); "
       "every thread key is used once; the only contact with more than one conversation is S7's website visitor (files 1, 2, 3)" % tuple(ids["vk_peers"]), not bad and list(shared.values()) == [[1, 2, 3]], bad or shared)

    bad, pics, mess = [], 0, 0
    for d in docs:
        for c in d["conversations"]:
            av = c["contact"]["avatar"]
            if c["channel"] == "chat":
                continue
            mess += 1
            if av["has"]:
                pics += 1
                low = av["shows"].lower()
                if av.get("person_in_it") is not False or av.get("kind") not in ("car", "pet", "view") or any(re.search(r"(?<![a-zа-яё])%s(?![a-zа-яё])" % w, low) for w in lang["person_words"]):
                    bad.append("%s: the picture must show no person" % d["id"])
                if av["kind"] == "car":
                    veh = av.get("matches_vehicle", "")
                    sc = json.dumps(d["scenario"], ensure_ascii=False) + json.dumps(d["cast"], ensure_ascii=False)
                    words = [w for w in re.findall(r"[A-Za-zА-Яа-яё-]{4,}", veh)]
                    if not veh or veh not in sc or not any(w.lower() in low for w in words):
                        bad.append("%s: a car picture must be the customer's car (%s)" % (d["id"], veh))
    row = get("conv.avatars")
    share = 100.0 * pics / mess
    ok("pictures of messenger contacts: %d of %d have one (%.0f %%; the ledger: %d %%, here within 15 points), each a car, a pet or a view with no person in it, a car being the customer's own; website visitors have none"
       % (pics, mess, share, row["messenger_contacts_with_a_picture_pct"]), not bad and abs(share - row["messenger_contacts_with_a_picture_pct"]) <= 15, bad)
    say()

    # ------------------------------------------------------------------------------------------------ 6
    say("6. The state at T (ledger conv.open_at_t, conv.live_demo)")
    open_now = [(d, c) for d in docs for c in d["conversations"] if c["state_at_t"]["status"] != "resolved"]
    got = sorted((d["number"], c["channel"], c["state_at_t"]["status"], c["state_at_t"]["owner"], c["state_at_t"]["draft_in_box"] is not None) for d, c in open_now)
    want = sorted([(3, "chat", "open", 6, True), (6, "chat", "open", 23, True), (7, "chat", "pending", None, False), (5, lang["channel_of"][5], "open", 16, False)])
    named_rows = get("conv.open_at_t")["named"]
    ok("open or pending at T are exactly the four chats the ledger names (%s): S7's return chat (web, open, slot 6, a draft waiting), S6's chat (web, open, slot 23, a draft waiting), S13's question (web, pending, nobody's), A2's weekly thread (%s, open, slot 16, no draft); the other 23 are resolved"
       % ("; ".join(named_rows), lang["channel_of"][5]), got == want and len(named_rows) == 4, got)
    bad = []
    for d, c in open_now:
        st, sim = c["state_at_t"], sims[(d["number"], c["key"])]
        last = sim["last_public"]
        t_local = cal.t_at(site_of(c))
        if c["channel"] != "chat":
            if last["from"] != "staff" or st["draft_in_box"] or st["waiting_since"] or st["unread"]:
                bad.append("%s: an open messenger chat must wait on the customer: last public line the shop's, no draft, nothing unread" % d["id"])
        if (t_local - instant(cal, last)).days >= 7:
            bad.append("%s: silent for seven days at T; Chatwoot would resolve it" % d["id"])
        if st["waiting_since"]:
            ws = sim["wait_start"]
            if not ws or (st["waiting_since"]["day"], st["waiting_since"]["at"]) != (label_of((ws[0].date() - cal.t.date()).days), ws[0].strftime("%H:%M:%S")):
                bad.append("%s: waiting_since" % d["id"])
            elif abs(cal.working(site_of(c), ws[0], t_local) - st["waited_working_minutes_at_t"]) > 0.15:
                bad.append("%s: waited_working_minutes_at_t" % d["id"])
            if st["unread"] != sum(1 for it in c["timeline"] if it["kind"] == "message" and it["from"] == "customer" and instant(cal, it) >= ws[0]):
                bad.append("%s: unread" % d["id"])
    ok("no open chat at T on Telegram, VK or Avito expects a reply from staff (its last public line is the shop's, no draft, nothing unread); the chats that wait on the shop are web chats; none has been silent for 7 days; waiting_since, the wait in working minutes and the unread count are the timeline's", not bad, bad)
    by = {d["number"]: d for d in docs}
    s6 = by[6]["conversations"][0]
    c6 = [it for it in s6["timeline"] if it["kind"] == "message" and it["from"] == "customer"]
    bursts, prev = [], None
    for it in c6:
        if prev is None or instant(cal, it) - instant(cal, prev) > dt.timedelta(hours=2):
            bursts.append(it)
        prev = it
    first_of_day = {}
    for it in bursts:
        first_of_day.setdefault(it["day"], it)
    days6 = sorted(-offset(x) for x in first_of_day)
    row6 = get("s6.customer_contacts")
    waits6 = []
    for day, it in sorted(first_of_day.items(), key=lambda kv: offset(kv[0])):
        later = [x for x in s6["timeline"] if x["n"] > it["n"] and x["kind"] == "message" and x["from"] == "staff"]
        end = instant(cal, later[0]) if later else cal.t_at("west")
        waits6.append((end - instant(cal, it)).total_seconds() / 3600)
    ok("S6: his messages are on %s days before T (ledger s6.customer_contacts.message_days_before_t = %s), each waits over %d hours for a person's reply (%s h), the chat is urgent by its wait and the car came in 9 calendar days before T"
       % (sorted(days6, reverse=True), row6["message_days_before_t"], row6["each_waited_hours_over"], ", ".join("%.1f" % x for x in waits6)),
       sorted(days6, reverse=True) == row6["message_days_before_t"] and min(waits6) > row6["each_waited_hours_over"] and s6["state_at_t"]["priority"]["shown"] == "urgent" and "T-9d" in by[6]["days"])
    s7 = [by[n]["conversations"][0] for n in (1, 2, 3)]
    first = instant(cal, s7[0]["timeline"][0])
    order = [instant(cal, c["timeline"][0]) for c in s7]
    thr = get("s7.thread")
    ret = [it for it in s7[2]["timeline"] if it["kind"] == "message"]
    staff3 = [it for it in ret if it["from"] == "staff"]
    last3 = [it for it in ret if it["from"] == "customer" and it["day"] == "T"]
    ok("S7: three web chats of one contact; the first at %s on the evening before day A and under %d days before T (%d); chat, visit, thanks, return chat in that order; the return message at %s, slot 6's first line at %s, her last message %d minutes before T; the return chat's draft is the only thing in its box"
       % (thr["chat"], get("conv.web_visitor_memory_days"), (cal.t - first).days, thr["return_message"], thr["taken_by_6"], thr["last_message_before_t_min"]),
       len({c["contact"]["identifier"] for c in s7}) == 1 and (cal.t - first).days < get("conv.web_visitor_memory_days") and order == sorted(order)
       and s7[0]["timeline"][0]["at"].startswith(thr["chat"]) and ret[0]["at"].startswith(thr["return_message"]) and staff3 and staff3[0]["at"].startswith(thr["taken_by_6"])
       and last3 and abs((cal.t - instant(cal, last3[0])).total_seconds() / 60 - thr["last_message_before_t_min"]) < 1.0)
    s1 = by[4]["conversations"][0]
    hand = [it for it in s1["timeline"] if it["kind"] == "handoff"][0]
    firstp = [it for it in s1["timeline"] if it["kind"] == "message" and it["from"] == "staff"][0]
    gap = (instant(cal, firstp) - instant(cal, hand)).total_seconds() / 86400
    day4 = cal.resolve({"kind": "weekday_of_week", "weekday": "Tue", "week": 4})
    ok("S1: A6's quote request is a web chat begun on the Tuesday of week T-4 (ledger s1.dates), the first line by a person comes %.2f days after the hand-off (s1.a6.quote_chat_waited_days = %s), by slot 7 after slot 5's note; resolved by nobody"
       % (gap, get("s1.a6")["quote_chat_waited_days"]),
       instant(cal, s1["timeline"][0]).date() == day4 and 1.75 <= gap <= 2.25 and firstp["slot"] == 7 and any(it["kind"] == "note" and it["slot"] == 5 and it["n"] < firstp["n"] for it in s1["timeline"])
       and s1["state_at_t"]["status"] == "resolved" and sims[(4, s1["key"])]["resolutions"][-1]["by"] is None)
    a2 = by[5]["conversations"][0]
    sess = a2["state_at_t"].get("sessions", [])
    ok("S1: A2's weekly thread is one %s conversation with %d written sessions, three resolved by slot 16 and the last open; S13: the web question is on the Monday of week W0 and the regular's on slot 16's last working day before T, both about the stocktake day of the ledger (site.stocktake)"
       % (lang["channel_of"][5], len(sess)),
       len(sess) == 4 and len(sims[(5, a2["key"])]["resolutions"]) == 3 and offset(by[7]["conversations"][0]["timeline"][0]["day"]) == (cal.resolve({"kind": "weekday_of_week", "weekday": "Mon", "week": 0}) - cal.t.date()).days
       and offset(by[8]["conversations"][0]["timeline"][0]["day"]) == (cal.resolve({"kind": "slot_working_day", "slot": 16, "n": -1}) - cal.t.date()).days
       and "Thursday of week W+1" in get("site.stocktake")["day"] and all("T+6d" in by[n]["days"] for n in (7, 8)))
    say()

    # ------------------------------------------------------------------------------------------------ 7
    say("7. People and unclear customers (DESIGN.md section 6; rule R13)")
    owners = {}
    for n in range(9, 25):
        c = by[n]["conversations"][0]
        first_staff = [it["slot"] for it in c["timeline"] if it.get("from") == "staff"]
        owners.setdefault(first_staff[0] if first_staff else None, []).append(n)
    ok("files 9 to 24 are two conversations for each of slots %s, each begun by that person's line, all resolved, spread from G to T (%d to %d days before T)"
       % (list(PEOPLE_SLOTS), max(-offset(by[n]["conversations"][0]["timeline"][0]["day"]) for n in range(9, 25)), min(-offset(by[n]["conversations"][0]["timeline"][0]["day"]) for n in range(9, 25))),
       sorted(owners) == sorted(PEOPLE_SLOTS) and all(len(v) == 2 for v in owners.values()) and all(by[n]["conversations"][0]["state_at_t"]["status"] == "resolved" for n in range(9, 25))
       and max(-offset(by[n]["conversations"][0]["timeline"][0]["day"]) for n in range(9, 25)) <= get("time.go_live_days"), owners)
    unclear = {d["number"]: d["scenario"]["unclear"] for d in docs if "unclear" in d["scenario"]}
    weds = [(cal.resolve({"kind": "weekday_of_week", "weekday": "Wed", "week": k}) - cal.t.date()).days for k in (13, 6, 2)]
    got_days = [offset(by[n]["conversations"][0]["timeline"][0]["day"]) for n in (25, 26, 27)]
    r27 = sims[(27, by[27]["conversations"][0]["key"])]["resolutions"]
    ok("unclear customers are in files %s and no other: S7's first chat (one question, as card S07 and ledger r13.story_items say) and the three R13 chats on the Wednesdays of weeks T-13, T-6 and T-2: clear after one question, after two, never; the third is resolved by nobody after 7 silent days"
       % sorted(unclear),
       sorted(unclear) == [1, 25, 26, 27] and (unclear[1]["loops"], unclear[1]["resolved"]) == (1, True) and (unclear[25]["loops"], unclear[25]["resolved"]) == (1, True)
       and (unclear[26]["loops"], unclear[26]["resolved"]) == (2, True) and unclear[27]["resolved"] is False and got_days == weds and r27 and r27[-1]["by"] is None
       and any("S7" in x and "once" in x for x in get("r13.story_items")), (unclear, got_days, weds))
    reasons = get("conv.reasons")["reasons"]
    short = lambda r: r.split(":")[0].strip()
    bad = [d["id"] for d in docs if not any(short(d["truth"].get("reason", "")) == short(r) or short(d["truth"].get("reason", "")) in r for r in reasons) or not d["truth"].get("facts") or "outcome" not in d["truth"] or not d["why"]]
    ok("every file carries its truth for the golden set (a reason of the ledger's taxonomy conv.reasons, who handled it, the outcome, the facts an answer may rest on) and says what to look at", not bad, bad)
    tally = {}
    for d in docs:
        tally[short(d["truth"]["reason"])] = tally.get(short(d["truth"]["reason"]), 0) + 1
    say("        reasons in the set: " + "; ".join("%s %d" % kv for kv in sorted(tally.items(), key=lambda kv: -kv[1])))
    say()

    # ------------------------------------------------------------------------------------------------ 8
    say("8. The samples (conversations/samples): the story conversations there are copies of the files here")
    bad = []
    for n, pattern in SAMPLES.items():
        sp = os.path.join(CONV, "samples", pattern.format(l=cfg))
        src = [p for p in paths if os.path.basename(p).startswith("%02d-" % n)]
        if not os.path.exists(sp) or not src or open(sp, encoding="utf-8").read() != open(src[0], encoding="utf-8").read():
            bad.append("%s is not a copy of %s" % (os.path.basename(sp), os.path.basename(src[0]) if src else "?"))
    extra = [os.path.basename(p) for p in glob.glob(os.path.join(CONV, "samples", cfg + "-*.json")) if os.path.basename(p) not in {v.format(l=cfg) for v in SAMPLES.values()}]
    ok("samples/%s-1, -2, -3, -4a and -4b are byte for byte files 01, 04, 06, 07 and 08 of this folder, and no other %s sample is left" % (cfg, cfg), not bad and not extra, bad + extra)
    say()

    n_lines = sum(len(c["timeline"]) for d in docs for c in d["conversations"])
    n_pub = sum(1 for d in docs for c in d["conversations"] for it in c["timeline"] if it["kind"] == "message")
    say("%d conversations, %d timeline lines, %d public messages, %d drafts, %d hand-offs; %d checks failed." % (len(docs), n_lines, n_pub, n_drafts, n_hand, len(FAILS)))
    say("RESULT " + ("PASS" if not FAILS else "FAIL"))
    print("\n".join(OUT))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
