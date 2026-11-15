# Story cards S09 to S12 (stories/S09.md .. S12.md).
from dsl import C, Q, T, day
from stories_a import PRICE_RISE

F = "stories/S%02d.md"

# ----------------------------------------------------------------------------------------------- S09
Q("S09.1", file=F % 9, ref="S9.1", story="S09", asker=2, kind="explanation", small=True,
  src_q="Why does Dale miss the Monday meeting? (old: why does the manager at `west` miss the Monday meeting)",
  q=T("Why does Dale miss the Monday meeting?", "Почему Ринат пропускает планёрку по понедельникам?"),
  scope=dict(population="The series, its occurrences, his answers; the shops' hours and zones.",
             period="From the first Monday on or after G to T.", definition="The start in his shop's own time."),
  answer=T("It starts at 05:45 his time, an hour and three quarters before his shop opens; the one week it was at "
           "10:00 Chattanooga time he came.",
           "Планёрка начинается в 07:15 по казанскому времени, за час сорок пять до открытия его сервиса; в ту "
           "неделю, когда её перенесли на 10:00 по ульяновскому времени, он пришёл."),
  facts=[T("It starts at 05:45 his time, an hour and three quarters before his shop opens.",
           "Планёрка начинается в 07:15 по казанскому времени, за час сорок пять до открытия его сервиса."),
         T("The one week it was moved to 10:00 Chattanooga time, {s9_moved_day}, he accepted and came.",
           "В ту единственную неделю, когда её перенесли на 10:00 по ульяновскому времени, {s9_moved_day}, он "
           "принял приглашение и пришёл.")],
  computed=[C("s9_moved_day", "the Monday the meeting was moved to 10:00 home time",
              "the series exception of kind replace; anchor: the Monday of week T-5",
              "core", ["work.event_series_exception", "work.calendar_event"], day("2026-10-05"))],
  keys=["s9.meeting", "s9.pattern", "site.hours.weekday", "geo.zone_gap_hours"],
  proof=[("core", "work.calendar_event, calendar_event_participant, core.location")], sources=["core"])

Q("S09.2", file=F % 9, ref="S9.2", story="S09", asker=2, kind="value", small=True, depends_on="S09.1",
  src_q="How often was he there?",
  q=T("How often was he there?", "Сколько раз он на ней был?"),
  scope=dict(population="Occurrences that were held (not cancelled).",
             period="From the first Monday on or after G up to T.", definition="attended for slot 22."),
  answer=T("{s9_attended} of the {s9_held} meetings that were held.",
           "На {s9_attended} из {s9_held} состоявшихся."),
  computed=[C("s9_attended", "occurrences slot 22 attended",
              "count of held occurrences up to T with attended true for slot 22; his answers follow the cycle of "
              "ledger row s9.pattern",
              "core", ["work.calendar_event_participant"], {"en": ("6", "came 6"), "ru": ("7", "came 7")}),
            C("s9_held", "occurrences held", "count of occurrences up to T that were not cancelled",
              "core", ["work.calendar_event", "work.event_series_exception"],
              {"en": ("22", "held 22"), "ru": ("24", "held 24")})],
  keys=["s9.pattern"],
  proof=[("core", "calendar_event_participant.attended")], sources=["core"])

Q("S09.3", file=F % 9, ref="S9.3", story="S09", asker=2, kind="action", small=True, depends_on="S09.1",
  src_q="Find a time that works for all three shops.",
  q=T("Find a time that works for all three shops.", "Найдите время, которое подойдёт всем трём сервисам."),
  scope=dict(population="A weekly slot of 30 minutes.", period="Weekly, from the next week.",
             definition="Scored by a test, not against one slot."),
  answer=T("A weekly half-hour slot that passes the test; for example Monday at half past ten, Chattanooga time.",
           "Еженедельное получасовое окно, которое проходит проверку; например, понедельник, полдень по "
           "ульяновскому времени."),
  action=dict(proposes=T("A weekly half-hour slot for the managers' meeting.",
                         "Еженедельное получасовое окно для планёрки руководителей."),
              passes_if=T("Any slot passes that is inside the opening hours of both zones, outside East Main's "
                          "morning block, and on a weekday when all six people are rostered and free. Nothing is "
                          "moved before the asker confirms.",
                          "Подходит любое время, которое попадает в часы работы в обоих часовых поясах, не "
                          "приходится на утренние часы Московского шоссе и выпадает на будний день, когда все "
                          "шестеро в смене и свободны. Пока спрашивающий не подтвердил, ничего не переносится.")),
  keys=["site.hours.weekday", "site.morning_block", "geo.zone_gap_hours"],
  proof=[("core", "find_free_slot; shifts; hours")], sources=["core"])

