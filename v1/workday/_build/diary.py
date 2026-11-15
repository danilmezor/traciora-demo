# The hand-written calendar: series, single entries, and the notes written on story days.
from cards import L

SERIES = [
    dict(
        id="S09-managers-meeting", story="S09", kind="meeting", organiser=2, site=None, repeat="weekly",
        rrule="FREQ=WEEKLY;BYDAY=MO", starts="G>=mon", written_through="T>+14d",
        start=L("06:45", "08:15"), end=L("07:15", "08:45"), zone="home",
        title=L("Monday managers' meeting", "Планёрка руководителей"),
        agenda=L("Last week's numbers by shop, this week's roster, one open item each. Thirty minutes.",
                 "Цифры прошлой недели по площадкам, график на эту неделю, по одному открытому вопросу "
                 "с каждого. Полчаса."),
        invitees=[
            dict(slot=4, role="required", rule="accepts and comes to every occurrence that is held"),
            dict(slot=3, role="required", rule="accepts and comes to every occurrence that is held"),
            dict(slot=5, role="required", rule=L("accepts and comes", "by_rota: accepts and comes on his working Mondays, declines the others")),
            dict(slot=16, role="required", rule=L("accepts and comes, except her days off (declined)",
                                                   "by_rota: accepts and comes on her working Mondays, declines the others")),
            dict(slot=22, role="required",
                 rule="ledger s9.pattern: the cycle of eleven over the regular occurrences, in order; the moved week accepted and came; "
                      "both future occurrences unanswered",
                 answers_at="the Sunday evening before, 20:40 his time, when he publishes his roster"),
        ],
        exceptions=[
            dict(occurrence="S9cancel", action="cancel", by=2, at="S9cancel>-3d@o+2:00",
                 why="called off by the organiser (card S09)"),
            dict(occurrence="every Monday that is a closed date (en)", action="cancel", by=2,
                 why="holiday Mondays are cancelled occurrences, written when the series is made"),
            dict(occurrence="W-5.mon", action="replace", start="10:00", end="10:30", by=2, at="W-6.thu@o+3:00",
                 why="the one week it was moved (card S09)"),
        ],
        future=dict(answered=[4, 3, 5, 16], unanswered=[22]),
        notes="no occurrence carries a note, a comment or a reason about its hour (question S9.4 is 'nothing')",
    ),
    dict(
        id="COACH-6", story="S04", kind="meeting", organiser=4, site="main", invitees=[dict(slot=6, role="required")],
        repeat=L("weekly", None), rrule=L("FREQ=WEEKLY;BYDAY=WE", None), starts="W-23.wed",
        when=L("Wednesday 14:00-14:30", "single entries, not a series: one a week on her first working day of the "
                                        "week that is a weekday, 15:00-15:30"),
        title=L("Call review: Maya", "Разбор звонков: Алина"),
        notes_from="coaching_notes below on the last occurrence of each score period; the bank on the others",
    ),
    dict(
        id="COACH-7", story="S04", kind="meeting", organiser=4, site="main", invitees=[dict(slot=7, role="required")],
        repeat=L("weekly", None), rrule=L("FREQ=WEEKLY;BYDAY=WE", None), starts="W-13.wed",
        when=L("Wednesday 14:30-15:00", "single entries: his first working weekday of the week, 15:30-16:00"),
        title=L("Call review: Caleb", "Разбор звонков: Никита"), notes_from="the bank",
    ),
    dict(
        id="COACH-17", story="S04", kind="meeting", organiser=4, site="east", invitees=[dict(slot=17, role="required")],
        repeat=L("weekly", None), rrule=L("FREQ=WEEKLY;BYDAY=TH", None), starts="W-23.thu",
        when=L("Thursday 14:00-14:30 (slot 4 is at Bonny Oaks on Tuesdays and Thursdays)",
               "single entries: his working Tuesday or Thursday of the week, else his first working weekday, 15:00-15:30"),
        title=L("Call review: Josh", "Разбор звонков: Артём"), notes_from="the bank",
    ),
    dict(
        id="COACH-29", story="S04", kind="meeting", organiser=4, site="main", invitees=[dict(slot=29, role="required")],
        repeat=None, starts="W-23.mon",
        when=L("none: she is part-time; one single entry on the first Saturday of each score period, 12:30-13:00, "
               "on a Saturday slot 4 comes in for",
               "single entries: her first working weekday of the week, 16:00-16:30"),
        title=L("Call review: Brenda", "Разбор звонков: Татьяна Геннадьевна"), notes_from="the bank",
    ),
    dict(id="STANDUP-main", story=None, kind="meeting", organiser=8, site="main", invitees=[], repeat="weekdays",
         rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", starts="G>=open", start=L("07:20", "08:50"), end=L("07:30", "09:00"),
         title=L("Morning huddle: East Main", "Утренняя планёрка: Московское шоссе"),
         notes_from="the bank: three lines, one each from three themes; the story days below"),
    dict(id="STANDUP-east", story=None, kind="meeting", organiser=18, site="east", invitees=[], repeat="weekdays",
         rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", starts="G>=open", start=L("07:20", "08:50"), end=L("07:30", "09:00"),
         title=L("Morning huddle: Bonny Oaks", "Утренняя планёрка: Инженерный"), notes_from="as main"),
    dict(id="STANDUP-west", story=None, kind="meeting", organiser=22, site="west", invitees=[], repeat="weekdays",
         rrule="FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR", starts="G>=open", start=L("07:20", "08:50"), end=L("07:30", "09:00"),
         zone="west", title=L("Morning huddle: Charlotte Pike", "Утренняя планёрка: Техническая"),
         notes_from="as main; slot 22 writes a note on one day in three"),
]

