"""Generator-spec section 4.8 and story S01: the six company accounts' visits by 30-day block, A2's Monday slot, the
orders S01 plants (nf.call.17, 21 to 25, nf.conv.04 and 05) and the accounts' declined estimates (`place`, before the
background fills every day around them); then the statements, their payments and the orders they pay (`bill`, after
the parts step, whose waits move the days an order is invoiced). Account orders stop at `invoiced` (`orders.order`
with `pay=None`); a paid statement adds `paid` to each of its orders.

`place` counts the account orders already in `b.orders` (S04's), so it runs after the other planted orders."""
import collections
import datetime as dt
import re
import string
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from seeder import clock, inputs, streams
from seeder.erp import background, customers, orders, plan

IDS = ("A1", "A2", "A3", "A4", "A5", "A6")
FLEET = ("maintenance", "brakes", "tyres_alignment")  # spec 4.8: the fleet jobs are fleet_pm_van, brakes and tyres
BLOCK, MINUTE, CENT = dt.timedelta(30), dt.timedelta(minutes=1), Decimal("0.01")
VAT = Decimal("1.05")
PM_HOLDS = ("oil_service", "engine_air_filter")  # catalogue.json fleet_pm_van: its oil and filters are part of the service  # tax.vat_divisor: an account's average is read before VAT
# kb.acct.approvers: A2's dispatcher and A4's instructor approve up to a limit, above it the president (en) or
# director (ru) and the owner; every other account its fleet contact in post that day, the first contact accounts.json
# lists for it. Indexes into the account's contacts.
APPROVERS = {"A2": (0, 1), "A4": (1, 0)}
# spec 4.8 and kb.acct.standing_instructions: the weekdays each account's visits come on (A2's others Wednesday to
# Friday, A4 booked Monday to Thursday, A6 back before Friday noon); A3's vans come in between opening and 30 minutes
WEEKDAYS = {"A2": (2, 3, 4), "A4": (0, 1, 2, 3), "A6": (0, 1, 2, 3)}


def block(T, at):
    """The 30-day block counted back from T that holds `at` (0 = the last 30 days), as checks.sql cuts them."""
    return (T - at) // BLOCK


def site_of(b, acct):
    return inputs.value(f"acct.{acct}.shop", b.cfg)


def joined(b, acct, car, day):
    """A4's cars with joined_fleet_months_before_t take orders only from that day (spec section 3, vehicle)."""
    f = next(f for x in customers.ACCOUNTS[b.cfg]["accounts"] if x["id"] == acct for f in x["fleet"] if f["unit"] == car["unit_number"])
    months = f.get("joined_fleet_months_before_t")
    return months is None or day >= clock.months_back(b.a["T"].date(), months)


def on_duty(b, site, day, slot):
    return slot in orders.advisors(b, site, day)


def next_day_of(b, site, slot, day):
    """`slot`'s first working day at `site` after `day`."""
    day += clock.DAY
    while not on_duty(b, site, day, slot):
        day += clock.DAY
    return day


def office(cfg, day):
    """A day the office books money: a weekday that is not a closed date."""
    return day.weekday() < 5 and not clock.closed(cfg, day)


def at_open(b, site, day, minutes=0):
    return orders.hours(b, site, day)[0] + minutes * MINUTE


def contact(b, acct, day, index):
    """The account's contact at `index` of accounts.json, or the first one in post on `day` (the fleet contact)."""
    rows = [c for c in b.tables["customer_contact"] if c["customer_id"] is b.accounts[acct]]
    if index is not None:
        return rows[index]["name"]
    return next(c for c in rows if c["started_on"] <= day and (c["ended_on"] is None or day <= c["ended_on"]))["name"]


def approver(b, acct, day, value):
    if acct not in APPROVERS:
        return contact(b, acct, day, None)
    below, above = APPROVERS[acct]
    limit = next(v for k, v in inputs.value("kb.acct.approvers", b.cfg)[acct].items() if k.endswith("_up_to"))
    return contact(b, acct, day, below if value <= limit else above)


def visit(acct, site, at, **more):
    return {"acct": acct, "site": site, "at": at, "car": None, "jobs": None, "advisor": None, "visit": True, "po": True, **more}


def job(key, **more):
    return {"key": key, "status": "approved", **more}


