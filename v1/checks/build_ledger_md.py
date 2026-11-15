# -*- coding: utf-8 -*-
# Writes ledger.md: the parameter ledger as a document to read, generated from ledger.json. Never edit ledger.md by
# hand: change a row in checks/build_ledger.py, run it, then run this. check_files.py fails when ledger.md is not
# what this script makes of ledger.json. Not product code. Run: python3 checks/build_ledger_md.py
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
GROUPS = [  # title, key prefixes; a row goes to the first group that claims it
 ("Geography and time", ("geo.", "time.")), ("Sites, hours, closed dates", ("site.",)), ("Roster patterns", ("roster.",)),
 ("Volume: orders, hours, average order, revenue", ("volume.",)), ("Prices and tax", ("price.", "tax.")),
 ("What the catalogue and the mix give", ("mix.",)), ("Rows the mix file proposed, with the decision on each", ("mixrow.",)), ("Rows other files proposed, with the decision on each", ("proposed.",)),
 ("Sums of the people rows: sold work, comebacks, lateness, call scores", ("sold.", "comeback.", "late.", "score.")),
 ("Calls", ("calls.",)), ("Unclear customers (rule R13)", ("r13.",)), ("Conversations", ("conv.",)), ("Task board", ("board.",)),
 ("Company accounts (story S1)", ("acct.", "s1.")), ("Payments, the walk-in record, the till (story S2)", ("pay.", "s2.")), ("Parts and suppliers (story S6)", ("parts.", "s6.")),
 ("Seasons (story S11)", ("season.",)), ("Story rows", ("s3.", "s4.", "s5.", "s7.", "s8.", "s9.", "s10.", "s12.", "s13.", "s14.", "s15.", "s16.")), ("The small size (rule R7)", ("size.",)),
 ("The knowledge base: its tree, and every fact its pages introduced (kb/)", ("kb.",)),
 ("The shop-system generator's background numbers (erp/generator-spec.md section 11)", ("erp.",)),
 ("The assistant side: Ask threads, memory, scheduled tasks and briefs (assistant/)", ("ask.", "mem.", "sched.")),
 ("The working day: punches, calendar, Inbox, console; postings (workday/, tenant/)", ("punch.", "calendar.", "inbox.", "console.", "cast.")),
 ("New facts of the story calls and the story conversations, one row per file", ("nf.",)),
]
SHOPS = (("main", "Flagship (`main`)"), ("east", "`east`"), ("west", "`west`"), ("none", "Owners and former staff"))
ADV_COLS = ("desk", "shifts_per_week", "order_share", "sold_rec", "answered_share", "call_score", "first_reply_min", "late", "absent", "no_shows", "requests", "tasks_on_time", "wrong_promise", "dropped_customer", "callback_not_kept")
MECH_COLS = ("billed_index", "comebacks", "late", "forgot_clock_out", "absent", "no_shows", "requests")
CHECKS = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")


def cell(x):
    if isinstance(x, float): x = ("%g" % x) if abs(x) < 1e6 else "{:,.0f}".format(x)
    elif isinstance(x, (dict, list)): x = json.dumps(x, ensure_ascii=False)
    elif x is None: x = "none"
    elif x is True or x is False: x = "yes" if x else "no"
    return str(x).replace("|", "\\|").replace("\n", " ")


def values(r):
    if "value" in r: return cell(r["value"]), None
    return cell(r["en"]), cell(r["ru"])


def both(r):
    a, b = values(r)
    return a if b is None or a == b else f"{a} / {b}"


def mark(r):
    if r.get("outcome"): return r["mark"] + ", outcome: measured by the build"
    if r["mark"] != "rate": return r["mark"]
    tol = "±%g" % r["tolerance"] + (" " + r["tolerance_unit"] if r.get("tolerance_unit") else "")
    return f"rate, {tol}, at least {r['min_count']} cases"


