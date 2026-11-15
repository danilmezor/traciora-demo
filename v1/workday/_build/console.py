# Feedback reports, alerts, and the two operators' Inbox at T.
from cards import L

# ---------------------------------------------------------------- nine feedback reports (platform.feedback_report)
# (id, slot, category, severity, status, sent at, status set at, screen, text)
FEEDBACK = [
    ("FB1", 3, "praise", "suggestion", "resolved", "W-12.wed@o+3:10", "W-12.thu@o+2:00", "home", L(
        "I can see who corrected a clock-out and when without calling the shop. Payroll hours took me half the "
        "time this period. Thank you.",
        "Вижу, кто и когда исправил отметку об уходе, не обзванивая площадки. Табель за этот период закрыла "
        "вдвое быстрее. Спасибо.")),
    ("FB2", 15, "notifications", "annoying", "seen", "W-7.wed@o+0:20", "W-7.thu@o+2:00", "inbox", L(
        "When the new week comes out my phone goes off five times, once for every day. One buzz with the whole "
        "week would do me fine!",
        "Когда выходит график на неделю, телефон жужжит пять раз подряд — по разу на каждый день. Мне бы одно "
        "сообщение на всю неделю, и хватит!")),
    ("FB3", 14, "bug", "blocks_work", "resolved", "W-2.wed@o+0:12", "W-2.fri@o+3:00", "home", L(
        "it wont let me fix yesterdays clock out. the question was there this morning then it was gone after i clocked in",
        "не даёт исправить вчерашний уход. утром вопрос был а как отметился на смену пропал(")),
    ("FB4", 5, "slow", "annoying", "resolved", "W-15.thu>=p5@o+4:30", "W-13.mon@o+2:00", "conversations", L(
        "Opening a chat with photos in it takes forever on the counter computer. Customer is standing there and "
        "I'm watching it spin.",
        "чат с фотками на компе у стойки открывается по минуте. клиент стоит ждёт а у меня колесо крутится")),
    ("FB5", 6, "wrong_answer", "annoying", "seen", "W-6.tue>=p6@o+2:40", "W-5.mon@o+2:00", "ask", L(
        "Asked what front pads and rotors cost and it gave me {ledger:s12.brake_price.stale} from the old brake "
        "page. The price list says {ledger:s12.brake_price.now}. It should know which page is the price list.",
        "Спросила, сколько стоят передние колодки с дисками, — ответил {ledger:s12.brake_price.stale} со старой "
        "страницы про тормоза. В прайсе {ledger:s12.brake_price.now}. Он должен понимать, какая страница — прайс.")),
    ("FB6", 22, "confusing", "annoying", "wont_fix", "W-10.sun@20:55", "W-9.wed@o+2:00", "planner", L(
        "Planner says 3 unpublished and I can't tell which 3. Let me print the week like I used to.",
        "В графике написано: 3 не опубликовано. Какие три — не видно. Дайте распечатать неделю, как раньше.")),
    ("FB7", 16, "missing_feature", "suggestion", "open", "W-4.mon>=p16@o+1:30", None, "calendar", L(
        "I would like to put the customer on a calendar entry. The Millsaps vans come every Monday at opening "
        "and all I can do is type their name in the title.",
        "Хотелось бы добавлять клиента в запись календаря. Машины «Тёплого контура» приезжают каждый понедельник "
        "к открытию, а я могу только вписать название в заголовок.")),
    ("FB8", 24, "notifications", "annoying", "open", "W-1.tue>=p24@o+5:00", None, "conversations", L(
        "A new chat alerts all of us at once, and twice this week two of us answered the same customer. Could it "
        "go to whoever is on the desk first?",
        "Уведомление о новом чате приходит сразу всем, и на этой неделе дважды одному клиенту ответили двое. "
        "Можно, чтобы сначала оно шло тому, кто сейчас на приёмке?")),
    ("FB9", 4, "missing_feature", "annoying", "open", L("east-2@c-1:00", "east-2<=p20@c-1:00"), None, "planner", L(
        "A no-show gets flagged and I can't find where. I learned Austin was out from the counter at 8:15, not "
        "from the app. Put it in my Inbox.",
        "Неявка отмечается, а где это увидеть — не нашёл. Что Блинов не вышел, узнал от приёмки в 9:40, а не из "
        "программы. Нужно, чтобы это приходило во входящие.")),
]
FEEDBACK_NOTES = {
    "s10": "FB1, FB2 and FB3 are card S10's three: the Wednesdays of weeks T-12, T-7 and T-2",
    "status_by": "slot 2, as the tenant's admin (operations.set_feedback_status); the report itself is written as its reporter",
    "device": {"FB2": "phone", "FB3": "phone", "FB6": "phone", "FB9": "phone", "others": "desktop"},
}

