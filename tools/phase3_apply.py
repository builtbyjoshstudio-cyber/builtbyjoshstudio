"""Phase 3 atomic update: convert chinese-zodiac-art.html to a hub, swap
homepage Chinese cards to new per-animal pages, add a Browse Chinese by
Animal section to collections/index.html, and update sitemap.xml."""
import re
import sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()

# (slug, TitleCase, recent-years-long, recent-years-short)
ANIMALS = [
    ('rat',     'Rat',     '1960, 1972, 1984, 1996, 2008, 2020', '2008, 2020, 2032'),
    ('ox',      'Ox',      '1961, 1973, 1985, 1997, 2009, 2021', '2009, 2021, 2033'),
    ('tiger',   'Tiger',   '1962, 1974, 1986, 1998, 2010, 2022', '2010, 2022, 2034'),
    ('rabbit',  'Rabbit',  '1963, 1975, 1987, 1999, 2011, 2023', '2011, 2023, 2035'),
    ('dragon',  'Dragon',  '1964, 1976, 1988, 2000, 2012, 2024', '2012, 2024, 2036'),
    ('snake',   'Snake',   '1965, 1977, 1989, 2001, 2013, 2025', '2013, 2025, 2037'),
    ('horse',   'Horse',   '1966, 1978, 1990, 2002, 2014, 2026', '2014, 2026, 2038'),
    ('goat',    'Goat',    '1967, 1979, 1991, 2003, 2015, 2027', '2015, 2027, 2039'),
    ('monkey',  'Monkey',  '1968, 1980, 1992, 2004, 2016, 2028', '2016, 2028, 2040'),
    ('rooster', 'Rooster', '1969, 1981, 1993, 2005, 2017, 2029', '2017, 2029, 2041'),
    ('dog',     'Dog',     '1970, 1982, 1994, 2006, 2018, 2030', '2018, 2030, 2042'),
    ('pig',     'Pig',     '1971, 1983, 1995, 2007, 2019, 2031', '2019, 2031, 2043'),
]


def update_chinese_hub():
    """Convert collections/chinese-zodiac-art.html from one-page-with-anchors
    to a hub linking out to per-animal pages."""
    path = ROOT / 'collections' / 'chinese-zodiac-art.html'
    text = path.read_text(encoding='utf-8')

    img_swaps = 0
    cta_swaps = 0
    for slug, name, _years_long, _years_short in ANIMALS:
        # Image src .jpg -> .webp
        old_img = f'<img src="../images/zodiac/chinese/{slug}.jpg"'
        new_img = f'<img src="../images/zodiac/chinese/{slug}.webp"'
        if old_img in text:
            text = text.replace(old_img, new_img, 1)
            img_swaps += 1

        # CTA: Etsy listing -> per-animal page (listing ID varies, so regex)
        cta_re = re.compile(
            rf'<a href="https://www\.etsy\.com/listing/\d+/{slug}-art-print-hyper-realistic[^"]*" class="etsy-cta-card" target="_blank" rel="noopener" data-animal="{slug}">Get the {name} Print on Etsy [^<]*</a>'
        )
        new_cta = (
            f'<a href="{slug}-chinese-zodiac-art.html" '
            f'class="etsy-cta-card" data-animal="{slug}">'
            f'View the Year of the {name} Collection ↗</a>'
        )
        text, n = cta_re.subn(new_cta, text, count=1)
        if n != 1:
            print(f'  WARN {slug}: CTA pattern not matched (count={n})')
        else:
            cta_swaps += 1

    # Hero chip: "$11.99 per bundle" -> "8 designs per animal"
    text, n_chip = re.subn(
        r'<span class="chip"><strong>\$11\.99</strong> per bundle</span>',
        r'<span class="chip"><strong>8 Designs</strong> per animal</span>',
        text, count=1
    )

    # Sidebar CTA: Etsy section link -> homepage Chinese section
    text, n_side = re.subn(
        r'<a href="https://www\.etsy\.com/shop/BuiltByJoshStudio\?section_id=58131947" target="_blank" rel="noopener" class="sidebar-cta">Browse the Full Collection [^<]*</a>',
        r'<a href="../index.html#chinese-zodiac" class="sidebar-cta">Browse All 12 Animals →</a>',
        text, count=1
    )

    # CTA band Etsy link -> homepage Chinese section
    text, n_band = re.subn(
        r'<a href="https://www\.etsy\.com/shop/BuiltByJoshStudio\?section_id=58131947" target="_blank" rel="noopener" class="btn-etsy">View the Chinese Zodiac Collection on Etsy [^<]*</a>',
        r'<a href="../index.html#chinese-zodiac" class="btn-etsy">Browse All 12 Year of the X Bundles →</a>',
        text, count=1
    )

    path.write_text(text, encoding='utf-8')
    print(
        f'chinese-zodiac-art.html: {img_swaps} img swaps, {cta_swaps} CTA swaps, '
        f'hero chip={n_chip}, sidebar={n_side}, CTA band={n_band}'
    )