def stories(b):
    """Section 5, S01, and the new facts nf.call.17, 21 to 25 and nf.conv.04 and 05: the planted account orders, each
    with its day, car, jobs and the rest the cards fix."""
    cfg, a = b.cfg, b.a
    T, fleet, en = a["T"].date(), b.fleets, cfg == "en"
    calls = a["calls"]
    validity = inputs.value("kb.estimate_validity_days", cfg)
    last_open = clock.wd(cfg, T, -1)  # the last full open day before T
    out = []

    # A5: two pad jobs at west by slot 27 with the cheap brand, about three weeks before the Tuesdays of weeks T-26 and
    # T-22 (21 days back, moved to a full open day); the warranty comebacks on those Tuesdays, first look by slot 22;
    # the last visit on the Thursday of week T-20, closed the same day
    pad = "front_pads_rotors"
    for unit, back in zip(("E-2", "E-6") if en else ("Э-1", "Э-10"), a["a5_comebacks"]):
        day = clock.snap(cfg, back - dt.timedelta(21))
        first = visit("A5", "west", at_open(b, "west", day, 15), car=fleet["A5"][unit], jobs=[job(pad, tier="cheap", tech="27", keep=True)])
        out.append(first)
        out.append(visit("A5", "west", at_open(b, "west", back, 20), car=fleet["A5"][unit], visit=False, kind="warranty", first=first,
                         jobs=[job(pad, tier="cheap", tech="27", keep=True)]))
    out.append(visit("A5", "west", at_open(b, "west", a["a5_last_visit"]), last=True))

    # A6, call 21: SC-2's fleet PM at list on the call's day + 2, 07:30, booked by slot 5 on the call; ru car No 1 the
    # day after the call, its PM and a low-beam bulb, and its previous PM three months before
    day21 = calls[21]["day"]
    if en:
        day = clock.snap(cfg, day21 + dt.timedelta(2))
        out.append(visit("A6", "main", at_open(b, "main", day), car=fleet["A6"]["SC-2"], jobs=[job("fleet_pm_van", tier="standard")],
                         booking=("phone", dt.datetime.combine(day21, dt.time(11)), "5")))
    else:
        day = clock.snap(cfg, day21 + clock.DAY)
        out.append(visit("A6", "main", at_open(b, "main", day), car=fleet["A6"]["1"], jobs=[job("fleet_pm_van", tier="standard"), job("headlight_bulb", tier="standard")]))
        out.append(visit("A6", "main", at_open(b, "main", clock.snap(cfg, clock.months_back(day, 3))), car=fleet["A6"]["1"],
                         jobs=[job("fleet_pm_van", tier="standard", amount=Decimal("9500"))]))  # nf.call.21: the old hour as the call prices it

    # A6's five slow estimates after P (s1.a6): call 22's two-van estimate, sent two days late and expired; the web
    # chat's, expired on the earlier of its validity and the last full open day before T; three more in the blocks
    # after P, one approved two days or more after it was written (a visit), one declined by phone, one expired
    def expiring(day):
        return min(clock.snap(cfg, day + dt.timedelta(validity), -1), last_open)
    day22 = calls[22]["day"]
    jobs22 = ["front_pads_rotors", "rear_pads_rotors", "fleet_pm_van"] if en else ["front_pads_rotors", "fleet_pm_van"]
    out.append(visit("A6", "main", at_open(b, "main", day22, 150), car=fleet["A6"]["SC-4" if en else "2"], visit=False, advisor="7",
                     jobs=[job(k, tier="standard", status="declined", decided=at_open(b, "main", expiring(day22), 30)) for k in jobs22]))
    sent = a["a6_chat_sent"] if en else a["a6_chat_sent"] + clock.DAY  # ru: sent at 20:41, after closing; written the next morning
    out.append(visit("A6", "main", at_open(b, "main", sent, 120), car=fleet["A6"]["SC-9" if en else "8"], visit=False, advisor="7",
                     jobs=[job(k, tier="standard", status="declined", decided=at_open(b, "main", expiring(sent), 45)) for k in ("front_pads_rotors", "battery_replace")]))
    rng = streams.stream(b.seed, "a6 slow estimates")
    quoted = ("SC-4", "SC-5", "SC-9") if en else ("2", "5", "7", "8")  # the vans of call 22 and of the chat
    spare = [c for u, c in fleet["A6"].items() if u not in quoted and u != ("SC-2" if en else "1")]
    for n, (back, how) in enumerate(((115, "approved"), (128, "phone"), (100, "expired"))):  # days before T: blocks b2, b1, b2
        day = clock.snap(cfg, T - dt.timedelta(back))
        while day.weekday() > 3:
            day = clock.snap(cfg, day + clock.DAY)
        later = clock.wd(cfg, day, 2 + rng.randrange(2))
        decided = at_open(b, "main", expiring(day) if how == "expired" else later, 30 + rng.randrange(240))
        status = "approved" if how == "approved" else "declined"
        out.append(visit("A6", "main", at_open(b, "main", day, 60 + n * 20), visit=how == "approved", car=spare[n],
                         jobs=[job("front_pads_rotors", tier="standard", status=status, decided=decided, method="phone" if how != "expired" else None)]))

    # A1: calls 23 and 24. A day after a call that the shops are shut moves on to the first full open day (TIMELINE.md's
    # rule for a weekday of a week; a booking stays after its call), here and for A6's and A2's
    if en:
        out.append(visit("A1", "main", at_open(b, "main", clock.snap(cfg, calls[23]["day"] + clock.DAY)), car=fleet["A1"]["ND-22"], po=False,
                         jobs=[job("check_engine_diag", tier="standard")], booking=("phone", dt.datetime.combine(calls[23]["day"], dt.time(10)), "6")))
        day = clock.snap(cfg, calls[24]["day"] + dt.timedelta(2))
        out.append(visit("A1", "main", at_open(b, "main", day), car=fleet["A1"]["ND-08"], po="ND-60418",
                         jobs=[job("fleet_pm_van", tier="standard"), job("wheel_balance", tier="standard")],
                         booking=("phone", dt.datetime.combine(calls[24]["day"], dt.time(10)), "6")))
    else:
        out.append(visit("A1", "main", at_open(b, "main", clock.snap(cfg, calls[23]["day"] + clock.DAY)), car=fleet["A1"]["07"], po=False, jobs=[job("fleet_pm_van", tier="standard")]))
        day = calls[24]["day"]
        out.append(visit("A1", "main", dt.datetime.combine(day, dt.time(14)), car=fleet["A1"]["24"], po="247/10", jobs=[job("front_brake_pads", tier="standard")],
                         booking=("phone", dt.datetime.combine(day, dt.time(10)), "6")))

    # A2: call 25, the strut order of nf.conv.05 (en) and the water pump found leaking on a Monday slot (ru)
    day = clock.snap(cfg, calls[25]["day"] + clock.DAY)
    key, unit, po = ("front_pads_rotors", "M-112", "4471B") if en else ("clutch_kit", "Т-17", "118/11")
    out.append(visit("A2", "east", at_open(b, "east", day), car=fleet["A2"][unit], po=po, jobs=[job(key, tier="standard", approver=0)],
                     booking=("phone", dt.datetime.combine(calls[25]["day"], dt.time(12)), None)))
    if en:
        out.append(visit("A2", "east", at_open(b, "east", a["week_day"](-15, 0)), car=fleet["A2"]["M-112"], po="4398A", slot=True, amount=Decimal("1119.98"),
                         jobs=[job("front_struts_pair", tier="standard"), job("wheel_alignment", tier="standard")]))
    else:
        monday = a["week_day"](-16, 0)
        out.append(visit("A2", "east", at_open(b, "east", monday), car=fleet["A2"]["Т-09"], slot=True, leak=True,
                         jobs=[job("fleet_pm_van", tier="standard"), job("courtesy_inspection")]))
        out.append(visit("A2", "east", at_open(b, "east", next_day_of(b, "east", "16", monday), 30), car=fleet["A2"]["Т-09"], po="96/07", advisor="16",
                         amount=Decimal("12279.80"), jobs=[job("water_pump", tier="standard")]))
    for r in out:
        r["planted"] = True
    return out


