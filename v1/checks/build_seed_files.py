# Authoring helper for demo seed v1 wave 1: turns hand-written specs into accounts.json,
# named_customers.json, vendors.json and cast.md. Deterministic (fixed seeds). Not product code.
import json, random, sys, os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = {**{2001 + i: str(i + 1) for i in range(9)}, **dict(zip(range(2010, 2031), "ABCDEFGHJKLMNPRSTVWXY")), 2000: "Y", 1999: "X", 1998: "W", 1997: "V"}
TR = {**{str(i): i for i in range(10)}, **dict(zip("ABCDEFGH", range(1, 9))), **dict(zip("JKLMN", range(1, 6))), "P": 7, "R": 9, **dict(zip("STUVWXYZ", range(2, 10)))}
W = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

def us_vin(wmi, vds, year, plant, serial):
    v = wmi + vds + "0" + YEAR[year] + plant + serial
    assert len(v) == 17, v
    c = sum(TR[ch] * w for ch, w in zip(v, W)) % 11
    return v[:8] + ("X" if c == 10 else str(c)) + v[9:]

rv = random.Random(20261113)
def digits(n): return "".join(rv.choice("0123456789") for _ in range(n))
def fser(): return rv.choice("AB") + digits(5)        # Ford style: letter + five digits
def nser(): return str(rv.randint(1, 8)) + digits(5)  # six digits

# key: (make, model, wmi, vds by year, plant, serial fn)
US = {
 "transit250": ("Ford", "Transit-250 Cargo Van", "1FT", lambda y: "BR1C8", "K", fser),
 "tconnect": ("Ford", "Transit Connect Cargo Van", "NM0", lambda y: "LS7E2", "1", nser),
 "f150": ("Ford", "F-150", "1FT", lambda y: "EW1E5", "F", fser),
 "f250": ("Ford", "F-250 Super Duty", "1FT", lambda y: "7W2B6", "E", fser),
 "f350": ("Ford", "F-350 Super Duty", "1FT", lambda y: "8W3BT", "E", fser),
 "ranger": ("Ford", "Ranger", "1FT", lambda y: "ER4EH", "P", fser),
 "escape": ("Ford", "Escape", "1FM", lambda y: "CU9GD", "U", fser),
 "explorer": ("Ford", "Explorer", "1FM", lambda y: "5K8D8", "G", fser),
 "pm2500": ("Ram", "ProMaster 2500 Cargo Van", "3C6", lambda y: "TRVDG", "E", nser),
 "pm1500": ("Ram", "ProMaster 1500 Cargo Van", "3C6", lambda y: "TRVAG", "E", nser),
 "pmcity": ("Ram", "ProMaster City", "ZFB", lambda y: "HRFAB", "6", nser),
 "ram1500": ("Ram", "1500", "1C6", lambda y: "RR7FT", "S", nser),
 "ram2500": ("Ram", "2500", "3C6", lambda y: "UR5DL", "G", nser),
 "sprinter": ("Mercedes-Benz", "Sprinter 2500 Cargo Van", None, lambda y: "4ECHY" if y >= 2020 else "PE7CD", "P", nser),
 "express2500": ("Chevrolet", "Express 2500 Cargo Van", "1GC", lambda y: "WGAFP", "1", nser),
 "express3500": ("Chevrolet", "Express 3500 Cutaway", "1GB", lambda y: "0GRFG", "1", nser),
 "silv2500": ("Chevrolet", "Silverado 2500HD", "1GC", lambda y: "1KVEG", "F", nser),
 "silv1500": ("Chevrolet", "Silverado 1500", "1GC", lambda y: "RYDED", "Z", nser),
 "colorado": ("Chevrolet", "Colorado", "1GC", lambda y: "GSBEA", "1", nser),
 "equinox": ("Chevrolet", "Equinox", "2GN", lambda y: "AXKEV", "6", nser),
 "nv200": ("Nissan", "NV200 Compact Cargo", "3N6", lambda y: "CM0KN", "K", nser),
 "sentra": ("Nissan", "Sentra", "3N1", lambda y: "AB8CV", "Y", nser),
 "versa": ("Nissan", "Versa", "3N1", lambda y: "CN7AP", "L", nser),
 "altima": ("Nissan", "Altima", "1N4", lambda y: "BL4CV", "N", nser),
 "rogue": ("Nissan", "Rogue", "5N1", lambda y: "AT2MT", "C", nser),
 "corolla": ("Toyota", "Corolla", "5YF", lambda y: "EPMAE" if y >= 2020 else "BURHE", "P", nser),
 "camry": ("Toyota", "Camry", "4T1", lambda y: "B11HK", "U", nser),
 "sienna": ("Toyota", "Sienna", "5TD", lambda y: "KZ3DC", "S", nser),
 "tacoma": ("Toyota", "Tacoma", "5TF", lambda y: "CZ5AN", "X", nser),
 "tundra": ("Toyota", "Tundra", "5TF", lambda y: "DW5F1", "X", nser),
 "rav4": ("Toyota", "RAV4", "2T3", lambda y: "BFREV", "W", nser),
 "elantra": ("Hyundai", "Elantra", "5NP", lambda y: "LL4AG" if y >= 2021 else "D84LF", "H", nser),
 "civic": ("Honda", "Civic", "2HG", lambda y: "FC2F6", "H", nser),
 "accord": ("Honda", "Accord", "1HG", lambda y: "CR2F3", "A", nser),
 "odyssey": ("Honda", "Odyssey", "5FN", lambda y: "RL5H6", "B", nser),
 "crv": ("Honda", "CR-V EX AWD", "2HK", lambda y: "RM4H5", "H", nser),
 "soul": ("Kia", "Soul", "KND", lambda y: "J23AU", "7", nser),
 "outback11": ("Subaru", "Outback 2.5i Premium", "4S4", lambda y: "BRBCC", "3", nser),
 "outback": ("Subaru", "Outback", "4S4", lambda y: "BTAFC", "3", nser),
 "xc60": ("Volvo", "XC60 T6 AWD", "YV4", lambda y: "902DZ", "2", nser),
}

# Each car's model in parc.json (its price class and engines come from there), or the class itself for a model the parc lacks.
PARC = {cfg: {(m["make"], m["model"]): m["vehicle_class"] for m in c["models"]} for cfg, c in json.load(open(os.path.join(OUT, "parc.json"), encoding="utf-8"))["configurations"].items()}
US_PARC = {"transit250": "Transit 150 / 250 / 350", "tconnect": "Transit Connect", "f150": "F-150", "f250": "F-250 Super Duty", "f350": "F-250 Super Duty", "ranger": "truck",
 "escape": "Escape", "explorer": "Explorer", "pm2500": "ProMaster 1500 / 2500", "pm1500": "ProMaster 1500 / 2500", "pmcity": "van", "ram1500": "1500", "ram2500": "truck",
 "sprinter": "Sprinter 2500", "express2500": "Express 2500", "express3500": "Express 2500", "silv2500": "Silverado 2500HD", "silv1500": "Silverado 1500", "colorado": "Colorado",
 "equinox": "Equinox", "nv200": "van", "sentra": "Sentra", "versa": "Versa", "altima": "Altima", "rogue": "Rogue", "corolla": "Corolla", "camry": "Camry", "sienna": "Sienna",
 "tacoma": "Tacoma", "tundra": "Tundra", "rav4": "RAV4", "elantra": "Elantra", "civic": "Civic", "accord": "Accord", "odyssey": "Odyssey", "crv": "CR-V", "soul": "Soul",
 "outback11": "Outback", "outback": "Outback", "xc60": "XC60 / XC90"}
RU_PARC = {"next_van": "ГАЗель Next", "next_iso": "ГАЗель Next", "next_bort": "ГАЗель Next", "nn_van": "ГАЗель Next", "biz_van": "ГАЗель (3302 / 2705), включая «Бизнес»",
 "biz_bort": "ГАЗель (3302 / 2705), включая «Бизнес»", "largus_van": "Largus фургон", "largus": "Largus универсал", "granta": "Granta", "granta_sw": "Granta", "vesta": "Vesta",
 "vesta_sw": "Vesta", "niva": "Niva Legend (2121 / 21213 / 21214)", "vaz2114": "2108 / 2109 / 21099 и 2113 / 2114 / 2115 (Samara)", "uaz3909": "СГР «Буханка» (3909 / 2206 / 3303)",
 "uaz_profi": "truck", "patriot": "Patriot", "transit": "Transit", "focus": "Focus I / II / III", "jumper": "van", "p308": "car", "logan": "Logan", "duster": "Duster", "rio": "Rio",
 "solaris": "Solaris", "polo": "Polo седан", "rapid": "Rapid", "xtrail": "X-Trail", "outlander": "Outlander", "nexia": "Nexia"}
