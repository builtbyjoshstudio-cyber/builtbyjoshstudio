"""Identity hygiene + site-wide Organization JSON-LD.

Part 1 — strips founder full name + city-level identity leaks.
Part 2 — injects a single Organization schema block into every page's <head>.

Idempotent: re-runs are safe (uses '@id' URL as the presence marker for the
schema, and the specific old-string match for the about.html copy).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── PART 2 — Organization schema (exact block from the brief) ──────────
ORG_SCHEMA_ID = 'https://builtbyjoshstudio.com/#organization'
ORG_SCHEMA = '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://builtbyjoshstudio.com/#organization",
  "name": "Built by Josh Studio LLC",
  "alternateName": ["BBJ Studio", "Built By Josh Studio"],
  "legalName": "Built by Josh Studio LLC",
  "url": "https://builtbyjoshstudio.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://builtbyjoshstudio.com/images/logo/logo.webp",
    "width": 512,
    "height": 512
  },
  "image": "https://builtbyjoshstudio.com/images/logo/logo.webp",
  "description": "Built by Josh Studio LLC is a Kansas-based independent creative studio that publishes original zodiac digital art under the Built By Josh Studio brand and Notion OS templates and personal finance workbooks under the Tynkr Tools & Co brand. All products are digital, instant-download, and built by a single founder.",
  "founder": {
    "@type": "Person",
    "name": "Josh"
  },
  "foundingDate": "2026-05-13",
  "foundingLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressRegion": "KS",
      "addressCountry": "US"
    }
  },
  "address": {
    "@type": "PostalAddress",
    "addressRegion": "KS",
    "addressCountry": "US"
  },
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
    {
      "@type": "Brand",
      "name": "Built By Josh Studio",
      "description": "Original digital zodiac art bundles — Western signs, Chinese signs, zodiac landscapes, and zodiac realms — sold as print-ready, POD-licensed digital downloads."
    },
    {
      "@type": "Brand",
      "name": "Tynkr Tools & Co",
      "description": "Notion OS templates and Excel and Google Sheets workbooks for creators, solopreneurs, and personal-finance milestones."
    }
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "josh@builtbyjoshstudio.com",
    "contactType": "customer support",
    "areaServed": "Worldwide",
    "availableLanguage": "English"
  },
  "sameAs": [
    "https://linktr.ee/builtbyjoshstudio",
    "https://tynkrtoolsco.substack.com/",
    "https://www.youtube.com/@TalesofInkShadowsStudio",
    "https://tynkrtoolsandco.etsy.com",
    "https://www.etsy.com/shop/BuiltByJoshStudio"
  ],
  "identifier": [
    {
      "@type": "PropertyValue",
      "propertyID": "Kansas Business ID",
      "value": "10076138"
    }
  ]
}
</script>'''


# ── helpers ────────────────────────────────────────────────────────────
def edit_in_place(path: Path, transforms: list) -> dict:
    """Apply (old, new) replacements; return {'pattern': hits} per pair."""
    text = path.read_text(encoding='utf-8')
    summary = {}
    for label, old, new in transforms:
        before = text.count(old) if isinstance(old, str) else len(re.findall(old, text))
        if isinstance(old, str):
            text = text.replace(old, new)
        else:
            text = old.sub(new, text)
        summary[label] = before
    path.write_text(text, encoding='utf-8')
    return summary


# ── PART 1 — file-specific edits ───────────────────────────────────────

# 1.1 + 1.3 — about.html
about = ROOT / 'about.html'
s = edit_in_place(about, [
    ('1.1 founder_line',
     'Built by Josh Studio LLC is a Kansas limited liability company that operates the Tynkr Tools &amp; Co and Built By Josh Studio brands. Founded in 2026 by Joshua Tran in Topeka, Kansas.',
     'Built by Josh Studio LLC is a Kansas limited liability company that operates the Tynkr Tools &amp; Co and Built By Josh Studio brands. The LLC was formed in 2026 and is based in Kansas.'),
    ('1.3 founded_2025',
     'Built By Josh Studio is the parent studio I founded in 2025',
     'Built By Josh Studio is the parent studio I founded in 2026'),
])
print(f'about.html  Part-1 specifics: {s}')

# 1.6 — index.html Person schema: drop givenName + familyName entirely.
# `"name": "Josh"` is already correct per the brief.
idx = ROOT / 'index.html'
s = edit_in_place(idx, [
    ('1.6 person_schema_strip',
     '    "givenName": "Joshua",\n    "familyName": "Tran",\n',
     ''),
])
print(f'index.html  Part-1 specifics: {s}')

# 1.5 — refunds / terms / privacy: drop "in Topeka," (state-level only)
for fname in ['refunds.html', 'terms.html', 'privacy.html']:
    p = ROOT / fname
    s = edit_in_place(p, [
        ('1.5 principal_office',
         'with its principal office in Topeka, Kansas.',
         'with its principal office in Kansas.'),
    ])
    print(f'{fname:<14} Part-1 specifics: {s}')

# 1.5 — pho blog post (visible body copy)
pho = ROOT / 'blog' / 'how-i-make-pho-two-day-method.html'
s = edit_in_place(pho, [
    ('1.5 pho_kitchen',
     'in my kitchen in Topeka, Kansas in 2026',
     'in my kitchen in Kansas in 2026'),
])
print(f'blog/pho    Part-1 specifics: {s}')


# ── PART 1.4 + PART 2 — site-wide sweep over all .html files ──────────
meta_keywords_re = re.compile(r'^[ \t]*<meta\s+name="keywords"[^\n]*\n', re.MULTILINE)
keywords_stripped = 0
schema_injected = 0
schema_skipped = 0
files_scanned = 0

for html_path in sorted(ROOT.rglob('*.html')):
    # Skip dotfile dirs (.claude, .netlify, .github, .git etc.)
    if any(part.startswith('.') for part in html_path.relative_to(ROOT).parts):
        continue
    files_scanned += 1
    text = html_path.read_text(encoding='utf-8')
    original = text

    # 1.4 — delete meta keywords
    text, n = meta_keywords_re.subn('', text)
    keywords_stripped += n

    # Part 2 — inject Organization schema right before </head>
    if ORG_SCHEMA_ID not in text:
        if '</head>' in text:
            # Indent schema 2 spaces to match other head children, with a
            # blank-line separator above for readability.
            indented = '  ' + ORG_SCHEMA.replace('\n', '\n  ')
            text = text.replace('</head>', indented + '\n</head>', 1)
            schema_injected += 1
        else:
            print(f'  !! {html_path.relative_to(ROOT)}: no </head> found, skipping schema injection')
    else:
        schema_skipped += 1

    if text != original:
        html_path.write_text(text, encoding='utf-8')

print()
print(f'Site-wide sweep:')
print(f'  HTML files scanned:        {files_scanned}')
print(f'  Meta keywords stripped:    {keywords_stripped}')
print(f'  Organization schema added: {schema_injected}')
print(f'  Already had schema:        {schema_skipped}')
