"""The step `calls`: the story calls of `v1/calls/<cfg>/` in the core database the way the product's phone pipeline puts
them there. Their legs are a seed call log the product reads (`call_log_store.read`), one read per call day at the end
of that day and a last one at T, so the product groups the legs into calls, writes each call, lands the misses and
follows them up. Each answered call is then attributed to its file's advisor as the extension's one person, and gets a
recording row with no audio, its transcript and its verdict through `commands/interactions.py` (calls/DESIGN.md section 1).

A file's `call` maps to legs, each dialling its shop's group line (the places file's extension with no slot): an
answered call is one leg on the desk that answered with the file's ring and talk; a miss is its file's legs, the first
desk at the start and the others together when the first one's ring ends; an outbound call is one leg placed from its
desk to the callee. Numbers are dialled digits in international form. The recording, transcript and analysis ids are
`ids.uuid` of the call's number; the call's id is the product's own."""
import datetime as dt
import hashlib
import json
import re
from zoneinfo import ZoneInfo

from seeder import ids, inputs, manifest

CONNECTOR, LABEL = "seed", "pbx"
PROVIDER = f"{CONNECTOR}:{LABEL}"
COUNTRY = {"en": "1", "ru": "7"}  # the calling code before a number a file writes without one
# Call 16's caller rang that morning and nobody answered (its call_log note: the hour, the first desk, then every desk).
# Call 31's earlier misses stay out: its file names no desk they rang after the first.
MORNING_MISS = 16


def digits(number, cfg):
    """A phone as the call log carries it: its digits, after the configuration's calling code when it has none."""
    found = re.sub(r"\D", "", number)
    return found if number.strip().startswith("+") else COUNTRY[cfg] + found


def places(cfg):
    """Each shop of the places file by its key."""
    return {p["key"]: p for p in inputs.load(f"tenant/roles-and-places.{cfg}.json")["places"]}


def legs(d, start, cfg, place):
    """The call-log legs of the call file `d` that starts at `start` (aware) at the shop `place`: CallLeg rows of the
    product's contract, the call's own first; for call 16 then the four legs of its morning miss."""
    from traciora.core.phonecalls.ingestion.contracts import CallLeg

    c, key = d["call"], f"{cfg}/{d['number']}"
    line = next(x["ext"] for x in place["extensions"] if x.get("slot") is None)

    def rings(at, caller, desks, tag):  # the first desk alone, then the others together when its ring ends
        first = desks[0][1]
        return [CallLeg(started_at=at + dt.timedelta(seconds=first if i else 0), caller=caller, dialled=line, rang=desk,
                        answered_by=None, context="", ring_s=ring, talk_s=0, status=status, kind="staff", recording_id=None,
                        source_key=f"{key}/{tag}{i + 1}") for i, (desk, ring, status) in enumerate(desks)]

    if c["direction"] == "outbound":
        callee = digits(c["callee_phone"], cfg)
        return [CallLeg(started_at=start, caller=line, dialled=callee, rang=c["placed_from"], answered_by=callee,
                        context="", ring_s=c["ring_s"], talk_s=c["talk_s"], status="answered", kind="outbound",
                        recording_id=None, source_key=f"{key}/1")]
    caller = digits(c["caller_phone"], cfg)
    if c.get("legs"):
        return rings(start, caller, [(x["extension"], x["ring_s"], x["status"]) for x in c["legs"]], "")
    own = [CallLeg(started_at=start, caller=caller, dialled=line, rang=c["answered_by"], answered_by=c["answered_by"],
                   context="", ring_s=c["ring_s"], talk_s=c["talk_s"], status="answered", kind="staff", recording_id=None,
                   source_key=f"{key}/1")]
    if d["number"] != MORNING_MISS:
        return own
    note = d["call_log"].get("earlier_miss") or d["call_log"]["missed_before"]
    at = dt.datetime.combine(start.date(), dt.time.fromisoformat(re.search(r"\d\d:\d\d", note)[0]), start.tzinfo)
    every = sorted(x["ext"] for x in place["extensions"] if x.get("slot") and not x["slot"].startswith("F"))
    return own + rings(at, caller, [(re.search(r"first desk (\d+)", note)[1], 20, "no_answer")] + [(x, 15, "no_answer") for x in every], "miss/")


def dialogue(d, labels):
    """The stored dialogue of the call file `d`: one line a segment, its speaker's label (the product's role labels) and
    its words, as the restoration writes it; with the segments as the transcript keeps them."""
    segments = d["transcript"]["segments"]
    return "\n".join(f"{labels[s['speaker_label']]}: {s['text']}" for s in segments), segments


