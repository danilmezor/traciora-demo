"""The step `workday`: the stories' working day in the core database, from `workday/<cfg>/` and `workday/roster.json`,
as `workday/DESIGN.md` designs it: the hand-written cards with their trails, the series and single entries of the
calendar with their invitations and answers, the shift templates, cover rules and the shifts of the weeks around T
(drafted, then published by the product's publish of each week), the clock-ins at T, the two open requests, and the two
operators' Inbox (the pushed lines this store owns and the read marks of every older line). Every row goes through the product's commands, run at the row's own instant
(`tenant_binding.at`); `created_at` is the one column no command takes, so it is set after the command (R1).

`plan(cfg, a)` reads the files into rows with every anchor placed and every text written, and touches no database;
`load(conn, cfg, client_id)` writes them in the caller's transaction. A card whose text names something no seed file
holds is left out and named in the plan's `skipped`, as is a trail step that falls after T."""
import datetime as dt
import re
from zoneinfo import ZoneInfo

from seeder import clock, ids, inputs, manifest

DAY = dt.timedelta(1)
DOW = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
# a cast role works the shift templates of this role (roster.json names templates by the base role's position)
BASE_ROLE = {"lead_advisor": "service_advisor", "diagnostic_technician": "technician", "electrical_technician": "technician",
             "lead_technician": "technician", "apprentice_technician": "technician", "lube_tyre_technician": "technician"}
TECHNICIAN = "technician"
READ_AFTER = {6: 20, 4: 60}  # DESIGN.md section 4: minutes after a line until its operator has read it
CONFIG_KEY = "config_key"  # traciora.core.queries.locations.CONFIG_KEY


class Missing(Exception):
    """A text names a value no seed file holds."""


class Clock:
    """Every anchor of DESIGN.md section 7 for one build: the named days from `clock.anchors`, the hops over each
    person's rota (roster.json), the hours over each shop's business hours (tenant/roles-and-places)."""

    def __init__(self, cfg, a):
        self.cfg, self.a = cfg, a
        self.places = {p["key"]: p for p in inputs.load(f"tenant/roles-and-places.{cfg}.json")["places"]}
        self.cast = {p["slot"]: p for p in inputs.load("cast.json")["people"]}
        self.patterns = inputs.load("workday/roster.json")["patterns"][cfg]
        self.home = ZoneInfo(inputs.value("geo.home_zone", cfg))
        self.t = a["T"].replace(tzinfo=self.home)
        self.T, self.w0 = a["T"].date(), a["W0"]
        self.started = {"14": a["slot14_starts"], "7": a["slot7_starts"]}
        self.left = {"F2": a["f2_fired"]}

    def site_of(self, slot):
        site = self.cast[str(slot)]["site"]
        return "main" if site == "none" else site

    def zone(self, site):
        return ZoneInfo(self.places[site]["tz"]) if site else self.home

    def hours(self, site, d):
        """((h, m), (h, m)) of the shop on day d, None when it is shut."""
        if clock.closed(self.cfg, d):
            return None
        spans = self.places[site]["business_hours"][DOW[d.weekday()]]
        return tuple(tuple(map(int, x.split(":"))) for x in spans[0]) if spans else None

    def saturday_crew(self, d):
        k = round((d - dt.timedelta(5) - self.w0).days / 7)
        advisor = {0: "6", 2: "5", 1: "7"}[k % 3]
        if d < self.started["7"] and advisor == "7":
            advisor = "5"
        crews = self.patterns["saturday"]["technicians"]
        return {advisor, "29"} | set(crews["even weeks (W0, W-2, ...)"] if k % 2 == 0 else crews["odd weeks"])

    def works(self, slot, d):
        """A day of the person's rota (roster.json patterns; slot 28 also on T's date)."""
        s = str(slot)
        if clock.closed(self.cfg, d) or (s in self.started and d < self.started[s]) or (s in self.left and d >= self.left[s]):
            return False
        wd = DOW[d.weekday()]
        if self.cfg == "en":
            if d.weekday() >= 5:
                return d == self.T and d.weekday() == 5 and s in self.saturday_crew(d)
            return wd in self.patterns["slot_28"]["days"] or d == self.T if s == "28" else True
        if s in ("6", "29", "17", "24", "5", "7", "16", "23"):
            phase_b = (d - self.T).days % 4 in (0, 1)
            return phase_b if int(s) in clock.PHASE_B else not phase_b
        if s in self.patterns["weekdays"]:
            return d.weekday() < 5
        if s == "28":
            return wd in self.patterns["slot_28"]["days"] or d == self.T
        off = self.patterns["days_off"].get(s)
        return wd not in off if off else d.weekday() < 5

    def pd(self, slot, n, d=None):
        d, step = d or self.T, 1 if n > 0 else -1
        for _ in range(abs(n)):
            d += dt.timedelta(step)
            while not self.works(slot, d):
                d += dt.timedelta(step)
        return d

    def base(self, token):
        a = self.a
        named = {"T": self.T, "G": a["G"], "S5": a["week_off"], "stock": a["stocktake"], "S16meet": a["s16_meeting"],
                 "S9cancel": a["s9_cancelled"]}
        if token in named:
            return named[token]
        if m := re.fullmatch(r"W([+-]?\d+)\.(\w{3})", token):
            return a["week_day"](int(m[1]), DOW.index(m[2]))
        if m := re.fullmatch(r"p(\w+?)([+-]\d+)", token):
            return self.pd(m[1], int(m[2]))
        if m := re.fullmatch(r"(?:main|east|west)([+-]\d+)", token):
            return clock.wd(self.cfg, self.T, int(m[1]))
        raise ValueError(f"unknown anchor {token!r}")

    def hop(self, d, token):
        if m := re.fullmatch(r"([+-]\d+)d", token):
            return d + dt.timedelta(int(m[1]))
        if token == "open":
            return clock.wd(self.cfg, d, 1)
        if token == "=open":
            return clock.snap(self.cfg, d)
        if token == "=mon":
            return d + dt.timedelta((7 - d.weekday()) % 7)
        m = re.fullmatch(r"(=|!|<=)?p(\w+)", token)
        if m is None:
            raise ValueError(f"unknown hop {token!r}")
        kind, slot = m[1], m[2]
        if kind in ("=", "<="):
            step = 1 if kind == "=" else -1
            while not self.works(slot, d):
                d += dt.timedelta(step)
            return d
        if kind == "!":
            d += DAY
            while self.works(slot, d) or self.hours(self.site_of(slot), d) is None:
                d += DAY
            return d
        return self.pd(slot, 1, d)

    def day(self, anchor):
        parts = re.split(r">|(?=<=)", anchor.split("@")[0])
        d = self.base(parts[0])
        for token in parts[1:]:
            d = self.hop(d, token)
        return d

    def at(self, anchor, site):
        """The instant of an anchor on the wall clock of `site` (None: the home zone)."""
        d, zone = self.day(anchor), self.zone(site)
        spot = site or "main"
        hours = self.hours(spot, d) or self.hours("main", d) or tuple(
            tuple(map(int, x.split(":"))) for x in self.places[spot]["business_hours"]["mon"][0])
        when = anchor.split("@")[1] if "@" in anchor else "12:00"
        if m := re.fullmatch(r"T-(\d+):(\d\d)", when):
            return (self.t - dt.timedelta(hours=int(m[1]), minutes=int(m[2]))).astimezone(zone)
        if when == "close":
            return dt.datetime.combine(d, dt.time(*hours[1]), zone)
        if m := re.fullmatch(r"([oc])([+-])(\d+):(\d\d)", when):
            edge = dt.datetime.combine(d, dt.time(*hours[0 if m[1] == "o" else 1]), zone)
            delta = dt.timedelta(hours=int(m[3]), minutes=int(m[4]))
            return edge + delta if m[2] == "+" else edge - delta
        h, mi = when.split(":")
        return dt.datetime.combine(d, dt.time(int(h), int(mi)), zone)