PARC_MAKE = {"LADA": "Lada", "Škoda": "Skoda"}
def classed(cfg, key, make):
    where = (US_PARC if cfg == "en" else RU_PARC)[key]
    if where in ("car", "suv", "truck", "van"):
        return {"vehicle_class": where, "parc_model": None}
    return {"vehicle_class": PARC[cfg][PARC_MAKE.get(make, make), where], "parc_model": where}

def us_car(key, year, novin=False):
    make, model, wmi, vds, plant, ser = US[key]
    if key == "sprinter": wmi = "W1Y" if year >= 2020 else "WD3"
    return {"make": make, "model": model, "year": year, "vin": None if novin else us_vin(wmi, vds(year), year, plant, ser()), **classed("en", key, make)}

# Russian market: WMI of the plant that built the model for Russia + a descriptor in the maker's style.
def y(c): return YEAR[c]
RU = {
 "next_van": ("ГАЗ", "ГАЗель Next, цельнометаллический фургон", lambda yr: "X96A31R32" + y(yr) + "0" + digits(6)),
 "next_iso": ("ГАЗ", "ГАЗель Next, изотермический фургон", lambda yr: "X96A21R22" + y(yr) + "0" + digits(6)),
 "next_bort": ("ГАЗ", "ГАЗель Next, бортовая", lambda yr: "X96A21R22" + y(yr) + "0" + digits(6)),
 "nn_van": ("ГАЗ", "ГАЗель NN, цельнометаллический фургон", lambda yr: "X96A31R35" + y(yr) + "0" + digits(6)),
 "biz_van": ("ГАЗ", "ГАЗель Бизнес 2705, фургон", lambda yr: "X96270500" + y(yr) + "0" + digits(6)),
 "biz_bort": ("ГАЗ", "ГАЗель Бизнес 3302, бортовая", lambda yr: "X96330200" + y(yr) + "0" + digits(6)),
 "largus_van": ("LADA", "Largus, фургон", lambda yr: "XTAFS045L" + y(yr) + digits(7)),
 "largus": ("LADA", "Largus, универсал", lambda yr: "XTAKS045L" + y(yr) + digits(7)),
 "granta": ("LADA", "Granta, седан", lambda yr: "XTA219010" + y(yr) + "0" + digits(6)),
 "granta_sw": ("LADA", "Granta, универсал", lambda yr: "XTA219410" + y(yr) + "0" + digits(6)),
 "vesta": ("LADA", "Vesta, седан", lambda yr: "XTAGFL110" + y(yr) + ("0" if yr >= 2023 else "Y") + digits(6)),
 "vesta_sw": ("LADA", "Vesta SW", lambda yr: "XTAGFK110" + y(yr) + ("0" if yr >= 2023 else "Y") + digits(6)),
 "niva": ("LADA", "Niva Legend", lambda yr: "XTA212140" + y(yr) + "0" + digits(6)),
 "vaz2114": ("LADA", "2114", lambda yr: "XTA211440" + y(yr) + "0" + digits(6)),
 "uaz3909": ("УАЗ", "3909", lambda yr: "XTT390995" + y(yr) + "1" + digits(6)),
 "uaz_profi": ("УАЗ", "Профи", lambda yr: "XTT236020" + y(yr) + "1" + digits(6)),
 "patriot": ("УАЗ", "Патриот", lambda yr: "XTT316300" + y(yr) + "1" + digits(6)),
 "transit": ("Ford", "Transit, фургон", lambda yr: "Z6FXXXESGX" + y(yr) + rv.choice("BCDEJKLMPRSTUY") + digits(5)),
 "focus": ("Ford", "Focus", lambda yr: "X9FMXXEEBM" + y(yr) + rv.choice("BCDEJKLMPRSTUY") + digits(5)),
 "jumper": ("Citroën", "Jumper, фургон", lambda yr: "VF7YCUMFC12" + digits(6)),
 "p308": ("Peugeot", "308", lambda yr: "VF34C5FS9" + y(yr) + "S" + digits(6)),
 "logan": ("Renault", "Logan", lambda yr: "X7L4SRAV4" + digits(8)),
 "duster": ("Renault", "Duster", lambda yr: "X7LHSRH8N" + digits(8)),
 "rio": ("Kia", "Rio", lambda yr: ("Z94C241BB" if yr >= 2017 else "Z94CB41BA") + y(yr) + "R" + digits(6)),
 "solaris": ("Hyundai", "Solaris", lambda yr: ("Z94K241CB" if yr >= 2017 else "Z94CT41DA") + y(yr) + "R" + digits(6)),
 "polo": ("Volkswagen", "Polo, седан", lambda yr: "XW8ZZZ61Z" + y(yr) + "G" + digits(6)),
 "rapid": ("Škoda", "Rapid", lambda yr: "XW8AG2NH5" + y(yr) + "K" + digits(6)),
 "xtrail": ("Nissan", "X-Trail", lambda yr: "Z8NTANT32" + y(yr) + "S" + digits(6)),
 "outlander": ("Mitsubishi", "Outlander", lambda yr: "Z8TXTGF3W" + y(yr) + "M" + digits(6)),
 "nexia": ("Daewoo", "Nexia", lambda yr: "XWB3L32CD" + y(yr) + "A" + digits(6)),
}
def ru_car(key, year, novin=False):
    make, model, fn = RU[key]
    vin = fn(year)
    assert len(vin) == 17, (key, vin)
    return {"make": make, "model": model, "year": year, "vin": None if novin else vin, **classed("ru", key, make)}

# Plates. Tennessee: serials BRC-2190..BRC-8000 were never issued (Wikipedia, Vehicle registration plates of Tennessee).
rp = random.Random(73116)
_tn = rp.sample(range(2190, 8001), 400)
def tn_plate(): return "BRC-%04d" % _tn.pop()
L = "АВЕКМНОРСТУХ"
_seen = set()
def ru_plate(regions):
    while True:
        a, b, c = rp.choice(L), rp.choice(L), rp.choice(L)
        n = rp.randint(102, 987)
        if a == b == c or len(set(str(n))) == 1: continue
        p = "%s%03d%s%s%s" % (a, n, b, c, rp.choice(regions))
        if p not in _seen:
            _seen.add(p); return p
ULY, KZN = ["73", "73", "173"], ["116", "716", "16", "716"]

# Phones (phones.md). English: tier A, NPA-555-01XX. Russian: mobiles in reserve code 907, city numbers starting with 1.
ph = random.Random(555)
_a = {"423": [n for n in ph.sample(range(100, 200), 100) if n not in (142, 167)], "615": [n for n in ph.sample(range(100, 200), 100) if n != 119]}
def us_phone(npa): return "(%s) 555-%04d" % (npa, _a[npa].pop())
_m = set()
def ru_mobile():
    while True:
        s = "%03d-%02d-%02d" % (ph.randint(200, 989), ph.randint(10, 98), ph.randint(10, 98))
        if s not in _m:
            _m.add(s); return "+7 907 " + s
def ru_city(city):
    if city == "uly": return "+7 (8422) 1%d-%02d-%02d" % (ph.randint(1, 9), ph.randint(10, 98), ph.randint(10, 98))
    return "+7 (843) 1%02d-%02d-%02d" % (ph.randint(10, 98), ph.randint(10, 98), ph.randint(10, 98))

def fleet(cfg, unit_fmt, items, miles, regions=None, flags=None):
    out, i = [], 0
    for key, years in items:
        for yr in years:
            i += 1
            car = us_car(key, yr) if cfg == "en" else ru_car(key, yr)
            unit = unit_fmt % i
            row = {"unit": unit, **car, "plate": tn_plate() if cfg == "en" else ru_plate(regions)}
            row["typical_yearly_" + ("miles" if cfg == "en" else "km")] = miles.get(key, miles["*"])
            if flags and unit in flags: row.update(flags[unit])
            out.append(row)
    return out

