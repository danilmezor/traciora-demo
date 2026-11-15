"""Section 5 of generator-spec.md, the stories of this module: S02 (with M5, the walk-in record), S04, S05, S07, S08 and
slot 8's open second look. S11, S13, S14 and S16 are carried by the background (seasons, F4, closed dates, F2) and by
S01's rows. `place(b)` writes the planted orders before the background fills every day to its count around them, so
each is counted in its day's volume, its advisor's share, its mechanic's hours and comebacks; `close(b)` adds what
follows the finished background: S8's second bill and payment, and en F1's voids after payment and his till.

A planted order's record (`b.orders[id(row)]`) carries `story` when `close` comes back to it, and `alone` when no
comeback may follow it (section 7: S7's and S8's phones are their own; S5.3's eleven orders). Times a card does not
give are drawn by the background's own rules (`plan.moment`, `jobs_for`); the choices no source fixes are named where they are made."""
import datetime as dt
import re
from decimal import Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, orders, plan

MINUTE = orders.MINUTE
DIAGNOSTICS = [k for k in plan.PRICED if plan.JOBS[k]["category"] == "diagnostics"]


def at(day, text):
    return dt.datetime.combine(day, dt.time.fromisoformat(text if len(text) > 5 else f"{text:0>5}"))


def days(start, end):
    return [start + dt.timedelta(i) for i in range((end - start).days)]


def jobs_for(b, rng, site, day, vehicle, tech, leads=plan.PRICED):
    """A visit's jobs as the background draws them (spec section 4.3): a lead by share_of_orders.lead and its season
    among `leads`, customer add-ons to mix.json jobs_per_order, the courtesy inspection at its share, tiers by
    tier_mix; every job with the mechanic `tech`, kept with him."""
    cfg, share = b.cfg, plan.SHARES[b.cfg]
    p = {"site": site, "day": day, "vehicle": vehicle}
    keys = [customers.weighted(rng, {k: share[k]["lead"] * plan.curve(cfg, k, day) for k in leads if plan.allowed(b, p, k)})]
    for _ in range(int(customers.weighted(rng, plan.MIX[cfg]["jobs_per_order"]["distribution"])) - 1):
        weights = {k: share[k]["addon"] * plan.curve(cfg, k, day) for k in plan.PRICED if k not in keys and plan.allowed(b, p, k)}
        if sum(weights.values()):
            keys.append(customers.weighted(rng, weights))
    if rng.random() < plan.JOBS["courtesy_inspection"][cfg]["share_of_orders"]["total"]:
        keys.append("courtesy_inspection")
    return [{"key": k, "status": "approved", "tech": tech, "tier": customers.weighted(rng, plan.MIX[cfg]["tier_mix"]), "keep": True} for k in keys]


def priced(b, site, day, customer, vehicle, jobs):
    """Prices the jobs in place (`orders.order` keeps prices already set) and returns the order's labour, its bill before
    any discount (labour, parts, sublets, fees) and its total with tax (spec section 1, Tax)."""
    for j in jobs:
        orders.price(b, day, customer, vehicle, j)
    labor, parts, sublet, fees, _ = orders.bill(b, jobs)
    gross = labor + parts + sublet + fees
    rate = orders.tax_rate(b, site, day)
    return labor, gross, gross if b.cfg == "ru" else gross + (gross * rate / 100).quantize(orders.CENT, orders.ROUND_HALF_UP)


def mechanic(b, site, day, rng, slot=None):
    """`slot`'s employee row when he works at the shop that day, else one of the mechanics on duty."""
    crew = orders.mechanics(b, site, day)
    return dict(crew).get(slot) or streams.pick(rng, crew)[1]


def place(b):
    s2(b)
    s4(b)
    s5(b)
    s7(b)
    s8(b)
    second_look(b)


