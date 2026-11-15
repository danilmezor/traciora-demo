# Story cards S13 to S16 (stories/S13.md .. S16.md).
from dsl import C, Q, T, day
from stories_a import A1_UNPAID

F = "stories/S%02d.md"

# ----------------------------------------------------------------------------------------------- S13
STOCKTAKE = C("stocktake_date", "the stocktake day",
              "the Thursday of week W+1; if that day is closed in the market, the Tuesday of that week",
              "core", ["core.location_hours_exception"], day("2026-11-19"))

Q("S13.1", file=F % 13, ref="S13.1", story="S13", asker=6, kind="smoke", small=True,
  src_q="Are we open on the afternoon of the stocktake day? (the date is typed; old: are we open on that afternoon)",
  q=T("Are we open on the afternoon of {stocktake_date}?", "Мы работаем {stocktake_date} после обеда?"),
  question_slots=[STOCKTAKE],
  scope=dict(population="Dated hours of the three shops.", period="The stocktake day.",
             definition="The date is typed in the question."),
  answer=T("No: every shop closes at 12:00 for the stocktake; the morning is open.",
           "Нет: все три сервиса в этот день закрываются в 12:00 на инвентаризацию; утром работаем."),
  facts=[T("No: every shop closes at 12:00 that day for the stocktake.",
           "Нет: в этот день все три сервиса закрываются в 12:00 на инвентаризацию."),
         T("The morning is open.", "Утром сервисы работают.")],
  keys=["site.stocktake"],
  proof=[("core", "core.location_hours_exception")], sources=["core"])

Q("S13.2", file=F % 13, ref="S13.2", story="S13", asker=4, kind="value", small=True,
  src_q="How many calls did we miss on the last holiday?",
  q=T("How many calls did we miss on the last holiday?",
      "Сколько звонков мы пропустили, когда последний раз были закрыты?"),
  scope=dict(population="Inbound calls at all shops.", period="The last closed date before T.",
             definition="Calls on a closed date are misses flagged out_of_hours and count in no desk's rate."),
  answer=T("[[=sum(L('calls.holiday_misses').values())|int]] on {last_closed_date}, all outside opening hours: East "
           "Main [[calls.holiday_misses.main|int]], Bonny Oaks [[calls.holiday_misses.east|int]], Charlotte Pike "
           "[[calls.holiday_misses.west|int]]. They are in no desk's miss rate.",
           "{s13_closed_day_misses}. Для большинства дат сборки ответ — «с запуска системы закрытых дней не было»; "
           "если же 1 или 2 января попадает в период работы системы, это звонки тех дней: все в нерабочее время, "
           "и ни в один показатель пропущенных они не входят."),
  computed=[C("last_closed_date", "en: the last closed date before T", "the latest location_hours_exception that "
              "closes every shop before T", "core", ["core.location_hours_exception"],
              {"en": ("2026-09-07", "| last closed date before T | 2026-09-07 |"), "ru": None}),
            C("s13_closed_day_misses", "ru: the misses on 1 and 2 January when those days lie inside the product "
              "period, by shop; otherwise the statement that no closed date lies between G and T",
              "missed_call rows with out_of_hours true on the last closed date between G and T",
              "core", ["missed_call", "call_leg", "core.location_hours_exception"])],
  only_slots={"en": ["last_closed_date"], "ru": ["s13_closed_day_misses"]},
  keys=["site.closed_dates", "calls.out_of_hours_share"],
  proof=[("core", "missed_call")], sources=["core"])

