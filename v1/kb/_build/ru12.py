# -*- coding: utf-8 -*-
from kbr import *
REV = lambda: D('@price_rise+3wd:main')
RISE = ['Новый нормо-час.']
def three(key, cls='car'):
    return f"{t(key,'economy',cls)} / {t(key,'standard',cls)} / {t(key,'premium',cls)}"
def name(key):
    return JOBS[key]['name']

page('services/README.md', 'Услуги',
 f"""*{S(5,'full')} · Проверено: {REV()}*

По странице на каждый вид работ. На каждой: что это за работа, когда она нужна машине, что спросить у клиента, сколько она занимает и на чём клиенты спорят. Написано для приёмки, а не для цеха.

**Цены на этих страницах — примеры:** легковой автомобиль, запчасти стандарт, без расходных материалов. Они здесь, чтобы объяснить работу. Клиенту цену называем по [прайс-листу](../prices/price-list.md).

| Раздел | Страницы |
|---|---|
| ТО | [Замена масла](maintenance/oil-change.md) · [Фильтры и щётки](maintenance/filters-and-wipers.md) · [Свечи зажигания](maintenance/spark-plugs.md) · [Замена антифриза](maintenance/coolant-service.md) · [ТО по регламенту](maintenance/scheduled-maintenance.md) · [Промывка инжектора и топливный фильтр](maintenance/fuel-system-service.md) · [ТО коммерческого автомобиля](maintenance/fleet-pm-service.md) |
| Тормоза | [Диагностика тормозов](brakes/brake-inspection.md) · [Колодки и диски](brakes/pads-and-rotors.md) · [Суппорты и барабанные тормоза](brakes/calipers-and-drum-brakes.md) · [Замена тормозной жидкости](brakes/brake-fluid-flush.md) |
| Шины | [Сезонный шиномонтаж и хранение шин](tires/seasonal-changeover-and-storage.md) · [Балансировка, перестановка и ремонт прокола](tires/rotation-balance-and-flat-repair.md) · [Сход-развал](tires/alignment.md) · [Новые шины и датчики давления](tires/new-tires-and-tpms.md) |
| Диагностика | [Горит «чек»](diagnostics/check-engine-light.md) · [Поиск неисправностей электрики](diagnostics/electrical-diagnosis.md) · [Стуки и вибрации](diagnostics/noises-and-vibrations.md) |
| Ходовая | [Стойки и амортизаторы](suspension/struts-and-shocks.md) · [Детали передней подвески](suspension/front-end-parts.md) · [Ступичные подшипники и рулевые рейки](suspension/wheel-bearings-and-steering-racks.md) |
| Кондиционер | [Диагностика и заправка](ac/ac-check-and-recharge.md) · [Компрессор и радиатор кондиционера](ac/ac-compressor-and-condenser.md) |
| Электрика | [Аккумулятор](electrical/battery.md) · [Генератор и стартер](electrical/alternator-and-starter.md) |
| Двигатель | [Ремень ГРМ](engine/timing-belt.md) · [Ремень навесных агрегатов](engine/drive-belt.md) · [Ремонт системы охлаждения](engine/cooling-system-repairs.md) · [Течи и прокладки](engine/leaks-and-gaskets.md) · [Зажигание, датчики и бензонасос](engine/ignition-sensors-and-fuel-pump.md) · [Опоры двигателя и глушитель](engine/mounts-and-exhaust.md) |
| Трансмиссия | [Замена масла в коробке](transmission/transmission-fluid-service.md) · [Сцепление и ШРУСы](transmission/clutch-and-cv-axles.md) · [Капитальный ремонт АКПП](transmission/transmission-rebuild.md) |
| Осмотры | [Осмотр по чек-листу](inspections/courtesy-inspection.md) · [Диагностика перед покупкой](inspections/pre-purchase-inspection.md) |

Отдельно: [Гибриды](hybrids.md).
""",
 diff=['38 service pages: the 37 of the English base and the seasonal tyre page, which exists only in Russian.',
       'Prices are examples: a passenger car, standard parts, before shop supplies; VAT is inside, as in the price list.',
       'The old page services/brakes/brake-questions.md is not in this index.'],
 msgs=RISE)

