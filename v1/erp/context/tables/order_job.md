# order_job

Jobs on an order, each approved, declined or pending.
- Approval is per job: one order can hold both.
- A job raised from the inspection has an `inspection_item` pointing at it; that is "recommended work".
- `deferred` = declined but still needed (a reminder exists).
- `approved_amount` is what the customer agreed to; it can differ from the lines when a price changed.
- `authorized_by` names who said yes on a company vehicle.
