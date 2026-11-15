---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# workforce.shift_template

One row per named shape of a shift at one shop: its position, local start and end, and the tolerances. late_entry_grace_min is how many minutes after the start a clock-in is still on time; early_exit_grace_min the same for leaving. A shift carries no template id: reach the template by the shift's shop and position (the active one), and use its grace when you judge lateness.
