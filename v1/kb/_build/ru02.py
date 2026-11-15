# -*- coding: utf-8 -*-
from kbr import *

page('customers/estimates-and-approvals.md', 'Смета и согласование работ',
 f"""*Действует с {D('T-26mo')} · Проверено: {D('T-5mo')}*

1. **Сначала смотрим.** Цена ремонта появляется после осмотра или диагностики, а не до них.
2. **Смета — письменно.** В ней каждая работа стоит отдельной строкой: работа, запчасти — и фотографии или замеры, на которых она основана.
3. **Вы согласуете каждую работу отдельно.** Можно согласиться на тормоза и отказаться от амортизаторов. Согласие принимаем сообщением в чате или мессенджере, подписью на приёмке или по телефону — тогда записываем, кто, когда и на что согласился, и просим подтвердить сообщением.
4. **Сверх согласованного не делаем.** Если по ходу ремонта выясняется, что нужно больше, останавливаемся и звоним. Нет согласия — нет дополнительных работ, и платить за них вы не обязаны.
5. **Отложенное не теряется.** Работы, от которых вы пока отказались, остаются в истории машины, и мы о них напомним. Без нажима.

Смета действует 14 дней. Дальше цены на запчасти могли измениться, и мы её пересчитываем.

Стоимость осмотра и диагностики есть на странице [цен](prices-for-common-services.md); она оплачивается независимо от того, будете вы делать ремонт или нет.
""",
 diff=['Approval is by a message (chat or messenger), a signature at the desk, or by phone with a note of who, when and what, followed by a message.',
       'An estimate is valid 14 days, not 30: parts prices move faster (ledger price.parts_drift_year 12 % a year).'],
 new=['Estimate validity 14 days.',
      'A phone approval is written on the order and the customer is asked to confirm it by a message.'],
 verify=['"You are not obliged to pay for work you did not agree to" and the written form of consent to extra paid work: the research has them only as unverified snippets of consumer-law pages (ru-shop.md, second pass, gap 9). Under ПП № 780 an estimate confirmed by the consumer becomes part of the contract (п. 18, read).'])

page('customers/warranty.md', 'Наша гарантия',
 f"""*Действует с {D('@warranty_2424')} · Проверено: {D('T-4mo')}*

**30 дней на слесарные и электротехнические работы.** Срок считается со дня, когда вы подписали акт выполненных работ и забрали машину. Пробегом гарантия не ограничена и действует во всех трёх сервисах «Ермак-Сервиса».

Если то, что мы отремонтировали, в этот срок снова вышло из строя, привезите машину и заказ-наряд в любой наш сервис. Переделаем работу или заменим деталь бесплатно.

## Где условия другие

- **Запчасти, купленные у нас:** гарантия производителя, её срок указан в заказ-наряде. Если деталь отказала позже 30 дней, но в срок производителя, меняем её по гарантии, а работа по замене оплачивается.
- **Колодки, щётки, лампы, свечи, фильтры:** гарантия только на заводской брак. Износ от езды — не брак.
- **Аккумуляторы и шины:** гарантия производителя по талону. Обращение оформляем мы.
- **Работы подрядчиков** (капитальный ремонт АКПП, ремонт рулевой рейки, стёкла): гарантия подрядчика. Передаём её вам письменно вместе с работой.
- **Ваши запчасти:** гарантия только на нашу работу, на саму деталь её нет. Подробнее: [Ремонт со своими запчастями](bringing-your-own-parts.md).
- **Диагностика и осмотр:** гарантийного срока нет, это заключение, а не ремонт.

## На что гарантия не распространяется

ДТП; перегрев или езда без масла после ремонта; гонки и бездорожье; вмешательство другого сервиса в тот же узел. Эвакуатор и такси не оплачиваем.

Гарантию мы установили сами. Ваших прав по Закону о защите прав потребителей она не ограничивает.
""",
 diff=['Terms follow ledger s12.warranty.ru: 30 days on mechanical and electrical work; no mileage limit; from the day the completion act is signed.',
       'No business-use tier, no 25-mile rule, no cap: the Russian page has none of them.',
       'Parts carry the maker\'s warranty; after day 30 the part is replaced under it and the labour is paid, which is why a repeat after day 30 is a paid order (ledger comeback.definition).',
       'Customer parts: warranty on the work only (English: none on part or labour).'],
 new=['Wear parts (pads, blades, bulbs, plugs, filters): factory defects only.',
      'After day 30 and inside the maker\'s term: the part is replaced, the labour is charged.',
      'Diagnosis and inspection carry no warranty term.',
      'Sublet work (gearbox rebuild, steering rack, glass): the subcontractor\'s warranty in writing; its length is stated nowhere in the base, as in English.'],
 verify=['"Body work" here: the catalogue has no body job and the public scope page says body repair and paint are not done; an earlier ledger row gave 6 months on body work.',
         'The sentence that the shop\'s own warranty does not limit the consumer\'s rights under the consumer-protection law is ordinary wording; the periods the law itself gives for claims on work are not in the research and are not stated.'])

