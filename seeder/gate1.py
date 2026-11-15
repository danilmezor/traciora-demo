"""Gate 1 of seed v1: the shop-system generator is done when this prints PASS for both configurations.

    python seeder/gate1.py [--head COMMIT] [--gate0 LINES] [--write]

COMMIT names the tested tree where it is no checkout (the build box), with `-dirty` when the tree differs from it; else
git gives it. A dirty tree never passes. LINES are Gate 0's FAIL lines and last line, run where the product's repository
is: its tenant check reads that repository and imports the product's tool catalogue, which the build box does not have;
its last line must name the same commit. Without LINES the gate runs Gate 0 itself. --write writes the manifests and the
answer pages of this build instead of comparing them. seeder/README.md has the build box's command.

Per configuration, a build at 10:30 of each sweep day (the nominal T, Friday 2026-11-13; Tuesday 2026-11-10; the 14
days after the nominal T; six later days), seeds 2 and 3 at the nominal T and a repeat of the nominal build under
another hash seed, each in its own database of traciora-test-pg, dropped when read; as many at once as the memory
holds, at most six. A day the generator cannot place builds at an earlier instant (its ERP line names the T it used):
it counts as built, its checks read the T it used, and the gate says how many days fell back and the farthest in days;
a day that falls back more than MAX_FALLBACK days fails. With --write the line says WROTE, never PASS.
B1: every build succeeds. B2: on every build each statement of erp/checks.sql, as many as the file holds, meets its
want line (seeder.checks): exact statements and invariants, contrasts, and B3: bands. B3: the bands' values at the
nominal T, seed 1 are v1/manifest.<cfg>.json. B4: the shop goldens of the yaml pass the product's golden.py `check`
through `run_questions` on the builds of the nominal T and Tuesday, run as the product runs them (its statement guard,
its driver, its row cap) with `now()` pinned to the build's T; each constrains its rows, and one that returns its rule's
ledger figure carries that figure and its tolerance; at the nominal T the reference query's rows hold the golden's
expect_keys and top, and every golden's rows are v1/goldens/answers.<cfg>.txt. B5: the repeat build is identical,
table by table, and Gate 0 (v1/checks/gate.py) passes on the same commit.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))  # run as a file, the folder that holds the package is not on the path

from seeder import checks, clock, inputs  # noqa: E402
from traciora.data.context.golden import RESULT_ROW_CAP, check, load_questions, run_questions  # noqa: E402
from traciora.data.sources.guard import check as guard  # noqa: E402
from traciora.data.sources.postgres import PostgresDriver  # noqa: E402

NOMINAL, TUESDAY = "2026-11-13", "2026-11-10"
DAYS = [NOMINAL, TUESDAY] + [str(dt.date(2026, 11, 14) + dt.timedelta(i)) for i in range(14)] + [
    "2026-12-11", "2027-01-22", "2027-03-12", "2027-06-25", "2027-08-17", "2027-10-05"]
SEEDS = (1, 2, 3)
ANSWER_ROWS = 15
MAX_FALLBACK = 7  # days a sweep day may fall back
SERVER = "postgresql://postgres:traciora@127.0.0.1:55934/"
# a build holds about 1.2 GB and the machine is shared: one build per 4 GB of memory, at most six
WORKERS = max(1, min(6, os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") // 4 ** 16))
# The session's search path puts seedclock ahead of pg_catalog, so an unqualified now() is seedclock.now(). These read
# the clock some other way and so would see the real moment: the SQL keywords for the current moment, the functions
# beside now(), the session and server start times, the input literals 'now' and 'today' however quoted, a qualified
# pg_catalog.now() and age(), which counts from current_date with one argument.
CLOCKS = re.compile(r"(?i)\b(current_date|current_time|current_timestamp|localtime|localtimestamp|transaction_timestamp|"
                    r"statement_timestamp|clock_timestamp|timeofday|xact_start|query_start|backend_start|"
                    r"pg_postmaster_start_time|pg_conf_load_time)\b|'\s*(now|today|tomorrow|yesterday)\s*'|"
                    r"\$(\w*)\$\s*(now|today|tomorrow|yesterday)\s*\$\3\$|\"?\bpg_catalog\b\"?\s*\.\s*\"?now\b\"?|\bage\s*\(")


def admin(sql):
    with psycopg.connect(SERVER + "postgres", autocommit=True) as conn:
        conn.execute(sql)


def why_failed(q, got, zone, cfg):
    """Why one golden fails, or None: its SQL's error or the assertion it breaks, an expectation of its columns only,
    a clock it reads past seedclock, or a ledger figure it does not carry as the ledger states it."""
    expected = q["expected"]
    if isinstance(got, Exception):
        return f"{type(got).__name__}: " + (str(got).strip().splitlines() or [""])[0][:160]
    columns, rows = got
    try:
        check(columns, rows, expected)
    except Exception as problem:
        return f"{type(problem).__name__}: {problem} (rows={len(rows)}" + (f", got {rows[0][0]}" if len(rows) == 1 and len(rows[0]) == 1 else "") + ")"
    if not expected.keys() & {"value", "rows", "nonempty"}:
        return "expects its columns only, which zero rows meet"
    # now() is seedclock's T only read on a stated clock: the home zone, or a shop's own zone from its row; bare, it
    # reads the session's zone (UTC on the build box), hours off
    bare = re.compile(r"(?i)\"?\bnow\b\"?\s*\(\s*\)(?!\s*AT\s+TIME\s+ZONE\s+(%s|\w+\.time_zone\b))" % re.escape(f"'{zone}'"))
    clocks = sorted({m.group(0).lower() for m in CLOCKS.finditer(q["sql"])} | {"now() off the home clock" for _ in bare.finditer(q["sql"])})
    if clocks:
        return f"reads {', '.join(clocks)}, which seedclock does not pin"
    if "figure_scale" in q or "value" in expected:
        row = inputs.ROWS.get(q["rule"])
        if row is None or "figure_scale" not in q:
            return f"carries a value but no ledger figure: rule {q['rule']}, figure_scale {q.get('figure_scale')}"
        if row.get("tolerance") is None:
            return f"ledger row {q['rule']} has no tolerance"
        value = Decimal(str(inputs.value(q["rule"], cfg))) * q["figure_scale"]
        per_cent = row.get("tolerance_unit") == "per cent of the value"
        tolerance = Decimal(str(row["tolerance"])) * (abs(value) / 100 if per_cent else q["figure_scale"])
        if "value" not in expected or (Decimal(str(expected["value"])), Decimal(str(expected.get("tolerance", 0)))) != (value, tolerance):
            return f"value {expected.get('value')} ± {expected.get('tolerance')} is not ledger {q['rule']}: {value} ± {tolerance}"
    return None


def held(cell, key):
    """A key of expect_keys or top in a result cell: a number equal to it, a text inside it."""
    if isinstance(key, (int, float)):
        try:
            return Decimal(str(cell)) == Decimal(str(key))
        except ArithmeticError:
            return False
    return str(key) in str(cell)


def keys_missed(q, columns, rows, a):
    """Why the reference query's rows do not name the golden's story keys, or None. A key '@<expression>' is a date of
    the clock's anchors `a` at the build's T: a list as a column's expect_keys, or one date (`@week_day(-22, 2)`)."""
    def anchor(key):
        return eval(key[1:], {"__builtins__": {}} | a) if isinstance(key, str) and key.startswith("@") else key

    for column, keys in q.get("expect_keys", {}).items():
        keys = {str(d): 1 for d in anchor(keys)} if isinstance(keys, str) else {str(anchor(k)) if anchor(k) is not k else k: n for k, n in keys.items()}
        cells = [row[list(columns).index(column)] for row in rows]
        got = {key: sum(held(cell, key) for cell in cells) for key in keys}
        stray = [str(cell) for cell in cells if not any(held(cell, key) for key in keys)]
        if got != keys or stray:
            return f"{column} holds {got}" + (f" and {', '.join(stray[:3])}" if stray else "") + f", not {keys}"
    for column, keys in q.get("top", {}).items():
        keys = [str(anchor(k)) if anchor(k) is not k else k for k in (keys if isinstance(keys, list) else [keys])]
        cells = [row[list(columns).index(column)] for row in rows[:len(keys)]]
        if len(cells) < len(keys) or not all(held(cell, key) for cell, key in zip(cells, keys)):
            return f"top {column} is {cells}, not {keys}"
    return None


