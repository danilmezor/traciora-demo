"""The step tenant: the demo tenant arrives the way a real tenant does. Always: the tenant folder (the product's
`config/tenant-template`, the knowledge pages and playbooks of `kb/<cfg>/` with every date placeholder filled from the
build's T, and the tenant's policy documents) and the seed's settings in `runtime/config/settings.json`. With a
built shop database also: a read-only login on its schema `shop`, the source `erp` declared through the product's
`cli.sources add`, the grants of `tenant/sources.<cfg>.json` on it and on the built-in sources, the context synced
through `cli.context sync`, and the context notes of `tenant/context/` and `erp/context/` written over the synced tree.
Runs in the product's Python (the install's .venv)."""
import calendar
import datetime as dt
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

from seeder import clock, inputs, manifest
from v1.kb.kb_paths import installed_ranks, russian_links, russian_paths

KB = inputs.SEED / "kb"
DATES = inputs.load("tenant/dates.json")
SEASONS = ("winter",) * 2 + ("spring",) * 3 + ("summer",) * 3 + ("fall",) * 3 + ("winter",)
# the bar is escaped inside a table cell; a full stop after it is dropped when the written date already ends in one
PLACEHOLDER = re.compile(r"\{\{([^{}|\\]+)\\?\|(date|day|month|season)\}\}(\.?)")
WHEN = re.compile(r"@(\w+)(?:\+(\d+)(wd:(?:main|east|west)|w|mo))?|T([+-]\d+)(mo|y)")
NOTE_HEADING = "\n\n## Demo tenant, notes v1\n\n"  # tenant/context/README.md: an "extends" note goes under it
LADDER = {"access_levels.json": "access_levels", "access_limits.json": "access_limits", "tools.json": "tools_json"}
SOURCE = "erp"
OLD_SOURCE = ["demo_source.*"]  # what the product's earlier demo declared: its business records inside the core database
HEAD = re.compile(r"(?:^|\n)(?:\*\*)?$|\.\s+$")  # what precedes a date that starts a line or a sentence


def months(d, n):
    """d moved by n calendar months, the day clamped to the month's last."""
    y, m = divmod(d.year * 12 + d.month - 1 + n, 12)
    return dt.date(y, m + 1, min(d.day, calendar.monthrange(y, m + 1)[1]))


def events(a):
    """Every named event of kb/OUTLINE.md section 1 and OUTLINE-ru.md section 1, by name, from the build's anchors."""
    return {"warranty_2424": months(a["T"].date(), -26), "purchase": a["bought"], "leak_start": a["s2_start"],
            "golive": a["G"], "money_found": a["s2_found"], "f1_fired": a["fired"], "discount_rule": a["rule_on"],
            "price_rise": a["P"], "price_rise_1": a["ru_rise"], "price_rise_2": a["s2_start"], "f2_fired": a["f2_fired"],
            "newcomers": a["slot7_starts"], "diag_back": a["week_day"](-8, 0), "early_desk": a["s3_fix"],
            "supplier_due": a["supplier_due"], "note_declined": a["s4_note2_decided"], "belt_proposal": a["s12_proposal"],
            # the outline's week W-1 is two weeks before the stocktake's published week (W+1 at the nominal T)
            "stocktake_notice": a["pub_week"] - dt.timedelta(14), "stocktake": a["stocktake"]}


def fill(text, cfg, a, where):
    """The page with every `{{<when>|<format>}}` written out; a placeholder outside the grammar stops the build."""
    named, T, names = events(a), a["T"].date(), DATES[cfg]

    def written(match):
        m = WHEN.fullmatch(match[1])
        if m is None or (m[1] and m[1] not in named):
            raise ValueError(f"kb/{cfg}/{where}: no date for the placeholder {match[0]}")
        if m[4]:
            d = months(T, int(m[4]) * (12 if m[5] == "y" else 1))
        else:
            d, n, unit = named[m[1]], int(m[2] or 0), m[3]
            if unit:
                d = clock.wd(cfg, d, n) if unit.startswith("wd") else d + dt.timedelta(7 * n) if unit == "w" else months(d, n)
        season = SEASONS[d.month - 1]
        if match[2] == "season" and season not in names["seasons"]:
            raise ValueError(f"kb/{cfg}/{where}: tenant/dates.json has no {cfg} word for the season {season}")
        out = names["formats"][match[2]].format(
            day=d.day, year=d.year, month=names["months"][d.month - 1], weekday=names["weekdays"][d.weekday()],
            month_genitive=names.get("months_genitive", names["months"])[d.month - 1], season=names["seasons"].get(season))
        if HEAD.search(text[:match.start()]):
            out = out[:1].upper() + out[1:]
        return out if out.endswith(".") else out + match[3]

    out = PLACEHOLDER.sub(written, text)
    if "{{" in out:
        raise ValueError(f"kb/{cfg}/{where}: a placeholder outside the grammar")
    return out