page('services/maintenance/oil-change.md', 'Замена масла',
 f"""*{S(5,'full')} · Проверено: {REV()}*

В наряде: **{name('oil_service')}**. Каждая четвёртая машина заезжает к нам именно за этим.

## Что входит

Слить старое, поставить новый фильтр, залить до четырёх литров масла, сбросить межсервисный интервал, долить омыватель, проверить давление в шинах — и осмотр по чек-листу. Работы на {hrs('oil_service')} нормо-часа; вместе с осмотром закладывайте час. Клиент может подождать.

## Три цены

| Масло | Фильтр | Цена |
|---|---|---:|
| {brand('oil_service',0,'economy')} | {brand('oil_service',1,'economy')} | {t('oil_service','economy')} |
| {brand('oil_service',0,'standard')} (его и считаем в смету) | {brand('oil_service',1,'standard')} | {t('oil_service')} |
| {brand('oil_service',0,'premium')} | Оригинал | {t('oil_service','premium')} |

Работа считается по нормо-часу, поэтому к ней идут расходные материалы. Если мотор берёт больше четырёх литров, каждый следующий литр стандартного масла — {part('oil_service',0)}. Кроссоверы и моторы от двух литров обычно берут.

## Спросить

- Год, марка, модель, двигатель. От двигателя зависят литры, допуск масла и фильтр.
- Пробег сейчас и при прошлой замене, если помнит.
- «А что-нибудь ещё беспокоит?» Это самый дешёвый визит, на котором находят самую дорогую неисправность.

## Сказать

- «Около часа. Заодно осмотрим машину и пришлём фотографии».
- Спрашивает, как часто: по сервисной книжке, а для города с короткими поездками — каждые 7 500–10 000 км или раз в год. Не каждые пять тысяч: лишних замен мы не продаём.
- Своё масло — обычное дело. Канистра должна быть запечатана. Тогда клиент платит за работу, {lab('oil_service')}, и за фильтр; гарантия — на работу.

## Клиент говорит

- **«В гараже за пятьсот рублей поменяют».** «Поменяют. Только машину там никто не осмотрит, а что залили и что написали — узнать будет не у кого. У нас с маслом эконом — {t('oil_service','economy')}, и механик смотрит машину по чек-листу».
- **«А зачем дорогое масло?»** Смотрим допуск в сервисной книжке. Требует производитель определённый допуск — льём масло с этим допуском. Не требует — выбор за клиентом, и на старом моторе эконом вполне годится.
""",
 diff=['The Russian oil service is priced by the hour (0.7 н/ч) with four litres and carries shop supplies; a quarter of orders carry it (catalogue share 0.244).',
       'Tiers: Лукойл Люкс with BIG Filter, Лукойл Genesis with MANN-FILTER, Shell Helix Ultra with the original filter.',
       'Interval 7 500 to 10 000 km or a year; the objection is «в гараже дешевле».',
       'A paragraph on customers who bring their own oil.'],
 new=['Own oil is accepted in a sealed can: labour and the filter are charged.'],
 msgs=RISE)

page('services/maintenance/filters-and-wipers.md', 'Фильтры и щётки',
 f"""*{S(5,'full')} · Проверено: {REV()}*

Три мелкие работы, которые почти всегда появляются из осмотра, а не из просьбы клиента.

| Работа | Время | Стандарт | От эконом до премиум |
|---|---|---:|---|
| Воздушный фильтр двигателя | {hrs('engine_air_filter')} н/ч | {t('engine_air_filter')} | от {t('engine_air_filter','economy')} до {t('engine_air_filter','premium')} |
| Салонный фильтр | {hrs('cabin_air_filter')} н/ч | {t('cabin_air_filter')} | от {t('cabin_air_filter','economy')} до {t('cabin_air_filter','premium')} |
| Щётки стеклоочистителя, комплект | {hrs('wiper_blades')} н/ч | {t('wiper_blades')} | от {t('wiper_blades','economy')} до {t('wiper_blades','premium')} |

- **Покажите старый.** Серый салонный фильтр с листьями и пухом продаёт себя сам. Чистый фильтр мы не рекомендуем, и клиент запоминает, что мы его не рекомендовали.
- Салонный — раз в год, перед летом; тем, кто ставит машину под тополями, чаще. Если из дефлекторов пахнет — начинаем с него.
- Щётки: полосят или скрипят. В цене почти всё — сами щётки, работа там копеечная.
- Клиент знает, что фильтр в магазине стоит дешевле. Скажите это первым: «Этот вы можете поменять и сами, выйдет почти вдвое дешевле. Если хотите, чтобы сделали мы, пока машина у нас, — это десять минут».

Топливный фильтр — другая работа и другая страница: [Промывка инжектора и топливный фильтр](fuel-system-service.md).
""",
 diff=['Wiper blades carry a small labour charge (0.1 н/ч) in the Russian catalogue; the blades are most of the price.',
       'Cabin filter yearly, before summer.'],
 msgs=RISE)