def contact(cfg, name, role, frm, to, domain, local, npa_or_city, mobile=True):
    c = {"name": name, "role": role, "from_months_before_t": frm, "to_months_before_t": to}
    c["phone"] = us_phone(npa_or_city) if cfg == "en" else ru_mobile()
    c["email"] = "%s@%s.example" % (local, domain)
    return c

DESIGN = {
 "A1": ("big, the anchor", "healthy, the largest single customer; pays later every month (about 30 days, now about 50)"),
 "A2": ("big", "healthy, the most frequent visitor; standing weekly slot"),
 "A3": ("medium", "healthy"),
 "A4": ("medium", "healthy, growing"),
 "A5": ("medium, left", "no visit for four and a half months"),
 "A6": ("medium, fading", "from eight visits a month to one over five months"),
}

def account(cfg, aid, kind, name, legal_form, shop, address, terms, domain, city, contacts, fl):
    size, state = DESIGN[aid]
    return {"id": aid, "kind": kind, "size": size, "state_at_t": state, "name": name, "legal_form": legal_form,
            "home_shop": shop, "address": address,
            "phone": us_phone(city) if cfg == "en" else ru_city(city), "email_domain": domain + ".example",
            "payment_terms_days": terms,
            "contacts": [contact(cfg, *c[:4], domain, c[4], city) for c in contacts],
            "fleet_count": len(fl), "fleet": fl}

BRAKE = {"story": "S1/S6: brake job at `west` that came back (T-6 and T-5 months), done by slot 27"}
JOIN8, JOIN3 = {"joined_fleet_months_before_t": 8}, {"joined_fleet_months_before_t": 3}

en_accounts = [
 account("en", "A1", "delivery service", "Nickajack Delivery", "LLC", "main", "4310 Amnicola Hwy, Chattanooga, TN 37406", 30, "nickajackdelivery", "423",
  [("Lonnie Coffey", "Fleet Manager", 48, None, "lcoffey"), ("Linda Qualls", "Accounts Payable", 62, None, "ap"), ("Stuart Haney", "Director of Operations", 90, None, "shaney")],
  fleet("en", "ND-%02d", [("transit250", [2019]*3 + [2020]*4 + [2021]*4 + [2022]*4 + [2023]*3), ("pm2500", [2019]*2 + [2020]*3 + [2021]*3 + [2022]*2 + [2023]), ("tconnect", [2018, 2019, 2020, 2021]), ("sprinter", [2019, 2020])], {"*": 28000, "tconnect": 22000})),
 account("en", "A2", "heating and plumbing service company", "Millsaps Heating & Plumbing", "Inc.", "east", "6120 Bonny Oaks Dr, Chattanooga, TN 37416", 30, "millsapshp", "423",
  [("Tina Ragsdale", "Dispatcher (books the weekly slot)", 70, None, "dispatch"), ("Hal Millsaps", "President", 300, None, "hal"), ("Joyce Millsaps", "Office Manager, payables", 240, None, "office")],
  fleet("en", "M-1%02d", [("express2500", [2015, 2015, 2016, 2017, 2017, 2018, 2019, 2020, 2022]), ("transit250", [2017, 2018, 2019, 2019, 2020, 2021, 2021, 2023]), ("pm1500", [2019, 2020, 2022]), ("f250", [2016, 2019, 2021]), ("escape", [2019, 2021])], {"*": 18000, "f250": 15000, "escape": 14000})),
 account("en", "A3", "cleaning company", "Moccasin Bend Janitorial Services", "LLC", "main", "2330 Rossville Blvd, Chattanooga, TN 37408", 15, "moccasinbendjanitorial", "423",
  [("Yolanda Fitch", "Operations Manager", 36, None, "yfitch"), ("Dennis Fitch", "Owner", 132, None, "dennis")],
  fleet("en", "MB-%d", [("tconnect", [2016, 2018, 2020]), ("nv200", [2017, 2019]), ("soul", [2018, 2020]), ("express2500", [2015]), ("corolla", [2019])], {"*": 13000, "express2500": 9000})),
 account("en", "A4", "driving school", "Missionary Ridge Driving School", "LLC", "east", "5512 Brainerd Rd, Chattanooga, TN 37411", 15, "missionaryridgedriving", "423",
  [("Denise Atchley", "Owner", 110, None, "denise"), ("Rob Atchley", "Lead Instructor, looks after the cars", 110, None, "rob")],
  fleet("en", "Car %d", [("corolla", [2019, 2021]), ("elantra", [2020, 2022]), ("sentra", [2021]), ("civic", [2018]), ("corolla", [2023]), ("sentra", [2024])], {"*": 17000}, flags={"Car 7": JOIN8, "Car 8": JOIN3})),
 account("en", "A5", "electrical contractor", "Cumberland Bend Electric", "LLC", "west", "5745 Centennial Blvd, Nashville, TN 37209", 30, "cumberlandbendelectric", "615",
  [("Wade Carlisle", "Operations Manager (the caller who was not called back)", 40, None, "wcarlisle"), ("Sherry Lane", "Bookkeeper", 85, None, "accounting")],
  fleet("en", "E-%d", [("express2500", [2014, 2016, 2017, 2019]), ("transit250", [2018, 2020, 2021]), ("f150", [2017, 2020]), ("pm2500", [2019]), ("silv2500", [2016])], {"*": 20000}, flags={"E-2": BRAKE, "E-6": BRAKE})),
 account("en", "A6", "catering company", "Sourwood Catering Co.", "LLC", "main", "1612 E 23rd St, Chattanooga, TN 37404", 30, "sourwoodcatering", "423",
  [("Bobby Shadden", "Kitchen and Fleet Manager (the old fleet contact)", 52, 5, "bshadden"), ("Erin Castillo", "Operations Coordinator (the new fleet contact)", 5, None, "ecastillo"), ("Marianne Tolliver", "Owner, Executive Chef; pays the bills", 96, None, "marianne")],
  fleet("en", "SC-%d", [("transit250", [2018, 2020, 2022]), ("pm2500", [2019, 2021]), ("tconnect", [2017, 2019]), ("express3500", [2015, 2017]), ("sienna", [2018])], {"*": 14000})),
]

