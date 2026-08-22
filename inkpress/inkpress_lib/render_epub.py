#!/usr/bin/env python3
"""
render_epub.py — write a valid EPUB 3 with nothing but the standard library.

One XHTML file per chapter, a nav document that doubles as the table of
contents, and a package document listing both. The archive is assembled by
hand because the ordering rules are strict: 'mimetype' must be the first entry
and must be stored uncompressed, or readers reject the file.

Builds are reproducible — the publication UUID is derived from title + author
via uuid5 and every timestamp comes from front matter, so rebuilding an
unchanged manuscript produces a byte-identical archive.
"""
import uuid
import zipfile

from . import body, inline

# Stable namespace so the same book always gets the same UUID.
_NAMESPACE = uuid.UUID("6f9b1c2e-3a4d-5e6f-8a9b-0c1d2e3f4a5b")

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

STYLE_CSS = """@charset "utf-8";

body { margin: 0 5%; line-height: 1.5; text-align: justify; }
h1, h2 { text-align: left; line-height: 1.2; page-break-before: always; }
h1 { font-size: 1.6em; margin: 2em 0 1em; }
h2 { font-size: 1.3em; margin: 1.6em 0 0.8em; }
h3 { font-size: 1.1em; margin: 1.4em 0 0.6em; text-align: left; }
p { margin: 0; text-indent: 1.4em; }
h1 + p, h2 + p, h3 + p, blockquote + p, .scene-break + p { text-indent: 0; }
.scene-break { text-align: center; text-indent: 0; margin: 1.4em 0; }
/* Left-aligned, not justified: short quotes on a narrow screen would
   otherwise stretch their word spacing into visible rivers. */
blockquote { margin: 1.2em 2em; font-style: italic; text-align: left; }
.titlepage { text-align: center; page-break-after: always; }
.titlepage h1 { text-align: center; page-break-before: avoid; }
.titlepage .author { margin-top: 2em; font-size: 1.1em; }
"""


def _xhtml(title, inner, language):
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{inline.escape_attr(language)}">
<head>
  <meta charset="utf-8" />
  <title>{inline.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
{inner}
</body>
</html>
"""


def _title_page(document):
    meta = document.meta
    centered = 'style="text-align: center; text-indent: 0;"'
    parts = [f'  <h1 {centered}>{inline.render(document.title)}</h1>']
    if meta.get("subtitle"):
        parts.append(
            f'  <p class="subtitle" {centered}>{inline.render(meta["subtitle"])}</p>'
        )
    parts.append(
        f'  <p class="author" {centered}>{inline.escape(meta.get("author", ""))}</p>'
    )
    return (
        f'<section class="titlepage" epub:type="titlepage" {centered}>\n'
        + "\n".join(parts)
        + "\n</section>"
    )


# Reading systems vary in how much of a stylesheet they honour, and several
# override rules on bare <p>. Centring that must survive is set inline too.
SCENE_BREAK_XHTML = (
    '<p class="scene-break" style="text-align: center; text-indent: 0;">* * *</p>'
)


def _chapter_xhtml(chapter, document):
    heading = f'  <h2 id="{chapter.slug}">{inline.render(chapter.title)}</h2>'
    prose = body.blocks_to_html(
        chapter.blocks, heading_level=3, indent="  ", scene_break=SCENE_BREAK_XHTML
    )
    inner = f'<section epub:type="chapter">\n{heading}\n' + "\n".join(prose) + "\n</section>"
    return _xhtml(inline.plain(chapter.title), inner, document.meta.get("language", "en"))


def _nav_xhtml(document):
    items = "\n".join(
        f'      <li><a href="chap-{chapter.number:03d}.xhtml">'
        f"{inline.escape(inline.plain(chapter.title))}</a></li>"
        for chapter in document.chapters
    )
    inner = f"""<nav epub:type="toc" id="toc">
  <h1>Contents</h1>
  <ol>
{items}
  </ol>
</nav>"""
    return _xhtml("Contents", inner, document.meta.get("language", "en"))


def _package_opf(document, book_uuid, modified):
    meta = document.meta
    language = meta.get("language", "en")

    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="style" href="style.css" media-type="text/css"/>',
        '    <item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['    <itemref idref="titlepage"/>', '    <itemref idref="nav"/>']

    for chapter in document.chapters:
        item_id = f"chap{chapter.number:03d}"
        manifest.append(
            f'    <item id="{item_id}" href="chap-{chapter.number:03d}.xhtml" '
            'media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="{item_id}"/>')

    optional = []
    if meta.get("publisher"):
        optional.append(f'    <dc:publisher>{inline.escape(meta["publisher"])}</dc:publisher>')
    if meta.get("description"):
        optional.append(f'    <dc:description>{inline.escape(meta["description"])}</dc:description>')
    if meta.get("date"):
        optional.append(f'    <dc:date>{inline.escape(str(meta["date"]))}</dc:date>')
    for subject in meta.get("subjects", []) or []:
        optional.append(f"    <dc:subject>{inline.escape(subject)}</dc:subject>")

    optional_block = ("\n" + "\n".join(optional)) if optional else ""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="pub-id" xml:lang="{inline.escape_attr(language)}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="pub-id">urn:uuid:{book_uuid}</dc:identifier>
    <dc:title>{inline.escape(inline.plain(document.title))}</dc:title>
    <dc:language>{inline.escape(language)}</dc:language>
    <dc:creator id="creator">{inline.escape(meta.get('author', ''))}</dc:creator>
    <meta refines="#creator" property="role" scheme="marc:relators">aut</meta>{optional_block}
    <meta property="dcterms:modified">{modified}</meta>
  </metadata>
  <manifest>
{chr(10).join(manifest)}
  </manifest>
  <spine>
{chr(10).join(spine)}
  </spine>
</package>
"""


def render(document, out_path):
    """Write the Document to out_path as an EPUB 3 file. Returns out_path."""
    meta = document.meta
    date = str(meta.get("date", "1970-01-01"))
    modified = f"{date}T00:00:00Z"
    book_uuid = meta.get("uuid") or uuid.uuid5(
        _NAMESPACE, f"{inline.plain(document.title)}|{meta.get('author', '')}"
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Fixed timestamp keeps rebuilds byte-identical.
    stamp = (1980, 1, 1, 0, 0, 0)

    def write(archive, name, data, compress=zipfile.ZIP_DEFLATED):
        info = zipfile.ZipInfo(name, date_time=stamp)
        info.compress_type = compress
        info.external_attr = 0o644 << 16
        archive.writestr(info, data)

    with zipfile.ZipFile(out_path, "w") as archive:
        # Must be first and stored, per the EPUB OCF spec.
        write(archive, "mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        write(archive, "META-INF/container.xml", CONTAINER_XML)
        write(archive, "OEBPS/style.css", STYLE_CSS)
        write(archive, "OEBPS/content.opf", _package_opf(document, book_uuid, modified))
        write(archive, "OEBPS/nav.xhtml", _nav_xhtml(document))
        write(
            archive,
            "OEBPS/titlepage.xhtml",
            _xhtml(inline.plain(document.title), _title_page(document),
                   meta.get("language", "en")),
        )
        for chapter in document.chapters:
            write(
                archive,
                f"OEBPS/chap-{chapter.number:03d}.xhtml",
                _chapter_xhtml(chapter, document),
            )

    return out_path
