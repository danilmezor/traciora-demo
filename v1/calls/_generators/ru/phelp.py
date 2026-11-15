import re
def sub(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:60], s.count(a))
        s = s.replace(a, b)
    open(path, 'w').write(s)

def replace_script(path, n, new_script):
    s = open(path).read()
    i = s.index(f'    n={n}, ')
    j = s.index('    script=[\n', i)
    k = s.index('    ],\n    judge=', j)
    s = s[:j] + new_script + s[k + len('    ],\n'):]
    open(path, 'w').write(s)

