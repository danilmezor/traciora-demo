"""python -m seeder.checks --cfg en|ru --at 'YYYY-MM-DD HH:MM' --db NAME|--dsn DSN [--file STATEMENTS] [--only PREFIX ...]:
every statement of a statements file (erp/checks.sql by default) run on a loaded database, its row read against the
`-- want:` line under its header. `--db` names a database in the container traciora-test-pg, read through its psql;
`--dsn` reaches any database through the driver, which fills the psql variables (`:'T'`) as psql does. A statement is of one of three kinds, named by a word after its key in the header (none: exact):
`exact` holds a planted fact, a count or an invariant (keys `inv.*`, expecting 0) as the file states it; `contrast`
holds a story's claim as an inequality; `band` holds an outcome inside a wide range, its want line `band(value, lo, hi)`.
Prints `FAIL <kind> <key>: ...` or `UNREAD <kind> <key>: ...` per statement that does not pass, `BAND <key> <value>
<lo> <hi>` per band statement read, then `CHECKS <cfg> pass=<p>/<n> unread=<u> exact=… contrast=… band=…` (passed/count
of each kind)."""
import argparse
import csv
import datetime as dt
import dis
import io
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

import psycopg

from seeder import clock, inputs

ERP = inputs.SEED / "erp" / "checks.sql"
PSQL =["docker", "exec", "-i", "traciora-test-pg", "psql", "-X", "-q", "-U", "postgres", "--csv", "-P", "null=\\N", "-v", "ON_ERROR_STOP=1", "-v", "VERBOSITY=verbose"]
HEADER = re.compile(r"-- ([A-Za-z0-9_.:]+) \|(?: (band|contrast) \|)?")
ANY_HEADER = re.compile(r"^-- [A-Za-z0-9_.:]+ \|", re.M)
KINDS = ("exact", "contrast", "band")
NUMBER = re.compile(r"-?(0|[1-9]\d*)(\.\d+)?")
BUILTINS = {f.__name__: f for f in (str, int, float, len, round, abs, min, max, all, any, sorted, sum, zip, range, enumerate, list, tuple, set, dict)}


def num(x):
    if isinstance(x, (int, float, Decimal)) and not isinstance(x, bool) or isinstance(x, str) and NUMBER.fullmatch(x):
        return Decimal(str(x))
    return None


def same(x, y):
    """Equal as numbers when both are numeric, else equal as text; None is never the same as anything."""
    if x is None or y is None:
        return False
    nx, ny = num(x), num(y)
    return nx == ny if nx is not None and ny is not None else str(x) == str(y)


def near(x, target, pct=None, abs=None):
    """x within pct per cent of target, or within abs of it (the wider when both are given)."""
    nx, nt = num(x), num(target)
    if nx is None or nt is None:
        return False
    tol = max(nt.copy_abs() * Decimal(str(pct or 0)) / 100, Decimal(str(abs or 0)))
    return -tol <= nx - nt <= tol


def each(text, targets, abs=None, pct=None, sep=", "):
    """A string_agg text compared member by member with targets: near when a tolerance is given, else same."""
    if text is None:
        return False
    parts = str(text).split(sep)
    return len(parts) == len(targets) and all(near(p, t, pct, abs) if pct or abs else same(p, t) for p, t in zip(parts, targets))


NAMES = {"value", "row", "L", "V", "a", "cfg", "same", "near", "each", "band", "date", "timedelta"} | set(BUILTINS)


def used_names(code):
    """The names an expression looks up, and every attribute name that starts with an underscore, in its code and every
    nested code object (lambdas, comprehensions): attributes such as `join` are free, `__class__` is not."""
    names = {i.argval for i in dis.get_instructions(code) if i.opname in ("LOAD_NAME", "LOAD_GLOBAL")} | {n for n in code.co_names if n.startswith("_")}
    return names.union(*(used_names(c) for c in code.co_consts if hasattr(c, "co_code")))


def variables(cfg, a):
    """The psql variables a statements file reads, from the clock's anchors `a`."""
    return {"cfg": cfg, "T": f"{a['T']:%Y-%m-%d %H:%M}"} | {n: str(a[n]) for n in ("G", "P", "bought", "s2_start", "fired", "rule_on", "leave_from", "leave_to", "pub_week")}


