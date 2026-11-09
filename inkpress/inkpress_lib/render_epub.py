#!/usr/bin/env python3
"""
render_epub.py — write a valid EPUB 3 with nothing but the standard library.

One XHTML file per chapter, a nav document that doubles as the table of
contents, and a package document listing both. The archive is assembled by
hand because the ordering rules are strict: 'mimetype' must be the first entry
and must be stored uncompressed, or readers reject the file.

The Edition supplies fonts, colours and ornaments. For tier 3 the generated
chapter art is written into the archive as SVG and referenced from each
chapter, so the ebook carries the same art direction as the printed interior.

Builds are reproducible — the publication UUID is derived from title + author
via uuid5, the art generator is seeded from chapter text, and every timestamp
comes from front matter, so rebuilding an unchanged manuscript produces a
byte-identical archive.
"""
import uuid
import zipfile
from pathlib import Path

from . import art, body, editions, inline, render_print

_COVER_MEDIA_TYPES = {
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}

# Stable namespace so the same book always gets the same UUID.
_NAMESPACE = uuid.UUID("6f9b1c2e-3a4d-5e6f-8a9b-0c1d2e3f4a5b")

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

# Reading systems vary in how much of a stylesheet they honour, and several
# override rules on bare <p>. Centring that must survive is set inline too.
_CENTERED = 'style="text-align: center; text-indent: 0;"'


def build_style(edition):
    drop_cap = ""
    if edition.drop_cap:
        dc_style = getattr(edition, "drop_cap_style", "classic")
        if dc_style == "framed":
            drop_cap = f""".dropcap {{
  float: left;
  font-family: {edition.display_font};
  font-size: 2.3em;
  line-height: 1;
  padding: 0.12em 0.22em;
  margin: 0.04em 0.22em 0.04em 0;
  border: 1.5px solid {edition.accent};
  color: {edition.accent};
}}
.opening {{ text-indent: 0; }}
"""
        elif dc_style == "boxed":
            drop_cap = f""".dropcap {{
  float: left;
  font-family: {edition.display_font};
  font-size: 2.3em;
  line-height: 1;
  padding: 0.14em 0.24em;
  margin: 0.04em 0.22em 0.04em 0;
  background: {edition.accent};
  color: {edition.paper};
}}
.opening {{ text-indent: 0; }}
"""
        else:
            drop_cap = f""".dropcap {{
  float: left;
  font-family: {edition.display_font};
  font-size: 3em;
  line-height: 0.82;
  padding-right: 0.07em;
  color: {edition.accent};
}}
.opening {{ text-indent: 0; }}
"""

    chapter_rule = ""
    if edition.chapter_rule:
        chapter_rule = f"""h2::after {{
  content: "";
  display: block;
  width: 2.2em;
  height: 1px;
  margin: 0.65em 0 0;
  background: {edition.accent};
  opacity: 0.75;
}}
"""

    chapter_number = ""
    if edition.chapter_number:
        chapter_number = f""".chapter-number {{
  display: block;
  font-family: {edition.display_font};
  font-size: 0.75em;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  text-align: center;
  color: {edition.accent};
  margin-bottom: 1em;
  break-after: avoid;
  page-break-after: avoid;
}}
"""

    chapter_art = ""
    if edition.art:
        chapter_art = """.chapter-art { text-align: center; margin: 0 0 1.4em; }
.chapter-art img { width: 100%; max-width: 100%; height: auto; }
"""

    border_css = ""
    b_style = getattr(edition, "border_style", "none")
    if b_style == "double":
        border_css = f""".titlepage, section {{ border: 3px double {edition.accent}; padding: 1.2em; }}
"""
    elif b_style == "single":
        border_css = f""".titlepage, section {{ border: 1.5px solid {edition.accent}; padding: 1.2em; }}
"""
    elif b_style == "rules":
        border_css = f""".titlepage, section {{ border-top: 2px solid {edition.accent}; border-bottom: 1px solid {edition.accent}; padding: 1em 0; }}
"""

    return f"""@charset "utf-8";

body {{
  margin: 0 5%;
  font-family: {edition.body_font};
  color: {edition.ink};
  line-height: 1.5;
  text-align: justify;
}}
h1, h2 {{
  font-family: {edition.display_font};
  font-weight: {edition.display_weight};
  letter-spacing: {edition.display_tracking};
  text-transform: {edition.display_transform};
  text-align: left;
  line-height: 1.2;
  page-break-before: always;
}}
h1 {{ font-size: 1.6em; margin: 2em 0 1em; break-after: avoid; page-break-after: avoid; }}
h2 {{ font-size: 1.3em; margin: 1.6em 0 0.8em; break-after: avoid; page-break-after: avoid; }}
h3 {{ font-size: 1.1em; margin: 1.4em 0 0.6em; text-align: left; font-style: italic; break-after: avoid; page-break-after: avoid; }}
p {{ margin: 0; text-indent: 1.4em; }}
h1 + p, h2 + p, h3 + p, blockquote + p, .scene-break + p, .chapter-number + p, .opening {{
  text-indent: 0;
}}
.scene-break {{
  text-align: center;
  text-indent: 0;
  margin: 1.4em 0;
  letter-spacing: 0.4em;
  color: {edition.accent};
}}
/* Left-aligned, not justified: short quotes on a narrow screen would
   otherwise stretch their word spacing into visible rivers. */
blockquote {{ margin: 1.2em 2em; font-style: italic; text-align: left; }}
blockquote p {{ text-indent: 0; }}
.titlepage {{ text-align: center; page-break-after: always; }}
.titlepage h1 {{ text-align: center; page-break-before: avoid; }}
.titlepage .author {{ margin-top: 2em; font-size: 1.1em; }}
{drop_cap}{chapter_rule}{chapter_number}{chapter_art}{border_css}"""


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
    parts = [f'  <h1 {_CENTERED}>{inline.render(document.title)}</h1>']
    if meta.get("subtitle"):
        parts.append(
            f'  <p class="subtitle" {_CENTERED}>{inline.render(meta["subtitle"])}</p>'
        )
    parts.append(
        f'  <p class="author" {_CENTERED}>{inline.escape(meta.get("author", ""))}</p>'
    )
    sections = [
        f'<section class="titlepage" epub:type="titlepage" {_CENTERED}>\n'
        + "\n".join(parts)
        + "\n</section>"
    ]
    copyright_line = render_print._copyright_text(meta)
    if copyright_line:
        sections.append(
            '<section class="copyright-page" epub:type="copyright-page">\n'
            f'  <p style="text-indent: 0;">{inline.render(copyright_line)}</p>\n'
            "</section>"
        )
    if meta.get("dedication"):
        sections.append(
            f'<section class="dedication-page" epub:type="dedication" {_CENTERED}>\n'
            f'  <p {_CENTERED}><em>{inline.render(str(meta["dedication"]))}</em></p>\n'
            "</section>"
        )
    return "\n".join(sections)


