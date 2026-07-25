#!/usr/bin/env python3
"""
structure.py — group flat blocks into chapters and apply typography.

Stage 3 of the pipeline. This is where the shared front-end ends: everything
downstream (site, EPUB, print) consumes the Document produced here, so the
three outputs can never disagree about chapter boundaries, scene breaks or
punctuation.

A manuscript with no "## " headings becomes a single implicit chapter titled
from the front matter, which is the normal shape for a short dispatch.
"""
import re
import unicodedata

from . import manuscript as ms
from . import inline, typography

_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")
_WORD_RE = re.compile(r"[A-Za-z0-9’'\-]+")


def slugify(text):
    """'The Things I Let Go' -> 'the-things-i-let-go'."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return _SLUG_STRIP_RE.sub("-", ascii_only).strip("-") or "untitled"


class Chapter:
    """One chapter: a title plus the blocks beneath it."""

    def __init__(self, title, number, blocks=None, implicit=False):
        self.title = title
        self.number = number
        self.blocks = blocks or []
        self.implicit = implicit

    @property
    def slug(self):
        return slugify(self.title)

    @property
    def word_count(self):
        total = 0
        for block in self.blocks:
            if block.kind in (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.SECTION):
                total += len(_WORD_RE.findall(block.text))
        return total


class Document:
    """The typeset, structured manuscript that renderers consume."""

    def __init__(self, meta, chapters, source_path=None):
        self.meta = meta
        self.chapters = chapters
        self.source_path = source_path

    @property
    def title(self):
        return self.meta.get("title", "Untitled")

    @property
    def slug(self):
        return self.meta.get("slug") or slugify(self.title)

    @property
    def word_count(self):
        return sum(chapter.word_count for chapter in self.chapters)

    @property
    def has_real_chapters(self):
        return not (len(self.chapters) == 1 and self.chapters[0].implicit)

    def plain_title(self):
        return inline.plain(self.title)


def build(parsed):
    """Manuscript -> Document. Applies typography to every text-bearing block."""
    meta = dict(parsed.meta)

    for key in ("title", "subtitle", "standfirst", "eyebrow", "logline"):
        if meta.get(key):
            meta[key] = typography.apply(str(meta[key]))

    chapters = []
    current = None

    for block in parsed.blocks:
        if block.kind == ms.CHAPTER:
            current = Chapter(typography.apply(block.text), len(chapters) + 1)
            chapters.append(current)
            continue

        if current is None:
            current = Chapter(
                meta.get("title", "Untitled"), 1, implicit=True
            )
            chapters.append(current)

        if block.kind in (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.SECTION):
            block.text = typography.apply(block.text)

        current.blocks.append(block)

    if not chapters:
        raise ms.ManuscriptError("manuscript produced no chapters")

    return Document(meta, chapters, source_path=parsed.source_path)
