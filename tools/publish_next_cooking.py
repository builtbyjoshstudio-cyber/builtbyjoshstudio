#!/usr/bin/env python3
"""
publish_next_cooking.py — publish the next cooking post in the queue.

Reads tools/cooking-queue.json, takes the first entry, pulls the HTML from
the cooking-stagger branch, substitutes date tokens, updates blog.html
(Projects section card + ItemList schema), updates sitemap.xml, removes
the entry from the queue, commits, and pushes.

Usage (from repo root):
    python tools/publish_next_cooking.py            # publish next
    python tools/publish_next_cooking.py --dry-run  # show what would happen
    python tools/publish_next_cooking.py --no-push  # commit but don't push
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "tools" / "cooking-queue.json"
BLOG_INDEX = REPO_ROOT / "blog.html"
SITEMAP = REPO_ROOT / "sitemap.xml"
STAGING_BRANCH = "cooking-stagger"


def run(cmd, capture=True):
    """Run a shell command in the repo root. Returns (rc, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=REPO_ROOT,
    )
    return result.returncode, (result.stdout or ""), (result.stderr or "")


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def human_date(dt):
    """Cross-platform 'May 5, 2026' style date (no leading zero on day)."""
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would happen, but don't write or commit.")
    p.add_argument("--no-push", action="store_true",
                   help="Commit but don't push.")
    return p.parse_args()


