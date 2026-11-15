# -*- coding: utf-8 -*-
"""Russian conversations 9 to 27: two per advisor (slots 5, 6, 7, 16, 17, 22, 23, 24) and three for rule R13.
Written in Russian from the advisors' voice notes, not from the English set: other customers, cars and jobs."""
from srclib import *

CFG = "ru"
HELLO = "Здравствуйте! Я виртуальный помощник «Ермак-Сервиса». "
SAID = "Заявку передал, с вами свяжутся в ближайшее время."
SAID_Q = "Вопрос передал, с вами свяжутся в ближайшее время."
LATER = "in the full seed this is a later session of the customer's one conversation on this channel; here it stands alone"


def fl(word, said_on, day, form=None):
    row = dict(word=word, said_on=said_on, day=day)
    if form:
        row["form"] = form
    return row


def cust(name, note, first_time=False, phone=None):
    row = {"name": name, "invented": True, "first_time": first_time, "note": note}
    if phone:
        row["phone"] = phone
    return row


def f09():
    f = File(CFG, 9, "people", "p05-telegram-itog",
             "Старший приёмщик флагмана в Telegram: готова ли машина и почему сумма больше",
             "Slot 5 in writing: a first reply after 13 minutes, typed in a hurry with no capitals, the total and the pick-up time in one line, «наберите меня, так быстрее» when a question takes more than a line. He writes his own text over two drafts and sends the third as it was. He does not resolve; Chatwoot does, a week later.")
    f.cast = {"customer": cust("Ильнур Сабиров", "постоянный клиент сервиса на Московском шоссе; Renault Duster 2014; в этот день меняли передний ступичный подшипник")}
    f.staff(5)
    d = f.day(wk("Thu", 18, slot=5))
    f.day(wk("Thu", 18, slot=5, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("7900", "замена подшипника передней ступицы, класс suv, стандартная запчасть, по прайсу (7 902); так он её округляет", job="wheel_bearing", cls="suv")
    f.p("7 902 ₽", "то же, точно", job="wheel_bearing", cls="suv")
    f.p("8 019,99", "то же с расходными материалами: к оплате, НДС в том числе", job="wheel_bearing", cls="suv", supplies=True)
    f.psup("117,99 ₽", "расходные материалы по этой работе: разница между названным по телефону и счётом", "wheel_bearing", cls="suv")
    f.scenario = {"who_writes": "Постоянный клиент, с работы, про машину, которую оставил утром.", "vehicle": "Renault Duster 2014",
                  "what_happens": "Спрашивает, готова ли машина. Дмитрий пишет, что сделали, сколько к оплате и до скольки забирать. Сумма больше той, что звучала по телефону; Дмитрий в одну строку объясняет почему и предлагает созвониться. Клиент приедет к семи.",
                  "facts": {"main_line": "+7 (8422) 10-40-40 (phones.md)", "public_pages_used": []}}
    f.floating = []
    c = tg(f, "c1", "main", 2114, "Ильнур", avatar=pic("car", "белый Renault Duster на грунтовой дороге у реки", matches="Renault Duster 2014"), opened_note=LATER)
    c.c(d + " 16:20:10", "Дмитрий добрый день. дастер готов?")
    c.d("16:20:55", "d1", "Здравствуйте! Данных по вашей машине у меня сейчас нет. Уточню у мастера и сразу напишу.")
    c.s(5, "16:33:40", "готов. подшипник ступичный поменяли, передний левый, гул ушел. к оплате 8 019,99. забирать до 20 00")
    c.c("16:36:05", "а почему больше. по телефону говорили 7900")
    c.d("16:36:50", "d2", "7 902 ₽ — это работа и запчасть. К ним добавляются расходные материалы, 117,99 ₽, поэтому к оплате 8 019,99 ₽. Приношу извинения, если по телефону это не прозвучало.")
    c.s(5, "16:44:30", "7900 это без расходников. работа та же, ничего не добавляли. наберите меня, так быстрее, 10-40-40")
    c.c("16:47:10", "да ладно, понял. к 7 подъеду")
    c.d("16:47:50", "d3", "Хорошо, ждём вас к 19:00.")
    c.s(5, "16:52:20", "Хорошо, ждём вас к 19:00.", use="d3")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 5: first answer {first} minutes (his ledger row is 14), three replies, two drafts discarded and one sent as it was, nothing resolved"}
    f.truth = {"reason": "is my car ready, has the part come", "handled": "slot 5; the assistant drafts", "outcome": "готов; 8 019,99 к оплате; закрыт по 7 дням тишины",
               "facts": ["the wheel-bearing job is 7 902 at list for class suv; with shop supplies (117,99) 8 019,99 to pay, VAT inside", "the customer had heard the figure without shop supplies on the phone", "slot 5 did not resolve the chat"], "questions": []}
    f.why = ["«гул ушел. к оплате 8 019,99. забирать до 20 00»: без заглавных, наспех, и всё равно две вещи, которые нужны клиенту, — итог и время.",
             "Второй черновик объясняет счёт лучше, чем он сам; он пишет своё и зовёт к телефону.", "Третий черновик ему подходит, и он его отправляет."]
    f.new_facts = ["Ильнур Сабиров (в Telegram «Ильнур»), Renault Duster 2014: замена переднего левого ступичного подшипника на main в первый рабочий день слота 5 начиная с четверга недели T-18: 7 902 по прайсу, 8 019,99 с расходными материалами (НДС в том числе); утром по телефону ему назвали сумму без расходных материалов.",
                   "Картинка контакта: белый Duster у реки."]
    return f


def f10():
    f = File(CFG, 10, "people", "p05-avito-sceplenie",
             "Авито: сколько стоит сцепление на Гранту, и можно ли со своим комплектом",
             "Avito is a listing, so the first question is a price. The assistant drafts it from the price list with one question back, and slot 5 takes the draft as it is. The second answer he types himself: lower case, a mechanic's tip, and «наберите меня». The last draft goes out untouched; he labels and resolves this one.")
    f.cast = {"customer": cust("Руслан", "пишет по объявлению сервиса; LADA Granta 2018, 8 клапанов; свой комплект сцепления", first_time=True)}
    f.staff(5)
    d = f.day(wk("Mon", 8, slot=5))
    f.p("26 550 ₽", "замена сцепления в сборе, класс car, стандартный комплект", job="clutch_kit")
    f.plab("10 450 ₽", "только работа по замене сцепления: 5,5 нормо-часа", "clutch_kit")
    f.plab("10450", "то же, как он пишет", "clutch_kit")
    f.num_("5,5 нормо-часа", "нормо-часы замены сцепления по каталогу")
    f.scenario = {"who_writes": "Человек по объявлению, с телефона.", "vehicle": "LADA Granta 2018, 8 кл.",
                  "what_happens": "Цена из прайса и встречный вопрос — черновик, отправленный как есть. Потом: можно ли со своим комплектом. Дмитрий отвечает сам, советует проверить выжимной и просит позвонить.",
                  "facts": {"listing": "объявление сервиса в категории «Услуги»", "note": "Номер клиента на Авито не виден; запись будет по звонку.", "public_pages_used": []}}
    f.floating = [fl("после обеда", d, d, "после + genitive")]
    c = avito(f, "c1", "main", 204, "Руслан", 41, "Замена сцепления: Granta, Vesta, Largus, Logan. Московское шоссе", opened_note="a new Avito chat: one per listing and buyer")
    c.c(d + " 11:14:20", "Здравствуйте. Ещё актуально? Сколько сцепление поменять на гранте")
    c.d("11:15:05", "d1", "Здравствуйте! Да, актуально. Замена сцепления в сборе (корзина, диск, выжимной подшипник) на Granta стоит 26 550 ₽ с запчастями. Подскажите год выпуска и какой двигатель, 8 или 16 клапанов?")
    c.s(5, "11:29:10", "Здравствуйте! Да, актуально. Замена сцепления в сборе (корзина, диск, выжимной подшипник) на Granta стоит 26 550 ₽ с запчастями. Подскажите год выпуска и какой двигатель, 8 или 16 клапанов?", use="d1")
    c.c("11:33:40", "2018, 8кл. а со своими запчастями можно? у меня комплект валео лежит")
    c.d("11:34:25", "d2", "Со своим комплектом можно: тогда оплачивается только работа, 10 450 ₽ (5,5 нормо-часа). Когда вам удобно подъехать?")
    c.s(5, "11:47:30", "можно со своим. работа 10450. только гляньте чтоб выжимной в комплекте был, а то бывает без него. наберите меня, запишу, так быстрее: 8422 10-40-40")
    c.c("11:52:10", "ок, наберу после обеда")
    c.d("11:52:50", "d3", "Хорошо, будем ждать звонка.")
    c.s(5, "11:58:00", "Хорошо, будем ждать звонка.", use="d3")
    c.label(5, "11:58:20", "цена")
    c.res(5, "11:58:40")
    c.reads_extra = {"operator_credit": "slot 5: first answer {first} minutes (his ledger row is 14), three replies, two drafts sent as they were and one discarded, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 5; the assistant drafts", "outcome": "цена названа; запись — по звонку клиента; закрыт слотом 5",
               "facts": ["a clutch set fitted is 26 550 at list; labour alone 10 450 when the customer brings the parts", "slot 5 asked him to phone; no time was fixed in the chat"], "questions": []}
    f.why = ["На Авито первым идёт вопрос «сколько», и черновик на него отвечает лучше, чем успел бы человек у стойки.",
             "Своё у Дмитрия — совет механика: «гляньте чтоб выжимной в комплекте был».", "«наберите меня, так быстрее»: чат для него — способ договориться о звонке."]
    f.new_facts = ["Объявление сервиса на Авито «Замена сцепления: Granta, Vesta, Largus, Logan. Московское шоссе» (идентификаторы под .example).",
                   "Руслан, LADA Granta 2018, 8 кл., свой комплект сцепления Valeo; запись — по его звонку (звонок в набор звонков не входит).", "У контакта нет картинки."]
    return f


def f11():
    f = File(CFG, 11, "people", "p06-vk-zapis-na-maslo",
             "Алина во «ВКонтакте»: запись на замену масла, сначала время, потом цена",
             "Slot 6 in writing: four minutes to a first reply, correct and complete, two times before the price, what is included, the address in the confirmation. She edits two drafts and sends the third as it was; labels and resolves.")
    f.cast = {"customer": cust("Ксения Мартынова", "LADA Vesta 2019; в сервисе впервые", first_time=True)}
    f.staff(6)
    d = f.day(wk("Tue", 11, slot=6))
    f.day(wk("Sat", 11), "«эта суббота»")
    f.p("6 700 ₽", "замена масла в двигателе и масляного фильтра, класс car, стандартные масло и фильтр", job="oil_service")
    f.scenario = {"who_writes": "Новая клиентка, из сообщества сервиса во «ВКонтакте».", "vehicle": "LADA Vesta 2019",
                  "what_happens": "Просит записать на субботу. Алина предлагает два времени, называет цену и что в неё входит; на вопрос про масло отвечает и подтверждает запись с адресом.",
                  "facts": {"booked": "суббота недели T-11, 10:00, main", "oil": "Лукойл Genesis Armortech 5W-40 и фильтр MANN-FILTER: стандартный вариант каталога", "public_pages_used": []}}
    f.floating = [fl("на эту субботу", d, "the Saturday of week T-11", "на + accusative"), fl("В субботу", d, "the Saturday of week T-11", "в + accusative"), fl("на субботу, 10:00", d, "the Saturday of week T-11", "на + accusative"),
                  fl("До субботы", d, "the Saturday of week T-11", "до + genitive")]
    c = vk(f, "c1", "main", 2231, "Ксения Мартынова", avatar=pic("pet", "рыжий кот спит на подоконнике"), opened_note="her first message to the community: a new conversation")
    c.c(d + " 12:40:15", "Добрый день! Подскажите, можно к вам на замену масла записаться на эту субботу? веста 2019")
    c.d("12:41:00", "d1", "Добрый день! Да, в субботу работаем с 9:00 до 20:00. Замена масла и масляного фильтра на Vesta стоит 6 700 ₽ с маслом и фильтром. На какое время вам удобно?")
    c.s(6, "12:44:30", "Ксения, добрый день! Да, конечно. В субботу могу записать вас на 10:00 или на 15:30, по времени это минут сорок. Замена масла с фильтром на Весту выйдет 6 700 ₽, масло и фильтр наши. Какое время вам удобнее?", edit="d1")
    c.c("12:47:05", "на 10. а масло какое льёте?")
    c.d("12:47:45", "d2", "В стоимость входит масло Лукойл Genesis Armortech 5W-40 и фильтр MANN-FILTER. Записать вас на субботу, 10:00?")
    c.s(6, "12:49:10", "Лукойл Genesis Armortech 5W-40 и фильтр MANN, это входит в цену. Записала вас на субботу, 10:00, Московское шоссе, 40. Если планы поменяются, просто напишите сюда.", edit="d2")
    c.c("12:50:30", "спасибо!")
    c.d("12:51:10", "d3", "Пожалуйста, Ксения! До субботы.")
    c.s(6, "12:51:50", "Пожалуйста, Ксения! До субботы.", use="d3")
    c.label(6, "12:52:10", "запись")
    c.res(6, "12:52:30")
    c.reads_extra = {"operator_credit": "slot 6: first answer {first} minutes (her ledger row is 4), three replies, two drafts edited and one sent as it was, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 6; the assistant drafts", "outcome": "записана на субботу, 10:00, main; закрыт слотом 6",
               "facts": ["two times were offered before the price", "the price is 6 700 with oil and filter", "the confirmation carries the address"], "questions": []}
    f.why = ["Черновик начинает с цены, Алина — с времени: так её научили звонки (история S4).", "В подтверждении есть адрес: его чаще всего и забывают.", "Смайлика нет ни одного; восклицательный знак — один на сообщение."]
    f.new_facts = ["Ксения Мартынова, LADA Vesta 2019: замена масла на main в субботу недели T-11, 10:00.", "Картинка контакта: рыжий кот на подоконнике."]
    return f


def f12():
    f = File(CFG, 12, "people", "p06-telegram-naydennye-raboty",
             "Алина в Telegram: при ТО нашли две работы, одна согласована, от другой отказались",
             "Found work on a messenger. Slot 6 answers in under five minutes with photos, the urgent finding first with its price and what it does, the second offered without pressure. The customer takes one; the assistant's summary of the decision goes out as it was. A closing 'еду' needs no answer, so she clears the draft, labels and resolves.")
    f.cast = {"customer": cust("Эльвира Насибуллина", "клиентка сервиса на Московском шоссе; Kia Sportage 2017, приехала на ТО")}
    f.staff(6)
    d = f.day(wk("Fri", 5, slot=6))
    f.p("4 463 ₽", "замена стоек стабилизатора передних, пара, класс suv", job="sway_bar_links", cls="suv")
    f.p("3 403 ₽", "замена щёток стеклоочистителя, класс suv", job="wiper_blades", cls="suv")
    f.scenario = {"who_writes": "Клиентка, чья машина с утра на ТО.", "vehicle": "Kia Sportage 2017",
                  "what_happens": "Спрашивает, не нашли ли чего. Нашли: разбитые стойки стабилизатора и щётки, которые полосят. Стойки она согласует, щётки муж купит сам.",
                  "facts": {"approved": "стойки стабилизатора, 4 463", "declined": "щётки стеклоочистителя, 3 403", "public_pages_used": []}}
    f.floating = [fl("сегодня", d, d, "adverb")]
    c = tg(f, "c1", "main", 2291, "Эльвира", opened_note=LATER)
    c.c(d + " 13:10:20", "Алина, здравствуйте. как там мой спортейдж, что-то нашли?")
    c.d("13:11:05", "d1", "Эльвира, здравствуйте! Данных по вашей машине у меня сейчас нет. Уточню у мастера и сразу напишу.")
    c.s(6, "13:14:50", "Эльвира, здравствуйте! Как раз собиралась вам писать. ТО сделали, при осмотре нашли две вещи, фото ниже. Стойки стабилизатора спереди разбиты, это они стучат на кочках: 4 463 ₽ за пару с работой, минут сорок. И щётки стеклоочистителя полосят, 3 403 ₽, но с ними можно и подождать. Делаем что-то из этого сегодня?",
        files=[{"kind": "image", "file": "sportage_stoyka.jpg", "pool": "worn-part-sway-link", "shows": "стойка стабилизатора в руке механика, пыльник порван, палец шарнира болтается"},
               {"kind": "image", "file": "sportage_schetki.jpg", "pool": "worn-wiper", "shows": "лобовое стекло под дождём, от щётки остаются полосы"}], edit="d1")
    c.c("13:19:30", "стойки делайте. щётки муж сам купит)")
    c.d("13:20:10", "d2", "Хорошо, Эльвира. Стойки стабилизатора меняем сегодня, 4 463 ₽, щётки не трогаем. Напишем, когда машина будет готова.")
    c.s(6, "13:21:30", "Хорошо, Эльвира. Стойки стабилизатора меняем сегодня, 4 463 ₽, щётки не трогаем. Напишем, когда машина будет готова.", use="d2")
    c.label(6, "13:21:50", "согласование")
    c.s(6, "15:02:10", "Эльвира, машина готова, можно забирать. Мы до 20:00.")
    c.c("15:05:20", "еду")
    c.d("15:06:00", "d3", "Ждём вас!", clear=(6, "15:07:10"))
    c.res(6, "15:07:20")
    c.reads_extra = {"operator_credit": "slot 6: first answer {first} minutes (her ledger row is 4), three replies, one draft edited, one sent as it was, one cleared, one resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "slot 6; the assistant drafts", "outcome": "стойки стабилизатора согласованы (4 463), щётки — отказ; закрыт слотом 6",
               "facts": ["two findings, each with a photo", "approved: front sway bar links; declined: wiper blades", "ready the same afternoon"], "questions": []}
    f.why = ["Первый черновик пуст, потому что ассистент не видит машину; Алина оставляет приветствие и пишет остальное.", "Срочное — первым, с причиной и ценой; второе предложено, а не навязано.", "На «еду» отвечать нечего: черновик она убирает."]
    f.new_facts = ["Эльвира Насибуллина (в Telegram «Эльвира»), Kia Sportage 2017, main, первый рабочий день слота 6 начиная с пятницы недели T-5: ТО; стойки стабилизатора согласованы, 4 463; щётки стеклоочистителя — отказ, 3 403.",
                   "Фото sportage_stoyka.jpg и sportage_schetki.jpg (пулы 'worn-part-sway-link', 'worn-wiper').", "У контакта нет картинки."]
    return f


def f13():
    f = File(CFG, 13, "people", "p07-avito-pervyy-iz-dvuh",
             "Новичок на Авито: два вопроса в одном сообщении, ответ на первый",
             "Slot 7 in writing: polite, short, «Да-да», an exclamation mark, and of two questions the first. He sends what he is given: three drafts go out untouched, and the one time he types for himself he drops half the question, so the customer has to ask again. He resolves.")
    f.cast = {"customer": cust("Саня", "пишет по объявлению; Renault Logan 2014, хрустит левый наружный ШРУС", first_time=True)}
    f.staff(7, s7={"weeks_in_the_job": 3})
    d = f.day(wk("Thu", 12, slot=7))
    f.day(wk("Thu", 12, slot=7, plus=1), "«завтра»")
    f.p("7 470 ₽", "замена наружного ШРУСа, класс car", job="cv_axle")
    f.scenario = {"who_writes": "Человек по объявлению, вечером.", "vehicle": "Renault Logan 2014",
                  "what_happens": "Цена и срок — черновик отвечает на оба вопроса, Никита его отправляет. Потом «завтра с утра можно? и пыльник отдельно не меняете?»: он печатает «Да-да, завтра к 9 приезжайте!», про пыльник приходится спрашивать ещё раз; следующий черновик отвечает, и он его отправляет.",
                  "facts": {"booked": "следующий день, 09:00, main (в тот день смена слотов 6 и 29)", "hours": "1,5 нормо-часа по каталогу: «около полутора часов»", "public_pages_used": []}}
    f.floating = [fl("завтра с утра", d, "the next day", "adverb"), fl("Завтра утром", d, "the next day", "adverb"), fl("завтра к 9", d, "the next day", "adverb"), fl("завтра к 9:00", d, "the next day", "adverb")]
    c = avito(f, "c1", "main", 219, "Саня", 44, "Ремонт ходовой: ШРУСы, стойки, рычаги, ступичные подшипники. Московское шоссе", avatar=pic("car", "серебристый Renault Logan во дворе у гаражей", matches="Renault Logan 2014"),
              opened_note="a new Avito chat: one per listing and buyer")
    c.c(d + " 18:02:10", "здравствуйте. шрус на логан наружный сколько стоит поменять и за сколько по времени сделаете")
    c.d("18:02:55", "d1", "Здравствуйте! Замена наружного ШРУСа на Logan стоит 7 470 ₽ с запчастью, по времени около полутора часов. Подскажите год выпуска и с какой стороны хрустит?")
    c.s(7, "18:11:30", "Здравствуйте! Замена наружного ШРУСа на Logan стоит 7 470 ₽ с запчастью, по времени около полутора часов. Подскажите год выпуска и с какой стороны хрустит?", use="d1")
    c.c("18:14:20", "2014, левый. завтра с утра можно? и пыльник отдельно не меняете, без шруса?")
    c.d("18:15:05", "d2", "Завтра утром можно, время подтвержу. По пыльнику: если ШРУС уже хрустит, один пыльник не поможет, шарнир изношен; мастер посмотрит на месте и скажет точно.")
    c.s(7, "18:19:40", "Да-да, завтра к 9 приезжайте!")
    c.c("18:22:10", "а пыльник?")
    c.d("18:22:50", "d3", "Если ШРУС уже хрустит, замена одного пыльника не поможет: шарнир изношен. Мастер посмотрит на месте и скажет точно.")
    c.s(7, "18:27:30", "Если ШРУС уже хрустит, замена одного пыльника не поможет: шарнир изношен. Мастер посмотрит на месте и скажет точно.", use="d3")
    c.c("18:29:15", "понял, буду")
    c.d("18:29:55", "d4", "Ждём вас завтра к 9:00: Московское шоссе, 40.")
    c.s(7, "18:33:20", "Ждём вас завтра к 9:00: Московское шоссе, 40.", use="d4")
    c.res(7, "18:33:50")
    c.reads_extra = {"operator_credit": "slot 7: first answer {first} minutes (his ledger row is 9), four replies, three drafts sent as they were and one discarded, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 7; the assistant drafts", "outcome": "записан на следующее утро, 09:00; закрыт слотом 7",
               "facts": ["the price given is 7 470", "of two questions in one message slot 7 answered the first; the second was asked again and answered by a draft sent as it was", "no name or number was asked for"], "questions": []}
    f.why = ["Черновик, который он выбросил, отвечал на оба вопроса; его собственная строка — на один.", "Три черновика из четырёх ушли без правки: это доля из его строки в леджере.",
             "Имя и телефон он не спросил; на Авито номер не виден, и запись осталась без контакта."]
    f.new_facts = ["Объявление сервиса на Авито «Ремонт ходовой: ШРУСы, стойки, рычаги, ступичные подшипники. Московское шоссе».",
                   "«Саня», Renault Logan 2014: замена левого наружного ШРУСа на main на следующий день после чата, 09:00; запись без телефона.", "Картинка контакта: серебристый Logan у гаражей."]
    return f


def f14():
    f = File(CFG, 14, "people", "p07-web-shinomontazh",
             "Сезон: переобуться на зиму. Ассистент называет цену и передаёт заявку, новичок записывает «на сегодня»",
             "A booking on the web chat inside the autumn tyre window. The assistant gives the public price, cannot book, hands over. Slot 7 answers in nine minutes: «Да-да», a time today, «должны успеть». A question about storage is answered by the draft, sent as it was; so is the closing line. He labels and resolves.")
    f.cast = {"customer": cust("Денис", "Kia Rio, колёса R15; в сервисе впервые", first_time=True, phone="+7 907 215-63-08")}
    f.staff(7, s7={"weeks_in_the_job": 11})
    d = f.day(wk("Tue", 3, slot=7))
    f.p("3 000 ₽", "сезонная замена шин: шиномонтаж 4 колёс с балансировкой, класс car", job="seasonal_tyre_change")
    f.p("3 000 ₽ за сезон", "сезонное хранение комплекта шин", job="tyre_storage")
    f.scenario = {"who_writes": "Новый клиент в разгар шинного сезона.", "vehicle": "Kia Rio",
                  "what_happens": "Цена из прайса, передача заявки, «сегодня к 18:00». Про хранение отвечает черновик.",
                  "facts": {"booked": "%s 18:00, main" % d, "season": "осеннее шинное окно: 13 октября — 9 ноября (catalogue.md)", "public_pages_used": ["прайс: шиномонтаж и хранение шин", "часы работы и адреса"]}}
    f.floating = [fl("сегодня вечером или завтра", d, "the day and the next", "adverb"), fl("сегодня", d, d, "adverb"), fl("к 6", d, d, "к + dative"), fl("сегодня к 18:00", d, d, "adverb")]
    c = web(f, "c1", "main", 512, 14)
    c.c(d + " 14:20:10", "здравствуйте, переобуться на зиму сколько стоит и когда можно")
    c.a("14:20:34", HELLO + "Сезонная замена шин, шиномонтаж четырёх колёс с балансировкой, стоит 3 000 ₽ для легкового автомобиля. Сам записать я не могу, но передам заявку мастеру-приёмщику. Какая у вас машина и на какой день хотите?")
    c.c("14:21:15", "киа рио, r15. лучше сегодня вечером или завтра")
    c.a("14:21:40", "Понял. Напишите, пожалуйста, как к вам обращаться и номер телефона. И в какой сервис удобнее: на Московском шоссе или в Новом городе?")
    c.c("14:22:10", "Денис 8 907 215 63 08, московское")
    c.a("14:22:34", "Спасибо, Денис. " + SAID)
    c.h("14:22:35", "scheduling", "Денис", "+7 907 215-63-08", "московское",
        "Денис, Kia Rio, колёса R15. Хочет сезонную замену шин на зимние сегодня вечером или завтра, Московское шоссе. Я назвал цену из прайса, 3 000 ₽.",
        "main", "%s 20:00, закрытие дня" % d)
    c.s(7, "14:31:50", "Денис, здравствуйте, это Никита, Московское шоссе. Да-да, сегодня можно, приезжайте к 18:00! За час должны успеть")
    c.c("14:34:20", "ок. а летние колёса у вас оставить на хранение можно?")
    c.d("14:35:00", "d1", "Да, сезонное хранение комплекта шин стоит 3 000 ₽ за сезон. Оформить можно при приёме машины.")
    c.s(7, "14:40:30", "Да, сезонное хранение комплекта шин стоит 3 000 ₽ за сезон. Оформить можно при приёме машины.", use="d1")
    c.c("14:42:10", "хорошо, буду к 6")
    c.d("14:42:50", "d2", "Ждём вас сегодня к 18:00: Московское шоссе, 40.")
    c.s(7, "14:47:40", "Ждём вас сегодня к 18:00: Московское шоссе, 40.", use="d2")
    c.label(7, "14:48:00", "шины")
    c.res(7, "14:48:20")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 7: his first line {first} minutes after the hand-off, three replies, two drafts sent as they were, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "assistant first, handed over (scheduling), slot 7", "outcome": "шиномонтаж в тот же день, 18:00, main; закрыт слотом 7",
               "facts": ["the price given is 3 000 for four wheels", "storage is 3 000 a season", "slot 7 promised an hour: «должны успеть»"], "questions": []}
    f.why = ["«Да-да, сегодня можно» и «должны успеть» в одной реплике: обещает то, на что надеется, в день, когда сервис работает в полтора раза плотнее обычного.", "Оба черновика ушли без правки.", "Ярлык «шины» он поставил: в сезон это половина его чатов."]
    f.new_facts = ["Денис, +7 907 215-63-08, Kia Rio R15: сезонная замена шин на main в первый рабочий день слота 7 начиная со вторника недели T-3, 18:00; спросил про хранение летних колёс (3 000 за сезон)."]
    return f


def f15():
    f = File(CFG, 15, "people", "p16-telegram-kondicioner",
             "Жалоба лучшему приёмщику: кондиционер заправили неделю назад, и он опять не холодит",
             "Slot 16 in writing: the customer's name and patronymic twice, «я бы на своей машине», two times to choose from, a summary with the address and who receives the car. She raises the chat to High herself and books a free check under the 30-day warranty. Two drafts edited; labelled and resolved.")
    f.cast = {"customer": cust("Галина Петровна Сорокина", "постоянная клиентка сервиса в Новом городе; LADA Granta 2020; неделю назад заправляли кондиционер")}
    f.staff(16)
    d = f.day(wk("Wed", 15, slot=16))
    f.day(wk("Wed", 15, slot=16, plus=1), "«завтра, пятница»")
    f.scenario = {"who_writes": "Постоянная клиентка, которой неудобно жаловаться.", "vehicle": "LADA Granta 2020",
                  "what_happens": "Кондиционер после заправки холодил три дня. Светлана благодарит, что написали, объясняет, что это утечка, а не заправка, предлагает сегодня к 14:00 или завтра к 9:30, бесплатно, по гарантии.",
                  "facts": {"warranty": "30 дней на слесарные и электрические работы (ledger s12.warranty)", "booked": "следующий день, 09:30, east: проверка на утечку по гарантии", "public_pages_used": []}}
    f.floating = [fl("на прошлой неделе", d, "the week T-16", "на + prepositional"), fl("сегодня к 14:00", d, d, "adverb"), fl("завтра к 9:30", d, "the next day", "adverb"), fl("завтра, пятница, 9:30", d, "the next day", "adverb, nominative")]
    c = tg(f, "c1", "east", 1422, "Галина Петровна", avatar=pic("view", "куст сирени у деревянного забора"), opened_note=LATER)
    c.c(d + " 09:20:15", "Светлана, здравствуйте. неудобно жаловаться, но кондиционер, который вы на прошлой неделе заправляли, опять не холодит")
    c.c("09:20:50", "дня три подул холодным и всё")
    c.d("09:21:30", "d1", "Здравствуйте! Приносим извинения. Если кондиционер перестал холодить через несколько дней после заправки, в системе может быть утечка, это нужно проверить. Когда вам удобно подъехать?")
    c.s(16, "09:26:40", "Галина Петровна, здравствуйте! И правильно, что написали, извиняться тут не за что. Если через три дня перестал холодить, значит, фреон уходит: где-то утечка, и сама заправка тут ни при чём. Я бы на своей машине второй раз не заправляла, пока не найдём, где течёт. Приезжайте сегодня к 14:00 или завтра к 9:30, проверим систему. Для вас это бесплатно, Галина Петровна: работа на гарантии.", edit="d1")
    c.prio(16, "09:27:10", "high")
    c.c("09:31:20", "завтра к 9:30 смогу")
    c.d("09:32:00", "d2", "Хорошо, Галина Петровна. Завтра в 9:30 ждём вас.")
    c.s(16, "09:34:10", "Записала, Галина Петровна: завтра, пятница, 9:30, проверка кондиционера на утечку, Granta, по гарантии, бесплатно. Мы на 10-м Инженерном проезде, 30. Принимаю я: найдём, где уходит, сразу покажу и скажу, сколько стоит это устранить.", edit="d2")
    c.label(16, "09:34:30", "жалоба")
    c.res(16, "09:34:50")
    c.reads_extra = {"operator_credit": "slot 16: first answer {first} minutes (her ledger row is 6), two replies, two drafts edited, a base priority of High set by her, one resolved"}
    f.truth = {"reason": "complaint, comeback, the bill", "handled": "slot 16; the assistant drafts", "outcome": "бесплатная проверка на утечку на следующий день, 09:30; закрыт слотом 16",
               "facts": ["the air conditioning stopped cooling three days after a recharge at east", "slot 16 set the priority to High and booked a free leak check under the warranty", "she did not offer a second recharge"], "questions": []}
    f.why = ["Она не защищает работу и не заправляет второй раз «на всякий случай»: сначала найти, где течёт.", "Имя-отчество дважды, «я бы на своей машине», два времени, итог с адресом и словами «принимаю я».", "Приоритет «Высокий» поставила она сама: жалобы у неё не ждут очереди."]
    f.new_facts = ["Галина Петровна Сорокина, LADA Granta 2020, east: заправка кондиционера на неделе T-16; бесплатная проверка на утечку по гарантии на следующий день после чата, 09:30 (гарантийный заказ со ссылкой на первый).",
                   "Картинка контакта: куст сирени у забора."]
    return f


def f16():
    f = File(CFG, 16, "people", "p16-web-pered-pokupkoy",
             "Машина с рук: проверить до покупки. Запись на день, когда Светлана выходная",
             "The web chat hands over a pre-purchase inspection. Slot 16 answers in six minutes with what the check is and two times, and says plainly that on that day she is off and the other advisor will receive the car: two on, two off. The summary carries the date, the address and what to bring.")
    f.cast = {"customer": cust("Антон", "покупает Skoda Octavia 2014 с рук; в сервисе впервые", first_time=True, phone="+7 907 441-09-27"),
              "named_in_a_line": [{"slot": 17, "name": "Артём Николаев", "role": "примет машину в среду"}]}
    f.staff(16)
    d = f.day(wk("Mon", 7, slot=16))
    f.day(wk("Wed", 7), "«в среду, 23 сентября»: slot 17's shift")
    f.p("3 000 ₽", "комплексная диагностика автомобиля перед покупкой, фиксированная цена", job="pre_purchase_inspection")
    f.scenario = {"who_writes": "Человек, который собирается купить подержанную машину.", "vehicle": "Skoda Octavia 2014, пока чужая",
                  "what_happens": "Цена из прайса, передача заявки; через шесть минут Светлана объясняет, что входит в проверку, и предлагает два времени в среду.",
                  "facts": {"booked": "среда недели T-7, 11:00, east; принимает слот 17", "hours": "1,5 нормо-часа по каталогу: «часа полтора»", "public_pages_used": ["прайс: диагностика перед покупкой"]}}
    f.floating = [fl("в среду", d, "the Wednesday of week T-7", "в + accusative"), fl("В среду", d, "the Wednesday of week T-7", "в + accusative"), fl("среда, 23 сентября, 11:00", d, "the Wednesday of week T-7", "nominative, date")]
    c = web(f, "c1", "east", 590, 16)
    c.c(d + " 17:42:10", "здравствуйте. а вы машины перед покупкой проверяете?")
    c.a("17:42:34", HELLO + "Да: комплексная диагностика автомобиля перед покупкой стоит 3 000 ₽. Передать заявку мастеру, чтобы вас записали?")
    c.c("17:43:20", "да. смотрю октавию 2014 с рук, продавец готов подъехать в среду")
    c.a("17:43:45", "Сам записать я не могу, но заявку передам. Напишите, пожалуйста, как к вам обращаться и номер телефона. И в какой сервис удобнее: на Московском шоссе или в Новом городе?")
    c.c("17:44:15", "Антон, 89074410927. новый город")
    c.a("17:44:39", "Спасибо, Антон. " + SAID)
    c.h("17:44:40", "scheduling", "Антон", "+7 907 441-09-27", "новый город",
        "Антон покупает Skoda Octavia 2014 с рук и хочет диагностику перед покупкой; продавец готов подъехать в среду. Я назвал цену, 3 000 ₽. Сервис в Новом городе.",
        "east", "%s 20:00, закрытие дня" % d)
    c.s(16, "17:50:30", "Антон, добрый вечер! Это Светлана, сервис в Новом городе. Правильно делаете, что проверяете до денег, Антон: я бы на своей покупке сделала так же. Диагностика перед покупкой у нас 3 000 ₽, занимает часа полтора: подъёмник, кузов, компьютер, по итогу лист с замечаниями, с ним можно торговаться. В среду я не работаю, вас примет Артём. Могу записать на 11:00 или на 16:00, как вам удобнее?")
    c.c("17:55:10", "на 11")
    c.d("17:55:50", "d1", "Хорошо, Антон. Среда, 11:00. Ждём вас: 10-й Инженерный проезд, 30.")
    c.s(16, "17:58:20", "Записала, Антон: среда, 23 сентября, 11:00, диагностика перед покупкой, Skoda Octavia 2014. Адрес: 10-й Инженерный проезд, 30. Попросите продавца взять ПТС и сервисную книжку, если есть. Примет вас Артём, я ему всё передам.", edit="d1")
    c.label(16, "17:58:40", "запись")
    c.res(16, "17:59:00")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 16: her first line {first} minutes after the hand-off, two replies, one draft edited, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "assistant first, handed over (scheduling), slot 16", "outcome": "диагностика перед покупкой в среду, 11:00, east, принимает слот 17; закрыт слотом 16",
               "facts": ["the assistant gave the public price, 3 000", "slot 16 replied {first} minutes after the hand-off", "she told the customer she is off that day and who will receive the car"], "questions": ["S5.1"]}
    f.why = ["«В среду я не работаю, вас примет Артём»: два через два, сказанное клиенту прямо.", "Реплика длиннее, чем у любого другого приёмщика, и в ней нет ни одного лишнего слова.", "В итоге есть дата, адрес и что взять с собой."]
    f.new_facts = ["Антон, +7 907 441-09-27: диагностика перед покупкой Skoda Octavia 2014 на east в среду недели T-7, 11:00; принимает слот 17."]
    return f


