#!/usr/bin/env python3
"""
validate.py — check a Document before anything is written to disk.

Stage 4 of the pipeline, and the reason a bad manuscript fails loudly at the
top instead of producing a subtly broken EPUB. Errors block the build; warnings
print and continue.

Requirements differ per target: the site page needs SEO metadata that an EPUB
does not care about, and the EPUB needs an author and a language that the site
page can infer. Targets are checked only if they were requested.
"""
import re
import struct
from pathlib import Path

from . import body, render_print
from . import manuscript as ms

# Front matter every target needs.
REQUIRED_ALWAYS = ("title", "author", "date")

# Extra front matter per render target.
REQUIRED_BY_TARGET = {
    "site": ("description",),
    "epub": ("language",),
    "print": (),
}

_DATE_HINT = "expected YYYY-MM-DD"
_REPEATED_WORD_RE = re.compile(r"\b([A-Za-z]{2,})\s+\1\b", re.IGNORECASE)
_ALLOWED_DOUBLES = frozenset(
    {"had", "that", "ha", "bye", "no", "there", "very", "so", "now", "blah", "hear"}
)
_PLACEHOLDER_RE = re.compile(r"\b(?:TODO|FIXME|TK)\b|\[\s*(?:TODO|TK|insert\b[^\]]*)\]", re.IGNORECASE)
_PROSE_KINDS = (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.ULIST, ms.OLIST, ms.CALLOUT, ms.IMAGE)


class ValidationError(Exception):
    """Raised when a Document cannot safely be rendered."""


