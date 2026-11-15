# -*- coding: utf-8 -*-
"""Russian story conversations 1 to 8 (stories S7, S1, S6, S13). Written in Russian from the cards, not from the English set."""
from srclib import *

CFG = "ru"
OLGA = {"ref": "named_customers.json ru.S7", "name": "Ольга Сергеевна Тимофеева", "in_chat": "Ольга", "first_time": True, "phone": "+7 907 378-60-35"}
OLGA_NOTE = "One website visitor: the browser of the first chat, remembered for 30 days (ledger conv.web_visitor_memory_days). The contact holds no name and no phone; both are in the hand-off notes and on the cards."
HELLO = "Здравствуйте! Я виртуальный помощник «Ермак-Сервиса». "


def fl(word, said_on, day, form=None):
    row = dict(word=word, said_on=said_on, day=day)
    if form:
        row["form"] = form
    return row


def f01():
    f = File(CFG, 1, "S7", "web-after-hours",
             "Чат на сайте в пятницу вечером: шум, один вопрос, ассистент передаёт заявку, утром Алина",
             "The assistant answers first on the web chat, from public pages only. The customer is unclear (R13): she asks what it costs to 'look at' a noise she hears mostly in the mornings. The assistant asks once, braking or turning, and that settles it; she adds her husband's guess, and the assistant does not argue with it. It cannot book: it takes a name and a number and hands over as a scheduling request. The junior operator picks it up six minutes after opening.")
    f.cast = {"customer": OLGA}
    f.staff(6)
    ev = f.day(wd(6, -10, plus=-1), "the chat, 21:10: the evening before day A")
    a = f.day(wd(6, -10), "day A: slot 6 takes the hand-over, books the visit, rings to confirm")
    v = f.day(wd(6, -9), "the visit, 09:30: slot 6's next working day after A")
    f.p("700 ₽", "диагностика тормозной системы, фиксированная цена", job="brake_inspection")
    f.scenario = {
        "who_writes": "Новая клиентка, с телефона, когда сервис уже закрыт.",
        "vehicle": "Hyundai Solaris 2016, 112 000 км",
        "wants": "Думает, что ей нужна цена «посмотреть шум». На деле нужна диагностика тормозов, и поскорее.",
        "what_happens": "Один уточняющий вопрос, цена диагностики с открытой страницы, просьба записать на воскресенье с утра. Записать ассистент не может: спрашивает имя, телефон и сервис, передаёт заявку и говорит, что с ней свяжутся. В субботу в 9:06 Алина записывает на воскресенье, 9:30, и обещает позвонить (звонок есть в наборе звонков, без оценки).",
        "facts": {"hours": "9:00–20:00, без выходных", "address_main": "Московское шоссе, 40",
                  "public_pages_used": ["часы работы и адреса", "прайс: диагностика тормозной системы", "вопросы о тормозах: скрежет при торможении"],
                  "booked": "%s 09:30, main; запись в ERP, источник web chat" % v,
                  "anchors": "rule R6: day A is slot 6's 10th working day before T (a Saturday for the nominal T); the chat is the evening before it and the visit her next working day, at 9:30 (ledger s7.booking_day, s7.thread). The first chat is under 30 days before T (conv.web_visitor_memory_days)."},
        "unclear": {"kind": "vague: a noise, mostly in the mornings, and a price asked for looking at it", "loops": 1, "resolved": True,
                    "how": "Ассистент один раз спрашивает, когда появляется шум: при нажатии на тормоз или при повороте руля. Ответ: «когда торможу, скрежет, спереди». Про подшипник не спорит и ремонт не оценивает."}}
    f.floating = [fl("в воскресенье с утра", ev, v, "в + accusative"), fl("на завтра, воскресенье", a, v, "на + accusative"), fl("завтра в 9:30", a, v, "adverb"),
                  fl("Сегодня", a, a, "adverb")]
    c = web(f, "c1", "main", 1, 1)
    c.c(ev + " 21:10:08", "здравствуйте. машина шумит, сколько стоит посмотреть")
    c.c("21:10:21", "по утрам в основном")
    c.a("21:10:46", HELLO + "Сейчас сервис закрыт, откроемся в 9:00, но на вопросы отвечу. Цена зависит от того, откуда шум, поэтому сначала уточню: он появляется, когда нажимаете на тормоз или когда поворачиваете руль? И какая у вас машина?")
    c.c("21:11:38", "когда торможу. скрежет такой противный, спереди")
    c.c("21:11:55", "муж говорит подшипник, но по моему нет")
    c.a("21:12:27", "Теперь понятно, спасибо. Скрежет спереди при нажатии на тормоз чаще всего связан с износом колодок, но точно скажет только мастер после осмотра: по переписке диагноз я поставить не могу. Начать стоит с диагностики тормозной системы: 700 ₽, около получаса. Мастер покажет, что нашёл, и только потом посчитает ремонт. С таким звуком лучше не затягивать. Передать заявку, чтобы вас записали?")
    c.c("21:13:10", "да, давайте. а в воскресенье с утра можно? солярис 2016")
    c.a("21:13:36", "Сам записать я не могу, но передам заявку мастеру-приёмщику, он подтвердит время. Напишите, пожалуйста, как к вам обращаться и номер телефона. И в какой сервис удобнее: на Московском шоссе или в Новом городе?")
    c.c("21:14:20", "Ольга 89073786035")
    c.c("21:14:31", "на московском")
    c.a("21:15:02", "Спасибо, Ольга. Заявку передал, с вами свяжутся в ближайшее время. Могу ещё чем-то помочь?")
    c.h("21:15:03", "scheduling", "Ольга", "+7 907 378-60-35", "на московском",
        "Hyundai Solaris 2016. Скрежет спереди при нажатии на тормоз, в основном по утрам. Сначала спросила, сколько стоит «посмотреть шум»; я один раз уточнил, при торможении он или при повороте руля: при торможении. Муж считает, что это подшипник. Просит записать на диагностику тормозов в воскресенье с утра, Московское шоссе.",
        "main", "%s 20:00, закрытие следующего рабочего дня" % a)
    c.c("21:15:40", "нет, спасибо")
    c.d("21:16:12", "d1", "Пожалуйста, Ольга! Хорошего вечера.")
    c.s(6, a + " 09:06:15", "Ольга, доброе утро! Это Алина, мастер-приёмщик «Ермак-Сервиса» на Московском шоссе. Записала вас на завтра, воскресенье, на 9:30: диагностика тормозов, Solaris. Это 700 ₽ и минут тридцать, по результату всё покажем и посчитаем. Если с утра не получится, есть ещё окно в 13:30. Сегодня наберу вас, чтобы подтвердить.")
    c.c("09:31:40", "9:30 отлично, спасибо большое")
    c.d("09:32:20", "d2", "Пожалуйста, Ольга! Ждём вас завтра в 9:30: Московское шоссе, 40.")
    c.s(6, "09:33:30", "Пожалуйста, Ольга! Ждём вас завтра в 9:30: Московское шоссе, 40.", use="d2")
    c.label(6, "09:33:50", "запись")
    c.res(6, "09:34:05")
    c.out("14:20", "calls", "Алина звонит подтвердить запись: исходящий, расшифрован, без оценки (calls design, story call 8); час звонка задаёт набор звонков")
    c.out(v + " 09:30", "erp", "клиентка приехала; заказ-наряд открыт слотом 6")
    c.state_extra = {"contact_note": OLGA_NOTE}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's (the assistant wrote it); slot 6 has two replies and one resolution"}
    f.truth = {"reason": "a symptom", "handled": "assistant first, handed over (scheduling), slot 6", "outcome": "диагностика тормозов назначена на следующий день, 09:30, main",
               "facts": ["first written at 21:10 on the evening before day A, outside opening hours", "one clarifying question, asked by the assistant",
                         "the assistant named only the inspection price, 700, and no repair", "handed over with her name and number; the contact itself holds neither",
                         "slot 6's first line {first} working minutes after opening", "resolved by slot 6, label «запись»"],
               "questions": ["S7.1"]}
    f.why = ["Ассистент не записывает, не называет цену ремонта и не обещает срок: «в ближайшее время» — формула самого продукта.",
             "Одного вопроса хватило: он предлагает два варианта, и ответ приходит двумя сообщениями, вторым — версия мужа. В заметке её слова и то, что спрашивали один раз.",
             "Две реплики Алины — её лист: грамотно, полно, сначала время, потом цена, без канцелярита; вторая — черновик ассистента, отправленный как есть."]
    f.new_facts = ["Звонок-подтверждение показан в 14:20; час задаёт calls/ru."]
    return f


