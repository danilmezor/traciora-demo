"""Section 5 of generator-spec.md, "The story files' new facts" that stand alone (the rows S01, S04, S06, S07 and S08
plant are theirs): the bookings, orders, comebacks and histories of the story calls' and conversations' people.
`place(b)` writes them before `background.fill`, so they count inside the day's volume, the advisors' shares, the
mechanics' hours and their dealt comebacks. A booking whose day is not after T is a visit that happened (spec section
1): the appointment arrived with its order; a first-time person's record is written at check-in (ru chat 13: with the
booking), and the booking keeps `contact_name` and `contact_phone` (spec section 3, appointment). Days are the story
files' (`clock.anchors`: a call's day, call + n days, a conversation's days, the weeks T-k); so are the times, readings,
odometers and car classes a file states (spec section 7b), the rest drawn as a background visit draws it."""
import datetime as dt
import re
from decimal import ROUND_HALF_UP, Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, orders, plan, reference

CHANNEL = {"chat": "web_chat"}  # every other channel of a conversation (telegram, vk, avito) is a messenger booking
FACTS = inputs.load("checks/new_facts.json")
ODOMETER = re.compile(r"([\d,]+) (?:miles|km)\b")
# spec section 7b: ru call 33's father is named by his given name only
FATHER_33 = re.search(r"ru call 33's father «([^»]+)»", (inputs.SEED / "erp" / "generator-spec.md").read_text(encoding="utf-8"))[1]


