"""Generate collections/<sign>-zodiac-art.html per Brief Message 2.

Brief target: rewrite each Western Signs per-sign page to reflect the
actual product (144 files, 14 styles, 24 designs, $24.99 bundle, POD
licensing). Adds Product/FAQPage/BreadcrumbList schemas, License+POD
trust block, sister-sign nav, accurate style copy.

Usage:
    python tools/build_western_signs_page.py [SIGN ...]   # defaults to Aries only

Message 2 ships Aries only. Message 5 will run this for the other 11.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'images' / 'zodiac' / 'western-signs-manifest.json'
OUT_DIR = ROOT / 'collections'

# ── per-sign metadata ──────────────────────────────────────────────────
SIGN_META = {
    'Aries': dict(
        slug='aries', symbol='♈', element='Fire', modality='Cardinal',
        planet='Mars', symbol_label='The Ram',
        dates='March 21 – April 19', dates_short='Mar 21 – Apr 19',
        sister_signs='Leo, Sagittarius',
        sku='BBJ-WS-ARIES',
        etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio?section_id=58115934',
    ),
    'Taurus':       dict(slug='taurus',      symbol='♉', element='Earth', modality='Fixed',    planet='Venus',   symbol_label='The Bull',         dates='April 20 – May 20',        dates_short='Apr 20 – May 20', sister_signs='Virgo, Capricorn',     sku='BBJ-WS-TAURUS',      etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Gemini':       dict(slug='gemini',      symbol='♊', element='Air',   modality='Mutable',  planet='Mercury', symbol_label='The Twins',        dates='May 21 – June 20',         dates_short='May 21 – Jun 20', sister_signs='Libra, Aquarius',      sku='BBJ-WS-GEMINI',      etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Cancer':       dict(slug='cancer',      symbol='♋', element='Water', modality='Cardinal', planet='Moon',    symbol_label='The Crab',         dates='June 21 – July 22',        dates_short='Jun 21 – Jul 22', sister_signs='Scorpio, Pisces',      sku='BBJ-WS-CANCER',      etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Leo':          dict(slug='leo',         symbol='♌', element='Fire',  modality='Fixed',    planet='Sun',     symbol_label='The Lion',         dates='July 23 – August 22',      dates_short='Jul 23 – Aug 22', sister_signs='Aries, Sagittarius',   sku='BBJ-WS-LEO',         etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Virgo':        dict(slug='virgo',       symbol='♍', element='Earth', modality='Mutable',  planet='Mercury', symbol_label='The Maiden',       dates='August 23 – September 22', dates_short='Aug 23 – Sep 22', sister_signs='Taurus, Capricorn',    sku='BBJ-WS-VIRGO',       etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Libra':        dict(slug='libra',       symbol='♎', element='Air',   modality='Cardinal', planet='Venus',   symbol_label='The Scales',       dates='September 23 – October 22',dates_short='Sep 23 – Oct 22', sister_signs='Gemini, Aquarius',     sku='BBJ-WS-LIBRA',       etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Scorpio':      dict(slug='scorpio',     symbol='♏', element='Water', modality='Fixed',    planet='Pluto',   symbol_label='The Scorpion',     dates='October 23 – November 21', dates_short='Oct 23 – Nov 21', sister_signs='Cancer, Pisces',       sku='BBJ-WS-SCORPIO',     etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Sagittarius':  dict(slug='sagittarius', symbol='♐', element='Fire',  modality='Mutable',  planet='Jupiter', symbol_label='The Archer',       dates='November 22 – December 21',dates_short='Nov 22 – Dec 21', sister_signs='Aries, Leo',           sku='BBJ-WS-SAGITTARIUS', etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Capricorn':    dict(slug='capricorn',   symbol='♑', element='Earth', modality='Cardinal', planet='Saturn',  symbol_label='The Goat',         dates='December 22 – January 19', dates_short='Dec 22 – Jan 19', sister_signs='Taurus, Virgo',        sku='BBJ-WS-CAPRICORN',   etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Aquarius':     dict(slug='aquarius',    symbol='♒', element='Air',   modality='Fixed',    planet='Uranus',  symbol_label='The Water Bearer', dates='January 20 – February 18', dates_short='Jan 20 – Feb 18', sister_signs='Gemini, Libra',        sku='BBJ-WS-AQUARIUS',    etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
    'Pisces':       dict(slug='pisces',      symbol='♓', element='Water', modality='Mutable',  planet='Neptune', symbol_label='The Fish',         dates='February 19 – March 20',   dates_short='Feb 19 – Mar 20', sister_signs='Cancer, Scorpio',      sku='BBJ-WS-PISCES',       etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
}

ALL_SIGNS_ORDER = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# ── per-sign style copy ────────────────────────────────────────────────
# Brief Message 2 provides Aries copy. Other signs ship in Message 5 with
# adapted prose. For now we use a sign-substituted variant of the Aries
# copy as a fallback. Display-style ordering = alphabetical-by-folder-name
# (already what the live page renders).
STYLE_ORDER = [
    ('anime', 'Anime'),
    ('celestial-animals', 'Celestial Animals'),
    ('halloween', 'Halloween'),
    ('halloween-horrors', 'Halloween Horrors'),
    ('hyper-realistic-signs', 'Hyper Realistic'),
    ('mythic-guardians', 'Mythic Guardians'),
    ('punk', 'Punk'),
    ('punk-oil', 'Punk Oil'),
    ('silhouette-aspects', 'Silhouette Aspects'),
    ('silhouettes', 'Silhouettes'),
    ('silhouettes-fantasy', 'Silhouettes Fantasy'),
    ('vintage-posters', 'Vintage Posters'),
    ('watercolor-1', 'Watercolor 1'),
    ('watercolor-2', 'Watercolor 2'),
]

# Aries-specific style copy from Brief 1.7 (verbatim, lightly adapted for HTML)
ARIES_STYLE_COPY = {
    'anime':                'Stylized, dynamic, Japanese-illustration-inspired. The Aries archetype rendered with motion lines, color saturation, and cinematic framing. Reads more like a key visual from an animated series than a horoscope graphic.',
    'celestial-animals':    'Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the ram positioned as a celestial archetype rather than a literal animal. The signature atmospheric look of the studio.',
    'halloween':            'Seasonal but not costume-y. Aries energy filtered through pumpkin-light, autumn palettes, and gothic-festival atmosphere. Designed to work year-round on a wall, not just in October.',
    'halloween-horrors':    'The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Aries rendered with menace — crimson, obsidian, and visual references to classic horror iconography.',
    'hyper-realistic-signs':'Photoreal portraiture with cinematic lighting and material detail. Skin texture, armor, weight. Designed for buyers who want gallery-quality realism rather than symbolic stylization.',
    'mythic-guardians':     'Hyper-realistic warrior portraiture — horned warlords, inferno generals, cinematic mythological figures. The signature hero-pose look of the catalog, rendered with crimson and obsidian palettes.',
    'punk':                 'Bold, graphic, attitude-forward. Aries reimagined with punk-rock visual language — sharp angles, defiant compositions, high-contrast color. Loud on purpose.',
    'punk-oil':             'The Punk style brushed through oil-painting texture. Painterly weight applied to the rebellious energy — more layered, slightly more vintage in feel, still loud.',
    'silhouette-aspects':   'Pure form against atmospheric backdrop. The ram and Aries iconography stripped to silhouette, with mood carried by the sky and palette behind it.',
    'silhouettes':          'Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.',
    'silhouettes-fantasy':  'Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.',
    'vintage-posters':      'Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — nostalgic warmth with unmistakable Aries intensity.',
    'watercolor-1':         "Soft painterly washes — crimson, gold, and warm earth tones. Fluid movement, organic edges, gentler but no less Aries. The studio's classic watercolor approach.",
    'watercolor-2':         'A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.',
}

# Per-sign style copy. Each sub-dict has 14 entries keyed by the same folder
# slugs as STYLE_ORDER. Brief 5A.3 §3 — 2-3 sentences each, describing the style
# as applied to that specific sign.
TAURUS_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Taurus rendered with grounded power and slow-burn presence rather than kinetic motion — the bull as anime archetype, drawn with weight and a quieter kind of gravitas.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the bull positioned as a celestial archetype — horned silhouette anchored in geometry rather than literal animal portraiture.",
    'halloween':            "Seasonal but not costume-y. Taurus energy filtered through pumpkin-light, autumn palettes, and harvest-festival atmosphere. The bull recast as the heaviest presence at the gathering, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. The bull as something ancient and unmoved — earth tones bleeding into obsidian, with the weight of something that has seen this all before.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Skin texture, horn weight, the mass of muscle. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — horned warriors in earth-toned armor, bovine iconography, cinematic mythological figures. The signature hero-pose look of the catalog, rendered in bronze and forest palettes rather than crimson.",
    'punk':                 "Bold, graphic, attitude-forward. Taurus reimagined with punk-rock visual language — heavy lines, immovable poses, defiant stillness. Loud on purpose, but never frantic.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to the bull's natural gravitas — more layered, slightly more vintage in feel, still planted.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The bull and Taurus iconography stripped to silhouette, with mood carried by sky and palette — golden hours, harvest light, low horizons.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of design that suits the Taurus appreciation for things built to last.",
    'watercolor-1':         "Soft painterly washes — earth tones, gold, and Venusian rose. Fluid movement, organic edges, gentler but no less anchored. The studio's classic watercolor approach applied to Taurus's slow weight.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

GEMINI_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. The Gemini twins rendered with anime motion — synchronized poses, mirrored expressions, the kinetic feel of two minds moving in step.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the twins positioned as a celestial archetype — paired figures bound by geometry rather than narrative.",
    'halloween':            "Seasonal but not costume-y. Gemini energy filtered through pumpkin-light, autumn palettes, and the playful mischief that suits the sign. Two-faced rather than two-headed — designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Gemini doubled into something off — twins where one of them isn't quite right.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Two faces, identical bone structure, subtly different expressions. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — paired warriors, twin armor sets, cinematic mythological figures. The signature hero-pose look of the catalog applied to a sign that comes pre-doubled.",
    'punk':                 "Bold, graphic, attitude-forward. Gemini reimagined with punk-rock visual language — split compositions, defiant duality, high-contrast color. Loud on purpose, in stereo.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to the mirrored attitude — more layered, slightly more vintage in feel, still loud, still doubled.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The twin profiles stripped to silhouette, with mood carried by sky and palette behind them — paired figures against open air.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. The twins reduced to two graphic shapes, designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians, with the doubling intact.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera from a Gemini's commonplace book — clever, conversational, double-sided.",
    'watercolor-1':         "Soft painterly washes — Mercurial blues, soft yellows, and air-sign clarity. Fluid movement, organic edges, gentler but no less Gemini. The studio's classic watercolor approach.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with the Watercolor 1 series the same way the twins pair with each other.",
}

CANCER_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Cancer rendered with anime sensitivity — expressive eyes, soft palettes, the tidal pull of feeling carried in posture rather than action.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the crab positioned as a celestial archetype — armored geometry against a moonlit ground.",
    'halloween':            "Seasonal but not costume-y. Cancer energy filtered through pumpkin-light, autumn palettes, and harvest-tide atmosphere. The crab tucked into shadow, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Cancer rendered with deep-sea menace — pale silver against abyssal black, with the quiet of things that watch from below.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Carapace, claw, the wet sheen of shell. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — armored guardians with crustacean motifs, lunar palettes, cinematic mythological figures. The signature hero-pose look of the catalog rendered in pearl and midnight.",
    'punk':                 "Bold, graphic, attitude-forward. Cancer reimagined with punk-rock visual language — sharp angles around soft centers, the contradiction the sign already lives. Loud on purpose, defensive by design.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign that already protects itself — more layered, slightly more vintage in feel, still guarded.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The crab and Cancer iconography stripped to silhouette, with mood carried by tidal palettes — moon-rise, lunar wash, deep water behind.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians, with the moon always somewhere in frame.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — nostalgic warmth that suits the Cancer love of held memory.",
    'watercolor-1':         "Soft painterly washes — pearl, silver, deep teal. Fluid movement, organic edges, gentler but no less Cancer. The studio's classic watercolor approach applied to a sign that already feels like water.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

LEO_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Leo rendered with anime swagger — manes drawn like flame, regal stillness alternating with cinematic motion. Reads like a key visual from an animated series.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the lion positioned as a celestial archetype — solar geometry around a regal silhouette.",
    'halloween':            "Seasonal but not costume-y. Leo energy filtered through pumpkin-light, autumn palettes, and harvest-court atmosphere. The lion at the head of the table, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Leo rendered with infernal authority — molten gold against obsidian, the lion as something older and hungrier than ceremony.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Mane texture, gold-flecked eyes, the weight of muscle in repose. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — golden-armored sovereigns, sun-king regalia, cinematic mythological figures. The signature hero-pose look of the catalog, rendered in solar gold and battle-worn bronze.",
    'punk':                 "Bold, graphic, attitude-forward. Leo reimagined with punk-rock visual language — sharp angles, defiant compositions, high-contrast color. Loud on purpose, never apologetic about it.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to the regal swagger — more layered, slightly more vintage in feel, still loud.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The lion and Leo iconography stripped to silhouette, with mood carried by sky and palette — sunrise, late gold, the colors of a kingdom at its peak.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of golden-age design that suits a sign built for the spotlight.",
    'watercolor-1':         "Soft painterly washes — gold, amber, warm earth tones. Fluid movement, organic edges, gentler but no less Leo. The studio's classic watercolor approach applied to solar weight.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

VIRGO_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Virgo rendered with anime restraint — careful linework, deliberate composition, expressions that hold the room rather than command it.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the maiden positioned as a celestial archetype — botanical geometry, careful symmetry, nothing wasted.",
    'halloween':            "Seasonal but not costume-y. Virgo energy filtered through pumpkin-light, autumn palettes, and the precise quiet of late harvest. The maiden in her own deliberate atmosphere, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Virgo rendered with antiseptic dread — sterile white against deep wound red, the horror that comes from things being too clean.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Skin texture, fabric weave, the precise architecture of a face. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — armored maidens, sacred wards, cinematic mythological figures. The signature hero-pose look of the catalog rendered with the precision the sign demands.",
    'punk':                 "Bold, graphic, attitude-forward. Virgo reimagined with punk-rock visual language — sharp angles, controlled compositions, defiance that still respects the layout. Loud on purpose, intentional about every choice.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign that values craft — more layered, slightly more vintage in feel, still composed.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The maiden and Virgo iconography stripped to silhouette, with mood carried by sky and palette — late harvest light, botanical greens, careful tonal work.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. The kind of minimalism a Virgo would design themselves.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of carefully-typeset design that suits the sign's love of craft.",
    'watercolor-1':         "Soft painterly washes — sage, parchment, late-summer earth tones. Fluid movement, organic edges, gentler but no less Virgo. The studio's classic watercolor approach applied to a sign that lives in detail.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

LIBRA_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Libra rendered with anime grace — symmetrical compositions, elegant lines, the kind of beauty that announces itself without raising its voice.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the scales positioned as a celestial archetype — perfectly balanced geometry against the cosmos.",
    'halloween':            "Seasonal but not costume-y. Libra energy filtered through pumpkin-light, autumn palettes, and the careful elegance of harvest-court ceremony. The scales held by candlelight, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Libra rendered with the horror of judgment — beautiful figures, terrible verdicts.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. The exact weight of brass, the precise tilt of a beam, the architecture of a balanced face. Designed for buyers who want gallery-quality realism.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — robed arbiters, ceremonial armor, cinematic mythological figures. The signature hero-pose look of the catalog applied to a sign that judges with composure.",
    'punk':                 "Bold, graphic, attitude-forward. Libra reimagined with punk-rock visual language — sharp angles, balanced asymmetry, defiance that still respects composition. Loud on purpose, never disordered.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign built around aesthetic — more layered, slightly more vintage in feel, still balanced.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The scales and Libra iconography stripped to silhouette, with mood carried by symmetry and palette — sunset gradients, balanced horizons.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of considered design that suits a sign devoted to aesthetic balance.",
    'watercolor-1':         "Soft painterly washes — rose, gold, twilight blue. Fluid movement, organic edges, gentler but no less Libra. The studio's classic watercolor approach applied to a sign that lives in harmony.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

SCORPIO_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Scorpio rendered with anime intensity — narrowed eyes, deep palettes, the kinetic feel of something about to strike. Reads like a key visual from a darker animated series.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the scorpion positioned as a celestial archetype — venom-tipped geometry against the deepest cosmic black.",
    'halloween':            "Seasonal but not costume-y. Scorpio energy filtered through pumpkin-light, autumn palettes, and the season the sign was born to own. The scorpion at the height of its hour, designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Scorpio rendered without restraint — blood-deep crimson, obsidian sting, the horror this sign carries by default.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Chitin texture, venom gleam, the exact weight of a curved tail. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — black-armored assassins, venomous guardians, cinematic mythological figures. The signature hero-pose look of the catalog rendered in obsidian and blood.",
    'punk':                 "Bold, graphic, attitude-forward. Scorpio reimagined with punk-rock visual language — sharp angles, defiant compositions, high-contrast color. Loud on purpose, intentionally menacing.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign already built around intensity — more layered, slightly more vintage in feel, still dangerous.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The scorpion and Scorpio iconography stripped to silhouette, with mood carried by sky and palette — blood moons, deep dusk, the colors of something hunting.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera from a darker era — the kind of design that suits a sign comfortable in shadow.",
    'watercolor-1':         "Soft painterly washes — crimson, deep purple, ink black. Fluid movement, organic edges, gentler but no less Scorpio. The studio's classic watercolor approach applied to a sign that bleeds.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

SAGITTARIUS_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Sagittarius rendered with anime momentum — drawn bow, mid-stride compositions, the cinematic feel of a hero already moving toward the next chapter.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the centaur archer positioned as a celestial archetype — drawn-arrow geometry against open sky.",
    'halloween':            "Seasonal but not costume-y. Sagittarius energy filtered through pumpkin-light, autumn palettes, and the late-fall restlessness that suits a fire sign at the edge of winter. Designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. The archer rendered as wild hunt — antlered, primal, dangerous in the way only freedom can be.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Sinew, drawn bowstring, the focus of an aim already locked. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — centaur archers, kinetic warriors mid-draw, cinematic mythological figures. The signature hero-pose look of the catalog rendered in flame-gold and forge-bronze.",
    'punk':                 "Bold, graphic, attitude-forward. Sagittarius reimagined with punk-rock visual language — kinetic compositions, defiant motion, high-contrast color. Loud on purpose, restless on principle.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign that never stops moving — more layered, slightly more vintage in feel, still aimed forward.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The archer and Sagittarius iconography stripped to silhouette, with mood carried by sky and palette — sunset wandering, open horizon, the colors of arrival just over the next ridge.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera from a traveler's wall — the kind of design that suits a sign always on its way somewhere.",
    'watercolor-1':         "Soft painterly washes — flame gold, dust red, late-autumn earth tones. Fluid movement, organic edges, gentler but no less Sagittarius. The studio's classic watercolor approach.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

CAPRICORN_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Capricorn rendered with anime gravitas — stoic poses, ancient palettes, the slow burn of a sign that's already calculated the next ten moves.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the sea-goat positioned as a celestial archetype — stone-carved geometry against deep starlit black.",
    'halloween':            "Seasonal but not costume-y. Capricorn energy filtered through pumpkin-light, autumn palettes, and the cold-edged threshold of late fall. Designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Capricorn rendered as something old — horned, stone-still, watching from the frozen peak.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Horn texture, mountain wind in fur, the weight of an immovable creature. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — armored sentinels, ancient guardians, cinematic mythological figures. The signature hero-pose look of the catalog rendered in slate, iron, and weathered bronze.",
    'punk':                 "Bold, graphic, attitude-forward. Capricorn reimagined with punk-rock visual language — sharp angles, immovable poses, defiance that doesn't move because it doesn't have to. Loud on purpose, never unstable.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign that already feels ancient — more layered, slightly more vintage in feel, still solid.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The sea-goat and Capricorn iconography stripped to silhouette, with mood carried by sky and palette — mountain dusk, deep cold blues, the colors of an arduous climb.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of design that suits a sign that respects what was built to last.",
    'watercolor-1':         "Soft painterly washes — slate, granite gray, deep evergreen. Fluid movement, organic edges, gentler but no less Capricorn. The studio's classic watercolor approach applied to enduring weight.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

AQUARIUS_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Aquarius rendered with anime futurism — cool palettes, asymmetric compositions, the cinematic feel of something only just arriving from further ahead.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the water bearer positioned as a celestial archetype — radial geometry pouring outward, the figure as transmission rather than person.",
    'halloween':            "Seasonal but not costume-y. Aquarius energy filtered through pumpkin-light, autumn palettes, and a cool-detached take on the season. Designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Aquarius rendered as something that arrives unexpectedly — angular, otherworldly, electric in the worst way.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. The exact pour of water against glass, the gleam of an unfamiliar metal, the architecture of an idea made literal. Designed for buyers who want gallery-quality realism.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — robed seers, electric prophets, cinematic mythological figures. The signature hero-pose look of the catalog rendered in arc-blue and station-white.",
    'punk':                 "Bold, graphic, attitude-forward. Aquarius reimagined with punk-rock visual language — angular figures, anti-establishment compositions, high-contrast color. Loud on purpose, future-facing on principle.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign that already invents new conventions — more layered, slightly more vintage in feel, still ahead of itself.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The water bearer and Aquarius iconography stripped to silhouette, with mood carried by sky and palette — predawn blue, station-light, the colors of something not from here.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — but specifically the kind a futurist would have collected, retro in service of looking forward.",
    'watercolor-1':         "Soft painterly washes — silver, ice blue, arc violet. Fluid movement, organic edges, gentler but no less Aquarius. The studio's classic watercolor approach applied to a sign made of frequencies.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

PISCES_STYLE_COPY = {
    'anime':                "Stylized, Japanese-illustration-inspired. Pisces rendered with anime softness — expressive eyes, flowing palettes, the cinematic feel of a character carrying entire interior worlds invisibly.",
    'celestial-animals':    "Cosmic-symbolic and sacred-geometric. Gold linework, deep cosmic backgrounds, and the paired fish positioned as a celestial archetype — circular geometry, two figures in eternal opposite motion.",
    'halloween':            "Seasonal but not costume-y. Pisces energy filtered through pumpkin-light, autumn palettes, and the misty in-between atmosphere the sign already lives in. Designed to work year-round on a wall.",
    'halloween-horrors':    "The darker companion to the Halloween series. Macabre, shadow-drenched, and unapologetically horror-leaning. Pisces rendered with deep-sea dread — pale shapes against black water, the horror of things glimpsed but never fully seen.",
    'hyper-realistic-signs':"Photoreal portraiture with cinematic lighting and material detail. Scale shimmer, water refraction, the exact weight of light underwater. Designed for buyers who want gallery-quality realism rather than symbolic stylization.",
    'mythic-guardians':     "Hyper-realistic warrior portraiture — pearl-armored guardians, coral-crowned figures, cinematic mythological warriors. The signature hero-pose look of the catalog rendered in oceanic palettes.",
    'punk':                 "Bold, graphic, attitude-forward. Pisces reimagined with punk-rock visual language — fluid compositions, soft defiance, high-contrast color. Loud on purpose, but in the way water can be loud — relentless rather than aggressive.",
    'punk-oil':             "The Punk style brushed through oil-painting texture. Painterly weight applied to a sign already comfortable with formlessness — more layered, slightly more vintage in feel, still moving.",
    'silhouette-aspects':   "Pure form against atmospheric backdrop. The two fish and Pisces iconography stripped to silhouette, with mood carried by sky and palette — predawn fog, deep water, the colors of the in-between hour.",
    'silhouettes':          "Stark high-contrast silhouettes — bolder edges, simpler compositions, gallery-wall ready. Designed to anchor a multi-sign or multi-style wall arrangement.",
    'silhouettes-fantasy':  "Silhouettes pushed into fantasy territory — magical elements, ethereal backdrops, mythic atmosphere. The bridge between the graphic silhouettes and the cinematic Mythic Guardians.",
    'vintage-posters':      "Classic printed-poster aesthetic. Bold typography, textured paper feel, mid-century color palettes. Reads like framed ephemera — the kind of dreamlike design that suits a sign that lives partly elsewhere.",
    'watercolor-1':         "Soft painterly washes — sea-foam, deep indigo, iridescent pearl. Fluid movement, organic edges, gentler but no less Pisces. The studio's classic watercolor approach applied to a sign that already is watercolor.",
    'watercolor-2':         "A second watercolor interpretation with different palette and brushwork emphasis — more saturated, slightly more graphic, designed to pair with or stand against the Watercolor 1 series.",
}

STYLE_COPY_BY_SIGN = {
    'Aries':       ARIES_STYLE_COPY,
    'Taurus':      TAURUS_STYLE_COPY,
    'Gemini':      GEMINI_STYLE_COPY,
    'Cancer':      CANCER_STYLE_COPY,
    'Leo':         LEO_STYLE_COPY,
    'Virgo':       VIRGO_STYLE_COPY,
    'Libra':       LIBRA_STYLE_COPY,
    'Scorpio':     SCORPIO_STYLE_COPY,
    'Sagittarius': SAGITTARIUS_STYLE_COPY,
    'Capricorn':   CAPRICORN_STYLE_COPY,
    'Aquarius':    AQUARIUS_STYLE_COPY,
    'Pisces':      PISCES_STYLE_COPY,
}


def style_copy_for(sign):
    return STYLE_COPY_BY_SIGN.get(sign, {})


# ── HTML builders ──────────────────────────────────────────────────────

def build_style_block(slug, display_name, designs, sign, copy_text):
    cards = []
    for d in designs:
        cards.append(
            '            <div class="style-card">\n'
            f'              <img src="../{d["webp_path"]}" alt="{display_name} variant {d["variant"]} — {sign} Zodiac Art Print" loading="lazy" width="720" height="900">\n'
            '              <div class="style-card-body">\n'
            f'                <h4 style="font-family:\'Cinzel\',serif;font-size:.85rem;font-weight:600;color:var(--bbj-muted);letter-spacing:.08em;text-transform:uppercase;margin:0">Variant {d["variant"]}</h4>\n'
            '              </div>\n'
            '            </div>'
        )
    desc_html = f'        <p class="style-block-desc">{copy_text}</p>\n' if copy_text else ''
    return (
        '        <div class="style-block">\n'
        f'          <h3 class="style-block-title">{display_name}</h3>\n'
        + desc_html
        + '          <div class="styles-grid">\n\n' + '\n\n'.join(cards) + '\n\n'
        '          </div>\n'
        '        </div>'
    )


def build_sister_nav(current_sign):
    cards = []
    for s in ALL_SIGNS_ORDER:
        m = SIGN_META[s]
        is_current = (s == current_sign)
        active_class = ' sister-card-current' if is_current else ''
        href = f'{m["slug"]}-zodiac-art.html'
        if is_current:
            inner = f'<div class="sister-card{active_class}"><span class="sister-glyph">{m["symbol"]}</span><span class="sister-name">{s}</span><span class="sister-meta">{m["element"]} · {m["dates_short"]}</span><span class="sister-here">You are here</span></div>'
        else:
            inner = f'<a href="{href}" class="sister-card{active_class}"><span class="sister-glyph">{m["symbol"]}</span><span class="sister-name">{s}</span><span class="sister-meta">{m["element"]} · {m["dates_short"]}</span></a>'
        cards.append(f'        {inner}')
    return '\n'.join(cards)


def build_faq_html(sign, styles_csv):
    faqs = faq_data(sign, styles_csv)
    items = []
    for q, a in faqs:
        items.append(
            '      <div class="faq-item">\n'
            f'        <h3>{q}</h3>\n'
            f'        <p>{a}</p>\n'
            '      </div>'
        )
    return '\n'.join(items)


def faq_data(sign, styles_csv):
    """Returns [(question, answer), ...] in display order. Schema and visible HTML
    must stay aligned — both built from this single source."""
    return [
        (f'What is included in the {sign} Zodiac Art Bundle?',
         f'The {sign} bundle includes 144 print-ready digital files covering 24 original {sign} designs across 14 art-style series — {styles_csv}. Every design ships in three aspect ratios (1:1, 4:5, 2:3) and both PNG and JPG formats, at 300 DPI. The bundle also includes a License Agreement and a Print Guide as PDFs.'),
        (f'How much does the {sign} Zodiac Art Bundle cost?',
         f'The {sign} bundle is priced at $24.99 — one-time payment, instant digital download. That works out to roughly $1.04 per individual design.'),
        (f'Can I use the {sign} Zodiac Art Bundle for print-on-demand or commercial sales?',
         'Yes. The license includes print-on-demand rights for up to 100 physical units per individual design, cumulative across all formats, vendors, and time periods combined. You can sell framed prints, posters, canvases, mugs, t-shirts, and similar physical products made from the designs within that cap. For more than 100 prints of any single design, contact Built by Josh Studio LLC about extended commercial licensing.'),
        (f'What sizes can I print the {sign} art at?',
         'The largest file (6000 × 9000 pixels) prints crisply up to 20" × 30" at full 300 DPI. With a print provider running 150 DPI for large-format jobs, prints up to roughly 40" × 60" still look excellent. The bundle also includes 1:1 files (4800 × 4800) for square framing and 4:5 files (4800 × 6000) for standard portrait sizes like 8×10 and 16×20.'),
        (f'How were the {sign} designs created?',
         f"The {sign} designs were created by Built by Josh Studio LLC using a combination of human creative direction and AI image generation tools, including Leonardo.ai. Every design is selected, curated, refined, and finalized by the studio's founder. This is disclosed in full in the license agreement included with every bundle."),
        ('What formats and color profiles do the files use?',
         'All files are delivered in both PNG (lossless) and JPG (92% quality compression) formats. Color profile is sRGB — the standard for virtually every print-on-demand service and consumer printer, requiring no color conversion before printing.'),
        (f'Where can I buy the {sign} Zodiac Art Bundle?',
         f'The {sign} bundle is sold directly on builtbyjoshstudio.com via secure Lemon Squeezy checkout. Click the "Buy the {sign} Bundle" button on this page to open the checkout overlay, complete the purchase, and receive instant access to the full bundle — no Etsy account required, no marketplace fees, files delivered immediately to your email. The Built By Josh Studio Etsy storefront carries other studio work but does not sell the full Collection bundles.'),
        ('Do you have art for other zodiac signs and the Chinese zodiac?',
         'Yes. Built By Josh Studio publishes 12 sign-specific bundles for all Western zodiac signs (Aries through Pisces, identical structure to the Aries bundle), 12 sign-specific bundles in the Western Realms landscape series, a full 12-landscape Western Landscapes Collection, 12 animal-specific Chinese Signs bundles, and a single Chinese Realms Collection covering all 12 Chinese animals.'),
    ]


def faq_schema_data(sign, styles_csv):
    """Schema variants: same Q/A but with inch-marks and curly quotes replaced
    for safe JSON. Q7 in particular has double-quoted button label which gets
    flattened to a quote-free form."""
    data = faq_data(sign, styles_csv)
    out = []
    for q, a in data:
        a_schema = (
            a
            .replace('20" × 30"', '20 by 30 inches')
            .replace('40" × 60"', '40 by 60 inches')
            .replace('8×10', '8x10')
            .replace('16×20', '16x20')
            .replace('×', 'x')
            .replace(f'"Buy the {sign} Bundle"', f'Buy the {sign} Bundle')
        )
        out.append({'q': q, 'a': a_schema})
    return out


def build_page(sign, manifest):
    m = SIGN_META[sign]
    slug = m['slug']
    sign_data = manifest[sign]
    styles_csv = ', '.join(name for _, name in STYLE_ORDER)

    # Build per-style HTML blocks
    copy_dict = style_copy_for(sign)
    style_blocks = []
    for folder_slug, display_name in STYLE_ORDER:
        # Find this style in the manifest
        style_entry = next((s for s in sign_data['styles'] if s['slug'] == folder_slug), None)
        if not style_entry:
            continue
        copy_text = copy_dict.get(folder_slug, '')
        style_blocks.append(build_style_block(folder_slug, display_name, style_entry['designs'], sign, copy_text))
    style_blocks_html = '\n\n'.join(style_blocks)

    # FAQ visible + schema
    faqs_visible = build_faq_html(sign, styles_csv)
    faqs_schema = faq_schema_data(sign, styles_csv)
    faqs_schema_json = ',\n'.join(
        '    {{\n'
        '      "@type": "Question",\n'
        f'      "name": {json.dumps(f["q"])},\n'
        '      "acceptedAnswer": {{\n'
        '        "@type": "Answer",\n'
        f'        "text": {json.dumps(f["a"])}\n'
        '      }}\n'
        '    }}'.replace('{{','{').replace('}}','}')
        for f in faqs_schema
    )

    sister_nav = build_sister_nav(sign)

    ls_disabled_attr, ls_url, ls_btn_text = ls_button_state(sign)

    return f'''<!DOCTYPE html>
<html lang="en" data-glass="cosmic">
<head>
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-QDSPBB7S9J"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-QDSPBB7S9J');
    </script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{sign} Zodiac Art Bundle — 144 Print-Ready Files | 14 Art Styles | BBJ Studio</title>
  <meta name="description" content="The {sign} zodiac art bundle from Built By Josh Studio — 144 print-ready digital files across 14 art styles and 24 original designs. Personal use + print-on-demand licensed up to 100 prints per design. Instant download." />
  <link rel="canonical" href="https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html" />

  <!-- Open Graph -->
  <meta property="og:title" content="{sign} Zodiac Art Bundle — 144 Print-Ready Files | 14 Art Styles | BBJ Studio" />
  <meta property="og:description" content="The {sign} zodiac art bundle from Built By Josh Studio — 144 print-ready digital files across 14 art styles and 24 original designs. Personal use + print-on-demand licensed up to 100 prints per design. Instant download." />
  <meta property="og:type" content="product" />
  <meta property="og:url" content="https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html" />
  <meta property="og:site_name" content="Built By Josh Studio" />
  <meta property="og:image" content="https://builtbyjoshstudio.com/images/zodiac/{slug}.webp" />

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{sign} Zodiac Art Bundle — 144 Print-Ready Files | 14 Art Styles | BBJ Studio" />
  <meta name="twitter:description" content="The {sign} zodiac art bundle from Built By Josh Studio — 144 print-ready digital files across 14 art styles and 24 original designs. Personal use + print-on-demand licensed up to 100 prints per design. Instant download." />
  <meta name="twitter:image" content="https://builtbyjoshstudio.com/images/zodiac/{slug}.webp" />

  <!-- Schema.org: BreadcrumbList (Brief 2.3 option b) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://builtbyjoshstudio.com/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Collections", "item": "https://builtbyjoshstudio.com/collections/" }},
      {{ "@type": "ListItem", "position": 3, "name": "{sign} Zodiac Art Bundle", "item": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html" }}
    ]
  }}
  </script>

  <!-- Schema.org: Product (Brief 2.1; aggregateRating omitted per brief recommendation) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html#product",
    "name": "{sign} Zodiac Art Bundle — 144 Print-Ready Files",
    "description": "The {sign} Zodiac Art Bundle contains 144 print-ready digital files covering 24 original {sign} designs across 14 art-style series — {styles_csv}. Every design ships in three aspect ratios (1:1, 4:5, 2:3) at 300 DPI in both PNG and JPG. Licensed for personal use and print-on-demand up to 100 prints per design.",
    "image": [
      "https://builtbyjoshstudio.com/images/zodiac/{slug}.webp"
    ],
    "url": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html",
    "sku": "{m['sku']}",
    "category": "Digital Art / Zodiac Art / Western Signs",
    "brand": {{
      "@type": "Brand",
      "name": "Built By Josh Studio"
    }},
    "manufacturer": {{
      "@id": "https://builtbyjoshstudio.com/#organization"
    }},
    "additionalProperty": [
      {{"@type": "PropertyValue", "name": "File Count", "value": "144"}},
      {{"@type": "PropertyValue", "name": "Designs", "value": "24"}},
      {{"@type": "PropertyValue", "name": "Art Styles", "value": "14"}},
      {{"@type": "PropertyValue", "name": "Resolution", "value": "300 DPI"}},
      {{"@type": "PropertyValue", "name": "Maximum Dimensions", "value": "6000 x 9000 pixels"}},
      {{"@type": "PropertyValue", "name": "Aspect Ratios", "value": "1:1, 4:5, 2:3"}},
      {{"@type": "PropertyValue", "name": "File Formats", "value": "PNG, JPG"}},
      {{"@type": "PropertyValue", "name": "Color Profile", "value": "sRGB"}},
      {{"@type": "PropertyValue", "name": "License", "value": "Personal use + POD up to 100 prints per design"}},
      {{"@type": "PropertyValue", "name": "Zodiac Sign", "value": "{sign}"}},
      {{"@type": "PropertyValue", "name": "Element", "value": "{m['element']}"}},
      {{"@type": "PropertyValue", "name": "Date Range", "value": "{m['dates']}"}}
    ],
    "offers": {{
      "@type": "Offer",
      "price": "24.99",
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock",
      "url": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-art.html",
      "seller": {{
        "@id": "https://builtbyjoshstudio.com/#organization"
      }},
      "itemCondition": "https://schema.org/NewCondition"
    }}
  }}
  </script>

  <!-- Schema.org: FAQPage (Brief 2.2; mirrors visible FAQ) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faqs_schema_json}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bbj-bg: #0b0813;
      --bbj-surface: #120f1f;
      --bbj-surface-2: #171327;
      --bbj-accent: #c9a84c;
      --bbj-accent2: #7b4fa6;
      --bbj-text: #ede8f5;
      --bbj-muted: #8a7fa8;
      --bbj-border: #2a2040;
      --body-read: #d6cee8;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'DM Sans', sans-serif; background: var(--bbj-bg); color: var(--bbj-text); overflow-x: hidden; min-height: 100vh; }}
    .stars {{ position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }}
    .star {{ position: absolute; width: 2px; height: 2px; background: #fff; border-radius: 50%; opacity: 0; animation: twinkle var(--d) ease-in-out infinite var(--delay); }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: 0; transform: scale(0.5); }} 50% {{ opacity: var(--op); transform: scale(1); }} }}
    .site-nav {{ position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; padding: 0 2.5rem; height: 64px; background: rgba(11,8,19,0.92); backdrop-filter: blur(12px); border-bottom: 1px solid var(--bbj-border); }}
    .nav-logo {{ font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.1rem; letter-spacing: -0.02em; color: var(--bbj-text); text-decoration: none; }}
    .nav-links {{ display: flex; gap: 2rem; list-style: none; }}
    .nav-links a {{ font-family: 'DM Sans', sans-serif; font-size: 0.85rem; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; text-decoration: none; color: var(--bbj-muted); transition: color 0.2s; }}
    .nav-links a:hover, .nav-links a.active {{ color: var(--bbj-accent); }}
    .collection-hero {{ padding: 9rem 2rem 3rem; max-width: 1200px; margin: 0 auto; text-align: center; position: relative; }}
    .collection-hero::before {{ content: ''; position: absolute; inset: 0; pointer-events: none;
      background: radial-gradient(ellipse at 50% 0%, rgba(201,168,76,0.1) 0%, transparent 55%),
                  radial-gradient(ellipse at 20% 80%, rgba(123,79,166,0.08) 0%, transparent 50%); }}
    .breadcrumb {{ font-family: 'Cinzel', serif; font-size: 0.68rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-muted); margin-bottom: 1.4rem; position: relative; }}
    .breadcrumb a {{ color: var(--bbj-accent); text-decoration: none; }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    .breadcrumb .sep {{ margin: 0 0.6rem; opacity: 0.5; }}
    .hero-eyebrow {{ font-family: 'Cinzel', serif; font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--bbj-accent); margin-bottom: 1.2rem; position: relative; }}
    h1.collection-title {{ font-family: 'Cinzel', serif; font-size: clamp(2.2rem, 5.5vw, 3.8rem); font-weight: 700; letter-spacing: 0.02em; line-height: 1.12; color: var(--bbj-text); margin-bottom: 1.4rem; max-width: 900px; margin-left: auto; margin-right: auto; position: relative; }}
    .collection-tagline {{ font-family: 'Crimson Pro', serif; font-size: clamp(1.05rem, 1.5vw, 1.18rem); color: var(--body-read); max-width: 760px; margin: 0 auto 2.5rem; line-height: 1.65; position: relative; }}
    .hero-image {{ max-width: 420px; margin: 0 auto; position: relative; border: 1px solid var(--bbj-border); overflow: hidden; aspect-ratio: 4/5; }}
    .hero-image img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .hero-image::after {{ content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 50% 50%, rgba(201,168,76,0.08) 0%, transparent 70%); pointer-events: none; }}

    /* The Short Version block (GEO-citable summary) */
    .short-version {{ max-width: 1000px; margin: 3rem auto 0; padding: 2rem 2.4rem; background: var(--bbj-surface); border: 1px solid var(--bbj-border); border-left: 4px solid var(--bbj-accent); position: relative; }}
    .short-version-label {{ font-family: 'Cinzel', serif; font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--bbj-accent); margin-bottom: 0.9rem; }}
    .short-version p {{ font-family: 'Crimson Pro', serif; font-size: 1.05rem; line-height: 1.75; color: var(--body-read); margin: 0; }}

    /* Main grid */
    .collection-main {{ max-width: 1200px; margin: 2rem auto 0; padding: 2rem 2rem 4rem; display: grid; grid-template-columns: 1fr 340px; gap: 3rem; align-items: start; }}
    .main-column {{ font-family: 'Crimson Pro', serif; font-size: 1.15rem; line-height: 1.75; color: var(--body-read); min-width: 0; }}
    .main-column section {{ margin-bottom: 3rem; padding-top: 2.5rem; border-top: 1px solid var(--bbj-border); }}
    .main-column section:first-child {{ border-top: none; padding-top: 0; }}
    .main-column h2 {{ font-family: 'Cinzel', serif; font-size: clamp(1.4rem, 2.6vw, 1.85rem); font-weight: 700; letter-spacing: 0.02em; color: var(--bbj-text); margin-bottom: 1.3rem; line-height: 1.2; }}
    .main-column p {{ margin-bottom: 1.3rem; }}
    .main-column p strong {{ color: var(--bbj-text); font-weight: 600; }}
    .main-column ul {{ list-style: none; margin: 0 0 1.5rem 0; padding: 0; }}
    .main-column ul li {{ position: relative; padding-left: 1.6rem; margin-bottom: 0.8rem; }}
    .main-column ul li::before {{ content: '◆'; position: absolute; left: 0; color: var(--bbj-accent); font-size: 0.7rem; top: 0.5rem; }}

    /* Quick facts data block */
    .quick-facts {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 1.3rem 1.7rem; margin: 0 0 2rem 0 !important; }}
    .quick-facts li {{ padding-left: 0 !important; margin-bottom: 0.5rem !important; font-family: 'DM Sans', sans-serif; font-size: 0.95rem; color: var(--body-read); }}
    .quick-facts li::before {{ content: '' !important; }}
    .quick-facts li strong {{ font-family: 'Cinzel', serif; font-size: 0.78rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--bbj-accent); display: inline-block; min-width: 145px; }}

    /* 14-style grouped layout */
    .styles-grouped {{ display: flex; flex-direction: column; gap: 2.5rem; margin-top: 1.5rem; }}
    .style-block {{ display: flex; flex-direction: column; gap: 0.8rem; }}
    .style-block-title {{ font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 700; color: var(--bbj-text); letter-spacing: 0.04em; text-transform: uppercase; padding-bottom: 0.6rem; border-bottom: 1px solid var(--bbj-border); margin: 0; }}
    .style-block-desc {{ font-family: 'Crimson Pro', serif; font-size: 1rem; line-height: 1.65; color: var(--body-read); margin: 0 0 0.5rem 0 !important; padding-left: 0 !important; }}
    .style-block-desc::before {{ content: '' !important; }}
    .styles-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }}
    .style-card {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 0; overflow: hidden; display: flex; flex-direction: column; transition: border-color 0.25s, background 0.25s; }}
    .style-card:hover {{ border-color: rgba(201,168,76,0.35); background: var(--bbj-surface-2); }}
    .style-card img {{ width: 100%; height: auto; aspect-ratio: 4/5; object-fit: cover; display: block; background: linear-gradient(135deg, #1a1230 0%, #0d0a1a 100%); border-bottom: 1px solid var(--bbj-border); }}
    .style-card-body {{ padding: 0.9rem 1.1rem 1rem; }}

    /* Lemon Squeezy checkout button (sidebar + final CTA) */
    .ls-checkout-btn {{ display: block; width: 100%; background: var(--bbj-accent); color: var(--bbj-bg); border: none; font-family: 'Cinzel', serif; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 1.05rem 1rem; text-align: center; cursor: pointer; transition: background 0.2s, transform 0.2s; margin-bottom: 0.7rem; }}
    .ls-checkout-btn:hover:not(:disabled) {{ background: #e0bd5a; transform: translateY(-1px); }}
    .ls-checkout-btn:disabled {{ background: transparent; color: var(--bbj-muted); border: 1px solid var(--bbj-border); cursor: default; font-weight: 600; letter-spacing: 0.12em; font-size: 0.74rem; }}
    .ls-checkout-btn--large {{ display: inline-block; width: auto; padding: 1.15rem 2.5rem; font-size: 0.82rem; margin: 0; }}
    .ls-checkout-btn--large:disabled {{ font-size: 0.78rem; padding: 1.1rem 2.2rem; }}
    .ls-checkout-sub {{ display: block; font-size: 0.74rem; font-style: italic; color: var(--bbj-muted); text-align: center; margin-bottom: 1.4rem; line-height: 1.45; }}

    /* Secondary Etsy reference block (muted, courtesy link only — not a competing sales path) */
    .etsy-secondary {{ margin-top: 1.4rem; padding-top: 1.2rem; border-top: 1px solid rgba(42,32,64,0.5); }}
    .etsy-secondary .etsy-secondary-label {{ font-family: 'Cinzel', serif; font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-muted); margin-bottom: 0.5rem; }}
    .etsy-secondary p {{ font-family: 'DM Sans', sans-serif; font-size: 0.78rem; color: var(--bbj-muted); line-height: 1.5; margin-bottom: 0.5rem; }}
    .etsy-secondary a {{ color: var(--bbj-muted); text-decoration: underline; text-decoration-color: rgba(138,127,168,0.4); }}
    .etsy-secondary a:hover {{ color: var(--bbj-accent); text-decoration-color: var(--bbj-accent); }}
    .etsy-secondary .etsy-pause-note {{ font-style: italic; font-size: 0.72rem; opacity: 0.75; margin-top: 0.4rem; margin-bottom: 0; }}

    /* License & POD block */
    .license-block {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 2rem 2.2rem; margin-top: 2rem; }}
    .license-block h3 {{ font-family: 'Cinzel', serif; font-size: 1.02rem; font-weight: 700; color: var(--bbj-text); letter-spacing: 0.05em; text-transform: uppercase; margin: 1.6rem 0 0.8rem 0; padding-bottom: 0.4rem; border-bottom: 1px solid var(--bbj-border); }}
    .license-block h3:first-child {{ margin-top: 0; }}
    .license-block ul {{ margin-bottom: 1.4rem !important; }}
    .license-block p.disclosure {{ background: rgba(123,79,166,0.07); border-left: 3px solid var(--bbj-accent2); padding: 1rem 1.2rem; margin-bottom: 1.4rem; font-size: 1rem; line-height: 1.65; }}
    .license-block p.contact-line {{ margin-bottom: 1.5rem; font-size: 1rem; color: var(--body-read); }}
    .license-block a.pdf-link {{ display: inline-block; font-family: 'Cinzel', serif; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--bbj-accent); text-decoration: none; padding: 0.6rem 1.1rem; border: 1px solid var(--bbj-accent); margin: 0.4rem 0.4rem 0 0; transition: background 0.2s, color 0.2s; }}
    .license-block a.pdf-link:hover {{ background: var(--bbj-accent); color: var(--bbj-bg); }}

    /* Sticky sidebar */
    .sticky-sidebar {{ position: sticky; top: 88px; background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 1.8rem 1.7rem; font-family: 'DM Sans', sans-serif; }}
    .sticky-sidebar::before {{ content: ''; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(135deg, rgba(201,168,76,0.05) 0%, transparent 60%); }}
    .sticky-sidebar > * {{ position: relative; }}
    .sidebar-label {{ font-family: 'Cinzel', serif; font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-muted); margin-bottom: 0.4rem; }}
    .sidebar-price {{ font-family: 'Cinzel', serif; font-size: 2.4rem; font-weight: 700; color: var(--bbj-accent); letter-spacing: -0.02em; line-height: 1; margin-bottom: 0.4rem; }}
    .sidebar-price-note {{ font-size: 0.78rem; color: var(--bbj-muted); letter-spacing: 0.02em; margin-bottom: 1.4rem; padding-bottom: 1.4rem; border-bottom: 1px solid var(--bbj-border); }}
    .sidebar-included-label {{ font-family: 'Cinzel', serif; font-size: 0.62rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-muted); margin-bottom: 0.8rem; }}
    .sidebar-included {{ list-style: none; padding: 0; margin: 0 0 1.5rem 0; }}
    .sidebar-included li {{ font-size: 0.84rem; color: var(--body-read); padding: 0.42rem 0 0.42rem 1.3rem; position: relative; line-height: 1.35; border-bottom: 1px solid rgba(42,32,64,0.5); }}
    .sidebar-included li:last-child {{ border-bottom: none; }}
    .sidebar-included li::before {{ content: '✓'; position: absolute; left: 0; color: var(--bbj-accent); font-weight: 700; font-size: 0.85rem; }}
    .sidebar-cta {{ display: block; background: var(--bbj-accent); color: var(--bbj-bg); font-family: 'Cinzel', serif; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 1.05rem 1rem; text-align: center; text-decoration: none; transition: background 0.2s, transform 0.2s; margin-bottom: 0.7rem; }}
    .sidebar-cta:hover {{ background: #e0bd5a; transform: translateY(-1px); }}
    .sidebar-cta-sub {{ display: block; font-size: 0.74rem; font-style: italic; color: var(--bbj-muted); text-align: center; margin-bottom: 1.4rem; line-height: 1.4; }}
    .sidebar-trust {{ list-style: none; padding: 0; margin: 0; }}
    .sidebar-trust li {{ font-size: 0.74rem; color: var(--bbj-muted); padding: 0.35rem 0 0.35rem 1.2rem; position: relative; line-height: 1.35; }}
    .sidebar-trust li::before {{ content: '✦'; position: absolute; left: 0; color: var(--bbj-accent); font-size: 0.72rem; top: 0.38rem; }}

    /* FAQ */
    .faq-section {{ max-width: 900px; margin: 0 auto; padding: 5rem 2rem 4rem; }}
    .section-label {{ font-family: 'Cinzel', serif; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-accent); text-align: center; margin-bottom: 0.6rem; }}
    .section-title-main {{ font-family: 'Cinzel', serif; font-size: clamp(1.8rem, 3.2vw, 2.4rem); font-weight: 700; letter-spacing: 0.02em; color: var(--bbj-text); text-align: center; margin-bottom: 2.8rem; }}
    .faq-list {{ display: flex; flex-direction: column; gap: 0; border-top: 1px solid var(--bbj-border); }}
    .faq-item {{ border-bottom: 1px solid var(--bbj-border); padding: 1.6rem 0; }}
    .faq-item h3 {{ font-family: 'Cinzel', serif; font-size: 1.05rem; font-weight: 600; color: var(--bbj-text); margin-bottom: 0.7rem; letter-spacing: 0.01em; }}
    .faq-item p {{ font-family: 'Crimson Pro', serif; font-size: 1.05rem; line-height: 1.65; color: var(--body-read); margin: 0; }}

    /* Sister-sign nav grid */
    .sister-nav-section {{ max-width: 1200px; margin: 0 auto; padding: 3rem 2rem 2rem; }}
    .sister-intro {{ font-family: 'Crimson Pro', serif; font-style: italic; font-size: 1.05rem; color: var(--body-read); text-align: center; max-width: 720px; margin: 0 auto 2rem; }}
    .sister-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; }}
    .sister-card {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 1rem 1rem 1rem; text-decoration: none; color: inherit; transition: transform 0.2s, border-color 0.2s, background 0.2s; display: flex; flex-direction: column; align-items: center; gap: 0.35rem; position: relative; }}
    .sister-card:hover {{ transform: translateY(-2px); border-color: rgba(201,168,76,0.4); background: var(--bbj-surface-2); }}
    .sister-card-current {{ border-color: var(--bbj-accent); background: rgba(201,168,76,0.05); cursor: default; }}
    .sister-card-current:hover {{ transform: none; }}
    .sister-glyph {{ font-size: 1.5rem; color: var(--bbj-accent); line-height: 1; }}
    .sister-name {{ font-family: 'Cinzel', serif; font-size: 0.92rem; font-weight: 700; letter-spacing: 0.03em; color: var(--bbj-text); }}
    .sister-meta {{ font-family: 'DM Sans', sans-serif; font-size: 0.7rem; color: var(--bbj-muted); letter-spacing: 0.04em; text-align: center; }}
    .sister-here {{ font-family: 'Cinzel', serif; font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-accent); margin-top: 0.3rem; }}

    /* Reviews */
    .reviews-section {{ max-width: 900px; margin: 0 auto; padding: 3rem 2rem 0; }}
    .reviews-header {{ display: flex; align-items: baseline; gap: 1rem; margin-bottom: 1.8rem; }}
    .reviews-header .star-display {{ font-family: 'Cinzel', serif; font-size: 1.2rem; color: var(--bbj-accent); font-weight: 700; }}
    .reviews-header .review-note {{ font-family: 'Crimson Pro', serif; font-size: 0.95rem; font-style: italic; color: var(--bbj-muted); }}
    .reviews-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }}
    .review-card {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 1.4rem; position: relative; }}
    .review-card .review-stars {{ font-size: 0.9rem; color: var(--bbj-accent); margin-bottom: 0.5rem; }}
    .review-card .review-text {{ font-family: 'Crimson Pro', serif; font-size: 1rem; font-style: italic; color: var(--body-read); line-height: 1.55; margin-bottom: 0.7rem; }}
    .review-card .review-author {{ font-family: 'DM Sans', sans-serif; font-size: 0.78rem; color: var(--bbj-muted); }}

    /* Related Collections */
    .related-section {{ max-width: 1200px; margin: 0 auto; padding: 3rem 2rem 5rem; }}
    .related-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.4rem; }}
    .related-card {{ background: var(--bbj-surface); border: 1px solid var(--bbj-border); padding: 1.6rem 1.6rem 1.4rem; text-decoration: none; color: inherit; transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s; display: flex; flex-direction: column; position: relative; overflow: hidden; }}
    .related-card::after {{ content: ''; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(135deg, rgba(201,168,76,0.04) 0%, transparent 60%); }}
    .related-card:hover {{ transform: translateY(-3px); border-color: rgba(201,168,76,0.35); box-shadow: 0 14px 40px rgba(201,168,76,0.08); }}
    .related-card > * {{ position: relative; z-index: 1; }}
    .related-meta {{ font-family: 'Cinzel', serif; font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase; color: var(--bbj-accent); margin-bottom: 0.7rem; }}
    .related-card h3 {{ font-family: 'Cinzel', serif; font-size: 1.1rem; font-weight: 700; color: var(--bbj-text); margin-bottom: 0.6rem; letter-spacing: 0.01em; line-height: 1.25; }}
    .related-card p {{ font-family: 'Crimson Pro', serif; font-size: 0.95rem; font-style: italic; color: var(--bbj-muted); line-height: 1.5; margin-bottom: 1rem; flex: 1; }}
    .related-link {{ font-family: 'Cinzel', serif; font-size: 0.66rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--bbj-accent); }}

    /* Final CTA band */
    .cta-band {{ padding: 5rem 2rem; text-align: center; background: linear-gradient(135deg, #1a1230 0%, #0d0a1a 100%); border-top: 1px solid var(--bbj-border); border-bottom: 1px solid var(--bbj-border); position: relative; }}
    .cta-band .cta-eyebrow {{ font-family: 'Cinzel', serif; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--bbj-accent); margin-bottom: 1rem; }}
    .cta-band h2 {{ font-family: 'Cinzel', serif; font-size: clamp(1.7rem, 3.2vw, 2.4rem); font-weight: 700; color: var(--bbj-text); margin-bottom: 0.8rem; letter-spacing: 0.02em; max-width: 720px; margin-left: auto; margin-right: auto; line-height: 1.2; }}
    .cta-band h2 .italic-accent {{ color: var(--bbj-accent); font-style: italic; font-family: 'Crimson Pro', serif; font-weight: 400; }}
    .cta-band .cta-sub {{ font-family: 'Crimson Pro', serif; color: var(--body-read); font-size: 1.05rem; max-width: 620px; margin: 0 auto 2rem; line-height: 1.6; }}
    .cta-band .cta-sub-line {{ display: block; font-family: 'Crimson Pro', serif; font-style: italic; font-size: 0.9rem; color: var(--bbj-muted); margin-top: 1rem; }}

    /* Footer */
    footer {{ background: #0a0a0f; padding: 3rem 5rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1.5rem; }}
    .footer-left {{ font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.3); }}
    .footer-left strong {{ color: rgba(255,255,255,0.7); }}
    .footer-links {{ display: flex; gap: 1.5rem; list-style: none; }}
    .footer-links a {{ font-size: 0.75rem; color: rgba(255,255,255,0.3); text-decoration: none; transition: color 0.2s; letter-spacing: 0.06em; text-transform: uppercase; }}
    .footer-links a:hover {{ color: rgba(255,255,255,0.7); }}
    .footer-legal {{ font-family: 'DM Sans', sans-serif; font-size: 0.7rem; color: rgba(255,255,255,0.3); width: 100%; text-align: center; margin-top: 1rem; line-height: 1.6; }}

    /* Responsive */
    @media (max-width: 1024px) {{
      .collection-main {{ grid-template-columns: 1fr; gap: 2.5rem; }}
      .sticky-sidebar {{ position: static; order: -1; max-width: 500px; margin: 0 auto; width: 100%; }}
      .related-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .reviews-grid {{ grid-template-columns: 1fr; }}
      .sister-grid {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    @media (max-width: 720px) {{
      .collection-hero {{ padding: 7rem 1.5rem 2rem; }}
      .short-version {{ padding: 1.6rem 1.4rem; }}
      .etsy-notice {{ padding: 1.2rem 1.4rem; }}
      .collection-main {{ padding: 1.5rem 1.5rem 3rem; }}
      .main-column {{ font-size: 1.08rem; }}
      .faq-section {{ padding: 4rem 1.5rem 3rem; }}
      .related-section {{ padding: 2rem 1.5rem 4rem; }}
      .related-grid {{ grid-template-columns: 1fr; }}
      .site-nav {{ padding: 0 1.5rem; }}
      .nav-links {{ gap: 1.2rem; }}
      .sister-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .styles-grid {{ grid-template-columns: 1fr; }}
      footer {{ flex-direction: column; padding: 2rem; text-align: center; }}
    }}

    .nav-logo {{ white-space: nowrap; }}
    .nav-logo .logo-short {{ display: none; }}
    @media (max-width: 720px) {{
      .site-nav {{ padding: 0 1rem; }}
      .nav-logo {{ font-size: 0.88rem; }}
      .nav-logo .logo-full {{ display: none; }}
      .nav-logo .logo-short {{ display: inline; }}
      .nav-links {{ gap: 0.9rem; }}
      .nav-links a {{ font-size: 0.72rem; letter-spacing: 0.04em; }}
    }}
    @media (max-width: 420px) {{
      .nav-logo {{ font-size: 0.78rem; }}
      .nav-links {{ gap: 0.55rem; }}
      .nav-links a {{ font-size: 0.62rem; letter-spacing: 0.03em; }}
    }}
  </style>
  <link rel="stylesheet" href="/css/tokens.css" />
  <link rel="stylesheet" href="/css/mobile-nav.css" />

  <!-- Organization schema (site-wide, from Message 1 identity cleanup) -->
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://builtbyjoshstudio.com/#organization",
  "name": "Built by Josh Studio LLC",
  "alternateName": ["BBJ Studio", "Built By Josh Studio"],
  "legalName": "Built by Josh Studio LLC",
  "url": "https://builtbyjoshstudio.com",
  "logo": {{
    "@type": "ImageObject",
    "url": "https://builtbyjoshstudio.com/images/logo/logo.webp",
    "width": 512,
    "height": 512
  }},
  "image": "https://builtbyjoshstudio.com/images/logo/logo.webp",
  "description": "Built by Josh Studio LLC is a Kansas-based independent creative studio that publishes original zodiac digital art under the Built By Josh Studio brand and Notion OS templates and personal finance workbooks under the Tynkr Tools & Co brand. All products are digital, instant-download, and built by a single founder.",
  "founder": {{
    "@type": "Person",
    "name": "Josh"
  }},
  "foundingDate": "2026-05-13",
  "foundingLocation": {{
    "@type": "Place",
    "address": {{
      "@type": "PostalAddress",
      "addressRegion": "KS",
      "addressCountry": "US"
    }}
  }},
  "address": {{
    "@type": "PostalAddress",
    "addressRegion": "KS",
    "addressCountry": "US"
  }},
  "areaServed": "Worldwide",
  "knowsAbout": [
    "Zodiac digital art",
    "Western zodiac",
    "Chinese zodiac",
    "Notion templates",
    "Personal finance spreadsheets",
    "Digital product design",
    "Print-on-demand licensing"
  ],
  "brand": [
    {{
      "@type": "Brand",
      "name": "Built By Josh Studio",
      "description": "Original digital zodiac art bundles — Western signs, Chinese signs, zodiac landscapes, and zodiac realms — sold as print-ready, POD-licensed digital downloads."
    }},
    {{
      "@type": "Brand",
      "name": "Tynkr Tools & Co",
      "description": "Notion OS templates and Excel and Google Sheets workbooks for creators, solopreneurs, and personal-finance milestones."
    }}
  ],
  "contactPoint": {{
    "@type": "ContactPoint",
    "email": "josh@builtbyjoshstudio.com",
    "contactType": "customer support",
    "areaServed": "Worldwide",
    "availableLanguage": "English"
  }},
  "sameAs": [
    "https://linktr.ee/builtbyjoshstudio",
    "https://tynkrtoolsco.substack.com/",
    "https://www.youtube.com/@TalesofInkShadowsStudio",
    "https://tynkrtoolsandco.etsy.com",
    "https://www.etsy.com/shop/BuiltByJoshStudio"
  ],
  "identifier": [
    {{
      "@type": "PropertyValue",
      "propertyID": "Kansas Business ID",
      "value": "10076138"
    }}
  ]
}}
  </script>
</head>
<body>
  <!-- STAR FIELD -->
  <div class="stars" id="starsContainer"></div>

  <!-- NAV -->
  <nav class="site-nav">
    <a href="../index.html" class="nav-logo"><span class="logo-full">Built By Josh Studio</span><span class="logo-short">BBJ Studio</span></a>
    <ul class="nav-links">
      <li><a href="../index.html#tynkr">Templates</a></li>
      <li><a href="../index.html#builtbyjosh" class="active">Zodiac Art</a></li>
      <li><a href="../blog.html">Blog</a></li>
      <li><a href="../resources/">Resources</a></li>
      <li><a href="../index.html#free-tools">Free Tools</a></li>
      <li><a href="../about.html">About</a></li>
    </ul>
    <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false" type="button">
      <span></span><span></span><span></span>
    </button>
  </nav>

  <!-- HERO -->
  <header class="collection-hero">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">Collections</a><span class="sep">/</span><span>{sign}</span>
    </div>
    <div class="hero-eyebrow">{m['symbol']} {sign} · {m['element']} Sign · {m['dates']}</div>
    <h1 class="collection-title">{sign} Zodiac Art Bundle — 144 Print-Ready Files</h1>
    <p class="collection-tagline">{hero_tagline_for(sign)}</p>
    <div class="hero-image">
      <img src="../images/zodiac/{slug}.webp" alt="{sign} zodiac art bundle preview — 14 art styles including celestial animals, mythic guardians, watercolor, Halloween Horrors, and vintage posters, from Built By Josh Studio" />
    </div>
  </header>

  <!-- The Short Version (GEO-citable summary) -->
  <aside class="short-version">
    <div class="short-version-label">The Short Version</div>
    <p>The {sign} Zodiac Art Bundle from Built By Josh Studio is a digital art collection containing 144 print-ready image files. Each bundle covers one Western zodiac sign and includes 24 original designs across 14 art-style series — {styles_csv}. Every design is delivered in three aspect ratios (1:1 square, 4:5 portrait, 2:3 portrait) at 300 DPI, in both PNG and JPG formats, with maximum dimensions of 6000 × 9000 pixels. The bundle is priced at $24.99 and includes a personal-use license plus print-on-demand rights for up to 100 physical prints per design. Files are instant-download — no physical shipping. All bundles are produced by Built by Josh Studio LLC, a Kansas limited liability company (Kansas Business ID 10076138).</p>
  </aside>

  <!-- MAIN LAYOUT -->
  <div class="collection-main">

    <!-- MAIN COLUMN -->
    <main class="main-column">

      <section>
        <h2>{sign} Zodiac Art Bundle — The Full Collection</h2>
        <p>The {sign} Zodiac Art Bundle from Built By Josh Studio is one of 12 sign-specific bundles in the Western Signs Collection. Each {sign} bundle contains 144 print-ready digital files — 24 unique designs rendered across 14 distinct art-style series, with every design delivered in three aspect ratios and both PNG and JPG formats.</p>
        <p>The 14 styles span the full visual range of the catalog. Some are atmospheric and editorial — Celestial Animals, Mythic Guardians, Vintage Posters. Some are stylized — Anime, Punk, Punk Oil. Some are softer — Watercolor 1, Watercolor 2, Silhouettes Fantasy. Some are graphic and high-contrast — Silhouettes, Silhouette Aspects, Hyper Realistic, Halloween, Halloween Horrors. Buyers don't pick one style; the bundle includes all 14.</p>
        <p>Built By Josh Studio is the zodiac art brand of Built by Josh Studio LLC, a Kansas-based independent creative studio. Every bundle is original work — concepted, generated, curated, and finalized by a single founder.</p>
      </section>

      <section>
        <h2>What Makes {sign}, {sign}</h2>
        <ul class="quick-facts">
          <li><strong>Element:</strong> {m['element']}</li>
          <li><strong>Modality:</strong> {m['modality']}</li>
          <li><strong>Ruling Planet:</strong> {m['planet']}</li>
          <li><strong>Symbol:</strong> {m['symbol_label']}</li>
          <li><strong>Dates:</strong> {m['dates']}</li>
          <li><strong>Sister {m['element']} Signs:</strong> {m['sister_signs']}</li>
        </ul>
        <p>{sign} is the {ordinal_of(sign)} sign of the zodiac, spanning {m['dates']}. It is {indef_article_for(m['element'])} {m['element'].lower()} sign ruled by {m['planet']}{planet_symbol_tail(sign)}</p>
        {what_makes_paras(sign)}
      </section>

      <section>
        <h2>The 14 Art Styles in the {sign} Bundle</h2>
        <p>The current page lists 14 distinct art-style series. The bundle includes all of them — every design, every variant, every format.</p>
        <div class="styles-grouped">
{style_blocks_html}
        </div>
      </section>

      <section>
        <h2>Who Buys {sign} Zodiac Art</h2>
        <ul>
          <li>{sign} ({m['dates']}) who want a single bundle covering every art style for their sign, rather than picking one print at a time</li>
          <li>Etsy, Printful, and Redbubble print-on-demand sellers building zodiac shops who need licensed, print-ready files with explicit POD rights</li>
          <li>Anyone shopping for a {sign} birthday gift who wants something more personal and lasting than a candle or mug</li>
          <li>Astrology content creators, bloggers, and course builders who need varied visual material for posts, social, and lesson assets — all within the personal and POD scope of the license</li>
          <li>Interior decorators and gallery-wall buyers stacking multiple signs and styles across a wall</li>
          <li>Anyone drawn to {sign} energy — {m['element'].lower()}, momentum, intensity — regardless of their own sun sign</li>
        </ul>
      </section>

      <section>
        <h2>What's Included With Every {sign} Bundle</h2>
        <p>Every {sign} Zodiac Art Bundle is a complete digital download. After purchase, you get instant access to 144 image files organized into 14 art-style subfolders — no shipping, no waiting, no physical product mailed to you.</p>
        <p>Each design is delivered in three aspect ratios: 1:1 square (4800 × 4800 pixels), 4:5 portrait (4800 × 6000 pixels), and 2:3 portrait (6000 × 9000 pixels). Every size is provided in both PNG (lossless) and JPG (92% quality) formats. All files are saved at 300 DPI in standard sRGB color space — the industry standard for high-quality print reproduction across home printers, professional print shops, and print-on-demand services.</p>
        <p>The bundle also includes two PDF documents: a <strong>License Agreement &amp; Terms of Use</strong> covering personal use, print-on-demand rights, and the 100-print-per-design cap, and a <strong>Print Guide &amp; User Manual</strong> explaining file structure, recommended print sizes, paper selection, and troubleshooting tips. Both are tailored to the Western Signs Collection.</p>
        <p>Pricing is $24.99 for the full bundle. Visit Etsy for current sales and promotions (Etsy shop currently in temporary verification pause — see notice above).</p>
      </section>

      <section>
        <h2>Licensing &amp; Print-on-Demand Rights</h2>
        <div class="license-block">
          <p>The {sign} Zodiac Art Bundle ships with a clear, plain-English license — not a vague "for personal use" disclaimer.</p>
          <h3>You may</h3>
          <ul>
            <li>Print and display the files in your own home or personal space</li>
            <li>Sell physical print-on-demand products (framed prints, posters, canvases, mugs, t-shirts, phone cases, etc.) made from the designs, up to a cumulative cap of 100 physical units per individual design across all formats, vendors, and time periods combined</li>
            <li>Use the prints as personal or commercial gifts within the same 100-print-per-design cap</li>
          </ul>
          <h3>You may not</h3>
          <ul>
            <li>Redistribute, share, sell, or transmit the digital files themselves to anyone, in any format</li>
            <li>Use the files as input, training data, or seed images for any AI model</li>
            <li>Mint or tokenize the files as NFTs or other blockchain assets</li>
            <li>Exceed the 100-print-per-design cap (it does not reset and is cumulative across all channels)</li>
            <li>Claim authorship of the designs or register them as your own intellectual property</li>
          </ul>
          <p class="disclosure"><strong>AI disclosure:</strong> The designs in the bundle were created using a combination of human creative direction and AI image generation tools, including Leonardo.ai, with selection, curation, refinement, and final arrangement by Built by Josh Studio LLC. This is disclosed in full in the license agreement.</p>
          <p class="contact-line"><strong>Need more than 100 prints per design?</strong> Extended commercial licensing is available — contact <a href="mailto:josh@builtbyjoshstudio.com" style="color:var(--bbj-accent);text-decoration:none">josh@builtbyjoshstudio.com</a> before exceeding the cap.</p>
          <a href="/legal/license-western-signs.pdf" class="pdf-link">Read the full Western Signs License (PDF) →</a>
          <a href="/legal/print-guide-western-signs.pdf" class="pdf-link">Read the Western Signs Print Guide (PDF) →</a>
        </div>
      </section>

    </main>

    <!-- STICKY SIDEBAR -->
    <aside class="sticky-sidebar">
      <div class="sidebar-label">Bundle Price</div>
      <div class="sidebar-price">$24.99</div>
      <div class="sidebar-price-note">One-time payment · Instant digital download · Secure Lemon Squeezy checkout</div>

      <div class="sidebar-included-label">What's Included</div>
      <ul class="sidebar-included">
        <li>144 print-ready digital files</li>
        <li>24 original designs in 14 art styles</li>
        <li>Three aspect ratios: 1:1, 4:5, 2:3</li>
        <li>PNG + JPG, both included</li>
        <li>Up to 6000 × 9000 pixels at 300 DPI</li>
        <li>Personal use + POD up to 100 prints per design</li>
        <li>License &amp; Print Guide PDFs included</li>
        <li>Instant download — no shipping</li>
      </ul>

      <button class="ls-checkout-btn"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{sign} Zodiac Art Bundle" data-product-price="24.99">{ls_btn_text}</button>
      <span class="ls-checkout-sub">Instant download · License &amp; Print Guide included · Secure checkout via Lemon Squeezy</span>

      <ul class="sidebar-trust">
        <li>Instant digital download</li>
        <li>300 DPI print-ready files</li>
        <li>Real Kansas LLC + clear POD license</li>
        <li>Secure direct checkout via Lemon Squeezy</li>
      </ul>

      <div class="etsy-secondary">
        <div class="etsy-secondary-label">Looking for something different?</div>
        <p>The Built By Josh Studio Etsy storefront has additional individual prints and other studio work. <a href="https://www.etsy.com/shop/BuiltByJoshStudio" target="_blank" rel="noopener">Visit the Etsy shop →</a></p>
        <p class="etsy-pause-note">Etsy storefront currently on a brief verification pause while the IRS finalizes EIN verification — {sign} bundle purchases above are unaffected.</p>
      </div>
    </aside>

  </div>

  <!-- FAQ -->
  <section class="faq-section">
    <div class="section-label">Frequently Asked</div>
    <h2 class="section-title-main">Frequently Asked Questions</h2>
    <div class="faq-list">
{faqs_visible}
    </div>
  </section>

  <!-- SISTER-SIGN NAV (Brief 1.12) -->
  <section class="sister-nav-section">
    <div class="section-label">Browse All Signs</div>
    <h2 class="section-title-main">Browse All 12 Western Zodiac Sign Bundles</h2>
    <p class="sister-intro">Every Western zodiac sign has its own bundle in the same structure — 144 files, 14 styles, 24 designs, $24.99 per sign. Click any sign below to see its full collection.</p>
    <div class="sister-grid">
{sister_nav}
    </div>
  </section>

  <!-- RELATED COLLECTIONS (Brief 1.13 — internal links only) -->
  <section class="related-section">
    <div class="section-label">Explore the rest of the BBJ Studio zodiac catalog</div>
    <h2 class="section-title-main">Related Collections</h2>
    <div class="related-grid">
      <a href="zodiac-landscapes.html" class="related-card">
        <div class="related-meta">Western Landscapes Collection</div>
        <h3>Zodiac Landscapes</h3>
        <p>One mythic environment per sign — 12 oil-painted landscapes for all the Western signs in a single bundle.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="{slug}-zodiac-realms.html" class="related-card">
        <div class="related-meta">Western Realms · {sign}</div>
        <h3>{sign} Zodiac Realms</h3>
        <p>Four hybrid cosmos-landscape Realm interpretations of {sign} — 8 designs across 4 named realms for the same sign.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="chinese-zodiac-art.html" class="related-card">
        <div class="related-meta">Eastern Zodiac · 12 Animals</div>
        <h3>Chinese Zodiac Signs</h3>
        <p>All 12 Chinese animals in two art styles — hyper-realistic and watercolor. 8 designs per animal, 12 animal bundles.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="chinese-zodiac-realms.html" class="related-card">
        <div class="related-meta">Eastern Zodiac · Lunar Realms</div>
        <h3>Chinese Zodiac Realms</h3>
        <p>Landscape-style art for all 12 Chinese animals — 24 designs in a single bundle.</p>
        <span class="related-link">View Collection →</span>
      </a>
    </div>
  </section>

  <!-- REVIEWS -->
  <section class="reviews-section">
    <div class="section-label">Shop Reviews</div>
    <div class="reviews-header">
      <span class="star-display">★★★★★ 4.7</span>
      <span class="review-note">Reviews from the Built By Josh Studio Etsy shop</span>
    </div>
    <div class="reviews-grid">
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">"Fantastic artwork, I really love it!"</p>
        <div class="review-author">Louise · Leo Zodiac Sign Print</div>
      </div>
      <div class="review-card">
        <div class="review-stars">★★★★★</div>
        <p class="review-text">"Files came through right away and look great."</p>
        <div class="review-author">Etsy buyer · Scorpio Zodiac Watercolor</div>
      </div>
      <div class="review-card">
        <div class="review-stars">★★★★☆</div>
        <p class="review-text">"Downloaded easily and what I wanted."</p>
        <div class="review-author">Mary · Scorpio Zodiac Sign Print</div>
      </div>
    </div>
  </section>

  <!-- FINAL CTA -->
  <section class="cta-band">
    <div class="cta-eyebrow">Browse the Collection</div>
    <h2>14 Styles. 24 Designs. <span class="italic-accent">One {sign} Bundle.</span></h2>
    <p class="cta-sub">Every art-style series in one $24.99 bundle. Print at home, print at a shop, sell on-demand up to 100 prints per design. Instant download, real license, no subscription.</p>
    <button class="ls-checkout-btn ls-checkout-btn--large"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{sign} Zodiac Art Bundle" data-product-price="24.99">{ls_btn_text}</button>
    <span class="cta-sub-line">Instant download — 144 print-ready files in your inbox the moment checkout completes.</span>
  </section>

  <!-- FOOTER -->
  <footer>
    <div class="footer-left"><strong>Built By Josh Studio</strong> · All digital products — instant download</div>
    <ul class="footer-links">
      <li><a href="../index.html">Home</a></li>
      <li><a href="index.html">Collections</a></li>
      <li><a href="../blog.html">Blog</a></li>
      <li><a href="../resources/">Resources</a></li>
      <li><a href="../about.html">About</a></li>
      <li><a href="https://www.etsy.com/shop/BuiltByJoshStudio" target="_blank" rel="noopener">Etsy</a></li>
      <li><a href="../refunds.html">Refunds</a></li>
      <li><a href="../privacy.html">Privacy</a></li>
      <li><a href="../terms.html">Terms</a></li>
    </ul>
    <div class="footer-legal">
      &copy; 2026 Built by Josh Studio LLC. All rights reserved.<br>
      Tynkr Tools &amp; Co is a brand of Built by Josh Studio LLC.
    </div>
  </footer>

  <!-- STAR FIELD JS -->
  <script>
    const container = document.getElementById('starsContainer');
    for (let i = 0; i < 80; i++) {{
      const s = document.createElement('div');
      s.className = 'star';
      s.style.cssText = `left:${{Math.random()*100}}%;top:${{Math.random()*100}}%;--d:${{2+Math.random()*4}}s;--delay:-${{Math.random()*4}}s;--op:${{0.3+Math.random()*0.7}};filter:blur(${{Math.random()>0.8?'1px':'0px'}});width:${{Math.random()>0.8?3:2}}px;height:${{Math.random()>0.8?3:2}}px;`;
      container.appendChild(s);
    }}
  </script>

  <!-- Etsy click-out tracking -->
  <script>
    document.addEventListener('click', function(e) {{
      var link = e.target.closest('a[href*="etsy.com"]');
      if (!link) return;
      var card = link.closest('[data-animal],[data-landscape],[data-realm],[data-sign],[data-product]');
      var section = 'collection-page';
      var productName = link.textContent.trim().length < 120 ? link.textContent.trim() : 'unknown';
      if (typeof gtag === 'function') {{
        gtag('event', 'click_out_to_etsy', {{
          etsy_url: link.href,
          product_name: productName,
          source_page: window.location.pathname,
          source_section: 'western-sign-bundle'
        }});
      }}
    }});
  </script>

  <script src="/js/ls-checkout-btn.js" defer></script>
  <script src="/js/mobile-nav.js" defer></script>
  <script src="/js/ga4-events.js" defer></script>
</body>
</html>
'''


# ── helpers for the small per-sign factoid paragraph in "What Makes X, X" ──
ORDINAL_BY_SIGN = {
    'Aries': 'first', 'Taurus': 'second', 'Gemini': 'third', 'Cancer': 'fourth',
    'Leo': 'fifth', 'Virgo': 'sixth', 'Libra': 'seventh', 'Scorpio': 'eighth',
    'Sagittarius': 'ninth', 'Capricorn': 'tenth', 'Aquarius': 'eleventh', 'Pisces': 'twelfth',
}


def ordinal_of(sign):
    return ORDINAL_BY_SIGN.get(sign, 'first')


# Indefinite article by element — fixes "a earth sign" / "a air sign" bug.
INDEF_ARTICLE_BY_ELEMENT = {'Fire': 'a', 'Earth': 'an', 'Air': 'an', 'Water': 'a'}


def indef_article_for(element):
    return INDEF_ARTICLE_BY_ELEMENT.get(element, 'a')


# Per-sign tail completing the first sentence: " — <planet descriptor>. <sign> is
# represented by <symbol>, <symbol descriptor>."  Lifted from existing live page
# astrological prose where present (Brief 5A.3 §2 — lift if quality copy exists).
PLANET_SYMBOL_TAIL_BY_SIGN = {
    'Aries':       ' — the planet of drive, aggression, and action. Aries is represented by the ram, a symbol of headfirst momentum and refusal to back down.',
    'Taurus':      ' — the planet of beauty, pleasure, and material value. Taurus is represented by the bull, a symbol of endurance, determination, and grounded strength.',
    'Gemini':      ' — the planet of communication, intellect, and adaptability. Gemini is represented by the twins, a symbol of duality, curiosity, and the ability to hold two truths at once.',
    'Cancer':      ' — the celestial body of emotion, memory, and intuition. Cancer is represented by the crab, a symbol of protection, sensitivity, and the instinct to guard what matters most.',
    'Leo':         ' — the only sign in the zodiac governed by a star rather than a planet. Leo is represented by the lion, a symbol of sovereignty, courage, and the kind of presence that doesn\'t need to announce itself.',
    'Virgo':       ' — the planet of intellect, communication, and analysis. Virgo is represented by the maiden, a symbol of purity not in the moral sense but in the sense of precision — the drive to refine, to improve, to get every detail right.',
    'Libra':       ' — the planet of beauty, love, and aesthetic value. Libra is represented by the scales, the only inanimate symbol in the zodiac — a sign defined not by instinct or force but by the pursuit of balance.',
    'Scorpio':     ' — the planet of transformation, death, and rebirth (with Mars as traditional co-ruler). Scorpio is represented by the scorpion, a symbol of intensity, resilience, and the willingness to go where other signs won\'t.',
    'Sagittarius': ' — the planet of expansion, philosophy, and boundless optimism. Sagittarius is represented by the archer, a centaur drawing back a bow, aiming at something just beyond the horizon.',
    'Capricorn':   ' — the planet of structure, discipline, and time. Capricorn is represented by the sea-goat, a mythic creature that climbs mountains and navigates depths — a symbol of ambition that operates in both the visible world and the one beneath the surface.',
    'Aquarius':    ' — the planet of rebellion, innovation, and sudden change (with Saturn as traditional co-ruler). The water bearer pours knowledge and truth, not water — making Aquarius the sign of ideas, not emotions.',
    'Pisces':      ' — the planet of dreams, illusion, and the subconscious (with Jupiter as traditional co-ruler). Pisces is represented by two fish swimming in opposite directions, a symbol of the sign\'s constant pull between the real world and the one they carry inside their head.',
}


def planet_symbol_tail(sign):
    return PLANET_SYMBOL_TAIL_BY_SIGN.get(sign, '.')


# Per-sign paras 2+3 of "What Makes X, X" — para 2 = personality/energy lift from
# existing live page; para 3 rewritten to reference the new 14 styles instead of
# the deprecated style names (Moonlit Lagoon / Frost Demon / cyberpunk edition /
# etc.) that the old pages used.  Brief 5A.3 §2.
WHAT_MAKES_PARAS_BY_SIGN = {
    'Aries':       (
        "<p>People born under Aries are often described as bold, competitive, and direct. They tend to be initiators — the ones who start the project, make the first move, and set the pace. Aries energy is forward motion. It doesn't wait for permission and it doesn't look back.</p>\n"
        "        <p>That energy defines this entire collection. Whether rendered in the gold-line sacred geometry of the Celestial Animals, the molten authority of the Mythic Guardians, or the crimson menace of the Halloween Horrors — every Aries piece is designed to feel like it's moving, even standing still.</p>"
    ),
    'Taurus':      (
        "<p>People born under Taurus are often described as reliable, patient, and deeply sensory. They value quality over quantity, comfort over chaos, and tend to build things meant to last. Taurus energy is slow and deliberate — it doesn't rush, but it doesn't quit either.</p>\n"
        "        <p>That steadiness runs through every piece in this collection. Whether expressed in the rich gold linework of the Celestial Animals, the painterly weight of the Punk Oil and Vintage Posters, or the soft permanence of the watercolor washes — every Taurus print is designed to feel anchored and intentional, the way the sign itself moves through the world.</p>"
    ),
    'Gemini':      (
        "<p>People born under Gemini are often described as quick-witted, versatile, and endlessly curious. They move between ideas, conversations, and interests with a fluidity that other signs can't match. Gemini energy is mental speed — the sign that's already three thoughts ahead of the room.</p>\n"
        "        <p>That duality defines this entire collection. Every piece plays with the idea of two — mirrored figures, split compositions, contrasting palettes. Whether rendered in the gold-line geometry of the Celestial Animals or the paired Silhouette Aspects, the Gemini prints are designed to feel like they're in conversation with themselves.</p>"
    ),
    'Cancer':      (
        "<p>People born under Cancer are often described as nurturing, emotionally perceptive, and deeply loyal. They feel everything at full volume but don't always show it — the hard shell exists for a reason. Cancer energy is tidal. It pulls inward, holds tight, and moves according to rhythms most people can't feel.</p>\n"
        "        <p>That lunar, tidal quality defines this entire collection. Whether rendered in pearlescent watercolor washes, the deep shadow-work of the Halloween Horrors, or the armored vigilance of the Mythic Guardians — every Cancer piece is designed to feel like it holds more beneath the surface than what's visible at first glance.</p>"
    ),
    'Leo':         (
        "<p>People born under Leo are often described as confident, generous, and magnetically warm. They lead naturally — not by force but by gravity. People orient around them. Leo energy is solar: it radiates outward, it lights up a room, and it expects the room to notice.</p>\n"
        "        <p>That commanding, luminous quality defines this entire collection. Whether rendered in sacred geometry and gold leaf, the cinematic weight of the Mythic Guardians, or the molten roar of the Halloween Horrors — every Leo piece is designed to feel like the centerpiece of whatever wall it hangs on. Nothing in this collection was made to blend in.</p>"
    ),
    'Virgo':       (
        "<p>People born under Virgo are often described as analytical, practical, and deeply attentive to quality. They notice what others miss. They build systems that work. They care about doing things well — not for applause but because doing it badly would bother them more than doing it right. Virgo energy is quiet competence, the kind that runs everything behind the scenes while louder signs take the credit.</p>\n"
        "        <p>That exacting, botanical clarity runs through this entire collection. Whether expressed in the intricate sacred geometry of the Celestial Animals, the careful linework of the Silhouettes, or the precise composition of the Vintage Posters — every Virgo piece is designed with the same attention to detail that defines the sign itself.</p>"
    ),
    'Libra':       (
        "<p>People born under Libra are often described as diplomatic, aesthetically driven, and deeply attuned to fairness. They seek harmony in their relationships, their environments, and even the visual composition of their living spaces. Libra energy is measured, intentional, and always considering both sides — but beneath the composure is a sign that cares fiercely about justice.</p>\n"
        "        <p>That tension between beauty and consequence runs through this entire collection. Whether expressed through the symmetrical sacred geometry of the Celestial Animals, the cold authority of the Mythic Guardians, or the haunting balance of the Halloween Horrors — every Libra piece is designed to look perfectly composed while carrying real weight underneath.</p>"
    ),
    'Scorpio':     (
        "<p>People born under Scorpio are often described as deeply passionate, fiercely loyal, and emotionally magnetic. They don't do anything halfway. They observe, they commit, and once they're in, they're all the way in. Scorpio energy is undercurrent — powerful, hidden, and capable of reshaping everything it touches.</p>\n"
        "        <p>That intensity defines this entire collection. Whether rendered in the dark sacred geometry of the Celestial Animals, the visceral menace of the Halloween Horrors, or the quiet authority of the Silhouettes — every Scorpio piece is designed to feel like it's watching you back. Nothing in this collection is passive.</p>"
    ),
    'Sagittarius': (
        "<p>People born under Sagittarius are often described as adventurous, honest to a fault, and perpetually reaching for something bigger. They chase truth, freedom, and meaning with the same intensity other signs chase stability. Sagittarius energy is forward momentum — the arrow already in flight, the next destination already chosen before the last one's finished.</p>\n"
        "        <p>That restless, expansive energy defines this entire collection. Whether rendered in the blazing sacred geometry of the Celestial Animals, the cinematic motion of the Mythic Guardians, or the untamed warmth of the watercolor washes — every Sagittarius piece is designed to feel like it's going somewhere. Nothing in this collection stands still.</p>"
    ),
    'Capricorn':   (
        "<p>People born under Capricorn are often described as driven, patient, and quietly relentless. They don't chase flashy wins — they build empires stone by stone. Capricorn energy is long-term: it plays the game that takes years, not minutes, and it rarely loses because it never stops working.</p>\n"
        "        <p>That ancient, structural power defines this entire collection. Whether rendered in the stone-carved sacred geometry of the Celestial Animals, the armored authority of the Mythic Guardians, or the patient weight of the Vintage Posters — every Capricorn piece is designed to feel like something built to outlast everything around it.</p>"
    ),
    'Aquarius':    (
        "<p>People born under Aquarius are often described as independent, unconventional, and quietly radical. They think in systems rather than sentiments. They care deeply about humanity in the abstract — about progress, fairness, and the future — even when they seem detached from the individual people around them. Aquarius energy is electric: it arrives suddenly, disrupts what was comfortable, and leaves something better in its wake.</p>\n"
        "        <p>That inventive, future-facing energy defines this entire collection. Whether rendered in the luminous geometry of the Celestial Animals, the angular intelligence of the Punk and Punk Oil series, or the spectral authority of the Mythic Guardians — every Aquarius piece is designed to feel like it came from somewhere ahead of the present moment.</p>"
    ),
    'Pisces':      (
        "<p>People born under Pisces are often described as deeply empathetic, creatively gifted, and emotionally porous. They absorb the feelings around them like water absorbs light — everything goes in, and the surface barely shows it. Pisces energy is oceanic: vast, shapeless, and capable of holding far more than it appears to from the shore.</p>\n"
        "        <p>That dreaming, dissolving quality defines this entire collection. Whether rendered in the luminous sacred geometry of the Celestial Animals, the abyssal weight of the Halloween Horrors, or the soft iridescence of the watercolor washes — every Pisces piece is designed to feel like it exists between two worlds, the way the sign itself does.</p>"
    ),
}


def what_makes_paras(sign):
    return f'        {WHAT_MAKES_PARAS_BY_SIGN.get(sign, "")}' if WHAT_MAKES_PARAS_BY_SIGN.get(sign) else ''


# Per-sign hero tagline (under H1) — bespoke per-sign opening with sign's
# signature energy descriptor. Brief 5A.3 §1 gives Taurus, Scorpio, Pisces
# examples; the rest follow the same pattern.
HERO_TAGLINE_BY_SIGN = {
    'Aries':       "24 original Aries designs across 14 art styles — bold, kinetic, refusing to wait. Crimson-armored mythic guardians, infernal Halloween Horrors, gold-line celestial geometry, anime motion, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Taurus':      "24 original Taurus designs across 14 art styles — grounded, sensual, and unhurried. Watercolor washes, vintage gold-leaf posters, mythic guardian armor, gothic-tinged silhouettes, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Gemini':      "24 original Gemini designs across 14 art styles — quick, dualistic, never quite settling. Mercurial line work, mirrored silhouettes, paired vintage posters, twin watercolor interpretations, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Cancer':      "24 original Cancer designs across 14 art styles — tidal, protective, emotionally layered. Pearlescent watercolor washes, shell-armored mythic guardians, moonlit silhouettes, deep-shadow Halloween Horrors, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Leo':         "24 original Leo designs across 14 art styles — solar, sovereign, impossible to ignore. Gold-leaf celestial work, cinematic mythic guardian portraiture, molten Halloween Horrors, vintage poster regalia, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Virgo':       "24 original Virgo designs across 14 art styles — precise, considered, never overstated. Botanical sacred geometry, clean-lined silhouettes, refined vintage poster compositions, careful watercolor washes, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Libra':       "24 original Libra designs across 14 art styles — composed, deliberate, beautiful and consequential at once. Symmetrical sacred geometry, balanced silhouettes, refined vintage posters, watercolor harmony pieces, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Scorpio':     "24 original Scorpio designs across 14 art styles — depth, intensity, and what's underneath. From the visceral menace of the Halloween Horrors to softer watercolor interpretations, mythic guardian armor in obsidian, vintage poster regalia, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Sagittarius': "24 original Sagittarius designs across 14 art styles — kinetic, expansive, always aiming further. Blazing celestial geometry, mid-draw mythic guardians, untamed watercolor warmth, vintage poster wanderlust, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Capricorn':   "24 original Capricorn designs across 14 art styles — structural, patient, built to outlast. Stone-cut celestial geometry, armored mythic guardians, weathered vintage posters, layered watercolor textures, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Aquarius':    "24 original Aquarius designs across 14 art styles — inventive, electric, ahead of the room. Luminous celestial geometry, angular punk-oil portraits, spectral mythic guardians, refracted watercolor washes, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Pisces':      "24 original Pisces designs across 14 art styles — dreamlike, fluid, and emotionally layered. Watercolor washes, ethereal silhouettes, oceanic mythic guardian armor, abyssal Halloween Horrors, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
}


def hero_tagline_for(sign):
    return HERO_TAGLINE_BY_SIGN.get(sign, HERO_TAGLINE_BY_SIGN['Aries'])


# Lemon Squeezy buy URLs per sign. Empty string => button stays disabled with
# "Coming Soon" copy. Populated URL => button is live, "$24.99" appears in the
# button text, and js/ls-checkout-btn.js opens the LS overlay on click.
LS_URL_BY_SIGN = {
    'Aries':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9bf59872-70d1-49de-8ea3-37372b9b2654?embed=1',
    'Taurus':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/7d8f4359-efdb-4e53-be48-85d8dc713b8e?embed=1',
    'Gemini':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/819241f2-324e-4896-a374-6aeec745ced3?embed=1',
    'Cancer':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/6edf2901-282b-40ba-8cf9-7c9b14a903a9?embed=1',
    'Leo':         'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/979fb682-41c8-4cc0-85dc-1f0cceaca40a?embed=1',
    'Virgo':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/27b54f15-e273-48ad-be62-79ec4c548014?embed=1',
    'Libra':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/7c253f3c-ed16-40f1-a47e-c135acbfb4af?embed=1',
    'Scorpio':     'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/3413255c-d3cc-4e32-ba40-c1519bdb857c?embed=1',
    'Sagittarius': 'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/eb84458a-2b8c-4117-91a7-9c2b7a7f1d66?embed=1',
    'Capricorn':   'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/28803ea4-8728-4da2-949a-7a08b4ca2bf3?embed=1',
    'Aquarius':    'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/e97d3548-3c07-4f4a-b053-265f607fbe4a?embed=1',
    'Pisces':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/d36c351f-7c2d-4303-891f-f6ef963adec4?embed=1',
}


def ls_button_state(sign, price='24.99'):
    """Return (disabled_attr, ls_url, button_text) for the LS button on a sign's
    page. Standing Instruction #6 — when URL is present, button is live with
    "$<price>" in the copy; when URL is empty, button stays disabled with
    "Coming Soon"."""
    url = LS_URL_BY_SIGN.get(sign, '')
    if url:
        return ('', url, f'Buy the {sign} Bundle — ${price}')
    return (' disabled', '', f'Buy the {sign} Bundle — Coming Soon')


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    signs = sys.argv[1:] if len(sys.argv) > 1 else ['Aries']
    for sign in signs:
        if sign not in SIGN_META:
            print(f'SKIP: unknown sign {sign}')
            continue
        out = OUT_DIR / f'{SIGN_META[sign]["slug"]}-zodiac-art.html'
        html = build_page(sign, manifest)
        out.write_text(html, encoding='utf-8')
        lines = html.count('\n') + 1
        size_kb = out.stat().st_size / 1024
        print(f'Wrote {out.name} ({lines} lines, {size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