def f02():
    f = File(CFG, 2, "S7", "web-approval-and-thanks",
             "День визита: в чате на сайте она соглашается на тормоза и откладывает амортизаторы; на следующий день благодарит",
             "A returning website visitor is the same contact, and the assistant remembers her name and number. It cannot see or change a repair order, so an approval is a hand-over, kind escalation. The junior operator confirms in four minutes with the price, the total and the pick-up time, and resolves. The thanks next morning reopens her chat on a day she is off (two on, two off): the newcomer on shift sends the waiting draft as it was, and she resolves the chat on her next working day.")
    f.cast = {"customer": dict(OLGA, first_time=False)}
    f.staff(6, 7)
    f.cast["named_in_a_line"] = [{"slot": 12, "name": "Алексей Карпов", "role": "механик, который делал машину"}]
    v = f.day(wd(6, -9), "the visit: slot 6's next working day after day A")
    th = f.day(wd(6, -9, plus=1), "the day after the visit; slot 6 is off, slot 7 is on")
    back = f.day(wd(6, -8), "slot 6's next working day: she resolves the chat")
    f.p("12 520 ₽", "замена передних тормозных дисков и колодок, класс car, стандартные запчасти", job="front_pads_rotors")
    f.p("13 322,60 ₽", "счёт к оплате: диагностика 700 + диски и колодки 12 520 + расходные материалы 102,60; НДС 5 % в том числе (634,41), сверху ничего не добавляется", amount=13322.6, source={"ledger": "s7.bill.with_tax"})
    f.scenario = {
        "who_writes": "Та же клиентка, с работы, прочитав смету, которую сервис прислал ей на почту.",
        "vehicle": "Hyundai Solaris 2016",
        "wants": "Согласиться на передние тормоза и отложить задние амортизаторы.",
        "what_happens": "Диагностика показала износ передних колодок и дисков и запотевший задний амортизатор. Решение она пишет в новом визите на сайт; ассистент передаёт его; Алина подтверждает работу, итог и время. Вечером она платит картой. Наутро благодарит: чат открывается снова, Алина выходная, готовый черновик отправляет Никита; Алина закрывает чат, когда выходит на смену.",
        "facts": {"found": "передние колодки стёрты до индикатора, диски с бортиком; правый задний амортизатор запотел", "approved": "замена передних тормозных дисков и колодок",
                  "declined_and_deferred": "задние амортизаторы, пара: 11 720 по прайсу (ledger s7.bill.declined_rear_shocks); поставлено напоминание",
                  "paid": "13 322,60 картой, в том числе НДС 634,41 (ledger s7.bill)", "public_pages_used": []}}
    f.floating = [fl("утром", v, v, "adverb"), fl("сегодня", v, v, "adverb"), fl("вчера", th, v, "adverb")]
    c = web(f, "c1", "main", 1, 2)
    c.out(v + " 09:30", "erp", "визит: заказ-наряд открыт слотом 6; осмотр делает слот 12")
    c.out("10:40", "erp", "смета уходит ей на электронную почту из учётной системы: диски и колодки спереди 12 520; задние амортизаторы, пара, 11 720")
    c.c("11:02:10", "здравствуйте, это Ольга, солярис, я утром у вас машину оставила")
    c.c("11:02:40", "смету на почте посмотрела. колодки с дисками делайте. амортизаторы пока нет, сразу столько не потяну")
    c.a("11:03:05", "Ольга, здравствуйте! Заказ-наряды я не вижу и изменить в них ничего не могу, поэтому сразу передам мастеру-приёмщику на Московском шоссе: передние колодки и диски делаем, задние амортизаторы пока нет. Номер для связи прежний, +7 907 378-60-35?")
    c.c("11:03:30", "да")
    c.a("11:03:53", "Спасибо. Передал, с вами свяжутся в ближайшее время.")
    c.h("11:03:54", "escalation", "Ольга", "+7 907 378-60-35", "Московское шоссе",
        "Ольга, Hyundai Solaris 2016, машина сегодня на Московском шоссе. Смету прочитала: передние тормозные колодки и диски делать, задние амортизаторы пока не делать, говорит, что сразу столько не потянет. Заказ-наряд я не вижу, поэтому ничего не подтверждал.",
        "main", "%s 20:00, закрытие дня" % v)
    c.s(6, "11:07:40", "Ольга, это Алина. Всё поняла: передние колодки и диски меняем сегодня, это 12 520 ₽, задние амортизаторы отметила как отложенные. Правый пока только запотел, не течёт, месяц-полтора с ним ездить можно, я поставлю вам напоминание. Вместе с диагностикой и расходными материалами сегодня выйдет 13 322,60 ₽. Машину Алексей отдаст к 15:00, мы до 20:00.")
    c.c("11:12:30", "хорошо, спасибо")
    c.d("11:13:10", "d1", "Пожалуйста, Ольга! Ждём вас после 15:00.")
    c.s(6, "11:14:20", "Пожалуйста, Ольга! Ждём вас после 15:00.", use="d1")
    c.label(6, "11:14:40", "согласование")
    c.res(6, "11:15:00")
    c.out("18:40", "erp", "заказ-наряд закрыт: диски и колодки спереди заменены; задние амортизаторы — отказ, отложено, напоминание создано; оплата картой, 13 322,60")
    c.c(th + " 10:15:20", "забрала вчера, тормозит как новая) спасибо вам большое")
    c.d("10:16:00", "d2", "Ольга, спасибо за добрые слова! Рады, что всё в порядке. Обращайтесь.")
    c.s(7, "10:33:10", "Ольга, спасибо за добрые слова! Рады, что всё в порядке. Обращайтесь.", use="d2")
    c.res(6, back + " 09:04:10")
    c.state_extra = {"contact_note": OLGA_NOTE}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 6 has two replies and two resolutions of one chat (Stats counts distinct chats: one), one draft sent as it was; slot 7 has one reply in her chat, a draft sent as it was"}
    f.truth = {"reason": "found work: approve or decline", "handled": "assistant first, handed over (escalation), slot 6; the thanks answered by slot 7",
               "outcome": "диски и колодки спереди согласованы и оплачены, 13 322,60, НДС в том числе; задние амортизаторы отложены",
               "facts": ["approved: front brake discs and pads, 12 520", "declined: rear shock absorbers (a pair), deferred with a reminder", "paid by card: 13 322,60, VAT inside",
                         "a thank-you from her the next morning, answered by slot 7 because slot 6 was off; the chat is resolved by slot 6", "the same website contact as the first chat"],
               "questions": ["S7.1", "S7.2"]}
    f.why = ["Ассистент повторяет её решение простыми словами и не подтверждает того, чего не видит.",
             "Алина отвечает на то, о чём спросили, и на то, о чём спросят следом: итог, время, и почему амортизатор может подождать.",
             "«Спасибо» приходит в её выходной. Никита отправляет готовый черновик, не меняя ни слова, а чат она закрывает сама, когда возвращается: два через два в одной переписке."]
    f.new_facts = ["Смета ушла ей на электронную почту из учётной системы около 10:40 в день визита (o.timofeeva@pochta.example).",
                   "Машина была готова к 15:00; наряд закрыт и оплачен около 18:40.", "Запотел правый задний амортизатор.",
                   "На «спасибо» ответил слот 7 (его смена), чат закрыла слот 6 на следующий свой рабочий день."]
    return f