def basis(r):
    if r["class"] == "derived":
        f = r["formula"]
        return "= " + (cell(f) if not isinstance(f, dict) else "en: " + str(f["en"]) + "; ru: " + str(f["ru"])).replace("|", "\\|")
    s = r.get("source") or r.get("reasoning") or ""
    if r.get("range"): s += " Range " + cell(r["range"]) + "."
    if r.get("decision"): s = f"[{r['decision']}] " + s
    return cell(s)


def table(rows):
    out = ["| Key | English | Russian | Unit | Class | Mark | Stories | Basis: formula, source or reasoning | How the seeded data is checked |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        a, b = values(r)
        out.append("| `%s` | %s | %s | %s | %s | %s | %s | %s | %s |" % (r["key"], a, "same" if b is None or b == a else b, cell(r.get("unit", "")), r["class"], mark(r), " ".join(r["stories"]), basis(r), cell(r["check"])))
    return "\n".join(out)


def render():
    led = json.load(open(os.path.join(SEED, "ledger.json"), encoding="utf-8"))
    cast = json.load(open(os.path.join(SEED, "cast.json"), encoding="utf-8"))
    rows = led["rows"]
    R = {r["key"]: r for r in rows}
    person = {("p%02d" % int(p["slot"]) if p["slot"].isdigit() else "p" + p["slot"]): p for p in cast["people"]}
    is_person = lambda k: re.match(r"p(\d\d|F\d)\.", k)
    n = len(rows)
    by = lambda f: ", ".join("%s %d" % (x, sum(1 for r in rows if r[f] == x)) for x in sorted({r[f] for r in rows}))
    out = ["# Demo seed v1: the parameter ledger", "",
           "Generated from `ledger.json` by `checks/build_ledger_md.py`. Do not edit this file: change the row in `checks/build_ledger.py`, run it, run `checks/check_ledger.py`, then run the generator again.", "",
           f"{n} rows. By class: {by('class')}. By mark: {by('mark')}.", "",
           "- **Class** says where a value comes from: *measured* (a source that was read), *measured-unverified* (a source still to be read), *derived* (a formula over other rows, recomputed by the check), *designed* (chosen, with its reasoning and range).",
           "- **Mark** says what happens to it when the data is built: *fixed* (a planted instance, the same in both sizes), *scales* (grows with the density of the build), *rate* (a share or a mean, with its tolerance and the number of cases it needs to be readable).",
           "- Where the English and the Russian configuration hold the same value the Russian column says \"same\". Percentages are per cent numbers. `[key]` in a formula is another row's value.",
           "- Notation: " + "; ".join(f"**{k}**: {v}" for k, v in led["_meta"]["notation"].items()) + ".", ""]
    used = set()
    for title, prefixes in GROUPS:
        grp = [r for r in rows if r["key"].startswith(prefixes) and not is_person(r["key"])]
        used |= {r["key"] for r in grp}
        out += [f"## {title}", "", f"{len(grp)} rows.", "", table(grp), ""]
    # people, per shop
    out += ["## People", "", "One row per person in each shop's table; a cell with two values is English / Russian. The class, mark and tolerance of each column are in the table that follows the shops'. Names are `cast.json`'s.", "",
            "Where a person's base is too small for a rate, the cell is a count of planted instances since G (rule R7): the wrong promises of slots 17 and 22, the dropped customers of slot 22, the callbacks not kept of slots 16 and 29, and slot 7's two wrong promises.", ""]
    prow = [r for r in rows if is_person(r["key"])]
    used |= {r["key"] for r in prow}
    def val(p, a):
        r = R.get(f"{p}.{a}")
        return both(r) if r else ""
    def name(p):
        x = person[p]
        return "%s / %s" % (x["en"]["full_name"], x["ru"]["full_name"])
    shown = set()
    for site, label in SHOPS:
        ps = [p for p in person if (person[p]["site"] == site) or (site == "none" and (person[p]["status"] != "active" or person[p]["site"] == "none"))]
        if site != "none": ps = [p for p in ps if person[p]["status"] == "active"]
        adv = [p for p in ps if f"{p}.answered_share" in R]
        mech = [p for p in ps if f"{p}.billed_index" in R and f"{p}.who" in R and p not in adv]
        rest = [p for p in ps if p not in adv and p not in mech]
        out += [f"### {label}", ""]
        if adv:
            out += ["Advisors and whoever answers the desk phones.", "", "| Slot | Name | Who | " + " | ".join(c.replace("_", " ") for c in ADV_COLS) + " |", "|---|---|---|" + "---|" * len(ADV_COLS)]
            for p in adv:
                out.append("| %s | %s | %s | %s |" % (p[1:].lstrip("0"), name(p), val(p, "who"), " | ".join(val(p, c) for c in ADV_COLS)))
                shown |= {f"{p}.{c}" for c in ADV_COLS + ("who",)}
            out += ["", "Style sheets: % of scored calls at level 0 / 1 / 2 on each check, and the sheet's expected mean score.", "", "| Slot | Sheet | " + " | ".join(c.replace("_", " ") for c in CHECKS) + " | expected |", "|---|---|" + "---|" * (len(CHECKS) + 1)]
            for p in adv:
                for ph in ("", ".first", ".last"):
                    if f"{p}.check{ph}.greeting" in R:
                        out.append("| %s | %s | %s | %s |" % (p[1:].lstrip("0"), {"": "the last 90 days", ".first": "first period", ".last": "last period"}[ph], " | ".join("/".join(str(x) for x in R[f"{p}.check{ph}.{c}"]["value"]) for c in CHECKS), val(p, f"sheet_expected{ph}")))
                        shown |= {f"{p}.check{ph}.{c}" for c in CHECKS} | {f"{p}.sheet_expected{ph}"}
            out.append("")
        if mech:
            out += ["Mechanics.", "", "| Slot | Name | Who | share of a full-time mechanic | " + " | ".join(c.replace("_", " ") for c in MECH_COLS) + " |", "|---|---|---|---|" + "---|" * len(MECH_COLS)]
            for p in mech:
                shares = ", ".join("%s %s" % (s, cell(R[f"{p}.share.{s}"]["value"])) for s in ("main", "east", "west") if f"{p}.share.{s}" in R)
                out.append("| %s | %s | %s | %s | %s |" % (p[1:].lstrip("0"), name(p), val(p, "who"), shares, " | ".join(val(p, c) for c in MECH_COLS)))
                shown |= {f"{p}.{c}" for c in MECH_COLS + ("who", "share.main", "share.east", "share.west")}
            out.append("")
        other = [r for r in prow if r["key"].split(".")[0] in ps and r["key"] not in shown]
        if other:
            out += ["Other rows of these people.", "", table(other), ""]
            shown |= {r["key"] for r in other}
    cols = {}
    for r in prow:
        a = r["key"].split(".", 1)[1]
        a = re.sub(r"^check(\.first|\.last)?\..*", "check.*", a)
        if a in ADV_COLS + MECH_COLS + ("check.*",) and a not in cols: cols[a] = r
    out += ["### The columns of the people tables", "", "| Column | Unit | Class | Mark | Basis | How the seeded data is checked |", "|---|---|---|---|---|---|"]
    for a, r in cols.items():
        out.append("| %s | %s | %s | %s | %s | %s |" % (a.replace("_", " "), cell(r.get("unit", "")), r["class"], mark(r), basis(r), cell(r["check"])))
    out.append("")
    left = [r for r in rows if r["key"] not in used]
    if left: out += ["## Rows outside the groups above", "", table(left), ""]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    s = render()
    open(os.path.join(SEED, "ledger.md"), "w", encoding="utf-8").write(s)
    print("ledger.md", len(s.split("\n")), "lines")
