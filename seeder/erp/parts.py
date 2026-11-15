"""Generator-spec section 4.10 and story S06: `place` writes the cars waiting for parts at T (s6.waiting_at_t; the
nine-day car of nf.conv.06 with its two purchase orders) before the background fills the days around them; `fill`
buys every approved catalogue part line of every order in `b.orders`, whoever placed it: from the shelf (issues,
weekly stock orders, the opening stock, transfers) or on a purchase order per vendor and decision, received at each
vendor's parts.on_time row; no work starts before its parts are in, unless the order is one dealt to wait
(parts.wait_over_a_day; the special orders of 2 working days or more and their deposits among them); then returns,
stocktake adjustments and stock_level. `reminders` writes service_reminder after `orders.finish` reads the odometers.

Choices no source fixes: V3's same-day delivery, which has a cut-off and no run, comes three hours after the cut; a
late delivery comes 1 to 3 working days after its promise; a stock order goes out on the first open day of the week for
the parts the week before gave out and brings each back up to its par, in whole units (`shelves`; spec 7b); the
extension of the stocked list looks only at the 25 part slots the catalogue's shares run most (a waiting car's part is
never one of them)."""
import bisect
import collections
import datetime as dt
import math
from decimal import Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, orders, plan, reference

MINUTE, HOUR = dt.timedelta(minutes=1), dt.timedelta(hours=1)
VENDORS = {cfg: inputs.load("vendors.json")[cfg] for cfg in ("en", "ru")}
REFRIGERANT = ("ac_recharge", "ac_recharge_1234yf")  # erp.stock.stocked_jobs: "refrigerant jobs at main only"
NINE_DAY_PART = {"en": "remanufactured angle gear", "ru": "насос ЭГУР"}  # spec section 5, S06: the S6 part, a typed line
REACH = 25  # the part slots the stocked list may grow by (module docstring)


def clock_of(text):
    return dt.time(*map(int, text.split(":")))


def site_of(b, row):
    return next(s for s, r in b.shops.items() if r is row)


def vendor_of(b, site, brand):
    """The vendor that carries the brand among those serving the shop (vendors.json brands, serves, house_brand);
    else west's from V2, the home shops' from V1 (spec 4.10)."""
    for v in VENDORS[b.cfg]:
        if site in v["serves"] and v.get("delivered_on_the_promised_day"):
            names = [n.split(" (")[0] for n in v["brands"]] + ([v["house_brand"]["name"]] if "house_brand" in v else [])
            if any(brand.casefold() == n.casefold() or brand.casefold().startswith(n.casefold() + " ") for n in names):
                return v["id"]
    return "V2" if site == "west" else "V1"


def open_on(b, site, day):
    """A day a vendor delivers to the shop: the shop is open (ru: no deliveries on Sunday, kb.supplier_times)."""
    return orders.hours(b, site, day) is not None and not (b.cfg == "ru" and day.weekday() == 6)


def working(b, site, day, n):
    for _ in range(n):
        day += clock.DAY
        while not open_on(b, site, day):
            day += clock.DAY
    return day


def promise(b, vendor, site, t):
    """kb.supplier_times and spec 7b: the vendor's next run whose cut-off the order at t makes (V2's runs at west are
    their own cut-offs), else the opening of its next delivery day."""
    cfg, times = b.cfg, inputs.value("kb.supplier_times", b.cfg)
    day = t.date()
    while not open_on(b, site, day):
        day += clock.DAY
        t = dt.datetime.combine(day, dt.time())

    close = orders.hours(b, site, day)[1]

    def at(text):
        return dt.datetime.combine(day, clock_of(text))

    def tomorrow():
        return promise(b, vendor, site, dt.datetime.combine(working(b, site, day, 1), dt.time()))

    def kept(run):  # a run the shop is open for: delivered within the hour after it (`arrival`), before closing
        return run if run + HOUR <= close else None
    if vendor == "V1":  # ru one run on Saturday
        runs = list(zip(times["V1"]["order_by"], times["V1"]["runs"]))[:1 if cfg == "ru" and day.weekday() == 5 else None]
        return next((at(run) for cut, run in runs if t <= at(cut) and kept(at(run))), None) or tomorrow()
    if vendor == "V2":
        return next((at(run) for run in times["V2_at_west"] if t <= at(run) and kept(at(run))), None) or tomorrow()
    if vendor == "V4" and cfg == "en":
        return at(times["V4"]["run"]) if t <= at(times["V4"]["order_by"]) and kept(at(times["V4"]["run"])) else tomorrow()
    cut = at({("en", "V3"): "10:00", ("ru", "V3"): "11:00", ("ru", "V4"): "12:00", ("en", "V5"): "16:00", ("ru", "V5"): "17:00"}[cfg, vendor])
    if vendor == "V3" and site != "west" and t <= cut and kept(cut + 3 * HOUR):  # V3: the same day at the home shops, west (Kazan) the next morning
        return cut + 3 * HOUR
    arrive = working(b, site, day, 1 + (t > cut))
    while vendor == "V5" and site == "west" and arrive.weekday() not in (1, 4):  # west on Tuesday and Friday only
        arrive = working(b, site, arrive, 1)
    return orders.hours(b, site, arrive)[0]


def stocked_jobs(cfg):
    return [k for k in inputs.value("erp.stock.stocked_jobs", cfg) if k in orders.JOBS]


def ranking(cfg):
    """The part slots no stocked job holds, by how often the catalogue's shares put them on an order, the most first;
    the refrigerant jobs' and the S6 pads' (only V2 sells them) left out."""
    base = {slot["name"] for k in stocked_jobs(cfg) for slot in orders.JOBS[k][cfg]["parts"]}
    runs = collections.Counter()
    for k, x in orders.JOBS.items():
        for slot in x[cfg]["parts"]:
            if slot["name"] not in base and k not in REFRIGERANT and not any("story" in o for o in slot["options"]):
                runs[slot["name"]] += x[cfg]["share_of_orders"]["total"]
    return [name for name, _ in sorted(runs.items(), key=lambda x: (-x[1], x[0]))]


