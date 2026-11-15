"""The order builder of generator-spec.md: `order` writes one repair order and every row under it (sections 3 and 4.3
to 4.7) from a plain description, priced by section 1 ("Prices on a date", "Tax", "Shop supplies", "Money"), its work
booked on the mechanics' days. The background fill calls it with drawn content; a story calls it with fixed content.
Everything an order owns is kept in `b.orders[id(order)]`; its history, time entries and payments stay there (a later
step may still move them: `wait`, `status`) until `finish` writes them, numbers the orders and reads the odometers.

A job of the description is a dict: `key` (catalogue job), `status` (approved, declined, pending), `tech` (the mechanic
meant to do it; on a declined job only the order's inspector), `tier` (economy, standard, premium, or `cheap` for the
S6 pad), `found` (bad or watch: raised from the inspection, with `reading` and `photo` for its item), `method` and
`decided` (the decision; drawn inside the approval window when left out), `authorized_by`, `hours` (a story's sold
hours), `clocked` (a story's minutes on the clock), `split` (begun late, its work runs on to the next day), `keep`
(the work stays with `tech`, even on a later day; "held": however long he has no room). `price` adds its priced lines to
it."""
import bisect
import collections
import datetime as dt
import functools
import re
from decimal import ROUND_HALF_UP, Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers, reference

JOBS = {j["key"]: j for j in reference.CATALOGUE["jobs"]}
PADS = tuple(reference.CATALOGUE["story_pins"]["S6"]["jobs"])
INSPECTING = ("courtesy_inspection", "brake_inspection", "pre_purchase_inspection")  # spec section 3, inspection
CENT, ZERO, MINUTE = Decimal("0.01"), Decimal(0), dt.timedelta(minutes=1)
TEXTS = inputs.load("erp/texts.json")
WEEKDAY = {cfg: tuple(tuple(map(int, x.split(":"))) for x in inputs.value("site.hours.weekday", cfg)) for cfg in ("en", "ru")}
PROMISE = {"en": dt.time(17), "ru": dt.time(18)}  # spec section 3, repair_order.promised_at
SUBLET = {"transmission_rebuild": ("V6", "transmission_rebuild_working_days", "gearbox_rebuild_working_days"),
          "steering_rack": ("V9", None, "steering_rack_working_days")}  # spec section 3, order_sublet; kb.sublet_times
# erp.stock.stocked_jobs: the jobs whose parts come from the shelf; every other part is a special order
STOCKED = tuple(k for k in inputs.value("erp.stock.stocked_jobs", "en") if k in JOBS)
FEE = {"new_tyres_fitted": "tyre_disposal", "tyre_storage": "tyre_storage"}  # spec section 3, order_fee
# the people of cast.json by what they do at each shop: advisors write orders (slot 22, the shop manager, writes none),
# mechanics do the work (slot 21 also at main, cast.json also_sites); F4 is one employee row per season (b.seasons)
ADVISORS = {s: tuple(p["slot"] for p in reference.CAST["people"] if p["site"] == s and p["role_key"] in ("lead_advisor", "service_advisor"))
            for s in ("main", "east", "west")}
MECHANICS = {s: tuple(p["slot"] for p in reference.CAST["people"] if p["slot"] != "F4" and (p["site"] == s or s in (p.get("also_sites") or ()))
                      and (p["role_key"].endswith("technician") or p["role_key"] == "technician")) for s in ("main", "east", "west")}
# roster.mechanic_pattern: the mechanics' shift; en main's Saturday crews (roster.saturday) work its Saturday hours
SHIFT = {cfg: tuple(tuple(map(int, x)) for x in re.findall(r"(\d\d):(\d\d)", inputs.value("roster.mechanic_pattern", cfg)))[:2] for cfg in ("en", "ru")}
_saturday = inputs.value("roster.saturday", "en")
CREWS = tuple(tuple(re.findall(r"\d+", crew)) for crew in re.search(r"crews ([\d, ]+) and ([\d, ]+) on", _saturday).groups())
TURN = tuple(re.findall(r"\d+", _saturday.split(" in turn")[0]))  # the advisors who take main's Saturday with slot 29 in turn
# roster.advisor_pattern (ru): 6, 29, 17 and 24 on phase B; F1 follows slot 24's phase and F3 slot 7's (spec section 7b)
PHASE_B = {str(s) for s in clock.PHASE_B} | {"F1"}
# s5.days_off_so_far (en): slot 16 is off on the Fridays of these weeks T-k and on the Mondays after them
DAYS_OFF_16 = tuple(int(k) for k in re.findall(r"T-(\d+)", inputs.value("s5.days_off_so_far", "en")["when"]))
DIAGNOSTICIAN = {p["site"]: (p["slot"], n) for k, n in inputs.value("kb.schedule.diagnostics_and_weekends", "en").items()
                 if (m := re.fullmatch(r"slot_(\d+)_diagnostic_jobs_a_day", k)) for p in reference.CAST["people"] if p["slot"] == m[1]}
# the courtesy inspection's eleven groups (spec section 3, inspection_item); the Russian names are the page's own words;
# READINGS names each group in texts.json
GROUPS = {"en": ("Tires", "Brake pads", "Lights", "Wipers", "Battery", "Belts and hoses", "Fluids and filters", "Leaks underneath",
                 "Shocks and struts", "CV boots", "Exhaust")}
