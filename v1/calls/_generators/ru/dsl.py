def a(s, *p, **o): return ('a', s, list(p), o)
def c(s, *p, **o): return ('c', s, list(p), o)
def h(s, stored='', pause=20): return ('h', s, [], {'hold': stored, 'pause': pause})
ALINA = {'slot': 6, 'name': 'Алина Хасанова', 'fixed': True}
DMITRY = {'slot': 5, 'name': 'Дмитрий Григорьев', 'fixed': True}
NIKITA = {'slot': 7, 'name': 'Никита Ведяшкин', 'fixed': True}
SVETLANA = {'slot': 16, 'name': 'Светлана Юрьевна Демидова', 'fixed': True}
ARTEM = {'slot': 17, 'name': 'Артём Николаев', 'fixed': True}
RINAT = {'slot': 22, 'name': 'Ринат Фаридович Галиев', 'fixed': True}
SLAVA = {'slot': 23, 'name': 'Вячеслав Крюков', 'fixed': True}
KAMILA = {'slot': 24, 'name': 'Камила Шакирова', 'fixed': True}
MELNIKOV = {'slot': 4, 'name': 'Сергей Анатольевич Мельников', 'fixed': True}
def call(day, date, start, site, desk, ring, phone, repeat=False, direction='inbound', offset=None):
    line = {'main': '600', 'east': '610', 'west': '620'}[site]
    import datetime as dt
    T = dt.date(2026, 11, 13)
    d = dt.date.fromisoformat(date)
    return {'day': day, 'nominal_offset': f'T-{(T - d).days}d', 'nominal_date': date, 'local_start': start, 'site': site,
            'direction': direction, 'line': line, 'answered_by': desk, 'ring_s': ring, 'caller_phone': phone,
            'repeat_caller': repeat}
U = 'noise: [unintelligible] where the models disagree'
UT = 'noise and another language: [unintelligible] where the models disagree'
M = 'noise: uncertain spans marked'
GONE = 'noise: words gone without a trace'
