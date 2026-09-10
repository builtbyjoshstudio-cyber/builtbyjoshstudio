# _nav_cooking_swap.py -- top nav: replace the LEGAL item with COOKING -> /kitchen-videos.html
# (Josh's call, 2026-09-10: keeps the nav at 8 items, so no overflow in the 720-900px band
# where the row is already only ~8px from the logo and the hamburger has not kicked in yet.)
#
# TRAP: the nav item and the FOOTER item are byte-identical --
#   <li><a href="/legal/">Legal</a></li>   x2 on every page.
# So the swap is scoped to the <ul class="nav-links"> block and the footer count is
# asserted unchanged on every file.
# Dry-run by default; --apply writes. Per-file EOL preserved.
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEGAL_LI = '<li><a href="/legal/">Legal</a></li>'
COOKING_LI = '<li><a href="/kitchen-videos.html">Cooking</a></li>'
COOKING_LI_ACTIVE = '<li><a href="/kitchen-videos.html" class="active">Cooking</a></li>'
NAV_RX = re.compile(r'<ul class="nav-links">.*?</ul>', re.S)


def run(apply):
    files = [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
             if os.sep + ".git" + os.sep not in f]
    swapped = already = skipped = 0
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
        if COOKING_LI in nav or COOKING_LI_ACTIVE in nav:
            already += 1
            continue
        assert LEGAL_LI in nav, ("no Legal item in nav", f)
        assert nav.count(LEGAL_LI) == 1, ("multiple Legal items in nav", f)

        footer_before = work.count(LEGAL_LI) - 1  # everything outside the nav block
        is_self = os.path.basename(f) == "kitchen-videos.html"
        new_nav = nav.replace(LEGAL_LI, COOKING_LI_ACTIVE if is_self else COOKING_LI)
        work = work[:m.start()] + new_nav + work[m.end():]

        # the footer legal link must survive untouched
        footer_after = work.count(LEGAL_LI)
        assert footer_after == footer_before, ("footer Legal link changed!", f, footer_before, footer_after)
        assert footer_after >= 1, ("page lost its footer Legal link", f)

        swapped += 1
        if apply:
            out = work.replace("\n", "\r\n") if crlf else work
            io.open(f, "wb").write(out.encode("utf-8"))

    print("nav swapped: %d | already done: %d | no nav (skipped): %d | %s"
          % (swapped, already, skipped, "APPLIED" if apply else "(dry-run)"))


if __name__ == "__main__":
    run("--apply" in sys.argv)
