#!/usr/bin/env python3
"""
body.py — render chapter blocks to HTML.

The split point of the pipeline. Every target calls this for prose and then
wraps the result in its own chrome, so a paragraph is marked up identically in
the site page, the EPUB and the print build. Only the wrapper differs.
"""
import re

from . import inline
from . import manuscript as ms

SCENE_BREAK_HTML = '<p class="scene-break" role="separator">* * *</p>'
_SAFE_VARIANT_RE = re.compile(r"[^a-z0-9\-]+")


def parse_image_block(text):
    """Unpack an ms.IMAGE block payload into (src, alt, caption)."""
    parts = str(text).split("\t")
    src = parts[0].strip() if len(parts) > 0 else ""
    alt = parts[1].strip() if len(parts) > 1 else ""
    caption = parts[2].strip() if len(parts) > 2 else ""
    return src, alt, caption


def apply_drop_cap(html, custom_letter=None):
    """Wrap the opening character of a rendered paragraph in a drop-cap span.

    Operates on rendered HTML so it survives inline markup, skipping over any
    leading tags. Leading punctuation rides along with the letter, so a
    paragraph opening on dialogue drops the quote mark and its letter together
    instead of setting a giant quote mark on its own.
    """
    index = 0
    length = len(html)

    while index < length:
        if html[index] == "<":
            close = html.find(">", index)
            if close == -1:
                return html
            index = close + 1
            continue
        break

    start = index
    while index < length and not html[index].isalnum():
        if html[index] == "<":
            return html
        index += 1

    if index >= length:
        return html

    chosen = str(custom_letter).strip()[:1].upper() if custom_letter else ""
    if chosen and html[index].upper() != chosen:
        opener = html[start:index] + chosen
        return f'{html[:start]}<span class="dropcap">{opener}</span>{html[index:]}'

    opener = html[start:index + 1]
    return f'{html[:start]}<span class="dropcap">{opener}</span>{html[index + 1:]}'


def blocks_to_html(blocks, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML,
                   drop_cap=False, drop_cap_letter=None, image_resolver=None):
    """Convert a chapter's blocks to a list of HTML strings.

    drop_cap marks the first paragraph so tiers 2 and 3 can set an opening
    capital; tier 1 leaves it alone.
    """
    out = []
    first_paragraph = True

    for block in blocks:
        if block.kind == ms.SCENE_BREAK:
            out.append(f"{indent}{scene_break}")

        elif block.kind == ms.PART:
            out.append(f'{indent}<div class="part-divider">{inline.render(block.text)}</div>')

        elif block.kind == ms.SECTION:
            tag = f"h{min(heading_level + 1, 6)}"
            out.append(f"{indent}<{tag}>{inline.render(block.text)}</{tag}>")

        elif block.kind == ms.BLOCKQUOTE:
            lines = [inline.render(line) for line in block.text.split("\n") if line.strip()]
            inner = "<br />\n".join(f"{indent}    {line}" for line in lines)
            out.append(f"{indent}<blockquote>\n{indent}  <p>\n{inner}\n{indent}  </p>\n{indent}</blockquote>")

        elif block.kind in (ms.ULIST, ms.OLIST):
            list_tag = "ul" if block.kind == ms.ULIST else "ol"
            items = [
                f"{indent}  <li>{inline.render(line.strip())}</li>"
                for line in block.text.split("\n")
                if line.strip()
            ]
            if items:
                out.append(f"{indent}<{list_tag}>\n" + "\n".join(items) + f"\n{indent}</{list_tag}>")

        elif block.kind == ms.CALLOUT:
            raw_variant, _, cbody = block.text.partition("\n")
            variant = _SAFE_VARIANT_RE.sub("", raw_variant.strip().lower()) or "box"
            chunks = re.split(r"\n\s*\n", cbody.strip())
            paras = []
            for chunk in chunks:
                lines = [inline.render(ln.strip()) for ln in chunk.split("\n") if ln.strip()]
                if lines:
                    joined = f"<br />\n{indent}    ".join(lines)
                    paras.append(f"{indent}  <p>{joined}</p>")
            if paras:
                out.append(
                    f'{indent}<aside class="callout callout-{variant}">\n'
                    + "\n".join(paras)
                    + f"\n{indent}</aside>"
                )

        elif block.kind == ms.IMAGE:
            src, alt, caption = parse_image_block(block.text)
            resolved_src = image_resolver(src) if image_resolver else src
            if resolved_src:
                alt_plain = inline.plain(alt) if alt else ""
                fig_parts = [
                    f'{indent}  <img src="{inline.escape_attr(resolved_src)}" '
                    f'alt="{inline.escape_attr(alt_plain)}" />'
                ]
                if caption:
                    fig_parts.append(f"{indent}  <figcaption>{inline.render(caption)}</figcaption>")
                out.append(
                    f'{indent}<figure class="inline-figure">\n'
                    + "\n".join(fig_parts)
                    + f"\n{indent}</figure>"
                )

        elif block.kind == ms.PARAGRAPH:
            paragraph = inline.render(block.text.replace("\n", " "))
            if first_paragraph:
                first_paragraph = False
                if drop_cap:
                    paragraph = apply_drop_cap(paragraph, custom_letter=drop_cap_letter)
                out.append(f'{indent}<p class="opening">{paragraph}</p>')
            else:
                out.append(f"{indent}<p>{paragraph}</p>")

    return out


def chapter_to_html(chapter, heading_level=2, indent="  ", include_heading=True,
                    scene_break=SCENE_BREAK_HTML, drop_cap=False, drop_cap_letter=None,
                    image_resolver=None):
    """Convert one chapter, optionally with its own heading, to an HTML string."""
    parts = []

    if include_heading and not chapter.implicit:
        tag = f"h{min(heading_level, 6)}"
        parts.append(f'{indent}<{tag} id="{chapter.slug}">{inline.render(chapter.title)}</{tag}>')

    parts.extend(
        blocks_to_html(chapter.blocks, heading_level=heading_level, indent=indent,
                       scene_break=scene_break, drop_cap=drop_cap,
                       drop_cap_letter=drop_cap_letter, image_resolver=image_resolver)
    )
    return "\n".join(parts)


def document_to_html(document, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML,
                     drop_cap=False, image_resolver=None):
    """Convert every chapter to one HTML string — used by the site renderer."""
    return "\n\n".join(
        chapter_to_html(chapter, heading_level=heading_level, indent=indent,
                        scene_break=scene_break, drop_cap=drop_cap,
                        image_resolver=image_resolver)
        for chapter in document.chapters
    )