def monday_lists(b):
    """nf.conv.05: the Monday lists of the weeks the chat names, week offset to its units."""
    text = inputs.value("nf.conv.05", b.cfg)[0]
    out = {}
    for week, units in re.findall(r"(?:week|неделя) (T-\d+|W\+\d+): ([^;.]*)", text):
        out[int(week[1:]) if week[0] == "W" else -int(week[2:])] = re.findall(r"[MТ]-\d+", re.sub(r"\(.*?\)", "", units))
    return out


def weekly_slot(b, rows):
    """acct.A2.weekly_slot: five vans at east every Monday at opening (a closed Monday moves to Tuesday), from the
    history's first week to the second week after T; the lists of nf.conv.05, otherwise the vans in turn. The visits
    up to T are orders with an arrived appointment, the later weeks booked or confirmed appointments; each booked by an
    east advisor on the Friday before at 12:00 or earlier (the list for a week after T was sent by T)."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    units = list(b.fleets["A2"])
    lists = monday_lists(b)
    planted = collections.defaultdict(list)
    for r in rows:
        if r.get("slot"):
            planted[r["at"].date() - dt.timedelta(r["at"].weekday())].append(r)
    turn, out = 0, []
    monday = a["history_start"] - dt.timedelta(a["history_start"].weekday())
    if monday < a["history_start"]:
        monday += dt.timedelta(7)
    while monday <= a["W0"] + dt.timedelta(14):
        day = monday if not clock.closed(cfg, monday) else monday + clock.DAY
        k = (monday - a["W0"]).days // 7
        have = planted[monday]
        named = [u for u in lists.get(k, []) if all(r["car"]["unit_number"] != u for r in have)]
        cars = [r["car"]["unit_number"] for r in have] + named
        while len(cars) < 5:
            u = units[turn % len(units)]
            turn += 1
            if u not in cars:
                cars.append(u)
        friday = monday - dt.timedelta(3)
        booked = dt.datetime.combine(friday, dt.time(12))
        while booked > T:
            booked -= dt.timedelta(7)
        booked -= streams.stream(b.seed, "a2 slot booked", monday).randrange(180) * MINUTE
        desk = orders.advisors(b, "east", booked.date()) or list(orders.ADVISORS["east"][:1])
        by = "16" if "16" in desk else desk[0]
        starts = at_open(b, "east", day)
        for n, u in enumerate(cars):
            r = next((r for r in have if r["car"]["unit_number"] == u), None)
            if starts <= orders.until(b, "east"):
                if r is None:
                    r = visit("A2", "east", starts + 2 * n * MINUTE, car=b.fleets["A2"][u], slot=True)
                    out.append(r)
                r["booking"] = ("messenger", booked, by)
                r["starts"] = starts
            else:
                out.append({"future": True, "car": b.fleets["A2"][u], "starts": starts, "booked": booked, "by": by})
        monday += dt.timedelta(7)
    return out


def generic(b, rows, existing):
    """Spec 4.8: every account's visits, exactly acct.<id>.visits in every 30-day block counted back from T (the first
    value for every block before T-150 days; the oldest block, cut by the history's start or west's purchase, in
    proportion), the planted ones and those already placed counted; spread over the block's open days that suit the
    account, at opening; A6's before F3 left on his days."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    out = []
    for acct in IDS:
        site, want = site_of(b, acct), inputs.value(f"acct.{acct}.visits", cfg)
        start = a["bought"] if site == "west" else a["history_start"]
        have = collections.Counter(block(T, r["at"]) for r in rows if r["acct"] == acct and r["visit"])
        have.update(block(T, at) for x, at in existing if x == acct)
        last = max((r["at"] for r in rows if r["acct"] == acct and r.get("last")), default=None)
        days = collections.defaultdict(list)
        day = start
        while day <= T.date():
            span = orders.hours(b, site, day)
            # (not the shop's last two open days before T's day: a fleet visit's work may not close by T, spec 4.5; none before the
            # account's record was made: west's came with the purchase)
            if (span and clock.full_open(cfg, day) and day.weekday() in WEEKDAYS.get(acct, range(7)) and span[0] <= orders.until(b, site)
                    and not day < T.date() <= orders.opening(b, site, orders.opening(b, site, span[1]) + dt.timedelta(days=1)).date()
                    and span[0] > b.accounts[acct]["created_at"]
                    and (last is None or span[0] < last) and not (acct == "A6" and day < b.people["F3"]["left_on"] and not on_duty(b, site, day, "F3"))):
                days[block(T, span[0])].append(day)
            day += clock.DAY
        oldest = block(T, at_open(b, site, start))
        rng = streams.stream(b.seed, "account visits", acct)
        for k in sorted(days):
            n = want[5 - k] if k < 5 else want[0]
            if k == oldest and k >= 5:
                n = round(want[0] * (T - BLOCK * k - at_open(b, site, start)) / BLOCK)
            n -= have[k]
            pool = days[k]
            offset = 0 if k == oldest else rng.random()
            picked = [pool[min(len(pool) - 1, int((i + offset) * len(pool) / n))] for i in range(n)] if n > 0 and pool else []
            for i, day in enumerate(picked):
                minutes = 5 * picked[:i].count(day) + rng.randrange(30 if acct == "A3" else 45)
                # (on the day a block begins, T's time of day minus k blocks: no later, so it stays in its block)
                out.append(visit(acct, site, min(at_open(b, site, day, minutes), T - BLOCK * k)))
    return out