def main():
    args = parse_args()

    # Load queue
    if not QUEUE_FILE.exists():
        die(f"Queue file not found: {QUEUE_FILE}")
    with QUEUE_FILE.open(encoding="utf-8") as f:
        queue = json.load(f)
    if not queue:
        print("All cooking posts have been published. Nothing to do.")
        return
    next_post = queue[0]
    slug = next_post["slug"]
    print(f"Next: {slug}")
    print(f"      {next_post['schema_name']}")

    # Pre-flight: working tree clean?
    rc, stdout, _ = run(["git", "status", "--porcelain", "blog.html", "sitemap.xml", "blog/", "tools/"])
    if stdout.strip():
        die("Working tree has uncommitted changes to blog.html / sitemap.xml / blog/ / tools/.\n"
            "Commit or stash them, then re-run.")

    # Make sure we have the latest cooking-stagger
    rc, _, stderr = run(["git", "fetch", "origin", STAGING_BRANCH])
    if rc != 0:
        die(f"git fetch failed: {stderr}")

    # Pull HTML from cooking-stagger
    rc, html_content, stderr = run(["git", "show", f"origin/{STAGING_BRANCH}:blog/{slug}.html"])
    if rc != 0:
        die(f"Could not read blog/{slug}.html from origin/{STAGING_BRANCH}: {stderr}")

    # Substitute date tokens with today
    today = datetime.now(timezone.utc)
    iso_date = today.strftime("%Y-%m-%dT00:00:00Z")
    sitemap_date = today.strftime("%Y-%m-%d")
    h_date = human_date(today)
    html_content = html_content.replace("{{PUBLISH_DATE_ISO}}", iso_date)
    html_content = html_content.replace("{{PUBLISH_DATE_HUMAN}}", h_date)
    if "{{PUBLISH_DATE" in html_content:
        die("Unsubstituted date token remains in HTML — aborting.")

    # Build the new card HTML for blog.html Projects section
    new_card = (
        '\n\n      '
        f'<a href="blog/{slug}.html" class="article-card reveal">\n'
        f'        <div class="article-meta">{next_post["card_meta"]}</div>\n'
        f'        <h3 class="article-title">{next_post["card_title"]}</h3>\n'
        f'        <p class="article-excerpt">{next_post["card_excerpt"]}</p>\n'
        '        <div class="article-footer">\n'
        '          <span class="read-more">Read More ↗</span>\n'
        '        </div>\n'
        '      </a>'
    )

    # Read blog.html
    blog_html = BLOG_INDEX.read_text(encoding="utf-8")

    # Insert new card right after the Projects section's <div class="article-grid">
    projects_section_marker = '<section id="projects"'
    sec_pos = blog_html.find(projects_section_marker)
    if sec_pos == -1:
        die("Could not find <section id=\"projects\"> in blog.html")
    grid_marker = '<div class="article-grid">'
    grid_pos = blog_html.find(grid_marker, sec_pos)
    if grid_pos == -1:
        die("Could not find article-grid tag in Projects section")
    insert_at = grid_pos + len(grid_marker)
    blog_html_new = blog_html[:insert_at] + new_card + blog_html[insert_at:]

    # Update Projects ItemList JSON-LD: insert new entry at position 1, renumber
    schema_marker = "<!-- Schema.org: ItemList — Projects section -->"
    sm_pos = blog_html_new.find(schema_marker)
    if sm_pos == -1:
        die("Could not find Projects ItemList schema marker comment")
    schema_re = re.compile(
        r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
        re.DOTALL,
    )
    m = schema_re.search(blog_html_new, sm_pos)
    if not m:
        die("Could not extract Projects ItemList JSON")
    try:
        schema_obj = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        die(f"Projects ItemList JSON is invalid: {e}")

    new_item = {
        "@type": "ListItem",
        "position": 1,
        "url": f"https://builtbyjoshstudio.com/blog/{slug}.html",
        "name": next_post["schema_name"],
    }
    for it in schema_obj.get("itemListElement", []):
        it["position"] = it.get("position", 0) + 1
    schema_obj["itemListElement"].insert(0, new_item)
    new_schema_str = json.dumps(schema_obj, indent=2, ensure_ascii=False)
    blog_html_new = blog_html_new[:m.start(1)] + new_schema_str + blog_html_new[m.end(1):]

    # Update sitemap.xml: bump blog.html lastmod, insert new URL block
    sitemap_text = SITEMAP.read_text(encoding="utf-8")
    bump_re = re.compile(
        r'(<loc>https://builtbyjoshstudio\.com/blog\.html</loc>\s*<lastmod>)([\d\-]+)(</lastmod>)'
    )
    sitemap_new, count = bump_re.subn(rf'\g<1>{sitemap_date}\g<3>', sitemap_text, count=1)
    if count == 0:
        die("Could not find blog.html lastmod block in sitemap.xml")
    new_url_block = (
        '  <url>\n'
        f'    <loc>https://builtbyjoshstudio.com/blog/{slug}.html</loc>\n'
        f'    <lastmod>{sitemap_date}</lastmod>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>0.8</priority>\n'
        '  </url>\n'
    )
    if "</urlset>" not in sitemap_new:
        die("Could not find </urlset> closing tag in sitemap.xml")
    sitemap_new = sitemap_new.replace("</urlset>", new_url_block + "</urlset>", 1)

    # Build updated queue
    queue_new = queue[1:]
    queue_new_str = json.dumps(queue_new, indent=2, ensure_ascii=False) + "\n"

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print(f"Would write blog/{slug}.html ({len(html_content)} chars)")
        print(f"Would update blog.html (+1 card, schema renumbered to {len(schema_obj['itemListElement'])} items)")
        print(f"Would update sitemap.xml (blog.html lastmod -> {sitemap_date}, +1 URL)")
        print(f"Would shrink queue: {len(queue)} -> {len(queue_new)}")
        return

    # Write the files
    blog_post_path = REPO_ROOT / "blog" / f"{slug}.html"
    blog_post_path.write_text(html_content, encoding="utf-8", newline="\n")
    BLOG_INDEX.write_text(blog_html_new, encoding="utf-8", newline="\n")
    SITEMAP.write_text(sitemap_new, encoding="utf-8", newline="\n")
    QUEUE_FILE.write_text(queue_new_str, encoding="utf-8", newline="\n")

    # Stage + commit + push
    files = [
        f"blog/{slug}.html",
        "blog.html",
        "sitemap.xml",
        "tools/cooking-queue.json",
    ]
    rc, _, stderr = run(["git", "add"] + files)
    if rc != 0:
        die(f"git add failed: {stderr}")

    commit_msg = f"Publish cooking post: {next_post['schema_name']}"
    rc, _, stderr = run(["git", "commit", "-m", commit_msg])
    if rc != 0:
        die(f"git commit failed: {stderr}")

    if args.no_push:
        print(f"\nCommitted (not pushed). Run 'git push origin main' when ready.")
        return

    rc, _, stderr = run(["git", "push", "origin", "main"])
    if rc != 0:
        die(f"git push failed: {stderr}")

    print()
    print(f"Published: https://builtbyjoshstudio.com/blog/{slug}.html")
    print(f"Remaining in queue: {len(queue_new)}")


if __name__ == "__main__":
    main()
