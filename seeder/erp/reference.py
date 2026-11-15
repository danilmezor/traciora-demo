"""Step 1 of generator-spec.md section 2, the shop system's reference tables, then step 2 (`customers.fill`).
`fill(build)` writes the rows into `build.tables` and the lookups the later steps read into `build`."""
import collections
import dataclasses
import datetime as dt
import re
import string
from decimal import ROUND_HALF_UP, Decimal

from seeder import clock, inputs, streams
from seeder.erp import customers

SITES = ("main", "east", "west")
CATALOGUE = inputs.load("catalogue.json")
CAST = inputs.load("cast.json")
# phones.md: the shops' own lines, the English table first, then the Russian one
SHOP_LINES = re.findall(r"^\| `(main|east|west)` \| ([^|]+?) \|", (inputs.SEED / "phones.md").read_text(encoding="utf-8"), re.M)
ROLE = {"founder": "owner", "managing_owner": "owner", "office_manager": "office", "service_manager": "manager", "shop_manager": "manager",
        "lead_advisor": "advisor", "service_advisor": "advisor", "shop_foreman": "foreman", "parts_manager": "parts", "seasonal_helper": "technician"}
SEASON = {"en": (10, (6,)), "ru": (6, (4, 10))}  # spec section 3, employee: weeks of a season and the months it starts in
CENT = Decimal("0.01")
# catalogue.json brands: the numbering patterns a brand's text writes with open places ("121.xxxxx", "TCKWP###"), as
# regular expressions with a group per open place, and the whole text (it names fixed series such as "471-"), by the
# brand's first word
PATTERNS = {cfg: collections.defaultdict(list) for cfg in ("en", "ru")}
NUMBERING = {cfg: collections.defaultdict(str) for cfg in ("en", "ru")}
for _cfg in PATTERNS:
    for _entry in CATALOGUE["brands"][_cfg]:
        for _name in _entry["brand"].split(", "):
            NUMBERING[_cfg][_name.split()[0].casefold()] += " " + _entry["numbering"]
            for _pattern in re.findall(r"[\w.\-]*[x#]{2,}[\w.\-#]*", _entry["numbering"]):
                PATTERNS[_cfg][_name.split()[0].casefold()].append("".join("([0-9A-Z])" if ch in "x#" else re.escape(ch) for ch in _pattern))


@dataclasses.dataclass(repr=False)  # a build's repr would print every row: a failing assert that names one must not
class Build:
    """One build: its inputs, its tables (table name to rows) and the lookups later steps read. Lookup values are the
    rows themselves. `named` and `pending` map a story key to (customer, [vehicles]); pending rows are not in the
    tables yet: the step that writes the record's first moment (a first-time caller's check-in, a duplicate's second
    record) appends them. A row added after the row its table's first moment is read from (a car added to an existing
    customer) carries that moment under `load.FIRST_KEY`."""
    cfg: str
    a: dict
    seed: int
    tables: dict = dataclasses.field(default_factory=lambda: collections.defaultdict(list))
    shops: dict = dataclasses.field(default_factory=dict)  # main, east, west
    people: dict = dataclasses.field(default_factory=dict)  # cast slot ("1" .. "29", "F1" .. "F3")
    seasons: list = dataclasses.field(default_factory=list)  # F4, one row per season, oldest first
    jobs: dict = dataclasses.field(default_factory=dict)  # catalogue key
    parts: dict = dataclasses.field(default_factory=dict)  # (brand, catalogue part number or else the slot name, vehicle class)
    vendors: dict = dataclasses.field(default_factory=dict)  # V1 ..
    referrals: dict = dataclasses.field(default_factory=dict)  # erp.referral.mix name
    accounts: dict = dataclasses.field(default_factory=dict)  # A1 .. A6
    fleets: dict = dataclasses.field(default_factory=dict)  # A1 .. A6, then unit
    small: list = dataclasses.field(default_factory=list)  # (customer, [vehicles]) in accounts.json order
    walkin: dict = None
    pools: dict = dataclasses.field(default_factory=dict)  # site: [(customer, [vehicles])]; west's is the bulk load
    named: dict = dataclasses.field(default_factory=dict)
    pending: dict = dataclasses.field(default_factory=dict)
    taken: set = dataclasses.field(default_factory=set)  # every phone, VIN and plate in use or named in a seed file
    orders: dict = dataclasses.field(default_factory=dict)  # id(repair_order row): the rows orders.order wrote under it
    timeline: dict = dataclasses.field(default_factory=dict)  # (id(mechanic row), day): his booked work, sorted (start, end)

    def add(self, table, **row):
        self.tables[table].append(row)
        return row


BY_MEASURE = ("л", "г", "кг")  # a fluid or gas sold by the litre, gram or kilogram keeps the catalogue's unit price (spec section 1, "Money")


