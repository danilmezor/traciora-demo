"""Both configurations' story chats read through the mapping without a database: the counts by channel and at T."""
import collections
import datetime as dt

import pytest

from seeder import inputs
from seeder.chats import rows

INBOXES = {"en": {"Chat": 16, "Telegram": 11}, "ru": {"Chat": 11, "Telegram": 8, "VK": 3, "Avito": 5}}


@pytest.mark.parametrize("cfg", ("en", "ru"))
def test_every_chat_maps(cfg):
    users = {s["slot"]: (1000 + i, s[f"username_{cfg}"]) for i, s in enumerate(inputs.load("tenant/ladder.json")["slots"])}
    who = {"account": 1, "inboxes": {"Chat": 1, "Telegram": 2, "VK": 3, "Avito": 4}, "bot": 1, "users": users, "service": "service", "resolve_days": 7}
    built = rows.build(cfg, dt.datetime(2026, 11, 13, 10, 30), who)
    chats = built["chats"]
    assert collections.Counter(c["inbox"] for c in chats) == INBOXES[cfg]
    assert sorted(c["n"] for c in chats if c["status"] != "resolved") == [3, 5, 6, 7]
    assert [c["id"] for c in chats] == list(range(rows.BASE + 1, rows.BASE + 28))
    assert all(m["content"] for m in built["messages"])  # a line that is only a file is not loaded
