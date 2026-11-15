# Writes evals/questions.en.md and evals/questions.ru.md from the JSON files: one table per area for a person
# to read; and refreshes the counts and the pending list of evals/README.md between its two markers.
# Nothing here adds or changes a question.   python3 evals/_build/render.py
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

TITLE = {"story": "Stories", "knowledge_base": "Knowledge base", "calls": "Calls", "conversations": "Conversations",
         "working_day": "Working day", "assistant": "Assistant"}


def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def asker(a):
    if a["slot"] == "customer":
        return "a customer (the website assistant)"
    return "%s (%s, %s%s)" % (a["name"], a["slot"], a["rank"], ", " + a["shop"] if a["shop"] else "")


def one_line(q):
    """The expected answer in a line; a computed slot shows its value for the nominal T where the timeline
    gives one."""
    nominal = {c["slot"]: c["nominal"]["value"] for c in q["expected"].get("computed", []) if c["nominal"]}
    text = q["expected"]["answer"]
    return re.sub(r"\{([a-z0-9_]+)\}", lambda m: "{%s = %s}" % (m.group(1), nominal[m.group(1)])
                  if m.group(1) in nominal else m.group(0), text)


def render(cfg):
    with open(os.path.join(common.EVALS, "questions.%s.json" % cfg), encoding="utf-8") as f:
        doc = json.load(f)
    qs = doc["questions"]
    out = ["# Eval questions, %s configuration" % ("English" if cfg == "en" else "Russian"), "",
           "Generated from `questions.%s.json` by `_build/render.py`; do not edit. Eval set %s, runs on seed %s. "
           "The record format is in `SCHEMA.md`. `{name}` is a value the seeder computes for its T; where "
           "`stories/TIMELINE.md` gives it for T = Fri 2026-11-13 10:30 it is shown after `=`. "
           "`pending` records are listed in `README.md` with their reasons." % (cfg, doc["eval_set"], doc["runs_on_seed"]),
           ""]
    kinds = collections.Counter((q["area"], q["kind"]) for q in qs)
    areas = [a for a in common.AREAS]
    out += ["| Area | Questions | " + " | ".join(common.KINDS) + " | pending |", "|---|---:|" + "---:|" * (len(common.KINDS) + 1)]
    for a in areas:
        n = sum(1 for q in qs if q["area"] == a)
        out.append("| %s | %d | %s | %d |" % (TITLE[a], n, " | ".join(str(kinds[(a, k)]) for k in common.KINDS),
                                           sum(1 for q in qs if q["area"] == a and q["status"] == "pending")))
    out.append("| all | %d | %s | %d |" % (len(qs), " | ".join(str(sum(kinds[(a, k)] for a in areas)) for k in common.KINDS),
                                        sum(1 for q in qs if q["status"] == "pending")))
    out.append("")
    for a in areas:
        rows = [q for q in qs if q["area"] == a]
        out += ["## %s" % TITLE[a], ""]
        if not rows:
            out += [doc["sources"][a].get("note", "No question.").capitalize() + ".", ""]
            continue
        out += ["| id | Asked by | Question | Kind | Expected answer | Status |", "|---|---|---|---|---|---|"]
        for q in rows:
            out.append("| %s | %s | %s | %s | %s | %s |" % (q["id"], cell(asker(q["asker"])), cell(q["question"]),
                                                            q["kind"], cell(one_line(q)), q["status"]))
        out.append("")
    path = os.path.join(common.EVALS, "questions.%s.md" % cfg)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("%s: %d rows" % (os.path.basename(path), len(qs)))




# ----------------------------------------------------------------------------- the generated part of README.md
def readme():
    docs = {}
    for cfg in common.CONFIGS:
        with open(os.path.join(common.EVALS, "questions.%s.json" % cfg), encoding="utf-8") as f:
            docs[cfg] = json.load(f)
    out = []
    for cfg in common.CONFIGS:
        qs = docs[cfg]["questions"]
        kinds = collections.Counter((q["area"], q["kind"]) for q in qs)
        out += ["**%s**: %d records for %d source questions." % (
            "English" if cfg == "en" else "Russian", len(qs),
            len({(q["area"], q["source"]["ref"]) for q in qs})), "",
            "| Area | Records | " + " | ".join(common.KINDS) + " | pending |",
            "|---|---:|" + "---:|" * (len(common.KINDS) + 1)]
        for a in common.AREAS:
            n = sum(1 for q in qs if q["area"] == a)
            out.append("| %s | %d | %s | %d |" % (TITLE[a], n, " | ".join(str(kinds[(a, k)]) for k in common.KINDS),
                                               sum(1 for q in qs if q["area"] == a and q["status"] == "pending")))
        out.append("| all | %d | %s | %d |" % (len(qs), " | ".join(
            str(sum(kinds[(a, k)] for a in common.AREAS)) for k in common.KINDS),
            sum(1 for q in qs if q["status"] == "pending")))
        out.append("")
    only = docs["ru"]["one_configuration_only"]
    out += ["**In one configuration only** (%d, all Russian):" % len(only), ""]
    out += ["- `%s`: %s" % (o["id"], o["reason"]) for o in only]
    known = [q for q in docs["en"]["questions"] if q["known_failure"]]
    if known:
        out += ["", "**Expected to fail on the product as it is** (ready, not pending): %s. %s." % (
            ", ".join("`%s`" % q["id"] for q in known), known[0]["known_failure"][0].upper() + known[0]["known_failure"][1:])]
    out += ["", "**Pending**, by reason:", ""]
    reasons = collections.OrderedDict()
    for cfg in common.CONFIGS:
        for q in docs[cfg]["questions"]:
            for r in q["pending"]:
                reasons.setdefault(r, {"en": [], "ru": []})[cfg].append(q["id"])
    for r, ids in reasons.items():
        both = [i for i in ids["en"] if i in ids["ru"]]
        parts = []
        if both:
            parts.append("both: " + ", ".join(both))
        for cfg in common.CONFIGS:
            rest = [i for i in ids[cfg] if i not in both]
            if rest:
                parts.append("%s only: %s" % (cfg, ", ".join(rest)))
        out += ["- %s" % r, "  - " + "; ".join(parts)]
    path = os.path.join(common.EVALS, "README.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    a, b = text.index("<!-- generated:start -->"), text.index("<!-- generated:end -->")
    text = text[:a] + "<!-- generated:start -->\n" + "\n".join(out) + "\n" + text[b:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("README.md: counts and pending list refreshed")


if __name__ == "__main__":
    for cfg in common.CONFIGS:
        render(cfg)
    readme()
