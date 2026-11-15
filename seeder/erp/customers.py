"""Step 2 of generator-spec.md section 2: the customers and cars that exist before any order (spec section 3, customer,
customer_contact, vehicle). `person`, `phone`, `mail` and `car` are the draws a later step reuses for a new private
customer; each keeps what it draws unique through `b.taken`."""
import datetime as dt
import functools
import json
import re
import string
from decimal import Decimal
from pathlib import Path

from seeder import clock, inputs, streams

ACCOUNTS = inputs.load("accounts.json")
NAMED = inputs.load("named_customers.json")
PARC = inputs.load("parc.json")["configurations"]
BY_LABEL = {cfg: {m["model"]: m for m in PARC[cfg]["models"]} for cfg in PARC}
HERE = Path(__file__).parent
NAMES = {cfg: json.loads((HERE / f"names.{cfg}.json").read_text(encoding="utf-8")) for cfg in ("en", "ru")}
TRANSLIT = json.loads((HERE / "translit.ru.json").read_text(encoding="utf-8"))
PHONES = (inputs.SEED / "phones.md").read_text(encoding="utf-8")
# phones.md section 1, tier B: area code shares at the home shops and at west. Its row "other real area codes" names no
# code, so that share is left out and the listed ones carry the whole.
AREAS = {"home": {}, "west": {}}
for _code, _home, _west in re.findall(r"^\| (\d{3})(?: \(\w+\))? \| [\d,]+ \| (?:(\d+) %)? *\| (?:(\d+) %)? *\|", PHONES, re.M):
    AREAS["home"].update({_code: int(_home)} if _home else {})
    AREAS["west"].update({_code: int(_west)} if _west else {})
TIER_B = [n for n in range(200, 10000) if n not in (1212, 4334)]
MOBILE = ("907", "935")  # phones.md section 2: background mobiles draw from both reserve codes
CITY = {"home": ("8422", 5), "west": ("843", 6)}  # phones.md section 2: a city number is the code, a 1, then 5 or 6 digits
# phones.md section 3: the private customers' domains, and the username: en "rdunlap", ru "o.timofeeva"
MAIL = {"en" if lang == "English" else "ru": domains for lang, *domains in re.findall(r"Private customers, (\w+) \| name@(\S+) or name@(\S+) \|", PHONES)}
WALKIN = {"en": "WALK-IN CUSTOMER", "ru": "Розничный покупатель"}  # generator-spec.md section 3, customer: the walk-in record
COMPANY_CLASS = ("A1", "A2")  # spec section 3, customer: the two accounts of the company price class
CROSSOVER = ("crossover", "krossover")  # a story car named only by its body (the Russian word transliterated): an suv
YEAR_CODES = "ABCDEFGHJKLMNPRSTVWXY123456789"  # 49 CFR 565.15: the model-year character, a 30-year cycle from 1980
VIN_VALUES = dict(zip("ABCDEFGHJKLMNPRSTUVWXYZ", (1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 7, 9, 2, 3, 4, 5, 6, 7, 8, 9)))  # 49 CFR 565.15
WEIGHTS = (8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2)
VIN_CHARS = string.digits + "".join(VIN_VALUES)
EN_LETTERS = "".join(c for c in string.ascii_uppercase if c not in "AEIOU")  # erp.vehicle.plates: "no vowels"


def tokens(text):
    return re.findall(r"\w+", text.casefold().replace("š", "s"))


def latin(text):
    """Lower-case Latin letters and digits only, Cyrillic through translit.ru.json: an e-mail username, a word to match."""
    return re.sub(r"[^a-z0-9]", "", "".join(TRANSLIT.get(ch, ch) for ch in text.casefold().replace("š", "s")))


def e164(text):
    digits = re.sub(r"\D", "", text)
    return ("+7" if digits.startswith("7") and len(digits) == 11 else "+1") + digits[-10:]


def trade_name(cfg, name, legal_form):
    """A company's name with its legal form as the market writes it: "Nickajack Delivery LLC"; the Russian form first,
    the name in quotes."""
    return name if not legal_form else f"{name} {legal_form}" if cfg == "en" else f"{legal_form} «{name}»"


