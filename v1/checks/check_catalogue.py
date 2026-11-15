#!/usr/bin/env python3
"""Check catalogue.json, parc.json and mix.json of demo seed v1 against the parameter ledger.

Reads the three files beside this folder and prints, per configuration, what the catalogue, the parc
and the mix give when multiplied out, next to the ledger's target and the deviation in percent: the
company rows, each shop's hours and average order at its own sold share, and the price history.
The targets in mix.json (ledger_targets) are ledger rows; checks/check_files.py proves they are equal.
Run: python3 checks/check_catalogue.py   (exit code 1 when a row misses its tolerance)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOL = 0.02
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
TIERS = ("economy", "standard", "premium")


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


def class_shares(parc_cfg):
    out = {}
    for m in parc_cfg["models"]:
        out[m["vehicle_class"]] = out.get(m["vehicle_class"], 0.0) + m["share"]
    total = sum(out.values())
    return {k: v / total for k, v in out.items()}


def class_factor(mult, shares):
    """Mean multiplier over the classes the job is offered for (None = not offered)."""
    if not mult:
        return 1.0
    offered = {k: v for k, v in mult.items() if v is not None}
    weight = sum(shares[k] for k in offered)
    return sum(shares[k] * v for k, v in offered.items()) / weight


def parts_value(job, tier_mix, field):
    """Tier-weighted parts money of one job at class 'car'. Story-only options are left out."""
    total = 0.0
    for slot in job["parts"]:
        by_tier = {}
        for opt in slot["options"]:
            if opt.get("story"):
                continue
            by_tier.setdefault(opt["tier"], opt)
        fallback = by_tier.get("standard") or next(iter(by_tier.values()))
        total += slot["qty"] * sum(tier_mix[t] * by_tier.get(t, fallback)[field] for t in TIERS)
    return total


def job_money(job, cfg_cat, mix_cfg, shares, when="after_rise"):
    hf = class_factor(job["hours_by_class"], shares)
    pf = 1.0
    if job["parts_scale_with_class"]:
        offered = [k for k, v in (job["hours_by_class"] or shares).items() if v is not None]
        pf = class_factor({k: cfg_cat["parts_class_multiplier"][k] for k in offered}, shares)
    labour = job["labour_price"][when] * hf
    parts = parts_value(job, mix_cfg["tier_mix"], "list_price") * pf
    cost = parts_value(job, mix_cfg["tier_mix"], "cost") * pf
    fees = sum(f["price"] for f in job["fees"])
    sublet = job["sublet"]["price"] if job["sublet"] else 0.0
    sup = cfg_cat["shop_supplies"]
    supplies = min(sup["rate_of_hourly_labour"] * labour, sup["cap_per_order"]) if job["labour_pricing"] == "hourly" else 0.0
    return dict(hours=job["hours"] * hf, labour=labour, parts=parts, parts_cost=cost, fees=fees, sublet=sublet,
                supplies=supplies)


def curve_by_day(curve):
    days = []
    if "by_month" in curve:
        for m, n in enumerate(DAYS):
            days += [curve["by_month"][m]] * n
        return days
    starts = [sum(DAYS[:m]) for m in range(12)]

    def doy(mmdd):
        mm, dd = mmdd.split("-")
        return starts[int(mm) - 1] + int(dd) - 1

    days = [curve["base"]] * 365
    for w in curve["windows"]:
        for d in range(doy(w["from"]), doy(w["to"]) + 1):
            days[d] = w["index"]
    return days


def by_month(days):
    out, i = [], 0
    for n in DAYS:
        out.append(sum(days[i:i + n]) / n)
        i += n
    return out


def age_stats(parc_cfg):
    """Age of a drawn car: model by share, then age by age_weights inside the model's years."""
    ref = parc_cfg["reference_year"]
    per_age = {}
    for b in parc_cfg["age_weights"]:
        n = b["age_to"] - b["age_from"] + 1
        for a in range(b["age_from"], b["age_to"] + 1):
            per_age[a] = b["weight"] / n
    dist, ok = {}, True
    for m in parc_cfg["models"]:
        ages = [a for a in per_age if m["year_from"] <= ref - a <= m["year_to"]]
        w = sum(per_age[a] for a in ages)
        if not ages or w <= 0:
            ok = False
            continue
        for a in ages:
            dist[a] = dist.get(a, 0.0) + m["share"] * per_age[a] / w
        for e in m["engines"]:
            lo = e["year_from"] or m["year_from"]
            hi = e["year_to"] or m["year_to"]
            if lo < m["year_from"] or hi > m["year_to"] or lo > hi:
                ok = False
    total = sum(dist.values())
    dist = {a: p / total for a, p in dist.items()}
    mean = sum(a * p for a, p in dist.items())
    older = sum(p for a, p in dist.items() if a > 10)
    return mean, older, ok, dist


