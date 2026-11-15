# -*- coding: utf-8 -*-
from kbr import *
import kbr, kbb, json, os
if MODE == 'before_rise':
    raise SystemExit  # the binaries have no earlier text

CLS = ['car', 'suv', 'truck', 'van']
BY_CLASS = [('front_pads_rotors', 'Передние диски и колодки'), ('rear_pads_rotors', 'Задние диски и колодки'), ('front_brake_pads', 'Передние колодки'),
            ('front_struts_pair', 'Передние стойки, пара'), ('rear_shocks_pair', 'Задние амортизаторы, пара'), ('wheel_bearing', 'Подшипник передней ступицы, одна сторона'),
            ('wheel_alignment', 'Сход-развал, две оси'), ('seasonal_tyre_change', 'Сезонный шиномонтаж, 4 колеса'), ('seasonal_wheel_swap', 'Колёса в сборе, 4 шт.'),
            ('alternator', 'Генератор'), ('starter', 'Стартер'), ('water_pump', 'Помпа'), ('radiator', 'Радиатор'), ('spark_plugs', 'Свечи зажигания'),
            ('timing_belt_kit', 'Ремень ГРМ с роликами и помпой'), ('clutch_kit', 'Сцепление в сборе')]
rows = []; classfacts = []
for k, n in BY_CLASS:
    vals = [nt(k, cls=c) for c in CLS]
    classfacts.append({'catalogue_key': k, 'car': vals[0], 'suv': vals[1], 'truck': vals[2], 'van': vals[3]})
    rows.append(f"| {n} | {M(vals[0])} | {M(vals[1])} | {M(vals[2])} | {M(vals[3])} |")
MENU = [('oil_service', 'Замена масла и фильтра: работа, 4 л масла, фильтр'), ('seasonal_tyre_change', 'Сезонный шиномонтаж, 4 колеса с балансировкой'),
        ('seasonal_wheel_swap', 'Сезонная замена колёс в сборе, 4 шт.'), ('tyre_storage', 'Хранение комплекта шин, сезон'), ('wheel_balance', 'Балансировка, 4 колеса'),
        ('tyre_repair', 'Ремонт прокола'), ('wheel_alignment', 'Сход-развал, две оси'), ('brake_inspection', 'Диагностика тормозной системы'),
        ('suspension_diag', 'Диагностика ходовой части'), ('ac_performance_check', 'Диагностика кондиционера'), ('check_engine_diag', 'Компьютерная диагностика двигателя'),
        ('electrical_diag', 'Поиск неисправности электрооборудования, 1,5 н/ч'), ('battery_test', 'Проверка АКБ и системы зарядки'),
        ('brake_fluid_exchange', 'Замена тормозной жидкости'), ('coolant_exchange', 'Замена антифриза'), ('ac_recharge', 'Заправка кондиционера, R134a'),
        ('ac_recharge_1234yf', 'Заправка кондиционера, R1234yf'), ('pre_purchase_inspection', 'Диагностика перед покупкой'), ('battery_replace', 'Аккумулятор 60 А·ч, стандарт, с установкой')]
menurows = '\n'.join(f"| {n} | {M(nt(k))} |" for k, n in MENU)

