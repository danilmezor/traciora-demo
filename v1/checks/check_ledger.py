# Proves that ledger.json closes (fix pass A added section 5b and 7b): derived rows against their formulas, people rows against shop and
# company rows, each story's numbers against the rows they rest on, every rate row's expected count
# against its minimum, the story cards' ledger keys, and (section 9, checks/check_files.py) every other seed file
# against the ledger, and (section 10, checks/check_kb.py) the knowledge base against the ledger. Reads cast.json, mix.json, catalogue.json, named_customers.json and vendors.json where a row
# rests on them. Not product code.
# Run: python3 checks/check_ledger.py   (writes checks/ledger_check.txt; exit code 0 only when all closes)
import glob, itertools, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))
load = lambda name: json.load(open(os.path.join(SEED, name), encoding="utf-8"))
LEDGER, CAST, MIX, CAT, NAMED, VENDORS, ACCOUNTS = (load(n) for n in ("ledger.json", "cast.json", "mix.json", "catalogue.json", "named_customers.json", "vendors.json", "accounts.json"))
ROWS = {r["key"]: r for r in LEDGER["rows"]}
SITES = ("main", "east", "west")
CHECKS = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")
WEIGHTS = dict(zip(CHECKS, (1, 2, 2, 2, 3, 3, 1, 2)))
OUT, FAILS, OPEN = [], [], []


def say(line=""):
    OUT.append(line)


def val(key, cfg):
    r = ROWS[key]
    return r["value"] if "value" in r else r[cfg]


def close(a, b, rel=0.004, ab=0.006):
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None or isinstance(a, str) or isinstance(b, str):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], rel, ab) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(close(x, y, rel, ab) for x, y in zip(a, b))
    return abs(a - b) <= max(ab, rel * abs(b))


def ok(section, name, cond, detail=""):
    say(f"  {'ok  ' if cond else 'FAIL'} {name}{': ' + detail if detail else ''}")
    if not cond:
        FAILS.append(f"{section}: {name}: {detail}")


class Cfg:
    """The functions a formula may call, for one configuration."""

    def __init__(self, cfg):
        self.cfg = cfg
        self.v = lambda key: val(key, cfg)
        self.jobs = {j["key"]: j[cfg] for j in CAT["jobs"]}
        self.ns = dict(sum=sum, min=min, max=max, len=len, round=round, abs=abs, range=range, mech_fte=self.mech_fte, shift_weight=self.shift_weight, sheet=self.sheet,
                       worst_check=self.worst_check, sum_rows=self.sum_rows, s6_counts=self.s6_counts, s7_bill=self.s7_bill, s12_brake=self.s12_brake,
                       cat_s8=self.cat_s8, cat_rec_hours=self.cat_rec_hours, cat_pad_share=self.cat_pad_share, mixv=self.mixv, season_last=self.season_last)

    def ev(self, formula):
        if isinstance(formula, dict):
            formula = formula[self.cfg]
        expr = re.sub(r"\[([A-Za-z][A-Za-z0-9_.]*)\]", lambda m: "(" + repr(self.v(m.group(1))) + ")", formula)
        return eval(expr, {"__builtins__": {}}, self.ns)

    def mech_fte(self, site):
        return round(sum(self.v(k) for k in ROWS if re.fullmatch(r"p\d\d\.share\." + site, k)), 4)

    def shift_weight(self, site):
        people = {k.split(".")[0] for k in ROWS if k.endswith(".who")}
        w = 0.0
        for p in sorted(people):
            if f"{p}.share.{site}" in ROWS:
                w += 5 * self.v(f"{p}.share.{site}")
            elif f"{p}.shifts_per_week" in ROWS and PERSON_SITE.get(p) == site:
                w += self.v(f"{p}.shifts_per_week")
        return round(w, 2)

    def sheet(self, prefix):
        lv = {c: self.v(f"{prefix}.{c}") for c in CHECKS}
        E = lambda c: (lv[c][1] + 2 * lv[c][2]) / 100
        known, price, timena, doubt, same, step1, _ = (self.v(f"calls.scenario.{k}") / 100 for k in ("customer_known", "price_asked", "time_not_applicable", "doubt_voiced", "same_rank", "step_at_level_one", "visit_at_level_two"))
        t, b = lv["offered_time"], lv["asked_for_booking"]
        ct, cb = [t[0] / 100, (t[0] + t[1]) / 100, 1.0], [b[0] / 100, (b[0] + b[1]) / 100, 1.0]
        joint, pts = {}, sorted(set(ct + cb + [0.0]))
        for lo, hi in zip(pts, pts[1:]):  # the same rank: both levels read off one quantile
            mid = (lo + hi) / 2
            key = (next(i for i, x in enumerate(ct) if mid < x), next(i for i, x in enumerate(cb) if mid < x))
            joint[key] = joint.get(key, 0) + same * (hi - lo)
        for tl, bl in itertools.product(range(3), repeat=2):
            joint[(tl, bl)] = joint.get((tl, bl), 0) + (1 - same) * t[tl] / 100 * b[bl] / 100
        total = 0.0
        for kn, pa, tn, db in itertools.product((0, 1), repeat=4):
            pc = (known if kn else 1 - known) * (price if pa else 1 - price) * (timena if tn else 1 - timena) * (doubt if db else 1 - doubt)
            for (tl, bl), pj in joint.items():
                for recap, pr in ((1, (0.0, step1, 1.0)[bl]), (0, (1.0, 1 - step1, 0.0)[bl])):
                    if not pj or not pr:
                        continue
                    num = WEIGHTS["greeting"] * E("greeting") / 2 + WEIGHTS["need_discovery"] * E("need_discovery") / 2 + WEIGHTS["asked_for_booking"] * bl / 2
                    den = WEIGHTS["greeting"] + WEIGHTS["need_discovery"] + WEIGHTS["asked_for_booking"]
                    for applies, c, level in ((not kn, "name_and_number", E("name_and_number")), (pa, "price_with_next_step", E("price_with_next_step")), (not tn, "offered_time", tl), (recap, "recap", E("recap")), (db, "objection", E("objection"))):
                        if applies:
                            num += WEIGHTS[c] * level / 2
                            den += WEIGHTS[c]
                    total += pc * pj * pr * 100 * num / den
        return round(total, 2)

    def worst_check(self, prefix):
        return min(CHECKS, key=lambda c: self.v(f"{prefix}.{c}")[1] + 2 * self.v(f"{prefix}.{c}")[2])

    def sum_rows(self, suffix):
        return sum(self.v(k) for k in ROWS if k.endswith(suffix) and re.fullmatch(r"p(\d\d|F\d)" + re.escape(suffix), k))

    def s6_counts(self):
        v = self.v
        west, share = v("s6.west_orders"), v("mix.pad_job_share") / 100
        pad = round(west * share)
        p27_orders = round(west * v("p27.billed_index") * v("p27.share.west") / v("volume.mechanic_fte.west"))
        p27_pad = round(pad * v("s6.p27_pad_share") / 100)
        p27_cheap = round(p27_pad * v("s6.cheap_share") / 100)
        others_pad = pad - p27_pad
        others_cheap = round(others_pad * v("s6.cheap_share") / 100)
        home_good = round((v("volume.orders_per_month.main") + v("volume.orders_per_month.east")) * v("time.history_months") * share)
        c = {"pad_jobs": pad, "p27_orders": p27_orders, "p27_good": p27_pad - p27_cheap, "p27_cheap": p27_cheap, "p27_other": p27_orders - p27_pad,
             "others_good": others_pad - others_cheap, "others_cheap": others_cheap}
        c["comebacks_p27_good"] = round(c["p27_good"] * v("s6.rate.good.p27") / 100)
        c["comebacks_p27_cheap"] = round(c["p27_cheap"] * v("s6.rate.cheap.p27") / 100)
        c["comebacks_others_cheap"] = round(c["others_cheap"] * v("s6.rate.cheap.others") / 100)
        c["comebacks_others_good_at_west"] = round(c["others_good"] * v("s6.rate.good.others") / 100)
        c["good_pad_jobs_not_27_all_shops"] = home_good + c["others_good"]
        c["comebacks_good_not_27_all_shops"] = round(c["good_pad_jobs_not_27_all_shops"] * v("s6.rate.good.others") / 100)
        return c

    def _job(self, key, tier="standard"):
        j = self.jobs[key]
        parts = sum(p["qty"] * next(o["list_price"] for o in p["options"] if o["tier"] == tier and not o.get("story")) for p in j["parts"])
        labour = j["labour_price"]["after_rise"]
        supplies = self.v("price.supplies.rate") / 100 * labour if j["shop_supplies"] else 0.0
        return labour, parts, supplies, j["labour_price"]["before_rise"]

    def s7_bill(self):
        il, ip, isup, _ = self._job("brake_inspection")
        bl, bp, bsup, _ = self._job("front_pads_rotors")
        sl, sp, ssup, _ = self._job("rear_shocks_pair")
        lst, declined, div = il + ip + isup + bl + bp + bsup, sl + sp + ssup, self.v("tax.vat_divisor")
        added = 1 if div > 1 else 1 + self.v("tax.rate.main") / 100  # ru: the tax is inside the list price; en: added on the bill
        return {"inspection": il + ip, "front_pads_rotors": round(bl + bp, 2), "supplies": round(isup + bsup, 2), "list_total": round(lst, 2), "before_tax": round(lst / div, 2), "tax": round(lst * added - round(lst / div, 2), 2), "with_tax": round(lst * added, 2),
                "declined_rear_shocks": round(sl + sp, 2), "declined_with_supplies": round(declined, 2), "declined_before_tax": round(declined / div, 2), "declined_with_tax": round(declined * added, 2)}

    def s12_brake(self):
        labour, parts, _, before = self._job("front_pads_rotors")
        return {"now": round(labour + parts, 2), "stale": round(before + parts, 2)}

    def cat_s8(self, field):
        return CAT["story_pins"]["S8"][self.cfg][field]

    def cat_rec_hours(self):
        w = [(j["share_of_orders"]["total"] * j["recommended_share"], j["hours"]) for j in self.jobs.values()]
        return round(sum(a * h for a, h in w) / sum(a for a, _ in w), 4)

    def cat_pad_share(self):
        return round(100 * sum(self.jobs[k]["share_of_orders"]["total"] for k in ("front_brake_pads", "front_pads_rotors", "rear_brake_pads", "rear_pads_rotors")), 2)

    def season_last(self, n):
        """The mean seasonal index of a day's orders over the n days before the nominal T (2026-11-13): each job's lead
        share times its curve on the day (mix.json seasonal), as the generator counts a day."""
        import datetime
        sea, cats = MIX["configurations"][self.cfg]["seasonal"], {j["key"]: j["category"] for j in CAT["jobs"]}

        def index(curve, d):
            if "by_month" in curve:
                return curve["by_month"][d.month - 1]
            mmdd = f"{d:%m-%d}"
            return next((w["index"] for w in curve["windows"] if w["from"] <= mmdd <= w["to"]), curve["base"])
        days = [datetime.date(2026, 11, 13) - datetime.timedelta(i) for i in range(1, n + 1)]
        return sum(j["share_of_orders"]["lead"] * index(sea["curves"][sea["job_curve"].get(k) or sea["category_curve"][cats[k]]], d) for k, j in self.jobs.items() for d in days) / n

    def mixv(self, path):
        node = MIX["configurations"][self.cfg]
        for part in path.split("."):
            node = node[part]
        return node


