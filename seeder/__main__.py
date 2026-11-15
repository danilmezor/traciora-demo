"""python -m seeder demo [--cfg en|ru] [--client-id ID] [--at 'YYYY-MM-DD HH:MM'] [--replace]: every step in order.
python -m seeder reset --cfg en|ru [--client-id ID]: every step's own rows emptied, the last step first.
python -m seeder <step> --cfg en|ru [--client-id ID] [--replace]: one step; tenant and erp also take --at, erp --seed N.
python -m seeder clock --cfg en|ru --at 'YYYY-MM-DD HH:MM' [--size full|small]: the psql variables of erp/checks.sql.
Every command but clock takes --dsn, the shop database (default: seeder.manifest.shop_dsn). seeder/README.md has the
step contract."""
import argparse
import datetime as dt
import importlib
import json
import os
import sys
import time
from zoneinfo import ZoneInfo

from seeder import clock, inputs, manifest

STEPS = {"erp": "seeder.erp", "tenant": "seeder.tenant", "people": "seeder.core.people", "calls": "seeder.core.calls",
         "chats": "seeder.chats", "workday": "seeder.core.workday", "assistant": "seeder.assistant"}
BEFORE_ERP = ("tenant", "erp")  # the steps that may run before a manifest exists: they take --at. In a demo run the
# tenant step follows erp, so the source it declares names a database that is built.


def find(name):
    """The step's module, or None while its file does not exist; an import that fails inside an existing step raises."""
    path = STEPS[name]
    try:
        return importlib.import_module(path)
    except ModuleNotFoundError as problem:
        if problem.name and (path == problem.name or path.startswith(problem.name + ".")):
            return None
        raise


def instant(text):
    return dt.datetime.strptime(text, manifest.FORMAT)


def main():
    parser = argparse.ArgumentParser(prog="python -m seeder")
    commands = parser.add_subparsers(dest="command", required=True)
    clock_cmd = commands.add_parser("clock", help="print the psql variables erp/checks.sql reads, one name=value per line")
    clock_cmd.add_argument("--cfg", choices=("en", "ru"), required=True)
    clock_cmd.add_argument("--at", required=True, type=instant, help="the build instant on the home clock")
    clock_cmd.add_argument("--size", choices=("full", "small"), default="full")
    subs = {"demo": commands.add_parser("demo", help="run every step in order"), "reset": commands.add_parser("reset", help="empty every step's rows")}
    subs |= {name: commands.add_parser(name, help=f"run the step {name}") for name in STEPS}
    for name, sub in subs.items():
        sub.add_argument("--cfg", choices=("en", "ru"), required=name != "demo", default="en")
        sub.add_argument("--client-id", default="demo")
        sub.add_argument("--dsn", help="the shop database (default: SEED_SHOP_DSN, else the product's server, database seed_shop_<client id>)")
        if name != "reset":
            sub.add_argument("--replace", action="store_true", help="empty the step's own rows first")
        if name in ("demo",) + BEFORE_ERP:
            sub.add_argument("--at", type=instant, help="the build instant on the home clock (default: now)")
    subs["erp"].add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    if args.command == "clock":
        try:
            a = clock.anchors(args.cfg, args.at)
        except ValueError as e:
            sys.exit(str(e))
        print(f"cfg={args.cfg}\nsize={args.size}\nT={a['T']:%Y-%m-%d %H:%M}")
        for name in ("G", "P", "bought", "s2_start", "fired", "rule_on", "leave_from", "leave_to", "pub_week"):
            print(f"{name}={a[name]}")
        if a["at"] != args.at:  # the clock fell back to an earlier day
            print(f"asked={args.at:%Y-%m-%d %H:%M}")
        return 0

    cfg, client_id = args.cfg, args.client_id
    if args.dsn:
        os.environ["SEED_SHOP_DSN"] = args.dsn
    if args.command != "reset":
        at = getattr(args, "at", None)
        if at is None and args.command in ("demo",) + BEFORE_ERP:
            at = dt.datetime.now(ZoneInfo(inputs.value("geo.home_zone", cfg))).replace(tzinfo=None, second=0, microsecond=0)
        elif at is None:  # a step after erp runs at the instant the shop database was built at
            built = manifest.read(manifest.shop_dsn(client_id))
            if not built:
                sys.exit("the shop database has no seed.manifest: run the step erp first")
            at = instant(built["asked"])
        try:
            clock.anchors(cfg, at)
        except ValueError as e:
            sys.exit(str(e))
        os.environ["SEED_AT"] = f"{at:{manifest.FORMAT}}"

    started = time.monotonic()
    names = list(STEPS) if args.command in ("demo", "reset") else [args.command]
    steps, absent = {}, []
    for name in reversed(names) if args.command == "reset" else names:
        module, began = find(name), time.monotonic()
        if module is None:
            absent.append(name)
            print(f"SEED {name} {cfg} absent")
        elif args.command == "reset":
            module.reset(cfg, client_id)
            print(f"SEED {name} {cfg} reset seconds={time.monotonic() - began:.1f}")
        else:
            steps[name] = module.step(cfg, client_id, args.replace, **({"seed": args.seed} if args.command == "erp" else {}))
            print(f"SEED {name} {cfg} rows={steps[name]} seconds={time.monotonic() - began:.1f}")
    if args.command == "reset":
        return 0
    if args.command != "demo":
        return 1 if absent else 0

    built = manifest.read(manifest.shop_dsn(client_id))
    status = "PARTIAL" if absent else "PASS"
    print(f"SEED DEMO {built['seed']} {(built['seeder_commit'] or 'nohead')[:7]} {cfg} {status} steps={len(steps)}/{len(STEPS)}" +
          (f" absent={','.join(absent)}" if absent else "") + f" T={built['T']} seconds={time.monotonic() - started:.1f}")
    root = manifest.runtime_root()
    if root:
        (root / "operator").mkdir(parents=True, exist_ok=True)
        record = {k: built[k] for k in manifest.BUILD} | {"result": status, "steps": {name: steps.get(name) for name in STEPS}}
        (root / "operator" / "demo-seed.json").write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 1 if absent else 0


if __name__ == "__main__":
    sys.exit(main())