Q("S13.3", file=F % 13, ref="S13.3", story="S13", asker=6, kind="list", small=True,
  src_q="Which dates in the next 60 days are we closed or closing early, beyond the usual weekly hours? (old: which "
        "days are we closed in the next 60 days)",
  q=T("Which dates in the next 60 days are we closed or closing early, beyond the usual weekly hours?",
      "В какие дни в ближайшие 60 дней мы закрыты или закрываемся раньше обычного?"),
  scope=dict(population="Dated hours.", period="From T to T+60 d.",
             definition="Closed dates and early closes."),
  answer=T("The stocktake afternoon, {stocktake_date} from 12:00, and each closed date in the window "
           "({closed_next_60}).",
           "Вторая половина дня инвентаризации, {stocktake_date} с 12:00, и все закрытые дни в этом окне "
           "({closed_next_60})."),
  list_rule="Every location_hours_exception between T and T+60 d: the stocktake's early close and each closed date.",
  member_slot="closed_next_60",
  computed=[STOCKTAKE,
            C("closed_next_60", "the closed dates between T and T+60 d",
              "location_hours_exception rows that close every shop in the window, from site.closed_dates",
              "core", ["core.location_hours_exception"])],
  keys=["site.stocktake", "site.closed_dates", "s13.next_closed_date"],
  proof=[("core", "core.location_hours_exception")], sources=["core"])

# ----------------------------------------------------------------------------------------------- S14
P20_DAY = C("p20_no_show_day", "the day of slot 20's no-show",
            "en: east's 2nd full open day before T; ru: slot 20's last working day on or before it",
            "core", ["platform.event", "workforce.shift"],
            {"en": ("2026-11-11", "ru slot 20's last working day on or before it | 2026-11-11"),
             "ru": ("2026-11-11", "ru slot 20's last working day on or before it | 2026-11-11")})
Q("S14.1", file=F % 14, ref="S14.1", story="S14", asker=4, kind="list", small=True,
  src_q="Who is late most often?",
  q=T("Who is late most often?", "Кто у нас чаще всех опаздывает?"),
  scope=dict(population="People on the roster at T.", period="Shifts of the last 90 days.",
             definition="Late: clocked in more than 5 minutes after the start; ranked by share of shifts."),
  tolerance="3 points",
  answer=T("Cody Gann, three shifts in ten ([[p15.late|pct]]); then Dustin Swafford ([[p11.late|pct]]).",
           "Евгений Чугунов — три смены из десяти ([[p15.late|pct]]); за ним Максим Рябов ([[p11.late|pct]])."),
  list_rule="People on the roster at T ranked by the share of their shifts of the last 90 days with a clock-in more "
            "than 5 minutes after the start; the first two.",
  members=[T("Cody Gann: [[p15.late|pct]]", "Евгений Чугунов: [[p15.late|pct]]"),
           T("Dustin Swafford: [[p11.late|pct]]", "Максим Рябов: [[p11.late|pct]]")],
  keys=["late.grace_min", "late.company"],
  proof=[("core", "workforce.punch")], sources=["core"])

Q("S14.2", file=F % 14, ref="S14.2", story="S14", asker=4, kind="list", small=True,
  src_q="Who forgot to clock out in the last 30 days? (old: this month)",
  q=T("Who forgot to clock out in the last 30 days?", "Кто за последние 30 дней забывал отметить уход?"),
  scope=dict(population="Shifts at every site.", period="The last 30 days.",
             definition="No clock-out by the end of the day."),
  answer=T("The full list per build ({forgot_clock_out_30d}): Hunter Varnell with "
           "[[s14.instances.p14_forgot_last_30_days|int]] days and their dates, and the others with theirs.",
           "Полный список на дату сборки ({forgot_clock_out_30d}): Иван Сурков — "
           "[[s14.instances.p14_forgot_last_30_days|int]] дня, с датами, и остальные со своими."),
  list_rule="People with a shift in the last 30 days that had no clock-out by the end of the day, each with the "
            "dates. Must contain slot 14 with four days.",
  member_slot="forgot_clock_out_30d",
  members=[T("Hunter Varnell: [[s14.instances.p14_forgot_last_30_days|int]] days, with their dates",
             "Иван Сурков: [[s14.instances.p14_forgot_last_30_days|int]] дня, с датами")],
  computed=[C("forgot_clock_out_30d", "everyone who forgot to clock out in the last 30 days, with the dates",
              "shifts of the last 30 days whose out punch is missing at the end of the day (the later out row has "
              "producer web_correction)", "core", ["workforce.punch", "workforce.shift"])],
  proof=[("core", "workforce.punch: a shift with a clock-in and no clock-out row by the end of the day; the later "
                   "correction punch (producer web_correction)")], sources=["core"])

