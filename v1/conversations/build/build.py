#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Writes conversations/en and conversations/ru from the src_*.py files beside it (see convlib.py)."""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.normpath(os.path.join(HERE, ".."))


def main():
    want = sys.argv[1:] or ["en", "ru"]
    for cfg in want:
        n = 0
        for part in ("a", "b"):
            name = "src_%s_%s" % (cfg, part)
            if not os.path.exists(os.path.join(HERE, name + ".py")):
                continue
            mod = importlib.import_module(name)
            for make in mod.FILES:
                f = make()
                f.write(os.path.join(OUT, cfg))
                n += 1
        print(cfg, n, "files")


if __name__ == "__main__":
    main()
