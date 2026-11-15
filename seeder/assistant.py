"""The step assistant: the managers' side of the assistant as the stories left it (v1/assistant/DESIGN.md, section 1 its
spec), from `assistant/<cfg>/`. In the core database: the 62 personal notes and the 14 team notes (`platform.memory`)
and the 19 proposals (`platform.proposal`). In auth.db: the 15 hand-written Ask threads and, for each note saved from a
background thread (`auto`), the one exchange that saved it (`conversations`, each with its chat-memory file under
`<runtime>/chat_memory/`); the 7 scheduled tasks with the run of their last due time before T and the S10 runs the task
file plants, the 15 briefs with the first brief of T's brief day for the four who read one (`cron_prompt_jobs`,
`cron_runs`, `managers.brief_seen_at`).

Written through the product where it has a writer that takes the seed's values: a task job through
`CronStore.create_prompt_job`, a brief job through `tasks.ensure_brief`, every run through `CronStore.add_run`, the
brief's last reading through `AuthManager.mark_brief_seen`, a chat file through `FileBasedMemory._write_payload`. Direct
writes, each because no product writer takes a past time or a chosen id: the memory and proposal rows (the commands stamp
`now()` and draw `gen_random_uuid()`; sealed with `envelope.encrypt`, keyed by `store.subject_token` and `slug_for`, as
the commands do), the `conversations` rows, and the id and times of a job the step made. Decision cards are the
product's own (`DecisionSpec.request`, `validate_answer`), tool labels its catalogue's in the configuration's locale.

A text's dates (`{{<when>|<format>}}`) and ledger constants (`{{$key|format}}`) are written out, and so are its computed
values (`{{=metric|population|period|format}}`) and tables (`{{#name}}`): each metric is the query of
`assistant/metrics.sql` run at the item's own instant (a turn's answer, a run's start, a brief's write time) on the shop
database or the core database, or the catalogue or the task's schedule, and written in the slot's format. A task's run
takes the first case whose leading figure the data gives (a calendar case first). An item is held back, never written with a template, when it needs a metric of `SLICE` (no
data in this slice: the item is not in v1) or of `UNDEFINED` (no definition), when the loaded data contradicts it
(`NOT_IN_V1`; a brief point there when its leading figure reads none or zero), or when it needs a Russian word the
seed's files do not hold; a thread held for a metric or by `NOT_IN_V1` is loaded as its note turns alone, with the
locale's acknowledgement; a job any of whose texts reads a metric of `SLICE` is not made, and a brief point held is left
out of its brief. `held` names each with its
reason. Every resolved slot is kept in `resolved` (item,
metric, instant, value). Not loaded: the background threads beyond the exchanges that saved a note, run history before
the last due time, the brief bank, Inbox lines, the nights."""
import contextlib
import datetime as dt
import hashlib
import json
import re
import sqlite3
import subprocess
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from seeder import clock, ids, inputs, manifest, tenant

UTC = dt.timezone.utc
DOW = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
WHEN = re.compile(r"(@\w+|T|W([+-]?\d+)\.(mon|tue|wed|thu|fri|sat|sun)|P([1-6])|slot(\d+):([+-]\d+))((?:[+-]\d+(?:wd:\w+|d|w|mo|y))*)")
MOVE = re.compile(r"([+-]\d+)(?:wd:(\w+)|(d|w|mo|y))")
SLOT = re.compile(r"\{\{([^{}]+)\}\}")
RUN_AT = re.compile(r"(\S+) (\d\d:\d\d)")
GAP = dt.timedelta(seconds=90)  # a person reads an answer before the next question
MODEL = "seed-v1"
FILES = ("threads", "notes", "team", "tasks")
LEDGER = inputs.ROWS | {r["key"]: r for r in inputs.load("assistant/ledger_rows.json")["rows"]}
CARDS = {"s3.early_desk_shift": "S03-early-desk", "s6.supplier_change": "S06-supplier"}  # a slot's name for a card of workday/<cfg>/cards.json
QUERIES = {m[1]: (m[2], block.split("\n", 1)[1]) for block in (inputs.SEED / "assistant" / "metrics.sql").read_text(encoding="utf-8").split("\n\n")
           if (m := re.match(r"-- ([a-z_.]+) \| store: (\w+) \|", block))}  # metric: (store, query)
# metrics.json's metrics with no data in this slice, so an item that reads one is not in v1: a day's call volume and the
# callers waiting at T (ledger calls.queue_at_t) need the call bank, which is not loaded, and shifts exist from the week
# of T only
SLICE = frozenset({"calls.inbound", "calls.missed", "calls.missed_share", "calls.missed_top_site", "calls.never_share", "calls.wait_median",
                   "calls.out_of_hours", "calls.called_back", "calls.waiting", "calls.oldest_waiting", "roster.shifts"})
# what the design, the dictionary and metrics.json leave without a definition the data can answer
UNDEFINED = {"bookings.free_slot": "no capacity per appointment time: kb.booking.slots names when a visit may be booked, not how many"}
# items the loaded data does not bear out: a thread is loaded as its note turns alone; a brief point is left out of its
# brief when its leading figure reads none or zero
NOT_IN_V1 = {"s4-call-summary": "her scored calls (01 to 07) are about a month apart, so her last shift before the thread has none, while "
                                "the thread speaks of several",
             "brief-4 point 3": "the roster's one cover band does not show the desk one short; the ledger's s5.week_off and card "
                                "G-cover-week-off say it is"}
NB = "\u00a0"  # v1/evals/_build/common.py's space inside a number and before its unit
CASE_DAY = {"yesterday-three-numbers": -1, "missed-calls-today": 0, "tomorrows-gaps": 1}  # the day a calendar case reads
# A job's runs take negative ids, ascending in time inside the job's block: the product numbers its own runs upward from the
# largest id (AUTOINCREMENT), so none of its runs falls in a block and a run of the seed is older than any it writes later.
RUNS_PER_JOB = 16


def ms(at):
    return int(at.timestamp() * 1000)


def utc(at, fmt="%Y-%m-%d %H:%M:%S"):
    return at.astimezone(UTC).strftime(fmt)


def stamp(at):
    """An instant as the scheduler writes one: ISO 8601 in UTC."""
    return at.astimezone(UTC).isoformat()


def worked(a, slot, d, n):
    """Slot's n-th working day after (n > 0) or before (n < 0) d; n = 0 its first on or after d."""
    works, step = a["works"], 1 if n >= 0 else -1
    while n == 0 and not works(slot, d):
        d += dt.timedelta(1)
    for _ in range(abs(n)):
        d += dt.timedelta(step)
        while not works(slot, d):
            d += dt.timedelta(step)
    return d


def day(c, text, now=None):
    """A date of the grammar of DESIGN.md section 2.5; `now` is the item's own date."""
    a, cfg = c["a"], c["cfg"]
    m = WHEN.fullmatch(text)
    if m is None:
        raise ValueError(f"assistant/{cfg}: no date for '{text}'")
    if m[1] == "@now":
        d = now
    elif m[1][0] == "@":
        d = c["events"][m[1][1:]]
    elif m[1] == "T":
        d = a["T"].date()
    elif m[3]:
        d = a["week_day"](int(m[2]), DOW.index(m[3]))
    elif m[4]:
        d = a["G"] + dt.timedelta(inputs.value("time.score_period_days", cfg) * (int(m[4]) - 1))
    else:
        d = worked(a, int(m[5]), a["T"].date(), int(m[6]))
    for n, who, unit in MOVE.findall(m[7]):
        n = int(n)
        if who.startswith("slot"):
            d = worked(a, int(who[4:]), d, n)
        elif who:
            d = clock.wd(cfg, d, n) if n else clock.snap(cfg, d)
        elif unit in ("d", "w"):
            d += dt.timedelta(n * (7 if unit == "w" else 1))
        else:
            d = tenant.months(d, n * (12 if unit == "y" else 1))
    return d


def at(d, hm, zone):
    return dt.datetime.combine(d, dt.time(*map(int, hm.split(":"))), zone).astimezone(UTC)


def hour(c, key, zone, d):
    """A time of day for an item the files date but do not time: between 09:00 and 17:00 on the person's clock."""
    minute = 540 + ids.number("minute", key, c["cfg"]) % 480
    return at(d, f"{minute // 60}:{minute % 60}", zone)


