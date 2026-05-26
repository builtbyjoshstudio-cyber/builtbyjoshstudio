"""Build per-sign Western Realms pages per the Master Template (Brief Msg 4).

Replaces the Phase 2 placeholder structure with the full master pattern:
LS-direct CTAs, License & POD Trust block, Sister-Realms nav, Related
Collections, Quick Facts, 4 per-Realm sub-sections with descriptions, 8
FAQs, full Product/FAQPage/BreadcrumbList schemas.

Run pattern:
    python tools/build_realm_page_master.py Aries       # Message 4: Aries only
    python tools/build_realm_page_master.py             # default = signs with copy

Signs without per-Realm descriptions in REALM_COPY_BY_SIGN are skipped — the
old Phase 2 page stays in place until Message 5 ships per-sign descriptions
for them.

This script reads:
  images/zodiac/realms/manifest.json (Phase 2 generated)

This script writes:
  collections/<sign>-zodiac-realms.html
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'images' / 'zodiac' / 'realms' / 'manifest.json'
OUT_DIR = ROOT / 'collections'

ALL_SIGNS_ORDER = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

SIGN_META = {
    'Aries':       dict(slug='aries',       symbol='♈', element='Fire',  modality='Cardinal', planet='Mars',    symbol_label='The Ram',          dates='March 21 – April 19',     dates_short='Mar 21 – Apr 19', sister_signs='Leo, Sagittarius',     sku='BBJ-WR-ARIES'),
    'Taurus':      dict(slug='taurus',      symbol='♉', element='Earth', modality='Fixed',    planet='Venus',   symbol_label='The Bull',         dates='April 20 – May 20',        dates_short='Apr 20 – May 20', sister_signs='Virgo, Capricorn',     sku='BBJ-WR-TAURUS'),
    'Gemini':      dict(slug='gemini',      symbol='♊', element='Air',   modality='Mutable',  planet='Mercury', symbol_label='The Twins',        dates='May 21 – June 20',         dates_short='May 21 – Jun 20', sister_signs='Libra, Aquarius',      sku='BBJ-WR-GEMINI'),
    'Cancer':      dict(slug='cancer',      symbol='♋', element='Water', modality='Cardinal', planet='Moon',    symbol_label='The Crab',         dates='June 21 – July 22',        dates_short='Jun 21 – Jul 22', sister_signs='Scorpio, Pisces',      sku='BBJ-WR-CANCER'),
    'Leo':         dict(slug='leo',         symbol='♌', element='Fire',  modality='Fixed',    planet='Sun',     symbol_label='The Lion',         dates='July 23 – August 22',      dates_short='Jul 23 – Aug 22', sister_signs='Aries, Sagittarius',   sku='BBJ-WR-LEO'),
    'Virgo':       dict(slug='virgo',       symbol='♍', element='Earth', modality='Mutable',  planet='Mercury', symbol_label='The Maiden',       dates='August 23 – September 22', dates_short='Aug 23 – Sep 22', sister_signs='Taurus, Capricorn',    sku='BBJ-WR-VIRGO'),
    'Libra':       dict(slug='libra',       symbol='♎', element='Air',   modality='Cardinal', planet='Venus',   symbol_label='The Scales',       dates='September 23 – October 22',dates_short='Sep 23 – Oct 22', sister_signs='Gemini, Aquarius',     sku='BBJ-WR-LIBRA'),
    'Scorpio':     dict(slug='scorpio',     symbol='♏', element='Water', modality='Fixed',    planet='Pluto',   symbol_label='The Scorpion',     dates='October 23 – November 21', dates_short='Oct 23 – Nov 21', sister_signs='Cancer, Pisces',       sku='BBJ-WR-SCORPIO'),
    'Sagittarius': dict(slug='sagittarius', symbol='♐', element='Fire',  modality='Mutable',  planet='Jupiter', symbol_label='The Archer',       dates='November 22 – December 21',dates_short='Nov 22 – Dec 21', sister_signs='Aries, Leo',           sku='BBJ-WR-SAGITTARIUS'),
    'Capricorn':   dict(slug='capricorn',   symbol='♑', element='Earth', modality='Cardinal', planet='Saturn',  symbol_label='The Goat',         dates='December 22 – January 19', dates_short='Dec 22 – Jan 19', sister_signs='Taurus, Virgo',        sku='BBJ-WR-CAPRICORN'),
    'Aquarius':    dict(slug='aquarius',    symbol='♒', element='Air',   modality='Fixed',    planet='Uranus',  symbol_label='The Water Bearer', dates='January 20 – February 18', dates_short='Jan 20 – Feb 18', sister_signs='Gemini, Libra',        sku='BBJ-WR-AQUARIUS'),
    'Pisces':      dict(slug='pisces',      symbol='♓', element='Water', modality='Mutable',  planet='Neptune', symbol_label='The Fish',         dates='February 19 – March 20',   dates_short='Feb 19 – Mar 20', sister_signs='Cancer, Scorpio',      sku='BBJ-WR-PISCES'),
}

# Per-Realm prose for each sign — keys MUST match the actual Realm titles in
# images/zodiac/realms/manifest.json (Phase 2 captured them from source files).
# Brief 5B.3 — 2-3 atmospheric sentences each.
REALM_COPY_BY_SIGN = {
    'Aries': {
        'Horizon of Fire and Dust':  'A vast horizon where crimson sky meets scorched earth, lit by a perpetual firestorm. The Aries Realm of momentum stretched flat across the open plain.',
        'The Crimson Battleforge':   'A cathedral of fire and steel — anvils the size of altars, lava as river, every surface ringing. The Aries Realm of creation under pressure.',
        'The Crimson Expansion':     'A volcanic frontier expanding outward from a single ignition point. Aries energy as a cosmic event, viewed from inside the blast.',
        'The Ignition Horizon':      'A horizon on fire — molten skies over glowing crimson geometry. The Aries Realm where every dawn is a first strike.',
    },
    'Taurus': {
        'The Celestial Pastures':    "Rolling green meadows beneath a star-strewn sky — the bull's domain extended into the cosmos. The Taurus Realm where pasture meets nebula, slow time held against deep time.",
        'The Emerald Drift':         'A slow-moving expanse of mossy stone and slow river, painted in deep greens and gold light. The Taurus Realm of unhurried beauty — landscape that asks you to stop and notice.',
        'The Emerald Vale':          "A wide forested valley enclosed by stone, every surface mossed and weighted with time. The Taurus Realm of held space — the kind of place that's been waiting for you.",
        'The Verdant Ridge':         'A sheer green ridgeline at golden hour, layered hills receding toward soft horizon. The Taurus Realm of permanence — earth-toned scale, gentle endurance.',
    },
    'Gemini': {
        'Reflections Between Worlds':'A landscape pierced by reflective surfaces — pools, mirror-glass, twin moons casting paired light. The Gemini Realm where every view contains its inversion.',
        'The Mirrored Divide':       'A canyon split by a mirrored seam, two halves of the same landscape facing each other across the cut. The Gemini Realm of duality made structural.',
        'The Mirrored Spiral':       'A double-helix of light spiraling against a cosmic backdrop, the same shape twinned and inverted. The Gemini Realm of conversation as architecture.',
        'The Skybound Library':      'Floating shelves of arcane volumes suspended in a starlit sky, the air thick with curiosity. The Gemini Realm of held knowledge, waiting to be doubled.',
    },
    'Cancer': {
        'The Lunar Coastline':       "An endless shoreline beneath a swollen moon, tide-pools glowing with reflected light. The Cancer Realm where the sea touches the sky's own gravity.",
        'The Lunar Veil':            'A diffuse silver atmosphere draped over still water, the moon hidden behind translucent cloud. The Cancer Realm of held mystery — sensitivity rendered as weather.',
        'The Moonlit Cove':          'A sheltered bay enclosed by stone, illuminated by a single low moon. The Cancer Realm of protected space — the inside of the shell, made geography.',
        'The Tides of the Universe': 'Cosmic-scale waves of starlight rolling across a galactic shore, tidal rhythm written into the architecture of space itself. The Cancer Realm where emotion is a cosmic force.',
    },
    'Leo': {
        'Solar Plains Beneath a Burning Sky': 'Wide golden grasslands stretched beneath a sky on fire, the horizon line blazing with reflected sun. The Leo Realm of unrivaled radiance — landscape as throne room.',
        'The Golden Citadel':        'A fortress of light rising from molten ground, every tower catching the sun like a polished crown. The Leo Realm where presence has been built into architecture.',
        'The Solar Eruption':        "A solar flare arcing across a celestial landscape, mountains glowing in the wake. The Leo Realm of radiant intensity — the sun's own confidence at planetary scale.",
        'The Solar Expanse':         'A wide cosmic vista lit edge-to-edge by golden light, every detail caught in solar glow. The Leo Realm where there is no shadow, only degrees of brilliance.',
    },
    'Virgo': {
        'Fields Beneath the Cosmic Veil': 'Cultivated rows of grain stretching to a horizon hung with a veil of cosmic light. The Virgo Realm where careful work meets cosmic order.',
        'The Ordered Constellation': 'Stars arranged in a precise pattern across deep velvet sky, every point of light in its assigned place. The Virgo Realm of cosmic precision — chaos refused entry.',
        'The Starlit Fields':        'Open fields under a thick canopy of stars, every blade of grass visible in soft starlight. The Virgo Realm of quiet attentiveness — the universe as something worth noticing.',
        'The Verdant Workshop':      'An open-air sanctuary of botanical work and careful arrangement, surrounded by stone and light. The Virgo Realm of devoted craft — landscape as discipline.',
    },
    'Libra': {
        'Balance of Light and Void': 'A composition split exactly between radiant light and starless dark, two halves held in tension. The Libra Realm where opposition becomes form.',
        'The Equilibrium Canyon':    'A vast canyon perfectly balanced on either side of its central seam — mirrored cliffs, paired pillars, geometry as restraint. The Libra Realm of measured space.',
        'The Ivory Court':           'A pale, columned arena beneath a soft sky, every surface honed to elegance. The Libra Realm where judgment is delivered with composure — beauty that carries weight.',
        'The Symmetry of Light':     'Architectural beams of light arranged in perfect symmetry against a violet sky, the composition reading like a balanced equation. The Libra Realm of aesthetic order.',
    },
    'Scorpio': {
        'The Obsidian Abyss':        'A bottomless chasm of black volcanic glass, lit only by deep crimson veins running through its walls. The Scorpio Realm of unmapped depth — where the sign keeps what it knows.',
        'The Plasma Desert':         'A waterless expanse under violet skies, electrified air shimmering above black-glass sand. The Scorpio Realm of charged silence — beautiful, dangerous, alive.',
        'The Plasma Dunes':          'Rolling dunes of dark plasma-glass, ridged in violet light, sky thick with electric charge. The Scorpio Realm of slow-burning transformation — landscape as undercurrent.',
        'The Violet Storm':          'A landscape consumed by a violet electrical storm — lightning architecture, charged horizon, the sky in active reformation. The Scorpio Realm of intensity made weather.',
    },
    'Sagittarius': {
        'The Celestial Horizon':     'An endless cosmic vista where the horizon line is the boundary between worlds — stars one side, terra the other. The Sagittarius Realm of looking outward by default.',
        'The Celestial Trajectory':  "An arcing trajectory of light crossing the sky, marking a path already chosen. The Sagittarius Realm of forward motion — the arrow's flight made permanent landscape.",
        'The Endless Voyage':        "A traveler's vista of open road and far horizon, the journey itself rendered as terrain. The Sagittarius Realm of perpetual departure — never quite arriving, never wanting to.",
        'The Horizon Expanse':       'A wide-open horizon under expansive sky, scale calibrated to make the next destination feel close. The Sagittarius Realm where the next place is always visible.',
    },
    'Capricorn': {
        'The Ascending Nebula':      'A nebular cloud climbing upward through cosmic space, structured like a mountain ascending in slow time. The Capricorn Realm where ambition is shaped at galactic scale.',
        'The Cosmic Summit':         'A peak of stone and starlight rising into open sky, surrounded by the deep cold of cosmic altitude. The Capricorn Realm of arrived ambition — view from the top, after the climb.',
        'The Star-Crowned Peak':     'A high mountain summit ringed by a halo of stars, its crown literal and astronomical. The Capricorn Realm where altitude becomes sovereignty.',
        'The Stone Pinnacle':        'A sheer column of stone reaching impossibly high, every layer a record of time. The Capricorn Realm of patient endurance — landscape as long memory.',
    },
    'Aquarius': {
        'The Celestial Spire':       'A towering spire of light piercing a cosmic sky, geometry meeting transmission. The Aquarius Realm of architectural intelligence — innovation made monument.',
        'The Cosmic Waterfall':      "A cascade of starlight falling from a galactic ridge into deep space, the water-bearer's pour rendered cosmic. The Aquarius Realm where ideas flow downhill at the speed of light.",
        'The Flow of Stars':         'A river of stars curving across an empty sky, current visible in the spacing of points. The Aquarius Realm of dispersed intelligence — pattern emerging from drift.',
        'The River of Light':        'A luminous river running through a velvet-dark landscape, banks lit by reflected radiance. The Aquarius Realm of inherited futurism — landscape from somewhere ahead.',
    },
    'Pisces': {
        'The Converging Currents':   'Two great ocean currents flowing toward each other across a vast water-scape, the meeting point shimmering with energy. The Pisces Realm of held opposites — direction without resolution.',
        'The Dreamweave Ocean':      "An ocean composed of woven dream-light, depths visible through translucent layers. The Pisces Realm where what's submerged is the entire architecture.",
        'The Infinite Sea':          'An ocean stretching beyond any horizon, the sky and water indistinguishable, scale unmeasurable. The Pisces Realm of dissolved boundaries.',
        'The Sea of Galaxies':       'A cosmic ocean where galaxies float like islands of light, every depth holding another world. The Pisces Realm where ocean becomes universe and back again.',
    },
}

# 3-paragraph astrological context per sign. Paras 1-2 lift the same astrology
# used in tools/build_western_signs_page.py (Msg 5A — WHAT_MAKES_PARAS_BY_SIGN);
# para 3 is rewritten here to tie the energy to the Realm titles instead of the
# 14 Western Signs styles.
ZODIAC_CONTEXT_PROSE = {
    'Aries': (
        '<p>Aries is the first sign of the zodiac, spanning March 21 through April 19. It is a fire sign ruled by Mars — the planet of drive, aggression, and action. Aries is represented by the ram, a symbol of headfirst momentum and refusal to back down.</p>\n'
        "        <p>People born under Aries are often described as bold, competitive, and direct. They tend to be initiators — the ones who start the project, make the first move, and set the pace. Aries energy is forward motion. It doesn't wait for permission and it doesn't look back.</p>\n"
        '        <p>That energy translates directly into the Aries Realms. Whether rendered as the molten Crimson Battleforge or the open Ignition Horizon, every Aries Realm is designed to feel like it is mid-motion — landscapes still cooling from a strike that just happened.</p>'
    ),
    'Taurus': (
        '<p>Taurus is the second sign of the zodiac, spanning April 20 through May 20. It is an earth sign ruled by Venus — the planet of beauty, pleasure, and material value. Taurus is represented by the bull, a symbol of endurance, determination, and grounded strength.</p>\n'
        "        <p>People born under Taurus are often described as reliable, patient, and deeply sensory. They value quality over quantity, comfort over chaos, and tend to build things meant to last. Taurus energy is slow and deliberate — it doesn't rush, but it doesn't quit either.</p>\n"
        '        <p>That steadiness translates directly into the Taurus Realms. Whether rendered as the held quiet of the Emerald Vale or the cosmic pasture of the Celestial Pastures, every Taurus Realm is designed to feel like it has been settling into place for a long time — landscapes built to outlast the moment you stand in front of them.</p>'
    ),
    'Gemini': (
        '<p>Gemini is the third sign of the zodiac, spanning May 21 through June 20. It is an air sign ruled by Mercury — the planet of communication, intellect, and adaptability. Gemini is represented by the twins, a symbol of duality, curiosity, and the ability to hold two truths at once.</p>\n'
        "        <p>People born under Gemini are often described as quick-witted, versatile, and endlessly curious. They move between ideas, conversations, and interests with a fluidity that other signs can't match. Gemini energy is mental speed — the sign that's already three thoughts ahead of the room.</p>\n"
        '        <p>That duality translates directly into the Gemini Realms. Whether rendered as the suspended shelves of the Skybound Library or the mirrored seam of the Mirrored Divide, every Gemini Realm is designed around doubling — paired forms, twinned compositions, two of everything always implied.</p>'
    ),
    'Cancer': (
        '<p>Cancer is the fourth sign of the zodiac, spanning June 21 through July 22. It is a water sign ruled by the Moon — the celestial body of emotion, memory, and intuition. Cancer is represented by the crab, a symbol of protection, sensitivity, and the instinct to guard what matters most.</p>\n'
        "        <p>People born under Cancer are often described as nurturing, emotionally perceptive, and deeply loyal. They feel everything at full volume but don't always show it — the hard shell exists for a reason. Cancer energy is tidal. It pulls inward, holds tight, and moves according to rhythms most people can't feel.</p>\n"
        "        <p>That tidal, lunar quality translates directly into the Cancer Realms. Whether rendered as the enclosed silver of the Moonlit Cove or the cosmic surge of the Tides of the Universe, every Cancer Realm is designed to feel like it holds more beneath the surface than what's visible at first glance — landscapes that breathe with the moon.</p>"
    ),
    'Leo': (
        '<p>Leo is the fifth sign of the zodiac, spanning July 23 through August 22. It is a fire sign ruled by the Sun — the only sign in the zodiac governed by a star rather than a planet. Leo is represented by the lion, a symbol of sovereignty, courage, and the kind of presence that doesn\'t need to announce itself.</p>\n'
        '        <p>People born under Leo are often described as confident, generous, and magnetically warm. They lead naturally — not by force but by gravity. People orient around them. Leo energy is solar: it radiates outward, it lights up a room, and it expects the room to notice.</p>\n'
        '        <p>That solar authority translates directly into the Leo Realms. Whether rendered as the molten architecture of the Golden Citadel or the wide-open radiance of the Solar Expanse, every Leo Realm is designed to feel like the centerpiece of whatever space it hangs in — landscapes that hold court.</p>'
    ),
    'Virgo': (
        '<p>Virgo is the sixth sign of the zodiac, spanning August 23 through September 22. It is an earth sign ruled by Mercury — the planet of intellect, communication, and analysis. Virgo is represented by the maiden, a symbol of purity not in the moral sense but in the sense of precision — the drive to refine, to improve, to get every detail right.</p>\n'
        '        <p>People born under Virgo are often described as analytical, practical, and deeply attentive to quality. They notice what others miss. They build systems that work. They care about doing things well — not for applause but because doing it badly would bother them more than doing it right. Virgo energy is quiet competence, the kind that runs everything behind the scenes while louder signs take the credit.</p>\n'
        '        <p>That exacting clarity translates directly into the Virgo Realms. Whether rendered as the precise arrangement of the Ordered Constellation or the botanical care of the Verdant Workshop, every Virgo Realm is composed with the same attention to detail that defines the sign — landscapes where nothing is accidental and nothing is wasted.</p>'
    ),
    'Libra': (
        '<p>Libra is the seventh sign of the zodiac, spanning September 23 through October 22. It is an air sign ruled by Venus — the planet of beauty, love, and aesthetic value. Libra is represented by the scales, the only inanimate symbol in the zodiac — a sign defined not by instinct or force but by the pursuit of balance.</p>\n'
        '        <p>People born under Libra are often described as diplomatic, aesthetically driven, and deeply attuned to fairness. They seek harmony in their relationships, their environments, and even the visual composition of their living spaces. Libra energy is measured, intentional, and always considering both sides — but beneath the composure is a sign that cares fiercely about justice.</p>\n'
        '        <p>That tension between beauty and consequence translates directly into the Libra Realms. Whether rendered as the honed elegance of the Ivory Court or the mirrored geometry of the Equilibrium Canyon, every Libra Realm is composed to look perfectly balanced while carrying real weight beneath — landscapes that read as composition, not improvisation.</p>'
    ),
    'Scorpio': (
        '<p>Scorpio is the eighth sign of the zodiac, spanning October 23 through November 21. It is a water sign ruled by Pluto — the planet of transformation, death, and rebirth (with Mars as traditional co-ruler). Scorpio is represented by the scorpion, a symbol of intensity, resilience, and the willingness to go where other signs won\'t.</p>\n'
        "        <p>People born under Scorpio are often described as deeply passionate, fiercely loyal, and emotionally magnetic. They don't do anything halfway. They observe, they commit, and once they're in, they're all the way in. Scorpio energy is undercurrent — powerful, hidden, and capable of reshaping everything it touches.</p>\n"
        '        <p>That intensity translates directly into the Scorpio Realms. Whether rendered as the unmapped chasm of the Obsidian Abyss or the charged sky of the Violet Storm, every Scorpio Realm is designed to feel like it has something running underneath — landscapes that watch back.</p>'
    ),
    'Sagittarius': (
        '<p>Sagittarius is the ninth sign of the zodiac, spanning November 22 through December 21. It is a fire sign ruled by Jupiter — the planet of expansion, philosophy, and boundless optimism. Sagittarius is represented by the archer, a centaur drawing back a bow, aiming at something just beyond the horizon.</p>\n'
        "        <p>People born under Sagittarius are often described as adventurous, honest to a fault, and perpetually reaching for something bigger. They chase truth, freedom, and meaning with the same intensity other signs chase stability. Sagittarius energy is forward momentum — the arrow already in flight, the next destination already chosen before the last one's finished.</p>\n"
        "        <p>That restless, expansive energy translates directly into the Sagittarius Realms. Whether rendered as the open road of the Endless Voyage or the arcing path of the Celestial Trajectory, every Sagittarius Realm is designed to feel like it's going somewhere — landscapes where the next destination is always part of the composition.</p>"
    ),
    'Capricorn': (
        '<p>Capricorn is the tenth sign of the zodiac, spanning December 22 through January 19. It is an earth sign ruled by Saturn — the planet of structure, discipline, and time. Capricorn is represented by the sea-goat, a mythic creature that climbs mountains and navigates depths — a symbol of ambition that operates in both the visible world and the one beneath the surface.</p>\n'
        "        <p>People born under Capricorn are often described as driven, patient, and quietly relentless. They don't chase flashy wins — they build empires stone by stone. Capricorn energy is long-term: it plays the game that takes years, not minutes, and it rarely loses because it never stops working.</p>\n"
        "        <p>That ancient, structural power translates directly into the Capricorn Realms. Whether rendered as the time-layered Stone Pinnacle or the high-altitude clarity of the Cosmic Summit, every Capricorn Realm is designed to feel like something built to outlast everything around it — landscapes that don't move because they've already arrived.</p>"
    ),
    'Aquarius': (
        '<p>Aquarius is the eleventh sign of the zodiac, spanning January 20 through February 18. It is an air sign ruled by Uranus — the planet of rebellion, innovation, and sudden change (with Saturn as traditional co-ruler). The water bearer pours knowledge and truth, not water — making Aquarius the sign of ideas, not emotions.</p>\n'
        '        <p>People born under Aquarius are often described as independent, unconventional, and quietly radical. They think in systems rather than sentiments. They care deeply about humanity in the abstract — about progress, fairness, and the future — even when they seem detached from the individual people around them. Aquarius energy is electric: it arrives suddenly, disrupts what was comfortable, and leaves something better in its wake.</p>\n'
        '        <p>That inventive, future-facing energy translates directly into the Aquarius Realms. Whether rendered as the rising architecture of the Celestial Spire or the cosmic cascade of the Cosmic Waterfall, every Aquarius Realm is designed to feel like it came from somewhere ahead of the present moment — landscapes that read as transmission.</p>'
    ),
    'Pisces': (
        "<p>Pisces is the twelfth and final sign of the zodiac, spanning February 19 through March 20. It is a water sign ruled by Neptune — the planet of dreams, illusion, and the subconscious (with Jupiter as traditional co-ruler). Pisces is represented by two fish swimming in opposite directions, a symbol of the sign's constant pull between the real world and the one they carry inside their head.</p>\n"
        '        <p>People born under Pisces are often described as deeply empathetic, creatively gifted, and emotionally porous. They absorb the feelings around them like water absorbs light — everything goes in, and the surface barely shows it. Pisces energy is oceanic: vast, shapeless, and capable of holding far more than it appears to from the shore.</p>\n'
        '        <p>That dreaming, dissolving quality translates directly into the Pisces Realms. Whether rendered as the woven depths of the Dreamweave Ocean or the cosmic ocean of the Sea of Galaxies, every Pisces Realm is designed to feel like it exists between two worlds — landscapes where the boundary between real and imagined never quite holds.</p>'
    ),
}


# Per-sign hero tagline (under H1) — bespoke landscape descriptor per Brief 5B.4
# examples (Aries fire-touched / Taurus verdant grounded / Pisces fluid oceanic /
# Capricorn sheer summit-cold). All tail with the bundle facts.
HERO_TAGLINE_BY_SIGN = {
    'Aries':       "Four mythic Aries Realms — fire-touched landscapes rendered with cinematic depth. The Crimson Battleforge, the Ignition Horizon, and two more volcanic frontiers, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Taurus':      "Four mythic Taurus Realms — verdant, grounded landscapes rendered with cinematic depth. The Emerald Vale, the Celestial Pastures, and two more held-time interiors, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Gemini':      "Four mythic Gemini Realms — dualistic, conversational landscapes rendered with cinematic depth. The Skybound Library, the Mirrored Spiral, and two more paired environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Cancer':      "Four mythic Cancer Realms — tidal, lunar landscapes rendered with cinematic depth. The Moonlit Cove, the Tides of the Universe, and two more emotionally layered environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Leo':         "Four mythic Leo Realms — radiant, sun-touched landscapes rendered with cinematic depth. The Golden Citadel, the Solar Eruption, and two more sovereign environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Virgo':       "Four mythic Virgo Realms — precise, considered landscapes rendered with cinematic depth. The Verdant Workshop, the Ordered Constellation, and two more meticulously composed environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Libra':       "Four mythic Libra Realms — symmetrical, composed landscapes rendered with cinematic depth. The Ivory Court, the Equilibrium Canyon, and two more aesthetically balanced environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Scorpio':     "Four mythic Scorpio Realms — deep, charged landscapes rendered with cinematic depth. The Obsidian Abyss, the Violet Storm, and two more transformative environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Sagittarius': "Four mythic Sagittarius Realms — expansive, horizon-bound landscapes rendered with cinematic depth. The Endless Voyage, the Celestial Trajectory, and two more outward-aimed environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Capricorn':   "Four mythic Capricorn Realms — sheer, summit-cold landscapes rendered with cinematic depth. The Stone Pinnacle, the Cosmic Summit, and two more enduring environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Aquarius':    "Four mythic Aquarius Realms — luminous, ahead-of-now landscapes rendered with cinematic depth. The Celestial Spire, the Cosmic Waterfall, and two more electric environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Pisces':      "Four mythic Pisces Realms — fluid, oceanic landscapes rendered with cinematic depth. The Dreamweave Ocean, the Sea of Galaxies, and two more dissolving environments, each delivered in two numbered variants across three print-ready sizes and both PNG and JPG. 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
}


def hero_tagline_for(sign):
    return HERO_TAGLINE_BY_SIGN.get(sign, HERO_TAGLINE_BY_SIGN['Aries'])


# Lemon Squeezy buy URLs per sign. Empty string => button stays disabled with
# "Coming Soon" copy. Populated URL => button is live, "$14.99" appears in the
# button text, and js/ls-checkout-btn.js opens the LS overlay on click.
LS_URL_BY_SIGN = {
    'Aries':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/2d91db12-fb82-43f8-9a5e-dc00985b5c44?embed=1',
    'Taurus':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/ede31a69-89bc-4a91-a032-eff90fec4822?embed=1',
    'Gemini':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/e3ebd386-4732-4b92-a1f3-5ecf359dcd65?embed=1',
    'Cancer':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/29aa0221-9029-4e43-beb8-b04fb8b4ed7d?embed=1',
    'Leo':         'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/d2de9520-f954-4c89-8f01-ef7c0c381d4c?embed=1',
    'Virgo':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/b51a078d-9e6d-41f7-b9cf-cf03dab9f5c0?embed=1',
    'Libra':       'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9fc68b81-a42f-4fe5-ab98-dfc335c5225a?embed=1',
    'Scorpio':     'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/c26077cf-5e8d-49b3-b3e3-3fe141da8aba?embed=1',
    'Sagittarius': 'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/d284ea3f-bb98-47b5-83e3-36d108df7f14?embed=1',
    'Capricorn':   'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9542be16-35b8-49a7-8366-67d6aecab104?embed=1',
    'Aquarius':    'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/9482fef7-2db3-4300-b5d1-7c645f0d2c85?embed=1',
    'Pisces':      'https://tynkrtoolsco.lemonsqueezy.com/checkout/buy/c64f38b8-2a61-4b7d-a5a7-70b197b9f6fd?embed=1',
}


def ls_button_state(sign, price='14.99'):
    """Return (disabled_attr, ls_url, button_text) for the LS button on a sign's
    page. Standing Instruction #6 — when URL is present, button is live with
    "$<price>" in the copy; when URL is empty, button stays disabled with
    "Coming Soon"."""
    url = LS_URL_BY_SIGN.get(sign, '')
    if url:
        return ('', url, f'Buy the {sign} Realms Bundle — ${price}')
    return (' disabled', '', f'Buy the {sign} Realms Bundle — Coming Soon')


def build_realm_block(title, designs, sign, description):
    """Render a single Realm sub-section: title + description + 2 variant cards."""
    cards = []
    for d in sorted(designs, key=lambda x: int(x['variant'])):
        cards.append(
            '            <div class="design-card">\n'
            f'              <img src="../{d["webp_path"]}" alt="{title} variant {d["variant"]} — {sign} Western Realms art print" loading="lazy" width="720" height="900">\n'
            '              <div class="design-card-body">\n'
            f'                <h4>Variant {d["variant"]}</h4>\n'
            '              </div>\n'
            '            </div>'
        )
    return (
        f'        <div class="realm-block">\n'
        f'          <h3 class="realm-block-title">{title}</h3>\n'
        f'          <p class="realm-block-desc">{description}</p>\n'
        '          <div class="designs-grid">\n\n' + '\n\n'.join(cards) + '\n\n'
        '          </div>\n'
        '        </div>'
    )


def build_sister_nav(current_sign):
    cards = []
    for s in ALL_SIGNS_ORDER:
        m = SIGN_META[s]
        is_current = (s == current_sign)
        if is_current:
            inner = f'<div class="sister-card sister-card-current"><span class="sister-glyph">{m["symbol"]}</span><span class="sister-name">{s}</span><span class="sister-meta">{m["element"]} · {m["dates_short"]}</span><span class="sister-here">You are here</span></div>'
        else:
            href = f'{m["slug"]}-zodiac-realms.html'
            inner = f'<a href="{href}" class="sister-card"><span class="sister-glyph">{m["symbol"]}</span><span class="sister-name">{s}</span><span class="sister-meta">{m["element"]} · {m["dates_short"]}</span></a>'
        cards.append(f'        {inner}')
    return '\n'.join(cards)


def faq_data(sign):
    realm_titles_csv = ', '.join(sorted(REALM_COPY_BY_SIGN.get(sign, {}).keys())) or 'four Realm designs'
    return [
        (f'What is included in the {sign} Western Realms Bundle?',
         f'The {sign} Realms bundle includes 48 print-ready digital files covering 4 unique {sign} Realm designs ({realm_titles_csv}), each with 2 numbered variants. Every design ships in three aspect ratios (1:1, 4:5, 2:3) and both PNG and JPG formats, at 300 DPI. The bundle also includes a License Agreement and a Print Guide as PDFs.'),
        (f'How much does the {sign} Western Realms Bundle cost?',
         f'The {sign} Realms bundle is priced at $14.99 — one-time payment, instant digital download. That works out to roughly $1.87 per unique design or $0.31 per file variant.'),
        (f'Can I use the {sign} Realms Bundle for print-on-demand or commercial sales?',
         'Yes. The license includes print-on-demand rights for up to 100 physical units per individual design, cumulative across all formats, vendors, and time periods combined. You can sell framed prints, posters, canvases, and similar physical products made from the Realm designs within that cap. For more than 100 prints of any single design, contact Built by Josh Studio LLC about extended commercial licensing.'),
        (f'What sizes can I print the {sign} Realms art at?',
         'The largest file (6000 × 9000 pixels) prints crisply up to 20" × 30" at full 300 DPI. With a print provider running 150 DPI for large-format jobs, prints up to roughly 40" × 60" still look excellent. The bundle also includes 1:1 files (4800 × 4800) for square framing and 4:5 files (4800 × 6000) for standard portrait sizes like 8×10 and 16×20.'),
        (f'How were the {sign} Realm designs created?',
         f"The {sign} Realm designs were created by Built by Josh Studio LLC using a combination of human creative direction and AI image generation tools, including Leonardo.ai. Every design is selected, curated, refined, and finalized by the studio's founder. This is disclosed in full in the license agreement included with every bundle."),
        (f"What's the difference between the {sign} Realms Bundle and the {sign} Zodiac Art Bundle?",
         f'The {sign} Zodiac Art Bundle ($24.99) contains 144 files covering 24 figure-based designs across 14 art styles — the sign rendered as a character. The {sign} Realms Bundle ($14.99) contains 48 files covering 4 landscape-style Realms with 2 variants each — {sign} rendered as place rather than figure. The two pair naturally as a figure-and-environment wall arrangement.'),
        (f'Where can I buy the {sign} Western Realms Bundle?',
         f'The {sign} Realms Bundle is sold directly on builtbyjoshstudio.com via secure Lemon Squeezy checkout. Click the "Buy the {sign} Realms Bundle" button on this page to open the checkout overlay, complete the purchase, and receive instant access to the full bundle — no Etsy account required, no marketplace fees, files delivered immediately to your email. The Built By Josh Studio Etsy storefront carries other studio work but does not sell the full Collection bundles.'),
        ('Do you have Realms for the other 11 Western zodiac signs?',
         'Yes. Built By Josh Studio publishes 12 sign-specific Realms bundles — one for every Western zodiac sign (Aries through Pisces). All 12 bundles share identical structure: 48 files, 4 Realm designs, 2 variants each, three aspect ratios, both PNG and JPG. The Chinese Realms Collection covers all 12 Chinese zodiac animals in a single bundle, also landscape-style.'),
    ]


def faq_schema_data(sign):
    """ASCII-safe variants for JSON. Replace inch marks with 'by' / 'inches'."""
    out = []
    for q, a in faq_data(sign):
        a_schema = (
            a
            .replace('20" × 30"', '20 by 30 inches')
            .replace('40" × 60"', '40 by 60 inches')
            .replace('8×10', '8x10')
            .replace('16×20', '16x20')
            .replace('×', 'x')
            .replace(f'"Buy the {sign} Realms Bundle"', f'Buy the {sign} Realms Bundle')
        )
        out.append({'q': q, 'a': a_schema})
    return out


def build_page(sign, manifest):
    m = SIGN_META[sign]
    slug = m['slug']
    sign_data = manifest[sign]
    designs = sign_data['designs']
    hub_thumb = sign_data['hub_thumb']  # images/zodiac/realms/<sign>.webp

    realm_copy = REALM_COPY_BY_SIGN.get(sign, {})
    if not realm_copy:
        raise SystemExit(f'No per-Realm copy for {sign} yet — add to REALM_COPY_BY_SIGN before regenerating.')

    # Group designs by Realm title, render 4 sub-sections
    by_title = {}
    for d in designs:
        by_title.setdefault(d['title'], []).append(d)
    titles_alpha = sorted(by_title.keys())
    realm_blocks_html = '\n\n'.join(
        build_realm_block(t, by_title[t], sign, realm_copy.get(t, ''))
        for t in titles_alpha
    )

    sister_nav = build_sister_nav(sign)

    # FAQ visible HTML
    faqs = faq_data(sign)
    faq_items_html = '\n'.join(
        '      <div class="faq-item">\n'
        f'        <h3>{q}</h3>\n'
        f'        <p>{a}</p>\n'
        '      </div>'
        for q, a in faqs
    )

    # FAQPage schema
    faq_schema = faq_schema_data(sign)
    faq_schema_json = ',\n'.join(
        '      {\n'
        '        "@type": "Question",\n'
        f'        "name": {json.dumps(f["q"])},\n'
        '        "acceptedAnswer": {\n'
        '          "@type": "Answer",\n'
        f'          "text": {json.dumps(f["a"])}\n'
        '        }\n'
        '      }'
        for f in faq_schema
    )

    zodiac_context = ZODIAC_CONTEXT_PROSE.get(sign, '')

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
  <title>{sign} Western Realms Bundle — 48 Print-Ready Landscape Files | BBJ Studio</title>
  <meta name="description" content="The {sign} Western Realms bundle from Built By Josh Studio — 48 print-ready landscape-style files covering 4 unique Realm designs with 2 variants each. Personal use + print-on-demand licensed up to 100 prints per design. Instant download from $14.99." />
  <link rel="canonical" href="https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html" />

  <meta property="og:title" content="{sign} Western Realms Bundle — 48 Print-Ready Landscape Files | BBJ Studio" />
  <meta property="og:description" content="48 print-ready landscape-style files covering 4 {sign} Realm designs with 2 variants each. Personal use + POD up to 100 prints per design." />
  <meta property="og:type" content="product" />
  <meta property="og:url" content="https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html" />
  <meta property="og:site_name" content="Built By Josh Studio" />
  <meta property="og:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{sign} Western Realms Bundle — 48 Print-Ready Landscape Files | BBJ Studio" />
  <meta name="twitter:description" content="48 print-ready landscape-style files covering 4 {sign} Realm designs with 2 variants each." />
  <meta name="twitter:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />

  <!-- Schema.org: BreadcrumbList (4-level) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://builtbyjoshstudio.com/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Collections", "item": "https://builtbyjoshstudio.com/collections/" }},
      {{ "@type": "ListItem", "position": 3, "name": "Western Realms", "item": "https://builtbyjoshstudio.com/index.html#western-realms" }},
      {{ "@type": "ListItem", "position": 4, "name": "{sign} Western Realms Bundle", "item": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html" }}
    ]
  }}
  </script>

  <!-- Schema.org: Product -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html#product",
    "name": "{sign} Western Realms Bundle — 48 Print-Ready Landscape Files",
    "description": "The {sign} Western Realms Bundle contains 48 print-ready digital files covering 4 unique landscape-style {sign} Realm designs, each with 2 numbered variants. Every design ships in three aspect ratios (1:1, 4:5, 2:3) at 300 DPI in both PNG and JPG. Licensed for personal use and print-on-demand up to 100 prints per design.",
    "image": [
      "https://builtbyjoshstudio.com/{hub_thumb}"
    ],
    "url": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html",
    "sku": "{m['sku']}",
    "category": "Digital Art / Zodiac Art / Western Realms",
    "brand": {{ "@type": "Brand", "name": "Built By Josh Studio" }},
    "manufacturer": {{ "@id": "https://builtbyjoshstudio.com/#organization" }},
    "additionalProperty": [
      {{"@type": "PropertyValue", "name": "File Count", "value": "48"}},
      {{"@type": "PropertyValue", "name": "Realm Designs", "value": "4"}},
      {{"@type": "PropertyValue", "name": "Variants per Design", "value": "2"}},
      {{"@type": "PropertyValue", "name": "Resolution", "value": "300 DPI"}},
      {{"@type": "PropertyValue", "name": "Maximum Dimensions", "value": "6000 x 9000 pixels"}},
      {{"@type": "PropertyValue", "name": "Aspect Ratios", "value": "1:1, 4:5, 2:3"}},
      {{"@type": "PropertyValue", "name": "File Formats", "value": "PNG, JPG"}},
      {{"@type": "PropertyValue", "name": "Color Profile", "value": "sRGB"}},
      {{"@type": "PropertyValue", "name": "License", "value": "Personal use + POD up to 100 prints per design"}},
      {{"@type": "PropertyValue", "name": "Zodiac Sign", "value": "{sign}"}},
      {{"@type": "PropertyValue", "name": "Element", "value": "{m['element']}"}},
      {{"@type": "PropertyValue", "name": "Style", "value": "Landscape-style hybrid cosmos"}},
      {{"@type": "PropertyValue", "name": "Date Range", "value": "{m['dates']}"}}
    ],
    "datePublished": "2026-05-26",
    "dateModified": "2026-05-26",
    "offers": {{
      "@type": "Offer",
      "price": "14.99",
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock",
      "url": "https://builtbyjoshstudio.com/collections/{slug}-zodiac-realms.html",
      "seller": {{ "@id": "https://builtbyjoshstudio.com/#organization" }},
      "itemCondition": "https://schema.org/NewCondition"
    }},
    "hasMerchantReturnPolicy": {{
      "@type": "MerchantReturnPolicy",
      "applicableCountry": "US",
      "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted"
    }}
  }}
  </script>

  <!-- Schema.org: FAQPage -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
{faq_schema_json}
    ]
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bbj-bg: #0b0813; --bbj-surface: #120f1f; --bbj-surface-2: #171327;
      --bbj-accent: #c9a84c; --bbj-accent2: #7b4fa6;
      --bbj-text: #ede8f5; --bbj-muted: #8a7fa8; --bbj-border: #2a2040;
      --body-read: #d6cee8;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'DM Sans', sans-serif; background: var(--bbj-bg); color: var(--bbj-text); overflow-x: hidden; min-height: 100vh; }}
    .stars {{ position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }}
    .star {{ position: absolute; width: 2px; height: 2px; background: #fff; border-radius: 50%; opacity: 0; animation: twinkle var(--d) ease-in-out infinite var(--delay); }}
    @keyframes twinkle {{ 0%,100% {{ opacity: 0; transform: scale(.5); }} 50% {{ opacity: var(--op); transform: scale(1); }} }}
    .site-nav {{ position: fixed; top:0; left:0; right:0; z-index:100; display:flex; align-items:center; justify-content:space-between; padding:0 2.5rem; height:64px; background:rgba(11,8,19,.92); backdrop-filter:blur(12px); border-bottom:1px solid var(--bbj-border); }}
    .nav-logo {{ font-family:'Syne',sans-serif; font-weight:800; font-size:1.1rem; letter-spacing:-.02em; color:var(--bbj-text); text-decoration:none; }}
    .nav-links {{ display:flex; gap:2rem; list-style:none; }}
    .nav-links a {{ font-family:'DM Sans',sans-serif; font-size:.85rem; font-weight:500; letter-spacing:.06em; text-transform:uppercase; text-decoration:none; color:var(--bbj-muted); transition:color .2s; }}
    .nav-links a:hover, .nav-links a.active {{ color: var(--bbj-accent); }}

    .collection-hero {{ padding:9rem 2rem 3rem; max-width:1200px; margin:0 auto; text-align:center; position:relative; }}
    .collection-hero::before {{ content:''; position:absolute; inset:0; pointer-events:none;
      background: radial-gradient(ellipse at 50% 0%, rgba(201,168,76,.1) 0%, transparent 55%),
                  radial-gradient(ellipse at 20% 80%, rgba(123,79,166,.08) 0%, transparent 50%); }}
    .breadcrumb {{ font-family:'Cinzel',serif; font-size:.68rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-muted); margin-bottom:1.4rem; position:relative; }}
    .breadcrumb a {{ color:var(--bbj-accent); text-decoration:none; }}
    .breadcrumb a:hover {{ text-decoration:underline; }}
    .breadcrumb .sep {{ margin:0 .6rem; opacity:.5; }}
    .hero-eyebrow {{ font-family:'Cinzel',serif; font-size:.72rem; letter-spacing:.22em; text-transform:uppercase; color:var(--bbj-accent); margin-bottom:1.2rem; position:relative; }}
    h1.collection-title {{ font-family:'Cinzel',serif; font-size:clamp(2.2rem,5.5vw,3.8rem); font-weight:700; letter-spacing:.02em; line-height:1.12; color:var(--bbj-text); margin-bottom:1.4rem; max-width:900px; margin-left:auto; margin-right:auto; position:relative; }}
    .collection-tagline {{ font-family:'Crimson Pro',serif; font-size:clamp(1.05rem,1.5vw,1.18rem); color:var(--body-read); max-width:760px; margin:0 auto 2.5rem; line-height:1.65; position:relative; }}
    .hero-image {{ max-width:420px; margin:0 auto; position:relative; border:1px solid var(--bbj-border); overflow:hidden; aspect-ratio:4/5; }}
    .hero-image img {{ width:100%; height:100%; object-fit:cover; display:block; }}
    .hero-image::after {{ content:''; position:absolute; inset:0; background: radial-gradient(circle at 50% 50%, rgba(201,168,76,.08) 0%, transparent 70%); pointer-events:none; }}

    .short-version {{ max-width:1000px; margin:3rem auto 0; padding:2rem 2.4rem; background:var(--bbj-surface); border:1px solid var(--bbj-border); border-left:4px solid var(--bbj-accent); position:relative; }}
    .short-version-label {{ font-family:'Cinzel',serif; font-size:.62rem; letter-spacing:.22em; text-transform:uppercase; color:var(--bbj-accent); margin-bottom:.9rem; }}
    .short-version p {{ font-family:'Crimson Pro',serif; font-size:1.05rem; line-height:1.75; color:var(--body-read); margin:0; }}

    .collection-main {{ max-width:1200px; margin:2rem auto 0; padding:2rem 2rem 4rem; display:grid; grid-template-columns:1fr 340px; gap:3rem; align-items:start; }}
    .main-column {{ font-family:'Crimson Pro',serif; font-size:1.15rem; line-height:1.75; color:var(--body-read); min-width:0; }}
    .main-column section {{ margin-bottom:3rem; padding-top:2.5rem; border-top:1px solid var(--bbj-border); }}
    .main-column section:first-child {{ border-top:none; padding-top:0; }}
    .main-column h2 {{ font-family:'Cinzel',serif; font-size:clamp(1.4rem,2.6vw,1.85rem); font-weight:700; letter-spacing:.02em; color:var(--bbj-text); margin-bottom:1.3rem; line-height:1.2; }}
    .main-column p {{ margin-bottom:1.3rem; }}
    .main-column p strong {{ color:var(--bbj-text); font-weight:600; }}
    .main-column ul {{ list-style:none; margin:0 0 1.5rem 0; padding:0; }}
    .main-column ul li {{ position:relative; padding-left:1.6rem; margin-bottom:.8rem; }}
    .main-column ul li::before {{ content:'◆'; position:absolute; left:0; color:var(--bbj-accent); font-size:.7rem; top:.5rem; }}

    .quick-facts {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); padding:1.3rem 1.7rem; margin:0 0 2rem 0 !important; }}
    .quick-facts li {{ padding-left:0 !important; margin-bottom:.5rem !important; font-family:'DM Sans',sans-serif; font-size:.95rem; color:var(--body-read); }}
    .quick-facts li::before {{ content:'' !important; }}
    .quick-facts li strong {{ font-family:'Cinzel',serif; font-size:.78rem; letter-spacing:.1em; text-transform:uppercase; color:var(--bbj-accent); display:inline-block; min-width:170px; }}

    .realms-grouped {{ display:flex; flex-direction:column; gap:2.5rem; margin-top:1.5rem; }}
    .realm-block {{ display:flex; flex-direction:column; gap:.8rem; }}
    .realm-block-title {{ font-family:'Cinzel',serif; font-size:1.15rem; font-weight:700; color:var(--bbj-text); letter-spacing:.04em; text-transform:uppercase; padding-bottom:.6rem; border-bottom:1px solid var(--bbj-border); margin:0; }}
    .realm-block-desc {{ font-family:'Crimson Pro',serif; font-size:1rem; line-height:1.65; color:var(--body-read); margin:0 0 .5rem 0 !important; padding-left:0 !important; }}
    .realm-block-desc::before {{ content:'' !important; }}
    .designs-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; }}
    .design-card {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); overflow:hidden; display:flex; flex-direction:column; transition:border-color .25s, background .25s; }}
    .design-card:hover {{ border-color:rgba(201,168,76,.35); background:var(--bbj-surface-2); }}
    .design-card img {{ width:100%; height:auto; aspect-ratio:4/5; object-fit:cover; display:block; background: linear-gradient(135deg,#1a1230 0%,#0d0a1a 100%); border-bottom:1px solid var(--bbj-border); }}
    .design-card-body {{ padding:.9rem 1.1rem 1rem; }}
    .design-card-body h4 {{ font-family:'Cinzel',serif; font-size:.85rem; font-weight:600; color:var(--bbj-muted); letter-spacing:.08em; text-transform:uppercase; margin:0; }}

    .realm-tally {{ font-family:'Crimson Pro',serif; font-style:italic; font-size:1rem; color:var(--bbj-muted); margin-top:1.5rem; padding-top:1rem; border-top:1px solid rgba(42,32,64,.5); }}

    .license-block {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); padding:2rem 2.2rem; margin-top:2rem; }}
    .license-block h3 {{ font-family:'Cinzel',serif; font-size:1.02rem; font-weight:700; color:var(--bbj-text); letter-spacing:.05em; text-transform:uppercase; margin:1.6rem 0 .8rem 0; padding-bottom:.4rem; border-bottom:1px solid var(--bbj-border); }}
    .license-block h3:first-child {{ margin-top:0; }}
    .license-block ul {{ margin-bottom:1.4rem !important; }}
    .license-block p.disclosure {{ background:rgba(123,79,166,.07); border-left:3px solid var(--bbj-accent2); padding:1rem 1.2rem; margin-bottom:1.4rem; font-size:1rem; line-height:1.65; }}
    .license-block p.contact-line {{ margin-bottom:1.5rem; font-size:1rem; color:var(--body-read); }}
    .license-block a.pdf-link {{ display:inline-block; font-family:'Cinzel',serif; font-size:.74rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:var(--bbj-accent); text-decoration:none; padding:.6rem 1.1rem; border:1px solid var(--bbj-accent); margin:.4rem .4rem 0 0; transition:background .2s, color .2s; }}
    .license-block a.pdf-link:hover {{ background:var(--bbj-accent); color:var(--bbj-bg); }}

    .ls-checkout-btn {{ display:block; width:100%; background:var(--bbj-accent); color:var(--bbj-bg); border:none; font-family:'Cinzel',serif; font-size:.82rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; padding:1.05rem 1rem; text-align:center; cursor:pointer; transition:background .2s, transform .2s; margin-bottom:.7rem; }}
    .ls-checkout-btn:hover:not(:disabled) {{ background:#e0bd5a; transform:translateY(-1px); }}
    .ls-checkout-btn:disabled {{ background:transparent; color:var(--bbj-muted); border:1px solid var(--bbj-border); cursor:default; font-weight:600; letter-spacing:.12em; font-size:.74rem; }}
    .ls-checkout-btn--large {{ display:inline-block; width:auto; padding:1.15rem 2.5rem; font-size:.82rem; margin:0; }}
    .ls-checkout-btn--large:disabled {{ font-size:.78rem; padding:1.1rem 2.2rem; }}
    .ls-checkout-sub {{ display:block; font-size:.74rem; font-style:italic; color:var(--bbj-muted); text-align:center; margin-bottom:1.4rem; line-height:1.45; }}

    .etsy-secondary {{ margin-top:1.4rem; padding-top:1.2rem; border-top:1px solid rgba(42,32,64,.5); }}
    .etsy-secondary .etsy-secondary-label {{ font-family:'Cinzel',serif; font-size:.6rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-muted); margin-bottom:.5rem; }}
    .etsy-secondary p {{ font-family:'DM Sans',sans-serif; font-size:.78rem; color:var(--bbj-muted); line-height:1.5; margin-bottom:.5rem; }}
    .etsy-secondary a {{ color:var(--bbj-muted); text-decoration:underline; text-decoration-color:rgba(138,127,168,.4); }}
    .etsy-secondary a:hover {{ color:var(--bbj-accent); text-decoration-color:var(--bbj-accent); }}
    .etsy-secondary .etsy-pause-note {{ font-style:italic; font-size:.72rem; opacity:.75; margin-top:.4rem; margin-bottom:0; }}

    .sticky-sidebar {{ position:sticky; top:88px; background:var(--bbj-surface); border:1px solid var(--bbj-border); padding:1.8rem 1.7rem; font-family:'DM Sans',sans-serif; }}
    .sticky-sidebar::before {{ content:''; position:absolute; inset:0; pointer-events:none; background:linear-gradient(135deg,rgba(201,168,76,.05) 0%,transparent 60%); }}
    .sticky-sidebar > * {{ position:relative; }}
    .sidebar-label {{ font-family:'Cinzel',serif; font-size:.62rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-muted); margin-bottom:.4rem; }}
    .sidebar-price {{ font-family:'Cinzel',serif; font-size:2.4rem; font-weight:700; color:var(--bbj-accent); letter-spacing:-.02em; line-height:1; margin-bottom:.4rem; }}
    .sidebar-price-note {{ font-size:.78rem; color:var(--bbj-muted); letter-spacing:.02em; margin-bottom:1.4rem; padding-bottom:1.4rem; border-bottom:1px solid var(--bbj-border); }}
    .sidebar-included-label {{ font-family:'Cinzel',serif; font-size:.62rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-muted); margin-bottom:.8rem; }}
    .sidebar-included {{ list-style:none; padding:0; margin:0 0 1.5rem 0; }}
    .sidebar-included li {{ font-size:.84rem; color:var(--body-read); padding:.42rem 0 .42rem 1.3rem; position:relative; line-height:1.35; border-bottom:1px solid rgba(42,32,64,.5); }}
    .sidebar-included li:last-child {{ border-bottom:none; }}
    .sidebar-included li::before {{ content:'✓'; position:absolute; left:0; color:var(--bbj-accent); font-weight:700; font-size:.85rem; }}
    .sidebar-trust {{ list-style:none; padding:0; margin:0; }}
    .sidebar-trust li {{ font-size:.74rem; color:var(--bbj-muted); padding:.35rem 0 .35rem 1.2rem; position:relative; line-height:1.35; }}
    .sidebar-trust li::before {{ content:'✦'; position:absolute; left:0; color:var(--bbj-accent); font-size:.72rem; top:.38rem; }}

    .faq-section {{ max-width:900px; margin:0 auto; padding:5rem 2rem 4rem; }}
    .section-label {{ font-family:'Cinzel',serif; font-size:.7rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-accent); text-align:center; margin-bottom:.6rem; }}
    .section-title-main {{ font-family:'Cinzel',serif; font-size:clamp(1.8rem,3.2vw,2.4rem); font-weight:700; letter-spacing:.02em; color:var(--bbj-text); text-align:center; margin-bottom:2.8rem; }}
    .faq-list {{ display:flex; flex-direction:column; gap:0; border-top:1px solid var(--bbj-border); }}
    .faq-item {{ border-bottom:1px solid var(--bbj-border); padding:1.6rem 0; }}
    .faq-item h3 {{ font-family:'Cinzel',serif; font-size:1.05rem; font-weight:600; color:var(--bbj-text); margin-bottom:.7rem; letter-spacing:.01em; }}
    .faq-item p {{ font-family:'Crimson Pro',serif; font-size:1.05rem; line-height:1.65; color:var(--body-read); margin:0; }}

    .sister-nav-section {{ max-width:1200px; margin:0 auto; padding:3rem 2rem 2rem; }}
    .sister-intro {{ font-family:'Crimson Pro',serif; font-style:italic; font-size:1.05rem; color:var(--body-read); text-align:center; max-width:720px; margin:0 auto 2rem; }}
    .sister-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; }}
    .sister-card {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); padding:1rem 1rem; text-decoration:none; color:inherit; transition:transform .2s, border-color .2s, background .2s; display:flex; flex-direction:column; align-items:center; gap:.35rem; position:relative; }}
    .sister-card:hover {{ transform:translateY(-2px); border-color:rgba(201,168,76,.4); background:var(--bbj-surface-2); }}
    .sister-card-current {{ border-color:var(--bbj-accent); background:rgba(201,168,76,.05); cursor:default; }}
    .sister-card-current:hover {{ transform:none; }}
    .sister-glyph {{ font-size:1.5rem; color:var(--bbj-accent); line-height:1; }}
    .sister-name {{ font-family:'Cinzel',serif; font-size:.92rem; font-weight:700; letter-spacing:.03em; color:var(--bbj-text); }}
    .sister-meta {{ font-family:'DM Sans',sans-serif; font-size:.7rem; color:var(--bbj-muted); letter-spacing:.04em; text-align:center; }}
    .sister-here {{ font-family:'Cinzel',serif; font-size:.58rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-accent); margin-top:.3rem; }}

    .related-section {{ max-width:1200px; margin:0 auto; padding:3rem 2rem 5rem; }}
    .related-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:1.4rem; }}
    .related-card {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); padding:1.6rem 1.6rem 1.4rem; text-decoration:none; color:inherit; transition:transform .25s, border-color .25s, box-shadow .25s; display:flex; flex-direction:column; position:relative; overflow:hidden; }}
    .related-card::after {{ content:''; position:absolute; inset:0; pointer-events:none; background:linear-gradient(135deg, rgba(201,168,76,.04) 0%, transparent 60%); }}
    .related-card:hover {{ transform:translateY(-3px); border-color:rgba(201,168,76,.35); box-shadow:0 14px 40px rgba(201,168,76,.08); }}
    .related-card > * {{ position:relative; z-index:1; }}
    .related-meta {{ font-family:'Cinzel',serif; font-size:.62rem; letter-spacing:.15em; text-transform:uppercase; color:var(--bbj-accent); margin-bottom:.7rem; }}
    .related-card h3 {{ font-family:'Cinzel',serif; font-size:1.1rem; font-weight:700; color:var(--bbj-text); margin-bottom:.6rem; letter-spacing:.01em; line-height:1.25; }}
    .related-card p {{ font-family:'Crimson Pro',serif; font-size:.95rem; font-style:italic; color:var(--bbj-muted); line-height:1.5; margin-bottom:1rem; flex:1; }}
    .related-link {{ font-family:'Cinzel',serif; font-size:.66rem; letter-spacing:.12em; text-transform:uppercase; color:var(--bbj-accent); }}

    .cta-band {{ padding:5rem 2rem; text-align:center; background:linear-gradient(135deg,#1a1230 0%,#0d0a1a 100%); border-top:1px solid var(--bbj-border); border-bottom:1px solid var(--bbj-border); position:relative; }}
    .cta-band .cta-eyebrow {{ font-family:'Cinzel',serif; font-size:.7rem; letter-spacing:.2em; text-transform:uppercase; color:var(--bbj-accent); margin-bottom:1rem; }}
    .cta-band h2 {{ font-family:'Cinzel',serif; font-size:clamp(1.7rem,3.2vw,2.4rem); font-weight:700; color:var(--bbj-text); margin-bottom:.8rem; letter-spacing:.02em; max-width:720px; margin-left:auto; margin-right:auto; line-height:1.2; }}
    .cta-band h2 .italic-accent {{ color:var(--bbj-accent); font-style:italic; font-family:'Crimson Pro',serif; font-weight:400; }}
    .cta-band .cta-sub {{ font-family:'Crimson Pro',serif; color:var(--body-read); font-size:1.05rem; max-width:620px; margin:0 auto 2rem; line-height:1.6; }}
    .cta-band .cta-sub-line {{ display:block; font-family:'Crimson Pro',serif; font-style:italic; font-size:.9rem; color:var(--bbj-muted); margin-top:1rem; }}

    footer {{ background:#0a0a0f; padding:3rem 5rem; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1.5rem; }}
    .footer-left {{ font-family:'Syne',sans-serif; font-size:.75rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:rgba(255,255,255,.3); }}
    .footer-left strong {{ color:rgba(255,255,255,.7); }}
    .footer-links {{ display:flex; gap:1.5rem; list-style:none; }}
    .footer-links a {{ font-size:.75rem; color:rgba(255,255,255,.3); text-decoration:none; transition:color .2s; letter-spacing:.06em; text-transform:uppercase; }}
    .footer-links a:hover {{ color:rgba(255,255,255,.7); }}
    .footer-legal {{ font-family:'DM Sans',sans-serif; font-size:.7rem; color:rgba(255,255,255,.3); width:100%; text-align:center; margin-top:1rem; line-height:1.6; }}

    @media (max-width:1024px) {{
      .collection-main {{ grid-template-columns:1fr; gap:2.5rem; }}
      .sticky-sidebar {{ position:static; order:-1; max-width:500px; margin:0 auto; width:100%; }}
      .related-grid {{ grid-template-columns:repeat(2,1fr); }}
      .sister-grid {{ grid-template-columns:repeat(3,1fr); }}
    }}
    @media (max-width:720px) {{
      .collection-hero {{ padding:7rem 1.5rem 2rem; }}
      .short-version {{ padding:1.6rem 1.4rem; }}
      .collection-main {{ padding:1.5rem 1.5rem 3rem; }}
      .main-column {{ font-size:1.08rem; }}
      .faq-section {{ padding:4rem 1.5rem 3rem; }}
      .related-section {{ padding:2rem 1.5rem 4rem; }}
      .related-grid {{ grid-template-columns:1fr; }}
      .site-nav {{ padding:0 1.5rem; }}
      .nav-links {{ gap:1.2rem; }}
      .sister-grid {{ grid-template-columns:repeat(2,1fr); }}
      .designs-grid {{ grid-template-columns:1fr; }}
      footer {{ flex-direction:column; padding:2rem; text-align:center; }}
    }}
    .nav-logo {{ white-space:nowrap; }}
    .nav-logo .logo-short {{ display:none; }}
    @media (max-width:720px) {{
      .site-nav {{ padding:0 1rem; }}
      .nav-logo {{ font-size:.88rem; }}
      .nav-logo .logo-full {{ display:none; }}
      .nav-logo .logo-short {{ display:inline; }}
      .nav-links {{ gap:.9rem; }}
      .nav-links a {{ font-size:.72rem; letter-spacing:.04em; }}
    }}
    @media (max-width:420px) {{
      .nav-logo {{ font-size:.78rem; }}
      .nav-links {{ gap:.55rem; }}
      .nav-links a {{ font-size:.62rem; letter-spacing:.03em; }}
    }}
  </style>
  <link rel="stylesheet" href="/css/tokens.css" />
  <link rel="stylesheet" href="/css/mobile-nav.css" />

  <!-- Organization schema (site-wide) -->
  <script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://builtbyjoshstudio.com/#organization",
  "name": "Built by Josh Studio LLC",
  "alternateName": ["BBJ Studio", "Built By Josh Studio"],
  "legalName": "Built by Josh Studio LLC",
  "url": "https://builtbyjoshstudio.com",
  "logo": {{ "@type": "ImageObject", "url": "https://builtbyjoshstudio.com/images/logo/logo.webp", "width": 512, "height": 512 }},
  "image": "https://builtbyjoshstudio.com/images/logo/logo.webp",
  "description": "Built by Josh Studio LLC is a Kansas-based independent creative studio that publishes original zodiac digital art under the Built By Josh Studio brand and Notion OS templates and personal finance workbooks under the Tynkr Tools & Co brand. All products are digital, instant-download, and built by a single founder.",
  "founder": {{ "@type": "Person", "name": "Josh" }},
  "foundingDate": "2026-05-13",
  "foundingLocation": {{ "@type": "Place", "address": {{ "@type": "PostalAddress", "addressRegion": "KS", "addressCountry": "US" }} }},
  "address": {{ "@type": "PostalAddress", "addressRegion": "KS", "addressCountry": "US" }},
  "areaServed": "Worldwide",
  "knowsAbout": ["Zodiac digital art","Western zodiac","Chinese zodiac","Notion templates","Personal finance spreadsheets","Digital product design","Print-on-demand licensing"],
  "brand": [
    {{ "@type": "Brand", "name": "Built By Josh Studio", "description": "Original digital zodiac art bundles — Western signs, Chinese signs, zodiac landscapes, and zodiac realms — sold as print-ready, POD-licensed digital downloads." }},
    {{ "@type": "Brand", "name": "Tynkr Tools & Co", "description": "Notion OS templates and Excel and Google Sheets workbooks for creators, solopreneurs, and personal-finance milestones." }}
  ],
  "contactPoint": {{ "@type": "ContactPoint", "email": "josh@builtbyjoshstudio.com", "contactType": "customer support", "areaServed": "Worldwide", "availableLanguage": "English" }},
  "sameAs": ["https://linktr.ee/builtbyjoshstudio","https://tynkrtoolsco.substack.com/","https://www.youtube.com/@TalesofInkShadowsStudio","https://tynkrtoolsandco.etsy.com","https://www.etsy.com/shop/BuiltByJoshStudio"],
  "identifier": [{{ "@type": "PropertyValue", "propertyID": "Kansas Business ID", "value": "10076138" }}]
}}
  </script>
</head>
<body>
  <div class="stars" id="starsContainer"></div>

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

  <header class="collection-hero">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">Collections</a><span class="sep">/</span><a href="../index.html#western-realms">Western Realms</a><span class="sep">/</span><span>{sign}</span>
    </div>
    <div class="hero-eyebrow">{m['symbol']} {sign} · {m['element']} Sign · Western Realms</div>
    <h1 class="collection-title">{sign} Western Realms Bundle — 48 Print-Ready Landscape Files</h1>
    <p class="collection-tagline">{hero_tagline_for(sign)}</p>
    <div class="hero-image">
      <img src="../{hub_thumb}" alt="{sign} Western Realms preview — four landscape-style {m['element'].lower()}-realms in hybrid cosmos style, from Built By Josh Studio" />
    </div>
  </header>

  <aside class="short-version">
    <div class="short-version-label">The Short Version</div>
    <p>The {sign} Western Realms Bundle from Built By Josh Studio is a landscape-style digital art collection containing 48 print-ready image files. Each Realms bundle covers one Western zodiac sign and includes 4 unique Realm designs — atmospheric mythic environments rather than figures — with 2 numbered variants per design. Every design is delivered in three aspect ratios (1:1 square, 4:5 portrait, 2:3 portrait) at 300 DPI, in both PNG and JPG formats, with maximum dimensions of 6000 × 9000 pixels. The bundle is priced at $14.99 and includes a personal-use license plus print-on-demand rights for up to 100 physical prints per design. Files are instant-download — no physical shipping. All bundles are produced by Built by Josh Studio LLC, a Kansas limited liability company (Kansas Business ID 10076138).</p>
  </aside>

  <div class="collection-main">
    <main class="main-column">

      <section>
        <h2>The {sign} Western Realms Bundle</h2>
        <p>The {sign} Western Realms Bundle is one of 12 sign-specific Realms bundles in the Western Realms Collection. Each Realms bundle pairs a Western zodiac sign with four distinct landscape-style interpretations — environments rather than figures, atmospheres rather than portraits. The {sign} bundle contains 48 print-ready digital files: 4 original Realm designs, each in 2 numbered variants, each variant rendered in three aspect ratios and both PNG and JPG formats.</p>
        <p>Where the Western Signs Collection gives you the {m['symbol_label'].lower().replace('the ','')} in 14 art styles, the Western Realms Collection gives you the world the {m['symbol_label'].lower().replace('the ','')} inhabits. Same {sign} energy, translated into landscape — the two Collections pair naturally as a figure-and-environment wall arrangement.</p>
        <p>Built By Josh Studio is the zodiac art brand of Built by Josh Studio LLC, a Kansas-based independent creative studio. Every Realm is original work — concepted, generated, curated, and finalized by a single founder.</p>
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
        {zodiac_context}
      </section>

      <section>
        <h2>The Four {sign} Realms</h2>
        <p>The {sign} Realms bundle contains 4 unique landscape designs, each delivered in 2 numbered variants — same Realm, alternate compositions. The 4 Realm titles are:</p>
        <div class="realms-grouped">
{realm_blocks_html}
        </div>
        <p class="realm-tally">Each Realm ships with 2 numbered variants — alternate compositions of the same Realm concept. Eight total designs in the bundle. With three sizes and two formats per design, that's 48 files in total.</p>
      </section>

      <section>
        <h2>Who Buys the {sign} Realms</h2>
        <ul>
          <li>Buyers who already own the {sign} Western Signs Bundle and want the matching landscape interpretation — figure and environment as a paired wall arrangement</li>
          <li>Atmospheric decor buyers who prefer landscape art over portraiture — especially for living rooms, dining rooms, and larger spaces that benefit from depth</li>
          <li>{sign} ({m['dates']}) who want their sign represented as a place rather than a character</li>
          <li>Etsy, Printful, and Redbubble print-on-demand sellers expanding into atmospheric and landscape categories with explicit POD licensing</li>
          <li>Interior decorators building moody, atmospheric, or element-aligned rooms</li>
          <li>Collectors stacking multiple zodiac landscapes from the broader BBJ Studio catalog</li>
        </ul>
      </section>

      <section>
        <h2>What's Included With Every {sign} Realms Bundle</h2>
        <p>Every {sign} Realms Bundle is a complete digital download. After purchase, you get instant access to 48 image files organized by Realm — no shipping, no waiting, no physical product mailed to you.</p>
        <p>Each Realm design is delivered in three aspect ratios: 1:1 square (4800 × 4800 pixels), 4:5 portrait (4800 × 6000 pixels), and 2:3 portrait (6000 × 9000 pixels). Every size is provided in both PNG (lossless) and JPG (92% quality) formats. All files are saved at 300 DPI in standard sRGB color space — the industry standard for high-quality print reproduction across home printers, professional print shops, and print-on-demand services.</p>
        <p>The bundle also includes two PDF documents: a <strong>License Agreement &amp; Terms of Use</strong> covering personal use, print-on-demand rights, and the 100-print-per-design cap, and a <strong>Print Guide &amp; User Manual</strong> explaining file structure, recommended print sizes, paper selection, and troubleshooting tips. Both are tailored to the Western Realms Collection.</p>
        <p>Pricing is <strong>$14.99</strong> for the full bundle. One-time payment, instant download, secure checkout via Lemon Squeezy.</p>
      </section>

      <section>
        <h2>Licensing &amp; Print-on-Demand Rights</h2>
        <div class="license-block">
          <p>The {sign} Western Realms Bundle ships with a clear, plain-English license — not a vague "for personal use" disclaimer.</p>
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
          <a href="/legal/license-western-realms.pdf" class="pdf-link">Read the Western Realms License (PDF) →</a>
          <a href="/legal/print-guide-western-realms.pdf" class="pdf-link">Read the Western Realms Print Guide (PDF) →</a>
        </div>
      </section>

    </main>

    <aside class="sticky-sidebar">
      <div class="sidebar-label">Bundle Price</div>
      <div class="sidebar-price">$14.99</div>
      <div class="sidebar-price-note">One-time payment · Instant digital download · Secure Lemon Squeezy checkout</div>

      <div class="sidebar-included-label">What's Included</div>
      <ul class="sidebar-included">
        <li>48 print-ready digital files</li>
        <li>4 unique Realm designs × 2 variants each</li>
        <li>Three aspect ratios: 1:1, 4:5, 2:3</li>
        <li>PNG + JPG, both included</li>
        <li>Up to 6000 × 9000 pixels at 300 DPI</li>
        <li>Personal use + POD up to 100 prints per design</li>
        <li>License &amp; Print Guide PDFs included</li>
        <li>Instant download — no shipping</li>
      </ul>

      <button class="ls-checkout-btn"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{sign} Western Realms Bundle" data-product-price="14.99">{ls_btn_text}</button>
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
        <p class="etsy-pause-note">Etsy storefront currently on a brief verification pause while the IRS finalizes EIN verification — {sign} Realms Bundle purchases above are unaffected.</p>
      </div>
    </aside>
  </div>

  <section class="faq-section">
    <div class="section-label">Frequently Asked</div>
    <h2 class="section-title-main">Frequently Asked Questions</h2>
    <div class="faq-list">
{faq_items_html}
    </div>
  </section>

  <section class="sister-nav-section">
    <div class="section-label">Browse All Realms</div>
    <h2 class="section-title-main">Browse All 12 Western Realms Bundles</h2>
    <p class="sister-intro">Every Western zodiac sign has its own Realms bundle in the same structure — 48 files, 4 Realm designs, 2 variants each, $14.99 per sign. Click any sign below to see its Realms.</p>
    <div class="sister-grid">
{sister_nav}
    </div>
  </section>

  <section class="related-section">
    <div class="section-label">Explore the rest of the BBJ Studio zodiac catalog</div>
    <h2 class="section-title-main">Related Collections</h2>
    <div class="related-grid">
      <a href="{slug}-zodiac-art.html" class="related-card">
        <div class="related-meta">Western Signs · {sign}</div>
        <h3>{sign} Zodiac Art Bundle</h3>
        <p>The 14-style figure version of {sign} — 144 files, 24 designs, $24.99. Pairs with this Realms bundle as figure-and-environment.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="zodiac-landscapes.html" class="related-card">
        <div class="related-meta">Western Landscapes Collection</div>
        <h3>Zodiac Landscapes</h3>
        <p>One mythic landscape per Western zodiac sign, oil-painted. The companion full-collection bundle to the per-sign Realms.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="chinese-zodiac-realms.html" class="related-card">
        <div class="related-meta">Eastern Zodiac · Lunar Realms</div>
        <h3>Chinese Zodiac Realms</h3>
        <p>Landscape-style art for all 12 Chinese zodiac animals — 24 designs in a single bundle.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="chinese-zodiac-art.html" class="related-card">
        <div class="related-meta">Eastern Zodiac · 12 Animals</div>
        <h3>Chinese Zodiac Signs</h3>
        <p>All 12 Chinese animals in two art styles — hyper-realistic and watercolor. 8 designs per animal, 12 animal bundles.</p>
        <span class="related-link">View Collection →</span>
      </a>
    </div>
  </section>

  <section class="cta-band">
    <div class="cta-eyebrow">Browse the Collection</div>
    <h2>4 Realms. 8 Variants. <span class="italic-accent">One {sign} Bundle.</span></h2>
    <p class="cta-sub">Four mythic {sign} landscapes, each in two compositional variants, every variant in three sizes and two formats. The full landscape interpretation of {sign} — $14.99, instant download, license and print guide included.</p>
    <button class="ls-checkout-btn ls-checkout-btn--large"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{sign} Western Realms Bundle" data-product-price="14.99">{ls_btn_text}</button>
    <span class="cta-sub-line">Instant download — 48 print-ready {sign} Realm files in your inbox the moment checkout completes.</span>
  </section>

  <footer>
    <div class="footer-left"><strong>Built By Josh Studio</strong> · All digital products — instant download</div>
    <ul class="footer-links">
      <li><a href="../index.html">Home</a></li>
      <li><a href="index.html">Collections</a></li>
      <li><a href="../blog.html">Blog</a></li>
      <li><a href="../resources/">Resources</a></li>
      <li><a href="../about.html">About</a></li>
      <li><a href="/legal/">Legal</a></li>
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

  <script>
    const container = document.getElementById('starsContainer');
    for (let i = 0; i < 80; i++) {{
      const s = document.createElement('div');
      s.className = 'star';
      s.style.cssText = `left:${{Math.random()*100}}%;top:${{Math.random()*100}}%;--d:${{2+Math.random()*4}}s;--delay:-${{Math.random()*4}}s;--op:${{0.3+Math.random()*0.7}};filter:blur(${{Math.random()>0.8?'1px':'0px'}});width:${{Math.random()>0.8?3:2}}px;height:${{Math.random()>0.8?3:2}}px;`;
      container.appendChild(s);
    }}
  </script>
  <script src="/js/ls-checkout-btn.js" defer></script>
  <script src="/js/mobile-nav.js" defer></script>
  <script src="/js/ga4-events.js" defer></script>
</body>
</html>
'''


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    signs = sys.argv[1:] if len(sys.argv) > 1 else list(REALM_COPY_BY_SIGN.keys())
    for sign in signs:
        if sign not in SIGN_META:
            print(f'SKIP: unknown sign {sign}')
            continue
        if sign not in REALM_COPY_BY_SIGN:
            print(f'SKIP: {sign} (no per-Realm copy yet — add to REALM_COPY_BY_SIGN)')
            continue
        out = OUT_DIR / f'{SIGN_META[sign]["slug"]}-zodiac-realms.html'
        html = build_page(sign, manifest)
        out.write_text(html, encoding='utf-8')
        lines = html.count('\n') + 1
        size_kb = out.stat().st_size / 1024
        print(f'Wrote {out.name} ({lines} lines, {size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
