#!/usr/bin/env python3
"""
render_site.py — render a Document as a drop-in site page.

Produces a full HTML document matching the shape of the existing writing/
dispatches: head metadata, Open Graph and Twitter cards, BreadcrumbList and
BlogPosting JSON-LD, then an <article class="dispatch"> body.

Site chrome (stylesheet links, analytics, nav, footer) is lifted from a donor
page rather than hardcoded here — pass --chrome-from path/to/an/existing.html
and the output inherits whatever the live site currently uses. Without a donor
the page still renders, just with no nav or footer.
"""
import json
import re

from . import art, body, editions, inline, render_print

DEFAULT_SITE_NAME = "Built By Josh Studio"
DEFAULT_BASE_URL = "https://builtbyjoshstudio.com"

# Styling for the classes inkpress introduces. A site stylesheet has no reason
# to know about .scene-break, so these ship with the page or the prose renders
# unstyled. Kept to single-class selectors so real site CSS outranks nothing it
# actually defines.
BASE_CSS_MINIMAL = """.dispatch-body .scene-break {
    text-align: center;
    text-indent: 0;
    letter-spacing: 0.55em;
    margin: 2.1em 0;
    opacity: 0.55;
  }
  .dispatch-body blockquote {
    margin: 1.7em 0;
    padding-left: 1.1em;
    border-left: 2px solid currentColor;
    font-style: italic;
    opacity: 0.85;
  }
  .dispatch-body blockquote p { text-indent: 0; }
  .dispatch-body .part-divider {
    text-align: center;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    font-size: 1.15rem;
    margin: 3rem 0 1.5rem;
  }
  .dispatch-body .callout {
    margin: 1.6em 0;
    padding: 1em 1.25em;
    border: 1px solid currentColor;
  }
  .dispatch-body .callout p { margin: 0 0 0.55em; text-indent: 0; }
  .dispatch-body .callout p:last-child { margin-bottom: 0; }
  .dispatch-body .callout-system {
    font-family: ui-monospace, "Cascadia Mono", Consolas, monospace;
    font-size: 0.92rem;
    background: rgba(128, 128, 128, 0.08);
  }
  .dispatch-body .callout-letter {
    font-style: italic;
    border: none;
    border-left: 2px solid currentColor;
  }
  .dispatch-body .inline-figure {
    margin: 1.8em 0;
    text-align: center;
  }
  .dispatch-body .inline-figure img { max-width: 100%; height: auto; }
  .dispatch-body .inline-figure figcaption {
    margin-top: 0.5em;
    font-size: 0.88rem;
    font-style: italic;
    opacity: 0.78;
  }
  .dispatch-backmatter {
    margin-top: 3.2rem;
    padding-top: 1.8rem;
    border-top: 1px solid rgba(128, 128, 128, 0.3);
  }
  .dispatch-backmatter .newsletter-cta {
    margin-top: 1.5rem;
    padding: 1.1rem 1.3rem;
    border: 1px solid currentColor;
    text-align: center;
  }"""

# Everything above plus a readable standalone layout, used when no donor page
# supplies the site's own stylesheet.
BASE_CSS_FULL = (
    """:root { color-scheme: light dark; }
  body {
    margin: 0;
    font-family: Georgia, "Iowan Old Style", "Times New Roman", serif;
    line-height: 1.65;
    color: #1c1c1e;
    background: #fdfdfc;
  }
  @media (prefers-color-scheme: dark) {
    body { color: #e8e8ea; background: #16161a; }
  }
  .dispatch { max-width: 40rem; margin: 0 auto; padding: 3rem 1.4rem 5rem; }
  .dispatch-header { margin-bottom: 2.4rem; }
  .dispatch-eyebrow {
    font-family: ui-monospace, "JetBrains Mono", SFMono-Regular, monospace;
    font-size: 0.72rem;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    opacity: 0.62;
    margin-bottom: 0.9rem;
  }
  .dispatch-header h1 {
    font-size: clamp(1.9rem, 5vw, 2.6rem);
    line-height: 1.15;
    margin: 0 0 0.9rem;
    font-weight: 600;
  }
  .dispatch-standfirst { font-size: 1.08rem; opacity: 0.82; margin: 0 0 0.5rem; }
  .dispatch-log {
    font-family: ui-monospace, "JetBrains Mono", SFMono-Regular, monospace;
    font-size: 0.8rem;
    opacity: 0.58;
    margin: 0;
  }
  .dispatch-body > p { margin: 0 0 1.25em; }
  .dispatch-body h2 { font-size: 1.45rem; margin: 2.6rem 0 1rem; line-height: 1.25; }
  .dispatch-body h3 { font-size: 1.12rem; margin: 2rem 0 0.7rem; opacity: 0.9; }
  .dispatch-body a { color: inherit; text-underline-offset: 0.16em; }
  """
    + BASE_CSS_MINIMAL
)

