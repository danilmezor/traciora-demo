# Story cards S01 to S04 (stories/S01.md .. S04.md).
from dsl import C, Q, T, day

F = "stories/S%02d.md"

# ----------------------------------------------------------------------------------------------- S01
A5_LAST = C("a5_last_visit", "the date of Cumberland Bend Electric's (A5) last order",
            "max(opened_at) over A5's orders; the card's anchor is the Thursday of week T-20",
            "erp", ["repair_order", "customer"], day("2026-06-25"))
A5_COMEBACKS = [
    C("a5_comeback_1", "the day A5's first comeback order was opened, with its order number",
      "the first of A5's warranty or goodwill orders that point at a first order; anchor: the Tuesday of week T-26",
      "erp", ["repair_order"], {"en": ("2026-05-12", "2026-05-12, 2026-06-09"), "ru": ("2026-05-12", "2026-05-12, 2026-06-09")}),
    C("a5_comeback_2", "the day A5's second comeback order was opened, with its order number",
      "the second such order; anchor: the Tuesday of week T-22",
      "erp", ["repair_order"], {"en": ("2026-06-09", "2026-05-12, 2026-06-09"), "ru": ("2026-06-09", "2026-05-12, 2026-06-09")}),
]
A5_CALL = C("a5_complaint_call", "the day of the complaint call (call 17)",
            "the answered inbound call from the caller's number, tagged complaint; anchor: the Tuesday of week T-19",
            "core", ["interactions.interaction", "interaction_analysis"], day("2026-06-30"))
A5_MISSES = C("a5_miss_dates", "the dates of the three unanswered calls (calls 18 to 20)",
              "missed_call rows in state waiting joined by phone('<number>') to A5's contact; 1, 6 and 9 calendar days "
              "after the complaint call",
              "core", ["missed_call", "call_leg"],
              {"en": ("2026-07-01, 2026-07-06, 2026-07-09", "2026-07-01, 2026-07-06, 2026-07-09"),
               "ru": ("2026-07-01, 2026-07-06, 2026-07-09", "2026-07-01, 2026-07-06, 2026-07-09")})
PRICE_RISE = C("price_rise_day", "P, the day of the last price rise",
               "the first Monday on or after T-150 calendar days; the price list's \"In force from\" date",
               "knowledge_base", ["prices/price-list.md"], day("2026-06-22"))
A1_UNPAID = C("a1_unpaid_bills", "Nickajack Delivery's (A1) bills unpaid at T, each with its age in days",
              "statement rows of A1 with no payment at T; age = T minus the issue date; overdue once past 30 days",
              "erp", ["statement", "payment"])

Q("S01.1", file=F % 1, ref="S1.1", story="S01", asker=2, kind="list", small=True,
  src_q="Which of our company accounts have we lost or are losing?",
  q=T("Which of our company accounts have we lost or are losing?",
      "Кто из корпоративных у нас отвалился, а кого теряем сейчас?"),
  scope=dict(population="The six customers billed on terms.",
             period="Orders by 30-day block over the last 180 days.",
             definition="Lost: no order in the last 90 days. Losing: orders in the last 30 days under half of a block "
                        "before T-150 d."),
  answer=T("Cumberland Bend Electric is lost: no order in the last 90 days, last visit on {a5_last_visit}. Sourwood "
           "Catering is being lost: [[acct.A6.visits[0]|int]] orders a 30-day block before, [[acct.A6.visits[5]|int]] "
           "in the last 30 days. Nobody else.",
           "Потерян «Идель-Электромонтаж»: за последние 90 дней ни одного заезда, последний был {a5_last_visit}. "
           "Теряем «Вкусный выезд»: раньше [[acct.A6.visits[0]|int]] заездов за 30 дней, за последние 30 дней — "
           "[[acct.A6.visits[5]|int]]. Больше никого."),
  list_rule="Accounts billed on terms (A1 to A6) that are lost or losing by the definition; each with its state.",
  members=[T("Cumberland Bend Electric: lost", "«Идель-Электромонтаж»: потерян"),
           T("Sourwood Catering Co.: losing", "«Вкусный выезд»: теряем")],
  computed=[A5_LAST], keys=["acct.A5.visits", "time.people_window_days", "time.score_period_days"],
  proof=[("erp", "repair_order by customer")], sources=["erp"])

Q("S01.2", file=F % 1, ref="S1.2", story="S01", asker=2, kind="explanation", small=True,
  src_q="Why did Cumberland Bend Electric stop coming?",
  q=T("Why did Cumberland Bend Electric stop coming?",
      "Почему «Идель-Электромонтаж» перестал к нам ездить?"),
  scope=dict(population="A5.", period="The whole history.", definition="All stores."),
  answer=T("Two brake comebacks at Charlotte Pike, a disputed and unpaid bill, a complaint call whose promised call "
           "back was never made, three more calls nobody answered or returned; no order since.",
           "Два возврата по тормозам на Технической, оспоренный и неоплаченный счёт, звонок с претензией, после "
           "которого обещали перезвонить и не перезвонили, ещё три звонка, на которые никто не ответил; с тех пор ни "
           "одного наряда."),
  facts=[T("Two brake comebacks at Charlotte Pike: pad jobs on its vans came back, in the orders opened on "
           "{a5_comeback_1} and on {a5_comeback_2}.",
           "Два возврата по тормозам на Технической: колодки на их фургонах пришлось переделывать — наряды, открытые "
           "{a5_comeback_1} и {a5_comeback_2}."),
         T("The bill that holds the second comeback's first order is disputed and unpaid.",
           "Счёт по наряду, с которого начался второй возврат, оспорен и не оплачен."),
         T("On {a5_complaint_call} its manager, Wade Carlisle, rang to complain; Dale Hutchins promised a call back "
           "and did not make it.",
           "{a5_complaint_call} с претензией звонил их руководитель, Рустем Ильгизович Фаттахов; Ринат Фаридович "
           "Галиев пообещал перезвонить и не перезвонил."),
         T("He rang [[s1.a5.misses|int]] more times in the [[s1.a5.miss_span_days|int]] days after; nobody answered "
           "and nobody called back.",
           "За следующие [[s1.a5.miss_span_days|int]] дней он звонил ещё [[s1.a5.misses|int]] раза: трубку не взяли и "
           "не перезвонили."),
         T("There has been no order since.", "С тех пор от них нет ни одного наряда.")],
  computed=A5_COMEBACKS + [A5_CALL],
  proof=[("erp", "comeback orders (repair_order), statement"), ("core", "call 17; missed_call by the caller's number")],
  sources=["erp", "core"])

