# -*- coding: utf-8 -*-
from kbr import *
import kbb

# ------------------------------------------------------------------ цены
CATS = [(c['key'], c['ru']) for c in kbb.cat['categories']]
rows_fact = []
def table(ck):
    out = ['| Работа | Н/ч | Работа, ₽ | Эконом | Стандарт | Премиум | Запчасти в стандартной смете |', '|---|---:|---:|---:|---:|---:|---|']
    for k, e in JOBS.items():
        if CATEGORY[k] != ck: continue
        eco, std, pre = (num_total(k, x) for x in ('economy', 'standard', 'premium'))
        labv = e['labour_price'][MODE]
        if MODE == 'before_rise':
            eco, std, pre = (num_total(k, x, 'before_rise') for x in ('economy', 'standard', 'premium'))
        rows_fact.append({'catalogue_key': k, 'name': e['name'], 'hours': e['hours'], 'labour': labv, 'labour_pricing': e['labour_pricing'], 'economy': eco, 'standard': std, 'premium': pre})
        name = e['name']
        sp = []
        for p in e['parts']:
            o = {x['tier']: x for x in p['options'] if not x.get('story')}
            op = o.get('standard') or list(o.values())[0]
            q = ('%g' % p['qty']).replace('.', ',') + ' ' + p['unit']
            sp.append(p['name'][0].lower() + p['name'][1:] + ' ' + op['brand'] + ', ' + q)
        if e['sublet']: sp.append('ремонт агрегата у подрядчика')
        if e['fees']: sp.append(e['fees'][0]['name'][0].lower() + e['fees'][0]['name'][1:])
        sp = '; '.join(sp) if sp else 'только работа'
        if e['labour_pricing'] == 'menu': name += ' (фикс.)'
        h = ('%g' % e['hours']).replace('.', ',')
        if eco == std == pre:
            out.append(f"| {name} | {h} | {M(labv)} | | {M(std)} | | {sp} |")
        else:
            out.append(f"| {name} | {h} | {M(labv)} | {M(eco)} | {M(std)} | {M(pre)} | {sp} |")
    return '\n'.join(out)

body = f"""*Отвечает: {S(2,'full')} · Действует с {D('@price_rise')} · Цену называем только с этой страницы.*

Все суммы — с НДС, для **легкового автомобиля**. Сверху НДС не добавляется: в заказ-наряде, акте и чеке стоит итог и строка «в том числе НДС 5 %». Для кроссовера, рамного внедорожника или фургона смотрите коэффициенты на странице [Нормо-час, сборы и классы автомобилей](labour-rates-and-fees.md) или распечатанный [прайс для стойки](counter-price-sheet.pdf).

Как читать строку. *Работа, ₽* — только работа. *Стандарт* — вся работа с запчастями, которые мы считаем в смету по умолчанию. *Эконом* и *Премиум* — то же с запчастями дешевле или лучше, там, где есть выбор. Пометка *(фикс.)* — цена фиксированная: за нормо-часом она не идёт, расходные материалы на неё не начисляются. На все остальные работы начисляются расходные материалы: 3 % от стоимости работы, но не больше {M(SUP_CAP)} на заказ-наряд. Клиенту называем итог вместе с ними.

Нормо-час: **{rate()}.**
"""
for ck, cn in CATS:
    body += f"\n## {cn}\n\n{table(ck)}\n"
    if ck == 'tyres_alignment':
        body += f"\nВ шиномонтаж новых шин входит утилизация старых, {fee('new_tyres_fitted')} за комплект. Хранение — за сезон, до семи месяцев, за комплект из четырёх шин, на дисках или без.\n"
    if ck == 'suspension_steering':
        body += f"\nРулевую рейку перебирает подрядчик: {sublet('steering_rack')} из итога — его работа. Наша работа — снять и поставить рейку.\n"
    if ck == 'transmission_driveline':
        body += f"\nКапитальный ремонт АКПП делает {V('V6')}, оплата идёт через нас: {sublet('transmission_rebuild')} из итога — их работа. Наша работа — снять и поставить коробку.\n"
    if ck == 'brakes':
        body += "\nКолодки и диски считаются на ось. Суппорт — за одну сторону.\n"
    if ck == 'air_conditioning':
        body += "\nХладагент считается по весу: в стандартной заправке 500 граммов. Если в систему входит больше, считаем по факту.\n"
