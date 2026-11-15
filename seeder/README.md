# seeder

Builds a Traciora demo from a seed version: the shop-system database first, then one step per store of the product,
in the order erp, tenant, people, calls, chats, workday, assistant. The entry point is `python -m seeder`.

## Where it runs

- **On a dev install of the product.** `traciora setup` and `traciora start --rebuild-demo` run `python -m seeder
  tenant`, `demo` and, on a rebuild, `reset`, with this checkout on `PYTHONPATH`. The product finds it as
  `traciora-demo` beside its own checkout, or at `TRACIORA_DEMO_SEED`. Gate 2 runs here.
- **On a build box, for the shop database alone, the checks and Gate 1.** `seeder/remote.sh <command>` copies this
  checkout to `~/seed-run/<folder name>` on the ssh host `SEED_HOST` (without `.git`) and runs the command in the copy
  with `PYTHONHASHSEED=0` and the box's Python. A build takes about 30 s there and the checks 5 s.

Below, `<product>` is the product's checkout and `SEED_HOST` is exported.

The build box, once: a Python 3.11 with the driver, the seed's own Postgres and a shim that lets the seeder's
`docker exec -i traciora-test-pg psql` reach it. The password is the one `seeder/gate1.py` connects with (`SERVER`); the server listens on the loopback address only.

```sh
ssh "$SEED_HOST" 'mkdir -p ~/seed-run/bin && cd ~/seed-run && uv venv -q --python 3.11 venv
  uv pip install -q --python venv/bin/python "psycopg[binary]==3.3.4" pytest pyyaml
  docker run -d --name seed-pg --shm-size=1g -e POSTGRES_PASSWORD=traciora -p 127.0.0.1:55934:5432 \
    pgvector/pgvector:pg15 -c fsync=off -c synchronous_commit=off -c max_connections=200
  printf "%s\n" "#!/bin/sh" "for a; do shift; [ \"\$a\" = traciora-test-pg ] && a=seed-pg; set -- \"\$@\" \"\$a\"; done" \
    "exec /usr/bin/docker \"\$@\"" > bin/docker && chmod +x bin/docker'
```

```sh
dsn=postgresql://postgres:traciora@127.0.0.1:55934
```

## Build the shop database

```sh
seeder/remote.sh python -m seeder erp --cfg en --at '2026-11-13 10:30' --dsn $dsn/seed_en --replace
```

`--at` is the build instant on the home clock (en America/New_York, ru Europe/Ulyanovsk). The step creates the
database when it is absent, loads schema `shop` and writes `seed.manifest` beside it; `--replace` drops both first.

## Steps

`python -m seeder demo [--cfg en|ru] [--client-id demo] [--at 'YYYY-MM-DD HH:MM'] [--replace]` runs the seven steps in
order; `python -m seeder <step> --cfg en|ru --client-id demo [--replace]` runs one (tenant and erp also take `--at`,
erp `--seed N`); `python -m seeder reset --cfg en|ru --client-id demo` empties every step's rows, the last step first.
Every command takes `--dsn` in place of `SEED_SHOP_DSN`. `--at` defaults to now on the home clock; a later step run
alone takes the `asked` of the manifest.