_HEAD_RE = re.compile(r"<head\b[^>]*>(.*?)</head>", re.DOTALL | re.IGNORECASE)
_ASSET_RE = re.compile(
    r"<link\b[^>]*\brel=[\"'](?:stylesheet|preconnect|preload)[\"'][^>]*>"
    r"|<script\b[^>]*>.*?</script>"
    r"|<script\b[^>]*/?>",
    re.DOTALL | re.IGNORECASE,
)
_LD_JSON_RE = re.compile(r"<script\b[^>]*application/ld\+json[^>]*>.*?</script>",
                         re.DOTALL | re.IGNORECASE)


def _extract_balanced(html, tag, attr_hint=None):
    """Return the full outer HTML of the first <tag> (optionally containing attr_hint)."""
    open_re = re.compile(rf"<{tag}\b[^>]*>", re.IGNORECASE)
    close_token = f"</{tag}>"

    for match in open_re.finditer(html):
        if attr_hint and attr_hint not in match.group(0):
            continue

        depth = 1
        cursor = match.end()
        scan = re.compile(rf"<{tag}\b[^>]*>|</{tag}>", re.IGNORECASE)

        while depth and cursor < len(html):
            step = scan.search(html, cursor)
            if not step:
                return None
            depth += -1 if step.group(0).lower().startswith(close_token) else 1
            cursor = step.end()

        if depth == 0:
            return html[match.start():cursor]

    return None


def extract_chrome(donor_html):
    """Pull reusable head assets, nav and footer out of an existing site page."""
    chrome = {"head_assets": "", "nav": "", "footer": ""}

    head_match = _HEAD_RE.search(donor_html)
    if head_match:
        head = _LD_JSON_RE.sub("", head_match.group(1))
        assets = [asset.strip() for asset in _ASSET_RE.findall(head)]
        chrome["head_assets"] = "\n  ".join(assets)

    nav = _extract_balanced(donor_html, "nav", attr_hint="site-nav")
    if nav:
        chrome["nav"] = nav

    footer = _extract_balanced(donor_html, "footer")
    if footer:
        chrome["footer"] = footer

    return chrome


def _url_for(document, base_url, path_prefix):
    return f"{base_url.rstrip('/')}/{path_prefix.strip('/')}/{document.slug}.html"


def _schema_blocks(document, page_url, meta, base_url):
    site_name = meta.get("site_name", DEFAULT_SITE_NAME)
    image = meta.get("image", "")
    title = inline.plain(document.title)

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home",
             "item": f"{base_url.rstrip('/')}/"},
            {"@type": "ListItem", "position": 2, "name": meta.get("section", "Writing"),
             "item": f"{base_url.rstrip('/')}/{meta.get('section_url', 'books.html')}"},
            {"@type": "ListItem", "position": 3, "name": title, "item": page_url},
        ],
    }

    posting = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": meta.get("description", ""),
        "url": page_url,
        "inLanguage": meta.get("language", "en-US"),
        "datePublished": meta.get("date", ""),
        "dateModified": meta.get("modified", meta.get("date", "")),
        "articleSection": meta.get("section", "Fiction"),
        "author": {"@type": "Person", "name": meta.get("author", "")},
        "publisher": {"@type": "Organization", "name": site_name},
        "wordCount": document.word_count,
    }
    if image:
        posting["image"] = image

    return "\n".join(
        f'  <script type="application/ld+json">\n{json.dumps(block, indent=2, ensure_ascii=False)}\n  </script>'
        for block in (breadcrumb, posting)
    )