body += f"""
## Чего нет в прайсе

Если работы здесь нет, цены на неё пока нет. Чаще всего спрашивают про то, что мы до сих пор не расценили: привязку ключей и брелоков, снятие «секреток» при потерянном ключе, полировку фар, установку фаркопа с проводкой, сварочные работы и любой дизель дальше жидкостей и фильтров. Не называйте цену на глаз и не берите её с похожей работы. Спросите старшего мастера-приёмщика: он посчитает по нормам времени и нормо-часу и скажет мне, чтобы я добавила строку.
"""
USED['prices'] = [{'rule': 'one row per catalogue job, vehicle class car, after the rise, all three tiers; generated from catalogue.json (ru)', 'rows': rows_fact}] + USED['prices']
page('prices/price-list.md', 'Прайс-лист', body,
 diff=['Generated from the Russian catalogue: 70 jobs, columns Работа, Н/ч, Работа ₽, Эконом, Стандарт, Премиум, parts of the standard quote. Fixed-price rows are marked (фикс.).',
       'Timing belt («Замена ремня ГРМ с роликами и помпой») standard total 16 000: the figure the stale page gets wrong (15 552).',
       'Shop supplies 3 % up to 500 RUB; every figure includes VAT at 5 % and nothing is added on top (ledger kb.vat_in_list_prices); refrigerant by weight; the steering rack and the gearbox rebuild are sublet.',
       'Unpriced jobs named: key and remote pairing, wheel-lock removal, headlight polishing, tow bar with wiring, welding, diesel work beyond fluids and filters.'],
 new=['The list of unpriced jobs for the Russian market (welding and tow bars instead of trailer wiring).'],
 msgs=['Новые цены с сегодняшнего дня. Нормо-час 1 900.', 'После истории с ремнём ГРМ.'])

# labour rates ----------------------------------------------------------------------------------------------
H = LV('price.hour.history'); HC = LV('price.hour.company_history')
PM = CFG['parts_class_multiplier']
def x(v): return '× ' + ('%g' % v).replace('.', ',')
def own(key):
    hb = JOBS[key]['hours_by_class']
    return ' | '.join('не делаем' if hb[c] is None else x(hb[c]) for c in ('suv', 'truck', 'van'))
