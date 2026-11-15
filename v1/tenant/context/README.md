# Context notes v1 for the two built-in sources

What the assistant is told about the `core` source (the product's own database) and the `chatwoot` source (the conversations database), as the demo tenant ships them in seed v1. These files are the layer the evals tune: change a note, bump the notes' version, keep the data.

How the seeder applies them. On the first context sync the product copies its shipped notes (`config/sources/traciora/` for `core`, `config/sources/chatwoot/` for `chatwoot`) into the tenant repository at `context/sources/<source>/`. The seeder then writes these files over that copy, in the same commit as the rest of the tenant repository:

- a file marked **extends** is appended to the shipped file of the same path, under the heading `## Demo tenant, notes v1`, with the shipped text left as it is;
- a file marked **new** is written as the table's `annotations.md` (it starts with the manual marker, so no sync overwrites it).

A table's note is seen only by the ranks that read the table (`../SOURCES.md`): the workforce notes, for example, are invisible to a junior.

Conventions only: no note names a person, a customer, a date or a count from a story.

## `core/` (target `context/sources/core/`)

| File here | Kind | Shipped file it extends |
|---|---|---|
| `RULES.md` | extends | `config/sources/traciora/RULES.md` |
| `core/location/annotations.md` | extends | `traciora/core/location/annotations.md` |
| `core/location_alias/annotations.md` | new | |
| `core/location_hours_exception/annotations.md` | new | |
| `identity/person/annotations.md` | extends | `traciora/identity/person/annotations.md` |
| `identity/person_location/annotations.md` | new | |
| `interactions/phone_call_leg/annotations.md` | extends | `traciora/interactions/phone_call_leg/annotations.md` |
| `interactions/phone_call_missed/annotations.md` | extends | `traciora/interactions/phone_call_missed/annotations.md` |
| `workforce/shift/annotations.md` | new | |
| `workforce/punch/annotations.md` | new | |
| `workforce/shift_template/annotations.md` | new | |
| `workforce/shift_change_request/annotations.md` | new | |
| `workforce/availability/annotations.md` | new | |
| `workforce/coverage_requirement/annotations.md` | new | |
| `workforce/roster_publish/annotations.md` | new | |
| `workforce/shift_schedule/annotations.md` | new | |
| `platform/event/annotations.md` | extends | `traciora/platform/event/annotations.md` |
| `platform/activity/annotations.md` | new | |
| `platform/notification_queue/annotations.md` | new | |
| `work/work_item/annotations.md` | extends | `traciora/work/work_item/annotations.md` |
| `work/work_participant/annotations.md` | extends | `traciora/work/work_participant/annotations.md` |
| `work/calendar_event/annotations.md` | new | |
| `work/calendar_event_participant/annotations.md` | new | |
| `work/event_series/annotations.md` | new | |
| `work/event_series_exception/annotations.md` | new | |

Not given notes on purpose: `platform.memory` and `platform.proposal` (no rank reads them through the source; the memory tools read notes and proposals with their owner and rank rules), and the shipped calls views other than legs and misses (their shipped notes already say what the questions need).

## `conversations/` (target `context/sources/chatwoot/`)

| File here | Kind | Shipped file it extends |
|---|---|---|
| `RULES.md` | extends | `config/sources/chatwoot/RULES.md` |
| `public/conversations/annotations.md` | extends | `chatwoot/public/conversations/annotations.md` |
| `public/messages/annotations.md` | extends | `chatwoot/public/messages/annotations.md` |
| `public/inboxes/annotations.md` | extends | `chatwoot/public/inboxes/annotations.md` |
| `public/users/annotations.md` | extends | `chatwoot/public/users/annotations.md` |
| `public/labels/annotations.md` | extends | `chatwoot/public/labels/annotations.md` |
| `traciora/conversation_facts/annotations.md` | new | |
| `traciora/message_facts/annotations.md` | new | |
| `traciora/reply_episodes/annotations.md` | new | |
| `traciora/resolutions/annotations.md` | new | |
