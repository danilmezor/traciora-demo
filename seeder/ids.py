"""Ids of seeded rows as a pure function of (seed version, configuration, kind, key): the same input gives the same id
on every machine, so a step points at another store's row without its code and a repeat build is identical. A person
is `uuid("person", slot, cfg)`."""
import hashlib
import uuid as uuids

from seeder import inputs


def name(kind, key, cfg):
    return f"seed:{inputs.SEED.name}/{cfg}/{kind}/{key}"


def uuid(kind, key, cfg):
    return uuids.uuid5(uuids.NAMESPACE_URL, name(kind, key, cfg))


def number(kind, key, cfg, bits=31):
    """A positive integer below 2**bits (31: an `integer` column, 63: a `bigint`)."""
    digest = hashlib.sha256(name(kind, key, cfg).encode()).digest()
    return int.from_bytes(digest[:8], "big") % (2 ** bits - 1) + 1
