"""sitemap_lastmod_sync.py -- keep <lastmod> truthful, derived from git history.

For every <url> in sitemap.xml, lastmod becomes the date of the most recent *content*
change of the page, where "content" = <title> + meta description + the visible text of
<body> (minus nav/footer/script/style/comments) + the href/src values in it. Chrome sweeps
(footer links, JSON-LD, analytics, redirect snippets) and attribute-only hygiene (image
width/height, loading, fetchpriority, classes) do NOT bump lastmod; copy, prices, links,
image sources, titles and sidebars DO.

Rules:
  * uncommitted working-tree content change  -> today
  * otherwise walk the file's git history (newest first) to the newest commit whose
    content fingerprint differs from its predecessor -> that commit's date
  * never move a lastmod backwards (max(existing, computed))
  * only the text inside <lastmod>..</lastmod> is rewritten; bytes/EOL otherwise untouched

Usage:
  python tools/sitemap_lastmod_sync.py [--root <repo>] [--apply] [--today YYYY-MM-DD]
  (dry run by default; prints every change)

Standing rule: run this (with --apply) before committing any content edit; commit the
sitemap with the edit. ASCII-only source on purpose.
"""
import argparse, datetime, hashlib, re, subprocess, sys
from pathlib import Path

RX_URL = re.compile(rb"<url>\s*<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", re.S)


def fingerprint(b: bytes) -> str:
    """Semantic content fingerprint: title + meta description + visible text of <body> (minus
    nav/footer/script/style/comments) + the href/src values in that body. Attribute-only
    hygiene (width/height, loading, fetchpriority, classes, ids) does NOT change it."""
    s = b.decode("utf-8", errors="replace")
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<script\b[^>]*>.*?</script>", "", s, flags=re.S | re.I)
    s = re.sub(r"<style\b[^>]*>.*?</style>", "", s, flags=re.S | re.I)
    title = re.search(r"<title>(.*?)</title>", s, re.S | re.I)
    desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', s, re.I)
    body = re.search(r"<body\b[^>]*>(.*)</body>", s, re.S | re.I)
    body = body.group(1) if body else s
    body = re.sub(r"<nav\b[^>]*>.*?</nav>", "", body, flags=re.S | re.I)
    body = re.sub(r"<footer\b[^>]*>.*?</footer>", "", body, flags=re.S | re.I)
    links = re.findall(r'\b(?:href|src)="([^"]*)"', body)
    text = re.sub(r"<[^>]+>", " ", body)
    text = (title.group(1) if title else "") + "|" + (desc.group(1) if desc else "") + "|" + text + "|" + "|".join(links)
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


class Git:
    def __init__(self, root: Path):
        self.root = root
        self.cat = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def log(self, rel: str):
        out = subprocess.run(["git", "-C", str(self.root), "log", "--format=%H %cs", "--", rel],
                             capture_output=True, text=True).stdout.split("\n")
        return [tuple(l.split(" ", 1)) for l in out if l.strip()]

    def blob(self, sha: str, rel: str):
        self.cat.stdin.write(f"{sha}:{rel}\n".encode()); self.cat.stdin.flush()
        hdr = self.cat.stdout.readline().decode().strip()
        if hdr.endswith("missing"):
            return None
        size = int(hdr.split()[2])
        data = self.cat.stdout.read(size); self.cat.stdout.read(1)
        return data

    def close(self):
        try:
            self.cat.stdin.close(); self.cat.wait(timeout=5)
        except Exception:
            pass


def url_to_rel(loc: str) -> str:
    path = re.sub(r"^https?://[^/]+/?", "", loc)
    if path == "" or path.endswith("/"):
        path += "index.html"
    return path


def content_date(git: Git, rel: str, today: str):
    f = git.root / rel
    if not f.exists():
        return None, "missing-file"
    hist = git.log(rel)
    if not hist:
        return today, "untracked"
    head_blob = git.blob("HEAD", rel)
    if head_blob is None or fingerprint(f.read_bytes()) != fingerprint(head_blob):
        return today, "worktree-change"
    fps = []
    for i, (sha, date) in enumerate(hist):
        b = git.blob(sha, rel)
        fps.append(fingerprint(b) if b is not None else None)
        if i >= 1 and fps[i] != fps[i - 1]:
            return hist[i - 1][1], f"content-change@{hist[i-1][0][:7]}"
    return hist[-1][1], "created"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--today", default=datetime.date.today().isoformat())
    a = ap.parse_args()
    root = Path(a.root); sm = root / "sitemap.xml"
    data = sm.read_bytes(); git = Git(root)
    changes, keep, out = [], 0, data
    for m in RX_URL.finditer(data):
        loc, old = m.group(1).decode(), m.group(2).decode().strip()
        rel = url_to_rel(loc)
        computed, why = content_date(git, rel, a.today)
        if computed is None:
            print(f"  !! {loc}: {why}"); continue
        new = max(old, computed[:10])
        if new != old:
            changes.append((loc, old, new, why))
        else:
            keep += 1
    git.close()
    # rebuild by sequential replacement (lengths are equal: YYYY-MM-DD -> YYYY-MM-DD), so offsets are stable
    if changes:
        buf = bytearray(data)
        for m in RX_URL.finditer(data):
            loc = m.group(1).decode()
            for c in changes:
                if c[0] == loc:
                    s, e = m.span(2)
                    assert e - s == len(c[2]), "lastmod length changed; refusing"
                    buf[s:e] = c[2].encode()
        out = bytes(buf)
    print(f"root={root.name} urls={keep + len(changes)} changed={len(changes)} kept={keep} today={a.today}")
    for loc, old, new, why in changes:
        print(f"  {old} -> {new}  {re.sub(r'^https?://[^/]+', '', loc) or '/'}  ({why})")
    if a.apply and changes:
        sm.write_bytes(out); assert sm.read_bytes() == out
        print("APPLIED")
    elif not a.apply:
        print("DRY RUN")


if __name__ == "__main__":
    main()