def f03():
    f = File(CFG, 3, "S7", "web-return-draft-waiting",
             "Она возвращается за амортизаторами: ассистент называет цену и передаёт заявку, Алина берёт чат; в момент T её ответ не прочитан и ждёт черновик",
             "The live-demo chat. A returning visitor asks to book the deferred work. The assistant answers from the public price list, cannot book, hands over; from Alina's first line the chat is hers and the assistant only drafts. Thirty minutes before T the customer writes again: the chat is open, owned by slot 6, unread, with one draft in the box that is honest about what the assistant cannot see. Editing it (two free times on the evenings she asked for, the total to pay) and sending it is the demo.")
    f.cast = {"customer": dict(OLGA, first_time=False)}
    f.staff(6)
    r = f.day(wd(6, -1), "the return chat, 15:40; slot 6 replies at 16:05")
    t = f.day(T(), "she writes again 30 minutes before T")
    f.day(wd(6, 1), "'в субботу': slot 6's next working day after T")
    f.day(wd(6, 2), "'во вторник': slot 6's 2nd working day after T")
    f.day(wd(6, 3), "'в среду': her 3rd")
    f.p("11 720 ₽", "замена задних амортизаторов, пара, класс car, стандартные запчасти, прайс на сегодня", job="rear_shocks_pair")
    f.scenario = {
        "who_writes": "Та же клиентка, с того же телефона, через 16 дней после визита.",
        "vehicle": "Hyundai Solaris 2016",
        "wants": "Записаться на задние амортизаторы, от которых отказалась, и узнать итог.",
        "what_happens": "Во вторник в 15:40 она спрашивает цену и можно ли на этой неделе. Ассистент называет цену из прайса и передаёт заявку. В 16:05 Алина предлагает два времени. В тот день ответа нет. В пятницу в 10:00 клиентка пишет, что ни одно не подходит, просит вторник или среду вечером и спрашивает итог. Ассистент готовит черновик; к моменту T его никто не открывал.",
        "facts": {"declined_at_the_visit": "задние амортизаторы, пара", "to_pay_with_supplies": 11811.2, "before_vat": 11248.76,
                  "expected_reply": "два свободных времени на main во вторник или в среду недели W+1 вечером, как она просит, и цена: 11 720 плюс расходные материалы, 11 811,20 к оплате, НДС в том числе (card S07, question S7.3)",
                  "public_pages_used": ["прайс: замена задних амортизаторов"]}}
    f.floating = [fl("на этой неделе", r, "the week W0", "на + prepositional"), fl("на пятницу на 16:00", r, "T", "на + accusative"), fl("на субботу на 12:30", r, "T+1d", "на + accusative"),
                  fl("в пятницу и субботу", t, "T and T+1d", "в + accusative"), fl("на следующей неделе", t, "the week W+1", "на + prepositional"),
                  fl("во вторник или среду вечером", t, "T+4d or T+5d", "в + accusative"), fl("на вторник или среду вечером", t, "T+4d or T+5d", "на + accusative")]
    c = web(f, "c1", "main", 1, 3)
    c.c(r + " 15:40:10", "здравствуйте, это снова Ольга, солярис. созрела на задние амортизаторы)")
    c.c("15:40:35", "сколько это будет и можно ли на этой неделе")
    c.a("15:41:00", "Ольга, здравствуйте, рад вас снова видеть! По прайсу замена задних амортизаторов, пара, для вашего класса машины стоит 11 720 ₽ с запчастями; точная сумма по вашей смете есть у мастера. Сам записать я не могу, передам заявку на Московское шоссе, время вам подтвердят. Номер прежний, +7 907 378-60-35?")
    c.c("15:41:30", "да, тот же")
    c.a("15:41:54", "Спасибо. Заявку передал, с вами свяжутся в ближайшее время.")
    c.h("15:41:55", "scheduling", "Ольга", "+7 907 378-60-35", "Московское шоссе",
        "Ольга, Hyundai Solaris 2016, Московское шоссе. Хочет записаться на замену задних амортизаторов, которую отложила в прошлый визит, на этой неделе. Я назвал цену из прайса за пару, 11 720 ₽ с запчастями, время не называл.",
        "main", "%s 20:00, закрытие дня" % r)
    c.s(6, "16:05:15", "Ольга, добрый день! Это Алина. Хорошо, что решились, с амортизаторами тянуть не стоит. Могу записать вас на пятницу на 16:00 или на субботу на 12:30, по времени это часа полтора. Как вам удобнее?",
        late="story: the card's 16:05 (ledger s7.thread.taken_by_6)")
    c.c(t + " 10:00:10", "Алина, доброе утро. простите что пропала, только увидела")
    c.c("10:00:42", "в пятницу и субботу никак, на работе завал. а на следующей неделе во вторник или среду вечером можно? и сколько всего с меня будет")
    c.d("10:01:20", "d1", "Ольга, доброе утро! Ничего страшного. Замена задних амортизаторов, пара, стоит 11 720 ₽ с запчастями. Итог по вашей смете и свободное время на вторник или среду вечером уточню и сразу вам напишу.")
    c.state_extra = {"contact_note": OLGA_NOTE,
                     "live_demo": "a web chat owned by slot 6, so the waiting draft can be edited and sent in a live demo (ledger conv.live_demo, conv.open_at_t)"}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 6: one reply 23 minutes after the hand-off, nothing resolved; the second hand-over card was taken by her at 16:05"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "assistant first, handed over (scheduling), slot 6; then drafts",
               "outcome": "open at T, owned by slot 6, unread, one unsent draft",
               "facts": ["she asked on slot 6's last working day before T to book the rear shock absorbers she had declined",
                         "the assistant gave the list price, 11 720 with parts, and handed over",
                         "slot 6 offered Friday 16:00 or Saturday 12:30; she cannot come either day and asks for Tuesday or Wednesday evening of the next week and for the total",
                         "the right answer offers two free times on the Tuesday or the Wednesday evening of week W+1 and the price: 11 720 plus supplies, 11 811,20 to pay, VAT inside", "nothing is sent without slot 6"],
               "questions": ["S7.1", "S7.2", "S7.3"]}
    f.why = ["В черновике то, что ассистент знает (цена из прайса), и обещание выяснить остальное. Правка Алины — два времени и итог.",
             "В её реплике в 16:05 цены нет: сначала время, а цену только что назвали.",
             "Вторник и среда следующей недели — её рабочие дни: Алина может ответить «приму сама»."]
    f.new_facts = ["Алина предложила пятницу (день T) в 16:00 и субботу в 12:30; клиентка не может в оба дня и просит вторник или среду следующей недели, вечером.",
                   "О замене задних амортизаторов говорят «часа полтора» (каталог: 1,6 нормо-часа)."]
    return f