def weighted(rng, weights):
    u, total = rng.random() * sum(weights.values()), 0
    for key, weight in weights.items():
        total += weight
        if u < total:
            return key
    return key


def deal(rng, n, weights):
    """n labels in the exact proportions of `weights` (largest remainder), shuffled: a rate row dealt, not rolled."""
    total = sum(weights.values())
    exact = {k: n * w / total for k, w in weights.items()}
    counts = {k: int(v) for k, v in exact.items()}
    for k in sorted(exact, key=lambda k: counts[k] - exact[k])[:n - sum(counts.values())]:
        counts[k] += 1
    labels = [k for k, c in counts.items() for _ in range(c)]
    rng.shuffle(labels)
    return labels


def engines(m, year):
    return [e["engine"] for e in m["engines"] if (e["year_from"] or 0) <= year <= (e["year_to"] or 9999)] if m else []


def vehicle(cfg, owner, c, unit=None):
    """A car of a seed file as given: its vehicle_class, and the first engine of its parc_model for its year."""
    found = engines(BY_LABEL[cfg].get(c["parc_model"]), c["year"])
    return dict(customer_id=owner, vin=c["vin"], plate=c["plate"], year=c["year"], make=c["make"], model=c["model"],
                engine=c.get("engine") or (found[0] if found else None), vehicle_class=c["vehicle_class"], unit_number=unit)


# Every VIN a seed file gives, with its car: the patterns a formed VIN copies (accounts.json _meta.how_formed)
EXAMPLES = {}
for _cfg in ("en", "ru"):
    _named = NAMED[_cfg]
    _cars = [f for acct in ACCOUNTS[_cfg]["accounts"] for f in acct["fleet"]] + [v for s in ACCOUNTS[_cfg]["small_business_customers"] for v in s["vehicles"]]
    _cars += [_named[k]["car"] for k in ("S7", "S8", "S6_waiting_nine_days")] + [x["car"] for x in _named["S15_duplicate_pairs"]]
    _cars += [x["car"] for x in _named["S15_car_on_the_wrong_customer"] if isinstance(x["car"], dict)]
    EXAMPLES[_cfg] = [(tokens(c["make"]), set(tokens(c["model"])), c["vehicle_class"], c["year"], c["vin"]) for c in _cars if c["vin"]]


def vin(b, make, model, vehicle_class, year, wmi, rng):
    """A VIN as accounts.json _meta.how_formed describes: the model's WMI (for a model parc.json gives none, that of a
    seed-file VIN of the make); the descriptor and plant character of a seed-file VIN of the make in this configuration
    (the one sharing most words with the model, then one of the same class), else drawn; the model-year character (ru:
    where the example writes one); a random six-digit serial; the English check digit."""
    same = [e for e in EXAMPLES[b.cfg] if e[0] == tokens(make)]
    wmi = wmi or next((e[4][:3] for cfg in (b.cfg, "en", "ru") for e in EXAMPLES[cfg] if e[0] == tokens(make)), None)
    if not wmi:
        raise ValueError(f"no WMI for {make} {model}: parc.json gives none and no seed file has a VIN of the make")
    code = YEAR_CODES[(year - 1980) % 30]
    if same:
        _, _, _, ex_year, base = max(same, key=lambda e: (len(e[1] & set(tokens(model))), e[2] == vehicle_class))
        descriptor, plant = base[3:8], base[10]
        position_9 = base[8]
        position_10 = code if b.cfg == "en" or base[9] == YEAR_CODES[(ex_year - 1980) % 30] else base[9]
    else:
        descriptor, plant = "".join(streams.pick(rng, VIN_CHARS) for _ in range(5)), streams.pick(rng, VIN_CHARS)
        position_9, position_10 = streams.pick(rng, VIN_CHARS), code
    while True:
        body = wmi + descriptor + position_9 + position_10 + plant + "".join(str(rng.randrange(10)) for _ in range(6))
        if b.cfg == "en":
            check = sum((int(c) if c.isdigit() else VIN_VALUES[c]) * w for c, w in zip(body, WEIGHTS)) % 11
            body = body[:8] + ("X" if check == 10 else str(check)) + body[9:]
        if body not in b.taken:
            b.taken.add(body)
            return body


