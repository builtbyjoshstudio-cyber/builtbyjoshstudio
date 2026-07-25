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

from . import body, inline

DEFAULT_SITE_NAME = "Built By Josh Studio"
DEFAULT_BASE_URL = "https://builtbyjoshstudio.com"

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


def render(document, chrome=None, base_url=DEFAULT_BASE_URL, path_prefix="writing"):
    """Render the Document as a complete site page. Returns HTML text."""
    meta = document.meta
    chrome = chrome or {"head_assets": "", "nav": "", "footer": ""}

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

    article_body = body.document_to_html(document, heading_level=2, indent="      ")

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
{head_assets}</head>
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