_page = re.search(r"## Что смотреть\n\n(.*?)\n", (inputs.SEED / "kb/ru/shop-floor/courtesy-inspection.md").read_text(encoding="utf-8"))[1]
_first, _second, _rest = _page.rstrip(".").split(". ")[:3]
GROUPS["ru"] = tuple(w[0].upper() + w[1:] for w in [_first.split(":")[0], _second.split(" —")[0], *_rest.split(", ")])
assert len(GROUPS["ru"]) == 11, GROUPS["ru"]
READINGS = ("tyres", "brake pads", "lights", "wipers", "battery", "belts and hoses", "fluids and filters", "leaks underneath",
            "shocks and struts", "CV boots", "exhaust")
# spec section 4.3: the group of a raised job, by category, then by job where the list names one
GROUP_OF = {"brakes": 1, "tyres_alignment": 0, "suspension_steering": 8, "battery_electrical": 4, "maintenance": 6, "engine_cooling": 5,
            "transmission_driveline": 7, "air_conditioning": 5}
GROUP_OF_JOB = {"brake_fluid_exchange": 6, "headlight_bulb": 2, "wiper_blades": 3, "spark_plugs": 5, "drive_belt": 5, "exhaust_muffler": 10,
                "valve_cover_gasket": 7, "cv_axle": 9, "electrical_diag": 4, "suspension_diag": 8, "cooling_pressure_test": 5}


def group(key):
    return GROUP_OF_JOB.get(key, GROUP_OF.get(JOBS[key]["category"]))


def reading(cfg, key, result, rng):
    """texts.json readings for the job's group and result (brake_fluid_exchange reads "brake fluid")."""
    return streams.pick(rng, TEXTS[cfg]["readings"]["brake fluid" if key == "brake_fluid_exchange" else READINGS[group(key)]][result])


def in_post(p, day):
    return p["hired_on"] <= day and (p["left_on"] is None or day < p["left_on"])


@functools.lru_cache(maxsize=None)
def _hours(cfg, site, day):
    if not (clock.main_open if site == "main" else clock.full_open)(cfg, day):
        return None
    span = clock.EN_SATURDAY if cfg == "en" and day.weekday() == 5 else WEEKDAY[cfg]
    return tuple(dt.datetime.combine(day, dt.time(*x)) for x in span)


def hours(b, site, day):
    """The shop's opening and closing on `day` (spec section 1), or None when it is shut."""
    return _hours(b.cfg, site, day)


def opening(b, site, t):
    """t when the shop is open then, else its next opening."""
    day = t.date()
    while True:
        span = hours(b, site, day)
        if span and t < span[1]:
            return max(t, span[0])
        day += clock.DAY
        t = dt.datetime.combine(day, dt.time())


def until(b, site):
    """T on the shop's own clock (spec section 1): west reads T - geo.zone_gap_hours."""
    return b.a["T"] - dt.timedelta(hours=inputs.value("geo.zone_gap_hours", b.cfg) if site == "west" else 0)


def decides(b, site, opened):
    """Whether an order's raised jobs are decided by T: an order of an earlier day, or one of T's day that came in two
    hours or more before T; a later one's are still with the customer at T."""
    T = until(b, site)
    return opened.date() < T.date() or opened + dt.timedelta(hours=2) <= T


@functools.lru_cache(maxsize=None)
def _weekly(seed, name, year, week, k):
    """k of the five weekdays (0 = Monday), drawn once per week for a roster with a share and no day (spec section 7b)."""
    return frozenset(streams.stream(seed, name, year, week).sample(range(5), k))


def advisors(b, site, day):
    """The slots of the advisors who write orders at `site` on `day` (roster.advisor_pattern), in post. en: weekdays;
    main's Saturday morning slot 29 and one of roster.saturday's advisors in turn; slot 29 covers two or three weekdays
    a week from F3's leaving to slot 7's start (spec section 7b). ru: two on, two off by phase, counted from T."""
    if hours(b, site, day) is None:
        return []
    on = [s for s in ADVISORS[site] if in_post(b.people[s], day)]
    if b.cfg == "en" and site == "east" and day in {b.a["week_day"](w, d) for k in DAYS_OFF_16 for w, d in ((-k, 4), (1 - k, 0))}:
        on.remove("16")
    if b.cfg == "ru":
        phase_b = (day - b.a["T"].date()).days % 4 in (0, 1)
        return [s for s in on if (s in PHASE_B) == phase_b]
    year, week, weekday = day.isocalendar()
    if weekday == 6:
        turn = [s for s in TURN if s in on]
        return [s for s in on if s == "29"] + [turn[week % len(turn)]]
    gap = b.people["F3"]["left_on"] <= day < b.people["7"]["hired_on"]
    cover = gap and weekday - 1 in _weekly(b.seed, "slot 29 covers", year, week, 2 + streams.stream(b.seed, "slot 29 cover days", year, week).randrange(2))
    return [s for s in on if s != "29" or cover]