HEAD = ['Автомобиль', 'Двигатель', 'Масло', 'Литров с фильтром', 'Антифриз', 'Коробка', 'У кого встречается']
FLUID = [
 ('ГАЗель Next, фургон и борт', 'Cummins ISF 2.8, дизель', '10W-40 CI-4', '6,0', 'G12 красный', 'МКПП, 75W-90 GL-4', '«Симбирский гонец», «Тёплый контур», «Чистый Венец» № 7, «Идель-Электромонтаж», «Вкусный выезд» № 1–3'),
 ('ГАЗель NN, фургон', 'Cummins ISF 2.8 или G21A 2.5, дизель: смотреть по VIN', '10W-40 CI-4', '6,0', 'G12 красный', 'МКПП, 75W-90 GL-4', '«Симбирский гонец»'),
 ('ГАЗель Бизнес 2705', 'УМЗ-4216, бензин', '10W-40 SL', '5,0', 'G11 зелёный', 'МКПП, 75W-90 GL-4', '«Симбирский гонец», три старые машины'),
 ('LADA Largus', '1.6 16 кл. (K4M), ремень ГРМ', '5W-40', '4,8 (в наряд 5)', 'Type D жёлтый', 'МКПП, 75W-80', '«Симбирский гонец», «Тёплый контур», «Вкусный выезд», «Идель-Электромонтаж»'),
 ('LADA Largus', '1.6 8 кл. (K7M)', '5W-40', '3,3 (в наряд 3,5)', 'Type D жёлтый', 'МКПП, 75W-80', '«Чистый Венец»'),
 ('LADA Granta', '1.6 8 кл. (11186)', '5W-40', '3,2 (в наряд 3,5)', 'G12 красный', 'МКПП, 75W-85', 'автошкола, «Тёплый контур», «Чистый Венец»'),
 ('LADA Niva Legend', '1.7 (21214)', '5W-40', '3,75 (в наряд 4)', 'G12 красный', 'МКПП; мосты и раздатка — отдельные работы', '«Тёплый контур», «Идель-Электромонтаж» Э-9'),
 ('УАЗ 3909 и УАЗ Профи', 'ЗМЗ-409 и ZMZ Pro 2.7', '10W-40', '7,0', 'G12 красный', 'МКПП, 75W-90 GL-4', '«Тёплый контур», «Идель-Электромонтаж» Э-7, Э-8'),
 ('Ford Transit, фургон', '2.2 TDCi, дизель, сажевый фильтр', '5W-30, только с допуском Ford WSS-M2C913-D', '6,2 (в наряд 6,5)', 'Оранжевый (Ford)', 'Не обслуживаем', '«Симбирский гонец», «Идель-Электромонтаж» Э-10, «Вкусный выезд» № 7'),
 ('Hyundai Solaris и Kia Rio', '1.6 (G4FC)', '5W-30 или 5W-40', '3,6 (в наряд 4)', 'Зелёный (Hyundai Long Life)', 'АКПП: ATF SP-IV. МКПП: 75W-85', 'самые частые машины частных клиентов; «Чистый Венец» № 8, автошкола № 6, «Вкусный выезд» № 9'),
 ('Renault Logan', '1.6 8 кл. (K7M)', '5W-40', '3,3 (в наряд 3,5)', 'Type D жёлтый', 'МКПП, 75W-80', '«Чистый Венец» № 9, автошкола № 5'),
 ('Renault Logan', '1.6 16 кл. (K4M), ремень ГРМ', '5W-40', '4,8 (в наряд 5)', 'Type D жёлтый', 'МКПП, 75W-80', 'частные клиенты'),
 ('Renault Duster', '2.0 (F4R)', '5W-40', '5,4 (в наряд 5,5)', 'Type D жёлтый', 'МКПП, 75W-80; АКПП: смотреть по VIN', '«Тёплый контур», «Идель-Электромонтаж» Э-11, частные клиенты'),
]
fl = '\n'.join('| ' + ' | '.join(r) + ' |' for r in FLUID)
EXTRA = [('LADA Vesta', '1.6 (21129)', '5W-40', 'заполнить', 'заполнить', 'заполнить', 'автошкола № 4 и № 7, «Вкусный выезд» № 10'),
         ('Citroën Jumper, фургон', '2.2 HDi, дизель', 'заполнить', 'заполнить', 'заполнить', 'заполнить', '«Вкусный выезд» № 8')]
fx = '\n'.join('| ' + ' | '.join(r) + ' |' for r in EXTRA)
hd = '| ' + ' | '.join(HEAD) + ' |\n|' + '---|' * len(HEAD)
BOOTS, TOOLS = 3000, 12000

