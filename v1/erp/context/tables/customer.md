# customer

A person or a company.
- Search by `phone`, not by name: some customers exist twice with the name spelled two ways; one phone = one customer.
- The record named "WALK-IN CUSTOMER" (ru «Розничный покупатель») at the bought shop is a bucket for counter sales, not a customer.
- `payment_terms_days` set = a company account billed on terms; `credit_limit` is set for those only.
- `price_class = 'company_account'` gets the negotiated rates.
- `created_at` of the bought shop's customers is the purchase day (a batch load), not their first visit.
- `notes` holds a company's standing instructions.
