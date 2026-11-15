import datetime as dt

from seeder import clock
from seeder.erp import background, orders, reference

AT = dt.datetime(2026, 11, 13, 10, 30)


def built(preplace):
    a = clock.anchors("en", AT)
    b = reference.Build("en", a, 1)
    reference.fill(b)
    preplace(b)
    background.fill(b)
    return b


def test_fill_counts_the_orders_already_there():
    """Orders a story places before the fill stand inside the day's count and the advisors' dealt shares: the day keeps
    its count and slot 5 his orders in the block, whatever was placed first."""
    day = clock.snap("en", AT.date() - dt.timedelta(7))
    block = (AT.date() - day).days // 30
    placed = []

    def preplace(b):
        customer, cars = b.pools["main"][0]
        for n, hour in enumerate((8, 11, 14)):
            job = {"key": "oil_service", "status": "approved", "tech": b.people["12"], "tier": "standard"}
            waits = [(dt.datetime.combine(day, dt.time(hour, 20)), dt.datetime.combine(day, dt.time(hour, 50)))] if n == 0 else ()
            placed.append(orders.order(b, "main", dt.datetime.combine(day, dt.time(hour)), customer, cars[0], "5", [job], pay="cash", waits=waits))

    def visits(b, test):
        return sum(1 for o in b.orders.values() if o["order"]["location_id"] is b.shops["main"] and o["order"]["status"] not in ("declined", "void")
                   and test(o["order"]))

    plain, seeded = built(lambda b: None), built(preplace)
    on_day = lambda o: o["opened_at"].date() == day  # noqa: E731
    assert visits(seeded, on_day) == visits(plain, on_day)
    assert all(id(o) in seeded.orders for o in placed)
    by_five = lambda b: lambda o: o["advisor_id"] is b.people["5"] and (AT.date() - o["opened_at"].date()).days // 30 == block  # noqa: E731
    assert visits(seeded, by_five(seeded)) == visits(plain, by_five(plain))
    history = [h["status"] for h in seeded.orders[id(placed[0])]["history"]]
    assert history[history.index("waiting_parts") + 1] == "in_progress" and history[-1] == "paid"