page('prices/labour-rates-and-fees.md', 'Нормо-час, сборы и классы автомобилей',
 f"""*Отвечает: {S(2,'full')} · Действует с {D('@price_rise')}*

## Нормо-час

| Ставка | За нормо-час | Кто платит |
|---|---:|---|
| Нормо-час по прайсу | {rate()} | Все, кроме тех, кто в следующей строке |
| Договорной нормо-час | {rate('company_account')} | Только {A('A1')} и {A('A2')} |

Как менялся нормо-час:

| С какого дня | По прайсу | Договорной |
|---|---:|---:|
| до {D('@price_rise_1')} | {M(H[0][1])} | {M(HC[0])} |
| с {D('@price_rise_1')} | {M(H[1][1])} | {M(HC[1])} |
| с {D('@price_rise_2')} | {M(H[2][1])} | {M(HC[2])} |
| с {D('@price_rise')} | {M(H[3][1])} | {M(HC[3])} |

До {D('@price_rise')} нормо-час был {rate('standard','before_rise')}. Фиксированные цены в тот же день выросли на те же {str(LV('price.rise.last_pct')).replace('.', ',')} %. Цены на запчасти с нормо-часом не связаны: они идут за закупкой.

## Что добавляется к сумме

| Что | Сколько | На что |
|---|---|---|
| Расходные материалы | 3 % от работы, не больше {M(SUP_CAP)} на заказ-наряд | Только работы по нормо-часу. На фиксированные цены не начисляются |
| Утилизация шин | {fee('new_tyres_fitted')} за комплект | Новые шины |

НДС к сумме не добавляется: все цены указаны с НДС 5 %. В заказ-наряде, акте и чеке стоит итог и строка «в том числе НДС 5 %»; организациям в счёте и УПД показываем сумму без НДС, НДС и итог отдельно. НДС мы платим с 1 января 2025 года, на упрощённой системе. В документах за более ранние даты НДС нет.

## Машины крупнее легковой

Прайс-лист посчитан на легковой автомобиль. Для остальных умножайте:

| Класс | Примеры | Работа на тяжёлых узлах | Запчасти |
|---|---|---:|---:|
| Легковой | Granta, Solaris, Logan, Camry | {x(1)} | {x(PM['car'])} |
| Кроссовер | Duster, Creta, RAV4, Niva, Jolion | {x(1.15)} | {x(PM['suv'])} |
| Рамный внедорожник, пикап | УАЗ Patriot, Land Cruiser Prado, Pajero, Hover | {x(1.3)} | {x(PM['truck'])} |
| Лёгкий коммерческий | ГАЗель, Соболь, Largus-фургон, Ducato, Transit | {x(1.3)} | {x(PM['van'])} |

«Тяжёлые узлы» — это тормоза, стойки и амортизаторы, рычаги, шаровые, ступичные подшипники, рулевая рейка, компрессор и радиатор кондиционера, генератор, стартер, помпа, термостат, радиатор, опоры двигателя, топливный насос, сцепление, ШРУСы, снятие коробки, а также сход-развал и замена колёс в сборе. Диагностика и осмотры стоят одинаково для любого класса. На жидкостях и фильтрах работа та же, а масло, жидкости и фильтры считаются с коэффициентом на запчасти.

У трёх работ свой коэффициент:

| Работа | Кроссовер | Рамный внедорожник | Фургон |
|---|---:|---:|---:|
| Свечи зажигания (на V6 и на рамных дольше) | {own('spark_plugs')} |
| Ремень ГРМ | {own('timing_belt_kit')} |
| Прокладка клапанной крышки | {own('valve_cover_gasket')} |
| Шиномонтаж, сезонный и новых шин | {own('seasonal_tyre_change')} |

Пример: передние диски и колодки на УАЗ Patriot. Работа {lab('front_pads_rotors')} × 1,3 = {lab('front_pads_rotors', cls='truck')}. Запчасти в стандарте {parts_total('front_pads_rotors')} {x(PM['truck'])} = {M(nt('front_pads_rotors', cls='truck') - nlab('front_pads_rotors', cls='truck'))}. Итого {t('front_pads_rotors', cls='truck')} без расходных материалов.
""",
 diff=['Rates 1 900 (list) and 1 700 (contract, accounts A1 and A2) from the rise; 1 760 and 1 580 before.',
       'The page carries the whole history of the hour: three rises in two years (ledger price.hour.history, price.hour.company_history).',
       'Shop supplies 3 % up to 500 RUB; VAT 5 % from 1 January 2025 (ledger tax.ru_vat_from), inside every price and not among the things added to the bill (ledger tax.ru_price_basis); one tyre fee (disposal, 400 RUB a set); no state fee.',
       'Class multipliers of the Russian catalogue: hours 1 / 1.15 / 1.3 / 1.3, parts 1 / 1.35 / 1.7 / 1.3; fluid and filter jobs keep the car\'s labour and scale their parts (catalogue parts_scale_with_class), diagnosis and inspections are flat; own multipliers for plugs, timing belt, valve-cover gasket and tyre fitting.',
       'The planted slip is kept in its Russian form: "three jobs have their own multiplier" above a table of four rows.',
       'Worked example: front discs and pads on a УАЗ Patriot (class truck).'],
 new=['Two events of the Russian timeline: @price_rise_1 (the first open day on or after T-18 months, 1 500 to 1 620) and @price_rise_2 (the first open day on or after T-11 months, 1 620 to 1 760). The grammar is unchanged; the events are named in OUTLINE-ru.md.',
      '1 January 2025 is written as a calendar date: it is a fact of law, not a story date.'],
 msgs=['Новые цены с сегодняшнего дня. Нормо-час 1 900.'])