ADVISORS = {"main": ("p05", "p06", "p07", "p29"), "east": ("p16", "p17"), "west": ("p23", "p24")}
ANSWERERS = {"main": ("p05", "p06", "p07", "p29"), "east": ("p16", "p17"), "west": ("p22", "p23", "p24")}
MECHS = {s: sorted(k.split(".")[0] for k in ROWS if re.fullmatch(r"p\d\d\.share\." + s, k)) for s in SITES}
PERSON_SITE = {p: s for s, ps in {"main": ("p03", "p04", "p05", "p06", "p07", "p08", "p09", "p29"), "east": ("p16", "p17"), "west": ("p22", "p23", "p24")}.items() for p in ps}
DESKS = {"main": {"A1": (101, 102, 105), "A2": (101, 102, 103, 105)}, "east": {"now": (201, 202)}, "west": {"now": (301, 302, 303)}}

say("demo seed v1: ledger check")
say(f"rows: {len(ROWS)}; classes: " + ", ".join(f"{c} {sum(1 for r in ROWS.values() if r['class'] == c)}" for c in ("measured", "measured-unverified", "derived", "designed")) + "; marks: " + ", ".join(f"{m} {sum(1 for r in ROWS.values() if r['mark'] == m)}" for m in ("fixed", "scales", "rate")))

# ---------------------------------------------------------------- 0. the shape of every row
say("\n0. row shape")
bad = []
for k, r in ROWS.items():
    need = {"derived": "formula", "measured": "source", "measured-unverified": "source", "designed": "reasoning"}[r["class"]]
    if need not in r or not r.get("check") or r["mark"] not in ("fixed", "scales", "rate") or ("value" in r) == ("en" in r):
        bad.append(k)
    if r["mark"] == "rate" and not ("tolerance" in r and "min_count" in r and "n" in r):
        bad.append(k)
ok("shape", "every row has its class's field, a mark, a check; every rate row a tolerance, a minimum count and a count formula", not bad, ", ".join(bad[:8]))

