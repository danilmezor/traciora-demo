"""Static checks of the ERP files of seed v1. Run: python3 validate.py (writes validate.txt, exits 0 on success).

1. schema.sql: 31 tables in schema shop; columns, types, nullability and IN-list enumerations.
2. dictionary.md: every table and column documented with the schema's type and nullability; every
   enumerated value listed in its column's row; no documented table or column the schema lacks.
3. generator-spec.md, checks.sql, context/: every table and table.column named exists; context has one
   note per table; checks.sql names only ledger keys that exist and parses (when sqlglot is installed).
No database is used.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, '..', 'ledger.json')
problems = []
lines_out = []


def say(msg):
    lines_out.append(msg)


def fail(msg):
    problems.append(msg)


# ---------- 1. schema
schema_text = open(os.path.join(HERE, 'schema.sql'), encoding='utf-8').read()
schema_text = '\n'.join(l for l in schema_text.splitlines() if not l.strip().startswith('--'))
CONSTRAINT_WORDS = ('CHECK', 'UNIQUE', 'PRIMARY', 'FOREIGN', 'CONSTRAINT', 'EXCLUDE')
tables = {}      # table -> {column: {'type': str, 'notnull': bool}}
enums = {}       # (table, column) -> [values]
for m in re.finditer(r'CREATE TABLE shop\.(\w+) \((.*?)\n\);', schema_text, re.S):
    table, body = m.group(1), m.group(2)
    cols = {}
    for raw in body.split('\n'):
        line = raw.strip().rstrip(',')
        if not line:
            continue
        first = line.split()[0]
        if first.upper() in CONSTRAINT_WORDS:
            continue
        cm = re.match(r'(\w+)\s+(integer|smallint|text|boolean|date|timestamp|numeric\(\d+,\d+\))(.*)$', line)
        if not cm:
            fail(f'schema: cannot read column line in {table}: {line}')
            continue
        name, typ, rest = cm.groups()
        cols[name] = {'type': typ, 'notnull': ('NOT NULL' in rest) or ('PRIMARY KEY' in rest)}
    tables[table] = cols
    for em in re.finditer(r'CHECK \((\w+) IN \(([^)]*)\)\)', body):
        col, vals = em.group(1), [v.strip().strip("'") for v in em.group(2).split(',')]
        if col not in cols:
            fail(f'schema: enumeration on unknown column {table}.{col}')
        enums[(table, col)] = vals
for im in re.finditer(r'CREATE (?:UNIQUE )?INDEX \w+ ON shop\.(\w+) \(([^)]*)\)', schema_text):
    t = im.group(1)
    if t not in tables:
        fail(f'schema: index on unknown table {t}')
        continue
    for c in re.findall(r'[a-z_]+', im.group(2)):
        if c not in tables[t] and c not in ('lower',):
            fail(f'schema: index on unknown column {t}.{c}')
for fk in re.finditer(r'REFERENCES shop\.(\w+)', schema_text):
    if fk.group(1) not in tables:
        fail(f'schema: reference to unknown table {fk.group(1)}')
n_cols = sum(len(c) for c in tables.values())
say(f'schema.sql: {len(tables)} tables, {n_cols} columns, {len(enums)} enumerated columns')
if len(tables) != 31:
    fail(f'schema: {len(tables)} tables, expected 31')
EXPECTED = {'location', 'employee', 'customer', 'customer_contact', 'vehicle', 'referral_source', 'service_category',
            'canned_job', 'labor_rate', 'part', 'vendor', 'appointment', 'repair_order', 'order_status_history',
            'order_job', 'order_labor', 'order_part', 'order_sublet', 'order_fee', 'inspection', 'inspection_item',
            'time_entry', 'statement', 'payment', 'cash_drawer_close', 'purchase_order', 'purchase_order_line',
            'stock_level', 'stock_movement', 'part_return', 'service_reminder'}
if set(tables) != EXPECTED:
    fail(f'schema: tables differ from design 2.2: missing {sorted(EXPECTED - set(tables))}, extra {sorted(set(tables) - EXPECTED)}')
if re.search(r'COMMENT ON', schema_text, re.I):
    fail('schema: the database must carry no comments')
if re.search(r'CREATE EXTENSION', schema_text, re.I):
    fail('schema: no extension may be used')

all_columns = {c for cols in tables.values() for c in cols}
all_enum_values = {v for vals in enums.values() for v in vals}

# ---------- 2. dictionary
dic = open(os.path.join(HERE, 'dictionary.md'), encoding='utf-8').read()
sections = re.split(r'^## ', dic, flags=re.M)
documented = {}
for sec in sections[1:]:
    head, _, body = sec.partition('\n')
    head = head.strip()
    if not re.fullmatch(r'[a-z_]+', head):
        continue
    if head not in tables:
        fail(f'dictionary: section for unknown table {head}')
        continue
    rows = {}
    for line in body.splitlines():
        rm = re.match(r'\| `(\w+)` \| ([^|]+) \| (yes|no) \| (.*)\|\s*$', line)
        if rm:
            rows[rm.group(1)] = {'type': rm.group(2).strip(), 'null': rm.group(3), 'text': rm.group(4)}
    documented[head] = rows
    if not re.search(r'\w', body.split('\n|')[0]):
        fail(f'dictionary: {head} has no paragraph before its columns')
for t, cols in tables.items():
    if t not in documented:
        fail(f'dictionary: table {t} not documented')
        continue
    rows = documented[t]
    for c, spec in cols.items():
        if c not in rows:
            fail(f'dictionary: column {t}.{c} not documented')
            continue
        if rows[c]['type'] != spec['type']:
            fail(f"dictionary: {t}.{c} type '{rows[c]['type']}' differs from schema '{spec['type']}'")
        want_null = 'no' if spec['notnull'] else 'yes'
        if rows[c]['null'] != want_null:
            fail(f"dictionary: {t}.{c} null '{rows[c]['null']}' differs from schema '{want_null}'")
        for v in enums.get((t, c), []):
            if f'`{v}`' not in rows[c]['text']:
                fail(f'dictionary: enumeration value {v} of {t}.{c} not listed')
    for c in rows:
        if c not in cols:
            fail(f'dictionary: documents {t}.{c}, which the schema lacks')
say(f'dictionary.md: {len(documented)} tables, {sum(len(r) for r in documented.values())} columns documented')

# ---------- 3a. references in markdown files
def check_md(path, label, strict_bare=False, own_table=None):
    text = open(path, encoding='utf-8').read()
    n = 0
    for tok in re.findall(r'`([^`\n]+)`', text):
        for ref in re.findall(r'\b([a-z_]+)\.([a-z_]+)\b', tok):
            t, c = ref
            if t in tables:
                n += 1
                if c not in tables[t]:
                    fail(f'{label}: {t}.{c} is not a column')
        if strict_bare and re.fullmatch(r'[a-z_]+', tok):
            if tok not in tables and tok not in all_columns and tok not in all_enum_values and tok not in ('erp', 'shop', 'true', 'false'):
                fail(f'{label}: `{tok}` is neither a table, a column nor an enumerated value')
            if own_table and tok in all_columns and tok not in tables[own_table] and tok not in tables:
                # a column of another table: allowed only when that table is named in the note
                owners = [t for t, cols in tables.items() if tok in cols]
                if not any(o in text for o in owners):
                    fail(f'{label}: `{tok}` is not a column of {own_table} nor of a table the note names')
    return n

spec_path = os.path.join(HERE, 'generator-spec.md')
n_spec = check_md(spec_path, 'generator-spec.md')
spec = open(spec_path, encoding='utf-8').read()
# a bare name in the spec is a table, a column, an enumerated value, or a field or key of the seed files
seed_names = {'main', 'east', 'west', 'en', 'ru', 'full', 'small', 'timestamp', 'kb'}
def collect(o):
    if isinstance(o, dict):
        for k, v in o.items():
            seed_names.add(k)
            collect(v)
    elif isinstance(o, list):
        for v in o:
            collect(v)
    elif isinstance(o, str) and re.fullmatch(r'[a-z_]+', o):
        seed_names.add(o)
for f in ('cast.json', 'accounts.json', 'named_customers.json', 'vendors.json', 'catalogue.json', 'parc.json', 'mix.json', 'ledger.json', 'erp/texts.json'):
    collect(json.load(open(os.path.join(HERE, '..', f), encoding='utf-8')))
for k in [r['key'] for r in json.load(open(LEDGER, encoding='utf-8'))['rows']]:
    seed_names.update(k.split('.'))
import glob
for f in glob.glob(os.path.join(HERE, '..', 'calls', '*', '*.json')):
    collect(json.load(open(f, encoding='utf-8')))
n_bare = 0
for tok in set(re.findall(r'`([a-z_]+)`', spec)):
    n_bare += 1
    if tok not in tables and tok not in all_columns and tok not in all_enum_values and tok not in seed_names:
        fail(f'generator-spec.md: `{tok}` is neither a table, a column, an enumerated value nor a seed-file name')
for h in re.findall(r'^### (.+)$', spec, re.M):
    names = [x.strip() for x in h.split(',')]
    if all(re.fullmatch(r'[a-z_]+', x) for x in names):
        for x in names:
            if x not in tables:
                fail(f'generator-spec.md: heading names unknown table {x}')
covered = set()
for h in re.findall(r'^### (.+)$', spec, re.M):
    covered.update(x.strip() for x in h.split(','))
for t in tables:
    if t not in covered:
        fail(f'generator-spec.md: table {t} has no section in part 3')
say(f'generator-spec.md: {n_spec} table.column references and {n_bare} distinct bare names checked; every table has a section')

ctx = os.path.join(HERE, 'context')
n_ctx = check_md(os.path.join(ctx, 'RULES.md'), 'context/RULES.md', strict_bare=True)
notes = {f[:-3] for f in os.listdir(os.path.join(ctx, 'tables')) if f.endswith('.md')}
if notes != set(tables):
    fail(f'context/tables: notes differ from tables: missing {sorted(set(tables) - notes)}, extra {sorted(notes - set(tables))}')
for t in sorted(notes):
    n_ctx += check_md(os.path.join(ctx, 'tables', t + '.md'), f'context/tables/{t}.md', strict_bare=True, own_table=t if t in tables else None)
say(f'context/: RULES.md and {len(notes)} table notes; {n_ctx} table.column references checked; every backticked name exists')

# ---------- 3b. checks.sql
ledger_keys = {r['key'] for r in json.load(open(LEDGER, encoding='utf-8'))['rows']}
chk = open(os.path.join(HERE, 'checks.sql'), encoding='utf-8').read()
comment_keys = re.findall(r'^-- ([\w.*]+) \| expected ', chk, re.M)
for k in comment_keys:  # an invariant (inv.*) states what cannot be in any shop's data; it reads no ledger row
    if k not in ledger_keys and not k.startswith('inv.'):
        fail(f'checks.sql: comment names unknown ledger key {k}')
for k in re.findall(r"SELECT '([\w.:]+)' AS ledger_key", chk):
    if k.split(':')[0] not in ledger_keys and not k.startswith('inv.'):
        fail(f'checks.sql: query returns unknown ledger key {k}')
body = '\n'.join(l for l in chk.splitlines() if not l.startswith('--'))
statements = [s for s in body.split(';\n') if s.strip()]
n_refs = 0
for st in statements:
    st_nostr = re.sub(r"'(?:[^']|'')*'", "''", st)
    amap = {}
    for tm in re.finditer(r'shop\.(\w+)(?:\s+(?:AS\s+)?(\w+))?', st_nostr):
        t, alias = tm.group(1), tm.group(2)
        if t not in tables:
            fail(f'checks.sql: unknown table shop.{t}')
            continue
        if alias and alias.upper() not in ('ON', 'WHERE', 'JOIN', 'LEFT', 'GROUP', 'ORDER', 'CROSS', 'AND', 'OR', 'LIMIT'):
            amap.setdefault(alias, set()).add(t)
    for a, c in re.findall(r'\b([a-z_][a-z0-9_]*)\.([a-z_][a-z0-9_]*)\b', st_nostr):
        if a in amap:
            n_refs += 1
            if not any(c in tables[t] for t in amap[a]):
                fail(f'checks.sql: {a}.{c} is not a column of {sorted(amap[a])}')
say(f'checks.sql: {len(comment_keys)} checks, {len(set(comment_keys))} distinct ledger keys, {n_refs} alias.column references checked')
try:
    import sqlglot  # optional
    sub = re.sub(r":'(\w+)'", "'2026-06-01'", body)
    bad = 0
    for st in [s for s in sub.split(';\n') if s.strip()]:
        try:
            sqlglot.parse_one(st, read='postgres')
        except Exception as e:  # noqa: BLE001
            bad += 1
            fail(f'checks.sql: does not parse: {str(e)[:120]}')
    for st in [s for s in schema_text.split(';\n') if s.strip()]:
        try:
            sqlglot.parse_one(st, read='postgres')
        except Exception as e:  # noqa: BLE001
            fail(f'schema.sql: does not parse: {str(e)[:120]}')
    say(f'sqlglot {sqlglot.__version__}: schema.sql and checks.sql parse as Postgres ({bad} errors)')
except ImportError:
    say('sqlglot not installed: parse step skipped (static checks only)')

# ---------- result
for p in problems:
    say('PROBLEM ' + p)
say('VALIDATE ' + ('PASS' if not problems else f'FAIL ({len(problems)} problems)'))
out = '\n'.join(lines_out) + '\n'
open(os.path.join(HERE, 'validate.txt'), 'w', encoding='utf-8').write(out)
sys.stdout.write(out)
sys.exit(0 if not problems else 1)
