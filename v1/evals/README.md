# Eval questions of seed v1

Every question an agent is asked about the seeded company, in one set per configuration: the 84 questions of the sixteen story cards, the knowledge-base outlines' questions, and the questions of the working-day and assistant designs. Each record says who asks, in which session, what kind of question it is, and what the answer must hold (`SCHEMA.md`). The Russian wording is written in Russian for the person who asks, not translated; the Russian outline's 121 questions are taken as they stand.

| File | What |
|---|---|
| `questions.en.json`, `questions.ru.json` | the sets |
| `questions.en.md`, `questions.ru.md` | the same as tables to read, written by `_build/render.py` |
| `SCHEMA.md` | one record |
| `_build/src/` | what the sets are assembled from: the story, working-day and assistant questions written once for both configurations; `kb.py` reads the two outlines |
| `_build/build.py` | fills every number from `ledger.json` (an outcome row from `manifest.<cfg>.json`) and writes the JSON |
| `../checks/check_evals.py` | proves the sets; output in `../checks/evals_check.txt` |

After a change to the ledger, a manifest, a card, an outline or `PENDING.md`: `python3 evals/_build/build.py && python3 evals/_build/render.py && python3 checks/check_evals.py`.

## Versions

This is eval set **v1.0.1** and it asks its questions of seed **v1** only: the header of each file says `eval_set` and `runs_on_seed`, and `ledger_sha256` names the ledger the numbers were filled from. A result records the eval set version, the seed version and T from the build's manifest, and the product release (design 0.2). The set holds what does not depend on the build; an answer that does is a computed slot the seeder emits for its T. A question added with no answer changed makes v1.1; a wording fixed makes v1.0.1; a seed change that changes an expected answer is seed v2 and eval set v2.

## Counts, and what is pending

<!-- generated:start -->
**English**: 236 records for 231 source questions.

| Area | Records | value | list | explanation | action | nothing | cannot tell | refusal | smoke | stale | pending |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stories | 84 | 22 | 18 | 16 | 3 | 6 | 4 | 7 | 7 | 1 | 0 |
| Knowledge base | 117 | 74 | 9 | 7 | 5 | 0 | 9 | 11 | 2 | 0 | 1 |
| Calls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Conversations | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Working day | 17 | 6 | 5 | 1 | 0 | 3 | 0 | 2 | 0 | 0 | 0 |
| Assistant | 18 | 6 | 5 | 1 | 0 | 1 | 1 | 4 | 0 | 0 | 5 |
| all | 236 | 108 | 37 | 25 | 8 | 10 | 14 | 24 | 9 | 1 | 6 |

**Russian**: 243 records for 238 source questions.

| Area | Records | value | list | explanation | action | nothing | cannot tell | refusal | smoke | stale | pending |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stories | 84 | 22 | 18 | 16 | 3 | 6 | 4 | 7 | 7 | 1 | 0 |
| Knowledge base | 124 | 80 | 9 | 7 | 5 | 0 | 10 | 11 | 2 | 0 | 1 |
| Calls | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Conversations | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Working day | 17 | 6 | 5 | 1 | 0 | 3 | 0 | 2 | 0 | 0 | 0 |
| Assistant | 18 | 6 | 5 | 1 | 0 | 1 | 1 | 4 | 0 | 0 | 5 |
| all | 243 | 114 | 37 | 25 | 8 | 10 | 15 | 24 | 9 | 1 | 6 |

**In one configuration only** (7, all Russian):

- `KB.P4.7`: the Russian leak's second and third signatures (parts issued with no sale, work done past the order: design rule R11) give the Russian base its own rule and question
- `KB.P4.8`: the same: how parts are issued from stock at the bought shop
- `KB.P5.9`: documents per order instead of a monthly statement (design rule R11)
- `KB.C6.6`: the tyre season exists only in the Russian configuration (pages `services/tires/seasonal-changeover-and-storage.md`, `customers/seasonal-tyre-change.md`)
- `KB.C6.7`: the same
- `KB.C7.8`: VAT at the till: the page `policies/documents-and-vat.md` exists only in Russian
- `KB.C8.8`: the tyre season exists only in the Russian configuration

**Expected to fail on the product as it is** (ready, not pending): `S01.8`, `S04.6`, `S06.6`. Fails until the product filters the call views (PENDING.md, The owner (O): "Decided and standing: S1.8, S6.6 and S4.6 are expected refusals that fail until the product filters the call views"; decided by the owner, 2026-11-14: the three stay expected refusals).

**Pending**, by reason:

- PENDING.md, The owner (O): "The fluid table needs a specialist's read in both languages (eval record KB.C3.4)."
  - both: KB.C3.4
- PENDING.md, The owner (O): "Read: seven of the eight implied team notes, slot 22's declined phone-greeting proposal and the question built on "Parts promises" are the assistant writer's inventions (eval records AS.05, AS.08, AS.16 wait on it)."
  - both: AS.05a, AS.05b, AS.05c, AS.08, AS.16
<!-- generated:end -->

## Read with care

- `calls/DESIGN.md` and `conversations/DESIGN.md` word no question, so those two areas are empty. The calls design names one without wording it (section 4, the difference between a call's truth and its verdict).
- A row with several askers is one record per asker (`KB.P4.6`, `KB.P5.7`, `KB.C3.2`, `AS.05`): rule R4.
- The sources name no session. A question with a pronoun carries `depends_on` when the same person asked the question before it, and `context` when somebody else did (`S08.3`, `S16.2`, eight knowledge-base questions).
- The outlines give no kind and no small-size mark; the kinds of the knowledge-base records were assigned here by the nine definitions, and `small_size` is null there and in the working day.
- English wording is the source's, with a shop's code replaced by its name (`west` is Charlotte Pike), "home time" by "Chattanooga time", and `WD.13` in the first person. The source's words are in `source.text`.
- The Russian outline drops names into sentences in the nominative; five such places are corrected and listed in `source.notes` (`KB.P3.1`, `KB.P5.5`, `KB.C8.1`, `KB.O3`, `KB.O8`).
- Values the ledger does not hold yet are computed slots with the design's sentence beside them (`WD.01`, `WD.05`, `WD.11`, `WD.15`, `AS.02`, `AS.05`, `AS.10`, `AS.12`, `AS.14`, `AS.16`).
- `AS.14` asks why there was no second brief; at the nominal T (10:30) the founder's second brief time (10:40) has not come.