page('customers/dropping-off-and-picking-up.md', 'Как сдать и забрать автомобиль',
 f"""## Приёмка

- **По записи.** Приезжайте к своему времени. Мастер-приёмщик обойдёт машину вместе с вами, запишет пробег, уровень топлива и то, что видно на кузове, а жалобу — вашими словами. Вы подписываете заказ-наряд и акт приёма-передачи, один экземпляр остаётся у вас.
- **С собой:** свидетельство о регистрации, ключ, «секретку» от колёс, сервисную книжку, если она есть.
- **Вечером накануне.** Можно поставить машину до 20:00, оформим её сразу. Ночью машины стоят на закрытой территории.

Ящика для ключей у нас нет: машину принимает человек и при вас.

## Ожидание

Замену масла, шиномонтаж, ремонт прокола и диагностику — всё, что занимает до часа, — можно подождать у нас. Есть кофе и Wi-Fi. Если работа дольше, машину лучше оставить.

## Как уехать без машины

Развозки у нас нет. Скажите мастеру-приёмщику — вызовет вам такси, поездку вы оплачиваете сами. До остановки от каждого сервиса несколько минут пешком.

## Выдача

Когда машина готова, звоним или пишем и называем итоговую сумму. Мастер-приёмщик проходит с вами по заказ-наряду строка за строкой и отдаёт старые детали, если вы просили их сохранить. Вы подписываете акт выполненных работ, оплачиваете и получаете чек.

**После 20:00** машину не выдаём. Если не успеваете, заберите утром: первые пять дней стоянка бесплатная.

За вас машину может забрать другой человек, если вы заранее назвали мастеру-приёмщику его имя.
""",
 diff=['No key drop box, no shuttle, no lock box: the car is taken and handed back by a person against signed documents (ПП № 780: the car is released against the act).',
       'Shops are open until 20:00 every day, so after-hours pick-up is "come in the morning".',
       'Loaner cars (подменный автомобиль) are mentioned on no page: the planted gap is kept.'],
 new=['A car can be left the evening before until 20:00 and is checked in at once; cars stand overnight on a closed lot.',
      'No shuttle: the advisor calls a taxi at the customer\'s cost.',
      'Another person may collect the car if the customer named them to the advisor beforehand.',
      'What to bring: registration certificate, key, wheel-lock key, service book.',
      'Five free days of parking after the car is ready (the storage policy).'])