# ---------------------------------------------------------------- alerts (platform.alert, category operations)
# The words are the product's own: alert.<rule>.summary of config/locales/{en,ru}.json filled with params.
SUMMARY = {
    "en": {
        "backup_missing": "No backup of the {database} database in the last 36 hours",
        "job_failed": "Job {job} failed ({error})",
        "job_silent": "Job {job} has not finished a run for {hours} h",
        "heartbeat_stale": "{component} has not reported for {minutes} min",
        "scheduler_away": "The scheduler is not running (last seen {last_seen})",
        "disk_low": "Disk space is low: {percent}% free ({free_gb} GB)",
        "provider_errors": "The model provider refused {errors} of {calls} calls in 15 min",
        "tool_slowdown": "{tool} is slow: p95 {now} s today, usually {usual} s",
        "cards_waiting": "A card has waited {hours} h for an answer ({tool})",
        "client_error_spike": "The app is failing in browsers: {errors} errors today, {rate} per 100 sessions (usually {usual})",
        "rollup_failed": "The nightly long-range rollup failed twice running ({error})",
        "knowledge_sync_failed": "The knowledge base did not get the ranks",
        "telemetry_dropping": "Telemetry is being dropped: {count} {exporter} items in the last 15 min",
        "push_silent_subscriptions": "Phone notifications are not arriving: {silent} of {accepted} phones never received one",
        "channel_quiet": "{channel} has been quiet for {hours} h: about {expected} messages usually arrive in that time",
        "channel_handler_errors": "{channel} messages fail after they arrive ({count} in the last 15 min)",
    },
    "ru": {
        "backup_missing": "Нет резервной копии базы {database} за последние 36 часов",
        "job_failed": "Задача {job} завершилась с ошибкой ({error})",
        "job_silent": "У задачи {job} нет завершённых запусков уже {hours} ч",
        "heartbeat_stale": "{component} не выходит на связь {minutes} мин",
        "scheduler_away": "Планировщик не работает (последний сигнал {last_seen})",
        "disk_low": "Мало места на диске: свободно {percent}% ({free_gb} ГБ)",
        "provider_errors": "Поставщик модели отказал в {errors} из {calls} вызовов за 15 мин",
        "tool_slowdown": "{tool} работает медленно: p95 {now} с сегодня, обычно {usual} с",
        "cards_waiting": "Карточка ждёт ответа {hours} ч ({tool})",
        "client_error_spike": "Приложение даёт сбои в браузерах: {errors} ошибок сегодня, {rate} на 100 сеансов (обычно {usual})",
        "rollup_failed": "Ночная сводка для долгих графиков не удалась два раза подряд ({error})",
        "knowledge_sync_failed": "База знаний не получила ранги",
        "telemetry_dropping": "Телеметрия теряется: {count} записей {exporter} за 15 мин",
        "push_silent_subscriptions": "Уведомления на телефоны не доходят: из {accepted} телефонов {silent} не получили ни одного",
        "channel_quiet": "{channel} молчит {hours} ч: обычно за это время приходит около {expected} сообщений",
        "channel_handler_errors": "Сообщения {channel} падают после получения ({count} за последние 15 мин)",
    },
}

