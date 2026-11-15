"""Sections 4.1 to 4.3 of generator-spec.md, the day plan: every shop's open days filled to their count around the
orders already in `b.orders` (planted, account and story orders, placed first), each background order with its advisor,
customer, car (`plan`) and jobs (`content`), every rate dealt over all orders of its population, those already there
included. `background.fill` gives the plans their mechanics, comebacks, bookings and money and writes them."""
import collections
import datetime as dt
import functools
import math

from seeder import clock, inputs, streams
from seeder.erp import customers, orders

SITES = ("main", "east", "west")
MIX = inputs.load("mix.json")["configurations"]
JOBS = orders.JOBS
ENGINES = {cfg: {e["engine"]: e["timing"] for m in customers.PARC[cfg]["models"] for e in m["engines"]} for cfg in ("en", "ru")}
PRICED = [k for k in JOBS if JOBS[k]["en"]["counts_as_priced_job"]]


def _shares(cfg):
    """Spec section 4.3: each job's share of orders as lead, sold raised and customer add-on, adding up to
    share_of_orders.total. A job whose lead share leaves its recommended share no room sells raised what its addon
    leaves (total - lead) and is never a customer add-on; what it loses goes to the other jobs' sold raised share in
    proportion to their customer add-on share, which shrinks by as much (among the jobs that are ever recommended: spec
    4.3 says check_engine_diag is never raised)."""
    out, lost = {}, 0.0
    for k in PRICED:
        s, rec = JOBS[k][cfg]["share_of_orders"], JOBS[k][cfg]["recommended_share"]
        sold, addon = s["total"] * rec, s["addon"] - s["total"] * rec
        if addon < 0:
            lost += sold - (s["total"] - s["lead"])
            sold, addon = s["total"] - s["lead"], 0.0
        out[k] = {"lead": s["lead"], "sold": sold, "addon": addon}
    takers = {k: x for k, x in out.items() if JOBS[k][cfg]["recommended_share"]}  # a job never recommended is never raised (check_engine_diag)
    room = sum(x["addon"] for x in takers.values())
    for x in takers.values():
        moved = lost * x["addon"] / room
        x["sold"] += moved
        x["addon"] -= moved
    return out


SHARES = {cfg: _shares(cfg) for cfg in ("en", "ru")}


def slot_key(slot, kind):
    """A person's ledger key: p05, p29, pF1."""
    return f"p{slot.zfill(2) if slot.isdigit() else slot}.{kind}"


def half_uniform(rng, row):
    """A draw from a {min, median, max} row: half the cases below the median, half above, uniform in each half (spec
    section 7b)."""
    lo, mid, hi = row["min"], row["median"], row["max"]
    return rng.randint(lo, mid) if rng.random() < 0.5 else rng.randint(mid, hi)


def deal(seed, key, n, weights):
    """n labels in the exact proportions of `weights`, shuffled (customers.deal); none for nothing to deal."""
    if n <= 0 or not sum(weights.values()):
        return []
    return customers.deal(streams.stream(seed, "deal", *key), n, weights)


def month_of(p):
    return p["site"], p["day"].year, p["day"].month


def by(groups_of, items):
    out = collections.defaultdict(list)
    for x in items:
        out[groups_of(x)].append(x)
    return out


def shares(b, site, day, f1=None):
    """The order shares of the advisors in post at `site` on `day` (spec section 4.2): F1 and F3 keep their own share
    while they worked (F1's `f1` where S02 sets it); the others split the rest in proportion to their pNN.order_share."""
    on = [s for s in orders.ADVISORS[site] if orders.in_post(b.people[s], day)]
    fixed = {s: f1 if s == "F1" and f1 else inputs.value(slot_key(s, "order_share"), b.cfg) for s in on if s in ("F1", "F3")}
    rest = {s: inputs.value(slot_key(s, "order_share"), b.cfg) for s in on if s not in fixed}
    return fixed | {s: (100 - sum(fixed.values())) * v / sum(rest.values()) for s, v in rest.items()}


def curve(cfg, key, day):
    """mix.json seasonal: the index of a job on `day` (its job curve, else its category's; ru seasonal tyres by date)."""
    s = MIX[cfg]["seasonal"]
    c = s["curves"][s["job_curve"].get(key) or s["category_curve"][JOBS[key]["category"]]]
    if "by_month" in c:
        return c["by_month"][day.month - 1]
    mmdd = f"{day.month:02d}-{day.day:02d}"
    return next((w["index"] for w in c["windows"] if w["from"] <= mmdd <= w["to"]), c["base"])


@functools.lru_cache(maxsize=None)
def month_curve(cfg, key, year, month):
    """A job's seasonal index over a calendar month (the mean of its days)."""
    days = [dt.date(year, month, 1) + dt.timedelta(i) for i in range(31) if (dt.date(year, month, 1) + dt.timedelta(i)).month == month]
    return sum(curve(cfg, key, d) for d in days) / len(days)