Q("S01.3", file=F % 1, ref="S1.3", story="S01", asker=4, kind="action", small=True,
  src_q="What should we do about Sourwood Catering?",
  q=T("What should we do about Sourwood Catering?", "Что делать с «Вкусным выездом»?"),
  scope=dict(population="A6.", period="The last 180 days.", definition="All stores."),
  answer=T("Names why the account is fading, then proposes that a named person call the new contact and offers to "
           "raise the task.",
           "Называет, почему клиент уходит, затем предлагает, чтобы названный сотрудник позвонил новому "
           "ответственному, и предлагает поставить на это задачу."),
  facts=[T("Visits fell from [[acct.A6.visits[0]|int]] in a 30-day block to [[acct.A6.visits[5]|int]].",
           "Заезды упали с [[acct.A6.visits[0]|int]] за 30 дней до [[acct.A6.visits[5]|int]]."),
         T("A new contact, Erin Castillo, since {price_rise_day}.",
           "С {price_rise_day} у них новый ответственный — Дарья Олеговна Вершинина."),
         T("Our prices rose on that same day.", "В тот же день у нас выросли цены."),
         T("[[s1.a6.estimates_waited_two_days_or_more|int]] estimates waited two days or more for an answer; "
           "[[s1.a6.estimates_declined_or_expired|int]] of them were then declined or expired.",
           "[[s1.a6.estimates_waited_two_days_or_more|int]] смет ждали ответа по два дня и дольше; "
           "[[s1.a6.estimates_declined_or_expired|int]] из них потом были отклонены или истекли."),
         T("A quote Caleb Sutton promised on the phone was sent two days late.",
           "Смету, которую Никита Ведяшкин пообещал по телефону, отправили на два дня позже."),
         T("A quote request in the website chat waited [[s1.a6.quote_chat_waited_days|int]] days for a person's "
           "first reply.",
           "Запрос сметы в чате на сайте [[s1.a6.quote_chat_waited_days|int]] дня ждал первого ответа сотрудника.")],
  action=dict(proposes=T("A call to the new contact by a named person, and an offer to raise the task as a decision "
                         "card.",
                         "Звонок новому ответственному от названного по имени сотрудника и предложение поставить на "
                         "это задачу — карточкой, которую нужно подтвердить."),
              passes_if=T("Nothing is written before the asker confirms the card.",
                          "Пока спрашивающий не подтвердил карточку, ничего не создаётся.")),
  computed=[PRICE_RISE],
  proof=[("erp", "estimates and order_status_history"), ("core", "calls 21, 22"), ("conversations", "the web chat")],
  sources=["erp", "core", "conversations"])

Q("S01.4", file=F % 1, ref="S1.4", story="S01", asker=2, kind="explanation", small=True,
  src_q="Is anything wrong with Nickajack Delivery?",
  q=T("Is anything wrong with Nickajack Delivery?", "С «Симбирским гонцом» у нас всё в порядке?"),
  scope=dict(population="A1.", period="The last 180 days.",
             definition="Orders by block; days from a bill's date to its payment, paid bills only; unpaid bills at T."),
  tolerance="3 days on days to pay",
  answer=T("Visits are steady at [[acct.A1.visits[5]|int]] a block, but it pays later: about "
           "[[acct.A1.days_to_pay.until|int]] days before, [[acct.A1.days_to_pay.last_three_paid[0]|int]], "
           "[[acct.A1.days_to_pay.last_three_paid[1]|int]] and [[acct.A1.days_to_pay.last_three_paid[2]|int]] days on "
           "the last three paid statements; the newer statements are unpaid.",
           "Ездят как раньше, [[acct.A1.visits[5]|int]] заезда за 30 дней, но платить стали позже: раньше — примерно "
           "за [[acct.A1.days_to_pay.until|int]] дней, по счетам двухмесячной давности — примерно за "
           "[[acct.A1.days_to_pay.late|int]]; более свежие счета не оплачены."),
  facts=[T("Visits are steady: [[acct.A1.visits[5]|int]] orders in every 30-day block.",
           "Заезды ровные: [[acct.A1.visits[5]|int]] наряда в каждые 30 дней."),
         T("Days to pay are up: bills used to be paid in about [[acct.A1.days_to_pay.until|int]] days; the last three "
           "paid statements took [[acct.A1.days_to_pay.last_three_paid[0]|int]], "
           "[[acct.A1.days_to_pay.last_three_paid[1]|int]] and [[acct.A1.days_to_pay.last_three_paid[2]|int]] days.",
           "Срок оплаты вырос: раньше счета оплачивали примерно за [[acct.A1.days_to_pay.until|int]] дней, счета "
           "двухмесячной давности — примерно за [[acct.A1.days_to_pay.late|int]]."),
         T("The bills unpaid at T, each with its age: {a1_unpaid_bills}.",
           "Счета, не оплаченные на сегодня, и сколько дней каждому: {a1_unpaid_bills}.")],
  computed=[A1_UNPAID], keys=["acct.A1.terms_days"],
  proof=[("erp", "statement, payment")], sources=["erp"])

Q("S01.5", file=F % 1, ref="S1.5", story="S01", asker=2, kind="list", small=True,
  src_q="Which company-account contacts called us and were never called back? (old: who has not been called back)",
  q=T("Which company-account contacts called us and were never called back?",
      "Кто из корпоративных клиентов звонил нам, а мы так и не перезвонили?"),
  scope=dict(population="Missed calls from numbers of contacts of A1 to A6, state waiting, with no later answered "
                        "call to or from the number.",
             period="Since G.",
             definition="Not the To call back screen, which shows seven days."),
  answer=T("Wade Carlisle of Cumberland Bend Electric: [[s1.a5.misses|int]] calls, on {a5_miss_dates}. Nobody else.",
           "Рустем Ильгизович Фаттахов из «Идель-Электромонтажа»: [[s1.a5.misses|int]] звонка — {a5_miss_dates}. "
           "Больше никого."),
  list_rule="Contacts of A1 to A6 with a missed call in state waiting since G and no later answered call to or from "
            "the number; each with the dates of the calls.",
  members=[T("Wade Carlisle, Cumberland Bend Electric: [[s1.a5.misses|int]] calls ({a5_miss_dates})",
             "Рустем Ильгизович Фаттахов, «Идель-Электромонтаж»: [[s1.a5.misses|int]] звонка ({a5_miss_dates})")],
  must_not=[T("Answering from the To call back list alone: it shows seven days and holds none of these calls.",
              "Отвечать только по списку «Перезвонить»: он показывает семь дней, и этих звонков в нём нет.")],
  computed=[A5_MISSES], keys=["time.callback_queue_days"],
  proof=[("core", "missed_call joined by phone('<number>')")], sources=["core", "erp"])

