# Story cards S05 to S08 (stories/S05.md .. S08.md).
from dsl import C, Q, T, day
from stories_a import P6_LAST, PRICE_RISE

F = "stories/S%02d.md"

# ----------------------------------------------------------------------------------------------- S05
WEEK_FROM = C("s5_week_from", "the first day of slot 16's week off",
              "the Thursday of week W+1; the Wednesday if the Thursday or Friday of W+1 is closed in the market",
              "core", ["workforce.availability"], {"en": ("2026-11-19", "2026-11-19 to 2026-11-25"),
                                                   "ru": ("2026-11-19", "2026-11-19 to 2026-11-25")})
WEEK_TO = C("s5_week_to", "the last day of slot 16's week off", "the Wednesday of week W+2",
            "core", ["workforce.availability"], {"en": ("2026-11-25", "2026-11-19 to 2026-11-25"),
                                                 "ru": ("2026-11-25", "2026-11-19 to 2026-11-25")})
REQ_DAYS = [
    C("s5_req_day_1", "the date of the first published shift inside her week off",
      "the shift of her first open request of kind remove (en: the Thursday of W+1; ru: her first rota day on or "
      "after the week's first day)", "core", ["workforce.shift_change_request", "workforce.shift"]),
    C("s5_req_day_2", "the date of the second published shift inside her week off",
      "the shift of her second open request (en: the Friday of W+1; ru: her next rota day)",
      "core", ["workforce.shift_change_request", "workforce.shift"]),
]

Q("S05.1", file=F % 5, ref="S5.1", story="S05", asker=4, kind="value", small=True,
  src_q="What happens at Bonny Oaks when Angie is off? (old: what happens at `east` when she is off)",
  q=T("What happens at Bonny Oaks when Angie is off?", "Что происходит на Инженерном, когда Светы нет в смене?"),
  scope=dict(population="Inspection-raised jobs at east.", period="G to T.",
             definition="Approved over approved plus declined, on days with and without a shift of hers; average "
                        "order on the same days."),
  tolerance="4 points",
  answer=T("Less recommended work is sold: [[s5.east_with_16|pct0]] of the jobs an inspection raises are approved "
           "on days she works, [[s5.east_without_16|pct]] on her days off. The average order before tax falls with it, by "
           "about [[s5.order_value_drop|money]].",
           "Хуже продаются рекомендованные работы: в её смены клиенты соглашаются на [[s5.east_with_16|pct0]] работ, "
           "найденных на осмотре, без неё — на [[s5.east_without_16|pct]]. Вместе с этим падает и средний наряд — "
           "примерно на [[s5.order_value_drop|money]] без НДС."),
  keys=["p16.sold_rec", "p17.sold_rec", "sold.east"],
  proof=[("erp", "order_job by day"), ("core", "workforce.shift")], sources=["erp", "core"])

Q("S05.2", file=F % 5, ref="S5.2", story="S05", asker=4, kind="list", small=True, depends_on="S05.1",
  src_q="Who can cover her week?",
  q=T("Who can cover her week?", "Кто может заменить её на неделе отпуска?"),
  scope=dict(population="The dates of her week off.", period="The Thursday of W+1 to the Wednesday of W+2.",
             definition="For each date: the desk cover at east against the requirement, and the advisors with no "
                        "shift, no unavailability and no rest-rule clash that day."),
  answer=T("For each day of the week, who is free ({s5_cover_by_day}): Brenda Pickett, part-time and free on "
           "weekdays, and Maya Torres on days East Main keeps two advisors. The week runs from {s5_week_from} to "
           "{s5_week_to}; two days are published and still hers; on the draft days nobody is at her desk.",
           "По каждому дню недели — кто свободен ({s5_cover_by_day}): Артём Николаев, Алина Хасанова и Татьяна "
           "Геннадьевна Пахомова, каждый в свои выходные по графику. Неделя идёт с {s5_week_from} по {s5_week_to}; "
           "две смены уже опубликованы и остаются за ней; в черновике на остальные дни на её месте никого нет."),
  list_rule="For each date of the week off: the advisors with no shift, no unavailability and no rest-rule clash "
            "that day (en: slot 29, and slot 6 on days main keeps two advisors; ru: slots 17, 6 and 29 on their own "
            "days off).",
  member_slot="s5_cover_by_day",
  facts=[T("The week runs from {s5_week_from} to {s5_week_to}.", "Неделя идёт с {s5_week_from} по {s5_week_to}."),
         T("[[s5.week_off.published_shifts_inside|int]] days are published and still hers: her requests are open, "
           "nothing is approved.",
           "[[s5.week_off.published_shifts_inside|int]] смены опубликованы и остаются за ней: заявки открыты, "
           "ничего не согласовано."),
         T("On the draft days nobody is at her desk.", "В черновике на остальные дни на её месте никого нет."),
         T("Who is free on each day: {s5_cover_by_day}.", "Кто свободен в каждый из дней: {s5_cover_by_day}.")],
  computed=[WEEK_FROM, WEEK_TO,
            C("s5_cover_by_day", "per date of the week off, the advisors who can take her desk",
              "workforce.shift, availability and the rest rule per advisor and date; coverage_requirement for the "
              "desk at east", "core", ["workforce.shift", "workforce.availability", "workforce.coverage_requirement"])],
  keys=["roster.advisor_pattern"],
  proof=[("core", "roster reads")], sources=["core"])