def calls(cfg, built):
    """Every call file of the configuration with its start: the manifest's day of the call at the file's local start, on
    its shop's clock, and its legs. A story whose manifest phone is not the file's number is refused, every case listed."""
    shops = places(cfg)
    found, wrong = [], []
    for n, d in sorted(inputs.STORY_FILES[("calls", cfg)].items()):
        c = d["call"]
        day = dt.date.fromisoformat(str(built["calls"][str(n)]["day"]))
        start = dt.datetime.combine(day, dt.time.fromisoformat(c["local_start"]), ZoneInfo(shops[c["site"]]["tz"]))
        story = built["stories"].get(f"call.{n:02d}") or built["stories"].get(d["story"])
        number = c.get("caller_phone") or c.get("callee_phone")
        if story and story["phone"] and digits(story["phone"], cfg) != digits(number, cfg):
            wrong.append(f"call {n}: {number} in the file, story {d['story']} has {story['phone']} in the shop database")
        found.append((n, d, start, legs(d, start, cfg, shops[c["site"]])))
    if wrong:
        raise SystemExit("the call files and the shop database disagree:\n  " + "\n  ".join(wrong))
    return found


class Log:
    """The seed's call log as a `CallLogSource`: every leg it holds that started in [since, now)."""

    internal_digits = 3

    def __init__(self, held):
        self.held = sorted(held, key=lambda leg: (leg.started_at, leg.source_key))

    def call_legs(self, since, *, now):
        from traciora.core.phonecalls.ingestion.contracts import CallLogRead

        return CallLogRead(legs=tuple(x for x in self.held if since <= x.started_at < now), covered_from=since, unplaced=(), refused=0)

    def recording_names(self, recording_id):
        return (recording_id,)


def step(cfg, client_id, replace):
    from traciora.core.commands.interactions import (add_participant, append_segments, attach_media, record_analysis,
                                                     record_contact, upsert_transcript)
    from traciora.core.core_db.engine import connect, tenant_dsn
    from traciora.core.phonecalls.config import load_phonecalls_config
    from traciora.core.phonecalls.ingestion import call_log_store, processing, repository
    from traciora.core.security import tenant_binding

    built = manifest.read(manifest.shop_dsn(client_id))
    if built.get("cfg") != cfg:
        raise SystemExit(f"the shop database is built for {built.get('cfg')}, not {cfg}")
    found = calls(cfg, built)
    if replace:
        reset(cfg, client_id)
    home = ZoneInfo(built["zone"])
    T = dt.datetime.strptime(built["T"], manifest.FORMAT).replace(tzinfo=home)
    log = Log([leg for *_, x in found for leg in x])
    ends = sorted({min(dt.datetime.combine(start.astimezone(home).date() + dt.timedelta(days=1), dt.time(), home), T) for _, _, start, _ in found} | {T})
    config = load_phonecalls_config()
    card, labels = config.scorecard, config.role_labels
    restoration, verdicts = processing.restoration_fingerprint(config, client_id=client_id), processing.verdict_version(config)
    rows = 0
    with connect(tenant_dsn(client_id)) as conn:
        conn.autocommit = True
        if conn.execute("SELECT exists (SELECT 1 FROM interactions.recording_run WHERE provider = %s)", (PROVIDER,)).fetchone()[0]:
            raise SystemExit("the story calls are loaded already: run the step with --replace")
        connection = repository.connection_for(conn, CONNECTOR, LABEL)
        for now in ends:
            with tenant_binding.at(now):
                outcome = call_log_store.read(conn, connection, log, now=now, run_kind="backfill")
            if outcome is None or outcome.error:
                raise SystemExit(f"the call log read at {now:%Y-%m-%d %H:%M} failed: {outcome and outcome.error}")
            rows += 1 + outcome.legs + outcome.calls + outcome.missed
        with conn.transaction():
            for n, d, _, held in found:
                if not d.get("transcript"):
                    continue
                first = held[0]
                interaction, started, answered, ended = conn.execute(
                    "SELECT i.id, i.started_at, i.answered_at, i.ended_at FROM interactions.call_leg l JOIN interactions.interaction i ON i.id = l.interaction_id"
                    " WHERE l.provider = %s AND l.started_at = %s AND l.extension = %s", (PROVIDER, first.started_at, first.rang)).fetchone()
                interaction, media, transcript = str(interaction), str(ids.uuid("call-recording", n, cfg)), str(ids.uuid("call-transcript", n, cfg))
                # The file's advisor, the one person at the desk that answered (tier 5): not the roster's presumption, and not
                # the desk's owner today, since desk 103 changed hands.
                person = str(ids.uuid("person", str(d["cast"]["advisor"]["slot"]), cfg))
                record_contact(conn, connection.actor_id, interaction, person_id=person, person_confidence_tier=5,
                               attributed_by="pbx_extension", started_at=started)
                # The roster's handler row goes with its presumption, by the statement call_log_store._write_call uses.
                conn.execute("DELETE FROM interactions.interaction_participant WHERE interaction_id = %s AND role = 'handler'"
                             " AND created_by = %s", (interaction, connection.actor_id))
                add_participant(conn, connection.actor_id, interaction_id=interaction, person_id=person, role="handler", from_at=answered)
                t, v = d["transcript"], d["verdict"]
                attach_media(conn, connection.actor_id, media, kind="recording", subject_type="interaction", subject_id=interaction,
                             interaction_id=interaction, mime="audio/wav", duration_s=t["duration_s"], pii_state="unscanned", source="pbx",
                             sha256=hashlib.sha256(ids.name("call-recording", n, cfg).encode()).digest())
                text, segments = dialogue(d, labels)
                upsert_transcript(conn, connection.actor_id, transcript, interaction_id=interaction, media_id=media, engine=t["engine"],
                                  engine_version=t["engine_version"].split(repository.RESTORE_MARK)[0] + repository.RESTORE_MARK + restoration,
                                  language=t["language"], text=text, pii_state=t["pii_state"], word_count=t["word_count"],
                                  duration_s=t["duration_s"], is_current=True)
                append_segments(conn, connection.actor_id, transcript, [
                    {k: s[k] for k in ("start_ms", "end_ms", "speaker_label", "text", "confidence")} for s in segments])
                public = v["result_public"] | {"scorecard": card.version, "weights": card.weights_version, "line": first.dialled
                                               if first.kind != "outbound" else first.caller}
                record_analysis(conn, connection.actor_id, interaction_id=interaction, transcript_id=transcript, kind=v["kind"],
                                prompt_version=verdicts, result_public=public,
                                result_enc=json.dumps(v["result_enc_plain"], ensure_ascii=False) if v["result_enc_plain"] else None,
                                score=v["score"], produced_at=ended, is_current=True)
                rows += 5 + len(segments)
    return rows


