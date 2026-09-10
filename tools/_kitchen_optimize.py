# _kitchen_optimize.py -- views/clicks pass on kitchen-videos.html:
#   1. per-video chapter rows -- every chapter deep-links into the video at its
#      timestamp (more indexable phrasing on-page + many more click targets than
#      the single "watch" button)
#   2. Clip (hasPart) schema on each VideoObject, built from the same chapters,
#      so Google can surface Key Moments
#   3. a runtime badge on each facade poster (the YouTube CTR convention)
# Chapters come from tools/_kitchen_chapters.json (pulled LIVE from YouTube by
# _kitchen_chapters.py -- never from the production kits, which drift).
# Idempotent. Dry-run by default; --apply writes. CRLF preserved.
import html as htmllib
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "kitchen-videos.html")
CH = os.path.join(ROOT, "tools", "_kitchen_chapters.json")

LABEL = {
    "RrnRbxW0wrQ": "Conditioning a Wood Cutting Board",
    "pjQIfvQ46hY": "Oiling an End-Grain Board",
    "xp9sr28cHhs": "Chunky Guacamole",
    "8zcTjBWd93Y": "One-Skillet Spicy Sausage Hash",
    "Mw-CTeEvBp4": "Ground Beef Bulgogi Bowls",
}


def mmss(s):
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return ("%d:%02d:%02d" % (h, m, sec)) if h else ("%d:%02d" % (m, sec))


def chapter_nav(vid, chapters):
    rows = []
    for c in chapters:
        url = "https://www.youtube.com/watch?v=%s&amp;t=%ds" % (vid, c["start"])
        rows.append(
            '          <a href="%s" target="_blank" rel="noopener">'
            '<b>%s</b> %s</a>' % (url, mmss(c["start"]), htmllib.escape(c["name"]))
        )
    return (
        '        <nav class="vid-chapters" aria-label="Jump to a step in %s">\n'
        '          <span class="vid-chapters-label">Jump to a step</span>\n'
        % htmllib.escape(LABEL[vid])
        + "\n".join(rows)
        + "\n        </nav>\n"
    )


def clips(vid, chapters, length):
    out = []
    for i, c in enumerate(chapters):
        end = chapters[i + 1]["start"] if i + 1 < len(chapters) else length
        if end <= c["start"]:
            continue
        out.append({
            "@type": "Clip",
            "name": c["name"],
            "startOffset": c["start"],
            "endOffset": end,
            "url": "https://www.youtube.com/watch?v=%s&t=%ds" % (vid, c["start"]),
        })
    lines = json.dumps(out, ensure_ascii=False, indent=2).splitlines()
    # first line stays on the "hasPart": line; the rest are indented to the block
    body = lines[0] + "\n" + "\n".join("          " + ln for ln in lines[1:])
    return '          "hasPart": ' + body + ",\n"


def run(apply):
    data = json.load(io.open(CH, encoding="utf-8"))
    raw = io.open(PAGE, "rb").read()
    crlf = raw.count(b"\r\n") > 0
    text = raw.decode("utf-8")
    work = text.replace("\r\n", "\n") if crlf else text
    before = work

    n_nav = n_clip = n_badge = 0
    for vid, info in data.items():
        chapters, length = info["chapters"], info["length"]
        assert chapters and length, ("no chapters/length", vid)

        # ---- 1. chapter nav, inserted just before this item's </article> ----
        if 'aria-label="Jump to a step in %s"' % LABEL[vid] not in work:
            anchor = 'data-ytid="%s"' % vid
            i = work.index(anchor)
            j = work.index("</article>", i)
            work = work[:j] + chapter_nav(vid, chapters) + "      " + work[j:]
            n_nav += 1

        # ---- 2. Clip schema, after this video's duration line ----
        emb = '"embedUrl": "https://www.youtube.com/embed/%s"' % vid
        k = work.index(emb)
        blk_start = work.rindex('"@type": "VideoObject"', 0, k)
        if '"hasPart"' not in work[blk_start:k]:
            dur = re.search(r'^ *"duration": "[^"]+",\n', work[blk_start:k], re.M)
            assert dur, ("duration line not found", vid)
            at = blk_start + dur.end()
            work = work[:at] + clips(vid, chapters, length) + work[at:]
            n_clip += 1

        # ---- 3. runtime badge on the facade ----
        badge = '<span class="yt-facade-dur" aria-hidden="true">%s</span>' % mmss(length)
        i = work.index('data-ytid="%s"' % vid)
        facade_end = work.index("</div>", i)
        # scope the "already applied" test to THIS facade -- two videos share 15:00,
        # so a global substring test silently skips the second one
        if badge not in work[i:facade_end]:
            marker = '<span class="yt-facade-play" aria-hidden="true"></span>'
            m = work.index(marker, i)
            at = m + len(marker)
            work = work[:at] + "\n            " + badge + work[at:]
            n_badge += 1

    # ---- CSS (once) ----
    if ".vid-chapters {" not in work:
        anchor = "    /* ── CROSS-SELL ── */"
        assert anchor in work, "css anchor not found"
        css = (
            "    /* Chapter deep-links: extra entry points into each video */\n"
            "    .vid-chapters { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 8px; align-items: baseline; margin-top: 4px; padding-top: 16px; border-top: 1px solid var(--line); }\n"
            "    .vid-chapters-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-right: 4px; }\n"
            "    .vid-chapters a { font-size: .82rem; color: #5c4326; text-decoration: none; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px; transition: border-color .15s, color .15s; }\n"
            "    .vid-chapters a:hover, .vid-chapters a:focus-visible { color: var(--accent); border-color: var(--accent); }\n"
            "    .vid-chapters a b { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: .76rem; color: var(--accent); margin-right: 5px; }\n"
            "    .yt-facade-dur { position: absolute; right: 10px; bottom: 10px; background: rgba(20,14,8,.85); color: #fff; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; padding: 3px 7px; border-radius: 5px; letter-spacing: .02em; }\n\n"
        )
        work = work.replace(anchor, css + anchor, 1)

    print("chapter navs: %d | Clip blocks: %d | duration badges: %d" % (n_nav, n_clip, n_badge))
    if work == before:
        print("no changes (already applied)")
        return
    if apply:
        out = work.replace("\n", "\r\n") if crlf else work
        io.open(PAGE, "wb").write(out.encode("utf-8"))
        print("APPLIED")
    else:
        print("(dry-run)")


if __name__ == "__main__":
    run("--apply" in sys.argv)
