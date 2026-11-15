# Builder, second pass: the output follows what checks/check_calls.py reads (counts, price rows, file names).
# Run: PYTHONPATH=<repo>/apps/backend/src <repo>/.venv/bin/python build2.py [call numbers]
import datetime, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import (SEED, OUT, REPO, CARD, WEIGHTS, CHECK_KEYS, ENGINE_VERSION, judge, scorecard, NUMWORD, WORD, ORDINAL, render_run,
                   LATIN, LADA, LATIN_RE, chance, tidy, sentences, lev, RULE_WHAT, R3KIND)
import more

CAT = json.load(open(SEED + '/catalogue.json'))
JOBS = {j['key']: j['ru'] for j in CAT['jobs']}
CFG = CAT['configurations']['ru']
T0 = datetime.date(2026, 11, 13)
P_DAY = datetime.date(2026, 6, 22)
FILL_DROP = 45   # % of sentence-initial fillers dropped
HES_KEEP = 15    # % of hesitations kept
R5_ERR = 50      # % of the numbers that can be split which are split (about 9 % of all number mentions)
RULE_WHAT = dict(RULE_WHAT, R2f='a first name heard as its neighbour')
RULE_WHAT['R2+'] = "the company's name loses its quotes and hyphen"

TERM_STEMS = ['газел', 'солярис', 'логан', 'дастер', 'сандеро', 'транзит', 'королл', 'камри', 'кашка', 'альмер', 'круз', 'лачетти',
              'рапид', 'лансер', 'поло', 'джолион', 'хавал', 'сид', 'рио', 'некст', 'пежо', 'вест', 'грант', 'ларгус', 'приор',
              'октави', 'мазд', 'киа', 'рено', 'форд', 'тойот', 'ниссан', 'шевроле', 'шкод', 'ситроен', 'патриот',
              'шаров', 'шрус', 'гранат', 'ступи', 'стабилизатор', 'амортизатор', 'сход-развал', 'грм', 'помп', 'термостат',
              'сцеплени', 'маховик', 'люфт', 'нормо-час', 'суппорт', 'глушител', 'резонатор', 'пыльник', 'баллонник', 'шпильк',
              'бремхоф', 'сангсин', 'аком', 'троит', 'хрусте', 'мандо', 'выжимн', 'рессор', 'рейк', 'корзин']
TERM_RE = re.compile(r'(?<![А-Яа-яЁёA-Za-z])(' + '|'.join(map(re.escape, TERM_STEMS)) + r')', re.I)
HES = re.compile(r'(?<![А-Яа-яЁё-])(?:[Ээ]-э(?:-э)*|[Мм]-м(?:-м)*|[Ээ]м+|[Хх]м|[Гг]м|[Мм]да)(?![А-Яа-яЁё-])[,.…]*\s*')
FILL_COUNT = re.compile(r'(?<![А-Яа-яЁё-])(?:ну|вот|значит)(?![А-Яа-яЁё-])', re.I)
FILL_HEAD = re.compile(r'(^|[.?!] )(Ну|Вот|Значит),? (?=[^\s.?!,]+[ ,]+[^\s.?!]+)')
NUM_LEFT = re.compile(r'(?<![А-Яа-яЁё-])(?:(?:в|к|на|до|с|после|около|за|из|по|от)\s+(?:один|одну|два|две|три|четыре|пять|шесть|семь|восемь|девять|'
                      r'двух|тр[её]х|четыр[её]х|пяти|шести|семи|восьми|девяти|десяти|одиннадцати|двенадцати|пятнадцати|двадцати|тридцати|'
                      r'восьмидесяти|сорока|ста)|тысяч[аиу]?|полтора|полторы|с половиной)(?![А-Яа-яЁё-])', re.I)


def cwords(s):
    """The checker's word list."""
    return [w for w in (x.strip('.,!?;:…—–-"«»') for x in s.lower().split()) if w]


