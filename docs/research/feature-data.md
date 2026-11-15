Read-only sweep done. Nothing edited, nothing run. Paths below are relative to the product's checkout. B = apps/backend/src/traciora. "not found" means I looked and did not find it.

## 1. Ranks and positions
- **Ladder shipped** (`config/defaults/access_levels.json:4-39`). Each step is key, rank, scope, name:
  - customer, 0, customer
  - technician, 1, worker
  - junior, 2, junior ("Junior manager")
  - middle, 3, middle
  - senior, 4, senior
  - admin, 5, admin ("Administrator")
- **Rules for steps.** Rank must be unique and scopes must never run backwards (`B/core/auth/access_ladder.py:138-164`). At least one step must have scope admin (`:164`). `core.access_level` is reconciled from this file at bootstrap (`B/core/core_db/bootstrap.py:88,114-162`). The ladder is replaceable per tenant.
- **Per-rank overlay** is `config/defaults/access_limits.json:3-16`. History windows: technician 180 days, junior 180, middle 365, senior null (whole history). Name, icon, description and console sections are also stored there (`access_ladder.py:41-46`). Non-admin steps must have an entry. No `console` list ships, so by default no non-admin step opens any console section.
- **Admin** is user-type SENIOR for tools (`access_ladder.py:240-251`). Admin opens every console section: overview, alerts, integrations, jobs, ai, experience, analytics, content, models, users, settings, job_roles (`B/core/auth/permissions.py:25-28`; `access_ladder.py:74-77`).
- **Tool floors** from `B/core/tools/tool_catalog.py:467-515`:
  - Worker: calendar tools, inbox tools, feedback, the "furniture" utilities, `my_schedule`, `request_shift_change`, `my_day`.
  - Junior and up: board, scheduled tasks, web, sandbox, memory (propose), roster read tools, data tools.
  - Senior only: `get_ai_usage_overview` (`B/core/tools/utilities/registration.py:339-342`), memory `decide_team_note` and `review_team_note` (`B/core/tools/workspace/memory/registration.py:40-60`), `plan_shifts`, which means planning the rota (`tool_catalog.py:507`; `B/core/tools/workspace/roster/access.py:15-34`).
  - Phone performance across colleagues defaults to senior (`TRACIORA_PHONECALLS_PERFORMANCE_RANK`, `docs/features/call-pipeline.md:262-266`).
  - Conversations stats: Now block for every manager, period and operator blocks from middle (`docs/features/conversations.md:490-496`).
  - Knowledge and Conversations screens: junior and up (`B/core/tools/tool_policy.py:128-137`).
- **Worker screens**: Home, Shifts, Ask, Calendar, plus the Inbox bell (`docs/features/home.md:166-171`, `docs/features/inbox.md:11-14`).
  - A worker is never offered board work and never appears in a manager's team list (`config/defaults/access_levels.json:2`).
  - A worker has no board and does not get handover lines (`docs/features/escalation.md:117-127`).
  - A worker's Home shows "For you" instead of "Needs you" and has no brief (`docs/features/home.md:8-11,55`).
  - A worker's calendar is their own, and clash answers show only "busy" (`docs/features/calendar.md:36-40,95-99`).
- **Admin vs senior**: admin gets the console and all its sections, plus Users → Roles, where ranks, job roles and the knowledge "Sync ranks" are edited. Admin also reads `everything` on built-in data sources, one rank above senior (`B/core/tools/data/registration.py:84`; `docs/features/data-layer.md:171-173`).
- **Positions**: no `core.position` rows are shipped. I found no insert in the schema or in `bootstrap.py`. Positions are created as the business's "job roles" in the console (Users → Roles → Job roles). The commands are `B/core/commands/roster.py:1383` (`upsert_position`), `:1429` (`retire_position`), `:1453` (`set_person_postings`) and `B/core/commands/people.py:22` (`position_id`).
  - Fields: name (unique), colour (hex), sequence, active (`apps/backend/schema/traciora-core.sql:512-553`).
  - A person's jobs at a site are `identity.person_location` rows (`:699`).

## 2. Home
- It is one read, `GET /api/manager/home`, composed in `B/core/tools/workspace/home_sql.py`. Panels (`docs/features/home.md:36-43`):
  - `greeting`: name from the person record, plus a "welcome back" summary.
  - `shift`: state before, late, on, done or off, with today's shifts, the next shift, an open change request, a forgotten clock-out, and who is on with you.
  - `needs_you`: the Inbox "act" lines.
  - `brief`: up to three points, from a scheduled prompt job.
  - `away`: Inbox "ran" lines since the last shift ended.
  - `day`: shift, diary entries and what is due.