def place(b):
    cfg, a, seed = b.cfg, b.a, b.seed
    en, week = cfg == "en", a["week_day"]
    calls, convs = a["calls"], a["conversations"]
    texts = orders.TEXTS[cfg]
    T = a["T"]
    plates = inputs.value("erp.vehicle.plates", cfg)

    def at(day, hhmm):
        return dt.datetime.combine(day, dt.time(*map(int, hhmm.split(":"))))

    def record(key, when):
        """The story person's record and cars; a first-time person's leaves b.pending, created at `when`."""
        if key in b.pending:
            c, cars = b.pending.pop(key)
            c["created_at"] = when
            b.named[key] = (c, cars)
            b.tables["customer"].append(c)
            b.tables["vehicle"].extend(cars)
        return b.named[key]

    def call_booking(n):
        """A call's booking: by phone, by the person at the answering desk (cast.json extension), at the call's start."""
        f = inputs.STORY_FILES["calls", cfg][n]["call"]
        by = next(p["slot"] for p in reference.CAST["people"] if p.get("extension") == f["answered_by"] and orders.in_post(b.people[p["slot"]], calls[n]["day"]))
        return "phone", by, at(calls[n]["day"], f["local_start"])

    def chat_booking(n, by=None):
        """A conversation's booking: web chat or messenger by its channel, by the staff member it was handed to (or the
        one a row names), at the hand-over."""
        f = inputs.STORY_FILES["conversations", cfg][n]
        given = f["conversations"][0]["assignee_history"][0]
        return CHANNEL.get(f["conversations"][0]["channel"], "messenger"), by or str(given["to"]), at(convs[n]["days"][given["day"]], given["at"][:5])

    def beats(n, day):
        """A conversation's work day as its messages on `day` (a key of its days) date it: the customer's decision (her
        first message after the shop's first), the car ready (the shop's first message an hour or more after it), her
        coming for it (her next message), and her first message an hour or more after the decision."""
        lines = [(m["from"], at(convs[n]["days"][day], m["at"][:5])) for m in inputs.STORY_FILES["conversations", cfg][n]["conversations"][0]["timeline"]
                 if m["day"] == day and m.get("text") and m.get("from") in ("customer", "staff")]
        first = next(t for who, t in lines if who == "staff")
        decided = next(t for who, t in lines if who == "customer" and t > first)
        ready = next((t for who, t in lines if who == "staff" and t - decided >= dt.timedelta(hours=1)), None)
        coming = next((t for who, t in lines if who == "customer" and ready and t >= ready), None)
        later = next((t for who, t in lines if who == "customer" and t - decided >= dt.timedelta(hours=1)), None)
        return decided, ready, coming, later

    def stated(kind, n):
        """The odometer a story file states for its person's car (new_facts.json: the car, then the facts)."""
        x = next(x for x in FACTS[f"{kind}.{cfg}"] if int(x["number"]) == n)
        m = ODOMETER.search(" ".join([(x.get("person") or {}).get("car") or "", *x["facts"]]))
        return int(m[1].replace(",", ""))

    def lead(site, day, car, rng):
        """A history order's own job, drawn as the background draws a lead job (spec section 4.3)."""
        p = {"site": site, "day": day, "vehicle": car}
        return customers.weighted(rng, {k: plan.SHARES[cfg][k]["lead"] * plan.curve(cfg, k, day) for k in plan.PRICED if plan.allowed(b, p, k)})

    def ahead(site, t):
        """A booked day on which the shop is shut at that hour: the same hour of its next day open then, as spec section 1
        moves a call's day (the first on or after); a booking stays after the call or chat that made it."""
        while not (span := orders.hours(b, site, t.date())) or not span[0] <= t < span[1]:
            t += clock.DAY
        return t

    def morning(key, site, day):  # "this morning": a check-in drawn in the first hour and a half after opening
        return orders.hours(b, site, day)[0] + streams.stream(seed, "fact morning", key, day).randrange(90) * orders.MINUTE

    def classed(key, site, cls):
        """The person's car, drawn again of class `cls` when the file's price is that class's (spec section 7b)."""
        c, cars = b.named.get(key) or b.pending[key]
        if cars[0]["vehicle_class"] != cls:
            shape, words = streams.stream(seed, "named car", key, cls), streams.stream(seed, "named car words", key, cls)
            models = [m for m in customers.PARC[cfg]["models"] if m["vehicle_class"] == cls]
            m = models[customers.weighted(shape, {i: m["share"] for i, m in enumerate(models)})]
            year = customers.PARC[cfg]["reference_year"] - customers.weighted(shape, customers.ages(cfg, m))
            cars[0].update(customers.drawn(b, c, m, year, shape, words, "named" if en else customers.weighted(words, plates["region_by_shop"][site])))

    def visit(key, site, opened, jobs, *, advisor=None, tech=None, book=None, contact=None, first=None, car=None, customer=None, done=None, paid=None,
              mileage=None, collected=True):
        """One order of a story person at `site` (jobs: catalogue keys or job dicts of orders.order, standard tier),
        with its arrived booking (source, booked_by, booked_at); a booking after T on the shop's clock is only the
        appointment. The advisor and mechanic are the row's, else drawn among those on duty (the diagnostician first
        for a diagnosis). A file's stated times: `done` the car ready (the jobs decided after check-in fill the time from
        their decision up to it, else the work starts so as to end then), `paid` the collection, `collected` False for a car
        nobody fetches (invoiced, no payment); `mileage` its odometer."""
        fresh = key in b.pending
        rng = streams.stream(seed, "fact", key, opened)
        c, cars = b.named.get(key) or b.pending[key]
        car = car or cars[0]
        jobs = [dict({"key": j} if isinstance(j, str) else j) for j in jobs]
        x = orders.JOBS[jobs[0]["key"]][cfg]
        minutes = max(30, -(-int(float(orders.sold_hours(cfg, jobs[0]["key"], car)) * 60) // 30) * 30)
        name = c["name"] if contact is None else contact or None
        if book and opened > orders.until(b, site):
            b.add("appointment", location_id=b.shops[site], customer_id=None if fresh else c, vehicle_id=None if fresh else car,
                  contact_name=name if fresh else None, contact_phone=c["phone"] if fresh else None, starts_at=opened, duration_min=minutes,
                  source=book[0], status="confirmed" if opened - T <= dt.timedelta(2) else "booked", reason=x["name"], booked_at=book[2],
                  booked_by_id=b.people[book[1]])
            return None
        c, cars = record(key, opened - rng.randint(1, 10) * orders.MINUTE)
        customer = customer or c
        day = opened.date()
        on = orders.advisors(b, site, day)
        if advisor not in on:
            advisor = streams.pick(rng, on)
        crew = dict(orders.mechanics(b, site, day))
        diagnostician = orders.DIAGNOSTICIAN.get(site, (None,))[0] if orders.JOBS[jobs[0]["key"]]["category"] == "diagnostics" else None
        mechanic = b.people[tech] if tech else crew.get(diagnostician) or streams.pick(rng, [crew[s] for s in sorted(crew)])
        for j in jobs:
            j.setdefault("status", "approved")
            j.setdefault("tier", "standard")
            if j["status"] == "approved":
                j.update(tech=mechanic, keep=True)
            if j.get("found") and "reading" not in j:
                j["reading"] = orders.reading(cfg, j["key"], j["found"], rng)
            if "value" not in j:
                lines = {k: j.pop(k) for k in ("parts", "fees") if k in j}  # a story's own lines in place of the catalogue's
                orders.price(b, day, customer, car, j)
                if lines:
                    j.update(lines)
                    j["value"] = ((j["labor"] or {}).get("amount", orders.ZERO) + (j["sublet"]["price"] if j["sublet"] else orders.ZERO)
                                  + sum((p["quantity"] * p["unit_price"]).quantize(orders.CENT, ROUND_HALF_UP) for p in j["parts"]))
        start = None
        if done:
            done = min(done, orders.shift(b, site, day)[1])  # "ready" said after the mechanics' shift: the work ends with it
            late = [j for j in jobs if j["status"] == "approved" and j["labor"] and j.get("decided")]
            work = late or [j for j in jobs if j["status"] == "approved" and j["labor"] and j["key"] != "courtesy_inspection"]
            normal = [orders.clocked(b, j) for j in work]
            span = int((done - max(j["decided"] for j in late)) / orders.MINUTE) if late else min(sum(normal), int((done - opened) / orders.MINUTE) - 15)
            if late:  # done by then, the clock at most an hour over the order's sold hours (section 7, S2.8)
                sold = 60 * sum(float(j["labor"]["hours"]) for j in jobs if j["status"] == "approved" and j["labor"])
                early = sum(orders.clocked(b, j) for j in jobs if j["status"] == "approved" and j["labor"] and j not in work and j["key"] != "courtesy_inspection")
                span = min(span, int(sold + 60 - early) - 5)
            for j, n in zip(work, normal):
                j["clocked"] = max(1, round(span * n / sum(normal)))
            work[-1]["clocked"] += span - sum(j["clocked"] for j in work)
            start = None if late else done - span * orders.MINUTE
        booking = book and {"source": book[0], "booked_by": book[1], "booked_at": book[2], "starts_at": opened, "duration": minutes}
        ro = orders.order(b, site, opened, customer, car, advisor, jobs, kind="warranty" if first else "customer_pay", comeback_of=first, booking=booking,
                          start=start, pay=None if paid or not collected else "card", complaint=None if first else x["name"])
        written = b.orders[id(ro)]
        written["planted"] = True  # a story's own order comes back only where its file says (one that does counts in its mechanic's comebacks)
        if booking and (fresh or contact is not None):
            written["appointment"].update(contact_name=name, contact_phone=c["phone"])
        if paid:
            orders.status(b, ro, "paid", paid)
            b.add("payment", repair_order_id=ro, kind="payment", method="card", amount=ro["total"], received_at=paid,
                  taken_by_id=b.people[(orders.advisors(b, site, paid.date()) or [advisor])[0]], reference=f"{rng.randrange(10 ** 6):06d}")
        if mileage:
            written["stated"] = ro["mileage_in"] = mileage
            ro["mileage_out"] = mileage + rng.randint(0, 15)
        return ro

    def history(key, site, lo, hi, jobs=(), car=None, drawn=False, n=0, customer=None):
        """An order of a regular's history on a day drawn from lo to before hi (west: from its purchase) at a drawn
        hour; with `drawn`, its own job drawn ahead of what the row puts on it."""
        rng = streams.stream(seed, "fact history", key, hi, n)
        lo = max(lo, a["bought"] if site == "west" else a["history_start"])
        day = streams.pick(rng, [d for d in (lo + dt.timedelta(i) for i in range((hi - lo).days)) if orders.advisors(b, site, d)])
        car = car or (b.named.get(key) or b.pending[key])[1][0]
        return visit(key, site, plan.moment(b, rng, site, day), [lead(site, day, car, rng)] * drawn + list(jobs), car=car, customer=customer)

    def regular(key, site, hi):
        """A regular's own visits before `hi`, as many as erp.customer.visits_per_year gives over the shop's window."""
        lo = a["bought"] if site == "west" else a["history_start"]
        for n in range(round(inputs.value("erp.customer.visits_per_year", cfg) * (hi - lo).days / 365.25)):
            history(key, site, lo, hi, drawn=True, n=n)

    def relative(key, given=None, family=None, female=False):
        """A relative of a story person no file names in full (spec section 7b): the given or family name the files
        give, the rest from the generator's lists; a long-standing customer of west, in its bulk load, with a car of
        her or his own unless one is handed over."""
        rng = streams.stream(seed, "relative", key)
        names, gender = customers.NAMES[cfg], "female" if female else "male"
        given = given or streams.pick(rng, names["given"][gender])
        family = family or streams.pick(rng, names["family"] if en else names["family"][gender])
        name = f"{given} {family}" if en else f"{family} {given} {streams.pick(rng, names['patronymic'][gender])}"
        b.taken.add(customers.full_name(name))
        return b.add("customer", kind="person", name=name, created_location_id=b.shops["west"], created_at=customers.created(b, "west", rng))

    def own_car(key, owner, site):  # a car of a person's own, drawn as a background car
        return b.add("vehicle", **customers.car(b, owner, site, streams.stream(seed, "own car", key), streams.stream(seed, "own car words", key),
                                                "named" if en else customers.weighted(streams.stream(seed, "own car plate", key), plates["region_by_shop"][site])))

    def after(t, key, limit=30):  # a collection the file dates only by "after t": drawn within `limit` minutes
        return t + streams.stream(seed, "fact collected", key).randrange(1, limit) * orders.MINUTE

    def month(day, m):  # the first day of the latest month m that begins before `day`, and the first day after it
        start = dt.date(day.year if day.month > m else day.year - 1, m, 1)
        return start, (start + dt.timedelta(32)).replace(day=1)

    def reading(group, kind, starts):  # the texts.json reading a row states ("3 mm"; en chat 17's clunk is play)
        return next(r for r in texts["readings"][group][kind] if starts(r))

    def after_noon(key, site, day):  # en and ru chat 19: the visit opens after 12:00
        close = orders.hours(b, site, day)[1]
        return at(day, "12:00") + streams.stream(seed, "fact", key, "noon").randrange(int((close - at(day, "12:00")) / orders.MINUTE) - 90) * orders.MINUTE

    def relatives_visit(key, parent, job):
        """Chat 19: the parent's car moves to the parent's own record; the son keeps his record, a car of his own and
        his history as a regular; the walk-in visit on the parent's record after 12:00."""
        son, (car,) = b.named[key]
        car["customer_id"] = parent
        mine = own_car(key, son, "west")
        b.named[key] = (son, [mine])
        day = week(-16, 1)
        regular(key, "west", day)
        visit(key, "west", after_noon(key, "west", day), [job], car=car, customer=parent)

    first_time = ((3, 0, "12:30", ["battery_replace"], ""), (4, 1, "10:00", ["check_engine_diag"], None), (5, 4, "13:30", ["wheel_alignment"], None),
                  (6, 2, "08:00", ["wheel_bearing"], None), (14, 2, "08:00", ["rear_pads_rotors"], None), (26, 1, "07:30", ["suspension_diag"], None),
                  (31, 0, "09:00", ["check_engine_diag"], None), (32, 0, "08:00", ["tyre_repair"], None)) if en else \
                 ((3, 1, "10:00", ["oil_service"], ""), (4, 1, "11:00", ["suspension_diag"], None), (5, 5, "09:00", ["sway_bar_links"], None),
                  (14, 3, "14:00", ["drive_belt"], "first"), (26, 1, "10:00", ["front_struts_pair", "wheel_alignment"], None),
                  (31, 0, "13:00", ["check_engine_diag"], None), (32, 1, "09:30", ["exhaust_muffler"], "first"), (36, 0, "16:00", ["wheel_alignment"], "first"))
    odometer = {26} if en else {3, 26}  # the first-time callers whose file states the car's odometer
    for n, plus, hhmm, jobs, name in first_time:
        key = f"call.{n:02d}"
        site = inputs.STORY_FILES["calls", cfg][n]["call"]["site"]
        contact = b.pending[key][0]["name"].split()[0] if name == "first" else name
        visit(key, site, ahead(site, at(calls[n]["day"] + dt.timedelta(plus), hhmm)), jobs, book=call_booking(n), contact=contact, tech="10" if en and n == 31 else None,
              mileage=stated("call", n) if n in odometer else None)

    # the uncollected car (erp.uncollected_car): a private regular of west, drawn from its customers with an earlier
    # visit of his drawn before; a job whose parts come from the shelf (no purchase order moves it), in that morning,
    # done and invoiced on west's 3rd full open day before T and never collected: no payment, invoiced at T, no
    # storage fee (kb.storage's free days)
    rng = streams.stream(seed, "uncollected car")
    day = clock.wd(cfg, T.date(), -3)
    b.named["uncollected"] = streams.pick(rng, b.pools["west"])
    car = b.named["uncollected"][1][0]
    history("uncollected", "west", a["bought"], day - dt.timedelta(30), drawn=True)
    p = {"site": "west", "day": day, "vehicle": car}
    job = customers.weighted(rng, {k: plan.SHARES[cfg][k]["lead"] * plan.curve(cfg, k, day) for k in plan.PRICED if plan.allowed(b, p, k)
                                   and orders.sold_hours(cfg, k, car) and all(k in orders.STOCKED for _ in orders.JOBS[k][cfg]["parts"])})
    visit("uncollected", "west", morning("uncollected", "west", day), [job], collected=False)

    if en:
        # call 27: her last oil service has a battery item watch and no job for it; then the booked test and battery
        ro = history("call.27", "east", a["history_start"], calls[27]["day"] - dt.timedelta(30), ["oil_service", "courtesy_inspection"])
        item = next(i for i in b.orders[id(ro)]["items"] if i["component"] == orders.GROUPS[cfg][4])
        item.update(result="watch", measurement=orders.reading(cfg, "battery_replace", "watch", streams.stream(seed, "fact", "call.27", "battery")))
        visit("call.27", "east", ahead("east", at(calls[27]["day"] + dt.timedelta(1), "07:30")), ["battery_test", "battery_replace"], book=call_booking(27))
        history("call.28", "east", a["history_start"], calls[28]["day"], drawn=True)
        first = visit("call.29", "main", plan.moment(b, streams.stream(seed, "fact", "call.29"), "main", week(-10, 1)), ["lower_control_arm"], tech="11")
        visit("call.29", "main", at(calls[29]["day"], "14:00"), ["wheel_alignment"], first=first, book=call_booking(29))
        # call 30: the Friday's water pump, paid about 15:40 (she picked the car up an hour before the 16:40 call);
        # the comeback that evening, the tow on it at the shop's cost, inside the hook-up's distance (spec section 7b)
        day = calls[30]["day"]
        first = visit("call.30", "main", orders.hours(b, "main", day)[0], ["water_pump"], tech="11", paid=at(day, "15:40"))
        ro = visit("call.30", "main", at(day, "17:20"), ["water_pump"], first=first)
        written = b.orders[id(ro)]  # a tow is no subcontracted repair: the car does not wait for it, and at price 0 it moves no total
        written["sublets"].append(b.add("order_sublet", order_job_id=written["jobs"][0]["row"], vendor_id=b.vendors["V8"], description=b.vendors["V8"]["name"],
                                       cost=Decimal(inputs.value("kb.towing", cfg)["hook_up"]), price=orders.ZERO))
        history("call.33", "west", a["bought"], calls[33]["day"], ["courtesy_inspection", {"key": "ball_joint", "status": "declined", "found": "watch"}], drawn=True)
        # call 34: the record is his mother's, Peggy Womack's, with his number (spec section 7b)
        b.named["call.34"][0]["name"] = re.search(r"customer of west, ([^,]+),", next(x for x in FACTS["call.en"] if x["number"] == "34")["facts"][0])[1]
        history("call.34", "west", a["bought"], calls[34]["day"], drawn=True)
        day = calls[36]["day"]
        history("call.36", "west", clock.months_back(day, 4), clock.months_back(day, 2), ["front_brake_pads"])
        visit("call.36", "west", at(day, "14:00"), ["cooling_pressure_test"], book=call_booking(36))

        # conversation 08: rear brakes found bad and declined at her last visit; the booking on slot 16's last working
        # day before her week off (rule A), an order by her when that day is not after T
        history("conv.08", "east", a["history_start"], convs[8]["days"]["T-1d"],
                ["courtesy_inspection", {"key": "rear_brake_pads", "status": "declined", "found": "bad", "photo": True}], drawn=True)
        visit("conv.08", "east", at(a["booking"], "13:00"), ["rear_brake_pads"], advisor="16", book=chat_booking(8))
        # conversation 09: ready at 4 and collected then ("see you at 4")
        day = convs[9]["days"]["T-127d"]
        hour = next(int(m[1]) for x in inputs.STORY_FILES["conversations", cfg][9]["conversations"][0]["timeline"] if (m := re.search(r"ready at (\d+)\b", x.get("text") or "")))
        ready = at(day, f"{hour % 12 + 12}:00")  # an afternoon hour
        visit("conv.09", "main", morning("conv.09", "main", day), ["alternator"], advisor="5", done=ready, paid=after(ready, "conv.09", 15))
        visit("conv.10", "main", at(convs[10]["days"]["T-60d"], "14:00"), ["cooling_pressure_test"], book=chat_booking(10))
        # conversation 11: the oil change done that morning; the rear pads at 3 mm and the cabin filter found with photos,
        # decided at 11:12, ready at 13:24, collected after 13:30
        day = convs[11]["days"]["T-80d"]
        decided, ready, coming, _ = beats(11, "T-80d")
        visit("conv.11", "main", morning("conv.11", "main", day),
              ["oil_service", "courtesy_inspection", {"key": "rear_brake_pads", "found": "bad", "photo": True, "method": "message", "decided": decided,
                                                     "reading": reading("brake pads", "bad", lambda r: r.startswith("3"))},
               {"key": "cabin_air_filter", "status": "declined", "found": "watch", "photo": True, "method": "message", "decided": decided}], advisor="6",
              done=ready, paid=after(coming, "conv.11"))
        classed("conv.12", "main", "car")
        visit("conv.12", "main", at(convs[12]["days"]["T-29d"], "08:00"), ["wheel_alignment"], book=chat_booking(12))
        visit("conv.13", "main", at(convs[13]["days"]["T-84d"], "08:30"), ["oil_service"], book=chat_booking(13),
              contact=inputs.STORY_FILES["conversations", cfg][13]["conversations"][0]["contact"]["name"])
        visit("conv.14", "main", at(convs[14]["days"]["T-23d"], "10:00"), ["brake_fluid_exchange"], book=chat_booking(14))
        # conversation 15: the comeback booked in the chat for 13:00, done before her 14:20 "all quiet now"
        first = history("conv.15", "east", week(-16, 0), week(-16, 0) + dt.timedelta(5), ["front_brake_pads"])
        quiet = beats(15, "T-107d")[3]
        visit("conv.15", "east", at(convs[15]["days"]["T-107d"], "13:00"), ["front_brake_pads"], first=first, book=chat_booking(15),
              done=quiet - streams.stream(seed, "fact", "conv.15", "done").randrange(5, 30) * orders.MINUTE)
        visit("conv.16", "east", at(convs[16]["days"]["T-51d"], "08:30"), ["pre_purchase_inspection"], book=chat_booking(16))
        given = inputs.STORY_FILES["conversations", cfg][17]["conversations"][0]["assignee_history"][0]["at"][:5]
        visit("conv.17", "east", plan.moment(b, streams.stream(seed, "fact", "conv.17"), "east", week(-12, 3)),
              ["oil_service", "courtesy_inspection", {"key": "sway_bar_links", "status": "declined", "found": "watch", "method": "message",
                                                     "reading": reading("shocks and struts", "watch", lambda r: "play" in r),
                                                     "decided": at(convs[17]["days"]["T-84d"], given)}], advisor="17")
        # conversation 18: four tyres he brought, mounted and balanced (no part lines), the disposal at kb.tyre_fees_each
        # a tyre, the state fee not charged
        classed("conv.18", "east", "car")
        day = convs[18]["days"]["T-140d"]
        fee = re.sub(r" and [^,]*\(\$[\d.]+\)", "", orders.JOBS["new_tyres_fitted"][cfg]["fees"][0]["name"])
        visit("conv.18", "east", at(day, "14:00"), [{"key": "new_tyres_fitted", "parts": [],
                                                     "fees": [("tyre_disposal", fee, 4 * Decimal(str(inputs.value("kb.tyre_fees_each", cfg)["disposal"])))]}],
              book=chat_booking(18))
        relatives_visit("conv.19", relative("conv.19", family=b.named["conv.19"][0]["name"].split()[-1], female=True), "suspension_diag")
        classed("conv.20", "west", "car")
        visit("conv.20", "west", orders.hours(b, "west", week(-9, 1))[0], ["water_pump"])
        classed("conv.22", "west", "car")
        day = week(-5, 2)
        visit("conv.22", "west", plan.moment(b, streams.stream(seed, "fact", "conv.22"), "west", day),
              [lead("west", day, b.named["conv.22"][1][0], streams.stream(seed, "fact lead", "conv.22")), "courtesy_inspection",
               {"key": "rear_brake_pads", "status": "declined", "found": "bad", "reading": reading("brake pads", "bad", lambda r: r.startswith("3"))}])
        # conversation 23: in that morning for the diagnosis; coil and plugs found and approved by message at 13:15;
        # ready at 16:22, collected after her 16:35 "on my way"
        day = convs[23]["days"]["T-70d"]
        decided, ready, coming, _ = beats(23, "T-70d")
        visit("conv.23", "west", morning("conv.23", "west", day),
              ["check_engine_diag", "courtesy_inspection", {"key": "ignition_coil", "found": "bad", "method": "message", "decided": decided},
               {"key": "spark_plugs", "found": "bad", "method": "message", "decided": decided}], advisor="24", mileage=stated("conv", 23),
              done=ready, paid=after(coming, "conv.23"))
        visit("conv.24", "west", at(convs[24]["days"]["T-122d"], "11:30"), ["battery_test"], book=chat_booking(24))
        visit("conv.25", "west", at(convs[25]["days"]["T-92d"], "07:30"), ["check_engine_diag"], book=chat_booking(25))
        day = convs[26]["days"]["T-43d"]
        history("conv.26", "east", *month(day, 3), ["wheel_balance"])
        history("conv.26", "east", *month(day, 6), ["battery_test"])
        visit("conv.26", "east", at(day, "09:00"), ["brake_inspection"], book=chat_booking(26))
        return

    # ru call 27: his own car (the file's words) with a hub job in its history; his daughter's car, on his record,
    # booked for an oil service on the Thursday after the call, at its stated odometer
    words = re.search(r"\(([^;()]+);", next(x for x in FACTS["call.ru"] if x["number"] == "27")["facts"][0])[1]
    region = customers.weighted(streams.stream(seed, "named car plate", "call.27"), plates["region_by_shop"]["east"])
    own = b.add("vehicle", **customers.story_car(b, b.named["call.27"][0], words, streams.stream(seed, "named car", "call.27", "own"),
                                                 streams.stream(seed, "named car words", "call.27", "own"), region))
    history("call.27", "east", a["history_start"], calls[27]["day"], ["wheel_bearing"], car=own)
    visit("call.27", "east", ahead("east", at(calls[27]["day"] + dt.timedelta(3), "10:00")), ["oil_service", "engine_air_filter", "cabin_air_filter"], book=call_booking(27),
          mileage=stated("call", 27))
    history("call.28", "east", a["history_start"], calls[28]["day"], drawn=True)
    # calls 29 and 30: slot 11's orders and their warranty comebacks on the call's day; 29's opened 20 minutes after
    # the call, its work by the foreman
    day = calls[29]["day"]
    # (a day before the call that is shut moves back to the last full open day: no file says)
    first = visit("call.29", "main", plan.moment(b, streams.stream(seed, "fact", "call.29"), "main", clock.snap(cfg, day - dt.timedelta(1), -1)), ["front_pads_rotors"], tech="11")
    ro = visit("call.29", "main", call_booking(29)[2] + 20 * orders.MINUTE, ["front_pads_rotors"], first=first)
    written = b.orders[id(ro)]
    for tech, piece in written["booked"]:  # slot 8 is on no mechanics' roster: the work's clock is his
        b.timeline[id(tech), piece[0].date()].remove(piece)
    written["booked"] = []
    for row in [j["labor_row"] for j in written["jobs"] if j.get("labor_row")] + written["entries"]:
        row["technician_id"] = b.people["8"]
    day = calls[30]["day"]
    first = visit("call.30", "main", plan.moment(b, streams.stream(seed, "fact", "call.30"), "main", clock.snap(cfg, day - dt.timedelta(2), -1)), ["oil_service"], tech="11")
    visit("call.30", "main", at(day, "14:00"), ["oil_service"], first=first, book=call_booking(30))
    # call 33: the caller's father «Фарид», a long-standing customer of west with his history (spec section 7b)
    father = relative("call.33", given=FATHER_33)
    b.named["call.33.father"] = (father, [own_car("call.33", father, "west")])
    regular("call.33.father", "west", calls[33]["day"])
    history("call.34", "west", a["bought"], calls[34]["day"], drawn=True)

    history("conv.08", "east", a["history_start"], convs[8]["days"]["T-1d"],
            ["oil_service", "courtesy_inspection", {"key": "rear_brake_pads", "status": "declined", "found": "watch"}])
    visit("conv.08", "east", at(a["booking"], "14:00"), ["rear_brake_pads"], advisor="16", book=chat_booking(8))
    visit("conv.09", "main", plan.moment(b, streams.stream(seed, "fact", "conv.09"), "main", convs[9]["days"]["T-126d"]), ["wheel_bearing"], advisor="5")
    # conversation 10: he phones that afternoon; the clutch with his own kit on slot 5's next working day, 09:00
    day = convs[10]["days"]["T-58d"] + clock.DAY
    while "5" not in orders.advisors(b, "main", day):
        day += clock.DAY
    rang = at(convs[10]["days"]["T-58d"], "13:00") + streams.stream(seed, "fact", "conv.10", "call").randrange(240) * orders.MINUTE
    visit("conv.10", "main", at(day, "09:00"), [{"key": "clutch_kit", "parts": []}], book=("phone", "5", rang))
    visit("conv.11", "main", at(convs[11]["days"]["T-76d"], "10:00"), ["oil_service"], book=chat_booking(11))
    # conversation 12: the service done that morning; the links and the wipers found with photos, decided at 13:19;
    # ready at 15:02, collected after her 15:05
    day = convs[12]["days"]["T-35d"]
    decided, ready, coming, _ = beats(12, "T-35d")
    visit("conv.12", "main", morning("conv.12", "main", day),
          ["oil_service", "courtesy_inspection", {"key": "sway_bar_links", "found": "bad", "photo": True, "method": "message", "decided": decided},
           {"key": "wiper_blades", "status": "declined", "found": "watch", "photo": True, "method": "message", "decided": decided}], advisor="6",
          done=ready, paid=after(coming, "conv.12"))
    book = chat_booking(13)
    c, _ = record("conv.13", book[2])
    visit("conv.13", "main", ahead("main", at(convs[13]["days"]["T-84d"], "09:00")), ["cv_axle"], book=book, contact=c["name"])
    visit("conv.14", "main", at(convs[14]["days"]["T-22d"], "18:00"), ["seasonal_tyre_change"], book=chat_booking(14))
    first = history("conv.15", "east", week(-16, 0), week(-16, 0) + dt.timedelta(7), ["ac_recharge"])
    visit("conv.15", "east", ahead("east", at(convs[15]["days"]["T-105d"], "09:30")), ["ac_performance_check"], first=first, book=chat_booking(15))
    visit("conv.16", "east", at(convs[16]["days"]["T-51d"], "11:00"), ["pre_purchase_inspection"], book=chat_booking(16, "17"))
    visit("conv.18", "east", at(convs[18]["days"]["T-30d"], "18:30"), ["seasonal_tyre_change"], book=chat_booking(18))
    relatives_visit("conv.19", relative("conv.19", family=b.named["conv.19"][0]["name"].split()[-1]), "cooling_pressure_test")
    classed("conv.20", "west", "car")  # (the file's labour is a car's: 3 % of 4,180)
    visit("conv.20", "west", orders.hours(b, "west", week(-9, 1))[0], ["water_pump"])
    classed("conv.22", "west", "car")
    day = clock.snap(cfg, convs[22]["days"]["T-34d"] - dt.timedelta(1), -1)  # (shut: back to the last full open day; no file says)
    visit("conv.22", "west", plan.moment(b, streams.stream(seed, "fact", "conv.22"), "west", day),
          [lead("west", day, b.named["conv.22"][1][0], streams.stream(seed, "fact lead", "conv.22")), "courtesy_inspection",
           {"key": "front_brake_pads", "status": "declined", "found": "bad", "reading": reading("brake pads", "bad", lambda r: r.startswith("2"))}])
    # conversation 23: in that morning for the pressure test; the pump and the belt found and approved by message at
    # 14:20; ready at 18:41, collected after his 18:50
    day = convs[23]["days"]["T-68d"]
    decided, ready, coming, _ = beats(23, "T-68d")
    visit("conv.23", "west", morning("conv.23", "west", day),
          ["cooling_pressure_test", "courtesy_inspection", {"key": "water_pump", "found": "bad", "method": "message", "decided": decided},
           {"key": "drive_belt", "found": "bad", "method": "message", "decided": decided}], advisor="24",
          done=ready, paid=after(coming, "conv.23"))
    visit("conv.24", "west", at(convs[24]["days"]["T-120d"], "17:00"), ["ac_recharge"], book=chat_booking(24))
    visit("conv.25", "east", at(convs[25]["days"]["T-92d"], "18:00"), ["check_engine_diag"], book=chat_booking(25, "17"))
    day = convs[26]["days"]["T-43d"]
    history("conv.26", "main", *month(day, 4), ["seasonal_tyre_change"])
    history("conv.26", "main", *month(day, 5), ["wheel_alignment"])
    visit("conv.26", "main", at(day, "11:00"), ["seasonal_tyre_change", "wheel_alignment"], book=chat_booking(26))
