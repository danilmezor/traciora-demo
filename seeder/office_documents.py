"""Small, deterministic Office Open XML writers for the authored seed documents."""
from html import escape
from io import BytesIO
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

OPEN_XML = "http://schemas.openxmlformats.org"
MAIN_NS = f"{OPEN_XML}/officeDocument/2006"
TYPES_NS = f"{OPEN_XML}/package/2006/content-types"
RELS_NS = f"{OPEN_XML}/package/2006/relationships"
WORD_NS = f"{OPEN_XML}/wordprocessingml/2006/main"
PPT_NS = f"{OPEN_XML}/presentationml/2006/main"
DRAWING_NS = f"{OPEN_XML}/drawingml/2006/main"
PPT = f'xmlns:p="{PPT_NS}" xmlns:r="{MAIN_NS}/relationships" xmlns:a="{DRAWING_NS}"'
PPT_TYPE = "application/vnd.openxmlformats-officedocument.presentationml."
WORD_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml."
GROUP = '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
SIZE = (12192000, 6858000)
COLOURS = {
    "dk1": "182527", "lt1": "FFFFFF", "dk2": "144C48", "lt2": "EEF4F2",
    "accent1": "144C48", "accent2": "437E78", "accent3": "A66037", "accent4": "53865D",
    "accent5": "526D8F", "accent6": "846B8E", "hlink": "2455A6", "folHlink": "75518B",
}
FONT = '<a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/>'
# Holidays and sickness, appearance and tools, and phones and leaving share pages.
HANDBOOK_PAGE_STARTS = {2, 3, 4, 5, 7, 9, 10, 11}


def archive(parts: dict[str, str | bytes]) -> bytes:
    """Write a ZIP with the same entry timestamps and order every time."""
    result = BytesIO()
    with ZipFile(result, "w") as package:
        for path, content in sorted(parts.items()):
            part = ZipInfo(path, date_time=(2000, 1, 1, 0, 0, 0))
            package.writestr(part, content, compress_type=ZIP_DEFLATED, compresslevel=9)
    return result.getvalue()


def _types(content: dict[str, str]) -> str:
    overrides = "".join(f'<Override PartName="/{name}" ContentType="{kind}"/>' for name, kind in content.items())
    return (f'<Types xmlns="{TYPES_NS}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-'
            f'package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
            f'{overrides}</Types>')


def _rels(*parts: tuple[str, str]) -> str:
    relations = "".join(f'<Relationship Id="rId{i}" Type="{MAIN_NS}/relationships/{kind}" Target="{target}"/>'
                        for i, (kind, target) in enumerate(parts, 1))
    return f'<Relationships xmlns="{RELS_NS}">{relations}</Relationships>'


def _word_paragraph(text: str, *, style: str = "", bullet: bool = False, new_page: bool = False) -> str:
    paragraph = f'<w:pStyle w:val="{style}"/>' if style else ""
    if new_page:
        paragraph += "<w:pageBreakBefore/>"
    if bullet:
        paragraph += '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
    if paragraph:
        paragraph = f"<w:pPr>{paragraph}</w:pPr>"
    return f'<w:p>{paragraph}<w:r><w:t xml:space="preserve">{escape(text, quote=False)}</w:t></w:r></w:p>'


def _word_table(table: ElementTree.Element) -> str:
    rows = []
    for row in table.iter("tr"):
        heading = row.find("th") is not None
        cells = []
        for cell in row:
            shade = '<w:shd w:fill="EEF4F2"/>' if heading else ""
            text = "".join(cell.itertext()).strip()
            cells.append(f'<w:tc><w:tcPr><w:tcW w:w="4300" w:type="dxa"/>{shade}</w:tcPr>'
                         f'{_word_paragraph(text)}</w:tc>')
        header = "<w:trPr><w:tblHeader/></w:trPr>" if heading else ""
        rows.append(f'<w:tr>{header}{"".join(cells)}</w:tr>')
    return ('<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>'
            + "".join(f'<w:{edge} w:val="single" w:sz="4" w:color="C5D0CD"/>'
                      for edge in ("top", "left", "bottom", "right", "insideH", "insideV"))
            + '</w:tblBorders></w:tblPr><w:tblGrid><w:gridCol w:w="4300"/><w:gridCol w:w="4300"/></w:tblGrid>'
            + "".join(rows) + "</w:tbl>")


