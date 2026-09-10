# _cooking_hub_gate.py -- gate for the new /cooking/ hub: CRLF, JSON-LD, heading order,
# every internal link resolves to a real file, every local asset exists, habit checks.
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "cooking", "index.html")

raw = io.open(PAGE, "rb").read()
text = raw.decode("utf-8")
fixed = text.replace("\r\n", "\n").replace("\n", "\r\n")
if fixed.encode("utf-8") != raw:
    io.open(PAGE, "wb").write(fixed.encode("utf-8"))
    print("normalized to CRLF")
    raw = io.open(PAGE, "rb").read()
    text = raw.decode("utf-8")
assert len(re.findall(rb"(?<!\r)\n", raw)) == 0, "mixed EOLs"
print("CRLF lines: %d" % raw.count(b"\r\n"))

blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
types = [json.loads(b).get("@type") for b in blocks]
assert types == ["BreadcrumbList", "Organization"], types
print("JSON-LD: %s" % types)

heads = re.findall(r"<h([1-6])[ >]", text)
assert heads[0] == "1" and heads.count("1") == 1, heads
# no level may jump by more than 1
for a, b in zip(heads, heads[1:]):
    assert int(b) - int(a) <= 1, ("heading skip", a, b, heads)
print("headings: %s" % "".join(heads))

# internal links resolve
missing = []
for href in sorted(set(re.findall(r'href="(/[^"#?]*)"', text))):
    if href.endswith("/"):
        p = os.path.join(ROOT, href.strip("/").replace("/", os.sep), "index.html")
    else:
        p = os.path.join(ROOT, href.lstrip("/").replace("/", os.sep))
    if not os.path.exists(p):
        missing.append(href)
assert not missing, ("internal links 404", missing)
print("internal links OK (%d unique)" % len(set(re.findall(r'href="(/[^"#?]*)"', text))))

for src in sorted(set(re.findall(r'src="(/[^"]+)"', text))):
    assert os.path.exists(os.path.join(ROOT, src.lstrip("/").replace("/", os.sep))), ("missing asset", src)
print("assets OK")

assert "UPGRADE35" not in text
assert ("Built " + "By Josh Studio") not in text
assert "joshcooksfood" not in text and "jotran18" not in text
t = re.search(r"<title>(.*?)</title>", text, re.S).group(1)
d = re.search(r'name="description" content="([^"]*)"', text).group(1)
print("title %d chars | description %d chars" % (len(t), len(d)))
assert len(t) <= 66 and len(d) <= 160, "title/description over the site limits"
print("ALL GATES PASS")
