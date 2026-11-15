---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# platform.notification_queue

One row per notification line pushed to one person (person_id) on one channel, with sent_at and, when opened, read_at. Most of a person's Inbox is not stored: it is worked out from the board, the roster, the calendar and the calls when it is read. So this table is not anybody's Inbox; a person's own Inbox is read with the Inbox tool.
