# Checks workday/<lang>/ against the cast, the ledger and the rules of the design.
#   python3 checks/check_workday.py en        python3 checks/check_workday.py ru
# Exit 0 when everything holds for the nominal T (Fri 2026-11-13 10:30, home time) and for an awkward one
# (the run instant Sat 2027-01-02 10:30: en T is that Saturday morning, ru T is the close of 31 December).
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = dt.date
DOW = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
RANK = {"worker": 1, "junior": 2, "middle": 3, "senior": 4, "admin": 5}
WEST = {"22", "23", "24", "25", "26", "27", "28"}
EAST = {"16", "17", "18", "19", "20", "21"}


def load(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------------- the calendar of a market
def observed(d):
    return d - dt.timedelta(1) if d.weekday() == 5 else d + dt.timedelta(1) if d.weekday() == 6 else d


def en_closed(y):
    may31 = D(y, 5, 31)
    memorial = may31 - dt.timedelta(may31.weekday() % 7)
    sep1 = D(y, 9, 1)
    labor = sep1 + dt.timedelta((7 - sep1.weekday()) % 7)
    nov1 = D(y, 11, 1)
    thanks = nov1 + dt.timedelta((3 - nov1.weekday()) % 7 + 21)
    return {observed(D(y, 1, 1)), memorial, observed(D(y, 7, 4)), labor, thanks, observed(D(y, 12, 25)),
            observed(D(y + 1, 1, 1))}


class Clock:
    """Places every anchor of DESIGN.md section 7 for one market and one run instant."""

    def __init__(self, mk, run, roster):
        self.mk, self.roster = mk, roster
        day = run.date()
        hours = self.hours("main", day)
        t = run
        if hours is None or (run.hour, run.minute) < hours[0]:
            day -= dt.timedelta(1)
            while self.hours("main", day) is None:
                day -= dt.timedelta(1)
            t = dt.datetime.combine(day, dt.time(*self.hours("main", day)[1]))
        elif (run.hour, run.minute) > hours[1]:
            t = dt.datetime.combine(day, dt.time(*hours[1]))
        self.t, self.T = t, t.date()
        self.w0 = self.T - dt.timedelta(self.T.weekday())
        self.G = self.snap(self.T - dt.timedelta(175))
        self.started = {"14": self.W(-15, 0), "7": self.W(-14, 0)}
        self.left = {"F2": self.W(-17, 0)}

    # opening hours of a shop on a date: ((h, m), (h, m)) or None when closed
    def closed(self, d):
        return d in en_closed(d.year) if self.mk == "en" else (d.month, d.day) in ((1, 1), (1, 2))

    def hours(self, site, d):
        if self.closed(d):
            return None
        if self.mk == "ru":
            return ((9, 0), (20, 0))
        if d.weekday() < 5:
            return ((7, 30), (17, 30))
        if d.weekday() == 5 and site == "main":
            return ((8, 0), (13, 0))
        return None

    def full_open(self, d):
        return not self.closed(d) and (self.mk == "ru" or d.weekday() < 5)

    def snap(self, d, step=1):
        while not self.full_open(d):
            d += dt.timedelta(step)
        return d

    def W(self, k, dow):
        d = self.w0 + dt.timedelta(7 * k + dow)
        return self.snap(d) if self.closed(d) else d

    def site_of(self, slot):
        s = str(slot).split(":")[-1]
        return "west" if s in WEST else "east" if s in EAST else "main"

    def saturday_crew(self, d):
        k = round((d - dt.timedelta(5) - self.w0).days / 7)
        advisor = {0: "6", 2: "5", 1: "7"}[k % 3]
        if d < self.started["7"] and advisor == "7":
            advisor = "5"
        return {advisor, "29"} | ({"11", "13", "15"} if k % 2 == 0 else {"12", "14", "21"})

    def works(self, slot, d, saturday=False):
        """Is this a day of the person's rota? Owners (1, 2) have none and are never asked."""
        s = str(slot)
        if self.closed(d):
            return False
        if s in self.started and d < self.started[s]:
            return False
        if s in self.left and d >= self.left[s]:
            return False
        wd = DOW[d.weekday()]
        if self.mk == "en":
            if d.weekday() == 5:
                return (saturday and s in self.saturday_crew(d)) or (d == self.T and s in self.saturday_crew(d))
            if d.weekday() == 6:
                return False
            if s == "28":
                return wd in ("mon", "wed", "fri") or d == self.T
            return True
        if s in ("6", "29", "17", "24", "5", "7", "16", "23"):
            phase_b = (d - self.T).days % 4 in (0, 1)
            return phase_b if s in ("6", "29", "17", "24") else not phase_b
        if s in self.roster["patterns"]["ru"]["weekdays"]:
            return d.weekday() < 5
        if s == "28":
            return wd in ("fri", "sat", "sun") or d == self.T
        off = self.roster["patterns"]["ru"]["days_off"].get(s)
        return wd not in off if off else d.weekday() < 5

    def pd(self, slot, n, d=None):
        d = d or self.T
        step = 1 if n > 0 else -1
        for _ in range(abs(n)):
            d += dt.timedelta(step)
            while not self.works(slot, d):
                d += dt.timedelta(step)
        return d

    def wd(self, d, n):
        step = 1 if n > 0 else -1
        for _ in range(abs(n)):
            d += dt.timedelta(step)
            while not self.full_open(d):
                d += dt.timedelta(step)
        return d

    def stock(self):
        d = self.w0 + dt.timedelta(7 + 3)
        return self.w0 + dt.timedelta(7 + 1) if self.closed(d) else d

    def s5(self):
        thu, fri = self.w0 + dt.timedelta(10), self.w0 + dt.timedelta(11)
        return self.w0 + dt.timedelta(9) if self.closed(thu) or self.closed(fri) else thu

    def s16meet(self):
        m = self.pd(6, 3)
        while not self.works(4, m) or m == self.stock() or m.weekday() > 4:
            m = self.pd(6, 1, m)
        return m

    def base(self, token):
        if token == "T":
            return self.T
        if token == "G":
            return self.G
        if token == "S5":
            return self.s5()
        if token == "stock":
            return self.stock()
        if token == "S16meet":
            return self.s16meet()
        if token == "S9cancel":
            d = self.w0 - dt.timedelta(63)
            return self.w0 - dt.timedelta(70) if self.closed(d) else d
        m = re.fullmatch(r"W([+-]?\d+)\.(\w{3})", token)
        if m:
            return self.W(int(m.group(1)), DOW.index(m.group(2)))
        m = re.fullmatch(r"p(\w+?)([+-]\d+)", token)
        if m:
            return self.pd(m.group(1), int(m.group(2)))
        m = re.fullmatch(r"(main|east|west)([+-]\d+)", token)
        if m:
            return self.wd(self.T, int(m.group(2)))
        raise ValueError(f"unknown anchor {token!r}")

    def hop(self, d, token):
        m = re.fullmatch(r"([+-]\d+)d", token)
        if m:
            return d + dt.timedelta(int(m.group(1)))
        if token == "open":
            return self.wd(d, 1)
        if token == "=open":
            return self.snap(d)
        if token == "=mon":
            return d + dt.timedelta((7 - d.weekday()) % 7)
        m = re.fullmatch(r"(=|!|<=)?p(\w+)", token)
        if m:
            kind, slot = m.group(1), m.group(2)
            if kind == "<=":  # his last working day on or before d
                while not self.works(slot, d):
                    d -= dt.timedelta(1)
                return d
            if kind == "=":
                while not self.works(slot, d):
                    d += dt.timedelta(1)
                return d
            if kind == "!":
                d += dt.timedelta(1)
                while self.works(slot, d) or self.hours(self.site_of(slot), d) is None:
                    d += dt.timedelta(1)
                return d
            return self.pd(slot, 1, d)
        raise ValueError(f"unknown hop {token!r}")

    def day(self, anchor):
        parts = re.split(r">|(?=<=)", anchor.split("@")[0])
        d = self.base(parts[0])
        for token in parts[1:]:
            d = self.hop(d, token)
        return d

    def at(self, anchor, slot=None):
        """The instant of an anchor in home time (a west actor's wall clock is an hour behind)."""
        d = self.day(anchor)
        site = self.site_of(slot) if slot is not None else "main"
        hours = self.hours(site, d) or self.hours("main", d) or (((7, 30), (17, 30)) if self.mk == "en" else ((9, 0), (20, 0)))
        shift = dt.timedelta(hours=1) if site == "west" else dt.timedelta(0)
        clock = anchor.split("@")[1] if "@" in anchor else "12:00"
        m = re.fullmatch(r"T-(\d+):(\d\d)", clock)
        if m:
            return self.t - dt.timedelta(hours=int(m.group(1)), minutes=int(m.group(2)))
        if clock == "close":
            return dt.datetime.combine(d, dt.time(*hours[1])) + shift
        m = re.fullmatch(r"([oc])([+-])(\d+):(\d\d)", clock)
        if m:
            edge = hours[0] if m.group(1) == "o" else hours[1]
            delta = dt.timedelta(hours=int(m.group(3)), minutes=int(m.group(4)))
            base = dt.datetime.combine(d, dt.time(*edge))
            return (base + delta if m.group(2) == "+" else base - delta) + shift
        h, mi = clock.split(":")
        return dt.datetime.combine(d, dt.time(int(h), int(mi))) + shift


# ----------------------------------------------------------------------------- the checks
class Check:
    def __init__(self, lang):
        self.lang = lang
        self.fails, self.passed = [], 0
        self.cast = {p["slot"]: p for p in load("cast.json")["people"]}
        self.ledger = {r["key"]: r for r in load("ledger.json")["rows"]}
        self.roster = load("workday", "roster.json")
        d = lambda name: load("workday", lang, name)  # noqa: E731
        self.cards, self.cal, self.req = d("cards.json"), d("calendar.json"), d("shift_requests.json")["requests"]
        self.fb, self.alerts, self.inbox = d("feedback.json"), d("alerts.json"), d("inbox.json")

    def val(self, key):
        r = self.ledger[key]
        return r["value"] if "value" in r else r[self.lang]

    def ok(self, cond, what):
        if cond:
            self.passed += 1
        else:
            self.fails.append(what)

    # ---- 1. the rank rule
    def person(self, who):
        return str(who).split(":")[-1]

    def rank(self, slot):
        return RANK.get(self.cast[str(slot)]["rank"] or "", 0)

    def sites(self, slot):
        p = self.cast[str(slot)]
        return {p["site"]} | set(p.get("also_sites") or [])

    def may_put_on(self, by, target):
        by, target = self.person(by), str(target)
        if by == target:
            return True
        if self.rank(by) < RANK["junior"] or self.rank(target) < RANK["junior"]:
            return False
        if self.rank(target) > self.rank(by):
            return False
        return self.rank(by) >= RANK["senior"] or bool(self.sites(by) & self.sites(target))

    def ranks(self):
        for c in self.cards["cards"]:
            on_card = {str(c["owner"])} | {str(p["slot"]) for p in c["participants"]}
            if c["owner"] is not None:
                self.ok(self.rank(c["owner"]) >= RANK["junior"], f"{c['id']}: owner {c['owner']} holds no board")
            for s in c["trail"]:
                by = s["by"]
                if s["verb"] == "assigned" and by != "A":
                    self.ok(self.may_put_on(by, s["to"]), f"{c['id']}: {by} may not give work to {s['to']}")
                if s["verb"] == "participant_added":
                    self.ok(self.may_put_on(by, s["who"]), f"{c['id']}: {by} may not add {s['who']}")
                for m in s.get("mentions", []):
                    self.ok(self.may_put_on(by, m) or str(m) in on_card, f"{c['id']}: {by} may not mention {m}")
                    name = self.cast[str(m)][self.lang]["full_name"]
                    self.ok("@" + name in s["body"], f"{c['id']}: the mention of {m} does not carry the name {name}")
                if by not in ("A", "S") and s["verb"] != "created":
                    self.ok(self.rank(self.person(by)) >= RANK["junior"], f"{c['id']}: {by} has no board to act on")
        for row in self.cards["bank_open_at_t"]:
            self.ok(self.rank(row["owner"]) >= RANK["junior"], f"bank card: owner {row['owner']} holds no board")
            self.ok(self.may_put_on(row["giver"], row["owner"]), f"bank card: {row['giver']} may not give work to {row['owner']}")

    # ---- 2 and 6. anchors, orders, gaps, rota days
    def on_rota(self, clock, slot, anchor, what, saturday=False):
        s = self.person(slot)
        if s in ("A", "S", "1", "2"):
            return
        self.ok(clock.works(s, clock.day(anchor), saturday), f"{what}: slot {s} is not on the rota on {clock.day(anchor)} ({anchor})")

    def dates(self, clock, label):
        T, t = clock.T, clock.t
        cards = {c["id"]: c for c in self.cards["cards"]}
        quiet_now = []
        for c in self.cards["cards"]:
            last = None
            for s in c["trail"]:
                try:
                    at = clock.at(s["at"], s["by"] if s["by"] not in ("A", "S") else c["owner"] or 4)
                except ValueError as e:
                    self.ok(False, f"{label} {c['id']}: {e}")
                    continue
                self.ok(at <= t, f"{label} {c['id']}: {s['verb']} at {at} is after T")
                self.ok(at.date() >= clock.G, f"{label} {c['id']}: {s['verb']} on {at.date()} is before go-live")
                self.ok(last is None or at >= last, f"{label} {c['id']}: {s['verb']} at {at} is before the step before it")
                last = at
                self.on_rota(clock, s["by"], s["at"], f"{label} {c['id']} {s['verb']}")
            due = clock.at(c["due"], c["owner"] or 4) if c["due"] else None
            if c["state_at_t"] not in ("completed", "cancelled"):
                idle = (t - last).days
                quiet = idle >= 7 and (due is None or due.date() <= T + dt.timedelta(7))
                if quiet:
                    quiet_now.append(c["id"])
                self.ok(("quiet" in c) == quiet, f"{label} {c['id']}: quiet at T is {quiet}, the card says {'quiet' in c}")
        self.ok(len(quiet_now) == 2, f"{label}: {len(quiet_now)} hand-written cards are quiet at T, the design plants two: {quiet_now}")

        # S16: given < part done < the comment with the mention < T < block < due < meeting, not on the stocktake day
        r = cards["S16-review"]
        given = clock.at(r["created"]["at"], 4)
        done = clock.at(r["participants"][1]["part_done_at"], 9)
        mention = [clock.at(s["at"], 4) for s in r["trail"] if s.get("mentions")][0]
        entries = {e["id"]: e for e in self.cal["entries"]}
        block, due = clock.at(entries["S16-block"]["start"], 6), clock.at(r["due"], 6)
        meet = clock.at(entries["S16-meeting"]["start"], 4)
        self.ok(given < done < mention < t < block < due < meet, f"{label} S16: the order given, part, comment, T, block, due, meeting fails")
        self.ok(meet.date() != clock.stock(), f"{label} S16: the meeting is on the stocktake day")
        for slot in (4, 6):
            self.ok(clock.works(slot, meet.date()), f"{label} S16: slot {slot} is off on the meeting day {meet.date()}")
        self.ok(clock.works(6, block.date()) and clock.works(6, due.date()), f"{label} S16: slot 6 is off on her block or due day")
        # when T is the close of a day (rule R2), the cards due that day are done by then and are not asked about
        closing = (t.hour, t.minute) == clock.hours("main", T)[1]
        junior_due = [clock.at(c["due"], 6) for c in self.cards["cards"]
                      if c["owner"] == 6 and c["due"] and c["state_at_t"] not in ("completed", "cancelled")
                      and not (closing and clock.day(c["due"]) == T)]
        self.ok(all(x > t for x in junior_due), f"{label} S16.4: a card of slot 6 is overdue at T")

        # S06: 21 to 27 days overdue; S03: the fix is 21 to 27 days before T, the card before it
        over = (T - clock.day(cards["S06-supplier"]["due"])).days
        self.ok(21 <= over <= 27, f"{label} S06: the supplier card is {over} days overdue, not 21 to 27")
        fix = clock.day("W-3.mon")
        self.ok(21 <= (T - fix).days <= 27, f"{label} S03: the fix is {(T - fix).days} days before T")
        s3 = cards["S03-early-desk"]
        self.ok(clock.day(s3["created"]["at"]) < fix == clock.day(s3["trail"][-1]["at"]), f"{label} S03: the card is not made before the fix and closed on it")

        # S08: raised, taken the next working day of slot 4, all before T; S07: the chat under 30 days before T
        s8 = cards["S08-complaint"]
        raised, taken = clock.day(s8["created"]["at"]), clock.day(s8["trail"][1]["at"])
        self.ok(clock.day("p7-5") < clock.day("p7-4") < raised < taken < T, f"{label} S08: quote, car in, ready, discount, T are out of order")
        s7 = cards["S07-handover"]
        chat = clock.at(s7["created"]["at"], 6)
        self.ok((t - chat).days < 30 and chat.date() < clock.day(s7["trail"][1]["at"]), f"{label} S07: the first chat is not inside 30 days, before day A")

        # S14: the no-show talk card, the east stand-up note and FB9 fall on the timeline's no-show day (stories/TIMELINE.md:
        # en east's 2nd full open day before T; ru slot 20's last working day on or before it), and slot 20 is rostered then
        sys.path.insert(0, os.path.join(ROOT, "checks"))
        import timeline_examples as tl
        noshow = dict(tl.place(self.lang, t)[0])["S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it"]
        placed = [clock.day(cards["G-no-show-talk"]["created"]["at"]),
                  clock.day(next(n["on"] for n in self.cal["standup_notes"] if n["series"] == "STANDUP-east")),
                  clock.day(next(f["sent"] for f in self.fb["reports"] if f["id"] == "FB9"))]
        self.ok(placed == [noshow] * 3 and clock.works(20, noshow), f"{label} S14: the no-show items fall on {placed}, the timeline's day is {noshow}")

        # S05 and S14: two published shifts of slot 16 in her week off, both in W+1 and after T; the open shift; the stocktake
        s5 = clock.s5()
        two = [clock.day("S5>=p16"), clock.day("S5>=p16>p16")]
        end_w1 = clock.w0 + dt.timedelta(13)
        self.ok(all(T < d <= end_w1 and s5 <= d <= s5 + dt.timedelta(6) for d in two), f"{label} S05: her two published shifts {two} are not in W+1 inside the week off")
        self.ok(clock.w0 + dt.timedelta(7) <= clock.stock() <= end_w1, f"{label} S13: the stocktake is not in the published week")
        self.ok(T < clock.day("W+1.tue") <= end_w1, f"{label} S14: the open shift is not between T and the end of W+1")

        # calendar: invitees who accepted are on the rota that day; notes are written by somebody who was in
        for e in self.cal["entries"]:
            start = clock.at(e["start"], e["organiser"])
            end = clock.at(e["end"], e["organiser"])
            self.ok(end >= start, f"{label} {e['id']}: ends before it starts")
            if not e.get("all_day"):
                self.on_rota(clock, e["organiser"], e["start"], f"{label} {e['id']} organiser")
            for i in e["invitees"]:
                if i["response"] == "accepted":
                    self.on_rota(clock, i["slot"], e["start"], f"{label} {e['id']} invitee")
                    if "at" in i:
                        self.ok(clock.at(i["at"], i["slot"]) <= min(start, t), f"{label} {e['id']}: slot {i['slot']} answers after the entry or after T")
        for n in self.cal["standup_notes"]:
            self.on_rota(clock, n["by"], n["on"], f"{label} stand-up note {n['series']}")
            self.ok(clock.day(n["on"]).weekday() < 5 and clock.day(n["on"]) < T, f"{label} stand-up note {n['series']} is not on a past weekday")

        # feedback and alerts: placed, in the product's months, never after T
        for f in self.fb["reports"]:
            at = clock.at(f["sent"], f["slot"])
            self.ok(clock.G <= at.date() and at <= t, f"{label} {f['id']}: sent {at}, outside G..T")
            if f["status_set"]:
                self.ok(at <= clock.at(f["status_set"], 2) <= t, f"{label} {f['id']}: its status is set before it was sent or after T")
        for a in self.alerts["alerts"]:
            opened = clock.at(a["opened"])
            self.ok(clock.G <= opened.date() and opened <= t, f"{label} {a['id']}: opened {opened}, outside G..T")
            if a["closed"]:
                self.ok(opened < clock.at(a["closed"]) <= t, f"{label} {a['id']}: closed before it opened or after T")
        # the Inbox lines and the bookings are placed too: a line that is news lies before T, a booking before its entry
        for who in ("junior", "senior"):
            for ln in self.inbox[who]["lines"]:
                at = clock.at(ln["at"], self.inbox[who]["slot"])
                if ln.get("verb") != "due_today":
                    self.ok(clock.G <= at.date() and at <= t, f"{label} {who} Inbox, {ln['about']}: its time {at} is outside G..T")
        self.on_rota(clock, 5, "p7-4>p5>p4>p5", f"{label} the knowledge proposal of slot 5")
        for e in self.cal["entries"]:
            self.ok(clock.at(e["booked"], e["organiser"]) <= min(clock.at(e["start"], e["organiser"]), t), f"{label} {e['id']}: booked after it starts or after T")
            self.on_rota(clock, e["organiser"], e["booked"], f"{label} {e['id']} booking")
        for s in (10, 11, 12):
            self.ok(self.fb["reports"][s - 10]["sent"].startswith(("W-12.wed", "W-7.wed", "W-2.wed")[s - 10]), f"{label}: S10's feedback {s - 9} is not on its Wednesday")

    # ---- 3. the 64 requests
    def requests(self, clock, label):
        for r in self.req:
            slot = r["slot"]
            sat = bool(r.get("saturday_turn"))
            try:
                day = clock.day(r["shift"])
            except ValueError as e:
                self.ok(False, f"{label} {r['id']}: {e}")
                continue
            self.ok(clock.works(slot, day, sat), f"{label} {r['id']}: slot {slot} has no shift on {day} ({r['shift']})")
            if "days_before_shift" in r["filed"]:
                filed = dt.datetime.combine(day - dt.timedelta(r["filed"]["days_before_shift"]), dt.time(*map(int, r["filed"]["at"].split(":"))))
            else:
                filed = clock.at(r["filed"]["at"], slot)
            self.ok(clock.G <= filed.date() < day, f"{label} {r['id']}: filed {filed.date()} is not between go-live and the shift {day}")
            limit = day
            if r["kind"] == "change_date":
                new = clock.day(r["proposed"]["date"])
                self.ok(not clock.works(slot, new, False) and clock.hours(clock.site_of(slot), new) is not None,
                        f"{label} {r['id']}: the day asked for, {new}, is a day slot {slot} already works or the shop is shut")
                self.ok(filed.date() < new, f"{label} {r['id']}: filed after the day asked for")
                limit = min(day, new)
            if r["status"] in ("approved", "declined"):
                dec = r["decided"]
                self.ok(self.rank(dec["by"]) >= RANK["senior"], f"{label} {r['id']}: {dec['by']} may not decide a request")
                if "working_days_after_filing" in dec:
                    when = filed.date()
                    while not clock.works(dec["by"], when):
                        when += dt.timedelta(1)
                    when = clock.pd(dec["by"], dec["working_days_after_filing"], when) if dec["working_days_after_filing"] else when
                else:
                    when = clock.day(dec["at"])
                self.ok(filed.date() <= when <= limit and when <= clock.T, f"{label} {r['id']}: decided {when}, not between the filing {filed.date()} and {limit}")
            if r["status"] == "open":
                self.ok(filed <= clock.t < dt.datetime.combine(day, dt.time(0)), f"{label} {r['id']}: an open request must be filed before T for a shift after T")
            else:
                self.ok(day < clock.T, f"{label} {r['id']}: a settled request is about a shift that has not passed")
        mine = [r for r in self.req if r["slot"] == "11"]
        recent = [r for r in mine if (clock.T - (clock.day(r["shift"]) - dt.timedelta(r["filed"]["days_before_shift"]))).days <= 90]
        want = self.val("s14.requests")["p11_last_90_days"]
        got = {"filed": len(recent), "approved": sum(r["status"] == "approved" for r in recent),
               "declined": sum(r["status"] == "declined" for r in recent)}
        self.ok(got == want, f"{label}: slot 11 in the last 90 days is {got}, the ledger says {want}")

    def request_sums(self):
        want = self.val("s14.requests")
        self.ok(len(self.req) == want["total"], f"{len(self.req)} requests, the ledger says {want['total']}")
        for status in ("approved", "declined", "expired", "withdrawn", "open"):
            got = sum(r["status"] == status for r in self.req)
            self.ok(got == want[status], f"{got} requests {status}, the ledger says {want[status]}")
        for slot, person in self.cast.items():
            row = self.ledger.get(f"p{slot.zfill(2) if slot.isdigit() else slot}.requests")
            got = sum(r["slot"] == slot for r in self.req)
            self.ok(got == (row["value"] if row else 0), f"slot {slot}: {got} requests, the ledger says {row['value'] if row else 0}")
        p11 = want["p11_since_G"]
        mine = [r for r in self.req if r["slot"] == "11"]
        self.ok({s: sum(r["status"] == s for r in mine) for s in ("approved", "declined", "expired")}
                == {s: p11[s] for s in ("approved", "declined", "expired")}, "slot 11's outcomes since G differ from the ledger")
        for r in self.req:
            self.ok(r["kind"] in want["kinds"], f"{r['id']}: kind {r['kind']}")
            self.ok(bool(r["reason"].strip()), f"{r['id']}: no reason")
            shape = {"change_time": {"start", "end"}, "change_date": {"date"}, "remove": None}[r["kind"]]
            self.ok((set(r["proposed"]) if "proposed" in r else None) == shape, f"{r['id']}: what it asks for does not fit its kind")
            if r["status"] == "declined":
                self.ok(bool(r["decided"]["note"]), f"{r['id']}: declined with no word")
        self.ok([r["slot"] for r in self.req if r["status"] == "open"] == ["16", "16"], "the two open requests are not slot 16's")

    # ---- 4. boards and Inboxes at T
    def boards(self, clock):
        want = self.val("board.open_at_t")
        live = [c for c in self.cards["cards"] if c["state_at_t"] not in ("completed", "cancelled")]
        bank = self.cards["bank_open_at_t"]
        self.ok(len(live) + len(bank) == want["all_managers"], f"{len(live) + len(bank)} open cards, the ledger says {want['all_managers']}")
        junior = [c for c in live if c["owner"] == 6]
        j = want["junior_operator"]
        self.ok(len(junior) == j["open"] and not [b for b in bank if b["owner"] == 6], f"the junior operator has {len(junior)} open cards, not {j['open']}")
        self.ok(sum(c["priority"] == "high" for c in junior) == j["high"], "the junior operator's high cards differ from the ledger")
        today = [c for c in junior if c["due"] and clock.day(c["due"]) == clock.T]
        self.ok(len(today) == j["for_today"], f"the junior operator has {len(today)} cards due today, not {j['for_today']}")
        senior = [c for c in live if c["owner"] == 4]
        self.ok(len(senior) == want["senior_operator"] and not [b for b in bank if b["owner"] == 4], f"the senior operator has {len(senior)} own cards")
        self.ok(sum(c["owner"] is None for c in live) == 1, "exactly one card has no owner")
        ids = {c["id"] for c in live}
        self.ok({"S01-a5-callback", "S06-supplier", "S16-review"} <= ids, "a planted open card is missing")
        urgent = {}
        for site, n in [(c["site"], c["priority"] == "urgent") for c in live] + [(clock.site_of(b["owner"]), b["priority"] == "urgent") for b in bank]:
            urgent[site] = urgent.get(site, 0) + n
        self.ok(all(n <= 3 for n in urgent.values()), f"more than three urgent cards at a site: {urgent}")
        per_owner = {}
        for owner in [c["owner"] for c in live] + [b["owner"] for b in bank]:
            per_owner[owner] = per_owner.get(owner, 0) + 1
        self.ok(all(self.rank(o) >= RANK["junior"] for o in per_owner if o is not None), "a worker holds a card")

        # the Inboxes: the design's counts (junior about 7, senior about 11), and every line points at something that exists
        jl, sl = self.inbox["junior"]["lines"], self.inbox["senior"]["lines"]
        self.ok(len({ln["item"] for ln in jl if ln["half"] == "update"}) == 7, "the junior operator's unread items are not the design's seven")
        self.ok(sum(ln["half"] == "needs" for ln in jl) == sum(1 for c in junior if c["due"] and clock.day(c["due"]) == clock.T),
                "the junior operator's Needs you is not her cards due today")
        self.ok(len(sl) == 11, f"the senior operator has {len(sl)} lines, the design says about 11")
        due_today = [c["id"] for c in senior if c["due"] and clock.day(c["due"]) == clock.T]
        self.ok(sorted(due_today) == sorted(ln["about"].split()[1] for ln in sl if ln.get("verb") == "due_today"),
                f"the senior operator's due-today lines are not his cards due today {due_today}")
        req_ids = {r["id"] for r in self.req}
        for who, lines in (("junior", jl), ("senior", sl)):
            for ln in lines:
                m = re.search(r"card ([\w-]+)", ln["about"])
                if m:
                    self.ok(m.group(1) in {c["id"] for c in self.cards["cards"]}, f"{who} Inbox: no card {m.group(1)}")
                m = re.search(r"request (R\d+)", ln["about"])
                if m:
                    self.ok(m.group(1) in req_ids, f"{who} Inbox: no request {m.group(1)}")
                m = re.search(r"entry ([\w-]+)", ln["about"])
                if m:
                    self.ok(m.group(1) in {e["id"] for e in self.cal["entries"]}, f"{who} Inbox: no entry {m.group(1)}")
        self.ok(sum(ln.get("type") == "memory.proposed" for ln in sl) == 2 and sum(ln.get("verb") == "change_requested" for ln in sl) == 2,
                "the senior operator's two notes and two requests are not all there")
        self.ok(sum(a["status_at_t"] == "open" for a in self.alerts["alerts"]) == 1
                and [a["severity"] for a in self.alerts["alerts"] if a["status_at_t"] == "open"] == ["warning"],
                "exactly one alert, of low severity, is open at T")
        self.ok(len(self.alerts["alerts"]) == 25, f"{len(self.alerts['alerts'])} alerts, the design says about 25")
        self.ok(len(self.fb["reports"]) == 9 and {f["status"] for f in self.fb["reports"]} == {"open", "seen", "resolved", "wont_fix"},
                "nine feedback reports in every status")

    # ---- 5. people, customers and cars exist in the seed files
    NAMES = {
        "en": ["Nickajack Delivery", "Cumberland Bend Electric", "Wade Carlisle", "Sequoyah", "Harpeth Valley", "Daugherty",
               "Outback", "Rachel Dunlap", "Millsaps", "Clabough Brothers Roofing", "Dogwood Lane Florals", "ProMaster City",
               "Phil Cantrell", "Malibu", "Lonnie Coffey", "Stuart Haney", "Tellico Tire Distributors", "Volvo", "(423) 555-0131"],
        "ru": ["Симбирск", "Идель-Электромонтаж", "Фаттахов", "Казань-АвтоСнаб", "АвтоДеталь-Венец", "Фомичёв", "Logan", "Тимофеева",
               "Тёплый контур", "Трофимов", "Абрамов", "Largus", "Маркелов", "Lancer", "Кравцов", "Бикмаев", "ШинТорг-Волга",
               "Peugeot", "+7 907 378-60-35"],
    }

    def names(self):
        seed = ""
        for name in ("cast.json", "accounts.json", "named_customers.json", "vendors.json"):
            seed += open(os.path.join(ROOT, name), encoding="utf-8").read()
        calls = os.path.join(ROOT, "calls", self.lang)
        for name in sorted(os.listdir(calls)):
            if name[:2] in ("29", "30"):
                seed += open(os.path.join(calls, name), encoding="utf-8").read()
        mine = "".join(json.dumps(x, ensure_ascii=False) for x in (self.cards, self.cal, self.req, self.fb, self.inbox))
        for name in self.NAMES[self.lang]:
            self.ok(name in seed, f"{name!r} is in no seed file")
            self.ok(name in mine, f"{name!r} is listed in the check and used by no item")
        # every colleague named by a first name or a surname in a text is a name the cast gives that person
        known = set()
        for p in self.cast.values():
            d = p[self.lang]
            for text in (d["full_name"], d.get("colleagues_call") or ""):
                known |= set(re.findall(r"[A-ZА-ЯЁ][a-zа-яё]+", text))
        slots = set(self.cast)
        for c in self.cards["cards"]:
            for s in c["trail"]:
                for key in ("by", "who") + (("to",) if s["verb"] == "assigned" else ()):
                    if key in s and s[key] not in ("A", "S"):
                        self.ok(self.person(s[key]) in slots, f"{c['id']}: no slot {s[key]} in the cast")
        for r in self.req:
            self.ok(r["slot"] in slots, f"{r['id']}: no slot {r['slot']}")
        for f in self.fb["reports"]:
            self.ok(str(f["slot"]) in slots, f"{f['id']}: no slot {f['slot']}")
        names_used = {"en": ["Claire", "Donna", "Marcus", "Maya", "Caleb", "Dale", "Jasmine", "Luis", "Randy", "Dustin", "Hunter", "Angie",
                             "Josh", "Brenda", "Austin", "Jordan", "Brandon", "Kevin", "Terry", "Andre", "Travis", "Tyler", "Cody"],
                      "ru": ["Екатерина", "Ирина", "Паш", "Мещеряков", "Хасанов", "Никита", "Ринат", "Камила", "Лёха", "Михалыч",
                             "Рябов", "Ваня", "Артём", "Аюпов", "Блинов", "Карпов", "Сурков", "Шубин", "Нуруллин", "Егоров",
                             "Григорьев", "Булат", "Демидов", "Николаев", "Пахомов", "Ведяшкин", "Женя", "Светлан", "Антон"]}[self.lang]
        castfile = open(os.path.join(ROOT, "cast.json"), encoding="utf-8").read()
        for name in names_used:
            self.ok(name in castfile, f"the colleague name {name!r} is not in cast.json")
            self.ok(name in mine, f"the colleague name {name!r} is checked and used by no item")

    def run(self):
        self.ranks()
        self.request_sums()
        self.names()
        nominal = Clock(self.lang, dt.datetime(2026, 11, 13, 10, 30), self.roster)
        awkward = Clock(self.lang, dt.datetime(2027, 1, 2, 10, 30), self.roster)
        self.boards(nominal)
        for clock, label in ((nominal, "nominal"), (awkward, "awkward")):
            before = len(self.fails)
            try:
                self.dates(clock, label)
                self.requests(clock, label)
            except Exception as e:  # an anchor that cannot be placed is a failure, not a crash
                self.ok(False, f"{label}: {type(e).__name__}: {e}")
            print(f"{self.lang} {label}: T = {clock.t:%a %Y-%m-%d %H:%M}, G = {clock.G}, {len(self.fails) - before} failures")
        return self


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("en", "ru"):
        sys.exit("usage: python3 checks/check_workday.py en|ru")
    check = Check(sys.argv[1]).run()
    for line in check.fails:
        print("FAIL", line)
    print(f"{check.passed} checks passed, {len(check.fails)} failed")
    print("RESULT", "PASS" if not check.fails else "FAIL")
    sys.exit(1 if check.fails else 0)


if __name__ == "__main__":
    main()