def pct(a, b): return ('%g' % round((b / a - 1) * 100, 1)).replace('.', ',')
page('prices/how-prices-change.md', 'Как меняются цены',
 f"""*{S(2,'full')} · {D('@belt_proposal')}*

Нормо-час и фиксированные цены устанавливаю я. Цены на запчасти считает {S(9,'fi')}: от закупки, по матрице наценок. Больше цены не меняет никто.

Когда меняется цена:

1. [Прайс-лист](price-list.md) и страница [про нормо-час](labour-rates-and-fees.md) меняются в то же утро, до открытия.
2. Страница [цен для клиентов](../customers/prices-for-common-services.md) — в то же утро.
3. Каждую страницу услуг, на которой есть сумма в рублях, в течение пяти рабочих дней проверяет тот, кто её ведёт. {S(5,'fi')} ведёт страницы услуг Московского шоссе, {S(16,'fi')} — тормоза и подвеску.
4. Смета, которую клиент уже получил, действует по своей цене свои 14 дней.

Шаг 3 мы и пропустили. После повышения {D('@price_rise')} на странице про ремень ГРМ остался старый нормо-час, мастер-приёмщик назвал цену с неё, и нам это стоило скидки и недовольного клиента. Найдёте ещё одну такую страницу — не обходите её молча, предложите правку в тот же день. Правка страницы про ремень ГРМ предложена, решение за {P(4,'Сергеем Анатольевичем')}.

## Что и когда менялось

| Дата | Что изменилось |
|---|---|
| {D('@price_rise_1')} | Нормо-час {M(H[0][1])} → {M(H[1][1])}. Договорной {M(HC[0])} → {M(HC[1])}. Фиксированные цены +{pct(H[0][1], H[1][1])} % |
| {D('@price_rise_2')} | Нормо-час {M(H[1][1])} → {M(H[2][1])}. Договорной {M(HC[1])} → {M(HC[2])}. Фиксированные цены +{pct(H[1][1], H[2][1])} % |
| {D('@price_rise')} | Нормо-час {M(H[2][1])} → {M(H[3][1])}. Договорной {M(HC[2])} → {M(HC[3])}. Фиксированные цены +{str(LV('price.rise.last_pct')).replace('.', ',')} %. Запчасти не менялись |

Три повышения за два года — это много, и каждый раз мы обещали себе обновить все страницы. Теперь это записано.
""",
 diff=['The record has three rows: the Russian shop raised the hour three times in two years (design R11, ledger price.hour.history).',
       'An open estimate is honoured for its 14 days.'],
 new=['Fixed prices rose by the same percentage as the hour at the two earlier rises (8 % and 8.6 %); the catalogue holds only the last step.'])

# ------------------------------------------------------------------ правила
page('policies/README.md', 'Правила',
 f"""То, что мы решили, записано здесь, чтобы во всех трёх сервисах было одинаково. Если правило расходится с привычкой, действует правило. Если правило неправильное — скажите мне.

| Страница | Одной строкой |
|---|---|
| [Скидки](discounts.md) | Больше 10 % — только с руководителем и с отметкой в наряде |
| [Гарантия](warranty.md) | 30 дней на слесарные и электротехнические работы |
| [Смета и согласование работ](estimates-and-approvals.md) | Письменно, по каждой работе, не больше согласованного |
| [Платная диагностика и осмотры](diagnostic-fees.md) | Оплачивается и в ремонт не засчитывается |
| [Запчасти клиента](customer-supplied-parts.md) | Ставим; гарантия только на работу |
| [Предоплата](deposits.md) | Под заказные запчасти и капремонт АКПП |
| [Отмена записи и неявка](cancellations-and-no-shows.md) | Без штрафа; после двух неявок на время не записываем |
| [Невостребованные автомобили](storage-of-uncollected-cars.md) | Пять дней бесплатно |
| [Жалобы и претензии](complaints.md) | Выслушать в тот же день, ответить за один |
| [Работа мимо наряда, списания и возврат денег](voids-and-refunds.md) | Нет строки в наряде — нет ни работы, ни детали |
| [Карточки клиентов](customer-records.md) | Один клиент — одна карточка, настоящее имя |
| [Стандарты обслуживания](service-standards.md) | Как быстро отвечаем, перезваниваем и считаем смету |
| [Документы клиенту и НДС](documents-and-vat.md) | Заказ-наряд, акт, чек; НДС 5 % в цене |

*{S(2,'full')}*
""",
 diff=['Thirteen rows: the twelve of the English index and the Russian-only page on documents and VAT.',
       '"Voids and refunds" is «Работа мимо наряда, списания и возврат денег»: the Russian leak is work past the order and parts written off with no sale (R11).'])