Q("S14.3", file=F % 14, ref="S14.3", story="S14", asker=4, kind="list", small=True,
  src_q="Which shifts between now and the end of next week have nobody? (old: which shifts next week have nobody)",
  q=T("Which shifts between now and the end of next week have nobody?",
      "На какие смены до конца следующей недели никто не поставлен?"),
  scope=dict(population="Published shifts with no person.", period="From T to the end of W+1.",
             definition="A shift with an open request is not empty."),
  answer=T("One: the mechanic's shift at East Main on {open_shift_day}. Angie Holloway's "
           "[[s5.week_off.published_shifts_inside|int]] shifts are not empty: her requests are open, not approved.",
           "Одна: смена механика на Московском шоссе {open_shift_day}. "
           "[[s5.week_off.published_shifts_inside|int]] смены Светланы Юрьевны Демидовой свободными не считаются: "
           "её заявки открыты, но не согласованы."),
  list_rule="Published shifts from T to the end of W+1 whose person is empty.",
  members=[T("The mechanic's shift at East Main on {open_shift_day}",
             "Смена механика на Московском шоссе {open_shift_day}")],
  must_not=[T("Listing Angie Holloway's two shifts as empty.",
              "Называть свободными две смены Светланы Юрьевны Демидовой.")],
  computed=[C("open_shift_day", "the day of the open shift", "the shift at main with person_id null; anchor: the "
              "Tuesday of week W+1", "core", ["workforce.shift"], day("2026-11-17"))],
  keys=["s14.instances"],
  proof=[("core", "workforce.shift")], sources=["core"])

Q("S14.4", file=F % 14, ref="S14.4", story="S14", asker=4, kind="value", small=True,
  src_q="How many requests did Dustin file in the last 90 days, and what happened to them? (old: this quarter)",
  q=T("How many requests did Dustin file in the last 90 days, and what happened to them?",
      "Сколько заявок по сменам подал Рябов за последние 90 дней и что по ним решили?"),
  scope=dict(population="Slot 11's change requests.", period="Filed in the last 90 days.",
             definition="Count by outcome."),
  answer=T("[[s14.requests.p11_last_90_days.filed|int]]: [[s14.requests.p11_last_90_days.approved|int]] approved, "
           "[[s14.requests.p11_last_90_days.declined|int]] declined.",
           "[[s14.requests.p11_last_90_days.filed|int]]: [[s14.requests.p11_last_90_days.approved|int]] согласованы, "
           "[[s14.requests.p11_last_90_days.declined|int]] отклонены."),
  proof=[("core", "workforce.shift_change_request")], sources=["core"])

