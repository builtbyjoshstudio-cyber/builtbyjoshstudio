"""Surgical update of the existing collections/<sign>-zodiac-art.html
pages to use the new Western Signs source structure (14 styles, 24 unique
compositions per sign).

Per Josh's directive (path 'a' in the Phase 5 plan): preserve all the
existing marketing copy on each per-sign page, swap ONLY the styles grid
and the hub thumbnail image references throughout.

Replacements per page:
  1. og:image, twitter:image, Product schema image
     -> images/zodiac/<sign>.webp (was .jpg)
  2. Hero <img src="../images/zodiac/<sign>.jpg"> -> .webp
  3. <div class="styles-grid"> ... </div>  (12 hardcoded style cards)
     -> a 14-section grouped layout (1-4 cards per style) using the
        new design webps from images/zodiac/<sign>/<style-slug>-<n>.webp
  4. CollectionPage mainEntity ItemList itemListElement (12 entries)
     -> 24 entries, one per unique composition
  5. Add a small CSS block for .style-block / .style-block-title inside
     the existing inline <style> (additive, no existing rules touched).

Run:
    python tools/update_western_sign_pages.py [SIGN ...]
With no args, updates all 12 signs.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'images' / 'zodiac' / 'western-signs-manifest.json'
PAGES_DIR = ROOT / 'collections'

SIGN_SLUGS = {
    'Aries': 'aries', 'Taurus': 'taurus', 'Gemini': 'gemini', 'Cancer': 'cancer',
    'Leo': 'leo', 'Virgo': 'virgo', 'Libra': 'libra', 'Scorpio': 'scorpio',
    'Sagittarius': 'sagittarius', 'Capricorn': 'capricorn',
    'Aquarius': 'aquarius', 'Pisces': 'pisces',
}

# Additive CSS block (inserted right after the existing styles-grid rules)
NEW_CSS = """
    /* ── PHASE 5: 14-STYLE GROUPED LAYOUT ── */
    .styles-grouped { display: flex; flex-direction: column; gap: 2rem; margin-top: 1.5rem; }
    .style-block { display: flex; flex-direction: column; gap: 1rem; }
    .style-block-title {
      font-family: 'Cinzel', serif; font-size: 1.05rem; font-weight: 700;
      color: var(--bbj-text); letter-spacing: 0.04em; text-transform: uppercase;
      padding-bottom: 0.6rem; border-bottom: 1px solid var(--bbj-border); margin: 0;
    }
