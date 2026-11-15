"""The build's clock: T and every anchor of `stories/TIMELINE.md` (rule R6), computed once from the build instant, with
rule A of `erp/generator-spec.md` section 1, and the day of every call and conversation story file."""
import datetime as dt
import re

from seeder import inputs

D, DAY = dt.date, dt.timedelta(1)
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
WDAY = "(" + "|".join(WEEKDAYS) + ")"
PHASE_B = (6, 29, 17, 24)  # ledger roster.advisor_pattern: the ru advisors who work T and T+1
WEEKDAY_STAFF = (3, 4, 8, 9, 22)  # ledger roster.manager_pattern (ru)
# ledger roster.mechanic_days_off (ru): slot 20, the one mechanic a story anchors to
RU_MECHANIC_DAYS_OFF = {20: tuple([w[:3] for w in WEEKDAYS].index(x) for x in inputs.value("roster.mechanic_days_off", "ru")["20"].split())}
# ledger site.open_days (en, main): the flagship's Saturday morning
EN_SATURDAY = tuple((int(h), int(m)) for h, m in re.findall(r"(\d\d):(\d\d)", inputs.value("site.open_days", "en")["main"].split("Saturday")[1]))
# The conversation days rule A moves into L (generator-spec.md section 1): the stocktake, the booking of nf.conv.08 and
# the days placed beside them.
WEEK_BOUND = {"en": {3: {"T+6d": "stocktake"}, 7: {"T+6d": "stocktake"}, 8: {"T+6d": "stocktake", "T+5d": "booking", "T+7d": "after_stocktake"}},
              "ru": {7: {"T+6d": "stocktake"}, 8: {"T+6d": "stocktake", "T+3d": "booking", "T+8d": "after_stocktake"}}}


def observed(d):
    return d - DAY if d.weekday() == 5 else d + DAY if d.weekday() == 6 else d


def en_closed(y):
    may31, sep1, nov1 = D(y, 5, 31), D(y, 9, 1), D(y, 11, 1)
    memorial = may31 - dt.timedelta(may31.weekday())
    labor = sep1 + dt.timedelta((7 - sep1.weekday()) % 7)
    thanks = nov1 + dt.timedelta((3 - nov1.weekday()) % 7 + 21)
    return {observed(D(y, 1, 1)), memorial, observed(D(y, 7, 4)), labor, thanks, observed(D(y, 12, 25)), observed(D(y + 1, 1, 1))}


def closed(cfg, d):  # ledger site.closed_dates
    return d in en_closed(d.year) if cfg == "en" else (d.month, d.day) in ((1, 1), (1, 2))


def full_open(cfg, d):  # a full open day for every shop: en weekdays, ru every day
    return not closed(cfg, d) and (cfg == "ru" or d.weekday() < 5)


def main_open(cfg, d):  # the flagship is open: en also on Saturday morning
    return not closed(cfg, d) and (cfg == "ru" or d.weekday() < 6)


def snap(cfg, d, step=1):
    while not full_open(cfg, d):
        d += dt.timedelta(step)
    return d


def wd(cfg, d, n):  # the n-th full open day after (n > 0) or before (n < 0) d
    step = 1 if n > 0 else -1
    for _ in range(abs(n)):
        d += dt.timedelta(step)
        while not full_open(cfg, d):
            d += dt.timedelta(step)
    return d


def months_back(t, m):  # T-m months, the day clamped to 28
    y, mo = divmod(t.year * 12 + t.month - 1 - m, 12)
    return D(y, mo + 1, min(t.day, 28))


def ordinal(word):  # "last" is the 1st; "14th" the 14th
    return 1 if word == "last" else int(re.match(r"\d+", word).group())


def anchors(cfg, when):
    """`place` at `when`, or, when the anchors' order cannot hold on that day, at the same hour of the latest of the 14 days
    before on which it does: a build never stops on the clock. `at` is the instant placed, `asked` the one asked."""
    for back in range(15):
        try:
            return place(cfg, when - back * DAY) | {"asked": when}
        except ValueError as e:
            first = first if back else e
    raise first