def answers(cfg, t, questions, seen):
    """The page of every golden's question and its reference rows, at most ANSWER_ROWS a golden."""
    out = [f"# Shop goldens ({cfg}) at T {t:%Y-%m-%d %H:%M}, seed 1: each question and its reference query's rows."]
    for q in questions:
        out += ["", f"## {q['id']}", q["question"] or "(no question)"]
        got = seen.get(q["sql"], RuntimeError("not run"))
        if isinstance(got, Exception):
            out.append(f"error: {type(got).__name__}: " + (str(got).strip().splitlines() or [""])[0][:160])
            continue
        columns, rows = got
        out.append(" | ".join(columns))
        out += [" | ".join("null" if x is None else str(x) for x in row) for row in rows[:ANSWER_ROWS]]
        out.append(f"({len(rows)} row{'' if len(rows) == 1 else 's'}" + (f", the first {ANSWER_ROWS} shown)" if len(rows) > ANSWER_ROWS else ")"))
    return "\n".join(out) + "\n"


def goldens(cfg, db, t, nominal):
    """The goldens' score on one build at T `t` and, per failing id, why; at the nominal T also their story keys and the
    answer page."""
    zone = inputs.value("geo.home_zone", cfg)
    with psycopg.connect(SERVER + db, autocommit=True) as conn:
        conn.execute(f"CREATE SCHEMA seedclock; CREATE FUNCTION seedclock.now() RETURNS timestamptz IMMUTABLE LANGUAGE sql "
                     f"AS $$ SELECT TIMESTAMP '{t:%Y-%m-%d %H:%M}' AT TIME ZONE '{zone}' $$")
    questions = load_questions(inputs.SEED / "goldens" / f"shop.{cfg}.yaml")
    driver, seen = PostgresDriver(SERVER + db), {}
    options = "-c search_path=seedclock,pg_catalog,public -c default_transaction_read_only=on -c statement_timeout=30000"
    with psycopg.connect(SERVER + db, options=options) as conn:
        pinned = conn.execute(f"SELECT (now() AT TIME ZONE '{zone}')::text").fetchone()[0]
        conn.rollback()
        if pinned != f"{t:%Y-%m-%d %H:%M}:00":
            raise RuntimeError(f"now() reads {pinned}, not T")

        def execute(sql):  # what the product's run_live does, keeping each result to say why a golden failed
            try:
                guard(sql, driver.dialect)
                result = driver.run(conn, sql, row_cap=RESULT_ROW_CAP)
                if result.truncated or len(result.rows) >= RESULT_ROW_CAP:
                    raise AssertionError("golden result at row cap is a failure")
            except Exception as problem:
                seen[sql] = problem
                raise
            seen[sql] = result.columns, result.rows
            return seen[sql]

        score = run_questions(questions, execute)
    why = {}
    for q in questions:
        got = seen.get(q["sql"], RuntimeError("not run"))
        try:
            reason = why_failed(q, got, zone, cfg) or (keys_missed(q, *got, clock.anchors(cfg, t)) if nominal else None)
        except Exception as problem:  # one golden's own defect is its reason, not the build's
            reason = f"{type(problem).__name__}: {problem}"
        if q["id"] in score.failed and not reason:
            reason = "run_questions failed it"
        if reason:
            why[q["id"]] = reason
    return len(questions) - len(why), len(questions), why, answers(cfg, t, questions, seen) if nominal else None