page('services/maintenance/spark-plugs.md', 'Свечи зажигания',
 f"""*{S(5,'full')} · Проверено: {REV()}*

Клиент редко просит «поменять свечи». Он говорит: троит, плохо заводится на холодную, расход вырос, тянуть перестала. Иногда за этим свечи, иногда нет. Если горит «чек» — сначала [диагностика](../diagnostics/check-engine-light.md).

## Свечи

В наряде: **{name('spark_plugs')}**. Обычные никелевые свечи ходят тысяч тридцать, иридиевые — шестьдесят и больше. Потом мотор начинает дёргаться по утрам и больше есть.

- Четырёхцилиндровый легковой: {hrs('spark_plugs')} нормо-часа, {t('spark_plugs')} со свечами {brand('spark_plugs',0,'standard')}.
- **На рамном внедорожнике это другая работа.** У V6 половина свечей под впускным коллектором, и его снимают. Работа — {lab('spark_plugs', cls='truck')} вместо {lab('spark_plugs')}, и свечей шесть, а не четыре. Считайте по [таблице классов](../../prices/labour-rates-and-fees.md), а не по этой странице.
- Кроссоверы и фургоны — посередине.

## Спросить

- Сколько цилиндров? Не знает — год, марка, модель, и смотрим сами.
- Горит ли «чек»? Горит — записываем на диагностику, а не на свечи. Свечи на машине с умершей катушкой — деньги, потраченные дважды.
- Когда меняли в последний раз? «Ни разу» на ста двадцати тысячах — не редкость.

## Клиент говорит

- **«Поменяйте свечи, сколько это?»** «На ваш четырёхцилиндровый — {t('spark_plugs')}. Если троит, давайте сначала посмотрим, в свечах ли дело: диагностика покажет».
- **«А почему на „Прадо“ вдвое дороже?»** «Половина свечей под впускным коллектором. Это больше часа работы вместо получаса, и свечей шесть».

Отказала одна катушка: [Зажигание, датчики и бензонасос](../engine/ignition-sensors-and-fuel-pump.md).
""",
 diff=['No "tune-up" in Russian: customers say «троит», «плохо заводится», «расход вырос».',
       'Four plugs, 0.6 н/ч; the heavy case is the body-on-frame class (labour multiplier 2.0), crossovers and vans 1.2.',
       'The six-plug total for a V6 is not printed and must be computed from the class table (the Russian twin of C2.1).'],
 new=['Nickel plugs about 30 000 km, iridium 60 000 km and more.'],
 msgs=RISE)

page('services/maintenance/coolant-service.md', 'Замена антифриза',
 f"""*{S(5,'full')} · Проверено: {REV()}*

В наряде: **{name('coolant_exchange')}**. {hrs('coolant_exchange')} нормо-часа, {t('coolant_exchange')}, шесть литров нужного антифриза.

Антифриз стареет: присадки, которые защищают от коррозии, вырабатываются лет за пять. Старый антифриз съедает помпу и радиатор изнутри.

- Продаётся из осмотра: механик проверяет антифриз тестером и пишет результат.
- **Антифриз подбирается по допуску производителя, а не по цвету.** У Renault он один, у Hyundai и Kia другой, у «Газели» третий. «Любой красный» в машину моложе десяти лет не льём.
- Антифриза мало — это течь, а не замена. Сначала опрессовка ({t('cooling_pressure_test')}): [Ремонт системы охлаждения](../engine/cooling-system-repairs.md).
- В любую работу, где система охлаждения вскрывается (помпа, термостат, радиатор, ремень ГРМ на части моторов), антифриз уже входит. Сверху эту работу не продаём.
""",
 diff=['«Замена охлаждающей жидкости», 1.2 н/ч, six litres. Coolant is chosen by the maker\'s approval, not by colour.'],
 new=['Five years as the interval.'],
 msgs=RISE)