def _edition_css(edition):
    """Tier styling for the web page: fonts, ornament colour, drop cap."""
    rules = [
        f"  .dispatch-body {{ font-family: {edition.body_font}; }}",
        f"  .dispatch-body .scene-break {{ color: {edition.accent}; }}",
        f"  .dispatch-body .part-divider {{ font-family: {edition.display_font}; color: {edition.accent}; }}",
        f"  .dispatch-body .callout {{ border-color: {edition.accent}; }}",
        f"  .dispatch-backmatter .newsletter-cta {{ border-color: {edition.accent}; }}",
        f"  .dispatch-header h1 {{ font-family: {edition.display_font};"
        f" font-weight: {edition.display_weight};"
        f" letter-spacing: {edition.display_tracking}; }}",
        f"  .dispatch-body h2 {{ font-family: {edition.display_font};"
        f" text-transform: {edition.display_transform};"
        f" letter-spacing: {edition.display_tracking};"
        f" font-weight: {edition.display_weight}; }}",
    ]

    if edition.drop_cap:
        dc_style = getattr(edition, "drop_cap_style", "classic")
        if dc_style == "framed":
            rules.append(
                f"  .dispatch-body .dropcap {{ float: left; font-family: "
                f"{edition.display_font}; font-size: 2.35em; line-height: 1;"
                f" padding: 0.12em 0.22em; margin: 0.04em 0.22em 0.04em 0;"
                f" border: 1.5px solid {edition.accent}; color: {edition.accent}; }}"
            )
        elif dc_style == "boxed":
            rules.append(
                f"  .dispatch-body .dropcap {{ float: left; font-family: "
                f"{edition.display_font}; font-size: 2.35em; line-height: 1;"
                f" padding: 0.14em 0.24em; margin: 0.04em 0.22em 0.04em 0;"
                f" background: {edition.accent}; color: {edition.paper}; }}"
            )
        else:
            rules.append(
                f"  .dispatch-body .dropcap {{ float: left; font-family: "
                f"{edition.display_font}; font-size: 3.1em; line-height: 0.82;"
                f" padding: 0.04em 0.09em 0 0; color: {edition.accent}; }}"
            )
        rules.append("  .dispatch-body .opening { text-indent: 0; }")

    if edition.chapter_rule:
        rules.append(
            f'  .dispatch-body h2::after {{ content: ""; display: block;'
            f" width: 2.2em; height: 1px; margin: 0.65em 0 0;"
            f" background: {edition.accent}; opacity: 0.75; }}"
        )

    if edition.chapter_number:
        rules.append(
            f"  .dispatch-body .chapter-number {{ display: block; font-family: "
            f"{edition.display_font}; font-size: 0.72rem; letter-spacing: 0.3em;"
            f" text-transform: uppercase; color: {edition.accent};"
            f" margin: 2.4rem 0 0.5rem; }}"
        )

    if edition.art:
        rules.append("  .dispatch-body .chapter-art { margin: 2.4rem 0 1.2rem; }")
        rules.append(
            "  .dispatch-body .chapter-art svg { display: block; width: 100%; height: auto; }"
        )

    b_style = getattr(edition, "border_style", "none")
    if b_style == "double":
        rules.append(
            f"  .dispatch {{ border: 4px double {edition.accent}; margin-top: 2rem; margin-bottom: 2rem; }}"
        )
    elif b_style == "single":
        rules.append(
            f"  .dispatch {{ border: 1.5px solid {edition.accent}; margin-top: 2rem; margin-bottom: 2rem; }}"
        )
    elif b_style == "rules":
        rules.append(
            f"  .dispatch-header {{ border-top: 2px solid {edition.accent}; border-bottom: 1px solid {edition.accent}; padding: 1.2rem 0; }}"
        )

    return "\n".join(rules)


def _chapters_html(document, edition):
    """Chapter bodies with the tier's opener treatment."""
    sections = []

    for chapter in document.chapters:
        parts = []

        if getattr(chapter, "part_title", None):
            parts.append(
                f'      <div class="part-divider">{inline.render(chapter.part_title)}</div>'
            )

        if edition.art:
            svg = art.render(
                edition.art,
                seed=f"{edition.key}|{chapter.number}|{inline.plain(chapter.title)}",
                ink=edition.ink,
                accent=edition.accent,
                title=inline.plain(chapter.title),
            )
            if svg:
                parts.append(f'      <div class="chapter-art">{svg}</div>')

        number_label, display_title = chapter.heading_parts(edition.chapter_number)
        if number_label:
            parts.append(
                f'      <span class="chapter-number">{inline.escape(number_label)}</span>'
            )
        if display_title:
            parts.append(
                f'      <h2 id="{chapter.slug}">{inline.render(display_title)}</h2>'
            )

        parts.append(
            body.chapter_to_html(
                chapter,
                heading_level=2,
                indent="      ",
                include_heading=False,
                scene_break=(
                    f'<p class="scene-break" role="separator">'
                    f"{inline.escape(edition.scene_break)}</p>"
                ),
                drop_cap=edition.drop_cap,
                drop_cap_letter=getattr(edition, "drop_cap_letter", None),
            )
        )
        sections.append("\n".join(part for part in parts if part))

    return "\n\n".join(sections)