def money(cfg, amount, factor=1, list_price=False):
    """amount x factor: cents, or for a Russian list price whole roubles rounded to 10 (spec section 1, "Money"); a
    price under 10 roubles a unit keeps its kopecks."""
    value = Decimal(str(amount)) * Decimal(str(factor))
    if cfg == "ru" and list_price and value >= 10:
        return (value / 10).quantize(Decimal(1), ROUND_HALF_UP) * 10
    return value.quantize(CENT, ROUND_HALF_UP)


def fill(b):
    cfg, a = b.cfg, b.a
    T = a["T"].date()
    lines = dict(SHOP_LINES[:3] if cfg == "en" else SHOP_LINES[3:6])
    east_months = int(re.search(r"\d+", inputs.value("proposed.cast.east_opened", cfg))[0])
    opened = {"main": clock.months_back(T, 30 * 12), "east": clock.months_back(T, east_months), "west": a["bought"]}  # main: design 1.1
    for site in SITES:
        address, lat, lon = re.fullmatch(r"(.*) \((-?[\d.]+), (-?[\d.]+)\)", inputs.value(f"geo.address.{site}", cfg)).groups()
        b.shops[site] = b.add("location", name=inputs.value("geo.short_name", cfg)[site], address=address, phone=customers.e164(lines[site]),
                              time_zone=inputs.value("geo.other_zone" if site == "west" else "geo.home_zone", cfg),
                              tax_rate=Decimal(str(inputs.value(f"tax.rate.{site}", cfg))), bays=inputs.value(f"site.bays.{site}", cfg),
                              latitude=Decimal(lat), longitude=Decimal(lon), opened_on=opened[site])

    categories = {c["key"]: b.add("service_category", code=c["key"], name=c[cfg]) for c in CATALOGUE["categories"]}
    for job in CATALOGUE["jobs"]:
        x = job[cfg]
        b.jobs[job["key"]] = b.add("canned_job", code=job["key"], service_category_id=categories[job["category"]], name=x["name"],
                                   hours=Decimal(str(x["hours"])), labor_pricing=x["labour_pricing"],
                                   menu_price=Decimal(str(x["labour_price"]["after_rise"])) if x["labour_pricing"] == "menu" else None)

    # price.hour.history names each period's first day by a TIMELINE anchor; the company hours share its dates
    starts = {"T-24 months": a["history_start"], "the first open day on or after T-18 months": clock.snap(cfg, clock.months_back(T, 18)),
              "the first full open day on or after T-335 days": a["s2_start"], "P": a["P"]}
    history = inputs.value("price.hour.history", cfg)
    froms = [starts[when] for when, _ in history]
    for site in SITES:
        for price_class, rates in (("standard", [r for _, r in history]), ("company_account", inputs.value("price.hour.company_history", cfg))):
            for start, end, rate in zip(froms, froms[1:] + [None], rates):
                if site == "west" and end is not None and end <= a["bought"]:
                    continue  # west has only the periods in force from its purchase day
                b.add("labor_rate", location_id=b.shops[site], price_class=price_class, rate=Decimal(str(rate)),
                      valid_from=max(start, a["bought"]) if site == "west" else start, valid_to=end - clock.DAY if end else None)

    for v in inputs.load("vendors.json")[cfg]:
        b.vendors[v["id"]] = b.add("vendor", name=customers.trade_name(cfg, v["name"], v["legal_form"]), kind="parts" if int(v["id"][1:]) <= 5 else "sublet",
                                   payment_terms_days=v["payment_terms_days"], phone=customers.e164(v["phone"]), email=v["email"])

    parts(b)

    for name in inputs.value("erp.referral.mix", cfg):
        if name != "blank":
            b.referrals[name] = b.add("referral_source", name=name)

    employees(b)
    customers.fill(b)


