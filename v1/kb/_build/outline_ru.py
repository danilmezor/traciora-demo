# -*- coding: utf-8 -*-
"""Writes kb/OUTLINE-ru.md: the Russian titles and display names per page key, the pages of one configuration only,
the planted challenges with their Russian facts, and the eval questions in Russian with expected answers.
Every amount is computed here from catalogue.json and ledger.json, so the outline follows the seed files."""
import json, posixpath, os
from collections import Counter
from kbr import *
import kbb, kbr

reg_all = json.load(open(REG))
reg = {p: r for p, r in reg_all.items() if not r.get('not_a_page')}
en = json.load(open(kbb.HERE + '/registry.json'))
m = fmt
def who(slot, rank):
    return f"{slot}, {rank}"
def nm(slot, form='fi'):
    p = PEOPLE[str(slot)]['ru']['full_name'].split()
    return {'fi': p[0] + ' ' + p[-1], 'full': ' '.join(p), 'io': ' '.join(p[:2]) if len(p) == 3 else p[0], 'f': p[-1]}[form]
def acn(aid, i, form='full'):
    p = ACCOUNTS[aid]['contacts'][i]['name'].split()
    return ' '.join(p) if form == 'full' else ' '.join(p[:2])
def an(aid):
    a = ACCOUNTS[aid]['name']; return a if '«' in a else '«' + a + '»'
def pc(x, nd=1): return ('%g' % round(float(x), nd)).replace('.', ',')

FOLDERS = [('', 'База знаний «Ермак-Сервиса»', 'worker (tenant setting); README.md itself junior'), ('customers', 'Клиентам', 'worker = public'), ('shop-floor', 'Цех', 'worker = public'),
           ('services', 'Услуги', 'worker = public'), ('services/maintenance', 'ТО', None), ('services/brakes', 'Тормоза', None), ('services/tires', 'Шины', None),
           ('services/diagnostics', 'Диагностика', None), ('services/suspension', 'Ходовая', None), ('services/ac', 'Кондиционер', None), ('services/electrical', 'Электрика', None),
           ('services/engine', 'Двигатель', None), ('services/transmission', 'Трансмиссия', None), ('services/inspections', 'Осмотры', None),
           ('prices', 'Цены', 'worker = public for the price list; the other three files junior'), ('policies', 'Правила', 'junior'), ('accounts', 'Корпоративные клиенты', 'junior'),
           ('accounts/credit', 'Лимиты задолженности', 'middle'), ('how-to', 'Как мы работаем', 'junior'), ('parts', 'Запчасти', 'junior'), ('shops', 'Площадки', 'junior'),
           ('shops/main', 'Московское шоссе', None), ('shops/east', 'Инженерный', None), ('shops/west', 'Техническая', None), ('team', 'Команда', 'junior'),
           ('office', 'Бухгалтерия', 'middle'), ('management', 'Руководству', 'senior'), ('management/owners', 'Владельцам', 'administrator'),
           ('playbooks', 'Памятки по должностям', 'administrator (pinned by the product\'s import)')]
vis_short = {'public': 'public', 'staff': 'staff', 'middle': 'middle', 'senior': 'senior', 'administrator': 'admin'}
def voice(s):
    s = str(s)
    return s + ' ' + nm(s)
tree = []
for d, name, seen in FOLDERS:
    ps = sorted(p for p in reg if posixpath.dirname(p) == d)
    if not ps: continue
    seen = seen or 'inherits ' + [f[2] for f in FOLDERS if f[0] == d.split('/')[0]][0].split(' ')[0]
    tree.append(f"\n### `{d or '(root)'}/` · «{name}» · {len(ps)} · seen from {seen}\n")
    tree.append('| Page key | Russian title | English title | Vis. | Voice | Len. | Rev. | In |')
    tree.append('|---|---|---|---|---|---|---:|---|')
    for p in ps:
        r = reg[p]
        flag = ' **stale**' if r['stale_on_purpose'] else ''
        tree.append(f"| `{posixpath.basename(p)}` | {r['title']}{flag} | {r['title_en'] or '-'} | {vis_short[r['visibility']]} | {voice(r['voice_of_slot'])} | {r['length_class'].replace('binary: ', '')} | {r['n_rev']} | {'both' if r['exists_in'] == 'both' else '**ru only**'} |")
TREE = '\n'.join(tree)

mdp = [p for p in reg if p.endswith('.md')]
byvis = Counter(reg[p]['visibility'] for p in mdp)
words = sum(json.load(open(f'{OUT}/facts-ru/{p[:-3]}.json'))['words_ru'] for p in mdp)
nhist = len([p for p in reg if reg[p].get('first_revision_text')])
only_ru = sorted(p for p in reg if p not in en)
verify, settled_items = [], []
for p in sorted(reg):
    s = json.load(open(OUT + '/facts-ru/' + (p[:-3] if p.endswith('.md') else p) + '.json'))
    for v in s.get('to_verify', []): verify.append((p, v))
    for v in s.get('settled', []): settled_items.append((p, v))
OUTC = {(p, o['starts']): o for p, os_ in kbr.OUTCOMES.items() for o in os_}
def outcome(p, item):
    return next(o for (pp, st), o in OUTC.items() if pp == p and item.startswith(st))
to_price_list = sorted(p for p in reg if 'prices/price-list.md' in reg[p]['links_to'])

# ---- figures used in the expected answers ----------------------------------------------------------------
TBn, TBo = nt('timing_belt_kit'), nt('timing_belt_kit', when='before_rise')
TBe, TBp, TBpo = nt('timing_belt_kit', 'economy'), nt('timing_belt_kit', 'premium'), nt('timing_belt_kit', 'premium', when='before_rise')
TBl, TBlo = nlab('timing_belt_kit'), nlab('timing_belt_kit', 'before_rise')
S8 = {k: LV('s8.' + k) for k in ('price_now', 'price_quoted', 'supplies', 'bill_list', 'bill_before_tax', 'discount', 'discount_pct', 'paid_with_tax')}
FPR, FPRo = nt('front_pads_rotors'), nt('front_pads_rotors', when='before_rise')
H = LV('price.hour.history'); HC = LV('price.hour.company_history')
DL = LV('s4.driver_limit'); OVER = DL + 1500
B7 = LV('s7.bill'); F2, F3 = LV('s2.f1.second'), LV('s2.f1.third')
PM_CO = nt('fleet_pm_van', cls='van', company=True)
TIE = nt('outer_tie_rod'); AL = nt('wheel_alignment')
TOW = 3000 + 4 * 70
SUP_FPR = nsup(nlab('front_pads_rotors'))
TO30 = [nt('scheduled_maintenance'), nt('oil_service'), nt('engine_air_filter'), nt('cabin_air_filter'), nt('brake_fluid_exchange')]
TO30_SUP = nsup(nlab('scheduled_maintenance'), nlab('oil_service'), nlab('engine_air_filter'), nlab('cabin_air_filter'), nlab('brake_fluid_exchange'))
ACD = nt('ac_recharge_1234yf') - nt('ac_recharge')
ALT_L = nlab('alternator'); REB = nt('transmission_rebuild'); DEP = JOBS['transmission_rebuild']['sublet']['price'] / 2
stale_bq = [(nrate('standard', 'before_rise'), nrate())] + [(nt(k, when='before_rise'), nt(k)) for k in ('front_pads_rotors', 'rear_pads_rotors', 'front_brake_pads', 'rear_brake_pads', 'brake_inspection', 'brake_fluid_exchange')]
CB = {k: LV('calls.callback.' + k) for k in ('main.after', 'east', 'west')}

