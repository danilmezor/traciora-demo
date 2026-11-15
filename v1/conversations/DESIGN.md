# Customer conversations: design (seed v1)

Brought to the ledger, the story cards and the owner's decisions in the reconcile pass of 2026-11-13: the rows of section 9 are in `../ledger.json` (`conv.*`, `r13.chats.*`, `pNN.first_reply_min`), and `../checks/check_files.py` fails on a difference.

Paths without a root are in the product repository; `C` = `apps/backend/src/traciora/core/channels/chatwoot`. Ledger = `../ledger.json`. Classes: **M** measured, **D** derived, **X** designed. Chatwoot schema facts were read with `\d` on the dev database `chatwoot_production` (container `demo-postgres`, last migration `20260831000000`); Chatwoot's Ruby source was not read, so every statement about what its API or its callbacks do is marked "from memory".

Five facts of the product shape everything below:

- **A conversation has no shop.** The tenant has one inbox per channel (`Chat`, `Telegram`, `VK`, `Avito`; `docs/features/chatwoot.md:255`), one queue, and Stats filter by channel and by operator only. A chat's shop is its owner's shop, or what the customer said. "Per shop" below is therefore an attribution the seed makes, not a column.
- **The channel of a chat is a row of ours, not Chatwoot's.** It is the bridge key of the chat's row in `bridge_threads` (`C/sync.py:214`, `C/stats_blocks.py:75-76`). No row: no channel, drafts only (`docs/features/conversations.md:383, 551`).
- **A messenger customer has one conversation for life.** A new message reopens the resolved one (`C/conversations.py:75-80`); only the web chat (one conversation per visit, `C/chat_bridge.py:1-8`) and Avito (one per listing) make new ones. So the unit below is the **session**: the messages between two resolutions. Stats' "new dialogs" and "time to first answer" count conversations created, not sessions (`docker/chatwoot/traciora_reader.sql:42-48`).
- **Only the relay wakes the assistant** (`C/relay.py:170-179`, `C/assistant.py:200-207`), and a turn left in `agent_turn` runs at the next start (`conversations.md:393-394`). Rows written past the relay wake nothing.
- **The assistant answers from public pages, cannot book and cannot read the shop system.** Its one way to a person is `forward_to_manager`, which needs a name and a phone (`docs/features/escalation.md:30-36`), tells the customer "somebody will get back to you as soon as possible", no time and no "reply here" (`config/locales/en.json:329`), and leaves a private note, the `handoff` label and an open chat (`C/conversations.py:107-126`), plus a board card: `task` at `normal` for a booking, `escalation` at `high` otherwise, one per conversation per day (`escalation.md:93-106`).

## 1. One conversation across the stores

### Chatwoot database (v4.18.0)