doc = f"""# Вложенные документы базы знаний (русская конфигурация)

Пять файлов — не Markdown. Здесь лежат их черновики; на следующем шаге каждый превращается в файл указанного формата и кладётся по указанному пути рядом со страницами. Даты записаны по грамматике из `OUTLINE.md`. Что движок базы знаний делает с каждым форматом (его `docs/search.md`): **из PDF, DOCX и PPTX текст извлекается** и участвует в поиске, с указанием места (PDF — страница; \
DOCX — абзац и заголовок раздела; PPTX — номер и заголовок слайда). **Из XLSX текст не извлекается**: файл находится по имени, а прочитать его помощник не может. Распознавания картинок нет, поэтому PDF должны быть текстовыми, а не сканами. Абзац курсивом под заголовком каждого файла описывает файл для сборки и в сам файл не входит.

| № | Путь | Формат | Кто видит | Страниц или слайдов | Что есть только здесь |
|---|---|---|---|---|---|
| 1 | `prices/counter-price-sheet.pdf` | PDF, A4, текстовый | приёмка и выше | 2 страницы | цены по классам автомобилей на шестнадцать частых работ (страница 2) |
| 2 | `team/staff-handbook.docx` | Word | приёмка и выше | около 9 страниц, 12 разделов | отпуск, праздничные дни, опоздания и взыскания, компенсации, увольнение |
| 3 | `parts/fleet-fluid-sheet.xlsx` | Excel, один лист «Жидкости» | приёмка и выше | 15 строк | помощнику не читается; две строки, которых нет в PDF |
| 4 | `parts/fleet-fluid-sheet.pdf` | PDF, альбомный, текстовый | приёмка и выше | 1 страница | объём и допуск масла, антифриз и масло в коробке по машинам |
| 5 | `team/the-call-in-eight-moves.pptx` | PowerPoint | приёмка и выше | 10 слайдов | «три фразы, которые я не говорю» (слайд 9), ответ на сомнение в цене (слайд 8) |

---

## 1. `prices/counter-price-sheet.pdf`

*Лист, приклеенный у каждого компьютера на приёмке. Две страницы. Страница 1 и страница 2 должны быть разными страницами PDF: проверочные вопросы опираются на номер страницы.*

### Страница 1

**«Ермак-Сервис» · Прайс для стойки**
Действует с {D('@price_rise')} · Нормо-час {rate()} · Цены с НДС 5 %

Фиксированные цены и частые работы, легковой автомобиль:

| Работа | Цена |
|---|---:|
{menurows}

Осмотр по чек-листу при любом ремонте — бесплатно.
Расходные материалы: 3 % от работ по нормо-часу, не больше {M(SUP_CAP)} на заказ-наряд. На фиксированные цены не начисляются.
Утилизация шин при покупке новых: {fee('new_tyres_fitted')} за комплект.
**Нет на этом листе — значит, это не цена. Смотрите прайс-лист или спросите старшего.**

### Страница 2

**По классам автомобилей** · запчасти стандарт · без расходных материалов

| Работа | Легковой | Кроссовер | Рамный внедорожник | Фургон, «Газель» |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}

Легковой: Granta, Solaris, Logan, Camry. Кроссовер: Duster, Creta, RAV4, Niva, Jolion. Рамный внедорожник: УАЗ Patriot, Land Cruiser Prado, Pajero, Hover. Фургон: ГАЗель, Соболь, Largus-фургон, Ducato, Transit.
Клиенты с договорным нормо-часом ({A('A1')}, {A('A2')}): цену берём из программы, а не с этого листа.
Напечатано {D('@price_rise')}. Лист с более ранней датой — выбросить.

---

## 2. `team/staff-handbook.docx`

*Документ Word, около девяти страниц, с настоящими стилями заголовков (Заголовок 1 — название, Заголовок 2 — каждый нумерованный раздел), чтобы вместе с каждым абзацем извлекался его раздел. Первую редакцию писал {S(1,'full')}, нынешнюю — {S(2,'full')}.*

# «Ермак-Сервис» · Правила внутреннего трудового распорядка

Редакция от {D('@golive+2w')}. Заменяет все прежние. Бумажный экземпляр лежит в папке в комнате отдыха каждого сервиса.

## 1. Общие положения

Первому своему работнику отец сказал две вещи: делай как себе и говори клиенту правду, даже если из-за неё потеряешь заказ. Правила с тех пор не изменились. Всё, что ниже, — подробности. {S(1,'full')} и {S(2,'full')}

## 2. Рабочее время и явка

Сервисы открыты каждый день с 9:00 до 20:00, кроме 1 и 2 января. Механики работают пять дней через два, с 9:00 до 18:00, с часовым перерывом; мастера-приёмщики — два через два, с 9:00 до 20:00; руководители, бухгалтерия и склад — пять будних дней. Ваш график стоит в Traciora и публикуется до полудня четверга на следующую неделю.

Приход отмечается, когда вы пришли в сервис, уход — когда уходите. Опоздание — это отметка больше чем через пять минут после начала смены.

Опоздания считаются за любые 30 дней:

- Три опоздания: разговор с руководителем. Без бумаг.
- Пять опозданий: письменное объяснение и замечание.
- Второе взыскание за полгода: выговор. После выговора следующий шаг — вопрос о том, работаете ли вы у нас.

Такой порядок — наш собственный: Трудовой кодекс очерёдности взысканий не задаёт.

Не выйти на смену и не предупредить — другое дело. Позвоните на приёмку до 8:30. Отсутствие без уважительной причины больше четырёх часов подряд — прогул. За прогул увольняют.

## 3. Оплата труда

Зарплата выплачивается два раза в месяц: аванс 25-го, расчёт 10-го. Как оплачивается ваша работа (сдельно, по часам или окладом), записано в трудовом договоре. Работа сверх графика — только по предварительному согласованию с тем, кто составляет график.

## 4. Отпуск

Ежегодный оплачиваемый отпуск — 28 календарных дней. За стаж в компании добавляем:

| Стаж в «Ермак-Сервисе» | Дополнительные дни |
|---|---|
| До 5 лет | Нет |
| От 5 лет | 3 |
| От 10 лет | 5 |

График отпусков на следующий год утверждается не позже чем за две недели до Нового года. Заявление — в Traciora, не позже чем за 14 дней. Одна из частей отпуска — не короче 14 дней. Одновременно в отпуске может быть не больше одного человека с приёмки и двух из цеха одного сервиса. В сезон шиномонтажа, с середины апреля до майских праздников и с середины октября до начала ноября, отпуска на шиномонтаже не даём.

## 5. Праздничные дни

В праздники сервисы работают. Закрыты мы 1 и 2 января. Смена, которая по графику выпала на праздничный день, оплачивается в двойном размере. Если хотите, вместо этого можно взять другой день отдыха — тогда смена оплачивается в одинарном размере.

## 6. Болезнь

Позвоните на приёмку до 8:30. Больничный оформляется в поликлинике в электронном виде; его номер сообщите в бухгалтерию в день открытия.

## 7. Внешний вид и спецодежда

Механикам выдаём два комплекта спецодежды в год и стираем её раз в неделю. В цехе — защитные очки. Обувь у каждого своя; на неё компенсируем {N(BOOTS,'компенсация на рабочую обувь, в год')} в год. Приёмка: фирменная рубашка, выдаём мы.

## 8. Инструмент

Ручной инструмент у механика свой. Сервис даёт подъёмники, сканеры, стенд сход-развала, станции для кондиционеров, динамометрические ключи и специальный инструмент. После первого года работы компенсируем {N(TOOLS,'компенсация на инструмент, в год')} в год на инструмент, по чекам. Инструмент сервиса возвращается на место.

## 9. Обучение

Курсы, на которые отправляем мы, оплачиваем мы, и время на них — рабочее. Работа со станцией для кондиционеров — только после обучения.

## 10. Автомобили и деньги клиентов

Машина клиента едет только на контрольную поездку и на перегон по территории. Только с открытым заказ-нарядом. Свою машину на посту ремонтируют с разрешения мастера цеха и тоже по наряду.

Сотрудник покупает запчасти по закупочной цене плюс 10 %. За работу на своей машине в нерабочее время не платит. Только на своей и только с разрешения мастера цеха.

Деньги принимают мастера-приёмщики и руководители, и больше никто. Никто не берёт денег за работу, которой нет в заказ-наряде. Никто не выносит со склада деталь, которой нет в заказ-наряде.

## 11. Телефоны

Личный телефон в цехе лежит в кармане, на приёмке — не на стойке. Фотографии для осмотра делаются рабочим телефоном.

## 12. Увольнение

О том, что уходите, предупредите письменно за две недели. Спецодежда, ключи и всё, что принадлежит сервису, сдаются в последний день. Неиспользованный отпуск оплачивается.

---

## 3. `parts/fleet-fluid-sheet.xlsx`

*Книга Excel, один лист «Жидкости», шапка закреплена, ведёт {S(9,'fi')}. Движок хранит файл и находит его по имени; на чтение отвечает, что текст не извлекается. В файле тринадцать строк, которые есть в PDF, и ещё две, добавленные после печати. Пометка для сборки, в сам файл не входит: все объёмы и допуски в этой таблице записаны по памяти и не сверены с данными производителей; каждую строку должен проверить специалист, прежде чем seed v1 будет зафиксирован. Привычка сервиса ставить в наряд на Solaris четыре литра совпадает с каталогом.*

{hd}
{fl}
{fx}

Ячейка A18: «Обновил {D('T-2mo')}. П. М. „Весту“ и „Джампер“ дозаполнить».

---

## 4. `parts/fleet-fluid-sheet.pdf`

*Одна альбомная страница, текстовый PDF, распечатан из таблицы {D('T-6mo')} и висит на постах. В нём первые тринадцать строк, двух последних нет.*

**Заправочные объёмы · склад «Ермак-Сервиса»** · напечатано {D('T-6mo')} · П. М.

{hd}
{fl}

Прежде чем лить — прочитай, что написано на крышке. В наряд — столько, сколько залил, с округлением вверх до полулитра. Масло для вариатора — не ATF.

---

## 5. `team/the-call-in-eight-moves.pptx`

*PowerPoint, десять слайдов, у каждого есть заголовок (извлекаются номер слайда и заголовок). Учебная презентация для новых мастеров-приёмщиков, её сделала {S(16,'full')}, {D('T-4mo')}, когда появилась оценка звонков. Заметки докладчика не извлекаются, поэтому ничего важного в них быть не должно.*

**Слайд 1 · Звонок в восемь шагов**
{S(16,'full')}, Инженерный. Для новых мастеров-приёмщиков.

**Слайд 2 · Две минуты**
Человек, который звонит нам впервые, решает минуты за две. У него наготове следующий номер. Половина тех, чей звонок мы пропустили, больше не позвонит.

**Слайд 3 · Восемь шагов**
1 Приветствие. 2 Имя и номер. 3 Что случилось. 4 Цена со следующим шагом. 5 Предложить время. 6 Попросить запись. 7 Итог. 8 Ответить на сомнение. Пятый и шестой весят больше всех.

**Слайд 4 · Здравствуйте**
«Ермак-Сервис, Светлана, здравствуйте». Сначала улыбнуться. Потом узнать имя и за первую минуту дважды назвать по нему.

**Слайд 5 · Выяснить**
Машина. Что с ней. На один вопрос больше, чем нужно. «Тормоза» без машины не оцениваем.

**Слайд 6 · Цена — это не конец разговора**
«Диагностика тормозов — {t('brake_inspection')}, и я могу принять вас в пятницу в девять». Цена, после которой ничего нет, — это «до свидания».

**Слайд 7 · Два времени — и молчать**
«Завтра к девяти или в пятницу к часу?» И замолчать. Потом: «Записала. Спросите меня». Потом проговорить всё с начала.

**Слайд 8 · Когда сомневаются в цене**
«А с чем вы сравниваете?» Потом — что входит в нашу сумму: запчасти по названиям, работа, 30 дней гарантии на работу и гарантия производителя на деталь. Дешевле — значит запчасть дешевле, и сказано это вслух. Тихих скидок не бывает.

**Слайд 9 · Три фразы, которые я не говорю**
1. «Без проблем».
2. «Должно быть готово».
3. «У нас на всё гарантия».
Первая звучит так, будто проблема была. Вторая — обещание, которое я не могу сдержать. Третья ни на что не отвечает.

**Слайд 10 · Слушать**
Попросите у {P(4,'Сергея Анатольевича')} пять моих звонков. Запишите, что я делаю после того, как назвала цену. Потом дайте мне послушать пять ваших.
"""
os.makedirs(kbb.OUT + '/ru', exist_ok=True)
open(kbb.OUT + '/ru/_binaries.md', 'w').write(doc)
BIN_AMOUNTS = sorted(set(kbr.AMOUNTS)); BIN_NEW = list(kbr.NEW_AMOUNTS)
del kbr.AMOUNTS[:], kbr.NEW_AMOUNTS[:]
for k in USED: USED[k] = []