Q("S05.3", file=F % 5, ref="S5.3", story="S05", asker=4, kind="explanation", small=True,
  src_q="What did the diagnostician's leave cost?",
  q=T("What did the diagnostician's leave cost?", "Во что нам обошёлся отпуск диагноста?"),
  scope=dict(population="main.", period="The two weeks of the leave against the four weeks before.",
             definition="Wait of diagnostic orders from opening to work; orders sent to east; billed hours."),
  answer=T("Two days' extra wait on diagnostic orders, [[s5.leave.orders_sent_to_east|int]] orders moved to Bonny "
           "Oaks, and billed hours [[s5.leave_drop_pct|pct0]] down in the two weeks.",
           "Наряды на диагностику ждали на два дня дольше, [[s5.leave.orders_sent_to_east|int]] нарядов ушли на "
           "Инженерный, а нормо-часов за эти две недели закрыто на [[s5.leave_drop_pct|pct0]] меньше."),
  facts=[T("Diagnostic orders at East Main waited [[s5.leave.wait_days_in_leave|num]] days from opening to work, "
           "against [[s5.leave.wait_days_normal|num]] normally: "
           "[[=L('s5.leave.wait_days_in_leave')-L('s5.leave.wait_days_normal')|num]] days more.",
           "Наряды на диагностику на Московском шоссе ждали начала работ [[s5.leave.wait_days_in_leave|num]] дня "
           "вместо обычных [[s5.leave.wait_days_normal|num]]: на "
           "[[=L('s5.leave.wait_days_in_leave')-L('s5.leave.wait_days_normal')|num]] дня дольше."),
         T("[[s5.leave.orders_sent_to_east|int]] orders were moved to Bonny Oaks.",
           "[[s5.leave.orders_sent_to_east|int]] нарядов ушли на Инженерный."),
         T("East Main's billed hours in the two weeks were [[s5.leave_drop_pct|pct0]] under the four weeks before.",
           "Нормо-часов на Московском шоссе за эти две недели закрыто на [[s5.leave_drop_pct|pct0]] меньше, чем за "
           "четыре недели до отпуска.")],
  proof=[("erp", "repair_order, order_status_history, order_labor")], sources=["erp"])

Q("S05.4", file=F % 5, ref="S5.4", story="S05", asker=4, kind="smoke", small=True,
  src_q="What is waiting for my decision about next week's roster?",
  q=T("What is waiting for my decision about next week's roster?",
      "Что по графику на следующую неделю ждёт моего решения?"),
  scope=dict(population="Open change requests.", period="At T.", definition="Requests of kind remove, still open."),
  answer=T("Angie Holloway's [[s5.week_off.open_requests|int]] requests to come off her shifts of {s5_req_day_1} "
           "and {s5_req_day_2}, the Thursday and the Friday of next week, filed on {s5_requests_filed}, each with "
           "its reason.",
           "[[s5.week_off.open_requests|int]] заявки Светланы Юрьевны Демидовой: снять её со смен {s5_req_day_1} и "
           "{s5_req_day_2} — двух её опубликованных смен на неделе отпуска. Поданы {s5_requests_filed}, в каждой "
           "указана причина."),
  facts=[T("Her [[s5.week_off.open_requests|int]] requests to come off the shifts of {s5_req_day_1} and "
           "{s5_req_day_2}.",
           "[[s5.week_off.open_requests|int]] её заявки: снять со смен {s5_req_day_1} и {s5_req_day_2}."),
         T("Both were filed on {s5_requests_filed}, her 3rd working day before T.",
           "Обе поданы {s5_requests_filed}, за три её рабочих дня до сегодняшнего."),
         T("Each carries its reason.", "В каждой указана причина.")],
  computed=REQ_DAYS + [C("s5_requests_filed", "the day she filed both requests", "her 3rd working day before T",
                         "core", ["workforce.shift_change_request"])],
  keys=["s5.dates"],
  proof=[("core", "workforce.shift_change_request")], sources=["core"])