def psql(db, values):
    """A statement run by the psql of traciora-test-pg on database `db`: (SQLSTATE, error, None) or (None, None, rows)
    with the header row first and None for a null."""
    flags = [x for n, v in values.items() for x in ("-v", f"{n}={v}")]

    def execute(sql):
        done = subprocess.run(PSQL + flags + ["-d", db, "-f", "-"], input=sql, capture_output=True, text=True)
        error = re.search(r"ERROR:\s+(\w{5}): (.*)", done.stderr)
        if done.returncode:
            return (error.group(1), error.group(2)) if error else (None, done.stderr.strip() or "psql failed"), None
        return None, [[None if cell == "\\N" else cell for cell in r] for r in csv.reader(io.StringIO(done.stdout))]

    return execute


def direct(dsn, values):
    """`psql` through the driver on any database: each `:'name'` of a set variable becomes its quoted text, and a cell is
    the server's text of the value, as psql prints it."""
    def execute(sql):
        sql = re.sub(r":'(\w+)'", lambda m: "'" + values[m[1]].replace("'", "''") + "'" if m[1] in values else m[0], sql)
        try:
            with psycopg.connect(dsn, autocommit=True) as conn:
                cur = conn.execute(sql)
                result = cur.pgresult
                while cur.nextset():  # the SET lines come first: the statement's result is the last
                    result = cur.pgresult
        except psycopg.Error as problem:
            return (problem.sqlstate, problem.diag.message_primary or str(problem).strip()), None
        names = [result.fname(i).decode() for i in range(result.nfields)]
        cells = [[None if (v := result.get_value(r, i)) is None else v.decode() for i in range(result.nfields)] for r in range(result.ntuples)]
        return None, [names] + cells

    return execute


def describe(path):
    """Each band statement's definition, window, unit and tax basis from its header; eval_answer false where an eval does
    not ask it."""
    described = {}
    for m in re.finditer(r"^-- ([A-Za-z0-9_.:]+) \| band \|(.*)$", path.read_text(encoding="utf-8"), re.M):
        fields = dict(part.split(": ", 1) for part in m.group(2).split(" | ") if part.split(": ", 1)[0] in ("definition", "window", "unit", "tax", "eval_answer"))
        described[m.group(1)] = {k: fields.get(k) for k in ("definition", "window", "unit", "tax")} | {"eval_answer": fields.get("eval_answer") != "false"}
    return described


