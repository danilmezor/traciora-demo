# Writes the three missed-call records (18 to 20) and copies the four samples into calls/ru under their numbers.
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build
from build import SEED, OUT, TERM_RE, LATIN_RE, wordsof, lev

A5 = {'name': 'Рустем Ильгизович Фаттахов', 'company': 'Идель-Электромонтаж', 'account': 'A5', 'ref': 'accounts.json ru.A5 contacts[0]'}
MISSES = [
    (18, '2026-07-01', '09:40', '302', 1, 'phase B day: desk 303 is the advisor on duty, desk 302\'s advisor is off'),
    (19, '2026-07-06', '14:15', '303', 6, 'phase A day: desk 302 is the advisor on duty, desk 303\'s advisor is off'),
    (20, '2026-07-09', '17:30', '302', 9, 'phase B day: desk 303 is the advisor on duty, desk 302\'s advisor is off'),
]
for n, date, start, first, after, phase in MISSES:
    others = [e for e in ('301', '302', '303')]
    rec = {
        'format': 'seed-call/1', 'id': f'ru-{n}-a5-miss-{n - 17}', 'configuration': 'ru', 'number': n, 'story': 'S1',
        'title': f'The electricians\' manager rings again, {after} day{"s" if after > 1 else ""} after the complaint call; nobody answers',
        'purpose': 'Story S1, calls 18 to 20. After the complaint call (17) and the promise to call back, the same number rings the Kazan shop three times in nine days. Nobody answers and nobody calls back. The misses stay in state waiting; they are older than the queue\'s seven days, so they are on no screen and are found only by a query on the number.',
        'cast': {'customer': dict(A5, first_time=False)},
        'call': {'day': f'{after} calendar day{"s" if after > 1 else ""} after call 17 (rule R6; card S01; ledger s1.a5)',
                 'nominal_offset': None, 'nominal_date': date, 'local_start': start, 'site': 'west', 'direction': 'inbound',
                 'line': '620', 'answered_by': None, 'answered': False, 'disposition': 'no_answer',
                 'ring_s': 35, 'talk_s': 0, 'caller_phone': '+7 907 906-45-83', 'repeat_caller': n > 18,
                 'first_desk': first,
                 'legs': [{'extension': first, 'status': 'no_answer', 'ring_s': 20, 'stage': 'the first desk, 20 s'}]
                         + [{'extension': e, 'status': 'no_answer', 'ring_s': 15, 'stage': 'every desk, 15 s'} for e in others]},
        'missed_call': {'state': 'waiting', 'out_of_hours': False, 'attempts': 0, 'resolved_by': None, 'claim': None,
                        'dismissed': False, 'in_queue_at_t': False,
                        'why_not_in_queue': 'the To call back screen shows the last seven days; this miss is months old'},
        'script': None, 'transcript': None, 'judge_answer': None, 'verdict': None,
        'truth': {'note': 'Пропущенный звонок: записи, расшифровки и оценки нет. У пропущенного звонка нет человека, есть только столы, на которые он звонил.',
                  'what_happened': 'Звонок с номера Фаттахова прозвенел 20 секунд на первом столе и 15 секунд на всех трёх; никто не ответил, никто не перезвонил.'},
        'why': {'no_person': 'Вопрос S1.6 («кто из мастеров пропустил звонки») по данным не решается: можно назвать только первый стол и тех, кто был в смене.',
                'state': 'waiting навсегда: после звонка 17 с этим номером нет ни одного отвеченного звонка ни в одну сторону, иначе правило продукта закрыло бы пропущенные.'},
        'conflicts': [f'Roster against ledger for the nominal T: the ledger gives the first desk as {first} (s1.a5.miss_first_desks: 302, 303, 302), but on the nominal date the two-on, two-off rota (rule R12) has it the other way round ({phase}). The ledger\'s desk is kept; which desk rings first on a day its advisor is off is for the seeder\'s owner to settle.'],
    }
    import datetime as dt
    rec['call']['nominal_offset'] = f'T-{(dt.date(2026, 11, 13) - dt.date.fromisoformat(date)).days}d'
    with open(f'{OUT}/{n}-s1-a5-miss-{n - 17}.json', 'w') as f:
        json.dump(rec, f, ensure_ascii=False, indent=2); f.write('\n')
    print('miss', n)

