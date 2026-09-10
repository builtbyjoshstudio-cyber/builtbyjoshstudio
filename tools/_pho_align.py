# _pho_align.py -- align blog/how-i-make-pho-two-day-method.html with the cookbook
# (Nước Mắm ch.7, "My Version" -- the two-day, broth-built-on-broth method).
# Josh: "cookbook is gospel."
#
# ALREADY MATCHING, left alone: the two-day structure, roasting the bones instead of
# par-boiling ("This replaces the traditional pre-boil"), Squid brand, carrots in the
# day-one pot, dry-roasting the spices, the spice list.
#
# CORRECTED here, cookbook -> post:
#   roast          400°F / 45 min            (post: 425°F / 30-45 min)
#   day-1 bones    marrow + knuckle + oxtail (post: short ribs + marrow; oxtail on day 2)
#                  -- cookbook offers short ribs as the no-butcher substitute
#   day-1 veg      + celery, + ginger        (post: carrots/onion/garlic only)
#   day-1 method   sweat carrots/onion/celery in oil first, bones in after
#   day-1 water    fill ~80%                 (post: "cover with cold water")
#   day-1 cook     8 hours on low            (post: 4-6 hours)
#   day-2 cook     12 hours                  (post: about 8)
#   sachet         last couple of hours      (post: last three)
#   fish sauce     2-3oz, season LIGHTLY -- it concentrates over 12 h and goes
#                  "very, very salty"; fix at the end
#                  (post said add "more than seemed reasonable" -- the opposite)
#   rock sugar     1-1.5oz
# Dry-run by default; --apply writes. CRLF preserved.
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = os.path.join(ROOT, "blog", "how-i-make-pho-two-day-method.html")