def plate_index(text):
    left, right = text.split("-")
    letters, number = (left, right) if left.isalpha() else (right, left)
    value = 0
    for ch in letters:
        value = value * len(EN_LETTERS) + EN_LETTERS.index(ch)
    return value * (10 ** len(number) - 1) + int(number) - 1


def plate(b, rng, how):
    """erp.vehicle.plates. en: `how` is a serial format, drawn inside its issued serials (letters major, digits minor),
    or "named" for a car a story names (the never-issued block); ru: `how` is the region code."""
    row = inputs.value("erp.vehicle.plates", b.cfg)
    while True:
        if b.cfg == "en":
            runs = [(plate_index(lo), plate_index(hi), lo) for lo, hi in
                    re.findall(r"(\w+-\w+) to (\w+-\w+)", row["named_cars"] if how == "named" else " ".join(row["issued"][how]))]
            u = rng.randrange(sum(hi - lo + 1 for lo, hi, _ in runs))
            for lo, hi, sample in runs:
                if u <= hi - lo:
                    break
                u -= hi - lo + 1
            left, right = sample.split("-")
            letters, number = (left, right) if left.isalpha() else (right, left)
            value, n = divmod(lo + u, 10 ** len(number) - 1)
            chars = ""
            for _ in letters:
                value, ch = divmod(value, len(EN_LETTERS))
                chars = EN_LETTERS[ch] + chars
            digits = f"{n + 1:0{len(number)}d}"
            text = f"{chars}-{digits}" if left.isalpha() else f"{digits}-{chars}"
        else:
            letters = row["letters"]
            text = streams.pick(rng, letters) + f"{rng.randrange(1, 1000):03d}" + streams.pick(rng, letters) + streams.pick(rng, letters) + how
        if text not in b.taken:
            b.taken.add(text)
            return text


def phone(b, site, rng, city=False):
    """A background phone, unique and never a named one: en tier B of phones.md with the shop's area-code mix; ru a
    mobile in 907 or 935, or with `city` the shop city's number."""
    group = "west" if site == "west" else "home"
    while True:
        if b.cfg == "en":
            text = f"+1{weighted(rng, AREAS[group])}555{streams.pick(rng, TIER_B):04d}"
        elif city:
            code, n = CITY[group]
            text = f"+7{code}1" + "".join(str(rng.randrange(10)) for _ in range(n))
        else:
            text = f"+7{streams.pick(rng, MOBILE)}" + "".join(str(rng.randrange(10)) for _ in range(7))
        if text not in b.taken:
            b.taken.add(text)
            return text


def full_name(name):
    """A person's name as a key that ignores order, case and punctuation: "PARKER, DENISE" is "Denise Parker"."""
    return "name:" + " ".join(sorted(tokens(name)))


def person(b, rng, caps=False):
    """A background person from the configuration's lists, never the full name of a named record, of the cast or of
    another background person: en "First Last" (caps: "LAST, FIRST"), ru "Family Given Patronymic" (caps: all capitals).
    Returns the name and the e-mail username of phones.md section 3: en first initial and surname, ru first initial, a
    dot, the surname."""
    lists = NAMES[b.cfg]
    while True:
        first, gender = streams.pick(rng, [(n, g) for g, names in lists["given"].items() for n in names])
        family = streams.pick(rng, lists["family"] if b.cfg == "en" else lists["family"][gender])
        name = f"{first} {family}" if b.cfg == "en" else f"{family} {first} {streams.pick(rng, lists['patronymic'][gender])}"
        if full_name(name) not in b.taken:
            b.taken.add(full_name(name))
            break
    if caps:
        name = f"{family}, {first}".upper() if b.cfg == "en" else name.upper()
    return name, latin(first[0]) + ("" if b.cfg == "en" else ".") + latin(family)


def mail(b, username, rng):
    """A unique private address at a domain of phones.md section 3; on a clash the username takes digits."""
    domain, n = streams.pick(rng, MAIL[b.cfg]), 1
    while (text := f"{username}{n if n > 1 else ''}@{domain}") in b.taken:
        n += 1
    b.taken.add(text)
    return text