# ----------------------------------------------------------------------------------------------- S06
CALL15 = C("s6_call_15_day", "the day of call 15",
           "en: west's 4th full open day before T; ru: slot 23's 3rd working day before T",
           "core", ["interactions.interaction"],
           {"en": ("2026-11-09", "ru slot 23's 3rd working day back | 2026-11-09"),
            "ru": ("2026-11-08", "ru slot 23's 3rd working day back | 2026-11-08")})
CALL16 = C("s6_call_16_day", "the day of the missed call and of call 16",
           "en: west's last full open day before T; ru: slot 23's last working day before T",
           "core", ["interactions.interaction", "missed_call"],
           {"en": ("2026-11-12", "ru slot 23's last working day | 2026-11-12"),
            "ru": ("2026-11-12", "ru slot 23's last working day | 2026-11-12")})

Q("S06.1", file=F % 6, ref="S6.1", story="S06", asker=2, kind="explanation", small=True,
  src_q="Why do cars stay longer at `west`? (old: why is `west` slow)",
  q=T("Why do cars stay longer at Charlotte Pike?", "Почему на Технической машины стоят дольше?"),
  scope=dict(population="Orders by shop; purchase orders by vendor.", period="Since the purchase.",
             definition="Share of orders with more than a day in waiting_parts; purchase orders received on the "
                        "promised day."),
  answer=T("Parts: [[parts.wait_over_a_day.west|pct]] of its orders wait over a day for parts against "
           "[[parts.wait_over_a_day.home|pct]] at the home shops, and its supplier is on time "
           "[[parts.on_time.V2|pct]] of the time against [[parts.on_time.V1|pct]].",
           "Из-за запчастей: [[parts.wait_over_a_day.west|pct]] её нарядов больше суток ждут запчасти, в "
           "ульяновских сервисах — [[parts.wait_over_a_day.home|pct]]; её поставщик привозит в обещанный день в "
           "[[parts.on_time.V2|pct]] случаев, ульяновский — в [[parts.on_time.V1|pct]]."),
  facts=[T("[[parts.wait_over_a_day.west|pct]] of Charlotte Pike's orders spend more than a day waiting for parts, "
           "against [[parts.wait_over_a_day.home|pct]] at the home shops.",
           "[[parts.wait_over_a_day.west|pct]] нарядов Технической больше суток стоят в ожидании запчастей; в "
           "ульяновских сервисах таких [[parts.wait_over_a_day.home|pct]]."),
         T("Its supplier, Harpeth Valley Parts Supply, delivers on the promised day [[parts.on_time.V2|pct]] of the "
           "time; the home supplier, Sequoyah Parts Supply, [[parts.on_time.V1|pct]].",
           "Её поставщик, «Казань-АвтоСнаб», привозит в обещанный день в [[parts.on_time.V2|pct]] случаев; "
           "ульяновский «АвтоДеталь-Венец» — в [[parts.on_time.V1|pct]].")],
  proof=[("erp", "order_status_history, purchase_order")], sources=["erp"])

Q("S06.2", file=F % 6, ref="S6.2", story="S06", asker=22, kind="list", small=True,
  src_q="Which cars are waiting for parts at `west` now, and for how long?",
  q=T("Which cars are waiting for parts at Charlotte Pike now, and for how long?",
      "Какие машины на Технической сейчас ждут запчасти и сколько дней?"),
  scope=dict(population="Orders at west in status waiting_parts.", period="At T.",
             definition="Calendar days in the status."),
  answer=T("[[=len(L('s6.waiting_at_t.west_days'))|int]] cars, longest first: [[s6.waiting_at_t.west_days[0]|int]], "
           "[[s6.waiting_at_t.west_days[1]|int]], [[s6.waiting_at_t.west_days[2]|int]], "
           "[[s6.waiting_at_t.west_days[3]|int]] and [[s6.waiting_at_t.west_days[4]|int]] days ({s6_waiting_west}); "
           "the longest is Curtis Vaughn's Volvo XC60.",
           "[[=len(L('s6.waiting_at_t.west_days'))|int]] машин, начиная с той, что стоит дольше всех: "
           "[[s6.waiting_at_t.west_days[0]|int]], [[s6.waiting_at_t.west_days[1]|int]], "
           "[[s6.waiting_at_t.west_days[2]|int]], [[s6.waiting_at_t.west_days[3]|int]] дня и "
           "[[s6.waiting_at_t.west_days[4]|int]] день ({s6_waiting_west}); дольше всех ждёт Peugeot Айрата "
           "Гизатуллина."),
  list_rule="Orders at west in status waiting_parts at T, longest first, each with its calendar days in the status; "
            "the longest named.",
  member_slot="s6_waiting_west",
  computed=[C("s6_waiting_west", "the five orders with customer, car and days waiting",
              "repair_order at west with status waiting_parts at T; days = T minus the status change",
              "erp", ["repair_order", "order_status_history"])],
  proof=[("erp", "repair_order")], sources=["erp"])