def run(cfg, a, path, execute, only=(), kinds=KINDS):
    """Every statement of the file at `path` whose key starts with one of `only` (all without) and whose kind is in
    `kinds`, run by `execute` at the clock's anchors `a`: the lines to print, whether all passed, and per band statement
    read its value and bounds as text ({key: {"value", "band": [lo, hi]}})."""
    out, measured = [], {}
    text = path.read_text(encoding="utf-8")
    preamble = "".join(line + "\n" for line in text.splitlines() if re.match(r"SET \w+ = \w+;$", line))
    passed, total = dict.fromkeys(KINDS, 0), dict.fromkeys(KINDS, 0)
    unread, readable, starts = 0, [], 0
    for block in text.split("\n\n"):  # a statement: its header, its want line, its SQL; blank lines between statements
        lines = block.strip("\n").splitlines()
        header = HEADER.match(lines[0]) if lines else None
        if not header:
            sql = [line for line in lines if line.strip() and not line.startswith("--") and not re.match(r"SET \w+ = \w+;$", line)]
            if sql:  # a statement without a header would go unchecked; the file's comments and SET preamble are not one
                total["exact"], unread = total["exact"] + 1, unread + 1
                out.append(f"UNREAD exact (no header): {sql[0][:120]}")
            continue
        starts += 1
        key, kind = header.group(1), header.group(2) or "exact"
        if only and not key.startswith(tuple(only)) or kind not in kinds:
            continue
        total[kind] += 1
        want = lines[1][len("-- want: "):] if len(lines) > 1 and lines[1].startswith("-- want: ") else None
        # two statements with no blank line between them read as one: the second would never run
        why = ("no want line" if want is None else
               "a second header or want line in its block (a blank line missing)" if len(ANY_HEADER.findall(block)) > 1 or sum(x.startswith("-- want:") for x in lines) > 1 else None)
        if not why:
            try:
                code = compile(want, key, "eval")
                names = used_names(code)
                outside = sorted(names - NAMES)
                why = ("names outside the contract: " + ", ".join(outside) if outside else
                       "no ledger row" if "L" in names and key not in inputs.ROWS else
                       f"a {kind} statement {'without' if kind == 'band' else 'with'} band()" if ("band" in names) != (kind == "band") else None)
            except SyntaxError as problem:
                why = f"does not compile: {problem.msg}"
        if why:
            unread += 1
            out.append(f"UNREAD {kind} {key}: {why}")
            continue
        readable.append((key, kind, want, code, preamble + "\n".join(lines[2:]) + "\n"))
    headers = len(ANY_HEADER.findall(text))
    if headers != starts:  # a header that does not start its block
        total["exact"], unread = total["exact"] + 1, unread + 1
        out.append(f"UNREAD exact (file): {headers} header lines, {starts} statements start with one")
    with ThreadPoolExecutor(8) as pool:  # the statements only read, so they run side by side; results are read in file order
        runs = list(pool.map(lambda r: execute(r[4]), readable))
    for (key, kind, want, code, _), (error, table) in zip(readable, runs):
        if error and (error[0] or "")[:2] in ("21", "22"):  # a subquery of several rows, a division by zero, ...: the data fails it
            out.append(f"FAIL {kind} {key}: {error[1][:120]} | want: {want}")
            continue
        if error:
            unread += 1
            out.append(f"UNREAD {kind} {key}: {error[1][:200]}")
            continue
        cells = table[1] if len(table) > 1 else [None] * len(table[0])
        row = {name: None if cell is None else (Decimal(cell) if "." in cell else int(cell)) if NUMBER.fullmatch(cell) else cell
               for name, cell in zip(table[0], cells)}
        value = list(row.values())[1] if len(row) > 1 else None
        first = str(list(row.values())[0]) if row else ""
        if first != key and not first.startswith(key + ":"):
            unread += 1
            out.append(f"UNREAD {kind} {key}: its SELECT returns the key {first}")
            continue
        bounds = []

        def band(x, lo, hi):  # an outcome inside [lo, hi]; the bounds are printed for the manifest
            bounds.append(tuple(round(Decimal(str(x)), 4).normalize() for x in (lo, hi)))
            return num(x) is not None and bounds[-1][0] <= num(x) <= bounds[-1][1]

        names = {"value": value, "row": row, "L": inputs.value(key, cfg) if key in inputs.ROWS else None, "V": lambda k: inputs.value(k, cfg),
                 "a": a, "cfg": cfg, "same": same, "near": near, "each": each, "band": band, "date": dt.date, "timedelta": dt.timedelta}
        try:
            ok, raised = eval(code, {"__builtins__": BUILTINS} | names), ""
        except Exception as problem:  # a want that raises on this row fails it
            ok, raised = False, f" ({type(problem).__name__}: {problem})"
        if bounds:
            measured[key] = {"value": str(value), "band": [f"{bounds[0][0]:f}", f"{bounds[0][1]:f}"]}
            out.append(f"BAND {key} {value} {bounds[0][0]:f} {bounds[0][1]:f}")
        if ok:
            passed[kind] += 1
        else:
            shown = value if len(row) <= 2 else " ".join(f"{k}={v}" for k, v in list(row.items())[1:])
            out.append(f"FAIL {kind} {key}: {str(shown)[:120]} | want: {want}{raised}")
    n, p = sum(total.values()), sum(passed.values())
    out.append(f"CHECKS {cfg} pass={p}/{n} unread={unread} " + " ".join(f"{k}={passed[k]}/{total[k]}" for k in KINDS))
    return out, bool(n) and p == n, measured


def main():
    parser = argparse.ArgumentParser(prog="python -m seeder.checks")
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--at", required=True, type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M"), help="the build instant on the home clock")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--db", help="a database in traciora-test-pg")
    target.add_argument("--dsn", help="any database, through the driver")
    parser.add_argument("--file", type=Path, default=ERP, help="the statements file (default v1/erp/checks.sql)")
    parser.add_argument("--only", nargs="+", default=(), help="keep the statements whose key starts with one of these")
    args = parser.parse_args()
    a = clock.anchors(args.cfg, args.at)
    values = variables(args.cfg, a)
    out, ok, _ = run(args.cfg, a, args.file, direct(args.dsn, values) if args.dsn else psql(args.db, values), args.only)
    print("\n".join(out))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