Q("S14.5", file=F % 14, ref="S14.5", story="S14", asker=4, kind="cannot tell", small=True,
  src_q="Why was Wes Tate let go?",
  q=T("Why was Wes Tate let go?", "За что уволили Жаркова?"),
  scope=dict(population="F2.", period="G to his last day.", definition="No store records a reason."),
  answer=T("The data cannot give the reason: no store records one. It shows lateness on [[pF2.late|pct]] of his "
           "shifts, [[pF2.no_shows|int]] no-shows in his last 40 working days, comebacks on [[pF2.comebacks|pct]] of "
           "his orders, and the day his sign-in ended, {f2_fired_day}.",
           "Причину по данным не назвать: она нигде не записана. Видно другое: опоздания в [[pF2.late|pct]] смен, "
           "[[pF2.no_shows|int]] неявок за последние 40 рабочих дней, возвраты по [[pF2.comebacks|pct]] его нарядов "
           "и день, когда ему закрыли вход в систему, — {f2_fired_day}."),
  cannot=dict(lacks=T("The reason: no store records one.", "Причина: она нигде не записана."),
              may_give=[T("Late on [[pF2.late|pct]] of his shifts.", "Опоздания в [[pF2.late|pct]] смен."),
                        T("[[pF2.no_shows|int]] no-shows in his last 40 working days.",
                          "[[pF2.no_shows|int]] неявок за последние 40 рабочих дней."),
                        T("Comebacks on [[pF2.comebacks|pct]] of his orders.",
                          "Возвраты по [[pF2.comebacks|pct]] его нарядов."),
                        T("The day his sign-in ended: {f2_fired_day}.",
                          "День, когда ему закрыли вход в систему: {f2_fired_day}.")],
              wrong_if=T("An answer that states a reason as fact is wrong.",
                         "Ответ, который называет причину как установленный факт, неверен.")),
  computed=[C("f2_fired_day", "the day F2's sign-in ended", "the Monday of week T-17",
              "core", ["identity.person"], day("2026-07-13"))],
  proof=[("core", "workforce.punch, platform.event"), ("erp", "comeback orders")], sources=["core", "erp"])

Q("S14.6", file=F % 14, ref="S14.6", story="S14", asker=4, kind="nothing", small=True,
  src_q="Did anyone at Bonny Oaks clock in from outside the site?",
  q=T("Did anyone at Bonny Oaks clock in from outside the site?",
      "На Инженерном кто-нибудь отмечал приход не с территории сервиса?"),
  scope=dict(population="Clock-ins at east.", period="Since G.", definition="A clock-in with a location exception."),
  answer=T("Nobody.", "Никто."),
  nothing=T("No clock-in at Bonny Oaks carries a location exception.",
            "На Инженерном нет ни одной отметки прихода, сделанной за пределами площадки."),
  keys=["geo.checkin_radius_m", "s14.instances"],
  proof=[("core", "workforce.punch")], sources=["core"])

Q("S14.7", file=F % 14, ref="S14.7", story="S14", asker=15, kind="refusal", small=True,
  src_q="Who is late most often?",
  q=T("Who is late most often?", "Кто у нас больше всех опаздывает?"),
  scope=dict(population="A worker has no data tools.", period="Any.", definition="Tool floors by rank."),
  answer=T("Refused by rank; he can be shown his own week.",
           "Отказ по уровню доступа; ему можно показать его собственную неделю."),
  refusal=dict(by="rank",
               reason=T("A worker has no data tools.", "У уровня «Работник» нет инструментов для работы с данными."),
               may_offer=T("His own week.", "Его собственная неделя.")),
  proof=[("core", "tool floors")], sources=["core"])

Q("S14.8", file=F % 14, ref="S14.8", story="S14", asker=4, kind="value", small=True,
  src_q="What happened to Austin Crabtree's shift two working days ago? (the date is typed)",
  q=T("What happened to Austin Crabtree's shift on {p20_no_show_day}?",
      "Что было со сменой Блинова {p20_no_show_day}?"),
  scope=dict(population="Slot 20's shift.",
             period=T("east's 2nd full open day before T; the date is typed in the question.",
                      "Slot 20's last working day on or before east's 2nd full open day before T; the date is typed "
                      "in the question."),
             definition="The shift, its punches and the no-show event."),
  answer=T("He did not come on {p20_no_show_day}; the shift was flagged as a no-show; Jordan Akins took it.",
           "{p20_no_show_day} он не вышел; смена отмечена как неявка; её отработал Марат Аюпов."),
  computed=[P20_DAY], question_slots=[P20_DAY],
  keys=["s14.instances"],
  proof=[("core", "platform.event, workforce.shift")], sources=["core"])