def binfact(path, title, purpose_note, fmt_, diff, new, verify, rev, only_here, facts=()):
    en = json.load(open(kbb.OUT + '/facts/' + path + '.json'))
    sheet = {'path': path, 'title': title, 'title_en': en['title'], 'exists_in': 'both', 'english_sheet': 'facts/' + path + '.json', 'kind': 'binary', 'format': fmt_,
             'visibility': en['visibility'], 'seen_from': en['seen_from'], 'voice_of_slot': en['voice_of_slot'], 'purpose': en['purpose'], 'serves': en['serves'],
             'draft': 'ru/_binaries.md', 'russian_form': purpose_note, 'facts': list(facts), 'facts_only_in_this_file': only_here,
             'differs_from_en': diff, 'new_facts': new, 'to_verify': settle(path, verify)[0], 'settled': settle(path, verify)[1], 'revisions': rev, 'has_history': len(rev) > 1}
    fp = kbb.OUT + '/facts-ru/' + path + '.json'; os.makedirs(os.path.dirname(fp), exist_ok=True)
    json.dump(sheet, open(fp, 'w'), ensure_ascii=False, indent=1)
    reg = json.load(open(REG))
    reg[path] = {'title': title, 'title_en': en['title'], 'exists_in': 'both', 'visibility': en['visibility'], 'voice_of_slot': en['voice_of_slot'], 'purpose': en['purpose'],
                 'serves': en['serves'], 'length_class': 'binary: ' + fmt_, 'links_to': [], 'has_history': len(rev) > 1, 'stale_on_purpose': None,
                 'broken_links_on_purpose': [], 'amounts': [], 'n_new': len(new), 'n_verify': len(verify), 'n_rev': len(rev), 'first_revision_text': None}
    json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=1)

