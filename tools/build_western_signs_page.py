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
    'Capricorn':    dict(slug='capricorn',   symbol='♑', element='Earth', modality='Cardinal', planet='Saturn',  symbol_label='The Sea-Goat',     dates='December 22 – January 19', dates_short='Dec 22 – Jan 19', sister_signs='Taurus, Virgo',        sku='BBJ-WS-CAPRICORN',   etsy_section_url='https://www.etsy.com/shop/BuiltByJoshStudio'),
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

# Map sign to its style copy. Message 5 will provide per-sign overrides.
STYLE_COPY_BY_SIGN = {'Aries': ARIES_STYLE_COPY}


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
         f'The {sign} bundle is priced at $24.99 — one-time payment, instant digital download. That works out to roughly $1.04 per individual design. Visit the Etsy listing for current promotional pricing if any sale is active.'),
        (f'Can I use the {sign} Zodiac Art Bundle for print-on-demand or commercial sales?',
         'Yes. The license includes print-on-demand rights for up to 100 physical units per individual design, cumulative across all formats, vendors, and time periods combined. You can sell framed prints, posters, canvases, mugs, t-shirts, and similar physical products made from the designs within that cap. For more than 100 prints of any single design, contact Built by Josh Studio LLC about extended commercial licensing.'),
        (f'What sizes can I print the {sign} art at?',
         'The largest file (6000 × 9000 pixels) prints crisply up to 20" × 30" at full 300 DPI. With a print provider running 150 DPI for large-format jobs, prints up to roughly 40" × 60" still look excellent. The bundle also includes 1:1 files (4800 × 4800) for square framing and 4:5 files (4800 × 6000) for standard portrait sizes like 8×10 and 16×20.'),
        (f'How were the {sign} designs created?',
         f"The {sign} designs were created by Built by Josh Studio LLC using a combination of human creative direction and AI image generation tools, including Leonardo.ai. Every design is selected, curated, refined, and finalized by the studio's founder. This is disclosed in full in the license agreement included with every bundle."),
        ('What formats and color profiles do the files use?',
         'All files are delivered in both PNG (lossless) and JPG (92% quality compression) formats. Color profile is sRGB — the standard for virtually every print-on-demand service and consumer printer, requiring no color conversion before printing.'),
        (f'Where can I buy the {sign} Zodiac Art Bundle right now?',
         f'The {sign} bundle is sold through the Built By Josh Studio Etsy shop. The shop is currently on a brief verification pause while the IRS finalizes EIN verification for the LLC. The bundle, pricing, and license structure are unchanged during the pause — the shop will resume normal operation once verification clears.'),
        ('Do you have art for other zodiac signs and the Chinese zodiac?',
         'Yes. Built By Josh Studio publishes 12 sign-specific bundles for all Western zodiac signs (Aries through Pisces, identical structure to the Aries bundle), 12 sign-specific bundles in the Western Realms landscape series, a full 12-landscape Western Landscapes Collection, 12 animal-specific Chinese Signs bundles, and a single Chinese Realms Collection covering all 12 Chinese animals.'),
    ]