| Table | A loader fills | Why (who reads it) |
|---|---|---|
| `contacts` | `account_id`, `name`, `identifier` = `<slug>_<peer id>` (unique per account; `core/channels/bridge.py:236-237`), `phone_number` only where the channel gave one (Telegram's shared contact, `C/telegram_bridge.py:281-287`), `created_at`, `updated_at`, `last_activity_at` | the list's name, the avatar colour by contact id (`conversations.md:228-230`), the relay's lookup by identifier on the next real message (`C/conversations.py:82-83`) |
| `contact_inboxes` | `contact_id`, `inbox_id`, `source_id` (unique per inbox), `pubsub_token` (unique), timestamps | Chatwoot refuses to serve an API-inbox conversation without it (from memory) |
| `conversations` | `account_id`, `inbox_id`, `contact_id`, `contact_inbox_id`, `status` (0 open, 1 resolved, 2 pending, 3 snoozed), `assignee_id`, `priority` (the **shown** level, `conversations.md:284-290`; null when never raised), `created_at`, `updated_at`, `last_activity_at`, `first_reply_created_at`, `waiting_since`, `agent_last_seen_at` (unread count follows from it), `contact_last_seen_at`, `snoozed_until`, `cached_label_list`, `custom_attributes` (the Avito or VK listing), `uuid`. **`display_id` cannot be set**: the trigger `conversations_before_insert_row_tr` overwrites it from `conv_dpid_seq_<account>`. The product's ids are display ids (`C/conversations_store.py:56`) while the views read `conversations.id` (`traciora_reader.sql:43`), so the loader inserts in id order with both sequences set to the same value and asserts `id = display_id` on every row | `conversation_facts`; every route; the sync's row (`C/sync.py:196-221`) |
| `messages` | `account_id`, `inbox_id`, `conversation_id`, `content`, `message_type` (0 incoming, 1 outgoing, 2 activity), `private`, `sender_type` and `sender_id` (`Contact`; `User` = the manager's Chatwoot user; `AgentBot` = the bot `assistant`), `status` (0 sent), `content_type` 0, `source_id` = `<slug>:<account>:<message id>#<part>` on customer lines (`bridge.py:232-233`), `created_at`, `updated_at` | `message_facts` (customer, manager, assistant, note), `reply_episodes`, `first_answer_at` (`traciora_reader.sql:45-75`); the thread |
| ... private notes | the same with `message_type = 1`, `private = true`; the hand-off note's sender is the bot | kind `note`; left out of every wait (`traciora_reader.sql:66`) |
| ... activity lines | `message_type = 2`, no sender, Chatwoot's own words in the account's locale, for: assigned, label added or removed, priority changed, resolved, reopened, resolved by inactivity. **Every resolution must leave one**, and its words must match the tenant's `chatwoot.resolved_patterns`: that line is how the assistant and Ask find where the current session starts (`C/session.py:18-19, 45-63`) | the thread's small centred lines; session cuts |
| `attachments`, `active_storage_attachments`, `active_storage_blobs` + the bytes in Chatwoot's storage | one of each per file: `file_type` (image, audio, file), blob `key`, `filename`, `content_type`, `byte_size`, `checksum` | the media route streams from Chatwoot's host (`conversations.md:206`); a photo with no bytes is a broken tile. v1 has no pool (section 5): no attachment row is written, a line with words keeps them, and a line that is only a file is not loaded, as an empty bubble is worse than no line |
| `labels`, `tags`, `taggings` | the account's label definitions; a tag per title; a tagging per chat and label (`taggable_type = 'Conversation'`, `context = 'labels'`); the same titles in `cached_label_list` | the label filter, the header's topic (`conversations.md:657-658`), the console's count per label (`conversations.md:266`) |
| `reporting_events` | one `conversation_resolved` row per resolution: `conversation_id`, `inbox_id`, `user_id` (the chat's assignee at that moment, as Chatwoot's listener writes it, whoever resolved it; null when nobody was assigned), `value` (seconds since the chat opened), `created_at`, `event_start_time`, `event_end_time`. Shape as `apps/backend/tests/chatwoot_crm.py:175-185` | `resolutions` (`traciora_reader.sql:76-79`). No other event name is read |
| `users`, `account_users`, `inbox_members`, `agent_bots`, `inboxes`, `channel_api` | **not loaded: made through the product** (section 2, step 1); the chats step names the service administrator after the tenant's assistant (`APP_TITLE`) on every build | a manager's Chatwoot user and token (`C/agent_sync.py:1-12`, `C/agents.py:60-67`); the bot (`conversations.md:456-459`) |

Search needs nothing: `messages.content` and the contact fields carry trigram indexes that Postgres keeps on insert.

### The product's own state (`auth.db` and files)

| Piece | A seed fills | Reference |
|---|---|---|
| `bridge_threads` | one row per conversation: `bridge` (`chat:default`, `telegram:default`, `vk:default`, `avito:default`), `thread_key` (web chat: the visit's session id; Avito: the chat id; else the peer id), `peer_id`, `contact_id`, `conversation_id`, `updated_at` = the last customer line | `C/relay_store.py:208-213, 553-563`; without it a chat is in no channel |
| `conversation_state` | only for chats open or pending at T that carry a fact Chatwoot does not: a manager's base priority, `arrived_closed`, `owner_since`. The first resync writes every other column and keeps these three (`C/sync.py:199-205`) | `C/conversations_store.py:182-190` |
| `draft_outcome` | one row per draft that left the box: `conversation_id`, `manager_id` (null for `replaced_unseen` by a newer draft), `draft_created_at`, `decided_at`, `outcome`, `trace_id` null | `C/conversations_store.py:196-199, 385-456` |
| `conversation_draft` | the draft waiting in the box at T (sealed under `MEMORY_ENCRYPTION_KEY`), through `ConversationStore.offer_draft(..., now=)` as the test stack does (`e2e/stack/stack.py:983-992`) | `C/conversations_store.py:193-195` |
| hand-off state | in Chatwoot: the bot's private note, the label `handoff` while nobody has replied, status open. In `auth.db`: `handoff_owed` stays **empty** (it is a debt for a Chatwoot outage, `:212-214`). In core: the hand-over card and its `customer.handover_requested` event (`escalation.md:64-102`), loaded by the board's loader with the same instant | `C/conversations.py:107-126` |
| `agent_turn`, `bridge_inbound`, `bridge_outbound`, `compose_text` | **empty**. A row in `agent_turn` would run a model at start | `conversations.md:393-394` |
| `chatwoot_agents` | written by the agent sync, not by the loader | `C/agents.py:60-67` |
| web-chat visitors | per seeded web visit: the claim of the session by its browser subject (`core/auth/manager.py:1321`, `api/routes/auth.py:98-121`). The customer agent's memory (`chatwoot-contact:<contact id>`, `conversations.md:399-402`) is written for the story customers only | `api/routes/web_chat.py:1-13` |

## 2. How to load it

| | Through Chatwoot's API | Straight into its tables |
|---|---|---|
| Past times | no: `created_at` is the server's clock on conversations, messages and events (from memory; the product's own `external_created_at` is an attribute, `C/conversations.py:97-98`) | yes |
| Derived columns and counters | Chatwoot computes them, against the wrong clock; every one would be patched by SQL afterwards | the loader owns them: `first_reply_created_at`, `waiting_since`, `last_activity_at`, `agent_last_seen_at`, `cached_label_list`, the two id sequences |
| Reporting events | written by Chatwoot's listeners at load time with load-time values | written with their own instant |
| Search | kept by Postgres | kept by Postgres |
| What it wakes | with the product up: the cable, a refresh and an Inbox line per chat (`conversations.md:121-126, 338-345`); not the assistant | nothing |
| Speed, for about 21,000 (EN) and 60,000 (RU) message rows | one request a message, a per-conversation flood limit (`C/relay.py:59-65`): over an hour, then the patch pass | `COPY`: seconds |
| Breaks on | little | a Chatwoot upgrade |

**Recommendation: load straight into the tables, pinned to v4.18.0, with Chatwoot's users, bot, inboxes and labels made through the product first.** The API cannot write the past, so the API path ends in the same SQL anyway. The tests already write these tables directly (`apps/backend/tests/chatwoot_crm.py:146-185`).

Order:

1. **T-state through the product, API process not serving:** `traciora start` has provisioned the account, the service administrator and the platform app (`docker/chatwoot/provision.rb`). The seeder then calls the product's own functions for: the four inboxes by name; the agent bot `assistant`; the labels; one agent-sync pass for every login, F1 included, then F1's login is ended and a second pass unlinks him ("their user and what they wrote stay", `C/agent_sync.py:8-9`). It reads back each manager's Chatwoot user id from `chatwoot_agents` and the bot's id.
2. **Guard:** the last row of `schema_migrations` is `20260831000000` and the `display_id` trigger exists; else stop.
3. **Stop Chatwoot's workers** (Sidekiq: auto-resolve, automation, listeners). The product's API stays down until step 7: no cable, relay, assistant, priority clock or agent sync.
4. **Bulk load** in one transaction: set `conversations_id_seq` and `conv_dpid_seq_<account>` to the same value; `contacts`, `contact_inboxes`, `conversations` in id order, `messages` in time order, attachments with their blobs and bytes, tags and taggings, `reporting_events`; set every sequence past its last id; assert `id = display_id`.
5. **`auth.db`:** `bridge_threads` and `draft_outcome` by insert with their own times; the drafts waiting at T through `offer_draft(now=)`; the few `conversation_state` rows; the web visits' claims.
6. **Core:** the hand-over cards and their events (the board loader's job; listed here because their instants are the hand-offs').
7. **Start Chatwoot's workers, then the product.** The cable's first resync fills `conversation_state` from Chatwoot's open and pending lists and alerts nobody (`conversations.md:115-119`); the day's priority thresholds are taken from the last 28 days of seeded replies (`:299-301`).
8. **Read back, as the product reads:** (a) `reads.conversation_facts`, `message_facts`, `reply_episodes`, `resolutions` as `traciora_reader` over the six months, through `stats.period_block` and `operators_block`, equal to the numbers the seeder computed from its own files with the same percentile function; (b) `GET /api/manager/conversations?tab=all` as the senior: the open set's ids, channels, owners, labels, shown levels, waits; (c) `GET /{id}/messages` for every hand-written conversation: kind, sender, privacy, text and files in order equal the file; (d) `GET /{id}`: the waiting draft's words; (e) `GET /stats?period=30d&channel=` for each channel; (f) a search `q=` for a phrase of one resolved story chat; (g) `agent_turn`, `bridge_outbound` and `handoff_owed` are empty, no row is dated after T, and after two minutes of the priority clock no seeded chat has gained an activity line.

**Main risk:** the loader copies conventions that live in Chatwoot's code, not in its schema (the display-id trigger, the label cache beside the taggings, the activity wording that the session cut depends on, the storage layout of a blob). Check (g) and (c) are what catch a wrong copy; a Chatwoot upgrade means re-deriving them.

Two things to settle with the seeder's owner: the shown level written to `conversations.priority` must be the one `priority.waiting_level` gives at T with the thresholds the product will compute (`C/sync.py:206-207`), or the 60-second job rewrites it and leaves a line dated today (`conversations.md:316-319`); and no open chat may be silent for 7 days at T, or Chatwoot resolves it on its first pass (`CONVERSATIONS_AUTO_RESOLVE_DAYS`, `conversations.md:568`).

## 3. Seeded chats in a live demo

What the code does when a manager replies:

| The chat's thread | Bridge | Result | Reference |
|---|---|---|---|
| `chat:default` | always built, needs no secret | **sent**: the bridge only acknowledges; nobody's page is open | `C/chat_bridge.py:93-95, 100-102` |
| `telegram`, `vk`, `avito` | not built (no credentials in the vault) | **refused before posting**: 503 `channel_unavailable`, a toast | `C/sender.py:53-55`, `api/routes/conversations.py:229-239` |
| the same | built with real credentials | posted, then marked "Not delivered — Telegram: chat not found" with Retry | `C/telegram_bridge.py:406-407`, `C/relay.py:267-270` |
| no thread row | none | posted into Chatwoot and shown as sent, but the chat is in no channel | `api/routes/conversations.py:784-788` |

So today only the web chat takes a reply. Private notes, labels, priority, assignment, resolve, drafts and Regenerate work on every channel.

**Decided by the owner (2026-11-13; ledger `conv.live_demo`):** in a live demo a reply is sent in the web chat only. Telegram, VK and Avito carry history: resolved chats and chats waiting on the customer. No product change, no bot token, no script line.

What that means for the state at T (ledger `conv.open_at_t`):

- Every messenger session older than a day is resolved (by a person or by the 7 silent days). An open messenger chat at T waits on the customer: its last public line is the shop's and no draft sits in its box.
- Open or pending at T: 9 (EN) and 14 (RU) chats. EN: 8 web chats (4 open, 4 pending and the assistant's) and 1 Telegram chat. RU: 10 web chats (5 open, 5 pending), 3 Telegram chats and 1 VK chat.
- The chats that wait on the shop at T are web chats, and they are named: S7's return chat (owned by slot 6, one draft: the draft the junior edits and sends in front of a buyer), S6's chat (owned by slot 23, urgent by its wait, one draft), and in the Russian configuration one background chat. A2's weekly thread is the named open messenger chat: Telegram, this week's vans confirmed, waiting on the customer.
- S7's dates sit inside the web chat's memory of a visitor: the browser's subject lasts 30 days from her first chat (`conv.web_visitor_memory_days`), so her three chats are one contact's.

**What a resolution does to a waiting draft: nothing.** This was read in the product at commit `af75145b8`.
- A status change, by a person or by Chatwoot's auto-resolve after 7 silent days, reaches the product as `conversation.status_changed`. That event only refreshes the chat's `conversation_state` row (`C/sync.py:57`, `:400-403`). The status route only toggles the status in Chatwoot (`api/routes/conversations.py:877-887`).
- A draft leaves the box in three ways only:
  - a message goes out: `draft_sent` or `own_text_sent` into `_empty_box` (`C/conversations_store.py:429-439`, `:452-456`; called at `api/routes/conversations.py:807`);
  - a manager clears it: `clear_draft` (`C/conversations_store.py:441-450`, called at `api/routes/conversations.py:1017`);
  - a newer draft replaces it as `replaced_unseen`, with no manager (`C/conversations_store.py:385-415`, the outcome at `:405-409`).
- The nightly prune deletes only `conversation_state` rows of closed chats idle 30 days (`C/conversations_store.py:48`, `:328-331`; `C/jobs.py:43`), never `conversation_draft`.

So a draft left waiting at a resolution stays in the box with no outcome row. If the customer writes again (a messenger reopens the same conversation), the first new draft writes `replaced_unseen` for it at that instant. If nobody writes again, which is always the case on the web chat (a new visit is a new conversation), the resolved chat keeps the draft for good, and no outcome ever counts it.

**Rule for the seed:** this changes what a closed chat may hold, so:
- A seeded chat that is resolved at T has no `conversation_draft` row.
- A session the 7 silent days resolve ends on a public line of the shop, or on a draft that a person acted on before the resolution.
- One exception, on a messenger conversation that has a later session: a draft left at the resolution gets its `replaced_unseen` row (manager null), dated at the later session's first draft. It counts in `conv.draft_replaced_unseen`.
- The hand-written conversations already keep this rule: no closed chat ends with a draft in its box.

## 4. Taxonomy

The tenant's settings (R9), the same in both markets (`conv.assistant_mode`, `conv.ownership`, `conv.auto_resolve_days`): `CHATWOOT_CHAT_ASSISTANT=sends`, `CHATWOOT_TELEGRAM_ASSISTANT=drafts` (the product ships `sends`; the owner set it to drafts for the demo tenant, and the advisors' reply-time rows need a channel where people answer first), VK and Avito `drafts` (shipped), `CONVERSATIONS_OWNERSHIP=first_reply`, auto-resolve 7 days. The business's reason: strangers on the website get an answer at any hour; in a messenger, where customers write about a car already in the shop, a person answers and the assistant prepares the words.

**Volume**, sessions a day, company (`conv.sessions_per_day`):

| | Web chat | Telegram | VK | Avito | All |
|---|---:|---:|---:|---:|---:|
| EN weekday | 11 | 5 | | | 16 |
| EN Saturday / Sunday | 4 / 3 | 2 / 0 | | | 6 / 3 |
| RU every day | 5 | 11 | 3 | 5 | 24 |

- EN: 74.0 inbound calls a day (37.0 orders × 2.0) × 0.15 written for every call ÷ 0.70 gives 16. RU: 61.6 calls a day (28.0 orders × 2.2), of which 62 % are enquiries, × 0.383 ÷ 0.65 gives 22.5, designed at 24; 0.383 is Callibri's 27.7 % of enquiries that are not calls (`ru-shop.md` section 5, read) and the divisor leaves room for existing-job sessions. EN has no source for the written share (`us-shop.md`, gap 11); 0.15 is designed in 0.10 to 0.25. Per inbound call that is 0.216 and 0.39 sessions (`conv.sessions_per_call`).
- Six months (175 days): 2,179 sessions before the season (EN; about 2,300 with June and July at +15 % inside) and 4,444 (RU, the four tyre weeks at +40 %) (`conv.sessions_product_period`, `conv.season`); 21,000 and 60,000 message rows with notes and activity lines (`conv.message_rows`).
- 30 % of web-chat sessions arrive outside opening hours; 12 % of messenger sessions (`conv.out_of_hours`).
- Of sessions a person handles, the customer's shop is known in 85 % (`conv.shop_known`); those go to that shop's advisors in the ledger's order shares, and at `west`, where the manager also answers, in the answered-call shares (`conv.person_share`). The rest go to whoever answers first. A person handles 9.95 sessions a weekday (EN) and 21.3 a day (RU) (`conv.handled_per_day`).

**Why people write**, share of sessions (`conv.reasons`, `conv.reasons.alone_on_web`):

| Reason | EN web | EN Telegram | RU web | RU Telegram | RU VK | RU Avito | Ends with the assistant alone, on the web chat |
|---|---:|---:|---:|---:|---:|---:|---|
| what a job costs | 26 | 14 | 30 | 20 | 24 | 42 | 60 %: a menu price is public; a quote for this car is a hand-off |
| to book or ask for a slot | 24 | 18 | 22 | 22 | 22 | 20 | 20 %: it cannot book, and one customer in five declines the hand-over and says they will call |
| hours, address, do you work on this | 20 | 6 | 16 | 6 | 12 | 14 | 95 % |
| a symptom: "is this serious", often with a photo | 12 | 8 | 12 | 10 | 12 | 8 | 35 % |
| is my car ready, has the part come | 5 | 24 | 5 | 18 | 8 | 2 | never: it cannot read the shop system |
| found work: photos sent, approve or decline | 2 | 16 | 2 | 12 | 6 | 0 | never |
| moving or cancelling a booking | 4 | 8 | 4 | 6 | 6 | 2 | never |
| complaint, comeback, the bill | 3 | 4 | 4 | 4 | 6 | 4 | never |
| company account: weekly bookings, quotes, documents | 1 | 2 | 2 | 2 | 0 | 6 | never |
| spam, sellers, wrong business | 3 | 0 | 3 | 0 | 4 | 2 | 100 % |

Designed (X), each row ± 5 points. Avito is a listing, so it is priced first; Telegram is where the shop already has the customer's car.

**Who answers first, and hand-offs** (`conv.web.alone` 46.6 and 44.8, `conv.web.handed_over`, `conv.web.abandoned` 8.4 and 9.2, `conv.assistant_alone_all`, `conv.handoff_kind`):

| | EN | RU |
|---|---:|---:|
| Web chat: the assistant answers first | 100 % | 100 % |
| ... ends with the assistant alone | 47 % | 45 % |
| ... handed over | 45 % | 46 % |
| ... customer left before a hand-off could be made (no number given) | 8 % | 9 % |
| Messengers: a person answers first | 100 % | 100 % |
| Sessions the assistant ends alone, all channels | 32 % | 9 % |
| Hand-off kind: `scheduling` / `escalation` | 70 / 30 | 65 / 35 |

A hand-off is made only after the customer typed a name and a number, so it comes two to four customer lines later than the question. On a drafts channel there is almost no hand-off: the chat is a person's from its first line and the assistant's question for a number would itself be a draft.

**Length and timing:**

| | EN | RU |
|---|---:|---:|
| Public lines in a session, median: assistant alone / person-handled | 4 / 8 | 5 / 11 |
| Customer lines sent in a burst (a thought in two or three messages) | 25 % of customer turns | 45 % |
| The assistant's reply on the web chat | 20 s median, 45 s at the 90th percentile (the 10 s typing wait, `conversations.md:389-390`, plus the model) | same |
| A draft appears on a messenger | 45 s median (30 s wait) | same |
| A person's first reply in a session, median (`pNN.first_reply_min`; defined in section 8 and in `conv.first_reply.definition`) | slot 5: 14 min, 6: 4, 7: 9, 29: 20, 16: 6, 17: 11, 22: 35, 23: 40, 24: 7 | the same, slot 29: 12 |
| A person's later replies in a live exchange | 0.6 × that row | same |
| The slowest tenth of a person's replies | 5 × that row; for slots 22 and 23 the next working day | same |
| Customer photos, of person-handled sessions | 14 % | 22 % |
| Voice messages, of Telegram sessions | 1 % | 6 % |
| Staff files: an estimate, a photo of the worn part | 9 % | 12 % (on Avito a photo only: it carries no other file, `C/avito_bridge.py:98-99`) |

The assistant reads a photo; it cannot hear a voice message and says so (`docs/features/chat-attachments.md:39-47`, `C/attachments.py:330-332`).

**Unclear customers (R13).** A session has a clarification loop when the customer's words can be read two ways or name the wrong thing, the first question does not settle it, and it has to be asked again or put another way. Asking "what car" is not a loop.

- **12 %** of sessions have at least one loop, as for calls (`r13.chats.clarification_loop`); a third of those need two (`r13.chats.two_loops`, 4 %). **3 % of sessions end unclear** (`r13.chats.unresolved`), against 2 % of calls: in a chat the customer can stop answering. Range 2 to 4.
- It is a property of the customer, drawn per session and independent of the advisor. Weights: by reason, symptom 1.6, booking 1.3, price 1.3, found work 1.0, status 0.5, hours 0.3; by channel, Avito 1.4, others 1.0.
- What the advisor does with it is the person's: the chance they ask instead of answering their first reading is 95 % (slot 16), 85 % (6, 24), 80 % (29), 75 % (5), 60 % (17), 45 % (7), 30 % (23), 25 % (22) (`conv.unclear`). A wrong first answer is corrected by the customer (a loop) or ends the session (unclear). So the weak desks have more sessions that end unclear without having more unclear customers.
- **The assistant** asks one plain question, then offers two readings ("on the brake pedal, or coasting?"); it stays on the question (`escalation.md:223-227`) and does not guess a job or a price. Clear after that: it answers or hands over, and the hand-off note carries the customer's own words and says what was asked. Still unclear: it hands over as `escalation` if it has a number, else the chat stays its own, unanswered by the customer, until the 7 days resolve it. In a draft the clarifying question is the draft, and its outcome shows what the advisor did: sent, or discarded for a guess.

**Labels** (the tenant's; one topic on 60 % of person-handled sessions, by person: 6, 16, 24 nearly always; 5, 17, 7, 29 half; 22, 23 almost never; `conv.label_share`): `booking`, `price`, `status`, `approval`, `complaint`, `fleet`, `tires`; `запись`, `цена`, `статус`, `согласование`, `жалоба`, `юрлицо`, `шины`; plus the product's `handoff`.

**Priority** (`conv.priority_set`). A manager sets a base on 5.5 % of person-handled sessions: high 4 % (complaints, company accounts), urgent 0.5 %, low 1 %. Everything else moves by the wait.

**Resolution.** A person resolves 55 % of the sessions they handled (slot 6: 85 %, 16: 80 %, 24: 80 %, 7: 60 %, 29: 55 %, 5: 50 %, 17: 45 %, 23: 15 %, 22: 10 %; `conv.resolved_by_person`); the rest, and every session the assistant ended alone, are resolved by Chatwoot after 7 silent days, with no person on the event. 1 % are snoozed at some point.

**Draft outcomes**, of drafts a person acted on (`conv.draft_outcomes`; `replaced_unseen` apart: 18 % of all drafts, a customer wrote again before anyone looked, `conv.draft_replaced_unseen`):

| Slot | Sent as is | Sent edited | Discarded | In words |
|---|---:|---:|---:|---|
| 5 | 50 | 10 | 40 | types slowly: takes the draft or writes "call me, easier" |
| 6 | 45 | 40 | 15 | uses it, trims it |
| 7 | 70 | 15 | 15 | sends what he is given |
| 29 | 30 | 20 | 50 | types with two fingers: writes her own, slowly, or walks the answer over to slot 6 |
| 16 | 20 | 60 | 20 | rewrites into her own voice, signs it |
| 17 | 40 | 25 | 35 | |
| 22 | 5 | 5 | 90 | "will do" |
| 23 | 15 | 5 | 80 | his own five words |
| 24 | 35 | 50 | 15 | adds the estimate |

Slot 29 joined the cast after this design was drafted; her rows here and in the lists above were set in the reconcile pass from her voice note in `cast.json`.

**Avatars** (`conv.avatars`; owner, 2026-11-13). The product shows a picture only for a customer contact; staff show initials. About 60 % of messenger contacts (Telegram, VK, Avito) carry an avatar and 40 % none. An avatar is always a photo with no person in it: their car, a pet, a view. The files come from free photo sites whose terms allow it, each recorded with its source and licence and kept in the private repository; no faces in v1. Web-chat visitors have no picture, as in the product.

## 5. Building a background conversation

`conversation = wording( scenario, channel mode, advisor's sheet, market )`

1. **Scenario**: the reason, the customer (first-time, known, company contact), the car from `parc.json`, the job and its price on that day from `catalogue.json`, whether there is a photo or a voice message, whether the customer is unclear and how it ends, the hour (in or out of opening hours).
2. **Channel mode** fixes the frame: on the web chat the assistant speaks first and the session ends alone, handed over or abandoned; on a messenger each customer turn raises a draft and the advisor's row decides its outcome.
3. **The advisor's sheet**: the reply delays above, the draft outcomes, the chance of a label, of resolving, of asking again, and the voice note from `cast.json` (slot 5 "call me, easier", slot 7 answers the first of two questions, slot 16 signs, slot 17's second answer waits an hour, slot 22 next day, slot 23 at closing time, slot 24 by points with the estimate).
4. **Market language**: every line comes from banks written in that language from nothing.

| Piece | Count per language | Gives |
|---|---:|---|
| skeletons: 8 each for price, booking, status and symptom; 5 each for the other six reasons | 62 | × job block × customer voice |
| job blocks, the 24 jobs of the calls design with their chat wording (what people call the job, the photo they send) | 24 | |
| customer voices: lower-case fragments, dictated run-on, polite and complete, emoji, businesslike, older and formal, photo first, one-word answers | 8 | |
| unclear openings (vague, wrong part named, two requests in one, wrong way round) with their second answers | 20 | R13 |
| advisor bank: 9 advisors (slot 29 added) × 12 moves (greet, ask, price, offer a time, confirm, not yet, moved, found work, decline a discount, sorry, close, pass on) × 3 wordings | about 320 lines | the person |
| assistant bank: 20 moves × 3 wordings, the facts filled from the public pages | 60 lines | the assistant sounds like one writer, on purpose |
| private notes: 30 | 30 | staff talking to staff |
| picture pool: dashboards with a lamp on, a worn pad, a tyre sidewall, a puddle under a car, a paper estimate, a registration card (RU); 6 voice stubs | 40 pictures, 6 stubs per market | fixed files made once, not at build time (R3) |

A manager sees one day's list, at most 24 sessions, 6 of one reason: 8 skeletons × 8 voices cover it without a repeat inside a week.

**What the generator renders, and what is a pool key.**
- The generator renders the text of every background session from the banks, with its slots filled, at build time.
- A picture or a voice message, in a background or a hand-written conversation, is a **pool key** with a description (`photo`, `voice_len`, the `files` of a staff line). The loader attaches the pool's file under that key: an attachment row, an Active Storage blob and the bytes.
- The pool's files are fixed files made once, outside the generator (design rule R3), and they are not made yet ("Not in this plan"). Until they exist, the loader writes no attachment row for a key, because a row without bytes is a broken tile, and leaves out a line that is only a file (section 1).
- An avatar is the same: a file from `conv.avatars`, not something the generator renders.

### Assembler rules (for the generator)

The banks are `bank-en/` and `bank-ru/`. The generator's own test suite runs the test named with each rule on sessions assembled over many random seeds (at least 40 seeds per language), never on one fixed seed.

1. **One price per job per conversation, and its tax basis said.** A job's price is drawn once per conversation (`catalogue.json` on the session's day, for the car's class and tier). Every line that gives it (the assistant's page figure, a person's quote, a draft, the customer typing it back) gives that figure, and says whether it is before or after tax.
   - English: `job_price` is before tax and `job_total` is with shop supplies and tax.
   - Russian: `job_price` is the price as paid, VAT inside, and `job_total` is with shop supplies, VAT inside.
   - A page figure (`page_price`, `page_low`, `page_high`) is quoted exactly as the public page states it, and a stale page is never quoted in a background session. When a person's quote for this car differs from the page figure (another class, another tier), the person's line says why.
   - *Test:* in every conversation, each job carries one money value per basis, and every line that gives a figure names its basis or carries it in its slot.
2. **A speaker says a beat once.** The customer does not ask the same question twice unless the skeleton's beat is a repeat on purpose (a nudge, or an R13 loop). A person or the assistant does not give the same answer, greeting or sign-off twice in a session; a draft and the message it became count as one. *Test:* no beat role other than nudges and R13 loops occurs twice for one speaker in a session, and no two public lines of one speaker are equal, ignoring case and punctuation.
3. **A follow-up only where its premise was said.** A follow-up is kept only when the line it rests on was said earlier in the session:
   - a "then see you at {time_agreed}" needs a time agreed;
   - a thanks after a hand-over needs the hand-over;
   - "go ahead with the {finding_item}" needs the finding presented;
   - a customer's "so it's {heard_price}?" needs a figure given;
   - an `echo` draft needs the time a person set;
   - a draft with `defers` needs the person's own answer to follow it.
   *Test:* every line whose beat or key needs a premise (the generator's table) has it earlier in the session.
4. **Lengths: designed against assembled.**
   - Designed: public lines in a session, assistant alone and person-handled, are 4 and 8 in English and 5 and 11 in Russian, each ± 2 (`conv.lines_per_session`). The web chat ends with the assistant alone in 47 % (English) and 45 % (Russian) of sessions (`conv.web.alone`).
   - Assembled: the Russian bank at an even draw gives person-handled sessions a median of 6 public lines, and the assistant alone on 60 % of web chats.
   - **The generator must reach the ledger rows.** It weights the long skeletons up, lays in the `extra` exchanges (Russian) or the `more` turns (English), and weights the skeletons by their `ends` so that each reason's ending shares of section 4 hold.
   *Test:* over many seeds, the median public lines per kind are within the ledger's ± 2, and the alone share of web chats is within 5 points of `conv.web.alone`.
5. **Gearbox-bound jobs** follow `../calls/DESIGN.md` section 3, rule 7: the English chat block `atf_drain_fill` is never drawn for a model sold without an automatic, or for an electric car.
6. **Contact and thread identifiers belong to the seeder.** Chatwoot contact ids and identifiers, web-chat visitor subjects, visit ids and thread keys are drawn at random by the seeder, inside the fictional ranges of section 9 (`conv.fictional_ids`). Patterned ids in the hand-written files (`chat_seedv1-browser-en-NNNN`, `5eedc0de-…`) are placeholders the seeder replaces (review 2, finding 35); the same applies to a transcript's `engine_version`. *Test:* no loaded id matches a placeholder pattern, and every Telegram, VK and Avito id is inside its fictional range.

**The two banks' formats differ, and must be reconciled into one format document before a generator is planned.** `bank-ru/FORMAT.md` follows `bank-en/FORMAT.md` as it stood at 2026-11-14 00:01 and adds 26 items. Neither bank is edited here. The differences:

- **The Russian bank adds:**
  - Grammar:
    - case-suffixed slots (`_acc`, `_gen`, `_dat`, `_prep`, `_on`, `_for`, `_from`, `_at`) filled from the `forms` tables (cars, days, shops);
    - capitalised slots (`{Job}`);
    - the customer's gender: `[[он|она]]`, and `g` on a pool entry or voice stub;
    - a number carries its noun;
    - money as a person types it (`_bare`, `_num`);
    - a greeting by the hour (`hello`, `hello_lc`), never repeated in a second message.
  - Customer messages:
    - `ch` channel lists;
    - job-block keys `staff_says {nom, acc}`, `short`, `said_inf`, `said_acc`, `advice`, `listing`, `finding` keys and the `price_kind` values;
    - `steps` and `findings`;
    - opening keys `kind`, `only` and `burst`, and named reason parts;
    - the generic additions (`give_phone`, `give_name`, `pick_more` and others);
    - a voice stub's fixed `seconds`.
  - Assistant: `quote` in place of the English `item`; the moves `greet`, `{price_move}`, `{advice_move}` and `{towing_move}`; the hand-off notes `unclear` and `unclear_never`; the draft group `tyres`; `defers` set by key.
  - Advisors: `sheet.curt`, `sheet.no_price`; the moves `sorry`, `thanks_reply`, `ask_lead`, `guess_tail` and `call_me`; an edit's `fits` and `sent: null`.
  - Skeletons: the `when` keys; customer-beat keys `kind`, `two`, `photo`, `stub`, `voice` and `if: "nocar"`; a staff beat without `reply`; `extra` beats with `reasons.json` `exchanges`; `end.how` `person` or `inactivity`.
  - Unclear loops: `second_to_guess`, `job` and `guess_job`, `reads`, `never_customer`, and two `level_0` wordings.
  - Notes: `slot`, `acks` and `labels.use`.
  - Plain-text sources in `_src/`, built by `_src/build.py`. The English `reasons.json` is edited by hand and its skeleton builder was not shipped.
- **The English format has, and the Russian bank does not use:**
  - the line keys `item` and `for_skeletons`;
  - the job-block key `symptom_more`;
  - the unclear-loop key `channels`;
  - the slots `last_name`, `full_name`, `phone`, `sir_maam`, `advisor_first`, `tech_first`, `manager_first`, `diag`, `finding_item`, `finding_b_item`, `appt_day`, `eta_day`, `page_item`, `next_open` and `sat_hours`. The Russian bank has case-form slots of its own in place of several of them.

## 6. Hand-written conversations

Once per language. Days are anchors of rule R6, as on the cards and in `../stories/TIMELINE.md`. "Open" and "pending" are the state at T. Every chat that waits on the shop at T is a web chat (`conv.live_demo`).

| # | Story | Channel | People | When | State at T |
|---|---|---|---|---|---|
| 1 | S7 | web chat | the private customer, assistant, slot 6 | 21:10 on the evening before day A; picked up on day A at opening (sample 1). Day A is slot 6's 14th working day before T (RU: her 10th) | resolved by 6 |
| 2 | S7 | web chat | the same | slot 6's next working day after A, the day of the visit: she approves the brakes and declines the shock absorbers in a new visit, handed over, 6 confirms; her thanks the day after | resolved by 6 |
| 3 | S7 | web chat | the same, the same contact: under 30 days since her first chat | slot 6's last working day before T, 15:40: she asks to book the deferred work; the assistant answers from the price list and hands over; 6 replies at 16:05 and owns the chat. On T's date, 30 minutes before T, she writes again | **open**, owned by 6, unread, draft waiting: the draft the junior edits and sends in a live demo |
| 4 | S1 | web chat | A6's new contact; slot 5's note; slot 7 | the Tuesday of week T-4: a quote request that waits two days for a person's first reply (card S01; ledger `s1.dates`, `s1.a6`). Sample 2 was written before the card: it is a Telegram (EN) or Avito (RU) thread nine weeks before T with call 22 inside it, and is to be rewritten to the card | resolved by inactivity |
| 5 | S1 | Telegram | A2's dispatcher, slot 16 | one conversation, a session every week since go-live; 4 written, the others built from them | **open**: this week's vans confirmed, waiting on the customer |
| 6 | S6 | web chat | the waiting customer; assistant; slot 23; notes by 24 and 22 | four messages in the nine days the car waits, the last on `west`'s last full open day before T (sample 3; the card gives 7, 5, 3 and 1 days before T) | **open**, owned by 23, urgent by wait, draft waiting |
| 7 | S13 | web chat | a customer, assistant | the 2nd full open day before T (sample 4a) | **pending**, answered |
| 8 | S13 | Telegram (EN), VK (RU) | a regular of `east`, slot 16 | slot 16's last working day before T (sample 4b) | resolved by 16 |
| 9 to 24 | people | mixed | two per advisor, slots 5, 6, 7, 16, 17, 22, 23, 24 | spread over the six months | resolved |
| 25 to 27 | R13 | web chat, Telegram, Avito (RU; EN: web chat) | clear after one question; after two; never | the Wednesdays of weeks T-13, T-6 and T-2 | resolved; the third by inactivity |

Background never uses a story customer, and no background chat at `west` is older than five days and open.

## 7. File format

One JSON file per story thread and language, `format: "seed-conversation/1"`; the eight files in `samples/` are the reference.

| Key | Holds |
|---|---|
| `id`, `configuration`, `story`, `title`, `demonstrates`, `nominal_t` | what it is; the T the literal dates in the text were written for |
| `cast`, `scenario` | the customer (a reference into `named_customers.json` or `accounts.json`, or invented), staff slots; who writes, about what, what happens, the facts the words rest on, and `unclear` (R13) when it applies |
| `floating_days` | every weekday or date in the text with its offset, as in the calls format |
| `conversations[]` | one Chatwoot conversation each: `channel`, `bridge`, `assistant_mode`, `clock` (whose wall clock the times are in), `thread_key`, `peer`, `contact`, `opened` |
| `conversations[].timeline[]` | in order, each with `day` and `at`: `message` (`from` customer, assistant or a slot; `text`; `files`), `note` (author, `mentions`), `draft` (`text`, and `outcome`: kind, who, when, which message it became), `handoff` (the tool's arguments, the note, the card), `activity` (assigned, label, priority, resolved, reopened), `outside` (a call or an order in another store, for the reader) |
| `conversations[].state_at_t` | status, owner, labels, base and shown priority, the wait, unread, the draft in the box |
| `conversations[].reads_back` | what the product must show for it: who answered first and after how long, the waits, the resolutions, the outcome rows |
| `why` | what to look at |

Activity lines are stored as facts (`{"what": "resolved", "by": 6}`); the loader writes Chatwoot's own sentence for them in the account's locale.

## 8. The Stats screen and the rows that drive it

| Block (`conversations.md:527-534`) | Driven by | What it should say |
|---|---|---|
| Now | the open set at T (`conv.open_at_t`); shifts | 9 open (EN), 14 (RU); 2 and 3 waiting, all of them web chats; the longest wait is S6's |
| Period totals | sessions a day by channel; the share that opens a new conversation; messages per session; assistant-alone share; resolution shares | EN 30 days: about 385 sessions shown as about 310 new dialogs, two assistant lines for every three of the managers'; RU: 720 sessions shown as about 400 new dialogs, because messenger sessions reopen (section 10) |
| Speed: first answer | channel modes; people's reply rows | EN median under a minute (the assistant), 90th percentile near 40 minutes; RU median about 8 minutes |
| Speed: await, resolution | people's rows × 0.6; the 7 silent days | the long tail is `west` |
| Rhythm | the hour curve (the calls' curve, shifted an hour later, with an evening shoulder on the web chat) | traffic after closing is the assistant's |
| Drafts | the outcome sheet | about a third each way; with the channel set to Telegram the split by person shows |
| Per operator | reply rows, draft sheet, resolve shares | slot 6: 4 minutes, most chats; slot 23: 40 minutes, almost every draft discarded, few resolved; slot 24 beside him: 7 minutes |

The per-operator "first answer" is credited only when a person wrote the chat's first public line (`conversations.md:540-544`), so on the web chat it is nobody's. The ledger's "first chat reply" (`pNN.first_reply_min`, `conv.first_reply.definition`) is therefore the wait before a person's first line in a session, in working minutes, which the screen shows as the operator's await time and, for chats born on a messenger, as first answer.

## 9. Ledger rows proposed

Merged into `../ledger.json` in the reconcile pass. The last column gives the ledger's decision and key; where the ledger adjusted a row, the cells carry the ledger's value.

| Key | English | Russian | Class | Basis | Ledger |
|---|---|---|---|---|---|
| assistant mode: chat / telegram / vk / avito | sends / drafts / – / – | sends / drafts / drafts / drafts | X | section 4; Telegram differs from the shipped default | accept: `conv.assistant_mode` |
| ownership; auto-resolve | first reply; 7 days | same | X | shipped defaults | accept: `conv.ownership`, `conv.auto_resolve_days` |
| written sessions per inbound call | 0.216 | 0.39 | D | 16 sessions over 74.0 calls a day; 24 over 61.6 | adjust: `conv.sessions_per_call`, derived from the sessions a day over the ledger's calls a day (the Russian 0.59 rested on 1.4 calls an order) |
| sessions a day by channel | web 11, Telegram 5; Saturday 4 + 2; Sunday 3 | web 5, Telegram 11, VK 3, Avito 5 | D / X | calls a day × the row above; the split is X: EN 70 / 30, RU 21 / 46 / 12 / 21 | accept: `conv.sessions_per_day` |
| season on sessions | +15 %, June and July | +40 %, the four tyre weeks | X | S11 | accept: `conv.season` |
| outside opening hours | web 30 %, messengers 12 % | same | X | range 20 to 40; 8 to 16 | accept: `conv.out_of_hours` |
| shop known, of person-handled sessions | 85 % | 85 % | X | | accept: `conv.shop_known` |
| reasons by channel | table in section 4 | same | X | ± 5 points a row | accept: `conv.reasons` |
| web chat: alone / handed over / abandoned | 47 / 45 / 8 | 45 / 46 / 9 | D | the reasons table × its last column | accept: `conv.web.alone` (derived from the reasons), `conv.web.handed_over`, `conv.web.abandoned` |
| sessions that open a new conversation | web 100 %, Telegram 35 % | web 100 %, Avito 80 %, Telegram and VK 30 % | X | a messenger customer's later sessions reopen the old one | accept: `conv.new_conversation_share` |
| hand-off kind, scheduling / escalation | 70 / 30 | 65 / 35 | X | | accept: `conv.handoff_kind` |
| public lines a session, alone / person-handled | 4 / 8 | 5 / 11 | X | range ± 2 | accept: `conv.lines_per_session` |
| customer turns sent as a burst | 25 % | 45 % | X | | accept: `conv.burst_share` |
| assistant's reply, web chat | 20 s median, 45 s p90 | same | D / X | 10 s wait + model | accept: `conv.assistant_reply_s` |
| a person's later replies | 0.6 × first-reply row | same | X | | accept: `conv.later_reply_factor` |
| slowest tenth of replies | 5 × the row; 22 and 23 next working day | same | X | | accept: `conv.slowest_tenth` |
| customer photos; voice; staff files | 14 %; 1 %; 9 % | 22 %; 6 %; 12 % | X | | accept: `conv.files` |
| sessions with a clarification loop; two loops; ending unclear | 12 %; 4 %; 3 % | same | X | R13; controller's 12 and 2, the last raised for chat | accept: `r13.chats.clarification_loop`, `r13.chats.two_loops`, `r13.chats.unresolved` |
| unclear weights by reason and channel; advisors' chance to ask | section 4 | same | X | | accept, slot 29 added: `conv.unclear` |
| a topic label, of person-handled sessions | 60 % | 60 % | X | by person, section 4 | accept, slot 29 added: `conv.label_share` |
| manager-set priority: high / urgent / low | 4 / 0.5 / 1 % | same | X | | accept: `conv.priority_set` |
| resolved by a person, of sessions they handled | 55 %; by person, section 4 | same | X | | accept, slot 29 added: `conv.resolved_by_person`, `conv.snoozed` |
| draft outcomes by person; `replaced_unseen` | table in section 4; 18 % | same | X | each cell ± 10 points | accept, slot 29 added: `conv.draft_outcomes`, `conv.draft_replaced_unseen` |
| open or pending at T | 9: web 8 (4 pending), Telegram 1 | 14: web 10 (5 pending), Telegram 3, VK 1 | X (fixed) | section 3 | adjust to the owner's decision: `conv.open_at_t`, `conv.live_demo` |
| hand-written conversations | 27 | 27 | X (fixed) | section 6 | accept: `conv.handwritten`; the threads' channels adjusted in `conv.story_threads` |
| pattern counts; picture pool | section 5 | same | X | | accept: `conv.patterns` |
| first chat reply by person | section 4 | section 4 | X | the people rows | accept the definition of section 8: `pNN.first_reply_min`, `conv.first_reply.definition`, `conv.person_share` |
| avatars of customer contacts | 60 % of messenger contacts, a photo with no person; none for web visitors | same | X | owner, 2026-11-13 | new: `conv.avatars` |
| a visitor remembered by the web chat | 30 days | 30 days | M | the product's cookie | new: `conv.web_visitor_memory_days` |
| fictional ids | Telegram peers 4503599627370497 and up | the same; VK peers 1,990,000,000 to 1,999,999,999; Avito chats `u2i-seedv1-…`, users and items 15 digits from 900… | X | below | accept, unverified: `conv.fictional_ids` |

**Identifiers that cannot be real accounts.** Telegram: a user id has at most 52 significant bits by the Bot API's own statement, so ids above 2^52 name nobody; no `@handle` is stored anywhere (a contact's name is the display name, `C/telegram_bridge.py:305`). VK: user ids are handed out in order and are near one billion; the top hundred million under 2,000,000,000 (where group chats begin) is unissued, the same guarantee as the ledger's tier-B phone numbers. Avito: ids are scoped to the seller's account, and the seeded forms are longer than any id Avito issues; listing links are under `.example`. Web chat: the browser subject and the visit id are random strings of ours. Phones: `phones.md`. The Telegram and VK ranges are from memory and are to be checked once against the platforms' documentation.

## 10. Product gaps met (for the owner; outside this plan)

1. **A conversation has no shop.** Three shops share one queue per channel; routing is a habit of the staff, and Stats cannot show a shop.
2. **No way to answer a seeded messenger chat** (section 3). The owner's decision for v1: a reply is sent in the web chat only.
3. **Returning messenger customers are invisible in "new dialogs" and "first answer"**: both count conversations created, and theirs was created months ago.
4. **The views read `conversations.id`, the product keeps `display_id`.** They are equal only while one account lives in the Chatwoot database and nothing was ever deleted.
5. **A hand-off needs a phone.** A customer who will not type one cannot be handed over; on Telegram the number is not known unless shared.
6. **A web-chat customer stays "Website visitor".** The name and number given in the chat reach the note and the card, not the contact. I found no path that writes a phone to a contact except Telegram's shared contact, so S7's customer is two contacts, one without a phone.
7. **The assistant cannot hear a voice message**, a daily event on a Russian messenger.
8. **Avito carries pictures only**: an estimate goes as a photo of the estimate.
9. **The Telegram greeting promises to "book a convenient time"** (`config/locales/en.json:1616`), which the assistant cannot do.
10. **Activity lines are Chatwoot's, in Chatwoot's locale**, and the session cut depends on their wording.

## Settled since the draft, and what is still open

1. **S7 is one contact.** Her three chats are web chats inside the 30 days the web chat remembers a visitor, so Chatwoot holds one contact for her, a "Website visitor"; her name and number are in the hand-off note and on the card (gap 6 stands).
2. **Telegram drafts** in the demo tenant: decided (`conv.assistant_mode`).
3. **"First chat reply"** is defined (`conv.first_reply.definition`); slot 22's share of `west`'s sessions is his answered-call share (`conv.person_share`).
4. **S13's day** is the Thursday of week W+1, or the Tuesday if that Thursday is closed in the market (`site.stocktake`); the samples carry it.
5. **S6's customer** is the one of `named_customers.json` in the card, in the calls samples and here: Curtis Vaughn, 2012 Volvo XC60, the angle gear; Айрат Гизатуллин, Peugeot 308 2011, насос электрогидроусилителя руля.
6. **The founder** is Ray Brennan everywhere.
7. Medium accounts pay list prices (`catalogue.json`), so A6's "price rise" is the full 8 %; sample 2's note says so.

Still open, for the samples' author:

- **Sample 2 against card S01.** The card and the ledger put A6's quote request in the web chat on the Tuesday of week T-4 and call 22 on the Tuesday of week T-9; the sample is one Telegram or Avito thread nine weeks before T with the call inside it.
- **Sample 3's days.** The card gives the four messages at 7, 5, 3 and 1 days before T; the sample's are at 8, 7, 2 and 1 (EN) and 7, 6, 2 and 1 (RU), tied to its weekday words and to the day promised in call 15.
- **Sample 1's questions.** The card says the assistant asks once; the sample takes two clarifying questions.

## Not in this plan

- An S12 chat in which the assistant quotes from the stale public page. Fits the story; not in its footprints.
- The pictures and voice stubs themselves; the Russian and English public pages the assistant quotes (wave 2: the samples' prices and hours are from `catalogue.json` and the ledger).
- The customer agent's memory files for background visitors.