def weights(b, r, kind, taken=()):
    """Jobs for an account order by their share of `kind` and season, offered on the car: a lead among the fleet jobs,
    an add-on among every priced job but the inspections."""
    p = {"vehicle": r["car"], "site": r["site"], "day": r["at"].date()}
    return {k: plan.SHARES[b.cfg][k][kind] * plan.curve(b.cfg, k, r["at"].date()) for k in plan.PRICED
            if (kind == "addon" or orders.JOBS[k]["category"] in FLEET) and k not in taken and k not in ("fleet_pm_van",) + orders.INSPECTING and plan.allowed(b, p, k)}


def value(b, r, jobs):
    """An order's money before tax, as acct.<id>.average_order reads it (ru: as billed / tax.vat_divisor)."""
    day = r["at"].date()
    for j in jobs:
        if "value" not in j:
            orders.price(b, day, b.accounts[r["acct"]], r["car"], j)
    labor, parts, sublet, fees, _ = orders.bill(b, jobs)
    gross = labor + parts + sublet + fees
    return gross if b.cfg == "en" else gross / VAT


def contents(b, rows):
    """The jobs of the visits no card fixes. The lead: fleet_pm_van on vans, so many a shop and month that it keeps its
    share_of_orders (lead and add-on) of the shop's month (volume.orders_per_month x season.total x its seasonal index, the planted
    ones counted; spec 4.3); otherwise a brake, tyre or maintenance job by its lead share and season. Then fleet add-ons
    (any priced job) by their add-on share until the account's running average comes to acct.<id>.average_order, none beyond its add-on
    share of the shop's month (the background's add-ons are dealt around them: a job keeps its share). Tiers: A3 economy
    (its standing instruction), the others standard (kb.worked_answers prices A1's maintenance there)."""
    cfg, a = b.cfg, b.a
    rng = streams.stream(b.seed, "account jobs")
    share = plan.SHARES[cfg]["fleet_pm_van"]["lead"] + plan.SHARES[cfg]["fleet_pm_van"]["addon"]
    months, volume, used = collections.defaultdict(list), {}, collections.Counter()
    for r in rows:
        months[r["site"], r["at"].year, r["at"].month].append(r)
    for (site, year, month), group in sorted(months.items()):
        first = dt.date(year, month, 1)
        length = ((first + dt.timedelta(32)).replace(day=1) - first).days
        start = a["bought"] if site == "west" else a["history_start"]
        inside = sum(1 for i in range(length) if start <= first + dt.timedelta(i) <= a["T"].date())
        volume[site, year, month] = inputs.value(f"volume.orders_per_month.{site}", cfg) * inputs.value("season.total", cfg)[month - 1] * inside / length
        quota = round(share * plan.month_curve(cfg, "fleet_pm_van", year, month) * volume[site, year, month])
        quota -= sum(1 for r in group if r["jobs"] and r["jobs"][0]["key"] == "fleet_pm_van")
        vans = [r for r in group if r["jobs"] is None and r["car"]["vehicle_class"] == "van"]
        for r in streams.stream(b.seed, "fleet pm", site, year, month).sample(vans, max(0, min(quota, len(vans)))):
            r["jobs"] = [job("fleet_pm_van")]
    for acct in IDS:
        target = Decimal(str(inputs.value(f"acct.{acct}.average_order", cfg)))
        tier = "economy" if acct == "A3" else "standard"
        # the account's average holds over the last 12 months (as acct.<id>.average_order reads it) and over the months
        # before: in each, the visits the cards fix count first, the others share what is left
        year = a["T"] - dt.timedelta(365)
        mine = sorted((r for r in rows if r["acct"] == acct and r["visit"]), key=lambda r: r["at"])
        for window in ([r for r in mine if r["at"] <= year], [r for r in mine if r["at"] > year]):
            fixed = [r for r in window if r.get("planted") and r["jobs"] is not None]
            left = target * len(window) - sum(value(b, r, [j for j in r["jobs"] if j["status"] == "approved"]) for r in fixed)
            free = [r for r in window if not (r.get("planted") and r["jobs"] is not None)]
            for n, r in enumerate(free):
                r["jobs"] = r["jobs"] or [job(customers.weighted(rng, weights(b, r, "lead")))]
                for j in r["jobs"]:
                    j.setdefault("tier", tier)
                wanted = left / (len(free) - n)
                v = value(b, r, r["jobs"])
                for _ in range(12):
                    if v >= wanted * Decimal("0.8"):
                        break
                    key = r["site"], r["at"].year, r["at"].month
                    pool = {k: w for k, w in weights(b, r, "addon", {j["key"] for j in r["jobs"]}).items()
                            if used[key, k] + 0.5 < plan.SHARES[cfg][k]["addon"] * plan.month_curve(cfg, k, *key[1:]) * volume[key]
                            and not (k in PM_HOLDS and any(j["key"] == "fleet_pm_van" for j in r["jobs"]))}
                    if not pool:
                        break
                    extra = job(customers.weighted(rng, pool), tier=tier)
                    more = value(b, r, r["jobs"] + [extra])
                    if more <= wanted * Decimal("1.25"):
                        r["jobs"].append(extra)
                        used[key, extra["key"]] += 1
                        v = more
                left -= v


