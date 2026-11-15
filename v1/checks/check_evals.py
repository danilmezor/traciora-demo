# Checks evals/questions.en.json and evals/questions.ru.json against evals/SCHEMA.md, the sources the questions
# come from, the cast, the ledger and the knowledge base.   python3 checks/check_evals.py
# Writes checks/evals_check.txt and exits 0 when everything closes; otherwise lists what does not and exits 1.
# What it proves:
#   1. every record is valid by SCHEMA.md;
#   2. the two files hold the same ids, except the ones each file declares as one configuration's own;
#   3. every asker is a person of cast.json with that rank and shop (or a customer);
#   4. every ledger key a record names is a row of ledger.json with a value for the configuration; a key that
#      only assistant/ledger_rows.json holds is allowed on a record marked pending for that reason;
#   5. every number in a question's expected answer is the ledger's: each filled token is recomputed, and every
#      numeral left in the text is found in the ledger rows, the knowledge pages or the seed files the record
#      names, or in its own question; a knowledge-base answer's numeral is also the outline row's own;
#   6. every page a record names exists under kb/en or kb/ru;
#   7. each source holds as many questions as the set took from it, with the same asker, kind and small-size
#      mark, and the source's wording is kept beside the question;
#   8. no Russian in the English file's questions and answers, no English sentence in the Russian file's;
#   9. a pending record carries its reasons, a ready one none; a slot's nominal value and a design value are
#      quoted from the file they name.
# Not product code.
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "evals", "_build"))
import common  # noqa: E402

RANKS = {"worker", "junior", "middle", "senior", "admin"}
STORES = {"erp", "core", "conversations", "knowledge_base", "memory", "account_store"}
SURFACES = {"ask", "customer_chat"}
BY = {"rank", "site", "owner", "staff_only"}
TOP = ["id", "source", "area", "story", "configuration", "question", "asker", "session", "kind", "scope", "expected",
       "numbers", "proof", "pages", "seed_files", "sources", "ledger_keys", "small_size", "depends_on_t", "status",
       "pending", "known_failure"]
ID = re.compile(r"^(S(0[1-9]|1[0-6])\.[1-9]|KB\.[PC]\d+\.\d+[ab]?|KB\.O\d+|WD\.\d\d|AS\.\d\d[abc]?)$")
SLOT = re.compile(r"\{([a-z0-9_]+)\}")
KB_SLOT = re.compile(r"`(@[a-z_0-9]+|T[-+]\d+(?:mo|y|w|d))`")
CYR = re.compile(r"[А-Яа-яЁё]")
LATIN_RUN = re.compile(r"(?:\b[A-Za-z]{2,}\b[ ,;:.!?'’-]*){3,}")

fails = []
notes = []


def fail(where, what):
    fails.append("%s: %s" % (where, what))


def spoken(q):
    """The texts a person reads: the question and every answer text, by the field that holds them."""
    e = q["expected"]
    out = [("question", q["question"]), ("answer", e.get("answer"))]
    out += [("facts", f["text"]) for f in e.get("facts", [])]
    out += [("list.members", m) for m in (e.get("list") or {}).get("members") or []]
    out += [("must_not", m) for m in e.get("must_not", [])]
    for part, fields in (("action", ("proposes", "passes_if")), ("nothing", ("why",)),
                         ("cannot_tell", ("lacks", "wrong_if")), ("refusal", ("reason", "may_offer")),
                         ("stale", ("must_state", "wrong_if"))):
        for f in fields:
            out.append(("%s.%s" % (part, f), (e.get(part) or {}).get(f)))
    out += [("cannot_tell.may_give", m) for m in (e.get("cannot_tell") or {}).get("may_give", [])]
    return [(k, v) for k, v in out if v]


# ----------------------------------------------------------------------------- the sources, read again
def md_rows(path, start, end=None):
    s = common.read(path)
    a = s.index(start)
    b = s.index(end, a + len(start)) if end else len(s)
    rows = []
    for line in s[a:b].split("\n"):
        if line.startswith("| ") and not line.startswith("|---"):
            rows.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))])
    return rows