IMP = {'n': 1, 'kind': 'import', 'author': 'operator (History shows "Administrator")', 'text_date': '{{@golive|date}}', 'what': 'the file as it stood on the shared drive', 'message_ru': 'Импортировано из файлов компании'}
binfact('prices/counter-price-sheet.pdf', 'Прайс для стойки', 'the printed price sheet, A4, two pages', 'PDF, 2 pages, text',
 ['Page 1: nineteen fixed-price and common jobs at the current list (class car), the hour at 1 900, prices with VAT at 5 % inside, shop supplies 3 % up to 500 RUB, tyre disposal 400 RUB a set.',
  'Page 2: sixteen jobs priced for car, crossover, body-on-frame and van with the Russian multipliers (hours 1 / 1.15 / 1.3 / 1.3 on heavy jobs; parts 1 / 1.35 / 1.7 / 1.3). It adds the two seasonal tyre jobs, the timing belt and the clutch to the English list.',
  'Spark plugs by class are the catalogue\'s own totals (four plugs with the class multipliers); the English sheet counts 6 and 8 plugs.',
  'No battery-test-is-free line: the test costs 300 RUB.'],
 ['The page-2 rows chosen for the Russian sheet.'], [],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '2', 'text_date': '{{@price_rise|date}}', 'what': 'the sheet reprinted at the new prices and uploaded over the old file', 'message_ru': 'Новые цены с сегодняшнего дня.'}],
 ['every crossover, body-on-frame and van price (the Markdown pages give multipliers and one worked example only)'],
 facts=[{'by_class_table': classfacts}])
