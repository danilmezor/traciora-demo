"""Check the demo tenant's configuration files (seed v1) against the product and the seed.

Run from anywhere with the product repository's interpreter:
    ../traciora/.venv/bin/python v1/tenant/validate.py
The product repository is ../traciora beside this checkout; TRACIORA_PRODUCT overrides it. Reads only; writes nothing but stdout.
Exit 0 when every check closes, 1 otherwise.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True  # import the product's modules without writing caches into its repository
HERE = Path(__file__).resolve().parent
SEED = HERE.parent
REPO = Path(os.environ.get("TRACIORA_PRODUCT") or SEED.parent.parent / "traciora")
CFGS = ("en", "ru")

results: list[tuple[bool, str]] = []


def check(ok: bool, what: str) -> bool:
    results.append((bool(ok), what))
    return bool(ok)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


ledger = {row["key"]: row for row in load(SEED / "ledger.json")["rows"]}
cast = load(SEED / "cast.json")
schema = load(REPO / "config/settings.schema.json")["settings"]


def lv(key: str, cfg: str):
    """The ledger's value of a row for a configuration."""
    row = ledger[key]
    if "value" in row:
        return row["value"]
    return row["en"] if cfg == "en" or row.get("ru") == "same" else row["ru"]


# ------------------------------------------------------------------ A. settings
def type_ok(spec: dict, value) -> tuple[bool, str]:
    kind = spec.get("type")
    if kind == "bool":
        return isinstance(value, bool), "bool"
    if kind == "int":
        if not isinstance(value, int) or isinstance(value, bool):
            return False, "int"
        if "min" in spec and value < spec["min"] or "max" in spec and value > spec["max"]:
            return False, f"int in [{spec.get('min')}, {spec.get('max')}]"
        return True, "int"
    if kind == "float":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False, "float"
        if "min" in spec and value < spec["min"] or "max" in spec and value > spec["max"]:
            return False, "float in range"
        return True, "float"
    if kind == "enum":
        return value in spec.get("options", []), f"one of {spec.get('options')}"
    if kind == "enum_list":
        return isinstance(value, list) and all(v in spec.get("options", []) for v in value), "subset of options"
    if kind == "timezone":
        try:
            ZoneInfo(value)
            return True, "timezone"
        except Exception:  # noqa: BLE001
            return False, "IANA timezone"
    if kind in ("string", "url"):
        if not isinstance(value, str):
            return False, kind
        if "pattern" in spec and not re.match(spec["pattern"], value):
            return False, f"string matching {spec['pattern']}"
        return True, kind
    return False, f"unsupported type {kind}"


settings = {}
for cfg in CFGS:
    s = load(HERE / f"settings.{cfg}.json")
    settings[cfg] = {k: v for k, v in s.items() if not k.startswith("_")}
    for key, value in settings[cfg].items():
        spec = schema.get(key)
        if not check(spec is not None, f"settings.{cfg}: {key} is declared in config/settings.schema.json"):
            continue
        ok, want = type_ok(spec, value)
        check(ok, f"settings.{cfg}: {key} = {value!r} is a valid {want}")