EDITS = [
    # --- Short Version -------------------------------------------------------
    ("<p>A two-day phở bò method: roast bones (don't par-boil), make stock day one with carrots in it, simmer everything day two for eight hours with a spice sachet added in the last three. Sautéed garlicky spinach goes at the bottom of the bowl. Squid brand fish sauce. A one-day version is included for when two isn't possible.</p>",
     "<p>A two-day phở bò method: roast the bones instead of par-boiling, build a beef stock on day one and cook it eight hours, then run the phở on day two for twelve, with a spice sachet in the last couple of hours. Season the fish sauce lightly — it concentrates as the broth reduces. Sautéed garlicky spinach goes at the bottom of the bowl. Squid brand fish sauce. A one-day version is included for when two isn't possible.</p>"),

    # --- Day One: bones ------------------------------------------------------
    ("<li><strong>Short ribs</strong> (English-cut, bone-in)</li>",
     "<li><strong>Marrow bones</strong> (16oz — the usual grocery store package)</li>\n            <li><strong>Beef knuckle bones</strong> (aim for 16oz — you don't want a whole knuckle, it's far too big, so this is a butcher-shop ask; if that's a hassle, English-cut short ribs are the substitute)</li>\n            <li><strong>Oxtail</strong> (16oz — not optional in our house)</li>"),

    ("<li><strong>Carrots</strong> (yes, carrots — not traditional, I do it anyway)</li>",
     "<li><strong>Carrots</strong> (3 whole — yes, carrots, not traditional, I do it anyway)</li>\n            <li><strong>Celery</strong> (3 stalks)</li>\n            <li><strong>Ginger</strong> (4 to 6oz — one typical root)</li>"),

    # --- Day One: roast ------------------------------------------------------
    ("<p>Before any of this goes in the pot, I roast the short ribs and marrow bones. In the oven, hot — somewhere around 425°F — for thirty to forty-five minutes, until the bones are deeply browned and the short ribs have a real crust on them. Sheet pan, foil-lined for cleanup, that's it.</p>",
     "<p>Before any of this goes in the pot, I roast the bones — forty-five minutes at 400°F, until they're deeply browned. Sheet pan, foil-lined for cleanup, that's it.</p>"),

    # --- Day One: the pot ----------------------------------------------------
    ("<p>Once the bones and short ribs are roasted, everything goes into the largest stock pot you have. Cover with cold water. Bring to a low simmer — not a boil, a simmer — and let it go for somewhere between four and six hours. Skim the foam off the top in the first hour. After that, the foam mostly stops coming.</p>",
     "<p>While the bones roast, cut the vegetables. Carrots and celery go on an angled bias into fifteen or twenty slices each — the more surface area, the more you pull out of them. Onion in thin slices, garlic lightly smashed, ginger sliced and smashed too.</p>\n\n      <p>Start the pot with a little avocado oil and sweat the carrots, onion and celery. When the bones come out of the oven they go straight in on top of the vegetables, then the garlic and ginger. Fill the pot about 80% of the way with cold water, and cook it on low for eight hours. Skim any scum — thanks to the roasting there shouldn't be much.</p>"),

    # --- Day Two: fish sauce -------------------------------------------------
    ("<p>How much fish sauce? More than you think. That's the lesson nobody tells you. Phở broth needs a real assertive saltiness from the fish sauce. Start with a few tablespoons, taste, add more. By the time the broth tastes \"right\" you'll have added more than seemed reasonable. That's correct.</p>",
     "<p>How much fish sauce? Less than you think, at this stage — and this is the part to be careful about. Start with two to three ounces. Over twelve hours you lose water and the flavors concentrate as the broth reduces, so a pot that tastes right at hour one is very, very salty by hour twelve. Season it lightly now; you can always fix it at the end. Rock sugar, an ounce to an ounce and a half, goes in at the same time.</p>"),

    # --- Day Two: cook time + sachet window ----------------------------------
    ("<p>Bring everything to a simmer and let it go for about eight hours. Total. Including the spice sachet, which doesn't go in until the last three hours.</p>",
     "<p>Bring everything to a simmer and let it go for twelve hours. There are no shortcuts here, and that's the point. The spice sachet doesn't join until the last couple of hours.</p>"),

    ("<strong>Add it to the broth in the last three hours.</strong>",
     "<strong>Add it to the broth for the last couple of hours.</strong>"),

    # --- the one-day fallback: keep it a fallback, but the spice rule is the
    #     cookbook's and applies regardless of total cook time
    ("<p><strong>One-day stockpot version:</strong> Skip the day-one stock. Roast the bones and short ribs as before. Add them with the oxtail, charred onion and ginger, fish sauce, and rock sugar to a stockpot. Simmer for six to eight hours. Add the spice sachet for the last three hours. Same assembly.</p>",
     "<p><strong>One-day stockpot version:</strong> Skip the day-one stock. Roast the bones as before. Add them with the charred onion and ginger, fish sauce, and rock sugar to a stockpot. Simmer for six to eight hours — fewer than the twelve the full method gets, which is exactly what you are trading away. Add the spice sachet for the last couple of hours. Same assembly.</p>"),
]


def run(apply):
    raw = io.open(POST, "rb").read()
    crlf = raw.count(b"\r\n") > 0
    text = raw.decode("utf-8")
    work = text.replace("\r\n", "\n") if crlf else text
    before = work
    done = skipped = 0
    for old, new in EDITS:
        if new.split("\n")[0] in work and old not in work:
            skipped += 1
            continue
        n = work.count(old)
        assert n == 1, ("anchor not unique/found (%d)" % n, old[:80])
        work = work.replace(old, new, 1)
        done += 1
    print("edits applied: %d | already done: %d" % (done, skipped))
    # sanity: the cookbook's numbers are now the ones on the page
    for needle in ["400°F", "eight hours", "twelve hours", "last couple of hours",
                   "two to three ounces", "80%", "Oxtail", "Celery"]:
        assert needle in work, ("expected needle missing after edit", needle)
    for gone in ["four and six hours", "about eight hours. Total", "more than seemed reasonable",
                 "last three hours", "425°F"]:
        assert gone not in work, ("stale text still present", gone)
    if apply and work != before:
        io.open(POST, "wb").write((work.replace("\n", "\r\n") if crlf else work).encode("utf-8"))
        print("APPLIED")
    else:
        print("(dry-run)")


if __name__ == "__main__":
    run("--apply" in sys.argv)
