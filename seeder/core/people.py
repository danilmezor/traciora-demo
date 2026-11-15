"""The step `people`: the core database's shops (hours, dated hours, extensions), positions, staff and sign-ins, written
through the product's commands from cast.json, tenant/ladder.json and tenant/roles-and-places.<cfg>.json. Each person is
the shop database's employee the manifest names for its slot and is refused when the two disagree. A person's id is
`ids.uuid("person", slot, cfg)` and carries the employee in `attrs_public.employee_id`; a shop is the location whose
`config_key` alias is its key (`main`, `east`, `west`), the manifest's key to its `location_id`. Every account signs in
with the password in TRACIORA_DEMO_MANAGER_PASSWORD; a former person is ended with their login and account
(`commands.accounts.set_active`). A rerun updates in place; `--replace` and `reset` refuse while another store's rows
point at what they would delete."""
import contextlib
import datetime as dt
import os
import sqlite3
from zoneinfo import ZoneInfo

import psycopg
from psycopg import sql

from seeder import clock, ids, inputs, manifest

PASSWORD = "TRACIORA_DEMO_MANAGER_PASSWORD"
CONFIG_KEY = "config_key"  # traciora.core.queries.locations.CONFIG_KEY: the tenant's own key for a site
# The months of roles-and-places.en.json's closed_dates rule, in its order: its row names each closed day by its holiday.
EN_HOLIDAY_MONTHS = (1, 5, 7, 9, 11, 12)
# This step's own tables besides the ones it deletes from by id: a row there pointing at a seeded row is this step's.
OWN = {"identity.person", "identity.person_location", "identity.login", "core.location", "core.location_alias",
       "core.location_hours_exception", "core.position"}


def cast(cfg, client_id):
    """Each cast person as the core will hold them, after the shop database agrees: the employee row of the slot in the
    manifest; for a seasonal hire (a list there, one row per season) the last season that reaches into G..T, and when
    none does he is a row of the shop system only. A person is active exactly when that row employs them at T and ends
    on its last day (a fixed term's may be ahead of T); cast.json's status must say the same for everyone but a seasonal
    hire, whose status is his season's. Every disagreement is collected and raised together."""
    dsn = manifest.shop_dsn(client_id)
    built = manifest.read(dsn)
    if built.get("cfg") != cfg:
        raise SystemExit(f"the shop database is built for {built.get('cfg')}, not {cfg}")
    a = clock.anchors(cfg, manifest.at())
    T = a["T"].date()
    with psycopg.connect(dsn) as conn:
        employees = {r[0]: r for r in conn.execute(
            "SELECT employee_id, location_id, concat_ws(' ', first_name, middle_name, last_name), title, hired_on, left_on FROM shop.employee")}
    seed, ladder = inputs.load("cast.json"), {s["slot"]: s for s in inputs.load("tenant/ladder.json")["slots"]}
    people, wrong = [], []
    for p in seed["people"]:
        slot, x = p["slot"], ladder[p["slot"]]
        seasonal = isinstance(built["people"][slot], list)
        if seasonal:
            seasons = [employees[n] for n in built["people"][slot] if employees[n][4] <= T and employees[n][5] >= a["G"]]
            if not seasons:
                continue
            e = seasons[-1]
        else:
            e = employees[built["people"][slot]]
        number, name, title, hired, left = e[0], e[2], e[3], e[4], e[5]
        active = left is None or left > T
        if name != p[cfg]["full_name"]:
            wrong.append(f"{slot}: {p[cfg]['full_name']} in cast.json, employee {number} is {name}")
        if title != seed["roles"][p["role_key"]][cfg]:
            wrong.append(f"{slot}: role {p['role_key']} in cast.json, employee {number} is titled {title}")
        if e[1] != built["shops"].get(p["site"]):
            wrong.append(f"{slot}: shop {p['site']} in cast.json, employee {number} is at location {e[1]}")
        if not seasonal and active != (p["status"] == "active"):
            wrong.append(f"{slot}: {p['status']} in cast.json, employee {number} leaves on {left} (T {T})")
        people.append({"slot": slot, "name": p[cfg]["full_name"], "employee": number, "active": active, "started": hired,
                       "ended": left, "role": p["role_key"], "rank": x["rank"],
                       "username": x[f"username_{cfg}"], "postings": x["postings"], "home": x["home"]})
    if wrong:
        raise SystemExit("cast.json and the shop database disagree:\n  " + "\n  ".join(wrong))
    return people


def dated_hours(cfg, places, a):
    """{shop key: {date: (opens, closes, reason)}}: the stocktake day and every closed date from T's date to 60 days on."""
    T = a["T"].date()
    stock = next(c for c in places["changed_hours"] if c["ledger_key"] == "site.stocktake")
    shut = places["closed_dates"]
    closed = [T + dt.timedelta(n) for n in range(61) if clock.closed(cfg, T + dt.timedelta(n))]
    out = {}
    for place in places["places"]:
        days = {d: (None, None, shut["rule"][0 if (d.month, d.day) == (12, 31) else EN_HOLIDAY_MONTHS.index(d.month)]
                    if cfg == "en" else shut["row"]["reason"]) for d in closed if place["key"] in shut["sites"]}
        if place["key"] in stock["sites"]:
            days[a["stocktake"]] = (stock["row"]["open_local"], stock["row"]["close_local"], stock["row"]["reason"])
        out[place["key"]] = days
    return out


