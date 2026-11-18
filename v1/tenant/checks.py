"""What proves the tenant step on an install. Run with the install's Python from its checkout, the install's environment
loaded (as the step runs):
    python <seed>/v1/tenant/checks.py --cfg en|ru [--client-id demo]
Checks: validate.py passes against the installed product; the tenant folder is provisioned for the T in force (the
shop database's, else the one its marker states) and holds every page of kb/<cfg>/ as the step renders it for that T,
no placeholder left anywhere in it, and the ladder documents; settings.json holds every value of settings.<cfg>.json but the feature
switches the administrator chose at setup.
With a built shop database also: the board states, task templates and call verdicts use the install's policy documents.
The sources erp, core and conversations hold the grants of sources.<cfg>.json and no
earlier demo source is declared; `python -m traciora.cli.sources check --name erp` passes; the source's login reads
every table of erp/schema.sql, nothing of schema seed, read-only; the context holds every one of those tables and every
note as the step writes it. One line out: TENANT <cfg> PASS ... or FAIL with the reasons; exit 0 or 1."""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import psycopg

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))  # the seed checkout, for seeder

from seeder import clock, inputs, manifest, tenant  # noqa: E402


def main():
    parser = argparse.ArgumentParser(prog="v1/tenant/checks.py")
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--client-id", default="demo")
    args = parser.parse_args()
    cfg, client_id = args.cfg, args.client_id
    from traciora.core.common.paths import REPO_ROOT

    failed, said = [], {}
    done = subprocess.run([sys.executable, str(HERE / "validate.py")], env=os.environ | {"TRACIORA_PRODUCT": str(REPO_ROOT)},
                          capture_output=True, text=True)
    lines = done.stdout.splitlines()
    if done.returncode:
        failed.append("validate.py: " + "; ".join([x for x in lines if x.startswith("FAIL")][:3] or lines[-1:] or [done.stderr.strip()[-200:]]))

    target, built = tenant.folder(client_id), tenant.build(cfg, client_id)
    stated = tenant.written_for(target)
    if stated is None:
        return report(cfg, said, failed + [f"{target} is not a provisioned tenant folder with the T of its pages"])
    a = tenant.anchors(cfg, built) if built else clock.anchors(cfg, dt.datetime.strptime(stated, manifest.FORMAT))
    if stated != f"{a['T']:{manifest.FORMAT}}":
        failed.append(f"the pages were written for T {stated}, the shop database is at T {a['T']:{manifest.FORMAT}}")
    wanted = tenant.files(cfg, a)
    differ = [rel for rel, text in wanted.items() if not (target / rel).is_file() or (target / rel).read_text(encoding="utf-8") != text]
    left = [p.relative_to(target).as_posix() for p in target.rglob("*.md") if ".git" not in p.parts and "{{" in p.read_text(encoding="utf-8")]
    failed += [f"files not as the step renders them for T {stated}: {differ[:3]} of {len(differ)}"] * bool(differ)
    failed += [f"placeholders left in {left[:3]} of {len(left)}"] * bool(left)
    said |= {"T": stated.replace(" ", "T"), "pages": sum(1 for rel in wanted if not rel.startswith("documents/") and rel not in differ)}

    seed = {k: v for k, v in inputs.load(f"tenant/settings.{cfg}.json").items() if not k.startswith("_")}
    path = tenant.runtime() / "config" / "settings.json"
    host = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    # a feature switch is the administrator's choice at setup: the seed fills it only where the host held none
    differ = sorted(k for k, v in seed.items() if host.get(k) != v and not (k.startswith("TRACIORA_FEATURE_") and k in host))
    failed += [f"settings.json differs from settings.{cfg}.json on {differ[:5]} of {len(differ)}"] * bool(differ)
    said["settings"] = f"{len(seed) - len(differ)}/{len(seed)}"

    if not built:
        said["source"] = "absent"
    else:
        failed += source(cfg, client_id, target, said)
        failed += workspace_policy(cfg, client_id)
    return report(cfg, said, failed)


def report(cfg, said, failed):
    line = " ".join(f"{k}={v}" for k, v in said.items())
    print(f"TENANT {cfg} PASS {line}" if not failed else f"TENANT {cfg} FAIL {line}\n" + "\n".join(f"  FAIL {x}" for x in failed))
    return 1 if failed else 0