def midnight(c, d):
    return dt.datetime.combine(d, dt.time(), c["home"]).astimezone(UTC)


class Held(Exception):
    """An item cannot be written: `kind` is slice (a metric with no data in this slice), undefined (a metric with no
    definition) or words (a Russian word the seed's files do not hold)."""

    def __init__(self, kind, what):
        super().__init__(f"{kind} {what}")
        self.kind, self.what = kind, what


def clock_text(cfg, t):
    """A time of day as metrics.json writes one: "8:30 a.m." (en), "9:40" (ru)."""
    return f"{t.hour % 12 or 12}:{t.minute:02} {'a.m.' if t.hour < 12 else 'p.m.'}" if cfg == "en" else f"{t.hour}:{t.minute:02}"


def date_text(cfg, d, fmt):
    """A date (or an instant, for daytime) in one of metrics.json's date formats, with the words of tenant/dates.json."""
    n = tenant.DATES[cfg]
    words = {"day": d.day, "year": d.year, "month": n["months"][d.month - 1], "weekday": n["weekdays"][d.weekday()],
             "month_genitive": n.get("months_genitive", n["months"])[d.month - 1]}
    forms = {"date": n["formats"]["date"], "day": n["formats"]["day"], "weekday": "{weekday}", "month": "{month} {year}"}
    if cfg == "en":
        forms |= {"short": f"{words['weekday'][:3]}, {words['month'][:3]} {d.day}", "numeric": f"{d.month}/{d.day}"}
        if isinstance(d, dt.datetime):  # metrics.json: "Wednesday at 8:30 a.m."
            forms["daytime"] = f"{words['weekday']} at {clock_text(cfg, d)}"
    else:  # metrics.json's examples: "4 марта", "марта 2026 года", "04.03", "в среду, 4 марта, в 10:00"
        forms |= {"date_gen": "{day} {month_genitive}", "month_gen": "{month_genitive} {year} года", "numeric": f"{d.day:02}.{d.month:02}",
                  "weekday_acc": n["weekdays_accusative"][d.weekday()], "on_weekday": n["on_weekday"][d.weekday()],
                  "on_day": f"{n['on_weekday'][d.weekday()]}, {n['on_day']}", "until_day": n["until_day"],
                  "since_weekday": n["since_weekday"][d.weekday()]}
        if isinstance(d, dt.datetime):
            forms["daytime"] = f"{forms['on_day']}, в {clock_text(cfg, d)}"
            forms["since_daytime"] = n["since_daytime"].format(since_weekday=forms["since_weekday"], time=clock_text(cfg, d))
    if fmt not in forms:
        raise Held("words", f"tenant/dates.json has no words for the {cfg} date format {fmt}")
    return forms[fmt].format(**words)


def number(cfg, v, places=0):
    """A number as v1/evals/_build/common.py writes it: 3,203.50 (en), 3 203,50 (ru), rounded half up."""
    text = f"{Decimal(str(v)).quantize(Decimal(1).scaleb(-places), 'ROUND_HALF_UP'):,.{places}f}"
    return text if cfg == "en" else text.replace(",", NB).replace(".", ",")


def money(cfg, v, places):
    return f"${number(cfg, v, places)}" if cfg == "en" else f"{number(cfg, v, places)}{NB}₽"


def value_text(cfg, v, fmt, zone):
    """A resolved value in a slot's format (metrics.json's value and date formats); a value the data does not have is
    written as a dash."""
    if v is None:
        return "—"
    if fmt.startswith("n:"):
        forms, n = fmt[2:].split("/"), int(Decimal(str(v)).quantize(Decimal(1), "ROUND_HALF_UP"))
        if cfg == "en":
            noun = forms[0] if n == 1 else forms[1]
        else:
            noun = forms[0] if n % 10 == 1 and n % 100 != 11 else forms[1] if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else forms[2]
        return f"{number(cfg, n)} {noun}"
    if fmt in ("int", "pct", "pct1", "score"):
        out = number(cfg, v, {"pct1": 1, "score": 1}.get(fmt, 0))
        return out + NB + "%" if fmt.startswith("pct") else out
    if fmt in ("money", "money0"):
        return money(cfg, v, 2 if fmt == "money" else 0)
    if fmt == "text":
        return str(v)
    if fmt == "names":
        return ", ".join(v) or "—"
    if isinstance(v, dt.datetime):
        v = v.astimezone(zone).replace(tzinfo=None)
    return date_text(cfg, v, fmt)


def ledger(cfg, body):
    path, fmt = body.split("|")
    keys = path.split(".")
    cut = next(n for n in range(len(keys), 0, -1) if ".".join(keys[:n]) in LEDGER)
    value = inputs.value(".".join(keys[:cut]), cfg) if ".".join(keys[:cut]) in inputs.ROWS else LEDGER[".".join(keys[:cut])][cfg]
    for key in keys[cut:]:
        value = value[key]
    return value_text(cfg, value, fmt, None)


def population(text):
    return dict(part.split("=") for part in text.split("&") if part)


def params(c, pop, store):
    """A slot's population as the variables of its query (metrics.sql's header): shops, people and cards by the ids of
    this build."""
    cfg, out = c["cfg"], {"cfg": c["cfg"], "zone": inputs.value("geo.home_zone", c["cfg"])}
    for key, v in pop.items():
        if key == "site":
            out["sites"] = ",".join(c["ids"][store]["sites"][s] for s in {"all": [], "home": ["main", "east"]}.get(v, [v]))
        elif key in ("advisor", "closed_by", "person"):
            out[("not_" if v[0] == "!" else "") + key] = c["ids"][store]["people"][v.lstrip("!")]
        elif key == "card":
            out["card"] = str(ids.uuid("card", CARDS[v], cfg))
        elif key == "position":  # the desk is the service advisor's position
            out["position"] = inputs.load("cast.json")["roles"]["service_advisor" if v == "desk" else v][cfg]
        elif key != "terms":  # every account query reads the accounts billed on terms
            out[key] = v
    return out


def window(c, text, at, zone):
    """A period of metrics.json as wall-clock bounds [lo, hi) on the reader's clock, a period that reaches the instant
    ending at it; (None, None) for a state at the instant."""
    local = at.astimezone(zone).replace(tzinfo=None)
    d, mid = local.date(), lambda x: dt.datetime.combine(x, dt.time())
    monday = d - dt.timedelta(d.weekday())
    if text == "at":
        return None, None
    if text in ("d7", "d30", "d90"):
        return local - dt.timedelta(int(text[1:])), local
    if ".." in text:
        first, last = text.split("..")
        return mid(day(c, first, d)), min(local, mid(day(c, last, d) + dt.timedelta(1)))
    lo, hi = {"day": (d, d + dt.timedelta(1)), "prev_day": (d - dt.timedelta(1), d), "next_day": (d + dt.timedelta(1), d + dt.timedelta(2)),
              "week": (monday, monday + dt.timedelta(7)), "prev_week": (monday - dt.timedelta(7), monday),
              "next_two_weeks": (d, c["a"]["T"].date() + dt.timedelta(15))}[text]
    return mid(lo), mid(hi)


def price(c, pop, metric, d):
    """catalogue.list_price, catalogue.price_at_old_hour: the job's labour for the class at the hour in force on day d
    (before or after the rise P; at_old_hour always before it) plus each part line's option of the tier (a line with one
    option, that one) at today's list price, as catalogue.json reads (`price_rise`, `how_to_read`)."""
    if d < c["a"]["G"]:
        raise ValueError(f"assistant/{c['cfg']}: a price before go-live {d} would need the parts drift")
    job = next(j for j in inputs.load("catalogue.json")["jobs"] if j["key"] == pop["job"])[c["cfg"]]
    scale = (job.get("hours_by_class") or {}).get(pop["class"], 1)
    labour = job["labour_price"]["after_rise" if metric == "catalogue.list_price" and d >= c["a"]["P"] else "before_rise"] * scale
    parts = 0
    for line in job["parts"]:
        option = next((o for o in line["options"] if o["tier"] == pop["tier"]), line["options"][0] if len(line["options"]) == 1 else None)
        parts += line["qty"] * option["list_price"] * (scale if job.get("parts_scale_with_class") else 1)
    return Decimal(str(round(labour + parts, 2)))