doc = f"""# Knowledge base of seed v1, Russian configuration: outline

Company: «Ермак-Сервис» (Ульяновск: Московское шоссе, 40 and 10-й Инженерный проезд, 30; Казань: улица Техническая, 30). Written as original Russian from the fact sheets, the ledger's `ru` values, the Russian catalogue and `demo-seed-research/ru-shop.md`; the English pages were read afterwards for dropped facts. This file is generated by `_build/outline_ru.py`: every amount in it is computed from `catalogue.json` and `ledger.json` at build time.

| | |
|---|---|
| Pages (Markdown) | {len(mdp)}, all written: `ru/<path>.md`, one sheet each in `facts-ru/<path>.json` (what differs from the English sheet, new facts, items to verify, the page's tables and lists as data, prices, people, dates, revisions) |
| Binary documents | {len(reg) - len(mdp)}, drafted in `ru/_binaries.md`, one sheet each in `facts-ru/<path>.<ext>.json` |
| Same key as the English base | {len([p for p in reg if p in en])} of {len(en)} English keys; none is missing |
| Only in Russian | {len(only_ru)}: {', '.join('`' + p + '`' for p in only_ru)} |
| By visibility | public {byvis['public']} · staff {byvis['staff']} (+ 5 binaries) · middle {byvis['middle']} · senior {byvis['senior']} · administrator {byvis['administrator']} |
| Pages with history | {sum(1 for p in mdp if reg[p]['has_history'])} |
| Pages stale on purpose | 6, the same six keys as in English |
| First-revision texts | `ru/_history/`: {nhist} pages whose only later change is the price pass, generated at the hour before the last rise ({m(nrate('standard','before_rise'))}) |
| Length | about {round(words, -2):,} words |
| New facts / to verify | {sum(reg[p]['n_new'] for p in reg)} / {len(verify)} (sections 7 and 8) |
| Eval questions | sections 5 and 6 |
| Reading guide for the owner | `ru/_README.md` (`ru/README.md` is the base's own front page) |

## 1. Placeholders

The grammar of `OUTLINE.md` is unchanged: `{{{{<when>|<format>}}}}`, the bar escaped inside a table cell.

Two events exist only in Russian, because the Russian shop raised its hour three times in two years (design R11, ledger `price.hour.history`):

| Event | Anchor | What |
|---|---|---|
| `@price_rise_1` | {H[1][0]} | нормо-час {m(H[0][1])} → {m(H[1][1])}, договорной {m(HC[0])} → {m(HC[1])} |
| `@price_rise_2` | {H[2][0]}: one statement in the ledger, `catalogue.json` and `stories/TIMELINE.md`; the day story S2 begins | {m(H[1][1])} → {m(H[2][1])}, договорной {m(HC[1])} → {m(HC[2])} |
| `@price_rise` | P, as in English | {m(H[2][1])} → {m(H[3][1])}, договорной {m(HC[2])} → {m(HC[3])} |

`@warranty_2424` keeps its English name; in Russian it is the day the 30-day warranty came into force (T-26 months). `@belt_proposal` is slot 5's first working day after the discount on the timing-belt bill, not the next full open day: Russian advisors work two on, two off (`stories/TIMELINE.md`, ledger `s12.proposal`). The first-revision texts speak of the rise before the last: where the current page says `@price_rise+3wd:main` they say `@price_rise_2+3wd:main`.

How the seeder renders the four formats in Russian, and how the pages are written to fit them:

| Format | Russian rendering | Where the pages put it |
|---|---|---|
| `date` | 4 марта 2026 г. | after «с», «до», «от», after a colon («Проверено: …»), or alone |
| `day` | четверг, 19 ноября (nominative weekday) | at the head of a sentence followed by a colon, or after a colon; never after «в» |
| `month` | март 2026 г. (nominative) | in brackets or after a colon |
| `season` | весна 2026 г. | after a colon |

Not placeholders, on purpose: the two tyre windows (13 апреля — 10 мая, 13 октября — 9 ноября: recurring month-days of ledger `season.tyre.windows`), 1 и 2 января (the closed dates), and two dates of law (1 января 2025 года: VAT at 5 %, ledger `tax.ru_vat_from`; 1 сентября 2025 года: ПП № 780 in force).

Money is written «12 520 ₽», kopecks only where there are any («102,60 ₽»). Every price on every page includes VAT at 5 % («с НДС») and nothing is added on top for any customer, an account billed on terms included; the amount before VAT of a bill is its total / 1,05 (ledger `tax.ru_price_basis`, `kb.vat_in_list_prices`). A private customer's order, act and receipt say «в том числе НДС 5 %»; an account's счёт and УПД show the amount before VAT, the VAT and the total (ledger `kb.documents`).

## 2. Who may read what

Exactly as in `OUTLINE.md` section 2: the same paths, the same `seen_from`, the same order of seeding. `ru/playbooks/*` goes to the tenant's `playbooks/` directory, everything else to `knowledge_base/`. The folder display names are in section 4.

The eleven pages of ledger row `s12.pages`, by their Russian names:

| Ledger | Page | Russian title | Readers |
|---|---|---|---|
| Price list | `prices/price-list.md` | {reg['prices/price-list.md']['title']} | public |
| Timing belt | `services/engine/timing-belt.md` | {reg['services/engine/timing-belt.md']['title']} | public, stale |
| Brake questions | `services/brakes/brake-questions.md` | {reg['services/brakes/brake-questions.md']['title']} | public, stale |
| Warranty | `customers/warranty.md`; staff terms `policies/warranty.md` | {reg['customers/warranty.md']['title']}; {reg['policies/warranty.md']['title']} | public |
| Warranty (old) | `customers/warranty-policy.md` | {reg['customers/warranty-policy.md']['title']} | public, out of date |
| Booking a visit | `how-to/booking-a-visit.md` | {reg['how-to/booking-a-visit.md']['title']} | staff |
| Discount policy | `policies/discounts.md` | {reg['policies/discounts.md']['title']} | staff |
| Company accounts | `accounts/company-account-terms.md` | {reg['accounts/company-account-terms.md']['title']} | staff |
| Suppliers | `parts/suppliers.md` | {reg['parts/suppliers.md']['title']} | staff |
| Staff handbook | `team/staff-handbook.docx` | {reg['team/staff-handbook.docx']['title']} | staff |
| Pay and till | `management/pay-and-till.md` | {reg['management/pay-and-till.md']['title']} | senior |

## 3. The three shops and the people, as the pages name them

| Site | Staff say | Customers read | Address | Line |
|---|---|---|---|---|
| `main` | Московское шоссе | Московское шоссе (Ульяновск) | {ADDR['main']} | {TEL['main']} |
| `east` | Инженерный | Инженерный (Ульяновск, Новый город) | {ADDR['east']} | {TEL['east']} |
| `west` | Техническая; in Ulyanovsk also «Казань» | Техническая (Казань) | {ADDR['west']} | {TEL['west']} |

The staff names are ledger row `geo.short_name` (the street each shop stands on); «Новый город» in the cast's Russian biographies is the district the second shop is in, and the customer pages name it once so that the shop can be found. People are addressed as `cast.json` says: {nm(2,'io')}, {nm(4,'io')}, {nm(3,'io')}, {nm(22,'io')} by name and patronymic; Дима, Алина, Света, Паша, Михалыч, Лёха among colleagues; signatures are the form the person would sign with. Declined forms are hand-written in the batches and checked against the seed files by their stems (`kbr.P`, `kbr.AD`, `kbr.ACD`): a renamed person or contact stops the build.

## 4. The tree

Columns: *Russian title* as the page is headed; *English title* of the same key; *Vis.*; *Voice* the cast slot and Russian name; *Len.*; *Rev.* revisions to seed; *In* which configuration has the page.
{TREE}

### Pages that exist in one configuration only

| Page | Why |
|---|---|
| `customers/seasonal-tyre-change.md` | The Russian year has two tyre seasons: seasonal tyre jobs lead {pc(LV('season.tyre.share_of_orders'))} % of orders and fill two four-week windows at {pc(LV('season.tyre.factor'), 0)} times the yearly mean. In English it is 0,2 % of orders and one paragraph. |
| `services/tires/seasonal-changeover-and-storage.md` | The same, for the counter: three order lines, prices by vehicle class, storage. |
| `how-to/tyre-season.md` | How the desk runs inside a window: the seasonal hire, six-day weeks, the booking grid, calls up {pc(LV('season.tyre.calls_up_pct'), 0)} %. |
| `policies/documents-and-vat.md` | The Russian counterpart of the English sales-tax lines and of the monthly statement: what a customer and a company get on paper (заказ-наряд, акт приёма-передачи, акт выполненных работ, кассовый чек; счёт и УПД по каждому наряду) and how VAT at 5 % is shown and said. |

No English page is absent in Russian. Six keys carry a different subject, because the trade differs:

| Key | English | Russian |
|---|---|---|
| `shops/main/saturdays.md` | the Saturday morning shift | weekends and public holidays: the shops are open every day; what is missing is the managers, the office, the parts manager and the diagnostician |
| `policies/voids-and-refunds.md` | voids after payment | work past the order, parts issued with no sale, and money back only by a return receipt (design R11) |
| `office/statements-and-receivables.md` | monthly statements | an invoice and a closing document per order, a reconciliation act quarterly |
| `office/payroll-hours.md` | two-week pay periods | the timesheet and pay twice a month |
| `parts/returns-and-cores.md` | returns and core charges | returns; exchange units only for steering racks |
| `team/staff-handbook.docx` | a staff handbook | «Правила внутреннего трудового распорядка» |

## 5. Planted on purpose, with the Russian facts and the questions in Russian

«Спрашивает» is the cast slot and rank; the customers' assistant is asked by «клиент». Expected answers hold for any T.

### Story plants

**P1. Two pages at the hour from before the last rise (S12).** `services/engine/timing-belt.md` ({hrs('timing_belt_kit')} н/ч по {m(nrate('standard','before_rise'))}, {m(TBo)}, «в тот же день») and `services/brakes/brake-questions.md` (signed «В. С.»: {', '.join(m(a) for a, b in stale_bq)}). The stale hour is the last but one of four ({', '.join(m(h[1]) for h in H)}).

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P1.1 | Сколько у нас стоит замена ремня ГРМ на Renault Logan 1.6 16 кл.? | {who(7,'junior')} | {m(TBn)} со стандартным комплектом (эконом {m(TBe)}, оригинал {m(TBp)}), без расходных материалов; {m(S8['bill_list'])} с расходными материалами — это сумма к оплате, НДС уже в ней. Страница услуги показывает {m(TBo)} и устарела | `prices/price-list.md` (Двигатель и система охлаждения), `services/engine/timing-belt.md` |
| P1.2 | На каких страницах остались старые цены? | {who(4,'senior')} | Ровно на двух: «Ремень ГРМ» и «Вопросы по тормозам». Не на странице про нормо-час и не на «Как меняются цены»: там {m(nrate('standard','before_rise'))} упомянут как история | обе страницы; `prices/labour-rates-and-fees.md` |
| P1.3 | Клиент говорит, что ему назвали {m(FPRo)} за передние диски с колодками. Это наша цена? | {who(17,'junior')} | Нет: {m(FPR)} в стандарте. {m(FPRo)} — со страницы «Вопросы по тормозам», написанной до повышения | `prices/price-list.md`, `services/brakes/brake-questions.md` |
| P1.4 | Можно сказать клиенту, что ремень ГРМ поменяем в тот же день? | {who(7,'junior')} | Нет. Так написано на странице про ремень ГРМ, но страница про заказ запчастей запрещает «сегодня же» только по длительности работы; записывать на полный день | `parts/ordering-parts.md`, `how-to/taking-a-call.md`, `services/engine/timing-belt.md` |
| P1.5 | Когда менялся нормо-час и с какого на какой? | {who(6,'junior')} | В день `@price_rise`: с {m(H[2][1])} до {m(H[3][1])}; договорной с {m(HC[2])} до {m(HC[3])}; фиксированные цены на {pc(LV('price.rise.last_pct'), 2)} %; запчасти не менялись. До этого было ещё два повышения: `@price_rise_1` ({m(H[0][1])} → {m(H[1][1])}) и `@price_rise_2` ({m(H[1][1])} → {m(H[2][1])}) | `prices/labour-rates-and-fees.md`, `prices/how-prices-change.md` |
| P1.6 | Сколько стоит поменять ремень ГРМ на «Логане»? | клиент | {m(TBn)} со стандартным комплектом, по прайс-листу; НДС в цене. Помощник видит и устаревшую страницу и не должен отвечать {m(TBo)} | `prices/price-list.md` |

**P2. An old warranty page beside the current one (S12).** `customers/warranty-policy.md` («Гарантийные обязательства»: 14 дней на любые работы, на электрооборудование гарантии нет, только там, где делали; действует с T-6y, пересмотрена T-38mo, подпись основателя) beside `customers/warranty.md` («Наша гарантия»: 30 дней на слесарные и электротехнические работы, с `@warranty_2424`); staff terms in `policies/warranty.md`.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P2.1 | Какая у нас гарантия? | {who(6,'junior')} | 30 дней на слесарные и электротехнические работы, без ограничения пробега, во всех трёх сервисах; на запчасти — гарантия производителя. Старая страница устарела и до сих пор говорит «14 дней» | `customers/warranty.md`, `policies/warranty.md`, `customers/warranty-policy.md` |
| P2.2 | Машину делали на Инженерном. Может ли гарантийный ремонт сделать Московское шоссе? | {who(17,'junior')} | Да, любой из трёх сервисов. Старая страница говорит: только там, где делали | те же |
| P2.3 | Какая гарантия на новый генератор? | {who(7,'junior')} | 30 дней на работу по замене; на сам генератор — гарантия производителя, срок в заказ-наряде (после 30 дней деталь меняют по гарантии, работа платная). Не «гарантии нет»: это правило старой страницы про электрооборудование | те же |
| P2.4 | Какая страница о гарантии действует и откуда это видно? | {who(4,'senior')} | «Наша гарантия» и «Гарантия» для сотрудников: действуют с `@warranty_2424`, проверена T-4mo, {nm(2,'full')}. Другая действует с T-6y, пересмотрена T-38mo, и действующая страница сама говорит, что старая ещё висит | обе страницы |
| P2.5 | Какая у вас гарантия на замену тормозов? | клиент | 30 дней на работу; колодки и диски — от заводского брака, износ браком не считается. Помощник видит и старую страницу и не должен отвечать «14 дней» | `customers/warranty.md` |

**P3. A correction that waits (S12).** Proposed by slot 5 at `@belt_proposal` (in Russian: his first working day after the discount) on the timing-belt page; pending; deciders slots 4, 22, 1, 2. The exact before and after text is in `facts-ru/services/engine/timing-belt.json` under `pending_proposal`.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P3.1 | Что в базе знаний ждёт утверждения? | {who(4,'senior')} | Одно предложение: правка {nm(5,'full')} к странице «Ремень ГРМ» | предложение; строка `knowledge.proposed` во Входящих |
| P3.2 | Кто предложил, когда и зачем? Что именно меняется? | {who(2,'admin')} | {nm(5)}, `@belt_proposal`; старый нормо-час; {m(TBo)} становится {m(TBn)}, {m(TBlo)} — {m(TBl)}, {m(TBpo)} — {m(TBp)}; абзац «в тот же день» заменён на «записывайте на полный день» | `pending_proposal` |
| P3.3 | Ждёт ли оно дольше нашего собственного стандарта? | {who(2,'admin')} | Нет: предложено день-два назад, в первый рабочий день Димы после скидки (для T = пт 13.11.2026 — два дня назад); стандарт — пять рабочих дней | `policies/service-standards.md` |
| P3.4 | Если его утвердят, старых цен в базе не останется? | {who(5,'middle')} | Останутся: страница «Вопросы по тормозам» устарела так же, и правки к ней нет | P1 |
| P3.5 | Может ли Дима утвердить его сам? | {who(5,'middle')} | Нет: он может предлагать, но не публиковать, и своё предложение никто сам не утверждает | `how-to/using-this-knowledge-base.md` |

**P4. The rules written after the theft (S2).** In Russian the leak has three signatures (ledger `s2.f1.*`): {LV('s2.f1.discounted')} unapproved discounts on cash orders ({m(LV('s2.f1.discount_total'))}), {F2['count']} issues of parts with no sale ({m(F2['total'])} at cost), {F3['count']} orders with {F3['hours']} clocked hours above the hours sold ({m(F3['total'])}); {m(LV('s2.total'))} in all, an estimate. The pages: `policies/discounts.md` (created at `@discount_rule` by slot 2, one later edit), `policies/voids-and-refunds.md` («Работа мимо наряда, списания и возврат денег»), `how-to/closing-the-till.md`, the changed `shops/west/opening-and-closing.md`, and the senior memo.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P4.1 | Какое у нас правило по скидкам и с какого времени? | {who(24,'junior')} | Скидку больше 10 % от всей суммы наряда до скидки согласует руководитель до закрытия наряда, с отметкой в наряде; действует с `@discount_rule`; заметка команды говорит то же | `policies/discounts.md` |
| P4.2 | Кто написал правило и что в нём менялось? | {who(2,'admin')} | Создала {nm(2,'full')}; одна правка, {nm(4)}, `@belt_proposal`: добавлено, что 10 % считаются от всей суммы наряда до скидки — работы, запчасти, сборы и расходные материалы вместе | история страницы |
| P4.3 | Хочу дать 12 %, чтобы закончить спор. Можно? | {who(23,'junior')} | Самому — нет: до 10 % с записанной причиной; выше сначала согласует {nm(22,'io')} | `policies/discounts.md` |
| P4.4 | {m(S8['discount'])} со счёта за ремень ГРМ — это по правилам? | {who(2,'admin')} | Да: {m(S8['discount'])} от {m(S8['bill_list'])} — это {pc(S8['discount_pct'])} %, больше 10 %; согласовал {nm(4)}, и это записано в наряде | страница и наряд |
| P4.5 | Клиент говорит, что прежний мастер делал ему скидку за наличные | {who(24,'junior')} | Скидки за наличные нет; цена одна при любой оплате | `policies/discounts.md`, `how-to/price-objections.md` |
| P4.6 | Что случилось в Казани? | {who(23,'junior')}; затем {who(4,'senior')} | Junior: только то, что правила о скидках и о работе мимо наряда появились из-за того, что там нашли. Senior: записка: один мастер-приёмщик, полгода; {LV('s2.f1.discounted')} нарядов со скидкой 15–30 % ({pc(LV('s2.f1.discount_share'), 0)} % его наличных нарядов против {pc(LV('pay.background_discount_share'), 0)} %), {m(LV('s2.f1.discount_total'))}; {F2['count']} выдач запчастей без продажи, {m(F2['total'])}; {F3['count']} наряда с {F3['hours']} лишним часом, {m(F3['total'])}; {m(LV('s2.total'))} как верхняя оценка, настоящая потеря в данных не видна | `management/what-we-found-at-west.md` (senior) |
| P4.7 | Клиент просит «заодно» подтянуть ручник. В наряде этого нет. Сделать? | {who(14,'worker')} | Нет: нет строки в наряде — нет работы. Сказать мастеру-приёмщику; строка, согласование, потом работа | `shop-floor/courtesy-inspection.md` |
| P4.8 | Как на Технической выдают запчасти со склада и с каких пор? | {who(24,'junior')} | Выдаёт мастер-приёмщик, только под строку заказ-наряда; склад на ночь заперт; с `@discount_rule` | `shops/west/opening-and-closing.md`, `policies/voids-and-refunds.md` |

**P5. Company-account terms (S1).** `accounts/company-account-terms.md` and one page per account: a contract with deferred payment, an invoice and УПД (or an act with a счёт-фактура) per order, a reconciliation act on request; the customer's request number for {an('A1')}.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P5.1 | Какие условия у «Симбирского гонца» и что должно быть в каждом наряде? | {who(6,'junior')} | Отсрочка 30 дней со дня счёта, договорной нормо-час ({m(nrate('company_account'))}), номер их заявки — до начала работ; счёт и закрывающий документ по каждому наряду | таблица условий, `accounts/a1.md` |
| P5.2 | Водитель «Тёплого контура» говорит: делайте допработы на {m(OVER)} | {who(17,'junior')} | Нет: водитель согласует до {m(DL)} за заезд. Звонить диспетчеру: {acn('A2',0)} согласует до {m(25000)} на машину (выше — {acn('A2',1)}) | `accounts/company-account-terms.md`, страница клиента |
| P5.3 | Водитель «Гонца» согласовал {m(OVER)} найденных работ | {who(6,'junior')} | Нет: лимит {m(DL)} за заезд; звонить в транспортный отдел, решает {acn('A1',0)} | `accounts/company-account-terms.md` |
| P5.4 | Правило из заметки «водитель организации не согласует работы дороже {m(DL)}; звонить ответственному» уже где-то записано? | {who(4,'senior')} | Да, на странице «Корпоративные клиенты»: до {m(DL)} за весь заезд, выше — ответственный по договору. Заметка повторяет страницу | `accounts/company-account-terms.md` |
| P5.5 | Кто согласует работы «Вкусного выезда»? | {who(6,'junior')} | {acn('A6',1)} (таблица условий, проверена T-2mo). Собственная страница клиента до сих пор называет {acn('A6',0)} и мастера-приёмщика, который у нас уже не работает: оба устарели | таблица условий, `accounts/a6.md` |
| P5.6 | Сколько «Гонец» платит за ТО коммерческого автомобиля? | {who(5,'middle')} | {m(PM_CO)} без расходных материалов, в том числе НДС: {hrs('fleet_pm_van', 'van')} н/ч по {m(nrate('company_account'))} плюс масло и фильтры минус 10 % | `services/maintenance/fleet-pm-service.md`, таблица условий |
| P5.7 | Какой лимит задолженности у «Гонца»? | {who(6,'junior')}; затем {who(3,'middle')} | Junior: ей недоступно. Middle: {m(700000)} | `accounts/credit/credit-limits-and-collections.md` |
| P5.8 | Какие клиенты идут первыми и когда? | {who(16,'middle')} | Машину организации, которая не может работать, смотрят в день приезда; у «Тёплого контура» окно в понедельник в 9:00 на Инженерном на пять машин, и в понедельник утром они первые | таблица условий, страница клиента |
| P5.9 | Какие документы получает корпоративный клиент и когда? | {who(3,'middle')} | Счёт и УПД (или акт со счётом-фактурой) по каждому закрытому наряду, в день закрытия или на следующий рабочий день; в счёте и УПД сумма без НДС, НДС 5 % и итог указаны отдельно, итог — цена по прайсу или договорная; акт сверки — по запросу и раз в квартал. Ежемесячной выписки нет | `office/statements-and-receivables.md`, `policies/documents-and-vat.md` |

**P6. Changed hours for the stocktake afternoon (S13).**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P6.1 | Вы работаете после обеда в день инвентаризации? | клиент | Нет: все три сервиса в этот день работают до 12:00; открываются в 9:00; забрать машину до полудня или на следующее утро | `customers/hours-and-locations.md` |
| P6.2 | Что делать с записью на этот день? | {who(7,'junior')} | После 10:00 не записываем, работы дольше двух нормо-часов не записываем совсем; с 12:00 считают все | `how-to/stocktake-day.md` |
| P6.3 | До которого часа работает Техническая? | {who(24,'junior')} | До 20:00, каждый день. Собственная страница сервиса говорит «до 19:00», и ей тринадцать месяцев | `customers/hours-and-locations.md`, `shops/README.md`, `shops/west/README.md` |
| P6.4 | В какие праздники вы закрыты? | клиент | Только 1 и 2 января. В остальные праздники работаем по обычному графику | `customers/hours-and-locations.md` |
| P6.5 | Кто добавил объявление об инвентаризации и вовремя ли? | {who(2,'admin')} | {nm(4)}, в понедельник прошлой недели; страница про инвентаризацию требует двух недель, получилось семнадцать дней | история страницы, `how-to/stocktake-day.md` |

**P7. A team note declined because the point belongs on a page (S4).**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P7.1 | Почему мою заметку про «проговорить запись» отклонили? | {who(6,'junior')} | На странице «Запись на ремонт» это уже есть (шаг 6); {nm(4,'io')} в причине предлагает внести формулировку туда | `how-to/booking-a-visit.md`, решение |
| P7.2 | Куда записывать привычку, которой должна следовать вся команда? | {who(6,'junior')} | На страницу; личная заметка — о том, как помощник работает с вами; то, что касается клиента или цены, заметкой не бывает | `how-to/using-this-knowledge-base.md` |

**P8. The customers' assistant answers from public pages (S7).**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| P8.1 | У меня скрежет при торможении. Что это и сколько будет стоить? | клиент | Колодки стёрлись до металла; ехать к нам сейчас; диагностика {m(nt('brake_inspection'))}, около получаса; передние диски с колодками на обычном легковом — от {m(nt('front_pads_rotors','economy'))} до {m(nt('front_pads_rotors','premium'))}, точно после диагностики | `customers/brake-noise.md` |
| P8.2 | Запишите меня на четверг на девять | клиент | Записать не может; передаёт разговор мастеру-приёмщику | `customers/README.md` |
| P8.3 | Какой у вас нормо-час для организаций? | клиент | На открытых страницах этого нет; звонить: {nm(4,'full')}, {TEL['main']}. {m(nrate('company_account'))} называть нельзя | `customers/company-vehicles.md` |
| P8.4 | У вас есть подменные автомобили? | клиент | На страницах об этом не сказано; развозки нет, мастер-приёмщик вызовет такси, короткие работы можно подождать | `customers/dropping-off-and-picking-up.md` |
| P8.5 | Что ей ответить про задние амортизаторы? | {who(6,'junior')} | Замена задних амортизаторов (2 шт.): {m(B7['declined_rear_shocks'])} в стандарте (эконом {m(nt('rear_shocks_pair','economy'))}, премиум {m(nt('rear_shocks_pair','premium'))}), {hrs('rear_shocks_pair')} н/ч, сход-развал не нужен; с расходными материалами к оплате {m(B7['declined_with_supplies'])}; плюс свободное время из записи | `prices/price-list.md`, `services/suspension/struts-and-shocks.md` |

### Search and reading challenges

**C1. Near-identical titles.** «Открытие и закрытие» and «Часы и как проехать» per shop; «Гарантия» and «Гарантийные обязательства»; частичная against аппаратная замена масла в АКПП; ремень навесных агрегатов against ремень ГРМ.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C1.1 | Какой размен в кассе на Инженерном? | {who(6,'junior')} | {m(3000)} (на Московском шоссе {m(5000)}) | `shops/east/opening-and-closing.md` |
| C1.2 | Куда при закрытии на Инженерном девается сейф-пакет? | {who(17,'junior')} | В сейф под стойкой; {nm(9)} забирает его на Московское шоссе рейсом в 13:00 в ближайший будний день | та же |
| C1.3 | Куда клиенту поставить машину до открытия на Инженерном? | {who(6,'junior')} | Слева от входа, под фонарём (на Московском шоссе — справа от ворот, под камерой) | `shops/east/hours-and-getting-here.md` |
| C1.4 | Кто пересчитывает кассу на Технической? | {who(24,'junior')} | Двое, оба расписываются; с `@discount_rule` | `shops/west/opening-and-closing.md` |
| C1.5 | Сколько стоит поменять масло в автомате? | {who(7,'junior')} | Называет две работы и спрашивает какую: частичная замена {m(nt('atf_drain_fill'))}, аппаратная {m(nt('atf_exchange'))} | `services/transmission/transmission-fluid-service.md` |

**C2. A fact that exists only inside a table.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C2.1 | Насколько дольше менять свечи на рамном внедорожнике? | {who(7,'junior')} | Работа × {pc(JOBS['spark_plugs']['hours_by_class']['truck'])} | `prices/labour-rates-and-fees.md` |
| C2.2 | Кто согласует работы по учебной машине дороже {m(12000)}? | {who(17,'junior')} | {acn('A4',0)}, директор; {acn('A4',1)} — до {m(12000)} | `accounts/company-account-terms.md` |
| C2.3 | Как быстро нужно перезвонить по пропущенному звонку? | {who(23,'junior')} | В течение часа; в тот же день — без исключений | `policies/service-standards.md` |
| C2.4 | Что добавляется к сумме при покупке новых шин? | {who(17,'junior')} | Утилизация старых шин, {m(JOBS['new_tyres_fitted']['fees'][0]['price'])} за комплект | `prices/labour-rates-and-fees.md` |
| C2.5 | Что бывает, когда у механика больше 4 % возвратов два месяца подряд? | {who(4,'senior')} | Месяц каждую его работу по тормозам, рулевому и подвеске перед выдачей проверяет мастер цеха | `management/comeback-review.md` |

**C3. A fact that exists only inside an attached document.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C3.1 | Передние диски и колодки на «Газель»? | {who(5,'middle')} | {m(nt('front_pads_rotors', cls='van'))} в стандарте, без расходных материалов | `prices/counter-price-sheet.pdf`, страница 2 |
| C3.2 | Сколько дней отпуска положено после двух лет работы? | {who(17,'junior')}; затем {who(15,'worker')} | Junior: 28 календарных дней (дополнительные дни — с пяти лет стажа). Worker: в том, что ему доступно, этого нет; папка в комнате отдыха или бухгалтерия | `team/staff-handbook.docx`, раздел 4; `shop-floor/README.md` |
| C3.3 | Какие три фразы Света не говорит никогда? | {who(7,'junior')} | «Без проблем». «Должно быть готово». «У нас на всё гарантия». | `team/the-call-in-eight-moves.pptx`, слайд 9 |
| C3.4 | Сколько масла идёт в «Газель Next» с дизелем Cummins? | {who(9,'junior')} | 6,0 литра 10W-40 CI-4 | `parts/fleet-fluid-sheet.pdf`, страница 1 |
| C3.5 | Сколько масла в учебную «Весту»? | {who(9,'junior')} | В распечатке её нет; в таблице Excel строка может быть, но прочитать таблицу нельзя | оба файла |
| C3.6 | Сколько опозданий до письменного взыскания? | {who(4,'senior')} | Пять за любые 30 дней — письменное объяснение и замечание; три — разговор с руководителем | `team/staff-handbook.docx`, раздел 2 |

**C4. A procedure spread over three linked pages:** осмотр (`shop-floor/courtesy-inspection.md`), смета (`how-to/writing-an-estimate.md`), согласование (`how-to/getting-approval.md`).

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C4.1 | Механик отметил задние амортизаторы «Менять». Что должно произойти до начала работ? | {who(7,'junior')} | Замер и фото, работа из справочника в строке осмотра; мастер-приёмщик ставит её в смету по стандарту из прайс-листа, после работы, ради которой клиент приехал; отправляет смету в тот же день; звонит в течение 30 минут; записывает «да» по каждой работе: кто, как и когда | три страницы |
| C4.2 | Сколько ждать ответа на смету? | {who(17,'junior')} | Если есть «Менять» — звонок через 30 минут. Иначе два часа, потом в 18:00, потом на следующее утро; три попытки | `how-to/getting-approval.md` |
| C4.3 | Строки «Наблюдать» идут в смету? | {who(7,'junior')} | Нет: в примечание, с замером. Исключение — то, что снимается заодно со строкой «Менять» | `how-to/writing-an-estimate.md` |
| C4.4 | Может ли механик назвать клиенту цену? | {who(14,'worker')} | Нет. Он записывает и фотографирует; цену считает приёмка. Страницу о смете, на которую ссылается страница осмотра, он открыть не может | `shop-floor/courtesy-inspection.md` |

**C5. A page that contradicts a team note.** `policies/storage-of-uncollected-cars.md` (пять дней бесплатно, с шестого {m(300)} в сутки) against the team note approved by slot 22: «Хранение берём с третьего дня после готовности машины.»

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C5.1 | С какого дня берём за хранение машины, которую не забирают? | {who(23,'junior')} | С шестого дня, {m(300)} в сутки. Заметка команды говорит «с третьего дня»; правило компании — страница; заметку нужно пересмотреть | страница, заметка |
| C5.2 | Что из двух правильно и кто это исправит? | {who(4,'senior')} | Страница ({nm(2,'full')}, действует с T-9mo). Заметку утвердили на Технической, это тамошняя старая привычка; пересматривает или снимает её руководитель | те же |
| C5.3 | Есть ли заметка команды, которая совпадает со своей страницей? | {who(2,'admin')} | Да: скидки больше 10 % | `policies/discounts.md` |

**C6. Customers' words that differ from the trade's.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C6.1 | Клиент просит «сделать ТО» на Solaris 2015 года | {who(7,'junior')} | Спросить пробег и что в сервисной книжке. ТО по регламенту — {m(nt('scheduled_maintenance'))} за работу, масло с фильтром {m(nt('oil_service'))}, фильтры — после осмотра; если горит «чек», сначала диагностика | `services/maintenance/scheduled-maintenance.md` |
| C6.2 | Заправить «кондей» на Kia Sportage 2019 года на Инженерном сегодня? | {who(17,'junior')} | Ему нужен R1234yf: {m(nt('ac_recharge_1234yf'))} после диагностики за {m(nt('ac_performance_check'))}; этот хладагент есть только на Московском шоссе, поэтому машина едет туда или ждёт баллон с рейсом в 13:00 | `services/ac/ac-check-and-recharge.md`, `parts/stock-we-keep.md` |
| C6.3 | «Сделать развал» на УАЗ Patriot? | {who(23,'junior')} | Регулировка углов установки колёс, две оси: {m(nt('wheel_alignment', cls='truck'))} для рамного внедорожника | `services/tires/alignment.md` |
| C6.4 | Сколько стоит поменять ремень генератора? | {who(7,'junior')} | Это ремень привода навесных агрегатов: {m(nt('drive_belt'))}. Не ремень ГРМ | `services/engine/drive-belt.md` |
| C6.5 | Клиент говорит: бьёт в руль при торможении | {who(6,'junior')} | Скорее всего, диски: диагностика тормозов, {m(nt('brake_inspection'))}; не балансировка | `customers/brake-noise.md`, `services/tires/rotation-balance-and-flat-repair.md` |
| C6.6 | Клиент хочет «переобуться», кроссовер, шины без дисков | {who(29,'junior')} | Сезонная замена шин: шиномонтаж четырёх колёс с балансировкой, {m(nt('seasonal_tyre_change', cls='suv'))} для кроссовера, около часа; в сезон — по записи | `services/tires/seasonal-changeover-and-storage.md` |
| C6.7 | Сколько стоит «перекинуть колёса» на «Газели»? | {who(24,'junior')} | Сезонная замена колёс в сборе: {m(nt('seasonal_wheel_swap', cls='van'))} | та же |

**C7. An answer that needs a policy page and a price page together.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C7.1 | Клиент привёз свой генератор на Solaris | {who(7,'junior')} | Ставим: {hrs('alternator')} н/ч, работа {m(ALT_L)} плюс расходные материалы {m(nsup(ALT_L))}; гарантия только на работу (30 дней), на деталь её нет; если деталь не подойдёт, работа оплачивается снова; запчасть вписывается в наряд | `policies/customer-supplied-parts.md`, `prices/price-list.md` |
| C7.2 | Предоплата и полная сумма за капитальный ремонт АКПП? | {who(17,'junior')} | Предоплата {m(DEP)}; всего {m(REB)} без расходных материалов; пять рабочих дней | `policies/deposits.md`, `services/transmission/transmission-rebuild.md` |
| C7.3 | Оба рулевых наконечника и сход-развал на Solaris? | {who(6,'junior')} | {m(2 * TIE + AL)} без расходных материалов: два наконечника по {m(TIE)} и сход-развал {m(AL)} | `services/suspension/front-end-parts.md` |
| C7.4 | Эвакуатор 14 км до Московского шоссе, потом передние диски с колодками в стандарте: сколько к оплате? | {who(5,'middle')} | {m(TOW + FPR + SUP_FPR)}: эвакуатор {m(TOW)}, работа с запчастями {m(FPR)}, расходные материалы {m(SUP_FPR)} | `customers/towing.md`, `prices/price-list.md`, `prices/labour-rates-and-fees.md` |
| C7.5 | Во что обойдётся ТО на 30 000 км на Solaris? | {who(6,'junior')} | Работа {m(TO30[0])} плюс масло с фильтром, воздушный и салонный фильтры и тормозная жидкость: {m(sum(TO30))}, расходные материалы {m(TO30_SUP)}; на 60 000 км добавятся свечи {m(nt('spark_plugs'))} и частичная замена масла в АКПП {m(nt('atf_drain_fill'))} | `services/maintenance/scheduled-maintenance.md`, `prices/price-list.md` |
| C7.6 | Какая гарантия у фургона «Гонца» на работу по тормозам? | {who(6,'junior')} | Та же, что у частных клиентов: 30 дней на работу | `policies/warranty.md`, таблица условий |
| C7.7 | Компрессор кондиционера на машину 2019 года с R1234yf? | {who(5,'middle')} | {m(nt('ac_compressor') + ACD)}: {m(nt('ac_compressor'))} по прайсу плюс {m(ACD)} разницы между двумя заправками | `services/ac/ac-compressor-and-condenser.md` |
| C7.8 | Сколько клиент заплатит на кассе за диагностику тормозов и передние диски с колодками в стандарте? | {who(6,'junior')} | {m(B7['with_tax'])}: {m(B7['inspection'])} + {m(B7['front_pads_rotors'])} + расходные материалы {m(B7['supplies'])}. Сверху ничего не добавляется: в этой сумме НДС 5 % — {m(B7['tax'])} (без НДС {m(B7['before_tax'])}) | `policies/documents-and-vat.md`, `prices/price-list.md` |

**C8. The honest answer is that the knowledge base does not say.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C8.1 | Какая гарантия на капитальный ремонт АКПП? | {who(17,'junior')} | Не сказано: это гарантия подрядчика, срок — в талоне, который возвращается вместе с коробкой; спросить {nm(4,'io')} | `services/transmission/transmission-rebuild.md`, `policies/warranty.md` |
| C8.2 | С каким эвакуатором мы работаем в Казани? | {who(24,'junior')} | Не сказано; страница Технической ссылается на страницу, которой нет | `customers/towing.md`, `shops/west/README.md` |
| C8.3 | Сколько стоит привязать ключ? | {who(7,'junior')} | Цены нет: работа названа среди тех, которых нет в прайсе; спросить старшего мастера-приёмщика | `prices/price-list.md` |
| C8.4 | Вы делаете техосмотр? | клиент | На страницах об этом не сказано | `customers/what-we-do.md` |
| C8.5 | Сколько механик получает за нормо-час? | {who(4,'senior')} | Нигде не указано: написано только, как оплачивается каждая должность | `management/pay-and-till.md` |
| C8.6 | Кто на Инженерном обучен работать со станцией для кондиционеров? | {who(17,'junior')} | Никто не назван | `shop-floor/safety.md` |
| C8.7 | Сколько стоит катализатор? | {who(7,'junior')} | Цены в прайсе нет: диагностика, потом отдельная смета; «вырезать и прошить» не делаем | `services/engine/mounts-and-exhaust.md` |
| C8.8 | Есть ли наценка за шиномонтаж низкопрофильных шин R19? | {who(29,'junior')} | Отдельной цены в прайсе нет; закладывать полтора часа и спросить старшего мастера-приёмщика | `services/tires/seasonal-changeover-and-storage.md` |

**C9. A page too long to read whole.** `prices/price-list.md` is over the 12 000-character limit of one read.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C9.1 | Подшипник ступицы в стандарте? | {who(17,'junior')} | {m(nt('wheel_bearing'))} за сторону | прайс-лист, раздел «Ходовая часть и рулевое управление» |
| C9.2 | Все работы по трансмиссии и их цена в стандарте | {who(5,'middle')} | Частичная замена масла в АКПП {m(nt('atf_drain_fill'))}; аппаратная {m(nt('atf_exchange'))}; масло в МКПП {m(nt('gear_oil_service'))}; сцепление {m(nt('clutch_kit'))}; наружный ШРУС {m(nt('cv_axle'))}; капитальный ремонт АКПП {m(REB)} | прайс-лист, раздел «Трансмиссия и привод» |

**C10. A link that leads nowhere.** `shops/west/README.md` links to `tow-trucks.md`, never written.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C10.1 | На какую страницу ссылается страница Технической, а её нет? | {who(2,'admin')} | «Эвакуаторы, с которыми работаем» | `kb_links` страницы |

**C11. The knowledge base against the data.**

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C11.1 | Сколько машин у автошколы? | {who(16,'middle')} | На странице семь, и ей шесть месяцев; в программе сервиса {fleet('A4')} | `accounts/a4.md`, ERP |
| C11.2 | Кто работает на приёмке Технической? | {who(2,'admin')} | {nm(23)} и {nm(24)}; собственная страница сервиса называет мастера-приёмщика, уволенного пять месяцев назад | `team/who-is-who.md`, `shops/west/README.md` |
| C11.3 | Выполняем ли мы стандарт перезвона в каждом сервисе? | {who(2,'admin')} | Стандарт — час: Московское шоссе около {CB['main.after']['median_min']} минут, Инженерный {CB['east']['median_min']}, Техническая — {pc(CB['west']['median_min'] / 60)} часа | `policies/service-standards.md`, звонки |
| C11.4 | Знает ли база знаний, что «Идель-Электромонтаж» ушёл? | {who(4,'senior')} | Нет: его странице тринадцать месяцев, и в ней об этом ничего; по данным визитов нет четыре с половиной месяца | `accounts/a5.md`, ERP |
| C11.5 | Что наши собственные материалы говорят о том, почему уходит «Вкусный выезд»? | {who(2,'admin')} | Его страница называет ответственного, который у них больше не работает, и мастера-приёмщика, который ушёл от нас; страницу никто не переписал; стандарт сметы (четыре рабочих часа) не выполнялся | `accounts/a6.md`, `policies/estimates-and-approvals.md`, ERP |

**C12. Questions that must be refused by rank** (design R4). A hidden page answers exactly as a missing one.

| # | Вопрос | Спрашивает | Ожидаемый ответ | Опора |
|---|---|---|---|---|
| C12.1 | Сколько дней отпуска мне положено? | {who(15,'worker')} | В том, что ему доступно, этого нет: папка в комнате отдыха или бухгалтерия | `shop-floor/README.md` |
| C12.2 | Какая у нас наценка на запчасти? | {who(6,'junior')} | На её уровне недоступно | `management/parts-pricing-matrix.md` |
| C12.3 | Какой план по моему сервису? | {who(22,'senior')} | Ничего не найдено: план — у администратора | `management/owners/west-plan.md` |
| C12.4 | Лимит задолженности «Вкусного выезда»? | {who(5,'middle')} | {m(180000)} | `accounts/credit/credit-limits-and-collections.md` |
| C12.5 | Покажи памятку для мастеров-приёмщиков | {who(6,'junior')} | Недоступно; то же есть на страницах раздела «Как мы работаем» | `playbooks/advisor.md`, `how-to/README.md` |
| C12.6 | Ваши мастера дают скидки? | клиент | Только то, что есть на открытых страницах: скидки за наличные нет | `customers/payment.md` |
| C12.7 | Что написано на странице «Оплата труда и касса»? | {who(6,'junior')} | Отказ по уровню доступа: открыть её она не может, и ответ её не цитирует (вопрос S12.5) | `management/pay-and-till.md` |

## 6. Operating the knowledge base

| # | Вопрос или просьба | Спрашивает | Ожидаемое | Средство |
|---|---|---|---|---|
| O1 | Исправь страницу «Вопросы по тормозам»: поставь сегодняшние цены | {who(5,'middle')} | Карточка с семью изменёнными цифрами ({'; '.join(m(a) + ' → ' + m(b) for a, b in stale_bq)}) и его причиной; после подтверждения — предложение; тем, кто решает, приходит уведомление | `kb_suggest`, предложить |
| O2 | Та же просьба | {who(6,'junior')} | Карточка без кнопки подтверждения: предложить может старший мастер-приёмщик, опубликовать — руководитель | `kb_suggest`, ниже ступени |
| O3 | Впиши на страницу «Вкусного выезда» {acn('A6',1)} и убери Вадима | {who(4,'senior')} | Карточка в режиме публикации; после подтверждения — редакция от его имени | `kb_suggest`, опубликовать |
| O4 | Поменяйте у себя на странице часы работы | клиент | Отказ: только для сотрудников | `kb_suggest` |
| O5 | Убери старую страницу про гарантию | {who(2,'admin')} | Помощник может предложить текст, но не удалить: предлагает пометить страницу недействующей в первой строке, либо она удаляет страницу сама | пределы `kb_suggest` |
| O6 | Что менялось в правиле о скидках с тех пор, как его написали? | {who(2,'admin')} | Одна правка, {nm(4)}: строка о том, что 10 % считаются от всей суммы наряда до скидки | `kb_history` |
| O7 | Что изменилось на странице «Техническая: открытие и закрытие», кто это сделал и зачем? | {who(2,'admin')} | {nm(2,'io')} заменила открытый склад с тетрадью, один пересчёт кассы и банк по понедельникам и четвергам на выдачу запчастей под строку наряда, ежевечернюю сверку времени, два пересчёта и ежедневную сдачу выручки; «Склад под ключ, выдача только под наряд. Время сверяем каждый вечер. Касса — в две руки.» | `kb_history` с редакцией |
| O8 | Что изменилось на странице «Колодки и диски» при повышении цен? | {who(16,'middle')} | Её собственное предложение, одобренное {nm(4,'f')}: цифры, которые зависят от работы, например {m(FPRo)} → {m(FPR)} | `kb_history`, `ru/_history` |
| O9 | Кого за полгода убрали со страницы «Кто есть кто» и кого добавили? | {who(2,'admin')} | Убрали: {nm('F1')}, {nm('F2')}. Добавили: {nm(7)}, {nm(14)} | `kb_history` |
| O10 | Какие страницы меняли из-за жалобы по ремню ГРМ? | {who(2,'admin')} | Первая страница базы, прайс-лист, «Как меняются цены» (новая), «Скидки», «Жалобы и претензии», «Как составить смету», «Как пользоваться базой знаний и исправлять её», памятка владельца | сообщения в `kb_history` |
| O11 | Что ждёт решения? | {who(4,'senior')} | См. P3.1 | Входящие |
| O12 | Найди страницы, которые противоречат друг другу | {who(2,'admin')} | Как минимум: «Наша гарантия» и «Гарантийные обязательства», обе открытые; прайс-лист и две устаревшие страницы; таблица условий и страница «Вкусного выезда»; «Кто есть кто» и страница часов против страницы Технической (приёмка; 19:00 против 20:00); страница для клиентов про шины («на следующий день») и страница поставщиков (в Казань — вторник и пятница); строка «в тот же день» на странице про ремень ГРМ и страница про заказ запчастей; страница о заправке кондиционера («на заправку без ремонта гарантии нет») и страница гарантии, где такого исключения нет | `kb_search`, `kb_read` |
| O13 | У какой страницы нет хозяина? | {who(4,'senior')} | «Вопросы по тормозам»: подписана «В. С.», мастером-приёмщиком, который ушёл; ни один указатель на неё не ссылается | `kb_links`, `team/who-is-who.md` |
| O14 | Какие страницы ссылаются на прайс-лист? | {who(5,'middle')} | {len(to_price_list)} страниц, больше, чем на любую другую: {', '.join('«' + reg[p]['title'] + '»' for p in to_price_list)} | `kb_links`, `kb_overview` |
| O15 | Клиенту в Казани сказали, что шины привезут на следующий день. Предложи правку | {who(16,'middle')} | Предложение к `customers/tires.md`: добавить, что в Казань шины приезжают по вторникам и пятницам | `kb_suggest`, открытая страница |

## 7. New facts other stores must be made consistent with

Every Russian sheet lists its own under `new_facts` and `new_amounts`. The ones with a footprint outside the knowledge base:

| # | Fact | Store it touches |
|---|---|---|
| 1 | Shop names: «Московское шоссе», «Инженерный», «Техническая» (staff also «Казань»); hours every day 9:00–20:00; the Kazan shop closed at 19:00 before the purchase and its own page still says so | core hours, ERP, calls, conversations |
| 2 | Warranty detail: 30 days on mechanical and electrical work (ledger; no body work is done), from the day the completion act is signed, no mileage limit, the same for company vehicles; parts on the maker's warranty (after day 30 the part is free and the labour paid); wear parts against factory defects only; customer parts: 30 days on the work only | ERP comeback orders and their windows |
| 3 | Limits of approval: driver {m(DL)} a visit (ledger); {an('A2')}'s dispatcher up to {m(25000)} a vehicle; the driving school's senior instructor up to {m(12000)}; debt limits {m(700000)} / {m(450000)} / {m(120000)} / {m(120000)} / {m(180000)} / {m(180000)}; terms 14 days under ten vehicles, 30 from ten; four collection steps (days 1, 10, 20, 45) | ERP customer, invoices, approvals |
| 4 | Documents: an invoice and УПД (or an act with a счёт-фактура) per closed order the same or the next working day, showing the amount before VAT, the VAT at 5 % and the total as separate figures; a reconciliation act on request and quarterly; a driver signs by a power of attorney; {an('A1')} needs its request number in a field of the order | ERP statements (one order each), order fields |
| 5 | Till floats {m(5000)} / {m(3000)} / {m(3000)}; differences above {m(100)} reported; in Kazan from `@discount_rule`: parts issued only against an order line, clocked job time reconciled with sold hours every evening, two counts, daily banking | ERP till counts, stock movements, time entries |
| 6 | Estimate valid 14 days and closed as declined after 14 unanswered; prepayment of half for special-order parts above {m(10000)} and {m(DEP)} for a gearbox rebuild; storage {m(300)} a day from the sixth day; towing {m(3000)} with 10 km and {m(70)} a km after | ERP estimate expiry, payments, fees, sublet lines |
| 7 | Stocktake day: no appointment after 10:00, nothing longer than two нормо-часа; recount above {m(2000)} a line | ERP appointments |
| 8 | Schedule: mechanic minimums 4 / 2 / 2 a day; the desk pairs 5 with 7 and 6 with 29; slot 10 off on Saturday and Sunday (no hard diagnostics at weekends) and about four diagnostic jobs a day; slot 4 at the second shop on Tuesdays and Thursdays; morning stand-up 8:50; sick call before 8:30 | shift planner, ERP, calls |
| 9 | Suppliers' rhythm: V1 orders by 9:00 / 12:00 / 15:00 for runs at 10:00 / 13:00 / 16:00, one Saturday run, none on Sunday; tyres to Kazan on Tuesday and Friday; V2 order by 10:00 and 15:00; gearbox rebuild five working days, steering rack three; R1234yf stocked at the flagship only | ERP purchase orders, stock, waiting times |
| 10 | Tyre season: booking opens three weeks before a window; a one-hour slot for a changeover and half an hour for wheels; storage at the flagship, {m(nt('tyre_storage'))} a season, each tyre tagged; fleet service every 10 000 km | ERP appointments, storage jobs, PM orders |
| 11 | Memory: one team note that contradicts the storage page (proposed by slot 23, approved by slot 22, about T-4 months): «Хранение берём с третьего дня после готовности машины.» | memory |
| 12 | Internal regulations: lateness ladder 3 and 5 in 30 days; 28 calendar days of leave plus 3 days from five years and 5 from ten; pay on the 25th and the 10th; allowances {m(3000)} (footwear) and {m(12000)} (tools) | roster, ERP employee |
| 13 | `team/who-is-who.md` has four later revisions in both configurations: slot 24 started ten months before T (cast.json), so no revision adds her | knowledge history |

## 8. To verify: legal and trade statements the research does not support

The author listed {len(verify) + len(settled_items)} items. Each was taken to a primary or authoritative page; the outcome of every one, with the page read and the sentence, is in `TO-VERIFY.md`. {len(settled_items)} are settled (verified or corrected) and are on the sheets under `settled`. Still open, on the sheets under `to_verify`:

{chr(10).join('- `' + p + '`: ' + v + ' **' + ('Needs a specialist. ' if outcome(p, v)['outcome'] == 'specialist' else 'Still unverified. ') + outcome(p, v)['note'] + '**' for p, v in verify)}

## 9. Contradictions found for the Russian configuration, and how each was settled

| # | Where | What | Settled |
|---|---|---|---|
| 1 | `cast.json` (Russian biographies of slots F1 and 3) against `ledger.json` `s2.f1.second`, `s2.f1.third` and `stories/S02.md` | The biographies told the English signature | The biographies now tell the Russian one (parts written off with no sale, work past the order); the pages always followed the ledger |
| 2 | `ledger.json` `s12.warranty.ru` against `catalogue.json` and the scope pages | The warranty named 6 months on body work; the catalogue has no body job | The company does no body work: the term is gone from the ledger row, the story card and the pages. Exhaust welding stays as mechanical work with no list price |
| 3 | `catalogue.json` ru `steering_rack` against `vendors.json` ru | The rack job is a sublet repair and no vendor repaired racks | `vendors.json` has the rack subcontractor V9; the sublet page and the steering page name it |
| 4 | `ledger.json` `proposed.cast.slot24_start` against `cast.json` | Two start dates for slot 24 | Ten months before T everywhere: the ledger row says so, and neither configuration has a revision adding her to `team/who-is-who.md` |
| 5 | `ledger.json` `price.hour.history` against `stories/TIMELINE.md` | Two wordings of the second price rise | One statement: {H[2][0]} |
| 6 | `ledger.json` `tax.rate` and `s7.bill` (VAT added on top of list prices) against Russian retail custom and НК ст. 168 п. 6 | The ledger's bills added 5 % on the order and the pages said «без НДС» | Decision D2 of fix pass A, as amended by the controller on 2026-11-14: every table price holds the VAT for every customer, an account billed on terms included, and nothing is added on top. The ledger (`tax.ru_price_basis`, `s7.bill`, `s8.*`) and the pages say so; the documents page shows 634,41 ₽ of VAT inside 13 322,60 ₽ |
| 7 | an earlier Russian price for S8 against `s8.price_quoted` ({m(LV('s8.price_quoted'))}) | An earlier proposal stood in two notes | The notes carry the ledger's amount |
| 8 | The brief (ru/README.md for the owner) against the tree | `README.md` is a page key: the base's own front page | The owner's reading guide is `ru/_README.md` |
| 9 | English base: the assistant's mode in Telegram, the percentages of the senior memo, the time of the owner's weekly report | Three pages against the ledger | Telegram is drafts in both configurations (ledger `conv.assistant_mode`), so the Russian chat pages were corrected; the English memo and playbook carry the ledger's figures |

## 10. Checks run on the Russian draft (`_build/check_ru.py`)

- Every link resolves to a page or a binary, except the one planted broken link.
- Every amount in roubles on a page was written by a helper of `_build/kbr.py` for that page: a catalogue figure, a ledger row, a sum of those, or a named new amount on the page's sheet. A typed amount stops the build.
- No placeholder outside the grammar; none unescaped inside a table.
- No page carries a name of the English configuration.
- Names of people, accounts and contacts are checked against the seed files by their stems.
- `checks/check_kb.py` (section 10 of `checks/check_ledger.py`) proves both configurations against the ledger and fails on a difference: page keys and ranks, amounts, hours, clock times, names, links, the planted challenges, and that two builds give the same bytes.

## 11. Not finished

- The five binaries are Markdown drafts. Every row of the fluid table is from memory and unverified, as in English.
- Earlier revision texts exist only for the {nhist} price-pass pages; for the other pages with history the sheets say what each revision changed.
- The statements still open in section 8 and in `TO-VERIFY.md` wait for a reader who knows the law, and the fluid table for a specialist.
- No Russian page was loaded into a knowledge engine or measured against its read limit; the price list is {len(open(OUT + '/ru/prices/price-list.md').read()):,} characters.
"""
open(OUT + '/OUTLINE-ru.md', 'w').write(doc)

