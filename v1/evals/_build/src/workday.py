# workday/DESIGN.md section 9: the seventeen questions of the working day (W1 to W17).
from dsl import C, Q, T, day

F = "workday/DESIGN.md"
D = lambda quote: (F, quote)  # noqa: E731 - where the design states the value a slot must come to

Q("WD.01", file=F, ref="W1", asker=4, kind="value",
  src_q="Who has not clocked in for a shift that has started?",
  q=T("Who has not clocked in for a shift that has started?", "Кто не отметился на смене, которая уже началась?"),
  scope=dict(population="Published shifts at every site whose start plus grace is before the asking instant.",
             period="At T.", definition="No clock-in."),
  answer=T("Tyler Jarrell at Charlotte Pike, whose shift started at {w1_shift_start}. Nobody else.",
           "Булат Гарипов на Технической: его смена началась в {w1_shift_start}. Больше никто."),
  computed=[C("w1_shift_start", "the start of slot 28's shift on T's date, or nobody",
              "slot 28's shift at west starts at the last quarter-hour at least 15 minutes before T and has no in "
              "punch; if west is closed at T or T is within two hours of its close, nobody is late and the answer is "
              "nobody", "core", ["workforce.shift", "workforce.punch"],
              design=D("his shift at `west` on T's date starts at the last quarter-hour at least 15 minutes before T "
                       "and he has not clocked in"))],
  keys=["late.grace_min"],
  proof=[("core", "workforce.shift, punch")], sources=["core"])

Q("WD.02", file=F, ref="W2", asker=4, kind="list",
  src_q="Which weeks of the roster are not published yet?",
  q=T("Which weeks of the roster are not published yet?", "Какие недели графика ещё не опубликованы?"),
  scope=dict(population="Shifts by site and status.", period="From T to T+14 d.", definition="A week whose shifts "
             "are a draft."),
  answer=T("At East Main and Bonny Oaks the week after next is a draft; at Charlotte Pike next week is.",
           "На Московском шоссе и Инженерном черновик — неделя после следующей; на Технической — уже следующая."),
  list_rule="Per site, the weeks between T and T+14 d whose shifts have no publish.",
  members=[T("East Main and Bonny Oaks: the week after next", "Московское шоссе и Инженерный: неделя после следующей"),
           T("Charlotte Pike: next week", "Техническая: следующая неделя")],
  keys=["time.roster_weeks"],
  proof=[("core", "workforce.shift.status, roster_publish")], sources=["core"])

Q("WD.03", file=F, ref="W3", asker=2, kind="explanation",
  src_q="When does Charlotte Pike publish its roster?",
  q=T("When does Charlotte Pike publish its roster?", "Когда Техническая публикует график?"),
  scope=dict(population="roster_publish rows by site.", period="Since G.",
             definition="The publishing instant against the week it covers."),
  answer=T("On the Sunday evening before the week, every week; the home shops publish on the Thursday before, "
           "before noon. The standard is Thursday 12:00.",
           "В воскресенье вечером, накануне самой недели, и так каждую неделю; ульяновские сервисы публикуют в "
           "четверг до полудня. Стандарт — четверг, 12:00."),
  facts=[T("Charlotte Pike publishes on the Sunday evening before the week, every week.",
           "Техническая публикует график в воскресенье вечером, накануне самой недели, — каждую неделю."),
         T("The home shops publish on the Thursday before, before noon.",
           "Ульяновские сервисы публикуют в четверг до полудня, за неделю."),
         T("The standard is Thursday 12:00 the week before.", "Стандарт — четверг, 12:00, за неделю.")],
  keys=["kb.schedule.rules"],
  proof=[("core", "roster_publish.published_at")], sources=["core", "knowledge_base"])

Q("WD.04", file=F, ref="W4", asker=4, kind="value",
  src_q="What did Cody ask for, and what was decided?",
  q=T("What did Cody ask for, and what was decided?", "О чём просил Чугунов и что решили?"),
  scope=dict(population="Slot 15's requests.", period="Since G.", definition="Each request with its outcome."),
  answer=T("[[p15.requests|int]] requests: three changes of hours, two approved and one declined with Greg "
           "Whitaker's note, and one day off he took back himself.",
           "[[p15.requests|int]] заявки: три — на другое время, из них две согласованы и одна отклонена с ответом "
           "Сергея Анатольевича Мельникова; четвёртая — на выходной, её он отозвал сам."),
  facts=[T("[[p15.requests|int]] requests since go-live.", "[[p15.requests|int]] заявки с запуска системы."),
         T("Three changes of hours: two approved, one declined with Greg Whitaker's note.",
           "Три — на другое время: две согласованы, одна отклонена, с ответом Сергея Анатольевича Мельникова."),
         T("One day off, which he took back.", "Одна — на выходной; её он отозвал сам.")],
  proof=[("core", "workforce.shift_change_request")], sources=["core"])

