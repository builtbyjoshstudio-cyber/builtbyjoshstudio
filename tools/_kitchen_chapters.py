# _kitchen_chapters.py -- pull the LIVE chapter markers for the videos embedded on
# kitchen-videos.html straight from YouTube, so the page's chapter links and Clip
# schema come from ground truth rather than from the production kits (which drift).
# Prints a JSON blob; --save writes it next to this script for the builder to read.
import json, re, sys, urllib.request, os

sys.stdout.reconfigure(encoding="utf-8")

VIDS = ["pjQIfvQ46hY", "xp9sr28cHhs", "8zcTjBWd93Y", "Mw-CTeEvBp4"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kitchen_chapters.json")

TITLE_RX = re.compile(r'"title":\s*\{\s*"simpleText":\s*"((?:[^"\\]|\\.)*)"')
START_RX = re.compile(r'"startMillis":\s*"?(\d+)"?')
TIMEDESC_RX = re.compile(r'"timeDescription":\s*\{\s*"simpleText":\s*"([0-9:]+)"')


def hhmmss_to_secs(t):
    parts = [int(p) for p in t.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def fetch(vid):
    req = urllib.request.Request(
        "https://www.youtube.com/watch?v=" + vid,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def chapters(html):
    out = []
    for block in re.findall(r'"macroMarkersListItemRenderer":\s*\{(.{0,800}?)"onTap"', html, re.S):
        t = TITLE_RX.search(block)
        if not t:
            continue
        # decode YouTube's JSON string escapes properly -- NEVER unicode_escape,
        # which re-reads UTF-8 bytes as latin-1 and mojibakes "Cảm ơn"
        name = json.loads('"%s"' % t.group(1))
        secs = None
        m = START_RX.search(block)
        if m:
            secs = int(m.group(1)) // 1000
        else:
            m = TIMEDESC_RX.search(block)
            if m:
                secs = hhmmss_to_secs(m.group(1))
        if secs is None:
            continue
        out.append({"start": secs, "name": name})
    # de-dup (YouTube repeats the list) and order
    seen, uniq = set(), []
    for c in sorted(out, key=lambda c: c["start"]):
        key = (c["start"], c["name"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return uniq


def main():
    data = {}
    for vid in VIDS:
        h = fetch(vid)
        ch = chapters(h)
        length = re.search(r'"lengthSeconds":"(\d+)"', h)
        data[vid] = {"length": int(length.group(1)) if length else None, "chapters": ch}
        print("%s  %ss  %d chapters" % (vid, data[vid]["length"], len(ch)))
        for c in ch:
            print("    %5d  %s" % (c["start"], c["name"]))
    if "--save" in sys.argv:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print("\nsaved -> " + OUT)


if __name__ == "__main__":
    main()
