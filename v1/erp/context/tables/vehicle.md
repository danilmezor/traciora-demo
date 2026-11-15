# vehicle

A car on a customer record.
- `customer_id` is the owner on record; an order's customer can differ when the car was booked under someone else.
- `vin` is empty on some old cars. A duplicated customer usually comes with a duplicated car (same VIN or plate).
- `vehicle_class` drives labour hours and parts prices. `unit_number` is a fleet's own van number.