CHANNEL_KEY = {"web chat": "CHAT", "Telegram": "TELEGRAM", "VK": "VK", "Avito": "AVITO"}
for cfg in CFGS:
    s = settings[cfg]
    check(s["BUSINESS_TIMEZONE"] == lv("geo.home_zone", cfg), f"settings.{cfg}: BUSINESS_TIMEZONE = ledger geo.home_zone")
    check(s["PRODUCTION_LANGUAGE"] == cfg, f"settings.{cfg}: PRODUCTION_LANGUAGE is {cfg}")
    check(s["CURRENCY"] == {"en": "USD", "ru": "RUB"}[cfg], f"settings.{cfg}: CURRENCY")
    check(s["REGION"] == lv("geo.home_city", cfg) == s["LOCATION_CITY"], f"settings.{cfg}: REGION and LOCATION_CITY = ledger geo.home_city")
    address = lv("geo.address.main", cfg)
    check(f"{s['LOCATION_ADDRESS']} ({s['LOCATION_LATITUDE']}, {s['LOCATION_LONGITUDE']})" == address,
          f"settings.{cfg}: LOCATION_ADDRESS and coordinates = ledger geo.address.main")
    modes = lv("conv.assistant_mode", cfg)
    channels = lv("conv.channels", cfg)
    check(set(modes) == set(channels), f"ledger: conv.assistant_mode and conv.channels name the same channels ({cfg})")
    for channel, key in CHANNEL_KEY.items():
        on = s.get(f"CHATWOOT_{key}_BRIDGE_ENABLED", schema[f"CHATWOOT_{key}_BRIDGE_ENABLED"]["default"])
        check(on == (channel in channels), f"settings.{cfg}: CHATWOOT_{key}_BRIDGE_ENABLED = {on} as ledger conv.channels")
        if channel in modes:
            mode = s.get(f"CHATWOOT_{key}_ASSISTANT", schema[f"CHATWOOT_{key}_ASSISTANT"]["default"])
            want = {"sends": "sends", "drafts": "drafts"}[modes[channel]]
            check(mode == want, f"settings.{cfg}: CHATWOOT_{key}_ASSISTANT = {mode} as ledger conv.assistant_mode")
    check(s["TRACIORA_STT_MODELS"] == lv("calls.recognition.engines", cfg), f"settings.{cfg}: TRACIORA_STT_MODELS = ledger calls.recognition.engines")
    kb = lv("kb.settings", cfg)
    check(s["TRACIORA_KNOWLEDGE_ROOT_SEEN_FROM"] == kb["TRACIORA_KNOWLEDGE_ROOT_SEEN_FROM"], f"settings.{cfg}: knowledge root = ledger kb.settings")
    check(s["TRACIORA_KNOWLEDGE_PROPOSE_FROM"] == kb["propose_from"], f"settings.{cfg}: propose rung = ledger kb.settings")
    check(s["TRACIORA_KNOWLEDGE_PUBLISH_FROM"] == kb["publish_and_decide_from"], f"settings.{cfg}: publish rung = ledger kb.settings")
    check(s["CONVERSATIONS_OWNERSHIP"] == lv("conv.ownership", cfg).replace(" ", "_"), f"settings.{cfg}: CONVERSATIONS_OWNERSHIP = ledger conv.ownership")
    check(s["CONVERSATIONS_AUTO_RESOLVE_DAYS"] == lv("conv.auto_resolve_days", cfg), f"settings.{cfg}: CONVERSATIONS_AUTO_RESOLVE_DAYS = ledger conv.auto_resolve_days")
    slot2 = next(p for p in cast["people"] if p["slot"] == "2")
    check(s["ADMIN_USERNAMES"] == slot2[cfg]["username"], f"settings.{cfg}: ADMIN_USERNAMES is slot 2's username")
    check(s["TRACIORA_GOOGLE_CALENDAR_ENABLED"] is False and s["TRACIORA_FEATURE_GOOGLE_CALENDAR"] is False, f"settings.{cfg}: Google Calendar off")
    check(s["TELEGRAM_MANAGER_BOT_ENABLED"] is False, f"settings.{cfg}: staff Telegram bot off")
    check(s["TRACIORA_PHONECALLS_PERFORMANCE_RANK"] == "senior", f"settings.{cfg}: performance rank senior (S4.2, S4.6)")

for cfg in CFGS:
    check(int(settings[cfg]["TRACIORA_MEMORY_RETEST_DAYS"]) == lv("mem.retest_days", cfg),
          f"settings.{cfg}: TRACIORA_MEMORY_RETEST_DAYS = ledger mem.retest_days")
    check(settings[cfg]["TRACIORA_CONTEXT_SYNC_AT"] == lv("console.context_sync_at", cfg),
          f"settings.{cfg}: TRACIORA_CONTEXT_SYNC_AT = ledger console.context_sync_at")

phones = (SEED / "phones.md").read_text(encoding="utf-8")
lines = re.findall(r"^\| `(main|east|west)` \| ([^|]+?) \| group (\d+), then ([\d, ]+)", phones, re.M)
public = {"en": {k: (num.strip(), grp, [x.strip() for x in rings.split(",")]) for k, num, grp, rings in lines[:3]},
          "ru": {k: (num.strip(), grp, [x.strip() for x in rings.split(",")]) for k, num, grp, rings in lines[3:6]}}
