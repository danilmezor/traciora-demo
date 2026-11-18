"""Render the seed's authored, date-resolved binary knowledge documents."""
from datetime import datetime
from html import escape
from io import BytesIO
from math import ceil
import re
from xml.etree import ElementTree
from zipfile import ZipFile

from markdown_it import MarkdownIt
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from weasyprint import CSS, HTML

from seeder.office_documents import archive, handbook, slide_deck


PATHS = (
    "prices/counter-price-sheet.pdf",
    "team/staff-handbook.docx",
    "parts/fleet-fluid-sheet.xlsx",
    "parts/fleet-fluid-sheet.pdf",
    "team/the-call-in-eight-moves.pptx",
)
DOCUMENT = re.compile(r"^## \d+\. `([^`]+)`[ \t]*$", re.M)
PAGE = re.compile(r"^### (?:Page|Страница) (\d+)[ \t]*$", re.M)
SLIDE = re.compile(r"^\*\*(?:Slide|Слайд) (\d+) · (.+?)\*\*[ \t]*$", re.M)
A18 = re.compile(r'^(?:Cell|Ячейка) A18:\s*(?:"(.*)"|«(.*)»)\.?$', re.M)
DECIMAL = re.compile(r"\d+[.,]\d+")
MARKDOWN = MarkdownIt("commonmark", {"breaks": True, "xhtmlOut": True}).enable("table")

PDF_STYLE = """
body { color: #182527; font: 9.5pt/1.28 "Noto Sans", "Arial", sans-serif; }
p { margin: 0 0 3mm; }
section { break-after: page; }
section:last-child { break-after: auto; }
section > p:first-child > strong:first-child { color: #144c48; font-size: 15pt; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; }
thead { background: #144c48; color: white; }
th, td { padding: 1.25mm 1.8mm; text-align: left; vertical-align: top; }
td { border-bottom: 1px solid #c5d0cd; }
tr { break-inside: avoid; }
tbody tr:nth-child(even) { background: #eef4f2; }
body.fleet { font-size: 8pt; }
.fleet th, .fleet td { padding: 1mm 1.35mm; }
.fleet td:nth-child(4), .counter td:not(:first-child) { white-space: nowrap; }
"""


def render(cfg: str, draft: str) -> dict[str, bytes]:
    if cfg not in ("en", "ru"):
        raise ValueError(f"unknown document configuration {cfg!r}")
    documents = _documents(draft)
    counter = _numbered(documents[PATHS[0]], PAGE, 2)
    fleet = documents[PATHS[3]]
    slides = _numbered(documents[PATHS[4]], SLIDE, 10)
    paper = "Letter" if cfg == "en" else "A4"
    return {
        PATHS[0]: _pdf(cfg, [body for _, body in counter], paper, "counter"),
        PATHS[1]: handbook(_elements(documents[PATHS[1]]), cfg, paper),
        PATHS[2]: _spreadsheet(cfg, documents[PATHS[2]]),
        PATHS[3]: _pdf(cfg, [fleet], f"{paper} landscape", "fleet"),
        PATHS[4]: slide_deck([(match[2], body.splitlines()) for match, body in slides], cfg),
    }


def _documents(draft: str) -> dict[str, str]:
    documents = {}
    matches = list(DOCUMENT.finditer(draft))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(draft)
        body = draft[match.end():end].strip().removesuffix("\n---").rstrip()
        description, separator, content = body.partition("\n\n")
        if not separator or not (description.startswith("*") and description.endswith("*")):
            raise ValueError(f"missing converter description for {match[1]}")
        if match[1] in documents or "{{" in content:
            raise ValueError(f"duplicate document or unresolved date: {match[1]}")
        documents[match[1]] = content
    if tuple(documents) != PATHS:
        raise ValueError("the document draft must contain the five authored formats in order")
    return documents


def _numbered(document: str, marker: re.Pattern, count: int) -> list[tuple[re.Match, str]]:
    parts = list(marker.finditer(document))
    if [int(part[1]) for part in parts] != list(range(1, count + 1)):
        raise ValueError(f"expected {count} consecutively numbered document parts")
    return [(part, document[part.end():parts[i + 1].start() if i + 1 < len(parts) else len(document)].strip())
            for i, part in enumerate(parts)]


def _elements(document: str) -> ElementTree.Element:
    return ElementTree.fromstring(f"<root>{MARKDOWN.render(document)}</root>")


def _pdf(cfg: str, pages: list[str], paper: str, kind: str) -> bytes:
    title = next(_elements(pages[0]).iter("strong")).text
    sections = "".join(f"<section>{MARKDOWN.render(page)}</section>" for page in pages)
    source = f'<!doctype html><html lang="{cfg}"><meta charset="utf-8"><title>{escape(title)}</title>' \
             f'<body class="{kind}">{sections}</body></html>'
    css = CSS(string=f"@page {{ size: {paper}; margin: 13mm 14mm; }}{PDF_STYLE}")
    document = HTML(string=source).render(stylesheets=[css])
    if len(document.pages) != len(pages):
        raise ValueError(f"the {cfg} {kind} PDF must occupy {len(pages)} page(s), got {len(document.pages)}")
    return document.write_pdf(pdf_variant="pdf/ua-1")


def _spreadsheet(cfg: str, document: str) -> bytes:
    table = _elements(document).find("table")
    note = A18.search(document)
    if table is None or note is None:
        raise ValueError("the fleet spreadsheet needs the authored table and A18 note")
    rows = [["".join(cell.itertext()).strip() for cell in row] for row in table.iter("tr")]
    if len(rows) != 16 or any(len(row) != 7 for row in rows):
        raise ValueError("the fleet spreadsheet must have seven columns and fifteen data rows")

    book = Workbook()
    book.properties.created = datetime(2000, 1, 1)
    sheet = book.active
    sheet.title = "Fluids" if cfg == "en" else "Жидкости"
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = "A1:G16"
    widths = (31, 32, 31, 24, 28, 35, 48)
    header = PatternFill("solid", fgColor="144C48")
    stripe = PatternFill("solid", fgColor="EEF4F2")
    for col, width in enumerate(widths, 1):
        sheet.column_dimensions[get_column_letter(col)].width = width
    for pos, row in enumerate(rows, 1):
        height = max(ceil(len(value) / (width - 2)) for value, width in zip(row, widths))
        sheet.row_dimensions[pos].height = 10 + 15 * height
        for col, value in enumerate(row, 1):
            cell = sheet.cell(pos, col, value)
            cell.data_type = "s"
            cell.alignment = Alignment(vertical="center", wrap_text=True)
            if pos == 1:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = header
            elif pos % 2 == 0:
                cell.fill = stripe
            if col == 4 and DECIMAL.fullmatch(value):
                number = value.replace(",", ".")
                cell.value = float(number)
                cell.number_format = "0." + "0" * len(number.partition(".")[2])
    sheet["A18"] = note[1] or note[2]

    output = BytesIO()
    book.save(output)
    with ZipFile(output) as package:
        parts = {name: package.read(name) for name in package.namelist()}
    props = parts["docProps/core.xml"]
    parts["docProps/core.xml"] = re.sub(
        rb"(<dcterms:modified\b[^>]*>)[^<]*(</dcterms:modified>)",
        rb"\g<1>2000-01-01T00:00:00Z\2", props,
    )
    return archive(parts)
