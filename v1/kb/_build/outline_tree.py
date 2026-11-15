import json, posixpath, kbb
from collections import Counter, OrderedDict
reg = json.load(open(kbb.REG))
def slotname(s):
    s = str(s)
    return {'F3': 'F3 Brad Keller'}.get(s) or (s + ' ' + ('Ray Brennan' if s == '1' else kbb.PEOPLE[s]['en']['full_name']))
ORDER = ['', 'customers', 'shop-floor', 'services', 'services/maintenance', 'services/brakes', 'services/tires', 'services/diagnostics', 'services/suspension', 'services/ac',
         'services/electrical', 'services/engine', 'services/transmission', 'services/inspections', 'prices', 'policies', 'accounts', 'accounts/credit', 'how-to', 'parts',
         'shops', 'shops/main', 'shops/east', 'shops/west', 'team', 'office', 'management', 'management/owners', 'playbooks']
SEEN = {'': 'worker (tenant setting); README.md itself junior', 'customers': 'worker = public', 'shop-floor': 'worker = public', 'services': 'worker = public', 'prices': 'worker = public for the price list; the other three files junior', 'policies': 'junior',
        'accounts': 'junior', 'accounts/credit': 'middle', 'how-to': 'junior', 'parts': 'junior', 'shops': 'junior', 'team': 'junior', 'office': 'middle', 'management': 'senior',
        'management/owners': 'administrator', 'playbooks': 'administrator (pinned by the product\'s import)'}
out = []
vis_short = {'public': 'public', 'staff': 'staff', 'middle': 'middle', 'senior': 'senior', 'administrator': 'admin'}
for d in ORDER:
    ps = sorted(p for p in reg if posixpath.dirname(p) == d)
    if not ps: continue
    seen = SEEN.get(d) or ('inherits ' + SEEN[d.split('/')[0]].split(' ')[0])
    out.append(f"\n### `{d or '(root)'}/` · {len(ps)} · seen from {seen}\n")
    out.append('| Page | Title | Vis. | Voice | Len. | Rev. | Serves | Purpose | Links to |')
    out.append('|---|---|---|---|---|---:|---|---|---|')
    for p in ps:
        r = reg[p]
        name = posixpath.basename(p)
        links = ', '.join(l[:-3] if l.endswith('.md') else l for l in r['links_to']) or '-'
        if r['broken_links_on_purpose']: links += ' (one broken on purpose)'
        ln = r['length_class'].replace('binary: ', '')
        serves = ' '.join(s.replace('challenge:', 'C:').replace('operate:', 'O:').replace('visibility:', 'V:') for s in r['serves'])
        flag = ' **stale**' if r['stale_on_purpose'] else ''
        out.append(f"| `{name}` | {r['title']}{flag} | {vis_short[r['visibility']]} | {slotname(r['voice_of_slot'])} | {ln} | {r['n_rev']} | {serves} | {r['purpose']} | {links} |")
open('tree.md', 'w').write('\n'.join(out) + '\n')
md = [p for p in reg if p.endswith('.md')]
print(len(md), Counter(reg[p]['visibility'] for p in md), sum(1 for p in md if reg[p]['has_history']), Counter(reg[p]['length_class'] for p in md))
print(len('\n'.join(out)))
