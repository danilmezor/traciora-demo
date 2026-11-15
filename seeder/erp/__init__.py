"""The step `erp`: the shop-system database of v1/erp/schema.sql, built at the runner's instant, loaded into the shop
database (created when absent) and described in seed.manifest."""
import time

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from seeder import clock, manifest


def build(cfg, at, dsn, seed, replace):
    from seeder.erp import accounts, assertions, background, facts, load, mess, orders, parts, reference, stories

    started = time.monotonic()
    a = clock.anchors(cfg, at)
    build = reference.Build(cfg, a, seed)
    reference.fill(build)
    stories.place(build)
    facts.place(build)
    parts.install(build)  # from here no order's work starts before its parts are in
    accounts.place(build)  # counts the account orders the stories placed
    parts.place(build)
    background.fill(build)
    mess.fill(build)  # before the parts step: a typed line has no stock movement, a moved order belongs to its record from the start
    parts.fill(build)
    background.billed(build, exact=True)  # the parts step moved some work on: the mechanics' readings again
    accounts.bill(build)
    stories.close(build)  # reads the final paid times
    orders.finish(build)
    parts.reminders(build)  # reads the mileage `finish` writes
    waiting = assertions.check(build)
    rows, keys = load.finalise(build.tables)
    load.load(dsn, rows, replace)
    manifest.write(dsn, build, keys)
    asked = f" asked={at:%Y-%m-%d %H:%M}" if a["at"] != at else ""  # the clock fell back to an earlier day
    count = sum(map(len, rows.values()))
    print(f"ERP {cfg} T={a['T']:%Y-%m-%d %H:%M}{asked} rows={count} tables={len(rows)} seconds={time.monotonic() - started:.1f}" +
          (f" waiting={','.join(waiting)}" if waiting else ""))
    return count


def database(dsn, create=False):
    """Whether the database `dsn` names exists on its server; created first when `create`."""
    name = conninfo_to_dict(dsn)["dbname"]
    with psycopg.connect(make_conninfo(dsn, dbname="postgres"), autocommit=True) as conn:
        if conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
            return True
        if create:
            conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        return create


def step(cfg, client_id, replace, seed=1):
    dsn = manifest.shop_dsn(client_id)
    database(dsn, create=True)
    return build(cfg, manifest.at(), dsn, seed, replace)


def reset(cfg, client_id):
    dsn = manifest.shop_dsn(client_id)
    if database(dsn):
        with psycopg.connect(dsn) as conn:
            conn.execute("DROP SCHEMA IF EXISTS shop CASCADE")
            conn.execute("DROP SCHEMA IF EXISTS seed CASCADE")
