# Demo tenant sources, seed v1

Data: `sources.en.json`, `sources.ru.json` (identical: the ERP's schema is English in both configurations, design 2 "1a"). They validate against `config/schemas/sources.schema.json` and parse with the product's own `parse_sources` (`validate.py`).

## How access works, and what it does not do

- A rank reads what its entry grants plus everything the ranks below grant. A table named by its exact name keeps its hidden columns at every higher rank until a higher rank names it again (`apps/backend/src/traciora/data/sources/config.py`, `_inherit`, `Access.hides`); a view is reached only by its own name.
- Workers have no data tools at all (`docs/features/data-layer.md`, "offered to every manager step"), whatever a source grants.
- **SQL is bound by rank and columns only.** The data tools apply no site binding and no history window (`core/tools/data/registration.py`; nothing in `data/sources/` reads `location_ids` or `history_days`). A junior posted at `main` who holds a table reads every shop's rows in it, and two years of them. The site binding and the history window bind the product's own tools and screens (board, roster, calendar, the Calls screens). This decides three questions below.
- `*_enc` columns of `core` are read in plain text by a rank that reads the column, except the sealed ones (`data/sources/personal_data.py`): `platform.event.payload_enc`, `platform.activity` texts, `roster_publish.diff_enc` and the like are unreadable at every rank.

## `erp` (the shop system, Postgres, schema `shop`)

Declared `kind: postgres`, no product seed (`system: null`), `include: ["shop.*"]`, so the seed's manifest, in a schema of its own, is never synced or read (design 2.1). Its 31 tables are those of design 2.2, specified in `../erp/schema.sql` and `../erp/dictionary.md`; access follows the rule of 2.6 as changed by R9 and 7.2. Every hidden column below is a column of `erp/schema.sql` (confirmed in fix pass B; `validate.py` checks each one).

| Rank | Reads | Hidden |
|---|---|---|
| worker | nothing (no data tools) | |
| junior | every table of `shop` (all 31) | staff pay: `employee.pay_type`; the till counts: `cash_drawer_close.float_amount`, `expected_cash`, `counted_cash`, `difference`, `note` |
| middle, senior, admin | every table | nothing (middle names the two tables again with no hidden column) |

Why: design 2.6 (junior and up read every table); R9 and the controller's decision of fix pass A: a customer's phone, email and address (`customer.phone`, `email`, `address`, `customer_contact.phone`, `email`, `appointment.contact_phone`) are readable from junior up, as on the Calls screens and in Chatwoot (`erp/dictionary.md`, access by rank); 7.2 Cast (the bookkeeper, middle, reads pay and till counts, so they open from middle, not senior). The ERP holds no pay amounts (`employee.pay_type` is the only pay column).

The 31 tables: `location`, `employee`, `customer`, `customer_contact`, `vehicle`, `referral_source`, `service_category`, `canned_job`, `labor_rate`, `part`, `vendor`, `appointment`, `repair_order`, `order_status_history`, `order_job`, `order_labor`, `order_part`, `order_sublet`, `order_fee`, `inspection`, `inspection_item`, `time_entry`, `statement`, `payment`, `cash_drawer_close`, `purchase_order`, `purchase_order_line`, `stock_level`, `stock_movement`, `part_return`, `service_reminder`.

## `core` (the product's own database, built in)

Declared with `system: traciora` and `applied_defaults` holding all three product defaults, so a start never adds a grant this file leaves out (`docs/features/data-layer.md`, "From the host").

| Rank | Adds | Hidden | Why |
|---|---|---|---|
| junior | views `phone_call`, `phone_call_participant`, `phone_call_transcript`, `phone_call_transcript_segment`, `phone_call_analysis`, `phone_call_leg`, `phone_call_missed`; table `interactions.recording_job` | | the product's shipped junior grant, kept: S4.1, S4.3, S7.1, S7.4 |
| | `core.location`, `core.location_alias`, `core.location_hours_exception`, `core.position`, `identity.person`, `identity.person_location` | `person.name_tokens` | S13.1, S13.3 (dated hours); naming the person on a call (S4.1); extension to shop |
| middle | `workforce.shift`, `workforce.punch`, `workforce.shift_template` | `shift.tips_declared_enc`, `shift.warning_override_comment_enc`; `punch.coordinates_enc`, `punch.note_enc` | the bookkeeper takes payroll hours from the punches (`kb/en/office/payroll-hours.md`); the template's grace judges lateness |
| senior | `workforce.shift_change_request`, `availability`, `coverage_requirement`, `roster_publish`, `shift_schedule`; `platform.event`; `work.work_item`, `work_participant`, `work_state`; `platform.activity`; view `phone_call_day_report` | `shift.tips_declared_enc`, `punch.coordinates_enc` (named again: the planner reads the punch note and the override comment) | S1.6, S3.7, S5.1, S5.2, S5.4, S14.*; the day reports from senior as shipped; card history for the per-person cycle times of design 4.2 |
| admin | schemas `core`, `identity`, `interactions`, `workforce`, `work`; `platform` tables except `memory` and `proposal` | inherits the senior's hidden columns (staff GPS stays hidden) | S6.4, S9, S11.2, S15.4, S16.2. **Changed from the shipped `everything`**: `platform.memory` would hand every manager's personal notes, decrypted, to the administrator's SQL, which the memory feature forbids ("no Ask tool reads another login", `assistant/DESIGN.md` A.4). Team notes and proposals are read with the memory tools. Cost: a table a later release adds is not granted to admin until the console ticks it. Confirmed by the controller (fix pass C, 2026-11-14) |

Platform tables admin reads: `event_type`, `event`, `activity`, `notification_type`, `notification_setting`, `notification_queue`, `config_version`, `alert`, `job_run`, `feedback_report`, `usage_event`, `push_subscription`, `metric_rollup`, `pii_access_log`, `utility_clock`, `saved_utility`, `notification_alert`.

## `chatwoot` (the conversations database, built in)

Declared with `system: chatwoot`. The reader login itself can select only `messages`, `conversations`, `inboxes`, `users` (id, type), `account_users` (user, account, role), the four `traciora.*` views and `traciora.contact_has_phone` (`docker/chatwoot/traciora_reader.sql`): a grant here cannot open more.

| Rank | Adds | Why |
|---|---|---|
| junior | tables `public.conversations`, `public.messages`, `public.inboxes`, `public.users`, `public.account_users`; views `traciora.conversation_facts`, `message_facts`, `reply_episodes`, `resolutions` | juniors already see every open chat on the Conversations screen (`CONVERSATIONS_ALL_TAB_RANK` junior); S7.1, S7.2, S7.3 need the chats in Ask. Contacts are not readable at any rank, so a customer's phone in Chatwoot is read only where a message carries it (the hand-over note), which agrees with R9 |
| admin | `everything` (shipped) | |

## Every question against the grants

Asker ranks from `stories/README.md`; the path is the source and tables, or the product tool, the card's proof names. "Granted" means every table and column the path needs is readable at the asker's rank; "refused" means the path is closed.

| # | Asker | Path | Granted? | Matches the card? |
|---|---|---|---|---|
| S1.1 | 2 admin | erp `repair_order`, `customer` | granted | yes |
| S1.2 | 2 admin | erp comeback orders, `statement`, `payment`; core `phone_call`, `phone_call_leg` (by token), `phone_call_missed`, `phone_call_analysis` | granted | yes |
| S1.3 | 4 senior | erp `repair_order`, `order_status_history`, `customer_contact`; core calls; chatwoot `messages`, `conversations`; board `create_task` | granted | yes |
| S1.4 | 2 admin | erp `statement`, `payment` | granted | yes |
| S1.5 | 2 admin | erp `customer_contact.phone`; core `phone_call_missed`, `phone_call_leg` tokens | granted | yes |
| S1.6 | 4 senior | core `phone_call_leg.extension`, `workforce.shift` | granted (answer: cannot tell) | yes |
| S1.7 | 16 middle | erp `statement`, `customer` | granted (answer: nothing) | yes |
| S1.8 | 6 junior | core calls views by token | **granted**: SQL is not site-bound | **no, expected and marked failing**: the card wants a refusal by site; refused on the Calls screens only, until the product filters its call views (owner's decision; no grant changed) |
| S2.1 | 2 admin | erp `repair_order`, `payment` | granted | yes |
| S2.2 | 2 admin | erp `repair_order`, `payment`, `cash_drawer_close` | granted | yes |
| S2.3 | 2 admin | erp `repair_order` | granted | yes |
| S2.4 | 6 junior | knowledge `policies/discounts.md` (junior); team note via `recall_memory` | granted | yes |
| S2.5 | 2 admin | erp `repair_order.discount_approved_by` | granted | yes |
| S2.6 | 2 admin | as S2.2 | granted (answer: cannot tell) | yes |
| S2.7 | 6 junior | erp `cash_drawer_close` counts | **refused**: the till counts (`float_amount`, `expected_cash`, `counted_cash`, `difference`, `note`) are hidden below middle | yes |
| S2.8 | 3 middle | erp `cash_drawer_close` (en), `stock_movement` (ru) | granted | yes |
| S3.1 | 4 senior | core `phone_call_missed`, `phone_call_leg`, `phone_call` | granted | yes |
| S3.2 | 4 senior | the same | granted | yes |
| S3.3 | 4 senior | the same | granted | yes |
| S3.4 | 6 junior | the To call back list read as her (Calls screen) | granted | yes: she is posted at `main` and `east` (ledger `cast.also_sites`), so her list holds `main` 4 (two from today) and `east` 1, five, the card's answer (`calls.queue_at_t`). Through SQL she would get all nine |
| S3.5 | 4 senior | the list, every shop | granted | yes |
| S3.6 | 4 senior | core `phone_call_leg.extension` | granted (answer: cannot tell by person) | yes |
| S3.7 | 4 senior | core `workforce.shift`, `punch` | granted (stale) | yes |
| S4.1 | 6 junior | core `phone_call_analysis`, `phone_call_participant`, `identity.person` | granted | yes |
| S4.2 | 4 senior | the same | granted | yes |
| S4.3 | 6 junior | core `phone_call_analysis.result_public` | granted | yes |
| S4.4 | 4 senior | memory tools (`review_team_note`) | granted | yes |
| S4.5 | 6 junior | her Inbox line and the memory tools | granted | yes |
| S4.6 | 6 junior | core `phone_call_analysis` for another person | **granted**: the performance rank binds the Calls screens, not SQL | **no, expected and marked failing**: the card wants a refusal by the performance rank, until the product filters its call views (owner's decision; no grant changed) |
| S5.1 | 4 senior | erp `order_job`, `repair_order`; core `workforce.shift` | granted | yes |
| S5.2 | 4 senior | roster tools; core `shift`, `availability`, `coverage_requirement` | granted | yes |
| S5.3 | 4 senior | erp | granted | yes |
| S5.4 | 4 senior | `show_requests`; core `shift_change_request` | granted | yes |
| S6.1 | 2 admin | erp `order_status_history`, `purchase_order` | granted | yes |
| S6.2 | 22 senior | erp `repair_order`, `order_status_history` | granted | yes |
| S6.3 | 2 admin | erp comeback orders, `order_part`, `order_labor` | granted | yes |
| S6.4 | 2 admin | core `work.work_item` | granted | yes |
| S6.5 | 22 senior | erp `repair_order`, `order_status_history`, `purchase_order` (the car that has waited longest); core calls by token; chatwoot `messages` | granted | yes |
| S6.6 | 6 junior | core `phone_call_missed` at `west` | **granted**: SQL is not site-bound | **no, expected and marked failing**: the card wants a refusal by site; refused on the Calls screens only, until the product filters its call views (owner's decision; no grant changed) |
| S7.1 | 6 junior | erp `customer.phone`, orders, `order_job`, `payment`, `appointment`; core `phone_call_leg` by token; chatwoot `messages`; board `show_task` | granted | yes |
| S7.2 | 6 junior | erp `order_job`; chatwoot `messages` | granted | yes |
| S7.3 | 6 junior | chatwoot conversation; erp `appointment`; knowledge price list | granted | yes |
| S7.4 | 6 junior | core `phone_call_analysis` (`judged` false) | granted (answer: nothing) | yes |
| S8.1 | 4 senior | core calls; erp order | granted | yes |
| S8.2 | 4 senior | erp `repair_order` | granted | yes |
| S8.3 | 5 middle | knowledge pages (public and staff) | granted | yes |
| S8.4 | 4 senior | core `phone_call_analysis` | granted (answer: nothing) | yes |
| S9.1 | 2 admin | core `calendar_event`, `calendar_event_participant`, `event_series`, `location` | granted | yes |
| S9.2 | 2 admin | core `calendar_event_participant.attended` | granted | yes |
| S9.3 | 2 admin | `find_free_slot`; roster; core `location` | granted | yes |
| S9.4 | 2 admin | core `work_item`, `activity`; team notes via `recall_memory` | granted (answer: nothing) | yes; team notes through the tool, not SQL (admin no longer reads `platform.memory`) |
| S10.1 | 2 admin | scheduled-task tools (her own runs); core `platform.alert` for the `job_failed` alert on the context sync (`s10.failure`, at `console.context_sync_at`) | granted | yes |
| S10.2 | 1 senior | `read_scheduled_task_runs` (his brief) | granted | yes |
| S10.3 | 2 admin | `list_scheduled_tasks` | granted | yes |
| S10.4 | 6 junior | another person's tasks | **refused**: task reads are the caller's own; no source reads `auth.db` | yes |
| S11.1 | 2 admin | erp | granted | yes |
| S11.2 | 2 admin | core calls, `shift`; erp | granted | yes |
| S11.3 | 4 senior | erp `order_job`, `employee` | granted | yes |
| S12.1 | 6 junior | knowledge (public) | granted | yes |
| S12.2 | 5 middle | knowledge | granted | yes |
| S12.3 | 6 junior | knowledge (public) | granted | yes |
| S12.4 | 4 senior | knowledge proposals | granted | yes |
| S12.5 | 6 junior | `management/pay-and-till.md`, seen from senior | **refused** by page rank | yes |
| S13.1 | 6 junior | core `location_hours_exception` | granted | yes |
| S13.2 | 4 senior | core `phone_call_missed.out_of_hours` | granted | yes |
| S13.3 | 6 junior | core `location_hours_exception` | granted | yes |
| S14.1 | 4 senior | core `punch`, `shift`, `shift_template` | granted | yes |
| S14.2 | 4 senior | core `punch`, `shift` (a clock-in with no clock-out by the end of its day; the `web_correction` punch) | granted | yes |
| S14.3 | 4 senior | core `shift` | granted | yes |
| S14.4 | 4 senior | core `shift_change_request` | granted | yes |
| S14.5 | 4 senior | core `punch`, `platform.event`; erp comebacks | granted (answer: cannot tell the reason) | yes |
| S14.6 | 4 senior | core `punch` | granted (answer: nothing) | yes |
| S14.7 | 15 worker | any data tool | **refused**: a worker has none | yes |
| S14.8 | 4 senior | core `platform.event` (`shift.no_show`), `shift` | granted | yes |
| S15.1 | 2 admin | erp `customer` | granted | yes |
| S15.2 | 2 admin | erp `repair_order` | granted | yes |
| S15.3 | 2 admin | erp | granted | yes |
| S15.4 | 2 admin | core calls (instants); erp `repair_order`, `location` | granted | yes |
| S15.5 | 4 senior | erp `repair_order`, `vehicle` | granted | yes |
| S15.6 | 2 admin | erp `repair_order` | granted | yes |
| S16.1 | 6 junior | board `show_task` (her card's parts) | granted | yes |
| S16.2 | 2 admin | core `work_item`, `work_participant` | granted | yes |
| S16.3 | 6 junior | erp `statement`, `payment`, `repair_order` | granted | yes |
| S16.4 | 6 junior | board | granted (answer: nothing) | yes: none overdue among her six open cards (`board.open_at_t`) |

84 questions: 81 match, 3 do not (S1.8, S4.6, S6.6). The seven refusals: S2.7, S10.4, S12.5, S14.7 hold; S1.8, S4.6, S6.6 do not, and stay expected refusals marked failing until the product filters its call views (owner's decision).

## The three that do not match

| # | Why | Decided |
|---|---|---|
| S1.8, S6.6 | the junior holds the calls views (shipped default) and SQL carries no site filter | the owner keeps the grant and asks for the product change: the data layer filters the `core` calls views for a site-bound rank to the asker's sites (`phone_call.location_id`, `phone_call_leg.location_id`; misses, transcripts and analysis through their call). Removing the junior's calls views was rejected: S4.1, S4.3, S7.1's call and S7.4 would lose their path |
| S4.6 | the performance rank binds the Calls screens only | the same change, plus: below `TRACIORA_PHONECALLS_PERFORMANCE_RANK`, `phone_call_analysis` and `phone_call_day_report` keep to the calls the asker handled |

Until the product change, the three are expected refusals marked as failing in eval set v1.0. No grant of this file changes for them.

## Notes the context gives (D)

`context/README.md` lists what extends the shipped notes and what is new, per source.