Q("S01.6", file=F % 1, ref="S1.6", story="S01", asker=4, kind="cannot tell", small=True,
  src_q="Which advisor missed the calls from Cumberland Bend Electric?",
  q=T("Which advisor missed the calls from Cumberland Bend Electric?",
      "Кто из мастеров пропустил звонки «Идель-Электромонтажа»?"),
  scope=dict(population="The same three misses as S01.5.", period="Since G.", definition="A missed call has no person."),
  answer=T("The data cannot tell: a missed call has no person. It can give the desks each call rang first "
           "([[s1.a5.miss_first_desks[0]|int]], [[s1.a5.miss_first_desks[1]|int]], [[s1.a5.miss_first_desks[2]|int]]) "
           "and who was on shift.",
           "По данным этого не сказать: у пропущенного звонка нет человека. Можно назвать аппараты, на которые "
           "каждый звонок пришёл первым ({a5_miss_desks}), и кто в это время был в смене."),
  cannot=dict(lacks=T("Who missed a call: a missed call carries no person.",
                      "Кто именно пропустил звонок: у пропущенного звонка нет человека."),
              may_give=[T("The desk each call rang first: [[s1.a5.miss_first_desks[0]|int]], "
                          "[[s1.a5.miss_first_desks[1]|int]], [[s1.a5.miss_first_desks[2]|int]].",
                          "Аппараты, на которые звонки пришли первым: {a5_miss_desks}."),
                        T("Who was on shift at those times.", "Кто в это время был в смене.")],
              wrong_if=T("An answer that names a person as having missed them is wrong.",
                         "Ответ, который называет человека, пропустившего эти звонки, неверен.")),
  computed=[C("a5_miss_desks", "ru: the desk each of A5's three missed calls rang first",
              "the first leg's extension of each miss: the desk of the advisor on shift at west that day (302 on slot "
              "23's days, 303 on slot 24's)", "core", ["call_leg", "workforce.shift"],
              design=("ledger.json", "303, 302, 303 for T = Fri 2026-11-13"))],
  keys=["s1.a5"],
  proof=[("core", "call_leg.extension, workforce.shift")], sources=["core"])

Q("S01.7", file=F % 1, ref="S1.7", story="S01", asker=16, kind="nothing", small=True,
  src_q="Which accounts at Bonny Oaks have a bill overdue?",
  q=T("Which accounts at Bonny Oaks have a bill overdue?",
      "У кого из корпоративных клиентов Инженерного есть просроченные счета?"),
  scope=dict(population="Customers billed on terms whose home shop is east (A2, A4).", period="At T.",
             definition="Bills past their terms and unpaid."),
  answer=T("None.", "Ни у кого."),
  nothing=T("Millsaps Heating & Plumbing and Missionary Ridge Driving School, the two accounts whose home shop is "
            "Bonny Oaks, have no bill past its terms and unpaid.",
            "У «Тёплого контура» и автошколы «Первая передача» — двух клиентов Инженерного, работающих по договору, — "
            "нет ни одного счёта, срок оплаты которого прошёл."),
  keys=["acct.others_pay_on_time", "acct.A2.shop", "acct.A4.shop"],
  proof=[("erp", "statement.status")], sources=["erp"])

Q("S01.8", file=F % 1, ref="S1.8", story="S01", asker=6, kind="refusal", small=True,
  src_q="Show me the calls from Cumberland Bend Electric's manager.",
  q=T("Show me the calls from Cumberland Bend Electric's manager.",
      "Покажите звонки руководителя «Идель-Электромонтажа»."),
  scope=dict(population="Core calls.", period="Any.", definition="Her rank is bound to main."),
  answer=T("Refused by site: the calls are at Charlotte Pike, which she cannot read. The answer says so; it does not "
           "say there were none.",
           "Отказ по площадке: эти звонки — на Технической, а её данные ей недоступны. Ответ так и говорит; он не "
           "утверждает, что звонков не было."),
  refusal=dict(by="site",
               reason=T("The calls are at Charlotte Pike; her rank is bound to East Main.",
                        "Звонки относятся к Технической; её доступ ограничен Московским шоссе.")),
  must_not=[T("Saying there were no such calls.", "Говорить, что таких звонков не было.")],
  proof=[("core", "site binding")], sources=["core"], known_failure=True)

# ----------------------------------------------------------------------------------------------- S02
RULE_DAY = C("discount_rule_day", "the day the discount rule came into force",
             "the \"In force from\" date in the text of the page \"Discount policy\": the full open day after F1's "
             "firing (west's 16th full open day after G)",
             "knowledge_base", ["policies/discounts.md"], day("2026-06-16", "2026-06-07"))

Q("S02.1", file=F % 2, ref="S2.1", story="S02", asker=2, kind="explanation", small=False,
  src_q="Were there unusual discounts at `west`, and who gave them?",
  q=T("Were there unusual discounts at Charlotte Pike, and who gave them?",
      "Были ли на Технической необычные скидки и кто их давал?"),
  scope=dict(population="Paid cash orders with a discount of 10 % or more of the bill before tax, by advisor.",
             period="From T-335 d to T.",
             definition="\"Everyone else\" is every other advisor in the company in the same 26 weeks."),
  answer=T("Yes: Brent Lassiter, [[s2.f1.discounted|int]] cash orders at 15 to 30 %, none approved, all in the "
           "[[s2.weeks|int]] weeks to his firing.",
           "Да: Артур Назаров — [[s2.f1.discounted|int]] наличных нарядов со скидкой 15–30 %, ни одна не согласована, "
           "все за [[s2.weeks|int]] недель до его увольнения."),
  facts=[T("Brent Lassiter gave them: [[s2.f1.discounted|int]] paid cash orders with a discount of 15 to 30 %.",
           "Их давал Артур Назаров: [[s2.f1.discounted|int]] оплаченных наличными нарядов со скидкой 15–30 %."),
         T("None of them was approved.", "Ни одна из этих скидок не согласована."),
         T("All fall in the [[s2.weeks|int]] weeks to his firing.",
           "Все они приходятся на [[s2.weeks|int]] недель до его увольнения."),
         T("At full size that is [[s2.f1.discount_share|pct0]] of his cash orders against "
           "[[pay.background_discount_share|pct]] for every other advisor in the company.",
           "В полном объёме данных это [[s2.f1.discount_share|pct0]] его наличных нарядов против "
           "[[pay.background_discount_share|pct]] у всех остальных мастеров-приёмщиков компании."),
         T("He also voided [[s2.f1.second.count|int]] orders after cash was taken, against one or two for any other "
           "advisor.", None)],
  proof=[("erp", "repair_order by advisor")], sources=["erp"])

