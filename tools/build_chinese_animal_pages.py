"""Generate per-animal Chinese Zodiac collection HTML pages from manifest.json.

Usage:
    python tools/build_chinese_animal_pages.py [ANIMAL ...]   # specific animals
    python tools/build_chinese_animal_pages.py                # all 12

Reads images/zodiac/chinese/manifest.json (built by the Chinese thumbs
generator). Writes collections/<animal>-chinese-zodiac-art.html.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'images' / 'zodiac' / 'chinese' / 'manifest.json'
OUT_DIR = ROOT / 'collections'

# Animal metadata. "blurb" lifted from the existing chinese-zodiac-art.html
# schema descriptions to preserve voice.
ANIMAL_META = {
    'Rat':     {'slug': 'rat',     'recent_years': '2008, 2020, 2032',
                'blurb': 'Clever, resourceful, and quick-witted. The Rat as a sharp-eyed sentinel in shadow and silver.'},
    'Ox':      {'slug': 'ox',      'recent_years': '2009, 2021, 2033',
                'blurb': 'Patient and built for the long haul. The Ox as an armored colossus — immovable, ancient, carved from the earth itself.'},
    'Tiger':   {'slug': 'tiger',   'recent_years': '2010, 2022, 2034',
                'blurb': 'Brave, competitive, magnetically confident. The Tiger in teal and gold with cosmic energy.'},
    'Rabbit':  {'slug': 'rabbit',  'recent_years': '2011, 2023, 2035',
                'blurb': 'Gentle, elegant, and quietly perceptive. The Rabbit as a luminous and watchful guardian.'},
    'Dragon':  {'slug': 'dragon',  'recent_years': '2012, 2024, 2036',
                'blurb': 'Powerful, ambitious, and revered. The Dragon in full spectacle — wings, fire, and cosmic scale.'},
    'Snake':   {'slug': 'snake',   'recent_years': '2013, 2025, 2037',
                'blurb': 'Wise, intuitive, enigmatic. The Snake as coiled intelligence and hypnotic, dangerous beauty. 2025 is the Year of the Snake.'},
    'Horse':   {'slug': 'horse',   'recent_years': '2014, 2026, 2038',
                'blurb': 'Energetic and free-spirited. The Horse mid-stride — mane blazing, hooves striking. 2026 is the Year of the Horse.'},
    'Goat':    {'slug': 'goat',    'recent_years': '2015, 2027, 2039',
                'blurb': 'Creative, gentle, drawn to beauty. The Goat as a serene, ethereal figure surrounded by soft cosmic light.'},
    'Monkey':  {'slug': 'monkey',  'recent_years': '2016, 2028, 2040',
                'blurb': 'Clever, playful, endlessly inventive. The Monkey as an agile, armored figure mid-leap with mischief in every detail.'},
    'Rooster': {'slug': 'rooster', 'recent_years': '2017, 2029, 2041',
                'blurb': 'Confident, honest, fiercely punctual. The Rooster as a crested warrior with metallic plumage.'},
    'Dog':     {'slug': 'dog',     'recent_years': '2018, 2030, 2042',
                'blurb': 'Loyal, honest, and protective. The Dog as an armored sentinel standing watch in cosmic darkness.'},
    'Pig':     {'slug': 'pig',     'recent_years': '2019, 2031, 2043',
                'blurb': 'Generous and warm-hearted. The Pig given a mythic frame — golden, generous, unapologetically present.'},
}

STYLE_LABELS = {
    'hyper-realistic': 'Hyper-Realistic — Lunar Guardians',
    'watercolor':      'Watercolor — Celestial Dreamscapes',
}


def build_design_card(d, animal, style_label):
    return f'''
          <div class="design-card">
            <img src="../{d["webp_path"]}" alt="{animal} Chinese Zodiac Art Print — {style_label} variant {d["variant"]}" loading="lazy" width="720" height="900">
            <div class="design-card-body">
              <h4>Variant {d["variant"]}</h4>
            </div>
          </div>'''


def build_style_block(style_key, designs, animal):
    label = STYLE_LABELS[style_key]
    sorted_designs = sorted(designs, key=lambda d: int(d['variant']))
    cards = ''.join(build_design_card(d, animal, label) for d in sorted_designs)
    return f'''
        <div class="realm-block">
          <h3 class="realm-title">{label}</h3>
          <div class="designs-grid">{cards}
          </div>
        </div>'''


def build_page(animal, manifest):
    meta = ANIMAL_META[animal]
    slug = meta['slug']
    animal_data = manifest[animal]
    designs = animal_data['designs']
    hub_thumb = animal_data['hub_thumb']

    by_style = {}
    for d in designs:
        by_style.setdefault(d['style'], []).append(d)

    # Order: hyper-realistic first, then watercolor
    style_order = ['hyper-realistic', 'watercolor']
    style_blocks_html = '\n'.join(build_style_block(s, by_style[s], animal) for s in style_order if s in by_style)

    # JSON-LD ItemList
    item_list_items = []
    for i, d in enumerate(designs, start=1):
        style_label = STYLE_LABELS[d['style']]
        item_list_items.append(
            '      {\n'
            '        "@type": "ListItem",\n'
            f'        "position": {i},\n'
            f'        "name": "{animal} — {style_label} variant {d["variant"]} Chinese Zodiac Art Print",\n'
            f'        "image": "https://builtbyjoshstudio.com/{d["webp_path"]}"\n'
            '      }'
        )
    item_list_json = ',\n'.join(item_list_items)

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
  <title>Year of the {animal} Chinese Zodiac Art Prints — 8 Lunar Guardian Designs | Built By Josh Studio</title>
  <meta name="description" content="8 original {animal} Chinese zodiac art prints — 4 hyper-realistic Lunar Guardian designs and 4 watercolor Celestial Dreamscape designs. Instant digital download bundle from Built By Josh Studio." />
  <meta name="keywords" content="Year of the {animal} art, {animal} Chinese zodiac art print, {animal} Lunar Guardian art, hyper-realistic {animal} wall art, watercolor {animal} zodiac print, Chinese zodiac digital download" />
  <link rel="canonical" href="https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" />

  <meta property="og:title" content="Year of the {animal} Chinese Zodiac Art Prints — 8 Designs | Built By Josh Studio" />
  <meta property="og:description" content="8 original {animal} Chinese zodiac art prints — 4 hyper-realistic + 4 watercolor. Instant digital download bundle from Built By Josh Studio." />
  <meta property="og:type" content="product" />
  <meta property="og:url" content="https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" />
  <meta property="og:site_name" content="Built By Josh Studio" />
  <meta property="og:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Year of the {animal} Chinese Zodiac Art Prints — 8 Designs | Built By Josh Studio" />
  <meta name="twitter:description" content="8 original {animal} Chinese zodiac art prints — 4 hyper-realistic + 4 watercolor. Instant digital download bundle from Built By Josh Studio." />
  <meta name="twitter:image" content="https://builtbyjoshstudio.com/{hub_thumb}" />

  <script type="application/ld+json">
  {{ "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {{ "@type": "ListItem", "position": 1, "name": "Home", "item": "https://builtbyjoshstudio.com/" }},
    {{ "@type": "ListItem", "position": 2, "name": "Collections", "item": "https://builtbyjoshstudio.com/collections/" }},
    {{ "@type": "ListItem", "position": 3, "name": "Year of the {animal} Chinese Zodiac", "item": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html" }}
  ] }}
  </script>

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Year of the {animal} Chinese Zodiac Art Prints",
    "description": "8 original {animal} Chinese zodiac art prints across 2 styles — 4 hyper-realistic Lunar Guardian designs and 4 watercolor Celestial Dreamscape designs.",
    "url": "https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html",
    "isPartOf": {{ "@type": "WebSite", "name": "Built By Josh Studio", "url": "https://builtbyjoshstudio.com" }},
    "about": {{ "@type": "Thing", "name": "Year of the {animal} Chinese Zodiac Art", "description": "Chinese zodiac art for the {animal} animal sign." }},
    "mainEntity": {{
      "@type": "ItemList",
      "name": "Year of the {animal} Chinese Zodiac Designs",
      "numberOfItems": {len(designs)},
      "itemListElement": [
{item_list_json}
      ]
    }}
  }}
  </script>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--bbj-bg:#0b0813;--bbj-surface:#120f1f;--bbj-surface-2:#171327;--bbj-accent:#c9a84c;--bbj-accent2:#7b4fa6;--bbj-text:#ede8f5;--bbj-muted:#8a7fa8;--bbj-border:#2a2040;--body-read:#d6cee8}}
    html{{scroll-behavior:smooth}}
    body{{font-family:'DM Sans',sans-serif;background:var(--bbj-bg);color:var(--bbj-text);overflow-x:hidden;min-height:100vh}}
    .stars{{position:absolute;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
    .star{{position:absolute;width:2px;height:2px;background:#fff;border-radius:50%;opacity:0;animation:twinkle var(--d) ease-in-out infinite var(--delay)}}
    @keyframes twinkle{{0%,100%{{opacity:0;transform:scale(.5)}}50%{{opacity:var(--op);transform:scale(1)}}}}
    .site-nav{{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:0 2.5rem;height:64px;background:rgba(11,8,19,.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--bbj-border)}}
    .nav-logo{{font-family:'Syne',sans-serif;font-weight:800;font-size:1.1rem;letter-spacing:-.02em;color:var(--bbj-text);text-decoration:none}}
    .nav-links{{display:flex;gap:2rem;list-style:none}}
    .nav-links a{{font-family:'DM Sans',sans-serif;font-size:.85rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;color:var(--bbj-muted);transition:color .2s}}
    .nav-links a:hover{{color:var(--bbj-accent)}}
    .nav-links a.active{{color:var(--bbj-accent)}}
    .collection-hero{{padding:9rem 2rem 3rem;max-width:1200px;margin:0 auto;text-align:center;position:relative}}
    .collection-hero::before{{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 0%,rgba(201,168,76,.1) 0%,transparent 55%),radial-gradient(ellipse at 20% 80%,rgba(123,79,166,.08) 0%,transparent 50%)}}
    .breadcrumb{{font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:var(--bbj-muted);margin-bottom:1.4rem;position:relative}}
    .breadcrumb a{{color:var(--bbj-accent);text-decoration:none}}
    .breadcrumb a:hover{{text-decoration:underline}}
    .breadcrumb .sep{{margin:0 .6rem;opacity:.5}}
    .hero-eyebrow{{font-family:'Cinzel',serif;font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;color:var(--bbj-accent);margin-bottom:1.2rem;position:relative}}
    h1.collection-title{{font-family:'Cinzel',serif;font-size:clamp(2.2rem,5.5vw,3.8rem);font-weight:700;letter-spacing:.02em;line-height:1.12;color:var(--bbj-text);margin-bottom:1.4rem;max-width:900px;margin-left:auto;margin-right:auto;position:relative}}
    h1.collection-title .italic-accent{{color:var(--bbj-accent);font-family:'Crimson Pro',serif;font-style:italic;font-weight:400}}
    .collection-tagline{{font-family:'Crimson Pro',serif;font-size:clamp(1.1rem,1.7vw,1.3rem);font-style:italic;color:var(--body-read);max-width:720px;margin:0 auto 2.5rem;line-height:1.6;position:relative}}
    .hero-image{{max-width:420px;margin:0 auto;position:relative;border:1px solid var(--bbj-border);overflow:hidden;aspect-ratio:4/5}}
    .hero-image img{{width:100%;height:100%;object-fit:cover;display:block}}
    .hero-image::after{{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(201,168,76,.08) 0%,transparent 70%);pointer-events:none}}
    .hero-meta-chips{{display:flex;justify-content:center;gap:.8rem;flex-wrap:wrap;position:relative;margin-top:2rem}}
    .chip{{font-family:'Cinzel',serif;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--bbj-muted);border:1px solid var(--bbj-border);padding:.5rem 1rem;background:rgba(255,255,255,.015)}}
    .chip strong{{color:var(--bbj-accent);font-weight:600}}
    .collection-main{{max-width:1200px;margin:2rem auto 0;padding:2rem 2rem 4rem;display:grid;grid-template-columns:1fr 340px;gap:3rem;align-items:start}}
    .main-column{{font-family:'Crimson Pro',serif;font-size:1.15rem;line-height:1.75;color:var(--body-read);min-width:0}}
    .main-column section{{margin-bottom:3rem;padding-top:2.5rem;border-top:1px solid var(--bbj-border)}}
    .main-column section:first-child{{border-top:none;padding-top:0}}
    .main-column h2{{font-family:'Cinzel',serif;font-size:clamp(1.4rem,2.6vw,1.85rem);font-weight:700;letter-spacing:.02em;color:var(--bbj-text);margin-bottom:1.3rem;line-height:1.2}}
    .main-column p{{margin-bottom:1.3rem}}
    .realm-block{{margin-bottom:2.5rem}}
    .realm-title{{font-family:'Cinzel',serif;font-size:1.3rem;font-weight:700;color:var(--bbj-text);letter-spacing:.02em;margin-bottom:1rem;padding-bottom:.6rem;border-bottom:1px solid var(--bbj-border)}}
    .designs-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}}
    .design-card{{background:var(--bbj-surface);border:1px solid var(--bbj-border);overflow:hidden;transition:border-color .25s,background .25s;display:flex;flex-direction:column}}
    .design-card:hover{{border-color:rgba(201,168,76,.35);background:var(--bbj-surface-2)}}
    .design-card img{{width:100%;height:auto;aspect-ratio:4/5;object-fit:cover;display:block;background:linear-gradient(135deg,#1a1230 0%,#0d0a1a 100%);border-bottom:1px solid var(--bbj-border)}}
    .design-card-body{{padding:.9rem 1.1rem 1rem}}
    .design-card-body h4{{font-family:'Cinzel',serif;font-size:.85rem;font-weight:600;color:var(--bbj-muted);letter-spacing:.08em;text-transform:uppercase;margin:0}}
    .sticky-sidebar{{position:sticky;top:88px;background:var(--bbj-surface);border:1px solid var(--bbj-border);padding:1.8rem 1.7rem;font-family:'DM Sans',sans-serif}}
    .sticky-sidebar::before{{content:'';position:absolute;inset:0;pointer-events:none;background:linear-gradient(135deg,rgba(201,168,76,.05) 0%,transparent 60%)}}
    .sticky-sidebar>*{{position:relative}}
    .sidebar-label{{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--bbj-muted);margin-bottom:.4rem}}
    .sidebar-price{{font-family:'Cinzel',serif;font-size:1.4rem;font-weight:700;color:var(--bbj-accent);line-height:1;margin-bottom:.4rem}}
    .sidebar-price-note{{font-size:.8rem;color:var(--bbj-muted);margin-bottom:1.4rem;padding-bottom:1.4rem;border-bottom:1px solid var(--bbj-border)}}
    .sidebar-included-label{{font-family:'Cinzel',serif;font-size:.62rem;letter-spacing:.2em;text-transform:uppercase;color:var(--bbj-muted);margin-bottom:.8rem}}
    .sidebar-included{{list-style:none;padding:0;margin:0 0 1.5rem 0}}
    .sidebar-included li{{font-size:.85rem;color:var(--body-read);padding:.42rem 0 .42rem 1.3rem;position:relative;line-height:1.35;border-bottom:1px solid rgba(42,32,64,.5)}}
    .sidebar-included li:last-child{{border-bottom:none}}
    .sidebar-included li::before{{content:'✓';position:absolute;left:0;color:var(--bbj-accent);font-weight:700;font-size:.85rem}}
    .sidebar-cta-pending{{display:block;padding:1.05rem 1rem;background:transparent;border:1px solid var(--bbj-border);color:var(--bbj-muted);font-family:'Cinzel',serif;font-size:.72rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;text-align:center;margin-bottom:1.1rem;cursor:default}}
    .sidebar-trust{{list-style:none;padding:0;margin:0}}
    .sidebar-trust li{{font-size:.75rem;color:var(--bbj-muted);padding:.35rem 0 .35rem 1.2rem;position:relative;line-height:1.35}}
    .sidebar-trust li::before{{content:'✦';position:absolute;left:0;color:var(--bbj-accent);font-size:.72rem;top:.38rem}}
    .faq-section{{max-width:900px;margin:0 auto;padding:5rem 2rem 4rem}}
    .section-label{{font-family:'Cinzel',serif;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--bbj-accent);text-align:center;margin-bottom:.6rem}}
    .section-title-main{{font-family:'Cinzel',serif;font-size:clamp(1.8rem,3.2vw,2.4rem);font-weight:700;letter-spacing:.02em;color:var(--bbj-text);text-align:center;margin-bottom:2.8rem}}
    .faq-list{{display:flex;flex-direction:column;gap:0;border-top:1px solid var(--bbj-border)}}
    .faq-item{{border-bottom:1px solid var(--bbj-border);padding:1.6rem 0}}
    .faq-item h3{{font-family:'Cinzel',serif;font-size:1.05rem;font-weight:600;color:var(--bbj-text);margin-bottom:.7rem}}
    .faq-item p{{font-family:'Crimson Pro',serif;font-size:1.05rem;line-height:1.65;color:var(--body-read);margin:0}}
    footer{{background:#0a0a0f;padding:3rem 5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1.5rem}}
    .footer-left{{font-family:'Syne',sans-serif;font-size:.75rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.3)}}
    .footer-left strong{{color:rgba(255,255,255,.7)}}
    .footer-links{{display:flex;gap:1.5rem;list-style:none}}
    .footer-links a{{font-size:.75rem;color:rgba(255,255,255,.3);text-decoration:none;transition:color .2s;letter-spacing:.06em;text-transform:uppercase}}
    .footer-links a:hover{{color:rgba(255,255,255,.7)}}
    .footer-legal{{font-family:'DM Sans',sans-serif;font-size:.7rem;color:rgba(255,255,255,.3);width:100%;text-align:center;margin-top:1rem;line-height:1.6}}
    @media(max-width:1024px){{.collection-main{{grid-template-columns:1fr;gap:2.5rem}}.sticky-sidebar{{position:static;order:-1;max-width:500px;margin:0 auto;width:100%}}}}
    @media(max-width:720px){{.collection-hero{{padding:7rem 1.5rem 2rem}}.collection-main{{padding:1.5rem 1.5rem 3rem}}.main-column{{font-size:1.08rem}}.faq-section{{padding:4rem 1.5rem 3rem}}.site-nav{{padding:0 1.5rem}}.nav-links{{gap:1.2rem}}.designs-grid{{grid-template-columns:1fr}}footer{{flex-direction:column;padding:2rem;text-align:center}}}}
    .nav-logo{{white-space:nowrap}}.nav-logo .logo-short{{display:none}}
    @media(max-width:720px){{.site-nav{{padding:0 1rem}}.nav-logo{{font-size:.88rem}}.nav-logo .logo-full{{display:none}}.nav-logo .logo-short{{display:inline}}.nav-links{{gap:.9rem}}.nav-links a{{font-size:.72rem;letter-spacing:.04em}}}}
    @media(max-width:420px){{.nav-logo{{font-size:.78rem}}.nav-links{{gap:.55rem}}.nav-links a{{font-size:.62rem;letter-spacing:.03em}}}}
  </style>
  <link rel="stylesheet" href="/css/tokens.css" />
  <link rel="stylesheet" href="/css/mobile-nav.css" />
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
    <div class="breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span><a href="index.html">Collections</a><span class="sep">/</span><span>Year of the {animal}</span></div>
    <div class="hero-eyebrow">Year of the {animal} · Chinese Zodiac · 4 Hyper-Realistic + 4 Watercolor</div>
    <h1 class="collection-title">Year of the {animal} — <span class="italic-accent">Chinese Zodiac Art</span></h1>
    <p class="collection-tagline">{meta['blurb']}</p>
    <div class="hero-image"><img src="../{hub_thumb}" alt="Year of the {animal} Chinese Zodiac Art Print — hero design" /></div>
    <div class="hero-meta-chips"><span class="chip"><strong>8 Designs</strong></span><span class="chip">2 Styles</span><span class="chip">Up to 6000×9000 px</span><span class="chip">Instant Download</span></div>
  </header>

  <div class="collection-main">
    <main class="main-column">
      <section>
        <h2>The Year of the {animal} Bundle — 8 Designs Across 2 Styles</h2>
        <p>The {animal} bundle includes all 8 Chinese zodiac art prints for the Year of the {animal} — 4 hyper-realistic Lunar Guardian designs and 4 watercolor Celestial Dreamscape designs. Every print is delivered at print-ready high resolution (up to 6000×9000 px).</p>
        <p>Recent Years of the {animal}: <strong>{meta['recent_years']}</strong>. If you, your partner, or a gift recipient was born in any of those years, the {animal} is their Chinese zodiac animal.</p>
      </section>

      <section>
        <h2>All 8 Year of the {animal} Designs</h2>
{style_blocks_html}
      </section>
    </main>

    <aside class="sticky-sidebar">
      <div class="sidebar-label">Bundle Price</div>
      <div class="sidebar-price">Coming soon</div>
      <div class="sidebar-price-note">The full 8-design Year of the {animal} bundle launches on Lemon Squeezy. Pricing to be set at launch.</div>
      <div class="sidebar-included-label">What's Included</div>
      <ul class="sidebar-included">
        <li>All 8 Year of the {animal} designs</li>
        <li>4 hyper-realistic Lunar Guardians</li>
        <li>4 watercolor Celestial Dreamscapes</li>
        <li>High-resolution files (up to 6000×9000 px)</li>
        <li>Both JPG and PNG, 3 aspect ratios per design</li>
        <li>Instant download after purchase</li>
      </ul>
      <div class="sidebar-cta-pending">Available Soon — Lemon Squeezy</div>
      <ul class="sidebar-trust">
        <li>Instant digital download</li>
        <li>High-resolution print-ready files</li>
        <li>No shipping, no waiting</li>
      </ul>
    </aside>
  </div>

  <section class="faq-section">
    <div class="section-label">Frequently Asked</div>
    <h2 class="section-title-main">Frequently Asked Questions</h2>
    <div class="faq-list">
      <div class="faq-item"><h3>What Chinese zodiac animal am I?</h3><p>Your Chinese zodiac animal is determined by your birth year. The 12-year cycle is Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, and Pig. Recent Years of the {animal}: {meta['recent_years']}. Note that the Chinese zodiac year starts at Lunar New Year (late January or February), so if you were born in January or early February, your animal may be from the previous year.</p></div>
      <div class="faq-item"><h3>What's included in the Year of the {animal} bundle?</h3><p>All 8 {animal} designs across two styles: 4 hyper-realistic Lunar Guardian prints (cinematic dark fantasy renderings) and 4 watercolor Celestial Dreamscape prints (soft painterly cosmos scenes). Files come in 3 sizes (4800×4800, 4800×6000, 6000×9000) and 2 formats (JPG + PNG). 48 files in total.</p></div>
      <div class="faq-item"><h3>When will this bundle be available to purchase?</h3><p>The Year of the {animal} bundle launches on Lemon Squeezy. We'll update this page when the bundle is live.</p></div>
      <div class="faq-item"><h3>Can I use these prints commercially or resell them?</h3><p>No. All prints are licensed for personal use only — printing for your own home, office, or as a personal gift. Commercial use including reselling, redistribution, print-on-demand, or merchandising is not permitted under the license.</p></div>
      <div class="faq-item"><h3>Do you have bundles for the other 11 Chinese zodiac animals?</h3><p>Yes. Built By Josh Studio has Chinese zodiac art bundles for all 12 animals — Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, and Pig. Browse all 12 on the homepage or the collections page.</p></div>
    </div>
  </section>

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
    <div class="footer-legal">&copy; 2026 Built by Josh Studio LLC. All rights reserved.<br>Tynkr Tools &amp; Co is a brand of Built by Josh Studio LLC.</div>
  </footer>

  <script>
    const container=document.getElementById('starsContainer');
    for(let i=0;i<80;i++){{
      const s=document.createElement('div');
      s.className='star';
      const left=Math.random()*100;
      const top=Math.random()*100;
      const d=2+Math.random()*4;
      const delay=Math.random()*4;
      const op=0.3+Math.random()*0.7;
      const blur=Math.random()>0.8?'1px':'0px';
      const wh=Math.random()>0.8?3:2;
      s.style.cssText='left:'+left+'%;top:'+top+'%;--d:'+d+'s;--delay:-'+delay+'s;--op:'+op+';filter:blur('+blur+');width:'+wh+'px;height:'+wh+'px;';
      container.appendChild(s);
    }}
  </script>
  <script src="/js/mobile-nav.js" defer></script>
  <script src="/js/ga4-events.js" defer></script>
</body>
</html>
'''


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    animals_to_build = sys.argv[1:] if len(sys.argv) > 1 else list(ANIMAL_META.keys())
    for animal in animals_to_build:
        if animal not in ANIMAL_META:
            print(f'SKIP: unknown animal {animal}')
            continue
        out_path = OUT_DIR / f'{ANIMAL_META[animal]["slug"]}-chinese-zodiac-art.html'
        html = build_page(animal, manifest)
        out_path.write_text(html, encoding='utf-8')
        lines = html.count('\n') + 1
        size_kb = out_path.stat().st_size / 1024
        print(f'Wrote {out_path.name} ({lines} lines, {size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