def f04():
    f = File(CFG, 4, "S1", "web-fleet-quote-waited",
             "Новый логист уходящего корпоративного клиента просит смету в чате на сайте; первый ответ человека через два дня",
             "A hand-over that nobody takes. The request arrives on Tuesday after closing; the assistant will not price contract work, takes a number and hands over. On Wednesday the lead advisor reads it and passes it on in a private note; the newcomer answers 'да-да, сделаю' in another note. A note answers nobody: the customer's follow-up on Thursday gets a draft that sits until 19:25, when the newcomer sends it as it was, writes 'сегодня должен отправить', answers one of her two questions and sends the estimate at 19:56. On Friday both are off (two on, two off); the assistant's draft answers the question he skipped, and the junior operator on shift sends it.")
    f.cast = {"customer": {"ref": "accounts.json ru.A6 contacts[1]", "name": "Дарья Олеговна Вершинина", "in_chat": "Дарья", "company": "ООО «Вкусный выезд»",
                           "role": "менеджер по логистике, отвечает за машины с даты P", "phone": "+7 907 747-46-46", "first_time": False},
              "named_in_a_line": [{"name": "Марина Александровна Белоусова", "ref": "accounts.json ru.A6 contacts[2]", "role": "директор; согласует оплату (в чате — «директор»)"}]}
    f.staff(5, 7, 6, s7={"weeks_in_the_job": 10})
    d0 = f.day(wk("Wed", 4, slot=7, plus=-1, note="card S01: the evening before the first day of a working pair of slot 7 on or after that Wednesday; for the nominal T the Wednesday is the pair's first day, so this is the Tuesday of week T-4"),
               "the quote request at 20:41, after closing (ledger s1.dates.a6_chat_waited_two_days)")
    d1 = f.day(wk("Wed", 4, slot=7), "the first day of slot 7's working pair; slots 5 and 7 on shift: two notes, no reply")
    d2 = f.day(wk("Wed", 4, slot=7, plus=1), "the second day of the pair: her follow-up; slot 7's first reply at 19:25; the estimate")
    d3 = f.day(wk("Wed", 4, slot=7, plus=2), "she passes it to the director; slots 5 and 7 are off, slot 6 sends the draft")
    f.day(wk("Wed", 4, slot=7, plus=9), "Chatwoot resolves the chat after 7 silent days")
    f.p("16 276 ₽", "замена передних тормозных дисков и колодок, класс van, стандартные запчасти, по прайсу (в смете)", job="front_pads_rotors", cls="van")
    f.p("11 274 ₽", "замена аккумуляторной батареи, класс van, по прайсу (в смете)", job="battery_replace", cls="van")
    f.num_("30 дней", "отсрочка платежа по договору (accounts.json, ledger acct.A6.terms_days)")
    f.scenario = {
        "who_writes": "Человек, которому машины достались от завхоза: тот просто звонил старшему приёмщику. Пишет из офиса, полными фразами, и сравнивает предложения.",
        "vehicles": ["№ 7, Ford Transit, фургон, 2019, К599МК73", "№ 8, Citroën Jumper, фургон, 2017, С152ХЕ173"],
        "wants": "Смету с разбивкой на две машины до записи, к пятнице: в пятницу утром директор согласует расходы.",
        "what_happens": "Во вторник в 20:41 она пишет. В среду в 12:10 Дмитрий оставляет заметку Никите. В четверг в 11:05 она напоминает. В 19:25 Никита отправляет ждавший черновик; смета уходит в 19:56, цены по прайсу. В пятницу она передаёт её директору. Записи нет; через неделю чат закрывает Chatwoot.",
        "facts": {"price_class": "по прайсу: у средних корпоративных клиентов договорных цен нет (catalogue.json company_account_terms)", "terms": "отсрочка 30 дней (accounts.json)",
                  "first_person_reply_after": "почти двое суток: вторник 20:43 — четверг 19:25; 1 285 рабочих минут",
                  "hours": "сервис работает без выходных, 9:00–20:00 (ledger site.open_days)", "public_pages_used": ["часы работы и адреса"],
                  "rota": "вторник — смена слотов 6 и 29, но запрос пришёл после закрытия; среда и четверг — смена 5 и 7; пятница — снова 6 и 29",
                  "note": "This is the chat of card S01's wrinkle, 'a chat that waited two days'. Call 22 (the quote promised and sent two days late) is another event, on the Tuesday of week T-9, about vans № 2 and № 5; this chat does not mention it. The two estimates are two of A6's five slow ones (ledger s1.a6). 16 276 and 11 274 are list prices: what A6 pays, VAT inside, nothing on top."}}
    f.floating = [fl("В пятницу утром", d0, d3, "в + accusative"), fl("со вторника", d2, d0, "с + genitive"), fl("сегодня", d2, d2, "adverb"), fl("завтра утром", d2, d3, "adverb"),
                  fl("в выходной", d2, "any Saturday or Sunday", "в + accusative"), fl("в субботу или воскресенье", d3, "any Saturday or Sunday", "в + accusative")]
    c = web(f, "c1", "main", 207, 4)
    c.c(d0 + " 20:41:10", "Добрый вечер. Меня зовут Дарья, компания «Вкусный выезд», обслуживаемся у вас на Московском шоссе по договору.")
    c.c("20:42:25", "Нужна смета на две машины, до записи. Ford Transit 2019: передние тормоза, колодки и диски. Citroën Jumper 2017: аккумулятор под замену. С разбивкой, работы и запчасти отдельно. В пятницу утром директор согласует расходы.")
    c.a("20:42:52", "Дарья, добрый вечер! Я виртуальный помощник «Ермак-Сервиса». Сейчас сервис закрыт, откроемся в 9:00. Смету на конкретные машины по договору я подготовить не могу и не хочу называть цены из общего прайса, которые могут не совпасть с вашими условиями. Передам запрос мастерам-приёмщикам на Московском шоссе, смету с разбивкой пришлют они. Напишите, пожалуйста, номер телефона для связи.")
    c.c("20:43:30", "+7 907 747-46-46")
    c.a("20:43:55", "Спасибо, Дарья. Запрос передал, с вами свяжутся в ближайшее время.")
    c.h("20:43:56", "escalation", "Дарья", "+7 907 747-46-46", "Московское шоссе",
        "Дарья, компания «Вкусный выезд» (клиент по договору, Московское шоссе). Просит смету с разбивкой на работы и запчасти до записи: Ford Transit 2019 — передние тормозные колодки и диски; Citroën Jumper 2017 — замена аккумулятора. В пятницу утром расходы согласует директор. Цен я не называл.",
        "main", "%s 20:00, закрытие следующего рабочего дня" % d1)
    c.n(5, d1 + " 12:10:30", "@Никита Ведяшкин посчитай смету вкусному выезду, 2 машины. цены по прайсу, договрных у них нет. я на выдаче зашиваюсь", mentions=[7])
    c.n(7, "12:16:10", "да-да, сделаю")
    c.c(d2 + " 11:05:20", "Добрый день. Подскажите, пожалуйста, по смете: вопрос актуален, жду со вторника.")
    c.d("11:06:00", "d1", "Дарья, добрый день! Приношу извинения за ожидание. Ваш запрос на смету по двум машинам у мастеров-приёмщиков, смету с разбивкой вам пришлют. Если пришлёте госномера или VIN, расчёт будет точным.")
    c.s(7, "19:25:30", "Дарья, добрый день! Приношу извинения за ожидание. Ваш запрос на смету по двум машинам у мастеров-приёмщиков, смету с разбивкой вам пришлют. Если пришлёте госномера или VIN, расчёт будет точным.",
        use="d1", late="story: the two days of card S01 (ledger s1.a6.quote_chat_waited_days)")
    c.s(7, "19:26:10", "Считаю, сегодня должен отправить")
    c.c("19:31:15", "Номера: К599МК73 и С152ХЕ173. Хорошо, жду. Напомню, что согласование завтра утром.")
    c.c("19:31:40", "И сразу два вопроса: отсрочка 30 дней по договору у нас сохраняется? И можно ли Transit принять в выходной? В будни он на линии.")
    c.d("19:32:25", "d2", "Спасибо, Дарья, этих данных достаточно. По отсрочке и приёму в выходной уточню и отвечу вместе со сметой.")
    c.s(7, "19:40:00", "Да, отсрочка сохраняется!")
    c.label(7, "19:40:30", "юрлицо")
    c.s(7, "19:56:40", "Дарья, смета по двум машинам во вложении. Когда удобно пригнать?",
        files=[{"kind": "file", "file": "Smeta_Vkusny_vyezd_Transit_Jumper.pdf", "pool": "estimate-pdf",
                "shows": "смета по прайсу на две машины: Ford Transit — замена передних тормозных дисков и колодок, 16 276 ₽; Citroën Jumper — замена аккумуляторной батареи, 11 274 ₽; расходные материалы отдельной строкой; итог — в том числе НДС 5 %"}])
    c.c(d3 + " 09:12:30", "Получила, спасибо. Передаю директору.")
    c.d("09:13:10", "d3", "Пожалуйста, Дарья! И по второму вопросу: сервис работает без выходных, с 9:00 до 20:00, так что Transit можно принять в субботу или воскресенье.")
    c.s(6, "09:17:20", "Пожалуйста, Дарья! И по второму вопросу: сервис работает без выходных, с 9:00 до 20:00, так что Transit можно принять в субботу или воскресенье.", use="d3")
    c.auto()
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 7: his first line {first} working minutes after the hand-off, four replies, one draft sent as it was and one discarded, nothing resolved; slot 5: a note and no reply; slot 6: one reply in his chat, a draft sent as it was"}
    f.truth = {"reason": "company account: weekly bookings, quotes, documents", "handled": "assistant first, handed over (escalation); slot 5's note; slot 7; one line by slot 6",
               "outcome": "смета отправлена почти через двое суток после запроса; записи нет; закрыт по 7 дням тишины",
               "facts": ["asked on the Tuesday of week T-4 at 20:41, after closing; handed over at 20:43", "the first line by a person came on Thursday at 19:25: almost two days, two full working days of slots 5 and 7",
                         "slot 5 read it on Wednesday and passed it to slot 7 in a private note", "the estimate, at list prices, went out on Thursday at 19:56",
                         "of her two questions slot 7 answered one; the other was answered by the assistant's draft, sent by slot 6 the next morning", "no visit followed"],
               "questions": ["S1.3"]}
    f.why = ["Дарья пишет как человек из офиса: полными фразами, с номерами, с датой согласования. Реплики всё короче: представилась, «жду со вторника», «Хорошо, жду», «Получила, спасибо». Никто никому не грубит.",
             "Дмитрий — в заметке, а не клиенту, наспех, с опечаткой («договрных»): как в cast.json.",
             "Никита: «да-да, сделаю», «должен отправить», восклицательный знак на опоздавшем ответе, из двух вопросов ответ на первый.",
             "Два через два: запрос приходит вечером чужой смены, два дня висит на своей, а на третий день хвост закрывает уже другая смена."]
    f.new_facts = ["Смета — на машины № 7 (Ford Transit: передние диски и колодки, 16 276 по прайсу) и № 8 (Citroën Jumper: аккумулятор, 11 274 по прайсу); нужна к согласованию у директора в пятницу недели T-4.",
                   "ERP: смету из этого чата предлагается считать одной из пяти «медленных» смет A6 (ledger s1.a6), просрочена; заказа не было.",
                   "Файл Smeta_Vkusny_vyezd_Transit_Jumper.pdf (пул 'estimate-pdf').",
                   "Запрос пришёл во вторник в 20:41, после закрытия: так день карточки сохранён, а первая реплика человека приходится на смену слотов 5 и 7.",
                   "Смета звонка 22 (неделя T-9) была на машины № 2 (передние колодки и диски, 16 276) и № 5 (ТО); эта, на № 7 и № 8, — другая: обе входят в пять «медленных» смет A6."]
    return f


