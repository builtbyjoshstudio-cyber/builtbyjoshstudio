#!/usr/bin/env python3
"""
editions.py — the three tiers and the three signature framed editions.

    Tier 1  clean        House typography, plain headings. No borders or ornaments.
    Tier 2  styled       House design with drop caps, chapter rules, and warm accent.
    Tier 3  illustrated  Signature framed editions with colored page borders,
                         ornamental chapter frames, and distinct display typography:

        ashveil     warm bronze double-rule frame & classic serif
        systemfall  slate-blue geometric frame & monospace headers
        vantablack  high-contrast architectural frame & grotesk headers

Any tier or edition can also have its border style ('none', 'single', 'double',
'rules') and border/accent colour ('#hex') customised via front matter or the
desktop app.
"""
import copy

CLEAN = "clean"
STYLED = "styled"
ILLUSTRATED = "illustrated"

TIERS = (CLEAN, STYLED, ILLUSTRATED)

ASHVEIL = "ashveil"
SYSTEMFALL = "systemfall"
VANTABLACK = "vantablack"

EDITIONS = (ASHVEIL, SYSTEMFALL, VANTABLACK)

BORDER_STYLES = ("double", "single", "rules", "none")

BORDER_STYLE_LABELS = {
    "double": "Double Frame",
    "single": "Single Frame",
    "rules": "Header & Footer Rules",
    "none": "No Border",
}

TIER_LABELS = {
    CLEAN: "Tier 1 - Clean",
    STYLED: "Tier 2 - Styled",
    ILLUSTRATED: "Tier 3 - Framed Edition",
}

EDITION_LABELS = {
    ASHVEIL: "Ashveil - warm bronze double frame",
    SYSTEMFALL: "Systemfall - slate geometric frame",
    VANTABLACK: "Vantablack - high-contrast noir frame",
}

# Curated bookish border/accent color palette for the studio UI.
COLOR_PRESETS = (
    ("Crimson", "#8B261D"),
    ("Bronze", "#8A4B26"),
    ("Navy", "#1E3A5F"),
    ("Forest", "#24523B"),
    ("Burgundy", "#5B2333"),
    ("Gold", "#9A7428"),
    ("Slate", "#2F6F8F"),
    ("Obsidian", "#191817"),
)

# Serif stacks chosen for wide availability on Windows and macOS alike.
_CLASSIC_SERIF = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif'
_TRANSITIONAL_SERIF = 'Georgia, "Times New Roman", Times, serif'
_GEOMETRIC_SANS = '"Futura", "Century Gothic", "Avenir Next", "Segoe UI", sans-serif'
_MONO = '"JetBrains Mono", "Cascadia Mono", Consolas, ui-monospace, monospace'
_GROTESK = '"Helvetica Neue", Helvetica, Arial, sans-serif'


class Edition:
    """One resolved look: tier plus typography, border style, and accent colour."""

    def __init__(self, tier, key, label, body_font, display_font, ink, paper,
                 accent, drop_cap=False, chapter_rule=False, art=None,
                 scene_break="* * *", display_transform="uppercase",
                 display_tracking="0.08em", display_weight="normal",
                 chapter_number=False, border_style="none"):
        self.tier = tier
        self.key = key
        self.label = label
        self.body_font = body_font
        self.display_font = display_font
        self.ink = ink
        self.paper = paper
        self.accent = accent
        self.drop_cap = drop_cap
        self.chapter_rule = chapter_rule
        self.art = art
        self.scene_break = scene_break
        self.display_transform = display_transform
        self.display_tracking = display_tracking
        self.display_weight = display_weight
        self.chapter_number = chapter_number
        self.border_style = border_style

    @property
    def is_illustrated(self):
        return self.tier == ILLUSTRATED

    def __repr__(self):
        return f"<Edition {self.tier}/{self.key}>"


_CLEAN = Edition(
    tier=CLEAN,
    key=CLEAN,
    label=TIER_LABELS[CLEAN],
    body_font=_TRANSITIONAL_SERIF,
    display_font=_TRANSITIONAL_SERIF,
    ink="#1c1c1e",
    paper="#ffffff",
    accent="#1c1c1e",
    drop_cap=False,
    chapter_rule=False,
    art=None,
    border_style="none",
)