def render(document, chrome=None, base_url=DEFAULT_BASE_URL, path_prefix="writing",
           base_css=True, edition=None):
    """Render the Document as a complete site page. Returns HTML text.

    base_css ships styling for the classes inkpress introduces. With a chrome
    donor only the gaps are filled (the donor's stylesheet does the rest); with
    no donor the page gets a full readable layout so it is never raw HTML.
    Pass False to emit no <style> block at all.
    """
    meta = document.meta
    edition = edition or editions.from_meta(meta)
    chrome = chrome or {"head_assets": "", "nav": "", "footer": ""}
    has_donor_css = bool(chrome.get("head_assets"))

    style_block = ""
    if base_css:
        rules = BASE_CSS_MINIMAL if has_donor_css else BASE_CSS_FULL
        style_block = (
            f'  <style data-inkpress="base">\n  {rules}\n{_edition_css(edition)}\n  </style>\n'
        )

    title = inline.plain(document.title)
    description = meta.get("description", "")
    page_url = meta.get("url") or _url_for(document, base_url, path_prefix)
    image = meta.get("image", "")
    site_name = meta.get("site_name", DEFAULT_SITE_NAME)

    head_title = meta.get("page_title") or title
    if meta.get("subtitle") and not meta.get("page_title"):
        head_title = f"{title} — {inline.plain(meta['subtitle'])}"

    social = [
        ("og:title", head_title),
        ("og:description", description),
        ("og:type", "article"),
        ("og:url", page_url),
        ("og:site_name", site_name),
    ]
    if image:
        social.append(("og:image", image))

    social_tags = "\n  ".join(
        f'<meta property="{key}" content="{inline.escape_attr(value)}" />'
        for key, value in social
        if value
    )

    twitter = [
        ("twitter:card", "summary_large_image" if image else "summary"),
        ("twitter:title", head_title),
        ("twitter:description", description),
    ]
    if image:
        twitter.append(("twitter:image", image))

    twitter_tags = "\n  ".join(
        f'<meta name="{key}" content="{inline.escape_attr(value)}" />'
        for key, value in twitter
        if value
    )

    header_bits = [f"      <h1>{inline.render(document.title)}</h1>"]
    if meta.get("eyebrow"):
        header_bits.insert(
            0, f'      <div class="dispatch-eyebrow">{inline.render(meta["eyebrow"])}</div>'
        )
    if meta.get("standfirst"):
        header_bits.append(
            f'      <p class="dispatch-standfirst">{inline.render(meta["standfirst"])}</p>'
        )
    if meta.get("logline"):
        header_bits.append(
            f'      <p class="dispatch-log">{inline.render(meta["logline"])}</p>'
        )

    article_body = _chapters_html(document, edition)
    back_sections = render_print.render_back_matter_sections(
        meta, section_class="dispatch-backmatter-section", heading_tag="h2"
    )
    if back_sections:
        article_body = (
            article_body
            + '\n\n      <aside class="dispatch-backmatter">\n'
            + "\n".join(back_sections)
            + "\n      </aside>"
        )

    nav_block = f"\n  {chrome['nav']}\n" if chrome.get("nav") else ""
    footer_block = f"\n  {chrome['footer']}\n" if chrome.get("footer") else ""
    head_assets = f"  {chrome['head_assets']}\n" if chrome.get("head_assets") else ""

    return f"""<!DOCTYPE html>
<html lang="{inline.escape_attr(meta.get('language', 'en'))}" data-theme="light" data-glass="books">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <title>{inline.escape(head_title)}</title>
  <meta name="description" content="{inline.escape_attr(description)}" />
  <meta name="author" content="{inline.escape_attr(meta.get('author', ''))}" />
  <link rel="canonical" href="{inline.escape_attr(page_url)}" />

  {social_tags}
  {twitter_tags}

{_schema_blocks(document, page_url, meta, base_url)}
{head_assets}{style_block}</head>
<body>
{nav_block}
  <article class="dispatch">
    <header class="dispatch-header">
{chr(10).join(header_bits)}
    </header>

    <div class="dispatch-body">
{article_body}
    </div>
  </article>
{footer_block}
</body>
</html>
"""