ru_accounts = [
 account("ru", "A1", "служба доставки", "Симбирский гонец", "ООО", "main", "г. Ульяновск, ул. Локомотивная, 14", 30, "simbirsky-gonets", "uly",
  [("Олег Вячеславович Кравцов", "начальник транспортного отдела", 48, None, "kravtsov"), ("Надежда Ивановна Зотова", "бухгалтер по расчётам с поставщиками", 62, None, "buh"), ("Тимур Рашидович Бикмаев", "исполнительный директор", 90, None, "bikmaev")],
  fleet("ru", "%02d", [("next_van", [2018]*2 + [2019]*3 + [2020]*3 + [2021]*3 + [2022]*2 + [2023]), ("nn_van", [2022]*2 + [2023]*2 + [2024]*2), ("largus_van", [2017, 2018, 2018, 2019, 2019, 2020, 2021, 2021]), ("transit", [2017, 2018, 2019, 2021]), ("biz_van", [2014, 2015, 2016])], {"*": 50000, "largus_van": 40000}, ULY)),
 account("ru", "A2", "сервисная компания (отопление и сантехника)", "Тёплый контур", "ООО", "east", "г. Ульяновск, пр-т Гая, 71", 30, "teply-kontur", "uly",
  [("Лариса Геннадьевна Шишкина", "диспетчер (записывает машины на еженедельное окно)", 70, None, "dispetcher"), ("Виктор Семёнович Агафонов", "директор", 180, None, "agafonov"), ("Ольга Петровна Агафонова", "главный бухгалтер", 170, None, "buh")],
  fleet("ru", "Т-%02d", [("largus_van", [2016, 2017, 2017, 2018, 2018, 2019, 2019, 2020, 2021, 2021]), ("granta_sw", [2018, 2019, 2021, 2022]), ("next_bort", [2017, 2020]), ("next_van", [2019, 2021]), ("niva", [2019, 2021, 2023]), ("uaz3909", [2017, 2020]), ("duster", [2017, 2019])], {"*": 28000}, ULY)),
 account("ru", "A3", "клининговая компания", "Чистый Венец", "ООО", "main", "г. Ульяновск, ул. Радищева, 140", 14, "chisty-venets", "uly",
  [("Гульнара Наилевна Садыкова", "управляющая", 36, None, "sadykova"), ("Борис Игоревич Лебедев", "директор, владелец", 110, None, "lebedev")],
  fleet("ru", "%d", [("largus", [2017, 2019, 2021]), ("largus_van", [2018]), ("granta", [2019, 2022]), ("next_van", [2018]), ("rio", [2018]), ("logan", [2017])], {"*": 18000}, ULY)),
 account("ru", "A4", "автошкола", "Автошкола «Первая передача»", "ООО", "east", "г. Ульяновск, пр-т Созидателей, 17", 14, "pervaya-peredacha", "uly",
  [("Елена Анатольевна Мартьянова", "директор", 110, None, "direktor"), ("Юрий Николаевич Тюрин", "старший мастер производственного обучения, отвечает за автомобили", 96, None, "tyurin")],
  fleet("ru", "Учебный %d", [("granta", [2019, 2020, 2022]), ("vesta", [2021]), ("logan", [2018]), ("rio", [2019]), ("vesta", [2023]), ("granta", [2024])], {"*": 30000}, ULY, flags={"Учебный 7": JOIN8, "Учебный 8": JOIN3})),
 account("ru", "A5", "электромонтажная компания", "Идель-Электромонтаж", "ООО", "west", "г. Казань, ул. Тихорецкая, 9", 30, "idel-elektromontazh", "kzn",
  [("Рустем Ильгизович Фаттахов", "заместитель директора по производству (тот, кому не перезвонили)", 40, None, "fattakhov"), ("Алсу Маратовна Гайнутдинова", "бухгалтер", 85, None, "buh")],
  fleet("ru", "Э-%d", [("next_van", [2018, 2020]), ("next_bort", [2019]), ("largus_van", [2017, 2019, 2021]), ("uaz3909", [2016]), ("uaz_profi", [2019]), ("niva", [2020]), ("transit", [2018]), ("duster", [2018])], {"*": 30000}, KZN, flags={"Э-1": BRAKE, "Э-10": BRAKE})),
 account("ru", "A6", "кейтеринговая компания", "Вкусный выезд", "ООО", "main", "г. Ульяновск, ул. Минаева, 32", 30, "vkusny-vyezd", "uly",
  [("Геннадий Павлович Лукьянов", "заведующий хозяйством, отвечал за транспорт (прежний контакт)", 52, 5, "lukyanov"), ("Дарья Олеговна Вершинина", "менеджер по логистике (новый контакт)", 5, None, "vershinina"), ("Марина Александровна Белоусова", "директор, шеф-повар; согласует оплату", 96, None, "belousova")],
  fleet("ru", "%d", [("next_iso", [2018, 2020, 2022]), ("largus_van", [2018, 2019, 2021]), ("transit", [2019]), ("jumper", [2017]), ("solaris", [2019]), ("vesta_sw", [2020])], {"*": 20000}, ULY)),
]

def sb(cfg, rows, regions_by_shop=None):
    out = []
    for name, kind, town, shop, cars in rows:
        vs = []
        for key, yr in cars:
            car = us_car(key, yr) if cfg == "en" else ru_car(key, yr)
            car["plate"] = tn_plate() if cfg == "en" else ru_plate(KZN if shop == "west" else ULY)
            vs.append(car)
        out.append({"name": name, "kind": kind, "town": town, "home_shop": shop, "vehicles": vs})
    return out

en_small = sb("en", [
 ("Greeson Lawn & Landscape", "landscaping", "Hixson, TN", "main", [("f250", 2017), ("silv1500", 2019)]),
 ("Tellico Pest Solutions", "pest control", "Chattanooga, TN", "east", [("ranger", 2020), ("tacoma", 2018), ("ranger", 2022)]),
 ("Clabough Brothers Roofing", "roofing", "Chattanooga, TN", "main", [("ram2500", 2016), ("f150", 2019)]),
 ("Cloudland Pool Service", "pool service", "Chattanooga, TN", "east", [("tconnect", 2018), ("tacoma", 2017)]),
 ("Hales Bar Lock & Key", "locksmith", "Chattanooga, TN", "main", [("tconnect", 2017)]),
 ("Dogwood Lane Florals", "florist", "Chattanooga, TN", "main", [("pmcity", 2019)]),
 ("Raccoon Mountain Home Inspections", "home inspection", "Chattanooga, TN", "main", [("rav4", 2018)]),
 ("Suck Creek Tree Service", "tree service", "Chattanooga, TN", "main", [("f350", 2015), ("silv2500", 2018)]),
 ("Wauhatchie Mobile Grooming", "mobile pet grooming", "Chattanooga, TN", "main", [("sprinter", 2019)]),
 ("Ooltewah Bread Company", "bakery", "Ooltewah, TN", "east", [("transit250", 2018), ("tconnect", 2020)]),
 ("Red Bank Sign Works", "sign shop", "Red Bank, TN", "main", [("f250", 2014), ("transit250", 2019)]),
 ("Kirkland & Daughters Painting", "painting contractor", "Chattanooga, TN", "east", [("express2500", 2016), ("transit250", 2020)]),
 ("Soddy Appliance Repair", "appliance repair", "Soddy-Daisy, TN", "main", [("express2500", 2015), ("nv200", 2018)]),
 ("Ringgold Road Carpet Care", "carpet cleaning", "East Ridge, TN", "main", [("express2500", 2017), ("transit250", 2021)]),
 ("St. Elmo Property Management", "property management", "Chattanooga, TN", "main", [("f150", 2018), ("tconnect", 2019)]),
 ("Battlefield Flooring", "flooring installer", "East Ridge, TN", "east", [("pm2500", 2018), ("f150", 2016)]),
 ("Walden Mobile Vet", "mobile veterinarian", "Signal Mountain, TN", "main", [("tconnect", 2019)]),
 ("Dallas Bay Dock Repair", "dock building and repair", "Hixson, TN", "main", [("f250", 2017), ("silv2500", 2015)]),
 ("Apison Fence Company", "fencing", "Apison, TN", "east", [("silv2500", 2019), ("f350", 2017), ("ram1500", 2021)]),
 ("Frazier Avenue Coffee Roasters", "coffee roaster", "Chattanooga, TN", "main", [("tconnect", 2020)]),
 ("Hamill Road Handyman", "handyman", "Hixson, TN", "main", [("colorado", 2019)]),
 ("Newsom Station Landscaping", "landscaping", "Nashville, TN", "west", [("silv2500", 2017), ("f150", 2020)]),
 ("Sylvan Heights Painting", "painting contractor", "Nashville, TN", "west", [("transit250", 2019)]),
 ("White Bridge Pharmacy", "independent pharmacy (delivery cars)", "Nashville, TN", "west", [("soul", 2019), ("versa", 2021)]),
 ("Richland Creek Florist", "florist", "Nashville, TN", "west", [("tconnect", 2018)]),
 ("Cockrill Bend Courier", "courier", "Nashville, TN", "west", [("pmcity", 2019), ("pmcity", 2021), ("tconnect", 2020)]),
 ("Lankford Heating & Air", "heating and air contractor", "Nashville, TN", "west", [("express2500", 2016), ("express2500", 2019), ("silv1500", 2018)]),
 ("Kingston Springs Tree Care", "tree service", "Kingston Springs, TN", "west", [("f350", 2016)]),
 ("Pasquo Lock & Key", "locksmith", "Nashville, TN", "west", [("nv200", 2019)]),
 ("Dozier Drywall", "drywall contractor", "Nashville, TN", "west", [("f150", 2015), ("ram1500", 2019)]),
])

