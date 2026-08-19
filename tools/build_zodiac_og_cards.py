# -*- coding: utf-8 -*-
"""build_zodiac_og_cards.py -- 1200x630 og:image cards for the 40 collection pages (2026-08-19).

For each collections/*.html page: read its current og:image (the 720x900 / 600x600 hero art), composite a
landscape card -- blurred darkened cover of the art as the background, the art itself right-aligned in a
framed panel, eyebrow + title (from the page H1, minus the file-count suffix) + price + domain on the left,
in the site's dark zodiac palette (#14130e bg, #f1eee6 ink, #ff5a30 accent) with the repo's Bricolage /
Hanken fonts (tools/_fonts). Output: images/og/zodiac/<page-slug>.jpg (JPEG q=88, ~100-200 KB), then the
page's og:image/twitter:image are repointed and og:image:width/height/alt added after og:image.

Hub pages (collections/index.html, chinese-zodiac-art.html) get cards too (multi-art strip background).
Idempotent: re-running regenerates images and leaves HTML alone if already pointed. Run it whenever
collection hero art or titles change. Requires Pillow. ASCII-safe I/O (HTML edited as bytes).

Usage: python tools/build_zodiac_og_cards.py [--apply]   (dry run lists actions)
"""
import argparse, glob, html, io, os, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "images" / "og" / "zodiac"
F_BRICOLAGE = str(ROOT / "tools" / "_fonts" / "Bricolage.ttf")
F_HANKEN = str(ROOT / "tools" / "_fonts" / "Hanken.ttf")
W, H = 1200, 630
BG, INK, MUT, ACC = (20, 19, 14), (241, 238, 230), (188, 183, 170), (255, 90, 48)


def fit_text(draw, text, font_path, max_w, start, min_size=30):
    size = start
    while size > min_size:
        f = ImageFont.truetype(font_path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(font_path, min_size)


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(art_paths, eyebrow, title, price_line, out_path):
    im = Image.new("RGB", (W, H), BG)
    # background: blurred, darkened cover of the first art
    art0 = Image.open(art_paths[0]).convert("RGB")
    bg = art0.copy()
    scale = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(22))
    im.paste(bg, (0, 0))
    im = Image.blend(im, Image.new("RGB", (W, H), BG), 0.72)
    d = ImageDraw.Draw(im)
    # right panel(s): 1 art -> one framed portrait; 2-3 arts -> overlapping strip
    panel_h = 520
    y0 = (H - panel_h) // 2
    if len(art_paths) == 1:
        a = art0
        ratio = a.width / a.height
        ph = panel_h
        pw = int(ph * ratio)
        a = a.resize((pw, ph))
        x0 = W - pw - 64
        d.rectangle([x0 - 4, y0 - 4, x0 + pw + 4, y0 + ph + 4], fill=(0, 0, 0))
        im.paste(a, (x0, y0))
        d.rectangle([x0 - 4, y0 - 4, x0 + pw + 4, y0 + ph + 4], outline=INK, width=3)
        text_right = x0 - 56
    else:
        xr = W - 60
        step = 150
        min_x0 = W
        for i, p in enumerate(reversed(art_paths[:3])):
            a = Image.open(p).convert("RGB")
            ph = panel_h - 60
            pw = int(ph * a.width / a.height)
            a = a.resize((pw, ph))
            x0 = xr - pw - (len(art_paths[:3]) - 1 - i) * step
            min_x0 = min(min_x0, x0)
            yy = y0 + 30
            d.rectangle([x0 - 4, yy - 4, x0 + pw + 4, yy + ph + 4], fill=(0, 0, 0))
            im.paste(a, (x0, yy))
            d.rectangle([x0 - 4, yy - 4, x0 + pw + 4, yy + ph + 4], outline=INK, width=3)
        text_right = min_x0 - 56
    # left text block
    lx = 64
    max_w = max(300, text_right - lx)
    d = ImageDraw.Draw(im)
    f_eye = ImageFont.truetype(F_HANKEN, 26)
    ey = eyebrow.upper()
    # letter-spaced eyebrow
    y = 96
    x = lx
    for ch in ey:
        w_ch = d.textlength(ch, font=f_eye)
        if x + w_ch > text_right - 8:  # clamp: never run into the art panel
            break
        d.text((x, y), ch, font=f_eye, fill=ACC)
        x += w_ch + 4
    y += 58
    f_t = ImageFont.truetype(F_BRICOLAGE, 68)
    lines = wrap(d, title, f_t, max_w)
    if len(lines) > 3:
        f_t = ImageFont.truetype(F_BRICOLAGE, 56)
        lines = wrap(d, title, f_t, max_w)
    for ln in lines[:4]:
        d.text((lx, y), ln, font=f_t, fill=INK)
        y += f_t.size + 12
    y += 18
    f_p = ImageFont.truetype(F_HANKEN, 34)
    d.text((lx, y), price_line, font=f_p, fill=INK)
    # accent rule + domain footer
    d.rectangle([lx, H - 92, lx + 64, H - 86], fill=ACC)
    f_d = ImageFont.truetype(F_HANKEN, 26)
    d.text((lx, H - 72), "builtbyjoshstudio.com", font=f_d, fill=MUT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    return out_path


def page_data(f):
    s = io.open(f, encoding="utf-8").read()
    og = re.search(r'<meta property="og:image" content="https://builtbyjoshstudio.com/([^"]*)"', s).group(1)
    # art = the page's own hero image (stable), NEVER the og:image (which points at the generated card
    # after the first run -- deriving art from og:image made run 2 build cards out of themselves)
    hero = re.search(r'<img src="\.\./((?:images/)[^"]+)"[^>]*fetchpriority="high"', s)
    hero = hero.group(1) if hero else None
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1)
    h1 = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h1))).strip()
    price = re.search(r'"price":\s*"([0-9.]+)"', s)
    return s, og, hero, h1, (price.group(1) if price else None)


