# repair_order

One order of one car, from estimate to paid; the estimate, the order and the invoice are this one row. A declined estimate or a void is not a visit.
- Filter `status <> 'void'`: voided orders keep their totals.
- Revenue: `order_type = 'customer_pay'`, status `invoiced` or `paid`, before tax = `total - tax_total`.
- An open order is one whose status is not `invoiced`, `paid`, `void` or `declined`.
- `comeback_of_id` points at the order a warranty or goodwill order repeats. Such an order keeps its lines at their prices, holds the whole amount in `discount_total` and has `total` 0, status `paid`, no payment.
- `discount_total` is the sum of the labour lines' `discount` (`order_labor`); part, sublet and fee lines carry none. On a warranty or goodwill order it is the whole amount of the lines and fees instead.
- `opened_at` is the shop's local time.
- `tax_included` says whether line prices contain the tax (true: VAT inside; false: sales tax added).
- `purchase_order_number` is the company customer's own reference.
- Status dates are in `order_status_history`, not here.
