"""Build per-animal Chinese Zodiac pages — Brief Msg 5C master pattern.

Replaces the Phase 3 placeholder structure with the full master pattern:
LS-direct CTAs, License & POD Trust block, Sister-Animals nav, Related
Collections, Quick Facts (Chinese-specific), 2 style sub-sections (Chinese
Animals + Hyper Realistic Chinese), 8 FAQs, Product/FAQPage/BreadcrumbList
schemas, site-wide Organization schema.

Usage:
    python tools/build_chinese_animal_pages.py [ANIMAL ...]   # specific animals
    python tools/build_chinese_animal_pages.py                # all 12

Reads:
  images/zodiac/chinese/manifest.json (Phase 3 generated, 8 designs per
  animal across 2 styles: hyper-realistic + watercolor)

Writes:
  collections/<animal>-chinese-zodiac-art.html
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'images' / 'zodiac' / 'chinese' / 'manifest.json'
OUT_DIR = ROOT / 'collections'

ALL_ANIMALS_ORDER = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig']

# Per-animal metadata. Years = 4 most recent (12-year cycle). Trine = the
# three-animal compatibility group this animal belongs to (includes self).
ANIMAL_META = {
    'Rat':     dict(slug='rat',     element='Water', yin_yang='Yang', order='1st',  sku='BBJ-CS-RAT',     years='2020, 2008, 1996, 1984', trine='Rat, Dragon, Monkey',   glyph='🐀'),
    'Ox':      dict(slug='ox',      element='Earth', yin_yang='Yin',  order='2nd',  sku='BBJ-CS-OX',      years='2021, 2009, 1997, 1985', trine='Ox, Snake, Rooster',    glyph='🐂'),
    'Tiger':   dict(slug='tiger',   element='Wood',  yin_yang='Yang', order='3rd',  sku='BBJ-CS-TIGER',   years='2022, 2010, 1998, 1986', trine='Tiger, Horse, Dog',     glyph='🐅'),
    'Rabbit':  dict(slug='rabbit',  element='Wood',  yin_yang='Yin',  order='4th',  sku='BBJ-CS-RABBIT',  years='2023, 2011, 1999, 1987', trine='Rabbit, Goat, Pig',     glyph='🐇'),
    'Dragon':  dict(slug='dragon',  element='Earth', yin_yang='Yang', order='5th',  sku='BBJ-CS-DRAGON',  years='2024, 2012, 2000, 1988', trine='Rat, Dragon, Monkey',   glyph='🐉'),
    'Snake':   dict(slug='snake',   element='Fire',  yin_yang='Yin',  order='6th',  sku='BBJ-CS-SNAKE',   years='2025, 2013, 2001, 1989', trine='Ox, Snake, Rooster',    glyph='🐍'),
    'Horse':   dict(slug='horse',   element='Fire',  yin_yang='Yang', order='7th',  sku='BBJ-CS-HORSE',   years='2026, 2014, 2002, 1990', trine='Tiger, Horse, Dog',     glyph='🐎'),
    'Goat':    dict(slug='goat',    element='Earth', yin_yang='Yin',  order='8th',  sku='BBJ-CS-GOAT',    years='2027, 2015, 2003, 1991', trine='Rabbit, Goat, Pig',     glyph='🐐'),
    'Monkey':  dict(slug='monkey',  element='Metal', yin_yang='Yang', order='9th',  sku='BBJ-CS-MONKEY',  years='2028, 2016, 2004, 1992', trine='Rat, Dragon, Monkey',   glyph='🐒'),
    'Rooster': dict(slug='rooster', element='Metal', yin_yang='Yin',  order='10th', sku='BBJ-CS-ROOSTER', years='2029, 2017, 2005, 1993', trine='Ox, Snake, Rooster',    glyph='🐓'),
    'Dog':     dict(slug='dog',     element='Earth', yin_yang='Yang', order='11th', sku='BBJ-CS-DOG',     years='2030, 2018, 2006, 1994', trine='Tiger, Horse, Dog',     glyph='🐕'),
    'Pig':     dict(slug='pig',     element='Water', yin_yang='Yin',  order='12th', sku='BBJ-CS-PIG',     years='2031, 2019, 2007, 1995', trine='Rabbit, Goat, Pig',     glyph='🐖'),
}

# Two styles. Brief 5C.3 order: Chinese Animals (traditional) first, then
# Hyper Realistic Chinese (photoreal). Manifest slugs are 'watercolor' and
# 'hyper-realistic' — the display labels per brief.
STYLE_ORDER = [
    ('watercolor',     'Chinese Animals',         'Traditional, culturally rooted depictions of the {animal} with classical Chinese aesthetic — flowing line work, traditional palette inspirations, symbolic iconography. Designed to honor the cultural origins of the Chinese zodiac while still feeling original and wall-worthy. 4 numbered variants in this series.'),
    ('hyper-realistic','Hyper Realistic Chinese', 'Photorealistic portraiture of the {animal} with cinematic lighting and material detail — fur, scale, feather, gleam — rendered with hero-pose presence and gallery-quality realism. The Hyper Realistic counterpart to the more traditional Chinese Animals series. 4 numbered variants in this series.'),
]


# Per-animal cultural context paragraph. Brief 5C.3 — keep factual and
# respectful, no horoscope tropes. The Dragon entry is the brief's example
# verbatim; the others follow the same pattern.
WHAT_MAKES_ANIMAL_PROSE = {
    'Rat':     "The Rat is the 1st animal in the Chinese zodiac cycle — the sign that begins the twelve. Associated with the Water element and Yang energy, the Rat represents intelligence, adaptability, and resourcefulness in Chinese tradition. Rat years run on a 12-year cycle — 2020, 2008, 1996, 1984, and so on. The Rat's compatible trine includes the Dragon and Monkey.",
    'Ox':      "The Ox is the 2nd animal in the Chinese zodiac cycle. Associated with the Earth element and Yin energy, the Ox represents diligence, dependability, and steady strength in Chinese tradition. Ox years run on a 12-year cycle — 2021, 2009, 1997, 1985, and so on. The Ox's compatible trine includes the Snake and Rooster.",
    'Tiger':   "The Tiger is the 3rd animal in the Chinese zodiac cycle. Associated with the Wood element and Yang energy, the Tiger represents courage, confidence, and a fierce competitive spirit in Chinese tradition. Tiger years run on a 12-year cycle — 2022, 2010, 1998, 1986, and so on. The Tiger's compatible trine includes the Horse and Dog.",
    'Rabbit':  "The Rabbit is the 4th animal in the Chinese zodiac cycle. Associated with the Wood element and Yin energy, the Rabbit represents gentleness, elegance, and quiet perceptiveness in Chinese tradition. Rabbit years run on a 12-year cycle — 2023, 2011, 1999, 1987, and so on. The Rabbit's compatible trine includes the Goat and Pig.",
    'Dragon':  "The Dragon is the 5th animal in the Chinese zodiac cycle and the only mythological creature among the twelve. Associated with the Earth element and Yang energy, the Dragon represents power, ambition, and good fortune in Chinese tradition. Dragon years run on a 12-year cycle — 2024, 2012, 2000, 1988, and so on. The Dragon's compatible trine includes the Rat and Monkey.",
    'Snake':   "The Snake is the 6th animal in the Chinese zodiac cycle. Associated with the Fire element and Yin energy, the Snake represents wisdom, intuition, and quiet intelligence in Chinese tradition. Snake years run on a 12-year cycle — 2025, 2013, 2001, 1989, and so on. The Snake's compatible trine includes the Ox and Rooster.",
    'Horse':   "The Horse is the 7th animal in the Chinese zodiac cycle. Associated with the Fire element and Yang energy, the Horse represents freedom, energy, and forward motion in Chinese tradition. Horse years run on a 12-year cycle — 2026, 2014, 2002, 1990, and so on. The Horse's compatible trine includes the Tiger and Dog.",
    'Goat':    "The Goat is the 8th animal in the Chinese zodiac cycle (sometimes called the Sheep or Ram). Associated with the Earth element and Yin energy, the Goat represents creativity, gentleness, and aesthetic sensibility in Chinese tradition. Goat years run on a 12-year cycle — 2027, 2015, 2003, 1991, and so on. The Goat's compatible trine includes the Rabbit and Pig.",
    'Monkey':  "The Monkey is the 9th animal in the Chinese zodiac cycle. Associated with the Metal element and Yang energy, the Monkey represents cleverness, invention, and quick-witted curiosity in Chinese tradition. Monkey years run on a 12-year cycle — 2028, 2016, 2004, 1992, and so on. The Monkey's compatible trine includes the Rat and Dragon.",
    'Rooster': "The Rooster is the 10th animal in the Chinese zodiac cycle. Associated with the Metal element and Yin energy, the Rooster represents honesty, confidence, and disciplined attention to detail in Chinese tradition. Rooster years run on a 12-year cycle — 2029, 2017, 2005, 1993, and so on. The Rooster's compatible trine includes the Ox and Snake.",
    'Dog':     "The Dog is the 11th animal in the Chinese zodiac cycle. Associated with the Earth element and Yang energy, the Dog represents loyalty, honesty, and protective sincerity in Chinese tradition. Dog years run on a 12-year cycle — 2030, 2018, 2006, 1994, and so on. The Dog's compatible trine includes the Tiger and Horse.",
    'Pig':     "The Pig is the 12th and final animal in the Chinese zodiac cycle. Associated with the Water element and Yin energy, the Pig represents generosity, warmth, and big-hearted abundance in Chinese tradition. Pig years run on a 12-year cycle — 2031, 2019, 2007, 1995, and so on. The Pig's compatible trine includes the Rabbit and Goat.",
}


# Per-animal hero tagline (under H1). Brief 5C.4 — animal's signature
# qualities + bundle composition. All tail with bundle facts.
HERO_TAGLINE_BY_ANIMAL = {
    'Rat':     "8 original Rat Chinese zodiac designs — clever, quick, adaptable. Four traditional Chinese Animals interpretations of the Rat alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Ox':      "8 original Ox Chinese zodiac designs — diligent, steady, immovably strong. Four traditional Chinese Animals interpretations of the Ox alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Tiger':   "8 original Tiger Chinese zodiac designs — fierce, magnetic, unmistakably present. Four traditional Chinese Animals interpretations of the Tiger alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Rabbit':  "8 original Rabbit Chinese zodiac designs — gentle, elegant, quietly watchful. Four traditional Chinese Animals interpretations of the Rabbit alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Dragon':  "8 original Dragon Chinese zodiac designs — powerful, ambitious, mythologically scaled. Four traditional Chinese Animals interpretations of the Dragon alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Snake':   "8 original Snake Chinese zodiac designs — wise, intuitive, hypnotically still. Four traditional Chinese Animals interpretations of the Snake alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Horse':   "8 original Horse Chinese zodiac designs — free-running, energetic, unbridled. Four traditional Chinese Animals interpretations of the Horse alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Goat':    "8 original Goat Chinese zodiac designs — creative, contemplative, drawn to beauty. Four traditional Chinese Animals interpretations of the Goat alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Monkey':  "8 original Monkey Chinese zodiac designs — clever, playful, endlessly inventive. Four traditional Chinese Animals interpretations of the Monkey alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Rooster': "8 original Rooster Chinese zodiac designs — honest, vigilant, fiercely punctual. Four traditional Chinese Animals interpretations of the Rooster alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Dog':     "8 original Dog Chinese zodiac designs — loyal, honest, protectively present. Four traditional Chinese Animals interpretations of the Dog alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
    'Pig':     "8 original Pig Chinese zodiac designs — generous, warm, abundantly present. Four traditional Chinese Animals interpretations of the Pig alongside four cinematic Hyper Realistic Chinese portraits, each in three print-ready sizes and both PNG and JPG, totaling 48 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.",
}


def hero_tagline_for(animal):
    return HERO_TAGLINE_BY_ANIMAL.get(animal, HERO_TAGLINE_BY_ANIMAL['Rat'])


def cultural_prose_for(animal):
    return WHAT_MAKES_ANIMAL_PROSE.get(animal, '')


# Lemon Squeezy buy URLs per animal. Empty string => button stays disabled
# with "Coming Soon" copy. Populated URL => button is live, "$14.99" appears
# in the button text, and js/ls-checkout-btn.js opens the LS overlay on click.
LS_URL_BY_ANIMAL = {
    'Rat':     'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/020469d4-d057-40c6-bcc2-63e4acdf1931?embed=1',
    'Ox':      'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/ad1241ae-d3a9-41e4-8609-b1da8a3b48f4?embed=1',
    'Tiger':   'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/e31b21dc-5272-483e-ba4e-f3143a116811?embed=1',
    'Rabbit':  'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/62e87b83-136c-4175-be85-70c74dcd368c?embed=1',
    'Dragon':  'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/c0c0d586-f817-4430-b2d8-12b276ce4f19?embed=1',
    'Snake':   'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/197182f1-a465-4327-b8f7-5c8ef190f6d6?embed=1',
    'Horse':   'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/81119fed-d52e-43c0-876c-60d4e27f1a17?embed=1',
    'Goat':    'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/7100e32d-32e3-417b-adbb-711a6d02ca16?embed=1',
    'Monkey':  'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/e0f0b887-68f1-43ca-aaf7-43754e6b9f04?embed=1',
    'Rooster': 'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/8177ada7-5f23-4555-a01a-92cb70bff51f?embed=1',
    'Dog':     'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/b13065dc-7d5e-4eea-9c36-a593678ba6aa?embed=1',
    'Pig':     'https://builtbyjoshstudio.lemonsqueezy.com/checkout/buy/59dfe109-d522-48c5-baf1-90f0281117ae?embed=1',
}


def ls_button_state(animal, price='14.99'):
    """Return (disabled_attr, ls_url, button_text) for the LS button on an
    animal's page. Standing Instruction #6 — when URL is present, button is
    live with "$<price>" in the copy; when URL is empty, button stays disabled
    with "Coming Soon"."""
    url = LS_URL_BY_ANIMAL.get(animal, '')
    if url:
        return ('', url, f'Buy the {animal} Bundle — ${price}')
    return (' disabled', '', f'Buy the {animal} Bundle — Coming Soon')


def build_style_block(style_slug, display_name, designs, animal, description):
    """Render a single style sub-section: title + description + 4 variant cards."""
    cards = []
    for d in sorted(designs, key=lambda x: int(x['variant'])):
        cards.append(
            '            <div class="design-card">\n'
            f'              <img src="../{d["webp_path"]}" alt="{display_name} variant {d["variant"]} — {animal} Chinese zodiac art print" loading="lazy" width="720" height="900">\n'
            '              <div class="design-card-body">\n'
            f'                <h4>Variant {d["variant"]}</h4>\n'
            '              </div>\n'
            '            </div>'
        )
    desc = description.format(animal=animal)
    return (
        '        <div class="style-block">\n'
        f'          <h3 class="style-block-title">{display_name}</h3>\n'
        f'          <p class="style-block-desc">{desc}</p>\n'
        '          <div class="designs-grid">\n\n' + '\n\n'.join(cards) + '\n\n'
        '          </div>\n'
        '        </div>'
    )


def build_sister_nav(current_animal):
    cards = []
    for a in ALL_ANIMALS_ORDER:
        m = ANIMAL_META[a]
        is_current = (a == current_animal)
        # First year of the 4 most recent — short year tag
        year_short = m['years'].split(',')[0].strip()
        if is_current:
            inner = f'<div class="sister-card sister-card-current"><span class="sister-glyph">{m["glyph"]}</span><span class="sister-name">{a}</span><span class="sister-meta">{m["element"]} · {year_short}</span><span class="sister-here">You are here</span></div>'
        else:
            href = f'{m["slug"]}-chinese-zodiac-art.html'
            inner = f'<a href="{href}" class="sister-card"><span class="sister-glyph">{m["glyph"]}</span><span class="sister-name">{a}</span><span class="sister-meta">{m["element"]} · {year_short}</span></a>'
        cards.append(f'        {inner}')
    return '\n'.join(cards)


def faq_data(animal):
    return [
        (f'What is included in the {animal} Chinese Zodiac Art Bundle?',
         f'The {animal} bundle includes 48 print-ready digital files covering 8 original {animal} designs across 2 art-style series — Chinese Animals (traditional cultural style) and Hyper Realistic Chinese (cinematic photoreal style) — with 4 numbered variants per series. Every design ships in three aspect ratios (1:1, 4:5, 2:3) and both PNG and JPG formats, at 300 DPI. The bundle also includes a License Agreement and a Print Guide as PDFs.'),
        (f'How much does the {animal} Chinese Zodiac Art Bundle cost?',
         f'The {animal} bundle is priced at $14.99 — one-time payment, instant digital download. That works out to roughly $1.87 per individual design.'),
        (f'Can I use the {animal} Bundle for print-on-demand or commercial sales?',
         'Yes. The license includes print-on-demand rights for up to 100 physical units per individual design, cumulative across all formats, vendors, and time periods combined. You can sell framed prints, posters, canvases, mugs, t-shirts, and similar physical products made from the designs within that cap. For more than 100 prints of any single design, contact Built by Josh Studio LLC about extended commercial licensing.'),
        (f'What sizes can I print the {animal} art at?',
         'The largest file (6000 × 9000 pixels) prints crisply up to 20" × 30" at full 300 DPI. With a print provider running 150 DPI for large-format jobs, prints up to roughly 40" × 60" still look excellent. The bundle also includes 1:1 files (4800 × 4800) for square framing and 4:5 files (4800 × 6000) for standard portrait sizes like 8×10 and 16×20.'),
        (f'How were the {animal} designs created?',
         f"The {animal} designs were created by Built by Josh Studio LLC using a combination of human creative direction and AI image generation tools, including Leonardo.ai. Every design is selected, curated, refined, and finalized by the studio's founder. This is disclosed in full in the license agreement included with every bundle."),
        ('What formats and color profiles do the files use?',
         'All files are delivered in both PNG (lossless) and JPG (92% quality compression) formats. Color profile is sRGB — the standard for virtually every print-on-demand service and consumer printer, requiring no color conversion before printing.'),
        (f'Where can I buy the {animal} Chinese Zodiac Art Bundle?',
         f'The {animal} bundle is sold directly on builtbyjoshstudio.com via secure Lemon Squeezy checkout. Click the "Buy the {animal} Bundle" button on this page to open the checkout overlay, complete the purchase, and receive instant access to the full bundle — no Etsy account required, no marketplace fees, files delivered immediately to your email. The Built by Josh Studio Etsy storefront carries other studio work but does not sell the full Collection bundles.'),
        ('Do you have art for the other Chinese zodiac animals and the Western zodiac?',
         'Yes. Built by Josh Studio publishes 12 sign-specific bundles for all Chinese zodiac animals (Rat through Pig, identical structure to this bundle), a single Chinese Realms Collection covering all 12 animals in landscape style, 12 sign-specific Western Signs bundles in 14 art styles each, 12 sign-specific Western Realms landscape bundles, and a full 12-landscape Western Landscapes Collection.'),
    ]


def faq_schema_data(animal):
    """ASCII-safe variants for JSON. Replace inch marks and curly quotes."""
    out = []
    for q, a in faq_data(animal):
        a_schema = (
            a
            .replace('20" × 30"', '20 by 30 inches')
            .replace('40" × 60"', '40 by 60 inches')
            .replace('8×10', '8x10')
            .replace('16×20', '16x20')
            .replace('×', 'x')
            .replace(f'"Buy the {animal} Bundle"', f'Buy the {animal} Bundle')
        )
        out.append({'q': q, 'a': a_schema})
    return out


def build_page(animal, manifest):
    m = ANIMAL_META[animal]
    slug = m['slug']
    animal_data = manifest[animal]
    designs = animal_data['designs']
    hub_thumb = animal_data['hub_thumb']

    # Group designs by style
    by_style = {}
    for d in designs:
        by_style.setdefault(d['style'], []).append(d)
    style_blocks_html = '\n\n'.join(
        build_style_block(slug_key, label, by_style[slug_key], animal, desc)
        for slug_key, label, desc in STYLE_ORDER
        if slug_key in by_style
    )

    sister_nav = build_sister_nav(animal)

    ls_disabled_attr, ls_url, ls_btn_text = ls_button_state(animal)

    # FAQ visible + schema
    faqs = faq_data(animal)
    faq_items_html = '\n'.join(
        '      <div class="faq-item">\n'
        f'        <h3>{q}</h3>\n'
        f'        <p>{a}</p>\n'
        '      </div>'
        for q, a in faqs
    )
    faq_schema = faq_schema_data(animal)
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

    cultural_prose = cultural_prose_for(animal)
    tagline = hero_tagline_for(animal)

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
  <title>{animal} Chinese Zodiac Art Bundle — 48 Print-Ready Files | BBJ Studio</title>
  <meta name="description" content="The {animal} Chinese zodiac art bundle from Built by Josh Studio — 48 print-ready digital files across 2 art styles (Chinese Animals + Hyper Realistic Chinese) and 8 original designs. Personal use + print-on-demand licensed up to 100 prints per design. Instant download from $14.99." />
  <link rel="canonical" href="https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" />

  <meta property="og:title" content="{animal} Chinese Zodiac Art Bundle — 48 Print-Ready Files | BBJ Studio" />
  <meta property="og:description" content="48 print-ready digital files covering 8 original {animal} designs across 2 art styles. Personal use + POD up to 100 prints per design." />
  <meta property="og:type" content="product" />
  <meta property="og:url" content="https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" />
  <meta property="og:site_name" content="Built by Josh Studio" />
  <meta property="og:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{animal} Chinese Zodiac Art Bundle — 48 Print-Ready Files | BBJ Studio" />
  <meta name="twitter:description" content="48 print-ready digital files covering 8 original {animal} designs across 2 art styles." />
  <meta name="twitter:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />

  <!-- Schema.org: BreadcrumbList (4-level: Home > Collections > Chinese Signs > Animal) -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://builtbyjoshstudio.com/" }},
      {{ "@type": "ListItem", "position": 2, "name": "Collections", "item": "https://builtbyjoshstudio.com/collections/" }},
      {{ "@type": "ListItem", "position": 3, "name": "Chinese Signs", "item": "https://builtbyjoshstudio.com/collections/chinese-zodiac-art.html" }},
      {{ "@type": "ListItem", "position": 4, "name": "{animal} Chinese Zodiac Art Bundle", "item": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" }}
    ]
  }}
  </script>

  <!-- Schema.org: Product -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Product",
    "@id": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html#product",
    "name": "{animal} Chinese Zodiac Art Bundle — 48 Print-Ready Files",
    "description": "The {animal} Chinese Zodiac Art Bundle contains 48 print-ready digital files covering 8 original {animal} designs across 2 art-style series — Chinese Animals (traditional cultural style) and Hyper Realistic Chinese (cinematic photoreal style) — with 4 numbered variants per series. Every design ships in three aspect ratios (1:1, 4:5, 2:3) at 300 DPI in both PNG and JPG. Licensed for personal use and print-on-demand up to 100 prints per design.",
    "image": [
      "https://builtbyjoshstudio.com/{hub_thumb}"
    ],
    "url": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html",
    "sku": "{m['sku']}",
    "category": "Digital Art / Zodiac Art / Chinese Signs",
    "brand": {{ "@type": "Brand", "name": "Built by Josh Studio" }},
    "manufacturer": {{ "@id": "https://builtbyjoshstudio.com/#organization" }},
    "additionalProperty": [
      {{"@type": "PropertyValue", "name": "File Count", "value": "48"}},
      {{"@type": "PropertyValue", "name": "Designs", "value": "8"}},
      {{"@type": "PropertyValue", "name": "Art Styles", "value": "2"}},
      {{"@type": "PropertyValue", "name": "Variants per Style", "value": "4"}},
      {{"@type": "PropertyValue", "name": "Resolution", "value": "300 DPI"}},
      {{"@type": "PropertyValue", "name": "Maximum Dimensions", "value": "6000 x 9000 pixels"}},
      {{"@type": "PropertyValue", "name": "Aspect Ratios", "value": "1:1, 4:5, 2:3"}},
      {{"@type": "PropertyValue", "name": "File Formats", "value": "PNG, JPG"}},
      {{"@type": "PropertyValue", "name": "Color Profile", "value": "sRGB"}},
      {{"@type": "PropertyValue", "name": "License", "value": "Personal use + POD up to 100 prints per design"}},
      {{"@type": "PropertyValue", "name": "Zodiac Animal", "value": "{animal}"}},
      {{"@type": "PropertyValue", "name": "Element", "value": "{m['element']}"}},
      {{"@type": "PropertyValue", "name": "Yin/Yang", "value": "{m['yin_yang']}"}},
      {{"@type": "PropertyValue", "name": "Order in Zodiac", "value": "{m['order']}"}},
      {{"@type": "PropertyValue", "name": "Recent Years", "value": "{m['years']}"}}
    ],
    "datePublished": "2026-05-26",
    "dateModified": "2026-05-26",
    "offers": {{
      "@type": "Offer",
      "price": "14.99",
      "priceCurrency": "USD",
      "availability": "https://schema.org/InStock",
      "url": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html",
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

  <!-- Schema.org: FAQPage (mirrors visible FAQ) -->
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

    .styles-grouped {{ display:flex; flex-direction:column; gap:2.5rem; margin-top:1.5rem; }}
    .style-block {{ display:flex; flex-direction:column; gap:.8rem; }}
    .style-block-title {{ font-family:'Cinzel',serif; font-size:1.15rem; font-weight:700; color:var(--bbj-text); letter-spacing:.04em; text-transform:uppercase; padding-bottom:.6rem; border-bottom:1px solid var(--bbj-border); margin:0; }}
    .style-block-desc {{ font-family:'Crimson Pro',serif; font-size:1rem; line-height:1.65; color:var(--body-read); margin:0 0 .5rem 0 !important; padding-left:0 !important; }}
    .style-block-desc::before {{ content:'' !important; }}
    .designs-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:1rem; }}
    .design-card {{ background:var(--bbj-surface); border:1px solid var(--bbj-border); overflow:hidden; display:flex; flex-direction:column; transition:border-color .25s, background .25s; }}
    .design-card:hover {{ border-color:rgba(201,168,76,.35); background:var(--bbj-surface-2); }}
    .design-card img {{ width:100%; height:auto; aspect-ratio:4/5; object-fit:cover; display:block; background: linear-gradient(135deg,#1a1230 0%,#0d0a1a 100%); border-bottom:1px solid var(--bbj-border); }}
    .design-card-body {{ padding:.9rem 1.1rem 1rem; }}
    .design-card-body h4 {{ font-family:'Cinzel',serif; font-size:.85rem; font-weight:600; color:var(--bbj-muted); letter-spacing:.08em; text-transform:uppercase; margin:0; }}

    .style-tally {{ font-family:'Crimson Pro',serif; font-style:italic; font-size:1rem; color:var(--bbj-muted); margin-top:1.5rem; padding-top:1rem; border-top:1px solid rgba(42,32,64,.5); }}

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
    .sister-glyph {{ font-size:1.5rem; line-height:1; }}
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
  "alternateName": ["BBJ Studio", "Built by Josh Studio"],
  "legalName": "Built by Josh Studio LLC",
  "url": "https://builtbyjoshstudio.com",
  "logo": {{ "@type": "ImageObject", "url": "https://builtbyjoshstudio.com/images/logo/logo.webp", "width": 512, "height": 512 }},
  "image": "https://builtbyjoshstudio.com/images/logo/logo.webp",
  "description": "Built by Josh Studio LLC is a Kansas-based independent creative studio that publishes original zodiac digital art under its own name and Notion OS templates and personal finance workbooks under the Tynkr Tools & Co brand. All products are digital, instant-download, and built by a single founder.",
  "founder": {{ "@type": "Person", "name": "Josh" }},
  "foundingDate": "2026-05-13",
  "foundingLocation": {{ "@type": "Place", "address": {{ "@type": "PostalAddress", "addressRegion": "KS", "addressCountry": "US" }} }},
  "address": {{ "@type": "PostalAddress", "addressRegion": "KS", "addressCountry": "US" }},
  "areaServed": "Worldwide",
  "knowsAbout": ["Zodiac digital art","Western zodiac","Chinese zodiac","Notion templates","Personal finance spreadsheets","Digital product design","Print-on-demand licensing"],
  "brand": [
    {{ "@type": "Brand", "name": "Built by Josh Studio", "description": "Original digital zodiac art bundles — Western signs, Chinese signs, zodiac landscapes, and zodiac realms — sold as print-ready, POD-licensed digital downloads." }},
    {{ "@type": "Brand", "name": "Tynkr Tools & Co", "description": "Notion OS templates and Excel and Google Sheets workbooks for creators, solopreneurs, and personal-finance milestones." }}
  ],
  "contactPoint": {{ "@type": "ContactPoint", "email": "josh@builtbyjoshstudio.com", "contactType": "customer support", "areaServed": "Worldwide", "availableLanguage": "English" }},
  "sameAs": ["https://linktr.ee/builtbyjoshstudio","https://tynkrtoolsco.substack.com/","https://www.youtube.com/@TalesofInkShadowsStudio","https://www.youtube.com/@joshandjordanskitchen","https://tynkrtoolsandco.etsy.com","https://www.etsy.com/shop/BuiltByJoshStudio"],
  "identifier": [{{ "@type": "PropertyValue", "propertyID": "Kansas Business ID", "value": "10076138" }}]
}}
  </script>
</head>
<body>
  <div class="stars" id="starsContainer"></div>

  <nav class="site-nav">
    <a href="../index.html" class="nav-logo"><span class="logo-full">Built by Josh Studio</span><span class="logo-short">BBJ Studio</span></a>
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
      <a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">Collections</a><span class="sep">/</span><a href="chinese-zodiac-art.html">Chinese Signs</a><span class="sep">/</span><span>{animal}</span>
    </div>
    <div class="hero-eyebrow">{m['glyph']} {animal} · Chinese Zodiac · {m['element']} Element · Years: {m['years']}</div>
    <h1 class="collection-title">{animal} Chinese Zodiac Art Bundle — 48 Print-Ready Files</h1>
    <p class="collection-tagline">{tagline}</p>
    <div class="hero-image">
      <img src="../{hub_thumb}" alt="{animal} Chinese zodiac art bundle preview — 2 art styles (Chinese Animals + Hyper Realistic Chinese) and 8 original designs, from Built by Josh Studio" />
    </div>
  </header>

  <aside class="short-version">
    <div class="short-version-label">The Short Version</div>
    <p>The {animal} Chinese Zodiac Art Bundle from Built by Josh Studio is a digital art collection containing 48 print-ready image files. Each bundle covers one Chinese zodiac animal and includes 8 original designs across 2 art-style series — Chinese Animals (traditional cultural style) and Hyper Realistic Chinese (cinematic photoreal style) — with 4 numbered variants per series. Every design is delivered in three aspect ratios (1:1 square, 4:5 portrait, 2:3 portrait) at 300 DPI, in both PNG and JPG formats, with maximum dimensions of 6000 × 9000 pixels. The bundle is priced at $14.99 and includes a personal-use license plus print-on-demand rights for up to 100 physical prints per design. Files are instant-download — no physical shipping. All bundles are produced by Built by Josh Studio LLC, a Kansas limited liability company (Kansas Business ID 10076138).</p>
  </aside>

  <div class="collection-main">
    <main class="main-column">

      <section>
        <h2>The {animal} Chinese Zodiac Art Bundle</h2>
        <p>The {animal} Chinese Zodiac Art Bundle is one of 12 animal-specific bundles in the Chinese Signs Collection. Each bundle pairs a Chinese zodiac animal with two complementary art-style interpretations — a traditional cultural reading and a cinematic photoreal one. The {animal} bundle contains 48 print-ready digital files: 8 original designs (4 per style), each rendered in three aspect ratios and both PNG and JPG formats.</p>
        <p>The two styles are designed to pair on a wall or to stand alone. The Chinese Animals series leans on classical visual language; the Hyper Realistic Chinese series leans on cinematic portraiture. Buyers don't pick one — the bundle includes both.</p>
        <p>Built by Josh Studio LLC, a Kansas-based independent creative studio, publishes this zodiac art under its own name. Every design is original work — concepted, generated, curated, and finalized by a single founder.</p>
      </section>

      <section>
        <h2>What Makes the {animal}, the {animal}</h2>
        <ul class="quick-facts">
          <li><strong>Element:</strong> {m['element']}</li>
          <li><strong>Yin/Yang:</strong> {m['yin_yang']}</li>
          <li><strong>Order in Zodiac:</strong> {m['order']}</li>
          <li><strong>Years (most recent):</strong> {m['years']}</li>
          <li><strong>Compatible Trine:</strong> {m['trine']}</li>
        </ul>
        <p>{cultural_prose}</p>
      </section>

      <section>
        <h2>The Two Art Styles in the {animal} Bundle</h2>
        <p>The {animal} bundle contains 8 unique designs across 2 art-style series. Same animal, two complementary visual readings.</p>
        <div class="styles-grouped">
{style_blocks_html}
        </div>
        <p class="style-tally">Across the two styles, the bundle contains 8 unique designs of the {animal}. With three sizes (1:1, 4:5, 2:3) and two formats (PNG, JPG) per design, that's 48 files in total.</p>
      </section>

      <section>
        <h2>Who Buys the {animal} Bundle</h2>
        <ul>
          <li>People born in a Year of the {animal} ({m['years']}, and every 12 years before and after) who want their zodiac animal as wall art</li>
          <li>Buyers shopping for someone born in a Year of the {animal} — birthday, housewarming, or culturally meaningful gift</li>
          <li>Etsy, Printful, and Redbubble print-on-demand sellers expanding into Chinese zodiac inventory with explicit POD licensing</li>
          <li>Buyers building a multi-animal Chinese zodiac wall arrangement — pair {animal} with the other 11 animals as a complete set</li>
          <li>Interior decorators working in Lunar New Year contexts or culturally themed spaces</li>
          <li>Collectors who already own the {m['trine']} trine and want to complete it</li>
        </ul>
      </section>

      <section>
        <h2>What's Included With Every {animal} Bundle</h2>
        <p>Every {animal} Chinese Zodiac Art Bundle is a complete digital download. After purchase, you get instant access to 48 image files organized into 2 art-style subfolders — no shipping, no waiting, no physical product mailed to you.</p>
        <p>Each design is delivered in three aspect ratios: 1:1 square (4800 × 4800 pixels), 4:5 portrait (4800 × 6000 pixels), and 2:3 portrait (6000 × 9000 pixels). Every size is provided in both PNG (lossless) and JPG (92% quality) formats. All files are saved at 300 DPI in standard sRGB color space — the industry standard for high-quality print reproduction across home printers, professional print shops, and print-on-demand services.</p>
        <p>The bundle also includes two PDF documents: a <strong>License Agreement &amp; Terms of Use</strong> covering personal use, print-on-demand rights, and the 100-print-per-design cap, and a <strong>Print Guide &amp; User Manual</strong> explaining file structure, recommended print sizes, paper selection, and troubleshooting tips. Both are tailored to the Chinese Signs Collection.</p>
        <p>Pricing is <strong>$14.99</strong> for the full bundle. One-time payment, instant download, secure checkout via Lemon Squeezy.</p>
      </section>

      <section>
        <h2>Licensing &amp; Print-on-Demand Rights</h2>
        <div class="license-block">
          <p>The {animal} Chinese Zodiac Art Bundle ships with a clear, plain-English license — not a vague "for personal use" disclaimer.</p>
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
          <a href="/legal/license-chinese-signs.pdf" class="pdf-link">Read the Chinese Signs License (PDF) →</a>
          <a href="/legal/print-guide-chinese-signs.pdf" class="pdf-link">Read the Chinese Signs Print Guide (PDF) →</a>
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
        <li>8 original {animal} designs across 2 styles</li>
        <li>4 variants per style</li>
        <li>Three aspect ratios: 1:1, 4:5, 2:3</li>
        <li>PNG + JPG, both included</li>
        <li>Up to 6000 × 9000 pixels at 300 DPI</li>
        <li>Personal use + POD up to 100 prints per design</li>
        <li>License &amp; Print Guide PDFs included</li>
      </ul>

      <button class="ls-checkout-btn"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{animal} Chinese Zodiac Art Bundle" data-product-price="14.99">{ls_btn_text}</button>
      <span class="ls-checkout-sub">Instant download · License &amp; Print Guide included · Secure checkout via Lemon Squeezy</span>

      <ul class="sidebar-trust">
        <li>Instant digital download</li>
        <li>300 DPI print-ready files</li>
        <li>Real Kansas LLC + clear POD license</li>
        <li>Secure direct checkout via Lemon Squeezy</li>
      </ul>

      <div class="etsy-secondary">
        <div class="etsy-secondary-label">Looking for something different?</div>
        <p>The Built by Josh Studio Etsy storefront has additional individual prints and other studio work. <a href="https://www.etsy.com/shop/BuiltByJoshStudio" target="_blank" rel="noopener">Visit the Etsy shop →</a></p>
        <p class="etsy-pause-note">Etsy storefront currently on a brief verification pause while the IRS finalizes EIN verification — {animal} bundle purchases above are unaffected.</p>
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
    <div class="section-label">Browse All Animals</div>
    <h2 class="section-title-main">Browse All 12 Chinese Zodiac Animal Bundles</h2>
    <p class="sister-intro">Every Chinese zodiac animal has its own bundle in the same structure — 48 files, 2 art styles, 8 designs, $14.99 per animal. Click any animal below to see its full collection.</p>
    <div class="sister-grid">
{sister_nav}
    </div>
  </section>

  <section class="related-section">
    <div class="section-label">Explore the rest of the BBJ Studio zodiac catalog</div>
    <h2 class="section-title-main">Related Collections</h2>
    <div class="related-grid">
      <a href="chinese-zodiac-realms.html" class="related-card">
        <div class="related-meta">Eastern Zodiac · Lunar Realms</div>
        <h3>Chinese Zodiac Realms</h3>
        <p>Landscape-style art for all 12 Chinese animals in a single bundle — environment rather than figure, two designs per animal.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="index.html" class="related-card">
        <div class="related-meta">Western Zodiac · 12 Signs</div>
        <h3>Western Signs Collection</h3>
        <p>All 12 Western zodiac signs in 14 art styles — 144 files per sign bundle, $24.99 each. The figure version of the Western zodiac.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="index.html" class="related-card">
        <div class="related-meta">Western Zodiac · 12 Realms</div>
        <h3>Western Realms Collection</h3>
        <p>Landscape-style art for all 12 Western signs — 48 files per sign bundle, $14.99 each. The environment version of the Western zodiac.</p>
        <span class="related-link">View Collection →</span>
      </a>
      <a href="zodiac-landscapes.html" class="related-card">
        <div class="related-meta">Western Landscapes Collection</div>
        <h3>Zodiac Landscapes</h3>
        <p>Oil-painted environments for all 12 Western signs in one bundle — the painterly companion to the Western Realms.</p>
        <span class="related-link">View Collection →</span>
      </a>
    </div>
  </section>

  <section class="cta-band">
    <div class="cta-eyebrow">Browse the Collection</div>
    <h2>2 Styles. 8 Designs. <span class="italic-accent">One {animal} Bundle.</span></h2>
    <p class="cta-sub">Eight original {animal} designs across two complementary styles, every design in three sizes and two formats. The full Chinese zodiac interpretation of the {animal} — $14.99, instant download, license and print guide included.</p>
    <button class="ls-checkout-btn ls-checkout-btn--large"{ls_disabled_attr} data-checkout-url="{ls_url}" data-product-name="{animal} Chinese Zodiac Art Bundle" data-product-price="14.99">{ls_btn_text}</button>
    <span class="cta-sub-line">Instant download — 48 print-ready {animal} files in your inbox the moment checkout completes.</span>
  </section>

  <footer>
    <div class="footer-left"><strong>Built by Josh Studio</strong> · All digital products — instant download</div>
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
    animals = sys.argv[1:] if len(sys.argv) > 1 else list(ANIMAL_META.keys())
    for animal in animals:
        if animal not in ANIMAL_META:
            print(f'SKIP: unknown animal {animal}')
            continue
        out = OUT_DIR / f'{ANIMAL_META[animal]["slug"]}-chinese-zodiac-art.html'
        html = build_page(animal, manifest)
        out.write_text(html, encoding='utf-8')
        lines = html.count('\n') + 1
        size_kb = out.stat().st_size / 1024
        print(f'Wrote {out.name} ({lines} lines, {size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