# ----------------------------------------------------------------------------------------------- S15
Q("S15.1", file=F % 15, ref="S15.1", story="S15", asker=2, kind="value", small=True,
  src_q="How many customers do we have?",
  q=T("How many customers do we have?", "Сколько у нас клиентов?"),
  scope=dict(population="customer rows.", period="At T.",
             definition="Two rows with the same phone are one customer; the walk-in record is not a customer. "
                        "Trap: the pairs; the walk-in record."),
  answer=T("{customer_count}, after merging the [[s15.mess.duplicate_pairs|int]] pairs that share a phone. The "
           "walk-in record at Charlotte Pike is named and left out.",
           "{customer_count} — после объединения [[s15.mess.duplicate_pairs|int]] пар карточек с одинаковым "
           "телефоном. Карточка «Розничный покупатель» на Технической названа и в подсчёт не входит."),
  must_not=[T("Counting customer rows as they are.", "Считать карточки клиентов как есть.")],
  computed=[C("customer_count", "the number of customers",
              "count of customer rows at T, minus one for each of the twelve pairs with the same phone, minus the "
              "walk-in record", "erp", ["customer"])],
  proof=[("erp", "customer")], sources=["erp"])

Q("S15.2", file=F % 15, ref="S15.2", story="S15", asker=2, kind="value", small=True,
  src_q="What was last month's revenue?",
  q=T("What was last month's revenue?", "Какая у нас выручка за прошлый месяц?"),
  scope=dict(population="Orders invoiced or paid in the month.", period="The calendar month before T's month.",
             definition=T("Totals before tax; no void, no warranty or goodwill order, no order still open. Trap: "
                          "voids keep totals; goodwill; open orders.",
                          "Totals before tax: the total less the VAT inside it; no void, no warranty or goodwill "
                          "order, no order still open. Trap: voids keep totals; goodwill; open orders.")),
  answer=T("{revenue_last_month}, before tax, and what it leaves out: voided orders, warranty and goodwill orders, "
           "and orders still open.",
           "{revenue_last_month} без НДС; в неё не вошли аннулированные наряды, гарантийные наряды и работы за "
           "счёт сервиса, а также ещё не закрытые наряды."),
  computed=[C("revenue_last_month", "the revenue of the calendar month before T's month",
              "sum of totals before tax (ru: total minus tax_total) of orders invoiced or paid in that month, leaving "
              "out voided, warranty, goodwill and open orders", "erp", ["repair_order"])],
  keys=["tax.vat_divisor"],
  proof=[("erp", "repair_order")], sources=["erp"])

Q("S15.3", file=F % 15, ref="S15.3", story="S15", asker=2, kind="value", small=True,
  src_q="What is the average order at each shop?",
  q=T("What is the average order at each shop?", "Какой средний наряд по каждому сервису?"),
  scope=dict(population="Orders closed, per shop.", period="The last 12 months.",
             definition="Totals before tax; warranty and goodwill orders and the never-closed orders are out. Trap: the never-closed orders."),
  tolerance="2 %",
  answer=T("East Main [[volume.average_order.main|money2]], Bonny Oaks [[volume.average_order.east|money2]], "
           "Charlotte Pike [[volume.average_order.west|money2]], before tax, on orders closed in the last 12 months.",
           "Московское шоссе — [[volume.average_order.main|money]], Инженерный — "
           "[[volume.average_order.east|money]], Техническая — [[volume.average_order.west|money]], без НДС: по "
           "нарядам, закрытым за последние 12 месяцев."),
  keys=["volume.average_order", "tax.vat_divisor"],
  proof=[("erp", "repair_order")], sources=["erp"])