ru_small = sb("ru", [
 ("ИП Сафиуллин Р. Н.", "доставка питьевой воды", "Ульяновск", "main", [("next_van", 2019), ("largus_van", 2018)]),
 ("ИП Кузьмичёв А. В.", "натяжные потолки", "Ульяновск", "main", [("largus_van", 2019)]),
 ("ИП Абрамова Е. С.", "цветочный салон с доставкой", "Ульяновск", "main", [("largus_van", 2020)]),
 ("ИП Юнусов Ф. Р.", "грузоперевозки по городу", "Ульяновск", "east", [("biz_bort", 2014), ("next_bort", 2018)]),
 ("ИП Трофимов Д. А.", "установка окон и дверей", "Ульяновск", "main", [("next_bort", 2017), ("granta", 2019)]),
 ("ИП Мясникова О. П.", "пекарня", "Ульяновск", "east", [("largus_van", 2017), ("next_van", 2021)]),
 ("ИП Назмутдинов И. И.", "ремонт бытовой техники на дому", "Ульяновск", "main", [("granta", 2018), ("granta", 2021)]),
 ("ИП Чекалин С. В.", "такси, три машины", "Ульяновск", "east", [("solaris", 2018), ("rio", 2019), ("polo", 2019)]),
 ("ИП Кириллов В. Н.", "доставка стройматериалов", "Ульяновск", "main", [("next_bort", 2019)]),
 ("ИП Бикбаева Г. Ш.", "швейный цех", "Ульяновск", "main", [("largus", 2018)]),
 ("ИП Ерофеев М. Ю.", "сборка и доставка мебели", "Ульяновск", "east", [("next_van", 2018), ("largus_van", 2021)]),
 ("ИП Хайруллин Д. Р.", "вывоз мусора, услуги грузчиков", "Ульяновск", "main", [("biz_bort", 2015)]),
 ("ИП Соловьёва Т. Г.", "кондитерская", "Ульяновск", "main", [("largus_van", 2019)]),
 ("ИП Петрухин Н. С.", "пасека, фермерские продукты", "Ульяновская область, Чердаклинский район", "east", [("niva", 2018), ("uaz3909", 2015)]),
 ("ИП Гайсин Р. Ф.", "ремонт квартир", "Ульяновск", "east", [("largus", 2017), ("next_bort", 2020)]),
 ("ООО «ВентКлимат-Симбирск»", "вентиляция и кондиционеры", "Ульяновск", "main", [("largus_van", 2018), ("next_van", 2020)]),
 ("ООО «Пожтехконтроль 73»", "монтаж и обслуживание пожарной сигнализации", "Ульяновск", "main", [("niva", 2019), ("largus_van", 2020)]),
 ("ООО «ГеоСимбирск»", "кадастровые и геодезические работы", "Ульяновск", "main", [("patriot", 2018), ("niva", 2021)]),
 ("ООО «Кофе-вендинг 73»", "кофейные автоматы", "Ульяновск", "east", [("largus_van", 2019), ("largus_van", 2021)]),
 ("ООО «Дезцентр Волга»", "дезинфекция и дератизация", "Ульяновск", "main", [("granta", 2020)]),
 ("ИП Маркелов А. А.", "монтаж видеонаблюдения", "Ульяновск", "main", [("logan", 2016)]),
 ("ИП Гарифуллин А. М.", "доставка обедов в офисы", "Казань", "west", [("rio", 2018), ("largus_van", 2020)]),
 ("ИП Шайдуллина Л. Р.", "кондитерская", "Казань", "west", [("largus_van", 2019)]),
 ("ИП Мухаметшин Р. Р.", "грузоперевозки", "Казань", "west", [("next_van", 2019), ("next_bort", 2017)]),
 ("ИП Валиуллин Т. И.", "монтаж кондиционеров", "Казань", "west", [("largus_van", 2018)]),
 ("ИП Садыков Б. Н.", "такси, три машины", "Казань", "west", [("solaris", 2019), ("polo", 2018), ("rio", 2020)]),
 ("ИП Овчинников К. Е.", "натяжные потолки", "Казань", "west", [("largus", 2019)]),
 ("ООО «Дастархан-Доставка»", "доставка готовой еды", "Казань", "west", [("largus_van", 2019), ("largus_van", 2021), ("next_van", 2020)]),
 ("ООО «Чистая Казанка»", "клининговая компания", "Казань", "west", [("granta", 2019), ("largus", 2020)]),
 ("ООО «КазВентМонтаж»", "монтаж вентиляции", "Казань", "west", [("next_bort", 2018), ("largus_van", 2020)]),
])

for cfg, accs, want in (("en", en_accounts, [35, 25, 9, 8, 11, 10]), ("ru", ru_accounts, [35, 25, 9, 8, 11, 10])):
    assert [a["fleet_count"] for a in accs] == want, [a["fleet_count"] for a in accs]
assert len(en_small) == 30 and len(ru_small) == 30

accounts = {
 "_meta": {
  "seed_version": "v1", "file": "accounts.json", "status": "draft by a wave-1 agent; proposals, not decisions",
  "source": "design story S1 and section 1.6; counts 35, 25, 9, 8, 11, 10",
  "how_formed": {
   "names": "every company name was searched on the web with its home city on 2026-11-13 and no business of that name was found there; the rejected names are in the agent's report. Russian sole traders (ИП) carry a surname and initials only, as the shop's system writes them, so they name nobody; they were not searched.",
   "us_vin": "17 characters: the maker's real world manufacturer identifier (WMI), a five-character descriptor in that model's style (best effort, not taken from a decoding table), the correct check digit in position 9, the real model-year letter in position 10, a plant character, a random serial. A decoder will confirm maker, year and check digit; it may not confirm the model. A coincidence with a real vehicle is unlikely but cannot be excluded.",
   "ru_vin": "17 characters: the WMI of the plant that built the model for the Russian market (X96 ГАЗ, XTA LADA, XTT УАЗ, Z6F Ford Sollers, X7L Renault, Z94 Hyundai and Kia, XW8 Volkswagen and Škoda, VF7 Citroën), a descriptor in the maker's style, the model-year letter where the maker uses one, a random serial. No check digit: these makers do not use the North American one.",
   "us_plates": "Tennessee's plates of the series issued since 2022, the county on a sticker and not in the serial. The cars a story names (fleets, named customers) are drawn from BRC-2190 to BRC-8000, serials that were never issued (Wikipedia, Vehicle registration plates of Tennessee, read 2026-11-13), so none can be on a real car. Background cars: ledger erp.vehicle.plates.",
   "ru_plates": "format А123ВС + region, letters АВЕКМНОРСТУХ only; the region is that of the shop the customer uses: 73 and 173 (Ульяновская область) at main and east, 16, 116 and 716 (Татарстан) at west. Background cars: ledger erp.vehicle.plates. No unissued series was researched, so a plate may coincide with a real registration.",
   "phones_and_email": "phones.md: English tier A (NPA-555-01XX); Russian mobiles in the reserve code 907, city numbers beginning with 1; e-mail under .example"
  },
  "proposed_ledger_rows": [
   "home shop per account: A1 main, A2 east, A3 main, A4 east, A5 west, A6 main (the design fixes only that the two big ones are at the home shops and that A5's comebacks were at west)",
   "payment terms: 30 days for A1, A2, A5, A6; 15 days (en) and 14 days (ru) for A3 and A4",
   "fleet composition by model and year for each account, and typical yearly mileage per vehicle type (en: 13,000 to 28,000 miles; ru: 18,000 to 50,000 km)",
   "A4 grew by two cars: one joined 8 months before T, one 3 months before T",
   "the two A5 vehicles of the brake comebacks are named (en E-2 and E-6; ru Э-1 and Э-10)",
   "contacts' start dates; A6's old contact held the role from 52 to 5 months before T, the new one from 5",
   "30 small business customers per configuration with %d (en) and %d (ru) vehicles, split main / east / west 15 / 6 / 9 (en) and 14 / 7 / 9 (ru)" % (sum(len(x["vehicles"]) for x in en_small), sum(len(x["vehicles"]) for x in ru_small))
  ]
 },
 "en": {"company": "Brennan Auto Care", "accounts": en_accounts, "small_business_customers": en_small},
 "ru": {"company": "«Ермак-Сервис»", "accounts": ru_accounts, "small_business_customers": ru_small},
}

