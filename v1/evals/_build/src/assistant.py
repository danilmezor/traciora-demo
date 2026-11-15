# assistant/DESIGN.md section 8: the sixteen questions of the managers' side of the assistant (A.1 to A.16).
# "All survive the small size."
from dsl import C, Q, T

F = "assistant/DESIGN.md"
D = lambda quote: (F, quote)  # noqa: E731

Q("AS.01", file=F, ref="A.1", asker=6, kind="list", small=True,
  src_q="Which notes do you keep about how I work?",
  q=T("Which notes do you keep about how I work?", "Что вы запомнили о том, как я работаю?"),
  scope=dict(population="Her live personal notes.", period="At T.", definition="By subject."),
  answer=T("Her [[s4.notes.personal_notes_of_6|int]], by subject: Reply drafts, Answer length, Prices source, "
           "Default shop, Call summaries, Money and dates.",
           "Её [[s4.notes.personal_notes_of_6|int]] заметок, по темам: «Черновики ответов», «Длина ответа», «Откуда "
           "брать цены», «Сервис по умолчанию», «Разбор звонков», «Суммы и даты»."),
  list_rule="Slot 6's personal notes in state active or dormant, by subject.",
  members=[T("Reply drafts", "«Черновики ответов»"), T("Answer length", "«Длина ответа»"),
           T("Prices source", "«Откуда брать цены»"), T("Default shop", "«Сервис по умолчанию»"),
           T("Call summaries", "«Разбор звонков»"), T("Money and dates", "«Суммы и даты»")],
  proof=[("memory", "platform.memory by login")], sources=["memory"])

Q("AS.02", file=F, ref="A.2", asker=6, kind="value", small=True,
  src_q="Where did my note about prices come from?",
  q=T("Where did my note about prices come from?", "Откуда взялась моя заметка про цены?"),
  scope=dict(population="The source of \"Prices source\".", period="At T.",
             definition="The chat and the turn that saved the note."),
  answer=T("From her chat “Front pads and rotors, Camry” of {a2_chat_day}, after an answer quoted the page “Brake "
           "questions”.",
           "Из её чата «Колодки и диски на Гранту» от {a2_chat_day}: заметка появилась после ответа, в котором "
           "была процитирована страница «Вопросы по тормозам»."),
  computed=[C("a2_chat_day", "the day of the chat that saved the note", "slot 6's 4th working day of period P5 "
              "(source_at of the note)", "memory", ["platform.memory", "conversations (auth.db)"],
              design=D("The chat \"Front pads and rotors, Camry\" in period P5 (date emitted)"))],
  proof=[("memory", "platform.memory.source_conversation_id"), ("account_store", "the thread")],
  sources=["memory", "account_store"])

Q("AS.03", file=F, ref="A.3", asker=7, kind="refusal", small=True,
  src_q="What notes do you keep about Maya?",
  q=T("What notes do you keep about Maya?", "Какие заметки у вас есть про Алину?"),
  scope=dict(population="Another person's notes.", period="At T.", definition="A personal note is its owner's."),
  answer=T("Refused: a personal note is its owner's.", "Отказ: личную заметку видит только её владелец."),
  refusal=dict(by="owner", reason=T("A personal note is its owner's.", "Личную заметку видит только её владелец.")),
  proof=[("memory", "store.visible")], sources=["memory"])

Q("AS.04", file=F, ref="A.4", asker=2, kind="refusal", small=True,
  src_q="What notes do you keep about Maya?",
  q=T("What notes do you keep about Maya?", "Какие заметки вы храните про Алину Хасанову?"),
  scope=dict(population="Another person's notes, asked in Ask.", period="At T.",
             definition="No Ask tool reads another login."),
  answer=T("Refused in Ask; the console's Memory view shows them and counts the read.",
           "В «Спросить» — отказ; чужие заметки показывает раздел памяти в консоли, и такой просмотр учитывается."),
  refusal=dict(by="owner", reason=T("No Ask tool reads another person's notes.",
                                    "В «Спросить» нет инструмента, который читает чужие заметки."),
               may_offer=T("The console's Memory view, which counts the read.",
                           "Раздел памяти в консоли, где такой просмотр учитывается.")),
  proof=[("memory", "no Ask tool reads another login")], sources=["memory"])

A5_SCOPE = dict(population="Team notes at or below the asker's rank.", period="At T.",
                definition="min_rank of each team note.")
A5_SLOT = C("a5_notes", "the team notes the asker sees, by subject",
            "platform.memory, scope business, with min_rank at or below the asker's rank",
            "memory", ["platform.memory"], design=D("11; 13; 14."))