def stocked(b, extra=()):
    """The parts on the shelf, by shop: erp.stock.stocked_jobs' and the slots of `extra` at every shop, the refrigerant
    jobs' at main only (kb.stock.refrigerant), for every vehicle class."""
    out = {}
    for s in reference.SITES:
        slots = {(o["brand"], slot["name"]) for k in stocked_jobs(b.cfg) + list(REFRIGERANT * (s == "main")) for slot in orders.JOBS[k][b.cfg]["parts"]
                 for o in slot["options"]}
        out[s] = {id(part) for (brand, _, _), part in b.parts.items() if (brand, part["description"]) in slots or part["description"] in extra}
    return out


def arrival(b, promised, ordered):
    """Spec 7b: a delivery comes with its run, within the hour after the run's hour (a next-day one within an hour of
    opening)."""
    return promised + streams.stream(b.seed, "receipt", ordered, promised).randrange(60) * MINUTE


def install(b):
    """From here on (`orders.settle` asks `b.parts_in`) no order's work starts before its special-order parts are in:
    each part off the stocked list is ordered at its job's decision and comes with the vendor's next run, as `fill`
    then writes it. The orders planted before (the stories') keep a card's times, and so does an order whose part would
    come once its mechanic has left: `fill` has their parts in by then."""
    shelf = stocked(b)
    for record in b.orders.values():
        record["early"] = True

    def parts_in(record, job=None):
        """When the order's special-order parts are in, or `job`'s alone (a job starts after its own parts)."""
        if record.get("waiting") or record["waits"] and not job:  # a car waiting at T begins before its part by design; one `fill`
            return None                                                # stops for a late part has its jobs' other parts in on time
        site, opened = record["site"], record["order"]["opened_at"]
        times = []
        for j in [job] if job else record["jobs"]:
            if j["status"] == "approved":
                decided = max(j.get("decided") or opened, opened)
                times += [arrival(b, promise(b, vendor_of(b, site, p["brand"]), site, decided), decided) for p in j.get("parts") or ()
                          if p["part_id"] is not None and id(p["part_id"]) not in shelf[site]]
        last = max(times, default=None)
        gone = [j["tech"]["left_on"] for j in record["jobs"] if j["status"] == "approved" and j.get("tech") and j["tech"]["left_on"]]
        if last and gone and last.date() >= min(gone):  # its part would come when its mechanic has left (his rows read his days)
            record["leaving"] = True
            return None
        return last
    b.parts_in = parts_in

    def parts_eta(p):
        """For a plan of the background, before its jobs are priced: when the parts of its approved jobs that are off
        the shelf could be in, ordered at check-in (the slot's option of the job's tier, the vendors' next runs)."""
        times = []
        for j in p["jobs"]:
            if j["status"] == "approved":
                for slot in orders.JOBS[j["key"]][b.cfg]["parts"]:
                    o = next((o for o in slot["options"] if o["tier"] == j.get("tier")), slot["options"][0])
                    part = b.parts.get((o["brand"], o["part_number"] or slot["name"], "car"))
                    if part is not None and id(part) not in shelf[p["site"]]:
                        times.append(promise(b, vendor_of(b, p["site"], o["brand"]), p["site"], p["at"]) + 30 * MINUTE)
        return max(times, default=None)
    b.parts_eta = parts_eta


def place(b):
    """s6.waiting_at_t: five cars at west in waiting_parts since the clock's s6_since days (9, 6, 4, 2 and 1 calendar
    days before T, each moved back to a full open day), two at main, one at east: each opened the open day before, its
    work begun and stopped for a part that has not come, a part no stocked list can hold (`ranking`). The nine-day car
    is S06's named customer with s6.nine_day_order's job and the S6 part typed, promised for call 15's day + 2
    (nf.conv.06)."""
    cfg, a = b.cfg, b.a
    T = a["T"].date()
    cold = {slot["name"] for k in stocked_jobs(cfg) for slot in orders.JOBS[k][cfg]["parts"]} | set(ranking(cfg)[:REACH])
    for n, (site, since_day) in enumerate([(s, d) for s in ("west", "main", "east") for d in a["s6_since"][s]]):
        rng = streams.stream(b.seed, "waiting car", n)
        opened_day = since_day - clock.DAY
        while not clock.full_open(cfg, opened_day) or orders.hours(b, site, opened_day) is None:
            opened_day -= clock.DAY
        start = orders.hours(b, site, since_day)[0] + HOUR
        opened = orders.hours(b, site, opened_day)[0] + (30 + rng.randrange(90)) * MINUTE
        advisor = streams.pick(rng, orders.advisors(b, site, opened_day))
        tech = streams.pick(rng, [p for _, p in orders.mechanics(b, site, since_day) if p["left_on"] is None])  # on duty the day the work begins, still here when the part comes
        if n == 0:
            customer, (car,) = b.named["S6"]
            x = inputs.value("s6.nine_day_order", cfg)
            job = {"key": x["job"], "status": "approved", "tech": tech, "keep": True, "hours": Decimal(str(x["hours"])), "tier": "standard"}
            orders.price(b, opened_day, customer, car, job)
            job["parts"] = [{"part_id": None, "description": NINE_DAY_PART[cfg], "brand": None, "quantity": Decimal(1),
                             "unit_cost": Decimal(str(x["typed_part_cost"])), "unit_price": Decimal(str(x["price"])), "vendor_id": b.vendors["V2"]}]
            job["value"] = job["labor"]["amount"] + job["parts"][0]["unit_price"]
        else:
            customer, garage = streams.pick(rng, b.pools[site])
            car = streams.pick(rng, garage)
            p = {"vehicle": car, "site": site, "day": opened_day}
            key = customers.weighted(rng, {k: plan.SHARES[cfg][k]["lead"] for k in plan.PRICED if orders.JOBS[k][cfg]["parts"]
                                           and not any(slot["name"] in cold for slot in orders.JOBS[k][cfg]["parts"])
                                           and orders.sold_hours(cfg, k, car) >= 1 and not orders.JOBS[k][cfg]["usually_sublet"] and plan.allowed(b, p, k)})
            job = {"key": key, "status": "approved", "tech": tech, "keep": True, "tier": "standard"}
        since = start + 15 * MINUTE
        ro = orders.order(b, site, opened, customer, car, advisor, [job], pay="card", start=start,
                          waits=[(since, dt.datetime.combine(T + dt.timedelta(60), dt.time(12)))])
        record = b.orders[id(ro)]
        record["waiting"] = since
        if n == 0:
            ro["promised_at"] = dt.datetime.combine(a["calls"][15]["day"] + dt.timedelta(2), orders.PROMISE[cfg])
            nine_day(b, record, opened_day)


