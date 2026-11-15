#!/usr/bin/env python3
"""Builds the Russian conversation bank (../*.json) from the text sources beside this file.

Run: python3 build.py. The sources are plain text so that a native reader can edit a line
without touching JSON. Format of the output: ../FORMAT.md.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

CH = {"w": "web", "t": "telegram", "v": "vk", "a": "avito"}
ALL_CH = ["web", "telegram", "vk", "avito"]
REASON_KEY = {"found": "found_work"}

# The numbers of ../DESIGN.md section 4 (ledger rows conv.draft_outcomes, pNN.first_reply_min,
# conv.unclear, conv.label_share, conv.resolved_by_person).
SHEET = {
    "5": {"draft_outcomes": [50, 10, 40], "first_reply_min": 14, "ask_chance": 75, "label_share": 50, "resolve_share": 50},
    "6": {"draft_outcomes": [45, 40, 15], "first_reply_min": 4, "ask_chance": 85, "label_share": 95, "resolve_share": 85},
    "7": {"draft_outcomes": [70, 15, 15], "first_reply_min": 9, "ask_chance": 45, "label_share": 50, "resolve_share": 60},
    "29": {"draft_outcomes": [30, 20, 50], "first_reply_min": 12, "ask_chance": 80, "label_share": 50, "resolve_share": 55},
    "16": {"draft_outcomes": [20, 60, 20], "first_reply_min": 6, "ask_chance": 95, "label_share": 95, "resolve_share": 80},
    "17": {"draft_outcomes": [40, 25, 35], "first_reply_min": 11, "ask_chance": 60, "label_share": 50, "resolve_share": 45},
    "22": {"draft_outcomes": [5, 5, 90], "first_reply_min": 35, "ask_chance": 25, "label_share": 5, "resolve_share": 10, "curt": True},
    "23": {"draft_outcomes": [15, 5, 80], "first_reply_min": 40, "ask_chance": 30, "label_share": 5, "resolve_share": 15, "curt": True},
    "24": {"draft_outcomes": [35, 50, 15], "first_reply_min": 7, "ask_chance": 85, "label_share": 95, "resolve_share": 80},
}

# The twelve moves of section 5 that are also a reply to a reason repeat that reply's first three wordings.
MOVE_FROM_REPLY = {
    "price": "price.quote", "offer_time": "booking.offer", "confirm": "booking.confirm",
    "not_yet": "status.not_yet", "moved": "moving.moved", "found_work": "found_work.present",
    "decline_discount": "price.objection",
}

GENERIC_ALIAS = {"generic.coming": "generic.close_coming", "generic.thanks_after": "generic.thanks"}
DECISION = {"yes": "approve", "one": "partial", "ask": "question", "no": "decline"}
INTENT = {"move": "move", "cancel": "cancel", "late": "late"}

# Per reason: the tenant's label, the share of sessions by channel, the share the assistant ends alone on the
# web chat and the weight of an unclear customer (../DESIGN.md section 4; ledger conv.reasons, conv.unclear).
REASON_META = {
    "price": {"label": "цена", "shares": {"web": 30, "telegram": 20, "vk": 24, "avito": 42}, "alone_on_web": 60, "unclear_weight": 1.3},
    "booking": {"label": "запись", "shares": {"web": 22, "telegram": 22, "vk": 22, "avito": 20}, "alone_on_web": 20, "unclear_weight": 1.3},
    "hours": {"label": None, "shares": {"web": 16, "telegram": 6, "vk": 12, "avito": 14}, "alone_on_web": 95, "unclear_weight": 0.3},
    "symptom": {"label": "запись", "shares": {"web": 12, "telegram": 10, "vk": 12, "avito": 8}, "alone_on_web": 35, "unclear_weight": 1.6},
    "status": {"label": "статус", "shares": {"web": 5, "telegram": 18, "vk": 8, "avito": 2}, "alone_on_web": 0, "unclear_weight": 0.5},
    "found_work": {"label": "согласование", "shares": {"web": 2, "telegram": 12, "vk": 6, "avito": 0}, "alone_on_web": 0, "unclear_weight": 1.0},
    "moving": {"label": "запись", "shares": {"web": 4, "telegram": 6, "vk": 6, "avito": 2}, "alone_on_web": 0, "unclear_weight": 1.0},
    "complaint": {"label": "жалоба", "shares": {"web": 4, "telegram": 4, "vk": 6, "avito": 4}, "alone_on_web": 0, "unclear_weight": 0.0},
    "fleet": {"label": "юрлицо", "shares": {"web": 2, "telegram": 2, "vk": 0, "avito": 6}, "alone_on_web": 0, "unclear_weight": 0.0},
    "spam": {"label": None, "shares": {"web": 3, "telegram": 0, "vk": 4, "avito": 2}, "alone_on_web": 100, "unclear_weight": 0.0},
}

# What the one who asked says last when the customer never makes it clear, by kind of loop.
NEVER = {
    "vague": ["Если напишете, что именно происходит с машиной, подскажу, какая услуга нужна.",
              "Опишите, пожалуйста, чуть подробнее, когда сможете: без этого я не пойму, чем помочь.",
              "Буду на связи, если решите уточнить."],
    "wrong": ["Когда уточните, о какой работе речь, назову цену.",
              "Если подскажете подробности, отвечу точнее.",
              "Напишите, когда будет удобно, и разберёмся, что именно нужно."],
    "two": ["Напишите, с чего начать, и я передам заявку.",
            "Когда решите, что делаем в первую очередь, запишем.",
            "Если уточните, какие работы нужны, подскажу по каждой."],
    "reversed": ["Уточните, пожалуйста, когда сможете: не хочу записать вас не туда.",
                 "Если напишете, как правильно, всё поправим.",
                 "Жду вашего ответа, без него ничего менять не буду."],
}

# Drafts that promise an answer («уточню и напишу»): sent as they are, the person's own answer follows them.
DEFERS = {"status.dont_have", "status.part", "status.sorry_wait", "status.total", "found_work.can_wait", "found_work.total",
          "complaint.service"}

JOB_SHORT = {
    "oil_change": "замена масла с фильтром", "seasonal_tyres": "переобувка, четыре колеса с балансировкой",
    "wheel_swap": "перекидка колёс в сборе", "tyre_storage": "хранение комплекта", "alignment": "сход-развал",
    "balance": "балансировка, четыре колеса", "puncture": "ремонт прокола", "brake_check": "диагностика тормозов",
    "front_pads": "передние колодки с заменой", "front_pads_discs": "передние диски с колодками",
    "suspension_check": "диагностика ходовой", "sway_links": "стойки стабилизатора, пара",
    "struts": "передние стойки, пара", "rear_shocks": "задние амортизаторы, пара",
    "wheel_bearing": "ступичный подшипник", "cv_joint": "наружный шрус", "clutch": "сцепление в сборе",
    "check_engine": "компьютерная диагностика", "battery": "аккумулятор с установкой",
    "ac_recharge": "заправка кондиционера", "timing_belt": "ремень грм с роликами и помпой",
    "coolant_leak": "замена помпы", "scheduled": "то по регламенту", "pre_purchase": "диагностика перед покупкой",
}

# First steps that are not among the 24 job blocks.
EXTRA_STEPS = [
    {"key": "battery_test", "catalogue": "battery_test", "staff_says": {"nom": "проверка аккумулятора и системы зарядки", "acc": "проверку аккумулятора"},
     "page": "customers/prices-for-common-services", "page_item": "Проверка аккумулятора и системы зарядки"},
    {"key": "ac_check", "catalogue": "ac_performance_check", "staff_says": {"nom": "диагностика кондиционера", "acc": "диагностику кондиционера"},
     "page": "customers/prices-for-common-services", "page_item": "Диагностика кондиционера"},
    {"key": "cooling_test", "catalogue": "cooling_pressure_test", "staff_says": {"nom": "опрессовка системы охлаждения", "acc": "опрессовку системы охлаждения"},
     "page": "prices/price-list", "page_item": "Опрессовка системы охлаждения, поиск утечки"},
]

# For an unclear loop: the job the first reading (level 0) prices. A job block, a step, or catalogue:<key>.
GUESS_JOB = {
    "vague-knock": "suspension_check", "vague-drives-wrong": "alignment", "vague-look-at-it": "suspension_check",
    "vague-as-usual": "scheduled", "vague-how-much-repair": None, "vague-drip": "cooling_test",
    "vague-sound": "suspension_check", "wrong-alignment-balance": "alignment", "wrong-battery-starter": "battery",
    "wrong-coolant-change": "catalogue:coolant_exchange", "wrong-bleed-brakes": "catalogue:brake_fluid_exchange",
    "wrong-which-oil": "oil_change", "wrong-tyres-or-wheels": "seasonal_tyres", "wrong-pads-which": "catalogue:rear_brake_pads",
    "two-oil-and-knock": "oil_change", "two-tyres-and-pads": "seasonal_tyres", "two-service-and-ac": "scheduled",
    "two-check-and-service": "scheduled", "reversed-cancel-move": None, "reversed-pickup-dropoff": None,
    "reversed-season": "seasonal_tyres", "reversed-earlier-later": None,
}


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f]


def sections(lines):
    """Yields (header, [lines]) for every @section; comment and blank lines are dropped, except
    that a blank line is kept as '' inside @edit (an empty 'sent' means the draft was cleared)."""
    head, body = None, []
    for ln in lines:
        if ln.startswith("#"):
            continue
        if ln.startswith("@"):
            if head is not None:
                yield head, body
            head, body = ln[1:].strip(), []
        elif head is not None:
            body.append(ln)
    if head is not None:
        yield head, body


def meta(text):
    """'text @@ k=v; flag' -> (text, {k: v, flag: True})."""
    if " @@ " not in text:
        return text.strip().replace("\\n", "\n"), {}
    t, m = text.split(" @@ ", 1)
    out = {}
    for part in re.split(r";\s*|\s+(?=[a-z_.]+=)|\s+(?=[a-z]+$)", m.strip()):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[part] = True
    return t.strip().replace("\\n", "\n"), out


def meta_semicolon(text):
    """Assistant lines: metadata split on ';' only, because quoted values hold spaces."""
    if " @@ " not in text:
        return text.strip().replace("\\n", "\n"), {}
    t, m = text.split(" @@ ", 1)
    out = {}
    for part in m.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[part] = True
    return t.strip().replace("\\n", "\n"), out


def channels(code):
    code = code.strip()
    if code == "*":
        return list(ALL_CH)
    return [CH[c] for c in code]


def rkey(k):
    """found.x -> found_work.x"""
    head, _, tail = k.partition(".")
    head = REASON_KEY.get(head, head)
    return head + ("." + tail if tail else "")


def entry(text, m):
    """A pool entry: a plain string, or an object when it carries gender, a burst or a restriction."""
    keep = {k: v for k, v in m.items() if k in ("g", "only", "kind")}
    if "\n" in text:
        keep["burst"] = True
    if not keep:
        return text
    return dict({"text": text}, **keep)


# ---------------------------------------------------------------- declension
def decline(word, cls):
    def last(fn):
        parts = word.split(" ")
        parts[-1] = fn(parts[-1])
        return " ".join(parts)
    if cls == "0":
        return dict.fromkeys(["nom", "acc", "gen", "dat", "prep"], word)
    if cls == "a":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": s("у"), "gen": s("ы"), "dat": s("е"), "prep": s("е")}
    if cls == "ka":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": s("у"), "gen": s("и"), "dat": s("е"), "prep": s("е")}
    if cls == "ya":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": s("ю"), "gen": s("и"), "dat": s("и"), "prep": s("и")}
    if cls == "c":
        s = lambda e: last(lambda w: w + e)
        return {"nom": word, "acc": word, "gen": s("а"), "dat": s("у"), "prep": s("е")}
    if cls == "c_j":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": word, "gen": s("я"), "dat": s("ю"), "prep": s("е")}
    if cls == "fem":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": word, "gen": s("и"), "dat": s("и"), "prep": s("и")}
    if cls == "masc_soft":
        s = lambda e: last(lambda w: w[:-1] + e)
        return {"nom": word, "acc": word, "gen": s("я"), "dat": s("ю"), "prep": s("е")}
    if cls == "adj_f":
        s = lambda e: last(lambda w: w[:-2] + e)
        return {"nom": word, "acc": s("ую"), "gen": s("ой"), "dat": s("ой"), "prep": s("ой")}
    raise SystemExit("unknown declension %r for %r" % (cls, word))


GENDER = {"a": "f", "ka": "f", "ya": "f", "fem": "f", "adj_f": "f", "c": "m", "c_j": "m", "masc_soft": "m", "0": None}


def forms(spec):
    word, _, cls = spec.strip().rpartition(":")
    d = decline(word, cls)
    d["gender"] = GENDER[cls]
    return d


# ---------------------------------------------------------------- customer-messages.json
def build_customer():
    out = {"format": "bank-ru/customer-messages/1"}
    reasons, generic, formsd = {}, {}, {}
    jobs, findings, pictures, stubs, voices = [], [], [], [], []
    for head, body in sections(read("customer.txt")):
        body = [b for b in body if b.strip()]
        kind, _, arg = head.partition(" ")
        if kind == "about":
            out["about"] = " ".join(body)
        elif kind == "voices":
            for b in body:
                k, says, habits = [x.strip() for x in b.split(" | ")]
                voices.append({"key": k, "says": says, "habits": [h.strip() for h in habits.split(";")]})
        elif kind == "findings":
            for b in body:
                k, cat, text, fix, said, why, photo = [x.strip() for x in b.split(" | ")]
                findings.append({"key": k, "catalogue": cat, "finding": text, "fix": fix, "said": said, "why": why, "photo": photo})
        elif kind == "jobs":
            cur = None
            for b in body:
                if b.startswith("= "):
                    k, cat, pk, page, item, step, advice = [x.strip() for x in b[2:].split(" | ")]
                    cur = {"key": k, "catalogue": cat, "price_kind": pk, "page": page, "page_item": item,
                           "first_step": None if step == "-" else step, "advice": None if advice == "none" else advice,
                           "short": JOB_SHORT[k]}
                    jobs.append(cur)
                else:
                    f, _, v = b.partition(":")
                    v = v.strip()
                    if f == "staff":
                        nom, acc = [x.strip() for x in v.split(" | ")]
                        cur["staff_says"] = {"nom": nom, "acc": acc}
                    elif f == "listing":
                        cur["listing"] = v
                    else:
                        name = {"said": "said", "inf": "said_inf", "acc": "said_acc", "symptom": "symptom_said",
                                "photo": "photo", "finding": "finding"}[f]
                        cur[name] = [x.strip() for x in v.split(";") if x.strip() and x.strip() != "-"]
        elif kind == "pictures":
            for b in body:
                k, by, shows = [x.strip() for x in b.split(" | ")]
                pictures.append({"key": k, "by": by, "shows": shows})
        elif kind == "stubs":
            for b in body:
                k, sec, said = [x.strip() for x in b.split(" | ")]
                stubs.append({"key": k, "len": "{voice_len}", "seconds": int(sec), "said": said,
                              "g": {"voice-stub-ru-1": "f", "voice-stub-ru-2": "m", "voice-stub-ru-3": "m", "voice-stub-ru-5": "m", "voice-stub-ru-6": "f"}.get(k)})
        elif kind == "open":
            reason, _, okind = arg.partition(".")
            reason = REASON_KEY.get(reason, reason)
            lst = reasons.setdefault(reason, {}).setdefault("open", [])
            for b in body:
                voice, ch, rest = [x.strip() for x in b.split(" | ", 2)]
                text, m = meta(rest)
                e = {"text": text, "voice": voice, "ch": channels(ch)}
                if okind:
                    e["kind"] = okind
                    if reason == "found_work":
                        e["decision"] = DECISION[okind]
                    if reason == "moving":
                        e["intent"] = INTENT[okind]
                if "kind" in m:
                    e["kind"] = m["kind"]
                if reason == "spam" and "kind" not in e:
                    e["kind"] = "wrong"
                if "photo" in m:
                    e["photo"] = m["photo"]
                if m.get("two"):
                    e["two"] = True
                if "stub" in m:
                    e["voice_stub"] = m["stub"]
                    e["voice"] = "voice"
                if "g" in m:
                    e["g"] = m["g"]
                if "only" in m:
                    e["only"] = m["only"].split(",")
                if "\n" in text:
                    e["burst"] = True
                lst.append(e)
        elif kind == "part":
            reason, _, part = arg.partition(".")
            reason = REASON_KEY.get(reason, reason)
            lst = reasons.setdefault(reason, {}).setdefault(part, [])
            for b in body:
                lst.append(entry(*meta(b)))
        elif kind == "generic":
            lst = generic.setdefault({"coming": "close_coming", "thanks_after": "thanks"}.get(arg, arg), [])
            for b in body:
                lst.append(entry(*meta(b)))
        elif kind == "forms":
            if arg == "days":
                formsd["days"] = {}
                for b in body:
                    k, nom, on, for_, from_ = [x.strip() for x in b.split(" | ")]
                    formsd["days"][k] = {"nom": nom, "on": on, "for": for_, "from": from_}
            elif arg == "shops":
                formsd["shops"] = {}
                for b in body:
                    k, short, at, to, said, said_at, city = [x.strip() for x in b.split(" | ")]
                    formsd["shops"][k] = {"shop": short, "shop_at": at, "shop_to": to,
                                          "shop_said": [x.strip() for x in said.split(";")],
                                          "shop_said_at": [x.strip() for x in said_at.split(";")], "city": city}
            elif arg == "cars":
                formsd["cars"] = []
                for b in body:
                    make, model, latin, said, staff = [x.strip() for x in b.split(" | ")]
                    row = {"make": make, "parc_model": model, "model": latin,
                           "car_said": [forms(x) for x in said.split(";")]}
                    row["model_ru"] = None if staff == "-" else forms(staff)
                    formsd["cars"].append(row)
        else:
            raise SystemExit("customer.txt: unknown section " + head)
    steps = []
    for j in jobs:
        if j["key"] in ("brake_check", "suspension_check", "check_engine"):
            steps.append({"key": j["key"], "catalogue": j["catalogue"], "staff_says": j["staff_says"],
                          "page": j["page"], "page_item": j["page_item"]})
    steps += EXTRA_STEPS
    generic["close_defer"] = list(reasons["price"]["more"])
    out.update({"voices": voices, "jobs": jobs, "steps": steps, "findings": findings, "pictures": pictures,
                "voice_stubs": stubs, "reasons": reasons, "generic": generic, "forms": formsd})
    return out


# ---------------------------------------------------------------- assistant.json
def aline(b):
    text, m = meta_semicolon(b)
    e = {"text": text}
    if "page" in m:
        e["page"] = m["page"]
    q = {k[2:]: v for k, v in m.items() if k.startswith("q.")}
    if q:
        e["quote"] = q
    if m.get("echo"):
        e["echo"] = True
    if "for_shops" in m:
        e["for_shops"] = m["for_shops"].split(",")
    return e


def build_assistant():
    out = {"format": "bank-ru/assistant/1", "greetings": {}, "sends": {}, "handoff_notes": {}, "drafts": {}}
    for head, body in sections(read("assistant.txt")):
        body = [b for b in body if b.strip()]
        kind, _, arg = head.partition(" ")
        if kind == "about":
            out["about"] = " ".join(body)
        elif kind == "greet":
            out["greetings"][arg] = [aline(b) for b in body]
        elif kind == "send":
            out["sends"][arg] = [aline(b) for b in body]
        elif kind == "note":
            out["handoff_notes"][rkey(arg)] = [meta_semicolon(b)[0] for b in body]
        elif kind == "draft":
            reason, _, move = rkey(arg).partition(".")
            ls = [aline(b) for b in body]
            if rkey(arg) in DEFERS:
                for l in ls:
                    l["defers"] = True
            out["drafts"].setdefault(reason, {})[move] = ls
        else:
            raise SystemExit("assistant.txt: unknown section " + head)
    return out


# ---------------------------------------------------------------- advisors/<slot>.json
def build_advisors(assistant):
    adv = {}
    cur = None
    for name in ("advisors_main.txt", "advisors_east_west.txt", "advisors_extra.txt"):
        for head, body in sections(read(name)):
            kind, _, arg = head.partition(" ")
            lines = [b for b in body if b.strip()]
            if kind == "advisor":
                cur = adv.setdefault(arg, {"format": "bank-ru/advisor/1", "slot": arg, "signoff": [], "pickup": [],
                                           "replies": {}, "moves": {}, "edits": [], "notes": {}})
                for b in lines:
                    f, _, v = b.partition(":")
                    cur[f.strip()] = v.strip()
            elif kind in ("signoff", "pickup"):
                cur[kind] = [meta(b)[0] for b in lines]
            elif kind == "reply":
                cur["replies"][rkey(arg)] = [meta(b)[0] for b in lines]
            elif kind == "move":
                cur["moves"][arg] = [meta(b)[0] for b in lines]
            elif kind == "note":
                cur["notes"].setdefault(arg, []).extend(meta(b)[0] for b in lines)
            elif kind == "edit":
                fields = [x.strip() for x in arg.split(" | ")]
                ref, outcome = fields[0], fields[1]
                fits = rkey(fields[2].split("=", 1)[1]) if len(fields) > 2 else None
                key, _, idx = ref.partition("#")
                key = rkey(key)
                reason, _, move = key.partition(".")
                draft = assistant["drafts"][reason][move][int(idx)]["text"]
                if outcome == "sent_as_is":
                    sent = draft
                else:
                    sent = meta(lines[0])[0] if lines else None
                e = {"draft_key": key, "draft": draft, "sent": sent, "outcome": outcome}
                if fits:
                    e["fits"] = fits
                cur["edits"].append(e)
            else:
                raise SystemExit(name + ": unknown section " + head)
    for slot, a in adv.items():
        sh = SHEET[slot]
        a["sheet"] = {"draft_outcomes": dict(zip(["sent_as_is", "sent_edited", "discarded"], sh["draft_outcomes"])),
                      "first_reply_min": sh["first_reply_min"], "ask_chance": sh["ask_chance"],
                      "label_share": sh["label_share"], "resolves": sh["resolve_share"], "curt": bool(sh.get("curt")),
                      "no_price": slot == "22"}
        for move, src in MOVE_FROM_REPLY.items():
            a["moves"][move] = a["replies"][src][:3]
        nested = {}
        for key, v in a["replies"].items():
            reason, _, move = key.partition(".")
            nested.setdefault(reason, {})[move] = v
        a["replies"] = nested
        a["notes_by_key"] = a["notes"]
        a["notes"] = [t for v in a["notes"].values() for t in v]
        a["slot"] = int(slot)
        order = ["format", "slot", "name", "shop", "voice", "sheet", "signoff", "pickup", "replies", "moves", "edits", "notes", "notes_by_key"]
        adv[slot] = {k: a[k] for k in order}
    return adv


# ---------------------------------------------------------------- reasons.json
def kv(tokens):
    d = {}
    for t in tokens:
        k, _, v = t.partition("=")
        d[k] = v if _ else True
    return d


def num(v):
    return float("0" + v) if isinstance(v, str) and v.startswith(".") else float(v)


# Where a person-handled skeleton has no exchange point of its own, the build puts one after the first staff line
# and one before the closing turn (../DESIGN.md section 4: eleven public lines in a person-handled session).
EXTRA_KEYS = {
    "price": (["vat", "own_parts", "how_long"], ["address", "pay", "wait", "storage"]),
    "booking": (["how_long", "wait", "storage"], ["address", "pay"]),
    "symptom": (["how_long", "wait"], ["address", "pay"]),
    "status": (["total", "pay"], []),
    "moving": ([], ["address"]),
}


def add_extras(skel, reason):
    if skel["ends"] not in ("person", "handed_over") or reason not in EXTRA_KEYS or any(b["who"] == "extra" for b in skel["beats"]):
        return
    first, last = EXTRA_KEYS[reason]
    beats = skel["beats"]
    if first:
        seen_customer = False
        for i, b in enumerate(beats):
            if b["who"] == "customer":
                seen_customer = True
            if b["who"] == "staff" and seen_customer:
                beats.insert(i + 1, {"who": "extra", "keys": first, "p": 0.6})
                break
    if last:
        idx = None
        for i in range(len(beats) - 1, -1, -1):
            b = beats[i]
            if b["who"] == "customer" and b.get("use") in ("generic.close", "generic.ok", "generic.close_coming"):
                idx = i
                break
            if b["who"] == "staff":
                idx = i + 1
                break
        if idx is not None and beats[idx - 1]["who"] != "extra":
            beats.insert(idx, {"who": "extra", "keys": last, "p": 0.6})


def build_reasons():
    out = {"format": "bank-ru/reasons/1",
           "about": "Скелеты по причинам и каналам (../DESIGN.md, разделы 4 и 5). Ход берёт формулировку из своих alts и из названного пула. Чат на сайте ведёт ассистент до передачи заявки; в Telegram, во «ВКонтакте» и на Авито с первой строки отвечает человек, и на каждую реплику клиента ассистент готовит черновик. Один скелет может стоять в нескольких каналах под одним id.",
           "exchanges": {
               "vat": {"customer": "price.vat", "draft": "price.extras", "reply": "price.total"},
               "own_parts": {"customer": "price.own_parts", "draft": "price.own_parts", "reply": "price.own_parts", "kinds": ["list"]},
               "how_long": {"customer": "price.how_long", "draft": "price.how_long", "reply": "price.how_long"},
               "wait": {"customer": "booking.wait", "draft": "booking.wait", "reply": "booking.wait"},
               "total": {"customer": "status.total", "draft": "status.total", "reply": "price.total"},
               "storage": {"customer": "generic.ask_storage", "draft": "tyres.storage", "reply": "tyres.storage", "jobs": ["seasonal_tyres", "wheel_swap"]},
               "address": {"customer": "generic.ask_address", "draft": "hours.address", "reply": "hours.address"},
               "pay": {"customer": "generic.ask_pay", "draft": "hours.pay", "reply": "hours.pay"}},
           "reasons": {r: dict(m, skeletons={}) for r, m in REASON_META.items()}}
    counters = {}
    for name in ("reasons_web.txt", "reasons_msg.txt"):
        skel = None
        for ln in read(name):
            if not ln.strip() or ln.startswith("#"):
                continue
            if ln.startswith("= "):
                parts = [x.strip() for x in ln[2:].split(" | ")]
                reason, ch, ends, summary = parts[:4]
                reason = REASON_KEY.get(reason, reason)
                when = kv(parts[4].split()) if len(parts) > 4 else {}
                for k in ("kinds", "jobs", "advisors"):
                    if k in when:
                        when[k] = when[k].split(",")
                for k in ("advice", "two", "photo", "bigger"):
                    if k in when:
                        when[k] = True
                chs = channels(ch)
                n = counters[(reason, name)] = counters.get((reason, name), 0) + 1
                sid = "%s.%s.%d" % (reason, "web" if name == "reasons_web.txt" else "msg", n)
                skel = {"id": sid, "ends": ends, "summary": summary}
                if when:
                    skel["when"] = when
                skel["beats"] = []
                for c in chs:
                    out["reasons"][reason]["skeletons"].setdefault(c, []).append(skel)
                continue
            if ln.startswith("  | "):
                text, m = meta(ln[4:])
                skel["beats"][-1].setdefault("alts", []).append(entry(text, m))
                continue
            code, _, rest = ln.partition(" ")
            toks = rest.split()
            if code == "C":
                b = {"who": "customer"}
                if toks and "=" not in toks[0]:
                    use = toks.pop(0)
                    b["use"] = [GENERIC_ALIAS.get(rkey(u), rkey(u)) for u in use.split("+")] if "+" in use else GENERIC_ALIAS.get(rkey(use), rkey(use))
                a = kv(toks)
                for k in ("burst", "p"):
                    if k in a:
                        b[k] = num(a[k])
                for k in ("two", "photo", "stub"):
                    if k in a:
                        b[k] = True
                for k in ("kind", "voice", "if"):
                    if k in a:
                        b[k] = a[k]
            elif code == "A":
                b = {"who": "assistant", "use": toks[0].split("+")}
                a = kv(toks[1:])
                if "p" in a:
                    b["p"] = num(a["p"])
            elif code == "H":
                b = {"who": "handoff", "kind": toks[0], "note": rkey(toks[1])}
            elif code == "S":
                a = kv(toks)
                b = {"who": "staff"}
                if "draft" in a:
                    b["draft"] = rkey(a["draft"]) if not a["draft"].startswith("{") else a["draft"]
                if "reply" in a:
                    rr = [rkey(x) if "." in x else ("pickup" if x == "pickup" else "moves." + x) for x in a["reply"].split("+")]
                    b["reply"] = rr if len(rr) > 1 else rr[0]
                if "file" in a:
                    b["files"] = [a["file"]]
                if "force" in a:
                    b["draft_outcome"] = a["force"]
                if "reroll" in a:
                    b["reroll"] = True
                if "if" in a:
                    b["if"] = a["if"]
                if "p" in a:
                    b["p"] = num(a["p"])
            elif code == "N":
                a = kv(toks[1:])
                b = {"who": "note", "use": toks[0]}
                if "p" in a:
                    b["p"] = num(a["p"])
            elif code == "V":
                b = {"who": "activity", "what": toks[0]}
                if toks[0] == "label_added":
                    b["label"] = toks[1]
                elif toks[0] == "priority":
                    b["level"] = toks[1]
                a = kv(toks[2:])
                if "p" in a:
                    b["p"] = num(a["p"])
            elif code == "X":
                a = kv(toks[1:])
                b = {"who": "extra", "keys": toks[0].split(","), "p": num(a["p"]) if "p" in a else 0.5}
            elif code == "U":
                b = {"who": "unclear", "kinds": toks[0].split(",")}
            elif code == "E":
                b = {"who": "end", "how": toks[0]}
            else:
                raise SystemExit("%s: bad beat %r" % (name, ln))
            skel["beats"].append(b)
    done = set()
    for reason, spec in out["reasons"].items():
        for sks in spec["skeletons"].values():
            for sk in sks:
                if id(sk) not in done:
                    done.add(id(sk))
                    add_extras(sk, reason)
    return out


# ---------------------------------------------------------------- unclear.json
def build_unclear():
    loops, cur = [], None
    for ln in read("unclear.txt"):
        if not ln.strip() or ln.startswith("#"):
            continue
        if ln.startswith("= "):
            i, kind, reasons, job, reads = [x.strip() for x in ln[2:].split(" | ")]
            cur = {"id": i, "kind": kind, "reasons": [REASON_KEY.get(r, r) for r in reasons.split(",")],
                   "job": None if job == "-" else job, "guess_job": GUESS_JOB[i], "reads": reads}
            loops.append(cur)
            continue
        f, _, v = ln.partition(":")
        vals = [x.strip() for x in v.split(" ; ")]
        cur[f.strip()] = vals
    out, seen = [], {}
    for c in loops:
        n = seen[c["kind"]] = seen.get(c["kind"], 0) + 1
        out.append({
            "id": c["id"], "kind": c["kind"], "reasons": c["reasons"], "job": c["job"], "guess_job": c["guess_job"],
            "reads": c["reads"], "open": c["open"],
            "second_unclear": c["unclear"], "second_clear": c["clear"], "second_to_guess": c["guess"],
            "third": c["third"],
            "ask": {"level_0": c["l0"], "level_1": c["l1"], "level_2": c["l2"]},
            "endings": {"after_one": c["ack"][0], "after_two": c["ack"][0],
                        "never": NEVER[c["kind"]][(n - 1) % len(NEVER[c["kind"]])]},
            "never_customer": c["never"][0] if c.get("never") and c["never"][0] else None,
        })
    return {"format": "bank-ru/unclear/1",
            "about": "Правило R13 для чатов: в 12 % сессий есть петля уточнения, в 4 % их две, 3 % сессий так и остаются неясными. Петля — свойство клиента; что с ней делает приёмщик, решает его ask_chance. Ассистент спрашивает уровень 1, потом уровень 2 и не угадывает ни работу, ни цену.",
            "loops": out}


# ---------------------------------------------------------------- labels-and-notes.json
def build_notes(advisors):
    out = {"format": "bank-ru/labels-and-notes/1",
           "about": "Сотрудники пишут друг другу внутри чата, и короткие строки, которые оставляют ярлыки и приоритет. У заметки есть ключ и слот автора: генератор берёт заметку того, кто ведёт чат.",
           "notes": [], "acks": [],
           "labels": {"available": [], "product": "handoff",
                      "by_reason": {r: m["label"] for r, m in REASON_META.items()},
                      "tires_instead": "когда работа — seasonal_tyres, wheel_swap, tyre_storage, puncture, balance или alignment, ярлык «шины» заменяет «цена» или «запись»",
                      "when": "ставит тот, кто ведёт чат, после своего ответа и до закрытия; чат о симптоме получает «запись», только если договорились о времени",
                      "handoff": "ярлык handoff ставит продукт при передаче заявки, и его снимает первый ответ человека; банк для него строк не пишет",
                      "use": []},
           "priority": {"base_shares": {"high": 4, "urgent": 0.5, "low": 1}, "patterns": [],
                        "by_wait": "всё остальное двигает ожидание, как его считает продукт; банк таких строк не пишет"}}
    reasons_of = {"ask_colleague": ["price", "booking", "found_work"], "next_shift": ["booking", "status", "fleet"],
                  "to_manager": ["complaint", "status"], "price_basis": ["price"], "callback": ["status", "price"],
                  "voice_heard": ["symptom", "booking", "status"], "draft_wrong": ["any"], "unclear_note": ["any"],
                  "no_show": ["booking", "moving"], "shop_other": ["any"]}
    for slot in sorted(advisors, key=int):
        for key, texts in advisors[slot]["notes_by_key"].items():
            for t in texts:
                out["notes"].append({"key": key, "reasons": reasons_of[key], "slot": int(slot), "text": t})
    for head, body in sections(read("notes.txt")):
        body = [b for b in body if b.strip()]
        for b in body:
            p = [x.strip() for x in b.split(" | ")]
            if head == "labels":
                out["labels"]["available"].append(p[0])
                out["labels"]["use"].append({"label": p[0], "reasons": p[1].split(","), "when": p[2]})
            elif head == "priority":
                out["priority"]["patterns"].append({"level": p[0], "reasons": p[1].split(","), "by": p[2], "when": p[3],
                                                    "note_with_it": "to_manager" if p[0] != "low" else None})
            elif head == "acks":
                out["acks"].append({"slot": int(p[0]), "text": p[1]})
            elif head == "extra_notes":
                out["notes"].append({"key": p[0], "reasons": reasons_of[p[0]], "slot": int(p[1]), "text": p[2]})
    return out


def dump(path, obj):
    with open(os.path.join(OUT, path), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    customer = build_customer()
    assistant = build_assistant()
    advisors = build_advisors(assistant)
    reasons = build_reasons()
    unclear = build_unclear()
    notes = build_notes(advisors)
    dump("customer-messages.json", customer)
    dump("assistant.json", assistant)
    os.makedirs(os.path.join(OUT, "advisors"), exist_ok=True)
    for slot, a in advisors.items():
        a = {k: v for k, v in a.items() if k != "notes_by_key"}
        dump(os.path.join("advisors", slot + ".json"), a)
    dump("reasons.json", reasons)
    dump("unclear.json", unclear)
    dump("labels-and-notes.json", notes)
    print("built: %d jobs, %d openings, %d assistant moves, %d advisors, %d skeleton slots, %d loops, %d notes" % (
        len(customer["jobs"]), sum(len(r.get("open", [])) for r in customer["reasons"].values()),
        len(assistant["sends"]), len(advisors),
        sum(len(v) for r in reasons["reasons"].values() for v in r["skeletons"].values()), len(unclear["loops"]),
        len(notes["notes"])))


if __name__ == "__main__":
    sys.exit(main())