page('customers/payment.md', 'Оплата',
 f"""- **Когда.** Оплата — при получении автомобиля.
- **Как.** Банковской картой, наличными или по QR-коду через СБП. Организации платят по счёту, безналичным переводом.
- **Чек.** Кассовый чек выдаём на бумаге либо присылаем на телефон или электронную почту — как вам удобнее.
- **Предоплата.** Просим её в двух случаях: если запчасть везём под заказ и она стоит дороже {N(10000,'порог предоплаты за запчасти под заказ')}, и перед тем, как отправить коробку передач на капитальный ремонт. Предоплата засчитывается в итоговую сумму, чек на неё выдаём сразу.
- **НДС.** Цены в прайс-листе указаны с НДС 5 %, сверху он не добавляется. В заказ-наряде, акте и чеке стоит итог и строка «в том числе НДС 5 %».
- **Организации с договором** получают счёт и акт или УПД по каждому заказ-наряду; сумма без НДС, НДС и итог указаны в них отдельно. См. [Автомобили организаций](company-vehicles.md).

Скидки за наличные нет. Цена одна при любом способе оплаты.

Вопросы по счёту или чеку — в сервис или в бухгалтерию: {TEL['main']}, добавочный 111, {S(3)}.
""",
 diff=['Methods follow ledger pay.mix.ru: card, СБП by QR code, cash; bank transfer on an invoice for companies. No cheques.',
       'VAT 5 % is inside every price; the order, the act and the receipt show the total and «в том числе НДС 5 %» (ledger kb.vat_in_list_prices).',
       'Companies under a contract get an invoice and an act or УПД per order, with the amount before VAT, the VAT and the total as separate figures (ledger kb.documents).'],
 new=['Prepayment threshold for special-order parts: 10 000 RUB.',
      'The cash receipt is given on paper or sent to a phone or e-mail.'])

page('customers/towing.md', 'Эвакуатор',
 f"""## Ульяновск (Московское шоссе и Инженерный)

Машина не едет — звоните нам, отправим эвакуатор, с которым работаем. Водителю платить не нужно: эвакуация войдёт в заказ-наряд.

- Подача и первые 10 км до любого из наших ульяновских сервисов: {N(3000,'эвакуация: подача и первые 10 км')}
- Каждый следующий километр: {N(70,'эвакуация: километр сверх десяти')}

Если мы уже закрыты, водитель оставит машину на нашей стоянке. Утром позвоните нам или приезжайте с ключом.

## Казань (Техническая)

Позвоните в сервис: {TEL['west']}. Подскажем телефон эвакуатора, который ближе к вам.
""",
 diff=['Partner V8 «Автоспас 73» serves the two Ulyanovsk shops and is not named to customers; the price is by kilometre.',
       'Kazan: no partner and no price anywhere in the base (planted gap kept).'],
 new=['Tow price: 3 000 RUB with the first 10 km, 70 RUB for each further km. The ERP needs matching sublet lines for towed cars.'])

page('customers/bringing-your-own-parts.md', 'Ремонт со своими запчастями',
 f"""Можно. Давайте по порядку.

- Ваши запчасти ставим по обычному нормо-часу, без наценки.
- Всё, что вы привезли, записываем в заказ-наряд: что за деталь, чьего производства, сколько стоит с ваших слов. Так положено, и потом не будет спора, чья была деталь.
- Гарантия — **только на нашу работу**: 30 дней на то, что поставлено правильно. На саму деталь гарантии нет. Не подошла, оказалась с браком, отказала через месяц — снять её и поставить другую стоит как новая работа.
- Не ставим привезённые **тормозные шланги, суппорты и главные тормозные цилиндры**, **подушки и ремни безопасности**, **шины старше шести лет** и любые детали тормозов и рулевого с разборки. Это либо наше, либо никак.
- Если в коробке явно не та деталь или явная подделка, механик скажет об этом сразу и ставить не будет.

Почему так. Когда запчасть наша, мы знаем, у кого её взяли, и отвечаем за весь ремонт: и за работу, и за деталь — см. [гарантию](warranty.md). За то, что выбирали не мы, отвечать не можем. Так дела не делаются.

*{S(1,'full')}*
""",
 diff=['Warranty on the work only, 30 days, never on the part (research: the Russian habit; ledger note).',
       'Customer parts are written into the order with name, maker and the price the customer states (ПП № 780, п. 9 and 12, read in the research).',
       'No surcharge on the hour for customer parts: a surcharge would need a catalogue row.'],
 new=['Refused: brake hoses, calipers and master cylinders, airbags and seat belts, tyres older than six years, any used brake or steering part.'],
 verify=['ПП № 780 п. 14-15 (the contractor warns about unfit customer parts and stops work) is read in the research; the page words it as "the mechanic will say so and will not fit it".'])

