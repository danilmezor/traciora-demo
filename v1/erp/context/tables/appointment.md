# appointment

Bookings. Many orders have none (drop-ins).
- `status`: `arrived` (then `repair_order_id` is set), `no_show`, `cancelled`; future ones `booked` or `confirmed`.
- A first-time caller may be booked before a customer record exists: `customer_id` empty, `contact_phone` set.
- `source` is where the booking came from.
