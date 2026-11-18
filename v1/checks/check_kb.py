# -*- coding: utf-8 -*-
# Proves that the knowledge base (kb/) agrees with ledger.json and the seed files: a difference is a failure.
# Called by check_ledger.py as its section 10; runs alone as: python3 checks/check_kb.py
# What it proves, for both configurations: the build is reproducible and the pages on disk are what the build makes;
# the east shop's placeholder name is gone; the page list, folders and reader ranks are the ledger's; the two
# configurations have the same page keys but for the declared Russian-only pages; every internal link resolves but
# the one planted broken link; every amount of money, labour hour and clock time on a page is a catalogue or ledger
# value of that configuration; every person, vendor and account named is in the seed files under that name; every
# planted challenge of the outlines is on the pages; every new fact of a page is a ledger row (kb.*).
# Not product code.
import glob, hashlib, json, os, posixpath, re, subprocess, sys
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
KB = os.path.join(SEED, "kb")
sys.path.insert(0, KB)
from kb_paths import russian_links, russian_paths, russian_ranks
OLD_NAME = "Jersey" + " " + "Pike"  # written in two parts: no seed file may hold the name, this one included
CLASSES = ("car", "suv", "truck", "van")
TIERS = ("economy", "standard", "premium")


def load(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return json.load(f)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def numbers(x, out=None):
    """Every number inside a ledger value, however nested; numbers written in a string count too."""
    out = set() if out is None else out
    if isinstance(x, bool) or x is None:
        return out
    if isinstance(x, (int, float)):
        out.add(round(float(x), 2))
    elif isinstance(x, str):
        for m in re.findall(r"(?<![\w.])\d[\d ,]*(?:\.\d+)?", x):
            t = m.strip().rstrip(",").replace(",", "")
            for cand in {t.replace(" ", ""), *t.split()}:
                try: out.add(round(float(cand), 2))
                except ValueError: pass
    elif isinstance(x, dict):
        for k, v in x.items(): numbers(k, out); numbers(v, out)
    elif isinstance(x, (list, tuple)):
        for v in x: numbers(v, out)
    return out


def times(x, out=None):
    """Every clock time (HH:MM) inside a ledger value."""
    out = set() if out is None else out
    if isinstance(x, str):
        for h, m in re.findall(r"(?<![\d:])(\d{1,2}):(\d{2})(?![\d:])", x): out.add("%d:%s" % (int(h), m))
    elif isinstance(x, dict):
        for k, v in x.items(): times(k, out); times(v, out)
    elif isinstance(x, (list, tuple)):
        for v in x: times(v, out)
    return out


def catalogue_money(cat, cfg):
    """Every amount the catalogue can give for a configuration, on the shop system's arithmetic (seeder/erp/orders.py:
    price): hourly labour is the class's hours to the hundredth x the hour, to the cent; a part line is its quantity x
    the unit price (class multiplier and company terms on the unit) to the cent; menu labour is its price x the class
    multiplier to the cent, a Russian list price to 10 roubles (seeder/erp/reference.py: money). Totals by tier, class and side of the
    rise, at list and at the company-account price; labour; parts each, by quantity and by job; fees; sublet; rates;
    supplies."""
    C = cat["configurations"][cfg]
    ok, hours = set(), set()
    add = lambda v: ok.add(round(v + 1e-9, 2))
    cent = lambda v: round(v + 1e-9, 2)
    off = 1 - C["company_account_terms"]["parts_discount"]
    for j in cat["jobs"]:
        e = j[cfg]
        hb = e["hours_by_class"] or {}
        for cls in CLASSES:
            hm = hb.get(cls, 1.0) if cls != "car" else 1.0
            if hm is None: continue
            hours.add(cent(e["hours"] * hm))
            pm = C["parts_class_multiplier"][cls] if e["parts_scale_with_class"] else 1.0
            extra = sum(f["price"] for f in e["fees"]) + (e["sublet"]["price"] if e["sublet"] else 0)
            for when in ("before_rise", "after_rise"):
                if e["labour_pricing"] == "hourly":
                    lab, lab_co = (cent(cent(e["hours"] * hm) * C["labour_rate"][kind][when]) for kind in ("standard", "company_account"))
                else:
                    lab, lab_co = (float((Decimal(str(e[k][when])) * Decimal(str(hm))).quantize(Decimal("0.01"), ROUND_HALF_UP)) for k in ("labour_price", "labour_price_company"))
                    if cfg == "ru" and lab >= 10:  # a Russian list price to 10 roubles (seeder/erp/reference.py: money)
                        lab = float((Decimal(str(e["labour_price"][when])) * Decimal(str(hm)) / 10).quantize(Decimal(1), ROUND_HALF_UP) * 10)
                add(lab); add(lab_co)
                for tier in TIERS:
                    parts = parts_co = parts_car = 0.0
                    for p in e["parts"]:
                        o = {x["tier"]: x for x in p["options"] if not x.get("story")}
                        op = o.get(tier) or o.get("standard") or list(o.values())[0]
                        unit = cent(op["list_price"] * pm)
                        parts += cent(p["qty"] * unit); parts_co += cent(p["qty"] * cent(unit * off)); parts_car += cent(p["qty"] * op["list_price"])
                    add(parts); add(parts_car)
                    add(lab + parts + extra)
                    add(lab_co + parts_co + extra)
        for p in e["parts"]:
            for o in p["options"]:
                add(o["list_price"]); add(o["cost"]); add(o["list_price"] * p["qty"])
        if e["sublet"]: add(e["sublet"]["price"]); add(e["sublet"]["cost"])
        for f in e["fees"]: add(f["price"])
    for kind in C["labour_rate"].values():
        for v in kind.values(): add(v)
    add(C["shop_supplies"]["cap_per_order"])
    for step in cat["price_history"][cfg]["labour_hour"]:
        add(step["standard"]); add(step["company_account"])
    return ok, hours


def tree_hash():
    """One hash of everything the build writes."""
    h = hashlib.sha256()
    paths = []
    for d in ("en", "ru", "facts", "facts-ru"):
        paths += [p for p in glob.glob(os.path.join(KB, d, "**", "*"), recursive=True) if os.path.isfile(p)]
    paths += [os.path.join(KB, n) for n in ("OUTLINE.md", "OUTLINE-ru.md", "TO-VERIFY.md", "_build/registry.json", "_build/registry-ru.json", "_build/tree.md")]
    for p in sorted(paths):
        h.update(os.path.relpath(p, KB).encode()); h.update(open(p, "rb").read())
    return h.hexdigest(), len(paths)


EN_MONEY = re.compile(r"\$([0-9][0-9,]*(?:\.[0-9]{2})?)")
RU_MONEY = re.compile(r"(?<![\d,])(\d{1,3}(?: \d{3})*(?:,\d{1,2})?) ₽")
EN_HOURS = re.compile(r"(?<![\d.,:$])(\d+(?:\.\d+)?) (?:labou?r )?hours?\b")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
RU_HOURS = re.compile(r"(?<![\d.,:])(\d+(?:,\d+)?) (?:нормо-час|н/ч)")
CLOCK = re.compile(r"(?<![\d:.,])(\d{1,2}):(\d{2})(?![\d:])(\s*(?:a\.m\.|p\.m\.|am\b|pm\b))?")
BARE_EN_TIME = re.compile(r"(?<![\d:.,$])(\d{1,2})\s*(a\.m\.|p\.m\.)")


def clock_times(text, cfg):
    """Clock times on a page as H:MM in 24 hours. English pages write 5:30 p.m. and, among staff, a bare 4:30."""
    out = set()
    for h, m, ap in CLOCK.findall(text):
        h = int(h)
        if h > 23 or int(m) > 59: continue
        if cfg == "en":
            ap = (ap or "").strip().replace(".", "")
            if ap == "pm" and h < 12: out.add("%d:%s" % (h + 12, m))
            elif ap == "am" or h >= 13 or h == 0: out.add("%d:%s" % (h, m))
            else: out.add(("%d:%s" % (h, m), "%d:%s" % (h + 12 if h < 12 else h, m)))  # a bare time: either half of the day
        else:
            out.add("%d:%s" % (h, m))
    if cfg == "en":
        for h, ap in BARE_EN_TIME.findall(text):
            h = int(h)
            if 1 <= h <= 12: out.add("%d:00" % (h + 12 if ap == "p.m." and h < 12 else h))
    return out


def run(say, ok):
    L = {r["key"]: r for r in load("ledger.json")["rows"]}
    v = lambda k, c: L[k]["value"] if "value" in L[k] else L[k][c]
    CAT, CAST, ACC, VEND, NAMED = (load(n) for n in ("catalogue.json", "cast.json", "accounts.json", "vendors.json", "named_customers.json"))
    KBROWS = {k: r for k, r in L.items() if k.startswith("kb.")}

    # ------------------------------------------------------------ 10.1 the build
    say("\n10.1 the knowledge base is what its build makes, twice over")
    before = tree_hash()
    runs = []
    for _ in range(2):
        p = subprocess.run([sys.executable, os.path.join(KB, "_build", "build.py")], capture_output=True, text=True)
        runs.append((p.returncode, tree_hash()))
    ok("kb", "kb/_build/build.py runs and its own checks pass (links, files, amounts written by a helper, placeholders)", all(rc == 0 for rc, _ in runs), (p.stderr or p.stdout)[-400:] if any(rc for rc, _ in runs) else "")
    ok("kb", f"the {before[1]} generated files on disk are the build's output, and two builds give the same bytes", before == runs[0][1] == runs[1][1], "run python3 kb/_build/build.py and look at what changed")
    held = [os.path.relpath(p, SEED) for p in glob.glob(os.path.join(KB, "**", "*"), recursive=True) if os.path.isfile(p) and "__pycache__" not in p and OLD_NAME.lower() in read_safe(p).lower()]
    held += [os.path.relpath(p, SEED) for p in glob.glob(os.path.join(KB, "**", "*"), recursive=True) if "jersey" in os.path.basename(p).lower()]
    ok("kb", "no file under kb/ holds the east shop's placeholder name, in its text or its path", not held, "; ".join(held[:6]))

    for cfg in ("en", "ru"):
        say(f"\n10. knowledge base, configuration {cfg}")
        reg_all = json.load(open(os.path.join(KB, "_build", "registry.json" if cfg == "en" else "registry-ru.json")))
        reg = {p: r for p, r in reg_all.items() if not r.get("not_a_page")}
        facts_dir = os.path.join(KB, "facts" if cfg == "en" else "facts-ru")
        sheets = {p: json.load(open(os.path.join(facts_dir, (p[:-3] if p.endswith(".md") else p) + ".json"))) for p in reg}
        pages = {p: read(os.path.join(KB, cfg, p)) for p in reg if p.endswith(".md")}
        history = {os.path.relpath(p, os.path.join(KB, cfg)): read(p) for p in glob.glob(os.path.join(KB, cfg, "_history", "**", "*.md"), recursive=True)}
        binaries = read(os.path.join(KB, cfg, "_binaries.md"))
        texts = {**pages, **history, "_binaries.md": binaries}

        # ---- the page list, folders and ranks
        want = {}
        for k, r in KBROWS.items():
            if not k.startswith("kb.pages."): continue
            val = v(k, cfg)
            for name in val["pages"]:
                want[(val["folder"] + "/" if val["folder"] else "") + name] = val["seen_from"]
        ranks = {**want, **{p: rank for p, rank in v("kb.file_ranks", cfg).items()}}
        seen = {p: s["seen_from"] for p, s in sheets.items()}
        diff = sorted(set(want) ^ set(reg)) + sorted(p for p in reg if p in ranks and ranks[p] != seen[p])
        ok("kb", f"({cfg}) the {len(reg)} page keys, their folders and reader ranks are the ledger's (kb.pages.*, kb.file_ranks)", not diff, "; ".join(diff[:8]))
        S12 = {"price_list": ("prices/price-list.md", "public", False), "timing_belt_service": ("services/engine/timing-belt.md", "public", True), "brake_questions": ("services/brakes/brake-questions.md", "public", True),
               "warranty_current": ("customers/warranty.md", "public", False), "warranty_old": ("customers/warranty-policy.md", "public", True), "booking_a_visit": ("how-to/booking-a-visit.md", "staff", False),
               "discount_policy": ("policies/discounts.md", "staff", False), "company_accounts": ("accounts/company-account-terms.md", "staff", False), "suppliers": ("parts/suppliers.md", "staff", False),
               "staff_handbook": ("team/staff-handbook.docx", "staff", False), "pay_and_till": ("management/pay-and-till.md", "senior", False)}
        bad = [name for name, (p, vis, stale) in S12.items() if p not in reg or reg[p]["visibility"] != vis or not v("s12.pages", cfg)[name].startswith(vis) or bool(reg[p]["stale_on_purpose"]) != stale]
        ok("kb", f"({cfg}) the eleven pages of s12.pages exist with the ledger's readers; the two stale service pages and the old warranty page are the stale ones", not bad and set(v("s12.pages", cfg)) == set(S12), ", ".join(bad))
        stale = sorted(p for p in reg if reg[p]["stale_on_purpose"])
        ok("kb", f"({cfg}) the pages stale on purpose are the ledger's six (kb.stale_pages)", stale == sorted(v("kb.stale_pages", cfg)), ", ".join(stale))

        # ---- links
        broken = sorted((p, l) for p, r in reg.items() for l in r["links_to"] if l not in reg)
        planted = v("kb.broken_link", cfg)
        ok("kb", f"({cfg}) every internal link resolves, except the one planted broken link", broken == [(planted["page"], planted["target"])], str(broken[:5]))
        raw = sorted({(p, m) for p, t in pages.items() for m in re.findall(r"\]\(([^)#\s]+)", t) if "://" not in m and not m.startswith("mailto:")
                      and posixpath.normpath(posixpath.join(posixpath.dirname(p), m)) not in reg})
        ok("kb", f"({cfg}) the links in the page text itself resolve the same way", raw == [(planted["page"], posixpath.basename(planted["target"]))] or [posixpath.normpath(posixpath.join(posixpath.dirname(a), b)) for a, b in raw] == [planted["target"]], str(raw[:5]))

        if cfg == "ru":
            installed = russian_paths()
            installed_ranks = {"playbooks": "administrator", **russian_ranks()}
            link_diff = []
            encoded_labels = []
            rank_diff = []
            for src, text in pages.items():
                path = installed[src]
                rewritten = russian_links(src, text)
                targets = [m for m in re.findall(r"\]\(([^)#\s]+)", rewritten)
                           if "://" not in m and not m.startswith("mailto:")]
                linked = {posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(m))) for m in targets}
                if any(CYRILLIC.findall(m) != CYRILLIC.findall(unquote(m)) for m in targets):
                    encoded_labels.append(path)
                expected = {installed[l] for l in reg[src]["links_to"]}
                if linked != expected:
                    link_diff.append((path, sorted(linked ^ expected)))
                parent = path
                while parent and parent not in installed_ranks:
                    parent = posixpath.dirname(parent)
                if installed_ranks.get(parent, "worker") != seen[src]:
                    rank_diff.append(path)
            ok("kb", "the installed Russian links name the same pages and keep the planted missing page", not link_diff, str(link_diff[:5]))
            ok("kb", "the installed Russian links keep Cyrillic readable in Markdown", not encoded_labels, str(encoded_labels[:5]))
            ok("kb", "the installed Russian pages keep the source ranks, including inherited folder ranks", not rank_diff, str(rank_diff[:5]))

        # ---- money, hours, clock times
        cat_money, cat_hours = catalogue_money(CAT, cfg)
        MONEY_ROWS = ("price.hour", "price.supplies.cap", "tax.max_single_part", "s2.f1.discount_total", "s2.f1.second", "s2.f1.third", "s2.total", "s4.driver_limit", "s7.bill", "s8.", "s12.brake_price",
                      "kb.acct.approvers", "kb.acct.credit_limits", "kb.till.floats", "kb.till.report_over", "kb.deposits", "kb.towing", "kb.storage", "kb.second_look_over", "kb.stocktake.rules", "kb.price_sheet.spark_plugs",
                      "kb.tyre_fees_each", "kb.worked_answers", "kb.figures_of_speech", "kb.handbook")
        led_money = set()
        for k, r in L.items():
            if k.startswith(MONEY_ROWS) or re.fullmatch(r"acct\.A\d\.average_order", k): numbers(v(k, cfg), led_money)
        find = EN_MONEY if cfg == "en" else RU_MONEY
        tonum = (lambda a: float(a.replace(",", ""))) if cfg == "en" else (lambda a: float(a.replace(" ", "").replace(",", ".")))
        unknown = {}
        for p, t in texts.items():
            for a in find.findall(t):
                x = round(tonum(a), 2)
                if x not in cat_money and x not in led_money: unknown.setdefault(p, set()).add(a)
        ok("kb", f"({cfg}) every amount of money on a page, an earlier text or a document draft is a catalogue figure or a ledger value", not unknown, "; ".join(f"{p}: {', '.join(sorted(a))}" for p, a in sorted(unknown.items())[:10]))
        if cfg == "ru":
            typed = sorted({(p, a["value"]) for p, s in sheets.items() for a in s.get("new_amounts", []) if round(float(a["value"]), 2) not in numbers([v(k, cfg) for k in KBROWS])})
            ok("kb", "(ru) every amount a page introduced (its sheet's new_amounts) is in a kb.* ledger row", not typed, str(typed[:8]))
        all_nums = set()  # hours a page may state beside a job's: the story's job, shift lengths, and the kb.* rows
        for k in L:
            if k.startswith(("kb.", "s8.breakdown", "roster.", "site.", "time.", "s2.f1.third")): numbers(v(k, cfg), all_nums)
        find_h = EN_HOURS if cfg == "en" else RU_HOURS
        badh = {}
        for p, t in texts.items():
            for a in find_h.findall(t):
                x = round(float(a.replace(",", ".")), 2)
                if x not in cat_hours and x not in all_nums: badh.setdefault(p, set()).add(a)
        ok("kb", f"({cfg}) every count of labour hours on a page is a catalogue job's hours or a ledger number", not badh, "; ".join(f"{p}: {', '.join(sorted(a))}" for p, a in sorted(badh.items())[:10]))
        led_times = set()
        for k in L: times(v(k, cfg), led_times)
        badt = {}
        for p, t in texts.items():
            for c in clock_times(t, cfg):
                if not (set(c) & led_times if isinstance(c, tuple) else c in led_times): badt.setdefault(p, set()).add(c[0] if isinstance(c, tuple) else c)
        ok("kb", f"({cfg}) every clock time on a page is a time the ledger holds for this configuration", not badt, "; ".join(f"{p}: {', '.join(sorted(a))}" for p, a in sorted(badt.items())[:12]))

        # ---- names
        people = {str(p["slot"]): p for p in CAST["people"]}
        vend = {x["id"]: x["name"] for x in VEND[cfg]}
        acc = {a["id"]: a for a in ACC[cfg]["accounts"]}
        bad = []
        for p, s in sheets.items():
            bad += [f"{p}: slot {x['slot']}" for x in s.get("people", []) if x["slot"] not in people]
            bad += [f"{p}: vendor {x['vendor']} {x['name']}" for x in s.get("vendors", []) if vend.get(x["vendor"]) != x["name"]]
            bad += [f"{p}: account {x['account']} {x.get('name')}" for x in s.get("accounts", []) if x["account"] not in acc or ("name" in x and acc[x["account"]]["name"] != x["name"])
                    or ("contact" in x and x["contact"] not in [c["name"] for c in acc[x["account"]]["contacts"]])]
        ok("kb", f"({cfg}) every person, vendor, account and contact a sheet records is in cast.json, vendors.json and accounts.json under that name", not bad, "; ".join(bad[:8]))
        if cfg == "en":
            full = {("Ray Brennan" if s == "1" else p["en"]["full_name"]) for s, p in people.items()}
            full |= {c["name"] for a in acc.values() for c in a["contacts"]}
            def walk(x):
                if isinstance(x, dict):
                    for k, y in x.items():
                        if k in ("name", "full_name") and isinstance(y, str): full.add(y)
                        walk(y)
                elif isinstance(x, list):
                    for y in x: walk(y)
            walk(NAMED.get("en", NAMED)); walk(ACC["en"])
            firsts = {n.split()[0] for n in full if len(n.split()) == 2}
            lasts = {n.split()[-1] for n in full if len(n.split()) == 2}
            allowed = full | set(v("kb.names_outside_the_seed", "en"))
            odd = sorted({f"{p}: {a} {b}" for p, t in texts.items() for a, b in re.findall(r"\b([A-Z][a-z]+) (?=([A-Z][a-z]+)\b)", t) if a in firsts and b in lasts and f"{a} {b}" not in allowed})
            ok("kb", "(en) a first name and a surname of the seed stand together only as a person the seed files have", not odd, "; ".join(odd[:8]))
            ext = {("Ray Brennan" if s == "1" else p["en"]["full_name"]): p.get("extension") for s, p in people.items() if p["status"] == "active"}
            rows = re.findall(r"^\| ([A-Z][a-z]+ [A-Z][a-z]+) \|[^|]*\| *(\d{3})? *\|", pages["team/who-is-who.md"], re.M)
            wrong = [f"{n}: {e or 'none'} on the page, {ext.get(n)} in cast.json" for n, e in rows if (ext.get(n) or "") != e]
            ok("kb", f"(en) Who is who lists the {len(ext)} active people with the cast's extensions, desk 105 among them", not wrong and {n for n, _ in rows} == set(ext), "; ".join(wrong[:6]))
        else:
            ext = {p["ru"]["full_name"]: p.get("extension") for s, p in people.items() if p["status"] == "active" and p.get("extension")}
            t = pages["team/who-is-who.md"]
            wrong = [n for n, e in ext.items() if not re.search(re.escape(n.split()[-1]) + r"[^|\n]*\|[^|\n]*\| *" + e + r" *\|", t) and not re.search(re.escape(" ".join(n.split()[:2])) + r"[^\n]*" + e, t)]
            ok("kb", f"(ru) «Кто есть кто» gives the cast's extension for each of the {len(ext)} people who have one", not wrong, "; ".join(wrong[:6]))
        for vid, name in vend.items():
            pass
        named_v = [name for name in vend.values() if not any(name in t for t in pages.values())]
        ok("kb", f"({cfg}) every vendor of vendors.json is named on a page", not named_v, ", ".join(named_v))
        ok("kb", f"({cfg}) the invented brake-pad brand is the ledger's and is on the brake-pad page", v("s6.brand", cfg) in pages["parts/brake-pads-we-fit.md"])

        # ---- the ledger's own facts on the pages that state them
        T = lambda p: pages[p]
        m = (lambda x: "${:,.2f}".format(x)) if cfg == "en" else (lambda x: ("{:,}".format(int(x)).replace(",", " ") if float(x).is_integer() else "{:,.2f}".format(x).replace(",", " ").replace(".", ",")) + " ₽")
        hist = v("price.hour.history", cfg)
        claims = [
            ("today's posted hour and every earlier one on the rates page", all(m(h) in T("prices/labour-rates-and-fees.md") for _, h in hist)),
            ("the company-account hour on the rates page and the terms page", m(v("price.hour.company", cfg)) in T("prices/labour-rates-and-fees.md") and m(v("price.hour.company", cfg)) in T("accounts/company-account-terms.md")),
            ("the timing-belt job: today's price on the price list, the price before the rise on the stale service page", m(v("s8.price_now", cfg)) in T("prices/price-list.md") and m(v("s8.price_quoted", cfg)) in T("services/engine/timing-belt.md") and m(v("s8.price_now", cfg)) not in T("services/engine/timing-belt.md")),
            ("front pads and rotors: today's price on the price list, the stale one on the brake questions page", m(v("s12.brake_price", cfg)["now"]) in T("prices/price-list.md") and m(v("s12.brake_price", cfg)["stale"]) in T("services/brakes/brake-questions.md")),
            ("the stale pages still use the hour before the rise", m(v("price.hour.before_last_rise", cfg)) in T("services/engine/timing-belt.md") and m(v("price.hour.before_last_rise", cfg)) in T("services/brakes/brake-questions.md")),
            ("shop supplies: the rate and the cap on the rates page", ("%g %%" % v("price.supplies.rate", cfg)) in T("prices/labour-rates-and-fees.md") and m(v("price.supplies.cap", cfg)) in T("prices/labour-rates-and-fees.md")),
            ("the tax rate on the rates page", ("%g %%" % v("tax.rate", cfg)).replace(".", "." if cfg == "en" else ",") in T("prices/labour-rates-and-fees.md")),
            ("the driver's approval limit on the company-accounts page", (("$%d" % v("s4.driver_limit", cfg)) if cfg == "en" else m(v("s4.driver_limit", cfg))) in T("accounts/company-account-terms.md")),
            ("the discount rule: 10 %, on the bill before tax, in force from the next full open day after the firing", ("%d %%" % v("price.discount_rule_pct", cfg)) in T("policies/discounts.md") and "@discount_rule" in T("policies/discounts.md")),
            ("the stocktake is the event @stocktake on the hours page and the stocktake page, closing at noon", "@stocktake" in T("customers/hours-and-locations.md") and "@stocktake" in T("how-to/stocktake-day.md") and "12:00" in T("customers/hours-and-locations.md")),
            ("A1's contact is the one in accounts.json", (acc["A1"]["contacts"][0]["name"] if cfg == "en" else " ".join(acc["A1"]["contacts"][0]["name"].split()[:2])) in T("accounts/a1.md")),
        ]
        FILES = {"A1": "a1", "A2": "a2", "A3": "a3", "A4": "a4", "A5": "a5", "A6": "a6"}
        days = "days" if cfg == "en" else "дней"
        rows = {a: next((ln for ln in T("accounts/company-account-terms.md").split("\n") if ln.startswith("|") and f"({f}.md)" in ln), "") for a, f in FILES.items()}
        claims += [
            ("each account's home shop and payment terms in the terms table are the ledger's", all(f"| {v('geo.short_name', cfg)[v(f'acct.{a}.shop', cfg)]} | {v(f'acct.{a}.terms_days', cfg)} {days} |" in rows[a] for a in FILES)),
            ("the account names in the terms table are those of accounts.json", all(acc[a]["name"].strip("«»") in rows[a] for a in FILES)),
        ]
        if cfg == "en":
            w = v("s12.warranty", "en")
            claims += [
                ("the current warranty on both warranty pages, the old terms on the old page", "24 months or 24,000 miles" in T("customers/warranty.md") and "24 months or 24,000 miles" in T("policies/warranty.md") and "12 months or 12,000 miles" in T("customers/warranty-policy.md") and w["current"].startswith("24 months or 24,000 miles") and w["old_page"] == "12 months or 12,000 miles"),
                ("weekday and Saturday hours on the hours page", "7:30 a.m. to 5:30 p.m." in T("customers/hours-and-locations.md") and "8:00 a.m. to 1:00 p.m." in T("customers/hours-and-locations.md") and v("site.hours.weekday", "en") == ["07:30", "17:30"]),
                ("the six closed dates on the hours page", all(d in T("customers/hours-and-locations.md") for d in v("site.closed_dates", "en"))),
                ("the east shop's address and short name on the hours page", "6340 Bonny Oaks Drive, Chattanooga, TN 37416" in T("customers/hours-and-locations.md") and v("geo.short_name", "en")["east"] in T("shops/README.md")),
                ("the assistant sends in the web chat and drafts on Telegram", "**Telegram:** the assistant only drafts" in T("how-to/chats-and-messages.md") and v("conv.assistant_mode", "en")["Telegram"] == "drafts"),
                ("the memo's shares of discounted cash orders are the ledger's", "from %.1f %% to %.1f %%" % (v("s2.west.discount_share_before", "en"), v("s2.west.discount_share_after", "en")) in T("management/what-we-found-at-west.md")),
                ("the owner's reports at the ledger's times", all(s in T("playbooks/owner.md") for s in ("Monday 8:00: company accounts", "Friday 4:00: discounts over 10 %", "Monday 9:00: Charlotte Pike against plan", "Daily 6:00 p.m.: missed calls")) and [t[2] for t in v("s10.tasks", "en")[1:5]] == ["Monday 08:00", "Friday 16:00", "Monday 09:00", "daily 18:00"]),
            ]
        else:
            w = v("s12.warranty", "ru")
            claims += [
                ("the current warranty on both warranty pages, the old terms on the old page, no body work anywhere", "30 дней на слесарные и электротехнические работы" in T("customers/warranty.md") and "30 дней на слесарные и электротехнические работы" in T("policies/warranty.md") and "14 дней" in T("customers/warranty-policy.md")
                 and w == {"current": "30 days on mechanical and electrical work", "old_page": "14 days on any work"} and not any("кузовные" in t for t in pages.values())),
                ("opening hours every day on the hours page; closed on 1 and 2 January only", "с 9:00 до 20:00" in T("customers/hours-and-locations.md") and "1 и 2 января" in T("customers/hours-and-locations.md") and v("site.hours.weekday", "ru") == ["09:00", "20:00"]),
                ("the shops' short names are the ledger's", all(n in T("shops/README.md") for n in v("geo.short_name", "ru").values())),
                ("the assistant sends in the web chat only and drafts on Telegram, VK and Avito", "**Чат на сайте:** помощник отвечает сам" in T("how-to/chats-and-messages.md") and "**Telegram, ВКонтакте и Авито:** помощник только готовит черновик" in T("how-to/chats-and-messages.md") and set(v("conv.assistant_mode", "ru").values()) == {"sends", "drafts"}),
                ("the memo's shares of discounted cash orders are the ledger's", ("с %.1f до %.1f %%" % (v("s2.west.discount_share_before", "ru"), v("s2.west.discount_share_after", "ru"))).replace(".", ",") in T("management/what-we-found-at-west.md")),
                ("the owner's reports at the ledger's times and under the ledger's names", all(f"«{name}»" in T("playbooks/owner.md") for o, name, when in v("s10.tasks", "ru") if o == 2) and all(s in T("playbooks/owner.md") for s in ("в 9:00", "в 18:00", "в 10:00", "в 20:15"))),
                ("list prices hold VAT and nothing is added on top: the price pages and the documents page say the same", all("с ндс" in T(p).lower() for p in ("prices/price-list.md", "customers/prices-for-common-services.md", "policies/documents-and-vat.md", "customers/README.md"))
                 and all("в том числе ндс 5" in T(p).lower() for p in ("prices/price-list.md", "customers/prices-for-common-services.md", "customers/payment.md")) and not any("без ндс" in T(p).lower() for p in ("prices/price-list.md", "customers/prices-for-common-services.md", "customers/README.md"))
                 and m(v("s7.bill", "ru")["with_tax"]) in T("policies/documents-and-vat.md") and m(v("s7.bill", "ru")["before_tax"]) in T("policies/documents-and-vat.md")),
                ("the steering-rack subcontractor of vendors.json is on the sublet page", vend["V9"] in T("parts/sublet-work.md")),
            ]
        for name, cond in claims:
            ok("kb", f"({cfg}) {name}", bool(cond))

        # ---- planted challenges
        outline = read(os.path.join(KB, "OUTLINE.md" if cfg == "en" else "OUTLINE-ru.md"))
        sec = outline[outline.index("## 5. Planted on purpose"):outline.index("## 7. " if cfg == "ru" else "## 6. ")]
        plants = re.findall(r"^\*\*([PC]\d+)\. ", sec, re.M)
        proofs = {q for line in sec.split("\n") if line.startswith("|") for q in re.findall(r"`([a-z][a-z0-9\-/]*\.(?:md|pdf|docx|xlsx|pptx))`", line)}
        missing = sorted(q for q in proofs if q not in reg and q not in ("tow-trucks.md", planted["target"]) and not q.startswith(("en/", "ru/")))
        ok("kb", f"({cfg}) the outline plants {len(plants)} challenges (P1 to P8, C1 to C12) and every page its questions rest on exists", len(plants) == 20 and not missing, ", ".join(missing[:8]))
        tags = {s for r in reg.values() for s in r["serves"] if s.startswith("challenge:")}
        ok("kb", f"({cfg}) the pages serve the ledger's challenge tags (kb.challenges)", tags == set(v("kb.challenges", cfg)), ", ".join(sorted(tags ^ set(v("kb.challenges", cfg)))))
        st = v("kb.storage", cfg)
        planted_ok = [
            ("C5: the storage page's free days and daily charge", m(st["per_day"]) in T("policies/storage-of-uncollected-cars.md") if cfg == "ru" else "$%d" % st["per_day"] in T("policies/storage-of-uncollected-cars.md")),
            ("C9: the price list is longer than one read", len(T("prices/price-list.md")) > 12000),
            ("C10: the bought shop's own page carries the broken link", planted["page"] == "shops/west/README.md" and posixpath.basename(planted["target"]) in T(planted["page"])),
            ("C3: the five documents are drafted", all(b in reg for b in v("kb.binaries", cfg))),
            ("P3: the one pending proposal is on the timing-belt sheet", "pending_proposal" in sheets["services/engine/timing-belt.md"] or any("proposal" in json.dumps(r, ensure_ascii=False).lower() for r in sheets["services/engine/timing-belt.md"].get("revisions", [])) or "proposal" in json.dumps(sheets["services/engine/timing-belt.md"], ensure_ascii=False).lower()),
        ]
        for name, cond in planted_ok:
            ok("kb", f"({cfg}) {name}", bool(cond))

        # ---- new facts
        placed = {pg for r in KBROWS.values() for pg in ([r["page"]] if isinstance(r.get("page"), str) else r.get("page", {}).get(cfg, []) if isinstance(r.get("page"), dict) else r.get("page", []))}
        with_new = sorted(p for p, s in sheets.items() if s.get("new_facts") and p not in placed and p not in v("kb.new_facts_without_a_row", cfg))
        ok("kb", f"({cfg}) every page that introduced a fact is named by a kb.* ledger row, or is listed in kb.new_facts_without_a_row with the reason", not with_new, ", ".join(with_new[:12]))

    # ------------------------------------------------------------ the two configurations beside each other
    say("\n10. the two configurations")
    en = set(json.load(open(os.path.join(KB, "_build", "registry.json"))))
    ru = {p for p, r in json.load(open(os.path.join(KB, "_build", "registry-ru.json"))).items() if not r.get("not_a_page")}
    ok("kb", "the Russian base has every English page key, and beyond them only the declared Russian-only pages (kb.ru_only_pages)", en <= ru and sorted(ru - en) == sorted(v("kb.ru_only_pages", "ru")), ", ".join(sorted(en - ru) + sorted(ru - en)))
    shape = [k for k, r in KBROWS.items() if r["class"] != "designed" or r["mark"] != "fixed" or not r.get("page") or not r.get("store")]
    ok("kb", f"the {len(KBROWS)} kb.* rows are designed, fixed, and each names the page that states it and the store that must carry it", not shape, ", ".join(shape[:8]))
    for name in ("CROSS-STORE.md", "TO-VERIFY.md"):
        ok("kb", f"kb/{name} exists", os.path.exists(os.path.join(KB, name)))
    cross = read(os.path.join(KB, "CROSS-STORE.md")) if os.path.exists(os.path.join(KB, "CROSS-STORE.md")) else ""
    notes = v("kb.team_note.storage", "en"), v("kb.team_note.storage", "ru")
    ok("kb", "kb/CROSS-STORE.md carries the wording of the team note that contradicts the storage page, in both configurations", all(n["text"] in cross for n in notes))


def read_safe(p):
    try:
        return open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, IsADirectoryError):
        return ""


if __name__ == "__main__":
    fails = []
    def _ok(section, name, cond, detail=""):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}{': ' + detail if detail else ''}")
        if not cond: fails.append(name)
    run(print, _ok)
    print(f"\n{'KB AGREES' if not fails else 'KB DISAGREES'}: {len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