# (id, rule, subject, severity, params, opened, status at T, closed, acknowledged (by slot, at) or None, markets)
ALERTS = [
    ("AL01", "backup_missing", "chatwoot", "critical", dict(database="chatwoot"), "G>+2d@03:40", "resolved", "G>+3d@03:20", None, "both"),
    ("AL02", "job_failed", "phonecalls_transcribe", "error", dict(job="phonecalls_transcribe", error="TimeoutError"), "W-23.tue@02:20", "resolved", "W-23.tue@03:20", None, "both"),
    ("AL03", "disk_low", "runtime", "warning", dict(percent=9, free_gb=21), "W-21.wed@14:10", "resolved", "W-21.fri@09:30", (2, "W-21.wed@15:00"), "both"),
    ("AL04", "heartbeat_stale", "worker-phonecalls", "error", dict(component="worker-phonecalls", minutes=12), "W-20.mon@06:12", "resolved", "W-20.mon@06:31", None, "both"),
    ("AL05", "scheduler_away", "scheduler", "error", dict(last_seen="06:01"), "W-20.mon@06:13", "resolved", "W-20.mon@06:30", None, "both"),
    ("AL06", "job_silent", "metric_rollup", "error", dict(job="metric_rollup", hours=27), "W-20.tue@07:15", "resolved", "W-20.tue@09:40", (2, "W-20.tue@09:10"), "both"),
    ("AL07", "provider_errors", "provider", "error", dict(errors=14, calls=96), "W-18.thu@10:42", "resolved", "W-18.thu@11:20", None, "both"),
    ("AL08", "tool_slowdown", "plan_shifts", "warning", dict(tool="plan_shifts", now="9.4", usual="3.8"), "W-17.tue@09:00", "resolved", "W-17.wed@09:00", None, "both"),
    ("AL09", "cards_waiting", "create_task", "warning", dict(hours=5, tool="create_task"), "W-16.wed@15:30", "resolved", "W-16.wed@17:05", None, "both"),
    ("AL10", "client_error_spike", "app", "warning", dict(errors=9, rate="6.4", usual="1.2"), "W-15.mon@11:00", "resolved", "W-15.tue@11:00", None, "both"),
    ("AL11", "knowledge_sync_failed", "ranks", "warning", {}, "W-14.mon@09:20", "resolved", "W-14.mon@10:05", None, "both"),
    ("AL12", "job_failed", "memory.dream", "error", dict(job="memory.dream", error="ValueError"), "W-14.thu@03:10", "resolved", "W-14.fri@03:08", None, "both"),
    ("AL13", "rollup_failed", "metric_rollup", "error", dict(error="OperationalError"), "W-13.wed@04:12", "resolved", "W-13.thu@04:11", (2, "W-13.wed@08:50"), "both"),
    ("AL14", "cards_waiting", "schedule_meeting", "warning", dict(hours=6, tool="schedule_meeting"), "W-11.fri@16:10", "resolved", "W-10.mon@08:05", None, "both"),
    ("AL15", "provider_errors", "provider", "error", dict(errors=11, calls=80), "W-9.tue@13:05", "resolved", "W-9.tue@13:40", None, "both"),
    ("AL16", "telemetry_dropping", "logs", "warning", dict(count=340, exporter="logs"), "W-8.wed@22:15", "resolved", "W-8.wed@22:45", None, "both"),
    ("AL17", "job_failed", "attachments_sweep", "error", dict(job="attachments_sweep", error="OSError"), "W-7.sun@04:00", "resolved", "W-7.sun@05:00", None, "en"),
    ("AL17", "channel_handler_errors", "avito", "error", dict(channel="Avito", count=4), "W-7.sun@12:40", "resolved", "W-7.sun@13:15", None, "ru"),
    ("AL18", "tool_slowdown", "show_board", "warning", dict(tool="show_board", now="4.1", usual="1.6"), "W-6.thu@09:00", "resolved", "W-6.fri@09:00", None, "en"),
    ("AL18", "channel_quiet", "vk", "error", dict(channel="VK", hours=6, expected=9), "W-6.thu@15:00", "resolved", "W-6.thu@16:10", (2, "W-6.thu@15:20"), "ru"),
    ("AL19", "disk_low", "runtime", "warning", dict(percent=8, free_gb=19), "W-5.tue@08:30", "resolved", "W-5.wed@10:00", None, "both"),
    ("AL20", "heartbeat_stale", "worker-scheduler", "error", dict(component="worker-scheduler", minutes=9), "W-4.sat@02:05", "dismissed", "W-4.sat@09:15", None, "both"),
    ("AL21", "cards_waiting", "add_shift", "warning", dict(hours=4, tool="add_shift"), "W-3.thu@19:30", "resolved", "W-3.fri@07:40", None, "both"),
    ("AL22", "job_failed", "context_sync", "error", dict(job="context_sync", error="OperationalError"),
     L("W-1.mon@07:56", "W-1.mon@08:55"), "resolved", L("W-1.mon@08:48", "W-1.mon@09:48"),
     (2, L("W-1.mon@08:18", "W-1.mon@09:18")), "both"),
    ("AL23", "client_error_spike", "app", "warning", dict(errors=7, rate="5.1", usual="1.3"), "W-1.wed@12:00", "resolved", "W-1.thu@12:00", None, "both"),
    ("AL24", "provider_errors", "provider", "error", dict(errors=12, calls=88), "W0.tue@15:40", "resolved", "W0.tue@16:15", None, "both"),
    ("AL25", "push_silent_subscriptions", "phones", "warning", dict(silent=1, accepted=3), "W-1.thu@09:05", "open", None, None, "both"),
]
ALERT_NOTES = {
    "AL22": "card S10: the shop-system source could not be reached from 8 minutes before to 40 minutes after slot 2's "
            "Monday report. No shipped rule says 'a source cannot be reached'; the built-in job context_sync runs "
            "5 minutes before that report (tenant setting TRACIORA_CONTEXT_SYNC_AT), fails, and the rule job_failed "
            "opens. Slot 2 acknowledges it; her Run now at 48 minutes past resolves it. An error alert also writes "
            "an ops.alert push row for her.",
    "AL20": "dismissed as a false alarm by slot 2: a planned restart",
    "AL25": "the one alert open at T, a warning: one of three phones with push on (slot 15's) never acknowledged a message",
    "times": "wall clock of the home zone; opened is created_at, closed is resolved_at (or the dismissal), last_seen_at is the close",
}

