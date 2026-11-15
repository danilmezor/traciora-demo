# Assembles evals/questions.en.json and evals/questions.ru.json from the sources in src/.
#   python3 evals/_build/build.py        then        python3 evals/_build/render.py
# Every number in a question or an expected answer is filled here from ledger.json for the configuration
# (tokens [[key.path|format]] and formulas [[=...|format]]); nothing in src/ types a ledger number by hand
# except where a record names the ledger row the check reads it from. SCHEMA.md defines a record.
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "src"))

import common  # noqa: E402
import dsl  # noqa: E402

for name in ("stories_a", "stories_b", "stories_c", "stories_d", "kb", "workday", "assistant"):
    __import__(name)
import kb  # noqa: E402

EVAL_SET = "v1.0"
SEED = "v1"
AREA = {"S": "story", "KB": "knowledge_base", "WD": "working_day", "AS": "assistant"}
SLOT = re.compile(r"\{([a-z0-9_]+)\}")
KB_SLOT = re.compile(r"`(@[a-z_0-9]+|T[-+]\d+(?:mo|y|w|d))`")

ledger = common.Ledger()
cast = {p["slot"]: p for p in common.load("cast.json")["people"]}


def pick(v, cfg):
    return v[cfg] if isinstance(v, dict) and set(v) == {"en", "ru"} else v


def asker_of(slot, cfg):
    if slot == "customer":
        return {"slot": "customer", "rank": "public", "shop": None, "name": None}
    p = cast[str(slot)]
    return {"slot": p["slot"], "rank": p["rank"], "shop": None if p["site"] in (None, "none") else p["site"],
            "name": p[cfg]["full_name"]}


def pending_text(name):
    if name.startswith("card_vs_ledger:"):
        return "card and ledger differ: " + name.split(":", 1)[1]
    return dsl.PENDING[name]


def build(rec, cfg):
    q = pick(rec["q"], cfg)
    if q is None or rec.get("only") not in (None, cfg):
        return None
    numbers = []
    keys = []
    for key in rec.get("keys") or []:   # a named row counts where it holds a value for the configuration
        if ledger.row(key) is None:
            raise KeyError("%s names ledger row %s, which does not exist" % (rec["id"], key))
        if ledger.value(key, cfg) is not None:
            keys.append(key)

    def text(v):
        v = pick(v, cfg)
        return None if v is None else common.fill(v, ledger, cfg, numbers, keys)

    kind = rec["kind"]
    exp = {"answer": text(rec["answer"])}
    facts = rec.get("facts_by_cfg", {}).get(cfg) if rec.get("facts_by_cfg") else [text(f) for f in rec.get("facts") or []]
    facts = [f for f in facts or [] if f]
    if facts:
        exp["facts"] = [{"id": "f%d" % (n + 1), "text": f} for n, f in enumerate(facts)]
    if kind == "list":
        members = (rec.get("members_by_cfg") or {}).get(cfg) or [text(m) for m in rec.get("members") or []]
        exp["list"] = {"rule": rec.get("list_rule"), "members": [m for m in members if m] or None,
                       "slot": rec.get("member_slot")}
    if kind == "action":
        a = rec["action"]
        exp["action"] = {"proposes": text(a["proposes"]), "passes_if": text(a["passes_if"]),
                         "writes_nothing_unconfirmed": True}
    if kind == "nothing":
        exp["nothing"] = {"why": text(rec["nothing"])}
    if kind == "cannot tell":
        c = rec["cannot"]
        exp["cannot_tell"] = {"lacks": text(c["lacks"]), "may_give": [text(m) for m in c.get("may_give") or []],
                              "wrong_if": text(c.get("wrong_if"))}
    if kind == "refusal":
        r = rec["refusal"]
        exp["refusal"] = {"by": r["by"], "reason": text(r["reason"]), "may_offer": text(r.get("may_offer"))}
    if kind == "stale":
        s = rec["stale"]
        exp["stale"] = {"must_state": text(s["must_state"]), "wrong_if": text(s["wrong_if"])}
    if rec.get("must_not"):
        exp["must_not"] = [text(m) for m in rec["must_not"]]
    if rec.get("tolerance"):
        exp["tolerance"] = rec["tolerance"]

    # computed slots: those the configuration's texts name
    question = text(q)
    said = json.dumps([question, exp], ensure_ascii=False)
    named = set(SLOT.findall(said)) | set(KB_SLOT.findall(said))
    if rec.get("member_slot"):
        named.add(rec["member_slot"])
    defined = {}
    for c in (rec.get("computed") or []) + (rec.get("question_slots") or []):
        defined[c["slot"]] = c
    missing = named - set(defined)
    assert not missing, "%s %s: no definition for %s" % (rec["id"], cfg, sorted(missing))
    computed = []
    for name in sorted(named):
        c = defined[name]
        nominal = (c.get("nominal") or {}).get(cfg)
        design = c.get("design")
        computed.append({"slot": name, "what": c["what"], "how": c["how"], "store": c["store"],
                         "tables": c["tables"],
                         "nominal": {"t": dsl.NOMINAL_T, "value": nominal[0], "quote": nominal[1]} if nominal else None,
                         "design": {"file": design[0], "quote": design[1]} if design else None})
    if computed:
        exp["computed"] = computed

    if kind == "value":
        in_answer = common.TOKEN.findall(pick(rec["answer"], cfg))
        items = []
        for n in numbers[:len(in_answer)]:
            if n["from"] == "ledger":
                items.append({"source": "ledger", "key": n["key"], "path": n["path"], "shown": n["shown"]})
            else:
                items.append({"source": "derived", "formula": n["formula"], "shown": n["shown"]})
        for name in SLOT.findall(exp["answer"]):
            items.append({"source": "computed", "slot": name})
        if not items and keys:
            items = [{"source": "ledger", "key": k, "path": "", "shown": None} for k in keys]
        if not items and rec.get("pages"):
            items = [{"source": "page", "pages": rec["pages"]}]
        if not items and rec.get("seed_files"):
            items = [{"source": "seed_file", "files": [f.replace("{cfg}", cfg) for f in rec["seed_files"]]}]
        exp["value"] = {"items": items}

    for shown, formula, f in (rec.get("extra_numbers") or {}).get(cfg, []):
        used = []
        now = common.fmt(common.evaluate(formula, ledger, cfg, used), f, cfg)
        assert now == shown, "%s %s: %r is %r by its formula" % (rec["id"], cfg, shown, now)
        for k_ in used:
            if k_ not in keys:
                keys.append(k_)
        numbers.append({"shown": shown, "from": "derived", "formula": formula, "format": f})
    proposed = sorted(k for k in keys if ledger.where(k) == "assistant/ledger_rows.json")
    pend = rec.get("pending") or {}
    reasons = [pending_text(n) for n in list(pend.get("both", [])) + list(pend.get(cfg, []))]
    if proposed and dsl.PENDING["proposed_rows"] not in reasons:
        reasons.append(dsl.PENDING["proposed_rows"])

    prefix = rec["id"].split(".")[0].rstrip("0123456789")
    area = rec.get("area") or AREA[prefix]
    src_q = pick(rec["src_q"], cfg)
    source = {"file": pick(rec["file"], cfg), "ref": rec["ref"], "text": src_q}
    if rec.get("notes"):
        source["notes"] = rec["notes"]
    proof = [{"store": s, "where": pick(w, cfg)} for s, w in rec["proof"]]
    seed_files = [f.replace("{cfg}", cfg) for f in rec.get("seed_files") or []]
    out = {
        "id": rec["id"], "source": source, "area": area, "story": rec.get("story"), "configuration": cfg,
        "question": question, "asker": asker_of(rec["asker"], cfg),
        "session": {"surface": rec.get("surface", "ask"), "at": rec.get("at", "T"),
                    "depends_on": rec.get("depends_on"), "context": rec.get("context")},
        "kind": kind,
        "scope": {k: pick(v, cfg) for k, v in rec["scope"].items()},
        "expected": exp, "numbers": numbers, "proof": proof, "pages": list(rec.get("pages") or []),
        "seed_files": seed_files, "sources": list(rec["sources"]), "ledger_keys": keys,
        "small_size": rec.get("small"), "depends_on_t": bool(computed),
        "status": "pending" if reasons else "ready", "pending": reasons,
        "known_failure": dsl.KNOWN_FAILURE if rec.get("known_failure") else None,
    }
    return out


