# The managers' side of the assistant: design (seed v1)

Ask threads, memory (personal notes, team notes, proposals), scheduled AI tasks with their runs, and the briefs. Rules R1 to R13 of the seed design are cited as "rule Rn". Every count here is a row of `ledger_rows.json` beside this file (section 7), proposed to `../ledger.json`; `../checks/check_assistant.py en|ru` fails on a difference.

Paths without a root are in the product repository; `B` = `apps/backend/src/traciora`. Classes: **M** measured, **D** derived, **X** designed. Read on 2026-11-13 at `af75145b8`.

Seven facts of the product shape everything below:

- **A thread is one encrypted file, and it holds no tool result.** `user_<conversation id>.json` keeps the person's messages and the assistant's final answers. A tool call survives only as a card on the answer: its name, labels, status and times (`B/core/agents/turn_activity.py:136-180, 215-234`). The arguments and the rows are not in the file. A query's rows are a separate artifact that expires after 30 days (`B/core/tools/data/adapters.py:40-64`, `B/core/artifacts/store.py:27`).
- **A personal note names a chat and a bound turn, not a message.** Saving a note binds the turn in the chat file's own metadata; `source_turn` is the ordinal of that binding in the chat (1 for the first note a chat saved), `source_at` its time (`B/core/memory/provenance.py:15-51`).
- **Every team note is published by an approved proposal** (`B/core/commands/memory.py:194-298`). There is no other writer. A proposal has three statuses; a withdrawal is a rejection decided by its proposer (`:301-319`).
- **A team note is visible from its proposer's rank** until a senior lowers it (`:161-170, 352-371`); the nightly proposal takes the highest rank among its holders (`B/core/memory/dream.py:84`).
- **The night acts on what is seeded.** At 00:00 the tidy-up makes a personal note dormant after 90 days without use, proposes any subject three people hold, and marks a team note unverified when its check is due (`dream.py:33-61, 82-103`, `B/core/memory/fingerprint.py:201-235`, `B/workers/app_runtime.py:563-567`). Seeded rows must already be where that rule would leave them, or the first night rewrites the demo.
- **The brief has no time of its own.** It is written up to four times a day by the person's shift, or at 06:40, 10:40, 14:40 and 18:40 without one; a time other than the day's first is written `skipped` while the brief before it is unread (`B/core/tools/workspace/brief.py:47-50, 68-82, 320-368`). The newest 200 rows of a job are kept, skipped ones included (`B/core/tools/workspace/scheduled_tasks/tasks.py:74`, `B/core/scheduling/cron_store.py:548-558`).
- **The scheduler pays its debts at start.** A task whose last due time no run answered gets a late run, and a brief whose latest time is unanswered is written (`tasks.py:116-130`, `brief.py:324-368`). Both call a model. So every job needs a row that answers its last due time before T.

## 1. One record across the stores