def ages(cfg, m):
    """parc.json age_weights, uniform inside a band, kept to the ages whose model year the model and one of its engines
    cover."""
    parc = PARC[cfg]
    return {age: band["weight"] / (band["age_to"] - band["age_from"] + 1) for band in parc["age_weights"]
            for age in range(band["age_from"], band["age_to"] + 1)
            if m["year_from"] <= parc["reference_year"] - age <= (m["year_to"] or parc["reference_year"]) and engines(m, parc["reference_year"] - age)}


def drawn(b, owner, m, year, shape, words, how, make=None, model=None):
    """A car of parc model `m` and a year: the engine among the year's (shape); the name (one of the label's `names`
    valid for the year, uniformly, with that name's make when it gives one; else the label), VIN and plate (words).
    `make` and `model` are the words a story file gave, kept as written."""
    engine = streams.pick(shape, engines(m, year)) if engines(m, year) else None
    names = [n for n in m.get("names") or [] if (n.get("year_from") or 0) <= year <= (n.get("year_to") or 9999)]
    name = streams.pick(words, names) if names else {"name": m["model"]}
    make, model = make or name.get("make", m["make"]), model or name["name"]
    return dict(customer_id=owner, vin=vin(b, make, model, m["vehicle_class"], year, m.get("wmi"), words), plate=plate(b, words, how),
                year=year, make=make, model=model, engine=engine, vehicle_class=m["vehicle_class"], unit_number=None)


def car(b, owner, site, shape, words, how):
    """A background car by parc.json how_to_draw: the model by share and the age by `ages` from the shape stream; the
    rest by `drawn`; its plate by `how` (see `plate`)."""
    models = PARC[b.cfg]["models"]
    m = models[weighted(shape, {i: m["share"] for i, m in enumerate(models)})]
    return drawn(b, owner, m, PARC[b.cfg]["reference_year"] - weighted(shape, ages(b.cfg, m)), shape, words, how)


def story_car(b, owner, text, shape, words, how):
    """A story person's car as the file words it ("2012 Toyota Tacoma, 4.0 V6", "Kia Rio, 2017", "Mazda 3"): a parc.json
    make, then as many words as that make's first matching model name has (up to a comma, a bracket or the year; the
    make and the next word written together match too: "Mazda 3" is "Mazda3"), and a year. What the words leave out is
    drawn: the model among the make's by share (with no make, among the models whose name the text holds, or the suv
    models for a crossover), the year by `ages`. None when nothing matches."""
    models = PARC[b.cfg]["models"]
    year = re.search(r"\b(?:19|20)\d\d\b", text)
    flat = text.replace("Š", "S").replace("š", "s")
    found = next((f for make in sorted({m["make"] for m in models}, key=lambda k: (-len(k), k))
                  if (f := re.search(rf"(?<!\w){re.escape(make)}(?!\w)", flat, re.I))), None)
    said = {latin(w) for w in re.findall(r"\w+", text)}
    match = make = model = None
    if found:
        make = text[found.start():found.end()]
        own = [x for x in models if x["make"].casefold() == found[0].casefold()]
        rest = re.split(r"[,(]|\b(?:19|20)\d\d\b", text[found.end():])[0].split()
        for x in own:
            for alt in x["model"].split(" / ") + [n["name"] for n in x.get("names") or []]:
                if rest and latin(rest[0]) == latin(alt.split()[0]):
                    match, model = x, " ".join(rest[:len(alt.split())])
                elif rest and latin(make + rest[0]) == latin(alt.split()[0]):
                    match, model = x, alt
                if match:
                    break
            if match:
                break
        candidates = [match] if match else own
    elif said & set(CROSSOVER):
        candidates = [x for x in models if x["vehicle_class"] == "suv"]
    else:
        candidates = [x for x in models if any(latin(alt.split()[0]) in said for alt in x["model"].split(" / ") + [n["name"] for n in x.get("names") or []])]
    if not candidates:
        return None
    m = candidates[weighted(shape, {i: x["share"] for i, x in enumerate(candidates)})]
    year = int(year[0]) if year else PARC[b.cfg]["reference_year"] - weighted(shape, ages(b.cfg, m))
    return drawn(b, owner, m, year, shape, words, how, make=make, model=model)