def tables(db):
    """Per table of schema shop, the hash of its rows in key order."""
    hashes = {}
    with psycopg.connect(SERVER + db) as conn:
        names = [n for (n,) in conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'shop' "
                                            "AND table_type = 'BASE TABLE' ORDER BY 1")]
        for name in names:
            digest = hashlib.sha256()
            with conn.cursor().copy(f"COPY (SELECT * FROM shop.{name} ORDER BY 1) TO STDOUT") as copy:
                for block in copy:
                    digest.update(block)
            hashes[name] = digest.hexdigest()
    return hashes


def job(cfg, day, seed, repeat, db):
    """One build at 10:30 of `day` and what is read on it: the checks, unless it is the repeat; the goldens on the
    nominal and the Tuesday build of seed 1; the table hashes on the nominal build and the repeat. The repeat runs under
    another hash seed, so an identical repeat also proves the build does not follow the order of a set or a dict of
    strings. The database is dropped at the end."""
    env = os.environ | {"PYTHONHASHSEED": "1" if repeat else "0"}
    admin(f"CREATE DATABASE {db}")
    try:
        built = subprocess.run([sys.executable, "-m", "seeder", "erp", "--cfg", cfg, "--at", f"{day} 10:30", "--dsn", SERVER + db, "--seed", str(seed)],
                               cwd=ROOT, env=env, capture_output=True, text=True)
        used = re.search(r"^ERP \w+ T=(\S+ \S+) ", built.stdout, re.M)
        if built.returncode or not used:
            return {"error": (built.stderr.strip().splitlines() or built.stdout.strip().splitlines() or ["failed"])[-1][:200]}
        t = dt.datetime.strptime(used.group(1), "%Y-%m-%d %H:%M")
        open_day = dt.date.fromisoformat(day)
        while not clock.main_open(cfg, open_day):
            open_day -= dt.timedelta(1)
        # T moves back to the flagship's last close on a day it does not open (ledger time.t_rule); earlier is a fallback
        fell_back = t.date() < open_day or open_day == dt.date.fromisoformat(day) and t != dt.datetime.combine(open_day, dt.time(10, 30))
        out = {"T": t, "fell_back": (open_day - t.date()).days if fell_back else None}
        nominal = day == NOMINAL and seed == 1
        if repeat:
            return out | {"hashes": tables(db)}
        # the checks run in their own process while this thread hashes the tables and runs the goldens; all of it only reads
        checking = subprocess.Popen([sys.executable, "-m", "seeder.checks", "--cfg", cfg, "--at", f"{t:%Y-%m-%d %H:%M}", "--db", db],
                                    cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            if nominal:
                out["hashes"] = tables(db)
            if seed == 1 and day in (NOMINAL, TUESDAY):
                out["goldens"] = goldens(cfg, db, t, nominal)
        finally:  # the checks finish on the database before it is dropped
            stdout, stderr = checking.communicate()
    finally:
        admin(f"DROP DATABASE IF EXISTS {db} WITH (FORCE)")
    last = (stdout.strip().splitlines() or [""])[-1]
    summary = re.fullmatch(rf"CHECKS {cfg} pass=(\d+)/(\d+) unread=(\d+) .*", last)
    if not summary:
        return out | {"error": "checks: last line is not a CHECKS line: " + (last or stderr.strip()[-200:])[:200]}
    passed, total, unread = map(int, summary.groups())
    if (checking.returncode == 0) != (total > 0 and passed == total):
        return out | {"error": f"checks: exit {checking.returncode} disagrees with {last}"}
    out["total"] = total
    out["failed"] = {m.group(3): (m.group(2), m.group(0)) for m in re.finditer(r"^(FAIL|UNREAD) (\w+) (.+?): .*$", stdout, re.M)}
    out["bands"] = {m.group(1): {"value": m.group(2), "band": [m.group(3), m.group(4)]}
                    for m in re.finditer(r"^BAND (\S+) (\S+) (\S+) (\S+)$", stdout, re.M)}
    return out


def where(builds):
    """The builds of one finding, as `11-20` for a day of seed 1 and `11-13/s2` for another seed."""
    return ",".join(day[5:] + (f"/s{seed}" if seed > 1 else "") for day, seed in builds)


def compare(path, text, write):
    """None when the committed file holds `text` (or is written now), else what differs first."""
    if write:
        path.write_text(text, encoding="utf-8")
        return None
    old = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    new = text.splitlines()
    if old == new:
        return None
    i = next((i for i, (a, b) in enumerate(zip(old, new)) if a != b), min(len(old), len(new)))
    return f"{path.relative_to(ROOT)} differs from the build at line {i + 1}: " + (f"committed '{old[i][:90]}'" if i < len(old) else "committed ends") + \
        (f", built '{new[i][:90]}'" if i < len(new) else ", built ends")


def stop(signum, _frame):
    raise SystemExit(128 + signum)  # through main's cleanup


def main():
    parser = argparse.ArgumentParser(prog="seeder/gate1.py")
    parser.add_argument("--head", help="the commit of the tested tree, with -dirty when the tree differs from it")
    parser.add_argument("--gate0", help="Gate 0's FAIL lines and last line, when it ran elsewhere")
    parser.add_argument("--write", action="store_true", help="write the manifests and answer pages instead of comparing them")
    args = parser.parse_args()
    started = time.monotonic()
    head = args.head
    if not head:
        try:
            git = ["git", "-C", str(ROOT)]
            head = subprocess.run(git + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
            if head and subprocess.run(git + ["status", "--porcelain"], capture_output=True, text=True).stdout.strip():
                head += "-dirty"
        except OSError:  # no git on the box
            pass
    head = head or "nohead"
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGHUP, stop)
    with psycopg.connect(SERVER + "postgres", autocommit=True) as conn:  # what a gate killed before its cleanup left
        for (name,) in conn.execute("SELECT datname FROM pg_database WHERE datname ~ '^seed_gate_[0-9]+(_|$)'").fetchall():
            try:
                os.kill(int(re.match(r"seed_gate_(\d+)", name).group(1)), 0)
            except ProcessLookupError:
                conn.execute(f"DROP DATABASE IF EXISTS {name} WITH (FORCE)")
            except PermissionError:  # alive, another user's
                pass
    runs = [(cfg, day, 1, False) for day in DAYS for cfg in ("en", "ru")] + \
           [(cfg, NOMINAL, seed, False) for seed in SEEDS[1:] for cfg in ("en", "ru")] + [(cfg, NOMINAL, 1, True) for cfg in ("en", "ru")]
    dbs = {r: f"seed_gate_{os.getpid()}_{r[0]}_{r[1].replace('-', '')}_s{r[2]}{'_repeat' if r[3] else ''}" for r in runs}
    pool = ThreadPoolExecutor(WORKERS)  # each build and its checks are processes of their own
    try:
        gate0 = None if args.gate0 else ThreadPoolExecutor(1).submit(
            subprocess.run, [sys.executable, str(ROOT / "v1" / "checks" / "gate.py")], env=os.environ | {"PYTHONHASHSEED": "0"}, capture_output=True, text=True)
        futures = {r: pool.submit(job, *r, dbs[r]) for r in runs}
        done = {}
        for r, future in futures.items():
            try:
                done[r] = future.result()
            except Exception as problem:
                done[r] = {"error": f"{type(problem).__name__}: {str(problem).strip()[:200]}"}
        gate0 = args.gate0 or gate0.result().stdout + gate0.result().stderr
    finally:
        # dropped before the workers are awaited, so after a signal the builds and checks on them end at once; again
        # after, for a database a worker was creating meanwhile
        for _ in range(2):
            for db in dbs.values():
                admin(f"DROP DATABASE IF EXISTS {db} WITH (FORCE)")
            pool.shutdown(cancel_futures=True)
    seconds = round(time.monotonic() - started)
    gate0_failed = [f"  gate0 {line.strip()[:220]}" for line in gate0.splitlines() if line.startswith("  FAIL")]
    if not re.search(rf"^SEED GATE v1 {re.escape(head.removesuffix('-dirty'))} PASS ", gate0, re.M):
        gate0_failed.append(f"  gate0 is not a PASS of {head.removesuffix('-dirty')}: " + (gate0.strip().splitlines() or ["no output"])[-1][:200])
    described = checks.describe(checks.ERP)
    passed = 0
    for cfg in ("en", "ru"):
        builds = {(day, seed): done[(cfg, day, seed, False)] for day in DAYS for seed in SEEDS if (cfg, day, seed, False) in done}
        again = done[(cfg, NOMINAL, 1, True)]
        failed = [f"  build {day} 10:30{f' seed {seed}' if seed > 1 else ''}: {r['error']}" for (day, seed), r in builds.items() if "error" in r and "T" not in r]
        failed += [f"  {day} 10:30{f' seed {seed}' if seed > 1 else ''}: {r['error']}" for (day, seed), r in builds.items() if "error" in r and "T" in r]
        if "error" in again:
            failed.append(f"  build {NOMINAL} 10:30 repeat: {again['error']}")
        built = [b for b in builds if "T" in builds[b]]
        read = {b: r for b, r in builds.items() if "total" in r}
        days = sum((day, 1) in built for day in DAYS)
        seeds = sum((NOMINAL, seed) in built for seed in SEEDS)
        fell_back = {day: builds[(day, 1)]["fell_back"] for day in DAYS if (day, 1) in built and builds[(day, 1)]["fell_back"] is not None}
        failed += [f"  {day} fell back {n} days, to {builds[(day, 1)]['T']:%Y-%m-%d %H:%M}" for day, n in fell_back.items() if n > MAX_FALLBACK]
        totals = {r["total"] for r in read.values()}
        total = max(totals, default=0)
        if len(totals) > 1:
            failed.append(f"  statements: the builds read {sorted(totals)} statements")
        findings = {}  # key -> kind, the builds it fails on, its first line
        for b, r in read.items():
            for key, (kind, line) in r["failed"].items():
                kind = "unread" if line.startswith("UNREAD") else "invariant" if key.startswith("inv.") else kind
                findings.setdefault(key, (kind, [], line))[1].append(b)
        for kind in ("unread", "exact", "invariant", "contrast", "band"):
            keys = sorted(k for k, f in findings.items() if f[0] == kind)
            if keys:
                failed.append(f"  {kind}:")
                failed += [f"    {key} on {len(findings[key][1])}/{len(read)} builds ({'all' if len(findings[key][1]) == len(read) else where(findings[key][1])}): "
                           f"{findings[key][2].split(': ', 1)[-1][:160]}" for key in keys]
        statements = total - len(findings)
        ran = {day: builds[(day, 1)]["goldens"] for day in (NOMINAL, TUESDAY) if "goldens" in builds.get((day, 1), {})}
        golden = min((g[0] for g in ran.values()), default=0) if len(ran) == 2 else 0
        count = max((g[1] for g in ran.values()), default=0)
        for gid in sorted({g for r in ran.values() for g in r[2]}):
            failed.append(f"  golden {gid}: " + "; ".join(f"{day[5:]} {r[2][gid]}" for day, r in ran.items() if gid in r[2]))
        nominal = builds.get((NOMINAL, 1), {})
        if "bands" in nominal:
            bands = {k: v | described[k] for k, v in nominal["bands"].items()}
            manifest = {"cfg": cfg, "T": f"{nominal['T']:%Y-%m-%d %H:%M}", "seed": 1, "bands": bands}
            path = inputs.SEED / f"manifest.{cfg}.json"
            if args.write:  # one line a band
                path.write_text(json.dumps({k: v for k, v in manifest.items() if k != "bands"})[:-1] + ', "bands": {\n' +
                                ",\n".join(f" {json.dumps(k)}: {json.dumps(v)}" for k, v in manifest["bands"].items()) + "\n}}\n", encoding="utf-8")
            elif not path.exists() or json.loads(path.read_text(encoding="utf-8"))["bands"] != manifest["bands"]:
                old = json.loads(path.read_text(encoding="utf-8"))["bands"] if path.exists() else {}
                moved = sorted(k for k in old.keys() | manifest["bands"].keys() if old.get(k) != manifest["bands"].get(k))
                failed.append(f"  manifest.{cfg}.json differs from the build in " + ", ".join(moved[:8]) + (f" and {len(moved) - 8} more" if len(moved) > 8 else ""))
        if NOMINAL in ran:
            differs = compare(inputs.SEED / "goldens" / f"answers.{cfg}.txt", ran[NOMINAL][3], args.write)
            if differs:
                failed.append(f"  {differs}")
        hashes = nominal.get("hashes"), again.get("hashes")
        repeat = "identical" if None not in hashes and hashes[0] == hashes[1] else "different"
        if repeat == "different" and None not in hashes:
            failed.append("  repeat differs in " + ", ".join(sorted(t for t in hashes[0].keys() | hashes[1].keys() if hashes[0].get(t) != hashes[1].get(t))))
        if head.endswith("-dirty") or head == "nohead":
            failed.append(f"  head {head}: the tree is not a commit")
        failed += gate0_failed
        ok = not failed and days == len(DAYS) and seeds == len(SEEDS) and len(read) == len(builds) and statements == total > 0 and golden == count > 0 and repeat == "identical"
        passed += ok
        print(f"SEED GATE1 v1 {head} {cfg} {'WROTE' if args.write else 'PASS' if ok else 'FAIL'} statements={statements}/{total} goldens={golden}/{count} "
              f"days={days}/{len(DAYS)} fell_back={len(fell_back)} farthest={max(fell_back.values(), default=0)}d seeds={seeds} repeat={repeat} seconds={seconds}")
        for line in failed:
            print(line)
    return 0 if passed == 2 and not args.write else 1


if __name__ == "__main__":
    sys.exit(main())
