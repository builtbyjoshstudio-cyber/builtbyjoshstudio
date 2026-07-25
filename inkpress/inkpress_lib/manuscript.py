#!/usr/bin/env python3
"""
manuscript.py — parse a manuscript source file into front matter + blocks.

Stage 1 of the pipeline. Reads a UTF-8 markdown-ish file with optional YAML
front matter and produces a Manuscript object holding raw metadata and a flat
list of Block tuples. No typography and no HTML happen here — this stage only
answers "what are the pieces and what kind is each one".

Supported front matter (a deliberate YAML subset — no external deps):
    key: value          scalars, quoted or bare
    key:                followed by "  - item" lines for lists
    # comment           ignored

Supported block syntax (prose fiction subset):
    ## Chapter title    chapter break
    ### Section title   section heading inside a chapter
    * * *  /  ---       scene break
    > quoted line       blockquote (consecutive lines merge)
    plain text          paragraph (blank-line separated)
"""
import re
from pathlib import Path

FRONT_MATTER_FENCE = "---"

# Block kinds
CHAPTER = "chapter"
SECTION = "section"
SCENE_BREAK = "scene_break"
BLOCKQUOTE = "blockquote"
PARAGRAPH = "paragraph"

_SCENE_BREAK_RE = re.compile(r"^\s*(\*\s*\*\s*\*|#\s*#\s*#|---+|___+)\s*$")
_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")


class ManuscriptError(Exception):
    """Raised when a manuscript cannot be parsed."""


class Block:
    """One structural unit of the manuscript."""

    __slots__ = ("kind", "text", "line")

    def __init__(self, kind, text, line):
        self.kind = kind
        self.text = text
        self.line = line

    def __repr__(self):
        preview = self.text[:40].replace("\n", " ")
        return f"<Block {self.kind} line={self.line} {preview!r}>"


class Manuscript:
    """Parsed manuscript: front matter dict + ordered blocks."""

    def __init__(self, meta, blocks, source_path=None):
        self.meta = meta
        self.blocks = blocks
        self.source_path = source_path

    def get(self, key, default=None):
        return self.meta.get(key, default)

    def require(self, key):
        value = self.meta.get(key)
        if value in (None, "", []):
            raise ManuscriptError(f"front matter is missing required key: {key}")
        return value


def _strip_quotes(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_front_matter(lines):
    """Parse the YAML subset between --- fences. Returns (meta, body_start_index)."""
    if not lines or lines[0].strip() != FRONT_MATTER_FENCE:
        return {}, 0

    meta = {}
    pending_list_key = None
    index = 1

    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        index += 1

        if stripped == FRONT_MATTER_FENCE:
            return meta, index

        if not stripped or stripped.startswith("#"):
            continue

        list_match = _LIST_ITEM_RE.match(raw)
        if list_match and pending_list_key:
            meta[pending_list_key].append(_strip_quotes(list_match.group(1).strip()))
            continue

        if ":" not in stripped:
            raise ManuscriptError(
                f"line {index}: front matter line is not 'key: value' or '- item': {stripped!r}"
            )

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if not value:
            meta[key] = []
            pending_list_key = key
        else:
            meta[key] = _strip_quotes(value)
            pending_list_key = None

    raise ManuscriptError("front matter opened with '---' but was never closed")


def parse_blocks(lines, offset=0):
    """Turn body lines into a flat list of Blocks."""
    blocks = []
    buffer = []
    buffer_kind = PARAGRAPH
    buffer_line = offset + 1

    def flush():
        nonlocal buffer, buffer_kind
        if buffer:
            text = "\n".join(buffer).strip()
            if text:
                blocks.append(Block(buffer_kind, text, buffer_line))
        buffer = []
        buffer_kind = PARAGRAPH

    for position, raw in enumerate(lines):
        line_number = offset + position + 1
        stripped = raw.strip()

        if not stripped:
            flush()
            continue

        if _SCENE_BREAK_RE.match(stripped):
            flush()
            blocks.append(Block(SCENE_BREAK, "", line_number))
            continue

        if stripped.startswith("### "):
            flush()
            blocks.append(Block(SECTION, stripped[4:].strip(), line_number))
            continue

        if stripped.startswith("## "):
            flush()
            blocks.append(Block(CHAPTER, stripped[3:].strip(), line_number))
            continue

        if stripped.startswith("# "):
            # A single leading H1 is the title; front matter owns that, so skip it.
            flush()
            continue

        if stripped.startswith(">"):
            if buffer_kind != BLOCKQUOTE:
                flush()
                buffer_kind = BLOCKQUOTE
                buffer_line = line_number
            buffer.append(stripped.lstrip(">").strip())
            continue

        if buffer_kind == BLOCKQUOTE:
            flush()

        if not buffer:
            buffer_line = line_number
        buffer.append(stripped)

    flush()
    return blocks


def load(path):
    """Read and parse a manuscript file."""
    path = Path(path)
    if not path.is_file():
        raise ManuscriptError(f"manuscript not found: {path}")

    text = path.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    meta, body_start = parse_front_matter(lines)
    blocks = parse_blocks(lines[body_start:], offset=body_start)

    if not blocks:
        raise ManuscriptError(f"{path.name} has front matter but no body content")

    return Manuscript(meta, blocks, source_path=path)