# ---------------- named customers ----------------
def enc(key, yr, novin=False):
    c = us_car(key, yr, novin); c["plate"] = tn_plate(); return c
def ruc(key, yr, regions, novin=False):
    c = ru_car(key, yr, novin); c["plate"] = ru_plate(regions); return c
def pair(cfg, n, a, b, diff, shop_a, shop_b, car):
    npa = "615" if shop_a == "west" else "423"
    return {"pair": n, "record_a": {"name": a, "created_at_shop": shop_a}, "record_b": {"name": b, "created_at_shop": shop_b},
            "difference": diff, "shared_phone": us_phone(npa) if cfg == "en" else ru_mobile(), "car": car}

named = {
 "_meta": {"seed_version": "v1", "file": "named_customers.json", "status": "draft by a wave-1 agent, brought to the ledger and the story cards in the reconcile pass (2026-11-13)",
  "sources": "stories/S06.md, S07.md, S08.md, S15.md; catalogue.json story_pins",
  "notes": ["VINs, plates and phones are formed as accounts.json and phones.md describe.",
            "S15 kind 2 (cars without a VIN, the oldest): the cars here with vin null are among them.",
            "Mileages and the customers' ages are this file's own. The S6 customer, his car and the part it waits for are the same in stories/S06.md, calls/samples and conversations/samples (ledger s6.waiting_at_t).", "The S8 cars are of the catalogue's vehicle class car, for which the ledger's timing-belt amounts hold (s8.price_now, s8.price_quoted)."]},
 "en": {
  "S7": {"name": "Rachel Dunlap", "age": 41, "phone": us_phone("423"), "email": "rdunlap@inbox.example", "shop": "main",
         "car": {**enc("crv", 2014), "mileage_at_first_visit_miles": 121400},
         "why_the_story_is_sound": "A 2014 CR-V at 121,000 miles is due its second set of front pads and its first front rotors, and the grinding she hears is the wear indicator. The CR-V has separate rear shock absorbers; one seeping oil at this age is common, safe to defer for a few weeks and cheap enough to come back for."},
  "S8": {"name": "Frank Daugherty", "age": 63, "phone": us_phone("423"), "email": "fdaugherty@postmail.example", "shop": "main",
         "car": {**enc("outback11", 2011), "engine": "2.5i (EJ253)", "vehicle_class": "car", "mileage_at_visit_miles": 209300},
         "why_the_story_is_sound": "The 2011 Outback 2.5i has the EJ253 engine with a timing belt due every 105,000 miles; this is its second. Belt, tensioner, idlers and water pump is 3.2 billed hours by the catalogue plus a kit, a job a shop can finish the same day when the car is in by eight, which is what the newcomer promised."},
  "S6_waiting_nine_days": {"name": "Curtis Vaughn", "age": 52, "phone": us_phone("615"), "email": "cvaughn@inbox.example", "shop": "west",
         "car": {**enc("xc60", 2012), "mileage_at_visit_miles": 148200},
         "waiting_for": "a remanufactured angle gear (the all-wheel-drive transfer unit), ordered from the shop's old supplier and promised twice",
         "why_the_story_is_sound": "Not a part any Nashville warehouse keeps on the shelf; a supplier that is late on four orders in ten can plausibly miss it twice, and the car cannot be driven without it."},
  "S15_duplicate_pairs": [
   pair("en", 1, "Bill Hargis", "William Hargis", "nickname and formal name", "main", "east", enc("f150", 2012)),
   pair("en", 2, "Teresa Brumlow", "Theresa Brumlow", "one letter", "main", "main", enc("altima", 2016)),
   pair("en", 3, "Linda McAllister", "Linda Mc Allister", "a space inside the surname", "east", "east", enc("camry", 2015)),
   pair("en", 4, "Ana Ramirez-Lopez", "Ana Ramirez", "second surname dropped", "main", "main", enc("odyssey", 2013)),
   pair("en", 5, "James Tolbert Jr.", "James Tolbert", "suffix", "west", "west", enc("silv1500", 2001, novin=True)),
   pair("en", 6, "PARKER, DENISE", "Denise Parker", "the bulk load's capitals and order against a record typed later", "west", "west", enc("rogue", 2017)),
   pair("en", 7, "Mark Stephens", "Mark Stevens", "ph and v", "east", "main", enc("equinox", 2014)),
   pair("en", 8, "Robert L. Goins", "Robert Goins", "middle initial", "main", "main", enc("tundra", 2010)),
   pair("en", 9, "Hung Nguyen", "Nguyen Hung", "name order", "west", "west", enc("camry", 2018)),
   pair("en", 10, "Katherine Yarbrough", "Catherine Yarborough", "two differences at once", "main", "east", enc("outback", 2019)),
   pair("en", 11, "Sean O'Dell", "Sean Odell", "apostrophe", "west", "west", enc("explorer", 2016)),
   pair("en", 12, "Jeffrey Whitlock", "Jeffery Whitlock", "two letters swapped", "main", "main", enc("tacoma", 1999, novin=True)),
  ],
  "S15_car_on_the_wrong_customer": [
   {"case": 1, "shop": "main", "car": enc("accord", 2015), "belongs_to": {"name": "Carol Renfro", "phone": us_phone("423")},
    "order_recorded_under": {"name": "Harold Renfro", "phone": us_phone("423")}, "why": "her father dropped the car off and the order was opened on his record"},
   {"case": 2, "shop": "main", "car": "the 2017 Ford F-250 of Greeson Lawn & Landscape (accounts.json, small business customers)", "belongs_to": {"name": "Greeson Lawn & Landscape"},
    "order_recorded_under": {"name": "Paul Greeson", "phone": us_phone("423")}, "why": "the owner's personal record was picked instead of his company's, so the order is missing from the company's history"},
  ],
 },
 "ru": {
  "S7": {"name": "Ольга Сергеевна Тимофеева", "in_chat": "Ольга", "age": 38, "phone": ru_mobile(), "email": "o.timofeeva@pochta.example", "shop": "main",
         "car": {**ruc("solaris", 2016, ULY), "mileage_at_first_visit_km": 112000},
         "why_the_story_is_sound": "У Solaris 2016 года к 110 тысячам обычно подходит вторая замена передних колодок и первая — дисков; звук, на который она жалуется, даёт индикатор износа. Сзади у машины отдельные амортизаторы, и запотевший или потёкший задний амортизатор на таком пробеге — обычное дело: с ним можно ездить несколько недель, и ради него стоит приехать ещё раз."},
  "S8": {"name": "Игорь Валентинович Фомичёв", "age": 57, "phone": ru_mobile(), "email": "fomichev.iv@yapochta.example", "shop": "main",
         "car": {**ruc("logan", 2015, ULY), "engine": "1.6 16 кл. (K4M)", "vehicle_class": "car", "mileage_at_visit_km": 118000},
         "why_the_story_is_sound": "На Logan с мотором K4M ремень ГРМ меняют каждые 60 тысяч километров, это вторая замена — вместе с роликами и помпой. По каталогу работа занимает 3,2 нормо-часа: если машину принять с утра, её действительно можно отдать в тот же день, что новичок и пообещал."},
  "S6_waiting_nine_days": {"name": "Айрат Гизатуллин", "age": 45, "phone": ru_mobile(), "email": "gizatullin.a@pochta.example", "shop": "west",
         "car": {**ruc("p308", 2011, KZN), "mileage_at_visit_km": 164000},
         "waiting_for": "насос электрогидроусилителя руля, заказан у прежнего поставщика сервиса, срок переносили дважды",
         "why_the_story_is_sound": "Деталь не складская, в Казани её возят под заказ; поставщик, который срывает четыре поставки из десяти, вполне может сорвать её дважды, а ездить без усилителя нельзя."},
  "S15_duplicate_pairs": [
   pair("ru", 1, "Фёдоров Сергей Александрович", "Федоров Сергей Александрович", "ё и е", "main", "east", ruc("granta", 2017, ULY)),
   pair("ru", 2, "Кузнецова Наталья", "Кузнецова Наталия", "Наталья и Наталия", "main", "main", ruc("rio", 2016, ULY)),
   pair("ru", 3, "Мухаметзянов Ильдус", "Мухамметзянов Ильдус", "удвоенная м", "west", "west", ruc("nexia", 2007, KZN, novin=True)),
   pair("ru", 4, "Семёнова Е. В.", "Семенова Елена Викторовна", "инициалы против полного имени, ё и е", "east", "east", ruc("solaris", 2015, ULY)),
   pair("ru", 5, "ПЕТРОВА ЕЛЕНА НИКОЛАЕВНА", "Петрова Елена Николаевна", "прописные буквы из массовой загрузки против записи, набранной позже", "west", "west", ruc("polo", 2014, KZN)),
   pair("ru", 6, "Cмирнов Андрей", "Смирнов Андрей", "первая буква в записи A — латинская C; на глаз записи одинаковы", "main", "main", ruc("vesta", 2018, ULY)),
   pair("ru", 7, "Зарипова Гульнара", "Зарипова Гюльнара", "два написания татарского имени", "west", "west", ruc("xtrail", 2015, KZN)),
   pair("ru", 8, "Саша Морозов", "Морозов Александр Иванович", "уменьшительное имя и другой порядок", "main", "main", ruc("vaz2114", 2008, ULY, novin=True)),
   pair("ru", 9, "Абдулин Геннадий", "Абдуллин Геннадий", "одна и две л", "east", "main", ruc("largus", 2015, ULY)),
   pair("ru", 10, "Шайхутдинов Рамиль", "Шайхутдинов Рамил", "мягкий знак", "west", "west", ruc("rapid", 2016, KZN)),
   pair("ru", 11, "Ершов Данила", "Ершов Даниил", "Данила и Даниил", "main", "east", ruc("focus", 2012, ULY)),
   pair("ru", 12, "Белова Софья", "Белова София", "Софья и София", "main", "main", ruc("outlander", 2014, ULY)),
  ],
  "S15_car_on_the_wrong_customer": [
   {"case": 1, "shop": "east", "car": ruc("rio", 2017, ULY), "belongs_to": {"name": "Агапова Марина Олеговна", "phone": ru_mobile()},
    "order_recorded_under": {"name": "Агапов Дмитрий Сергеевич", "phone": ru_mobile()}, "why": "машину привёз муж, и наряд открыли на его карточку"},
   {"case": 2, "shop": "main", "car": "Largus-фургон ИП Кузьмичёва А. В. (accounts.json, small business customers)", "belongs_to": {"name": "ИП Кузьмичёв А. В."},
    "order_recorded_under": {"name": "Кузьмичёв Алексей Владимирович", "phone": ru_mobile()}, "why": "вместо карточки ИП выбрали личную карточку владельца, и наряд не попал в историю ИП"},
  ],
 },
}
named["ru"]["S15_duplicate_pairs"][5]["record_a"]["name"] = "C" + "мирнов Андрей"  # Latin capital C on purpose