- **Tables behind it**: `workforce.shift` and `workforce.punch`, `work.work_item` and `work.calendar_event` via `person_day` and `my_schedule`, `platform.notification_queue` and `platform.activity` via the Inbox lines, and auth.db `cron_prompt_jobs` and `cron_runs` for the brief.
- **By rank**: a planner (senior) also sees unfilled required places from the coverage rows (`home.md:51-53`). A worker sees invitations and answers to their own change requests. The brief needs scheduled tasks to be on and the step to be allowed to own them.
- **Calls to return are not on Home.** I found no call or missed-call read in `home_sql.py`.
- **Clock in and out**: `POST /api/manager/home/punch` calls `commands.roster.punch` (`B/core/commands/roster.py:249`). A punch is never refused. `exception_type` is time, location, network or missing, and the check-in radius comes from `core.location.checkin_radius_m` (`roster.py:336`).
- **Forgotten clock-out**: `home_sql.fix_clock_out` writes a punch with producer `web_correction` and pushes a `punch.corrected` update to the site's seniors and admins (`home_sql.py:481`).

## 3. Inbox and notifications
- **Tray is derived.** Seven sources (`docs/features/inbox.md:99-110`):
  - `activity`: `platform.activity`
  - `diary`: `work.calendar_event_participant`
  - `rota`: `workforce.shift` (and its publishes)
  - `due`: `work.work_item.due_at`
  - `rota_news`: `workforce.shift_change_request`
  - `handover`: a card resting on a `customer.handover_requested` event
  - `notice`: pushed notification rows
- **A row reaches `platform.notification_queue` in two ways.**
  - On first read, `B/core/commands/notifications/inbox.py:53` `mark_read` writes one row under type `board.inbox` with key `<person>:<line key>`.
  - Pushed lines go through `inbox.py:87` `push` (in-app, sent and delivered immediately, text sealed into `context_enc`). `push` then calls `service.notify` (`B/core/commands/notifications/service.py:12`), which also writes `platform.notification_alert` (the 62nd table) and, if the person has opted in, push rows via `queue.enqueue` (`queue.py:83`).
- **`platform.notification_type` rows shipped** (`B/core/packs.py:269-327`, seeded by `bootstrap.py:256`):
  - `board.inbox` (in_app): read state of derived lines.
  - `calendar.google_lost` (in_app): the Google grant was refused. Goes to that person.
  - `scheduled_task.ran`, `scheduled_task.failed`, `scheduled_task.removed` (in_app): raised by `tasks.py:353-415` for the task owner (removed is raised when an admin deletes the task).
  - `board.quiet` (in_app): the nightly card pass (`commands/nudges.py`). Goes to the owner, or the site's seniors if unowned.
  - `board.given` (in_app): a batch hand-out, one line per person.
  - `memory.proposed` goes to seniors and admins. `memory.decided` goes to the proposer. `memory.unverified` goes to seniors.
  - `punch.corrected` (in_app): a forgotten clock-out fixed. Goes to site seniors and admins.
  - `tool.proposed` (in_app): an MCP-proposed write, waiting in the proposer's own Needs you (`B/core/agents/proposed_calls.py:52`).
  - `knowledge.proposed` goes to the engine's deciders. `knowledge.decided` goes to the proposer.
  - `conversation.new` goes to every manager. `conversation.message` goes to the chat's owner. `conversation.mention` goes to the person named.
  - `ops.alert` (push): error or critical operations alerts. Goes to everyone who may open console Alerts.
  - `ops.feedback`, `ops.data_sharing` (server): no person recipient.
  - `push.canary` (push): once a day per phone, at the first app open after 09:00.
  - `utility.timer` (push).
  - `task.assigned`, `task.mention` (producer: `B/core/commands/notifications/producers.py:8`; payload is built in `service.py`).
  - `assistant.completed` (producer: `answers.py:26`).
- **Related tables**: `platform.notification_setting` (per person, type and channel, with quiet hours) and `platform.push_subscription`. A channel is one of in_app, sms, push, chat or server.

## 4. Task board
- **Columns** (`config/defaults/work_states.json:4-8`): Backlog (backlog), To do (unstarted, default), In progress (started), Done (completed), Cancelled (cancelled). The group set is backlog, unstarted, started, completed, cancelled, triage (`schema:2296+`). One default row only (`work_state_one_default_idx`).
- **`work.work_item`** (`schema:2485+`): `kind` is task, follow_up, escalation or other. `priority` is low, normal, high or urgent. Other fields: `title_enc` plus tokens, `description_enc`, `state_id`, `owner_id`, `location_id`, `due_local`/`due_tz`/`due_at` (due fields come as a pair), `sort_order`, `interaction_id`, `work_item_template_id`, `origin` (model, human, connector, template, api, migration), `origin_ref`, `reason_text_enc` (the "why now" line).
- **`work.work_participant`**: role is `participant` (helper) or `observer` (watcher). The owner is `owner_id`. Optional `personal_lane` is today, later or waiting. `completed_at` and `completed_by` mark each person's own part.
- **`work.work_item_source`**: links a card to events, with role trigger, evidence or context.
- **Templates** (`config/defaults/automations.json`): "Customer handover" (high priority) and "Missed call callback" (normal). Both are pack `core`. They are seeded once by `bootstrap.py:239+`.
- **How a task is raised:**
  - Manager by form: `POST /api/manager/board/tasks`, calling `board_sql.create_task` (`B/core/tools/workspace/board/board_sql.py:333`).
  - Assistant: the same `create_task` tool, behind a decision card. Also `assign_batch` (`:499`) and `plan_work`.
  - Call claim: `B/core/phonecalls/claims.py:84-134`. It writes `work.upsert_work_item` with kind `follow_up`, origin `human`, `origin_ref` `calls:claim`, in the started column, owned by the claimer, with `interaction_id` set to the missed call. It lapses after 30 minutes.
  - Escalation or handover: `B/core/tools/utilities/escalation_tools.py:138` `raise_handover_card`. It writes kind `escalation` at high priority (or `task` at normal for a `scheduling` request), unowned, in the first backlog column, origin `model`, `origin_ref` `chat:<session>`, due at close of business. It also emits a `platform.event` `customer.handover_requested` and links it as trigger (`docs/features/escalation.md:64-107`).
