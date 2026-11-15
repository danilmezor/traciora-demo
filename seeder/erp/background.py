"""Section 4 of generator-spec.md, 4.2 to 4.7 and 4.9, after the day plan: `fill(b)` takes `plan.plan(b)`'s orders and
their jobs (`plan.content`), gives them their mechanics (4.2), comebacks (4.6), bookings (section 3, appointment) and
money (4.7), writes them through `orders.order`, re-issues slot 7's bills (4.5) and closes the tills (4.9).
`orders.finish` writes their history, time entries and payments once every later step has had its say.

The background stops where a later step starts: no `waiting_parts` (the parts step calls `orders.wait`), no deposit on
special-order parts (4.10), no statement payments (account orders are placed by their step with `pay=None`), and no
story behaviour: slot 16's days off, F1's cash share, discounts, voids and till shortfalls, the leave's eleven orders
sent to east, the waiting cars and the never-closed orders are planted by section 5; F1 gets his ordinary share by the
background rows."""
import bisect
import collections
import datetime as dt
import itertools
import re
from decimal import Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, orders, reference, stories
from seeder.erp.plan import JOBS, MIX, PRICED, SHARES, SITES, allowed, approve, block, by, content, deal, half_uniform, moment, month_of, plan, slot_key, window

MOVERS = [p["slot"] for p in reference.CAST["people"] if slot_key(p["slot"], "billed_index") in inputs.ROWS]  # the mechanics with a row
PHRASES = {}  # job key: what a customer says about it (the phrase bank of calls/bank-<cfg>/job-blocks.json)
for _cfg in ("en", "ru"):
    for _block in inputs.load(f"calls/bank-{_cfg}/job-blocks.json")["jobs"]:
        for _key in filter(None, (_block["catalogue"]["price"], _block["catalogue"]["price_alt"])):
            PHRASES.setdefault((_cfg, _key), []).extend(x["need"] for x in _block["customer_says"])


def hours_of(b, p):
    """An order's approved sold hours, the en courtesy line's 0.1 hour among them."""
    return sum(float(orders.sold_hours(b.cfg, j["key"], p["vehicle"])) for j in p["jobs"] if j["status"] == "approved")


def work_day(b, p):
    """The day an order's work is done: the day its wait ends, else the day the car and its parts are in (`eta`,
    parts.install), or the next open day when that is within the last hour of the mechanics' shift."""
    if p.get("start"):
        return p["start"].date()
    t = orders.opening(b, p["site"], max([p["at"]] + [p["eta"]] * bool(p.get("eta"))))
    end = orders.shift(b, p["site"], t.date())[1]
    return orders.opening(b, p["site"], end).date() if t >= end - dt.timedelta(hours=1) else t.date()


