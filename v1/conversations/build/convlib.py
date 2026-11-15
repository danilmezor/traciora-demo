#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""How the hand-written story conversations of conversations/en and conversations/ru were first set down.

The JSON files are the source of record. This library exists so that the parts of a file that follow from its
lines (numbering, the activity lines the product writes by itself, draft outcomes, waits in working minutes, the
state at T) are computed once and the same way in every file. `python3 build.py` writes both folders again from
src_en.py and src_ru.py; a JSON file edited by hand afterwards is not read back. Not product code.
"""
import datetime as dt
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, "..", ".."))
NOMINAL = dt.datetime(2026, 11, 13, 10, 30)
ZONE = {"en": "America/New_York", "ru": "Europe/Ulyanovsk"}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
EN_CLOSED = {dt.date(2026, 5, 25), dt.date(2026, 7, 3), dt.date(2026, 9, 7), dt.date(2026, 11, 26)}
PHASE = {"A": (5, 7, 16, 23), "B": (6, 29, 17, 24)}
RU_MANAGERS = (3, 4, 8, 9, 22)
THRESHOLDS = {"first": (12, 36), "later": (24, 72)}
BRIDGE = {"chat": ("chat:default", "Chat", "sends"), "telegram": ("telegram:default", "Telegram", "drafts"),
          "vk": ("vk:default", "VK", "drafts"), "avito": ("avito:default", "Avito", "drafts")}

CAT = json.load(open(os.path.join(SEED, "catalogue.json"), encoding="utf-8"))
JOBS = {j["key"]: j for j in CAT["jobs"]}


# ------------------------------------------------------------------------------------------------ the calendar
def closed(cfg, d):
    return d in EN_CLOSED if cfg == "en" else (d.month, d.day) in ((1, 1), (1, 2))


def full_open(cfg, d):
    return not closed(cfg, d) and (cfg == "ru" or d.weekday() < 5)


def hours(cfg, site, d):
    """Opening and closing of a site on a date, in minutes of its own wall clock; None when closed."""
    if closed(cfg, d):
        return None
    if cfg == "ru":
        return (9 * 60, 20 * 60)
    if d.weekday() < 5:
        return (7 * 60 + 30, 17 * 60 + 30)
    if d.weekday() == 5 and site == "main":
        return (8 * 60, 13 * 60)
    return None


def works(cfg, slot, d):
    if cfg == "en":
        return full_open(cfg, d)
    if closed(cfg, d):
        return False
    if slot in RU_MANAGERS:
        return d.weekday() < 5
    n = (d - NOMINAL.date()).days % 4
    return n in ((2, 3) if slot in PHASE["A"] else (0, 1))


def t_at(site):
    """T on the wall clock of a site: the bought shop is one hour behind the business zone."""
    return NOMINAL - dt.timedelta(hours=1) if site == "west" else NOMINAL


def working_minutes(cfg, site, a, b):
    if b <= a:
        return 0.0
    total, d = 0.0, a.date()
    while d <= b.date():
        h = hours(cfg, site, d)
        if h:
            lo = max(a, dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[0]))
            hi = min(b, dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[1]))
            if hi > lo:
                total += (hi - lo).total_seconds() / 60
        d += dt.timedelta(days=1)
    return total


def add_working(cfg, site, a, minutes):
    """The instant at which `minutes` working minutes have passed since a."""
    d, left = a.date(), minutes
    for _ in range(40):
        h = hours(cfg, site, d)
        if h:
            lo = max(a, dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[0]))
            hi = dt.datetime.combine(d, dt.time()) + dt.timedelta(minutes=h[1])
            if hi > lo:
                span = (hi - lo).total_seconds() / 60
                if span >= left:
                    return lo + dt.timedelta(minutes=left)
                left -= span
        d += dt.timedelta(days=1)
    raise ValueError("no working time")


def is_open(cfg, site, a):
    h = hours(cfg, site, a.date())
    m = a.hour * 60 + a.minute + a.second / 60
    return bool(h) and h[0] <= m < h[1]


# ------------------------------------------------------------------------------------------------ anchors (rule R6)
def week_monday(k):
    """Monday of the ISO week k weeks before the week of T (negative k: after)."""
    t = NOMINAL.date()
    return t - dt.timedelta(days=t.weekday()) - dt.timedelta(weeks=k)


def resolve(cfg, rule):
    kind = rule["kind"]
    if kind == "T":
        d = NOMINAL.date()
    elif kind == "calendar":
        d = NOMINAL.date() + dt.timedelta(days=rule["days"])
    elif kind == "weekday_of_week":
        d = week_monday(rule["week"]) + dt.timedelta(days=WEEKDAYS.index(rule["weekday"]))
        while closed(cfg, d):
            d += dt.timedelta(days=1)
        if rule.get("on_or_after_for_slot"):
            while not works(cfg, rule["on_or_after_for_slot"], d):
                d += dt.timedelta(days=1)
    elif kind == "slot_working_day":
        d, n, step = NOMINAL.date(), abs(rule["n"]), (1 if rule["n"] > 0 else -1)
        while n:
            d += dt.timedelta(days=step)
            if works(cfg, rule["slot"], d):
                n -= 1
    elif kind == "open_day":
        d, n, step = NOMINAL.date(), abs(rule["n"]), (1 if rule["n"] > 0 else -1)
        while n:
            d += dt.timedelta(days=step)
            if full_open(cfg, d):
                n -= 1
        if rule.get("snap_back"):
            pass
    else:
        raise ValueError(kind)
    return d + dt.timedelta(days=rule.get("plus_days", 0))


def label(d):
    n = (d - NOMINAL.date()).days
    return "T" if n == 0 else ("T%+dd" % n)


def ordinal(n):
    return {1: "last", 2: "2nd", 3: "3rd"}.get(n, "%dth" % n)


def T():
    return ("T's date", {"kind": "T"})


def cal(n, why="calendar days, as the card states them"):
    return ("%d calendar days %s T (%s)" % (abs(n), "before" if n < 0 else "after", why), {"kind": "calendar", "days": n})


def wk(weekday, k, slot=None, plus=0, note=None):
    name = {"Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"}[weekday]
    week = "W0" if k == 0 else ("T-%d" % k if k > 0 else "W+%d" % -k)
    text = "the %s of week %s" % (name, week)
    rule = {"kind": "weekday_of_week", "weekday": weekday, "week": k}
    if slot:
        text = "slot %d's first working day on or after %s" % (slot, text)
        rule["on_or_after_for_slot"] = slot
    if plus:
        text = "%d calendar day%s %s %s" % (abs(plus), "" if abs(plus) == 1 else "s", "after" if plus > 0 else "before", text)
        rule["plus_days"] = plus
    if note:
        text += " (%s)" % note
    return (text, rule)


def wd(slot, n, plus=0, note=None):
    text = "slot %d's %s working day %s T" % (slot, ordinal(abs(n)), "before" if n < 0 else "after")
    rule = {"kind": "slot_working_day", "slot": slot, "n": n}
    if plus:
        text = "%d calendar day%s %s %s" % (abs(plus), "" if abs(plus) == 1 else "s", "after" if plus > 0 else "before", text)
        rule["plus_days"] = plus
    if note:
        text += " (%s)" % note
    return (text, rule)


def od(site, n, plus=0, note=None):
    text = "%s's %s full open day %s T" % (site, ordinal(abs(n)), "before" if n < 0 else "after")
    rule = {"kind": "open_day", "site": site, "n": n}
    if plus:
        text = "%d calendar day%s %s %s" % (abs(plus), "" if abs(plus) == 1 else "s", "after" if plus > 0 else "before", text)
        rule["plus_days"] = plus
    if note:
        text += " (%s)" % note
    return (text, rule)


# ------------------------------------------------------------------------------------------------ prices
def price(cfg, job, cls="car", tier="standard", klass="list", supplies=False, tax=False):
    """A job's price today from catalogue.json: list or company-account class, optionally with shop supplies and tax."""
    j = JOBS[job][cfg]
    conf = CAT["configurations"][cfg]
    hm = (j.get("hours_by_class") or {}).get(cls, 1) if j.get("hours_by_class") else 1
    lab = (j["labour_price_company"] if klass == "company" else j["labour_price"])["after_rise"] * hm
    pm = conf["parts_class_multiplier"][cls] if j.get("parts_scale_with_class") else 1
    parts = 0.0
    for p in j["parts"]:
        opts = {o["tier"]: o for o in p["options"] if not o.get("story")}
        o = opts.get(tier) or opts.get("standard") or list(opts.values())[0]
        parts += o["list_price"] * p["qty"] * pm
    fees = sum(f.get("price", 0) for f in j.get("fees", []))
    sub = (j.get("sublet") or {}).get("price", 0) if j.get("usually_sublet") else 0
    other = parts + fees + sub
    if klass == "company":
        other *= 0.9
    total = lab + other
    if supplies and j.get("shop_supplies"):
        total += round(lab * conf["shop_supplies"]["rate_of_hourly_labour"], 2)
    if tax:
        total *= 1 + conf["tax"]["rate"]
    return round(total + 1e-9, 2)