def value(c, metric, pop, period, at, zone, bounds=None, extra=None):
    """A metric's value at instant `at` for a population and period, read on the reader's clock `zone`: from the
    catalogue, the task's schedule or its query (`c['measure']`); `bounds` replaces the period's, `extra` adds variables
    (a table's row)."""
    from traciora.core.scheduling import schedule_words
    from traciora.core.tools.workspace.scheduled_tasks import tasks

    if metric in SLICE:
        raise Held("slice", metric)
    if metric in UNDEFINED:
        raise Held("undefined", f"{metric}: {UNDEFINED[metric]}")
    if metric.startswith("catalogue."):
        return price(c, pop, metric, at.astimezone(zone).date())
    if metric == "tasks.next_run":
        task = next(x for x in c["files"]["tasks"]["tasks"] if x["id"] == pop["task"])
        expr = schedule_words.build(task["schedule"]["days"], task["schedule"]["times"], min_gap=tasks.MIN_INTERVAL_MINUTES)
        return tasks.next_due(expr, c["zone"], at)
    store = QUERIES[metric][0]
    if period == "prev_shift":  # metrics.json: the person's last worked day before the instant
        d = worked(c["a"], int(pop["person"]), at.astimezone(zone).date(), -1)
        bounds = (dt.datetime.combine(d, dt.time()), dt.datetime.combine(d + dt.timedelta(1), dt.time()))
    lo, hi = bounds or window(c, period, at, zone)
    p = params(c, pop, store) | {"at": at.isoformat(), "lo": "" if lo is None else str(lo), "hi": "" if hi is None else str(hi)} | (extra or {})
    if "advisor" in (extra or {}):
        p.pop("not_advisor", None)
    if metric.startswith("plan."):
        p["plan"] = str(inputs.value("s10.west_plan", c["cfg"])["orders" if metric == "plan.orders_share" else "revenue"])
    v = c["measure"](metric, p)
    if metric == "roster.free_people":
        return [c["names"][x] for x in (v or "").split(",") if x]
    if metric in ("calls.worst_check", "calls.best_check") and v:
        return check_name(c["cfg"], v)
    if metric == "bookings.first" and v:
        hm, customer, reason = v.split("|")
        return ", ".join(x for x in (clock_text(c["cfg"], dt.time(*map(int, hm.split(":")))), customer, reason) if x)
    return v


def field_text(c, key, v):
    """A table's row field: a day (short), a month, a band's hours, or the row's own words."""
    if v is None:
        return "—"
    if key in ("date", "week"):
        return date_text(c["cfg"], v, "short" if c["cfg"] == "en" else "numeric")
    if key == "month":
        return date_text(c["cfg"], v, "month")
    if key == "hours":
        return "–".join(clock_text(c["cfg"], t) for t in v)
    return str(v)


ORDER = {"share desc": lambda r: -(r["raw"].get("orders.discounted_share") or 0), "date desc": lambda r: -r["raw"]["date"].toordinal(),
         "month asc": lambda r: r["raw"]["month"], "week desc": lambda r: -r["raw"]["week"].toordinal(),
         "site, hours": lambda r: (r["raw"]["site"], r["raw"]["hours"]),
         "flagged first, then days since last visit desc": lambda r: (not r["raw"]["acct.flagged"], -(r["raw"]["acct.days_since_visit"] or 0)),
         "unapproved first, then date": lambda r: (r["raw"]["approver"] is not None, r["raw"]["date"])}


def check_name(cfg, key):
    """A scorecard check by its name in the tenant's scorecard. The seed gives the scorecard no Russian wording
    (calls/DESIGN.md, not in this plan), so a Russian text cannot name a check."""
    from traciora.core.phonecalls.config import load_phonecalls_config

    if cfg == "ru":
        raise Held("words", "the tenant's scorecard has no Russian names for its checks")
    return next(x.name for x in load_phonecalls_config().scorecard.checks if x.key == key)


def table(c, spec, at, zone):
    """A block of DESIGN.md section 6 as a Markdown table: its rows (a query's, or the months or full weeks of the
    period), each column a row field or a metric over the block's population narrowed to the row."""
    if f"rows.{spec['rows']}" in UNDEFINED:
        raise Held("undefined", f"rows.{spec['rows']}: {UNDEFINED['rows.' + spec['rows']]}")
    pop = population(spec["where"])
    lo, hi = window(c, spec["period"], at, zone)
    rows = []
    if spec["rows"] in ("month", "week"):
        start = lo.date().replace(day=1) if spec["rows"] == "month" else lo.date() + dt.timedelta(-lo.weekday() % 7)
        while dt.datetime.combine(start, dt.time()) < hi:
            end = tenant.months(start, 1) if spec["rows"] == "month" else start + dt.timedelta(7)
            if spec["rows"] == "month" or dt.datetime.combine(end, dt.time()) <= hi:  # a week row is a full week
                rows.append({"bounds": (max(lo, dt.datetime.combine(start, dt.time())), min(hi, dt.datetime.combine(end, dt.time()))),
                             "extra": {}, "raw": {spec["rows"]: start}})
            start = end
    else:
        store, _ = QUERIES[f"rows.{spec['rows']}"]
        found = c["measure"](f"rows.{spec['rows']}", params(c, pop, store) | {"at": at.isoformat(), "lo": "" if lo is None else str(lo),
                                                                               "hi": "" if hi is None else str(hi)}, many=True)
        key = {"advisor": "advisor", "order": "order", "account": "account", "gap": "band"}[spec["rows"]]
        for r in found:
            extra = {key: str(r["key"])} | ({"sites": str(r["site_id"])} if "site_id" in r else {})
            raw = {k: v for k, v in r.items() if k not in ("key", "site_id", "starts", "ends")} | ({"hours": (r["starts"], r["ends"])} if "starts" in r else {})
            rows.append({"bounds": None, "extra": extra, "raw": raw})

    def cells(row, where):
        out = []
        for _, column in spec["columns"]:
            if column[0] != "=":
                out.append(field_text(c, column, row["raw"].get(column)))
                continue
            metric, extra_pop, fmt = column[1:].split("|")
            v = value(c, metric, where | population(extra_pop), spec["period"], at, zone, row["bounds"], row["extra"])
            row["raw"][metric] = v
            out.append(value_text(c["cfg"], v, fmt, zone))
        return out

    for row in rows:
        row["cells"] = cells(row, pop)
        if spec["rows"] == "account":
            row["raw"]["acct.flagged"] = value(c, "acct.flagged", {}, "at", at, zone, extra=row["extra"])
    rows.sort(key=ORDER[spec["order"]])
    rows = rows[:spec.get("limit") or len(rows)]
    lines = [[header for header, _ in spec["columns"]]] + [row["cells"] for row in rows]
    if spec.get("extra_row"):
        extra_row = {"bounds": None, "extra": {}, "raw": {}}
        lines.append([spec["extra_row"]["label"]] + cells(extra_row, population(spec["extra_row"]["where"]))[1:])
    if spec.get("total"):
        sums = [sum(r["raw"][col[1:].split("|")[0]] or 0 for r in rows) if col[0] == "=" else None for _, col in spec["columns"]]
        fmts = [col.rsplit("|", 1)[1] if col[0] == "=" else None for _, col in spec["columns"]]
        lines.append([inputs.load("assistant/metrics.json")["table_total"][c["cfg"]]] + [value_text(c["cfg"], s, f, zone) for s, f in zip(sums[1:], fmts[1:])])
    return "\n".join(["| " + " | ".join(lines[0]) + " |", "|" + "---|" * len(lines[0])] + ["| " + " | ".join(x) + " |" for x in lines[1:]])


def fill(c, text, now, where, at=None, zone=None, blocks=None):
    """The text with its dates, ledger constants, computed values and tables written out, each computed one at instant
    `at` on the reader's clock `zone` and kept in `c['resolved']`; raises Held for an item that cannot be written."""
    used = re.findall(r"\{\{=([a-z_.]+)\|", text) + [col[1:].split("|")[0] for name in re.findall(r"\{\{#(\w+)\}\}", text)
                                                       for _, col in blocks[name]["columns"] if col[0] == "="]
    for metric in used:  # before anything is read: an item that needs a metric with no data in this slice is held first
        if metric in SLICE:
            raise Held("slice", metric)

    def one(m):
        body = m[1]
        if body[0] == "#":
            out = table(c, blocks[body[1:]], at, zone)
            c["resolved"].append({"item": where, "slot": m[0], "metric": body, "at": at, "value": None, "text": out})
            return out
        if body[0] == "=":
            metric, pop, period, fmt = body[1:].split("|")
            v = value(c, metric, population(pop), period, at, zone)
            out = value_text(c["cfg"], v, fmt, zone)
            c["resolved"].append({"item": where, "slot": m[0], "metric": metric, "at": at, "value": v, "text": out})
            return out
        if body[0] == "$":
            return ledger(c["cfg"], body[1:])
        when, fmt = body.rsplit("|", 1)
        out = date_text(c["cfg"], day(c, when, now), fmt)
        return out[:1].upper() + out[1:] if tenant.HEAD.search(text[:m.start()]) else out
    return SLOT.sub(one, text)