Q("S09.4", file=F % 9, ref="S9.4", story="S09", asker=2, kind="nothing", small=True,
  src_q="Has anyone raised the Monday meeting time as a problem?",
  q=T("Has anyone raised the Monday meeting time as a problem?",
      "Кто-нибудь поднимал вопрос о времени понедельничной планёрки?"),
  scope=dict(population="Cards, comments and team notes.", period="Since G.",
             definition="Any mention of the meeting's time."),
  answer=T("Nothing.", "Никто."),
  nothing=T("No card, comment or team note mentions it.",
            "Об этом нет ни задачи, ни комментария, ни заметки команды."),
  proof=[("core", "work.work_item, platform.activity"), ("memory", "platform.memory")], sources=["core", "memory"])

# ----------------------------------------------------------------------------------------------- S10
Q("S10.1", file=F % 10, ref="S10.1", story="S10", asker=2, kind="smoke", small=True,
  src_q="Did all my reports run last week?",
  q=T("Did all my reports run last week?", "На прошлой неделе все мои отчёты отработали?"),
  scope=dict(population="Runs of her four tasks.", period="Week W-1, Monday to Sunday.",
             definition="A run's status at its scheduled time."),
  answer=T("All but Monday's “Company accounts this week”: it failed at its scheduled time because the shop system "
           "could not be reached, and ran again 65 minutes later.",
           "Все, кроме отчёта «Корпоративные клиенты за неделю» в понедельник: в назначенное время он не выполнился, "
           "потому что учётная программа была недоступна, и через 65 минут его запустили снова."),
  facts=[T("All ran but one.", "Отработали все, кроме одного."),
         T("Monday's “Company accounts this week” failed at its scheduled time: the shop system could not be "
           "reached.",
           "В понедельник отчёт «Корпоративные клиенты за неделю» не выполнился в назначенное время: учётная "
           "программа была недоступна."),
         T("It ran again 65 minutes later and succeeded.", "Через 65 минут его запустили снова, и он выполнился.")],
  keys=["s10.failure", "s10.tasks"],
  proof=[("account_store", "auth.db cron_runs")], sources=["account_store"])

Q("S10.2", file=F % 10, ref="S10.2", story="S10", asker=1, kind="list", small=True,
  src_q="What did my brief say this morning? (old: what did the founder's brief say this morning)",
  q=T("What did my brief say this morning?", "Что было в утренней сводке"),
  scope=dict(population="His first finished brief of T's date (06:40 home time: he has no shifts).", period="T's date.",
             definition="The brief's points."),
  answer=T("Its three points ({founder_brief_points}); each number in them agrees with the stores.",
           "Три её пункта ({founder_brief_points}); каждая цифра в них сходится с данными."),
  list_rule="The three points of slot 1's brief of T's date, as the seeder wrote them for the build.",
  member_slot="founder_brief_points",
  computed=[C("founder_brief_points", "the three points of the founder's brief of T's date",
              "the answer of his finished brief run of T's date; each number is computed by the seeder for the "
              "build", "account_store", ["cron_runs"])],
  keys=["sched.brief_times"],
  proof=[("account_store", "his brief run")], sources=["account_store"])

