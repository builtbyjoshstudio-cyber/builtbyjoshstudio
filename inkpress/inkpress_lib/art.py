#!/usr/bin/env python3
"""
art.py — typographic borders, ornamental rules, and framed covers.

Replaces procedural picture generation with clean typographic rules and
colored border frames that match the Edition's accent colour and border style:

    ashveil     double-line rule with centered diamond ornament
    systemfall  bracketed hairline rule with geometric end ticks
    vantablack  architectural heavy-over-fine rule

Also renders a clean typographic SVG cover (render_cover) with single or
double colored borders and zero generated illustrations.
"""
import hashlib
import textwrap

VIEW_WIDTH = 600
VIEW_HEIGHT = 32


class _Rng:
    """Small deterministic PRNG. Seeded from text, never from the clock."""

    def __init__(self, seed):
        self._block = hashlib.sha256(str(seed).encode("utf-8")).digest()
        self._index = 0

    def _byte(self):
        if self._index >= len(self._block):
            self._block = hashlib.sha256(self._block).digest()
            self._index = 0
        value = self._block[self._index]
        self._index += 1
        return value

    def unit(self):
        """A float in [0, 1)."""
        return self._byte() / 256.0

    def between(self, low, high):
        return low + (high - low) * self.unit()

    def chance(self, probability):
        return self.unit() < probability


