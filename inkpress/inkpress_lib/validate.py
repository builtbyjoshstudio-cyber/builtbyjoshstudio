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


class ValidationError(Exception):
    """Raised when a Document cannot safely be rendered."""


def _looks_like_iso_date(value):
    parts = str(value).split("-")
    if len(parts) != 3:
        return False
    if not all(part.isdigit() for part in parts):
        return False
    year, month, day = (int(part) for part in parts)
    return len(parts[0]) == 4 and 1 <= month <= 12 and 1 <= day <= 31


def check(document, targets, edition=None):
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

    seen_slugs = {}
    for chapter in document.chapters:
        if not chapter.title.strip():
            errors.append(f"chapter {chapter.number} has an empty title")
        slug = chapter.slug
        if slug in seen_slugs:
            errors.append(
                f"chapter {chapter.number} and chapter {seen_slugs[slug]} both slugify to {slug!r}"
            )
        seen_slugs[slug] = chapter.number

        if not any(block.kind == ms.PARAGRAPH for block in chapter.blocks):
            warnings.append(f"chapter {chapter.number} ({chapter.title!r}) has no paragraphs")

        for block in chapter.blocks:
            if block.kind not in (ms.PARAGRAPH, ms.BLOCKQUOTE):
                continue
            for match in _REPEATED_WORD_RE.finditer(block.text):
                word = match.group(1)
                if word.lower() not in _ALLOWED_DOUBLES:
                    warnings.append(
                        f"chapter {chapter.number} (line {block.line}): "
                        f"repeated word '{word} {word}'"
                    )
            for match in _PLACEHOLDER_RE.finditer(block.text):
                token = match.group(0)
                if token.upper() in ("TODO", "FIXME", "TK") or token.startswith("["):
                    if token.upper() == "TK" and token != "TK":
                        continue
                    warnings.append(
                        f"chapter {chapter.number} (line {block.line}): "
                        f"unresolved placeholder {token!r}"
                    )

    if "site" in targets and document.word_count > 8000:
        warnings.append(
            f"{document.word_count} words is long for a single site page; consider splitting"
        )

    if errors:
        raise ValidationError("\n".join(f"  - {message}" for message in errors))

    return warnings