Q("S02.2", file=F % 2, ref="S2.2", story="S02", asker=2, kind="value", small=True, depends_on="S02.1",
  src_q="What did it cost?",
  q=T("What did it cost?", "Во что это обошлось?"),
  scope=dict(population="F1's orders and closes.", period="The 26 weeks to his firing.",
             definition=T("Three components: unapproved discounts; orders voided after cash was taken; days the till "
                          "was short when he closed it.",
                          "Three components: unapproved discounts; parts issued from stock under his name with no "
                          "sale; orders with mechanics' clocked time above the hours sold.")),
  answer=T("An estimate of [[s2.total|money]]: [[s2.f1.discount_total|money]] in unapproved discounts on "
           "[[s2.f1.discounted|int]] orders, [[s2.f1.second.total|money]] on [[s2.f1.second.count|int]] orders voided "
           "after cash was taken, and [[s2.f1.third.total|money]] short in the till on [[s2.f1.third.count|int]] of "
           "the [[s2.f1.third.of_days_he_closed|int]] days he closed it; each by month ({s2_by_month}). It is an "
           "estimate: the true loss is not in the data.",
           "Оценка — [[s2.total|money]]: [[s2.f1.discount_total|money]] несогласованных скидок по "
           "[[s2.f1.discounted|int]] нарядам, [[s2.f1.second.total|money]] — себестоимость запчастей по "
           "[[s2.f1.second.count|int]] выдачам со склада без продажи и [[s2.f1.third.total|money]] — "
           "[[s2.f1.third.hours|int]] час работы механиков сверх проданного по [[s2.f1.third.count|int]] нарядам; "
           "каждая часть — по месяцам ({s2_by_month}). Это оценка: настоящей потери в данных нет."),
  computed=[C("s2_by_month", "the three components by calendar month",
              "sum of each component's money by the month of the order, the close or the stock movement",
              "erp", ["repair_order", "payment", "cash_drawer_close", "stock_movement", "time_entry", "order_labor"])],
  proof=[("erp", "repair_order, cash_drawer_close (en); stock_movement, time_entry, order_labor (ru)")],
  sources=["erp"])

Q("S02.3", file=F % 2, ref="S2.3", story="S02", asker=2, kind="explanation", small=True, depends_on="S02.2",
  src_q="Did it stop?",
  q=T("Did it stop?", "Это прекратилось?"),
  scope=dict(population="west's cash orders with a discount of 10 % or more.",
             period="The 26 weeks against the time since the firing.", definition="Share of west's cash orders."),
  answer=T("Yes, the week he left. Since then Charlotte Pike has [[s2.west.discounts_after.orders|int]] such orders, "
           "[[s2.west.discounts_after.approved_by_22|int]] of them approved.",
           "Да, в ту же неделю, когда он ушёл. С тех пор на Технической [[s2.west.discounts_after.orders|int]] таких "
           "наряда, [[s2.west.discounts_after.approved_by_22|int]] из них согласованы."),
  facts=[T("Yes: it stopped the week he left.", "Да: прекратилось в ту же неделю, когда он ушёл."),
         T("Since then Charlotte Pike has [[s2.west.discounts_after.orders|int]] cash orders with a discount of "
           "[[price.discount_rule_pct|pct]] or more; [[s2.west.discounts_after.approved_by_22|int]] were approved.",
           "С тех пор на Технической [[s2.west.discounts_after.orders|int]] наличных наряда со скидкой "
           "[[price.discount_rule_pct|pct]] и больше; [[s2.west.discounts_after.approved_by_22|int]] из них "
           "согласованы."),
         T("At full size: [[s2.west.discount_share_before|pct1]] of Charlotte Pike's cash orders before, "
           "[[s2.west.discount_share_after|pct1]] since.",
           "В полном объёме данных: [[s2.west.discount_share_before|pct1]] наличных нарядов Технической до "
           "увольнения, [[s2.west.discount_share_after|pct1]] — после.")],
  proof=[("erp", "repair_order")], sources=["erp"])

Q("S02.4", file=F % 2, ref="S2.4", story="S02", asker=6, kind="value", small=True,
  src_q="What is our rule on discounts, and since when?",
  q=T("What is our rule on discounts, and since when?", "Какое у нас правило по скидкам и с какого числа?"),
  scope=dict(population="The staff page and the team note.", period="At T.", definition="The rule and its date."),
  answer=T("A discount above [[price.discount_rule_pct|pct]] of the bill before tax needs the approval of the shop's "
           "senior, recorded on the order. In force from {discount_rule_day}, the date in the page text. It is on the "
           "staff page “Discount policy” and in a team note.",
           "Скидку больше [[price.discount_rule_pct|pct]] от всей суммы наряда до скидки согласует руководитель "
           "сервиса, с отметкой в наряде. Действует с {discount_rule_day} — дата стоит в тексте страницы. Правило "
           "записано на странице «Скидки» и в заметке команды."),
  facts=[T("Above [[price.discount_rule_pct|pct]] of the bill before tax a discount needs the approval of the shop's "
           "senior, recorded on the order.",
           "Скидку больше [[price.discount_rule_pct|pct]] от всей суммы наряда до скидки согласует руководитель "
           "сервиса, с отметкой в наряде."),
         T("In force from {discount_rule_day}, the date in the page text (the next full open day after the firing).",
           "Действует с {discount_rule_day}: дата стоит в тексте страницы (следующий полный рабочий день после увольнения)."),
         T("Names the page “Discount policy” and the team note.", "Называет страницу «Скидки» и заметку команды.")],
  computed=[RULE_DAY], pages=["policies/discounts.md"],
  proof=[("knowledge_base", "page \"Discount policy\""), ("memory", "platform.memory, business scope")],
  sources=["knowledge_base", "memory"])

Q("S02.5", file=F % 2, ref="S2.5", story="S02", asker=2, kind="list", small=True,
  src_q="Has anyone broken the discount rule in the last 30 days? (old: does anyone break it today)",
  q=T("Has anyone broken the discount rule in the last 30 days?",
      "За последние 30 дней кто-нибудь нарушал правило по скидкам?"),
  scope=dict(population="Orders of every shop with a discount above 10 % and no approver.",
             period="The last 30 days.", definition="discount_approved_by is empty."),
  answer=T("Chad Binkley at Charlotte Pike, twice: [[s2.west.discounts_after.unapproved_pct_each|pct]] each, no "
           "approval recorded ({s2_unapproved_days}). Nobody else.",
           "Вячеслав Крюков на Технической, дважды: по [[s2.west.discounts_after.unapproved_pct_each|pct]], "
           "согласование не отмечено ({s2_unapproved_days}). Больше никто."),
  list_rule="Orders of the last 30 days, any shop, with a discount above 10 % of the bill before tax and no approver; "
            "by advisor.",
  members=[T("Chad Binkley, Charlotte Pike: [[s2.west.discounts_after.unapproved_by_23|int]] orders, "
             "[[s2.west.discounts_after.unapproved_pct_each|pct]] each, no approver",
             "Вячеслав Крюков, Техническая: [[s2.west.discounts_after.unapproved_by_23|int]] наряда, по "
             "[[s2.west.discounts_after.unapproved_pct_each|pct]], согласующего нет")],
  computed=[C("s2_unapproved_days", "the days of slot 23's two unapproved discounts",
              "closed_at of the two orders; anchors: the Wednesday of week T-3 and the Thursday of week T-1",
              "erp", ["repair_order"])],
  keys=["price.discount_rule_pct"],
  proof=[("erp", "repair_order.discount_approved_by")], sources=["erp"])

