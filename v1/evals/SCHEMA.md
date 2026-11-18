# One question record

`questions.en.json` and `questions.ru.json` hold the same shape: a header and `questions`, a list of records. One record is one question asked by one person in one configuration, with the answer it must get. `checks/check_evals.py` proves every record against this page.

## The file header

| Field | Holds |
|---|---|
| `format` | `seed-eval-questions/1` |
| `eval_set` | the version of the question set, `v1.0.1` |
| `runs_on_seed` | the seed version the set asks its questions of, `v1` |
| `configuration` | `en` or `ru` |
| `ledger_sha256` | the hash of `ledger.json` the numbers were filled from |
| `sources` | per area: the source file and how many questions it holds |
| `one_configuration_only` | the ids that exist in one file only, each with the configuration and the reason |
| `questions` | the records |

## The record

| Field | Holds |
|---|---|
| `id` | stable. `S01.5` is question 5 of card S01; `KB.P4.6a` is question 6 of plant P4 in the knowledge-base outline, first asker; `KB.O3` is operating question 3; `WD.05` is W5 of the working-day design; `AS.05b` is A.5 of the assistant design, second asker. An id never changes when a wording does |
| `source` | `file`, `ref` (the source's own number: `S1.5`, `P4.6`, `W5`, `A.5`) and `text`, the source's wording of the question word for word. `notes` lists every word of the Russian outline that was corrected |
| `area` | `story`, `knowledge_base`, `calls`, `conversations`, `working_day`, `assistant` |
| `story` | the card a question belongs to or serves (`S01` to `S16`), or null |
| `configuration` | `en` or `ru` |
| `question` | what the person types, in the configuration's language and the asker's voice. A `{name}` in it is a slot the seeder fills (card S13 types the stocktake date) |
| `asker` | `slot`, `rank`, `shop` and `name` as `cast.json` has them (`shop` null for the two owners). The customers' assistant is asked by `{"slot": "customer", "rank": "public"}` |
| `session` | `surface`: `ask` (the staff assistant, signed in as the asker) or `customer_chat` (the website chat). `at`: `T`, or `T+1d` for the one question asked a day after T. `depends_on`: the id of the question asked just before it in the same conversation, when a pronoun needs it. `context`: what a pronoun refers to when the asker's own conversation does not say |
| `kind` | `value`, `list`, `explanation`, `action`, `nothing`, `cannot tell`, `refusal`, `smoke`, `stale` (stories/README.md) |
| `scope` | `population`, `period`, `definition`: rule R5 of the seed design, in English in both files |
| `expected` | the answer, below |
| `numbers` | where each filled number came from: `shown` (as written), and `key` with `path` into a ledger row, or `formula` over ledger rows |
| `proof` | where the answer can be read: `store` and `where` (table, screen or page) |
| `pages` | knowledge pages the answer rests on, as installed paths. Russian paths resolve to their source keys with `kb/kb_paths.py` |
| `seed_files` | seed files, other than the ledger, that hold a designed instance the answer names |
| `sources` | the stores an agent needs: `erp` (the shop system), `core` (the core database: calls, roster, board, calendar, Inbox), `conversations` (Chatwoot), `knowledge_base`, `memory` (notes and proposals), `account_store` (scheduled tasks, runs, briefs, Ask threads) |
| `ledger_keys` | every ledger row the answer rests on |
| `small_size` | true if the small size keeps the question, false if it drops it, null where the source does not say (the knowledge-base outlines and the working-day design) |
| `depends_on_t` | true when the expected answer holds a value the seeder computes for its T (a computed slot) |
| `status` | `ready`, or `pending` |
| `pending` | the reasons, each in the words of the open item of `PENDING.md`, or `card and ledger differ: ...` |
| `known_failure` | null, or why the expected answer is known to fail on the product as it is: a decided state, not an open one, so the record stays `ready` |

## The expected answer

`answer` is always there: the answer in a line, in the configuration's language, as a manager would accept it. The rest depends on the kind.

| Kind | Field | Holds |
|---|---|---|
| value | `value.items` | one item per figure: `{"source": "ledger", "key", "path", "shown"}`, `{"source": "derived", "formula", "shown"}`, `{"source": "computed", "slot"}`, `{"source": "page", "pages"}` or `{"source": "seed_file", "files"}` |
| list | `list` | `rule`: the membership rule, in English. `members`: the members in the configuration's language when they are the same for every T, else null. `slot`: the computed slot that holds the list per build |
| explanation, smoke | `facts` | the facts an answer must contain, one per entry with an `id`, so a grader counts them |
| action | `action` | `proposes`: what the assistant proposes or drafts. `passes_if`: the test an answer passes. `writes_nothing_unconfirmed`: always true |
| nothing | `nothing.why` | why there is none |
| cannot tell | `cannot_tell` | `lacks`: what the data does not hold. `may_give`: what an honest answer may give instead. `wrong_if`: the answer that fails |
| refusal | `refusal` | `by`: `rank`, `site`, `owner` (a person reads only their own) or `staff_only`. `reason`. `may_offer`: what may be given instead |
| stale | `stale` | `must_state`: what moment the answer must say its data is from. `wrong_if` |
| any | `facts`, `must_not`, `tolerance` | further facts the source lists; answers that fail; the tolerance on a rate |
| any | `computed` | the slots, below |

## Numbers

No number in a question or an expected answer is typed by hand.

- A ledger value is written in the source as `[[key.path|format]]` and filled by `_build/build.py` from `ledger.json` for the configuration: `[[s2.total|money]]` is `$11,400` in English and `321 360 ₽` in Russian. A value that follows from ledger rows is a formula, `[[=L('acct.A1.visits')[5]*L('acct.A1.average_order')|money]]`. Each is listed under `numbers` and recomputed by the check.
- A ledger row marked `outcome` is filled with the value the build measured, from `manifest.<cfg>.json` (seed 1 at the nominal T), not with the ledger's design target.
- A number the ledger holds inside a sentence (a clock time, a warranty term) is written as it stands; the check finds it in a row named under `ledger_keys`, on a page named under `pages`, or in a file named under `seed_files`.
- A knowledge-base answer is the outline's own text. Its numbers are the knowledge base's, proved against the catalogue and the ledger by `checks/check_kb.py`; the check finds each on a named page or ledger row and says which it could not.
- A value that depends on T is not a number in the text: it is a computed slot.

## Computed slots

A `{name}` in a text is a value the seeder computes for its T and writes beside the data (design 0.2: golden answers are built with the seed). `expected.computed` defines each slot named:

| Field | Holds |
|---|---|
| `slot` | the name |
| `what` | what the value is |
| `how` | how the seeder computes it: the anchor of `stories/TIMELINE.md` or the query |
| `store`, `tables` | where it is read |
| `nominal` | the value for T = Fri 2026-11-13 10:30, where `stories/TIMELINE.md` works it out, with the quote it is read from; null otherwise |
| `design` | a file and the sentence in it that says what the slot must come to, for a value no ledger row holds yet |

A date slot is rendered as the sentence needs it: `October 19` after "on", "since", "from" in English; «19 октября» in Russian, which stands after «с», «до», «от» and alone. Knowledge-base answers keep the knowledge base's own placeholders in backticks (`` `@price_rise` ``, `` `T-4mo` ``); they are filled as the pages are (`kb/OUTLINE.md` section 1) and are defined as slots under their own names.

## Languages

`question` and every text of `expected` except `list.rule` are in the configuration's language: no Russian in the English file, no English sentence in the Russian one. Names of systems, car makes, identifiers in backticks and slot names stay as they are. `scope`, `proof`, `list.rule`, `session.context` and the slots' `what` and `how` are the specification for the seeder and the grader and are English in both files; a knowledge-base record's `proof` is the outline's own cell, Russian in the Russian file.