def _image_dimensions(path):
    """Return (width, height) for PNG, JPEG, or GIF files using stdlib only."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return int(width), int(height)
    if len(data) >= 10 and data[:6] in (b"GIF87a", b"GIF89a"):
        width, height = struct.unpack("<HH", data[6:10])
        return int(width), int(height)
    if len(data) >= 4 and data[:2] == b"\xff\xd8":
        idx = 2
        length = len(data)
        while idx < length - 9:
            if data[idx] != 0xFF:
                idx += 1
                continue
            while idx < length and data[idx] == 0xFF:
                idx += 1
            if idx >= length:
                break
            marker = data[idx]
            idx += 1
            if marker in (0xD8, 0xD9) or (0xD0 <= marker <= 0xD7):
                continue
            if idx + 2 > length:
                break
            seg_len = struct.unpack(">H", data[idx:idx + 2])[0]
            if seg_len < 2 or idx + seg_len > length:
                break
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                if idx + 7 <= length:
                    height, width = struct.unpack(">HH", data[idx + 3:idx + 7])
                    return int(width), int(height)
            idx += seg_len
    return None


def estimate_paperback_pages(document):
    """Estimate KDP paperback page count from word count, chapters, and trim."""
    trim = str(document.meta.get("trim", "6x9")).strip().lower()
    words_per_page = {"5x8": 250, "5.25x8": 265, "5.5x8.5": 285, "6x9": 320}.get(trim, 300)
    raw = 6 + int(round(document.word_count / max(words_per_page, 1))) + int(len(document.chapters) * 1.5)
    return raw + (raw % 2)


def _looks_like_iso_date(value):
    parts = str(value).split("-")
    if len(parts) != 3:
        return False
    if not all(part.isdigit() for part in parts):
        return False
    year, month, day = (int(part) for part in parts)
    return len(parts[0]) == 4 and 1 <= month <= 12 and 1 <= day <= 31


def check(document, targets, edition=None, kdp_preflight=False):
    """Validate a Document for the given targets. Returns a list of warnings."""
    errors = []
    warnings = []

    # A tier 3 edition set on a tier 1 or 2 job is almost always a mistake in
    # the order, so say so rather than silently ignoring it.
    if edition is not None and not edition.is_illustrated and document.meta.get("edition"):
        warnings.append(
            f"'edition: {document.meta['edition']}' is ignored on {edition.tier} - "
            "edition styles apply to the illustrated tier only"
        )

    required = set(REQUIRED_ALWAYS)
    for target in targets:
        required.update(REQUIRED_BY_TARGET.get(target, ()))

    for key in sorted(required):
        if not document.meta.get(key):
            errors.append(f"front matter is missing required key for {'/'.join(targets)}: {key}")

    date = document.meta.get("date")
    if date and not _looks_like_iso_date(date):
        errors.append(f"front matter 'date' is {date!r} — {_DATE_HINT}")

    description = document.meta.get("description")
    if description and len(description) > 160:
        warnings.append(
            f"description is {len(description)} chars; search engines truncate near 160"
        )

    if document.word_count == 0:
        errors.append("manuscript contains no prose")

    custom_cover = document.meta.get("cover")
    if custom_cover:
        cover_path = Path(str(custom_cover))
        if not cover_path.is_absolute() and getattr(document, "source_path", None):
            candidate = Path(document.source_path).parent / cover_path
            if candidate.is_file():
                cover_path = candidate
        if not cover_path.is_file():
            warnings.append(f"custom cover file not found: {custom_cover}")
        else:
            dims = _image_dimensions(cover_path)
            if dims is not None:
                width, height = dims
                if width < 600 or height < 900:
                    warnings.append(
                        f"cover image is {width}x{height}px; KDP and ebook stores "
                        "recommend at least 1600x2560px (1.6:1 height:width)"
                    )

    seen_slugs = {}
    seen_titles = {}
    for chapter in document.chapters:
        if not chapter.title.strip():
            errors.append(f"chapter {chapter.number} has an empty title")
        slug = chapter.slug
        if slug in seen_slugs:
            errors.append(
                f"chapter {chapter.number} and chapter {seen_slugs[slug]} both slugify to {slug!r}"
            )
        seen_slugs[slug] = chapter.number

        norm_title = chapter.title.strip().lower()
        if norm_title in seen_titles:
            warnings.append(
                f"chapter {chapter.number} and chapter {seen_titles[norm_title]} "
                f"share the title {chapter.title!r} (linked as #{slug})"
            )
        else:
            seen_titles[norm_title] = chapter.number

        if not any(block.kind in _PROSE_KINDS for block in chapter.blocks):
            warnings.append(f"chapter {chapter.number} ({chapter.title!r}) has no paragraphs")

        for block in chapter.blocks:
            if block.kind == ms.IMAGE:
                src, _, _ = body.parse_image_block(block.text)
                local_img = render_print.resolve_image_path(src, document)
                if local_img is not None and not local_img.is_file():
                    warnings.append(
                        f"chapter {chapter.number} (line {block.line}): "
                        f"inline image file not found: {src}"
                    )
                continue

            if block.kind not in (ms.PARAGRAPH, ms.BLOCKQUOTE, ms.ULIST, ms.OLIST, ms.CALLOUT):
                continue
            probe_text = (
                block.text.partition("\n")[2]
                if block.kind == ms.CALLOUT
                else block.text
            )
            for match in _REPEATED_WORD_RE.finditer(probe_text):
                word = match.group(1)
                if word.lower() not in _ALLOWED_DOUBLES:
                    warnings.append(
                        f"chapter {chapter.number} (line {block.line}): "
                        f"repeated word '{word} {word}'"
                    )
            for match in _PLACEHOLDER_RE.finditer(probe_text):
                token = match.group(0)
                if token.upper() in ("TODO", "FIXME", "TK") or token.startswith("["):
                    if token.upper() == "TK" and token != "TK":
                        continue
                    warnings.append(
                        f"chapter {chapter.number} (line {block.line}): "
                        f"unresolved placeholder {token!r}"
                    )

    if "print" in targets and (kdp_preflight or document.meta.get("isbn")):
        est_pages = estimate_paperback_pages(document)
        if est_pages < 24:
            warnings.append(
                f"estimated paperback length (~{est_pages} pages) is below Amazon KDP's "
                "24-page paperback minimum"
            )

    if "site" in targets and document.word_count > 8000:
        warnings.append(
            f"{document.word_count} words is long for a single site page; consider splitting"
        )

    if errors:
        raise ValidationError("\n".join(f"  - {message}" for message in errors))

    return warnings
