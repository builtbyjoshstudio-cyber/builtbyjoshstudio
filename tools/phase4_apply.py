"""Phase 4 atomic update for Chinese Zodiac Realms:
  - Insert <section id="chinese-realms"> into index.html between
    #chinese-zodiac and #landscapes (12 cards linking to anchors on the
    single chinese-zodiac-realms.html bundle page)
  - Add #chinese-realms to the BBJ glass styling multi-selectors in
    index.html inline <style> AND css/tokens.css (don't repeat the
    Phase 2 oversight)
  - Add a 3rd Chinese Realms card to the Signature Series on
    collections/index.html (alongside Chinese + Landscapes)
  - Bump sitemap lastmods and add 1 new <url> for the bundle page."""
import json
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()

# (animal, realm_title) — for each animal, the realm title from manifest
MANIFEST = ROOT / 'images' / 'zodiac' / 'chinese-realms' / 'manifest.json'

ANIMAL_ORDER = ['Rat','Ox','Tiger','Rabbit','Dragon','Snake','Horse','Goat','Monkey','Rooster','Dog','Pig']


def build_homepage_section(realm_titles):
    """Build the <section id='chinese-realms'> block for index.html.
    Mirrors the structure of #landscapes (12 cards on a single bundle page)."""
    cards = []
    for animal in ANIMAL_ORDER:
        slug = animal.lower()
        title = realm_titles[animal]
        cards.append(
            f'      <a href="collections/chinese-zodiac-realms.html#{slug}" class="card-bbj reveal">\n'
            f'        <div class="card-img-bbj"><img src="images/zodiac/chinese-realms/{slug}.webp" alt="{title} — Year of the {animal} Chinese Zodiac Realm Art Print" loading="lazy"></div>\n'
            f'        <div class="card-body-bbj">\n'
            f'          <div class="card-sign">{title} · {animal}</div>\n'
            f'          <div class="card-title-bbj"><span class="btn-buy-bbj">View Collection ↗</span></div>\n'
            f'        </div>\n'
            f'      </a>'
        )
    return (
        '\n\n  <!-- CHINESE ZODIAC REALMS ART -->\n'
        '  <section id="chinese-realms">\n'
        '    <div class="section-header-bbj" style="padding-bottom:1.5rem;border-bottom:1px solid var(--bbj-border);margin-bottom:2.5rem;">\n'
        '      <div>\n'
        '        <div class="bbj-eyebrow" style="font-family:\'Cinzel\',serif;font-size:0.68rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--bbj-accent);margin-bottom:0.5rem;">Built By Josh Studio</div>\n'
        '        <h2 style="font-family:\'Cinzel\',serif;font-size:clamp(1.8rem,3vw,2.6rem);font-weight:700;letter-spacing:0.04em;color:var(--bbj-text);line-height:1.15;">Chinese Zodiac Realms Art Prints</h2>\n'
        '        <p style="font-family:\'Crimson Pro\',serif;font-style:italic;font-size:1rem;color:var(--bbj-muted);margin-top:0.4rem;">Lunar Realms Series · One Realm Per Animal · 2 Variants Each</p>\n'
        '      </div>\n'
        '    </div>\n\n'
        '    <div class="product-grid-bbj">\n\n'
        + '\n\n'.join(cards)
        + '\n\n    </div>\n'
        '  </section>\n'
    )


