#!/usr/bin/env python3
"""
art.py — generated chapter-opener art for the tier 3 editions.

Each edition has its own art direction, drawn as SVG at build time rather than
shipped as image files: nothing to license, nothing to lose track of, and the
art recolours itself with the edition palette.

    ashveil     charcoal epic - layered ash ridge with ember flecks
    systemfall  geometric, system-flavoured - node grid and hairline traces
    vantablack  high-contrast noir - solid black bar cut by negative space

Output is deterministic. The generator is seeded from the chapter title and
number, so a given chapter draws the same art on every rebuild - which is what
keeps EPUB builds byte-identical - while different chapters differ from each
other.
"""
import hashlib

VIEW_WIDTH = 600
VIEW_HEIGHT = 120


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
    """Charcoal epic: a jagged ridge under drifting ash, flecked with embers."""
    parts = []

    # Three ridge layers, back to front, each darker and lower.
    for layer in range(3):
        opacity = 0.18 + layer * 0.22
        base = 84 - layer * 6
        points = [f"0,{_fmt(base + rng.between(-4, 4))}"]
        x = 0.0
        while x < VIEW_WIDTH:
            x += rng.between(28, 62)
            peak = base - rng.between(10, 34) + layer * 4
            points.append(f"{_fmt(min(x, VIEW_WIDTH))},{_fmt(peak)}")
        points.append(f"{VIEW_WIDTH},{VIEW_HEIGHT}")
        points.append(f"0,{VIEW_HEIGHT}")
        parts.append(
            f'<polygon points="{" ".join(points)}" fill="{ink}" opacity="{opacity:.2f}"/>'
        )

    # Ash drifting above the ridge.
    for _ in range(26):
        cx = rng.between(0, VIEW_WIDTH)
        cy = rng.between(6, 62)
        radius = rng.between(0.6, 2.1)
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(radius)}" '
            f'fill="{ink}" opacity="{rng.between(0.08, 0.3):.2f}"/>'
        )

    # Embers, sparse and warm.
    for _ in range(7):
        cx = rng.between(20, VIEW_WIDTH - 20)
        cy = rng.between(40, 92)
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(rng.between(1.1, 2.4))}" '
            f'fill="{accent}" opacity="{rng.between(0.5, 0.95):.2f}"/>'
        )

    parts.append(
        f'<rect x="0" y="{VIEW_HEIGHT - 2}" width="{VIEW_WIDTH}" height="1" '
        f'fill="{ink}" opacity="0.55"/>'
    )
    return parts


def _systemfall(rng, ink, accent):
    """Geometric and system-flavoured: a node grid over orthogonal traces."""
    parts = []
    columns = 12
    spacing = VIEW_WIDTH / (columns + 1)
    baseline = 74

    # Orthogonal traces stepping across the band.
    x = spacing * 0.5
    y = baseline
    path = [f"M {_fmt(x)} {_fmt(y)}"]
    while x < VIEW_WIDTH - spacing:
        run = rng.between(spacing * 0.8, spacing * 2.0)
        x = min(x + run, VIEW_WIDTH - 6)
        path.append(f"L {_fmt(x)} {_fmt(y)}")
        if rng.chance(0.6):
            y = max(22, min(baseline + 22, y + rng.between(-24, 24)))
            path.append(f"L {_fmt(x)} {_fmt(y)}")
    parts.append(
        f'<path d="{" ".join(path)}" fill="none" stroke="{accent}" '
        'stroke-width="1" opacity="0.75"/>'
    )

    # Node grid.
    for column in range(1, columns + 1):
        cx = column * spacing
        for row, cy in enumerate((36, 58, 80)):
            if not rng.chance(0.55):
                continue
            size = 3.4 if rng.chance(0.3) else 2.2
            filled = rng.chance(0.4)
            parts.append(
                f'<rect x="{_fmt(cx - size / 2)}" y="{_fmt(cy - size / 2)}" '
                f'width="{_fmt(size)}" height="{_fmt(size)}" '
                f'fill="{accent if filled else "none"}" stroke="{ink}" '
                f'stroke-width="0.8" opacity="{0.85 if filled else 0.45:.2f}"/>'
            )

    parts.append(
        f'<rect x="0" y="{VIEW_HEIGHT - 2}" width="{VIEW_WIDTH}" height="1" '
        f'fill="{ink}" opacity="0.9"/>'
    )
    return parts


def _vantablack(rng, ink, accent):
    """High-contrast noir: a solid bar cut by hard negative space."""
    parts = []
    bar_top = 30
    bar_height = 58

    parts.append(
        f'<rect x="0" y="{bar_top}" width="{VIEW_WIDTH}" height="{bar_height}" fill="{ink}"/>'
    )

    # Negative-space cuts through the bar.
    cut_x = rng.between(VIEW_WIDTH * 0.35, VIEW_WIDTH * 0.72)
    slant = rng.between(10, 26)
    parts.append(
        f'<polygon points="{_fmt(cut_x)},{bar_top} '
        f'{_fmt(cut_x + slant)},{bar_top} '
        f'{_fmt(cut_x + slant - 14)},{bar_top + bar_height} '
        f'{_fmt(cut_x - 14)},{bar_top + bar_height}" fill="#ffffff"/>'
    )

    thin_x = rng.between(VIEW_WIDTH * 0.08, VIEW_WIDTH * 0.28)
    parts.append(
        f'<rect x="{_fmt(thin_x)}" y="{bar_top}" width="3" height="{bar_height}" '
        'fill="#ffffff"/>'
    )

    # A single detached block, offset below the bar.
    block = rng.between(9, 16)
    parts.append(
        f'<rect x="{_fmt(rng.between(VIEW_WIDTH * 0.74, VIEW_WIDTH * 0.9))}" '
        f'y="{_fmt(bar_top + bar_height + 8)}" width="{_fmt(block)}" '
        f'height="{_fmt(block)}" fill="{ink}"/>'
    )
    return parts


_GENERATORS = {
    "ashveil": _ashveil,
    "systemfall": _systemfall,
    "vantablack": _vantablack,
}


def is_available(name):
    return name in _GENERATORS


def render(name, seed, ink="#000000", accent="#000000", title=""):
    """Return a standalone SVG string for one chapter opener.

    seed drives the generator, so the same chapter always draws the same art.
    Returns "" for an edition that has no art direction (tiers 1 and 2).
    """
    generator = _GENERATORS.get(name)
    if generator is None:
        return ""

    shapes = generator(_Rng(seed), ink, accent)
    safe_title = (
        str(title).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    label = (
        f"<title>Chapter opener art for {safe_title}</title>"
        if safe_title
        else "<title>Chapter opener art</title>"
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" '
        f'width="100%" height="{VIEW_HEIGHT}" role="img" '
        f'preserveAspectRatio="xMidYMax meet">'
        f"{label}"
        + "".join(shapes)
        + "</svg>"
    )
