# The three missed-call records (18 to 20) and the four samples copied into calls/ru under their numbers,
# brought to the shape checks/check_calls.py reads.
import datetime, json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build2 import SEED, OUT, TERM_RE, LATIN_RE, HES, FILL_COUNT, NUM_LEFT, cwords, lev, price_rows, count_mentions
import more

T0 = datetime.date(2026, 11, 13)
A5 = {'name': 'Рустем Ильгизович Фаттахов', 'company': 'Идель-Электромонтаж', 'account': 'A5', 'ref': 'accounts.json ru.A5 contacts[0]'}
MISSES = [
    (18, '2026-07-01', '09:40', '302', 1, 'a phase-B day: desk 303 has its advisor on duty, desk 302\'s advisor is off'),
    (19, '2026-07-06', '14:15', '303', 6, 'a phase-A day: desk 302 has its advisor on duty, desk 303\'s advisor is off'),
    (20, '2026-07-09', '17:30', '302', 9, 'a phase-B day: desk 303 has its advisor on duty, desk 302\'s advisor is off'),
]
for n, date, start, first, after, phase in MISSES:
    days = f'{after} calendar day{"s" if after > 1 else ""}'
    rec = {
        'format': 'seed-call/1', 'id': f'ru-{n}-a5-miss-{n - 17}', 'configuration': 'ru', 'number': n, 'story': 'S1',
        'title': f'The electricians\' manager rings again, {days} after the complaint call; nobody answers',
        'purpose': 'Story S1, calls 18 to 20. After the complaint call (17) and the promise to call back, the same number rings the Kazan shop three times in nine days. Nobody answers and nobody calls back. The misses stay in state waiting; they are older than the queue\'s seven days, so they are on no screen and are found only by a query on the number.',
        'cast': {'customer': dict(A5, first_time=False)},
        'call': {'day': f'{days} after call 17 (rule R6; card S01; ledger s1.a5)',
                 'nominal_offset': f'T-{(T0 - datetime.date.fromisoformat(date)).days}d', 'nominal_date': date, 'local_start': start, 'site': 'west',
                 'direction': 'inbound', 'line': '620', 'answered_by': None, 'answered': False, 'disposition': 'no_answer',
                 'ring_s': 35, 'talk_s': 0, 'caller_phone': '+7 907 906-45-83', 'repeat_caller': n > 18, 'first_desk': first,
                 'legs': [{'extension': first, 'status': 'no_answer', 'ring_s': 20, 'stage': 'the first desk, 20 s'}]
                         + [{'extension': e, 'status': 'no_answer', 'ring_s': 15, 'stage': 'every desk, 15 s'} for e in ('301', '302', '303')]},
        'missed_call': {'state': 'waiting', 'out_of_hours': False, 'attempts': 0, 'resolved_by': None, 'claim': None, 'dismissed': False,
                        'in_queue_at_t': False, 'why_not_in_queue': 'the To call back screen shows the last seven days; this miss is months old'},
        'scenario': {'who_calls': 'Рустем Ильгизович Фаттахов of account A5, waiting for the call back promised in call 17.',
                     'what_happens': 'The call rings the first desk for 20 seconds, then every desk for 15, and is not answered. Nobody calls the number back.'},
        'floating_days': [], 'script': None, 'recognition': None, 'transcript': None, 'judge_answer': None, 'verdict': None,
        'truth': {'note': 'Пропущенный звонок: записи, расшифровки и оценки нет. У пропущенного звонка нет человека, есть только столы, на которые он звонил.',
                  'what_happened': 'Звонок с номера Фаттахова прозвенел 20 секунд на первом столе и 15 секунд на всех трёх; никто не ответил, никто не перезвонил.'},
        'why': {'no_person': 'Вопрос S1.6 («кто из мастеров пропустил звонки») по данным не решается: можно назвать только первый стол и тех, кто был в смене.',
                'state': 'waiting навсегда: после звонка 17 с этим номером нет ни одного отвеченного звонка ни в одну сторону, иначе правило продукта закрыло бы пропущенные.',
                'carried_by': []},
        'new_facts': [],
        'conflicts': [f'Ledger against the rota for the nominal T: the ledger gives the first desk as {first} (s1.a5.miss_first_desks: 302, 303, 302), and on the nominal date it is {phase} (rule R12, roster.advisor_pattern). The ledger\'s desk is kept. Whether a desk rings first on a day its advisor is off is for the seeder\'s owner to settle.'],
    }
    with open(f'{OUT}/{n}-S1-a5-miss-{n - 17}.json', 'w') as f:
        json.dump(rec, f, ensure_ascii=False, indent=2); f.write('\n')