@functools.lru_cache(maxsize=None)
def _offered(cfg, key, cls, engine):
    by_class = JOBS[key][cfg]["hours_by_class"]
    return not (by_class and by_class.get(cls) is None) and (key != "timing_belt_kit" or ENGINES[cfg].get(engine, "belt") == "belt")


def allowed(b, p, key):
    """A job this order can carry (spec sections 4.2, 4.3 and 4.5): offered for the car's class and engine; none of the
    diagnostics on en main's Saturday; no work sent to a subcontractor on an order of the two weeks before T's day, which
    it would still hold open at T."""
    x = JOBS[key]
    if not _offered(b.cfg, key, p["vehicle"]["vehicle_class"], p["vehicle"]["engine"]):
        return False
    if b.cfg == "en" and p["site"] == "main" and p["day"].weekday() == 5 and x["category"] == "diagnostics":
        return False
    if x[b.cfg]["usually_sublet"] and any(JOBS[j["key"]][b.cfg]["usually_sublet"] for j in p.get("jobs", ()) if j["key"] != key):
        return False  # one subcontractor's job an order: the car is away while it is done
    return not (x[b.cfg]["usually_sublet"] and 0 < (b.a["T"].date() - p["day"]).days <= 14)


def site_of(b, row):
    return next(s for s, r in b.shops.items() if r is row)


def view(b, o):
    """An order already in the tables, read as a plan for the counts: its shop, day, advisor, kind, jobs and mechanic."""
    ro = o["order"]
    c = ro["customer_id"]
    hours = collections.Counter()
    for j in o["jobs"]:
        if j["status"] == "approved" and j.get("labor") and j.get("tech") and j["key"] != "courtesy_inspection":
            hours[orders.slot_of(b, j["tech"])] += j["labor"]["hours"]
    kind = (ro["status"] if ro["status"] in ("declined", "void") else "comeback" if ro["comeback_of_id"] else "account" if c.get("payment_terms_days")
            else "small" if any(c is x for x, _ in b.small) else "walkin" if c is b.walkin else "private")
    return {"site": site_of(b, ro["location_id"]), "day": ro["opened_at"].date(), "at": ro["opened_at"], "advisor": orders.slot_of(b, ro["advisor_id"]),
            "kind": kind, "visit": kind not in ("declined", "void"), "jobs": o["jobs"], "vehicle": ro["vehicle_id"], "customer": c, "fixed": True,
            "order": ro, "record": o, "pay": (o["payments"] or [{}])[-1].get("method"), "tech": max(sorted(hours), key=hours.get) if hours else None}


def block(b, day):
    """The 30-day block counted back from T that holds `day` (0 = the last 30 days)."""
    return (b.a["T"].date() - day).days // 30


def window(b, p):
    """The group a person's dealt rate is counted in: the 90 days before T, as the pNN rows read them (W90), else the
    order's 30-day block."""
    return -1 if p["at"] > b.a["T"] - dt.timedelta(90) else block(b, p["day"])