def metrics(cat, parc, mix, cfg):
    c = cat["configurations"][cfg]
    mx = mix["configurations"][cfg]
    shares = class_shares(parc["configurations"][cfg])
    r = mx["realisation"]
    factor = (1 - r["company_account_share_of_sales"] * r["company_account_discount"]) * (1 - r["discounts_and_coupons"]) * (1 - r["warranty_and_goodwill"])
    tot = dict(hours=0.0, labour=0.0, parts=0.0, parts_cost=0.0, fees=0.0, sublet=0.0, supplies=0.0)
    before_labour = 0.0
    rev_cat, lead_cat, lines_cat = {}, {}, {}
    lead_sum = priced = rec_sold = rec_value = rec_hours = 0.0
    for job in cat["jobs"]:
        j = job[cfg]
        p = j["share_of_orders"]["total"]
        m = job_money(j, c, mx, shares)
        for k in tot:
            tot[k] += p * m[k]
        before_labour += p * job_money(j, c, mx, shares, "before_rise")["labour"]
        value = m["labour"] + m["parts"] + m["fees"] + m["sublet"] + m["supplies"]
        k = job["category"]
        rev_cat[k] = rev_cat.get(k, 0.0) + p * value
        lead_cat[k] = lead_cat.get(k, 0.0) + j["share_of_orders"]["lead"]
        lead_sum += j["share_of_orders"]["lead"]
        if j["counts_as_priced_job"]:
            priced += p
            lines_cat[k] = lines_cat.get(k, 0.0) + p
        rec_sold += p * j["recommended_share"]
        rec_value += p * j["recommended_share"] * value
        rec_hours += p * j["recommended_share"] * m["hours"]
    non_labour_list = tot["parts"] + tot["fees"] + tot["sublet"] + tot["supplies"]
    labour = tot["labour"] * factor
    non_labour = non_labour_list * factor
    rev_total = sum(rev_cat.values())
    # seasonal
    curves = {n: curve_by_day(cv) for n, cv in mx["seasonal"]["curves"].items()}
    total_days = [0.0] * 365
    cat_days = {k: [0.0] * 365 for k in lead_cat}
    for job in cat["jobs"]:
        lead = job[cfg]["share_of_orders"]["lead"]
        if not lead:
            continue
        name = mx["seasonal"]["job_curve"].get(job["key"], mx["seasonal"]["category_curve"][job["category"]])
        for d in range(365):
            total_days[d] += lead * curves[name][d]
            cat_days[job["category"]][d] += lead * curves[name][d] / lead_cat[job["category"]]
    jpo = mx["jobs_per_order"]["distribution"]
    mean_age, older10, parc_ok, age_dist = age_stats(parc["configurations"][cfg])
    s8 = next(j for j in cat["jobs"] if j["key"] == "timing_belt_kit")[cfg]
    s8_parts = sum(s["qty"] * next(o for o in s["options"] if o["tier"] == "standard")["list_price"] for s in s8["parts"])
    global s8h
    s8h = s8["labour_price"]["history"]
    return dict(
        shares=shares, factor=factor, hours=tot["hours"], labour=labour, non_labour=non_labour,
        order=labour + non_labour, labour_list=tot["labour"], labour_before=before_labour * factor,
        parts_list=tot["parts"], parts_cost=tot["parts_cost"], fees=tot["fees"], sublet=tot["sublet"],
        supplies=tot["supplies"], elr=labour / (tot["hours"] * c["labour_rate"]["standard"]["after_rise"]),
        parts_margin=1 - tot["parts_cost"] / tot["parts"],
        revenue_share={k: v / rev_total for k, v in rev_cat.items()}, lead_share=lead_cat,
        lines_share={k: v / priced for k, v in lines_cat.items()}, lead_sum=lead_sum, priced_jobs=priced,
        jpo_mean=sum(int(k) * v for k, v in jpo.items()), jpo_sum=sum(jpo.values()),
        rec_sold=rec_sold, rec_value=rec_value / rec_sold, rec_hours=rec_hours / rec_sold,
        curve_means={n: sum(d) / 365 for n, d in curves.items()}, curve_peaks={n: max(by_month(d)) for n, d in curves.items()},
        curve_day_peaks={n: max(d) for n, d in curves.items()},
        total_by_month=by_month(total_days), cat_by_month={k: by_month(d) for k, d in cat_days.items()},
        total_mean=sum(total_days) / 365, total_day_peak=max(total_days), mean_age=mean_age, older10=older10,
        parc_ok=parc_ok, age_dist=age_dist,
        s8_price=s8["labour_price"]["after_rise"] + s8_parts, s8_old_by_rule=s8["labour_price"]["before_rise"] + s8_parts,
        s8_supplies=c["shop_supplies"]["rate_of_hourly_labour"] * s8["labour_price"]["after_rise"],
    )