for cfg in ("en", "ru"):
    C = Cfg(cfg)
    v = C.v
    say(f"\n==================== configuration {cfg} ====================")

    # ------------------------------------------------------------ 1. derived rows
    say("\n1. every derived row's formula against its stated value")
    n_ok, wrong = 0, []
    for k, r in ROWS.items():
        if r["class"] != "derived":
            continue
        stated = v(k)
        try:
            got = C.ev(r["formula"])
        except Exception as e:  # a formula that cannot be evaluated is a failure
            wrong.append(f"{k}: {type(e).__name__} {e}")
            continue
        tol = dict(rel=0.004, ab=0.3) if "sheet(" in str(r["formula"]) else dict(rel=0.004, ab=0.006)
        if close(got, stated, **tol):
            n_ok += 1
        else:
            wrong.append(f"{k}: stated {stated}, formula gives {got}")
    ok("derived", f"{n_ok} derived rows evaluate to their stated value (0.4 % or 0.006; sheet scores 0.3 points)", not wrong, "; ".join(wrong[:12]))

    # ------------------------------------------------------------ 2. orders a day from mechanics
    say("\n2. orders a day from mechanics, billed hours and hours per order")
    design_orders = {"en": (17, 11, 9), "ru": (13, 8, 7)}[cfg]  # the design table said 9 at the Russian east; the read norm of 140 to 150 gives 8
    for s, design in zip(SITES, design_orders):
        fte = sum(v(f"{p}.share.{s}") for p in MECHS[s])
        idx = sum(v(f"{p}.share.{s}") * v(f"{p}.billed_index") for p in MECHS[s])
        hours_day = idx * v(f"volume.norm.{s}") / (1 if cfg == "en" else v("site.open_days_per_month"))
        orders = hours_day / v(f"volume.hours_per_order.{s}")
        ok("mechanics", f"{s}: {len(MECHS[s])} people = {fte:.1f} full-time; indices x shares = {idx:.2f}; {hours_day:.2f} billed hours a day / {v(f'volume.hours_per_order.{s}')} = {orders:.2f} orders a day (row {v(f'volume.orders_per_day.{s}')}, in round figures {design})",
           close(fte, v(f"volume.mechanic_fte.{s}")) and abs(idx - fte) <= 0.005 and close(orders, v(f"volume.orders_per_day.{s}")) and abs(orders - design) <= 0.5)
        lo, hi = ROWS[f"volume.norm.{s}"]["range"][cfg]
        ok("mechanics", f"{s}: norm {v(f'volume.norm.{s}')} inside its accepted range {lo} to {hi}", lo <= v(f"volume.norm.{s}") <= hi)

    # ------------------------------------------------------------ 3. orders a month and revenue
    say("\n3. orders a month and revenue per shop and company")
    months, paying, revenue = {}, {}, {}
    for s in SITES:
        months[s] = v(f"volume.orders_per_day.{s}") * v("site.open_days_per_month") + (v("volume.saturday_orders.main") * v("site.saturdays_per_month") if s == "main" else 0)
        paying[s] = months[s] * (1 - v(f"comeback.{s}") / 100)
        revenue[s] = paying[s] * 12 * v(f"volume.average_order.{s}") / 1e6
        ok("volume", f"{s}: {months[s]:.1f} orders a month, {paying[s]:.1f} of them paying x average order {v(f'volume.average_order.{s}')} = {revenue[s]:.3f} million a year", close(months[s], v(f"volume.orders_per_month.{s}")) and close(revenue[s], v(f"volume.revenue_year.{s}")))
    tot, rev = sum(months.values()), sum(revenue.values())
    weighted = sum(paying[s] * v(f"volume.average_order.{s}") for s in SITES) / sum(paying.values())
    ok("volume", f"company: {tot:.1f} orders a month; {rev:.3f} million a year; shop averages weigh back to {weighted:.1f} against the company row {v('volume.average_order')}",
       close(tot, v("volume.orders_per_month.company")) and close(rev, v("volume.revenue_year.company")) and abs(weighted / v("volume.average_order") - 1) < 0.005)
    hw = sum(months[s] * v(f"volume.hours_per_order.{s}") for s in SITES) / tot
    ok("volume", f"company: shop hours per order weigh back to {hw:.3f} against {v('volume.hours_per_order')}", abs(hw / v("volume.hours_per_order") - 1) < 0.005)
    if cfg == "ru":
        ok("volume", f"revenue {rev:.1f} million RUB a year is inside the 5 % VAT band (20 to 272.5 million)", 20 < rev < 272.5)

    # ------------------------------------------------------------ 4. people rows to shop and company rows
    say("\n4. people rows summed to shop and company rows")
    sold = {}
    for s in SITES:
        shares = sum(v(f"{p}.order_share") for p in ADVISORS[s])
        sold[s] = sum(v(f"{p}.order_share") * v(f"{p}.sold_rec") for p in ADVISORS[s]) / shares
        ok("sold", f"recommended work sold, {s}: order shares sum to {shares:g}; weighted {sold[s]:.2f} % (row {v(f'sold.{s}')})", close(shares, 100) and close(sold[s], v(f"sold.{s}")))
    comp = sum(months[s] * sold[s] for s in SITES) / tot
    ok("sold", f"recommended work sold, company: {comp:.2f} % by orders a month (row {v('sold.company')})", close(comp, v("sold.company")))
    cb = {}
    for s in SITES:
        w = {p: v(f"{p}.share.{s}") * v(f"{p}.billed_index") for p in MECHS[s]}
        cb[s] = sum(w[p] * v(f"{p}.comebacks") for p in w) / sum(w.values())
        ok("comebacks", f"comebacks, {s}: {cb[s]:.2f} % by billed share (row {v(f'comeback.{s}')})", close(cb[s], v(f"comeback.{s}"), ab=0.011))
    comp = sum(months[s] * cb[s] for s in SITES) / tot
    ok("comebacks", f"comebacks, company: {comp:.2f} % (row {v('comeback.company')})", close(comp, v("comeback.company"), ab=0.011))
    score, answered = {}, {}
    for s in SITES:
        shares = sum(v(f"{p}.answered_share") for p in ANSWERERS[s])
        score[s] = sum(v(f"{p}.answered_share") * v(f"{p}.call_score") for p in ANSWERERS[s]) / shares
        answered[s] = v(f"calls.per_day.{s}") * (1 - v(f"calls.{s}.miss_w90") / 100)
        ok("scores", f"call score, {s}: answered shares sum to {shares:g}; weighted {score[s]:.2f} (row {v(f'score.{s}')})", close(shares, 100) and close(score[s], v(f"score.{s}")))
    comp = sum(answered[s] * score[s] for s in SITES) / sum(answered.values())
    ok("scores", f"call score, company: {comp:.2f} by answered calls (row {v('score.company')})", close(comp, v("score.company")))
    for p in ("p05", "p07", "p29", "p16", "p17", "p22", "p23"):
        ok("scores", f"{p}: style sheet gives {C.sheet(p + '.check')} against the row's score {v(p + '.call_score')}", abs(C.sheet(p + ".check") - v(p + ".call_score")) <= 0.5)
    for p in ("p06", "p24"):
        first, last, path = C.sheet(p + ".check.first"), C.sheet(p + ".check.last"), v(p + ".score_path")
        ok("scores", f"{p}: sheets give {first} and {last} against the first and last of the path {path}", abs(first - path[0]) <= 0.5 and abs(last - path[-1]) <= 0.5)
    miss, ms = {}, v("calls.morning_share")
    for reg, desks in DESKS["main"].items():
        ring = sum(v(f"calls.desk.{d}.{reg}.first_ring") for d in desks)
        mean = sum(v(f"calls.desk.{d}.{reg}.first_ring") * v(f"calls.desk.{d}.{reg}.factor") for d in desks) / ring
        ok("missed", f"missed calls, main, desks of regime {reg}: first-ring shares sum to {ring:g}; the share-weighted factor is {mean:.3f}, so the desks reproduce the shop's rate in every block", close(ring, 100) and abs(mean - 1) <= 0.002)
    for per, reg in (("before", "A2"), ("since", "A2")):
        mm, mr = v(f"calls.main.{per}.miss_morning"), v(f"calls.main.{per}.miss_rest")
        by_desk = {d: (v(f"calls.desk.{d}.{reg}.factor") * mm, v(f"calls.desk.{d}.{reg}.factor") * mr) for d in DESKS["main"][reg]}
        day = sum(v(f"calls.desk.{d}.{reg}.first_ring") * (ms * a + (100 - ms) * b) / 100 for d, (a, b) in by_desk.items()) / 100
        miss[per] = day
        ok("missed", f"missed calls, main, {per} the fix: desks " + ", ".join(f"{d} {a:.1f}/{b:.1f}" for d, (a, b) in by_desk.items()) + f" % (morning/rest) give {day:.2f} % over the day (row {v(f'calls.main.{per}.miss_day')}; blocks {mm} and {mr} %)", close(day, v(f"calls.main.{per}.miss_day")))
    for s in ("east", "west"):
        desks = DESKS[s]["now"]
        ring = sum(v(f"calls.desk.{d}.now.first_ring") for d in desks)
        miss[s] = sum(v(f"calls.desk.{d}.now.first_ring") * v(f"calls.desk.{d}.now.miss") for d in desks) / ring
        ok("missed", f"missed calls, {s}: first-ring shares sum to {ring:g}; desks give {miss[s]:.2f} % (row {v(f'calls.{s}.miss_w90')})", close(ring, 100) and close(miss[s], v(f"calls.{s}.miss_w90")))
    fix = v("calls.main.fix_days")
    miss["main"] = ((90 - fix) * miss["before"] + fix * miss["since"]) / 90
    ok("missed", f"missed calls, main, last 90 days: {90 - fix} days at {miss['before']:.2f} % and {fix} at {miss['since']:.2f} % = {miss['main']:.2f} % (row {v('calls.main.miss_w90')}); desk 103 alone {v('calls.desk.103.miss_w90')} %", close(miss["main"], v("calls.main.miss_w90")))
    calls = {s: v(f"calls.per_day.{s}") for s in SITES}
    comp = sum(calls[s] * miss[s] for s in SITES) / sum(calls.values())
    lo, hi, name = dict(en=(10, 21, "the measured band 10 to 21 %"), ru=(15, 17, "the measured 16 %"))[cfg]
    ok("missed", f"missed calls, company: weights are calls a day {calls['main']:.1f} : {calls['east']:.1f} : {calls['west']:.1f}; {comp:.2f} % (row {v('calls.company.miss_w90')}; {name})", close(comp, v("calls.company.miss_w90")) and lo <= comp <= hi)
    late = {}
    for s in SITES:
        pairs = [(v(f"{p}.shifts_per_week"), v(f"{p}.late")) for p, ps in PERSON_SITE.items() if ps == s] + [(5 * v(f"{p}.share.{s}"), v(f"{p}.late")) for p in MECHS[s]]
        late[s] = (sum(w * x for w, x in pairs) / sum(w for w, _ in pairs), sum(w for w, _ in pairs))
        ok("late", f"late shifts, {s}: {len(pairs)} people, {late[s][1]:g} shifts a week; {late[s][0]:.2f} % (row {v(f'late.{s}')})", close(late[s][0], v(f"late.{s}"), ab=0.011))
    comp = sum(a * w for a, w in late.values()) / sum(w for _, w in late.values())
    ok("late", f"late shifts, company: {comp:.2f} % (row {v('late.company')})", close(comp, v("late.company"), ab=0.011))

    # ------------------------------------------------------------ 5. stories
    say("\n5. each story's numbers against the rows they rest on")
    vis = {a: v(f"acct.{a}.visits") for a in ("A1", "A2", "A3", "A4", "A5", "A6")}
    money = {a: vis[a][5] * v(f"acct.{a}.average_order") for a in vis}
    a5 = v("s1.a5")
    ok("S1", f"A6 falls {vis['A6'][0]} to {vis['A6'][5]} visits; A5 is at {vis['A5'][5]}; A2 has the most visits ({vis['A2'][5]}) and A1 the most money ({money['A1']:.0f} against {money['A2']:.0f}); nobody else moves down",
       vis["A6"][0] == 8 and vis["A6"][5] in (1, 2) and vis["A5"][1:] == [1, 0, 0, 0, 0] and max(vis, key=lambda a: vis[a][5]) == "A2" and max(money, key=money.get) == "A1" and all(vis[a][5] >= vis[a][0] for a in ("A1", "A2", "A3", "A4")))
    ok("S1", f"A5: {a5['misses']} misses in {a5['miss_span_days']} days after the complaint call, no answered call after; older than the queue's {v('time.callback_queue_days')} days", a5["misses"] == 3 and a5["answered_calls_after"] == 0 and 19 * 7 > v("time.callback_queue_days") and len(a5["miss_first_desks"]) == 3)
    pay = v("acct.A1.days_to_pay")
    ok("S1", "A1 pays later: " + (f"30 days, then {pay['last_three_paid']}" if cfg == "en" else f"{pay['until']} days, then {pay['late']}") + f" against terms of {v('acct.A1.terms_days')}", (pay["last_three_paid"] == sorted(pay["last_three_paid"]) and pay["last_three_paid"][-1] > 45) if cfg == "en" else pay["late"] == 50)
    second, third = v("s2.f1.second"), v("s2.f1.third")
    ok("S2", f"three components {v('s2.f1.discount_total')} + {second['total']} + {third['total']} = {v('s2.total')}" + (" (design: 11,400 USD)" if cfg == "en" else ""), v("s2.f1.discount_total") + second["total"] + third["total"] == v("s2.total") and (cfg == "ru" or v("s2.total") == 11400))
    cash_share = 100 * v("s2.f1.cash_orders") / v("s2.f1.orders")
    ok("S2", f"F1: {v('s2.f1.discounted')} of {v('s2.f1.cash_orders')} cash orders discounted = {v('s2.f1.discount_share')} % against {v('pay.background_discount_share')} %; cash on {cash_share:.0f} % of his {v('s2.f1.orders'):.0f} orders against {v('pay.cash_share')} %",
       21 <= v("s2.f1.discount_share") <= 23 and v("s2.f1.cash_orders") < v("s2.f1.orders") and cash_share > 2 * v("pay.cash_share"))
    w = v("s2.walkin")
    after = v("s2.west.discounts_after")
    ok("S2", f"walk-in record: {w['fixed_orders']} planted + {w['background_orders_at_full_size']} background = {v('s2.walkin.total')}; by advisor {sum(w['by_advisor_at_full_size'].values())}; after the rule {after['orders']} orders, {after['unapproved_by_23']} unapproved at {after['unapproved_pct_each']} %",
       w["fixed_orders"] == v("s2.f1.discounted") + 14 and sum(w["by_advisor_at_full_size"].values()) == v("s2.walkin.total") == 240 and after["approved_by_22"] + after["unapproved_by_23"] == after["orders"] and after["unapproved_pct_each"] > v("price.discount_rule_pct"))
    if cfg == "en":
        ok("S2", f"{second['count']} voids, the till short on {third['count']} of the {third['of_days_he_closed']} days he closed it", second["count"] == 14 and third["count"] == 19 <= third["of_days_he_closed"])
    ok("S3", f"morning {v('calls.main.before.miss_morning')} % before the fix and {v('calls.main.since.miss_morning')} % since; the rest of the day {v('calls.main.since.miss_rest')} %",
       (v("calls.main.before.miss_morning"), v("calls.main.since.miss_morning"), v("calls.main.before.miss_rest"), v("calls.main.since.miss_rest")) == (31.0, 12.0, 8.0, 8.0))
    mon = v("calls.busiest_mornings_since_fix")
    mornings = v("calls.per_day.main") * v("calls.morning_share") / 100 * mon["mornings_since_fix"]
    others = 100 * (mornings * v("calls.main.since.miss_morning") / 100 - mon["missed_named"]) / (mornings - mon["calls_at_full_size"])
    ok("S3", f"{mon['weekday']}s since the fix: {mon['missed_named']} of {mon['calls_at_full_size']} = {100 * mon['missed_named'] / mon['calls_at_full_size']:.1f} %; the other mornings {others:.1f} % (row {mon['other_mornings_missed_pct']})",
       18.5 <= 100 * mon["missed_named"] / mon["calls_at_full_size"] <= 20 and abs(others - mon["other_mornings_missed_pct"]) <= 1.5)
    if cfg == "en":
        ok("S3", f"Saturday mornings are planted lower ({v('calls.saturday.main.miss')} %) than every weekday block", v("calls.saturday.main.miss") < min(v("calls.main.since.miss_rest"), v("calls.main.since.miss_morning")))
    q = v("calls.queue_at_t")
    ok("S3", f"queue at T: {sum(q[s]['waiting'] for s in SITES)} waiting, {sum(q[s]['from_today'] for s in SITES)} from today", sum(q[s]["waiting"] for s in SITES) == 9 and sum(q[s]["from_today"] for s in SITES) == 4)
    f, l, path = v("p06.sheet_expected.first"), v("p06.sheet_expected.last"), v("p06.score_path")
    mixed = [(1 - lam) * f + lam * l for lam in (0, 0.22, 0.37, 0.65, 0.87, 1)]
    ok("S4", f"her path {path} against the two sheets mixed: {[round(x, 1) for x in mixed]}; visits {v('p06.visit_agreed.first')} to {v('p06.visit_agreed.last')} %; worst check {v('p06.worst_check')}",
       all(abs(a - b) <= 0.6 for a, b in zip(path, mixed)) and (v("p06.visit_agreed.first"), v("p06.visit_agreed.last")) == (46.0, 58.0) and v("p06.worst_check") == "objection")
    ok("S5", f"east sells {v('s5.east_with_16')} % with her and {v('s5.east_without_16')} % without; {v('s5.rec_jobs_on_days_off')} recommended jobs on her days off; the diagnostician's leave cost {v('s5.leave_drop_pct')} % of two weeks",
       (v("s5.east_with_16"), v("s5.east_without_16")) == dict(en=(63.4, 52.0), ru=(71.0, 52.0))[cfg] and v("s5.rec_jobs_on_days_off") >= 100 and v("s5.week_off")["published_shifts_inside"] == v("s5.week_off")["open_requests"] == 2)
    c = v("s6.counts")
    ok("S6", f"slot 27 on good pads: {c['comebacks_p27_good']} of {c['p27_good']} ({100 * c['comebacks_p27_good'] / c['p27_good']:.1f} %); everyone else on good pads: {c['comebacks_good_not_27_all_shops']} of {c['good_pad_jobs_not_27_all_shops']} ({100 * c['comebacks_good_not_27_all_shops'] / c['good_pad_jobs_not_27_all_shops']:.1f} %): the mechanic effect",
       c["comebacks_p27_good"] >= 5 and c["p27_good"] >= 100 and c["comebacks_p27_good"] / c["p27_good"] > 2 * c["comebacks_good_not_27_all_shops"] / c["good_pad_jobs_not_27_all_shops"])
    ok("S6", f"cheap pads: his colleagues {c['comebacks_others_cheap']} of {c['others_cheap']} ({100 * c['comebacks_others_cheap'] / c['others_cheap']:.1f} %), slot 27 {c['comebacks_p27_cheap']} of {c['p27_cheap']} ({100 * c['comebacks_p27_cheap'] / c['p27_cheap']:.1f} %): the pad effect, {v('s6.pad_factor')} times for anyone",
       c["comebacks_others_cheap"] >= 5 and abs(c["comebacks_others_cheap"] / c["others_cheap"] / 0.02 - 4) <= 0.5 and abs(c["comebacks_p27_cheap"] / c["p27_cheap"] / (c["comebacks_p27_good"] / c["p27_good"]) - 4) <= 0.5)
    wt = v("s6.waiting_at_t")
    ok("S6", f"on time {v('parts.on_time.V2')} % against {v('parts.on_time.V1')} %; orders waiting over a day {v('parts.wait_over_a_day.west')} % against {v('parts.wait_over_a_day.home')} %; {len(wt['west_days'])} cars waiting at west, the longest {max(wt['west_days'])} days",
       (v("parts.on_time.V2"), v("parts.on_time.V1"), v("parts.wait_over_a_day.west"), v("parts.wait_over_a_day.home")) == (62, 93, 14, 4) and len(wt["west_days"]) == 5 and max(wt["west_days"]) == 9)
    b = v("s7.bill")
    ok("S7", f"bill {b['inspection']} + {b['front_pads_rotors']} + {b['supplies']} = {b['before_tax']} before tax, {b['with_tax']} with; declined {b['declined_rear_shocks']}; Telegram is a channel", close(b["inspection"] + b["front_pads_rotors"] + b["supplies"], b["list_total"]) and close(b["before_tax"] + b["tax"], b["with_tax"]) and (b["with_tax"] == b["list_total"]) == (cfg == "ru") and "Telegram" in v("conv.channels"))
    hours = C.jobs["timing_belt_kit"]["hours"]
    step = v("price.hour.posted") - v("price.hour.before_last_rise")
    ok("S8", f"{v('s8.price_now')} now, {v('s8.price_quoted')} before the rise ({hours} hours x {step:g}); bill {v('s8.bill_before_tax')} before tax; {v('s8.discount')} off is {v('s8.discount_pct')} % (rule: over {v('price.discount_rule_pct')} % needs approval); paid {v('s8.paid_with_tax')}",
       close(v("s8.price_now") - hours * step, v("s8.price_quoted")) and v("s8.discount_pct") > v("price.discount_rule_pct") and (cfg == "ru" or (v("s8.price_now"), v("s8.price_quoted"), round(v("s8.bill_before_tax"))) == (720.0, 688.0, 742)))
    ok("S8", f"the quote call's {v('s8.quote_call_score')} is a score the weights can give (10 of 32 points, 31.25, stored to one decimal); a complaint about an existing job and an outbound call carry none", v("s8.quote_call_score") == round(100 * 10 / 32, 1) == 31.2)
    cyc = v("s9.pattern")["slot_22_on_regular_occurrences_in_order"]
    seq = [cyc[i % len(cyc)] for i in range(22)]
    ok("S9", f"22 regular occurrences: {seq.count('declined')} declined, {seq.count('accepted, absent')} accepted and absent, {seq.count('accepted, came')} came; with the moved week he came to {seq.count('accepted, came') + 1} of 23 held",
       (seq.count("declined"), seq.count("accepted, absent"), seq.count("accepted, came")) == (8, 8, 6))
    tasks = v("s10.tasks")
    owners = [t[0] for t in tasks]
    ok("S10", f"{len(tasks)} scheduled tasks: founder {owners.count(1)}, managing owner {owners.count(2)}, senior {owners.count(4)}, junior {owners.count(6)}; none runs more than daily or by day of month", len(tasks) == 7 and (owners.count(1), owners.count(2), owners.count(4), owners.count(6)) == (1, 4, 1, 1) and all(t[2].split()[0] in ("daily", "Monday", "Friday") for t in tasks))
    if cfg == "en":
        ac = v("season.ac_curve")
        ok("S11", f"air conditioning peaks at {max(ac)} times the mean; months above 1.5: {[i + 1 for i, x in enumerate(ac) if x > 1.5]}", 2.4 <= max(ac) <= 2.6 and [i + 1 for i, x in enumerate(ac) if x > 1.5] == [5, 6, 7, 8])
    else:
        ok("S11", f"tyre windows {v('season.tyre.windows')} at {v('season.tyre.factor')} times; orders {v('season.tyre.orders_in_window')} times and calls up {v('season.tyre.calls_up_pct')} % inside a window", v("season.tyre.factor") == 6.0 and 38 <= v("season.tyre.calls_up_pct") <= 42 and v("season.tyre.windows") == [[w["from"], w["to"]] for w in MIX["configurations"]["ru"]["seasonal"]["curves"]["tyres_seasonal"]["windows"] if w["index"] == 6.0])
    br = v("s12.brake_price")
    ok("S12", f"stale pages carry the hour before the rise: timing belt {v('s8.price_quoted')} against {v('s8.price_now')}; front brakes {br['stale']} against {br['now']}", close(br["now"] - C.jobs["front_pads_rotors"]["hours"] * step, br["stale"]) and len(v("s12.pages")) == 11)
    ok("S13", f"{len(v('site.closed_dates'))} closed dates a year; the stocktake is in a published week", "W+1" in v("site.stocktake")["day"] and "W+1" in v("time.roster_weeks")["published"] and (cfg == "en" or v("site.closed_dates") == ["1 January", "2 January"]))
    rq = v("s14.requests")
    lateness = sorted(((v(k), k.split(".")[0]) for k in ROWS if re.fullmatch(r"p\d\d\.late", k)), reverse=True)
    ok("S14", f"requests {rq['approved']} + {rq['declined']} + {rq['expired']} + {rq['withdrawn']} + {rq['open']} = {rq['total']} = the people rows' {v('s14.requests_sum')}; no-shows {v('s14.no_shows_sum')}; most often late among people working now: {lateness[0][1]} ({lateness[0][0]} %), then {lateness[1][1]} ({lateness[1][0]} %); F2 was at {v('pF2.late')} %",
       rq["approved"] + rq["declined"] + rq["expired"] + rq["withdrawn"] + rq["open"] == rq["total"] == v("s14.requests_sum") == 64 and v("s14.no_shows_sum") == 8 and [x[1] for x in lateness[:2]] == ["p15", "p11"] and v("pF2.late") > lateness[0][0] and rq["open"] == v("s5.week_off")["open_requests"])
    mess = v("s15.mess")
    ok("S15", f"{mess['duplicate_pairs']} pairs and {mess['wrong_customer_orders']} orders on the wrong customer, as named_customers.json lists them", mess["duplicate_pairs"] == len(NAMED[cfg]["S15_duplicate_pairs"]) and mess["wrong_customer_orders"] == len(NAMED[cfg]["S15_car_on_the_wrong_customer"]) and len({p["shared_phone"] for p in NAMED[cfg]["S15_duplicate_pairs"]}) == 12)
    card = v("s16.card")
    ok("S16", f"card: owner {card['owner']}, helpers {card['helpers']}, the open part is slot {card['parts_open']}; due before the meeting", card["owner"] == 6 and card["helpers"] == [3, 9] and card["parts_open"] == [3] and "second" in card["due"] and "third" in card["meeting"])

    # ------------------------------------------------------------ 5b. the rows of fix pass A
    say("\n5b. tax by shop, amounts before and after tax, the rota, and the rows fix pass A accepted")
    rates = {s: v(f"tax.rate.{s}") for s in SITES}
    ok("tax", f"tax by shop {rates}; tax.rate is the home shops' rate", v("tax.rate") == rates["main"] == rates["east"] and rates == dict(en=dict(main=9.25, east=9.25, west=9.75), ru=dict(main=5.0, east=5.0, west=5.0))[cfg])
    div = v("tax.vat_divisor")
    blend = v("price.year_blend.order")
    net = {k: v(f"volume.average_order{k}") * div * (1 - v(f"comeback{k or '.company'}") / 100) / blend for k in ("", ".main", ".east", ".west")}
    parts = v("volume.parts_per_order") * div * (1 - 0.01) * (1 - v("comeback.company") / 100) / v("price.year_blend.parts")
    ok("tax", f"amounts before tax on paying orders over the last 12 months are the list amounts at today's prices / {div} / the paying share x the year's price blend ({blend} an order, {v('price.year_blend.parts')} parts): average order {v('volume.average_order')} against {v('volume.average_order_list')} at list; parts {v('volume.parts_per_order')} against {v('volume.parts_per_order_list')}; labour {v('volume.labour_per_order')}",
       all(abs(net[k] / v(f"volume.average_order_list{k}") - 1) < 0.004 for k in net) and abs(parts / v("volume.parts_per_order_list") - 1) < 0.004 and close(v("volume.labour_per_order") + v("volume.parts_per_order"), v("volume.average_order"), ab=0.2) and close(v("price.effective_rate_net") * div, v("price.effective_rate")))
    ok("tax", f"S8: {v('s8.bill_list')} at list, {v('s8.bill_before_tax')} before tax, paid {v('s8.paid_with_tax')} ({v('s8.paid_before_tax')} before tax)", close(v("s8.bill_before_tax") * div, v("s8.bill_list")) and close(v("s8.paid_before_tax") * (div if cfg == "ru" else 1 + rates["main"] / 100), v("s8.paid_with_tax")))
    if cfg == "ru":
        th, inc = v("tax.ru_thresholds"), v("tax.ru_income_2024_home")
        ok("tax", f"the two home shops took {inc} million RUB in 2024, above the {th['2025']['exempt_with_2024_income_up_to']} million under which a simplified-system company stayed exempt in 2025 and under {th['2025']['five_pct_up_to']}: the bills from {v('tax.ru_vat_from')} carry VAT at 5 %; this year's {v('volume.revenue_year.company')} million is inside the 2026 band {th['2026']['exempt_below']} to {th['2026']['five_pct_up_to']}",
           th["2025"]["exempt_with_2024_income_up_to"] < inc < th["2025"]["five_pct_up_to"] and th["2026"]["exempt_below"] < v("volume.revenue_year.company") < th["2026"]["five_pct_up_to"] and v("tax.rate") == 5.0)
        ok("tax", "the knowledge base's rows follow: VAT inside S7's bill; an account billed on terms pays the table price, VAT inside, and its documents show the amount before VAT, the VAT and the total as separate figures",
           close(v("kb.worked_answers")["vat_on_the_S7_bill"], v("s7.bill")["tax"]) and all("separate figures" in v(k) and "othing is added on top" in v(k) for k in ("kb.vat_in_list_prices", "tax.ru_price_basis")) and "tax_included true" in v("tax.ru_price_basis"))
        billed = dict(A1=13500, A2=9200, A3=10400, A4=7500, A5=12600, A6=10900)
        ok("tax", f"an account's average order before tax is what it is billed / {div}: " + ", ".join(f"{a} {v(f'acct.{a}.average_order')} of {g}" for a, g in billed.items()), all(abs(v(f"acct.{a}.average_order") * div - g) < 0.01 for a, g in billed.items()))
    pm = v("pay.mix")
    ok("pay", f"payment methods {pm} sum to 100" + ("; checks about 1 %" if cfg == "en" else ""), sum(pm.values()) == 100 and (cfg == "ru" or pm["check"] == 1))
    ok("pay", f"an ordinary day's till differs by no more than {v('pay.till_day_difference_max')} (the report line of kb.till.report_over)", v("pay.till_day_difference_max") == v("kb.till.report_over"))
    q = v("calls.queue_at_t")
    ok("S3", f"slot 6 reads main and east: {q['read_by_slot_6']} waiting callers on her list", q["read_by_slot_6"] == q["main"]["waiting"] + q["east"]["waiting"] == 5 and "east" in v("cast.also_sites")["6"] and "east" in v("cast.also_sites")["29"])
    meet = v("s9.meeting")
    hm = lambda x: int(x[:2]) * 60 + int(x[3:5])
    start = hm(re.search(r"\d\d:\d\d", meet["when"]).group(0))
    opens, block_end, call31 = hm(v("site.hours.weekday")[0]), hm(v("site.morning_block")[1]), hm(re.search(r"\d\d:\d\d", v("s3.dates")["call_31"]).group(0))
    ok("S9", f"the Monday meeting {meet['when'][:24]}: over before the home shops open at {v('site.hours.weekday')[0]}, so no lead advisor leaves the counter in the morning block and call 31 is not inside it; it starts {opens + 60 * v('geo.zone_gap_hours') - start} minutes before west opens",
       start + 30 <= opens and not (start <= call31 < start + 30) and start + 30 <= block_end and opens + 60 * v("geo.zone_gap_hours") - start == 105 and "an hour and three quarters" in meet["west_local"])
    mp, tn = v("mem.proposals"), v("mem.team_notes")
    ok("assistant", f"proposals {mp['all']}: every one of the {tn['all']} team notes rests on an approved one; {mp['declined']} declined, {mp['withdrawn']} withdrawn, {mp['waiting']} waiting; threads by person sum to {v('ask.threads')}",
       mp["approved"] == tn["all"] == 14 and mp["approved"] + mp["declined"] + mp["withdrawn"] + mp["waiting"] == mp["all"] == 19 and sum(v("ask.threads_per_person").values()) == v("ask.threads") and mp["waiting"] == 2 and v("mem.retest_days") < v("time.go_live_days") and v("sched.brief_times")["kept_rows"] == 200)
    ok("console", f"the context sync runs at {v('console.context_sync_at')}, five minutes before 'Company accounts this week'; job runs are kept {v('console.job_history_days')} days", hm(v("console.context_sync_at")) + 5 == hm(v("s10.tasks")[1][2].split()[1]) and v("console.job_history_days") == 90 and "job_failed" in v("s10.failure")["alert"])
    for k in ("erp.referral.mix", "erp.appointment.source", "erp.approval.method"):
        ok("erp", f"{k} sums to 100", sum(v(k).values()) == 100)
    est, a6 = v("erp.estimate.declined_share"), v("s1.a6")
    a6_share = 100 * a6["estimates_declined_or_expired"] / (sum(v("acct.A6.visits")[1:]) + a6["estimates_declined_or_expired"])
    ok("erp", f"declined estimates: private {est['private']} %, accounts on terms {est['accounts_on_terms']} %, A6 {a6_share:.0f} % of its last 150 days, above both", est["accounts_on_terms"] < est["private"] < a6_share)
    ot = {k: v(f"parts.on_time.{k}") for k in ("V1", "V2", "V3", "V4", "V5")}
    ok("erp", f"on-time shares {ot}: V3 to V5 between V2 and V1, and as vendors.json has them", all(ot["V2"] < ot[k] < ot["V1"] for k in ("V3", "V4", "V5")) and all(next(x for x in VENDORS[cfg] if x["id"] == k)["delivered_on_the_promised_day"] == f"{ot[k]} %" for k in ot))
    ok("erp", "statement pay days are inside each account's terms", all(d < v(f"acct.{a}.terms_days") for a, d in v("erp.statement.pay_day").items() if a != "spread"))
    bands, tv = v("calls.story_bands"), v("calls.truth_vs_verdict")
    ok("calls", f"bands of calls 33 and 34 hold the stored verdict and a judge that scores the summary 0; planted truth-against-verdict differences: calls {sorted(tv)}", bands["33"][0] <= 40.0 and 44.4 <= bands["33"][1] and bands["34"][0] <= 45.8 and 50.0 <= bands["34"][1] and sorted(tv) == dict(en=["25", "30"], ru=["25", "33"])[cfg])
    ok("S6", "call 16 carries the auto-fail dropped_customer; the fourth message is unanswered at T", "dropped_customer" in v("s6.customer_contacts")["call_16_auto_fail"] and "unanswered at T" in v("s6.customer_contacts")["replies"])
    ok("S15", "an open order is defined by status", v("s15.mess")["open_order"] == "an order whose status is not invoiced, paid, void or declined")
    import timeline_examples as tl
    for when in tl.WHEN:
        rows_, order, shift = tl.place(cfg, when)
        off = [f"{e} (slot {s_}, {d})" for e, s_, d, good in shift if not good] + [k for k, good in order if not good]
        ok("rota", f"T from {when:%a %Y-%m-%d %H:%M} (" + ("nominal" if when == tl.WHEN[0] else "awkward") + f"): {len(shift)} story events fall on a day their named person is rostered; {len(order)} order assertions hold", not off, "; ".join(off[:6]))
    if cfg == "ru":
        pat = v("roster.advisor_pattern")
        ok("rota", "the phases of timeline_examples.py are the ledger's (roster.advisor_pattern, roster.mechanic_days_off)", "6 and 29 are phase B, 5 and 7 phase A" in pat and "16 phase A, 17 phase B" in pat and "23 phase A, 24 phase B" in pat and v("roster.mechanic_days_off")["20"] == "Thu Fri" and tl.PHASE_B == (6, 29, 17, 24))

    # ------------------------------------------------------------ 6. rate rows
    say("\n6. every rate row's expected count at full size against its minimum")
    density = v("size.small.density")
    short, dropped, kept, n_rate = [], [], 0, 0
    for k, r in ROWS.items():
        if r["mark"] != "rate" or v(k) is None:
            continue
        n_rate += 1
        if r["n"] == "None":
            OPEN.append(f"{k}: {r.get('open', 'open')}")
            continue
        n = C.ev(r["n"])
        if n < r["min_count"]:
            short.append(f"{k}: {n:.0f} < {r['min_count']}")
        scales = any(ROWS[m]["mark"] == "scales" for m in re.findall(r"\[([A-Za-z][A-Za-z0-9_.]*)\]", str(r["n"])))
        if scales and n * density < r["min_count"]:
            dropped.append(k)
        else:
            kept += 1
    ok("rates", f"{n_rate} rate rows: every one with a count reaches its minimum at full size", not short, "; ".join(short[:10]))
    say(f"  at the small size (density {density}) {kept} rate rows keep their count and {len(dropped)} do not; their questions are full size only:")
    groups = {}
    for k in dropped:
        g = re.sub(r"\.check\..*", ".check.*", k)
        groups.setdefault(g, 0)
        groups[g] += 1
    for i in range(0, len(groups), 6):
        say("    " + ", ".join(list(groups)[i:i + 6]))