def mechanics(b, site, day):
    """The mechanics working at `site` on `day` (roster.mechanic_pattern; spec sections 4.2 and 7b), as (slot, employee
    row). en: weekdays; slot 21 is at main one weekday a week and slot 28 works three, drawn per week; main's Saturday
    crews alternate. ru: roster.mechanic_days_off (F2 had slot 14's); slot 15 works a sixth day, his Saturday, inside the
    tyre windows (season.extra_shifts); the seasonal helper is off on Sunday. Slot 10 is away in s5.leave."""
    if hours(b, site, day) is None:
        return []
    cfg, a = b.cfg, b.a
    year, week, weekday = day.isocalendar()
    name = clock.WEEKDAYS[weekday - 1][:3]
    window = cfg == "ru" and any(f <= f"{day.month:02d}-{day.day:02d}" <= t for f, t in inputs.value("season.tyre.windows", "ru"))
    out = []
    for s in MECHANICS[site]:
        p = b.people[s]
        if not in_post(p, day) or s == "10" and a["leave_from"] <= day <= a["leave_to"]:
            continue
        if cfg == "en":
            if weekday == 6:
                works = site == "main" and s in CREWS[week % 2]
            elif s == "21":
                works = (weekday - 1 in _weekly(b.seed, "slot 21 at main", year, week, 1)) == (site == "main")
            elif s == "28":
                works = weekday - 1 in _weekly(b.seed, "slot 28 days", year, week, 3)
            else:
                works = weekday < 6
        else:
            text = inputs.value("roster.mechanic_days_off", "ru")["14" if s == "F2" else s]
            if text.startswith("works"):
                works = name in text
            else:
                works = (name not in text.split("(")[0] or s == "15" and window and name == "Sat") and (s != "21" or (name == "Tue") == (site == "main"))
        if works:
            out.append((s, p))
    for p in b.seasons:
        if site == "main" and in_post(p, day) and (weekday < 6 if cfg == "en" else weekday < 7):
            out.append(("F4", p))
    return out


def slot_of(b, row):
    return next((s for s, p in b.people.items() if p is row), "F4")


def shift(b, site, day):
    """A mechanic's day at the shop: roster.mechanic_pattern's shift, en main's Saturday its opening hours."""
    if b.cfg == "en" and day.weekday() == 5:
        return hours(b, site, day)
    return tuple(dt.datetime.combine(day, dt.time(*x)) for x in SHIFT[b.cfg])


def clocked(b, job):
    """Minutes on the clock for a job's sold hours (erp.time.clocked_over_sold)."""
    factor = inputs.value("erp.time.clocked_over_sold", b.cfg)
    return job.get("clocked") or max(1, round(float(job["labor"]["hours"]) * factor.get(f"slot {slot_of(b, job['tech'])}", factor["everyone"]) * 60))


def free(b, tech, day, t, end, need):
    """The first minute at or after t from which `tech` is free for `need` on `day` before `end`, or None."""
    for s, e in b.timeline.get((id(tech), day), ()):
        if e <= t:
            continue
        if t + need <= s:
            break
        t = max(t, e)
    return t if t + need <= end else None