A5_PENDING = {"both": ["inventions"]}

Q("AS.05a", file=F, ref="A.5", asker=6, kind="list", small=True,
  src_q="Which team notes can I see?",
  q=T("Which team notes can I see?", "Какие заметки команды мне видны?"),
  scope=A5_SCOPE,
  answer=T("[[mem.team_notes.visible_from.junior|int]] ({a5_notes}). She does not see “Money in answers”, "
           "“Declined work” or “Desks, not people”.",
           "[[mem.team_notes.visible_from.junior|int]] ({a5_notes}). Заметок «Суммы в ответах», «Отказ от работ» и "
           "«Аппараты, а не люди» она не видит."),
  list_rule="Team notes whose min_rank is junior or below.", member_slot="a5_notes",
  must_not=[T("Listing “Money in answers”, “Declined work” or “Desks, not people”.",
              "Называть заметки «Суммы в ответах», «Отказ от работ» или «Аппараты, а не люди».")],
  computed=[A5_SLOT], proof=[("memory", "platform.memory.min_rank")], sources=["memory"], pending=A5_PENDING)

Q("AS.05b", file=F, ref="A.5", asker=5, kind="list", small=True,
  src_q="Which team notes can I see?",
  q=T("Which team notes can I see?", "какие заметки команды мне видны"),
  scope=A5_SCOPE,
  answer=T("[[=L('mem.team_notes.visible_from.junior')+L('mem.team_notes.visible_from.middle')|int]] "
           "({a5_notes}).",
           "[[=L('mem.team_notes.visible_from.junior')+L('mem.team_notes.visible_from.middle')|int]] ({a5_notes})."),
  list_rule="Team notes whose min_rank is middle or below.", member_slot="a5_notes",
  computed=[A5_SLOT], proof=[("memory", "platform.memory.min_rank")], sources=["memory"], pending=A5_PENDING)

Q("AS.05c", file=F, ref="A.5", asker=4, kind="list", small=True,
  src_q="Which team notes can I see?",
  q=T("Which team notes can I see?", "Какие заметки команды я вижу?"),
  scope=A5_SCOPE,
  answer=T("All [[mem.team_notes.all|int]] ({a5_notes}).", "Все [[mem.team_notes.all|int]] ({a5_notes})."),
  list_rule="Team notes whose min_rank is senior or below: all of them.", member_slot="a5_notes",
  computed=[A5_SLOT], proof=[("memory", "platform.memory.min_rank")], sources=["memory"], pending=A5_PENDING)

Q("AS.06", file=F, ref="A.6", asker=4, kind="cannot tell", small=True,
  src_q="Which three advisors hold the note about price sources?",
  q=T("Which three advisors hold the note about price sources?",
      "У каких троих мастеров есть заметка про то, откуда брать цены?"),
  scope=dict(population="The night's proposal.", period="At T.",
             definition="The proposal carries holders_count and no owner."),
  answer=T("The data cannot tell him: the proposal carries a count of three and no names.",
           "По данным этого не сказать: в предложении указано только число — трое, имён в нём нет."),
  cannot=dict(lacks=T("The names: the proposal carries a count of three and no names.",
                      "Имена: в предложении есть только число — трое."),
              may_give=[T("That three people hold a note with this subject.",
                          "Что заметка с такой темой есть у троих.")],
              wrong_if=T("An answer that names the three is wrong.", "Ответ, который называет этих троих, неверен.")),
  proof=[("memory", "platform.proposal.holders_count, no owner")], sources=["memory"])

Q("AS.07", file=F, ref="A.7", asker=22, kind="list", small=True,
  src_q="What waits for my decision in Memory?",
  q=T("What waits for my decision in Memory?", "Что в «Памяти» ждёт моего решения?"),
  scope=dict(population="Open proposals and unverified team notes.", period="At T.",
             definition="The same for slots 1, 2 and 4."),
  answer=T("Two proposals, company drivers and price sources, and one team note to check, “Missed callers”.",
           "Два предложения — «Водители организаций» и «Откуда брать цены» — и одна заметка команды на проверку, "
           "«Пропущенные клиенты»."),
  list_rule="Proposals in state proposed and team notes in state unverified.",
  members=[T("Proposal: “Company drivers”, from Maya Torres", "Предложение «Водители организаций» от Алины Хасановой"),
           T("Proposal: “Prices source”, from the nightly tidy-up",
             "Предложение «Откуда брать цены» от ночной проверки"),
           T("Team note to check: “Missed callers”", "Заметка команды на проверку: «Пропущенные клиенты»")],
  keys=["mem.retest_days"],
  proof=[("memory", "platform.proposal, platform.memory")], sources=["memory"])

