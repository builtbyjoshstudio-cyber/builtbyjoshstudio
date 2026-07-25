#!/usr/bin/env python3
"""
typography.py — turn typewriter punctuation into typeset punctuation.

Stage 2 of the pipeline. Runs on raw block text before any HTML exists, so it
never has to reason about tags. Code spans and link targets are masked out
first: a URL must keep its straight quotes and hyphens intact, and code should
read exactly as typed.

Transforms:
    ...             ->  … (ellipsis)
    ---             ->  — (em dash)
    --              ->  – (en dash)
    "quoted"        ->  “quoted” (directional double quotes)
    'quoted'        ->  ‘quoted’ (directional single quotes)
    don't / '90s    ->  don’t / ’90s (apostrophe, not an opening quote)
"""
import re

ELLIPSIS = "…"
EM_DASH = "—"
EN_DASH = "–"
LEFT_DOUBLE = "“"
RIGHT_DOUBLE = "”"
LEFT_SINGLE = "‘"
RIGHT_SINGLE = "’"

# Characters after which a quote must be an opening quote.
_OPENERS = set(" \t\n([{<" + EM_DASH + EN_DASH + LEFT_DOUBLE + LEFT_SINGLE)

_CODE_SPAN_RE = re.compile(r"`[^`]*`")
_LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
_PLACEHOLDER = "\x00MASK{}\x00"


def _mask(text):
    """Replace code spans and link targets with placeholders. Returns (text, store)."""
    store = []

    def take(match):
        store.append(match.group(0))
        return _PLACEHOLDER.format(len(store) - 1)

    text = _CODE_SPAN_RE.sub(take, text)
    text = _LINK_TARGET_RE.sub(take, text)
    return text, store


def _unmask(text, store):
    for index, original in enumerate(store):
        text = text.replace(_PLACEHOLDER.format(index), original)
    return text


def _dashes(text):
    text = text.replace("...", ELLIPSIS)
    text = text.replace(". . .", ELLIPSIS)
    # Longest first so --- never gets eaten by the -- rule.
    text = re.sub(r"(?<!-)---(?!-)", EM_DASH, text)
    text = re.sub(r"(?<!-)--(?!-)", EN_DASH, text)
    return text


def _quotes(text):
    out = []
    previous = " "

    for index, char in enumerate(text):
        nxt = text[index + 1] if index + 1 < len(text) else ""

        if char == '"':
            out.append(LEFT_DOUBLE if previous in _OPENERS else RIGHT_DOUBLE)
        elif char == "'":
            if previous.isalnum() or previous in (RIGHT_DOUBLE, RIGHT_SINGLE):
                # Mid-word: don't, rock'n'roll, riders'
                out.append(RIGHT_SINGLE)
            elif previous in _OPENERS and nxt.isdigit():
                # Elided decade: '90s
                out.append(RIGHT_SINGLE)
            elif previous in _OPENERS:
                out.append(LEFT_SINGLE)
            else:
                out.append(RIGHT_SINGLE)
        else:
            out.append(char)

        previous = out[-1] if out else " "

    return "".join(out)


def apply(text):
    """Apply all typographic transforms to a chunk of plain text."""
    if not text:
        return text
    masked, store = _mask(text)
    masked = _dashes(masked)
    masked = _quotes(masked)
    return _unmask(masked, store)
