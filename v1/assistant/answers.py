"""python v1/assistant/answers.py --cfg en|ru [--client-id demo]: writes assistant/answers.<cfg>.txt, the page a person
reads to see what the assistant step's texts say on a loaded build: per item, each computed slot's metric, the instant
it was read at and the value as written into the text (a table in full), then what is held back and why, and what is
not in v1 and why. Runs in the
product's Python, in the install's working directory, after the step; it writes nothing else."""
import argparse
import datetime as dt
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from seeder import assistant, manifest  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg", choices=("en", "ru"), required=True)
    parser.add_argument("--client-id", default="demo")
    args = parser.parse_args()
    found = manifest.read(manifest.shop_dsn(args.client_id))
    os.environ["SEED_AT"] = found["asked"]
    with assistant.mapping(args.cfg, args.client_id) as (_, c):
        built = assistant.records(c)
    lines, item = [f"# Assistant texts ({args.cfg}) at T {found['T']}: each loaded item's computed slots, the instant each was read at (UTC)"
                   " and the value written into the text.", ""], None
    for r in built["resolved"]:
        if r["item"] != item:
            item = r["item"]
            lines += ["", f"## {item}"]
        shown = "\n" + r["text"] if r["metric"].startswith("#") else r["text"]
        lines.append(f"{r['slot']} | {r['metric']} | {r['at'].astimezone(dt.timezone.utc):%Y-%m-%d %H:%M} | {shown}")
    out = [h for h in built["held"] if h["kind"] in ("slice", "not in v1")]
    lines += ["", "## Held back"] + [f"{h['item']}: {h['kind']} {h['why']} (loaded: {h['loaded']})" for h in built["held"] if h not in out]
    lines += ["", "## Not in v1"] + [f"{h['item']}: {'reads what v1 does not load: ' if h['kind'] == 'slice' else ''}{h['why']} (loaded: {h['loaded']})"
                                     for h in out]
    path = Path(__file__).with_name(f"answers.{args.cfg}.txt")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"ASSISTANT ANSWERS {args.cfg} items={len({r['item'] for r in built['resolved']})} slots={len(built['resolved'])} held={len(built['held'])} -> {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