Q("S02.6", file=F % 2, ref="S2.6", story="S02", asker=2, kind="cannot tell", small=True,
  src_q="How much did Brent Lassiter actually take?",
  q=T("How much did Brent Lassiter actually take?", "Сколько Назаров взял на самом деле?"),
  scope=dict(population="The same rows as S02.2.", period="The 26 weeks to his firing.",
             definition="What the stores record against what left unrecorded."),
  answer=T("The data cannot tell. It shows three things under his name, [[s2.total|money]] in all as an estimate; "
           "whether each discount was pocketed, and what else left unrecorded, is in no store.",
           "По данным этого не сказать. Видны три вещи под его фамилией, всего на [[s2.total|money]], и это оценка; "
           "забрал ли он себе каждую скидку и что ещё ушло мимо учёта — этого нет ни в одной системе."),
  cannot=dict(lacks=T("Whether each discount was pocketed, and what else left unrecorded.",
                      "Забрал ли он себе каждую скидку и что ещё ушло мимо учёта."),
              may_give=[T("Unapproved discounts: [[s2.f1.discount_total|money]].",
                          "Несогласованные скидки: [[s2.f1.discount_total|money]]."),
                        T("Orders voided after cash was taken: [[s2.f1.second.total|money]].",
                          "Выдачи запчастей со склада без продажи: [[s2.f1.second.total|money]]."),
                        T("Till shortages on days he closed it: [[s2.f1.third.total|money]].",
                          "Работа механиков сверх проданных часов: [[s2.f1.third.total|money]]."),
                        T("Their sum, [[s2.total|money]], stated as an estimate.",
                          "Их сумма, [[s2.total|money]], названная оценкой.")],
              wrong_if=T("An answer that gives one figure as what he took is wrong.",
                         "Ответ, который называет одну сумму как взятую им, неверен.")),
  proof=[("erp", "as S02.2")], sources=["erp"])

Q("S02.7", file=F % 2, ref="S2.7", story="S02", asker=6, kind="refusal", small=True,
  src_q="How short was the Nashville till on the days Brent closed it?",
  q=T("How short was the Nashville till on the days Brent closed it?",
      "Какая была недостача в кассе в Казани в те дни, когда её закрывал Артур Назаров?"),
  scope=dict(population="cash_drawer_close.", period="Any.", definition="Till counts are hidden below middle."),
  answer=T("Refused by rank: she cannot read till counts. No figure is given.",
           "Отказ по уровню доступа: пересчёты кассы ей недоступны. Ни одной суммы в ответе нет."),
  refusal=dict(by="rank",
               reason=T("Till counts are hidden below middle rank.",
                        "Пересчёты кассы скрыты от всех, кто ниже уровня «Менеджер».")),
  must_not=[T("Giving any figure from the till counts.", "Называть любую сумму из пересчётов кассы.")],
  proof=[("erp", "sources.json denied columns")], sources=["erp"])

Q("S02.8", file=F % 2, ref="S2.8", story="S02", asker=3, kind="list", small=True,
  src_q="On which days was `west`'s till short by 20 dollars or more? (ru: which parts left `west`'s stock with no "
        "sale?)",
  q=T("On which days was the Charlotte Pike till short by 20 dollars or more?",
      "Какие запчасти ушли со склада на Технической без продажи?"),
  scope=dict(population=T("cash_drawer_close at west.", "stock_movement issues at west with no order line."),
             period="The last 365 days.",
             definition=T("A difference of -20 or less.", "An issue from stock that no order line carries.")),
  answer=T("The [[s2.f1.third.count|int]] days ({s2_rows}), each closed by Brent Lassiter, "
           "[[s2.f1.third.total|money]] short in all.",
           "[[s2.f1.second.count|int]] выдач ({s2_rows}), все на имя Артура Назарова, на "
           "[[s2.f1.second.total|money]] по себестоимости."),
  list_rule="en: the days of the last 365 at west whose till count is 20 dollars or more under the expected cash, "
            "with who closed. ru: the issues from west's stock in the last 365 days with no order line, with who "
            "issued and the cost.",
  member_slot="s2_rows",
  computed=[C("s2_rows", "en: the 19 short days; ru: the 46 issues with no sale",
              "en: cash_drawer_close rows at west with counted minus expected of -20 or less. ru: stock_movement "
              "issues at west with no order line",
              "erp", ["cash_drawer_close", "stock_movement", "employee"])],
  proof=[("erp", "cash_drawer_close (en); stock_movement (ru)")], sources=["erp"])

# ----------------------------------------------------------------------------------------------- S03
FIX_DAY = C("s3_fix_day", "the day of the fix: the early desk shift and the cover of two",
            "valid_from of the coverage requirement with min_count 2 at main; anchor: the Monday of week T-3",
            "core", ["workforce.coverage_requirement", "workforce.shift_template"], day("2026-10-19"))
Q_MAIN = C("queue_main", "the callers waiting at East Main, oldest first",
           "waiting, undismissed misses of the last 7 days at the sites the asker reads, read as her",
           "core", ["missed_call", "call_leg"])
Q_HER = C("queue_her", "the callers waiting at the sites she reads (East Main, and Bonny Oaks where she is posted "
          "for cover days), oldest first",
          "waiting, undismissed misses of the last 7 days at main and east, read as her (cast.also_sites)",
          "core", ["missed_call", "call_leg"])
Q_ALL = C("queue_all", "the callers waiting at all three shops, oldest first",
          "waiting, undismissed misses of the last 7 days at every site, read as him",
          "core", ["missed_call", "call_leg"])