def nine_day(b, record, opened_day):
    """nf.conv.06: the first purchase order to V2 placed the day after the car came in, promised for 7 days before T
    (ru 6, a Saturday) and cancelled after missing it; the second placed the next open day, promised for west's 4th
    full open day before T (ru the day after call 15), not received by T. kb.deposits: half of the special-order part
    taken with the first order."""
    cfg, a = b.cfg, b.a
    T = a["T"].date()
    line = record["parts"][0]
    first_at = orders.hours(b, "west", working(b, "west", opened_day, 1))[0] + 30 * MINUTE
    first_promise = dt.datetime.combine(T - dt.timedelta(7 if cfg == "en" else 6), dt.time(14))
    second_day = clock.wd(cfg, T, -4) if cfg == "en" else a["calls"][15]["day"] + clock.DAY
    second_at = orders.hours(b, "west", working(b, "west", first_promise.date(), 1))[0] + 30 * MINUTE
    for at, promised, status in ((first_at, first_promise, "cancelled"), (second_at, max(second_at + 2 * HOUR, dt.datetime.combine(second_day, dt.time(14))), "ordered")):
        po = b.add("purchase_order", location_id=b.shops["west"], vendor_id=b.vendors["V2"], repair_order_id=record["order"], status=status,
                   ordered_at=at, promised_at=promised, received_at=None)
        b.add("purchase_order_line", purchase_order_id=po, part_id=None, description=line["description"], quantity_ordered=line["quantity"],
              quantity_received=Decimal(0), unit_cost=line["unit_cost"])
    worth = line["unit_price"] * line["quantity"]
    if worth > Decimal(str(inputs.value("kb.deposits", cfg)["on_special_order_parts_over"])):
        record["payments"].append({"repair_order_id": record["order"], "kind": "deposit", "method": "card", "amount": (worth / 2).quantize(Decimal("0.01")),
                                   "received_at": first_at, "taken_by_id": record["order"]["advisor_id"],
                                   "reference": f"{streams.stream(b.seed, 'nine-day deposit').randrange(10 ** 6):06d}"})
    record["parts_done"] = True


def ready_of(record):
    """When an order's work may start as `orders.settle` reads it: its start, or its first approval and its look."""
    approved = [j["decided"] for j in record["jobs"] if j["status"] == "approved" and j.get("decided")]
    if not approved:
        return None
    return record["start"] or max([min(approved)] + [record["looked"]] * bool(record["looked"]))


def restart(b, record, start, waits=()):
    """The order's work from `start` (the shop's next open minute), the clock stopped for `waits`, through
    `orders.settle`; when no mechanic has room the start moves to the next day; statuses a later step added (a re-issued
    bill) move with the completion. An order whose work would go to another mechanic, or a closed one that would be open
    at T or finish more than two weeks later, keeps its times as they were: returns whether the new ones stand."""
    ro = record["order"]
    before = {k: record[k] for k in ("start", "waits", "added", "history", "entries", "payments", "booked", "left", "deposit")}
    status, techs = ro["status"], [(j, j.get("tech"), j.get("labor_row") and j["labor_row"]["technician_id"]) for j in record["jobs"]]
    done = next((h["changed_at"] for h in record["history"] if h["status"] == "completed"), None)
    start, settled = orders.opening(b, record["site"], start) if start else record["start"], False
    for _ in range(5):
        record["start"], record["waits"] = start, list(waits)
        try:
            orders.settle(b, record)
            settled = True
            break
        except ValueError:
            if not start:
                break
            start = orders.opening(b, record["site"], dt.datetime.combine(start.date() + clock.DAY, dt.time()))
    now = next((h["changed_at"] for h in record["history"] if h["status"] == "completed"), None)
    same = all(j.get("tech") is tech for j, tech, _ in techs)  # the dealt mechanic still does it (his hours and comebacks stand)
    stopped = not waits or any(h["status"] == "waiting_parts" for h in record["history"])
    if settled and same and stopped and (status not in ("invoiced", "paid") or ro["status"] in ("invoiced", "paid") and now and now <= done + dt.timedelta(14)):
        return True
    for tech, piece in record["booked"]:
        b.timeline[id(tech), piece[0].date()].remove(piece)
    for tech, piece in before["booked"]:
        bisect.insort(b.timeline.setdefault((id(tech), piece[0].date()), []), piece)
    record.update(before)
    ro["status"] = status
    for j, tech, row_tech in techs:
        j["tech"] = tech
        if row_tech is not None:
            j["labor_row"]["technician_id"] = row_tech
    return False


