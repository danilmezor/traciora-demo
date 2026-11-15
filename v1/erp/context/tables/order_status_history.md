# order_status_history

Every status change of an order with its local time. Time spent in a status = the next row's time minus this row's; the last row runs to now. An order can wait for parts more than once. A re-issued bill shows `invoiced` twice.
