---
type: manual
comment: These are manual notes you want the agent to keep in mind, safe to edit.
---

# identity.person_location

One row per person and shop they are posted at, with the position they work there. is_home marks the one home shop. valid_from and valid_to bound the posting (valid_to empty: current). A person may be posted at two shops at once; the planner offers a person only for shops they are posted at. A posting is not a shift: whether they worked there on a day is workforce.shift.