def _fmt(value):
    """Trim float noise so the SVG stays short and diffs stay readable."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def _ashveil(rng, ink, accent):
    """Double-line ornamental rule with a centered diamond."""
    inset = _fmt(rng.between(60, 96))
    right = _fmt(VIEW_WIDTH - float(inset))
    mid = VIEW_WIDTH // 2
    return [
        f'<line x1="{inset}" y1="14" x2="{mid - 16}" y2="14" stroke="{accent}" stroke-width="1.5"/>',
        f'<line x1="{mid + 16}" y1="14" x2="{right}" y2="14" stroke="{accent}" stroke-width="1.5"/>',
        f'<line x1="{inset}" y1="18" x2="{mid - 16}" y2="18" stroke="{ink}" stroke-width="0.7" opacity="0.55"/>',
        f'<line x1="{mid + 16}" y1="18" x2="{right}" y2="18" stroke="{ink}" stroke-width="0.7" opacity="0.55"/>',
        f'<polygon points="{mid},10 {mid + 6},16 {mid},22 {mid - 6},16" fill="{accent}"/>',
    ]


def _systemfall(rng, ink, accent):
    """Geometric bracketed rule with end ticks."""
    inset = _fmt(rng.between(48, 84))
    right = _fmt(VIEW_WIDTH - float(inset))
    mid = VIEW_WIDTH // 2
    return [
        f'<line x1="{inset}" y1="16" x2="{right}" y2="16" stroke="{accent}" stroke-width="1.2"/>',
        f'<line x1="{inset}" y1="10" x2="{inset}" y2="22" stroke="{accent}" stroke-width="1.5"/>',
        f'<line x1="{right}" y1="10" x2="{right}" y2="22" stroke="{accent}" stroke-width="1.5"/>',
        f'<rect x="{mid - 3}" y="13" width="6" height="6" fill="{ VIEW_WIDTH and "#ffffff" }" stroke="{accent}" stroke-width="1.2"/>',
    ]


def _vantablack(rng, ink, accent):
    """Architectural heavy-over-fine double rule."""
    inset = _fmt(rng.between(40, 76))
    right = _fmt(VIEW_WIDTH - float(inset))
    return [
        f'<rect x="{inset}" y="11" width="{_fmt(float(right) - float(inset))}" height="3.5" fill="{accent}"/>',
        f'<line x1="{inset}" y1="19" x2="{right}" y2="19" stroke="{ink}" stroke-width="1"/>',
    ]


_GENERATORS = {
    "ashveil": _ashveil,
    "systemfall": _systemfall,
    "vantablack": _vantablack,
}


def is_available(name):
    return name in _GENERATORS


def _escape_xml(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render(name, seed, ink="#000000", accent="#000000", title=""):
    """Return a clean typographic chapter-header rule SVG for the edition."""
    generator = _GENERATORS.get(name)
    if generator is None:
        return ""

    shapes = generator(_Rng(seed), ink, accent)
    safe_title = _escape_xml(title)
    label = (
        f"<title>Chapter header rule for {safe_title}</title>"
        if safe_title
        else "<title>Chapter header rule</title>"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" '
        f'width="100%" height="{VIEW_HEIGHT}" role="img" '
        f'preserveAspectRatio="xMidYMid meet">'
        f"{label}"
        + "".join(shapes)
        + "</svg>"
    )


def render_cover(edition, title, subtitle="", author="", seed=""):
    """Return a clean typographic 600x900 SVG book cover with colored borders."""
    width, height = 600, 900
    ink = edition.ink
    paper = edition.paper
    accent = edition.accent
    border_style = getattr(edition, "border_style", "double") or "double"
    display_font = _escape_xml(edition.display_font)
    body_font = _escape_xml(edition.body_font)
    safe_title = _escape_xml(title)
    safe_sub = _escape_xml(subtitle)
    safe_author = _escape_xml(author)
    safe_ornament = _escape_xml(edition.scene_break)

    title_lines = textwrap.wrap(str(title).strip() or "Untitled", width=22)[:4]
    font_size = 34 if len(title_lines) == 1 else (30 if len(title_lines) == 2 else 26)
    line_step = int(font_size * 1.28)
    start_y = 290 - ((len(title_lines) - 1) * line_step) // 2
    tspans = "".join(
        f'<tspan x="300" y="{start_y + idx * line_step}">{_escape_xml(line)}</tspan>'
        for idx, line in enumerate(title_lines)
    )
    sub_y = start_y + len(title_lines) * line_step + 24

    sub_el = (
        f'<text x="300" y="{sub_y}" text-anchor="middle" font-family="{body_font}" '
        f'font-size="20" font-style="italic" fill="{ink}" opacity="0.82">{safe_sub}</text>'
        if safe_sub
        else ""
    )

    rule_y = (sub_y + 36) if safe_sub else (start_y + len(title_lines) * line_step + 24)

    border_els = []
    if border_style == "double":
        border_els.append(
            f'<rect x="34" y="34" width="{width - 68}" height="{height - 68}" '
            f'fill="none" stroke="{accent}" stroke-width="3"/>'
        )
        border_els.append(
            f'<rect x="44" y="44" width="{width - 88}" height="{height - 88}" '
            f'fill="none" stroke="{accent}" stroke-width="1" opacity="0.75"/>'
        )
    elif border_style == "single":
        border_els.append(
            f'<rect x="38" y="38" width="{width - 76}" height="{height - 76}" '
            f'fill="none" stroke="{accent}" stroke-width="2"/>'
        )
    elif border_style == "rules":
        border_els.append(
            f'<line x1="48" y1="54" x2="{width - 48}" y2="54" stroke="{accent}" stroke-width="2.5"/>'
        )
        border_els.append(
            f'<line x1="48" y1="{height - 54}" x2="{width - 48}" y2="{height - 54}" stroke="{accent}" stroke-width="2.5"/>'
        )

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">'
        f"<title>{safe_title}</title>"
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{paper}"/>'
        + "".join(border_els)
        + f'<text x="300" y="{start_y}" text-anchor="middle" font-family="{display_font}" '
        f'font-size="{font_size}" font-weight="{_escape_xml(edition.display_weight)}" '
        f'fill="{ink}">{tspans}</text>'
        f"{sub_el}"
        f'<line x1="220" y1="{rule_y}" x2="380" y2="{rule_y}" stroke="{accent}" stroke-width="1.5"/>'
        f'<text x="300" y="{rule_y + 42}" text-anchor="middle" font-family="{display_font}" '
        f'font-size="18" fill="{accent}">{safe_ornament}</text>'
        f'<text x="300" y="790" text-anchor="middle" font-family="{display_font}" '
        f'font-size="18" letter-spacing="3" fill="{ink}">{safe_author.upper()}</text>'
        "</svg>"
    )
