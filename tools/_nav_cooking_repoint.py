# _nav_cooking_repoint.py -- point the COOKING nav item at the new /cooking/ hub
# instead of /kitchen-videos.html (the hub is now the section landing page).
# Scoped to the <ul class="nav-links"> block: the FOOTER separately carries a
# "Kitchen Videos" -> /kitchen-videos.html link that must NOT be touched.
# Idempotent. Dry-run by default; --apply writes. Per-file EOL preserved.
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = '<li><a href="/kitchen-videos.html">Cooking</a></li>'
OLD_ACTIVE = '<li><a href="/kitchen-videos.html" class="active">Cooking</a></li>'
NEW = '<li><a href="/cooking/">Cooking</a></li>'
NEW_ACTIVE = '<li><a href="/cooking/" class="active">Cooking</a></li>'
NAV_RX = re.compile(r'<ul class="nav-links">.*?</ul>', re.S)
FOOTER_VIDEOS = '<li><a href="/kitchen-videos.html">Kitchen Videos</a></li>'


def run(apply):
    files = [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
             if os.sep + ".git" + os.sep not in f]
    changed = already = skipped = 0
    for f in files:
        raw = io.open(f, "rb").read()
        crlf = raw.count(b"\r\n") > 0
        text = raw.decode("utf-8")
        work = text.replace("\r\n", "\n") if crlf else text

        m = NAV_RX.search(work)
        if not m:
            skipped += 1
            continue
        nav = m.group(0)
        if NEW in nav or NEW_ACTIVE in nav:
            already += 1
            continue
        assert (OLD in nav) or (OLD_ACTIVE in nav), ("no Cooking nav item", f)

        footer_before = work.count(FOOTER_VIDEOS)
        new_nav = nav.replace(OLD_ACTIVE, NEW_ACTIVE).replace(OLD, NEW)
        work = work[:m.start()] + new_nav + work[m.end():]
        assert work.count(FOOTER_VIDEOS) == footer_before, ("footer Kitchen Videos link changed", f)
        assert NAV_RX.search(work).group(0).count("/kitchen-videos.html") == 0, ("nav still points at the video page", f)

        changed += 1
        if apply:
            out = work.replace("\n", "\r\n") if crlf else work
            io.open(f, "wb").write(out.encode("utf-8"))

    print("nav re-pointed: %d | already: %d | no nav: %d | %s"
          % (changed, already, skipped, "APPLIED" if apply else "(dry-run)"))


if __name__ == "__main__":
    run("--apply" in sys.argv)