Q("S06.3", file=F % 6, ref="S6.3", story="S06", asker=2, kind="explanation", small=False,
  src_q="Is the brake problem the mechanic or the parts?",
  q=T("Is the brake problem the mechanic or the parts?", "Проблема с тормозами — это механик или запчасти?"),
  scope=dict(population="Pad jobs by pad brand and mechanic.",
             period="Since the purchase (west) and over the history (home shops).",
             definition=T("A comeback: a warranty or goodwill order pointing at the first order.",
                          "A comeback: a warranty or goodwill order pointing at the first order, opened within 30 "
                          "days of it.")),
  answer=T("Both: the cheap pads come back about [[s6.pad_factor|int]] times as often for anyone, and Derek Hooper "
           "comes back more than anyone else on other pads too.",
           "И то и другое: дешёвые колодки возвращаются примерно в [[s6.pad_factor|int]] раза чаще у кого угодно, а "
           "у Виталия Сомова больше возвратов, чем у остальных, и на других колодках."),
  facts=[T("Both.", "И то и другое."),
         T("The cheap brand, [[s6.brand|text]], comes back about [[s6.pad_factor|int]] times as often whoever fits "
           "it: [[s6.rate.cheap.others|pct]] for his colleagues and [[s6.rate.cheap.p27|pct]] for Derek Hooper, "
           "against [[s6.rate.good.others|pct]] and [[s6.rate.good.p27|pct]] on other pads.",
           "Дешёвые колодки [[s6.brand|text]] возвращаются примерно в [[s6.pad_factor|int]] раза чаще, кто бы их ни "
           "ставил: [[s6.rate.cheap.others|pct]] у его коллег и [[s6.rate.cheap.p27|pct]] у Виталия Сомова против "
           "[[s6.rate.good.others|pct]] и [[s6.rate.good.p27|pct]] на остальных колодках."),
         T("Derek Hooper comes back more than anyone else on other pads too: [[s6.rate.good.p27|pct]] against "
           "[[s6.rate.good.others|pct]].",
           "У Сомова и на остальных колодках возвратов больше, чем у всех: [[s6.rate.good.p27|pct]] против "
           "[[s6.rate.good.others|pct]]."),
         T("Counts: Hooper [[s6.counts.comebacks_p27_good|int]] of [[s6.counts.p27_good|int]] on other brands and "
           "[[s6.counts.comebacks_p27_cheap|int]] of [[s6.counts.p27_cheap|int]] on the cheap brand; his colleagues "
           "at Charlotte Pike [[s6.counts.comebacks_others_cheap|int]] of [[s6.counts.others_cheap|int]] on the cheap "
           "brand and [[s6.counts.comebacks_others_good_at_west|int]] of [[s6.counts.others_good|int]] on other "
           "brands; everyone but him on other brands, all shops, "
           "[[s6.counts.comebacks_good_not_27_all_shops|int]] of [[s6.counts.good_pad_jobs_not_27_all_shops|int]].",
           "В штуках: Сомов — [[s6.counts.comebacks_p27_good|int]] из [[s6.counts.p27_good|int]] на остальных "
           "брендах и [[s6.counts.comebacks_p27_cheap|int]] из [[s6.counts.p27_cheap|int]] на дешёвом; его коллеги "
           "на Технической — [[s6.counts.comebacks_others_cheap|int]] из [[s6.counts.others_cheap|int]] на дешёвом и "
           "[[s6.counts.comebacks_others_good_at_west|int]] из [[s6.counts.others_good|int]] на остальных; все, "
           "кроме него, на остальных брендах по трём сервисам — "
           "[[s6.counts.comebacks_good_not_27_all_shops|int]] из "
           "[[s6.counts.good_pad_jobs_not_27_all_shops|int]].")],
  keys=["comeback.definition", "s6.p27_pad_share", "s6.cheap_share"],
  proof=[("erp", "comeback orders; order_part (brand), order_labor (mechanic)")], sources=["erp"])

