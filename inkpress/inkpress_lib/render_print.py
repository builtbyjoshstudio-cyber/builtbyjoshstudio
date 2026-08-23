#!/usr/bin/env python3
"""
render_print.py — render a Document as print-ready paged HTML.

Emits a single HTML file using CSS Paged Media (@page), which any of
WeasyPrint, Prince, PagedJS or a browser's "Print to PDF" can turn into a
KDP-ready interior. Nothing here shells out — the PDF step is left to whatever
tool is on the machine, so the pipeline itself stays dependency-free.

The Edition object supplies fonts, colours, chapter treatment and ornaments, so
tier 1 and tier 3 differ in data rather than in branches through this file.

Trim size, margins and gutter come from front matter:
    trim: 6x9           inches, KDP's most common paperback trim
    margin: 0.75in
    gutter: 0.25in      extra inner margin for the bound edge
"""
from . import art, body, editions, inline

DEFAULT_TRIM = "6x9"
DEFAULT_MARGIN = "0.75in"
DEFAULT_GUTTER = "0.25in"


def _trim_dimensions(trim):
    """'6x9' -> ('6in', '9in'). Falls back to the KDP default."""
    text = str(trim).strip().lower()
    if "x" in text and "in" not in text and " " not in text:
        width, _, height = text.partition("x")
        try:
            return f"{float(width):g}in", f"{float(height):g}in"
        except ValueError:
            pass
    if " " in text:
        width, _, height = text.partition(" ")
        return width.strip(), height.strip()
    return "6in", "9in"


def _trim_to_size(trim):
    """'6x9' -> '6in 9in'. Passes through anything already CSS-shaped."""
    width, height = _trim_dimensions(trim)
    return f"{width} {height}"


def _scene_break_html(edition):
    return (
        f'<p class="scene-break" role="separator">'
        f"{inline.escape(edition.scene_break)}</p>"
    )


def build_css(document, edition=None):
    edition = edition or editions.resolve()
    meta = document.meta
    trim_width, trim_height = _trim_dimensions(meta.get("trim", DEFAULT_TRIM))
    size = f"{trim_width} {trim_height}"
    margin = meta.get("margin", DEFAULT_MARGIN)
    gutter = meta.get("gutter", DEFAULT_GUTTER)
    title = inline.plain(document.title).replace('"', '\\"')
    author = str(meta.get("author", "")).replace('"', '\\"')

    # Screen preview: draw each section as a physical sheet at the real trim
    # size. Without this the file is laid out at browser-window width, which
    # makes absolute-unit spacing and ::first-line rules look wrong even when
    # they are correct for print.
    screen = f"""@media screen {{
  body {{
    background: #d9d9dc;
    padding: 24px 0;
  }}
  .titlepage, .chapter {{
    width: {trim_width};
    min-height: {trim_height};
    margin: 0 auto 24px;
    padding: {margin};
    box-sizing: border-box;
    background: {edition.paper};
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.28);
  }}
  .sheet-note {{
    max-width: {trim_width};
    margin: 0 auto 16px;
    font-family: -apple-system, Segoe UI, sans-serif;
    font-size: 12px;
    color: #45454b;
    text-align: center;
  }}
}}

@media print {{
  .sheet-note {{ display: none; }}
}}
"""

    drop_cap = ""
    if edition.drop_cap:
        drop_cap = f"""
.opening .dropcap {{
  float: left;
  font-family: {edition.display_font};
  font-size: 3.05em;
  line-height: 0.82;
  padding: 0.06em 0.08em 0 0;
  margin-right: 0.02em;
  color: {edition.accent};
}}
.opening {{ text-indent: 0; }}
"""

    chapter_rule = ""
    if edition.chapter_rule:
        chapter_rule = f"""
.chapter h2::after {{
  content: "";
  display: block;
  width: 2.2em;
  height: 1px;
  margin: 0.9em auto 0;
  background: {edition.accent};
  opacity: 0.75;
}}
"""

    chapter_number = ""
    if edition.chapter_number:
        chapter_number = f"""
.chapter-number {{
  display: block;
  font-family: {edition.display_font};
  font-size: 9pt;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  text-align: center;
  color: {edition.accent};
  margin-bottom: 1.1em;
}}
"""

    opener_art = ""
    if edition.art:
        opener_art = """
.chapter-art {
  display: block;
  width: 100%;
  margin: 0 0 1.6em;
}
.chapter-art svg { display: block; width: 100%; height: auto; }
@media print { .chapter-art { break-inside: avoid; } }
"""

    return screen + f"""
@page {{
  size: {size};
  margin: {margin};

  @bottom-center {{
    content: counter(page);
    font-family: {edition.body_font};
    font-size: 9pt;
    color: #444;
  }}
}}

@page :left {{
  margin-right: calc({margin} + {gutter});
  @top-left {{
    content: "{author}";
    font-family: {edition.display_font};
    font-size: 8.5pt;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #555;
  }}
}}

@page :right {{
  margin-left: calc({margin} + {gutter});
  @top-right {{
    content: "{title}";
    font-family: {edition.display_font};
    font-size: 8.5pt;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #555;
  }}
}}

/* Front matter carries no running heads or folios. */
@page blank {{ @top-left {{ content: "" }} @top-right {{ content: "" }} @bottom-center {{ content: "" }} }}

html {{ font-family: {edition.body_font}; font-size: 11pt; color: {edition.ink}; }}
body {{ margin: 0; line-height: 1.42; text-align: justify; hyphens: auto; }}

.titlepage {{ page: blank; text-align: center; page-break-after: always; }}
.titlepage h1 {{
  font-family: {edition.display_font};
  font-size: 24pt;
  margin-top: 2.4in;
  font-weight: {edition.display_weight};
  letter-spacing: 0.02em;
}}
.titlepage .subtitle {{ font-size: 13pt; font-style: italic; margin-top: 0.6em; color: #333; }}
.titlepage .author {{
  margin-top: 3em;
  font-family: {edition.display_font};
  font-size: 12pt;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}}

.chapter {{ page-break-before: right; }}
.chapter h2 {{
  font-family: {edition.display_font};
  font-size: 15pt;
  font-weight: {edition.display_weight};
  letter-spacing: {edition.display_tracking};
  text-transform: {edition.display_transform};
  text-align: center;
  /* Absolute, not a percentage: a percentage resolves against container
     width, so it collapses or explodes whenever the layout width changes. */
  margin: {"0.9in" if edition.art else "1.5in"} 0 2.2em;
}}
.chapter h3 {{ font-size: 11.5pt; font-style: italic; text-align: left; margin: 1.8em 0 0.7em; }}

p {{ margin: 0; text-indent: 1.4em; orphans: 2; widows: 2; }}
h2 + p, h3 + p, blockquote + p, .scene-break + p, .chapter-number + p {{ text-indent: 0; }}
/* Small caps on the opening line only. Scoped to the sheet width so it can
   never run away across a full browser window. */
h2 + p::first-line, .opening::first-line {{ font-variant: small-caps; letter-spacing: 0.04em; }}

.scene-break {{
  text-align: center;
  text-indent: 0;
  margin: 1.5em 0;
  letter-spacing: 0.5em;
  color: {edition.accent};
}}
/* Block quotations are set left-aligned, not justified: a short quote across a
   narrow measure would otherwise stretch its word spacing into visible rivers. */
blockquote {{ margin: 1.2em 2.2em; font-size: 10.5pt; font-style: italic; text-align: left; }}
blockquote p {{ text-indent: 0; }}
code {{ font-family: "Courier New", monospace; font-size: 9.5pt; }}
{drop_cap}{chapter_rule}{chapter_number}{opener_art}"""