@functools.lru_cache(maxsize=None)
def counter_days(cfg, site, start, end):
    """The days from `start` to before `end` on which the shop is open (spec section 1), with its opening and closing in
    minutes."""
    hours = [tuple(map(int, x.split(":"))) for x in inputs.value("site.hours.weekday", cfg)]
    days, d = [], start
    while d < end:
        if (clock.main_open if site == "main" else clock.full_open)(cfg, d):
            (o_h, o_m), (c_h, c_m) = clock.EN_SATURDAY if cfg == "en" and d.weekday() == 5 else hours
            days.append((d, o_h * 60 + o_m, c_h * 60 + c_m))
        d += clock.DAY
    return days


def created(b, site, rng):
    """A record that exists before any order, made at the counter: at west in the bulk load (purchase day, 08:00 to
    09:00, M11); at a home shop on an open day inside its opening hours, uniform over the ten years before the history
    start, never before the shop opened."""
    if site == "west":
        return dt.datetime.combine(b.a["bought"], dt.time(8)) + dt.timedelta(seconds=rng.randrange(3600))
    start = max(clock.months_back(b.a["history_start"], 120), b.shops[site]["opened_on"])
    day, opens, closes = streams.pick(rng, counter_days(b.cfg, site, start, b.a["history_start"]))
    return dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=rng.randrange(opens, closes))


def pool_size(b, site):
    """spec section 3: (the shop's private background orders a year x erp.customer.returning_share) /
    erp.customer.visits_per_year. Private orders over the shop's window are its orders less the accounts' visits (their
    30-day blocks counted back from T), the small businesses' share and, at west, the walk-in record's orders."""
    cfg, a = b.cfg, b.a
    months = inputs.value("time.west_bought_months" if site == "west" else "time.history_months", cfg)
    blocks = (a["T"].date() - (a["bought"] if site == "west" else a["history_start"])).days / 30
    orders = inputs.value(f"volume.orders_per_month.{site}", cfg) * months
    visits = sum(v[0] * (blocks - 5) + sum(v[1:]) for acct in ACCOUNTS[cfg]["accounts"] if inputs.value(f"acct.{acct['id']}.shop", cfg) == site
                 for v in [inputs.value(f"acct.{acct['id']}.visits", cfg)])
    private = orders - visits - orders * inputs.value("acct.small.orders_share", cfg) / 100 - (inputs.value("s2.walkin.total", cfg) if site == "west" else 0)
    return round(private * 12 / months * inputs.value("erp.customer.returning_share", cfg) / 100 / inputs.value("erp.customer.visits_per_year", cfg))