Q("S15.4", file=F % 15, ref="S15.4", story="S15", asker=2, kind="value", small=True,
  src_q="How many calls and orders did `west` have before 9:00 home time last week?",
  q=T("How many calls and orders did Charlotte Pike have before 9:00 Chattanooga time last week?",
      "Сколько звонков и нарядов было на Технической до 9:00 по ульяновскому времени на прошлой неделе?"),
  scope=dict(population="west's inbound calls and opened orders.", period="Week W-1.",
             definition="Before 09:00 in the home zone, which is 08:00 on west's own clock. Trap: the shop's own "
                        "clock."),
  answer=T("{west_calls_before_9} calls and {west_orders_before_9} orders, counted after shifting the hour: the "
           "shop system keeps Charlotte Pike's own clock, [[geo.zone_gap_hours|int]] hour behind Chattanooga.",
           "Звонков — {west_calls_before_9}, нарядов — {west_orders_before_9}; считать нужно со сдвигом на час: "
           "учётная программа хранит время по часам самой Технической, а они на [[geo.zone_gap_hours|int]] час "
           "отстают от ульяновских."),
  computed=[C("west_calls_before_9", "west's inbound calls before 09:00 home time in week W-1",
              "interactions with started_at (an instant) before 09:00 in the home zone", "core",
              ["interactions.interaction", "call_leg"]),
            C("west_orders_before_9", "west's orders opened before 09:00 home time in week W-1",
              "repair_order.opened_at is west's local time with no zone: before 08:00 local, with location.time_zone",
              "erp", ["repair_order", "location"])],
  proof=[("core", "calls (instants)"), ("erp", "repair_order (local time) and location")], sources=["core", "erp"])

Q("S15.5", file=F % 15, ref="S15.5", story="S15", asker=4, kind="list", small=True,
  src_q="Which orders have a mileage that cannot be right?",
  q=T("Which orders have a mileage that cannot be right?", "В каких нарядах пробег явно неверный?"),
  scope=dict(population="Orders whose mileage in is below the same car's earlier visit, or ten times its "
                        "neighbours.", period="The last 24 months.", definition="Trap: none."),
  answer=T("The [[s15.mess.wrong_mileage_orders|int]] named orders ({wrong_mileage_orders}).",
           "[[s15.mess.wrong_mileage_orders|int]] нарядов ({wrong_mileage_orders})."),
  list_rule="Orders of the last 24 months whose mileage in is below the same car's earlier visit, or ten times its "
            "neighbours.",
  member_slot="wrong_mileage_orders",
  computed=[C("wrong_mileage_orders", "the six planted orders with their cars and mileages",
              "repair_order joined to the same vehicle's other orders", "erp", ["repair_order", "vehicle"])],
  keys=["time.history_months"],
  proof=[("erp", "repair_order, vehicle")], sources=["erp"])

Q("S15.6", file=F % 15, ref="S15.6", story="S15", asker=2, kind="list", small=True,
  src_q="Which orders have been open for more than 60 days?",
  q=T("Which orders have been open for more than 60 days?", "Какие наряды открыты больше 60 дней?"),
  scope=dict(population="Open orders at T: status not invoiced, paid, void or declined. An invoiced order waiting on "
                        "an unpaid statement (A1's) or on a dispute (A5's) is not open.",
             period="At T, opened over 60 days ago.", definition="Trap: none."),
  answer=T("[[=1+L('s15.mess.never_closed.others_over_60_days')|int]]: the one at Charlotte Pike opened on "
           "{s15_west_order_day}, and the [[s15.mess.never_closed.others_over_60_days|int]] others, opened on "
           "{s15_main_order_day} at East Main and on {s15_east_order_day} at Bonny Oaks.",
           "[[=1+L('s15.mess.never_closed.others_over_60_days')|int]] наряда: на Технической — открыт "
           "{s15_west_order_day}, и ещё [[s15.mess.never_closed.others_over_60_days|int]]: на Московском шоссе — "
           "{s15_main_order_day}, на Инженерном — {s15_east_order_day}."),
  list_rule="Orders whose status at T is not invoiced, paid, void or declined, opened over 60 days ago, with their "
            "dates.",
  members=[T("Charlotte Pike: the order opened on {s15_west_order_day}", "Техническая: наряд от {s15_west_order_day}"),
           T("East Main: the order opened on {s15_main_order_day}", "Московское шоссе: наряд от {s15_main_order_day}"),
           T("Bonny Oaks: the order opened on {s15_east_order_day}", "Инженерный: наряд от {s15_east_order_day}")],
  computed=[C("s15_west_order_day", "the day the west order was opened", "the Wednesday of week T-22",
              "erp", ["repair_order"]),
            C("s15_main_order_day", "the day the main order was opened", "the Tuesday of week T-12",
              "erp", ["repair_order"]),
            C("s15_east_order_day", "the day the east order was opened", "the Tuesday of week T-10",
              "erp", ["repair_order"])],
  keys=["s15.dates"],
  proof=[("erp", "repair_order.status")], sources=["erp"])

