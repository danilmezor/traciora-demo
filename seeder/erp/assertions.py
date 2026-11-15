"""Section 7 of generator-spec.md: what the background must never do, asserted over the built tables before they load
(spec section 2, step 7). `check(b)` evaluates every line; a line that fails stops the build with its name, unless it
is in WAITING: the lines that rest on rows another step of the build writes, reported until that step is in. Beside
section 7's lines, `facts.mileage` (a story file's stated odometer is its order's `mileage_in`) and
`erp.uncollected_car`."""
import collections
import datetime as dt
from decimal import Decimal

from seeder import clock, inputs
from seeder.erp import customers, orders, plan
from seeder.erp.accounts import office

# S6.3 rests on the pad jobs per fitter and brand of s6.counts and s6.p27_pad_share, which the pad deal of the
# background and parts steps does not reach yet
WAITING = ("S6.3",)
OPEN = ("estimate", "approved", "in_progress", "waiting_parts", "waiting_sublet", "completed")


def check(b):
    cfg, a = b.cfg, b.a
    T = a["T"]
    slot = {id(p): s for s, p in b.people.items()}
    records = list(b.orders.values())
    history = collections.defaultdict(list)
    for h in b.tables["order_status_history"]:
        history[id(h["repair_order_id"])].append(h)
    payments = collections.defaultdict(list)
    for p in b.tables["payment"]:
        if p["repair_order_id"] is not None:
            payments[id(p["repair_order_id"])].append(p)
    comebacks = collections.defaultdict(list)
    for o in records:
        if o["order"]["comeback_of_id"]:
            comebacks[id(o["order"]["comeback_of_id"])].append(o)
    accounts = b.accounts

    def account(o):
        return next((i for i, c in accounts.items() if o["order"]["customer_id"] is c), None)

    def visit(o):
        return o["order"]["status"] not in ("void", "declined")

    def gross(ro):  # the bill before the discount (price.discount_base: en before tax, ru as billed)
        return ro["labor_total"] + ro["parts_total"] + ro["sublet_total"] + ro["fees_total"]

    def share(ro):
        return ro["discount_total"] / gross(ro) if gross(ro) else 0

    def advisor(o):
        return slot.get(id(o["order"]["advisor_id"]))

    lines = {}
    days = lambda n: T - dt.timedelta(n)  # noqa: E731

    # S1.1: every account but A5 came in the last 90 days; none but A5 and A6 under half a pre-T-150 block in the last 30
    lines["S1.1"] = all(any(account(o) == i and visit(o) and o["order"]["opened_at"] > days(90) for o in records) for i in accounts if i != "A5") and all(
        sum(account(o) == i and visit(o) and o["order"]["opened_at"] > days(30) for o in records) >= inputs.value(f"acct.{i}.visits", cfg)[0] / 2
        for i in accounts if i not in ("A5", "A6"))
    # S1.2: no A5 order after its last visit
    lines["S1.2"] = not any(account(o) == "A5" and o["order"]["opened_at"].date() > a["a5_last_visit"] for o in records)

    # S1.6: the accounts' estimates whose first decision came two days or more after opening are A6's five; its
    # declined ones are its four
    def slow(o):
        rows = sorted(history[id(o["order"])], key=lambda h: h["changed_at"])
        return len(rows) > 1 and rows[1]["changed_at"] - rows[0]["changed_at"] >= dt.timedelta(2)
    waited = [account(o) for o in records if account(o) and slow(o)]
    s1a6 = inputs.value("s1.a6", cfg)
    lines["S1.6"] = waited == ["A6"] * s1a6["estimates_waited_two_days_or_more"] and sum(
        account(o) == "A6" and o["order"]["status"] == "declined" for o in records) == s1a6["estimates_declined_or_expired"]

    # S1.4 and S16.3: A1's statements are paid as acct.A1.days_to_pay says, and only so
    pay = inputs.value("acct.A1.days_to_pay", cfg)
    statements = sorted((s for s in b.tables["statement"] if s["customer_id"] is accounts["A1"]), key=lambda s: s["issued_on"])
    paid_on = {id(p["statement_id"]): p["received_at"].date() for p in b.tables["payment"] if p.get("statement_id")}
    late = [(s, paid_on.get(id(s))) for s in statements]

    def moved(issued, days):  # the row's day, moved on to the office's next working day (accounts.bill)
        day = issued + dt.timedelta(days)
        while not office(cfg, day):
            day += clock.DAY
        return day
    if cfg == "en":
        n = sum(s["issued_on"] + dt.timedelta(pay["last_three_paid"][-1]) <= T.date() - clock.DAY for s, _ in late)
        lines["S1.4/S16.3"] = bool(late) and all(
            (when is None and s["status"] == ("overdue" if (T.date() - s["issued_on"]).days > pay["until"] else "sent")) if i >= n else
            when is not None and office(cfg, when) and (when == moved(s["issued_on"], pay["last_three_paid"][i - n + 3]) if i >= n - 3 else abs((when - s["issued_on"]).days - pay["until"]) <= 2)
            for i, (s, when) in enumerate(late))
    else:
        lines["S1.4/S16.3"] = bool(late) and all(
            (when is None and s["status"] == ("overdue" if x > pay["until"] else "sent")) if x < 60 else
            when is not None and when == moved(s["issued_on"], round(pay["until"] + (pay["late"] - pay["until"]) * (150 - min(x, 150)) / 90))
            for s, when in late for x in [(T.date() - s["issued_on"]).days])
    # S1.7: no statement of A2 or A4 overdue at T
    lines["S1.7"] = bool(b.tables["statement"]) and not any(s["status"] == "overdue" and s["customer_id"] in (accounts["A2"], accounts["A4"]) for s in b.tables["statement"])

    # S2.1, S2.3, S2.5: no discount of 15 % or more but F1's; after the rule none of 10 % or more without an approver
    # but slot 23's two; at west after the rule exactly four orders with a discount of 10 % or more, all paid in cash;
    # en no void with a payment but F1's 14
    paying = [o for o in records if o["order"]["order_type"] == "customer_pay"]
    lines["S2.1"] = not any(share(o["order"]) >= Decimal("0.15") and advisor(o) != "F1" for o in paying)
    after = [o for o in paying if o["order"]["opened_at"].date() >= a["rule_on"] and share(o["order"]) >= Decimal("0.1")]
    unapproved = [advisor(o) for o in after if o["order"]["discount_approved_by_id"] is None]
    west_after = inputs.value("s2.west.discounts_after", cfg)
    west = [o for o in after if o["site"] == "west"]
    lines["S2.3"] = unapproved == ["23"] * west_after["unapproved_by_23"] and len(west) == west_after["orders"] and all(
        any(p["method"] == "cash" for p in payments[id(o["order"])]) for o in west)
    voided = [advisor(o) for o in records if o["order"]["status"] == "void" and payments[id(o["order"])]]
    lines["S2.5"] = cfg == "ru" or voided == ["F1"] * inputs.value("s2.f1.second", cfg)["count"]

    # S2.8: en no till difference of -20 or less but F1's 19; ru no issue without an order line but F1's 46, and no
    # order at west clocked more than an hour over its sold hours but F1's 22
    if cfg == "en":
        short = [slot.get(id(c["closed_by_id"])) for c in b.tables["cash_drawer_close"] if c["difference"] <= -20]
        lines["S2.8"] = short == ["F1"] * inputs.value("s2.f1.third", cfg)["count"]
    else:
        loose = [slot.get(id(m["employee_id"])) for m in b.tables["stock_movement"] if m["kind"] == "issue" and m.get("order_part_id") is None]
        clocked = collections.Counter()
        for e in b.tables["time_entry"]:
            if e["clock_out"]:
                clocked[id(e["order_job_id"]["repair_order_id"])] += (e["clock_out"] - e["clock_in"]).total_seconds() / 3600
        over = [advisor(o) for o in records if o["site"] == "west" and clocked[id(o["order"])] > float(sum(l["hours"] for l in o["labor"] if l["technician_id"])) + 1]
        lines["S2.8"] = loose == ["F1"] * inputs.value("s2.f1.second", cfg)["count"] and over == ["F1"] * inputs.value("s2.f1.third", cfg)["count"]

    # S5.1: east's sold share by day follows the advisor on duty only; S5.3: east's diagnostic orders for main's
    # customers in the leave weeks are the eleven
    # (the raised jobs at east since G, approved over decided, on the days slot 16 wrote orders and on the others, at
    # s5.east_with_16 and s5.east_without_16 within checks.sql's 4 points)
    her_days = {o["order"]["opened_at"].date() for o in records if advisor(o) == "16"}
    raised = [(o["order"]["opened_at"].date() in her_days, j["status"]) for o in records if o["site"] == "east" and o["order"]["opened_at"].date() >= a["G"]
              for j in o["jobs"] if j.get("item_row") and j["status"] in ("approved", "declined")]
    lines["S5.1"] = all(abs(100 * sum(st == "approved" for d, st in raised if d == hers) / max(1, sum(d == hers for d, _ in raised)) - inputs.value(key, cfg)) <= 4
                        for hers, key in ((True, "s5.east_with_16"), (False, "s5.east_without_16")))
    lines["S5.3"] = sum(o["site"] == "east" and a["leave_from"] <= o["order"]["opened_at"].date() <= a["leave_to"] and o["order"]["customer_id"]["created_location_id"] is b.shops["main"]
                        and orders.JOBS[o["jobs"][0]["key"]]["category"] == "diagnostics" for o in records) == inputs.value("s5.leave", cfg)["orders_sent_to_east"]

    # S6.2: the cars in waiting_parts at T are s6.waiting_at_t, by shop and calendar days since the status was set
    want = {s: [(T.date() - d).days for d in a["s6_since"][s]] for s in ("main", "east", "west")}  # each count moved back to a full open day
    have = collections.defaultdict(list)
    for o in records:
        if o["order"]["status"] == "waiting_parts":
            have[o["site"]].append((T.date() - max(h["changed_at"] for h in history[id(o["order"])] if h["status"] == "waiting_parts").date()).days)
    lines["S6.2"] = all(sorted(have[s], reverse=True) == sorted(d, reverse=True) for s, d in want.items())

    # S6.3: the pad jobs that came back, per fitter and brand, are those of s6.counts
    brand = inputs.value("s6.brand", cfg)
    back = collections.Counter()
    for o in paying:
        if o["site"] == "west" and o["order"]["opened_at"].date() < a["bought"]:
            continue
        returned = any(j["key"] in orders.PADS for c in comebacks[id(o["order"])] for j in c["jobs"])
        for j in o["jobs"]:
            if j["key"] in orders.PADS and j["status"] == "approved" and returned:
                cheap = any(p["brand"] == brand for p in j["parts"])
                by27 = j.get("labor_row") and j["labor_row"]["technician_id"] is b.people["27"]
                back["p27_cheap" if by27 and cheap else "p27_good" if by27 else "others_cheap" if cheap and o["site"] == "west" else
                     "others_good_at_west" if o["site"] == "west" else None] += 1
                back["good_not_27_all_shops"] += not by27 and not cheap
    counts = inputs.value("s6.counts", cfg)
    lines["S6.3"] = all(back[k] == counts[f"comebacks_{k}"] for k in ("p27_good", "p27_cheap", "others_cheap", "others_good_at_west", "good_not_27_all_shops"))

    # S7, S8: the named customers' phones are theirs alone; S8's job is slot 7's one approved job whose approved
    # amount differs from its lines; only slot 7's p07.rebilled orders are invoiced twice
    phones = collections.Counter(c.get("phone") for c in b.tables["customer"] if c.get("phone"))
    s8 = b.named["S8"][0]
    odd = [o for o in records if advisor(o) == "7" for j in o["jobs"] if j["status"] == "approved" and j["row"]["approved_amount"] != j["value"]]
    twice = [advisor(o) for o in records if sum(h["status"] == "invoiced" for h in history[id(o["order"])]) > 1]
    lines["S7/S8"] = all(phones[b.named[k][0]["phone"]] == 1 for k in ("S7", "S8")) and [o["order"]["customer_id"] for o in odd] == [s8] and twice == ["7"] * inputs.value("p07.rebilled", cfg)

    # S14.5: F2's comebacks are pF2.comebacks of his orders of his last six months (dealt exactly)
    since = clock.months_back(b.people["F2"]["left_on"], 6)
    def most(o):  # the mechanic with the most hours on the order, as pF2.comebacks reads him
        hours = collections.Counter()
        for line in o["labor"]:
            if line["technician_id"]:
                hours[id(line["technician_id"])] += line["hours"]
        return max(hours, key=hours.get, default=None)
    his = [o for o in paying if not o["order"]["comeback_of_id"] and o["order"]["opened_at"].date() >= since and o["order"]["status"] in ("invoiced", "paid")
           and most(o) == id(b.people["F2"])]
    lines["S14.5"] = sum(bool(comebacks[id(o["order"])]) for o in his) == round(len(his) * inputs.value("pF2.comebacks", cfg) / 100)

    # S15: the counts of section 6, kind by kind; every warranty and goodwill order keeps erp.warranty_order_totals
    lines["S15.M1"] = sum(n > 1 for n in phones.values()) == inputs.value("s15.mess", cfg)["duplicate_pairs"]
    cars = b.tables["vehicle"]
    unknown = [v for v in cars if v["vin"] is None]
    named = {id(v) for _, vs in b.named.values() for v in vs}  # the named cars without a VIN count, wherever their year falls (mess.py, M2)
    lines["S15.M2"] = len(unknown) == round(len(cars) * inputs.value("s15.mess", cfg)["vin_missing_pct"] / 100) and max(
        (v["year"] for v in unknown if id(v) not in named), default=0) <= min((v["year"] for v in cars if v["vin"]), default=9999)
    readings = collections.defaultdict(list)
    for o in sorted(records, key=lambda o: o["order"]["opened_at"]):
        readings[id(o["order"]["vehicle_id"])].append(o["order"])
    lines["S15.M3"] = sum(r["opened_at"] > dt.datetime.combine(clock.months_back(T.date(), 24), T.time()) and (r["mileage_in"] < p["mileage_in"] or r["mileage_in"] > 3 * p["mileage_in"])
                          for rs in readings.values() for p, r in zip(rs, rs[1:])) == inputs.value("s15.mess", cfg)["wrong_mileage_orders"]
    lines["S15.M4"] = [(o["site"], o["order"]["status"], o["order"]["opened_at"].date()) for o in sorted(records, key=lambda o: o["order"]["opened_at"])
                       if o["order"]["status"] in OPEN and o["order"]["opened_at"] < days(60)] == [
        ("west", "completed", a["week_day"](-22, 2)), ("main", "in_progress", a["week_day"](-12, 1)), ("east", "approved", a["week_day"](-10, 1))]
    lines["S15.M5"] = sum(c["name"] == customers.WALKIN[cfg] for c in b.tables["customer"]) == 1
    mess = inputs.value("s15.mess", cfg)["payments_not_one_to_one"]
    in_parts = sum(sum(p["kind"] == "payment" for p in ps) > 1 for ps in payments.values())
    refunds = sum(p["kind"] == "refund" for p in b.tables["payment"])
    several = [p for p in b.tables["payment"] if p.get("statement_id") and sum(o["order"].get("statement_id") is p["statement_id"] for o in records) > 1]
    settled = [p for p in b.tables["payment"] if p.get("statement_id")]
    lines["S15.M6"] = in_parts == mess["order_paid_in_two_parts"] and refunds == mess["refund"] and (len(several) == len(settled) > 0 if cfg == "en" else len(several) == 1)
    typed = inputs.value("parts.typed_by_hand", cfg)
    year = [(o["site"], p) for o in records if o["order"]["opened_at"] > dt.datetime.combine(clock.months_back(T.date(), 12), T.time()) for p in o["parts"]]
    lines["S15.M7"] = all(abs(100 * sum(p["part_id"] is None for s, p in year if (s == "west") == west) / max(1, sum((s == "west") == west for s, _ in year))
                              - typed["west" if west else "home"]) <= 0.5 for west in (True, False))
    lines["S15.M8"] = sum(o["order"]["customer_id"] is not o["order"]["vehicle_id"]["customer_id"] for o in records) == inputs.value("s15.mess", cfg)["wrong_customer_orders"]
    # (paid once its work is completed; one completed on T's day is collected at the counter after T; slot 8's open second
    # look is still approved at T)
    lines["S15.warranty"] = all(o["order"]["total"] == 0 and o["order"]["tax_total"] == 0 and o["order"]["discount_total"] == gross(o["order"])
                                and o["order"].get("discount_approved_by_id") is None and not any(p["kind"] == "payment" for p in payments[id(o["order"])])
                                and (o["order"]["status"] == "paid" or not any(h["status"] == "completed" for h in history[id(o["order"])])
                                     or max(h["changed_at"] for h in history[id(o["order"])] if h["status"] == "completed").date() == orders.until(b, o["site"]).date())
                                for o in records if o["order"]["order_type"] != "customer_pay")

    # S11: no seasonal tyre job outside the windows beyond the base (ru: season.tyre.factor), no air-conditioning spike
    # outside May to August: by the index checks.sql reads (jobs per period over the mean, 730 days), within its 0.3
    since = T - dt.timedelta(730)
    approved = [(o["order"]["opened_at"], j["key"]) for o in records if o["order"]["opened_at"] > since for j in o["jobs"] if j["status"] == "approved"]
    cool = collections.Counter(t.month for t, k in approved if orders.JOBS[k]["category"] == "air_conditioning")
    curve = inputs.value("season.ac_curve", cfg)
    mean = sum(cool.values()) / 12
    lines["S11"] = all(abs(cool[m] / mean - curve[m - 1]) <= 0.3 for m in range(1, 13) if m not in (5, 6, 7, 8))
    if cfg == "ru":
        days = [since.date() + dt.timedelta(i) for i in range(731)]
        base = {d: plan.curve(cfg, "seasonal_tyre_change", d) for d in days}
        low = min(base.values())
        tyres = collections.Counter(t.date() for t, k in approved if k in ("seasonal_tyre_change", "seasonal_wheel_swap"))
        out = [d for d in days if base[d] == low]
        lines["S11"] &= abs(sum(tyres[d] for d in out) / len(out) / (sum(tyres.values()) / len(days)) - low / (sum(base.values()) / len(days))) <= 0.3

    # erp.uncollected_car: one counter order at west invoiced before T's day and unpaid at T, on west's 3rd full open
    # day before T (an order invoiced late on the open day before T may stand beside it until it is collected)
    def invoiced(o):
        return min(h["changed_at"] for h in history[id(o["order"])] if h["status"] == "invoiced").date()
    eve = clock.wd(cfg, T.date(), -1)
    unpaid = [invoiced(o) for o in paying if o["site"] == "west" and o["order"]["status"] == "invoiced"
              and not o["order"]["customer_id"].get("payment_terms_days") and not payments[id(o["order"])] and invoiced(o) < eve]
    lines["erp.uncollected_car"] = unpaid == [clock.wd(cfg, T.date(), -3)]

    lines["facts.mileage"] = all(o["order"]["mileage_in"] == o["stated"] for o in records if "stated" in o)

    failed = [name for name, ok in lines.items() if not ok]
    stop = [name for name in failed if name not in WAITING]
    if stop:
        raise ValueError("generator-spec.md section 7 fails: " + ", ".join(stop))
    return failed
