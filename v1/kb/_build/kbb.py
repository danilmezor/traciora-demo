"""Builder for demo-seed-v1/kb: one call per page writes en/<path>.md and facts/<path>.json.
Prices are read from catalogue.json and recorded on the page's fact sheet as they are used."""
import json, os, re, posixpath
from decimal import Decimal, ROUND_HALF_UP
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
ROOT = os.path.dirname(OUT)
CFGNAME = os.environ.get('KB_CFG', 'en')  # the configuration being built: 'en' here, 'ru' through kbr.py
REG = HERE + ('/registry.json' if CFGNAME == 'en' else '/registry-%s.json' % CFGNAME)
cat = json.load(open(ROOT + '/catalogue.json'))
JOBS = {j['key']: j[CFGNAME] for j in cat['jobs']}
CATEGORY = {j['key']: j['category'] for j in cat['jobs']}
CFG = cat['configurations'][CFGNAME]
PEOPLE = {str(p['slot']): p for p in json.load(open(ROOT + '/cast.json'))['people']}
VENDORS = {v['id']: v for v in json.load(open(ROOT + '/vendors.json'))[CFGNAME]}
ACCOUNTS = {a['id']: a for a in json.load(open(ROOT + '/accounts.json'))[CFGNAME]['accounts']}
MODE = os.environ.get('KB_WHEN', 'after_rise')
HISTORY_EXTRA = {'customers/prices-for-common-services.md', 'policies/diagnostic-fees.md'}
USED = {'prices': [], 'people': [], 'vendors': [], 'accounts': [], 'dates': []}
VIS = {'W': 'public', 'J': 'staff', 'M': 'middle', 'S': 'senior', 'A': 'administrator'}
SEEN = {'W': 'worker', 'J': 'junior', 'M': 'middle', 'S': 'senior', 'A': 'administrator'}

def _rec(kind, item):
    if item not in USED[kind]:
        USED[kind].append(item)

def _m(x):
    return '${:,.2f}'.format(x)  # kbr.py replaces this for the Russian configuration

def labour(key, when='after_rise', cls='car', company=False):
    """A job's labour on the shop system's arithmetic (seeder/erp/orders.py: price): an hourly job is the class's hours
    to the hundredth x the hour, to the cent; a menu job is its price x the class multiplier, to the cent, and a Russian
    list price of 10 roubles or more to 10 roubles (seeder/erp/reference.py: money)."""
    e = JOBS[key]
    hb = e['hours_by_class'] or {}
    hm = hb.get(cls, 1.0) if cls != 'car' else 1.0
    if hm is None:
        raise ValueError(f'{key} not offered for {cls}')
    if e['labour_pricing'] == 'hourly':
        return round(round(e['hours'] * hm + 1e-9, 2) * CFG['labour_rate']['company_account' if company else 'standard'][when] + 1e-9, 2)
    v = Decimal(str((e['labour_price_company'] if company else e['labour_price'])[when])) * Decimal(str(hm))
    if CFGNAME == 'ru' and not company and v >= 10:
        return float((v / 10).quantize(Decimal(1), ROUND_HALF_UP) * 10)
    return float(v.quantize(Decimal('0.01'), ROUND_HALF_UP))

def num_total(key, tier='standard', when='after_rise', cls='car', company=False):
    """A job's total before tax as the shop system bills it: its labour, and each part line its quantity x the unit
    price (class multiplier and company terms on the unit) to the cent."""
    e = JOBS[key]
    pm = CFG['parts_class_multiplier'][cls] if e['parts_scale_with_class'] else 1.0
    parts = 0.0
    for p in e['parts']:
        o = {x['tier']: x for x in p['options'] if not x.get('story')}
        op = o.get(tier) or o.get('standard') or list(o.values())[0]
        unit = round(op['list_price'] * pm + 1e-9, 2)
        if company:
            unit = round(unit * (1 - CFG['company_account_terms']['parts_discount']) + 1e-9, 2)
        parts += round(p['qty'] * unit + 1e-9, 2)
    extra = sum(f['price'] for f in e['fees']) + (e['sublet']['price'] if e['sublet'] else 0)
    return round(labour(key, when, cls, company) + parts + extra + 1e-9, 2)

def t(key, tier='standard', cls='car'):
    if MODE == 'before_rise':
        return _m(num_total(key, tier, 'before_rise', cls))
    v = num_total(key, tier, 'after_rise', cls)
    _rec('prices', {'catalogue_key': key, 'what': 'total before tax', 'tier': tier, 'class': cls, 'when': 'after_rise', 'value': v})
    return _m(v)

