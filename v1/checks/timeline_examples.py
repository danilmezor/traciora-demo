# Worked examples for stories/TIMELINE.md: places every anchor of rule R6 for a given run instant, and proves that
# every named person is rostered on the day a story puts them (the Russian two-on, two-off rota above all).
# run: python3 checks/timeline_examples.py   (checks/check_ledger.py imports place() for the nominal and the awkward T)
import datetime as dt
D, DAY = dt.date, dt.timedelta(1)
PHASE_B, PHASE_A, WEEKDAY_STAFF = (6, 29, 17, 24), (5, 7, 16, 23), (2, 3, 4, 8, 9, 22)   # ledger roster.advisor_pattern, roster.manager_pattern
RU_MECHANIC_DAYS_OFF = {20: (3, 4)}                                                         # ledger roster.mechanic_days_off: slot 20 is off Thursday and Friday
WHEN = (dt.datetime(2026, 11, 13, 10, 30), dt.datetime(2027, 1, 2, 10, 30))
def observed(d):
    return d - DAY if d.weekday() == 5 else d + DAY if d.weekday() == 6 else d
def en_closed(y):
    may31 = D(y, 5, 31); memorial = may31 - dt.timedelta((may31.weekday()) % 7)
    sep1 = D(y, 9, 1); labor = sep1 + dt.timedelta((7 - sep1.weekday()) % 7)
    nov1 = D(y, 11, 1); thanks = nov1 + dt.timedelta((3 - nov1.weekday()) % 7 + 21)
    return {observed(D(y, 1, 1)), memorial, observed(D(y, 7, 4)), labor, thanks, observed(D(y, 12, 25)), observed(D(y + 1, 1, 1))}
def closed(mk, d):
    return d in en_closed(d.year) if mk == "en" else (d.month, d.day) in ((1, 1), (1, 2))
def full_open(mk, d):  # a full open day for every shop: en weekdays, ru every day
    return not closed(mk, d) and (mk == "ru" or d.weekday() < 5)
def main_open(mk, d):
    return not closed(mk, d) and (mk == "ru" or d.weekday() < 6)
def snap(mk, d, step=1):
    while not full_open(mk, d): d += dt.timedelta(step)
    return d
def wd(mk, d, n):  # the n-th full open day after (n > 0) or before (n < 0) d
    step = 1 if n > 0 else -1
    for _ in range(abs(n)):
        d += dt.timedelta(step)
        while not full_open(mk, d): d += dt.timedelta(step)
    return d
