# Demo tenant ladder, seed v1

Data: `ladder.json` (the same in both configurations). Decision: **the shipped ladder, unchanged** (`config/defaults/access_levels.json`, `access_limits.json`; `tools.json` empty). Why: every card's asker fits a shipped step (design 1.4: "ranks follow the shipped ladder"), the planned refusals rest on shipped floors (S14.7, S12.5, S10.4), and a renamed or inserted step would renumber ranks and make the seed a test of the ladder instead of the agent.

## The steps

| Step key | Scope | Rank | History | Screens | Who in the cast |
|---|---|---|---|---|---|
| `worker` | worker | 1 | 180 days | Home, My schedule, Calendar, Inbox, Ask | the mechanics, the lube and tyre technician, F2, F4 when in season |
| `junior` | junior | 2 | 180 days | + Board, Memory, Knowledge base, Conversations, Calls reports, Scheduled tasks | advisors, foreman, parts manager, F1 |
| `middle` | middle | 3 | 365 days | as junior | the lead advisors and the bookkeeper |
| `senior` | senior | 4 | whole | the Planner in place of My schedule | founder, service manager, `west`'s shop manager |
| `admin` | admin | 5 | whole | + the console | the managing owner |

Go-live is T-175 days (ledger `time.go_live_days`), inside the junior's 180 (SETTINGS.md).

## Tools each rank holds (shipped audience, the demo's grants)

