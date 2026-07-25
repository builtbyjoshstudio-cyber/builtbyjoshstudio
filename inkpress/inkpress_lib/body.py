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


def blocks_to_html(blocks, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML):
    """Convert a chapter's blocks to a list of HTML strings."""
    out = []

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
            out.append(f"{indent}<p>{paragraph}</p>")

    return out


def chapter_to_html(chapter, heading_level=2, indent="  ", include_heading=True,
                    scene_break=SCENE_BREAK_HTML):
    """Convert one chapter, optionally with its own heading, to an HTML string."""
    parts = []

    if include_heading and not chapter.implicit:
        tag = f"h{min(heading_level, 6)}"
        parts.append(f'{indent}<{tag} id="{chapter.slug}">{inline.render(chapter.title)}</{tag}>')

    parts.extend(
        blocks_to_html(chapter.blocks, heading_level=heading_level, indent=indent,
                       scene_break=scene_break)
    )
    return "\n".join(parts)


def document_to_html(document, heading_level=2, indent="  ", scene_break=SCENE_BREAK_HTML):
    """Convert every chapter to one HTML string — used by the site renderer."""
    return "\n\n".join(
        chapter_to_html(chapter, heading_level=heading_level, indent=indent,
                        scene_break=scene_break)
        for chapter in document.chapters
    )