def lead(c, text, at, zone):
    """The first computed value of a text: a case whose leading figure is none or zero is not the data's case."""
    m = re.search(r"\{\{=([^{}]+)\}\}", text)
    if m is None:
        return True
    metric, pop, period, _ = m[1].split("|")
    return value(c, metric, population(pop), period, at, zone)


def context(cfg, a, who, sha, zone, measure, found):
    """What every mapping reads: the clock, each slot's ids (`who`: login, actor, account, rank number, clock, shifts), the
    product's commit, the scheduler's clock, the metrics' reader (`measurer`) and the build's ids it names (`found`)."""
    home = ZoneInfo(inputs.value("geo.home_zone", cfg))
    names = {str(ids.uuid("person", p["slot"], cfg)): p[cfg]["full_name"] for p in inputs.load("cast.json")["people"]}
    return {"cfg": cfg, "a": a, "events": tenant.events(a), "home": home, "T": a["T"].replace(tzinfo=home).astimezone(UTC),
            "who": who, "sha": f"{MODEL}+{sha}", "zone": zone, "held": [], "resolved": [], "measure": measure, "ids": found, "names": names,
            "files": {name: inputs.load(f"assistant/{cfg}/{name}.json") for name in FILES}}


def measurer(shop, core):
    """`c['measure']`: a metric's query of metrics.sql on the open shop or core connection, every variable it does not
    set ''; its `value`, or with `many` its rows."""
    from psycopg.rows import dict_row

    def measure(metric, variables, many=False):
        store, sql = QUERIES[metric]
        names = set(re.findall(r":'(\w+)'", sql))
        with (shop if store == "erp" else core).cursor(row_factory=dict_row) as cur:
            rows = cur.execute(re.sub(r":'(\w+)'", r"%(\1)s", sql), dict.fromkeys(names, "") | {k: v for k, v in variables.items() if k in names}).fetchall()
        return rows if many else rows[0]["value"] if rows else None
    return measure


def found_ids(cfg, shop_manifest, core):
    """The ids a slot's population names: per store, each shop key's location and each cast slot's person (an employee
    of the shop database, a core person)."""
    people = {k: str(v[0] if isinstance(v, list) else v) for k, v in shop_manifest["people"].items()}
    sites = dict(core.execute("SELECT a.value, l.id::text FROM core.location l JOIN core.location_alias a ON a.location_id = l.id"
                              " WHERE a.namespace = 'config_key'").fetchall())
    return {"erp": {"sites": {k: str(v) for k, v in shop_manifest["shops"].items()}, "people": people},
            "core": {"sites": sites, "people": {s["slot"]: str(ids.uuid("person", s["slot"], cfg)) for s in inputs.load("tenant/ladder.json")["slots"]}}}


def card_args(c, tool, card, item):
    """The arguments the model's call would have carried, from the seed record the card names."""
    f = c["files"]
    if tool == "remember_note":
        n = next(x for x in f["notes"]["notes"] if x["id"] == card["note"])
        return {"subject": n["subject"], "text": n["text"], "why": n["why"], "how_to_apply": n["how"]}
    if tool == "propose_team_note":
        p = texts(f, card["proposal"])
        return {"subject": p["subject"], "text": p["text"], "why": p["why"], "how_to_apply": p["how"]}
    if tool == "schedule_task":
        t = next(x for x in f["tasks"]["tasks"] if x["id"] == card["task"])
        return {"name": t["name"], "prompt": fill(c, t["prompt"], None, item), "times": t["schedule"]["times"], "days": t["schedule"]["days"]}
    board = next(x for x in inputs.load(f"workday/{c['cfg']}/cards.json")["cards"] if x["id"] == CARDS[card["board_card"]])
    when, offset = board["due"].split("@o+")
    opens = dt.datetime.combine(day(c, when), dt.time(*map(int, inputs.value("site.hours.weekday", c["cfg"])[0].split(":"))))
    place = next(p for p in inputs.load(f"tenant/roles-and-places.{c['cfg']}.json")["places"] if p["key"] == board["site"])
    hours, minutes = map(int, offset.split(":"))
    return {"title": board["title"], "due": f"{opens + dt.timedelta(hours=hours, minutes=minutes):%Y-%m-%dT%H:%M}",
            "site": place["name"], "description": board["description"], "priority": board["priority"]}


def texts(f, pid):
    """A proposal's four texts: its own, or the team note it published."""
    p = next(x for x in f["team"]["proposals"] if x["id"] == pid)
    return p if "text" in p else next(x for x in f["team"]["team_notes"] if x["id"] == p["published_as"])


def ack_turn(c, note, said, n=1):
    """The exchange that saves a note: the manager's words, an acknowledgement of patterns.json (the next in turn by the
    note's id) and the remember-note card."""
    acks = inputs.load(f"assistant/{c['cfg']}/patterns.json")["note_ack"]
    text = next(x["text"] for x in c["files"]["notes"]["notes"] if x["id"] == note)
    return {"n": n, "user": said, "tools": ["remember_note"], "assistant": acks[ids.number("ack", note, c["cfg"]) % len(acks)].replace("{note_text}", text),
            "card": {"tool": "remember_note", "answer": "save", "note": note}}


def chats(c):
    """Every chat the step writes, in one shape: the hand-written threads, then for each `auto` note the one exchange
    that saved it (`ack_turn`), at the note's time, titled with the note's subject."""
    f = c["files"]
    out = [{"key": t["id"], "owner": t["owner"]["slot"], "title": t["title"], "turns": t["turns"],
            "start": at(day(c, t["when"]), t["at"], c["who"][t["owner"]["slot"]]["zone"])} for t in f["threads"]["threads"]]
    for n in f["notes"]["notes"]:
        if "auto" in n["source"]:
            owner, turn = n["owner"]["slot"], ack_turn(c, n["id"], n["source"]["said"])
            saved = hour(c, n["id"], c["who"][owner]["zone"], day(c, n["when"]))
            out.append({"key": f"auto:{n['id']}", "owner": owner, "title": n["subject"], "turns": [turn],
                        "start": saved - dt.timedelta(seconds=6 + 7 * len(turn["tools"]))})
    return out


