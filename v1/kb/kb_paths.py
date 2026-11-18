"""Give Russian demo pages their installed names while the source keys stay shared with English."""

from functools import lru_cache
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import quote

KB = Path(__file__).resolve().parent
RU_FOLDERS = {
    "customers": ("Клиентам", "worker"),
    "shop-floor": ("Цех", "worker"),
    "services": ("Услуги", "worker"),
    "services/maintenance": ("ТО", None),
    "services/brakes": ("Тормоза", None),
    "services/tires": ("Шины", None),
    "services/diagnostics": ("Диагностика", None),
    "services/suspension": ("Ходовая", None),
    "services/ac": ("Кондиционер", None),
    "services/electrical": ("Электрика", None),
    "services/engine": ("Двигатель", None),
    "services/transmission": ("Трансмиссия", None),
    "services/inspections": ("Осмотры", None),
    "prices": ("Цены", "worker"),
    "policies": ("Правила", "junior"),
    "accounts": ("Корпоративные клиенты", "junior"),
    "accounts/credit": ("Лимиты задолженности", "middle"),
    "how-to": ("Как мы работаем", "junior"),
    "parts": ("Запчасти", "junior"),
    "shops": ("Площадки", "junior"),
    "shops/main": ("Московское шоссе", None),
    "shops/east": ("Инженерный", None),
    "shops/west": ("Техническая", None),
    "team": ("Команда", "junior"),
    "office": ("Бухгалтерия", "middle"),
    "management": ("Руководству", "senior"),
    "management/owners": ("Владельцам", "administrator"),
    "playbooks": ("Памятки по должностям", "administrator"),
}
RU_MISSING = {"shops/west/tow-trucks.md": "Эвакуаторы, с которыми работаем"}
RANKS = {"public": "worker", "staff": "junior", "middle": "middle", "senior": "senior", "administrator": "administrator"}
LOCAL_LINK = re.compile(r"\]\((?P<path>(?:[./]*[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)(?P<tail>[^)]*)\)")


@lru_cache(maxsize=1)
def russian_pages():
    registry = json.loads((KB / "_build/registry-ru.json").read_text(encoding="utf-8"))
    return {path: record for path, record in registry.items() if not record.get("not_a_page")}


@lru_cache(maxsize=1)
def russian_paths():
    folders = {"": ""}
    for source, (name, _) in RU_FOLDERS.items():
        folders[source] = posixpath.join(folders[posixpath.dirname(source)], source if source == "playbooks" else name)
    paths = {source: path for source, path in folders.items() if source}
    for source, title in ({path: record["title"] for path, record in russian_pages().items()} | RU_MISSING).items():
        file = PurePosixPath(source)
        name = "Обзор" if file.name == "README.md" else title
        paths[source] = posixpath.join(folders[posixpath.dirname(source)], name + file.suffix)
    if len(set(paths.values())) != len(paths):
        raise ValueError("Russian knowledge pages must have distinct installed paths")
    return paths


@lru_cache(maxsize=1)
def russian_sources():
    return {installed: source for source, installed in russian_paths().items()}


def russian_links(source, text):
    """Point links in the installed Markdown at installed paths, including the planted missing page."""
    paths = russian_paths()

    def destination(match):
        target = posixpath.normpath(posixpath.join(posixpath.dirname(source), match["path"]))
        installed = posixpath.relpath(paths[target], posixpath.dirname(paths[source]) or ".")
        return "](" + quote(installed, safe="/") + match["tail"] + ")"

    return LOCAL_LINK.sub(destination, text)


def russian_ranks():
    """Folder defaults and file exceptions from the Russian outline and page registry."""
    paths = russian_paths()
    ranks = {path: rank for path, (_, rank) in RU_FOLDERS.items() if rank}
    for path, record in russian_pages().items():
        if not path.endswith(".md"):
            continue  # the seed's binary drafts are not installed
        parent = posixpath.dirname(path)
        while parent and parent not in ranks:
            parent = posixpath.dirname(parent)
        rank = RANKS[record["visibility"]]
        if rank != ranks.get(parent, "worker"):
            ranks[path] = rank
    return {paths[source]: rank for source, rank in ranks.items() if source != "playbooks"}
