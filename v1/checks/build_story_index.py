# Authoring helper: reads the question tables of stories/S01.md to S16.md and writes the table of all
# questions, with counts by kind, into stories/README.md between its two markers. Not product code.
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STORIES = os.path.normpath(os.path.join(HERE, "..", "stories"))
KINDS = ("value", "list", "explanation", "action", "nothing", "cannot tell", "refusal", "smoke", "stale")


def questions():
    out = []
    for path in sorted(glob.glob(os.path.join(STORIES, "S[0-9][0-9].md"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        title = lines[0].lstrip("# ").strip()
        start = next(i for i, l in enumerate(lines) if l.startswith("| # | Question |"))
        head = [c.strip() for c in lines[start].strip("|").split("|")]
        for l in lines[start + 2:]:
            if not l.startswith("|"):
                break
            cells = [c.strip() for c in l.strip().strip("|").split("|")]
            assert len(cells) == len(head), (path, l[:60])
            row = dict(zip(head, cells))
            row["story"] = title
            out.append(row)
    return out


def table(rows):
    md = ["| # | Story | Question | Asked by | Kind | Small size |", "|---|---|---|---|---|---|"]
    for r in rows:
        q = re.sub(r"\s*\((old|the date is typed|ru):[^)]*\)", "", r["Question"])
        md.append(f"| {r['#']} | {r['story'].split('.', 1)[1].strip()} | {q} | {r['Asked by']} | {r['Kind']} | {r['Small']} |")
    counts = {k: sum(1 for r in rows if r["Kind"] == k) for k in KINDS}
    small = sum(1 for r in rows if r["Small"] == "yes")
    md += ["", f"{len(rows)} questions in {len({r['story'] for r in rows})} cards; the small size keeps {small} and drops {len(rows) - small}.", "", "| Kind | Questions |", "|---|---:|"]
    md += [f"| {k} | {v} |" for k, v in counts.items()] + [f"| all | {len(rows)} |"]
    return "\n".join(md)


if __name__ == "__main__":
    rows = questions()
    bad = [r["#"] for r in rows if r["Kind"] not in KINDS or r["Small"] not in ("yes", "no") or not re.match(r"\d+ \(", r["Asked by"])]
    if bad:
        sys.exit("malformed question rows: " + ", ".join(bad))
    p = os.path.join(STORIES, "README.md")
    s = open(p, encoding="utf-8").read()
    a, b = s.index("<!-- questions:start -->"), s.index("<!-- questions:end -->")
    open(p, "w", encoding="utf-8").write(s[:a] + "<!-- questions:start -->\n" + table(rows) + "\n" + s[b:])
    print(len(rows), "questions")
