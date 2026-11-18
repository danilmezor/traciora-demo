"""D2 and D3 of the seed gate. gate.py imports this file from its temporary copy of v1 and calls run(root).

D2: on a scratch database loaded from erp/schema.sql in the container traciora-test-pg, every statement of
erp/checks.sql (once per configuration, its psql variables set to the header's example values) and every SQL of
goldens/shop.*.yaml plans under EXPLAIN. EXPLAIN executes nothing. The scratch database is always dropped.
D3: every fact of goldens/kb.*.yaml is printed on the page it names, read again here from kb/<lang>/, and every
golden's `username` is its asker's sign-in name in cast.json (none for a customer).
"""
import json
import os
import re
import shlex
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "kb"))
from kb_paths import russian_sources

CONTAINER = "traciora-test-pg"
LANGS = ("en", "ru")
PSQL = ["docker", "exec", "-i", CONTAINER, "psql", "-X", "-q", "-U", "postgres", "-v", "ON_ERROR_STOP=1"]


def spaces(text):
    return re.sub(r"\s+", " ", text)


def page(root, lang, path):
    """The page's printed text: the file, or a binary document's draft in _binaries.md; placeholders dropped."""
    if lang == "ru":
        path = russian_sources().get(path)
        if path is None:
            return None
    file = os.path.join(root, "kb", lang, path)
    if os.path.isfile(file):
        text = open(file, encoding="utf-8").read()
    else:
        drafts = open(os.path.join(root, "kb", lang, "_binaries.md"), encoding="utf-8").read()
        found = re.search(r"^## \d+\. `%s`\n(.*?)(?=^## \d+\. `|\Z)" % re.escape(path), drafts, re.S | re.M)
        if not found:
            return None
        text = found.group(1)
    return spaces(re.sub(r"\{\{[^}]*\}\}", " ", text))


def on_page(value, text, lang):
    """The value stands on the page as itself, not inside a longer number."""
    before, after = (r"(?<![\w.,])(?<!\d )", r"(?!\w|,\d| \d{3}(?!\d))") if lang == "ru" else (r"(?<![\w.,])", r"(?!\w|[.,]\d)")
    return re.search(before + re.escape(spaces(str(value)).strip()) + after, text) is not None


def d3(root):
    failed, counts, ids, off = [], {}, {}, 0
    people = json.load(open(os.path.join(root, "cast.json"), encoding="utf-8"))["people"]
    for lang in LANGS:
        usernames = {p["slot"]: p[lang]["username"] for p in people}
        path = os.path.join(root, "goldens", f"kb.{lang}.yaml")
        if not os.path.exists(path):
            failed.append(f"D3 goldens/kb.{lang}.yaml is missing")
            counts[lang], ids[lang] = 0, set()
            continue
        questions = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("questions") or []
        names = [q.get("id") for q in questions]
        counts[lang], ids[lang] = len(questions), set(names)
        failed += [f"D3 kb.{lang}.yaml: id {i} appears {names.count(i)} times" for i in sorted(set(names), key=str) if names.count(i) > 1]
        if len(questions) < 30:
            failed.append(f"D3 kb.{lang}.yaml holds {len(questions)} goldens, fewer than 30")
        for q in questions:
            if not q.get("facts"):
                failed.append(f"D3 kb.{lang}.yaml {q.get('id')}: no facts")
            if q.get("username") != usernames.get(q.get("asker")):
                failed.append(f"D3 kb.{lang}.yaml {q.get('id')}: username {q.get('username')!r} is not asker {q.get('asker')}'s")
            if page(root, lang, q.get("rule") or "") is None:
                failed.append(f"D3 kb.{lang}.yaml {q.get('id')}: no source for rule {q.get('rule')}")
            for fact in q.get("facts") or []:
                text = page(root, lang, fact.get("page") or "")
                if text is None or not on_page(fact.get("value", ""), text, lang):
                    off += 1
                    failed.append(f"D3 kb.{lang}.yaml {q.get('id')}: {fact.get('value')!r} is not on {fact.get('page')}")
    for lang, other in (("en", "ru"), ("ru", "en")):
        if ids[lang] - ids[other]:
            print(f"  NOTE D3 kb goldens in {lang} only: " + ", ".join(sorted(ids[lang] - ids[other], key=str)))
    return [f"kb_goldens={counts['en']}+{counts['ru']}", "facts_on_page=" + ("all" if not off else str(off))], failed


def statements(sql):
    """The statements of a script, split at semicolons outside quotes, comments and dollar quotes."""
    out, start, i, n = [], 0, 0, len(sql)
    while i < n:
        c = sql[i]
        if sql.startswith("--", i):
            i = sql.find("\n", i)
            i = n if i < 0 else i
        elif c in "'\"":
            i = sql.find(c, i + 1)
            i = n if i < 0 else i
        elif c == "$" and re.match(r"\$\w*\$", sql[i:]):
            tag = re.match(r"\$\w*\$", sql[i:]).group(0)
            i = sql.find(tag, i + len(tag))
            i = n if i < 0 else i + len(tag) - 1
        elif c == ";":
            out.append(sql[start:i])
            start = i + 1
        i += 1
    out.append(sql[start:])
    body = [re.sub(r"^(\s*--[^\n]*\n)*\s*", "", s).strip() for s in out]
    return [s for s in body if s]