page('customers/if-something-is-not-right.md', 'Если что-то не так',
 f"""Скажите нам. Лучше мы услышим это от вас, чем прочитаем в отзывах.

1. Позвоните в сервис, где делали машину, и попросите руководителя: {S(4,'full')} — Московское шоссе и Инженерный, {S(22,'full')} — Техническая. Или скажите любому мастеру-приёмщику, он его позовёт.
2. Вам ответят в течение одного рабочего дня — человек, который может решить вопрос.
3. Если машину нужно показать, смотрим её первой, вне очереди. За осмотр вы не платите.

Письменную претензию можно оставить на приёмке или прислать на почту сервиса. Отвечаем на неё письменно, в течение десяти дней.

Если ответ вас не устроил, напишите директору: {S(2,'full')}, eermolaeva@ermak-service.example.
""",
 diff=['A written claim (претензия) is a route of its own in Russia; the page promises a written answer within ten days.',
       'Slot 2 is «директор»; her address follows phones.md.'],
 new=['A written claim is answered in writing within ten days.'],
 verify=['The ten-day term for answering a consumer\'s written claim about work (consumer-protection law, article 31) is not in the research.'])

# ---------------------------------------------------------------- цех (worker rank)
page('shop-floor/README.md', 'Цех',
 f"""Для механиков. Коротко, чтобы читали.

- [Отметки прихода и ухода](clocking-in-and-out.md)
- [Замены смен и отгулы](shift-changes-and-time-off.md)
- [Осмотр по чек-листу](courtesy-inspection.md)
- [Перед тем как отдать машину](before-a-car-leaves.md)
- [Если машина вернулась](when-a-car-comes-back.md)
- [Техника безопасности](safety.md)

Правила внутреннего распорядка лежат в папке в комнате отдыха. По зарплате и отпускам — к {P(3,'Ирине Владимировне')} в бухгалтерию.

*{S(8)}, мастер цеха*
""",
 diff=['The handbook is «Правила внутреннего трудового распорядка», a paper folder in the rest room.'])

page('shop-floor/clocking-in-and-out.md', 'Отметки прихода и ухода',
 f"""*{S(4)} · Проверено: {D('T-2mo')}*

- Приход отмечайте с телефона, **когда вы уже в сервисе**, а не по дороге. Приложение видит, где вы находитесь. Отметка дальше {LV('geo.checkin_radius_m')} метров от сервиса помечается и приходит мне.
- Смена начинается во время, которое стоит в графике. Через {LV('late.grace_min')} минут после него это опоздание, и в отметке оно видно.
- Уходите — отметьте уход. Забыли — утром на Главной появится вопрос: поставьте время, когда на самом деле ушли, и отправьте. Согласую в тот же день.
- Не просите отметить вас и не отмечайте других.
- Отметка — это явка. Время по заказ-наряду ведётся отдельно, в программе сервиса: взяли работу — запустили, закончили — остановили. По каждой работе, как всегда.

Приложение не пускает — скажите мастеру цеха или руководителю СТО до начала смены, а не после.
""",
 diff=['The check-in radius is given in metres (ledger geo.checkin_radius_m).',
       'Job time in the shop system matters more in Russian: clocked job time against sold hours is one of the three signatures of story S2.'],
 msgs=['Отмечаемся в сервисе, а не с дороги.'])