page('policies/discounts.md', 'Скидки',
 f"""*{S(2,'full')} · Действует с {D('@discount_rule')} · Последнее изменение: {D('@belt_proposal')}*

## Правило

- **До 10 % от суммы заказ-наряда** мастер-приёмщик может дать сам. Причину пишет в наряде.
- **Больше 10 %** согласует руководитель, **до** закрытия наряда, и в наряде видно, кто согласовал. На Московском шоссе и на Инженерном это {P(4,'Сергей Анатольевич')}, на Технической — {P(22,'Ринат Фаридович')}. Если его нет на месте, звоните мне. Старший мастер-приёмщик такую скидку согласовать не может.
- 10 % считаются от **всей суммы наряда до скидки**: работы, запчасти, сборы и расходные материалы вместе.
- Скидка — это всё, от чего сумма становится меньше: минус в строке, срезанные нормо-часы «по-человечески», деталь в подарок, сбор, который «забыли» поставить.

## Чего нельзя ни при каком проценте

- **Скидки за наличные.** Её нет. Если клиент говорит, что раньше ему здесь так делали, ответ один: цена одна при любой оплате.
- **Цены «без оформления».** Работы без заказ-наряда у нас не бывает, и детали без строки в наряде — тоже. Об этом отдельная страница: [Работа мимо наряда, списания и возврат денег](voids-and-refunds.md).
- Округлять сумму вниз, чтобы закончить разговор.
- Давать скидку без записанной причины.

## Что скидкой не считается

- Договорной нормо-час, по которому платят {A('A1')} и {A('A2')}. Это другая цена, а не скидка.
- Гарантийный ремонт. Это гарантийный наряд без оплаты, привязанный к первому.
- Компенсация: когда ошиблись мы и исправляем за свой счёт. Компенсация больше 10 % идёт по тому же правилу, что и любая скидка: руководитель, отметка в наряде.

## Как я проверяю

Каждую пятницу мне приходит список всех нарядов со скидкой больше 10 % — с тем, кто её согласовал. Строка без согласующего — это разговор со мной в понедельник.

Это правило появилось из-за того, что мы нашли в Казани. Действует оно для всех.
""",
 diff=['Same rule and percentages (ledger price.discount_rule_pct, price.discount_base: the bill at list before the discount, as billed, VAT inside; the share is the same before VAT, so the page names no tax).',
       'The forbidden list adds the Russian form of the leak: a price "without paperwork", work with no order, a part with no order line (design R11).',
       'S8 in Russian: 1 800 RUB off a bill of 16 182,40 as billed (VAT inside) is 11.1 %, approved by slot 4 and recorded: inside the rule. Slot 23 gave 12 % twice in the last 30 days with no approver: outside it.'],
 new=['The advisor\'s own limit is up to 10 % with a written reason; lead advisors cannot approve above it; slot 2 is the fallback approver (as in English).'],
 created=(2, '@discount_rule'),
 rev=[(4, '@belt_proposal', 'added the line that the 10 % is measured on the whole bill before the discount: work, parts, fees and shop supplies together (the Russian bill holds VAT, so the line names no tax), after the timing-belt discount', {'message_ru': 'От всей суммы наряда до скидки. Всплыло на наряде по ремню ГРМ.'})])

