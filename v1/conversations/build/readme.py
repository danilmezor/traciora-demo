#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes conversations/en/README.md and conversations/ru/README.md: the fixed text below, and the table and the
list of new facts read from the JSON files, so the two cannot drift from the files. Also refreshes the samples."""
import glob
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, ".."))
SAMPLES = {1: "{l}-1-web-after-hours.json", 4: "{l}-2-fleet-quote-waited.json", 6: "{l}-3-west-nine-days.json",
           7: "{l}-4a-stocktake-web.json", 8: "{l}-4b-stocktake-messenger.json"}
CHANNEL = {"en": {"chat": "web chat", "telegram": "Telegram"}, "ru": {"chat": "чат на сайте", "telegram": "Telegram", "vk": "ВКонтакте", "avito": "Авито"}}

EN_HEAD = """# Story conversations, English configuration (Brennan Auto Care)

The 27 hand-written conversations of `../DESIGN.md` section 6, one JSON file each, format `seed-conversation/1` (section 7). These files are the source of record; `../samples/` holds copies of five of them. `../../checks/check_conversations.py en` checks all of it and its output is `../../checks/conversations_check_en.txt`.

Read first: **03** (the live-demo chat: a draft waits for the junior operator), **06** (the car that has waited nine days: three late replies, a note, 'handled') and **04** beside **05** (the fading account's quote that waited two days; the healthy account's weekly list answered in six minutes).

## The conversations

| # | File | Story | Channel | Staff (slot) | Begins | State at T | Shows |
|---|---|---|---|---|---|---|---|
{table}

## How a file reads