Q("S03.1", file=F % 3, ref="S3.1", story="S03", asker=4, kind="value", small=True,
  src_q="When do we miss the most calls at the flagship?",
  q=T("When do we miss the most calls at the flagship?",
      "В какие часы на Московском пропускаем больше всего звонков?"),
  scope=dict(population="In-hours inbound calls at main by hour of day and weekday.", period="G to the fix.",
             definition="Calls outside opening hours are left out."),
  tolerance="3 points",
  answer=T("In the morning block, [[site.morning_block[0]|text]] to [[site.morning_block[1]|text]] on weekdays: "
           "[[calls.main.before.miss_morning|pct]] of in-hours calls were missed there until the fix of {s3_fix_day}, "
           "against [[calls.main.before.miss_rest|pct]] in the rest of the day. Not Saturday mornings, and not calls "
           "outside opening hours.",
           "В утренние часы, с [[site.morning_block[0]|text]] до [[site.morning_block[1]|text]]: до {s3_fix_day} там "
           "пропускали [[calls.main.before.miss_morning|pct]] звонков в рабочее время против "
           "[[calls.main.before.miss_rest|pct]] в остальные часы дня. Звонки в нерабочее время сюда не входят."),
  must_not=[T("Giving Saturday mornings or out-of-hours calls as the answer.",
              "Называть ответом звонки в нерабочее время.")],
  computed=[FIX_DAY], keys=["calls.hour_curve", "calls.saturday.main.miss", "calls.out_of_hours_share"],
  proof=[("core", "missed_call, call_leg by hour")], sources=["core"])

Q("S03.2", file=F % 3, ref="S3.2", story="S03", asker=4, kind="explanation", small=False,
  src_q="Did the early shift help?",
  q=T("Did the early shift help?", "Помогло, что оба мастера смены теперь выходят к открытию?"),
  scope=dict(population="The same calls as S03.1.", period="G to the fix against the fix to T, by block.",
             definition=T("Missed share by block; median wait of a missed caller for a call back or to get through.",
                          "The same; where a tyre window overlaps, compared within the same weeks' other hours.")),
  answer=T("Yes: the morning went from [[calls.main.before.miss_morning|pct]] missed to "
           "[[calls.main.since.miss_morning|pct]], and the wait for a call back from "
           "[[calls.callback.main.before.median_min|dur]] to [[calls.callback.main.after.median_min|dur]].",
           "Да: утром пропускали [[calls.main.before.miss_morning|pct]] звонков, теперь "
           "[[calls.main.since.miss_morning|pct]]; перезвона ждали [[calls.callback.main.before.median_min|dur]], "
           "теперь [[calls.callback.main.after.median_min|dur]]."),
  facts=[T("Morning block: [[calls.main.before.miss_morning|pct]] missed before the fix, "
           "[[calls.main.since.miss_morning|pct]] since.",
           "Утренние часы: до перемены пропускали [[calls.main.before.miss_morning|pct]] звонков, после — "
           "[[calls.main.since.miss_morning|pct]]."),
         T("Rest of the day: [[calls.main.before.miss_rest|pct]] before and [[calls.main.since.miss_rest|pct]] "
           "since.",
           "Остальное время дня: [[calls.main.before.miss_rest|pct]] до и [[calls.main.since.miss_rest|pct]] после."),
         T("Median wait for a call back: [[calls.callback.main.before.median_min|dur]] before, "
           "[[calls.callback.main.after.median_min|dur]] since.",
           "Медианное ожидание перезвона: [[calls.callback.main.before.median_min|dur]] до, "
           "[[calls.callback.main.after.median_min|dur]] после."),
         T("Never called back: [[calls.callback.main.before.never_pct|pct]] of missed callers before; "
           "[[calls.callback.main.after.never_named|int]] named callers since ({s3_never_called_back}).",
           "Так и не перезвонили: до перемены — [[calls.callback.main.before.never_pct|pct]] пропущенных, после — "
           "[[calls.callback.main.after.never_named|int]] конкретным клиентам ({s3_never_called_back}).")],
  computed=[C("s3_never_called_back", "the two callers missed between the fix and T-7 d and never called back",
              "waiting misses at main between the fix and T-7 d with no later answered call to or from the number",
              "core", ["missed_call", "call_leg"])],
  proof=[("core", "missed_call")], sources=["core"])

Q("S03.3", file=F % 3, ref="S3.3", story="S03", asker=4, kind="list", small=True, depends_on="S03.2",
  src_q="What is still wrong?",
  q=T("What is still wrong?", "Что всё ещё не так?"),
  scope=dict(population="Morning-block calls at main.", period="Since the fix, by weekday.",
             definition="The market's busiest weekday: Monday (en), Tuesday (ru)."),
  answer=T("Monday mornings: [[calls.busiest_mornings_since_fix.missed_named|int]] calls missed on the first "
           "[[calls.busiest_mornings_since_fix.mornings|int]] Mondays since the fix, with the callers "
           "({s3_busiest_misses}); at full size "
           "[[=100.0*L('calls.busiest_mornings_since_fix.missed_named')/L('calls.busiest_mornings_since_fix.calls_at_full_size')|pct0]] "
           "of [[calls.busiest_mornings_since_fix.calls_at_full_size|int]] calls, against about "
           "[[calls.busiest_mornings_since_fix.other_mornings_missed_pct|pct]] on other mornings.",
           "Утро вторника: за первые [[calls.busiest_mornings_since_fix.mornings|int]] вторника после перемены "
           "пропущено [[calls.busiest_mornings_since_fix.missed_named|int]] звонков, со списком звонивших "
           "({s3_busiest_misses}); в полном объёме данных это "
           "[[=100.0*L('calls.busiest_mornings_since_fix.missed_named')/L('calls.busiest_mornings_since_fix.calls_at_full_size')|pct0]] "
           "из [[calls.busiest_mornings_since_fix.calls_at_full_size|int]] звонков против примерно "
           "[[calls.busiest_mornings_since_fix.other_mornings_missed_pct|pct]] в остальные утра."),
  list_rule="The calls missed in the morning block at main on the first three of the busiest weekday on or after the "
            "fix, each with its caller.",
  member_slot="s3_busiest_misses",
  computed=[C("s3_busiest_misses", "the seven missed calls with their callers",
              "misses at main in the morning block on the first three Mondays (en) or Tuesdays (ru) on or after the "
              "fix", "core", ["missed_call", "call_leg"])],
  proof=[("core", "missed_call")], sources=["core"])

