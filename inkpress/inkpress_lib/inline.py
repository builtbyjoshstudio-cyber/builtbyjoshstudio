#!/usr/bin/env python3
"""
inline.py — convert inline markdown to HTML, escaping everything else.

Shared by every renderer so the site page, the EPUB and the print build all
agree on what "*emphasis*" means. Escaping happens first and markup is written
with placeholders, which means a manuscript containing a literal < or & can
never inject tags into the output.

Supported: **strong**, *em*, _em_, `code`, [text](href)
"""
import re

_ESCAPES = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"))

_CODE_RE = re.compile(r"`([^`]+)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_STRONG_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.DOTALL)
_EM_STAR_RE = re.compile(r"(?<!\*)\*(?=\S)([^*]+?)(?<=\S)\*(?!\*)", re.DOTALL)
_EM_UNDER_RE = re.compile(r"(?<![A-Za-z0-9_])_(?=\S)([^_]+?)(?<=\S)_(?![A-Za-z0-9_])", re.DOTALL)


def escape(text):
    """Escape HTML-significant characters."""
    for raw, encoded in _ESCAPES:
        text = text.replace(raw, encoded)
    return text


def escape_attr(text):
    """Escape a string for use inside a double-quoted HTML attribute."""
    return escape(text).replace('"', "&quot;")


def render(text):
    """Convert inline markdown in an already-typeset string to HTML."""
    if not text:
        return ""

    store = []

    def stash(html):
        store.append(html)
        return f"\x00INL{len(store) - 1}\x00"

    # Code first: nothing inside a code span is markup.
    text = _CODE_RE.sub(lambda m: stash(f"<code>{escape(m.group(1))}</code>"), text)
    text = _LINK_RE.sub(
        lambda m: stash(f'<a href="{escape_attr(m.group(2))}">{escape(m.group(1))}</a>'),
        text,
    )

    text = escape(text)

    text = _STRONG_RE.sub(r"<strong>\1</strong>", text)
    text = _EM_STAR_RE.sub(r"<em>\1</em>", text)
    text = _EM_UNDER_RE.sub(r"<em>\1</em>", text)

    for index, html in enumerate(store):
        text = text.replace(f"\x00INL{index}\x00", html)

    return text


def plain(text):
    """Strip inline markup entirely — for <title>, meta descriptions, EPUB nav."""
    text = _CODE_RE.sub(r"\1", text)
    text = _LINK_RE.sub(r"\1", text)
    text = _STRONG_RE.sub(r"\1", text)
    text = _EM_STAR_RE.sub(r"\1", text)
    text = _EM_UNDER_RE.sub(r"\1", text)
    return text