| Step | Module | Writes |
|---|---|---|
| erp | `seeder.erp` | schemas `shop` and `seed` of the shop database |
| tenant | `seeder.tenant` | the tenant folder (template, knowledge pages with dates, playbooks, ladder), settings; with a shop database also its reader login, the source `erp`, the sources' grants, the context and its notes (`v1/tenant/checks.py` proves it) |
| people | `seeder.core.people` | core people, places, sign-ins. Stable across `--replace`: a person's id, `ids.uuid("person", slot, cfg)`; the rest is found by key: a shop by its `config_key` alias, a position by name, a login by `identity.login.person_id`, an account by its username |
| calls | `seeder.core.calls` | the story calls: legs read by the product's call-log reader (provider `seed:pbx`, one read a call day, one at T), so calls, misses and follow-up come from its rules; each answered call's handler (the file's slot, by its desk extension), recording row (no audio), transcript and verdict. Stable across `--replace`: a call's id (the product's, from its first leg) |
| chats | `seeder.chats` | the story chats: inboxes, bot, labels, agents through the product; contacts, conversations, messages, taggings, resolution events into Chatwoot's tables (v4.18.0 guard); bridge threads, drafts, the day's priority thresholds and the open set in auth.db |
| workday | `seeder.core.workday` | the hand-written cards with trails, the calendar's series and entries, shift templates, cover rules and the shifts from W0 to T+14 with publishes, the clock-ins at T, the open requests, the operators' pushed lines and read marks. What lies after T is left out. It refuses to build over an earlier build (the timeline is append-only): a rebuild starts from a new core database; reset leaves the append-only timeline, publishes and punches, and the shifts that carry a punch |
| assistant | `seeder.assistant` | core `platform.memory`, `platform.proposal`; `auth.db` conversations with their chat files, `cron_prompt_jobs`, `cron_runs`, `managers.brief_seen_at`. Computed values and tables are read at each item's instant by `v1/assistant/metrics.sql`; an item that needs data this slice lacks or a definition nobody wrote is held back (`v1/assistant/answers.<cfg>.txt` shows both): no template is ever stored |

A step is a module with `step(cfg, client_id, replace) -> int` (rows written) and `reset(cfg, client_id)`. The runner
imports it by that path; while the file does not exist the step is absent. It reads:

| What | From |
|---|---|
| the shop database | `seeder.manifest.shop_dsn(client_id)`: `SEED_SHOP_DSN`, else the product's `core_db.engine.admin_dsn()` with the database `seed_shop_<client id>` |
| the build | `seeder.manifest.read(dsn)`: every key of `seed.manifest` |
| the clock | `clock.anchors(cfg, seeder.manifest.at())`: `SEED_AT`, which the runner sets for every step |
| the runtime folder | `seeder.manifest.runtime_root()`: `RUNTIME_ROOT`, else `./runtime` when it exists, else None |
| ids | `seeder.ids.uuid(kind, key, cfg)`, `seeder.ids.number(kind, key, cfg, bits=31)` |
| its content | the files under `v1/` |

It never imports `seeder.erp`. The runner prints `SEED <step> <cfg> rows=<n> seconds=<s>` (or `absent`) per step, then
`SEED DEMO v1 <head> <cfg> PASS steps=7/7 T=<T> seconds=<s>` (`PARTIAL steps=<n>/7 absent=<names>`, exit 1, while a
step is absent) and writes the manifest's build keys and each step's rows to `<runtime>/operator/demo-seed.json`.

`seed.manifest` (key, jsonb value; dates `YYYY-MM-DD`, instants `YYYY-MM-DD HH:MM`):

| Key | Holds |
|---|---|
| `seed`, `cfg`, `T`, `asked`, `zone`, `random_seed` | the build; T is earlier than `asked` when the clock fell back |
| `seeder_commit`, `product_commit` | `SEED_COMMIT` (else git's, in a git checkout) and `TRACIORA_PRODUCT_COMMIT`, else null |
| `anchors` | every named date of `clock.anchors` |
| `calls`, `conversations` | by file number: a call's `day` and `floating` days, a chat's labelled `days` and `floating` days |
| `stories` | by the build's story key (`S8`, `call.27`, `conv.19`, `dup.3.a`): `customer_id`, `phone`, `shop`, `plates`, `orders` (numbers), `appointments` (`starts_at`, `shop`) |
| `people`, `shops` | cast slot to `employee_id` (`F4`: one per season, oldest first); `main`, `east`, `west` to `location_id` |
| `bands` | the band statements of `v1/erp/checks.sql` on this build, as `v1/manifest.<cfg>.json` |

## Checks

```sh
seeder/remote.sh python -m seeder.checks --cfg en --at '2026-11-13 10:30' --db seed_en
```

Every statement of `v1/erp/checks.sql` against its `-- want:` line. `--file` runs another statements file of the same
format, `--dsn` any database in place of one in `traciora-test-pg`. A statement is `exact` (a planted fact, a count,
or an invariant `inv.*` that must read 0), `contrast` (a story's claim as an inequality) or `band` (an outcome, an average
or share over thousands of rows, inside a wide range: `band(value, lo, hi)`); the word after the key in its header
names the kind, none is exact. A statement is unread when its block holds a second header or want line (a blank line
missing), when the file's header lines outnumber the statements, or when its SELECT returns another key than its header.
The last line is `CHECKS en pass=<p>/<n> unread=<u> exact=… contrast=… band=…`.

## Gate 1

```sh
head=$(git rev-parse --short HEAD)$([ -z "$(git status --porcelain)" ] || echo -dirty)
gate0=$(<product>/.venv/bin/python v1/checks/gate.py | grep -E '^  FAIL|^SEED GATE')
seeder/remote.sh python seeder/gate1.py --head "$head" --gate0 "$gate0"
```

Per configuration it builds at 10:30 of 22 days (the nominal T Friday 2026-11-13, Tuesday 2026-11-10, the 14 days
after the nominal T and six later days), seeds 2 and 3 at the nominal T and a repeat of the nominal build under another
hash seed, six at a time, and runs the checks on every build and the shop goldens on the nominal and the Tuesday
build. A day the generator cannot place builds at an earlier instant; it counts as built, is checked at the T its
`ERP` line names, and fails when it fell back more than 7 days. It prints, per configuration:

`SEED GATE1 v1 <head> <cfg> PASS|FAIL|WROTE statements=<p>/<n> goldens=<g>/<n> days=<built>/22 fell_back=<days> farthest=<d>d seeds=<built>/3 repeat=identical|different seconds=<s>`

`statements` counts those that hold on every build, out of all in the file; under a FAIL what failed: builds, then statements by kind with the builds each fails on (`11-20`, `11-13/s2`), the
goldens, the manifest and the answer page, the repeat, Gate 0. A pass needs every build, every statement and golden,
the story keys the goldens name (`expect_keys`, `top`) at the nominal T, `v1/manifest.<cfg>.json` (the bands' values at
the nominal T, seed 1) and `v1/goldens/answers.<cfg>.txt` (every golden's rows there) equal to the build, an identical
repeat, a clean commit and Gate 0's PASS of it; Gate 0 runs on the laptop (it reads the product's repository). After a
change that moves an outcome or an answer, write both files (the line then says WROTE) and commit them with the change:

```sh
seeder/remote.sh python seeder/gate1.py --head "$head" --gate0 "$gate0" --write
rsync "$SEED_HOST":seed-run/$(basename "$PWD")/v1/manifest.\*.json v1/ && rsync "$SEED_HOST":seed-run/$(basename "$PWD")/v1/goldens/answers.\*.txt v1/goldens/
```

It drops its databases `seed_gate_<pid>_*` as it reads them, at the start also those of a gate that died before its
cleanup.

The goldens run through the product's `golden.py`, statement guard and Postgres driver. On the build box they come from a
read-only copy of the product's `traciora.data` package (it imports no other part of the product) and its two packages
beside psycopg and PyYAML; again after the product changes them:

```sh
(cd <product>/apps/backend/src && rsync -a --delete --exclude __pycache__ --include /traciora/ \
  --include /traciora/__init__.py --include '/traciora/data/***' --exclude '*' ./ "$SEED_HOST":seed-run/product/)
ssh "$SEED_HOST" 'find ~/seed-run/product -type f -exec chmod a-w {} +
  uv pip install --python ~/seed-run/venv/bin/python sqlglot==30.23.0 pymssql==2.4.2
  echo ~/seed-run/product > $(~/seed-run/venv/bin/python -c "import site; print(site.getsitepackages()[0])")/seed-product.pth'
```

## Gate 2

On a dev install of the product with the seed beside it, its API and workers stopped, its Postgres and Chatwoot up,
with the install's Python and environment from the product's folder:

```sh
PYTHONPATH=<seed> .venv/bin/python <seed>/seeder/gate2.py --head <head>
```

Per configuration it empties the install of the demo (every step's rows of either configuration, the tenant folder
parked under `runtime/legacy_root`, a new core database) and builds it with `python -m seeder demo --replace`, three
times: at the nominal T, at now on the home clock, at the nominal T again. After the first two it runs every store's
statements (`v1/erp`, `v1/core`, `v1/calls`, `v1/conversations`, `v1/workday`, `v1/assistant` `checks.sql`; `v1/tenant`,
`v1/conversations`, `v1/workday`, `v1/assistant` `checks.py`); the third must write the same rows a step and read the same statements
as the first. It prints, per configuration:

`SEED GATE2 v1 <head> <cfg> PASS|FAIL stores=<steps>/7 statements=<p>/<n> T=<nominal>|<now> repeat=same|differs seconds=<s>`

`repeat=same` compares counts and statement results, not rows: several stores take their ids from the product. The
install is left on the last configuration at the nominal T.

## Pass rate

The agent's pass rate on the shop goldens is measured by the product's own test, from the product's checkout with the
provider's key in the environment:

```sh
TRACIORA_TEST_TRACIORA_DSN=<read-only DSN> TRACIORA_TEST_CONTEXT_TRACIORA_TENANT=<tenant folder> \
TRACIORA_TEST_CONTEXT_TRACIORA_SOURCE=erp TRACIORA_TEST_CONTEXT_GOLDEN=<this checkout>/v1/goldens/shop.en.yaml \
.venv/bin/python -m pytest apps/backend/tests/llm_eval/test_context_questions.py -m llm_eval -s -k traciora
```

The DSN is a read-only login with rights on schema `shop` only, on a build at the nominal T whose database pins
`now()`: schema `seedclock` with `now()` returning T, and `ALTER DATABASE <db> SET search_path = seedclock, pg_catalog,
public`. The tenant folder is the one the tenant step wrote. The agent answers in its own words, a second call restates
the answer in the golden's columns, and the product's `compare_results` scores it. `v1/evals/pass-rate.<cfg>.json` keeps
the runs and, per failed question, why.