# ---------------- vendors ----------------
def vendor(cfg, vid, role, name, form, city, terms, sells, brands, serves, on_time=None, extra=None, npa="423", rcity="uly", domain=None):
    v = {"id": vid, "role": role, "name": name, "legal_form": form, "city": city, "payment_terms_days": terms, "sells": sells,
         "brands": brands, "serves": serves, "delivered_on_the_promised_day": on_time,
         "phone": us_phone(npa) if cfg == "en" else ru_city(rcity), "email": "orders@%s.example" % domain}
    if extra: v.update(extra)
    return v

vendors = {
 "_meta": {"seed_version": "v1", "file": "vendors.json", "status": "draft by a wave-1 agent, brought to the ledger in the reconcile pass (2026-11-13)",
  "sources": "stories/S06.md and ledger parts.on_time.V1, parts.on_time.V2, s6.brand; design section 1.5 (transmission rebuilds go to a subcontractor)",
  "rules": ["Every supplier is an invented regional distributor; the brands it carries are real brands of that market. No real manufacturer or distributor is a counterparty.",
            "Every name was searched on the web with its city on 2026-11-13; no business of that name was found there."],
  "the_cheap_brake_pads": {"brand": {"en": "Calder ValueStop", "ru": "BREMHOF"}, "invented": True,
   "what": "The cheap pad of story S6 is a brand that does not exist: the house brand of supplier V2, which does not exist either. It is sold only by V2 and fitted only at west (ledger s6.brand; catalogue.json story_pins.S6).",
   "why": "Story S6 says these pads come back four times as often as any other pad. Saying that of a real budget brand in a sales demo would be unfair to it, and nothing in the seed could support it. So no real brand carries the planted comeback rate.",
   "namesake_check": "Done in the reconcile pass on 2026-11-13 by web search of each name in quotes with 'brake pads' / «тормозные колодки»: no brand, product line or seller called Calder ValueStop or BREMHOF came back; the Russian query returned only Brembo pages. A search is not a trademark clearance: before either name is shown outside a demo, the trademark registers of the market are to be read."},
  "ru_only": "V9, the steering-rack subcontractor, exists only in the Russian configuration: the Russian catalogue makes the rack job a sublet repair (cost 9 000, price 12 500); the English catalogue fits a remanufactured rack from a parts supplier.",
  "proposed_ledger_rows": ["payment terms per vendor", "which shops each vendor serves", "delivery rate is set only for the two suppliers of story S6; the others are to be set when the parts part is designed"]},
 "en": [
  vendor("en", "V1", "home parts supplier", "Sequoyah Parts Supply", "Inc.", "Chattanooga, TN", 30, "general-line parts for domestic and import cars and light trucks; three delivery runs a day to both Chattanooga shops",
         ["ACDelco", "Motorcraft", "Denso", "NGK", "Bosch", "Wagner", "Akebono", "Raybestos", "Gates", "Moog", "Monroe", "Wix", "Timken", "Standard Motor Products"], ["main", "east"], "93 %", domain="sequoyahparts"),
  vendor("en", "V2", "the bought shop's old parts supplier", "Harpeth Valley Parts Supply", "LLC", "Nashville, TN", 15, "general-line parts with an economy bias; two delivery runs a day; its own Calder ValueStop economy line of brake pads and rotors",
         ["Dorman", "Centric", "Fram", "Champion", "Autolite", "Prestone"], ["west"], "62 %", {"house_brand": {"name": "Calder ValueStop", "what": "economy brake pads and rotors, the pads of story S6", "invented": True}}, npa="615", domain="harpethvalleyparts"),
  vendor("en", "V3", "parts supplier: Asian and European makes", "Ridge & Valley Import Parts", "Inc.", "Chattanooga, TN", 30, "original-equipment-brand parts for Asian and European cars; next-morning delivery, same day for stocked lines",
         ["Denso", "Aisin", "NGK", "Beck/Arnley", "Bosch", "Mann-Filter", "Mahle", "Lemförder", "Textar", "Zimmermann", "Sachs", "Koyo"], ["main", "east", "west"], domain="ridgevalleyimport"),
  vendor("en", "V4", "parts supplier: batteries, electrical and air conditioning", "Hiwassee Battery & Electric", "Inc.", "Chattanooga, TN", 30, "batteries, starters and alternators, air-conditioning compressors, condensers and refrigerant",
         ["Deka", "Odyssey", "Denso", "Four Seasons", "UAC", "Delphi", "Standard Motor Products"], ["main", "east"], domain="hiwasseebattery"),
  vendor("en", "V5", "tyre supplier", "Tellico Tire Distributors", "LLC", "Chattanooga, TN", 30, "passenger and light-truck tires, wheel weights and valves; daily run in Chattanooga, twice a week to Nashville",
         ["Michelin", "BFGoodrich", "Goodyear", "Cooper", "Hankook", "General", "Falken", "Firestone"], ["main", "east", "west"], domain="tellicotire"),
  vendor("en", "V6", "transmission subcontractor", "Coulter Transmission & Driveline", "LLC", "Chattanooga, TN", 15, "automatic and manual transmission rebuilds, transfer cases and differentials, billed to the shop as sublet work",
         ["Sonnax", "Raybestos Powertrain", "BorgWarner", "Transtec"], ["main", "east"], domain="coultertransmission"),
  vendor("en", "V7", "glass subcontractor", "Walden Auto Glass", "LLC", "Chattanooga, TN", 15, "windshield and door-glass replacement at the shop, camera recalibration",
         ["Pilkington", "PGW", "Fuyao", "Carlite"], ["main", "east"], domain="waldenautoglass"),
  vendor("en", "V8", "towing partner", "Mowbray Towing & Recovery", "LLC", "Soddy-Daisy, TN", 15, "light-duty towing and roadside recovery around Chattanooga, billed per tow on a monthly statement", [], ["main", "east"], domain="mowbraytowing"),
 ],
 "ru": [
  vendor("ru", "V1", "основной поставщик запчастей", "АвтоДеталь-Венец", "ООО", "Ульяновск", 30, "запчасти для иномарок и отечественных автомобилей со склада; три доставки в день на обе ульяновские площадки",
         ["Bosch", "TRW", "Sangsin", "Mann-Filter", "Filtron", "NGK", "Denso", "Gates", "SKF", "Lemförder", "KYB", "Sachs", "LuK", "Mando", "CTR", "Trialli", "Fenox"], ["main", "east"], "93 %", domain="avtodetal-venets"),
  vendor("ru", "V2", "прежний поставщик купленного сервиса", "Казань-АвтоСнаб", "ООО", "Казань", 14, "запчасти эконом-сегмента со склада и под заказ; две доставки в день; собственная марка тормозных колодок и дисков BREMHOF",
         ["Patron", "LYNXauto", "Zekkert", "Stellox", "Miles"], ["west"], "62 %", {"house_brand": {"name": "BREMHOF", "what": "бюджетные тормозные колодки и диски, те самые колодки из истории S6", "invented": True}}, rcity="kzn", domain="kazan-avtosnab"),
  vendor("ru", "V3", "поставщик запчастей: отечественные автомобили", "Симбирск-Комплект", "ООО", "Ульяновск", 14, "запчасти для LADA, ГАЗ и УАЗ, оригинальные и заменители; доставка в день заказа",
         ["LADA (оригинальные запчасти)", "ГАЗ (оригинальные запчасти)", "УАЗ (оригинальные запчасти)", "Трек", "СААЗ", "Пекар", "БелМаг", "Fenox"], ["main", "east", "west"], domain="simbirsk-komplekt"),
  vendor("ru", "V4", "поставщик масел, жидкостей и фильтров", "ОйлТрейд-Симбирск", "ООО", "Ульяновск", 30, "моторные и трансмиссионные масла в бочках и канистрах, антифризы, тормозная жидкость, фильтры",
         ["Лукойл", "Роснефть", "G-Energy", "Sintec", "ZIC", "Liqui Moly", "Felix", "Mann-Filter", "Big Filter"], ["main", "east"], domain="oiltrade-simbirsk"),
  vendor("ru", "V5", "поставщик шин", "ШинТорг-Волга", "ООО", "Ульяновск", 30, "легковые и легкогрузовые шины, диски, грузики и вентили; в сезон доставка каждый день, в Казань два раза в неделю",
         ["Cordiant", "Viatti", "КАМА", "Ikon Tyres", "Белшина", "Triangle", "Sailun", "Kumho", "Hankook"], ["main", "east", "west"], domain="shintorg-volga"),
  vendor("ru", "V6", "субподрядчик по трансмиссиям", "ТрансмиссияПрофи", "ООО", "Ульяновск", 7, "ремонт АКПП, вариаторов и роботизированных коробок, раздаточных коробок и редукторов; оформляется как работа сторонней организации", [], ["main", "east"], domain="transmissiya-profi"),
  vendor("ru", "V7", "субподрядчик по стёклам", "Стекломастер 73", "ООО", "Ульяновск", 7, "замена лобовых и боковых стёкол с выездом в сервис",
         ["Fuyao", "XYG", "KMK Glass", "БОР"], ["main", "east"], domain="steklomaster73"),
  vendor("ru", "V8", "партнёр по эвакуации", "Автоспас 73", "ООО", "Ульяновск", 10, "эвакуация легковых автомобилей и лёгких фургонов по Ульяновску и области; счёт раз в месяц", [], ["main", "east"], domain="avtospas73"),
  vendor("ru", "V9", "субподрядчик по рулевым рейкам", "РулТех-Симбирск", "ООО", "Ульяновск", 7, "ремонт рулевых реек с гидро- и электроусилителем, обменный фонд реек; оформляется как работа сторонней организации (catalogue.json, работа steering_rack)", [], ["main", "east"],
         extra={"namesake_check": "Searched on the web in quotes with «ремонт рулевых реек Ульяновск» on 2026-11-13: no business of this name came back. A search is not a register check: before the name is shown outside a demo, the companies register is to be read."}, domain="rultech-simbirsk"),
 ],
}