- **Commands** in `B/core/commands/work.py`: `upsert_work_item:189`, `edit_work_item:261`, `assign_work_item:383`, `move_work_item:471`, `complete_work_item:491`, `comment_on_work_item:500`, `mark_part:546`, `keep_work_item:573`, `add_work_participant:589`, `remove_work_participant:610`, `set_personal_lane:654`, `link_work_item_source:667`, `attach_file:1123`.
  - Helpers for states are `group_state:151` and `default_state:130`.
  - Tools in `board_sql.py`: `edit_task:415`, `move_task:622`, `comment_task:817`, `mark_part:672`, `keep_task:706`.
- **Rules**: the owner closes the card (`owner_closes`). Urgent is rationed per site (`TRACIORA_BOARD_URGENT_LIMIT`, default 3, with `step_down`). A card is quiet after `TRACIORA_BOARD_QUIET_DAYS` (default 7). Work may be put on yourself or on lower ranks only (`docs/features/task-board.md:28-37,61-73`).
- **`platform.activity` for a card** (`schema:3090+`):
  - Columns: `subject_type`='work_item', `subject_id`, `group_id`, `verb`, field with old/new values, `actor_kind`, `via` (ui, api, agent, connector, migration, system), `origin`, `utterance_enc`, `payload_enc`, `event_id`, `occurred_at`.
  - Verbs: created, assigned, moved, reopened, completed, cancelled, comment (body in `payload_enc`, mentions in `payload_public`), part_done, part_reopened, kept, attached, detached, and field edits (retitled, described, reasoned, reprioritised, rescheduled, resited) (`task-board.md:57-59,226-228,247`).
  - A move also writes a `platform.event`: `work_item.created`, `.assigned`, `.state_changed`, `.completed` (`packs.py:107-139`).

## 5. Calendar
- **`work.calendar_event.kind`** is meeting, block, personal or external (`schema:2618+`).
  - A `block` always has a `work_item_id`, and a block is the only kind that may have one (`calendar_event_block_shape`).
  - `external` is imported from Google, read-only, with no series and no interaction.
  - `show_as` is busy, tentative, out_of_office or free.
  - Other fields: `all_day`, `cancelled_at`, `series_id`, `occurrence_key`, `interaction_id` (a recorded meeting).
- **Recurrence**:
  - `work.event_series` (`rrule`, `starts_on`, `ends_on`, `materialise_horizon_days` 1-730, `materialised_through`) and `work.event_series_exception` (cancel or replace, with the replacement times).
  - The product's repeat words are daily, weekdays, weekly, fortnightly, monthly. `create_event_series` writes every occurrence up front, to `until` or a year ahead (`docs/features/calendar.md:95-120,206-211`).
