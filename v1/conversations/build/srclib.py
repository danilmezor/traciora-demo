# -*- coding: utf-8 -*-
"""Shorthand shared by src_en_*.py and src_ru_*.py: the channel identities that cannot be real accounts."""
from convlib import *  # noqa: F401,F403

WEST_CLOCK = {"en": "west (Central; one hour behind the business zone)", "ru": "west (Казань, UTC+3; на час меньше, чем в зоне компании)"}
VISITOR = {"en": "Website visitor", "ru": "Посетитель сайта"}


def web(f, key, site, visitor, visit, **kw):
    """A website chat: one browser (visitor) is one contact for 30 days, each visit a conversation."""
    tail = (0xE0 if f.cfg == "en" else 0xA0) * 256 + visit
    return f.conv(key, "chat", site, "5eedc0de-%04d-4e00-8000-%012x" % (visit, tail), "seedv1-browser-%s-%04d" % (f.cfg, visitor), VISITOR[f.cfg],
                  clock=WEST_CLOCK[f.cfg] if site == "west" else site, **kw)


def tg(f, key, site, k, name, avatar=None, **kw):
    """Telegram: peer ids above 2^52 name nobody (ledger conv.fictional_ids)."""
    peer = str(4503599627370497 + k)
    return f.conv(key, "telegram", site, peer, peer, name, avatar=avatar, clock=WEST_CLOCK[f.cfg] if site == "west" else site, **kw)


def vk(f, key, site, k, name, avatar=None, **kw):
    peer = str(1990000000 + k)
    return f.conv(key, "vk", site, peer, peer, name, avatar=avatar, clock=WEST_CLOCK[f.cfg] if site == "west" else site, **kw)


def avito(f, key, site, k, name, item, title, avatar=None, **kw):
    peer = "9000000000%05d" % k
    listing = {"listing_context": {"item_id": "9000000000%05d" % item, "title": title, "url": "https://avito.example/9000000000%05d" % item}}
    return f.conv(key, "avito", site, "u2i-seedv1-%04d-0001" % k, peer, name, avatar=avatar, extra=listing,
                  clock=WEST_CLOCK[f.cfg] if site == "west" else site, **kw)


def pic(kind, shows, matches=None):
    row = {"has": True, "kind": kind, "shows": shows, "person_in_it": False}
    if matches:
        row["matches_vehicle"] = matches
    return row


NO_PIC = {"has": False}