def close(b):
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "stories close")
    f1 = b.people["F1"]
    for record in [r for r in b.orders.values() if r.get("planted") in ("s8", "s2.void")]:
        ro = record["order"]
        if record["planted"] == "s8":
            # slot 4's next working day: after his call (call 11) the bill is re-opened, invoiced again with the discount
            # and paid that afternoon by card (nf.call.11: en in the afternoon, ru about 18:00)
            call = at(a["s8_discount"], inputs.STORY_FILES["calls", cfg][11]["call"]["local_start"])
            orders.status(b, ro, "completed", call + 10 * MINUTE)
            orders.status(b, ro, "invoiced", call + 25 * MINUTE)
            paid = at(a["s8_discount"], "13:00") + rng.randrange(240) * MINUTE if cfg == "en" else at(a["s8_discount"], "17:50") + rng.randrange(21) * MINUTE
            orders.status(b, ro, "paid", paid)
            on = orders.advisors(b, "main", paid.date())
            b.add("payment", repair_order_id=ro, kind="payment", method="card", amount=ro["total"], received_at=paid,
                  taken_by_id=b.people["7" if "7" in on or not on else on[0]], reference=f"{rng.randrange(10 ** 6):06d}")
        elif record["planted"] == "s2.void":
            # en second way: voided after the cash was taken, the same day, the payment kept (s2.f1.second)
            paid = next(h["changed_at"] for h in reversed(record["history"]) if h["status"] == "paid")
            close_ = orders.hours(b, "west", paid.date())[1]
            when = paid + rng.randrange(1, max(2, int((close_ - paid) / MINUTE))) * MINUTE
            orders.status(b, ro, "void", when)
            ro.update(voided_at=when, voided_by_id=f1, void_reason="customer changed mind")
    if cfg == "en":
        till(b, rng)


def till(b, rng):
    """en third way (s2.f1.third, spec section 4.9): F1 closes exactly of_days_he_closed of west's tills (days he was on
    duty are moved to him, or from him to another advisor on duty); 19 of them inside the 26 weeks short by 20 or more,
    summing to -1,700, noted with texts.json till_note."""
    a = b.a
    f1, row = b.people["F1"], inputs.value("s2.f1.third", "en")
    west = [r for r in b.tables["cash_drawer_close"] if r["location_id"] is b.shops["west"]]
    rng.shuffle(west)
    west.sort(key=lambda r: not a["s2_start"] <= r["business_date"] < a["fired"])  # inside his 26 weeks first
    his = [r for r in west if r["closed_by_id"] is f1]
    if len(his) < row["of_days_he_closed"]:
        for r in [r for r in west if r["closed_by_id"] is not f1 and "F1" in orders.advisors(b, "west", r["business_date"])][:row["of_days_he_closed"] - len(his)]:
            r["closed_by_id"] = f1
    for r in reversed(his[row["of_days_he_closed"]:]):
        others = [s for s in orders.advisors(b, "west", r["business_date"]) if s != "F1"]
        if others:
            r["closed_by_id"] = b.people[others[0]]
    short = [r for r in west if r["closed_by_id"] is f1 and a["s2_start"] <= r["business_date"] < a["fired"]][:row["count"]]
    raw = [Decimal(rng.randint(0, 14000)) for _ in short]
    spare = Decimal(row["total"] - 20 * row["count"])
    cuts = [(x * spare / sum(raw)).quantize(orders.CENT) for x in raw]
    cuts[0] += spare - sum(cuts)
    was_exact = sum(r["difference"] == 0 for r in short)
    for r, cut in zip(short, cuts):
        r.update(difference=-(20 + cut), counted_cash=r["expected_cash"] - 20 - cut, note=orders.TEXTS["en"]["till_note"])
    # pay.till_exact_days is dealt over the shops' last 365 days: as many of their other uneven closes as the shorts
    # took from the even ones count even, so the share stands
    year = a["T"].date() - dt.timedelta(365)
    uneven = [r for r in b.tables["cash_drawer_close"] if r["difference"] != 0 and r["business_date"] > year and not any(r is x for x in short)]
    for r in rng.sample(uneven, min(was_exact, len(uneven))):
        r.update(difference=orders.ZERO, counted_cash=r["expected_cash"], note=None)