Q("S03.4", file=F % 3, ref="S3.4", story="S03", asker=6, kind="list", small=True,
  src_q="Who is waiting for a call back right now?",
  q=T("Who is waiting for a call back right now?", "Кто сейчас ждёт перезвона?"),
  scope=dict(population="Waiting misses at the sites she reads: main, and east, where she is posted for cover days.",
             period="The last seven days, at T.", definition="The To call back queue read as her."),
  answer=T("[[calls.queue_at_t.read_by_slot_6|int]] callers, oldest first: the [[calls.queue_at_t.main.waiting|int]] at East "
           "Main, [[calls.queue_at_t.main.from_today|int]] of them from today, and the "
           "[[calls.queue_at_t.east.waiting|int]] at Bonny Oaks, from today ({queue_her}). None of Charlotte Pike's.",
           "[[calls.queue_at_t.read_by_slot_6|int]] человек, начиная с того, кто ждёт дольше всех: "
           "[[calls.queue_at_t.main.waiting|int]] на Московском шоссе, [[calls.queue_at_t.main.from_today|int]] из "
           "них звонили сегодня, и [[calls.queue_at_t.east.waiting|int]] на Инженерном, звонил сегодня ({queue_her}). "
           "С Технической в списке никого."),
  list_rule="Waiting, undismissed misses of the last seven days at main and east, the sites she reads, oldest first.",
  member_slot="queue_her", computed=[Q_MAIN, Q_HER], keys=["time.callback_queue_days", "cast.also_sites"],
  proof=[("core", "the queue read as her")], sources=["core"])

Q("S03.5", file=F % 3, ref="S3.5", story="S03", asker=4, kind="list", small=True,
  src_q="Who is waiting for a call back right now?",
  q=T("Who is waiting for a call back right now?", "Кто сейчас ждёт перезвона?"),
  scope=dict(population="Waiting misses at all sites.", period="The last seven days, at T.",
             definition="The To call back queue read as him."),
  answer=T("The [[=sum(L('calls.queue_at_t')[s]['waiting'] for s in ('main', 'east', 'west'))|int]]: East Main "
           "[[calls.queue_at_t.main.waiting|int]], Bonny Oaks [[calls.queue_at_t.east.waiting|int]], Charlotte Pike "
           "[[calls.queue_at_t.west.waiting|int]] ({queue_all}). Cumberland Bend Electric's "
           "[[s1.a5.misses|int]] missed calls are not among them: they are months old.",
           "[[=sum(L('calls.queue_at_t')[s]['waiting'] for s in ('main', 'east', 'west'))|int]] человек: Московское "
           "шоссе — [[calls.queue_at_t.main.waiting|int]], Инженерный — [[calls.queue_at_t.east.waiting|int]], "
           "Техническая — [[calls.queue_at_t.west.waiting|int]] ({queue_all}). [[s1.a5.misses|int]] пропущенных "
           "звонка «Идель-Электромонтажа» в этот список не входят: им уже несколько месяцев."),
  list_rule="Waiting, undismissed misses of the last seven days at every site, oldest first.",
  member_slot="queue_all", computed=[Q_ALL], keys=["time.callback_queue_days"],
  proof=[("core", "the queue read as him")], sources=["core"])

Q("S03.6", file=F % 3, ref="S3.6", story="S03", asker=4, kind="cannot tell", small=True,
  src_q="Which advisor misses the most calls at the flagship?",
  q=T("Which advisor misses the most calls at the flagship?",
      "Кто из мастеров на Московском пропускает больше всех звонков?"),
  scope=dict(population="In-hours calls at main.", period="The last 90 days.",
             definition="A desk's rate is the misses among calls that rang that desk first."),
  answer=T("By person the data cannot tell: a miss has no person. By desk: 103, about "
           "[[calls.desk.103.miss_w90|pct0]] of the calls that rang it first, against "
           "[[calls.desk.101.miss_w90|pct0]] to [[calls.desk.102.miss_w90|pct0]] for desks 101 and 102.",
           "По людям этого не сказать: у пропущенного звонка нет человека. По аппаратам: 103 — около "
           "[[calls.desk.103.miss_w90|pct0]] звонков, которые пришли на него первым, против "
           "[[calls.desk.101.miss_w90|pct0]]–[[calls.desk.102.miss_w90|pct0]] у аппаратов 101 и 102."),
  cannot=dict(lacks=T("Who missed a call: a miss has no person.",
                      "Кто пропустил звонок: у пропущенного звонка нет человека."),
              may_give=[T("By desk: 103 misses about [[calls.desk.103.miss_w90|pct0]] of the calls that rang it "
                          "first, against [[calls.desk.101.miss_w90|pct0]] to [[calls.desk.102.miss_w90|pct0]] for "
                          "desks 101 and 102.",
                          "По аппаратам: 103 пропускает около [[calls.desk.103.miss_w90|pct0]] звонков, пришедших на "
                          "него первым, против [[calls.desk.101.miss_w90|pct0]]–[[calls.desk.102.miss_w90|pct0]] у "
                          "аппаратов 101 и 102.")],
              wrong_if=T("An answer that ranks advisors by missed calls is wrong.",
                         "Ответ, который ранжирует мастеров по пропущенным звонкам, неверен.")),
  proof=[("core", "call_leg.extension of the first leg")], sources=["core"])

Q("S03.7", file=F % 3, ref="S3.7", story="S03", asker=4, kind="stale", small=True, at="T+1d",
  src_q="Who is on the phones at the flagship right now?",
  q=T("Who is on the phones at the flagship right now?", "Кто сейчас на телефонах на Московском?"),
  scope=dict(population="The roster at the asking instant; punches and calls end at T.",
             period="Asked one day after T.", definition="The answer must say what moment its data is from."),
  answer=T("Names the advisors rostered at the asking instant ({rostered_at_asking}) and says that its latest "
           "clock-in and call on record are dated {t_instant}.",
           "Называет мастеров-приёмщиков, которые по графику стоят в смене в момент вопроса "
           "({rostered_at_asking}), и говорит, что последние отметки прихода и звонки в данных — от {t_instant}."),
  stale=dict(must_state=T("What moment its data is from: the latest clock-in and call on record are dated "
                          "{t_instant}.",
                          "На какой момент у него данные: последние отметки прихода и звонки датированы "
                          "{t_instant}."),
             wrong_if=T("An answer that presents the desk of {t_instant} as “now” is wrong.",
                        "Ответ, который выдаёт за «сейчас» тех, кто был на приёмке {t_instant}, неверен.")),
  computed=[C("rostered_at_asking", "the advisors with a desk shift at main that holds the asking instant",
              "workforce.shift at main, desk position, containing the asking instant (T plus one day)",
              "core", ["workforce.shift"]),
            C("t_instant", "T, the instant the data ends", "the manifest's T; the latest punch and call are dated T",
              "core", ["workforce.punch", "interactions.interaction"], {"en": ("2026-11-13 10:30", "Fri 2026-11-13 10:30"),
                                                                        "ru": ("2026-11-13 10:30", "Fri 2026-11-13 10:30")})],
  proof=[("core", "workforce.shift, punch")], sources=["core"])

