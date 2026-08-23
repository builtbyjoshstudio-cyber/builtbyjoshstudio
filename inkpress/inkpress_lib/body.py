#!/usr/bin/env python3
"""
body.py — render chapter blocks to HTML.

The split point of the pipeline. Every target calls this for prose and then
wraps the result in its own chrome, so a paragraph is marked up identically in
the site page, the EPUB and the print build. Only the wrapper differs.
"""
from . import inline
from . import manuscript as ms

SCENE_BREAK_HTML = '<p class="scene-break" role="separator">* * *</p>'


def apply_drop_cap(html):
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

    opener = html[start:index + 1]
    return f'{html[:start]}<span class="dropcap">{opener}</span>{html[index + 1:]}'


def blocks_to_html(blocks, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML,
                   drop_cap=False):
    """Convert a chapter's blocks to a list of HTML strings.

    drop_cap marks the first paragraph so tiers 2 and 3 can set an opening
    capital; tier 1 leaves it alone.
    """
    out = []
    drop_cap_pending = drop_cap

    for block in blocks:
        if block.kind == ms.SCENE_BREAK:
            out.append(f"{indent}{scene_break}")

        elif block.kind == ms.SECTION:
            tag = f"h{min(heading_level + 1, 6)}"
            out.append(f"{indent}<{tag}>{inline.render(block.text)}</{tag}>")

        elif block.kind == ms.BLOCKQUOTE:
            lines = [inline.render(line) for line in block.text.split("\n") if line.strip()]
            inner = "<br />\n".join(f"{indent}    {line}" for line in lines)
            out.append(f"{indent}<blockquote>\n{indent}  <p>\n{inner}\n{indent}  </p>\n{indent}</blockquote>")

        elif block.kind == ms.PARAGRAPH:
            paragraph = inline.render(block.text.replace("\n", " "))
            if drop_cap_pending:
                paragraph = apply_drop_cap(paragraph)
                drop_cap_pending = False
                out.append(f'{indent}<p class="opening">{paragraph}</p>')
            else:
                out.append(f"{indent}<p>{paragraph}</p>")

    return out


def chapter_to_html(chapter, heading_level=2, indent="  ", include_heading=True,
                    scene_break=SCENE_BREAK_HTML, drop_cap=False):
    """Convert one chapter, optionally with its own heading, to an HTML string."""
    parts = []

    if include_heading and not chapter.implicit:
        tag = f"h{min(heading_level, 6)}"
        parts.append(f'{indent}<{tag} id="{chapter.slug}">{inline.render(chapter.title)}</{tag}>')

    parts.extend(
        blocks_to_html(chapter.blocks, heading_level=heading_level, indent=indent,
                       scene_break=scene_break, drop_cap=drop_cap)
    )
    return "\n".join(parts)


def document_to_html(document, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML,
                     drop_cap=False):
    """Convert every chapter to one HTML string — used by the site renderer."""
    return "\n\n".join(
        chapter_to_html(chapter, heading_level=heading_level, indent=indent,
                        scene_break=scene_break, drop_cap=drop_cap)
        for chapter in document.chapters
    )