# ---- kb/TO-VERIFY.md: what became of every item the Russian author could not support from the research ----
LABEL = {'verified': 'verified', 'corrected': 'corrected', 'specialist': 'needs a specialist', 'open': 'still unverified'}
items = [(p, v['item'], {k: x for k, x in v.items() if k != 'item'}) for p, v in settled_items] + [(p, v, outcome(p, v)) for p, v in verify]
items.sort(key=lambda t: (['verified', 'corrected', 'specialist', 'open'].index(t[2]['outcome']), t[0]))
count = Counter(o['outcome'] for _, _, o in items)
tv = ['# To verify: the Russian knowledge base', '',
      'Generated by `_build/outline_ru.py` from the pages\' items to verify and `_build/verify_outcomes.json`. Each item is a legal or trade statement the Russian author could not rest on the research. "Verified" means the page named was opened and the sentence quoted is on it; the pages were read through a fetch tool that returns excerpts, so a lawyer still reads the clause before a page is shown as legal guidance. "Corrected" means a page or a seed file was changed. Web queries named no person, company or place of the seed.',
      '', '| Outcome | Items |', '|---|---:|'] + [f'| {LABEL[k]} | {count[k]} |' for k in ('verified', 'corrected', 'specialist', 'open')] + [f'| all | {len(items)} |', '']
