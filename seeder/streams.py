"""Keyed randomness: the rule that lets the dataset end at ``now()`` and stay stable.

**The rule.** No stage ever draws from a stream that advances as generation walks
forward. Every draw comes from a stream keyed by what it is about, so the same key
gives the same numbers on any machine, in any order, at any horizon:

- ``day_stream(seed, site, day, purpose)`` — everything that happens at one site on
  one day, per purpose (``"jobs"``, ``"calls"``, ...). Extending the horizon by a
  week reproduces every earlier day byte for byte and adds seven new days.
- ``entity_stream(seed, kind, ordinal)`` — everything about one long-lived entity
  (a customer, a technician, a vehicle) by its ordinal in its own kind, so a
  customer's name, phone and vehicles do not move when the horizon grows.

The key is hashed with blake2b and the digest seeds ``random.Random``; the hash makes
neighbouring keys independent, which a bare tuple seed does not.

Two consequences the stages must respect:

1. **A count drawn for a period is drawn for the whole period, then filtered by T.**
   A year's hires are drawn from that year's stream and the ones dated after T are
   left out; they are not re-drawn when T moves.
2. **An entity's ordinal is arithmetic, never a running counter.** Ordinals are
   built out of the entity's own coordinates (the month it first appears and its
   place in that month), so a row that was not emitted yet leaves a gap rather than
   shifting the rows after it.
"""

from __future__ import annotations

import hashlib
import random
from datetime import date
from typing import Any, Iterable, Mapping, Sequence, TypeVar

K = TypeVar("K")

_SEPARATOR = b"\x1f"


def _digest(seed: int, key: Iterable[Any]) -> bytes:
    h = hashlib.blake2b(digest_size=32)
    h.update(str(int(seed)).encode("utf-8"))
    for part in key:
        h.update(_SEPARATOR)
        h.update((part.isoformat() if isinstance(part, date) else str(part)).encode("utf-8"))
    return h.digest()


def stream(seed: int, *key: Any) -> random.Random:
    """A random stream for one key. Prefer the two named shapes below; this is what
    they are made of, and what a stage uses for a key of its own (a planted problem's
    subset, a catalogue edit)."""
    return random.Random(int.from_bytes(_digest(seed, key), "big"))


def day_stream(seed: int, site: Any, day: date, purpose: str) -> random.Random:
    """What happens at one site on one day, for one purpose."""
    return stream(seed, "day", site, day, purpose)


def entity_stream(seed: int, kind: str, ordinal: int) -> random.Random:
    """The **shape** of one long-lived entity of a kind, by its ordinal: how many cars it
    has, whether its phone is missing, which planted rate it falls under. Only draws
    whose meaning is a number belong here."""
    return stream(seed, "entity", kind, ordinal)


def words_stream(seed: int, kind: str, ordinal: int) -> random.Random:
    """The **words** of the same entity: the name, the model, the colour, the number.

    Shape and words never share a stream. A locale pack with a longer list of surnames
    consumes a different amount of randomness for one name (``random.randrange`` samples
    by rejection), so a shared stream would let the pack move a structural draw and the
    two configurations would stop being one dataset in two languages. Split, the shape
    is identical whatever the pack holds and only the words differ."""
    return stream(seed, "words", kind, ordinal)


# --------------------------------------------------------------------------- draws


def from_quantiles(rng: random.Random, quantiles: Mapping[str, float | None], *, u: float | None = None) -> float:
    """A draw from a p10/p25/p50/p75/p90 histogram, which is the only shape the
    measured baseline records. The value is read
    off the piecewise-linear inverse CDF, with the tails extended by the width of the
    outermost band so the extremes are not clipped to p10 and p90.

    ``u`` supplies the position in the distribution instead of drawing one, which is how
    a draw is made to depend on something (``within_band``)."""
    points = [(float(q[1:]) / 100.0, float(quantiles[q])) for q in ("p10", "p25", "p50", "p75", "p90") if quantiles.get(q) is not None]
    if not points:
        raise ValueError("no quantiles to draw from")
    if len(points) == 1:
        return points[0][1]
    lo_p, lo_v = points[0]
    hi_p, hi_v = points[-1]
    points = [(0.0, lo_v - (points[1][1] - lo_v))] + points + [(1.0, hi_v + (hi_v - points[-2][1]))]
    u = rng.random() if u is None else min(1.0, max(0.0, float(u)))
    for (p0, v0), (p1, v1) in zip(points, points[1:]):
        if u <= p1:
            span = p1 - p0
            return v0 if span == 0 else v0 + (v1 - v0) * (u - p0) / span
    return points[-1][1]


def bands(weights: Mapping[K, float]) -> dict[K, tuple[float, float]]:
    """The unit interval cut into one band per class, in the order given, each as wide as
    that class's share of the population. The bands tile [0, 1] exactly."""
    total = sum(float(weight) for weight in weights.values()) or 1.0
    out: dict[K, tuple[float, float]] = {}
    cursor = 0.0
    for key, weight in weights.items():
        width = float(weight) / total
        out[key] = (cursor, width)
        cursor += width
    return out


def within_band(rng: random.Random, band: tuple[float, float], explains: float) -> float:
    """A position in a distribution that a class explains part of.

    With probability ``explains`` the draw lands inside the class's own band; otherwise it
    is uniform over the whole range. Because the bands tile [0, 1] and each is as wide as
    its class's share of the population, the mixture over the whole population is *exactly*
    uniform again: the measured distribution is untouched, and the class explains
    ``explains`` of the variance in it rather than all or none of it. That is what lets a
    premium car cost more than a cheap one without the chain's measured ticket moving a
    cent.
    """
    lower, width = band
    if rng.random() < float(explains):
        return lower + rng.random() * width
    return rng.random()


def happens(rng: random.Random, share: float) -> bool:
    """True with the measured share's probability. A share is a rate from the
    baseline, so the generated rate holds within sampling error, which is what the
    invariant tests assert with a tolerance."""
    return rng.random() < float(share)


def pick(rng: random.Random, values: Sequence[K]) -> K:
    return values[rng.randrange(len(values))]