page('services/maintenance/scheduled-maintenance.md', 'ТО по регламенту',
 f"""*{S(5,'full')} · Проверено: {REV()}*

В наряде: **{name('scheduled_maintenance')}**. {hrs('scheduled_maintenance')} нормо-часа, {t('scheduled_maintenance')} — только работа.

За эти деньги делаем всё, что производитель велит проверить на этом пробеге, и делаем как следует. Тормоза замерены на снятых колёсах, подвеска и рулевое проверены на подъёмнике, петли и замки смазаны, жидкости проверены и долиты, аккумулятор проверен, контрольная поездка, межсервисный интервал сброшен.

**Запчасти и жидкости, которые положены по регламенту, сюда не входят.** Это отдельные строки, по прайсу, и на разном пробеге они разные:

| Пробег | Что обычно ещё положено |
|---|---|
| 15 000 км | Масло с фильтром, воздушный и салонный фильтры |
| 30 000 км | То же и тормозная жидкость |
| 60 000 км | То же, плюс свечи и масло в автоматической коробке; спросить про ремень ГРМ |
| 90 000 км | Как на 30 000, плюс антифриз, если не меняли |

Поэтому ТО на 30 000 — это не {t('scheduled_maintenance')}. Сложите всё по прайсу до приезда клиента, чтобы сумма на приёмке совпала с той, что он слышал по телефону.

- Клиент говорит «сделать ТО» и чаще всего имеет в виду масло с фильтрами. Спросите пробег и что написано в сервисной книжке: по ней и считаем.
- Регламент смотрите для конкретной машины. Таблица — ориентир, а не правило.
- Спрашивают, можно ли обслуживать гарантийную машину не у дилера. Отвечаем аккуратно: условия гарантии записаны в сервисной книжке, посмотрите её. Заказ-наряд, акт и чеки мы выдаём полные.
""",
 diff=['Russian service intervals are 15 000 km; the table is by 15 000 / 30 000 / 60 000 / 90 000 km.',
       'The customer\'s word is «сделать ТО» (the Russian twin of C6.1).',
       'A full quote for the 30 000 km service must be added up from the price list (labour, oil service, both filters, brake fluid).',
       'On new cars under the maker\'s warranty the page gives no legal advice: it points to the service book.'],
 new=['The table of typical extras by mileage.'],
 msgs=RISE)

page('services/maintenance/fuel-system-service.md', 'Промывка инжектора и топливный фильтр',
 f"""*{S(5,'full')} · Проверено: {REV()}*

Две работы.

**{name('fuel_system_cleaning')}**: {hrs('fuel_system_cleaning')} нормо-час, {t('fuel_system_cleaning')}. Мотор какое-то время работает на промывочной жидкости вместо бензина. Помогает моторам с пробегом, у которых плавает холостой ход и пропала приёмистость. Машине, которая едет нормально, это не даёт ничего, и мы ей это не продаём.

**{name('fuel_filter')}**: {hrs('fuel_filter')} нормо-часа, {t('fuel_filter')}. Только там, где фильтр стоит отдельно: «Гранта», «Логан», «Газель» и многое из того, что ездит к нам каждый день. На Solaris и Rio он в баке, вместе с насосом, и это уже другая работа. Если справочник не предлагает замену для этой машины, отдельного фильтра у неё нет.

Клиенты просят «промыть форсунки», потому что так было написано на бутылке с присадкой. Говорите честно: если машина плохо едет, первая работа — [диагностика](../diagnostics/check-engine-light.md), а не промывка.
""",
 diff=['«Промывка инжектора без снятия форсунок» (1.0 н/ч) and «Замена топливного фильтра» (0.4 н/ч, reference Lada Granta). A separate fuel filter is still common on the Russian parc.'],
 msgs=RISE)