Q("S10.3", file=F % 10, ref="S10.3", story="S10", asker=2, kind="list", small=True,
  src_q="Which scheduled reports do I have? (old: which reports does the company run, and whose are they)",
  q=T("Which scheduled reports do I have?", "Какие отчёты у меня стоят по расписанию?"),
  scope=dict(population="Her own tasks.", period="At T.", definition="A person reads only their own."),
  answer=T("Her four, with their schedules. The company's full list is on the console, which the assistant cannot "
           "read.",
           "Четыре её отчёта с расписанием. Полный список по компании есть только в консоли, а консоль помощнику "
           "недоступна."),
  list_rule="The scheduled tasks owned by slot 2, each with its schedule in home time.",
  members=[T("Company accounts this week: Mondays at 08:00", "«Корпоративные клиенты за неделю»: по понедельникам "
             "в 09:00"),
           T("Discounts over 10 %: Fridays at 16:00", "«Скидки больше 10 %»: по пятницам в 18:00"),
           T("Charlotte Pike against plan: Mondays at 09:00", "«Казань: план и факт»: по понедельникам в 10:00"),
           T("Missed calls today: daily at 18:00", "«Пропущенные звонки за день»: каждый день в 20:15")],
  facts=[T("The company's full list is on the console, which the assistant cannot read.",
           "Полный список по компании — в консоли; помощнику она недоступна.")],
  keys=["s10.tasks"],
  proof=[("account_store", "auth.db cron_prompt_jobs by owner")], sources=["account_store"])

Q("S10.4", file=F % 10, ref="S10.4", story="S10", asker=6, kind="refusal", small=True,
  src_q="What are the founder's reports?",
  q=T("What are the founder's reports?", "Какие отчёты получает Николай Петрович?"),
  scope=dict(population="Another person's tasks.", period="At T.",
             definition="Task reads are scoped to the caller."),
  answer=T("Refused: she can see only her own, “My call backs”.",
           "Отказ: ей видны только её собственные — «Мои перезвоны»."),
  refusal=dict(by="owner",
               reason=T("A person reads only their own scheduled tasks.",
                        "Задачи по расписанию каждый видит только свои."),
               may_offer=T("Her own task, “My call backs”.", "Её собственный отчёт «Мои перезвоны».")),
  keys=["s10.tasks"],
  proof=[("account_store", "task reads are scoped to the caller")], sources=["account_store"])

# ----------------------------------------------------------------------------------------------- S11
SEASONS = C("s11_seasons_counted", "the past seasons that lie whole inside the ERP history",
            "seasons by season.threshold between T-24 months and T; a season cut by the start of the history is "
            "named as partial and left out", "erp", ["repair_order", "order_job"])

Q("S11.1", file=F % 11, ref="S11.1", story="S11", asker=2, kind="explanation", small=False,
  src_q="When is our busiest time, and with what work?",
  q=T("When is our busiest time, and with what work?", "Когда у нас самое загруженное время и на каких работах?"),
  scope=dict(population="Orders and jobs by month (en) or week (ru).",
             period="The seasons that lie whole inside the history.",
             definition="Season as defined in ledger row season.threshold."),
  answer=T("Air conditioning, May to August, 2.5 times its usual level at the peak; all orders together move under "
           "[[=ceil((max(L('season.total'))-1)*100)|pct]].",
           "Два шинных сезона, с 13 апреля по 10 мая и с 13 октября по 9 ноября: сезонных шинных работ в "
           "[[season.tyre.factor|num]] раз больше обычного, нарядов в день — в "
           "[[season.tyre.orders_in_window|num]] раза."),
  facts=[T("Air conditioning, May to August: every month above 1.5 times the yearly monthly mean.",
           "Два шинных сезона: с 13 апреля по 10 мая и с 13 октября по 9 ноября."),
         T("At the peak, in June and July, 2.5 times.",
           "Сезонных шинных работ в эти недели в [[season.tyre.factor|num]] раз больше среднего за год."),
         T("All orders together move under [[=ceil((max(L('season.total'))-1)*100)|pct]] in any month.",
           "Нарядов в день в сезон в [[season.tyre.orders_in_window|num]] раза больше обычного."),
         T("Says which past seasons it counted: {s11_seasons_counted}.",
           "Называет, какие прошедшие сезоны посчитаны: {s11_seasons_counted}.")],
  computed=[SEASONS], keys=["season.name", "season.threshold", "season.ac_curve", "season.tyre.windows"],
  proof=[("erp", "repair_order, order_job by week and category")], sources=["erp"])

