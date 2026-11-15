# -*- coding: utf-8 -*-
"""Russian configuration of the knowledge-base builder. A batch file ruNN.py does `from kbr import *` and calls
page() once per page: it writes ru/<path>.md and facts-ru/<path>.json. The page keys, readers, voices, purposes
and revision plans are those of the English fact sheets (facts/<path>.json), unless the call says otherwise.

Every amount of money in a Russian page goes through a helper here, so that it is a catalogue figure (t, lab,
part, rate ...), a ledger row (LM), a sum of such figures (M) or a named new fact (N). check_ru.py refuses any
other amount. Names go through S / P (cast), A / AD / AC / ACD (accounts) and V (vendors); the declined forms
are written by hand and checked against the seed files by their stems, so a renamed person breaks the build."""
import os, json, re, posixpath
os.environ['KB_CFG'] = 'ru'
import kbb
from kbb import t, told, tco, lab, part, parts_total, rate, num_total, V, JOBS, CFG, CATEGORY, MODE, OUT, ROOT, REG, PEOPLE, VENDORS, ACCOUNTS, USED, _rec, _links, _structure, _len

LEDGER = {r['key']: r for r in json.load(open(ROOT + '/ledger.json'))['rows']}
AMOUNTS, NEW_AMOUNTS = [], []
VIS, SEEN = kbb.VIS, kbb.SEEN
VIS_KEY = {v: k for k, v in VIS.items()}
ONLY_RU = {}  # filled by page(only_ru=...)
OUTCOMES = json.load(open(kbb.HERE + '/verify_outcomes.json'))  # what became of each item to verify (kb/TO-VERIFY.md)

def settle(path, verify):
    """Split a page's items to verify into those still open (or waiting for a specialist) and those settled:
    verified on a primary page or corrected. Every item must have an outcome in verify_outcomes.json."""
    still, settled = [], []
    for item in verify:
        hit = [o for o in OUTCOMES.get(path, []) if item.startswith(o['starts'])]
        assert len(hit) == 1, f'{path}: no single outcome in verify_outcomes.json for the item to verify {item[:60]!r}'
        o = hit[0]
        if o['outcome'] in ('verified', 'corrected'):
            settled.append({'item': item, **{k: v for k, v in o.items() if k != 'starts'}})
        else:
            still.append(item)
    return still, settled

def fmt(x):
    """12 520 ₽; kopecks only when there are any: 102,60 ₽."""
    x = round(float(x) + 1e-9, 2)
    if abs(x - round(x)) < 0.005:
        s = '{:,}'.format(int(round(x))).replace(',', ' ')
    else:
        s = '{:,.2f}'.format(x).replace(',', ' ').replace('.', ',')
    return s + ' ₽'

def _m(x):
    AMOUNTS.append(round(float(x) + 1e-9, 2))
    return fmt(x)
kbb._m = _m  # every catalogue helper of kbb now writes roubles and reports what it wrote

def M(x):
    """A figure computed from catalogue or ledger figures (a sum, a bill with VAT)."""
    return _m(x)

def N(x, why):
    """An amount that is in no seed file: a new fact of this page, listed on its fact sheet with the reason."""
    NEW_AMOUNTS.append({'value': x, 'why': why})
    return _m(x)

def LV(key):
    r = LEDGER[key]
    return r['ru'] if 'ru' in r and r.get('ru') is not None else r.get('value', r.get('ru'))

def LM(key, sub=None):
    v = LV(key)
    if sub is not None: v = v[sub]
    return _m(v)

def nt(key, tier='standard', cls='car', when='after_rise', company=False):
    return num_total(key, tier, when, cls, company)

def nlab(key, when='after_rise', cls='car'):
    return round(kbb.labour(key, when, cls) + 1e-9, 2)

def nrate(kind='standard', when='after_rise'):
    return CFG['labour_rate'][kind][when]

SUP_RATE = CFG['shop_supplies']['rate_of_hourly_labour']; SUP_CAP = CFG['shop_supplies']['cap_per_order']; VAT = CFG['tax']['rate']
def nsup(*labours):
    """Расходные материалы on an order: the rate on its hourly-priced labour, up to the cap."""
    return round(min(SUP_RATE * sum(labours), SUP_CAP) + 1e-9, 2)

def vat(x):
    return round(x * (1 + VAT) + 1e-9, 2)

def hrs(key, cls='car'):
    return kbb.hrs(key, cls).replace('.', ',')

def brand(key, idx=0, tier='standard'):
    return part(key, idx, tier, 'brand')

def D(expr, fmt_='date'):
    """Dates keep the outline's grammar. Before the last rise the page spoke of the rise before it (@price_rise_2)."""
    if MODE == 'before_rise' and expr.startswith('@price_rise') and not expr.startswith('@price_rise_'):
        expr = expr.replace('@price_rise', '@price_rise_2', 1)
    s = '{{' + expr + '|' + fmt_ + '}}'
    _rec('dates', s)
    return s

