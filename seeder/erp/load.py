"""The build's tables and their loader. A row is a dict of column to value without its primary key; a foreign key
holds the referenced row's dict itself, so any step can create rows in any order. `finalise` gives every table its
dense ids in time order (generator-spec.md section 1, "Ids") and `load` copies the result into a fresh schema `shop`."""
import datetime as dt
import re

import psycopg

from seeder import inputs

FIRST = {
    "location": "opened_on",
    "employee": "hired_on",
    "referral_source": None,
    "customer": "created_at",
    "customer_contact": "started_on",
    "vehicle": "customer_id.created_at",
    "service_category": None,
    "canned_job": None,
    "labor_rate": "valid_from",
    "vendor": None,
    "part": None,
    "statement": "issued_on",
    "repair_order": "opened_at",
    "order_status_history": "changed_at",
    "order_job": "repair_order_id.opened_at",
    "order_labor": "order_job_id.repair_order_id.opened_at",
    "order_part": "order_job_id.repair_order_id.opened_at",
    "order_sublet": "order_job_id.repair_order_id.opened_at",
    "order_fee": "repair_order_id.opened_at",
    "inspection": "completed_at",
    "inspection_item": "inspection_id.completed_at",
    "time_entry": "clock_in",
    "appointment": "booked_at",
    "payment": "received_at",
    "cash_drawer_close": "business_date",
    "purchase_order": "ordered_at",
    "purchase_order_line": "purchase_order_id.ordered_at",
    "stock_level": None,
    "part_return": "returned_on",
    "stock_movement": "moved_at",
    "service_reminder": "created_on",
}

SQL = (inputs.SEED / "erp" / "schema.sql").read_text(encoding="utf-8")


# A row whose first moment is not the column FIRST names (a car added to an existing customer) carries it under this
# key; finalise sorts by it and drops it.
FIRST_KEY = "_first"

# Per table, in the file's order (which is a foreign-key order, or the file would not load): its columns, primary key,
# references (column to table) and defaults. Column lines are lower case; constraint lines (CHECK, UNIQUE) are not.
SCHEMA = {}
for _name, _body in re.findall(r"CREATE TABLE shop\.(\w+) \((.*?)\n\);", SQL, re.S):
    _columns = re.findall(r"^    ([a-z_]+) +(.*?),?$", _body, re.M)
    _defaults = [(c, m[1]) for c, rest in _columns if (m := re.search(r"DEFAULT ('[^']*'|\w+)", rest))]
    SCHEMA[_name] = {
        "columns": [c for c, _ in _columns],
        "pk": next(c for c, rest in _columns if "PRIMARY KEY" in rest),
        "refs": {c: m[1] for c, rest in _columns if (m := re.search(r"REFERENCES shop\.(\w+)", rest))},
        "defaults": {c: d[1:-1] if d[0] == "'" else d == "true" if d in ("true", "false") else int(d) for c, d in _defaults},
    }
assert len(SCHEMA) == 31 and set(SCHEMA) == set(FIRST), "schema.sql and FIRST disagree"


def finalise(tables):
    """Every table as a list of tuples in schema column order, primary key first, sorted by its first moment (the row's
    FIRST_KEY, else the path FIRST names; ties keep insertion order), keys dense from 1, every reference replaced by
    the referenced row's key; and per table each row's key ({id(row): key})."""
    keys, ordered = {}, {}
    for name, spec in SCHEMA.items():
        rows = tables.get(name, [])
        for row in rows:
            unknown = set(row) - set(spec["columns"]) - {FIRST_KEY} | {spec["pk"]} & set(row)
            if unknown:
                raise ValueError(f"{name}: columns {sorted(unknown)} are not its own (or are its key): {row}")
        if FIRST[name]:
            moments = []
            for row in rows:
                value = row.get(FIRST_KEY)
                if value is None:
                    value = row
                    for column in FIRST[name].split("."):
                        value = value.get(column) if value is not None else None
                if value is None:
                    raise ValueError(f"a {name} row has neither {FIRST_KEY} nor {FIRST[name]}: {row}")
                moments.append(value if isinstance(value, dt.datetime) else dt.datetime.combine(value, dt.time()))
            rows = [row for _, _, row in sorted(zip(moments, range(len(rows)), rows), key=lambda m: m[:2])]
        keys[name] = {id(row): n for n, row in enumerate(rows, 1)}
        ordered[name] = rows

    def cell(name, row, column):
        spec = SCHEMA[name]
        if column == spec["pk"]:
            return keys[name][id(row)]
        value = row.get(column, spec["defaults"].get(column))
        if column in spec["refs"] and value is not None:
            try:
                return keys[spec["refs"][column]][id(value)]
            except KeyError:
                raise ValueError(f"{name}.{column} points at a row that is not in {spec['refs'][column]}: {value}") from None
        return value

    return {name: [tuple(cell(name, row, c) for c in SCHEMA[name]["columns"]) for row in rows] for name, rows in ordered.items()}, keys


def load(dsn, rows, replace=False):
    """One transaction: the schema, then every table by COPY in the schema's order. The one self-reference
    (repair_order.comeback_of_id) is checked at the end of its COPY statement, so no constraint is deferred. A replaced
    schema shop takes schema seed with it: a manifest never stands beside another build."""
    with psycopg.connect(dsn) as conn:
        if conn.execute("SELECT 1 FROM pg_namespace WHERE nspname = 'shop'").fetchone():
            if not replace:
                raise SystemExit("the database already has a schema shop; pass --replace to drop it")
            conn.execute("DROP SCHEMA shop CASCADE")
            conn.execute("DROP SCHEMA IF EXISTS seed CASCADE")
        conn.execute(SQL)
        for name, spec in SCHEMA.items():
            with conn.cursor().copy(f"COPY shop.{name} ({', '.join(spec['columns'])}) FROM STDIN") as copy:
                for row in rows[name]:
                    copy.write_row(row)
        conn.commit()
        conn.execute("ANALYZE")