def s2(b):
    """S02 at west. F1's s2.f1.cash_orders cash orders spread over his days of the 26 weeks: s2.f1.discounted of them
    with an unapproved labour discount of 15 to 30 % (mean 22.5 %) summing to s2.f1.discount_total; en 14 whose totals
    sum to s2.f1.second's (voided after payment by `close`); ru 22 on which the mechanics clocked s2.f1.third's hours
    over the hours sold; 49 of them on the walk-in record (s2.walkin: the discounted, en the voids, ru the first 14 of
    the 22), each with its own car; the rest by customers of west's pool. ru: F1's 46 stock issues with no order line.
    After the rule (s2.west.discounts_after): two cash discounts approved by slot 22 and slot 23's two of 12 %. The
    background gives F1 his other orders (his share), none of them in cash, and the walk-in record its other orders."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "s2")
    texts = orders.TEXTS[cfg]
    mine = [d for d in days(a["s2_start"], a["fired"]) if "F1" in orders.advisors(b, "west", d)]
    n = inputs.value("s2.f1.cash_orders", cfg)
    second, third = inputs.value("s2.f1.second", cfg), inputs.value("s2.f1.third", cfg)
    special = second["count"] if cfg == "en" else third["count"]
    kinds = ["discount"] * inputs.value("s2.f1.discounted", cfg) + ["special"] * special
    kinds += ["plain"] * (n - len(kinds))
    rng.shuffle(kinds)
    slots = []
    plates = inputs.value("erp.vehicle.plates", cfg)
    for i, kind in enumerate(kinds):
        day = mine[i * len(mine) // n]
        slots.append({"at": plan.moment(b, rng, "west", day), "kind": kind, "day": day})
    specials_on_walkin = 0
    for p in sorted(slots, key=lambda p: p["at"]):
        if p["kind"] == "discount" or p["kind"] == "special" and (cfg == "en" or specials_on_walkin < 14):
            specials_on_walkin += p["kind"] == "special"
            how = customers.weighted(rng, plates["formats"] if cfg == "en" else plates["region_by_shop"]["west"])
            p["customer"] = b.walkin
            p["vehicle"] = customers.car(b, b.walkin, "west", streams.stream(b.seed, "s2 walk-in car", p["at"]),
                                         streams.stream(b.seed, "s2 walk-in car words", p["at"]), how)
        else:
            p["customer"], cars = streams.pick(rng, b.pools["west"])
            p["vehicle"] = streams.pick(rng, cars)
        p["tech"] = mechanic(b, "west", p["day"], rng)

    def draw(p, ok=lambda labor, gross, total: total > 0):  # a cash order has something to pay (a free test takes no payment row)
        while True:
            jobs = jobs_for(b, rng, "west", p["day"], p["vehicle"], p["tech"])
            got = priced(b, "west", p["day"], p["customer"], p["vehicle"], jobs)
            if ok(*got):
                return jobs, got

    # the discounted: orders whose labour covers 30 % of the bill, drawn so that the bills come to about the total
    # over the mean share; the shares drawn inside 15 to 30 % and moved by a constant and a term in the bill so that
    # their mean is 22.5 % and the discounts come to the total, to the cent on the largest bill
    discounted = [p for p in slots if p["kind"] == "discount"]
    target, mean = Decimal(str(inputs.value("s2.f1.discount_total", cfg))), Decimal("0.225")
    lo, hi = Decimal("0.151"), Decimal("0.299")  # inside 15 to 30 % once the amounts are rounded to the cent
    left = target / mean
    for k, p in enumerate(discounted):
        goal = left / (len(discounted) - k)
        tries = [draw(p, lambda labor, gross, total: labor >= hi * gross > 0) for _ in range(8)]
        p["jobs"], (p["labor"], p["gross"], _) = min(tries, key=lambda t: abs(t[1][1] - goal))
        left -= p["gross"]
    shares = [lo + (hi - lo) * Decimal(str(rng.random())) for _ in discounted]
    for _ in range(30):
        free = [i for i, x in enumerate(shares) if lo < x < hi]
        g = [discounted[i]["gross"] for i in free]
        if len(set(g)) < 2:  # no two bills left to move against each other: the largest bill takes the rest below
            break
        g_mean = sum(g) / len(g)
        alpha = (mean * len(shares) - sum(shares)) / len(free)
        beta = (target - sum(x * p["gross"] for x, p in zip(shares, discounted)) - alpha * sum(g)) / sum((x - g_mean) * x for x in g)
        for i, x in zip(free, g):
            shares[i] = min(max(shares[i] + alpha + beta * (x - g_mean), lo), hi)
        if all(lo < shares[i] < hi for i in free):
            break
    amounts = [(x * p["gross"]).quantize(orders.CENT, orders.ROUND_HALF_UP) for x, p in zip(shares, discounted)]
    biggest = max(range(len(discounted)), key=lambda i: discounted[i]["gross"])
    amounts[biggest] += target - sum(amounts)
    for p, amount in zip(discounted, amounts):
        p["discount"] = (amount / p["gross"], "regular customer" if cfg == "en" else "постоянный клиент", None)

    specials = [p for p in slots if p["kind"] == "special"]
    if cfg == "en":
        # the voids: totals summing to s2.f1.second's total and bills before tax to s2.amounts_basis's figure, both to the
        # cent; all but the last two drawn near the mean, the last two found among drawn pairs
        target = Decimal(str(second["total"]))
        before = Decimal(re.search(r"\(([\d,]+\.\d\d) before tax\)", inputs.value("s2.amounts_basis", "en")["voids_5600"])[1].replace(",", ""))
        for _ in range(500):
            for p in specials[:-2]:
                p["jobs"], (_, p["gross"], p["total"]) = draw(p, lambda labor, gross, total: target / 14 * Decimal("0.6") <= total <= target / 14 * Decimal("1.4"))
            rest = (before - sum(p["gross"] for p in specials[:-2]), target - sum(p["total"] for p in specials[:-2]))
            last = {}
            for _ in range(200):
                jobs, (_, gross, total) = draw(specials[-2])
                last.setdefault((gross, total), jobs)
            pair = None
            for _ in range(200):
                jobs, (_, gross, total) = draw(specials[-1])
                if (rest[0] - gross, rest[1] - total) in last:
                    pair = (last[rest[0] - gross, rest[1] - total], jobs)
                    break
            if pair:
                specials[-2]["jobs"], specials[-1]["jobs"] = pair
                break
        else:
            raise ValueError("S02: no set of voids meets s2.f1.second and s2.amounts_basis")
    else:
        # the unbilled work: on each order the mechanics clock 1.5 to 4 hours (dealt) over the hours sold, the extra on its
        # lead job, all of them coming to exactly s2.f1.third's hours. Every job's clock runs a multiple of 3 minutes, so
        # each entry reads as a whole hundredth of an hour (s2.total sums the hours at the hour's rate to the rouble),
        # and the sold minutes of the 22 orders add up to a whole multiple of 3
        while True:
            for p in specials:
                p["jobs"], _ = draw(p, lambda labor, gross, total: labor > 0)
            sold = [60 * sum(j["labor"]["hours"] for j in p["jobs"] if j["labor"]) for p in specials]
            if sum(sold) % 3 == 0:
                break
        over = [Decimal(str(1.5 + 2.5 * rng.random())) for _ in specials]
        over = [x * third["hours"] / sum(over) for x in over]
        for k, (p, s, o) in enumerate(zip(specials, sold, over)):
            p["clocked"] = 3 * round((o * 60 + s) / 3) if k < len(specials) - 1 else int(third["hours"] * 60 + sum(sold) - sum(q["clocked"] for q in specials[:-1]))
            worked = [j for j in p["jobs"] if j["labor"] and j["key"] != "courtesy_inspection"]
            for j in worked[1:]:
                j["clocked"] = max(3, 3 * round(orders.clocked(b, j) / 3))
            worked[0]["clocked"] = p["clocked"] - sum(j["clocked"] for j in worked[1:])

    for p in slots:
        if "jobs" not in p:
            p["jobs"], _ = draw(p)
        if p["customer"] is b.walkin:
            p["vehicle"] = b.add("vehicle", **p["vehicle"])
        ro = orders.order(b, "west", p["at"], p["customer"], p["vehicle"], "F1", p["jobs"], pay="cash", discount=p.get("discount"),
                          complaint=plan.JOBS[p["jobs"][0]["key"]][cfg]["name"])
        if cfg == "en" and p["kind"] == "special":
            b.orders[id(ro)]["planted"] = "s2.void"

    if cfg == "ru":
        issues(b, rng, mine, second)

    # after the rule: slot 23's two of 12 % with no approver on a['s2_discounts'], and two approved by slot 22 on days
    # drawn after the rule, 10 to under 15 % as the background discounts
    open_days = [d for d in days(a["rule_on"], a["T"].date() - dt.timedelta(14)) if orders.advisors(b, "west", d)]  # paid by T (S2.3)
    after = [(d, "23", Decimal(inputs.value("s2.west.discounts_after", cfg)["unapproved_pct_each"]) / 100, None) for d in a["s2_discounts"]]
    after += [(d, streams.pick(rng, orders.advisors(b, "west", d)), Decimal(str(0.10 + 0.05 * rng.random())), b.people["22"]) for d in rng.sample(open_days, 2)]
    for day, advisor, share, approver in after:
        customer, cars = streams.pick(rng, b.pools["west"])
        p = {"day": day, "customer": customer, "vehicle": streams.pick(rng, cars), "tech": mechanic(b, "west", day, rng)}
        jobs, _ = draw(p, lambda labor, gross, total: labor >= share * gross > 0)
        orders.order(b, "west", plan.moment(b, rng, "west", day), customer, p["vehicle"], advisor, jobs, pay="cash",
                     discount=(share, streams.pick(rng, texts["background_discount_reasons"]), approver), complaint=plan.JOBS[jobs[0]["key"]][cfg]["name"])


def issues(b, rng, mine, second):
    """ru second way: s2.f1.second's count of stock issues at west under F1 with no order line, spread over his days,
    parts of the stocked jobs (erp.stock.stocked_jobs) at their cost on the day, 1 to 4 units, summing at cost to its
    total; all but the last two drawn, the last two found among the possible ones."""
    parts = []
    for part in (b.parts[o["brand"], o["part_number"] or s["name"], "car"] for k in orders.STOCKED for s in orders.JOBS[k]["ru"]["parts"] for o in s["options"]):
        if not any(part is q for q in parts):
            parts.append(part)
    when = [mine[i * len(mine) // second["count"]] for i in range(second["count"])]
    target = Decimal(str(second["total"]))

    def options(day):
        return {orders.drifted(b, p["cost"], day) * q: (p, q) for p in parts for q in range(1, 5)}
    for _ in range(500):
        drawn = [(streams.pick(rng, parts), rng.randint(1, 4)) for _ in when[:-2]]
        rest = target - sum(orders.drifted(b, p["cost"], d) * q for (p, q), d in zip(drawn, when))
        last, first = options(when[-1]), options(when[-2])
        hit = next((v for v in sorted(first) if rest - v in last), None)
        if hit is not None:
            drawn += [first[hit], last[rest - hit]]
            break
    else:
        raise ValueError("S02: no set of stock issues sums to s2.f1.second")
    for (part, q), day in zip(drawn, when):
        open_, close_ = orders.hours(b, "west", day)
        b.add("stock_movement", location_id=b.shops["west"], part_id=part, kind="issue", quantity=Decimal(-q), unit_cost=orders.drifted(b, part["cost"], day),
              moved_at=open_ + rng.randrange(int((close_ - open_) / MINUTE)) * MINUTE, employee_id=b.people["F1"])


def s4(b):
    """S04, call 7 (nf.call.07): an account's order approved by its driver over s4.driver_limit, on the call's day at
    main, by slot 6 who took the call. The found work is raised from the courtesy inspection and approved by phone at
    the call, `authorized_by` the driver. en: A3's MB-6, oil service and a right front CV axle, slot 12, done by 16:00;
    ru: A1's car № 12, fleet ТО at the company price, the ball joint and brake fluid found, the alignment added on the
    call (the ball joint at the call file's 3,766.10), each by a mechanic of its own so the car is ready by 18:00. Billed
    on the account's statement (the accounts track); the check-in hour drawn by the background's rule, before the
    inspection's hour (en: in the morning)."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "s4")
    call = inputs.STORY_FILES["calls", cfg][7]["call"]
    day = a["calls"][7]["day"]
    decided = at(day, call["local_start"])
    acct, unit, driver = ("A3", "MB-6", "Ronnie Eaves (driver)") if cfg == "en" else ("A1", "12", "Фёдор")
    customer, car = b.accounts[acct], b.fleets[acct][unit]
    opened = plan.moment(b, rng, "main", day)
    while opened + 60 * MINUTE > decided or cfg == "en" and opened.time() >= dt.time(12):  # en: dropped off "this morning"
        opened = plan.moment(b, rng, "main", day)
    crew = [r for _, r in orders.mechanics(b, "main", day)]
    rng.shuffle(crew)
    if cfg == "en":
        tech = b.people["12"]
        jobs = [{"key": "oil_service", "status": "approved", "tech": tech, "tier": "standard", "keep": True},
                {"key": "courtesy_inspection", "status": "approved", "tech": tech, "keep": True}]
        found = [("cv_axle", tech)]
    else:
        jobs = [{"key": "fleet_pm_van", "status": "approved", "tech": crew[0], "tier": "standard", "keep": True},
                {"key": "courtesy_inspection", "status": "approved", "tech": crew[0], "keep": True}]
        found = list(zip(("ball_joint", "brake_fluid_exchange"), crew[1:] + crew))
    for key, tech in found:
        jobs.append({"key": key, "status": "approved", "tech": tech, "tier": "standard", "keep": True, "found": "bad", "photo": True,
                     "reading": "3 % воды" if key == "brake_fluid_exchange" else orders.reading(cfg, key, "bad", rng), "method": "phone",
                     "decided": decided, "authorized_by": driver})
    if cfg == "ru":  # the alignment follows the ball joint: added on the call, no item of its own
        jobs.append({"key": "wheel_alignment", "status": "approved", "tech": crew[3 % len(crew)], "keep": True, "method": "phone", "decided": decided,
                     "authorized_by": driver})
    priced(b, "main", day, customer, car, jobs)
    if cfg == "ru":  # the call file's company price of the ball joint for a van (catalogue list x 1.3 x 0.9 before rounding)
        part = jobs[2]["parts"][0]
        part["unit_price"] = Decimal("3766.10") - jobs[2]["labor"]["amount"]
        jobs[2]["value"] = Decimal("3766.10")
    orders.order(b, "main", opened, customer, car, "6", jobs, pay=None, complaint=None)
    named = jobs[2]  # the found part named by its side, as the call names it
    named["item_row"]["component"] = f"{orders.GROUPS[cfg][orders.group(named['key'])]}: " + ("right front CV axle" if cfg == "en" else "левая шаровая опора")


def s5(b):
    """S05, the diagnostician's leave (s5.leave): orders_sent_to_east diagnostic orders opened at east in the leave weeks
    for customers of main's pool, the lead a diagnostic job, done by another mechanic than slot 18 (the background gives
    him his two diagnostic jobs a day: spec section 4.2), paid by a method of pay.mix's counter shares (the background
    deals the month's mix around them). Slot 16's en days off are `orders.advisors`' (s5.days_off_so_far)."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "s5")
    leave = [d for d in days(a["leave_from"], a["leave_to"] + clock.DAY) if orders.advisors(b, "east", d)]
    methods = {"card": "card", "cash": "cash", "fast payment (СБП)": "fast_payment"}  # a private customer: no cheque, no account
    mix = {methods[k]: v for k, v in inputs.value("pay.mix", cfg).items() if k in methods}
    for _ in range(inputs.value("s5.leave", cfg)["orders_sent_to_east"]):
        day = streams.pick(rng, leave)
        customer, cars = streams.pick(rng, b.pools["main"])
        car = streams.pick(rng, cars)
        jobs = jobs_for(b, rng, "east", day, car, streams.pick(rng, [r for s, r in orders.mechanics(b, "east", day) if s != "18"]), DIAGNOSTICS)
        ro = orders.order(b, "east", plan.moment(b, rng, "east", day), customer, car, streams.pick(rng, orders.advisors(b, "east", day)), jobs,
                          pay=customers.weighted(rng, mix), complaint=plan.JOBS[jobs[0]["key"]][cfg]["name"])
        b.orders[id(ro)]["planted"] = True  # a comeback would be a twelfth such order (section 7, S5.3)


def s7(b):
    """S07: booked on day A by slot 6 from the web chat (booked at the confirming call's hour), the visit at its hour
    with slot 6 and slot 12; the brake inspection approved at the counter; front pads and rotors and the rear shocks
    found bad and decided by message at slot 6's reply in the chat (conversation 02), the pads approved, the right rear
    shock seeping and declined, so deferred; paid by card at s7.thread's hour. The reminder is the reminders step's."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "s7")
    thread, x = inputs.value("s7.thread", cfg), customers.NAMED[cfg]["S7"]
    customer, (car,) = b.named["S7"]
    visit = at(a["s7_visit"], thread["visit"])
    crew = [s for s, _ in orders.mechanics(b, "main", a["s7_visit"]) if s != "F4"]  # slot 12, or on his day off (ru rota) the first on duty
    tech = b.people["12" if "12" in crew else crew[0]]
    chat = a["conversations"][2]["days"]
    reply = next(m for m in inputs.STORY_FILES["conversations", cfg][2]["conversations"][0]["timeline"]  # slot 6's reply in the chat
                 if m["kind"] == "message" and m["from"] == "staff" and chat[m["day"]] == a["s7_visit"])
    decided = at(a["s7_visit"], reply["at"])
    shocks = ("seeping", "right rear shock absorber") if cfg == "en" else ("запотел", "задний правый амортизатор")
    jobs = [{"key": "brake_inspection", "status": "approved", "tech": tech, "keep": True},
            {"key": "front_pads_rotors", "status": "approved", "tech": tech, "tier": "standard", "keep": True, "found": "bad", "photo": True,
             "reading": orders.reading(cfg, "front_pads_rotors", "bad", rng), "method": "message", "decided": decided},
            {"key": "rear_shocks_pair", "status": "declined", "tech": tech, "tier": "standard", "found": "bad", "reading": shocks[0],
             "method": "message", "decided": decided}]
    booking = {"source": "web_chat", "booked_at": at(a["s7_day_a"], thread["confirming_call"].split(" ")[0]), "booked_by": "6", "starts_at": visit,
               "duration": 30}
    ro = orders.order(b, "main", visit, customer, car, "6", jobs, pay=None, booking=booking, complaint=plan.JOBS["brake_inspection"][cfg]["name"])
    jobs[2]["item_row"]["component"] = f"{orders.GROUPS[cfg][orders.group('rear_shocks_pair')]}: {shocks[1]}"
    b.orders[id(ro)]["planted"] = True
    paid = at(a["s7_visit"], thread["paid"])
    orders.status(b, ro, "paid", paid)
    b.add("payment", repair_order_id=ro, kind="payment", method="card", amount=ro["total"], received_at=paid, taken_by_id=b.people["6"],
          reference=f"{rng.randrange(10 ** 6):06d}")
    ro["mileage_in"] = x["car"]["mileage_at_first_visit_miles" if cfg == "en" else "mileage_at_first_visit_km"]
    ro["mileage_out"] = ro["mileage_in"] + rng.randint(0, 15)


def s8(b):
    """S08: the estimate opened at the quote call (call 9) by slot 7, the timing belt approved by phone at the call at
    s8.price_quoted, its lines at today's list; the booking for the car-in day at 08:00, promised that day. The car goes
    on the lift after lunch, too late for the job to fit the shift (13:00, or later by as much): its first clock entry
    runs to the shift's end and the rest the next morning; completed and invoiced on the ready day, unpaid. The discount s8.discount approved by slot 4 is on the
    order from the start; `close` re-issues the bill and takes the payment."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "s8")
    x, breakdown = customers.NAMED[cfg]["S8"], inputs.value("s8.breakdown", cfg)
    customer, (car,) = b.named["S8"]
    quote = at(a["s8_quote"], inputs.STORY_FILES["calls", cfg][9]["call"]["local_start"])
    car_in = a["s8_car_in"]
    # slot 12 does it; when the card's car-in or ready day is a day off of his (ru: rota days), or he works a day between
    # them (en: main's Saturday crews), the first of main's mechanics on duty on both and on none between, so the car is
    # ready on the card's day
    between = [car_in + clock.DAY * k for k in range(1, (a["s8_ready"] - car_in).days)]
    both = [s for s, _ in orders.mechanics(b, "main", car_in) if s != "F4" and s in dict(orders.mechanics(b, "main", a["s8_ready"]))
            and not any(s in dict(orders.mechanics(b, "main", d)) for d in between)]
    job = {"key": "timing_belt_kit", "status": "approved", "tech": b.people["12" if "12" in both else both[0]], "tier": "standard", "keep": True, "decided": quote, "method": "phone",
           "split": True}
    priced(b, "main", car_in, customer, car, [job])
    for part, amount in zip(job["parts"], (breakdown["kit"], breakdown["coolant"])):  # s8.breakdown's amounts, as the story carries them
        part["unit_price"] = Decimal(str(amount)) / part["quantity"]
    labor, parts, sublet, fees, _ = orders.bill(b, [job])
    gross = labor + parts + sublet + fees
    job["value"] = labor + parts
    end = orders.shift(b, "main", car_in)[1]
    start = max(at(car_in, "13:00"), end - orders.clocked(b, job) * MINUTE + 30 * MINUTE)
    booking = {"source": "phone", "booked_at": quote, "booked_by": "7", "starts_at": at(car_in, "08:00"),
               "duration": -(-int(job["labor"]["hours"] * 60) // 30) * 30}
    ro = orders.order(b, "main", quote, customer, car, "7", [job], pay=None, booking=booking, start=start,
                      discount=(Decimal(str(inputs.value("s8.discount", cfg))) / gross, orders.TEXTS[cfg]["s8_discount_reason"], b.people["4"]),
                      complaint=plan.JOBS["timing_belt_kit"][cfg]["name"])
    job["row"]["approved_amount"] = Decimal(str(inputs.value("s8.price_quoted", cfg)))
    record = b.orders[id(ro)]
    record["planted"] = "s8"
    ro["promised_at"] = dt.datetime.combine(car_in, orders.PROMISE[cfg])
    ro["mileage_in"] = x["car"]["mileage_at_visit_miles" if cfg == "en" else "mileage_at_visit_km"]
    ro["mileage_out"] = ro["mileage_in"] + rng.randint(0, 15)


FLORIST = {"en": "Dogwood Lane Florals", "ru": "ИП Абрамова"}  # board.second_look_open's small business, its van the card's


def second_look(b):
    """Slot 8's open second look (board.second_look_open, card F-recheck-open): the small business's van gets rear pads
    by slot 14 at main a few days before slot 5 writes the card on his last working day before T (the generator's
    choice: slot 14's third working day before it); on the card's due day, slot 8's next working day, a warranty order
    at opening pointing at it, the job redone at its prices, approved at T, its work after T. When the due day is after
    T only an appointment at opening on that day exists (booked when the card was written, by phone)."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "second look")
    customer, (van,) = next((c, cars) for c, cars in b.small if c["name"].startswith(FLORIST[cfg]))
    card = a["s4_nightly"] - clock.DAY  # slot 5's last working day before T
    due = card + clock.DAY
    while not (clock.full_open(cfg, due) and due.weekday() < 5):  # slot 8 works the weekdays (roster.manager_pattern)
        due += clock.DAY
    day, n = card, 0
    while n < 3:
        day -= clock.DAY
        n += any(s == "14" for s, _ in orders.mechanics(b, "main", day))
    tech = b.people["14"]
    job = {"key": "rear_brake_pads", "status": "approved", "tech": tech, "tier": "standard", "keep": True}
    first = orders.order(b, "main", plan.moment(b, rng, "main", day), customer, van, streams.pick(rng, orders.advisors(b, "main", day)), [job],
                         pay="card" if cfg == "en" else "fast_payment", complaint=plan.JOBS["rear_brake_pads"][cfg]["name"])
    opening = orders.hours(b, "main", due)[0]
    if opening <= a["T"]:
        orders.order(b, "main", opening, customer, van, streams.pick(rng, orders.advisors(b, "main", due)),
                     [{"key": "rear_brake_pads", "status": "approved", "tech": tech, "tier": "standard", "keep": True}],
                     kind="warranty", comeback_of=first, pay=None, start=a["T"] + MINUTE)
    else:
        b.add("appointment", location_id=b.shops["main"], customer_id=customer, vehicle_id=van, starts_at=opening, duration_min=60, source="phone",
              status="confirmed" if opening - a["T"] <= dt.timedelta(2) else "booked", reason=plan.JOBS["rear_brake_pads"][cfg]["name"],
              booked_at=orders.hours(b, "main", card)[1] - 90 * MINUTE, booked_by_id=b.people["5"])