| Family | Worker | Junior and middle add | Senior and admin add |
|---|---|---|---|
| calendar | `my_day`, `show_calendar`, `show_meeting`, `schedule_meeting`, `edit_meeting`, `cancel_meeting`, `respond_meeting`, `block_time`, `check_availability`, `find_free_slot`, `invitable` | | |
| inbox | `my_inbox`, `open_line` | | |
| roster | `my_schedule`, `request_shift_change`, `withdraw_request`, `show_requests`, `who_is_working` | `add_shift`, `cancel_shift` (registered from junior, refused per call below senior: planning is senior work) | `plan_shifts`, `show_week`, `show_site_setup`, `show_publishes`, `open_publish`, `copy_week`, `move_shift`, `set_rotation` |
| knowledge | `kb_search`, `kb_read`, `kb_overview`, `kb_links`, `kb_history` | `kb_suggest` (registered from junior; the knowledge base's own rungs, propose from middle and publish from senior, decide what a suggestion may do) | |
| utilities | `calculator`, `get_current_time`, `get_todays_date`, `get_current_weather`, `product_help`, `send_feedback` | `web_search`, `web_fetch`, `web_browse`, `export_analysis_artifact` | `get_ai_usage_overview` |
| board | none | `show_board`, `show_task`, `create_task`, `edit_task`, `move_task`, `comment_task`, `assign_batch`, `plan_work`, `my_team`, `archive` | |
| memory | none | `recall_memory`, `remember_note`, `propose_team_note` | `decide_team_note`, `review_team_note` |
| scheduled tasks | none | `list_scheduled_tasks`, `read_scheduled_task_runs`, `schedule_task`, `update_scheduled_task`, `delete_scheduled_task` (each reads only the caller's own) | |
| analytics (data) | none | `list_context`, `search_context`, `grep_context`, `read_context`, `execute_sql`, `read_query_result`, `display_chart` | |

Not registered: `run_bash` (code sandbox not granted). Admin holds the senior's tools in chat (the admin scope maps to the senior's tool audience) and reads the sources at the `admin` rank. What each rank reads inside the data tools is `SOURCES.md`. Middle holds no tool a junior lacks; it differs in its sources' columns, its history window and the knowledge base's propose rung.

What a rank lacks follows from the table: a worker has no board, memory, scheduled tasks or data tools, which is the refusal of S14.7 ("Who is late most often?" asked by slot 15: no tool reads anyone's punches). Below senior nobody plans the roster or decides a team note.

## Cast slots

Postings are `identity.person_location` rows (first is the home shop). A worker, junior or middle login is bound to the shops of its postings on the day it asks; a senior or admin is bound to none and reads every shop (`docs/features/core-db.md`, the site binding).

| Slot | Who (en / ru) | Role | Rank | Postings | Bound to | What follows |
|---|---|---|---|---|---|---|
| 1 | Ray Brennan / Николай Петрович Ермолаев | founder | senior | none | every shop | Receives every shift request and every team-note proposal of all three shops in his Inbox, and may decide them. **Intended** (design 7.2, Cast: the founder's Inbox is a planner's and is designed as such). Reads his brief (S10.2) |
| 2 | Claire Brennan / Екатерина Николаевна Ермолаева | managing owner | admin | none | every shop | the console; asks the data questions; adds herself as watcher on S16's card (the assignment rule refuses the senior adding her) |
| 3 | Donna Ledford / Ирина Владимировна Кудашкина | office manager | middle | main | main | ERP pay and till counts (opened from middle, design 7.2); punches for payroll hours (core grant from middle; `kb/en/office/payroll-hours.md`) |
| 4 | Greg Whitaker / Сергей Анатольевич Мельников | service manager | senior | main, east | every shop | the senior operator: plans both home shops, decides team notes, sees colleagues' phone performance; also receives `west`'s requests and proposals |
| 5 | Travis Burnette / Дмитрий Олегович Григорьев | lead advisor | middle | main | main | proposes the knowledge correction (S12.4) |
| 6 | Maya Torres / Алина Рамилевна Хасанова | service advisor | junior | main, east | main and east | the junior operator. The east posting (ledger `cast.also_sites`) lets her be rostered at east and offered as cover for slot 16's week (S5.2); it also binds her to east, so her call-back list holds east's waiting miss: five callers in all (S3.4, `calls.queue_at_t`) |
| 7 | Caleb Sutton / Никита Ведяшкин | service advisor | junior | main | main | |
| 8 | Randy Elrod / Александр Михайлович Бурмистров | shop foreman | junior | main | main | |
| 9 | Marcus Gaines / Павел Мещеряков | parts manager | junior | main, east | main and east | serves both home shops (S16 helper) |
| 10 | Kevin Lawson / Андрей Викторович Шубин | diagnostic technician | worker | main | main | |
| 11 | Dustin Swafford / Максим Рябов | technician | worker | main | main | files shift requests (S14.4) |
| 12 | Luis Herrera / Алексей Карпов | technician | worker | main | main | |
| 13 | Terry Dotson / Ильдар Фаритович Нуруллин | electrical technician | worker | main | main | |
| 14 | Hunter Varnell / Иван Сурков | apprentice technician | worker | main | main | corrects forgotten clock-outs on Home |
| 15 | Cody Gann / Евгений Чугунов | lube and tyre technician | worker | main | main | asks S14.7 and is refused |
| 16 | Angie Holloway / Светлана Юрьевна Демидова | lead advisor | middle | east | east | asks S1.7 about east |
| 17 | Josh Tipton / Артём Николаев | service advisor | junior | east | east | |
| 18 | Andre Simmons / Валерий Геннадьевич Егоров | lead technician | worker | east | east | |
| 19 | Brandon Sisk / Роман Кудряшов | technician | worker | east | east | |
| 20 | Austin Crabtree / Антон Блинов | technician | worker | east | east | |
| 21 | Jordan Akins / Марат Аюпов | technician | worker | east, main | east and main | floats; takes slot 20's shift (S14.8) |
| 22 | Dale Hutchins / Ринат Фаридович Галиев | shop manager | senior | west | every shop | plans `west`'s roster; as a senior also receives the home shops' requests and proposals (intended, as for slot 1) |
| 23 | Chad Binkley / Вячеслав Крюков | service advisor | junior | west | west | |
| 24 | Jasmine Bolden / Камила Шакирова | service advisor | junior | west | west | |
| 25 | Gary Tidwell / Фарит Мансурович Зиннатуллин | technician | worker | west | west | |
| 26 | Shane Maddox / Станислав Орехов | technician | worker | west | west | |
| 27 | Derek Hooper / Виталий Сомов | technician | worker | west | west | |
| 28 | Tyler Jarrell / Булат Гарипов | technician | worker | west | west | part-time |
| 29 | Brenda Pickett / Татьяна Геннадьевна Пахомова | service advisor | junior | main, east | main and east | posted at main and east (ledger `cast.also_sites`, `cast.json` `also_sites`): S5.2 names her as east's cover in both markets, and the planner offers only people posted at the shop |
| F1 | Brent Lassiter / Артур Назаров | service advisor | junior | west | (ended) | login and Chatwoot user ended the day he was fired; person kept, inactive |
| F2 | Wes Tate / Константин Жарков | technician | worker | main | (ended) | login ended the day he was fired |
| F3 | Brad Keller / Вадим Савельев | service advisor | none | main | no login | left before go-live: ERP only |
| F4 | Mason Pruitt / Рустам Юсупов | seasonal helper | worker | main | main, in season | worker per build (ledger `cast.f4_rank`, `cast.json` rank): whenever one of his seasons lies inside G..T or runs at T (design 7.2, S11), he has a person, a posting at main and a worker login that ends with the season; otherwise ERP only. For the reference T (2026-11-13) that is the English summer and the Russian autumn season, which runs at T |

Every slot has exactly one rank (`validate.py`).