def step(cfg, client_id, replace):
    from traciora.core.auth.manager import AuthManager
    from traciora.core.commands import accounts, locations, logins, people as staff
    from traciora.core.commands.rows import insert, update
    from traciora.core.core_db.engine import connect, tenant_dsn
    from traciora.core.queries.logins import login_for_username
    from traciora.core.security.actors import actor

    password = os.environ.get(PASSWORD)
    if not password:
        raise SystemExit(f"{PASSWORD} is not set: every seeded account signs in with it")
    people = cast(cfg, client_id)
    places = inputs.load(f"tenant/roles-and-places.{cfg}.json")
    a = clock.anchors(cfg, manifest.at())
    now = a["T"].replace(tzinfo=ZoneInfo(inputs.value("geo.home_zone", cfg)))
    dated = dated_hours(cfg, places, a)
    with connect(tenant_dsn(client_id)) as conn:
        ranks = dict(conn.execute("SELECT key, rank FROM core.access_level WHERE active").fetchall())
    unknown = sorted({f"{p['slot']}: {p['rank']}" for p in people if p["rank"] != "none" and p["rank"] not in ranks})
    if unknown:
        raise SystemExit("ranks that are no live step of the tenant's ladder: " + ", ".join(unknown))
    if replace:
        reset(cfg, client_id)
    auth, rows = AuthManager(), 0
    with connect(tenant_dsn(client_id)) as conn:
        me = actor(conn, "system", "provisioning")
        position = {r["key"]: staff.position_id(conn, me, r["name"]) for r in places["roles"]}
        site = {}
        for place in places["places"]:
            found = conn.execute("SELECT location_id FROM core.location_alias WHERE namespace = %s AND value = %s",
                                 (CONFIG_KEY, place["key"])).fetchone()
            if found:
                site[place["key"]] = where = str(found[0])
            else:
                site[place["key"]] = where = locations.originate_location(conn, me, name=place["name"], tz=place["tz"], staffed=place["staffed"],
                                                                          address_raw=place["address"]).entity_id
                insert(conn, me, "core.location_alias", {"location_id": where, "namespace": CONFIG_KEY, "value": place["key"]}, {})
            locations.set_location_hours(conn, me, where, business_hours=place["business_hours"])
            locations.set_location_checkin(conn, me, where, latitude=place["latitude"], longitude=place["longitude"], radius_m=place["checkin_radius_m"])
            locations.set_location_extensions(conn, me, where, extensions=[x["ext"] for x in place["extensions"]])
            days = dated[place["key"]]
            for (day,) in conn.execute("SELECT on_date FROM core.location_hours_exception WHERE location_id = %s", (where,)).fetchall():
                if day not in days:  # a day of a build at another T
                    locations.remove_location_hours_exception(conn, where, on_date=day)
            for day, (opens, closes, reason) in sorted(days.items()):
                locations.set_location_hours_exception(conn, me, where, on_date=day, opens=opens, closes=closes, reason=reason, now=now)
            rows += 2 + len(place["extensions"]) + len(days)
        rows += len(position)
        for p in people:
            person = str(ids.uuid("person", p["slot"], cfg))
            # written on the staff, then a former person is ended through the accounts' lifecycle: a person written
            # inactive here would be marked removed (purged) by the command
            staff.upsert_person_by_id(conn, me, person, name=p["name"], origin="ui", active=True, started_on=p["started"],
                                      ended_on=p["ended"] if p["active"] else None, attrs_public={"employee_id": p["employee"]})
            for shop in p["postings"]:
                posting = {"is_home": shop == p["home"], "valid_from": p["started"], "valid_to": p["ended"]}
                held = conn.execute("SELECT id FROM identity.person_location WHERE person_id = %s AND location_id = %s AND position_id = %s",
                                    (person, site[shop], position[p["role"]])).fetchone()
                if held:  # one posting a shop, whatever T the last build had
                    update(conn, me, "identity.person_location", str(held[0]), posting, {})
                else:
                    staff.post_person(conn, me, person_id=person, location_id=site[shop], position_id=position[p["role"]], **posting)
            rows += 1 + len(p["postings"])
            if p["rank"] != "none":
                account = auth.get_manager_by_username(p["username"], include_inactive=True)
                if account is None:
                    if not auth.create_manager(p["username"], password, access_level=ranks[p["rank"]]):
                        raise SystemExit(f"the account {p['username']} could not be created")
                    account = auth.get_manager_by_username(p["username"], include_inactive=True)
                elif int(account["access_level"]) != ranks[p["rank"]]:
                    auth.set_manager_access_level_by_username(p["username"], ranks[p["rank"]])
                auth.set_manager_active(p["username"], True)
                before = login_for_username(conn, p["username"])
                logins.upsert_login(conn, me, username=p["username"], person_id=person, access_level_key=p["rank"],
                                    auth_ref=logins.auth_reference(int(account["id"])))
                if before and before["person_id"] != person:  # the staff record core_db init made for the account
                    conn.execute("DELETE FROM identity.person p WHERE id = %s AND origin = 'ui' AND NOT attrs_public ? 'employee_id'"
                                 " AND NOT EXISTS (SELECT 1 FROM identity.person_location WHERE person_id = p.id)", (before["person_id"],))
                rows += 1
            if not p["active"]:
                accounts.set_active(conn, me, auth, person_id=person, active=False, on=p["ended"])
        conn.commit()
    return rows