SAMPLES = {
    1: ('ru-1-junior-early', 'S4', '01-s4-junior-early', ['Тарасов'], {}),
    6: ('ru-2-junior-now', 'S4', '06-s4-junior-now', ['Сафин', 'Московское шоссе'], {}),
    15: ('ru-3-weak-desk', 'S6', '15-s6-weak-desk', ['Гизатуллин'], {}),
    25: ('ru-4-good-call-damaged', 'S5', '25-s5-good-call-damaged', ['Тёплый контур', 'Верхнюю Террасу', 'Инженерн', 'Ильдус'], {}),
}
# (rule, index among the sample's entries of that rule) -> (error, error_count)
ERRORS = {
    1: {},
    6: {('R2', 0): (True, 1)},
    15: {('R2', 0): (True, 1)},
    25: {('R8', 0): (True, 1), ('R3', 0): (True, 2), ('R3', 1): (True, 1), ('R2', 0): (True, 3), ('R4', 0): (True, 5), ('R5', 0): (True, 1)},
}
MENT = {  # plates, order numbers, phones: [mentions, errors]
    1: {'phones': [1, 0]}, 6: {'phones': [1, 0]}, 15: {}, 25: {'plates': [3, 2], 'order_numbers': [2, 1]},
}
LATIN_STORED = {1: 0, 6: 1, 15: 1, 25: 1}
for n, (src, story, name, stems, _) in SAMPLES.items():
    d = json.load(open(f'{SEED}/calls/samples/{src}.json'))
    out = {}
    for k, v in d.items():
        out[k] = v
        if k == 'configuration':
            out['number'] = n; out['story'] = story; out['copied_from'] = f'calls/samples/{src}.json'
    out['id'] = f'ru-{name}'
    if n == 25:
        # an older plate was left in the script and in one note; the stored line already says 358
        for t in out['script']:
            if t['n'] == 9:
                assert t['said'].startswith('Четыреста семьдесят два о-ка')
                t['said'] = t['said'].replace('Четыреста семьдесят два о-ка', 'Триста пятьдесят восемь эн-е')
        for e in out['recognition']['applied']:
            if e['rule'] == 'R3' and 'окей' in e['what']:
                e['what'] = "the plate comes out three ways: right, with эн heard as эм, and with 'эн-е' heard as 'не'"
    seen = {}
    for e in out['recognition']['applied']:
        i = seen.get(e['rule'], 0); seen[e['rule']] = i + 1
        err, cnt = ERRORS[n].get((e['rule'], i), (False, 0))
        e['error'] = err
        if err and cnt != 1:
            e['error_count'] = cnt
    said = ' '.join(t['said'] for t in out['script'])
    stored = ' '.join(s['text'] for s in out['transcript']['segments'])
    m = {'names': [0, 0], 'plates': [0, 0], 'order_numbers': [0, 0], 'vins': [0, 0], 'part_numbers': [0, 0],
         'listed_terms': [0, 0], 'foreign_names': [0, 0], 'numbers': [0, 0], 'phones': [0, 0]}
    for stem in stems:
        m['names'][0] += len(re.findall(re.escape(stem), said, re.I))
    m['names'][1] = {1: 0, 6: 1, 15: 1, 25: 3}[n]
    m['listed_terms'] = [len(TERM_RE.findall(said)), 5 if n == 25 else 0]
    m['foreign_names'] = [len(LATIN_RE.findall(said)), LATIN_STORED[n]]
    m['numbers'] = [len(re.findall(r'\d+(?:[ :/,.-]\d+)*', stored)), 1 if n == 25 else 0]
    for k, v in MENT[n].items():
        m[k] = v
    rec = {}
    for k, v in out['recognition'].items():
        rec[k] = v
        if k == 'applied':
            rec['mentions'] = m
            rec['lines_with_a_marker'] = sum(1 for s in out['transcript']['segments'] if '{?likely' in s['text'] or '[unintelligible]' in s['text'])
    out['recognition'] = rec
    if n == 15:
        out['conflicts'] = ["Card S06 against the rota (rule R12): 'west's 4th full open day before T' is T-4d, and T-4d is always a phase-B day, on which slot 23 is off (roster.advisor_pattern: phase A works d mod 4 in {2, 3}). The card's anchor and the sample's weekday words are kept as approved; slot 23's nearest working day is T-5d. To be settled by the card's owner."]
    if n == 25:
        out['new_facts'] = ['Рамиль, сотрудник «Тёплого контура» (A2), который ведёт машины компании, телефон +7 907 471-16-40, и водитель Ильдус: оба придуманы для этого звонка, в accounts.json их нет.',
                            'Номер заявки клиента 118/11 на замену сцепления машины Т-17.']
    with open(f'{OUT}/{name}.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2); f.write('\n')
    sw, tw = wordsof(said), wordsof(stored)
    print('sample', n, name, 'words', len(sw), len(tw), 'lev', round(lev(sw, tw) / len(sw), 3), 'stated', out['recognition']['strict_word_difference'], m)