def fill(b):
    cfg, a = b.cfg, b.a
    T = a["T"]
    rng = streams.stream(b.seed, "parts")
    # (their times are a card's; a re-issued or split bill's statuses stand between its bill and its payment)
    keep_out = lambda r: r.get("early") or r.get("leaving") or r.get("planted") or r.get("open") or r.get("waiting") or r["added"]  # noqa: E731
    records = sorted((o for o in b.orders.values() if not o.get("parts_done")), key=lambda o: o["order"]["opened_at"])
    wanted = []  # (record, [(order line, vendor, decision)])
    for record in records:
        decided = {id(j["row"]): max(j.get("decided") or record["order"]["opened_at"], record["order"]["opened_at"]) for j in record["jobs"]}
        wanted.append((record, [(line, vendor_of(b, record["site"], line["brand"]), decided[id(line["order_job_id"])]) for line in record["parts"]
                                if line["part_id"] is not None and line["order_job_id"]["status"] == "approved"]))

    # parts.po_per_order is held by the stocked list: it grows by the next highest-running part slots of `ranking` until
    # purchase orders, a week's stock order per shop and vendor among them, come to the row (spec 4.10)
    visits = sum(1 for o in b.orders.values() if o["order"]["status"] not in ("declined", "void"))
    extra = []

    def count(shelf):
        special = sum(len({(v, d) for line, v, d in lines if id(line["part_id"]) not in shelf[r["site"]]}) for r, lines in wanted)
        weeks = {(r["site"], d.date() - dt.timedelta(d.weekday()), v) for r, lines in wanted for line, v, d in lines if id(line["part_id"]) in shelf[r["site"]]}
        return special + len(weeks)
    shelf = stocked(b)
    for name in ranking(cfg)[:REACH]:
        if count(shelf) <= inputs.value("parts.po_per_order", cfg) * visits:
            break
        extra.append(name)
        shelf = stocked(b, extra)

    pos = []  # [purchase order, its lines, the record or None, the order lines]
    for record, lines in wanted:
        bought = collections.defaultdict(list)
        for line, vendor, decided in lines:
            if id(line["part_id"]) not in shelf[record["site"]]:
                bought[vendor, decided].append(line)
        for (vendor, decided), lines_ in sorted(bought.items(), key=lambda x: (x[0][1], x[0][0])):
            po = b.add("purchase_order", location_id=b.shops[record["site"]], vendor_id=b.vendors[vendor], repair_order_id=record["order"],
                       status="ordered", ordered_at=decided, promised_at=promise(b, vendor, record["site"], decided), received_at=None)
            for line in lines_:
                line["vendor_id"] = b.vendors[vendor]
            pos.append([po, [b.add("purchase_order_line", purchase_order_id=po, part_id=line["part_id"], description=line["description"],
                                   quantity_ordered=line["quantity"], quantity_received=Decimal(0), unit_cost=line["unit_cost"]) for line in lines_], record, lines_])

    # the shelf's issues as the orders now start; stock orders (erp.stock.reorder) and the opening stock (spec 7b)
    def issues():
        out = []
        for record, lines in wanted:
            started = next((h["changed_at"] for h in record["history"] if h["status"] == "in_progress"), None)
            out += [(record["site"], line, started) for line, _, _ in lines if id(line["part_id"]) in shelf[record["site"]] and started]
        return out
    weekly = collections.defaultdict(collections.Counter)
    first_weeks = collections.defaultdict(collections.Counter)
    for site, line, at in issues():
        weekly[site, at.date() - dt.timedelta(at.weekday() - 7)][id(line["part_id"])] += line["quantity"]
        if at.date() < (a["bought"] if site == "west" else a["history_start"]) + dt.timedelta(84):
            first_weeks[site][id(line["part_id"])] += line["quantity"]
    # every part a shop's shelf may give out (its orders' lines, S02's loose issues; main also east's, which draws on it)
    # has a par: twice its mean weekly issue of the first twelve weeks, at least one (`shelves` raises main's and west's)
    parts, par = {}, {}
    given = [(r["site"], line["part_id"]) for r, lines in wanted for line, _, _ in lines] + [(site_of(b, m["location_id"]), m["part_id"]) for m in b.tables["stock_movement"]]
    for site, part in given + [("main", part) for site, part in given if site == "east"]:
        if id(part) in shelf[site]:
            parts[id(part)] = part
            par[site, id(part)] = max(1, math.ceil(2 * first_weeks[site][id(part)] / 12))
    for site in reference.SITES:  # the opening stock: the par, a stock order received before the history (spec 7b), on the
        # last full open day, so main's is in before east can draw on it
        day = clock.snap(cfg, (a["bought"] if site == "west" else a["history_start"]) - clock.DAY, -1)
        weekly[site, day] = collections.Counter({pid: n for (s, pid), n in par.items() if s == site})
    opening = set()
    for (site, monday), counts in sorted(weekly.items(), key=lambda x: (reference.SITES.index(x[0][0]), x[0][1])):
        day = monday
        while orders.hours(b, site, day) is None:
            day += clock.DAY
        at = orders.hours(b, site, day)[0] + 30 * MINUTE
        if at > orders.until(b, site):
            continue
        by_vendor = collections.defaultdict(list)
        for pid, qty in sorted(counts.items(), key=lambda x: (parts[x[0]]["description"], parts[x[0]]["brand"], str(parts[x[0]]["part_number"]))):
            by_vendor[vendor_of(b, site, parts[pid]["brand"])].append((parts[pid], math.ceil(qty)))
        first = monday < (a["bought"] if site == "west" else a["history_start"])
        for vendor, lines in sorted(by_vendor.items()):
            po = b.add("purchase_order", location_id=b.shops[site], vendor_id=b.vendors[vendor], repair_order_id=None, status="ordered",
                       ordered_at=at, promised_at=at + 2 * HOUR if first else promise(b, vendor, site, at), received_at=None)  # (spec 7b: the opening stock comes that day)
            pos.append([po, [b.add("purchase_order_line", purchase_order_id=po, part_id=part, description=part["description"], quantity_ordered=Decimal(qty),
                                   quantity_received=Decimal(0), unit_cost=part["cost"]) for part, qty in lines if qty > 0], None, None])
            if first:
                opening.add(id(po))

    late, special, wants = waits(b, pos, keep_out)

    # parts.on_time.<vendor>: dealt over each vendor's purchase orders promised by T: the waiting orders' late ones
    # first, then stock orders, then orders that start after their late part; a card's order and the opening stock on time
    for vendor in b.vendors:
        mine = [x for x in pos if x[0]["vendor_id"] is b.vendors[vendor] and x[0]["promised_at"] <= T and not (x[2] and x[2].get("waiting"))]
        n = round(len(mine) * (100 - inputs.value(f"parts.on_time.{vendor}", cfg)) / 100) - sum(id(x[0]) in late for x in mine) if mine else 0
        free = [x for x in mine if id(x[0]) not in late and id(x[0]) not in special and id(x[0]) not in opening and x[0]["promised_at"] <= T - dt.timedelta(5)
                and not (x[2] and (keep_out(x[2]) or x[2]["returned"]))]
        others = [x for x in free if x[2] is not None]
        streams.stream(b.seed, "late", vendor).shuffle(others)
        for x in ([x for x in free if x[2] is None] + others)[:max(0, n)]:
            late[id(x[0])] = working(b, site_of(b, x[0]["location_id"]), x[0]["promised_at"].date(), 1 + rng.randrange(3))

    # receipts: with the run (spec 7b: within the hour after it), or on the late day at that hour
    def receive(po, day=None):
        at = po["promised_at"]
        if day is not None:  # a late delivery comes at the promised hour, inside that day's hours (en main's Saturday morning)
            span = orders.hours(b, site_of(b, po["location_id"]), day)
            at = min(max(dt.datetime.combine(day, at.time()), span[0]), span[1] - HOUR)
        received = arrival(b, at, po["ordered_at"])
        now = orders.until(b, site_of(b, po["location_id"]))  # T on the shop's own clock
        po.update(status="received" if received <= now else "ordered", received_at=received if received <= now else None)
    by_record, lines_of = collections.defaultdict(list), {}
    for po, rows, record, lines in pos:
        lines_of[id(po)] = lines or []
        if record is None:
            receive(po, late.get(id(po)))
            continue
        by_record[id(record["order"])].append(po)
        if record.get("waiting"):
            continue
        receive(po, late.get(id(po)))
        started = next((h["changed_at"] for h in record["history"] if h["status"] == "in_progress"), None)
        if keep_out(record) and started and po["received_at"] and po["received_at"] > started:  # a card's times stand: its part is in by then
            po["received_at"] = po["promised_at"] = max(po["ordered_at"], started - 5 * MINUTE, orders.hours(b, record["site"], started.date())[0])

    # no work before its parts are in (`install` holds it for every order the background wrote). The orders dealt to wait
    # (the special ones first, then the others in a dealt order, to each group's count) work until their part is wanted
    # and stop until it comes; an order with a late part otherwise starts after it. One whose work then finds no room
    # (`restart`) keeps its times: a waiting order then starts after its part, and failing that its parts come on time.
    def started_of(record):
        return next((h["changed_at"] for h in record["history"] if h["status"] == "in_progress"), None)
    for group, sites in (("west", ("west",)), ("home", ("main", "east"))):
        pool = [r for r in records if r.get("awaited") and r["site"] in sites]
        first = [r for r in pool if id(r["awaited"]) in special]
        rest = [r for r in pool if id(r["awaited"]) not in special]
        streams.stream(b.seed, "waiting orders", group).shuffle(rest)
        kept = 0
        for record in first + rest:
            po = record.pop("awaited")
            # (a part that comes before the work would stop for it holds nothing up)
            if (kept < wants[group] or id(po) in special) and (po["received_at"] or T + clock.DAY) > stop(record) > started_of(record) \
                    and stop(record) >= orders.hours(b, record["site"], stop(record).date())[0] \
                    and restart(b, record, started_of(record), [(stop(record), po["received_at"] or T + clock.DAY)]):
                record["awaited"] = po
                kept += 1
            elif id(po) in special:
                po["promised_at"] = special.pop(id(po))[2]
                receive(po)
    for record in records:
        mine = by_record.get(id(record["order"]))
        started = started_of(record)
        if not mine or keep_out(record) or not started or record.get("awaited") or record.get("returned"):  # (one that came back keeps its times)
            continue
        # each job after its own parts: a late line holds back its job, not the order's other work
        job_of = {id(j["row"]): j for j in record["jobs"] if j.get("row")}
        begun = {}
        for e in record["entries"]:
            begun.setdefault(id(e["order_job_id"]), e["clock_in"])
        late = {}
        for po in mine:
            for line in lines_of[id(po)]:
                j = job_of.get(id(line["order_job_id"]))
                if j and (po["received_at"] or T + clock.DAY) > begun.get(id(j), T + clock.DAY):
                    late[id(j)] = max(late.get(id(j), started), po["received_at"] or T + clock.DAY)
        if late:
            for j in record["jobs"]:
                if id(j) in late:
                    j["after"] = late[id(j)]
            if not restart(b, record, None):
                for j in record["jobs"]:
                    j.pop("after", None)
                for po in mine:
                    if po["received_at"] is None or any(po["received_at"] > begun.get(id(job_of.get(id(line["order_job_id"]))), T) for line in lines_of[id(po)]):
                        receive(po)
    # whatever still comes after the work that needs it (another line of an order that waits, a promise later than the
    # start it was kept for) comes before it, as a card's times do: no part is fitted after its job began
    for record in records:
        if record.get("waiting"):
            continue
        firsts = {}  # a job's row to its first clock-in (an entry names the job, a line its row)
        for e in record["entries"]:
            firsts.setdefault(id(e["order_job_id"].get("row")), e["clock_in"])
        for po in by_record.get(id(record["order"]), ()):
            need = min((firsts[id(line["order_job_id"])] for line in lines_of[id(po)] if id(line["order_job_id"]) in firsts), default=None)
            if po is not record.get("awaited") and need and (po["received_at"] is None or po["received_at"] > need) and po["ordered_at"] <= need:
                po.update(status="received", received_at=max(po["ordered_at"], need - 5 * MINUTE, orders.hours(b, record["site"], need.date())[0]))
                po["promised_at"] = po["received_at"]
    for po_id, (record, worth, _) in special.items():  # the deposit of section 4.7, taken when the part is ordered (kb.deposits)
        po = record["awaited"]
        deposit = (worth / 2).quantize(Decimal("0.01"))
        pay = next((p for p in record["payments"] if p["kind"] == "payment"), None)
        if pay:
            pay["amount"] -= deposit
        on = orders.advisors(b, record["site"], po["ordered_at"].date())
        record["payments"].append({"repair_order_id": record["order"], "kind": "deposit", "method": record["pay"], "amount": deposit, "received_at": po["ordered_at"],
                                   "taken_by_id": record["order"]["advisor_id"] if not on or orders.slot_of(b, record["order"]["advisor_id"]) in on else b.people[on[0]],
                                   "reference": None if record["pay"] == "cash" else f"{streams.stream(b.seed, 'deposit', po['ordered_at']).randrange(10 ** 6):06d}"})

    # movements: a receipt for every line received, the issue to its order line a minute later; the shelf's issues when
    # the job starts (at main and east the parts manager on his weekdays, else the order's advisor)
    receipts = {}
    for po, rows, record, lines in pos:
        if po["received_at"] is None:
            continue
        site = site_of(b, po["location_id"])
        for row, line in zip(rows, lines or [None] * len(rows)):
            who = keeper(b, site, record, po["received_at"].date())
            receipts[id(row)] = b.add("stock_movement", location_id=po["location_id"], part_id=row["part_id"], kind="receipt", quantity=row["quantity_ordered"],
                                      unit_cost=row["unit_cost"], moved_at=po["received_at"], employee_id=who, purchase_order_line_id=row)
            if line is not None:
                b.add("stock_movement", location_id=po["location_id"], part_id=row["part_id"], kind="issue", quantity=-row["quantity_ordered"],
                      unit_cost=row["unit_cost"], moved_at=min(po["received_at"] + MINUTE, orders.until(b, site)), employee_id=who, order_part_id=line)
    for site, line, at in issues():
        record = b.orders[id(line["order_job_id"]["repair_order_id"])]
        if at <= orders.until(b, site):
            b.add("stock_movement", location_id=b.shops[site], part_id=line["part_id"], kind="issue", quantity=-line["quantity"], unit_cost=line["unit_cost"],
                  moved_at=at, employee_id=keeper(b, site, record, at.date()), order_part_id=line)
    returned = returns(b, pos, receipts, opening)
    shelves(b, shelf, [(po, rows) for po, rows, record, _ in pos if record is None], receipts, returned, par)
    for po, rows, _, _ in pos:  # a received order's lines came in whole (the stock lines sized by `shelves`)
        for row in rows:
            row["quantity_received"] = row["quantity_ordered"] if po["received_at"] else Decimal(0)
    for n, po in enumerate(sorted(b.tables["purchase_order"], key=lambda p: p["ordered_at"]), 1):
        po["number"] = f"{'PO' if cfg == 'en' else 'ЗП'}-{n:06d}"
    till(b)


