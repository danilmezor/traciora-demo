# Builds workday/{en,ru}/*.json and workday/roster.json from the sources in this folder.
#   python3 workday/_build/build.py
# The JSON files are what the seeder reads; edit the sources here and rebuild, then run checks/check_workday.py.
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import banks_en, banks_ru, diary as cal, cards as cd, console as con, shift_requests as rq  # noqa: E402

OUT = os.path.dirname(HERE)


def pick(value, lang):
    """A value written once per language is {'en': .., 'ru': ..}; anything else is shared."""
    if isinstance(value, dict):
        if set(value) <= {"en", "ru"} and value:
            return pick(value.get(lang), lang)
        return {k: pick(v, lang) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [pick(v, lang) for v in value]
    return value


def card(c, lang):
    c = pick(c, lang)
    trail = [{"at": c["at"], "by": c["by"], "verb": "created"}]
    if c.get("owner0") is not None:
        trail.append({"at": c["at"], "by": c["by"], "verb": "assigned", "to": c["owner0"]})
    for p in c.get("parts", []):
        trail.append({"at": p["added_at"], "by": p["added_by"], "verb": "participant_added", "who": p["slot"], "role": p["role"]})
    trail += c.get("trail", [])
    out = {k: c[k] for k in ("id", "story", "kind", "origin", "site", "priority") if k in c}
    out.update(origin_ref=c.get("origin_ref"), template=c.get("template"),
               title=c["title"], description=c.get("desc"), why_now=c.get("why"),
               created={"by": c["by"], "at": c["at"]}, owner=c["owner"], due=c.get("due"), state_at_t=c["state"],
               participants=[{"slot": p["slot"], "role": p["role"], "added_by": p["added_by"],
                              "part_done_at": p["part_done_at"]} for p in c.get("parts", [])],
               trail=trail)
    for k in ("quiet", "rests_on", "source", "needs", "note"):
        if k in c:
            out[k] = c[k]
    return out


def request(row, lang):
    rid, slot, kind, shift, proposed, days, at, status, by, wd, dat, reason, note = row
    out = {"id": rid, "slot": slot, "kind": kind, "shift": shift, "reason": reason, "status": status}
    if kind == "change_time":
        out["proposed"] = {"start": proposed[0], "end": proposed[1]}
    elif kind == "change_date":
        out["proposed"] = {"date": proposed}
    out["filed"] = {"at": at} if days is None else {"days_before_shift": days, "at": at}
    if status in ("approved", "declined"):
        out["decided"] = ({"by": by, "at": dat} if wd is None
                          else {"by": by, "working_days_after_filing": wd, "at": dat})
        out["decided"]["note"] = note
    elif status == "withdrawn":
        out["withdrawn"] = {"days_after_filing": wd, "at": dat}
    elif status == "expired":
        out["expired"] = {"at": "the daily pass on the day after the shift", "note": "The shift passed before anyone answered"}
    if lang == "en" and rid in rq.SATURDAY_TURNS_EN:
        out["saturday_turn"] = True
    return out


def alerts(lang):
    out = []
    for aid, rule, subject, severity, params, opened, status, closed, ack, markets in con.ALERTS:
        if markets not in ("both", lang):
            continue
        row = {"id": aid, "rule_id": rule, "subject": subject, "severity": severity, "category": "operations",
               "params": params, "summary": con.SUMMARY[lang][rule].format(**params),
               "opened": pick(opened, lang), "status_at_t": status, "closed": pick(closed, lang)}
        if ack:
            row["acknowledged"] = {"by": ack[0], "at": pick(ack[1], lang)}
        out.append(row)
    return out


ROSTER = {
    "_what": "the designed part of the shift planner: templates, cover rules, rota patterns, publishes and the state at T; "
             "shifts and punches are generated from these and from each person's ledger row (DESIGN.md section 1)",
    "templates": {
        "en": [
            {"site": "main", "name": "Desk early", "position": "Service Advisor", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "main", "name": "Desk late", "position": "Service Advisor", "start": "09:00", "end": "17:30", "break_min": 30},
            {"site": "main", "name": "Desk Saturday", "position": "Service Advisor", "start": "08:00", "end": "13:00", "break_min": 0},
            {"site": "main", "name": "Bay", "position": "Automotive Technician", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "main", "name": "Bay Saturday", "position": "Automotive Technician", "start": "08:00", "end": "13:00", "break_min": 0},
            {"site": "main", "name": "Foreman", "position": "Shop Foreman", "start": "07:15", "end": "16:00", "break_min": 30},
            {"site": "main", "name": "Parts", "position": "Parts Manager", "start": "07:30", "end": "16:30", "break_min": 30},
            {"site": "main", "name": "Office", "position": "Office Manager / Bookkeeper", "start": "08:00", "end": "16:30", "break_min": 30},
            {"site": "main", "name": "Service manager", "position": "Service Manager", "start": "07:30", "end": "17:00", "break_min": 30},
            {"site": "east", "name": "Desk early", "position": "Service Advisor", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "east", "name": "Desk late", "position": "Service Advisor", "start": "09:00", "end": "17:30", "break_min": 30},
            {"site": "east", "name": "Bay", "position": "Automotive Technician", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "east", "name": "Service manager", "position": "Service Manager", "start": "07:30", "end": "17:00", "break_min": 30},
            {"site": "west", "name": "Desk early", "position": "Service Advisor", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "west", "name": "Desk late", "position": "Service Advisor", "start": "09:00", "end": "17:30", "break_min": 30},
            {"site": "west", "name": "Bay", "position": "Automotive Technician", "start": "07:30", "end": "16:00", "break_min": 30},
            {"site": "west", "name": "Shop manager", "position": "Shop Manager", "start": "07:30", "end": "17:00", "break_min": 30},
        ],
        "ru": [
            {"site": "main", "name": "Приёмка", "position": "Мастер-приёмщик", "start": "09:00", "end": "20:00", "break_min": 60},
            {"site": "main", "name": "Приёмка с 11:30", "position": "Мастер-приёмщик", "start": "11:30", "end": "20:00", "break_min": 45,
             "active_until": "the day before the fix (the Monday of week T-3)"},
            {"site": "main", "name": "Цех", "position": "Автомеханик", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "main", "name": "Мастер цеха", "position": "Мастер цеха", "start": "08:45", "end": "18:00", "break_min": 60},
            {"site": "main", "name": "Склад", "position": "Менеджер по запчастям", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "main", "name": "Бухгалтерия", "position": "Бухгалтер", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "main", "name": "Руководитель сервиса", "position": "Руководитель сервиса", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "east", "name": "Приёмка", "position": "Мастер-приёмщик", "start": "09:00", "end": "20:00", "break_min": 60},
            {"site": "east", "name": "Цех", "position": "Автомеханик", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "east", "name": "Руководитель сервиса", "position": "Руководитель сервиса", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "west", "name": "Приёмка", "position": "Мастер-приёмщик", "start": "09:00", "end": "20:00", "break_min": 60},
            {"site": "west", "name": "Цех", "position": "Автомеханик", "start": "09:00", "end": "18:00", "break_min": 60},
            {"site": "west", "name": "Руководитель СТО", "position": "Руководитель СТО", "start": "09:00", "end": "18:00", "break_min": 60},
        ],
        "every_template": {"begin_check_in_before_min": 15, "allow_check_out_after_min": 60, "late_entry_grace_min": 5,
                           "early_exit_grace_min": 5},
    },
    "coverage": {
        "en": [
            {"site": "main", "position": "Service Advisor", "days": "Mon-Fri", "band": ["07:30", "17:30"], "min": 1, "valid_to": "W-3.mon>-1d"},
            {"site": "main", "position": "Service Advisor", "days": "Mon-Fri", "band": ["07:30", "10:00"], "min": 2, "valid_from": "W-3.mon"},
            {"site": "main", "position": "Service Advisor", "days": "Mon-Fri", "band": ["10:00", "17:30"], "min": 1, "valid_from": "W-3.mon"},
            {"site": "main", "position": "Service Advisor", "days": "Sat", "band": ["08:00", "13:00"], "min": 2},
            {"site": "main", "position": "Automotive Technician", "days": "Mon-Fri", "band": ["07:30", "16:00"], "min": 4},
            {"site": "main", "position": "Automotive Technician", "days": "Sat", "band": ["08:00", "13:00"], "min": 2},
            {"site": "east", "position": "Service Advisor", "days": "Mon-Fri", "band": ["07:30", "17:30"], "min": 1},
            {"site": "east", "position": "Automotive Technician", "days": "Mon-Fri", "band": ["07:30", "16:00"], "min": 3},
            {"site": "west", "position": "Service Advisor", "days": "Mon-Fri", "band": ["07:30", "17:30"], "min": 1},
            {"site": "west", "position": "Automotive Technician", "days": "Mon-Fri", "band": ["07:30", "16:00"], "min": 3},
        ],
        "ru": [
            {"site": "main", "position": "Мастер-приёмщик", "days": "every day", "band": ["09:00", "20:00"], "min": 1, "valid_to": "W-3.mon>-1d"},
            {"site": "main", "position": "Мастер-приёмщик", "days": "every day", "band": ["09:00", "11:30"], "min": 2, "valid_from": "W-3.mon"},
            {"site": "main", "position": "Мастер-приёмщик", "days": "every day", "band": ["11:30", "20:00"], "min": 1, "valid_from": "W-3.mon"},
            {"site": "main", "position": "Автомеханик", "days": "every day", "band": ["09:00", "18:00"], "min": 4},
            {"site": "east", "position": "Мастер-приёмщик", "days": "every day", "band": ["09:00", "20:00"], "min": 1},
            {"site": "east", "position": "Автомеханик", "days": "every day", "band": ["09:00", "18:00"], "min": 2},
            {"site": "west", "position": "Мастер-приёмщик", "days": "every day", "band": ["09:00", "20:00"], "min": 1},
            {"site": "west", "position": "Автомеханик", "days": "every day", "band": ["09:00", "18:00"], "min": 2},
        ],
        "source": "ledger kb.schedule.minimums, s3.fix; every rule is required",
    },
    "patterns": {
        "en": {
            "weekdays": ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                         "21", "22", "23", "24", "25", "26", "27", "F2"],
            "desk_shift_before_fix": {"main": {"early": ["5"], "late": ["6", "7"]}},
            "desk_shift_since_fix": {"main": {"early": ["5", "6"], "late": ["7"]}},
            "desk_shift": {"east": {"early": ["16"], "late": ["17"]}, "west": {"early": ["24"], "late": ["23"]}},
            "slot_21": "four weekdays at east, one at main; his main day changes week by week and, in the week of the "
                       "no-show, is the no-show's day",
            "slot_28": {"days": ["mon", "wed", "fri"], "and": "T's date", "hours": ["07:30", "13:30"]},
            "slot_29": "every Saturday morning at main, and cover days on weekdays (about one day in two weeks)",
            "saturday": {
                "advisor_turn": "week index k of W+k: k mod 3 = 0 slot 6, 2 slot 5, 1 slot 7 (before slot 7 started: 5 and 6 alternate)",
                "technicians": {"even weeks (W0, W-2, ...)": ["11", "13", "15"], "odd weeks": ["12", "14", "21"]},
            },
        },
        "ru": {
            "advisors": "ledger roster.advisor_pattern: two on, two off; phase B (6, 29, 17, 24) works day index d mod 4 in {0, 1}, "
                        "phase A (5, 7, 16, 23) in {2, 3}; d counts calendar days from T",
            "weekdays": ["3", "4", "8", "9", "22"],
            "days_off": {
                "10": ["sat", "sun"], "11": ["wed", "thu"], "12": ["mon", "tue"], "13": ["wed", "thu"], "14": ["mon", "tue"],
                "15": ["fri", "sat"], "18": ["sat", "sun"], "19": ["sat", "sun"], "20": ["thu", "fri"], "21": ["mon", "wed"],
                "25": ["sat", "sun"], "26": ["sun", "mon"], "27": ["wed", "thu"], "F2": ["sun", "mon"],
            },
            "slot_21": "Tuesday at main, Thursday to Sunday at east",
            "slot_28": {"days": ["fri", "sat", "sun"], "and": "T's date", "hours": ["09:00", "18:00"]},
            "on_duty_per_day": {"main": "four mechanics at least on every weekday", "east": "two at least", "west": "two at least"},
        },
        "rotations": "one workforce.shift_schedule row per person and rule: en BYDAY weekly rules; ru advisors two rules each, "
                     "FREQ=DAILY;INTERVAL=4 from the first and from the second day of the pair; ru mechanics BYDAY weekly rules",
    },
    "publishes": {
        "home": {"sites": ["main", "east"], "by": 4, "when": "the Thursday before the week, between 11:20 and 11:55 home time",
                 "at_t": {"published": ["W0", "W+1"], "draft": ["W+2 (to T+14 days)"]}},
        "west": {"sites": ["west"], "by": 22, "when": "the Sunday evening before the week, about 20:40 his time",
                 "at_t": {"published": ["W0"], "draft": ["W+1"], "not_started": ["W+2"]}},
        "extra": ["the fix: slot 4 republishes week W-3 at main on its Monday at o+0:25 (card S03)",
                  "the no-show day: a one-shift publish for slot 21 at east 55 minutes after opening",
                  "an approved request reaches its person with the next publish of that day"],
    },
    "at_t": {
        "late_now": {"slot": "28", "rule": "he has a shift at west on T's date that starts at the last quarter-hour at least 15 minutes "
                                           "before T (west's wall clock) and has no clock-in at T; if west is closed at T, or T is "
                                           "within two hours of west's close, nobody is late at T"},
        "open_shift": {"site": "main", "position": "technician", "day": "W+1.tue", "status": "published", "person": None},
        "week_off": {"slot": "16", "from": "S5", "published_shifts": ["S5>=p16", "S5>=p16>p16"], "requests": ["R50", "R51"]},
        "stocktake": {"day": "stock", "every_shift_ends_by": "12:00"},
    },
}