# ---------------------------------------------------------------- 7. the seed files beside the ledger
say("\n==================== files ====================")
say("\n7. the seed files the ledger rests on")
people = {p["slot"]: p for p in CAST["people"]}
ok("files", "cast.json holds slots 1 to 29 and F1 to F4", set(people) == {str(i) for i in range(1, 30)} | {"F1", "F2", "F3", "F4"})
ok("files", f"the founder is {people['1']['en']['full_name']} in the English configuration", people["1"]["en"]["full_name"] == "Ray Brennan" and "Walt" not in json.dumps(people["1"]["en"]))
s29 = people.get("29", {})
ok("files", "slot 29 is an advisor at main with names, a biography, a voice and an extension in both configurations", s29.get("role_key") == "service_advisor" and s29.get("site") == "main" and str(s29.get("extension")) == str(val("p29.desk", "en")) and all(s29.get(c, {}).get(f) for c in ("en", "ru") for f in ("full_name", "biography", "voice")))
need_rows = [f"p{int(s):02d}.who" for s in people if s.isdigit()] + [f"p{s}.period" for s in ("F1", "F2", "F3")] + ["pF4.billed_index"]
ok("files", "every person of the cast has ledger rows", all(k in ROWS for k in need_rows), ", ".join(k for k in need_rows if k not in ROWS))
ok("files", "every advisor's desk is the cast's extension", all(str(people[str(int(p[1:]))]["extension"]) == str(val(f"{p}.desk", "en")) for p in ("p05", "p06", "p07", "p29", "p16", "p17", "p22", "p23", "p24")) and str(people["F1"]["extension"]) == str(val("pF1.desk", "en")))
for cfg in ("en", "ru"):
    brand = CAT["story_pins"]["S6"]["brand"][cfg]
    v2 = next(x for x in VENDORS[cfg] if x["id"] == "V2")
    ok("files", f"S6's cheap pad brand is {brand} in the catalogue, the ledger and vendors.json ({cfg})", val("s6.brand", cfg) == brand == v2["house_brand"]["name"] and v2["delivered_on_the_promised_day"] == f"{val('parts.on_time.V2', cfg)} %")
