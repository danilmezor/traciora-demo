#!/usr/bin/env python3
"""Check the managers' side of the assistant in seed v1: Ask threads, memory, scheduled tasks, briefs.

    <product repo>/.venv/bin/python checks/check_assistant.py en
    <product repo>/.venv/bin/python checks/check_assistant.py ru

With the product on the path (TRACIORA_PRODUCT, default ../traciora beside this checkout) the note gate
and the schedule builder are the product's own; without it the same rules are applied as read on
2026-11-13 and the report says so. Exit 0 when nothing fails.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent
A = SEED / "assistant"
REPO = Path(os.environ.get("TRACIORA_PRODUCT") or SEED.parent.parent / "traciora")
DECIDERS = {"1", "2", "4", "22"}          # seniors and the administrator: who a proposal is shown to
RANKS = ("worker", "junior", "middle", "senior", "admin")

fails: list[str] = []
notes_out: list[str] = []


def fail(msg: str) -> None:
    fails.append(msg)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- the product's rules

def product():
    """(reject_candidate, Candidate, build, parts) from the product, or None."""
    src = REPO / "apps/backend/src"
    if not src.exists():
        return None
    sys.path.insert(0, str(src))
    try:
        from traciora.core.memory import gates
        from traciora.core.memory.store import Candidate
        from traciora.core.scheduling import schedule_words
        return gates.reject_candidate, Candidate, schedule_words.build, schedule_words.parts
    except Exception as exc:  # noqa: BLE001 the fallback says which rules were used
        notes_out.append(f"product import failed ({type(exc).__name__}: {exc}); rules applied as read")
        return None


_TOKEN = re.compile(r"\b[a-z][a-z0-9_]*_ref:[a-z0-9_]+\b", re.I)
_SHAPES = (
    re.compile(r"(?<![A-Za-z0-9])[ABEKMHOPCTYX]\s?\d{3}\s?[ABEKMHOPCTYX]{2}\s?\d{2,3}(?![A-Za-z0-9])", re.I),
    re.compile(r"(?<![\w+:.,])\+?\(?\d(?:[ ()-]{0,2}\d){9,}(?![\w:])"),
    re.compile(r"(?<![A-Za-z0-9])[A-Z]{2}\d{2} ?[A-Z]{3}(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9-])[A-Za-z]{2,3}-\d{3,4}(?![A-Za-z0-9-])"),
)


def gate_by_rule(memory_class, subject, text, why, how, team):
    """gates.reject_candidate without the PII detector (core/memory/gates.py:31-50)."""
    if memory_class not in (("practice",) if team else ("preference", "correction")):
        return "class"
    fields = (subject, text, why, how)
    if any(not value.strip() for value in fields):
        return "empty"
    if len(text.split()) > 40 or len(subject.split()) > 6 or len(why.split()) > 60 or len(how.split()) > 60:
        return "too_long"
    if any(_TOKEN.search(value) for value in fields):
        return "token"
    if any(shape.search(value) for value in fields for shape in _SHAPES):
        return "pii"
    return None


# --------------------------------------------------------------------------- slots

WHEN = re.compile(
    r"^(@[a-z0-9_]+|T|W[+-]?\d+\.(mon|tue|wed|thu|fri|sat|sun)|P[1-6]|slot\d+:[+-]\d+)"
    r"([+-]\d+(wd:(main|east|west|slot\d+)|d|w|mo|y))*$")
SLOT = re.compile(r"\{\{(.+?)\}\}")
PARAM = re.compile(r"(?<!\{)\{([a-z_]+)\}(?!\})")


class Registry:
    def __init__(self, lang: str):
        reg = load(A / "metrics.json")
        self.metrics = set(reg["metrics"])
        self.dims = set(reg["dimensions"])
        self.periods = set()
        for key in reg["periods"]:
            self.periods.update(part.strip() for part in key.split(","))
        self.value_formats = set()
        for key in reg["value_formats"]:
            self.value_formats.update(part.strip().split(":")[0] for part in key.split(","))
        self.date_formats = set(reg["date_formats"][lang])
        self.events = set(reg["when"]["events"])
        self.forms = 2 if lang == "en" else 3
        ledger = {row["key"]: row for row in load(SEED / "ledger.json")["rows"]}
        ledger.update({row["key"]: row for row in load(A / "ledger_rows.json")["rows"]})
        self.ledger = ledger
        self.lang = lang

    def when(self, text: str, where: str) -> None:
        if not WHEN.match(text):
            fail(f"{where}: date '{text}' is not in the date grammar")
            return
        base = re.match(r"@[a-z0-9_]+", text)
        if base and base.group(0) not in self.events:
            fail(f"{where}: event '{base.group(0)}' is not defined in metrics.json")

    def period(self, text: str, where: str) -> None:
        if text in self.periods or re.fullmatch(r"d(7|30|90)", text):
            return
        if ".." in text:
            for part in text.split(".."):
                self.when(part, where)
            return
        fail(f"{where}: period '{text}' is not defined")

    def population(self, text: str, where: str) -> None:
        if text in ("", "all"):
            return
        for pair in text.split("&"):
            name, _, value = pair.partition("=")
            if name not in self.dims or not value:
                fail(f"{where}: population '{pair}' names no dimension of metrics.json")

    def value_format(self, text: str, where: str) -> None:
        name, _, forms = text.partition(":")
        if name not in self.value_formats and name not in self.date_formats:
            fail(f"{where}: format '{text}' is not defined")
        if name == "n" and len(forms.split("/")) != self.forms:
            fail(f"{where}: '{text}' needs {self.forms} noun forms in {self.lang}")

    def value(self, body: str, where: str, *, column: bool = False) -> None:
        parts = body.split("|")
        if column:
            if len(parts) != 3:
                fail(f"{where}: a block column is =metric|population|format, got '={body}'")
                return
            metric, population, fmt = parts
        else:
            if len(parts) != 4:
                fail(f"{where}: a value slot is =metric|population|period|format, got '={body}'")
                return
            metric, population, period, fmt = parts
            self.period(period, where)
        if metric not in self.metrics:
            fail(f"{where}: metric '{metric}' is not defined in metrics.json")
        self.population(population, where)
        self.value_format(fmt, where)

    def ledger_slot(self, body: str, where: str) -> None:
        path, _, fmt = body.partition("|")
        keys = path.split(".")
        found = None
        for cut in range(len(keys), 0, -1):
            if ".".join(keys[:cut]) in self.ledger:
                found, rest = self.ledger[".".join(keys[:cut])], keys[cut:]
                break
        if found is None:
            fail(f"{where}: ledger key '{path}' is in neither ledger.json nor assistant/ledger_rows.json")
            return
        value = found.get(self.lang, found.get("value"))
        for key in rest:
            if not isinstance(value, dict) or key not in value:
                fail(f"{where}: ledger path '{path}' does not resolve")
                return
            value = value[key]
        self.value_format(fmt, where)

    def text(self, text: str, where: str, blocks: dict, params: set | None) -> None:
        for body in SLOT.findall(text):
            if body.startswith("="):
                self.value(body[1:], where)
            elif body.startswith("$"):
                self.ledger_slot(body[1:], where)
            elif body.startswith("#"):
                if body[1:] not in blocks:
                    fail(f"{where}: block '{body}' is not defined beside the text")
            else:
                parts = body.split("|")
                if len(parts) != 2:
                    fail(f"{where}: a date slot is when|format, got '{body}'")
                    continue
                self.when(parts[0], where)
                if parts[1] not in self.date_formats:
                    fail(f"{where}: date format '{parts[1]}' is not defined for {self.lang}")
        if params is not None:
            bare = SLOT.sub(lambda m: PARAM.sub("x", m.group(0)), text)
            for name in PARAM.findall(SLOT.sub("", bare)):
                if name not in params:
                    fail(f"{where}: parameter '{{{name}}}' is not declared")

    def block(self, spec: dict, where: str) -> None:
        self.period(spec.get("period", "at"), where)
        self.population(re.sub(r"\{[a-z_]+\}", "x", spec.get("where", "all")), where)
        for column in spec.get("columns", []):
            if len(column) != 2:
                fail(f"{where}: a column is [header, value]")
            elif column[1].startswith("="):
                self.value(column[1][1:], where, column=True)

    def walk(self, node, where: str, blocks: dict | None = None, params: set | None = None) -> None:
        """Every string under ``node``, with the blocks defined at or above it."""
        blocks = dict(blocks or {})
        if isinstance(node, dict):
            for name, spec in (node.get("blocks") or {}).items():
                blocks[name] = spec
                self.block(spec, f"{where}.blocks.{name}")
            for key, value in node.items():
                if key in ("blocks", "expect", "purpose", "about", "params", "fixed_by", "when", "unit", "reasoning"):
                    continue
                self.walk(value, f"{where}.{key}", blocks, params)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                self.walk(value, f"{where}[{index}]", blocks, params)
        elif isinstance(node, str):
            self.text(re.sub(r"=\{[a-z_]+\}", "=x", node) if params is not None else node, where, blocks, params)


# --------------------------------------------------------------------------- the checks

def words_of_point(point: str) -> int:
    """Words of a brief point once rendered: a counted slot is two words, a date at most three."""
    def render(match):
        body = match.group(1)
        if body.startswith("="):
            fmt = body.split("|")[-1]
            return "9 x" if fmt.startswith("n:") else "x"
        if body.startswith("$"):
            return "x"
        return "x x x" if body.split("|")[-1] in ("day", "on_day", "until_day", "date", "date_gen") else "x"
    return sum(1 for word in SLOT.sub(render, point.lstrip("- ")).split() if re.search(r"\w", word))


def main(lang: str) -> int:
    if lang not in ("en", "ru"):
        print("usage: check_assistant.py en|ru")
        return 2
    reg = Registry(lang)
    cast = {person["slot"]: person for person in load(SEED / "cast.json")["people"]}
    rows = {row["key"]: row for row in load(A / "ledger_rows.json")["rows"]}
    threads = load(A / lang / "threads.json")["threads"]
    notes = load(A / lang / "notes.json")["notes"]
    team = load(A / lang / "team.json")
    tasks_file = load(A / lang / "tasks.json")
    bank = load(A / lang / "patterns.json")
    prod = product()
    notes_out.append("note gate and schedule builder: " + ("the product's own, imported" if prod else "applied by rule"))

    def name_ok(owner: dict, where: str) -> None:
        person = cast.get(owner.get("slot"))
        if person is None:
            fail(f"{where}: no cast slot {owner.get('slot')}")
        elif person[lang]["full_name"] != owner.get("name"):
            fail(f"{where}: name '{owner.get('name')}' is not cast.json's '{person[lang]['full_name']}'")

    def gate(memory_class, subject, text, why, how, team_note, where):
        if prod:
            reason = prod[0](prod[1](memory_class, subject, text, why, how), team=team_note)
        else:
            reason = gate_by_rule(memory_class, subject, text, why, how, team_note)
        if reason:
            fail(f"{where}: the note gate refuses it ({reason})")
        if len(subject.split()) > 6 or len(text.split()) > 40:
            fail(f"{where}: over the limit of 6 words of subject or 40 of text")

    # ---- threads
    by_thread = {}
    for thread in threads:
        where = f"thread {thread['id']}"
        by_thread[thread["id"]] = thread
        name_ok(thread["owner"], where)
        reg.when(thread["when"], where)
        if not re.fullmatch(r"\d\d:\d\d", thread["at"]):
            fail(f"{where}: 'at' is not HH:MM")
        if not thread["title"] or len(thread["title"]) > 60:
            fail(f"{where}: a title of 1 to 60 characters")
        if [turn["n"] for turn in thread["turns"]] != list(range(1, len(thread["turns"]) + 1)):
            fail(f"{where}: turns are not numbered from 1")
        if not 1 <= len(thread["turns"]) <= 6:
            fail(f"{where}: 2 to 12 messages")
        for turn in thread["turns"]:
            if not turn["user"].strip() or not turn["assistant"].strip():
                fail(f"{where} turn {turn['n']}: empty message")
            if turn.get("feedback") not in (None, "up", "down"):
                fail(f"{where} turn {turn['n']}: feedback is up or down")
            card = turn.get("card")
            if card and card["tool"] not in turn["tools"]:
                fail(f"{where} turn {turn['n']}: the card's tool is not among the turn's tools")
        for slot, written in thread.get("people", {}).items():
            person = cast.get(slot)
            if person is None:
                fail(f"{where}: people names slot {slot}, not in cast.json")
                continue
            known = (person[lang]["full_name"] + " " + person[lang]["colleagues_call"]).casefold()
            stems = [word[:4].casefold() for word in re.findall(r"\w+", written) if len(word) > 2]
            if not any(stem in known for stem in stems):
                fail(f"{where}: '{written}' does not match slot {slot} in cast.json")
            said = " ".join(turn["user"] + " " + turn["assistant"] for turn in thread["turns"])
            if written not in said:
                fail(f"{where}: '{written}' is listed in people and not written in the thread")
        for fact in thread.get("kb_facts", []):
            page = SEED / "kb" / lang / fact["page"]
            body = page.read_text(encoding="utf-8") if page.exists() else ""
            for needle in fact["contains"]:
                if needle not in body:
                    fail(f"{where}: kb page {fact['page']} does not say '{needle}'")
        reg.walk(thread, where)
    if len(threads) != rows["ask.handwritten"]["value"]:
        fail(f"hand-written threads: {len(threads)}, ledger row ask.handwritten says {rows['ask.handwritten']['value']}")

    # ---- patterns
    kinds = Counter(pattern["kind"] for pattern in bank["patterns"])
    if dict(kinds) != rows["ask.patterns"]["value"]:
        fail(f"pattern counts {dict(kinds)} differ from ledger row ask.patterns")
    declared = set(bank["params"]) | {f"{name}_name" for name in bank["params"]} | {
        "site_at", "site_gen", "other_site_at", "other_site_name", "note_text", "note_subject"}
    seen_ids = set()
    for pattern in bank["patterns"]:
        where = f"pattern {pattern['id']}"
        if pattern["id"] in seen_ids:
            fail(f"{where}: id used twice")
        seen_ids.add(pattern["id"])
        if pattern["ranks"] not in RANKS:
            fail(f"{where}: ranks is one of {RANKS}")
        if len(pattern["ask"]) < 2 or len(set(pattern["ask"])) != len(pattern["ask"]):
            fail(f"{where}: at least two different wordings of the question")
        for fact in pattern.get("kb_facts", []):
            page = SEED / "kb" / lang / fact["page"]
            body = page.read_text(encoding="utf-8") if page.exists() else ""
            for needle in fact["contains"]:
                if needle not in body:
                    fail(f"{where}: kb page {fact['page']} does not say '{needle}'")
        if "valid_from" in pattern:
            reg.when(pattern["valid_from"], where)
        reg.walk({k: v for k, v in pattern.items() if k != "valid_from"}, where, params=declared)
    for key in ("note_ack", "note_replace_ack", "propose_ack"):
        reg.walk(bank[key], f"patterns.{key}", params=declared)
    if sum(rows["ask.threads_per_person"]["value"].values()) != rows["ask.threads"]["value"]:
        fail("ask.threads_per_person does not sum to ask.threads")
    for slot in rows["ask.threads_per_person"]["value"]:
        if cast[slot]["rank"] == "worker" or cast[slot]["status"] != "active":
            fail(f"ask.threads_per_person: slot {slot} is not an active manager")
    per_owner = Counter(thread["owner"]["slot"] for thread in threads)
    for slot, count in per_owner.items():
        if count > rows["ask.threads_per_person"]["value"].get(slot, 0):
            fail(f"slot {slot} has more hand-written threads than threads")

    # ---- personal notes
    by_note = {note["id"]: note for note in notes}
    live = [note for note in notes if note["state"] in ("active", "unverified", "dormant")]
    slots_seen = set()
    for note in notes:
        where = f"note {note['id']}"
        name_ok(note["owner"], where)
        if note["id"].split(".")[0] != note["owner"]["slot"]:
            fail(f"{where}: id does not start with the owner's slot")
        gate(note["class"], note["subject"], note["text"], note["why"], note["how"], False, where)
        reg.when(note["when"], where)
        if note["state"] not in ("active", "dormant", "archived"):
            fail(f"{where}: a personal note is active, dormant or archived (never unverified)")
        source = note["source"]
        if "thread" in source:
            thread = by_thread.get(source["thread"])
            turn = next((t for t in (thread or {}).get("turns", []) if t["n"] == source["turn"]), None)
            if thread is None or turn is None:
                fail(f"{where}: source thread {source['thread']} turn {source.get('turn')} does not exist")
            else:
                if thread["owner"]["slot"] != note["owner"]["slot"]:
                    fail(f"{where}: its source thread belongs to somebody else")
                if (turn.get("card") or {}).get("note") != note["id"]:
                    fail(f"{where}: turn {source['turn']} of {source['thread']} does not save this note")
                if note["text"] not in turn["assistant"]:
                    fail(f"{where}: the turn's answer does not say the note in its own words")
                if thread["when"] != note["when"]:
                    fail(f"{where}: 'when' differs from its source thread's")
        elif "auto" in source:
            if source["auto"] not in kinds:
                fail(f"{where}: source kind '{source['auto']}' has no pattern in the bank")
            if not source.get("said", "").strip():
                fail(f"{where}: an auto source needs the manager's own words")
        elif "same_as" in source:
            if source["same_as"] not in by_note or note.get("replaces") != source["same_as"]:
                fail(f"{where}: same_as must name the note it replaces")
        else:
            fail(f"{where}: no source")
        if note["state"] == "dormant" and "last_used" not in note:
            fail(f"{where}: a dormant note says when it was last used")
        if note["state"] == "archived":
            ended = note.get("ended") or {}
            if ended.get("by") not in ("owner_in_chat", "owner_on_page", "nightly_tighten", "owner_deleted"):
                fail(f"{where}: an archived note says how it ended")
            reg.when(ended.get("when", ""), where)
            after = ended.get("superseded_by")
            if (after is None) != (ended.get("by") == "owner_deleted"):
                fail(f"{where}: only a deleted note has no successor")
            if after:
                new = by_note.get(after)
                if new is None or new.get("replaces") != note["id"] or (
                        new["owner"]["slot"], new["class"], new["subject"]) != (
                        note["owner"]["slot"], note["class"], note["subject"]):
                    fail(f"{where}: its successor must keep owner, class and subject and name it")
                if ended["by"] == "nightly_tighten" and not (
                        len(note["text"].split()) > 12 and 0 < len(new["text"].split()) <= 12):
                    fail(f"{where}: the nightly pass tightens a text over 12 words to at most 12 (dream.py:130-134)")
    slot_of = defaultdict(list)
    for note in live:
        slot_of[(note["owner"]["slot"], note["class"], " ".join(note["subject"].lower().split()))].append(note["id"])
    for key, ids in slot_of.items():
        if len(ids) > 1:
            fail(f"live notes {ids} share owner, class and subject")
    counts = Counter(note["state"] for note in live)
    want = rows["mem.personal_live"]["value"]
    if (len(live), counts["active"], counts["dormant"]) != (want["all"], want["active"], want["dormant"]):
        fail(f"live personal notes {len(live)} ({dict(counts)}) differ from ledger row mem.personal_live {want}")
    ended = Counter(note["ended"]["by"] for note in notes if note["state"] == "archived")
    want = rows["mem.personal_ended"]["value"]
    if (sum(ended.values()), ended["owner_in_chat"], ended["owner_on_page"], ended["nightly_tighten"],
            ended["owner_deleted"]) != (want["all"], want["replaced_in_chat"], want["changed_on_page"],
                                        want["tightened_by_night"], want["deleted_by_owner"]):
        fail(f"ended personal notes {dict(ended)} differ from ledger row mem.personal_ended")
    per_person = Counter(note["owner"]["slot"] for note in live)
    if dict(per_person) != rows["mem.personal_per_person"]["value"]:
        fail(f"live notes per person {dict(per_person)} differ from ledger row mem.personal_per_person")

    # ---- the nightly rule: three holders of one subject, and no other subject with three
    holders = defaultdict(set)
    for note in live:
        holders[" ".join(note["subject"].lower().split())].add(note["owner"]["slot"])
    crowded = {subject: who for subject, who in holders.items() if len(who) >= 3}

    # ---- team notes and proposals
    proposals = {p["id"]: p for p in team["proposals"]}
    team_notes = {t["id"]: t for t in team["team_notes"]}
    cross = (SEED / "kb" / "CROSS-STORE.md").read_text(encoding="utf-8")
    for note in team["team_notes"]:
        where = f"team note {note['id']}"
        gate("practice", note["subject"], note["text"], note["why"], note["how"], True, where)
        if note["visible_from"] not in RANKS[1:]:
            fail(f"{where}: visible_from is a manager rank")
        if note["state"] not in ("active", "unverified"):
            fail(f"{where}: state")
        reg.when(note["approved"], where)
        proposal = proposals.get(note["proposal"])
        if proposal is None or proposal["status"] != "approved" or proposal.get("published_as") != note["id"]:
            fail(f"{where}: no approved proposal publishes it")
            continue
        if proposal["decided"] != note["approved"]:
            fail(f"{where}: approved '{note['approved']}' differs from its proposal's decision '{proposal['decided']}'")
        if "text" in proposal and (proposal["subject"], proposal["text"]) != (note["subject"], note["text"]):
            fail(f"{where}: differs from the proposal that published it")
        if proposal["subject"] != note["subject"]:
            fail(f"{where}: subject differs from its proposal's")
        proposer_rank = cast[proposal["by"]["slot"]]["rank"]
        if "lowered" in note:
            name_ok(note["lowered"]["by"], where)
            if note["lowered"]["from"] != proposer_rank or cast[note["lowered"]["by"]["slot"]]["rank"] != "senior":
                fail(f"{where}: lowered from the proposer's rank by a senior")
        elif note["visible_from"] != proposer_rank:
            fail(f"{where}: visible from '{note['visible_from']}' but proposed at rank '{proposer_rank}' and never lowered")
        review = note.get("review")
        if (note["state"] == "unverified") != (review is not None and review.get("answer") is None):
            fail(f"{where}: unverified means a check that waits")
        if review and review.get("by"):
            name_ok(review["by"], where)
    open_subjects = Counter()
    for proposal in team["proposals"]:
        where = f"proposal {proposal['id']}"
        nightly = proposal["by"] == "nightly"
        if not nightly:
            name_ok(proposal["by"], where)
        if proposal["status"] not in ("proposed", "approved", "rejected"):
            fail(f"{where}: status is proposed, approved or rejected")
        if proposal["status"] == "rejected" and not proposal.get("reason", "").strip():
            fail(f"{where}: a rejection carries a reason")
        if proposal["status"] != "proposed":
            name_ok(proposal["decided_by"], where)
            decider = proposal["decided_by"]["slot"]
            if proposal.get("withdrawn"):
                if decider != proposal["by"]["slot"]:
                    fail(f"{where}: a withdrawal is decided by its proposer")
            else:
                if decider not in DECIDERS:
                    fail(f"{where}: decided by somebody who is neither senior nor administrator")
                if not nightly and decider == proposal["by"]["slot"]:
                    fail(f"{where}: nobody decides their own proposal")
            reg.when(proposal["decided"], where)
        if proposal["status"] == "proposed":
            open_subjects[" ".join(proposal["subject"].lower().split())] += 1
        if "text" in proposal:
            gate("practice", proposal["subject"], proposal["text"], proposal["why"], proposal["how"], True, where)
        elif proposal.get("published_as") not in team_notes:
            fail(f"{where}: no text and no team note to take it from")
        if nightly:
            subject = " ".join(proposal["subject"].lower().split())
            held = [n for n in live if " ".join(n["subject"].lower().split()) == subject]
            if sorted({n["owner"]["slot"] for n in held}) != sorted(proposal["holders"]) or len(held) != 3:
                fail(f"{where}: the nightly proposal needs exactly its three holders of the subject")
            if len({(n["subject"], n["text"]) for n in held}) != 1 or held and held[0]["text"] != proposal["text"]:
                fail(f"{where}: the three holders' notes are not word for word the same")
            top = max(RANKS.index(cast[slot]["rank"]) for slot in proposal["holders"])
            if RANKS[top] != proposal["visible_from"]:
                fail(f"{where}: visible from the highest holder's rank, {RANKS[top]}")
            if set(crowded) != {subject}:
                fail(f"subjects held by three or more people: {sorted(crowded)}; the nightly pass would raise each")
        else:
            reg.when(proposal["proposed"], where)
            source = proposal.get("source") or {}
            if "thread" in source:
                thread = by_thread.get(source["thread"])
                turn = next((t for t in (thread or {}).get("turns", []) if t["n"] == source["turn"]), None)
                if turn is None or (turn.get("card") or {}).get("proposal") != proposal["id"]:
                    fail(f"{where}: source turn does not propose it")
                elif proposal["text"] not in turn["assistant"] and proposal["text"] not in " ".join(
                        t["assistant"] for t in thread["turns"]):
                    fail(f"{where}: its thread does not say the proposal in its own words")
            elif source.get("auto") not in kinds or not source.get("said", "").strip():
                fail(f"{where}: source is a thread turn or an auto kind with the proposer's words")
    for subject, count in open_subjects.items():
        if count > 1:
            fail(f"more than one open proposal on '{subject}'")
    status = Counter()
    for proposal in team["proposals"]:
        status["withdrawn" if proposal.get("withdrawn") else
               {"approved": "approved", "rejected": "declined", "proposed": "waiting"}[proposal["status"]]] += 1
    want = rows["mem.proposals"]["value"]
    got = {"all": len(team["proposals"]), **status, "designed_in_4_5": sum(1 for p in team["proposals"] if p["designed"])}
    if got != want:
        fail(f"proposals {got} differ from ledger row mem.proposals {want}")
    want = rows["mem.team_notes"]["value"]
    states = Counter(note["state"] for note in team["team_notes"])
    seen_from = Counter(note["visible_from"] for note in team["team_notes"])
    if (len(team["team_notes"]), states["active"], states["unverified"], dict(seen_from)) != (
            want["all"], want["active"], want["unverified"], want["visible_from"]):
        fail(f"team notes {len(team['team_notes'])} {dict(states)} {dict(seen_from)} differ from ledger row mem.team_notes")
    reviews = Counter("waiting_at_t" if n["review"]["answer"] is None else "kept"
                      for n in team["team_notes"] if n.get("review"))
    if dict(reviews) != rows["mem.reviews"]["value"]:
        fail(f"reviews {dict(reviews)} differ from ledger row mem.reviews")
    lines = Counter()
    for proposal in team["proposals"]:
        by = None if proposal["by"] == "nightly" else proposal["by"]["slot"]
        lines["memory.proposed"] += len(DECIDERS - {by})
        if by and proposal["status"] != "proposed" and not proposal.get("withdrawn"):
            lines["memory.decided"] += 1
    lines["memory.unverified"] = 4 * sum(reviews.values())
    if dict(lines) != rows["mem.inbox_lines"]["value"]:
        fail(f"memory Inbox lines {dict(lines)} differ from ledger row mem.inbox_lines")
    # wordings fixed elsewhere
    fixed = [team_notes["T1"]["subject"], team_notes["T1"]["text"], team_notes["T2"]["text"], team_notes["T3"]["text"],
             proposals["P07"]["text"], proposals["P10"]["text"], proposals["P11"]["subject"], proposals["P11"]["text"]]
    reason = proposals["P07"]["reason"]
    for wording in fixed:
        if wording.rstrip(".") not in cross:
            fail(f"'{wording}' is not the wording of kb/CROSS-STORE.md")
    if reason[1:].replace("„", "").replace("“", "").replace("'", "")[:20] not in cross.replace("„", "").replace("“", "").replace("'", ""):
        fail("the decline reason of P07 is not the wording of kb/CROSS-STORE.md")
    limit = reg.ledger["s4.driver_limit"][lang]
    if f"{limit:,}".replace(",", " " if lang == "ru" else ",") not in proposals["P10"]["text"]:
        fail(f"P10 does not carry the driver limit of ledger s4.driver_limit ({limit})")

    # ---- scheduled tasks
    ledger_tasks = reg.ledger["s10.tasks"][lang]
    owners = Counter()
    if len(tasks_file["tasks"]) != len(ledger_tasks):
        fail("the tasks are not the seven of ledger s10.tasks")
    names_of_kb = {**{name: name for _, name, _ in ledger_tasks}, **reg.ledger["kb.scheduled_report_names"][lang]}
    for task, (slot, name, when) in zip(tasks_file["tasks"], ledger_tasks):
        where = f"task {task['id']}"
        name_ok(task["owner"], where)
        owners[task["owner"]["slot"]] += 1
        if task["owner"]["slot"] != str(slot) or task["name"] != names_of_kb[name]:
            fail(f"{where}: owner and name differ from ledger s10.tasks ({slot}, '{names_of_kb[name]}')")
        days, times = task["schedule"]["days"], task["schedule"]["times"]
        said = when.split()
        want_days = None if said[0] == "daily" else [said[0][:3].lower()]
        if (days, times) != (want_days, [said[1]]):
            fail(f"{where}: schedule {days} {times} differs from ledger '{when}'")
        try:
            if prod:
                expr = prod[2](days, times, min_gap=30)
                parts = prod[3](expr)
                if parts is None or list(parts.times) != times or (list(parts.days) if parts.days else None) != days:
                    fail(f"{where}: the product does not read the schedule back as written")
            else:
                for one in times:
                    hour, minute = map(int, re.fullmatch(r"(\d\d):(\d\d)", one).groups())
                    assert hour < 24 and minute < 60
                assert all(day in ("mon", "tue", "wed", "thu", "fri", "sat", "sun") for day in days or [])
        except Exception as exc:  # noqa: BLE001
            fail(f"{where}: the product cannot express the schedule ({exc})")
        if len(task["prompt"]) > 4000:
            fail(f"{where}: prompt over 4000 characters")
        reg.when(task["created"], where)
        wordings = max(len(texts) for texts in task["cases"].values())
        if wordings != rows["sched.run_wordings"]["value"][task["id"]]:
            fail(f"{where}: {wordings} wordings, ledger row sched.run_wordings says {rows['sched.run_wordings']['value'][task['id']]}")
        for case, texts in task["cases"].items():
            for index, text in enumerate(texts):
                first = text.split("\n")[0]
                if len(SLOT.sub("000", first)) > 200:
                    fail(f"{where} case {case}[{index}]: first line over the 200 characters an Inbox line carries")
        for run in task.get("planted_runs", []):
            if run["kind"] not in ("scheduled", "late", "again", "trial") or run["status"] not in (
                    "ok", "failed", "not_run", "skipped", "running"):
                fail(f"{where}: a planted run has a kind or status the product does not have")
            if run["status"] == "failed":
                text = run["error_text"]
                if re.match(r"(?:[\w.]*(?:Error|Exception):|Error code:\s*\d{3}\b)", text) or len(text) > 200:
                    fail(f"{where}: the failure reason would be replaced or cut on the Inbox line")
                if text != rows["s10.failure_reason"][lang]:
                    fail(f"{where}: failure reason differs from ledger row s10.failure_reason")
        reg.walk(task, where)
    for slot, count in owners.items():
        if count > 10:
            fail(f"slot {slot} owns {count} tasks; the product allows ten")
    briefs = tasks_file["briefs"]
    if len(briefs["jobs_for"]) != rows["sched.brief_jobs"]["value"]:
        fail("brief jobs differ from ledger row sched.brief_jobs")
    for slot in briefs["jobs_for"]:
        if cast[slot]["rank"] == "worker" or cast[slot]["status"] != "active":
            fail(f"brief job for slot {slot}, who is not an active manager")
    if [b["owner"]["slot"] for b in briefs["at_t"]] != ["1", "2", "4", "6"]:
        fail("briefs at T are the founder's, the managing owner's, the senior's and the junior's")
    for brief in briefs["at_t"]:
        name_ok(brief["owner"], f"brief of slot {brief['owner']['slot']}")
    for where, points in [(f"brief of slot {b['owner']['slot']}", b["points"]) for b in briefs["at_t"]] + [
            (f"brief bank {p['id']}", [p["point"]]) for p in briefs["bank"]]:
        if not 1 <= len(points) <= 3:
            fail(f"{where}: one to three points")
        for point in points:
            if not point.startswith("- ") or "\n" in point:
                fail(f"{where}: a point is one line starting '- '")
            if words_of_point(point) > 20:
                fail(f"{where}: over 20 words: {point}")
    reg.walk(briefs, "briefs")

    print(f"check_assistant {lang}: {len(threads)} threads, {len(notes)} personal note rows ({len(live)} live), "
          f"{len(team['team_notes'])} team notes, {len(team['proposals'])} proposals, {len(tasks_file['tasks'])} tasks, "
          f"{len(briefs['at_t'])} briefs at T, {len(briefs['bank'])} brief points, {len(bank['patterns'])} patterns")
    for line in notes_out:
        print("  note:", line)
    for line in fails:
        print("  FAIL:", line)
    print(f"check_assistant {lang}: {'PASS' if not fails else f'{len(fails)} FAILED'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ""))