def split_error(rendered):
    """A number split the way recognition splits it, or None."""
    m = re.fullmatch(r'(\d)(\d) (\d)(\d\d)', rendered)
    if m and m.group(1) != '1' and m.group(2) != '0' and m.group(4) == '00':
        return f'{m.group(1)}0 {m.group(2)}{m.group(3)}00'          # 27 400 -> 20 7400
    m = re.fullmatch(r'(\d{1,2}) (\d)(\d\d)', rendered)
    if m and m.group(3) != '00':
        return f'{m.group(1)} {m.group(2)}00 {int(m.group(3))}'     # 15 552 -> 15 500 52
    m = re.fullmatch(r'(\d)(\d)(\d\d)', rendered)
    if m and m.group(3) != '00' and m.group(2) != '0':
        return f'{m.group(1)}{m.group(2)}00 {int(m.group(3))}'      # 8760 -> 8700 60
    if m and m.group(3) == '00' and m.group(2) != '0':
        return f'{m.group(1)} {m.group(2)}00'                       # 9500 -> 9 500 (two numbers: 9 and 500)
    m = re.fullmatch(r'(\d)(\d)(\d)', rendered)
    if m and m.group(2) != '0' and m.group(3) != '0':
        return f'{m.group(1)}00 {m.group(2)}{m.group(3)}'           # 135 -> 100 35
    m = re.fullmatch(r'(\d{1,2}):(\d\d)', rendered)
    if m and m.group(2) != '00':
        return f'{m.group(1)} {m.group(2)}'                         # 9:30 -> 9 30
    return None


def to_digits(text, st, key):
    words = [(m.start(), m.end(), m.group()) for m in WORD.finditer(text)]
    out, pos, k = [], 0, 0
    while k < len(words):
        s, e, w = words[k]
        if w.lower() not in NUMWORD:
            k += 1
            continue
        run = [k]
        while run[-1] + 1 < len(words) and words[run[-1] + 1][2].lower() in NUMWORD \
                and text[words[run[-1]][1]:words[run[-1] + 1][0]] == ' ':
            run.append(run[-1] + 1)
        toks = [words[j][2].lower() for j in run]
        prev_word = words[run[0] - 1][2].lower() if run[0] > 0 and text[words[run[0] - 1][1]:s] == ' ' else ''
        nxt = words[run[-1] + 1][2].lower() if run[-1] + 1 < len(words) and \
            text[words[run[-1]][1]:words[run[-1] + 1][0]] == ' ' else ''
        rendered = None if ORDINAL.match(nxt) else render_run(toks, prev_word)
        if rendered is not None:
            said = text[s:words[run[-1]][1]]
            dictated = text[words[run[-1]][1]:words[run[-1]][1] + 2] == ', ' and nxt == '' and run[-1] + 1 < len(words) and words[run[-1] + 1][2].lower() in NUMWORD
            dictated = dictated or (s >= 2 and text[s - 2:s] == ', ' and run[0] > 0 and words[run[0] - 1][2].lower() in NUMWORD)
            if chance(*key, 'r5', s, said) < R5_ERR and not st.get('no_r5_errors') and not dictated:
                bad = split_error(rendered)
                if bad:
                    st['r5err'].append((key[1], said, bad))
                    rendered = bad
            out.append(text[pos:s]); out.append(rendered); pos = words[run[-1]][1]
            st['digits'] += 1
        k = run[-1] + 1
    out.append(text[pos:])
    res = ''.join(out)
    res, n = re.subn(r'\b(\d{3}), (\d{3}), (\d{2}), (\d{2})\b', r'\1 \2 \3 \4', res)
    st['phones'] += n
    return res