def update_index_html(realm_titles):
    path = ROOT / 'index.html'
    text = path.read_text(encoding='utf-8')

    # (1) Inline <style> multi-selectors — add #chinese-realms
    inline_swaps = [
        (
            '    #builtbyjosh, #western-realms, #chinese-zodiac, #landscapes {',
            '    #builtbyjosh, #western-realms, #chinese-zodiac, #chinese-realms, #landscapes {'
        ),
        (
            '    #builtbyjosh::before, #western-realms::before {',
            '    #builtbyjosh::before, #western-realms::before, #chinese-realms::before {'
        ),
        (
            '      #tynkr, #builtbyjosh, #western-realms, #chinese-zodiac, #landscapes { padding: 4rem 2rem; }',
            '      #tynkr, #builtbyjosh, #western-realms, #chinese-zodiac, #chinese-realms, #landscapes { padding: 4rem 2rem; }'
        ),
        (
            '      #tynkr, #builtbyjosh, #western-realms, #chinese-zodiac, #landscapes { padding: 3.5rem 1.5rem; }',
            '      #tynkr, #builtbyjosh, #western-realms, #chinese-zodiac, #chinese-realms, #landscapes { padding: 3.5rem 1.5rem; }'
        ),
    ]
    n_inline = 0
    for old, new in inline_swaps:
        if old in text:
            text = text.replace(old, new, 1)
            n_inline += 1
    print(f'index.html inline CSS multi-selectors: {n_inline}/{len(inline_swaps)} updated')

    # (2) Insert the new section between #chinese-zodiac </section> and the next sibling
    # Anchor: the closing </section> of #chinese-zodiac, followed by the Landscapes comment
    section_html = build_homepage_section(realm_titles)
    anchor = '    </div>\n  </section>\n\n  <!-- ZODIAC LANDSCAPES ART -->'
    if anchor not in text:
        raise SystemExit('index.html: insertion anchor (Landscapes comment) not found')
    replacement = '    </div>\n  </section>' + section_html + '\n  <!-- ZODIAC LANDSCAPES ART -->'
    text = text.replace(anchor, replacement, 1)
    print(f'index.html: inserted <section id="chinese-realms"> with 12 cards')

    path.write_text(text, encoding='utf-8')


def update_tokens_css():
    path = ROOT / 'css' / 'tokens.css'
    text = path.read_text(encoding='utf-8')

    swaps = [
        (
            '#builtbyjosh::before,\n#western-realms::before,\n#chinese-zodiac::before,\n#landscapes::before {',
            '#builtbyjosh::before,\n#western-realms::before,\n#chinese-zodiac::before,\n#chinese-realms::before,\n#landscapes::before {'
        ),
        (
            '#builtbyjosh .card-bbj,\n#western-realms .card-bbj,\n#chinese-zodiac .card-bbj,\n#landscapes .card-bbj {',
            '#builtbyjosh .card-bbj,\n#western-realms .card-bbj,\n#chinese-zodiac .card-bbj,\n#chinese-realms .card-bbj,\n#landscapes .card-bbj {'
        ),
        (
            '#builtbyjosh .card-bbj:hover,\n#western-realms .card-bbj:hover,\n#chinese-zodiac .card-bbj:hover,\n#landscapes .card-bbj:hover {',
            '#builtbyjosh .card-bbj:hover,\n#western-realms .card-bbj:hover,\n#chinese-zodiac .card-bbj:hover,\n#chinese-realms .card-bbj:hover,\n#landscapes .card-bbj:hover {'
        ),
        (
            '  #builtbyjosh .card-bbj,\n  #western-realms .card-bbj,\n  #chinese-zodiac .card-bbj,\n  #landscapes .card-bbj {',
            '  #builtbyjosh .card-bbj,\n  #western-realms .card-bbj,\n  #chinese-zodiac .card-bbj,\n  #chinese-realms .card-bbj,\n  #landscapes .card-bbj {'
        ),
    ]
    n = 0
    for old, new in swaps:
        if old in text:
            text = text.replace(old, new, 1)
            n += 1
    print(f'css/tokens.css multi-selectors: {n}/{len(swaps)} updated')
    path.write_text(text, encoding='utf-8')


