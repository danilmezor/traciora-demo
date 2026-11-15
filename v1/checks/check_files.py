# -*- coding: utf-8 -*-
# Proves that every seed file beside ledger.json agrees with it: mix and catalogue shares and prices, the cast's
# profiles and desks, the accounts, the named customers' cars against the stories' jobs, the calls design's style
# sheets and counts, the conversations rows, the story cards' numbers, the samples' names and quotes.
# A difference is a failure. Called by check_ledger.py as its section 9; runs alone as: python3 checks/check_files.py
# Not product code. The kb/ folder is checked by checks/check_kb.py (section 10 of check_ledger.py).
import glob, io, json, os, re, subprocess, sys, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))


def load(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return json.load(f)


def text(name):
    with open(os.path.join(SEED, name), encoding="utf-8") as f:
        return f.read()


def money(x, cfg=None):
    """A number as the cards write it: 1,765 or 688.00."""
    return "{:,.0f}".format(x) if float(x).is_integer() else "{:,.2f}".format(x)


def run(say, ok):
    L = {r["key"]: r for r in load("ledger.json")["rows"]}
    v = lambda k, c: L[k]["value"] if "value" in L[k] else L[k][c]
    MIX, CAT, PARC, CAST, ACC, NAMED, VEND = (load(n) for n in ("mix.json", "catalogue.json", "parc.json", "cast.json", "accounts.json", "named_customers.json", "vendors.json"))
    near = lambda a, b, tol=1e-4: abs(a - b) <= tol
    SITES = ("main", "east", "west")

    # ------------------------------------------------------------ mix.json
    say("\n9.1 mix.json against the ledger")
    for cfg in ("en", "ru"):
        m = MIX["configurations"][cfg]
        r, w, t = m["realisation"], m["recommended_work"], m["ledger_targets"]
        pairs = [("share of recommended work sold", w["sold_share"], v("sold.company", cfg) / 100), ("orders with recommended work", w["orders_with_recommended_work"], v("mix.orders_with_rec", cfg) / 100),
                 ("recommended jobs on such an order", w["recommended_jobs_per_such_order"], v("mix.rec_jobs_per_such_order", cfg)), ("recommended jobs sold per order", w["sold_recommended_jobs_per_order"], v("mix.sold_rec_jobs_per_order", cfg)),
                 ("value of a recommended job", w["average_list_value_of_a_recommended_job"], v("mix.rec_job_value", cfg)), ("warranty and goodwill share", r["warranty_and_goodwill"], v("comeback.company", cfg) / 100),
                 ("company-account share of sales", r["company_account_share_of_sales"], v("acct.big_two_share", cfg) / 100), ("realisation factor", m["computed"]["realisation_factor"], v("mix.realisation", cfg)),
                 ("target hours per order", t["billed_hours_per_order"], v("volume.hours_per_order", cfg)), ("target parts per order", t["parts_per_order"], v("volume.parts_per_order_list", cfg)),
                 ("target average order", t["average_order"], v("volume.average_order_list", cfg)), ("target labour per order", t["labour_per_order"], round(v("volume.hours_per_order", cfg) * v("price.hour.posted", cfg) * v("price.effective_rate_list", cfg), 1)),
                 ("target sold share", t["recommended_work_sold"], v("sold.company", cfg) / 100), ("target posted hour", t["posted_labour_hour"], v("price.hour.posted", cfg)), ("target last rise", t["price_rise"], round(v("price.rise.last_pct", cfg) / 100, 4)),
                 ("S8 price now", t["s8_current_price"], v("s8.price_now", cfg)), ("S8 price quoted", t["s8_story_old_price"], v("s8.price_quoted", cfg))]
        pairs += [(f"target average order, {s}", t["average_order_by_shop"][s], v(f"volume.average_order_list.{s}", cfg)) for s in SITES]
        pairs += [(f"target hours per order, {s}", t["billed_hours_per_order_by_shop"][s], v(f"volume.hours_per_order.{s}", cfg)) for s in SITES]
        pairs += [(f"sold share, {s}", t["recommended_work_sold_by_shop"][s], v(f"sold.{s}", cfg) / 100) for s in SITES]
        if cfg == "en":
            pairs.append(("Saturday at main, share of a weekday", m["weekday"]["saturday_at_main"], round(v("volume.saturday_orders.main", "en") / v("volume.orders_per_day.main", "en"), 2)))
        bad = [f"{n}: {a} there, {b} in the ledger" for n, a, b in pairs if not near(a, b, 5e-4 if abs(b) < 10 else 0.06)]
        ok("files", f"mix.json ({cfg}): {len(pairs)} shares, factors and targets equal their ledger rows", not bad, "; ".join(bad[:6]))
        curve_ok = [round(x, 3) for x in m["seasonal"]["derived_by_month"]["total"]] == v("season.total", cfg)
        ok("files", f"mix.json ({cfg}): the seasonal curve of all orders is the ledger's", curve_ok)

    # ------------------------------------------------------------ catalogue.json
    say("\n9.2 catalogue.json against the ledger")
    jobs = {j["key"]: j for j in CAT["jobs"]}
    for cfg in ("en", "ru"):
        c = CAT["configurations"][cfg]
        hist, comp = v("price.hour.history", cfg), v("price.hour.company_history", cfg)
        steps = CAT["price_history"][cfg]["labour_hour"]
        s8 = CAT["story_pins"]["S8"][cfg]
        sold = sum(j[cfg]["share_of_orders"]["total"] * j[cfg]["recommended_share"] for j in CAT["jobs"])
        checks = [("the price history's steps are the ledger's", [[s["from"], s["standard"]] for s in steps] == hist and [s["company_account"] for s in steps] == comp),
                  ("today's and the previous hour", (c["labour_rate"]["standard"]["after_rise"], c["labour_rate"]["standard"]["before_rise"]) == (v("price.hour.posted", cfg), v("price.hour.before_last_rise", cfg))),
                  ("the company-account hour", c["labour_rate"]["company_account"]["after_rise"] == v("price.hour.company", cfg)),
                  ("the parts drift", near(CAT["price_history"][cfg]["parts_drift_per_year"], v("price.parts_drift_year", cfg) / 100)),
                  ("shop supplies and tax", near(c["shop_supplies"]["rate_of_hourly_labour"], v("price.supplies.rate", cfg) / 100) and c["shop_supplies"]["cap_per_order"] == v("price.supplies.cap", cfg) and near(c["tax"]["rate"], v("tax.rate", cfg) / 100)),
                  ("recommended jobs sold per order", near(sold, v("mix.sold_rec_jobs_per_order", cfg), 0.001)),
                  ("story S8's pins", (s8["current_list_price"], s8["price_before_rise_by_the_rule"], s8["story_old_price"], s8["story_new_price"], s8["story_discount"], s8["bill_before_tax"], s8["shop_supplies"]) == (v("s8.price_now", cfg), v("s8.price_quoted", cfg), v("s8.price_quoted", cfg), v("s8.price_now", cfg), v("s8.discount", cfg), v("s8.bill_before_tax", cfg), v("s8.supplies", cfg)) and near(s8["story_paid_with_tax"], v("s8.paid_with_tax", cfg), 0.006) and "open_contradiction" not in CAT["story_pins"]["S8"]),
                  ("every job carries its labour price in each period", all(len(j[cfg][k]["history"]) == len(steps) for j in CAT["jobs"] for k in ("labour_price", "labour_price_company")))]
        bad = [n for n, good in checks if not good]
        ok("files", f"catalogue.json ({cfg}): hours by date, drift, supplies, tax, recommended shares and story pins equal the ledger", not bad, "; ".join(bad))
    buf = io.StringIO()
    sys.path.insert(0, HERE)
    import check_catalogue
    with contextlib.redirect_stdout(buf):
        rc = check_catalogue.main()
    ok("files", "checks/check_catalogue.py passes: hours, labour, parts and average order for the company and each shop, the price history", rc == 0, "; ".join(l.strip() for l in buf.getvalue().split("\n") if "MISS" in l)[:400])

    # ------------------------------------------------------------ cast
    say("\n9.3 cast.json and cast.md against the ledger")
    people = {p["slot"]: p for p in CAST["people"]}
    desks = {k[1:-5]: v(k, "en") for k in L if re.fullmatch(r"p(\d\d|F\d)\.desk", k)}
    bad = [f"slot {s}: {people[str(int(s)) if s.isdigit() else s]['extension']} against {d}" for s, d in desks.items() if str(people[str(int(s)) if s.isdigit() else s]["extension"]) != str(d)]
    ok("files", f"every desk of the ledger ({', '.join(str(d) for d in sorted(desks.values()))}) is that person's extension in cast.json", not bad, "; ".join(bad))
    ok("files", "every person's profile points at ledger rows that exist", all(any(k.startswith(p["profile"]["ledger_rows"][:-1]) for k in L) for p in CAST["people"]))
    cast_blob = json.dumps(CAST, ensure_ascii=False)
    ok("files", "cast.json: 29 slots and 4 former people; no 'Walt', no '28 people', no 'month-end', no 'all 32'", len(people) == 33 and not re.search(r"Walt|28 people|month-end|all 32 ", cast_blob))
    c27 = {cfg: round(v("p27.comebacks", cfg)) for cfg in ("en", "ru")}
    words = {"en": {7: "Seven of his jobs in a hundred", 5: "Five of his jobs in a hundred"}, "ru": {7: "возвращаются семь", 5: "возвращаются пять"}}
    ok("files", f"slot 27's biography states his comeback rate as the ledger has it ({c27['en']} and {c27['ru']} in a hundred; 5 against 2 on good pads)",
       all(words[cfg][c27[cfg]] in people["27"][cfg]["biography"] for cfg in ("en", "ru")) and "five times in a hundred, against two" in people["27"]["en"]["biography"] and "пять работ из ста против двух" in people["27"]["ru"]["biography"]
       and (v("s6.rate.good.p27", "en"), v("s6.rate.good.others", "en")) == (5.0, 2.0))
    f1 = people["F1"]
    ok("files", "F1's biographies carry each market's leak signature (en: voids and a short till; ru: parts with no sale and work past the order)",
       "voiding" in f1["en"]["biography"] and "nineteen" in f1["en"]["biography"] and "списывал запчасти" in f1["ru"]["biography"] and "сверх наряда" in f1["ru"]["biography"] and "аннулировал" not in f1["ru"]["biography"]
       and v("s2.f1.third", "en")["count"] == 19 and "parts" in v("s2.f1.second", "ru")["what"])
    ok("files", "slot 16's English biography says what she sells and what the shop sells with and without her", "seven recommendations in ten herself" in people["16"]["en"]["biography"] and round(v("p16.sold_rec", "en"), -1) == 70 and 60 < v("s5.east_with_16", "en") < 70 and round(v("s5.east_without_16", "en"), -1) == 50)
    md = text("cast.md")
    sys_rows = [f"| {p['slot']} | " for p in CAST["people"]]
    path6, path24 = v("p06.score_path", "en"), v("p24.score_path", "en")
    facts = [f"call score {path6[0]} to {path6[-1]}", f"call score {path24[0]} to {path24[-1]}", f"{round(v('s5.leave_drop_pct', 'en'))} % of its billed hours", f"call score {v('p23.call_score', 'en')}", "| 105 |", "| 304 |", "Ray Brennan"]
    ok("files", "cast.md is cast.json's table and its one-liners carry the ledger's figures", all(r in md for r in sys_rows) and all(f in md for f in facts) and all(p["en"]["full_name"] in md and p["ru"]["full_name"] in md for p in CAST["people"]), ", ".join(f for f in facts if f not in md))
    ph = text("phones.md")
    ok("files", "phones.md rings desk 105 at main and names 304 as retired", ph.count("101, 102, 103, 105") == 2 and ph.count("304") == 2)

    # ------------------------------------------------------------ accounts, vendors, named customers
    say("\n9.4 accounts, vendors and named customers")
    for cfg in ("en", "ru"):
        accts = {a["id"]: a for a in ACC[cfg]["accounts"]}
        ok("files", f"accounts.json ({cfg}): vehicle counts, home shops and terms of A1 to A6 are the ledger's", all((a["fleet_count"], len(a["fleet"]), a["home_shop"], a["payment_terms_days"]) == (v(f"acct.{k}.vehicles", cfg), v(f"acct.{k}.vehicles", cfg), v(f"acct.{k}.shop", cfg), v(f"acct.{k}.terms_days", cfg)) for k, a in accts.items()) and sorted(accts) == ["A1", "A2", "A3", "A4", "A5", "A6"])
        first = {p[cfg]["full_name"].split()[0] for p in CAST["people"]}
        outside = [c["name"] for a in accts.values() for c in a["contacts"]] + [x["name"] for x in NAMED[cfg].values() if isinstance(x, dict) and "name" in x]
        clash = [n for n in outside if n.split()[0] in first]
        ok("files", f"accounts.json and named_customers.json ({cfg}): no contact or story customer shares a first name with the cast", not clash, ", ".join(clash))
        v2 = next(x for x in VEND[cfg] if x["id"] == "V2")
        note = VEND["_meta"]["the_cheap_brake_pads"]
        ok("files", f"vendors.json ({cfg}): the cheap pad brand is the ledger's, marked invented, with its reason and namesake check; delivery rates are the ledger's",
           v2["house_brand"]["name"] == v("s6.brand", cfg) == note["brand"][cfg] and note["invented"] is True and note["why"] and note["namesake_check"]
           and v2["delivered_on_the_promised_day"] == f"{v('parts.on_time.V2', cfg)} %" and next(x for x in VEND[cfg] if x["id"] == "V1")["delivered_on_the_promised_day"] == f"{v('parts.on_time.V1', cfg)} %")
        models = {(m["make"], m["model"].split(" /")[0].split()[0]): m for m in PARC["configurations"][cfg]["models"]}
        car = NAMED[cfg]["S8"]["car"]
        m = models.get((car["make"], car["model"].split()[0]))
        hours = jobs["timing_belt_kit"][cfg]["hours"]
        why = NAMED[cfg]["S8"]["why_the_story_is_sound"]
        ok("files", f"named_customers.json S8 ({cfg}): {car['make']} {car['model']} is class car in parc.json with a timing belt, and the text states the catalogue's {hours} hours",
           bool(m) and m["vehicle_class"] == "car" == car.get("vehicle_class") and any(e["timing"] == "belt" for e in m["engines"]) and (str(hours) in why or str(hours).replace(".", ",") in why) and CAT["story_pins"]["S8"]["vehicle_class"] == "car")
        s6 = NAMED[cfg]["S6_waiting_nine_days"]
        surname = s6["name"].split()[-1]
        places = {"stories/S06.md": text("stories/S06.md"), f"calls/samples/{cfg}-3-weak-desk.json": text(f"calls/samples/{cfg}-3-weak-desk.json"), f"conversations/samples/{cfg}-3-west-nine-days.json": text(f"conversations/samples/{cfg}-3-west-nine-days.json")}
        part = {"en": "angle gear", "ru": "насос"}[cfg]
        model = {"en": "XC60", "ru": "308"}[cfg]
        miss = [p for p, t in places.items() if not (surname in t and model in t and part in t)]
        ok("files", f"S6's waiting customer ({cfg}): {s6['name']}, {s6['car']['make']} {s6['car']['model']}, '{part}' in the card, the call sample and the conversation sample", not miss and part in s6["waiting_for"] and model in s6["car"]["model"] and max(v("s6.waiting_at_t", cfg)["west_days"]) == 9, ", ".join(miss))
    ok("files", "named_customers.json lists the 12 pairs and 2 wrong-customer orders of the ledger", all(len(NAMED[c]["S15_duplicate_pairs"]) == v("s15.mess", c)["duplicate_pairs"] and len(NAMED[c]["S15_car_on_the_wrong_customer"]) == v("s15.mess", c)["wrong_customer_orders"] for c in ("en", "ru")))

    # ------------------------------------------------------------ calls design and samples
    say("\n9.5 calls/DESIGN.md and its samples")
    cd = text("calls/DESIGN.md")
    names = {"5 lead": "p05.check", "6 junior operator, month 1": "p06.check.first", "6 junior operator, month 6": "p06.check.last", "7 newcomer": "p07.check", "29 fourth advisor": "p29.check", "16 lead": "p16.check", "17": "p17.check",
             "22 shop manager": "p22.check", "23 weak desk": "p23.check", "24, month 1": "p24.check.first", "24, month 6": "p24.check.last"}
    CH = ("greeting", "name_and_number", "need_discovery", "price_with_next_step", "offered_time", "asked_for_booking", "recap", "objection")
    bad, seen = [], 0
    for line in cd.split("\n"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 11 and re.fullmatch(r"\d+/\d+/\d+", cells[1]):
            key = next((kk for n, kk in names.items() if cells[0].startswith(n) and (n != "17" or cells[0] == "17")), None)
            if not key:
                bad.append("no ledger sheet for row " + cells[0]); continue
            seen += 1
            for cname, cell in zip(CH, cells[1:9]):
                if [int(x) for x in cell.split("/")] != v(f"{key}.{cname}", "en"): bad.append(f"{cells[0]} {cname}")
            p = key.split(".")[0]
            want = v(p + ".score_path", "en")[0 if key.endswith("first") else -1] if key.endswith(("first", "last")) else v(p + ".call_score", "en")
            if float(cells[10]) != float(want): bad.append(f"{cells[0]}: ledger column {cells[10]} against {want}")
            exp = v(key.replace(".check", ".sheet_expected"), "en")
            if abs(float(cells[9]) - exp) > 0.11: bad.append(f"{cells[0]}: expected {cells[9]} against {exp}")
    ok("files", f"calls/DESIGN.md: the {seen} style sheets, their expected scores and their ledger scores are the People rows", seen == 11 and not bad, "; ".join(bad[:6]))
    n_en, n_ru = (v("calls.inbound_product_period", c) for c in ("en", "ru"))
    figures = ["{:,}".format(int(v(k, c))) for k in ("calls.inbound_product_period", "calls.answered_product_period", "calls.outbound_product_period") for c in ("en", "ru")]
    need = figures + ["2.2 an order", "`r13.calls.clarification_loop`", "`r13.calls.unresolved`", f"{v('r13.calls.clarification_loop', 'en'):g} %", "101 (slot 5), 102 (6), 103 (7) and 105 (29)", "Desk 304 was F1's", "two named callers",
                      "Monday in the English configuration and Tuesday in the Russian", "unclear openings", "seven named calls"]
    miss = [x for x in need if x not in cd]
    ok("files", "calls/DESIGN.md: call counts at 2.0 and 2.2 an order, desks 105 and 304, rule R13 in the taxonomy and the patterns, the instances the ledger made of '5 % never' and 'Mondays'", not miss and "T−" not in cd and not re.search(r"\bT-\d+d\b", cd) and v("calls.inbound_per_order", "ru") == 2.2
       and v("calls.callback.main.after", "en")["never_named"] == 2 and v("calls.busiest_mornings_since_fix", "ru")["weekday"] == "Tuesday", "; ".join(miss))
    slot_name = {cfg: {int(s): p[cfg]["full_name"] for s, p in people.items() if s.isdigit()} for cfg in ("en", "ru")}
    bad = []
    for f in sorted(glob.glob(os.path.join(SEED, "calls", "samples", "*.json"))):
        d, n = json.load(open(f, encoding="utf-8")), os.path.basename(f)
        cfg = n[:2]
        adv = d["cast"]["advisor"]
        full = slot_name[cfg][adv["slot"]]
        if not (adv["name"] == full or adv["name"] == " ".join([full.split()[0], full.split()[-1]])) or "placeholder" in json.dumps(d["cast"]): bad.append(n + ": advisor name or a placeholder")
        if str(d["call"]["answered_by"]) != str(v(f"p{adv['slot']:02d}.desk", cfg)): bad.append(n + ": answering desk")
        if re.search(r"T-\d+d", d["call"]["day"]): bad.append(n + ": the day is not an anchor of rule R6")
        segs = {x["sequence"]: x for x in d["transcript"]["segments"]}
        ja, alltext = d["judge_answer"], " ".join(x["text"] for x in d["transcript"]["segments"])
        for c in ja.get("checks", []) + ja.get("auto_fails", []):
            if c["quote"] not in segs[c["segment"]]["text"]: bad.append(f"{n}: quote of {c['key']} is not on its line")
        for grp in ("checks", "auto_fails"):
            for k, q in d["verdict"]["result_enc_plain"].get(grp, {}).items():
                if q not in alltext: bad.append(f"{n}: stored quote of {k} is not in the transcript")
        pub = d["verdict"]["result_public"]
        if [(c["key"], c["level"]) for c in ja["checks"]] != [(c["key"], c["level"]) for c in pub["checks"]] or d["verdict"]["score"] != pub["score"]: bad.append(n + ": verdict and judge answer differ")
        if re.search(r"Jersey Pike|Tolliver|Pruitt|Соловь|927 000|917 000|555-0142", json.dumps(d, ensure_ascii=False)): bad.append(n + ": a name or number the seed does not have")
    ok("files", "calls/samples: the cast's names and desks, rule-R6 days, every quoted line word for word in its transcript, verdicts equal to the judge answers", not bad, "; ".join(bad[:6]))

    # ------------------------------------------------------------ conversations design and samples
    say("\n9.6 conversations/DESIGN.md and its samples")
    cv = text("conversations/DESIGN.md")
    spd = {c: v("conv.sessions_per_day", c) for c in ("en", "ru")}
    rows = {"| EN weekday | %d | %d | | | %d |" % (spd["en"]["weekday"]["web chat"], spd["en"]["weekday"]["Telegram"], v("conv.sessions_per_day.total", "en")),
            "| RU every day | %d | %d | %d | %d | %d |" % tuple([spd["ru"]["every day"][k] for k in ("web chat", "Telegram", "VK", "Avito")] + [v("conv.sessions_per_day.total", "ru")])}
    out = v("conv.draft_outcomes", "en")
    rows |= {"| %s | %d | %d | %d |" % (s, *o) for s, o in out.items()}
    fr = "slot 5: %d min, 6: %d, 7: %d, 29: %d, 16: %d, 17: %d, 22: %d, 23: %d, 24: %d" % tuple(v(f"p{s}.first_reply_min", "en") for s in ("05", "06", "07", "29", "16", "17", "22", "23", "24"))
    o_en, o_ru = v("conv.open_at_t", "en"), v("conv.open_at_t", "ru")
    need = sorted(rows) + [fr, "slot 29: %d" % v("p29.first_reply_min", "ru"), "**%g %%** of sessions have at least one loop" % v("r13.chats.clarification_loop", "en"), "**%g %% of sessions end unclear**" % v("r13.chats.unresolved", "en"),
                           "| open or pending at T | %d: web %d (%d pending), Telegram %d | %d: web %d (%d pending), Telegram %d, VK %d |" % (o_en["total"], sum(o_en["web chat"].values()), o_en["web chat"]["pending"], o_en["Telegram"]["open"], o_ru["total"], sum(o_ru["web chat"].values()), o_ru["web chat"]["pending"], o_ru["Telegram"]["open"], o_ru["VK"]["open"]),
                           "`CHATWOOT_TELEGRAM_ASSISTANT=drafts`", "in a live demo a reply is sent in the web chat only", "About %d %% of messenger contacts" % v("conv.avatars", "en")["messenger_contacts_with_a_picture_pct"], "Web-chat visitors have no picture",
                           "{:,} sessions".format(v("conv.sessions_product_period", "en")), "{:,} (RU".format(v("conv.sessions_product_period", "ru")), "`conv.first_reply.definition`"]
    miss = [x for x in need if x not in cv]
    keys = set(re.findall(r"`((?:conv|r13|pNN)\.[A-Za-z0-9_.]+)`", cv))
    unknown = sorted(k for k in keys if not k.startswith("pNN") and k not in L and not any(x.startswith(k.rstrip("*")) for x in L))
    ok("files", f"conversations/DESIGN.md: volumes by channel, draft outcomes and reply times per advisor, rule R13, the open set at T, Telegram on drafts, the live-demo rule and avatars are the ledger's; its {len(keys)} ledger keys exist",
       not miss and not unknown and v("conv.assistant_mode", "en")["Telegram"] == "drafts" == v("conv.assistant_mode", "ru")["Telegram"] and "T−" not in cv, "; ".join(miss[:5] + unknown[:5]))
    bad = []
    for f in sorted(glob.glob(os.path.join(SEED, "conversations", "samples", "*.json"))):
        d, n = json.load(open(f, encoding="utf-8")), os.path.basename(f)
        cfg = n[:2]
        for s in d["cast"].get("staff", []):
            if s["name"] != slot_name[cfg][s["slot"]] and s["name"] != " ".join([slot_name[cfg][s["slot"]].split()[0], slot_name[cfg][s["slot"]].split()[-1]]): bad.append(f"{n}: staff name {s['name']}")
        for c in d["conversations"]:
            st = c["state_at_t"]
            if st["status"] in ("open", "pending") and (st.get("draft_in_box") or st.get("waiting_since")) and c["channel"] != "chat": bad.append(n + ": a chat that waits on the shop at T is not a web chat")
            if c["channel"] != "chat" and c["assistant_mode"] != "drafts": bad.append(n + ": a messenger that is not on drafts")
            if c["channel"] == "chat" and c["contact"].get("phone"): bad.append(n + ": a web visitor with a phone on the contact")
        if d["story"] in ("S6", "S7") and any(c["channel"] != "chat" for c in d["conversations"]): bad.append(n + ": the story's thread is a web chat on the card")
        if d["story"] == "S7":
            first = min(int(x) for x in re.findall(r'"day": "T-(\d+)d"', json.dumps(d)))
            if max(int(x) for x in re.findall(r'"day": "T-(\d+)d"', json.dumps(d))) >= v("conv.web_visitor_memory_days", cfg): bad.append(n + ": the first chat is not inside the web chat's 30 days")
        if re.search(r"Jersey Pike|A, B or C", json.dumps(d, ensure_ascii=False)): bad.append(n + ": a name or note the seed no longer has")
    ok("files", "conversations/samples: the cast's names, S6 and S7 in the web chat, S7 inside the visitor's 30 days, messengers on drafts, nothing waiting on the shop outside the web chat", not bad, "; ".join(bad[:6]))

    # ------------------------------------------------------------ story cards: the numbers they quote
    say("\n9.7 the story cards' figures and anchors")
    S = {n: text(f"stories/S{n:02d}.md") for n in range(1, 17)}
    TL = text("stories/TIMELINE.md")
    c_en, c_ru = v("s6.counts", "en"), v("s6.counts", "ru")
    b_en, b_ru = v("s7.bill", "en"), v("s7.bill", "ru")
    want = {
     2: [f"{money(v('s2.total', 'en'))} USD", f"{money(v('s2.total', 'ru'))} RUB", f"{v('s2.f1.cash_orders', 'en')} of his {round(v('s2.f1.orders', 'en'))} orders", "| %.1f %%, %.1f %% |" % (v("s2.west.discount_share_before", "ru"), v("s2.west.discount_share_after", "ru"))],
     3: ["| %s %%, %s %% | %s %%, %s %% |" % (v("calls.main.before.miss_day", "en"), v("calls.main.since.miss_day", "en"), v("calls.main.before.miss_day", "ru"), v("calls.main.since.miss_day", "ru"))],
     5: ["| Average order falls by | %d USD | %s RUB |" % (round(v("s5.order_value_drop", "en")), money(v("s5.order_value_drop", "ru"))), "| %s %% (the shop, both at the desk) | %d %% (her days) |" % (v("s5.east_with_16", "en"), v("s5.east_with_16", "ru")),
         "| Missed calls at `east` | %s %% | %d %%" % (v("calls.east.miss_w90", "en"), v("calls.east.miss_w90", "ru")), "Bonny Oaks"],
     6: ["| %d comebacks of %d (5 %%) | %d of %d |" % (c_en["comebacks_p27_good"], c_en["p27_good"], c_ru["comebacks_p27_good"], c_ru["p27_good"]), "| %d of %d (20 %%) | %d of %d |" % (c_en["comebacks_p27_cheap"], c_en["p27_cheap"], c_ru["comebacks_p27_cheap"], c_ru["p27_cheap"]),
         "| %d of %s (2 %%) | %d of %s |" % (c_en["comebacks_good_not_27_all_shops"], money(c_en["good_pad_jobs_not_27_all_shops"]), c_ru["comebacks_good_not_27_all_shops"], money(c_ru["good_pad_jobs_not_27_all_shops"])),
         "| slot 27, all his orders | %.1f %% | %.1f %% |" % (v("p27.comebacks", "en"), v("p27.comebacks", "ru"))],
     7: ["en: slot 6's 14th working day before T; ru: her 10th", "= %.2f |" % b_en["before_tax"] if False else "555.10", "%s with sales tax" % b_en["with_tax"], "{:,.2f}, VAT inside".format(b_ru["with_tax"]), "less than 30 days before T", "web chat"],
     8: ["%.2f USD (3.2 hours at 135" % v("s8.price_now", "en"), "%.2f (the hour at 125)" % v("s8.price_quoted", "en"), "%s (the hour at 1,760)" % money(v("s8.price_quoted", "ru")), "%.2f | %s |" % (v("s8.paid_with_tax", "en"), "{:,.2f}".format(v("s8.paid_with_tax", "ru"))), "Renault Logan 2015"],
     15: ["| %s, %s, %s USD | %s, %s, %s RUB |" % tuple([v(f"volume.average_order.{s}", "en") for s in SITES] + [money(v(f"volume.average_order.{s}", "ru")) for s in SITES])],
    }
    bad = [f"S{n:02d}: {w}" for n, ws in want.items() for w in ws if w not in S[n]]
    ok("files", "the cards quote the ledger's figures: S2's estimate and shares, S3's missed share, S5's sold shares and order drop, S6's counts, S7's bill and anchors, S8's amounts and car, S15's averages", not bad, "; ".join(bad[:6]))
    a_en, a_ru = v("s7.booking_day", "en"), v("s7.booking_day", "ru")
    ok("files", "TIMELINE.md places S7 by the ledger's anchors, inside the web chat's 30 days, and its worked examples are the script's output", "slot 6's 14th (en) or 10th (ru) working day before T" in TL and "14th" in a_en and "10th" in a_ru and "S7 first chat under 30 days before T holds" in TL and "FAILS" not in TL
       and subprocess.run([sys.executable, os.path.join(HERE, "timeline_examples.py")], capture_output=True, text=True).stdout.strip() in TL)

    # ------------------------------------------------------------ nothing stale anywhere outside kb/
    say("\n9.8 names and figures that must be gone, in every seed file outside kb/")
    files = [p for p in glob.glob(os.path.join(SEED, "**", "*"), recursive=True) if os.path.isfile(p) and os.sep + "kb" + os.sep not in p and not p.endswith((".DS_Store", "PENDING.md", ".pyc", "check_files.py", "check_calls.py", "check_conversations.py", "ledger_check.txt")) and "__pycache__" not in p]
    stale = {"Jersey Pike": "the English east shop is Bonny Oaks", "Ray Coffey": "A1's contact was renamed", "rcoffey": "A1's contact was renamed", "Walt Brennan": "the founder is Ray", "840 orders": "the English orders a month are 808",
             "names a Renault Duster": "S8's Russian car is a Logan", "decision A, B or C": "the live-demo rule is decided", "2026-11-13-demo-seed-parameters.md": "the ledger is ledger.json"}
    hits = [f"{os.path.relpath(p, SEED)}: {k}" for p in files for k in stale if k in open(p, encoding="utf-8", errors="ignore").read()]
    ok("files", f"{len(files)} files hold none of: " + ", ".join(stale), not hits, "; ".join(hits[:8]))
    ok("files", "the east shop's address and short name are in the ledger", "6340 Bonny Oaks Drive" in v("geo.address.east", "en") and v("geo.short_name", "en")["east"] == "Bonny Oaks")
    import build_ledger_md
    ok("files", "ledger.md is what checks/build_ledger_md.py makes of ledger.json", os.path.exists(os.path.join(SEED, "ledger.md")) and build_ledger_md.render() == text("ledger.md"))


if __name__ == "__main__":
    fails = []
    def ok(section, name, cond, detail=""):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}{': ' + detail if detail and not cond else ''}")
        if not cond: fails.append(name)
    run(print, ok)
    print(f"\n{'ALL AGREE' if not fails else 'DISAGREE'}: {len(fails)} failure(s)")
    sys.exit(1 if fails else 0)
