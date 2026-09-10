# _cookbook_consistency.py -- align the blog posts' rice/finger method with the
# cookbook (Nước Mắm, ch. 4 "Over Rice"), which is the authority.
#
# The cookbook is explicit and the posts had it wrong in a way that matters:
#   small batch -> finger goes DOWN THROUGH the rice to the BOTTOM of the cooker,
#                  water to the first knuckle (pinky)
#   big batch   -> finger rests FLAT ON TOP of the rice, water 1/8-1/2 inch UNDER
#                  the first knuckle (index). Filling to the knuckle with the finger
#                  on top is the cookbook's named mistake: "more than likely too much water."
# Both posts described the on-top placement with water up TO the knuckle for every
# batch size -- i.e. the error the cookbook warns against.
# Dry-run by default; --apply writes. CRLF preserved.
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RICE = "blog/how-i-cook-rice-finger-method.html"
LEARNED = "blog/how-i-learned-to-cook.html"

EDITS = [
    (RICE,
     "<p>After the rice is rinsed and sitting in the cooker, you add water. You don't measure it with a cup. You put your finger in the cooker, touching the top of the rice, and you add water until the water reaches the first knuckle of your finger above the rice line.</p>",
     "<p>After the rice is rinsed and sitting in the cooker, you add water. You don't measure it with a cup — you measure it with your finger. But it matters <em>where</em> you put the finger, because getting that slightly wrong means too much water.</p>"),

    (RICE,
     "<p>The finger I use is my left pinky for the small rice cooker. First knuckle of the pinky, resting on top of the rice. Add water to that knuckle. Done.</p>",
     "<p>For a small batch — about half a cup of rice, which covers me and my girlfriend in the small cooker — I put my pinky down <em>through</em> the rice until it's touching the bottom of the cooker, and add water until it reaches my first knuckle. That's it. Small batch, pinky, through the rice, water to the first knuckle.</p>"),

    (RICE,
     "<p>For the larger rice cooker, when I'm cooking bigger portions, I use my index finger instead — same first-knuckle measurement, but a longer finger because there's more rice and more water needed. That's the entire scaling logic. Small batch, small finger. Larger batch, longer finger.</p>",
     "<p>For a bigger batch you can't really reach the bottom through all that rice, so the placement changes. Rest your finger flat <em>on top</em> of the rice instead — and here's the part people get wrong: the water should come up to about an eighth to half an inch <em>under</em> your first knuckle. If you fill all the way to the knuckle with your finger sitting on top of the rice, that will more than likely be too much water. I use my index finger for the big cooker, pinky for the small one.</p>"),

    (RICE,
     "The amount of water you need is the amount that sits roughly one knuckle above whatever rice is in the pot.",
     "The amount of water you need is the amount that sits about a knuckle's depth above the rice — measured from the bottom of the cooker on a small batch, or just under the knuckle with your finger resting on top of a big one."),

    (RICE,
     "But if you're brand new to it and want a reference point: the first knuckle of an average adult finger is roughly half an inch to three-quarters of an inch above the surface of the rice. That's the rough water-above-rice target you're going for, regardless of how you measure it.",
     "But if you're brand new to it and want a reference point: the first knuckle of an average adult finger sits roughly half an inch to three-quarters of an inch up from the fingertip. On a big batch, with your finger flat on the rice, you're stopping the water an eighth to half an inch short of it. If you'd rather use the cup, the by-the-book measurement is 1 cup of rice to 1½ cups of water."),

    (LEARNED,
     "And the finger-measuring thing my dad did — first knuckle of your index finger, resting on top of the rice — actually works, even though there's no chef's textbook that recommends it.",
     "And the finger-measuring thing my dad did — pinky down through the rice to the bottom of the cooker on a small batch, index finger resting on top for a big one — actually works, even though there's no chef's textbook that recommends it."),

    (LEARNED,
     "I rinse it until the water runs clear, I put my finger in the pot, I add water up to my first knuckle, and the rice comes out right.",
     "I rinse it until the water runs mostly clear, I put my finger in the pot, I add water to my first knuckle, and the rice comes out right."),
]


def run(apply):
    by_file = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel, pairs in by_file.items():
        p = os.path.join(ROOT, rel.replace("/", os.sep))
        raw = io.open(p, "rb").read()
        crlf = raw.count(b"\r\n") > 0
        text = raw.decode("utf-8")
        work = text.replace("\r\n", "\n") if crlf else text
        done = 0
        for old, new in pairs:
            if new in work:
                continue
            n = work.count(old)
            assert n == 1, ("anchor not unique/found", rel, n, old[:70])
            work = work.replace(old, new, 1)
            done += 1
        print("%-46s %d/%d edits" % (rel, done, len(pairs)))
        if apply and work != (text.replace("\r\n", "\n") if crlf else text):
            io.open(p, "wb").write((work.replace("\n", "\r\n") if crlf else work).encode("utf-8"))
    print("APPLIED" if apply else "(dry-run)")


if __name__ == "__main__":
    run("--apply" in sys.argv)