def dump(name, obj):
    p = os.path.join(OUT, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(name, os.path.getsize(p))

# Fix pass A (2026-11-14). The other parts suppliers get their own on-time shares (ledger parts.on_time.V3 to V5),
# and the new facts of the story calls and conversations (checks/new_facts.json, the accepted snapshot) are carried:
# invented people into named_customers.json, facts about A1 to A6 into accounts.json. Cars of invented people keep the
# words of the file that named them; the shop-system generator gives them VINs and plates (erp/generator-spec.md section 5).
ON_TIME = {"en": {"V3": 88, "V4": 90, "V5": 84}, "ru": {"V3": 87, "V4": 91, "V5": 80}}
for cfg, shares in ON_TIME.items():
    for v in vendors[cfg]:
        if v["id"] in shares: v["delivered_on_the_promised_day"] = "%d %%" % shares[v["id"]]
NF = json.load(open(os.path.join(OUT, "checks", "new_facts.json"), encoding="utf-8"))
for cfg in ("en", "ru"):
    people = lambda kind: [x["person"] for x in NF["%s.%s" % (kind, cfg)] if x["person"] and x["person"]["name"] not in ("Website visitor", "Посетитель сайта")]
    named[cfg]["story_callers"], named[cfg]["story_chat_customers"] = people("call"), people("conv")
    for a in accounts[cfg]["accounts"]:
        a["from_story_files"] = [{"source": x["file"], "facts": x["facts"]} for kind in ("call", "conv") for x in NF["%s.%s" % (kind, cfg)] if a["id"] in x["accounts"] and x["facts"]]
named["_meta"]["notes"].append("story_callers and story_chat_customers (fix pass A): the people the story calls and story conversations invented, as checks/new_facts.json accepted them; ledger rows nf.call.NN and nf.conv.NN")

# Final review M15: call 25's caller is A2's mechanic, a contact of the account (fixed number, no draw from the generator).
next(a for a in accounts["ru"]["accounts"] if a["id"] == "A2")["contacts"].append(
    {"name": "Рамиль", "role": "механик", "from_months_before_t": 24, "to_months_before_t": None, "phone": "+7 907 471-16-40", "email": None})
dump("accounts.json", accounts); dump("named_customers.json", named); dump("vendors.json", vendors)

# sanity: uniqueness of VINs, plates, phones across the three files
blob = json.dumps([accounts, named, vendors], ensure_ascii=False)
import re
for label, pat in (("vin", r'"vin": "([A-Z0-9]{17})"'), ("plate", r'"plate": "([^"]+)"'), ("us phone", r'"(\(\d{3}\) 555-\d{4})"'), ("ru mobile", r'"(\+7 907 [\d-]+)"')):
    xs = re.findall(pat, blob)
    dup = {x for x in xs if xs.count(x) > 1}
    print(label, len(xs), "dups:", dup if label not in ("us phone", "ru mobile") else len(dup))
print("423 left", len(_a["423"]), "615 left", len(_a["615"]), "TN plates left", len(_tn))
bad = [v for v in re.findall(r'"vin": "([A-Z0-9]{17})"', blob) if v[:3] in ("1FT", "1FM", "3C6", "1GC", "1GB", "5YF", "2HG", "2HK", "4S4", "YV4", "KND", "5NP", "3N1", "3N6", "NM0", "5TD", "5TF", "2T3", "4T1", "1HG", "5FN", "1N4", "5N1", "2GN", "1C6", "ZFB", "W1Y", "WD3")
       and (sum(TR[ch] * w for ch, w in zip(v, W)) % 11) != (10 if v[8] == "X" else int(v[8]))]
print("US VINs failing the check digit:", bad)