def place(cfg, when):
    """Every date of the build for configuration `cfg` and the run instant `when` (a naive datetime on the home clock)."""
    weekday = tuple(tuple(map(int, x.split(":"))) for x in inputs.value("site.hours.weekday", cfg))

    def hours(d):  # the flagship's opening and closing on day d
        return EN_SATURDAY if cfg == "en" and d.weekday() == 5 else weekday

    # ledger time.t_rule: on a closed date, before opening or after closing, T is the close of the flagship's last open day
    day, t = when.date(), when
    if not main_open(cfg, day) or (when.hour, when.minute) < hours(day)[0]:
        day -= DAY
        while not main_open(cfg, day):
            day -= DAY
        t = dt.datetime.combine(day, dt.time(*hours(day)[1]))
    elif (when.hour, when.minute) > hours(day)[1]:
        t = dt.datetime.combine(day, dt.time(*hours(day)[1]))
    T = t.date()
    w0 = T - dt.timedelta(T.weekday())

    def W(k, dow=0):  # the day of week W+k (k < 0: week T-k)
        return w0 + dt.timedelta(7 * k + dow)

    def week_day(k, dow):  # the <weekday> of week W+k; a closed date moves to the next full open day
        d = W(k, dow)
        return snap(cfg, d) if closed(cfg, d) else d

    def works(slot, d):
        if not full_open(cfg, d) and not (cfg == "en" and d == T):
            return False
        if cfg == "en" or slot in WEEKDAY_STAFF:
            return d.weekday() < 5 or d == T
        if slot in RU_MECHANIC_DAYS_OFF:
            return d.weekday() not in RU_MECHANIC_DAYS_OFF[slot]
        phase_b = (d - T).days % 4 in (0, 1)
        return phase_b if slot in PHASE_B else not phase_b

    def pd(slot, n, d=None):  # slot's n-th working day after (n > 0) or before (n < 0) d, T by default
        d, step = d or T, 1 if n > 0 else -1
        for _ in range(abs(n)):
            d += dt.timedelta(step)
            while not works(slot, d):
                d += dt.timedelta(step)
        return d

    def on(slot, d, step=1):  # slot's first working day on or after d (step 1), or last on or before it (step -1)
        while not works(slot, d):
            d += dt.timedelta(step)
        return d

    def pair_start(slot, d):  # the first day of a working pair of slot on or after d
        while not (works(slot, d) and not works(slot, d - DAY)):
            d += DAY
        return d

    a = {"T": t, "W0": w0, "at": when}
    a["history_start"] = snap(cfg, months_back(T, inputs.value("time.history_months", cfg)))
    a["bought"] = snap(cfg, months_back(T, inputs.value("time.west_bought_months", cfg)))
    a["s2_start"] = snap(cfg, T - dt.timedelta(335))
    a["f3_resigns"] = week_day(-30, 0)
    a["a5_comebacks"] = (week_day(-26, 1), week_day(-22, 1))
    G = a["G"] = snap(cfg, T - dt.timedelta(175))
    P = T - dt.timedelta(150)
    a["P"] = snap(cfg, P + dt.timedelta((7 - P.weekday()) % 7))
    s9_first = a["s9_first"] = G + dt.timedelta((7 - G.weekday()) % 7)
    a["s2_found"], a["s2_follow_up"] = wd(cfg, G, 5), wd(cfg, G, 10)
    fired = a["fired"] = wd(cfg, G, 15)
    a["rule_on"] = wd(cfg, fired, 1)
    a["call21"] = on(5, week_day(-20, 1))
    a["a5_last_visit"] = snap(cfg, W(-20, 3), -1)
    complaint = a["a5_complaint"] = week_day(-19, 1)
    a["a5_misses"] = tuple(snap(cfg, complaint + dt.timedelta(k)) for k in (1, 6, 9))
    a["f2_fired"], a["slot14_starts"], a["slot7_starts"] = week_day(-17, 0), week_day(-15, 0), week_day(-14, 0)
    a["call23"], a["call24"] = on(6, week_day(-17, 2)), on(6, week_day(-4, 2))
    a["leave_from"], a["leave_to"] = W(-10), W(-9, 4)
    a["call22"] = on(7, week_day(-9, 1))
    mondays = [m for m in (s9_first + dt.timedelta(7 * i) for i in range(40)) if m <= T]
    cancelled = a["s9_cancelled"] = W(-10) if closed(cfg, W(-9)) else W(-9)
    moved = a["s9_moved"] = W(-5)
    holidays = a["s9_holidays"] = [m for m in mondays if closed(cfg, m)]
    a["s9_mondays"] = mondays
    a["s9_regular"] = [m for m in mondays if m not in holidays and m not in (cancelled, moved)]
    a["supplier_task"], a["supplier_due"] = week_day(-7, 0), week_day(-3, 0)
    a["call31"] = on(5, week_day(-6, 0))
    note1 = a["s4_note1"] = on(6, week_day(-6, 0))
    a["s4_note1_decided"] = pd(4, 1, note1)
    a["call12"] = on(7, week_day(-5, 1))
    a["senior_thread"] = week_day(-4, 0)
    if cfg == "ru":
        pair = pair_start(7, week_day(-4, 2))
        a["a6_chat_sent"], a["a6_chat_reply"] = pair - DAY, pair + DAY
    else:
        a["a6_chat_sent"], a["a6_chat_reply"] = week_day(-4, 1), week_day(-4, 1) + 2 * DAY
    a["s3_fix"] = week_day(-3, 0)
    note2 = a["s4_note2"] = on(6, week_day(-3, 0))
    a["s4_note2_decided"] = pd(4, 1, note2)
    a["s2_discounts"] = (on(23, week_day(-3, 2), -1), on(23, week_day(-1, 3), -1))
    day_a = a["s7_day_a"] = pd(6, -14 if cfg == "en" else -10)
    a["s7_chat"], a["s7_visit"] = day_a - DAY, pd(6, 1, day_a)
    a["s8_quote"] = pd(7, -5)
    car = a["s8_car_in"] = pd(7, -4)
    ready = car + DAY
    while not (works(5, ready) and (cfg == "ru" or ready.weekday() < 5)):
        ready += DAY
    a["s8_ready"] = ready
    disc = a["s8_discount"] = pd(4, 1, ready)
    a["s12_proposal"] = on(5, disc + DAY) if cfg == "ru" else wd(cfg, disc, 1)
    a["s10_report"] = week_day(-1, 0)
    # s6.waiting_at_t: a car's status is set on a day the shops are open, so a count that lands on a shut day moves back
    a["s6_since"] = {site: [snap(cfg, T - dt.timedelta(n), -1) for n in inputs.value("s6.waiting_at_t", cfg)[f"{site}_days"]] for site in ("west", "main", "east")}
    a["s6_waiting"] = a["s6_since"]["west"][0]
    a["call15"], a["call16"] = (pd(23, -3), pd(23, -1)) if cfg == "ru" else (wd(cfg, T, -4), wd(cfg, T, -1))
    a["s14_no_show"] = on(20, wd(cfg, T, -2), -1) if cfg == "ru" else wd(cfg, T, -2)
    a["s7_return"] = pd(6, -1)
    a["s4_nightly"] = pd(5, -1) + DAY
    a["s16_block"], a["s16_due"] = pd(6, 1), pd(6, 2)
    meet = pd(6, 3)
    # Rule A: the home shops publish on Thursday at 12:00; L is the week after the last publish on or before T.
    L = 1 if t >= dt.datetime.combine(W(0, 3), dt.time(12)) else 0
    a["pub_week"] = W(L)
    stock = a["stocktake"] = W(L, 1) if closed(cfg, W(L, 3)) else W(L, 3)  # ledger site.stocktake
    while not works(4, meet) or meet == stock or meet.weekday() > 4:
        meet = pd(6, 1, meet)
    a["s16_meeting"] = meet
    a["s14_open_shift"] = W(1, 1)
    off_from = a["week_off"] = W(L, 2) if closed(cfg, W(L, 3)) or closed(cfg, W(L, 4)) else W(L, 3)
    a["booking"] = pd(16, -1, off_from)
    a["roster_end"] = T + dt.timedelta(14)
    last_closed = T
    while not closed(cfg, last_closed):
        last_closed -= DAY
    a["last_closed"] = last_closed
    a["ru_rise"] = snap(cfg, months_back(T, 18))  # ledger price.hour.history: ru's second rate, the first open day on or after T-18 months
    a["week_day"], a["works"] = week_day, works
    # generator-spec.md "employee": one F4 row per season that overlaps the history; ledger season.hire: en ten weeks from the first
    # Monday of June, ru six weeks from the first Monday of April and of October
    start, (weeks, months) = a["history_start"], (10, (6,)) if cfg == "en" else (6, (4, 10))
    firsts = [D(y, m, 1) + dt.timedelta((7 - D(y, m, 1).weekday()) % 7) for y in range(start.year - 1, T.year + 1) for m in months]
    a["f4_seasons"] = [d for d in firsts if d + dt.timedelta(7 * weeks) > start and d <= T]
    # (to the Monday of W+2: A2's weekly slot runs to the second week after T, booked ahead)
    a["closed_mondays"] = [d for d in (start + dt.timedelta(i) for i in range((W(2) - start).days + 1)) if d.weekday() == 0 and closed(cfg, d)]

    def call_day(n, call, days):
        text = re.sub(r"\s*\([^()]*\)$", "", call["day"])
        if m := re.fullmatch(r"a working day of slot (\d+) in score period P\d", text):
            return on(int(m[1]), T + dt.timedelta(int(call["nominal_offset"][1:-1])))
        if m := re.search(r"the next full open day after slot (\d+)'s (\w+) working day before T on which slot (\d+) works", text):
            d = pd(int(m[1]), -ordinal(m[2])) + DAY
            while not (full_open(cfg, d) and works(int(m[3]), d)):
                d += DAY
            return d
        if m := re.search(r"slot (\d+)'s next working day after call (\d+)", text):
            return pd(int(m[1]), 1, days[int(m[2])])
        if m := re.search(r"(\d+) calendar days? after call (\d+)", text):
            return days[int(m[2])] + dt.timedelta(int(m[1]))
        if m := re.search(r"slot (\d+)'s first working day on or after the " + WDAY + r" of week T-(\d+)", text):
            return on(int(m[1]), week_day(-int(m[3]), WEEKDAYS.index(m[2])))
        if m := re.search(r"slot (\d+)'s (\w+) working day before T", text):
            return pd(int(m[1]), -ordinal(m[2]))
        if m := re.search(r"(?:main|east|west)'s (\w+) full open day before T", text):
            return wd(cfg, T, -ordinal(m[1]))
        if m := re.search(r"the " + WDAY + r" of week T-(\d+)", text):
            return week_day(-int(m[2]), WEEKDAYS.index(m[1]))
        raise ValueError(f"call {n} ({cfg}): no anchor for the day '{call['day']}'")

    def rule_day(rule):  # a conversation day's rule (conversations/DESIGN.md); "week" counts back from W0
        kind = rule["kind"]
        if kind == "T":
            d = T
        elif kind == "calendar":
            d = T + dt.timedelta(rule["days"])
        elif kind == "weekday_of_week":
            d = week_day(-rule["week"], [w[:3] for w in WEEKDAYS].index(rule["weekday"]))
            if rule.get("on_or_after_for_slot"):
                d = on(rule["on_or_after_for_slot"], d)
        elif kind == "slot_working_day":
            d = pd(rule["slot"], rule["n"])
        elif kind == "open_day":
            d = wd(cfg, T, rule["n"])
        else:
            raise ValueError(f"no anchor for the rule {rule}")
        return d + dt.timedelta(rule.get("plus_days", 0))

    def said_days(text, days):  # a conversation's floating day: the days it names by label or by the <weekday> of a week
        labels = [days[x] for x in re.findall(r"T(?:[+-]\d+d)?(?![\w-])", text) if x in days]
        if labels:
            return labels
        out = []
        for m in re.finditer(r"the " + WDAY + "(?: and " + WDAY + r")? of week (T-\d+|W\+\d+|W0)", text):
            k = 0 if m[3] == "W0" else int(m[3][1:]) if m[3][0] == "W" else -int(m[3][2:])
            out += [week_day(k, WEEKDAYS.index(w)) for w in (m[1], m[2]) if w]
        return out

    calls = {}
    for n, f in inputs.STORY_FILES["calls", cfg].items():
        d = call_day(n, f["call"], {k: v["day"] for k, v in calls.items()})
        floating = [[] if x["day"] == "any" else [d + dt.timedelta(int(x["day"][4:-1] or 0))] for x in f["floating_days"]]
        calls[n] = {"day": d, "floating": floating}
    a["calls"] = calls
    # conversation 08's other offered time: en the next full open day after the stocktake, ru slot 17's first working day after it
    moved_by_rule_a = {"stocktake": stock, "booking": a["booking"], "after_stocktake": wd(cfg, stock, 1) if cfg == "en" else pd(17, 1, stock)}
    conversations = {}
    for n, f in inputs.STORY_FILES["conversations", cfg].items():
        bound = WEEK_BOUND[cfg].get(n, {})
        days = {k: moved_by_rule_a[bound[k]] if k in bound else rule_day(v["rule"]) for k, v in f["days"].items()}
        conversations[n] = {"days": days, "floating": [said_days(x["day"], days) for x in f["floating_days"]]}
    a["conversations"] = conversations

    # stories/TIMELINE.md "What the seeder asserts" and rule A: a build fails when one of these fails
    ru, block, due, booking = cfg == "ru", a["s16_block"], a["s16_due"], a["booking"]
    q, d23a, d23b, s12 = a["s8_quote"], *a["s2_discounts"], a["s12_proposal"]
    checks = [
        ("found<fired", a["s2_found"] < fired), ("fired<P", a["rule_on"] < a["P"]), ("P<complaint", a["P"] < complaint),
        ("P<call 21", a["P"] < a["call21"]), ("call 12<call 9", a["call12"] < q), ("quote<car<ready<discount<T", q < car < ready < disc < T),
        ("slot 7 in post 90 days", (T - a["slot7_starts"]).days >= 90), ("block<due<meeting", block < due < meet),
        ("S7 first chat under 30 days before T",
         a["s7_chat"] < a["s7_visit"] < a["s7_return"] and t - dt.datetime.combine(a["s7_chat"], dt.time(21, 10)) < dt.timedelta(30)),
        ("stocktake in the published week L", a["pub_week"] <= stock <= a["pub_week"] + 6 * DAY), ("call 15<call 16<T", a["call15"] < a["call16"] < T),
        ("slot 23's discounts in the last 30 days, each before its week's Friday list",
         (T - d23a).days <= 30 and d23a < d23b < T and d23a.weekday() <= 4 and d23b.weekday() <= 4),
        ("A6's chat waits two days", (a["a6_chat_reply"] - a["a6_chat_sent"]).days == 2),
        ("S12 proposal after the discount, before T", disc < s12 < T or (disc < s12 and not ru)), ("nightly proposal on or before T's date", a["s4_nightly"] <= T),
        ("stocktake on or after T's date", stock >= T), ("week off on or after T's date", off_from >= T),
        ("conversation 08's chat <= booking < week off", conversations[8]["days"]["T-1d"] <= booking < off_from),
        ("booking within pub_week - 3 days to pub_week + 4 days", a["pub_week"] - 3 * DAY <= booking <= a["pub_week"] + 4 * DAY),
    ]
    shift = [("S1 call 21", 5, a["call21"]), ("S1 call 22", 7, a["call22"]), ("S1 A6 chat, first reply", 7, a["a6_chat_reply"]), ("S1 call 23", 6, a["call23"]),
             ("S1 call 24", 6, a["call24"]), ("S2 discount 1", 23, d23a), ("S2 discount 2", 23, d23b), ("S3 call 31", 5, a["call31"]), ("S3 call 32", 6, pd(6, -8)),
             ("S4 call 7", 6, pd(6, -2)), ("S4 proposal 1", 6, note1), ("S4 proposal 1 decided", 4, a["s4_note1_decided"]), ("S4 proposal 2", 6, note2),
             ("S4 proposal 2 decided", 4, a["s4_note2_decided"]), ("S4 proposal 3", 6, a["s7_return"]), ("S4 slot 5's note", 5, pd(5, -1)),
             ("S5 requests filed", 16, pd(16, -3)), ("S5 call 28", 17, pd(17, -12) if ru else week_day(-6, 0)), ("S6 call 15", 23, a["call15"]),
             ("S6 call 16", 23, a["call16"]), ("S7 day A", 6, day_a), ("S7 visit", 6, a["s7_visit"]), ("S7 return chat", 6, a["s7_return"]), ("S8 call 9", 7, q),
             ("S8 car in", 7, car), ("S8 call 10", 5, ready), ("S8 call 11", 4, disc), ("S8 slot 7's note", 7, on(7, disc)), ("S12 call 12", 7, a["call12"]),
             ("S12 proposal", 5, s12), ("S13 messenger chat", 16, pd(16, -1)), ("S14 no-show (he was rostered)", 20, a["s14_no_show"]), ("S16 block", 6, block),
             ("S16 due", 6, due), ("S16 meeting", 6, meet), ("S16 meeting", 4, meet)]
    if ru:
        shift += [("S6 chat, first reply", 23, T - 6 * DAY), ("S6 chat, second reply", 23, T - 5 * DAY), ("S6 chat, note to the manager", 24, T - 3 * DAY),
                  ("S6 chat, third reply", 23, T - 2 * DAY), ("S7 thanks answered", 7, a["s7_visit"] + DAY)]
    failed = [name for name, ok in checks if not ok] + [f"{e} on shift (slot {s}, {d})" for e, s, d in shift if not works(s, d)]
    if failed:
        raise ValueError(f"build at {when:%Y-%m-%d %H:%M} ({cfg}) fails: " + "; ".join(failed))
    return a
