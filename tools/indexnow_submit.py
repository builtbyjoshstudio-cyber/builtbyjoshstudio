"""Ping IndexNow (Bing / Yandex / Seznam / Naver) when URLs on builtbyjoshstudio.com change.

Google does NOT use IndexNow — this speeds up Bing and friends only.

The key file must be live at KEY_LOCATION before submitting, or the API returns 403.

Usage:
    python tools/indexnow_submit.py https://builtbyjoshstudio.com/blog/foo.html [more urls...]
    python tools/indexnow_submit.py --sitemap        # submit every <loc> in sitemap.xml
    python tools/indexnow_submit.py --sitemap --dry  # show what would be sent

Run from the site repo root.
"""
import json
import re
import sys
import urllib.request

HOST = "builtbyjoshstudio.com"
KEY = "5a022f04e3b3cf4668a3f5c8d70cbecb"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10000  # IndexNow per-request cap

# 200 = accepted, 202 = accepted pending key validation
OK_CODES = {200, 202}
MEANING = {
    200: "OK - URLs accepted",
    202: "Accepted - key validation pending",
    400: "Bad request - invalid format",
    403: "Forbidden - key not valid / key file not reachable",
    422: "Unprocessable - URL doesn't match host, or key mismatch",
    429: "Too many requests - slow down",
}


def urls_from_sitemap(path="sitemap.xml"):
    xml = open(path, encoding="utf-8").read()
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def main(argv):
    dry = "--dry" in argv
    args = [a for a in argv if not a.startswith("--")]

    if "--sitemap" in argv:
        urls = urls_from_sitemap()
    else:
        urls = args
    if not urls:
        print(__doc__)
        return 1

    bad = [u for u in urls if not u.startswith(f"https://{HOST}/")]
    if bad:
        print(f"ABORT: {len(bad)} URL(s) not on https://{HOST}/ -- IndexNow rejects these:")
        for u in bad[:5]:
            print("  ", u)
        return 1
    if len(urls) > MAX_URLS:
        print(f"ABORT: {len(urls)} URLs exceeds the {MAX_URLS} per-request cap")
        return 1

    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }

    print(f"{len(urls)} URL(s) -> {ENDPOINT}")
    for u in urls[:10]:
        print("  ", u)
    if len(urls) > 10:
        print(f"   ... and {len(urls) - 10} more")

    if dry:
        print("\n(dry run - nothing sent)")
        return 0

    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
            body = r.read().decode("utf-8", "replace").strip()
    except urllib.error.HTTPError as e:
        code = e.code
        body = e.read().decode("utf-8", "replace").strip()

    print(f"\nHTTP {code} - {MEANING.get(code, 'unknown')}")
    if body:
        print(body[:500])
    return 0 if code in OK_CODES else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