page('policies/warranty.md', 'Гарантия',
 f"""*{S(2,'full')} · Действует с {D('@warranty_2424')} · Проверено: {D('T-4mo')}*

## Условия

**30 дней на слесарные и электротехнические работы.** Срок идёт со дня, когда клиент подписал акт выполненных работ. Пробегом гарантия не ограничена. Любой из трёх сервисов принимает гарантийный случай по ремонту, сделанному в другом.

| Случай | Гарантия |
|---|---|
| Слесарные и электротехнические работы | 30 дней |
| Запчасти, купленные у нас | Гарантия производителя, срок указываем в заказ-наряде. После 30 дней деталь меняем по гарантии, работа по замене платная |
| Колодки, щётки, лампы, свечи, фильтры | Только заводской брак. Износ — не брак |
| Аккумуляторы | По гарантийному талону производителя |
| Шины | Гарантия производителя; обращение оформляем мы |
| Работы подрядчика (капремонт АКПП, рулевая рейка, стёкла) | Гарантия подрядчика, письменно, отдаём клиенту вместе с заказ-нарядом |
| Б/у запчасти, которые клиент попросил поставить | На деталь гарантии нет; на работу — 30 дней |
| Запчасти клиента | Только на работу, 30 дней |
| Диагностика | Если наша диагностика оказалась неверной, клиент не платит за деталь, которая не помогла |
| Автомобили организаций | Те же сроки, что и у частных клиентов |

## На что гарантия не распространяется

ДТП. Перегрев или езда без масла после ремонта. Гонки и бездорожье. Вмешательство другого сервиса в тот же узел. Эвакуатор и такси — если только {P(4,'Сергей Анатольевич')} или {P(22,'Ринат Фаридович')} не решат иначе, в порядке компенсации.

## Как оформлять

1. Новый заказ-наряд, вид **гарантийный**, с привязкой к первому. Старый наряд не переоткрываем.
2. Первым машину смотрит мастер цеха: [Если машина вернулась](../shop-floor/when-a-car-comes-back.md).
3. Случай гарантийный — делаем бесплатно и говорим об этом прямо. Не гарантийный — объясняем почему, с первым нарядом в руках, и считаем смету, как на любую работу.
4. Не уверены — не решайте на приёмке. {P(4,'Сергей Анатольевич')} по Ульяновску, {P(22,'Ринат Фаридович')} по Казани, в тот же день.
5. Та же жалоба после 30 дней — наряд обычный, платный. Если видно, что виноваты всё-таки мы, руководитель оформляет компенсацию.

Что говорить клиенту на приёмке и трудные случаи: [Возврат на приёмке](../how-to/a-comeback-at-the-counter.md).

## Откуда сроки

Договор с клиентом — это заказ-наряд, и гарантийные сроки в нём напечатаны. С 1 сентября 2025 года действуют новые правила оказания услуг по ремонту автомобилей (постановление Правительства № 780), прежние, № 290, отменены. Минимального гарантийного срока в них нет: срок тот, что записан в договоре. Поэтому срок в заказ-наряде и срок на этой странице обязаны совпадать. Меняем одно — в тот же день меняем другое.

Среди ответов клиентам до сих пор висит старая страница про гарантию. Действуют эта страница и [Наша гарантия](../customers/warranty.md).
""",
 diff=['Terms from ledger s12.warranty.ru: 30 days on mechanical and electrical work; no mileage; honoured at any of the three shops.',
       'No business-use tier: company vehicles get the same terms (English: 12/12). The later revision (T-4mo) added that row and the closing line about the old page.',
       'A fifth write-up step: the same complaint after day 30 is a paid order (ledger comeback.definition).',
       'A section on where the terms come from: the order is the contract; ПП № 780 of 2025 replaced № 290 and sets no minimum warranty (research, read).'],
 new=['Used parts fitted at the customer\'s request: no warranty on the part, 30 days on the work.',
      'Wrong diagnosis: the customer does not pay for the part that did not fix the fault (as in English).',
      '1 September 2025 is written as a calendar date: a fact of law.'],
 verify=['Body work: see customers/warranty.md. The catalogue has no welding job; the price list names welding among the unpriced jobs.',
         'ПП № 780: in force from 2025-09-01, replaced № 290, no minimum warranty, warranty terms in the written contract "if set" (ru-shop.md, gap 15, read through a summarising fetch): re-read the primary text before the page is shown as legal guidance.'],
 msgs=['Корпоративные — те же сроки, записала отдельной строкой. Старую страницу ещё нужно убрать.'])

page('customers/warranty-policy.md', 'Гарантийные обязательства',
 f"""*Действует с {D('T-6y')} · Пересмотрено: {D('T-38mo')}*

На все работы, выполненные в «Ермак-Сервисе», даём гарантию **14 дней**.

- На электрооборудование (стартеры, генераторы, датчики, блоки управления) гарантии нет. Проверяйте при получении.
- Аккумуляторы — по талону завода.
- Тормозные колодки — 14 дней от заводского брака. Износ не в счёт.
- На запчасти клиента и на б/у запчасти гарантии нет никакой, ни на деталь, ни на работу.

Гарантийный ремонт делаем там, где делали машину. Заказ-наряд берите с собой.

Гарантия не действует, если машина побывала в ДТП, если ею пользовались не по назначению или продолжали ездить после поломки. Эвакуатор не оплачиваем.

Если клиент недоволен решением по гарантии — отправляйте ко мне.

*{S(1,'full')}*
""",
 diff=['STALE ON PURPOSE. 14 days on any work (ledger s12.warranty.ru old_page); no warranty on electrical equipment; only at the shop that did the work; nothing on customer parts or used parts; complaints to the founder.',
       'It contradicts the current pages on four points: the term (14 against 30 days), electrical work (none against 30 days), where it is honoured (the original shop against all three), customer parts (nothing against the work).',
       'Title «Гарантийные обязательства» beside «Наша гарантия» and the staff «Гарантия».'],
 new=['The old page gave no warranty on electrical equipment (a term seen in the research at one network).'])
