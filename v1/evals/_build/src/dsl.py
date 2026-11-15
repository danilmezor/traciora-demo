# The few words the source files are written in. A record is written once for both configurations:
# every text a person reads is T(english, russian); every number in a text is a ledger token
# [[key.path|format]] or a formula [[=expression|format]] that build.py fills from ledger.json, or a
# computed slot {name} that the seeder emits per build.
RECORDS = []

NOMINAL_T = "2026-11-13T10:30"

# The open items a record still rests on, in the words of PENDING.md (or of PENDING-controller.md, which
# checks/check_evals.py does not read), by the name the sources use for them.
PENDING = {
    "inventions": "PENDING.md, The owner (O): \"Read: seven of the eight implied team notes, slot 22's declined "
                  "phone-greeting proposal and the question built on \"Parts promises\" are the assistant writer's "
                  "inventions (eval records AS.05, AS.08, AS.16 wait on it).\"",
    "fluid": "PENDING.md, The owner (O): \"The fluid table needs a specialist's read in both languages (eval record "
             "KB.C3.4).\"",
    "proposed_rows": "the answer's numbers are rows of `assistant/ledger_rows.json`, which assistant/DESIGN.md "
                     "section 7 proposes to `ledger.json`; `ledger.json` does not hold them yet",
}


# Decided, not pending: the owner, 2026-11-14.
KNOWN_FAILURE = ("fails until the product filters the call views (PENDING.md, The owner (O): \"Decided and standing: "
                 "S1.8, S6.6 and S4.6 are expected refusals that fail until the product filters the call views\"; "
                 "decided by the owner, 2026-11-14: the three stay expected refusals)")


def T(en, ru):
    return {"en": en, "ru": ru}


def C(slot, what, how, store, tables, nominal=None, design=None):
    """A computed slot: what the seeder must compute for its T, from which store and tables, and how.
    nominal: {'en': (value, quote), 'ru': (value, quote)} for the T of stories/TIMELINE.md's worked example;
    the quote is the text of that example the value is read from. design: (file, quote) where a design file
    states the value the slot is expected to come to."""
    return {"slot": slot, "what": what, "how": how, "store": store, "tables": tables, "nominal": nominal,
            "design": design}


def day(en, ru=None):
    """The nominal date of a slot in both configurations, read from TIMELINE.md's worked example."""
    ru = ru or en
    return {"en": (en, en), "ru": (ru, ru)}


def Q(id, **kw):
    kw["id"] = id
    RECORDS.append(kw)
    return kw