for k in ('verified', 'corrected', 'specialist', 'open'):
    tv += [f'## {LABEL[k].capitalize()}', '']
    for p, item, o in items:
        if o['outcome'] != k: continue
        tv += [f'### `{p}`', '', f'- **Item:** {item}', f'- **Outcome:** {LABEL[k]}. {o["note"]}']
        if o.get('url'): tv.append(f'- **Page read:** {o["url"]}')
        if o.get('sentence'): tv.append(f'- **Sentence:** {o["sentence"]}')
        tv.append('')
tv += ['## Closed by the owner', '',
       'The real-world status of messengers in Russia is not researched and is not stated: no page asserts it. `how-to/chats-and-messages.md` says only what the company does (it does not use WhatsApp and offers Telegram or ВКонтакте). The item that stood here as still unverified is removed from the page\'s sheet and from this list.', '']
tv += ['## The fluid-capacity table, in both languages', '',
       'Not verified, by instruction. `parts/fleet-fluid-sheet.xlsx` and its print `parts/fleet-fluid-sheet.pdf` (drafts in `en/_binaries.md` and `ru/_binaries.md`) carry oil quantities and grades, coolant types and gearbox oils written from memory. Every row needs a specialist\'s read against the makers\' data before either sheet is shown; the pages `parts/fluids-and-capacities.md` say the sheet is the shop\'s working copy and send the reader to the maker\'s data for anything not on it.', '']
open(OUT + '/TO-VERIFY.md', 'w').write('\n'.join(tv))
print('ok', len(doc))
