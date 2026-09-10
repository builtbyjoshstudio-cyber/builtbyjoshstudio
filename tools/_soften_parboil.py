# _soften_parboil.py -- soften the batch-broths post's characterisation of par-boiling
# so it matches the cookbook's respect for it. The cookbook keeps BOTH: dad's par-boil
# ("this step is why our broth comes out clean... Don't skip it") and Josh's roast
# ("roasting cleans and browns at the same time, so you get a deeper flavor").
# Josh's preference (roast) stays; the "par-boiling gives you thin, flavorless broth /
# it's why your broth failed" framing goes.
# Dry-run by default; --apply writes. CRLF preserved.
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = os.path.join(ROOT, "blog", "why-home-cooks-should-batch-broths.html")

EDITS = [
    # the failure-mode list item -- par-boiling was being blamed for bad broth
    ("<li><strong>They par-boiled the bones</strong> and ended up with thin, flavorless broth and a sense that the effort wasn't worth it.</li>",
     "<li><strong>They par-boiled the bones and stopped there</strong> — a clean, clear broth, but without the browning step that would have given it color and depth, so it tasted thinner than they hoped.</li>"),

    # "It also removes flavor." -> par-boil is a real technique with a real purpose
    ("<p><strong>1. Roast the bones first, don't par-boil them.</strong> The traditional advice is to par-boil bones for ten minutes, drain them, rinse them, and then start the actual broth. This is meant to remove \"scum\" and impurities. It also removes flavor.</p>",
     "<p><strong>1. Roast the bones rather than par-boiling them.</strong> The traditional advice is to par-boil bones for ten minutes, drain them, rinse them, and then start the actual broth. That step does exactly what it promises — it takes off the blood and impurities that would otherwise cloud the pot, and it is the reason a properly made phở broth comes out clear. My dad has always done it that way. What it doesn't do is build any color or browning, and that is the part I want.</p>"),

    ("<p>I roast my bones instead. Twenty minutes in a 425°F oven, on a sheet pan, until they're deeply browned. Then they go into the pot. The roasting accomplishes the same goal as the par-boil (removing the surface proteins that would otherwise scum up the broth) but adds color and Maillard flavor instead of removing it. When I make broth this way, there's almost no scum to skim during the simmer. The roasting handled it.</p>",
     "<p>So I roast mine instead. Twenty minutes in a 425°F oven, on a sheet pan, until they're deeply browned. Then they go into the pot. Roasting does both jobs at once — it cleans and it browns — so you get the depth as well as a pot that stays clean. When I make broth this way, there's almost no scum to skim during the simmer. The roasting handled it. If you want the clearest possible broth, the par-boil is still the more direct route; I'd rather have the color.</p>"),

    ("<p>The fix for all three is in the techniques above. Roast, don't par-boil. Double-strain. Set it and walk away.</p>",
     "<p>The fix for all three is in the techniques above. Roast rather than par-boil. Double-strain. Set it and walk away.</p>"),

    # the Short Version line
    ("Roast bones (don't par-boil), double-strain, fridge-skim the fat",
     "Roast the bones rather than par-boiling, double-strain, fridge-skim the fat"),
]


def run(apply):
    raw = io.open(POST, "rb").read()
    crlf = raw.count(b"\r\n") > 0
    text = raw.decode("utf-8")
    work = text.replace("\r\n", "\n") if crlf else text
    before = work
    done = 0
    for old, new in EDITS:
        if old not in work and new[:40] in work:
            continue
        assert work.count(old) == 1, ("anchor not unique/found", old[:70])
        work = work.replace(old, new, 1)
        done += 1
    print("softened: %d/%d" % (done, len(EDITS)))
    assert "thin, flavorless broth" not in work
    assert "It also removes flavor." not in work
    assert "roast" in work.lower()  # Josh's preference survives
    if apply and work != before:
        io.open(POST, "wb").write((work.replace("\n", "\r\n") if crlf else work).encode("utf-8"))
        print("APPLIED")
    else:
        print("(dry-run)")


if __name__ == "__main__":
    run("--apply" in sys.argv)