Q("S06.4", file=F % 6, ref="S6.4", story="S06", asker=2, kind="smoke", small=True,
  src_q="What was decided about `west`'s supplier? (old: what was decided about it)",
  q=T("What was decided about Charlotte Pike's supplier?", "Что решили по поставщику Технической?"),
  scope=dict(population="Cards about the supplier.", period="At T.", definition="The card, its owner and its state."),
  answer=T("Her card for Dale Hutchins, to move Charlotte Pike to the home supplier, was due {s6_task_due}; it is "
           "open and three weeks overdue.",
           "Её задача Ринату Фаридовичу Галиеву — перевести Техническую на ульяновского поставщика — со сроком "
           "{s6_task_due}; задача открыта и просрочена на три недели."),
  facts=[T("Her card for Dale Hutchins: move Charlotte Pike to the home supplier.",
           "Её задача Ринату Фаридовичу Галиеву: перевести Техническую на ульяновского поставщика."),
         T("It was due {s6_task_due}.", "Срок был {s6_task_due}."),
         T("It is open and three weeks overdue.", "Задача открыта и просрочена на три недели.")],
  computed=[C("s6_task_due", "the card's due date", "due_at of slot 2's card owned by slot 22; anchor: the Monday of "
              "week T-3", "core", ["work.work_item"], {"en": ("2026-10-19", "2026-09-21; 2026-10-19"),
                                                       "ru": ("2026-10-19", "2026-09-21; 2026-10-19")})],
  keys=["s6.supplier_task"],
  proof=[("core", "work.work_item")], sources=["core"])

Q("S06.5", file=F % 6, ref="S6.5", story="S06", asker=22, kind="explanation", small=True,
  src_q="What did we promise the customer whose car has waited longest at `west`? (old: whose car has waited nine "
        "days)",
  q=T("What did we promise the customer whose car has waited longest at Charlotte Pike?",
      "Что мы обещали клиенту, чья машина на Технической ждёт запчасть дольше всех?"),
  scope=dict(population="His calls and messages.", period="The last 14 days.", definition="All stores."),
  answer=T("On {s6_call_15_day} Chad Binkley promised a day that has passed and did not note the added work; of the "
           "customer's [[s6.customer_contacts.messages|int]] messages, three were answered late and the fourth is "
           "unanswered, with a draft waiting; on {s6_call_16_day} a missed call and then a call that ended with his "
           "question unanswered.",
           "{s6_call_15_day} Вячеслав Крюков пообещал день готовности, который уже прошёл, и не записал допработы; "
           "из [[s6.customer_contacts.messages|int]] сообщений клиента на три ответили с опозданием, четвёртое до "
           "сих пор без ответа, в чате ждёт черновик; {s6_call_16_day} — пропущенный звонок, а потом разговор, после "
           "которого клиент так и не получил ответа на свой вопрос."),
  facts=[T("On {s6_call_15_day}, on the phone, Chad Binkley promised a day; that day has passed.",
           "{s6_call_15_day} Вячеслав Крюков по телефону пообещал день готовности; этот день уже прошёл."),
         T("That call scored [[s6.customer_contacts.call_15_score|num]] with the auto-fail `wrong_promise`.",
           "Этот звонок получил оценку [[s6.customer_contacts.call_15_score|num]] с автоматическим провалом "
           "`wrong_promise`."),
         T("He did not note the added work the customer asked for.",
           "Допработы, о которых просил клиент, он не записал."),
         T("The customer wrote [[s6.customer_contacts.messages|int]] messages; each waited over "
           "[[s6.customer_contacts.each_waited_hours_over|int]] working hours for a person's reply.",
           "Клиент написал [[s6.customer_contacts.messages|int]] сообщения; ответа сотрудника на каждое из первых "
           "трёх он ждал больше [[s6.customer_contacts.each_waited_hours_over|int]] рабочих часов."),
         T("Three of them were answered late, by Chad Binkley.",
           "На все три с опозданием ответил Вячеслав Крюков."),
         T("The fourth is unanswered at T, with a draft reply waiting.",
           "Четвёртое до сих пор без ответа; в чате ждёт черновик ответа."),
         T("On {s6_call_16_day} his call was missed in the morning; he got through in the afternoon, and that call "
           "ended with his question unanswered.",
           "{s6_call_16_day} утром его звонок пропустили; днём он дозвонился, но разговор закончился, а ответа на "
           "свой вопрос он не получил."),
         T("That call carries the auto-fail `dropped_customer`.",
           "У этого звонка автоматический провал `dropped_customer`.")],
  computed=[CALL15, CALL16],
  proof=[("core", "calls by his number"), ("conversations", "his web chat")], sources=["core", "conversations"],
  keys=["s6.customer_contacts"])