def render(document, css_override=None, edition=None):
    """Render the Document as print-ready paged HTML. Returns HTML text."""
    edition = edition or editions.from_meta(document.meta)
    meta = document.meta
    css = css_override if css_override is not None else build_css(document, edition)

    title_bits = [f'  <h1>{inline.render(document.title)}</h1>']
    if meta.get("subtitle"):
        title_bits.append(f'  <p class="subtitle">{inline.render(meta["subtitle"])}</p>')
    title_bits.append(f'  <p class="author">{inline.escape(meta.get("author", ""))}</p>')

    scene_break = _scene_break_html(edition)

    chapters = []
    for chapter in document.chapters:
        opener = []

        if edition.art:
            svg = art.render(
                edition.art,
                seed=f"{edition.key}|{chapter.number}|{inline.plain(chapter.title)}",
                ink=edition.ink,
                accent=edition.accent,
                title=inline.plain(chapter.title),
            )
            if svg:
                opener.append(f'  <div class="chapter-art">{svg}</div>')

        if edition.chapter_number and not chapter.implicit:
            opener.append(
                f'  <span class="chapter-number">Chapter {chapter.number}</span>'
            )

        if not chapter.implicit:
            opener.append(
                f'  <h2 id="{chapter.slug}">{inline.render(chapter.title)}</h2>'
            )

        prose = body.blocks_to_html(
            chapter.blocks, heading_level=3, indent="  ",
            scene_break=scene_break, drop_cap=edition.drop_cap,
        )
        inner = "\n".join(part for part in (opener + prose) if part)
        chapters.append(f'<section class="chapter">\n{inner}\n</section>')

    trim_width, trim_height = _trim_dimensions(meta.get("trim", DEFAULT_TRIM))
    note = (
        f'<p class="sheet-note">{inline.escape(edition.label)} &middot; print preview at '
        f"{trim_width} &times; {trim_height}. Each sheet below is one page. "
        "Print to PDF with margins set to None.</p>"
    )

    return f"""<!DOCTYPE html>
<html lang="{inline.escape_attr(meta.get('language', 'en'))}">
<head>
  <meta charset="utf-8" />
  <title>{inline.escape(inline.plain(document.title))} — print interior</title>
  <style>
{css}
  </style>
</head>
<body>
{note}
<section class="titlepage">
{chr(10).join(title_bits)}
</section>

{chr(10).join(chapters)}
</body>
</html>
"""
