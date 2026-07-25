#!/usr/bin/env python3
"""
render_print.py — render a Document as print-ready paged HTML.

Emits a single HTML file using CSS Paged Media (@page), which any of
WeasyPrint, Prince, PagedJS or a browser's "Print to PDF" can turn into a
KDP-ready interior. Nothing here shells out — the PDF step is left to whatever
tool is on the machine, so the pipeline itself stays dependency-free.

Trim size, margins and gutter come from front matter:
    trim: 6x9           inches, KDP's most common paperback trim
    margin: 0.75in
    gutter: 0.25in      extra inner margin for the bound edge
"""
from . import body, inline

DEFAULT_TRIM = "6x9"
DEFAULT_MARGIN = "0.75in"
DEFAULT_GUTTER = "0.25in"


def _trim_to_size(trim):
    """'6x9' -> '6in 9in'. Passes through anything already CSS-shaped."""
    text = str(trim).strip().lower()
    if "x" in text and "in" not in text and " " not in text:
        width, _, height = text.partition("x")
        try:
            return f"{float(width)}in {float(height)}in"
        except ValueError:
            pass
    return text or "6in 9in"


def build_css(document):
    meta = document.meta
    size = _trim_to_size(meta.get("trim", DEFAULT_TRIM))
    margin = meta.get("margin", DEFAULT_MARGIN)
    gutter = meta.get("gutter", DEFAULT_GUTTER)
    title = inline.plain(document.title).replace('"', '\\"')
    author = str(meta.get("author", "")).replace('"', '\\"')

    return f"""@page {{
  size: {size};
  margin: {margin};

  @bottom-center {{
    content: counter(page);
    font-family: Georgia, "Times New Roman", serif;
    font-size: 9pt;
    color: #444;
  }}
}}

@page :left {{
  margin-right: calc({margin} + {gutter});
  @top-left {{
    content: "{author}";
    font-family: Georgia, "Times New Roman", serif;
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
    font-family: Georgia, "Times New Roman", serif;
    font-size: 8.5pt;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #555;
  }}
}}

/* Front matter carries no running heads or folios. */
@page blank {{ @top-left {{ content: "" }} @top-right {{ content: "" }} @bottom-center {{ content: "" }} }}

html {{ font-family: Georgia, "Times New Roman", serif; font-size: 11pt; }}
body {{ margin: 0; line-height: 1.42; text-align: justify; hyphens: auto; }}

.titlepage {{ page: blank; text-align: center; page-break-after: always; }}
.titlepage h1 {{ font-size: 24pt; margin-top: 30%; font-weight: normal; letter-spacing: 0.02em; }}
.titlepage .subtitle {{ font-size: 13pt; font-style: italic; margin-top: 0.6em; color: #333; }}
.titlepage .author {{ margin-top: 3em; font-size: 12pt; letter-spacing: 0.08em; text-transform: uppercase; }}

.chapter {{ page-break-before: right; }}
.chapter h2 {{
  font-size: 15pt;
  font-weight: normal;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-align: center;
  margin: 18% 0 2.4em;
}}
.chapter h3 {{ font-size: 11.5pt; font-style: italic; text-align: left; margin: 1.8em 0 0.7em; }}

p {{ margin: 0; text-indent: 1.4em; orphans: 2; widows: 2; }}
h2 + p, h3 + p, blockquote + p, .scene-break + p {{ text-indent: 0; }}
h2 + p::first-line {{ font-variant: small-caps; letter-spacing: 0.04em; }}

.scene-break {{ text-align: center; text-indent: 0; margin: 1.5em 0; letter-spacing: 0.5em; }}
blockquote {{ margin: 1.2em 2.2em; font-size: 10.5pt; font-style: italic; }}
blockquote p {{ text-indent: 0; }}
code {{ font-family: "Courier New", monospace; font-size: 9.5pt; }}
"""


def render(document, css_override=None):
    """Render the Document as print-ready paged HTML. Returns HTML text."""
    meta = document.meta
    css = css_override if css_override is not None else build_css(document)

    title_bits = [f'  <h1>{inline.render(document.title)}</h1>']
    if meta.get("subtitle"):
        title_bits.append(f'  <p class="subtitle">{inline.render(meta["subtitle"])}</p>')
    title_bits.append(f'  <p class="author">{inline.escape(meta.get("author", ""))}</p>')

    chapters = []
    for chapter in document.chapters:
        heading = (
            f'  <h2 id="{chapter.slug}">{inline.render(chapter.title)}</h2>'
            if not chapter.implicit
            else ""
        )
        prose = body.blocks_to_html(chapter.blocks, heading_level=3, indent="  ")
        inner = "\n".join(part for part in ([heading] + prose) if part)
        chapters.append(f'<section class="chapter">\n{inner}\n</section>')

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
<section class="titlepage">
{chr(10).join(title_bits)}
</section>

{chr(10).join(chapters)}
</body>
</html>
"""