Q("S06.6", file=F % 6, ref="S6.6", story="S06", asker=6, kind="refusal", small=True,
  src_q="Who is in `west`'s call-back queue?",
  q=T("Who is in Charlotte Pike's call-back queue?", "Кто в списке на перезвон на Технической?"),
  scope=dict(population="The queue.", period="At T.", definition="Her rank is bound to main."),
  answer=T("Refused by site.", "Отказ по площадке."),
  refusal=dict(by="site",
               reason=T("Her rank is bound to East Main; she cannot read Charlotte Pike's queue.",
                        "Её доступ ограничен Московским шоссе; список Технической ей недоступен.")),
  proof=[("core", "site binding")], sources=["core"], known_failure=True)

# ----------------------------------------------------------------------------------------------- S07
CHAT_DAY = C("s7_chat_day", "the evening of her first web chat", "the evening before day A (slot 6's 14th working "
             "day before T in en, her 10th in ru), 21:10", "conversations", ["conversations", "messages"],
             day("2026-10-25", "2026-10-23"))
VISIT_DAY = C("s7_visit_day", "the day of the visit", "slot 6's next working day after day A",
              "erp", ["repair_order", "appointment"], day("2026-10-27", "2026-10-25"))
RETURN_DAY = dict(P6_LAST, slot="s7_return_day", what="the day she came back to the web chat",
                  store="conversations", tables=["conversations", "messages"])

Q("S07.1", file=F % 7, ref="S7.1", story="S07", asker=6, kind="explanation", small=True,
  src_q="Tell me everything about Rachel Dunlap. (old: tell me everything about this customer)",
  q=T("Tell me everything about Rachel Dunlap.", "Покажите всё, что у нас есть по Ольге Сергеевне Тимофеевой."),
  scope=dict(population="Every store.", period="The whole history.",
             definition="Joined by her phone (the demo tenant shows a customer's phone from junior up)."),
  answer=T("Her web chat, the booking and the confirming call, the visit and what it found, the brakes approved and "
           "paid, the shock absorbers declined and deferred, her thank-you, and the return chat, open and hers, "
           "with a draft waiting.",
           "Чат на сайте, запись и звонок с подтверждением, заезд и что на нём нашли, согласованные и оплаченные "
           "тормоза, отложенные амортизаторы, её благодарность и новый чат — открытый, закреплённый за Алиной, с "
           "черновиком ответа."),
  facts=[T("Her web chat about a brake noise, on the evening of {s7_chat_day}.",
           "Чат на сайте про шум при торможении, вечером {s7_chat_day}."),
         T("The booking Maya Torres made the next morning.",
           "Запись, которую на следующее утро сделала Алина Хасанова."),
         T("The confirming call to her that day.", "Звонок клиентке в тот же день с подтверждением записи."),
         T("The visit on {s7_visit_day}: the inspection found worn front pads and rotors and a seeping rear shock "
           "absorber.",
           "Заезд {s7_visit_day}: на осмотре нашли изношенные передние колодки и диски и подтекающий задний "
           "амортизатор."),
         T("She approved the brakes and paid [[s7.bill.with_tax|money2]] by card.",
           "Тормоза она согласовала и оплатила картой: [[s7.bill.with_tax|money2]] с НДС."),
         T("She declined the rear shock absorbers; they are marked deferred.",
           "От задних амортизаторов отказалась; работа отмечена как отложенная."),
         T("Her thank-you message the day after the visit.", "На следующий день после заезда она написала спасибо."),
         T("She came back to the website chat on {s7_return_day}: the chat is open, owned by Maya Torres, with a "
           "draft waiting.",
           "{s7_return_day} она снова написала в чат на сайте: чат открыт, закреплён за Алиной Хасановой, в нём "
           "ждёт черновик ответа.")],
  computed=[CHAT_DAY, VISIT_DAY, RETURN_DAY],
  proof=[("erp", "by customer.phone"), ("core", "by phone('<number>')"),
         ("conversations", "by the hand-off notes and cards that carry her number (the web contact holds none)")],
  sources=["erp", "core", "conversations"])

Q("S07.2", file=F % 7, ref="S7.2", story="S07", asker=6, kind="value", small=True, depends_on="S07.1",
  src_q="What did she decline, and has she come back for it?",
  q=T("What did she decline, and has she come back for it?",
      "От чего она тогда отказалась и обращалась ли потом по этому поводу?"),
  scope=dict(population="Her order's declined jobs; her later contacts.", period="The whole history.",
             definition="Declined and deferred jobs; any later contact that asks for them."),
  answer=T("The rear shock absorbers, a pair. Yes: on {s7_return_day} she asked in the website chat to book them.",
           "От замены задних амортизаторов, пары. Да: {s7_return_day} она написала в чат на сайте и попросила "
           "записать её на эту работу."),
  computed=[RETURN_DAY],
  proof=[("erp", "order_job"), ("conversations", "the return chat")], sources=["erp", "conversations"])