def threads(c):
    """The chats (`chats`): each its conversations row and its chat file's payload with every slot resolved; a chat that
    needs a metric of `SLICE` or `UNDEFINED`, or of `NOT_IN_V1`, as its note turns alone (`ack_turn`), one held for
    another reason not at all (`held`).
    Also the bindings its cards made, held or not: a note's (conversation, turn, time), a proposal's (time, its chat's
    last note binding or None), a task's time."""
    from traciora.core.agents.agent_memory import ANSWER_FEEDBACK_KEY, ANSWER_TRACES_KEY, MEMORY_SCHEMA_VERSION
    from traciora.core.agents.skill_registry import tool_label
    from traciora.core.common.i18n import t
    from traciora.core.human_decision import validate_answer
    from traciora.core.tools.workspace.board.decisions import CREATE_TASK_DECISION
    from traciora.core.tools.workspace.memory.memory_tools import DECISIONS
    from traciora.core.tools.workspace.scheduled_tasks.tasks import decisions

    specs = DECISIONS | decisions(None) | {"create_task": CREATE_TASK_DECISION}
    cfg, prose = c["cfg"], c["files"]["threads"]["prose_version"]
    notes = {n["id"]: n for n in c["files"]["notes"]["notes"]}
    out, bound = [], {}

    def build(thread):
        cid, owner, hold, binds = str(ids.uuid("thread", thread["key"], cfg)), c["who"][thread["owner"]], [], {}

        def written(text, when, where, blocks=None):
            try:
                return fill(c, text, when.astimezone(owner["zone"]).date(), where, when, owner["zone"], blocks)
            except Held as why:
                hold.append(why)
                return text

        q = thread["start"]
        first, messages, traces, thumbs, turns = q, [], {}, {}, {}
        for turn in thread["turns"]:
            item, tools = f"{thread['key']}#{turn['n']}", turn["tools"]
            tid = str(ids.uuid("turn", item, cfg))
            answer = q + dt.timedelta(seconds=6 + 7 * len(tools))
            events = [{"id": f"h{k}", "name": name, "display_name": tool_label(name), "done_name": t(f"tools_done.{name}"),
                       "status": "succeeded", "started_at": ms(q + dt.timedelta(seconds=2 + 7 * k)),
                       "ended_at": ms(q + dt.timedelta(seconds=7 + 7 * k)), "text_offset": 0} for k, name in enumerate(tools)]
            activity = {"tool_events": events}
            card = turn.get("card")
            if card:
                tool = card["tool"]
                # a note that takes another's place keeps its subject, as the product's card shows it
                known = {"subject": notes[card["note"]]["subject"]} if tool == "remember_note" and notes[card["note"]].get("replaces") else {}
                request = {**specs[tool].request(f"seed-{item}", tool, card_args(c, tool, card, item), known), "position": {"index": 1, "of": 1}}
                activity["decisions"] = [{"request": request, "answer": validate_answer(request, {"answer": card["answer"]}), "done": True,
                                          "text_offset": 0, "asked_at": events[tools.index(tool)]["started_at"]}]
                if tool == "remember_note":
                    turns[tid] = [len(turns) + 1, answer.isoformat()]
                    binds[card["note"]] = (cid, len(turns), answer)
                elif tool == "propose_team_note":
                    binds[card["proposal"]] = (answer, (cid, len(turns)) if turns else None)
                elif tool == "schedule_task":
                    binds[card["task"]] = answer
            traces[tid] = hashlib.sha256(f"{MODEL}:{item}".encode()).hexdigest()[:32]
            if turn.get("feedback"):
                thumbs[traces[tid]] = turn["feedback"]
            asked, said = q.isoformat(), answer.isoformat()
            messages += [
                {"type": "HumanMessage", "content": written(turn["user"], q, item), "timestamp": asked,
                 "additional_kwargs": {"timestamp": asked, "turn_id": tid}},
                {"type": "AIMessage", "content": written(turn["assistant"], answer, item, turn.get("blocks")), "timestamp": said,
                 "additional_kwargs": {"timestamp": said, "turn_id": tid, "activity": activity,
                                       "seed": {"seed": inputs.SEED.name, "prose": prose, "item": item}},
                 "response_metadata": {"model_name": MODEL}}]
            last, q = answer, answer + GAP
        metadata = {ANSWER_TRACES_KEY: traces, ANSWER_FEEDBACK_KEY: thumbs}
        if turns:
            metadata["memory_sql_provenance"] = {"login_id": owner["login"], "conversation_id": cid, "turns": turns}
        row = {"id": cid, "manager_id": owner["account"], "title": thread["title"],
               "created_at": utc(first), "replied_at": utc(last, "%Y-%m-%d %H:%M:%S.%f")[:-3],
               "read_at": utc(last + GAP, "%Y-%m-%d %H:%M:%S.%f")[:-3],
               "payload": {"schema_version": MEMORY_SCHEMA_VERSION, "user_id": cid, "last_updated": last.isoformat(),
                           "message_count": len(messages), "metadata": metadata, "messages": messages}}
        return row, binds, hold

    for thread in chats(c):
        resolved = len(c["resolved"])
        row, binds, hold = (None, {}, [Held("not in v1", NOT_IN_V1[thread["key"]])]) if thread["key"] in NOT_IN_V1 else build(thread)
        why, kind = sorted({h.what for h in hold}), hold and hold[0].kind
        if hold and all(h.kind in ("slice", "undefined", "not in v1") for h in hold):  # its note turns alone, so the notes saved in it open
            del c["resolved"][resolved:]
            lone = [ack_turn(c, x["card"]["note"], x["user"], n) for n, x in enumerate(
                (x for x in thread["turns"] if (x.get("card") or {}).get("tool") == "remember_note"), 1)]
            row, binds, hold = build(thread | {"turns": lone})
            c["held"].append({"item": f"thread {thread['key']}", "kind": kind, "why": "; ".join(why), "loaded": "its note turns alone"})
        elif hold:
            del c["resolved"][resolved:]
            c["held"].append({"item": f"thread {thread['key']}", "kind": hold[0].kind, "why": "; ".join(why), "loaded": "nothing"})
        bound |= binds
        if not hold:
            out.append(row)
    return out, bound


def notes(c, bound):
    """The personal notes, successors before the notes they replaced, each placed where the night's rule leaves it."""
    from traciora.core.memory import gates, store

    cfg, a, T = c["cfg"], c["a"], c["T"]
    ns = {n["id"]: n for n in c["files"]["notes"]["notes"]}
    after = {n["replaces"]: n for n in ns.values() if n.get("replaces")}
    agent = c["who"]["agent"]["actor"]

    def source(n):  # (conversation, turn, time)
        if "same_as" not in n["source"]:  # a hand-written thread or its own exchange (`chats`)
            return bound[n["id"]]
        return source(ns[n["source"]["same_as"]])

    def begins(n):
        s = n["source"]
        if "same_as" not in s:
            return source(n)[2]
        if ns[s["same_as"]]["ended"]["by"] == "nightly_tighten":
            return midnight(c, day(c, n["when"]))
        return hour(c, n["id"], c["who"][n["owner"]["slot"]]["zone"], day(c, n["when"]))

    rows, wrong = [], []
    for n in sorted(ns.values(), key=lambda n: n["state"] == "archived"):
        who = c["who"][n["owner"]["slot"]]
        refused = gates.reject_candidate(store.Candidate(n["class"], n["subject"], n["text"], n["why"], n["how"]))
        if refused:
            wrong.append(f"note {n['id']}: the product's gate refuses it ({refused})")
        conversation, turn, bound_at = source(n)
        start, nightly = begins(n), "same_as" in n["source"] and ns[n["source"]["same_as"]]["ended"]["by"] == "nightly_tighten"
        end = used = None
        if n["state"] == "archived":
            ended = n["ended"]
            end = begins(after[n["id"]]) if ended.get("superseded_by") else hour(c, f"{n['id']}:ended", who["zone"], day(c, ended["when"]))
            touched = end
        elif n["state"] == "dormant":
            used = hour(c, f"{n['id']}:used", who["zone"], day(c, n["last_used"]))
            touched = midnight(c, used.astimezone(c["home"]).date() + dt.timedelta(91))
            if not dt.timedelta(90) <= T - used < dt.timedelta(180) or touched > T:
                wrong.append(f"note {n['id']}: dormant, last used {used:%Y-%m-%d}, outside 90 to 180 days before T")
        else:
            used = max(start, hour(c, f"{n['id']}:used", who["zone"], worked(a, int(n["owner"]["slot"]), a["T"].date(), -1)))
            touched = start
            if T - used >= dt.timedelta(90):
                wrong.append(f"note {n['id']}: active, last used {used:%Y-%m-%d}, 90 days or more before T")
        token = store.subject_token(n["subject"])
        rows.append({
            "id": str(ids.uuid("note", n["id"], cfg)), "scope": "personal", "login_id": who["login"], "slug": store.slug_for(n["class"], token),
            "memory_class": n["class"], "subject_token": token, "subject": n["subject"], "text": n["text"], "why": n["why"], "how_to_apply": n["how"],
            "state": n["state"], "source_conversation_id": conversation, "source_turn": turn, "source_at": bound_at, "valid_from": start,
            "valid_to": end, "superseded_by": str(ids.uuid("note", n["ended"]["superseded_by"], cfg)) if n.get("ended", {}).get("superseded_by") else None,
            "use_count": 0 if used is None else 1, "last_used_at": used, "release_sha_written": c["sha"],
            "created_by": agent if nightly else who["actor"], "updated_by": agent if n["state"] == "dormant" or nightly or
            n.get("ended", {}).get("by") == "nightly_tighten" else who["actor"], "created_at": start, "updated_at": touched})
    return rows, wrong