# ---------------------------------------------------------------- the two operators' Inbox at T
# half: needs (Needs you, kind act) or update (Updates, kind inform; all listed here are unread).
# key: what the line's id is in the product, so a read mark can name it.
INBOX = {
    "junior": dict(
        slot=6, zone="home",
        opened_today="she opened the tray at o+0:10 and tapped one line: slot 4's comment on the review card (read)",
        lines=[
            dict(half="needs", source="due", verb="due_today", about="card J-estimate", key="due:<card>:<T's date>", at="T@15:00"),
            dict(half="needs", source="due", verb="due_today", about="card J-confirm", key="due:<card>:<T's date>", at=L("T@15:00", "T@17:00")),
            dict(half="update", item=1, source="activity", verb="assigned", about="card S16-review, given by slot 4",
                 key="the activity row", at="W-1.mon@o+1:10"),
            dict(half="update", item=2, source="notice", type="memory.decided", about="her note proposal 2, declined by slot 4",
                 key="the pushed row", at="W-3.mon>=p6>p4@o+1:00",
                 text=L("Read the booking back before hanging up — declined: the page 'Booking a visit' already says this; "
                        "propose the wording there",
                        "Проговорить запись перед тем, как положить трубку — отклонено: На странице «Запись на ремонт» "
                        "это уже есть; предложите формулировку туда")),
            dict(half="update", item=3, source="rota", verb="shift_published", about="her shifts of week W+1, one line a shift",
                 key="each shift's id", at=L("W0.thu@11:40", "W0.thu@11:40"), lines=L(5, 4),
                 which=L("Monday to Friday of W+1", "her rota days of W+1")),
            dict(half="update", item=4, source="diary", verb="invited", state="accepted", about="entry S16-meeting",
                 key="her participant row", at="W-1.mon>=p6@o+5:35"),
            dict(half="update", item=5, source="activity", verb="mentioned", about="slot 5's comment on card M-chats-cover",
                 key="the activity row", at="p5-1@c-0:28"),
            dict(half="update", item=6, source="notice", type="conversation.message", about="S7's return chat, which she owns",
                 key="the pushed row", at="T@T-0:30",
                 text=L("Rachel Dunlap: anything wed or thurs, early? and whats my total with tax",
                        "Ольга: в пятницу и субботу никак, на работе завал. а на следующей неделе во вторник или среду вечером можно? и сколько всего с меня будет")),
            dict(half="update", item=7, source="notice", type="scheduled_task.ran", about="her task 'My call backs' / «Мои перезвоны»",
                 key="task_run:<task>:<finished at>", at=L("T@07:30", "T@09:00"),
                 text=L("{n} waiting at East Main; the oldest has waited {days} days.",
                        "На Московском шоссе ждут перезвона: {n}; самый давний — {days} дн."),
                 computed="n = the queue at main less today's misses (calls.queue_at_t: 4 - 2 = 2); days from the oldest"),
        ],
        counts=dict(needs=2, update_items=7, update_lines=L(11, 10)),
    ),
    "senior": dict(
        slot=4, zone="home",
        lines=[
            dict(half="needs", source="handover", verb="handover_requested", about="card H-east-waiting", key="handover:<card>", at="T@T-0:40"),
            dict(half="needs", source="due", verb="due_today", about="card G-listen-calls", key="due:<card>:<T's date>", at="W0.fri@c-0:30",
                 only_if="T's date is the Friday of W0 (the nominal T)"),
            dict(half="needs", source="due", verb="due_today", about="card G-weekly-callers", key="due:<card>:<T's date>", at="W0.fri@c-0:30",
                 only_if="T's date is the Friday of W0 (the nominal T)"),
            dict(half="needs", source="rota_news", verb="change_requested", about="request R50 (slot 16, remove)", key="the activity row", at="p16-3@o+1:05"),
            dict(half="needs", source="rota_news", verb="change_requested", about="request R51 (slot 16, remove)", key="the activity row", at="p16-3@o+1:08"),
            dict(half="needs", source="notice", type="memory.proposed", about="slot 6's proposal 3 (the company driver's limit)",
                 key="the pushed row", at="p6-1@o+6:30",
                 text=L("A company driver cannot approve work over 300 USD; call the fleet contact",
                        "Водитель организации не согласует работы дороже 8 000 ₽; звонить ответственному")),
            dict(half="needs", source="notice", type="memory.proposed", about="the nightly proposal, three holders (5, 6, 7)",
                 key="the pushed row", at="T@03:30",
                 text=L("Prices source: Take prices from the price list page, never from a service page",
                        "Откуда брать цены: Цены брать со страницы прайс-листа, а не со страницы услуги")),
            dict(half="needs", source="notice", type="knowledge.proposed", about="slot 5's correction to the timing-belt page",
                 key="knowledge:<proposal id>", at="p7-4>p5>p4>p5@o+2:00",
                 text="ids only; the engine words it when the tray is read"),
            dict(half="needs", source="notice", type="board.quiet", about="card Q-04-rack", key="quiet:<card>:<since>", at="W-2.thu@05:30"),
            dict(half="update", item=1, source="notice", type="punch.corrected", about="slot 14 fixed the clock-out he forgot",
                 key="the pushed row", at="p14-1@o+0:02",
                 context=dict(business_day="p14-2", left_at_local=L("16:05", "18:10"), site="main")),
            dict(half="update", item=2, source="notice", type="scheduled_task.ran", about="his task 'Tomorrow's gaps in cover' / «Завтрашние пробелы в графике»",
                 key="task_run:<task>:<finished at>", at=L("T>-1d@16:30", "T>-1d@18:30"),
                 text=L("No gaps tomorrow at East Main or Bonny Oaks.",
                        "Завтра пробелов нет: на Московском шоссе и на Инженерном людей хватает по норме."),
                 computed="from the cover of T's date against the rules in force"),
        ],
        counts=dict(needs=9, update_items=2, update_lines=L(2, 2)),
        not_a_line="the flagged no-show of card S14: the product writes a shift.no_show event and no tray line reads it "
                   "(DESIGN.md section 10)",
    ),
}