def references(conn, targets):
    """Rows of other stores that point at `targets` ({table: ids}), as 'table.column n', by every single-column
    foreign key the database declares on those tables."""
    found = []
    for schema, table, column, target in conn.execute(
            "SELECT rn.nspname, r.relname, a.attname, tn.nspname || '.' || t.relname FROM pg_constraint c"
            " JOIN pg_class r ON r.oid = c.conrelid JOIN pg_namespace rn ON rn.oid = r.relnamespace"
            " JOIN pg_class t ON t.oid = c.confrelid JOIN pg_namespace tn ON tn.oid = t.relnamespace"
            " JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]"
            " WHERE c.contype = 'f' AND cardinality(c.conkey) = 1 AND tn.nspname || '.' || t.relname = ANY(%s)", (list(targets),)).fetchall():
        if f"{schema}.{table}" in OWN or not targets[target]:
            continue
        n = conn.execute(sql.SQL("SELECT count(*) FROM {}.{} WHERE {} = ANY(%s::uuid[])").format(sql.Identifier(schema), sql.Identifier(table), sql.Identifier(column)),
                         (targets[target],)).fetchone()[0]
        if n:
            found.append(f"{schema}.{table}.{column} {n}")
    return found


def reset(cfg, client_id):
    """Both configurations' rows, so a build in one replaces the other: the cast's people with their postings and
    logins; the shops by their keys, with their aliases and dated hours; the positions of roles-and-places; the accounts
    of the ladder's usernames. The logins' actors stay (other stores' rows may name them). Refused, before anything is
    deleted, while another store's row points at one of them (in the core database or in auth.db)."""
    from traciora.core.auth.manager import AuthManager
    from traciora.core.core_db.engine import connect, tenant_dsn

    persons = [str(ids.uuid("person", p["slot"], c)) for p in inputs.load("cast.json")["people"] for c in ("en", "ru")]
    places = [inputs.load(f"tenant/roles-and-places.{c}.json") for c in ("en", "ru")]
    usernames = sorted({s[f"username_{c}"] for s in inputs.load("tenant/ladder.json")["slots"] for c in ("en", "ru")})
    auth = AuthManager()
    accounts = [a["id"] for a in (auth.get_manager_by_username(u, include_inactive=True) for u in usernames) if a]
    with connect(tenant_dsn(client_id)) as conn:
        shops = [str(r[0]) for r in conn.execute("SELECT location_id FROM core.location_alias WHERE namespace = %s AND value = ANY(%s)",
                                                 (CONFIG_KEY, [p["key"] for f in places for p in f["places"]])).fetchall()]
        positions = [str(r[0]) for r in conn.execute("SELECT id FROM core.position WHERE name = ANY(%s)",
                                                     ([r["name"] for f in places for r in f["roles"]],)).fetchall()]
        held = conn.execute("SELECT id::text, actor_id::text FROM identity.login WHERE person_id = ANY(%s::uuid[])", (persons,)).fetchall()
        found = references(conn, {"identity.person": persons, "core.location": shops, "core.position": positions,
                                  "identity.login": [r[0] for r in held], "core.actor": [r[1] for r in held]})
        with contextlib.closing(sqlite3.connect(auth.db_path)) as store:  # auth.db's rows that name an account by its id
            for (table,) in store.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name <> 'managers'").fetchall():
                if accounts and "manager_id" in [c[1] for c in store.execute(f"PRAGMA table_info({table})")]:
                    n = store.execute(f"SELECT count(*) FROM {table} WHERE manager_id IN ({','.join('?' * len(accounts))})", accounts).fetchone()[0]
                    if n:
                        found.append(f"auth.db {table}.manager_id {n}")
        if found:
            raise SystemExit("people: other stores' rows point at the seeded people, shops or sign-ins (" + ", ".join(found) +
                             "); reset those stores first: python -m seeder reset empties every step, the last first")
        conn.execute("DELETE FROM identity.login WHERE person_id = ANY(%s::uuid[])", (persons,))
        conn.execute("DELETE FROM identity.person_location WHERE person_id = ANY(%s::uuid[])", (persons,))
        conn.execute("DELETE FROM identity.person WHERE id = ANY(%s::uuid[])", (persons,))
        conn.execute("DELETE FROM core.location WHERE id = ANY(%s::uuid[])", (shops,))
        conn.execute("DELETE FROM core.position WHERE id = ANY(%s::uuid[])", (positions,))
        conn.commit()
    for username in usernames:
        if auth.get_manager_by_username(username, include_inactive=True):
            auth.delete_manager_row(username)
