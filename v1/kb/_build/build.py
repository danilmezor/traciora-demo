"""Rebuild both configurations of the knowledge base from the seed files, then check them.
English: kb/en, kb/facts, kb/en/_history, kb/OUTLINE.md. Russian: kb/ru, kb/facts-ru, kb/ru/_history, kb/OUTLINE-ru.md.
Run from anywhere: python3 kb/_build/build.py"""
import os, subprocess, sys, glob
here = os.path.dirname(os.path.abspath(__file__))
# Everything under en/, ru/, facts/ and facts-ru/ is generated, except the owner's reading guide ru/_README.md:
# clear it first, so a renamed or dropped page leaves no file behind.
import shutil
_kb = os.path.dirname(here)
for d in ('en', 'facts', 'facts-ru', 'ru'):
    for name in os.listdir(os.path.join(_kb, d)) if os.path.isdir(os.path.join(_kb, d)) else ():
        p = os.path.join(_kb, d, name)
        if name == '_README.md': continue
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
reg = os.path.join(here, 'registry.json')
if os.path.exists(reg): os.remove(reg)
batches = sorted(glob.glob(os.path.join(here, 'b[0-9][0-9].py')))
for b in batches:
    subprocess.run([sys.executable, b], check=True, cwd=here, stdout=subprocess.DEVNULL)
for b in batches[:-1]:  # the last batch is the binaries, which have no earlier text
    subprocess.run([sys.executable, b], check=True, cwd=here, stdout=subprocess.DEVNULL, env={**os.environ, 'KB_WHEN': 'before_rise'})
subprocess.run([sys.executable, os.path.join(here, 'outline_tree.py')], check=True, cwd=here, stdout=subprocess.DEVNULL)
out = os.path.dirname(here)
with open(os.path.join(out, 'OUTLINE.md'), 'w') as f:
    for part in ('outline_head.md', 'tree.md', 'outline_tail.md'):
        f.write(open(os.path.join(here, part)).read())
subprocess.run([sys.executable, os.path.join(here, 'check.py')], check=True, cwd=here)

# ---- the Russian configuration (kbr.py): the same page keys, its own text, the catalogue's and the ledger's `ru` values
regru = os.path.join(here, 'registry-ru.json')
if os.path.exists(regru): os.remove(regru)
ru = sorted(glob.glob(os.path.join(here, 'ru[0-9][0-9].py')))
envru = {**os.environ, 'KB_CFG': 'ru'}
for b in ru:
    subprocess.run([sys.executable, b], check=True, cwd=here, stdout=subprocess.DEVNULL, env=envru)
for b in ru[:-1]:  # the last batch is the binaries, which have no earlier text
    subprocess.run([sys.executable, b], check=True, cwd=here, stdout=subprocess.DEVNULL, env={**envru, 'KB_WHEN': 'before_rise'})
if os.path.exists(os.path.join(here, 'outline_ru.py')):
    subprocess.run([sys.executable, os.path.join(here, 'outline_ru.py')], check=True, cwd=here, stdout=subprocess.DEVNULL, env=envru)
subprocess.run([sys.executable, os.path.join(here, 'check_ru.py')], check=True, cwd=here, env=envru)