def _word_styles(lang: str) -> str:
    return (f'<w:styles xmlns:w="{WORD_NS}"><w:docDefaults><w:rPrDefault><w:rPr>'
            f'<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/><w:lang w:val="{lang}"/>'
            '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="150" w:line="286" '
            'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
            + "".join(
                f'<w:style w:type="paragraph" w:styleId="Heading{n}"><w:name w:val="heading {n}"/>'
                f'<w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>'
                f'<w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="100"/>'
                f'<w:outlineLvl w:val="{n - 1}"/></w:pPr><w:rPr><w:b/><w:color w:val="144C48"/>'
                f'<w:sz w:val="{size}"/></w:rPr></w:style>'
                for n, size in ((1, 42), (2, 29))
            ) + "</w:styles>")


def handbook(contents: ElementTree.Element, cfg: str, paper: str) -> bytes:
    lang = "ru-RU" if cfg == "ru" else "en-US"
    width, height = (11906, 16838) if paper == "A4" else (12240, 15840)
    section = (f'<w:sectPr><w:type w:val="continuous"/><w:pgSz w:w="{width}" w:h="{height}"/>'
               '<w:pgMar w:top="1000" w:right="1200" w:bottom="1000" w:left="1200" '
               'w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')
    content = []
    headings = 0
    for block in contents:
        text = "".join(block.itertext()).strip()
        if block.tag == "h1":
            content.append(_word_paragraph(text, style="Heading1"))
        elif block.tag == "h2":
            if headings:
                content.append(f"<w:p><w:pPr>{section}</w:pPr></w:p>")
            headings += 1
            content.append(_word_paragraph(text, style="Heading2", new_page=headings in HANDBOOK_PAGE_STARTS))
        elif block.tag == "p":
            content.append(_word_paragraph(text))
        elif block.tag == "ul":
            content.extend(_word_paragraph("".join(item.itertext()).strip(), bullet=True) for item in block)
        elif block.tag == "table":
            content.append(_word_table(block))
        else:
            raise ValueError(f"unexpected handbook block {block.tag!r}")
    if headings != 12:
        raise ValueError("the staff handbook must have twelve authored sections")
    numbering = (
        f'<w:numbering xmlns:w="{WORD_NS}"><w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="singleLevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/>'
        '<w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="360"/></w:tabs>'
        '<w:ind w:left="360" w:hanging="240"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="1">'
        '<w:abstractNumId w:val="0"/></w:num></w:numbering>'
    )
    return archive({
        "[Content_Types].xml": _types({
            "word/document.xml": WORD_TYPE + "document.main+xml",
            "word/styles.xml": WORD_TYPE + "styles+xml",
            "word/numbering.xml": WORD_TYPE + "numbering+xml",
        }),
        "_rels/.rels": _rels(("officeDocument", "word/document.xml")),
        "word/_rels/document.xml.rels": _rels(("styles", "styles.xml"), ("numbering", "numbering.xml")),
        "word/document.xml": f'<w:document xmlns:w="{WORD_NS}"><w:body>{"".join(content)}{section}</w:body></w:document>',
        "word/styles.xml": _word_styles(lang),
        "word/numbering.xml": numbering,
    })


def _theme() -> str:
    colours = "".join(f'<a:{key}><a:srgbClr val="{value}"/></a:{key}>' for key, value in COLOURS.items())
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    lines = "".join(f'<a:ln w="{width}">{fill}</a:ln>' for width in (9525, 25400, 38100))
    effects = '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3
    return (f'<a:theme xmlns:a="{DRAWING_NS}" name="Training"><a:themeElements><a:clrScheme name="Training">'
            f'{colours}</a:clrScheme><a:fontScheme name="Arial"><a:majorFont>{FONT}</a:majorFont>'
            f'<a:minorFont>{FONT}</a:minorFont></a:fontScheme><a:fmtScheme name="Training">'
            f'<a:fillStyleLst>{fill * 3}</a:fillStyleLst><a:lnStyleLst>{lines}</a:lnStyleLst>'
            f'<a:effectStyleLst>{effects}</a:effectStyleLst><a:bgFillStyleLst>{fill * 3}</a:bgFillStyleLst>'
            '</a:fmtScheme></a:themeElements></a:theme>')