class Report:
    def __init__(self):
        self.lines, self.failed, self.gaps = [], 0, 0

    def head(self, text):
        self.lines += ["", text, "-" * len(text)]

    def row(self, label, got, target, tol=TOL, unit="", absolute=False):
        dev = (got - target) if absolute else (got / target - 1) * 100
        ok = abs(dev) <= (tol if absolute else tol * 100) + 1e-9
        self.failed += 0 if ok else 1
        devtxt = ("%+.3f abs" % dev) if absolute else ("%+.2f %%" % dev)
        self.lines.append("  %-52s %12s %12s %12s  %s" % (label, fmt(got) + unit, fmt(target) + unit, devtxt, "ok" if ok else "MISS"))

    def info(self, label, text):
        self.lines.append("  %-52s %s" % (label, text))

    def flag(self, label, ok, text, reported_gap=False):
        if not ok and reported_gap:
            self.gaps += 1
        else:
            self.failed += 0 if ok else 1
        self.lines.append("  %-52s %s  %s" % (label, text, "ok" if ok else ("GAP (reported, see catalogue.md)" if reported_gap else "MISS")))


def fmt(x):
    if abs(x) >= 1000:
        return "{:,.0f}".format(x)
    if abs(x) >= 20:
        return "%.1f" % x
    return "%.3f" % x


def season_means(months):
    def avg(idx):
        return sum(months[i] * DAYS[i] for i in idx) / sum(DAYS[i] for i in idx)
    return dict(winter=avg([11, 0, 1]), spring=avg([2, 3, 4]), summer=avg([5, 6, 7]), autumn=avg([8, 9, 10]))


