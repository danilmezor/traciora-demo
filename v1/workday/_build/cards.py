# The hand-written cards of the board, both languages side by side. Built into en/cards.json and
# ru/cards.json by build.py. Anchors and times: DESIGN.md section 7.
# A text may hold {day:ANCHOR}, {month:ANCHOR} and {ledger:key}: the seeder renders them for its T.


def L(en, ru):
    return {"en": en, "ru": ru}


# (slot, role, added_by, added_at, part_done_at)
def part(slot, role, by, at, done=None):
    return {"slot": slot, "role": role, "added_by": by, "added_at": at, "part_done_at": done}


# One trail step after "created" (and the first "assigned", which build.py writes from owner0).
def step(at, by, verb, **more):
    return {"at": at, "by": by, "verb": verb, **more}


CARDS = [
    # ------------------------------------------------------------------ S16
    dict(
        id="S16-review", story="S16", kind="task", origin="human", site="main", priority="high",
        state="started", owner=6, owner0=6, by=4, at="W-1.mon@o+1:10", due="p6+2@12:00",
        title=L("Prepare Nickajack Delivery's quarterly review",
                "Подготовить квартальный обзор по «Симбирскому гонцу»"),
        desc=L("The review is {day:S16meet} at 10:00 with Claire and me. One page: visits and spend by month "
               "since {month:G}, what their vans needed most, and how many days they take to pay now. "
               "Donna has the statement, Marcus the parts.",
               "Встреча {day:S16meet} в 10:00, будут Екатерина Николаевна и я. Одна страница: заезды и выручка "
               "по месяцам с {month:G}, что чаще всего делали на их машинах и за сколько дней они теперь платят. "
               "Акт сверки у Ирины Владимировны, запчасти у Паши."),
        why=L("They pay later every month; Claire wants it on the table at the review.",
              "Платят всё позже; Екатерина Николаевна хочет обсудить это на встрече."),
        parts=[part(3, "participant", 4, "W-1.mon@o+1:10"),
               part(9, "participant", 4, "W-1.mon@o+1:10", done="W-1.thu@o+6:20"),
               part(2, "observer", 2, "W-1.mon@o+2:05")],
        trail=[
            step("W-1.mon>=p6@o+5:30", 6, "moved", to="started"),
            step("W-1.thu@o+3:00", 3, "attached",
                 file=L("Nickajack Delivery statement {month:T}.pdf", "Акт сверки Симбирский гонец {month:T}.pdf"),
                 note="generated per build: its numbers equal the ERP's at T (card S16)"),
            step("W-1.thu@o+6:15", 9, "comment", body=L(
                "Their vans since {month:G}, by count: brakes first, then batteries, then wipers. "
                "Full list by van is in the parts report under the account. Done on my side.",
                "По их машинам с {month:G}: больше всего колодок, дальше аккумуляторы и щётки. "
                "Полный список по машинам — в отчёте по запчастям клиента. Моя часть готова.")),
            step("W-1.thu@o+6:20", 9, "part_done"),
            step("p6-2@o+4:10", 6, "comment", body=L(
                "Visits and spend by month are in the draft. Still missing: the days-to-pay table.",
                "Заезды и выручка по месяцам уже в черновике. Не хватает одного: за сколько дней они платят, по месяцам.")),
            step("p4-1@c-0:40", 4, "comment", mentions=[3], body=L(
                "@Donna Ledford: Maya needs the days-to-pay table before noon on {day:p6+2}. "
                "The statement is already on the card.",
                "@Ирина Владимировна Кудашкина, Хасановой нужна таблица по срокам оплаты до 12:00 {day:p6+2}. "
                "Акт сверки уже на карточке.")),
        ],
    ),
    # ------------------------------------------------------------------ S06
    dict(
        id="S06-supplier", story="S06", kind="task", origin="human", site="west", priority="high",
        state="unstarted", owner=22, owner0=22, by=2, at="W-7.mon@o+1:20", due="W-3.mon@c-0:30",
        title=L("Move Charlotte Pike's parts ordering to Sequoyah",
                "Перевести Техническую на ульяновского поставщика"),
        desc=L("Marcus takes the ordering from East Main. Harpeth Valley stays for what Sequoyah cannot "
               "bring the next day. Tell Harpeth Valley, switch the order sheet, start with brakes.",
               "Заказы берёт на себя Мещеряков с Московского шоссе. «Казань-АвтоСнаб» остаётся для того, "
               "что «АвтоДеталь-Венец» не привезёт на следующий день. Предупредить «Казань-АвтоСнаб», "
               "поменять бланк заказа, начать с тормозов."),
        why=L("Harpeth Valley is on time on six orders in ten; Sequoyah on nine.",
              "«Казань-АвтоСнаб» привозит в срок шесть заказов из десяти, «АвтоДеталь-Венец» — девять."),
        trail=[
            step("W-5.mon@o+2:00", 2, "comment", body=L(
                "Dale, two weeks in. What is in the way? Marcus is ready to take the orders.",
                "Ринат Фаридович, прошло две недели. Что мешает? Мещеряков готов забрать заказы.")),
            step("W-5.tue@o+4:00", 22, "comment", body=L("will do", "принял")),
            step("W0.mon@o+0:50", 2, "comment", body=L(
                "Three weeks past due. I need a date from you today.",
                "Срок вышел три недели назад. Сегодня мне нужна от вас дата.")),
        ],
    ),
    # ------------------------------------------------------------------ S01
    dict(
        id="S01-a5-callback", story="S01", kind="task", origin="human", site="west", priority="high",
        state="unstarted", owner=22, owner0=22, by=2, at="W-18.mon@o+1:30", due="W-18.wed@c-0:30",
        title=L("Call Cumberland Bend Electric back", "Перезвонить в «Идель-Электромонтаж»"),
        desc=L("Wade Carlisle, their operations manager. Two of their vans came back on brakes, the last bill "
               "is disputed and unpaid, and he has rung since without an answer. Ring him, hear him out, "
               "tell me what he wants.",
               "Рустем Ильгизович Фаттахов, заместитель директора по производству. Две их машины вернулись "
               "по тормозам, последний счёт оспорен и не оплачен, после этого он звонил и не дозвонился. "
               "Позвоните, выслушайте и напишите мне, чего он хочет."),
        why=L("Eleven vans, and no order since their last visit.",
              "Одиннадцать машин, и ни одного заезда после последнего визита."),
        trail=[
            step("W-16.mon@o+2:10", 2, "comment", body=L(
                "Dale, did you reach Wade Carlisle?", "Ринат Фаридович, дозвонились до Фаттахова?")),
            step("W-16.tue@o+5:00", 22, "comment", body=L("will call him", "позвоню")),
            step("W0.mon@o+0:55", 2, "comment", body=L(
                "Still open. He rang us four times in ten days. Call him this week or I will.",
                "Карточка всё ещё открыта. Он звонил нам четыре раза за десять дней. "
                "Позвоните ему на этой неделе, или это сделаю я.")),
        ],
    ),
    # ------------------------------------------------------------------ the two quiet cards
    dict(
        id="Q-22-regulars", story="board", kind="task", origin="human", site="west", priority="normal",
        state="unstarted", owner=22, owner0=22, by=2, at="W-4.mon@o+1:40", due="W-3.fri@c-0:30",
        title=L("List Charlotte Pike regulars not seen in six months",
                "Список постоянных клиентов Технической, не приезжавших полгода"),
        desc=L("Name, vehicle, last visit, what was done. Jasmine can pull it; you know who is worth a call.",
               "Имя, машина, дата последнего визита, что делали. Выгрузить может Камила; кому стоит "
               "позвонить, знаете вы."),
        why=L("Fourteen months in and I still cannot see who stopped coming.",
              "Прошло четырнадцать месяцев с покупки, а я до сих пор не вижу, кто перестал ездить."),
        trail=[step("W-4.tue@o+6:30", 22, "comment", body=L("will do", "сделаем"))],
        quiet=dict(asked_at="W-3.wed@05:30", asked_of=[22], answered=None),
    ),
    dict(
        id="Q-04-rack", story="board", kind="task", origin="human", site="east", priority="low",
        state="backlog", owner=4, owner0=4, by=4, at="W-3.wed@o+7:10", due=None,
        title=L("Bonny Oaks: two quotes for a second alignment rack",
                "Инженерный: два предложения на второй стенд сход-развала"),
        desc=L("Installed price and lead time from two dealers. Alignments back up there in a busy week.",
               "Цена с монтажом и срок поставки от двух поставщиков. В загруженную неделю запись на развал "
               "там уходит на дни вперёд."),
        why=L(None, None),
        trail=[],
        quiet=dict(asked_at="W-2.thu@05:30", asked_of=[4], answered=None),
    ),
    # ------------------------------------------------------------------ the one card nobody owns
    dict(
        id="H-east-waiting", story="board", kind="escalation", origin="model", origin_ref="chat:{session}",
        template="Customer handover", site="east", priority="high",
        state="backlog", owner=None, owner0=None, by="A", at="T@T-0:40", due="T@close",
        title=L("{visitor_name} asked for a person", "{visitor_name} просит связаться с сотрудником"),
        desc=L("{visitor_name} asked to be put through to somebody. In their words: I'd rather talk to a person. "
               "It's about a noise in my truck and it's hard to describe.\n\nRing them on {visitor_phone}.",
               "{visitor_name} просит соединить с сотрудником. Его слова: Лучше я с человеком поговорю. "
               "Стук в машине, словами не объяснишь.\n\nПерезвонить: {visitor_phone}."),
        why=L("Asked for a person in the assistant (escalation); nobody has called back yet.",
              "Попросил сотрудника в чате с помощником; пока никто не перезвонил."),
        trail=[],
        rests_on="the web chat handed over at east 40 minutes before T (conversations state at T); "
                 "the name, the phone and the quoted line are that chat's, the words here are a stand-in",
        source=dict(event="customer.handover_requested", role="trigger"),
    ),
    # ------------------------------------------------------------------ S08
    dict(
        id="S08-complaint", story="S08", kind="task", origin="human", site="main", priority="high",
        state="completed", owner=4, owner0=None, by=5, at="p7-4>p5@c-2:10", due=None,
        title=L("Daugherty, 2011 Outback: quoted {ledger:s8.price_quoted}, billed {ledger:s8.bill_before_tax}",
                "Фомичёв, Logan: назвали {ledger:s8.price_quoted}, в наряде {ledger:s8.bill_list}"),
        desc=L("Caleb quoted the timing belt at {ledger:s8.price_quoted} off the service page and told him same day. "
               "Car was ready a day late and the bill is {ledger:s8.bill_before_tax} before tax. He argued at the "
               "counter and rang again this afternoon. I told him a manager would call tommorow. He wants the "
               "difference back.",
               "Никита посчитал ремень ГРМ по странице услуги — {ledger:s8.price_quoted} — и пообещал отдать "
               "в тот же день. Машина была готова на день позже, в наряде {ledger:s8.bill_list}. Клиент ругался "
               "на приёмке и после обеда позвонил ещё раз. Я сказал, что завтра ему перезвонит руководитель. "
               "Хочет вернуть разницу."),
        why=L("Call back promised for tomorrow.", "Обещан звонок на завтра."),
        trail=[
            step("p7-4>p5>p4@o+0:40", 4, "assigned", to=4),
            step("p7-4>p5>p4@o+0:41", 4, "moved", to="started"),
            step("p7-4>p5>p4@o+3:00", 4, "comment", body=L(
                "Called Frank Daugherty back before noon. Took {ledger:s8.discount} off, approved on the order; "
                "he paid {ledger:s8.paid_with_tax} and is fine. Caleb: prices come from the price list, see your card.",
                "Перезвонил Фомичёву до обеда. Снял {ledger:s8.discount}, отметка в наряде; к оплате "
                "{ledger:s8.paid_with_tax}, заберёт сегодня после работы. Ведяшкин: цены берём из прайса, "
                "карточка у тебя.")),
            step("p7-4>p5>p4@o+3:05", 4, "completed"),
        ],
    ),
    dict(
        id="S08-prices", story="S08", kind="task", origin="human", site="main", priority="normal",
        state="completed", owner=7, owner0=7, by=4, at="p7-4>p5>p4@o+3:10", due="p7-4>p5>p4>=p7@c-1:00",
        title=L("Prices come from the price list", "Цены — только из прайс-листа"),
        desc=L("From today every price you say on the phone comes from the price list page, not from a service "
               "page. Read it and reply here.",
               "С сегодняшнего дня любую цену по телефону называешь со страницы прайс-листа, а не со страницы "
               "услуги. Прочитай её и отпишись здесь."),
        why=L(None, None),
        trail=[
            step("p7-4>p5>p4>=p7@c-2:00", 7, "comment", body=L(
                "Read it. I also saved a note so the assistant reminds me. Sorry about Mr. Daugherty.",
                "Прочитал. Ещё сохранил заметку для помощника, чтобы напоминал. Перед Игорем Валентиновичем "
                "неудобно вышло.")),
            step("p7-4>p5>p4>=p7@c-1:58", 7, "completed"),
        ],
    ),
    # ------------------------------------------------------------------ S03
    dict(
        id="S03-early-desk", story="S03", kind="task", origin="human", site="main", priority="normal",
        state="completed", owner=4, owner0=4, by=4, at="W-4.mon@o+3:00", due="W-3.mon@o+1:00",
        title=L("Add an early desk shift at East Main", "Вторая смена на приёмке с открытия (Московское шоссе)"),
        desc=L("Mornings we miss three calls in ten; the rest of the day, one in twelve. Two advisors from "
               "opening, cover at the desk raised to two until 10:00. New shift template, then publish.",
               "С утра пропускаем три звонка из десяти, в остальное время — один из двенадцати. Оба "
               "мастера-приёмщика смены выходят с 9:00, норма на приёмке до 11:30 — двое. Новый шаблон смены, "
               "потом публикация."),
        why=L("One advisor checks cars in and the phones ring out.",
              "Один принимает машины, и телефон в это время никто не берёт."),
        trail=[
            step("W-4.tue@o+1:00", 4, "moved", to="started"),
            step("W-3.mon@o+0:25", 4, "comment", body=L(
                "Early desk is in this week's roster: two from 7:30, one late. Cover rule changed from today.",
                "С этой недели оба мастера смены с 9:00. Норма на приёмке изменена с сегодняшнего дня.")),
            step("W-3.mon@o+0:30", 4, "completed"),
        ],
    ),
    # ------------------------------------------------------------------ S07
    dict(
        id="S07-handover", story="S07", kind="task", origin="model", origin_ref="chat:{session}",
        template="Customer handover", site="main", priority="normal",
        state="completed", owner=6, owner0=None, by="A",
        at=L("p6-14>-1d@21:15", "p6-10>-1d@21:15"), due=L("p6-14@close", "p6-10@close"),
        title=L("Rachel Dunlap asked for a person", "Ольга просит связаться с сотрудником"),
        desc=L("Rachel Dunlap asked to be put through to somebody. In their words: 2014 Honda CR-V. Scraping sound "
               "when she presses the brake, mostly in the morning; the red BRAKE light is on (photo in the chat). She "
               "first asked what it costs to fix a noise; I asked once whether it was when braking or when turning, and "
               "she said braking. Wants a brake inspection on Tuesday morning before work, East Main Street.\n\n"
               "Ring them on (423) 555-0131.",
               "Ольга просит соединить с сотрудником. Её слова: Hyundai Solaris 2016. Скрежет спереди при нажатии "
               "на тормоз, в основном по утрам. Сначала спросила, сколько стоит «посмотреть шум»; я один раз уточнил, "
               "при торможении он или при повороте руля: при торможении. Муж считает, что это подшипник. Просит "
               "записать на диагностику тормозов в воскресенье с утра, Московское шоссе.\n\n"
               "Перезвонить: +7 907 378-60-35."),
        why=L("Asked for a person in the assistant (scheduling); nobody has called back yet.",
              "Попросила сотрудника в чате с помощником; пока никто не перезвонил."),
        trail=[
            step(L("p6-14@o+0:20", "p6-10@o+0:20"), 6, "assigned", to=6),
            step(L("p6-14@o+0:45", "p6-10@o+0:45"), 6, "comment", body=L(
                "Booked for tomorrow 9:00 and confirmed by phone.",
                "Записала на завтра на 9:30, в чате она подтвердила. Днём ещё наберу.")),
            step(L("p6-14@o+0:46", "p6-10@o+0:46"), 6, "completed"),
        ],
        rests_on=L("S7's first web chat; the words are that chat's hand-off note (conversations/en/01, n 13)",
                   "S7's first web chat; the words are that chat's hand-off note (conversations/ru/01, n 12)"),
        source=dict(event="customer.handover_requested", role="trigger"),
    ),
    # ------------------------------------------------------------------ the foreman's second looks
    dict(
        id="F-recheck-call29", story="people (call 29)", kind="task", origin="human", site="main",
        priority="high", state="completed", owner=8, owner0=8, by=5,
        at=L("W-10.fri@11:40", "W-10.fri@18:00"), due=L("W-10.fri@16:00", "W-10.fri@20:00"),
        title=L("Look again: Malibu lower control arm, wheel sits crooked",
                "Посмотреть ещё раз: Lancer, не затянуты гайки колеса"),
        desc=L("Phil Cantrell, 2014 Malibu. Dustin did the driver's lower control arm Tuesday, no alignment on "
               "the ticket. Wheel is off-centre and it drifts. He's back at 2:00 today, no charge. Randy, check "
               "the arm and put it on the rack.",
               "Денис Маркелов, Lancer X 2011. Вчера Рябов менял передние колодки и диски, на левом переднем "
               "гайки не протянуты, клиент встал на объездной. Едет к нам потихоньку. Михалыч, сними оба "
               "колеса, проверь шпильки и диски, протяни всё ключом."),
        why=L("Customer back at 2:00 today.", "Клиент будет в течение часа."),
        trail=[
            step(L("W-10.fri@15:10", "W-10.fri@19:20"), 8, "comment", body=L(
                "arm was fine. toe was out, set it. told dustin to his face",
                "шпильки целые, диски в норме, протянул оба колеса. рябову сказал при всех")),
            step(L("W-10.fri@15:11", "W-10.fri@19:21"), 8, "completed"),
        ],
    ),
    dict(
        id="F-recheck-open", story="board", kind="task", origin="human", site="main", priority="high",
        state="unstarted", owner=8, owner0=8, by=5, at="p5-1@c-1:30", due="p5-1>p8@c-1:30",
        title=L("Look again: Dogwood Lane Florals van, rear brakes dragging",
                "Посмотреть ещё раз: Largus цветочного салона, греется задний тормоз"),
        desc=L("2019 ProMaster City. Hunter did the rear pads a few days ago. Driver says the right rear is hot "
               "and smells after ten minutes. Van comes back first thing tomorrow. Randy, pull that wheel "
               "yourself before Hunter touches it.",
               "Largus-фургон ИП Абрамовой. На днях Ваня менял задние колодки. Водитель говорит, справа сзади "
               "греется и пахнет минут через десять. Пригонят завтра к открытию. Михалыч, сними это колесо "
               "сам, до Вани."),
        why=L("Back first thing tomorrow; they deliver mid-morning.", "Завтра к открытию; к обеду у них доставка."),
        trail=[],
        needs="a warranty order at main opened on the due day for this van, pointing at slot 14's order "
              "(one of his planted comebacks, inside the pads' warranty; ledger board.second_look_open); when the due "
              "day falls after T, only an appointment at opening on that day",
    ),
    # ------------------------------------------------------------------ the junior operator's other five
    dict(
        id="J-estimate", story="board", kind="task", origin="human", site="main", priority="normal",
        state="unstarted", owner=6, owner0=6, by=5, at="p5-1@c-1:10", due="T@15:00",
        title=L("Estimate to Clabough Brothers Roofing: Ram 2500 front end",
                "Смета для ИП Трофимова: ГАЗель Next, передняя подвеска"),
        desc=L("Luis found both lower ball joints and the left tie rod end on their 2016 Ram. Price it with "
               "standard parts, add the alignment, send it to their office before three. They want it done "
               "next week.",
               "Лёха нашёл на их ГАЗели люфт обеих нижних шаровых и левого рулевого наконечника. Посчитай "
               "со стандартными запчастями, добавь сход-развал и отправь им до трёх. Делать хотят на "
               "следующей неделе."),
        why=L("The truck is here and they decide on the number.", "Машина у нас, ждут сумму."),
        trail=[],
    ),
    dict(
        id="J-confirm", story="board", kind="task", origin="human", site="main", priority="normal",
        state="started", owner=6, owner0=6, by=6, at="T@o+0:15", due=L("T@15:00", "T@17:00"),
        title=L("Confirm the next day's drop-offs by 3:00", "Подтвердить завтрашние записи до 17:00"),
        desc=L("Call or text each one. A slot nobody confirms is held 30 minutes and then goes to the waiting list.",
               "Каждому позвонить или написать. Неподтверждённую запись держим 30 минут, потом отдаём "
               "следующему из листа ожидания."),
        why=L(None, None),
        trail=[step("T@o+0:16", 6, "moved", to="started")],
    ),
    dict(
        # the hand-over card of S7's return chat (ledger board.open_at_t), in both configurations
        id="S07-return-handover", story="S07", kind="task", origin="model",
        origin_ref="chat:{session}", template="Customer handover",
        site="main", priority="normal", state="unstarted", owner=6, owner0=None, by="A",
        at="p6-1@15:41", due=None,
        title=L("Rachel Dunlap asked for a person",
                "Ольга просит связаться с сотрудником"),
        desc=L("Rachel Dunlap asked to be put through to somebody. In their words: Rachel Dunlap, 2014 Honda CR-V, "
               "East Main. She wants to book the rear shock absorbers she put off at her last visit, some time next "
               "week. I gave her the price-list figure for the pair, $339.28 before shop supplies and tax, and no "
               "time.\n\nRing them on (423) 555-0131.",
               "Ольга просит соединить с сотрудником. Её слова: Ольга, Hyundai Solaris 2016, Московское шоссе. Хочет "
               "записаться на замену задних амортизаторов, которую отложила в прошлый визит, на этой неделе. Я назвал "
               "цену из прайса за пару, 11 720 ₽ с запчастями, время не называл.\n\nПерезвонить: +7 907 378-60-35."),
        why=L("Asked for a person in the assistant (scheduling); nobody has called back yet.",
              "Попросила сотрудника в чате с помощником; пока никто не перезвонил."),
        trail=[step("p6-1@16:05", 6, "assigned", to=6),
               step("p6-1@16:05", 6, "rescheduled", field="due", old="p6-1@close", new=None)],
        note=L("the hand-over of S7's return chat (conversations/en/03, n 6; event customer.handover_requested): raised "
               "unowned at 15:41, taken by slot 6 at 16:05 when she answered the chat; she cleared the due date the "
               "product sets at the day's close, since the booking waits on the customer's answer",
               "the hand-over of S7's return chat (conversations/ru/03, n 6; event customer.handover_requested; the visitor "
               "is Ольга Сергеевна Тимофеева of named_customers.json, whose name the web contact does not hold): raised "
               "unowned at 15:41, taken by slot 6 at 16:05 when she answered the chat; she cleared the due date the "
               "product sets at the day's close, since the booking waits on the customer's answer"),
    ),
    dict(
        id="J-po-numbers", story="S01", kind="task", origin="human", site="main", priority="normal",
        state="unstarted", owner=6, owner0=6, by=3, at="p3-2@o+2:30", due="p6+3@12:00",
        title=L("Nickajack Delivery: purchase-order numbers on their open orders",
                "«Симбирский гонец»: номера заявок в открытых заказ-нарядах"),
        desc=L("Some of their open orders carry no purchase-order number, and their payables office sends such "
               "lines back. Please get the numbers from Lonnie Coffey's office and put them on the orders.",
               "В части их открытых заказ-нарядов нет номера заявки, а без него бухгалтерия «Гонца» документы "
               "не принимает. Прошу уточнить номера в транспортном отделе у Кравцова и внести в наряды."),
        why=L("Without the numbers they pay later still.", "Без номера оплата опять задержится."),
        trail=[],
    ),
    dict(
        id="J-saved-replies", story="board", kind="task", origin="human", site="main", priority="low",
        state="backlog", owner=6, owner0=6, by=6, at="p6-2@o+6:00", due=None,
        title=L("Rewrite my saved replies for tire questions", "Переписать шаблоны ответов про шины"),
        desc=L("Rotation, flat repair, the pressure light. Three short ones.",
               "Переобувка, хранение, датчики давления. Три коротких."),
        why=L(None, None), trail=[],
    ),
    # ------------------------------------------------------------------ the senior operator's own (with Q-04-rack: nine)
    dict(
        id="G-cover-week-off", story="S05", kind="task", origin="human", site="east", priority="high",
        state="started", owner=4, owner0=4, by=4, at="p16-3>=p4@c-1:00", due="W+1.mon@12:00",
        title=L("Cover for Angie's week off", "Кто заменит Демидову на неделе её отпуска"),
        desc=L("She is out {day:S5} to {day:S5>+6d}. Two shifts in it are published and still hers; the draft "
               "days have nobody at her desk. Brenda has weekdays free; Maya can go over on days East Main "
               "keeps two.",
               "Её не будет с {day:S5} по {day:S5>+6d}. Две смены на этой неделе уже опубликованы и пока за ней; "
               "в черновике на её дни на приёмке никого. В свои выходные свободны Николаев, Хасанова и Пахомова."),
        why=L("The draft week publishes Thursday and Bonny Oaks is one short at the desk.",
              "В четверг публикуем следующую неделю, а на Инженерном в её дни приёмка пустая."),
        trail=[
            step("p16-3>=p4@c-0:58", 4, "moved", to="started"),
            step("p16-2@o+2:20", 16, "comment", body=L(
                "Josh has my open estimates and the Millsaps list. I'm reachable the first morning until "
                "we're on the road.",
                "Сергей Анатольевич, открытые сметы и список по «Тёплому контуру» оставила Артёму. В первый "
                "день до обеда я ещё на связи.")),
        ],
    ),
    dict(
        id="G-no-show-talk", story="S14", kind="task", origin="human", site="east", priority="normal",
        state="unstarted", owner=4, owner0=4, by=4, at=L("east-2@c-2:00", "east-2<=p20@c-2:00"), due="p4+1@c-1:00",
        title=L("Talk to Austin about the no-show", "Поговорить с Блиновым про неявку"),
        desc=L("He did not come in and called at ten. Jordan covered. A second job in the evenings is my guess; "
               "ask, don't guess. Before his next shift if I can.",
               "Не вышел, позвонил только к десяти. Подменил Аюпов. Думаю, вторая работа по вечерам, но надо "
               "спросить, а не гадать. По возможности до его следующей смены."),
        why=L("First time, and he was vague about it.", "Первый раз, и объяснить толком не смог."),
        trail=[],
    ),
    dict(
        id="G-open-shift", story="S14", kind="task", origin="human", site="main", priority="normal",
        state="unstarted", owner=4, owner0=4, by=4, at="W0.thu@c-3:30", due="W+1.mon@c-1:00",
        title=L("Fill the open technician shift at East Main ({day:W+1.tue})",
                "Закрыть свободную смену механика на Московском ({day:W+1.tue})"),
        desc=L("Published open and nobody has taken it. Ask Jordan first, then Brandon.",
               "Опубликована без человека, никто не взял. Сначала спросить Карпова (у него выходной), "
               "потом Суркова."),
        why=L("Still open, and it is next week.", "До смены несколько дней, а она всё ещё свободна."),
        trail=[],
    ),
    dict(
        id="G-stocktake", story="S13", kind="task", origin="human", site="main", priority="normal",
        state="started", owner=4, owner0=4, by=4, at="W-1.thu@o+5:00", due="W+1.wed@12:00",
        title=L("Stocktake day: count teams and who locks up at noon",
                "Инвентаризация: кто считает и кто закрывает площадки в 12:00"),
        desc=L("All three shops close at 12:00 on {day:stock}. Count teams of two per shop, last car in by 10:30, "
               "no job over two hours. Marcus runs the sheets; Dale sends his by the end of the day.",
               "{day:stock} все три сервиса закрываются в 12:00. По два человека на пересчёт на площадку, "
               "последняя запись на 10:00, работы не длиннее двух нормо-часов. Ведомости ведёт Мещеряков; "
               "Казань присылает свои до 18:00 по Москве."),
        why=L(None, None),
        trail=[
            step("W-1.thu@o+5:02", 4, "moved", to="started"),
            step("W0.wed@o+3:40", 9, "comment", body=L(
                "Count sheets are printed for all three shops. Any line off by more than 50 dollars gets a recount.",
                "Ведомости на все три площадки распечатал. Расхождение больше 2 000 ₽ по строке — пересчитываем.")),
        ],
    ),
    dict(
        id="G-90-day-review", story="board", kind="task", origin="human", site="main", priority="normal",
        state="unstarted", owner=4, owner0=4, by=2, at="W0.mon@o+1:05", due="W+1.fri@c-0:30",
        title=L("Caleb's 90-day review: write-up", "Ведяшкин: итоги испытательного срока"),
        desc=L("Three months in. I want his call scores by month, the two wrong prices and what changed after "
               "each, and your recommendation. One page.",
               "Три месяца прошло. Мне нужны оценки звонков по месяцам, два случая с неверной ценой и что "
               "изменилось после каждого, и твоя рекомендация. Одна страница."),
        why=L("He passed 90 days this month.", "Три месяца истекли в этом месяце."),
        trail=[],
    ),
    dict(
        id="G-listen-calls", story="S04", kind="task", origin="human", site="main", priority="normal",
        state="started", owner=4, owner0=4, by=4, at="W0.mon@o+1:30", due="W0.fri@c-0:30",
        title=L("Listen to five of Caleb's calls this week", "Прослушать пять звонков Ведяшкина за неделю"),
        desc=L("Two from the morning block, three from the afternoon. Notes go into his next call review.",
               "Два утренних, три после обеда. Разобрать на ближайшем разборе звонков."),
        why=L(None, None),
        trail=[step("W0.tue@o+6:00", 4, "moved", to="started")],
    ),
    dict(
        id="G-weekly-callers", story="S01", kind="task", origin="human", site="main", priority="normal",
        state="unstarted", owner=4, owner0=4, by=4, at="W0.mon@o+1:32", due="W0.fri@c-0:30",
        title=L("Weekly read: callers who fell off the call-back list",
                "Сверка за неделю: кто из звонивших выпал из списка перезвонов"),
        desc=L("Call history for the week, all three shops: anyone who rang, got nobody and is older than "
               "the list shows.",
               "История звонков за неделю по трём площадкам: кто не дозвонился и в списке уже не виден."),
        why=L(None, None), trail=[],
    ),
    dict(
        id="G-standing-cover", story="S05", kind="task", origin="human", site="east", priority="normal",
        state="unstarted", owner=4, owner0=4, by=2, at="p16-2@o+3:00", due="W+2.mon@c-0:30",
        title=L("Bonny Oaks counter: a standing answer for when Angie is off",
                "Приёмка на Инженерном: постоянное решение на дни без Демидовой"),
        desc=L("Not this one week: every time. Who goes over, from which shift, and what East Main keeps. "
               "The shop sells about half of what it recommends on her days off and better than six in ten "
               "with her.",
               "Не про одну эту неделю, а на каждый раз: кто выходит, из какой смены и кто остаётся на "
               "Московском. Без неё на Инженерном соглашаются на пять рекомендаций из десяти, с ней — на семь."),
        why=L("Her days off cost us sold work every time.", "Каждый её выходной — это потерянные работы."),
        trail=[],
    ),
    # ------------------------------------------------------------------ the mention the junior has unread
    dict(
        id="M-chats-cover", story="board", kind="task", origin="human", site="main", priority="low",
        state="unstarted", owner=5, owner0=5, by=5, at="p5-1@c-0:30", due=None,
        title=L("Chats: who covers when Maya is at Bonny Oaks", "Чаты: кто отвечает, когда Алина на Инженерном"),
        desc=L(None, None), why=L(None, None),
        trail=[step("p5-1@c-0:28", 5, "comment", mentions=[6], body=L(
            "@Maya Torres, which day are you at Bonny Oaks next week? I'll take the chats that day.",
            "@Алина Рамилевна Хасанова, в какой день ты на следующей неделе на Инженерном? Чаты в этот день возьму на себя."))],
    ),
]