def _slide_box(lines: list[str], lang: str, title: bool) -> str:
    ident, name, y, height, size, colour = (2, "Title", 790000, 1500000, 3500, "144C48") if title else (
        3, "Text", 2490000, 3300000, 2250, "182527")
    placeholder = '<p:ph type="title"/>' if title else ""
    bold = ' b="1"' if title else ""
    paragraphs = "".join(
        f'<a:p><a:pPr><a:spcAft><a:spcPts val="800"/></a:spcAft></a:pPr><a:r>'
        f'<a:rPr lang="{lang}" sz="{size}"{bold}><a:solidFill><a:srgbClr val="{colour}"/></a:solidFill>'
        f'<a:latin typeface="Arial"/></a:rPr><a:t>{escape(text, quote=False)}</a:t></a:r></a:p>'
        for text in lines if text.strip()
    )
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{ident}" name="{name}"/><p:cNvSpPr txBox="1"/>'
            f'<p:nvPr>{placeholder}</p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="850000" y="{y}"/>'
            f'<a:ext cx="10450000" cy="{height}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            '<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr><p:txBody>'
            f'<a:bodyPr wrap="square" anchor="t" lIns="0" rIns="0" tIns="0" bIns="0"/><a:lstStyle/>'
            f'{paragraphs}</p:txBody></p:sp>')


def slide_deck(slides: list[tuple[str, list[str]]], cfg: str) -> bytes:
    lang = "ru-RU" if cfg == "ru" else "en-US"
    master = "ppt/slideMasters/slideMaster1.xml"
    layout = "ppt/slideLayouts/slideLayout1.xml"
    types = {name: PPT_TYPE + media + "+xml" for name, media in {
        "ppt/presentation.xml": "presentation.main", "ppt/presProps.xml": "presProps",
        master: "slideMaster", layout: "slideLayout",
    }.items()}
    types["ppt/theme/theme1.xml"] = "application/vnd.openxmlformats-officedocument.theme+xml"
    relations = [("slideMaster", "slideMasters/slideMaster1.xml"), ("presProps", "presProps.xml")]
    slides_xml = []
    cm = '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
    empty = f'<p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>'
    mapping = " ".join(f'{key}="{role}"' for key, role in (
        ("bg1", "lt1"), ("tx1", "dk1"), ("bg2", "lt2"), ("tx2", "dk2"),
        *((key, key) for key in list(COLOURS)[4:]),
    ))
    parts = {
        "_rels/.rels": _rels(("officeDocument", "ppt/presentation.xml")),
        "ppt/presProps.xml": f'<p:presentationPr {PPT}/>',
        master: (f'<p:sldMaster {PPT}>{empty}<p:clrMap {mapping}/><p:sldLayoutIdLst>'
                 '<p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst></p:sldMaster>'),
        layout: f'<p:sldLayout {PPT} type="blank" preserve="1">{empty}{cm}</p:sldLayout>',
        "ppt/slideMasters/_rels/slideMaster1.xml.rels":
            _rels(("slideLayout", "../slideLayouts/slideLayout1.xml"), ("theme", "../theme/theme1.xml")),
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": _rels(("slideMaster", "../slideMasters/slideMaster1.xml")),
        "ppt/theme/theme1.xml": _theme(),
    }
    for n, (heading, lines) in enumerate(slides, 1):
        path = f"ppt/slides/slide{n}.xml"
        boxes = _slide_box([heading], lang, True) + _slide_box(lines, lang, False)
        parts[path] = f'<p:sld {PPT}><p:cSld><p:spTree>{GROUP}{boxes}</p:spTree></p:cSld>{cm}</p:sld>'
        parts[f"ppt/slides/_rels/slide{n}.xml.rels"] = _rels(("slideLayout", "../slideLayouts/slideLayout1.xml"))
        types[path] = PPT_TYPE + "slide+xml"
        relations.append(("slide", f"slides/slide{n}.xml"))
        slides_xml.append(f'<p:sldId id="{255 + n}" r:id="rId{n + 2}"/>')
    parts["[Content_Types].xml"] = _types(types)
    parts["ppt/_rels/presentation.xml.rels"] = _rels(*relations)
    parts["ppt/presentation.xml"] = (
        f'<p:presentation {PPT}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{"".join(slides_xml)}</p:sldIdLst><p:sldSz cx="{SIZE[0]}" cy="{SIZE[1]}"/>'
        '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
    )
    return archive(parts)