def money(value, cfg):
    text = f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"
    return "$" + text if cfg == "en" else text.replace(",", " ").replace(".", ",") + " ₽"


def written(text, c, extra=None):
    """A seed text with `{day:A}`, `{month:A}` (tenant/dates.json: a day in the form `on_day` where the file has one, a
    month in `month_after_<word>` right after that word), `{ledger:key}` (an amount in the tenant's money;
    `{ledger:key.N}` the N-th of a list) and `{name}` from `extra` written out; an unknown name raises Missing."""
    if text is None:
        return None
    names = inputs.load("tenant/dates.json")[c.cfg]

    def one(m):
        kind, arg = m[1], m[2]
        if kind in ("day", "month"):
            d = c.day(arg)
            form = names.get("on_day", names["formats"]["day"]) if kind == "day" else next(
                (names[k] for k in names if k.startswith("month_after_")
                 and re.search(rf"(?:^|\s){re.escape(k[len('month_after_'):])}\s$", text[:m.start()])), names["formats"]["month"])
            return form.format(day=d.day, year=d.year, month=names["months"][d.month - 1], weekday=names["weekdays"][d.weekday()],
                               month_genitive=names.get("months_genitive", names["months"])[d.month - 1])
        if kind == "ledger":
            if arg in inputs.ROWS:
                return money(inputs.value(arg, c.cfg), c.cfg)
            key, n = arg.rsplit(".", 1)
            return str(inputs.value(key, c.cfg)[int(n) - 1])
        if extra and arg in extra:
            return str(extra[arg])
        raise Missing(arg)

    return re.sub(r"\{(?:(day|month|ledger):)?([^{}]+)\}", one, text)


def thread(card, cfg):
    """The chat a hand-over card rests on: (thread key, customer phone) of the story chat its notes name."""
    said = card.get("rests_on", "") + card.get("note", "")
    m = re.search(rf"conversations/{cfg}/(\d+)", said)
    if m is None:
        return None
    story = inputs.STORY_FILES["conversations", cfg][int(m[1])]
    return story["conversations"][0]["thread_key"], story["cast"]["customer"].get("phone")


def plan_cards(cfg, c):
    """The cards as rows; a card whose texts name a value no seed file holds is returned in `skipped`."""
    rows, skipped = [], []
    for card in inputs.load(f"workday/{cfg}/cards.json")["cards"]:
        site = card["site"]
        chat = thread(card, cfg) if card["origin"] == "model" else None
        extra = {"session": chat[0]} if chat else {}
        try:
            texts = {k: written(card[k], c, extra) for k in ("title", "description", "why_now", "origin_ref")}
            trail = [dict(s, body=written(s.get("body"), c, extra)) for s in card["trail"]]
        except Missing as name:  # H-east-waiting rests on a chat of the bank, which this plan leaves out; no file names its visitor
            skipped.append(f"{card['id']}: no seed file holds {{{name}}}")
            continue
        where = lambda by: site if str(by).startswith("A") else c.site_of(by)  # noqa: E731
        wall = lambda anchor: None if anchor is None else (c.at(anchor, site).replace(tzinfo=None), c.places[site]["tz"])  # noqa: E731
        # the deadline the card was written with: the one a later "rescheduled" step moved from, else the file's
        due = next((wall(s["old"]) for s in trail if s["verb"] == "rescheduled"), wall(card["due"]))
        moves = any(s["verb"] in ("moved", "completed") for s in trail)
        if card["origin"] == "model" and not moves and card["state_at_t"] != "backlog":
            # the product files a hand-over to the backlog; whoever takes it moves it where the file says it stands
            taken = next(s for s in trail if s["verb"] == "assigned")
            trail.insert(trail.index(taken) + 1, {"at": taken["at"], "by": taken["by"], "verb": "moved", "to": card["state_at_t"]})
            moves = True
        steps = sorted(({**s, "when": c.at(s["at"], where(s["by"])), "due": wall(s.get("new"))} for s in trail), key=lambda s: s["when"])
        later = [f"{s['verb']} at {s['when']:%Y-%m-%d %H:%M}" for s in steps if s["when"] > c.t]
        if later:  # an anchor of the file that falls after this build's T: the line has not happened yet
            skipped.append(f"{card['id']}: after T, {', '.join(later)}")
        steps = [s for s in steps if s["when"] <= c.t]
        if not steps or steps[0]["verb"] != "created":
            continue
        rows.append({
            "key": card["id"], "kind": card["kind"], "origin": card["origin"], "priority": card["priority"], "site": site,
            "template": card["template"], "phone": chat[1] if chat else None, "session": extra.get("session"), **texts,
            "due": due,
            "first": ("backlog" if card["origin"] == "model" else "unstarted") if moves else card["state_at_t"],
            "trail": steps,
            "quiet": None if not card.get("quiet") else [(slot, c.at(card["quiet"]["asked_at"], c.site_of(slot)))
                                                         for slot in card["quiet"]["asked_of"]],
        })
    return rows, skipped


def clock_span(text):
    return [dt.time(*map(int, x.split(":"))) for x in re.findall(r"(\d\d:\d\d)-(\d\d:\d\d)", text)[0]]


