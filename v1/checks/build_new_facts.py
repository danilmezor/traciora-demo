# Authoring helper for demo seed v1 (fix pass A, 2026-11-14): takes the "new_facts" each story call and story
# conversation lists and freezes them in checks/new_facts.json, the accepted snapshot. build_ledger.py makes one ledger
# row per file from the snapshot (nf.call.NN, nf.conv.NN); build_seed_files.py merges the same snapshot into
# named_customers.json (invented people) and accounts.json (facts about A1 to A6). A fact that contradicts an existing
# ledger row is not accepted as written: REPLACED gives the accepted wording and the content file is corrected to
# it. Rerun only on purpose: a rerun accepts whatever the content files say now.
# Not product code. Run: python3 checks/build_new_facts.py
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.normpath(os.path.join(HERE, ".."))

# (kind, cfg, number, a substring of the fact as written) -> the fact as accepted
REPLACED = {
 ("conv", "en", "23", "576.86 with shop supplies"): "Latoya Greene, 2014 Chevrolet Equinox, 96,000 miles, at west on the Friday of week T-10: check engine diagnosis 135.00, ignition coil 153.86, spark plugs 222.28; 579.50 with shop supplies (16.88) and Nashville's sales tax (tax.rate.west, 9.75 %).",
 ("conv", "ru", "09", "8 420,99"): "Ильнур Сабиров (в Telegram «Ильнур»), Renault Duster 2014: замена переднего левого ступичного подшипника на main в первый рабочий день слота 5 начиная с четверга недели T-18: 7 902 по прайсу, 8 019,99 с расходными материалами (НДС внутри цены, tax.ru_price_basis); утром по телефону ему назвали сумму без расходных материалов.",
 ("conv", "ru", "23", "итог с расходными материалами и НДС"): "Тимур Валеев, Hyundai Creta 2018, west, первый рабочий день слота 24 начиная с пятницы недели T-10: опрессовка 950, замена помпы 13 366, замена ремня 3 313,50; итог с расходными материалами в чате, НДС внутри цены (tax.ru_price_basis).",
}
ACCOUNT_NAMES = {
 "A1": ("A1", "Nickajack", "Симбирск", "гонц"), "A2": ("A2", "Millsaps", "Тёпл", "контур"), "A3": ("A3", "Moccasin", "Чист", "Венец"),
 "A4": ("A4", "Missionary", "Первая передача", "Автошкол"), "A5": ("A5", "Cumberland", "Идель"), "A6": ("A6", "Sourwood", "Вкусн"),
}
PHONE = re.compile(r"\(?\b\d{3}\)?[ -]555-\d{4}|\+7 \d{3} \d{3}-\d{2}-\d{2}")


def facts_of(kind, cfg, path):
    d = json.load(open(path, encoding="utf-8"))
    number = os.path.basename(path)[:2]
    raw = d.get("new_facts") or []
    if isinstance(raw, dict):
        raw = [f"{k}: {v}" for k, v in raw.items()]
    out, replaced = [], []
    for x in raw:
        s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
        for (k, c, n, sub), new in REPLACED.items():
            if (k, c, n) == (kind, cfg, number) and sub in s:
                replaced.append({"as_written": s, "accepted": new})
                s = new
        out.append(s)
    cast, call, sc = d.get("cast") or {}, d.get("call") or {}, d.get("scenario") or {}
    cust = cast.get("customer") or {}
    text = " ".join(out)
    phone = call.get("caller_phone") or cust.get("phone") or (PHONE.search(text).group(0) if PHONE.search(text) else None)
    shop = call.get("site") or next((s for s in ("main", "east", "west") if re.search(r"\b(at|на|в) %s\b|\b%s\b" % (s, s), text)), None)
    person = None
    if cust.get("invented") and cust.get("name"):
        person = {"name": cust["name"], "phone": phone, "shop": shop, "car": sc.get("vehicle"), "first_time": cust.get("first_time"),
                  "source": os.path.relpath(path, SEED), "facts": out}
    accounts = sorted(a for a, names in ACCOUNT_NAMES.items() if any(re.search(r"\b%s\b" % re.escape(n) if n.startswith("A") and len(n) == 2 else re.escape(n), text + " " + json.dumps(sc, ensure_ascii=False)) for n in names))
    return {"number": number, "file": os.path.relpath(path, SEED), "title": d.get("title") or d.get("demonstrates") or "", "facts": out, "replaced": replaced, "person": person, "accounts": accounts}


def build():
    snap = {"_meta": {"what": "the new facts of the story calls and story conversations as accepted in fix pass A (2026-11-14); written by checks/build_new_facts.py",
                      "stores": "the shop-system database (customers, cars, appointments, orders: erp/generator-spec.md section 5), the call log, Chatwoot, the picture and file pools",
                      "replaced": "facts whose amounts contradicted a ledger row (tax.rate.west, tax.ru_price_basis): the accepted wording is in 'facts', the file's own in 'replaced'"}}
    for kind, folder in (("call", "calls"), ("conv", "conversations")):
        for cfg in ("en", "ru"):
            snap[f"{kind}.{cfg}"] = [facts_of(kind, cfg, p) for p in sorted(glob.glob(os.path.join(SEED, folder, cfg, "[0-9][0-9]-*.json")))]
    return snap


if __name__ == "__main__":
    snap = build()
    with open(os.path.join(HERE, "new_facts.json"), "w", encoding="utf-8") as f:
        json.dump(snap, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for k, v in snap.items():
        if k != "_meta":
            print(k, len(v), "files,", sum(len(x["facts"]) for x in v), "facts,", sum(1 for x in v if x["person"]), "invented people,", sum(len(x["replaced"]) for x in v), "replaced")