def book(b, site, ready, minutes, tech, keep=False, waits=(), due=None, split=False):
    """Books a job of `minutes` ready at `ready` on a mechanic's day (spec section 3, time_entry): from the next free
    minute of `tech` on one of his next three days at the shop (none after `due`), else of another mechanic on duty with
    room, day by day; with `keep` only that mechanic for a week (an order of an earlier day: until T's day), once begun only
    that mechanic. The clock stops for each (from, to) of `waits`. A
    job longer than a shift takes his whole days; with `split` (a story's job begun late) its first piece runs from the
    start to the shift's end and the rest the next day. Returns the mechanic and the pieces [(start, end)]."""
    if not keep:
        t, worked = ready, 0
        while worked < 3 and (due is None or t.date() <= due):
            day = t.date()
            if any(r is tech for _, r in mechanics(b, site, day)):
                worked += 1
                start, end = shift(b, site, day)
                if free(b, tech, day, max(t, start), end, dt.timedelta(minutes=min(minutes, int((end - start).total_seconds() // 60)))):
                    keep = True
                    break
            t = dt.datetime.combine(day + clock.DAY, dt.time())
    pieces, left, t = [], minutes, ready
    for _ in range(2000):
        if left <= 0:
            return tech, pieces
        day = t.date()
        crew = [r for _, r in mechanics(b, site, day)]
        if keep and not pieces and due and day >= due and any(r is tech for r in crew):
            start, end = shift(b, site, day)
            mine = free(b, tech, day, max(t, start), end, dt.timedelta(minutes=min(left, int((end - start).total_seconds() // 60))))
        else:
            mine = None
        if keep and not pieces and (tech["left_on"] and day >= tech["left_on"] or (day - ready.date()).days > 7 and keep != "held" or due and day >= due and not mine):
            keep = False  # he left, or has had no room at the shop for a week, or none before T's day: whoever is on duty does it
        names = ([tech] if any(r is tech for r in crew) else []) + ([] if keep or pieces else [r for r in crew if r is not tech])
        if due and not keep and not pieces and crew:  # an order of an earlier day: whoever finishes first, so it closes by T
            start, end = shift(b, site, day)
            need = dt.timedelta(minutes=min(left, int((end - start).total_seconds() // 60)))
            names.sort(key=lambda r: free(b, r, day, max(t, start), end, need) or dt.datetime.max)
        for r in names:
            start, end = shift(b, site, day)
            need = dt.timedelta(minutes=min(left, int((end - start).total_seconds() // 60)))
            if split and not pieces and end > max(t, start):
                need = min(need, end - max(t, start))
            # work that stops for a wait needs room only up to the wait (a car begun and left waiting for its part)
            cut = next((since for since, _ in waits if max(t, start) < since < max(t, start) + need), None)
            s = free(b, r, day, max(t, start), end, min(need, cut - max(t, start)) if cut else need)
            if s is None:
                continue
            inside = next((till for since, till in waits if since <= s < till), None)
            if inside:  # waiting for parts: nothing is done until they come
                t = inside
                break
            e = next((since for since, till in waits if s < since < s + need), s + need)
            bisect.insort(b.timeline.setdefault((id(r), day), []), (s, e))
            pieces.append((s, e))
            left -= int((e - s).total_seconds() // 60)
            tech, keep = r, True
            t = next((till for since, till in waits if since == e), e)
            break
        else:
            t = dt.datetime.combine(day + clock.DAY, dt.time())
    raise ValueError(f"no mechanic at {site} has room for {minutes} minutes from {ready} ({slot_of(b, tech)}, keep {keep})")


def period(b, day):
    """The index of the labour-price period in force on `day` (price.hour.history; its first day the history start)."""
    a = b.a
    starts = {"P": a["P"], "the first full open day on or after T-335 days": a["s2_start"], "the first open day on or after T-18 months": a["ru_rise"]}
    return sum(day >= starts[when] for when, _ in inputs.value("price.hour.history", b.cfg)[1:])


def drifted(b, amount, day, list_price=True):
    """A part, fee or sublet price on `day`: today's from G, before G today's x (1 - price.parts_drift_year) ^ years."""
    if day >= b.a["G"]:
        return amount
    years = (b.a["G"] - day).days / 365.25
    return reference.money(b.cfg, amount, (1 - inputs.value("price.parts_drift_year", b.cfg) / 100) ** years, list_price)


def sold_hours(cfg, key, vehicle):
    """A job's sold hours on a car (spec section 3, order_labor): canned hours x the class multiplier; none on tyre
    storage; the en courtesy inspection's 0.1 hour (spec section 4.3)."""
    x = JOBS[key][cfg]
    return (Decimal(str(x["hours"])) * Decimal(str((x["hours_by_class"] or {}).get(vehicle["vehicle_class"]) or 1))).quantize(CENT, ROUND_HALF_UP)


def price(b, day, customer, vehicle, job):
    """Prices one job in place (spec section 1, "Prices on a date"; section 3, order_labor to order_fee): `labor`,
    `parts`, `sublet` and `fees`, and `value`, the job's lines at approval. The en courtesy inspection's line is free."""
    cfg, x = b.cfg, JOBS[job["key"]][b.cfg]
    company = customer.get("price_class") == "company_account"
    i = period(b, day)
    hour = Decimal(str((inputs.value("price.hour.company_history", cfg) if company else [r for _, r in inputs.value("price.hour.history", cfg)])[i]))
    job["labor"] = job["sublet"] = None
    sold = job.get("hours") or sold_hours(cfg, job["key"], vehicle)
    if sold:
        if job["key"] == "courtesy_inspection":
            hour = amount = ZERO
        elif x["labour_pricing"] == "hourly":
            amount = (sold * hour).quantize(CENT, ROUND_HALF_UP)
        else:
            mult = Decimal(str((x["hours_by_class"] or {}).get(vehicle["vehicle_class"]) or 1))
            amount = reference.money(cfg, (x["labour_price_company"] if company else x["labour_price"])["history"][i], mult, not company)
        job["labor"] = {"hours": sold, "rate": hour, "amount": amount, "discount": ZERO}
    job["parts"] = []
    cls = vehicle["vehicle_class"] if x["parts_scale_with_class"] else "car"
    for slot in x["parts"]:
        # the S6 pad on a cheap pad job's pad slot; its other slots at economy, the tier the cheap pad sits in; a slot with
        # one option is the same in every tier
        story = [o for o in slot["options"] if "story" in o]
        tier = job.get("tier") if job.get("tier") != "cheap" or story else "economy"
        options = story if tier == "cheap" else [o for o in slot["options"] if "story" not in o]
        o = next((o for o in options if o["tier"] in (tier, "cheap")), options[0])
        part = b.parts[o["brand"], o["part_number"] or slot["name"], cls]
        unit = drifted(b, part["list_price"], day)
        job["parts"].append({"part_id": part, "description": slot["name"], "brand": part["brand"], "quantity": Decimal(str(slot["qty"])),
                             "unit_cost": drifted(b, part["cost"], day), "unit_price": (unit * Decimal("0.9")).quantize(CENT, ROUND_HALF_UP) if company else unit,
                             "vendor_id": None})
    if x["usually_sublet"]:
        vendor = b.vendors[SUBLET[job["key"]][0] if cfg == "ru" else "V6"]
        job["sublet"] = {"vendor_id": vendor, "description": x["sublet"]["what"], "cost": drifted(b, Decimal(str(x["sublet"]["cost"])), day),
                         "price": drifted(b, Decimal(str(x["sublet"]["price"])), day)}
    job["fees"] = [(FEE[job["key"]], f["name"], drifted(b, Decimal(str(f["price"])), day)) for f in x["fees"]]
    job["value"] = ((job["labor"] or {}).get("amount", ZERO) + sum((p["quantity"] * p["unit_price"]).quantize(CENT, ROUND_HALF_UP) for p in job["parts"])
                    + (job["sublet"]["price"] if job["sublet"] else ZERO))


def bill(b, jobs):
    """The order's labour, parts, sublet and fees (D1): the approved jobs' lines, or every job's while none is approved
    (the estimate's value); shop supplies on the approved hourly labour, capped (spec section 1)."""
    live = [j for j in jobs if j["status"] == "approved"] or jobs
    hourly = sum(j["labor"]["amount"] for j in jobs if j["status"] == "approved" and j["labor"] and JOBS[j["key"]][b.cfg]["labour_pricing"] == "hourly")
    supplies = min((hourly * Decimal(str(inputs.value("price.supplies.rate", b.cfg))) / 100).quantize(CENT, ROUND_HALF_UP), Decimal(str(inputs.value("price.supplies.cap", b.cfg))))
    return (sum(j["labor"]["amount"] for j in live if j["labor"]), sum((p["quantity"] * p["unit_price"]).quantize(CENT, ROUND_HALF_UP) for j in live for p in j["parts"]),
            sum(j["sublet"]["price"] for j in live if j["sublet"]), sum(f[2] for j in live for f in j["fees"]) + supplies, supplies)


def tax_rate(b, site, day):
    """spec section 1, Tax: en the shop's rate; ru 5 from tax.ru_vat_from, 0 before."""
    if b.cfg == "ru" and day < dt.date.fromisoformat(inputs.value("tax.ru_vat_from", "ru")):
        return ZERO
    return Decimal(str(inputs.value(f"tax.rate.{site}", b.cfg)))


def status(b, ro, name, when):
    """A status change a later step adds to a built order (the statement's `paid`, a re-issued bill); the order's status
    is its last row (D2)."""
    record = b.orders[id(ro)]
    record["added"].append((name, when))
    record["history"].append({"repair_order_id": ro, "status": name, "changed_at": when})
    record["history"].sort(key=lambda h: h["changed_at"])
    ro["status"] = record["history"][-1]["status"]


def wait(b, ro, since, till):
    """Puts a built order in waiting_parts from `since` to `till` (spec section 4.10: a purchase order that arrives after
    work started): the clock of the open job stops and starts again, the work after it moves, and completion,
    collection and payment follow."""
    record = b.orders[id(ro)]
    record["waits"].append((since, till))
    settle(b, record)


def order(b, site, opened, customer, vehicle, advisor, jobs, *, kind="customer_pay", comeback_of=None, pay="card", discount=None,
          void=None, booking=None, start=None, waits=(), complaint=None):
    """Writes one order at `site` opened at `opened` (shop clock) and returns its repair_order row.

    `pay`: the counter payment's method, None for an order billed on a statement (it stops at invoiced; the statement
    step adds `paid` with `status`). `discount`: (share of the bill before the discount, reason, approver) on the labour
    lines. `void`: the reason of a background void. An order whose jobs are all declined is a declined estimate; a
    declined job with `expires` is declined on the day its estimate expires. `comeback_of`: the first order (kind warranty
    or goodwill; first look by the shop's kb.comeback_first_look person). `booking`: the arrived appointment (source,
    booked_at, booked_by, starts_at, duration). `start`: when work starts, when the order waited for it. `waits`: (from,
    to) spans in waiting_parts (or later, `wait`)."""
    cfg, day, T = b.cfg, opened.date(), until(b, site)
    rng = streams.stream(b.seed, "order", site, opened, vehicle["plate"] or vehicle["vin"])
    last = hours(b, site, day)[1] - MINUTE
    rate, included = tax_rate(b, site, day), cfg == "ru"
    ro = b.add("repair_order", location_id=b.shops[site], customer_id=customer, vehicle_id=vehicle, advisor_id=b.people[advisor], order_type=kind,
               comeback_of_id=comeback_of, opened_at=opened, complaint=complaint, tax_rate=rate, tax_included=included,
               purchase_order_number=None)
    record = b.orders[id(ro)] = {"order": ro, "site": site, "jobs": jobs, "history": [], "entries": [], "payments": [], "left": None,
                                 "booked": [], "waits": list(waits), "added": [], "start": start, "pay": pay, "void": void, "booking": booking,
                                 "labor": [], "parts": [], "sublets": [], "fees": [], "inspection": None, "items": [], "appointment": None}
    for j in jobs:
        if "value" not in j:
            price(b, day, customer, vehicle, j)

    # spec section 4.5: customer jobs at check-in, raised jobs after the inspection, inside the approval window and the
    # shop's hours; a void is written off before any look
    checked = min(opened + rng.randrange(16) * MINUTE, last)
    looked = min(opened + rng.randrange(10, 61) * MINUTE, last) if comeback_of or not void and any(j["key"] in INSPECTING for j in jobs) else None
    record["looked"] = looked
    for j in jobs:
        if j["status"] != "pending":
            if j.get("expires"):  # the expiry day, or the last open day before it
                last_day = day + dt.timedelta(j["expires"])
                while hours(b, site, last_day) is None:
                    last_day -= clock.DAY
                j["decided"] = hours(b, site, last_day)[0] + rng.randrange(60) * MINUTE
            j["decided"] = j.get("decided") or (min(looked + rng.randrange(121) * MINUTE, last) if j.get("found") else checked)
            if j.get("found") and day == T.date():  # T's day: decided by T, or still with the customer (`decides`)
                j["decided"] = min(j["decided"], T) if decides(b, site, opened) else max(j["decided"], T + MINUTE)
            j["method"] = j.get("method") or ("phone" if booking and booking["source"] == "phone" else "counter")
    record["voided"] = min(opened + rng.randrange(5, 61) * MINUTE, last) if void else None
    settle(b, record)
    for j in jobs:
        if j.get("decided") and j["decided"] > T:
            j.update(status="pending", decided=None, method=None)
    if looked and looked > T:
        jobs[:] = [j for j in jobs if not j.get("found")]
        looked = None

    # lines and totals (D1)
    labor, parts, sublet, fees, supplies = bill(b, jobs)
    gross = labor + parts + sublet + fees
    approved_labor = [j["labor"] for j in jobs if j["status"] == "approved" and j["labor"]]
    off = ZERO
    if kind != "customer_pay":
        off = gross
        for line in approved_labor:
            line["discount"] = line["amount"]
    elif discount and approved_labor and labor:  # price.discount_base: the bill before the discount (en before tax, ru as billed)
        # (an estimate whose decision comes after T, or free labour, carries none)
        off = min((Decimal(str(discount[0])) * gross).quantize(CENT, ROUND_HALF_UP), labor)
        rest = off
        for line in sorted(approved_labor, key=lambda line: line["amount"]):  # in proportion; the largest line takes the rounding
            line["discount"] = min((off * line["amount"] / labor).quantize(CENT, ROUND_HALF_UP), rest, line["amount"])
            rest -= line["discount"]
        max(approved_labor, key=lambda line: line["amount"])["discount"] += rest
        ro.update(discount_reason=discount[1], discount_approved_by_id=discount[2])
    if kind != "customer_pay":
        tax = total = ZERO
    elif included:
        total = gross - off
        tax = total - (total / (1 + rate / 100)).quantize(CENT, ROUND_HALF_UP)
    else:
        tax = ((gross - off) * rate / 100).quantize(CENT, ROUND_HALF_UP)
        total = gross - off + tax
    ro.update(labor_total=labor, parts_total=parts, sublet_total=sublet, fees_total=fees, discount_total=off, tax_total=tax, total=total)
    for pay in record["payments"]:
        pay["amount"] = pay["amount"] if pay["amount"] is not None else total - record["deposit"]
    record["payments"] = [p for p in record["payments"] if p["amount"] > 0]
    if void:
        ro.update(voided_at=record["voided"], voided_by_id=b.people[advisor], void_reason=void)
    if booking:
        lead = jobs[0]
        fits = opened + dt.timedelta(hours=float((lead["labor"] or {}).get("hours", 0))) <= dt.datetime.combine(day, PROMISE[cfg])
        ro["promised_at"] = dt.datetime.combine(day, PROMISE[cfg]) if fits else None
        record["appointment"] = b.add("appointment", location_id=b.shops[site], customer_id=customer, vehicle_id=vehicle, starts_at=booking["starts_at"],
                                      duration_min=booking["duration"], source=booking["source"], status="arrived", reason=JOBS[lead["key"]][cfg]["name"],
                                      booked_at=booking["booked_at"], booked_by_id=b.people[booking["booked_by"]], repair_order_id=ro)

    for j in jobs:
        x = JOBS[j["key"]][cfg]
        live = j["status"] == "approved"
        note = f" ({TEXTS[cfg]['comeback_note']})" if comeback_of else ""
        j["row"] = b.add("order_job", repair_order_id=ro, canned_job_id=b.jobs[j["key"]], description=x["name"] + note, status=j["status"],
                         approval_method=j.get("method"), decided_at=j.get("decided"), authorized_by=j.get("authorized_by"),
                         approved_amount=j["value"] if live else None, deferred=j["status"] == "declined" and j.get("found") == "bad")
        if j["labor"]:
            j["labor_row"] = b.add("order_labor", order_job_id=j["row"], technician_id=j.get("tech") if live else None, **j["labor"])
            record["labor"].append(j["labor_row"])
        record["parts"] += [b.add("order_part", order_job_id=j["row"], **p) for p in j["parts"]]
        if j["sublet"]:
            record["sublets"].append(b.add("order_sublet", order_job_id=j["row"], **j["sublet"]))
    for j in [j for j in jobs if j["status"] == "approved"] or jobs:
        record["fees"] += [b.add("order_fee", repair_order_id=ro, kind=k, description=name, amount=amount) for k, name, amount in j["fees"]]
    if supplies:
        record["fees"].append(b.add("order_fee", repair_order_id=ro, kind="shop_supplies",
                                    description=reference.CATALOGUE["configurations"][cfg]["shop_supplies"]["name"], amount=supplies))
    courtesy_line(b, record)

    if looked:
        inspector = b.people[str(inputs.value("kb.comeback_first_look", cfg)[site])] if comeback_of else next(j["tech"] for j in jobs if j.get("tech"))
        record["inspection"] = b.add("inspection", repair_order_id=ro, technician_id=inspector, completed_at=looked)
        raised = collections.defaultdict(list)
        for j in jobs:
            if j.get("found"):
                raised[group(j["key"])].append(j)
        for g, name in enumerate(GROUPS[cfg]):
            for j in raised.get(g, []):
                x = JOBS[j["key"]][cfg]
                j["item_row"] = b.add("inspection_item", inspection_id=record["inspection"], component=f"{name}: {x['parts'][0]['name'] if x['parts'] else x['name']}",
                                      result=j["found"], measurement=j.get("reading"), has_photo=bool(j.get("photo")), order_job_id=j["row"])
                record["items"].append(j["item_row"])
            if g not in raised:
                record["items"].append(b.add("inspection_item", inspection_id=record["inspection"], component=name, result="good", measurement=None,
                                             has_photo=False, order_job_id=None))
    return ro


def courtesy_line(b, record):
    """The en courtesy inspection's free line goes to the order's mechanic with the most hours (spec section 4.3)."""
    jobs = record["jobs"]
    hours_by = collections.Counter()
    for j in jobs:
        if j["status"] == "approved" and j["labor"] and j.get("tech") and j["key"] != "courtesy_inspection":
            hours_by[id(j["tech"])] += j["labor"]["hours"]
    for j in jobs:
        if j["key"] == "courtesy_inspection" and j.get("labor_row"):
            techs = [x["tech"] for x in jobs if x.get("tech") and id(x["tech"]) in hours_by]
            top = max(techs, key=lambda r: hours_by[id(r)], default=next((x["tech"] for x in jobs if x.get("tech")), None))
            j["tech"] = j["labor_row"]["technician_id"] = top if j["status"] == "approved" else None


def settle(b, record):
    """The order's timeline (spec section 4.5) from its decisions: approval, the work booked on the mechanics' days
    (`book`), waiting_sublet while a subcontractor has the car (kb.sublet_times), the waits for parts, completion,
    invoicing, collection the same day or the next morning (spec section 7b); a warranty order is paid at completion.
    Every status lies inside the shop's hours; what falls after T is not written (spec section 1)."""
    cfg, site, ro, jobs = b.cfg, record["site"], record["order"], record["jobs"]
    opened, T = ro["opened_at"], until(b, site)
    due = T.date() - clock.DAY if opened.date() < T.date() else None  # an order of an earlier day is done before T's day
    if record.get("open") == "completed":  # M4's car (mess.py): its work is done on its start's day, by whoever has room
        due = record["start"].date()
    rng = streams.stream(b.seed, "settle", site, opened)
    for tech, piece in record["booked"]:
        b.timeline[id(tech), piece[0].date()].remove(piece)
    record["booked"], entries = [], []
    steps, left, paid, deposit = [("estimate", opened)], None, None, ZERO
    if record["void"]:
        steps.append(("void", record["voided"]))
    elif all(j["status"] == "declined" for j in jobs):
        steps.append(("declined", max(j["decided"] for j in jobs)))
        left = steps[-1][1]
    elif any(j["status"] == "approved" for j in jobs):
        approved = [j for j in jobs if j["status"] == "approved"]
        first = min(j["decided"] for j in approved)
        steps.append(("approved", first))
        ready = record["start"] or max([first] + [record["looked"]] * bool(record["looked"]))
        for j in sorted(approved, key=lambda j: (bool(j.get("found")), j["decided"])):
            if not (j["labor"] and j.get("tech")) or j["key"] == "courtesy_inspection":
                continue
            # a job starts after its own special-order parts are in (parts.install; a late one held, `after`)
            minutes = clocked(b, j)
            at = max([ready, j["decided"]] + [t for t in [getattr(b, "parts_in", None) and b.parts_in(record, j), j.get("after")] if t])
            if j["sublet"]:  # removal, the car at the subcontractor for kb.sublet_times working days, refitting
                j["tech"], pieces = book(b, site, at, minutes // 2, j["tech"], j.get("keep"), record["waits"], due)
                back = pieces[-1][1].date()
                for _ in range(inputs.value("kb.sublet_times", cfg)[SUBLET[j["key"]][2 if cfg == "ru" else 1]]):
                    back = opening(b, site, dt.datetime.combine(back + clock.DAY, dt.time())).date()
                steps += [("waiting_sublet", pieces[-1][1]), ("in_progress", hours(b, site, back)[0])]
                entries += [(j, j["tech"], p) for p in pieces]
                j["tech"], pieces = book(b, site, hours(b, site, back)[0], minutes - minutes // 2, j["tech"], True, record["waits"])
            else:
                j["tech"], pieces = book(b, site, at, minutes, j["tech"], j.get("keep"), record["waits"], due, j.get("split"))
            entries += [(j, j["tech"], p) for p in pieces]
            if j.get("labor_row"):
                j["labor_row"]["technician_id"] = j["tech"]
        record["booked"] = [(tech, p) for _, tech, p in entries]
        done = max([ready] + [p[1] for _, _, p in entries])
        begun = min([p[0] for _, _, p in entries], default=ready)  # in_progress: the first technician's start (spec 4.5)
        if any(since <= begun for since, _ in record["waits"]):  # a waiting car of parts.place whose mechanic has no shift before its wait: as planted
            begun = ready
        steps.append(("in_progress", begun))
        for since, till in record["waits"]:
            if begun < since < done:
                steps += [("waiting_parts", since), ("in_progress", till)]
        steps.append(("completed", done))
        steps.append(("invoiced", opening(b, site, done + MINUTE)))
        if opened.date() == T.date():  # today's orders are still open at T (spec section 4.5): billed and paid after it
            steps[-1] = ("invoiced", max(steps[-1][1], T + MINUTE))
        if ro["order_type"] != "customer_pay":
            paid = opening(b, site, done + 2 * MINUTE)
        elif record["pay"]:  # collected the same day, or the next morning when the work ends late (spec section 7b)
            close = hours(b, site, done.date())[1]
            if close - done >= 30 * MINUTE:
                paid = done + rng.randrange(1, int((close - done) / MINUTE)) * MINUTE
            else:
                paid = opening(b, site, close) + rng.randrange(121) * MINUTE
        if paid:
            if opened.date() == T.date():
                paid = max(paid, steps[-1][1] + MINUTE)
            steps.append(("paid", paid))
        left = paid or steps[-1][1]
        if record.get("labor"):
            courtesy_line(b, record)
    steps = sorted(steps + record["added"], key=lambda s: s[1])
    if record.get("open"):  # spec section 6, M4 (mess.py): never closed, the order stops at this status, unbilled
        steps, paid = steps[:[name for name, _ in steps].index(record["open"]) + 1], None
        left = steps[-1][1] if record["open"] == "completed" else None
        if record["open"] == "approved":  # its work never started
            for tech, piece in record["booked"]:
                b.timeline[id(tech), piece[0].date()].remove(piece)
            record["booked"], entries = [], []
    record["history"] = [{"repair_order_id": ro, "status": name, "changed_at": when} for name, when in steps if when <= T]
    ro["status"] = record["history"][-1]["status"]
    record["left"] = left if left and left <= T else None
    record["entries"] = [{"technician_id": tech, "order_job_id": j, "clock_in": s, "clock_out": e if e <= T else None}
                         for j, tech, (s, e) in sorted(entries, key=lambda x: x[2]) if s <= T]
    record["payments"] = []
    total = ro.get("total")
    if record["pay"] and ro["order_type"] == "customer_pay":
        # kb.deposits: a rebuild's deposit at booking or check-in (special-order parts are the parts step's, 4.10)
        rebuild = any(j["key"] == "transmission_rebuild" and j["status"] == "approved" for j in jobs)
        deposit = Decimal(str(inputs.value("kb.deposits", cfg)["transmission_rebuild" if cfg == "en" else "gearbox_rebuild"])) if rebuild else ZERO
        booking = record["booking"]
        # (at a booking made away from the counter cash cannot change hands: a cash deposit is taken at check-in)
        got, taker = (booking["booked_at"], booking["booked_by"]) if booking and (record["pay"] != "cash" or booking["source"] == "walk_in") \
            else (opened, slot_of(b, ro["advisor_id"]))
        if deposit and got <= T:
            record["payments"].append({"repair_order_id": ro, "kind": "deposit", "method": record["pay"], "amount": deposit, "received_at": got,
                                       "taken_by_id": b.people[taker], "reference": None if record["pay"] == "cash" else f"{rng.randrange(10 ** 6):06d}"})
        if paid and paid <= T and (total is None or total > deposit):
            on = advisors(b, site, paid.date())
            mine = slot_of(b, ro["advisor_id"])
            record["payments"].append({"repair_order_id": ro, "kind": "payment", "method": record["pay"], "amount": None if total is None else total - deposit,
                                       "received_at": paid, "taken_by_id": b.people[mine if mine in on or not on else on[0]],
                                       "reference": None if record["pay"] == "cash" else f"{rng.randrange(10 ** 6):06d}"})
    record["deposit"] = deposit


def finish(b):
    """The last step of an order's life in the build: its payments' amounts, history, time entries and payments into
    the tables, the odometers (spec section 4.4) and the document numbers (spec section 1)."""
    for record in b.orders.values():
        b.tables["order_status_history"] += record["history"]
        b.tables["time_entry"] += [dict(e, order_job_id=e["order_job_id"]["row"]) for e in record["entries"]]
        b.tables["payment"] += record["payments"]
    odometers(b)
    rows = sorted(b.tables["repair_order"], key=lambda r: r["opened_at"])
    per_shop = collections.Counter()
    for n, ro in enumerate(rows):
        site = next(s for s, r in b.shops.items() if r is ro["location_id"])
        per_shop[site] += 1
        ro["number"] = str(104001 + n) if b.cfg == "en" else f"ЗН{('main', 'east', 'west').index(site) + 1}-{per_shop[site]:06d}"


def odometers(b):
    """4.4: a car's odometer at the history start is its age (from 1 July of the year before its model year, spec
    section 7b) x its yearly distance (fleets their own, others erp.vehicle.yearly_distance), growing linearly with a
    wobble of up to 10 % per visit, never falling and under three times the visit before (spec section 6, M3); a reading
    a story set stays. mileage_out adds the road test (0 to 15) once the car has left."""
    cfg = b.cfg
    yearly_of = {f["vin"]: f.get("typical_yearly_miles") or f.get("typical_yearly_km") for a in customers.ACCOUNTS[cfg]["accounts"] for f in a["fleet"]}
    visits = collections.defaultdict(list)
    for o in sorted(b.orders.values(), key=lambda o: o["order"]["opened_at"]):
        visits[id(o["order"]["vehicle_id"])].append(o)
    for group_ in visits.values():
        car = group_[0]["order"]["vehicle_id"]
        yearly = yearly_of.get(car["vin"]) or inputs.value("erp.vehicle.yearly_distance", cfg)
        last = 0
        for o in group_:
            ro = o["order"]
            if ro.get("mileage_in") is None:
                rng = streams.stream(b.seed, "odometer", car["plate"] or car["vin"], ro["opened_at"])
                years = max((ro["opened_at"].date() - dt.date(car["year"] - 1, 7, 1)).days / 365.25, 0.1)
                drawn = round(yearly * years * (0.9 + 0.2 * rng.random()))
                ro["mileage_in"] = min(max(last, drawn), 3 * last - 1) if last else drawn
                if o.get("misread"):  # spec section 6, M3 (mess.py): a digit dropped or added at the counter
                    ro["mileage_in"] = ro["mileage_in"] // 10 if o["misread"] == "dropped" else ro["mileage_in"] * 10 + ro["mileage_in"] % 10
                ro["mileage_out"] = ro["mileage_in"] + rng.randint(0, 15) if o["left"] else None
            last = ro["mileage_in"]