for cfg in CFGS:
    check(settings[cfg]["CONTACT_PHONE"] == public[cfg]["main"][0], f"settings.{cfg}: CONTACT_PHONE = phones.md main public line")

# ------------------------------------------------------------------ B. ladder
ladder = load(HERE / "ladder.json")
product_levels = load(REPO / "config/defaults/access_levels.json")
product_limits = load(REPO / "config/defaults/access_limits.json")
check(ladder["access_levels"]["levels"] == product_levels["levels"], "ladder: access_levels equal the shipped file")
check(ladder["access_limits"]["limits"] == product_limits["limits"], "ladder: access_limits equal the shipped file")
check(ladder["tools_json"] == {"families": {}, "tools": {}}, "ladder: tools.json empty (no tool moved)")
scopes = {lvl["scope"] for lvl in product_levels["levels"]}
check(set(ladder["ranks"]) <= scopes, "ladder: every rank is a scope of the shipped ladder")
junior_days = product_limits["limits"]["junior"]["history_days"]
check(lv("time.go_live_days", "en") <= junior_days, f"ladder: go-live ({lv('time.go_live_days', 'en')} d) inside the junior's window ({junior_days} d)")

sys.path.insert(0, str(REPO / "apps/backend/src"))
live = None
try:
    import traciora.core.common.client_runtime_config as crc

    crc.memory_running = lambda: True
    crc.sources_configured = lambda: True
    type(crc.get_client_runtime_config()).feature_active = lambda self, *a, **k: True
    from traciora.core.tools import tool_policy as tp
    from traciora.core.tools.tool_catalog import access_floor

    live = {name: access_floor(info.allowed_users) for name, info in tp.build(tp.EVERYTHING)._tools.items()}
except Exception as exc:  # noqa: BLE001
    check(False, f"ladder: the product's tool catalogue could be built ({type(exc).__name__}: {exc})")
backend = REPO / "apps/backend/src/traciora/core/tools"
source_text = "\n".join(p.read_text(encoding="utf-8") for p in backend.rglob("*.py"))
ORDER = ["customer", "worker", "junior", "middle", "senior"]
named = set()
for rank, entry in ladder["ranks"].items():
    for family, names in entry["tools"].items():
        for name in names:
            named.add(name)
            if live is not None and name in live:
                floor = live[name]
                rr = "senior" if rank == "admin" else rank
                check(ORDER.index(floor) <= ORDER.index(rr), f"ladder: {rank} may call {name} (shipped floor {floor})")
            else:
                check(f'"{name}"' in source_text, f"ladder: {name} is a registered tool name in the product")
if live is not None:
    for name, floor in live.items():
        if floor == "customer" or name in ladder["not_registered"]:
            continue
        for rank in ("worker", "junior", "middle", "senior"):
            holds = any(name in v for v in ladder["ranks"][rank]["tools"].values())
            if ORDER.index(floor) <= ORDER.index(rank) and not holds:
                check(False, f"ladder: {rank} holds {name} by the shipped floor but ladder.json omits it")

slots = {s["slot"]: s for s in ladder["slots"]}
cast_slots = {p["slot"]: p for p in cast["people"]}
check(set(slots) == set(cast_slots) and len(slots) == len(ladder["slots"]), "ladder: every cast slot appears exactly once")
for slot, person in cast_slots.items():
    mine = slots.get(slot, {})
    rank = mine.get("rank")
    check(rank in ("worker", "junior", "middle", "senior", "admin", "none"), f"ladder: slot {slot} has exactly one rank ({rank})")
    want = person["rank"] or "none"
    check(rank == want, f"ladder: slot {slot} rank {rank} = cast.json {want}")
    check(mine.get("role_key") == person["role_key"] and person["role_key"] in cast["roles"], f"ladder: slot {slot} role is a cast.json role")
    home = person["site"]
    if home != "none":
        check(mine.get("home") == home, f"ladder: slot {slot} home posting = cast.json site {home}")
        for extra in person.get("also_sites", []):
            check(extra in mine.get("postings", []), f"ladder: slot {slot} posted at {extra} (cast.json also_sites)")