Q("S07.3", file=F % 7, ref="S7.3", story="S07", asker=6, kind="action", small=True, depends_on="S07.2",
  src_q="What should I answer her?",
  q=T("What should I answer her?", "Что ей ответить?"),
  scope=dict(population="The open chat; free appointment times at main; today's price list.",
             period="The next seven days.",
             definition=T("Class car, standard parts; the days and the time of day she asked for in her last message.",
                          "Class car, standard parts, VAT inside; the days and the time of day she asked for in her "
                          "last message.")),
  answer=T("A draft reply that offers two free times early on the Wednesday or the Thursday of next week, the days she "
           "asked for (nothing after 10:30 on the Thursday, the stocktake day), and the price: "
           "[[s7.bill.declined_rear_shocks|money2]] for the pair plus shop supplies, "
           "[[s7.bill.declined_with_tax|money2]] with tax.",
           "Черновик ответа с двумя свободными временами во вторник или в среду следующей недели, вечером, как "
           "она просила, и с ценой: [[s7.bill.declined_rear_shocks|money]] за пару плюс расходные материалы, к "
           "оплате [[s7.bill.declined_with_tax|money2]], НДС в цене."),
  action=dict(proposes=T("A reply that offers two appointment times free at East Main on the days and at the time of "
                         "day she asked for (early on the Wednesday or the Thursday of next week; the Thursday not "
                         "after 10:30) and gives the price: [[s7.bill.declined_rear_shocks|money2]] plus shop "
                         "supplies, [[s7.bill.declined_with_tax|money2]] with tax.",
                         "Ответ, в котором предложены два свободных времени на Московском шоссе в те дни и в то "
                         "время, о которых она просила в последнем сообщении (вторник или среда следующей недели, "
                         "вечером), и названа цена: [[s7.bill.declined_rear_shocks|money]] плюс расходные "
                         "материалы, к оплате [[s7.bill.declined_with_tax|money2]], НДС в цене."),
              passes_if=T("Any two times pass that are free in the shop system's appointments on those days and at "
                          "that time of day. It is offered as a draft; nothing is sent without her.",
                          "Подходят любые два времени в эти дни, вечером, свободные в записи учётной программы. "
                          "Ответ предлагается как черновик; без неё ничего не отправляется.")),
  pages=["prices/price-list.md"], keys=["kb.stocktake.rules"],
  proof=[("erp", "appointment"), ("knowledge_base", "price list")], sources=["erp", "knowledge_base", "conversations"])

Q("S07.4", file=F % 7, ref="S7.4", story="S07", asker=6, kind="nothing", small=True, depends_on="S07.1",
  src_q="What score did my confirming call to her get?",
  q=T("What score did my confirming call to her get?",
      "Какую оценку получил мой звонок ей с подтверждением записи?"),
  scope=dict(population="The call of day A.", period="Day A.", definition="An outbound call is not judged."),
  answer=T("None.", "Никакую."),
  nothing=T("An outbound call is not judged.", "Исходящие звонки не оцениваются."),
  proof=[("core", "interaction_analysis.result_public.judged")], sources=["core"])

# ----------------------------------------------------------------------------------------------- S08
Q("S08.1", file=F % 8, ref="S8.1", story="S08", asker=4, kind="explanation", small=True,
  src_q="What went wrong with Frank Daugherty's timing-belt job? (old: what went wrong with this customer's job)",
  q=T("What went wrong with Frank Daugherty's timing-belt job?",
      "Что пошло не так с заменой ремня ГРМ у Фомичёва?"),
  scope=dict(population="The customer.", period="The last 14 days.", definition="All stores."),
  answer=T("A quote at the old price with a same-day promise, a car ready a working day late, a bill above the "
           "quote, an argument and a complaint call, then a goodwill discount and a call back.",
           "Старая цена и обещание сделать в тот же день, машина готова на рабочий день позже, счёт больше "
           "названного, спор на приёмке и звонок с жалобой, потом скидка и ответный звонок."),
  facts=[T("Caleb Sutton quoted the old price: [[s8.price_quoted|money]] against [[s8.price_now|money]] at today's "
           "list.",
           "Никита Ведяшкин назвал старую цену: [[s8.price_quoted|money]] вместо [[s8.price_now|money]] по "
           "действующему прайсу."),
         T("He promised the car the same day.", "Он пообещал отдать машину в тот же день."),
         T("The car was ready a working day late.", "Машина была готова на рабочий день позже."),
         T("The bill was [[s8.bill_before_tax|money2]] before tax.",
           "Счёт вышел на [[s8.bill_list|money2]]."),
         T("The customer argued at the desk and rang to complain that afternoon.",
           "Клиент поспорил на приёмке и в тот же день позвонил с жалобой."),
         T("Greg Whitaker gave a discount of [[s8.discount|money]] and called him back.",
           "Сергей Анатольевич Мельников сделал скидку [[s8.discount|money]] и перезвонил клиенту.")],
  proof=[("core", "calls 9 to 11"), ("erp", "the order")], sources=["core", "erp"])

