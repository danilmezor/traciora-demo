"""python seeder/gate2.py --head HEAD [--cfg en ru]: Gate 2, every store of the demo built on a dev install.

Run it with the install's Python in the install's environment, from the product's folder, with the install's API and
workers stopped and its Postgres and Chatwoot up (README, "Gate 2"). Per configuration it builds the demo twice from an
empty install, at the nominal T and at now on the home clock: the stores' own rows removed, the tenant folder parked
under runtime/legacy_root, the core database dropped and initialised, then `python -m seeder demo --replace`. After each
build every store's statements run. A third build, at the nominal T again, must write the same rows a step and read
the same statements. One line a configuration:

    SEED GATE2 v1 <head> <cfg> PASS stores=7/7 statements=<p>/<n> T=<nominal>|<now> repeat=same seconds=<s>

`repeat=same` compares the steps' row counts and the statements' results, not the rows themselves: several stores take
their ids from the product."""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import time
import zoneinfo
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SEED))

from seeder import chats, inputs, manifest  # noqa: E402
from seeder.__main__ import STEPS  # noqa: E402

NOMINAL = "2026-11-13 10:30"
SQL = (("erp", "v1/erp/checks.sql", "shop"), ("people", "v1/core/checks.sql", "core"), ("calls", "v1/calls/checks.sql", "core"),
       ("chats", "v1/conversations/checks.sql", "chatwoot"), ("workday", "v1/workday/checks.sql", "core"),
       ("assistant", "v1/assistant/checks.sql", "core"))
SCRIPTS = (("tenant", "v1/tenant/checks.py"), ("chats", "v1/conversations/checks.py"), ("workday", "v1/workday/checks.py"),
           ("assistant", "v1/assistant/checks.py"))


def python(*args, quiet=False):
    done = subprocess.run([sys.executable, *args], env=os.environ | {"PYTHONPATH": str(SEED)}, capture_output=True, text=True)
    if done.returncode and not quiet:
        print(done.stdout[-2000:] + done.stderr[-2000:], file=sys.stderr)
    return done


def empty(client_id):
    """The install with no demo in it: each step's rows of either configuration gone, the tenant folder parked, a new
    core database, the accounts' store parked with the tenant folder."""
    from traciora.core.core_db.engine import tenant_database_name
    from traciora.core.core_db.schema import drop_database

    for cfg in ("en", "ru"):
        python("-m", "seeder", "reset", "--cfg", cfg, "--client-id", client_id, quiet=True)
    root = manifest.runtime_root()
    parked = root / "legacy_root" / f"{dt.datetime.now():%Y%m%d_%H%M%S}"
    parked.mkdir(parents=True)
    folder = Path(os.environ.get("TRACIORA_TENANT_DIR") or root / "tenant") / client_id
    if folder.exists():
        shutil.move(str(folder), str(parked / f"tenant-{client_id}"))
    # the accounts and what the running product wrote beside them, as the operator's rebuild parks them; the runtime
    # vault (console-entered keys, source secrets) stays
    shutil.move(str(root / "chat_memory"), str(parked / "chat_memory"))
    (root / "chat_memory").mkdir()
    for vault in (parked / "chat_memory").glob("connectors.db*"):
        shutil.copy2(vault, root / "chat_memory" / vault.name)
    drop_database(tenant_database_name(client_id))
    for module in ("traciora.cli.core_db", "traciora.cli.sources"):
        if python("-m", module, "init" if module.endswith("core_db") else "builtin").returncode:
            raise SystemExit(f"{module} failed on the empty install")


def build(cfg, client_id, at):
    """One demo build and its statements: (failures, rows a step, statements read)."""
    from traciora.core.core_db.engine import tenant_dsn

    failed, read = [], {}
    done = python("-m", "seeder", "demo", "--cfg", cfg, "--client-id", client_id, "--replace", "--at", at)
    rows = dict(re.findall(rf"^SEED (\w+) {cfg} rows=(\d+)", done.stdout, re.M))
    if not re.search(rf"^SEED DEMO \S+ \S+ {cfg} PASS steps={len(STEPS)}/{len(STEPS)} ", done.stdout, re.M):
        return [f"demo at {at}: " + (done.stdout.strip().splitlines() or ["no output"])[-1]], rows, read
    dsn = {"shop": manifest.shop_dsn(client_id), "core": tenant_dsn(client_id), "chatwoot": chats.chatwoot_dsn()}
    for store, path, where in SQL:
        out = python("-m", "seeder.checks", "--cfg", cfg, "--at", at, "--file", str(SEED / path), "--dsn", dsn[where]).stdout
        line = re.search(rf"^CHECKS {cfg} pass=(\d+)/(\d+) unread=(\d+)", out, re.M)
        read[path] = (int(line[1]), int(line[2])) if line else (0, 1)
        if not line or line[1] != line[2] or line[3] != "0":
            failed += [f"{store} at {at}: " + x for x in re.findall(r"^  FAIL.*", out, re.M)[:8] or [out.strip()[-300:] or "no output"]]
    for store, path in SCRIPTS:
        out = python(str(SEED / path), "--cfg", cfg, "--client-id", client_id).stdout.strip().splitlines()
        read[path] = (1, 1) if out and " PASS" in out[-1] else (0, 1)
        if read[path] == (0, 1):
            failed.append(f"{store} at {at}: " + (out[-1] if out else "no output")[:300])
    return failed, rows, read


def main():
    parser = argparse.ArgumentParser(prog="python seeder/gate2.py")
    parser.add_argument("--head", required=True)
    parser.add_argument("--cfg", nargs="+", choices=("en", "ru"), default=("en", "ru"))
    parser.add_argument("--client-id", default="demo")
    args = parser.parse_args()
    ok = True
    for cfg in args.cfg:
        started = time.monotonic()
        now = f"{dt.datetime.now(zoneinfo.ZoneInfo(inputs.value('geo.home_zone', cfg))):%Y-%m-%d %H:%M}"
        failed, seen = [], []
        for at in (NOMINAL, now, NOMINAL):  # the last build stays on the install: the nominal T
            empty(args.client_id)
            bad, rows, read = build(cfg, args.client_id, at)
            failed += bad
            seen.append((rows, read))
        if seen[0] != seen[2]:
            failed.append("repeat: " + ", ".join(sorted(k for k in seen[0][0].keys() | seen[2][0].keys() if seen[0][0].get(k) != seen[2][0].get(k)) +
                                                 sorted(k for k in seen[0][1].keys() | seen[2][1].keys() if seen[0][1].get(k) != seen[2][1].get(k))))
        passed, total = (sum(v[i] for _, read in seen[:2] for v in read.values()) for i in (0, 1))
        for line in failed:
            print("  FAIL " + line)
        ok &= not failed
        print(f"SEED GATE2 {inputs.SEED.name} {args.head} {cfg} {'FAIL' if failed else 'PASS'} stores={len(seen[0][0])}/{len(STEPS)} "
              f"statements={passed}/{total} T={NOMINAL}|{now} repeat={'differs' if seen[0] != seen[2] else 'same'} seconds={time.monotonic() - started:.0f}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