def pages(cfg):
    """(path in the tenant folder, source file) of every page: `playbooks/` to the tenant's playbooks, the rest to
    `knowledge_base/`. A name starting with `_` is the drafts' own (history texts, binaries, reading guide)."""
    root = KB / cfg
    names = russian_paths() if cfg == "ru" else {}
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if not any(part.startswith("_") for part in rel.parts):
            installed = Path(names[rel.as_posix()]) if names else rel
            yield (installed if rel.parts[0] == "playbooks" else Path("knowledge_base") / installed), path


def runtime():
    root = manifest.runtime_root()
    if root is None:
        raise SystemExit("no runtime folder: set RUNTIME_ROOT or run from the product's checkout")
    return root.resolve()


def folder(client_id):
    """The tenant folder: `<TRACIORA_TENANT_DIR>/<client id>` as the product reads it, else `<runtime>/tenant/<client id>`."""
    root = os.environ.get("TRACIORA_TENANT_DIR")
    return (Path(root).expanduser().resolve() if root else runtime() / "tenant") / client_id


def anchors(cfg, built):
    """The clock in force: the shop database's build instant, else the runner's."""
    return clock.anchors(cfg, dt.datetime.strptime(built["asked"], manifest.FORMAT) if built else manifest.at())


def written_for(target):
    """The T the folder's pages were written for, as its provisioned marker states it; None for a marker without one."""
    ready = target / ".git" / "traciora-provisioned"
    lines = ready.read_text(encoding="utf-8").splitlines() if ready.is_file() else []
    return next((line[2:] for line in lines if line.startswith("T ")), None)


def build(cfg, client_id):
    """The shop database's manifest, {} when the database or its manifest is absent, its server cannot be reached
    (setup runs this step before any database exists) or it holds another configuration's build (a rebuild in another
    language runs this step before the erp step replaces that build)."""
    try:
        built = manifest.read(manifest.shop_dsn(client_id))
    except psycopg.OperationalError:
        return {}
    return built if built.get("cfg") == cfg else {}


def files(cfg, a):
    """Every file the seed puts in the tenant folder, by its path there."""
    out = {}
    for rel, src in pages(cfg):
        source = src.relative_to(KB / cfg).as_posix()
        text = fill(src.read_text(encoding="utf-8"), cfg, a, source)
        out[rel.as_posix()] = russian_links(source, text) if cfg == "ru" else text
    from seeder.binaries import render

    draft = (KB / cfg / "_binaries.md").read_text(encoding="utf-8")
    names = russian_paths() if cfg == "ru" else {}
    for source, content in render(cfg, fill(draft, cfg, a, "_binaries.md")).items():
        out[f"knowledge_base/{names.get(source, source)}"] = content
    ladder = inputs.load("tenant/ladder.json")
    out.update({f"documents/{name}": json.dumps(ladder[key], ensure_ascii=False, indent=2) + "\n" for name, key in LADDER.items()})
    folders = (inputs.value(key, cfg) for key in inputs.ROWS if key.startswith("kb.pages."))
    ranks = installed_ranks(cfg, folders, inputs.value("kb.file_ranks", cfg))
    out["documents/knowledge_import.json"] = json.dumps({"seen_from": ranks}, ensure_ascii=False, indent=2) + "\n"
    return out


def put(root, written):
    for rel, content in written.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))


def write_folder(target, written, T, replace):
    """A new folder from the template plus `written`, committed as the product provisions a tenant and marked ready
    with the T its pages were written for; an existing one under `replace` or when its pages were written for another
    T, its changed files committed. Files written."""
    from traciora.core.common.paths import REPO_ROOT
    from traciora.core.common.tenant.repo import BOT_AUTHOR, TenantRepo

    ready = target / ".git" / "traciora-provisioned"
    if target.exists() and not ready.exists():
        raise SystemExit(f"unfinished tenant folder at {target}; move it away or remove it, then try again")
    if target.exists() and not replace and written_for(target) == T:
        return 0
    if target.exists():
        put(target, written)
        TenantRepo(target).commit_paths(written, author=BOT_AUTHOR, message="seed: tenant files")
        ready.write_text(f"demo tenant ready\nT {T}\n", encoding="utf-8")
        return len(written)
    with tempfile.TemporaryDirectory(prefix="seed-tenant-") as staging:
        shutil.copytree(REPO_ROOT / "config/tenant-template", staging, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))
        put(Path(staging), written)
        target.mkdir(parents=True)
        TenantRepo(target).init_from_template(Path(staging))
    ready.write_text(f"demo tenant ready\nT {T}\n", encoding="utf-8")
    return len(written)


