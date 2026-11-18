"""The seed gate. One line says whether seed v1 is ready for its first slice, the shop-system generator.

Run it under the product's Python, from the seed's folder:

    ../traciora/.venv/bin/python v1/checks/gate.py

It copies v1 to a temporary folder and runs everything there, so a run leaves the tree as it was. The checks find the
product at TRACIORA_PRODUCT, else at ../traciora beside this checkout, which the gate resolves before it copies.
D1: the nineteen checks of the seed pass.  D2: every statement of erp/checks.sql and every shop golden's
SQL plans under EXPLAIN on an empty database loaded from erp/schema.sql.  D3: every fact of a
knowledge-base golden is found on the built page it names.  D4: the "Slice 1" list of PENDING.md is empty.
D2 and D3 live in gate_goldens.py, which this file calls when it exists.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

V1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCT = os.environ.get("TRACIORA_PRODUCT") or os.path.join(os.path.dirname(os.path.dirname(V1)), "traciora")
LANGS = ("en", "ru")
CHECKS = [["checks/check_ledger.py"]] + [[f"checks/{c}.py", lang] for c in ("check_calls", "check_conversations", "check_workday", "check_assistant") for lang in LANGS] + [
    [f"checks/{c}.py"] for c in ("check_evals", "check_kb", "check_catalogue", "check_bank_en", "check_bank_ru", "check_conv_bank_en", "check_conv_bank_ru", "check_files")] + [["erp/validate.py"], ["tenant/validate.py"]]


def slice1_open(root):
    """The bullet lines under the heading that starts '## Slice 1' in PENDING.md."""
    text = open(os.path.join(root, "PENDING.md"), encoding="utf-8").read()
    found = re.search(r"^## Slice 1[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not found:
        return None
    return [line for line in found.group(1).splitlines() if line.startswith("- ")]


def main():
    head = subprocess.run(["git", "-C", V1, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip() or "nohead"
    work = tempfile.mkdtemp(prefix="seed-gate-")
    root = os.path.join(work, "v1")
    shutil.copytree(V1, root, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(os.path.join(os.path.dirname(V1), "seeder"), os.path.join(work, "seeder"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    failed, parts = [], []
    try:
        passed = 0
        for check in CHECKS:
            folder = os.path.join(root, os.path.dirname(check[0])) if check[0].endswith("validate.py") else root
            script = os.path.basename(check[0]) if check[0].endswith("validate.py") else check[0]
            done = subprocess.run([sys.executable, script] + check[1:], cwd=folder, capture_output=True, text=True,
                                  env=os.environ | {"TRACIORA_PRODUCT": PRODUCT})
            if done.returncode == 0:
                passed += 1
            else:
                failed.append("D1 " + " ".join(check) + ": " + (done.stdout.strip().splitlines() or [done.stderr.strip()[-200:]])[-1][:200])
        parts.append(f"checks={passed}")
        goldens = os.path.join(root, "checks", "gate_goldens.py")
        if os.path.exists(goldens):
            spec = importlib.util.spec_from_file_location("gate_goldens", goldens)
            sys.path.insert(0, work)  # run the generator against the copy being checked
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            more_parts, more_failed = module.run(root)
            parts += more_parts
            failed += more_failed
        else:
            failed.append("D2, D3: checks/gate_goldens.py is not written yet")
        open_items = slice1_open(root)
        if open_items is None:
            failed.append("D4: PENDING.md has no '## Slice 1' heading")
        else:
            parts.append(f"slice1_open={len(open_items)}")
            failed += ["D4 open: " + item[:160] for item in open_items]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    for line in failed:
        print("  FAIL " + line)
    print(f"SEED GATE v1 {head} {'FAIL' if failed else 'PASS'} " + " ".join(parts))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