def f05():
    f = File(CFG, 5, "S1", "telegram-weekly-vans",
             "Здоровый корпоративный клиент: заявка диспетчера на понедельник, каждую неделю, в одном чате в Telegram",
             "One messenger conversation for life: every week the dispatcher's message reopens it, the assistant drafts, the east shop's lead advisor edits and sends, and resolves. Four sessions are written: the first after go-live, found work that had hung for two days on the other advisor's shift, a van swapped, and this week's, which at T is confirmed and waits on the customer. It is the named open messenger chat: its last public line is the shop's and no draft sits in its box.")
    f.cast = {"customer": {"ref": "accounts.json ru.A2 contacts[0]", "name": "Лариса Геннадьевна Шишкина", "company": "ООО «Тёплый контур»", "role": "диспетчер (записывает машины на еженедельное окно)",
                           "phone": "+7 907 514-79-22", "first_time": False},
              "named_in_a_line": [{"name": "Виктор Семёнович Агафонов", "ref": "accounts.json ru.A2 contacts[1]", "role": "директор"},
                                  {"slot": 17, "name": "Артём Николаев", "role": "второй приёмщик east: обещал перезвонить и не перезвонил"}]}
    f.staff(16)
    s1 = f.day(wk("Thu", 23, slot=16), "session 1: the first list sent here, for the Monday after")
    f.day(wk("Mon", 22), "«понедельник, 8 июня»")
    f.day(wk("Mon", 16), "the Monday the Largus Т-09 came in; slot 17's shift")
    s2 = f.day(wk("Mon", 16, slot=16), "session 2: found work that waited two days for an answer")
    s3 = f.day(wk("Thu", 6, slot=16), "session 3: a van swapped")
    f.day(wk("Mon", 5), "the Monday of session 3")
    f.day(wk("Mon", 4), "«понедельник, 12 октября»")
    s4 = f.day(wd(16, -1), "session 4: this week's list, for the Monday of week W+1")
    f.day(wk("Mon", -1), "«понедельник, 16 ноября»")
    pump = f.p("12 279,80 ₽", "замена водяного насоса (помпы), класс van, договорная цена", job="water_pump", cls="van", klass="company")
    f.num_("3 мм", "толщина колодок, ниже которой она спрашивает решение; привычка сервиса, не строка каталога")
    f.num_("километров на семьсот", "на сколько Т-08 переходил ТО в сессии 3; придумано")
    f.scenario = {
        "who_writes": "Диспетчер клиента с самым большим числом визитов. Заявку на понедельник она годами передавала по телефону; с запуска системы пишет сюда.",
        "vehicles": "пять машин каждый понедельник к 9:00 из парка в 25 (accounts.json ru.A2): номера названы в каждой сессии",
        "wants": "Подтверждение окна на понедельник; по найденным работам — решение в тот же день.",
        "what_happens": "Сессия 1: первая заявка в мессенджере. Сессия 2: Largus Т-09 стоит с понедельника, второй приёмщик обещал перезвонить по помпе и не перезвонил; Светлана в свою смену извиняется, присылает фото и договорную цену, директор согласует, машина готова к вечеру. Сессия 3: одну машину меняют, пропущенную ставят на другой понедельник. Сессия 4, накануне T: пять машин на следующий понедельник подтверждены, и Светлана задаёт один вопрос, на который ещё не ответили.",
        "facts": {"weekly_slot": "понедельник, 09:00, пять машин (ledger acct.A2.weekly_slot)", "price_class": "договорные цены (A1 и A2; ledger price.hour.company)",
                  "sessions_written": 4, "sessions_in_the_seed": "по одной в неделю с даты G; остальные собираются из этих четырёх: номера из парка, те же два голоса",
                  "rota": "Светлана работает два через два (фаза A); в её выходные заявку принимает слот 17",
                  "public_pages_used": []}}
    f.floating = [fl("на понедельник", s1, "the Monday of week T-22", "на + accusative"), fl("8 июня", s1, "the Monday of week T-22", "date"), fl("До понедельника", s1, "the Monday of week T-22", "до + genitive"),
                  fl("с понедельника", s2, "the Monday of week T-16", "с + genitive"), fl("в понедельник", s2, "the Monday of week T-16", "в + accusative"), fl("сегодня", s2, s2, "adverb"),
                  fl("в понедельник вместе с остальными", s2, "the Monday of week T-15", "в + accusative"),
                  fl("на понедельник", s3, "the Monday of week T-5", "на + accusative"), fl("В понедельник", s3, "the Monday of week T-5", "в + accusative"), fl("всю неделю", s3, "the week T-6", "accusative"),
                  fl("12 октября", s3, "the Monday of week T-4", "date"),
                  fl("На понедельник, 16-е", s4, "the Monday of week W+1 (T+3d)", "на + accusative"), fl("16 ноября", s4, "the Monday of week W+1 (T+3d)", "date"), fl("в понедельник", s4, "the Monday of week W+1 (T+3d)", "в + accusative")]
    c = tg(f, "c1", "east", 1310, "Лариса Шишкина", avatar=pic("view", "герань на подоконнике, за окном двор в снегу"),
           opened_note="the conversation was created by the first session; every later session reopens it")
    # session 1
    c.c(s1 + " 14:20:10", "Светлана, добрый день. Это Лариса Геннадьевна, «Тёплый контур». Виктор Семёнович сказал, заявки на понедельник теперь можно сюда писать, а не звонить?")
    c.c("14:21:05", "На понедельник, 8 июня: Т-02, Т-06, Т-11, Т-15, Т-22. Всем ТО. По Т-15 водитель жалуется, тянет вправо.")
    c.d("14:21:50", "d1", "Лариса Геннадьевна, добрый день! Да, заявки на понедельник можно присылать сюда. На понедельник, 8 июня, к 9:00: Т-02, Т-06, Т-11, Т-15 и Т-22 на ТО; по Т-15 проверим, почему машину тянет вправо.")
    c.s(16, "14:26:30", "Лариса Геннадьевна, добрый день! Да, пишите сюда, так даже удобнее: всё перед глазами. Записала на понедельник, 8 июня, к 9:00 все пять: Т-02, Т-06, Т-11, Т-15 и Т-22, ТО. ГАЗель Т-15 сразу загоним на стенд, посмотрим развал. Как обычно, Лариса Геннадьевна: по готовности каждой машины напишу сюда, а всё, что сверх ТО, сначала согласую с вами.", edit="d1")
    c.c("14:28:40", "Отлично, спасибо")
    c.d("14:29:20", "d2", "Спасибо, Лариса Геннадьевна! До понедельника.")
    c.s(16, "14:30:05", "Спасибо, Лариса Геннадьевна! До понедельника.", use="d2")
    c.label(16, "14:30:20", "юрлицо")
    c.res(16, "14:30:40")
    # session 2
    c.c(s2 + " 10:05:20", "Светлана, добрый день. Ларгус Т-09 с понедельника у вас стоит. Артём в понедельник сказал, что помпа течёт, обещал перезвонить с ценой и пропал. Машина нам нужна.")
    c.d("10:06:05", "d3", "Лариса Геннадьевна, добрый день! Приношу извинения, что вам не перезвонили. Данных по Т-09 у меня сейчас нет: уточню у мастера, что с помпой и сколько стоит замена, и сразу напишу.")
    c.s(16, "10:11:40", "Лариса Геннадьевна, добрый день! Прошу прощения, это наша недоработка: вам должны были перезвонить ещё в понедельник. Т-09 посмотрела сама. Помпа течёт по сальнику, антифриз уходит, фото ниже. Я бы на такой машине людей на объекты не отправляла: встанет с перегревом. Замена помпы по вашему договору — 12 279,80 ₽ с запчастью. Запчасть есть: если подтвердите до 12:00, сегодня к 17:00 машина будет готова. Или делаем в понедельник вместе с остальными. Как решите, Лариса Геннадьевна?",
        files=[{"kind": "image", "file": "T-09_pompa.jpg", "pool": "worn-part-water-pump", "shows": "помпа на двигателе Largus, розовые подтёки антифриза под шкивом, на них показывает отвёртка"}], edit="d3")
    c.c("10:15:10", "Сейчас у Виктора Семёновича спрошу")
    c.d("10:15:50", "d4", "Хорошо, Лариса Геннадьевна, ждём вашего решения.")
    c.c("10:31:20", "Делайте сегодня. Заявка 96/07")
    c.d("10:32:00", "d5", "Спасибо, Лариса Геннадьевна. Меняем помпу на Т-09 сегодня, заявка 96/07, к 17:00 машина будет готова.")
    c.s(16, "10:35:10", "Спасибо, Лариса Геннадьевна, и Виктору Семёновичу спасибо за быстрый ответ. Итак: меняем помпу на Ларгусе Т-09 сегодня, заявка 96/07, 12 279,80 ₽. К 17:00 будет готов, водителю напишу сама, когда можно забирать.", edit="d5",
        late="nothing to answer until the customer came back with the decision: the product counts the wait from «Сейчас спрошу»")
    c.label(16, "10:35:30", "согласование")
    c.c("10:36:40", "Спасибо")
    c.d("10:37:20", "d6", "Пожалуйста, Лариса Геннадьевна!", clear=(16, "10:38:30"))
    c.res(16, "10:38:40")
    # session 3
    c.c(s3 + " 15:40:10", "Светлана, на понедельник замена: вместо Т-08 пришлём Т-13. Восьмой Ларгус всю неделю на объекте в Димитровграде.")
    c.c("15:40:45", "Итого: Т-04, Т-05, Т-13, Т-18, Т-24")
    c.d("15:41:30", "d7", "Принято, Лариса Геннадьевна: вместо Т-08 будет Т-13. На понедельник к 9:00: Т-04, Т-05, Т-13, Т-18 и Т-24.")
    c.s(16, "15:46:20", "Поняла, Лариса Геннадьевна: вместо Т-08 ставлю Т-13. В понедельник к 9:00 ждём Т-04, Т-05, Т-13, Т-18 и Т-24. Восьмой Ларгус уже километров на семьсот переходил ТО, я бы дольше не тянула. Поставить его на понедельник, 12 октября?", edit="d7")
    c.c("15:50:30", "да, ставьте")
    c.d("15:51:10", "d8", "Готово, Лариса Геннадьевна. Т-08 записан на понедельник, 12 октября.")
    c.s(16, "15:53:20", "Записала: Т-08 на понедельник, 12 октября. Накануне напомню.", edit="d8")
    c.res(16, "15:53:40")
    # session 4
    c.c(s4 + " 13:20:15", "Светлана, добрый день. На понедельник, 16-е: Т-03, Т-07, Т-12, Т-16, Т-25.")
    c.c("13:20:50", "По Т-12 водитель говорит, печка еле дует. Не май месяц)")
    c.d("13:21:30", "d9", "Лариса Геннадьевна, добрый день! Принято на понедельник, 16 ноября, к 9:00: Т-03, Т-07, Т-12, Т-16 и Т-25. По Т-12 проверим отопитель.")
    c.s(16, "13:26:40", "Лариса Геннадьевна, добрый день! Записала на понедельник, 16 ноября, к 9:00 все пять: Т-03, Т-07, Т-12, Т-16 и Т-25. Гранту Т-12 посмотрим первой: я бы на своей машине проверила уровень антифриза и термостат, пока морозы не ударили. И один вопрос к вам, Лариса Геннадьевна: на Дастере Т-25 на прошлом ТО задние колодки были уже на исходе. Если в понедельник намеряем меньше 3 мм, меняем сразу или сначала звоню Виктору Семёновичу?", edit="d9")
    c.state_extra = {"waits_on": "the customer: the last public line is the shop's question; a reply cannot be sent on Telegram in a live demo and none is owed (ledger conv.live_demo, conv.open_at_t)",
                     "sessions": [{"n": 1, "day": s1, "ended": "resolved by 16"}, {"n": 2, "day": s2, "ended": "resolved by 16"}, {"n": 3, "day": s3, "ended": "resolved by 16"},
                                  {"n": 4, "day": s4, "ended": "open at T, waiting on the customer"}]}
    c.reads_extra = {"operator_credit": "slot 16: the chat's first answer is hers (6.3 minutes, her ledger row is 6); in the four sessions seven replies, five drafts edited, one sent as it was, one cleared; three resolutions of one chat",
                     "new_dialogs": "Stats counts this chat once, in the week it was created: its later sessions are in no 'new dialogs' figure (design section 10, gap 3)"}
    f.truth = {"reason": "company account: weekly bookings, quotes, documents", "handled": "slot 16; the assistant drafts",
               "outcome": "open at T: next Monday's five vehicles confirmed, one question to the customer unanswered",
               "facts": ["A2 books five vehicles every Monday at 09:00 through this conversation", "found work on Т-09 (a water pump, 12 279,80 at the contract price) waited two days because slot 17 did not call back; slot 16 had it approved in half an hour, request 96/07",
                         "Т-08 missed a Monday and was put on a later one", "at T the list for the Monday of week W+1 is confirmed and the shop waits for an answer about Т-25's rear brake shoes",
                         "nothing is overdue on the shop's side"],
               "questions": ["S1.1", "S5.1"]}
    f.why = ["Лариса Геннадьевна пишет как диспетчер: номера машин, никаких вступлений со второй недели, «Сейчас у Виктора Семёновича спрошу».",
             "Светлана сохраняет факты черновика и добавляет своё: имя-отчество дважды, «я бы на такой машине», выбор из двух, итог.",
             "Сессия 2 — история S5 в переписке: без неё машина два дня ждёт звонка, с ней вопрос решён за полчаса. Вину она берёт на сервис и Артёма не выгораживает.",
             "Черновик, который клиент «обогнал», уходит как «заменён, никто не действовал» (d4); «спасибо», на которое отвечать нечего, она просто убирает (d6)."]
    f.new_facts = ["Заявки на понедельник: неделя T-22: Т-02, Т-06, Т-11, Т-15, Т-22; неделя T-5: Т-04, Т-05, Т-13, Т-18, Т-24 (Т-08 заменён); неделя T-4: добавлен Т-08; неделя W+1: Т-03, Т-07, Т-12, Т-16, Т-25.",
                   "Largus Т-09 приехал в понедельник недели T-16 на ТО, у него нашли течь помпы; слот 17 обещал перезвонить с ценой и не перезвонил; помпу заменили в первый рабочий день слота 16 после этого, 12 279,80 по договору, заявка 96/07.",
                   "ГАЗель Т-15 тянуло вправо (неделя T-22); у Granta Т-12 слабо греет печка (неделя W0); у Duster Т-25 задние колодки были на исходе на прошлом ТО; Т-08 в начале октября работал на объекте в Димитровграде.",
                   "Фото T-09_pompa.jpg (пул 'worn-part-water-pump').", "Картинка контакта: герань на подоконнике, за окном двор в снегу."]
    return f


