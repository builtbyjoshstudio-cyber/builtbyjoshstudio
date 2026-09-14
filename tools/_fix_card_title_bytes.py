# _fix_card_title_bytes.py -- remove the 12 stray 0x01 bytes from index.html.
#
# Origin: commit b834086 (2026-04-08, "Link all 12 zodiac cards to individual Etsy
# product listings") wrote a regex backreference as a literal byte, so each western
# zodiac card's title div became   <div class="card-title-bbj"> 0x01 <a ...>
# The byte renders as a ~10px glyph that pushes the "View Collection" button 10px out
# of line with every other zodiac card on the page (measured live: 10px vs 0px).
#
# The fix is removal, not restoring the April title text: the realms cards -- never
# touched by that bug -- use the identical layout (sign line, then the button alone),
# so removing the byte makes the western cards match the rest of the page exactly.
#
# The byte is addressed in hex and the anchor is the full card-title opening tag, so
# nothing else in the file can match. Dry-run by default; --apply writes.
import re
import sys

PAGE = r"C:\Users\jotra\builtbyjoshstudio-workspace\builtbyjoshstudio\index.html"

OPEN_TAG = b'<div class="card-title-bbj">'
SOH = bytes.fromhex("01")
BAD = OPEN_TAG + SOH + b'<a href="collections/'
GOOD = OPEN_TAG + b'<a href="collections/'


def run(apply):
    data = open(PAGE, "rb").read()
    total = data.count(SOH)
    anchored = data.count(BAD)
    print("0x01 bytes in file: %d | inside a card-title anchor: %d" % (total, anchored))
    assert total == 12 and anchored == 12, "expected exactly 12, all inside card-title anchors"

    fixed = data.replace(BAD, GOOD)
    assert fixed.count(SOH) == 0
    assert not re.findall(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]", fixed), "other control chars present"
    assert len(data) - len(fixed) == 12, "must remove exactly 12 bytes and nothing else"
    # each of the 12 western signs now opens its title slot exactly like a realms card
    for sign in ("aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
                 "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"):
        needle = OPEN_TAG + b'<a href="collections/' + sign.encode() + b'-zodiac-art.html"'
        assert fixed.count(needle) == 1, ("card not found exactly once", sign)

    if apply:
        open(PAGE, "wb").write(fixed)
        print("APPLIED: removed 12 bytes; 0 control characters remain")
    else:
        print("(dry-run) would remove 12 bytes")


if __name__ == "__main__":
    run("--apply" in sys.argv)