def moment(b, rng, site, day):
    """A check-in time on `day` by mix.json hour_of_day, inside the shop's hours (en main's Saturday: the last car by
    11:30, kb.schedule.diagnostics_and_weekends), the minute uniform. On the last open day before T's day the last car
    comes four hours before the mechanics' shift ends, so that its order closes by T (spec section 4.5)."""
    bins = sorted((tuple(map(int, k.split(":"))), v) for k, v in MIX[b.cfg]["hour_of_day"]["share_of_arrivals"].items())
    open_, close = orders.hours(b, site, day)
    if b.cfg == "en" and day.weekday() == 5:
        close = dt.datetime.combine(day, dt.time(11, 30))
    if day < b.a["T"].date() and orders.opening(b, site, close).date() >= b.a["T"].date():
        close = min(close, orders.shift(b, site, day)[1] - dt.timedelta(hours=4))
    spans = {}
    for n, ((h, m), share) in enumerate(bins):
        lo = dt.datetime.combine(day, dt.time(h, m))
        hi = dt.datetime.combine(day, dt.time(*bins[n + 1][0])) if n + 1 < len(bins) else close
        lo, hi = max(lo, open_), min(hi, close)
        if hi > lo:
            spans[(lo, hi)] = share * (hi - lo) / dt.timedelta(hours=1)
    lo, hi = customers.weighted(rng, spans)
    return lo + dt.timedelta(minutes=rng.randrange(int((hi - lo).total_seconds() // 60)))


def plan(b):
    """The background visits, declined estimates and voids of every shop and day with their advisor, customer and car
    (spec section 4.1, 4.2 and the rates of 4.5 and 4.7 they carry). Returns them, the day counts, each shop's known
    customers (by created_at) and the orders already there, read as plans."""
    cfg, a, seed = b.cfg, b.a, b.seed
    T = a["T"]
    fixed = [view(b, o) for o in b.orders.values()]

    # 4.1: every open day's count by the day's seasonal index (the lead shares x each job's curve on that day; its
    # monthly mean is season.total, and inside ru's tyre windows it stands at season.tyre.orders_in_window), dealt so
    # each month's sum matches; ru also by the advisors on duty (their days carry their order share:
    # s5.rec_jobs_on_days_off), averaged over the shop's own days
    weekday_index = MIX[cfg]["weekday"]["index"]
    lead = {k: j[cfg]["share_of_orders"]["lead"] for k, j in JOBS.items() if j[cfg]["share_of_orders"]["lead"]}

    def base(site, d):
        if cfg == "en" and d.weekday() == 5:
            return inputs.value("volume.saturday_orders.main", cfg)
        return (inputs.value(f"volume.orders_per_day.{site}", cfg) * sum(share * curve(cfg, k, d) for k, share in lead.items())
                * weekday_index[clock.WEEKDAYS[d.weekday()][:3].lower()])

    # S05: main's counts on the leave's days are scaled so that its billed hours a week there stand s5.leave_drop_pct
    # under the mean week of the four weeks before (the orders already there as they are, the others at
    # volume.hours_per_order.main), and twelve per cent over that: `background.leave_hours` takes the hours to the row as
    # the statement reads them; the month's sum is lower, not made up on its other days
    def open_main(lo, hi):
        return [lo + dt.timedelta(i) for i in range((hi - lo).days + 1) if orders.hours(b, "main", lo + dt.timedelta(i))]

    def there_(days_):
        mine = [v for v in fixed if v["site"] == "main" and v["visit"] and v["day"] in days_]
        return len(mine), sum(float(j["labor"]["hours"]) for v in mine for j in v["jobs"] if j["status"] == "approved" and j.get("labor"))
    per_order = inputs.value("volume.hours_per_order.main", cfg)
    leave_days, before_days = open_main(a["leave_from"], a["leave_to"]), open_main(a["leave_from"] - dt.timedelta(28), a["leave_from"] - clock.DAY)
    (n_before, h_before), (n_leave, h_leave) = there_(before_days), there_(leave_days)
    want = 2 * (1 - inputs.value("s5.leave_drop_pct", cfg) / 100) * (h_before + (sum(base("main", d) for d in before_days) - n_before) * per_order) / 4
    leave_scale = 1.12 * ((want - h_leave) / per_order + n_leave) / sum(base("main", d) for d in leave_days)
    # S02: F1 writes s2.f1.orders visits in his 26 weeks (the ledger's figure is a month's orders x six x his share), so
    # there his share is that count over the shop's visits of those days (here from the days' expected counts, which ru
    # weights by the advisors on duty; the advisors' quotas below take it from the counts dealt)
    window = [d for d in (a["s2_start"] + dt.timedelta(i) for i in range((a["fired"] - a["s2_start"]).days)) if orders.hours(b, "west", d)]
    f1 = 100 * inputs.value("s2.f1.orders", cfg) / sum(base("west", d) for d in window)
    counts, plans = {}, []
    for site in SITES:
        first = a["bought"] if site == "west" else a["history_start"]
        month = dt.date(first.year, first.month, 1)
        while month <= T.date() + dt.timedelta(10):
            days = [month + dt.timedelta(i) for i in range(31) if (month + dt.timedelta(i)).month == month.month and orders.hours(b, site, month + dt.timedelta(i))]
            exact = {d: base(site, d) for d in days}
            if cfg == "ru":
                duty = {d: sum(shares(b, site, d, f1 if a["s2_start"] <= d < a["fired"] else None).get(s, 0) for s in orders.advisors(b, site, d))
                        for d in days if d >= first}
                mean = sum(duty.values()) / len(duty)
                exact = {d: x * duty[d] / mean if d in duty else x for d, x in exact.items()}
            if site == "main":
                exact = {d: x * leave_scale if d in leave_days else x for d, x in exact.items()}
            target, floors = round(sum(exact.values())), {d: int(x) for d, x in exact.items()}
            for d in sorted(days, key=lambda d: (int(exact[d]) - exact[d], d))[:target - sum(floors.values())]:
                floors[d] += 1
            counts.update({(site, d): n for d, n in floors.items() if d >= first})
            month = (month + dt.timedelta(32)).replace(day=1)
    there = collections.Counter((v["site"], v["day"]) for v in fixed if v["visit"])
    for (site, day), n in sorted(counts.items(), key=lambda x: (SITES.index(x[0][0]), x[0][1])):
        if day > T.date():
            continue
        rng = streams.day_stream(seed, site, day, "slots")
        floor = dt.datetime.combine(day, dt.time(9)) if site == "west" and day == a["bought"] else dt.datetime.min  # after the bulk load (M11)
        times = sorted(max(moment(b, rng, site, day), floor) for _ in range(max(0, n - there[site, day])))
        plans += [{"site": site, "day": day, "at": t, "kind": "private", "i": i, "visit": True} for i, t in enumerate(times) if t <= orders.until(b, site)]

    # 4.2: advisors, dealt per shop and 30-day block over every order of the block, each on a day he is on duty
    # S02: F1's visits in his 26 weeks are the middle of what s2.f1.orders (within the 3 % of its statement: the row
    # carries no tolerance) and pF1.order_share (his share of the shop's visits there) allow together
    visits = sum(counts["west", d] for d in window)
    want, share_row = inputs.value("s2.f1.orders", cfg), inputs.ROWS["pF1.order_share"]
    lo = max(want * 0.97, (inputs.value("pF1.order_share", cfg) - share_row["tolerance"]) * visits / 100)
    hi = min(want * 1.03, (inputs.value("pF1.order_share", cfg) + share_row["tolerance"]) * visits / 100)
    f1 = 100 * (lo + hi) / 2 / visits
    old_advisor = collections.Counter((v["site"], block(b, v["day"]), v["advisor"]) for v in fixed if v["visit"])
    for (site, k), group in by(lambda p: (p["site"], block(b, p["day"])), plans).items():
        days = sorted({p["day"] for p in group})
        per_day = collections.Counter(p["day"] for p in group)
        exact = collections.Counter()
        for d in days:
            for s, share in shares(b, site, d, f1 if a["s2_start"] <= d < a["fired"] else None).items():
                exact[s] += (per_day[d] + there[site, d]) * share / 100
        on_duty = {d: orders.advisors(b, site, d) for d in days}
        capacity = collections.Counter(s for p in group for s in on_duty[p["day"]])
        # whole quotas by the largest remainder, so they add up to the block's orders; one who cannot take his (slot 29,
        # on duty a few days) leaves the rest to the others in proportion to theirs, while they have the days for it
        quota = {s: max(0, x - old_advisor[site, k, s]) for s, x in exact.items() if capacity[s]}
        while True:
            over = {s: q - capacity[s] for s, q in quota.items() if q > capacity[s]}
            free = {s: q for s, q in quota.items() if q < capacity[s]}
            if not over or not free:
                break
            for s in over:
                quota[s] = capacity[s]
            for s in free:
                quota[s] += sum(over.values()) * free[s] / sum(free.values())
        total = sum(quota.values())
        quota = {s: q * len(group) / total for s, q in quota.items()}  # (the orders already there may have taken more than a share)
        whole = {s: math.floor(q) for s, q in quota.items()}
        for s in sorted(quota, key=lambda s: (whole[s] - quota[s], s))[:len(group) - sum(whole.values())]:
            whole[s] += 1
        got = collections.Counter()
        order_ = group[:]
        streams.stream(seed, "advisors", site, k).shuffle(order_)
        for p in order_:
            eligible = on_duty[p["day"]]
            p["advisor"] = max(eligible, key=lambda s: ((whole.get(s, 0) - got[s]) / capacity[s], -eligible.index(s)))
            got[p["advisor"]] += 1
            for s in eligible:
                capacity[s] -= 1
        # what the greedy pass leaves over or under its quota is moved, one order at a time, to someone on duty that day
        for _ in range(len(group)):
            over = [s for s in whole if got[s] > whole[s]]
            under = [s for s in whole if got[s] < whole[s]]
            move = next(((p, t) for p in order_ if p["advisor"] in over for t in under if t in on_duty[p["day"]]), None)
            if move is None:
                break
            got[move[0]["advisor"]] -= 1
            move[0]["advisor"] = move[1]
            got[move[1]] += 1

    # 4.5 and 4.7: declined estimates and voids, beyond the day's count; a declined estimate on the day and desk of a
    # visit of its month, dealt per shop and month at the private rate, half of them left to expire after
    # kb.estimate_validity_days (one that would expire after T is declined at check-in); voids dealt per advisor but F1
    declined_share = inputs.value("erp.estimate.declined_share", cfg)["private"] / 100
    validity = inputs.value("kb.estimate_validity_days", cfg)
    old_declined = collections.Counter(month_of(v) for v in fixed if v["kind"] == "declined" and v["customer"].get("payment_terms_days") is None)
    old_counter = collections.Counter(month_of(v) for v in fixed if v["visit"] and v["kind"] in ("private", "small", "walkin"))
    extra = []
    for key, group in by(month_of, plans).items():
        rng = streams.stream(seed, "declined", *key)
        n = max(0, round((len(group) + old_counter[key]) * declined_share / (1 - declined_share)) - old_declined[key])
        for expires in deal(seed, ("expiry", *key), n, {True: 1, False: 1}):
            host = streams.pick(rng, group)
            ends = orders.opening(b, host["site"], dt.datetime.combine(host["day"] + dt.timedelta(validity), dt.time()))
            extra.append({"site": host["site"], "day": host["day"], "at": moment(b, rng, host["site"], host["day"]), "kind": "declined", "visit": False,
                          "advisor": host["advisor"], "expires": validity if expires and ends <= orders.until(b, host["site"]) else None})
    void_rate = inputs.value("pay.void_rate", cfg) / 100
    old_voids = collections.Counter(v["advisor"] for v in fixed if v["kind"] == "void")
    old_mine = collections.Counter(v["advisor"] for v in fixed if v["visit"])
    for s, group in by(lambda p: p["advisor"], plans).items():
        if s == "F1":
            continue
        rng = streams.stream(seed, "voids", s)
        for _ in range(max(0, round((len(group) + old_mine[s]) * void_rate / (1 - void_rate)) - old_voids[s])):
            host = streams.pick(rng, group)
            extra.append({"site": host["site"], "day": host["day"], "at": moment(b, rng, host["site"], host["day"]), "kind": "void", "advisor": s,
                          "void": streams.pick(rng, orders.TEXTS[cfg]["void_reasons"]), "visit": False})
    extra = [p for p in extra if p["at"] <= orders.until(b, p["site"])]

    # who comes: the small businesses' share per shop and month, the walk-in record's orders per advisor (s2.walkin), the
    # rest private customers (spec section 3, customer; s2.walkin)
    old_kind = collections.Counter((*month_of(v), v["kind"]) for v in fixed if v["visit"])
    for key, group in by(month_of, plans).items():
        n = round((len(group) + sum(v for k, v in old_kind.items() if k[:3] == key)) * inputs.value("acct.small.orders_share", cfg) / 100) - old_kind[(*key, "small")]
        for p in streams.stream(seed, "small", *key).sample(group, max(0, min(n, len(group)))):
            p["kind"] = "small"
    old_walkin = collections.Counter(v["advisor"] for v in fixed if v["kind"] == "walkin")
    for s, n in inputs.value("s2.walkin", cfg)["by_advisor_at_full_size"].items():
        # (none on the last days before T, whose orders may not be placed when they cannot close by T)
        mine = [p for p in plans if p.get("advisor") == s and p["site"] == "west" and p["kind"] == "private" and (T.date() - p["day"]).days > 3]
        for p in streams.stream(seed, "walk-in", s).sample(mine, max(0, min(n - old_walkin[s], len(mine)))):
            p["kind"] = "walkin"

    # customers and cars, in time order per shop: a returning customer by erp.customer.returning_share (dealt per shop
    # and month), else a new one made at the counter 1 to 10 minutes before the order (spec section 3, customer)
    every = sorted(plans + extra, key=lambda p: (SITES.index(p["site"]), p["at"]))
    returning = inputs.value("erp.customer.returning_share", cfg)
    for key, group in by(month_of, [p for p in every if p["kind"] in ("private", "declined", "void")]).items():
        for p, flag in zip(group, deal(seed, ("returning", *key), len(group), {True: returning, False: 100 - returning})):
            p["returning"] = flag
    traits = {}
    plates = inputs.value("erp.vehicle.plates", cfg)
    mail_share, extra_car = inputs.value("erp.customer.email_share", cfg), inputs.value("erp.vehicle.per_private_customer", cfg) - 1
    for key, group in by(month_of, [p for p in every if p.get("returning") is False]).items():
        n = len(group)
        seconds = deal(seed, ("second car", *key), n, {True: extra_car, False: 1 - extra_car})
        hows = deal(seed, ("plate", *key), n + sum(seconds), plates["formats"] if cfg == "en" else plates["region_by_shop"][key[0]])
        mails = deal(seed, ("email", *key), n, {True: mail_share, False: 100 - mail_share})
        refs = deal(seed, ("referral", *key), n, inputs.value("erp.referral.mix", cfg))
        for p, second, mail, ref in zip(group, seconds, mails, refs):
            traits[id(p)] = (mail, ref, [hows.pop(), *([hows.pop()] if second else [])])
    walkin_hows = deal(seed, ("plate", "walk-in"), sum(p["kind"] == "walkin" for p in every), plates["formats"] if cfg == "en" else plates["region_by_shop"]["west"])
    known = {site: sorted(b.pools[site], key=lambda x: x[0]["created_at"]) for site in SITES}
    small_of = {site: [(c, cars) for c, cars in b.small if c["created_location_id"] is b.shops[site]] for site in SITES}
    seen = set()
    for p in every:
        site = p["site"]
        rng = streams.stream(seed, "customer", site, p["at"], p["kind"], p.get("i"))
        if p["kind"] == "small":
            c, cars = streams.pick(rng, small_of[site])
        elif p["kind"] == "walkin":
            c, cars = b.walkin, [b.add("vehicle", **customers.car(b, b.walkin, site, rng, streams.stream(seed, "walk-in car", p["at"]), walkin_hows.pop()))]
        elif p["returning"]:
            for _ in range(100):
                c, cars = streams.pick(rng, known[site])
                if c["created_at"] < p["at"] and (id(c), p["day"]) not in seen:
                    break
        else:
            mail, ref, hows = traits[id(p)]
            words = streams.stream(seed, "new customer words", site, p["at"], p["kind"], p.get("i"))
            name, user = customers.person(b, words)
            c = b.add("customer", kind="person", name=name, phone=customers.phone(b, site, words), email=customers.mail(b, user, words) if mail else None,
                      referral_source_id=b.referrals.get(ref), created_location_id=b.shops[site], created_at=p["at"] - rng.randint(1, 10) * orders.MINUTE)
            cars = [b.add("vehicle", **customers.car(b, c, site, rng, words, how)) for how in hows]
            known[site].append((c, cars))
        seen.add((id(c), p["day"]))
        p["customer"], p["vehicle"] = c, streams.pick(rng, cars)
    return every, counts, known, fixed


def assign(b, rng, wanted, labels, weight):
    """Puts job labels (a Counter of key to count) on orders: `wanted` holds (plan, how many); each takes keys it can
    carry and does not hold, by what is left of each label; when no label fits, a key by `weight(key, plan)` (a car the
    labels did not foresee)."""
    for p, n in wanted:
        for _ in range(n):
            taken = {j["key"] for j in p["jobs"]}
            fits = {k: c for k, c in labels.items() if c > 0 and k not in taken and allowed(b, p, k)}
            if not fits:
                fits = {k: weight(k, p) for k in PRICED if k not in taken and allowed(b, p, k) and weight(k, p) > 0}
            if not fits:
                break
            k = customers.weighted(rng, fits)
            labels[k] -= 1
            yield p, k


def content(b, every, fixed):
    """Spec section 4.3: the jobs of every plan. Per shop and month over its visits (those already there counted), each
    job's count is its share of orders x its seasonal index: leads by `lead` over the month's orders; sold raised and
    customer add-ons over the month's orders taken out of season (the month's count over its season index), so a job
    follows its own curve, not the month's volume. The courtesy inspection on share_of_orders.total of visits; orders
    with raised jobs at mix.orders_with_rec of the season-free base, 3 or 4 jobs each (spec section 7b), a bad or watch
    finding each; approvals at the advisor's pNN.sold_rec per 30-day block; priced jobs per order by mix.json
    jobs_per_order. Declined estimates carry the customer's own jobs, voids their lead."""
    cfg, seed = b.cfg, b.seed
    share = SHARES[cfg]
    courtesy = JOBS["courtesy_inspection"][cfg]["share_of_orders"]["total"]
    rec_mean = inputs.value("mix.rec_jobs_per_such_order", cfg)
    rec_share = inputs.value("mix.orders_with_rec", cfg) / 100
    weights = {kind: (lambda kind: lambda k, p: share[k][kind] * curve(cfg, k, p["day"]))(kind) for kind in ("lead", "sold", "addon")}
    for p in every:
        p["jobs"] = []
    visits = [p for p in every if p["visit"]]
    fixed_by = by(month_of, [v for v in fixed if v["visit"] and v["kind"] != "comeback"])
    rank = {"van": 0, "truck": 1, "suv": 2, "car": 3}
    pools, carry = {}, collections.defaultdict(lambda: collections.Counter())
    for key, group in by(month_of, visits).items():
        site, year, month = key
        rng = streams.stream(seed, "content", *key)
        olds = fixed_by.get(key, [])
        n = len(group) + len(olds)
        mc = {k: month_curve(cfg, k, year, month) for k in PRICED}
        base = n / sum(share[k]["lead"] * mc[k] for k in PRICED)
        # comebacks will take comeback.<site> of these visits and hand their inspection and raised jobs to the others: the
        # inspection and raised-job counts are dealt on the visits that stay
        stay = 1 - inputs.value(f"comeback.{site}", cfg) / 100
        group.sort(key=lambda p: (p["day"].weekday() != 5, rank[p["vehicle"]["vehicle_class"]], p["at"]))

        def labels(kind, count):
            # largest remainder over the jobs, each job's remainder carried to the shop's next month, so that a job's
            # count over any run of months stays within one of its share (a job of a low month still comes)
            weights = {k: share[k][kind] * mc[k] for k in PRICED}
            exact = {k: count * w / sum(weights.values()) + carry[site, kind][k] for k, w in weights.items()}
            out = collections.Counter({k: max(0, math.floor(x)) for k, x in exact.items()})
            order_ = sorted(exact, key=lambda k: (out[k] - exact[k], k))
            for k in order_[:max(0, count - sum(out.values()))]:
                out[k] += 1
            for k in [k for k in reversed(order_) if out[k]][:max(0, sum(out.values()) - count)]:
                out[k] -= 1
            carry[site, kind] = {k: exact[k] - out[k] for k in exact}
            for v in olds:
                for j in v["jobs"]:
                    if kind == ("lead" if j is v["jobs"][0] else "sold" if j.get("found") else "addon" if j["key"] != "courtesy_inspection" else None):
                        out[j["key"]] -= 1
            return out
        for p, k in assign(b, rng, [(p, 1) for p in group], labels("lead", n), weights["lead"]):
            p["jobs"].append({"key": k, "status": "approved"})
        have = sum(any(j["key"] == "courtesy_inspection" for j in v["jobs"]) for v in olds)
        for p in rng.sample(group, max(0, min(len(group), round(courtesy * n * stay) - have))):
            p["jobs"].append({"key": "courtesy_inspection", "status": "approved"})
        looked = [p for p in group if any(j["key"] in orders.INSPECTING for j in p["jobs"])]
        old_found = [j for v in olds for j in v["jobs"] if j.get("found")]
        lift = sum(share[k]["sold"] * mc[k] for k in PRICED) / sum(share[k]["sold"] for k in PRICED)
        have = sum(any(j.get("found") for j in v["jobs"]) for v in olds)
        rec = rng.sample(looked, max(0, min(len(looked), round(rec_share * base * lift * stay) - have)))
        sizes = [int(s) for s in deal(seed, ("rec size", *key), len(rec), {"3": 4 - rec_mean, "4": rec_mean - 3})]
        for p, k in assign(b, rng, list(zip(rec, sizes)), labels("sold", sum(sizes) + len(old_found)), weights["sold"]):
            p["jobs"].append({"key": k, "status": "declined", "found": None})
        # what was found: bad for erp.inspection.bad_share, documented at the shop's erp.inspection.bad_documented, the
        # rest of the bad items one of the two or neither; readings from texts.json
        found = [j for p in rec for j in p["jobs"] if "found" in j]
        bads = round((len(found) + len(old_found)) * inputs.value("erp.inspection.bad_share", cfg) / 100) - sum(j["found"] == "bad" for j in old_found)
        bads = max(0, min(bads, len(found)))
        for j, bad in zip(found, deal(seed, ("bad", *key), len(found), {True: bads, False: len(found) - bads})):
            j["found"] = "bad" if bad else "watch"
        bad_jobs = [j for j in found if j["found"] == "bad"]
        old_bad = [j for j in old_found if j["found"] == "bad"]
        full = round((len(bad_jobs) + len(old_bad)) * inputs.value("erp.inspection.bad_documented", cfg)[site] / 100) - sum(
            1 for j in old_bad if j.get("reading") and j.get("photo"))
        full = max(0, min(full, len(bad_jobs)))
        for j, whole in zip(bad_jobs, deal(seed, ("documented", *key), len(bad_jobs), {True: full, False: len(bad_jobs) - full})):
            measured, j["photo"] = [(True, True), (True, False), (False, True), (False, False)][0 if whole else rng.randrange(1, 4)]
            j["reading"] = orders.reading(cfg, j["key"], "bad", rng) if measured else None
        for j in found:
            if j["found"] == "watch":
                j["reading"] = orders.reading(cfg, j["key"], "watch", rng)
        # one call per order: the same day for 90 %, the next morning for the rest (spec section 4.5), by
        # erp.approval.method; the next morning only where it comes before T's day, so the order closes by T
        later = [p for p in rec if orders.opening(b, site, orders.hours(b, site, p["day"])[1]).date() < b.a["T"].date()]
        late = {id(p) for p in rng.sample(later, min(len(later), round(len(rec) * 0.1)))}
        for p, method in zip(rec, deal(seed, ("method", *key), len(rec), inputs.value("erp.approval.method", cfg))):
            decided = None
            if id(p) in late:
                decided = orders.opening(b, site, orders.hours(b, site, p["day"])[1]) + streams.stream(seed, "next morning", site, p["at"]).randrange(61) * orders.MINUTE
            for j in p["jobs"]:
                if "found" in j:
                    j.update(method=method, **({"decided": decided} if decided else {}))
        pools[key] = labels("addon", round(base * sum(share[k]["addon"] * mc[k] for k in PRICED)))

    approve(b, visits, fixed)

    # priced jobs per order by mix.json jobs_per_order, per shop and month: the largest counts go to the orders with the
    # most approved raised jobs; the month's customer add-ons fill them
    distribution = MIX[cfg]["jobs_per_order"]["distribution"]
    for key, group in by(month_of, visits).items():
        rng = streams.stream(seed, "add-ons", *key)
        pool = pools[key]
        sold = {id(p): sum(j["status"] == "approved" for j in p["jobs"] if j.get("found")) for p in group}
        ranked = sorted(group, key=lambda p: (sold[id(p)], rng.random()))
        slots = [max(0, int(n) - 1 - sold[id(p)]) for p, n in zip(ranked, sorted(deal(seed, ("jobs per order", *key), len(group), distribution), key=int))]
        room = sum(max(c, 0) for c in pool.values())
        while sum(slots) > room:  # fewer add-ons in the month than the counts ask: the largest give first
            slots[slots.index(max(slots))] -= 1
        i = 0
        while sum(slots) < room:  # more: the orders with the fewest jobs take them
            slots[i % len(slots)] += 1
            i += 1
        for p, k in assign(b, rng, list(zip(ranked, slots)), pool, weights["addon"]):
            p["jobs"].insert(1, {"key": k, "status": "approved"})
    for p in every:
        if not p["visit"]:
            rng = streams.stream(seed, "estimate jobs", p["site"], p["at"])
            p["jobs"] = [{"key": customers.weighted(rng, {k: weights["lead"](k, p) for k in PRICED if allowed(b, p, k)}), "status": "approved"}]
            if p["kind"] == "void":
                p["jobs"][0]["status"] = "pending"
                continue
            for _ in range(int(customers.weighted(rng, distribution)) - 1):
                taken = {j["key"] for j in p["jobs"]}
                p["jobs"].append({"key": customers.weighted(rng, {k: weights["addon"](k, p) for k in PRICED if k not in taken and allowed(b, p, k)}),
                                  "status": "approved"})
            for j in p["jobs"]:
                j.update(status="declined", expires=p["expires"])
    tiers(b, every, fixed)


def approve(b, visits, fixed, again=False):
    """The advisor's dealt rate (spec section 4.3): for every advisor and `window`, pNN.sold_rec of his raised jobs are
    approved (F1 has no row: west's, sold.west); inside a group the jobs approved are those whose catalogue job is
    furthest behind the common rate, so each job's sold count holds too. A job held for a comeback stays approved. The
    days at east without slot 16 are dealt apart: slot 17 decides alone there at his rate (s5.east_without_16).
    `again`, after the comebacks moved raised jobs between visits: each group back to its count by turning as few free
    jobs as it takes (not the pad jobs, counted exactly by s6.counts), a job turned approved done by its visit's mechanic."""
    cfg, seed = b.cfg, b.seed

    def group_of(p):
        return p["advisor"], window(b, p), p["site"] == "east" and "16" not in orders.advisors(b, "east", p["day"])
    groups = by(group_of, visits)
    olds = by(group_of, [v for v in fixed if v["visit"]])
    quotas = {}
    for (s, k, alone), group in groups.items():
        sold = inputs.value(slot_key(s, "sold_rec") if s != "F1" else "sold.west", cfg)
        old = [j for v in olds.get((s, k, alone), []) for j in v["jobs"] if j.get("found") and j["status"] in ("approved", "declined")]
        raised = [j for p in group if orders.decides(b, p["site"], p["at"]) for j in p["jobs"] if j.get("found")]
        quotas[s, k, alone] = round((len(raised) + len(old)) * sold / 100) - sum(j["status"] == "approved" for j in old)
    carry = collections.defaultdict(collections.Counter)
    for s, k, alone in sorted(groups, key=lambda x: (-x[1], x[0], x[2])):
        raised = [j for p in groups[s, k, alone] if orders.decides(b, p["site"], p["at"]) for j in p["jobs"] if j.get("found")]
        streams.stream(seed, "sold", s, k, *(("alone",) if alone else ())).shuffle(raised)
        if again:
            need = quotas[s, k, alone] - sum(j["status"] == "approved" for j in raised)
            visit = {id(j): p for p in groups[s, k, alone] for j in p["jobs"]}
            for j in raised:
                if need and not j.get("keep") and j["key"] not in orders.PADS and j["status"] == ("declined" if need > 0 else "approved"):
                    j["status"] = "approved" if need > 0 else "declined"
                    if need > 0:
                        j["tech"] = visit[id(j)]["jobs"][0].get("tech")
                    need -= 1 if need > 0 else -1
            continue
        # each catalogue job approved at the group's own rate by the largest remainder, its remainder carried to the advisor's
        # next group (over the history, not inside one group alone: a seasonal job approved at the rate of its own month,
        # so its curve holds, and a rare one still comes)
        locked = [j for j in raised if j.get("keep")]
        free = [j for j in raised if not j.get("keep")]
        want = max(0, min(len(free), quotas[s, k, alone] - len(locked)))
        seen = collections.Counter(j["key"] for j in free)
        exact = {key: want * n / len(free) + carry[s, alone][key] for key, n in seen.items()} if free else {}
        take = {key: min(seen[key], max(0, math.floor(x))) for key, x in exact.items()}
        for key in sorted(exact, key=lambda key: (take[key] - exact[key], key)):
            if sum(take.values()) >= want:
                break
            if take[key] < seen[key]:
                take[key] += 1
        for key in sorted(exact, key=lambda key: (exact[key] - take[key], key)):
            if sum(take.values()) <= want:
                break
            if take[key] > 0:
                take[key] -= 1
        for key, x in exact.items():
            carry[s, alone][key] = x - take[key]
        for j in free:
            j["status"] = "approved" if take[j["key"]] > 0 else "declined"
            take[j["key"]] -= j["status"] == "approved"
        for j in locked:
            j["status"] = "approved"


def tiers(b, every, fixed):
    """Parts tiers by mix.json tier_mix, dealt per shop and month over every job with parts (those already there counted);
    west's cheap pads stay (`background.technicians`)."""
    cfg, seed = b.cfg, b.seed
    olds = by(month_of, fixed)
    for key, group in by(month_of, every).items():
        mine = [j for p in group for j in p["jobs"] if JOBS[j["key"]][cfg]["parts"] and j.get("tier") != "cheap"]
        old = [j for v in olds.get(key, []) for j in v["jobs"] if JOBS[j["key"]][cfg]["parts"] and j.get("tier")]
        labels = collections.Counter(deal(seed, ("tier", *key), len(mine) + len(old), MIX[cfg]["tier_mix"]))
        labels.subtract(j["tier"] for j in old)
        pool = [t for t, c in labels.items() for _ in range(max(c, 0))]
        streams.stream(seed, "tiers", *key).shuffle(pool)
        for j, tier in zip(mine, pool + ["standard"] * len(mine)):
            j["tier"] = tier