def usd(x):
    return "$%s" % ("{:,.2f}".format(x))


def rub(x, sep=" "):
    s = "{:,.2f}".format(x) if abs(x - round(x)) > 0.004 else "{:,}".format(int(round(x)))
    return s.replace(",", sep).replace(".", ",") if sep != "," else s


# ------------------------------------------------------------------------------------------------ a conversation
class Conv:
    def __init__(self, f, key, channel, site, thread_key, peer_id, peer_name, phone=None, avatar=None, clock=None, extra=None, opened_note=None):
        self.f, self.key, self.channel, self.site = f, key, channel, site
        self.thread_key, self.peer_id, self.peer_name, self.phone = thread_key, peer_id, peer_name, phone
        self.avatar = avatar if avatar is not None else {"has": False, "why": "website visitors have no picture"} if channel == "chat" else {"has": False}
        self.clock, self.extra, self.opened_note = clock or site, extra or {}, opened_note
        self.items, self.day, self.seq = [], None, 0
        self.state_extra, self.reads_extra = {}, {}

    # -- time
    def when(self, at):
        if " " in at:
            day, at = at.split(" ")
            self.day = day
        n = 0 if self.day == "T" else int(self.day[1:-1])
        parts = [int(x) for x in at.split(":")]
        while len(parts) < 3:
            parts.append(0)
        d = NOMINAL.date() + dt.timedelta(days=n)
        return dt.datetime.combine(d, dt.time(parts[0], parts[1], parts[2])), at

    def add(self, at, kind, **kw):
        t, shown = self.when(at)
        self.seq += 1
        it = {"t": t, "seq": self.seq, "day": self.day, "at": shown, "kind": kind}
        it.update(kw)
        self.items.append(it)
        return it

    # -- what the author writes
    def c(self, at, text, files=None):
        return self.add(at, "message", **{"from": "customer", "text": text, **({"files": files} if files else {})})

    def a(self, at, text):
        return self.add(at, "message", **{"from": "assistant", "text": text})

    def s(self, slot, at, text, files=None, use=None, edit=None, late=None):
        kw = {"from": "staff", "slot": slot, "text": text}
        if files:
            kw["files"] = files
        it = self.add(at, "message", **kw)
        it["_use"], it["_edit"], it["_late"] = use, edit, late
        return it

    def n(self, slot, at, text, mentions=None):
        kw = {"from": "staff", "slot": slot}
        if mentions:
            kw["mentions"] = mentions
        kw["text"] = text
        return self.add(at, "note", **kw)

    def d(self, at, did, text, clear=None):
        it = self.add(at, "draft", id=did, text=text)
        it["_clear"] = clear  # (slot, "at") when a person clears it without sending anything
        return it

    def h(self, at, typ, name, phone, site_words, context, card_site, due):
        tool = {"name": "forward_to_manager", "type": typ, "arguments": {"name": name, "phone": phone, "site": site_words, "context": context}}
        card = {"template": "Customer handover", "kind": "task" if typ == "scheduling" else "escalation",
                "priority": "normal" if typ == "scheduling" else "high", "site": card_site, "owner": None, "due": due}
        return self.add(at, "handoff", tool=tool, note={"from": "assistant", "private": True, "text": context},
                        label_added="handoff", status="pending -> open", card=card)

    def act(self, at, what, **kw):
        return self.add(at, "activity", what=what, **kw)

    def label(self, slot, at, name):
        return self.act(at, "label_added", label=name, by=slot)

    def prio(self, slot, at, level):
        return self.act(at, "priority", **{"from": "normal", "to": level, "by": slot, "how": "set by a manager: the base level"})

    def res(self, slot, at):
        return self.act(at, "resolved", by=slot)

    def auto(self):
        """Chatwoot resolves the chat seven days after its last line."""
        last = max(i["t"] for i in self.items if i["kind"] in ("message", "note"))
        t = last + dt.timedelta(days=7)
        self.day = label(t.date())
        return self.act(t.strftime("%H:%M"), "resolved", by=None, how="7 silent days")

    def out(self, at, store, what):
        return self.add(at, "outside", store=store, what=what)

    # -- what follows from the lines
    def build(self):
        cfg, f = self.f.cfg, self.f
        bridge, inbox, mode = BRIDGE[self.channel]
        base_items = sorted(self.items, key=lambda i: (i["t"], i["seq"]))
        out, owner, labels, status = [], None, [], None
        base, raised, history = "normal", "normal", []
        drafts_state = mode == "drafts"
        box = None  # the draft in the reply box
        wait_start, person_replied, session_person = None, False, False
        resolutions, first_item = [], base_items[0]
        status = "pending" if mode == "sends" else "open"
        opened_status = status
        extra_seq = [0]

        def emit(it):
            out.append(it)

        def auto_act(t, what, **kw):
            extra_seq[0] += 1
            emit({"t": t, "seq": 0, "day": label(t.date()), "at": t.strftime("%H:%M:%S") if t.second else t.strftime("%H:%M"), "kind": "activity", "what": what, "derived": True, **kw})

        def raise_lines(until, final=False):
            nonlocal raised
            if wait_start is None:
                return
            hi, ur = THRESHOLDS["later" if session_person else "first"]
            start = wait_start
            for level, mins, frm in (("high", hi, "normal"), ("urgent", ur, "high")):
                order = ["low", "normal", "high", "urgent"]
                if order.index(raised) >= order.index(level):
                    continue
                at = add_working(cfg, self.site, start, mins)
                if at <= until:
                    auto_act(at.replace(second=0), "priority", **{"from": raised, "to": level, "by": "service", "how": "the wait"})
                    raised = level

        for it in base_items:
            k, t = it["kind"], it["t"]
            if k == "message" and it["from"] == "customer":
                if status == "resolved":
                    status = "open" if (owner or drafts_state or "handoff" in labels) else "pending"
                    auto_act(t, "reopened", how="a new customer message")
                    session_person = False
                if box is not None and box.get("_pending_replace"):
                    pass
                emit(it)
                if status == "open" and wait_start is None:
                    wait_start = t if is_open(cfg, self.site, t) else t
                if box is not None:
                    box["_superseded"] = True
            elif k == "message" and it["from"] == "assistant":
                assert status == "pending" and not owner and "handoff" not in labels, "%s: the assistant sends only in a chat that is its own (%s)" % (f.fid, it["text"][:40])
                emit(it)
            elif k == "handoff":
                emit(it)
                labels.append("handoff")
                status = "open"
                wait_start = t
            elif k == "draft":
                assert status == "open", "%s: a draft needs an open chat" % f.fid
                if box is not None:
                    box["outcome"] = {"kind": "replaced_unseen", "by": None, "day": it["day"], "at": it["at"],
                                      "because": "the customer wrote again and a newer draft took its place; nobody had acted on it"}
                it["why_a_draft"] = ("the channel is set to drafts" if drafts_state else
                                     "the chat is owned by a person" if owner else "the chat carries handoff, so the assistant no longer sends")
                it["outcome"] = None
                emit(it)
                box = it
                if it.get("_clear"):
                    slot, at = it["_clear"]
                    tt, shown = self.when(at)
                    it["outcome"] = {"kind": "discarded", "by": slot, "day": self.day, "at": shown, "because": "cleared from the reply box"}
                    box = None
            elif k == "message" and it["from"] == "staff":
                slot = it["slot"]
                raise_lines(t)
                if owner is None:
                    auto_act(t - dt.timedelta(seconds=2), "assigned", to=slot, by=slot, how="first reply")
                    owner = slot
                    history.append({"day": it["day"], "at": (t - dt.timedelta(seconds=2)).strftime("%H:%M:%S"), "to": slot, "how": "first reply"})
                status = "open"
                if box is not None:
                    if it["_use"] == box["id"]:
                        assert it["text"] == box["text"], "%s: %s is sent as it was, so the texts must be equal" % (f.fid, box["id"])
                        box["outcome"] = {"kind": "sent_as_is", "by": slot, "day": it["day"], "at": it["at"], "became": it}
                    elif it["_edit"] == box["id"]:
                        assert it["text"] != box["text"]
                        box["outcome"] = {"kind": "sent_edited", "by": slot, "day": it["day"], "at": it["at"], "became": it}
                    else:
                        box["outcome"] = {"kind": "discarded", "by": slot, "day": it["day"], "at": it["at"],
                                          "because": ("she" if f.gender(slot) == "female" else "he") + " sent " + ("her" if f.gender(slot) == "female" else "his") + " own text", "_own": it}
                    box = None
                else:
                    assert not it["_use"] and not it["_edit"], "%s: no draft in the box for %s" % (f.fid, it["text"][:30])
                if wait_start is not None:
                    it["_wait"] = (wait_start, "first" if not session_person else "later")
                emit(it)
                if "handoff" in labels:
                    labels.remove("handoff")
                    auto_act(t + dt.timedelta(seconds=1), "label_removed", label="handoff", by=slot, how="a manager's reply takes it off")
                if raised != base:
                    auto_act(t + dt.timedelta(seconds=2), "priority", **{"from": raised, "to": base, "by": "service", "how": "answered"})
                    raised = base
                wait_start, session_person = None, True
            elif k == "note":
                emit(it)
            elif k == "activity":
                if it["what"] == "label_added":
                    labels.append(it["label"])
                elif it["what"] == "priority":
                    base = it["to"]
                    it["from"] = raised
                    raised = max(raised, base, key=["low", "normal", "high", "urgent"].index)
                elif it["what"] == "resolved":
                    assert box is None, "%s: a draft is still in the box when the chat is resolved" % f.fid
                    raise_lines(t)
                    status = "resolved"
                    resolutions.append({"day": it["day"], "at": it["at"], "by": it["by"]})
                    wait_start = None
                    raised = base
                emit(it)
            elif k == "outside":
                emit(it)
        t_local = t_at(self.site)
        if status != "resolved":
            raise_lines(t_local)
        assert all(i["t"] <= t_local for i in out), "%s: a line is dated after T" % f.fid

        out.sort(key=lambda i: (i["t"], i["seq"]))
        for n, it in enumerate(out, 1):
            it["n"] = n
        # the public shape
        timeline = []
        for it in out:
            row = {"n": it["n"], "day": it["day"], "at": it["at"], "kind": it["kind"]}
            for key, val in it.items():
                if key in ("n", "day", "at", "kind", "t", "seq") or key.startswith("_"):
                    continue
                if key == "outcome" and val:
                    val = dict(val)
                    if "became" in val:
                        val["became"] = val["became"]["n"]
                    if "_own" in val:
                        val["because"] += " (n %d)" % val.pop("_own")["n"]
                row[key] = val
            if it["kind"] == "message" and it["from"] == "staff" and it.get("_late"):
                row["late"] = it["_late"]
            timeline.append(OneLine(row))

        # what the product must read back
        waits, kinds = [], {"customer": 0, "assistant": 0, "manager": 0, "note": 0}
        asked, first_answer, first_person = None, None, None
        last_handoff = None
        for it in out:
            if it["kind"] == "handoff":
                kinds["note"] += 1
                last_handoff = it
            elif it["kind"] == "note":
                kinds["note"] += 1
            elif it["kind"] == "activity" and it["what"] == "resolved":
                asked = None
            elif it["kind"] == "message":
                who = it["from"]
                kinds["customer" if who == "customer" else "assistant" if who == "assistant" else "manager"] += 1
                if who == "customer":
                    if asked is None:
                        asked = it
                elif asked is not None or (who == "staff" and it.get("_wait")):
                    src = asked or last_handoff
                    w = {"asked": src["n"], "answered": it["n"], "by": "assistant" if who == "assistant" else it["slot"]}
                    if who == "assistant":
                        w["wall_seconds"] = int((it["t"] - max(x["t"] for x in out if x["kind"] == "message" and x["from"] == "customer" and x["t"] <= it["t"])).total_seconds())
                    else:
                        start, kind_ = it["_wait"]
                        w["working_minutes"] = round(working_minutes(cfg, self.site, start, it["t"]), 1)
                        w["wall_minutes"] = round((it["t"] - start).total_seconds() / 60, 1)
                        w["measured_from"] = "n %d" % next(x["n"] for x in out if x["t"] == start and x["kind"] in ("message", "handoff"))
                        w["reply"] = kind_
                        if it.get("_late"):
                            w["late"] = it["_late"]
                        if first_person is None and kind_ == "first":
                            first_person = {"by": it["slot"], "n": it["n"], "working_minutes": w["working_minutes"],
                                            "note": "the ledger's first chat reply (conv.first_reply.definition): the wait before the person's first line in the session"}
                    if first_answer is None:
                        first_answer = {"by": w["by"]}
                        first_answer.update({"wall_seconds": w["wall_seconds"]} if who == "assistant" else {"working_minutes": w["working_minutes"]})
                    waits.append(OneLine(w))
                    asked = None
        if asked is not None:
            waits.append(OneLine({"asked": asked["n"], "answered": None, "note": "open at T"}))
        outcomes = [OneLine({"draft": i["id"], "outcome": i["outcome"]["kind"], "manager": i["outcome"]["by"]}) for i in out if i["kind"] == "draft" and i["outcome"]]
        in_box = [i["id"] for i in out if i["kind"] == "draft" and not i["outcome"]]
        assert len(in_box) <= 1
        if in_box:
            assert status == "open" and self.channel == "chat", "%s: a draft may wait at T only in an open web chat" % f.fid
        order = ["low", "normal", "high", "urgent"]
        state = {"status": status, "owner": owner, "labels": labels, "priority": {"base": base, "shown": raised}}
        peak = max([i["to"] for i in out if i["kind"] == "activity" and i["what"] == "priority"] + [raised], key=order.index)
        if peak != raised:
            state["priority"]["peak"] = peak
        unanswered = [i for i in out if i["kind"] == "message" and i["from"] == "customer" and wait_start is not None and i["t"] >= wait_start]
        if status == "open" and wait_start is not None:
            state["waiting_since"] = {"day": label(wait_start.date()), "at": wait_start.strftime("%H:%M:%S")}
            state["waited_working_minutes_at_t"] = round(working_minutes(cfg, self.site, wait_start, t_local), 1)
            state["unread"] = len(unanswered)
        else:
            state["waiting_since"] = None
            state["unread"] = 0
        state["draft_in_box"] = in_box[0] if in_box else None
        state.update(self.state_extra)
        reads = {"first_answer": first_answer, "waits": waits}
        if first_person:
            reads["first_person_line"] = first_person
        reads["message_kinds"] = kinds
        reads["resolutions"] = [OneLine(r) for r in resolutions]
        reads["draft_outcomes"] = outcomes
        reads.update(self.reads_extra)
        t0 = first_item["t"]
        conv = {"key": self.key, "channel": self.channel, "bridge": bridge, "inbox": inbox, "assistant_mode": mode, "clock": self.clock,
                "thread_key": self.thread_key, "peer": {"id": self.peer_id, "name": self.peer_name},
                "contact": {"identifier": "%s_%s" % (self.channel, self.peer_id), "name": self.peer_name, "phone": self.phone, "avatar": self.avatar}}
        conv.update(self.extra)
        opened = {"day": first_item["day"], "at": first_item["at"], "status": opened_status, "arrived_closed": not is_open(cfg, self.site, t0)}
        if self.opened_note:
            opened["note"] = self.opened_note
        conv["opened"] = opened
        conv["timeline"] = timeline
        conv["assignee_history"] = [OneLine(h) for h in history]
        conv["state_at_t"] = state
        conv["reads_back"] = reads
        return conv