Q("AS.08", file=F, ref="A.8", asker=2, kind="value", small=True,
  src_q="Why was Jasmine's note about answering the phone declined?",
  q=T("Why was Jasmine's note about answering the phone declined?",
      "Почему отклонили заметку Камилы о том, как брать трубку?"),
  scope=dict(population="Proposal P08.", period="At T.", definition="The decider, the day and the reason."),
  answer=T("Dale Hutchins declined it the day it was proposed, {a8_day}: “Folks here know who they called. Not "
           "needed.”",
           "Ринат Фаридович Галиев отклонил её в день подачи, {a8_day}: «У нас клиенты и так знают, куда звонят. "
           "Лишнее.»"),
  computed=[C("a8_day", "the day proposal P08 was proposed and declined",
              "decided_at of the proposal; the Wednesday of week T-9 (ru: slot 24's first working day on or after "
              "it)", "memory", ["platform.proposal"])],
  proof=[("memory", "platform.proposal"), ("core", "her Inbox update")], sources=["memory"],
  pending={"both": ["inventions"]})

Q("AS.09", file=F, ref="A.9", asker=5, kind="nothing", small=True,
  src_q="Do I have a team note waiting for a decision?",
  q=T("Do I have a team note waiting for a decision?", "у меня есть заметка для команды которая ждёт решения"),
  scope=dict(population="His own open proposals.", period="At T.", definition="open_proposals(owner)."),
  answer=T("None.", "Нет."),
  nothing=T("His one proposal was approved; the price-source proposal is the night's, not his.",
            "Его единственное предложение уже утверждено, а предложение про цены подала ночная проверка, не он."),
  proof=[("memory", "open_proposals(owner)")], sources=["memory"])

Q("AS.10", file=F, ref="A.10", asker=4, kind="value", small=True,
  src_q="What did my note \"The shop\" say before I changed it?",
  q=T("What did my note “The shop” say before I changed it?",
      "Что было в моей заметке «Наш сервис» до того, как я её поменял?"),
  scope=dict(population="The archived predecessor.", period="At T.", definition="The note this one replaced."),
  answer=T("“'The shop' means East Main”, replaced on {a10_day}.",
           "«„Сервис“ без уточнения — это Московское шоссе»; заменена {a10_day}."),
  computed=[C("a10_day", "the day he replaced the note", "the Wednesday of week T-18 (valid_to of the archived note)",
              "memory", ["platform.memory"], design=D("replaced on the Wednesday of week T-18"))],
  proof=[("memory", "platform.memory.superseded_by")], sources=["memory"])

Q("AS.11", file=F, ref="A.11", asker=2, kind="value", small=True,
  src_q="Which of my notes have gone unused?",
  q=T("Which of my notes have gone unused?", "Какими из моих заметок вы давно не пользуетесь?"),
  scope=dict(population="Her dormant notes.", period="At T.", definition="state dormant."),
  answer=T("One: “Tables as files”, unused for over ninety days and still recallable.",
           "Одной: «Таблицы файлом» — ею не пользовались больше девяноста дней, но она по-прежнему доступна."),
  seed_files=["assistant/{cfg}/notes.json"],
  proof=[("memory", "platform.memory.state")], sources=["memory"])

Q("AS.12", file=F, ref="A.12", asker=2, kind="value", small=True,
  src_q="How often did the Friday list show a discount nobody approved?",
  q=T("How often did the Friday list show a discount nobody approved?",
      "Сколько раз в пятничном списке была скидка без согласования?"),
  scope=dict(population="Runs of \"Discounts over 10 %\".", period="Since the rule.",
             definition="A run whose answer lists an order with no approver."),
  answer=T("Twice, on the Fridays of {a12_fridays}: Chad Binkley, "
           "[[s2.west.discounts_after.unapproved_pct_each|pct]] each.",
           "Дважды, в пятницы {a12_fridays}: оба раза Вячеслав Крюков, по "
           "[[s2.west.discounts_after.unapproved_pct_each|pct]]."),
  computed=[C("a12_fridays", "the two Fridays whose run lists an unapproved discount",
              "the Fridays of weeks T-3 and T-1: the runs after slot 23's two orders",
              "account_store", ["cron_runs"], design=D("Twice: the Fridays of weeks T-3 and T-1, Chad Binkley, 12 % "
                                                       "each"))],
  proof=[("account_store", "auth.db cron_runs")], sources=["account_store"])