def keeper(b, site, record, day):
    """Who records a movement: at main and east the parts manager on his weekdays, else the order's advisor."""
    manager = b.people["9"]
    if site != "west" and orders.in_post(manager, day) and clock.full_open(b.cfg, day) and day.weekday() < 5:
        return manager
    if record:
        return record["order"]["advisor_id"]
    on = orders.advisors(b, site, day)
    return b.people[on[0]] if on else None


def waits(b, pos, keep_out):
    """parts.wait_over_a_day: west's (since the purchase) and the home shops' orders spend more than a day in
    waiting_parts at their rows, the cars waiting at T counted: closed orders with a purchase order, opened three weeks
    or more before T, no comeback holding to them, whose work begins before the part it waits for. First the special
    orders of 2 working days or more (spec 4.10): counter orders whose awaited purchase order costs the customer more
    than kb.deposits' limit, promised 2 to 5 (ru 2 to 10) working days ahead, about 300 dealt evenly over the history;
    then orders whose awaited purchase order comes 1 to 3 working days late, a third more than the count (`fill` keeps the
    count). Returns the purchase orders made late, with their day; the special ones, with their record, worth and first
    promise; and each group's count."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    rng = streams.stream(b.seed, "waits")
    limit = Decimal(str(inputs.value("kb.deposits", cfg)["on_special_order_parts_over"]))
    days = inputs.value("kb.supplier_times", cfg)["special_orders_working_days"]
    returned = {id(o["order"]["comeback_of_id"]) for o in b.orders.values() if o["order"]["comeback_of_id"]}
    for o in b.orders.values():
        o["returned"] = id(o["order"]) in returned

    def waited(record):
        return sum((min(till, T) - since for since, till in record["waits"]), dt.timedelta()) > dt.timedelta(1)
    by_order = collections.defaultdict(list)
    for x in pos:
        if x[2] is not None:
            by_order[id(x[2]["order"])].append(x)
    candidates = [o for o in b.orders.values() if id(o["order"]) in by_order and o["order"]["status"] in ("invoiced", "paid") and not keep_out(o)
                  and not o["returned"] and T - o["order"]["opened_at"] > dt.timedelta(21) and ready_of(o)
                  and stop(o) > next(h["changed_at"] for h in o["history"] if h["status"] == "in_progress")]
    candidates.sort(key=lambda o: o["order"]["opened_at"])

    def worth(x):
        return sum(line["quantity"] * line["unit_price"] for line in x[3])
    counter = [(o, max(by_order[id(o["order"])], key=worth)) for o in candidates if o["pay"] and not o["order"]["customer_id"].get("payment_terms_days")]
    dear = [(o, x) for o, x in counter if worth(x) > limit]
    n = min(len(dear), 300)  # spec 4.10 and section 10: about 300 deposits at full size
    chosen = [dear[int((i + 0.5) * len(dear) / n)] for i in range(n)] if n else []
    late, special, wants = {}, {}, {}
    for o, x in chosen:
        po = x[0]
        promised = promise(b, vendor_key(b, po), o["site"], dt.datetime.combine(working(b, o["site"], po["ordered_at"].date(), rng.randint(*days)), dt.time()))
        special[id(po)] = (o, worth(x), po["promised_at"])
        po["promised_at"] = promised
        o["awaited"] = po
    for group, sites in (("west", ("west",)), ("home", ("main", "east"))):
        visits = [o for o in b.orders.values() if o["site"] in sites and o["order"]["status"] not in ("declined", "void")]
        wants[group] = round(len(visits) * inputs.value(f"parts.wait_over_a_day.{group}", cfg) / 100) - sum(waited(o) for o in visits)
        want = round(1.3 * wants[group]) - sum(o["site"] in sites for o, _ in chosen)  # a third more: some find no room after the wait
        pool = [o for o in candidates if o["site"] in sites and not o.get("awaited")]
        rng.shuffle(pool)
        for o in pool:
            if want <= 0:
                break
            po = max((x[0] for x in by_order[id(o["order"])]), key=lambda p: p["promised_at"])
            for k in (1, 2, 3):
                day = working(b, o["site"], po["promised_at"].date(), k)
                if dt.datetime.combine(day, po["promised_at"].time()) - stop(o) > dt.timedelta(1, minutes=20):
                    late[id(po)] = day
                    o["awaited"] = po
                    want -= 1
                    break
    return late, special, wants


def stop(record):
    """When a waiting order's work stops for its part: ten minutes before the work would have been done."""
    return next(h["changed_at"] for h in record["history"] if h["status"] == "completed") - 10 * MINUTE