binfact('team/staff-handbook.docx', 'Правила внутреннего трудового распорядка', 'the Russian counterpart of the staff handbook: internal labour regulations, twelve numbered sections', 'DOCX with heading styles, about 9 pages',
 ['The document is «Правила внутреннего трудового распорядка», which a Russian employer keeps by law, not a handbook: leave is 28 calendar days for everyone with extra days for length of service (English: 0 / 5 / 10 / 15 / 20 days); pay twice a month on the 25th and the 10th (English: every second Friday); sick leave by an electronic certificate (English: three paid sick days); discipline in the Labour Code\'s steps (замечание, выговор, увольнение; прогул is an absence of more than four hours in a row). The order замечание then выговор is stated as the company\'s own ladder (ТК ст. 192 sets no order); the leave schedule is approved no later than two weeks before the new year (ТК ст. 123) (ledger kb.handbook).',
  'Section numbers are kept so that the eval questions map: section 2 attendance and the lateness ladder (three in 30 days a talk, five a written explanation and a замечание, a second penalty in six months a выговор); section 4 leave; section 5 public holidays (the shops work; a holiday shift is paid double, or at the employee\'s wish single with another day off); section 10 customers\' cars and money.',
  'Section 10 has the sentence added after S2 and one more for the Russian leak: nobody takes a part from the stockroom that is not on an order.',
  'Allowances in roubles: 3 000 a year for footwear, 12 000 a year for tools after the first year; staff parts at purchase price plus 10 %.',
  'The founder\'s two things to his first worker: «делай как себе и говори клиенту правду».',
  'Seen from junior: technicians and the website assistant cannot read it; the paper folder is their copy.'],
 ['Every number is a new fact: the ladder (3, 5, a second penalty in six months), extra leave of 3 days from five years and 5 from ten, notice of 14 days for leave, one from a desk and two from a floor off at a time, 3 000 RUB for footwear, 12 000 RUB for tools, purchase price plus 10 %. The ladder is set so that slot F2 (late four shifts in ten, two written warnings, five absences) is clearly over it and slot 15 (late three in ten, never warned) is over it too.',
  'Leave of slot 10 (two weeks) and slot 16 (a week) fits 28 calendar days.'],
 ['Labour Code facts stated as the document would state them and not in the research: 28 calendar days of annual leave; one part of the leave not shorter than 14 days; the leave schedule drawn up in December; pay at least twice a month; a holiday shift paid double or compensated by a day off; прогул as an absence of more than four hours in a row and dismissal for it; two weeks\' written notice; the order замечание then выговор. To be read by someone who keeps personnel records before the document is used.'],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '2', 'text_date': '{{@golive+2w|date}}', 'what': 'the edition the text is dated by, uploaded over the old file two weeks after go-live: the schedule and leave requests are in Traciora; section 10 gained the two sentences on money and parts not on an order', 'message_ru': 'Новая редакция: график и заявления теперь в Traciora, в раздел 10 добавлены две строки.'}],
 ['the leave rule and the extra days', 'holiday work', 'the lateness ladder', 'allowances', 'staff parts price', 'notice'])