# Notes on occurrences (the entry's description), written by the organiser after it.
STANDUP_NOTES = [
    dict(series="STANDUP-east", on=L("east-2", "east-2<=p20"), by=18, body=L(
        "- Austin is not in and has not called; Jordan is coming over from East Main\n"
        "- Two waiters before nine, both oil services\n"
        "- Rack is booked until two: no walk-in alignments",
        "— Блинова нет, не звонил; на подмену выходит Аюпов\n"
        "— До десяти два клиента ждут в зале, оба на замену масла\n"
        "— Стенд развала занят до двух: без записи не берём")),
    dict(series="STANDUP-main", on="W-3.mon", by=8, body=L(
        "- Early desk starts today: two at the counter from open, phones first\n"
        "- Kevin has the hybrid until noon; Terry takes the two charging checks\n"
        "- Parts land 9:15, 12:15, 3:15 as usual",
        "— С сегодняшнего дня оба мастера-приёмщика с 9:00: сначала телефон, потом стойка\n"
        "— Шубин до обеда на гибриде; зарядку и стартер берёт Нуруллин\n"
        "— Карпов и Сурков выходные: на подъёмниках сегодня четверо")),
    dict(series="STANDUP-main", on="W-10.mon", by=8, body=L(
        "- Kevin is out two weeks from today: diagnostics cut to what Terry can take\n"
        "- Overflow goes to Andre at Bonny Oaks; Travis books it there, not here\n"
        "- No hybrid work until he is back",
        "— Шубин с сегодняшнего дня две недели в отпуске: диагностику берём только ту, что потянет Нуруллин\n"
        "— Остальное — Егорову на Инженерный; записывает Григорьев, сразу туда\n"
        "— Гибриды до его возвращения не принимаем")),
    dict(series="STANDUP-west", on="west-1", by=22, body=L(
        "- Volvo's angle gear: supplier says tomorrow, again\n"
        "- Four cars waiting on parts; do the walk-ins first\n"
        "- Tyler starts late tomorrow, class in the morning",
        "— Насос ЭГУР на Peugeot: поставщик теперь говорит «на следующей неделе»\n"
        "— Четыре машины ждут запчасти; сначала берём тех, кто без записи\n"
        "— Булат завтра выходит позже, с утра у него пары")),
]