"""


def build_style_block(style_obj, sign):
    cards = []
    for d in style_obj['designs']:
        cards.append(
            '          <div class="style-card">\n'
            f'            <img src="../{d["webp_path"]}" alt="{style_obj["name"]} Variant {d["variant"]} — {sign} Zodiac Art Print" loading="lazy" width="720" height="900">\n'
            '            <div class="style-card-body">\n'
            f'              <h4 style="font-family:\'Cinzel\',serif;font-size:.85rem;font-weight:600;color:var(--bbj-muted);letter-spacing:.08em;text-transform:uppercase;margin:0">Variant {d["variant"]}</h4>\n'
            '            </div>\n'
            '          </div>'
        )
    return (
        '        <div class="style-block">\n'
        f'          <h3 class="style-block-title">{style_obj["name"]}</h3>\n'
        '          <div class="styles-grid">\n\n' + '\n\n'.join(cards) + '\n\n'
        '          </div>\n'
        '        </div>'
    )


def build_grouped_grid(sign_data, sign):
    blocks = [build_style_block(s, sign) for s in sign_data['styles']]
    return (
        '        <div class="styles-grouped">\n\n' + '\n\n'.join(blocks) + '\n\n'
        '        </div>'
    )


def build_item_list(sign_data, sign, sign_slug):
    items = []
    pos = 1
    for style in sign_data['styles']:
        for d in style['designs']:
            items.append(
                '      {\n'
                '        "@type": "ListItem",\n'
                f'        "position": {pos},\n'
                f'        "name": "{style["name"]} — Variant {d["variant"]} ({sign} Zodiac Art Print)",\n'
                f'        "url": "https://www.etsy.com/shop/BuiltByJoshStudio",\n'
                f'        "image": "https://builtbyjoshstudio.com/{d["webp_path"]}"\n'
                '      }'
            )
            pos += 1
    return ',\n'.join(items)


def update_page(sign, manifest):
    sign_slug = SIGN_SLUGS[sign]
    path = PAGES_DIR / f'{sign_slug}-zodiac-art.html'
    if not path.exists():
        print(f'SKIP {sign}: {path.name} not found')
        return
    text = path.read_text(encoding='utf-8')
    sign_data = manifest[sign]

    summary = {}

    # (1) Hub thumbnail .jpg -> .webp in og:image, twitter:image, Product schema image
    abs_old = f'https://builtbyjoshstudio.com/images/zodiac/{sign_slug}.jpg'
    abs_new = f'https://builtbyjoshstudio.com/images/zodiac/{sign_slug}.webp'
    n = text.count(abs_old)
    text = text.replace(abs_old, abs_new)
    summary['abs_url_swaps'] = n

    # (2) Hero <img src="..">
    rel_old = f'<img src="../images/zodiac/{sign_slug}.jpg"'
    rel_new = f'<img src="../images/zodiac/{sign_slug}.webp"'
    n = text.count(rel_old)
    text = text.replace(rel_old, rel_new)
    summary['rel_img_swaps'] = n

    # (2b) Patch the existing .styles-grid .style-card img rule to use 4/5 +
    # height: auto so the HTML height="900" attr doesn't override aspect-ratio
    # (was aspect-ratio: 1/1 designed for the old square thumb files).
    old_img_rule = (
        '    .styles-grid .style-card img {\n'
        '      width: 100%;\n'
        '      aspect-ratio: 1 / 1;\n'
        '      object-fit: cover;\n'
        '      display: block;'
    )
    new_img_rule = (
        '    .styles-grid .style-card img {\n'
        '      width: 100%;\n'
        '      height: auto;\n'
        '      aspect-ratio: 4 / 5;\n'
        '      object-fit: cover;\n'
        '      display: block;'
    )
    if old_img_rule in text:
        text = text.replace(old_img_rule, new_img_rule, 1)
        summary['img_aspect_patched'] = True
    else:
        summary['img_aspect_patched'] = 'already-patched-or-missing'

    # (3) Add new CSS just after the existing "STYLE CARDS WITH THUMBNAILS" block
    css_anchor = '    /* ── STYLE CARDS WITH THUMBNAILS ── */'
    if css_anchor in text and 'PHASE 5: 14-STYLE GROUPED LAYOUT' not in text:
        # Insert NEW_CSS at the END of the existing "STYLE CARDS WITH THUMBNAILS" block.
        # The block ends at the next style-card-body { ... } closing. Use closing brace
        # of the .style-card-body p rule as the anchor.
        end_of_block_anchor = '    .styles-grid .style-card .style-card-body p { margin-bottom: 0 !important; }\n'
        if end_of_block_anchor in text:
            text = text.replace(end_of_block_anchor, end_of_block_anchor + NEW_CSS, 1)
            summary['css_inserted'] = True
        else:
            summary['css_inserted'] = False
            print(f'  WARN: {sign}: css insertion anchor not found')
    else:
        summary['css_inserted'] = 'already-present' if 'PHASE 5' in text else False

    # (4) Replace the <div class="styles-grid"> ... </div> block with the new grouped grid.
    # Use a marker pair: opening (with the indentation we know) and a unique
    # closing pattern that includes the section close that follows.
    grid_pattern = re.compile(
        r'        <div class="styles-grid">.*?\n        </div>\n      </section>',
        re.DOTALL
    )
    new_grid_block = build_grouped_grid(sign_data, sign) + '\n      </section>'
    new_text, n_grid = grid_pattern.subn(new_grid_block, text, count=1)
    summary['grid_replaced'] = n_grid
    if n_grid == 1:
        text = new_text

    # (5) Replace the CollectionPage ItemList itemListElement contents.
    # The existing JSON-LD has the pattern:
    #   "numberOfItems": 12,
    #   "itemListElement": [
    #     {...}, {...}, ..., {...}
    #   ]
    # We replace the inner array contents AND bump numberOfItems.
    new_items = build_item_list(sign_data, sign, sign_slug)
    total = sum(len(s['designs']) for s in sign_data['styles'])

    # Bump numberOfItems
    text, n_nof = re.subn(
        r'(\"name\": \"' + re.escape(sign) + r' Zodiac Art Print Styles\",\s*\n\s*\"numberOfItems\":\s*)\d+',
        rf'\g<1>{total}', text, count=1
    )
    summary['numberOfItems_bumped'] = n_nof

    # Replace the CollectionPage ItemList's itemListElement contents.
    # Anchor on the unique CollectionPage block (its mainEntity.name +
    # numberOfItems + itemListElement together) so we don't accidentally hit
    # the BreadcrumbList ItemList earlier in the file.
    item_list_pattern = re.compile(
        r'(\"name\": \"' + re.escape(sign) + r' Zodiac Art Print Styles\",\s*\n\s*\"numberOfItems\":\s*\d+,\s*\n\s*\"itemListElement\":\s*\[\n)(.*?)(\n\s*\]\n\s*\})',
        re.DOTALL
    )
    text, n_il = item_list_pattern.subn(
        lambda m: m.group(1) + new_items + m.group(3),
        text, count=1
    )
    summary['itemList_replaced'] = n_il

    path.write_text(text, encoding='utf-8')
    return summary


def main():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    signs = sys.argv[1:] if len(sys.argv) > 1 else list(SIGN_SLUGS.keys())
    for sign in signs:
        if sign not in SIGN_SLUGS:
            print(f'SKIP: unknown sign {sign}')
            continue
        summary = update_page(sign, manifest)
        if summary:
            print(f'{sign:<13} {summary}')


if __name__ == '__main__':
    main()