binfact('parts/fleet-fluid-sheet.xlsx', 'Заправочные объёмы (таблица)', 'the parts manager\'s working sheet, in litres, for the Russian fleets\' models', 'XLSX, one sheet',
 ['Fifteen rows: the thirteen of the PDF plus LADA Vesta (the driving school\'s cars 4 and 7) and Citroën Jumper (the caterer\'s van 8), both unfinished.',
  'Models are those of accounts.json ru: ГАЗель Next, NN and Бизнес, Largus, Granta, Niva Legend, УАЗ, Ford Transit, Solaris and Rio, Logan, Duster.',
  'Not extracted by the engine: found by name, cannot be read.'],
 ['ALL QUANTITIES AND SPECIFICATIONS ARE RECALLED, NOT VERIFIED, as in the English draft: every row is to be checked against the makers\' data.'],
 ['Every oil quantity, oil grade, coolant type and gearbox oil in the table.'],
 [IMP, {'n': 2, 'kind': 'new_version', 'author_slot': '4', 'text_date': '{{T-2mo|date}}', 'what': 'the parts manager\'s updated file with the two new rows (uploaded by slot 4; juniors cannot publish)', 'message_ru': 'Таблица Паши, две новые машины.'}],
 ['the rows for LADA Vesta and Citroën Jumper'])
