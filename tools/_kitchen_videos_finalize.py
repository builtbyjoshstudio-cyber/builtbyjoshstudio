# _kitchen_videos_finalize.py -- gate for kitchen-videos.html.
#   default : structural checks (EOLs, JSON-LD, needles, headings, assets, leaks)
#   --live  : ALSO verify every embedded/linked video against YouTube -- public,
#             and the schema's duration/title/uploadDate match reality.
# RULE: never push this page without a clean `--live` run. Video metadata drifts
# (the bulgogi cut was retitled days after publish) and staged cuts start private.
import io, json, os, re, sys, urllib.request

ROOT = r"C:\Users\jotra\builtbyjoshstudio-workspace\builtbyjoshstudio"
PAGE = os.path.join(ROOT, "kitchen-videos.html")

# video id -> (role, expected ISO duration or None to skip)
EXPECTED = {
    "xp9sr28cHhs": ("guacamole 3-min version", "PT3M50S"),
    "nXyCGLQLA3M": ("guacamole real-time", "PT10M50S"),  # 10:50 per YouTube Studio
    "8zcTjBWd93Y": ("sausage hash 15-min cut", "PT15M"),
    "r9uiTmLPR78": ("sausage hash uncut", None),
    "Mw-CTeEvBp4": ("bulgogi 15-min cut", "PT15M"),
    "uxaviluHHm4": ("bulgogi uncut", None),
}

def iso(seconds):
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    out = "PT"
    if h: out += "%dH" % h
    if m: out += "%dM" % m
    if s: out += "%dS" % s
    return out

raw = io.open(PAGE, "rb").read()
text = raw.decode("utf-8")

# 1. CRLF purity (site convention).
body = text.replace("\r\n", "\n").replace("\n", "\r\n")
if body.encode("utf-8") != raw:
    io.open(PAGE, "wb").write(body.encode("utf-8"))
    print("normalized to CRLF")
    raw = io.open(PAGE, "rb").read()
    text = raw.decode("utf-8")
lone_lf = len(re.findall(rb"(?<!\r)\n", raw))
print("CRLF lines: %d | lone LFs: %d" % (raw.count(b"\r\n"), lone_lf))
assert lone_lf == 0, "mixed EOLs"

# 2. JSON-LD parses; ItemList shape is coherent.
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
types, schema = [], {}
for b in blocks:
    data = json.loads(b)
    types.append(data.get("@type"))
    if data.get("@type") == "ItemList":
        items = data["itemListElement"]
        assert data["numberOfItems"] == len(items), "numberOfItems != items"
        for i, li in enumerate(items, 1):
            assert li["position"] == i, ("positions must be 1..n in order", li["position"], i)
            v = li["item"]
            assert v["@type"] == "VideoObject"
            assert v["publisher"]["@id"] == "https://builtbyjoshstudio.com/#organization"
            assert v["thumbnailUrl"].startswith("https://builtbyjoshstudio.com/images/")
            vid = v["embedUrl"].rsplit("/", 1)[-1]
            schema[vid] = v
print("JSON-LD %s | ItemList videos: %d" % (types, len(schema)))
assert types == ["BreadcrumbList", "Organization", "ItemList"], types

# 3. Every schema video is embedded on the page; every facade has schema.
facades = re.findall(r'data-ytid="([\w-]{11})"', text)
assert sorted(facades) == sorted(schema), ("facade/schema mismatch", facades, list(schema))
for vid in facades:
    assert EXPECTED[vid][1] is not None, ("an uncut/real-time video must not be embedded", vid)

# 4. Linked-but-not-embedded videos (the real-time cooks).
linked = set(re.findall(r'youtu\.be/([\w-]{11})', text))
for vid in linked:
    assert vid in EXPECTED, ("unknown linked video", vid)
print("embedded: %d | linked-out: %d" % (len(facades), len(linked)))

# 5. Structure + habit gates.
heads = re.findall(r'<h([1-6])[ >]', text)
assert heads[0] == '1' and heads.count('1') == 1 and set(heads) <= {'1', '2'}, heads
assert text.count('<script src="/js/lite-yt.js" defer></script>') == 1
assert text.count('class="yt-facade-poster"') == len(facades)
assert "UPGRADE35" not in text and "Built By Josh Studio" not in text
assert "joshcooksfood" not in text and "jotran18" not in text
for m in set(re.findall(r'(?:src|href)="(/(?:images|css|js)/[^"]+)"', text)):
    assert os.path.exists(os.path.join(ROOT, m.lstrip("/").replace("/", os.sep))), ("missing asset", m)
print("headings %s | assets ok" % "".join(heads))

# 6. Live verification (required before any push).
if "--live" in sys.argv:
    print("\n-- live YouTube check --")
    bad = []
    for vid, (role, want) in EXPECTED.items():
        if vid not in facades and vid not in linked:
            continue
        req = urllib.request.Request("https://www.youtube.com/watch?v=" + vid,
                                     headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        status = re.search(r'"playabilityStatus":\{"status":"([A-Z_]+)"', h)
        status = status.group(1) if status else "UNKNOWN"
        secs = re.search(r'"lengthSeconds":"(\d+)"', h)
        title = re.search(r'<meta name="title" content="([^"]*)"', h)
        title = title.group(1) if title else ""
        if status != "OK":
            bad.append("%s (%s): NOT PUBLIC -- %s" % (vid, role, status))
            continue
        real = iso(int(secs.group(1))) if secs else "?"
        line = "  %s %-26s %-10s %s" % (vid, role, real, title[:52])
        if want and real != want:
            bad.append("%s (%s): schema duration %s != live %s" % (vid, role, want, real))
        if vid in schema and schema[vid]["name"] != title:
            bad.append("%s (%s): schema name != live title\n      schema: %s\n      live:   %s"
                       % (vid, role, schema[vid]["name"], title))
        pub = re.search(r'"publishDate":"([^"]+)"', h)
        if vid in schema and pub and schema[vid]["uploadDate"] != pub.group(1):
            bad.append("%s (%s): schema uploadDate %s != live publishDate %s"
                       % (vid, role, schema[vid]["uploadDate"], pub.group(1)))
        print(line)
    if bad:
        print("\nLIVE CHECK FAILED -- do NOT push:")
        for b in bad:
            print("  * " + b)
        sys.exit(1)
    print("live check clean")

print("\nALL GATES PASS")