# ---- names -------------------------------------------------------------------------------------------------
def _stems_ok(text, words):
    ws = [w.lower().replace('ё', 'е') for w in re.findall(r'[А-Яа-яЁё]+', ' '.join(words)) if len(w) >= 3]
    for w in re.findall(r'[А-Яа-яЁё]+', text):
        w = w.lower().replace('ё', 'е')
        if len(w) < 3: continue
        ok = False
        for n in ws:
            c = 0
            while c < min(len(w), len(n)) and w[c] == n[c]: c += 1
            if c >= 3 and c >= min(len(w), len(n)) - 3: ok = True; break
        if not ok: return False
    return True

def _person(slot):
    p = PEOPLE[str(slot)]; r = p['ru']
    return p, r, [r['full_name'], r.get('colleagues_call') or '', r.get('customers_call') or '']

def S(slot, form='io'):
    """A person in the nominative. full: Имя Отчество Фамилия; io: Имя Отчество (the first name where the cast
    gives no patronymic); fi: Имя Фамилия; f: Фамилия; i: Имя; fio: Фамилия И. О."""
    p, r, _ = _person(slot)
    parts = r['full_name'].split(); first, last = parts[0], parts[-1]; patr = parts[1] if len(parts) == 3 else None
    out = {'full': r['full_name'], 'io': (first + ' ' + patr) if patr else first, 'fi': first + ' ' + last, 'f': last, 'i': first,
           'fio': last + ' ' + first[0] + '.' + ((' ' + patr[0] + '.') if patr else '')}[form]
    _rec('people', {'slot': str(slot), 'written_as': out, 'role': p['role_key'], 'site': p['site']})
    return out

def P(slot, text):
    """A person as the sentence needs them (declined, or as colleagues call them). Checked against cast.json."""
    p, r, words = _person(slot)
    assert _stems_ok(text, words), f'{text!r} does not match slot {slot} in cast.json: {words}'
    _rec('people', {'slot': str(slot), 'written_as': text, 'role': p['role_key'], 'site': p['site']})
    return text

def A(aid):
    """A company account by name, in guillemets as a Russian page writes it."""
    a = ACCOUNTS[aid]; _rec('accounts', {'account': aid, 'name': a['name']})
    return a['name'] if '«' in a['name'] else '«' + a['name'] + '»'

def AD(aid, text):
    a = ACCOUNTS[aid]
    assert _stems_ok(text.replace('«', ' ').replace('»', ' '), [a['name']]), f'{text!r} does not match account {aid}: {a["name"]}'
    _rec('accounts', {'account': aid, 'name': a['name'], 'written_as': text})
    return text

def AC(aid, idx, form='io'):
    """A contact of an account, by position in accounts.json."""
    c = ACCOUNTS[aid]['contacts'][idx]; parts = c['name'].split()
    out = {'full': c['name'], 'io': ' '.join(parts[:2]), 'f': parts[-1], 'fi': parts[0] + ' ' + parts[-1]}[form]
    _rec('accounts', {'account': aid, 'contact': c['name'], 'role': c['role'], 'written_as': out})
    return out

def ACD(aid, idx, text):
    c = ACCOUNTS[aid]['contacts'][idx]
    assert _stems_ok(text, [c['name']]), f'{text!r} does not match contact {idx} of {aid}: {c["name"]}'
    _rec('accounts', {'account': aid, 'contact': c['name'], 'role': c['role'], 'written_as': text})
    return text

def fleet(aid):
    return ACCOUNTS[aid]['fleet_count']

# ---- the page ----------------------------------------------------------------------------------------------
def _en_sheet(path):
    fp = OUT + '/facts/' + (re.sub(r'\.md$', '.json', path) if path.endswith('.md') else path + '.json')
    return json.load(open(fp)) if os.path.exists(fp) else None