def write_settings(cfg, client_id, replace):
    """The seed's settings into the host's settings.json, as the console writes it: under `replace` every key the seed
    states, else only those the host lacks or holds empty. A feature switch (`TRACIORA_FEATURE_*`) the host already
    holds is the administrator's choice at setup and is never written over; the seed's value fills only a switch the
    host lacks. The product refusing a key or a value stops the step. The keys the seed states under `replace`
    (whatever the host held before: a repeat build counts the same), else the keys filled."""
    from traciora.core.common import host_config, launch_gate

    seed = {k: v for k, v in inputs.load(f"tenant/settings.{cfg}.json").items() if not k.startswith("_")}
    unknown = sorted(set(seed) - set(launch_gate.settings_schema()))
    problems = launch_gate.validate(seed, launch_gate._settings_schema(launch_gate.ROOT))
    if unknown or problems:
        raise SystemExit(f"the product refuses tenant/settings.{cfg}.json: undeclared {unknown}; {problems}")
    env = {"RUNTIME_ROOT": str(runtime())}
    host = host_config.read(host_config.host_dir(launch_gate.ROOT, env) / "settings.json")
    changed = {k: v for k, v in seed.items()
               if ((replace and not k.startswith("TRACIORA_FEATURE_")) or host.get(k) in (None, "")) and host.get(k) != v}
    if changed:
        host_config.write(launch_gate.ROOT, client_id, "settings.json", host | changed, env)
    return len(seed) if replace else len(changed)


def superuser(dsn):
    """The shop database as the server's superuser `postgres`: only a superuser makes roles on the stack's Postgres."""
    password = os.environ.get("TRACIORA_POSTGRES_PASSWORD")
    if not password:
        raise SystemExit("TRACIORA_POSTGRES_PASSWORD is not set: the reader login needs the server's superuser")
    return make_conninfo(dsn, user="postgres", password=password)


def reader_name(client_id):
    return f"seed_shop_reader_{client_id}"