def parts(b):
    """spec section 3, part: one row per distinct (brand, part number) of the catalogue's options, class `car` (a part
    with no number: per brand and slot name); for slots of jobs whose parts scale with the class, a row per other class
    the job is offered for, priced by the class multiplier, its number styled on the brand's numbering: a series the
    brand's text names is kept, and the places a pattern of the brand leaves open are redrawn, else the number's last
    longest run of digits, else (a number of letters, a model code) its last group of letters; unique within the brand.
    Fluids keep no number."""
    cfg = b.cfg
    multiplier = CATALOGUE["configurations"][cfg]["parts_class_multiplier"]
    numbers = collections.defaultdict(set)
    for job in CATALOGUE["jobs"]:
        for slot in job[cfg]["parts"]:
            for o in slot["options"]:
                numbers[o["brand"]].add(o["part_number"])
    for job in CATALOGUE["jobs"]:
        x = job[cfg]
        by_class = x["hours_by_class"]
        classes = [c for c in multiplier if c != "car" and (by_class is None or by_class.get(c) is not None)] if x["parts_scale_with_class"] else []
        for slot in x["parts"]:
            for o in slot["options"]:
                brand, number = o["brand"], o["part_number"]
                key = number or slot["name"]
                if (brand, key, "car") not in b.parts:
                    b.parts[brand, key, "car"] = b.add("part", part_number=number, brand=brand, description=slot["name"], unit=slot["unit"],
                                                       cost=money(cfg, o["cost"]), list_price=money(cfg, o["list_price"], list_price=slot["unit"] not in BY_MEASURE))
                for c in classes:
                    if (brand, key, c) in b.parts:
                        continue
                    styled = None
                    if number and slot["kind"] != "fluid":
                        rng = streams.stream(b.seed, "part", brand, number, c)
                        first = brand.split()[0].casefold()
                        # a series the brand's text names ("471-", "MT-") stays: the longest prefix ending in a separator
                        # or letter that the text holds and that leaves digits to redraw
                        fixed = max((k for k in range(1, len(number)) if not number[k - 1].isdigit() and number[:k] in NUMBERING[cfg][first]
                                     and re.search(r"\d", number[k:])), default=0)
                        matches = [m for p in PATTERNS[cfg][first] if (m := re.fullmatch(p, number))]
                        runs = list(re.finditer(r"\d+", number[fixed:]))
                        if matches:
                            places = [i for g in range(1, matches[0].lastindex + 1) for i in range(*matches[0].span(g)) if number[i].isdigit() and i >= fixed]
                        elif runs:
                            places = [fixed + i for i in range(*max(reversed(runs), key=lambda r: len(r[0])).span())]
                        else:
                            places = range(*re.search(r"[A-Z]+(?=[^A-Z]*$)", number).span())
                        while styled is None or styled in numbers[brand]:
                            chars = list(number)
                            for i in places:
                                chars[i] = streams.pick(rng, string.digits if number[i].isdigit() else string.ascii_uppercase)
                            styled = "".join(chars)
                        numbers[brand].add(styled)
                    b.parts[brand, key, c] = b.add("part", part_number=styled, brand=brand, description=slot["name"], unit=slot["unit"],
                                                   cost=money(cfg, o["cost"], multiplier[c]),
                                                   list_price=money(cfg, o["list_price"], multiplier[c]))  # list x multiplier to the kopeck, as the story files quote it


def employees(b):
    """spec section 3, employee: slots 1 to 29 and F1 to F3 from cast.json, then one row per season of F4 that overlaps the
    history. Slots 7 and 14 start on their TIMELINE anchors; people who came with west, on the purchase day."""
    cfg, a = b.cfg, b.a
    T = a["T"].date()
    pay = {kind: re.findall(r"\b(\d+|F\d)\b", text) for kind, text in re.findall(r"(salary|hourly) for slots ([^;]+)", inputs.value("kb.pay_types", "en"))}
    left = {"F1": a["fired"], "F2": a["f2_fired"], "F3": a["f3_resigns"]}
    anchored = {"7": a["slot7_starts"], "14": a["slot14_starts"]}
    for p in CAST["people"]:
        slot, x = p["slot"], p[cfg]
        role = ROLE.get(p["role_key"]) or ("technician" if p["role_key"].endswith("technician") else None)
        if role is None:
            raise ValueError(f"cast slot {slot}: no shop-system role for {p['role_key']}")
        pay_type = next((kind for kind in ("salary", "hourly") if slot in pay[kind]), "flat_rate") if role == "technician" else "salary"
        tokens = x["full_name"].split()
        row = dict(location_id=b.shops.get(p["site"]), first_name=tokens[0], middle_name=tokens[1] if len(tokens) == 3 else None, last_name=tokens[-1],
                   role=role, title=CAST["roles"][p["role_key"]][cfg], pay_type=pay_type)
        if slot == "F4":
            weeks, months = SEASON[cfg]
            for year in range(a["history_start"].year, T.year + 1):
                for month in months:
                    first = dt.date(year, month, 1) + dt.timedelta((7 - dt.date(year, month, 1).weekday()) % 7)
                    last = first + dt.timedelta(7 * weeks - 1)
                    if last >= a["history_start"] and first <= T:
                        b.seasons.append(b.add("employee", **row, hired_on=first, left_on=last))  # a fixed term: its last day, also ahead of T
            continue
        if slot in anchored:
            hired = anchored[slot]
        elif "at_shop_since_months_before_t" in x:
            hired = a["bought"]
        else:
            hired = clock.months_back(T, int(x["start_months_before_t"]))
        b.people[slot] = b.add("employee", **row, hired_on=hired, left_on=left.get(slot))