SAMPLES = {1: ('ru-1-junior-early', 'S4', '01-S4-junior-early', ['Тарасов']),
           6: ('ru-2-junior-now', 'S4', '06-S4-junior-now', ['Сафин', 'Московское шоссе']),
           15: ('ru-3-weak-desk', 'S6', '15-S6-weak-desk', ['Гизатуллин']),
           25: ('ru-4-good-call-damaged', 'S5', '25-S5-good-call-damaged', ['Тёплый контур', 'Верхнюю Террасу', 'Инженерн'])}
# (rule, index among the sample's entries of that rule) -> the entry is an error
ERRORS = {1: set(), 6: {('R2', 0)}, 15: {('R2', 0)}, 25: {('R8', 0), ('R3', 0), ('R3', 1), ('R2', 0), ('R4', 0), ('R5', 0)}}
FIX = {  # what cannot be counted from the text alone
    1: dict(names_wrong=0, first_wrong=0, latin=0, money_wrong=0, phones=(1, 0), bursts=0, joined=1, profanity=0),
    6: dict(names_wrong=1, first_wrong=0, latin=1, money_wrong=0, phones=(1, 0), bursts=0, joined=0, profanity=0),
    15: dict(names_wrong=1, first_wrong=0, latin=1, money_wrong=0, phones=(0, 0), bursts=0, joined=0, profanity=2),
    25: dict(names_wrong=2, first_wrong=1, latin=1, money_wrong=1, phones=(0, 0), bursts=4, joined=0, profanity=0, plates=(3, 2), orders=(2, 1), swap=3, term_wrong_extra=1),
}
for n, (src, story, name, stems) in SAMPLES.items():
    d = json.load(open(f'{SEED}/calls/samples/{src}.json'))
    out = {}
    for k, v in d.items():
        out[k] = v
        if k == 'configuration':
            out['number'] = n; out['story'] = story; out['copied_from'] = f'calls/samples/{src}.json'
    out['id'] = 'ru-' + name.replace('-S', '-s', 1).lower()
    changes = ['number, story, copied_from; scenario.facts.prices; recognition.counts and an error flag on each applied rule; word counts by the checker\'s word list; new_facts']
    if n == 25:
        for t in out['script']:
            if t['n'] == 9:
                assert t['said'].startswith('Четыреста семьдесят два о-ка')
                t['said'] = t['said'].replace('Четыреста семьдесят два о-ка', 'Триста пятьдесят восемь эн-е')
        for e in out['recognition']['applied']:
            if e['rule'] == 'R3' and 'окей' in e['what']:
                e['what'] = "the plate comes out three ways: right, with эн heard as эм, and with 'эн-е' heard as 'не'"
        changes.append('script turn 9 and the note of rule R3 still carried an older plate (472ОК); both now say Н358НЕ, as the stored line and accounts.json do')
    seen = {}
    for e in out['recognition']['applied']:
        i = seen.get(e['rule'], 0); seen[e['rule']] = i + 1
        e['error'] = (e['rule'], i) in ERRORS[n]
    said = ' '.join(t['said'] for t in out['script'])
    stored = ' '.join(s['text'] for s in out['transcript']['segments'])
    fx = FIX[n]
    names_n, firsts_n, hes_c, fill_c = count_mentions(said, stored, stems + ['Ермак'], more.FIRSTS[n])
    digits = len(re.findall(r'\d+(?:[ :/,.-]\d+)*', stored))
    left = len(NUM_LEFT.findall(stored))
    gaz = max(0, said.count('Газел') - stored.count('Газел'))
    counts = {
        'overlaps': {'said': sum(1 for t in out['script'] if t.get('overlap')), 'lost': 0, 'joined': fx['joined']},
        'hesitations': {'said': hes_c[0], 'dropped': hes_c[1]}, 'fillers': {'said': fill_c[0], 'dropped': fill_c[1]},
        'names': {'mentions': names_n, 'wrong': fx['names_wrong']}, 'first_names': {'mentions': firsts_n, 'wrong': fx['first_wrong']},
        'plates': {'mentions': fx.get('plates', (0, 0))[0], 'wrong': fx.get('plates', (0, 0))[1]}, 'vins': {'mentions': 0, 'wrong': 0},
        'order_numbers': {'mentions': fx.get('orders', (0, 0))[0], 'wrong': fx.get('orders', (0, 0))[1]},
        'part_numbers': {'mentions': 0, 'wrong': 0},
        'trade_terms': {'mentions': len(TERM_RE.findall(said)), 'wrong': gaz + fx.get('term_wrong_extra', 0)},
        'script_choice': {'foreign_names': len(LATIN_RE.findall(said)), 'latin': fx['latin']},
        'money_time': {'mentions': digits + left, 'as_digits': digits, 'wrong': fx['money_wrong']},
        'phones': {'mentions': fx['phones'][0], 'wrong': fx['phones'][1]},
        'noise_bursts': fx['bursts'], 'speaker_swap_turns': fx.get('swap', 0), 'hold': False, 'bad_line': False,
        'profanity': fx['profanity'], 'invented_lines': 0,
        'lines_with_a_marker': sum(1 for s in out['transcript']['segments'] if '{?likely' in s['text'] or '[unintelligible]' in s['text']),
    }
    sw, tw = cwords(said), cwords(stored)
    rec = {}
    for k, v in out['recognition'].items():
        if k in ('script_words', 'stored_words', 'strict_word_difference'):
            continue
        rec[k] = v
        if k == 'applied':
            rec['counts'] = counts
    rec.update(script_words=len(sw), stored_words=len(tw), strict_word_difference=round(lev(sw, tw) / len(sw), 3))
    out['recognition'] = rec
    out['transcript']['word_count'] = sum(len(s['text'].split()) for s in out['transcript']['segments']) + len(out['transcript']['segments'])
    rows = price_rows(n, out['call']['nominal_date'])
    out['scenario']['facts']['prices'] = rows
    out['new_facts'] = []
    if n == 15:
        out['conflicts'] = ["Card S06 against the rota (rule R12): 'west's 4th full open day before T' is T-4d, and T-4d is a phase-B day for every T, on which slot 23 is off (roster.advisor_pattern: phase A works d mod 4 in {2, 3}). The card's anchor and the sample's weekday words are kept as approved. Slot 23's nearest working day is T-5d; moving the call there shifts every weekday word by one. To be settled by the card's owner."]
    if n == 25:
        out['new_facts'] = ['Рамиль, сотрудник «Тёплого контура» (A2), который ведёт машины компании, телефон +7 907 471-16-40, и водитель Ильдус: оба придуманы для этого звонка, в accounts.json их нет.',
                            'Номер заявки клиента 118/11 на замену сцепления машины Т-17; запись на следующий день, 9:00.']
    out['changes_against_the_sample'] = changes
    with open(f'{OUT}/{name}.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2); f.write('\n')
    print('sample', n, name, len(sw), len(tw), rec['strict_word_difference'], counts['money_time'], counts['fillers'], counts['trade_terms'], counts['names'], counts['first_names'])
