"""Section 6 of generator-spec.md, the planted mess of story S15, kinds M1, M2, M3, M4, M6 (the split payment and the
refund; the statement payments are the accounts step's), M7 and M8 (M9, M10 and M11 are made where their rows are; M5
by S02). `fill(b)` runs after `background.fill`: every
order it touches is a background order of the day plan, so the day counts, shares and rates stay as dealt (M4's west
order is planted, one order more that day). It runs
before the steps that read an order's lines or customer (parts and stock, reminders): a typed line has no stock
movement, and a duplicate's or a wrong record's order is theirs from the start. The orders it picks have no comeback
either way, are paid by card (a till close holds only cash) and are no story's: no planted record (`planted`) and no
story person's."""
import collections
import datetime as dt
from decimal import Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, orders, plan


def fill(b):
    cfg, a, seed = b.cfg, b.a, b.seed
    T = a["T"]
    rng = streams.stream(seed, "mess")
    records = sorted(b.orders.values(), key=lambda o: o["order"]["opened_at"])
    story = {id(c) for c, _ in b.named.values()} | {id(c) for c, _ in b.small} | {id(b.walkin)}
    planted = {id(o["order"]) for o in records if o.get("planted")}
    returned = {id(o["order"]["comeback_of_id"]) for o in records if o["order"]["comeback_of_id"]}
    visits = collections.Counter(id(o["order"]["customer_id"]) for o in records)
    used = set()

    def hosts(site, car=None, since=dt.datetime.min, pays=("card",)):
        """Paid background orders by card (or `pays`) of a private customer at `site`, not F1's, no comeback and none come
        back, re-billed never; with `car` (the order moves to it), of a returning customer, so that his record keeps an order, of the
        car's class and offered for it."""
        out = []
        for o in records:
            ro, c = o["order"], o["order"]["customer_id"]
            if (o["site"] != site or ro["opened_at"] <= since or id(ro) in used or id(ro) in planted or id(ro) in returned or ro["comeback_of_id"] or ro["status"] != "paid"
                    or o["pay"] not in pays or o["added"] or id(c) in story or c.get("payment_terms_days") or car and visits[id(c)] < 2
                    or ro["advisor_id"] is b.people["F1"]):  # S02 counts every order of F1's and its cash payments
                continue
            p = {"site": site, "day": ro["opened_at"].date(), "vehicle": car}
            if car and (ro["vehicle_id"]["vehicle_class"] != car["vehicle_class"] or not all(plan.allowed(b, p, j["key"]) for j in o["jobs"])
                        or ro["vehicle_id"]["model"] in (ro["complaint"] or "")):
                continue
            out.append(o)
        return out

    def move(o, c, car):
        """The order written on another record or car; its booking follows."""
        used.add(id(o["order"]))
        o["order"].update(customer_id=c, vehicle_id=car)
        if o["appointment"]:
            o["appointment"].update(customer_id=c, vehicle_id=car)

    # M4 (s15.dates): west opened on the Wednesday of week T-22, its work done the next day, never invoiced, the car
    # gone; main (Tuesday of week T-12) left in_progress; east (Tuesday of week T-10) left approved, its work never
    # started (orders.settle keeps them there whatever later step settles them again). West's is planted, as the
    # uncollected car is (a quiet Wednesday at west may have no background order whose work fits the next day): a
    # private customer of west, a job whose parts come from the shelf, its work put into the next day's shift by whoever
    # has room then (`orders.settle` books an order left completed on its start's day). Main's and east's are hosts of
    # that day: their payment goes, and a cash one leaves that day's till close
    day = a["week_day"](-22, 2)
    nxt = orders.opening(b, "west", orders.hours(b, "west", day)[1])
    rng4 = streams.stream(seed, "m4 west")
    opened = plan.moment(b, rng4, "west", day)
    customer, cars = streams.pick(rng4, [(c, v) for c, v in b.pools["west"] if id(c) not in story and c["created_at"] < opened])
    car = streams.pick(rng4, cars)
    p = {"site": "west", "day": day, "vehicle": car}
    key = customers.weighted(rng4, {k: plan.SHARES[cfg][k]["lead"] * plan.curve(cfg, k, day) for k in plan.PRICED
                                    if k in orders.STOCKED and orders.sold_hours(cfg, k, car) and plan.allowed(b, p, k)})
    tech = streams.pick(rng4, [r for s, r in orders.mechanics(b, "west", nxt.date()) if r["left_on"] is None])
    ro = orders.order(b, "west", opened, customer, car, streams.pick(rng4, orders.advisors(b, "west", day)),
                      [{"key": key, "status": "approved", "tech": tech, "tier": "standard"}], start=nxt, complaint=orders.JOBS[key][cfg]["name"])
    o = b.orders[id(ro)]
    o["open"], o["planted"] = "completed", True
    orders.settle(b, o)
    used.add(id(ro))
    for site, day, left in (("main", a["week_day"](-12, 1), "in_progress"), ("east", a["week_day"](-10, 1), "approved")):
        pool = [o for o in hosts(site, pays=("card", "fast_payment", "check", "cash")) if o["order"]["opened_at"].date() == day and not o["sublets"]]
        o = streams.pick(rng, pool)
        before_pay = list(o["payments"])
        o["open"] = left
        orders.settle(b, o)
        for pay in before_pay:
            if pay["method"] == "cash" and pay not in o["payments"]:
                close = next(r for r in b.tables["cash_drawer_close"] if r["location_id"] is b.shops[site] and r["business_date"] == pay["received_at"].date())
                for column in ("expected_cash", "counted_cash"):
                    close[column] -= pay["amount"] * (-1 if pay["kind"] == "refund" else 1)
        used.add(id(o["order"]))

    # M1: the 24 records of the duplicate pairs, an order on each; record b made at the counter for its order, after
    # record a's; ru: the pair's first order at a shop of its plate's region (erp.vehicle.plates)
    regions = inputs.value("erp.vehicle.plates", cfg).get("region_by_shop")
    for x in customers.NAMED[cfg]["S15_duplicate_pairs"]:
        first_c, (first_car,) = b.named[f"dup.{x['pair']}.a"]
        second_c, (second_car,) = b.pending.pop(f"dup.{x['pair']}.b")
        site = x["record_a"]["created_at_shop"]
        if cfg == "ru" and not any(first_car["plate"].endswith(r) for r in regions[site]):
            site = next(s for s, rs in regions.items() if any(first_car["plate"].endswith(r) for r in rs))
        later = hosts(x["record_b"]["created_at_shop"], second_car, first_c["created_at"])
        one = streams.pick(rng, [o for o in hosts(site, first_car, first_c["created_at"]) if o["order"]["opened_at"] + clock.DAY < later[-1]["order"]["opened_at"]])
        move(one, first_c, first_car)
        two = streams.pick(rng, [o for o in later if o["order"]["opened_at"] > one["order"]["opened_at"] + clock.DAY and id(o["order"]) not in used])
        second_c["created_at"] = two["order"]["opened_at"] - rng.randint(1, 10) * orders.MINUTE
        b.named[f"dup.{x['pair']}.b"] = (second_c, [second_car])
        b.tables["customer"].append(second_c)
        b.tables["vehicle"].append(second_car)
        move(two, second_c, second_car)

    # M8: case 1 the owner's car on her relative's record; case 2 the company's van or truck on its owner's own record
    for x in customers.NAMED[cfg]["S15_car_on_the_wrong_customer"]:
        under = b.named[f"m8.{x['case']}.under"][0]
        if isinstance(x["car"], dict):
            car = b.named[f"m8.{x['case']}.owner"][1][0]
            move(streams.pick(rng, hosts(x["shop"], car, under["created_at"])), under, car)  # (after the record was made)
            continue
        company, cars = next((c, cars) for c, cars in b.small if c["name"] == x["belongs_to"]["name"])
        car = next(v for v in cars if v["model"].split(",")[0].split()[0] in x["car"])
        own = [o for o in records if o["order"]["vehicle_id"] is car and o["order"]["status"] == "paid" and id(o["order"]) not in returned | planted
               and not o["order"]["comeback_of_id"]]
        own = [o for o in own if o["order"]["opened_at"] > under["created_at"]]
        move(streams.pick(rng, own) if own else streams.pick(rng, hosts(x["shop"], car, under["created_at"])), under, car)

    # M3: six misread odometers, one in each of the last six quarters before T, at the shops in turn: three a digit
    # short, three a digit long, each on the car's last visit after an earlier one (orders.odometers applies them)
    by_car = collections.defaultdict(list)
    for o in sorted(b.orders.values(), key=lambda o: o["order"]["opened_at"]):
        by_car[id(o["order"]["vehicle_id"])].append(o)
    lasts = {id(group[-1]["order"]) for group in by_car.values() if len(group) > 1 and all(g["order"].get("mileage_in") is None and id(g["order"]) not in planted for g in group)}
    kinds = plan.deal(seed, ("misread",), 6, {"dropped": 1, "added": 1})
    for k, kind in enumerate(kinds):
        lo, hi = (dt.datetime.combine(clock.months_back(T.date(), 3 * n), T.time()) for n in (k + 1, k))
        pool = [o for site in plan.SITES for o in hosts(site) if lo < o["order"]["opened_at"] <= hi and id(o["order"]) in lasts]
        o = streams.pick(rng, [o for o in pool if o["site"] == plan.SITES[k % 3]] or pool)  # west only since its purchase
        used.add(id(o["order"]))
        o["misread"] = kind

    # M6 (s15.mess payments_not_one_to_one): one counter order paid in two parts, by card and in cash the same day,
    # and one refund by card against an order on which the customer was overcharged, with the card receipt's
    # reference. Their orders have no special-order part (no later wait moves them), the split one's payments written
    # here and its till close counting the cash; the overcharge (a share of the bill) and the parts are drawn
    # (a week and more before T: the refund comes up to a week after the payment, by T)
    shelf = [o for site in plan.SITES for o in hosts(site) if o["order"]["total"] > 0 and [p["kind"] for p in o["payments"]] == ["payment"] and o["order"]["opened_at"].date() < T.date() - dt.timedelta(9)
             and all(j["key"] in orders.STOCKED or not j["parts"] or j["status"] != "approved" for j in o["jobs"])]
    split, refunded = rng.sample(shelf, 2)
    for o in (split, refunded):
        used.add(id(o["order"]))
    ro, paid = split["order"], split["payments"][0]
    cash = (ro["total"] * Decimal(str(rng.uniform(0.2, 0.8)))).quantize(Decimal(1))
    split["pay"], split["payments"] = None, []
    orders.settle(b, split)
    orders.status(b, ro, "paid", paid["received_at"])
    b.add("payment", **dict(paid, amount=ro["total"] - cash))
    b.add("payment", **dict(paid, method="cash", amount=cash, reference=None))
    close = next(c for c in b.tables["cash_drawer_close"] if c["location_id"] is ro["location_id"] and c["business_date"] == paid["received_at"].date())
    close["expected_cash"] += cash
    close["counted_cash"] += cash
    paid = refunded["payments"][0]
    back = orders.opening(b, refunded["site"], paid["received_at"] + dt.timedelta(days=rng.randint(1, 7))) + rng.randrange(120) * orders.MINUTE
    b.add("payment", repair_order_id=refunded["order"], kind="refund", method="card", received_at=back, reference=paid["reference"],
          amount=(refunded["order"]["total"] * Decimal(str(rng.uniform(0.01, 0.1)))).quantize(orders.CENT),
          taken_by_id=b.people[(orders.advisors(b, refunded["site"], back.date()) or [orders.slot_of(b, refunded["order"]["advisor_id"])])[0]])

    # M7 (parts.typed_by_hand): per shop and month the share of part lines typed by hand, west's apart, none of them a
    # pad job's (story S6 counts the pads by their brand) nor a planted order's; the clerk's words: the slot name
    # without the part's number, its long words cut short, and half of them with two letters swapped; the brand left
    # out on half
    share = inputs.value("parts.typed_by_hand", cfg)
    lines = collections.defaultdict(list)
    for o in records:
        lines[o["site"], o["order"]["opened_at"].year, o["order"]["opened_at"].month] += [p for p in o["parts"] if id(o["order"]) not in planted]
    for key, group in lines.items():
        typed = sum(p["part_id"] is None for p in group)
        catalogue = [p for p in group if p["part_id"] is not None and p["order_job_id"]["canned_job_id"]["code"] not in orders.PADS]
        n = max(0, min(len(catalogue), round(len(group) * share["west" if key[0] == "west" else "home"] / 100) - typed))
        for p, (pick, how) in zip(catalogue, plan.deal(seed, ("typed", *key), len(catalogue), {(True, k): n / 4 for k in range(4)} | {(False, 0): len(catalogue) - n})):
            if not pick:
                continue
            words = [w[:4] + "." if len(w) > 5 and w.isalpha() else w for w in p["description"].replace(p["part_id"]["part_number"] or "\0", "").split()]
            if how % 2:
                i = max(range(len(words)), key=lambda i: len(words[i]))
                w = words[i]
                words[i] = w[:1] + w[2:3] + w[1:2] + w[3:] if len(w) > 3 else w
            p.update(part_id=None, description=" ".join(words), brand=None if how >= 2 else p["brand"])

    # M2: 3 % of the cars have no VIN: the named cars without one, then the oldest by model year (ties drawn); a
    # duplicate pair's two rows keep the same VIN, so a car sharing its VIN is passed over. (ru: the named ones, of 2007
    # and 2008, are younger than the oldest 3 %, against spec section 3's "they are old enough")
    cars = b.tables["vehicle"]
    shared = {v for v, n in collections.Counter(c["vin"] for c in cars).items() if n > 1}
    n = round(len(cars) * inputs.value("s15.mess", cfg)["vin_missing_pct"] / 100)
    order = sorted(cars, key=lambda c: (c["year"], rng.random()))
    gone = [c for c in order if c["vin"] is None]
    for c in order:
        if len(gone) >= n:
            break
        if c["vin"] is not None and c["vin"] not in shared:
            c["vin"] = None
            gone.append(c)