- `scenario`: who writes, what happens, the facts the lines rest on; `unclear` only where rule R13 applies (files 01, 25, 26, 27). `scenario.facts.prices` lists every amount a line says, with the catalogue job, vehicle class and price class it is computed from; `numbers` lists every other number of 20 or more.
- `days`: every day used, as an anchor of rule R6 (`rule` is the machine form) with the date it falls on for the nominal T. `floating_days`: every weekday word and 'today', 'tomorrow', 'yesterday' in the text, with the day it means.
- `conversations[].timeline`: `message` (customer, assistant, staff slot), `note` (private), `draft` with its `outcome`, `handoff` (the tool's arguments, the bot's private note, the board card), `activity`, `outside` (a call or an ERP event, for the reader). Activity lines marked `derived` are the ones the product writes by itself: assigned on the first reply, the handoff label taken off, reopened, and the priority lines of the wait.
- `state_at_t`, `reads_back`: what the Conversations screen and Stats must show. `truth`: the reason (the ledger's taxonomy), who handled it, the outcome, the facts an answer may rest on, the card questions it serves. `new_facts`: what the file invented.

## Conventions the seeder should know

- **Priority lines are derived with designed thresholds**: a chat nobody has answered turns High after 12 working minutes and Urgent after 36; a later message after 24 and 72. The product computes its own from 28 days of replies; the seeder must recompute these lines and the shown level at T (DESIGN.md section 2).
- **Prices are today's list** (class car unless the file says otherwise; the company-account class for A2), with the labour hour after the last rise. Every dated chat is after P. Parts are not drifted back in time, as in the story calls (`../../PENDING.md`).
- **Waits** are in working minutes on the shop's own clock (07:30 to 17:30 weekdays; East Main also Saturday 08:00 to 13:00); the Charlotte Pike chats are on Central time. A wait starts at the hand-off or at the first unanswered customer line.
- **A drafts chat never ends with a draft in the box** unless it is open at T: the last draft is sent, edited, written over or cleared before the chat is resolved, because what Chatwoot's auto-resolve does to a waiting draft was not read in the product.
- **Invented customers' phone numbers are tier B** of `../../phones.md` (NPA-555-0200 and up), so they cannot collide with the tier-A numbers the story calls gave their own invented callers.

## Where a file could not be made to agree, and what was done

{disagree}

## New facts other stores must carry

{facts}

## How the files were made

`../build/` holds the sources (`src_en_a.py`, `src_en_b.py`), the library that derives numbering, activity lines, outcomes, waits and the state at T (`convlib.py`), and `build.py`. A JSON file edited by hand is not read back by the builder; the checker reads only the JSON.
"""

EN_DISAGREE = """- **File 07, the day.** DESIGN.md section 6 puts S13's web question on the 2nd full open day before T; card S13 puts it on the Monday of week W0 when that is before T. The card is followed. The card's footprint calls the chat resolved; the ledger (`conv.open_at_t`) names it as pending, and it is pending: fewer than seven silent days have passed.
- **File 01, 'in the morning'.** Card S07 has the assistant tell her someone will confirm a time in the morning. The product's sentence for a hand-off names no time (`escalation.said.handover`), so the assistant says the shops open at 7:30 and that somebody will get back to her as soon as possible.
- **File 06, the hours of the calls.** `calls/en` was not read (another agent's). The missed call is shown at 09:20, call 16 at 14:10 and message 4 after it at 16:48; call 8 in file 01 is shown at 13:40. The calls set decides the hours; if call 16 is later than 16:48, message 4 moves after it.
- **File 06, the first date.** With the card's days (7, 5, 3, 1) the first chat message is on the Friday, so the 'Friday' of call 15 ('Fella told me Friday') cannot have been given in the chat: it was given when the part was ordered, the day after the car came in.
- **File 04, the vehicles.** Call 22's vehicles were not read. The quote here is for SC-4 and SC-9, chosen to differ from the old sample's SC-6, SC-8 and SC-10.
- **File 08.** Both times Angie offers are inside the week she has asked off (S5). Her two shifts there are published and the request is undecided, so the line stands as in the sample; if the request is ever approved in the seed, the appointment needs another advisor."""

RU_HEAD = """# Сюжетные переписки, русская конфигурация («Ермак-Сервис»)

27 написанных вручную переписок из раздела 6 `../DESIGN.md`, по одному JSON-файлу на переписку, формат `seed-conversation/1` (раздел 7). Эти файлы — первоисточник; в `../samples/` лежат копии пяти из них. Всё проверяет `../../checks/check_conversations.py ru`, вывод — в `../../checks/conversations_check_ru.txt`.

Русские переписки написаны с карточек историй и с описаний людей в `cast.json`, а не с английского набора: другие клиенты, машины, работы и поводы. Реплики клиентов, приёмщиков, ассистента, заметки и поле `why` — по-русски; служебные поля (`demonstrates`, `truth`, якоря дней) — по-английски, как в образцах.

## С чего начать читать

1. **06, Казань, девятый день.** Клиент пишет четыре раза, Вячеслав отвечает под закрытие и четырнадцатью словами на три ответа, Камила пишет руководителю заметку, руководитель отвечает «принял». Здесь же голосовое, которое ассистент не может прослушать, и график два через два: первое сообщение приходит вечером чужой смены.
2. **05, «Тёплый контур», заявка на понедельник.** Диспетчер и Светлана, четыре недели из одной переписки в Telegram. Вторая сессия — история S5 в двух репликах: Артём обещал перезвонить и пропал, Светлана за полчаса согласовала помпу.
3. **27, Авито, «сколько стоит стойки поменять».** Непонятный клиент (правило R13) и приёмщик, который вместо вопроса дважды называет цену. Рядом стоит прочитать **26**: тот же случай у Татьяны Геннадьевны, два вопроса — и всё ясно.

Для живого показа — **03**: чат на сайте, открыт, принадлежит Алине, в поле ответа ждёт черновик ассистента.

На что смотреть как носителю языка: пишут ли клиенты так, как пишут в мессенджер в 2026 году («созрела на задние амортизаторы)», «дороговато чет», «ау», «??»); отличаются ли приёмщики друг от друга без подписей (Дмитрий: «наберите меня, так быстрее»; Никита: «Да-да», «должны успеть»; Артём: «Понял, принял»; Вячеслав: «4560. час»; Камила: «давайте сделаем так»; Светлана: имя дважды и «я бы на своей машине»; Татьяна Геннадьевна: полные предложения и ни одного смайлика); читается ли ассистент как вежливая машина, а не как перевод.

## Переписки

Даты в таблице — для номинального T (пт, 13.11.2026, 10:30 по Ульяновску); якорь каждого дня по правилу R6 записан в поле `days` файла.

| № | Файл | История | Канал | Сотрудники (слот) | Начало | Состояние в момент T | Что показывает |
|---|---|---|---|---|---|---|---|
{table}

## Как читать файл

- `scenario`: кто пишет, что происходит, факты, на которых держатся реплики; `unclear` — только там, где действует правило R13 (файлы 01, 25, 26, 27). В `scenario.facts.prices` — каждая сумма из реплик с работой каталога, классом машины и видом цены, из которых она посчитана; в `numbers` — остальные числа от 20.
- `days`: каждый день переписки как якорь правила R6 (`rule` — машинная запись) и дата, на которую он приходится при номинальном T. `floating_days`: каждое «в среду», «завтра», «сегодня», «вчера» из текста и день, который оно означает.
- `conversations[].timeline`: `message` (клиент, ассистент, сотрудник), `note` (заметка для своих), `draft` с исходом в `outcome`, `handoff` (аргументы инструмента, заметка бота, карточка на доске), `activity`, `outside` (звонок или событие в учётной системе, для читателя). Строки `activity` с пометкой `derived` продукт пишет сам: назначение при первом ответе, снятие ярлыка handoff, повторное открытие, смена приоритета из-за ожидания.
- `state_at_t`, `reads_back`: что должны показать экран переписок и статистика. `truth`: причина обращения (таксономия леджера), кто вёл, чем закончилось, факты для эталонного ответа. `new_facts`: что файл придумал.

## Что нужно знать сборщику

- **График два через два соблюдён в каждой реплике сотрудника** (`roster.advisor_pattern`): слоты 5, 7, 16, 23 — фаза A, слоты 6, 29, 17, 24 — фаза B, руководитель — по будням. Якорь «вторник недели T-k» для переписки приёмщика читается как «его первый рабочий день начиная с этого вторника», как в звонках.
- **Строки приоритета выведены по придуманным порогам**: неотвеченный чат становится «Высоким» через 12 рабочих минут и «Срочным» через 36; следующее сообщение — через 24 и 72. Продукт считает пороги сам по 28 дням ответов; сборщик должен пересчитать эти строки и уровень на момент T (раздел 2 DESIGN.md).
- **Цены — сегодняшний прайс** (класс car, если в файле не сказано иное; договорные для A2), нормо-час после последнего повышения. Все переписки с ценами — после даты P. Запчасти с даты запуска стоят как сегодня, как и в сюжетных звонках.
- **Каждая сумма — сумма к оплате, НДС внутри** (`tax.ru_price_basis`): сверху ничего не добавляется ни частному клиенту, ни клиенту по договору. Итог счёта — это работы и запчасти по прайсу плюс расходные материалы; где в реплике назван налог, там сказано «НДС в том числе». В `scenario.facts.prices` у всех сумм `with_tax: false`: это значит «сверху ничего не добавлено», а не «без НДС».
- **Ожидание** считается в рабочих минутах по часам своего сервиса (9:00–20:00, без выходных); чаты Технической — по казанскому времени. Отсчёт идёт от передачи заявки или от первой неотвеченной реплики клиента.
- **В закрытом чате черновик в поле ответа не остаётся**: последний черновик отправлен, исправлен, заменён своим текстом или убран до закрытия. Что делает с ждущим черновиком автозакрытие Chatwoot, в продукте не читалось.
- **Авито передаёт только картинки**; ни в одной из пяти переписок на Авито сотрудник файл не отправляет.

## Где файл не удалось согласовать с карточкой, и что сделано

{disagree}

## Новые факты, которые должны появиться в других хранилищах

{facts}

## Как сделаны файлы

В `../build/` лежат исходники (`src_ru_a.py`, `src_ru_b.py`), библиотека, которая выводит нумерацию, строки активности, исходы черновиков, ожидания и состояние на момент T (`convlib.py`), и `build.py`. JSON, исправленный руками, сборщик обратно не читает; проверка читает только JSON.
"""

RU_DISAGREE = """- **Файл 06 и график.** По карточке S06 сообщения приходятся на 7, 5, 3 и 1 день до T, а чат принадлежит слоту 23. По графику Вячеслав выходной за 7, 4 и 3 дня до T. Поэтому первое сообщение приходит за 7 дней в 20:41, после закрытия (смена Камилы уже кончилась), первым отвечает Вячеслав на следующий день, и чат становится его; на третье сообщение он отвечает наутро, выйдя на смену, а в день сообщения заметку руководителю пишет Камила. Звонок 15 карточка теперь ставит на третий рабочий день Вячеслава до T: это воскресенье, день второго сообщения. Клиент звонит в 16:10, не дождавшись ответа в чате; во вторник он пишет «вы в воскресенье по телефону сказали насос в понедельник придёт, во вторник заберу», а Камила в заметке: «Слава в воскресенье по телефону пообещал ему вторник».
- **Файл 06, первый срок.** При днях карточки «субботу» из звонка 15 («Мне сначала сказали — в субботу») нельзя было назвать в чате: её назвали при заказе насоса, на следующий день после приёма машины.
- **Файл 06, часы звонков.** Пропущенный звонок в 10:05, звонок 16 в 15:25, четвёртое сообщение после него, в 17:22; звонок 15 в 16:10. Это часы `calls/ru` и карточки S06.
- **Файл 04 и график.** Карточка S01 ставит запрос на вечер перед первым днём рабочей пары слота 7, начиная со среды недели T-4: для номинального T это вторник, 20:41, после закрытия (вторник — смена слотов 6 и 29). Среда и четверг — смена 5 и 7; первая реплика человека — в четверг в 19:25, через 1,95 суток. В пятницу оба выходные, и черновик с ответом на пропущенный вопрос отправляет Алина.
- **Файл 04, машины.** Смета звонка 22 (неделя T-9) была на машины № 2 и № 5; смета этого чата — на № 7 и № 8. Это две из пяти «медленных» смет A6. Цены в обеих по прайсу: это то, что платит A6, НДС в том числе.
- **Файл 02 и график.** «Спасибо» приходит в выходной Алины. На него готовым черновиком отвечает Никита (его смена), а закрывает чат Алина в свой следующий рабочий день: раздел 6 требует «resolved by 6».
- **Файл 07, день.** Раздел 6 DESIGN.md ставит вопрос про инвентаризацию на второй открытый день до T, карточка S13 — на понедельник недели W0, если он раньше T. Сделано по карточке: чат ожидающий, семи дней тишины ещё не прошло.
- **Файл 01, «утром».** Формула продукта для передачи заявки срока не называет, поэтому ассистент говорит, что сервис откроется в 9:00 и что с ней свяжутся в ближайшее время; так теперь и в карточке S07. Звонок-подтверждение в 14:20, как в `calls/ru`.
- **Файл 08, машина и день.** В образце у постоянной клиентки Марины была Kia Rio 2017; такая же машина в `named_customers.json` записана на другую Марину того же сервиса на Инженерном (S15). Машина заменена на Volkswagen Polo 2017. В образце Светлана предлагала четверг и пятницу недели W+1, то есть дни внутри недели, на которую она просит отпуск (S5). Теперь она записывает клиентку на понедельник, свой последний рабочий день перед этой неделей, а вторым временем называет субботу у Артёма.
- **Файл 08 и список правок.** Список правок велел предложить «пятницу, примет Артём». Пятница недели W+1 по графику — день самой Светланы, Артём в четверг и пятницу выходной, а кто её подменит, не решено (S5). Поэтому вторым временем названа суббота, первая смена Артёма после инвентаризации.
- **Файл 09, сумма.** Раньше клиенту по телефону называли сумму «без НДС», а в счёте появлялся налог. Цены прайса уже с НДС, поэтому разница теперь в расходных материалах: 7 902 по прайсу и 8 019,99 к оплате."""


def table(cfg):
    rows, facts = [], []
    for p in sorted(glob.glob(os.path.join(OUT, cfg, "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        c = d["conversations"][0]
        st = c["state_at_t"]
        staff = ", ".join("%s (%d)" % (s["name"], s["slot"]) for s in d["cast"].get("staff", [])) or ("the assistant alone" if cfg == "en" else "только ассистент")
        day = d["days"][c["timeline"][0]["day"]]
        if cfg == "en":
            state = st["status"] + ("" if st["status"] == "resolved" and st["owner"] is None else ", %s" % ("slot %d" % st["owner"] if st["owner"] else "the assistant's"))
            if st["status"] == "resolved":
                last = c["reads_back"]["resolutions"][-1]["by"]
                state = "resolved by %s" % ("slot %d" % last if last else "7 silent days")
            if st["draft_in_box"]:
                state += ", **draft waiting**"
        else:
            if st["status"] == "resolved":
                last = c["reads_back"]["resolutions"][-1]["by"]
                state = "закрыт: %s" % ("слот %d" % last if last else "7 дней тишины")
            else:
                state = ("открыт" if st["status"] == "open" else "ожидает, у ассистента") + (", слот %d" % st["owner"] if st["owner"] else "")
            if st["draft_in_box"]:
                state += ", **ждёт черновик**"
        if cfg == "en":
            begins = "%s (%s)" % (day["anchor"].split(" (")[0], day["nominal"])
        else:
            wd, iso = day["nominal"].split(" ")
            y, m, dd = iso.split("-")
            begins = "%s, %s.%s.%s" % ({"Mon": "пн", "Tue": "вт", "Wed": "ср", "Thu": "чт", "Fri": "пт", "Sat": "сб", "Sun": "вс"}[wd], dd, m, y)
        rows.append("| %02d | `%s` | %s | %s | %s | %s | %s | %s |" % (d["number"], d["id"] + ".json", d["story"], CHANNEL[cfg][c["channel"]], staff, begins, state, d["title"]))
        for x in d["new_facts"]:
            facts.append("| %02d | %s |" % (d["number"], x.replace("|", "/")))
    head = "| File | New fact |\n|---|---|\n" if cfg == "en" else "| Файл | Новый факт |\n|---|---|\n"
    return "\n".join(rows), head + "\n".join(facts)


def main():
    for cfg, text, dis in (("en", EN_HEAD, EN_DISAGREE), ("ru", RU_HEAD, RU_DISAGREE)):
        t, f = table(cfg)
        with open(os.path.join(OUT, cfg, "README.md"), "w", encoding="utf-8") as fh:
            fh.write(text.replace("{table}", t).replace("{facts}", f).replace("{disagree}", dis))
        for n, pattern in SAMPLES.items():
            src = [p for p in glob.glob(os.path.join(OUT, cfg, "%02d-*.json" % n))][0]
            shutil.copyfile(src, os.path.join(OUT, "samples", pattern.format(l=cfg)))
        old = os.path.join(OUT, "samples", "%s-4-stocktake-two-modes.json" % cfg)
        if os.path.exists(old):
            os.remove(old)
    print("readmes and samples written")


if __name__ == "__main__":
    main()