- **Invitations**: `work.calendar_event_participant` has role `required` or `optional`, response `invited`, `accepted`, `declined` or `tentative` (`responded_at` is null only while invited), and `attended` (boolean).
- **Commands** in `B/core/commands/work.py`: `upsert_calendar_event:685`, `create_event_series:786`, `end_event_series:797`, `except_occurrence:811`, `cancel_calendar_event:856`, `edit_calendar_event:923`, `invite:1009`, `uninvite:989`, `respond:1023`, `close_meeting:1057` (creates the meeting's `interactions.interaction` with channel meeting), `record_attendance:1099`.
- **Tools**: `schedule_meeting`, `edit_meeting`, `cancel_meeting`, `respond_meeting`, `block_time`, `show_calendar`, `my_day`, `check_availability`, `find_free_slot`, `show_meeting`, `invitable`.
- **Google sync tables**: `work.calendar_sync` (one per person, vault entry), `calendar_sync_calendar`, `calendar_event_ref`.
- **Events**: `calendar_event.scheduled`, `.rescheduled`, `.cancelled`, `.responded` and `calendar.google_imported` (`packs.py:159-201`).

## 6. Shift planner and roster
- **Tables** (`schema:1715-2296`):
  - `workforce.shift_template`: name, location, position, start and end times, `break_minutes`, `begin_check_in_before_min`, `allow_check_out_after_min`, `late_entry_grace_min`, `early_exit_grace_min`.
  - `workforce.coverage_requirement`: location, position, `day_mask` (bit(7)), times, `min_count`, `required`, validity dates.
  - `workforce.shift_schedule` (rotation): template, person, `rrule`, `valid_from`, `valid_to`, `materialise_horizon_days` (default 42).
  - `workforce.shift`: `status` is draft, published or cancelled. `confirm_status` is not_required, required, confirmed or declined. A person may not have overlapping shifts (an exclusion constraint). A null `person_id` is an open shift.
  - `workforce.roster_publish`: range, `published_by` (a person), `diff_public` and `diff_enc`.
  - `workforce.availability`: kind is unavailable, undesired or desired, with either `day_mask` or `on_date`.
  - `workforce.shift_change_request`: kind is change_time, change_date or remove. Status is open, approved, declined, withdrawn or expired.
  - `workforce.punch`: `log_type` in or out. `exception_type` is none, time, location, network or missing. Also `offshift`, `geo_distance_m`, `coordinates_enc`, `note_enc`, producer plus `producer_punch_id` (unique).
- **Commands** in `B/core/commands/roster.py`:
  - Shift templates and publishes: `upsert_shift_template:68`, `publish_roster:75`.
  - Shifts: `upsert_shift:89`, `publish_shift:98` (the demo path; one shift is published individually), `draft_shift:491`, `move_shift:515`, `cancel_shift:147`, `copy_week:1191`.
  - Publishing a week: `publish_week:632`, with `pending_publish:719` for the preview.
  - Planning inputs: `set_requirements:847`, `set_availability:883`.
  - Change requests: `file_change_request:905`, `decide_change_request:1011`, `withdraw_change_request:1165`, `expire_change_requests:1125`.
  - Rotations: `materialise_schedules:1299`. The rotation row itself is inserted in `B/core/tools/workspace/roster/rotations.py:69`.
  - Punches: `punch:249`, `record_punch:203`, `flag_no_shows:375`. Check-in radius is `commands/locations.py:195` `set_location_checkin`, and `punch` compares against `latitude`/`longitude`/`checkin_radius_m` on `core.location`.
- **Who can do what**:
  - Plan (draft, move, cancel, publish, requirements, postings, decide requests): the `plan_shifts` audience, senior by default. The gate is `roster/access.py:15-34`, and a login must be linked to a person.
  - Everyone else: own published week via `my_schedule`, plus `request_shift_change` and `withdraw_request`.
  - Below senior the grid is read-only, narrowed to the sites where they work that week.
  - Past days are read-only through the screens and tools (`_refuse_passed`). The commands stay open.
- **Built-in jobs**: `roster_materialise` (daily) and `attendance_no_shows` (every 15 minutes) (`docs/features/roster.md:150-158`).
- **A staffed site** is required for planning (`core.location.staffed`).

## 7. Scheduled AI tasks
- **Not in the core DB.** They live in auth.db table `cron_prompt_jobs` (`B/core/auth/manager.py:322-336`): `slug`, `name`, `cron_expr`, `prompt_text` (sealed), `output_kind`, `output_chat_id`, `enabled`, `created_by` (manager id), `config_version`. Writers are `cron_store.create_prompt_job` (`B/core/scheduling/cron_store.py:413`) and the tool `schedule_task` (`B/core/tools/workspace/scheduled_tasks/tasks.py:612+`).
- **Schedule** is times plus days, built by `schedule_words.build`. Several times are stored as crontabs joined with `;`. The owner is `created_by`.
- **Limits** (`tasks.py:67-69`): 10 tasks per manager (the brief is not counted), at least 30 minutes between runs, 4000-character prompt, unique name per owner (case-insensitive). The floor is junior (`SCREENS` in `tool_policy.py`).
- **Delivery is `output_kind="store"`** (`tasks.py:460,719`). The result goes into `cron_runs` (`manager.py:376`): `task_slug`, `owner_id`, `kind` (scheduled, late, again, trial), `status` (running, ok, failed, not_run, skipped), `due_at`, `started_at`, `finished_at`, `answer_enc`, `instruction_enc`, `cost_usd`, `tokens`. `record_run` (`tasks.py:353`) pushes a `scheduled_task.ran` or `scheduled_task.failed` line to the owner's Inbox (trial runs push nothing). The newest 200 runs per task are kept.
- **The brief** is one hidden job per manager, slug `brief-<manager id>` (`ensure_brief`, `tasks.py:441`).
- **Other cron tables**: `cron_job_overrides`, `cron_run_requests`, `cron_job_status`.

## 8. Conversations
- **Channels as Chatwoot bridges** (`B/core/channels/chatwoot/`): `chat` (the product's own web chat, `chat_bridge.py:29`), `telegram` (`telegram_bridge.py:125`), `vk` (`vk_bridge.py:123`), `avito` (`avito_bridge.py:95`). The bridge key is `<slug>:<account>`. Bridge switches are `CHATWOOT_{VK,AVITO,TELEGRAM,CHAT}_BRIDGE_ENABLED` (`docs/features/chatwoot.md:21-27`).
- **Where data lives**:
  - The record is Chatwoot's own Postgres DB (contacts, conversations, messages, labels, assignee, priority field). Nothing in the core DB's 62 tables holds chat messages.
  - Our side is in auth.db, never the record:
    - `conversation_state`: cache of the open and pending chats, plus the base priority, `arrived_closed` and `owner_since`.
    - `conversation_draft` and `draft_outcome`: the assistant's draft. Outcomes are `sent_as_is`, `sent_edited`, `discarded` or `replaced_unseen`.
    - `compose_text` and `agent_turn` (`conversations_store.py:182-204`).
    - `bridge_inbound`, `bridge_outbound` and `bridge_threads` (`relay_store.py`).
  - Cached last-message text and drafts are encrypted.
- **Priority**: low, normal, high or urgent. The shown level is the higher of the manager's base and the wait's level. Chatwoot's one priority field holds the shown level. The base lives only in `conversation_state` (`docs/features/conversations.md:282-300`).
- **`interactions.interaction` for a chat**: the schema allows `channel` in call, chat, web, social, visit, email and meeting. The product code writes interactions only for phone calls (`B/core/phonecalls/ingestion/`) and recorded meetings (`work.py:1057-1094`). I found no product code that writes a chat interaction. `core/commands/interactions.py:50` `record_contact` is generic and is what `demo_factory` uses.
- **Assistant modes**: per channel `CHATWOOT_<SLUG>_ASSISTANT` is off, drafts or sends. `chat` and `telegram` default to sends, and `vk` and `avito` default to drafts (`conversations.md:375-385`). A `sends` chat stays `pending`, shown with the "Agent" mark. A chat that is owned or carries `handoff` always gets drafts.
- **Hand-off**: `forward_to_manager` leads to `conversations.hand_off`. It posts a private note, adds the `handoff` label and opens the chat in New. If Chatwoot does not answer, it is retried from `handoff_owed`.
- **Stats**: `GET /stats` and `/stats/access`, built from `channels/chatwoot/stats.py` and `stats_blocks.py` over four views in Chatwoot's `traciora` schema (`conversation_facts`, `message_facts`, `reply_episodes`, `resolutions`) plus `draft_outcome`. The data tools can also read these views through the built-in `chatwoot` source. I found no dedicated agent tool for conversation stats.

## 9. Calls
- **One finished call** (`schema:757-1650`):
  - `interactions.interaction`: `channel`='call', `direction` (inbound, outbound, internal, unknown), `state` (open, snoozed, closed), `started_at`, `ended_at`, `answered_at`, `duration_s`, `location_id`, `person_id`, `person_confidence_tier`, `attributed_by` (pbx_extension, login_session, roster, speaker_id, manual, connector, unknown), `disposition` (booked, unbooked, excused, no_answer, unknown).
  - `interaction_participant`: role handler or observer.
  - `media_object`: kind `recording`. A transcript needs a `media_id` row, but `storage_ref_enc` may be null.
  - `transcript`: engine, version, language, text, `pii_state`, `is_current`.
  - `transcript_segment`: `sequence`, timing, `speaker_label`, text.
  - `interaction_analysis`: `kind` is rubric, scorecard, summary, flags, topics, disposition, csat or other. It holds `result_public`, `result_enc`, `score` and `is_current`.
  - `recording_job`: provider plus external token, `ingest_status`, `processing_status`, `source_window_date`.
  - `recording_run`: `run_kind` and status.
  - `recording_export`: unique on provider plus day, status pending, succeeded or failed.
  - `call_leg`: status answered, no_answer, busy or failed, plus `ring_s`, `talk_s`, `extension`, `line`, `location_id`.
  - `missed_call`: state waiting, called_back or got_through, with `resolved_by_interaction_id`, `attempts`, `out_of_hours`, `dismissed_at`.
  - `phone_day_report`: per person or extension and day, with `text_enc`, `highlights`, `scorecard_version`.
- **Scorecard result** (`B/core/phonecalls/judge.py:95-120`):
  - `result_public` has `scheme`, `scorecard`, `weights`, `judged`, `call_type`, `line`, `checks` (key, level 0/1/2, segment), `na`, `unverified`, `not_applicable`, `auto_fails` (key, segment), `outcome`, `no_visit_reason`, `tags`, `score`, `applicable`, `asr_quality`, `strength_segment`, `try_next_check`.
  - `result_enc` seals the quotes, N/A reasons, strength and `try_next`.
  - `score` is `100·Σ(weight·level/2)/Σweight`. It is null under 3 scored checks. Bands: strong from 70, weak under 40.
  - The default rubric is `config/defaults/phonecalls_scorecard.json`. Checks: greeting, name_and_number, need_discovery, price_with_next_step, offered_time, asked_for_booking, recap, objection. Auto-fails: wrong_promise, dropped_customer, callback_not_kept. Outcomes: visit_agreed, callback_promised, customer_will_call, no_visit. Call types: new_enquiry, existing_job, supplier, wrong_number, other. 13 tags.
  - The analysis `prompt_version` is `scorecard:<v>|prompt:<digest>`.
- **Attribution**:
  - Site: extension to `core.location_alias` (namespace `pbx_extension`), set by `commands/locations.py:160` `set_location_extensions` (`B/core/phonecalls/ingestion/repository.py:1139`; `claims.py:63`). A line is matched through the same alias.
  - Person: `roster.handler_on_duty` (`B/core/commands/roster.py:428`) writes `attributed_by='roster'` with tier 3, 2 or 1 (open clock-in, then confirmed shift, then merely planned) (`docs/features/call-pipeline.md:62-76`).
- **Callback queue**: the `missed_call` rows in state `waiting`, listed by `GET /api/calls/queue`. A claim creates a board card (see item 4). Dismiss records `dismissed_by` and `dismissed_at`.
- **Audio is not required.** The sheet draws a player only when `audio` is true, otherwise nothing (`B/core/phonecalls/call_reads.py:440-472`; `call-pipeline.md:~395`). Transcript, verdict and the Calls list work without audio. The transcript row must point to a `media_object`.
- **Transcript search**: words use pg_trgm `word_similarity` on `transcript_segment.text`, for current transcripts only. A query of 5 or more digits is a phone-token match on `call_leg.caller_token` or `callee_token` (`call-pipeline.md:~340`).

## 10. Memory
- **`platform.memory`** (`schema:3344+`): `memory_class` is preference, correction or practice. `scope` is personal (has `login_id`, `min_rank` null) or business (no `login_id`, `min_rank` and approver set). `state` is active, unverified, dormant or archived. Other fields: `subject`, `text`, `why`, `how_to_apply` (all sealed), `tools_referenced`, `release_sha_written`, `source_conversation_id`, `source_turn` (>0), `source_at`, `last_confirmed_at`, `next_retest_at`, `use_count`, `superseded_by`.
  - A personal note must have `source_conversation_id` and `source_at` (`memory_personal_has_provenance`).
  - Only one live row per scope, class and subject.
- **Visibility**: personal notes are the owner's. Team notes (business scope) are visible at or above `min_rank`. The console Memory view is admin-only and logs an audit entry on a nonempty read (`docs/features/agent-memory.md`).
- **`platform.proposal`** life cycle: `proposed` then `approved` (`published_as`=`memory:<id>` and `published_at` set) or `rejected` (decline, with a reason). Proposer rank, `min_rank`, `holders_count` and `dream_night` (for nightly proposals) are on the row (`B/core/commands/memory.py:244-300`).
  - A proposal can also be withdrawn by its proposer (`commands/memory.py:301`).
  - A proposer cannot approve their own, unless there is no other decider.
- **Writers** in `B/core/memory/store.py`: `write_personal:97`, `archive:252`, `change_personal:270`. In `B/core/commands/memory.py`: `propose:161`, `propose_from_count:173` (nightly dream), `decide:244`, `withdraw:301`, `review:322`, `set_min_rank:352`.
- **Tools**: `recall_memory`, `remember_note` (all managers), `propose_team_note` (all managers), `decide_team_note` and `review_team_note` (senior).
- **Memory screen** (doc): decisions waiting, "Proposed by you", personal notes, team notes at your rank, and the Changes log. I did not find tabs named in `MemoryPage.tsx`; the page uses sections.
- **Provenance** (`B/core/memory/provenance.py`): `bind_published_turn` binds the conversation and turn.

## 11. Knowledge base
- **It lives in a separate engine** (mnemosyne), reached over the Unix socket `MNEMOSYNE_SOCKET` with credentials in `MNEMOSYNE_CREDENTIALS` (`B/core/content/knowledge.py:1-30`). It is not in the core DB or the tenant folder after import. A feature grant is needed (`TRACIORA_FEATURE_KNOWLEDGE`).
- **Import**: `python -m traciora.cli.knowledge import --client-id ID [--if-empty]` (`B/cli/knowledge.py`; `B/core/commands/knowledge_import.py`).
  - It takes `runtime/tenant/<id>/knowledge_base/` into the engine root and `playbooks/` into the `playbooks` folder (pinned at admin).
  - Batches are 32 entries, conflict policy `skip`, files up to 16 MiB. It runs once, marked by `imported.json`.
  - `traciora start` runs it with `--if-empty`. The `config/tenant-template/knowledge_base` and `playbooks` folders are empty.
- **Formats**: Markdown pages and binaries. `kb_read` returns binaries as extracted text with page or slide locators (`kb_tools.py:828`). I found no format list beyond that.
- **Search**: the engine's `find` and keyword `search`, with typos allowed (`docs/guides/knowledge-base.md:252`). I found no vector index in the product code.
- **Tools** (`B/core/tools/retrieval/knowledge/kb_tools.py:826-835`): `kb_overview`, `kb_search`, `kb_read`, `kb_links`, `kb_history` (staff only), `kb_suggest` (staff only, junior and up; the person publishes or proposes the change on a card). Proposal notifications are `knowledge.proposed` and `knowledge.decided`.
- **Product help pages** are separate: `config/knowledge/traciora/<lang>/…`.

## 12. Manager chat (Ask)
- **Two stores.**
  - auth.db `conversations` (`manager.py:245`): `id`, `manager_id`, `title`, `created_at`, plus `model`, `subject_json`, `replied_at`, `read_at`, `title_set_by_person`. Also `deleted_conversations`.
  - Messages are not in a table. They are one file per conversation, `user_<conversation_id>.json`, under `paths.chat_memory_dir()` (the runtime `chat_memory` folder), written by `FileBasedMemory` (`B/core/agents/agent_memory.py:141-215`).
- **Message file content**: LangChain Human, AI, Tool and System messages with `timestamp`, `kind` and `turn_id`. The file is encrypted with `MEMORY_ENCRYPTION_KEY`. Also stored in the file: answer traces and feedback thumbs (`ANSWER_TRACES_KEY`, `ANSWER_FEEDBACK_KEY`).
- **A seed needs both** a `conversations` row and the file.
- **Customer sessions use the same file store**, with `customer_conversation_owner` in auth.db.

## 13. Connected data source
- **Declaration**: `runtime/config/sources.json`, schema `config/schemas/sources.schema.json`. Per entry: `name` (`^[a-z][a-z0-9_]{0,30}$`), `kind` (`postgres` or `mssql` only), `include` and `exclude` globs, and `access` per rank (worker, junior, middle, senior, admin) built from everything, schemas, tables with `denied_columns`, patterns and views. Optional `system` (starter notes: netix, chatwoot or traciora).
  - DSN and restore secrets go in the vault under `source/<name>`.
- **Console**: Data sources page (admin only). CLI: `python -m traciora.cli.sources --client-id T add --name N --kind postgres` (also `test`, `list`, `remove`, `builtin`) (`docs/features/data-layer.md:7-60,185-200`).
- **MySQL is not supported.** The kind enum is postgres and mssql only, and `B/data/sources/guard.py:20` lists `mysql_query` only as a name.
- **Context files**: `python -m traciora.cli.context sync --client-id T [--source N --select 'schema.table*']`. Per table it writes `columns.md`, `preview.md` (10 rows) and `profiling.md` (weekly) under `runtime/tenant/<id>/context/sources/<source>/<schema>/<table>/`. Hand-written, never overwritten: `annotations.md`, `RULES.md` at root and at source level, `metrics/`, `skills/`. The scheduler runs it daily at `TRACIORA_CONTEXT_SYNC_AT` (default 05:30). Product seeds are in `config/sources/{netix,chatwoot,traciora}/`.
- **Rank limits**: only the tables and columns the rank's access ticks are readable. A rank also reads what ranks below it read. A table no rank ticks is read by nobody. A column in `denied_columns` is hidden. Views are reached only when named. Enforced by `B/data/sources/access.py` and `B/core/tools/data/registration.py`.
  - The built-in `core` source grants phone call views from junior and day reports from senior. Admin reads everything on it.
  - Workers get no data tools at all.

## 14. Console pieces that would look empty
- **Alerts**: `platform.alert` (`schema:3582`): severity info, warning, error or critical, `category` security or operations (operations needs `rule_id` and `fingerprint`), `status`, `occurrences`, `muted_until`. Write path is `B/core/commands/operations.py:409` `raise_alert` and `:476-499` (acknowledge, mute, dismiss). auth.db also has a `security_alerts` table (`manager.py:190`), which I did not read.
- **Job runs**: `platform.job_run` (`job_id`, `process`, `started_at`, `outcome` ok, ok_empty, failed or skipped, `work_units`, `error_enc`). Written by `operations.start_run:215` and `settle_run:224` (`record_job_run:284`). The built-in job list comes from `commands/builtin_jobs.py`.
- **Usage**: `platform.usage_event` (written by `commands/usage_events.py:39` `record`), `platform.metric_rollup` (`commands/metric_rollups.py:23` `write`; period hour, day or week), and `reply_costs` in a SQLite store (`B/core/models/reply_cost.py`).
- **Feedback reports**: `platform.feedback_report`, written by `operations.record_feedback:563` and moved with `set_feedback_status:662`. Category is bug, slow, wrong_answer, notifications, missing_feature, confusing, praise or other. Severity is blocks_work, annoying or suggestion. Status is open, seen, resolved or wont_fix.
- **PII access log**: `platform.pii_access_log`, written by `B/core/queries/scope.py:189` (`pii_access`). Purpose is call_lookup, display, self_service, export, erasure, connector, analysis or knowledge_history.
- Also: `platform.config_version` (versioned configuration), `platform.push_subscription`.

## 15. demo_factory (only what was asked)
- **`demo_factory/originate.py`** calls, from `traciora.core.commands.*`:
  - `locations.originate_location`, `set_location_hours`, `set_location_checkin`.
  - `people.position_id`, `upsert_person_by_id`, `post_person`.
  - `logins.upsert_login`, `retire_login`, `login_for_username`, `auth_reference`.
  - `roster.upsert_shift_template`, `publish_roster`, `upsert_shift`, `draft_shift`, `record_punch`, `set_requirements`, `set_availability`, `file_change_request`, `decide_change_request`, `expire_change_requests`, `move_shift`, `publish_shift`.
  - `interactions.record_contact`, `add_participant`, `attach_media`, `upsert_transcript`, `append_segments`, `record_analysis`.
  - `work.upsert_calendar_event`, `cancel_calendar_event`, `invite`, `respond`, `record_attendance`.
  - `rows.insert` for `core.location_alias` (namespaces `config_key` and `pbx_extension`).
  - Also AuthManager `create_manager`.
- **`demo_factory/work_layer.py`**:
  - `traciora.core.tools.utilities.escalation_tools.raise_handover_card`.
  - `traciora.core.tools.workspace.scheduled_tasks.tasks.make_tools(...)["schedule_task"]`, with `CronStore`.
  - `history.close_old_cards` (not in the product).
- **`tenant_binding.at`** (`B/core/security/tenant_binding.py:155-173`): a context manager that fixes the trusted instant, which `tenant_binding.now()` returns, for the current thread/task. It needs a timezone-aware instant. Every command reads `now()`, so a card's `created_at`, its event and its activity row all take that time. `originate.py:326-336` uses it to approve a change request in the past. `work_layer.py:124` uses it when raising a handover card at the chat's own time.

## 16. Tables not covered above, and what they belong to
- `core.actor`: audit identity for every writer (system, login, agent, connector, api, migration).
- `core.tenant`: the tenant record.
- `core.location`: sites. Fields include `tz`, `business_hours`, `checkin_radius_m`, `staffed`.
- `core.location_hours_exception`: closures or special hours per date. Written by `commands/locations.py:119` `set_location_hours_exception`. Affects the calendar, call out-of-hours flags and conversation wait priority.
- `core.location_alias`: PBX extensions (namespace `pbx_extension`) and config keys (namespace `config_key`). Part of calls attribution (item 9).
- `core.entity_registry`: the list of types a generic (type, id) reference may use (media, activity, event).
- `identity.person`, `identity.login`, `identity.person_location`: staff, sign-ins, postings. Part of items 1 and 6.
- `platform.event_type`, `platform.event`: event log under tasks, calendar, shifts and calls (items 4, 5, 9).
- `platform.notification_alert`: the browser push feed (item 3).
- `platform.utility_clock` and `platform.saved_utility`: the assistant's timer, stopwatch and saved-calculation utilities, written by `B/core/commands/utilities.py`. Not covered by items 1-15.
- `work.event_series`, `work.event_series_exception`, `work.calendar_sync*`, `calendar_event_ref`: covered under item 5.

## Doc vs code disagreements
- **Ladder**: the SQL seed in `traciora-core.sql` (`:462-473`) lists customer, junior(1), middle(2), senior(3), admin(4). `config/defaults/access_levels.json` adds technician (rank 1, scope worker) and shifts the rest up one. The JSON wins at bootstrap (`bootstrap.py:88,114+`), so the SQL seed is stale.
- **Proposal status**: your "published" status does not exist. Schema `status` allows only proposed, approved and rejected (`schema:3461+`). Code writes approved plus `published_as`. The `proposal_publication_shape` check still mentions `'published'`, which can never occur. A decline is stored as `rejected`.
- **Scheduled-task delivery**: the `cron_prompt_jobs.output_kind` default is `'telegram'` in the DDL (`manager.py:322-336`), but every code path writes `'store'` (`tasks.py:460,719`).
- **Chat interactions**: the schema comment describes an interaction for every chat, but the product writes only call and meeting interactions. Chatwoot chats are not in the core tables.
- **Data source engines**: `sources.schema.json` allows postgres and mssql only. There is no MySQL, despite the question.
- **Home**: `home.md` does not mention calls to return, and `home_sql.py` has none, so nothing to seed there.
- **Calendar**: `docs/features/calendar.md` says "no materialisation job", but `work.event_series` has `materialise_horizon_days` (default 90) and `materialised_through`. Only roster rotations have a materialising job.
- **Roster gate**: `roster.md` says planning is senior work. The code asks whether the caller's scope is in the audience of `plan_shifts`, so a tenant's `tools.json` can lower it (`roster/access.py:15-20`).
- **Notification types**: `task.assigned`, `task.mention` and `assistant.completed` are declared, but their producers are thin. `producers.py:8` and `answers.py:26` are the only hits I found.