def told(key, tier='standard', cls='car'):
    v = num_total(key, tier, 'before_rise', cls)
    _rec('prices', {'catalogue_key': key, 'what': 'total before tax', 'tier': tier, 'class': cls, 'when': 'before_rise', 'stale_on_purpose': 'S12', 'value': v})
    return _m(v)

def tco(key, tier='standard', cls='car'):
    v = num_total(key, tier, 'after_rise', cls, company=True)
    _rec('prices', {'catalogue_key': key, 'what': 'total before tax, company-account price class', 'tier': tier, 'class': cls, 'when': 'after_rise', 'value': v})
    return _m(v)

def lab(key, when=None, cls='car'):
    when = when or MODE
    v = round(labour(key, when, cls) + 1e-9, 2)
    r = {'catalogue_key': key, 'what': 'labour', 'class': cls, 'when': when, 'value': v}
    if when == 'before_rise': r['stale_on_purpose'] = 'S12'
    _rec('prices', r)
    return _m(v)

def hrs(key, cls='car'):
    e = JOBS[key]; hb = e['hours_by_class'] or {}
    v = round(e['hours'] * (hb.get(cls, 1.0) if cls != 'car' else 1.0), 2)
    _rec('prices', {'catalogue_key': key, 'what': 'hours', 'class': cls, 'value': v})
    return ('%g' % v)

def part(key, idx=0, tier='standard', field='list_price'):
    p = JOBS[key]['parts'][idx]
    o = {x['tier']: x for x in p['options'] if not x.get('story')}
    op = o.get(tier) or o.get('standard')
    if field == 'brand':
        return op['brand']
    v = op['list_price']
    _rec('prices', {'catalogue_key': key, 'what': 'part list price each: ' + p['name'], 'tier': tier, 'qty': p['qty'], 'unit': p['unit'], 'brand': op['brand'], 'value': v})
    return _m(v)

def parts_total(key, tier='standard'):
    e = JOBS[key]; s = 0
    for p in e['parts']:
        o = {x['tier']: x for x in p['options'] if not x.get('story')}
        op = o.get(tier) or o.get('standard')
        s += op['list_price'] * p['qty']
    v = round(s + 1e-9, 2)
    _rec('prices', {'catalogue_key': key, 'what': 'parts and fluids total', 'tier': tier, 'value': v})
    return _m(v)

def rate(kind='standard', when=None):
    when = when or MODE
    v = CFG['labour_rate'][kind][when]
    r = {'catalogue_key': f'configurations.{CFGNAME}.labour_rate.{kind}.{when}', 'what': 'labour hour', 'value': v}
    if when == 'before_rise': r['stale_on_purpose'] = 'S12'
    _rec('prices', r)
    return _m(v)

def money(v, why):
    """A number that is not in the catalogue: must be listed under new facts by the page."""
    return _m(v) if isinstance(v, float) or v >= 1000 else '${:,}'.format(v) if isinstance(v, int) else _m(v)

FOUNDER_FULL = 'Ray Brennan'
def S(slot, form='first'):
    p = PEOPLE[str(slot)]; e = p['en']
    full = FOUNDER_FULL if str(slot) == '1' else e['full_name']
    out = full if form == 'full' else full.split()[0]
    _rec('people', {'slot': str(slot), 'written_as': out, 'role': p['role_key'], 'site': p['site']})
    return out

def V(vid, form='name'):
    v = VENDORS[vid]
    _rec('vendors', {'vendor': vid, 'name': v['name']})
    return v['name'] if form == 'name' else v[form]

def A(aid):
    a = ACCOUNTS[aid]
    _rec('accounts', {'account': aid, 'name': a['name']})
    return a['name']

def D(expr, fmt='date'):
    if MODE == 'before_rise' and expr.startswith('@price_rise'):
        expr = 'T-29mo' if expr == '@price_rise' else 'T-9mo'
    s = '{{' + expr + '|' + fmt + '}}'
    _rec('dates', s)
    return s

def _links(path, body):
    out = []
    for m in re.finditer(r'\]\(([^)#\s]+)(#[^)]*)?\)', body):
        tgt = m.group(1)
        if '://' in tgt or tgt.startswith('mailto:'):
            continue
        res = posixpath.normpath(posixpath.join(posixpath.dirname(path), tgt))
        if res not in out:
            out.append(res)
    return out