def place(mk, when):
    """Returns (table rows, order assertions, [(event, slot, date, rostered)])."""
    day = when.date()
    hours = {"en": ((7, 30), (17, 30)), "ru": ((9, 0), (20, 0))}[mk]
    if mk == "en" and day.weekday() == 5: hours = ((8, 0), (13, 0))
    t = when
    if not main_open(mk, day) or (when.hour, when.minute) < hours[0]:
        day -= DAY
        while not main_open(mk, day): day -= DAY
        close = (13, 0) if mk == "en" and day.weekday() == 5 else {"en": (17, 30), "ru": (20, 0)}[mk]
        t = dt.datetime(day.year, day.month, day.day, *close)
    elif (when.hour, when.minute) > hours[1]:
        t = dt.datetime(day.year, day.month, day.day, *hours[1])
    T = t.date()
    w0 = T - dt.timedelta(T.weekday())
    W = lambda k, dow=0: w0 + dt.timedelta(7 * k + dow)
    def works(slot, d):
        if not full_open(mk, d) and not (mk == "en" and d == T): return False
        if mk == "en" or slot in WEEKDAY_STAFF: return d.weekday() < 5 or d == T
        if slot in RU_MECHANIC_DAYS_OFF: return d.weekday() not in RU_MECHANIC_DAYS_OFF[slot]
        phase_b = (d - T).days % 4 in (0, 1)
        return phase_b if slot in PHASE_B else not phase_b
    def pd(slot, n, d=None):  # slot's n-th working day after (n > 0) or before (n < 0) d
        d = d or T; step = 1 if n > 0 else -1
        for _ in range(abs(n)):
            d += dt.timedelta(step)
            while not works(slot, d): d += dt.timedelta(step)
        return d
    def on(slot, d, step=1):  # slot's first working day on or after d (step 1), or last on or before it (step -1)
        while not works(slot, d): d += dt.timedelta(step)
        return d
    def pair_start(slot, d):  # the first day of a working pair of slot on or after d
        while not (works(slot, d) and not works(slot, d - DAY)): d += DAY
        return d
    G = snap(mk, T - dt.timedelta(175))
    P = T - dt.timedelta(150); P += dt.timedelta((7 - P.weekday()) % 7); P = snap(mk, P)
    first_mon = G + dt.timedelta((7 - G.weekday()) % 7)
    mondays = [first_mon + dt.timedelta(7 * i) for i in range(40) if first_mon + dt.timedelta(7 * i) <= T]
    cancelled = W(-9)
    if closed(mk, cancelled): cancelled = W(-10)
    moved = W(-5)
    hol = [m for m in mondays if closed(mk, m)]
    regular = [m for m in mondays if m not in hol and m not in (cancelled, moved)]
    cyc = ["D", "A-", "A+", "A-", "D", "A-", "A+", "D", "A-", "D", "A+"]
    seq = [cyc[i % 11] for i in range(len(regular))]
    A = pd(6, -14 if mk == "en" else -10); visit = pd(6, 1, A)
    q = pd(7, -5); car = pd(7, -4); ready = car + DAY
    while not (works(5, ready) and (mk == "ru" or ready.weekday() < 5)): ready += DAY
    disc = pd(4, 1, ready)
    stock = W(1, 3)
    if closed(mk, stock): stock = W(1, 1)
    off_from = W(1, 3)
    if closed(mk, W(1, 3)) or closed(mk, W(1, 4)): off_from = W(1, 2)
    block, due = pd(6, 1), pd(6, 2)
    meet = pd(6, 3)
    while not works(4, meet) or meet == stock or meet.weekday() > 4: meet = pd(6, 1, meet)
    fired = wd(mk, G, 15)
    wait = T - dt.timedelta(9)
    while not full_open(mk, wait): wait -= DAY
    last_closed = T
    while not closed(mk, last_closed): last_closed -= DAY
    ru = mk == "ru"
    call21, call22 = on(5, snap(mk, W(-20, 1))), on(7, snap(mk, W(-9, 1)))
    call23, call24 = on(6, snap(mk, W(-17, 2))), on(6, snap(mk, W(-4, 2)))
    pair = pair_start(7, snap(mk, W(-4, 2))) if ru else None
    a6_sent, a6_reply = (pair - DAY, pair + DAY) if ru else (snap(mk, W(-4, 1)), snap(mk, W(-4, 1)) + 2 * DAY)
    d23a, d23b = on(23, snap(mk, W(-3, 2)), -1), on(23, snap(mk, W(-1, 3)), -1)
    call31, call12 = on(5, snap(mk, W(-6))), on(7, snap(mk, W(-5, 1)))
    prop1, prop2 = on(6, snap(mk, W(-6))), on(6, snap(mk, W(-3)))
    call15, call16 = (pd(23, -3), pd(23, -1)) if ru else (wd(mk, T, -4), wd(mk, T, -1))
    call28 = pd(17, -12) if ru else snap(mk, W(-6))
    noshow = on(20, wd(mk, T, -2), -1) if ru else wd(mk, T, -2)
    s12prop = on(5, disc + DAY) if ru else wd(mk, disc, 1)
    note7 = on(7, disc)
    nightly = pd(5, -1) + DAY
    rows = [
     ("T", t.strftime("%a %Y-%m-%d %H:%M")), ("W0", f"{w0} to {w0 + dt.timedelta(6)}"),
     ("ERP history starts (T-24 months, next full open day)", snap(mk, D(T.year - 2, T.month, min(T.day, 28)))),
     ("west bought (T-14 months)", snap(mk, D(T.year - 2 + (T.month + 9) // 12, (T.month + 9) % 12 + 1, min(T.day, 28)))),
     ("S2 begins: first full open day on or after T-335 d", snap(mk, T - dt.timedelta(335))),
     ("F3 resigns: Mon W-30", snap(mk, W(-30))),
     ("A5 comebacks: Tue W-26, Tue W-22", f"{snap(mk, W(-26, 1))}, {snap(mk, W(-22, 1))}"),
     ("G, go-live: T-175 d", G),
     ("S9 series starts: first Monday on or after G", first_mon),
     ("S2 found, owner's thread: 5th full open day after G", wd(mk, G, 5)), ("S2 follow-up thread: 5 more", wd(mk, G, 10)),
     ("F1 fired: west's 15th full open day after G", fired), ("discount rule page and team note: next day", wd(mk, fired, 1)),
     ("P, price rise; A6's new contact: first Monday on or after T-150 d", P),
     ("S1 call 21 (slot 5): Tue W-20; ru his first working day on or after", call21),
     ("A5 last visit: Thu W-20", snap(mk, W(-20, 3), -1)),
     ("A5 complaint call: Tue W-19", snap(mk, W(-19, 1))),
     ("A5 three misses: +1, +6, +9 days", ", ".join(str(snap(mk, snap(mk, W(-19, 1)) + dt.timedelta(k))) for k in (1, 6, 9))),
     ("F2 fired: Mon W-17", snap(mk, W(-17))), ("slot 14 starts: Mon W-15", snap(mk, W(-15))), ("slot 7 starts: Mon W-14", snap(mk, W(-14))),
     ("S1 calls 23 and 24 (slot 6): Wed W-17, Wed W-4; ru her first working day on or after", f"{call23}, {call24}"),
     ("diagnostician's leave: Mon W-10 to Fri W-9", f"{W(-10)} to {W(-9, 4)}"),
     ("S1 call 22 (slot 7): Tue W-9; ru his first working day on or after", call22),
     ("S9 cancelled by the organiser", cancelled), ("S9 holiday Mondays (cancelled)", ", ".join(map(str, hol)) or "none"),
     ("supplier task created: Mon W-7; due: Mon W-3", f"{snap(mk, W(-7))}; {snap(mk, W(-3))}"),
     ("S3 call 31 (slot 5): Mon W-6; ru his first working day on or after", call31),
     ("S4 approved note proposed: Mon W-6; ru her first working day on or after; decided slot 4's next working day", f"{prop1}; {pd(4, 1, prop1)}"),
     ("S9 moved to 10:00: Mon W-5", moved), ("slot 7's first wrong price, call 12: Tue W-5; ru his first working day on or after", call12),
     ("senior's thread and task: Mon W-4", snap(mk, W(-4))),
     ("S1 A6's web chat sent; first reply (slot 7)", f"{a6_sent}; {a6_reply}"),
     ("S3 fix: Mon W-3", snap(mk, W(-3))),
     ("S4 declined note proposed: Mon W-3; ru her first working day on or after; decided slot 4's next working day", f"{prop2}; {pd(4, 1, prop2)}"),
     ("S2 slot 23's two discounts: Wed W-3, Thu W-1; ru his last working day on or before", f"{d23a}, {d23b}"),
     ("S7 web chat 21:10: the evening before day A", A - DAY), ("S7 day A (card taken, booked, confirming call)", A), ("S7 visit: her next working day", visit),
     ("S8 quote call, slot 7's second wrong price: his 5th working day back", q), ("S8 car in: his 4th", car), ("S8 ready, bill, argument, complaint call", ready), ("S8 discount and call back", disc),
     ("S12 proposal: en next full open day; ru slot 5's first working day after", s12prop),
     ("S10 report fails; S16 card given: Mon W-1", snap(mk, W(-1))),
     ("S6 car enters waiting_parts: T-9 d, snapped back", wait),
     ("S6 call 15: en west's 4th full open day back; ru slot 23's 3rd working day back", call15),
     ("S6 missed call and call 16: en west's last full open day; ru slot 23's last working day", call16),
     ("S14 no-show: en east's 2nd full open day back; ru slot 20's last working day on or before it", noshow),
     ("S7 return chat (web); S4 waiting note: slot 6's last working day", pd(6, -1)),
     ("S4 nightly proposal: the pass after slot 5's last working day", nightly),
     ("S16 block / due 12:00 / meeting 10:00", f"{block} / {due} / {meet}"),
     ("S14 open shift: Tue W+1", W(1, 1)), ("S13 stocktake, closed from 12:00", stock),
     ("S5 week off", f"{off_from} to {off_from + dt.timedelta(6)}"), ("roster ends: T+14 d", T + dt.timedelta(14)),
     ("last closed date before T", last_closed),
     ("S9 counts", f"{len(mondays)} occurrences: {len(hol)} holiday, 1 cancelled, 1 moved, {len(regular)} regular; held {len(regular) + 1}; slot 22 declined {seq.count('D')}, accepted {seq.count('A-') + seq.count('A+') + 1}, came {seq.count('A+') + 1}"),
    ]
    order = [("found<fired", wd(mk, G, 5) < fired), ("fired<P", wd(mk, fired, 1) < P), ("P<complaint", P < snap(mk, W(-19, 1))), ("P<call 21", P < call21), ("call 12<call 9", call12 < q), ("quote<car<ready<discount<T", q < car < ready < disc < T),
             ("slot 7 in post 90 days", (T - snap(mk, W(-14))).days >= 90), ("block<due<meeting", block < due < meet),
             ("S7 first chat under 30 days before T", A - DAY < visit < pd(6, -1) and (t - dt.datetime.combine(A - DAY, dt.time(21, 10))).total_seconds() < 30 * 86400),
             ("stocktake in a published week", w0 + dt.timedelta(7) <= stock <= w0 + dt.timedelta(13)), ("call 15<call 16<T", call15 < call16 < T),
             ("slot 23's discounts in the last 30 days, each before its week's Friday list", (T - d23a).days <= 30 and d23a < d23b < T and d23a.weekday() <= 4 and d23b.weekday() <= 4),
             ("A6's chat waits two days", (a6_reply - a6_sent).days == 2), ("S12 proposal after the discount, before T", disc < s12prop < T or (disc < s12prop and not ru)), ("nightly proposal on or before T's date", nightly <= T)]
    shift = [("S1 call 21", 5, call21), ("S1 call 22", 7, call22), ("S1 A6 chat, first reply", 7, a6_reply), ("S1 call 23", 6, call23), ("S1 call 24", 6, call24),
             ("S2 discount 1", 23, d23a), ("S2 discount 2", 23, d23b), ("S3 call 31", 5, call31), ("S3 call 32", 6, pd(6, -8)),
             ("S4 call 7", 6, pd(6, -2)), ("S4 proposal 1", 6, prop1), ("S4 proposal 1 decided", 4, pd(4, 1, prop1)), ("S4 proposal 2", 6, prop2), ("S4 proposal 2 decided", 4, pd(4, 1, prop2)), ("S4 proposal 3", 6, pd(6, -1)), ("S4 slot 5's note", 5, pd(5, -1)),
             ("S5 requests filed", 16, pd(16, -3)), ("S5 call 28", 17, call28), ("S6 call 15", 23, call15), ("S6 call 16", 23, call16),
             ("S7 day A", 6, A), ("S7 visit", 6, visit), ("S7 return chat", 6, pd(6, -1)),
             ("S8 call 9", 7, q), ("S8 car in", 7, car), ("S8 call 10", 5, ready), ("S8 call 11", 4, disc), ("S8 slot 7's note", 7, note7), ("S12 call 12", 7, call12), ("S12 proposal", 5, s12prop),
             ("S13 messenger chat", 16, pd(16, -1)), ("S14 no-show (he was rostered)", 20, noshow), ("S16 block", 6, block), ("S16 due", 6, due), ("S16 meeting", 6, meet), ("S16 meeting", 4, meet)]
    if ru:
        shift += [("S6 chat, first reply", 23, T - 6 * DAY), ("S6 chat, second reply", 23, T - 5 * DAY), ("S6 chat, note to the manager", 24, T - 3 * DAY), ("S6 chat, third reply", 23, T - 2 * DAY), ("S7 thanks answered", 7, visit + DAY)]
    return rows, order, [(e, s, d, works(s, d)) for e, s, d in shift]
def run(mk, when):
    rows, order, shift = place(mk, when)
    print(f"\n### {mk}, run at {when:%a %Y-%m-%d %H:%M}\n\n| Anchor | Date |\n|---|---|")
    for a, b in rows: print(f"| {a} | {b} |")
    print("\nAsserted: " + "; ".join(f"{k} {'holds' if v else 'FAILS'}" for k, v in order))
    off = [f"{e} (slot {s}, {d})" for e, s, d, ok in shift if not ok]
    print(f"\nOn shift: {len(shift)} story events, each on a day its named person is rostered" + (" holds" if not off else " FAILS: " + "; ".join(off)))
if __name__ == "__main__":
    for when in WHEN:
        for mk in ("en", "ru"): run(mk, when)