# ----------------------------------------------------------------------------------------------- S16
DUE = C("s16_due_day", "the day the review card falls due", "slot 6's second working day after T",
        "core", ["work.work_item"], {"en": ("2026-11-17", "2026-11-16 / 2026-11-17 / 2026-11-18"),
                                     "ru": ("2026-11-17", "2026-11-14 / 2026-11-17 / 2026-11-18")})

Q("S16.1", file=F % 16, ref="S16.1", story="S16", asker=6, kind="value", small=True,
  src_q="What is still missing for the review?",
  q=T("What is still missing for the review?", "Чего ещё не хватает для обзора?"),
  scope=dict(population="The card's parts.", period="At T.", definition="Each helper's own part and its state."),
  answer=T("Donna Ledford's part, how late Nickajack Delivery now pays, is still open; Marcus Gaines's part is "
           "done. The card is due at 12:00 on {s16_due_day}.",
           "Не готова часть Ирины Владимировны Кудашкиной — насколько позже стал платить «Симбирский гонец»; часть "
           "Павла Мещерякова готова. Срок задачи — {s16_due_day}, 12:00."),
  computed=[DUE], keys=["s16.card"],
  proof=[("core", "work.work_participant")], sources=["core"])

Q("S16.2", file=F % 16, ref="S16.2", story="S16", asker=2, kind="smoke", small=True,
  context="\"It\" is the card \"Prepare Nickajack Delivery's quarterly review\" (ru: «Подготовить квартальный "
          "обзор по «Симбирскому гонцу»»), on which the asker is the watcher.",
  src_q="Who is working on it?",
  q=T("Who is working on it?", "Кто этим занимается?"),
  scope=dict(population="The card's people.", period="At T.", definition="Owner, helpers, watcher, giver."),
  answer=T("Owner Maya Torres; helpers Donna Ledford and Marcus Gaines; watcher Claire Brennan; given by Greg "
           "Whitaker.",
           "Исполнитель — Алина Хасанова; участники — Ирина Владимировна Кудашкина и Павел Мещеряков; наблюдатель — "
           "Екатерина Николаевна Ермолаева; задачу поставил Сергей Анатольевич Мельников."),
  facts=[T("Owner: Maya Torres.", "Исполнитель — Алина Хасанова."),
         T("Helpers: Donna Ledford and Marcus Gaines.",
           "Участники — Ирина Владимировна Кудашкина и Павел Мещеряков."),
         T("Watcher: Claire Brennan, who added herself.",
           "Наблюдатель — Екатерина Николаевна Ермолаева, она добавила себя сама."),
         T("Given by Greg Whitaker.", "Задачу поставил Сергей Анатольевич Мельников.")],
  keys=["s16.card"],
  proof=[("core", "work.work_item, work.work_participant")], sources=["core"])