def _structure(text):
    """Tables (rows keyed by header) and list items of a page, by section heading: the page's data,
    so that the fact sheet carries every fact that sits in a table or a list."""
    sec, tables, items, cur, head = '(top)', [], [], None, None
    clean = lambda s: re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s).replace('**', '').replace('\\|', '|').strip()
    for ln in text.split('\n'):
        if ln.startswith('#'):
            sec = ln.lstrip('#').strip(); cur = None; continue
        if ln.startswith('|'):
            cells = [clean(c) for c in re.split(r'(?<!\\)\|', ln.strip().strip('|'))]
            if cur is None:
                head = cells; cur = {'section': sec, 'columns': head, 'rows': []}; tables.append(cur)
            elif all(re.fullmatch(r':?-+:?', c) for c in cells):
                continue
            else:
                cur['rows'].append(dict(zip(head, cells)) if len(set(head)) == len(head) and all(head) else cells)
            continue
        cur = None
        m = re.match(r'\s*(?:[-*]|\d+\.)\s+(.*)', ln)
        if m:
            items.append({'section': sec, 'item': clean(m.group(1))})
    return tables, items

def _len(body):
    n = len(re.findall(r'\S+', body))
    return n, ('tiny' if n < 90 else 'short' if n < 260 else 'medium' if n < 650 else 'long')

def page(path, title, vis, by, purpose, body, serves=(), facts=(), new=(), rev=(), ru=(), created=None, broken=(), stale=None):
    """by: cast slot of the person whose voice the page is in. rev: list of (slot, date expr, what) after the
    first version. created: (slot, date expr) when the page did not come with the go-live import."""
    body = body.strip('\n')
    body = '\n'.join(re.sub(r'(\{\{[^}|]*)(?<!\\)\|([a-z]+\}\})', r'\1\\|\2', ln) if ln.startswith('|') else ln for ln in body.split('\n'))
    text = f'# {title}\n\n{body}\n'
    if MODE == 'before_rise':
        for k in USED: USED[k] = []
        if path in HISTORY_EXTRA or any(str(r[1]).startswith('@price_rise+3wd') for r in rev):
            fp = f'{OUT}/en/_history/{path}'; os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, 'w').write(text)
        return path
    links = _links(path, text)
    n, cls = _len(text)
    first = ({'n': 1, 'kind': 'import', 'author': 'operator (History shows "Administrator")', 'text_date': '{{@golive|date}}',
              'what': 'the page as it stood on the shared drive when Traciora went live; message "Imported from the tenant\'s files"'}
             if created is None else
             {'n': 1, 'kind': created[2] if len(created) > 2 else 'edit', 'author_slot': str(created[0]), 'text_date': '{{' + created[1] + '|date}}', 'what': 'page created'})
    if created is not None and len(created) > 3:
        first.update(created[3])
    revs = [first]
    for i, r in enumerate(rev):
        d = {'n': i + 2, 'kind': 'edit', 'author_slot': str(r[0]), 'text_date': '{{' + r[1] + '|date}}', 'what': r[2]}
        if len(r) > 3: d.update(r[3])
        revs.append(d)
    sheet = {
        'path': path, 'title': title, 'first_revision_text': ('en/_history/' + path) if (path in HISTORY_EXTRA or any(str(r[1]).startswith('@price_rise+3wd') for r in rev)) else None, 'visibility': VIS[vis], 'seen_from': SEEN[vis],
        'voice_of_slot': str(by), 'purpose': purpose, 'serves': list(serves),
        'length_class': cls, 'words_en': n, 'links_to': links, 'broken_links_on_purpose': list(broken),
        'stale_on_purpose': stale,
        'facts': list(facts), 'tables': _structure(text)[0], 'list_items': _structure(text)[1], 'prices': USED['prices'], 'people': USED['people'], 'vendors': USED['vendors'],
        'accounts': USED['accounts'], 'dates': USED['dates'], 'new_facts': list(new),
        'revisions': revs, 'has_history': len(revs) > 1 or created is not None, 'notes_for_russian_writer': list(ru),
    }
    for k in USED: USED[k] = []
    fp = f'{OUT}/en/{path}'; os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(text)
    jp = OUT + '/facts/' + re.sub(r"\.md$", ".json", path); os.makedirs(os.path.dirname(jp), exist_ok=True)
    json.dump(sheet, open(jp, 'w'), ensure_ascii=False, indent=1)
    reg = json.load(open(REG)) if os.path.exists(REG) else {}
    reg[path] = {k: sheet[k] for k in ('title', 'visibility', 'voice_of_slot', 'purpose', 'serves', 'length_class', 'links_to', 'has_history', 'stale_on_purpose', 'broken_links_on_purpose')}
    reg[path]['n_new'] = len(sheet['new_facts']); reg[path]['n_rev'] = len(revs)
    json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=1)
    return path