# The 24 open cards at T that are built from the text banks: owner, who gave it, where it comes from, priority,
# column, the deadline as a working-day offset of the owner from T (negative: overdue), and the age in days of its
# last timeline line (under 7, so none of them is quiet). With the 21 open hand-written cards above: 45.
BANK_OPEN_AT_T = [
    # owner, giver, source, priority, state, due_working_days, last_line_days
    (22, 2, "task", "urgent", "unstarted", 1, 2), (22, 22, "task", "normal", "started", 3, 1),
    (5, 4, "task", "urgent", "started", 1, 1), (5, 5, "handover", "high", "started", 0, 0),
    (5, "A:5", "assistant", "normal", "unstarted", 2, 0),
    (7, 5, "task", "normal", "unstarted", -2, 3), (7, 7, "handover", "high", "started", 0, 0),
    (7, 4, "task", "urgent", "unstarted", 1, 1),
    (29, 5, "task", "normal", "unstarted", 1, 2), (29, 29, "handover", "high", "started", 0, 0),
    (16, 4, "task", "urgent", "started", 1, 1), (16, 16, "handover", "high", "started", 0, 0),
    (16, "A:16", "assistant", "normal", "unstarted", 4, 2),
    (17, 16, "task", "normal", "unstarted", -1, 2), (17, 17, "handover", "high", "started", 0, 1),
    (17, 4, "task", "low", "backlog", 5, 5),
    (23, 22, "task", "urgent", "unstarted", -3, 4), (23, 22, "task", "normal", "unstarted", -6, 6),
    (23, 23, "handover", "high", "started", 0, 1), (23, 2, "task", "normal", "unstarted", 2, 3),
    (24, 22, "task", "urgent", "started", 1, 0), (24, 24, "handover", "high", "started", 0, 0),
    (3, 2, "task", "normal", "started", 3, 2),
    (9, 4, "task", "normal", "started", 1, 1),
]
