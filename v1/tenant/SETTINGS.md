# Demo tenant settings, seed v1

The values are in `settings.en.json` and `settings.ru.json` (flat, as `runtime/config/settings.json` holds them). Every key is one `config/settings.schema.json` declares; `validate.py` checks the key, the type and the ledger value. Rule R9: the settings are part of the seed and versioned with it, so the files also **pin** the keys whose shipped default the stories rely on: a later product default cannot move a golden answer.

The feature switches (`TRACIORA_FEATURE_*`) below are the seed's defaults: the tenant step fills a switch only where the install holds none, so the features an administrator chooses at setup stay as chosen through every build and rebuild.

Ledger rows are `ledger.json` keys; every value below that rests on a row names it, `mem.retest_days` and `console.context_sync_at` among them.

## Set away from the shipped default

| Key | English | Russian | Why |
|---|---|---|---|
| `BUSINESS_TIMEZONE` | `America/New_York` | `Europe/Ulyanovsk` | ledger `geo.home_zone`; every "today", the brief times and T (rule R2) are home-zone |
| `PRODUCTION_LANGUAGE` | `en` (default) | `ru` | the configuration's language; pinned in English too |
| `CURRENCY` | `USD` (default) | `RUB` | design 1.1; core seed refuses to start without it |
| `REGION` | `Chattanooga, Tennessee` | `Ульяновск` | core seed needs a non-empty region; value is ledger `geo.home_city` verbatim |
| `BRAND_NAME` | `Brennan Auto Care` | `«Ермак-Сервис»` | the company the assistant speaks for; Russian verbatim from `kb/ru/README.md` |
| `APP_TITLE` | `Brennan Auto Care AI assistant` | `ИИ-ассистент «Ермак-Сервис»` | the product's title in the browser and the console; stated so a rebuilt demo never keeps the previous demo's title (controller's values) |
| `CONTACT_PHONE` | `(423) 555-0142` | `+7 (8422) 10-40-40` | the flagship's public line, `phones.md` and `kb/CROSS-STORE.md` section 7 |
| `CONTACT_EMAIL` | `main@brennanautocare.example` | `main@ermak-service.example` | `phones.md` section 3, shop mailboxes |
| `LOCATION_CITY` | `Chattanooga, Tennessee` | `Ульяновск` | ledger `geo.home_city` |
| `LOCATION_ADDRESS` | `2106 East Main St, Chattanooga, TN 37404` | `432045, Ульяновск, Московское шоссе, 40` | ledger `geo.address.main` |
| `LOCATION_LATITUDE` / `LOCATION_LONGITUDE` | 35.02473 / -85.27695 | 54.30296 / 48.28615 | ledger `geo.address.main` |
| `ADMIN_USERNAMES` | `cbrennan` | `eermolaeva` | slot 2 is the administrator (design 1.4; `cast.json` username) |
| `TRACIORA_FEATURE_BOARD`, `_ROSTER`, `_CALENDAR`, `_SCHEDULED_TASKS` | true | true | design 0: every feature is seeded; S1, S5, S9, S10, S14, S16 |
| `TRACIORA_FEATURE_PHONECALLS` | true | true | S1, S3, S4, S6, S8, S13 |
| `TRACIORA_FEATURE_CHATWOOT` | true | true | the conversations store; S6, S7, S13 |
| `TRACIORA_FEATURE_TELEGRAM` | true | true | needed for the Telegram customer channel (ledger `conv.channels`); the staff bot stays off, below |
| `TRACIORA_FEATURE_MEMORY` + `TRACIORA_MEMORY_ENABLED` | true + true | true + true | memory ships off; S2.4, S4.4, S4.5, design 4.5 |
| `TRACIORA_FEATURE_KNOWLEDGE` | true | true | S8.3, S12, the website assistant's answers (S7) |
| `TRACIORA_FEATURE_PII` | true | true | personal-data protection, section below |
| `TRACIORA_FEATURE_MCP` | true | true | design 7.3: MCP tokens get a minimal footprint; with the grant off they would be invisible. An edge install must also supply `TRACIORA_DOMAIN_MCP` (operator's) |
| `TRACIORA_MEMORY_RETEST_DAYS` | `"90"` | `"90"` | ledger `mem.retest_days`: at the shipped 180 no team note could come due inside 175 product days, and the assistant part plants five kept and one unverified |
| `TRACIORA_KNOWLEDGE_ROOT_SEEN_FROM` | `worker` | `worker` | ledger `kb.settings`: the website assistant reads as worker, so the public folders must be seen from worker. Console-only key: the seeder sets it through the knowledge base's own control before any page lands (`kb/OUTLINE.md` section 2) |
| `CHATWOOT_TELEGRAM_BRIDGE_ENABLED` | true | true | Telegram is a channel in both (ledger `conv.channels`, design O3); with no customer-bot token the bridge is not built and a reply there is refused, as `conv.live_demo` wants |
| `CHATWOOT_TELEGRAM_ASSISTANT` | `drafts` | `drafts` | ledger `conv.assistant_mode`: the owner set Telegram to drafts (shipped: sends), so each configuration shows drafting |
| `CHATWOOT_VK_BRIDGE_ENABLED`, `CHATWOOT_AVITO_BRIDGE_ENABLED` | false (default) | true | ledger `conv.channels`; English has web chat and Telegram only (design O3). `VK_GROUP_ID` and `AVITO_WEBHOOK_URL` stay unset: the console lists them as unwired, which never stops a start; with no credentials the bridges are not built, so a reply on those chats is refused (`conv.live_demo`). The two channel alerts of the history (`workday/ru/alerts.json` AL17, AL18) are seeded rows, both resolved |
| `TRACIORA_STT_MODELS` | `["parakeet","faster_whisper"]` | `["tone","gigaam"]` | ledger `calls.recognition.engines` ("tenant settings"); `transcript.engine_version` names them |
| `TRACIORA_CONTEXT_SYNC_AT` | `07:55` | `08:55` | ledger `console.context_sync_at`: five minutes before slot 2's Monday "Company accounts this week" (ledger `s10.tasks`), so the ERP outage of `s10.failure` also fails that morning's context sync: the `job_failed` alert of S10 (07:55 en, 08:55 ru, the Monday of week T-1) |

## Pinned at the shipped default

| Key | Value | Why it is pinned |
|---|---|---|
| `TRACIORA_BOARD_URGENT_LIMIT` | 3 | urgent cards per shop; the board loader never leaves more than three urgent open at a site and `west` meets the limit (`workday/DESIGN.md`, priorities) |
| `TRACIORA_BOARD_QUIET_DAYS` | 7 | "two cards gone quiet" at T (ledger `board.open_at_t`) are read against seven days |
| `TRACIORA_BOARD_CLOSED_DAYS` | 7 | the Done column's window on the board screens |
| `TRACIORA_ROSTER_REQUEST_DAYS` | 30 | how long a decided request shows on a person's own schedule; S14.4's 90 days are read through the source, not this screen |
| `TRACIORA_MEMORY_PROPOSE_HOLDERS`, `TRACIORA_MEMORY_DORMANT_DAYS` | `"3"`, `"90"` | the nightly proposal needs three holders (S4.4, `mem.nightly`); four notes are dormant after 90 days (assistant part) |
| `TRACIORA_KNOWLEDGE_PROPOSE_FROM`, `_PUBLISH_FROM`, `_VISIBILITY_FROM` | `middle`, `senior`, `senior` | ledger `kb.settings`: slot 5 (middle) proposes the timing-belt fix, slot 4 (senior) decides (S12.4) |
| `CHATWOOT_CHAT_BRIDGE_ENABLED`, `CHATWOOT_CHAT_ASSISTANT` | true, `sends` | ledger `conv.assistant_mode`: the assistant sends on the website chat; the live demo replies there (`conv.live_demo`) |
| `CHATWOOT_VK_ASSISTANT`, `CHATWOOT_AVITO_ASSISTANT` (ru file only) | `drafts` | ledger `conv.assistant_mode` |
| `CONVERSATIONS_OWNERSHIP` | `first_reply` | ledger `conv.ownership`: S7's return chat becomes slot 6's at her first reply |
| `CONVERSATIONS_AUTO_RESOLVE_DAYS` | 7 | ledger `conv.auto_resolve_days` |
| `CONVERSATIONS_ALL_TAB_RANK` | `junior` | juniors see every open chat, as the conversations design assumes; also why juniors read the chats through the source (SOURCES.md) |
| `CONVERSATIONS_PRIORITY_FLOOR_MINUTES`, `_CEILING_MINUTES` | 5, 60 | the shown priority of S6's chat ("urgent by its wait", `conv.open_at_t`) is computed with them |
| `TRACIORA_PHONECALLS_PERFORMANCE_RANK` | `senior` | the rank that sees colleagues' phone performance: S4.2 (senior reads Maya's scores) and S4.6 (a junior is refused Caleb's) |
| `TRACIORA_PHONECALLS_CALLBACK_MINUTES` | 60 | the To call back list's urgency of the nine waiting at T (ledger `calls.queue_at_t`) |
| `PII_LEAK_GUARD_ENABLED`, `PII_SECOND_PASS`, `PII_LANGUAGE`, `PII_EXCLUDED_CATEGORIES` | true, `encoder`, `auto`, `["url"]` | personal-data protection, below; the second pass is off by default, and the seed turns it on so names and street addresses are protected too |
| `TRACIORA_BOARD_ENABLED`, `TRACIORA_ROSTER_ENABLED`, `TRACIORA_CALENDAR_ENABLED`, `TRACIORA_SCHEDULED_TASKS_ENABLED` | true | the four workspace switches, pinned on |

## Product rules the stories rely on (no setting)

No key of `config/settings.schema.json` sets these; the seed relies on them as the product ships them, and the rows say so (D13).

| Rule | Value | Ledger |
|---|---|---|
| Brief times | fifteen hidden brief jobs, one per manager of junior rank or above who has opened Home; written five minutes before the first shift, a third and two thirds of the way, and an hour before the end, or at 06:40, 10:40, 14:40, 18:40 for a person with no shift (home zone, or the shift's site zone); 200 rows kept | `sched.brief_jobs`, `sched.brief_times` |
| Job history | the console keeps job runs for 90 days | `console.job_history_days` |
| S10's alert | the report "Company accounts this week" fails on the Monday of week T-1 because the shop system cannot be reached and runs again 65 minutes later; the context sync at `TRACIORA_CONTEXT_SYNC_AT`, five minutes earlier and inside the outage, raises the `job_failed` alert, acknowledged. No alert rule exists for an unreachable source | `s10.failure`, `console.context_sync_at` |

## Stated as off (design 4.8)

| Feature | How it is off |
|---|---|
| Google Calendar | `TRACIORA_FEATURE_GOOGLE_CALENDAR` false and `TRACIORA_GOOGLE_CALENDAR_ENABLED` false (both the shipped default, pinned) |
| The staff Telegram bot | `TELEGRAM_MANAGER_BOT_ENABLED` false; `TELEGRAM_SCHEDULER_ENABLED` and `SECURITY_ALERT_ENABLED` false too, so no report or alert leaves for Telegram (ops signals stay in the console) |
| Audio playback | no setting gives it: a call's sheet draws a player only while the recording's bytes are in the media store (`docs/features/call-pipeline.md`, "One call"). The seed stores no bytes (`calls/DESIGN.md` section 1, `media_object.storage_ref_enc` empty), so no call plays |
| Code sandbox | `TRACIORA_FEATURE_CODE_SANDBOX` false (default): no story needs it, and `run_bash` is then not registered |

## Personal-data protection

What protection on and off do to the model's view and to the cross-store questions (S1.2, S1.5, S6.5, S7.1: a customer found by phone in one store and looked up in another):

| | A (seeded): protection on | B: protection off |
|---|---|---|
| Keys | `TRACIORA_FEATURE_PII` true | `TRACIORA_FEATURE_PII` false |
| What the model sees | names, phones, emails, plates, VINs as stable reference tokens; every person reads the real values: answers, cards, titles, call transcripts | everything as stored |
| Cross-store questions | work: a token is resolved to the real value at the tool boundary, so `phone('<token>')` in SQL matches; the same value gives the same token inside a conversation, so the model can match a number seen in the ERP with one in a chat note | work |
| What it costs | every turn runs the detector and the second pass (latency); a false positive (a car model or a street read as a name) can cost an answer, so a failed eval may be the detector's and not the agent's | the demo shows no protection, and the evals do not measure a configuration a privacy-bound tenant runs |

Recommendation: **A** for the seed, because it is what a tenant who must protect customers' data runs and it keeps every cross-store question answerable; run the eval set once with **B** as the control, so a drop between the two is read as the detector's. Context files: with `pii` on, the sync also masks phones and plates in every table's preview and profile (`docs/features/data-layer.md`), which the notes do not rely on.

## History windows per rank

The ladder's `access_limits.json` is kept as shipped (worker 180 days, junior 180, middle 365, senior and admin the whole history; `ladder.json`). Go-live is T-175 days (ledger `time.go_live_days`), so the junior's 180-day window holds the whole product period with five days to spare, and her first score period (S4.1) is inside it (review 17, resolved by design 7.2 S4). Nothing to change.

The window binds the product's own tools and screens (calls screens, board, roster, calendar). It does not bind SQL over any source (`execute_sql` applies no window, `apps/backend/src/traciora/core/tools/data/registration.py`): a junior reads the ERP's two years. The cards define their own periods, so no golden answer depends on it; see SOURCES.md.

## Not set by the seed

Install-specific and the operator's: `PUBLIC_BASE_URL`, `TRACIORA_DOMAIN_*`, `TRACIORA_EDGE_TLS`, model roles, `LANGFUSE_*`, every secret. The call-log connection (`ASTERISK_*`) stays unset: the seed writes the call log's rows and one `recording_run` itself (`calls/DESIGN.md` section 1), and the console lists the address as unwired, which never stops a start. `CHATWOOT_ACCOUNT_ID` is obtained by the start.

## Needs a product change

| Behaviour the design needs | No setting gives it because | Smallest change |
|---|---|---|
| A junior's question about another shop's calls is refused (S1.8, S6.6), and a junior is refused a colleague's scores (S4.6); until then the three are expected refusals marked failing (owner's decision) | the data layer applies neither the site binding nor `TRACIORA_PHONECALLS_PERFORMANCE_RANK` to SQL: a rank granted the calls views reads every shop's and everyone's rows | in the data layer, filter the `core` source's calls views for a site-bound rank to the asker's sites (`location_id`, through the call for missed calls), and below the performance rank keep `phone_call_analysis` and `phone_call_day_report` to calls the asker handled; detail in SOURCES.md |
| Naming the person behind a chat reply through the source | the Chatwoot reader reads `users.id` and `type` only | grant the reader `users.name` (or a view of id and display name) |
| Draft outcomes asked in Ask | they live in `auth.db`, which no source reads | none for v1: the Conversations Stats screen and the console count them; a question about them is answered from the screen |

## Russian display values not in the seed files

- Russian names of the ladder's steps, if the Russian configuration wants its own: the seed keeps the product's step names and the product's own translation of the scopes.