def vendor_key(b, po):
    return next(k for k, v in b.vendors.items() if v is po["vendor_id"])


def returns(b, pos, receipts, opening):
    """parts.returned_share of purchase-order lines go back (kb.returns): one unit or the line, the credit asked at
    cost, a reason of texts.json, inside the return window of the receipt, after it; erp.part_return.rejected_share
    refused, the rest credited 7 to 30 days later, or still sent when returned in the last 30 days; a vendor_return
    movement when the part had gone on the shelf (a stock order's line; the opening stock is not sent back). Returns the
    shelf's returns, movement to (return, line, whole line or one unit): `shelves` sizes the stock lines afterwards."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    rng = streams.stream(b.seed, "returns")
    window = inputs.value("kb.returns", cfg)["return_window_days"]
    lines = [(row, po) for po, rows, _, _ in pos for row in rows]
    able = [(row, po) for row, po in lines if po["received_at"] and po["received_at"] < T - dt.timedelta(1) and id(po) not in opening]
    chosen = sorted(rng.sample(able, min(len(able), round(len(lines) * inputs.value("parts.returned_share", cfg) / 100))), key=lambda x: x[1]["received_at"])
    refused = set(rng.sample(range(len(chosen)), round(len(chosen) * inputs.value("erp.part_return.rejected_share", cfg) / 100)))
    shelf = {}
    for i, (row, po) in enumerate(chosen):
        whole = rng.random() < 0.5
        qty = row["quantity_ordered"] if row["quantity_ordered"] <= 1 or whole else Decimal(1)
        day = min(po["received_at"].date() + dt.timedelta(1 + rng.randrange(window)), (T - dt.timedelta(1)).date())
        site = site_of(b, po["location_id"])
        while orders.hours(b, site, day) is None and day > po["received_at"].date():  # a part goes back on a day the shop trades
            day -= clock.DAY
        credited = day + dt.timedelta(7 + rng.randrange(24))
        status = "rejected" if i in refused else "sent" if (T.date() - day).days < 30 or credited > T.date() else "credited"
        back = b.add("part_return", purchase_order_line_id=row, quantity=qty, amount=(qty * row["unit_cost"]).quantize(Decimal("0.01")),
                     reason=streams.pick(rng, orders.TEXTS[cfg]["part_return_reasons"]), returned_on=day, status=status,
                     credited_on=credited if status == "credited" else None)
        if po["repair_order_id"] is None:
            span = orders.hours(b, site, day)
            moved = min(max(span[0] + HOUR, po["received_at"] + HOUR), span[1] - MINUTE, orders.until(b, site))
            m = b.add("stock_movement", location_id=po["location_id"], part_id=row["part_id"], kind="vendor_return", quantity=-qty, unit_cost=row["unit_cost"],
                      moved_at=moved, employee_id=receipts[id(row)]["employee_id"], part_return_id=back)
            shelf[id(m)] = (back, row, whole)
    return shelf


def shelves(b, shelf, stock, receipts, returned, par):
    """Spec 4.10 and 7b, each shop's shelf: at each half-yearly stocktake in the history (the Thursday of the next one's
    ISO week, a year back, and of the week 26 from it; the Tuesday when the Thursday is closed)
    erp.stock.stocktake_adjust_share of the stocked lines move by one unit, one fewer only when there is one; ru west from
    the rule a weekly write-off of one unit of a fluid (kb.till.west_since_the_rule). Then, part by part in time order,
    every stock-order line (`stock`: the opening stock and the weekly orders) brings the part back up to its par, on the
    shelf and on order, by at least one unit; so a week's order replaces what left the shelf, sold, sent back, moved to
    east or lost at a count. East, which runs short, draws the shortfall from main on the last 13:00 run before it
    (kb.supplier_times); main's and west's par is raised to the most their shelf gives out between two deliveries, so
    neither runs dry. stock_level is the sum of each stocked part's movements at T."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    rng = streams.stream(b.seed, "stocktake")
    moves, parts = collections.defaultdict(list), {}
    for m in b.tables["stock_movement"]:
        site = site_of(b, m["location_id"])
        if id(m["part_id"]) in shelf[site]:
            moves[site, id(m["part_id"])].append(m)
            parts[id(m["part_id"])] = m["part_id"]
    order = sorted(moves, key=lambda k: (reference.SITES.index(k[0]), parts[k[1]]["description"], parts[k[1]]["brand"], str(parts[k[1]]["part_number"])))
    staff = {"main": b.people["9"], "east": b.people["9"], "west": b.people["22"]}

    def move(site, pid, kind, qty, at, note=None):
        moves[site, pid].append(b.add("stock_movement", location_id=b.shops[site], part_id=parts[pid], kind=kind, quantity=Decimal(qty),
                                      unit_cost=parts[pid]["cost"], moved_at=at, employee_id=staff[site], note=note))
    year, week, _ = a["stocktake"].isocalendar()
    # (a year without the stocktake's week 53 counts in its last week, the one 28 December falls in)
    thursdays = [dt.date.fromisocalendar(y, min(w, dt.date(y, 12, 28).isocalendar()[1]), 4) for y in range(year - 3, year + 1) for w in (week, (week + 25) % 52 + 1)]
    counts = sorted({d for d in thursdays if a["history_start"] < d < T.date()})
    for count in counts:
        day = count if not clock.closed(cfg, count) else count - dt.timedelta(2)
        keys = [k for k in order if not (k[0] == "west" and day < a["bought"])]
        for site, pid in rng.sample(keys, round(len(keys) * inputs.value("erp.stock.stocktake_adjust_share", cfg) / 100)):
            move(site, pid, "adjustment", rng.choice((-1, 1)), orders.hours(b, site, day)[0])  # counted at opening
    if cfg == "ru":
        fluids = [k for k in order if k[0] == "west" and parts[k[1]]["part_number"] is None]
        day = a["rule_on"]
        while fluids and day <= T.date():
            if day.weekday() == 0 and orders.hours(b, "west", day) and orders.hours(b, "west", day)[1] - HOUR <= orders.until(b, "west"):
                site, pid = streams.pick(rng, fluids)
                move(site, pid, "adjustment", -1, orders.hours(b, "west", day)[1] - HOUR, "списание расходников")
            day += clock.DAY
    placed = collections.defaultdict(list)
    for po, rows in stock:
        for row in rows:
            placed[site_of(b, po["location_id"]), id(row["part_id"])].append((po["ordered_at"], row))

    def run(site, pid, top):
        """The part's shelf in time order (an order placed, then inflows, then outflows at one minute) with par `top`:
        sizes its stock lines, the returns of them, a count's sign and east's draws on main; returns its lowest level."""
        level = on_order = low = Decimal(0)
        events = [(t, 0, row) for t, row in placed[site, pid]] + [(m["moved_at"], 1 if m["quantity"] > 0 else 2, m) for m in moves[site, pid]]
        for t, kind, x in sorted(events, key=lambda e: (e[0], e[1])):
            if kind == 0:
                x["quantity_ordered"] = Decimal(max(1, math.ceil(top - level - on_order)))
                on_order += x["quantity_ordered"]
                if id(x) in receipts:
                    receipts[id(x)]["quantity"] = x["quantity_ordered"]
                continue
            if id(x) in returned:
                back, row, whole = returned[id(x)]
                back["quantity"] = row["quantity_ordered"] if row["quantity_ordered"] <= 1 or whole else Decimal(1)
                back["amount"] = (back["quantity"] * row["unit_cost"]).quantize(Decimal("0.01"))
                x["quantity"] = -back["quantity"]
            if x["kind"] == "receipt":
                on_order -= x["quantity"]
            if x["kind"] == "adjustment" and x.get("note") is None and level + x["quantity"] < 0:
                x["quantity"] = Decimal(1)
            if site == "east" and level + x["quantity"] < 0:
                at = dt.datetime.combine(t.date(), dt.time(13))
                while at > t or orders.hours(b, "east", at.date()) is None:
                    at = dt.datetime.combine(at.date() - clock.DAY, dt.time(13))
                qty = math.ceil(-(level + x["quantity"]))
                move("main", pid, "transfer_out", -qty, at)
                move("east", pid, "transfer_in", qty, at)
                level += qty
            level += x["quantity"]
            low = min(low, level)
        return low
    for site, pid in sorted(order, key=lambda k: k[0] != "east"):  # east first: its draws are main's outflows
        top = par.get((site, pid), 0)
        if site != "east":
            top += math.ceil(-run(site, pid, top))  # (whole units: the opening line moves the level by as much)
        run(site, pid, top)
    for site, pid in sorted(moves, key=lambda k: (reference.SITES.index(k[0]), parts[k[1]]["description"], parts[k[1]]["brand"], str(parts[k[1]]["part_number"]))):
        b.add("stock_level", location_id=b.shops[site], part_id=parts[pid], quantity_on_hand=sum(m["quantity"] for m in moves[site, pid]))