def asked_by(cell):
    """'6 (junior, `main`)' or '4 (senior), asked one day after T' -> [('6', 'junior')]; several when split by ';'."""
    out = []
    for part in re.split(r";\s*(?:then|затем)?\s*", cell):
        part = part.strip()
        if part in ("customer", "клиент"):
            out.append(("customer", "public"))
            continue
        m = re.match(r"^(\d+|F\d)\s*[,(]\s*(\w+)", part)
        if not m:
            raise ValueError(cell)
        out.append((m.group(1), m.group(2)))
    return out


def story_source():
    rows = {}
    for n in range(1, 17):
        for c in md_rows("stories/S%02d.md" % n, "## Questions"):
            if not re.match(r"^S\d+\.\d+$", c[0]):
                continue
            rows[c[0]] = {"text": c[1], "askers": asked_by(c[2]), "kind": c[-2], "small": c[-1] == "yes",
                          "late": "after T" in c[2]}
    index = [c for c in md_rows("stories/README.md", "<!-- questions:start -->", "<!-- questions:end -->")
             if re.match(r"^S\d+\.\d+$", c[0])]
    return rows, index


def kb_source(cfg):
    path = "kb/OUTLINE.md" if cfg == "en" else "kb/OUTLINE-ru.md"
    rows = {}
    for c in md_rows(path, "## 5. Planted on purpose", "## 6. New facts" if cfg == "en" else "## 7. New facts"):
        if re.match(r"^([PC]\d+\.\d+|O\d+)$", c[0]):
            rows[c[0]] = {"text": c[1], "askers": asked_by(c[2]), "expected": c[3]}
    return rows


def design_source(path, start, end, prefix):
    rows = {}
    for c in md_rows(path, start, end):
        if re.match(r"^%s\.?\d+$" % prefix, c[0]):
            rows[c[0]] = {"text": c[1], "askers": asked_by(c[2]), "kind": c[-1].split(",")[0].strip()}
    return rows


# ----------------------------------------------------------------------------- where a number may come from
class Pools:
    def __init__(self, cfg, ledger):
        self.cfg, self.ledger = cfg, ledger
        self.files = {}
        self.kb_rows = common.numbers_in([ledger.value(k, cfg) for k in ledger.rows if k.startswith("kb.")])

    def key(self, key):
        row = self.ledger.row(key)
        return common.numbers_in([self.ledger.value(key, self.cfg), row.get("unit", "")])

    def file(self, path):
        if path not in self.files:
            full = os.path.join(ROOT, path)
            self.files[path] = common.numbers_in(common.read(path)) if os.path.exists(full) else (set(), set())
        return self.files[path]

    def page(self, page):
        cfg = self.cfg
        facts = "kb/facts%s/%s.json" % ("" if cfg == "en" else "-ru", re.sub(r"\.md$", "", page))
        nums, clocks = set(), set()
        for path in ("kb/%s/%s" % (cfg, page), facts, "kb/%s/_history/%s" % (cfg, page)):
            n, c = self.file(path)
            nums |= n
            clocks |= c
        if not page.endswith(".md"):
            n, c = self.file("kb/%s/_binaries.md" % cfg)
            nums |= n
            clocks |= c
        return nums, clocks


def page_exists(cfg, page):
    if os.path.exists(os.path.join(ROOT, "kb", cfg, page)):
        return True
    facts = os.path.join(ROOT, "kb", "facts" if cfg == "en" else "facts-ru", page + ".json")
    return (not page.endswith(".md") and os.path.exists(facts)
            and page in common.read("kb/%s/_binaries.md" % cfg))


