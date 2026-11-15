# -*- coding: utf-8 -*-
"""Checks of the Russian configuration: links, files, amounts, placeholders, leftovers of the English configuration, counts.
Run by build.py after the Russian batches; prints findings, asserts only what must never happen."""
import json, re, os, glob, posixpath
from collections import Counter
os.environ['KB_CFG'] = 'ru'
import kbb
OUT = kbb.OUT
reg_all = json.load(open(kbb.REG))
reg = {p: r for p, r in reg_all.items() if not r.get('not_a_page')}
en = json.load(open(kbb.HERE + '/registry.json'))
paths = set(reg)
order = ['public', 'staff', 'middle', 'senior', 'administrator']
bad, above = [], []
for p, r in reg.items():
    for l in r['links_to']:
        if l not in paths:
            if l not in r['broken_links_on_purpose']: bad.append((p, l))
        elif order.index(reg[l]['visibility']) > order.index(r['visibility']):
            above.append((p, l))
print('RU BROKEN LINKS', bad)
print('RU LINKS TO A HIGHER RANK', len(above))
for p in paths:
    if p.endswith('.md'):
        assert os.path.exists(f'{OUT}/ru/{p}'), p
        assert os.path.exists(f'{OUT}/facts-ru/{p[:-3]}.json'), p
    else:
        assert os.path.exists(f'{OUT}/facts-ru/{p}.json'), p
    if reg[p].get('first_revision_text'):
        assert os.path.exists(f'{OUT}/{reg[p]["first_revision_text"]}'), 'no history text for ' + p
md = [m for m in glob.glob(f'{OUT}/ru/**/*.md', recursive=True) if '/_history/' not in m]
rel = lambda m: os.path.relpath(m, f'{OUT}/ru')
print('RU FILES NOT IN REGISTRY', [rel(m) for m in md if rel(m) not in paths and not posixpath.basename(m).startswith('_')])
hist = glob.glob(f'{OUT}/ru/_history/**/*.md', recursive=True)
want_hist = {r['first_revision_text'] for r in reg.values() if r.get('first_revision_text')}
print('RU HISTORY FILES', len(hist), 'expected', len(want_hist), 'stray', sorted(set(os.path.relpath(h, OUT) for h in hist) - want_hist))
# amounts: every amount of money on a page was written by a helper of kbr.py for that page
MONEY = re.compile(r'(?<![\d,])(\d{1,3}(?: \d{3})*(?:,\d{2})?) ₽')
unknown = {}
for m in md:
    if posixpath.basename(m) == '_README.md': continue
    ok = set(reg_all.get(rel(m), {}).get('amounts', []))
    txt = open(m).read()
    for a in MONEY.findall(txt):
        v = float(a.replace(' ', '').replace(',', '.'))
        if v not in ok: unknown.setdefault(rel(m), set()).add(a)
    for a in re.findall(r'\d[\d ]*\s*(?:руб|р\.)', txt): unknown.setdefault(rel(m), set()).add('NOT ₽: ' + a)
    if '$' in txt or 'USD' in txt: unknown.setdefault(rel(m), set()).add('dollar sign')
print('RU AMOUNTS NOT WRITTEN BY A HELPER')
for k, v in sorted(unknown.items()): print('  ', k, sorted(v))
assert not unknown and not bad
# placeholders
EVENTS = {'warranty_2424', 'purchase', 'leak_start', 'golive', 'money_found', 'f1_fired', 'discount_rule', 'price_rise', 'f2_fired', 'newcomers', 'diag_back', 'early_desk',
          'supplier_due', 'note_declined', 'belt_proposal', 'stocktake_notice', 'stocktake', 'price_rise_1', 'price_rise_2'}
PH = re.compile(r'\{\{([^}]*)\}\}')
WHEN = re.compile(r'^(?:@([a-z_0-9]+)(?:\+\d+(?:wd:[a-z]+|w|mo))?|T[+-]\d+(?:\.\d+)?(?:mo|y))$')
ph = Counter(); wrong = []
for m in md + hist:
    for i, line in enumerate(open(m).read().split('\n')):
        for inner in PH.findall(line):
            parts = re.split(r'\\?\|', inner)
            mt = WHEN.match(parts[0]) if len(parts) == 2 else None
            if not mt or parts[1] not in ('date', 'day', 'month', 'season') or (mt.group(1) and mt.group(1) not in EVENTS):
                wrong.append((os.path.relpath(m, OUT), i + 1, inner))
            elif line.startswith('|') and '\\|' not in inner:
                wrong.append((os.path.relpath(m, OUT), i + 1, 'bar not escaped in a table: ' + inner))
            else: ph[(parts[0], parts[1])] += 1
print('RU PLACEHOLDERS OUTSIDE THE GRAMMAR', wrong)
assert not wrong
# leftovers of the English configuration
LEFT = re.compile(r'Brennan|Chattanooga|Nashville|East Main|Bonny Oaks|Charlotte Pike|Nickajack|Millsaps|Sourwood|Tennessee|\bmiles?\b|quart')
left = [(rel(m), LEFT.findall(open(m).read())[:3]) for m in md if LEFT.search(open(m).read())]
print('RU PAGES WITH ENGLISH-CONFIGURATION WORDS', left)
# counts
mdp = [p for p in paths if p.endswith('.md')]
print('ru pages', len(mdp), 'binaries', len(paths) - len(mdp))
print('only in ru', sorted(p for p in paths if p not in en), '| only in en', sorted(p for p in en if p not in paths))
print('by visibility', Counter(reg[p]['visibility'] for p in mdp))
print('with history', sum(1 for p in mdp if reg[p]['has_history']), 'stale', [p for p in mdp if reg[p]['stale_on_purpose']])
print('visibility differs from en', [(p, reg[p]['visibility'], en[p]['visibility']) for p in paths if p in en and reg[p]['visibility'] != en[p]['visibility']])
print('revision count differs from en', [(p, reg[p]['n_rev'], en[p]['n_rev']) for p in paths if p in en and reg[p]['n_rev'] != en[p]['n_rev']])
print('length', Counter(reg[p]['length_class'] for p in mdp))
print('new facts', sum(reg[p]['n_new'] for p in paths), 'to verify', sum(reg[p]['n_verify'] for p in paths))
print('words', sum(json.load(open(f'{OUT}/facts-ru/{p[:-3]}.json'))['words_ru'] for p in mdp))
print(sorted(ph.items()))
