# Builder for the Russian story calls (scratch tool; the JSON files it writes are the deliverable).
# Run with the product's interpreter: PYTHONPATH=<repo>/apps/backend/src <repo>/.venv/bin/python build.py
import hashlib, json, math, os, re, sys

SEED = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REPO = os.path.join(os.path.dirname(os.path.dirname(SEED)), 'traciora')
OUT = SEED + '/calls/ru'
from traciora.core.phonecalls import judge, scorecard  # read-only import of the product's scoring code

CARD = scorecard.parse(json.load(open(REPO + '/config/defaults/phonecalls_scorecard.json')))
WEIGHTS = {c.key: c.weight for c in CARD.checks}
CHECK_KEYS = [c.key for c in CARD.checks]
ENGINE_VERSION = ('tone+gigaam|tone=106f3b0b32a9e107eb613312e4ebc61ff3d53926|'
                  'gigaam=7655ad717f8122257385bb4b2f373db3697e8680|restore=<restoration fingerprint, computed at seed time>')

# ----------------------------------------------------------------------------- numerals
UNITS = {'ноль': 0, 'один': 1, 'одна': 1, 'одну': 1, 'одно': 1, 'два': 2, 'две': 2, 'три': 3, 'четыре': 4, 'пять': 5,
         'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9}
TEENS = {'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
         'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19}
TENS = {'двадцать': 20, 'тридцать': 30, 'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семьдесят': 70,
        'восемьдесят': 80, 'девяносто': 90}
HUND = {'сто': 100, 'двести': 200, 'триста': 300, 'четыреста': 400, 'пятьсот': 500, 'шестьсот': 600, 'семьсот': 700,
        'восемьсот': 800, 'девятьсот': 900}
THOU = {'тысяча', 'тысячи', 'тысяч', 'тысячу'}
ONES = {'один', 'одна', 'одну', 'одно'}
NUMWORD = set(UNITS) | set(TEENS) | set(TENS) | set(HUND) | THOU
TIME_PREPS = {'в', 'к', 'на', 'до', 'с', 'после', 'около'}
ORDINAL = re.compile(r'^(перв|втор|трет|четв[её]рт|пят|шест|седьм|восьм|девят|десят|\w+надцат|двадцат|тридцат|сороков|'
                     r'пятидесят|сот)(ый|ой|ого|ому|ым|ом|ая|ую|ое|ые|ых|ыми|ье|ья|ьего|ий|ьей|ью|ьем)$')
WORD = re.compile(r'[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*')


def fmt(n):
    return f'{n:,}'.replace(',', ' ') if n >= 10000 else str(n)


def parse_group(toks, i):
    """One number group starting at toks[i]: (value, next index, digit) or None."""
    start, val = i, 0
    if i < len(toks) and toks[i] in HUND:
        val += HUND[toks[i]]; i += 1
    if i < len(toks) and toks[i] in TEENS:
        val += TEENS[toks[i]]; i += 1
    elif i < len(toks) and toks[i] in TENS:
        val += TENS[toks[i]]; i += 1
        if i < len(toks) and toks[i] in UNITS and toks[i] != 'ноль':
            val += UNITS[toks[i]]; i += 1
    elif i < len(toks) and toks[i] in UNITS:
        val += UNITS[toks[i]]; i += 1
    if i == start:
        return None
    return val, i, (i - start == 1 and toks[start] in UNITS)


def render_run(toks, prev_word):
    """Digits for a run of numeral words, or None when the run stays as words."""
    if toks[0] in ('тысяч', 'тысячи'):
        return None
    if len(toks) == 1:
        t = toks[0]
        if t in TEENS or t in TENS or t in HUND:
            return str((TEENS.get(t) or TENS.get(t) or HUND.get(t)))
        return None
    if toks[0] in ONES and toks[1] not in THOU:
        return None
    groups, i = [], 0
    while i < len(toks):
        if toks[i] in THOU:
            if toks[i] in ('тысяча', 'тысячу'):
                val, i = 1000, i + 1
                g = parse_group(toks, i)
                if g:
                    val += g[0]; i = g[1]
                groups.append((val, False))
                continue
            return None
        g = parse_group(toks, i)
        if g is None:
            return None
        val, i, digit = g
        if i < len(toks) and toks[i] in THOU:
            val *= 1000; i += 1; digit = False
            g2 = parse_group(toks, i)
            if g2:
                val += g2[0]; i = g2[1]
        groups.append((val, digit))
    if len(groups) == 1:
        return fmt(groups[0][0])
    if all(d for _, d in groups):
        return ''.join(str(v) for v, _ in groups)
    if len(groups) == 2:
        (a, da), (b, db) = groups
        if 1 <= a < 1000 and 100 <= b <= 999:
            return fmt(a * 1000 + b)
        if prev_word in TIME_PREPS and a <= 23 and b < 60 and not db:
            return f'{a}:{b:02d}'
    out, digits = [], ''
    for v, d in groups:
        if d:
            digits += str(v)
        else:
            if digits:
                out.append(digits); digits = ''
            out.append(str(v))
    if digits:
        out.append(digits)
    return ' '.join(out)


def to_digits(text, stats):
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
            out.append(text[pos:s]); out.append(rendered); pos = words[run[-1]][1]
            stats['digits'] += 1
        else:
            stats['words'] += 1
        k = run[-1] + 1
    out.append(text[pos:])
    res = ''.join(out)
    res, n = re.subn(r'\b(\d{3}), (\d{3}), (\d{2}), (\d{2})\b', r'\1 \2 \3 \4', res)
    stats['phones'] += n
    return res


# ----------------------------------------------------------------------------- script choice and term lists
LATIN = {'Киа Рио': 'Kia Rio', 'Киа Сид': 'Kia Ceed', 'Рено Логан': 'Renault Logan', 'Рено Дастер': 'Renault Duster',
         'Рено Сандеро': 'Renault Sandero', 'Форд Транзит': 'Ford Transit', 'Тойота Королла': 'Toyota Corolla',
         'Тойота Камри': 'Toyota Camry', 'Ниссан Кашкай': 'Nissan Qashqai', 'Ниссан Альмера': 'Nissan Almera',
         'Шевроле Круз': 'Chevrolet Cruze', 'Шевроле Лачетти': 'Chevrolet Lacetti', 'Шкода Рапид': 'Skoda Rapid',
         'Митсубиси Лансер': 'Mitsubishi Lancer', 'Фольксваген Поло': 'Volkswagen Polo', 'Хавал Джолион': 'Haval Jolion',
         'Лада Веста': 'Lada Vesta', 'Лада Гранта': 'Lada Granta', 'Лада Приора': 'Lada Priora',
         'Солярис': 'Solaris', 'Логан': 'Logan', 'Дастер': 'Duster', 'Сандеро': 'Sandero', 'Транзит': 'Transit',
         'Королла': 'Corolla', 'Камри': 'Camry', 'Кашкай': 'Qashqai', 'Альмера': 'Almera', 'Круз': 'Cruze',
         'Лачетти': 'Lacetti', 'Рапид': 'Rapid', 'Лансер': 'Lancer', 'Поло': 'Polo', 'Джолион': 'Jolion',
         'Хавал': 'Haval', 'Сид': 'Ceed', 'Рио': 'Rio', 'Некст': 'Next', 'Пежо': 'Peugeot', 'Веста': 'Vesta',
         'Гранта': 'Granta', 'Мазда': 'Mazda', 'Ларгус': 'Largus', 'Приора': 'Priora', 'Октавия': 'Octavia'}
LADA = {'Веста', 'Гранта', 'Ларгус', 'Приора', 'Лада Веста', 'Лада Гранта', 'Лада Приора'}
LATIN_KEYS = sorted(LATIN, key=len, reverse=True)
LATIN_RE = re.compile(r'(?<![А-Яа-яЁё-])(' + '|'.join(map(re.escape, LATIN_KEYS)) + r')(?![А-Яа-яЁё-])')
# trade words, makes and models counted as 'listed terms' (stems, matched case-insensitively at a word start)
TERM_STEMS = ['газел', 'солярис', 'логан', 'дастер', 'сандеро', 'транзит', 'королл', 'камри', 'кашка', 'альмер', 'круз',
              'лачетти', 'рапид', 'лансер', 'поло', 'джолион', 'хавал', 'сид', 'рио', 'некст', 'пежо', 'вест', 'грант',
              'ларгус', 'приор', 'октави', 'мазд', 'киа', 'рено', 'форд', 'тойот', 'ниссан', 'шевроле', 'шкод', 'митсубиси',
              'фольксваген', 'колодк', 'диск', 'суппорт', 'шаров', 'шрус', 'гранат', 'ступи', 'подшипник', 'стойк',
              'стабилизатор', 'амортизатор', 'сход-развал', 'развал', 'грм', 'ремен', 'ремн', 'помп', 'ролик',
              'термостат', 'антифриз', 'аккумулятор', 'свеч', 'сцеплени', 'маховик', 'насос', 'рейк', 'люфт', 'наряд',
              'нормо-час', 'дефектовк', 'шиномонтаж', 'балансировк', 'кондиционер', 'фреон', 'генератор', 'защит',
              'bremhof', 'бремхоф', 'эвакуатор', 'тормозн', 'диагностик', 'чек']
TERM_RE = re.compile(r'(?<![А-Яа-яЁёA-Za-z])(' + '|'.join(map(re.escape, TERM_STEMS)) + r')', re.I)


def chance(*key):
    return int(hashlib.md5(':'.join(map(str, key)).encode()).hexdigest()[:8], 16) % 100


# ----------------------------------------------------------------------------- one line through recognition
HES = re.compile(r'(?<![А-Яа-яЁё-])(?:[Ээ]-э(?:-э)*|[Мм]-м(?:-м)*|[Ээ]м+)(?![А-Яа-яЁё-])[,.…]*\s*')


def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip()
    for _ in range(3):
        s = re.sub(r'\s+([,.?!:;])', r'\1', s)
        s = re.sub(r',\s*,', ',', s)
        s = re.sub(r',\s*([.?!])', r'\1', s)
        s = re.sub(r'([.?!])\s*,\s*', r'\1 ', s)
        s = re.sub(r'\.\s*\.', '.', s)
        s = re.sub(r'^[,.;:]\s*', '', s)
    s = re.sub(r'([.?!]\s+)([а-яё])', lambda m: m.group(1) + m.group(2).upper(), s)
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def store_line(call, turn, said, pairs, stats, auto):
    s, held = said, []
    for pair in pairs:
        a, b = pair[0], pair[1]
        if a not in s:
            raise SystemExit(f'call {call["n"]} turn {turn}: fragment not in the line: {a!r}')
        s = s.replace(a, f'\x00{len(held)}\x00', 1)
        held.append(b)
    before = s
    if 'Ермак-Сервис' in s:
        s = s.replace('Ермак-Сервис', 'Ермак Сервис'); auto['hyphen'].add(turn)
    s2 = HES.sub('', s)
    s2 = re.sub(r'\?\.\.', '?', s2)
    s2 = re.sub(r'!\.\.', '.', s2)
    s2 = re.sub(r'^(?:\.\.\.|…)\s*', '', s2)
    s2 = re.sub(r'(?:\.\.\.|…)\s+(?=[А-ЯЁA-Z\x00«\d])', '. ', s2)
    s2 = re.sub(r'(?:\.\.\.|…)\s+', ', ', s2)
    s2 = re.sub(r'(?:\.\.\.|…)$', '.', s2)
    s2 = re.sub(r'(?<=[,.?!:])\s+—\s+', ' ', s2)
    s2 = re.sub(r'\s+—\s+', ' \x01 ', s2)
    s2 = s2.replace('!', '.')
    if s2.replace(' \x01 ', ' — ') != s:
        auto['smooth'].add(turn)
    s = s2

    def latin(m):
        word = m.group(1)
        stats['foreign'] += 1
        limit = 25 if word in LADA else 55
        if chance(call['n'], turn, word, m.start()) < limit:
            stats['latin'] += 1
            auto['latin'].append((turn, word, LATIN[word]))
            return LATIN[word]
        return word
    s = LATIN_RE.sub(latin, s)
    if call.get('gazelle_lower') and 'Газел' in s:
        cnt = s.count('Газел')
        s = s.replace('Газел', 'газел'); auto['gazelle'].append((turn, cnt)); stats['term_errors'] += cnt
    d0 = stats['digits']
    s = to_digits(s, stats)
    if stats['digits'] != d0:
        auto['digits'].add(turn)
    for i, b in enumerate(held):
        s = s.replace(f'\x00{i}\x00', b)
    s = re.sub(r' \x01 (?=\d)', ' — ', s)
    s = s.replace(' \x01 ', ', ')
    return tidy(s)


def sentences(text):
    return [p for p in re.split(r'(?<=[.?!])\s+', text) if p]


def wordsof(text):
    return re.findall(r'[\w]+(?:-[\w]+)*', text.lower())


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


RULE_WHAT = {
    'R1': 'small particles dropped and word-form slips of the kind recognition makes',
    'R2': 'a name heard as a neighbour in sound',
    'R3': 'a spelled string: one character swapped, dropped or regrouped',
    'R3+': 'a spelled string rendered right',
    'R4': 'a trade word or a model heard as a common word that sounds alike',
    'R4L': 'a name said in Russian comes out in Latin',
    'R5': 'a number split, merged or changed',
    'R5+': 'numbers as digits; no value is wrong',
    'R5p': 'the phone number loses or changes a digit',
    'R5p+': 'the phone number as digits, right',
    'R6': 'noise: words lost, marked as uncertain or replaced',
    'R9': 'the hold',
    'R10': 'a bad mobile line: the sentence end clipped',
    'R11': 'the caller\'s profanity',
}
R3KIND = {'plate': 'plates', 'order': 'order_numbers', 'vin': 'vins', 'part': 'part_numbers'}


def build(call):
    n = call['n']
    stats = dict(digits=0, words=0, phones=0, foreign=0, latin=0, term_errors=0)
    auto = dict(hyphen=set(), smooth=set(), latin=[], gazelle=[], digits=set())
    script, portions, applied_pairs = [], {}, []
    t, prev_end = 0.0, 0.0
    turns = []
    for idx, row in enumerate(call['script'], 1):
        who, said = row[0], row[1]
        pairs = row[2] if len(row) > 2 and row[2] else []
        opts = row[3] if len(row) > 3 else {}
        turns.append((idx, who, said, pairs, opts))
    for idx, who, said, pairs, opts in turns:
        nw = len(wordsof(said))
        dur = max(1.0, nw / 1.9)
        gap = 0.5 + chance(n, idx, 'gap') % 10 / 10
        if said.startswith('...') or said.startswith('…'):
            gap += 1.4
        gap += opts.get('pause', 0)
        start = max(0.0, prev_end - 0.7) if opts.get('overlap') else prev_end + (gap if idx > 1 else 0)
        entry = {'n': idx, 'who': {'a': 'advisor', 'c': 'customer', 'h': 'hold'}[who], 'at_s': round(start, 1), 'said': said}
        if opts.get('overlap'):
            entry['overlap'] = True
        script.append(entry)
        prev_end = max(prev_end, start + dur)
        if 'hold' in opts:
            portions[idx] = opts['hold']
        elif opts.get('lost'):
            portions[idx] = None
        else:
            portions[idx] = store_line(call, idx, said, pairs, stats, auto)
        for pair in pairs:
            applied_pairs.append((idx, pair))
    talk_s = int(math.ceil(prev_end + 0.8))

    # segments: a lost backchannel joins its neighbours; a swap flips the label
    segments, turn_seg = [], {}
    pending_merge = False
    for idx, who, said, pairs, opts in turns:
        text = portions[idx]
        if text is None:
            pending_merge = True
            continue
        if text == '':
            continue
        label = 'customer' if who == 'c' else 'manager'
        if opts.get('swap'):
            label = 'customer' if label == 'manager' else 'manager'
        if (pending_merge or opts.get('join')) and segments and segments[-1]['speaker_label'] == label:
            segments[-1]['text'] += ' ' + text
            turn_seg[idx] = len(segments) - 1
        else:
            segments.append({'sequence': len(segments), 'speaker_label': label, 'start_ms': None, 'end_ms': None,
                             'text': text, 'confidence': None})
            turn_seg[idx] = len(segments) - 1
        pending_merge = False

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
            if q not in text:
                raise SystemExit(f'call {n}: quote not on turn {turn}: {q!r}\n   line: {text!r}')
        return q, turn_seg[turn]

    # recognition block
    applied, grouped = [], {}
    mentions = {'names': [0, 0], 'plates': [0, 0], 'order_numbers': [0, 0], 'vins': [0, 0], 'part_numbers': [0, 0],
                'listed_terms': [0, 0], 'foreign_names': [0, 0], 'numbers': [0, 0], 'phones': [0, 0]}
    for turn, pair in applied_pairs:
        a, b, rule = pair[0], pair[1], pair[2]
        what = pair[3] if len(pair) > 3 else None
        base, kind = rule, None
        m = re.match(r'^R3(plate|order|vin|part)(\+?)$', rule)
        if m:
            kind, base = R3KIND[m.group(1)], 'R3' + m.group(2)
            mentions[kind][0] += 1
            mentions[kind][1] += 0 if m.group(2) else 1
        error = base in ('R2', 'R3', 'R4', 'R5', 'R5p')
        if base == 'R2':
            mentions['names'][1] += 1
        if base == 'R4':
            mentions['listed_terms'][1] += 1
        if base in ('R5', 'R5+'):
            mentions['numbers'][0] += 1
            mentions['numbers'][1] += 1 if base == 'R5' else 0
        if base in ('R5p', 'R5p+'):
            mentions['phones'][0] += 1
            mentions['phones'][1] += 1 if base == 'R5p' else 0
        if base == 'R4L':
            mentions['foreign_names'][0] += 1; mentions['foreign_names'][1] += 1
        key = (base, what or RULE_WHAT[base], error)
        grouped.setdefault(key, []).append((turn, a, b))
    order = ['R8', 'R3', 'R3+', 'R2', 'R4', 'R4L', 'R5', 'R5p', 'R5+', 'R5p+', 'R6', 'R10', 'R11', 'R9', 'R1']
    for key in sorted(grouped, key=lambda k: (order.index(k[0]) if k[0] in order else 99)):
        base, what, error = key
        rows = grouped[key]
        e = {'rule': base.rstrip('+').replace('R4L', 'R4').replace('R5p', 'R5'), 'what': what}
        if len(rows) == 1:
            e.update(script_turn=rows[0][0], said=rows[0][1], stored=rows[0][2])
        else:
            e.update(script_turns=[r[0] for r in rows], said=[r[1] for r in rows], stored=[r[2] for r in rows])
        e['error'] = error
        applied.append(e)
    swaps = [idx for idx, who, said, pairs, opts in turns if opts.get('swap')]
    if swaps:
        applied.insert(0, {'rule': 'R8', 'what': call.get('swap_what', f'{len(swaps)} turns in a row carry the wrong speaker'),
                           'script_turns': swaps, 'error': True})
    lost = [idx for idx, who, said, pairs, opts in turns if opts.get('lost')]
    joined = [idx for idx, who, said, pairs, opts in turns if opts.get('join')]
    if lost:
        applied.append({'rule': 'R7', 'what': 'a backchannel said over the other speaker is lost and the turns around it become one line',
                        'script_turns': lost, 'error': False})
    if joined:
        applied.append({'rule': 'R7', 'what': 'two turns of one speaker joined into one line', 'script_turns': joined, 'error': False})
    holds = [idx for idx, who, said, pairs, opts in turns if 'hold' in opts]
    if holds:
        applied.append({'rule': 'R9', 'what': call.get('hold_what', 'the hold: the message under the manager\'s label'),
                        'script_turns': holds, 'error': False})
    if auto['latin']:
        applied.append({'rule': 'R4', 'what': 'a make or model said in Russian comes out in Latin in some lines and in Cyrillic in others',
                        'script_turns': sorted({x[0] for x in auto['latin']}), 'said': [x[1] for x in auto['latin']],
                        'stored': [x[2] for x in auto['latin']], 'error': False})
    if auto['gazelle']:
        applied.append({'rule': 'R4', 'what': "'Газель' as a common noun, in lower case",
                        'script_turns': sorted({x[0] for x in auto['gazelle']}), 'said': 'Газель', 'stored': 'газель', 'error': True})
    if auto['hyphen']:
        applied.append({'rule': 'R2', 'what': "the company's name loses its hyphen", 'script_turns': sorted(auto['hyphen']),
                        'said': 'Ермак-Сервис', 'stored': 'Ермак Сервис', 'error': False})
    if auto['digits']:
        applied.append({'rule': 'R5', 'what': 'money, times, mileage and counts as digits; no value is wrong',
                        'script_turns': sorted(auto['digits']), 'error': False})
    if auto['smooth']:
        applied.append({'rule': 'R1', 'what': 'hesitations, trailing-offs and exclamations smoothed',
                        'script_turns': sorted(auto['smooth']), 'error': False})
    said_all = ' '.join(e['said'] for e in script)
    stored_all = ' '.join(s['text'] for s in segments)
    for stem in call.get('names', []):
        mentions['names'][0] += len(re.findall(re.escape(stem), said_all, re.I))
    mentions['listed_terms'][0] = len(TERM_RE.findall(said_all))
    mentions['listed_terms'][1] += stats['term_errors']
    mentions['foreign_names'][0] += stats['foreign']; mentions['foreign_names'][1] += stats['latin']
    mentions['numbers'][0] += stats['digits']
    mentions['phones'][0] += stats['phones']
    sw, tw = wordsof(said_all), wordsof(stored_all)
    markers = sum(1 for s in segments if '{?likely' in s['text'] or '[unintelligible]' in s['text'])
    profile = call['profile']
    recognition = {'profile': profile, 'consensus_score': call['consensus'],
                   'restoration_tier': {'light': 'high', 'marked': 'medium', 'heavy': 'low'}[profile]}
    if call.get('noise'):
        recognition['noise'] = call['noise']
    recognition.update(applied=applied, mentions=mentions, lines_with_a_marker=markers, script_words=len(sw),
                       stored_words=len(tw), strict_word_difference=round(lev(sw, tw) / len(sw), 3))

    c = dict(call['call'])
    c['talk_s'] = talk_s
    out = {'format': 'seed-call/1', 'id': f'ru-{n:02d}-{call["slug"]}', 'configuration': 'ru', 'number': n,
           'story': call['story'], 'title': call['title'], 'purpose': call['purpose'], 'cast': call['cast'], 'call': c,
           'scenario': call['scenario'],
           'floating_days': [{'word': w, 'day': d, 'form': f} for w, d, f in call.get('floating', [])],
           'script': script, 'recognition': recognition,
           'transcript': {'engine': 'ensemble', 'engine_version': ENGINE_VERSION, 'language': 'ru', 'pii_state': 'raw',
                          'word_count': len(tw) + len(segments), 'duration_s': float(talk_s), 'segments': segments}}
    if call.get('unclear'):
        out['unclear'] = call['unclear']

    j = call.get('judge')
    facts = judge.CallFacts(direction=c['direction'], started_local=c['local_start'], line=c['line'],
                            answered_by=c['answered_by'], ring_s=c['ring_s'], talk_s=talk_s,
                            repeat_caller=c['repeat_caller'])
    if j is None:
        out['judge_answer'] = None
        out['verdict'] = {'kind': 'scorecard', 'score': None,
                          'result_public': {'scheme': 'scorecard', 'scorecard': CARD.version, 'weights': CARD.weights_version,
                                            'judged': False, 'direction': c['direction'], 'line': c['line'], 'checks': [],
                                            'tags': [], 'media_version': 1},
                          'result_enc_plain': None}
        out['truth'] = call['truth']
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
        st, ssel, swhy = j['strength']
        q, seg = quote(st, ssel)
        answer['strength'] = {'quote': q, 'why': swhy, 'segment': seg}
        tcheck, (tt, tsel), tsay = j['try_next']
        q, _ = quote(tt, tsel)
        answer['try_next'] = {'check': tcheck, 'instead_of': q, 'say': tsay}
        answer['asr_quality'] = j.get('asr', 'ok')
        lines = [judge.Line(number=s['sequence'], role=s['speaker_label'], text=s['text']) for s in segments]
        v = judge.verdict(answer, lines, CARD, facts)
        pub = v.public(CARD, line=facts.line)
        pub['media_version'] = 1
        # every designed level must have survived the product's quote check
        got = {ch['key']: ch['level'] for ch in pub['checks']}
        want = {k: lv[0] for k, lv in j['checks'].items() if k not in j.get('unverified', [])}
        if j['call_type'] == 'existing_job':
            want = {k: v_ for k, v_ in want.items() if CARD.check(k).applies == 'inbound'}
        if got != want:
            raise SystemExit(f'call {n}: the verdict keeps {got}, designed {want}; unverified {pub["unverified"]}')
        if set(pub['na']) != set(j.get('na', {})) and j['call_type'] == 'new_enquiry':
            raise SystemExit(f'call {n}: N/A differs: {pub["na"]} vs {list(j.get("na", {}))}')
        if len(pub['auto_fails']) != len(j.get('auto_fails', {})):
            raise SystemExit(f'call {n}: auto-fail quote not found')
        if v.strength is None or (v.try_next is None and pub['score'] is not None):
            raise SystemExit(f'call {n}: strength or try_next dropped by the product ({v.strength}, {v.try_next})')
        out['judge_answer'] = answer
        out['verdict'] = {'kind': 'scorecard', 'score': v.score, 'result_public': pub, 'result_enc_plain': v.sealed()}
        tl = call.get('truth_levels')
        levels = {k: (j['checks'][k][0] if k in j['checks'] else 'na') for k in CHECK_KEYS}
        if j['call_type'] == 'existing_job':
            levels = {k: (levels[k] if CARD.check(k).applies == 'inbound' else 'not_applicable') for k in CHECK_KEYS}
        if tl:
            levels.update(tl)
        tscore, _ = scorecard.score({k: lv for k, lv in levels.items() if isinstance(lv, int)}, CARD)
        out['truth'] = {'note': call.get('truth_note', 'Чистая речь даёт те же уровни: распознавание этому звонку ничего не стоило.'),
                        'levels': levels, 'score': tscore}
        if call.get('truth_extra'):
            out['truth'].update(call['truth_extra'])
        # the score line of `why`
        scored = [(k, lv) for k, lv in ((k, got.get(k)) for k in CHECK_KEYS) if lv is not None]
        why = dict(call['why'])
        if v.score is not None:
            earned = sum(WEIGHTS[k] * lv for k, lv in scored) / 2
            total = sum(WEIGHTS[k] for k, _ in scored)
            exact = 100 * earned / total
            line = ('(' + ' + '.join(f'{WEIGHTS[k]}·{lv}' for k, lv in scored) + f') / 2 = {earned:g} из {total} весовых баллов = {v.score}')
            if abs(round(exact, 1) - v.score) > 1e-9 or abs(exact * 100 - round(exact * 100)) < 1e-9 and abs(exact - v.score) > 1e-9:
                line += f' (точно {exact:g}; продукт округляет до десятых)'
            why['score'] = line + '.'
        else:
            why['score'] = f'Оценки нет: применимых проверок {pub["applicable"]}, а для оценки нужно не меньше {scorecard.MIN_APPLICABLE}.'
        why['carried_by'] = call.get('carried_by', [])
        out['why'] = why
    if j is None:
        out['why'] = call['why']
    for key in ('call_log', 'day_report', 'new_facts', 'conflicts'):
        if call.get(key):
            out[key] = call[key]
    return out


def main():
    import importlib
    os.makedirs(OUT, exist_ok=True)
    only = set(map(int, sys.argv[1:]))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    calls = []
    for name in ('src_a', 'src_b', 'src_c', 'src_d', 'src_e', 'src_f'):
        try:
            calls += importlib.import_module(name).CALLS
        except ModuleNotFoundError:
            pass
    for call in calls:
        if only and call['n'] not in only:
            continue
        out = build(call)
        path = f'{OUT}/{call["n"]:02d}-{call["story"].lower()}-{call["slug"]}.json'
        with open(path, 'w') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
            f.write('\n')
        v = out['verdict']
        print(f'{call["n"]:02d} {out["id"]}: score {v["score"]} talk {out["call"]["talk_s"]}s turns {len(out["script"])} '
              f'diff {out["recognition"]["strict_word_difference"]} {out["recognition"]["profile"]}')
        if os.environ.get('SHOW'):
            for s in out['transcript']['segments']:
                print(f'   [{s["sequence"]:2d}] {s["speaker_label"][:1]}: {s["text"]}')


if __name__ == '__main__':
    main()