def _chapter_xhtml(chapter, document, edition, has_art):
    scene_break = (
        f'<p class="scene-break" style="text-align: center; text-indent: 0;">'
        f"{inline.escape(edition.scene_break)}</p>"
    )

    opener = []
    if has_art:
        opener.append(
            f'  <div class="chapter-art" {_CENTERED}>'
            f'<img src="art/chap-{chapter.number:03d}.svg" alt="" /></div>'
        )
    number_label, display_title = chapter.heading_parts(edition.chapter_number)
    if number_label:
        opener.append(
            f'  <span class="chapter-number" {_CENTERED}>{inline.escape(number_label)}</span>'
        )
    if display_title:
        opener.append(f'  <h2 id="{chapter.slug}">{inline.render(display_title)}</h2>')

    prose = body.blocks_to_html(
        chapter.blocks, heading_level=3, indent="  ",
        scene_break=scene_break, drop_cap=edition.drop_cap,
        drop_cap_letter=getattr(edition, "drop_cap_letter", None),
    )
    inner = '<section epub:type="chapter">\n' + "\n".join(opener + prose) + "\n</section>"
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


def _package_opf(document, book_uuid, modified, edition, art_numbers, cover_item=None):
    meta = document.meta
    language = meta.get("language", "en")

    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="style" href="style.css" media-type="text/css"/>',
        '    <item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>',
    ]
    if cover_item:
        cover_href, cover_media = cover_item
        manifest.append(
            f'    <item id="cover-image" href="{cover_href}" '
            f'media-type="{cover_media}" properties="cover-image"/>'
        )
    spine = ['    <itemref idref="titlepage"/>', '    <itemref idref="nav"/>']

    for chapter in document.chapters:
        item_id = f"chap{chapter.number:03d}"
        manifest.append(
            f'    <item id="{item_id}" href="chap-{chapter.number:03d}.xhtml" '
            'media-type="application/xhtml+xml"/>'
        )
        spine.append(f'    <itemref idref="{item_id}"/>')

    for number in art_numbers:
        manifest.append(
            f'    <item id="art{number:03d}" href="art/chap-{number:03d}.svg" '
            'media-type="image/svg+xml"/>'
        )

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


def render(document, out_path, edition=None):
    """Write the Document to out_path as an EPUB 3 file. Returns out_path."""
    edition = edition or editions.from_meta(document.meta)
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

    artwork = {}
    if edition.art:
        for chapter in document.chapters:
            svg = art.render(
                edition.art,
                seed=f"{edition.key}|{chapter.number}|{inline.plain(chapter.title)}",
                ink=edition.ink,
                accent=edition.accent,
                title=inline.plain(chapter.title),
            )
            if svg:
                artwork[chapter.number] = (
                    '<?xml version="1.0" encoding="utf-8"?>\n' + svg
                )

    cover_href = "cover.svg"
    cover_media = "image/svg+xml"
    cover_data = None
    custom_cover = meta.get("cover")
    if custom_cover:
        cover_path = Path(str(custom_cover))
        if not cover_path.is_absolute() and document.source_path:
            candidate = Path(document.source_path).parent / cover_path
            if candidate.is_file():
                cover_path = candidate
        ext = cover_path.suffix.lower()
        if cover_path.is_file() and ext in _COVER_MEDIA_TYPES:
            cover_href = f"cover{ext}"
            cover_media = _COVER_MEDIA_TYPES[ext]
            cover_data = cover_path.read_bytes()

    if cover_data is None:
        cover_data = art.render_cover(
            edition,
            title=inline.plain(document.title),
            subtitle=inline.plain(str(meta.get("subtitle", ""))),
            author=str(meta.get("author", "")),
        ).encode("utf-8")

    with zipfile.ZipFile(out_path, "w") as archive:
        # Must be first and stored, per the EPUB OCF spec.
        write(archive, "mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        write(archive, "META-INF/container.xml", CONTAINER_XML)
        write(archive, "OEBPS/style.css", build_style(edition))
        write(
            archive,
            "OEBPS/content.opf",
            _package_opf(
                document,
                book_uuid,
                modified,
                edition,
                sorted(artwork),
                cover_item=(cover_href, cover_media),
            ),
        )
        write(archive, f"OEBPS/{cover_href}", cover_data)
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
                _chapter_xhtml(chapter, document, edition, chapter.number in artwork),
            )
        for number, svg in sorted(artwork.items()):
            write(archive, f"OEBPS/art/chap-{number:03d}.svg", svg)

    return out_path
