---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.shift_change_request

One row per request by the person standing a shift to change it: kind change_time, change_date or remove. status open, approved, declined, withdrawn, or expired (the shift's day came before anyone decided; the screens show it as declined, but count it as its own status). filed_at is when it was asked, decided_at when a senior answered (empty for expired and open). reason_enc is the person's own words; decision_note_enc the answer.

"Requests filed in the last N days": by filed_at. "What happened to them": group by status, listing expired apart. Open requests at an instant: status open and filed before it.