def update_collections_hub():
    """Add a Chinese Realms card to the Signature Series on collections/index.html
    (3rd card, sitting alongside Chinese + Landscapes)."""
    path = ROOT / 'collections' / 'index.html'
    text = path.read_text(encoding='utf-8')

    # The Signature Series uses a 2-column grid via inline style. Bumping to
    # auto-fit so a 3rd card flows naturally without needing to re-spec the grid.
    # Simpler: add a 3rd <a> card before the closing </div> of the signature grid.
    new_card = (
        '\n      <a href="chinese-zodiac-realms.html" class="collection-card">\n'
        '        <div class="card-img"><img src="../images/zodiac/chinese-realms/dragon.webp" alt="Chinese Zodiac Realms — hybrid cosmos-landscape series for all 12 animals" loading="lazy" /></div>\n'
        '        <div class="card-body">\n'
        '          <div class="card-sign">Chinese Zodiac Realms · 24 Designs · 12 Animals</div>\n'
        '          <div class="card-name">Chinese Zodiac Realms</div>\n'
        '          <span class="card-link">View Collection →</span>\n'
        '        </div>\n'
        '      </a>\n'
    )

    # Anchor: the closing </a> of the existing Landscapes Signature card, then </div>
    anchor = (
        '      <a href="zodiac-landscapes.html" class="collection-card">'
    )
    if anchor not in text:
        raise SystemExit('collections/index.html: Landscapes Signature card not found')

    # Find the matching </a> for the Landscapes card and insert our new card after it
    landscapes_end = text.index('</a>', text.index(anchor)) + len('</a>')
    text = text[:landscapes_end] + '\n' + new_card + text[landscapes_end:]

    # Bump the grid from 2-col to auto (3 cards now). Look for the inline style.
    text, n_grid = re.subn(
        r'(<div class="collection-grid" style="grid-template-columns:repeat\()2(,1fr\);max-width:)900px(;margin:0 auto">)',
        r'\g<1>3\g<2>1100px\g<3>', text, count=1
    )
    print(f'collections/index.html: inserted Signature Series Chinese Realms card; grid bump = {n_grid}')

    path.write_text(text, encoding='utf-8')


def update_sitemap():
    path = ROOT / 'sitemap.xml'
    text = path.read_text(encoding='utf-8')

    # Bump homepage, /collections/
    for url_pat, label in [
        (r'<loc>https://builtbyjoshstudio\.com/</loc>',                  'homepage'),
        (r'<loc>https://builtbyjoshstudio\.com/collections/</loc>',       'collections/'),
    ]:
        text, n = re.subn(
            rf'({url_pat}\s*\n\s*<lastmod>)\d{{4}}-\d{{2}}-\d{{2}}(</lastmod>)',
            rf'\g<1>{TODAY}\g<2>', text, count=1
        )
        print(f'sitemap.xml: {label} lastmod bump = {n}')

    # Add 1 new <url> for chinese-zodiac-realms.html
    new_entry = (
        '  <url>\n'
        '    <loc>https://builtbyjoshstudio.com/collections/chinese-zodiac-realms.html</loc>\n'
        f'    <lastmod>{TODAY}</lastmod>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>'
    )

    # Append after the last per-animal Chinese URL (pig)
    pig_anchor = (
        '  <url>\n'
        '    <loc>https://builtbyjoshstudio.com/collections/pig-chinese-zodiac-art.html</loc>\n'
        f'    <lastmod>{TODAY}</lastmod>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>'
    )
    if pig_anchor not in text:
        raise SystemExit('sitemap.xml: pig-chinese-zodiac-art.html anchor not found')
    text = text.replace(pig_anchor, pig_anchor + '\n' + new_entry, 1)
    path.write_text(text, encoding='utf-8')
    print(f'sitemap.xml: appended chinese-zodiac-realms.html, now {text.count("<loc>")} total <loc> entries')


if __name__ == '__main__':
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    realm_titles = {a: manifest[a].get('realm_titles', ['Lunar Realm'])[0] for a in ANIMAL_ORDER}

    update_index_html(realm_titles)
    update_tokens_css()
    update_collections_hub()
    update_sitemap()