def f06():
    f = File(CFG, 6, "S6", "web-west-nine-days",
             "Казань: машина ждёт запчасть девятый день, владелец пишет в четвёртый раз",
             "A web chat: the assistant answers first, cannot read the shop system and hands the question over; from the advisor's first line the chat is his and the assistant only drafts. The weak desk in writing: replies under closing time, three or four words, a new date or none, and no reason. Every draft is discarded; two are replaced before anyone looks, because the customer writes again (a '??', a voice message the assistant cannot hear). A private note by the other advisor says what is really going on, and the manager's answer to it is one word. At T the fourth message is unanswered, the chat is Urgent by its wait, and a usable draft sits in the box.")
    f.cast = {"customer": {"ref": "named_customers.json ru.S6_waiting_nine_days", "name": "Айрат Гизатуллин", "first_time": False, "phone": "+7 907 526-98-79"},
              "named_in_a_note": [{"slot": 9, "name": "Павел Мещеряков"}, {"vendor": "V2", "name": "Казань-АвтоСнаб"}]}
    f.staff(23, 24, 22)
    car = f.day(cal(-9, "the car enters waiting_parts; a full open day"), "машину пригнали")
    o8 = f.day(cal(-8, "the day after the car came in"), "насос заказан; ему называют субботу")
    m1 = f.day(cal(-7), "message 1, after closing; slot 23 is off that day")
    r1 = f.day(cal(-6, "the day after message 1"), "the reply to message 1: slot 23's first working day after it; «суббота»")
    m2 = f.day(cal(-5), "message 2; call 15 at 16:10 (card S06: slot 23's 3rd working day before T)")
    mon = f.day(cal(-4, "the day after call 15"), "«понедельник»: the supplier's second date, the day the pump was to come; slot 23 is off")
    m3 = f.day(cal(-3), "message 3; slot 23 is off, slot 24 writes the note; the day promised in call 15")
    d2 = f.day(cal(-2), "the manager's note; the reply to message 3")
    m4 = f.day(cal(-1), "message 4; the missed call and call 16 (card S06: slot 23's last working day before T)")
    f.day(T(), "«завтра девять дней»")
    f.num_("девять дней", "calendar days in waiting_parts at T (ledger s6.waiting_at_t)")
    f.num_("308", "the model")
    f.scenario = {
        "who_writes": "Клиент, чья машина стоит в сервисе на Технической с %s и ждёт запчасть." % car,
        "vehicle": "Peugeot 308, 2011, О972НВ116",
        "waiting_for": "насос электрогидроусилителя руля, заказан у поставщика, который остался у сервиса от прежнего владельца; срок переносили дважды",
        "what_happens": "Он пишет за 7, 5, 3 и 1 день до T и звонит в %s и %s (calls/ru, звонки 15 и 16). Вячеслав отвечает трижды: под закрытие или на следующий день, сроком или ничем. Камила в заметке просит руководителя заказать насос через Ульяновск или сказать клиенту как есть. Руководитель пишет «принял». Ничего не меняется." % (m2, m4),
        "facts": {"car_in": car,
                  "dates_given": ["суббота, %s (при заказе насоса, %s; вне чата)" % (r1, o8), "понедельник, %s (в чате, %s)" % (mon, r1),
                                  "насос в понедельник, машина во вторник, %s (по телефону, %s; ничем не подтверждено)" % (m3, m2)],
                  "each_message_waits_over_hours": 4, "at_t": "девятый день; подтверждённого срока поставки нет",
                  "rota": "Вячеслав (фаза A) работает %s, %s, %s, %s и выходной в %s, %s, %s и в день T; Камила (фаза B) наоборот; руководитель работает по будням" % (r1, m2, d2, m4, m1, mon, m3),
                  "public_pages_used": [],
                  "note": "Ассистент не видит учётную систему: в каждом черновике он пишет, что данных у него нет, и обещает только выяснить. Срок не называет ни разу. Голосовое сообщение он прослушать не может и пишет об этом в черновике."}}
    f.floating = [fl("на завтра", m1, r1, "на + accusative"), fl("завтра", m1, r1, "adverb"), fl("на понедельник", r1, mon, "на + accusative"),
                  fl("в понедельник", m2, mon, "в + accusative"), fl("во вторник", m2, m3, "в + accusative"), fl("сегодня", m2, m2, "adverb"),
                  fl("в воскресенье", m3, m2, "в + accusative"), fl("в понедельник", m3, mon, "в + accusative"), fl("во вторник", m3, m3, "в + accusative"),
                  fl("сегодня", m3, m3, "adverb"), fl("В четверг", m3, o8, "в + accusative"),
                  fl("субботу", m3, r1, "accusative"), fl("на понедельник", m3, mon, "на + accusative"), fl("на следующей неделе", m3, "T+3d to T+9d", "на + prepositional"),
                  fl("вторник", m3, m3, "accusative"), fl("завтра", m4, "T", "adverb"), fl("Завтра до обеда", m4, "T", "adverb")]
    c = web(f, "c1", "west", 733, 6)
    c.c(m1 + " 20:41:10", "добрый вечер. гизатуллин, пежо 308 у вас на технической стоит. насос на завтра обещали, все в силе?")
    c.a("20:41:34", HELLO + "Сейчас сервис закрыт, откроемся в 9:00. Заказ-наряды я не вижу, поэтому сказать, придёт ли насос завтра, не могу. Передам ваш вопрос мастеру-приёмщику на Технической, он ответит. Напишите, пожалуйста, как к вам обращаться и номер телефона.")
    c.c("20:42:15", "айрат 89075269879")
    c.a("20:42:38", "Спасибо, Айрат. Вопрос передал, с вами свяжутся в ближайшее время.")
    c.h("20:42:39", "escalation", "Айрат", "+7 907 526-98-79", "Техническая",
        "Peugeot 308, стоит в сервисе на Технической, ждёт насос. Фамилия Гизатуллин. Ему обещали насос на завтра, спрашивает, в силе ли срок. Заказ-наряды я не вижу, поэтому ни статуса, ни срока не называл.",
        "west", "%s 20:00, закрытие следующего рабочего дня" % r1)
    c.s(23, r1 + " 19:05:20", "не пришло. поставщик перенёс на понедельник", late="story: card S06, each message waits over four hours")
    c.c(m2 + " 15:02:30", "в понедельник точно будет? мне во вторник в челны ехать")
    c.d("15:03:15", "d1", "Айрат, здравствуйте. Подтверждения от поставщика у меня пока нет. Уточню и напишу вам сегодня до закрытия.")
    c.c("15:40:20", "??")
    c.d("15:41:05", "d2", "Айрат, прошу прощения за ожидание. Уточняю у поставщика, будет ли насос в понедельник, и сегодня до 20:00 напишу вам точный ответ.")
    c.out("16:10", "calls", "он звонит, не дождавшись ответа в чате; Вячеслав говорит, что насос придёт завтра и во вторник машину можно забрать (calls/ru, звонок 15: wrong_promise, 25.0)")
    c.s(23, "19:31:40", "должны привезти", late="story: card S06, each message waits over four hours")
    c.c(m3 + " 16:15:10", "Вячеслав, вы в воскресенье по телефону сказали насос в понедельник придёт, во вторник заберу. пришёл?")
    c.d("16:15:55", "d3", "Айрат, приношу извинения: срок, который вам назвали, у меня пока не подтверждён. Сегодня выясню, где насос, и перезвоню вам.")
    c.c("16:17:25", "", files=[{"kind": "audio", "file": "voice.ogg", "pool": "voice-stub-ru-3", "seconds": 41,
                                 "shows": "голосовое, 0:41: мужчина говорит раздражённо, про эвакуатор и другой сервис; слова в данных не хранятся, в чате на сайте это прикреплённый аудиофайл"}])
    c.d("16:18:10", "d4", "Айрат, приношу извинения: сроки, которые вам называли, не выдержаны. Голосовое сообщение я прослушать не могу, напишите, пожалуйста, текстом. Новую дату называть не буду, пока нет подтверждения от поставщика. Сегодня выясню, где насос, и перезвоню вам.")
    c.n(24, "16:40:30", "@Ринат Фаридович Галиев клиент по 308-му пишет третий раз и уже звонил. В четверг, когда заказывали насос ЭГУР, АвтоСнаб обещал субботу, потом перенёс на понедельник, сегодня мне сказали «на следующей неделе», трек-номер не дают. А Слава в воскресенье по телефону пообещал ему вторник. Может, закажем через Пашу Мещерякова в Ульяновске? Или хотя бы скажем человеку как есть. Он в голосовом уже про эвакуатор говорит, послушайте.", mentions=[22])
    c.n(22, d2 + " 09:15:40", "принял")
    c.s(23, "09:40:15", "не пришло еще. как придёт наберу", late="story: card S06, each message waits over four hours")
    c.out(m4 + " 10:05", "calls", "он звонит, трубку не берут: пропущенный, первый стол 302; закрыт звонком 16 (got_through)")
    c.out("15:25", "calls", "он дозванивается (calls/ru, звонок 16: existing job, no score; repeat_caller, complaint; автопровал dropped_customer: его вопрос про «то, второе» не уточняют, и он уходит без ответа)")
    c.c("17:22:10", "четвертый раз пишу. завтра девять дней как машина у вас")
    c.c("17:22:30", "скажите прямо, насос вообще едет или нет? я на такси уже больше чем на ремонт потратил")
    c.d("17:23:15", "d5", "Айрат, вы правы, и я приношу извинения. Три срока, которые мы вам назвали, сорваны. Подтверждённой даты поставки у меня нет, и четвёртую наугад называть не буду. Завтра до обеда вам позвонит руководитель сервиса и скажет, где насос и что мы можем сделать.")
    c.state_extra = {"live_demo": "a web chat, so the waiting draft can be edited and sent in a live demo (ledger conv.live_demo, conv.open_at_t)",
                     "shown_why": "the wait: 158 working minutes on the last open day and the first half-hour of T at the shop",
                     "owner_on_shift_at_t": False}
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's (the assistant wrote it); slot 23: his first line {first} working minutes after the shop opened on the day after the hand-off, three replies, three drafts discarded, two replaced unseen, nothing resolved; slots 24 and 22 wrote notes only, which count nowhere"}
    f.truth = {"reason": "is my car ready, has the part come", "handled": "assistant first, handed over (escalation), slot 23; notes by 24 and 22",
               "outcome": "open at T, owned by slot 23, urgent by its wait, unread, one unsent draft",
               "facts": ["four messages, 7, 5, 3 and 1 days before T, each waiting over four hours for a person's reply; the fourth unanswered at T",
                         "slot 23 wrote «поставщик перенёс на понедельник», then «должны привезти», then «как придёт наберу»",
                         "the Tuesday promise was made in call 15, on the Sunday, and had nothing behind it; the car is still waiting at T",
                         "slot 24 told the manager in a note that the supplier promised Saturday, moved it to Monday and now says next week, and proposed ordering through the home shops; slot 22 answered «принял»",
                         "he says he has spent more on taxis than the repair costs; in a voice message he speaks of a tow truck"],
               "questions": ["S6.5", "S6.2"]}
    f.why = ["Три ответа Вячеслава — четырнадцать слов на все три, без заглавных букв и без причины.",
             "Клиент начинает с «добрый вечер» и фамилии, а заканчивает счётом дней и денег на такси; в тексте не ругается, ругается в голосовом.",
             "Поставщик назван только в заметке Камилы, и через строку под ней стоит «принял».",
             "Черновики становятся лучше, чем злее клиент, а строки исходов показывают, что ни одним не воспользовались."]
    f.new_facts = ["Первый срок, суббота, ему назвали в день заказа насоса (на следующий день после приёма машины), вне чата и вне написанных звонков (звонок 15: «Мне сначала сказали — в субботу»).",
                   "ERP: заказ поставщику на насос ЭГУР обещан на субботу (6 дней до T), перенесён на понедельник (4 дня до T); в день третьего сообщения поставщик говорит «на следующей неделе» и не даёт трек-номер.",
                   "Первое сообщение пришло в 20:41, после закрытия, в день смены слота 24; первым ответил слот 23 на следующий день, в свою смену, и чат стал его.",
                   "Во вторник ему нужно было ехать в Набережные Челны; на такси он, по его словам, потратил больше, чем стоит ремонт.",
                   "Голосовое сообщение 0:41 (пул 'voice-stub-ru-3'): в чате на сайте это аудиофайл.",
                   "Пропущенный звонок (10:05) и звонок 16 (15:25) стоят в часы набора звонков; четвёртое сообщение написано после звонка 16.",
                   "Звонок 15 приходится на воскресенье, пятый день до T: это смена слота 23 и день второго сообщения; он звонит в 16:10, не дождавшись ответа в чате, а «должны привезти» Вячеслав пишет уже после звонка."]
    return f