def team(c, bound):
    """The team notes and the proposals: each proposal with its proposer, decider and times; each team note published by
    its approved proposal, its 90-day check kept or waiting."""
    from traciora.core.memory import gates, store

    cfg, T, f, who = c["cfg"], c["T"], c["files"]["team"], c["who"]
    retest = dt.timedelta(LEDGER["mem.retest_days"]["value"])
    ranks = c["ranks"]
    when, rows, proposals, wrong = {}, [], [], []
    for p in f["proposals"]:
        if p["by"] == "nightly":
            proposed = midnight(c, day(c, p["proposed"].removeprefix("night after ")) + dt.timedelta(1))
        elif "thread" in (p.get("source") or {}):
            proposed = bound[p["id"]][0]
        else:
            proposed = hour(c, f"{p['id']}:proposed", who[p["by"]["slot"]]["zone"], day(c, p["proposed"]))
        decided = None
        if p["status"] != "proposed":
            decided = max(hour(c, f"{p['id']}:decided", who[p["decided_by"]["slot"]]["zone"], day(c, p["decided"])), proposed + dt.timedelta(hours=2))
        when[p["id"]] = (proposed, decided)
    published = {n["proposal"]: str(ids.uuid("team_note", n["id"], cfg)) for n in f["team_notes"]}
    for n in f["team_notes"]:
        refused = gates.reject_candidate(store.Candidate("practice", n["subject"], n["text"], n["why"], n["how"]), team=True)
        if refused:
            wrong.append(f"team note {n['id']}: the product's gate refuses it ({refused})")
        p = next(x for x in f["proposals"] if x["id"] == n["proposal"])
        approver, approved = who[p["decided_by"]["slot"]], when[p["id"]][1]
        review, confirmed, by = n.get("review"), approved, approver
        if n.get("lowered"):
            by = who[n["lowered"]["by"]["slot"]]
        if review and review["answer"] == "keep":
            days = int(re.fullmatch(r"approved\+(\d+)d", review["due"])[1])
            by = who[review["by"]["slot"]]
            confirmed = hour(c, f"{n['id']}:review", by["zone"], approved.astimezone(c["home"]).date() + dt.timedelta(days))
        if (confirmed + retest > T) != (n["state"] == "active"):
            wrong.append(f"team note {n['id']}: {n['state']}, its check due {confirmed + retest:%Y-%m-%d} (T {T:%Y-%m-%d})")
        source = (bound.get(p["id"]) or (None, None))[1]
        token = store.subject_token(n["subject"])
        rows.append({
            "id": published[n["proposal"]], "scope": "business", "login_id": None, "slug": store.slug_for("practice", token),
            "memory_class": "practice", "subject_token": token, "subject": n["subject"], "text": n["text"], "why": n["why"], "how_to_apply": n["how"],
            "state": n["state"], "min_rank": ranks[n["visible_from"]], "approved_by_login_id": approver["login"], "approved_at": approved,
            "last_confirmed_at": confirmed, "next_retest_at": confirmed + retest, "source_conversation_id": source[0] if source else None,
            "source_turn": source[1] if source else 1, "valid_from": approved, "release_sha_written": c["sha"],
            "created_by": approver["actor"], "updated_by": by["actor"], "created_at": approved, "updated_at": confirmed})
    for p in f["proposals"]:
        night, body = p["by"] == "nightly", texts({"team": f}, p["id"])
        owner = None if night else who[p["by"]["slot"]]
        decider = who[p["decided_by"]["slot"]] if p.get("decided_by") else None
        proposed, decided = when[p["id"]]
        rank = ranks[p["visible_from"]] if night else owner["rank"]
        source = (bound.get(p["id"]) or (None, None))[1]
        proposals.append({
            "id": str(ids.uuid("proposal", p["id"], cfg)), "owner_login_id": owner and owner["login"], "status": p["status"],
            "subject": body["subject"], "subject_token": store.subject_token(body["subject"]), "text": body["text"], "why": body["why"],
            "how_to_apply": body["how"], "reason": p.get("reason"), "proposer_rank": rank, "min_rank": rank,
            "holders_count": len(p["holders"]) if night else None, "dream_night": proposed.astimezone(c["home"]).date() if night else None,
            "source_conversation_id": source[0] if source else None, "source_turn": source[1] if source else None,
            "approver_login_id": decider and decider["login"], "decided_at": decided,
            "published_at": decided if p["status"] == "approved" else None,
            "published_as": f"memory:{published[p['id']]}" if p["status"] == "approved" else None,
            "created_by": who["agent"]["actor"] if night else owner["actor"], "updated_by": (decider or owner or who["agent"])["actor"],
            "created_at": proposed, "updated_at": decided or proposed})
    return rows, proposals, wrong


def run_id(cfg, job, index):
    return -(ids.number("runs", job, cfg, bits=40) * RUNS_PER_JOB + RUNS_PER_JOB - 1 - index)


