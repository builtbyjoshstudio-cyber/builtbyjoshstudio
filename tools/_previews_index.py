# _previews_index.py -- make both chapter previews indexable, and bring the Overlayed
# Echoes sample inside the KDP Select excerpt allowance first (Josh approved, 2026-09-14).
#
# Measured against the published manuscripts:
#   Overlayed Echoes  sample Ch.1+2 = 8,929 words / story 89,218 = 10.01%  -> 8 words OVER
#                     trimmed to Ch.1 = 3,632 words              =  4.07%
#   Ebonspire         sample Ch.1  ~2,400-3,700 / 73,832          = ~3-5%   -> fine as-is
#
# The cut: from the midpoint CTA through the end of Chapter Two. Removing only Chapter
# Two would stack the midpoint CTA directly on top of the existing "The sample ends here"
# section -- two buy buttons back to back. Chapter One now flows straight into that
# end-of-sample section. The midpoint CTA's CSS becomes orphaned and is removed with it.
#
# Every link on the site that promised "the first two chapters" is updated to match.
# Dry-run by default; --apply writes. Per-file EOL preserved (the preview is LF-authored).
import glob, io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OE = os.path.join(ROOT, "overlayed-echoes-preview.html")
EB = os.path.join(ROOT, "ebonspire-chronicles-preview.html")

NOINDEX = '<meta name="robots" content="noindex,follow">'
INDEXABLE = '<meta name="robots" content="max-image-preview:large, max-snippet:-1, max-video-preview:-1">'

# (old, new, expected count)
OE_TEXT = [
    (NOINDEX, INDEXABLE, 1),
    ("Free Sample (Ch. 1–2)", "Free Sample (Ch. 1)", 3),
    ("Read the first two chapters of Overlayed Echoes free", "Read the first chapter of Overlayed Echoes free", 4),
    ("Free Sample (Chapters 1–2)", "Free Sample (Chapter One)", 1),
    ("This page offers the first two chapters", "This page offers the first chapter", 1),
    ("Read the first two chapters below, on the house.", "Read the first chapter below, on the house.", 1),
    ("Sample is Chapters 1 &amp; 2 &mdash;", "Sample is Chapter One &mdash;", 1),
]

MIDPOINT_CSS = (
    "  /* Mid-point CTA — end of Chapter 1 (echoes the end-block visual language) */\n"
    "  .preview-midpoint-cta {\n"
    "    max-width: 600px; margin: 3.5rem auto 1rem; padding: 2rem 1.5rem; text-align: center;\n"
    "    background: var(--paper-card); border: 1px solid var(--rule); border-radius: 8px;\n"
    "  }\n"
    "  .preview-midpoint-cta .midpoint-line { color: var(--muted); font-size: 1.02rem; margin: 0 0 1.25rem; }\n"
    "  .reader .preview-midpoint-cta .midpoint-line::first-letter { font-size: inherit; float: none; color: inherit; font-weight: inherit; padding: 0; }\n"
)

LINK_OLD = "Read the first two chapters free →"
LINK_NEW = "Read Chapter One free →"
BOOKS_OLD = "Read Chapters 1 &amp; 2 free →"


def rw(p):
    raw = io.open(p, "rb").read()
    crlf = raw.count(b"\r\n") > 0
    t = raw.decode("utf-8")
    return (t.replace("\r\n", "\n") if crlf else t), crlf


def save(p, t, crlf, apply):
    if apply:
        io.open(p, "wb").write((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


def run(apply):
    # ---- 1. Overlayed Echoes preview ------------------------------------------
    t, crlf = rw(OE)
    if "Chapter Two: Rolling the Heroes" in t:
        for old, new, n in OE_TEXT:
            got = t.count(old)
            assert got == n, ("OE count mismatch", old[:60], got, n)
            t = t.replace(old, new)

        start = t.index('<div class="preview-midpoint-cta">')
        end = t.index("\n  </main>")
        cut = t[start:end]
        assert "Chapter Two: Rolling the Heroes" in cut and "Curtain rises on Act One." in cut
        assert cut.count("<div") == cut.count("</div>"), ("unbalanced divs in the cut", cut.count("<div"), cut.count("</div>"))
        assert "Curtain up. The fellowship arrives." not in cut  # Chapter One's ending survives
        t = t[:start].rstrip() + "\n" + t[end:]

        assert t.count(MIDPOINT_CSS) == 1, "midpoint CSS block not found exactly once"
        t = t.replace(MIDPOINT_CSS, "")

        assert "Chapter Two" not in t and "preview-midpoint-cta" not in t
        assert "Chapter One: The Setup" in t and "The sample ends here" in t
        assert t.count("</main>") == 1 and "noindex" not in t
        save(OE, t, crlf, apply)
        print("OE preview: Chapter Two + midpoint CTA removed (%d chars), copy updated, now indexable" % len(cut))
    else:
        print("OE preview: already trimmed")

    # ---- 2. Ebonspire preview: indexable ---------------------------------------
    t, crlf = rw(EB)
    if NOINDEX in t:
        assert t.count(NOINDEX) == 1
        save(EB, t.replace(NOINDEX, INDEXABLE), crlf, apply)
        print("Ebonspire preview: now indexable")
    else:
        print("Ebonspire preview: already indexable")

    # ---- 3. every link that promised two chapters -------------------------------
    links = 0
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if "graphify-out" in f or os.path.abspath(f) == os.path.abspath(OE):
            continue
        t, crlf = rw(f)
        n = t.count(LINK_OLD) + t.count(BOOKS_OLD)
        if not n:
            continue
        t = t.replace(LINK_OLD, LINK_NEW).replace(BOOKS_OLD, LINK_NEW)
        save(f, t, crlf, apply)
        links += n
    print("inbound links re-labelled: %d" % links)

    # ---- 4. sitemap: both previews back in ------------------------------------
    sm = os.path.join(ROOT, "sitemap.xml")
    t, crlf = rw(sm)
    added = 0
    for slug in ("overlayed-echoes-preview.html", "ebonspire-chronicles-preview.html"):
        url = "https://builtbyjoshstudio.com/" + slug
        if url in t:
            continue
        m = re.search(r"(  <url>\n    <loc>https://builtbyjoshstudio\.com/books\.html</loc>\n.*?\n  </url>\n)", t, re.S)
        assert m, "books.html sitemap anchor not found"
        entry = ("  <url>\n    <loc>%s</loc>\n    <lastmod>2026-09-14</lastmod>\n"
                 "    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n" % url)
        t = t[:m.end(1)] + entry + t[m.end(1):]
        added += 1
    save(sm, t, crlf, apply)
    print("sitemap entries added: %d (urls now %d)" % (added, t.count("<url>")))
    print("APPLIED" if apply else "(dry-run)")


if __name__ == "__main__":
    run("--apply" in sys.argv)