# ------------------------------------------------------------------ C. sources
try:
    import jsonschema
except ImportError:
    jsonschema = None
check(jsonschema is not None, "sources: jsonschema is available in this interpreter")
src_schema = load(REPO / "config/schemas/sources.schema.json")
core_sql = (REPO / "apps/backend/schema/traciora-core.sql").read_text(encoding="utf-8")
core_relations = set(re.findall(r"CREATE (?:TABLE|VIEW)(?: IF NOT EXISTS)? (\w+\.\w+)", core_sql))
erp_tables = set(re.findall(r"^## ([a-z_]+)$", (SEED / "erp/dictionary.md").read_text(encoding="utf-8"), re.M))
check(len(erp_tables) == 31, f"erp/dictionary.md describes 31 ERP tables ({len(erp_tables)})")
erp_columns = {}
for m in re.finditer(r"CREATE TABLE shop\.(\w+) \((.*?)\n\);", (SEED / "erp/schema.sql").read_text(encoding="utf-8"), re.S):
    erp_columns[m.group(1)] = {ln.split()[0] for ln in m.group(2).split("\n") if ln.strip() and ln.split()[0].islower()}
check(set(erp_columns) == erp_tables, "erp/schema.sql has the 31 tables of erp/dictionary.md")
reader_sql = (REPO / "docker/chatwoot/traciora_reader.sql").read_text(encoding="utf-8")

parse_sources = None
try:
    from traciora.data.sources.config import parse_sources
except Exception as exc:  # noqa: BLE001
    check(False, f"sources: the product's parse_sources imports ({type(exc).__name__})")

