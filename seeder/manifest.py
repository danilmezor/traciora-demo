"""`seed.manifest`: what a build of the shop database holds, one jsonb value a key, in schema `seed` beside schema `shop`
(outside a source that reads `shop.*`). The erp step writes it after the load from the finished build; every later step
reads it (`read`) instead of the generator's objects. Also where a step finds the shop database, the build instant and
the runtime folder."""
import collections
import datetime as dt
import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.types.json import Jsonb

from seeder import checks, inputs

FORMAT = "%Y-%m-%d %H:%M"
BUILD = ("seed", "cfg", "T", "asked", "zone", "random_seed", "seeder_commit", "product_commit")


def shop_dsn(client_id):
    """The shop database: `SEED_SHOP_DSN`, else the product's admin DSN with the database `seed_shop_<client id>`."""
    if os.environ.get("SEED_SHOP_DSN"):
        return os.environ["SEED_SHOP_DSN"]
    from traciora.core.core_db.engine import admin_dsn  # only here: a build with the variable set needs no product

    return make_conninfo(admin_dsn(), dbname=f"seed_shop_{client_id}")


def runtime_root():
    """The product's runtime folder: `RUNTIME_ROOT`, else `./runtime` when the working directory holds one, else None."""
    if os.environ.get("RUNTIME_ROOT"):
        return Path(os.environ["RUNTIME_ROOT"])
    return Path("runtime") if Path("runtime").is_dir() else None


def at():
    """The build instant on the home clock, `SEED_AT` as the runner sets it for every step."""
    return dt.datetime.strptime(os.environ["SEED_AT"], FORMAT)


def read(dsn):
    """Every key of the database's seed.manifest, {} when it has none or the database itself does not exist (a first
    build's reset runs before the erp step creates it). A server that does not answer is an error."""
    try:
        conn = psycopg.connect(dsn)
    except psycopg.OperationalError as e:
        if "does not exist" in str(e):
            return {}
        raise
    with conn:
        if conn.execute("SELECT to_regclass('seed.manifest')").fetchone()[0] is None:
            return {}
        return dict(conn.execute("SELECT key, value FROM seed.manifest ORDER BY key").fetchall())


def plain(value):
    if isinstance(value, dt.datetime):
        return f"{value:{FORMAT}}"
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"no JSON form for {value!r}")


def commit():
    """The seed checkout's commit: `SEED_COMMIT`, else git's when this is a git checkout, else None."""
    if os.environ.get("SEED_COMMIT"):
        return os.environ["SEED_COMMIT"]
    root = inputs.SEED.parent
    if not (root / ".git").exists():
        return None
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or None
    except OSError:  # no git on the box
        return None


def write(dsn, b, keys):
    """seed.manifest of the loaded build `b`, its rows keyed as `keys` (table: {id(row): key}) by load.finalise. Stories
    are the build's named records (`b.named`, and `b.pending` records that were written): customer, phone, home shop,
    the named cars' plates, every order number and appointment of the customer in key order. Bands are the band
    statements of erp/checks.sql run on this database."""
    a, cfg = b.a, b.cfg
    site = {id(row): name for name, row in b.shops.items()}
    orders, appointments = collections.defaultdict(list), collections.defaultdict(list)
    for row in b.tables["repair_order"]:
        orders[id(row["customer_id"])].append(row)
    for row in b.tables["appointment"]:
        if row.get("customer_id") is not None:
            appointments[id(row["customer_id"])].append(row)
    stories = {}
    for name, (customer, cars) in sorted((b.pending | b.named).items()):
        if id(customer) not in keys["customer"]:
            continue
        stories[name] = {
            "customer_id": keys["customer"][id(customer)], "phone": customer.get("phone"), "shop": site[id(customer["created_location_id"])],
            "plates": [car.get("plate") for car in cars],
            "orders": [o["number"] for o in sorted(orders[id(customer)], key=lambda o: keys["repair_order"][id(o)])],
            "appointments": [{"starts_at": x["starts_at"], "shop": site[id(x["location_id"])]}
                             for x in sorted(appointments[id(customer)], key=lambda x: keys["appointment"][id(x)])],
        }
    measured = checks.run(cfg, a, checks.ERP, checks.direct(dsn, checks.variables(cfg, a)), kinds=("band",))[2]
    described = checks.describe(checks.ERP)
    values = {
        "seed": inputs.SEED.name, "cfg": cfg, "T": a["T"], "asked": a["asked"], "zone": inputs.value("geo.home_zone", cfg), "random_seed": b.seed,
        "seeder_commit": commit(), "product_commit": os.environ.get("TRACIORA_PRODUCT_COMMIT") or None,
        "anchors": {k: v for k, v in a.items() if k not in ("week_day", "works", "calls", "conversations")},
        "calls": {str(n): v for n, v in a["calls"].items()}, "conversations": {str(n): v for n, v in a["conversations"].items()},
        "stories": stories,
        "people": {slot: keys["employee"][id(row)] for slot, row in b.people.items()} | {"F4": [keys["employee"][id(row)] for row in b.seasons]},
        "shops": {name: keys["location"][id(row)] for name, row in b.shops.items()},
        "bands": {k: v | described[k] for k, v in measured.items()},
    }
    dumps = lambda v: json.dumps(v, default=plain, ensure_ascii=False)  # noqa: E731
    with psycopg.connect(dsn) as conn:
        conn.execute("DROP SCHEMA IF EXISTS seed CASCADE")
        conn.execute("CREATE SCHEMA seed")
        conn.execute("CREATE TABLE seed.manifest (key text PRIMARY KEY, value jsonb NOT NULL)")
        conn.cursor().executemany("INSERT INTO seed.manifest VALUES (%s, %s)", [(k, Jsonb(v, dumps)) for k, v in values.items()])