Q("S11.2", file=F % 11, ref="S11.2", story="S11", asker=2, kind="explanation", small=False,
  src_q="How did the last season go?",
  q=T("How did the last season go?", "Как прошёл последний сезон?"),
  scope=dict(population="The last season that lies whole inside the product period (none is a valid answer).",
             period="The season against the eight weeks before it.",
             definition="Calls a day, missed share, extra shifts."),
  answer=T("Names the last season that lies whole inside the product period ({s11_last_season}) or says there is "
           "none; for the demo's nominal T there is none, as this year's season began before go-live and the eight "
           "weeks before it hold no calls. When there is one: air-conditioning jobs at their peak, orders "
           "[[=round((L('season.total')[6]-1)*100)|int]] to [[=round((L('season.total')[5]-1)*100)|pct]] up, missed "
           "calls no higher than before.",
           "За {s11_last_season}: звонков в день больше примерно на [[season.tyre.calls_up_pct|pct0]], доля "
           "пропущенных примерно на четверть выше в любое время дня, у двоих появился шестой рабочий день."),
  facts=[T("Names the season it speaks of: {s11_last_season}; if none lies whole inside the product period, it "
           "says so.",
           "Называет сезон, о котором говорит: {s11_last_season}; если целиком в период работы системы не попал ни "
           "один, так и отвечает."),
         T("Air-conditioning jobs were at their peak.",
           "Звонков в день стало больше примерно на [[season.tyre.calls_up_pct|pct0]]."),
         T("Orders were [[=round((L('season.total')[6]-1)*100)|int]] to "
           "[[=round((L('season.total')[5]-1)*100)|pct]] up.",
           "Доля пропущенных звонков выросла примерно на четверть в любое время дня."),
         T("Missed calls were no higher than before.", "У двух человек появился шестой рабочий день в неделю.")],
  computed=[C("s11_last_season", "the last season that lies whole inside the product period, or none",
              "the latest season by season.threshold with both ends between G and T, and whose eight weeks before "
              "lie after G (en)", "erp", ["repair_order", "order_job"],
              design=("stories/S11.md", "en: for T = Fri 2026-11-13, none: the 2026 season began before go-live"))],
  keys=["season.name", "calls.season_miss_factor", "season.extra_shifts", "season.total"],
  proof=[("core", "calls; shifts"), ("erp", "orders")], sources=["core", "erp"])

Q("S11.3", file=F % 11, ref="S11.3", story="S11", asker=4, kind="value", small=False,
  src_q="When should the seasonal hire start this year?",
  q=T("When should the seasonal hire start this year?", "С какого числа брать сезонного шиномонтажника в следующем сезоне?"),
  scope=dict(population="Seasonal jobs by month (en) or week (ru); the hire's past start dates.",
             period="Each whole past season.",
             definition="The first month (en) or week (ru) in which the seasonal jobs passed the threshold."),
  answer=T("A month earlier than before: the season starts in May, and he started in June ({s11_hire_starts}).",
           "С первого понедельника апреля и с первого понедельника октября, как и в прошлые годы, — за "
           "неделю-полторы до окна: окна открываются 13 апреля и 13 октября ({s11_hire_starts})."),
  computed=[C("s11_hire_starts", "the hire's past start dates", "hired dates of slot F4 per season",
              "erp", ["employee"])],
  keys=["season.hire", "season.name", "season.tyre.windows", "season.threshold"],
  proof=[("erp", "order_job, employee")], sources=["erp"])

# ----------------------------------------------------------------------------------------------- S12
Q("S12.1", file=F % 12, ref="S12.1", story="S12", asker=6, kind="value", small=True,
  src_q="What do we charge for a timing belt on a 2011 Subaru Outback? (old: what do we charge for a timing belt on "
        "this car)",
  q=T("What do we charge for a timing belt on a 2011 Subaru Outback?",
      "Сколько у нас стоит замена ремня ГРМ на Renault Logan 2015 года?"),
  scope=dict(population="The current price list.", period="At T.",
             definition=T("Class car, standard parts, before sales tax.",
                          "Class car, standard parts, as listed, VAT inside.")),
  answer=T("[[s8.price_now|money]] before tax, from the price list in force since {price_rise_day}. The service "
           "page “Timing belt” is stale: it still says [[s8.price_quoted|money]].",
           "[[s8.price_now|money]], по прайс-листу, который действует с {price_rise_day}. Страница услуги "
           "«Ремень ГРМ» устарела: на ней до сих пор [[s8.price_quoted|money]]."),
  must_not=[T("Answering [[s8.price_quoted|money]], the stale page's figure.",
              "Отвечать [[s8.price_quoted|money]] — цифрой с устаревшей страницы.")],
  computed=[PRICE_RISE], pages=["prices/price-list.md", "services/engine/timing-belt.md"],
  seed_files=["named_customers.json"],
  proof=[("knowledge_base", "price list; service page")], sources=["knowledge_base"])

