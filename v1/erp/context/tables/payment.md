# payment

Money in or back, for one order or one statement.
- One statement payment covers all the orders on that statement (English install: always several; Russian install: an invoice usually holds one order).
- `kind`: `payment`, `deposit`, `refund`; amounts are positive, so subtract refunds.
- An order can have more than one payment. A warranty or goodwill order has none.
- `received_at` is local time.
