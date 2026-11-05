"""Remove Etsy references from the zodiac Collection pages (and their generators).

Scope (Josh, 2026-11-05): the 40 zodiac Collection pages under collections/
plus the 5 generators that build them and the Collection page master template.
The Lemon Squeezy checkout overlay becomes the only purchase action.

  - FAQ answer (schema + visible): "no Etsy account required" -> "no account
    required"; the "Etsy storefront ... does not sell the full Collection
    bundles" sentence dropped.
  - Sidebar "Looking for something different?" block: the Etsy shop paragraph
    is removed. On the 12 Western Signs pages the block keeps its Redbubble
    paragraph and is renamed .alt-shop; everywhere else the block held only
    the Etsy link, so the whole div and its CSS go.
  - Reviews: "Reviews from ... Etsy shop" -> "Verified Buyer Reviews",
    "Etsy buyer" -> "Verified buyer". Same markup, so the grid is unchanged.
  - "Who buys" bullet, pricing note, Chinese hub sidebar/FAQ copy.
  - Orphan CSS: .etsy-notice (no element uses it), .etsy-pause-note (dead
    since f3e9d3e). Chinese hub internal links styled as .etsy-cta-card /
    .btn-etsy are renamed .animal-cta-card / .btn-cta.

NOT touched (global): the Organization sameAs list and the footer Etsy link.
Idempotent: a second run changes nothing. Every replacement is count-asserted.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WESTERN = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra',
           'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
ANIMALS = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake', 'horse', 'goat',
           'monkey', 'rooster', 'dog', 'pig']

ETSY_P = re.compile(
    r'\n[ \t]*<p>The Built by Josh Studio Etsy storefront has additional individual prints and other '
    r'studio work\. <a href="https://www\.etsy\.com/shop/BuiltByJoshStudio" target="_blank" '
    r'rel="noopener">Visit the Etsy shop →</a></p>')
# Whole block when the Etsy paragraph is its only content (blank line before it included).
ETSY_ONLY_BLOCK = re.compile(
    r'\n\n[ \t]*<div class="etsy-secondary">\n[ \t]*<div class="etsy-secondary-label">Looking for '
    r'something different\?</div>\n[ \t]*<p>The Built by Josh Studio Etsy storefront[^\n]*</p>\n'
    r'[ \t]*</div>')
SECONDARY_CSS_LINE = re.compile(r'\n[ \t]*\.etsy-secondary[^\n]*')
SECONDARY_COMMENT = re.compile(r'\n[ \t]*/\* Secondary Etsy reference block[^\n]*\*/')
PAUSE_CSS_LINE = re.compile(r'\n[ \t]*\.etsy-secondary \.etsy-pause-note[^\n]*')
NOTICE_CSS_LINE = re.compile(r'\n[ \t]*\.etsy-notice \{\{? padding: 1\.2rem 1\.4rem; \}\}?')

FAQ_DROP = ' The Built by Josh Studio Etsy storefront carries other studio work but does not sell the full Collection bundles.'

COMMON = [
    ('no Etsy account required', 'no account required'),
    (FAQ_DROP, ''),
]
# zodiac-landscapes.html has no "Who buys" Etsy bullet, so this one is not required to match
AUDIENCE = [
    ('Etsy, Printful, and Redbubble print-on-demand sellers', 'Printful, Redbubble, and other print-on-demand sellers'),
]
REVIEWS = [
    ('Reviews from the Built by Josh Studio Etsy shop', 'Verified Buyer Reviews'),
    ('Etsy buyer · ', 'Verified buyer · '),
]
WESTERN_PRICING = [
    (' The Built by Josh Studio Etsy shop carries individual prints and other studio work — not this bundle as packaged here.', ''),
]
CHINESE_HUB = [
    (' The Built by Josh Studio Etsy shop carries individual prints and other studio work, not these bundles.', ''),
    ('; the Etsy shop carries individual prints and other studio work.', '.'),
    (' The Built by Josh Studio Etsy shop carries individual prints and other studio work — the bundles as packaged here are sold on this site.', ''),
    ('Multiple prints per bundle Visit Etsy for current sales and promotions.', 'Multiple prints per bundle'),
    ('Reviews from our Etsy shop', 'Verified Buyer Reviews'),
    ('Etsy buyer · ', 'Verified buyer · '),
    ('etsy-cta-card', 'animal-cta-card'),
    ('btn-etsy', 'btn-cta'),
]


def read(path):
    with open(path, encoding='utf-8', newline='') as fh:
        return fh.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)


HITS = {}


def literal(text, pairs, path):
    """Replace each pair; on a not-yet-scrubbed file every pair must match at least once."""
    fresh = bool(leftover(text))
    for old, new in pairs:
        n = text.count(old)
        assert n or not fresh, (path, old)
        HITS[(path, old)] = n
        text = text.replace(old, new)
    return text


def secondary_block(text, path, keep_redbubble):
    """Strip the Etsy paragraph; keep the block (renamed) only when Redbubble remains."""
    if keep_redbubble:
        text = ETSY_P.sub('', text)
        text = PAUSE_CSS_LINE.sub('', text)
        text = SECONDARY_COMMENT.sub(
            '\n    /* Secondary print-on-demand link (muted, courtesy link only — not a competing sales path) */',
            text)
        text = text.replace('etsy-secondary-label', 'alt-shop-label').replace('etsy-secondary', 'alt-shop')
        assert 'class="alt-shop"' in text and 'Redbubble' in text, path
    else:
        text = ETSY_ONLY_BLOCK.sub('', text)
        text = SECONDARY_COMMENT.sub('', text)
        text = SECONDARY_CSS_LINE.sub('', text)
    assert 'etsy-secondary' not in text and 'Visit the Etsy shop' not in text, path
    return text


def scrub_page(path, kind):
    text = before = read(path)
    if kind != 'chinese-hub':  # the hub's FAQ uses its own wording (CHINESE_HUB)
        text = literal(text, COMMON, path)
        text = text.replace(*AUDIENCE[0])
    if kind == 'western':
        text = literal(text, REVIEWS, path)
        text = text.replace(*WESTERN_PRICING[0])  # the stale generator has its own pricing line (see main)
    if kind == 'chinese-hub':
        text = literal(text, CHINESE_HUB, path)
    else:
        text = secondary_block(text, path, keep_redbubble=(kind == 'western'))
    text = NOTICE_CSS_LINE.sub('', text)
    assert 'class="etsy-notice' not in text, path
    return before, text


ALLOWED_LEFT = re.compile(
    r'"https://tynkrtoolsandco\.etsy\.com"|"https://www\.etsy\.com/shop/BuiltByJoshStudio"'
    r'|<li><a href="https://www\.etsy\.com/shop/BuiltByJoshStudio" target="_blank" rel="noopener">Etsy</a></li>')


def leftover(text):
    """Etsy mentions still present once the global sameAs + footer link are set aside."""
    return [l for l in text.splitlines() if re.search('etsy', ALLOWED_LEFT.sub('', l), re.I)
            # prior-structure history in the landscapes generator docstring stays
            and 'Etsy-primary' not in l and 'landscape Etsy buttons removed' not in l]


def main():
    dry = '--dry' in sys.argv
    jobs = []
    for s in WESTERN:
        jobs.append((f'collections/{s}-zodiac-art.html', 'western'))
        jobs.append((f'collections/{s}-zodiac-realms.html', 'realms'))
    for a in ANIMALS:
        jobs.append((f'collections/{a}-chinese-zodiac-art.html', 'animal'))
    jobs += [('collections/chinese-zodiac-art.html', 'chinese-hub'),
             ('collections/chinese-zodiac-realms.html', 'single'),
             ('collections/zodiac-landscapes.html', 'single')]
    on_disk = {os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, 'collections', '*zodiac*.html'))}
    assert on_disk == {j[0] for j in jobs}, sorted(on_disk ^ {j[0] for j in jobs})

    # Generators: same template text, CSS braces doubled for str.format/f-strings.
    gens = [('tools/build_western_signs_page.py', 'western'),
            ('tools/build_realm_page_master.py', 'realms'),
            ('tools/build_chinese_animal_pages.py', 'animal'),
            ('tools/build_chinese_realms_page.py', 'single'),
            ('tools/build_zodiac_landscapes_page.py', 'single')]

    changed = 0
    for rel, kind in jobs + gens:
        path = os.path.join(ROOT, rel)
        before, text = scrub_page(path, kind)
        if rel == 'tools/build_western_signs_page.py':
            text = re.sub(r",?\s*etsy_section_url='https://www\.etsy\.com/shop/BuiltByJoshStudio[^']*',?",
                          lambda m: ',' if m.group(0).endswith(',') else '', text)
            text = literal(text, [(' Visit Etsy for current sales and promotions (Etsy shop currently in '
                                   'temporary verification pause — see notice above).', '')], rel)
        if rel == 'tools/build_chinese_realms_page.py':
            text = literal(text, [('& POD Trust block, secondary Etsy block, 12 animal',
                                   '& POD Trust block, 12 animal')], rel)
        if rel == 'tools/build_zodiac_landscapes_page.py':
            text = literal(text, [('LS-direct sidebar + final CTA, License & POD Trust block, secondary Etsy\nblock, ',
                                   'LS-direct sidebar + final CTA, License & POD Trust block,\n')], rel)
        rest = leftover(text)
        assert not rest, (rel, rest)
        if text != before:
            changed += 1
            if not dry:
                write(path, text)
        print(f'{"would change" if dry else "changed"} {rel}' if text != before else f'unchanged {rel}')
        if text != before:
            n_before, n_after = len(re.findall('etsy', before, re.I)), len(re.findall('etsy', text, re.I))
            print(f'    etsy mentions {n_before} -> {n_after}')

    tpl = os.path.join(ROOT, 'templates/collection-page-master.md')
    t = before = read(tpl)
    old_spec = re.compile(r'Secondary Etsy reference \(styled smaller/quieter, NOT a competing CTA\):\n'
                          r'(?:  [^\n]*\n)+?(?=```)')
    t = old_spec.sub(
        'Secondary print-on-demand link (Western Signs per-sign pages only; styled\n'
        'smaller/quieter, NOT a competing CTA). No Etsy link on Collection pages —\n'
        'the Lemon Squeezy overlay is the only purchase action:\n'
        '  Label: Looking for something different?\n'
        '  Body: Prefer it already printed? The <Sign> celestial artwork is available\n'
        '        on posters, canvas prints, apparel, and more at the studio’s\n'
        '        Redbubble shop. See <Sign> on Redbubble →\n', t)
    assert 'Secondary Etsy reference' not in t and 'verification pause' not in t, tpl
    if t != before:
        changed += 1
        if not dry:
            write(tpl, t)
    print(('unchanged' if t == before else 'would change' if dry else 'changed') + ' templates/collection-page-master.md')
    print(f'{changed} file(s) {"would change" if dry else "changed"}')


if __name__ == '__main__':
    main()