def till(b):
    """Spec 4.9 after the parts moved collections: each close expects its day's cash payments less cash refunds again,
    and is counted off by the difference it had."""
    cash = collections.Counter()
    for o in b.orders.values():
        for pay in o["payments"]:
            if pay["method"] == "cash":
                cash[o["site"], pay["received_at"].date()] += pay["amount"] * (-1 if pay["kind"] == "refund" else 1)
    for row in b.tables["cash_drawer_close"]:
        row["expected_cash"] = cash[site_of(b, row["location_id"]), row["business_date"]] or orders.ZERO
        row["counted_cash"] = row["expected_cash"] + row["difference"]


def reminders(b):
    """service_reminder (spec section 3), after the odometers. deferred_work: one per deferred job, due and raised on
    its decision day; done when a later order of the car carries the same job, dismissed when no later order came in
    12 months, sent erp.reminder.send_after_days after the decision when that is by T, else pending. maintenance_due:
    one per approved oil_service of a closed order, due at mileage_out (mileage_in while the car is in) plus the lower
    end of kb.maintenance_intervals oil; done when a later oil service exists, else pending."""
    cfg, a = b.cfg, b.a
    T = a["T"].date()
    after = dt.timedelta(inputs.value("erp.reminder.send_after_days", cfg))
    interval = int(inputs.value("kb.maintenance_intervals", cfg)["oil"].split(" to ")[0].replace(",", "").replace(" ", ""))
    by_car = collections.defaultdict(list)
    records = sorted(b.orders.values(), key=lambda o: o["order"]["opened_at"])
    for o in records:
        if o["order"]["status"] not in ("declined", "void"):
            by_car[id(o["order"]["vehicle_id"])].append(o)
    for o in records:
        ro = o["order"]
        later = [x for x in by_car[id(ro["vehicle_id"])] if x["order"]["opened_at"] > ro["opened_at"]]
        for j in o["jobs"]:
            row = j.get("row")
            if row is None:
                continue
            done = next((x["order"] for x in later if any(k["key"] == j["key"] and k["status"] == "approved" for k in x["jobs"])), None)
            if row["deferred"] and row["decided_at"]:
                day = row["decided_at"].date()
                status = "done" if done else "dismissed" if not later and day + dt.timedelta(365) <= T else "sent" if day + after <= T else "pending"
                b.add("service_reminder", customer_id=ro["customer_id"], vehicle_id=ro["vehicle_id"], order_job_id=row, kind="deferred_work",
                      description=row["description"], due_on=day, due_mileage=None, status=status, sent_on=day + after if status == "sent" else None,
                      done_repair_order_id=done, created_on=day)
            elif j["key"] == "oil_service" and j["status"] == "approved" and ro["status"] in ("invoiced", "paid"):
                b.add("service_reminder", customer_id=ro["customer_id"], vehicle_id=ro["vehicle_id"], order_job_id=None, kind="maintenance_due",
                      description=row["description"], due_on=None, due_mileage=(ro["mileage_out"] or ro["mileage_in"]) + interval,
                      status="done" if done else "pending", sent_on=None, done_repair_order_id=done,
                      created_on=next(h["changed_at"] for h in o["history"] if h["status"] == "completed").date())