for cfg in ("en", "ru"):
    accts = {a["id"]: a for a in ACCOUNTS[cfg]["accounts"]}
    ok("files", f"accounts.json ({cfg}): A1 to A6 with the ledger's vehicles, home shops and terms", sorted(accts) == ["A1", "A2", "A3", "A4", "A5", "A6"] and all(
        (a["fleet_count"], len(a["fleet"]), a["home_shop"], a["payment_terms_days"]) == (val(f"acct.{k}.vehicles", cfg), val(f"acct.{k}.vehicles", cfg), val(f"acct.{k}.shop", cfg), val(f"acct.{k}.terms_days", cfg)) for k, a in accts.items()))
say("\n7b. the snapshots fix pass A froze, against the files that stated them: a difference is a failure")
NF, ACC = (json.load(open(os.path.join(HERE, n), encoding="utf-8")) for n in ("new_facts.json", "accepted_rows.json"))
import build_new_facts
now = build_new_facts.build()
for k in ("call.en", "call.ru", "conv.en", "conv.ru"):
    moved = [x["number"] for x, y in zip(NF[k], now[k]) if x["facts"] != y["facts"]]
    rows = sum(1 for x in NF[k] if x["facts"])
    ok("new facts", f"{k}: {sum(len(x['facts']) for x in NF[k])} facts of {rows} files are what the files state now; each file with facts has its ledger row", not moved and len(NF[k]) == len(now[k]) and all(f"nf.{k.split('.')[0]}.{x['number']}" in ROWS for x in NF[k] if x["facts"]), ("changed since the snapshot: " + ", ".join(moved)) if moved else "")
    against = [f"{x['file']}: {r['as_written'][:90]}" for x in now[k] for r in x["replaced"]]
    ok("new facts", f"{k}: no file states a fact against a ledger row (tax.rate.west, tax.ru_price_basis)", not against, "; ".join(against))
    cfg = k.split(".")[1]
    invented = [x["person"]["name"] for x in NF[k] if x["person"] and x["person"]["name"] not in ("Website visitor", "Посетитель сайта")]
    ok("new facts", f"{k}: the {len(invented)} invented people are in named_customers.json", [p["name"] for p in NAMED[cfg]["story_callers" if k.startswith("call") else "story_chat_customers"]] == invented)