page('services/maintenance/fleet-pm-service.md', 'ТО коммерческого автомобиля',
 f"""*{S(4)} · Проверено: {REV()}*

В наряде: **{name('fleet_pm_van')}**. Только для фургонов и «Газелей». {hrs('fleet_pm_van', cls='van')} нормо-часа.

## Что входит

- Масло и фильтры: шесть литров дизельного масла по {part('fleet_pm_van',0)} за литр, масляный фильтр за {part('fleet_pm_van',1)} и воздушный за {part('fleet_pm_van',2)}.
- Смазка по точкам, где есть пресс-маслёнки. Петли дверей, направляющая сдвижной двери, ограничители задних дверей.
- Осмотр по чек-листу: тормоза с замером на всех колёсах, шины с остатком протектора и годом выпуска, свет, включая освещение кузова, ремни, патрубки, течи, аккумулятор, щётки, сигнал, люфт руля, крепление перегородки и пола грузового отсека.
- Заполненный лист по машине: гаражный номер, пробег, что подойдёт к следующему ТО.

## Цена

По прайсу: работа {lab('fleet_pm_van', cls='van')} плюс масло и фильтры, всего **{t('fleet_pm_van', cls='van')}** без расходных материалов, в том числе НДС.

Клиенты с договорным нормо-часом платят за работу по договорной ставке, а за масло и фильтры — на 10 % меньше: см. [Корпоративные клиенты](../../accounts/company-account-terms.md). Считайте оттуда. По памяти эту цифру не называют.

## Как это устроено

- Каждые 10 000 км для парков доставки. Список машин, которым подошёл срок, присылает транспортный отдел клиента.
- Машина возвращается в тот же день. Из-за ТО фургон рейс не пропускает.
- **Всё найденное — это смета ответственному по договору**, а не разговор с водителем сверх его лимита.
- Литры по машинам: [Жидкости и заправочные объёмы](../../parts/fluids-and-capacities.md).
""",
 diff=['«ТО коммерческого автомобиля» (reference ГАЗель Next with the Cummins diesel): 1.5 н/ч, six litres of diesel oil, an oil filter and an air filter; list 9 710 RUB.',
       'The contract price is deliberately not printed: 1.5 × 1 700 = 2 550 labour plus 0.9 × 6 860 of oil and filters = 8 724 RUB before shop supplies, VAT inside: what the account pays (the Russian twin of P5.6; ledger kb.worked_answers, price.company_rounding).',
       'Interval 10 000 km.'],
 new=['Expected answer for "what does «Симбирский гонец» pay for the service": 8 724 RUB before shop supplies, VAT inside.'],
 msgs=RISE)

# ---------------------------------------------------------------- тормоза
page('services/brakes/brake-inspection.md', 'Диагностика тормозов',
 f"""*{S(16,'full')} · Проверено: {REV()}*

С неё начинается любая жалоба на тормоза. В наряде: **{name('brake_inspection')}**, {t('brake_inspection')}, полчаса. Цена фиксированная.

Снимаем все четыре колеса. Колодки и диски меряем в миллиметрах, смотрим шланги и трубки, проверяем, не закисли ли направляющие суппортов, проверяем жидкость. Если на машине можно ехать — короткая контрольная поездка. Клиент получает замеры и фотографии.

Записывайте именно на диагностику, а не «на тормоза». Пока колёса не сняты, мы не знаем, что нужно машине. И клиент не знает, что бы ему ни сказали в прошлом сервисе.

- Машина уже у нас на другой работе, и механик через диск увидел тонкие колодки — это бесплатный осмотр по чек-листу сделал своё дело. Диагностику за это в наряд не ставим.
- В стоимость ремонта диагностика не засчитывается. [Почему](../../policies/diagnostic-fees.md).
- Скрежет, педаль проваливается или горит лампа тормозов — скажите клиенту далеко не ездить и предложите [эвакуатор](../../customers/towing.md).

Дальше обычно идут [колодки и диски](pads-and-rotors.md).

*{P(16,'Света')}*
""",
 diff=['«Диагностика тормозной системы», a fixed 700 RUB, 0.4 н/ч.'],
 msgs=RISE)