def main():
    with open(os.path.join(common.ROOT, "ledger.json"), "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    ids = {cfg: [] for cfg in common.CONFIGS}
    for cfg in common.CONFIGS:
        questions = [x for x in (build(r, cfg) for r in dsl.RECORDS) if x]
        ids[cfg] = [x["id"] for x in questions]
        assert len(ids[cfg]) == len(set(ids[cfg])), "duplicate ids"
        only = [{"id": r["id"], "configuration": r["only"], "reason": r.get("only_reason")}
                for r in dsl.RECORDS if r.get("only")]
        doc = {
            "format": "seed-eval-questions/1",
            "eval_set": EVAL_SET,
            "runs_on_seed": SEED,
            "configuration": cfg,
            "ledger_sha256": sha,
            "sources": {
                "story": {"file": "stories/S01.md .. S16.md", "questions": 84},
                "knowledge_base": {"file": kb.EN if cfg == "en" else kb.RU,
                                   "questions": kb.COUNTS[cfg]["plants"] + kb.COUNTS[cfg]["operating"],
                                   "in_plants": kb.COUNTS[cfg]["plants"], "operating": kb.COUNTS[cfg]["operating"]},
                "calls": {"file": "calls/DESIGN.md", "questions": 0,
                          "note": "the file words no question; section 4 names one without wording it (\"that "
                                  "difference is planted, counted and an eval question in itself\")"},
                "conversations": {"file": "conversations/DESIGN.md", "questions": 0,
                                  "note": "the file words no question"},
                "working_day": {"file": "workday/DESIGN.md section 9", "questions": 17},
                "assistant": {"file": "assistant/DESIGN.md section 8", "questions": 16},
            },
            "one_configuration_only": only,
            "questions": questions,
        }
        path = os.path.join(common.EVALS, "questions.%s.json" % cfg)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("%s: %d questions, %d pending" % (os.path.basename(path), len(questions),
                                                 sum(1 for x in questions if x["status"] == "pending")))


if __name__ == "__main__":
    main()