def store_line(call, turn, said, pairs, st, auto):
    n, s, held = call['n'], said, []
    for pair in pairs:
        a, b = pair[0], pair[1]
        if a not in s:
            raise SystemExit(f'call {n} turn {turn}: fragment not in the line: {a!r}\n   {s!r}')
        s = s.replace(a, f'\x00{len(held)}\x00', 1)
        held.append(b)
    if 'Ермак-Сервис' in s:
        s = s.replace('Ермак-Сервис', 'Ермак Сервис'); auto['hyphen'].add(turn)
    before = s
    s = HES.sub(lambda m: m.group(0) if chance(n, turn, 'hes', m.start()) < HES_KEEP else '', s)
    s = re.sub(r'\?\.\.', '?', s)
    s = re.sub(r'!\.\.', '.', s)
    s = re.sub(r'^(?:\.\.\.|…)\s*', '', s)
    s = re.sub(r'(?:\.\.\.|…)\s+(?=[А-ЯЁA-Z\x00«\d])', '. ', s)
    s = re.sub(r'(?:\.\.\.|…)\s+', ', ', s)
    s = re.sub(r'(?:\.\.\.|…)$', '.', s)
    s = re.sub(r'(?<=[,.?!:])\s+—\s+', ' ', s)
    s = re.sub(r'\s+—\s+', ' \x01 ', s)
    s = s.replace('!', '.')
    s = tidy(s.replace(' \x01 ', ' \x02 ')).replace(' \x02 ', ' \x01 ')
    if not call.get('keep_fillers'):
        def drop(m):
            if chance(n, turn, 'fill', m.start()) < FILL_DROP:
                auto['fillers'].add(turn)
                return m.group(1)
            return m.group(0)
        s = FILL_HEAD.sub(drop, s)
    if s.replace(' \x01 ', ' — ') != before:
        auto['smooth'].add(turn)

    def latin(m):
        word = m.group(1)
        st['foreign'] += 1
        if chance(n, turn, word, m.start()) < (25 if word in LADA else 55):
            st['latin'] += 1
            auto['latin'].append((turn, word, LATIN[word]))
            return LATIN[word]
        return word
    s = LATIN_RE.sub(latin, s)
    if call.get('gazelle_lower') and 'Газел' in s:
        cnt = s.count('Газел')
        s = s.replace('Газел', 'газел'); auto['gazelle'].append((turn, cnt)); st['term_errors'] += cnt
    d0 = st['digits']
    s = to_digits(s, st, (n, turn))
    if st['digits'] != d0:
        auto['digits'].add(turn)
    for i, b in enumerate(held):
        s = s.replace(f'\x00{i}\x00', b)
    s = re.sub(r' \x01 (?=\d)', ' — ', s)
    s = s.replace(' \x01 ', ', ')
    return tidy(s)


def list_price(job, cls, tier, company, when):
    """catalogue.json's price as checks/check_calls.py computes it."""
    j = JOBS[job]
    hm = (j['hours_by_class'] or {}).get(cls, 1.0) if j['hours_by_class'] else 1.0
    lab = (j['labour_price_company'] if company else j['labour_price'])[when] * hm
    parts = 0.0
    for slot in j['parts']:
        opts = {o['tier']: o for o in slot['options'] if not o.get('story')}
        o = opts.get(tier) or opts.get('standard') or next(iter(opts.values()))
        parts += slot['qty'] * o['list_price']
    parts *= CFG['parts_class_multiplier'][cls] if j['parts_scale_with_class'] else 1.0
    if company:
        parts *= 1 - CFG['company_account_terms']['parts_discount']
    total = lab + parts + sum(f['price'] for f in j['fees']) + (j['sublet']['price'] if j['sublet'] else 0.0)
    return round(total, 2)


def price_rows(n, date):
    when = 'after_rise' if datetime.date.fromisoformat(date) >= P_DAY else 'before_rise'
    rows = []
    for job, cls, tier, pclass, said, figure in more.PRICES.get(n, []):
        company = pclass == 'company_account'
        row = {'job': job, 'name': JOBS[job]['name'], 'vehicle_class': cls, 'parts_tier': tier, 'price_class': pclass,
               'rub': list_price(job, cls, tier, company, when),
               'labour_hour_rub': CFG['labour_rate']['company_account' if company else 'standard'][when]}
        if said:
            row['said'] = said; row['said_rub'] = figure
        rows.append(row)
    return rows


def count_mentions(script_text, stored_text, names, firsts):
    names_n = sum(len(re.findall(re.escape(stem), script_text, re.I)) for stem in names)
    firsts_n = sum(len(re.findall(re.escape(stem), script_text, re.I)) for stem in firsts)
    hes_said = len(HES.findall(script_text))
    hes_left = len(HES.findall(stored_text))
    fill_said = len(FILL_COUNT.findall(script_text))
    fill_left = len(FILL_COUNT.findall(stored_text))
    return names_n, firsts_n, (hes_said, max(0, hes_said - hes_left)), (fill_said, max(0, fill_said - fill_left))