def faq_schema_data(sign, styles_csv):
    """Schema variants: same Q/A but with inch-marks replaced for safe JSON."""
    data = faq_data(sign, styles_csv)
    out = []
    for q, a in data:
        # Replace " inch marks with the word "by" or "inches" for clean JSON
        a_schema = a.replace('20" × 30"', '20 by 30 inches').replace('40" × 60"', '40 by 60 inches').replace('8×10', '8x10').replace('16×20', '16x20').replace('×', 'x')
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

    /* Etsy vacation notice */
    .etsy-notice {{ max-width: 1000px; margin: 1.5rem auto 0; padding: 1.4rem 1.7rem; background: rgba(123,79,166,0.07); border: 1px solid rgba(123,79,166,0.25); border-left: 4px solid var(--bbj-accent2); }}
    .etsy-notice-label {{ font-family: 'Cinzel', serif; font-size: 0.62rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--bbj-accent); margin-bottom: 0.5rem; }}
    .etsy-notice p {{ font-family: 'Crimson Pro', serif; font-size: 0.98rem; line-height: 1.6; color: var(--body-read); margin: 0; }}

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
    .btn-etsy {{ display: inline-block; background: var(--bbj-accent); color: var(--bbj-bg); font-family: 'Cinzel', serif; font-size: 0.82rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; padding: 1.15rem 2.5rem; text-decoration: none; transition: background 0.2s, transform 0.2s; }}
    .btn-etsy:hover {{ background: #e0bd5a; transform: translateY(-2px); }}
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
    <p class="collection-tagline">24 original {sign} designs across 14 art styles — celestial, dark fantasy, watercolor, vintage poster, anime, hyper-realistic, silhouette, mythic guardian, and more. Every design ships in three print-ready sizes and both PNG and JPG, totaling 144 files in one bundle. Licensed for personal use and print-on-demand up to 100 prints per design.</p>
    <div class="hero-image">
      <img src="../images/zodiac/{slug}.webp" alt="{sign} zodiac art bundle preview — 14 art styles including celestial, dark fantasy, watercolor, and mythic guardians, from Built By Josh Studio" />
    </div>
  </header>

  <!-- The Short Version (GEO-citable summary) -->
  <aside class="short-version">
    <div class="short-version-label">The Short Version</div>
    <p>The {sign} Zodiac Art Bundle from Built By Josh Studio is a digital art collection containing 144 print-ready image files. Each bundle covers one Western zodiac sign and includes 24 original designs across 14 art-style series — {styles_csv}. Every design is delivered in three aspect ratios (1:1 square, 4:5 portrait, 2:3 portrait) at 300 DPI, in both PNG and JPG formats, with maximum dimensions of 6000 × 9000 pixels. The bundle is priced at $24.99 and includes a personal-use license plus print-on-demand rights for up to 100 physical prints per design. Files are instant-download — no physical shipping. All bundles are produced by Built by Josh Studio LLC, a Kansas limited liability company (Kansas Business ID 10076138).</p>
  </aside>

  <!-- Etsy vacation notice -->
  <aside class="etsy-notice">
    <div class="etsy-notice-label">Currently available via Etsy — temporary verification pause</div>
    <p>The Built By Josh Studio Etsy shop is briefly paused while the IRS finalizes our new LLC's EIN verification. The full {sign} Zodiac Art Bundle is queued and will be available for direct purchase again as soon as Etsy completes verification. Bookmark this page or follow the studio's Substack for the relaunch — no changes to pricing, file structure, or licensing during the pause.</p>
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
        <p>{sign} is the {ordinal_of(sign)} sign of the zodiac, spanning {m['dates']}. It is a {m['element'].lower()} sign ruled by {m['planet']}{aries_extra(sign)}</p>
        {aries_what_makes_extra(sign)}
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
      <div class="sidebar-price-note">One-time payment · Instant digital download · Etsy checkout</div>

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

      <a href="{m['etsy_section_url']}" target="_blank" rel="noopener" class="sidebar-cta">Buy on Etsy →</a>
      <span class="sidebar-cta-sub">Etsy shop on brief verification pause — bookmark and check back</span>

      <ul class="sidebar-trust">
        <li>Instant digital download</li>
        <li>300 DPI print-ready files</li>
        <li>Real Kansas LLC + clear POD license</li>
        <li>4.7★ shop rating on Etsy</li>
      </ul>
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
    <a href="{m['etsy_section_url']}" target="_blank" rel="noopener" class="btn-etsy">Buy the {sign} Bundle on Etsy →</a>
    <span class="cta-sub-line">Etsy currently on brief verification pause — bookmark this page and check back</span>
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


def aries_extra(sign):
    """Per-sign tail after 'ruled by <planet>'. Aries gets the brief-preserved
    descriptive sentence; other signs get a clean period."""
    if sign == 'Aries':
        return ' — the planet of drive, aggression, and action. Aries is represented by the ram, a symbol of headfirst momentum and refusal to back down.'
    return '.'


def aries_what_makes_extra(sign):
    """Preserve the original Aries paragraphs (Brief 1.6 says keep this section
    as-is for Aries). Other signs get nothing extra for now — Message 5 will
    provide per-sign equivalents."""
    if sign == 'Aries':
        return (
            '        <p>People born under Aries are often described as bold, competitive, and direct. They tend to be initiators — the ones who start the project, make the first move, and set the pace. Aries energy is forward motion. It doesn\'t wait for permission and it doesn\'t look back.</p>\n'
            '        <p>That energy defines this entire collection. Whether rendered in sacred geometry and gold leaf or in neon cyberpunk circuitry, every Aries piece is designed to feel like it\'s moving — even standing still.</p>'
        )
    return ''


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