def force(b, jobs, amount, whole=True):
    """A story amount as its ledger row or file states it (spec section 1, "Prices on a date"): the difference goes on
    a part line whose quantity divides it, else the share the first part line's quantity takes goes there and the odd
    cent is returned, for the order's shop-supplies fee (`write`): a labour line keeps hours x rate (D7). `whole`: the
    amount is the order's (en before tax, ru as billed), else the job's value."""
    diff = amount - (sum(orders.bill(b, jobs)[:4]) if whole else jobs[0]["value"])
    for j in jobs:
        for p in j["parts"]:
            if diff and (diff / p["quantity"]).quantize(CENT) * p["quantity"] == diff:
                p["unit_price"] += (diff / p["quantity"]).quantize(CENT)
                j["value"] += diff
                return 0
    if not diff:
        return 0
    j = next(j for j in jobs if j["parts"])
    share = (diff / j["parts"][0]["quantity"]).quantize(CENT, ROUND_DOWN)
    j["parts"][0]["unit_price"] += share
    j["value"] += share * j["parts"][0]["quantity"]
    return diff - share * j["parts"][0]["quantity"]


def book(b, rows):
    """Section 3, appointment: the account visits no card books and no slot holds come from a booking as any order does,
    erp.appointment.share_of_orders of them dealt per account, sources by erp.appointment.source (A2's others never by
    messenger: spec 4.8), at the drop-off slot the check-in kept (`background.slot_start`), booked a draw of
    erp.appointment.lead_days before by an advisor on duty that day."""
    cfg = b.cfg
    share = inputs.value("erp.appointment.share_of_orders", cfg)
    lead = inputs.value("erp.appointment.lead_days", cfg)
    for acct in IDS:
        mine = sorted((r for r in rows if r["acct"] == acct and r["visit"] and not r.get("planted") and not r.get("slot")), key=lambda r: r["at"])
        sources = {k: v for k, v in inputs.value("erp.appointment.source", cfg).items() if not (acct == "A2" and k == "messenger")}
        flags = plan.deal(b.seed, ("account bookings", acct), len(mine), {True: share, False: 100 - share})
        booked = [r for r, flag in zip(mine, flags) if flag]
        for r, source in zip(booked, plan.deal(b.seed, ("account sources", acct), len(booked), sources)):
            rng = streams.stream(b.seed, "account booking", acct, r["at"])
            hours = float(orders.sold_hours(cfg, r["jobs"][0]["key"], r["car"]))
            starts = background.slot_start(b, r["site"], r["at"], hours)
            if starts is None:
                continue
            day = starts.date() - dt.timedelta(plan.half_uniform(rng, lead))
            while orders.hours(b, r["site"], day) is None:
                day -= clock.DAY
            open_, close = orders.hours(b, r["site"], day)
            at = min(open_ + rng.randrange(int((close - open_).total_seconds() // 60)) * MINUTE, starts - MINUTE)
            r["booking"], r["starts"] = (source, at, streams.pick(rng, orders.advisors(b, r["site"], day) or [r["advisor"]])), starts


def place(b):
    cfg, a = b.cfg, b.a
    T = a["T"]
    rows = stories(b)
    future = weekly_slot(b, rows)
    rows += [r for r in future if not r.get("future")]
    existing = [(x, o["order"]["opened_at"]) for o in b.orders.values() for x in IDS
                if o["order"]["customer_id"] is b.accounts[x] and o["order"]["order_type"] == "customer_pay" and o["order"]["status"] not in ("declined", "void")]
    rows += generic(b, rows, existing)

    # the cars in turn, the advisors on duty by their order shares (A6's F3 while he worked, A2's slot slot 16 when on
    # shift, else slot 17)
    turn = collections.Counter()
    one = sorted(r["at"].date() for r in rows if r.get("planted") and cfg == "ru" and r["car"] is b.fleets["A6"]["1"])
    for r in sorted(rows, key=lambda r: r["at"]):
        day, site, acct = r["at"].date(), r["site"], r["acct"]
        if r["car"] is None:  # (ru A6's car No 1 has no service between its two planted ones: nf.call.21)
            units = [c for c in b.fleets[acct].values() if joined(b, acct, c, day) and not (one and c is b.fleets["A6"]["1"] and one[0] <= day <= one[-1])]
            r["car"] = units[turn[acct] % len(units)]
            turn[acct] += 1
        if r["advisor"] is None:
            on = orders.advisors(b, site, day) or list(orders.ADVISORS[site][:1])
            if acct == "A6" and day < b.people["F3"]["left_on"] and "F3" in on:
                r["advisor"] = "F3"
            elif r.get("slot"):
                r["advisor"] = "16" if "16" in on else on[0]
            else:
                split = {s: w for s, w in plan.shares(b, site, day).items() if s in on}
                r["advisor"] = customers.weighted(streams.stream(b.seed, "account advisor", acct, r["at"]), split) if split else on[0]
    contents(b, rows)
    book(b, rows)

    # erp.estimate.declined_share: 2 % of the estimates of A1 to A5 end declined, dealt over their visits; written at
    # check-in on a visit's day (spec section 7, S1.6: no account's estimate but A6's waits two days)
    rng = streams.stream(b.seed, "account declined")
    hosts = [r for r in rows if r["acct"] != "A6" and r["visit"] and not r.get("last")]  # S1.2: A5's last visit stays its last order
    rate = inputs.value("erp.estimate.declined_share", cfg)["accounts_on_terms"] / 100
    for host in sorted(rng.sample(hosts, round(len(hosts) * rate / (1 - rate))), key=lambda r: r["at"]):
        at = min(host["at"] + (30 + rng.randrange(120)) * MINUTE, orders.hours(b, host["site"], host["at"].date())[1] - 30 * MINUTE)
        if at > orders.until(b, host["site"]):
            continue
        rows.append(visit(host["acct"], host["site"], at, car=host["car"], advisor=host["advisor"], visit=False,
                          jobs=[job(customers.weighted(rng, weights(b, host, "lead")), status="declined", decided=at + rng.randrange(16) * MINUTE, method="counter",
                                    tier="economy" if host["acct"] == "A3" else "standard")]))

    for r in sorted(rows, key=lambda r: r["at"]):
        write(b, r)
    for x in future:
        if x.get("future"):
            b.add("appointment", location_id=b.shops["east"], customer_id=b.accounts["A2"], vehicle_id=x["car"], starts_at=x["starts"],
                  duration_min=60, source="messenger", status="confirmed" if x["starts"] - T <= dt.timedelta(2) else "booked",
                  reason=orders.JOBS["fleet_pm_van"][cfg]["name"], booked_at=x["booked"], booked_by_id=b.people[x["by"]])


def write(b, r):
    """One planted or account order through `orders.order`, billed on terms (`pay=None`): its mechanic one on duty,
    drawn by pNN.billed_index so the background can still bring each to his row (a card's own where it names one), its
    approver, its customer's own order number (spec section 1), its booking."""
    cfg, site, acct, day = b.cfg, r["site"], r["acct"], r["at"].date()
    customer, rng = b.accounts[acct], streams.stream(b.seed, "account order", acct, r["at"])
    crew = orders.mechanics(b, site, day) or orders.mechanics(b, site, orders.opening(b, site, r["at"] + dt.timedelta(1)).date())
    staying = [(s, p) for s, p in crew if p["left_on"] is None] or crew  # a leaving mechanic's days are the background's (his rows)
    free = dict(staying)[customers.weighted(rng, {s: inputs.value(plan.slot_key(s, "billed_index"), cfg) for s, _ in staying})]
    for j in r["jobs"]:
        j["tech"] = b.people[j["tech"]] if isinstance(j.get("tech"), str) else free
        j.setdefault("tier", "economy" if acct == "A3" else "standard")
        if "value" not in j:
            orders.price(b, day, customer, r["car"], j)
        if j["status"] == "approved" and j["key"] != "courtesy_inspection":
            j["authorized_by"] = contact(b, acct, day, j.pop("approver")) if "approver" in j else approver(b, acct, day, j["value"])
    if r.get("amount"):
        odd = force(b, r["jobs"], r["amount"])
    for j in r["jobs"]:
        if j.get("amount"):
            force(b, [j], j.pop("amount"), whole=False)
    booking = None
    if r.get("booking"):
        source, booked, by = r["booking"]
        by = by or (orders.advisors(b, site, booked.date()) or [r["advisor"]])[0]
        hours = float((r["jobs"][0]["labor"] or {}).get("hours", 0.5))
        booking = {"source": source, "booked_at": booked, "booked_by": by, "starts_at": r.get("starts", r["at"]), "duration": max(30, -(-int(hours * 60) // 30) * 30)}
    first = r.get("first", {}).get("order")
    ro = orders.order(b, site, r["at"], customer, r["car"], r["advisor"], r["jobs"], kind=r.get("kind", "customer_pay"), comeback_of=first, pay=None,
                      booking=booking)
    r["order"] = ro
    record = b.orders[id(ro)]
    if acct == "A5":
        record["planted"] = True  # A5 left after its two comebacks (s1.a5): no other comeback is dealt to its orders
    ro["purchase_order_number"] = r["po"] if isinstance(r["po"], str) else None
    record["no_po"] = r["po"] is False  # call 23's order: opened with no purchase-order number
    if r.get("amount") and odd:  # the cent no part quantity takes: on the shop-supplies fee, within the rule's cent (price.supplies.rate)
        fee = next(f for f in record["fees"] if f["kind"] == "shop_supplies")
        fee["amount"] += odd
        ro["fees_total"] += odd
        gross = ro["labor_total"] + ro["parts_total"] + ro["sublet_total"] + ro["fees_total"] - ro["discount_total"]
        if cfg == "ru":
            ro.update(total=gross, tax_total=gross - (gross / (1 + ro["tax_rate"] / 100)).quantize(CENT, ROUND_HALF_UP))
        else:
            ro["tax_total"] = (gross * ro["tax_rate"] / 100).quantize(CENT, ROUND_HALF_UP)
            ro["total"] = gross + ro["tax_total"]
    if r.get("leak"):  # nf.conv.05 (ru): the inspection finds the water pump leaking; the promised call was not made, so no job
        g = orders.group("water_pump")
        item = next(i for i in record["items"] if i["component"] == orders.GROUPS[cfg][g])
        item.update(component=f"{orders.GROUPS[cfg][g]}: {orders.JOBS['water_pump'][cfg]['parts'][0]['name']}", result="bad",
                    measurement=orders.reading(cfg, "water_pump", "bad", rng), has_photo=True)


def bill(b):
    """Spec 4.8. en: on the first full open day of each month one statement per account for its orders invoiced in the
    month before (an order alone in its month waits for the next one: every statement holds more than one order, M6),
    due after the account's terms; one payment settles it, by cheque or transfer, on the day acct.A1.days_to_pay,
    erp.statement.pay_day or the dispute gives. ru: one invoice per closed order, issued the day it closed or the next
    working day; once, one invoice for three orders of A3 in a month (M6); A1 by its row's formula, the others inside
    their terms. The disputed bill (S01) is the one holding the order of A5's second comeback, unpaid. Paid bills put
    their orders at paid."""
    cfg, a = b.cfg, b.a
    T = a["T"]
    # spec section 1: every order of A1 and A2 carries the customer's own order number (ru A2's none but the cards'),
    # comebacks included, call 23's aside; drawn without replacement, never one a card plants
    rng = streams.stream(b.seed, "customer order numbers")
    taken = {o["order"]["purchase_order_number"] for o in b.orders.values()}
    for o in sorted(b.orders.values(), key=lambda o: o["order"]["opened_at"]):
        ro = o["order"]
        acct = next((x for x in ("A1", "A2") if ro["customer_id"] is b.accounts[x]), None)
        if acct is None or ro["purchase_order_number"] or o.get("no_po") or cfg == "ru" and acct == "A2":
            continue
        number = None
        while number is None or number in taken:
            number = (f"ND-6{rng.randrange(10 ** 4):04d}" if acct == "A1" else f"{rng.randrange(1000, 10 ** 4)}{streams.pick(rng, string.ascii_uppercase)}") \
                if cfg == "en" else f"{rng.randrange(1, 400)}/{ro['opened_at'].month:02d}"
        taken.add(number)
        ro["purchase_order_number"] = number
    pay_day = inputs.value("erp.statement.pay_day", cfg)
    days_a1 = inputs.value("acct.A1.days_to_pay", cfg)
    disputed = {id(o["order"]["comeback_of_id"]) for o in b.orders.values() if o["order"]["comeback_of_id"] is not None
                and o["order"]["customer_id"] is b.accounts["A5"] and o["order"]["opened_at"].date() == a["a5_comebacks"][1]}
    note = "Disputes the E-6 pad job: came back in three weeks" if cfg == "en" else "Оспаривает работы по Э-10: колодки вернулись через три недели"
    rank = {id(row): n for n, (_, _, row) in enumerate(sorted((c["created_at"], i, c) for i, c in enumerate(b.tables["customer"])), 1)}
    bills = []  # (account, issued, [orders])
    for acct in IDS:
        mine = []
        for o in b.orders.values():
            ro = o["order"]
            invoiced = next((h["changed_at"] for h in o["history"] if h["status"] == "invoiced"), None)
            if ro["customer_id"] is b.accounts[acct] and ro["order_type"] == "customer_pay" and invoiced and ro["status"] != "void":
                mine.append((invoiced, ro))
        mine.sort(key=lambda x: x[0])
        if cfg == "en":
            carry = []
            for (year, month), group in sorted(collections.Counter((t.year, t.month) for t, _ in mine).items()):
                group = carry + [ro for t, ro in mine if (t.year, t.month) == (year, month)]
                issued = clock.snap(cfg, (dt.date(year, month, 1) + dt.timedelta(32)).replace(day=1))
                if issued > T.date():
                    break
                if len(group) < 2:
                    carry = group
                    continue
                carry = []
                bills.append((acct, issued, group))
        else:
            a3 = [ro for t, ro in mine if acct == "A3" and (T - t).days > 90]
            months = collections.defaultdict(list)
            for ro in a3:
                months[ro["opened_at"].year, ro["opened_at"].month].append(ro)
            combined = next((group[:3] for _, group in sorted(months.items(), reverse=True) if len(group) >= 3), [])
            rng = streams.stream(b.seed, "invoices", acct)
            for t, ro in mine:
                if any(ro is x for x in combined[1:]):
                    continue
                group = combined if ro is (combined or [None])[0] else [ro]
                last = max(next(h["changed_at"] for h in b.orders[id(x)]["history"] if h["status"] == "invoiced") for x in group).date()
                issued = last if rng.random() < 0.5 else clock.snap(cfg, last + clock.DAY)
                if issued <= T.date():
                    bills.append((acct, issued, group))
    bills.sort(key=lambda x: (x[1], IDS.index(x[0])))

    a1 = [x for x in bills if x[0] == "A1"]
    if cfg == "en":  # the newest A1 statement that can be paid in 51 days by T - 1 day in 51, the two before in 44 and 38
        n = sum(1 for _, issued, _ in a1 if issued + dt.timedelta(days_a1["last_three_paid"][-1]) <= T.date() - clock.DAY)
    for i, (acct, issued, group) in enumerate(bills):
        rng = streams.stream(b.seed, "statement", acct, issued, i)
        terms = inputs.value(f"acct.{acct}.terms_days", cfg)
        dispute = any(id(ro) in disputed for ro in group)
        # the days to pay: a range the row allows, or one figure; the money arrives on an office day (a weekday not a closed
        # date), a figure's day moved on to the next one (acct.A1.days_to_pay reads it within three days)
        if dispute:
            days = None
        elif acct == "A1" and cfg == "en":
            k = next(j for j, x in enumerate(a1) if x[1] == issued)
            days = [days_a1["last_three_paid"][k - n + 3]] if n - 3 <= k < n else None if k >= n else range(days_a1["until"] - 2, days_a1["until"] + 3)
        elif acct == "A1":
            x = (T.date() - issued).days
            days = None if x < 60 else [round(days_a1["until"] + (days_a1["late"] - days_a1["until"]) * (150 - min(x, 150)) / 90)]
        else:
            days = range(pay_day[acct] - pay_day["spread"], pay_day[acct] + pay_day["spread"] + 1)
        received = None
        if days is not None:
            # (a range's day before T's date: the office's books for T's day are not closed at T)
            choice = [d for d in (issued + dt.timedelta(k) for k in days) if office(cfg, d)]
            day = streams.pick(rng, [d for d in choice if d < T.date()] or [d for d in choice if d > T.date()] or choice or [issued + dt.timedelta(days[-1])])
            while not office(cfg, day):
                day += clock.DAY
            received = dt.datetime.combine(day, dt.time(10)) + rng.randrange(300) * MINUTE
            if day == T.date():  # due on T's own day: in by T
                received = min(received, T - MINUTE)
            if received > T:
                received = None
        due = issued + dt.timedelta(terms)
        total = sum(ro["total"] for ro in group)
        statement = b.add("statement", customer_id=b.accounts[acct], issued_on=issued, due_on=due, total=total,
                          status="paid" if received else "overdue" if T.date() > due else "sent", dispute_note=note if dispute else None)
        # spec section 1: en the month billed (the one before the issue) and the account's id; ru a running number
        statement["number"] = f"ST-{issued.replace(day=1) - clock.DAY:%Y%m}-{rank[id(b.accounts[acct])]}" if cfg == "en" else f"СЧ-{i + 1:06d}"
        for ro in group:
            ro["statement_id"] = statement
            if received:
                orders.status(b, ro, "paid", received)
        if received:
            b.add("payment", repair_order_id=None, statement_id=statement, kind="payment",
                  method="bank_transfer" if cfg == "ru" or rng.random() < 0.5 else "check", amount=total, received_at=received, taken_by_id=None,
                  reference=f"{rng.randrange(10 ** 6):06d}")