def plan_calendar(cfg, c):
    """The series with their occurrences, and the single entries; every invitation with its answer and attendance."""
    from traciora.core.commands.work import occurrences

    cal = inputs.load(f"workday/{cfg}/calendar.json")
    end_day = c.T + dt.timedelta(14)
    away = {}  # a person's out-of-office days, from their personal entries
    for e in cal["entries"]:
        if e.get("show_as") == "out_of_office":
            first, last = c.day(e["start"]), c.day(e["end"])
            away.setdefault(str(e["organiser"]), set()).update(first + dt.timedelta(i) for i in range((last - first).days + 1))
    notes = {(n["series"], c.day(n["on"])): n["body"] for n in cal["standup_notes"]}
    periods = [c.a["G"] + dt.timedelta(30 * i) for i in range(6)] + [c.T + DAY]
    series = []
    for s in cal["series"]:
        site, zone = s["site"], c.zone(s["site"] if s.get("zone") != "home" else None)
        first = c.day(s["starts"])
        start, end = (dt.time.fromisoformat(s["start"]), dt.time.fromisoformat(s["end"])) if s.get("start") else clock_span(s["when"])
        if s.get("rrule"):
            days = [x.date() for x in occurrences(s["rrule"], dt.datetime.combine(first, start), ends_on=end_day, horizon_days=0)]
        elif "score period" in s["when"]:  # one entry on the first Saturday of each score period
            days = [p + dt.timedelta((5 - p.weekday()) % 7) for p in periods[:-1]]
        else:  # one a week: the invitee's first working weekday (or their working Tuesday or Thursday)
            slot, prefer = str(s["invitees"][0]["slot"]), (1, 3) if "Tuesday or Thursday" in s["when"] else ()
            days = []
            for monday in (first - dt.timedelta(first.weekday()) + dt.timedelta(7 * k) for k in range(60)):
                week = [monday + dt.timedelta(i) for i in range(5) if c.works(slot, monday + dt.timedelta(i))]
                if week:
                    days.append(next((d for d in week if d.weekday() in prefer), week[0]))
        days = [d for d in days if first <= d <= end_day]
        made = dt.datetime.combine(days[0] - DAY, start, zone)
        exceptions = {}
        for x in s.get("exceptions", []):
            if "closed date" in x["occurrence"]:
                exceptions.update({d: ("cancel", made, x["by"]) for d in days if clock.closed(cfg, d)})
            else:
                exceptions[c.day(x["occurrence"])] = (x["action"], c.at(x["at"], c.site_of(x["by"])), x["by"], x.get("start"), x.get("end"))
        coached = {}
        if s["id"] == "COACH-6":
            for n in cal["coaching_notes_slot_6"]:
                held = [d for d in days if periods[n["period"] - 1] <= d < periods[n["period"]] and d not in exceptions]
                if held:
                    coached[held[-1]] = n["body"]
        held = [d for d in days if d < c.T and (exceptions.get(d) or ("replace",))[0] == "replace"]
        regular = [d for d in held if d not in exceptions]
        rows = []
        for n, d in enumerate(days):
            x = exceptions.get(d)
            moved = x if x and x[0] == "replace" else None
            begins = dt.time.fromisoformat(moved[3]) if moved else start
            ends = dt.time.fromisoformat(moved[4]) if moved else end
            answers = []
            for inv in s["invitees"]:
                slot = str(inv["slot"])
                answers.append((slot, inv.get("role", "required"), *answer(cfg, c, inv, slot, d, x, regular, held, away, made, zone)))
            rows.append({"day": d, "key": dt.datetime.combine(d, start).isoformat(timespec="minutes") if s.get("rrule") else str(n),
                         "planned": (dt.datetime.combine(d, start), dt.datetime.combine(d, end)),
                         "start": dt.datetime.combine(d, begins), "end": dt.datetime.combine(d, ends),
                         "cancel": x[1:3] if x and x[0] == "cancel" else None, "move": moved[1:3] if moved else None,
                         "description": written(notes.get((s["id"], d)) or coached.get(d) or s.get("agenda"), c),
                         "answers": answers})
        series.append({"key": s["id"], "kind": s["kind"], "organiser": str(s["organiser"]), "site": site, "zone": str(zone),
                       "rrule": s.get("rrule"), "first": days[0], "made": made, "title": written(s["title"], c), "rows": rows})
    entries = []
    for e in cal["entries"]:
        site, zone = e["site"], c.zone(e["site"])
        booked = c.at(e["booked"], c.site_of(e["organiser"]))
        if e.get("all_day"):
            start = dt.datetime.combine(c.day(e["start"]), dt.time())
            end = dt.datetime.combine(c.day(e["end"]) + DAY, dt.time())
        else:
            start, end = (c.at(e[k], site).replace(tzinfo=None) for k in ("start", "end"))
        answers = []
        for inv in e["invitees"]:
            slot = str(inv["slot"])
            by_rota = inv["response"] == "by_rota"
            said = ("accepted" if c.works(slot, start.date()) else "declined") if by_rota else inv["response"]
            came = inv.get("attended", said == "accepted" if by_rota else None) if start.date() < c.T else None
            answers.append((slot, "required", said, c.at(inv["at"], c.site_of(slot)) if inv.get("at") else booked, came))
        entries.append({"key": e["id"], "kind": e["kind"], "organiser": str(e["organiser"]), "site": site, "zone": str(zone),
                        "start": start, "end": end, "all_day": bool(e.get("all_day")), "show_as": e.get("show_as", "busy"),
                        "card": e.get("card"), "made": booked, "title": written(e["title"], c),
                        "description": written(e.get("agenda"), c), "answers": answers})
    return series, entries


def answer(cfg, c, inv, slot, d, x, regular, held, away, made, zone):
    """(response, answered at, attended) of one invitee on one occurrence (calendar.json invitee rules)."""
    if x and x[0] == "cancel":
        return "invited", None, None
    past = d < c.T
    rule = inv.get("rule", "")
    if "s9.pattern" in rule:
        if not past:
            return "invited", None, None
        sunday = d - dt.timedelta(d.weekday() + 1)
        at = dt.datetime.combine(sunday, dt.time(20, 40), c.zone(c.site_of(slot)))
        if x:  # the moved week: accepted, and he came
            return "accepted", at, True
        said = inputs.value("s9.pattern", cfg)["slot_22_on_regular_occurrences_in_order"]
        said = said[regular.index(d) % len(said)]
        return ("declined", at, None) if said == "declined" else ("accepted", at, said.endswith("came"))
    if rule.startswith("by_rota"):
        ok = c.works(slot, d)
    else:
        ok = d not in away.get(slot, ())
    return ("accepted" if ok else "declined"), made, (ok if past and d in held else None)