binfact('parts/fleet-fluid-sheet.pdf', 'Заправочные объёмы (распечатка)', 'a one-page print of the sheet: the readable copy', 'PDF, 1 page landscape, text',
 ['Thirteen rows: vehicle, engine, oil, litres with filter, coolant, gearbox, where seen. Printed six months before T; two rows behind the spreadsheet.',
  'The ГАЗель Next with the Cummins diesel takes 6,0 litres of 10W-40 CI-4 (the catalogue\'s fleet PM bills six litres): the Russian twin of C3.4.',
  'The Ford Transit takes an oil with a Ford approval that is not stocked: agrees with the account page (Transits: fluids, filters, brakes and tyres only).'],
 ['All thirteen rows are recalled, not verified.'], ['Every quantity and specification.'], [IMP],
 ['every quantity and specification'],
 facts=[{'rows': [dict(zip(['vehicle', 'engine', 'oil', 'litres_with_filter', 'coolant', 'gearbox', 'seen_in'], r)) for r in FLUID]}])
binfact('team/the-call-in-eight-moves.pptx', 'Звонок в восемь шагов', 'the lead advisor\'s ten-slide training deck', 'PPTX, 10 titled slides',
 ['Ten slides in slot 16\'s Russian voice. Slide 9, the three sentences: «Без проблем», «Должно быть готово», «У нас на всё гарантия».',
  'Slide 6 uses the Russian brake-inspection price (700 RUB); slide 8 names the Russian warranty (30 days on the work, the maker\'s on the part).',
  'Agrees with how-to/taking-a-call.md and how-to/price-objections.md.'],
 [], [],
 [{'n': 1, 'kind': 'edit', 'author_slot': '4', 'text_date': '{{T-4mo|date}}', 'what': 'file uploaded for slot 16 (binary uploads are edits: published by slot 4)', 'message_ru': 'Учебная презентация Светы.'}],
 ['the three sentences of slide 9'])
reg = json.load(open(REG))
reg['_binaries.md'] = {'amounts': BIN_AMOUNTS, 'new_amounts': BIN_NEW, 'not_a_page': True}
json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=1)
print('ok')