def build(call):
    n = call['n']
    st = dict(digits=0, phones=0, foreign=0, latin=0, term_errors=0, r5err=[], no_r5_errors=call.get('no_r5_errors'))
    auto = dict(hyphen=set(), smooth=set(), latin=[], gazelle=[], digits=set(), fillers=set())
    bc, hes, xpairs = more.BC.get(n, {}), more.HES.get(n, {}), more.XPAIRS.get(n, {})
    # expand: source turns, with the backchannels after the turns they are said over
    turns = []
    for idx, row in enumerate(call['script'], 1):
        who, said = row[0], row[1]
        pairs = list(row[2]) if len(row) > 2 and row[2] else []
        opts = dict(row[3]) if len(row) > 3 else {}
        if idx in hes:
            a, b = hes[idx]
            if a not in said:
                raise SystemExit(f'call {n} turn {idx}: hesitation anchor not found: {a!r}')
            said = said.replace(a, b, 1)
        pairs += xpairs.get(idx, [])
        turns.append(dict(src=idx, who=who, said=said, pairs=pairs, opts=opts))
        if idx in bc:
            roll = chance(n, idx, 'bc')
            state = 'lost' if roll < 50 else 'joined' if roll < 70 else 'kept'
            turns.append(dict(src=None, who='c' if who == 'a' else 'a', said=bc[idx], pairs=[], opts={'overlap': True, 'bc': state}))
    # a joined backchannel needs the same speaker's turn right after it
    for i, t in enumerate(turns):
        if t['opts'].get('bc') == 'joined':
            nxt = turns[i + 1] if i + 1 < len(turns) else None
            if not nxt or nxt['who'] != t['who'] or nxt['opts'].get('lost') or 'hold' in nxt['opts'] or nxt['opts'].get('swap'):
                t['opts']['bc'] = 'kept'
    script, prev_end, prev_start = [], 0.0, 0.0
    for i, t in enumerate(turns, 1):
        t['n'] = i
        nw = len(cwords(t['said']))
        dur = max(1.0, nw / 1.9)
        gap = 0.5 + chance(n, t['src'] or -i, 'gap') % 10 / 10
        if t['said'].startswith('...') or t['said'].startswith('…'):
            gap += 1.4
        hold_s = t['opts'].get('pause', 0) if t['who'] == 'h' else 0
        if t['opts'].get('overlap'):
            start = max(prev_start + 0.4, prev_end - 0.9)
        else:
            start = prev_end + (gap if i > 1 else 0)
        entry = {'n': i, 'who': {'a': 'advisor', 'c': 'customer', 'h': 'hold'}[t['who']], 'at_s': round(start, 1), 'said': t['said']}
        if t['opts'].get('overlap'):
            entry['overlap'] = True
        if t['who'] == 'h':
            entry['hold_s'] = hold_s
            dur = hold_s
        script.append(entry)
        prev_start = start
        prev_end = max(prev_end, start + dur)
    talk_s = int(math.ceil(prev_end + 0.8))
    src_n = {t['src']: t['n'] for t in turns if t['src']}

    # stored portions
    for t in turns:
        if 'hold' in t['opts']:
            t['stored'] = t['opts']['hold']
        elif t['opts'].get('lost') or t['opts'].get('bc') == 'lost':
            t['stored'] = None
        else:
            t['stored'] = store_line(call, t['n'], t['said'], t['pairs'], st, auto)
    portions = {t['src']: t['stored'] for t in turns if t['src']}

    segments, turn_seg = [], {}
    merge_next = False
    for i, t in enumerate(turns):
        text = t['stored']
        if text is None:
            if t['opts'].get('lost'):
                merge_next = True          # the sample-1 kind: the neighbours of the other speaker become one line
            continue
        if text == '':
            continue
        label = 'customer' if t['who'] == 'c' else 'manager'
        if t['opts'].get('swap'):
            label = 'customer' if label == 'manager' else 'manager'
        joined_bc = i > 0 and turns[i - 1]['opts'].get('bc') == 'joined'
        if (merge_next or t['opts'].get('join') or joined_bc) and segments and segments[-1]['speaker_label'] == label:
            segments[-1]['text'] += ' ' + text
        else:
            segments.append({'sequence': len(segments), 'speaker_label': label, 'start_ms': None, 'end_ms': None, 'text': text, 'confidence': None})
        if t['src']:
            turn_seg[t['src']] = len(segments) - 1
        merge_next = False

    def quote(turn, sel):
        text = portions[turn]
        if sel is None:
            q = text
        elif isinstance(sel, int):
            q = sentences(text)[sel]
        elif isinstance(sel, tuple):
            q = ' '.join(sentences(text)[sel[0]:sel[1] + 1])
        else:
            q = sel
        if q not in segments[turn_seg[turn]]['text']:
            raise SystemExit(f'call {n}: quote not on turn {turn}: {q!r}\n   line: {segments[turn_seg[turn]]["text"]!r}')
        return q, turn_seg[turn]

    # ------------------------------------------------------------------ recognition: applied rules and counts
    applied, grouped = [], {}
    cnt = {'plates': [0, 0], 'vins': [0, 0], 'order_numbers': [0, 0], 'part_numbers': [0, 0]}
    wrong = dict(names=0, first_names=0, terms=st['term_errors'], money=len(st['r5err']), phones=0)
    digits_pairs = phones_pairs = bursts = profanity = 0
    bad_line = False
    for t in turns:
        for pair in t['pairs']:
            a, b, rule = pair[0], pair[1], pair[2]
            what = pair[3] if len(pair) > 3 else None
            base = rule
            m = re.match(r'^R3(plate|order|vin|part)(\+?)$', rule)
            if m:
                base = 'R3' + m.group(2)
                kind = 'order_numbers' if m.group(1) == 'part' else R3KIND[m.group(1)]   # part numbers are counted with order numbers
                cnt[kind][0] += 1
                cnt[kind][1] += 0 if m.group(2) else 1
            error = base in ('R2', 'R2f', 'R3', 'R4', 'R5', 'R5p')
            wrong['names'] += base == 'R2'
            wrong['first_names'] += base == 'R2f'
            wrong['terms'] += base == 'R4'
            wrong['money'] += base == 'R5'
            wrong['phones'] += base == 'R5p'
            digits_pairs += base in ('R5', 'R5+')
            phones_pairs += base in ('R5p', 'R5p+')
            bursts += base in ('R6', 'R10')
            profanity += base == 'R11'
            bad_line = bad_line or base == 'R10'
            grouped.setdefault((base, what or RULE_WHAT[base], error), []).append((t['n'], a, b))
    order = ['R3', 'R3+', 'R2', 'R2f', 'R2+', 'R4', 'R4L', 'R5', 'R5p', 'R5+', 'R5p+', 'R6', 'R10', 'R11', 'R1']
    for key in sorted(grouped, key=lambda k: order.index(k[0]) if k[0] in order else 99):
        base, what, error = key
        rows = grouped[key]
        e = {'rule': {'R3+': 'R3', 'R2f': 'R2', 'R2+': 'R2', 'R4L': 'R4', 'R5p': 'R5', 'R5+': 'R5', 'R5p+': 'R5'}.get(base, base), 'what': what}
        if len(rows) == 1:
            e.update(script_turn=rows[0][0], said=rows[0][1], stored=rows[0][2])
        else:
            e.update(script_turns=[r[0] for r in rows], said=[r[1] for r in rows], stored=[r[2] for r in rows])
        e['error'] = error
        applied.append(e)
    if st['r5err']:
        applied.append({'rule': 'R5', 'what': 'a number split in two by the recogniser', 'script_turns': [x[0] for x in st['r5err']],
                        'said': [x[1] for x in st['r5err']], 'stored': [x[2] for x in st['r5err']], 'error': True})
    swaps = [t['n'] for t in turns if t['opts'].get('swap')]
    if swaps:
        applied.insert(0, {'rule': 'R8', 'what': call.get('swap_what', f'{len(swaps)} turns in a row carry the wrong speaker'), 'script_turns': swaps, 'error': True})
    ov_lost = [t['n'] for t in turns if t['opts'].get('bc') == 'lost']
    ov_joined = [t['n'] for t in turns if t['opts'].get('bc') == 'joined' or (t['opts'].get('overlap') and t['opts'].get('lost'))]
    ov_all = [t['n'] for t in turns if t['opts'].get('overlap')]
    if ov_lost:
        applied.append({'rule': 'R7', 'what': 'a backchannel said over the other speaker is lost', 'script_turns': ov_lost, 'error': False})
    if ov_joined:
        applied.append({'rule': 'R7', 'what': 'a backchannel said over the other speaker: the neighbouring turns of one speaker are stored as one line',
                        'script_turns': ov_joined, 'error': False})
    holds = [t for t in turns if 'hold' in t['opts']]
    if holds:
        e = {'rule': 'R9', 'what': call.get('hold_what', 'the hold'), 'script_turns': [t['n'] for t in holds], 'error': False}
        if any(t['opts']['hold'] for t in holds):
            e['stored'] = [t['opts']['hold'] for t in holds if t['opts']['hold']][0]
        applied.append(e)
    if auto['latin']:
        applied.append({'rule': 'R4', 'what': 'a make or model said in Russian comes out in Latin in some lines and in Cyrillic in others',
                        'script_turns': sorted({x[0] for x in auto['latin']}), 'said': [x[1] for x in auto['latin']],
                        'stored': [x[2] for x in auto['latin']], 'error': False})
    if auto['gazelle']:
        applied.append({'rule': 'R4', 'what': "'Газель' as a common noun, in lower case", 'script_turns': sorted({x[0] for x in auto['gazelle']}),
                        'said': 'Газель', 'stored': 'газель', 'error': True})
    if auto['hyphen']:
        applied.append({'rule': 'R2', 'what': "the company's name loses its hyphen", 'script_turns': sorted(auto['hyphen']),
                        'said': 'Ермак-Сервис', 'stored': 'Ермак Сервис', 'error': False})
    if auto['digits']:
        applied.append({'rule': 'R5', 'what': 'money, times, mileage and counts as digits', 'script_turns': sorted(auto['digits']), 'error': False})
    if auto['smooth'] or auto['fillers']:
        applied.append({'rule': 'R1', 'what': 'hesitations dropped, trailing-offs and exclamations smoothed, some opening fillers dropped',
                        'script_turns': sorted(auto['smooth'] | auto['fillers']), 'error': False})
    said_all = ' '.join(e['said'] for e in script if e['who'] != 'hold')
    stored_all = ' '.join(s['text'] for s in segments)
    names_n, firsts_n, hes_c, fill_c = count_mentions(said_all, stored_all, call.get('names', []) + ['Ермак'], more.FIRSTS.get(n, []))
    as_digits = st['digits'] + digits_pairs
    left = len(NUM_LEFT.findall(stored_all))
    counts = {
        'overlaps': {'said': len(ov_all), 'lost': len(ov_lost), 'joined': len(ov_joined)},
        'hesitations': {'said': hes_c[0], 'dropped': hes_c[1]}, 'fillers': {'said': fill_c[0], 'dropped': fill_c[1]},
        'names': {'mentions': max(names_n, wrong['names']), 'wrong': wrong['names']},
        'first_names': {'mentions': max(firsts_n, wrong['first_names']), 'wrong': wrong['first_names']},
        'plates': {'mentions': cnt['plates'][0], 'wrong': cnt['plates'][1]}, 'vins': {'mentions': cnt['vins'][0], 'wrong': cnt['vins'][1]},
        'order_numbers': {'mentions': cnt['order_numbers'][0], 'wrong': cnt['order_numbers'][1]},
        'part_numbers': {'mentions': cnt['part_numbers'][0], 'wrong': cnt['part_numbers'][1]},
        'trade_terms': {'mentions': len(TERM_RE.findall(said_all)), 'wrong': wrong['terms']},
        'script_choice': {'foreign_names': st['foreign'] + sum(1 for k in grouped if k[0] == 'R4L' for _ in grouped[k]),
                          'latin': st['latin'] + sum(1 for k in grouped if k[0] == 'R4L' for _ in grouped[k])},
        'money_time': {'mentions': as_digits + left, 'as_digits': as_digits, 'wrong': wrong['money']},
        'phones': {'mentions': st['phones'] + phones_pairs, 'wrong': wrong['phones']},
        'noise_bursts': bursts, 'speaker_swap_turns': len(swaps), 'hold': bool(holds), 'bad_line': bad_line,
        'profanity': profanity, 'invented_lines': 0,
        'lines_with_a_marker': sum(1 for s in segments if '{?likely' in s['text'] or '[unintelligible]' in s['text']),
    }
    sw, tw = cwords(said_all), cwords(stored_all)
    profile = call['profile']
    recognition = {'profile': profile, 'consensus_score': call['consensus'],
                   'restoration_tier': {'light': 'high', 'marked': 'medium', 'heavy': 'low'}[profile]}
    if call.get('noise'):
        recognition['noise'] = call['noise']
    recognition.update(applied=applied, counts=counts, script_words=len(sw), stored_words=len(tw),
                       strict_word_difference=round(lev(sw, tw) / len(sw), 3))

    c = dict(call['call'])
    c['talk_s'] = talk_s
    if c['direction'] == 'outbound':
        c['placed_from'] = c['answered_by']
        c['answered_by'] = None
    scenario = dict(call['scenario'])
    facts = dict(scenario.get('facts', {}))
    rows = price_rows(n, c['nominal_date'])
    if rows:
        facts['prices'] = rows
    if n in more.LEDGER:
        facts['ledger'] = more.LEDGER[n]
    scenario['facts'] = facts
    if call.get('unclear'):
        scenario['unclear'] = call['unclear']
    out = {'format': 'seed-call/1', 'id': f'ru-{n:02d}-{call["slug"]}', 'configuration': 'ru', 'number': n,
           'story': call['story'], 'title': call['title'], 'purpose': call['purpose'], 'cast': call['cast'], 'call': c,
           'scenario': scenario,
           'floating_days': [{'word': w, 'day': d, 'form': f} for w, d, f in call.get('floating', [])],
           'script': script, 'recognition': recognition,
           'transcript': {'engine': 'ensemble', 'engine_version': ENGINE_VERSION, 'language': 'ru', 'pii_state': 'raw',
                          'word_count': sum(len(s['text'].split()) for s in segments) + len(segments), 'duration_s': float(talk_s),
                          'segments': segments}}

    j = call.get('judge')
    facts_ = judge.CallFacts(direction=c['direction'], started_local=c['local_start'], line=c['line'], answered_by=str(c['answered_by']),
                             ring_s=c['ring_s'], talk_s=talk_s, repeat_caller=bool(c['repeat_caller']))
    if j is None:
        out['judge_answer'] = None
        out['verdict'] = {'kind': 'scorecard', 'score': None,
                          'result_public': {'scheme': 'scorecard', 'scorecard': CARD.version, 'weights': CARD.weights_version,
                                            'judged': False, 'direction': c['direction'], 'line': c['line'], 'checks': [], 'tags': [], 'media_version': 1},
                          'result_enc_plain': None}
        out['truth'] = call['truth']
        out['why'] = call['why']
    else:
        answer = {'call_type': j['call_type'], 'checks': [], 'na': [], 'auto_fails': []}
        for key in CHECK_KEYS:
            if key in j['checks']:
                level, turn, sel = j['checks'][key]
                q, seg = quote(turn, sel)
                answer['checks'].append({'key': key, 'quote': q, 'level': level, 'segment': seg})
        for key in CHECK_KEYS:
            if key in j.get('na', {}):
                answer['na'].append({'key': key, 'why': j['na'][key]})
        for key, (turn, sel) in j.get('auto_fails', {}).items():
            q, seg = quote(turn, sel)
            answer['auto_fails'].append({'key': key, 'quote': q, 'segment': seg})
        answer['outcome'] = j['outcome']
        answer['no_visit_reason'] = j.get('reason')
        answer['tags'] = j['tags']
        stt, ssel, swhy = j['strength']
        q, seg = quote(stt, ssel)
        answer['strength'] = {'quote': q, 'why': swhy, 'segment': seg}
        tcheck, (tt, tsel), tsay = j['try_next']
        q, _ = quote(tt, tsel)
        answer['try_next'] = {'check': tcheck, 'instead_of': q, 'say': tsay}
        answer['asr_quality'] = j.get('asr', 'ok')
        lines = [judge.Line(number=s['sequence'], role=s['speaker_label'], text=s['text']) for s in segments]
        v = judge.verdict(answer, lines, CARD, facts_)
        pub = v.public(CARD, line=facts_.line)
        pub['media_version'] = 1
        got = {ch['key']: ch['level'] for ch in pub['checks']}
        want = {k: lv[0] for k, lv in j['checks'].items()}
        if j['call_type'] == 'existing_job':
            want = {k: v_ for k, v_ in want.items() if CARD.check(k).applies == 'inbound'}
        if got != want:
            raise SystemExit(f'call {n}: the verdict keeps {got}, designed {want}; unverified {pub["unverified"]}')
        if j['call_type'] == 'new_enquiry' and set(pub['na']) != set(j.get('na', {})):
            raise SystemExit(f'call {n}: N/A differs: {pub["na"]} vs {list(j.get("na", {}))}')
        if len(pub['auto_fails']) != len(j.get('auto_fails', {})):
            raise SystemExit(f'call {n}: auto-fail quote not found')
        if v.strength is None or v.try_next is None:
            raise SystemExit(f'call {n}: strength or try_next dropped by the product ({v.strength}, {v.try_next})')
        out['judge_answer'] = answer
        out['verdict'] = {'kind': 'scorecard', 'score': v.score, 'result_public': pub, 'result_enc_plain': v.sealed()}
        levels = {k: (j['checks'][k][0] if k in j['checks'] else 'na') for k in CHECK_KEYS}
        if j['call_type'] == 'existing_job':
            levels = {k: (levels[k] if CARD.check(k).applies == 'inbound' else 'not_applicable') for k in CHECK_KEYS}
        if call.get('truth_levels'):
            levels.update(call['truth_levels'])
        tscore, _ = scorecard.score({k: lv for k, lv in levels.items() if isinstance(lv, int)}, CARD)
        out['truth'] = {'note': call.get('truth_note', 'Чистая речь даёт те же уровни: распознавание этому звонку ничего не стоило.'),
                        'levels': levels, 'score': tscore}
        scored = [(k, got[k]) for k in CHECK_KEYS if k in got]
        why = dict(call['why'])
        if v.score is not None:
            earned = sum(WEIGHTS[k] * lv for k, lv in scored) / 2
            total = sum(WEIGHTS[k] for k, _ in scored)
            exact = 100 * earned / total
            line = '(' + ' + '.join(f'{WEIGHTS[k]}·{lv}' for k, lv in scored) + f') / 2 = {earned:g} из {total} весовых баллов = {v.score}'
            if abs(exact * 100 - round(exact * 100)) < 1e-9 and abs(exact - v.score) > 1e-9:
                line += f' (точно {exact:g}; продукт хранит одну цифру после запятой)'
            why['score'] = line + '.'
        elif 'score' not in why:
            why['score'] = f'Оценки нет: применимых проверок {pub["applicable"]}, а для оценки нужно не меньше {scorecard.MIN_APPLICABLE}.'
        why['carried_by'] = call.get('carried_by', [])
        out['why'] = why
    for key in ('call_log', 'day_report'):
        if call.get(key):
            out[key] = call[key]
    out['new_facts'] = more.NEW_FACTS.get(n, []) + call.get('new_facts', [])
    if call.get('conflicts'):
        out['conflicts'] = call['conflicts']
    return out


