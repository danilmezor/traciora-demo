# location

A shop. Three rows; `name` is what staff call it.
- `time_zone` is the only zone in the database; every timestamp of a shop is its local wall-clock time.
- `tax_rate` is today's rate, and shops can differ (the shop in the other city charges its own sales tax). Each order carries its own `tax_rate`.
- `opened_on` for the bought shop is the purchase day: nothing of it is older.