Q("S12.2", file=F % 12, ref="S12.2", story="S12", asker=5, kind="list", small=True,
  src_q="Which pages still show the old prices?",
  q=T("Which pages still show the old prices?", "на каких страницах ещё остались старые цены"),
  scope=dict(population="Pages whose text uses the hour from before P.", period="At T.",
             definition="A page that only mentions the old hour as history does not count."),
  answer=T("Two: “Timing belt” and “Brake questions”.", "На двух: «Ремень ГРМ» и «Вопросы по тормозам»."),
  list_rule="Pages whose text prices work at the labour hour from before P.",
  members=[T("Timing belt", "«Ремень ГРМ»"), T("Brake questions", "«Вопросы по тормозам»")],
  keys=["s12.pages"], pages=["services/engine/timing-belt.md", "services/brakes/brake-questions.md"],
  proof=[("knowledge_base", "the two pages")], sources=["knowledge_base"])

Q("S12.3", file=F % 12, ref="S12.3", story="S12", asker=6, kind="value", small=True,
  src_q="What is our warranty?",
  q=T("What is our warranty?", "Какая у нас гарантия?"),
  scope=dict(population="The current warranty page.", period="At T.", definition="The terms in force."),
  answer=T("24 months or 24,000 miles on parts and labour. The old warranty page is out of date and still claims 12 "
           "months or 12,000 miles.",
           "30 дней на слесарные и электротехнические работы. Старая страница «Гарантийные обязательства» устарела "
           "и до сих пор обещает 14 дней на любые работы."),
  must_not=[T("Giving the old page's term as the warranty.", "Называть гарантией срок со старой страницы.")],
  keys=["s12.warranty"], pages=["customers/warranty.md", "customers/warranty-policy.md"],
  proof=[("knowledge_base", "the current and the old warranty page")], sources=["knowledge_base"])

Q("S12.4", file=F % 12, ref="S12.4", story="S12", asker=4, kind="smoke", small=True,
  src_q="What is waiting to be approved in the knowledge base?",
  q=T("What is waiting to be approved in the knowledge base?", "Что в базе знаний ждёт утверждения?"),
  scope=dict(population="Proposals waiting.", period="At T.", definition="Knowledge proposals not yet decided."),
  answer=T("One: Travis Burnette's correction to “Timing belt”.",
           "Одно предложение: правка Дмитрия Григорьева к странице «Ремень ГРМ»."),
  facts=[T("One proposal waits: Travis Burnette's correction to the page “Timing belt”.",
           "Ждёт одно предложение: правка Дмитрия Григорьева к странице «Ремень ГРМ».")],
  keys=["s12.proposal"], pages=["services/engine/timing-belt.md"],
  proof=[("knowledge_base", "the proposal"), ("core", "platform.notification_queue knowledge.proposed")],
  sources=["knowledge_base", "core"])

Q("S12.5", file=F % 12, ref="S12.5", story="S12", asker=6, kind="refusal", small=True,
  src_q="What does the \"Pay and till\" page say?",
  q=T("What does the “Pay and till” page say?", "Что написано на странице «Оплата труда и касса»?"),
  scope=dict(population="A page for senior readers.", period="At T.", definition="Page rank."),
  answer=T("Refused by rank: she cannot open it, and the answer does not quote it.",
           "Отказ по уровню доступа: открыть её она не может, и ответ её не цитирует."),
  refusal=dict(by="rank",
               reason=T("The page is for senior readers.",
                        "Страница открыта с уровня «Старший менеджер».")),
  must_not=[T("Quoting the page.", "Цитировать страницу.")],
  keys=["s12.pages"], pages=["management/pay-and-till.md"],
  proof=[("knowledge_base", "page rank")], sources=["knowledge_base"])