def f07():
    f = File(CFG, 7, "S13", "web-stocktake-question",
             "Про день инвентаризации спрашивают на сайте: ассистент отвечает сам",
             "Web chat, assistant sends: two customer lines, two answers from the dated hours, no person. The chat stays the assistant's: pending at T, in All with the Agent mark, owed nothing.")
    f.cast = {"customer": {"name": "Посетитель сайта", "invented": True, "first_time": True}}
    f.cast["staff"] = []
    q = f.day(wk("Mon", 0), "the customer's question (card S13: the Monday of week W0 when it is before T)")
    st = f.day(wk("Thu", -1), "the stocktake: every shop closes at 12:00")
    f.scenario = {
        "who_writes": "Человек, который хочет поменять масло в определённый день после обеда.",
        "what_happens": "Он спрашивает, работает ли сервис 19-го после обеда. Ассистент отвечает: нет, почему и когда открыто; предлагает передать заявку на утро и не настаивает, когда отказываются.",
        "facts": {"stocktake": "четверг недели W+1: все сервисы работают до 12:00 (card S13; ledger site.stocktake). Номинально четверг, 19 ноября 2026.",
                  "hours": "9:00–20:00, без выходных", "public_pages_used": ["часы работы и адреса, с датой инвентаризации"]}}
    f.floating = [fl("19го", q, st, "date"), fl("19 ноября", q, st, "date"), fl("в пятницу", q, "not fixed: he may mean either Friday, and the assistant does not guess", "в + accusative"),
                  fl("По пятницам", q, "any Friday", "по + dative")]
    c = web(f, "c1", "main", 388, 7)
    c.c(q + " 13:22:40", "добрый день. 19го после обеда работаете? масло поменять хотел")
    c.a("13:23:02", "Добрый день! 19 ноября все три сервиса «Ермак-Сервис» работают до 12:00: во второй половине дня у нас инвентаризация. С 9:00 до 12:00 принимаем как обычно, в остальные дни работаем с 9:00 до 20:00. Передать мастерам, чтобы вас записали на утро?")
    c.c("13:24:15", "не, с утра не могу. в пятницу тогда заеду")
    c.a("13:24:38", "Хорошо! По пятницам работаем как обычно, с 9:00 до 20:00. Хорошего дня!")
    c.state_extra = {"shown_as": "in All with the Agent mark; not in the Queue: nobody is owed an answer",
                     "later": "Chatwoot resolves it after 7 silent days, three days after T: not in the data"}
    c.reads_extra = {"operator_credit": "nobody: the assistant is not an operator"}
    f.truth = {"reason": "hours, address, do you work on this", "handled": "the assistant alone", "outcome": "answered; pending at T, the assistant's",
               "facts": ["no: every shop closes at 12:00 that day for the stocktake", "the morning is open from 9:00", "a hand-over for a morning time was offered and declined"],
               "questions": ["S13.1", "S13.3"]}
    f.why = ["Такие переписки в жизни именно такой длины.", "Ассистент предлагает передать заявку на утро и не настаивает, когда отказываются.",
             "Ответ на вопрос «работаем ли мы в этот день после обеда» есть здесь словами ассистента, а в файле 08 — словами человека."]
    f.new_facts = []
    f.extra = {"disagrees_with": "DESIGN.md section 6 puts this chat on the 2nd full open day before T; card S13 puts it on the Monday of week W0 when that day is before T. The card is followed. The card's footprint says 'resolved'; the ledger (conv.open_at_t) and the design name it as pending at T, and it is pending here: under seven silent days have passed."}
    return f