def plan_roster(cfg, c):
    """Templates, cover rules, the shifts from the Monday of T's week to T+14 days, the publishes, slot 16's week off
    and the open requests (roster.json, shift_requests.json)."""
    roster = inputs.load("workday/roster.json")
    a, T, cast = c.a, c.T, c.cast
    roles = {r["key"]: r["name"] for r in inputs.load(f"tenant/roles-and-places.{cfg}.json")["roles"]}
    templates = [{"key": f"{t['site']}:{t['name']}", "site": t["site"], "name": t["name"], "position": t["position"],
                  "start": dt.time.fromisoformat(t["start"]), "end": dt.time.fromisoformat(t["end"]),
                  "break": t["break_min"], "active": "active_until" not in t} for t in roster["templates"][cfg]]
    masks = {"Mon-Fri": "1111100", "Sat": "0000010", "every day": "1111111"}
    fix = c.at("W-3.mon@o+0:25", "main")
    coverage = [{"key": f"{r['site']}:{r['position']}:{r['days']}:{r['band'][0]}:{r['min']}", "site": r["site"], "position": r["position"],
                 "mask": masks[r["days"]], "start": dt.time.fromisoformat(r["band"][0]), "end": dt.time.fromisoformat(r["band"][1]),
                 "min": r["min"], "from": c.day(r["valid_from"]) if r.get("valid_from") else None,
                 "to": c.day(r["valid_to"]) if r.get("valid_to") else None} for r in roster["coverage"][cfg]]
    weeks_published = {"main": (a["pub_week"] - c.w0).days // 7, "east": (a["pub_week"] - c.w0).days // 7, "west": 0}
    publisher = {"main": "4", "east": "4", "west": "22"}

    def published_at(site, k):  # the publish of week W+k: home shops Thursday 11:40, west Sunday 20:40 its time
        monday = c.w0 + dt.timedelta(7 * k)
        if site == "west":
            return dt.datetime.combine(monday - DAY, dt.time(20, 40), c.zone(site))
        return dt.datetime.combine(monday - dt.timedelta(4), dt.time(11, 40), c.home)

    def kept(t, d):  # the template's hours on day d (the stocktake day ends at 12:00)
        return t["start"], min(t["end"], dt.time(12)) if d == a["stocktake"] else t["end"]

    def pick(site, position, d, desk=None):
        mine = [t for t in templates if t["site"] == site and t["position"] == position and t["active"]]
        if cfg == "en" and d.weekday() == 5:
            close = c.hours(site, d)[1]
            return next(t for t in mine if (t["end"].hour, t["end"].minute) <= close)
        longest = max(dt.datetime.combine(d, t["end"]) - dt.datetime.combine(d, t["start"]) for t in mine)
        mine = sorted((t for t in mine if dt.datetime.combine(d, t["end"]) - dt.datetime.combine(d, t["start"]) == longest),
                      key=lambda t: t["start"])
        return mine[-1] if desk == "late" else mine[0]

    desks = {}
    if cfg == "en":
        for site, sides in (roster["patterns"]["en"]["desk_shift_since_fix"] | roster["patterns"]["en"]["desk_shift"]).items():
            desks.update({slot: side for side, slots in sides.items() for slot in slots})
    noshow = a["s14_no_show"]
    week = lambda d: f"W{(d - c.w0).days // 7:+d}.{DOW[d.weekday()]}"  # noqa: E731  a shift's key: the same for every T
    week_off = (a["week_off"], a["week_off"] + dt.timedelta(6))
    shifts = []
    days = [c.w0 + dt.timedelta(i) for i in range((T + dt.timedelta(14) - c.w0).days + 1)]
    for slot, p in cast.items():
        if p["status"] != "active" or p["site"] == "none":
            continue
        role = BASE_ROLE.get(p["role_key"], p["role_key"])
        for d in days:
            site = p["site"]
            if cfg == "en" and slot == "29":
                on = d.weekday() == 5 and not clock.closed(cfg, d)
            elif cfg == "en" and d.weekday() == 5:
                on = not clock.closed(cfg, d) and slot in c.saturday_crew(d)
                site = "main"
            elif slot == "21":  # en: one weekday at main, the no-show's day in its week, else the Monday; ru: Tuesday
                monday = d - dt.timedelta(d.weekday())
                main_day = (noshow if noshow - dt.timedelta(noshow.weekday()) == monday else monday) if cfg == "en" else monday + DAY
                on, site = c.works(slot, d), "main" if d == main_day else "east"
            else:
                on = c.works(slot, d)
            if not on:
                continue
            k = (d - c.w0).days // 7
            status = "published" if k <= weeks_published[site] else "draft"
            if slot == "16" and week_off[0] <= d <= week_off[1] and status == "draft":
                continue
            t = pick(site, roles[role], d, desks.get(slot))
            start, end = kept(t, d)
            late = False
            if slot == "28":
                start, end = (dt.time.fromisoformat(x) for x in roster["patterns"][cfg]["slot_28"]["hours"])
                there, hours = c.t.astimezone(c.zone(site)), c.hours(site, d)
                if d == T and hours and there.replace(tzinfo=None) <= dt.datetime.combine(d, dt.time(*hours[1])) - dt.timedelta(hours=2):
                    # at_t.late_now: his shift on T's date starts at the last quarter-hour at least 15 minutes before T
                    begin = there.replace(tzinfo=None) - dt.timedelta(minutes=15)
                    start, late = dt.time(begin.hour, begin.minute - begin.minute % 15), True
                    end = max(end, (dt.datetime.combine(d, start) + dt.timedelta(hours=1)).time())
                end = min(end, dt.time(12)) if d == a["stocktake"] else end
            shifts.append({"key": f"{slot}:{week(d)}", "slot": slot, "site": site, "position": t["position"], "day": d,
                           "start": dt.datetime.combine(d, start), "end": dt.datetime.combine(d, end), "status": status,
                           "week": k, "cancel": None, "late": late})
    open_day = c.day(roster["at_t"]["open_shift"]["day"])
    t = pick("main", roles[TECHNICIAN], open_day)
    k = (open_day - c.w0).days // 7
    shifts.append({"key": f"open:{week(open_day)}", "slot": None, "site": "main", "position": t["position"], "day": open_day,
                   "start": dt.datetime.combine(open_day, kept(t, open_day)[0]), "end": dt.datetime.combine(open_day, kept(t, open_day)[1]),
                   "status": "published" if k <= weeks_published["main"] else "draft", "week": k, "cancel": None, "late": False})
    if noshow >= c.w0:  # slot 21 takes over at east 55 minutes after opening; a shift he held that day is called off
        covered = dt.datetime.combine(noshow, dt.time(*c.hours("east", noshow)[0]), c.zone("east")) + dt.timedelta(minutes=55)
        for s in shifts:
            if s["slot"] == "21" and s["day"] == noshow:
                s["cancel"] = covered
        t = pick("east", roles[TECHNICIAN], noshow)
        shifts.append({"key": f"21:{week(noshow)}:cover", "slot": "21", "site": "east", "position": t["position"], "day": noshow,
                       "start": covered.replace(tzinfo=None), "end": dt.datetime.combine(noshow, kept(t, noshow)[1]),
                       "status": "published", "week": 0, "cancel": None, "late": False, "covered": covered})
    publishes = sorted({(s["site"], s["week"]) for s in shifts if s["status"] == "published"})
    publishes = {key: {"by": publisher[key[0]], "at": published_at(*key)} for key in publishes}
    # a week is drafted a week before its publish, and never after the newest publish of its shop before T
    newest = {site: max(x["at"] for (s, _), x in publishes.items() if s == site) for site in publisher}
    drafted = {(s["site"], s["week"]): min(published_at(s["site"], s["week"]) - dt.timedelta(7), newest[s["site"]]) for s in shifts}
    requests = [{"key": r["id"], "slot": r["slot"], "kind": r["kind"], "shift": f"{r['slot']}:{week(c.day(r['shift']))}", "reason": r["reason"],
                 "filed": c.at(r["filed"]["at"], c.site_of(r["slot"]))}
                for r in inputs.load(f"workday/{cfg}/shift_requests.json")["requests"] if r["status"] == "open"]
    away = [week_off[0] + dt.timedelta(i) for i in range(7)]
    return {"monday": c.w0, "templates": templates, "coverage": coverage, "fix": fix, "shifts": shifts, "publishes": publishes,
            "drafted": drafted, "requests": requests, "away": ("16", away, c.at("p16-3@o+1:00", c.site_of("16")))}


def plan(cfg, a):
    """Every row of the step for configuration `cfg` and the build's anchors `a`, without a database."""
    c = Clock(cfg, a)
    cards, skipped = plan_cards(cfg, c)
    series, entries = plan_calendar(cfg, c)
    return {"clock": c, "cards": cards, "skipped": skipped, "series": series, "entries": entries,
            "roster": plan_roster(cfg, c), "inbox": inputs.load(f"workday/{cfg}/inbox.json")}


class Store:
    """The core rows a write names: people, their actors, shops, positions, the board's columns; ids of this step."""

    def __init__(self, conn, cfg):
        from traciora.core.commands import work
        from traciora.core.security.actors import actor
        from traciora.core.tools.utilities import escalation_tools as esc

        self.conn, self.cfg = conn, cfg
        self.agent = actor(conn, esc.ACTOR_KIND, esc.ACTOR_KEY)
        self.loop = actor(conn, "system", "loop")
        persons = {p["slot"]: self.person(p["slot"]) for p in inputs.load("cast.json")["people"]}
        self.places = {p["key"]: p for p in inputs.load(f"tenant/roles-and-places.{cfg}.json")["places"]}
        self.tz = {key: p["tz"] for key, p in self.places.items()}
        held = dict(conn.execute("select person_id::text, actor_id::text from identity.login where person_id = any(%s::uuid[])",
                                 (list(persons.values()),)).fetchall())
        self.actors = {slot: held[pid] for slot, pid in persons.items() if pid in held}
        self.sites = {key: str(row[0]) for key in ("main", "east", "west")
                      for row in conn.execute("select location_id from core.location_alias where namespace = %s and value = %s",
                                              (CONFIG_KEY, key))}
        self.site_names = {key: conn.execute("select name from core.location where id = %s", (loc,)).fetchone()[0]
                           for key, loc in self.sites.items()}
        self.positions = dict(conn.execute("select name, id::text from core.position").fetchall())
        self.states = {group: work.group_state(conn, group) for group in ("backlog", "started", "completed", "cancelled")}
        self.states["unstarted"] = work.default_state(conn)
        self.handover_template = conn.execute(
            "select id::text from work.work_item_template where pack = %s and name = %s and active",
            (esc.TEMPLATE_PACK, esc.TEMPLATE_NAME)).fetchone()

    def person(self, slot):
        return str(ids.uuid("person", str(slot), self.cfg))

    def id(self, kind, key):
        return str(ids.uuid(kind, key, self.cfg))

    def actor(self, by):
        return self.agent if str(by) == "A" else self.actors[str(by)]


def backdate(conn, table, row_id, at):
    """`created_at` is the row's own instant (DESIGN.md, rule R1); no command takes it."""
    conn.execute(f"update {table} set created_at = %s where id = %s", (at, row_id))


def write_cards(st, cards):
    from traciora.core.commands import work
    from traciora.core.commands.activity import Trace
    from traciora.core.commands.events import emit_event
    from traciora.core.commands.notifications import inbox
    from traciora.core.packs import HANDOVER_REQUESTED
    from traciora.core.security import envelope, tenant_binding
    from traciora.core.tools.utilities import escalation_tools as esc

    conn, rows, skipped = st.conn, 0, []
    for card in cards:
        cid = st.id("card", card["key"])
        for s in card["trail"]:
            by, when, verb = str(s["by"]), s["when"], s["verb"]
            me, trace = st.actor(by), Trace(via="agent") if by == "A" else None
            with tenant_binding.at(when):
                if verb == "created":
                    if card["origin"] == "model":  # what forward_to_manager writes: the event, the card, the card's trigger
                        event = emit_event(
                            conn, me, event_type=HANDOVER_REQUESTED, producer=esc.PRODUCER,
                            producer_event_id_token=envelope.token(esc.PRODUCER, cid), subject_type="work_item", subject_id=cid,
                            occurred_at=when, change_kind="c", location_id=st.sites[card["site"]],
                            payload_public={"type": "escalation" if card["kind"] == "escalation" else "scheduling",
                                            "session_id": card["session"], "phone_token": esc._phone_token(card["phone"] or "")})
                    work.upsert_work_item(
                        conn, me, cid, trace=trace, kind=card["kind"], priority=card["priority"], title_enc=card["title"],
                        description_enc=card["description"], reason_text_enc=card["why_now"], location_id=st.sites[card["site"]],
                        due_local=card["due"] and card["due"][0], due_tz=card["due"] and card["due"][1],
                        state_id=st.states[card["first"]], origin=card["origin"], origin_ref=card["origin_ref"], created_as=me,
                        work_item_template_id=st.handover_template[0] if card["template"] else None)
                    if card["origin"] == "model":
                        work.link_work_item_source(conn, me, cid, event, "trigger")
                    backdate(conn, "work.work_item", cid, when)
                elif verb == "assigned":
                    work.assign_work_item(conn, me, cid, st.person(s["to"]), trace=trace)
                elif verb == "participant_added":
                    work.add_work_participant(conn, me, cid, st.person(s["who"]), s["role"], trace=trace)
                elif verb == "moved":
                    work.move_work_item(conn, me, cid, st.states[s["to"]], at=when, closer=st.person(by), trace=trace)
                elif verb == "completed":
                    work.complete_work_item(conn, me, cid, st.person(by), when, trace=trace)
                elif verb == "comment":
                    work.comment_on_work_item(conn, me, cid, body=s["body"], mentions=[st.person(m) for m in s.get("mentions", [])],
                                              trace=trace, at=when)
                elif verb == "part_done":
                    work.mark_part(conn, me, cid, st.person(by), done=True, at=when, trace=trace)
                elif verb == "rescheduled":
                    work.edit_work_item(conn, me, cid, trace=trace, due_local=s["due"] and s["due"][0], due_tz=s["due"] and s["due"][1])
                else:  # "attached": the file is not in this plan (attachments are left out)
                    skipped.append(f"{card['key']}: {verb} at {when:%Y-%m-%d %H:%M}")
                    continue
            rows += 1
        for slot, at in card["quiet"] or ():  # the daily board pass's question (commands.nudges.nudge_board)
            since = conn.execute("select max(occurred_at) from platform.activity where subject_type = 'work_item' and subject_id = %s"
                                 " and occurred_at < %s", (cid, at)).fetchone()[0]
            rows += inbox.push(conn, st.loop, kind="board.quiet", person_id=st.person(slot), key=f"quiet:{cid}:{since.isoformat()}",
                               at=at, context={"task_id": cid, "days": (at - since).days})
    return rows, skipped


def write_entry(st, eid, e, row, series_id=None):
    """One diary entry with its invitations and answers, each at its own instant."""
    from traciora.core.commands import work
    from traciora.core.security import tenant_binding

    conn, org, site = st.conn, st.actor(e["organiser"]), e["site"]
    start, end = row.get("planned") or (row["start"], row["end"])
    with tenant_binding.at(e["made"]):
        work.upsert_calendar_event(
            conn, org, eid, kind=e["kind"], organiser_id=st.person(e["organiser"]), location_id=site and st.sites[site],
            title_enc=e["title"], description_enc=row.get("description"), start_local=start, end_local=end, tz=e["zone"],
            all_day=e.get("all_day", False), show_as=e.get("show_as", "busy"), work_item_id=e.get("card") and st.id("card", e["card"]),
            series_id=series_id, occurrence_key=series_id and row["key"], origin="ui")
        backdate(conn, "work.calendar_event", eid, e["made"])
        for slot, role, *_ in row["answers"]:
            backdate(conn, "work.calendar_event_participant", work.invite(conn, org, eid, st.person(slot), role).entity_id, e["made"])
    rows = 1 + len(row["answers"])
    if row.get("move"):
        at, by = row["move"]
        with tenant_binding.at(at):
            if series_id:
                work.except_occurrence(conn, st.actor(by), series_id, row["key"], action="replace",
                                       replacement=(row["start"], row["end"], e["zone"]))
            work.upsert_calendar_event(conn, st.actor(by), eid, kind=e["kind"], organiser_id=st.person(e["organiser"]),
                                       location_id=site and st.sites[site], start_local=row["start"], end_local=row["end"],
                                       tz=e["zone"], origin="ui")
    if row.get("cancel"):
        at, by = row["cancel"]
        with tenant_binding.at(at):
            if series_id:
                work.except_occurrence(conn, st.actor(by), series_id, row["key"], action="cancel")
            work.cancel_calendar_event(conn, st.actor(by), eid, at)
    for slot, _, said, at, came in row["answers"]:
        if said != "invited":
            with tenant_binding.at(at):
                work.respond(conn, st.actor(slot), eid, st.person(slot), said, at)
        if came is not None:
            work.record_attendance(conn, org, eid, st.person(slot), came)
    return rows


def write_calendar(st, series, entries):
    from traciora.core.commands import work

    rows = 0
    for s in series:
        sid = st.id("series", s["key"]) if s["rrule"] else None
        if sid:
            work.create_event_series(st.conn, st.actor(s["organiser"]), sid, rrule=s["rrule"], starts_on=s["first"], ends_on=None,
                                     horizon_days=14, materialised_through=s["rows"][-1]["day"])
            backdate(st.conn, "work.event_series", sid, s["made"])
            rows += 1
        for row in s["rows"]:
            rows += write_entry(st, st.id("calendar", f"{s['key']}:{row['key']}"), s, row, sid)
    for e in entries:
        rows += write_entry(st, st.id("calendar", e["key"]), e, e)
    return rows


def write_roster(st, r):
    from traciora.core.commands import roster
    from traciora.core.security import tenant_binding

    conn, rows, publisher = st.conn, 0, {"main": "4", "east": "4", "west": "22"}
    tolerance = inputs.load("workday/roster.json")["templates"]["every_template"]
    for t in r["templates"]:
        roster.upsert_shift_template(conn, st.actor(publisher[t["site"]]), st.id("template", t["key"]), name=t["name"],
                                     location_id=st.sites[t["site"]], position_id=st.positions[t["position"]],
                                     start_time_local=t["start"], end_time_local=t["end"], break_minutes=t["break"],
                                     begin_check_in_before_min=tolerance["begin_check_in_before_min"],
                                     allow_check_out_after_min=tolerance["allow_check_out_after_min"],
                                     late_entry_grace_min=tolerance["late_entry_grace_min"],
                                     early_exit_grace_min=tolerance["early_exit_grace_min"], active=t["active"])
        rows += 1
    with tenant_binding.at(r["fix"]):
        for site in publisher:
            mine = [x for x in r["coverage"] if x["site"] == site]
            roster.set_requirements(conn, st.actor(publisher[site]), location_id=st.sites[site], at=r["fix"], entries=[
                {"id": st.id("coverage", x["key"]), "position_id": st.positions[x["position"]], "day_mask": x["mask"],
                 "start_time_local": x["start"], "end_time_local": x["end"], "min_count": x["min"], "required": True,
                 "valid_from": x["from"], "valid_to": x["to"]} for x in mine])
            rows += len(mine)
    def where(s):
        return dict(location_id=st.sites[s["site"]], position_id=st.positions[s["position"]], business_day=s["day"],
                    start_local=s["start"], end_local=s["end"], tz=st.tz[s["site"]])

    # every shift is first the planner's draft, and a week reaches its people through the product's publish
    cover = [s for s in r["shifts"] if s.get("covered")]
    for s in r["shifts"]:
        if s in cover:
            continue
        at = r["drafted"][(s["site"], s["week"])]
        with tenant_binding.at(at):
            roster.draft_shift(conn, st.actor(publisher[s["site"]]), st.id("shift", s["key"]), person_id=s["slot"] and st.person(s["slot"]),
                               **where(s), at=at)
        rows += 1
    for (site, k), x in sorted(r["publishes"].items(), key=lambda kv: kv[1]["at"]):
        monday = r["monday"] + dt.timedelta(7 * k)
        with tenant_binding.at(x["at"]):
            roster.publish_week(conn, st.actor(x["by"]), location_id=st.sites[site], range_start=monday, range_end=monday + dt.timedelta(6),
                                published_by=st.person(x["by"]), published_at=x["at"])
        rows += 1
    for s in r["shifts"]:
        if s["cancel"]:
            with tenant_binding.at(s["cancel"]):
                roster.cancel_shift(conn, st.actor("4"), st.id("shift", s["key"]), s["cancel"])
    for s in cover:  # slot 21 takes over the no-show's day: his own shift, published alone the moment he does
        sid, at = st.id("shift", s["key"]), s["covered"]
        with tenant_binding.at(at):
            roster.draft_shift(conn, st.actor("4"), sid, person_id=st.person(s["slot"]), **where(s), at=at)
            roster.publish_week(conn, st.actor("4"), location_id=st.sites[s["site"]], range_start=s["day"], range_end=s["day"],
                                published_by=st.person("4"), published_at=at, shift_id=sid)
        rows += 2
    slot, days, at = r["away"]
    with tenant_binding.at(at):
        roster.set_availability(conn, st.actor(slot), person_id=st.person(slot), at=at,
                                entries=[{"kind": "unavailable", "on_date": d} for d in days])
    rows += len(days)
    for q in r["requests"]:
        with tenant_binding.at(q["filed"]):
            roster.file_change_request(conn, st.actor(q["slot"]), shift_id=st.id("shift", q["shift"]), person_id=st.person(q["slot"]),
                                       kind=q["kind"], reason=q["reason"], filed_at=q["filed"])
        rows += 1
    return rows


def clock_in(st, s, latest):
    """The `in` punch of a published shift (roster.punch, the app's), on time: from 12 minutes before its start to 4 after."""
    from traciora.core.commands import roster
    from traciora.core.security import tenant_binding

    sid, place = st.id("shift", s["key"]), st.places[s["site"]]
    start = s["start"].replace(tzinfo=ZoneInfo(place["tz"]))
    at = min(start + dt.timedelta(minutes=ids.number("punch", s["key"], st.cfg) % 17 - 12), latest)
    with tenant_binding.at(at):
        roster.punch(conn=st.conn, actor=st.actor(s["slot"]), log_type="in", person_id=st.person(s["slot"]), location_id=st.sites[s["site"]],
                     at=at, producer_punch_id=f"seed:{sid}:in", coordinates=(place["latitude"], place["longitude"]), shift_id=sid)
    return 1


def write_punches(st, p):
    """Everybody whose published shift holds T has clocked in, but slot 28 (roster.json at_t.late_now)."""
    c = p["clock"]
    return sum(clock_in(st, s, c.t) for s in p["roster"]["shifts"]
               if s["slot"] and not s["late"] and not s["cancel"] and s["status"] == "published"
               and s["start"].replace(tzinfo=c.zone(s["site"])) <= c.t < s["end"].replace(tzinfo=c.zone(s["site"])))


def write_notices(st, p):
    """The operators' pushed lines this store owns (inbox.json): a corrected clock-out to the site's seniors and admins
    (tools.workspace.home_sql.fix_clock_out); the board's quiet questions are written with their cards."""
    from traciora.core.commands import roster
    from traciora.core.commands.notifications import inbox
    from traciora.core.commands.nudges import _seniors
    from traciora.core.security import tenant_binding

    c, rows = p["clock"], 0
    for side in ("junior", "senior"):
        for line in p["inbox"][side]["lines"]:
            if line.get("type") != "punch.corrected":
                continue
            slot = re.search(r"slot (\d+)", line["about"])[1]
            day, at = c.day(line["context"]["business_day"]), c.at(line["at"], c.site_of(slot))
            site = line["context"]["site"]
            shift = st.id("shift", f"{slot}:W{(day - c.w0).days // 7:+d}.{DOW[day.weekday()]}")
            name = next(x[st.cfg]["full_name"] for x in inputs.load("cast.json")["people"] if x["slot"] == slot)
            fix = st.id("punch_fix", f"{slot}:{line['context']['business_day']}")
            worked = next((x for x in p["roster"]["shifts"] if st.id("shift", x["key"]) == shift and x["status"] == "published"), None)
            if worked:  # his clock-in of that day, and the clock-out he gave at his next clock-in
                rows += clock_in(st, worked, at)
                left = dt.datetime.combine(day, dt.time.fromisoformat(line["context"]["left_at_local"]), ZoneInfo(st.tz[site]))
                with tenant_binding.at(at):
                    roster.punch(st.conn, st.actor(slot), log_type="out", person_id=st.person(slot), location_id=st.sites[site], at=left,
                                 producer_punch_id=f"fix:{fix}", producer="web_correction", shift_id=shift)
                rows += 1
            for senior in _seniors(st.conn, st.sites[site], c.T, {}, groups=("senior", "admin")):
                if senior != st.person(slot):
                    rows += inbox.push(st.conn, st.actor(slot), kind="punch.corrected", person_id=senior,
                                       key=f"punch_fix:{fix}", at=at,
                                       context={"business_day": day.isoformat(), "location_id": st.sites[site], "site": st.site_names[site],
                                                "shift_id": shift if worked else None, "left_at_local": line["context"]["left_at_local"]},
                                       secret={"name": name})
    return rows


# The tray's lines about this step's rows, one statement per source of queries.work_board._INBOX, each read as the person
# it is addressed to: (line key, instant, waits). A line that waits (Needs you) is never marked read.
LINES = """
with mine as (
    select wi.id from work.work_item wi
    left join work.work_participant wp on wp.work_item_id = wi.id and wp.person_id = %(p)s::uuid
    where wi.id = any(%(cards)s::uuid[]) and (wi.owner_id = %(p)s::uuid or wp.id is not null))
select a.id::text, a.occurred_at, false from platform.activity a
where a.subject_type = 'work_item' and a.subject_id = any(%(cards)s::uuid[]) and a.actor_id <> %(actor)s::uuid
  and not (a.verb = 'assigned' and a.payload_public ? 'batch')
  and (a.payload_public -> 'mentions' @> to_jsonb(%(p)s::text)
       or (a.subject_id in (select id from mine)
           and (a.verb in ('comment', 'moved', 'reopened', 'completed', 'cancelled', 'participant_added', 'attached', 'detached')
                or a.field in ('title_enc', 'description_enc', 'reason_text_enc', 'priority', 'due_local', 'location_id')))
       or (a.verb in ('assigned', 'participant_added') and a.new_identifier = %(p)s::text))
union all
select cep.id::text, coalesce(cep.responded_at, cep.created_at),
       cep.person_id = %(p)s::uuid and cep.response in ('invited', 'none') and ce.cancelled_at is null
from work.calendar_event_participant cep join work.calendar_event ce on ce.id = cep.event_id
where ce.id = any(%(events)s::uuid[])
  and ((cep.person_id = %(p)s::uuid and ce.organiser_id <> %(p)s::uuid)
       or (ce.organiser_id = %(p)s::uuid and cep.person_id <> %(p)s::uuid and cep.responded_at is not null))
union all
select a.id::text, a.occurred_at, false from platform.activity a
join work.calendar_event_participant cep on cep.event_id = a.subject_id and cep.person_id = %(p)s::uuid
where a.subject_type = 'calendar_event' and a.subject_id = any(%(events)s::uuid[]) and a.verb in ('rescheduled', 'cancelled')
  and a.actor_id <> %(actor)s::uuid
union all
select s.id::text, rp.published_at, false from workforce.shift s join workforce.roster_publish rp on rp.id = s.roster_publish_id
where s.id = any(%(shifts)s::uuid[]) and s.person_id = %(p)s::uuid and s.status in ('published', 'cancelled')
union all
select a.id::text, a.occurred_at, false from platform.activity a
where %(plans)s and a.verb = 'coverage_set' and a.subject_type = 'location' and a.subject_id = any(%(sites)s::uuid[])
  and a.occurred_at = %(fix)s and a.actor_id <> %(actor)s::uuid
union all
select 'due:' || wi.id || ':' || d::date, wi.due_at, false from work.work_item wi
join work.work_state ws on ws.id = wi.state_id
cross join generate_series(%(today)s::date, %(until)s::date, interval '1 day') d
where wi.id in (select id from mine) and wi.due_local::date <= %(today)s::date and ws.state_group in ('completed', 'cancelled')
union all
select 'handover:' || wi.id, wi.created_at, false from work.work_item wi
join work.work_state ws on ws.id = wi.state_id
join work.work_item_source wis on wis.work_item_id = wi.id and wis.role = 'trigger'
where wi.id = any(%(cards)s::uuid[]) and (wi.owner_id is not null or ws.state_group in ('completed', 'cancelled'))
  and wi.updated_at >= (%(today)s::date - 7)::timestamptz
"""


def unread(st, p, side):
    """The keys of the derived lines inbox.json leaves unread for one operator."""
    line_keys, person = set(), st.person(p["inbox"][side]["slot"])
    for line in p["inbox"][side]["lines"]:
        if line["half"] != "update":
            continue
        card = re.search(r"card (\S+?)(?:,|$|\s)", line["about"])
        by = re.search(r"slot (\d+)", line["about"])
        if line["source"] == "activity":
            verb = "assigned" if line["verb"] == "assigned" else "comment"
            line_keys.update(str(r[0]) for r in st.conn.execute(
                "select id from platform.activity where subject_id = %s and verb = %s and actor_id = %s"
                " and (new_identifier = %s or payload_public -> 'mentions' @> to_jsonb(%s::text))",
                (st.id("card", card[1]), verb, st.actor(by[1]), person, person)))
        elif line["source"] == "rota":
            k = int(re.search(r"week W([+-]\d+)", line["about"])[1])
            line_keys.update(st.id("shift", x["key"]) for x in p["roster"]["shifts"]
                             if x["slot"] == str(p["inbox"][side]["slot"]) and x["week"] == k and x["status"] == "published")
        elif line["source"] == "diary":
            entry = re.search(r"entry (\S+)", line["about"])[1]
            line_keys.update(str(r[0]) for r in st.conn.execute(
                "select id from work.calendar_event_participant where event_id = %s and person_id = %s", (st.id("calendar", entry), person)))
    return line_keys


def write_reads(st, p, cards, events, shifts):
    """Every line about this step's rows that the operator has seen: read a set time after it arrived (READ_AFTER), never
    after T; the lines inbox.json leaves unread, and the lines that wait, stay as they are."""
    from traciora.core.commands.notifications import inbox

    c, rows = p["clock"], 0
    # a closed card's deadline line stays a week after the card last changed, which is this build, and its key names the
    # day it is read on: it is marked read for every day from T's to a week after the build
    until = dt.datetime.now(c.home).date() + dt.timedelta(7)
    for side in ("junior", "senior"):
        slot = p["inbox"][side]["slot"]
        person, keep = st.person(slot), unread(st, p, side)
        found = st.conn.execute(LINES, {"p": person, "actor": st.actor(slot), "cards": cards, "events": events, "shifts": shifts,
                                        "today": c.T.isoformat(), "until": until.isoformat(), "sites": list(st.sites.values()), "fix": p["roster"]["fix"],
                                        "plans": side == "senior"}).fetchall()
        for key, at, waits in sorted(found, key=lambda r: (r[1], r[0])):
            if not waits and key not in keep and at is not None and at <= c.t:
                rows += inbox.mark_read(st.conn, st.actor(slot), person_id=person, keys=[key],
                                        at=min(at + dt.timedelta(minutes=READ_AFTER[slot]), c.t))
    return rows


def load(conn, cfg, client_id):
    """Every row of the step in the caller's transaction; (rows written, what was left out)."""
    built = manifest.read(manifest.shop_dsn(client_id))
    if built.get("cfg") != cfg:
        raise SystemExit(f"the shop database is built for {built.get('cfg')}, not {cfg}")
    p = plan(cfg, clock.anchors(cfg, manifest.at()))
    st = Store(conn, cfg)
    cards, skipped = write_cards(st, p["cards"])
    rows = cards + write_calendar(st, p["series"], p["entries"]) + write_roster(st, p["roster"]) + write_punches(st, p) + write_notices(st, p)
    events = [st.id("calendar", f"{s['key']}:{row['key']}") for s in p["series"] for row in s["rows"]]
    rows += write_reads(st, p, [st.id("card", x["key"]) for x in p["cards"]], events + [st.id("calendar", e["key"]) for e in p["entries"]],
                        [st.id("shift", x["key"]) for x in p["roster"]["shifts"]])
    return rows, p["skipped"] + skipped


def keys(cfg):
    """This step's ids by kind, for configuration `cfg`: from the files, and the shifts and single entries any T can give
    (a series' occurrences are found by their series)."""
    cast = [x["slot"] for x in inputs.load("cast.json")["people"]] + ["open"]
    weeks = [f"W{k:+d}.{d}" for k in range(3) for d in DOW]
    uid = lambda kind, key: str(ids.uuid(kind, key, cfg))  # noqa: E731
    cal = inputs.load(f"workday/{cfg}/calendar.json")
    occurrences = [uid("calendar", f"{s['id']}:{n}") for s in cal["series"] for n in range(200)]
    roster = inputs.load("workday/roster.json")
    return {
        "card": [uid("card", x["id"]) for x in inputs.load(f"workday/{cfg}/cards.json")["cards"]],
        "series": [uid("series", s["id"]) for s in cal["series"]],
        "calendar": [uid("calendar", e["id"]) for e in cal["entries"]] + occurrences,
        "shift": [uid("shift", f"{slot}:{w}") for slot in cast for w in weeks] + [uid("shift", f"21:{w}:cover") for w in weeks],
        "template": [uid("template", f"{t['site']}:{t['name']}") for t in roster["templates"][cfg]],
        "coverage": [uid("coverage", f"{r['site']}:{r['position']}:{r['days']}:{r['band'][0]}:{r['min']}") for r in roster["coverage"][cfg]],
        "punch_fix": [uid("punch_fix", f"{s}:{x['context']['business_day']}") for side in ("junior", "senior")
                      for x in inputs.load(f"workday/{cfg}/inbox.json")[side]["lines"] if x.get("type") == "punch.corrected"
                      for s in re.findall(r"slot (\d+)", x["about"])],
        "person16": [uid("person", "16")],
    }


def clear(conn, cfg, client_id):
    """This step's rows of configuration `cfg` that the tenant's role may delete. The append-only tables keep theirs:
    `platform.activity`, `platform.event` (the timelines), `workforce.roster_publish` and `workforce.punch`. Slot 16's
    unavailable dates are the week off of the build in the shop database's manifest."""
    k = keys(cfg)
    built = manifest.read(manifest.shop_dsn(client_id))
    week_off = clock.anchors(cfg, dt.datetime.strptime(built["asked"], manifest.FORMAT))["week_off"] if built else None
    k["away"] = [week_off + dt.timedelta(i) for i in range(7)] if week_off else []
    k["calendar"] += [str(r[0]) for r in conn.execute("select id from work.calendar_event where series_id = any(%s::uuid[])", (k["series"],))]
    subjects = k["card"] + k["calendar"] + k["shift"]
    statements = [
        ("delete from platform.notification_queue where substr(idempotency_key, 38) in"
         " (select id::text from platform.activity where subject_id = any(%(subjects)s::uuid[]))"
         " or substr(idempotency_key, 38) in (select id::text from work.calendar_event_participant where event_id = any(%(calendar)s::uuid[]))"
         " or substr(idempotency_key, 38) = any(%(shift)s::text[])"
         " or split_part(substr(idempotency_key, 38), ':', 2) = any(%(card)s::text[])"
         " or context_public ->> 'task_id' = any(%(card)s::text[]) or context_public ->> 'subject' = any(%(card)s::text[])"
         " or split_part(idempotency_key, ':', 3) = any(%(punch_fix)s::text[])"),
        "delete from platform.notification_alert where payload ->> 'subject' = any(%(card)s::text[])",
        "delete from work.work_item_source where work_item_id = any(%(card)s::uuid[])",
        "delete from work.work_participant where work_item_id = any(%(card)s::uuid[])",
        "delete from work.calendar_event_participant where event_id = any(%(calendar)s::uuid[])",
        "delete from work.event_series_exception where series_id = any(%(series)s::uuid[])",
        "delete from work.calendar_event where id = any(%(calendar)s::uuid[]) or series_id = any(%(series)s::uuid[])",
        "delete from work.event_series where id = any(%(series)s::uuid[])",
        "delete from work.work_item where id = any(%(card)s::uuid[])",
        "delete from workforce.shift_change_request where shift_id = any(%(shift)s::uuid[])",
        "delete from workforce.availability where person_id = any(%(person16)s::uuid[]) and kind = 'unavailable' and on_date = any(%(away)s::date[])",
        "delete from workforce.shift s where id = any(%(shift)s::uuid[]) and not exists (select 1 from workforce.punch p where p.shift_id = s.id)",
        "delete from workforce.coverage_requirement where id = any(%(coverage)s::uuid[])",
        "delete from workforce.shift_template where id = any(%(template)s::uuid[])",
    ]
    for statement in statements:
        conn.execute(statement, k | {"subjects": subjects})
    return conn.execute("select count(*) from platform.activity where subject_id = any(%s::uuid[])", (subjects,)).fetchone()[0]


def step(cfg, client_id, replace):
    from traciora.core.core_db.engine import connect, tenant_dsn

    with connect(tenant_dsn(client_id)) as conn:
        # an earlier build leaves its timeline, which no command removes: --replace cannot start over on top of it
        left = conn.execute("select count(*) from platform.activity where subject_id = any(%s::uuid[])",
                            ([x for c in ("en", "ru") for kind in ("card", "calendar", "shift") for x in keys(c)[kind]],)).fetchone()[0]
        if left:
            raise SystemExit(f"the core database holds {left} timeline rows of an earlier workday build, which are append-only"
                             " for the tenant's role and no command removes: rebuild the core database first")
        if replace:
            for c in ("en", "ru"):
                clear(conn, c, client_id)
        rows, skipped = load(conn, cfg, client_id)
        conn.commit()
    for item in skipped:
        print(f"SEED workday {cfg} left out: {item}")
    return rows


def reset(cfg, client_id):
    """Both configurations' rows the tenant's role may delete (clear)."""
    from traciora.core.core_db.engine import connect, tenant_dsn

    with connect(tenant_dsn(client_id)) as conn:
        for c in ("en", "ru"):
            clear(conn, c, client_id)
        conn.commit()