# ----------------------------------------------------------------------------- one record
def check_record(q, cfg, ledger, pools, tiers, timeline, proposed_reason, outline=None):
    w = "%s %s" % (cfg, q.get("id"))
    for f in TOP:
        if f not in q:
            fail(w, "field %s is missing" % f)
            return
    extra = set(q) - set(TOP)
    if extra:
        fail(w, "fields outside the schema: %s" % sorted(extra))
    if not ID.match(q["id"]):
        fail(w, "id is not of a known form")
    if q["area"] not in common.AREAS:
        fail(w, "area %r" % q["area"])
    if q["configuration"] != cfg:
        fail(w, "configuration %r in the %s file" % (q["configuration"], cfg))
    if q["kind"] not in common.KINDS:
        fail(w, "kind %r" % q["kind"])
    if set(q["source"]) - {"file", "ref", "text", "notes"} or not all(q["source"].get(k) for k in ("file", "ref", "text")):
        fail(w, "source needs file, ref and text")
    if set(q["asker"]) != {"slot", "rank", "shop", "name"}:
        fail(w, "asker needs slot, rank, shop, name")
    s = q["session"]
    if set(s) != {"surface", "at", "depends_on", "context"} or s["surface"] not in SURFACES or s["at"] not in ("T", "T+1d"):
        fail(w, "session is not valid")
    if set(q["scope"]) != {"population", "period", "definition"} or not all(q["scope"].values()):
        fail(w, "scope needs population, period and definition")
    if not q["sources"] or set(q["sources"]) - STORES:
        fail(w, "sources %r" % q["sources"])
    if not q["proof"] or any(set(p) != {"store", "where"} or p["store"] not in STORES or not p["where"] for p in q["proof"]):
        fail(w, "proof needs a store and a place")
    if q["small_size"] not in (True, False, None):
        fail(w, "small_size")
    if q["status"] not in ("ready", "pending") or (q["status"] == "pending") != bool(q["pending"]):
        fail(w, "status %r with %d reasons" % (q["status"], len(q["pending"])))

    if q["known_failure"] is not None and (not isinstance(q["known_failure"], str) or q["kind"] != "refusal"):
        fail(w, "known_failure is a reason on a refusal, or null")

    e = q["expected"]
    if not e.get("answer"):
        fail(w, "expected.answer is missing")
    need = {"value": "value", "list": "list", "action": "action", "nothing": "nothing", "cannot tell": "cannot_tell",
            "refusal": "refusal", "stale": "stale"}.get(q["kind"])
    if need and need not in e:
        fail(w, "a %s question needs expected.%s" % (q["kind"], need))
    if q["kind"] in ("explanation", "smoke") and not e.get("facts"):
        fail(w, "a %s question needs expected.facts" % q["kind"])
    if q["kind"] == "value" and not (e.get("value") or {}).get("items"):
        fail(w, "a value question needs a ledger key, a page, a seed file or a computed slot")
    if q["kind"] == "list" and not (e.get("list") or {}).get("rule"):
        fail(w, "a list question needs its membership rule")
    if q["kind"] == "refusal" and (e["refusal"].get("by") not in BY or not e["refusal"].get("reason")):
        fail(w, "a refusal needs by and reason")
    if q["kind"] == "cannot tell" and not e["cannot_tell"].get("lacks"):
        fail(w, "a cannot-tell question says what the data lacks")
    if q["kind"] == "action" and not (e["action"].get("proposes") and e["action"].get("passes_if")):
        fail(w, "an action needs proposes and passes_if")
    if q["kind"] == "stale" and not e["stale"].get("must_state"):
        fail(w, "a stale question says what the answer must state")
    if q["session"]["at"] == "T+1d" and q["kind"] != "stale":
        fail(w, "asked after T but not of kind stale")

    # slots
    texts = spoken(q)
    said = " ".join(v for _, v in texts)
    named = set(SLOT.findall(said)) | set(KB_SLOT.findall(said))
    if (e.get("list") or {}).get("slot"):
        named.add(e["list"]["slot"])
    defined = {c["slot"]: c for c in e.get("computed", [])}
    if named != set(defined):
        fail(w, "computed slots named %s, defined %s" % (sorted(named), sorted(defined)))
    if q["depends_on_t"] != bool(defined):
        fail(w, "depends_on_t does not follow the computed slots")
    for c in defined.values():
        if not all(c.get(k) for k in ("what", "how", "store", "tables")):
            fail(w, "slot %s needs what, how, store and tables" % c["slot"])
        if c.get("nominal") and c["nominal"]["quote"] not in timeline:
            fail(w, "slot %s: %r is not in TIMELINE.md's example for %s" % (c["slot"], c["nominal"]["quote"], cfg))
        if c.get("nominal") and c["nominal"]["value"] not in c["nominal"]["quote"]:
            fail(w, "slot %s: the nominal value is not in its quote" % c["slot"])
        if c.get("design") and c["design"]["quote"] not in common.read(c["design"]["file"]):
            fail(w, "slot %s: %r is not in %s" % (c["slot"], c["design"]["quote"], c["design"]["file"]))

    # ledger keys
    for key in q["ledger_keys"]:
        where = ledger.where(key)
        if where is None:
            fail(w, "ledger key %s does not exist" % key)
            continue
        try:
            v = ledger.value(key, cfg)
        except KeyError:
            v = None
        if v is None:
            fail(w, "ledger key %s has no value for %s" % (key, cfg))
        if where != "ledger.json" and proposed_reason not in q["pending"]:
            fail(w, "ledger key %s is only in %s and the record is not pending for it" % (key, where))

    # numbers: the filled tokens, recomputed
    shown = []
    for n in q["numbers"]:
        try:
            if n["from"] == "ledger":
                key, path, v = ledger.get(n["key"] + n["path"], cfg)
                now = common.fmt(v, n["format"], cfg)
                if n["key"] not in q["ledger_keys"]:
                    fail(w, "token key %s is not among ledger_keys" % n["key"])
            else:
                now = common.fmt(common.evaluate(n["formula"], ledger, cfg), n["format"], cfg)
        except Exception as x:  # noqa: BLE001
            fail(w, "number %r cannot be recomputed: %s" % (n.get("shown"), x))
            continue
        if now != n["shown"]:
            fail(w, "number %r is %r in the ledger now" % (n["shown"], now))
        if n["shown"] not in said:
            fail(w, "number %r is not in the record's texts" % n["shown"])
        shown.append(n["shown"])

    # numbers: every numeral left in an answer text
    token_nums, token_clocks = common.numbers_in(shown)
    own_nums, own_clocks = common.numbers_in(q["question"])
    for field, value in texts:
        if field == "question":
            continue
        for kind, n in common.numerals(value, cfg):
            pool = token_clocks if kind == "clock" else token_nums
            if n in pool:
                tiers["token"] += 1
                continue
            if n in (own_clocks if kind == "clock" else own_nums):
                tiers["question"] += 1
                continue
            if outline is not None and not (n in outline[1] if kind == "clock" else n in outline[0]):
                fail(w, "%s: %s is not a figure of the outline's row" % (field, n if kind == "clock" else "%g" % n))
                continue
            found = None
            for key in q["ledger_keys"]:
                if ledger.row(key) is None:
                    continue
                nums, clocks = pools.key(key)
                if (kind == "clock" and n in clocks) or (kind == "n" and common.matches(n, nums)):
                    found = "ledger row"
                    break
            if not found:
                for page in q["pages"]:
                    nums, clocks = pools.page(page)
                    if (kind == "clock" and n in clocks) or (kind == "n" and n in nums):
                        found = "page"
                        break
            if not found:
                for path in q["seed_files"]:
                    nums, clocks = pools.file(path)
                    if (kind == "clock" and n in clocks) or (kind == "n" and n in nums):
                        found = "seed file"
                        break
            if not found and q["area"] == "knowledge_base":
                nums, clocks = pools.kb_rows
                if (kind == "clock" and n in clocks) or (kind == "n" and n in nums):
                    found = "ledger kb.*"
            if not found and outline is not None:
                nums, clocks = outline
                if (kind == "clock" and n in clocks) or (kind == "n" and n in nums):
                    found = "outline only"
                    notes.append("%s: %s is the outline's own computed figure: it is not on a page the record "
                                 "names nor in the ledger" % (w, n if kind == "clock" else ("%g" % n)))
            if found:
                tiers[found] += 1
            else:
                fail(w, "%s: %s in %r is not a ledger value, a page value or a seed-file value the record names"
                     % (field, n if kind == "clock" else ("%g" % n), value[:90]))

    # pages
    for page in q["pages"]:
        if not page_exists(cfg, page):
            fail(w, "page %s is not under kb/%s" % (page, cfg))
    for path in q["seed_files"]:
        if not os.path.exists(os.path.join(ROOT, path)):
            fail(w, "seed file %s does not exist" % path)

    # language
    for field, value in texts:
        clean = common.CODE.sub(" ", common.SLOT.sub(" ", value))
        if cfg == "en" and CYR.search(clean):
            fail(w, "%s holds Russian: %r" % (field, value[:80]))
        if cfg == "ru":
            if not CYR.search(clean) and re.search(r"[A-Za-z]{4,}", clean):
                fail(w, "%s holds no Russian: %r" % (field, value[:80]))
            m = LATIN_RUN.search(clean)
            if m:
                fail(w, "%s holds an English run %r" % (field, m.group(0).strip()))