page('shop-floor/shift-changes-and-time-off.md', 'Замены смен и отгулы',
 f"""*{S(4)}*

- Механики работают пять дней через два, с 9:00 до 18:00; выходные у всех в разные дни, чтобы в сервисе всю неделю хватало людей. Мастера-приёмщики — два через два, с 9:00 до 20:00.
- Просьбу оставляйте в приложении, на той смене, которую хотите поменять. Не сообщением и не через кого-то.
- **Пишите причину.** Просьбу без причины не рассматриваю.
- Просите не позже чем за 7 дней. Позже — постараюсь, но ответ обычно «нет», если вы не привели человека, который выйдет вместо вас.
- Обмена сменами в приложении нет. Просите перенести смену на другой день и напишите, кто выйдет вместо вас. «Он обещал» — не подтверждение: спрошу его сам.
- График на неделю публикую до полудня четверга предыдущей недели. Опубликованный график — это график.
- Заболели — позвоните на приёмку до 8:30. Сообщение товарищу — не предупреждение. Номер больничного листка сообщите {P(3,'Ирине Владимировне')}.
- В сезон шиномонтажа, в апреле — мае и октябре — ноябре, отгулы на шиномонтаже не согласую.

На Технической график составляет и на просьбы отвечает {P(22,'Ринат Фаридович')}.
""",
 diff=['Patterns: mechanics five days on, two off, 9:00-18:00, days off staggered; advisors two on, two off, 9:00-20:00 (ledger roster.*).',
       'Sick: call the desk before 8:30 and give the number of the sick-leave certificate to the bookkeeper.',
       'The product has no swap (stories/S14: change of time, change of date, removal): the page asks for a move to another day and the name of who comes in.'],
 new=['Sick call before 8:30 (half an hour before opening).',
      'No days off on the tyre bays in the two tyre seasons (ledger season.extra_shifts: slot 15 and the seasonal fitter work six days a week then).'])

page('shop-floor/courtesy-inspection.md', 'Осмотр по чек-листу',
 f"""Каждую машину, которая заехала на любую работу, осматриваем по чек-листу, если мастер-приёмщик не написал в наряде «без осмотра». Десять минут. Так клиент узнаёт, что нужно машине, а мы — какая работа будет следующей.

## Что смотреть

Шины: остаток протектора в миллиметрах на всех четырёх и год выпуска. Колодки — через диск или на снятом колесе, если оно всё равно снято. Свет, щётки, аккумулятор, ремни и патрубки, уровни и состояние жидкостей, течи снизу, амортизаторы, пыльники ШРУСов, выхлоп.

## Как отмечать

- **Норма:** делать нечего.
- **Наблюдать:** изношено, но ездить можно. Пиши замер: «колодки перед 4 мм», а не «колодки подходят».
- **Менять:** нужно делать сейчас. Замер **и фото**. Нет фото — приёмка это не продаст, а я отправлю тебя фотографировать.

К каждой строке «Наблюдать» и «Менять» выбери работу из справочника. Руками работу не вбивай, если она есть в списке.

## Дальше

Закрой осмотр в программе. Он уходит мастеру-приёмщику, тот считает смету: [Как составить смету](../how-to/writing-an-estimate.md). Цену клиенту не называй. Ничего не начинай, пока работы нет в наряде. Нет строки в наряде — нет работы, без исключений.

*{S(8)}, мастер цеха*
""",
 diff=['The inspection is «осмотр по чек-листу», free with any repair; states are «Норма», «Наблюдать», «Менять» (ERP good, watch, bad). Tread depth in millimetres.',
       'The last line is harder than in English: work with no order line is one of the three signatures of the Russian story S2.'],
 new=['State names «Норма», «Наблюдать», «Менять».'])

page('shop-floor/before-a-car-leaves.md', 'Перед тем как отдать машину',
 f"""Каждая машина, каждый раз. На контрольную поездку выезжаю сам, когда успеваю. Успеваю не всегда.

1. Колёса снимал? **Затяни динамометрическим ключом**, руками, по моменту. Не гайковёртом.
2. Тормоза делал? Прокачай педаль до того, как тронешь машину с места. Направляющие почисти и смажь. Уровень жидкости проверь.
3. Пробки на месте: масло, антифриз, тормозная, омыватель. Щуп вставлен.
4. Под капотом ничего не осталось. Инструмент пересчитай.
5. Заведи, загляни под машину: не капает?
6. Проедь хотя бы вокруг сервиса. Тормоза, рулевое, подвеска и всё, что стучало, — настоящая контрольная поездка.
7. Сбрось межсервисный интервал. Давление в шинах выставь по табличке в проёме двери.
8. Старые детали — в пакет и в багажник, если в наряде отмечено, что клиент их забирает.
9. Протри руль, рычаг и ручку двери. Чехол с сиденья и накидку с крыла сними.
10. Останови время по наряду. Запиши в наряд, что сделал и что увидел.

Вернётся машина по пункту из этого списка — разговор будет со мной.

*{S(8)}, мастер цеха*
""",
 diff=['Same ten checks in the foreman\'s Russian voice («ты» to mechanics).'])

