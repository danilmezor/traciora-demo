#!/bin/bash
# seeder/remote.sh <command ...>: copy this checkout to the ssh host SEED_HOST (~/seed-run/<folder name>, without
# .git) and run the command there, inside the copy, with the host's Python and PYTHONHASHSEED=0. One-time setup of
# the host: seeder/README.md.
set -euo pipefail
host=${SEED_HOST:-}
[ -n "$host" ] || { echo "seeder/remote.sh: set SEED_HOST to the ssh host of the build box" >&2; exit 2; }
root=$(cd "$(dirname "$0")/.." && pwd)
name=$(basename "$root")
rsync -a --delete --exclude .git --exclude __pycache__ --exclude .pytest_cache "$root/" "$host:seed-run/$name/"
ssh -o BatchMode=yes "$host" "cd seed-run/$name && PYTHONHASHSEED=0 PATH=\$HOME/seed-run/bin:\$HOME/seed-run/venv/bin:\$PATH $(printf '%q ' "$@")"