def reset(cfg, client_id):
    """The seed call log's legs, calls, misses, handlers, recordings, transcripts, verdicts, reads and its connector
    actor: every row of the provider, so a build in one configuration replaces the other."""
    from traciora.core.core_db.engine import connect, tenant_dsn

    with connect(tenant_dsn(client_id)) as conn:
        held = [r[0] for r in conn.execute("SELECT DISTINCT interaction_id FROM interactions.call_leg WHERE provider = %s"
                                           " AND interaction_id IS NOT NULL", (PROVIDER,))]
        # Verdicts and lines are append-only: their delete triggers are off for this transaction alone (the owner may).
        for table, trigger in (("interaction_analysis", "interaction_analysis_append_only"), ("transcript_segment", "transcript_segment_append_only")):
            conn.execute(f"ALTER TABLE interactions.{table} DISABLE TRIGGER {trigger}")
        conn.execute("DELETE FROM interactions.interaction_analysis WHERE interaction_id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.transcript_segment WHERE transcript_id IN"
                     " (SELECT id FROM interactions.transcript WHERE interaction_id = ANY(%s))", (held,))
        for table, trigger in (("interaction_analysis", "interaction_analysis_append_only"), ("transcript_segment", "transcript_segment_append_only")):
            conn.execute(f"ALTER TABLE interactions.{table} ENABLE TRIGGER {trigger}")
        conn.execute("DELETE FROM interactions.transcript WHERE interaction_id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.media_object WHERE interaction_id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.missed_call WHERE interaction_id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.interaction_participant WHERE interaction_id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.call_leg WHERE provider = %s", (PROVIDER,))
        conn.execute("DELETE FROM interactions.interaction WHERE id = ANY(%s)", (held,))
        conn.execute("DELETE FROM interactions.recording_run WHERE provider = %s", (PROVIDER,))
        conn.execute("DELETE FROM core.actor WHERE kind = 'connector' AND actor_key = %s", (PROVIDER,))
        conn.commit()
