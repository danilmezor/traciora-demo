# Design of the demo seed

The demo seed is one fictional company, designed so that an agent working on it can be scored: every number has a
stated origin, every story crosses several stores, and every question has an expected answer for the build it is
asked of.

## A seed version

A seed version is the whole of: the business and cast, the stories, the parameter ledger, the shop-system schema and
the text in both languages. Seed v1 lives in `v1/`; a later major version gets a folder of its own, so a result on v1
can still be reproduced.

| Change | Version |
|---|---|
| an existing expected answer changes | next major |
| stories or questions are added and no existing answer changes | next minor |
| wording fixed, no answer changes | patch |

An eval set names the seed it runs on. The header of each `v1/evals/questions.<cfg>.json` says `eval_set` (v1.0),
`runs_on_seed` (v1) and `ledger_sha256`, the ledger its numbers were filled from. A result records the eval set, the
seed version, T from the build's manifest and the product release.

## The company

Brennan Auto Care: three shops, East Main and Bonny Oaks in Chattanooga and Charlotte Pike in Nashville, one hour
behind. The Russian configuration holds the same shops, people and planted facts in Ulyanovsk and Kazan, but runs as
its own trade runs: its own hours, shift patterns, prices, seasons and channels. Its text is written in Russian, not
translated. `v1/cast.json` holds 33 people, 29 at work and four who have left.

## The ledger

`v1/ledger.json` is the one place every number of the seed comes from: 1,140 rows, each `measured` (a source and a
date), `derived` (a formula over other rows) or `designed` (reasoning, and a range where one exists). A row is
`fixed` (a planted instance), `scales` (grows with density) or a `rate` (with a tolerance and the count it is read
on). The 41 rows marked `outcome` are measured on the build: the ledger holds the design target and
`v1/manifest.<cfg>.json` the value of the build. `v1/checks/check_ledger.py` proves the sums close.

## Stories

A story is a thread through several stores, so a question about it cannot be answered from one screen. The sixteen
cards in `v1/stories/` hold 84 questions; each names who asks, the population, the period and the definition, or the
facts an answer must hold. Some questions exist to be refused, by rank or by site, and some have "nothing" or "cannot
tell" as the right answer. The thirteen rules R1 to R13 that every card follows are in `v1/stories/README.md`.

## The stores

The seeder fills a Traciora install in seven steps, in this order, one store each. A step is a module with
`step(cfg, client_id, replace)` and `reset(cfg, client_id)`; it reads its content from `v1/` and never imports
another step.

| Step | Store |
|---|---|
| `erp` | the shop-system database, schemas `shop` (31 tables) and `seed` (the manifest, which the source declaration leaves out) |
| `tenant` | the tenant folder and settings; the shop database's reader login, the source `erp`, its grants and notes |
| `people` | the core database's people, places and sign-ins |
| `calls` | the story calls, read in by the product's call-log reader, with handlers, transcripts and verdicts |
| `chats` | Chatwoot's contacts, conversations and messages; the assistant's drafts and the open set in `auth.db` |
| `workday` | cards, calendar, shift templates, cover rules, shifts, clock-ins, requests |
| `assistant` | memory, proposals, Ask threads with their chat files, scheduled tasks and their runs |

Ids that must survive a rebuild are derived from the seed (`seeder.ids`); several stores take their ids from the
product.

## T

A build is a function of the seed version, the configuration, the instant T and a random seed, all written to the
manifest. T is an instant on the home clock (America/New_York in English, Europe/Ulyanovsk in Russian); when the
build is asked for on a day the shops are closed, T is the close of the last open day, so T can be earlier than
`asked`. Every date in a card is an anchor counted from T: a working-day offset of a named shop or person, or a
weekday of a named week. `seeder/clock.py` turns T into every named date, and the manifest keeps them under
`anchors`. A build at another T tells the same stories, dated from that T.

Nothing calls a model at build time. Verdicts, reports, briefs, run answers and threads are written by the seeder,
the prose fixed and the numbers computed from the build.

## Goldens

| Goldens | What they hold | Checked by |
|---|---|---|
| `v1/goldens/shop.<cfg>.yaml` | 40 manager questions per configuration, each with reference SQL on schema `shop` | Gate 0 plans them; Gate 1 runs them on the nominal and the Tuesday build and compares with `answers.<cfg>.txt` |
| `v1/goldens/kb.<cfg>.yaml` | knowledge-base questions (34 English, 43 Russian) and the facts an answer must quote from a named page | Gate 0 finds every fact on its built page |
| `v1/evals/questions.<cfg>.json` | every question of the stories, knowledge base, working day and assistant: 236 records in English, 243 in Russian | `v1/checks/check_evals.py` |

The shop goldens run through the product's `golden.py`, statement guard and Postgres driver. An answer that depends
on T is computed for the build, not written by hand.

## Statements

Each store has statements of what a build must hold (`v1/<store>/checks.sql`, and `checks.py` where SQL cannot say
it). A statement is `exact` (a planted fact, a count, or an invariant that must read 0), `contrast` (a story's claim as
an inequality) or `band` (an outcome over thousands of rows, inside a wide range).

## Gates

| Gate | Where it runs | Passes when |
|---|---|---|
| Gate 0, `v1/checks/gate.py` | the seed files, in a temporary copy | the 19 checks pass; every statement of `erp/checks.sql` and every shop golden plans under EXPLAIN on an empty database loaded from `erp/schema.sql`; every knowledge-base fact is on its page; the "Slice 1" list of `v1/PENDING.md` is empty |
| Gate 1, `seeder/gate1.py` | the shop database | per configuration, builds on 22 days, under seeds 2 and 3 and as a repeat hold every statement; the goldens hold; the manifest and the answer pages equal the build; the repeat is identical; Gate 0 passed on the same commit |
| Gate 2, `seeder/gate2.py` | every store, on a dev install of the product | three builds (the nominal T, now, the nominal T again); every store's statements hold after the first two; the third writes and reads the same as the first |

The pass rate is not a gate: the product's own eval test (`seeder/README.md`, "Pass rate") asks its agent each shop golden and writes the
score and every failure's cause to `v1/evals/pass-rate.<cfg>.json`.