def workspace_policy(cfg, client_id):
    """Read the policy used by the demo's work items and calls from the core database."""
    from seeder.core.calls import PROVIDER
    from traciora.core.common import settings
    from traciora.core.core_db.bootstrap import seed_rows
    from traciora.core.core_db.engine import connect, tenant_dsn
    from traciora.core.phonecalls import scorecard

    policy = seed_rows(client_id)
    rubric = scorecard.parse(settings.document("PHONECALLS_SCORECARD", client_id=client_id))
    wanted_states = sorted((row["state_group"], row["name"], row["sequence"], row["colour"], row["is_default"])
                           for row in policy.work_states)
    text_fields = ("title_template", "description_template", "reason_template")
    wanted_templates = sorted((row["pack"], row["name"], *(row[field] for field in text_fields), row["default_priority"])
                              for row in policy.work_item_templates)
    with connect(tenant_dsn(client_id)) as conn:
        held_states = sorted(conn.execute(
            "select state_group, name, sequence, colour, is_default from work.work_state where active").fetchall())
        held_templates = sorted(conn.execute(
            "select pack, name, title_template, description_template, reason_template, default_priority"
            " from work.work_item_template where active").fetchall())
        held_rubrics = conn.execute(
            "select distinct a.result_public->>'scorecard', a.result_public->>'weights'"
            " from interactions.interaction_analysis a where a.kind = 'scorecard' and a.is_current"
            " and exists (select 1 from interactions.call_leg l where l.interaction_id = a.interaction_id and l.provider = %s)",
            (PROVIDER,)).fetchall()
    failed = []
    if held_states != wanted_states:
        failed.append(f"board states do not match the install's document: {held_states}")
    if held_templates != wanted_templates:
        failed.append("task templates do not match the install's document")
    if held_rubrics and held_rubrics != [(rubric.version, rubric.weights_version)]:
        failed.append(f"call verdicts do not use the install's scorecard: {held_rubrics}")
    if cfg == "ru":
        visible = [row["name"] for row in policy.work_states]
        visible += [row[field] for row in policy.work_item_templates for field in text_fields if row[field]]
        visible += [row.name for row in (*rubric.checks, *rubric.auto_fails)]
        if not all(re.search(r"[А-Яа-я]", text) for text in visible):
            failed.append("the board, task templates or call scorecard have an untranslated label")
    return failed


def source(cfg, client_id, target, said):
    """The declared sources, the login and the context; the reasons it fails."""
    from traciora.core.common.runtime_vault import source_secret
    from traciora.core.tools.data.adapters import sources_document

    failed = []
    seed = {s["name"]: s for s in inputs.load(f"tenant/sources.{cfg}.json")["sources"]}
    declared = {"chatwoot" if e.get("system") == "chatwoot" else e["name"]: e for e in sources_document()["sources"]}
    failed += [f"source {name} is not declared" for name in seed if name not in declared]
    failed += [f"source {name} lacks the grants of sources.{cfg}.json" for name in seed if name in declared and declared[name].get("access") != seed[name]["access"]]
    failed += [f"the earlier demo's source {e['name']} is declared" for e in declared.values() if e.get("include") == tenant.OLD_SOURCE]
    if declared.get(tenant.SOURCE, {}).get("include") != seed[tenant.SOURCE]["include"]:
        failed.append(f"source {tenant.SOURCE} does not include {seed[tenant.SOURCE]['include']}")
    done = subprocess.run([sys.executable, "-m", "traciora.cli.sources", "check", "--name", tenant.SOURCE],
                          env=os.environ | {"CLIENT_ID": client_id}, capture_output=True, text=True)
    if done.returncode:
        failed.append(f"sources check --name {tenant.SOURCE} exited {done.returncode}: {done.stdout.strip()[-300:]}")
    dsn = source_secret(f"source/{tenant.SOURCE}/dsn")
    if not dsn:
        return failed + [f"no DSN in the vault entry source/{tenant.SOURCE}"]
    tables = re.findall(r"^CREATE TABLE shop\.(\w+)", (inputs.SEED / "erp/schema.sql").read_text(encoding="utf-8"), re.M)
    with psycopg.connect(dsn) as conn:
        seeds, readonly = conn.execute("SELECT has_schema_privilege('seed', 'USAGE'), current_setting('default_transaction_read_only')").fetchone()
        unread = [t for t in tables if not conn.execute("SELECT to_regclass(%s) IS NOT NULL AND has_table_privilege(%s, 'SELECT')",
                                                         (f"shop.{t}", f"shop.{t}")).fetchone()[0]]
    failed += [f"the login cannot read {unread[:3]} of {len(unread)} tables of erp/schema.sql"] * bool(unread)
    failed += ["the login reads schema seed"] * seeds + ["the login may write"] * (readonly != "on")
    unsynced = [t for t in tables if not (target / "context/sources" / tenant.SOURCE / "shop" / t / "columns.md").is_file()]
    failed += [f"context lacks shop tables {unsynced[:3]} of {len(unsynced)}"] * bool(unsynced)
    over = tenant.notes(declared["chatwoot"]["name"] if "chatwoot" in declared else None)
    differ = [rel for rel, text in over.items() if not (target / rel).is_file() or (target / rel).read_text(encoding="utf-8") != text]
    failed += [f"notes not as the step writes them: {differ[:3]} of {len(differ)}"] * bool(differ)
    said |= {"source": tenant.SOURCE, "tables": f"{len(tables) - len(unsynced)}/{len(tables)}", "notes": f"{len(over) - len(differ)}/{len(over)}"}
    return failed


if __name__ == "__main__":
    sys.exit(main())
