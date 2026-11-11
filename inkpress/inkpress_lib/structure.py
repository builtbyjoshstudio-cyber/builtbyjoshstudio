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
_UNNUMBERED_RE = re.compile(
    r"^(?:prologue|epilogue|foreword|preface|introduction|afterword|"
    r"acknowledgm?ents|about the author|author[’']s note|also by\b.*|"
    r"appendix\b.*|glossary)$",
    re.IGNORECASE,
)
_CHAPTER_PREFIX_RE = re.compile(
    r"^chapter\s+(?:[0-9]+|[ivxlcdm]+|one|two|three|four|five|six|seven|eight|"
    r"nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    r"eighteen|nineteen|twenty(?:[\-\s][a-z]+)?|thirty(?:[\-\s][a-z]+)?)"
    r"(?:\s*[:.\-—–]\s*(.+))?$",
    re.IGNORECASE,
)


def is_unnumbered_heading(title):
    plain = inline.plain(str(title)).strip()
    return bool(_UNNUMBERED_RE.match(plain))


def slugify(text):
    """'The Things I Let Go' -> 'the-things-i-let-go'."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return _SLUG_STRIP_RE.sub("-", ascii_only).strip("-") or "untitled"


class Chapter:
    """One chapter: a title plus the blocks beneath it."""

    def __init__(self, title, number, blocks=None, implicit=False,
                 display_number=None, slug=None, part_title=None):
        self.title = title
        self.number = number
        self.blocks = blocks or []
        self.implicit = implicit
        self._slug = slug
        self.part_title = part_title
        if implicit or is_unnumbered_heading(title):
            self.display_number = None
        else:
            self.display_number = number if display_number is None else display_number

    def heading_parts(self, show_chapter_number=False):
        """Return (number_label, display_title) for rendering a chapter opener."""
        if self.implicit:
            return None, None
        if not show_chapter_number or self.display_number is None:
            return None, self.title

        match = _CHAPTER_PREFIX_RE.match(self.title.strip())
        if match:
            remainder = (match.group(1) or "").strip()
            if remainder:
                return f"Chapter {self.display_number}", remainder
            return None, self.title

        return f"Chapter {self.display_number}", self.title

    @property
    def slug(self):
        return self._slug or slugify(self.title)

    @property
    def word_count(self):
        total = 0
        for block in self.blocks:
            if block.kind in (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.SECTION, ms.ULIST, ms.OLIST):
                total += len(_WORD_RE.findall(block.text))
            elif block.kind == ms.CALLOUT:
                _, _, cbody = block.text.partition("\n")
                total += len(_WORD_RE.findall(cbody))
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

    for key in (
        "title",
        "subtitle",
        "standfirst",
        "eyebrow",
        "logline",
        "dedication",
        "epigraph",
        "also_by",
        "about_author",
        "acknowledgments",
        "newsletter_cta",
    ):
        if meta.get(key):
            meta[key] = typography.apply(str(meta[key]))

    chapters = []
    current = None
    numbered_count = 0
    slug_counts = {}
    pending_part = None

    for block in parsed.blocks:
        if block.kind == ms.PART:
            part_text = typography.apply(block.text)
            if current is None or not current.blocks:
                pending_part = part_text
            else:
                pending_part = part_text
            continue

        if block.kind == ms.CHAPTER:
            title_text = typography.apply(block.text)
            if is_unnumbered_heading(title_text):
                disp_num = None
            else:
                numbered_count += 1
                disp_num = numbered_count
            base_slug = slugify(title_text)
            slug_counts[base_slug] = slug_counts.get(base_slug, 0) + 1
            unique_slug = (
                base_slug
                if slug_counts[base_slug] == 1
                else f"{base_slug}-{slug_counts[base_slug]}"
            )
            current = Chapter(
                title_text,
                len(chapters) + 1,
                display_number=disp_num,
                slug=unique_slug,
                part_title=pending_part,
            )
            pending_part = None
            chapters.append(current)
            continue

        if current is None:
            current = Chapter(
                meta.get("title", "Untitled"),
                1,
                implicit=True,
                part_title=pending_part,
            )
            pending_part = None
            chapters.append(current)
        elif pending_part is not None:
            current.blocks.append(ms.Block(ms.PART, pending_part, block.line))
            pending_part = None

        if block.kind in (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.SECTION, ms.ULIST, ms.OLIST):
            block.text = typography.apply(block.text)
        elif block.kind == ms.CALLOUT:
            variant, _, cbody = block.text.partition("\n")
            block.text = f"{variant}\n{typography.apply(cbody)}"
        elif block.kind == ms.IMAGE:
            parts = block.text.split("\t")
            src_txt = parts[0] if len(parts) > 0 else ""
            alt_txt = typography.apply(parts[1]) if len(parts) > 1 and parts[1] else ""
            cap_txt = typography.apply(parts[2]) if len(parts) > 2 and parts[2] else ""
            block.text = f"{src_txt}\t{alt_txt}\t{cap_txt}"

        current.blocks.append(block)

    if not chapters:
        raise ms.ManuscriptError("manuscript produced no chapters")

    return Document(meta, chapters, source_path=parsed.source_path)