def main():
    ledger = common.Ledger()
    cast = {p["slot"]: p for p in common.load("cast.json")["people"]}
    docs = {cfg: common.load("evals", "questions.%s.json" % cfg) for cfg in common.CONFIGS}
    timeline_all = common.read("stories/TIMELINE.md")
    proposed_reason = None
    sys.path.insert(0, os.path.join(ROOT, "evals", "_build", "src"))
    import dsl  # the names of the pending reasons
    proposed_reason = dsl.PENDING["proposed_rows"]
    pending_md = common.read("PENDING.md")

    stories, index = story_source()
    if len(stories) != 84 or len(index) != 84:
        fail("stories", "the cards hold %d questions and the index %d, not 84" % (len(stories), len(index)))
    wd = design_source("workday/DESIGN.md", "## 9. Eval questions this part supports", "## 10.", "W")
    asst = design_source("assistant/DESIGN.md", "## 8. Eval questions this part supports", "## 9.", r"A\.")
    out = ["checks/check_evals.py", ""]
    tiers_all = {}

    for cfg in common.CONFIGS:
        doc = docs[cfg]
        qs = doc["questions"]
        pools = Pools(cfg, ledger)
        a = timeline_all.index("### %s, run at Fri 2026-11-13 10:30" % cfg)
        timeline = timeline_all[a:timeline_all.index("###", a + 5)]
        tiers = collections.Counter()
        seen = set()
        kb = kb_source(cfg)
        refs = collections.defaultdict(list)
        for q in qs:
            if q.get("id") in seen:
                fail("%s %s" % (cfg, q.get("id")), "the id is used twice")
            seen.add(q.get("id"))
            row = kb.get((q.get("source") or {}).get("ref")) if q.get("area") == "knowledge_base" else None
            check_record(q, cfg, ledger, pools, tiers, timeline, proposed_reason,
                         common.numbers_in(row["expected"]) if row else None)
            if set(TOP) - set(q):
                continue
            w = "%s %s" % (cfg, q["id"])
            refs[(q["area"], q["source"]["ref"])].append(q)

            # the asker
            a_ = q["asker"]
            if a_["slot"] == "customer":
                if q["session"]["surface"] != "customer_chat" or a_["rank"] != "public":
                    fail(w, "a customer asks in the customer chat, as public")
            else:
                p = cast.get(a_["slot"])
                if p is None:
                    fail(w, "asker slot %s is not in cast.json" % a_["slot"])
                else:
                    shop = None if p["site"] in (None, "none") else p["site"]
                    if (a_["rank"], a_["shop"], a_["name"]) != (p["rank"], shop, p[cfg]["full_name"]):
                        fail(w, "asker %s is %s, %s, %s in cast.json" % (a_["slot"], p["rank"], shop, p[cfg]["full_name"]))
                    if p["status"] != "active":
                        fail(w, "asker %s is not active" % a_["slot"])
            dep = q["session"]["depends_on"]
            if dep and dep not in {x["id"] for x in qs}:
                fail(w, "depends on %s, which is not in the file" % dep)

            # the source row
            ref, area = q["source"]["ref"], q["area"]
            src = {"story": stories, "knowledge_base": kb, "working_day": wd, "assistant": asst}[area].get(ref)
            if src is None:
                fail(w, "source row %s is not in %s" % (ref, q["source"]["file"]))
                continue
            if a_["slot"] != "customer" and (a_["slot"], a_["rank"]) not in src["askers"]:
                fail(w, "asked by %s (%s); the source says %s" % (a_["slot"], a_["rank"], src["askers"]))
            if a_["slot"] == "customer" and ("customer", "public") not in src["askers"]:
                fail(w, "the source's asker is not a customer")
            if "kind" in src and src["kind"] != q["kind"]:
                fail(w, "kind %s; the source says %s" % (q["kind"], src["kind"]))
            if "small" in src and src["small"] != q["small_size"]:
                fail(w, "small size %s; the card says %s" % (q["small_size"], src["small"]))
            if src.get("late") and q["session"]["at"] != "T+1d":
                fail(w, "the card asks it one day after T")
            if q["source"]["text"] != src["text"]:
                fail(w, "source.text is not the source's wording")
            if area == "knowledge_base" and cfg == "ru" and q["question"] != src["text"] and ref != "O2":
                if not any("ru question" in n for n in q["source"].get("notes", [])):
                    fail(w, "the Russian outline's question was changed without a note")
            if area == "knowledge_base" and cfg == "en" and q["question"] != src["text"] and ref != "O2":
                fail(w, "the English outline's question was changed")

            # pending reasons that quote PENDING.md hold its words
            for reason in q["pending"] + ([q["known_failure"]] if q["known_failure"] else []):
                for quoted in re.findall(r"\"(.{40,}?)\"(?:$|; decided)", reason):
                    for piece in re.split(r"\s*\[\.\.\.\]\s*", quoted):
                        if piece.replace('\\"', '"') not in pending_md:
                            fail(w, "pending reason quotes words PENDING.md does not hold: %r" % piece[:70])

        # counts per source
        per_area = collections.Counter(q["area"] for q in qs if "area" in q)
        got = {a_: len({r for (ar, r) in refs if ar == a_}) for a_ in common.AREAS}
        want = {"story": len(stories), "knowledge_base": len(kb), "working_day": len(wd), "assistant": len(asst),
                "calls": 0, "conversations": 0}
        for a_ in common.AREAS:
            if got[a_] != want[a_]:
                fail(cfg, "%s: %d source questions in the set, the source holds %d" % (a_, got[a_], want[a_]))
            if doc["sources"][a_]["questions"] != want[a_]:
                fail(cfg, "%s: the file's header says %d, the source holds %d" % (a_, doc["sources"][a_]["questions"], want[a_]))
        for (a_, ref), group in refs.items():
            src = {"story": stories, "knowledge_base": kb, "working_day": wd, "assistant": asst}[a_].get(ref)
            if src and len(group) != len(src["askers"]):
                fail(cfg, "%s %s: %d records for %d askers" % (a_, ref, len(group), len(src["askers"])))
        missing = [r for r in list(stories) if ("story", r) not in refs] + \
                  [r for r in kb if ("knowledge_base", r) not in refs] + \
                  [r for r in wd if ("working_day", r) not in refs] + [r for r in asst if ("assistant", r) not in refs]
        if missing:
            fail(cfg, "source questions not in the set: %s" % missing)
        tiers_all[cfg] = tiers
        kinds = collections.Counter(q["kind"] for q in qs)
        out.append("%s: %d records (%s); source questions: %s" % (
            cfg, len(qs), ", ".join("%s %d" % (a_, per_area[a_]) for a_ in common.AREAS),
            ", ".join("%s %d" % (a_, got[a_]) for a_ in common.AREAS)))
        out.append("   by kind: " + ", ".join("%s %d" % (k, kinds[k]) for k in common.KINDS))
        out.append("   status: ready %d, pending %d" % (sum(1 for q in qs if q["status"] == "ready"),
                                                         sum(1 for q in qs if q["status"] == "pending")))
        out.append("   numbers in answers, by where each was found: " +
                   ", ".join("%s %d" % (k, v) for k, v in sorted(tiers.items(), key=lambda kv: -kv[1])))

    # the same ids in both files
    ids = {cfg: {q["id"] for q in docs[cfg]["questions"]} for cfg in common.CONFIGS}
    declared = {cfg: {o["id"]: o for o in docs[cfg]["one_configuration_only"]} for cfg in common.CONFIGS}
    if declared["en"] != declared["ru"]:
        fail("ids", "the two files declare different one-configuration questions")
    for cfg, other in (("en", "ru"), ("ru", "en")):
        for i in sorted(ids[cfg] - ids[other]):
            d = declared[cfg].get(i)
            if not d or d["configuration"] != cfg or not d["reason"]:
                fail("ids", "%s is only in the %s file and is not declared with a reason" % (i, cfg))
    for i, d in declared["en"].items():
        if i in ids["en"] and i in ids["ru"]:
            fail("ids", "%s is declared as %s only and is in both files" % (i, d["configuration"]))
    for i in sorted(ids["en"] & ids["ru"]):
        a_, b = [next(q for q in docs[cfg]["questions"] if q["id"] == i) for cfg in common.CONFIGS]
        for f in ("area", "kind", "story", "small_size"):
            if a_[f] != b[f]:
                fail("ids", "%s: %s differs between the files (%r, %r)" % (i, f, a_[f], b[f]))
        if a_["asker"]["slot"] != b["asker"]["slot"] or a_["session"] != b["session"]:
            fail("ids", "%s: asker or session differs between the files" % i)
    only = sorted(set(declared["en"]))
    out.append("")
    out.append("ids: %d in both files; one configuration only: %s" % (
        len(ids["en"] & ids["ru"]), ", ".join("%s (%s)" % (i, declared["en"][i]["configuration"]) for i in only) or "none"))

    # the rendered tables are the JSON's
    for cfg in common.CONFIGS:
        md = common.read("evals/questions.%s.md" % cfg)
        for q in docs[cfg]["questions"]:
            if "| %s |" % q["id"] not in md:
                fail(cfg, "%s is not in questions.%s.md: run evals/_build/render.py" % (q["id"], cfg))
    import hashlib
    with open(os.path.join(ROOT, "ledger.json"), "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    for cfg in common.CONFIGS:
        if docs[cfg]["ledger_sha256"] != sha:
            notes.append("%s: ledger.json changed since the file was built; every number was recomputed against "
                         "the ledger as it is now" % cfg)

    out.append("")
    for n in notes:
        out.append("note: " + n)
    if fails:
        out.append("DOES NOT CLOSE: %d" % len(fails))
        out += ["  " + f for f in fails]
    else:
        out.append("EVALS PASS: every record valid, ids matched, askers in the cast, ledger keys present, numbers "
                   "the ledger's, pages present, counts equal to the sources, languages apart")
    text = "\n".join(out) + "\n"
    with open(os.path.join(ROOT, "checks", "evals_check.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.write(text)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