Q("S16.3", file=F % 16, ref="S16.3", story="S16", asker=6, kind="explanation", small=True,
  src_q="What should the review say about Nickajack Delivery? (old: what should the review say about A1)",
  q=T("What should the review say about Nickajack Delivery?", "Что написать в обзоре про «Симбирский гонец»?"),
  scope=dict(population="A1.", period="The last 180 days (her window).",
             definition="Orders by 30-day block, spend by block, days from a bill to its payment."),
  tolerance="5 % on money, 3 days",
  answer=T("Visits steady at [[acct.A1.visits[5]|int]] a block; spend about "
           "[[=L('acct.A1.visits')[5]*L('acct.A1.average_order')|money]] a block before sales tax; days to pay up from "
           "about "
           "[[acct.A1.days_to_pay.until|int]] to [[acct.A1.days_to_pay.last_three_paid[2]|int]], with the unpaid "
           "bills at T.",
           "Заезды ровные, [[acct.A1.visits[5]|int]] за 30 дней; оборот — около "
           "[[=round(L('acct.A1.visits')[5]*L('acct.A1.average_order')*L('tax.vat_divisor'))|money]] за 30 дней в "
           "суммах к оплате, с НДС ([[=round(L('acct.A1.visits')[5]*L('acct.A1.average_order'))|money]] без НДС); срок "
           "оплаты вырос примерно с "
           "[[acct.A1.days_to_pay.until|int]] до [[acct.A1.days_to_pay.late|int]] дней, плюс счета, не оплаченные на "
           "сегодня."),
  facts=[T("Visits are steady at [[acct.A1.visits[5]|int]] a 30-day block.",
           "Заезды ровные: [[acct.A1.visits[5]|int]] за каждые 30 дней."),
         T("Spend is about [[=L('acct.A1.visits')[5]*L('acct.A1.average_order')|money]] a block, before sales tax.",
           "Оборот — около [[=round(L('acct.A1.visits')[5]*L('acct.A1.average_order')*L('tax.vat_divisor'))|money]] "
           "за 30 дней в суммах к оплате, с НДС; без НДС — "
           "[[=round(L('acct.A1.visits')[5]*L('acct.A1.average_order'))|money]]."),
         T("Days to pay are up from about [[acct.A1.days_to_pay.until|int]] to "
           "[[acct.A1.days_to_pay.last_three_paid[0]|int]], [[acct.A1.days_to_pay.last_three_paid[1]|int]] and "
           "[[acct.A1.days_to_pay.last_three_paid[2]|int]] on the last three paid statements.",
           "Срок оплаты вырос примерно с [[acct.A1.days_to_pay.until|int]] до [[acct.A1.days_to_pay.late|int]] дней "
           "по счетам двухмесячной давности."),
         T("The bills unpaid at T: {a1_unpaid_bills}.", "Счета, не оплаченные на сегодня: {a1_unpaid_bills}.")],
  computed=[A1_UNPAID], keys=["time.junior_history_days"],
  proof=[("erp", "repair_order, statement, payment")], sources=["erp"])

Q("S16.4", file=F % 16, ref="S16.4", story="S16", asker=6, kind="nothing", small=True,
  src_q="Is any task of mine overdue?",
  q=T("Is any task of mine overdue?", "У меня есть просроченные задачи?"),
  scope=dict(population="Her open cards.", period="At T.", definition="A card past its due time."),
  answer=T("None.", "Нет."),
  nothing=T("None of her [[board.open_at_t.junior_operator.open|int]] open cards is past its due time: the review "
            "card is due at 12:00 on {s16_due_day}, [[board.open_at_t.junior_operator.for_today|int]] are due today "
            "and not yet past their time, the hand-over card of Rachel Dunlap's return chat has no due date, and two "
            "more.",
            "Ни одна из её [[board.open_at_t.junior_operator.open|int]] открытых задач не просрочена; срок задачи "
            "по обзору ещё не наступил."),
  computed=[DUE], keys=["s16.card"],
  proof=[("core", "work.work_item")], sources=["core"])