def fill(b):
    cfg, a, seed = b.cfg, b.a, b.seed
    every, counts, known, fixed = plan(b)
    content(b, every, fixed)

    waits(b, every, fixed)  # a first time, so that the mechanics are dealt on the days the work is done

    # an order of the last open day before T's day comes in early enough for its work to be done that day (spec 4.5)
    for p in every:
        end = orders.shift(b, p["site"], p["day"])[1]
        if p["visit"] and p["day"] < a["T"].date() <= orders.opening(b, p["site"], orders.hours(b, p["site"], p["day"])[1]).date() and not p.get("start"):
            latest = max(orders.hours(b, p["site"], p["day"])[0], end - dt.timedelta(hours=hours_of(b, p) * 0.9 + 2.75))  # its work and two hours of others ahead of it
            if p["at"] > latest:
                if p.get("returning") is False:
                    p["customer"]["created_at"] -= p["at"] - latest
                p["at"] = latest.replace(second=0, microsecond=0)
    technicians(b, every, fixed)
    drift = waited(b, every, fixed)  # the packed days moved the waits: the plan once more, the drift taken back
    if any(abs(x) > 0.02 for x in drift.values()):
        for p in every:
            p.pop("reach", None)
            p.pop("start", None)
        waits(b, every, fixed, drift)
        technicians(b, every, fixed)
    pad_cells(b, every, fixed)
    comebacks(b, every, fixed)
    leave_hours(b, every, fixed)
    waits(b, every, fixed)  # again over the orders as they now stand: comebacks and moved raised jobs
    bookings(b, every, known, counts)
    sold_value(b, every, fixed)
    # the comebacks moved raised jobs between visits and the leave's hours took visits away: each advisor's count again
    approve(b, [p for p in every if p["visit"]], fixed, again=True)
    money(b, every, fixed)
    # the dealt mechanic does the order's work, on a later day of his when his day is full (his hours and comebacks are
    # dealt on it); `orders.book` lets it go only after a week, or before T's day to whoever has room
    for p in every:
        for j in p["jobs"]:
            j["keep"] = j.get("keep") or True
    # in the order `technicians` planned the mechanics' days, so each order's work lands where it was dealt (a
    # diagnostic job on the day the diagnostician's cap counted it), the waiting orders before all others: their work
    # begins when the wait ends (in_progress, spec 4.5)
    def place(p):
        if p["kind"] == "comeback":
            # it comes in once its first order is done, the shortest gap of erp.comeback.gap_days after it, however long
            # that one waited for its mechanic: on the next day its advisor writes orders (ru inside the 30 days of
            # comeback.definition, and early enough to close by T; else it stays where it was dealt)
            done = next((h["changed_at"] for h in b.orders[id(p["first"]["order"])]["history"] if h["status"] == "completed"), None)
            soonest = done and done + dt.timedelta(inputs.value("erp.comeback.gap_days", cfg)["min"])
            if soonest and p["at"] < soonest:
                last = min([a["T"].date() - dt.timedelta(3)] + [p["first"]["order"]["opened_at"].date() + dt.timedelta(30)] * (cfg == "ru"))
                day = next((d for d in (soonest.date() + dt.timedelta(i) for i in range((last - soonest.date()).days + 1))
                            if p["advisor"] in orders.advisors(b, p["site"], d) and not (cfg == "en" and p["site"] == "main" and d.weekday() == 5)), None)
                if day:
                    open_, close = orders.hours(b, p["site"], day)
                    p["day"], p["at"] = day, min(max(dt.datetime.combine(day, p["at"].time()), soonest, open_), close - dt.timedelta(hours=1))
        x = JOBS[p["jobs"][0]["key"]][cfg]
        said = PHRASES.get((cfg, p["jobs"][0]["key"]))
        complaint = None
        if p["kind"] != "comeback":
            complaint = streams.pick(streams.stream(seed, "complaint", p["at"]), said) if said else x["name"]
            female = p["customer"]["kind"] == "person" and any(t in customers.NAMES[cfg]["given"]["female"] for t in p["customer"]["name"].title().split())
            complaint = re.sub(r"\{c:([^|}]*)\|([^}]*)\}", lambda m: m[2 if female else 1], complaint).replace("{car_model}", p["vehicle"]["model"])
            complaint = complaint[0].upper() + complaint[1:]
        p["order"] = orders.order(b, p["site"], p["at"], p["customer"], p["vehicle"], p["advisor"], p["jobs"],
                                  kind="warranty" if p["kind"] == "comeback" else "customer_pay", comeback_of=p.get("first", {}).get("order"),
                                  pay=p.get("pay"), discount=p.get("discount"), void=p.get("void"), booking=p.get("booking"), start=p.get("start"),
                                  complaint=complaint)
    for p in sorted(every, key=lambda p: (not p.get("start"), p.get("seq", -1))):
        place(p)

    # an order of an earlier day whose work its shop's mechanics cannot fit before T is not opened (spec 4.5: the work on
    # hand exceeds the crews), a comeback included: its customer holds an appointment for the next half hour the shop is
    # open after T, its day has one order fewer
    gone = set()
    for p in every:
        if p["day"] < orders.until(b, p["site"]).date() and p["order"]["status"] not in ("invoiced", "paid", "void", "declined") \
                and not (p["kind"] == "comeback" and any(j["key"] in orders.PADS for j in p["jobs"])):  # (a pad comeback is s6.counts')
            record = b.orders.pop(id(p["order"]))
            for tech, piece in record["booked"]:
                b.timeline[id(tech), piece[0].date()].remove(piece)
            gone.update(id(r) for r in [p["order"], record["appointment"], record["inspection"], *record["items"], *record["labor"], *record["parts"],
                                        *record["sublets"], *record["fees"], *(j["row"] for j in record["jobs"])] if r is not None)
            T_ = orders.until(b, p["site"])
            starts = orders.opening(b, p["site"], T_.replace(minute=0, second=0, microsecond=0) + dt.timedelta(minutes=30 if T_.minute < 30 else 60))
            if starts > orders.hours(b, p["site"], starts.date())[1] - dt.timedelta(hours=1):
                starts = orders.opening(b, p["site"], orders.hours(b, p["site"], starts.date())[1])
            lead = p["jobs"][0]
            b.add("appointment", location_id=b.shops[p["site"]], customer_id=p["customer"], vehicle_id=p["vehicle"], starts_at=starts,
                  duration_min=max(30, -(-int(float(orders.sold_hours(cfg, lead["key"], p["vehicle"])) * 60) // 30) * 30), source="phone",
                  status="confirmed" if starts - a["T"] <= dt.timedelta(2) else "booked", reason=JOBS[lead["key"]][cfg]["name"],
                  booked_at=p["at"], booked_by_id=b.people[p["advisor"]])
    every[:] = [p for p in every if id(p["order"]) not in gone]
    if gone:
        for name, rows in b.tables.items():
            b.tables[name] = [r for r in rows if id(r) not in gone]
    for p in every:
        b.orders[id(p["order"])]["movable"] = p["visit"] and p["kind"] in ("private", "small", "walkin") and not any(
            p["site"] == "west" and j["key"] in orders.PADS for j in p["jobs"])  # (west's pad jobs are dealt per fitter: s6.counts)
    billed(b)
    rebilled(b, every, fixed)
    till(b)


def billed(b, exact=False):
    """4.2, read as checks.sql reads pNN.billed_index: a mechanic's sold hours on the orders opened in the last 90 days
    over the days he clocked in then (en weekdays), against the norm of his shop and its season there (its billed hours
    per open day in the 90 days over the 12 months); F2 and F4 over all their days, no season. The work was dealt on the
    days as planned; the days' timelines leave each a little off his row, so whole orders move between two mechanics
    on duty that day, the one over his row giving, while that brings both nearer: the receiver books them where he
    has room on that day, the order's hours, shop and day stay; only background orders with no west pad job move, a
    waiting order only when its work still begins when the wait ends, a lead diagnostic job not past the
    diagnostician's cap (a day past it gives its later ones away first); then the comebacks are dealt on who did the
    work. `exact`: after the parts step, which moves some
    work on, only to one who clocks the same minutes and is free at those very minutes, so nothing else changes."""
    cfg, T = b.cfg, b.a["T"]
    since, year = T - dt.timedelta(90), clock.months_back(T.date(), 12)
    norm = {s: inputs.value(f"volume.norm.{s}", cfg) / (1 if cfg == "en" else 21.74) for s in SITES}
    weekday = (lambda t: True) if cfg == "ru" else (lambda t: t.weekday() < 5)
    rows = {id(r): s for s, r in b.people.items() if s in MOVERS} | {id(r): "F4" for r in b.seasons}
    home = {p["slot"]: p["site"] for p in reference.CAST["people"] if p["slot"] in MOVERS}
    whole = {"F2", "F4"}  # read over all their days, as checks.sql reads them
    factor = inputs.value("erp.time.clocked_over_sold", cfg)

    def lines(record):  # (mechanic, hours) of the order's approved labour
        return [(l["technician_id"], float(l["hours"])) for l in record["labor"] if l["technician_id"] is not None and l["order_job_id"]["status"] == "approved"]
    shop = collections.defaultdict(float)
    days_of = collections.defaultdict(set)
    hours, clocked = collections.Counter(), collections.defaultdict(collections.Counter)
    for record in b.orders.values():
        ro = record["order"]
        if ro["status"] in ("declined", "void"):
            continue
        at = ro["opened_at"]
        for tech, h in lines(record):
            if at.date() > year and weekday(at):
                shop[record["site"], at > since] += h
                days_of[record["site"], at > since].add(at.date())
            s = rows.get(id(tech))
            if s and (s in whole or at > since and weekday(at)):
                hours[s] += h
        for e in record["entries"]:
            s = rows.get(id(e["technician_id"]))
            if s and (s in whole or e["clock_in"] > since and weekday(e["clock_in"])):
                clocked[s][e["clock_in"].date()] += 1
    season = {site: shop[site, True] / len(days_of[site, True]) / ((shop[site, True] + shop[site, False]) / len(days_of[site, True] | days_of[site, False]))
              for site in SITES if days_of[site, True]}

    def off(s):  # his reading less his row, squared: a shop's shortfall is shared out evenly
        unit = norm[home[s]] * (1 if s in whole else season[home[s]]) * max(len(clocked[s]), 1)
        return (hours[s] / unit - inputs.value(slot_key(s, "billed_index"), cfg)) ** 2

    def pace(s):
        return factor.get(f"slot {s}", factor["everyone"])
    # the comebacks are dealt on the mechanic who did the work (spec 4.2): after the moves, each mechanic's orders with a
    # comeback come to round(n x pNN.comebacks) of his n orders in the row's window, as `comebacks` reads it
    f2_since = clock.months_back(b.people["F2"]["left_on"], 6)
    soon = T - dt.timedelta(inputs.value("erp.comeback.gap_days", cfg)["min"])  # (the row reads orders completed by then)

    def windowed(s, record):
        at = record["order"]["opened_at"]
        done = next((h["changed_at"] for h in record["history"] if h["status"] == "completed"), None)
        return (s == "27" and not any(j["key"] in orders.PADS and j["status"] == "approved" for j in record["jobs"]) or s == "F2" and at.date() >= f2_since
                or s not in ("27", "F2", "F4") and at > dt.datetime.combine(year, T.time()) and done is not None and done <= soon)
    rate = {s: 0 if s == "F4" else inputs.value("s6.rate.other_work.p27" if s == "27" else slot_key(s, "comebacks"), cfg) / 100 for s in MOVERS}
    firsts, came = collections.Counter(), collections.Counter()
    back = {id(o["order"]["comeback_of_id"]) for o in b.orders.values() if o["order"]["comeback_of_id"]}

    def lead(record):  # the order's lead job when it is a diagnostic one (kb.schedule.diagnostics_and_weekends counts those)
        j = record["jobs"][0]
        return j["status"] == "approved" and JOBS[j["key"]]["category"] == "diagnostics"
    looked = collections.Counter()  # the diagnosticians' lead diagnostic jobs a day, by the day each is begun
    for record in b.orders.values():
        hrs = collections.Counter()
        for tech, x in lines(record):
            hrs[id(tech)] += x
        s = rows.get(max(hrs, key=hrs.get)) if hrs else None
        if s and not record["order"]["comeback_of_id"] and record["order"]["status"] in ("invoiced", "paid") and windowed(s, record):
            firsts[s] += 1
            came[s] += id(record["order"]) in back
        if lead(record):
            e = next((e for e in record["entries"] if e["order_job_id"] is record["jobs"][0]), None)
            if e:
                looked[orders.slot_of(b, e["technician_id"]), e["clock_in"].date()] += 1
    cap = {slot: n for slot, n in orders.DIAGNOSTICIAN.values()}

    def tally(s, record, sign):  # the order in or out of s's readings
        at = record["order"]["opened_at"]
        if windowed(s, record):
            firsts[s] += sign
            came[s] += sign * (id(record["order"]) in back)
        looked[s, record["entries"][0]["clock_in"].date()] += sign * lead(record)
        if s in whole or at > since and weekday(at):
            hours[s] += sign * sum(x for _, x in lines(record))
        for e in record["entries"]:
            if s in whole or e["clock_in"] > since and weekday(e["clock_in"]):
                clocked[s][e["clock_in"].date()] += sign
                if not clocked[s][e["clock_in"].date()]:
                    del clocked[s][e["clock_in"].date()]

    def over(s):  # his orders that came back less his row's share of his orders, in cases
        return came[s] - firsts[s] * rate[s]

    def strain(g, r):  # how far the two stand beyond one case of their shares (F2 half a case: S14.5 reads his exactly)
        return sum(max(0.0, abs(over(s)) - (0.5 if s == "F2" else 1.0)) for s in (g, r))

    def spread(g, r):  # the two's distance from their shares, F2's first
        return sum(over(s) ** 2 * (100 if s == "F2" else 1) for s in (g, r))

    def moved_to(g, r, record, measure):  # `measure` of the two once the order is r's
        tally(g, record, -1)
        tally(r, record, 1)
        out = measure(g, r)
        tally(r, record, -1)
        tally(g, record, 1)
        return out

    def better(g, r, record):
        """Would the order's move from g to r bring the two nearer their rows, together, and leave neither further
        than one case from his comeback share?"""
        return moved_to(g, r, record, strain) <= strain(g, r) + 1e-9 and moved_to(g, r, record, lambda g, r: off(g) + off(r)) < off(g) + off(r) - 1e-6

    def single(record):  # (its mechanic, his row, its day) for an order one mechanic did in a day, else None
        if not record.get("movable") or record["order"]["status"] not in ("invoiced", "paid") or not record["entries"]:
            return None
        techs = {id(t) for t, _ in lines(record)} | {id(e["technician_id"]) for e in record["entries"]}
        day, last = record["entries"][0]["clock_in"].date(), record["entries"][-1]
        if (len(techs) != 1 or id(last["technician_id"]) not in rows or last["clock_out"] is None or last["clock_out"].date() != day
                or any(j["sublet"] for j in record["jobs"] if j["status"] == "approved")):
            return None
        return rows[id(last["technician_id"])], last["technician_id"], day

    def move(record, g, giver, r, row, day):
        """The order's work from g to r on its day: `exact`, at the same minutes; else booked where r has room that day,
        a waiting order's work still begun when its wait ends. Returns whether it moved."""
        if r in cap and lead(record) and looked[r, day] >= cap[r]:
            return False
        start, end = orders.shift(b, record["site"], day)
        if sum(x for _, x in lines(record)) * pace(r) * 60 > (end - start).total_seconds() / 60:
            return False  # more than his shift at his pace: the work would not stay on its day
        if exact:
            if pace(g) != pace(r) or any(orders.free(b, row, day, e["clock_in"], e["clock_out"], e["clock_out"] - e["clock_in"]) != e["clock_in"] for e in record["entries"]):
                return False
            tally(g, record, -1)
            for _, piece in record["booked"]:
                b.timeline[id(giver), day].remove(piece)
                bisect.insort(b.timeline.setdefault((id(row), day), []), piece)
            record["booked"] = [(row, piece) for _, piece in record["booked"]]
            for x in record["entries"] + [line for line in record["labor"] if line["technician_id"] is giver]:
                x["technician_id"] = row
            for j in record["jobs"]:
                if j.get("tech") is not None:
                    j["tech"] = row
            tally(r, record, 1)
            return True
        kept = {k: record[k] for k in ("history", "entries", "payments", "booked", "left", "deposit", "leaving") if k in record}
        status, begun = record["order"]["status"], record["entries"][0]["clock_in"]
        techs = [(j, j.get("tech"), j.get("labor_row") and j["labor_row"]["technician_id"]) for j in record["jobs"]]
        tally(g, record, -1)
        for j in record["jobs"]:
            if j.get("tech") is not None:
                j["tech"] = row
        orders.settle(b, record)
        if (record["order"]["status"] in ("invoiced", "paid") and all(e["technician_id"] is row and e["clock_in"].date() == day for e in record["entries"])
                and not (record["start"] and record["entries"][0]["clock_in"] != begun)):
            tally(r, record, 1)
            return True
        for tech, piece in record["booked"]:  # back as it was
            b.timeline[id(tech), piece[0].date()].remove(piece)
        for tech, piece in kept["booked"]:
            bisect.insort(b.timeline.setdefault((id(tech), piece[0].date()), []), piece)
        record.pop("leaving", None)
        record.update(kept)
        record["order"]["status"] = status
        for j, tech, row_tech in techs:
            j["tech"] = tech
            if row_tech is not None:
                j["labor_row"]["technician_id"] = row_tech
        tally(g, record, 1)
        return False

    def crew(record, day, g):
        return sorted(((s, x) for s, x in orders.mechanics(b, record["site"], day) if s in rows.values() and s != g), key=lambda x: x[0])
    movable = sorted((o for o in b.orders.values() if o.get("movable")), key=lambda o: o["order"]["opened_at"])
    # a diagnostician's day past his cap gives its later lead diagnostic orders to whoever has room
    for record in movable:
        x = single(record)
        if x and x[0] in cap and lead(record) and looked[x[0], x[2]] > cap[x[0]]:
            g, giver, day = x
            any(r not in cap and move(record, g, giver, r, row, day) for r, row in crew(record, day, g))
    for _ in range(6):
        moved = False
        for record in movable:
            x = single(record)
            if x:
                g, giver, day = x
                moved |= any(better(g, r, record) and move(record, g, giver, r, row, day) for r, row in crew(record, day, g))
        if not moved:
            break
    # the comebacks: an order that came back goes, on its day, from its mechanic to another on duty while that brings
    # the two nearer their rows' shares of their orders (`spread`), so each ends within a case of his share and later
    # steps that take an order or two away (M4, F1's voids, a late part) leave him there
    for _ in range(8):
        moved = False
        for record in movable:
            x = single(record)
            if not x or id(record["order"]) not in back or not windowed(x[0], record):
                continue
            g, giver, day = x
            moved |= any(windowed(r, record) and moved_to(g, r, record, spread) < spread(g, r) - 1e-9 and move(record, g, giver, r, row, day)
                         for r, row in crew(record, day, g))
        if not moved:
            break


def wait_groups(b, every, fixed):
    """The diagnostic orders at main (an approved diagnostic job: a declined one waits for nobody), in and out of the
    diagnostician's leave, each group with its row's mean wait in days (s5.leave) and the sum of what the orders already
    there waited."""
    a, leave = b.a, inputs.value("s5.leave", b.cfg)
    waiting = [p for p in every + fixed if p["site"] == "main" and p["visit"]
               and any(JOBS[j["key"]]["category"] == "diagnostics" and j["status"] == "approved" for j in p["jobs"])]
    return [(in_leave, both, leave["wait_days_in_leave"] if in_leave else leave["wait_days_normal"],
             sum((next((h["changed_at"] for h in v["record"]["history"] if h["status"] == "in_progress"), v["at"]) - v["at"] for v in both if v.get("fixed")), dt.timedelta()))
            for in_leave, both in by(lambda p: a["leave_from"] <= p["day"] <= a["leave_to"], waiting).items()]


def waited(b, every, fixed):
    """Each group's mean wait as the orders now stand, less its row, in days."""
    return {in_leave: ((there + sum(((p["start"] - p["at"]) if p.get("start") else dt.timedelta(hours=0.5) for p in both if not p.get("fixed")), dt.timedelta()))
                       / len(both)).total_seconds() / 86400 - mean for in_leave, both, mean, there in wait_groups(b, every, fixed)}


def waits(b, every, fixed, offset=None):
    """4.5: diagnostic orders at main (`wait_groups`) wait for the diagnostician, the work starting at a minute of the
    mechanics' shifts within twice s5.leave.wait_days_normal
    of the check-in (in the leave weeks wait_days_in_leave; spec section 7b), the minutes dealt evenly over the shift time
    in reach in each of the two groups, the reach fitted so the group's mean wait is its row with the orders already
    there (account orders start at check-in) counted; an order of an earlier day never waits into T's day (it starts
    after its look)."""
    cfg, a, seed = b.cfg, b.a, b.seed
    groups = wait_groups(b, every, fixed)

    def works(day):  # a day of diagnostic work at main: open, and en not its Saturday (kb.schedule.diagnostics_and_weekends)
        return orders.hours(b, "main", day) and not (cfg == "en" and day.weekday() == 5)

    def start_of(p, x, reach):
        # (early enough in a shift for the first job to be done before it ends, else the work would wait for the next day)
        need = dt.timedelta(hours=float(orders.sold_hours(cfg, p["jobs"][0]["key"], p["vehicle"])) * inputs.value("erp.time.clocked_over_sold", cfg)["everyone"])
        spans, day = [], p["at"].date()
        while day <= (p["at"] + reach).date():
            if works(day):
                lo, hi = orders.shift(b, "main", day)
                lo, hi = max(lo, p["at"] + 20 * orders.MINUTE), min(hi - need, p["at"] + reach)
                if hi > lo:
                    spans.append((lo, hi))
            day += clock.DAY
        point = x * sum((hi - lo for lo, hi in spans), dt.timedelta())
        for lo, hi in spans:
            if point < hi - lo:
                start = (lo + point).replace(second=0, microsecond=0)
                break
            point -= hi - lo
        else:  # no shift time within reach: the next shift time
            start, day = p["at"] + 20 * orders.MINUTE, p["at"].date()
            while not (works(day) and start < orders.shift(b, "main", day)[1]):
                day += clock.DAY
                start = dt.datetime.combine(day, dt.time())
            start = max(start, orders.shift(b, "main", day)[0])
        return start if start.date() < a["T"].date() or p["day"] == a["T"].date() else None
    for in_leave, both, mean, there in groups:
        mean -= (offset or {}).get(in_leave, 0)  # (`technicians` packs the diagnostician's day: what that moved, the plan takes back)
        # (on the second pass the orders that have their wait keep it, their mechanics were dealt on it; the others
        # join at the reach found)
        group = [p for p in both if not p.get("fixed") and "reach" not in p]
        reach = next((p["reach"] for p in both if "reach" in p), None)
        spread = [(i + 0.5) / len(group) for i in range(len(group))]
        streams.stream(seed, "wait", in_leave, reach is None).shuffle(spread)
        low, high = 0.5, 8.0
        for _ in range(16 if reach is None else 1):
            k = reach or (low + high) / 2
            starts = [start_of(p, x, dt.timedelta(days=2 * mean * k)) for p, x in zip(group, spread)]
            waited = (there + sum(((s - p["at"]) if s else dt.timedelta(hours=0.5) for p, s in zip(group, starts)), dt.timedelta())) / len(both)
            low, high = (k, high) if waited < dt.timedelta(days=mean) else (low, k)
        for p, start in zip(group, starts):
            p["reach"] = k
            if start:
                p["start"] = start
    held = {id(p) for _, both, _, _ in groups for p in both}
    for p in every:  # a comeback that took the place of a waiting visit carries its own job
        if p.get("start") and id(p) not in held:
            del p["start"]


def leave_hours(b, every, fixed):
    """S05 (s5.leave_drop_pct, spec S05): main's billed hours a week on the orders opened in the diagnostician's leave
    stand the row under the mean week of the four weeks before, as the statement reads them. `plan.plan` scales the
    leave's day counts to a little above that; here returning customers' visits of those days (none a comeback holds)
    are taken out, in a dealt order, while that brings the hours nearer."""
    a = b.a
    before = (a["leave_from"] - dt.timedelta(28), a["leave_from"] - clock.DAY)
    main = [p for p in every + fixed if p["site"] == "main" and p["visit"]]

    def hours(p):
        if p.get("fixed"):
            return sum(float(j["labor"]["hours"]) for j in p["jobs"] if j["status"] == "approved" and j.get("labor"))
        return hours_of(b, p)
    week = sum(hours(p) for p in main if before[0] <= p["day"] <= before[1]) / 4
    target = 2 * week * (1 - inputs.value("s5.leave_drop_pct", b.cfg) / 100)
    during = [p for p in main if a["leave_from"] <= p["day"] <= a["leave_to"]]
    now = sum(hours(p) for p in during)
    spare = [p for p in during if not p.get("fixed") and p["kind"] == "private" and p.get("returning") and not p.get("start")  # (a waiting order stays: the waits' mean is fitted on them)
             and not any(j.get("keep") or j["key"] in orders.PADS and j["status"] == "approved" for j in p["jobs"])]  # a pad job stays: s6.counts
    streams.stream(b.seed, "leave hours").shuffle(spare)
    out = set()
    for p in spare:
        if abs(now - hours(p) - target) < abs(now - target):
            now -= hours(p)
            out.add(id(p))
    every[:] = [p for p in every if id(p) not in out]


def sold_value(b, every, fixed):
    """S05 (s5.order_value_drop): at east from G the raised work sold per order on slot 16's days stands the row above
    the other days, before tax. The approvals dealt per advisor and block (`plan.approve`) keep their counts: inside a
    group an approved raised job and a declined one trade places, the best trade first, until each kind of day holds the
    sum the row gives it with the shop's sold raised work unchanged."""
    cfg, a = b.cfg, b.a
    rate = 1 + orders.tax_rate(b, "east", a["G"]) / 100 if cfg == "ru" else 1
    gap = Decimal(str(inputs.value("s5.order_value_drop", cfg))) * rate
    visits = [p for p in every + fixed if p["site"] == "east" and p["visit"] and p["kind"] != "comeback" and a["G"] <= p["day"] < a["T"].date()]
    for p in visits:
        if not p.get("fixed"):
            for j in p["jobs"]:
                if j.get("found"):
                    orders.price(b, p["day"], p["customer"], p["vehicle"], j)
    hers = {d: "16" in orders.advisors(b, "east", d) for d in {p["day"] for p in visits}}
    side = by(lambda p: hers[p["day"]], visits)
    if len(side) < 2:
        return
    have = {h: sum(j["value"] for p in group for j in p["jobs"] if j.get("found") and j["status"] == "approved") for h, group in side.items()}
    n = {h: len(group) for h, group in side.items()}
    want = {True: (gap + (have[True] + have[False]) / n[False]) / (Decimal(1) / n[True] + Decimal(1) / n[False])}
    want[False] = have[True] + have[False] - want[True]
    for h, group in side.items():
        pools = []
        for _, mine in by(lambda p: (p["advisor"], window(b, p)), [p for p in group if not p.get("fixed")]).items():
            found = [j for p in mine for j in p["jobs"] if j.get("found") and not j.get("keep") and j["key"] not in orders.PADS]  # s6.counts
            pools.append(([j for j in found if j["status"] == "approved"], sorted((j for j in found if j["status"] == "declined"), key=lambda j: j["value"])))
        for _ in range(5000):
            need, best = want[h] - have[h], None
            for approved, declined in pools:
                values = [j["value"] for j in declined]
                for x in approved:
                    i = bisect.bisect_left(values, x["value"] + need)
                    for y in declined[max(0, i - 1):i + 1]:
                        gain = y["value"] - x["value"]
                        if abs(need - gain) < abs(need) - Decimal("0.005") and (best is None or abs(need - gain) < abs(need - best[0])):
                            best = (gain, x, y, approved, declined)
            if best is None:
                break
            gain, x, y, approved, declined = best
            x["status"], y["status"] = "declined", "approved"
            approved.remove(x)
            approved.append(y)
            declined.remove(y)
            bisect.insort(declined, x, key=lambda j: j["value"])
            have[h] += gain


def technicians(b, every, fixed):
    """4.2, the technician: per shop and 30-day block every mechanic's sold hours come to pNN.billed_index x
    volume.norm.<site> x his worked days x one factor, the block's hours over those targets (F2 and F4, read over their
    whole time, at their rows as they stand). An order goes to one mechanic on duty the day its work is done, the one
    furthest behind his target who still has room in his shift; diagnostic lead jobs go first to the diagnostician of
    kb.schedule.diagnostics_and_weekends (slot 10 at main, four a day; slot 18 at east, two); s6.p27_pad_share of west's
    pad orders go to slot 27, dealt on the days he works; on every mechanic's west pad jobs the cheap pad (s6.brand) at
    s6.cheap_share."""
    cfg, seed = b.cfg, b.seed
    norm = {s: inputs.value(f"volume.norm.{s}", cfg) / (1 if cfg == "en" else 21.74) for s in SITES}  # ru: the month norm over 21.74 days
    old_hours = collections.Counter()
    for v in fixed:
        for j in v["jobs"]:
            if j["status"] == "approved" and j.get("labor") and j.get("tech"):
                old_hours[v["site"], block(b, v["day"]), orders.slot_of(b, j["tech"])] += float(j["labor"]["hours"])
    work = [p for p in every if p["kind"] != "void"]
    for p in work:
        p["eta"] = b.parts_eta(p) if getattr(b, "parts_eta", None) and p["visit"] else None  # no work before its parts are in
        p["work_day"] = work_day(b, p)
    hours = {id(p): hours_of(b, p) for p in work}
    # kb.schedule.diagnostics_and_weekends counts lead diagnostic jobs a day (spec 4.2), the planted ones included
    diag_jobs = {id(p): int(p["visit"] and p["jobs"][0]["status"] == "approved" and JOBS[p["jobs"][0]["key"]]["category"] == "diagnostics") for p in work}
    old_diag = collections.Counter()
    for v in fixed:
        e = next((e for e in v["record"]["entries"] if e["order_job_id"] is v["jobs"][0]), None)
        if e and JOBS[v["jobs"][0]["key"]]["category"] == "diagnostics" and orders.slot_of(b, e["technician_id"]) == orders.DIAGNOSTICIAN.get(v["site"], (None,))[0]:
            old_diag[v["site"], e["clock_in"].date()] += 1
    factor = inputs.value("erp.time.clocked_over_sold", cfg)
    seq = itertools.count()
    roster = {}

    def crew(site, day):
        if (site, day) not in roster:
            roster[site, day] = dict(orders.mechanics(b, site, day))
        return roster[site, day]
    forced = {}
    pads = [p for p in work if p["site"] == "west" and p["visit"] and any(j["key"] in orders.PADS and j["status"] == "approved" for j in p["jobs"])]
    pad_ids = {id(p) for p in pads}
    his = [p for p in pads if "27" in crew("west", p["work_day"])]
    for p in streams.stream(seed, "pads to 27").sample(his, min(len(his), round(len(pads) * inputs.value("s6.p27_pad_share", cfg) / 100))):
        forced[id(p)] = "27"
    for (site, k), group in by(lambda p: (p["site"], block(b, p["work_day"])), work).items():
        days = sorted({p["work_day"] for p in group})
        worked = collections.Counter(s for d in days for s in crew(site, d))
        target = {s: inputs.value(slot_key(s, "billed_index"), cfg) * norm[site] * n for s, n in worked.items()}
        fixed_ = {s: v for s, v in target.items() if s in ("F2", "F4")}
        supply = sum(hours[id(p)] for p in group if p["visit"]) + sum(v for key, v in old_hours.items() if key[:2] == (site, k))
        scale = (supply - sum(fixed_.values())) / max(sum(target.values()) - sum(fixed_.values()), 1e-9)
        left = {s: v * (1 if s in fixed_ else scale) - old_hours[site, k, s] for s, v in target.items()}
        days_left = collections.Counter(worked)
        rng = streams.stream(seed, "technicians", site, k)
        first_in = orders.DIAGNOSTICIAN.get(site)
        by_day = by(lambda p: p["work_day"], group)
        carry = collections.Counter()  # a mechanic's work that ran past yesterday's shift
        for d in days:
            on = crew(site, d)
            start, end = orders.shift(b, site, d)
            # each mechanic's day as `orders.book` will find it: the planted work already on it, what ran over yesterday
            busy = {s: sorted(b.timeline.get((id(row), d), []) + [(start, start + dt.timedelta(hours=carry[s]))] * (carry[s] > 0)) for s, row in on.items()}
            today = collections.Counter()
            # the diagnostician's daily cap; a lead diagnostic order comes to him first when his day has room for it then
            room = first_in[1] - old_diag[site, d] if first_in and first_in[0] in on else 0

            def slot(s, p):  # where s would do p's work: from the first free minute it fits in once it is ready
                need = dt.timedelta(hours=hours[id(p)] * factor.get(f"slot {s}", factor["everyone"]))
                # after the look and the call, and the parts; a waiting order from the car's check-in, its work packed
                # on the day its wait ends (its diagnostic job needs no part)
                t = max(p["at"] + 20 * orders.MINUTE if p.get("start") else max(p["at"] + dt.timedelta(minutes=60), p["eta"] or start), start)
                for lo, hi in busy[s]:
                    if hi <= t:
                        continue
                    if t + need <= lo:
                        break
                    t = max(t, hi)
                return t, t + need

            def on_time(s, p):  # done before the shift ends
                return slot(s, p)[1] <= end
            lead_diag = {id(p) for p in by_day[d] if p["visit"] and JOBS[p["jobs"][0]["key"]]["category"] == "diagnostics"}
            todays = sorted(by_day[d], key=lambda p: (forced.get(id(p)) not in on, id(p) not in lead_diag, not p.get("start"), p.get("start") or p["at"], p["at"]))
            for p in todays:
                h = hours[id(p)] if p["visit"] else 0
                if not p["visit"]:  # a declined estimate: no labour by a technician; one of them looks the car over
                    s = streams.pick(rng, sorted(on))
                elif forced.get(id(p)) in on:  # slot 27's pads: his even on a full day
                    s = forced[id(p)]
                else:
                    banned = {"27"} if id(p) in pad_ids else set()
                    if first_in and diag_jobs[id(p)] > room:
                        banned.add(first_in[0])
                    choice = [s for s in on if s not in banned] or list(on)
                    if (b.a["T"].date() - d).days <= 7:  # near T a mechanic off tomorrow could not finish it before T's day
                        choice = [s for s in choice if s in crew(site, orders.opening(b, site, end).date())] or choice
                    # nor, on his last day, one who leaves, when it would run past his shift or waits for a later decision
                    choice = [s for s in choice if not (b.people.get(s) or {}).get("left_on") or slot(s, p)[1] <= end and not any(j.get("found") for j in p["jobs"])
                              or any(s in crew(site, d + dt.timedelta(i)) for i in range(1, (b.people[s]["left_on"] - d).days))] or choice
                    fits = [s for s in choice if on_time(s, p)]
                    if id(p) in lead_diag and first_in and first_in[0] in fits:
                        s = first_in[0]
                    elif fits:
                        s = max(fits, key=lambda s: (left.get(s, 0) / max(days_left[s], 1) - today[s], -fits.index(s)))
                    else:  # nobody has room: whoever finishes it first, among those back tomorrow
                        back = [s for s in choice if s in crew(site, orders.opening(b, site, end).date())] or choice
                        s = min(back, key=lambda s: (slot(s, p)[1], back.index(s)))
                    if first_in and s == first_in[0]:
                        room -= diag_jobs[id(p)]
                if h:
                    if p.get("start"):  # the wait ends when the work begins
                        p["start"] = slot(s, p)[0]
                    bisect.insort(busy[s], slot(s, p))
                today[s] += h
                p["seq"] = next(seq)  # the order in which `fill` books the work, as planned here
                for j in p["jobs"]:
                    j["tech"] = on[s]
                p["tech"] = s
            for s in on:
                left[s] = left.get(s, 0) - today[s]
                days_left[s] -= 1
                carry[s] = max(0.0, (max([end] + [hi for _, hi in busy[s]]) - end).total_seconds() / 3600)
    share = inputs.value("s6.cheap_share", cfg)
    old_pads = collections.Counter((v["tech"], j.get("tier") == "cheap") for v in fixed if v["site"] == "west" for j in v["jobs"]
                                   if j["key"] in orders.PADS and j["status"] == "approved")
    for s, group in by(lambda j: j[1], [(j, p["tech"]) for p in pads for j in p["jobs"] if j["key"] in orders.PADS and j["status"] == "approved"]).items():
        n = round((len(group) + old_pads[s, True] + old_pads[s, False]) * share / 100) - old_pads[s, True]
        for (j, _), cheap in zip(group, deal(seed, ("cheap pads", s), len(group), {True: max(0, n), False: max(0, len(group) - n)})):
            if cheap:
                j["tier"] = "cheap"


def pad_cells(b, every, fixed):
    """S06 (s6.counts, full size): the approved pad jobs are the row's cells exactly: at west since the purchase slot
    27's other brands and cheap brand and his colleagues' (s6.p27_pad_share, s6.cheap_share for every mechanic), at the
    home shops the other brands of everyone (the all-shops cell less west's). Visits of the background take a pad job
    as an add-on, or give one up (an add-on first, then a lead, which takes another lead job), with the mechanic the
    cell needs; then each fitter's cheap pads are dealt to the cell. The orders already there count as they are."""
    cfg, seed = b.cfg, b.seed
    cells = inputs.value("s6.counts", cfg)
    rng = streams.stream(seed, "pad cells")
    weights = {k: SHARES[cfg][k]["lead"] + SHARES[cfg][k]["addon"] for k in orders.PADS}

    def pads(p):
        return [j for j in p["jobs"] if j["key"] in orders.PADS and j["status"] == "approved"]
    mine = [p for p in every if p["visit"] and p["kind"] in ("private", "small", "walkin") and (p["site"] != "west" or p["day"] >= b.a["bought"])]
    # the last week's visits carry none: one that cannot close by T is not placed (`fill`), and its pad would leave its cell
    for p in [p for p in mine if (b.a["T"].date() - p["day"]).days <= 7]:
        for j in pads(p):
            if j is p["jobs"][0]:
                j.update(key=customers.weighted(rng, {k: SHARES[cfg][k]["lead"] for k in PRICED if k not in orders.PADS and allowed(b, p, k)
                                                      and all(k != x["key"] for x in p["jobs"])}), tier="standard")
            else:
                p["jobs"].remove(j)
    mine = [p for p in mine if (b.a["T"].date() - p["day"]).days > 7]
    olds = [v for v in fixed if v["visit"] and v["kind"] in ("private", "small", "walkin", "account") and (v["site"] != "west" or v["day"] >= b.a["bought"])]
    groups = (("west 27", lambda p: p["site"] == "west" and p["tech"] == "27", cells["p27_good"] + cells["p27_cheap"]),
              ("west others", lambda p: p["site"] == "west" and p["tech"] != "27", cells["others_good"] + cells["others_cheap"]),
              ("home", lambda p: p["site"] != "west", cells["good_pad_jobs_not_27_all_shops"] - cells["others_good"]))
    for name, member, want in groups:
        have = sum(len(pads(v)) for v in olds if member(v))
        group = [p for p in mine if member(p)]
        rng.shuffle(group)
        n = want - have - sum(len(pads(p)) for p in group)
        for p in group:
            if n == 0:
                break
            if n > 0 and not pads(p) and not (b.people.get(p["tech"]) or {}).get("left_on"):  # a leaving mechanic's last days stay as dealt
                fits = {k: w for k, w in weights.items() if allowed(b, p, k)}
                if fits:
                    p["jobs"].insert(1, {"key": customers.weighted(rng, fits), "status": "approved", "tech": p["jobs"][0].get("tech"),
                                         "tier": "standard", "keep": True})
                    n -= 1
            elif n < 0 and pads(p):
                j = next((j for j in pads(p) if j is not p["jobs"][0] and not j.get("found")), None) or (pads(p)[0] if pads(p)[0] is p["jobs"][0] else None)
                if j is None:
                    continue
                if j is p["jobs"][0]:
                    lead = {k: SHARES[cfg][k]["lead"] for k in PRICED if k not in orders.PADS and allowed(b, p, k) and all(k != x["key"] for x in p["jobs"])}
                    j.update(key=customers.weighted(rng, lead))
                else:
                    p["jobs"].remove(j)
                n += 1
        if name == "home":
            continue
        cheap = cells["p27_cheap" if name == "west 27" else "others_cheap"] - sum(j.get("tier") == "cheap" for v in olds if member(v) for j in pads(v))
        jobs = [j for p in group for j in pads(p)]
        for j, flag in zip(jobs, deal(seed, ("pad cells cheap", name), len(jobs), {True: max(0, cheap), False: max(0, len(jobs) - cheap)})):
            j["tier"] = "cheap" if flag else "standard" if j.get("tier") == "cheap" else j.get("tier")


def comebacks(b, every, fixed):
    """4.6: per mechanic of the first order, exactly round(n x rate) of his orders over his row's window get a comeback
    (pNN.comebacks: the last 12 months, slot 27 since the purchase, F2 his last six months; older orders at the same row,
    F2's at comeback.main, F4's none: spec section 7b), the orders already there and their comebacks counted; pad jobs
    first, the comebacks of each cell of s6.counts (west colleagues' other brands apart from the all-shops pool), no host
    holding a pad job. A comeback takes the place of a background visit at the same shop
    erp.comeback.gap_days after its first order is completed, never after T; that visit's courtesy inspection and raised
    jobs move to another visit of its advisor and month (so the dealt shares stay); the same customer and car, the
    repeated job at list, done by that visit's mechanic, first look by the shop's kb.comeback_first_look person;
    warranty (en every gap of the row is inside the warranty; ru the gap is cut to 30 days from the first order)."""
    cfg, a, seed = b.cfg, b.a, b.seed
    T = a["T"].date()
    gap = inputs.value("erp.comeback.gap_days", cfg)
    year_ago = clock.months_back(T, 12)
    # an order counts for the mechanic with its most approved hours; one with none counts for nobody (as pNN.comebacks reads)
    firsts = [p for p in every if p["kind"] in ("private", "small", "walkin") and p["day"] < T and hours_of(b, p) > 0]
    # (a planted order counts only when it came back: section 7, S5.3, S7 and S8)
    of_first = {id(v["order"]["comeback_of_id"]): v for v in fixed if v["kind"] == "comeback"}
    firsts += [v for v in fixed if v["kind"] in ("private", "small", "walkin", "account") and v["order"]["status"] in ("invoiced", "paid") and v["tech"]
               and (not v["record"].get("planted") or id(v["order"]) in of_first)]
    done_before = {id(v): of_first[id(v["order"])] for v in firsts if v.get("fixed") and id(v["order"]) in of_first}

    def ends(p):
        """When the first order is done at the latest: its completion, or its work day, its sublet days and days to spare."""
        if p.get("fixed"):
            return next((h["changed_at"].date() for h in p["record"]["history"] if h["status"] == "completed"), p["day"])
        extra = sum(inputs.value("kb.sublet_times", cfg)[orders.SUBLET[j["key"]][2 if cfg == "ru" else 1]] + 2
                    for j in p["jobs"] if j["status"] == "approved" and JOBS[j["key"]][cfg]["usually_sublet"])
        eta = getattr(b, "parts_eta", None) and b.parts_eta(p)  # (its special-order parts first: no work before they are in)
        work = max(p["work_day"], eta.date()) if eta else p["work_day"]
        day = work + dt.timedelta(1)  # the mechanic's next day at the shop, three days to spare
        while p["tech"] not in dict(orders.mechanics(b, p["site"], day)) and day < work + dt.timedelta(8):
            day += dt.timedelta(1)
        return day + dt.timedelta(3 + extra + any(j.get("decided") for j in p["jobs"] if j.get("found")))

    def population(p):  # the window of the mechanic's row, read as pNN.comebacks reads it
        s = p["tech"]
        if s == "27":
            return s, True
        if s == "F2":
            return s, p["day"] >= clock.months_back(b.people["F2"]["left_on"], 6)
        return s, p["at"] > dt.datetime.combine(year_ago, a["T"].time())

    def rate(key):
        s, window = key
        if s == "F4":
            return 0
        if s == "F2" and not window:
            return inputs.value("comeback.main", cfg)
        return inputs.value("s6.rate.other_work.p27" if s == "27" else slot_key(s, "comebacks"), cfg)

    def pad_jobs(p):
        return [j for j in p["jobs"] if j["key"] in orders.PADS and j["status"] == "approved"]

    def pad_groups(p):  # (by slot 27, cheap, a colleague's other-brand pad at west: the cell s6.counts deals apart)
        return collections.Counter((p["tech"] == "27", j.get("tier") == "cheap", p["site"] == "west" and p["tech"] != "27" and j.get("tier") != "cheap")
                                   for j in pad_jobs(p))

    def repeatable(p):  # a job the shop's own mechanics redo (not an inspection, not a subcontractor's)
        return [j for j in p["jobs"] if j["status"] == "approved" and j["key"] not in orders.PADS + orders.INSPECTING
                and not JOBS[j["key"]][cfg]["usually_sublet"] and orders.sold_hours(cfg, j["key"], p["vehicle"])]

    # (not a waiting one: the waits' mean is fitted on them; none on the shop's last two open days before T's day, whose
    # work may not close by T: fill turns such an order into an appointment, spec 4.5)
    def late(p):
        nxt = orders.opening(b, p["site"], orders.hours(b, p["site"], p["day"])[1])
        return p["day"] < T <= orders.opening(b, p["site"], nxt + dt.timedelta(days=1)).date()
    hosts_by = by(lambda p: (p["site"], p["day"]), [p for p in every if p["kind"] == "private" and p["visit"] and not p.get("start") and not late(p)])
    rng = streams.stream(seed, "comebacks")
    chosen, hosts = {}, {}  # id(first): (first, job); id(first): host plan

    def take_host(p, pad=False):
        start = ends(p) + dt.timedelta(gap["min"])
        last = min(T, p["day"] + dt.timedelta(30)) if cfg == "ru" else T
        days = half_uniform(rng, gap)
        target = min(ends(p) + dt.timedelta(days), last)
        used = {id(h) for h in hosts.values()} | set(chosen)
        tries = [target + dt.timedelta(i) for i in range((last - target).days + 1)] + [target - dt.timedelta(i) for i in range(1, (target - start).days + 1)]
        for d in tries:
            if pad and (T - d).days <= 7:  # a pad comeback open at T cannot be dropped (`fill`; s6.counts): it has a week to close
                continue
            free = [h for h in hosts_by.get((p["site"], d), []) if id(h) not in used and h["at"] > p["at"] and not pad_jobs(h)
                    and not (cfg == "en" and p["site"] == "main" and d.weekday() == 5)]  # s6.counts; no diagnostic job on main's Saturday
            if free:
                return streams.pick(rng, free)
        return None

    def steady(p):
        """The first order's mechanic does its work: he stays two weeks more, works at the shop its day and the next, and
        three of the six days after it (not a leave ahead: work he holds would wait for him past its comeback)."""
        left = (b.people.get(p["tech"]) or {}).get("left_on")
        if p.get("fixed") or left and left <= p["day"] + dt.timedelta(14):
            return bool(p.get("fixed"))
        day = p["work_day"]
        week = [day + dt.timedelta(k) for k in range(1, 7)]
        return all(p["tech"] in dict(orders.mechanics(b, p["site"], d)) for d in (day, orders.opening(b, p["site"], orders.hours(b, p["site"], day)[1]).date())) \
            and sum(p["tech"] in dict(orders.mechanics(b, p["site"], d)) for d in week) >= 3
    # a first order needs room for its comeback before T (ru inside its 30 days) and a steady mechanic
    ready = [p for p in firsts if p["kind"] != "walkin" and not (p.get("fixed") and p["record"].get("planted")) and ends(p) + dt.timedelta(gap["min"]) <= T and steady(p)
             and not (cfg == "ru" and ends(p) + dt.timedelta(gap["min"]) > p["day"] + dt.timedelta(30))]
    rng.shuffle(ready)
    florist = {id(p) for p in ready if p["customer"]["name"].startswith(stories.FLORIST[cfg])}  # its van's comeback is board.second_look_open's alone
    for _ in range(10):  # the hosts leave their mechanics' populations: deal again until the counts hold
        changed = False
        out = {id(h) for h in hosts.values()}
        members = [p for p in firsts if id(p) not in out]
        got = sum((pad_groups(chosen[k][0]) for k in chosen if chosen[k][1]["key"] in orders.PADS), collections.Counter())
        got += sum((pad_groups(v) for v in members if id(v) in done_before and any(j["key"] in orders.PADS for j in done_before[id(v)]["jobs"])), collections.Counter())
        cells = inputs.value("s6.counts", cfg)  # the comebacks of each cell as the row deals them (full size)
        target = {(True, False, False): cells["comebacks_p27_good"], (True, True, False): cells["comebacks_p27_cheap"],
                  (False, True, False): cells["comebacks_others_cheap"], (False, False, True): cells["comebacks_others_good_at_west"],
                  (False, False, False): cells["comebacks_good_not_27_all_shops"] - cells["comebacks_others_good_at_west"]}
        for p in ready:
            groups = pad_groups(p)
            if id(p) in chosen or id(p) in out or id(p) in done_before or id(p) in florist or not groups or not p.get("visit", True):
                continue
            if all(got[g] + n <= target[g] for g, n in groups.items()):
                host = take_host(p, pad=True)
                if host:
                    got.update(groups)
                    chosen[id(p)], hosts[id(p)] = (p, pad_jobs(p)[0]), host
                    out.add(id(host))
                    changed = True
        for key, group in by(population, members).items():
            pool = [p for p in group if not pad_jobs(p)] if key[0] == "27" else group
            have = [p for p in pool if id(p) in chosen or id(p) in done_before]
            want = round(len(pool) * rate(key) / 100)
            if len(have) > want:
                for p in [p for p in have if id(p) in chosen and chosen[id(p)][1]["key"] not in orders.PADS][:len(have) - want]:
                    del chosen[id(p)], hosts[id(p)]
                    changed = True
            elif len(have) < want:
                for p in ready:
                    if len(have) >= want:
                        break
                    if population(p) != key or id(p) in chosen or id(p) in out or id(p) in done_before or id(p) in florist or (key[0] == "27" and pad_jobs(p)) or not repeatable(p):
                        continue
                    host = take_host(p)
                    if host:
                        chosen[id(p)], hosts[id(p)] = (p, streams.pick(rng, repeatable(p))), host
                        out.add(id(host))
                        have.append(p)
                        changed = True
        if not changed:
            break
    # the hosts become the comebacks; what they carried moves to another visit of the same advisor and month
    receivers = by(lambda p: (p["site"], p["day"].year, p["day"].month), [p for p in every if p["visit"] and p["kind"] in ("private", "small", "walkin")])
    taken = {id(h) for h in hosts.values()} | set(chosen)
    for key, (p, job) in chosen.items():
        h = hosts[key]
        found = [j for j in h["jobs"] if j.get("found")]
        courtesy = [j for j in h["jobs"] if j["key"] == "courtesy_inspection"]
        for moving, inspected in ((found, True), (courtesy, False)):
            if not moving:
                continue
            pool = [r for r in receivers[month_of(h)] if id(r) not in taken and not any(j.get("found") for j in r["jobs"])
                    and not (b.people.get(r.get("tech")) or {}).get("left_on")  # a leaving mechanic's orders keep what he was dealt
                    and any(j["key"] in orders.INSPECTING for j in r["jobs"]) == inspected and not any(j["key"] == "courtesy_inspection" for j in r["jobs"][1:]) * (not inspected)]
            pool.sort(key=lambda r: (r["advisor"] != h["advisor"], window(b, r) != window(b, h), r.get("tech") != h.get("tech"), r["at"]))
            for r in pool[:1]:
                carried = {j["key"] for j in r["jobs"]}
                # (a decision the host's day fixed is the receiver's own again: decided when its check-in calls for it)
                r["jobs"] += [dict({k: v for k, v in j.items() if k != "decided"}, tech=r["jobs"][0].get("tech")) for j in moving if j["key"] not in carried and allowed(b, r, j["key"])]
                taken.add(id(r))
        tech = h["jobs"][0].get("tech")
        h.update(kind="comeback", first=p, customer=p["customer"], vehicle=p["vehicle"],
                 jobs=[{"key": job["key"], "status": "approved", "tech": tech, "tier": job.get("tier")}])
        if not p.get("fixed"):
            for j in p["jobs"]:
                j["keep"] = "held"  # the first order's work stays with its mechanic however long he is full: the comeback is his


def slot_start(b, site, at, lead):
    """kb.booking.slots: the appointment a check-in at `at` kept, or None. en: drop-offs at 07:30, 08:00 and 08:30;
    waiters on the half hour from 09:00 to 14:00, jobs of an hour or less. ru: on the half hour from 09:00 to 18:00.
    Nothing over three hours after 13:00 (en) or 15:00 (ru); east on Monday keeps the account's slots, others from 09:30
    (en) or 10:30 (ru)."""
    cfg, slots = b.cfg, inputs.value("kb.booking.slots", b.cfg)
    clock_ = lambda text: dt.time(*map(int, text.split(":")))  # noqa: E731
    t = at.replace(minute=at.minute // 30 * 30, second=0)
    if cfg == "en":
        if at.time() < clock_("9:00"):
            t = max((dt.datetime.combine(at.date(), clock_(x)) for x in slots["drop_offs"] if clock_(x) <= at.time()), default=None)
        elif lead > 1 or t.time() > clock_(slots["waiters"].split(" to ")[1].split(",")[0]):
            return None
    else:
        lo, hi = (clock_(x) for x in slots["appointments"].split(" to "))
        if not lo <= t.time() <= hi:
            return None
    if t is None or lead > 3 and t.time() > clock_(re.search(r"after (\d+:\d+)", slots["long_jobs"])[1]):
        return None
    if site == "east" and at.weekday() == 0 and t.time() < clock_(re.search(r"others from (\d+:\d+)", slots["east_on_Monday"])[1]):
        return None
    return t


def bookings(b, every, known, counts):
    """Spec section 3, appointment: erp.appointment.share_of_orders of the visits (comebacks and the walk-in record left
    out; the orders already there counted) arrived from a booking, dealt per shop and month among those a booking slot
    fits; the no-shows and cancellations of erp.appointment.outcome beside them; and the bookings made by T for the days
    after it."""
    cfg, a, seed = b.cfg, b.a, b.seed
    share = inputs.value("erp.appointment.share_of_orders", cfg)
    outcome = inputs.value("erp.appointment.outcome", cfg)
    sources = inputs.value("erp.appointment.source", cfg)
    lead = inputs.value("erp.appointment.lead_days", cfg)
    kept = 1 - sum(outcome.values()) / 100
    created = {site: [c["created_at"] for c, _ in known[site]] for site in SITES}
    old = collections.Counter()
    for o in b.orders.values():
        if o["appointment"]:
            old[(next(s for s, r in b.shops.items() if r is o["order"]["location_id"]), o["order"]["opened_at"].year, o["order"]["opened_at"].month)] += 1

    def booked(site, starts, rng):
        day = starts.date() - dt.timedelta(half_uniform(rng, lead))
        while orders.hours(b, site, day) is None:
            day -= clock.DAY
        open_, close = orders.hours(b, site, day)
        at = min(open_ + dt.timedelta(minutes=rng.randrange(int((close - open_).total_seconds() // 60))), starts - orders.MINUTE)
        return at, streams.pick(rng, orders.advisors(b, site, day) or orders.advisors(b, site, starts.date()))

    def minutes(hours):
        return max(30, -(-int(hours * 60) // 30) * 30)

    def booking_row(site, day, rng, status, when=None):
        count = bisect.bisect_left(created[site], when or dt.datetime.combine(day, dt.time()))
        if not count:
            return
        c, cars = known[site][rng.randrange(count)]
        car = streams.pick(rng, cars)
        key = customers.weighted(rng, {k: SHARES[cfg][k]["lead"] for k in PRICED if JOBS[k][cfg]["hours"] and (JOBS[k][cfg]["hours_by_class"] or {}).get(car["vehicle_class"], 1)})
        hours = float(orders.sold_hours(cfg, key, car))
        for _ in range(20):
            starts = slot_start(b, site, moment(b, rng, site, day), hours)
            if starts and not (day == a["stocktake"] and starts.time() > (dt.time(10, 30) if cfg == "en" else dt.time(10))):
                break
        else:
            return
        at, by_ = booked(site, starts, rng)
        if when and at > when:
            return
        b.add("appointment", location_id=b.shops[site], customer_id=c, vehicle_id=car, starts_at=starts, duration_min=minutes(hours),
              source=customers.weighted(rng, sources), status=status, reason=JOBS[key][cfg]["name"], booked_at=at, booked_by_id=b.people[by_])

    for key, group in by(month_of, [p for p in every if p["kind"] in ("private", "small")]).items():
        site = key[0]
        rng = streams.stream(seed, "bookings", *key)
        lead_hours = {id(p): float(orders.sold_hours(cfg, p["jobs"][0]["key"], p["vehicle"])) for p in group}
        fits = [p for p in group if slot_start(b, site, p["at"], lead_hours[id(p)])]
        chosen = rng.sample(fits, max(0, min(len(fits), round(len(group) * share / 100) - old[key])))
        for p, source in zip(sorted(chosen, key=lambda p: p["at"]), deal(seed, ("source", *key), len(chosen), sources)):
            starts = slot_start(b, site, p["at"], lead_hours[id(p)])
            at, by_ = booked(site, starts, streams.stream(seed, "booked", site, p["at"]))
            p["booking"] = {"source": source, "booked_at": at, "booked_by": by_, "starts_at": starts, "duration": minutes(lead_hours[id(p)])}
        total = round(len(chosen) / kept)
        days = sorted({p["day"] for p in group if p["day"] < a["T"].date()})
        for status in ("no_show", "cancelled"):
            for _ in range(round(total * outcome[status] / 100) if days else 0):
                booking_row(site, streams.pick(rng, days), rng, status)
    # the days after T: the bookings already made (confirmed within two days of T); none on the stocktake day after
    # its last slot (spec section 3, appointment)
    for (site, day), n in sorted(counts.items(), key=lambda x: (SITES.index(x[0][0]), x[0][1])):
        if a["T"].date() < day <= a["T"].date() + dt.timedelta(lead["max"]):
            rng = streams.day_stream(seed, site, day, "future bookings")
            for _ in range(round(n * share / 100 / kept)):
                booking_row(site, day, rng, None, when=orders.until(b, site))
    for row in b.tables["appointment"]:
        if row["status"] is None:
            row["status"] = "confirmed" if row["starts_at"] - a["T"] <= dt.timedelta(2) else "booked"


def money(b, every, fixed):
    """4.7: the counter payment's method by pay.mix, dealt per shop and month over the counter orders (F1's apart: his
    cash is a story's); background discounts on pay.background_discount_share of cash orders, 10 % to under 15 % of the
    bill before the discount (price.discount_base) on the labour, no approver before the rule, slot 4's after it at main
    and east, none at west from the firing on (its four are planted; s2.west.discounts_after counts from that day);
    coupons of 5 % on non-cash orders bring the month's discounts to mixrow.discounts (1 % of sales); reasons from
    texts.json."""
    cfg, a, seed = b.cfg, b.a, b.seed
    texts = orders.TEXTS[cfg]
    mix = inputs.value("pay.mix", cfg)
    cash_share = inputs.value("pay.cash_share", cfg)
    for p in every:
        for j in p["jobs"]:
            orders.price(b, p["day"], p["customer"], p["vehicle"], j)
    olds = by(month_of, fixed)

    def bill(jobs):
        labor, parts, sublet, fees, _ = orders.bill(b, jobs)
        return labor, labor + parts + sublet + fees

    carry = collections.Counter()
    for key, group in by(month_of, [p for p in every if p["kind"] in ("private", "small", "walkin")]).items():
        site = key[0]
        old = olds.get(key, [])
        accounts = sum(1 for v in old if v["kind"] == "account")
        for f1 in (False, True):
            counter = [p for p in group if (p["advisor"] == "F1") == f1]
            mine = [v for v in old if v["pay"] and (v["advisor"] == "F1") == f1]
            had = collections.Counter(v["pay"] for v in mine)
            n = len(counter) + len(mine)
            rng = streams.stream(seed, "pay", *key, f1)
            smalls = [p for p in counter if p["kind"] == "small"]
            rest = [p for p in counter if p["kind"] != "small"]
            rng.shuffle(rest)
            # S02: in his 26 weeks F1's cash orders are the story's (s2.f1.cash_orders); his month's cash goes to his days
            # before them, none to those inside
            inside = {id(p) for p in rest if f1 and a["s2_start"] <= p["day"] < a["fired"]}
            rest.sort(key=lambda p: id(p) in inside)
            if cfg == "en":
                checks = max(0, min(round((n + accounts) * mix["check"] / 100) - had["check"], len(smalls)))
                for i, p in enumerate(smalls):
                    p["pay"] = "check" if i < checks else "card"
            else:
                transfers = max(0, min(round((n + accounts) * mix["invoice (bank transfer)"] / 100) - accounts - had["bank_transfer"], len(smalls)))
                for i, p in enumerate(smalls):
                    p["pay"] = "bank_transfer" if i < transfers else "fast_payment"
            cash = max(0, round((n + accounts * (not f1)) * cash_share / 100) - had["cash"])  # over every paid order, as pay.mix reads it
            fast = max(0, round((n + accounts) * mix["fast payment (СБП)"] / 100) - had["fast_payment"] - sum(p["pay"] == "fast_payment" for p in smalls)) if cfg == "ru" else 0
            for i, p in enumerate(rest):
                p["pay"] = "cash" if i < cash and id(p) not in inside else "fast_payment" if i < cash + fast and fast else "card"
        rng = streams.stream(seed, "discounts", *key)
        sales = sum(bill(p["jobs"])[1] for p in group) + sum(v["order"]["labor_total"] + v["order"]["parts_total"] + v["order"]["sublet_total"]
                                                             + v["order"]["fees_total"] for v in old if v["visit"] and v["order"]["order_type"] == "customer_pay")
        given = sum(v["order"]["discount_total"] for v in old if v["order"]["order_type"] == "customer_pay")
        cash_orders = [p for p in group if p["pay"] == "cash" and p["advisor"] != "F1"]
        old_cash = [v for v in old if v["pay"] == "cash" and v["advisor"] != "F1"]
        had = sum(1 for v in old_cash if v["order"]["discount_total"] >= Decimal("0.1") * (v["order"]["total"] - v["order"]["tax_total"] + v["order"]["discount_total"]))
        # dealt per shop and month, each month's remainder carried to the next, so that a shop's months keep the share
        exact = (len(cash_orders) + len(old_cash)) * inputs.value("pay.background_discount_share", cfg) / 100 + carry[site]
        carry[site] = exact - round(exact)
        n = round(exact) - had
        able = [p for p in cash_orders if not (site == "west" and p["day"] >= a["fired"]) and bill(p["jobs"])[0] >= Decimal("0.15") * bill(p["jobs"])[1] > 0]  # a free order has nothing to discount
        for p in rng.sample(able, max(0, min(n, len(able)))):
            share = 0.10 + 0.05 * rng.random()
            p["discount"] = (share, streams.pick(rng, texts["background_discount_reasons"]), b.people["4"] if p["day"] >= a["rule_on"] and site != "west" else None)
            given += Decimal(str(share)) * bill(p["jobs"])[1]
        target = Decimal(str(MIX[cfg]["realisation"]["discounts_and_coupons"])) * sales  # mixrow.discounts: 1 % of sales
        others = [p for p in group if p["pay"] != "cash" and p["advisor"] != "F1" and not p.get("discount")]
        rng.shuffle(others)
        for p in others:
            if given >= target:
                break
            labor, gross = bill(p["jobs"])
            if labor >= Decimal("0.05") * gross > 0:
                p["discount"] = (0.05, streams.pick(rng, texts["coupon_reasons"]), None)
                given += Decimal("0.05") * gross

    # S02: of west's cash orders in F1's 26 weeks, s2.west.discount_share_before carry a discount of 10 % or more, his
    # planted ones among them. The row reads the shop's visits there as six average months; the season makes them
    # fewer, so the others' background discounts there are dealt to the row's share, not to the month's rate
    def mine(p):
        return p["site"] == "west" and a["s2_start"] <= p["day"] < a["fired"] and p.get("pay") == "cash"
    cash = [p for p in every if mine(p) and p["kind"] in ("private", "small", "walkin")]
    old = [v for v in fixed if mine(v)]
    big = sum(v["order"]["discount_total"] >= Decimal("0.1") * (v["order"]["labor_total"] + v["order"]["parts_total"] + v["order"]["sublet_total"]
                                                                + v["order"]["fees_total"]) > 0 for v in old)
    want = round(inputs.value("s2.west.discount_share_before", cfg) * (len(cash) + len(old)) / 100) - big
    have = [p for p in cash if p.get("discount") and p["discount"][0] >= 0.10]
    able = [p for p in cash if p["advisor"] != "F1" and not p.get("discount") and bill(p["jobs"])[0] >= Decimal("0.15") * bill(p["jobs"])[1] > 0]
    rng = streams.stream(seed, "discounts", "west", "S02")
    for p in rng.sample(have, max(0, len(have) - want)):
        del p["discount"]
    for p in rng.sample(able, max(0, min(len(able), want - len(have)))):
        p["discount"] = (0.10 + 0.05 * rng.random(), streams.pick(rng, texts["background_discount_reasons"]), None)


def rebilled(b, every, fixed):
    """4.5: slot 7's re-issued bills (p07.rebilled; S8's is planted with its story, the others are background): paid
    orders of his with a part line and no discount, re-opened after the bill and invoiced again the same day for a wrong
    part price, the line now at the catalogue's price; history invoiced, completed, invoiced (`orders.status`)."""
    done = sum(1 for v in fixed if v["advisor"] == "7" and sum(h["status"] == "invoiced" for h in v["record"]["history"]) > 1)

    def spare(p):
        history = b.orders[id(p["order"])]["history"]
        return (history[-1]["status"] == "paid" and history[-1]["changed_at"] - history[-2]["changed_at"] >= dt.timedelta(minutes=20)
                and history[-1]["changed_at"].date() == history[-2]["changed_at"].date())  # the same day: no status in the night between
    mine = [p for p in every if p["advisor"] == "7" and p["kind"] != "comeback" and not p.get("discount") and spare(p)
            and any(j["parts"] for j in p["jobs"] if j["status"] == "approved")]
    rng = streams.stream(b.seed, "rebilled")
    for p in rng.sample(mine, max(0, min(len(mine), inputs.value("p07.rebilled", b.cfg) - 1 - done))):
        history = b.orders[id(p["order"])]["history"]
        invoiced, paid = history[-2]["changed_at"], history[-1]["changed_at"]
        reopened = (invoiced + (paid - invoiced) * rng.uniform(0.2, 0.5)).replace(second=0, microsecond=0)
        orders.status(b, p["order"], "completed", reopened)
        orders.status(b, p["order"], "invoiced", (reopened + (paid - reopened) * rng.uniform(0.2, 0.8)).replace(second=0, microsecond=0))


def till(b):
    """4.9: one close per shop and open day that has closed by T: the day's cash payments less cash refunds; counted
    exact on pay.till_exact_days of days (dealt per shop), else off by 0.01 to kb.till.report_over (texts.json till_note
    beyond it); closed by the advisors on duty in turn; at west from the rule day a second count by slot 22, or the other
    advisor on duty, or on a day with neither slot 25 or, when he is off, the mechanic on duty with the lowest slot."""
    cfg, a, seed = b.cfg, b.a, b.seed
    cash = collections.Counter()
    for o in b.orders.values():
        site = next(s for s, r in b.shops.items() if r is o["order"]["location_id"])
        for pay in o["payments"]:
            if pay["method"] == "cash":
                cash[site, pay["received_at"].date()] += pay["amount"] * (-1 if pay["kind"] == "refund" else 1)
    limit = inputs.value("kb.till.report_over", cfg)
    exact = inputs.value("pay.till_exact_days", cfg)
    for site in SITES:
        day, closes = (a["bought"] if site == "west" else a["history_start"]), []
        while day <= a["T"].date():
            span = orders.hours(b, site, day)
            if span and span[1] <= orders.until(b, site):
                closes.append(day)
            day += clock.DAY
        rng = streams.stream(seed, "till", site)
        turns = collections.Counter()
        # (dealt apart over the last 365 days, the window pay.till_exact_days reads, and the days before)
        recent = [d for d in closes if d > a["T"].date() - dt.timedelta(365)]
        rights = deal(seed, ("till", site), len(closes) - len(recent), {True: exact, False: 100 - exact}) + deal(seed, ("till", site, "recent"), len(recent), {True: exact, False: 100 - exact})
        for day, right in zip(closes, rights):
            on = orders.advisors(b, site, day)
            closer = min(on, key=lambda s: (turns[s], rng.random()))
            turns[closer] += 1
            second = None
            if site == "west" and day >= a["rule_on"]:
                others = [s for s in on if s != closer]
                crew = sorted(orders.mechanics(b, site, day), key=lambda x: int(x[0]) if x[0].isdigit() else 99)
                staff = "22" if day.weekday() < 5 else others[0] if others else next((s for s, _ in crew if s == "25"), crew[0][0] if crew else None)
                second = b.people.get(staff)
            expected = cash[site, day] or orders.ZERO
            off = orders.ZERO if right else (Decimal(rng.randint(1, limit * 100)) / 100) * rng.choice((-1, 1))
            b.add("cash_drawer_close", location_id=b.shops[site], business_date=day, closed_by_id=b.people[closer], second_counter_id=second,
                  float_amount=Decimal(str(inputs.value("kb.till.floats", cfg)[site])), expected_cash=expected, counted_cash=expected + off,
                  difference=off, note=orders.TEXTS[cfg]["till_note"] if abs(off) > limit else None)