def main():
    import importlib
    os.makedirs(OUT, exist_ok=True)
    only = set(map(int, [a for a in sys.argv[1:] if a.isdigit()]))
    calls = []
    for name in ('src_a', 'src_b', 'src_c', 'src_d', 'src_e'):
        calls += importlib.import_module(name).CALLS
    for call in calls:
        if only and call['n'] not in only:
            continue
        out = build(call)
        path = f'{OUT}/{call["n"]:02d}-{call["story"]}-{call["slug"]}.json'
        with open(path, 'w') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write('\n')
        r, cn = out['recognition'], out['recognition']['counts']
        rate = len(cwords(' '.join(e['said'] for e in out['script'] if e['who'] != 'hold'))) / max(1, out['call']['talk_s'] - sum(e.get('hold_s', 0) for e in out['script']))
        print(f'{call["n"]:02d} score {out["verdict"]["score"]} talk {out["call"]["talk_s"]}s turns {len(out["script"])} w/s {rate:.2f} '
              f'diff {r["strict_word_difference"]} {r["profile"]} bursts {cn["noise_bursts"]} ov {cn["overlaps"]} r5 {cn["money_time"]} terms {cn["trade_terms"]}')
        if os.environ.get('SHOW'):
            for s in out['transcript']['segments']:
                print(f'   [{s["sequence"]:2d}] {s["speaker_label"][:1]}: {s["text"]}')
            for e in r['applied']:
                if e['rule'] == 'R5' and e.get('error'):
                    print('   R5 errors:', e.get('said'), '->', e.get('stored'))


if __name__ == '__main__':
    main()