Q("AS.13", file=F, ref="A.13", asker=6, kind="refusal", small=True,
  src_q="What did Greg's brief say this morning?",
  q=T("What did Greg's brief say this morning?", "Что было в утренней сводке Сергея Анатольевича?"),
  scope=dict(population="Another person's brief.", period="T's date.",
             definition="Task reads are scoped to the caller."),
  answer=T("Refused: she reads her own.", "Отказ: ей доступна только её собственная сводка."),
  refusal=dict(by="owner", reason=T("A person reads only their own brief.", "Сводку каждый читает только свою."),
               may_offer=T("Her own brief.", "Её собственная сводка.")),
  proof=[("account_store", "task reads are scoped to the caller")], sources=["account_store"])

Q("AS.14", file=F, ref="A.14", asker=1, kind="value", small=True,
  src_q="Why did I get no second brief today?",
  q=T("Why did I get no second brief today?", "Почему сегодня не было второй сводки"),
  scope=dict(population="His brief runs.", period="T's date.", definition="A run written skipped."),
  answer=T("It was skipped ({a14_skipped_run}): the brief before it had not been opened.",
           "Её пропустили ({a14_skipped_run}): предыдущую сводку так и не открыли."),
  computed=[C("a14_skipped_run", "the time of slot 1's skipped brief run of T's date",
              "his brief runs of T's date with status skipped; one exists only when T is after the day's second "
              "brief time (10:40 home time for a person with no shift), so for an earlier T the question has no "
              "second brief to ask about", "account_store", ["cron_runs"],
              design=D("a time other than the day's first is written `skipped` while the brief before it is unread"))],
  proof=[("account_store", "auth.db cron_runs.error_text")], sources=["account_store"])

Q("AS.15", file=F, ref="A.15", asker=4, kind="refusal", small=True,
  src_q="Did all of Claire's reports run last week?",
  q=T("Did all of Claire's reports run last week?", "Все отчёты Екатерины Николаевны отработали на прошлой неделе?"),
  scope=dict(population="Another person's tasks.", period="Week W-1.",
             definition="Task reads are scoped to the caller."),
  answer=T("Refused: he reads his own, “Tomorrow's gaps in cover”.",
           "Отказ: ему доступен только его собственный отчёт — «Завтрашние пробелы в графике»."),
  refusal=dict(by="owner", reason=T("A person reads only their own scheduled tasks.",
                                    "Задачи по расписанию каждый видит только свои."),
               may_offer=T("His own task, “Tomorrow's gaps in cover”.",
                           "Его собственный отчёт «Завтрашние пробелы в графике».")),
  keys=["s10.tasks"],
  proof=[("account_store", "task reads are scoped to the caller")], sources=["account_store"])

Q("AS.16", file=F, ref="A.16", asker=4, kind="explanation", small=True,
  src_q="Is there a team rule about promising a pickup day, and was it kept?",
  q=T("Is there a team rule about promising a pickup day, and was it kept?",
      "Есть ли у команды правило про обещание дня выдачи и соблюдалось ли оно?"),
  scope=dict(population="Team note \"Parts promises\"; S8 and S6 after its date.", period="Since the note.",
             definition="A promised pickup day with no confirmed delivery behind it."),
  answer=T("Yes, the team note “Parts promises”, approved on {a16_approved_day}; it was broken twice, by Caleb "
           "Sutton's same-day promise and by the day Chad Binkley promised.",
           "Да, заметка команды «Обещание срока», утверждена {a16_approved_day}; нарушали её дважды: Никита "
           "Ведяшкин пообещал сделать в тот же день, Вячеслав Крюков назвал день готовности."),
  facts=[T("The team note “Parts promises”: promise a pickup day only after the parts manager confirms the "
           "delivery; approved on {a16_approved_day}.",
           "Заметка команды «Обещание срока»: день выдачи обещаем только после того, как менеджер по запчастям "
           "подтвердил поставку; утверждена {a16_approved_day}."),
         T("Broken by Caleb Sutton's same-day promise on the timing-belt job.",
           "Нарушено: Никита Ведяшкин пообещал сделать ремень ГРМ в тот же день."),
         T("Broken by the day Chad Binkley promised the customer whose car waits for a part.",
           "Нарушено: Вячеслав Крюков назвал день готовности клиенту, чья машина ждёт запчасть.")],
  computed=[C("a16_approved_day", "the day the team note was approved", "the Thursday of week T-11",
              "memory", ["platform.memory"], design=D("The note, approved in week T-11"))],
  proof=[("memory", "platform.memory"), ("core", "calls 9 and 15")], sources=["memory", "core"],
  pending={"both": ["inventions"]})
