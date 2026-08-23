#!/usr/bin/env python3
"""
editions.py — the three tiers and the three illustrated editions.

    Tier 1  clean        House typography, plain headings. No choices.
    Tier 2  styled       House design with drop caps and chapter treatments.
                         One fixed look, done well.
    Tier 3  illustrated  Buyer picks an edition, which sets both the
                         typography package and the art direction:

        ashveil     charcoal epic
        systemfall  clean geometric, system-flavoured
        vantablack  stark high-contrast noir

A tier is a data object, not a branch in the renderers. Each one declares its
fonts, colours, chapter-opener treatment and ornaments; every renderer reads
the same object, so a tier looks like itself across the web page, the ebook
and the printed interior.

Fonts are stacks, never embedded files — no licences travel with the output.
"""

CLEAN = "clean"
STYLED = "styled"
ILLUSTRATED = "illustrated"

TIERS = (CLEAN, STYLED, ILLUSTRATED)

ASHVEIL = "ashveil"
SYSTEMFALL = "systemfall"
VANTABLACK = "vantablack"

EDITIONS = (ASHVEIL, SYSTEMFALL, VANTABLACK)

TIER_LABELS = {
    CLEAN: "Tier 1 - Clean",
    STYLED: "Tier 2 - Styled",
    ILLUSTRATED: "Tier 3 - Illustrated",
}

EDITION_LABELS = {
    ASHVEIL: "Ashveil - charcoal epic",
    SYSTEMFALL: "Systemfall - geometric, system-flavoured",
    VANTABLACK: "Vantablack - high-contrast noir",
}

# Serif stacks chosen for wide availability on Windows and macOS alike.
_CLASSIC_SERIF = '"Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif'
_TRANSITIONAL_SERIF = 'Georgia, "Times New Roman", Times, serif'
_GEOMETRIC_SANS = '"Futura", "Century Gothic", "Avenir Next", "Segoe UI", sans-serif'
_MONO = '"JetBrains Mono", "Cascadia Mono", Consolas, ui-monospace, monospace'
_GROTESK = '"Helvetica Neue", Helvetica, Arial, sans-serif'


class Edition:
    """One resolved look: tier plus, for tier 3, the buyer's chosen edition."""

    def __init__(self, tier, key, label, body_font, display_font, ink, paper,
                 accent, drop_cap=False, chapter_rule=False, art=None,
                 scene_break="* * *", display_transform="uppercase",
                 display_tracking="0.08em", display_weight="normal",
                 chapter_number=False):
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
    chapter_rule=False,
    chapter_number=True,
    art=ASHVEIL,
    scene_break="◆",
    display_tracking="0.14em",
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
    chapter_rule=False,
    chapter_number=True,
    art=VANTABLACK,
    scene_break="▬",
    display_transform="uppercase",
    display_tracking="0.02em",
    display_weight="800",
)

_BY_EDITION = {
    ASHVEIL: _ASHVEIL,
    SYSTEMFALL: _SYSTEMFALL,
    VANTABLACK: _VANTABLACK,
}


class EditionError(Exception):
    """Raised when a tier or edition name is not recognised."""


def resolve(tier=None, edition=None):
    """Resolve front matter into an Edition. Defaults to tier 1."""
    tier = (str(tier).strip().lower() if tier else CLEAN)
    edition_key = str(edition).strip().lower() if edition else None

    if tier not in TIERS:
        raise EditionError(
            f"unknown tier {tier!r} - choose one of: {', '.join(TIERS)}"
        )

    if tier != ILLUSTRATED:
        return _CLEAN if tier == CLEAN else _STYLED

    if not edition_key:
        raise EditionError(
            "tier 'illustrated' needs an edition - choose one of: "
            + ", ".join(EDITIONS)
        )

    if edition_key not in _BY_EDITION:
        raise EditionError(
            f"unknown edition {edition_key!r} - choose one of: {', '.join(EDITIONS)}"
        )

    return _BY_EDITION[edition_key]


def from_meta(meta, tier_override=None, edition_override=None):
    """Resolve from front matter, with explicit overrides winning."""
    return resolve(
        tier_override or meta.get("tier"),
        edition_override or meta.get("edition"),
    )