Q("WD.05", file=F, ref="W5", asker=2, kind="list",
  src_q="Which shift requests at Charlotte Pike were never answered?",
  q=T("Which shift requests at Charlotte Pike were never answered?",
      "Какие заявки по сменам на Технической остались без ответа?"),
  scope=dict(population="Requests on west shifts with status expired.", period="Since G.",
             definition="A request that expired with no decision."),
  answer=T("Six: two of Chad Binkley's, one of Jasmine Bolden's, one of Shane Maddox's and two of Tyler Jarrell's, "
           "with their days ({w5_requests}).",
           "Шесть: две — Вячеслава Крюкова, одна — Камилы Шакировой, одна — Станислава Орехова и две — Булата "
           "Гарипова, с датами смен ({w5_requests})."),
  list_rule="Requests since G on shifts at west whose status is expired, with the person and the shift's day.",
  member_slot="w5_requests",
  computed=[C("w5_requests", "the six expired requests (R53, R54, R56, R58, R61, R64) with their shift days",
              "shift_change_request rows on west shifts with status expired",
              "core", ["workforce.shift_change_request"],
              design=D("Six: R53, R54 (slot 23), R56 (24), R58 (26), R61, R64 (28), with their days"))],
  proof=[("core", "workforce.shift_change_request")], sources=["core"])

Q("WD.06", file=F, ref="W6", asker=12, kind="refusal",
  src_q="Show me Dustin's shift requests.",
  q=T("Show me Dustin's shift requests.", "Покажи заявки Макса по сменам."),
  scope=dict(population="Another person's requests.", period="Any.", definition="A worker reads his own requests."),
  answer=T("Refused by rank; his own can be shown.", "Отказ по уровню доступа; его собственные показать можно."),
  refusal=dict(by="rank", reason=T("A worker reads only his own requests.", "Работник видит только свои заявки."),
               may_offer=T("His own requests.", "Его собственные заявки.")),
  proof=[("core", "tool floors")], sources=["core"])

Q("WD.07", file=F, ref="W7", asker=22, kind="value",
  src_q="Was Shane late on the days he clocked in from outside the site?",
  q=T("Was Shane late on the days he clocked in from outside the site?",
      "Стас опаздывал в те дни, когда отмечался не с территории?"),
  scope=dict(population="Slot 26's clock-ins with a location exception.", period="Since G.",
             definition="Lateness of those clock-ins."),
  answer=T("No: both times he was on time, [[s14.instances.p26_far_punches.metres|int]] metres away.",
           "Нет: оба раза он отметился вовремя, в [[s14.instances.p26_far_punches.metres|int]] метрах от сервиса."),
  proof=[("core", "workforce.punch.exception_type, geo_distance_m")], sources=["core"])

Q("WD.08", file=F, ref="W8", asker=6, kind="list",
  src_q="What is on my board?",
  q=T("What is on my board?", "Что у меня на доске?"),
  scope=dict(population="Her open cards.", period="At T.", definition="Each with priority and due time."),
  answer=T("[[board.open_at_t.junior_operator.open|int]]: the review, high priority; "
           "[[board.open_at_t.junior_operator.for_today|int]] due today; three more. None overdue.",
           "[[board.open_at_t.junior_operator.open|int]] задач: обзор — с высоким приоритетом; со сроком сегодня — "
           "[[board.open_at_t.junior_operator.for_today|int]]; ещё три. Просроченных нет."),
  list_rule="Slot 6's open cards at T.",
  members=[T("Prepare Nickajack Delivery's quarterly review (high)",
             "Подготовить квартальный обзор по «Симбирскому гонцу» (высокий приоритет)"),
           T("Estimate to Clabough Brothers Roofing: Ram 2500 front end (due today)",
             "Смета для ИП Трофимова: ГАЗель Next, передняя подвеска (срок сегодня)"),
           T("Confirm the next day's drop-offs by 3:00 (due today)",
             "Подтвердить завтрашние записи до 17:00 (срок сегодня)"),
           T("Rachel Dunlap: book the rear shocks when she picks a day",
             "Тимофеева: записать на задние амортизаторы, когда выберет день"),
           T("Nickajack Delivery: purchase-order numbers on their open orders",
             "«Симбирский гонец»: номера заявок в открытых заказ-нарядах"),
           T("Rewrite my saved replies for tire questions", "Переписать шаблоны ответов про шины")],
  seed_files=["workday/{cfg}/cards.json"],
  proof=[("core", "work.work_item")], sources=["core"])