| Record | Store | A loader fills | Reference |
|---|---|---|---|
| Ask thread | auth.db `conversations` | `id` (a uuid: it is also the note's `source_conversation_id`), `manager_id`, `title`, `created_at`, `replied_at` (the last answer), `read_at` (after it, so the thread is not unread), `title_set_by_person` 0; `model` and `subject_json` null, except a thread begun from a run (`{"kind":"scheduled_run","task_id","run_id"}`) | `B/core/auth/manager.py:243-281, 1181-1273` |
| its messages | chat memory file | `schema_version` 2, `user_id`, `message_count`, `messages`: per message `type` (`HumanMessage`, `AIMessage`), `content`, `timestamp`, `additional_kwargs` with `timestamp`, `turn_id` (one client id per exchange, on both messages) and, on an answer, `activity.tool_events` (`id` h0.., `name`, `display_name`, `done_name`, `status`, `started_at`, `ended_at`, `text_offset`) and `activity.decisions` for a card (`request`, `answer`, `done`) | `B/core/agents/agent_memory.py:307-320, 331-389`; `turn_activity.py:191-234` |
| its metadata | the same file | `answer_traces` {turn id: trace id}, `answer_feedback` {trace id: `up` or `down`}, `memory_sql_provenance` {`login_id`, `conversation_id`, `turns` {turn id: [n, time]}} for a chat that saved a note | `agent_memory.py:52-60`; `B/api/routes/chat.py:2337-2395`; `provenance.py:28-46` |
| personal note | core `platform.memory`, scope `personal` | `login_id`, `slug` and `subject_token` from the product's `store.subject_token` and `slug_for`, `memory_class`, the four sealed texts, `state`, `source_conversation_id`, `source_turn`, `source_at`, `valid_from`, `valid_to`, `superseded_by`, `use_count`, `last_used_at`, `release_sha_written`, `created_by`, `updated_by`, `created_at`, `updated_at` | `apps/backend/schema/traciora-core.sql:3344-3455`; `B/core/memory/store.py:83-150` |
| team note | the same, scope `business` | the same texts, `min_rank`, `approved_by_login_id`, `approved_at`, `last_confirmed_at`, `next_retest_at`, `tools_referenced` empty | `commands/memory.py:194-241` |
| proposal | core `platform.proposal` | `owner_login_id` (null for the night's), `status`, sealed subject, text, why, how and reason, `subject_token`, `proposer_rank`, `min_rank`, `holders_count`, `dream_night`, `source_conversation_id` and `source_turn` (null unless the chat had saved a note), `approver_login_id`, `published_as` `memory:<id>`, `decided_at`, `published_at` | `traciora-core.sql:3461-3536`; `commands/memory.py:136-191` |
| the nights | core `platform.config_version` | one row `memory.dream:<date>` per night since G with the night's counts; the night of T's date among them, or the real job runs it again | `dream.py:217-275` |
| scheduled task | auth.db `cron_prompt_jobs` | `slug` from the product's `_slugify` and free-slug rule in creation order, `name`, `cron_expr` from `schedule_words.build`, sealed `prompt_text`, `output_kind` `store`, `enabled` 1, `created_by`, `created_at`, `updated_at` | `manager.py:322-336`; `tasks.py:88-93`; `B/core/scheduling/schedule_words.py:138-162` |
| run | auth.db `cron_runs` | `task_slug`, `owner_id`, `kind`, `status`, `due_at`, `started_at`, `finished_at`, `duration_ms`, sealed `answer_enc` and `instruction_enc`, `error_text`; ids ascending in time, because the newest 200 are kept by id | `manager.py:376-398`; `tasks.py:288-338, 1040-1047` |
| brief job and its runs | the same two tables | job: slug `brief-<manager id>`, the locale's name, `cron_expr` empty, the product's `brief.md` sealed. Runs: `due_at` from `brief.run_times`, `instruction_enc` = `brief.header(...)` + the prompt. `managers.brief_seen_at` | `tasks.py:441-469`; `brief.py:68-82, 376` |
| Inbox line | core `platform.notification_queue` | type, `person_id`, `send_at` = `sent_at` = `delivered_at`, `read_at`, `context_public`, sealed `context_enc`, key `<person>:<line key>` | `traciora-core.sql:3271-3338`; `B/core/commands/notifications/inbox.py:87-112` |

**Loaded with past times (rule R1).**

- Chat files: the loader builds the payload and writes it with the product's `secure_storage.encrypt_text(..., key_env="MEMORY_ENCRYPTION_KEY")`, as `FileBasedMemory._write_payload` does (`agent_memory.py:282-302`). Every message carries its own `timestamp`, so nothing is stamped at build time.
- auth.db: plain inserts with explicit times. Prompts, answers and instructions are sealed with `auth_manager.encrypt_secret` (`tasks.py:230-233`).
- Core: rows go in with the core bulk loader, the `touch_mutable_row` trigger off for the load. Texts are sealed with `envelope.encrypt(text, "platform.memory.<field>_enc")`, proposals with `platform.proposal.<field>_enc`, Inbox words with the notifications' `CONTEXT_ENC`. `updated_at` matters: the model's note index prints it as the note's date (`B/core/memory/index.py:34`).
- Tool labels (`display_name`, `done_name`) and card bodies are produced at build time by the product's own `tool_label`, `t("tools_done.<name>")` and `memory_tools._ask_remember` / `_ask_propose` in the configuration's locale, so a thread file names only the tool and the card's answer.

**What a command still does at T.** Only the Inbox lines that are still open at T go through the product's `inbox.push(..., at=)`, which takes its time as an argument: the two waiting proposals (four people each), the unverified note (four people) and today's runs. Nothing else of this part needs a command.

**Left the way the night would leave it.** An active personal note has `greatest(last_used_at, valid_from)` inside the last 90 days; a dormant one between 90 and 180 days back; only one subject is held by three people, and it is already proposed; team notes past their check are either kept (`next_retest_at` ahead of T) or unverified. `checks/check_assistant.py` proves the subject rule; the seeder asserts the dates.

**Read back** through the product's reads: `GET /api/chat/history` per thread (messages, cards, thumbs), `store.visible` and `commands.memory.open_proposals` per person, `tasks.task_public` and `run_public` per task, `brief.panel` for the four, the tray per person.

**The version stamp (rule R3).** Nothing here is a model's output, and each store says so without showing it on a screen people read:

| Artefact | Stamp |
|---|---|
| assistant answer | `additional_kwargs.seed` = {`seed`: `v1`, `prose`: the file's `prose_version`, `item`: `<thread id>#<turn>`}; `response_metadata.model_name` `seed-v1`; trace id = the first 32 hex of sha256(`seed-v1:<thread>#<turn>`) |
| run answer, brief | a last line of `instruction_enc`: `[seed v1 · <task id> · <case>/<wording> · <prose_version>]`. The instruction as it ran is shown only when a run is opened |
| note, team note | `release_sha_written` = `seed-v1+<product sha>` |
| nightly proposal, tightened note | written by the actor `agent` / `seed-v1`, which the product shows as "the nightly tidy-up" (`B/core/memory/notify.py:15-26`) |

## 2. Ask threads

### 2.1 Who has how many

180 threads (`ask.threads`), 15 written by hand and 165 built from patterns: slot 4 has 40, slot 2 30, slot 6 25, slot 1 10, slot 5 10, 16 and 7 nine each, 3 and 24 eight, 9 seven, 17 six, 22, 29 and 8 five, 23 three (`ask.threads_per_person`). Mechanics have Ask and no seeded thread ("Not in this plan"). A thread is a planted instance: both sizes hold all 180.

### 2.2 What managers ask

Share of a person's background exchanges, by rank (`ask.kind_mix`, X, tolerance 8 points):

| Kind | Tools on the card | admin | senior | middle | junior |
|---|---|---:|---:|---:|---:|
| shop system: money, orders, accounts, parts, comebacks | `execute_sql`, `read_context` | 55 | 20 | 30 | 15 |
| calls: missed, the queue, scores | `execute_sql` | 15 | 15 | 10 | 15 |
| roster: who is on, gaps, requests, lateness | `who_is_working`, `show_week`, `show_requests`, `plan_shifts`, `my_schedule` | 0 | 25 | 5 | 5 |
| board: my day, overdue, give a task | `my_day`, `show_board`, `create_task` | 5 | 15 | 10 | 10 |
| knowledge base: a price, a rule, a how-to | `kb_search`, `kb_read` | 5 | 5 | 15 | 20 |
| drafting a message | none, or the lookup the draft needs | 10 | 10 | 15 | 20 |
| planning: a slot, a block, next week | `find_free_slot`, `block_time`, `schedule_meeting` | 5 | 5 | 5 | 3 |
| one customer across stores | `execute_sql` twice | 0 | 0 | 5 | 10 |
| the product itself: my tasks, a run, my notes | `list_scheduled_tasks`, `read_scheduled_task_runs`, `product_help` | 5 | 5 | 5 | 2 |

By person the mix bends to the job: slot 3 asks about bills and punches, slot 9 about purchase orders, slot 8 about returned cars, slot 22 asks little and in one line, slot 1 only what his brief made him curious about. Nine background exchanges end in a refusal by rank or site and four in "the data cannot tell" (`ask.refusals`), from the refusal and cannot-tell patterns.

### 2.3 How a thread is built

- **Exchanges.** One to four per background thread (weights 30, 40, 20, 10 %; 2 to 12 messages, `ask.messages_per_thread`). The first exchange is a pattern of the person's mix; a follow-up is the pattern's own `then`, or a second pattern of a neighbouring kind.
- **Times.** A thread sits on a working day of its owner, at an hour of that person's habit (slot 2 after 21:00, advisors between calls, slot 1 before 08:00). An answer follows its question by 6 s plus 7 s per tool card; a tool card runs 2 to 9 s inside that.
- **Tool cards.** A turn lists its tools in order. Each becomes a `tool_events` entry with status `succeeded` and `text_offset` 0 (the cards sit before the answer text). A refused read is still a card: the tool ran and returned the refusal.
- **Decision cards.** A turn with `card` saves a note, proposes a team note, creates a task or a meeting. The answer on the card is always the applying one, except where an item says `leave`. A note turn writes the binding in the file's metadata and the note's row; its answer repeats the note in the saved words, as the product does (`docs/features/agent-memory.md:3`).
- **Thumbs** (`ask.feedback`): up on 6 % of answers, down on 1.5 %, the down ones on answers that a correction follows. Hand-written threads carry theirs.
- **Titles** are the titling agent's kind of title: the subject in two to five words, in the thread's language, never the question itself.
- **Note turns in background threads.** A note whose `source` is `auto` gives the kind of thread it joins and the manager's own sentence (`said`); the seeder appends that sentence and one of four acknowledgements to a thread of that kind on the note's day.
- **What the generator renders, and what the files hold.**
  - The files hold the 15 hand-written threads, the patterns (`<lang>/patterns.json`) and the notes (`<lang>/notes.json`).
  - The generator renders at build time, as written above:
    - the 165 background threads: their turns, slots, tool cards, titles and thumbs;
    - the 50 note-source turns per language: the `auto` notes of `notes.json`, each a sentence and an acknowledgement appended to a thread on the note's day.
  - Neither exists as text in the files, so the generator's own test asserts the counts (165 threads and `ask.threads_per_person`; 50 note turns), that every slot resolves as its owner reads it, and that each note turn sits in a thread of its owner on the note's day.
  - Ask threads carry no pictures or voice. The only pool keys of the seed are in the conversations (`../conversations/DESIGN.md` section 5).

### 2.4 What a stored tool result looks like

There is none. The file keeps the card, not the call. So an answer must stand without its rows: every table a manager would want is in the answer text, and every answer ends by naming its source in words ("Source: shop system, paid cash orders"). The seeder writes no query artifact: one written at build time would expire 30 days later and none older than 30 days could exist. This answers review finding 41.

### 2.5 The slot grammar (rule R3)

A text is fixed prose with slots. A slot is resolved by the seeder against the generated data **as of the item's own instant** (a turn's time, a run's due time, a brief's write time) and **as the item's owner reads** (their shops, their history window, their hidden columns: rule R4). A slot whose population reaches outside the owner's reach fails the build.

```
{{<when>|<format>}}                          a date: the knowledge base's own placeholder, plus @now
{{=<metric>|<population>|<period>|<format>}} a computed value; {{$<ledger key>|<format>}} a ledger constant
{{#<block>}}                                 a table or list defined beside the text: one row dimension, each column a value
```

- `<when>`: `@event`, `@now`, `T`, `W-4.mon` (that weekday of week T-4; if closed, the next full open day), `P1`..`P6`, `slot6:-1` (slot 6's last working day before T), each movable by `+3wd:main`, `+0wd:slot7` (the first working day on or after), `-1d`, `+2w`, `-12mo`. It is the grammar of `../kb/OUTLINE.md` section 1 with three bases added, so a date reads the same in a page and in a thread.
- `<metric>` is a key of `metrics.json`: 113 metrics, each with its store and definition (`orders.discounted`, `calls.missed_share`, `roster.gaps`, `catalogue.list_price`).
- `<population>` is `all` or `dimension=value` pairs joined by `&`: `site=west&advisor=F1&pay=cash&min=10`; `!F1` is everyone but F1; `me` is the owner.
- `<period>` is `at` (a state at the instant), a named window (`day`, `prev_day`, `prev_shift`, `week`, `prev_week`, `d30`, `since_prev`) or `<when>..<when>`.
- `<format>`: `int`, `pct`, `pct1`, `money`, `money0`, `dur`, `clock`, `score`, `text`, `names`, and `n:` with the noun's forms, two in English (`n:order/orders`), three in Russian (`n:наряд/наряда/нарядов`). Russian dates have the forms the sentence needs (`on_weekday` «во вторник», `until_day`, `month_gen`); Russian texts avoid a counted noun as a subject, so no verb has to agree with a computed number.
- A story item states what its slots must come to (`expect`, by ledger key and tolerance). A slot outside its expectation fails the build: the card is then changed, never the number by hand.

## 3. Memory

**Classes and scopes.** Personal: `preference` (how the assistant should answer or draft for this person) and `correction` (how to read a word or a figure). Team: `practice`. Nothing else is writable (`B/core/memory/gates.py:28-35`). A note is about how the assistant works with a person or a team; customer facts are on knowledge pages (review finding 25). Every note and proposal in the files passes the product's `gates.reject_candidate`, imported by the check.

**A personal note and its thread.** A note's `source` names a thread and the turn whose card saved it. The loader writes the same uuid on the `conversations` row and in `source_conversation_id`, the binding's ordinal in `source_turn`, the turn's time in `source_at` and `valid_from`. The Memory tab then links the note back into that chat.

**States, and how each arises in history.**

| State | In the row | Arises | Seeded |
|---|---|---|---:|
| active | `state` `active` | saved from a chat; used inside the last 90 days | 52 personal, 13 team |
| dormant | `dormant` | the night found it unused for 90 days; still recallable | 4 (slots 2, 4, 5, 17: habits of the first weeks) |
| unverified | `unverified`, team notes only | the 90-day check came due and nobody answered Keep or Remove | 1 ("Missed callers", due in the last 11 days) |
| archived, deleted | `archived`, no successor, ended by its owner's login | Delete on the Memory tab | 3 (slots 2, 16, 17) |
| archived, replaced ("superseded" is not a state) | `archived` with `superseded_by` | the owner said the opposite in chat (slot 4, "The shop"); the owner reworded it on the Memory page, same source (slot 9); the night tightened a text over 12 words to at most 12 (slot 3) | 3 |

The check interval is a tenant setting of 90 days (`mem.retest_days`; shipped 180), or nothing could come due inside 175 days of product. Five team notes came due and were kept, each leaving a Keep in history. "Unused" archiving needs 180 days without use and cannot have happened yet.

**Proposals.** A manager asks in chat, answers a Propose card, and the row waits. Each proposal sends `memory.proposed` to the seniors and the administrator other than the proposer (slots 1, 2, 4, 22); the first answer decides and sends `memory.decided` to the proposer.

| Life | Count | Which |
|---|---:|---|
| approved and published as a team note | 14 | six designed (S2, S4, kb, three more) and eight that the other team notes require |
| declined with a reason | 2 | slot 6's "read the booking back" (S4, slot 4's reason); slot 24's phone greeting, declined by slot 22 the same day |
| withdrawn | 1 | slot 16's "photo first": `rejected`, decided by herself, the locale's sentence as its reason |
| waiting at T | 2 | slot 6's "company drivers" (S4); the night's "Prices source" |

The night's proposal: slots 6 (in P5), 7 (the day of the S8 discount) and 5 (his last working day before T) each saved a correction with the subject "Prices source" and the same text. The first pass after the third note, at 00:00, raises one proposal with `holders_count` 3, no owner, the count as its reason and middle rank as its floor. It names nobody.

**What each rank sees.** A person sees their own notes and the team notes at or below their rank: a junior 11, a middle 13, a senior and the administrator 14. Seniors and the administrator decide proposals and answer Keep or Remove. Nobody reads another person's notes in Ask; the console's Memory view shows them to the administrator and counts the read.

## 4. Scheduled tasks and briefs

**The seven tasks** are those of `s10.tasks`, with the names the knowledge base uses and schedules the product writes back unchanged (checked through `schedule_words.build` and `parts`). Slot 2 owns four, nobody more. "Discounts over 10 %" is created in the thread of the rule's day; the other six on G. Prompts are in the owner's voice (`tasks.json`).

**What a run stores.** One `cron_runs` row per due time since the task's creation: kind `scheduled`, status `ok`, `started_at` at the due time, 20 to 90 s long, the answer and the instruction as it ran. No task runs more than daily, so 175 rows fit the 200 kept (review finding 42). The run of each task's last due time before T exists, so the scheduler owes nothing at start.

**Six months of answers (rule R3).** Each task has cases, each case one to three wordings (`sched.run_wordings`). A run takes the case its data calls for (a closed day, nothing to report, an unapproved discount) and the next wording in turn, so two neighbouring runs never read alike and the slots make each one different anyway. The first line is written to stand alone: it is what the Inbox shows, cut at 200 characters.

**The failed run and the run again** (S10): the Monday of week T-1, "Company accounts this week", status `failed` at its due time with a reason in words (`s10.failure_reason`); its `scheduled_task.failed` line is settled 65 minutes later by a run of kind `again`, status `ok`, started from the line's Run again, which posts `scheduled_task.ran`.

**Inbox lines.** Every run of the seven posts one line to its owner, with its own time: about 250 for slot 2, 175 each for slots 1, 4 and 6 over the period. Lines older than seven days are read; the junior's "My call backs" of T's morning is unread (design 4.4). A brief posts none.

**Briefs.** Fifteen jobs, one per manager (`sched.brief_jobs`). Run times follow the product: 06:40, 10:40, 14:40 and 18:40 on the home clock for slots 1 and 2, who have no shifts, and for anyone on a day without one; five minutes before the first shift, a third and two thirds of the way through and an hour before the end for everyone else, on their own shop's clock. How many of a day's times run is each person's habit of opening Home (`sched.brief_reads`); the rest are `skipped` rows with the product's own reason. Only the newest 200 rows per job are written, about 50 to 100 days. **At T** each of the four story people has one finished brief, the first of T's brief day, and `skipped` rows for any later time before T, with `brief_seen_at` before the first run: so "what did my brief say this morning" has one answer and Home shows it. The four are written by hand; every other brief takes up to three points from a bank of twenty, each with the condition under which it is said.

## 5. Written by hand, and built from patterns

Per language; the Russian items are written from the cards and the people, not from the English ones.

| Item | Story | Owner | Anchor | Purpose |
|---|---|---|---|---|
| thread `s2-discounts` | S2 | 2 | the 5th full open day after G, evening | the question, the table by advisor, who approved, which customers, what else |
| thread `s2-cost` | S2 | 2 | 5 full open days later | the three components by month as an estimate; a draft to slot 22; her note "Number first" |
| thread `s2-rule` | S2 | 2 | the rule's day | proposes the team note; sets up the Friday list |
| thread `s3-missed-calls` | S3 | 4 | the Monday of week T-4 | when calls are missed; who is on the desk; by desk, not by person; his note; the card for the early shift |
| six threads `s4-...` | S4 | 6 | P1 (two), P2 (two), P3, P5 | where each of her six notes came from |
| three threads `s4-...-proposal` | S4 | 6 | the Mondays of weeks T-6 and T-3; her last working day before T | her three proposals |
| thread `s8-prices-source` | S8 | 7 | the day of the discount | his correction, word for word the others' |
| thread `s12-prices-source` | S12 | 5 | his last working day before T | the third holder; the second stale page named |
| 62 personal note rows | S4, S8, S3, S2 and people | 12 people | each its own | subject, text, why, how, and the sentence that prompted it |
| 14 team notes, 19 proposals | S2, S4, kb | proposers and deciders by name | each its own | the three wordings fixed elsewhere, exact; reasons of the two declines |
| 7 tasks with prompts and run templates | S10, S2, S3 | 1, 2, 4, 6 | G; the rule's day | en 16 cases and 31 wordings; ru 15 and 30 (no Saturday case) |
| 4 briefs at T | S10 | 1, 2, 4, 6 | the first run of T's brief day | three points each, numbers as slots |

Built from patterns:

| Kind | Patterns per language | Gives |
|---|---:|---|
| question patterns in nine kinds, with two wordings each and a follow-up on three | 42 | with the parameters (three shops, people, 70 jobs, six accounts, customers) no person meets one twice |
| refusals by rank and site; "the data cannot tell" | 4 + 2 | the seeded refusals |
| acknowledgements of a saved note; of a proposal | 4 + 1; 3 | the note turns |
| brief points with their conditions | 20 | every brief but the four |

## 6. File formats

| Format | File | Keys |
|---|---|---|
| `seed-ask-thread/1` | `<lang>/threads.json` | `id`, `story`, `owner` {slot, name}, `when`, `at`, `title`, `purpose`, `people` {slot: the name as written}, `kb_facts` [{page, contains}], `turns` [{`n`, `user`, `tools`, `assistant`, `blocks`, `expect`, `feedback`, `card` {tool, answer, note or proposal or task}}] |
| `seed-ask-patterns/1` | `<lang>/patterns.json` | `params`, the shop's name forms, `note_ack`, `propose_ack`, `patterns` [{`id`, `kind`, `ranks` (the lowest rank that may ask), `max_rank`, `tools`, `card`, `subject`, `ask` [two wordings], `answer`, `blocks`, `then`, `valid_from`}] |
| `seed-memory-note/1` | `<lang>/notes.json` | `id` (slot.n), `owner`, `class`, `subject`, `text`, `why`, `how`, `state`, `when`, `last_used`, `source` ({thread, turn} or {auto: kind, said} or {same_as}), `replaces`, `ended` {when, by, superseded_by}, `applies` (the kinds of thread that count as a use) |
| `seed-team-memory/1` | `<lang>/team.json` | `team_notes` [{`id`, `proposal`, the four texts, `visible_from`, `lowered` {from, by, when}, `state`, `approved`, `review` {due, answer, by}}]; `proposals` [{`id`, `designed`, `by` (a person or `nightly`), `holders`, the four texts, `proposed`, `status`, `withdrawn`, `decided`, `decided_by`, `reason`, `published_as`, `source`}] |
| `seed-scheduled-task/1` | `<lang>/tasks.json` | `id`, `owner`, `name`, `schedule` {days, times} (the product's wire shape), `created`, `prompt`, `blocks`, `cases` {case: [wordings]}, `planted_runs`, `expect` |
| `seed-brief/1` | the same file, `briefs` | `jobs_for`, `at_t` [{owner, run, points}], `bank` [{id, for, when, point}] |
| `seed-assistant-metrics/1` | `metrics.json` | metrics, dimensions, periods, formats, events |

A block is `{kind, rows, where, period, columns [[header, value]], order, limit, total, extra_row}`; a column value is a row field or `=metric|population|format`.

## 7. Ledger rows proposed

In `ledger_rows.json`, each with class, mark, reasoning and, for a rate, tolerance and minimum count.

| Key | Value | Class | Mark |
|---|---|---|---|
| `ask.threads` | 180 | X, design 4.6 | fixed |
| `ask.threads_per_person` | 40, 30, 25, 10 and 75 over eleven people | X | fixed |
| `ask.handwritten` | 15 per language | X | fixed |
| `ask.messages_per_thread` | 2 to 12, mean 5.2 | X | rate ± 0.6, min 165 |
| `ask.kind_mix` | the table of 2.2 | X | rate ± 8 points, min 25 |
| `ask.refusals` | 9 refusals, 4 "cannot tell" | X | fixed |
| `ask.feedback` | 6 % up, 1.5 % down | X, range 3 to 10 and 0.5 to 3 | rate ± 2, min 400 |
| `ask.patterns` | 48 per language by kind | X | fixed |
| `mem.personal_live` | 56: 52 active, 4 dormant | X, design 4.5 | fixed |
| `mem.personal_ended` | 6: 3 replaced, 3 deleted | X | fixed |
| `mem.personal_per_person` | twelve holders | X | fixed |
| `mem.team_notes` | 14: 13 active, 1 unverified; from junior 11, middle 2, senior 1 | X | fixed |
| `mem.proposals` | 19: 14 approved, 2 declined, 1 withdrawn, 2 waiting | D: one approval per team note | fixed |
| `mem.retest_days` | 90 | X, a tenant setting | fixed |
| `mem.reviews` | 5 kept, 1 waiting | D | fixed |
| `mem.nightly` | 3 holders, raised the night after the third note | X | fixed |
| `mem.inbox_lines` | proposed 72, decided 16, unverified 24 | D | fixed |
| `sched.brief_jobs` | 15 | X | fixed |
| `sched.brief_times` | the product's rule; 200 rows kept | M, `brief.py:47-50`, `tasks.py:74` | fixed |
| `sched.brief_reads` | briefs a person reads a day | X | fixed |
| `sched.run_wordings` | 2 or 3 per task | X | fixed |
| `sched.runs` | a run per due time | D | scales with T |
| `sched.created` | G; the rule's day for the discounts task | X | fixed |
| `s10.west_plan` | en 60 orders and 29,000 USD a week; ru 57 and 650,000 RUB | X on `volume.norm.west` | fixed |
| `s10.failure_reason` | the reason in words | X | fixed |

## 8. Eval questions this part supports

Asked by a slot and rank (rule R4), with population and period (rule R5). All survive the small size.

| # | Question | Asked by | Population, period, definition | Expected | Proof | Kind |
|---|---|---|---|---|---|---|
| A.1 | Which notes do you keep about how I work? | 6 (junior) | Her live personal notes at T. | Her six, by subject. | `platform.memory` by login | list |
| A.2 | Where did my note about prices come from? | 6 (junior) | The source of "Prices source". | The chat "Front pads and rotors, Camry" in period P5 (date emitted), after an answer quoted "Brake questions". | `source_conversation_id`, the thread | value |
| A.3 | What notes do you keep about Maya? | 7 (junior) | Another person's notes. | Refused: a personal note is its owner's. | `store.visible` | refusal |
| A.4 | What notes do you keep about Maya? | 2 (admin) | The same, asked in Ask. | Refused in Ask; the console's Memory view shows them and counts the read. | no Ask tool reads another login | refusal |
| A.5 | Which team notes can I see? | 6 (junior); 5 (middle); 4 (senior) | Team notes at or below the asker's rank. | 11; 13; 14. The junior does not see "Money in answers", "Declined work" or "Desks, not people". | `min_rank` | list, one answer per asker |
| A.6 | Which three advisors hold the note about price sources? | 4 (senior) | The night's proposal. | The data cannot tell him: the proposal carries a count of three and no names. | `holders_count`, no owner | cannot tell |
| A.7 | What waits for my decision in Memory? | 22 (senior) | Open proposals and unverified team notes at T. | Two proposals (company drivers; price sources) and one note to check ("Missed callers"). The same for slots 1, 2 and 4. | `platform.proposal`, `platform.memory` | list |
| A.8 | Why was Jasmine's note about answering the phone declined? | 2 (admin) | Proposal P08. | Dale Hutchins declined it the day it was proposed: "Folks here know who they called. Not needed." | her Inbox update; the console's proposal history | value |
| A.9 | Do I have a team note waiting for a decision? | 5 (middle) | His own open proposals. | None: his one proposal was approved; the price-source proposal is the night's, not his. | `open_proposals(owner)` | nothing |
| A.10 | What did my note "The shop" say before I changed it? | 4 (senior) | The archived predecessor. | "'The shop' means East Main", replaced on the Wednesday of week T-18. | `superseded_by` | value |
| A.11 | Which of my notes have gone unused? | 2 (admin) | Her dormant notes. | One: "Tables as files", unused for over 90 days, still recallable. | `state` | value |
| A.12 | How often did the Friday list show a discount nobody approved? | 2 (admin) | Runs of "Discounts over 10 %" since the rule. | Twice: the Fridays of weeks T-3 and T-1, Chad Binkley, 12 % each. | `cron_runs` | value |
| A.13 | What did Greg's brief say this morning? | 6 (junior) | Another person's brief. | Refused: she reads her own. | task reads are scoped to the caller | refusal |
| A.14 | Why did I get no second brief today? | 1 (senior) | His brief runs of T's date. | It was skipped: the brief before it had not been opened. | `cron_runs.error_text` | value |
| A.15 | Did all of Claire's reports run last week? | 4 (senior) | Another person's tasks. | Refused: he reads his own ("Tomorrow's gaps in cover"). | the same | refusal |
| A.16 | Is there a team rule about promising a pickup day, and was it kept? | 4 (senior) | Team note "Parts promises"; S8 and S6 after its date. | The note, approved in week T-11; broken by slot 7's same-day promise (S8) and slot 23's promised day (S6). | memory; calls 9 and 15 | explanation |

## 9. Product gaps met (for the owner; outside this plan)

1. A proposal's source is the last turn that saved a personal note in that chat, or nothing (`B/core/tools/workspace/memory/memory_tools.py:398-410`). A proposal made in a chat with no saved note cannot be traced to its chat.
2. A team note proposed by an administrator or a senior is born invisible to the people it is for; someone must lower it by hand. The note the night proposes takes the highest holder's rank, so two of its three holders would not see it.
3. A note's tool dependence is a substring match on tool names (`memory_tools.py:391-395`): a note containing "archive" or "calculator" depends on the tool of that name.
4. A task named in Cyrillic gets the slug `m<id>-task`, then `-2`, `-3` (`tasks.py:88-93`).
5. A failed run's reason reaches its owner only when it does not look like an exception; otherwise the line says to try again (`tasks.py:144-149`). During a source outage the owner cannot learn the cause from the Inbox, and an agent that merely reports the outage ends `ok`.
6. A brief job keeps about 50 days of history when its skipped times count against the 200 rows.
7. A thread older than 30 days cannot show the rows behind its answer, and the file never held the query.
8. The product holds no plan or target; "against plan" lives in a prompt.
9. A thumb on an answer needs a trace id; nothing marks an answer as not produced by a model, and neither `cron_runs` nor `platform.memory` has a field for origin.
10. `proposal_publication_shape` still names a status `published` that cannot occur (`traciora-core.sql:3522-3525`).
11. The team-note check interval is an environment variable, not a console setting.

## Contradictions met in the design, the ledger and the cards

| Where | What | Resolved here as |
|---|---|---|
| card S10, `s10.tasks` | the brief "daily 07:00 / 08:00" for four people | the product's own times; fifteen jobs (`sched.brief_times`, `sched.brief_jobs`) |
| card S10 | "a run on every scheduled day since G" for the briefs | the newest 200 rows per job |
| design 4.5 | fourteen team notes and six approved proposals | nineteen proposals; the eleven of 4.5 are marked `designed` |
| design 4.5 | "superseded" as a state | archived with a successor |
| cards S10 and S02 | every task defined on G; the Friday list "since the rule" | the Friday list is created on the rule's day |
| `kb/CROSS-STORE.md` 1.2, question S2.4 | a note proposed by the administrator, read by a junior | slot 4 lowers it on approval |
| card S04 | the nightly proposal waits "since the night before T" | true when slot 5 works the day before T; when T is a Monday (en) it was raised three nights earlier. The anchor is "the first pass after slot 5's last working day before T" |
| card S10, `s10.failure` | the run "failed because the source could not be reached" | a reason in words that no product path writes today (gap 5) |
| `kb/CROSS-STORE.md` 1 | subjects given for two of six notes | chosen here: "Discount approval", "First call", "Booking read-back", "Company drivers" and their Russian subjects |
| ledger | no plan for the bought shop | `s10.west_plan` |
| card S09, question S9.4 | no note may mention the Monday meeting | the three notes about clocks speak of bookings and deliveries only |

## Not in this plan

- Ask threads of mechanics; threads begun from a board card or a shift.
- A team note removed on its check; a proposal declined from the Inbox with no words.
- Chart artifacts in answers; attachments in threads.
- The usage and cost a run would have had (design 4.7 decides those numbers).
- Name forms for Russian patterns that inflect a person's name: the patterns are built so that none is needed.