def fill(b):
    cfg, a = b.cfg, b.a
    T = a["T"].date()

    def walk(node):  # every phone, VIN, plate, e-mail and person's name the seed files give: background draws never repeat one
        for key, value in node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ():
            if isinstance(value, str) and key in ("vin", "plate", "email"):
                b.taken.add(value)
            elif isinstance(value, str) and "phone" in str(key):
                b.taken.add(e164(value))
            elif isinstance(value, str) and key == "name":
                b.taken.add(full_name(value))
            else:
                walk(value)
    walk(ACCOUNTS[cfg])
    walk(NAMED[cfg])
    b.taken.update(r["phone"] for r in [*b.shops.values(), *b.vendors.values()])
    b.taken.update(full_name(" ".join(filter(None, (p["first_name"], p["middle_name"], p["last_name"])))) for p in [*b.people.values(), *b.seasons])
    mix = inputs.value("erp.referral.mix", cfg)

    def deal_referrals(group, sites):  # erp.referral.mix dealt over a group's home records; the bulk load is blank
        labels = iter(deal(streams.stream(b.seed, "deal", group, "referral"), sum(s != "west" for s in sites), mix))
        return [None if s == "west" else b.referrals.get(next(labels)) for s in sites]

    opening = dt.time(*map(int, inputs.value("site.hours.weekday", cfg)[0].split(":")))
    sites = [inputs.value(f"acct.{acct['id']}.shop", cfg) for acct in ACCOUNTS[cfg]["accounts"]]
    for acct, site, referral in zip(ACCOUNTS[cfg]["accounts"], sites, deal_referrals("accounts", sites)):
        i, contacts = acct["id"], acct["contacts"]
        # the earliest contact's start, or the shop's opening when the account is older than its shop
        since = dt.datetime.combine(max(clock.months_back(T, max(c["from_months_before_t"] for c in contacts)), b.shops[site]["opened_on"]), opening)
        b.accounts[i] = b.add(
            "customer", kind="company", name=trade_name(cfg, acct["name"], acct["legal_form"]), phone=e164(acct["phone"]),
            email=next((c["email"] for c in contacts if (c["email"] or "").startswith("ap@")), contacts[0]["email"]), address=acct["address"],
            price_class="company_account" if i in COMPANY_CLASS else "standard", payment_terms_days=inputs.value(f"acct.{i}.terms_days", cfg),
            credit_limit=Decimal(str(inputs.value("kb.acct.credit_limits", cfg)[i])), referral_source_id=referral, created_location_id=b.shops[site],
            created_at=created(b, site, streams.stream(b.seed, "account", i)) if site == "west" else since,
            notes=(inputs.value("kb.acct.standing_instructions", cfg) if cfg == "en" else inputs.value("erp.customer.account_notes", cfg)).get(i))
        for c in contacts:
            start, end = c["from_months_before_t"], c["to_months_before_t"]
            started, ended = clock.months_back(T, start), clock.months_back(T, end) if end is not None else None
            if i == "A6" and end is not None:  # card S01: the old fleet contact leaves the day before P, the new one starts on P
                ended = a["P"] - clock.DAY
            if i == "A6" and any(o["to_months_before_t"] == start for o in contacts):
                started = a["P"]
            b.add("customer_contact", customer_id=b.accounts[i], name=c["name"], role=c["role"], phone=c["phone"] and e164(c["phone"]),
                  email=c["email"], started_on=started, ended_on=ended)
        b.fleets[i] = {f["unit"]: b.add("vehicle", **vehicle(cfg, b.accounts[i], f, unit=f["unit"])) for f in acct["fleet"]}

    small = ACCOUNTS[cfg]["small_business_customers"]
    for n, (s, referral) in enumerate(zip(small, deal_referrals("small", [s["home_shop"] for s in small]))):
        rng = streams.stream(b.seed, "small", n)
        row = b.add("customer", kind="company", name=s["name"], phone=phone(b, s["home_shop"], rng, city=True), address=s["town"],
                    referral_source_id=referral, created_location_id=b.shops[s["home_shop"]], created_at=created(b, s["home_shop"], rng))
        b.small.append((row, [b.add("vehicle", **vehicle(cfg, row, v)) for v in s["vehicles"]]))

    b.walkin = b.add("customer", kind="person", name=WALKIN[cfg], created_location_id=b.shops["west"],
                     created_at=created(b, "west", streams.stream(b.seed, "walk-in")))

    plates = inputs.value("erp.vehicle.plates", cfg)
    mail_share, caps_share = inputs.value("erp.customer.email_share", cfg), inputs.value("erp.west.bulk_caps_share", cfg)
    extra = inputs.value("erp.vehicle.per_private_customer", cfg) - 1
    for site in ("main", "east", "west"):
        n, kind = pool_size(b, site), f"customer.{site}"
        mails = deal(streams.stream(b.seed, "deal", site, "email"), n, {True: mail_share, False: 100 - mail_share})
        caps = deal(streams.stream(b.seed, "deal", site, "caps"), n, {True: caps_share, False: 100 - caps_share}) if site == "west" else [False] * n
        second = deal(streams.stream(b.seed, "deal", site, "second car"), n, {True: extra, False: 1 - extra})
        hows = iter(deal(streams.stream(b.seed, "deal", site, "plate"), n + sum(second),
                         plates["formats"] if cfg == "en" else plates["region_by_shop"][site]))
        referrals = deal_referrals(site, [site] * n)
        b.pools[site] = []
        for i in range(n):
            words = streams.words_stream(b.seed, kind, i)
            name, username = person(b, words, caps[i])
            row = b.add("customer", kind="person", name=name, phone=phone(b, site, words), email=mail(b, username, words) if mails[i] else None,
                        referral_source_id=referrals[i], created_location_id=b.shops[site], created_at=created(b, site, streams.entity_stream(b.seed, kind, i)))
            cars = [b.add("vehicle", **car(b, row, site, streams.entity_stream(b.seed, f"vehicle.{site}", 2 * i + k),
                                           streams.words_stream(b.seed, f"vehicle.{site}", 2 * i + k), next(hows))) for k in range(1 + second[i])]
            b.pools[site].append((row, cars))

    named(b, mix)


