"""blog_rss_build.py -- build feed.xml (RSS 2.0) for the Studio Blog from the blog/*.html posts.

Source of truth is each post's own markup: <title>/H1, meta description, canonical URL, the Article
JSON-LD datePublished/dateModified/author, and the section the post sits under on blog.html (Templates,
Learning, Projects = the studio kitchen, Money & Business, Tabletop & RPG) -> <category>. The meta-refresh
redirect stub (no Article node) is skipped. Items are newest-first; all posts are included.

Usage:
  python tools/blog_rss_build.py [--root <repo>] [--apply]     (dry run by default: prints the item list)

Run with --apply after publishing or editing a post; commit feed.xml with the post. Pages carry
<link rel="alternate" type="application/rss+xml" href="https://builtbyjoshstudio.com/feed.xml">.
Output is UTF-8 + CRLF (site convention). ASCII-only source on purpose.
"""
import argparse, datetime, html, json, re, subprocess, sys
from email.utils import format_datetime
from pathlib import Path

SITE = "https://builtbyjoshstudio.com/"
FEED_URL = SITE + "feed.xml"
CHANNEL_TITLE = "The Studio Blog \u2014 Built by Josh Studio"
CHANNEL_LINK = SITE + "blog.html"
CHANNEL_DESC = ("Template walkthroughs, personal-finance and creator-business explainers, free-tool build notes, "
                "food essays from the studio kitchen, and tabletop notes \u2014 from Built by Josh Studio LLC "
                "(Tynkr Tools & Co).")
CATEGORY = {"Templates": "Templates & Workbooks", "Learning": "Personal Finance & Creator Business",
            "Projects": "Kitchen & Cooking", "Money & Business": "Money & Business Tools", "Tabletop & RPG": "Tabletop & RPG"}
RX_LD = re.compile(r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)


def norm(t):
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def article(s):
    for m in RX_LD.finditer(s):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        for n in walk(d):
            if n.get("@type") in ("Article", "BlogPosting", "NewsArticle") and n.get("datePublished"):
                return n
    return None


def to_dt(v):
    v = v.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
        return datetime.datetime.strptime(v, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    v = v.replace("Z", "+00:00")
    dt = datetime.datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def sections(root):
    s = (root / "blog.html").read_bytes().decode("utf-8")
    body = s[s.find("<body"):]
    cur = None; out = {}
    for part in re.split(r"(<h2[^>]*>.*?</h2>)", body):
        if part.startswith("<h2"):
            cur = norm(re.sub(r"<[^>]+>", "", part)); continue
        for h in re.findall(r'href="(blog/[^"#]+)"', part):
            out.setdefault(h, cur)
    return out


def esc(t):
    return html.escape(t, quote=False)


def build(root):
    secs = sections(root)
    files = subprocess.run(["git", "-C", str(root), "ls-files", "blog/*.html"], capture_output=True, text=True).stdout.split()
    items = []
    for rel in files:
        s = (root / rel).read_bytes().decode("utf-8")
        a = article(s)
        if not a:
            continue
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', s).group(1)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        title = norm(re.sub(r"<[^>]+>", " ", h1.group(1))) if h1 else norm(a.get("headline", ""))
        dm = re.search(r'<meta name="description" content="([^"]*)"', s)
        desc = norm(dm.group(1)) if dm else norm(a.get("description", ""))
        au = a.get("author"); au = au.get("name") if isinstance(au, dict) else (au or "Josh")
        pub = to_dt(a["datePublished"])
        mod = to_dt(a["dateModified"]) if a.get("dateModified") else pub
        cat = CATEGORY.get(secs.get(rel, ""), None)
        items.append((pub, mod, title, canon, desc, au, cat))
    items.sort(key=lambda r: (r[0], r[3]), reverse=True)
    last_build = max(max(r[0], r[1]) for r in items)
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/">',
         '<channel>',
         '  <title>%s</title>' % esc(CHANNEL_TITLE),
         '  <link>%s</link>' % CHANNEL_LINK,
         '  <atom:link href="%s" rel="self" type="application/rss+xml" />' % FEED_URL,
         '  <description>%s</description>' % esc(CHANNEL_DESC),
         '  <language>en-us</language>',
         '  <copyright>Built by Josh Studio LLC</copyright>',
         '  <lastBuildDate>%s</lastBuildDate>' % format_datetime(last_build),
         '  <generator>tools/blog_rss_build.py</generator>']
    for pub, mod, title, canon, desc, au, cat in items:
        L.append('  <item>')
        L.append('    <title>%s</title>' % esc(title))
        L.append('    <link>%s</link>' % canon)
        L.append('    <guid isPermaLink="true">%s</guid>' % canon)
        L.append('    <pubDate>%s</pubDate>' % format_datetime(pub))
        L.append('    <dc:creator>%s</dc:creator>' % esc(au))
        if cat:
            L.append('    <category>%s</category>' % esc(cat))
        L.append('    <description>%s</description>' % esc(desc))
        L.append('  </item>')
    L += ['</channel>', '</rss>', '']
    return "\r\n".join(L).encode("utf-8"), items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    xml, items = build(root)
    sys.stdout.reconfigure(encoding="utf-8")
    for pub, mod, title, canon, desc, au, cat in items:
        print(pub.date(), "|", (cat or "-")[:24].ljust(24), "|", title[:80])
    print("items:", len(items), " bytes:", len(xml))
    out = root / "feed.xml"
    if a.apply:
        out.write_bytes(xml)
        print("WROTE", out)
    else:
        print("dry run (use --apply)")


if __name__ == "__main__":
    main()