def jobs(c, bound):
    """The tasks and the briefs: each job with its runs, in time order. A task runs at its last due time before T, on the
    case the calendar gives it, else the first whose leading figure the data gives (`lead`), the wording in turn; the
    briefs of `at_t` are the first run of T's brief day, a later time before T skipped as the product skips one whose
    brief before it is unread. A job's runs stand together: a job one of whose texts cannot be written is not made
    (`held`), so the scheduler owes it nothing at start."""
    from traciora.core.common.prompts import load_client_prompt
    from traciora.core.common.i18n import t
    from traciora.core.scheduling import schedule_words
    from traciora.core.tools.workspace import brief
    from traciora.core.tools.workspace.scheduled_tasks import tasks

    cfg, T, zone, f = c["cfg"], c["T"], c["zone"], c["files"]["tasks"]
    prose = f["prose_version"]

    def run(key, case, wording, answer, instruction, due, started, seconds, kind="scheduled", status="ok", error=None):
        finished = started + dt.timedelta(seconds=seconds)
        return {"key": key, "kind": kind, "status": status, "due_at": due and stamp(due), "started_at": stamp(started),
                "finished_at": stamp(finished), "duration_ms": seconds * 1000, "answer": answer,
                "instruction": f"{instruction}\n\n[seed {inputs.SEED.name} · {key} · {case}/{wording} · {prose}]", "error_text": error,
                "updated_at": stamp(finished)}

    out, hold = [], {}

    def answered(key, text, when, reader, where, blocks):
        try:
            return fill(c, text, when.astimezone(reader).date(), where, when, reader, blocks)
        except Held as why:
            hold.setdefault(key, []).append(why)
            return text

    def chosen(task, when, reader):
        """The calendar's case, else the first case whose leading figure is neither none nor zero; the case "nothing"
        (nothing to report) when it is reached."""
        key, read = task["id"], when.astimezone(zone).date() + dt.timedelta(CASE_DAY.get(task["id"], 0))
        if key in CASE_DAY and clock.closed(cfg, read) and "closed" in task["cases"]:
            return "closed"
        if key in CASE_DAY and read.weekday() == 5 and "saturday" in task["cases"]:
            return "saturday"
        for case, wordings in task["cases"].items():
            if case in ("closed", "saturday"):
                continue
            try:
                if case == "nothing" or lead(c, wordings[0], when, reader):
                    return case
            except Held:
                return case
        return next(iter(task["cases"]))

    for task in f["tasks"]:
        owner, key = c["who"][task["owner"]["slot"]], task["id"]
        sliced = SLICE & set(re.findall(r"=([a-z_.]+)\|", json.dumps([task["prompt"], task["cases"], task.get("blocks")], ensure_ascii=False)))
        if sliced:  # a job whose texts read a day's call volume is not in v1, whichever case a build would pick
            c["held"].append({"item": f"job {key}", "kind": "slice", "why": "; ".join(sorted(sliced)), "loaded": "not made"})
            continue
        expr = schedule_words.build(task["schedule"]["days"], task["schedule"]["times"], min_gap=tasks.MIN_INTERVAL_MINUTES)
        made = bound[key] if "created_in" in task else hour(c, f"{key}:created", owner["zone"], day(c, task["created"]))
        prompt = fill(c, task["prompt"], made.astimezone(zone).date(), key)
        def nth(until):  # the run of due time `until` is the task's n-th
            n, due = 0, tasks.next_due(expr, zone, made)
            while due <= until:
                n, due = n + 1, tasks.next_due(expr, zone, due + dt.timedelta(seconds=1))
            return n

        last, runs = tasks.last_due(expr, zone, T), []
        for planted in task.get("planted_runs") or []:
            started_text = planted["started"]
            due = planted["due"] and at(day(c, RUN_AT.fullmatch(planted["due"])[1]), RUN_AT.fullmatch(planted["due"])[2], zone)
            started = due if started_text == "due" else at(day(c, RUN_AT.fullmatch(started_text)[1]), RUN_AT.fullmatch(started_text)[2], zone)
            seconds = int(planted["finished"].removeprefix("due+").removesuffix("s")) if "finished" in planted else 20 + ids.number("seconds", f"{key}:{started_text}", cfg) % 71
            case = planted.get("case", planted["status"])
            wording = planted.get("wording") or (nth(due) - 1) % len(task["cases"][case]) + 1 if "case" in planted else 1
            answer = (answered(key, task["cases"][case][wording - 1], started, owner["zone"], f"{key} {case}/{wording} {started:%Y-%m-%d}", task.get("blocks"))
                      if "case" in planted else None)
            runs.append(run(key, case, wording, answer, prompt, due, started, seconds, planted["kind"], planted["status"], planted.get("error_text")))
        case = chosen(task, last, owner["zone"])
        wording = (nth(last) - 1) % len(task["cases"][case]) + 1
        runs.append(run(key, case, wording, answered(key, task["cases"][case][wording - 1], last, owner["zone"], f"{key} {case}/{wording} {last:%Y-%m-%d}",
                                                     task.get("blocks")), prompt, last, last, 20 + ids.number("seconds", f"{key}:last", cfg) % 71))
        runs.sort(key=lambda r: r["started_at"])
        out.append({"key": key, "id": ids.number("task", key, cfg), "brief": False, "owner": owner["account"],
                    "slug": tasks._slugify(task["name"], owner["account"]), "name": task["name"], "cron_expr": expr, "prompt": prompt,
                    "at": made, "runs": runs, "seen": None})
    briefs = f["briefs"]
    reads = {b["owner"]["slot"]: b for b in briefs["at_t"]}
    instruction = load_client_prompt("brief.md")
    for slot in briefs["jobs_for"]:
        owner, key = c["who"][slot], f"brief-{slot}"
        runs, seen = [], None
        if slot in reads:
            plan = brief.plan_at(owner["shifts"], now=T, zone=c["home"])
            first = plan.runs[0]
            if first > T:
                raise SystemExit(f"assistant: slot {slot}'s first brief of T's brief day is at {first}, after T")
            points = []
            for n, point in enumerate(reads[slot]["points"], 1):
                sliced = SLICE & set(re.findall(r"\{\{=([a-z_.]+)\|", point))
                if sliced:
                    c["held"].append({"item": f"{key} point {n}", "kind": "slice", "why": "; ".join(sorted(sliced)), "loaded": f"{key} without it"})
                    continue
                if f"{key} point {n}" in NOT_IN_V1 and not lead(c, point, first, plan.zone):
                    c["held"].append({"item": f"{key} point {n}", "kind": "not in v1", "why": NOT_IN_V1[f"{key} point {n}"],
                                      "loaded": f"{key} without it"})
                    continue
                points.append(answered(key, point, first, plan.zone, f"{key} at_t", None))
            points = "\n".join(points)
            header = brief.header(now=first, plan=plan, following=None, previous=None)
            runs.append(run(key, "at_t", 1, points, f"{header}\n\n{instruction}", first, first, 20 + ids.number("seconds", key, cfg) % 71))
            runs += [{"key": key, "kind": "scheduled", "status": "skipped", "due_at": stamp(later), "error_text": brief.UNREAD}
                     for later in plan.runs[1:] if later <= T]
            seen = stamp(plan.before + GAP)
        out.append({"key": key, "id": ids.number("brief", slot, cfg), "brief": True, "owner": owner["account"],
                    "slug": f"brief-{owner['account']}", "name": t("home.brief.name"), "cron_expr": "", "prompt": instruction,
                    "at": midnight(c, c["a"]["G"]), "runs": runs, "seen": seen})
    made = []
    for job in out:
        for index, r in enumerate(job["runs"]):
            r["id"] = run_id(cfg, job["key"], index)
        why = sorted({h.what for h in hold.get(job["key"], [])})
        if not why:
            made.append(job)
            continue
        c["resolved"][:] = [r for r in c["resolved"] if r["item"].split(" ")[0] != job["key"]]
        kinds = {h.kind for h in hold[job["key"]]}
        c["held"].append({"item": f"job {job['key']}", "kind": "slice" if "slice" in kinds else sorted(kinds)[0], "why": "; ".join(why), "loaded": "not made"})
    return made


def records(c):
    """Everything the step writes, as rows and payloads, for the configuration's locale; nothing is written."""
    from traciora.core.common.i18n import locale_scope

    with locale_scope(c["cfg"]):
        conversations, bound = threads(c)
        personal, wrong = notes(c, bound)
        business, proposals, refused = team(c, bound)
        return {"threads": conversations, "notes": personal + business, "proposals": proposals, "jobs": jobs(c, bound),
                "wrong": wrong + refused, "held": c["held"], "resolved": c["resolved"]}


def product_sha():
    """The product checkout's commit (the step runs in it), else 'unknown'."""
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


def people(cfg, conn):
    """Each ranked slot's login, actor, account, rank number, clock and shifts around T, by the people step's keys; and
    the actor the night writes as."""
    from traciora.core.auth.manager import AuthManager
    from traciora.core.queries.home import brief_shifts
    from traciora.core.security.actors import actor
    from traciora.core.tools.workspace import brief

    a = clock.anchors(cfg, manifest.at())
    T = a["T"].date()
    ranks = dict(conn.execute("SELECT key, rank FROM core.access_level WHERE active").fetchall())
    zones = {p["key"]: p["tz"] for p in inputs.load(f"tenant/roles-and-places.{cfg}.json")["places"]}
    auth, who = AuthManager(), {}
    for s in inputs.load("tenant/ladder.json")["slots"]:
        if s["rank"] == "none":
            continue
        found = conn.execute("SELECT id::text, actor_id::text FROM identity.login WHERE person_id = %s",
                             (str(ids.uuid("person", s["slot"], cfg)),)).fetchone()
        account = auth.get_manager_by_username(s[f"username_{cfg}"], include_inactive=True)
        if found is None or account is None:
            raise SystemExit(f"assistant: slot {s['slot']} has no sign-in; run the step people first")
        shifts = brief_shifts(conn, None, accounts=brief._logins([account["id"]]), days=[T + dt.timedelta(n) for n in range(-2, 3)])
        who[s["slot"]] = {"login": found[0], "actor": found[1], "account": int(account["id"]), "rank": ranks[s["rank"]],
                          "zone": ZoneInfo(zones[s["home"]] if s["home"] else inputs.value("geo.home_zone", cfg)),
                          "shifts": shifts.get(int(account["id"]), [])}
    who["agent"] = {"actor": actor(conn, "agent", MODEL)}
    return a, who, ranks


MEMORY = ("id", "scope", "login_id", "slug", "memory_class", "subject_token", "min_rank", "approved_by_login_id", "approved_at",
          "valid_from", "valid_to", "superseded_by", "release_sha_written", "state", "source_conversation_id", "source_turn", "source_at",
          "last_confirmed_at", "last_used_at", "use_count", "next_retest_at", "created_at", "created_by", "updated_at", "updated_by")
PROPOSAL = ("id", "owner_login_id", "status", "subject_token", "proposer_rank", "min_rank", "holders_count", "dream_night",
            "source_conversation_id", "source_turn", "approver_login_id", "published_as", "decided_at", "published_at", "created_at",
            "created_by", "updated_at", "updated_by")


@contextlib.contextmanager
def mapping(cfg, client_id):
    """The open core connection and the mapping's context on a loaded build, its metrics read from the core database
    and, read-only, the shop database."""
    import psycopg
    from traciora.core.core_db.engine import connect, tenant_dsn
    from traciora.core.scheduling.cron_store import scheduler_zone

    dsn = manifest.shop_dsn(client_id)
    if manifest.read(dsn).get("cfg") != cfg:
        raise SystemExit(f"assistant: the shop database is not built for {cfg}")
    with connect(tenant_dsn(client_id)) as conn, psycopg.connect(dsn) as shop:
        shop.read_only = True
        a, who, ranks = people(cfg, conn)
        yield conn, context(cfg, a, who, product_sha(), scheduler_zone(), measurer(shop, conn), found_ids(cfg, manifest.read(dsn), conn)) | {"ranks": ranks}


