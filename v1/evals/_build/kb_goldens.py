# Writes the knowledge-base goldens, goldens/kb.en.yaml and goldens/kb.ru.yaml, from the question records
# (evals/questions.<lang>.json) and the built pages (kb/<lang>/), and lists every record it leaves out with its
# reason in goldens/kb.skipped.md.      python3 evals/_build/kb_goldens.py
# A record enters only if every figure of its expected answer occurs literally on a page it names (spaces
# normalised). Dates are left out; a figure the pages do not print (a computed sum) keeps the record out.
# Nothing here types a value: each fact is a figure of the record's own answer, written as the page prints it.
# Each golden carries its asker's sign-in name from cast.json (`username`); a customer's question has none.
import json
import os
import re

import yaml

V1 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(V1, "goldens")
KINDS = ("value", "list")
MONTHS = ("January|February|March|April|May|June|July|August|September|October|November|December|"
          "января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря")
DATE = re.compile(r"`[^`]*`|\b\d{1,2}\.\d{1,2}\.\d{4}\b|\b\d{1,2}(?:(?:, | и | and )\d{1,2})* (?:%s)\b" % MONTHS)
EDGE = r"(?<![\w.,])"
FIGURE = {
    "en": re.compile(EDGE + r"(?:\(\d{3}\) \d{3}-\d{4}|\$(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\d{1,2}:\d{2}|[A-Za-z]+-?\d[\w-]*"
                     r"|\d+[A-Za-z]+(?:-\d+)?\w*|\d+/\d+|(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?: ?%)?)"),
    "ru": re.compile(EDGE + r"(?:\d{1,2}:\d{2}|[A-Za-z]+-?\d[\w-]*|(?:\d{1,3}(?: \d{3})+|\d+)(?:,\d+)?(?: ?[₽%])?)"),
}


def spaces(text):
    return re.sub(r"\s+", " ", text)


def page_text(lang, path):
    """A page as printed: its Markdown, or a binary document's draft section in _binaries.md; placeholders dropped."""
    file = os.path.join(V1, "kb", lang, path)
    if os.path.isfile(file):
        text = open(file, encoding="utf-8").read()
    else:
        drafts = open(os.path.join(V1, "kb", lang, "_binaries.md"), encoding="utf-8").read()
        found = re.search(r"^## \d+\. `%s`\n(.*?)(?=^## \d+\. `|\Z)" % re.escape(path), drafts, re.S | re.M)
        if not found:
            return None
        text = found.group(1)
    return spaces(re.sub(r"\{\{[^}]*\}\}", " ", text))


def printed(figure, text, lang):
    """The figure as the page prints it, or None. It may not be part of a longer number (Russian groups thousands
    with a space)."""
    head, tail = (r"(?<![\w.,])(?<!\d )", r"(?!\w|,\d| \d{3}(?!\d))") if lang == "ru" else (r"(?<![\w.,])", r"(?!\w|[.,]\d)")
    found = re.search(head + re.escape(figure).replace(r"\ ", " ?") + tail, text)
    return found.group(0) if found else None


def convert(record, lang, usernames):
    """(entry, None) when the record enters, (None, reason) when it does not."""
    if record["status"] != "ready":
        return None, "pending"
    if record["kind"] not in KINDS:
        return None, "kind: " + record["kind"]
    if record["sources"] != ["knowledge_base"]:
        return None, "mixes stores: " + ", ".join(record["sources"])
    if not record["pages"]:
        return None, "names no page"
    answer = spaces(record["expected"]["answer"])
    undated = DATE.sub(" ", answer)
    figures = list(dict.fromkeys(f.strip() for f in FIGURE[lang].findall(undated)))
    if not figures:
        return None, "no figure but a date" if undated != answer else "no figure in the answer"
    pages = {p: page_text(lang, p) for p in record["pages"]}
    missing = [p for p, t in pages.items() if t is None]
    if missing:
        return None, "page not built: " + ", ".join(missing)
    found = {f: [p for p in record["pages"] if printed(f, pages[p], lang)] for f in figures}
    absent = [f for f, where in found.items() if not where]
    if absent:
        return None, "not printed on a named page: " + ", ".join(absent)
    order = sorted(record["pages"], key=lambda p: -sum(p in where for where in found.values()))
    facts = []
    for f, where in found.items():
        page = next(p for p in order if p in where)
        facts.append({"value": printed(f, pages[page], lang), "page": page})
    slot = str(record["asker"]["slot"])
    asker = {"asker": slot} if slot == "customer" else {"asker": slot, "username": usernames[slot]}
    return {"id": record["id"], "question": record["question"], **asker, "facts": facts,
            "rule": order[0], "assertions": [{"type": "tool_call", "tool": "kb_read"}]}, None


def main():
    os.makedirs(OUT, exist_ok=True)
    skipped, counts = [], {}
    people = json.load(open(os.path.join(V1, "cast.json"), encoding="utf-8"))["people"]
    for lang in ("en", "ru"):
        usernames = {p["slot"]: p[lang]["username"] for p in people}
        records = json.load(open(os.path.join(V1, "evals", f"questions.{lang}.json"), encoding="utf-8"))["questions"]
        entries = []
        for record in records:
            if record["area"] != "knowledge_base":
                continue
            entry, reason = convert(record, lang, usernames)
            if entry:
                entries.append(entry)
            else:
                skipped.append((record["id"], lang, reason))
        counts[lang] = len(entries)
        with open(os.path.join(OUT, f"kb.{lang}.yaml"), "w", encoding="utf-8") as f:
            f.write(f"# Written by evals/_build/kb_goldens.py from evals/questions.{lang}.json and kb/{lang}/; do not edit.\n")
            yaml.safe_dump({"questions": entries}, f, allow_unicode=True, sort_keys=False, width=1000)
    with open(os.path.join(OUT, "kb.skipped.md"), "w", encoding="utf-8") as f:
        f.write("# Knowledge-base records that are not goldens\n\nWritten by `evals/_build/kb_goldens.py`; do not edit. "
                "A record is a golden only if every figure of its answer is printed on a page it names (`goldens/kb.*.yaml`). "
                f"Goldens: {counts['en']} English, {counts['ru']} Russian. Left out: {len(skipped)}.\n\n| Id | Language | Reason |\n|---|---|---|\n")
        f.writelines(f"| `{i}` | {lang} | {reason.replace('|', '/')} |\n" for i, lang, reason in skipped)
    print(f"kb goldens: en={counts['en']} ru={counts['ru']} skipped={len(skipped)}")


if __name__ == "__main__":
    main()