# (source, rank, schema, table, column or None, view?, expected): what each rank must and must not read.
EXPECT = [
    ("erp", "worker", "shop", "repair_order", None, False, False),
    ("erp", "junior", "shop", "repair_order", None, False, True),
    ("erp", "junior", "shop", "customer", "phone", False, True),
    ("erp", "junior", "shop", "customer", "email", False, True),
    ("erp", "junior", "shop", "customer", "address", False, True),
    ("erp", "junior", "shop", "customer_contact", "email", False, True),
    ("erp", "junior", "shop", "appointment", "contact_phone", False, True),
    ("erp", "junior", "shop", "cash_drawer_close", "counted_cash", False, False),
    ("erp", "junior", "shop", "cash_drawer_close", "note", False, False),
    ("erp", "junior", "shop", "cash_drawer_close", "business_date", False, True),
    ("erp", "middle", "shop", "cash_drawer_close", "counted_cash", False, True),
    ("erp", "middle", "shop", "employee", "pay_type", False, True),
    ("erp", "junior", "shop", "employee", "pay_type", False, False),
    ("erp", "admin", "seed_manifest", "manifest", None, False, False),
    ("core", "worker", "interactions", "phone_call_missed", None, True, False),
    ("core", "junior", "interactions", "phone_call_missed", None, True, True),
    ("core", "junior", "interactions", "phone_call_analysis", None, True, True),
    ("core", "junior", "interactions", "phone_call_day_report", None, True, False),
    ("core", "senior", "interactions", "phone_call_day_report", None, True, True),
    ("core", "junior", "core", "location_hours_exception", None, False, True),
    ("core", "junior", "workforce", "punch", None, False, False),
    ("core", "middle", "workforce", "punch", "at", False, True),
    ("core", "middle", "workforce", "punch", "note_enc", False, False),
    ("core", "senior", "workforce", "punch", "note_enc", False, True),
    ("core", "admin", "workforce", "punch", "coordinates_enc", False, False),
    ("core", "middle", "workforce", "shift_change_request", None, False, False),
    ("core", "senior", "workforce", "shift_change_request", "reason_enc", False, True),
    ("core", "senior", "platform", "event", None, False, True),
    ("core", "senior", "work", "calendar_event", None, False, False),
    ("core", "admin", "work", "calendar_event", None, False, True),
    ("core", "admin", "platform", "memory", None, False, False),
    ("core", "admin", "platform", "proposal", None, False, False),
    ("core", "admin", "platform", "alert", None, False, True),
    ("chatwoot", "worker", "public", "messages", None, False, False),
    ("chatwoot", "junior", "public", "messages", None, False, True),
    ("chatwoot", "junior", "traciora", "reply_episodes", None, True, True),
]
for cfg in CFGS:
    doc = load(HERE / f"sources.{cfg}.json")
    if jsonschema is not None:
        try:
            jsonschema.validate(doc, src_schema)
            check(True, f"sources.{cfg}: valid against config/schemas/sources.schema.json")
        except jsonschema.ValidationError as exc:
            check(False, f"sources.{cfg}: schema: {exc.message}")
    by_name = {s["name"]: s for s in doc["sources"]}
    check(set(by_name) == {"erp", "core", "chatwoot"}, f"sources.{cfg}: declares erp, core and chatwoot")
    for rank, grant in by_name["erp"]["access"].items():
        for t in grant.get("tables", []):
            check(t["schema"] == "shop" and t["table"] in erp_tables, f"sources.{cfg}: erp {rank} names {t['schema']}.{t['table']}, a table of erp/dictionary.md")
            for col in t.get("denied_columns", []):
                check(col in erp_columns.get(t["table"], set()), f"sources.{cfg}: erp {rank} hides {t['table']}.{col}, a column of erp/schema.sql")
    for rank, grant in by_name["core"]["access"].items():
        for t in grant.get("tables", []):
            check(f"{t['schema']}.{t['table']}" in core_relations, f"sources.{cfg}: core {rank} names {t['schema']}.{t['table']}, a core table")
        for v in grant.get("views", []):
            check(v in core_relations, f"sources.{cfg}: core {rank} names view {v}, a core view")
        for sch in grant.get("schemas", []):
            check(any(r.startswith(sch + ".") for r in core_relations), f"sources.{cfg}: core {rank} schema {sch} exists")
    for rank, grant in by_name["chatwoot"]["access"].items():
        for t in grant.get("tables", []):
            check(re.search(rf"\b{t['table']}\b", reader_sql) is not None, f"sources.{cfg}: chatwoot {rank} names {t['table']}, which the reader login may select")
        for v in grant.get("views", []):
            check(f"VIEW {v}" in reader_sql, f"sources.{cfg}: chatwoot view {v} exists in traciora_reader.sql")
    if parse_sources is not None:
        try:
            parsed = {s.name: s for s in parse_sources(doc, lambda key: "postgresql://reader:x@localhost/db")}
            check(True, f"sources.{cfg}: the product's parse_sources accepts it")
        except ValueError as exc:
            check(False, f"sources.{cfg}: parse_sources: {exc}")
            continue
        for name, rank, sch, table, column, view, want in EXPECT:
            access = parsed[name].access[rank]
            reads = access.allows_table(sch, table, view=view)
            if column is not None:
                reads = reads and not access.hides(sch, table, column, view=view)
            what = f"{sch}.{table}" + (f".{column}" if column else "")
            check(reads == want, f"sources.{cfg}: {name} {rank} {'reads' if want else 'does not read'} {what}")