class OneLine(dict):
    pass


def dump(obj, ind=0):
    pad = "  " * ind
    if isinstance(obj, OneLine):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        flat = json.dumps(obj, ensure_ascii=False)
        if len(flat) <= 100 and not any(isinstance(v, (dict, list)) and v for v in obj.values()):
            return flat
        rows = ["%s  %s: %s" % (pad, json.dumps(k, ensure_ascii=False), dump(v, ind + 1)) for k, v in obj.items()]
        return "{\n" + ",\n".join(rows) + "\n" + pad + "}"
    if isinstance(obj, list):
        if not obj:
            return "[]"
        flat = json.dumps(obj, ensure_ascii=False)
        if len(flat) <= 100 and not any(isinstance(v, (dict, list)) for v in obj):
            return flat
        rows = ["%s  %s" % (pad, dump(v, ind + 1)) for v in obj]
        return "[\n" + ",\n".join(rows) + "\n" + pad + "]"
    return json.dumps(obj, ensure_ascii=False)


class File:
    def __init__(self, cfg, num, story, name, title, demonstrates):
        self.cfg, self.num, self.story, self.name = cfg, num, story, name
        self.fid = "%02d-%s-%s" % (num, story.lower(), name)
        self.title, self.demonstrates = title, demonstrates
        self.cast, self.scenario, self.floating, self.days, self.convs = {}, {}, [], {}, []
        self.why, self.new_facts, self.truth, self.prices, self.numbers = [], [], {}, [], []
        self.extra = {}
        people = json.load(open(os.path.join(SEED, "cast.json"), encoding="utf-8"))["people"]
        self.people = {p["slot"]: p for p in people}

    def gender(self, slot):
        return self.people[str(slot)]["gender"]

    def staff(self, *slots, **more):
        rows = []
        for s in slots:
            full = self.people[str(s)][self.cfg]["full_name"].split()
            name = " ".join(full if (self.cfg == "en" or s in (1, 2, 4, 22, 29) or len(full) < 3) else [full[0], full[-1]])
            row = {"slot": s, "name": name}
            row.update(more.get("s%d" % s, {}))
            rows.append(row)
        self.cast["staff"] = rows

    def first(self, slot):
        return self.people[str(slot)][self.cfg]["full_name"].split()[0]

    def day(self, anchor, why=None):
        text, rule = anchor
        d = resolve(self.cfg, rule)
        lab = label(d)
        row = {"anchor": text, "rule": rule, "nominal": "%s %s" % (WEEKDAYS[d.weekday()], d.isoformat())}
        if why:
            row["what"] = why
        if lab in self.days and self.days[lab]["rule"] != rule:
            row["also"] = self.days[lab]["anchor"]
        self.days[lab] = row
        return lab

    def p(self, said, what, job=None, amount=None, source=None, **kw):
        """Declares a price a line mentions: `said` is how it is written in the text."""
        if job:
            amount = price(self.cfg, job, **kw)
            src = {"catalogue": job, "class": kw.get("cls", "car"), "tier": kw.get("tier", "standard"), "price_class": kw.get("klass", "list"),
                   "with_supplies": bool(kw.get("supplies")), "with_tax": bool(kw.get("tax"))}
        else:
            src = source
        self.prices.append(OneLine({"said": said, "amount": amount, "what": what, "from": src}))
        return amount

    def psum(self, said, what, jobs, supplies=True, tax=True):
        """A bill of several jobs: list prices, shop supplies on the hourly labour (capped), then tax."""
        conf = CAT["configurations"][self.cfg]
        total, lab, parts = 0.0, 0.0, []
        for job, cls in jobs:
            total += price(self.cfg, job, cls=cls)
            j = JOBS[job][self.cfg]
            if j.get("shop_supplies"):
                hm = (j.get("hours_by_class") or {}).get(cls, 1) if j.get("hours_by_class") else 1
                lab += j["labour_price"]["after_rise"] * hm
            parts.append({"catalogue": job, "class": cls})
        if supplies:
            total += min(round(lab * conf["shop_supplies"]["rate_of_hourly_labour"] + 1e-9, 2), conf["shop_supplies"]["cap_per_order"])
        if tax:
            total *= 1 + conf["tax"]["rate"]
        amount = round(total + 1e-9, 2)
        self.prices.append(OneLine({"said": said, "amount": amount, "what": what, "from": {"sum_of": parts, "with_supplies": supplies, "with_tax": tax}}))
        return amount

    def psup(self, said, what, job, cls="car"):
        """The shop-supplies line of one job: the rate times its hourly labour."""
        conf = CAT["configurations"][self.cfg]
        j = JOBS[job][self.cfg]
        hm = (j.get("hours_by_class") or {}).get(cls, 1) if j.get("hours_by_class") else 1
        amount = round(j["labour_price"]["after_rise"] * hm * conf["shop_supplies"]["rate_of_hourly_labour"] + 1e-9, 2)
        self.prices.append(OneLine({"said": said, "amount": amount, "what": what, "from": {"shop_supplies_of": job, "class": cls}}))
        return amount

    def plab(self, said, what, job, cls="car"):
        """The labour of one job alone (a customer brings the parts)."""
        j = JOBS[job][self.cfg]
        hm = (j.get("hours_by_class") or {}).get(cls, 1) if j.get("hours_by_class") else 1
        amount = round(j["labour_price"]["after_rise"] * hm + 1e-9, 2)
        self.prices.append(OneLine({"said": said, "amount": amount, "what": what, "from": {"labour_of": job, "class": cls}}))
        return amount

    def num_(self, said, what):
        self.numbers.append(OneLine({"said": said, "what": what}))

    def conv(self, *a, **kw):
        c = Conv(self, *a, **kw)
        self.convs.append(c)
        return c

    def write(self, folder):
        sc = dict(self.scenario)
        facts = dict(sc.get("facts", {}))
        if self.prices:
            facts["prices"] = self.prices
        if self.numbers:
            facts["numbers"] = self.numbers
        if facts:
            sc["facts"] = facts
        doc = {"format": "seed-conversation/1", "id": self.fid, "configuration": self.cfg, "number": self.num, "story": self.story,
               "title": self.title, "demonstrates": self.demonstrates,
               "nominal_t": "%s %s" % (NOMINAL.strftime("%Y-%m-%d %H:%M"), ZONE[self.cfg]),
               "cast": self.cast, "scenario": sc,
               "days": {k: OneLine(v) for k, v in sorted(self.days.items(), key=lambda kv: (0 if kv[0] == "T" else int(kv[0][1:-1])))},
               "floating_days": [OneLine(x) for x in self.floating]}
        doc.update(self.extra)
        doc["conversations"] = [c.build() for c in self.convs]
        for c in doc["conversations"]:
            for it in c["timeline"]:
                assert it["day"] in self.days, "%s: day %s has no anchor" % (self.fid, it["day"])
        for p in self.prices:
            texts = " ".join(json.dumps(c, ensure_ascii=False) for c in doc["conversations"])
            assert p["said"] in texts, "%s: the price %s is declared and never said" % (self.fid, p["said"])
        firsts = [c["reads_back"]["first_person_line"]["working_minutes"] for c in doc["conversations"] if "first_person_line" in c["reads_back"]]
        if firsts:
            def fill(o):
                if isinstance(o, str):
                    return o.replace("{first}", ("%.1f" % firsts[0]))
                if isinstance(o, list):
                    return [fill(x) for x in o]
                if isinstance(o, dict) and not isinstance(o, OneLine):
                    for k in list(o):
                        o[k] = fill(o[k])
                return o
            for c in doc["conversations"]:
                fill(c["reads_back"])
            self.truth = fill(self.truth)
        doc["truth"] = self.truth
        doc["why"] = self.why
        doc["new_facts"] = self.new_facts
        path = os.path.join(folder, self.fid + ".json")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(dump(doc) + "\n")
        json.load(open(path, encoding="utf-8"))
        return path