_STYLED = Edition(
    tier=STYLED,
    key=STYLED,
    label=TIER_LABELS[STYLED],
    body_font=_CLASSIC_SERIF,
    display_font=_CLASSIC_SERIF,
    ink="#191817",
    paper="#ffffff",
    accent="#6b5b4a",
    drop_cap=True,
    chapter_rule=True,
    chapter_number=True,
    art=None,
    scene_break="❧",
    border_style="rules",
)

_ASHVEIL = Edition(
    tier=ILLUSTRATED,
    key=ASHVEIL,
    label=EDITION_LABELS[ASHVEIL],
    body_font=_CLASSIC_SERIF,
    display_font=_CLASSIC_SERIF,
    ink="#17150f",
    paper="#ffffff",
    accent="#8a4b26",
    drop_cap=True,
    chapter_rule=True,
    chapter_number=True,
    art=ASHVEIL,
    scene_break="◆",
    display_tracking="0.14em",
    border_style="double",
)

_SYSTEMFALL = Edition(
    tier=ILLUSTRATED,
    key=SYSTEMFALL,
    label=EDITION_LABELS[SYSTEMFALL],
    body_font=_TRANSITIONAL_SERIF,
    display_font=_MONO,
    ink="#12161b",
    paper="#ffffff",
    accent="#2f6f8f",
    drop_cap=True,
    chapter_rule=True,
    chapter_number=True,
    art=SYSTEMFALL,
    scene_break="· · ·",
    display_transform="uppercase",
    display_tracking="0.22em",
    border_style="single",
)

_VANTABLACK = Edition(
    tier=ILLUSTRATED,
    key=VANTABLACK,
    label=EDITION_LABELS[VANTABLACK],
    body_font=_TRANSITIONAL_SERIF,
    display_font=_GROTESK,
    ink="#000000",
    paper="#ffffff",
    accent="#000000",
    drop_cap=True,
    chapter_rule=True,
    chapter_number=True,
    art=VANTABLACK,
    scene_break="▬",
    display_transform="uppercase",
    display_tracking="0.02em",
    display_weight="800",
    border_style="double",
)

_BY_EDITION = {
    ASHVEIL: _ASHVEIL,
    SYSTEMFALL: _SYSTEMFALL,
    VANTABLACK: _VANTABLACK,
}


class EditionError(Exception):
    """Raised when a tier or edition name is not recognised."""


def resolve(tier=None, edition=None, border_color=None, border_style=None):
    """Resolve front matter into an Edition. Defaults to tier 1."""
    tier = (str(tier).strip().lower() if tier else CLEAN)
    edition_key = str(edition).strip().lower() if edition else None

    if tier not in TIERS:
        raise EditionError(
            f"unknown tier {tier!r} - choose one of: {', '.join(TIERS)}"
        )

    if tier != ILLUSTRATED:
        base = _CLEAN if tier == CLEAN else _STYLED
    else:
        if not edition_key:
            raise EditionError(
                "tier 'illustrated' needs an edition - choose one of: "
                + ", ".join(EDITIONS)
            )
        if edition_key not in _BY_EDITION:
            raise EditionError(
                f"unknown edition {edition_key!r} - choose one of: {', '.join(EDITIONS)}"
            )
        base = _BY_EDITION[edition_key]

    if not border_color and not border_style:
        return base

    custom = copy.copy(base)
    if border_color and str(border_color).strip():
        custom.accent = str(border_color).strip()
    if border_style and str(border_style).strip().lower() in BORDER_STYLES:
        custom.border_style = str(border_style).strip().lower()
        if custom.border_style != "none":
            custom.chapter_rule = True
    return custom


def from_meta(meta, tier_override=None, edition_override=None):
    """Resolve from front matter, with explicit overrides winning."""
    return resolve(
        tier_override or meta.get("tier"),
        edition_override or meta.get("edition"),
        border_color=meta.get("border_color"),
        border_style=meta.get("border_style"),
    )