def named(b, mix):
    """The named customers of named_customers.json (spec section 3, customer and vehicle): a record that exists before
    any order goes into the tables; a first-time caller's (made at check-in) and a duplicate's second record (made after
    the first record's first order) wait in `b.pending` for the step that dates them. A driver of an account is not a
    customer. A story car is read by `story_car`, or drawn when the file names none."""
    cfg = b.cfg
    files = NAMED[cfg]
    regions = inputs.value("erp.vehicle.plates", cfg).get("region_by_shop")
    fleet_plates = [v["plate"] for units in b.fleets.values() for v in units.values()]

    def record(key, name, site, phone_text=None, email=None, pending=False):
        rng = streams.stream(b.seed, "named", key)
        row = dict(kind="person", name=name, phone=phone_text and e164(phone_text), email=email, created_location_id=b.shops.get(site),
                   referral_source_id=None if site == "west" else b.referrals.get(weighted(rng, mix)))
        if not pending:
            row["created_at"] = created(b, site, rng)
        return row

    def keep(key, row, cars, pending=False):
        (b.pending if pending else b.named)[key] = (row, cars)
        if not pending:
            b.tables["customer"].append(row)
            b.tables["vehicle"].extend(cars)

    for key, file_key in (("S7", "S7"), ("S8", "S8"), ("S6", "S6_waiting_nine_days")):
        x = files[file_key]
        row = record(key, x["name"], x["shop"], x["phone"], x["email"])
        keep(key, row, [vehicle(cfg, row, x["car"])])
    for x in files["S15_duplicate_pairs"]:
        for side in ("a", "b"):
            key = f"dup.{x['pair']}.{side}"
            row = record(key, x[f"record_{side}"]["name"], x[f"record_{side}"]["created_at_shop"], x["shared_phone"], pending=side == "b")
            keep(key, row, [vehicle(cfg, row, x["car"])], pending=side == "b")
    for x in files["S15_car_on_the_wrong_customer"]:
        if isinstance(x["car"], dict):  # case 1: the owner's record and car; case 2's car is a small business's
            row = record(f"m8.{x['case']}.owner", x["belongs_to"]["name"], x["shop"], x["belongs_to"]["phone"])
            keep(f"m8.{x['case']}.owner", row, [vehicle(cfg, row, x["car"])])
        under = x["order_recorded_under"]
        keep(f"m8.{x['case']}.under", record(f"m8.{x['case']}.under", under["name"], x["shop"], under["phone"]), [])

    for kind, group in (("calls", "story_callers"), ("conversations", "story_chat_customers")):
        for x in files[group]:
            number = int(re.search(r"/(\d\d)-", x["source"])[1])
            key = f"{kind[:4]}.{number:02d}"
            text = x["car"]
            if text and any(p in text for p in fleet_plates):
                continue
            story = inputs.STORY_FILES[kind, cfg][number]
            site = x["shop"] or (story["call"]["site"] if kind == "calls" else story["conversations"][0]["clock"])
            row = record(key, x["name"], site, x["phone"], pending=bool(x["first_time"]))
            shape, words = streams.stream(b.seed, "named car", key), streams.stream(b.seed, "named car words", key)
            how = "named" if cfg == "en" else weighted(words, regions[site])
            got = car(b, row, site, shape, words, how) if text is None else story_car(b, row, text, shape, words, how)
            keep(key, row, [got] if got else [], bool(x["first_time"]))