def main():
    cat, parc, mix = load("catalogue.json"), load("parc.json"), load("mix.json")
    rep = Report()
    rep.lines.append("demo seed v1: catalogue, parc and mix against the parameter ledger (tolerance %.0f %%)" % (TOL * 100))
    rep.lines.append("columns: computed, target, deviation")
    for cfg in ("en", "ru"):
        m = metrics(cat, parc, mix, cfg)
        mx = mix["configurations"][cfg]
        c = cat["configurations"][cfg]
        t = mx["ledger_targets"]
        cur = " " + c["currency"]
        rep.head("%s configuration (%s)" % ("English" if cfg == "en" else "Russian", c["currency"]))
        rep.info("vehicle classes of the parc", ", ".join("%s %.1f %%" % (k, v * 100) for k, v in sorted(m["shares"].items())))
        rep.row("billed hours per order", m["hours"], t["billed_hours_per_order"])
        rep.row("labour per order", m["labour"], t["labour_per_order"], unit=cur)
        rep.row("parts and other non-labour per order", m["non_labour"], t["parts_per_order"], unit=cur)
        rep.row("average order, before tax", m["order"], t["average_order"], unit=cur)
        for s in ("main", "east", "west"):  # a shop differs from the company by the recommended work its advisors sell
            more = m["rec_sold"] * (t["recommended_work_sold_by_shop"][s] / mx["recommended_work"]["sold_share"] - 1)
            rep.row("  %s, sold share %.2f %%: billed hours per order" % (s, 100 * t["recommended_work_sold_by_shop"][s]), m["hours"] + more * m["rec_hours"], t["billed_hours_per_order_by_shop"][s])
            rep.row("  %s: average order, before tax" % s, m["order"] + more * m["rec_value"] * m["factor"], t["average_order_by_shop"][s], unit=cur)
        if "effective_labour_rate" in t:
            rep.row("effective labour rate, share of posted", m["elr"], t["effective_labour_rate"])
        rep.info("  of non-labour at list: parts / fees / sublet / supplies", "%s / %s / %s / %s" % (fmt(m["parts_list"]), fmt(m["fees"]), fmt(m["sublet"]), fmt(m["supplies"])))
        rep.info("  realisation factor (accounts, discounts, warranty)", "%.4f" % m["factor"])
        rep.info("  labour per order before the price rise", fmt(m["labour_before"]) + cur)
        rate = c["labour_rate"]["standard"]
        rep.row("last labour rate rise, at P", rate["after_rise"] / rate["before_rise"] - 1, t["price_rise"], tol=0.002, absolute=True)
        rep.row("posted labour hour", rate["after_rise"], t["posted_labour_hour"], unit=cur)
        steps = cat["price_history"][cfg]["labour_hour"]
        unit, bad = (0.01 if cfg == "en" else 10), []
        for job in cat["jobs"]:
            j = job[cfg]
            for key, col in (("labour_price", "standard"), ("labour_price_company", "company_account")):
                h = j[key]["history"]
                if len(h) != len(steps) or (h[-2], h[-1]) != (j[key]["before_rise"], j[key]["after_rise"]):
                    bad.append(job["key"])
                for i, st in enumerate(steps):
                    if j["labour_pricing"] == "hourly":
                        want, tol_i = j["hours"] * st[col], 0.006
                    elif key == "labour_price":
                        want, tol_i = j[key]["after_rise"] * st[col] / steps[-1][col], unit + 1e-9
                    else:
                        want, tol_i = 0.9 * j["labour_price"]["history"][i], unit + 1e-9
                    if abs(h[i] - want) > tol_i:
                        bad.append("%s %s period %d" % (job["key"], key, i))
        rep.flag("price history: every job's labour in each of the %d periods follows the rule" % len(steps), not bad, ", ".join(bad[:6]))
        rep.info("  posted hour by period (company account)", "; ".join("%s (%s) from %s" % (fmt(st["standard"]), fmt(st["company_account"]), st["from"]) for st in steps))
        rep.info("  parts drift", "%.0f %% lower for each year before T" % (100 * cat["price_history"][cfg]["parts_drift_per_year"]))
        lo, hi = t["parts_margin_range"]
        rep.flag("parts gross margin, tier-weighted", lo <= m["parts_margin"] <= hi, "%.1f %% (accepted %.0f to %.0f %%)" % (m["parts_margin"] * 100, lo * 100, hi * 100))
        rep.row("lead shares of orders sum to one", m["lead_sum"], 1.0, tol=0.0005, absolute=True)
        rep.row("jobs per order: distribution mean vs job shares", m["jpo_mean"], m["priced_jobs"])
        rep.row("jobs per order: distribution sums to one", m["jpo_sum"], 1.0, tol=0.0005, absolute=True)
        rw = mx["recommended_work"]
        implied = rw["orders_with_recommended_work"] * rw["recommended_jobs_per_such_order"] * rw["sold_share"]
        rep.row("recommended jobs sold per order: mix vs catalogue", implied, m["rec_sold"])
        rep.row("recommended work sold (ledger)", rw["sold_share"], t["recommended_work_sold"], tol=0.0005, absolute=True)
        rep.row("S8 timing belt, class car, standard kit, current list", m["s8_price"], t["s8_current_price"], tol=0.0005, unit=cur)
        rep.row("  S8 the same job at the hour before the rise (what the stale page gives)", m["s8_old_by_rule"], t["s8_story_old_price"], tol=0.0005, unit=cur)
        rep.info("  S8 labour by period, parts at today's list", " / ".join(fmt(x) for x in s8h))
        rep.info("  S8 with shop supplies, before tax", fmt(m["s8_price"] + m["s8_supplies"]) + cur)
        rep.lines.append("  share of revenue by category: computed, mix.json row, deviation")
        for k in sorted(m["revenue_share"], key=lambda k: -m["revenue_share"][k]):
            row = mx["category_mix"][k]
            rep.row("    " + k, m["revenue_share"][k], row["share_of_revenue"], tol=0.002, absolute=True)
        rep.lines.append("  share of orders by lead category: computed, mix.json row, deviation")
        for k in sorted(m["lead_share"], key=lambda k: -m["lead_share"][k]):
            rep.row("    " + k, m["lead_share"][k], mx["category_mix"][k]["share_of_orders"], tol=0.002, absolute=True)
        rep.lines.append("  seasonal curves: yearly mean, target 1")
        for n in sorted(m["curve_means"]):
            rep.row("    " + n, m["curve_means"][n], 1.0, tol=0.005, absolute=True)
        rep.row("    all orders (lead-weighted)", m["total_mean"], 1.0, tol=0.005, absolute=True)
        stored = mx["seasonal"]["derived_by_month"]["total"]
        worst = max(abs(a - b) for a, b in zip(stored, m["total_by_month"]))
        rep.flag("  total curve by month in mix.json equals recomputed", worst < 0.002, "largest gap %.4f" % worst)
        rep.info("  all orders by month", " ".join("%.2f" % v for v in m["total_by_month"]))
        s = season_means(m["total_by_month"])
        rep.info("  all orders by season (winter spring summer autumn)", " ".join("%+.1f %%" % ((s[k] - 1) * 100) for k in ("winter", "spring", "summer", "autumn")))
        rep.info("  busiest day of the year, all orders", "%.2f times the mean" % m["total_day_peak"])
        sc = t["seasonal"]
        if "season_band" in sc:
            rep.flag("  each season within the band", all(abs(v - 1) <= sc["season_band"] + 1e-9 for v in s.values()), "band +/- %.1f %%" % (sc["season_band"] * 100))
        for name, peak in sc["peaks"].items():
            got = m["curve_day_peaks"][name] if sc["peak_basis"][name] == "day" else m["curve_peaks"][name]
            rep.row("  peak of " + name + " (" + sc["peak_basis"][name] + ")", got, peak)
        wk = mx["weekday"]["index"]
        rep.row("weekday curve mean over the days it covers", sum(wk.values()) / len(wk), 1.0, tol=0.005, absolute=True)
        rep.row("hour-of-day arrivals sum to one", sum(mx["hour_of_day"]["share_of_arrivals"].values()), 1.0, tol=0.0005, absolute=True)
        a = t["parc"]
        if "mean_age" in a:
            rep.row("parc: mean age of a drawn car, years", m["mean_age"], a["mean_age"])
        if "mean_age_min" in a:
            rep.flag("parc: mean age of a drawn car", m["mean_age"] >= a["mean_age_min"], "%.2f years (design: over %.0f)" % (m["mean_age"], a["mean_age_min"]), a.get("mean_age_gap_reported", False))
        bands = [(0, 3), (4, 7), (8, 10), (11, 15), (16, 20), (21, 25), (26, 99)]
        rep.info("parc: drawn cars by age band", ", ".join("%d-%s %.1f %%" % (lo, hi if hi < 99 else "up", 100 * sum(p for a, p in m["age_dist"].items() if lo <= a <= hi)) for lo, hi in bands))
        if "older_than_ten" in a:
            rep.row("parc: share of cars older than ten years", m["older10"], a["older_than_ten"])
        else:
            rep.info("parc: share of cars older than ten years", "%.1f %%" % (m["older10"] * 100))
        rep.flag("parc: no car older than its model, engines inside the model's years", m["parc_ok"], "")
        rep.row("parc: shares sum to one", sum(x["share"] for x in parc["configurations"][cfg]["models"]), 1.0, tol=0.0005, absolute=True)
        rep.info("counts", "%d jobs, %d models" % (len(cat["jobs"]), len(parc["configurations"][cfg]["models"])))
    verdict = "every row within tolerance" if not rep.failed else "%d row(s) MISS" % rep.failed
    if rep.gaps:
        verdict += "; %d reported gap(s) left open on purpose" % rep.gaps
    rep.lines += ["", "RESULT: " + verdict]
    text = "\n".join(rep.lines) + "\n"
    sys.stdout.write(text)
    with open(os.path.join(HERE, "catalogue_check.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