def step(cfg, client_id, replace):
    from traciora.core.agents.agent_memory import FileBasedMemory
    from traciora.core.auth.manager import AuthManager
    from traciora.core.commands.memory import PCOL
    from traciora.core.memory.store import COL
    from traciora.core.scheduling.cron_store import CronStore
    from traciora.core.security import envelope
    from traciora.core.tools.workspace.scheduled_tasks import tasks

    if replace:
        reset(cfg, client_id)
    auth = AuthManager()
    with mapping(cfg, client_id) as (conn, c):
        if conn.execute("SELECT count(*) FROM platform.memory WHERE id = ANY(%s::uuid[])", (own(cfg)["memory"],)).fetchone()[0]:
            raise SystemExit("assistant: its rows are loaded; run it with --replace")
        built = records(c)
        if built["wrong"]:
            raise SystemExit("assistant: the seed files and the product disagree:\n  " + "\n  ".join(built["wrong"]))
        for row in built["notes"]:
            sealed = {f"{k}_enc": envelope.encrypt(row[k], COL[k]) for k in ("subject", "text", "why", "how_to_apply")}
            values = {k: row[k] for k in MEMORY if k in row} | sealed
            conn.execute(f"INSERT INTO platform.memory ({', '.join(values)}) VALUES ({', '.join(['%s'] * len(values))})", list(values.values()))
        for row in built["proposals"]:
            sealed = {f"{k}_enc": envelope.encrypt(row[k], PCOL[k]) for k in ("subject", "text", "why", "how_to_apply", "reason") if row[k] is not None}
            values = {k: row[k] for k in PROPOSAL} | sealed
            conn.execute(f"INSERT INTO platform.proposal ({', '.join(values)}) VALUES ({', '.join(['%s'] * len(values))})", list(values.values()))
        conn.commit()
    memory, rows = FileBasedMemory(), len(built["notes"]) + len(built["proposals"])
    with contextlib.closing(sqlite3.connect(auth.db_path)) as db:
        for t in built["threads"]:
            db.execute("INSERT INTO conversations (id, manager_id, title, created_at, replied_at, read_at, title_set_by_person) VALUES (?, ?, ?, ?, ?, ?, 0)",
                       (t["id"], t["manager_id"], t["title"], t["created_at"], t["replied_at"], t["read_at"]))
        db.commit()
    for t in built["threads"]:
        memory._write_payload(memory._get_file_path(t["id"]), t["payload"])
    rows += 2 * len(built["threads"])
    store = CronStore(auth.db_path)
    for job in built["jobs"]:
        if job["brief"]:
            made = tasks.ensure_brief(store, auth, manager_id=job["owner"], locale=cfg)
        else:
            slug, n = job["slug"], 1
            while store.get_prompt_job(slug):
                n, slug = n + 1, f"{job['slug'][:56]}-{n + 1}"
            job["slug"] = slug
            made = store.create_prompt_job(slug=slug, name=job["name"], cron_expr=job["cron_expr"], prompt_text=tasks._seal(auth, job["prompt"]),
                                           output_kind="store", output_chat_id=None, created_by=job["owner"])
        if made:  # the job is this step's: its id and its time are the seed's
            with contextlib.closing(sqlite3.connect(auth.db_path)) as db:
                db.execute("UPDATE cron_prompt_jobs SET id = ?, created_at = ?, updated_at = ? WHERE slug = ?",
                           (job["id"], utc(job["at"]), utc(job["at"]), job["slug"]))
                db.commit()
            rows += 1
        for r in job["runs"]:
            fields = {k: v for k, v in r.items() if k not in ("key", "answer", "instruction")}
            if "instruction" in r:
                fields |={"answer_enc": tasks._seal(auth, r["answer"]), "instruction_enc": tasks._seal(auth, r["instruction"])}
            store.add_run(task_slug=job["slug"], owner_id=job["owner"], **fields)
            rows += 1
        if job["seen"]:
            auth.mark_brief_seen(job["owner"], job["seen"])
    return rows


def own(cfg):
    """The ids this step gives its rows in one configuration (`reset` takes both): memory, proposals, threads, jobs, runs."""
    f = {name: inputs.load(f"assistant/{cfg}/{name}.json") for name in FILES}
    tasks = [t["id"] for t in f["tasks"]["tasks"]]
    slots = f["tasks"]["briefs"]["jobs_for"]
    keys = tasks + [f"brief-{s}" for s in slots]
    return {"memory": [str(ids.uuid("note", n["id"], cfg)) for n in f["notes"]["notes"]] +
                      [str(ids.uuid("team_note", n["id"], cfg)) for n in f["team"]["team_notes"]],
            "proposals": [str(ids.uuid("proposal", p["id"], cfg)) for p in f["team"]["proposals"]],
            "threads": [str(ids.uuid("thread", t["id"], cfg)) for t in f["threads"]["threads"]] +
                       [str(ids.uuid("thread", f"auto:{n['id']}", cfg)) for n in f["notes"]["notes"] if "auto" in n["source"]],
            "jobs": [ids.number("task", k, cfg) for k in tasks] + [ids.number("brief", s, cfg) for s in slots],
            "runs": [run_id(cfg, k, i) for k in keys for i in range(RUNS_PER_JOB)],
            "readers": [b["owner"]["slot"] for b in f["tasks"]["briefs"]["at_t"]]}


def reset(cfg, client_id):
    """Both configurations' rows and files: the memory and proposal rows, the conversations with their chat files, the
    jobs the step made with their runs, the runs it wrote, the readers' brief_seen_at. The night's actor stays."""
    from traciora.core.agents.agent_memory import FileBasedMemory
    from traciora.core.auth.manager import AuthManager
    from traciora.core.core_db.engine import connect, tenant_dsn

    mine = [own(c) for c in ("en", "ru")]
    pick = lambda key: [x for m in mine for x in m[key]]  # noqa: E731
    with connect(tenant_dsn(client_id)) as conn:
        conn.execute("DELETE FROM platform.proposal WHERE id = ANY(%s::uuid[])", (pick("proposals"),))
        conn.execute("DELETE FROM platform.memory WHERE id = ANY(%s::uuid[])", (pick("memory"),))
        conn.commit()
    auth, memory = AuthManager(), FileBasedMemory()
    usernames = {s["slot"]: s for s in inputs.load("tenant/ladder.json")["slots"]}
    readers = [a["id"] for m, c in zip(mine, ("en", "ru")) for a in (auth.get_manager_by_username(usernames[s][f"username_{c}"], include_inactive=True)
                                                                     for s in m["readers"]) if a]
    marks = lambda n: ",".join("?" * n)  # noqa: E731
    with contextlib.closing(sqlite3.connect(auth.db_path)) as db:
        threads, jobs, runs = pick("threads"), pick("jobs"), pick("runs")
        db.execute(f"DELETE FROM conversations WHERE id IN ({marks(len(threads))})", threads)
        slugs = [r[0] for r in db.execute(f"SELECT slug FROM cron_prompt_jobs WHERE id IN ({marks(len(jobs))})", jobs)]
        db.execute(f"DELETE FROM cron_runs WHERE task_slug IN ({marks(len(slugs))})", slugs)
        db.execute(f"DELETE FROM cron_prompt_jobs WHERE id IN ({marks(len(jobs))})", jobs)
        for chunk in range(0, len(runs), 500):
            db.execute(f"DELETE FROM cron_runs WHERE id IN ({marks(len(runs[chunk:chunk + 500]))})", runs[chunk:chunk + 500])
        # brief_seen_at only says which of a brief job's briefs its reader has seen; a reader whose job the step made loses
        # that job with all its briefs here, so no reading of theirs is left to keep: null is the account's state before it
        readers = [r for r in readers if f"brief-{r}" in slugs]
        if readers:
            db.execute(f"UPDATE managers SET brief_seen_at = NULL WHERE id IN ({marks(len(readers))})", readers)
        db.commit()
    for thread in threads:
        path = memory._get_file_path(thread)
        path.unlink(missing_ok=True)
        Path(path).with_suffix(".lock").unlink(missing_ok=True)