# ------------------------------------------------------------------ E. roles and places
NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def us_holidays(year: int) -> dict[str, dt.date]:
    def nth(month, weekday, n):
        d = dt.date(year, month, 1)
        d += dt.timedelta(days=(weekday - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)

    def last(month, weekday):
        d = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
        return d - dt.timedelta(days=(d.weekday() - weekday) % 7)

    def observed(d):
        return d - dt.timedelta(days=1) if d.weekday() == 5 else d + dt.timedelta(days=1) if d.weekday() == 6 else d

    return {"New Year's Day": observed(dt.date(year, 1, 1)), "Memorial Day": last(5, 0),
            "Independence Day": observed(dt.date(year, 7, 4)), "Labor Day": nth(9, 0, 1),
            "Thanksgiving Day": nth(11, 3, 4), "Christmas Day": observed(dt.date(year, 12, 25))}


def closed_dates(cfg: str, years) -> set[dt.date]:
    out = set()
    for y in years:
        if cfg == "en":
            out |= set(us_holidays(y).values())
        else:
            out |= {dt.date(y, 1, 1), dt.date(y, 1, 2)}
    return out


T = dt.date(2026, 11, 13)
cast_ext = {p["slot"]: p.get("extension") for p in cast["people"]}
desk_rows = {k.split(".")[0][1:].lstrip("0") or "0": v["value"] for k, v in ledger.items() if re.fullmatch(r"p(\d\d|F\d)\.desk", k)}
for cfg in CFGS:
    rp = load(HERE / f"roles-and-places.{cfg}.json")
    check(rp["configuration"] == cfg, f"roles-and-places.{cfg}: configuration")
    check({r["key"]: r["name"] for r in rp["roles"]} == {k: v[cfg] for k, v in cast["roles"].items()},
          f"roles-and-places.{cfg}: role keys and names = cast.json roles (verbatim)")
    short = lv("geo.short_name", cfg)
    places = {p["key"]: p for p in rp["places"]}
    check(set(places) == {"main", "east", "west"}, f"roles-and-places.{cfg}: three shops")
    hours = lv("site.hours.weekday", cfg)
    open_days = lv("site.open_days", cfg)
    all_ext = set()
    for key, p in places.items():
        check(p["name"] == short[key], f"roles-and-places.{cfg}: {key} name = ledger geo.short_name")
        check(f"{p['address']} ({p['latitude']}, {p['longitude']})" == lv(f"geo.address.{key}", cfg),
              f"roles-and-places.{cfg}: {key} address and coordinates = ledger geo.address.{key}")
        zone = lv("geo.other_zone" if key == "west" else "geo.home_zone", cfg)
        check(p["tz"] == zone, f"roles-and-places.{cfg}: {key} tz = ledger {zone}")
        check(p["checkin_radius_m"] == lv("geo.checkin_radius_m", cfg), f"roles-and-places.{cfg}: {key} check-in radius = ledger geo.checkin_radius_m")
        check(p["staffed"] is True, f"roles-and-places.{cfg}: {key} staffed")
        want = {}
        rule = open_days[key]
        for i, day in enumerate(NAMES):
            if rule == "every day" or (rule.startswith("Mon to Fri") and i < 5):
                want[day] = [hours]
            elif day == "sat" and "Saturday" in rule:
                m = re.search(r"Saturday (\d\d:\d\d) to (\d\d:\d\d)", rule)
                want[day] = [[m.group(1), m.group(2)]]
            else:
                want[day] = []
        check(p["business_hours"] == want, f"roles-and-places.{cfg}: {key} business_hours = ledger site.hours.weekday and site.open_days")
        num, grp, rings = public[cfg][key]
        check(p["public_line"] == num, f"roles-and-places.{cfg}: {key} public line = phones.md")
        group = [e for e in p["extensions"] if e["kind"] == "group line"]
        check(len(group) == 1 and group[0]["ext"] == grp and group[0]["rings"] == rings,
              f"roles-and-places.{cfg}: {key} group line {grp} rings {rings} as phones.md")
        for e in p["extensions"]:
            all_ext.add(e["ext"])
            if "slot" in e:
                check(cast_ext.get(e["slot"]) == e["ext"], f"roles-and-places.{cfg}: extension {e['ext']} is slot {e['slot']}'s in cast.json")
                if e["slot"] in desk_rows:
                    check(str(desk_rows[e["slot"]]) == e["ext"], f"roles-and-places.{cfg}: extension {e['ext']} = ledger p{e['slot']}.desk")
    for e in rp["head_office"]["extensions"]:
        all_ext.add(e["ext"])
        check(cast_ext.get(e["slot"]) == e["ext"], f"roles-and-places.{cfg}: head-office extension {e['ext']} is slot {e['slot']}'s")
    for slot, ext in cast_ext.items():
        if ext and slot != "F3":
            check(ext in all_ext, f"roles-and-places.{cfg}: cast extension {ext} (slot {slot}) is declared")
    for slot, ext in desk_rows.items():
        check(str(ext) in all_ext, f"roles-and-places.{cfg}: ledger desk {ext} is declared")
    cd = rp["closed_dates"]
    check(cd["rule"] == lv("site.closed_dates", cfg), f"roles-and-places.{cfg}: closed dates = ledger site.closed_dates")
    closed = closed_dates(cfg, range(2025, 2028))

    def full_open(d):
        return d not in closed and (cfg == "ru" or d.weekday() < 5)

    g = T - dt.timedelta(days=lv("time.go_live_days", cfg))
    while not full_open(g):
        g += dt.timedelta(days=1)
    since = sorted(d.isoformat() for d in closed if g <= d < T)
    ahead = sorted(d.isoformat() for d in closed if T <= d <= T + dt.timedelta(days=60))
    ex = cd["example_for_T_2026_11_13"]
    check(ex["since_G"] == since, f"roles-and-places.{cfg}: closed dates since G for the reference T = {since}")
    check(ex["next_60_days"] == ahead, f"roles-and-places.{cfg}: closed dates in the next 60 days for the reference T = {ahead}")
    st = rp["changed_hours"][0]
    stock = lv("site.stocktake", cfg)
    check(st["anchor"] == stock["day"], f"roles-and-places.{cfg}: stocktake anchor = ledger site.stocktake")
    check(st["row"]["close_local"] == stock["closes_at"].split()[0] and st["row"]["open_local"] == hours[0],
          f"roles-and-places.{cfg}: stocktake hours open..{stock['closes_at']}")
    monday = T - dt.timedelta(days=T.weekday())
    day = monday + dt.timedelta(weeks=1, days=3)
    if day in closed:
        day = monday + dt.timedelta(weeks=1, days=1)
    check(st["example_for_T_2026_11_13"] == day.isoformat(), f"roles-and-places.{cfg}: stocktake date for the reference T = {day}")

# ------------------------------------------------------------------ D. context notes
ctx = HERE / "context"
readme = (ctx / "README.md").read_text(encoding="utf-8")
MARKER = "---\ntype: manual\n"
for folder, shipped_root in (("core", "config/sources/traciora"), ("conversations", "config/sources/chatwoot")):
    rows = re.findall(r"^\| `([^`]+)` \| (extends|new) \|", readme.split(f"## `{folder}/`", 1)[1].split("\n## ", 1)[0], re.M)
    listed = {path for path, _ in rows}
    on_disk = {str(p.relative_to(ctx / folder)) for p in (ctx / folder).rglob("*.md")}
    check(listed == on_disk, f"context/{folder}: README lists exactly the files on disk")
    for path, kind in rows:
        text = (ctx / folder / path).read_text(encoding="utf-8")
        if kind == "new":
            check(text.startswith(MARKER) and not (REPO / shipped_root / path).exists(),
                  f"context/{folder}/{path}: new note with the manual marker, no shipped file of that path")
        else:
            check((REPO / shipped_root / path).exists(), f"context/{folder}/{path}: extends shipped {shipped_root}/{path}")


def names_in(node, out: set):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("name", "full_name", "company", "legal_name", "display_name") and isinstance(v, str) and len(v) > 5 and " " in v:
                out.add(v)
            names_in(v, out)
    elif isinstance(node, list):
        for v in node:
            names_in(v, out)


story_names: set[str] = set()
for f in ("cast.json", "accounts.json", "named_customers.json", "vendors.json"):
    names_in(load(SEED / f), story_names)
notes_text = "\n".join(p.read_text(encoding="utf-8") for p in ctx.rglob("*.md"))
leaked = sorted(n for n in story_names if n in notes_text)
check(not leaked, f"context: no person, customer, account or vendor of the stories is named in a note {leaked[:5]}")

# ------------------------------------------------------------------ report
failed = [w for ok, w in results if not ok]
for ok, what in results:
    if not ok:
        print("FAIL", what)
print(f"{len(results)} checks, {len(results) - len(failed)} pass, {len(failed)} fail")
print("VALIDATE " + ("PASS" if not failed else "FAIL"))
sys.exit(0 if not failed else 1)