Q("WD.09", file=F, ref="W9", asker=4, kind="list",
  src_q="Which cards have gone quiet?",
  q=T("Which cards have gone quiet?", "Какие задачи затихли?"),
  scope=dict(population="Open cards with no timeline line for seven days, not due further ahead.", period="At T.",
             definition="Quiet: seven days with no line."),
  answer=T("Two: his alignment-rack card and Dale Hutchins's regulars list.",
           "Две: его задача про второй стенд сход-развала и список постоянных клиентов у Рината Фаридовича "
           "Галиева."),
  list_rule="Open cards with no timeline line for seven days.",
  members=[T("His own: “Bonny Oaks: two quotes for a second alignment rack”",
             "Его собственная: «Инженерный: два предложения на второй стенд сход-развала»"),
           T("Dale Hutchins's: “List Charlotte Pike regulars not seen in six months”",
             "Рината Фаридовича Галиева: «Список постоянных клиентов Технической, не приезжавших полгода»")],
  keys=["board.open_at_t"],
  proof=[("core", "platform.activity")], sources=["core"])

Q("WD.10", file=F, ref="W10", asker=6, kind="nothing",
  src_q="Is any customer waiting for a person at my shop?",
  q=T("Is any customer waiting for a person at my shop?", "У нас на Московском кто-нибудь из клиентов ждёт сотрудника?"),
  scope=dict(population="Unowned hand-over cards at the sites she reads.", period="At T.",
             definition="A hand-over card nobody has taken."),
  answer=T("None.", "Никто."),
  nothing=T("The one customer waiting for a person is at Bonny Oaks, not at East Main.",
            "Единственный клиент, который ждёт сотрудника, — на Инженерном, а не на Московском шоссе."),
  keys=["board.open_at_t"],
  proof=[("core", "work.work_item by site")], sources=["core"])

Q("WD.11", file=F, ref="W11", asker=4, kind="value",
  src_q="Is any customer waiting for a person?",
  q=T("Is any customer waiting for a person?", "Кто-нибудь из клиентов сейчас ждёт сотрудника?"),
  scope=dict(population="Unowned hand-over cards at all sites.", period="At T.",
             definition="A hand-over card nobody has taken."),
  answer=T("One, at Bonny Oaks, waiting since {w11_since}.", "Один, на Инженерном; ждёт с {w11_since}."),
  computed=[C("w11_since", "the instant the unowned hand-over at east was raised", "40 minutes before T",
              "core", ["work.work_item"], design=D("a hand-over at `east`, 40 minutes old"))],
  keys=["board.open_at_t"],
  proof=[("core", "work.work_item by site")], sources=["core"])

Q("WD.12", file=F, ref="W12", asker=6, kind="refusal",
  src_q="Give Donna a task: the days-to-pay table by Monday.",
  q=T("Give Donna a task: the days-to-pay table by Monday.",
      "Поставьте задачу Ирине Владимировне: таблица по срокам оплаты к понедельнику."),
  scope=dict(population="The rank rule.", period="At T.", definition="Work goes on yourself or on lower ranks only."),
  answer=T("Refused: a junior may not put work on a middle. It can offer a comment on the review card.",
           "Отказ: младший менеджер не может ставить задачи менеджеру. Можно предложить комментарий в задаче по "
           "обзору."),
  refusal=dict(by="rank", reason=T("A junior may not put work on a middle.",
                                   "Младший менеджер не может ставить задачи менеджеру."),
               may_offer=T("A comment on the review card.", "Комментарий в задаче по обзору.")),
  proof=[("core", "work_board.py:2052")], sources=["core"])

