# employee

The shop system's staff list, current and former.
- Former staff keep their rows (`left_on`) and their orders still point at them.
- No reason for leaving is recorded.
- A seasonal worker has a new row each season.
- `role` is the system's code; `title` is the job as the company names it (lead advisors are `advisor`).
- Match to people in the product by first and last name; there is no shared key.
- `pay_type` is hidden from lower ranks; pay amounts are not in this database.