Q("S08.2", file=F % 8, ref="S8.2", story="S08", asker=4, kind="value", small=True, depends_on="S08.1",
  src_q="Was the discount inside our rules?",
  q=T("Was the discount inside our rules?", "Скидка была по правилам?"),
  scope=dict(population=T("The order's discount over its bill before tax.",
                          "The order's discount over its bill as billed, VAT inside (ledger row price.discount_base: "
                          "the share is the same on the amount before VAT)."),
             period="The order.",
             definition="Against the rule: above 10 % needs the senior's approval, recorded on the order."),
  answer=T("Yes: [[s8.discount|money]] on [[s8.bill_before_tax|money2]] is [[s8.discount_pct|pct1]], above "
           "[[price.discount_rule_pct|pct]], so it needed the senior's approval; Greg Whitaker approved it and it is "
           "recorded on the order.",
           "Да: [[s8.discount|money]] от [[s8.bill_list|money2]] — это [[s8.discount_pct|pct1]], "
           "больше [[price.discount_rule_pct|pct]], поэтому нужно согласование руководителя сервиса; Сергей "
           "Анатольевич Мельников её согласовал, и это отмечено в наряде."),
  keys=["price.discount_base"],
  proof=[("erp", "repair_order")], sources=["erp", "knowledge_base"])

Q("S08.3", file=F % 8, ref="S8.3", story="S08", asker=5, kind="explanation", small=True,
  context="The wrong price is the one quoted to Frank Daugherty (ru: Игорь Валентинович Фомичёв) for his "
          "timing-belt job.",
  src_q="Where did the wrong price come from?",
  q=T("Where did the wrong price come from?", "откуда вообще взялась неправильная цена"),
  scope=dict(population="Knowledge pages.", period="At T.", definition="The page whose text gives the quoted price."),
  answer=T("From the service page “Timing belt”, which still uses the labour hour from before the rise and gives "
           "[[s8.price_quoted|money]]; the price list gives [[s8.price_now|money]].",
           "Со страницы услуги «Ремень ГРМ»: в её тексте остался нормо-час до повышения и сумма "
           "[[s8.price_quoted|money]]; в прайс-листе — [[s8.price_now|money]]."),
  facts=[T("The service page “Timing belt”: its text still uses the hour from before the rise and gives "
           "[[s8.price_quoted|money]].",
           "Страница услуги «Ремень ГРМ»: в её тексте остался нормо-час до повышения, и сумма там "
           "[[s8.price_quoted|money]]."),
         T("Its “Last reviewed” date is before the price rise of {price_rise_day}.",
           "Дата «Проверено» на ней — раньше повышения цен {price_rise_day}."),
         T("The price list gives [[s8.price_now|money]] since the rise.",
           "В прайс-листе с повышения стоит [[s8.price_now|money]].")],
  computed=[PRICE_RISE], pages=["services/engine/timing-belt.md", "prices/price-list.md"],
  proof=[("knowledge_base", "pages \"Timing belt\" and \"Price list\"")], sources=["knowledge_base"])

Q("S08.4", file=F % 8, ref="S8.4", story="S08", asker=4, kind="nothing", small=True, depends_on="S08.1",
  src_q="What did the complaint call score?",
  q=T("What did the complaint call score?", "Какую оценку получил звонок с жалобой?"),
  scope=dict(population="Call 10.", period="The day the car was ready.",
             definition="A complaint about an existing job carries no score."),
  answer=T("Nothing.", "Никакую."),
  nothing=T("A complaint about an existing job carries no score; only the greeting and the summary were checked.",
            "Звонок с жалобой по уже открытому наряду не оценивается; проверены только приветствие и итог "
            "разговора."),
  proof=[("core", "interaction_analysis")], sources=["core"])