ok("new facts", "facts about A1 to A6 are in accounts.json", all(len(a["from_story_files"]) == sum(1 for kind in ("call", "conv") for x in NF[f"{kind}.{cfg}"] if a["id"] in x["accounts"] and x["facts"]) for cfg in ("en", "ru") for a in ACCOUNTS[cfg]["accounts"]))
proposed = json.load(open(os.path.join(SEED, "assistant", "ledger_rows.json"), encoding="utf-8"))["rows"]
ok("accepted rows", f"assistant/ledger_rows.json still proposes the {len(ACC['assistant'])} rows the ledger accepted", proposed == ACC["assistant"] and all(r["key"] in ROWS for r in ACC["assistant"]))
ok("files", "cast.json: slot 29 is posted at east as well; F4 has a worker rank", people["29"].get("also_sites") == ["east"] and people["F4"]["rank"] == "worker")
ok("files", "catalogue.json: tax by shop, VAT inside the Russian prices, parts flat from G, company-account prices not rounded again", CAT["configurations"]["en"]["tax"]["rate_by_shop"] == {s: val(f"tax.rate.{s}", "en") / 100 for s in SITES} and CAT["configurations"]["ru"]["tax"]["included_in_prices"] is True
   and "from G to T" in CAT["price_history"]["rule"]["parts, fluids, tyres, fees, sublet"] and "not rounded again" in CAT["price_history"]["rule"]["company account"] and CAT["story_pins"]["S8"]["ru"]["bill_list"] == val("s8.bill_list", "ru"))

