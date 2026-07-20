"""Ping IndexNow (Bing / Yandex / Seznam / Naver) when URLs change on any studio host.

Google does NOT use IndexNow -- this speeds up Bing and friends only.

Each host serves its own key file (IndexNow requires the key to be hosted on the host
being submitted). The keys below are PUBLIC by design -- hosting one proves domain
ownership. They are not credentials.

  main   builtbyjoshstudio.com        -> repo: builtbyjoshstudio
  tools  tools.builtbyjoshstudio.com  -> repo: tools
  tynkr  tynkr.builtbyjoshstudio.com  -> repo: tynkr-site

The key file must be LIVE on that host before submitting, or the API returns 403.

Usage (run from the site repo root):
    python tools/indexnow_submit.py https://builtbyjoshstudio.com/blog/foo.html [more...]
    python tools/indexnow_submit.py --host tools https://tools.builtbyjoshstudio.com/tabletop/
    python tools/indexnow_submit.py --sitemap                 # main sitemap.xml
    python tools/indexnow_submit.py --host tools --sitemap /c/Users/jotra/tools/sitemap.xml
    python tools/indexnow_submit.py --sitemap --dry           # preview, send nothing

Host is inferred from the first URL when not passed explicitly.
"""
import json
import re
import sys
import urllib.request

HOSTS = {
    "main":  ("builtbyjoshstudio.com",       "5a022f04e3b3cf4668a3f5c8d70cbecb"),
    "tools": ("tools.builtbyjoshstudio.com", "8f0b6b574090115771be348b5d74bffa"),
    "tynkr": ("tynkr.builtbyjoshstudio.com", "bbbd007439d2e4feec181190678fd2fd"),
}
ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10000

OK_CODES = {200, 202}
MEANING = {
    200: "OK - URLs accepted",
    202: "Accepted - key validation pending",
    400: "Bad request - invalid format",
    403: "Forbidden - key not valid / key file not reachable on that host",
    422: "Unprocessable - URL doesn't match host, or key mismatch",
    429: "Too many requests - slow down",
}


def urls_from_sitemap(path):
    xml = open(path, encoding="utf-8").read()
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def infer_host(url):
    for name, (host, _) in HOSTS.items():
        if url.startswith(f"https://{host}/"):
            return name
    return None


def take_opt(argv, flag, default=None):
    """Return the value following `flag`, or default. Removes both from argv."""
    if flag in argv:
        i = argv.index(flag)
        val = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else default
        del argv[i:i + (2 if val is not default else 1)]
        return val
    return default


def main(argv):
    argv = list(argv)
    dry = "--dry" in argv
    if dry:
        argv.remove("--dry")

    host_key = take_opt(argv, "--host")
    sitemap = None
    if "--sitemap" in argv:
        sitemap = take_opt(argv, "--sitemap", "sitemap.xml")

    urls = [a for a in argv if not a.startswith("--")]
    if sitemap:
        urls = urls_from_sitemap(sitemap)
    if not urls:
        print(__doc__)
        return 1

    if not host_key:
        host_key = infer_host(urls[0])
    if host_key not in HOSTS:
        print(f"ABORT: unknown host {host_key!r}. Use --host {'|'.join(HOSTS)}")
        return 1

    host, key = HOSTS[host_key]
    key_location = f"https://{host}/{key}.txt"

    bad = [u for u in urls if not u.startswith(f"https://{host}/")]
    if bad:
        print(f"ABORT: {len(bad)} URL(s) not on https://{host}/ -- IndexNow rejects these:")
        for u in bad[:5]:
            print("  ", u)
        return 1
    if len(urls) > MAX_URLS:
        print(f"ABORT: {len(urls)} URLs exceeds the {MAX_URLS} per-request cap")
        return 1

    payload = {"host": host, "key": key, "keyLocation": key_location, "urlList": urls}

    print(f"[{host_key}] {len(urls)} URL(s) -> {ENDPOINT}")
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
            code, body = r.status, r.read().decode("utf-8", "replace").strip()
    except urllib.error.HTTPError as e:
        code, body = e.code, e.read().decode("utf-8", "replace").strip()

    print(f"\nHTTP {code} - {MEANING.get(code, 'unknown')}")
    if body:
        print(body[:500])
    return 0 if code in OK_CODES else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
