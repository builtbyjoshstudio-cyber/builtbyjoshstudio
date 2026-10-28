# cooking_strip_sync.py -- keep the /cooking/ hub's "Watch the cooks" strip on the 3 NEWEST
# kitchen videos (Josh, 2026-10-27: "always show the most recent 3").
# Source of truth = the ItemList on kitchen-videos.html (newest first, position 1..n): the top 3
# items give the order, the poster (thumbnailUrl) and, via each entry's <h2>, the card title.
# The alt text and the "short · long" line are hand-written per video in CARD below -- add a row
# whenever a video is added to kitchen-videos (step of the VIDEO RECIPE); the script asserts one
# exists for each of the top 3. _kitchen_videos_finalize.py imports build() and fails the gate if
# the strip is stale, so a new video cannot ship without it.
# Dry-run by default (prints the diff state); --apply writes. CRLF preserved. Idempotent.
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, "kitchen-videos.html")
HUB = os.path.join(ROOT, "cooking", "index.html")
SITE = "https://builtbyjoshstudio.com"

# video id -> (poster alt text, card line "short version · long version")
CARD = {
    "qhqCfAxh8Vw": ("Sugar cookie cups in a mini muffin pan, with rainbow sprinkles",
                    "4-min version · 10-min full bake"),
    "VR1muzTHaU4": ("Golden chicken stock in the pot",
                    "11-min cut · 35-min uncut"),
    "dFLWiZrQSmQ": ("Bite-sized chocolate chip cookie cups with flaky salt, fresh out of a mini muffin pan",
                    "6-min version · 11-min real-time bake"),
    "qqurZXTPZMw": ("A golden rotisserie chicken in its tray, ready to break down",
                    "5-min version · 10-min real time"),
    "BvA6dtVpQYw": ("Chocolate chip cookie dough with mini chips in a mixing bowl",
                    "Under-3-min version · 9-min full bake"),
}

OPEN = '      <div class="ck-videos">\n'
BLOCK_RX = re.compile(r'      <div class="ck-videos">\n.*?\n      </div>\n', re.S)

CARD_HTML = """        <a class="ck-video" href="/kitchen-videos.html">
          <img src="%s" width="1280" height="720" loading="lazy" decoding="async" alt="%s" />
          <div class="ck-video-body"><strong>%s</strong><span>%s</span></div>
        </a>
"""


def read(path):
    raw = io.open(path, "rb").read().decode("utf-8")
    return raw, raw.replace("\r\n", "\n")


def newest_three(videos):
    s = videos.index('"@type": "ItemList"')
    e = videos.index("</script>", s)
    data = json.loads(videos[videos.rindex("{", 0, s):e])
    items = sorted(data["itemListElement"], key=lambda li: li["position"])
    out = []
    for li in items[:3]:
        v = li["item"]
        vid = v["embedUrl"].rsplit("/", 1)[-1]
        poster = v["thumbnailUrl"]
        assert poster.startswith(SITE + "/images/"), ("poster not self-hosted", vid, poster)
        art = videos.index('data-ytid="%s"' % vid)
        title = re.search(r"<h2>(.*?)</h2>", videos[art:]).group(1)
        assert vid in CARD, ("no CARD row for %s (%s) -- add its alt text + card line" % (vid, title))
        out.append((vid, poster[len(SITE):], title) + CARD[vid])
    return out


def build(root=ROOT):
    """Return (current hub text LF, expected hub text LF, raw hub text, the 3 cards)."""
    _, videos = read(os.path.join(root, "kitchen-videos.html"))
    raw, hub = read(os.path.join(root, "cooking", "index.html"))
    assert hub.count(OPEN) == 1 and len(BLOCK_RX.findall(hub)) == 1, "ck-videos block"
    cards = newest_three(videos)
    block = OPEN + "".join(CARD_HTML % (src, alt, title, line) for _, src, title, alt, line in cards) + "      </div>\n"
    return hub, BLOCK_RX.sub(lambda m: block, hub, count=1), raw, cards


def main():
    hub, want, raw, cards = build()
    for vid, src, title, _, line in cards:
        print("  %s  %-36s %s" % (vid, title, line))
    if hub == want:
        print("strip: up to date")
        return
    print("strip: STALE")
    if "--apply" in sys.argv:
        crlf = "\r\n" in raw
        io.open(HUB, "wb").write((want.replace("\n", "\r\n") if crlf else want).encode("utf-8"))
        print("APPLIED")
    else:
        print("(dry-run)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
