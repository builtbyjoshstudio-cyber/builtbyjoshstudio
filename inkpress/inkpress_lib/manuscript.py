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
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

FRONT_MATTER_FENCE = "---"

# Block kinds
PART = "part"
CHAPTER = "chapter"
SECTION = "section"
SCENE_BREAK = "scene_break"
BLOCKQUOTE = "blockquote"
ULIST = "ulist"
OLIST = "olist"
CALLOUT = "callout"
IMAGE = "image"
PARAGRAPH = "paragraph"

_SCENE_BREAK_RE = re.compile(
    r"^\s*(?:(?:\*\s*){3,}|(?:#\s*){3,}|#|---+|_{3,}|(?:~\s*){3,})\s*$"
)
_LIST_ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
_ULIST_LINE_RE = re.compile(r"^\s*[-*+]\s+(.+)$")
_OLIST_LINE_RE = re.compile(r"^\s*\d+[.)]\s+(.+)$")
_CALLOUT_OPEN_RE = re.compile(r"^:::\s*([a-zA-Z0-9_\-]+)?\s*$")
_IMAGE_LINE_RE = re.compile(
    r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+["\']([^"\']*)["\'])?\)\s*$'
)
_PART_HEADING_RE = re.compile(
    r"^(?:part|act|book|volume)\s+(?:[0-9]+|[ivxlcdm]+|one|two|three|four|"
    r"five|six|seven|eight|nine|ten)\b",
    re.IGNORECASE,
)
_CHAPTER_NUM_RE = (
    r"(?:[0-9]+|[ivxlcdm]+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty(?:[\-\s][a-z]+)?|thirty(?:[\-\s][a-z]+)?)"
)
_BARE_CHAPTER_RE = re.compile(
    rf"^(?:chapter\s+{_CHAPTER_NUM_RE}(?:\s*[:.\-—–]\s*.+)?"
    r"|prologue(?:\s*[:.\-—–]\s*.+)?"
    r"|epilogue(?:\s*[:.\-—–]\s*.+)?)$",
    re.IGNORECASE,
)
_W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_DC_NS = "{http://purl.org/dc/elements/1.1/}"


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

        if value in ("|", ">"):
            block_lines = []
            while index < len(lines):
                peek_raw = lines[index]
                peek_stripped = peek_raw.strip()
                if peek_stripped == FRONT_MATTER_FENCE:
                    break
                if not peek_stripped:
                    block_lines.append("")
                    index += 1
                    continue
                if peek_raw.startswith(("  ", "\t")):
                    indent_len = 2 if peek_raw.startswith("  ") else 1
                    block_lines.append(peek_raw[indent_len:].rstrip())
                    index += 1
                    continue
                break
            joiner = "\n" if value == "|" else " "
            meta[key] = joiner.join(block_lines).strip()
            pending_list_key = None
        elif not value:
            meta[key] = []
            pending_list_key = key
        else:
            meta[key] = _strip_quotes(value)
            pending_list_key = None

    raise ManuscriptError("front matter opened with '---' but was never closed")


def _is_bare_chapter_heading(text):
    stripped = text.strip()
    if len(stripped) > 80 or stripped.endswith((".", "?", "!", ",", ";", '"', "'")):
        return False
    return bool(_BARE_CHAPTER_RE.match(stripped))


def parse_blocks(lines, offset=0):
    """Turn body lines into a flat list of Blocks."""
    blocks = []
    buffer = []
    buffer_kind = PARAGRAPH
    buffer_line = offset + 1
    has_explicit_h2 = any(raw.strip().startswith("## ") for raw in lines)
    seen_body_block = False

    in_callout = False
    callout_variant = "box"
    callout_lines = []
    callout_start_line = offset + 1

    def flush():
        nonlocal buffer, buffer_kind, seen_body_block
        if buffer:
            text = "\n".join(buffer).strip()
            if text:
                if (
                    not has_explicit_h2
                    and buffer_kind == PARAGRAPH
                    and len(buffer) == 1
                    and _is_bare_chapter_heading(text)
                ):
                    blocks.append(Block(CHAPTER, text, buffer_line))
                else:
                    blocks.append(Block(buffer_kind, text, buffer_line))
                seen_body_block = True
        buffer = []
        buffer_kind = PARAGRAPH

    for position, raw in enumerate(lines):
        line_number = offset + position + 1
        stripped = raw.strip()

        if in_callout:
            if stripped == ":::":
                body_text = "\n".join(callout_lines).strip()
                if body_text:
                    blocks.append(
                        Block(
                            CALLOUT,
                            f"{callout_variant}\n{body_text}",
                            callout_start_line,
                        )
                    )
                    seen_body_block = True
                in_callout = False
                callout_lines = []
            else:
                callout_lines.append(stripped)
            continue

        callout_match = _CALLOUT_OPEN_RE.match(stripped)
        if callout_match:
            flush()
            in_callout = True
            callout_variant = (callout_match.group(1) or "box").strip().lower()
            callout_lines = []
            callout_start_line = line_number
            continue

        if not stripped:
            flush()
            continue

        if _SCENE_BREAK_RE.match(stripped):
            flush()
            blocks.append(Block(SCENE_BREAK, "", line_number))
            seen_body_block = True
            continue

        img_match = _IMAGE_LINE_RE.match(stripped)
        if img_match:
            flush()
            alt_txt = img_match.group(1).strip()
            src_txt = img_match.group(2).strip()
            cap_txt = (img_match.group(3) or "").strip()
            blocks.append(Block(IMAGE, f"{src_txt}\t{alt_txt}\t{cap_txt}", line_number))
            seen_body_block = True
            continue

        if stripped.startswith("### "):
            flush()
            blocks.append(Block(SECTION, stripped[4:].strip(), line_number))
            seen_body_block = True
            continue

        if stripped.startswith("## "):
            flush()
            blocks.append(Block(CHAPTER, stripped[3:].strip(), line_number))
            seen_body_block = True
            continue

        if stripped.startswith("# "):
            flush()
            h1_text = stripped[2:].strip()
            if _PART_HEADING_RE.match(h1_text) or seen_body_block:
                blocks.append(Block(PART, h1_text, line_number))
                seen_body_block = True
            continue

        if stripped.startswith(">"):
            if buffer_kind != BLOCKQUOTE:
                flush()
                buffer_kind = BLOCKQUOTE
                buffer_line = line_number
            buffer.append(stripped.lstrip(">").strip())
            continue

        ulist_match = _ULIST_LINE_RE.match(raw)
        if ulist_match:
            if buffer_kind != ULIST:
                flush()
                buffer_kind = ULIST
                buffer_line = line_number
            buffer.append(ulist_match.group(1).strip())
            continue

        olist_match = _OLIST_LINE_RE.match(raw)
        if olist_match:
            if buffer_kind != OLIST:
                flush()
                buffer_kind = OLIST
                buffer_line = line_number
            buffer.append(olist_match.group(1).strip())
            continue

        if buffer_kind in (BLOCKQUOTE, ULIST, OLIST):
            flush()

        if not buffer:
            buffer_line = line_number
        buffer.append(stripped)

    if in_callout and callout_lines:
        body_text = "\n".join(callout_lines).strip()
        if body_text:
            blocks.append(
                Block(CALLOUT, f"{callout_variant}\n{body_text}", callout_start_line)
            )

    flush()
    return blocks


def _docx_flag_enabled(rpr, tag):
    if rpr is None:
        return False
    el = rpr.find(f"{_W_NS}{tag}")
    if el is None:
        return False
    val = el.get(f"{_W_NS}val", "true").strip().lower()
    return val not in ("0", "false", "none")


def _wrap_inline(text, marker):
    stripped = text.strip()
    if not stripped:
        return text
    lead = text[: len(text) - len(text.lstrip())]
    tail = text[len(text.rstrip()) :]
    return f"{lead}{marker}{stripped}{marker}{tail}"


def _read_docx(path):
    """Extract metadata and markdown-like lines from a Word .docx archive."""
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "word/document.xml" not in names:
                raise ManuscriptError(f"{path.name} is not a valid Word .docx document")
            doc_xml = archive.read("word/document.xml")
            core_xml = archive.read("docProps/core.xml") if "docProps/core.xml" in names else None
    except zipfile.BadZipFile as error:
        raise ManuscriptError(f"could not read .docx file {path.name}: {error}") from error

    doc_meta = {}
    if core_xml:
        try:
            core_root = ET.fromstring(core_xml)
            for tag, key in (
                ("title", "title"),
                ("creator", "author"),
                ("description", "description"),
                ("language", "language"),
            ):
                node = core_root.find(f".//{_DC_NS}{tag}")
                if node is not None and node.text and node.text.strip():
                    doc_meta[key] = node.text.strip()
        except ET.ParseError:
            pass

    try:
        root = ET.fromstring(doc_xml)
    except ET.ParseError as error:
        raise ManuscriptError(f"corrupt XML in {path.name}: {error}") from error

    paragraphs = []
    for p_node in root.iter(f"{_W_NS}p"):
        style = ""
        has_numpr = False
        ppr = p_node.find(f"{_W_NS}pPr")
        if ppr is not None:
            pstyle = ppr.find(f"{_W_NS}pStyle")
            if pstyle is not None:
                raw_style = pstyle.get(f"{_W_NS}val", "")
                style = re.sub(r"[\s\-_]+", "", raw_style).lower()
            if ppr.find(f"{_W_NS}numPr") is not None:
                has_numpr = True

        chunks = []
        for child in p_node:
            if child.tag == f"{_W_NS}r":
                rpr = child.find(f"{_W_NS}rPr")
                run_parts = []
                for item in child:
                    if item.tag == f"{_W_NS}t" and item.text:
                        run_parts.append(item.text)
                    elif item.tag == f"{_W_NS}br":
                        run_parts.append("\n")
                run_text = "".join(run_parts)
                if run_text:
                    if _docx_flag_enabled(rpr, "i"):
                        run_text = _wrap_inline(run_text, "*")
                    if _docx_flag_enabled(rpr, "b"):
                        run_text = _wrap_inline(run_text, "**")
                    chunks.append(run_text)

        text = "".join(chunks).strip()
        if not text:
            continue
        paragraphs.append((style, text, has_numpr))

    has_heading2 = any(st == "heading2" for st, _, _ in paragraphs)
    lines = []
    in_front_matter = False
    prev_was_list = False
    for index, (style, text, has_numpr) in enumerate(paragraphs):
        if index == 0 and text == FRONT_MATTER_FENCE:
            in_front_matter = True
            lines.append(FRONT_MATTER_FENCE)
            continue
        if in_front_matter:
            lines.extend(text.split("\n"))
            if text.strip() == FRONT_MATTER_FENCE or text.endswith(f"\n{FRONT_MATTER_FENCE}"):
                in_front_matter = False
                lines.append("")
            continue

        is_ordered_list = style.startswith("listnumber")
        is_bullet_list = has_numpr or style in ("listparagraph", "listbullet") or style.startswith("listbullet")
        if prev_was_list and not (is_ordered_list or is_bullet_list):
            lines.append("")
            prev_was_list = False

        if is_ordered_list:
            lines.append(f"1. {text.replace(chr(10), ' ')}")
            prev_was_list = True
        elif is_bullet_list:
            lines.append(f"- {text.replace(chr(10), ' ')}")
            prev_was_list = True
        elif style == "title":
            doc_meta.setdefault("title", text)
            lines.extend([f"# {text}", ""])
        elif style == "subtitle":
            doc_meta.setdefault("subtitle", text)
        elif style == "heading1" and (has_heading2 or _PART_HEADING_RE.match(text)):
            lines.extend([f"# {text}", ""])
        elif style in ("heading1", "heading2"):
            lines.extend([f"## {text}", ""])
        elif style == "heading3":
            lines.extend([f"### {text}", ""])
        elif style == "intensequote":
            lines.append("::: box")
            for qline in text.split("\n"):
                lines.append(qline.strip())
            lines.extend([":::", ""])
        elif style in ("quote", "blocktext"):
            for qline in text.split("\n"):
                lines.append(f"> {qline.strip()}")
            lines.append("")
        else:
            lines.extend([text, ""])

    if prev_was_list:
        lines.append("")

    return doc_meta, lines


def load(path):
    """Read and parse a manuscript file (.md, .markdown, .txt, or .docx)."""
    path = Path(path)
    if not path.is_file():
        raise ManuscriptError(f"manuscript not found: {path}")

    doc_meta = {}
    if path.suffix.lower() == ".docx":
        doc_meta, lines = _read_docx(path)
    else:
        text = path.read_text(encoding="utf-8-sig")
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    meta, body_start = parse_front_matter(lines)
    merged_meta = dict(doc_meta)
    merged_meta.update(meta)
    blocks = parse_blocks(lines[body_start:], offset=body_start)

    if not blocks:
        raise ManuscriptError(f"{path.name} has front matter but no body content")

    return Manuscript(merged_meta, blocks, source_path=path)