COACHING_NOTES_SLOT_6 = [  # on the last call review of each 30-day score period (P1..P6), by slot 4
    dict(period=1, body=L(
        "- Greeting and vehicle details: every call, keep it\n"
        "- You name the price and wait. Next week: two times first, price second\n"
        "- Average this period: {ledger:p06.score_path.1}",
        "— Приветствие и данные машины — в каждом звонке, так держать\n"
        "— Называет цену и ждёт. На следующую неделю: сначала два времени, потом цена\n"
        "— Средняя за период: {ledger:p06.score_path.1}")),
    dict(period=2, body=L(
        "- You now ask when they can come: good\n"
        "- Don't ask, offer: two times, your own words\n"
        "- Average: {ledger:p06.score_path.2}",
        "— Уже спрашивает, когда клиенту удобно приехать\n"
        "— Не спрашивать, а предлагать: «завтра в 9:00 или послезавтра в 14:00»\n"
        "— Средняя: {ledger:p06.score_path.2}")),
    dict(period=3, body=L(
        "- You take the booking when they name a time\n"
        "- Still no recap. Day, time, job, before you hang up\n"
        "- Average: {ledger:p06.score_path.3}",
        "— Запись берёт, когда клиент сам называет время\n"
        "— Итога пока нет. Перед тем как положить трубку: день, время, работа\n"
        "— Средняя: {ledger:p06.score_path.3}")),
    dict(period=4, body=L(
        "- Recap on most calls now; add the address for a new customer\n"
        "- On 'that's a lot' you sympathise. Answer it: what the price includes\n"
        "- Average: {ledger:p06.score_path.4}",
        "— Итог есть почти в каждом звонке; новым клиентам добавлять адрес\n"
        "— На «дорого» сочувствует. Нужно отвечать: что входит в цену\n"
        "— Средняя: {ledger:p06.score_path.4}")),
    dict(period=5, body=L(
        "- Two times before the price, and you take the booking: this is the standard\n"
        "- A doubt: say what happens if they wait, then offer the time again\n"
        "- Average: {ledger:p06.score_path.5}",
        "— Два времени до цены и запись — это уже стандарт\n"
        "— Сомнение клиента: сказать, что будет, если отложить, и ещё раз предложить время\n"
        "— Средняя: {ledger:p06.score_path.5}")),
    dict(period=6, body=L(
        "- Best period so far; the Nickajack driver call was right by the rubric\n"
        "- The driver's limit you found is proposed as a team note: good catch\n"
        "- Still the weak one: answering a doubt. One line of what the price includes, every time",
        "— Лучший период; звонок с водителем «Гонца» по чек-листу без замечаний\n"
        "— Правило про лимит водителя подала заметкой для команды — правильно\n"
        "— Слабое место то же: ответ на сомнение. Одна фраза «что входит в цену» — каждый раз")),
]