page('services/brakes/pads-and-rotors.md', 'Колодки и диски',
 f"""*{S(16,'full')} · Проверено: {REV()}*

Главная работа по тормозам. Считается на ось.

## Что продаём

| В наряде | Н/ч | Эконом / Стандарт / Премиум |
|---|---|---|
| {name('front_pads_rotors')} | {hrs('front_pads_rotors')} | {three('front_pads_rotors')} |
| {name('rear_pads_rotors')} | {hrs('rear_pads_rotors')} | {three('rear_pads_rotors')} |
| {name('front_brake_pads')} | {hrs('front_brake_pads')} | {three('front_brake_pads')} |
| {name('rear_brake_pads')} | {hrs('rear_brake_pads')} | {three('rear_brake_pads')} |

Легковой автомобиль, без расходных материалов. Кроссоверы, рамные внедорожники и фургоны дороже: [таблица классов](../../prices/labour-rates-and-fees.md).

## Одни колодки или с дисками?

Диски мы меряем. Если толщина больше минимальной, которая выбита на самом диске, поверхность ровная и биения нет — меняем одни колодки, и я продаю это с чистой совестью. Если диск тоньше допуска, с бортиком, с задирами или посинел, новые колодки на нём заскрипят и через месяц вернутся. Тогда колодки с дисками, и я показываю клиенту замер. Проточку дисков не делаем: на современном тонком диске протачивать нечего.

## Какие колодки

Стандарт — {brand('front_brake_pads',0,'standard')}: такие я поставила бы на свою машину. Премиум — {brand('front_brake_pads',0,'premium')}: меньше пылят, дольше ходят, стоят своих денег, если человек на машине надолго. Эконом — {brand('front_brake_pads',0,'economy')}, и это нормальные колодки. Подробнее: [Какие колодки мы ставим](../../parts/brake-pads-we-fit.md).

## По телефону

- Ни одной цены без машины и без слова «если». «Если нужны передние диски с колодками, на ваш Solaris это {t('front_pads_rotors')}. Если диски в допуске — {t('front_brake_pads')}. Что именно, покажет диагностика».
- Потом время. Машина, которую поставили к девяти, к вечеру готова, если запчасти на полке. На ходовые модели они на полке.

## На приёмке

Сначала фото. Старая колодка рядом с новой. Потом цена. Потом: «Могу сделать сегодня к пяти или в четверг с утра. Делаем?»

## Клиент говорит

- **«В другом сервисе сказали пять тысяч за тормоза».** «За одни колодки, на одну ось и с самыми дешёвыми колодками. Про диски скажут, когда снимут колёса. У нас с колодками эконом — {t('front_brake_pads','economy')}. Посчитать вам оба варианта?»
- **«А можно только колодки?»** «Если диски в допуске — да, и я вам так и скажу. Если нет, лучше не делать ничего, чем выбросить деньги на колодки».
- **«А свои колодки можно?»** Можно: [Запчасти клиента](../../policies/customer-supplied-parts.md). Гарантия тогда только на установку.
- **«Скрипят, а меняли недавно».** Где? У нас и месяца не прошло — это [возврат](../../how-to/a-comeback-at-the-counter.md), смотрим бесплатно. Не у нас — диагностика.

Гарантия на работу по тормозам — 30 дней. На сами колодки и диски — от заводского брака. Износ — не брак.

*{P(16,'Света')}*
""",
 diff=['Four catalogue jobs under their Russian order names, hours and the three tier totals.',
       'Disc machining (проточка) is common in Russia: the page says the shop does not do it.',
       'Pads: Sangsin Hi-Q (standard), TRW (premium), Marshall (economy).',
       'Warranty: 30 days on the work; pads and discs against factory defects.',
       'A row on the customer\'s own pads. «Делаем?» is slot 16\'s closing word.',
       'The competitor figure is a customer\'s words, written in words.'],
 new=['The shop does not machine discs (no catalogue job).'],
 msgs=RISE)