def f08():
    f = File(CFG, 8, "S13", "vk-stocktake-regular",
             "Про день инвентаризации спрашивают во «ВКонтакте»: ассистент готовит черновик, Светлана правит и отправляет",
             "VK, a drafts-only channel: the draft is correct and plain; the east shop's lead advisor keeps its facts and rewrites it in her own voice, twice. Both outcomes are sent_edited.")
    f.cast = {"customer": {"name": "Марина Захарова", "invented": True, "first_time": False,
                           "note": "постоянная клиентка сервиса в Новом городе; Volkswagen Polo 2017; задние колодки ей рекомендовали на прошлом ТО"}}
    f.staff(16)
    q = f.day(wd(16, -1), "slot 16's last working day before T")
    st = f.day(wk("Thu", -1), "the stocktake: every shop closes at 12:00")
    mon = f.day(wd(16, 2, note="card S13: her last working day before her week off, the Monday of week W+1 for the nominal T"), "her appointment, 14:00")
    sat = f.day(wk("Sat", -1), "the first day after the stocktake on which slot 17 has the desk: the other time she is offered")
    f.scenario = {
        "who_writes": "Постоянная клиентка, пишет Светлане по имени.",
        "vehicle": "Volkswagen Polo 2017",
        "what_happens": "Она просит записать её на день инвентаризации после обеда. Из «не работаем» в черновике Светлана делает два времени на выбор: понедельник у себя или суббота у Артёма, потому что с четверга она неделю не работает. Вторым сообщением подводит итог.",
        "facts": {"stocktake": "четверг недели W+1: все сервисы работают до 12:00 (card S13; ledger site.stocktake)", "hours": "9:00–20:00, без выходных", "address_east": "10-й Инженерный проезд, 30",
                  "booked": "понедельник недели W+1, 14:00, east, принимает слот 16; запись в ERP, источник messenger", "public_pages_used": ["часы работы и адреса, с датой инвентаризации"],
                  "rota": "понедельник недели W+1 — последний рабочий день Светланы перед неделей, на которую она просит отпуск (S5, с четверга); решения по заявке нет, но на эти дни она никого на себя не записывает. Суббота недели W+1 — смена слота 17"}}
    f.floating = [fl("в четверг 19го", q, st, "в + accusative, date"), fl("В четверг, 19 ноября", q, st, "в + accusative, date"), fl("В четверг, 19-го", q, st, "в + accusative, date"),
                  fl("в понедельник, 16-го", q, mon, "в + accusative, date"), fl("в субботу, 21-го", q, sat, "в + accusative, date"), fl("с четверга", q, st, "с + genitive"),
                  fl("в понедельник в 14", q, mon, "в + accusative"),
                  fl("Понедельник, 16 ноября", q, mon, "nominative, date"), fl("понедельник, 16 ноября", q, mon, "nominative, date")]
    c = vk(f, "c1", "east", 417, "Марина Захарова", avatar=pic("view", "набережная Волги зимой, фонари, людей нет"),
           opened_note="in the full seed this is a later session of her one VK conversation; here it stands alone")
    c.c(q + " 10:41:20", "Светлана здравствуйте) а в четверг 19го после обеда можно подъехать? задние колодки, вы говорили пора")
    c.d("10:42:05", "d1", "Здравствуйте! В четверг, 19 ноября, сервис работает до 12:00: во второй половине дня инвентаризация, принять машину после обеда не получится. С 9:00 до 12:00 работаем как обычно, в остальные дни с 9:00 до 20:00. Подойдёт ли вам утро?")
    c.s(16, "10:47:50", "Марина, здравствуйте! В четверг, 19-го, мы работаем только до 12: инвентаризация, после обеда не примем. Я бы на своей машине с задними колодками до конца месяца не тянула. Могу принять вас в понедельник, 16-го, в 14:00. Или после инвентаризации, в субботу, 21-го, но тогда вас примет Артём: меня с четверга неделю не будет. Как вам удобнее, Марина?", edit="d1")
    c.c("10:58:30", "в понедельник в 14 давайте")
    c.d("10:59:15", "d2", "Хорошо, Марина. Понедельник, 16 ноября, 14:00. Ждём вас!")
    c.s(16, "11:01:40", "Записала, Марина: понедельник, 16 ноября, 14:00, задние колодки, Volkswagen Polo. Мы на 10-м Инженерном проезде, 30. Займёт около часа, можно подождать у нас. Принимаю я. До встречи!", edit="d2")
    c.label(16, "11:02:00", "запись")
    c.res(16, "11:02:20")
    c.reads_extra = {"operator_credit": "slot 16: first answer {first} minutes (her ledger row is 6), two replies, two drafts edited, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 16; the assistant drafts", "outcome": "записана на понедельник недели W+1, 14:00, east, к слоту 16: до инвентаризации и до её недели отпуска; закрыт слотом 16",
               "facts": ["the shop closes at 12:00 on the stocktake day, so the afternoon she asked for is not possible", "slot 16 offered her own last working day before her week off, the Monday of week W+1, at 14:00, or the Saturday after the stocktake with slot 17",
                         "she chose the Monday at 14:00; slot 16 books nobody to herself inside the week she has asked off"],
               "questions": ["S13.1"]}
    f.why = ["В черновике и в ответе Светланы одни и те же факты. У неё дважды имя клиентки, «я бы на своей машине», два времени на выбор.",
             "Второе сообщение — итог: день, время, работа, машина, адрес, кто принимает."]
    f.new_facts = ["Марина Захарова, постоянная клиентка east, Volkswagen Polo 2017 (в образце была Kia Rio 2017: такая же машина в named_customers.json записана на другую Марину того же сервиса), задние колодки рекомендованы на прошлом ТО; запись на понедельник недели W+1, 14:00, принимает слот 16.",
                   "«Принимаю я» сказано про понедельник, её последний рабочий день перед неделей отпуска (S5); на дни внутри этой недели она никого на себя не записывает и вторым временем называет субботу у Артёма (слот 17), его смену.",
                   "Картинка контакта: набережная Волги зимой."]
    return f


FILES = [f01, f02, f03, f04, f05, f06, f07, f08]