# ---------------------------------------------------------------- 8. the story cards
say("\n8. ledger keys named by the story cards")
cards = sorted(glob.glob(os.path.join(SEED, "stories", "S[0-9][0-9].md")))
missing, named = [], 0
for path in cards:
    for line in open(path, encoding="utf-8"):
        if line.startswith("**Ledger keys"):
            for key in re.findall(r"`([^`]+)`", line):
                named += 1
                if not (key in ROWS or key.endswith(".*") and any(k.startswith(key[:-1]) for k in ROWS)):
                    missing.append(f"{os.path.basename(path)}: {key}")
ok("cards", f"{len(cards)} cards name {named} ledger keys; every one exists", len(cards) == 16 and named > 0 and not missing, "; ".join(missing[:10]))
SECTIONS = ("**Path:**", "## Who", "## When", "## Footprints", "## Ledger keys", "## Questions")
lacking = [f"{os.path.basename(p)}: {sec}" for p in cards for sec in SECTIONS if sec not in open(p, encoding="utf-8").read()]
ok("cards", "every card has its path, who, when, footprints, ledger keys and questions", not lacking, "; ".join(lacking[:8]))
sys.path.insert(0, HERE)
import build_story_index as index
qs = index.questions()
malformed = [q["#"] for q in qs if q["Kind"] not in index.KINDS or q["Small"] not in ("yes", "no") or not re.match(r"\d+ \(", q["Asked by"]) or not q["Expected"] or not q["Proof"] or not q["Population, period, definition"]]
ok("cards", f"{len(qs)} questions: each names its asker and rank, its population and period, an expected answer, its proof, a kind and the small size", not malformed, ", ".join(malformed[:10]))
readme = open(os.path.join(SEED, "stories", "README.md"), encoding="utf-8").read()
ok("cards", "stories/README.md lists every question", all(f"| {q['#']} |" in readme for q in qs) and f"| all | {len(qs)} |" in readme)
say("  questions by kind: " + ", ".join(f"{k} {sum(1 for q in qs if q['Kind'] == k)}" for k in index.KINDS) + f"; kept at the small size {sum(1 for q in qs if q['Small'] == 'yes')} of {len(qs)}")

# ---------------------------------------------------------------- 9. every other seed file against the ledger
say("\n9. the seed files beside the ledger: a difference is a failure")
import check_files
check_files.run(say, ok)

# ---------------------------------------------------------------- 10. the knowledge base against the ledger
say("\n10. the knowledge base (kb/): a difference from the ledger or the seed files is a failure")
import check_kb
check_kb.run(say, ok)

say("\n==================== result ====================")
if OPEN:  # a rate row with no expected count cannot be proved: it is a failure, not a note
    for line in sorted(set(OPEN)):
        FAILS.append("rate row with no expected count: " + line)
say("nothing is printed here as a note: every rate row has its expected count, and every seed file, the knowledge base included, agrees with the ledger or fails above")
say(f"\n{'ALL CLOSES' if not FAILS else 'DOES NOT CLOSE'}: {len(FAILS)} failure(s)")
for line in FAILS:
    say("  " + line)
text = "\n".join(OUT) + "\n"
open(os.path.join(HERE, "ledger_check.txt"), "w", encoding="utf-8").write(text)
sys.stdout.write(text)
sys.exit(1 if FAILS else 0)