ENTRIES = [
    dict(id="S16-meeting", story="S16", kind="meeting", organiser=4, site="main", show_as="busy",
         start="S16meet@10:00", end="S16meet@11:00", booked="W-1.mon@o+1:20",
         title=L("Nickajack Delivery: quarterly review", "Квартальный обзор: «Симбирский гонец»"),
         agenda=L("Lonnie Coffey and Stuart Haney come to East Main. Maya presents the page; Claire raises the payment days.",
                  "Приезжают Кравцов и Бикмаев. Алина показывает страницу; о сроках оплаты говорит Екатерина Николаевна."),
         invitees=[dict(slot=6, response="accepted", at="W-1.mon>=p6@o+5:35"),
                   dict(slot=2, response="accepted", at="W-1.mon@o+2:06")]),
    dict(id="S16-block", story="S16", kind="block", organiser=6, site="main", show_as="busy", card="S16-review",
         start="p6+1@14:00", end="p6+1@15:30", booked="p6-1@o+6:00",
         title=L("Review prep: Nickajack Delivery", "Подготовка обзора: «Симбирский гонец»"), invitees=[]),
    dict(id="S05-leave-10", story="S05", kind="personal", organiser=10, site=None, show_as="out_of_office", all_day=True,
         start="W-10.mon", end="W-9.fri", booked="W-14.mon@o+0:10",
         title=L("On leave", "Отпуск"), invitees=[],
         with_it="availability 'unavailable' on each date and no shift (leave has no record of its own)"),
    dict(id="S05-week-off-16", story="S05", kind="personal", organiser=16, site=None, show_as="out_of_office", all_day=True,
         start="S5", end="S5>+6d", booked="p16-3@o+1:00",
         title=L("Away: family wedding", "Отпуск: свадьба дочери"), invitees=[],
         with_it="availability 'unavailable' on the seven dates; the two published shifts stand, each with an open request"),
    dict(id="S13-stocktake", story="S13", kind="meeting", organiser=9, site="main", show_as="busy",
         start="stock@12:00", end="stock@16:00", booked="W-1.thu@o+5:20",
         title=L("Stocktake: count from noon", "Инвентаризация: пересчёт с 12:00"),
         agenda=L("Shops close at 12:00. Teams of two, sheets back to Marcus before four.",
                  "Сервисы закрываются в 12:00. Считаем по двое, ведомости сдаём Мещерякову до четырёх."),
         invitees=[dict(slot=4, response="accepted", at="W-1.thu@o+5:40"),
                   dict(slot=8, response="accepted", at="W-1.fri@o+0:30"),
                   dict(slot=3, response="accepted", at="W-1.fri@o+2:10")]),
    dict(id="TRN-hybrid-10", story=None, kind="personal", organiser=10, site=None, show_as="out_of_office", all_day=True,
         start="W-21.wed", end="W-21.wed", booked="W-23.mon@o+0:15",
         title=L("Hybrid battery service class (off site)", "Курсы: высоковольтные системы гибридов (выездные)"),
         invitees=[], with_it="no shift that day; not an absence"),
    dict(id="TRN-lifts", story=None, kind="meeting", organiser=8, site="main", show_as="busy",
         start=L("W-13.thu@07:30", "W-13.fri@09:00"), end=L("W-13.thu@08:00", "W-13.fri@09:30"), booked="W-14.fri@o+2:00",
         title=L("Lift safety and jack-stand check: all technicians", "Повторный инструктаж: подъёмники и страховочные стойки"),
         invitees=[dict(slot=s, response="by_rota") for s in (10, 11, 12, 13, 14, 15)]),
    dict(id="SUP-home-supplier", story=None, kind="meeting", organiser=9, site="main", show_as="busy",
         start="W-12.wed@o+3:00", end="W-12.wed@o+3:45", booked="W-13.mon@o+2:00",
         title=L("Sequoyah Parts Supply: fall stocking order and returns", "«АвтоДеталь-Венец»: осенний заказ и возвраты"),
         invitees=[dict(slot=4, response="accepted", attended=True, at="W-13.mon@o+4:00")]),
    dict(id="SUP-tyres", story=None, kind="meeting", organiser=9, site="main", show_as="busy",
         start="W-8.tue@o+2:30", end="W-8.tue@o+3:15", booked="W-9.wed@o+1:00",
         title=L("Tellico Tire Distributors: winter fitments and the Nashville run", "«ШинТорг-Волга»: зимний ассортимент и хранение шин"),
         invitees=[dict(slot=4, response="accepted", attended=True, at="W-9.wed@o+3:00"),
                   dict(slot=8, response="accepted", attended=True, at="W-9.thu@o+0:20")]),
]

# en only: slot 16's six days off so far (card S05), each an all-day personal entry "Day off".
ENTRIES_EN_ONLY = [
    dict(id=f"S05-day-off-16-{i + 1}", story="S05", kind="personal", organiser=16, site=None, show_as="out_of_office",
         all_day=True, start=a, end=a, booked=b, title={"en": "Day off"}, invitees=[],
         with_it="availability 'unavailable' and no shift; the Friday of week T-7 was published first and came off by request R49")
    for i, (a, b) in enumerate([("W-17.fri", "W-19.mon@o+2:00"), ("W-16.mon", "W-19.mon@o+2:00"),
                                ("W-12.fri", "W-14.mon@o+2:00"), ("W-11.mon", "W-14.mon@o+2:00"),
                                ("W-7.fri", "W-8.mon@o+2:00"), ("W-6.mon", "W-8.mon@o+2:00")])
]

# The job interviews for the two replacements (slot 14 started the Monday of week T-15, slot 7 of week T-14).
for n, (day, who, role) in enumerate([("W-19.tue", 8, "tech"), ("W-19.thu", 8, "tech"), ("W-18.wed", 8, "tech"),
                                      ("W-18.thu", 5, "adv"), ("W-17.tue", 5, "adv"), ("W-17.thu", 5, "adv")]):
    k = n % 3 + 1
    ENTRIES.append(dict(
        id=f"INT-{role}-{k}", story=None, kind="meeting", organiser=4, site="main", show_as="busy",
        start=f"{day}@c-1:15", end=f"{day}@c-0:30", booked=f"{day}>-7d@o+2:00",
        title=(L(f"Interview: apprentice technician ({k} of 3)", f"Собеседование: ученик автомеханика ({k} из 3)") if role == "tech"
               else L(f"Interview: service advisor ({k} of 3)", f"Собеседование: мастер-приёмщик ({k} из 3)")),
        invitees=[dict(slot=who, response="by_rota")]))
