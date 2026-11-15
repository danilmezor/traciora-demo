"""The seed's inputs, read from `v1/` beside this package: ledger rows by configuration, the seed files and the story files."""
import json
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent / "v1"


def load(name):
    """A seed file by its path under `v1/`: `cast.json`, `accounts.json`, `checks/new_facts.json`, ..."""
    return json.loads((SEED / name).read_text(encoding="utf-8"))


ROWS = {r["key"]: r for r in load("ledger.json")["rows"]}


def value(key, cfg):
    """A ledger row's value in one configuration: `value` when both share it, else the row's `en` or `ru`."""
    row = ROWS[key]
    return row["value"] if "value" in row else row[cfg]


# The numbered story files of `calls` and `conversations`, by (kind, configuration), then by number.
STORY_FILES = {(kind, cfg): {int(p.name[:2]): json.loads(p.read_text(encoding="utf-8")) for p in sorted((SEED / kind / cfg).glob("[0-9][0-9]-*.json"))}
               for kind in ("calls", "conversations") for cfg in ("en", "ru")}