EYEBROW = {
    "zodiac-art": "Western Zodiac · Zodiac Art",
    "zodiac-realms": "Western Realms · Zodiac Art",
    "chinese-zodiac-art": "Chinese Zodiac · Lunar Guardians",
    "chinese-zodiac-realms": "Chinese Zodiac Realms",
    "zodiac-landscapes": "Western Landscapes",
    "index": "Zodiac Art Collections",
}
SUFFIX = re.compile(r"\s+—\s+(144|48|12) [^—]+$")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); a = ap.parse_args()
    pages = sorted(glob.glob(str(ROOT / "collections" / "*.html")))
    made, edited = 0, 0
    for f in pages:
        rel = os.path.basename(f)[:-5]
        s, og, hero, h1, price = page_data(f)
        # eyebrow by page kind
        kind = "index" if rel == "index" else next((k for k in ("chinese-zodiac-realms", "chinese-zodiac-art", "zodiac-realms", "zodiac-landscapes", "zodiac-art") if rel.endswith(k) or rel == k), "zodiac-art")
        eyebrow = EYEBROW[kind]
        title = SUFFIX.sub("", h1)
        if kind in ("chinese-zodiac-realms",) or len(title) > 46:
            title = title.split(" — ")[0]  # keep the name half on very long titles
        price_line = f"${price} · instant digital download" if price else "Instant digital downloads"
        # art inputs
        if rel == "index":
            arts = [ROOT / "images/zodiac/libra.webp", ROOT / "images/zodiac/chinese/dragon.webp", ROOT / "images/zodiac/realms/aries.webp"]
        elif rel == "chinese-zodiac-art":
            arts = [ROOT / "images/zodiac/chinese/tiger.webp", ROOT / "images/zodiac/chinese/dragon.webp", ROOT / "images/zodiac/chinese/rabbit.webp"]
        else:
            assert hero and "images/og/" not in hero, (rel, hero)
            arts = [ROOT / hero]
        assert all(p.exists() for p in arts), (rel, arts)
        out = OUTDIR / f"{rel}.jpg"
        if a.apply:
            card([str(p) for p in arts], eyebrow, title, price_line, out)
        made += 1
        # repoint HTML
        url = f"https://builtbyjoshstudio.com/images/og/zodiac/{rel}.jpg"
        b = Path(f).read_bytes()
        old_og = ('<meta property="og:image" content="https://builtbyjoshstudio.com/%s" />' % og).encode()
        assert b.count(old_og) == 1, (f, og)
        alt = html.escape(title + " — zodiac art by Built by Josh Studio", quote=True)
        new_og = ('<meta property="og:image" content="%s" />\r\n  <meta property="og:image:width" content="1200" />\r\n  <meta property="og:image:height" content="630" />\r\n  <meta property="og:image:alt" content="%s" />' % (url, alt)).encode()
        nb = b.replace(old_og, new_og)
        old_tw = ('<meta name="twitter:image" content="https://builtbyjoshstudio.com/%s" />' % og).encode()
        if old_tw in nb:
            nb = nb.replace(old_tw, ('<meta name="twitter:image" content="%s" />' % url).encode())
        if b'og:image:width' not in b:
            edited += 1
            if a.apply:
                assert b"\n" not in nb.replace(b"\r\n", b"") or b"\r\n" not in nb
                Path(f).write_bytes(nb)
        print(("MADE " if a.apply else "plan ") + str(out.relative_to(ROOT)), "| art:", ",".join(p.name for p in arts), "|", title[:50], "| $", price)
    print("cards:", made, "pages edited:", edited)
    print("APPLIED" if a.apply else "dry run")


if __name__ == "__main__":
    main()
