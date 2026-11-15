"""Checks of the English configuration run by build.py: links, files, placeholders; then counts for the outline.
A finding stops the build."""
import json, re, os, glob, posixpath
import kbb
OUT = kbb.OUT
reg = json.load(open(kbb.REG))
paths = set(reg)
# 1 links
bad = []
above = []
order = ['public', 'staff', 'middle', 'senior', 'administrator']
def eff_vis(p): return reg[p]['visibility']
for p, r in reg.items():
    for l in r['links_to']:
        if l not in paths:
            if l not in r['broken_links_on_purpose']: bad.append((p, l))
        elif order.index(eff_vis(l)) > order.index(eff_vis(p)):
            above.append((p, eff_vis(p), l, eff_vis(l)))
print('BROKEN LINKS', bad)
assert not bad, 'a link leads nowhere and is not the planted one'
print('LINKS TO A HIGHER RANK', len(above))
for a in above: print('  ', a)
# 2 files present
for p in paths:
    if p.endswith('.md'):
        assert os.path.exists(f'{OUT}/en/{p}'), p
        assert os.path.exists(f'{OUT}/facts/{p[:-3]}.json'), p
    else:
        assert os.path.exists(f'{OUT}/facts/{p}.json'), p
md = [m for m in glob.glob(f'{OUT}/en/**/*.md', recursive=True) if '/_history/' not in m]
extra = [m for m in md if os.path.relpath(m, f'{OUT}/en') not in paths and not m.endswith('_binaries.md')]
print('EN FILES NOT IN REGISTRY', extra)
assert not extra, 'a page file no batch wrote'
# 3 amounts of money, labour hours, clock times and names are proved against the catalogue and the ledger by
#   checks/check_kb.py (section 10 of checks/check_ledger.py): one list of what a page may state, in the ledger
# 4 placeholders with a bar inside table rows
for m in md:
    for i, line in enumerate(open(m).read().split('\n')):
        if line.startswith('|') and re.search(r'\{\{[^}]*[^\\]\|[^}]*\}\}', line):
            raise AssertionError('placeholder bar not escaped in a table: %s line %d' % (os.path.relpath(m, f'{OUT}/en'), i + 1))
# 5 counts
from collections import Counter
mdp = [p for p in paths if p.endswith('.md')]
print('pages', len(mdp), 'binaries', len(paths) - len(mdp))
print('by visibility', Counter(reg[p]['visibility'] for p in mdp), 'binaries', Counter(reg[p]['visibility'] for p in paths if not p.endswith('.md')))
print('with history', sum(1 for p in mdp if reg[p]['has_history']), 'stale', [p for p in mdp if reg[p]['stale_on_purpose']])
print('length', Counter(reg[p]['length_class'] for p in mdp))
folders = set()
for p in paths:
    d = posixpath.dirname(p)
    while d:
        folders.add(d); d = posixpath.dirname(d)
print('folders', len(folders), sorted(folders))
print('new facts', sum(reg[p]['n_new'] for p in paths))
tot = sum(json.load(open(f'{OUT}/facts/{p[:-3]}.json'))['words_en'] for p in mdp)
print('words', tot)
ph = Counter()
for m in md:
    for a in re.findall(r'\{\{([^}|\\]+)\\?\|([a-z]+)\}\}', open(m).read()): ph[a] += 1
print(sorted(ph.items()))