Q("WD.13", file=F, ref="W13", asker=2, kind="value",
  src_q="How did Dale do with the tasks Claire gave him?",
  q=T("How did Dale do with the tasks I gave him?", "Как Ринат справился с задачами, которые я ему ставила?"),
  scope=dict(population="Cards created by slot 2 and owned by slot 22.", period="Since G.",
             definition="Closed by the due time, closed late, open and overdue."),
  answer=T("[[p22.owner_tasks.given_by_2_since_G|int]]: [[p22.owner_tasks.closed_on_time|int]] closed on time, "
           "[[p22.owner_tasks.closed_late|int]] late, [[p22.owner_tasks.open_overdue_at_T|int]] open and overdue.",
           "Из [[p22.owner_tasks.given_by_2_since_G|int]] задач [[p22.owner_tasks.closed_on_time|int]] закрыты в "
           "срок, [[p22.owner_tasks.closed_late|int]] — с опозданием, [[p22.owner_tasks.open_overdue_at_T|int]] "
           "открыты и просрочены."),
  proof=[("core", "work.work_item, platform.activity")], sources=["core"])

Q("WD.14", file=F, ref="W14", asker=9, kind="nothing",
  src_q="Did anyone decline the stocktake?",
  q=T("Did anyone decline the stocktake?", "Инвентаризация: кто-нибудь отказался?"),
  scope=dict(population="The entry's invitations.", period="At T.", definition="An invitation answered declined."),
  answer=T("Nobody.", "Никто."),
  nothing=T("All three invited people accepted.", "Все трое приглашённых приняли приглашение."),
  proof=[("core", "work.calendar_event_participant")], sources=["core"])

Q("WD.15", file=F, ref="W15", asker=4, kind="list",
  src_q="What needs me?",
  q=T("What needs me?", "Что сейчас на мне?"),
  scope=dict(population="His Needs you.", period="At T.", definition="The tray read as him, in the tray's order."),
  answer=T("Nine lines in the tray's order, the hand-over first ({w15_lines}).",
           "Девять строк в порядке «Ждёт вас», первая — клиент, который ждёт сотрудника ({w15_lines})."),
  list_rule="The lines of slot 4's Needs you at T, in the tray's order.",
  members=[T("The hand-over at Bonny Oaks", "Клиент на Инженерном, который ждёт сотрудника"),
           T("Two cards due today", "Две задачи со сроком сегодня"),
           T("Angie Holloway's two requests to come off her shifts",
             "Две заявки Светланы Юрьевны Демидовой — снять её со смен"),
           T("The two team notes that wait for a decision", "Две заметки команды, которые ждут решения"),
           T("The correction to the page “Timing belt”", "Правка к странице «Ремень ГРМ»"),
           T("The quiet card", "Задача, которая затихла")],
  member_slot="w15_lines",
  computed=[C("w15_lines", "the lines of his Needs you at T",
              "the tray read as slot 4; the two due-today lines exist when T's date is the Friday of W0",
              "core", ["work.work_item", "workforce.shift_change_request", "platform.proposal",
                       "platform.notification_queue"],
              design=D("Needs you 9, in the tray's order: the hand-over at `east`; two cards due today; requests R50 "
                       "and R51; the two team notes; the knowledge correction; the quiet card"))],
  proof=[("core", "the tray read as him")], sources=["core", "memory", "knowledge_base"])

Q("WD.16", file=F, ref="W16", asker=4, kind="nothing",
  src_q="Is any card of mine overdue?",
  q=T("Is any card of mine overdue?", "У меня есть просроченные задачи?"),
  scope=dict(population="His open cards.", period="At T.", definition="A card past its due time."),
  answer=T("None.", "Нет."),
  nothing=T("None is overdue; two are due today, when T's date is the Friday of this week, and one has gone quiet.",
            "Просроченных нет; у двух срок сегодня, если сегодня пятница, и одна затихла."),
  keys=["board.open_at_t"],
  proof=[("core", "work.work_item, platform.activity")], sources=["core"])

Q("WD.17", file=F, ref="W17", asker=16, kind="value",
  src_q="Who covered Austin's shift?",
  q=T("Who covered Austin's shift?", "Кто вышел вместо Антона?"),
  scope=dict(population="Shifts and punches at east.", period="The no-show day.",
             definition="Who worked in place of slot 20."),
  answer=T("Jordan Akins, on a shift of his own published that morning, {p20_no_show_day}; Austin Crabtree's shift "
           "has no punch.",
           "Марат Аюпов — на собственной смене, опубликованной в то же утро, {p20_no_show_day}; по смене Антона "
           "Блинова отметок нет."),
  computed=[C("p20_no_show_day", "the day of slot 20's no-show", "en: east's 2nd full open day before T; ru: slot 20's last working day on or before it",
              "core", ["platform.event", "workforce.shift"], day("2026-11-11"))],
  keys=["s14.instances"],
  proof=[("core", "workforce.shift, punch, platform.event")], sources=["core"])