page('services/brakes/calipers-and-drum-brakes.md', 'Суппорты и барабанные тормоза',
 f"""*{S(16,'full')} · Проверено: {REV()}*

**{name('brake_caliper')}**: {hrs('brake_caliper')} нормо-часа, {t('brake_caliper')} с новым суппортом {brand('brake_caliper',0,'standard')}. Считается за одну сторону. Суппорт меняют, когда он течёт или когда закис поршень или направляющие. Признаки: одна колодка стёрта в ноль, а вторая как новая; колесо горячее после поездки; машину тянет в сторону при торможении. Обычно это находят, когда меняют колодки, поэтому клиент узнаёт о суппорте по телефону, а не при приёмке. Держите фото под рукой.

Меняем тот, который отказал. Если второй того же возраста и пыльник на нём порван, говорим об этом, а решает клиент.

Если суппорт можно спасти ремкомплектом, механик скажет. Этой работы в прайсе нет: цену считает старший мастер-приёмщик.

**{name('rear_brake_shoes')}**: {hrs('rear_brake_shoes')} нормо-часа, {t('rear_brake_shoes')}. Барабаны сзади стоят на половине машин, которые к нам ездят: «Гранта», «Логан», «Ларгус», простые «Солярисы». Колодки в барабане живут долго, тысяч до ста, поэтому клиент про них обычно и не слышал. «Работа та же, что с дисковыми, только тормоз старого типа. Возни больше, поэтому почти два часа».

*{P(16,'Света')}*
""",
 diff=['The standard caliper is a new one (Mando), not a remanufactured one: there is no core to return.',
       'Drum brakes at the rear are common on the Russian parc (Granta, Logan, Largus, basic Solaris).',
       'A caliper repair kit is named as a job with no list price.'],
 msgs=RISE)

page('services/brakes/brake-fluid-flush.md', 'Замена тормозной жидкости',
 f"""*{S(16,'full')} · Проверено: {REV()}*

В наряде: **{name('brake_fluid_exchange')}**. {hrs('brake_fluid_exchange')} нормо-час, {t('brake_fluid_exchange')}.

Тормозная жидкость набирает воду из воздуха. Жидкость с водой закипает на долгом спуске к Волге с полной машиной, а ещё от неё изнутри ржавеют суппорты и блок ABS. Менять раз в два года, при любом пробеге.

- На осмотре механик проверяет жидкость тестером и пишет процент. Больше 3 % воды — рекомендация. Покажите клиенту цифру.
- В девяти случаях из десяти эта работа продаётся из осмотра. Сам с этим никто не звонит.
- Клиенты называют это «прокачать тормоза». Прокачка — только часть работы: при замене суппорта или шланга прокачивается один контур, а не меняется вся жидкость. Если жидкость старая, продавайте обе работы вместе: система всё равно вскрыта.

*{P(16,'Света')}*
""",
 diff=['Every two years. The local line is a long descent to the Volga instead of the mountains near Chattanooga.',
       'Customers call it «прокачать тормоза».'],
 new=['The 3 % water threshold (as in English).'],
 msgs=RISE)

page('services/brakes/brake-questions.md', 'Вопросы по тормозам',
 f"""*В. С. · {D('T-9mo')}*

Короткие ответы для телефона. Нормо-час {rate('standard','before_rise')}.

**Сколько стоят тормоза?**
Передние диски с колодками, на большинство машин: {told('front_pads_rotors')} с колодками Hi-Q. 1,8 н/ч по {rate('standard','before_rise')} плюс запчасти.
Задние диски с колодками: {told('rear_pads_rotors')}.
Только колодки, перед: {told('front_brake_pads')}. Зад: {told('rear_brake_pads')}.
Кроссоверы и «Газели» дороже. Всегда говорить «на большинство машин».

**Сколько стоит посмотреть?**
Диагностика {told('brake_inspection')}. Полчаса.

**Сколько по времени?**
Диски с колодками — два часа на ось. С утра поставил, к обеду забрал.

**Диски точите?**
Нет. Меняем.

**Тормозная жидкость?**
Замена {told('brake_fluid_exchange')}. Раз в 2 года.

**Скрипят после замены?**
Первые дни нормально, притираются. Через неделю всё ещё скрипят — пусть приезжает, посмотрим бесплатно.

**Гарантия?**
30 дней на работу. Колодки — от брака.

**«Вечные» колодки?**
Не ставим. Кто ставит, отбивает своё на дисках.

В. С.
""",
 diff=['STALE ON PURPOSE (S12): the hour of 1 760 RUB from before the last rise (the last but one of the history) and the before-rise totals: front discs and pads 12 268 (ledger s12.brake_price.ru stale; current 12 520), rear discs and pads, front pads, rear pads, inspection 650 (current 700), fluid 2 340 (current 2 480).',
       'Signed «В. С.» (cast: slot F3 signs his order comments so), dated nine months before T; he resigned in week T-30. The date is after the second rise (eleven months before T), so the hour it shows was the current one when it was written.',
       'Its other answers (no disc machining, 30 days on the work) agree with the current pages.'])