def reader(dsn, client_id):
    """The shop database's read-only login with a fresh password: CONNECT to this database alone, USAGE and SELECT on
    schema `shop`, nothing on `seed`, every transaction read-only. Its DSN."""
    info, role, password = conninfo_to_dict(dsn), reader_name(client_id), secrets.token_urlsafe(24)
    name, database = sql.Identifier(role), sql.Identifier(info["dbname"])
    with psycopg.connect(superuser(dsn), autocommit=True) as conn:
        if conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,)).fetchone() is None:
            conn.execute(sql.SQL("CREATE ROLE {}").format(name))
        conn.execute(sql.SQL("ALTER ROLE {} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT PASSWORD {}").format(name, sql.Literal(password)))
        conn.execute(sql.SQL("ALTER ROLE {} SET default_transaction_read_only = on").format(name))
        conn.execute(sql.SQL("REVOKE CONNECT ON DATABASE {} FROM PUBLIC").format(database))
        conn.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(database, name))
        conn.execute(sql.SQL("GRANT USAGE ON SCHEMA shop TO {}").format(name))
        conn.execute(sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA shop TO {}").format(name))
    return f"postgresql://{role}:{password}@{info.get('host', 'localhost')}:{info.get('port', '5432')}/{info['dbname']}"


def product(client_id, *args, env=()):
    """A command of the product's CLI, in this interpreter, quiet unless it fails."""
    done = subprocess.run([sys.executable, "-m", *args], env=os.environ | {"CLIENT_ID": client_id, "RUNTIME_ROOT": str(runtime())} | dict(env),
                          capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"python -m {' '.join(args)} exited {done.returncode}:\n{done.stdout}{done.stderr}")


def declare(cfg, client_id, dsn):
    """The source `erp` through `cli.sources add` (its DSN to the vault entry source/erp), then the grants of
    tenant/sources.<cfg>.json on it and on the built-in sources, saved as the console saves them: `add` keeps the
    access the console set, so the grants have no command. The earlier demo's source is removed through `cli.sources
    remove`, so no rank reads the previous business beside this one. The name the conversations source is declared
    under."""
    from traciora.core.tools.data.adapters import save_sources_document, sources_document, sources_lock

    seed = {s["name"]: s for s in inputs.load(f"tenant/sources.{cfg}.json")["sources"]}
    product(client_id, "traciora.cli.sources", "add", "--name", SOURCE, "--kind", seed[SOURCE]["kind"], "--include", *seed[SOURCE]["include"],
            env={"TRACIORA_SOURCE_DSN": reader(dsn, client_id)})
    for old in [e["name"] for e in sources_document()["sources"] if e.get("include") == OLD_SOURCE]:
        product(client_id, "traciora.cli.sources", "remove", "--name", old)
    with sources_lock():
        document = sources_document()
        by_seed = {"chatwoot" if e.get("system") == "chatwoot" else e["name"]: e for e in document["sources"]}
        if "core" not in by_seed:
            raise SystemExit("the source core is not declared: the product's built-in sources come before this step")
        for name, entry in by_seed.items():
            if name in seed:
                entry["access"] = seed[name]["access"]
                entry.update({"applied_defaults": seed[name]["applied_defaults"]} if "applied_defaults" in seed[name] else {})
        save_sources_document(document)
    return by_seed["chatwoot"]["name"] if "chatwoot" in by_seed else None


def notes(conversations):
    """Every context note by its path in the tenant folder: `erp/context/` as the source's rules and table notes
    (manual, as the product's own notes are), `tenant/context/` over the built-in sources' shipped notes; the
    conversations notes only while that source is declared."""
    from traciora.core.common.paths import REPO_ROOT
    from traciora.data.context.tree import MANUAL_MARKER

    erp = inputs.SEED / "erp/context"
    out = {f"context/sources/{SOURCE}/RULES.md": MANUAL_MARKER + "\n\n" + (erp / "RULES.md").read_text(encoding="utf-8")}
    out |= {f"context/sources/{SOURCE}/shop/{p.stem}/annotations.md": MANUAL_MARKER + "\n\n" + p.read_text(encoding="utf-8")
            for p in sorted((erp / "tables").glob("*.md"))}
    for here, source, shipped in (("core", "core", "traciora"), ("conversations", conversations, "chatwoot")):
        if source is None:
            continue
        root = inputs.SEED / "tenant/context" / here
        for path in sorted(root.rglob("*.md")):
            rel, text = path.relative_to(root).as_posix(), path.read_text(encoding="utf-8")
            if text.startswith("<!-- extends"):  # its first line names the shipped file it is appended to
                text = (REPO_ROOT / "config/sources" / shipped / rel).read_text(encoding="utf-8").rstrip("\n") + NOTE_HEADING + text.split("\n", 1)[1].lstrip("\n")
            out[f"context/sources/{source}/{rel}"] = text
    return out


def step(cfg, client_id, replace):
    built = build(cfg, client_id)
    a = anchors(cfg, built)
    target = folder(client_id)
    written = write_folder(target, files(cfg, a), f"{a['T']:{manifest.FORMAT}}", replace) + write_settings(cfg, client_id, replace)
    if not built:
        return written
    from traciora.core.core_db.bootstrap import seed_rows, write_policy_seeds
    from traciora.core.core_db.engine import connect, tenant_dsn

    # The core database can be prepared before the tenant folder is written.
    with connect(tenant_dsn(client_id)) as conn:
        write_policy_seeds(conn, seed_rows(client_id))

    conversations = declare(cfg, client_id, manifest.shop_dsn(client_id))
    for name in (SOURCE, "core", conversations):
        if name:  # each source's first sync copies the product's shipped notes, which the seed's notes then extend
            product(client_id, "traciora.cli.context", "sync", "--source", name)
    from traciora.core.common.tenant.repo import BOT_AUTHOR, TenantRepo

    over = notes(conversations)
    put(target, over)
    TenantRepo(target).commit_paths(over, author=BOT_AUTHOR, message="seed: context notes")
    return written + 1 + len(over)


def reset(cfg, client_id):
    """The source `erp` removed with its vault entry, and its login dropped; the tenant folder stays (the operator
    parks it)."""
    from traciora.core.tools.data.adapters import sources_document

    if any(e["name"] == SOURCE for e in sources_document()["sources"]):
        product(client_id, "traciora.cli.sources", "remove", "--name", SOURCE)
    dsn = manifest.shop_dsn(client_id)
    try:
        conn = psycopg.connect(superuser(dsn), autocommit=True)
    except psycopg.OperationalError:  # no shop database, so no grant of the login is left in one
        conn = psycopg.connect(make_conninfo(superuser(dsn), dbname="postgres"), autocommit=True)
    with conn:
        if conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (reader_name(client_id),)).fetchone():
            conn.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(reader_name(client_id))))
            conn.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(reader_name(client_id))))