def page(path, title, body, by=None, vis=None, purpose=None, serves=None, diff=(), new=(), verify=(), msgs=(), rev=None,
         created=None, stale='inherit', broken=None, hist=None):
    """diff: where the Russian page differs from the English sheet (numbers, terms, names, law). new: new facts.
    verify: legal or trade statements the research does not support. msgs: the Russian messages of the revisions
    after the first, in the order of the English sheet. rev / created: only when the Russian history differs."""
    en = _en_sheet(path)
    if en is None:
        assert vis and by is not None and purpose and serves is not None, f'{path}: a page only in Russian needs vis, by, purpose, serves'
    vis = vis or VIS_KEY[en['visibility']]
    by = str(by if by is not None else en['voice_of_slot'])
    body = body.strip('\n')
    assert '$' not in body, path
    body = '\n'.join(re.sub(r'(\{\{[^}|]*)(?<!\\)\|([a-z]+\}\})', r'\1\\|\2', ln) if ln.startswith('|') else ln for ln in body.split('\n'))
    text = f'# {title}\n\n{body}\n'
    if hist is None:
        hist = bool(en and en.get('first_revision_text'))
    if MODE == 'before_rise':
        for k in USED: USED[k] = []
        del AMOUNTS[:], NEW_AMOUNTS[:]
        if hist:
            fp = f'{OUT}/ru/_history/{path}'; os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, 'w').write(text)
        return path
    if rev is None and created is None and en is not None:
        revs = json.loads(json.dumps(en['revisions']))
        later = [r for r in revs if r['n'] > 1]
        assert len(msgs) <= len(later), f'{path}: {len(msgs)} messages for {len(later)} later revisions'
        for r, m in zip(later, msgs): r['message_ru'] = m
    else:
        first = ({'n': 1, 'kind': 'import', 'author': 'operator (History shows "Administrator")', 'text_date': '{{@golive|date}}',
                  'what': 'the page as it stood on the shared drive when Traciora went live', 'message_ru': 'Импортировано из файлов компании'}
                 if created is None else
                 {'n': 1, 'kind': created[2] if len(created) > 2 else 'edit', 'author_slot': str(created[0]), 'text_date': '{{' + created[1] + '|date}}', 'what': 'page created'})
        if created is not None and len(created) > 3: first.update(created[3])
        revs = [first]
        for i, r in enumerate(rev or ()):
            d = {'n': i + 2, 'kind': 'edit', 'author_slot': str(r[0]), 'text_date': '{{' + r[1] + '|date}}', 'what': r[2]}
            if len(r) > 3: d.update(r[3])
            revs.append(d)
    n, cls = _len(text)
    verify, settled = settle(path, verify)
    sheet = {
        'path': path, 'title': title, 'title_en': en['title'] if en else None, 'exists_in': 'both' if en else 'ru only',
        'english_sheet': ('facts/' + re.sub(r'\.md$', '.json', path)) if en else None,
        'first_revision_text': ('ru/_history/' + path) if hist else None,
        'visibility': VIS[vis], 'seen_from': SEEN[vis], 'voice_of_slot': by,
        'purpose': purpose or en['purpose'], 'serves': list(serves if serves is not None else en['serves']),
        'length_class': cls, 'words_ru': n, 'links_to': _links(path, text),
        'broken_links_on_purpose': list(broken if broken is not None else (en['broken_links_on_purpose'] if en else [])),
        'stale_on_purpose': (en['stale_on_purpose'] if en else None) if stale == 'inherit' else stale,
        'differs_from_en': list(diff), 'new_facts': list(new), 'new_amounts': list(NEW_AMOUNTS), 'to_verify': list(verify), 'settled': settled,
        'tables': _structure(text)[0], 'list_items': _structure(text)[1],
        'prices': USED['prices'], 'people': USED['people'], 'vendors': USED['vendors'], 'accounts': USED['accounts'], 'dates': USED['dates'],
        'amounts': sorted(set(AMOUNTS)),
        'revisions': revs, 'has_history': len(revs) > 1 or revs[0]['kind'] != 'import',
    }
    for k in USED: USED[k] = []
    del AMOUNTS[:], NEW_AMOUNTS[:]
    fp = f'{OUT}/ru/{path}'; os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(text)
    jp = OUT + '/facts-ru/' + re.sub(r'\.md$', '.json', path); os.makedirs(os.path.dirname(jp), exist_ok=True)
    json.dump(sheet, open(jp, 'w'), ensure_ascii=False, indent=1)
    reg = json.load(open(REG)) if os.path.exists(REG) else {}
    reg[path] = {k: sheet[k] for k in ('title', 'title_en', 'exists_in', 'visibility', 'voice_of_slot', 'purpose', 'serves', 'length_class', 'links_to',
                                       'has_history', 'stale_on_purpose', 'broken_links_on_purpose', 'amounts')}
    reg[path]['n_new'] = len(sheet['new_facts']); reg[path]['n_verify'] = len(sheet['to_verify']); reg[path]['n_rev'] = len(revs)
    reg[path]['first_revision_text'] = sheet['first_revision_text']
    json.dump(reg, open(REG, 'w'), ensure_ascii=False, indent=1)
    return path

def fee(key, idx=0):
    f = JOBS[key]['fees'][idx]
    _rec('prices', {'catalogue_key': key, 'what': 'fee: ' + f['name'], 'value': f['price']})
    return _m(f['price'])

def sublet(key, field='price'):
    s = JOBS[key]['sublet']
    _rec('prices', {'catalogue_key': key, 'what': 'sublet ' + field + ': ' + s['what'], 'value': s[field]})
    return _m(s[field])

# The three shops as staff name them (ledger geo.short_name), and their public lines (phones.md).
MAIN, EAST, WEST = 'Московское шоссе', 'Инженерный', 'Техническая'
TEL = {'main': '+7 (8422) 10-40-40', 'east': '+7 (8422) 10-40-41', 'west': '+7 (843) 100-40-30'}
ADDR = {'main': 'Ульяновск, Московское шоссе, 40', 'east': 'Ульяновск, 10-й Инженерный проезд, 30', 'west': 'Казань, ул. Техническая, 30'}

def pl(n, one, few, many):
    """22 наряда, 61 час, 46 выдач: the number with the right form of the noun."""
    n = int(n); k = n % 100
    w = many if 11 <= k <= 14 else one if n % 10 == 1 else few if 2 <= n % 10 <= 4 else many
    return f'{n} {w}'