def update_homepage():
    """Update index.html homepage #chinese-zodiac cards: swap anchor links to
    per-animal page URLs and .jpg thumbnails to .webp."""
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')

    href_swaps = 0
    img_swaps = 0
    for slug, name, *_ in ANIMALS:
        old_href = f'href="collections/chinese-zodiac-art.html#{slug}"'
        new_href = f'href="collections/{slug}-chinese-zodiac-art.html"'
        if old_href in text:
            text = text.replace(old_href, new_href, 1)
            href_swaps += 1
        old_img = f'src="images/zodiac/chinese/{slug}.jpg"'
        new_img = f'src="images/zodiac/chinese/{slug}.webp"'
        if old_img in text:
            text = text.replace(old_img, new_img, 1)
            img_swaps += 1
    path.write_text(text, encoding='utf-8')
    print(f'index.html: {href_swaps} href swaps, {img_swaps} img swaps')


def update_collections_hub():
    """Insert Browse Chinese by Animal section into collections/index.html
    between Western Realms and Signature Series."""
    path = ROOT / 'collections' / 'index.html'
    text = path.read_text(encoding='utf-8')

    cards = []
    for slug, name, _y_long, y_short in ANIMALS:
        cards.append(
            f'      <a href="{slug}-chinese-zodiac-art.html" class="collection-card">\n'
            f'        <div class="card-img"><img src="../images/zodiac/chinese/{slug}.webp" alt="Year of the {name} Chinese zodiac art bundle" loading="lazy" /></div>\n'
            f'        <div class="card-body">\n'
            f'          <div class="card-sign">{name} · {y_short}</div>\n'
            f'          <div class="card-name">Year of the {name}</div>\n'
            f'          <span class="card-link">View Collection →</span>\n'
            f'        </div>\n'
            f'      </a>'
        )

    section = (
        '\n  <section class="collections-section" style="padding-top:0">\n'
        '    <div class="section-label">Chinese Zodiac</div>\n'
        '    <h2 class="section-title">Browse Chinese by Animal</h2>\n\n'
        '    <div class="collection-grid">\n\n'
        + '\n\n'.join(cards)
        + '\n\n    </div>\n'
        '  </section>\n'
    )

    anchor = '  <section class="collections-section" style="padding-top:0">\n    <div class="section-label">Signature Series</div>'
    if anchor not in text:
        raise SystemExit('collections/index.html: Signature Series anchor not found')
    text = text.replace(anchor, section + '\n' + anchor, 1)
    path.write_text(text, encoding='utf-8')
    print(f'collections/index.html: inserted Browse Chinese by Animal ({len(ANIMALS)} cards)')


def update_sitemap():
    """Bump homepage, /collections/, chinese-zodiac-art.html lastmods.
    Append 12 new per-animal URLs after the chinese-zodiac-art.html entry."""
    path = ROOT / 'sitemap.xml'
    text = path.read_text(encoding='utf-8')

    bump_targets = [
        (r'<loc>https://builtbyjoshstudio\.com/</loc>',                                  'homepage'),
        (r'<loc>https://builtbyjoshstudio\.com/collections/</loc>',                       'collections/'),
        (r'<loc>https://builtbyjoshstudio\.com/collections/chinese-zodiac-art\.html</loc>', 'chinese-zodiac-art.html'),
    ]
    for url_pat, label in bump_targets:
        text, n = re.subn(
            rf'({url_pat}\s*\n\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}(</lastmod>)',
            rf'\g<1>{TODAY}\g<2>', text, count=1
        )
        print(f'sitemap.xml: {label} lastmod bump = {n}')

    new_entries = []
    for slug, *_ in ANIMALS:
        new_entries.append(
            '  <url>\n'
            f'    <loc>https://builtbyjoshstudio.com/collections/{slug}-chinese-zodiac-art.html</loc>\n'
            f'    <lastmod>{TODAY}</lastmod>\n'
            '    <changefreq>monthly</changefreq>\n'
            '    <priority>0.8</priority>\n'
            '  </url>'
        )

    anchor = (
        '  <url>\n'
        '    <loc>https://builtbyjoshstudio.com/collections/chinese-zodiac-art.html</loc>\n'
        f'    <lastmod>{TODAY}</lastmod>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>'
    )
    if anchor not in text:
        raise SystemExit('sitemap.xml: chinese-zodiac-art.html anchor not found post-bump')
    text = text.replace(anchor, anchor + '\n' + '\n'.join(new_entries), 1)
    path.write_text(text, encoding='utf-8')
    print(
        f'sitemap.xml: appended {len(ANIMALS)} new URLs, '
        f'now {text.count("<loc>")} total <loc> entries'
    )


if __name__ == '__main__':
    update_chinese_hub()
    update_homepage()
    update_collections_hub()
    update_sitemap()