def f17():
    f = File(CFG, 17, "people", "p17-vk-ne-segodnya",
             "Второй приёмщик на Инженерном во «ВКонтакте»: цена раньше причины, и первое же «не сегодня» принято",
             "Slot 17 in writing: the price before the need, «Понял, принял» at the first no. The draft he wrote over said why the check comes before the alignment; the one he wrote over next argued for the visit. A later question waits an hour, and then the draft goes out as it was. He does not resolve.")
    f.cast = {"customer": cust("Вадим", "Chevrolet Cruze 2012; поймал яму, руль стоит криво", first_time=True)}
    f.staff(17)
    d = f.day(wk("Fri", 12, slot=17))
    f.day(wk("Fri", 12, slot=17, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("3 000 ₽", "регулировка углов установки колёс (сход-развал), две оси, класс car", job="wheel_alignment")
    f.p("3 000", "то же, как он пишет", job="wheel_alignment")
    f.p("800 ₽", "диагностика ходовой части", job="suspension_diag")
    f.scenario = {"who_writes": "Парень после ямы, пишет на «ты».", "vehicle": "Chevrolet Cruze 2012",
                  "what_happens": "«Сколько развал сделать»: цена. «Дороговато, не сегодня»: «Понял, принял». Потом: сильно ли съест резину? Через час: да.",
                  "facts": {"sold": "нет", "public_pages_used": []}}
    f.floating = [fl("не сегодня", d, d, "adverb")]
    c = vk(f, "c1", "east", 3162, "Вадим Корнеев", avatar=pic("car", "чёрный Chevrolet Cruze на парковке у торгового центра", matches="Chevrolet Cruze 2012"), opened_note="his first message to the community: a new conversation")
    c.c(d + " 11:05:10", "привет. яму поймал, руль теперь криво стоит. сколько развал сделать")
    c.d("11:05:55", "d1", "Здравствуйте! Регулировка углов установки колёс (сход-развал) на две оси стоит 3 000 ₽. После удара о яму сначала стоит проверить ходовую: если погнут рычаг или тяга, развал не выставится. Когда вам удобно подъехать?")
    c.s(17, "11:17:20", "Здравствуйте! Развал 3 000 за две оси. Всё сделаем, когда подъедете?")
    c.c("11:20:40", "дороговато чет. не сегодня тогда")
    c.d("11:21:20", "d2", "Понимаю. Если руль стоит криво после удара, с ремонтом лучше не затягивать: шины будут изнашиваться неравномерно. Можем сначала посмотреть ходовую, диагностика стоит 800 ₽.")
    c.s(17, "11:28:05", "Понял, принял. Надумаете — пишите!")
    c.c("11:31:15", "а если так ездить резину сильно съест?")
    c.d("11:31:55", "d3", "Да: при нарушенных углах шины изнашиваются неравномерно и быстрее, особенно передние.")
    c.c("11:58:40", "мне просто до зарплаты дотянуть надо")
    c.d("11:59:25", "d4", "Понимаю. До зарплаты доехать можно, но при нарушенных углах шины изнашиваются неравномерно и быстрее, особенно передние: лучше не затягивать.")
    c.s(17, "12:29:40", "Понимаю. До зарплаты доехать можно, но при нарушенных углах шины изнашиваются неравномерно и быстрее, особенно передние: лучше не затягивать.", use="d4", late="второй вопрос может ждать час (cast.json)")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 17: first answer {first} minutes (his ledger row is 11), three replies, two drafts discarded, one replaced before he looked and one sent as it was, nothing resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 17; the assistant drafts", "outcome": "визита нет; закрыт по 7 дням тишины",
               "facts": ["the price was named before the reason for the work", "the customer said «не сегодня» once and slot 17 accepted it", "both discarded drafts proposed checking the suspension first, 800",
                         "a later question waited 58 minutes"], "questions": ["S5.1"]}
    f.why = ["Цена, потом «всё сделаем», потом «надумаете — пишите»: три привычки из его листа звонков, только набранные.", "Оба выброшенных черновика — то, что написала бы Светлана.", "Это его смена: в такие дни сервис продаёт меньше (история S5)."]
    f.new_facts = ["Вадим Корнеев («ВКонтакте»), Chevrolet Cruze 2012: спрашивал сход-развал на east (3 000) после удара о яму; не приехал.", "Картинка контакта: чёрный Cruze на парковке."]
    return f


def f18():
    f = File(CFG, 18, "people", "p17-avito-shiny-hranenie",
             "Авито перед сезоном: шиномонтаж на кроссовер, и хранение, про которое пришлось спросить дважды",
             "An Avito price question a day before the tyre window. Slot 17 sends the first draft as it was, answers the first half of a double question himself, and gets to the second half 58 minutes after it is asked again, editing the draft into a booking with the address. He labels it and does not resolve.")
    f.cast = {"customer": cust("Олег", "пишет по объявлению; кроссовер, колёса R16", first_time=True)}
    f.staff(17)
    d = f.day(wk("Mon", 4, slot=17))
    f.day(wk("Wed", 4), "«в среду»")
    f.day(wk("Mon", 4, slot=17, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("3 750 ₽", "сезонная замена шин, 4 колеса с балансировкой, класс suv", job="seasonal_tyre_change", cls="suv")
    f.p("3 000 ₽ за сезон", "сезонное хранение комплекта шин", job="tyre_storage")
    f.p("3 000 за сезон", "то же, как он пишет", job="tyre_storage")
    f.num_("до семи месяцев", "срок хранения в названии услуги каталога")
    f.scenario = {"who_writes": "Человек по объявлению, за день до начала шинного окна.", "vehicle": "кроссовер, R16 (модель не названа)",
                  "what_happens": "Цена, запись на среду вечером, и хранение летней резины: на этот вопрос ответ приходит почти через час после второго напоминания.",
                  "facts": {"booked": "среда недели T-4, 18:30, east (в тот день смена слота 16)", "public_pages_used": []}}
    f.floating = [fl("в среду вечером", d, "the Wednesday of week T-4", "в + accusative"), fl("В среду вечером", d, "the Wednesday of week T-4", "в + accusative"), fl("В среду", d, "the Wednesday of week T-4", "в + accusative"),
                  fl("среда, 18:30", d, "the Wednesday of week T-4", "nominative")]
    c = avito(f, "c1", "east", 233, "Олег", 52, "Шиномонтаж, балансировка, сезонное хранение шин. Новый город", opened_note="a new Avito chat: one per listing and buyer")
    c.c(d + " 10:10:05", "Добрый день. Шиномонтаж r16 сколько? 4 колеса, кроссовер")
    c.d("10:10:50", "d1", "Добрый день! Сезонная замена шин, 4 колеса с балансировкой, для кроссовера стоит 3 750 ₽. На какой день вас записать?")
    c.s(17, "10:21:30", "Добрый день! Сезонная замена шин, 4 колеса с балансировкой, для кроссовера стоит 3 750 ₽. На какой день вас записать?", use="d1")
    c.c("10:24:10", "в среду вечером. и хранение летней резины есть у вас? почём")
    c.d("10:24:55", "d2", "В среду вечером можно, время подтвержу. Сезонное хранение комплекта шин стоит 3 000 ₽ за сезон.")
    c.s(17, "10:33:20", "В среду могу на 18:30 записать, подойдёт?")
    c.label(17, "10:33:40", "шины")
    c.c("10:35:40", "да. а хранение?")
    c.d("10:36:20", "d3", "Сезонное хранение комплекта из четырёх шин стоит 3 000 ₽ за сезон, до семи месяцев.")
    c.s(17, "11:34:10", "Хранение 3 000 за сезон, это до семи месяцев. Записал: среда, 18:30, шиномонтаж 4 колеса. Адрес: 10-й Инженерный проезд, 30.", edit="d3", late="второй вопрос может ждать час (cast.json)")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 17: first answer {first} minutes (his ledger row is 11), three replies, one draft sent as it was, one discarded, one edited, nothing resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 17; the assistant drafts", "outcome": "шиномонтаж в среду, 18:30, east; закрыт по 7 дням тишины",
               "facts": ["the price given is 3 750 for a crossover", "storage (3 000 a season) was asked about twice and answered 58 minutes after the second asking"], "questions": []}
    f.why = ["Выброшенный черновик отвечал на оба вопроса сразу.", "Час ожидания — тот самый «второй вопрос может ждать час» из его описания.", "Имя на Авито есть, телефона нет: запись без контакта."]
    f.new_facts = ["Объявление сервиса на Авито «Шиномонтаж, балансировка, сезонное хранение шин. Новый город».", "«Олег», кроссовер R16: шиномонтаж на east в среду недели T-4, 18:30; спрашивал про хранение.", "У контакта нет картинки."]
    return f


def f19():
    f = File(CFG, 19, "people", "p22-telegram-prigonyay",
             "Руководитель казанского сервиса и человек, которого он знает много лет",
             "Slot 22 in writing, at his warmest: half an hour to a first reply, a few words and a question about the customer's father. No time, no price, nothing written down; «принял». Both drafts written over. Nobody resolves it.")
    f.cast = {"customer": cust("Марат Нуриев", "давний клиент сервиса на Технической, ещё при прежнем владельце; пригоняет отцовскую «Ниву»")}
    f.staff(22)
    d = f.day(wk("Tue", 16))
    f.day(wk("Tue", 16, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.scenario = {"who_writes": "Давний клиент, пишет руководителю по имени-отчеству.", "vehicle": "отцовская «Нива» (год не назван)",
                  "what_happens": "«Нива» опять греется. «пригоняй, посмотрим. как отец, здоров?» Будет после обеда. «принял».",
                  "facts": {"public_pages_used": [], "note": "нигде ничего не записано: ни записи, ни времени; визит — без записи"}}
    f.floating = [fl("после обеда", d, d, "после + genitive"), fl("сегодня или завтра", d, "the day or the next", "adverb")]
    c = tg(f, "c1", "west", 3105, "Марат Нуриев", avatar=pic("view", "река, камыши и закат"), opened_note=LATER)
    c.c(d + " 09:12:20", "Ринат Фаридович, салам. это Марат Нуриев, отцова нива опять греется. можно пригоню?")
    c.d("09:13:05", "d1", "Здравствуйте, Марат! Да, пригоняйте, посмотрим. Если двигатель перегревается, лучше не откладывать. Когда вам удобно, сегодня или завтра?")
    c.s(22, "09:45:30", "салам. пригоняй, посмотрим. как отец, здоров?")
    c.c("09:49:10", "здоров, спасибо, вам привет передаёт. после обеда буду")
    c.d("09:49:50", "d2", "Спасибо, взаимно! Ждём вас после обеда.")
    c.s(22, "10:20:15", "принял")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 22: first answer {first} minutes (his ledger row is 35), two replies, two drafts discarded, nothing resolved"}
    f.truth = {"reason": "a symptom", "handled": "slot 22; the assistant drafts", "outcome": "приедет без записи после обеда; закрыт по 7 дням тишины",
               "facts": ["slot 22 offered no time and no price and took no note of the car", "both drafts were discarded"], "questions": []}
    f.why = ["За это его и любят постоянные клиенты, и это настоящее.", "Рядом — файл 20: тот же человек, незнакомый клиент, на следующий день, семь слов.", "Черновик спрашивал «сегодня или завтра»; он не спросил."]
    f.new_facts = ["Марат Нуриев, давний клиент west, отцовская «Нива» (перегрев, повторно), визит без записи во вторник недели T-16.", "Картинка контакта: река, камыши и закат."]
    return f


def f20():
    f = File(CFG, 20, "people", "p22-web-rashodnye-materialy",
             "Строка в наряде, о которой не сказали: руководитель отвечает на следующий день, а объясняет Камила",
             "A question about a bill on the web chat: the assistant explains the charge in general, cannot see the order, hands over. It arrives on the weak desk's shift; the chat turns Urgent and stays so overnight. Slot 22 answers the next morning in seven words. The customer's reply gets a draft he does not touch; slot 24, back on shift, edits it and sends it eight minutes later, with the figure, and resolves.")
    f.cast = {"customer": cust("Фарид", "клиент сервиса на Технической; накануне ему меняли помпу", phone="+7 907 551-34-26")}
    f.staff(22, 24)
    d = f.day(wk("Wed", 9))
    n = f.day(wk("Wed", 9, plus=1), "the next day: slot 24 is on shift")
    f.psup("125,40", "расходные материалы на замене помпы: 3 % от работы по нормо-часам, 4 180", "water_pump")
    f.plab("4 180 ₽", "работа по замене помпы: 2,2 нормо-часа", "water_pump")
    f.num_("3 процента", "ставка расходных материалов (ledger price.supplies.rate)")
    f.num_("3 %", "то же")
    f.num_("500 ₽", "предел на заказ (ledger price.supplies.cap)")
    f.scenario = {"who_writes": "Клиент, который дома прочитал заказ-наряд.", "what_happens": "«Расходные материалы 125,40. Мне про неё никто не говорил.» Ответ приходит наутро: «это во всех нарядах. 3 процента от работ». Он пишет, что могли бы и предупредить. Объясняет ему Камила.",
                  "facts": {"rule": "3 % от работ по нормо-часам на заказе, не больше 500 (catalogue.json shop_supplies)",
                            "rota": "в день вопроса на приёмке слот 23 и руководитель; слот 24 выходит на следующий день", "public_pages_used": ["прайс: расходные материалы"]}}
    f.floating = [fl("Вчера", d, "the Tuesday of week T-9", "adverb")]
    c = web(f, "c1", "west", 702, 20)
    c.c(d + " 11:40:10", "Здравствуйте. Вчера забирал машину на Технической, в заказ-наряде строка «расходные материалы» 125,40. Мне про неё никто не говорил. Это что?")
    c.a("11:40:35", HELLO + "Ваш заказ-наряд я не вижу. В целом расходные материалы — это небольшая доплата к работам, которые считаются по нормо-часам: очистители, смазки, крепёж. По вашему наряду вопрос передам на Техническую. Напишите, пожалуйста, как к вам обращаться и номер телефона.")
    c.c("11:41:20", "Фарид, +79075513426")
    c.a("11:41:44", "Спасибо, Фарид. " + SAID_Q)
    c.h("11:41:45", "escalation", "Фарид", "+7 907 551-34-26", "Техническая",
        "Фарид вчера забрал машину на Технической. В заказ-наряде строка «расходные материалы», 125,40, о которой ему не сказали; спрашивает, что это. Наряд я не вижу, объяснил только в общих словах.",
        "west", "%s 20:00, закрытие дня" % d)
    c.s(22, n + " 09:25:10", "это во всех нарядах. 3 процента от работ", late="he answers the next day (ledger conv.slowest_tenth)")
    c.c("09:48:30", "Могли бы и предупредить. Ладно.")
    c.d("09:49:10", "d1", "Вы правы, Фарид, приносим извинения, что об этом не сказали при выдаче. Расходные материалы — это 3 % от стоимости работ по нормо-часам, не больше 500 ₽ на заказ; строка есть в каждой смете.")
    c.s(24, "09:56:40", "Фарид, здравствуйте, это Камила, мастер-приёмщик на Технической. Вы правы, и извините, что при выдаче об этом не сказали. Расходные материалы — это 3 % от работ по нормо-часам, не больше 500 ₽ на заказ. У вас 125,40 — это 3 % от работы по замене помпы, 4 180 ₽. Эта строка должна быть в смете ещё до начала ремонта. Если в наряде что-то ещё непонятно, пишите сюда, разберёмся.", edit="d1")
    c.label(24, "09:57:00", "жалоба")
    c.res(24, "09:57:20")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 22: his first line {first} working minutes after the hand-off, the next morning; slot 24: one reply in his chat, one draft edited, one resolved"}
    f.truth = {"reason": "complaint, comeback, the bill", "handled": "assistant first, handed over (escalation), slot 22, then slot 24", "outcome": "объяснено на следующий день; закрыт слотом 24",
               "facts": ["shop supplies are 3 % of hourly work, at most 500 an order; on his order 125,40", "the hand-over waited from 11:41 to the next morning", "slot 22 owns the chat; slot 24 wrote the reply that explained it"], "questions": []}
    f.why = ["Семь слов, без имени, без извинения, и по сути верно.", "Черновик был готов через сорок секунд после его реплики; владелец чата его не тронул; им воспользовалась Камила, выйдя на смену.", "Владелец чата и тот, кто помог клиенту, — не всегда одна строка в статистике."]
    f.new_facts = ["Фарид, +7 907 551-34-26: замена помпы на west, машину забрал во вторник недели T-9; в наряде расходные материалы 125,40 (3 % от работы 4 180)."]
    return f


def f21():
    f = File(CFG, 21, "people", "p23-telegram-v-lyuboe-vremya",
             "Слабая приёмка на записи: «можно. приезжайте», «в любое время»",
             "Slot 23 in writing on an ordinary day: 44 minutes to a first reply, two words, no day and no time. Asked what time and whether he may bring his own oil, he answers both in five words twenty minutes before closing. Both drafts written over; nothing labelled, nothing resolved.")
    f.cast = {"customer": cust("Ильдар", "Volkswagen Polo 2015; в сервисе на Технической уже бывал")}
    f.staff(23)
    d = f.day(wk("Mon", 13, slot=23))
    f.day(wk("Mon", 13, slot=23, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("6 700 ₽", "замена масла и масляного фильтра, класс car, с маслом и фильтром (в черновике)", job="oil_service")
    f.plab("1 330 ₽", "только работа по замене масла: 0,7 нормо-часа (в черновике)", "oil_service")
    f.scenario = {"who_writes": "Клиент, который хочет поменять масло в выходные.", "vehicle": "Volkswagen Polo 2015",
                  "what_happens": "«Можно. приезжайте». «А во сколько? и масло своё можно?» ждёт почти девять часов, с одним «ау» посередине, до «в любое время. можно своё». Приехал ли он — скажет учётная система.",
                  "facts": {"hours": "без выходных, 9:00–20:00 (ledger site.open_days)", "public_pages_used": []}}
    f.floating = [fl("на выходные", d, "the Saturday and Sunday of week T-13", "на + accusative"), fl("В субботу или в воскресенье", d, "the Saturday and Sunday of week T-13", "в + accusative"),
                  fl("В субботу и воскресенье", d, "the Saturday and Sunday of week T-13", "в + accusative")]
    c = tg(f, "c1", "west", 3218, "Ильдар", avatar=pic("pet", "овчарка на заднем сиденье машины"), opened_note=LATER)
    c.c(d + " 10:05:15", "добрый день. на замену масла можно записаться на выходные?")
    c.d("10:06:00", "d1", "Добрый день! Да, сервис работает без выходных, с 9:00 до 20:00. Замена масла и фильтра стоит 6 700 ₽ с маслом и фильтром. В субботу или в воскресенье, и в какое время вам удобно?")
    c.s(23, "10:50:30", "можно. приезжайте")
    c.c("10:57:10", "а во сколько? и масло своё можно?")
    c.d("10:57:50", "d2", "В субботу и воскресенье работаем с 9:00 до 20:00, время подтвержу. Со своим маслом можно: тогда оплачивается работа, 1 330 ₽, и фильтр.")
    c.c("14:30:20", "ау")
    c.d("14:31:05", "d3", "Прошу прощения за ожидание. В субботу и воскресенье работаем с 9:00 до 20:00, время подтвержу. Со своим маслом можно: тогда оплачивается работа, 1 330 ₽, и фильтр.")
    c.s(23, "19:40:20", "в любое время. можно своё", late="под закрытие: его ответы приходят вечером (cast.json; ledger conv.slowest_tenth)")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 23: first answer {first} minutes (his ledger row is 40), two replies, two drafts discarded and one replaced before he looked, nothing resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 23; the assistant drafts", "outcome": "время не назначено; закрыт по 7 дням тишины",
               "facts": ["no day and no time were offered; asked for one, slot 23 answered «в любое время» almost nine hours later", "no draft was used, and each carried a price"], "questions": []}
    f.why = ["Здесь нет ни грубости, ни ошибки, и нет записи.", "Каждый черновик заканчивался вопросом, который закрепил бы время, и называл цену.", "Рядом — файл 24: та же приёмка, такой же запрос, другой приёмщик."]
    f.new_facts = ["«Ильдар», Volkswagen Polo 2015: спрашивал запись на замену масла на выходные на west; запись не сделана.", "Картинка контакта: овчарка на заднем сиденье."]
    return f


def f22():
    f = File(CFG, 22, "people", "p23-web-rekomendaciya-v-naryade",
             "Рекомендация в наряде, о которой не сказали вслух: клиентка спрашивает на сайте",
             "Slot 23 writes up what he is asked for and mentions the rest at pick-up, or not at all. A customer finds «рекомендовано: замена передних тормозных колодок, остаток 2 мм» in her order at home. The assistant says what 2 mm means in general and hands over. His reply comes at 19:10: come and we will change them. Asked the price, he gives it the next morning: two words.")
    f.cast = {"customer": cust("Регина", "клиентка сервиса на Технической; накануне забрала машину", phone="+7 907 612-05-84")}
    f.staff(23)
    d = f.day(wk("Thu", 5, slot=23))
    n = f.day(wk("Thu", 5, slot=23, plus=1), "the next day: slot 23's second working day")
    f.day(wk("Thu", 5, slot=23, plus=8), "Chatwoot resolves the chat after 7 silent days")
    f.p("4 560 ₽", "замена передних тормозных колодок, класс car, стандартные колодки", job="front_brake_pads")
    f.p("4560", "то же, как он пишет", job="front_brake_pads")
    f.num_("2 мм", "остаток колодок в её наряде")
    f.scenario = {"who_writes": "Клиентка, которая дома прочитала заказ-наряд.", "what_happens": "Можно ли с этим ездить? Ассистент: 2 мм — почти предел; передаю мастеру. Мастер, под закрытие: приезжайте, поменяем. Сколько и как долго? Наутро: «4560. час».",
                  "facts": {"recommended": "замена передних тормозных колодок; записано в наряде, при выдаче не сказано", "sold": "нет", "public_pages_used": ["вопросы о тормозах: остаток колодок"]}}
    f.floating = [fl("Вчера", d, "the day before", "adverb")]
    c = web(f, "c1", "west", 760, 22)
    c.c(d + " 12:30:10", "Здравствуйте. Вчера забрала машину на Технической, дома читаю наряд: «рекомендовано: замена передних тормозных колодок, остаток 2 мм». Мне при выдаче ни слова не сказали. С этим вообще ездить можно?")
    c.a("12:30:36", HELLO + "Ваш заказ-наряд я не вижу и диагноз по переписке поставить не могу, но остаток 2 мм — это почти предел, с заменой передних колодок лучше не тянуть. Передам ваш вопрос мастеру-приёмщику на Технической, он всё объяснит. Напишите, пожалуйста, как к вам обращаться и номер телефона.")
    c.c("12:31:20", "Регина 89076120584")
    c.a("12:31:44", "Спасибо, Регина. " + SAID_Q)
    c.h("12:31:45", "escalation", "Регина", "+7 907 612-05-84", "Техническая",
        "Регина вчера забрала машину на Технической. В наряде написано «рекомендовано: замена передних тормозных колодок, остаток 2 мм»; при выдаче ей об этом не сказали, спрашивает, можно ли ездить. Я ответил, что 2 мм — почти предел и с заменой лучше не тянуть; наряд я не вижу.",
        "west", "%s 20:00, закрытие дня" % d)
    c.s(23, "19:10:30", "да, колодки на исходе. приезжайте поменяем", late="под закрытие: его ответы приходят вечером (cast.json; ledger conv.slowest_tenth)")
    c.c("19:22:10", "Сколько это стоит и сколько по времени?")
    c.d("19:22:50", "d1", "Замена передних тормозных колодок стоит 4 560 ₽ с запчастями, по времени около часа. Записать вас?")
    c.s(23, n + " 09:50:20", "4560. час")
    c.auto()
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 23: his first line {first} working minutes after the hand-off, two replies, one draft discarded, nothing resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "assistant first, handed over (escalation), slot 23", "outcome": "рекомендованные колодки не проданы; закрыт по 7 дням тишины",
               "facts": ["the recommendation was in the order and was not said at pick-up", "slot 23 answered at 19:10 with no price and no time", "the price, 4 560, came the next morning; no time was offered"], "questions": []}
    f.why = ["«приезжайте поменяем» — рекомендация, о которой вспомнили, когда уже поздно, только письменно.", "Черновик заканчивался словами «Записать вас?»; его строка заканчивается словом «час».", "Так сервис продаёт четыре рекомендации из десяти."]
    f.new_facts = ["Регина, +7 907 612-05-84: машину забрала на west накануне чата; в наряде рекомендация «замена передних тормозных колодок, остаток 2 мм» (4 560), не продана. Марка машины в чате не названа."]
    return f


def f23():
    f = File(CFG, 23, "people", "p24-telegram-smeta-faylom",
             "Светлое пятно на Технической: находки по пунктам, смета файлом, итог до копейки",
             "Slot 24 in writing: seven minutes to a first reply, the findings as a numbered list with the estimate as a file, «давайте сделаем так» and a deadline for the answer, then the approved work and the total with supplies, VAT inside. Two drafts edited, one sent as it was; labelled and resolved.")
    f.cast = {"customer": cust("Тимур Валеев", "клиент сервиса на Технической; Hyundai Creta 2018, уходит антифриз")}
    f.staff(24)
    d = f.day(wk("Fri", 10, slot=24))
    f.p("13 366 ₽", "замена водяного насоса (помпы), класс suv", job="water_pump", cls="suv")
    f.p("3 313,50 ₽", "замена ремня привода навесных агрегатов, класс suv", job="drive_belt", cls="suv")
    f.p("950 ₽", "опрессовка системы охлаждения, поиск утечки", job="cooling_pressure_test")
    f.psum("17 836,41 ₽", "помпа, ремень и опрессовка с расходными материалами: к оплате, НДС в том числе", [("water_pump", "suv"), ("drive_belt", "suv"), ("cooling_pressure_test", "suv")], tax=False)
    f.scenario = {"who_writes": "Клиент, чья машина с утра на диагностике.", "vehicle": "Hyundai Creta 2018",
                  "what_happens": "Есть новости? Диагностика закончена: течёт помпа, ремень в трещинах. Обе работы сегодня к 19:00, если подтвердит до 15:00. Он пишет «обе» и спрашивает итог.",
                  "facts": {"approved": "замена помпы и ремня привода навесных агрегатов", "public_pages_used": []}}
    f.floating = [fl("утром", d, d, "adverb"), fl("сегодня", d, d, "adverb")]
    c = tg(f, "c1", "west", 3340, "Тимур Валеев", avatar=pic("car", "белая Hyundai Creta у подъезда", matches="Hyundai Creta 2018"), opened_note=LATER)
    c.c(d + " 14:05:10", "Камила, добрый день. По Крете есть новости?")
    c.d("14:05:55", "d1", "Тимур, добрый день! Данных по вашей машине у меня сейчас нет. Уточню у мастера и сразу напишу.")
    c.s(24, "14:12:20", "Тимур, добрый день! Да, диагностику закончили, смета во вложении.\n1. Течёт помпа: подтёки антифриза на блоке, поэтому и уровень уходит. Замена — 13 366 ₽.\n2. Ремень навесного оборудования в трещинах, менять лучше сразу, заодно с помпой: 3 313,50 ₽.\n3. Опрессовка системы, которую вы согласовали утром, — 950 ₽.\nДавайте сделаем так: если подтвердите до 15:00, обе работы сделаем сегодня и машину отдадим к 19:00. Делаем обе или только помпу?",
        files=[{"kind": "file", "file": "Smeta_Creta_Valeev.pdf", "pool": "estimate-pdf", "shows": "смета на одну страницу: опрессовка, помпа, ремень, расходные материалы; итог — в том числе НДС 5 %"}], edit="d1")
    c.c("14:20:40", "обе. итого сколько?")
    c.d("14:21:20", "d2", "Спасибо, Тимур. Делаем обе работы. Итоговую сумму с расходными материалами сейчас уточню.")
    c.s(24, "14:24:10", "Спасибо, Тимур. Согласовано: помпа и ремень. Итого с опрессовкой и расходными материалами — 17 836,41 ₽, НДС в том числе. Будет готово к 19:00, напишу сюда.", edit="d2")
    c.label(24, "14:24:30", "согласование")
    c.s(24, "18:41:30", "Тимур, Крета готова. Антифриз в норме, подтёков нет. Мы до 20:00.")
    c.c("18:50:10", "выезжаю")
    c.d("18:50:50", "d3", "Ждём вас, Тимур.")
    c.s(24, "18:52:00", "Ждём вас, Тимур.", use="d3")
    c.res(24, "18:52:20")
    c.reads_extra = {"operator_credit": "slot 24: first answer {first} minutes (her ledger row is 7), four replies, two drafts edited and one sent as it was, one resolved"}
    f.truth = {"reason": "found work: approve or decline", "handled": "slot 24; the assistant drafts", "outcome": "помпа и ремень согласованы; итого с расходными материалами по смете, НДС в том числе; закрыт слотом 24",
               "facts": ["the findings came as a numbered list with the estimate attached", "both jobs approved in eight minutes", "ready before the time she gave"], "questions": []}
    f.why = ["Список, файл, срок и выбор из двух: клиент отвечает одним словом.", "«Давайте сделаем так» там, где на другой смене сказали бы «сегодня не успеем».", "Тот же сервис, что в файлах 21 и 22."]
    f.new_facts = ["Тимур Валеев, Hyundai Creta 2018, west, первый рабочий день слота 24 начиная с пятницы недели T-10: опрессовка 950, замена помпы 13 366, замена ремня 3 313,50; итог с расходными материалами в чате: 17 836,41, НДС в том числе.",
                   "Файл Smeta_Creta_Valeev.pdf (пул 'estimate-pdf').", "Картинка контакта: белая Creta у подъезда."]
    return f


def f24():
    f = File(CFG, 24, "people", "p24-avito-kondicioner",
             "Авито в июле: заправка кондиционера «сегодня реально попасть?»",
             "Avito carries a price question and a same-day request. Slot 24 edits the draft into her own: who she is and where, the price with what it covers, the morning is full and what she can do, and the one question that decides the job. The confirmation lists everything and names what happens if the system is empty. The closing draft goes out as it was; labelled and resolved.")
    f.cast = {"customer": cust("Айдар", "пишет по объявлению; Hyundai Solaris 2019", first_time=True)}
    f.staff(24)
    d = f.day(wk("Tue", 17, slot=24))
    f.p("3 800 ₽", "заправка кондиционера с вакуумированием (R134a)", job="ac_recharge")
    f.p("900 ₽", "диагностика системы кондиционирования", job="ac_performance_check")
    f.scenario = {"who_writes": "Человек по объявлению, в жару.", "vehicle": "Hyundai Solaris 2019",
                  "what_happens": "Цена и «сегодня реально попасть?». Утро занято; 13:30 или 17:00. Он берёт 17:00.",
                  "facts": {"booked": "%s 17:00, west" % d, "public_pages_used": []}}
    f.floating = [fl("сегодня", d, d, "adverb"), fl("сегодня на 13:30 или на 17:00", d, d, "adverb"), fl("сегодня, 17:00", d, d, "adverb")]
    c = avito(f, "c1", "west", 247, "Айдар", 63, "Заправка и ремонт автокондиционеров. Казань, Техническая", opened_note="a new Avito chat: one per listing and buyer")
    c.c(d + " 09:40:10", "Здравствуйте, заправка кондера сколько стоит? сегодня реально попасть?")
    c.d("09:40:55", "d1", "Здравствуйте! Заправка кондиционера с вакуумированием (R134a) стоит 3 800 ₽. Время на сегодня уточню. Какая у вас машина и какого года?")
    c.s(24, "09:47:30", "Айдар, здравствуйте! Это Камила, «Ермак-Сервис» на Технической. Заправка с вакуумированием — 3 800 ₽, это для фреона R134a, занимает около часа. Утро занято, давайте сделаем так: сегодня на 13:30 или на 17:00. Какая у вас машина и какого года? От этого зависит фреон.", edit="d1")
    c.c("09:52:15", "солярис 2019. на 17 давайте")
    c.d("09:52:55", "d2", "Хорошо, Айдар. Сегодня в 17:00 ждём вас.")
    c.s(24, "09:55:20", "Записала: сегодня, 17:00, заправка кондиционера, Solaris 2019, фреон R134a, 3 800 ₽. Адрес: Казань, улица Техническая, 30. Если кондиционер не холодит совсем, сначала проверим систему на утечку, диагностика 900 ₽; без вашего согласия ничего не делаем.", edit="d2")
    c.c("09:57:05", "ок")
    c.d("09:57:45", "d3", "До встречи в 17:00!")
    c.s(24, "09:58:30", "До встречи в 17:00!", use="d3")
    c.label(24, "09:58:50", "запись")
    c.res(24, "09:59:10")
    c.reads_extra = {"operator_credit": "slot 24: first answer {first} minutes (her ledger row is 7), three replies, two drafts edited and one sent as it was, one resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 24; the assistant drafts", "outcome": "заправка кондиционера в тот же день, 17:00, west; закрыт слотом 24",
               "facts": ["the price given is 3 800 for R134a", "the morning was full; she offered 13:30 or 17:00", "a leak check, 900, is named as the step if the system is empty"], "questions": []}
    f.why = ["Она называет себя и сервис: на Авито человек не знает, с кем говорит.", "«Утро занято, давайте сделаем так»: отказ, который клиент слышит как согласие.", "Вопрос про машину и год — не формальность: от него зависит фреон и цена."]
    f.new_facts = ["Объявление сервиса на Авито «Заправка и ремонт автокондиционеров. Казань, Техническая».", "«Айдар», Hyundai Solaris 2019: заправка кондиционера на west в первый рабочий день слота 24 начиная со вторника недели T-17, 17:00.", "У контакта нет картинки."]
    return f


def f25():
    f = File(CFG, 25, "R13", "web-one-question",
             "Непонятно, а после одного вопроса понятно: «а вы компьютер делаете?»",
             "Rule R13 on the web chat. The customer names a tool, not a need. The assistant asks one plain question (what is wrong with the car?) and the answer settles it: the check-engine lamp, for three days. It prices the diagnosis, hands over, and its note says what was asked. The advisor's own question (steady or blinking) is need discovery, not a second loop.")
    f.cast = {"customer": cust("Сергей", "LADA Priora 2012; в сервисе впервые", first_time=True, phone="+7 907 302-71-45"),
              "named_in_a_line": [{"slot": 17, "name": "Артём Николаев", "role": "примет машину на следующий день"}]}
    f.staff(16)
    d = f.day(wk("Wed", 13), "the Wednesday of week T-13 (DESIGN.md section 6, row 25); a working day of slot 16")
    f.day(wk("Thu", 13), "«завтра, четверг»: slot 17's shift")
    f.p("1 200 ₽", "компьютерная диагностика двигателя: считывание и анализ ошибок", job="check_engine_diag")
    f.scenario = {"who_writes": "Человек, который знает, что есть «компьютер», и не знает, как это называется.", "vehicle": "LADA Priora 2012",
                  "what_happens": "Один уточняющий вопрос; потом цена, передача заявки и два времени от Светланы.",
                  "facts": {"booked": "четверг недели T-13, 18:00, east; принимает слот 17", "public_pages_used": ["прайс: компьютерная диагностика двигателя"]},
                  "unclear": {"kind": "vague: names a tool («компьютер») instead of what is wrong", "loops": 1, "resolved": True,
                              "how": "Ассистент спрашивает, что с машиной: горит ошибка на панели или что-то не работает. Ответ: «чек горит третий день»."}}
    f.floating = [fl("третий день", d, "since two days before", "accusative"), fl("завтра после работы", d, "the Thursday of week T-13", "adverb"), fl("Завтра после работы", d, "the Thursday of week T-13", "adverb"),
                  fl("Завтра в 18:00", d, "the Thursday of week T-13", "adverb"), fl("завтра, четверг, 18:00", d, "the Thursday of week T-13", "adverb, nominative"), fl("Завтра вас примет", d, "the Thursday of week T-13", "adverb")]
    c = web(f, "c1", "east", 835, 25)
    c.c(d + " 13:15:10", "здравствуйте. а вы компьютер делаете?")
    c.a("13:15:34", HELLO + "Уточните, пожалуйста, что с машиной: на панели горит ошибка или что-то не работает? Тогда подскажу, какая услуга нужна.")
    c.c("13:16:20", "чек горит третий день. приора 2012")
    c.a("13:16:46", "Понял, спасибо. Когда горит «чек», нужна компьютерная диагностика двигателя: считывание и анализ ошибок, 1 200 ₽. Мастер скажет, что нашёл, и только потом посчитает ремонт. Передать заявку, чтобы вас записали?")
    c.c("13:17:15", "да, в новый город, завтра после работы")
    c.a("13:17:40", "Сам записать я не могу, но заявку передам. Напишите, пожалуйста, как к вам обращаться и номер телефона.")
    c.c("13:18:05", "Сергей 89073027145")
    c.a("13:18:28", "Спасибо, Сергей. " + SAID)
    c.h("13:18:29", "scheduling", "Сергей", "+7 907 302-71-45", "новый город",
        "Сергей, LADA Priora 2012. Сначала спросил, «делаем ли мы компьютер»; я один раз уточнил, что с машиной: горит «чек», третий день. Назвал компьютерную диагностику двигателя, 1 200 ₽. Хочет приехать завтра после работы, Новый город.",
        "east", "%s 20:00, закрытие дня" % d)
    c.s(16, "13:24:40", "Сергей, добрый день! Это Светлана, сервис в Новом городе. Чек третий день — правильно, что не стали ждать дальше, Сергей. Завтра после работы могу записать вас на 17:30 или на 18:00, диагностика занимает минут тридцать, стоит 1 200 ₽. Подскажите ещё: чек горит ровно или мигает? Если мигает, на машине лучше не ездить.")
    c.c("13:27:30", "ровно. на 18")
    c.d("13:28:10", "d1", "Хорошо, Сергей. Завтра в 18:00 ждём вас: 10-й Инженерный проезд, 30.")
    c.s(16, "13:30:20", "Записала, Сергей: завтра, четверг, 18:00, компьютерная диагностика двигателя, Приора, 1 200 ₽. Адрес: 10-й Инженерный проезд, 30. Раз горит ровно, доехать можно спокойно. Завтра вас примет Артём, я ему всё передам.", edit="d1")
    c.label(16, "13:30:40", "запись")
    c.res(16, "13:31:00")
    c.reads_extra = {"operator_credit": "the chat's first answer is nobody's; slot 16: her first line {first} minutes after the hand-off, two replies, one draft edited, one resolved"}
    f.truth = {"reason": "a symptom", "handled": "assistant first, handed over (scheduling), slot 16", "outcome": "компьютерная диагностика на следующий день, 18:00, east; закрыт слотом 16",
               "facts": ["unclear first message; clear after one question by the assistant", "the hand-off note carries his own words and says what was asked", "the price named is the diagnosis, 1 200"], "questions": []}
    f.why = ["По слову «компьютер» ассистент работу не угадывает: спрашивает, что с машиной.", "Заметка избавляет приёмщика от вопроса, который ассистент уже задал.", "«Ровно или мигает» — тот вопрос, который судья звонков засчитал бы за выяснение потребности."]
    f.new_facts = ["Сергей, +7 907 302-71-45, LADA Priora 2012: компьютерная диагностика двигателя на east в четверг недели T-13, 18:00; принимает слот 17."]
    return f


def f26():
    f = File(CFG, 26, "R13", "telegram-two-questions",
             "Непонятно, и понятно только после двух вопросов: «мне бы то же самое, что весной»",
             "Rule R13 on a drafts channel, with the flagship's fourth advisor. The clarifying question is the draft; she writes her own over it, slowly and correctly. The first answer («ну колёса») does not settle it, because in the spring there were two jobs. She asks again by naming both, and the answer is: both. The last draft goes out as it was, and she adds one line of her own. Booked, labelled, resolved; the address is not in it.")
    f.cast = {"customer": cust("Николай Иванович Кузьмин", "пожилой постоянный клиент сервиса на Московском шоссе; Toyota Corolla 2010; в апреле менял шины на летние, в мае делал сход-развал")}
    f.staff(29)
    d = f.day(wk("Wed", 6), "the Wednesday of week T-6 (DESIGN.md section 6, row 26); a working day of slot 29")
    f.day(wk("Thu", 6), "«завтра, четверг»")
    f.day(wk("Sun", 6), "«на воскресенье»")
    f.p("3 000 ₽", "сезонная замена шин с балансировкой, класс car; и сход-развал на две оси: обе работы стоят по 3 000", job="seasonal_tyre_change")
    f.scenario = {"who_writes": "Постоянный клиент, который уверен, что Татьяна помнит.", "vehicle": "Toyota Corolla 2010",
                  "what_happens": "Два вопроса, прежде чем просьба становится ясной; потом запись на обе работы на следующий день.",
                  "facts": {"history": "в апреле — сезонная замена шин на летние; в мае — сход-развал", "booked": "четверг недели T-6, 11:00, main: сезонная замена шин и сход-развал",
                            "alignment": "сход-развал на две оси — тоже 3 000 (catalogue.json wheel_alignment)", "public_pages_used": []},
                  "unclear": {"kind": "two requests in one: «то же самое, что весной» is two jobs, and he wants both", "loops": 2, "resolved": True,
                              "how": "Татьяна спрашивает, какую работу он имеет в виду; ответ — «ну колёса». Она называет обе весенние работы и спрашивает, какая нужна; оказывается, обе: переобуть и чтобы не тянуло вправо."}}
    f.floating = [fl("весной", d, "April and May", "instrumental"), fl("Весной", d, "April and May", "instrumental"), fl("В апреле", d, "April", "в + prepositional"), fl("в мае", d, "May", "в + prepositional"),
                  fl("на завтра на 11:00", d, "the Thursday of week T-6", "на + accusative"), fl("на воскресенье на 10:00", d, "the Sunday of week T-6", "на + accusative"),
                  fl("завтра в 11", d, "the Thursday of week T-6", "adverb"), fl("Завтра в 11:00", d, "the Thursday of week T-6", "adverb")]
    c = tg(f, "c1", "main", 2650, "Николай Иванович", opened_note=LATER)
    c.c(d + " 10:20:10", "Татьяна, здравствуйте. Мне бы то же самое сделать, что весной делали")
    c.d("10:20:55", "d1", "Здравствуйте! Подскажите, пожалуйста, какую именно работу вы имеете в виду?")
    c.s(29, "10:32:30", "Николай Иванович, здравствуйте. Подскажите, пожалуйста, какую именно работу вы имеете в виду? Весной вы были у нас дважды.")
    c.c("10:36:15", "ну колёса")
    c.d("10:36:55", "d2", "Уточните, пожалуйста: вам нужно поменять шины на зимние или что-то ещё по колёсам?")
    c.s(29, "10:44:10", "Уточню, чтобы записать вас правильно. В апреле мы меняли вам шины на летние, а в мае делали сход-развал. Сейчас нужно поставить зимние шины или снова проверить развал?")
    c.c("10:49:30", "зимние поставить. и чтоб вправо не тянуло, а то опять ведёт")
    c.d("10:50:10", "d3", "Понятно, спасибо. Сезонная замена шин с балансировкой стоит 3 000 ₽. Если машину ведёт вправо, стоит проверить углы установки колёс: сход-развал на две оси стоит 3 000 ₽. Когда вам удобно подъехать?")
    c.s(29, "10:58:40", "Теперь понятно, Николай Иванович: нужно и то и другое. Сезонная замена шин с балансировкой стоит 3 000 ₽, сход-развал на две оси — ещё 3 000 ₽. Развал лучше делать сразу после замены шин. Могу записать вас на завтра на 11:00 или на воскресенье на 10:00, обе работы займут около двух часов. Какой день вам подходит?", edit="d3")
    c.c("11:03:20", "завтра в 11")
    c.d("11:04:00", "d4", "Хорошо, Николай Иванович. Завтра в 11:00 ждём вас.")
    c.s(29, "11:12:15", "Хорошо, Николай Иванович. Завтра в 11:00 ждём вас.", use="d4")
    c.s(29, "11:13:40", "Зимние шины, пожалуйста, привезите с собой.")
    c.label(29, "11:14:00", "шины")
    c.res(29, "11:14:20")
    c.reads_extra = {"operator_credit": "slot 29: first answer {first} minutes (her ledger row is 12), five replies, two drafts discarded, one edited and one sent as it was, one resolved"}
    f.truth = {"reason": "to book or ask for a slot", "handled": "slot 29; the assistant drafts", "outcome": "сезонная замена шин и сход-развал на следующий день, 11:00, main; закрыт слотом 29",
               "facts": ["unclear first message; clear after two questions by slot 29", "what he asked for («то же, что весной») was two jobs; he wanted both", "each job is 3 000"], "questions": []}
    f.why = ["Второй черновик ассистента угадывает одну работу; Татьяна называет две, которые были на самом деле.", "Полные предложения, ни одного смайлика, «Николай Иванович» в каждой второй реплике.", "В подтверждении есть день, время и работа; адреса нет: его она обычно забывает (cast.json)."]
    f.new_facts = ["Николай Иванович Кузьмин (в Telegram «Николай Иванович»), Toyota Corolla 2010, постоянный клиент main: в апреле сезонная замена шин, в мае сход-развал; запись на четверг недели T-6, 11:00: сезонная замена шин и сход-развал.",
                   "У контакта нет картинки."]
    return f


def f27():
    f = File(CFG, 27, "R13", "avito-never-clear",
             "Непонятно и так и не прояснилось: «сколько стоит стойки поменять»",
             "Rule R13 on Avito, the session that ends unclear. «Стойки» is two different parts. The assistant's draft is the clarifying question; slot 17 writes a price for his first reading over it, is corrected, guesses a second time, and when the customer says he needs only one, the right question goes out an hour later, as the draft wrote it. Nobody answers it. Chatwoot resolves the chat after seven silent days.")
    f.cast = {"customer": cust("Эдуард", "пишет по объявлению; машина не названа", first_time=True)}
    f.staff(17)
    d = f.day(wk("Wed", 2), "the Wednesday of week T-2 (DESIGN.md section 6, row 27); a working day of slot 17")
    f.day(wk("Wed", 2, plus=7), "Chatwoot resolves the chat after 7 silent days")
    f.p("3 700", "замена стоек стабилизатора передних, пара, класс car", job="sway_bar_links")
    f.p("18 580", "замена передних амортизаторных стоек, пара, класс car", job="front_struts_pair")
    f.scenario = {"who_writes": "Человек по объявлению, который называет деталь так, как её называют в гараже.", "what_happens": "Три реплики клиента, две догадки приёмщика, один правильный вопрос через час, тишина.",
                  "facts": {"public_pages_used": [], "note": "Ни машина, ни ось, ни сторона так и не названы; цену на одну стойку никто не посчитал."},
                  "unclear": {"kind": "one word, two parts: «стойки» are sway bar links or strut assemblies; then one of a pair", "loops": 2, "resolved": False,
                              "how": "Черновик спрашивает, какие стойки и какая машина. Артём вместо вопроса называет цену стоек стабилизатора; клиент: «не. которые большие». Артём называет пару передних амортизаторных стоек; клиент: «мне только одну. ладно». Вопрос из третьего черновика уходит через час, ответа нет."}}
    f.floating = []
    c = avito(f, "c1", "east", 261, "Эдуард", 57, "Ремонт ходовой, диагностика подвески. Новый город", opened_note="a new Avito chat: one per listing and buyer")
    c.c(d + " 15:10:05", "здравствуйте сколько стоит стойки поменять")
    c.d("15:10:50", "d1", "Здравствуйте! Уточните, пожалуйста: вам нужны амортизаторные стойки или стойки стабилизатора? И какая у вас машина?")
    c.s(17, "15:21:40", "Здравствуйте! Стойки стабилизатора 3 700 за пару с работой. Когда подъедете?")
    c.c("15:25:10", "не. которые большие")
    c.d("15:25:50", "d2", "Понял, амортизаторные стойки. Уточните, пожалуйста: передние или задние? И какая у вас машина и какого года: от этого зависит цена.")
    c.s(17, "15:33:30", "А, амортизаторы. Передние 18 580 за пару с работой, всё сделаем")
    c.c("15:36:40", "да не. мне только одну. ладно")
    c.d("15:37:20", "d3", "Уточните, пожалуйста, с какой стороны и на какой оси стойка и какая у вас машина: посчитаем точно. Стойки обычно меняют парой на одной оси.")
    c.s(17, "16:35:05", "Уточните, пожалуйста, с какой стороны и на какой оси стойка и какая у вас машина: посчитаем точно. Стойки обычно меняют парой на одной оси.", use="d3", late="второй вопрос может ждать час (cast.json)")
    c.auto()
    c.reads_extra = {"operator_credit": "slot 17: first answer {first} minutes (his ledger row is 11), three replies, two drafts discarded and one sent as it was, nothing resolved"}
    f.truth = {"reason": "what a job costs", "handled": "slot 17; the assistant drafts", "outcome": "просьба осталась неясной; закрыт по 7 дням тишины",
               "facts": ["the request was never made clear", "both discarded drafts were the clarifying questions; slot 17 answered his first reading twice (3 700, then 18 580)",
                         "the right question was sent 58 minutes after the customer's last line and got no answer"], "questions": []}
    f.why = ["Оба выброшенных черновика — вопросы, которые прояснили бы просьбу за минуту.", "Клиент не становится яснее от того, что ему называют цену: он уходит.",
             "Неясных клиентов у слабого приёмщика столько же, сколько у сильного; неясных итогов — больше (DESIGN.md, раздел 4)."]
    f.new_facts = ["Объявление сервиса на Авито «Ремонт ходовой, диагностика подвески. Новый город».", "«Эдуард»: спрашивал замену «стоек», машину не назвал, не приехал.", "У контакта нет картинки."]
    return f


FILES = [f09, f10, f11, f12, f13, f14, f15, f16, f17, f18, f19, f20, f21, f22, f23, f24, f25, f26, f27]