def main():
    for lang, bank in (("en", banks_en.BANK), ("ru", banks_ru.BANK)):
        d = os.path.join(OUT, lang)
        os.makedirs(d, exist_ok=True)
        files = {
            "cards.json": {
                "_what": "the hand-written cards with their whole trail; anchors and times as DESIGN.md section 7",
                "cards": [card(c, lang) for c in cd.CARDS],
                "bank_open_at_t": [dict(zip(("owner", "giver", "source", "priority", "state", "due_working_days", "last_line_days"), r))
                                   for r in cd.BANK_OPEN_AT_T],
            },
            "calendar.json": {
                "_what": "the hand-written series, entries and notes",
                "series": [pick(s, lang) for s in cal.SERIES],
                "standup_notes": [pick(n, lang) for n in cal.STANDUP_NOTES],
                "coaching_notes_slot_6": [pick(n, lang) for n in cal.COACHING_NOTES_SLOT_6],
                "entries": [pick(e, lang) for e in cal.ENTRIES] + ([pick(e, lang) for e in cal.ENTRIES_EN_ONLY] if lang == "en" else []),
            },
            "shift_requests.json": {
                "_what": "the 64 shift change requests since G (ledger s14.requests)",
                "requests": [request(r, lang) for r in (rq.EN if lang == "en" else rq.RU)],
            },
            "feedback.json": {
                "_what": "the nine feedback reports from staff",
                "reports": [{"id": i, "slot": s, "category": c, "severity": sv, "status": st, "sent": pick(at, lang),
                             "status_set": sat, "screen": scr, "summary": pick(text, lang)}
                            for i, s, c, sv, st, at, sat, scr, text in con.FEEDBACK],
                "notes": con.FEEDBACK_NOTES,
            },
            "alerts.json": {"_what": "the operations alerts since G", "alerts": alerts(lang), "notes": pick(con.ALERT_NOTES, lang)},
            "inbox.json": {"_what": "the two operators' Inbox at T, line by line", **pick(con.INBOX, lang)},
            "banks.json": bank,
        }
        for name, body in files.items():
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                json.dump(body, f, ensure_ascii=False, indent=1)
                f.write("\n")
    with open(os.path.join(OUT, "roster.json"), "w", encoding="utf-8") as f:
        json.dump(ROSTER, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("built", OUT)


if __name__ == "__main__":
    main()