page('shop-floor/when-a-car-comes-back.md', 'Если машина вернулась',
 f"""Возврат — это машина, которая приехала с тем же, за что нам уже заплатили. Гарантия на работу — 30 дней.

- Возврат идёт вне очереди. Человек уже один раз заплатил.
- Приёмка открывает новый заказ-наряд, гарантийный, с привязкой к первому. По старому наряду не работаем.
- **Первым смотрит мастер цеха** — вместе с тем, кто делал, если он в смене. На Инженерном это {P(18,'Валерий Геннадьевич')}, на Технической — {P(22,'Ринат Фаридович')}.
- Пиши, что нашёл, прямо. «Направляющие сухие, колодку закусило» — полезно. «Со слов клиента шум» — нет.
- С клиентом никто не спорит, кто виноват. Ни у машины, ни на приёмке.
- Приехал позже 30 дней с той же жалобой — наряд обычный, платный. Смотрю всё равно я, а что с этим делать, решает {P(4,'Сергей Анатольевич')}.

Возвраты считаем по каждому механику, раз в месяц. Они есть у всех. Цифра нужна, чтобы работать лучше. Свою покажу, если спросишь.

*{S(8)}, мастер цеха*
""",
 diff=['The comeback window is the 30-day warranty (ledger comeback.definition); a repeat after day 30 is an ordinary paid order.',
       'The trade word is «возврат».'],
 new=['After day 30 with the same complaint: a paid order, the foreman still looks first, the service manager decides.'])

page('shop-floor/safety.md', 'Техника безопасности',
 f"""- Очки в цехе. Всегда.
- Подъёмник: лапы под штатные точки, на высоте колена качни машину, только потом поднимай. Под машину — когда подъёмник встал на стопоры.
- Под машину на одном домкрате не лезть. Страховочные стойки.
- **Оранжевые провода — высокое напряжение.** Гибриды делает {S(10,'f')}, на Московском шоссе, и больше никто. Стоит у тебя гибрид на тормоза или шиномонтаж — делаешь тормоза или шиномонтаж, оранжевое не трогаешь.
- Фреон откачиваем станцией, в воздух не стравливаем. Кондиционеры делают те, кто обучен работать со станцией. Кто это в твоём сервисе, спроси у мастера цеха.
- Кислота из аккумулятора, очиститель тормозов возле огня, ремень на заведённом моторе: сам знаешь. Вот и веди себя так, будто знаешь.
- Пролил — убери сразу. Кто ближе, тот и убирает.
- Травма, любая, — в тот же день скажи мастеру цеха. Запишем.
- Инструктаж по охране труда — под подпись в журнале. Не расписался — к работе не допущен. Повторный — раз в полгода. У кого это первая работа и кто стоит на опасных работах — первый год раз в три месяца.

*{S(8)}, мастер цеха*
""",
 diff=['There is no refrigerant certificate in the Russian trade: A/C work goes to "those trained on the station"; the page still names nobody (planted gap kept).',
       'The safety-briefing journal is signed; the repeated briefing is every six months, and every three months in the first year for a first-time worker on hazardous work (ledger kb.handbook safety_briefing; ПП № 2464 п. 14).'],
 new=['A mechanic who has not signed the safety-briefing journal is not admitted to work.'],
 verify=['How often the repeated safety briefing is due is not in the research; the page gives no interval.'])
