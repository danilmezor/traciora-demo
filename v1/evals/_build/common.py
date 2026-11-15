# Shared by build.py, render.py and checks/check_evals.py: the ledger lookup, the number tokens and the
# number formats of each configuration. Nothing here writes a file.
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
EVALS = os.path.dirname(HERE)
ROOT = os.path.dirname(EVALS)
NB = " "
CONFIGS = ("en", "ru")
KINDS = ("value", "list", "explanation", "action", "nothing", "cannot tell", "refusal", "smoke", "stale")
AREAS = ("story", "knowledge_base", "calls", "conversations", "working_day", "assistant")
SOURCES = ("erp", "core", "conversations", "knowledge_base", "memory", "account_store")


def load(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return json.load(f)


def read(*path):
    with open(os.path.join(ROOT, *path), encoding="utf-8") as f:
        return f.read()


class Ledger:
    """ledger.json plus the rows another design part proposed and the ledger has not merged yet."""

    def __init__(self):
        self.rows = {r["key"]: r for r in load("ledger.json")["rows"]}
        # an outcome row's answer is what the build measured (manifest.<cfg>.json), not the ledger's design target
        self.measured = {cfg: {k: float(b["value"]) if "." in b["value"] else int(b["value"])
                               for k, b in load("manifest.%s.json" % cfg)["bands"].items() if b["eval_answer"]}
                         for cfg in ("en", "ru")}
        self.proposed = {}
        path = os.path.join(ROOT, "assistant", "ledger_rows.json")
        if os.path.exists(path):
            for r in load("assistant", "ledger_rows.json")["rows"]:
                if r["key"] not in self.rows:
                    self.proposed[r["key"]] = r

    def where(self, key):
        return "ledger.json" if key in self.rows else "assistant/ledger_rows.json" if key in self.proposed else None

    def row(self, key):
        return self.rows.get(key) or self.proposed.get(key)

    def value(self, key, cfg):
        r = self.row(key)
        if r is None:
            raise KeyError(key)
        if r.get("outcome") and key in self.measured[cfg]:
            return self.measured[cfg][key]
        if "value" in r:
            v = r["value"]
            # a few proposed rows keep both configurations inside one value
            if isinstance(v, dict) and set(v) == {"en", "ru"}:
                return v[cfg]
            return v
        return r.get(cfg)

    def split(self, ref):
        """'acct.A6.visits[0]' -> ('acct.A6.visits', '[0]'): the longest prefix that is a key."""
        parts = re.split(r"(?=[.\[])", ref)
        for n in range(len(parts), 0, -1):
            key = "".join(parts[:n])
            if self.row(key) is not None:
                return key, "".join(parts[n:])
        raise KeyError(ref)

    def get(self, ref, cfg):
        key, path = self.split(ref)
        v = self.value(key, cfg)
        for name, index in re.findall(r"\.([^.\[]+)|\[(-?\d+)\]", path):
            v = v[name] if name else v[int(index)]
        if v is None:
            raise KeyError("%s has no value for %s" % (ref, cfg))
        return key, path, v


def group(n, cfg):
    s = "%d" % abs(n)
    out = ""
    while len(s) > 3:
        out = ("," if cfg == "en" else NB) + s[-3:] + out
        s = s[:-3]
    return ("-" if n < 0 else "") + s + out


def plain(v, cfg, places=None):
    """A number as the configuration writes it: 3,203 and 2.5 in English, 3 203 and 2,5 in Russian."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise TypeError("not a number: %r" % (v,))
    if places is None:
        if float(v) == int(v):
            return group(int(v), cfg)
        s = ("%.4f" % v).rstrip("0")
        whole, frac = s.split(".")
    else:
        s = "%.*f" % (places, v)
        whole, frac = (s.split(".") + [""])[:2]
    whole = group(int(whole), cfg)
    if not frac:
        return whole
    return whole + ("." if cfg == "en" else ",") + frac


def fmt(v, f, cfg):
    if f == "text":
        return str(v)
    if f in ("int", "num", "x"):
        return plain(v, cfg)
    if f == "r0":
        return plain(int(math.floor(v + 0.5)), cfg)
    if f == "r1":
        return plain(v, cfg, 1)
    if f in ("pct", "pct0", "pct1"):
        n = plain(v, cfg) if f == "pct" else plain(int(math.floor(v + 0.5)), cfg) if f == "pct0" else plain(v, cfg, 1)
        return n + NB + "%"
    if f in ("money", "money2"):
        whole = float(v) == int(v) and f == "money"
        n = plain(v, cfg) if whole else plain(v, cfg, 2)
        return "$" + n if cfg == "en" else n + NB + "₽"
    if f == "dur":
        h, m = divmod(int(v), 60)
        hh, mm = ("h", "min") if cfg == "en" else ("ч", "мин")
        if h and m:
            return "%d%s%s %d%s%s" % (h, NB, hh, m, NB, mm)
        return "%d%s%s" % (h, NB, hh) if h else "%d%s%s" % (m, NB, mm)
    raise ValueError("unknown format %r" % f)


TOKEN = re.compile(r"\[\[(=?)(.+?)\|([a-z0-9]+)\]\]")
SAFE = {"round": round, "sum": sum, "min": min, "max": max, "abs": abs, "len": len, "int": int,
        "ceil": math.ceil, "floor": math.floor}


def evaluate(formula, ledger, cfg, used=None):
    def L(ref):
        key, _, v = ledger.get(ref, cfg)
        if used is not None:
            used.append(key)
        return v
    return eval(formula, dict(SAFE, L=L, __builtins__={}))  # noqa: S307 - formulas are this folder's own


def fill(text, ledger, cfg, numbers, keys):
    """Replaces every [[key.path|format]] and [[=formula|format]] by its value for the configuration and
    records where each number came from."""
    def one(m):
        formula, ref, f = m.group(1), m.group(2).strip(), m.group(3)
        if formula:
            used = []
            v = evaluate(ref, ledger, cfg, used)
            shown = fmt(v, f, cfg)
            for k in used:
                if k not in keys:
                    keys.append(k)
            numbers.append({"shown": shown, "from": "derived", "formula": ref, "format": f})
        else:
            key, path, v = ledger.get(ref, cfg)
            shown = fmt(v, f, cfg)
            if key not in keys:
                keys.append(key)
            numbers.append({"shown": shown, "from": "ledger", "key": key, "path": path, "format": f,
                            "file": ledger.where(key)})
        return shown
    return TOKEN.sub(one, text)


# ----------------------------------------------------------------------------- reading numbers out of a text
SLOT = re.compile(r"\{[a-z0-9_]+\}")
CODE = re.compile(r"`[^`]*`")
CLOCK = re.compile(r"(?<![\d.,])(\d{1,2}):(\d{2})(?![\d:])")
NUM_EN = re.compile(r"(?<![\w.,])\d{1,3}(?:,\d{3})+(?:\.\d+)?|(?<![\w.,])\d+(?:\.\d+)?")
NUM_RU = re.compile(r"(?<![\w.,])\d{1,3}(?:[  ]\d{3})+(?:,\d+)?(?![\d])|(?<![\w.,])\d+(?:,\d+)?")


def numerals(text, cfg):
    """Every number written in a text, as (kind, canonical) pairs: ('clock', '07:30') or ('n', 11400.0).
    Computed slots {name} and `code` spans hold no number of the answer."""
    text = CODE.sub(" ", SLOT.sub(" ", text))
    out = []
    for m in CLOCK.finditer(text):
        out.append(("clock", "%02d:%s" % (int(m.group(1)), m.group(2))))
    text = CLOCK.sub(" ", text)
    for m in (NUM_EN if cfg == "en" else NUM_RU).finditer(text):
        s = m.group(0)
        s = s.replace(",", "") if cfg == "en" else s.replace(" ", "").replace(NB, "").replace(",", ".")
        out.append(("n", float(s)))
    return out


def numbers_in(obj):
    """Every number a JSON value or a source text holds, for looking a written number up: numbers of any
    notation, and clock times."""
    nums, clocks = set(), set()

    def text(s):
        for m in CLOCK.finditer(s):
            clocks.add("%02d:%s" % (int(m.group(1)), m.group(2)))
        for raw in re.findall(r"\d+(?:[  ,]\d{3})*(?:[.,]\d+)?", s):
            for variant in (raw.replace(",", "").replace(" ", "").replace(NB, ""),
                            raw.replace(" ", "").replace(NB, "").replace(",", "."),
                            re.sub(r"[  ,]\d{3}.*$", "", raw)):
                try:
                    nums.add(float(variant))
                except ValueError:
                    pass
        for raw in re.findall(r"\d+", s):
            nums.add(float(raw))

    def walk(v):
        if isinstance(v, bool) or v is None:
            return
        if isinstance(v, (int, float)):
            nums.add(float(v))
        elif isinstance(v, str):
            text(v)
        elif isinstance(v, dict):
            for k, x in v.items():
                text(str(k))
                walk(x)
        elif isinstance(v, (list, tuple)):
            for x in v:
                walk(x)

    walk(obj)
    return nums, clocks


def matches(n, pool):
    """A written number equals a source number, exactly or as its rounding to the written precision."""
    if n in pool:
        return True
    for places in (0, 1, 2):
        if abs(n * 10 ** places - round(n * 10 ** places)) < 1e-9:
            return any(abs(math.floor(p * 10 ** places + 0.5) / 10 ** places - n) < 1e-9 for p in pool)
    return False