def example_variables(sql):
    """The `-v name=value` pairs of the header's Example line and the lines that continue it."""
    lines = sql.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("-- Example:"))
    words = shlex.split(lines[start].split("Example:", 1)[1])
    for line in lines[start + 1:]:
        if not re.match(r"--\s+-v ", line):
            break
        words += shlex.split(line[2:])
    return [tuple(w.split("=", 1)) for flag, w in zip(words, words[1:]) if flag == "-v"]


def plan(db, preamble, named, variables=()):
    """EXPLAIN each (name, sql); returns the failure lines. Restarts after each statement that does not plan."""
    failed, k = [], 0
    args = [a for name, value in variables for a in ("-v", f"{name}={value}")]
    while k < len(named):
        script, spans = "".join(s + ";\n" for s in preamble), []
        line = script.count("\n") + 1
        for name, sql in named[k:]:
            text = "EXPLAIN " + sql + ";\n"
            spans.append((line, line + text.count("\n") - 1))
            script += text
            line += text.count("\n")
        done = subprocess.run(PSQL + args + ["-d", db, "-f", "-"], input=script, capture_output=True, text=True)
        if done.returncode == 0:
            break
        error = re.search(r"psql:<stdin>:(\d+): (ERROR: .*)", done.stderr)
        if not error:
            failed += [f"{name}: {(done.stderr.strip().splitlines() or ['psql failed'])[0]}" for name, _ in named[k:]]
            break
        at = int(error.group(1))
        j = next((j for j, (a, b) in enumerate(spans) if a <= at <= b), None)
        if j is None:
            j = max([j for j, (a, _) in enumerate(spans) if a <= at] or [0])
        failed.append(f"{named[k + j][0]}: {spaces(error.group(2))[:200]}")
        k += j + 1
    return failed


def d2(root):
    failed, shop = [], {}
    for lang in LANGS:
        path = os.path.join(root, "goldens", f"shop.{lang}.yaml")
        if os.path.exists(path):
            shop[lang] = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("questions") or []
    missing = [f"goldens/shop.{lang}.yaml" for lang in LANGS if lang not in shop]
    if missing:
        failed.append("D2 " + " and ".join(missing) + (" is" if len(missing) == 1 else " are") + " missing")
    for lang, questions in shop.items():
        if len(questions) != 40:
            failed.append(f"D2 shop.{lang}.yaml holds {len(questions)} goldens, not 40")
    if len(shop) == 2 and {q.get("id") for q in shop["en"]} != {q.get("id") for q in shop["ru"]}:
        en, ru = ({q.get("id") for q in shop[lang]} for lang in LANGS)
        failed.append(f"D2 shop golden ids differ: en only {sorted(en - ru, key=str)}, ru only {sorted(ru - en, key=str)}")
    checks = open(os.path.join(root, "erp", "checks.sql"), encoding="utf-8").read()
    every = statements(checks)
    preamble = [s for s in every if re.match(r"(?i)SET\b", s)]
    named = [(re.search(r"'([^']+)' AS ledger_key", s).group(1) if re.search(r"'([^']+)' AS ledger_key", s) else s.splitlines()[0][:60], s)
             for s in every if s not in preamble]
    golden_sql = [(f"shop.{lang}.yaml {q.get('id')}", (q.get("sql") or "").strip().rstrip(";")) for lang in LANGS for q in shop.get(lang, [])]
    total = 2 * len(named) + len(golden_sql)
    variables = example_variables(checks)
    db = f"seed_gate_{os.getpid()}"
    not_planned = []
    try:
        made = subprocess.run(PSQL + ["-d", "postgres", "-c", f"CREATE DATABASE {db}"], capture_output=True, text=True)
        if made.returncode:
            raise RuntimeError(f"cannot create {db}: " + (made.stderr.strip().splitlines() or ["?"])[0])
        loaded = subprocess.run(PSQL + ["-d", db, "-f", "-"], input=open(os.path.join(root, "erp", "schema.sql"), encoding="utf-8").read(), capture_output=True, text=True)
        if loaded.returncode:
            raise RuntimeError("erp/schema.sql does not load: " + (loaded.stderr.strip().splitlines() or ["?"])[0])
        for cfg in LANGS:
            with_cfg = [(name, value) for name, value in variables if name != "cfg"] + [("cfg", cfg)]
            not_planned += [f"D2 checks.sql ({cfg}) {line}" for line in plan(db, preamble, named, with_cfg)]
        empty = [name for name, sql in golden_sql if not sql]
        not_planned += [f"D2 {name}: no sql" for name in empty]
        not_planned += [f"D2 {line}" for line in plan(db, ["SET search_path = shop"], [(n, s) for n, s in golden_sql if s])]
    except (OSError, RuntimeError) as problem:
        failed.append(f"D2 {problem}")
        not_planned = [None] * total
    finally:
        try:
            subprocess.run(PSQL + ["-d", "postgres", "-c", f"DROP DATABASE IF EXISTS {db} WITH (FORCE)"], capture_output=True, text=True)
        except OSError:
            pass
    failed += [line for line in not_planned if line]
    parts = [f"explain={total - len(not_planned)}/{total}", f"shop_goldens={len(shop.get('en', []))}+{len(shop.get('ru', []))}"]
    return parts, failed


def run(root):
    parts, failed = d2(root)
    more_parts, more_failed = d3(root)
    return parts + more_parts, failed + more_failed