# ----------------------------------------------------------------------------------------------- S04
P6_LAST = C("p6_last_working_day", "slot 6's last working day before T",
            "the last day before T's date with a shift of slot 6", "core", ["workforce.shift"],
            day("2026-11-12", "2026-11-10"))
S4_SCOPE = dict(population="Her scored inbound new enquiries.",
                period="The first 30 days after G against the last 30 days.",
                definition="Mean score; share with outcome visit_agreed in the same two windows.")
S4_ANSWER = T("The mean call score rose from [[p06.score_path[0]|int]] in the first 30 days to about "
              "[[p06.score_path[5]|int]] in the last 30 (by period: [[p06.score_path[0]|int]], "
              "[[p06.score_path[1]|int]], [[p06.score_path[2]|int]], [[p06.score_path[3]|int]], "
              "[[p06.score_path[4]|int]], [[p06.score_path[5]|int]]). Calls that end in an agreed visit rose from "
              "[[p06.visit_agreed.first|pct]] to [[p06.visit_agreed.last|pct]].",
              "Средняя оценка звонков выросла с [[p06.score_path[0]|int]] за первые 30 дней примерно до "
              "[[p06.score_path[5]|int]] за последние 30 (по периодам: [[p06.score_path[0]|int]], "
              "[[p06.score_path[1]|int]], [[p06.score_path[2]|int]], [[p06.score_path[3]|int]], "
              "[[p06.score_path[4]|int]], [[p06.score_path[5]|int]]). Доля звонков, которые заканчиваются записью, "
              "выросла с [[p06.visit_agreed.first|pct]] до [[p06.visit_agreed.last|pct]].")

Q("S04.1", file=F % 4, ref="S4.1", story="S04", asker=6, kind="value", small=True,
  src_q="How has my phone work changed since we started? (old: how has her phone work changed)",
  q=T("How has my phone work changed since we started?", "Как изменились мои звонки с запуска системы?"),
  scope=S4_SCOPE, tolerance="1.5 points on the score, 4 points on the share", answer=S4_ANSWER,
  keys=["time.score_period_days"],
  proof=[("core", "interaction_analysis by person")], sources=["core"])

Q("S04.2", file=F % 4, ref="S4.2", story="S04", asker=4, kind="value", small=True,
  src_q="How has Maya's phone work changed since we started?",
  q=T("How has Maya's phone work changed since we started?",
      "Как изменились звонки Алины Хасановой с запуска системы?"),
  scope=S4_SCOPE, tolerance="1.5 points on the score, 4 points on the share",
  answer=T(S4_ANSWER["en"] + " A senior may read a colleague's scores.",
           S4_ANSWER["ru"] + " Руководителю оценки коллеги доступны."),
  keys=["time.score_period_days"],
  proof=[("core", "interaction_analysis by person")], sources=["core"])

Q("S04.3", file=F % 4, ref="S4.3", story="S04", asker=6, kind="value", small=True,
  src_q="What do I still do worst on the phone? (old: what does she still do worst)",
  q=T("What do I still do worst on the phone?", "Что у меня в звонках до сих пор получается хуже всего?"),
  scope=dict(population="Her scored calls.", period="The last 30 days.", definition="Mean level per check."),
  answer=T("Answering a doubt: the `objection` check has the lowest mean level.",
           "Ответ на сомнение клиента: у проверки `objection` самый низкий средний уровень."),
  keys=["p06.worst_check"],
  proof=[("core", "interaction_analysis.result_public.checks")], sources=["core"])

Q("S04.4", file=F % 4, ref="S4.4", story="S04", asker=4, kind="smoke", small=True,
  src_q="Which team notes wait for a decision?",
  q=T("Which team notes wait for a decision?", "Какие заметки команды ждут решения?"),
  scope=dict(population="Proposals in state proposed.", period="At T.", definition="Open proposals of team notes."),
  answer=T("Two: Maya Torres's about the company driver, from {p6_last_working_day}, and the nightly one, “Prices "
           "source”, with three holders.",
           "Две: предложение Алины Хасановой про водителей организаций, от {p6_last_working_day}, и ночное — "
           "«Откуда брать цены», такая заметка есть у троих."),
  facts=[T("Two proposals wait.", "Ждут два предложения."),
         T("Maya Torres's, about the company driver, proposed on {p6_last_working_day}.",
           "Предложение Алины Хасановой про водителей организаций, подано {p6_last_working_day}."),
         T("The nightly tidy-up's, “Prices source”, held by three people.",
           "Предложение ночной проверки «Откуда брать цены»: одинаковая заметка есть у троих.")],
  computed=[P6_LAST], keys=["s4.notes"],
  proof=[("memory", "platform.proposal")], sources=["memory"])

Q("S04.5", file=F % 4, ref="S4.5", story="S04", asker=6, kind="value", small=True,
  src_q="Why was my note declined? (old: why was her note declined)",
  q=T("Why was my note declined?", "Почему мою заметку отклонили?"),
  scope=dict(population="Her rejected proposal.", period="At T.", definition="The decider's reason and its date."),
  answer=T("Greg Whitaker declined it on {s4_declined_day}: the knowledge page “Booking a visit” already says it, "
           "and the wording should be proposed there.",
           "Сергей Анатольевич Мельников отклонил её {s4_declined_day}: на странице «Запись на ремонт» это уже "
           "есть, формулировку он предлагает внести туда."),
  computed=[C("s4_declined_day", "the day slot 4 declined her second proposal",
              "decided_at of the rejected proposal: the full open day after the Monday of week T-3 (ru: after her "
              "first working day on or after it)", "memory", ["platform.proposal"])],
  keys=["s4.notes"], pages=["how-to/booking-a-visit.md"],
  proof=[("memory", "platform.proposal")], sources=["memory", "knowledge_base"])

Q("S04.6", file=F % 4, ref="S4.6", story="S04", asker=6, kind="refusal", small=True,
  src_q="How do Caleb's call scores compare with mine?",
  q=T("How do Caleb's call scores compare with mine?", "Какие оценки звонков у Никиты по сравнению с моими?"),
  scope=dict(population="A colleague's phone performance.", period="Any.",
             definition="Colleagues' phone performance is read from senior rank."),
  answer=T("Refused by rank for his scores; her own may be given.",
           "Отказ по уровню доступа: его оценки ей недоступны; свои она получить может."),
  refusal=dict(by="rank",
               reason=T("A colleague's call scores are read from senior rank.",
                        "Оценки звонков коллеги видны с уровня «Старший менеджер»."),
               may_offer=T("Her own scores.", "Её собственные оценки.")),
  proof=[("core", "performance rank setting")], sources=["core"], known_failure=True)
